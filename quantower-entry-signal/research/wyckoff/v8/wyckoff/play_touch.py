#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
play_touch.py — PLAY1 (CORVEN): cham vung (HVN tuan/ngay) -> nen xac nhan M1 NGUOC huong
cham -> vao. RR co dinh (truyen tu ngoai). CORVEN_SPEC_V1.md §3 Play1, PLAN_KB_ABC.md §4.2.

Gate giu theo spec:
  R2  — vung bi cham phai o r2_frac (mac dinh 25%) bien tren/duoi cua range r2_win nen gan nhat
  R10 — nen tu choi phai CO volume (vratio >= vsa_min), cam dung "vol thap" lam tin hieu dao
  Xac nhan M1 — confirm_m1.confirm_long/confirm_short (co the tat qua confirm_on=False, khi do
  chi doi huong dong nen dung + R10, KHONG doi hinh dang — dung cho A/B ConfirmOn).

KHONG goi lai imp_reversal_sweep.detect() truc tiep (no neo VWAP phien, khac vung HVN) —
nhung GIU cung logic hinh hoc (touch/tol, dedup, SL neo cuc tri+buffer) cho parity ve chat luong.
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
for p in (HERE, V8, WYCK, RESEARCH):
    if p not in sys.path:
        sys.path.insert(0, p)

import confirm_m1 as CM

TICK = 0.1


def _confirm_ok(bj, side, confirm_on, vsa_min):
    if confirm_on:
        shape_ok = CM.confirm_short(bj) if side == 'SHORT' else CM.confirm_long(bj)
    else:
        shape_ok = (bj['c'] < bj['o']) if side == 'SHORT' else (bj['c'] > bj['o'])
    return shape_ok and bj['vratio'] >= vsa_min


def detect_play1(B, zone_lookup, tol_ticks=12, vsa_min=1.8, confirm_bars=3, confirm_on=True,
                  r2_frac=0.25, r2_win=60, buf_ticks=2, sl_floor_pts=0.5, sl_cap_pts=7.0,
                  vol_floor=20, warmup=20):
    """zone_lookup(dt) -> (fr, to, hvn_list) tu zones_corven.zone_lookup_series. hvn_list =
    list[(price, count, ratio)] tu verify_zones_v2.find_hvn."""
    tol = tol_ticks * TICK
    raw = []
    N = len(B)
    for i in range(max(warmup, r2_win) + 1, N):
        b = B[i]
        if not (b['v'] >= vol_floor and b['since_gap'] >= warmup and b['vma'] >= vol_floor * 0.6):
            continue
        z = zone_lookup(b['dt'])
        if z is None:
            continue
        _, _, hvn_list = z
        if not hvn_list:
            continue
        win = B[i - r2_win:i]
        hi60 = max(x['hi'] for x in win)
        lo60 = min(x['lo'] for x in win)
        span60 = hi60 - lo60
        if span60 <= 0:
            continue
        for zp, _cnt, _ratio in hvn_list:
            near_top = zp >= hi60 - r2_frac * span60
            near_bot = zp <= lo60 + r2_frac * span60
            if near_top and b['hi'] >= zp - tol:
                _try_confirm(raw, B, i, zp, 'SHORT', confirm_bars, confirm_on, vsa_min,
                             buf_ticks, sl_floor_pts, sl_cap_pts)
            if near_bot and b['lo'] <= zp + tol:
                _try_confirm(raw, B, i, zp, 'LONG', confirm_bars, confirm_on, vsa_min,
                             buf_ticks, sl_floor_pts, sl_cap_pts)
    return _dedup(raw)


def _try_confirm(raw, B, i, zp, side, confirm_bars, confirm_on, vsa_min, buf_ticks, sl_floor_pts, sl_cap_pts):
    N = len(B)
    extreme = B[i]['hi'] if side == 'SHORT' else B[i]['lo']
    for k in range(0, confirm_bars + 1):
        j = i + k
        if j >= N:
            return
        bj = B[j]
        extreme = max(extreme, bj['hi']) if side == 'SHORT' else min(extreme, bj['lo'])
        if _confirm_ok(bj, side, confirm_on, vsa_min):
            entry = bj['c']
            buf = buf_ticks * TICK
            if side == 'SHORT':
                sl = extreme + buf
                risk = (sl - entry) / TICK
            else:
                sl = extreme - buf
                risk = (entry - sl) / TICK
            risk_pts = risk * TICK
            if risk_pts < sl_floor_pts or risk_pts > sl_cap_pts or risk <= 0:
                return
            raw.append(dict(i=j, dt=bj['dt'], ym=bj['ym'], side=side, entry=entry, sl=sl,
                             risk_t=risk, zone=zp, touch_i=i))
            return


def _dedup(raw, min_gap_bars=6):
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= min_gap_bars for m in out):
            continue
        out.append(s)
    return out
