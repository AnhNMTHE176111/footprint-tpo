#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RESEARCH WR + THANG RR THEO HOP LUU (user 2026-07-28).
1) Do MFE (max favorable excursion) theo tung muc hop luu -> gia co CHAY xa hon o hop luu manh khong?
   (day la cot loi: neu MFE tran ~1.5R thi TP 4-5R KHONG the an duoc)
2) Thang RR theo hop luu: nhe->1.5R, >=2->2R/3R, >=3->4R/5R (chay that 2 version).
3) Tran WR that su + duong bien WR<->so lenh + hạ RR co keo WR len khong.
Chay tren dxFeed 5-7/2026, delta-free."""
import entry_dxfeed as E
import statistics as st
TICK=0.1
E.B=E.load_m1();E.VOLFLOOR_AUTO=E.calc_volfloor(E.B);pool=E.build_zones(E.B);E.USE_DELTA=False
MONTHS=('2026-05','2026-06','2026-07')
B=E.B

def sim_rr(s,rr):
    entry=s['entry'];sl=s['sl'];side=s['side'];risk=s['risk_t']*TICK
    tp=entry+rr*risk if side=='LONG' else entry-rr*risk
    for j in range(s['i']+1,len(B)):
        hb=B[j]
        hitSL=hb['lo']<=sl if side=='LONG' else hb['hi']>=sl
        hitTP=hb['hi']>=tp if side=='LONG' else hb['lo']<=tp
        if hitSL:return 'SL',-1.0
        if hitTP:return 'TP',rr
    return 'open',0.0
def mfe(s):
    entry=s['entry'];sl=s['sl'];side=s['side'];risk=s['risk_t']*TICK
    best=0.0
    for j in range(s['i']+1,len(B)):
        hb=B[j]
        fav=(hb['hi']-entry) if side=='LONG' else (entry-hb['lo'])
        best=max(best,fav/risk)
        if (hb['lo']<=sl if side=='LONG' else hb['hi']>=sl):break
    return best

# BASE: lay TAT CA setup (hop luu >=1) de bucket theo confl
print("Chay base (hop luu>=1)...")
C=E.prep(dict(E.make(MIN_CONFL=1)))
raw=E.run(B,pool,C)
sig=[s for s in E.dedup(raw,pool,C) if s['ym'] in MONTHS]
for s in sig:s['mfe']=mfe(s)
print(f"tong setup (confl>=1): {len(sig)}")

def bucket(c):return '1' if c==1 else ('2' if c==2 else '>=3')
print("\n### MFE + WR@1.5R theo MUC HOP LUU (co chay xa hon khong?)")
print(f"{'hop luu':<8}{'n':>5}{'MFE_median':>12}{'MFE_p75':>10}{'%MFE>=2R':>10}{'%>=3R':>8}{'%>=4R':>8}{'WR@1.5':>9}")
for bk in ['1','2','>=3']:
    g=[s for s in sig if bucket(s['confl'])==bk]
    if not g:continue
    mfes=[s['mfe'] for s in g]
    wr15=[sim_rr(s,1.5)[0] for s in g];settled=[o for o in wr15 if o in('TP','SL')]
    wr=sum(o=='TP' for o in settled)/len(settled) if settled else 0
    print(f"{bk:<8}{len(g):>5}{st.median(mfes):>11.2f}R{sorted(mfes)[int(len(mfes)*0.75)]:>9.2f}R"
          f"{100*sum(m>=2 for m in mfes)/len(g):>9.0f}%{100*sum(m>=3 for m in mfes)/len(g):>7.0f}%"
          f"{100*sum(m>=4 for m in mfes)/len(g):>7.0f}%{wr*100:>8.0f}%")

def eval_ladder(ladder,gate,label):
    g=[s for s in sig if s['confl']>=gate]
    tot=0.0;tp=0;n=0
    for s in g:
        rr=ladder(s['confl']);o,r=sim_rr(s,rr)
        if o in('TP','SL'):n+=1;tp+=(o=='TP');tot+=r
    wr=tp/n if n else 0
    print(f"  {label:<34} n={n:>3} WR {wr*100:>3.0f}% tong {tot:+6.1f}R exp {tot/n if n else 0:+.2f}R")

print("\n### THANG RR THEO HOP LUU (gate >=2, tru khi ghi 'gom confl1')")
eval_ladder(lambda c:1.5, 2, "PHANG 1.5R (nen tham chieu)")
eval_ladder(lambda c:(2.0 if c==2 else 4.0), 2, "V1: 2->2R, >=3->4R")
eval_ladder(lambda c:(3.0 if c==2 else 5.0), 2, "V2: 2->3R, >=3->5R")
eval_ladder(lambda c:(1.5 if c==2 else 3.0), 2, "V3 nhe: 2->1.5R, >=3->3R")
eval_ladder(lambda c:(2.0 if c==2 else 3.0), 2, "V4: 2->2R, >=3->3R")
print("  --- co gom ca hop luu NHE (confl==1) @1.5R de tang so luong ---")
eval_ladder(lambda c:(1.5 if c<=2 else 4.0), 1, "V5: 1&2->1.5R, >=3->4R")
eval_ladder(lambda c:(1.5 if c==1 else (2.0 if c==2 else 4.0)), 1, "V6: 1->1.5, 2->2, >=3->4")

print("\n### TRAN WR: loc manh dan (hop luu>=2 base)")
g2=[s for s in sig if s['confl']>=2]
def wrstat(ss,rr=1.5):
    r=[sim_rr(s,rr) for s in ss];se=[x for x in r if x[0] in('TP','SL')]
    tp=sum(x[0]=='TP' for x in se);R=sum(x[1] for x in r)
    return len(se),(tp/len(se) if se else 0),R
for lbl,ss in [("all confl>=2",g2),
               ("+climax tim",[s for s in g2 if s['climax']]),
               ("+zone manh>=66",[s for s in g2 if s['zstr']>=66]),
               ("confl>=3",[s for s in sig if s['confl']>=3]),
               ("confl>=3+climax",[s for s in sig if s['confl']>=3 and s['climax']]),
               ("confl>=4",[s for s in sig if s['confl']>=4]),
               ("chi cham&dao xuong confl>=2",[s for s in g2 if s['scen']=='2 cham&dao xuong'])]:
    n,wr,R=wrstat(ss);print(f"  {lbl:<30} n={n:>3} WR {wr*100:>3.0f}% tong {R:+.0f}R")

print("\n### HA RR co keo WR len 80% khong? (confl>=2)")
for rr in (0.6,0.8,1.0,1.2,1.5):
    n,wr,R=wrstat(g2,rr);print(f"  RR {rr}: n={n} WR {wr*100:.0f}% tong {R:+.0f}R exp {R/n if n else 0:+.2f}R")
