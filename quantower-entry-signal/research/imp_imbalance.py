#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAI TIEN — IMBALANCE / STACKED IMBALANCE tung MUC GIA (footprint diagonal).
Dinh nghia diagonal imbalance tren b['levels'] (bid/ask tung muc gia, buoc 0.1):
  BUY imbalance tai p : ask[p] ap dao bid[p-1tick]   (mua nhac chao ap dao ban duoi)
  SELL imbalance tai p: bid[p] ap dao ask[p+1tick]   (ban dap gia ap dao mua tren)
Nguong ty le RATIO in {2,3,4}; bo muc volume qua nho bang nguong TUONG DOI
  (vmin = max(MINC, VMULT * trung_vi_vol_muc cua cua so)).
Stacked = so muc LIEN TIEP (grid 0.1) cung chieu imbalance (run>=2, >=3).
Tong hop tren CUA SO W nen (W=1 chi nen vao; W=3 gom nhip cham vung) — KHONG nhin bar tuong lai.
2 gia thuyet:
  (a) imbalance THUAN huong lenh (long<->buy) la diem cong?
  (b) imbalance NGUOC huong (bi hap thu, giong absorption) la diem cong? (long ma co sell-imb nhung gia giu)
So voi BASELINE (feed ghep 6 thang): phang +15.5R, nhoi>=3 +39.5R, WR45%, n=137 (co delta 98).
Xu ly nen khong-delta 2 kieu: (A) LOAI, (B) GIU nguyen. Bao ca hai."""
import fp_merged as M
import entry_dxfeed as E
import statistics as st
from collections import Counter
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

# ---- signal set (nen, delta-free gate) ----
E.USE_DELTA=False
C=E.prep(dict(E.make(MIN_CONFL=2)))
S=[s for s in E.dedup(E.run(B,pool,C),pool,C)]
S.sort(key=lambda s:s['i'])
for s in S:
    s['r']=sim_rr(s,1.5)
    s['has_delta']=B[s['i']]['has_delta']
S=[s for s in S if s['r'] is not None]

def agg_levels(s,W):
    """Gom levels bid/ask cua W nen cuoi (den nen vao i). None neu khong nen nao co delta."""
    ks=[k for k in range(max(0,s['i']-W+1),s['i']+1) if B[k]['has_delta']]
    if not ks:return None
    agg={}
    for k in ks:
        for p,lv in B[k]['levels'].items():
            a=agg.get(p)
            if a is None:a=agg[p]=dict(bid=0.0,ask=0.0,vol=0.0)
            a['bid']+=lv['bid'];a['ask']+=lv['ask'];a['vol']+=lv['vol']
    return agg

def imb_flags(agg,ratio,vmult,minc=3):
    """Tra ve set gia co BUY-imb, SELL-imb + do dai run lien tiep dai nhat moi chieu."""
    prices=sorted(agg)
    if not prices:return None
    med=st.median([agg[p]['vol'] for p in prices])
    vmin=max(minc,vmult*med)
    def gv(p,key):
        a=agg.get(round(p,1));return a[key] if a else 0.0
    buy=set();sell=set()
    for p in prices:
        a=agg[p]['ask'];b_below=gv(p-TICK,'bid')
        if a>=vmin and a>=ratio*max(b_below,1):buy.add(round(p,1))
        b=agg[p]['bid'];a_above=gv(p+TICK,'ask')
        if b>=vmin and b>=ratio*max(a_above,1):sell.add(round(p,1))
    def maxrun(fs):
        if not fs:return 0
        best=0
        for p in fs:
            if round(p-TICK,1) in fs:continue      # khong phai dau run
            L=0;q=p
            while round(q,1) in fs:L+=1;q=round(q+TICK,1)
            best=max(best,L)
        return best
    return dict(nbuy=len(buy),nsell=len(sell),run_buy=maxrun(buy),run_sell=maxrun(sell))

def features(s,W,ratio,vmult):
    """Gan co imbalance THEO HUONG LENH. Tra ve dict hoac None (khong delta)."""
    agg=agg_levels(s,W)
    if agg is None:return None
    f=imb_flags(agg,ratio,vmult)
    if f is None:return None
    if s['side']=='LONG':
        withc=f['nbuy'];withrun=f['run_buy'];oppc=f['nsell'];opprun=f['run_sell']
    else:
        withc=f['nsell'];withrun=f['run_sell'];oppc=f['nbuy'];opprun=f['run_buy']
    return dict(withc=withc,withrun=withrun,oppc=oppc,opprun=opprun)

def report(name,S,keepfn):
    """keepfn(s)->True giu / False bo / None khong-delta. In 2 kieu no-delta."""
    withd=[s for s in S if s['has_delta']]
    def line(pool_,tag):
        kept=[s for s in pool_ if keepfn(s) is True]
        if len(kept)==0:return f"{tag} n=  0 (rong)"
        wr=sum(x['r']>0 for x in kept)/len(kept)
        flat=[x['r'] for x in kept];nhoi=[(3 if x['confl']>=3 else 1)*x['r'] for x in kept]
        return (f"{tag} n={len(kept):>3} WR{wr*100:>3.0f}% phang{sum(flat):>+6.1f} "
                f"nhoi>={sum(nhoi):>+6.1f} MDD{dd(nhoi):>4.0f}")
    # Kieu A: chi tren nen co delta (keepfn None se thanh khong-True -> bi loai tu nhien vi withd)
    a=line(withd,"A(loai no-delta):")
    # Kieu B: giu no-delta (keepfn None -> ep True)
    keepB=lambda s:(True if keepfn(s) is None else keepfn(s))
    b=line(S,"B(giu no-delta): ")
    print(f"  {name:<34} | {a}   || {b}")

# ---- BASELINE ----
wr=sum(s['r']>0 for s in S)/len(S)
flat=[s['r'] for s in S];nhoi=[(3 if s['confl']>=3 else 1)*s['r'] for s in S]
print(f"\n{'='*118}")
print(f"BASELINE (confl>=2, nen): n={len(S)} WR{wr*100:.0f}% phang{sum(flat):+.1f} nhoi>={sum(nhoi):+.1f} MDD{dd(nhoi):.0f} | co delta {sum(s['has_delta'] for s in S)}/{len(S)}")
print(f"{'='*118}")

# ---- kiem tra do phu: co bao nhieu tin hieu co imbalance thuan/nghich theo tung nguong ----
print("\n### DO PHU imbalance (bao nhieu tin hieu co it nhat 1 muc imbalance) — tren 98 nen co delta")
print(f"  {'W ratio vmult':<16}{'#thuan>=1':>10}{'#nghich>=1':>12}{'#thuan_run>=3':>15}{'#nghich_run>=3':>16}")
for W in (1,3):
    for ratio in (2,3,4):
        for vmult in (2,):
            wd=[s for s in S if s['has_delta']]
            ft={id(s):features(s,W,ratio,vmult) for s in wd}
            th=sum(1 for s in wd if ft[id(s)] and ft[id(s)]['withc']>=1)
            ng=sum(1 for s in wd if ft[id(s)] and ft[id(s)]['oppc']>=1)
            th3=sum(1 for s in wd if ft[id(s)] and ft[id(s)]['withrun']>=3)
            ng3=sum(1 for s in wd if ft[id(s)] and ft[id(s)]['opprun']>=3)
            print(f"  W{W} r{ratio} v{vmult:<9}{th:>10}{ng:>12}{th3:>15}{ng3:>16}")

# ---- SWEEP gia thuyet ----
def make_keep(W,ratio,vmult,mode,direction):
    """mode: 'any'(count>=1) / 's2'(run>=2) / 's3'(run>=3). direction:'thuan'/'nghich'."""
    def keep(s):
        f=features(s,W,ratio,vmult)
        if f is None:return None
        if direction=='thuan':c=f['withc'];r=f['withrun']
        else:c=f['oppc'];r=f['opprun']
        if mode=='any':return c>=1
        if mode=='s2':return r>=2
        return r>=3
    return keep

for direction in ('thuan','nghich'):
    lbl='(a) THUAN huong lenh' if direction=='thuan' else '(b) NGUOC huong (absorption)'
    print(f"\n{'#'*118}\n### GIA THUYET {lbl}\n{'#'*118}")
    for W in (1,3):
        for mode in ('any','s2','s3'):
            print(f"--- W={W} nen, che do={mode} ---")
            for ratio in (2,3,4):
                report(f"r{ratio} v2 {mode}",S,make_keep(W,ratio,2,mode,direction))

# ---- phan bo theo thang cho 1-2 cau hinh dang chu y (in cuoi, dien vao sau khi xem sweep) ----
def bymonth(name,keepfn):
    kept=[s for s in S if keepfn(s) is True]
    if not kept:print(f"  {name}: rong");return
    print(f"  {name}: n={len(kept)} WR{sum(x['r']>0 for x in kept)/len(kept)*100:.0f}% phang{sum(x['r'] for x in kept):+.1f} nhoi>={sum((3 if x['confl']>=3 else 1)*x['r'] for x in kept):+.1f}")
    for m in MONTHS:
        mm=[s for s in kept if s['ym']==m]
        if mm:print(f"      {m}: n={len(mm)} WR{sum(x['r']>0 for x in mm)/len(mm)*100:.0f}% R{sum(x['r'] for x in mm):+.1f}")

print(f"\n{'='*118}\nPHAN BO THEO THANG — vai cau hinh dang chu y (kieu A, loai no-delta)\n{'='*118}")
bymonth("nghich any W3 r3 v2",make_keep(3,3,2,'any','nghich'))
bymonth("nghich s2  W3 r3 v2",make_keep(3,3,2,'s2','nghich'))
bymonth("thuan any W3 r3 v2 ",make_keep(3,3,2,'any','thuan'))

# ============================================================================
# PHAN TICH SAC BEN HON: PHAN HOACH (partition) + IMBALANCE LAM NHOI-TRIGGER
# ============================================================================
def exp_of(g):
    if not g:return (0,0.0,0.0)
    return (len(g),sum(x['r']>0 for x in g)/len(g),sum(x['r'] for x in g))
print(f"\n{'='*118}")
print("PHAN HOACH delta-signals theo co imbalance (any, W3) — so exp/lenh 2 nua (chan overfit)")
print(f"{'='*118}")
print(f"  baseline delta-bars: n={sum(s['has_delta'] for s in S)} exp={sum(x['r'] for x in S if x['has_delta'])/sum(s['has_delta'] for s in S):+.3f}")
print(f"  {'phan hoach (W3,any)':<26}{'n':>4}{'WR':>5}{'R':>7}{'exp':>8}  ||  {'nua con lai n':>6}{'WR':>5}{'R':>7}{'exp':>8}")
wd=[s for s in S if s['has_delta']]
for ratio in (2,3,4):
    for vmult in (1,2,3):
        ft={id(s):features(s,3,ratio,vmult) for s in wd}
        for direction in ('nghich','thuan'):
            key='oppc' if direction=='nghich' else 'withc'
            has=[s for s in wd if ft[id(s)] and ft[id(s)][key]>=1]
            non=[s for s in wd if not(ft[id(s)] and ft[id(s)][key]>=1)]
            n1,w1,r1=exp_of(has);n2,w2,r2=exp_of(non)
            print(f"  {direction} r{ratio} v{vmult:<14}{n1:>4}{w1*100:>4.0f}%{r1:>+7.1f}{(r1/n1 if n1 else 0):>+8.3f}  ||  {n2:>6}{w2*100:>4.0f}%{r2:>+7.1f}{(r2/n2 if n2 else 0):>+8.3f}")

print(f"\n{'='*118}")
print("IMBALANCE NGUOC (any,W3) LAM NHOI-TRIGGER tren TOAN BO 137 (khong loai bo lenh)")
print("  nhoi 3 lot khi: confl>=3 (hien tai) HOAC co opp-imbalance (chi ap bar co delta). So voi +39.5R")
print(f"{'='*118}")
print(f"  {'so do nhoi':<40}{'#nhoi':>6}{'tong_phang':>11}{'tong_nhoi':>10}{'MDD':>6}{'R/MDD':>7}")
flatall=[s['r'] for s in S]
def nhoi_scheme(trigfn,label):
    seq=[(3 if trigfn(s) else 1)*s['r'] for s in S]
    ntr=sum(trigfn(s) for s in S)
    print(f"  {label:<40}{ntr:>6}{sum(flatall):>+11.1f}{sum(seq):>+10.1f}{dd(seq):>6.0f}{(sum(seq)/dd(seq) if dd(seq)>0 else 0):>7.2f}")
nhoi_scheme(lambda s:s['confl']>=3,"confl>=3 (baseline nhoi)")
for ratio in (2,3):
    def opp_any(s,ratio=ratio):
        f=features(s,3,ratio,2);return bool(f and f['oppc']>=1)
    nhoi_scheme(lambda s,r=ratio:(s['confl']>=3 or opp_any(s)),f"confl>=3 OR opp-imb(r{ratio})")
    nhoi_scheme(lambda s,r=ratio:opp_any(s),f"CHI opp-imb(r{ratio}) (bo confl-nhoi)")
# nhoi khi opp-imb VA confl>=3 (giao)
def opp_and_c3(s):
    f=features(s,3,2,2);return bool(f and f['oppc']>=1) and s['confl']>=3
nhoi_scheme(opp_and_c3,"opp-imb(r2) AND confl>=3 (giao)")
