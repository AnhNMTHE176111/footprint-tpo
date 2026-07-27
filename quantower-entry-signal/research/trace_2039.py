#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trace forward-scan cua break 20:30 (07/22) — vi sao khong ra entry 20:39?"""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
import entry_cbr as C
TICK = em.TICK
B = em.load_m1()


def idx(day, hh, mm):
    return next((k for k, b in enumerate(B) if b['dt'].strftime('%m/%d') == day and b['dt'].hour == hh and b['dt'].minute == mm), None)


i = idx('07/22', 20, 30)
b = B[i]
win = B[i - C.RANGE_LEN:i]
rhi = max(x['hi'] for x in win); rlo = min(x['lo'] for x in win)
edge = rhi; peak = b['hi']; since = i
print(f"break 20:30 idx={i} edge(rhi)={edge:.1f} peak={peak:.1f} span={(rhi-rlo)/TICK:.0f}t")
for j in range(i + 1, min(len(B), i + 1 + C.WAIT_BARS)):
    bj = B[j]
    g = em.gate(bj)
    back = (bj['c'] < edge - C.HOLD_TOL_T * TICK)
    pseg = B[since + 1:j + 1]
    pull_ext = min(x['lo'] for x in pseg) if pseg else None
    leg = peak - edge
    depth = (peak - pull_ext) if pull_ext else 0
    retr = depth / leg if leg > 0 else 0
    held = pull_ext >= edge - C.HOLD_TOL_T * TICK if pull_ext else False
    resume = bj['c'] > B[j - 1]['hi'] and bj['c'] > bj['o'] and bj['brat'] >= C.RESUME_BODY
    fire = (j >= since + 2 and C.PULL_MIN <= retr <= C.PULL_MAX and held and resume)
    print(f"  {bj['dt']:%H:%M} c{bj['c']:.1f} hi{bj['hi']:.1f} peak{peak:.1f} since{B[since]['dt']:%H:%M} "
          f"pull_ext{pull_ext if pull_ext else 0:.1f} retr{retr:.0%} held{held} "
          f"resume{resume}(c>{B[j-1]['hi']:.1f}?{bj['c']>B[j-1]['hi']},br{bj['brat']*100:.0f}%) "
          f"j>=since+2:{j>=since+2} {'<<FIRE' if fire else ''}"
          + ('  [gate-off BREAK]' if not g else '') + ('  [back-in-range BREAK]' if back else ''))
    if not g or back:
        print("   ==> loop BREAK here"); break
    if bj['hi'] > peak:
        peak = bj['hi']; since = j
