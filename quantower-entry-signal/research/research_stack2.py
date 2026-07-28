#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NHOI 3 LOT CUNG entry/SL/TP=1.5R KHI HOP LUU>=3 (user 2026-07-28).
Base van la he hien tai: chi vao lenh khi confl>=2.
  - confl==2 : 1 lot
  - confl>=3 : 3 lot (cung entry/SL/TP=1.5R => WR khong doi, chi x3 size lenh do)
Thong ke DAY DU: so lenh, WR (tong + tung nhom), tong R (size-weighted) vs base phang,
MDD, chuoi thua, R/tung thang, va R tren MOI DON VI VON bo ra (de thay tang R den tu dau).
dxFeed 5-7/2026, delta-free."""
import entry_dxfeed as E
TICK=0.1
E.B=E.load_m1();E.VOLFLOOR_AUTO=E.calc_volfloor(E.B);pool=E.build_zones(E.B);E.USE_DELTA=False
MONTHS=('2026-05','2026-06','2026-07')
B=E.B

def sim_rr(s,rr=1.5):
    entry=s['entry'];sl=s['sl'];side=s['side'];risk=s['risk_t']*TICK
    tp=entry+rr*risk if side=='LONG' else entry-rr*risk
    for j in range(s['i']+1,len(B)):
        hb=B[j]
        if (hb['lo']<=sl if side=='LONG' else hb['hi']>=sl):return -1.0
        if (hb['hi']>=tp if side=='LONG' else hb['lo']<=tp):return rr
    return None

def dd(seq):  # seq R theo thu tu tg -> (MDD, chuoi thua dai nhat)
    eq=0.0;peak=0.0;mdd=0.0;st=0;ws=0
    for r in seq:
        eq+=r;peak=max(peak,eq);mdd=max(mdd,peak-eq)
        if r<0:st+=1;ws=max(ws,st)
        else:st=0
    return mdd,ws

C=E.prep(dict(E.make(MIN_CONFL=2)))
raw=E.run(B,pool,C)
sig=[s for s in E.dedup(raw,pool,C) if s['ym'] in MONTHS]
sig.sort(key=lambda s:s['i'])
for s in sig:s['r']=sim_rr(s,1.5)
S=[s for s in sig if s['r'] is not None]   # da dong

def size(s):return 3 if s['confl']>=3 else 1

n2=[s for s in S if s['confl']==2];n3=[s for s in S if s['confl']>=3]
def wr(ss):
    w=sum(x['r']>0 for x in ss);return (w,len(ss),100*w/len(ss) if ss else 0)

print(f"Tong setup confl>=2 (da dong): {len(S)}   | confl==2: {len(n2)}   confl>=3: {len(n3)}")
print("\n"+"="*70)
print("WINRATE (khong doi theo size — cung nhung lenh do)")
print("="*70)
for lbl,ss in [("confl==2",n2),("confl>=3",n3),("TONG (>=2)",S)]:
    w,n,p=wr(ss);print(f"  {lbl:<14} thang {w:>3}/{n:<3}  WR {p:>4.0f}%")

print("\n"+"="*70)
print("TONG R & DRAWDOWN")
print("="*70)
base=[s['r'] for s in S]                       # phang 1 lot
sized=[size(s)*s['r'] for s in S]              # nhoi 3 lot khi >=3
mdd_b,ws_b=dd(base);mdd_s,ws_s=dd(sized)
units_b=len(S)                                  # von bo ra (don vi rui ro)
units_s=sum(size(s) for s in S)
print(f"  {'so do':<34}{'tongR':>8}{'MDD':>8}{'thua_lien':>10}{'von_bo_ra':>11}{'R/von':>8}")
print(f"  {'PHANG 1 lot (he hien tai)':<34}{sum(base):>+8.1f}{mdd_b:>8.1f}{ws_b:>10}{units_b:>11}{sum(base)/units_b:>+8.3f}")
print(f"  {'NHOI 3 lot khi >=3':<34}{sum(sized):>+8.1f}{mdd_s:>8.1f}{ws_s:>10}{units_s:>11}{sum(sized)/units_s:>+8.3f}")
print(f"\n  => R tang: {sum(base):+.1f}R  ->  {sum(sized):+.1f}R   (+{sum(sized)-sum(base):.1f}R, tang {100*(sum(sized)-sum(base))/sum(base):.0f}%)")
print(f"     nhung von bo ra cung tang {units_b} -> {units_s} don vi (+{100*(units_s-units_b)/units_b:.0f}%)")
print(f"     R tren moi dong von: {sum(base)/units_b:+.3f}  ->  {sum(sized)/units_s:+.3f}  (nho DON tien vao nhom edge cao)")

print("\n"+"="*70)
print("THEO TUNG THANG (co on dinh khong?)")
print("="*70)
print(f"  {'thang':<10}{'#lenh':>6}{'#>=3':>6}{'WR%':>6}{'R_phang':>9}{'R_nhoi':>9}")
for m in MONTHS:
    mm=[s for s in S if s['ym']==m]
    if not mm:continue
    w,n,p=wr(mm);b=sum(s['r'] for s in mm);z=sum(size(s)*s['r'] for s in mm)
    print(f"  {m:<10}{n:>6}{sum(s['confl']>=3 for s in mm):>6}{p:>6.0f}{b:>+9.1f}{z:>+9.1f}")

print("\n"+"="*70)
print("RIENG NHOM confl>=3 (nhom duoc nhoi) — no co dang tin cay khong?")
print("="*70)
w,n,p=wr(n3);r3=sum(s['r'] for s in n3)
print(f"  n={n}  WR {p:.0f}%  tong (1 lot) {r3:+.1f}R  exp {r3/n:+.3f}R/lenh  |  x3 => {r3*3:+.1f}R")
for m in MONTHS:
    mm=[s for s in n3 if s['ym']==m]
    if mm:
        w2,n2m,p2=wr(mm);print(f"    {m}: n={n2m} WR {p2:.0f}% R(1lot) {sum(s['r'] for s in mm):+.1f}")
