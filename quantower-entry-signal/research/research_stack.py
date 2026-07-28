#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NHOI 3 LENH CUNG 1 VI TRI khi hop luu>=2 (user 2026-07-28).
Danh gia 2 NGHIA khac nhau + DRAWDOWN (vi nhoi lenh = rui ro nhan len):

NGHIA A - 3 lot cung entry/SL/TP=1.5R  => TOAN HOC = 1 lot x3 (don bay 3x).
   WR & R/don-vi KHONG doi; chi nhan doi ca LOI LAN LO. Cau hoi that su = tai khoan chiu noi 3x
   drawdown khong. Do: tong R (theo don vi rui ro goc), MAX DRAWDOWN (R), chuoi thua dai nhat.
   So sanh: A=phang 1u; B=3u dong loat (>=2); C=1u@confl2/3u@confl>=3 (sizing theo NIEM TIN);
            D=ladder 1/2/3 theo confl 1/2/>=3 (gom ca confl1 de tang so lenh).

NGHIA B - 3 lot CHIA TP khac nhau (scale-out) + doi SL ve HOA VON sau khi lot1 an.
   Day moi la cach dan trader hay lam. Do R/don-vi + WR-cam-giac (%lenh net duong) + MDD.
Chay dxFeed 5-7/2026, delta-free, RR nen 1.5."""
import entry_dxfeed as E
TICK=0.1
E.B=E.load_m1();E.VOLFLOOR_AUTO=E.calc_volfloor(E.B);pool=E.build_zones(E.B);E.USE_DELTA=False
MONTHS=('2026-05','2026-06','2026-07')
B=E.B

def sim_rr(s,rr):
    entry=s['entry'];sl=s['sl'];side=s['side'];risk=s['risk_t']*TICK
    tp=entry+rr*risk if side=='LONG' else entry-rr*risk
    for j in range(s['i']+1,len(B)):
        hb=B[j]
        hitSL=hb['lo']<=sl if side=='LONG' else hb['hi']>=sl
        hitTP=hb['hi']>=tp if side=='LONG' else hb['lo']<=tp
        if hitSL:return -1.0
        if hitTP:return rr
    return None  # chua dong -> loai

def sim_scaleout(s,tps,be_after_lot=1):
    """3 lot, moi lot 1 don vi rui ro. tps=list R muc tieu (asc). Sau be_after_lot lot chot -> SL ve BE.
    Tra ve TONG R cong don tren 3 lot (moi lot rui ro 1u)."""
    entry=s['entry'];sl=s['sl'];side=s['side'];risk=s['risk_t']*TICK
    lots=sorted(tps);closed=[False]*len(lots);realized=0.0;done=0;cur_sl=sl
    any_settled=False
    for j in range(s['i']+1,len(B)):
        hb=B[j]
        hitSL=hb['lo']<=cur_sl if side=='LONG' else hb['hi']>=cur_sl
        if hitSL:
            rex=(cur_sl-entry)/risk if side=='LONG' else (entry-cur_sl)/risk
            for k in range(len(lots)):
                if not closed[k]:realized+=rex;closed[k]=True
            any_settled=True;break
        for k in range(len(lots)):
            if closed[k]:continue
            tp=entry+lots[k]*risk if side=='LONG' else entry-lots[k]*risk
            if (hb['hi']>=tp if side=='LONG' else hb['lo']<=tp):
                realized+=lots[k];closed[k]=True;done+=1;any_settled=True
                if done>=be_after_lot and cur_sl!=entry:cur_sl=entry
        if all(closed):break
    if not any_settled:return None
    return realized  # tong tren 3 lot

def stats(seq):
    """seq = list R theo THU TU thoi gian (da nhan he so size). Tra ve tongR, MDD, chuoi thua."""
    tot=sum(seq);eq=0.0;peak=0.0;mdd=0.0;streak=0;worst_streak=0
    for r in seq:
        eq+=r;peak=max(peak,eq);mdd=max(mdd,peak-eq)
        if r<0:streak+=1;worst_streak=max(worst_streak,streak)
        else:streak=0
    return tot,mdd,worst_streak

# ---- lay TAT CA setup confl>=1, theo thu tu thoi gian (sort theo bar index i) ----
C=E.prep(dict(E.make(MIN_CONFL=1)))
raw=E.run(B,pool,C)
sig=[s for s in E.dedup(raw,pool,C) if s['ym'] in MONTHS]
sig.sort(key=lambda s:s['i'])
for s in sig:s['r15']=sim_rr(s,1.5)
settled=[s for s in sig if s['r15'] is not None]
print(f"tong setup confl>=1: {len(sig)} | da dong (settled): {len(settled)}")
n1=sum(s['confl']==1 for s in settled);n2=sum(s['confl']==2 for s in settled);n3=sum(s['confl']>=3 for s in settled)
print(f"phan bo: confl1={n1}  confl2={n2}  confl>=3={n3}")

print("\n"+"="*78)
print("NGHIA A - 3 lot CUNG entry/SL/TP=1.5R  (= don bay, WR & R/1u KHONG doi)")
print("="*78)
print(f"{'so do sizing':<40}{'#lenh':>6}{'tongR':>8}{'MDD':>8}{'R/MDD':>7}{'thua_lien':>10}")
def run_size(sizer,label,gate=2):
    seq=[sizer(s)*s['r15'] for s in settled if s['confl']>=gate and sizer(s)>0]
    if not seq:print(f"  {label:<38} (rong)");return
    tot,mdd,ws=stats(seq)
    print(f"  {label:<38}{len(seq):>6}{tot:>+8.1f}{mdd:>8.1f}{(tot/mdd if mdd>0 else 0):>7.2f}{ws:>10}")
run_size(lambda s:1, "A phang 1u (confl>=2)  [he hien tai]",2)
run_size(lambda s:3, "B 3u dong loat (confl>=2)  [y user]",2)
run_size(lambda s:(3 if s['confl']>=3 else 1),"C 1u@confl2 / 3u@confl>=3 (niem tin)",2)
run_size(lambda s:(1 if s['confl']==1 else(2 if s['confl']==2 else 3)),"D ladder 1/2/3 theo confl 1/2/>=3",1)
# tham chieu: chi so R/MDD cao = sizing dang; nhung B chi la A nhan 3 (R/MDD y het A)

print("\n"+"="*78)
print("NGHIA B - 3 lot CHIA TP + doi SL ve HOA VON sau lot1  (scale-out, confl>=2)")
print("  R/1u = tongR chia 3 (3 don vi rui ro). WR-cam-giac = %lenh net > 0.")
print("="*78)
g2=[s for s in settled if s['confl']>=2]
print(f"  {'so do scale-out':<34}{'#lenh':>6}{'R/1u':>8}{'WRcamgiac':>11}{'MDD(3u)':>9}")
def run_so(tps,be,label):
    rs=[]
    for s in g2:
        r=sim_scaleout(s,tps,be)
        if r is not None:rs.append(r)
    if not rs:print(f"  {label:<34} (rong)");return
    perunit=sum(rs)/3/len(rs)  # R tren 1 don vi rui ro moi lenh
    wrfeel=sum(r>0 for r in rs)/len(rs)
    _,mdd,_=stats(rs)
    print(f"  {label:<34}{len(rs):>6}{perunit:>+8.2f}{wrfeel*100:>10.0f}%{mdd:>9.1f}")
# tham chieu phang 1 lot 1.5R:
ref=[s['r15'] for s in g2]
print(f"  {'(tham chieu) 1 lot phang 1.5R':<34}{len(ref):>6}{sum(ref)/len(ref):>+8.2f}{sum(r>0 for r in ref)/len(ref)*100:>10.0f}%{stats(ref)[1]:>9.1f}")
run_so([1.0,1.5,2.0],1,"SO1 [1.0/1.5/2.0] BE sau lot1")
run_so([1.0,1.5,2.5],1,"SO2 [1.0/1.5/2.5] BE sau lot1")
run_so([1.5,1.5,1.5],1,"SO3 [1.5/1.5/1.5] BE sau lot1")
run_so([1.0,2.0,3.0],1,"SO4 [1.0/2.0/3.0] BE sau lot1")
run_so([1.0,1.5,2.0],0,"SO5 [1.0/1.5/2.0] KHONG doi BE")
