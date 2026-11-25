"""Ca biên T5 (PLAN.md mục 4, 6.6). python bw1_edge.py -> out_bw1_edge.txt
out_bw1_pick.txt không có cấu hình nào đạt hết T1-T4 -> chạy cho 6 cấu hình rớt ít nhất / tốt nhất từng ứng viên (danh sách EDGE_CFGS),
kèm luật hiện tại (CUR) để đối chiếu. Mọi ngưỡng chỉ từ nến đóng trước; không dùng giá."""
import os, sys, io, pickle, re
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bw1_common as C
import bw1_rules as RU

EDGE_CFGS = [('A_D5_R8', 'W690'), ('A_D3_R8', 'W690'), ('A_D10_R8', 'W690'), ('C_q15_k3', 'W690'), ('D_k200_R10', 'W690'), ('E_75', 'tu_nhien')]
out = io.StringIO()


def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.write(s + '\n')


with open(os.path.join(C.SCRATCH, 'bw1_runs.pkl'), 'rb') as f:
    RUNS = pickle.load(f)
LOGS = RUNS['logs']


def thr_for(cfg, warm, log):
    m = re.match(r'A_D(\d+)_R(\d+)$', cfg)
    if m: c = C.CandA(log, int(m[1]), [int(m[2])]); code = 'A'
    elif re.match(r'C_q(\d+)_k(\d+)$', cfg):
        m = re.match(r'C_q(\d+)_k(\d+)$', cfg); c = C.CandC(log, [(int(m[1]), int(m[2]))]); code = 'C'
    elif re.match(r'D_k(\d+)_R(\d+)$', cfg):
        m = re.match(r'D_k(\d+)_R(\d+)$', cfg); c = C.CandHill(log, [(int(m[1]), int(m[2]))]); code = 'D'
    elif re.match(r'G_T(\d+)_K(\d+)$', cfg):
        m = re.match(r'G_T(\d+)_K(\d+)$', cfg); c = C.CandG(log, int(m[1]), [int(m[2])]); code = 'G'
    elif re.match(r'B_D(\d+)_R(\d+)$', cfg):
        m = re.match(r'B_D(\d+)_R(\d+)$', cfg); c = C.CandB(log, int(m[1]), [int(m[2])]); code = 'B'
    elif cfg.startswith('E_'):
        return np.full(log.nb, float(cfg[2:]))
    elif cfg == 'CUR':
        return C.thr_current(log)
    else:
        raise ValueError(cfg)
    th, mn, fu, src = C.run_multi(c, log)
    a = RU.avail_mask(warm, code, mn, fu, src, c.full_minutes)
    return np.where(a, th[0], np.nan)


def day_level(log):
    cday = log.day[log.cb]
    return {d: C.level1pct(log.cmot[cday == d]) for d in set(log.day)}


def rounds_df(log, thr):
    r = C.select_rounds(log, thr)
    if len(r):
        r['t'] = pd.to_datetime(log.t[r.bar.values]); r['day'] = log.day[r.bar.values]; r['ses'] = log.ses[r.bar.values]
    return r


ALL = EDGE_CFGS + [('CUR', 'tu_nhien')]

# (a) chart mới mở: mở ở đầu từng ngày giao dịch (nhật ký trống trước đó)
P('=' * 110)
P('T5(a) CHART MOI MO: cat nhat ky tu dau ngay giao dich d (truoc do trong). Bao: phut nen toi khi co nguong dau tien; so vong trong 1380 phut nen dau;'
  ' vong nho nhat / muc 1% cua chinh ngay do (dat: khong vong nao < 3 lan); so voi trung vi vong/ngay on dinh (out_bw1_grid, doan chon, cung cau hinh).')
