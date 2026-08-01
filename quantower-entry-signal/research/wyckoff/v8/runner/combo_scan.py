#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
combo_scan.py — CORVEN UNION: GIU NGUYEN CBR (range noi bo) + QUAY_DAU (VWAP phien) y nguyen
nhu v5 shipped, CONG THEM tin hieu neo HVN/VWAP tuan+ngay (CORVEN) nhu MOT NGUON BO SUNG
(khong thay the, khong xoa nhanh cu). Cau hoi can tra loi: giu ca 2 (cu + CORVEN) cung luc co
lam TANG so lenh / winrate / tong R so voi chi dung nhanh cu khong?

Merge o muc RAW (truoc dedup/cooldown), roi ap DUY NHAT 1 lan dedup(6 nen)+cooldown(15 nen)
theo TUNG NHANH (CBR rieng, QUAY_DAU rieng) — dung dung y nghia "1 co che phat hien tin hieu
danh cho ca nhanh, nhieu nguon vung dua vao roi loc trung theo bar+side" (giong cach 1 indicator
that se lam neu ban them nguon vung ma khong doi engine dedup/cooldown).

Nguon dung lai KHONG SUA: zone_engine.py (bars/build_zone_lookup/LIVE1), cbr_hvn.py (run/run_zone/
dedup/cooldown/post/evaluate/hit/cfg/MONTHS), entry_dxfeed.py (VSA_MA/WARMUP_AFTER_GAP).

Chay: python3 combo_scan.py
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
sys.path.insert(0, V8)
sys.path.insert(0, HERE)

import entry_dxfeed as E
import zone_engine as ZE
import cbr_hvn as CBR

B = ZE.bars()
vf = ZE.VOLFLOOR_FROZEN
C = CBR.cfg()
TICK = ZE.TICK

zone_w = ZE.build_zone_lookup(B, mode='week', causal='closed', include_vwap=True)
zone_d = ZE.build_zone_lookup(B, mode='day', causal='closed', include_vwap=True)


# ============================================================================
# CBR / PLAY2 — union cua range noi bo (run) + HVN/VWAP tuan (run_zone) + ngay (run_zone)
# ============================================================================
def cbr_before():
    return CBR.scan(B, C, vf, None)


def cbr_combo():
    raw = CBR.run(B, C, vf, None) + CBR.run_zone(B, C, vf, zone_w) + CBR.run_zone(B, C, vf, zone_d)
    return CBR.evaluate(B, CBR.post(CBR.cooldown(CBR.dedup(raw), C['COOL']), C), C)


# ============================================================================
# QUAY_DAU / PLAY1 — union cua VWAP phien (sess_raw, ban sao imp_reversal_sweep.detect() tren
# CUNG B/index voi zone de gop RAW duoc) + HVN/VWAP tuan (zone_raw) + ngay (zone_raw)
# ============================================================================
def sess_raw(B, vf=ZE.VOLFLOOR_FROZEN):
    P = ZE.LIVE1
    tol = P['tol_ticks'] * TICK
    cpos_lo, cpos_hi = 0.5 - P['cpos_h'], 0.5 + P['cpos_h']
    raw = []
    for i in range(E.VSA_MA + 2, len(B)):
        b = B[i]
        if not (b['v'] >= vf and b['since_gap'] >= E.WARMUP_AFTER_GAP and b['vma'] >= vf * 0.6):
            continue
        rng = b['rng']
        if rng <= 0:
            continue
        vw = b['vwap']
        touch_up = b['hi'] >= vw - tol
        rej_short = (b['uw'] >= P['wick_frac'] * rng and b['cpos'] <= cpos_lo and b['c'] < vw
                     and b['brat'] >= P['body_min'] and b['vratio'] >= P['vsa_conf'])
        touch_dn = b['lo'] <= vw + tol
        rej_long = (b['lw'] >= P['wick_frac'] * rng and b['cpos'] >= cpos_hi and b['c'] > vw
                    and b['brat'] >= P['body_min'] and b['vratio'] >= P['vsa_conf'])
        appro_up = appro_dn = False
        for k in range(max(0, i - P['approach_bars']), i):
            if B[k]['c'] < vw:
                appro_up = True
            if B[k]['c'] > vw:
                appro_dn = True
        side = 0
        anchor = 0.0
        if touch_up and rej_short and appro_up:
            side = -1
            anchor = max(b['hi'], vw)
        elif touch_dn and rej_long and appro_dn:
            side = 1
            anchor = min(b['lo'], vw)
        if side == 0:
            continue
        if P['trend_on'] and b['trend'] != side:
            continue
        entry = b['c']
        if side > 0:
            sl = anchor - P['sl_buf_t'] * TICK
            risk = (entry - sl) / TICK
        else:
            sl = anchor + P['sl_buf_t'] * TICK
            risk = (sl - entry) / TICK
        if risk <= 5 or risk > P['sl_cap_t']:
            continue
        raw.append(dict(i=i, dt=b['dt'], ym=b['ym'], side=('LONG' if side > 0 else 'SHORT'),
                         entry=entry, sl=sl, risk_t=risk, hour=b['dt'].hour))
    return raw


