"""So điểm nổ bóng của indicator (luật CellBig 2026-11-11: gom hàng 2 tick pha 1, bóng ở tâm hàng, max(buy,sell) >= 1,3 x B20 hàng, >=3) với bóng CORVEN.
Vẽ lên chính ảnh chart CORVEN: vòng XANH LÁ = mình nổ & CORVEN cũng có bóng (±1 tick);
vòng VÀNG = mình nổ nhưng CORVEN không có; ô vuông TRẮNG viền đen = CORVEN có bóng mà mình KHÔNG nổ."""
import json, numpy as np, pandas as pd
from PIL import Image, ImageDraw
from bubble_common import load_bars, minute_grid, LVL
S="C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/14112285-cd5a-4717-90f2-b4fe405421be/scratchpad"
cal=json.load(open('calib.json')); cal.pop('1-07-55',None)
bars=load_bars(); t0,H,L,row=minute_grid(bars)
from io import StringIO
rows=[l for l in open(LVL) if (',2026-11-04' in l[:40] or ',2026-11-05' in l[:40] or ',2026-11-06' in l[:40] or ',2026-11-07' in l[:40])]
D=pd.read_csv(StringIO('bar_idx,datetime,price,bid_vol,ask_vol,volume,delta,trades,buy_trades,sell_trades,max_one_trade\n'+''.join(rows)),parse_dates=['datetime'])
D=D[D.volume>0].copy(); D['tk']=(D.price*10).round().astype(int)
# LUẬT MỚI 2026-11-11 (= CellBigLogic C#): gom HÀNG 2 tick pha 1 (row = floor((tick-1)/2)), bóng ở TÂM hàng
R=D.assign(row=(D.tk-1)//2).groupby(['datetime','row'],as_index=False).agg(bid=('bid_vol','sum'),ask=('ask_vol','sum'),vol=('volume','sum'))
R['side']=R[['bid','ask']].max(axis=1); R['tk']=R.row*2+1.5   # tâm hàng (chỉ số tick, có thể lẻ nửa tick)
B=R.groupby('datetime').vol.mean().sort_index().shift(1).rolling(20,min_periods=5).mean()
R['B']=R.datetime.map(B)
ours=R[(R.B>0)&(R.side>=1.3*R.B)&(R.side>=3)].copy()
ours=ours.rename(columns={'bid':'bid_vol','ask':'ask_vol'})
O=pd.read_csv('corven_bubbles.csv',parse_dates=['time_utc']); O['tk']=O.price*10   # giá bóng CORVEN đã bù lệch tâm (build_csv)
C=pd.read_csv('corven_bars_control.csv',parse_dates=['time_utc']); vis=set(C.time_utc)
def stats(times,lab):
    o=O[O.time_utc.isin(times)]; p=ours[ours.datetime.isin(times)]
    cb={}; [cb.setdefault(t,set()).add(k) for t,k in zip(o.time_utc,o.tk)]
    pb={}; [pb.setdefault(t,set()).add(k) for t,k in zip(p.datetime,p.tk)]
    r=[]
    for tol in (0,1):
        prec=np.mean([any(abs(k-b)<=tol for b in cb.get(t,())) for t,k in zip(p.datetime,p.tk)])
        rec=np.mean([any(abs(k-q)<=tol for q in pb.get(t,())) for t,k in zip(o.time_utc,o.tk)])
        r.append(f'lệch {tol} tick: trùng chỗ CORVEN {prec:.0%}, bắt được bóng CORVEN {rec:.0%}')
    # cấp nến: nến có bóng / không
    hasC={t for t in times if t in cb}; hasP={t for t in times if t in pb}
    bar_acc=np.mean([(t in hasC)==(t in hasP) for t in times])
    print(f'{lab}: {len(times)} nến, CORVEN {len(o)} bóng, mình {len(p)} bóng | '+' | '.join(r)+f' | nến có/không bóng khớp {bar_acc:.0%}')
stats(vis,'TẤT CẢ')
for d in ('2026-11-05','2026-11-06'):
    stats({t for t in vis if str(t).startswith(d)},d)
# màu
O['rk']=np.floor((O.tk-1)/2).astype(int); ours['rk']=ours.row.astype(int)
m=O.merge(ours[['datetime','rk','bid_vol','ask_vol','side']],left_on=['time_utc','rk'],right_on=['datetime','rk'])
mine=np.where(np.minimum(m.bid_vol,m.ask_vol)/m.side>=0.75,'tim',np.where(m.ask_vol>=m.bid_vol,'xanh','do'))
print('màu khớp (bóng trùng đúng hàng):',f'{(mine==m.color).mean():.0%}',len(m))
# vẽ
def draw(fr):
    c=cal[fr]; im=Image.open(f'{S}/hi/{fr}.png').convert('RGB'); d=ImageDraw.Draw(im)
    W,Hh=im.size
    def xy(t,price):
        mm=int((t-t0).total_seconds()//60); k=mm-c['n0']+c['kmin']
        return c['x0']+c['s']*k, c['a']+c['bb']*price
    ts=[t for t in vis]
    cb={}; [cb.setdefault(t,set()).add(k) for t,k in zip(O.time_utc,O.tk)]
    pb={}; [pb.setdefault(t,set()).add(k) for t,k in zip(ours.datetime,ours.tk)]
    xs=[]
    for t,k in zip(ours.datetime,ours.tk):
        x,y=xy(t,k/10)
        if not(60<x<1335 and 270<y<c['y1']): continue
        ok=any(abs(k-b)<=1 for b in cb.get(t,()))
        R=9; d.ellipse((x-R,y-R,x+R,y+R),outline=(0,200,0) if ok else (255,190,0),width=3); xs.append(x)
    for t,k in zip(O.time_utc,O.tk):
        x,y=xy(t,k/10)
        if not(60<x<1335 and 270<y<c['y1']): continue
        if not any(abs(k-q)<=1 for q in pb.get(t,())):
            d.rectangle((x-6,y-6,x+6,y+6),outline=(0,0,0),width=3)
    if xs:
        im=im.crop((max(0,int(min(xs))-60),250,min(W,int(max(xs))+60),min(Hh,c['y1']+110)))
    im.save(f'compare/{fr}.png')
import os; os.makedirs('compare',exist_ok=True)
for fr in cal: draw(fr)
print('ảnh:',sorted(os.listdir('compare')))
