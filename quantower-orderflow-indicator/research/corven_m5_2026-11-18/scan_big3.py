import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools
from score import *
F=pd.read_pickle('F_m5.pkl')
# add wider local maxima of vol
D=F; idx=D.set_index(['datetime','tk'])
def locmax(col,k):
    mx=np.zeros(len(D))
    for o in range(-k,k+1):
        if o==0: continue
        j=pd.MultiIndex.from_arrays([D.datetime,D.tk+o]); mx=np.maximum(mx,idx[col].reindex(j).fillna(0).values)
    return D[col].values>mx
for k in (8,):
    F['vlm%d'%k]=locmax('vol',k)
S=sample(F).copy().reset_index(drop=True)
res=[]
met={'vol':S.vol,'side':S.side,'trades':S.trades}
bas={'bar_max':S.bar_max,'B20_m':S.B20_m,'B20_mx':S.B20_mx,'bar_mean':S.bar_mean,'B50_m':S.B50_m,'B20_p90':S.B20_p90}
lms={0:np.ones(len(S),bool),1:S.locmax1,2:S.locmax2,3:S.locmax3,5:S.locmax5,8:S.vlm8}
for (mn,mv),(bn,bv) in itertools.product(met.items(),bas.items()):
    rel=mv/bv
    for k in np.arange(0.3,4.01,0.1):
        for w,lm in lms.items():
            for rt in (0,2,3,5):
                for fl in (0,9,15):
                    m=(rel>=k)&lm&(S.ratio>=rt)&(S.side>=fl)
                    n=m.sum()
                    if not 18<=n<=32: continue
                    r=score_big(S[m],2); res.append((r['hit'],n,mn,bn,round(k,2),w,rt,fl))
res.sort(reverse=True)
for r in res[:30]: print(r)
print(len(res))
