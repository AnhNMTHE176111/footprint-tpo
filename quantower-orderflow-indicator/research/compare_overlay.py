"""So điểm nổ bóng của indicator (luật mới CellBig: max(buy,sell) >= 1,5 x B20, >=3) với bóng CORVEN.
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
D['side']=D[['bid_vol','ask_vol']].max(axis=1); D['tk']=(D.price*10).round().astype(int)
g=D[D.volume>0].groupby('datetime'); B=(g.volume.sum()/g.volume.count()).sort_index()
Bb=B.shift(1).rolling(20,min_periods=5).mean()
D['B']=D.datetime.map(Bb)
D['hit']=(D.side>=1.5*D.B)&(D.side>=3)
ours=D[D.hit]
# gộp ô liền kề ±1 tick như C# (side giảm dần, hòa lấy tick thấp)
keep=[]
for t,g2 in ours.groupby('datetime'):
    taken=[]
    for idx,tk,sd in sorted(zip(g2.index,g2.tk,g2.side),key=lambda z:(-z[2],z[1])):
        if all(abs(tk-x)>1 for x in taken): taken.append(tk); keep.append(idx)
ours=ours.loc[keep]
O=pd.read_csv('corven_bubbles.csv',parse_dates=['time_utc']); O['tk']=(O.price*10).round().astype(int)
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
m=O.merge(ours[['datetime','tk','bid_vol','ask_vol','side']],left_on=['time_utc','tk'],right_on=['datetime','tk'])
mine=np.where(np.minimum(m.bid_vol,m.ask_vol)/m.side>=0.6,'tim',np.where(m.ask_vol>=m.bid_vol,'xanh','do'))
print('màu khớp (ô trùng đúng tick):',f'{(mine==m.color).mean():.0%}',len(m))
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
        if not(60<x<1335 and 270<y<c['y1']+90): continue
        ok=any(abs(k-b)<=1 for b in cb.get(t,()))
        R=9; d.ellipse((x-R,y-R,x+R,y+R),outline=(0,200,0) if ok else (255,190,0),width=3); xs.append(x)
    for t,k in zip(O.time_utc,O.tk):
        x,y=xy(t,k/10)
        if not(60<x<1335 and 270<y<c['y1']+90): continue
        if not any(abs(k-q)<=1 for q in pb.get(t,())):
            d.rectangle((x-6,y-6,x+6,y+6),outline=(0,0,0),width=3)
    if xs:
        im=im.crop((max(0,int(min(xs))-60),250,min(W,int(max(xs))+60),min(Hh,c['y1']+110)))
    im.save(f'compare/{fr}.png')
import os; os.makedirs('compare',exist_ok=True)
for fr in cal: draw(fr)
print('ảnh:',sorted(os.listdir('compare')))
