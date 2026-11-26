"""Nạp nến + footprint theo tick. bars: list dict(t, o,h,l,c (tick), lv={tick:(bid,ask,vol)})."""
import os, pickle, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '../../../data-export/data-footprint/')
P = os.path.join(HERE, '../nq_calib_2026-11-24/')
SYM = {'GC': ('fp_GCZ26_XCEC_Time_20260811-20261109_90d', 0.1, '2026-08-11'),
       'NQ': ('fp_NQZ26_XCME_Time_20260826-20261124_90d', 0.25, '2026-09-14'),
       'GC18': ('fp_GCZ26_XCEC_Time_20261108-20261118_9d16h', 0.1, '2026-11-08')}

def load(sym, t0=None, t1=None, mins=1):
    f, tick, since = SYM[sym]
    cache = os.path.join(HERE, f'_cache_{sym}.pkl')
    if os.path.exists(cache): F, B = pickle.load(open(cache, 'rb'))
    else:
        d = pd.read_csv(DATA + f + '.csv', usecols=['datetime', 'price', 'bid_vol', 'ask_vol', 'volume'])
        F = pd.DataFrame(dict(t=pd.to_datetime(d.datetime), tk=np.round(d.price / tick).astype(np.int64), bid=d.bid_vol, ask=d.ask_vol, vol=d.volume))
        F = F[(F.vol > 0) & (F.t >= since)]
        B = pd.read_csv(DATA + f + '_bars.csv', usecols=['datetime', 'open', 'high', 'low', 'close']); B['t'] = pd.to_datetime(B.datetime)
        B = B[B.t >= since].drop(columns='datetime')
        for c in 'open high low close'.split(): B[c] = np.round(B[c] / tick).astype(np.int64)
        pickle.dump((F, B), open(cache, 'wb'))
    if t0 is not None: F = F[(F.t >= t0) & (F.t <= t1)]; B = B[(B.t >= t0) & (B.t <= t1)]
    if mins != 1:
        F = F.assign(t=F.t.dt.floor(f'{mins}min')).groupby(['t', 'tk'], as_index=False).sum()
        g = B.groupby(B.t.dt.floor(f'{mins}min')); B = pd.DataFrame(dict(open=g.open.first(), high=g.high.max(), low=g.low.min(), close=g.close.last())).reset_index()
    F = F.sort_values(['t', 'tk']); B = B.sort_values('t')
    tv = F.t.values; cut = np.r_[0, np.flatnonzero(tv[1:] != tv[:-1]) + 1, len(F)]
    tk = F.tk.values; bid = F.bid.values; ask = F.ask.values; vol = F.vol.values
    lvs = {}
    for i in range(len(cut) - 1):
        a, b = cut[i], cut[i + 1]
        lvs[tv[a]] = (tk[a:b], bid[a:b].astype(float), ask[a:b].astype(float), vol[a:b].astype(float))
    bars = []
    for t, o, h, l, c in zip(B.t.values, B.open.values, B.high.values, B.low.values, B.close.values):
        x = lvs.get(t)
        if x is None: continue
        bars.append(dict(t=pd.Timestamp(t), o=int(o), h=int(h), l=int(l), c=int(c), tk=x[0], bid=x[1], ask=x[2], vol=x[3]))
    return bars, tick
