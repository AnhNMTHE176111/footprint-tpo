# Thử luật nổ bóng cấp Ô so với bóng CORVEN (khớp ±1 tick). Opus viết 2026-11-11.
import pandas as pd, numpy as np
F='../../data-export/data-footprint/fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv'
rows=[l for l in open(F) if ',2026-11-0' in l[:30] and (',2026-11-04' in l or ',2026-11-05' in l or ',2026-11-06' in l)]
from io import StringIO
D=pd.read_csv(StringIO('bar_idx,datetime,price,bid_vol,ask_vol,volume,delta,trades,buy_trades,sell_trades,max_one_trade\n'+''.join(rows)),parse_dates=['datetime'])
D['side']=D[['bid_vol','ask_vol']].max(axis=1)
D['tk']=(D.price*10).round().astype(int)
B=D.groupby('datetime').agg(bmean=('volume','mean'),bmed=('volume','median')).sort_index()
for n in (10,20,50,100):
    B[f'ma{n}']=B.bmean.shift(1).rolling(n,min_periods=5).mean()
# baseline kiểu side: mean of side per cell
B['smean']=D.groupby('datetime').side.mean()
B['sma20']=B.smean.shift(1).rolling(20,min_periods=5).mean()
D=D.join(B,on='datetime')
C=pd.read_csv('corven_bars_control.csv',parse_dates=['time_utc'])
vis=set(C.time_utc)
O=pd.read_csv('corven_bubbles.csv',parse_dates=['time_utc']); O['tk']=(O.price*10).round().astype(int)
O=O[O.time_utc.isin(vis)]
V=D[D.datetime.isin(vis)].copy()
bub={}
for t,k in zip(O.time_utc,O.tk): bub.setdefault(t,set()).add(k)
def ev(mask,label):
    P=V[mask]; pk={}
    for t,k in zip(P.datetime,P.tk): pk.setdefault(t,set()).add(k)
    tp=sum(1 for t,k in zip(P.datetime,P.tk) if any(abs(k-b)<=1 for b in bub.get(t,())))
    prec=tp/max(1,len(P))
    rec=sum(1 for t,k in zip(O.time_utc,O.tk) if any(abs(k-p)<=1 for p in pk.get(t,())))/len(O)
    f1=2*prec*rec/max(1e-9,prec+rec)
    return (round(f1,3),round(prec,2),round(rec,2),len(P),label)
res=[]
for T in range(3,21): res.append(ev(V.side>=T,f'side>={T}'))
for T in range(4,25,2): res.append(ev(V.volume>=T,f'vol>={T}'))
for n in (10,20,50,100):
  for k in np.arange(1.0,4.01,0.2):
    for fl in (0,3,5):
      res.append(ev((V.side>=k*V[f'ma{n}'])&(V.side>=fl),f'side>={k:.1f}*ma{n} floor{fl}'))
      res.append(ev((V.volume>=k*V[f'ma{n}'])&(V.volume>=fl),f'vol>={k:.1f}*ma{n} floor{fl}'))
res.sort(reverse=True)
print('bubbles',len(O),'cells',len(V))
for r in res[:25]: print(r)
print([r for r in res if r[4].startswith('side>=') and 'ma' not in r[4]][:5])
print('--- k mịn ma20')
for k in (1.3,1.4,1.5,1.6,1.7,1.8): print(ev(V.side>=k*V.ma20,f'{k}'))
# mô phỏng luật hiện tại: z>=2.5 trên side của 3 ô đậm nhất / nến, 100 nến; top2/nến
g=D.sort_values(['datetime','volume'],ascending=[True,False]).groupby('datetime').head(3)
ts=sorted(D.datetime.unique()); thr={}
from collections import deque
q=deque()
gs=dict(tuple(g.groupby('datetime').side))
for t in ts:
    if len(q)>=40:
        a=np.concatenate(list(q)); m=np.median(a); mad=np.median(abs(a-m))
        thr[t]=m+2.5*mad/0.6745 if mad>0 else m*3.5
    q.append(gs[t].values);
    if len(q)>100: q.popleft()
V['thr']=V.datetime.map(thr)
cur=(V.side>=V.thr)&(V.volume>=5)
V['r']=V[cur].groupby('datetime').side.rank(ascending=False,method='first')
print('luật hiện tại', ev(cur&(V.r<=2),'z2.5 top2'), 'ngưỡng trung vị',np.nanmedian(V.thr))
# màu: tím khi bên yếu/bên mạnh >= r
M=O.copy(); M['mn']=M[['w_bid','w_ask']].min(axis=1); M['mx']=M[['w_bid','w_ask']].max(axis=1); M['bal']=M.mn/M.mx.clip(lower=1)
for r in (0.4,0.5,0.6,0.7):
    pred=np.where(M.bal>=r,'tim',np.where(M.w_ask>M.w_bid,'xanh','do'))
    print('tím nếu yếu/mạnh>=',r,'đúng màu',round((pred==M.color).mean(),2))
print(M.groupby('color').bal.describe()[['25%','50%','75%']])

# ===== KIỂM CHÉO CellBigLogic.cs (2026-11-11): mô phỏng ĐÚNG luật C# =====
# B = TB 20 nến TRƯỚC (không gồm nến hiện tại, cần >=5 nến) của (tổng volume nến / số ô giá có volume>0);
# nổ khi max(buy,sell) >= 1.5*B và >= 3; không giới hạn số bóng/nến. Màu: tím nếu yếu/mạnh>=0.6.
def csharp_rule(Dall, ratio=1.5, nbase=20, minside=3):
    bm = Dall[Dall.volume>0].groupby('datetime').agg(tv=('volume','sum'), nl=('volume','size')).sort_index()
    bm['bm'] = bm.tv/bm.nl
    hist=[]; Bv={}
    for t,v in bm.bm.items():            # nến lần lượt: B chỉ gồm các nến TRƯỚC t
        Bv[t] = (sum(hist[-nbase:])/len(hist[-nbase:])) if len(hist)>=5 else np.nan
        hist.append(v)
    X = Dall.copy(); X['Bc']=X.datetime.map(Bv)
    X['hit']=(X.side>=ratio*X.Bc)&(X.side>=minside)
    return X
X=csharp_rule(D)
Xv=X[X.datetime.isin(vis)]
print('--- KIỂM CHÉO C# (Python mô phỏng đúng luật C#)')
print('F1,prec,rec,n,label =', ev(Xv.hit.values,'csharp rule 1.5xB20 min3'))
# màu
Hh=Xv[Xv.hit].copy(); Hh['col']=np.where(Hh[['bid_vol','ask_vol']].min(axis=1)/Hh.side>=0.6,'tim',np.where(Hh.ask_vol>=Hh.bid_vol,'xanh','do'))
print('số bóng theo màu:',Hh.col.value_counts().to_dict())
