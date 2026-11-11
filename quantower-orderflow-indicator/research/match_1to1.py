"""Ghép 1-1 bóng của mình với bóng CORVEN (mỗi bóng chỉ được ghép 1 lần, lệch <= tol tick, cùng nến).
Đếm: trúng, thừa (mình có - CORVEN không), sót (CORVEN có - mình không). Thử nhiều hệ số k."""
import numpy as np, pandas as pd
from io import StringIO
from bubble_common import LVL
rows=[l for l in open(LVL) if any(f',2026-11-0{d}' in l[:40] for d in (4,5,6,7))]
D=pd.read_csv(StringIO('bar_idx,datetime,price,bid_vol,ask_vol,volume,delta,trades,buy_trades,sell_trades,max_one_trade\n'+''.join(rows)),parse_dates=['datetime'])
D['side']=D[['bid_vol','ask_vol']].max(axis=1); D['tk']=(D.price*10).round().astype(int)
g=D[D.volume>0].groupby('datetime'); B=(g.volume.sum()/g.volume.count()).sort_index()
D['B']=D.datetime.map(B.shift(1).rolling(20,min_periods=5).mean())
O=pd.read_csv('corven_bubbles.csv',parse_dates=['time_utc']); O['tk']=(O.price*10).round().astype(int)
C=pd.read_csv('corven_bars_control.csv',parse_dates=['time_utc']); vis=set(C.time_utc)
O=O[O.time_utc.isin(vis)]; V=D[D.datetime.isin(vis)]
cb={t:sorted(s.tk) for t,s in O.groupby('time_utc')}
def run(k,tol=1,topn=0):
    P=V[(V.side>=k*V.B)&(V.side>=3)]
    if topn: P=P.sort_values('side',ascending=False).groupby('datetime').head(topn)
    pb={t:sorted(s.tk) for t,s in P.groupby('datetime')}
    hit=0; per=[]
    for t in vis:
        a=list(pb.get(t,[])); b=list(cb.get(t,[]))
        pairs=sorted((abs(x-y),i,j) for i,x in enumerate(a) for j,y in enumerate(b) if abs(x-y)<=tol)
        ua=set(); ub=set(); h=0
        for _,i,j in pairs:
            if i in ua or j in ub: continue
            ua.add(i); ub.add(j); h+=1
        hit+=h; per.append((len(b),len(a),h))
    nP=len(P); nC=len(O)
    return k,tol,nC,nP,hit,nP-hit,nC-hit,per
print('k  tol | CORVEN | minh | trung | THUA | SOT | thua/minh | sot/CORVEN')
for k in (1.5,1.6,1.7,1.8,2.0,2.2):
    for tol in (1,):
        k_,t,nC,nP,h,ex,ms,per=run(k,tol)
        print(f'{k} {t} | {nC} | {nP} | {h} | {ex} | {ms} | {ex/nP:.0%} | {ms/nC:.0%}')
# phân bố theo nến cho k=1.5
*_,per=run(1.5)
per=pd.DataFrame(per,columns=['corven','minh','trung'])
per['diff']=per.minh-per.corven
print('k=1.5 chênh số bóng/nến (mình - CORVEN):',per['diff'].value_counts().sort_index().to_dict())
print('nến mình nhiều gấp đôi CORVEN trở lên (CORVEN>=2):',int(((per.minh>=2*per.corven)&(per.corven>=2)).sum()),'/',int((per.corven>=2).sum()))
print('nến CORVEN 0 bóng mà mình có:',int(((per.corven==0)&(per.minh>0)).sum()),'/',int((per.corven==0).sum()))
# Bóng thừa nằm đâu? Thử gộp ô liền kề (giữ ô lớn nhất trong cụm lệch <= g tick)
def nms(P,gap):
    keep=[]
    for t,s in P.groupby('datetime'):
        s=s.sort_values('side',ascending=False); taken=[]
        for _,r in s.iterrows():
            if all(abs(r.tk-x)>gap for x in taken): taken.append(r.tk); keep.append(r)
    return pd.DataFrame(keep)
def score(P,tol=1):
    pb={t:sorted(s.tk) for t,s in P.groupby('datetime')}; hit=0
    for t in vis:
        a=pb.get(t,[]); b=cb.get(t,[])
        pairs=sorted((abs(x-y),i,j) for i,x in enumerate(a) for j,y in enumerate(b) if abs(x-y)<=tol)
        ua=set(); ub=set()
        for _,i,j in pairs:
            if i in ua or j in ub: continue
            ua.add(i); ub.add(j); hit+=1
    return len(P),hit,len(P)-hit,len(O)-hit
print('--- gộp ô liền kề')
for k in (1.3,1.4,1.5,1.6):
    base=V[(V.side>=k*V.B)&(V.side>=3)]
    for gap in (0,1,2):
        P=base if gap==0 else nms(base,gap)
        n,h,ex,ms=score(P)
        print(f'k={k} gộp±{gap}: mình {n} | trúng {h} | THỪA {ex} ({ex/n:.0%}) | SÓT {ms} ({ms/len(O):.0%})')
# CORVEN có bóng liền kề nhau không?
adj=sum(1 for t,b in cb.items() for i in range(1,len(b)) if b[i]-b[i-1]==1)
print('cặp bóng CORVEN liền nhau 1 tick:',adj,'/',len(O))
