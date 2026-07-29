#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROBE #2 (GD4 — chi DO HINH HOC, KHONG backtest chien luoc, KHONG co WR).
================================================================================
Tra loi 3 cau hoi thiet ke cho KB3 (scalp bien<->bien trong range):
  1. R bien thien: neu SL dat ngoai cuc tri nen cham (+2 tick) va TP la bien DOI DIEN
     (tru dem), thi RR KHA DUNG phan bo the nao? -> chon nguong "RR toi thieu" bang so.
  2. Gate "thuan xu huong" cua v6 (close vs close[-480], tol 1.0 gia) nhan gia tri gi
     tai cac lan cham bien? -> KB3 nghich da, phai biet gate nay giet bao nhieu.
  3. Bien range co hop luu voi vung D-1/session (VAH/VAL/POC/dinh/day) khong, va bao nhieu %?
Dung lai range detector cua probe_range_feasibility.py.
Chay: python3 probe_kb3_geometry.py
"""
import sys, statistics as st
from collections import defaultdict
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/wyckoff/v7")
import entry_dxfeed as E
from probe_range_feasibility import scan_ranges, touches

TICK = E.TICK
W37 = ('2026-05', '2026-06', '2026-07')
TREND_LB, TREND_TOL = 480, 1.0


def add_trend(B):
    for i, b in enumerate(B):
        if i >= TREND_LB:
            d = b['c'] - B[i - TREND_LB]['c']
            b['trend6'] = 1 if d > TREND_TOL else (-1 if d < -TREND_TOL else 0)
        else:
            b['trend6'] = 0


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(len(v) * p))] if v else 0.0


def probe(B, pool, minw, maxw, buf_t=2, tp_buf_t=2):
    R = scan_ranges(B, minw, maxw)
    R = [r for r in R if r['ym'] in W37 and r['valid_at'] is not None]
    ev = []
    for r in R:
        seg = B[r['i']:r['j']]
        rhi = max(x['hi'] for x in seg)
        rlo = min(x['lo'] for x in seg)
        width = rhi - rlo
        tol = max(0.3, 0.15 * width)
        post = seg[r['valid_at']:]
        off = r['i'] + r['valid_at']
        for up_edge in (True, False):
            edge = rhi if up_edge else rlo
            for k in touches(post, edge, tol, up_edge):
                b = post[k]
                gi = off + k
                entry = b['c']
                if up_edge:                                    # cham bien TREN -> scalp SHORT ve bien duoi
                    sl = max(b['hi'], edge) + buf_t * TICK
                    risk = sl - entry
                    tp = rlo + tp_buf_t * TICK
                    room = entry - tp
                    side = -1
                else:
                    sl = min(b['lo'], edge) - buf_t * TICK
                    risk = entry - sl
                    tp = rhi - tp_buf_t * TICK
                    room = tp - entry
                    side = +1
                if risk <= 0:
                    continue
                ev.append(dict(ym=b['ym'], side=side, risk=risk, room=room,
                               rr=room / risk, width=width, trend=b['trend6'],
                               vwap_ok=(b['c'] <= b['vwap']) if side < 0 else (b['c'] >= b['vwap']),
                               i=gi, edge=edge))
    print(f"--- range minw={minw} maxw={maxw}: n_range={len(R)}  n_lan_cham(sau XN)={len(ev)}")
    if not ev:
        return
    bym = defaultdict(int)
    for e in ev:
        bym[e['ym']] += 1
    print("    theo thang: " + " ".join(f"{m[-2:]}={bym[m]}" for m in W37))
    print(f"    R (gia)        p10={q([e['risk'] for e in ev],.1):.2f} med={st.median([e['risk'] for e in ev]):.2f} p90={q([e['risk'] for e in ev],.9):.2f}")
    print(f"    room->bien doi dien (gia) med={st.median([e['room'] for e in ev]):.2f}")
    rr = [e['rr'] for e in ev]
    print(f"    RR kha dung    p10={q(rr,.1):.2f} p25={q(rr,.25):.2f} med={st.median(rr):.2f} p75={q(rr,.75):.2f} p90={q(rr,.9):.2f}")
    for thr in (1.0, 1.5, 2.0, 2.5, 3.0):
        k = sum(1 for x in rr if x >= thr)
        print(f"      so lan cham co RR >= {thr:.1f}: {k:4d}  ({100*k/len(rr):.0f}%)")
    tc = defaultdict(int)
    for e in ev:
        tc[e['trend']] += 1
    print(f"    gate THUAN xu huong v6 tai nen cham: trend=+1:{tc[1]}  trend=0:{tc[0]}  trend=-1:{tc[-1]}")
    agree = sum(1 for e in ev if e['trend'] == e['side'])
    print(f"      trong do 'thuan huong scalp' (trend==side) = {agree} ({100*agree/len(ev):.0f}%)"
          f" -> neu ap gate v6 nguyen ban, KB3 con n={agree}")
    zero = sum(1 for e in ev if e['trend'] == 0)
    print(f"      neu chi cho KB3 chay khi trend==0: n={zero} ({100*zero/len(ev):.0f}%)")
    vok = sum(1 for e in ev if e['vwap_ok'])
    print(f"    dung phia VWAP (theo huong scalp): {vok} ({100*vok/len(ev):.0f}%)")
    # hop luu bien range voi zone pool
    for tolp in (0.3, 0.7):
        hit = 0
        for e in ev:
            t = B[e['i']]['dt']
            if any(z['ready'] <= t <= z['expire'] and abs(z['price'] - e['edge']) <= tolp for z in pool):
                hit += 1
        print(f"    bien range hop luu voi >=1 vung (D-1/session) trong +-{tolp} gia: "
              f"{hit} ({100*hit/len(ev):.0f}%)")


if __name__ == '__main__':
    B = E.load_m1()
    add_trend(B)
    pool = E.build_zones(B)
    print(f"dxFeed M1={len(B)} nen | zones={len(pool)}\n")
    for mn, mx in ((2.0, 6.0), (2.0, 8.0), (3.0, 12.0)):
        probe(B, pool, mn, mx)
        print()
