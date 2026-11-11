from lookup import *
import json
cal=json.load(open('calib.json'))
O=pd.read_csv('corven_bubbles.csv',parse_dates=['time_utc'])
tm2idx={t:i for i,t in enumerate(b.datetime)}
O['idx']=O.time_utc.map(tm2idx)
_,_,_,ROW=minute_grid(b)
vis=set()
for f,c in cal.items():
    if f=='1-07-55': continue
    for k in range(0,200):
        x=c['x0']+c['s']*k
        if x<85 or x>1355: continue
        i=slot_row(c,k,ROW)
        if i is None: continue
        bar=b.iloc[i]
        y_hi=c['a']+c['bb']*bar.high; y_lo=c['a']+c['bb']*bar.low
        if y_hi<290 or y_lo>c['y1']-12: continue
        vis.add(i)
S=[]
for i in range(len(b)):
    g=cells.get(int(b.bar_idx[i]))
    S.append((g.volume.sum(),g.volume.max(),g.volume.mean(),max(g.bid_vol.max(),g.ask_vol.max())) if g is not None else (0,0,0,0))
S=pd.DataFrame(S,columns=['bvol','bmax','bmean','bside'])
S['cellmean_ma20']=S.bmean.rolling(20,min_periods=5).mean()
V=pd.DataFrame({'idx':sorted(vis)})
V=V.join(S,on='idx')
nd=O.groupby('idx').size(); nbig=O[O.size_px>=9].groupby('idx').size()
V['ndots']=V.idx.map(nd).fillna(0).astype(int); V['nbig']=V.idx.map(nbig).fillna(0).astype(int)
V['has']=V.ndots>0
V['time_utc']=[str(b.datetime[i]) for i in V.idx]
V['side_rel']=V.bside/V.cellmean_ma20
V.to_csv('corven_bars_control.csv',index=False)
print('nen nhin ro:',len(V),' co bong:',V.has.sum(),' khong bong:',(~V.has).sum())
for c in ('bside','bmax','bvol','side_rel'):
    a=V[V.has][c]; n=V[~V.has][c]
    # AUC
    from itertools import product
    r=pd.concat([a,n]).rank().values; na,nn=len(a),len(n)
    auc=(r[:na].sum()-na*(na+1)/2)/(na*nn)
    best=max(((V[c]>=t).eq(V.has).mean(),t) for t in np.unique(V[c].round(2)))
    print('%-9s co bong: q10/50/90 %s | khong bong: %s | AUC=%.2f | nguong tot nhat %.1f acc=%.2f'%(c,np.round(a.quantile([.1,.5,.9]).values,1),np.round(n.quantile([.1,.5,.9]).values,1),auc,best[1],best[0]))
print('nen khong bong, bside max:',V[~V.has].bside.max(),'; nen co bong, bside min:',V[V.has].bside.min())
# bar-level: nen co bong lon
for c in ('bside','bmax'):
    a=V[V.nbig>0][c]; n=V[V.nbig==0][c]
    print('co bong LON (>=9px) n=%d %s:%s  | khong: %s'%(len(a),c,np.round(a.quantile([0,.1,.25,.5,.75,1]).values,0),np.round(n.quantile([.5,.9,.99,1]).values,0)))
# phan bo bong
for col in ('xanh','do','tim'):
    g=O[O.color==col]
    ds=g.w_ask if col=='xanh' else g.w_bid if col=='do' else g[['w_bid','w_ask']].max(axis=1)
    print(col,len(g),'domside_win min med max',ds.min(),ds.median(),ds.max(),'| vol o',g.w_volume.min(),g.w_volume.median(),g.w_volume.max(),'| |delta|',g.w_delta.abs().min(),g.w_delta.abs().median(),g.w_delta.abs().max())
