#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vong 4 — chot cau hinh v6 tren dxFeed + KIEM LOP DELTA THAT tren merged feed (6/1->7/27).
(1) tinh chinh quanh cau hinh thang: sach + retrace60-100 + RR4/5, thu tat liquidity.
(2) R1 'buy limit vs buy market': leg phai do lenh CHU DONG day (ddom cua leg) — merged feed.
(3) R2 'buy limit o chan song thi ngon, o dinh thi lo': hap thu tai CUC TRI.
Chay: python3 round4_v6.py"""
import sys, statistics as st
from collections import defaultdict
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/wyckoff")
import entry_dxfeed as E
import cbr_v6 as V
from round3_v6 import has_counter_sweep
cfg, scan, TICK = V.cfg, V.scan, V.TICK

def patch_clean(look=20, w=5, cl=0.50):
    V._phase_c = lambda Bx, i, up, C: not has_counter_sweep(Bx, i, up, look, w, cl)

def line(tag, S, half=True):
    if not S:
        print(f"  {tag:<38} n=  0  —"); return
    rs = [s['r'] for s in S]; wn = sum(1 for r in rs if r > 0)
    bym = defaultdict(float)
    for s in S: bym[s['ym']] += s['r']
    mm = " ".join(f"{m[-2:]}:{bym[m]:+5.1f}" for m in V.MONTHS if m in bym)
    ok = all(bym.get(m, 0) > 0 for m in V.MONTHS if any(s['ym'] == m for s in S))
    ex = ""
    if half and len(S) > 3:
        cut = sorted(s['dt'] for s in S)[len(S)//2]
        h1 = [s['r'] for s in S if s['dt'] < cut]; h2 = [s['r'] for s in S if s['dt'] >= cut]
        ex = f"| nua1 {sum(h1):+5.1f}(n{len(h1)}) nua2 {sum(h2):+5.1f}(n{len(h2)})"
    print(f"  {tag:<38} n={len(S):3d} WR={100*wn/len(S):5.1f}% tong={sum(rs):+7.1f}R "
          f"EV={sum(rs)/len(S):+.3f} MDD={V.mdd(rs):5.1f} | {mm} {'✓' if ok else '✗'} {ex}")

# ============================ PHAN 1: dxFeed 3 thang ============================
B = E.load_m1(); vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf
avg = st.mean(b['vma'] for b in B if b['vma'] > 0)
print("=" * 132)
print("PHAN 1 — dxFeed 5-7/2026 (khong delta). Nen: sach look20w5 + retrace60-100")
patch_clean()
line("v5 BASELINE (doi chieu)", scan(B, cfg(PHASE_C=False), vf, avg))
for rr in (3.0, 4.0, 5.0):
    line(f"v6 sach+r60-100 RR{rr}", scan(B, cfg(PHASE_C=True, PMAX=1.00, RR=rr), vf, avg))
    line(f"   ^ + TAT liquidity", scan(B, cfg(PHASE_C=True, PMAX=1.00, RR=rr, LIQ=False), vf, avg))
print("-" * 132)
print("  Nhay cam tham so 'sach' quanh diem chot (RR4, retrace60-100):")
for look, w in ((15, 5), (18, 5), (20, 5), (22, 5), (25, 5), (20, 4), (20, 6)):
    patch_clean(look, w)
    line(f"  look{look} w{w}", scan(B, cfg(PHASE_C=True, PMAX=1.00, RR=4.0), vf, avg))
print("=" * 132)

# ============================ PHAN 2: merged feed co DELTA ============================
print("PHAN 2 — merged feed (dxFeed OHLC + footprint delta THAT), 6/1 -> 7/27")
import fp_merged as M
BM = M.load_merged()
vfm = E.calc_volfloor(BM); avgm = st.mean(b['vma'] for b in BM if b['vma'] > 0)
MONTHS_M = ('2026-06', '2026-07')
V.MONTHS = MONTHS_M
patch_clean()

print("  (a) nen v6 tren merged feed — doi chieu truoc khi them delta")
line("v5 baseline", scan(BM, cfg(PHASE_C=False, RR=4.0), vfm, avgm))
line("v6 sach+r60-100 RR4", scan(BM, cfg(PHASE_C=True, PMAX=1.00, RR=4.0), vfm, avgm))
print("  (b) R1 — leg phai do LENH CHU DONG day (ddom leg >= nguong)")
for a in (0.00, 0.03, 0.05, 0.10, 0.15):
    line(f"v6 + AGGR>={a:+.2f}", scan(BM, cfg(PHASE_C=True, PMAX=1.00, RR=4.0, AGGR=True, AGGR_MIN=a), vfm, avgm))
print("  (c) doi chieu: leg NGUOC delta (buy-limit-driven) — theo CORVEN la 'khong ben'")
_orig = V._leg_aggr
V._leg_aggr = lambda Bx, i0, i1, up: (lambda a: None if a is None else -a)(_orig(Bx, i0, i1, up))
line("v6 + leg NGUOC delta", scan(BM, cfg(PHASE_C=True, PMAX=1.00, RR=4.0, AGGR=True, AGGR_MIN=0.05), vfm, avgm))
V._leg_aggr = _orig
print("=" * 132)
print("Nhac trung thuc: PHAN 2 chi 2 thang, n nho. Chenh lech nho = KHONG ket luan duoc.")
