"""Vòng 2, mục 6.3: Big Trade — phân vị cuốn trên lệnh đơn, cửa sổ A / B / C × T 120 / 240 × p 1% / 0,5% (12 tổ hợp) + hai mốc đối chứng.
Nhật ký: GC (16 phiên; 10 đầu chọn / 6 cuối kiểm), NQ (6 phiên, không có đoạn kiểm), GClive (đứt quãng, đoạn kiểm thứ hai). Khung M1…H1.
Thước đã sửa: "20 ô lớn nhất ngày" chỉ tính ngày có >= 400 nến M1 có số liệu; "5 ô lớn nhất phiên" chỉ (ngày × phiên) có >= 60 nến M1;
  "Khớp theo giờ" đạt khi >= 5/6 số giờ có nến nằm trong 0,5–2; sót chia "chưa có ngưỡng" / "vì ngưỡng".
Phép thử buổi tối: nhật ký GC, NQ chỉ giữ 12:00–18:00 UTC mỗi ngày. "20 ô lớn nhất ngày" ở phép thử này tính trên ngày có >= 300 nến M1
  (buổi tối tối đa 360 nến M1, mốc 400 không ngày nào đạt — ghi ở mục bất thường).
Ra: out_r2_bt_score.csv, out_r2_bt_evening.csv, out_r2_bt_pick.txt.  Chạy: python sa2_bt_eval.py"""
import time, numpy as np, pandas as pd
import sa_dot_rules as R1
from sa_bt_rules import BtData, evaluate_bt, bt_configs
from sa_eval_lib import calib_and_density
from sa_oracle_lib import rulers, near_dot, top_sets
from bt_common import load_m1, to_tf
import sa2_lib as L

t0 = time.time()
KEYS = ('GC', 'NQ', 'GClive')
DOANS = {'GC': ('chon', 'kiem'), 'NQ': ('tat_ca',), 'GClive': ('kiem',)}
SCORE, EVE = [], []


def fmt(x):
    return 'nan' if x is None or not np.isfinite(x) else f'{x:.3f}'


def okmasks(bt, M1, min_day=400, min_ses=60):
    b1 = pd.DatetimeIndex(sorted(set(M1.t)))
    d1 = (b1 + pd.Timedelta(hours=2)).normalize(); s1 = L.ses_code(b1)
    cnt = pd.Series(1, index=d1).groupby(level=0).size()
    okd = set(cnt[cnt >= min_day].index)
    cs = pd.Series(1, index=pd.MultiIndex.from_arrays([d1, s1])).groupby(level=[0, 1]).size()
    oks = set(cs[cs >= min_ses].index)
    dayok = np.isin(bt.tday.values, np.array(sorted(okd), dtype='datetime64[ns]'))
    sesok = np.array([(d, s) in oks for d, s in zip(bt.tday, bt.ses)], bool)
    return dayok, sesok, len(okd), len(oks)


def all_runs(bt):
    out = []
    for w, T, p in L.BT_COMBOS:
        out.append((L.bt_name(w, T, p), L.bt_eval(bt, w, T, p)))
    allc = {c['name']: c for c in bt_configs(bt.key)}
    for nm in ('dc_codinh10', 'dc_dang_chay_thich_nghi'):
        r = evaluate_bt(bt, allc[nm])
        out.append((nm, L.Res(bt, allc[nm], r.has, r.thr, r.nom, r.exc, r.dot, None, 'base', np.nan)))
    return out


