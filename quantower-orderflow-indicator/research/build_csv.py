"""Gop detections -> corven_bubbles.csv (+ corven_bars_control.csv). Chay sau calib_all.py + detect_bubbles.py."""
import json
from lookup import *
cal=json.load(open('calib.json'))
raw=pd.read_csv('bubbles_raw.csv'); raw=raw[raw.frame!='1-07-55']   # 1-07-55: calib hong (cost 17px)
raw['bb']=raw.frame.map(lambda f:cal[f]['bb'])
raw['pc']=raw.price+0.3*raw.r/abs(raw.bb)          # bu lech tam bong ~0.3*r px (do bang tuong quan voi o)
raw['p1']=(raw.pc*10).round()
# khu trung: cung nen + cung mau + cach <=1 tick; giu cai to nhat, dem so khung
raw=raw.sort_values('r',ascending=False).reset_index(drop=True)
kept=[]
for _,r in raw.iterrows():
    for k in kept:
        if k['idx']==r.idx and k['color']==r.color and abs(k['p1']-r.p1)<=1:
            k['n_frames'].add(r.frame); break
    else:
        d=r.to_dict(); d['n_frames']={r.frame}; kept.append(d)
rows=[]
for k in kept:
    i=int(k['idx']); g=cells[int(b.bar_idx[i])]; bar=b.iloc[i]
    p0=int(round(k['pc']*10))
    def row(p):
        if p in g.index: c=g.loc[p]; return int(c.bid_vol),int(c.ask_vol),int(c.volume),int(c.delta)
        return 0,0,0,0
    bid,ask,vol,dl=row(p0)
    win=[p for p in (p0-1,p0,p0+1)]
    if k['color']=='xanh': key=lambda p:(row(p)[1]-row(p)[0])
    elif k['color']=='do': key=lambda p:(row(p)[0]-row(p)[1])
    else: key=lambda p:row(p)[2]
    pw=max(win,key=key); wb,wa,wv,wd=row(pw)
    mv=g.volume.max(); ms=max(g.bid_vol.max(),g.ask_vol.max())
    rank=int((g.volume>vol).sum()+1) if vol>0 else None
    rankw=int((g.volume>wv).sum()+1) if wv>0 else None
    utc=bar.datetime; vn=utc+pd.Timedelta(hours=7)
    conf='cao' if (k['r']>=4.5 or len(k['n_frames'])>=2) else 'thap'
    rows.append(dict(frame=k['frame'],all_frames='|'.join(sorted(k['n_frames'])),time_vn=str(vn),time_utc=str(utc),price=round(p0/10,1),color=k['color'],
        size_px=round(2*k['r'],1),printed_number='',bid=bid,ask=ask,volume=vol,delta=dl,rank_in_bar=rank,
        w_price=pw/10,w_bid=wb,w_ask=wa,w_volume=wv,w_delta=wd,w_rank_in_bar=rankw,
        bar_max_vol=int(mv),bar_max_side=int(ms),bar_vol=int(g.volume.sum()),bar_delta=int(g.delta.sum()),confidence=conf))
O=pd.DataFrame(rows).sort_values(['time_utc','price']); O.to_csv('corven_bubbles.csv',index=False)
print('bong khu trung:',len(O),' tu',len(raw),'phat hien tho; khung:',O.frame.nunique(),'; nen duy nhat:',O.time_utc.nunique())
print(O.color.value_counts().to_dict(), O.confidence.value_counts().to_dict())
