"""Kiệt sức: dựng bảng đặc trưng theo (nến, phía) cho GC/NQ ở các khung, lưu X_<mã>_m<khung>.pkl (không commit).
Mỗi dòng: t, top (True = đỉnh/kiệt sức buy, soi Ask; False = đáy/kiệt sức sell, soi Bid), wick, rng, S<n> = tổng bên soi trên n tick từ cực trị vào trong,
O<n> = tổng bên đối diện, V<n> = tổng volume, Bm20/Bm = volume TB mỗi ô của 20 / N nến trước (N = nbase), R = biên độ TB N nến trước, own = volume TB mỗi ô của chính nến.
Chạy: python exh_common.py"""
import numpy as np, pandas as pd
from common_window import nbase
DATA = '../../../data-export/data-footprint/'
SYM = {'GC': ('fp_GCZ26_XCEC_Time_20260811-20261109_90d', 0.1, '2026-08-11'), 'NQ': ('fp_NQZ26_XCME_Time_20260826-20261124_90d', 0.25, '2026-09-14')}
NS = (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64)
P = '../nq_calib_2026-11-24/'

def ohlc(sym, m):
    f, tick, since = SYM[sym]
    B = pd.read_csv(DATA + f + '_bars.csv', usecols=['datetime', 'open', 'high', 'low', 'close']); B['dt'] = pd.to_datetime(B.datetime)
    B = B[B.dt >= since].sort_values('dt'); g = B.groupby(B.dt.dt.floor(f'{m}min'))
    o = pd.DataFrame({'o': g.open.first(), 'h': g.high.max(), 'l': g.low.min(), 'c': g.close.last()})
    return np.round(o / tick).astype(np.int64)

def table(sym, m, F=None, S=None, O=None, save=True):
    if F is None: F = pd.read_pickle(f'{P}F_{sym}_m{m}.pkl').sort_values(['t', 'tk']); S = pd.read_pickle(f'{P}S_{sym}_m{m}.pkl'); O = ohlc(sym, m)
    N = nbase(m)
    Bm20 = S['mean'].shift(1).rolling(20, min_periods=5).mean(); Bm = S['mean'].shift(1).rolling(N, min_periods=5).mean(); R = S.rng.shift(1).rolling(N, min_periods=5).mean()
    rows = []; tv = F.t.values; cut = np.r_[0, np.flatnonzero(tv[1:] != tv[:-1]) + 1, len(F)]
    tk = F.tk.values; bid = F.bid.values.astype(float); ask = F.ask.values.astype(float); vol = F.vol.values.astype(float); mx = max(NS)
    for i in range(len(cut) - 1):
        a, b = cut[i], cut[i + 1]; t = pd.Timestamp(tv[a])
        if t not in O.index: continue
        o, h, l, c = O.loc[t].values
        if h <= l: continue
        n = h - l + 1; A = np.zeros(n + mx); Bd = np.zeros(n + mx); V = np.zeros(n + mx)
        k = tk[a:b] - l; ok = (k >= 0) & (k < n)
        A[k[ok]] = ask[a:b][ok]; Bd[k[ok]] = bid[a:b][ok]; V[k[ok]] = vol[a:b][ok]
        for top in (True, False):
            if top: s, op, v = A[:n][::-1], Bd[:n][::-1], V[:n][::-1]
            else: s, op, v = Bd[:n], A[:n], V[:n]
            cs = np.cumsum(np.r_[s, np.zeros(mx)]); co = np.cumsum(np.r_[op, np.zeros(mx)]); cv = np.cumsum(np.r_[v, np.zeros(mx)])
            r = dict(t=t, top=top, wick=(h - max(o, c)) if top else (min(o, c) - l), rng=h - l, own=vol[a:b].mean(), nl=b - a, tot=vol[a:b].sum(), s_all=s.sum(),
                     Bm20=Bm20.get(t, np.nan), Bm=Bm.get(t, np.nan), R=R.get(t, np.nan))
            # số tick liên tiếp từ cực trị có bên soi = 0
            nz = np.flatnonzero(s > 0); r['zeros'] = int(nz[0]) if len(nz) else n
            for q in NS: r[f'S{q}'] = cs[q - 1]; r[f'O{q}'] = co[q - 1]; r[f'V{q}'] = cv[q - 1]
            r['cs'] = cs[:mx].astype(np.float32); r['co'] = co[:mx].astype(np.float32)
            rows.append(r)
    X = pd.DataFrame(rows)
    if save: X.to_pickle(f'X_{sym}_m{m}.pkl'); print(sym, m, len(X) // 2, 'nến')
    return X

if __name__ == '__main__':
    for sym in ('GC', 'NQ'):
        for m in (1, 5, 15, 30, 60): table(sym, m)


TOP = {'2026-11-18 12:35', '2026-11-18 12:45', '2026-11-18 12:50', '2026-11-18 13:30', '2026-11-18 13:45'}
BOT = {'2026-11-18 12:15', '2026-11-18 13:10', '2026-11-18 13:20', '2026-11-18 13:40', '2026-11-18 13:45', '2026-11-18 13:50'}

def corven_gt(full=False):
    """Bảng đặc trưng cho 26 nến M5 của chart CORVEN 18/11 (GC, 12:15-14:20 UTC), cột y = CORVEN có đánh dấu kiệt sức (11 dấu; nguồn: ../corven_m5_2026-11-18/exh_feats.py)."""
    f = 'fp_GCZ26_XCEC_Time_20261108-20261118_9d16h'
    L = pd.read_csv(DATA + f + '.csv'); B = pd.read_csv(DATA + f + '_bars.csv')
    F = pd.DataFrame(dict(t=pd.to_datetime(L.datetime), tk=np.round(L.price / 0.1).astype(np.int64), bid=L.bid_vol, ask=L.ask_vol, vol=L.volume)); F = F[F.vol > 0].sort_values(['t', 'tk'])
    S = F.groupby('t').agg(mean=('vol', 'mean'), hi=('tk', 'max'), lo=('tk', 'min')); S['rng'] = S.hi - S.lo
    O = np.round(B.set_index(pd.to_datetime(B.datetime))[['open', 'high', 'low', 'close']] / 0.1).astype(np.int64); O.columns = ['o', 'h', 'l', 'c']
    X = table('GC', 5, F, S, O, save=False)
    ts = X.t.dt.strftime('%Y-%m-%d %H:%M'); X['y'] = np.where(X.top, ts.isin(TOP), ts.isin(BOT))
    X['gt'] = (X.t >= '2026-11-18 12:15') & (X.t <= '2026-11-18 14:20')      # 26 nến của chart CORVEN
    return X if full else X[X.gt].copy()


def tail_base(X, n=6, N=20, how='median'):
    """Mức nền của ĐUÔI nến: trung vị (hoặc trung bình) của tổng bên soi trên n tick từ cực trị, lấy trên cả đỉnh lẫn đáy của N nến ĐÃ ĐÓNG trước (2N giá trị, cần >= 5 nến)."""
    col = f'S{n}'
    W = X.pivot(index='t', columns='top', values=col).sort_index()
    if how == 'mean':
        b = W.mean(axis=1).shift(1).rolling(N, min_periods=5).mean()
    else:
        v = W.values; b = pd.Series(np.nan, index=W.index)
        for i in range(5, len(W)):
            b.iloc[i] = np.median(v[max(0, i - N):i])
    return X.t.map(b).values
