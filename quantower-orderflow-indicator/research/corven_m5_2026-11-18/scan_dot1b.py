import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools, time
from score import *; from score_dots import *
F=pd.read_pickle('F_m5.pkl'); S=sample(F).copy().reset_index(drop=True)
met={'side':S.side,'vol':S.vol,'trades':S.trades,'adelta':S.delta.abs()}
bas={'B20_m':S.B20_m,'B20_mx':S.B20_mx,'bar_mean':S.bar_mean,'bar_max':S.bar_max,'B50_m':S.B50_m,'B20_p90':S.B20_p90,'B100_m':S.B100_m}
lms={0:np.ones(len(S),bool),1:S.locmax1,2:S.locmax2,3:S.locmax3}
res=[]; t0=time.time()
for (mn,mv),(bn,bv) in itertools.product(met.items(),bas.items()):
    rel=mv/bv
    for k in np.quantile(rel,np.linspace(0.88,0.995,30)):
        for w,lm in lms.items():
            for rt in (0,2,3):
                m=(rel>=k)&lm&(S.ratio>=rt); n=m.sum()
                if not 28<=n<=38: continue
                r=score_dots(S[m]); res.append((r['pix_f1'],r['n'],r['dot_hit'],r['blob_hit'],r['blob_extra'],mn,bn,round(k,2),w,rt))
res.sort(reverse=True)
for r in res[:20]: print(r)
print(len(res),time.time()-t0)
