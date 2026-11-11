"""Brainstorm luật nổ bóng, chấm bằng ghép 1-1 (±1 tick) với bóng CORVEN. Fit ngày 05/11, kiểm ngày 06/11."""
import numpy as np, pandas as pd, itertools
from io import StringIO
from bubble_common import LVL
rows=[l for l in open(LVL) if any(f',2026-11-0{d}' in l[:40] for d in (4,5,6,7))]
D=pd.read_csv(StringIO('bar_idx,datetime,price,bid_vol,ask_vol,volume,delta,trades,buy_trades,sell_trades,max_one_trade\n'+''.join(rows)),parse_dates=['datetime'])
D=D[D.volume>0].copy()
D['side']=D[['bid_vol','ask_vol']].max(axis=1); D['ad']=D.delta.abs(); D['tk']=(D.price*10).round().astype(int)
g=D.groupby('datetime')
def base(col): return D.datetime.map(g[col].mean().sort_index().shift(1).rolling(20,min_periods=5).mean())
D['Bv']=base('volume'); D['Bs']=base('side'); D['Bd']=base('ad')
D['barmean']=g.volume.transform('mean'); D['barmax']=g.volume.transform('max')
D['loc_max']=False
D=D.sort_values(['datetime','tk']).reset_index(drop=True)
O=pd.read_csv('corven_bubbles.csv',parse_dates=['time_utc']); O['tk']=(O.price*10).round().astype(int)
C=pd.read_csv('corven_bars_control.csv',parse_dates=['time_utc']); vis=set(C.time_utc)
O=O[O.time_utc.isin(vis)]; V=D[D.datetime.isin(vis)].copy()
cb={t:list(s.tk) for t,s in O.groupby('time_utc')}
def nms(P,key,gap):
    if gap<=0 or len(P)==0: return P
    out=[]
    for t,s in P.groupby('datetime',sort=False):
        taken=[]
        for tk,v,idx in sorted(zip(s.tk,s[key],s.index),key=lambda z:-z[1]):
            if all(abs(tk-x)>gap for x in taken): taken.append(tk); out.append(idx)
    return P.loc[out]
def score(P,day):
    times=[t for t in vis if str(t).startswith(day)]
    pb={t:list(s.tk) for t,s in P[P.datetime.isin(times)].groupby('datetime')}
    nC=sum(len(cb.get(t,[])) for t in times); nP=sum(len(pb.get(t,[])) for t in times); hit=0
    for t in times:
        a=pb.get(t,[]); b=cb.get(t,[])
        pairs=sorted((abs(x-y),i,j) for i,x in enumerate(a) for j,y in enumerate(b) if abs(x-y)<=1)
        ua=set(); ub=set()
        for _,i,j in pairs:
            if i in ua or j in ub: continue
            ua.add(i); ub.add(j); hit+=1
    ex=nP-hit; ms=nC-hit; f1=2*hit/max(1,nP+nC)
    return f1,nP,nC,hit,ex,ms
fams=[]
for k in np.arange(1.2,2.21,0.1):
  for gap in (0,1,2):
    fams.append((f'A side>={k:.1f}xB_vol gộp{gap}', (V.side>=k*V.Bv)&(V.side>=3),'side',gap))
    fams.append((f'B side>={k:.1f}xB_side gộp{gap}', (V.side>=k*V.Bs)&(V.side>=3),'side',gap))
    fams.append((f'C vol>={k+0.5:.1f}xB_vol gộp{gap}', (V.volume>=(k+0.5)*V.Bv)&(V.volume>=3),'volume',gap))
    fams.append((f'D side>={k:.1f}x max(B_vol, TB nến) gộp{gap}', (V.side>=k*np.maximum(V.Bv,V.barmean))&(V.side>=3),'side',gap))
    for kd in (1.5,2.0,2.5):
      fams.append((f'E (|delta|>={kd}xB_d hoặc vol>={k+1:.1f}xB_vol) gộp{gap}', ((V.ad>=kd*V.Bd)|(V.volume>=(k+1)*V.Bv))&(V.side>=3),'volume',gap))
res=[]
for name,m,key,gap in fams:
    P=nms(V[m],key,gap)
    a=score(P,'2026-11-05'); b=score(P,'2026-11-06')
    res.append((a[0],name,a,b))
res.sort(reverse=True)
print('top theo F1 ngày 05 (fit) -> kiểm ngày 06:  F1 | mình | CORVEN | trúng | thừa | sót')
for r in res[:15]:
    a,b=r[2],r[3]
    print(f'{r[1]:45s} 05: {a[0]:.3f} {a[1]}/{a[2]} thừa {a[4]} sót {a[5]} || 06: {b[0]:.3f} {b[1]}/{b[2]} thừa {b[4]} sót {b[5]}')
cur=[r for r in res if r[1]=='A side>=1.5xB_vol gộp0'][0]
print('LUẬT HIỆN TẠI',cur[1],cur[2],cur[3])
