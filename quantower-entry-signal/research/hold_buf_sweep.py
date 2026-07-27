#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chon buffer cho filter 'retest giu vung' (low khong xuyen qua vung > buf tick).
retrace<=100% <=> low>=zp (buf=0). Sweep buf 0..4 tick tren 1 thang, KB1 cum>=2, SL floor 4 gia."""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
em.SL_MIN_T = 40; em.SL_MAX_T = 60; em.RR = 1.5; em.NEXTZONE_MINR = 2.0
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


def ev(B, sub, rm):
    tp = sl = 0
    for s in sub:
        r = s['risk_t'] * TICK
        o = hit(B, s['i'], s['side'], s['sl'], s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r)
        tp += o == 'TP'; sl += o == 'SL'
    n = tp + sl
    return (tp / n if n else 0), ((tp * rm - sl) / n if n else 0)


B = em.load_m1(); pool = em.build_zones(B)
raw = em.run(B, pool)
for s in raw: s['cluster'] = clu(pool, s['dt'], float(s['zone'].split()[-1]))
sig = em.dedup(raw)
for s in sig: s.setdefault('cluster', 1)
kb1 = [s for s in sig if s['cluster'] >= 2 and s['scen'].startswith('1')]
for s in kb1:
    zp = float(s['zone'].split()[-1]); b = B[s['i']]
    s['slice'] = (zp - b['lo']) / TICK if s['side'] == 'LONG' else (b['hi'] - zp) / TICK

print(f"KB1 cum>=2, n={len(kb1)}.  Filter: giu lenh co slice <= buf (low khong xuyen vung qua buf tick)")
print(f"  {'buf(t)':>7}{'n giu':>7}{'1.5R WR':>9}{'1.5R exp':>10}{'3R WR':>8}{'3R exp':>9}")
for buf in [99, 0, 1, 2, 3, 4]:
    sub = [s for s in kb1 if s['slice'] <= buf]
    w1, e1 = ev(B, sub, 1.5); w3, e3 = ev(B, sub, 3.0)
    tag = "  (=hien tai, khong loc)" if buf == 99 else ("  <- retrace<=100%" if buf == 0 else "")
    print(f"  {buf:>7}{len(sub):>7}{w1:>8.0%}{e1:>+9.2f}R{w3:>7.0%}{e3:>+8.2f}R{tag}")
# 2 lenh
for tag, hh, mm in [("LENH1", 8, 3), ("LENH2", 18, 20)]:
    m = [s for s in kb1 if s['dt'].strftime('%m/%d') == '07/23' and s['dt'].hour == hh and abs(s['dt'].minute - mm) <= 1]
    if m: print(f"  {tag}: slice={m[0]['slice']:.0f}t  (buf<3 -> {'GIU' if m[0]['slice']<=2 else 'BO'})")
