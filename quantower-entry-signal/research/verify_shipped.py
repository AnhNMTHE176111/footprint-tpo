#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERIFY cau hinh DA SHIP: cluster>=2 + SL floor 4d + RR 1.5. So sanh voi cau hinh CU."""
import sys, statistics as st
from datetime import datetime, timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em, research as R
TICK = em.TICK


def with_cluster(B, pool):
    raw = em.run(B, pool); TOL = em.ARM_DIST_T and 7
    for s in raw:
        zp = float(s['zone'].split()[-1]); t = s['dt']; seen = set()
        for z in pool:
            if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= 7:
                seen.add(round(z['price'] / TICK))
        s['cluster'] = len(seen)
    sig = em.dedup(raw)
    for s in sig: s.setdefault('cluster', 1)
    return sig


def report(B, pool, label):
    outs = {}
    for tag, (floor, rr, gate) in {
        "CU  (trigger>=2, SL2d, RR3)": (20, 3.0, 'confl'),
        "MOI (cluster>=2, SL4d, RR1.5)": (40, 1.5, 'cluster'),
    }.items():
        em.SL_MIN_T = floor; em.RR = rr
        sig = with_cluster(B, pool)
        sub = [s for s in sig if (s['confl'] if gate == 'confl' else s.get('cluster', 1)) >= 2]
        tp = sl = 0; rs = []
        for s in sub:
            o = R.hit_target(B, s['i'], s['side'], s['sl'], s['tp3'])   # tp3 = entry +- RR*risk
            if o == 'TP': tp += 1; rs.append(rr)
            elif o == 'SL': sl += 1; rs.append(-1.0)
        n = tp + sl
        ndays = len(set(s['dt'].date() for s in sig))
        wr = tp / n if n else 0
        exp = sum(rs) / n if n else 0
        medsl = st.median([s['risk_t'] for s in sub]) / 10 if sub else 0
        outs[tag] = (len(sub), ndays, len(sub) / max(ndays, 1), wr, exp, medsl, tp, sl)
    em.SL_MIN_T = 20; em.RR = 3.0
    print(f"\n### {label}")
    print(f"  {'cau hinh':<32}{'n':>4}{'/ngay':>7} | {'WR':>5} {'exp(R)':>7} | medSL | ket qua")
    for tag, (n, nd, perday, wr, exp, msl, tp, sl) in outs.items():
        print(f"  {tag:<32}{n:>4}{perday:>7.1f} | {wr:>4.0%} {exp:>+7.2f} | {msl:>3.1f}d  | {tp}TP {sl}SL")


# 28 ngay
B = em.load_m1(); pool = em.build_zones(B)
report(B, pool, "28 NGAY (fp-m1-1-month, 6/26->7/25)")

# 6-thang LIQUID (thang 7 front-month) — nap qua backtest_6month
import types
src = open("/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/backtest_6month.py").read().replace("\nmain()\n", "\n")
bt = types.ModuleType("bt6"); bt.__dict__.update(sys=sys, em=em, R=R, TICK=TICK)
exec(compile(src, "bt6", "exec"), bt.__dict__)
B6 = bt.load_m1_6m(); pool6 = bt.build_zones_6m(B6)
Bjul = [b for b in B6 if b['dt'] >= datetime(2026, 7, 1)]
# scan tren toan bo (vung can lich su) nhung chi danh gia tin hieu thang 7
print("\n(thang 7 = front-month thanh khoan that; vung dung tu ca 6 thang)")


def report_window(B, pool, cutoff, label):
    outs = {}
    for tag, (floor, rr, gate) in {
        "CU  (trigger>=2, SL2d, RR3)": (20, 3.0, 'confl'),
        "MOI (cluster>=2, SL4d, RR1.5)": (40, 1.5, 'cluster'),
    }.items():
        em.SL_MIN_T = floor; em.RR = rr
        sig = with_cluster(B, pool)
        sig = [s for s in sig if s['dt'] >= cutoff]
        sub = [s for s in sig if (s['confl'] if gate == 'confl' else s.get('cluster', 1)) >= 2]
        tp = sl = 0; rs = []
        for s in sub:
            o = R.hit_target(B, s['i'], s['side'], s['sl'], s['tp3'])
            if o == 'TP': tp += 1; rs.append(rr)
            elif o == 'SL': sl += 1; rs.append(-1.0)
        n = tp + sl; nd = len(set(s['dt'].date() for s in sig))
        outs[tag] = (len(sub), nd, len(sub) / max(nd, 1), tp / n if n else 0, sum(rs) / n if n else 0, tp, sl)
    em.SL_MIN_T = 20; em.RR = 3.0
    print(f"\n### {label}")
    print(f"  {'cau hinh':<32}{'n':>4}{'/ngay':>7} | {'WR':>5} {'exp(R)':>7} | ket qua")
    for tag, (n, nd, pd, wr, exp, tp, sl) in outs.items():
        print(f"  {tag:<32}{n:>4}{pd:>7.1f} | {wr:>4.0%} {exp:>+7.2f} | {tp}TP {sl}SL")


report_window(B6, pool6, datetime(2026, 7, 1), "THANG 7 FRONT-MONTH (out-of-window phan lon)")
print("\nDONE")
