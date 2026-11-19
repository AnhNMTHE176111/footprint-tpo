import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools
from score import *
F=pd.read_pickle('F_m5.pkl'); S=sample(F).copy().reset_index(drop=True)
S['adelta']=S.delta.abs()
metrics={'side':S.side,'vol':S.vol,'adelta':S.adelta,'exc':S.exc.clip(lower=0),'ratio':S.ratio,'diag':S.diag,'avgsz':S.avgsz,'trades':S.trades}
bases={'1':1.0,'bar_mean':S.bar_mean,'bar_med':S.bar_med,'bar_max':S.bar_max,'bar_tot':S.bar_tot,'B10_m':S.B10_m,'B20_m':S.B20_m,'B50_m':S.B50_m,'B100_m':S.B100_m,'B20_mx':S.B20_mx,'B20_p90':S.B20_p90,'B50_p90':S.B50_p90}
gates={'none':np.ones(len(S),bool),'lm1':S.locmax1,'lm2':S.locmax2,'lm3':S.locmax3,'lm5':S.locmax5,'r2':S.ratio>=2,'r3':S.ratio>=3,'lm2r2':S.locmax2&(S.ratio>=2),'lm3r3':S.locmax3&(S.ratio>=3),'d2':S.diag>=2,'d3':S.diag>=3,
 'wick':(S.d_hi<=15)|(S.d_lo<=15),'wick30':(S.d_hi<=30)|(S.d_lo<=30)}
res=[]
for (mn,mv),(bn,bv),(gn,gv) in itertools.product(metrics.items(),bases.items(),gates.items()):
    val=(mv/bv) if not np.isscalar(bv) else mv/bv
    val=val.where(gv,-1)
    order=val.sort_values(ascending=False)
    for N in (20,25,30):
        sel=S.loc[order.index[:N]]
        r=score_big(sel,2); res.append((r['hit'],N,mn,bn,gn,r['f1']))
res.sort(reverse=True)
for r in res[:40]: print(r)
print(len(res))
