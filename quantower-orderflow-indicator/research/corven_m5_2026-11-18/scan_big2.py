import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools
from score import *
import score as sc
F=pd.read_pickle('F_m5.pkl'); S=sample(F).copy().reset_index(drop=True)
def run(tol,agnostic):
    G=GT_BIG if not agnostic else [(t,tk,'X') for t,tk,c in GT_BIG]
    def sb(sel):
        ours=list(zip(sel.datetime,sel.tk,['X']*len(sel) if agnostic else sel.col)); p=match(ours,G,tol); return len(p)
    metrics={'side':S.side,'vol':S.vol,'trades':S.trades,'exc':S.exc.clip(lower=0)}
    bases={'1':1.0,'bar_mean':S.bar_mean,'bar_max':S.bar_max,'B20_m':S.B20_m,'B50_m':S.B50_m,'B20_mx':S.B20_mx}
    gates={'none':np.ones(len(S),bool),'lm2':S.locmax2,'lm3':S.locmax3,'lm5':S.locmax5,'r2':S.ratio>=2,'lm3r3':S.locmax3&(S.ratio>=3)}
    res=[]
    for (mn,mv),(bn,bv),(gn,gv) in itertools.product(metrics.items(),bases.items(),gates.items()):
        val=(mv/bv).where(gv,-1); order=val.sort_values(ascending=False)
        for N in (25,):
            res.append((sb(S.loc[order.index[:N]]),N,mn,bn,gn))
    res.sort(reverse=True); return res[:6]
for tol in (2,4):
    for ag in (False,True): print(tol,ag,run(tol,ag))
