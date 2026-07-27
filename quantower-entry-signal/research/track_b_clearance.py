#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRACK B huong DUNG (khong phai 'vao nen xac nhan' — cai do da test TE hon).
Giu entry nhip-hoi (nhu ba A) + hold-zone, roi thu 2 don bay cho 3R:
  (1) CLEARANCE: chi vao neu con DU CHO chay toi 3R (khong co vung can nguoc trong 3R).
      -> tra loi lenh 1 (bi rejection 4142 chan tren dau nen ket o 2R).
  (2) SL siet 2 gia (de 3R=6 gia, gan hon).
Do @3R. cum>=2, hold-zone ON.
"""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
em.SL_MIN_T = 40; em.SL_MAX_T = 60; em.RR = 1.5; em.NEXTZONE_MINR = 2.0; em.RETEST_HOLD_T = 0
CONFL_TOL = 7


def hit(B, i, side, sl, tp):
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl): return 'SL'
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp): return 'TP'
    return 'open'


def clu(pool, t, zp):
    s = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL: s.add(round(z['price'] / TICK))
    return len(s)


def opp_clearance_R(pool, s):
    """khoang toi vung CAN nguoc gan nhat, tinh theo R."""
    r = s['risk_t'] * TICK; e = s['entry']
    cand = [z['price'] for z in pool if z['ready'] <= s['dt'] <= z['expire']]
    if s['side'] == 'LONG':
        up = [p for p in cand if p > e + 3 * TICK]
        return (min(up) - e) / r if up else 99.0
    else:
        dn = [p for p in cand if p < e - 3 * TICK]
        return (e - max(dn)) / r if dn else 99.0


def ev(B, S, rm, slw=None):
    tp = sl = 0
    for s in S:
        if slw is None:
            r = s['risk_t'] * TICK; slp = s['sl']
        else:
            r = slw * TICK; slp = s['entry'] - r if s['side'] == 'LONG' else s['entry'] + r
        tpp = s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r
        o = hit(B, s['i'], s['side'], slp, tpp)
        tp += o == 'TP'; sl += o == 'SL'
    n = tp + sl
    return len(S), (tp / n if n else 0), ((tp * rm - sl) / n if n else 0), (tp * rm - sl)


B = em.load_m1(); pool = em.build_zones(B)
raw = em.run(B, pool)
for s in raw: s['cluster'] = clu(pool, s['dt'], float(s['zone'].split()[-1]))
sig = em.dedup(raw)
for s in sig: s.setdefault('cluster', 1)
sig = [s for s in sig if s['cluster'] >= 2]
for s in sig: s['clear'] = opp_clearance_R(pool, s)

print("=" * 92)
print("TRACK B — entry nhip-hoi + hold-zone, don bay cho 3R (cum>=2, 1 thang, n=%d)" % len(sig))
print("\n(1) CLEARANCE toi 3R (khong vung can nguoc trong 3R):")
print(f"  {'nhom':<34}{'n':>4}{'3R WR':>8}{'3R exp':>9}{'tong':>8}")
for lbl, S in [("TAT CA", sig),
               ("clearance >= 3R (du cho)", [s for s in sig if s['clear'] >= 3.0]),
               ("clearance >= 4R (rong rai)", [s for s in sig if s['clear'] >= 4.0]),
               ("clearance < 3R (bi chan) -> BO", [s for s in sig if s['clear'] < 3.0])]:
    n, wr, exp, tot = ev(B, S, 3.0)
    print(f"  {lbl:<34}{n:>4}{wr:>7.0%}{exp:>+8.2f}R{tot:>+7.1f}R")

print("\n(2) SIET SL 2 gia (3R=6 gia) tren nhom clearance>=3R:")
S = [s for s in sig if s['clear'] >= 3.0]
for slw, rm in [(40, 3.0), (20, 3.0), (20, 2.0)]:
    n, wr, exp, tot = ev(B, S, rm, slw=slw)
    print(f"  SL {slw/10:.0f} gia @ {rm:.0f}R (={slw*rm/10:.0f} gia): n={n} WR{wr:.0%} exp{exp:+.2f}R tong{tot:+.1f}R")

print("\n(so chieu: Track A ca he @1.5R = +0.52R ; clean-KB1 @3R = +0.20R)")
print("=" * 92)
