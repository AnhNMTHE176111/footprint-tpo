#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAI TIEN #1 — ABSORPTION qua DELTA NGUOC PHIA (lead: delta nguoc phia lenh WR52% vs cung phia 36%).
Y nghia: vao LONG tai ho tro ma thay delta BAN (am) bi HAP THU -> gia giu -> dao len. Nguoc lai voi short.
Test cac bo loc tren feed ghep 6 thang (delta THAT). So voi baseline: phang +15.5R, nhoi>=3 +39.5R, WR45%."""
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
    s['r']=sim_rr(s,1.5);eb=B[s['i']]
    s['has_delta']=eb['has_delta'];s['ddom']=eb['ddom']
    # absorption tai NHIP CHAM vung: xet nen vao + toi da 2 nen truoc (nhip test vung)
    win=[B[k] for k in range(max(0,s['i']-2),s['i']+1) if B[k]['has_delta']]
    s['ddom_win']=(sum(x['delta'] for x in win)/sum(x['v_fp'] for x in win)) if win and sum(x['v_fp'] for x in win)>0 else None
S=[s for s in S if s['r'] is not None]

def opp(s,use_win=False,thr=0.0):
    d=s['ddom_win'] if use_win else s['ddom']
    if d is None:return None   # khong co delta
    # nguoc phia = long voi delta<=-thr, short voi delta>=+thr
    return (d<=-thr) if s['side']=='LONG' else (d>=thr)

def report(name,keep):
    """keep(s)->True giu, False bo, None=khong co delta (xu ly rieng)."""
    kept=[s for s in S if keep(s) is True]
    nod=[s for s in S if keep(s) is None]
    if not kept:print(f"  {name:<40} (rong)");return
    wr=sum(s['r']>0 for s in kept)/len(kept)
    flat=[s['r'] for s in kept];nhoi=[(3 if s['confl']>=3 else 1)*s['r'] for s in kept]
    print(f"  {name:<40} n={len(kept):>3} WR{wr*100:>3.0f}% phang{sum(flat):>+6.1f} nhoi>=3{sum(nhoi):>+6.1f} MDD{dd(nhoi):>4.0f}  (bo{len([s for s in S if keep(s) is False])}, khong-delta{len(nod)})")

print(f"\nBASELINE tren tap nay: n={len(S)} WR{sum(s['r']>0 for s in S)/len(S)*100:.0f}% phang{sum(s['r'] for s in S):+.1f} nhoi>=3 {sum((3 if s['confl']>=3 else 1)*s['r'] for s in S):+.1f}")
print("\n### Loc ABSORPTION (delta nguoc phia). None(khong delta) xu ly theo 2 kieu:")
print("--- Kieu A: BO luon nen khong co delta (chi giu absorption ro) ---")
for t in (0.0,0.15,0.25,0.4):
    report(f"nen-vao ddom nguoc >= {t}",lambda s:opp(s,False,t))
    report(f"nhip(3nen) ddom nguoc >= {t}",lambda s:opp(s,True,t))
print("--- Kieu B: GIU nen khong co delta (chi bo same-side ro) ---")
for t in (0.0,0.15,0.25):
    report(f"nen-vao (giu no-delta) nguoc>={t}",lambda s:(True if not s['has_delta'] else opp(s,False,t)))
    report(f"nhip(3nen)(giu no-delta) nguoc>={t}",lambda s:(True if s['ddom_win'] is None else opp(s,True,t)))
print("--- Ket hop: absorption nguoc + confl>=2 (mac dinh) da co; thu absorption + nhoi khi confl>=3 ---")
# da nam trong cot 'nhoi>=3' o tren
