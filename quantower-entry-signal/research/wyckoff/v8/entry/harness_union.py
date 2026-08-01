#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/entry/harness_union.py — cau hoi nguoi dung 2026-08-01: "giu nhu cu + THEM quan
diem CORVEN (HVN tuan/ngay + VWAP tuan/ngay) thi n/WR/R co tang khong?"
KHAC thi nghiem truoc (harness_corven.py = THAY THE pool cu bang pool CORVEN, da KILL):
o day pool = pool CU UNION pool CORVEN, CONFIG GIU NGUYEN nhu P0 (E.make(VOL_FLOOR=..),
MIN_CONFL=2 mac dinh, RR=1.5, khong bat CONFIRM_ON) — dung LAI warm-up/MONTHS cua P0
de so duoc voi cot TRUOC trong RESULTS_ENTRY_ZONES.md.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)
sys.path.insert(0, os.path.join(WYCK, 'v7'))
sys.path.insert(0, HERE)

import entry_dxfeed as E    # noqa: E402
import report as RPT        # noqa: E402
import pool_corven as PC    # noqa: E402
import run_union as RU      # noqa: E402
from harness import warmup_cutoff, MONTHS  # noqa: E402


def build_union_pool(B, min_ratio=1.5):
    """Tra (static_pool, old_pool, hvn_pool). PC.build_pool_corven mutate B them
    b['vwap_week']/b['vwap_day'] (can cho RU.dedup_union doc hop luu VWAP moi)."""
    old_pool = E.build_zones(B)
    hvn_pool = PC.build_pool_corven(B, min_ratio=min_ratio)
    return old_pool + hvn_pool, old_pool, hvn_pool


def run_union_baseline(label="P-UNION: pool CU + them HVN tuan/ngay + VWAP tuan/ngay CORVEN "
                              "(config GIU NGUYEN nhu TRUOC)"):
    B = E.load_m1()
    static_pool, old_pool, hvn_pool = build_union_pool(B)
    C = E.make(VOL_FLOOR=E.VOLFLOOR_FROZEN)   # y het config P0 (MIN_CONFL=2, RR=1.5, ...)

    raw = RU.run_union(B, static_pool, C)
    sig = RU.dedup_union(raw, static_pool, B, C)
    sig = [s for s in sig if s['ym'] in MONTHS]

    cutoff = warmup_cutoff(B)
    n_before_cut = len(sig)
    if cutoff is not None:
        sig = [s for s in sig if s['dt'].date() >= cutoff]
    n_dropped = n_before_cut - len(sig)

    for s in sig:
        _, r = E.sim(B, s, 'tp3', C['RR'])
        s['r'] = r

    print("=" * 100)
    print(label)
    print(f"  pool cu={len(old_pool)} vung | + HVN tuan/ngay={len(hvn_pool)} vung | "
          f"tong pool tinh={len(static_pool)} | + 3 VWAP dong (phien/tuan/ngay)")
    print(f"  warm-up: bo {n_dropped} tin hieu dau cua so scored (cutoff={cutoff}), con {len(sig)}")
    print("-" * 100)

    d_all = RPT.line("TONG", sig, MONTHS)
    longs = [s for s in sig if s['side'] == 'LONG']
    shorts = [s for s in sig if s['side'] == 'SHORT']
    d_long = RPT.line("LONG", longs, MONTHS)
    d_short = RPT.line("SHORT", shorts, MONTHS)
    play1 = [s for s in sig if s['scen'].startswith('2')]
    play2 = [s for s in sig if s['scen'].startswith('1')]
    d_p1 = RPT.line("PLAY1 cham-dao", play1, MONTHS)
    d_p2 = RPT.line("PLAY2 pha-hoi", play2, MONTHS)
    print("-" * 100)

    return dict(B=B, static_pool=static_pool, old_pool=old_pool, hvn_pool=hvn_pool, C=C,
                sig=sig, all=d_all, long=d_long, short=d_short, play1=d_p1, play2=d_p2,
                cutoff=cutoff, n_dropped=n_dropped)


if __name__ == '__main__':
    run_union_baseline()
