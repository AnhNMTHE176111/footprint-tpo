#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
play_breakret.py — PLAY2 (CORVEN): pha vung (HVN tuan/ngay) -> hoi ve mep vung nhung GIU ->
nen xac nhan M1 THUAN huong pha -> vao. CORVEN_SPEC_V1.md §3 Play2, PLAN_KB_ABC.md §4.2.

State machine 1-per-zone (mo phong entry_dxfeed.run(): idle -> broke_up/broke_dn -> idle),
"edge" = GIA HVN (khac cbr_v6 dung bien box 8 nen). BREAK SACH (NoCounterSweep, tuy chon) goi
lai cbr_v6.counter_sweep() de giu parity co che voi KB1 goc.

ConfirmOn=True  -> nen VAO phai la confirm_m1 (dong dep, brat/wick chuan).
ConfirmOn=False -> dung dieu kien "resume" cu (dong vuot cuc tri nhip hoi + huong dung + than
                    >= resume_body) NHU cbr_v6/KB1 goc, de A/B xem confirm_m1 co tang EV khong.
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
for p in (HERE, V8, WYCK, RESEARCH):
    if p not in sys.path:
        sys.path.insert(0, p)

import cbr_v6 as V6
import confirm_m1 as CM

TICK = 0.1


def _entry_ok(b, prior, up, confirm_on, resume_body=0.35):
    if confirm_on:
        return CM.confirm_long(b) if up else CM.confirm_short(b)
    if up:
        return b['c'] > prior['hi'] and b['up'] and b['brat'] >= resume_body
    return b['c'] < prior['lo'] and b['dn'] and b['brat'] >= resume_body


def detect_play2(B, zone_lookup, wait_bars=12, pull_min=0.60, pull_max=1.00, hold_tol_ticks=2,
                  buf_ticks=2, sl_floor_pts=3.0, sl_cap_pts=7.0, bvsa=2.0, bbody=0.50,
                  confirm_on=True, resume_body=0.35,
                  clean_break=True, clean_look=20, clean_win=5, clean_close=0.50,
                  vol_floor=20, warmup=20):
    raw = []
    N = len(B)
    zone_state = {}
    for i in range(warmup, N):
        b = B[i]
        z = zone_lookup(b['dt'])
        if z is None:
            continue
        _, _, hvn_list = z
        if not (b['v'] >= vol_floor and b['since_gap'] >= warmup and b['vma'] >= vol_floor * 0.6):
            continue
        buf = buf_ticks * TICK
        for zp, _cnt, _ratio in hvn_list:
            key = round(zp, 1)
            st = zone_state.get(key)
            if st is None:
                st = dict(state='idle', brk_bar=-999, peak=None, since=None)
                zone_state[key] = st

            if st['state'] == 'idle':
                up = b['c'] > zp + buf and b['vratio'] >= bvsa and b['brat'] >= bbody and b['up']
                dn = b['c'] < zp - buf and b['vratio'] >= bvsa and b['brat'] >= bbody and b['dn']
                if not (up or dn):
                    continue
                if clean_break and V6.counter_sweep(B, i, up, clean_look, clean_win, clean_close):
                    continue
                st['state'] = 'broke_up' if up else 'broke_dn'
                st['brk_bar'] = i
                st['peak'] = b['hi'] if up else b['lo']
                st['since'] = i
                continue

            up = (st['state'] == 'broke_up')
            edge = zp
            if i - st['brk_bar'] > wait_bars:
                st['state'] = 'idle'
                continue
            if (b['c'] < edge - hold_tol_ticks * TICK) if up else (b['c'] > edge + hold_tol_ticks * TICK):
                st['state'] = 'idle'
                continue
            if (b['hi'] > st['peak']) if up else (b['lo'] < st['peak']):
                st['peak'] = b['hi'] if up else b['lo']
                st['since'] = i
                continue
            if i < st['since'] + 2:
                continue
            pseg = B[st['since'] + 1:i + 1]
            pext = min(x['lo'] for x in pseg) if up else max(x['hi'] for x in pseg)
            leg = (st['peak'] - edge) if up else (edge - st['peak'])
            depth = (st['peak'] - pext) if up else (pext - st['peak'])
            retr = depth / leg if leg > 0 else 0
            held = (pext >= edge - hold_tol_ticks * TICK) if up else (pext <= edge + hold_tol_ticks * TICK)
            if not (pull_min <= retr <= pull_max and held):
                continue
            if not _entry_ok(b, B[i - 1], up, confirm_on, resume_body):
                continue
            entry = b['c']
            sl = pext - buf if up else pext + buf
            risk = (entry - sl) / TICK if up else (sl - entry) / TICK
            risk_pts = risk * TICK
            if risk_pts < sl_floor_pts:
                sl = entry - sl_floor_pts if up else entry + sl_floor_pts
                risk = sl_floor_pts / TICK
                risk_pts = sl_floor_pts
            if risk_pts > sl_cap_pts or risk <= 0:
                st['state'] = 'idle'
                continue
            raw.append(dict(i=i, dt=b['dt'], ym=b['ym'], side=('LONG' if up else 'SHORT'),
                             entry=entry, sl=sl, risk_t=risk, zone=zp))
            st['state'] = 'idle'
    return _dedup(raw)


def _dedup(raw, min_gap_bars=6):
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= min_gap_bars for m in out):
            continue
        out.append(s)
    return out
