"""Bảng đặc trưng theo (nến, phía) cho các nến trong gt_sides.csv. G = số tick mỗi hàng (1 = từng tick), off = lệch mốc hàng."""
import numpy as np, pandas as pd, data

def side_arrays(b, top, G=1, off=0):
    """Mảng bên soi S, bên đối diện O, tổng V theo HÀNG, thứ tự từ cực trị đi vào trong. Kèm số tick của hàng cực trị nằm trong nến."""
    r = (b['tk'] - off) // G; lo = (b['l'] - off) // G; hi = (b['h'] - off) // G; n = hi - lo + 1
    A = np.zeros(n); Bd = np.zeros(n); V = np.zeros(n)
    np.add.at(A, r - lo, b['ask']); np.add.at(Bd, r - lo, b['bid']); np.add.at(V, r - lo, b['vol'])
    if top: return A[::-1], Bd[::-1], V[::-1], (b['h'] - off) % G + 1
    return Bd, A, V, G - (b['l'] - off) % G

def build(sym, G=1, off=0, t0=None, t1=None, bars=None):
    if bars is None: bars, tick = data.load(sym, t0, t1)
    rows = []; hist = []
    for i, b in enumerate(bars):
        o, h, l, c = b['o'], b['h'], b['l'], b['c']
        rb = lambda x: (x - off) // G
        for top in (True, False):
            S, O, V, nt = side_arrays(b, top, G, off)
            n = len(S); pad = lambda a, k: np.r_[a, np.zeros(max(0, k - len(a)))][:k]
            wick_t = (h - max(o, c)) if top else (min(o, c) - l)
            wick_r = (rb(h) - rb(max(o, c))) if top else (rb(min(o, c)) - rb(l))
            d = dict(t=b['t'], side='T' if top else 'B', rng=h - l, nrow=n, wick=wick_t, wick_r=wick_r, body=abs(c - o), up=int(c > o) - int(c < o), nt=nt,
                     vol=b['vol'].sum(), delta=b['ask'].sum() - b['bid'].sum(), s_tot=S.sum(), s_max=S.max(), v_max=V.max(), v_mean=V[V > 0].mean(), s_mean=S[S > 0].mean() if (S > 0).any() else 0,
                     poc_pos=int(np.argmax(V)), smax_pos=int(np.argmax(S)))
            for k in range(8): d[f's{k}'] = pad(S, 8)[k]; d[f'o{k}'] = pad(O, 8)[k]; d[f'v{k}'] = pad(V, 8)[k]
            nz = np.flatnonzero(S > 0); d['zeros'] = int(nz[0]) if len(nz) else n
            # ngữ cảnh: cực trị so với các nến trước / sau
            for N in (1, 3, 5, 10):
                prev = bars[max(0, i - N):i]
                if prev: d[f'hh{N}'] = int(h > max(p['h'] for p in prev)) if top else int(l < min(p['l'] for p in prev))
                else: d[f'hh{N}'] = 0
            nxt = bars[i + 1] if i + 1 < len(bars) else None
            d['nxt_sweep'] = int((nxt['h'] > h) if top else (nxt['l'] < l)) if nxt else -1
            rows.append(d)
    X = pd.DataFrame(rows)
    # nền lịch sử: TB volume mỗi hàng có giao dịch của 20 nến trước; trung vị s0, s_cum
    per = X[X.side == 'T'].set_index('t')
    base = per.v_mean.shift(1).rolling(20, min_periods=5).mean(); X['Bmean'] = X.t.map(base)
    X['Bvol'] = X.t.map(per.vol.shift(1).rolling(20, min_periods=5).mean()); X['Brng'] = X.t.map(per.rng.shift(1).rolling(20, min_periods=5).mean())
    X['Bvmax'] = X.t.map(per.v_max.shift(1).rolling(20, min_periods=5).mean())
    return X

if __name__ == '__main__':
    gt = pd.read_csv('gt_sides.csv', parse_dates=['t_utc'])
    out = []
    for sym, G, off in (('NQ', 1, 0), ('NQ', 8, 4), ('NQ', 4, 0), ('GC', 1, 0), ('GC', 2, 1)):
        g = gt[gt.sym == sym]; t0 = g.t_utc.min() - pd.Timedelta(hours=3); t1 = g.t_utc.max() + pd.Timedelta(minutes=5)
        X = build(sym, G, off, t0, t1); X['sym'] = sym; X['G'] = G
        X = X.merge(g[['t_utc', 'side', 'y', 'sample']], left_on=['t', 'side'], right_on=['t_utc', 'side']); out.append(X); print(sym, G, len(X), X.y.sum())
    pd.concat(out).to_pickle('feats.pkl')
