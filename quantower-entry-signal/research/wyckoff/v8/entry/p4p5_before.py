#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Doi chung ngau nhien + cost sweep cho cot TRUOC (pool cu), de bang cuoi co du du lieu
2 cot ma khong phai bo trong. Dung LAI dung config/warmup cua P0 (harness.py)."""
import os
import sys
import random

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)
sys.path.insert(0, HERE)
import entry_dxfeed as E   # noqa: E402
from harness import warmup_cutoff, MONTHS  # noqa: E402

SHIFT_GIA = 3.0
SEEDS = [1, 2, 3, 4, 5]


def run_once(B, pool, C):
    raw = E.run(B, pool, C)
    sig = E.dedup(raw, pool, C)
    sig = [s for s in sig if s['ym'] in MONTHS]
    cutoff = warmup_cutoff(B)
    if cutoff is not None:
        sig = [s for s in sig if s['dt'].date() >= cutoff]
    for s in sig:
        _, r = E.sim(B, s, 'tp3', C['RR'])
        s['r'] = r
    return sig


if __name__ == '__main__':
    B = E.load_m1()
    pool = E.build_zones(B)
    C = E.make(VOL_FLOOR=E.VOLFLOOR_FROZEN)

    real_sig = run_once(B, pool, C)
    n_real = len(real_sig)
    ev_real = sum(s['r'] for s in real_sig) / n_real
    print(f"THAT (pool cu): n={n_real} EV={ev_real:+.3f}")

    print(f"\nNgau nhien (dich MOI vung +-{SHIFT_GIA} gia, {len(SEEDS)} seed):")
    evs = []
    for sd in SEEDS:
        rnd = random.Random(sd)
        pool_r = [dict(z, price=z['price'] + rnd.uniform(-SHIFT_GIA, SHIFT_GIA)) for z in pool]
        sig_r = run_once(B, pool_r, C)
        n_r = len(sig_r)
        ev_r = sum(s['r'] for s in sig_r) / n_r if n_r else 0.0
        evs.append(ev_r)
        print(f"  seed={sd}  n={n_r:3d}  EV={ev_r:+.3f}")
    ev_null_mean = sum(evs) / len(evs)
    print(f"\nEV(that)={ev_real:+.3f}  EV(ngau nhien TB)={ev_null_mean:+.3f}  chenh={ev_real-ev_null_mean:+.3f}")

    print(f"\nCost sweep 0-8 tick (pool cu, n={n_real}):")
    for cost_tick in range(0, 9):
        rs = [s['r'] - cost_tick / s['risk_t'] for s in real_sig]
        ev = sum(rs) / n_real
        print(f"  cost={cost_tick} tick  EV={ev:+.3f}  tong={sum(rs):+.1f}R")
