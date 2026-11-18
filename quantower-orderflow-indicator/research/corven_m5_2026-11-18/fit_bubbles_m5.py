import pandas as pd, numpy as np, itertools
from pathlib import Path
# chay duoc tu bat ky thu muc nao: duong dan tinh tu vi tri file nay (repo = footprint-tpo)
REPO=Path(__file__).resolve().parents[3]
F=str(REPO/'data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h.csv')
D=pd.read_csv(F); D=D[D.volume>0].copy(); D['tk']=(D.price*10).round().astype(int)
D['datetime']=D.datetime.str[:16]
R=D.assign(row=(D.tk-1)//2).groupby(['datetime','row'],as_index=False).agg(bid=('bid_vol','sum'),ask=('ask_vol','sum'),vol=('volume','sum'),n=('trades','sum'))
R['side']=R[['bid','ask']].max(axis=1); R['weak']=R[['bid','ask']].min(axis=1); R['pos']=(R.row*2+1.5)/10
R['delta']=R.ask-R.bid
g=R.groupby('datetime')
st=pd.DataFrame({'mean':g.vol.mean(),'maxside':g.side.max(),'tot':g.vol.sum(),'nrow':g.size()}).sort_index()
for c,w in (('mean',20),('maxside',20),('tot',20)):
    st['B_'+c]=st[c].shift(1).rolling(w,min_periods=5).mean()
# per-row distribution baseline: 95th pct of side over prior 20 bars
R=R.merge(st[[c for c in st.columns if c.startswith('B_')]],left_on='datetime',right_index=True)
GT=[('12:15','P',3774.65),('12:30','P',3768.05),('12:35','P',3760.95),('12:35','P',3760.15),('12:45','P',3754.15),('12:45','P',3752.45),
('12:50','P',3750.75),('12:55','P',3748.95),('13:00','P',3757.15),('13:00','B',3755.4),('13:00','B',3750.6),('13:00','B',3749.0),
('13:05','B',3766.3),('13:10','B',3773.5),('13:10','B',3770.55),('13:15','P',3772.15),('13:15','B',3767.95),('13:20','B',3770.2),
('13:25','P',3773.85),('13:30','P',3782.4),('13:30','B',3779.8),('13:50','P',3790.75),('13:50','P',3788.55),('14:20','B',3777.95)]
times=[f'2026-11-18 {h:02d}:{m:02d}' for h in (12,13,14) for m in range(0,60,5) if (12,15)<=(h,m)<=(14,25)]
V=R[R.datetime.isin(times)].copy()
def score(P,tol=0.5,colour=False):
    hit=0;col=0
    for t in times:
        a=P[P.datetime==t]; b=[g for g in GT if '2026-11-18 '+g[0]==t]
        pairs=sorted((abs(x.pos-y[2]),i,j) for i,x in enumerate(a.itertuples()) for j,y in enumerate(b) if abs(x.pos-y[2])<=tol)
        ua=set();ub=set();al=list(a.itertuples())
        for _,i,j in pairs:
            if i in ua or j in ub: continue
            ua.add(i);ub.add(j);hit+=1
            c='B' if al[i].ask>=al[i].bid else 'P'
            col+= c==b[j][1]
    nP=len(P); f1=2*hit/(nP+len(GT)) if nP+len(GT) else 0
    return nP,hit,col,f1
print('current rule (ratio 1,3, san 9, khong cong can bang):', score(V[(V.side>=1.3*V.B_mean)&(V.side>=9)]))
# LUAT DA CHON (2026-11-18): ben troi >= 1,25 x TB volume/hang cua 20 nen truoc, ben troi >= 3 x ben yeu, san 9
CH=V[(V.side>=1.25*V.B_mean)&(V.side>=3*V.weak)&(V.side>=9)]
nP,hit,col,f1=score(CH)
print(f'CHOSEN RULE (1,25 x TB, >= 3 x ben yeu, san 9): {nP} bong, {hit} trung vi tri (+-0,5 gia) / {len(GT)} bong CORVEN, F1 {f1:.2f}')
bars_with=CH.datetime.nunique(); gtb={'2026-11-18 '+g[0] for g in GT}
print(f'  so nen co bong: {bars_with}; nen CORVEN co bong: {len(gtb)}; nen ca hai cung co bong: {len(set(CH.datetime)&gtb)}; nen ca hai cung KHONG co: {len(set(times)-set(CH.datetime)-gtb)}')
res=[]
for base in ('B_mean','B_maxside'):
    for k in np.arange(1.0,8.01,0.25):
        for imb in (0,1.5,2,2.5,3):
            P=V[(V.side>=k*V[base])&((imb==0)|(V.side>=imb*V.weak))]
            res.append((score(P)[3],base,k,imb,score(P)))
        for k2 in (0,):
            P=V[(V.delta.abs()>=k*V[base])]
            res.append((score(P)[3],base+'|delta|',k,0,score(P)))
res.sort(key=lambda r:-r[0])
for r in res[:25]: print(r)
print('==== excess (vol - trades) per row')
V['ex']=V.vol-V.n
st2=R.assign(ex=R.vol-R.n).groupby('datetime').ex.mean().sort_index().shift(1).rolling(20,min_periods=5).mean()
V['Bex']=V.datetime.map(st2)
res=[]
for k in np.arange(1,15.01,0.5):
    P=V[V.ex>=k*V.Bex]; res.append((score(P)[3],'ex/Bex',k,score(P)))
for k in range(5,60,2):
    P=V[V.ex>=k]; res.append((score(P)[3],'ex abs',k,score(P)))
for k in np.arange(0.5,4,0.25):
    P=V[V.ex>=k*V.B_mean]; res.append((score(P)[3],'ex/Bmean',k,score(P)))
res.sort(key=lambda r:-r[0])
for r in res[:12]: print(r)
print('==== detail k1.25 imb3')
P=V[(V.side>=1.25*V.B_mean)&(V.side>=3*V.weak)]
for t in times:
    a=P[P.datetime==t]; b=[g for g in GT if '2026-11-18 '+g[0]==t]
    print(t[11:], 'ours:',' '.join(f"{x.pos:.2f}{'B' if x.ask>x.bid else 'P'}({x.bid}x{x.ask},B{x.B_mean:.0f})" for x in a.itertuples()),'| CORVEN:',' '.join(f"{g[2]:.2f}{g[1]}" for g in b))
# density whole 9 days
A=R.copy(); A['weak']=A[['bid','ask']].min(axis=1)
for k,imb in ((1.3,0),(1.25,3),(1.25,2.5),(1.5,3)):
    n=((A.side>=k*A.B_mean)&(A.side>=9)&((imb==0)|(A.side>=imb*A.weak))).sum(); print(k,imb,'per bar',n/A.datetime.nunique())
