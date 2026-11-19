import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools
from score import *
from stackfeat import *
F=pd.read_pickle('F_m5.pkl'); S=sample(F).copy().reset_index(drop=True)
T={R:add_stack(S,R) for R in (2,3,4,6)}
met={'vol':S.vol,'side':S.side,'trades':S.trades}
bas={'bar_max':S.bar_max,'B20_m':S.B20_m,'B20_mx':S.B20_mx,'bar_mean':S.bar_mean}
lms={0:np.ones(len(S),bool),2:S.locmax2,3:S.locmax3,5:S.locmax5}
res=[]
for R in T:
  imb=T[R].imb; stk=T[R].stk
  for sk in (1,2,3):
    g=imb&(stk>=sk)
    for (mn,mv),(bn,bv) in itertools.product(met.items(),bas.items()):
      rel=mv/bv
      for k in np.arange(0.3,3.01,0.1):
        for w,lm in lms.items():
          m=(rel>=k)&lm&g
          n=m.sum()
          if not 18<=n<=32: continue
          r=score_big(S[m],2); res.append((r['hit'],int(n),R,sk,mn,bn,round(k,2),w))
res.sort(reverse=True)
for r in res[:25]: print(r)
print(len(res))