grid = pd.read_csv(os.path.join(C.HERE, 'out_bw1_grid.csv'))
for key in ('GCX_M1', 'GCX_M5', 'NQ_M1', 'NQ_M15', 'GCZ_M1'):
    log = LOGS[key]; lvl = day_level(log)
    days = sorted(set(log.day))
    starts = [d for d in days if log.daymin[d] >= 400][:6]
    for cfg, warm0 in ALL:
        warms = ['W240', 'W690', 'W1380', 'du'] if warm0 != 'tu_nhien' else ['tu_nhien']
        for warm in warms:
            stable = grid[(grid.nhat_ky == key) & (grid.cau_hinh == cfg) & (grid.khoi_dong == warm) & (grid.doan.isin(['chon', 'ngoai']))].vong_ngay_tv
            stable = stable.iloc[0] if len(stable) else np.nan
            res = []
            for d0 in starts:
                idx = np.nonzero(np.array([d >= d0 for d in log.day]))[0]
                sub = log.subset_bars(idx)
                thr = thr_for(cfg, warm, sub)
                ok = np.nonzero(~np.isnan(thr))[0]
                first = (ok[0] * sub.m) if len(ok) else None
                fb = int(np.ceil(1380 / sub.m))
                r = rounds_df(sub, thr); r1 = r[r.bar < fb] if len(r) else r
                ratio = [row.mot / lvl[row.day] for row in r1.itertuples()] if len(r1) else []
                bad = sum(1 for x in ratio if x < 3)
                res.append(f'{C.fmt_day(d0)}: nguong sau {first if first is not None else "-"}p, {len(r1)} vong ngay dau'
                           + (f', nho nhat {r1.mot.min()} (= {min(ratio):.1f} x muc1%)' if len(r1) else '') + (f' ROT {bad} vong < 3x' if bad else ''))
            P(f'  {key:7s} {cfg:10s} [{warm:8s}] on dinh TV {stable}/ngay | ' + ' ; '.join(res))

# (b), (c), (d)
P('=' * 110)
P('T5(b) NHAT KY NGAT QUANG _GCZ26 M1 / M5 (chay rieng tung nhat ky, tu dau): vong/ngay, vong nho nhat (dat: khong vong < 20)')
for key, fn in (('GCZ_M1', None), ('GCZ_M5', None)):
    log = LOGS.get(key) or C.load(key)
    for cfg, warm in ALL:
        thr = thr_for(cfg, warm, log); r = rounds_df(log, thr)
        per = r.groupby('day').size().to_dict() if len(r) else {}
        lo = int(r.mot.min()) if len(r) else None
        P(f'  {key} {cfg:10s} [{warm:8s}] co nguong tu nen {int(np.argmax(~np.isnan(thr))) if (~np.isnan(thr)).any() else "-"}/{log.nb}; '
          f'vong {len(r)}; theo ngay ' + ' '.join(f'{C.fmt_day(d)}:{n}' for d, n in sorted(per.items()))
          + f' | nho nhat {lo}' + (' ROT (< 20)' if lo is not None and lo < 20 else ''))

P('=' * 110)
P('T5(c) NGAY VANG 23-24/11 (vang _GCZ26 M1, nguong tu toan nhat ky truoc do) + NQ 24/11 (nua ngay) va 25/11 (mau): liet ke vong (dat: khong vong < 20)')
for key, ds in (('GCZ_M1', ['2026-11-23', '2026-11-24']), ('NQ_M1', ['2026-11-24', '2026-11-25']), ('NQ_M15', ['2026-11-24', '2026-11-25'])):
    log = LOGS[key]
    ds = [pd.Timestamp(x).date() for x in ds]
    for cfg, warm in ALL:
        thr = thr_for(cfg, warm, log); r = rounds_df(log, thr)
        rr = r[r.day.isin(ds)] if len(r) else r
        bm = np.isin(log.day, ds)
        tv = thr[bm]
        P(f'  {key} {cfg:10s} [{warm:8s}] phut nen ' + '/'.join(str(log.daymin.get(d, 0)) for d in ds)
          + f'; nguong cac nen do min/TV/max {np.nanmin(tv) if (~np.isnan(tv)).any() else "-"}/{np.nanmedian(tv) if (~np.isnan(tv)).any() else "-"}/{np.nanmax(tv) if (~np.isnan(tv)).any() else "-"}'
          + f'; {len(rr)} vong: ' + ', '.join(f'{x.t:%d/%m %H:%M} {x.mot}' for x in rr.itertuples())
          + (' ROT (< 20)' if len(rr) and rr.mot.min() < 20 else ''))

