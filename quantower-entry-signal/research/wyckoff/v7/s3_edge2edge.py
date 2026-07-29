#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s3_edge2edge.py — KB3: scalp bien<->bien trong range da xac nhan (SPEC_V7_3KB.md §6).
================================================================================
KHONG dung ten "kb3" trong bat ky ten module nao khac ngoai file nay (canh bao §1.3 —
research/kb3_climax_break.py cu dung "KB3" nghia KHAC, khong lien quan).

Dung LAI ha tang GD6 (KHONG viet lai): features.range_struct_scan (state machine §4.3),
features.session_bias_series (bias TPO §2), engine.hit_v7 (SPEC §6.5.1 R bien thien),
loaders.py (session/IB), report.py (line/partition/sweep dinh dang chuan).

R model (§6.5) — R BIEN THIEN, khac han KB1/KB2:
  SHORT (fade bien tren): entry=c[i]; sl_raw=max(hi[i],rhi)+2tick; R=max(sl_raw-entry,SlFloor);
                          sl=entry+R; tp=rlo+TpBuf*tick; room=entry-tp; bo neu room/R < MinRr
  LONG: guong lai.
"""
import sys, os, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_dxfeed as E
import cbr_v6 as V6
import engine, features, report, loaders

TICK = E.TICK
MONTHS = ('2026-05', '2026-06', '2026-07')


def cfg(**kw):
    c = dict(
        Kb3SlFloorPts=1.5, Kb3MinRr=1.5, Kb3TpBufTicks=2, Kb3MaxHoldBars=60,
        Kb3VsaMin=1.2, Kb3WickFrac=0.35, Kb3ExtremeWin=20,
        Kb3TrendMode=0,             # 0=khong loc, 1=chi thuan (trend==side), 2=chi trend==0 (BI BAC, xem SPEC)
        Kb3RequireConfluence=False, Kb3ConfluenceTolPts=0.7,
        DEAD=False, DEAD_FROM=2, DEAD_TO=8,     # phien chet UTC — MIEN mac dinh (§6.6)
        LIQ=True, LIQ_K=0.75,
        RangeTouchMin=2,            # doi => phai goi lai features.range_struct_scan voi P['TOUCH'] khac
        SEP=3, CPOS_SHORT=0.45, CPOS_LONG=0.55, BODY_MIN=0.25,
    )
    c.update(kw)
    return c


# ------------------------------------------------------------------ Buoc 1: cham bien (ARM+ENTRY cung nen)
def find_touch_events(B, states, C, range_P=None):
    """Voi moi nen i ma range dang VALID va i>valid_bar: kiem cham bien tren/duoi. Tra ve MOI
    lan cham (chua loc chat luong) kem: cac co chat luong (bool), R model, va thong tin de tra
    cuu dead_at (pha nguoc lenh) sau nay. Day la tap 'raw' dung cho ca thong ke hinh hoc VA
    backtest (khong trung lap logic)."""
    P = dict(features.DEFAULT_P, **(range_P or {}))
    ew = C['Kb3ExtremeWin']
    out = []
    last_touch = {}  # i0 -> {up: last_i, dn: last_i} de tach 2 lan cham (SEP)
    for i, s in enumerate(states):
        if s is None or s['state'] != 'VALID' or s['valid_bar'] is None or i <= s['valid_bar']:
            continue
        b = B[i]
        i0 = s['i0']
        rhi, rlo = s['rhi'], s['rlo']
        width = rhi - rlo
        tol = max(P['TOLMIN'], P['TOLF'] * width)
        lt = last_touch.setdefault(i0, {})
        touch_up = b['hi'] >= rhi - tol and (i - lt.get('up', -999) >= C['SEP'])
        touch_dn = b['lo'] <= rlo + tol and (i - lt.get('dn', -999) >= C['SEP'])
        if touch_up:
            lt['up'] = i
            out.append(_build_event(B, i, i0, s['valid_bar'], rhi, rlo, width, tol, up_edge=True, C=C, ew=ew))
        if touch_dn:
            lt['dn'] = i
            out.append(_build_event(B, i, i0, s['valid_bar'], rhi, rlo, width, tol, up_edge=False, C=C, ew=ew))
    return out


def _build_event(B, i, i0, valid_bar, rhi, rlo, width, tol, up_edge, C, ew):
    b = B[i]
    rng = b['rng'] if b['rng'] > 0 else 1e-9
    lo_k = max(0, i - ew + 1)
    if up_edge:
        side = 'SHORT'
        cpos_ok = b['cpos'] <= C['CPOS_SHORT']
        wick_ok = b['uw'] >= C['Kb3WickFrac'] * rng
        extreme_ok = b['hi'] == max(x['hi'] for x in B[lo_k:i + 1])
        entry = b['c']
        sl_raw = max(b['hi'], rhi) + 2 * TICK
        R = max(sl_raw - entry, C['Kb3SlFloorPts'])
        sl = entry + R
        tp = rlo + C['Kb3TpBufTicks'] * TICK
        room = entry - tp
        edge, opp_edge = rhi, rlo
    else:
        side = 'LONG'
        cpos_ok = b['cpos'] >= C['CPOS_LONG']
        wick_ok = b['lw'] >= C['Kb3WickFrac'] * rng
        extreme_ok = b['lo'] == min(x['lo'] for x in B[lo_k:i + 1])
        entry = b['c']
        sl_raw = min(b['lo'], rlo) - 2 * TICK
        R = max(entry - sl_raw, C['Kb3SlFloorPts'])
        sl = entry - R
        tp = rhi - C['Kb3TpBufTicks'] * TICK
        room = tp - entry
        edge, opp_edge = rlo, rhi

    body_ok = b['brat'] >= C['BODY_MIN']
    vsa_ok = b['vratio'] >= C['Kb3VsaMin']
    rr_avail = room / R if R > 1e-9 else 0.0
    quality_ok = cpos_ok and wick_ok and body_ok and vsa_ok and extreme_ok
    liq_ok = (not C['LIQ']) or b.get('liqratio', 1.0) >= C['LIQ_K']
    dead_hour_ok = (not C['DEAD']) or not (C['DEAD_FROM'] <= b['dt'].hour < C['DEAD_TO'])
    return dict(i=i, dt=b['dt'], ym=b['ym'], i0=i0, valid_bar=valid_bar, side=side,
                edge=edge, opp_edge=opp_edge, width=width, tol=tol,
                entry=entry, sl=sl, tp=tp, risk_t=R / TICK, room=room, rr_avail=rr_avail,
                cpos_ok=cpos_ok, wick_ok=wick_ok, body_ok=body_ok, vsa_ok=vsa_ok,
                extreme_ok=extreme_ok, quality_ok=quality_ok, liq_ok=liq_ok,
                dead_hour_ok=dead_hour_ok, trend=b.get('trend', 0), hour=b['dt'].hour,
                vratio=b['vratio'])


# ------------------------------------------------------------------ dead_at: range vo NGUOC lenh
def find_dead_at(states, ev, cap_bars=200):
    """Tu nen ev['i'], tim nen j dau tien (cung range i0) ma state chuyen sang BREAKING theo
    huong NGUOC voi lenh (SHORT so bien tren -> ban tren; up-break la nguoc; LONG so bien duoi
    -> nguoc la down-break). Tra ve None neu khong xay ra trong pham vi cap_bars/truoc khi
    range doi i0."""
    i0 = ev['i0']
    against_dir = 1 if ev['side'] == 'SHORT' else -1     # SHORT so bien tren: nguoc = pha LEN (dir=1)
    n = len(states)
    end = min(n, ev['i'] + 1 + cap_bars)
    for j in range(ev['i'] + 1, end):
        s = states[j]
        if s is None or s.get('i0') != i0:
            return None                      # range da bi thay the (i0 khac) -> khong con theo doi duoc
        if s['state'] == 'BREAKING' and s.get('brk_bar') == j and s.get('brk_dir') == against_dir:
            return j
    return None


# ------------------------------------------------------------------ danh gia (dung engine.hit_v7)
def evaluate(B, events, C):
    out = []
    states = C['_states']
    for ev in events:
        dead_at = find_dead_at(states, ev, cap_bars=C['Kb3MaxHoldBars'] + 5)
        o, r_extra = engine.hit_v7(B, ev['i'], ev['side'], ev['sl'], ev['tp'], ev['entry'],
                                    maxbars=C['Kb3MaxHoldBars'], dead_at=dead_at)
        if o == 'open':
            continue
        e2 = dict(ev)
        e2['outcome'] = o
        e2['rr_real'] = ev['rr_avail']
        e2['r'] = ev['rr_avail'] if o == 'TP' else (-1.0 if o == 'SL' else r_extra)
        e2['dead_at'] = dead_at
        out.append(e2)
    return out


def base_filter(events, C):
    """'Ban tran' (SPEC §6.10 buoc 3): chi chat luong nen tu choi + Kb3MinRr + thanh khoan."""
    return [e for e in events
            if e['quality_ok'] and e['liq_ok'] and e['rr_avail'] >= C['Kb3MinRr']]


def dedup_touch(events):
    """1 lan cham = 1 tin hieu (da tach boi SEP trong find_touch_events); dedup bo sung theo
    (i0, side) qua neu 2 canh tranh cung 1 nen (hiem, phong ho)."""
    seen = set()
    out = []
    for e in sorted(events, key=lambda x: x['i']):
        k = (e['i'], e['side'])
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out


def post_months(sig):
    return [s for s in sig if s['ym'] in MONTHS]
