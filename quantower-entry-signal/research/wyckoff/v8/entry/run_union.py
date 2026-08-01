#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/entry/run_union.py — engine THEM (union, KHONG thay the): giu NGUYEN pool cu
(session POC/VAH/VAL/Dinh/Day + D-1 + VWAP phien) va CONG THEM pool CORVEN (HVN
tuan/ngay + VWAP tuan/ngay) vao CUNG mot engine, dem hop luu tren toan bo vung.
Cau hoi dang tra loi: "giu nhu cu + them goc nhin Corven thi n/WR/R co tang khong?"
— khac voi thi nghiem truoc (run_corven.py) la THAY THE toan bo pool cu.

Tai su dung KHONG SUA: entry_dxfeed.{long_sig,short_sig,next_zone,_emit,sim}.
Chi vung dong VWAP la khac ban goc: 3 vung (VWAP phien-cu + VWAP tuan-moi +
VWAP ngay-moi) thay vi 1 (entry_dxfeed) hoac 2 (run_corven).
"""
import os
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)
sys.path.insert(0, HERE)

import entry_dxfeed as E   # noqa: E402
from run_corven import confirm_m1  # noqa: E402  (nen xac nhan M1, tuy chon CONFIRM_ON)

TICK = E.TICK
ARM_DIST_T, BUF_T = E.ARM_DIST_T, E.BUF_T
RETEST_BARS, RETEST_TOL_T = E.RETEST_BARS, E.RETEST_TOL_T
VSA_GATE, VSA_CLIMAX, VSA_BREAK = E.VSA_GATE, E.VSA_CLIMAX, E.VSA_BREAK
VSA_MA, WARMUP_AFTER_GAP = E.VSA_MA, E.WARMUP_AFTER_GAP
DEDUP_BARS, DEDUP_TICKS = E.DEDUP_BARS, E.DEDUP_TICKS
CONFLUENCE_TOL_T = E.CONFLUENCE_TOL_T


def run_union(B, static_pool, C):
    """static_pool = pool CU (session+D-1) UNION pool CORVEN (HVN tuan+ngay), da gop
    san boi harness_union.build_union_pool(). Ham nay CHI khac entry_dxfeed.run() o
    cho ho tro 3 vung VWAP DONG thay vi 1."""
    volfloor = C['VOL_FLOOR']
    raw = []
    vwap_s = dict(price=0.0, kind="VWAP phien", strength=64,
                  ready=B[0]['dt'], expire=B[-1]['dt'] + timedelta(days=1), is_vwap=True, field='vwap')
    vwap_w = dict(price=0.0, kind="VWAP tuan", strength=70,
                  ready=B[0]['dt'], expire=B[-1]['dt'] + timedelta(days=1), is_vwap=True, field='vwap_week')
    vwap_d = dict(price=0.0, kind="VWAP ngay", strength=64,
                  ready=B[0]['dt'], expire=B[-1]['dt'] + timedelta(days=1), is_vwap=True, field='vwap_day')
    dyn = [vwap_s, vwap_w, vwap_d]
    Z = [dict(z) for z in static_pool] + dyn
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
        for z in dyn:
            z['price'] = b[z['field']]
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
            bu = (b['c'] > zhi and b['hi'] > zp and b['brat'] >= 0.5 and bull
                  and b['vratio'] >= VSA_BREAK and z['prev_rel'] in ('below', 'in'))
            bd = (b['c'] < zlo and b['lo'] < zp and b['brat'] >= 0.5 and bear
                  and b['vratio'] >= VSA_BREAK and z['prev_rel'] in ('above', 'in'))
            if bu:
                z['state'] = 'broke_up'; z['brk_bar'] = i
            elif bd:
                z['state'] = 'broke_dn'; z['brk_bar'] = i
            em = False
            hv = C.get('HOVER_H')
            cancel_up = (b['c'] < zp - hv) if hv is not None else (b['c'] < zp - BUF_T * TICK)
            cancel_dn = (b['c'] > zp + hv) if hv is not None else (b['c'] > zp + BUF_T * TICK)
            hold_lo = zp - (hv if hv is not None else C['RETEST_HOLD_T'] * TICK)
            hold_hi = zp + (hv if hv is not None else C['RETEST_HOLD_T'] * TICK)
            if z['state'] == 'broke_up' and 0 < i - z['brk_bar'] <= RETEST_BARS:
                if cancel_up:
                    z['state'] = 'idle'
                elif b['lo'] <= zp + RETEST_TOL_T * TICK and b['lo'] >= hold_lo:
                    ok, w = E.long_sig(b)
                    ok = ok and (not confirm_on or confirm_m1(b, 'LONG'))
                    if ok and liq_ok(b) and E._emit(raw, B, i, z, 'LONG', '1 pha&hoi len', min(b['lo'], zp), w, static_pool, C):
                        em = True; z['cool'] = i; z['state'] = 'idle'
            elif z['state'] == 'broke_dn' and 0 < i - z['brk_bar'] <= RETEST_BARS:
                if cancel_dn:
                    z['state'] = 'idle'
                elif b['hi'] >= zp - RETEST_TOL_T * TICK and b['hi'] <= hold_hi:
                    ok, w = E.short_sig(b)
                    ok = ok and (not confirm_on or confirm_m1(b, 'SHORT'))
                    if ok and liq_ok(b) and E._emit(raw, B, i, z, 'SHORT', '1 pha&hoi xuong', max(b['hi'], zp), w, static_pool, C):
                        em = True; z['cool'] = i; z['state'] = 'idle'
            if not em and C.get('KB2_CLIMAX', True) and z['state'] in ('idle', 'broke_up', 'broke_dn') and b['vratio'] >= VSA_CLIMAX:
                if up and tagged and b['c'] < zhi:
                    ok, w = E.short_sig(b)
                    ok = ok and (not confirm_on or confirm_m1(b, 'SHORT'))
                    if ok and liq_ok(b) and E._emit(raw, B, i, z, 'SHORT', '2 cham&dao xuong', max(b['hi'], zp), w + ['climax-abs'], static_pool, C):
                        z['cool'] = i; z['state'] = 'idle'
                elif dn and tagged and b['c'] > zlo:
                    ok, w = E.long_sig(b)
                    ok = ok and (not confirm_on or confirm_m1(b, 'LONG'))
                    if ok and liq_ok(b) and E._emit(raw, B, i, z, 'LONG', '2 cham&dao len', min(b['lo'], zp), w + ['climax-abs'], static_pool, C):
                        z['cool'] = i; z['state'] = 'idle'
            z['prev_rel'] = rel
    return raw


def cluster_count_union(s, static_pool):
    """Hop luu = so vung TINH (pool cu + HVN) quanh entry, dedup theo gia — GIONG HET
    entry_dxfeed.cluster_count (khong ke VWAP), chi khac la pool da la UNION."""
    seen = set()
    n = 0
    for z in static_pool:
        if z['ready'] <= s['dt'] <= z['expire'] and abs(z['price'] - s['entry']) / TICK <= CONFLUENCE_TOL_T:
            k = round(z['price'] / TICK)
            if k not in seen:
                seen.add(k); n += 1
    return n, seen


def dedup_union(raw, static_pool, B, C):
    """B: can de doc vwap_week/vwap_day dung tai nen s['i']. Hop luu cong THEM 2 VWAP
    moi (tuan/ngay) neu chua trung gia voi vung tinh nao — giong quy uoc run_corven.py.
    VWAP PHIEN (cu) tiep tuc KHONG tinh vao hop luu, dung nhu entry_dxfeed truoc gio."""
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
        n_static, seen = cluster_count_union(s, static_pool)
        vw, vd = B[s['i']]['vwap_week'], B[s['i']]['vwap_day']
        n_extra = 0
        for vp in (vw, vd):
            if vp and vp > 0 and abs(vp - s['entry']) / TICK <= CONFLUENCE_TOL_T:
                k = round(vp / TICK)
                if k not in seen:
                    seen.add(k); n_extra += 1
        s['confl'] = n_static + n_extra
        if s['confl'] < C['MIN_CONFL']:
            continue
        if C.get('TREND_ON'):
            if s['side'] == 'LONG' and s['trend'] < 0:
                continue
            if s['side'] == 'SHORT' and s['trend'] > 0:
                continue
        if C.get('VWAP_ON') and not (C.get('VWAP_KB1ONLY') and not s['scen'].startswith('1')):
            m = C.get('VWAP_MARGIN', 0.0)
            if s['side'] == 'LONG' and not (s['vwap_dist'] > m):
                continue
            if s['side'] == 'SHORT' and not (s['vwap_dist'] < -m):
                continue
        res.append(s)
    return res