P('=' * 110)
P('T5(d) NGAY DON: vang 20/11 (_GCZ26 M1) va NQ 30/10 (M1, M15): liet ke du vong (dat: <= 40)')
for key, d in (('GCZ_M1', '2026-11-20'), ('NQ_M1', '2026-10-30'), ('NQ_M15', '2026-10-30')):
    log = LOGS[key]; d = pd.Timestamp(d).date()
    for cfg, warm in ALL:
        thr = thr_for(cfg, warm, log); r = rounds_df(log, thr)
        rr = r[r.day == d] if len(r) else r
        lst = ', '.join(f'{x.t:%H:%M}UTC {x.ses} {x.mot}(>{x.thr:.0f})' for x in rr.itertuples())
        P(f'  {key} {C.fmt_day(d)} {cfg:10s} [{warm:8s}] {len(rr)} vong' + (' ROT (> 40)' if len(rr) > 40 else '')
          + (': ' + lst if len(rr) <= 45 else ''))

P('=' * 110)
P('T5(e) NOI HOP DONG: _GC_XCEC (thang 9) + _GCZ26 (thang 11) thanh mot chuoi; so nguong tren cac nen _GCZ26 voi khi tinh rieng _GCZ26 (dat: lech <= 30%)')
for small_k, big_k in (('GCX_M1', 'GCZ_M1'),):
    a, b = LOGS[small_k], LOGS[big_k]
    j = C.Log('JOIN', a.m, a.tick, a.sym, np.concatenate([a.t, b.t]), np.concatenate([a.cb, b.cb + a.nb]),
              np.concatenate([a.ctk, b.ctk]), np.concatenate([a.cmot, b.cmot]), np.concatenate([a.cvol, b.cvol]))
    for cfg, warm in ALL:
        tj = thr_for(cfg, warm, j)[a.nb:]; tb = thr_for(cfg, warm, b)
        both = ~np.isnan(tj) & ~np.isnan(tb)
        dev = np.abs(tj[both] - tb[both]) / tb[both]
        # theo phút nến kể từ chỗ nối
        mins = np.arange(b.nb) * b.m
        segs = []
        for lo, hi in ((0, 690), (690, 1380), (1380, 2760), (2760, 6900), (6900, 10 ** 9)):
            mm = both & (mins >= lo) & (mins < hi)
            if mm.any():
                dv = np.abs(tj[mm] - tb[mm]) / tb[mm]
                segs.append(f'[{lo}-{hi if hi < 10**9 else "het"}p] TV {np.median(dv):.0%} max {dv.max():.0%} >30%: {np.mean(dv > 0.30):.0%}')
        onlyj = int(np.sum(~np.isnan(tj) & np.isnan(tb)))
        rj = C.select_rounds(b, np.where(np.isnan(tj), np.nan, tj)); rb = C.select_rounds(b, tb)
        P(f'  {cfg:10s} [{warm:8s}] nen co ca hai: {int(both.sum())}/{b.nb}; chi chuoi noi co nguong: {onlyj}; lech TV {np.median(dev) if len(dev) else np.nan:.0%}'
          f' | ' + ' ; '.join(segs) + f' | vong tren _GCZ26: noi {len(rj)} / rieng {len(rb)}')
        if cfg == 'A_D5_R8':
            tj_full = thr_for(cfg, warm, j)
            P(f'      nguong chuoi noi ngay cuoi thang 9 (TV) {np.nanmedian(tj_full[a.nb - 1380:a.nb]):.0f}; 1380 nen dau _GCZ26: noi TV {np.nanmedian(tj[:1380]):.0f} / rieng TV {np.nanmedian(tb[:1380]):.0f}')

with open(os.path.join(C.HERE, 'out_bw1_edge.txt'), 'w', encoding='utf-8') as f:
    f.write(out.getvalue())
