#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MO HINH ARM->CONFIRM (dac ta user, chinh xac):
  ARM   : nen RUT RAU tai vung (choi) — KHONG can vol manh. Vao che do chuan bi.
          LONG: low cham ho tro Z, dong tren Z, rau duoi dai.  (phe ban day xuong that bai)
  HOLD  : con arm neu gia CHUA dong xuyen qua Z (chua pha vung).
  CONFIRM: trong <=W cay sau, xuat hien nen TANG MANH vol>=High -> VAO tai dong nen confirm.
          (2 nen co the cach vai cay — arm van con hieu luc neu vung chua bi pha)
So sanh: don-vung vs cum>=2 ; quet W ; vs core confluence>=2 (+0.48R). SL floor 4d, cap 6d.
"""
import sys
from datetime import datetime
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em, research as R
TICK = em.TICK
BUF = 2; WICK = em.WICK_FRAC; GATE = em.VSA_GATE
SL_FLOOR_T = 40; SL_CAP_T = 60


def active_zones(pool, t):
    return [z for z in pool if z['ready'] <= t <= z['expire']]


def cluster_size(pool, t, price, tol):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - price) / TICK <= tol:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def detect(B, pool, W, min_cluster=1, cl_tol=7, confirm_vsa=GATE):
    """arm->confirm. Tra list tin hieu."""
    raw = []
    # arm state per side: giu (zone_price, arm_bar, arm_low) cho LONG va SHORT rieng
    for i in range(em.VSA_MA + 2, len(B)):
        b = B[i]
        # 1) tim ARM moi tai bar i (moi zone)
        for z in active_zones(pool, b['dt']):
            Z = z['price']
            if b['rng'] <= 0: continue
            # LONG arm: rut rau duoi cham Z, dong tren Z
            if (b['lo'] <= Z + em.RETEST_TOL_T * TICK and b['lo'] >= Z - 12 * TICK
                    and b['c'] > Z and b['lw'] >= WICK * b['rng'] and b['cpos'] >= 0.5):
                z.setdefault('_armL', []).append((i, b['lo']))
            # SHORT arm: rut rau tren cham Z, dong duoi Z
            if (b['hi'] >= Z - em.RETEST_TOL_T * TICK and b['hi'] <= Z + 12 * TICK
                    and b['c'] < Z and b['uw'] >= WICK * b['rng'] and b['cpos'] <= 0.5):
                z.setdefault('_armS', []).append((i, b['hi']))
        # 2) xet CONFIRM tai bar i cho moi zone dang arm
        if em.gate(b):
            for z in active_zones(pool, b['dt']):
                Z = z['price']
                # LONG confirm
                arms = [a for a in z.get('_armL', []) if 0 < i - a[0] <= W]
                # disarm neu dong xuyen duoi Z
                if b['c'] < Z - BUF * TICK:
                    z['_armL'] = []
                elif arms:
                    strong = (b['brat'] >= 0.55 and b['delta'] > 0 and b['c'] > Z
                              and b['cpos'] >= 0.6 and b['vratio'] >= confirm_vsa)
                    if strong:
                        arm_low = min(a[1] for a in arms)
                        if cluster_size(pool, b['dt'], Z, cl_tol) >= min_cluster:
                            entry = b['c']
                            sl = min(arm_low - BUF * TICK, entry - SL_FLOOR_T * TICK)
                            risk = (entry - sl) / TICK
                            if 0 < risk <= SL_CAP_T:
                                raw.append(dict(i=i, dt=b['dt'], side='LONG', entry=entry, sl=sl, risk_t=risk,
                                                zone=Z, gap=i - max(a[0] for a in arms),
                                                cl=cluster_size(pool, b['dt'], Z, cl_tol)))
                            z['_armL'] = []
                # SHORT confirm
                armsS = [a for a in z.get('_armS', []) if 0 < i - a[0] <= W]
                if b['c'] > Z + BUF * TICK:
                    z['_armS'] = []
                elif armsS:
                    strongS = (b['brat'] >= 0.55 and b['delta'] < 0 and b['c'] < Z
                               and b['cpos'] <= 0.4 and b['vratio'] >= confirm_vsa)
                    if strongS:
                        arm_hi = max(a[1] for a in armsS)
                        if cluster_size(pool, b['dt'], Z, cl_tol) >= min_cluster:
                            entry = b['c']
                            sl = max(arm_hi + BUF * TICK, entry + SL_FLOOR_T * TICK)
                            risk = (sl - entry) / TICK
                            if 0 < risk <= SL_CAP_T:
                                raw.append(dict(i=i, dt=b['dt'], side='SHORT', entry=entry, sl=sl, risk_t=risk,
                                                zone=Z, gap=i - max(a[0] for a in armsS),
                                                cl=cluster_size(pool, b['dt'], Z, cl_tol)))
                            z['_armS'] = []
    # clear state
    for z in pool: z.pop('_armL', None); z.pop('_armS', None)
    # dedup
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= 6 and abs(s['entry'] - m['entry']) / TICK <= 6 for m in out):
            continue
        out.append(s)
    return out


def wr(B, sigs, rm):
    tp = sl = 0
    for s in sigs:
        r = s['risk_t'] * TICK
        tpp = s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r
        o = R.hit_target(B, s['i'], s['side'], s['sl'], tpp)
        s[f'o{rm}'] = o
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    return n, (tp / n if n else 0), ((tp * rm - sl) / n if n else 0)


B = em.load_m1(); pool = em.build_zones(B)
nd = len(set(b['dt'].date() for b in B))
print("=" * 98)
print("ARM->CONFIRM (rut rau ARM khong can vol; nen tang manh CONFIRM vol>=High; cach <=W cay). SL floor4/cap6.")
print(f"  {'cau hinh':<42}{'n':>4}{'/ng':>6} | 1.5R WR/exp | 2R WR/exp | 3R WR/exp")
configs = [
    ("don-vung, W=4", dict(W=4, min_cluster=1)),
    ("don-vung, W=6", dict(W=6, min_cluster=1)),
    ("cum>=2 (tol10), W=4", dict(W=4, min_cluster=2, cl_tol=10)),
    ("cum>=2 (tol10), W=6", dict(W=6, min_cluster=2, cl_tol=10)),
    ("cum>=2 (tol7), W=4", dict(W=4, min_cluster=2, cl_tol=7)),
    ("cum>=2 (tol7), W=6", dict(W=6, min_cluster=2, cl_tol=7)),
    ("cum>=2 (tol7), W=8", dict(W=8, min_cluster=2, cl_tol=7)),
]
for lbl, kw in configs:
    for z in pool: z.pop('_armL', None); z.pop('_armS', None)
    sg = detect(B, pool, **kw)
    ndd = len(set(s['dt'].date() for s in sg)) or 1
    n15, w15, e15 = wr(B, sg, 1.5); n2, w2, e2 = wr(B, sg, 2.0); n3, w3, e3 = wr(B, sg, 3.0)
    print(f"  {lbl:<42}{len(sg):>4}{len(sg)/ndd:>6.1f} | {w15:>3.0%}/{e15:+5.2f} | {w2:>3.0%}/{e2:+5.2f} | {w3:>3.0%}/{e3:+5.2f}")
print("  ---")
print("  (so chieu: core confluence>=2 hien tai = +0.48R@2R, ~2.8/ngay)")

# co bat 20:31 khong? (cum>=2 tol7 W6)
for z in pool: z.pop('_armL', None); z.pop('_armS', None)
sg = detect(B, pool, W=6, min_cluster=1)
h = [s for s in sg if s['dt'].strftime('%m/%d') == '07/24' and s['dt'].hour == 20 and 28 <= s['dt'].minute <= 40]
hh = [(s['dt'].strftime('%H:%M'), round(s['entry'], 1), s.get('o2.0')) for s in h]
print("\n  20:30-20:40 (don-vung W6):", hh)
print("=" * 98)
