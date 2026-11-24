import sys, os, numpy as np, pandas as pd
R = r'c:/Users/anhla/OneDrive/Documents/footprint-tpo/quantower-orderflow-indicator/research/stat_anomaly_2026-11-24'
sys.path.insert(0, R); os.chdir(R)
from sa_common import load_dot, NQDIR
from sa_dot_rules import evaluate, all_configs
from sa_oracle_lib import top_sets, near_dot
by = {c['name']: c for c in all_configs()}
rs = np.random.RandomState(7)
# A. brute force doc lap: cung_gio_K10_lc_p2
for sym, m in (('NQ', 5), ('GC', 15)):
    ds = load_dot(sym, m)
    res = evaluate(ds, by['cung_gio_K10_lc_p2'])
    F = pd.read_pickle(os.path.join(NQDIR, f'F_{sym}_m{m}.pkl'))
    F['day'] = (F.t + pd.Timedelta(hours=2)).dt.normalize()
    W = max(30, m); F['slot'] = (F.t.dt.hour * 60 + F.t.dt.minute) // W; ns = 1440 // W
    bad = 0; n = 0
    for b in rs.choice(ds.nb, 60, replace=False):
        t = ds.t[b]; day = (t + pd.Timedelta(hours=2)).normalize(); s = (t.hour * 60 + t.minute) // W
        vals = []; ncen = 0
        for j, ss in enumerate([s, (s - 1) % ns, (s + 1) % ns]):
            X = F[(F.slot == ss) & (F.day < day)]
            dd = sorted(X.day.unique())[-10:]
            if j == 0: ncen = len(dd)
            X = X[X.day.isin(dd)]
            vals += [X.bid.values[X.bid.values > 0], X.ask.values[X.ask.values > 0]]
        v = np.sort(np.concatenate(vals))[::-1] if vals else np.zeros(0)
        thr = None
        if ncen >= 3 and len(v) * 200 >= 50000:
            K = (200 * len(v)) // 10000
            thr = v[K]
        got = res.thr[b] if res.has[b] else None
        n += 1
        if (thr is None) != (got is None) or (thr is not None and thr != got): bad += 1; print('LECH', sym, m, t, thr, got)
    print('A', sym, m, 'kiem', n, 'nen ngau nhien, lech', bad)
    # B. top20 sot: do chua co nguong hay do nguong
    mask = ds.doan_mask('kiem')
    for cn in ('cung_gio_K10_lc_p2', 'lai_mean_K20_p2'):
        r = evaluate(ds, by[cn])
        t20, t5 = top_sets(ds, mask)
        for nm, idx in (('top20', t20), ('top5', t5)):
            ok = r.exc[idx] | near_dot(ds, r, idx, ds.w)
            miss = idx[~ok]; nh = (~r.has[ds.sbar[miss]]).sum()
            hasidx = idx[r.has[ds.sbar[idx]]]
            ok2 = r.exc[hasidx] | near_dot(ds, r, hasidx, ds.w)
            print('B', sym, m, cn, nm, 'so o', len(idx), 'sot', len(miss), 'trong do nen chua co nguong', int(nh), '| chi nen co nguong:', round(ok2.mean(), 4))
            if nm == 'top20' and len(miss) - nh > 0:
                mm = miss[r.has[ds.sbar[miss]]]
                print('   sot du co nguong:', [(str(ds.t[ds.sbar[i]]), int(ds.sval[i]), float(r.thr[ds.sbar[i]])) for i in mm[:8]])
