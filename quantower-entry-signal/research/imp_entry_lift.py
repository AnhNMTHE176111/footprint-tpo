#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FEATURE-LIFT tren EntrySignal (scalp RR1.5) — PYTHON REFLECTION (khong phai C# live).
Sinh lenh delta-free (USE_DELTA=False, MIN_CONFL=2, config shipped) tren merged feed,
sim RR1.5 pessimistic (SL truoc TP), giu lenh SETTLED, roi soi subset xau -> ung vien BO.
Cau hoi trung tam: cut 'dead session' [02,08) UTC+7 (da cuu runner) co giup EntrySignal khong?
TRUNG THUC: bao n moi cell; cell n<15 = khong tin (flag). Chi de xuat cut khi (a) co co che
thi truong + (b) nhat quan qua cac thang (cross-tab). dt merged = UTC; UTC+7 = dt+7h."""
import fp_merged as M, entry_dxfeed as E
from collections import defaultdict
TICK=E.TICK

# ---------- 1. sinh lenh (giong bd_month.py) ----------
B=M.load_merged()
E.VOLFLOOR_AUTO=E.calc_volfloor(B); pool=E.build_zones(B)
E.USE_DELTA=False
C=E.prep(dict(E.make(MIN_CONFL=2)))
S=E.dedup(E.run(B,pool,C),pool,C)
S.sort(key=lambda s:s['i'])

def sim(s,rr=1.5):
    e=s['entry'];sl=s['sl'];sd=s['side'];risk=s['risk_t']*TICK
    tp=e+rr*risk if sd=='LONG' else e-rr*risk
    for j in range(s['i']+1,len(B)):
        b=B[j]
        if (b['lo']<=sl if sd=='LONG' else b['hi']>=sl):return -1.0   # SL truoc TP = bi quan
        if (b['hi']>=tp if sd=='LONG' else b['lo']<=tp):return rr
    return None

for s in S:
    s['r']=sim(s,1.5)
    b=B[s['i']]
    s['lhour']=(b['dt'].hour+7)%24                      # UTC+7 display hour (khop runner)
    # absorption entry-bar: delta nguoc huong = tot
    s['has_d']=b['has_delta']
    s['ddom']=b['ddom'] if b['has_delta'] else None
    s['delta']=b['delta'] if b['has_delta'] else None
    # ddw = delta-dominance 3 nen (i-2..i), weighted volume footprint (giong bd_month)
    win=[B[k] for k in range(max(0,s['i']-2),s['i']+1) if B[k]['has_delta']]
    tv=sum(x['v_fp'] for x in win); s['ddw']=(sum(x['delta'] for x in win)/tv) if win and tv>0 else None
    s['kind']=s['zone'].rsplit(' ',1)[0]               # "POC A 3350.0" -> "POC A"

S=[s for s in S if s['r'] is not None]                 # SETTLED only

# ---------- helpers ----------
def stats(rs):
    if not rs:return (0,0.0,0.0,0.0)
    n=len(rs);w=sum(x['r']>0 for x in rs);tot=sum(x['r'] for x in rs)
    return (n,w/n,tot/n,tot)

MONTHS_ALL=sorted(set(s['ym'] for s in S))
M3=['2026-05','2026-06','2026-07']                     # regime thanh khoan (khop runner)

def line(tag,rs):
    n,wr,ev,tot=stats(rs);flag=' <<n_nho' if 0<n<15 else ''
    print(f"  {tag:<22}{n:>5}{wr*100:>6.0f}%{ev:>+8.2f}{tot:>+8.1f}{flag}")

def group(keyfn,title,order_ev=True):
    print(f"\n### {title}")
    print(f"  {'gia tri':<22}{'n':>5}{'WR':>6}{'EV':>8}{'totR':>8}")
    g=defaultdict(list)
    for s in S3:g[keyfn(s)].append(s)
    ks=sorted(g,key=lambda k:stats(g[k])[2]) if order_ev else sorted(g,key=str)
    for k in ks:line(str(k),g[k])

def hourbk(h):
    if 7<=h<14:return 'A (07-14)'
    if 14<=h<19:return 'AU(14-19)'
    if 19<=h<24 or h<2:return 'MY(19-02)'
    return 'dem(02-07)'
def dead(s):return 2<=s['lhour']<8                     # DEAD SESSION [02,08) UTC+7
def absbk(s):
    if not s['has_d']:return 'no-delta'
    same=(s['ddom']>0)==(s['side']=='LONG')            # delta cung huong lenh
    return 'MOMENTUM(cung)' if same else 'ABSORB(nguoc)'
def trendal(s):
    if s['trend']==0:return 'flat'
    return 'thuan' if (s['trend']>0)==(s['side']=='LONG') else 'nguoc'
def vwapal(s):
    return 'thuan-vwap' if (s['vwap_side']=='tren')==(s['side']=='LONG') else 'nguoc-vwap'
def vsabk(s):
    v=s['vsa']
    return '<1.5' if v<1.5 else('1.5-2.2' if v<2.2 else('2.2-3.0' if v<3.0 else '>=3.0'))
def scenbk(s):return s['scen']

# ---------- 2. BASELINE ----------
print("="*70)
print(f"BASELINE EntrySignal (delta-free, confl>=2, RR1.5, sim pessimistic)")
n,wr,ev,tot=stats(S)
print(f"  FULL WINDOW settled n={n} | WR {wr*100:.0f}% | EV {ev:+.3f}R | tong {tot:+.1f}R")
print(f"  cua so: {B[0]['dt']} .. {B[-1]['dt']}  ({len(B)} bar M1, 76% co delta)")
print("  --- theo thang (ALL) ---")
for m in MONTHS_ALL:line(m,[s for s in S if s['ym']==m])
S3=[s for s in S if s['ym'] in M3]                     # PRIMARY regime cho moi phan tich cut
n3,wr3,ev3,tot3=stats(S3)
print(f"  --- PRIMARY (May-Jul, khop runner) n={n3} WR {wr3*100:.0f}% EV {ev3:+.3f}R tong {tot3:+.1f}R ---")

# ---------- 3. DEAD SESSION cross-tab per-month (CAU HOI TRUNG TAM) ----------
print("\n"+"="*70)
print("Q: CUT DEAD SESSION [02,08) UTC+7 co giup EntrySignal? (per-month)")
print("="*70)
print(f"  {'thang':<9}{'DEAD n':>7}{'WR':>5}{'EV':>7}  |{'KEEP(rest) n':>13}{'WR':>5}{'EV':>7}")
for m in M3:
    dd=[s for s in S3 if s['ym']==m and dead(s)]
    kk=[s for s in S3 if s['ym']==m and not dead(s)]
    nd,wd,ed,_=stats(dd);nk,wk,ek,_=stats(kk)
    fd=' *n<15' if 0<nd<15 else ''
    print(f"  {m:<9}{nd:>7}{wd*100:>4.0f}%{ed:>+7.2f}  |{nk:>13}{wk*100:>4.0f}%{ek:>+7.2f}{fd}")
dd=[s for s in S3 if dead(s)];kk=[s for s in S3 if not dead(s)]
nd,wd,ed,td=stats(dd);nk,wk,ek,tk=stats(kk)
print(f"  {'TONG':<9}{nd:>7}{wd*100:>4.0f}%{ed:>+7.2f}  |{nk:>13}{wk*100:>4.0f}%{ek:>+7.2f}")
print(f"  => BO dead: tong R {tot3:+.1f} -> {tk:+.1f} (d {tk-tot3:+.1f}R); dead subset EV {ed:+.2f}R n={nd}")

# ---------- 4. FEATURE GROUPS (May-Jul) ----------
print("\n"+"="*70);print("FEATURE GROUPS (May-Jul, sort EV tang dan = xau trc)");print("="*70)
group(lambda s:hourbk(s['lhour']),"PHIEN (UTC+7 display hour)")
group(lambda s:s['lhour'],"GIO cu the (UTC+7)")
group(lambda s:s['confl'],"HOP LUU (cluster_count)")
group(absbk,"DELTA vs HUONG (absorption)")
group(trendal,"TREND-align (proxy close vs 480 nen)")
group(vwapal,"VWAP-align")
group(vsabk,"VSA (vratio) muc")
group(lambda s:s['climax'],"CLIMAX (vratio>=2.2)")
group(scenbk,"KICH BAN (scen)")
group(lambda s:s['side'],"HUONG")
group(lambda s:s['kind'],"LOAI VUNG (zone kind)")

# ---------- 5. CUT LIFT (May-Jul): bo subset -> giu con lai ----------
print("\n"+"="*70);print("CUT-LIFT (May-Jul): giu-set sau khi BO subset | + per-month robustness cua PHAN BO");print("="*70)
cuts={
 "dead [02,08)":            lambda s:dead(s),
 "phien MY(19-02)":         lambda s:hourbk(s['lhour'])=='MY(19-02)',
 "phien AU(14-19)":         lambda s:hourbk(s['lhour'])=='AU(14-19)',
 "confl==2 (giu>=3)":       lambda s:s['confl']<3,
 "MOMENTUM (giu absorb+nodelta)":lambda s:absbk(s)=='MOMENTUM(cung)',
 "US-fade hours [19,01)":   lambda s:s['lhour']>=19 or s['lhour']<1,
 "non-climax (vratio<2.2)": lambda s:not s['climax'],
 "1 pha&hoi break-retest":  lambda s:s['scen'].startswith('1'),
 "nguoc-trend":             lambda s:trendal(s)=='nguoc',
 "nguoc-vwap":              lambda s:vwapal(s)=='nguoc-vwap',
 "VSA<1.5":                 lambda s:s['vsa']<1.5,
 "climax vratio>=2.2":      lambda s:s['climax'],
 "scen 2 cham&dao (giu KB1)":lambda s:s['scen'].startswith('2'),
 "SHORT (giu LONG)":        lambda s:s['side']=='SHORT',
 "LONG (giu SHORT)":        lambda s:s['side']=='LONG',
}
print(f"  {'BO subset':<32}{'keep_n':>7}{'WR':>5}{'EV':>7}{'totR':>7}{'dR':>7}")
res=[]
for nm,pred in cuts.items():
    keep=[s for s in S3 if not pred(s)]
    n,wr,ev,tot=stats(keep)
    res.append((nm,pred,n,wr,ev,tot,tot-tot3))
for nm,pred,n,wr,ev,tot,dR in sorted(res,key=lambda x:-x[6]):
    rem=[s for s in S3 if pred(s)];nr=len(rem)
    flag=' <<keep_n_nho' if n<15 else ''
    # per-month EV cua subset BO (robustness: xau deu moi thang?)
    pm=" ".join(f"{m[5:]}:{stats([s for s in rem if s['ym']==m])[2]:+.1f}({len([s for s in rem if s['ym']==m])})" for m in M3)
    print(f"  {nm:<32}{n:>7}{wr*100:>4.0f}%{ev:>+7.2f}{tot:>+7.1f}{dR:>+7.1f}{flag}")
    print(f"      BO n={nr} EV{stats(rem)[2]:+.2f} | per-thang EV(n) subset-bo: {pm}")
print(f"\n  (baseline giu HET May-Jul: n={n3} WR {wr3*100:.0f}% EV {ev3:+.3f} tong {tot3:+.1f}R)")

# ---------- 6. COMBO 2 cut manh nhat (US-fade + absorption) per-month ----------
print("\n"+"="*70);print("COMBO: BO US-fade[19,01) + BO momentum (giu absorb/no-delta) — per-month");print("="*70)
usfade=lambda s:s['lhour']>=19 or s['lhour']<1
mom=lambda s:absbk(s)=='MOMENTUM(cung)'
print(f"  {'thang':<9}{'base n/WR/EV/R':>26}{'->':>4}{'combo n/WR/EV/R':>26}")
for m in M3+['TONG']:
    bset=[s for s in S3 if (m=='TONG' or s['ym']==m)]
    cset=[s for s in bset if not usfade(s) and not mom(s)]
    nb,wb,eb,tb=stats(bset);nc,wc,ec,tc=stats(cset)
    print(f"  {m:<9}{nb:>6}{wb*100:>4.0f}%{eb:>+7.2f}{tb:>+7.1f}{'':>4}{nc:>8}{wc*100:>4.0f}%{ec:>+7.2f}{tc:>+7.1f}")
