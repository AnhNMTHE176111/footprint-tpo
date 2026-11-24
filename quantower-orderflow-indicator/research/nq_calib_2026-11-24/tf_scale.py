"""Bộ số NQ tự nới theo độ rộng nến: w = max(8, round(R20 / D)), che = round(1,5 x w), k cố định.
R20 = biên độ (tick) trung bình 20 nến ĐÃ ĐÓNG trước. So mật độ chấm/nến của NQ với GC (bộ GC 2,8/±4/che 6) cùng khung."""
import sys, numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

def fast_dots(F, k, wbar, hbar, floor=9):
    """wbar, hbar: Series theo t (cửa sổ, che) của từng nến. Trả số chấm đỏ/xanh mỗi nến."""
    F = F.sort_values(['t', 'tk']).reset_index(drop=True)
    F['w'] = F.t.map(wbar).fillna(-1).astype(int); F['h'] = F.t.map(hbar).fillna(-1).astype(int)
    F = F[(F.w >= 0) & F.B_med.notna()].reset_index(drop=True)
    res = []
    for w, G in F.groupby('w'):
        G = G.reset_index(drop=True)
        lo = G.groupby('t').tk.transform('min'); bar_id = G.t.factorize()[0]
        # đặt các nến nối nhau trên một trục dày, chèn khoảng trống w+1 giữa nến
        spans = G.groupby('t').tk.agg(lambda x: x.max() - x.min() + 1).reindex(G.t.unique()).values
        off = np.concatenate([[0], np.cumsum(spans + w + 1)[:-1]])
        pos = off[bar_id] + (G.tk - lo).values
        N = pos.max() + 1
        out = {}
        for col in ('ask', 'bid'):
            A = np.zeros(N); A[pos] = G[col].values
            if w > 0:
                # max trên [i-w, i-1] và [i+1, i+w]
                pad = np.concatenate([np.zeros(w), A, np.zeros(w)])
                win = sliding_window_view(pad, w)            # win[j] = pad[j:j+w]
                left = win[np.arange(N)]                     # pad[i:i+w] = A[i-w:i]
                right = win[np.arange(N) + w + 1]            # pad[i+w+1:i+2w+1] = A[i+1:i+w+1]
                nm = np.maximum(left.max(1), right.max(1))[pos]
            else:
                nm = np.zeros(len(G))
            v = G[col].values
            out[col] = (v >= np.maximum(k * G.B_med.values, floor)) & (v > nm)
        G['red'] = out['bid']; G['blue'] = out['ask']
        res.append(G)
    G = pd.concat(res, ignore_index=True)
    # che xanh gần đỏ
    R = G[G.red][['t', 'tk']].rename(columns={'tk': 'rtk'})
    B = G[G.blue][['t', 'tk', 'h']].reset_index()
    m = B.merge(R, on='t', how='left'); hid = m[(m.h >= 0) & ((m.rtk - m.tk).abs() <= m.h)]['index'].unique()
    nred = G.red.sum(); nblue = len(B) - len(hid)
    return nred, nblue

def run(sym, m, k, rule):
    F = pd.read_pickle(f'F_{sym}_m{m}.pkl'); S = pd.read_pickle(f'S_{sym}_m{m}.pkl')
    R20 = S.rng.shift(1).rolling(20, min_periods=5).mean()
    w = R20.apply(lambda r: rule(r) if r == r else np.nan)
    h = (1.5 * w).round()
    r, b = fast_dots(F, k, w, h)
    n = S.B_med.notna().sum()
    return (r + b) / n, r / n, b / n, R20.median(), w.median()

if __name__ == '__main__':
    rows = []
    for m in (1, 5, 15, 30, 60):
        g = run('GC', m, 2.8, lambda r: 4); rows.append(dict(M=m, bo='GC bộ GC', cham=g[0], do=g[1], xanh=g[2], R20=g[3], w=g[4]))
        for name, k, rule in (('NQ cố định 3,5/8', 3.5, lambda r: 8),
                              ('NQ 3,5 D13', 3.5, lambda r: max(8, round(r / 13))),
                              ('NQ 3,5 D10', 3.5, lambda r: max(8, round(r / 10))),
                              ('NQ 3,5 D8', 3.5, lambda r: max(8, round(r / 8)))):
            x = run('NQ', m, k, rule); rows.append(dict(M=m, bo=name, cham=x[0], do=x[1], xanh=x[2], R20=x[3], w=x[4]))
        print(pd.DataFrame(rows[-5:]).round(2).to_string(index=False), flush=True)
