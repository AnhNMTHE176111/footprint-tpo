#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boc theo thang 5/6/7: so lenh, win, loss, tong R — cho baseline & absorption & nhoi."""
import fp_merged as M
import entry_dxfeed as E
TICK=E.TICK
B=M.load_merged()
E.VOLFLOOR_AUTO=E.calc_volfloor(B);pool=E.build_zones(B)
def sim(s,rr=1.5):
    e=s['entry'];sl=s['sl'];sd=s['side'];risk=s['risk_t']*TICK
    tp=e+rr*risk if sd=='LONG' else e-rr*risk
    for j in range(s['i']+1,len(B)):
        b=B[j]
        if (b['lo']<=sl if sd=='LONG' else b['hi']>=sl):return -1.0
        if (b['hi']>=tp if sd=='LONG' else b['lo']<=tp):return rr
    return None
E.USE_DELTA=False
C=E.prep(dict(E.make(MIN_CONFL=2)))
S=[s for s in E.dedup(E.run(B,pool,C),pool,C)]
S.sort(key=lambda s:s['i'])
for s in S:
    s['r']=sim(s,1.5)
    win=[B[k] for k in range(max(0,s['i']-2),s['i']+1) if B[k]['has_delta']]
    tv=sum(x['v_fp'] for x in win);s['ddw']=(sum(x['delta'] for x in win)/tv) if win and tv>0 else None
S=[s for s in S if s['r'] is not None]
def keepAbs(s):
    d=s['ddw']
    if d is None:return True
    return (d<=0) if s['side']=='LONG' else (d>=0)
MONTHS=['2026-05','2026-06','2026-07']
def tbl(name,sigs,nhoi=False):
    print(f"\n### {name}")
    print(f"  {'thang':<9}{'lenh':>5}{'win':>5}{'loss':>5}{'WR':>6}{'R':>8}")
    tn=tw=tl=0;tR=0.0
    for m in MONTHS:
        g=[s for s in sigs if s['ym']==m]
        w=sum(s['r']>0 for s in g);l=sum(s['r']<0 for s in g)
        R=sum((3 if (nhoi and s['confl']>=3) else 1)*s['r'] for s in g)
        tn+=len(g);tw+=w;tl+=l;tR+=R
        wr=100*w/len(g) if g else 0
        print(f"  {m:<9}{len(g):>5}{w:>5}{l:>5}{wr:>5.0f}%{R:>+8.1f}")
    print(f"  {'TONG':<9}{tn:>5}{tw:>5}{tl:>5}{(100*tw/tn if tn else 0):>5.0f}%{tR:>+8.1f}")

Sm=[s for s in S if s['ym'] in MONTHS]
Sa=[s for s in Sm if keepAbs(s)]
tbl("BASELINE (confl>=2, 1 lot, RR1.5)",Sm)
tbl("BASELINE + NHOI x3 khi confl>=3",Sm,nhoi=True)
tbl("LOC ABSORPTION (1 lot)",Sa)
tbl("LOC ABSORPTION + NHOI x3 khi confl>=3",Sa,nhoi=True)
