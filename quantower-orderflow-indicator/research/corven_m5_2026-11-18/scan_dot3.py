import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools, time
from score import *; from score_dots import *
F=pd.read_pickle('F_m5.pkl'); S=sample(F).copy().reset_index(drop=True)
S['share']=S.side/S.bar_tot; S['tshare']=S.trades/S.bar_tot
S['zt']=(S.trades-S.groupby('datetime').trades.transform('mean'))/S.groupby('datetime').trades.transform('std')
S['vs20tot']=S.side/S.B20_tot; S['t_B20tot']=S.trades/S.B20_tot
feats={'share':S.share,'tshare':S.tshare,'z':S.z,'zt':S.zt,'vs20tot':S.vs20tot,'t_B20tot':S.t_B20tot,'side/trades':S.side,'abs_side':S.side,'abs_trades':S.trades,'abs_vol':S.vol}
lms={0:np.ones(len(S),bool),2:S.locmax2,3:S.locmax3}
res=[]
for fn,fv in feats.items():
    for k in np.quantile(fv,np.linspace(0.85,0.995,40)):
        for w,lm in lms.items():
            m=(fv>=k)&lm; n=m.sum()
            if not 25<=n<=48: continue
            r=score_dots(S[m]); res.append((r['pix_f1'],r['n'],r['dot_hit'],r['blob_hit'],r['blob_extra'],fn,round(k,4),w))
res.sort(reverse=True)
for r in res[:20]: print(r)
