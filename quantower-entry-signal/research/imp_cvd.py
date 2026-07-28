#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAI TIEN #2 — CUMULATIVE DELTA (CVD) + PHAN KY CVD.
Gia thuyet:
  - Pha&hoi (scen '1', momentum): CVD THUAN huong (long: CVD doc len) -> dong lenh xac nhan -> tot hon?
  - Cham&dao (scen '2', reversal): PHAN KY (gia day/dinh moi nhung CVD KHONG) -> can kiet -> tot hon?
Feed ghep 6 thang (delta THAT). Baseline can vuot (RR1.5, confl>=2):
  n=137 WR45% phang +15.5R  nhoi>=3 +39.5R  MDD~19R.
KHONG nhin tuong lai: CVD + dinh/day chi tinh toi bar s['i'] (bao gom).
"""
import fp_merged as M, entry_dxfeed as E
import statistics as st
from collections import Counter
TICK=E.TICK

B=M.load_merged()
E.VOLFLOOR_AUTO=E.calc_volfloor(B); pool=E.build_zones(B)
E.USE_DELTA=False
C=E.prep(dict(E.make(MIN_CONFL=2)))
S=E.dedup(E.run(B,pool,C),pool,C); S.sort(key=lambda s:s['i'])

def sim_rr(s,rr=1.5):
    e=s['entry'];sl=s['sl'];sd=s['side'];risk=s['risk_t']*TICK
    tp=e+rr*risk if sd=='LONG' else e-rr*risk
    for j in range(s['i']+1,len(B)):
        b=B[j]
        if (b['lo']<=sl if sd=='LONG' else b['hi']>=sl): return -1.0
        if (b['hi']>=tp if sd=='LONG' else b['lo']<=tp): return rr
    return None
for s in S: s['r']=sim_rr(s)
S=[s for s in S if s['r'] is not None]

# ---------------------------------------------------------------------------
# CVD cong don theo PHIEN. Reset khi since_gap==0 (gap>30 phut giua 2 bar).
# Xu ly bar thieu delta: "bo qua" (khong cong) == "coi delta=0" cho TONG cong don
#   (dong nhat ve toan hoc: skip == +0). Ta dung skip; CVD carry-forward qua bar thieu.
# ndelta_since = so bar co delta ke tu dau phien (do do TIN CAY cua CVD tai bar do).
# ---------------------------------------------------------------------------
CVD=[0.0]*len(B); sess_start=[0]*len(B); ndelta_since=[0]*len(B)
cvd=0.0; ss=0; nd=0
for i,b in enumerate(B):
    if b['since_gap']==0:
        cvd=0.0; ss=i; nd=0
    if b['has_delta']:
        cvd+=b['delta']; nd+=1
    CVD[i]=cvd; sess_start[i]=ss; ndelta_since[i]=nd

MINCTX=3   # can toi thieu 3 bar co delta trong phien de CVD co nghia

def slope(i,k):
    j=max(sess_start[i], i-k)
    return CVD[i]-CVD[j]

def cvd_thuan(s,k,thr):
    """scen '1': CVD doc THUAN huong lenh. True=giu, False=bo, None=thieu ngu canh delta."""
    i=s['i']
    if ndelta_since[i]<MINCTX or i-sess_start[i]<3: return None
    sl=slope(i,k)
    return (sl>thr) if s['side']=='LONG' else (sl<-thr)

def diverg(s,W):
    """scen '2': PHAN KY. LONG: gia day moi trong cua so nhung CVD KHONG day moi.
    True=co phan ky (giu), False=khong phan ky (bo), None=thieu ngu canh."""
    i=s['i']; wsb=max(sess_start[i], i-W)
    win=[j for j in range(wsb,i)]
    if len(win)<4 or ndelta_since[i]<MINCTX: return None
    if s['side']=='LONG':
        price_new_low = B[i]['lo'] <= min(B[j]['lo'] for j in win)
        cvd_not_low   = CVD[i] > min(CVD[j] for j in win)   # CVD cao hon day cu -> phan ky
        return price_new_low and cvd_not_low
    else:
        price_new_high= B[i]['hi'] >= max(B[j]['hi'] for j in win)
        cvd_not_high  = CVD[i] < max(CVD[j] for j in win)
        return price_new_high and cvd_not_high

# ---------------------------------------------------------------------------
def dd(seq):
    eq=0.0;pk=0.0;m=0.0
    for r in seq: eq+=r;pk=max(pk,eq);m=max(m,pk-eq)
    return m
def met(sigs):
    sigs=sorted(sigs,key=lambda s:s['i'])
    n=len(sigs)
    if n==0: return dict(n=0,wr=0,flat=0.0,nhoi=0.0,mdd=0.0)
    wr=sum(s['r']>0 for s in sigs)/n
    flat=[s['r'] for s in sigs]
    nhoi=[(3 if s['confl']>=3 else 1)*s['r'] for s in sigs]
    return dict(n=n,wr=wr,flat=sum(flat),nhoi=sum(nhoi),mdd=dd(nhoi),mddflat=dd(flat))
def prow(name,sigs,base=None):
    m=met(sigs)
    tag=""
    if base is not None:
        tag=" | d nhoi %+.1f"%(m['nhoi']-base)
    print("  %-42s n=%3d WR%3.0f%% phang%+6.1f nhoi>=3%+6.1f MDD%4.0f%s"%(
        name,m['n'],m['wr']*100,m['flat'],m['nhoi'],m['mdd'],tag))
    return m
def bymonth(sigs):
    for ym in sorted(set(s['ym'] for s in sigs)):
        g=[s for s in sigs if s['ym']==ym]; m=met(g)
        print("      %-8s n=%2d WR%3.0f%% phang%+5.1f nhoi%+6.1f"%(ym,m['n'],m['wr']*100,m['flat'],m['nhoi']))

# ---------------------------------------------------------------------------
S1=[s for s in S if s['scen'].startswith('1')]   # pha&hoi (momentum)
S2=[s for s in S if s['scen'].startswith('2')]    # cham&dao (reversal)
BASE_NHOI=met(S)['nhoi']

print("\n"+"="*84)
print("A. BASELINE (tap khop de bai)")
print("="*84)
b_all=prow("TAT CA (baseline)",S)
b_s1 =prow("  chi scen'1' pha&hoi (momentum)",S1)
b_s2 =prow("  chi scen'2' cham&dao (reversal)",S2)
hd=sum(B[s['i']]['has_delta'] for s in S)
print("  phu delta tai bar-vao: %d/%d (%.0f%%) | scen1 %d/%d | scen2 %d/%d"%(
    hd,len(S),100*hd/len(S),
    sum(B[s['i']]['has_delta'] for s in S1),len(S1),
    sum(B[s['i']]['has_delta'] for s in S2),len(S2)))
print("  Ghi chu skip-vs-zero: CVD cong-don giong HET nhau (skip bar thieu == cong 0). Da xac minh.")

# helpers ap loc theo scen, phan cua con lai
def apply_scen(target, decide, keep_none):
    """Giu tat ca signal KHONG thuoc 'target' scen. Voi target: decide(s) True giu/False bo/None.
       keep_none=True -> giu ca None (kieu B); False -> bo None (kieu A)."""
    out=[]; dropped=[]; nod=[]
    for s in S:
        in_target = (s in target)
        if not in_target:
            out.append(s); continue
        d=decide(s)
        if d is True: out.append(s)
        elif d is False: dropped.append(s)
        else:
            nod.append(s)
            if keep_none: out.append(s)
    return out,dropped,nod

def subset_only(target, decide, keep_none):
    """Chi lay signal target sau loc (de soi tin hieu thuan tuy)."""
    out=[];dr=[];nod=[]
    for s in target:
        d=decide(s)
        if d is True: out.append(s)
        elif d is False: dr.append(s)
        else:
            nod.append(s)
            if keep_none: out.append(s)
    return out,dr,nod

print("\n"+"="*84)
print("B. MOMENTUM — scen'1' can CVD THUAN huong (long: slope>thr, short: slope<-thr)")
print("   [scen'2' giu nguyen]. So sanh subset scen'1' + toan danh muc.")
print("="*84)
best_mom=None
for k in (5,10,15):
    for thr in (0,20,50):
        for keep_none,knm in ((False,'A-bo'),(True,'B-giu')):
            dec=lambda s,k=k,thr=thr: cvd_thuan(s,k,thr)
            sub,dr,nod=subset_only(S1,dec,keep_none)
            full,fdr,fnod=apply_scen(S1,dec,keep_none)
            ms=met(sub); mf=met(full)
            print("  k=%2d thr=%2d %s | scen'1' sub: n=%2d WR%3.0f%% phang%+5.1f nhoi%+5.1f (bo%d,nodelta%d) || FULL n=%3d WR%3.0f%% nhoi%+6.1f MDD%3.0f"%(
                k,thr,knm,ms['n'],ms['wr']*100,ms['flat'],ms['nhoi'],len(dr),len(nod),
                mf['n'],mf['wr']*100,mf['nhoi'],mf['mdd']))
            cand=(mf['nhoi'],mf['n'],k,thr,keep_none,full,sub,dr)
            if best_mom is None or mf['nhoi']>best_mom[0]: best_mom=cand

print("\n"+"="*84)
print("C. REVERSAL — scen'2' can PHAN KY CVD (gia dinh/day moi, CVD khong theo)")
print("   [scen'1' giu nguyen]. So sanh subset scen'2' + toan danh muc.")
print("="*84)
best_rev=None
for W in (10,20,30):
    for keep_none,knm in ((False,'A-bo'),(True,'B-giu')):
        dec=lambda s,W=W: diverg(s,W)
        sub,dr,nod=subset_only(S2,dec,keep_none)
        full,fdr,fnod=apply_scen(S2,dec,keep_none)
        ms=met(sub); mf=met(full)
        print("  W=%2d %s | scen'2' sub: n=%2d WR%3.0f%% phang%+5.1f nhoi%+5.1f (bo%d,nodelta%d) || FULL n=%3d WR%3.0f%% nhoi%+6.1f MDD%3.0f"%(
            W,knm,ms['n'],ms['wr']*100,ms['flat'],ms['nhoi'],len(dr),len(nod),
            mf['n'],mf['wr']*100,mf['nhoi'],mf['mdd']))
        cand=(mf['nhoi'],mf['n'],W,keep_none,full,sub,dr)
        if best_rev is None or mf['nhoi']>best_rev[0]: best_rev=cand

# --- doi chung: cac tin hieu bi BO co WR thap that khong? ---
print("\n"+"="*84)
print("D. SOI GIA TRI LOC — WR cua nhom BI LOAI (neu thap => loc dung 'lenh xau')")
print("="*84)
def wrof(g): return (sum(x['r']>0 for x in g)/len(g)*100) if g else 0.0
# momentum: bo cac scen1 KHONG thuan (thr=0,k=10)
mdrop=[s for s in S1 if cvd_thuan(s,10,0) is False]
mkeep=[s for s in S1 if cvd_thuan(s,10,0) is True]
print("  Momentum k10 thr0: GIU(thuan) n=%d WR%.0f%% nhoi%+.1f | BO(nguoc) n=%d WR%.0f%% nhoi%+.1f"%(
    len(mkeep),wrof(mkeep),met(mkeep)['nhoi'],len(mdrop),wrof(mdrop),met(mdrop)['nhoi']))
# reversal: bo cac scen2 KHONG phan ky (W=20)
rdrop=[s for s in S2 if diverg(s,20) is False]
rkeep=[s for s in S2 if diverg(s,20) is True]
print("  Reversal W20: GIU(phan ky) n=%d WR%.0f%% nhoi%+.1f | BO(khong pky) n=%d WR%.0f%% nhoi%+.1f"%(
    len(rkeep),wrof(rkeep),met(rkeep)['nhoi'],len(rdrop),wrof(rdrop),met(rdrop)['nhoi']))
# doi chung NGUOC: scen2 neu doi lai (CVD THUAN huong dao) thi sao? (long reversal + CVD da doc len)
def rev_cvdconf(s,k=10):  # reversal ma CVD da xac nhan dao chieu (long: slope>0)
    i=s['i']
    if ndelta_since[i]<MINCTX or i-sess_start[i]<3: return None
    sl=slope(i,k)
    return (sl>0) if s['side']=='LONG' else (sl<0)
r2keep=[s for s in S2 if rev_cvdconf(s) is True]
r2drop=[s for s in S2 if rev_cvdconf(s) is False]
print("  (doi chung) Reversal CVD-THUAN-dao k10: GIU n=%d WR%.0f%% nhoi%+.1f | BO n=%d WR%.0f%% nhoi%+.1f"%(
    len(r2keep),wrof(r2keep),met(r2keep)['nhoi'],len(r2drop),wrof(r2drop),met(r2drop)['nhoi']))

print("\n"+"="*84)
print("E. KET HOP TOT NHAT (scen'1' CVD-thuan + scen'2' phan ky) — cac to hop")
print("="*84)
def combo(k,thr,W,keep_none):
    out=[]
    for s in S:
        if s in S1: d=cvd_thuan(s,k,thr)
        else: d=diverg(s,W)
        if d is True: out.append(s)
        elif d is None and keep_none: out.append(s)
    return out
best_combo=None
for k,thr in ((10,0),(10,20),(5,0),(15,0)):
    for W in (10,20,30):
        for keep_none,knm in ((False,'A-bo'),(True,'B-giu')):
            g=combo(k,thr,W,keep_none); m=met(g)
            print("  k=%2d thr=%2d W=%2d %s -> n=%3d WR%3.0f%% phang%+6.1f nhoi>=3%+6.1f MDD%3.0f%s"%(
                k,thr,W,knm,m['n'],m['wr']*100,m['flat'],m['nhoi'],m['mdd'],
                "  *vuot" if m['nhoi']>BASE_NHOI else ""))
            if best_combo is None or m['nhoi']>best_combo[0]: best_combo=(m['nhoi'],k,thr,W,keep_none,g,m)

print("\n"+"="*84)
print("F. CAU HINH TOT NHAT + theo thang")
print("="*84)
print("BASELINE nhoi>=3 = %+.1fR (phang %+.1fR, MDD %.0f)"%(BASE_NHOI,met(S)['flat'],met(S)['mdd']))
_,k,thr,W,kn,g,m=best_combo
print("\nKET HOP tot nhat: k=%d thr=%d W=%d %s"%(k,thr,W,'giu-nodelta' if kn else 'bo-nodelta'))
prow("  ket hop",g,BASE_NHOI); bymonth(g)
print("\nMOMENTUM tot nhat (chi loc scen1, scen2 nguyen):")
prow("  momentum best",best_mom[5],BASE_NHOI)
print("\nREVERSAL tot nhat (chi loc scen2, scen1 nguyen):")
prow("  reversal best",best_rev[4],BASE_NHOI)
print("\nfile: /home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/imp_cvd.py")
