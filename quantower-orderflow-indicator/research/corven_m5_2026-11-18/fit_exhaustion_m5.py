import pandas as pd, itertools
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]   # chay duoc tu bat ky thu muc nao
F=str(REPO/'data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h')
D=pd.read_csv(F+'.csv'); B=pd.read_csv(F+'_bars.csv')
D=D[D.datetime.str.startswith('2026-11-18')]; B=B[B.datetime.str.startswith('2026-11-18')]
D['t']=D.datetime.str[11:16]; B['t']=B.datetime.str[11:16]; B=B.set_index('t')
top={'12:35','12:45','12:50','13:30','13:45'}; bot={'12:15','13:10','13:20','13:40','13:45','13:50'}
times=[t for t in B.index if '12:15'<=t<='14:25']
feat=[]
for t in times:
    L=D[D.t==t]; L=L.assign(tk=(L.price*10).round().astype(int)).set_index('tk')
    b=B.loc[t]; hi=round(b.high*10); lo=round(b.low*10); o=round(b.open*10); c=round(b.close*10)
    mean=L.volume[L.volume>0].mean(); rng=hi-lo
    g=lambda k,col: float(L[col].get(k,0))
    for side in ('T','B'):
        ext=hi if side=='T' else lo; st=-1 if side=='T' else 1; col='ask_vol' if side=='T' else 'bid_vol'
        seq=[g(ext+st*j,col) for j in range(6)]
        row2=seq[0]+seq[1]
        wick=(hi-max(o,c)) if side=='T' else (min(o,c)-lo)
        closeaway=((hi-c) if side=='T' else (c-lo))/max(rng,1)
        feat.append(dict(t=t,side=side,y=(t in (top if side=='T' else bot)),e=seq[0],r2=row2,s3=sum(seq[:3]),mean=mean,wick=wick,ca=closeaway,delta=b.delta,rng=rng))
F=pd.DataFrame(feat)
print(F.groupby('y')[['e','r2','s3','wick','ca','rng']].describe().T.to_string())
res=[]
for s3 in range(3,12):
  for w in (1,3,5,8,10):
    for rel in (0,):
      p=(F.s3<=s3)&(F.wick>=w)
      tp=(p&F.y).sum(); n=p.sum(); res.append((2*tp/(n+11),s3,w,n,tp))
    for r in (0.2,0.3,0.4,0.5):
      p=(F.s3<=r*F['mean'])&(F.wick>=w); tp=(p&F.y).sum(); n=p.sum(); res.append((2*tp/(n+11),f'rel{r}',w,n,tp))
cur=((F.e<=0.1*F['mean'])&(F.wick>=1)); print('current small-only',cur.sum(),(cur&F.y).sum())
# LUAT DA CHON (2026-11-18): rau >= 3 tick VA tong ben soi (Ask o dinh, Bid o day) 3 tick tu cuc tri vao trong <= 0,5 x TB volume/muc
ch=(F.s3<=0.5*F['mean'])&(F.wick>=3); tp=(ch&F.y).sum(); n=ch.sum()
print(f'CHOSEN RULE (rau >= 3 tick, tong 3 tick <= 0,5 x TB/muc): {n} dau, {tp} trung / {F.y.sum()} dau CORVEN, F1 {2*tp/(n+F.y.sum()):.2f}')
for r in sorted(res,key=lambda x:-x[0])[:14]: print(r)
print('--- rel only')
for r in sorted([x for x in res if isinstance(x[1],str)],key=lambda x:-x[0])[:6]: print(r)
for r in (0.2,0.25,0.3,0.35,0.4):
  for w in (3,):
    p=(F.s3<=r*F['mean'])&(F.wick>=w)&(F.e<=0.1*F['mean']+1e-9); tp=(p&F.y).sum(); n=p.sum(); print('rel+e',r,w,n,tp,2*tp/(n+11))
