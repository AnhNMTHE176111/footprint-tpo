#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XAC NHAN bo loc ABSORPTION tot nhat: side LONG & ddom_win<=0, SHORT & ddom_win>=0, hoac KHONG co delta -> GIU.
Kiem: (1) robust theo THANG? (2) co phai chi la 'chon kich ban dao chieu' (scen2) khong? (3) combined + nhoi>=3."""
import fp_merged as M
import entry_dxfeed as E
TICK=E.TICK
B=M.load_merged()
E.VOLFLOOR_AUTO=E.calc_volfloor(B);pool=E.build_zones(B)
MONTHS=tuple(sorted(set(b['ym'] for b in B)))
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
E.USE_DELTA=False
C=E.prep(dict(E.make(MIN_CONFL=2)))
S=[s for s in E.dedup(E.run(B,pool,C),pool,C)]
S.sort(key=lambda s:s['i'])
for s in S:
    s['r']=sim_rr(s,1.5)
    win=[B[k] for k in range(max(0,s['i']-2),s['i']+1) if B[k]['has_delta']]
    tv=sum(x['v_fp'] for x in win)
    s['ddom_win']=(sum(x['delta'] for x in win)/tv) if win and tv>0 else None
S=[s for s in S if s['r'] is not None]
def KEEP(s):
    d=s['ddom_win']
    if d is None:return True
    return (d<=0) if s['side']=='LONG' else (d>=0)

def blk(name,ss):
    if not ss:print(f"  {name:<20} (rong)");return
    wr=sum(x['r']>0 for x in ss)/len(ss)
    flat=[x['r'] for x in ss];nhoi=[(3 if x['confl']>=3 else 1)*x['r'] for x in ss]
    print(f"  {name:<20} n={len(ss):>3} WR{wr*100:>3.0f}% phang{sum(flat):>+6.1f} nhoi>=3{sum(nhoi):>+6.1f} MDD{dd(nhoi):>4.0f}")
F=[s for s in S if KEEP(s)]
DROP=[s for s in S if not KEEP(s)]
print(f"\n=== TONG QUAN (6 thang) ===")
blk("baseline (het)",S)
blk("SAU loc absorption",F)
blk("bi BO",DROP)
print(f"\n=== BO nhung gi? (scen) — kiem co phai chi la 'chon dao chieu' ===")
print(f"  Trong {len(DROP)} lenh bi bo: pha&hoi(scen1)={sum(x['scen'].startswith('1') for x in DROP)}  cham&dao(scen2)={sum(x['scen'].startswith('2') for x in DROP)}")
print(f"  Trong {len(F)} lenh GIU:     pha&hoi(scen1)={sum(x['scen'].startswith('1') for x in F)}  cham&dao(scen2)={sum(x['scen'].startswith('2') for x in F)}")
# so voi chi loc scen2 (bo het pha&hoi) de tach bach
onlyRev=[s for s in S if s['scen'].startswith('2')]
blk("(so sanh) chi cham&dao scen2",onlyRev)
print(f"\n=== ROBUST THEO THANG (phang 1 lot) ===")
print(f"  {'thang':<9}{'base_n':>7}{'base_R':>8}{'  |':>4}{'loc_n':>6}{'loc_WR':>7}{'loc_R':>7}{'loc_nhoi':>9}")
for m in MONTHS:
    bm=[s for s in S if s['ym']==m];fm=[s for s in F if s['ym']==m]
    if not bm:continue
    fw=sum(x['r']>0 for x in fm)/len(fm)*100 if fm else 0
    print(f"  {m:<9}{len(bm):>7}{sum(x['r'] for x in bm):>+8.1f}{'  |':>4}{len(fm):>6}{fw:>6.0f}%{sum(x['r'] for x in fm):>+7.1f}{sum((3 if x['confl']>=3 else 1)*x['r'] for x in fm):>+9.1f}")
print(f"\n=== COMBINED: loc absorption + nhoi 3 lot khi confl>=3 ===")
nhoi=[(3 if x['confl']>=3 else 1)*x['r'] for x in F]
print(f"  tong {sum(nhoi):+.1f}R  MDD {dd(nhoi):.1f}  WR {sum(x['r']>0 for x in F)/len(F)*100:.0f}%  n={len(F)} (nhoi {sum(x['confl']>=3 for x in F)} lenh)")
