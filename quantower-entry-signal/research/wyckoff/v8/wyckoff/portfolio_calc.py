#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""portfolio_calc.py — tinh so KB-A gop / KB-B gop / portfolio KB-A+KB-B (cong gop, CHUA
router 1-vi-the) cho bang cuoi RESULTS_KB_AB.md. Script tam, mot lan."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
V7 = os.path.join(WYCK, 'v7')
for p in (HERE, V8, WYCK, RESEARCH, V7):
    if p not in sys.path:
        sys.path.insert(0, p)

import entry_dxfeed as E
import zones_corven as Z
import play_touch as P1
import play_breakret as P2
import eval_intraday as EI
import report

RR = 3.0
MONTHS = ('2026-05', '2026-06', '2026-07')


def run(B, lookup, sessions, starts):
    s1 = [s for s in P1.detect_play1(B, lookup, confirm_on=True) if s['ym'] in MONTHS]
    s2 = [s for s in P2.detect_play2(B, lookup, confirm_on=True) if s['ym'] in MONTHS]
    e1 = EI.evaluate(B, s1, RR, sessions, starts)
    e2 = EI.evaluate(B, s2, RR, sessions, starts)
    return e1, e2


def main():
    B = E.load_m1()
    sessions, starts = EI.session_ends(B)
    ser_w = Z.build_zone_series(B, mode='week', causal='closed')
    ser_d = Z.build_zone_series(B, mode='day', causal='closed')
    lk_w = Z.zone_lookup_series(ser_w)
    lk_d = Z.zone_lookup_series(ser_d)

    e1_wc, e2_wc = run(B, lk_w, sessions, starts)
    e1_dc, e2_dc = run(B, lk_d, sessions, starts)
    kb_a = sorted(e1_wc + e2_wc, key=lambda x: x['dt'])
    kb_b = sorted(e1_dc + e2_dc, key=lambda x: x['dt'])
    portfolio = sorted(kb_a + kb_b, key=lambda x: x['dt'])

    print("KB-A gop:")
    report.line("KB-A", kb_a)
    print("KB-B gop:")
    report.line("KB-B", kb_b)
    print("Portfolio KB-A+KB-B (cong gop theo thoi gian, CHUA router 1-vi-the):")
    report.line("Portfolio", portfolio)

    # them LONG/SHORT cho portfolio
    L = [s for s in portfolio if s['side'] == 'LONG']
    Sh = [s for s in portfolio if s['side'] == 'SHORT']
    report.line("Portfolio :: LONG", L)
    report.line("Portfolio :: SHORT", Sh)


if __name__ == '__main__':
    main()
