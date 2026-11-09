import sys, numpy as np, pandas as pd
sys.argv=['x']
import kernel as K
import setup_c_fade_canh as C
import setup_a_pha_hoi as A
from _dissect import dissect, BASE
P=C.prepare(BASE); df=P['df']; u=P['u']
ent,_=C.run(P, pen_ticks=2, min_width=6.0, tp_mode='fixed2')
# NGHICH DAO C: sau nen phá hụt (dong trong range), dat STOP ngoài râu phá hụt; neu khop trong 10 nen -> vao theo chieu PHA.
# SL = canh E lui vao trong range 1u (hoac rau doi dien nen poke neu xa hon? giu don gian: E -/+ 1u), TP 2R. Tran SL 4 gia.
for slk in (0.5, 1.0, 1.5):
  for rr in (2.0, 3.0):
    ee=[]
    for e in ent:
        s=-int(e['side'])   # chieu pha = nguoc chieu fade
        E=e['edge']; i=int(e['idx']); pk=df.iloc[int(e['poke_idx'])]
        trig = (pk['high']+0.1) if s>0 else (pk['low']-0.1)
        uu=float(u.iloc[i])
        fill=None
        for j in range(i+1, min(i+11, len(df))):
            b=df.iloc[j]
            if (s>0 and b['high']>=trig) or (s<0 and b['low']<=trig):
                fill=j; break
        if fill is None: continue
        sl = E - s*slk*uu
        d=(trig-sl)*s
        if d<=0 or d>4.0: continue
        ee.append(dict(idx=fill, side=s, entry=trig, sl=sl, tp=trig+s*rr*d, setup='Cinv', zone=e['zone'], note=''))
    tt=K.simulate(df, ee); m=K.metrics(tt)
    tt['t']=pd.to_datetime(tt['t_utc']); tr=tt[tt.t<'2026-09-16']; te=tt[tt.t>='2026-09-16']
    mtr=K.metrics(tr); mte=K.metrics(te)
    print(f"NGHICH DAO C | SL={slk}u TP={rr}R: n={m['n']} WR={m['wr']:.0%} R_TB={m['avg_r']:+.2f} | TRAIN n={mtr['n']} {mtr['avg_r']:+.2f} | TEST n={mte['n']} {mte['avg_r']:+.2f}")
print("\n######## SETUP A")
D=A.Data(BASE)
_,tA=A.run(D, n_min=3, body=0.5, expire=30)
dA=dissect(tA, D.df, K.median_range(D.df), 'A pha hoi V3 TP3R')
_,tA2=A.run(D, n_min=3, body=0.5, expire=30, rr=2.0)
dA2=dissect(tA2, D.df, K.median_range(D.df), 'A pha hoi V3 TP2R')
