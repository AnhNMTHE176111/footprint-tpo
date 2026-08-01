#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/runner/measure.py — P0: do cot TRUOC (bang chinh harness se dung do cot SAU) cho ca hai
nhanh cua RunnerSignal.cs v5 (CBR/PLAY2 va QUAY_DAU/PLAY1), tach rieng + gop portfolio.

Nguon dung lai KHONG SUA (read-only theo PLAN session): cbr_hvn.py (copy nguyen ban cua
cbr_v6.py, dat trong chinh thu muc nay nen duoc phep sua sau nay), imp_reversal_sweep.py
(QUAY_DAU exact replica cua RunnerSignal.cs::ScanReversal), v7/report.py (line/mdd/_half_split).

Chay: python3 measure.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)
sys.path.insert(0, WYCK)
sys.path.insert(0, os.path.join(WYCK, 'v7'))
sys.path.insert(0, HERE)

import cbr_hvn as CBR                # copy cua cbr_v6.py — nam trong v8/runner, duoc phep sua
import imp_reversal_sweep as REV      # QUAY_DAU exact replica (READ-ONLY, chi goi ham)
import report as R                    # v7/report.py (READ-ONLY)

TICK = REV.TICK


# ============================================================================
# CBR / PLAY2 — dung thang cbr_hvn.scan(), output da co 'dt'/'ym'/'r'/'side' dung schema report.py
# ============================================================================
def cbr_signals(C=None):
    B = CBR.E.load_m1()
    vf = CBR.E.calc_volfloor(B)
    CBR.prepare(B)
    C = C if C is not None else CBR.cfg()
    return B, CBR.scan(B, C, vf, None)


# ============================================================================
# QUAY_DAU / PLAY1 — adapter: detect() (READ-ONLY) tra list thieu 'r'/'ym'/outcome, tu tinh
# bang rv.hit() (READ-ONLY) + rr, roi doi sang schema cua report.line() (can 'dt','ym','r').
# ============================================================================
def rev_signals(rr=None, **kw):
    B = REV.bars()
    rr = rr if rr is not None else REV.LIVE['rr']
    sigs = REV.in_window(B, REV.detect(B, **kw))
    out = []
    for s in sigs:
        r_ = s['risk_t'] * TICK
        tgt = s['entry'] + rr * r_ if s['side'] == 'LONG' else s['entry'] - rr * r_
        o = REV.rv.hit(B, s['i'], s['side'], s['sl'], tgt)
        if o not in ('TP', 'SL', 'amb'):
            continue
        r_val = rr if o == 'TP' else -1.0
        s2 = dict(s)
        s2['ym'] = s['dt'].strftime('%Y-%m')
        s2['r'] = r_val
        s2['outcome'] = o
        out.append(s2)
    return B, out


def split_side(S):
    return [s for s in S if s['side'] == 'LONG'], [s for s in S if s['side'] == 'SHORT']


def p0_table():
    print("=" * 118)
    print("P0 — GOLDEN + cot TRUOC (nguon: dxFeed 27-7, 5-7/2026 — CUNG 1 cua so ca 2 nhanh)")
    print("=" * 118)

    print("\n[CBR / PLAY2] — cbr_hvn.py, cfg() mac dinh (khop RunnerSignal.cs v5: RR3, khong CleanBreak)")
    _, S_cbr = cbr_signals()
    d_cbr = R.line("CBR TRUOC (range noi bo, gop)", S_cbr)
    lc, sc = split_side(S_cbr)
    R.line("  LONG", lc)
    R.line("  SHORT", sc)

    print("\n[QUAY_DAU / PLAY1] — imp_reversal_sweep.detect(), LIVE params (khop ScanReversal, KHONG loc phien chet)")
    _, S_rev = rev_signals()
    d_rev = R.line("QUAY_DAU TRUOC (VWAP phien, gop)", S_rev)
    lr, sr = split_side(S_rev)
    R.line("  LONG", lr)
    R.line("  SHORT", sr)

    print("\n[PORTFOLIO] — gop theo thoi gian (CANH BAO: khong mo phong Dedup gop 2 nhanh, xem BASELINE.md §1)")
    S_all = sorted(S_cbr + S_rev, key=lambda s: s['dt'])
    R.line("CBR+QUAY_DAU TRUOC (gop theo tg)", S_all)

    print("\n" + "=" * 118)
    print("Doi chieu voi tham chieu da biet (khong tu tin ke qua khop, chi de nguoi doc kiem):")
    print("  CBR    ky vong n=55 WR=47.3% tong=+49.0R EV=+0.891 MDD=6.0R (cbr_v6.py chay truc tiep)")
    print("  QUAY_DAU ky vong n=27 WR=55.6%(56%) EV=+0.389 net=+10.5R (BASELINE.md, imp_reversal_sweep truc tiep)")


if __name__ == '__main__':
    p0_table()
