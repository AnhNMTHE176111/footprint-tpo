#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHON DIEU KIEN WINRATE CAO NHAT -> NHOI 3 LOT DUNG VAO DO (user 2026-07-28).
Base = he scalp hien tai: vao lenh khi hop luu>=2, 1 lot, RR1.5.
Quet nhieu dieu kien con (sub-filter cua confl>=2), xep theo WR. Voi moi dieu kien:
  nhoi = 3 lot neu lenh THUOC dieu kien do, con lai 1 lot.
Do tong R, MDD, R/MDD, n_nhoi, WR_nhoi + theo thang. So voi phang & nhoi-confl>=3.
dxFeed 5-7/2026, delta-free."""
import entry_dxfeed as E
from collections import Counter
TICK=0.1
E.B=E.load_m1();E.VOLFLOOR_AUTO=E.calc_volfloor(E.B);pool=E.build_zones(E.B);E.USE_DELTA=False
MONTHS=('2026-05','2026-06','2026-07');B=E.B
def sim(s,rr=1.5):
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

C=E.prep(dict(E.make(MIN_CONFL=2)))
raw=E.run(B,pool,C)
S=[s for s in E.dedup(raw,pool,C) if s['ym'] in MONTHS]
S.sort(key=lambda s:s['i'])
for s in S:s['r']=sim(s,1.5)
S=[s for s in S if s['r'] is not None]   # confl>=2 da dong

# --- cac dieu kien ung vien (deu la subset cua confl>=2) ---
def scen2(s):return s['scen'].startswith('2')            # cham&dao (dao chieu)
def scen2dn(s):return s['scen'].startswith('2') and s['side']=='SHORT'
def scen2up(s):return s['scen'].startswith('2') and s['side']=='LONG'
def scen1(s):return s['scen'].startswith('1')            # pha&hoi (momentum)
CANDS={
 'confl>=3'              : lambda s:s['confl']>=3,
 'confl>=3 + climax'     : lambda s:s['confl']>=3 and s['climax'],
 'confl>=4'              : lambda s:s['confl']>=4,
 'cham&dao (ca 2 phia)'  : scen2,
 'cham&dao XUONG (short)': scen2dn,
 'cham&dao LEN (long)'   : scen2up,
 'pha&hoi (momentum)'    : scen1,
 'cham&dao + confl>=3'   : lambda s:scen2(s) and s['confl']>=3,
 'climax'                : lambda s:s['climax'],
 'cham&dao + climax'     : lambda s:scen2(s) and s['climax'],
}
def wr_of(cond):
    g=[s for s in S if cond(s)]
    if not g:return (0,0,0)
    return (len(g),sum(x['r']>0 for x in g)/len(g),sum(x['r'] for x in g))

print("="*70)
print("XEP HANG DIEU KIEN THEO WINRATE (trong base confl>=2, RR1.5)")
print("="*70)
print(f"  {'dieu kien':<26}{'n':>5}{'WR':>6}{'R(1lot)':>9}{'exp/lenh':>10}")
rank=[]
for name,cond in CANDS.items():
    n,wr,R=wr_of(cond)
    rank.append((name,cond,n,wr,R))
for name,cond,n,wr,R in sorted(rank,key=lambda x:-x[3]):
    print(f"  {name:<26}{n:>5}{wr*100:>5.0f}%{R:>+9.1f}{(R/n if n else 0):>+10.2f}")

# chon dieu kien WR cao nhat co n>=20 (du de nhoi co nghia)
elig=[r for r in rank if r[2]>=20]
best=max(elig,key=lambda x:x[3])
print(f"\n>> WR cao nhat (n>=20): '{best[0]}'  (n={best[2]}, WR {best[3]*100:.0f}%, +{best[4]:.1f}R@1lot)")

def scheme(cond):
    flat=[s['r'] for s in S]
    nhoi=[(3 if cond(s) else 1)*s['r'] for s in S]
    ng=[s for s in S if cond(s)]
    return sum(flat),dd(flat),sum(nhoi),dd(nhoi),len(ng)

print("\n"+"="*70)
print("NHOI 3 LOT theo tung TRIGGER (giu 1 lot cho phan con lai, base confl>=2)")
print("="*70)
print(f"  {'trigger nhoi':<26}{'#nhoi':>6}{'tong_phang':>11}{'tong_nhoi':>10}{'MDD_nhoi':>9}{'R/MDD':>7}")
triggers=['(WR cao nhat) '+best[0], 'confl>=3', 'cham&dao XUONG (short)', 'cham&dao + confl>=3', 'confl>=3 + climax']
seen=set()
for t in triggers:
    key=t.replace('(WR cao nhat) ','')
    if key in seen:continue
    seen.add(key)
    cond=CANDS[key]
    fp,fmdd,np_,nmdd,ng=scheme(cond)
    print(f"  {t:<26}{ng:>6}{fp:>+11.1f}{np_:>+10.1f}{nmdd:>9.1f}{(np_/nmdd if nmdd>0 else 0):>7.2f}")

print("\n"+"="*70)
print(f"CHI TIET THEO THANG — nhoi vao '{best[0]}' (WR cao nhat)")
print("="*70)
bc=best[1]
print(f"  {'thang':<10}{'#lenh':>6}{'#nhoi':>6}{'WR%':>6}{'phang':>9}{'nhoi':>9}")
for m in MONTHS:
    mm=[s for s in S if s['ym']==m]
    if not mm:continue
    ph=sum(s['r'] for s in mm);nh=sum((3 if bc(s) else 1)*s['r'] for s in mm)
    print(f"  {m:<10}{len(mm):>6}{sum(bc(s) for s in mm):>6}{sum(s['r']>0 for s in mm)/len(mm)*100:>6.0f}{ph:>+9.1f}{nh:>+9.1f}")
