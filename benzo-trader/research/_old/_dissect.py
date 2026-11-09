import sys, numpy as np, pandas as pd
sys.argv=['x']
import kernel as K
import setup_c_fade_canh as C
import setup_a_pha_hoi as A
BASE='../../data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d'
def dissect(t, df, u, name):
    t=t[t.outcome.isin(['TP','SL'])].copy()
    rows=[]
    for _,e in t.iterrows():
        i=int(e['idx']); s=int(e['side']); ent=e['entry']; sl=e['sl']; tp=e['tp']; R=abs(ent-sl)
        ex=int(e['exit_idx']); seg=df.iloc[i+1:ex+1]
        fav=((seg['high'] if s>0 else seg['low'])-ent)*s; adv=(ent-(seg['low'] if s>0 else seg['high']))*s
        mfe=fav.max()/R if len(seg) else 0; mae=adv.max()/R if len(seg) else 0
        after=df.iloc[ex+1:ex+61]
        reach_tp=False
        if e.outcome=='SL' and len(after):
            reach_tp=bool((((after['high'] if s>0 else after['low'])-tp)*s>=0).any())
        hold=ex-i
        rows.append(dict(out=e.outcome, R=R, R_u=R/float(u.iloc[i]) if u.iloc[i]>0 else np.nan, floor=float(e.get('floor_applied',np.nan)), mfe=mfe, mae=mae, hold=hold, sl_then_tp=reach_tp, hour_vn=(df['t_vn'].iloc[i].hour), side=s))
    d=pd.DataFrame(rows)
    sl=d[d.out=='SL']; tp=d[d.out=='TP']
    print(f"\n===== {name}: n={len(d)} SL={len(sl)} TP={len(tp)} WR={len(tp)/len(d):.0%}")
    print("Khoang SL (gia): trung vi", round(d.R.median(),2), "| SL/u:", round(d.R_u.median(),2), "| san nhieu ap dung:", d.floor.mean())
    print("Lenh SL: hold trung vi", sl.hold.median(), "nen | SL trong <=3 nen:", round((sl.hold<=3).mean()*100), "% | <=10 nen:", round((sl.hold<=10).mean()*100), "%")
    print("Lenh SL: MFE truoc khi SL >=0.5R:", round((sl.mfe>=0.5).mean()*100), "% | >=1R:", round((sl.mfe>=1).mean()*100), "%")
    print("Lenh SL: sau do gia toi TP trong 60 nen (SL qua chat):", round(sl.sl_then_tp.mean()*100), "%")
    print("Lenh TP: hold trung vi", tp.hold.median(), "| MAE trung vi", round(tp.mae.median(),2))
    print("Theo gio VN: n / SL rate"); print(d.groupby(pd.cut(d.hour_vn,[-1,4,12,18,20,23]),observed=True)['out'].agg(['count',lambda x:round((x=='SL').mean(),2)]).to_string())
    print("Theo SL/u: n / SL rate"); print(d.groupby(pd.cut(d.R_u,[0,1.5,2.5,4,20]),observed=True)['out'].agg(['count',lambda x:round((x=='SL').mean(),2)]).to_string())
    print("Theo chieu: n / SL rate"); print(d.groupby('side')['out'].agg(['count',lambda x:round((x=='SL').mean(),2)]).to_string())
    return d
if __name__=='__main__':
    P=C.prepare(BASE); df=P['df']; u=P['u']
    _,tC=C.run(P, pen_ticks=2, min_width=6.0, tp_mode='fixed2'); dissect(tC,df,u,'C fade canh TP2R')
    _,tC2=C.run(P, pen_ticks=2, min_width=6.0, tp_mode='poc'); dissect(tC2,df,u,'C fade canh TP poc')
