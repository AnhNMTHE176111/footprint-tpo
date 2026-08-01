#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/entry/harness_corven.py — do EntrySignal SAU khi doi tang vung sang CORVEN (P2-P5).
Dung LAI cung nguon/cung quy tac warm-up voi P0 (harness.py) de TRUOC/SAU so duoc.
"""
import os
import sys
import copy
import random

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)
sys.path.insert(0, os.path.join(WYCK, 'v7'))
sys.path.insert(0, WYCK)
sys.path.insert(0, V8)
sys.path.insert(0, HERE)

import entry_dxfeed as E   # noqa: E402
import report as RPT       # noqa: E402
import zones_corven as ZC  # noqa: E402
import pool_corven as PC   # noqa: E402
import run_corven as RC    # noqa: E402
from harness import warmup_cutoff, MONTHS  # noqa: E402

_CACHE = {}


def get_B():
    if 'B' not in _CACHE:
        _CACHE['B'] = E.load_m1()
    return _CACHE['B']


def get_pool(min_ratio=1.5):
    key = ('pool', min_ratio)
    if key not in _CACHE:
        B = get_B()
        _CACHE[key] = PC.build_pool_corven(B, min_ratio=min_ratio)
    return _CACHE[key]


def default_cfg(**kw):
    c = dict(RETEST_HOLD_T=0, SL_FLOOR_T=40, SL_CAP_T=60, RR=1.5, NEXTZONE_MINR=2.0,
              EXTEND=True, MIN_CONFL=2, COOLDOWN=15, VOL_FLOOR=E.VOLFLOOR_FROZEN,
              TREND_ON=False, KB2_CLIMAX=True, CONFIRM_ON=False, CAUSAL='closed', MIN_RATIO=1.5)
    c.update(kw)
    return c


def run_config(label, C, verbose=True):
    B = get_B()
    hvn_pool = get_pool(min_ratio=C['MIN_RATIO'])
    if C['CAUSAL'] == 'running':
        # xay lai pool rieng cho che do running (P1: khong nhan qua ~ chi dung de doi chieu,
        # KHONG dung lam so PASS/KILL chinh thuc)
        key = ('pool_running', C['MIN_RATIO'])
        if key not in _CACHE:
            B2 = get_B()
            days = ZC.group_days(B2)
            weeks = ZC.group_weeks(B2, days)
            ser_w = ZC.build_zone_series(B2, mode='week', causal='running')
            ser_d = ZC.build_zone_series(B2, mode='day', causal='running')
            hp = (PC._series_to_static_zones(ser_w, "HVN tuan(run)", 75, B2[-1]['dt'])
                  + PC._series_to_static_zones(ser_d, "HVN ngay(run)", 65, B2[-1]['dt']))
            _CACHE[key] = hp
        hvn_pool = _CACHE[key]

    raw = RC.run_corven(B, hvn_pool, C)
    sig = RC.dedup_corven(raw, hvn_pool, B, C)
    sig = [s for s in sig if s['ym'] in MONTHS]

    cutoff = warmup_cutoff(B)
    n_before = len(sig)
    if cutoff is not None:
        sig = [s for s in sig if s['dt'].date() >= cutoff]
    n_dropped = n_before - len(sig)

    for s in sig:
        _, r = E.sim(B, s, 'tp3', C['RR'])
        s['r'] = r

    if verbose:
        print("=" * 100)
        print(f"{label}  | config: MIN_CONFL={C['MIN_CONFL']} RR={C['RR']} CONFIRM_ON={C['CONFIRM_ON']} "
              f"CAUSAL={C['CAUSAL']} MIN_RATIO={C['MIN_RATIO']}")
        print(f"  pool CORVEN = {len(hvn_pool)} vung tinh (HVN tuan+ngay) + 2 VWAP dong | "
              f"warm-up bo {n_dropped} tin hieu (cutoff={cutoff})")
        print("-" * 100)
        d_all = RPT.line("TONG", sig, MONTHS)
        longs = [s for s in sig if s['side'] == 'LONG']
        shorts = [s for s in sig if s['side'] == 'SHORT']
        RPT.line("LONG", longs, MONTHS)
        RPT.line("SHORT", shorts, MONTHS)
        play1 = [s for s in sig if s['scen'].startswith('2')]
        play2 = [s for s in sig if s['scen'].startswith('1')]
        RPT.line("PLAY1 cham-dao", play1, MONTHS)
        RPT.line("PLAY2 pha-hoi", play2, MONTHS)
        print("-" * 100)
        return dict(sig=sig, all=d_all, longs=longs, shorts=shorts, play1=play1, play2=play2, C=C, hvn_pool=hvn_pool)
    return dict(sig=sig, C=C, hvn_pool=hvn_pool)


CONFIGS = [
    ("SAU-A  MinConfl=2 RR1.5 confirm=off (chi doi pool, sat TRUOC nhat)", default_cfg(MIN_CONFL=2, RR=1.5, CONFIRM_ON=False)),
    ("SAU-B  MinConfl=1 RR1.5 confirm=off", default_cfg(MIN_CONFL=1, RR=1.5, CONFIRM_ON=False)),
    ("SAU-C  MinConfl=2 RR3.0 confirm=off (RR theo CORVEN_SPEC)", default_cfg(MIN_CONFL=2, RR=3.0, CONFIRM_ON=False)),
    ("SAU-D  MinConfl=2 RR1.5 confirm=ON", default_cfg(MIN_CONFL=2, RR=1.5, CONFIRM_ON=True)),
    ("SAU-E  MinConfl=2 RR3.0 confirm=ON (dung SPEC day du)", default_cfg(MIN_CONFL=2, RR=3.0, CONFIRM_ON=True)),
    ("SAU-F  MinConfl=1 RR3.0 confirm=ON", default_cfg(MIN_CONFL=1, RR=3.0, CONFIRM_ON=True)),
    ("SAU-G  nhu E nhung CAUSAL=running (P1: CHUA xac nhan nhan qua cho live!)", default_cfg(MIN_CONFL=2, RR=3.0, CONFIRM_ON=True, CAUSAL='running')),
]

if __name__ == '__main__':
    results = {}
    for label, C in CONFIGS:
        results[label] = run_config(label, C)
