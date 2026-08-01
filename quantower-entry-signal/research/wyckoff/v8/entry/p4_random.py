#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P4 — doi chung ngau nhien (BAT BUOC, PLAN §Phan3-P4). Dich HVN tuan/ngay +-3 GIA
(=+-30 tick, TICK=0.1), 5 seed, so EV that vs EV ngau nhien. VWAP KHONG dich (VWAP la
cong thuc tinh dong, khong phai "vi tri vung" chon tuy y — cai dang kiem la vi tri
HVN co mang thong tin khong, giong phuong phap BACKTEST-ZONES-V2.md da dung).
Chi chay tren SAU-B (MinConfl=1 RR1.5 confirm=off) — cau hinh DUY NHAT dat n>=25
trong P2/P3 (xem harness_corven.py CONFIGS).
"""
import os
import sys
import random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import harness_corven as HC  # noqa: E402
import entry_dxfeed as E     # noqa: E402
import run_corven as RC      # noqa: E402
from harness import warmup_cutoff, MONTHS  # noqa: E402

SHIFT_GIA = 3.0
SEEDS = [1, 2, 3, 4, 5]


def shifted_pool(hvn_pool, seed):
    rnd = random.Random(seed)
    out = []
    for z in hvn_pool:
        z2 = dict(z)
        z2['price'] = z['price'] + rnd.uniform(-SHIFT_GIA, SHIFT_GIA)
        out.append(z2)
    return out


def ev_of(sig_list):
    if not sig_list:
        return None, 0
    tot = sum(s['r'] for s in sig_list)
    return tot / len(sig_list), len(sig_list)


def run_once(hvn_pool, B, C):
    raw = RC.run_corven(B, hvn_pool, C)
    sig = RC.dedup_corven(raw, hvn_pool, B, C)
    sig = [s for s in sig if s['ym'] in MONTHS]
    cutoff = warmup_cutoff(B)
    if cutoff is not None:
        sig = [s for s in sig if s['dt'].date() >= cutoff]
    for s in sig:
        _, r = E.sim(B, s, 'tp3', C['RR'])
        s['r'] = r
    return sig


if __name__ == '__main__':
    B = HC.get_B()
    C = HC.default_cfg(MIN_CONFL=1, RR=1.5, CONFIRM_ON=False)
    real_pool = HC.get_pool(min_ratio=C['MIN_RATIO'])

    real_sig = run_once(real_pool, B, C)
    ev_real, n_real = ev_of(real_sig)
    print(f"THAT (SAU-B): n={n_real} EV={ev_real:+.3f}  tong={sum(s['r'] for s in real_sig):+.1f}R")

    print(f"\nNgau nhien (dich HVN +-{SHIFT_GIA} gia, {len(SEEDS)} seed):")
    evs = []
    for sd in SEEDS:
        pool_r = shifted_pool(real_pool, sd)
        sig_r = run_once(pool_r, B, C)
        ev_r, n_r = ev_of(sig_r)
        evs.append(ev_r if ev_r is not None else 0.0)
        print(f"  seed={sd}  n={n_r:3d}  EV={'n/a' if ev_r is None else f'{ev_r:+.3f}'}  "
              f"tong={sum(s['r'] for s in sig_r):+.1f}R")

    ev_null_mean = sum(evs) / len(evs)
    gap = (ev_real or 0.0) - ev_null_mean
    print(f"\nEV(that)={ev_real:+.3f}  EV(ngau nhien TB 5 seed)={ev_null_mean:+.3f}  "
          f"chenh={gap:+.3f}")
    if gap >= 0.25:
        verdict = "PASS (chenh >= +0.25R)"
    elif gap < 0.10:
        verdict = "KILL — vi tri vung KHONG mang thong tin cho signal nay (chenh < +0.10R)"
    else:
        verdict = "KHONG RO RANG (0.10 <= chenh < 0.25)"
    print(f"=> {verdict}")
