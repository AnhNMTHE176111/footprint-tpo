#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/runner/zone_engine.py — PLAY1 (cham->dao) neo vung CORVEN (HVN tuan/ngay + VWAP tuan/ngay),
+ ham dung chung cho P2 (probe MFE), P4 (doi chung ngau nhien), P6 (chi phi giao dich).
PLAY2 (pha->hoi->tiep) nam trong cbr_hvn.run_zone()/scan_zone() (edited copy cua cbr_v6.py).

Nguon dung lai KHONG SUA: entry_dxfeed.py (bars), zones_corven.py (HVN/VWAP causal),
v7/report.py (line/mdd/_half_split). cbr_hvn.py la file cua chinh session nay (duoc sua).

CHOT THIET KE (ghi vao RESULTS_RUNNER_ZONES.md, dung lam tham chieu khi doc code):
  - vf = VOLFLOOR_FROZEN = 20.0 (KHONG calc_volfloor - tranh look-ahead, dung cho MOI phep do
    tu P1 tro di; GOLDEN o P0 dung calc_volfloor() rieng cua cbr_v6.py, da xac nhan vf=17 vs 20
    cho KET QUA GIONG HET voi CBR nen doi sang 20 khong lam sai lech cot TRUOC).
  - Zone tol: sweep {8,12,20} tick quanh moi gia HVN/VWAP (HVN la MOT DAI, khong phai 1 muc -
    xem PLAN §P2 "Be rong vung HVN"). Bao cao mac dinh tol=12 (khop VwapTolTicks cua RunnerSignal.cs).
  - R2 (hap thu chi co gia tri o cuc tri): "range gan" = window R2_LOOKBACK=50 nen TRUOC bar cham
    (khong gom bar do). Vi tri zp trong range do phai <=25% (LONG, gan day) hoac >=75% (SHORT, gan dinh).
  - Nen xac nhan M1 (ConfirmOn): False = vao ngay tren nen cham+tu choi (khop v5 ScanReversal hien tai,
    da co dieu kien wick+cpos+brat lam "xac nhan cung nen"). True = doi THEM 1 nen sau dong THUAN
    huong vuot qua close cua nen cham roi moi vao tai close nen do (tre 1 nen, dung nghia den cua
    "khong vao khi gia vua cham" trong CORVEN_SPEC §1).
  - approach_bars=6, wick_frac=0.50, cpos_h=0.05, body_min=0.30, vsa_conf=1.8, sl_buf_t=2, sl_cap_t=70,
    cooldown=15, dedup_bars=6 — GIU NGUYEN gia tri LIVE cua ScanReversal (imp_reversal_sweep.LIVE),
    chi thay nguon vung (VWAP phien -> HVN/VWAP tuan|ngay).
  - TrendFilter (R5, xuyen suot) AP DUNG cho ca 2 KB, dung field 'trend' da chuan hoa TREND_TOL=1.0
    boi cbr_hvn.prepare(B) (KHONG dung field 'trend' tho cua entry_dxfeed.load_m1 - khac o tolerance).

