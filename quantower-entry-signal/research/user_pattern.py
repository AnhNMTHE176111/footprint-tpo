#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST mau 2 nen dao chieu tai HO TRO (theo mo ta user):
  Nen A (choi/hammer): rut rau DUOI dai, dong nua tren, delta>=0, VSA cao -> ban that bai.
  Nen B (xac nhan)   : than dai tang, rau tren ngan, dong > dong A, delta>0, VSA cao -> mua ap dao.
  Boi canh: 2 nen ngay tren vung HO TRO (co zone active gan day nen A).
Test: entry tai B (xac nhan) vs tai A (hammer, RR tot hon). Liet ke MOI lan + ket qua de user check.
"""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em, research as R
TICK = em.TICK


def zones_active_near(pool, t, price, tol_t):
    return [z for z in pool if z['ready'] <= t <= z['expire'] and abs(z['price'] - price) / TICK <= tol_t]


def detect(B, pool, vsa_min, entry_on='B', need_cluster=False):
    """entry_on='B' vao nen xac nhan; 'A' vao nen hammer. need_cluster: yeu cau >=2 zone tai ho tro."""
    raw = []
    for i in range(em.VSA_MA + 3, len(B)):
        A = B[i - 1]; Bb = B[i]
        if not em.gate(Bb):
            continue
        # nen A: hammer rut rau duoi
        hammerA = (A['lw'] >= 0.5 * A['rng'] and A['cpos'] >= 0.5 and A['delta'] >= 0 and A['vratio'] >= vsa_min and A['rng'] > 0)
        # nen B: than dai tang, rau tren ngan
        strongB = (Bb['brat'] >= 0.55 and Bb['delta'] > 0 and Bb['c'] > A['c']
                   and Bb['uw'] <= 0.35 * Bb['rng'] and Bb['cpos'] >= 0.6 and Bb['vratio'] >= vsa_min and Bb['rng'] > 0)
        if not (hammerA and strongB):
            continue
        # ho tro: zone active gan DAY nen A (support ngay duoi)
        low = min(A['lo'], Bb['lo'])
        sup = [z for z in zones_active_near(pool, A['dt'], A['lo'], 6) if z['price'] <= A['c'] + 2 * TICK]
        # them VWAP dong
        if abs(A['vwap'] - A['lo']) / TICK <= 8 and A['vwap'] <= A['c']:
            sup.append(dict(price=A['vwap'], kind='VWAP'))
        nsup = len(set(round(z['price'] / TICK) for z in sup))
        if nsup < (2 if need_cluster else 1):
            continue
        if entry_on == 'B':
            entry = Bb['c']; ii = i
        else:
            entry = A['c']; ii = i - 1
        sl = low - 2 * TICK; risk = (entry - sl) / TICK
        if risk <= 0 or risk > 70:
            continue
        raw.append(dict(i=ii, dt=Bb['dt'], side='LONG', entry=entry, sl=sl, risk_t=risk,
                        nsup=nsup, vsaA=A['vratio'], vsaB=Bb['vratio'], dA=A['delta'], dB=Bb['delta']))
    # dedup
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(abs(s['i'] - m['i']) <= 6 and abs(s['entry'] - m['entry']) / TICK <= 6 for m in out):
            continue
        out.append(s)
    return out


def evalR(B, sigs, rm):
    tp = sl = 0
    for s in sigs:
        r = s['risk_t'] * TICK
        tpp = s['entry'] + rm * r
        o = R.hit_target(B, s['i'], 'LONG', s['sl'], tpp)
        s[f'o{rm}'] = o
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    return n, (tp / n if n else 0), ((tp * rm - sl) / n if n else 0)


B = em.load_m1(); pool = em.build_zones(B)
ndays = len(set(b['dt'].date() for b in B))
print("=" * 96)
print("MAU 2 NEN DAO CHIEU TAI HO TRO (mo ta user) — 28 ngay")
print(f"  {'bien the':<40}{'n':>4}{'/ng':>6} | 1.5R WR/exp | 2R WR/exp | 3R WR/exp")
variants = [
    ("VSA>=climax(2.2), entry B (xac nhan)", dict(vsa_min=2.2, entry_on='B', need_cluster=False)),
    ("VSA>=climax(2.2), entry A (hammer)", dict(vsa_min=2.2, entry_on='A', need_cluster=False)),
    ("VSA>=High(1.2), entry B", dict(vsa_min=1.2, entry_on='B', need_cluster=False)),
    ("VSA>=High(1.2), entry A (hammer)", dict(vsa_min=1.2, entry_on='A', need_cluster=False)),
    ("VSA>=climax, entry A, ho tro >=2 zone", dict(vsa_min=2.2, entry_on='A', need_cluster=True)),
]
best = None
for lbl, kw in variants:
    sg = detect(B, pool, **kw)
    nd = len(set(s['dt'].date() for s in sg))
    n15, w15, e15 = evalR(B, sg, 1.5); n2, w2, e2 = evalR(B, sg, 2.0); n3, w3, e3 = evalR(B, sg, 3.0)
    print(f"  {lbl:<40}{len(sg):>4}{len(sg)/max(nd,1):>6.1f} | {w15:>3.0%}/{e15:+4.2f} | {w2:>3.0%}/{e2:+4.2f} | {w3:>3.0%}/{e3:+4.2f}")
    if lbl.startswith("VSA>=High(1.2), entry A"):
        best = (lbl, sg)

# LIET KE MOI LAN cua bien the "entry A, VSA>=High" (nhieu mau nhat) -> user check thang/thua
lbl, sg = best
evalR(B, sg, 2.0)
print(f"\n### DANH SACH MOI LAN — {lbl} (out@2R) — de ban tu check tren chart:")
print(f"  {'ngay gio':<20}{'entry':>8}{'SL':>8}{'risk':>6} {'nsup':>4} {'VSA A/B':>10} {'out@2R':>7}")
tp = sl = 0
for s in sorted(sg, key=lambda x: x['dt']):
    o = s.get('o2.0', '?')
    if o == 'TP': tp += 1
    elif o == 'SL': sl += 1
    print(f"  {s['dt']:%m/%d %H:%M}      {s['entry']:>8.1f}{s['sl']:>8.1f}{s['risk_t']/10:>5.1f}d {s['nsup']:>4} "
          f"{s['vsaA']:>4.1f}/{s['vsaB']:<4.1f} {o:>7}")
print(f"\n  => {tp} TP / {sl} SL  (con lai open). LOSERS de check: ", end="")
print(", ".join(f"{s['dt']:%m/%d %H:%M}" for s in sorted(sg, key=lambda x: x['dt']) if s.get('o2.0') == 'SL'))
print("=" * 96)
