#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIEM DINH ung vien KB4 (C3) — holdout thang 3-4/2026 (CHUA he dung khi tim tham so),
tru phi, MDD, binomial p. Muc dich: xem +41R la EDGE hay la NHIEU cua 25 lan thu."""
import math
from collections import defaultdict
import reversal_vwap as rv, entry_dxfeed as ed, probe_kb4_zone as K
import imp_reversal_sweep as IRS
TICK = K.TICK
C3 = dict(one_arm=True, one_per_day=True, leg_min=5.0, trend=True)
POCV = dict(one_arm=True, one_per_day=True, leg_min=3.0, kinds={'POC', 'D-1'})

def binom_p(k, n, p):
    """P(X>=k) voi X~Bin(n,p) — mot phia."""
    return sum(math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(k, n+1))

def run(B, sigs, rr, cost_t=0.0):
    """cost_t = phi tinh bang TICK, tru truc tiep vao ket qua moi lenh."""
    eq = 0.0; peak = 0.0; mdd = 0.0; tp = sl = 0; bym = defaultdict(float); seq = []
    for s in sorted(sigs, key=lambda x: x['i']):
        r = s['risk_t'] * TICK
        tgt = s['entry'] + rr*r if s['side'] == 'LONG' else s['entry'] - rr*r
        o = rv.hit(B, s['i'], s['side'], s['sl'], tgt)
        if o not in ('TP', 'SL', 'amb'): continue
        d = rr if o == 'TP' else -1.0
        d -= cost_t / s['risk_t']              # phi quy ve R theo risk cua chinh lenh do
        tp += (o == 'TP'); sl += (o != 'TP')
        eq += d; seq.append(d); bym[s['dt'].strftime('%Y-%m')] += d
        peak = max(peak, eq); mdd = max(mdd, peak - eq)
    n = tp + sl
    return dict(n=n, wr=tp/n if n else 0, net=eq, ev=eq/n if n else 0, mdd=mdd,
                bym=dict(bym), tp=tp)

def show(lab, r, rr):
    be = 1/(1+rr)
    cells = " ".join(f"{k[-2:]}:{v:+.0f}" for k, v in sorted(r['bym'].items()))
    p = binom_p(r['tp'], r['n'], be) if r['n'] else 1.0
    print(f"  {lab:34s} n={r['n']:4d} WR {r['wr']*100:4.1f}% (BE {be*100:.1f}%) EV {r['ev']:+.3f} "
          f"net {r['net']:+7.1f}R MDD {r['mdd']:5.1f}R p={p:.3f}  [{cells}]")

B = rv.load_dxfeed(K.DX); Z = ed.build_zones(B)
sig_c3 = K.detect(B, Z, mode='AB', **C3)
sig_poc = K.detect(B, Z, mode='AB', **POCV)
sig_kb2 = IRS.detect(B)

def win(sigs, months):
    return [s for s in sigs if (s['dt'].year, s['dt'].month) in months]
IS = {(2026,5),(2026,6),(2026,7)}
HOLD = {(2026,3),(2026,4)}

print("="*128)
print("A. CUA SO DUNG DE TIM THAM SO (5-7/2026) — so nay DA BI CHON LOC, khong dung de ket luan")
for rr in (1.5, 2.0):
    show(f"KB4-C3 @{rr}R", run(B, win(sig_c3, IS), rr), rr)
show("KB4-POC-only @1.5R", run(B, win(sig_poc, IS), 1.5), 1.5)
show("KB2 VWAP (ship) @1.5R", run(B, win(sig_kb2, IS), 1.5), 1.5)
print()
print("B. HOLDOUT THAT — 3-4/2026 (chua he dung khi tim tham so)")
for rr in (1.5, 2.0):
    show(f"KB4-C3 @{rr}R", run(B, win(sig_c3, HOLD), rr), rr)
show("KB4-POC-only @1.5R", run(B, win(sig_poc, HOLD), 1.5), 1.5)
show("KB2 VWAP (ship) @1.5R", run(B, win(sig_kb2, HOLD), 1.5), 1.5)
print()
print("C. TRU PHI (spread+slippage) tren cua so 5-7/2026, KB4-C3 @2R")
for c in (0, 1, 2, 3):
    show(f"phi {c} tick/lenh", run(B, win(sig_c3, IS), 2.0, cost_t=c), 2.0)
print()
print("D. TRU PHI — KB2 VWAP @1.5R (de so cong bang: risk lon hon nen chiu phi tot hon?)")
for c in (0, 1, 2, 3):
    show(f"phi {c} tick/lenh", run(B, win(sig_kb2, IS), 1.5, cost_t=c), 1.5)
print()
rs = [s['risk_t'] for s in win(sig_c3, IS)]
rk = [s['risk_t'] for s in win(sig_kb2, IS)]
print(f"risk TB: KB4-C3 {sum(rs)/len(rs):.1f} tick (n={len(rs)})   KB2 {sum(rk)/len(rk):.1f} tick (n={len(rk)})")
print("="*128)
