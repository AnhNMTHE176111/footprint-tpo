"""Chấm T1-T4 (PLAN.md mục 4) cho từng dòng lưới. python bw1_score.py -> out_bw1_score.csv, out_bw1_pick.txt
Đọc SCRATCH/bw1_runs.pkl (do bw1_rules.py ghi).

Cách tính (giả định ghi cả ở R1-KET-QUA.md):
  T1  trung vị vòng/ngày trong [4, 12]; không ngày nào > 40; trung vị từng phiên Á/Âu/Mỹ <= 6.
  T2  tỉ số = cỡ vòng / mức 1% lệnh đơn M1 cùng khung 30' Chicago của 5 ngày giao dịch trước có số liệu ở khung đó
      (mức 1% = lớn thứ n//100 + 1; cần >= 2 ngày trước, vòng không tra được thì bỏ khỏi T2 và đếm riêng); nhỏ nhất >= 3, trung vị >= 5.
      Nhật ký M1 dùng tra: GCX_M1 cho vàng tháng 9, NQ_M1 cho NQ, GCZ_M1 cho vàng tháng 11.
  T3  (a) hệ số biến thiên trung vị ngưỡng theo ngày <= 30%; (b) |vòng TV đoạn kiểm - đoạn chọn| / đoạn chọn <= 40%
      (dòng 'ngoai' của GCZ so với đoạn chọn GCX_M1 cùng cấu hình); (c) cặp khung (GCX M1-M5, NQ M1-M15), cùng ngày đánh giá chung:
      vòng trùng = cùng tick, cùng cỡ, giờ nến M1 nằm trong nến khung lớn; tỉ lệ = số cặp trùng / max(số vòng hai khung) >= 85%.
  T4  "nổ" = ô có lệnh đơn > ngưỡng của nến (sau gộp, ô không vẽ chỉ vì nằm cạnh một vòng lớn hơn trong cùng nến vẫn tính là đã thể hiện).
      (a) lệnh lớn nhất mỗi ngày 100%; (b) 3 ô lớn nhất mỗi ngày >= 85%; (c) lệnh lớn nhất từng phiên, chỉ phiên có
      lớn nhất >= 5 x mức 1% (lớn thứ n//100 + 1) của chính phiên đó trong ngày đó, >= 80%; in riêng Á/Âu/Mỹ.
Đánh giá chỉ trên ngày đánh giá của dòng (ngày đủ, mọi nến có ngưỡng)."""
import os, sys, pickle
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bw1_common as C
import bw1_rules as RU

with open(os.path.join(C.SCRATCH, 'bw1_runs.pkl'), 'rb') as f:
    RUNS = pickle.load(f)
store = RUNS['store']
grid = pd.read_csv(os.path.join(C.HERE, 'out_bw1_grid.csv'))
logs = RUNS['logs']   # ảnh chụp nhật ký lúc chạy lưới (nhật ký NQ còn đang ghi thêm)
M1_OF = {'GCX_M1': 'GCX_M1', 'GCX_M5': 'GCX_M1', 'NQ_M1': 'NQ_M1', 'NQ_M15': 'NQ_M1', 'GCZ_M1': 'GCZ_M1'}
p1per = {k: C.p1_slot_table(logs[k])[1] for k in ('GCX_M1', 'NQ_M1', 'GCZ_M1')}
p1cache = {}


def p1(m1key, day, slot):
    key = (m1key, day, slot)
    if key not in p1cache: p1cache[key] = C.p1_lookup(p1per[m1key], day, slot)
    return p1cache[key]


