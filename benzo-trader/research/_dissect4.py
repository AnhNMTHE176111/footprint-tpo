import sys; sys.argv=['x']
import numpy as np, pandas as pd, kernel as K
from _dissect import BASE
import setup_c_fade_canh as C, setup_a_pha_hoi as A
P=C.prepare(BASE); df=P['df']; u=P['u']
D=A.Data(BASE)
def sim_be(df, ents, be_r):
    """mo phong co doi SL ve hoa khi gia di duoc be_r R (kiem tra bang high/low nen sau)"""
    rows=[]
    for e in ents:
        i=int(e['idx']); s=e['side']; ent=e['entry']; sl=e['sl']; tp=e['tp']; R=abs(ent-sl); be=False
        for j in range(i+1, min(i+400,len(df))):
            b=df.iloc[j]
            hit_sl=(b['low']<=sl) if s>0 else (b['high']>=sl)
            hit_tp=(b['high']>=tp) if s>0 else (b['low']<=tp)
            if hit_sl: rows.append(0.0 if be else -1.0); break
            if hit_tp: rows.append((tp-ent)*s/R); break
            fav=((b['high'] if s>0 else b['low'])-ent)*s
            if be_r and not be and fav>=be_r*R: sl=ent; be=True
        else: continue
    r=np.array(rows)-0.2/np.array([abs(e['entry']-e['sl']) for e in ents][:len(rows)])
    return len(r), (r>0).mean(), r.mean()
def variants(name, ents, dfx, uu):
    print(f"\n== {name} n_ent={len(ents)}")
    for be in (0, 1.0, 1.5):
        n,wr,ar=sim_be(dfx, ents, be); print(f"  be@{be}R: n={n} WR={wr:.0%} R_TB={ar:+.2f}")
    # loc 'o lung': |entry - E| <= 1 gia
    near=[e for e in ents if abs(e['entry']-e.get('edge',e.get('E',np.nan)))<=1.0] if 'edge' in ents[0] else ents
    if near is not ents: n,wr,ar=sim_be(dfx, near, 0); print(f"  chi vao khi |entry-E|<=1 gia: n={n} WR={wr:.0%} R_TB={ar:+.2f}")
    # SL = ngoai E >= 1u
    ee=[]
    for e in ents:
        E=e.get('edge',None)
        if E is None: continue
        s=e['side']; i=int(e['idx']); d=max(abs(e['entry']-e['sl']), (abs(e['entry']-E)+float(uu.iloc[i])))
        if d>4: continue
        e2=dict(e); e2['sl']=e['entry']-s*d; e2['tp']=e['entry']+s*2*d; ee.append(e2)
    if ee: n,wr,ar=sim_be(dfx, ee, 0); print(f"  SL ngoai E >=1u (TP2R): n={n} WR={wr:.0%} R_TB={ar:+.2f}")
    # loai 3 nen sau nen dai nhat 20 nen
    keep=[]
    for e in ents:
        i=int(e['idx']); seg=df.iloc[max(0,i-20):i+1]; rg=(seg['high']-seg['low']).to_numpy(); k=rg.argmax()
        if len(rg)-1-k > 3: keep.append(e)
    n,wr,ar=sim_be(dfx, keep, 0); print(f"  loai <=3 nen sau nen dai nhat 20 nen: n={n} WR={wr:.0%} R_TB={ar:+.2f}")
entC,_=C.run(P,pen_ticks=2,min_width=6.0,tp_mode='fixed2'); variants('C fade TP2R', entC, df, u)
entA,_=A.run(D,n_min=3,body=0.5,expire=30,rr=2.0)
for e in entA:
    e.setdefault('edge', e.get('E', e.get('zone_price', np.nan)))
print(list(entA[0].keys()))
variants('A pha hoi TP2R', entA, D.df, K.median_range(D.df))