def zone_raw(B, zone_at_fn, vf=ZE.VOLFLOOR_FROZEN, **kw):
    """Ban sao PHAN LOI cua ZE.play1_raw() — GIU NGUYEN toan bo dieu kien, chi KHONG ap
    dedup/cooldown o cuoi (de gop chung voi sess_raw/zone khac roi dedup 1 lan duy nhat)."""
    P = dict(ZE.LIVE1)
    P.update(kw)
    tol = P['tol_ticks'] * TICK
    cpos_lo, cpos_hi = 0.5 - P['cpos_h'], 0.5 + P['cpos_h']
    N = len(B)
    raw = []
    for i in range(E.VSA_MA + 2, N - (1 if P['confirm_on'] else 0)):
        b = B[i]
        if not (b['v'] >= vf and b['since_gap'] >= E.WARMUP_AFTER_GAP and b['vma'] >= vf * 0.6):
            continue
        rng = b['rng']
        if rng <= 0:
            continue
        zps = zone_at_fn(i)
        if not zps:
            continue
        lo_k = max(0, i - P['r2_lookback'])
        window = B[lo_k:i]
        if len(window) < 10:
            continue
        loc_lo = min(x['lo'] for x in window)
        loc_hi = max(x['hi'] for x in window)
        span = loc_hi - loc_lo
        if span <= 0:
            continue
        for zp in zps:
            touch_up = b['hi'] >= zp - tol
            touch_dn = b['lo'] <= zp + tol
            rej_short = (b['uw'] >= P['wick_frac'] * rng and b['cpos'] <= cpos_lo and b['c'] < zp
                         and b['brat'] >= P['body_min'] and b['vratio'] >= P['vsa_conf'])
            rej_long = (b['lw'] >= P['wick_frac'] * rng and b['cpos'] >= cpos_hi and b['c'] > zp
                        and b['brat'] >= P['body_min'] and b['vratio'] >= P['vsa_conf'])
            appro_up = appro_dn = False
            for k in range(max(0, i - P['approach_bars']), i):
                if B[k]['c'] < zp:
                    appro_up = True
                if B[k]['c'] > zp:
                    appro_dn = True
            side = 0
            anchor = 0.0
            if touch_up and rej_short and appro_up:
                side = -1
                anchor = max(b['hi'], zp + tol)
            elif touch_dn and rej_long and appro_dn:
                side = 1
                anchor = min(b['lo'], zp - tol)
            if side == 0:
                continue
            pos = (zp - loc_lo) / span
            if side > 0 and pos > P['r2_frac']:
                continue
            if side < 0 and pos < (1 - P['r2_frac']):
                continue
            if P['trend_on'] and b['trend'] != side:
                continue
            entry_bar = b
            entry_i = i
            if P['confirm_on']:
                nb = B[i + 1]
                if not (nb['v'] >= vf and nb['since_gap'] >= E.WARMUP_AFTER_GAP):
                    continue
                confirm_ok = (nb['c'] > b['c']) if side > 0 else (nb['c'] < b['c'])
                if not confirm_ok:
                    continue
                entry_bar = nb
                entry_i = i + 1
            entry = entry_bar['c']
            if side > 0:
                sl = anchor - P['sl_buf_t'] * TICK
                risk = (entry - sl) / TICK
            else:
                sl = anchor + P['sl_buf_t'] * TICK
                risk = (sl - entry) / TICK
            if risk <= 5 or risk > P['sl_cap_t']:
                continue
            raw.append(dict(i=entry_i, dt=entry_bar['dt'], ym=entry_bar['ym'],
                             side=('LONG' if side > 0 else 'SHORT'), entry=entry, sl=sl,
                             risk_t=risk, hour=entry_bar['dt'].hour))
    return raw