# chuẩn bị theo nhật ký: ô top-3 mỗi ngày, lớn nhất từng phiên
prep = {}
for k, log in logs.items():
    cday = log.day[log.cb]; cses = log.ses[log.cb]
    days = sorted(set(log.day))
    top = {}; sesmax = {}
    for d in days:
        idx = np.nonzero(cday == d)[0]
        o = idx[np.argsort(-log.cmot[idx], kind='stable')]
        top[d] = o[:3]
        for s in ('A', 'Au', 'My'):
            ii = idx[cses[idx] == s]
            if not len(ii): continue
            j = ii[np.argmax(log.cmot[ii])]
            lvl = C.level1pct(log.cmot[ii])
            sesmax[(d, s)] = (j, log.cmot[j], lvl)
    prep[k] = (top, sesmax)


def ev_days(log, seg, thr):
    return RU.eval_days(log, RU.seg_days(log, seg), thr)


def match_rate(ks, kl, cfg, warm, days):
    a, b = logs[ks], logs[kl]
    ra = store[(ks, cfg, warm)]['rounds']; rb = store[(kl, cfg, warm)]['rounds']
    if not len(ra) and not len(rb): return np.nan, 0, 0
    ra = ra[np.isin(a.day[ra.bar.values], days)] if len(ra) else ra
    rb = rb[np.isin(b.day[rb.bar.values], days)] if len(rb) else rb
    if not len(ra) and not len(rb): return np.nan, 0, 0
    ta = pd.to_datetime(a.t[ra.bar.values]).floor(f'{b.m}min') if len(ra) else []
    sa = set(zip(ta, ra.tick.values, ra.mot.values)) if len(ra) else set()
    tb = pd.to_datetime(b.t[rb.bar.values]) if len(rb) else []
    sb = list(zip(tb, rb.tick.values, rb.mot.values)) if len(rb) else []
    m = sum(1 for x in sb if x in sa)
    return m / max(len(ra), len(rb)), len(ra), len(rb)


