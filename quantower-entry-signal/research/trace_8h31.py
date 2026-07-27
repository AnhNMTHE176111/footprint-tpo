#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRACE nen 7/24 20:31 (8:31 PM) gia ~4051.8: co bi sot that khong? Old vs New."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
B = em.load_m1(); pool = em.build_zones(B)

# 1) tim nen quanh 20:25-20:45 ngay 7/24
print("=== NEN 7/24 20:20 -> 20:45 (gia, delta, vsa, vwap) ===")
idx8 = None
for i, b in enumerate(B):
    if b['dt'].strftime('%m/%d') == '07/24' and 20 <= b['dt'].hour and 20 <= b['dt'].minute + b['dt'].hour * 60 - 20 * 60 <= 45:
        star = " <==" if abs(b['c'] - 4051.8) < 0.6 else ""
        print(f"  {b['dt']:%H:%M} O{b['o']:.1f} H{b['hi']:.1f} L{b['lo']:.1f} C{b['c']:.1f} "
              f"Δ{b['delta']:+.0f} vsa{b['vratio']:.1f}x vwap{b['vwap']:.1f} cpos{b['cpos']:.2f} "
              f"brat{b['brat']:.2f} lw{b['lw']:.1f} uw{b['uw']:.1f}{star}")
        if abs(b['c'] - 4051.8) < 0.7 and star: idx8 = i

# fallback: nen gan 4051.8 nhat trong 20:28-20:34
if idx8 is None:
    cand = [i for i, b in enumerate(B) if b['dt'].strftime('%m/%d') == '07/24' and b['dt'].hour == 20 and 28 <= b['dt'].minute <= 34]
    if cand: idx8 = min(cand, key=lambda i: abs(B[i]['c'] - 4051.8))
print(f"\n  -> chon nen idx={idx8} luc {B[idx8]['dt']:%H:%M} C={B[idx8]['c']:.1f}" if idx8 else "  KHONG thay nen 4051.8!")

if idx8:
    b = B[idx8]; t = b['dt']
    # 2) vung active gan 4051.8
    print(f"\n=== VUNG ACTIVE gan {b['c']:.1f} (trong 15 tick) luc {t:%H:%M} ===")
    near = []
    vwapz = ('VWAP', b['vwap'])
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - b['c']) / TICK <= 15:
            near.append((z['kind'], z['price']))
    near.append(vwapz)
    for k, p in sorted(near, key=lambda x: x[1]):
        d = (p - b['c']) / TICK
        print(f"    {k:<14} {p:.1f}  ({d:+.0f}t)")
    # cum trong 7t quanh 4051.8
    prices = sorted(set(round(p / TICK) for k, p in near if abs(p - b['c']) / TICK <= 10))
    print(f"    -> so muc KHAC NHAU trong ~10t quanh nen: {len(prices)}")

    # 3) tin hieu OLD (trigger) va cluster tren toan bo
    def with_cluster(B, pool):
        raw = em.run(B, pool)
        for s in raw:
            zp = float(s['zone'].split()[-1]); tt = s['dt']; seen = set()
            for z in pool:
                if z['ready'] <= tt <= z['expire'] and abs(z['price'] - zp) / TICK <= 7:
                    seen.add(round(z['price'] / TICK))
            s['cluster'] = len(seen)
        return raw
    raw = with_cluster(B, pool)
    sig = em.dedup(raw)
    for s in sig: s.setdefault('cluster', 1)
    print(f"\n=== TIN HIEU trong 20:25-20:40 (raw + sau dedup) ===")
    for s in raw:
        if s['dt'].strftime('%m/%d') == '07/24' and s['dt'].hour == 20 and 25 <= s['dt'].minute <= 40:
            print(f"  RAW {s['dt']:%H:%M} {s['side']:<5} {s['scen']:<16} zone={s['zone']:<14} cluster={s.get('cluster')} entry{s['entry']:.1f} | {s['why']}")
    hit = [s for s in sig if s['dt'].strftime('%m/%d') == '07/24' and s['dt'].hour == 20 and 25 <= s['dt'].minute <= 40]
    print(f"  sau dedup+gate: {len(hit)} tin hieu")
    for s in hit:
        print(f"    {s['dt']:%H:%M} {s['side']} confl={s['confl']} cluster={s['cluster']} -> "
              f"{'GATE cu(trigger>=2): PASS' if s['confl']>=2 else 'GATE cu: LOAI'} | "
              f"{'GATE moi(cluster>=2): PASS' if s['cluster']>=2 else 'GATE moi: LOAI'}")

    # 4) tai sao nen 20:31 co bat khong: chay long_sig/short_sig thu
    print(f"\n=== NEN {t:%H:%M} co thoa dieu kien NEN TIN HIEU khong? ===")
    okL, wL = em.long_sig(b); okS, wS = em.short_sig(b)
    print(f"  long_sig={okL} {wL}")
    print(f"  short_sig={okS} {wS}")
    print(f"  gate volume/warmup: {em.gate(b)} (v={b['v']:.0f} since_gap={b['since_gap']} vma={b['vma']:.0f})")
print("=" * 90)
