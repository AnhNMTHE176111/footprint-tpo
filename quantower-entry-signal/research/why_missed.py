#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vi sao 3 ca BO SOT khong ban? Soi tung dieu kien tai nen do."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_replay_july as R
TICK = R.TICK

CASES = [(datetime(2026,7,31,7,59), -1, "anh copy 5 — SHORT 4125.1 (pha range, hoi yeu)"),
         (datetime(2026,7,31,12,36), -1, "anh copy 3 — SHORT 4104.2 (pha range duoi, hoi lai)"),
         (datetime(2026,7,31,15,38), +1, "anh copy 2 — LONG 4098.4 (rut rau vung hop luu -> nen xac nhan)")]

B = R.load_bars(); lv = R.load_levels()
pool, vwapz = R.build_pool(B, lv)
idx = {b["time"]: b["idx"] for b in B}

for t, side, lbl in CASES:
    i = idx.get(t)
    print("="*110); print(lbl, f"  bar#{i}")
    if i is None: print("  KHONG CO BAR"); continue
    b = B[i]
    print(f"  O={b['o']} H={b['h']} L={b['l']} C={b['c']} vol={b['vol']} delta={b['delta']} "
          f"vratio={b['vratio']:.2f} brat={b['brat']:.2f} cpos={b['cpos']:.2f} ddom={b['ddom']:.2f} "
          f"uw={b['uw']:.1f} lw={b['lw']:.1f} rng={b['rng']:.1f} than={'TANG' if b['c']>b['o'] else 'GIAM'}")
    okL, wL = R.long_sig(b); okS, wS = R.short_sig(b)
    print(f"  long_sig={okL} {wL}   short_sig={okS} {wS}")
    gated = b["vol"] >= R.VOL_FLOOR and b["since_gap"] >= R.WARMUP_BARS and b["vma"] >= R.VOL_FLOOR*0.6
    print(f"  gate co ban (vol>={R.VOL_FLOOR}, since_gap>={R.WARMUP_BARS}, vma) = {gated}  (vol={b['vol']} since_gap={b['since_gap']} vma={b['vma']:.0f})")
    # vung con song gan gia
    near = [z for z in pool if not z["is_vwap"] and z["ready"] <= t <= z["expire"] and abs(z["price"]-b["c"]) <= 1.5]
    near.sort(key=lambda z: abs(z["price"]-b["c"]))
    print(f"  vung con song trong +-1.5 gia quanh close: {len(near)}")
    for z in near[:10]:
        print(f"     {z['kind']:<12} {z['price']:.1f}   cach {abs(z['price']-b['c'])/TICK:.0f} tick   cum={R.cluster_count(pool, t, z['price'])}")
    if not near: print("     (khong co vung nao) -> khong the ban KB1/KB2")
    # cum tai chinh gia vao
    print(f"  cum tai gia vao {b['c']:.1f} = {R.cluster_count(pool, t, b['c'])}")
    # 12 nen truoc: co pha vung nao khong
    print("  --- 12 nen truoc (de xem nhip pha/hoi) ---")
    for j in range(max(0,i-12), i+1):
        x = B[j]
        print(f"    {x['time']:%H:%M} O={x['o']:.1f} H={x['h']:.1f} L={x['l']:.1f} C={x['c']:.1f} v={x['vol']:.0f} d={x['delta']:+.0f} vr={x['vratio']:.1f}")
