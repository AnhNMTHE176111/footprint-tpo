import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from score import *; from score_dots import *; from rules import *
import score_dots as sd
F=pd.read_pickle('F_m5.pkl')
def scored(S,bars):
    """score_dots restricted to given bars"""
    full=sd.GT_DOT
    sd.GT_DOT=[g for g in full if g[0] in bars]
    try: return sd.score_dots(S)
    finally: sd.GT_DOT=full
def fit(bars,lo=1.0,hi=1.6,metric='trades'):
    S=F[F.datetime.isin(bars)].reset_index(drop=True); res=[]
    for w in (0,1,2,3,5):
        lm=locmax(S,metric,w) if w>0 else np.ones(len(S),bool)
        for k in np.arange(1.0,5.01,0.1):
            m=(S[metric]>=k*S.B20_m)&lm; n=m.sum()
            if not lo*len(bars)<=n<=hi*len(bars): continue
            r=scored(S[m],bars); res.append((r['pix_f1'],round(k,1),w,r['n'],r['dot_hit'],r['blob_hit'],r['blob_extra']))
    res.sort(reverse=True); return res
if __name__=='__main__':
    for name,bars in (('all26',SAMPLE),('first13',SAMPLE[:13]),('last13',SAMPLE[13:]),('even',SAMPLE[0::2]),('odd',SAMPLE[1::2])):
        print(name,fit(bars)[:3])
