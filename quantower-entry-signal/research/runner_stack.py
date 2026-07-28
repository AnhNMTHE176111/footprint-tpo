#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RUNNER + NHOI 3 LOT KHI HOP LUU>=3 (user 2026-07-28).
PHAN A: CSV v5 THAT (data-export/27-7, ~1 thang) — phan bo hop luu + WR/R theo muc + nhoi>=3.
PHAN B: tai dung CBR continuation tren dxFeed 3 THANG (delta-free) + loc v5 (trend/vwap/l* thanh khoan),
        do cluster tung lenh, so phang 1 lot vs nhoi 3 lot khi cluster>=3, RR=3 (runner). Theo thang + MDD.
LUU Y trung thuc: PHAN B la XAP XI v5 (CBR core + loc portable), KHONG gom nhanh QUAY_DAU reversal;
   dxFeed la proxy yeu (khong delta). Diem chac chan = PHAN BO hop luu (runner hiem khi >=3)."""
import csv,statistics as st
import entry_dxfeed as E
TICK=E.TICK

def dd(seq):
    eq=0.0;peak=0.0;mdd=0.0
    for r in seq:eq+=r;peak=max(peak,eq);mdd=max(mdd,peak-eq)
    return mdd

# ================= PHAN A: CSV v5 that =================
print("="*74)
print("PHAN A — RunnerSignal v5 THAT (CSV 29/6->27/7, ~1 thang), RR=3")
print("="*74)
rows=list(csv.DictReader(open("/home/asl86/Documents/footprint-tpo/data-export/27-7/RunnerSignal_signals.csv",encoding="utf-8-sig")))
def rval(kq,rr=3):return rr if kq=='WIN' else(-1.0 if kq=='LOSS' else None)
def bkt(c):c=int(c);return '0' if c==0 else('1' if c==1 else('2' if c==2 else '>=3'))
print(f"  tong lenh: {len(rows)}  | nhanh: CBR/QUAY_DAU")
print(f"  {'hop luu':<8}{'n':>5}{'settled':>8}{'WR':>6}{'tongR(1lot)':>13}")
allR=[]
for b in ['0','1','2','>=3']:
    g=[r for r in rows if bkt(r['co_vung'])==b]
    rs=[rval(r['KQ']) for r in g];se=[x for x in rs if x is not None]
    wr=sum(x>0 for x in se)/len(se) if se else 0
    print(f"  {b:<8}{len(g):>5}{len(se):>8}{wr*100:>5.0f}%{sum(se):>+13.1f}")
# tong + nhoi>=3
se_all=[(int(r['co_vung']),rval(r['KQ'])) for r in rows if rval(r['KQ']) is not None]
flat=sum(r for _,r in se_all)
nhoi=sum((3 if c>=3 else 1)*r for c,r in se_all)
n3=[r for c,r in se_all if c>=3]
print(f"\n  TONG phang 1 lot : {flat:+.1f}R  (n_settled={len(se_all)}, WR {sum(r>0 for _,r in se_all)/len(se_all)*100:.0f}%)")
print(f"  NHOI 3 lot khi>=3: {nhoi:+.1f}R   (nhom>=3 chi n={len(n3)} lenh: {n3})")
print(f"  => nhoi>=3 chi doi {flat:+.1f} -> {nhoi:+.1f}R  (nhom>=3 qua hiem: {len(n3)}/{len(se_all)} = {100*len(n3)/len(se_all):.0f}%)")

# ================= PHAN B: CBR tren dxFeed 3 thang =================
print("\n"+"="*74)
print("PHAN B — CBR continuation tai dung tren dxFeed 3 THANG (delta-free, xap xi v5)")
print("="*74)
B=E.load_m1();E.VOLFLOOR_AUTO=E.calc_volfloor(B);vf=E.VOLFLOOR_AUTO;pool=E.build_zones(B)
MONTHS=('2026-05','2026-06','2026-07')
avg_vma=st.mean(b['vma'] for b in B if b['vma']>0)
RANGE_LEN=8;RMIN=30;RMAX=75;BVSA=2.0;BBODY=0.50;WAIT=12;PMIN=0.40;PMAX=0.90
HOLD_TOL=2;RBODY=0.35;FLOOR=30;CAP=70;BUF=2;COOL=15
V5=True   # loc trend + vwap-side + thanh khoan (portable, delta-free)
def gate(b):return b['v']>=vf and b['since_gap']>=E.WARMUP_AFTER_GAP and b['vma']>=vf*0.6
def run_cbr(B):
    raw=[];N=len(B)
    for i in range(E.VSA_MA+2,N):
        b=B[i]
        if not gate(b):continue
        win=B[i-RANGE_LEN:i];rhi=max(x['hi'] for x in win);rlo=min(x['lo'] for x in win)
        span=(rhi-rlo)/TICK
        if span>RMAX or span<RMIN:continue
        up=b['c']>rhi+BUF*TICK and b['vratio']>=BVSA and b['brat']>=BBODY and b['c']>b['o']
        dn=b['c']<rlo-BUF*TICK and b['vratio']>=BVSA and b['brat']>=BBODY and b['c']<b['o']
        if V5:  # THUAN xu huong + dung phia VWAP + thanh khoan du
            if up and not(b['trend']>0 and b['c']>b['vwap'] and b['vma']>=0.75*avg_vma):up=False
            if dn and not(b['trend']<0 and b['c']<b['vwap'] and b['vma']>=0.75*avg_vma):dn=False
        if not(up or dn):continue
        side='LONG' if up else 'SHORT';edge=rhi if up else rlo
        peak=b['hi'] if up else b['lo'];since=i
        for j in range(i+1,min(N,i+1+WAIT)):
            bj=B[j]
            if not gate(bj):break
            if (bj['c']<edge-HOLD_TOL*TICK) if up else (bj['c']>edge+HOLD_TOL*TICK):break
            pseg=B[since+1:j+1]
            if pseg:
                pext=min(x['lo'] for x in pseg) if up else max(x['hi'] for x in pseg)
                leg=(peak-edge) if up else (edge-peak)
                depth=(peak-pext) if up else (pext-peak)
                retr=depth/leg if leg>0 else 0
                held=(pext>=edge-HOLD_TOL*TICK) if up else (pext<=edge+HOLD_TOL*TICK)
                resume=((bj['c']>B[j-1]['hi'] and bj['c']>bj['o']) if up else (bj['c']<B[j-1]['lo'] and bj['c']<bj['o'])) and bj['brat']>=RBODY
                if j>=since+2 and PMIN<=retr<=PMAX and held and resume:
                    entry=bj['c']
                    if up:sl=pext-BUF*TICK;risk=(entry-sl)/TICK
                    else:sl=pext+BUF*TICK;risk=(sl-entry)/TICK
                    if risk<FLOOR:sl=(entry-FLOOR*TICK) if up else (entry+FLOOR*TICK);risk=FLOOR
                    if risk>CAP:break
                    raw.append(dict(i=j,dt=bj['dt'],ym=bj['ym'],side=side,entry=entry,sl=sl,risk_t=risk))
                    break
            if (bj['hi']>peak) if up else (bj['lo']<peak):peak=bj['hi'] if up else bj['lo'];since=j
    return raw
def dedup(raw):
    out=[]
    for s in sorted(raw,key=lambda x:x['i']):
        if any(m['side']==s['side'] and abs(s['i']-m['i'])<=E.DEDUP_BARS for m in out):continue
        out.append(s)
    return out
def cooldown(sig,cd):
    out=[];last={}
    for s in sorted(sig,key=lambda x:x['i']):
        if s['i']-last.get(s['side'],-999)<cd:continue
        out.append(s);last[s['side']]=s['i']
    return out
def hit(i,side,sl,tp):
    for j in range(i+1,len(B)):
        b=B[j]
        if (b['lo']<=sl) if side=='LONG' else (b['hi']>=sl):return 'SL'
        if (b['hi']>=tp) if side=='LONG' else (b['lo']<=tp):return 'TP'
    return 'open'

sig=cooldown(dedup(run_cbr(B)),COOL)
sig=[s for s in sig if s['ym'] in MONTHS]
sig.sort(key=lambda s:s['i'])
for s in sig:s['cluster']=E.cluster_count(s,pool)
for s in sig:
    r=s['risk_t']*TICK;tp=s['entry']+3*r if s['side']=='LONG' else s['entry']-3*r
    o=hit(s['i'],s['side'],s['sl'],tp);s['o']=o;s['r']=3.0 if o=='TP' else(-1.0 if o=='SL' else None)
S=[s for s in sig if s['r'] is not None]
print(f"  n (3 thang, da dong) = {len(S)}   | RR=3")
from collections import Counter
cc=Counter(min(s['cluster'],3) for s in S)
print(f"  PHAN BO hop luu: 0={cc[0]}  1={cc[1]}  2={cc[2]}  >=3={cc[3]}   (>=3 = {100*cc[3]/len(S):.0f}% — hiem nhu du doan)")
wr=sum(s['r']>0 for s in S)/len(S)
flat=[s['r'] for s in S];nhoi=[(3 if s['cluster']>=3 else 1)*s['r'] for s in S]
print(f"  {'so do':<26}{'tongR':>8}{'MDD':>8}{'WR':>6}")
print(f"  {'phang 1 lot':<26}{sum(flat):>+8.1f}{dd(flat):>8.1f}{wr*100:>5.0f}%")
print(f"  {'nhoi 3 lot khi >=3':<26}{sum(nhoi):>+8.1f}{dd(nhoi):>8.1f}{wr*100:>5.0f}%")
print(f"  => nhoi>=3 doi {sum(flat):+.1f} -> {sum(nhoi):+.1f}R  (chenh {sum(nhoi)-sum(flat):+.1f}R tu {cc[3]} lenh >=3)")
print("\n  Theo thang (phang vs nhoi):")
for m in MONTHS:
    mm=[s for s in S if s['ym']==m]
    if not mm:continue
    print(f"    {m}: n={len(mm):>3} >=3:{sum(s['cluster']>=3 for s in mm):>2} WR{sum(s['r']>0 for s in mm)/len(mm)*100:>3.0f}% "
          f"phang {sum(s['r'] for s in mm):+.1f}R  nhoi {sum((3 if s['cluster']>=3 else 1)*s['r'] for s in mm):+.1f}R")
# tham chieu cac RR khac
print("\n  Tham chieu tong R theo RR (phang 1 lot):")
for rr in (1.5,2.0,3.0):
    tot=0;t=0;n=0
    for s in S:
        r=s['risk_t']*TICK;tp=s['entry']+rr*r if s['side']=='LONG' else s['entry']-rr*r
        o=hit(s['i'],s['side'],s['sl'],tp)
        if o in('TP','SL'):n+=1;t+=o=='TP';tot+=(rr if o=='TP' else -1)
    print(f"    RR{rr}: n={n} WR {t/n*100:.0f}% tong {tot:+.1f}R")
