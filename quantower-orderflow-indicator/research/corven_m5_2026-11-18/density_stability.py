import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools
from common import *; from feats import build; from rules import *; from exh_feats import exh_table; from score import *; import score_dots as sd
from final_eval import P, exh_score
def load_days(path,days):
    ch=[]
    for c in pd.read_csv(str(path)+'.csv',chunksize=500000):
        c=c[c.datetime.str[:10].isin(days)]
        if len(c): ch.append(c)
    D=pd.concat(ch); B=pd.read_csv(str(path)+'_bars.csv'); B=B[B.datetime.str[:10].isin(days)]
    D=D[D.volume>0].copy(); D['tk']=(D.price*10).round().astype(int); D['datetime']=D.datetime.str[:16]; B['datetime']=B.datetime.str[:16]
    D=D.rename(columns={'bid_vol':'bid','ask_vol':'ask','volume':'vol'}); D['side']=D[['bid','ask']].max(axis=1); D['weak']=D[['bid','ask']].min(axis=1); D['col']=np.where(D.ask>D.bid,'B','S')
    return D.sort_values(['datetime','tk']).reset_index(drop=True),B.set_index('datetime')
def dens(F,E,only=None):
    if only is not None: F=F[F.datetime.str[:10]==only]; E=E[E.t.str[:10]==only]
    F=F[F.B20_m.notna()]; nb=F.datetime.nunique()
    b=big_rule(F,**P['big']); d=dot_rule2(F,**P['dot']); e=exh_rule(E[E.B20_m.notna()],**P['exh'])
    return dict(bars=nb,big=round(len(b)/nb,3),dot=round(len(d)/nb,3),exh=round(len(e)/nb,3),big_n=len(b),dot_n=len(d),exh_n=len(e))
if __name__=='__main__':
    F=pd.read_pickle('F_m5.pkl'); E=pd.read_pickle('E_m5.pkl')
    print('M5 full 9d16h',dens(F,E))
    print('M5 sample-day 2026-11-18',dens(F,E,'2026-11-18'))
    print('CORVEN (sample 26 bars): big 25/26=0.96, dot ~33/26=1.27 (16 blobs), exh 11/26=0.42')
    D,B=load_days(M1,['2026-11-04','2026-11-05'])
    F1=build(D,B); E1=exh_table(D,B,sorted(D.datetime.unique())); print('M1 loaded',len(D),'rows',D.datetime.nunique(),'bars')
    # B20 for E1 comes from exh_table: ok
    print('M1 2026-11-05',dens(F1,E1,'2026-11-05'))
