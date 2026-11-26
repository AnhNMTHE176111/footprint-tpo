"""Quét cách tính nền (số nến N, TB / trung vị / gộp, có tính nến hiện tại không) cho luật: 3 hàng cực trị <= a x nền hàng, volume nến >= c x nền volume, râu >= w."""
import pandas as pd, numpy as np, data, feats
from grid1 import f1
gt = pd.read_csv('gt_sides.csv', parse_dates=['t_utc'])
CFG = {'GC': (2, 1), 'NQ': (8, 4)}
def bar_table(sym):
    G, off = CFG[sym]; g = gt[gt.sym == sym]
    bars = data.load(sym, g.t_utc.min() - pd.Timedelta(hours=6), g.t_utc.max() + pd.Timedelta(minutes=5))[0]
    rows = []
    for b in bars:
        r = (b['tk'] - off) // G; lo = r.min(); n = r.max() - lo + 1
        A = np.zeros(n); Bd = np.zeros(n); V = np.zeros(n); np.add.at(A, r - lo, b['ask']); np.add.at(Bd, r - lo, b['bid']); np.add.at(V, r - lo, b['vol'])
        rb = lambda x: (x - off) // G
        pad = lambda a: np.r_[a, np.zeros(4)][:4]
        rows.append(dict(t=b['t'], vol=V.sum(), nrow=n, nz=(V > 0).sum(), vmean=V[V > 0].mean(), vmed=np.median(V[V > 0]), vmax=V.max(),
                         T=pad(A[::-1]), B=pad(Bd), wT=rb(b['h']) - rb(max(b['o'], b['c'])), wB=rb(min(b['o'], b['c'])) - rb(b['l']), wtT=b['h'] - max(b['o'], b['c']), wtB=min(b['o'], b['c']) - b['l'], G=G))
    return pd.DataFrame(rows).set_index('t')
def sides(T, sym):
    g = gt[gt.sym == sym]; out = []
    for r in g.itertuples():
        if r.t_utc not in T.index: continue
        b = T.loc[r.t_utc]; s = b['T'] if r.side == 'T' else b['B']
        out.append(dict(t=r.t_utc, side=r.side, y=r.y, sample=r.sample, s0=s[0], s1=s[1], s2=s[2], s3=s[3], wick_r=b.wT if r.side == 'T' else b.wB, wick=b.wtT if r.side == 'T' else b.wtB))
    return pd.DataFrame(out)
def baselines(T, N, how, cur):
    sh = 0 if cur else 1
    if how == 'mean': rowb = T.vmean.shift(sh).rolling(N, min_periods=5).mean()
    elif how == 'median': rowb = T.vmed.shift(sh).rolling(N, min_periods=5).mean()
    elif how == 'pooled': rowb = T.vol.shift(sh).rolling(N, min_periods=5).sum() / T.nz.shift(sh).rolling(N, min_periods=5).sum()
    elif how == 'pooled_all': rowb = T.vol.shift(sh).rolling(N, min_periods=5).sum() / T.nrow.shift(sh).rolling(N, min_periods=5).sum()
    elif how == 'vmax': rowb = T.vmax.shift(sh).rolling(N, min_periods=5).mean()
    volb = T.vol.shift(sh).rolling(N, min_periods=5).mean()
    return rowb, volb
def best(S, T, N, how, cur, As, Cs, Ws=(1, 2, 3)):
    rowb, volb = baselines(T, N, how, cur)
    rb = S.t.map(rowb).values; vb = S.t.map(volb).values; vol = S.t.map(T.vol).values
    m3 = S[['s0', 's1', 's2']].max(1).values / rb; vr = vol / vb; y = S.y.values.astype(bool); res = []
    for a in As:
        for c in Cs:
            for w in Ws:
                res.append((f1(y, (m3 <= a) & (vr >= c) & (S.wick_r.values >= w)), a, c, w))
    return max(res, key=lambda z: z[0][0])
if __name__ == '__main__':
    TT = {s: bar_table(s) for s in CFG}; SS = {s: sides(TT[s], s) for s in CFG}
    import pickle; pickle.dump((TT, SS), open('_bt.pkl', 'wb'))
    for how in ('mean', 'median', 'pooled', 'pooled_all', 'vmax'):
        sc = {'mean': 1, 'median': 1.4, 'pooled': 1, 'pooled_all': 1.1, 'vmax': 0.4}[how]
        As = np.round(np.arange(0.2, 0.56, 0.025) * sc, 3)
        for N in (5, 10, 20, 30, 50, 100):
            for cur in (0, 1):
                print(how, N, cur, ' | '.join('%s %s' % (s, best(SS[s], TT[s], N, how, cur, As, (0, .6, .7, .75, .8, .85, .9, .95, 1.0, 1.1))) for s in CFG))
