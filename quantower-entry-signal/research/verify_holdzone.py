#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XAC MINH filter 'retest giu vung' tren TOAN indicator (KB1+KB2, cum>=2, SL floor4, RR1.5).
So OFF (RETEST_HOLD_T=999) vs ON (=0, shipped moi). KB2 phai khong doi (filter chi cham KB1)."""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
em.SL_MIN_T = 40; em.SL_MAX_T = 60; em.RR = 1.5; em.NEXTZONE_MINR = 2.0
CONFL_TOL = 7; RRV = 1.5


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


def build(B, pool):
    raw = em.run(B, pool)
    for s in raw: s['cluster'] = clu(pool, s['dt'], float(s['zone'].split()[-1]))
    sig = em.dedup(raw)
    for s in sig: s.setdefault('cluster', 1)
    sig = [s for s in sig if s['cluster'] >= 2]
    for s in sig:
        r = s['risk_t'] * TICK
        s['out'] = hit(B, s['i'], s['side'], s['sl'], s['entry'] + RRV * r if s['side'] == 'LONG' else s['entry'] - RRV * r)
        s['o3'] = hit(B, s['i'], s['side'], s['sl'], s['entry'] + 3 * r if s['side'] == 'LONG' else s['entry'] - 3 * r)
        s['kb'] = 'KB1' if s['scen'].startswith('1') else 'KB2'
    return sig


def rep(sig, rm='out'):
    clo = [s for s in sig if s[rm] in ('TP', 'SL')]
    tp = sum(s[rm] == 'TP' for s in sig); sl = sum(s[rm] == 'SL' for s in sig)
    mult = 1.5 if rm == 'out' else 3.0
    wr = tp / len(clo) if clo else 0; totR = tp * mult - sl
    return len(sig), tp, sl, wr, (totR / len(clo) if clo else 0), totR


B = em.load_m1(); pool = em.build_zones(B)
print("=" * 90)
print("XAC MINH filter 'retest GIU vung' — 1 thang, KB1+KB2, cum>=2, SL floor 4 gia, RR 1.5")
for hold, lbl in [(999, "OFF (cu — retest cho phep low xuyen vung)"), (0, "ON  (moi — retest phai giu vung)")]:
    em.RETEST_HOLD_T = hold
    sig = build(B, pool)
    n, tp, sl, wr, exp, totR = rep(sig, 'out')
    n3, tp3, sl3, wr3, exp3, totR3 = rep(sig, 'o3')
    k1 = [s for s in sig if s['kb'] == 'KB1']; k2 = [s for s in sig if s['kb'] == 'KB2']
    _, k1tp, k1sl, k1wr, _, k1R = rep(k1, 'out'); _, k2tp, k2sl, k2wr, _, k2R = rep(k2, 'out')
    print(f"\n[{lbl}]")
    print(f"  TONG: {n} lenh | @1.5R: WIN {tp} LOSS {sl} | WR {wr:.0%} | exp {exp:+.2f}R | tong {totR:+.1f}R")
    print(f"        @3R:  WIN {tp3} LOSS {sl3} | WR {wr3:.0%} | exp {exp3:+.2f}R | tong {totR3:+.1f}R")
    print(f"  KB1 pha&hoi : {len(k1):>2} lenh | WR {k1wr:.0%} ({k1tp}W/{k1sl}L) | {k1R:+.1f}R")
    print(f"  KB2 cham&dao: {len(k2):>2} lenh | WR {k2wr:.0%} ({k2tp}W/{k2sl}L) | {k2R:+.1f}R  (phai KHONG doi)")
print("=" * 90)
