"""Reverse-engineer: chart Sierra của CORVEN gộp 2 tick / 1 hàng (0,2 giá), hàng = (tick lẻ, tick chẵn kế)
-> bóng đặt ở tâm hàng. Kiểm: luật trên HÀNG 2 tick vs luật trên Ô 1 tick (+/- gộp liền kề)."""
import numpy as np, pandas as pd, json
from io import StringIO
from bubble_common import LVL
rows=[l for l in open(LVL) if any(f',2026-11-0{d}' in l[:40] for d in (4,5,6,7))]
D=pd.read_csv(StringIO('bar_idx,datetime,price,bid_vol,ask_vol,volume,delta,trades,buy_trades,sell_trades,max_one_trade\n'+''.join(rows)),parse_dates=['datetime'])
D=D[D.volume>0].copy(); D['tk']=(D.price*10).round().astype(int)
C=pd.read_csv('corven_bars_control.csv',parse_dates=['time_utc']); vis=set(C.time_utc)
O=pd.read_csv('corven_bubbles.csv',parse_dates=['time_utc']); O=O[O.time_utc.isin(vis)]
O['t10']=O.price*10   # giá đã bù lệch tâm (build_csv)
def make(off):
    R=D.assign(row=(D.tk-off)//2).groupby(['datetime','row'],as_index=False).agg(bid=('bid_vol','sum'),ask=('ask_vol','sum'),vol=('volume','sum'))
    R['side']=R[['bid','ask']].max(axis=1); R['pos']=R.row*2+off+0.5
    g=R.groupby('datetime'); B=g.vol.mean().sort_index().shift(1).rolling(20,min_periods=5).mean()
    R['B']=R.datetime.map(B); return R
def score(P,tol,day=None):
    times=[t for t in vis if day is None or str(t).startswith(day)]
    cb={t:list(s.t10) for t,s in O[O.time_utc.isin(times)].groupby('time_utc')}
    pb={t:list(s.pos) for t,s in P[P.datetime.isin(times)].groupby('datetime')}
    nC=sum(map(len,cb.values())); nP=sum(map(len,pb.values())); hit=0; colok=0
    for t in times:
        a=pb.get(t,[]); b=cb.get(t,[])
        pairs=sorted((abs(x-y),i,j) for i,x in enumerate(a) for j,y in enumerate(b) if abs(x-y)<=tol)
        ua=set(); ub=set()
        for _,i,j in pairs:
            if i in ua or j in ub: continue
            ua.add(i); ub.add(j); hit+=1
    return nP,nC,hit,nP-hit,nC-hit
print('lệch pha hàng: off=1 nghĩa là hàng (x.1,x.2), off=0 hàng (x.0,x.1)')
for off in (0,1):
    R=make(off); V=R[R.datetime.isin(vis)]
    for k in (1.2,1.3,1.4,1.5,1.6,1.8):
        P=V[(V.side>=k*V.B)&(V.side>=3)]
        a=score(P,1.0); e=score(P,0.5)
        print(f'off={off} k={k}: mình {a[0]} CORVEN {a[1]} | ±1 tick: trúng {a[2]} thừa {a[3]} ({a[3]/a[0]:.0%}) sót {a[4]} ({a[4]/a[1]:.0%}) | ±0,5 tick: trúng {e[2]} thừa {e[3]/e[0]:.0%} sót {e[4]/e[1]:.0%}')
print('--- theo ngày, off=1')
R=make(1); V=R[R.datetime.isin(vis)]
for k in (1.25,1.3,1.35,1.4):
    P=V[(V.side>=k*V.B)&(V.side>=3)]
    for d in ('2026-11-05','2026-11-06'):
        a=score(P,1.0,d); print(f'k={k} {d}: mình {a[0]} CORVEN {a[1]} trúng {a[2]} thừa {a[3]/a[0]:.0%} sót {a[4]/a[1]:.0%} F1 {2*a[2]/(a[0]+a[1]):.3f}')
# màu trên hàng
P=V[(V.side>=1.3*V.B)&(V.side>=3)].copy()
P['key']=list(zip(P.datetime,np.round(P.pos).astype(int)))
O['key']=list(zip(O.time_utc,[int(np.floor((x-1)/2))*2+2 for x in O.t10]))  # tâm hàng làm tròn
P['key']=list(zip(P.datetime,(P.row*2+2).astype(int)))
M=O[['key','color']].merge(P,on='key')
for bp in (0.5,0.6,0.7,0.75,0.8,0.9):
    pred=np.where(np.minimum(M.bid,M.ask)/M.side>=bp,'tim',np.where(M.ask>=M.bid,'xanh','do'))
    print('tím nếu yếu/mạnh >=',bp,'màu đúng',f'{(pred==M.color).mean():.0%}',len(M))

# ===================== KIỂM CHÉO ĐÚNG LUẬT C# (CellBigLogic, 2026-11-11) =====================
# RowTicks=2, RowOffset=1, Ratio 1,3, sàn 3, tím khi bên yếu >= 1,3 x B và >= 3 (luật 2026-11-12), B = TB 20 nến đóng trước (>=5) của vol TB mỗi hàng có vol>0,
# bóng ở TÂM hàng (R.pos tính theo décima-giá = tick). Ghép 1-1 ±1 tick, giống bảng báo cáo.
print('=== MÔ PHỎNG ĐÚNG LUẬT C# (ratio 1,3, sàn 3, tím = bên yếu cũng nổ, hàng 2 tick pha 1) ===')
R=make(1); V=R[R.datetime.isin(vis)]
PC=V[(V.B>0)&(V.side>=1.3*V.B)&(V.side>=3)].copy()
for lab,day in (('TỔNG',None),('05/11','2026-11-05'),('06/11','2026-11-06')):
    a=score(PC,1.0,day); print(f'{lab}: mình {a[0]} CORVEN {a[1]} trúng {a[2]} thừa {a[3]} ({a[3]/a[0]:.0%}) sót {a[4]} ({a[4]/a[1]:.0%}) F1 {2*a[2]/(a[0]+a[1]):.3f}')
PC['key']=list(zip(PC.datetime,(PC.row*2+2).astype(int)))
M=O[['key','color']].merge(PC,on='key')
pred=np.where((np.minimum(M.bid,M.ask)>=1.3*M.B)&(np.minimum(M.bid,M.ask)>=3),'tim',np.where(M.ask>=M.bid,'xanh','do'))
_t=(M.color=='tim'); _p=(pred=='tim')
print(f'tím: bắt được {(_t&_p).sum()}/{_t.sum()} ({(_t&_p).sum()/max(1,_t.sum()):.0%}) | báo tím đúng {(_t&_p).sum()}/{_p.sum()} ({(_t&_p).sum()/max(1,_p.sum()):.0%})')
print(f'màu đúng {(pred==M.color).mean():.0%} (trên {len(M)} bóng ghép được theo hàng)')
