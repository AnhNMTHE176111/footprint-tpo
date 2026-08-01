#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/entry/run_corven.py — engine PLAY1 (cham->dao)/PLAY2 (pha->hoi) chay tren POOL CORVEN
(HVN tuan/ngay + VWAP tuan/ngay), copy+sua tu entry_dxfeed.run()/dedup() (READ-ONLY,
khong sua file goc) de:
  1) ho tro 2 vung VWAP DONG (tuan + ngay) thay vi 1 (entry_dxfeed chi ho tro 1 is_vwap)
  2) hop luu = cac KHUNG dong y (HVN tuan/ngay + VWAP tuan/ngay trong ConfluenceTol),
     KHAC voi pool cu (hop luu tinh tren nhieu vung CUNG khung phien) — them ca VWAP
     vao dem hop luu (pool cu CO Y loai VWAP, xem entry_dxfeed.cluster_count).
  3) NEN XAC NHAN M1 (CORVEN_SPEC §1, PLAN §4.3) — cong THEM vao long_sig/short_sig da co,
     bat/tat bang CONFIRM_ON (A/B).
Tai su dung KHONG SUA: entry_dxfeed.{long_sig,short_sig,gate-thresholds,next_zone,sim}.
"""
import os
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)

import entry_dxfeed as E  # noqa: E402

TICK = E.TICK
ARM_DIST_T, BUF_T = E.ARM_DIST_T, E.BUF_T
RETEST_BARS, RETEST_TOL_T = E.RETEST_BARS, E.RETEST_TOL_T
VSA_GATE, VSA_CLIMAX, VSA_BREAK = E.VSA_GATE, E.VSA_CLIMAX, E.VSA_BREAK
WICK_FRAC = E.WICK_FRAC
VSA_MA, WARMUP_AFTER_GAP = E.VSA_MA, E.WARMUP_AFTER_GAP
DEDUP_BARS, DEDUP_TICKS = E.DEDUP_BARS, E.DEDUP_TICKS
CONFLUENCE_TOL_T = E.CONFLUENCE_TOL_T


# ============================================================================
# NEN XAC NHAN M1 (CORVEN_SPEC_V1.md §1: "bat buoc cho nen xac nhan tren M1 roi
# moi vao — khong vao khi gia vua cham"). Dinh nghia de xuat (PLAN_KB_ABC §4.3):
# close>open (LONG) + cpos>=0.60 + than>=30% range + rau NGUOC <=35% range.
# ============================================================================
def confirm_m1(b, side):
    if b['rng'] <= 0:
        return False
    if side == 'LONG':
        return b['c'] > b['o'] and b['cpos'] >= 0.60 and b['brat'] >= 0.30 and (b['uw'] / b['rng']) <= 0.35
    else:
        return b['c'] < b['o'] and b['cpos'] <= 0.40 and b['brat'] >= 0.30 and (b['lw'] / b['rng']) <= 0.35


def run_corven(B, hvn_pool, C):
    """C them 2 khoa so voi BASE cua entry_dxfeed: CONFIRM_ON (bool)."""
    volfloor = C['VOL_FLOOR']
    raw = []
    vwap_w = dict(price=0.0, kind="VWAP tuan", strength=70,
                   ready=B[0]['dt'], expire=B[-1]['dt'] + timedelta(days=1), is_vwap=True, field='vwap_week')
    vwap_d = dict(price=0.0, kind="VWAP ngay", strength=64,
                   ready=B[0]['dt'], expire=B[-1]['dt'] + timedelta(days=1), is_vwap=True, field='vwap_day')
    Z = [dict(z) for z in hvn_pool] + [vwap_w, vwap_d]
    for z in Z:
        z.update(state='idle', brk_bar=-999, cool=-999, prev_rel=None)

    def gate(b):
        return b['v'] >= volfloor and b['since_gap'] >= WARMUP_AFTER_GAP and b['vma'] >= volfloor * 0.6

    def liq_ok(b):
        if not C.get('LIQ_ON'):
            return True
        return b.get('liqbase', 0) > 0 and b['vma'] >= C['LIQ_MIN'] * b['liqbase']

    confirm_on = C.get('CONFIRM_ON', False)

    for i in range(VSA_MA + 2, len(B)):
        b = B[i]
        px = b['c']
        vwap_w['price'] = b['vwap_week']
        vwap_d['price'] = b['vwap_day']
        active = [z for z in Z if z['ready'] <= b['dt'] <= z['expire']]
        if not gate(b):
            for z in active:
                z['prev_rel'] = 'above' if px > z['price'] else 'below'
            continue
        for z in active:
            zp = z['price']
            if zp <= 0:
                z['prev_rel'] = 'above' if px > zp else 'below'
                continue
            dist = abs(px - zp) / TICK
            rel = 'above' if b['c'] > zp + BUF_T * TICK else 'below' if b['c'] < zp - BUF_T * TICK else 'in'
            if (dist > ARM_DIST_T and z['state'] == 'idle') or i - z['cool'] < C['COOLDOWN']:
                z['prev_rel'] = rel
                continue
            zlo, zhi = zp - BUF_T * TICK, zp + BUF_T * TICK
            tagged = b['lo'] <= zhi and b['hi'] >= zlo
            up, dn = z['prev_rel'] == 'below', z['prev_rel'] == 'above'
            bull, bear = b['up'], b['dn']
            bu = b['c'] > zhi and b['hi'] > zp and b['brat'] >= 0.5 and bull and b['vratio'] >= VSA_BREAK and z['prev_rel'] in ('below', 'in')
            bd = b['c'] < zlo and b['lo'] < zp and b['brat'] >= 0.5 and bear and b['vratio'] >= VSA_BREAK and z['prev_rel'] in ('above', 'in')
            if bu:
                z['state'] = 'broke_up'; z['brk_bar'] = i
            elif bd:
                z['state'] = 'broke_dn'; z['brk_bar'] = i
            em = False
            if z['state'] == 'broke_up' and 0 < i - z['brk_bar'] <= RETEST_BARS:
                if b['c'] < zp - BUF_T * TICK:
                    z['state'] = 'idle'
                elif b['lo'] <= zp + RETEST_TOL_T * TICK and b['lo'] >= zp - C['RETEST_HOLD_T'] * TICK:
                    ok, w = E.long_sig(b)
                    ok = ok and (not confirm_on or confirm_m1(b, 'LONG'))
                    if ok and liq_ok(b) and _emit(raw, B, i, z, 'LONG', '1 pha&hoi len', min(b['lo'], zp), w, hvn_pool, C):
                        em = True; z['cool'] = i; z['state'] = 'idle'
            elif z['state'] == 'broke_dn' and 0 < i - z['brk_bar'] <= RETEST_BARS:
                if b['c'] > zp + BUF_T * TICK:
                    z['state'] = 'idle'
                elif b['hi'] >= zp - RETEST_TOL_T * TICK and b['hi'] <= zp + C['RETEST_HOLD_T'] * TICK:
                    ok, w = E.short_sig(b)
                    ok = ok and (not confirm_on or confirm_m1(b, 'SHORT'))
                    if ok and liq_ok(b) and _emit(raw, B, i, z, 'SHORT', '1 pha&hoi xuong', max(b['hi'], zp), w, hvn_pool, C):
                        em = True; z['cool'] = i; z['state'] = 'idle'
            if not em and C.get('KB2_CLIMAX', True) and z['state'] in ('idle', 'broke_up', 'broke_dn') and b['vratio'] >= VSA_CLIMAX:
                if up and tagged and b['c'] < zhi:
                    ok, w = E.short_sig(b)
                    ok = ok and (not confirm_on or confirm_m1(b, 'SHORT'))
                    if ok and liq_ok(b) and _emit(raw, B, i, z, 'SHORT', '2 cham&dao xuong', max(b['hi'], zp), w + ['climax-abs'], hvn_pool, C):
                        z['cool'] = i; z['state'] = 'idle'
                elif dn and tagged and b['c'] > zlo:
                    ok, w = E.long_sig(b)
                    ok = ok and (not confirm_on or confirm_m1(b, 'LONG'))
                    if ok and liq_ok(b) and _emit(raw, B, i, z, 'LONG', '2 cham&dao len', min(b['lo'], zp), w + ['climax-abs'], hvn_pool, C):
                        z['cool'] = i; z['state'] = 'idle'
            z['prev_rel'] = rel
    return raw


def next_zone(entry, side, t, hvn_pool):
    cands = [z['price'] for z in hvn_pool if z['ready'] <= t <= z['expire']]
    if side == 'LONG':
        up = [p for p in cands if p > entry + 5 * TICK]
        return min(up) if up else None
    dn = [p for p in cands if p < entry - 5 * TICK]
    return max(dn) if dn else None


def _emit(raw, B, i, z, side, scen, anchor, why, hvn_pool, C):
    b = B[i]
    entry = b['c']
    fl = C['SL_FLOOR_T'] * TICK
    if side == 'LONG':
        sl = min(anchor - E.SL_BUF_T * TICK, entry - fl); risk = (entry - sl) / TICK
    else:
        sl = max(anchor + E.SL_BUF_T * TICK, entry + fl); risk = (sl - entry) / TICK
    if risk <= 0 or risk > C['SL_CAP_T']:
        return False
    r_dollar = risk * TICK
    RR = C['RR']
    tp3 = entry + RR * r_dollar if side == 'LONG' else entry - RR * r_dollar
    tpx, rx = tp3, RR
    if C.get('EXTEND'):
        nz = next_zone(entry, side, b['dt'], hvn_pool)
        if nz is not None:
            cand = nz - 2 * TICK if side == 'LONG' else nz + 2 * TICK
            rr_cand = abs(cand - entry) / r_dollar
            if rr_cand >= C['NEXTZONE_MINR']:
                tpx, rx = cand, rr_cand
    raw.append(dict(i=i, dt=b['dt'], ym=b['ym'], side=side, scen=scen,
                     zone=f"{z['kind']} {z['price']:.1f}", zstr=z['strength'],
                     entry=entry, sl=sl, tp3=tp3, tpx=tpx, rx=rx, risk_t=risk,
                     climax=b['vratio'] >= VSA_CLIMAX, trend=b['trend'], vsa=b['vratio'], why=";".join(why)))
    return True


def cluster_count_corven(s, hvn_pool):
    """Hop luu CORVEN = so KHUNG dong y quanh entry: HVN tuan/ngay (tu hvn_pool) + VWAP
    tuan/ngay (gia tri dong tai s['dt'], da luu san trong s luc _emit... nhung _emit
    khong luu vwap — nen tra lai tu B). Ham nay chi dem hvn_pool; VWAP duoc cong them
    o dedup_corven() (can B de tra vwap_week/vwap_day dung luc dt)."""
    seen = set()
    n = 0
    for z in hvn_pool:
        if z['ready'] <= s['dt'] <= z['expire'] and abs(z['price'] - s['entry']) / TICK <= CONFLUENCE_TOL_T:
            k = round(z['price'] / TICK)
            if k not in seen:
                seen.add(k); n += 1
    return n, seen


def dedup_corven(raw, hvn_pool, B, C):
    """B: danh sach bar goc (de doc vwap_week/vwap_day dung tai nen s['i'])."""
    raw = sorted(raw, key=lambda s: (s['i'], s['zone']))
    out = []
    for s in raw:
        m = None
        for k in out:
            if k['side'] == s['side'] and abs(s['i'] - k['i']) <= DEDUP_BARS and abs(s['entry'] - k['entry']) / TICK <= DEDUP_TICKS:
                m = k; break
        if m:
            if s['zstr'] > m['zstr']:
                m.update(zone=s['zone'], zstr=s['zstr'])
        else:
            out.append(dict(s))
    res = []
    for s in out:
        n_hvn, seen = cluster_count_corven(s, hvn_pool)
        vw, vd = B[s['i']]['vwap_week'], B[s['i']]['vwap_day']
        n_extra = 0
        for vp in (vw, vd):
            if vp and vp > 0 and abs(vp - s['entry']) / TICK <= CONFLUENCE_TOL_T:
                k = round(vp / TICK)
                if k not in seen:
                    seen.add(k); n_extra += 1
        s['confl'] = n_hvn + n_extra
        if s['confl'] < C['MIN_CONFL']:
            continue
        if C.get('TREND_ON'):
            if s['side'] == 'LONG' and s['trend'] < 0:
                continue
            if s['side'] == 'SHORT' and s['trend'] > 0:
                continue
        res.append(s)
    return res