Chay truc tiep: python3 zone_engine.py p1|p2|p3|p4|p5|p6|all
"""
import os
import sys
import statistics as st
from collections import deque

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
import zones_corven as Z
import report as R
import cbr_hvn as CBR

TICK = E.TICK
MONTHS = ('2026-05', '2026-06', '2026-07')
VOLFLOOR_FROZEN = 20.0

_BARS = None


def bars():
    """B chuan hoa 1 lan: entry_dxfeed.load_m1() + cbr_hvn.prepare() (trend TOL=1.0, liqratio cuon)."""
    global _BARS
    if _BARS is None:
        B = E.load_m1()
        CBR.prepare(B)
        _BARS = B
    return _BARS


# ============================================================================
# Zone lookup — gop HVN (tuan hoac ngay, causal) + VWAP (tuan hoac ngay) thanh 1 ham zone_at(i)
# ============================================================================
def build_zone_lookup(B, mode, causal='closed', include_vwap=True, min_ratio=1.5, max_n=3):
    days = Z.group_days(B)
    spans = Z.group_weeks(B, days) if mode == 'week' else [[d] for d in days]
    series = Z.build_zone_series(B, mode=mode, causal=causal)
    get = Z.zone_lookup_series(series)
    vwap_arr = None
    if include_vwap:
        vwap_spans = [(w[0][0], w[-1][1]) for w in spans] if mode == 'week' else days
        vwap_arr = Z.vwap_series(B, vwap_spans)

    def zone_at(i):
        r = get(B[i]['dt'])
        zps = [p for p, _, ratio in r[2] if ratio >= min_ratio][:max_n] if r else []
        if include_vwap:
            zps = zps + [vwap_arr[i]]
        return zps
    return zone_at


# ============================================================================
# PLAY1 — cham vung -> dao chieu (ban sao ScanReversal, thay VWAP phien = zone CORVEN)
# ============================================================================
LIVE1 = dict(
    tol_ticks=12, approach_bars=6, wick_frac=0.50, cpos_h=0.05, body_min=0.30,
    vsa_conf=1.8, sl_buf_t=2, sl_cap_t=70, cooldown=15, dedup_bars=6,
    r2_lookback=50, r2_frac=0.25, trend_on=True, confirm_on=False,
)


def play1_raw(B, zone_at_fn, vf=VOLFLOOR_FROZEN, **kw):
    P = dict(LIVE1); P.update(kw)
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
                             risk_t=risk, zone_edge=zp, hour=entry_bar['dt'].hour))
    raw.sort(key=lambda x: x['i'])
    deduped = []
    for s in raw:
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= P['dedup_bars'] for m in deduped):
            continue
        deduped.append(s)
    out = []
    last = {}
    for s in sorted(deduped, key=lambda x: x['i']):
        if s['i'] - last.get(s['side'], -999) < P['cooldown']:
            continue
        out.append(s)
        last[s['side']] = s['i']
    return out


def play1_scan(B, zone_at_fn, rr, months=MONTHS, vf=VOLFLOOR_FROZEN, **kw):
    raw = play1_raw(B, zone_at_fn, vf=vf, **kw)
    out = []
    for s in raw:
        if s['ym'] not in months:
            continue
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


# ============================================================================
# P2 — phan phoi MFE (truoc khi chot RR cho PLAY1)
# ============================================================================
def mfe_distribution(B, sigs, max_bars=1000):
    mfes = []
    for s in sigs:
        r_ = s['risk_t'] * TICK
        entry, side, sl = s['entry'], s['side'], s['sl']
        best = 0.0
        for j in range(s['i'] + 1, min(len(B), s['i'] + 1 + max_bars)):
            bj = B[j]
            hit_sl = bj['lo'] <= sl if side == 'LONG' else bj['hi'] >= sl
            if hit_sl:
                break
            fav = (bj['hi'] - entry) if side == 'LONG' else (entry - bj['lo'])
            best = max(best, fav / r_)
        mfes.append(best)
    return mfes


def p2_probe():
    B = bars()
    zone_at = build_zone_lookup(B, mode='week', causal='closed', include_vwap=True)
    raw = play1_raw(B, zone_at, vf=VOLFLOOR_FROZEN, confirm_on=False)
    raw = [s for s in raw if s['ym'] in MONTHS]
    print(f"[P2] PLAY1 neo HVN+VWAP TUAN (W_CLOSED), tol=12t, confirm_on=False: n={len(raw)}")
    if not raw:
        print("  KHONG CO tin hieu nao -> khong probe duoc MFE.")
        return raw, []
    mfes = mfe_distribution(B, raw)
    thr = (1.5, 2.0, 3.0, 4.0)
    for t in thr:
        p = sum(1 for m in mfes if m >= t) / len(mfes)
        print(f"  P(MFE>={t}R) = {p*100:.1f}%  ({sum(1 for m in mfes if m>=t)}/{len(mfes)})")
    lc = [s for s in raw if s['side'] == 'LONG']
    sc = [s for s in raw if s['side'] == 'SHORT']
    print(f"  LONG n={len(lc)}  SHORT n={len(sc)}")
    return raw, mfes


# ============================================================================
# P4 — doi chung ngau nhien: dich MOI zone +-3 gia, giu nguyen logic, 5 seed
# ============================================================================
import random as _random


def shifted_zone_lookup_seeded(zone_at_fn, seed, shift_pts=3.0, max_slots=8):
    """Dich TUNG vung +-shift_pts, dau (+/-) co dinh theo VI TRI trong danh sach (khong doi giua
    cac bar) nhung DUOC RUT NGAU NHIEN theo seed -> 5 seed = 5 ban vung "gia" khac nhau, tai lap
    duoc. Day la doi chung: giu nguyen logic phat hien tin hieu, chi lam SAI VI TRI vung."""
    rng = _random.Random(seed)
    signs = [1 if rng.random() < 0.5 else -1 for _ in range(max_slots)]

    def f(i):
        zps = zone_at_fn(i)
        return [zp + signs[k % max_slots] * shift_pts for k, zp in enumerate(zps)]
    return f


def random_control(B, zone_at_fn, rr, play='play1', seeds=(1, 2, 3, 4, 5), shift_pts=3.0, C=None, **kw):
    evs = []
    for seed in seeds:
        zf = shifted_zone_lookup_seeded(zone_at_fn, seed, shift_pts=shift_pts)
        if play == 'play1':
            S = play1_scan(B, zf, rr, vf=VOLFLOOR_FROZEN, **kw)
        else:
            S = CBR.scan_zone(B, C, VOLFLOOR_FROZEN, zf)
        ev = (sum(s['r'] for s in S) / len(S)) if S else 0.0
        evs.append((seed, len(S), ev))
    return evs


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'p2'
    if mode == 'p2':
        p2_probe()
