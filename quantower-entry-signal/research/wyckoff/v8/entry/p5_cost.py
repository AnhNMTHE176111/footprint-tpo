#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P5 — quet chi phi giao dich 0->8 tick/luot cho SAU-B (config duy nhat qua P2/P3+P4
o muc n>=25). Chi phi tru theo R: moi lenh mat them cost_tick/risk_t(tick) cua CHINH no
(vi 1R = risk_t tick cua lenh do, khong phai hang so)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import harness_corven as HC  # noqa: E402
import entry_dxfeed as E     # noqa: E402
import run_corven as RC      # noqa: E402
from harness import warmup_cutoff, MONTHS  # noqa: E402
from p4_random import run_once  # noqa: E402

if __name__ == '__main__':
    B = HC.get_B()
    C = HC.default_cfg(MIN_CONFL=1, RR=1.5, CONFIRM_ON=False)
    pool = HC.get_pool(min_ratio=C['MIN_RATIO'])
    sig = run_once(pool, B, C)
    n = len(sig)
    print(f"SAU-B  n={n}")
    for cost_tick in range(0, 9):
        rs = [s['r'] - cost_tick / s['risk_t'] for s in sig]
        tot = sum(rs)
        ev = tot / n if n else 0.0
        print(f"  cost={cost_tick} tick/luot  EV={ev:+.3f}  tong={tot:+.1f}R")
