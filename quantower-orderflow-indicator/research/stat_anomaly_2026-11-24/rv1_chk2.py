import sys, os, numpy as np, pandas as pd
R = r'c:/Users/anhla/OneDrive/Documents/footprint-tpo/quantower-orderflow-indicator/research/stat_anomaly_2026-11-24'
sys.path.insert(0, R); os.chdir(R)
from sa_common import DotData, load_nq_full, nb_window_kth, CAP, rhu
from sa_dot_rules import evaluate, all_configs
from sa_oracle_lib import top_sets, near_dot, rulers, oracle_row
by = {c['name']: c for c in all_configs()}
class RR: pass
def mk(ds, thr, cfgname='x'):
    r = RR(); r.has = np.isfinite(thr); r.thr = thr
    r.exc = (ds.sval > np.where(r.has, thr, np.inf)[ds.sbar]); r.dot = r.exc & ds.lmax; r.cfg = dict(pa=cfgname); r.kind = 'p'
    return r
def to_ct(ds):
    t = ds.t
    off = np.where(t < pd.Timestamp('2026-11-01 07:00'), -5, -6)
    ct = t + pd.to_timedelta(off, unit='h')
    ds.tday = (ct + pd.Timedelta(hours=7)).normalize()
    ud, ds.dayi = np.unique(ds.tday.values, return_inverse=True); ds.days = pd.DatetimeIndex(ud)
    ds.slot = ((ct.hour * 60 + ct.minute) // ds.W).values.astype(np.int64)
    return ds
def roll_thr(ds, T, pbp):
    n = max(5, rhu(T / ds.m)); b = np.arange(ds.nb); lo = np.maximum(0, b - n); hi = b
    cs = np.r_[0, np.cumsum(ds.npos)]; ns = cs[hi] - cs[lo]
    K = np.where(ns * pbp >= 50000, (pbp * ns) // 10000, -1).astype(np.int64)[:, None]
    thr, gt = nb_window_kth(ds.sval, ds.s0, ds.s1, lo.astype(np.int64), hi.astype(np.int64), K, CAP)
    t = thr[:, 0]; return np.where(t >= 0, t, np.nan)
def report(tag, ds, r, Rr, mask):
    o = oracle_row(ds, r, Rr, mask, ds.w)
    hs = mask & r.has
    ndot = np.bincount(ds.sbar[r.dot], minlength=ds.nb); nexc = np.bincount(ds.sbar[r.exc], minlength=ds.nb)
    # theo ngay: ti le no / 2%
    dd = pd.DataFrame(dict(d=ds.dayi[hs], x=nexc[hs], n=ds.npos[hs], c=ndot[hs])).groupby('d').sum()
    rate = dd.x / dd.n / 0.02
    # gio trong tuan 02-06/11 (theo gio UTC)
    wk = hs & (ds.t >= '2026-11-01 22:00') & (ds.t < '2026-11-06 22:00')
    hh = pd.DataFrame(dict(h=ds.hour[wk], x=nexc[wk], n=ds.npos[wk])).groupby('h').sum(); hr = hh.x / hh.n / 0.02
    print(f"{tag:34s} co nguong {hs.sum()/mask.sum():.3f} p^ {o['p_hat']:.4f} cham/nen {ndot[hs].sum()/hs.sum():.2f} top20 {o['top20_ngay_gop']:.3f} top5 {o['top5_phien_gop']:.3f} cuc tri {o['chat_ca_hai_gop']:.3f} nhieu {o['nhieu_ngoai_ca_hai']:.3f} | ngay: min {rate.min():.2f} p10 {rate.quantile(.1):.2f} p90 {rate.quantile(.9):.2f} max {rate.max():.2f} | gio ok 02-06/11: {int(((hr>=.5)&(hr<=2)).sum())}/{len(hr)}", flush=True)
    return r
for sym, ms in (('NQ', (1, 15)), ('GC', (5,))):
  for m in ms:
    print('====', sym, m)
    ds = DotData(sym, m); mask = ds.doan_mask('kiem'); Rr = rulers(ds)
    r0 = evaluate(ds, by['cung_gio_K10_lc_p2']); report('UTC cg_K10_lc_p2', ds, mk(ds, np.where(r0.has, r0.thr, np.nan)), Rr, mask)
    r5 = evaluate(ds, by['cung_gio_K5_lc_p2'])
    rl = evaluate(ds, by['lai_mean_K20_p2']); report('UTC lai_mean_K20_p2 (thuoc do)', ds, rl, Rr, mask)
    cu = {T: roll_thr(ds, T, 200) for T in (120, 240, 480)}
    g5 = roll_thr(ds, 120, 500); g4 = roll_thr(ds, 240, 400)
    t0 = np.where(r0.has, r0.thr, np.nan)
    for T in (120, 240, 480):
        report(f'UTC cg + du phong cuon{T}', ds, mk(ds, np.where(np.isfinite(t0), t0, cu[T])), Rr, mask)
        both = np.isfinite(t0) & np.isfinite(cu[T]) & mask
        q = np.quantile(cu[T][both] / t0[both], [.1, .5, .9])
        print(f'     cuon{T}/cg nguong: p10 {q[0]:.2f} p50 {q[1]:.2f} p90 {q[2]:.2f}')
    tf = np.where(np.isfinite(t0), t0, cu[240])
    report('UTC cg+dp240 + chan max(cuon120 5%)', ds, mk(ds, np.fmax(tf, g5)), Rr, mask)
    report('UTC cg+dp240 + chan max(cuon240 4%)', ds, mk(ds, np.fmax(tf, g4)), Rr, mask)
    # nguong < 9
    hs = mask & np.isfinite(t0)
    print('     nguong cg p2: p1 %.0f p10 %.0f p50 %.0f | ti le nen nguong < 8: %.3f' % (*np.quantile(t0[hs], [.01, .1, .5]), (t0[hs] < 8).mean()))
    ds2 = to_ct(DotData(sym, m)); Rr2 = rulers(ds2)
    r0c = evaluate(ds2, by['cung_gio_K10_lc_p2']); t0c = np.where(r0c.has, r0c.thr, np.nan)
    report('CT  cg_K10_lc_p2', ds2, mk(ds2, t0c), Rr2, mask)
    report('CT  cg + du phong cuon240', ds2, mk(ds2, np.where(np.isfinite(t0c), t0c, cu[240])), Rr2, mask)
    r0n = evaluate(ds2, by['cung_gio_K10_p2']); t0n = np.where(r0n.has, r0n.thr, np.nan)
    report('CT  cg_K10 (khong lan can) + dp240', ds2, mk(ds2, np.where(np.isfinite(t0n), t0n, cu[240])), Rr2, mask)
# chuyen hop dong
print('==== NQfull M5, 07/09 -> 25/09')
ds = load_nq_full(5)
r0 = evaluate(ds, by['cung_gio_K10_lc_p2']); t0 = np.where(r0.has, r0.thr, np.nan)
g5 = roll_thr(ds, 120, 500); g4 = roll_thr(ds, 240, 400); c240 = roll_thr(ds, 240, 200)
tf = np.where(np.isfinite(t0), t0, c240)
rl = evaluate(ds, by['lai_mean_K20_p2'])
for tag, thr in (('cg+dp240', tf), ('+chan cuon120 5%', np.fmax(tf, g5)), ('+chan cuon240 4%', np.fmax(tf, g4)), ('lai_mean_K20_p2', None)):
    r = mk(ds, thr) if thr is not None else rl
    nexc = np.bincount(ds.sbar[r.exc], minlength=ds.nb); ndot = np.bincount(ds.sbar[r.dot], minlength=ds.nb)
    k = r.has & (ds.t >= '2026-09-06 22:00') & (ds.t < '2026-09-25 22:00')
    dd = pd.DataFrame(dict(d=ds.tday[k].strftime('%m-%d'), x=nexc[k], n=ds.npos[k], c=ndot[k], b=1)).groupby('d').sum()
    print(tag, 'ti le no/2% theo ngay:', ' '.join(f'{i}:{v:.1f}' for i, v in (dd.x / dd.n / 0.02).items()))
    print('    cham/nen theo ngay:', ' '.join(f'{v:.1f}' for v in (dd.c / dd.b)))
