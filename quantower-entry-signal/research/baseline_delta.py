#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASELINE tren feed GHEP 6 thang CO DELTA THAT.
So sanh: (1) delta-free (nen) vs delta-that; (2) do lai nhoi confl>=3; (3) do phu 'mot' (max_one_trade)."""
import fp_merged as M
import entry_dxfeed as E
import statistics as st
from collections import Counter
TICK=E.TICK
B=M.load_merged()
E.VOLFLOOR_AUTO=E.calc_volfloor(B);pool=E.build_zones(B)
MONTHS=tuple(sorted(set(b['ym'] for b in B)))
print(f"merged {len(B)} bar, {len(pool)} zone, thang={MONTHS}")
# do phu mot
motpos=sum(1 for b in B if b['mot']>0);print(f"'mot' co gia tri >0: {100*motpos/len(B):.0f}% bar (big-trade dung duoc neu cao)")

def sim_rr(s,rr=1.5):
    entry=s['entry'];sl=s['sl'];side=s['side'];risk=s['risk_t']*TICK
    tp=entry+rr*risk if side=='LONG' else entry-rr*risk
    for j in range(s['i']+1,len(B)):
        hb=B[j]
        if (hb['lo']<=sl if side=='LONG' else hb['hi']>=sl):return -1.0
        if (hb['hi']>=tp if side=='LONG' else hb['lo']<=tp):return rr
    return None
def dd(seq):
    eq=0.0;pk=0.0;m=0.0
    for r in seq:eq+=r;pk=max(pk,eq);m=max(m,pk-eq)
    return m
def getsig():
    E.USE_DELTA=False   # sinh tin hieu tren NEN (delta-gate nen-vao da chung minh over-filter); giu delta de LOC SAU
    C=E.prep(dict(E.make(MIN_CONFL=2)))
    raw=E.run(B,pool,C)
    S=[s for s in E.dedup(raw,pool,C)]
    S.sort(key=lambda s:s['i'])
    for s in S:
        s['r']=sim_rr(s,1.5)
        eb=B[s['i']];s['has_delta']=eb['has_delta'];s['ddom']=eb['ddom'];s['bar']=eb
    return [s for s in S if s['r'] is not None]

S=getsig()
wr=sum(s['r']>0 for s in S)/len(S)
flat=[s['r'] for s in S];nhoi=[(3 if s['confl']>=3 else 1)*s['r'] for s in S]
c3=sum(s['confl']>=3 for s in S)
print(f"\n===== BASELINE (nen, delta giu de loc) — 6 thang feed ghep =====")
print(f"  n={len(S)}  WR {wr*100:.0f}%  | confl>=3: {c3} ({100*c3/len(S):.0f}%) | co delta tren nen vao: {sum(s['has_delta'] for s in S)}/{len(S)}")
print(f"  phang 1 lot:      tong {sum(flat):+.1f}R  MDD {dd(flat):.1f}  exp {sum(flat)/len(S):+.3f}R")
print(f"  nhoi 3 lot >=3:   tong {sum(nhoi):+.1f}R  MDD {dd(nhoi):.1f}")
print("  theo thang (phang | n):",end="")
for m in MONTHS:
    mm=[s for s in S if s['ym']==m]
    if mm:print(f"  {m[-2:]}={sum(s['r'] for s in mm):+.0f}(n{len(mm)})",end="")
print()
# nhanh phu: delta co giup PHAN LOAI thang/thua khong? (dieu tra, chua phai loc)
wd=[s for s in S if s['has_delta']]
for lbl,cond in [("ddom cung phia lenh (long:ddom>0)",lambda s:(s['ddom']>0)==(s['side']=='LONG')),
                 ("|ddom|>=0.25",lambda s:abs(s['ddom'])>=0.25)]:
    g=[s for s in wd if cond(s)];gw=[s for s in wd if not cond(s)]
    if g and gw:
        print(f"  [dieu tra] {lbl}: n={len(g)} WR{sum(s['r']>0 for s in g)/len(g)*100:.0f}% R{sum(s['r'] for s in g):+.0f}  || nguoc lai n={len(gw)} WR{sum(s['r']>0 for s in gw)/len(gw)*100:.0f}% R{sum(s['r'] for s in gw):+.0f}")