def evaluate_rev(B, sig, rr):
    out = []
    for s in sig:
        r_ = s['risk_t'] * TICK
        tgt = s['entry'] + rr * r_ if s['side'] == 'LONG' else s['entry'] - rr * r_
        o, _ = CBR.hit(B, s['i'], s['side'], s['sl'], tgt)
        if o not in ('TP', 'SL'):
            continue
        s2 = dict(s)
        s2['r'] = rr if o == 'TP' else -1.0
        s2['outcome'] = o
        out.append(s2)
    return out


def rev_before():
    raw = sess_raw(B, vf)
    sig = [s for s in CBR.cooldown(CBR.dedup(raw), ZE.LIVE1['cooldown']) if s['ym'] in CBR.MONTHS]
    return evaluate_rev(B, sig, rr=1.5)


def rev_combo():
    raw = sess_raw(B, vf) + zone_raw(B, zone_w, vf) + zone_raw(B, zone_d, vf)
    sig = [s for s in CBR.cooldown(CBR.dedup(raw), ZE.LIVE1['cooldown']) if s['ym'] in CBR.MONTHS]
    return evaluate_rev(B, sig, rr=1.5)


# ============================================================================
def stat(S, label):
    n = len(S)
    if n == 0:
        print(f"{label}: n=0")
        return 0, 0, 0.0
    w = sum(1 for s in S if s['r'] > 0)
    tot = sum(s['r'] for s in S)
    print(f"{label}: n={n:3d}  thang={w:3d}  WR={100*w/n:5.1f}%  tongR={tot:+7.1f}R")
    return n, w, tot


def main():
    days = sorted({b['dt'].date() for b in B if b['ym'] in CBR.MONTHS})
    print(f"Cua so du lieu: {CBR.MONTHS[0]}..{CBR.MONTHS[-1]}  so ngay co du lieu={len(days)}")
    print("=" * 90)

    print("[CBR / PLAY2]")
    n1, w1, r1 = stat(cbr_before(), "  TRUOC (chi range noi bo)")
    n2, w2, r2 = stat(cbr_combo(), "  SAU   (+ HVN/VWAP tuan+ngay)")
    print()

    print("[QUAY_DAU / PLAY1]")
    n3, w3, r3 = stat(rev_before(), "  TRUOC (chi VWAP phien)")
    n4, w4, r4 = stat(rev_combo(), "  SAU   (+ HVN/VWAP tuan+ngay)")
    print()

    print("[PORTFOLIO gop 2 nhanh]")
    nA, wA, rA = n1 + n3, w1 + w3, r1 + r3
    nB, wB, rB = n2 + n4, w2 + w4, r2 + r4
    print(f"  TRUOC: n={nA:3d} thang={wA:3d} WR={100*wA/nA:5.1f}% tongR={rA:+7.1f}R")
    print(f"  SAU  : n={nB:3d} thang={wB:3d} WR={100*wB/nB:5.1f}% tongR={rB:+7.1f}R")


if __name__ == '__main__':
    main()