rows = []
for _, g in grid.iterrows():
    k, cfg, warm, seg = g.nhat_ky, g.cau_hinh, g.khoi_dong, g.doan
    log = logs[k]; st = store[(k, cfg, warm)]
    thr = st['thr'].astype(float); rr = st['rounds']
    days = ev_days(log, seg, thr)
    res = dict(nhat_ky=k, cau_hinh=cfg, ung_vien=g.ung_vien, khoi_dong=warm, doan=seg, so_ngay=len(days),
               vong_tv=g.vong_ngay_tv, vong_max=g.vong_ngay_max, tv_A=g.tv_A, tv_Au=g.tv_Au, tv_My=g.tv_My,
               nguong_p50=g.nguong_p50, co_vong_min=g.co_vong_min)
    if not days:
        res.update(T1=False, T2=False, T3a=False, T3b=False, T3c=False, T4=False, ghi_chu='khong co ngay danh gia')
        rows.append(res); continue
    # T1
    t1 = (4 <= g.vong_ngay_tv <= 12) and g.vong_ngay_max <= 40 and max(g.tv_A, g.tv_Au, g.tv_My) <= 6
    # T2
    rin = rr[np.isin(log.day[rr.bar.values], days)] if len(rr) else rr
    ratios = []; nolook = 0
    for b, mot in zip(rin.bar.values if len(rin) else [], rin.mot.values if len(rin) else []):
        lv = p1(M1_OF[k], log.day[b], int(log.slot[b]) if log.m <= 30 else 0)
        if np.isnan(lv) or lv <= 0: nolook += 1; continue
        ratios.append(mot / lv)
    ratios = np.array(ratios)
    t2min = ratios.min() if len(ratios) else np.nan; t2med = np.median(ratios) if len(ratios) else np.nan
    t2 = bool(len(ratios) and t2min >= 3 and t2med >= 5)
    # T3a
    t3a = bool(not np.isnan(g.nguong_cv) and g.nguong_cv <= 0.30)
    # T3b
    if seg == 'chon':
        other = grid[(grid.nhat_ky == k) & (grid.cau_hinh == cfg) & (grid.khoi_dong == warm) & (grid.doan == 'kiem')]
        ref = g.vong_ngay_tv; cmpv = other.vong_ngay_tv.iloc[0] if len(other) else np.nan
    elif seg == 'kiem':
        other = grid[(grid.nhat_ky == k) & (grid.cau_hinh == cfg) & (grid.khoi_dong == warm) & (grid.doan == 'chon')]
        ref = other.vong_ngay_tv.iloc[0] if len(other) else np.nan; cmpv = g.vong_ngay_tv
    else:
        other = grid[(grid.nhat_ky == 'GCX_M1') & (grid.cau_hinh == cfg) & (grid.khoi_dong == warm) & (grid.doan == 'chon')]
        ref = other.vong_ngay_tv.iloc[0] if len(other) else np.nan; cmpv = g.vong_ngay_tv
    dev = abs(cmpv - ref) / ref if (ref and not np.isnan(ref) and not np.isnan(cmpv) and ref > 0) else np.nan
    t3b = bool(not np.isnan(dev) and dev <= 0.40)
    # T3c
    pair = {'GCX_M1': ('GCX_M1', 'GCX_M5'), 'GCX_M5': ('GCX_M1', 'GCX_M5'), 'NQ_M1': ('NQ_M1', 'NQ_M15'), 'NQ_M15': ('NQ_M1', 'NQ_M15')}.get(k)
    if pair:
        ks, kl = pair
        d2 = sorted(set(ev_days(logs[ks], seg, store[(ks, cfg, warm)]['thr'].astype(float))) & set(ev_days(logs[kl], seg, store[(kl, cfg, warm)]['thr'].astype(float))))
        mr, na, nb = match_rate(ks, kl, cfg, warm, d2) if d2 else (np.nan, 0, 0)
    else:
        mr, na, nb = np.nan, 0, 0
    t3c = bool(not np.isnan(mr) and mr >= 0.85) if pair else None
    # T4
    top, sesmax = prep[k]
    cthr = thr[log.cb]
    fired = lambda j: (not np.isnan(cthr[j])) and log.cmot[j] > cthr[j]
    a = [fired(top[d][0]) for d in days]
    b3 = [fired(j) for d in days for j in top[d]]
    cs = {'A': [], 'Au': [], 'My': []}
    for d in days:
        for s in cs:
            v = sesmax.get((d, s))
            if v and v[1] >= 5 * v[2]: cs[s].append(fired(v[0]))
    call = sum(cs.values(), [])
    t4a = np.mean(a); t4b = np.mean(b3); t4c = np.mean(call) if call else np.nan
    t4 = bool(t4a == 1.0 and t4b >= 0.85 and (np.isnan(t4c) or t4c >= 0.80))
    res.update(T1=t1, T2=t2, T3a=t3a, T3b=t3b, T3c=t3c, T4=t4,
               t2_min=round(t2min, 2) if len(ratios) else np.nan, t2_tv=round(t2med, 2) if len(ratios) else np.nan, t2_khong_tra=nolook,
               nguong_cv=g.nguong_cv, t3b_lech=round(dev, 3) if not np.isnan(dev) else np.nan, t3c_trung=round(mr, 3) if not np.isnan(mr) else np.nan,
               t3c_n=f'{na}/{nb}', t4a=round(t4a, 3), t4b=round(t4b, 3), t4c=round(t4c, 3) if not np.isnan(t4c) else np.nan,
               t4c_A=f'{sum(cs["A"])}/{len(cs["A"])}', t4c_Au=f'{sum(cs["Au"])}/{len(cs["Au"])}', t4c_My=f'{sum(cs["My"])}/{len(cs["My"])}',
               vong_nho_nhat_so_25=(int(g.co_vong_min) if not np.isnan(g.co_vong_min) else np.nan) if log.sym == 'GC' else np.nan, ghi_chu='')
    rows.append(res)

sc = pd.DataFrame(rows)
sc.to_csv(os.path.join(C.HERE, 'out_bw1_score.csv'), index=False, float_format='%.4g')