def score(bt, res, nm, Rr, mask, tops, key, doan):
    c, d, s = calib_and_density(bt, res, nm, doan)
    o = L.oracle2(bt, res, Rr, mask, bt.g, tops)
    hs = mask & res.has
    nd = np.bincount(bt.sbar[res.dot], minlength=bt.nb)
    row = dict(cau_hinh=nm, ma=key, khung=bt.m, doan=doan, so_nen=int(mask.sum()), ti_le_nen_co_nguong=hs.sum() / max(mask.sum(), 1),
               khop_chung=s['khop_chung'], khop_A=s['khop_phien'][0], khop_Au=s['khop_phien'][1], khop_My=s['khop_phien'][2], ti_le_no_o=s['ti_le_no_o'])
    if res.kind == 'p':
        k = row['khop_chung']; row['v_khop_chung'] = ('ĐẠT ' if 0.8 <= k <= 1.25 else 'TRƯỢT ') + fmt(k)
        kp = s['khop_phien']; kv = kp[np.isfinite(kp)]
        okp = len(kv) == 3 and np.all((kv >= .67) & (kv <= 1.5)) and kv.max() / max(kv.min(), 1e-12) <= 1.8
        row['v_khop_phien'] = ('ĐẠT ' if okp else 'TRƯỢT ') + '/'.join(fmt(x) for x in kp)
        kg = s['khop_gio']; pres = s['gio_co_nen']
        good = int(np.sum(pres & (kg >= .5) & (kg <= 2))); npres = int(pres.sum())
        row['v_khop_gio'] = ('ĐẠT ' if good * 6 >= 5 * npres else 'TRƯỢT ') + f'{good}/{npres}'
    else:
        row['v_khop_chung'] = row['v_khop_phien'] = row['v_khop_gio'] = 'KHÔNG ÁP DỤNG'
    for g in ('top20', 'top5', 'cuc_tri'):
        row[g] = o[g]; row[f'{g}_so_o'] = o[f'{g}_so_o']; row[f'{g}_sot_chua_nguong'] = o[f'{g}_sot_chua_nguong']; row[f'{g}_sot_vi_nguong'] = o[f'{g}_sot_vi_nguong']
        row[f'{g}_tren_nen_co_nguong'] = o.get(f'{g}_co_nguong', np.nan)
    row.update(nhieu=o['nhieu'], le3=o['le3'], p_hat=o['p_hat'], so_vong=o['so_cham'])
    row['v_nhieu'] = ('ĐẠT ' if np.isfinite(o['nhieu']) and o['nhieu'] <= .05 else 'TRƯỢT ') + fmt(o['nhieu'])
    if hs.any():
        x = nd[hs]
        row.update(vong_nen=x.mean(), vong_1nen_p50=np.quantile(x, .5), vong_1nen_p95=np.quantile(x, .95), vong_1nen_max=int(x.max()))
        for i, sn in enumerate(('A', 'Au', 'My')):
            k = hs & (bt.ses == i)
            row[f'vong_nen_{sn}'] = nd[k].mean() if k.any() else np.nan
            if k.any() and np.isfinite(res.thr[k]).any():
                q = np.nanquantile(res.thr[k], [.1, .5, .9]); row[f'nguong_{sn}_p10'], row[f'nguong_{sn}_p50'], row[f'nguong_{sn}_p90'] = q
    return row


