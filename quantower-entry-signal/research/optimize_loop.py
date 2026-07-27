#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VONG LAP TOI UU WINRATE — CBR + Reversal, tren cua so thanh khoan 5-7/2026 (dxFeed GCQ26).
Muc tieu user: NANG WINRATE, giu net duong + ON DINH (ca 3 thang duong = chong overfit).
Chay lai nhieu vong: sua param -> do WR/net/thang -> brainstorm -> sua tiep.
"""
import reversal_vwap as rv, entry_cbr as cbr
from collections import defaultdict
TICK = rv.TICK
DX = ("/home/asl86/Documents/footprint-tpo/data-export/27-7/"
      "_GCQ26XCEC dxFeed, Time - Time - 1m, 11_3_2025 120000 AM-7_27_2026 105600 PM_8b750702-5f00-4836-bf74-81e2a0c4495f.csv")

_B = None
def bars():
    global _B
    if _B is None:
        Bdx = rv.load_dxfeed(DX)
        _B = [b for b in Bdx if b['dt'].year == 2026 and b['dt'].month >= 5]
        # gan trend nhieu lookback san
        for N in (240, 360, 480, 720):
            for i, b in enumerate(_B):
                b[f'tr{N}'] = 0 if i < N else (1 if _B[i]['c']-_B[i-N]['c'] > 10*TICK else -1 if _B[i]['c']-_B[i-N]['c'] < -10*TICK else 0)
    return _B

def trend_of(b, N): return b.get(f'tr{N}', 0)

def kq(B, s, rm):
    r = s['risk_t']*TICK
    return cbr.hit(B, s['i'], s['side'], s['sl'], s['entry']+rm*r if s['side'] == 'LONG' else s['entry']-rm*r)

def evalsig(B, sigs, rm, trendN=0, label="", show=True):
    """trendN>0 = loc THUAN trend N bars. tra (wr, net, n_closed, all_pos)."""
    if trendN:
        sigs = [s for s in sigs if trend_of(B[s['i']], trendN) == (1 if s['side'] == 'LONG' else -1)]
    bym = defaultdict(lambda: [0, 0, 0.0])  # n, tp, net
    for s in sigs:
        o = kq(B, s, rm)
        if o not in ('TP', 'SL'): continue
        m = s['dt'].strftime('%Y-%m')
        bym[m][0] += 1; bym[m][1] += (o == 'TP'); bym[m][2] += (rm if o == 'TP' else -1)
    n = sum(v[0] for v in bym.values()); tp = sum(v[1] for v in bym.values()); net = sum(v[2] for v in bym.values())
    wr = tp/n if n else 0
    allpos = all(v[2] >= 0 for v in bym.values()) and len(bym) >= 2
    if show:
        cells = "  ".join(f"{m[-2:]}:{v[2]:+.0f}R({v[1]}/{v[0]})" for m, v in sorted(bym.items()))
        flag = "✓all+" if allpos else ""
        print(f"  {label:34s} n={n:3d} WR {wr:.0%} net {net:+.1f}R {flag:6s} [{cells}]")
    return wr, net, n, allpos

def run_cbr(**kw):
    defaults = dict(RANGE_LEN=8, RANGE_MIN_T=30, RANGE_MAX_T=75, BREAK_VSA=2.0, BREAK_BODY=0.50,
                    WAIT_BARS=12, PULL_MIN=0.40, PULL_MAX=0.90, HOLD_TOL_T=2, RESUME_BODY=0.35,
                    SL_FLOOR_T=30, SL_CAP_T=70, BUF=2, COOLDOWN=15)
    defaults.update(kw)
    for k, v in defaults.items(): setattr(cbr, k, v)
    B = bars()
    return cbr.cooldown_filter(cbr.dedup(cbr.run_cbr(B)), cbr.COOLDOWN)

def run_rev(**kw):
    for k, v in kw.items(): setattr(rv, k, v)
    return rv.vwap_reversal(bars(), use_delta=kw.get('use_delta', False))
