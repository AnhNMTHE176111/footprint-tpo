#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BANG SO CHOT — engine da sua 3 loi parity. Moi so trong PLAN lay tu day.
Chay lai: python3 final_table.py"""
import sys, statistics as st
from collections import defaultdict
sys.path.insert(0,"/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
sys.path.insert(0,".")
import entry_dxfeed as E, cbr_v6 as V

B=E.load_m1(); vf=E.calc_volfloor(B); E.VOLFLOOR_AUTO=vf; V.prepare(B)
CL=dict(CLEAN=True)
def DIRTYCFG(**kw):
    c=V.cfg(**kw); c['CLEAN']=False
    V._phase_c=lambda Bx,i,up,C: V.counter_sweep(Bx,i,up,C['CL_LOOK'],C['CL_W'],C['CL_CLOSE'])
    c['PHASE_C']=True; return c


def line(tag,S):
    if not S: print(f"  {tag:<40} n=0"); return
    rs=[s['r'] for s in S]; w=sum(1 for r in rs if r>0)
    bym=defaultdict(float)
    for s in S: bym[s['ym']]+=s['r']
    mm=" ".join(f"{m[-2:]}:{bym[m]:+5.1f}" for m in V.MONTHS if m in bym)
    ok=all(bym.get(m,0)>0 for m in V.MONTHS)
    cut=sorted(s['dt'] for s in S)[len(S)//2]
    h1=[s['r'] for s in S if s['dt']<cut]; h2=[s['r'] for s in S if s['dt']>=cut]
    print(f"  {tag:<40} n={len(S):3d} WR={100*w/len(S):5.1f}% tong={sum(rs):+6.1f}R EV={sum(rs)/len(S):+.3f} "
          f"MDD={V.mdd(rs):4.1f} | {mm} {'✓' if ok else '✗'} | nua {sum(h1):+.0f}/{sum(h2):+.0f}")
print("="*124); print("1. LO TRINH TU v5 SHIP -> v6  (dxFeed GCQ26, 5-7/2026, chi nhanh CBR)")
line("v5 nhu DANG SHIP (cat sai khung gio)", V.scan(B,V.cfg(DEAD=True,DEAD_FROM=19,DEAD_TO=1),vf,None))
line("+ B1 sua khung gio (cat UTC 02-08)",   V.scan(B,V.cfg(),vf,None))
line("+ B2 BREAK SACH",                      V.scan(B,V.cfg(CLEAN=True),vf,None))
line("+ B3 retrace 60-100%",                 V.scan(B,V.cfg(CLEAN=True,PMAX=1.00),vf,None))
line("+ B4 RR4 (thay RR3)",                  V.scan(B,V.cfg(CLEAN=True,PMAX=1.00,RR=4.0),vf,None))
print("="*124); print("2. BANG CHUNG bo loc BREAK SACH (chia CUNG tap baseline thanh 2 nhom ROI NHAU, RR3)")
line("nhom SACH",           V.scan(B,V.cfg(CLEAN=True),vf,None))
line("nhom CO QUET NGUOC",  V.scan(B,DIRTYCFG(),vf,None))
print("="*124); print("3. CHON RR (tren nen v6 = sach + retrace60-100)")
for rr in (2.0,3.0,4.0,5.0,6.0):
    line(f"RR {rr}", V.scan(B,V.cfg(CLEAN=True,PMAX=1.00,RR=rr),vf,None))
print("="*124); print("4. QUYET DINH CON LAI (tren nen v6 RR4)")
c=dict(CLEAN=True,PMAX=1.00,RR=4.0)
line("v6 RR4 (chuan)",              V.scan(B,V.cfg(**c),vf,None))
line("  TAT loc thanh khoan",       V.scan(B,V.cfg(LIQ=False,**c),vf,None))
line("  TAT loc gio chet",          V.scan(B,V.cfg(DEAD=False,**c),vf,None))
line("  TAT loc trend",             V.scan(B,V.cfg(TREND=False,**c),vf,None))
line("  TAT VWAP-align",            V.scan(B,V.cfg(VWAP=False,**c),vf,None))
line("  + R9 chat luong leg 50%",   V.scan(B,V.cfg(LEGQ=True,**c),vf,None))
line("  + span range <= 6.0 gia",   V.scan(B,V.cfg(RMAX=60,**c),vf,None))
print("="*124); print("5. DO NHAY tham so BREAK SACH (v6 RR4) — kiem cao nguyen, khong phai diem le")
for look,w in ((15,4),(15,5),(18,5),(20,4),(20,5),(20,6),(22,5),(25,5),(30,5)):
    line(f"look{look} w{w}", V.scan(B,V.cfg(CL_LOOK=look,CL_W=w,**c),vf,None))
print("="*124)
