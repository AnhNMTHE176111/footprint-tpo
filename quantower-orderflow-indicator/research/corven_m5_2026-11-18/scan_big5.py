import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools
from score import *
F=pd.read_pickle('F_m5.pkl'); S=sample(F).copy().reset_index(drop=True)
met={'vol':S.vol,'side':S.side,'trades':S.trades}
bas={'B20_m':S.B20_m,'B20_mx':S.B20_mx,'bar_mean':S.bar_mean,'B50_m':S.B50_m}
lms={0:np.ones(len(S),bool),1:S.locmax1,2:S.locmax2,3:S.locmax3,5:S.locmax5}
res=[]
for (mn,mv),(bn,bv) in itertools.product(met.items(),bas.items()):
    rel=mv/bv
    for k in np.quantile(rel,np.linspace(0.8,0.999,60)):
        for w,lm in lms.items():
            for rt in (0,1.5,2,3,4):
                m=(rel>=k)&lm&(S.ratio>=rt); n=m.sum()
                if not 12<=n<=45: continue
                r=score_big(S[m],2); res.append((round(r['f1'],3),r['hit'],int(n),mn,bn,round(k,2),w,rt))
res.sort(reverse=True)
for r in res[:25]: print(r)
