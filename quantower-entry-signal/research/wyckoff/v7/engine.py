#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine.py — v7: mo rong cbr_v6 (KHONG SUA cbr_v6.py — file do dong bang) de:
  1. Ho tro nguon RANGE thu hai ("range theo cau truc" tu features.range_struct_scan) ben canh
     box N-nen goc cua v5/v6 — RangeMode 0=box (mac dinh) | 1=struct (SPEC §4.3/§4.8, H5).
  2. Ho tro gate BIAS (session_bias_series) THAY THE hoac CONG THEM gate trend-proxy hien co
     (SPEC §2.5/§2.6, H6) — qua co C['BIAS_ON'] + bias_at[] truyen vao.
  3. evaluate_v7()/hit_v7() tong quat hoa RR CO DINH (KB1/KB2, dung cho luot nay) VA TP theo
     MUC GIA tuyet doi (chuan bi cho KB3 — SPEC §6.5.1) — la NO-OP cho tin hieu KHONG co key
     'tp'/'maxbars'/'dead_at' (dung y het cbr_v6.evaluate()/hit() — kiem bang GOLDEN TEST).

engine.py DUOC PHEP import tu cbr_v6 (dung lai _gate/counter_sweep/dedup/cooldown/post/mdd/line);
KHONG dung cbr_v6.run()/cbr_v6.evaluate() truc tiep cho v7 (v7 co ban tong quat hoa rieng), tru
khi can doi chieu GOLDEN.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cbr_v6
import features

E = cbr_v6.E
TICK = cbr_v6.TICK


# ===================================================================== §6.5.1 evaluate/hit tong quat
def hit_v7(B, i, side, sl, tp, entry_px, maxbars=None, dead_at=None):
    """Tong quat hoa cbr_v6.hit(): giu nguyen thu tu kiem SL TRUOC TP trong cung nen (bi quan,
    SPEC §9 rui ro #5). maxbars/dead_at khac None CHI duoc dung boi KB3 (chua implement luot
    nay) — voi KB1/KB2 luon la None => hanh vi giong het cbr_v6.hit()."""
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl):
            return 'SL', -1.0
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp):
            return 'TP', None
        if dead_at is not None and j >= dead_at:
            r = (b['c'] - entry_px) if side == 'LONG' else (entry_px - b['c'])
            return 'BREAK', r / abs(entry_px - sl)
        if maxbars is not None and j - i >= maxbars:
            r = (b['c'] - entry_px) if side == 'LONG' else (entry_px - b['c'])
            return 'TO', r / abs(entry_px - sl)
    return 'open', 0.0


def evaluate_v7(B, sig, C):
    """NO-OP cho KB1/KB2 (khong co s['tp']) — RR = C['RR'] co dinh, y het cbr_v6.evaluate().
    KB3 (chua lam luot nay) se truyen s['tp'] (gia tuyet doi) => rr bien thien."""
    out = []
    for s in sig:
        r = s['risk_t'] * TICK
        if s.get('tp') is not None:
            tp = s['tp']; rr = abs(tp - s['entry']) / r
        else:
            rr = C['RR']
            tp = s['entry'] + rr * r if s['side'] == 'LONG' else s['entry'] - rr * r
        o, r_extra = hit_v7(B, s['i'], s['side'], s['sl'], tp, s['entry'],
                             maxbars=s.get('maxbars'), dead_at=s.get('dead_at'))
        if o == 'open':
            continue
        s2 = dict(s); s2['rr_real'] = rr
        s2['r'] = rr if o == 'TP' else (-1.0 if o == 'SL' else r_extra)
        out.append(s2)
    return out


# ===================================================================== WAIT/entry dung chung (§4.4)
def _wait_entry(B, i, up, edge, C, vf, bias_at=None):
    """Tu nen ARM `i` (da xac dinh up/edge boi box HOAC struct), quet WAIT nen tim ENTRY.
    Y HET logic vong lap trong cbr_v6.run() (peak/since/retr/held/resume/SL floor-cap/gate
    tai nen VAO) — CHI THEM gate BIAS (okB), la NO-OP khi C['BIAS_ON'] khong bat."""
    peak = B[i]['hi'] if up else B[i]['lo']
    since = i
    N = len(B)
    for j in range(i + 1, min(N, i + 1 + C['WAIT'])):
        bj = B[j]
        if not cbr_v6._gate(bj, vf):
            return None
        if (bj['c'] < edge - C['HOLD_TOL'] * TICK) if up else (bj['c'] > edge + C['HOLD_TOL'] * TICK):
            return None
        pseg = B[since + 1:j + 1]
        if pseg:
            pext = min(x['lo'] for x in pseg) if up else max(x['hi'] for x in pseg)
            leg = (peak - edge) if up else (edge - peak)
            depth = (peak - pext) if up else (pext - peak)
            retr = depth / leg if leg > 0 else 0
            held = (pext >= edge - C['HOLD_TOL'] * TICK) if up else (pext <= edge + C['HOLD_TOL'] * TICK)
            resume = ((bj['c'] > B[j - 1]['hi'] and bj['up']) if up
                      else (bj['c'] < B[j - 1]['lo'] and bj['dn'])) and bj['brat'] >= C['RBODY']
            if j >= since + 2 and C['PMIN'] <= retr <= C['PMAX'] and held and resume:
                entry = bj['c']
                anchor = pext
                sl = anchor - C['BUF'] * TICK if up else anchor + C['BUF'] * TICK
                risk = (entry - sl) / TICK if up else (sl - entry) / TICK
                if risk < C['FLOOR']:
                    sl = entry - C['FLOOR'] * TICK if up else entry + C['FLOOR'] * TICK
                    risk = C['FLOOR']
                if risk > C['CAP']:
                    return None
                sd = 1 if up else -1
                okT = (not C['TREND']) or bj['trend'] == sd
                okB = (not C.get('BIAS_ON')) or (bias_at is not None and bias_at[j] == sd)
                okV = (not C['VWAP']) or (bj['c'] >= bj['vwap'] if up else bj['c'] <= bj['vwap'])
                okL = (not C['LIQ']) or bj['liqratio'] >= C['LIQ_K']
                if okT and okB and okV and okL:
                    return dict(i=j, dt=bj['dt'], ym=bj['ym'], side=('LONG' if up else 'SHORT'),
                                entry=entry, sl=sl, risk_t=risk, retr=retr, brk_i=i, peak_i=since,
                                hour=bj['dt'].hour, pext=pext)
                return None
        if (bj['hi'] > peak) if up else (bj['lo'] < peak):
            peak = bj['hi'] if up else bj['lo']; since = j
    return None


