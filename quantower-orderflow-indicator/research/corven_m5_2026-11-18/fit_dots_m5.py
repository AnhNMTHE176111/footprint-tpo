import os
import pandas as pd, numpy as np
F=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','data-export','data-footprint','fp_GCZ26_XCEC_Time_20261108-20261118_9d16h.csv')
D=pd.read_csv(F); D=D[D.volume>0].copy(); D['tk']=(D.price*10).round().astype(int); D['datetime']=D.datetime.str[:16]
OFF=-0.25; P=lambda y:3792-(y-12.7)/14.0+OFF
# blobs: (bar, colour, y0, y1) from segment_chart output (solid red/blue)
BL=[(0,'B',252,261),(2,'R',352,358),(3,'B',348,363),(3,'R',364,377),(4,'R',460,516),(5,'R',540,548),(6,'B',545,557),(6,'R',571,599),
(7,'R',605,624),(8,'R',650,660),(14,'B',224,248),(21,'B',80,93),(22,'B',77,84),(24,'B',174,192),(24,'R',194,198),(25,'R',194,203),(26,'R',208,214)]
t0=pd.Timestamp('2026-11-18 12:15')
blobs=[((t0+pd.Timedelta(minutes=5*b)).strftime('%Y-%m-%d %H:%M'),c,P(y1-4),P(y0+4)) for b,c,y0,y1 in BL]
times=[(t0+pd.Timedelta(minutes=5*k)).strftime('%Y-%m-%d %H:%M') for k in range(26)]  # drop live 14:25
blobs=[b for b in blobs if b[0] in times]
def build(rt,off):
    R=D.assign(row=(D.tk-off)//rt).groupby(['datetime','row'],as_index=False).agg(bid=('bid_vol','sum'),ask=('ask_vol','sum'),vol=('volume','sum'))
    R['side']=R[['bid','ask']].max(axis=1); R['weak']=R[['bid','ask']].min(axis=1); R['pos']=(R.row*rt+off+(rt-1)/2)/10
    g=R.groupby('datetime'); st=pd.DataFrame({'mean':g.vol.mean(),'maxs':g.side.max(),'bv':g.vol.sum()}).sort_index()
    for c in st.columns: R=R.merge(st[c].shift(1).rolling(20,min_periods=5).mean().rename('B_'+c),left_on='datetime',right_index=True)
    return R[R.datetime.isin(times)]
def score(Pr,tol=0.15):
    hitb=0; fp=0; colok=0
    for t in times:
        bb=[b for b in blobs if b[0]==t]; pp=Pr[Pr.datetime==t]
        got=[False]*len(bb)
        for x in pp.itertuples():
            c='B' if x.ask>x.bid else 'R'; m=False
            for i,b in enumerate(bb):
                if b[2]-tol<=x.pos<=b[3]+tol:
                    m=True; 
                    if c==b[1]: got[i]=True
            if not m: fp+=1
        hitb+=sum(got)
    rec=hitb/len(blobs); prec=1-fp/max(1,len(Pr))
    return len(Pr),hitb,fp,round(2*rec*prec/(rec+prec+1e-9),3)
print('blobs',len(blobs))
res=[]
for rt,off in ((1,0),(2,1)):
    R=build(rt,off)
    for base in ('B_mean','B_maxs'):
        for k in np.arange(0.5,4.01,0.1):
            for imb in (0,1.5,2,3):
                Pr=R[(R.side>=k*R[base])&((imb==0)|(R.side>=imb*R.weak))]
                res.append((score(Pr),rt,base,round(k,2),imb))
res.sort(key=lambda r:-r[0][3])
for r in res[:15]: print(r)
print('=== own-bar relative & diagonal imbalance')
res=[]
for rt,off in ((1,0),(2,1)):
    R=build(rt,off)
    R['own']=R.groupby('datetime').vol.transform('mean')
    for k in np.arange(1.5,6.01,0.25):
        for imb in (0,2,3):
            Pr=R[(R.side>=k*R.own)&((imb==0)|(R.side>=imb*R.weak))]
            res.append((score(Pr),'own',rt,round(k,2),imb))
# diagonal per tick
T=D[D.datetime.isin(times)].copy()
T=T.set_index(['datetime','tk'])
bidmap=T.bid_vol.to_dict(); askmap=T.ask_vol.to_dict()
rows=[]
for (t,tk),r in T.iterrows():
    a=r.ask_vol; b=r.bid_vol
    bl=bidmap.get((t,tk-1),0); au=askmap.get((t,tk+1),0)
    rows.append((t,tk,a,b,bl,au))
X=pd.DataFrame(rows,columns=['datetime','tk','a','b','bl','au']); X['pos']=X.tk/10
for ratio in (3,4,5,8):
  for mv in (5,10,15,20,30,40):
    sa=X[(X.a>=mv)&(X.a>=ratio*X.bl)].assign(ask=1,bid=0); sb=X[(X.b>=mv)&(X.b>=ratio*X.au)].assign(ask=0,bid=1)
    Pr=pd.concat([sa,sb]); res.append((score(Pr),'diag',ratio,mv,0))
res.sort(key=lambda r:-r[0][3])
for r in res[:12]: print(r)
print('=== detail 2tick k1.6')
R=build(2,1)
big=(R.side>=1.25*R.B_mean)&(R.side>=3*R.weak)
Pr=R[(R.side>=1.6*R.B_mean)]
for t in times:
    pp=Pr[Pr.datetime==t]; bb=[b for b in blobs if b[0]==t]
    print(t[11:],f"B{R[R.datetime==t].B_mean.iloc[0]:.0f}",' '.join(f"{x.pos:.2f}{'B' if x.ask>x.bid else 'R'}{x.bid}x{x.ask}{'*' if x.side>=3*x.weak else ''}" for x in pp.itertuples()),'| dots:',' '.join(f"{b[1]}{b[2]:.1f}-{b[3]:.1f}" for b in bb))

print('=== TIERS (luat chon): Big = 1.25xB & 3xweak & san 9; Dot = 1.5xB & san 9, khong phai Big')
Rr=build(2,1)
isbig=(Rr.side>=1.25*Rr.B_mean)&(Rr.side>=3*Rr.weak)&(Rr.side>=9)
isdot=(Rr.side>=1.5*Rr.B_mean)&(Rr.side>=9)&~isbig
print('Big',int(isbig.sum()),'Dot (ngoai Big)',int(isdot.sum()),'Dot tong (ca Big)',int(((Rr.side>=1.5*Rr.B_mean)&(Rr.side>=9)).sum()))
print('score Dot-tong',score(Rr[(Rr.side>=1.5*Rr.B_mean)&(Rr.side>=9)]))
