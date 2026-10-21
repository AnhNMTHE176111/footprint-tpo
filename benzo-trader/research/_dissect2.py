import sys, numpy as np, pandas as pd
sys.argv=['x']
import kernel as K
import setup_c_fade_canh as C
import setup_a_pha_hoi as A
from _dissect import dissect, BASE
P=C.prepare(BASE); df=P['df']; u=P['u']
_,t=C.run(P, pen_ticks=2, min_width=6.0, tp_mode='fixed2')
t=t[t.outcome.isin(['TP','SL'])].copy()
# phan loai lenh SL: (a) pha that: trong 20 nen sau SL co nen M1 dong ngoai canh E >= 1u ; (b) quet: khong (a) va gia quay lai trong range
sl=t[t.outcome=='SL']
cls=[]
for _,e in sl.iterrows():
    s=int(e.side); E=e.edge; ex=int(e.exit_idx); uu=float(u.iloc[int(e.idx)])
    after=df.iloc[ex+1:ex+21]
    beyond=((E-after['close'])*s >= uu)   # buy: close < E-u ; sell: close > E+u
    cls.append('PHA_THAT' if beyond.any() else 'QUET')
sl=sl.assign(cls=cls)
print("Lenh SL cua C: phan loai\n", sl.cls.value_counts().to_string())
print("Theo phase:\n", pd.crosstab(sl.phase, sl.cls).to_string())
# Thu: SL rong hon (them 1u) & TP 2R tren cung entries -> ket qua?
ent,_=C.run(P, pen_ticks=2, min_width=6.0, tp_mode='fixed2')
for extra in (0.0, 0.5, 1.0):
    ee=[]
    for e in ent:
        e=dict(e); s=e['side']; uu=float(u.iloc[e['idx']]); d=abs(e['entry']-e['sl'])+extra*uu
        if d>4.0: continue
        e['sl']=e['entry']-s*d; e['tp']=e['entry']+s*2*d; ee.append(e)
    tt=K.simulate(df, ee); m=K.metrics(tt)
    print(f"SL +{extra}u: n={m['n']} WR={m['wr']:.0%} R_TB={m['avg_r']:+.2f}")
# Thu: vao bang limit tai canh E thay vi close (gia tot hon), SL giu nguyen
ee=[]
for e in ent:
    e=dict(e); s=e['side']; E=e['edge']
    # limit tai E: gia su khop neu nen ke tiep cham E
    nxt=df.iloc[e['idx']+1]
    touch = (nxt['low']<=E) if s>0 else (nxt['high']>=E)
    if not touch: continue
    e['entry']=E; d=abs(E-e['sl']); 
    if d<=0: continue
    e['tp']=E+s*2*d; e['idx']=e['idx']+1; ee.append(e)
tt=K.simulate(df, ee); m=K.metrics(tt); print(f"Limit tai E (khop nen ke): n={m['n']} WR={m['wr']:.0%} R_TB={m['avg_r']:+.2f}")
