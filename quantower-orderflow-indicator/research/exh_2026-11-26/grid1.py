import pandas as pd, numpy as np, itertools, sys
import os
F = pd.read_pickle('feats.pkl') if os.path.exists('feats.pkl') else None   # chạy feats.py trước khi dùng các script dò (grid*, split)
def prep(X):
    X = X.copy(); S = X[[f's{k}' for k in range(8)]].values; V = X[[f'v{k}' for k in range(8)]].values; O = X[[f'o{k}' for k in range(8)]].values
    for n in range(1, 9):
        X[f'cs{n}'] = S[:, :n].sum(1); X[f'ms{n}'] = S[:, :n].max(1); X[f'cv{n}'] = V[:, :n].sum(1); X[f'mv{n}'] = V[:, :n].max(1); X[f'co{n}'] = O[:, :n].sum(1)
    return X
def f1(y, h):
    tp = (y & h).sum(); fp = (~y & h).sum(); fn = (y & ~h).sum()
    return (2 * tp / max(1, 2 * tp + fp + fn), int(tp), int(fp), int(fn))
def grid(X, wcol='wick', wvals=(0, 1, 2, 3, 4, 5, 6), top=6):
    y = X.y.values.astype(bool); res = []
    for n in range(1, 9):
        for num in ('cs', 'ms', 'cv', 'mv'):
            a = X[f'{num}{n}'].values
            for den in ('abs', 'Bmean', 'v_max', 's_max', 'v_mean', 'vol', 's_tot', 'Bvol', 'Bvmax'):
                d = np.ones(len(X)) if den == 'abs' else X[den].values
                r = a / np.where(d > 0, d, np.nan)
                for w in wvals:
                    ok = X[wcol].values >= w
                    for thr in np.unique(np.nanquantile(r[ok & y], [0.7, 0.8, 0.9, 0.95, 1.0])):
                        h = ok & (r <= thr)
                        res.append((f1(y, h), n, num, den, w, round(float(thr), 4)))
    res.sort(key=lambda z: -z[0][0]); return res[:top]
if __name__ == '__main__':
    for sym, G in (('GC', 1), ('GC', 2), ('NQ', 8), ('NQ', 1), ('NQ', 4)):
        X = prep(F[(F.sym == sym) & (F.G == G)]); print(sym, G, len(X), X.y.sum())
        for wc in ('wick',) + (('wick_r',) if G > 1 else ()):
            for r in grid(X, wc): print('   ', wc, r)
