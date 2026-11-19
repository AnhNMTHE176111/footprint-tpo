import pandas as pd, numpy as np
from common import *
def build(D,B,N=20):
    """per-level feature table for every cell."""
    D=D.copy()
    g=D.groupby('datetime')
    D['bar_mean']=g.vol.transform('mean'); D['bar_med']=g.vol.transform('median'); D['bar_max']=g.side.transform('max'); D['bar_tot']=g.vol.transform('sum')
    D['bar_sd']=g.vol.transform('std').fillna(0); D['nlev']=g.vol.transform('size')
    D['rank']=g.side.rank(ascending=False,method='first')
    D['z']=(D.side-D.bar_mean)/D.bar_sd.replace(0,np.nan)
    D['delta']=D.ask-D.bid
    D['ratio']=D.side/(D.weak.clip(lower=1))
    D['dom_frac']=D.side/D.vol
    D['exc']=D.vol-D.trades
    D['avgsz']=D.vol/D.trades.clip(lower=1)
    st=pd.DataFrame({'m':g.vol.mean(),'mx':g.side.max(),'tot':g.vol.sum(),'med':g.vol.median(),'p90':g.vol.quantile(0.9)}).sort_index()
    for w in (10,20,50,100):
        for c in ('m','mx','tot','med','p90'):
            D['B%d_%s'%(w,c)]=D.datetime.map(st[c].shift(1).rolling(w,min_periods=5).mean())
    # pooled percentile baseline: per-level side distribution over prior 20 bars -> 90th pct etc computed via bars
    # local max of dominant side among +-k neighbours (by tick, same bar)
    D['key']=D.datetime+'_'+D.tk.astype(str)
    idx=D.set_index(['datetime','tk'])
    for k in (1,2,3,5):
        mx=np.zeros(len(D))
        for o in range(-k,k+1):
            if o==0: continue
            j=pd.MultiIndex.from_arrays([D.datetime,D.tk+o])
            v=idx.side.reindex(j).fillna(0).values
            mx=np.maximum(mx,v)
        D['locmax%d'%k]=D.side>mx
    # diagonal imbalance ask[p] vs bid[p-1] and bid[p] vs ask[p+1]
    ja=pd.MultiIndex.from_arrays([D.datetime,D.tk-1]); jb=pd.MultiIndex.from_arrays([D.datetime,D.tk+1])
    D['bid_below']=idx.bid.reindex(ja).fillna(0).values; D['ask_above']=idx.ask.reindex(jb).fillna(0).values
    D['diag_ask']=D.ask/(D.bid_below.clip(lower=1)); D['diag_bid']=D.bid/(D.ask_above.clip(lower=1))
    D['diag']=np.where(D.col=='B',D.diag_ask,D.diag_bid)
    b=B[['high','low','open','close']].copy(); b['hi']=(b.high*10).round().astype(int); b['lo']=(b.low*10).round().astype(int)
    D=D.join(b[['hi','lo']],on='datetime')
    D['d_hi']=D.hi-D.tk; D['d_lo']=D.tk-D.lo
    return D
