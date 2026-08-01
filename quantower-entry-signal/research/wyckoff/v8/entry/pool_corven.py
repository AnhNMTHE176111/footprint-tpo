#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/entry/pool_corven.py — dung zones_corven.py (READ-ONLY) de dung POOL vung CORVEN
(HVN tuan + HVN ngay + VWAP tuan + VWAP ngay) o dang tuong thich voi engine EntrySignal.

P1 da kiem: causal='closed' TRUNG KHIT khi cat chuoi (nhan qua that). causal='running'
LECH khi cat chuoi (bug that trong zones_corven.py: group_days() gan ngay cuoi = het du
lieu lam ngay 'da dong', nen chay tren du lieu bi cat giua ngay se doc ca du lieu dang
hinh thanh cua CHINH ngay do). Vi vay module nay CHI dung causal='closed' — an toan da
xac nhan. Xem RESULTS_ENTRY_ZONES.md muc "bug phat hien o file dung chung".
"""
import os
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)
sys.path.insert(0, WYCK)
sys.path.insert(0, V8)

import zones_corven as ZC   # noqa: E402

FAR_FUTURE = None  # set khi biet B[-1]['dt']


def _series_to_static_zones(series, kind_label, strength, last_dt):
    """Chuyen (eff_from, fr, to, hvn_list) -> list zone dict {price,kind,strength,ready,expire}.
    Vung hieu luc [eff_from_k, eff_from_{k+1}) — dung dung logic 'chot lai moi ky' cua §3.2."""
    zones = []
    for k in range(len(series)):
        eff_from, fr, to, hvn = series[k]
        expire = series[k + 1][0] if k + 1 < len(series) else last_dt + timedelta(days=1)
        for price, _cnt, ratio in hvn:
            zones.append(dict(price=price, kind=f"{kind_label} x{ratio:.1f}",
                               strength=strength, ready=eff_from, expire=expire))
    return zones


def build_pool_corven(B, min_ratio=1.5):
    """Tra (hvn_pool, ) va GAN b['vwap_week']/b['vwap_day'] vao tung bar cua B (mutate in-place).
    hvn_pool = list zone dict {price,kind,strength,ready,expire} cho HVN tuan + HVN ngay,
    CHI causal='closed' (an toan). Dung de truyen vao run_corven()/dedup_corven()."""
    last_dt = B[-1]['dt']
    days = ZC.group_days(B)
    weeks = ZC.group_weeks(B, days)

    ser_w = ZC.build_zone_series(B, mode='week', causal='closed')
    ser_d = ZC.build_zone_series(B, mode='day', causal='closed')
    # sweep min_ratio ap dung xuyen suot ca 2 khung (P1: plateau, khong nhay cam trong 5-7/2026)
    if min_ratio != 1.5:
        ser_w = [(ef, fr, to, ZC.hvn_of(B, fr, to, min_ratio=min_ratio)) for ef, fr, to, _ in ser_w]
        ser_d = [(ef, fr, to, ZC.hvn_of(B, fr, to, min_ratio=min_ratio)) for ef, fr, to, _ in ser_d]

    hvn_pool = (_series_to_static_zones(ser_w, "HVN tuan", 75, last_dt)
                + _series_to_static_zones(ser_d, "HVN ngay", 65, last_dt))

    vwap_w = ZC.vwap_series(B, [(w[0][0], w[-1][1]) for w in weeks])
    vwap_d = ZC.vwap_series(B, days)
    for i, b in enumerate(B):
        b['vwap_week'] = vwap_w[i]
        b['vwap_day'] = vwap_d[i]

    return hvn_pool
