import pandas as pd, numpy as np
O=pd.read_csv('corven_bubbles.csv',parse_dates=['time_utc'])
O['dom_w']=np.where(O.color=='xanh',O.w_ask,np.where(O.color=='do',O.w_bid,O[['w_bid','w_ask']].max(axis=1)))
O['dom_c']=np.where(O.color=='xanh',O.ask,np.where(O.color=='do',O.bid,O[['bid','ask']].max(axis=1)))
O['adl_w']=(O.w_ask-O.w_bid).abs()
q=[0,.1,.25,.5,.75,.9,1]
print('SO BONG',len(O),'khung',O.frame.nunique(),'nen',O.time_utc.nunique())
for lab,g in [('tat ca',O),('cao',O[O.confidence=='cao']),('to>=9px',O[O.size_px>=9])]:
    print('==',lab,len(g))
    for c in ('xanh','do','tim'):
        h=g[g.color==c]
        if len(h)==0: continue
        print(' ',c,len(h),'ben ap dao(cua so)',np.round(h.dom_w.quantile(q).values,0).tolist(),'| vol o',np.round(h.w_volume.quantile(q).values,0).tolist(),'| |delta| o',np.round(h.adl_w.quantile(q).values,0).tolist())
# ben ap dao dung phia mau
for c,col in (('xanh','w_ask'),('do','w_bid')):
    h=O[O.color==c]; opp='w_bid' if c=='xanh' else 'w_ask'
    print(c,'cell: ben cung mau > ben kia:',round((h[col]>h[opp]).mean(),2),' = ben kia:',round((h[col]==h[opp]).mean(),2))
h=O[O.color=='tim']; print('tim: ratio dom/opp median',np.round((h[['w_bid','w_ask']].max(axis=1)/np.maximum(1,h[['w_bid','w_ask']].min(axis=1))).quantile([.25,.5,.75]).values,1), ' ask>bid:',round((h.w_ask>h.w_bid).mean(),2))
# size vs volume
O['sz']=pd.cut(O.size_px,[0,5,6.5,8,10,14,40])
print(O.groupby('sz',observed=True).agg(n=('dom_w','size'),vol_med=('w_volume','median'),vol_q10=('w_volume',lambda s:s.quantile(.1)),dom_med=('dom_w','median'),dom_q10=('dom_w',lambda s:s.quantile(.1)),rank1=('w_rank_in_bar',lambda s:(s==1).mean())).round(2).to_string())
# theo phien
O['hour']=O.time_utc.dt.hour
O['sess']=pd.cut(O.hour,[-1,3,8,12,16,24],labels=['00-03','04-08','09-12','13-16','17-23'])
print(O[O.color!='tim'].groupby('sess',observed=True).agg(n=('dom_w','size'),q10=('dom_w',lambda s:s.quantile(.1)),q25=('dom_w',lambda s:s.quantile(.25)),med=('dom_w','median')).to_string())
print('rank w=1 ti le:',round((O.w_rank_in_bar==1).mean(),2), ' bubbles to>=9px:',round((O[O.size_px>=9].w_rank_in_bar==1).mean(),2),' cell max-side:',round((O[O.size_px>=9].dom_w==O[O.size_px>=9].bar_max_side).mean(),2))
