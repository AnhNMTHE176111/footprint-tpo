#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vong 2 — sweep RR, chong toggle THANG, va thu BIEN THE khac cua W3 (Phase C/D).
Chay: python3 stack_v6.py"""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/wyckoff")
import entry_dxfeed as E
import cbr_v6 as V
cfg, scan, line, TICK = V.cfg, V.scan, V.line, V.TICK

B = E.load_m1(); vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf
avg = st.mean(b['vma'] for b in B if b['vma'] > 0)
print(f"M1={len(B)}  volfloor={vf}\n" + "=" * 118)

print("A. SWEEP RR (SL v5, khong doi gi khac) — kiem 'bop SL de gong dai' o phia TP")
for rr in (2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0):
    line(f"RR {rr}", scan(B, cfg(RR=rr), vf, avg))
print("=" * 118)

print("B. SWEEP nguong chat luong leg R9 (RR3)")
for m in (0.30, 0.40, 0.50, 0.60, 0.70):
    line(f"LEGQ>={m:.0%}", scan(B, cfg(LEGQ=True, LEGQ_MIN=m), vf, avg))
print("  -- cung nguong nhung RR5 --")
for m in (0.40, 0.50, 0.60):
    line(f"LEGQ>={m:.0%} + RR5", scan(B, cfg(LEGQ=True, LEGQ_MIN=m, RR=5.0), vf, avg))
print("=" * 118)

print("C. SWEEP retrace (v5 dang 60-90%)")
for lo, hi in ((0.40, 0.90), (0.50, 0.90), (0.60, 0.90), (0.70, 0.90), (0.60, 1.00), (0.50, 1.00)):
    line(f"retrace {lo:.0%}-{hi:.0%}", scan(B, cfg(PMIN=lo, PMAX=hi), vf, avg))
print("=" * 118)

print("D. SWEEP span range (v5 dang 3.0-7.5 gia) — 'bien cua chu to the'")
for lo, hi in ((20, 75), (30, 75), (30, 60), (30, 50), (40, 75), (20, 50)):
    line(f"span {lo/10:.1f}-{hi/10:.1f}gia", scan(B, cfg(RMIN=lo, RMAX=hi), vf, avg))
print("=" * 118)

print("E. STACK cac thu THANG (RR5 + LEGQ) + kiem tung buoc")
line("baseline RR3", scan(B, cfg(), vf, avg))
line("+RR5", scan(B, cfg(RR=5.0), vf, avg))
line("+RR5 +LEGQ50", scan(B, cfg(RR=5.0, LEGQ=True), vf, avg))
line("+RR5 +LEGQ50 +span<=6.0", scan(B, cfg(RR=5.0, LEGQ=True, RMAX=60), vf, avg))
print("=" * 118)

print("F. W3 bien the — 'dung danh UT som / sang D moi danh'")
print("   F1: bat buoc PHA HUT canh doi dien (spring/upthrust) — da test, sweep them")
for look, w in ((15, 4), (20, 5), (30, 5), (30, 8), (40, 8)):
    line(f"PhaseC look{look} w{w}", scan(B, cfg(PHASE_C=True, PC_LOOK=look, PC_W=w), vf, avg))
print("   F2: doi lai — CAM khi co pha hut (tuc chi danh break 'sach')")
import types
_orig = V._phase_c
V._phase_c = lambda B, i, up, C: not _orig(B, i, up, C)
for look in (20, 30):
    line(f"KHONG-PhaseC look{look}", scan(B, cfg(PHASE_C=True, PC_LOOK=look), vf, avg))
V._phase_c = _orig
print("=" * 118)
print("Nhac: '✓3thg' = duong ca 3 thang. Khong co = KHONG nhan (chong overfit).")
