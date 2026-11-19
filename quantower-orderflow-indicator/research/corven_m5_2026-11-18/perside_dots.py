"""Thử giả thuyết: chấm Bid (đỏ) và chấm Ask (xanh) xét RIÊNG từng bên (không phải 'bên trội'), chấm đỏ vẽ đè lên chấm xanh."""
import pandas as pd, numpy as np
from common import *; from score import sample; from score_dots import score_dots, y_of_tk
from rules import locmax, dot_rule2
F=pd.read_pickle('F_m5.pkl')
def perside(F,k,w,base='B20_m',metric='vol',occl=True):
    out=[]
    for s,c in (('ask','B'),('bid','S')):
        G=F.copy(); G['v']=G[s]
        lm=locmax(G,'v',w) if w>0 else np.ones(len(G),bool)
        H=G[(G.v>=k*G[base])&lm&(G.v>=9)].copy(); H['col']=c; out.append(H)
    R=pd.concat(out,ignore_index=True)   # ignore_index: nhãn dòng của Ask và Bid trùng nhau, nếu không .loc kéo nhầm cả dòng đã bị che (lỗi bản đầu, 36 thay vì 33)
    if occl:  # chấm xanh bị chấm đỏ cùng nến che (cách < 1 đường kính chấm ~7 tick)
        red=R[R.col=='S']; keep=[]
        for r in R.itertuples():
            if r.col=='B':
                rr=red[red.datetime==r.datetime]
                if ((rr.tk-r.tk).abs()<=6).any(): continue
            keep.append(r.Index)
        R=R.loc[keep]
    return R
S=sample(F)
print('hiện tại (bên trội, số lệnh):',score_dots(dot_rule2(S,2.4,3)))
res=[]
for base in ('B20_m','B20_mx','B20_med'):
    for k in np.round(np.arange(0.3,4.01,0.1),2):
        for w in (0,1,2,3,5):
            R=perside(S,k,w,base); sc=score_dots(R); res.append((sc['pix_f1'],base,k,w,sc))
res.sort(key=lambda r:-r[0])
for r in res[:10]: print(r)
