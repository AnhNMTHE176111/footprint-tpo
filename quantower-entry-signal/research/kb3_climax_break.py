#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nen 20:31 bi bo vi: (1) la nen PHA cum tu duoi len (khong phai retest, khong phai cham-tu-tren)
-> khong khop KB1/KB2; (2) delta +19 tren climax volume => ddom~0.08 < 0.25 -> long_sig=False.
CAU HOI: them "KB3 climax PHA qua cum >=2" co EDGE khong? Test trung thuc tren 28 ngay.
"""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em, research as R
TICK = em.TICK
B = em.load_m1(); pool = em.build_zones(B)


def clusters_at(t, lo_price, hi_price):
    """Tra cac cum >=2 (list tam gia trung binh) active luc t."""
    ps = sorted(set(round(z['price'] / TICK) * TICK for z in pool
                    if z['ready'] <= t <= z['expire'] and lo_price - 3 <= z['price'] <= hi_price + 3))
    clus = []; cur = [ps[0]] if ps else []
    for p in ps[1:]:
        if (p - cur[-1]) / TICK <= 7: cur.append(p)
        else:
            if len(cur) >= 2: clus.append(sum(cur) / len(cur))
            cur = [p]
    if len(cur) >= 2: clus.append(sum(cur) / len(cur))
    return clus


def kb3(B, climax=em.VSA_CLIMAX, need_dom=False):
    raw = []
    for i in range(em.VSA_MA + 2, len(B)):
        b = B[i]; pb = B[i - 1]
        if not em.gate(b): continue
        if b['vratio'] < climax: continue
        for c in clusters_at(b['dt'], b['lo'], b['hi']):
            # LONG: pha len qua cum (prev duoi cum, nay dong tren cum)
            up = pb['c'] < c - 2 * TICK and b['c'] > c and b['cpos'] >= 0.6 and b['delta'] >= 0 and b['brat'] >= 0.4
            dn = pb['c'] > c + 2 * TICK and b['c'] < c and b['cpos'] <= 0.4 and b['delta'] <= 0 and b['brat'] >= 0.4
            if need_dom:
                up = up and b['ddom'] >= 0.15
                dn = dn and b['ddom'] <= -0.15
            if up:
                sl = min(b['lo'], c) - 2 * TICK; risk = (b['c'] - sl) / TICK
                if 0 < risk <= 60: raw.append(dict(i=i, dt=b['dt'], side='LONG', entry=b['c'], sl=sl, risk_t=risk, c=c))
            elif dn:
                sl = max(b['hi'], c) + 2 * TICK; risk = (sl - b['c']) / TICK
                if 0 < risk <= 60: raw.append(dict(i=i, dt=b['dt'], side='SHORT', entry=b['c'], sl=sl, risk_t=risk, c=c))
    # dedup theo bar+gia
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= 6 and abs(s['entry'] - m['entry']) / TICK <= 6 for m in out):
            continue
        out.append(s)
    return out


def wr_exp(sigs, rm):
    tp = sl = 0
    for s in sigs:
        r = s['risk_t'] * TICK
        tpp = s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r
        o = R.hit_target(B, s['i'], s['side'], s['sl'], tpp)
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    return n, (tp / n if n else 0), ((tp * rm - sl) / n if n else 0)


print("=" * 88)
print("KB3 'climax PHA qua cum >=2' — co edge khong? (28 ngay)")
for lbl, sigs in [("climax pha cum (khong ep dom)", kb3(B, need_dom=False)),
                  ("climax pha cum + dom nhe", kb3(B, need_dom=True))]:
    nd = len(set(s['dt'].date() for s in sigs))
    n2, w2, e2 = wr_exp(sigs, 2.0); n3, w3, e3 = wr_exp(sigs, 3.0)
    n15, w15, e15 = wr_exp(sigs, 1.5)
    print(f"\n  {lbl}: {len(sigs)} lenh / {nd} ngay = {len(sigs)/max(nd,1):.1f}/ngay")
    print(f"    1.5R WR{w15:.0%} exp{e15:+.2f} | 2R WR{w2:.0%} exp{e2:+.2f} | 3R WR{w3:.0%} exp{e3:+.2f}")

# co bat duoc nen 20:31 khong?
k = kb3(B, need_dom=False)
hit = [s for s in k if s['dt'].strftime('%m/%d') == '07/24' and s['dt'].hour == 20 and 28 <= s['dt'].minute <= 34]
print(f"\n  -> nen 20:31 (4051.8): KB3 bat duoc = {len(hit)>0}")
for s in hit:
    o2 = R.hit_target(B, s['i'], s['side'], s['sl'], s['entry'] + 2 * s['risk_t'] * TICK)
    print(f"     {s['dt']:%H:%M} {s['side']} entry{s['entry']:.1f} SL{s['sl']:.1f} cum{s['c']:.1f} -> out@2R={o2}")
print("=" * 88)
