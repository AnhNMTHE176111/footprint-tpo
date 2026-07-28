#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IMP ABSORPTION TAI MUC CUC TRI (PER-LEVEL) — tin hieu MUC-GIA, khac delta-trung-binh-ca-nen.
Gia thuyet: tai muc CUC TRI cua nhip cham vung (LONG: day nhip; SHORT: dinh nhip), co khoi luong
BAN chu dong (bid) lon + delta AM manh nhung gia KHONG thung tiep -> ban bi hap thu -> dao len
(SHORT doi xung: ask lon, delta duong tai dinh, dong cua thap).
So voi BASELINE (RR1.5, confl>=2, 6 thang) va so voi DELTA-TRUNG-BINH-CA-NEN nguoc phia (WR~52%).

Chi dung bar <= s['i'] (khong nhin tuong lai). Bar thieu delta (has_delta=False): bao ca 2 cach
(LOAI / GIU). Nguong TUONG DOI (boi so trung vi vol/muc), khong so tuyet doi."""
import fp_merged as M, entry_dxfeed as E
import statistics as st
from collections import Counter
TICK=E.TICK

B=M.load_merged()
E.VOLFLOOR_AUTO=E.calc_volfloor(B); pool=E.build_zones(B)
E.USE_DELTA=False
C=E.prep(dict(E.make(MIN_CONFL=2)))
S=E.dedup(E.run(B,pool,C), pool, C); S.sort(key=lambda s:s['i'])
MONTHS=tuple(sorted(set(b['ym'] for b in B)))

def sim_rr(s,rr=1.5):
    e=s['entry'];sl=s['sl'];sd=s['side'];risk=s['risk_t']*TICK
    tp=e+rr*risk if sd=='LONG' else e-rr*risk
    for j in range(s['i']+1,len(B)):
        b=B[j]
        if (b['lo']<=sl if sd=='LONG' else b['hi']>=sl): return -1.0
        if (b['hi']>=tp if sd=='LONG' else b['lo']<=tp): return rr
    return None

def mdd(seq):
    eq=pk=m=0.0
    for r in seq: eq+=r; pk=max(pk,eq); m=max(m,pk-eq)
    return m

# ---- gan R + dac trung absorption cho moi signal ----
def features(s, band_t):
    """Gom levels cua nhip cham vung (nen vao + <=2 nen truoc, chi bar co delta) tai vung cuc tri.
    band_t = so tick tinh tu cuc tri. Tra dict dac trung, hoac None neu khong co delta trong nhip."""
    idxs=[k for k in range(max(0,s['i']-2),s['i']+1) if B[k]['has_delta']]
    if not idxs: return None
    bars=[B[k] for k in idxs]
    allvol=[d['vol'] for b in bars for d in b['levels'].values()]
    if not allvol: return None
    med=st.median(allvol)
    win_tot=sum(allvol)
    if s['side']=='LONG':
        ext=min(b['lo'] for b in bars); lim=ext+band_t*TICK
        insel=lambda p: p<=lim+1e-9
    else:
        ext=max(b['hi'] for b in bars); lim=ext-band_t*TICK
        insel=lambda p: p>=lim-1e-9
    ev=eb=ea=ed=0.0; mx=0.0
    for b in bars:
        for p,d in b['levels'].items():
            if insel(p):
                ev+=d['vol']; eb+=d['bid']; ea+=d['ask']; ed+=d['delta']; mx=max(mx,d['vol'])
    if ev<=0: return None
    # opp = phia AGGRESSION nguoc voi huong lenh (can duoc HAP THU)
    opp = eb if s['side']=='LONG' else ea      # LONG can BAN(bid) bi hap thu; SHORT can MUA(ask)
    dratio = ed/ev                              # delta ratio tai cuc tri
    return dict(ext_vol=ev, ext_bid=eb, ext_ask=ea, ext_delta=ed, ext_max=mx,
                opp=opp, dratio=dratio, med=med, win_tot=win_tot,
                opp_ratio=opp/ev, conc_frac=ev/win_tot, mx_med=(mx/med if med>0 else 0),
                opp_med=(opp/med if med>0 else 0))

for s in S:
    s['r']=sim_rr(s,1.5)
    eb=B[s['i']]
    s['has_delta']=eb['has_delta']; s['cpos']=eb['cpos']
    s['ddom']=eb['ddom']            # delta trung binh NEN VAO
    # delta trung binh nhip 3 nen (de so sanh "delta-trung-binh")
    win=[B[k] for k in range(max(0,s['i']-2),s['i']+1) if B[k]['has_delta']]
    tv=sum(x['v_fp'] for x in win)
    s['ddom_win']=(sum(x['delta'] for x in win)/tv) if win and tv>0 else None
    s['f2']=features(s,2); s['f3']=features(s,3); s['f5']=features(s,5)
S=[s for s in S if s['r'] is not None]

def block(name, keep, cnt_dropped=True):
    """keep(s)-> True giu / False bo / None khong-co-delta. In 1 dong metrics."""
    kept=[s for s in S if keep(s) is True]
    nod =[s for s in S if keep(s) is None]
    ndrop=[s for s in S if keep(s) is False]
    if not kept:
        print(f"  {name:<46} (rong)  khong-delta={len(nod)}"); return None
    wr=sum(s['r']>0 for s in kept)/len(kept)
    flat=[s['r'] for s in kept]
    nhoi=[(3 if s['confl']>=3 else 1)*s['r'] for s in kept]
    tag=" <n20" if len(kept)<20 else ""
    print(f"  {name:<46} n={len(kept):>3} WR{wr*100:>3.0f}% phang{sum(flat):>+6.1f} nhoi>=3{sum(nhoi):>+6.1f} MDD{mdd(nhoi):>4.0f}  (bo{len(ndrop)},noDelta{len(nod)}){tag}")
    return dict(n=len(kept),wr=wr,flat=sum(flat),nhoi=sum(nhoi),mdd=mdd(nhoi))

# ===================== BASELINE =====================
wr0=sum(s['r']>0 for s in S)/len(S)
flat0=[s['r'] for s in S]; nhoi0=[(3 if s['confl']>=3 else 1)*s['r'] for s in S]
print(f"\n================ BASELINE (confl>=2, RR1.5, 6 thang) ================")
print(f"  n={len(S)}  WR{wr0*100:.0f}%  phang{sum(flat0):+.1f}R  nhoi>=3 {sum(nhoi0):+.1f}R  MDD{mdd(nhoi0):.0f}  | co-delta {sum(s['has_delta'] for s in S)}/{len(S)}")
print("  theo thang (phang|n):",end="")
for m in MONTHS:
    mm=[s for s in S if s['ym']==m]
    if mm: print(f"  {m[-2:]}={sum(s['r'] for s in mm):+.0f}(n{len(mm)})",end="")
print()

# ===================== THAM CHIEU: DELTA-TRUNG-BINH-CA-NEN nguoc phia =====================
print(f"\n================ THAM CHIEU: DELTA-TRUNG-BINH (ca nen) nguoc phia ================")
def opp_avg(s,use_win,thr):
    d=s['ddom_win'] if use_win else s['ddom']
    if d is None: return None
    return (d<=-thr) if s['side']=='LONG' else (d>=thr)
print("  (LOAI bar khong delta)")
for thr in (0.0,0.15,0.25):
    block(f"nen-vao ddom nguoc>={thr}", lambda s,t=thr: opp_avg(s,False,t))
for thr in (0.0,0.15,0.25):
    block(f"nhip3nen ddom nguoc>={thr}", lambda s,t=thr: opp_avg(s,True,t))

# ===================== ABSORPTION PER-LEVEL TAI CUC TRI =====================
def has_f(s,bt): return s[f'f{bt}'] is not None
def F(s,bt): return s[f'f{bt}']

print(f"\n================ ABSORPTION PER-LEVEL TAI CUC TRI (LOAI bar khong delta) ================")

# --- V1: delta AM/DUONG nguoc phia tai cuc tri (dratio) ---
print("--- V1: dratio tai cuc tri nguoc phia lenh (LONG day delta<=-thr / SHORT dinh >=+thr) ---")
def v1(s,bt,thr):
    if not has_f(s,bt): return None
    d=F(s,bt)['dratio']
    return (d<=-thr) if s['side']=='LONG' else (d>=thr)
res={}
for bt in (2,3,5):
    for thr in (0.0,0.2,0.35,0.5):
        res[f'V1 band{bt}t dratio-nguoc>={thr}']=block(f"band{bt}t dratio nguoc>={thr}", lambda s,b=bt,t=thr: v1(s,b,t))

# --- V2: khoi luong PHE NGUOC (opp) TAP TRUNG tai cuc tri (boi so trung vi) + dratio nguoc ---
print("--- V2: opp-aggression tap trung tai cuc tri (opp>=k*trung vi) + dratio nguoc<0 ---")
def v2(s,bt,k):
    if not has_f(s,bt): return None
    f=F(s,bt)
    conc = f['opp_med']>=k
    dopp = (f['dratio']<0) if s['side']=='LONG' else (f['dratio']>0)
    return bool(conc and dopp)
for bt in (2,3,5):
    for k in (2.0,3.0,4.0):
        res[f'V2 band{bt}t opp>={k}xmed +dratioNguoc']=block(f"band{bt}t opp>={k}xmed +dNguoc", lambda s,b=bt,kk=k: v2(s,b,kk))

# --- V3: V1 (dratio nguoc) + XAC NHAN cpos bat lai (LONG cpos>=0.5 / SHORT cpos<=0.5) ---
print("--- V3: dratio nguoc>=thr + cpos xac nhan bat lai (LONG cpos>=0.5 / SHORT<=0.5) ---")
def v3(s,bt,thr):
    if not has_f(s,bt): return None
    d=F(s,bt)['dratio']
    dopp=(d<=-thr) if s['side']=='LONG' else (d>=thr)
    cconf=(s['cpos']>=0.5) if s['side']=='LONG' else (s['cpos']<=0.5)
    return bool(dopp and cconf)
for bt in (2,3):
    for thr in (0.0,0.2,0.35):
        res[f'V3 band{bt}t dNguoc>={thr}+cpos']=block(f"band{bt}t dNguoc>={thr}+cpos", lambda s,b=bt,t=thr: v3(s,b,t))

# --- V4: TAP TRUNG KHOI LUONG tai cuc tri (conc_frac hoac mx_med) — KHONG dung dau delta ---
print("--- V4: chi TAP TRUNG volume tai cuc tri (KHONG xet delta) — de xem delta co them gia tri ---")
def v4(s,bt,f):
    if not has_f(s,bt): return None
    return F(s,bt)['conc_frac']>=f
for bt in (2,3):
    for f in (0.3,0.45,0.6):
        res[f'V4 band{bt}t conc_frac>={f}']=block(f"band{bt}t conc_frac>={f} (no-delta)", lambda s,b=bt,ff=f: v4(s,b,ff))

# --- V5: opp tap trung + dratio nguoc + cpos (combo chat nhat) ---
print("--- V5: opp>=k*med + dratio nguoc + cpos xac nhan (combo) ---")
def v5(s,bt,k):
    if not has_f(s,bt): return None
    f=F(s,bt)
    conc=f['opp_med']>=k
    dopp=(f['dratio']<0) if s['side']=='LONG' else (f['dratio']>0)
    cconf=(s['cpos']>=0.5) if s['side']=='LONG' else (s['cpos']<=0.5)
    return bool(conc and dopp and cconf)
for bt in (2,3):
    for k in (2.0,3.0):
        res[f'V5 band{bt}t opp>={k}+d+cpos']=block(f"band{bt}t opp>={k}xmed+d+cpos", lambda s,b=bt,kk=k: v5(s,b,kk))

# ===================== GIU bar khong-delta (kieu B) cho cau hinh tot nhat =====================
print(f"\n================ GIU bar khong-delta (cau hinh V1 dratio nguoc>=0, vai band) ================")
def v1_keep(s,bt,thr):
    if not has_f(s,bt): return True    # khong co delta -> GIU
    d=F(s,bt)['dratio']
    return (d<=-thr) if s['side']=='LONG' else (d>=thr)
for bt in (2,3):
    for thr in (0.0,0.2):
        block(f"band{bt}t dNguoc>={thr} (GIU no-delta)", lambda s,b=bt,t=thr: v1_keep(s,b,t))

# ===================== TONG KET: top cau hinh vs baseline =====================
print(f"\n================ TOP cau hinh (LOAI no-delta) theo R phang, n>=20 ================")
base=dict(n=len(S),flat=sum(flat0),nhoi=sum(nhoi0))
rows=[(k,v) for k,v in res.items() if v and v['n']>=20]
rows.sort(key=lambda kv:-kv[1]['flat'])
print(f"  {'cau hinh':<40} {'n':>3} {'WR':>4} {'phang':>7} {'nhoi':>7} {'MDD':>4}")
for k,v in rows[:12]:
    print(f"  {k:<40} {v['n']:>3} {v['wr']*100:>3.0f}% {v['flat']:>+6.1f} {v['nhoi']:>+6.1f} {v['mdd']:>4.0f}")
print(f"\n  BASELINE: n={base['n']} phang{base['flat']:+.1f} nhoi{base['nhoi']:+.1f}")

# ===================== PHU: co edge that su khong? (co-delta baseline + complement) =====================
print(f"\n================ KIEM EDGE: co-delta baseline vs cac lat cat ================")
cd=[s for s in S if s['has_delta']]
wrcd=sum(s['r']>0 for s in cd)/len(cd)
print(f"  co-delta baseline (chi 98 nen co delta): n={len(cd)} WR{wrcd*100:.0f}% phang{sum(s['r'] for s in cd):+.1f} nhoi{sum((3 if s['confl']>=3 else 1)*s['r'] for s in cd):+.1f}")
def edge(name, cond):
    g=[s for s in cd if cond(s)]; gw=[s for s in cd if not cond(s)]
    if not g or not gw: print(f"  {name:<40} (khong tach duoc)"); return
    print(f"  {name:<40} GIU n={len(g):>3} WR{sum(s['r']>0 for s in g)/len(g)*100:>3.0f}% R{sum(s['r'] for s in g):>+5.1f} || BO n={len(gw):>3} WR{sum(s['r']>0 for s in gw)/len(gw)*100:>3.0f}% R{sum(s['r'] for s in gw):>+5.1f}")
edge("bar-avg ddom nguoc phia (nen vao)", lambda s:(s['ddom']<=0) if s['side']=='LONG' else (s['ddom']>=0))
edge("extreme band5t dratio nguoc phia", lambda s:(s['f5'] and ((s['f5']['dratio']<=0) if s['side']=='LONG' else (s['f5']['dratio']>=0))))
edge("extreme band2t dratio nguoc phia", lambda s:(s['f2'] and ((s['f2']['dratio']<=0) if s['side']=='LONG' else (s['f2']['dratio']>=0))))
edge("extreme band2t opp>=3xmed +dNguoc", lambda s:(s['f2'] and s['f2']['opp_med']>=3 and ((s['f2']['dratio']<0) if s['side']=='LONG' else (s['f2']['dratio']>0))))
