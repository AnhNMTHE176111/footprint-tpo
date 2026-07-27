#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRACK A — kiem tra phan hoi SL cua user:
  "dang fix cung SL 4 gia; phai dat DUOI cay nen; min 4, cap 6 (khong reject)."
Do phan bo risk hien tai + so sanh 3 cach dat SL tren cung tap tin hieu shipped (cum>=2):
  A. SHIPPED   : SL=min(anchor-2t, entry-40t); reject neu risk>60t
  B. CAP@6     : nhu A nhung CAP 60t thay vi reject (lay them lenh)
  C. UNDER-swing: anchor = swing low/high 5 nen gan nhat; floor 40t; CAP 60t (dat han duoi cum nen)
"""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
em.SL_MIN_T = 40; em.SL_MAX_T = 60; em.RR = 1.5; em.NEXTZONE_MINR = 2.0
CONFL_TOL = 7; RRV = 1.5


def hit_target(B, i, side, sl_px, tp_px):
    for j in range(i + 1, len(B)):
        b = B[j]
        sl = (b['lo'] <= sl_px) if side == 'LONG' else (b['hi'] >= sl_px)
        tp = (b['hi'] >= tp_px) if side == 'LONG' else (b['lo'] <= tp_px)
        if sl: return 'SL'
        if tp: return 'TP'
    return 'open'


def cluster_of(pool, t, zp):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def sl_for(B, s, mode):
    """tra (sl_px, risk_t, taken) theo mode."""
    i = s['i']; side = s['side']; entry = s['entry']
    anchor = s['anchor']                              # min(low,zone) / max(hi,zone) — nhu shipped
    swinglo = min(x['lo'] for x in B[max(0, i-4):i+1])
    swinghi = max(x['hi'] for x in B[max(0, i-4):i+1])
    if side == 'LONG':
        if mode == 'C': base = swinglo - em.SL_BUF_T * TICK
        else: base = anchor - em.SL_BUF_T * TICK
        sl = min(base, entry - 40 * TICK)            # duoi nen HOAC san 4 gia (lay xa hon)
        risk = (entry - sl) / TICK
    else:
        if mode == 'C': base = swinghi + em.SL_BUF_T * TICK
        else: base = anchor + em.SL_BUF_T * TICK
        sl = max(base, entry + 40 * TICK)
        risk = (sl - entry) / TICK
    if risk <= 0: return None, 0, False
    if risk > 60:
        if mode == 'A': return None, risk, False     # reject
        # cap 6 gia
        sl = entry - 60 * TICK if side == 'LONG' else entry + 60 * TICK
        risk = 60
    return sl, risk, True


B = em.load_m1(); pool = em.build_zones(B)
raw = em.run(B, pool)
for s in raw:
    s['cluster'] = cluster_of(pool, s['dt'], float(s['zone'].split()[-1]))
    # anchor da dung trong _emit: min(low,zone)/max(hi,zone)
    zp = float(s['zone'].split()[-1]); b = B[s['i']]
    s['anchor'] = min(b['lo'], zp) if s['side'] == 'LONG' else max(b['hi'], zp)
sig = em.dedup(raw)
for s in sig: s.setdefault('cluster', 1)
sig = [s for s in sig if s['cluster'] >= 2]

# phan bo risk hien tai
risks = [s['risk_t'] / 10 for s in sig]
at4 = sum(abs(r - 4.0) < 0.05 for r in risks)
print("=" * 92)
print(f"TRACK A — SL analysis tren tap shipped (cum>=2), n={len(sig)}")
print(f"  Risk hien tai: min {min(risks):.1f} / trung vi {st.median(risks):.1f} / max {max(risks):.1f} gia")
print(f"  So lenh dinh SAN 4.0 gia (structural <4 -> bi san day xuong): {at4}/{len(sig)} ({100*at4//len(sig)}%)")
print(f"  -> user dung: phan lon SL bam san 4 gia vi nen entry (nhip cham) nho, cach entry <4 gia.\n")

print(f"  {'cach dat SL':<34}{'n lay':>6}{'risk tv':>9}{'WR@1.5R':>9}{'exp':>8}{'tong R':>9}")
for mode, lbl in [('A', 'A. SHIPPED (reject >6 gia)'), ('B', 'B. CAP @6 gia (lay them lenh)'),
                  ('C', 'C. UNDER swing-low 5 nen, cap 6')]:
    taken = []
    for s in sig:
        slp, risk, ok = sl_for(B, s, mode)
        if not ok: continue
        r = risk * TICK
        tpp = s['entry'] + RRV * r if s['side'] == 'LONG' else s['entry'] - RRV * r
        o = hit_target(B, s['i'], s['side'], slp, tpp)
        taken.append((risk, o))
    clo = [t for t in taken if t[1] in ('TP', 'SL')]
    tp = sum(t[1] == 'TP' for t in taken); sl = sum(t[1] == 'SL' for t in taken)
    wr = tp / len(clo) if clo else 0; totR = tp * RRV - sl
    rtv = st.median([t[0] / 10 for t in taken]) if taken else 0
    print(f"  {lbl:<34}{len(taken):>6}{rtv:>8.1f}d{wr:>8.0%}{totR/len(clo) if clo else 0:>+8.2f}{totR:>+8.1f}R")
print("  (RRV=1.5; 'reject' = bo lenh khi cau truc doi SL>6 gia; cap = van vao voi SL=6 gia)")
print("=" * 92)
