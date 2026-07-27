#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Do nhay cua ConfluenceTol: 7/10/12/15 tick — edge cum>=2 co giu khi noi tol khong?
   + co cuu duoc tin hieu 20:30 (bat ho tro) khong?"""
import sys
from datetime import datetime
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em, research as R
TICK = em.TICK
B = em.load_m1(); pool = em.build_zones(B)


def with_cluster(B, pool, tol):
    raw = em.run(B, pool)
    for s in raw:
        zp = float(s['zone'].split()[-1]); t = s['dt']; seen = set()
        for z in pool:
            if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= tol:
                seen.add(round(z['price'] / TICK))
        s['cluster'] = len(seen)
    sig = em.dedup(raw)
    for s in sig: s.setdefault('cluster', 1)
    return sig


def wr(sigs, rm):
    tp = sl = 0
    for s in sigs:
        r = s['risk_t'] * TICK
        tpp = s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r
        o = R.hit_target(B, s['i'], s['side'], s['sl'], tpp)
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    return n, (tp / n if n else 0), ((tp * rm - sl) / n if n else 0)


ndays = len(set(b['dt'].date() for b in B))
print("=" * 90)
print("DO NHAY ConfluenceTol (gate cum>=2):")
print(f"  {'tol':>5}{'n_c2':>6}{'/ng':>6} | 2R WR/exp | 3R WR/exp | 20:30 pass?")
for tol in [7, 10, 12, 15, 20]:
    sig = with_cluster(B, pool, tol)
    c2 = [s for s in sig if s['cluster'] >= 2]
    n2, w2, e2 = wr(c2, 2.0); n3, w3, e3 = wr(c2, 3.0)
    p2030 = any(s['dt'].strftime('%m/%d') == '07/24' and s['dt'].hour == 20 and 28 <= s['dt'].minute <= 32 and s['cluster'] >= 2 for s in sig)
    print(f"  {tol:>5}{len(c2):>6}{len(c2)/ndays:>6.1f} | {w2:>3.0%}/{e2:+5.2f} | {w3:>3.0%}/{e3:+5.2f} | {p2030}")
print("=" * 90)