# ---------- chọn ----------
CRIT = ['T1', 'T2', 'T3a', 'T3c', 'T4']
PICKLOGS = ['GCX_M1', 'GCX_M5', 'NQ_M1', 'NQ_M15']
ch = sc[(sc.doan == 'chon') & sc.nhat_ky.isin(PICKLOGS)]
lines = []
summ = []
for (cfg, warm), g in ch.groupby(['cau_hinh', 'khoi_dong']):
    fails = []
    for _, r in g.iterrows():
        for c in CRIT:
            v = r[c]
            if v is False or v == False: fails.append(f'{r.nhat_ky}:{c}')  # noqa: E712
    nf = len(fails) + 5 * (len(PICKLOGS) - len(g))
    summ.append((nf, cfg, warm, fails))
summ.sort(key=lambda x: (x[0], x[1], x[2]))
passed = [s for s in summ if s[0] == 0]


def fmt_row(r):
    return (f'    {r.nhat_ky:7s} {r.doan:5s} ngay {r.so_ngay:2d} | vong/ngay TV {r.vong_tv:5.1f} max {r.vong_max:4.0f} | phien A/Au/My {r.tv_A:.1f}/{r.tv_Au:.1f}/{r.tv_My:.1f}'
            f' | nguong TV {r.nguong_p50:6.1f} cv {r.get("nguong_cv", np.nan):.2f} | vong nho nhat {r.co_vong_min} | T2 min/TV {r.get("t2_min", np.nan)}/{r.get("t2_tv", np.nan)}'
            f' | T3b {r.get("t3b_lech", np.nan)} T3c {r.get("t3c_trung", np.nan)} | T4 a/b/c {r.get("t4a", np.nan)}/{r.get("t4b", np.nan)}/{r.get("t4c", np.nan)}'
            f' (A {r.get("t4c_A", "")} Au {r.get("t4c_Au", "")} My {r.get("t4c_My", "")})'
            f' | dat: ' + ' '.join(c for c in ['T1', 'T2', 'T3a', 'T3b', 'T3c', 'T4'] if r[c] is True or r[c] == True) + (f' [{r.ghi_chu}]' if r.ghi_chu else ''))  # noqa: E712


lines.append('Tieu chi xet o doan chon: ' + ', '.join(CRIT) + ' tren ca 4 nhat ky GCX_M1, GCX_M5, NQ_M1, NQ_M15 (cung tham so). T3b (kiem so chon) in kem, khong dung de chon.')
lines.append(f'So cau hinh (cau hinh x khoi dong) xet: {len(summ)}; dat het: {len(passed)}')
show = passed[:6] if passed else summ[:10]
lines.append('CAU HINH DAT HET:' if passed else 'KHONG CO CAU HINH NAO DAT HET -> 10 cau hinh rot it nhat:')
for nf, cfg, warm, fails in show:
    lines.append(f'== {cfg} [{warm}]  so tieu chi rot {nf}: {", ".join(fails) if fails else "-"}')
    for _, r in sc[(sc.cau_hinh == cfg) & (sc.khoi_dong == warm)].sort_values(['nhat_ky', 'doan']).iterrows():
        lines.append(fmt_row(r))
lines.append('')
lines.append('Dat het tren doan chon ma KHONG tinh T3c (de Fable xem):')
for nf, cfg, warm, fails in summ:
    if all(':T3c' in f for f in fails) and fails:
        lines.append(f'   {cfg} [{warm}] rot: {", ".join(fails)}')
lines.append('')
# T4 bỏ riêng (c) lớn nhất từng phiên: đạt (a) 100% và (b) >= 85%
sc['T4ab'] = (sc.t4a == 1.0) & (sc.t4b >= 0.85)
ch = sc[(sc.doan == 'chon') & sc.nhat_ky.isin(PICKLOGS)]
summ2 = []
for (cfg, warm), g in ch.groupby(['cau_hinh', 'khoi_dong']):
    fails = [f'{r.nhat_ky}:{c}' for _, r in g.iterrows() for c in ['T1', 'T2', 'T3a', 'T3c', 'T4ab'] if not bool(r[c] is True or r[c] == True)]  # noqa: E712
    summ2.append((len(fails) + 5 * (len(PICKLOGS) - len(g)), cfg, warm, fails))
