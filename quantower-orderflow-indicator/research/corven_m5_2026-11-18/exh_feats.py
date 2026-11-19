import pandas as pd, numpy as np
from common import *
TOP={'2026-11-18 12:35','2026-11-18 12:45','2026-11-18 12:50','2026-11-18 13:30','2026-11-18 13:45'}
BOT={'2026-11-18 12:15','2026-11-18 13:10','2026-11-18 13:20','2026-11-18 13:40','2026-11-18 13:45','2026-11-18 13:50'}
def exh_table(D,B,times=None):
    """one row per (bar, side T/B) with candidate features."""
    if times is None: times=sorted(D.datetime.unique())
    g=dict(tuple(D.groupby('datetime')))
    mean20={}; 
    st=D.groupby('datetime').agg(m=('vol','mean'),tot=('vol','sum')).sort_index()
    for w in (20,50): st['B%d_m'%w]=st.m.shift(1).rolling(w,min_periods=5).mean(); st['B%d_tot'%w]=st.tot.shift(1).rolling(w,min_periods=5).mean()
    rows=[]
    for t in times:
        if t not in g or t not in B.index: continue
        L=g[t].set_index('tk'); b=B.loc[t]
        hi=round(b.high*10); lo=round(b.low*10); o=round(b.open*10); c=round(b.close*10); rng=hi-lo
        for side in ('T','B'):
            ext=hi if side=='T' else lo; st_=-1 if side=='T' else 1; col='ask' if side=='T' else 'bid'; oc='bid' if side=='T' else 'ask'
            seq=[float(L[col].get(ext+st_*j,0)) for j in range(8)]
            oseq=[float(L[oc].get(ext+st_*j,0)) for j in range(8)]
            vseq=[float(L.vol.get(ext+st_*j,0)) for j in range(8)]
            wick=(hi-max(o,c)) if side=='T' else (min(o,c)-lo)
            closeaway=((hi-c) if side=='T' else (c-lo))/max(rng,1)
            r=dict(t=t,side=side,y=(t in TOP) if side=='T' else (t in BOT),wick=wick,rng=rng,ca=closeaway,delta=b.delta,bdir=np.sign(c-o),
                   bar_mean=st.m[t],B20_m=st.B20_m[t],B50_m=st.B50_m[t],tot=st.tot[t],B20_tot=st.B20_tot[t],nl=len(L),bvol=b.bar_volume,
                   closedelta=np.sign(b.delta)*(1 if side=='T' else -1))
            for n in (1,2,3,4,5,6): r['s%d'%n]=sum(seq[:n]); r['o%d'%n]=sum(oseq[:n]); r['v%d'%n]=sum(vseq[:n])
            r['sel1']=seq[0]; r['ext_vol']=vseq[0]
            r['exp_top']=0
            rows.append(r)
    return pd.DataFrame(rows)