# ===================================================================== RangeMode 0 — box (v6 goc)
def run_box(B, C, vf, bias_at=None):
    """Y HET cbr_v6.run(), CHI them gate BIAS (okB, NO-OP khi tat) — dam bao GOLDEN TEST khop
    tuyet doi voi cbr_v6.scan() khi BIAS_ON=False."""
    raw = []
    N = len(B)
    for i in range(E.VSA_MA + 2, N):
        b = B[i]
        if not cbr_v6._gate(b, vf):
            continue
        win = B[i - C['RANGE_LEN']:i]
        rhi = max(x['hi'] for x in win); rlo = min(x['lo'] for x in win)
        span = (rhi - rlo) / TICK
        if span > C['RMAX'] or span < C['RMIN']:
            continue
        up = b['c'] > rhi + C['BUF'] * TICK and b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and b['up']
        dn = b['c'] < rlo - C['BUF'] * TICK and b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and b['dn']
        if not (up or dn):
            continue
        if C['CLEAN'] and cbr_v6.counter_sweep(B, i, up, C['CL_LOOK'], C['CL_W'], C['CL_CLOSE']):
            continue
        edge = rhi if up else rlo
        sig = _wait_entry(B, i, up, edge, C, vf, bias_at=bias_at)
        if sig is not None:
            sig['span'] = span
            raw.append(sig)
    return raw


def scan_box(B, C, vf, bias_at=None):
    raw = run_box(B, C, vf, bias_at=bias_at)
    sig = cbr_v6.post(cbr_v6.cooldown(cbr_v6.dedup(raw), C['COOL']), C)
    return evaluate_v7(B, sig, C)


# ===================================================================== RangeMode 1 — struct (§4.3)
def run_struct(B, C, vf, arms, bias_at=None):
    """RangeMode=1: dung arm events tu features.range_struct_scan() thay cho box N-nen; sau ARM
    dung LAI dung _wait_entry (SPEC §4.4: 'giu nguyen, v7 chi doi nguon cua edge')."""
    raw = []
    for a in arms:
        i = a['i']; up = a['up']; edge = a['edge']
        b = B[i]
        if not cbr_v6._gate(b, vf):
            continue
        if not (b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and (b['up'] if up else b['dn'])):
            continue
        if C['CLEAN'] and cbr_v6.counter_sweep(B, i, up, C['CL_LOOK'], C['CL_W'], C['CL_CLOSE']):
            continue
        sig = _wait_entry(B, i, up, edge, C, vf, bias_at=bias_at)
        if sig is not None:
            sig['span'] = a['width'] / TICK
            raw.append(sig)
    return raw


def scan_struct(B, C, vf, arms, bias_at=None):
    raw = run_struct(B, C, vf, arms, bias_at=bias_at)
    sig = cbr_v6.post(cbr_v6.cooldown(cbr_v6.dedup(raw), C['COOL']), C)
    return evaluate_v7(B, sig, C)


# ===================================================================== WY04 partition helper (§4.10 step4)
def wy04_ok(B, sig):
    """Voi moi tin hieu da co (dict co 'peak_i'..'i' la nhip hoi, 'side'), kiem xem NEN co
    pext (cuc tri nhip hoi, luu trong _wait_entry) co la no_supply (SHORT-pullback trong LONG)
    / no_demand (LONG-pullback trong SHORT) hay khong. Tra ve list bool cung do dai sig."""
    out = []
    for s in sig:
        # tim nen dat pext trong khoang (peak_i, i] — quet lai vi pext khong luu index, chi luu gia
        found = False
        up = s['side'] == 'LONG'
        for k in range(s['peak_i'] + 1, s['i'] + 1):
            b = B[k]
            if up and abs(b['lo'] - s['pext']) < 1e-9:
                found = features.no_supply(B, k) or found
            if (not up) and abs(b['hi'] - s['pext']) < 1e-9:
                found = features.no_demand(B, k) or found
        out.append(found)
    return out