summ2.sort(key=lambda x: (x[0], x[1], x[2]))
p2 = [s for s in summ2 if s[0] == 0]
lines.append(f'Neu BO T4(c) (lon nhat tung phien), giu T4(a)(b): dat het tren doan chon ca 4 nhat ky = {len(p2)} cau hinh:')
for nf, cfg, warm, fails in p2:
    rr = sc[(sc.cau_hinh == cfg) & (sc.khoi_dong == warm)]
    def cell(k, s, col):
        x = rr[(rr.nhat_ky == k) & (rr.doan == s)]
        return x[col].iloc[0] if len(x) else np.nan
    lines.append(f'   {cfg:12s} [{warm:5s}] vong/ngay TV chon/kiem: GC M1 {cell("GCX_M1","chon","vong_tv")}/{cell("GCX_M1","kiem","vong_tv")}'
                 f'  NQ M1 {cell("NQ_M1","chon","vong_tv")}/{cell("NQ_M1","kiem","vong_tv")}  GCZ ngoai {cell("GCZ_M1","ngoai","vong_tv")}'
                 f' | T4c chon GC/NQ {cell("GCX_M1","chon","t4c")}/{cell("NQ_M1","chon","t4c")} kiem GC/NQ {cell("GCX_M1","kiem","t4c")}/{cell("NQ_M1","kiem","t4c")}'
                 f' | kiem dat T1-T4(ab): ' + ','.join(f'{k}' for k in PICKLOGS if all(bool(rr[(rr.nhat_ky == k) & (rr.doan == "kiem")][c].iloc[0]) for c in ['T1', 'T2', 'T3a', 'T3c', 'T4ab']) if len(rr[(rr.nhat_ky == k) & (rr.doan == "kiem")])))
lines.append('')
# cấu hình tốt nhất từng ứng viên (ít tiêu chí rớt nhất ở đoạn chọn; hòa thì trung vị vòng/ngày GC M1 gần 8 nhất)
lines.append('Cau hinh tot nhat tung ung vien tren doan chon (it tieu chi rot nhat T1,T2,T3a,T3c,T4; hoa -> TV vong/ngay GCX_M1 gan 8 nhat):')
best = {}
for nf, cfg, warm, fails in summ:
    code = sc[sc.cau_hinh == cfg].ung_vien.iloc[0]
    x = sc[(sc.cau_hinh == cfg) & (sc.khoi_dong == warm) & (sc.nhat_ky == 'GCX_M1') & (sc.doan == 'chon')]
    gap = abs(x.vong_tv.iloc[0] - 8) if len(x) and not np.isnan(x.vong_tv.iloc[0]) else 99
    key = (nf, gap)
    if code not in best or key < best[code][0]: best[code] = (key, cfg, warm, fails)
for code in ['A', 'B', 'C', 'Cx', 'D', 'E', 'F', 'G']:
    if code not in best: continue
    (nf, gap), cfg, warm, fails = best[code]
    lines.append(f'== [{code}] {cfg} [{warm}] rot {nf}: {", ".join(fails) if fails else "-"}')
    for _, r in sc[(sc.cau_hinh == cfg) & (sc.khoi_dong == warm)].sort_values(['nhat_ky', 'doan']).iterrows():
        lines.append(fmt_row(r))
lines.append('')
lines.append('Hai moc so sanh:')
for cfg in ('CUR', 'ADAPT'):
    for _, r in sc[sc.cau_hinh == cfg].sort_values(['nhat_ky', 'doan']).iterrows():
        lines.append(f'  {cfg:5s}' + fmt_row(r))
with open(os.path.join(C.HERE, 'out_bw1_pick.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))
