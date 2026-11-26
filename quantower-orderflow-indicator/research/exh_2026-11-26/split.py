import pandas as pd, numpy as np
from grid1 import *
def enrich(X):
    X = prep(X).copy()
    for k in range(5): X[f'r{k}'] = X[f's{k}'] / X.Bmean; X[f'ro{k}'] = X[f'o{k}'] / X.Bmean; X[f'rv{k}'] = X[f'v{k}'] / X.Bmean
    sgn = np.where(X.side == 'T', 1, -1)
    X['dir'] = X.up * sgn            # +1: nến đi về phía cực trị đang xét (nến tăng với đỉnh), -1 ngược lại
    X['dlt'] = X.delta * sgn; X['dlt_rel'] = X.dlt / X.vol
    X['vol_rel'] = X.vol / X.Bvol; X['rng_rel'] = X.rng / X.Brng; X['wick_rel'] = X.wick / X.rng; X['body_rel'] = X.body / X.rng
    X['poc_rel'] = X.poc_pos / X.nrow; X['smax_rel'] = X.smax_pos / X.nrow; X['vmax_rel'] = X.v_max / X.Bvmax; X['smax_v'] = X.s_max / X.Bmean
    X['stot_rel'] = X.s_tot / X.vol
    X['r01'] = X[['r0', 'r1']].max(1); X['r012'] = X[['r0', 'r1', 'r2']].max(1); X['rc2'] = X.r0 + X.r1; X['rc3'] = X.rc2 + X.r2; X['rc4'] = X.rc3 + X.r3
    X['inc'] = ((X.s0 <= X.s1) & (X.s1 <= X.s2)).astype(int); X['inc3'] = (X.inc & (X.s2 <= X.s3)).astype(int)
    return X
def auc(y, v):
    y = np.asarray(y, bool); v = np.asarray(v, float); ok = ~np.isnan(v); y = y[ok]; v = v[ok]
    if y.sum() == 0 or (~y).sum() == 0: return 0.5
    r = pd.Series(v).rank().values; return (r[y].sum() - y.sum() * (y.sum() + 1) / 2) / (y.sum() * (~y).sum())
def rank_feats(Z, skip=()):
    num = [c for c in Z.columns if Z[c].dtype != object and c not in ('y', 'G', 'n_vis', 'n_mark') and not str(Z[c].dtype).startswith('datetime') and c not in skip]
    r = sorted(((auc(Z.y, Z[c]), c) for c in num), key=lambda z: -abs(z[0] - .5))
    return r
if __name__ == '__main__':
    F = pd.read_pickle('feats.pkl')
    for sym, G in (('NQ', 8), ('GC', 2), ('GC', 1)):
        X = enrich(F[(F.sym == sym) & (F.G == G)])
        thr = X[X.y == 1].r01.max(); wm = X[X.y == 1].wick.min()
        base = (X.r01 <= thr) & (X.wick >= wm); Z = X[base]
        print(sym, G, 'nguong r01', round(thr, 3), 'wick>=', wm, 'ung vien', len(Z), 'dau', int(Z.y.sum()))
        print('  ', [(round(a, 2), c) for a, c in rank_feats(Z)[:25]])
