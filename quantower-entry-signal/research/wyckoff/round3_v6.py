#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vong 3 — dao sau phat hien 'BREAK SACH' (khong co cu quet nguoc gan do) + stack + OOS split.
Vong 2 cho: cam-khi-co-pha-hut (tuc CHI danh break sach) => n30 WR53% +34R EV+1.13 MDD3.
Vong nay: (a) dinh nghia lai cho ro rang, (b) sweep, (c) stack voi RR/span/retrace/LEGQ,
(d) CHIA DOI cua so lam OOS tho, (e) do bang so lenh de biet cell nao qua nho.
Chay: python3 round3_v6.py"""
import sys, statistics as st
from collections import defaultdict
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/wyckoff")
import entry_dxfeed as E
import cbr_v6 as V
cfg, scan, TICK = V.cfg, V.scan, V.TICK

B = E.load_m1(); vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf
avg = st.mean(b['vma'] for b in B if b['vma'] > 0)

# ---------------- dinh nghia BREAK SACH ----------------
# "quet nguoc" = trong CLEAN_LOOK nen truoc nen break, co >=1 nen dam thung cuc tri cuc bo
# phia DOI DIEN huong break roi DONG lai vao trong (that bai). Co = thi truong dang xoay 2 chieu
# -> break tiep theo de la bay. Khong co = nen sach -> break dang tin.
def has_counter_sweep(B, i, up, look, w, cl):
    lo_k = max(E.VSA_MA, i - look)
    for k in range(lo_k + w, i):
        b = B[k]
        if b['rng'] <= 0:
            continue
        win = B[k - w:k]
        if not win:
            continue
        if up:
            loc = min(x['lo'] for x in win)
            if b['lo'] < loc - TICK and b['c'] > loc and b['cpos'] >= cl:
                return True
        else:
            loc = max(x['hi'] for x in win)
            if b['hi'] > loc + TICK and b['c'] < loc and b['cpos'] <= 1 - cl:
                return True
    return False

def patch_clean(look, w, cl=0.50):
    """PHASE_C=True se duoc hieu la: CHI nhan khi KHONG co quet nguoc (break sach)."""
    V._phase_c = lambda Bx, i, up, C: not has_counter_sweep(Bx, i, up, look, w, cl)

def line(tag, S, half=None):
    if not S:
        print(f"  {tag:<36} n=  0  —"); return
    rs = [s['r'] for s in S]; wnum = sum(1 for r in rs if r > 0)
    bym = defaultdict(float)
    for s in S: bym[s['ym']] += s['r']
    mm = " ".join(f"{m[-2:]}:{bym[m]:+5.1f}" for m in V.MONTHS if m in bym)
    ok = all(bym.get(m, 0) > 0 for m in V.MONTHS)
    extra = ""
    if half:
        cut = sorted(s['dt'] for s in S)[len(S)//2]
        h1 = [s['r'] for s in S if s['dt'] < cut]; h2 = [s['r'] for s in S if s['dt'] >= cut]
        extra = f"| nua1 {sum(h1):+5.1f}R(n{len(h1)}) nua2 {sum(h2):+5.1f}R(n{len(h2)})"
    print(f"  {tag:<36} n={len(S):3d} WR={100*wnum/len(S):5.1f}% tong={sum(rs):+7.1f}R "
          f"EV={sum(rs)/len(S):+.3f} MDD={V.mdd(rs):5.1f} | {mm} {'✓' if ok else '✗'} {extra}")

if __name__ == "__main__":
    import sys as _s; _s.exit(0)  # cac test cu da chuyen sang final_table.py

#print("=" * 130)
#print("A. SWEEP dinh nghia 'BREAK SACH' (khong co quet nguoc trong LOOK nen truoc), RR3")
#for look, w in ((10, 4), (15, 4), (15, 5), (20, 5), (25, 5), (30, 5), (20, 8), (30, 8)):
#    patch_clean(look, w)
#    line(f"sach look{look} w{w}", scan(B, cfg(PHASE_C=True), vf, avg), half=True)
#print("=" * 130)
#
#print("B. BREAK SACH (look20 w5) x RR")
#patch_clean(20, 5)
#for rr in (2.0, 3.0, 4.0, 5.0, 6.0, 8.0):
#    line(f"sach + RR{rr}", scan(B, cfg(PHASE_C=True, RR=rr), vf, avg), half=True)
#print("=" * 130)
#
#print("C. STACK tren nen BREAK SACH (look20 w5, RR3 tru khi ghi ro)")
#patch_clean(20, 5)
#line("sach", scan(B, cfg(PHASE_C=True), vf, avg), half=True)
#line("sach + retrace60-100", scan(B, cfg(PHASE_C=True, PMAX=1.00), vf, avg), half=True)
#line("sach + LEGQ50", scan(B, cfg(PHASE_C=True, LEGQ=True), vf, avg), half=True)
#line("sach + span<=6.0", scan(B, cfg(PHASE_C=True, RMAX=60), vf, avg), half=True)
#line("sach + retrace60-100 + RR4", scan(B, cfg(PHASE_C=True, PMAX=1.00, RR=4.0), vf, avg), half=True)
#line("sach + retrace60-100 + RR5", scan(B, cfg(PHASE_C=True, PMAX=1.00, RR=5.0), vf, avg), half=True)
#line("sach + retrace60-100 + LEGQ50 RR4", scan(B, cfg(PHASE_C=True, PMAX=1.00, LEGQ=True, RR=4.0), vf, avg), half=True)
#print("=" * 130)
#
#print("D. Doi chieu: bo tung gate v5 khoi 'sach' de xem gate nao con dong gop")
#patch_clean(20, 5)
#line("sach (du gate)", scan(B, cfg(PHASE_C=True), vf, avg))
#line("sach, TAT trend", scan(B, cfg(PHASE_C=True, TREND=False), vf, avg))
#line("sach, TAT vwap", scan(B, cfg(PHASE_C=True, VWAP=False), vf, avg))
#line("sach, TAT liquidity", scan(B, cfg(PHASE_C=True, LIQ=False), vf, avg))
#line("sach, TAT loc phien chet", scan(B, cfg(PHASE_C=True, DEAD=False), vf, avg))
#print("=" * 130)
#
#print("E. Chung minh 'sach' KHONG chi la trung lap voi trend: xet ca 2 nhom")
#patch_clean(20, 5)
#S_clean = scan(B, cfg(PHASE_C=True), vf, avg)
#V._phase_c = lambda Bx, i, up, C: has_counter_sweep(Bx, i, up, 20, 5, 0.50)
#S_dirty = scan(B, cfg(PHASE_C=True), vf, avg)
#line("nhom SACH", S_clean)
#line("nhom CO QUET NGUOC", S_dirty)
#print("  => neu nhom 'co quet nguoc' te ro rang thi bo loc co co so, khong phai nhieu.")
#print("=" * 130)
#
