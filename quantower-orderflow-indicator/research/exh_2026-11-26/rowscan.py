"""Quét cách gom hàng (số tick mỗi hàng, lệch mốc) cho họ luật: 3 hàng cực trị đều nhỏ so với nền + nến đủ volume + râu."""
import pandas as pd, numpy as np, data, feats
from split import enrich
from grid1 import f1
gt = pd.read_csv('gt_sides.csv', parse_dates=['t_utc'])
BARS = {}
def get(sym, G, off):
    g = gt[gt.sym == sym]
    if sym not in BARS: BARS[sym] = data.load(sym, g.t_utc.min() - pd.Timedelta(hours=3), g.t_utc.max() + pd.Timedelta(minutes=5))[0]
    X = feats.build(sym, G, off, bars=BARS[sym])
    X = X.merge(g[['t_utc', 'side', 'y', 'sample']], left_on=['t', 'side'], right_on=['t_utc', 'side'])
    return enrich(X)
def best(X, wcol='wick', ws=(2, 3, 4, 5, 6, 8)):
    y = X.y.values.astype(bool); res = []
    for a in (.2, .25, .3, .35, .4, .5):
        for b in (.2, .3, .4, .5, 9):
            for c in (0, .7, .8, .9, 1.0):
                for w in ws:
                    h = ((X.r01 <= a) & (X.r2 <= b) & (X.vol_rel >= c) & (X[wcol] >= w)).values; res.append((f1(y, h), a, b, c, w))
    return max(res, key=lambda z: z[0][0])
if __name__ == '__main__':
    for sym, grid in (('GC', [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (4, 3), (5, 0), (5, 2)]),
                      ('NQ', [(1, 0), (2, 0), (4, 0), (4, 2), (6, 0), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (10, 0), (12, 0), (12, 4), (16, 4), (16, 12)])):
        for G, off in grid:
            X = get(sym, G, off); print(sym, G, off, best(X))
