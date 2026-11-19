import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools, json
from score import *; from score_dots import *; from rules import *
F=pd.read_pickle('F_m5.pkl')
SMP=SAMPLE
def subset(F,bars): return F[F.datetime.isin(bars)]
# ---- BIG
def fit_big(bars):
    Fb=subset(F,bars); S=Fb  # features already contain prior-bar baselines
    gtb=[g for g in GT_BIG if g[0] in bars]
    import score as sc
    best=None; allr=[]
    lmc={w:locmax(S,'side',w) for w in (2,3,5,8)}
    for k in np.arange(0.3,1.21,0.05):
        for w in (2,3,5,8):
            for rt in (2,3,4,5):
                m=(S.side>=k*S.B20_mx)&lmc[w]&(S.side>=rt*S.weak.clip(lower=1)); sel=S[m]
                ours=marks_of(sel); h=len(match(ours,gtb,2)); n=len(ours); f1=2*h/(n+len(gtb)) if n else 0
                pen=0.0 if abs(n-len(gtb))<=3 else 0.03*(abs(n-len(gtb))-3)
                allr.append((f1-pen,round(k,2),w,rt,n,h))
    allr.sort(reverse=True); return allr
if __name__=='__main__':
    for name,bars in (('all26',SMP),('first13',SMP[:13]),('last13',SMP[13:]),('even',SMP[0::2]),('odd',SMP[1::2])):
        r=fit_big(bars); print(name,r[:3])