M1S = {k: load_m1(k) for k in KEYS}
for key in KEYS:
    for m in (1, 5, 15, 30, 60):
        bt = BtData(key, m, to_tf(M1S[key], m)); Rr = rulers(bt)
        dayok, sesok, nd_ok, ns_ok = okmasks(bt, M1S[key])
        runs = all_runs(bt)
        for doan in DOANS[key]:
            mask = bt.doan_mask(doan) if doan != 'tat_ca' else np.ones(bt.nb, bool)
            tops = L.top_sets_f(bt, mask, dayok, sesok)
            for nm, res in runs:
                r = score(bt, res, nm, Rr, mask, tops, key, doan); r['so_ngay_du_400'] = nd_ok; r['so_ngay_phien_du_60'] = ns_ok
                SCORE.append(r)
        # phép thử buổi tối
        if key in ('GC', 'NQ'):
            M1e = M1S[key]; tod = M1e.t.dt.hour * 60 + M1e.t.dt.minute
            M1e = M1e[(tod >= 720) & (tod < 1080)].reset_index(drop=True)
            be = BtData(key, m, to_tf(M1e, m))
            dayok_e, _, nd_e, _ = okmasks(be, M1e, min_day=300)
            t20e, _ = top_sets(be, dayok_e)
            full = dict(runs)
            for nm, rf in runs:
                if nm.startswith('dc_'):
                    rc = {c['name']: c for c in bt_configs(key)}[nm]
                    x = evaluate_bt(be, rc); re = L.Res(be, rc, x.has, x.thr, x.nom, x.exc, x.dot, None, 'base', np.nan)
                else:
                    cfg = rf.cfg; re = L.bt_eval(be, cfg['w'], cfg['T'], cfg['pbp'])
                # nến đầu mỗi buổi chưa có ngưỡng
                firsts = []
                for d in np.unique(be.dayi):
                    h = re.has[be.dayi == d]
                    firsts.append(int(np.argmax(h)) if h.any() else len(h))
                # vòng trùng trên các nến chung
                tf_ = bt.t.values[bt.sbar[rf.dot]]; keep = np.isin(tf_, be.t.values)
                A = set(zip(tf_[keep].astype(np.int64), bt.stk[rf.dot][keep]))
                B = set(zip(be.t.values[be.sbar[re.dot]].astype(np.int64), be.stk[re.dot]))
                hit = re.exc[t20e] | near_dot(be, re, t20e, be.g) if len(t20e) else np.zeros(0, bool)
                nothr = ~re.has[be.sbar[t20e]] if len(t20e) else np.zeros(0, bool)
                EVE.append(dict(cau_hinh=nm, ma=key, khung=m, so_buoi=len(firsts), nen_dau_chua_nguong_tb=np.mean(firsts), nen_dau_chua_nguong_max=int(np.max(firsts)),
                                ti_le_nen_co_nguong=re.has.mean(), vong_buoi_toi=len(B), vong_day_du_cung_nen=len(A), trung=len(A & B) / max(len(A | B), 1),
                                top20=hit.mean() if len(hit) else np.nan, top20_so_o=len(t20e), top20_sot_chua_nguong=int((~hit & nothr).sum()),
                                top20_sot_vi_nguong=int((~hit & ~nothr).sum()), so_ngay_du_300=nd_e))
        R1._memo.clear()
        print(f'{key} M{m} xong ({time.time() - t0:.0f} s)', flush=True)

S = pd.DataFrame(SCORE); E = pd.DataFrame(EVE)
S.to_csv('out_r2_bt_score.csv', index=False, float_format='%.5g'); E.to_csv('out_r2_bt_evening.csv', index=False, float_format='%.5g')

# ---------------- luật chọn viết trước ----------------
lines = []
names = [L.bt_name(*c) for c in L.BT_COMBOS]
cand = []
for nm in names:
    g = S[(S.cau_hinh == nm) & (S.khung.isin([1, 5, 15])) & (((S.ma == 'GC') & (S.doan == 'kiem')) | (S.ma == 'NQ'))]
    okc = g.khop_chung.between(0.8, 1.25).all() and (g.nhieu <= 0.05).all()
    vals = list(S[(S.cau_hinh == nm) & S.khung.isin([1, 5, 15]) & (((S.ma == 'GC') & (S.doan == 'kiem')) | S.ma.isin(['NQ', 'GClive']))].top20) + \
        list(E[(E.cau_hinh == nm) & E.khung.isin([1, 5, 15])].top20)
    mn = np.nanmin(vals)
    lines.append(f'{nm}: điều kiện Khớp chung 0,8–1,25 và nhiễu <= 5% (GC kiểm + NQ, M1/M5/M15) = {"ĐẠT" if okc else "TRƯỢT"}; '
                 f'Khớp chung {g.khop_chung.min():.3f}–{g.khop_chung.max():.3f}, nhiễu lớn nhất {g.nhieu.max():.4f}; "20 ô lớn nhất ngày" nhỏ nhất = {mn:.4f}')
    if okc: cand.append((nm, mn))
if cand:
    best = max(v for _, v in cand)
    tied = [n for n, v in cand if v >= best - 0.005]
    pref = lambda n: ('ABC'.index(n.split('_')[1]), 0 if '_T240_' in n else 1, 0 if n.endswith('p1') else 1)
    win = sorted(tied, key=pref)[0]
    lines.append(f'KẾT QUẢ ÁP LUẬT: giá trị nhỏ nhất cao nhất = {best:.4f}; các tổ hợp lệch dưới 0,005: {", ".join(tied)}; theo thứ tự ưu tiên A>B>C, T240>T120, p1% -> {win}')
else:
    lines.append('KẾT QUẢ ÁP LUẬT: không tổ hợp nào qua điều kiện Khớp chung + nhiễu.')
open('out_r2_bt_pick.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
print(f'xong ({time.time() - t0:.0f} s)')
