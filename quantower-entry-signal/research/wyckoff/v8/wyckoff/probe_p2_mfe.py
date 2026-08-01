#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_p2_mfe.py — P2 (PLAN_KB_ABC.md §2.2/§5): probe MFE cho PLAY1 (cham->dao) tai vung HVN
tuan+ngay, TRUOC khi chot RR cho KB-A/KB-B. Day la HINH HOC (khong phai ket qua backtest):
MFE = quang duong thuan loi toi da tinh tu entry, TRONG PHIEN (khong qua dem, dung
eval_intraday.session_ends), quy doi theo R = risk cua tung tin hieu.

Chay: python3 probe_p2_mfe.py
"""
import sys, os, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
for p in (HERE, V8, WYCK, RESEARCH):
    if p not in sys.path:
        sys.path.insert(0, p)

import entry_dxfeed as E
import zones_corven as Z
import play_touch as P1
import eval_intraday as EI

TICK = 0.1
MONTHS = ('2026-05', '2026-06', '2026-07')


def mfe_of(B, s, sessions, starts):
    i, side, entry = s['i'], s['side'], s['entry']
    r = s['risk_t'] * TICK
    if r <= 0:
        return None
    end_idx = EI._end_idx(sessions, starts, i)
    if end_idx is None or end_idx <= i:
        return None
    best = 0.0
    for j in range(i + 1, end_idx + 1):
        b = B[j]
        fav = (b['hi'] - entry) if side == 'LONG' else (entry - b['lo'])
        if fav > best:
            best = fav
    return best / r


def report_dist(label, mfes):
    if not mfes:
        print(f"  {label}: n=0")
        return
    n = len(mfes)
    def pct(th):
        return sum(1 for m in mfes if m >= th) / n * 100
    print(f"  {label}: n={n}  med={st.median(mfes):.2f}R  "
          f"P(>=1.5R)={pct(1.5):.0f}%  P(>=2R)={pct(2.0):.0f}%  P(>=3R)={pct(3.0):.0f}%  P(>=4R)={pct(4.0):.0f}%")
    return dict(n=n, p15=pct(1.5), p20=pct(2.0), p30=pct(3.0), p40=pct(4.0))


def main():
    B = E.load_m1()
    sessions, starts = EI.session_ends(B)
    print(f"M1={len(B)} nen | {B[0]['dt']} -> {B[-1]['dt']} (UTC)")

    ser_w = Z.build_zone_series(B, mode='week', causal='closed')
    ser_d = Z.build_zone_series(B, mode='day', causal='closed')
    lookup_w = Z.zone_lookup_series(ser_w)
    lookup_d = Z.zone_lookup_series(ser_d)

    print("\n" + "=" * 100)
    print("P2 — Probe MFE cho PLAY1 (cham HVN -> confirm_m1) — HINH HOC, khong phai backtest")
    print("=" * 100)

    results = {}
    for tag, lookup in (("HVN TUAN (W_CLOSED)", lookup_w), ("HVN NGAY (D_CLOSED)", lookup_d)):
        sigs = P1.detect_play1(B, lookup, confirm_on=True)
        sigs_is = [s for s in sigs if s['ym'] in MONTHS]
        mfes = [mfe_of(B, s, sessions, starts) for s in sigs_is]
        mfes = [m for m in mfes if m is not None]
        print(f"\n-- {tag} -- (tong tin hieu PLAY1 in-sample = {len(sigs_is)})")
        d = report_dist(tag, mfes)
        results[tag] = d
        long_mfe = [mfe_of(B, s, sessions, starts) for s in sigs_is if s['side'] == 'LONG']
        short_mfe = [mfe_of(B, s, sessions, starts) for s in sigs_is if s['side'] == 'SHORT']
        long_mfe = [m for m in long_mfe if m is not None]
        short_mfe = [m for m in short_mfe if m is not None]
        report_dist(f"  {tag} :: LONG", long_mfe)
        report_dist(f"  {tag} :: SHORT", short_mfe)

    print("\n" + "=" * 100)
    print("KET LUAN P2 (theo nguong PLAN_KB_ABC.md §2.2/§6.9):")
    for tag, d in results.items():
        if d is None:
            continue
        verdict = "RR3 KHA THI (>=35%)" if d['p30'] >= 35 else ("RR THAP HON (<20%) -> de xuat RR1.5-2 cho PLAY1" if d['p30'] < 20 else "VUNG GIUA — can them thong tin khac de quyet")
        print(f"  {tag}: P(MFE>=3R)={d['p30']:.0f}%  => {verdict}")


if __name__ == '__main__':
    main()
