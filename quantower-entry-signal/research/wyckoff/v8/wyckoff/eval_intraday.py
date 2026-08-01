#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eval_intraday.py — cham diem tin hieu PLAY1/PLAY2 voi RANG BUOC "chi trong ngay, khong qua
dem" (CORVEN_SPEC_V1.md §1: "Thoi gian giu: CHI trong ngay"). SL/TP giong cbr_v6.hit(), nhung
neu chua chot truoc khi PHIEN (session) chua nen vao KET THUC -> DONG MARKET tai close cuoi
phien (outcome 'EOD'), khong giu qua dem.

Phien dung dinh nghia loaders.sessions_from_m1 (gap>45', khop DayGapMin=45 cua C#).
"""
import sys, os, bisect
HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
V7 = os.path.join(WYCK, 'v7')
for p in (HERE, V8, WYCK, RESEARCH, V7):
    if p not in sys.path:
        sys.path.insert(0, p)

import loaders

TICK = 0.1


def session_ends(B):
    """Tra list start-index da sort, dung bisect tim phien chua bar i. Dung lai
    loaders.sessions_from_m1 (KHONG sua)."""
    sessions = loaders.sessions_from_m1(B)
    starts = [s['i0'] for s in sessions]
    return sessions, starts


def _end_idx(sessions, starts, i):
    k = bisect.bisect_right(starts, i) - 1
    if k < 0:
        return len(starts) and sessions[-1]['i1']
    return sessions[k]['i1']


def evaluate(B, sigs, rr, sessions, starts):
    out = []
    for s in sigs:
        i, side, sl, entry = s['i'], s['side'], s['sl'], s['entry']
        r = s['risk_t'] * TICK
        if r <= 0:
            continue
        tp = entry + rr * r if side == 'LONG' else entry - rr * r
        end_idx = _end_idx(sessions, starts, i)
        outcome, rr_real = None, 0.0
        for j in range(i + 1, min(len(B), end_idx + 1)):
            b = B[j]
            hit_sl = (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl)
            hit_tp = (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp)
            if hit_sl:
                outcome, rr_real = 'SL', -1.0
                break
            if hit_tp:
                outcome, rr_real = 'TP', rr
                break
        if outcome is None:
            if end_idx is not None and end_idx > i:
                close_px = B[end_idx]['c']
                rr_real = (close_px - entry) / r if side == 'LONG' else (entry - close_px) / r
                outcome = 'EOD'
            else:
                continue
        s2 = dict(s)
        s2['r'] = rr_real
        s2['outcome'] = outcome
        out.append(s2)
    return out


def dedup_side(sigs, min_gap_bars=6):
    out = []
    for s in sorted(sigs, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= min_gap_bars for m in out):
            continue
        out.append(s)
    return out
