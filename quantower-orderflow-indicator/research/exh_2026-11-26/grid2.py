import pandas as pd, numpy as np
from grid1 import f1
D = {'GC': pd.read_pickle('X_GC.pkl'), 'NQ': pd.read_pickle('X_NQ.pkl')}
for s, X in D.items():
    X['in_vol'] = (X.vol - X.cv3) / X.Bvol; X['vmean_rel'] = X.v_mean / X.Bmean; X['one'] = 1.0
    X['ms2'] = X[['s0', 's1']].max(1)
def rule(X, num, den1, a, f2, c, wc, w):
    return ((X[num] / X[den1] <= a) & (X[f2] >= c) & (X[wc] >= w)).values
def run(fit, test):
    X = D[fit]; y = X.y.values.astype(bool); res = []
    for num in ('ms3', 'cs3', 'ms2', 'cs2', 'ms4', 'cs4'):
        for den1 in ('Bmean', 'v_mean', 'Bvmax', 'v_max', 'vol', 'Bvol', 's_max'):
            base = (X[num] / X[den1]).values
            for a in np.unique(np.round(np.quantile(base[y], [.8, .85, .9, .95, 1.0]), 4)):
                for f2 in ('vol_rel', 'in_vol', 'vmax_rel', 'smax_v', 'vmean_rel', 'rng_rel', 'one'):
                    for c in np.unique(np.round(np.quantile(X[f2].values[y], [0, .05, .1, .15, .2]), 3)):
                        for wc, ws in (('wick_r', (1, 2, 3)), ('wick', (0,))):
                            for w in ws:
                                res.append((f1(y, rule(X, num, den1, a, f2, c, wc, w)), num, den1, a, f2, c, wc, w))
    res.sort(key=lambda z: -z[0][0])
    T = D[test]; yt = T.y.values.astype(bool)
    print('fit', fit, '-> test', test)
    seen = set()
    for r in res:
        k = (r[1], r[2], r[4])
        if k in seen: continue
        seen.add(k)
        ft = f1(yt, rule(T, *r[1:]))
        print('  fit F1 %.3f tp %d fp %d fn %d | test F1 %.3f tp %d fp %d fn %d |' % (r[0] + ft), r[1:])
        if len(seen) >= 14: break
run('GC', 'NQ'); run('NQ', 'GC')
