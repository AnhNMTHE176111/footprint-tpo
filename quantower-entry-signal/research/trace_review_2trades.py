#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRACE 2 lenh user review (07/23 08:03 LONG 4136.1 ; 07/23 18:20 LONG 4088.0).
Muc dich: doi chieu voi chart user, xem lai:
  - lenh 1: pha co bi rut rau tren manh? retest co "chua dong tren vung"?
  - lenh 2: entry co phai "gia pha va vao luon" (retest nong) khong? 19:20 co phai nhip hoi that?
In tung nen quanh entry + trang thai zone + do sau hoi (retracement cua chan pha).
Don vi: 'gia' = 1.0 diem gia (= 10 tick, TICK=0.1).
"""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK


def barflags(b):
    ls, lw = em.long_sig(b)
    ss, sw = em.short_sig(b)
    tags = []
    if ls: tags.append("LONGsig")
    if ss: tags.append("SHORTsig")
    if b['lw'] >= em.WICK_FRAC * b['rng'] and b['rng'] > 0: tags.append("rau-duoi")
    if b['uw'] >= em.WICK_FRAC * b['rng'] and b['rng'] > 0: tags.append("rau-tren")
    if b['brat'] >= 0.55: tags.append("than-manh")
    return " ".join(tags)


def dump(B, i0, i1, zprice=None):
    print(f"  {'gio':<6}{'O':>8}{'H':>8}{'L':>8}{'C':>8}{'body%':>6}{'uw%':>5}{'lw%':>5}"
          f"{'delta':>7}{'ddom':>6}{'VSA':>5}{'cpos':>5}  flags")
    for j in range(i0, i1):
        b = B[j]
        uwp = 100 * b['uw'] / b['rng'] if b['rng'] > 0 else 0
        lwp = 100 * b['lw'] / b['rng'] if b['rng'] > 0 else 0
        rel = ""
        if zprice is not None:
            rel = " ABOVE" if b['c'] > zprice + 0.2 else (" below" if b['c'] < zprice - 0.2 else " ==in==")
        print(f"  {b['dt']:%H:%M} {b['o']:>8.1f}{b['hi']:>8.1f}{b['lo']:>8.1f}{b['c']:>8.1f}"
              f"{100*b['brat']:>5.0f}%{uwp:>4.0f}%{lwp:>4.0f}%{b['delta']:>7.0f}{b['ddom']:>6.2f}"
              f"{b['vratio']:>5.1f}{b['cpos']:>5.2f} {barflags(b)}{rel}")


def cluster(pool, t, zp, tol=7):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= tol:
            seen.add((round(z['price'], 1), z['kind']))
    return sorted(seen)


B = em.load_m1()
pool = em.build_zones(B)
raw = em.run(B, pool)
sig = em.dedup(raw)
idx = {b['dt']: i for i, b in enumerate(B)}

for label, day, hh, mm, entry_px in [("LENH 1", "07/23", 8, 3, 4136.1), ("LENH 2", "07/23", 18, 20, 4088.0)]:
    match = [s for s in sig if s['dt'].strftime('%m/%d') == day and s['dt'].hour == hh and abs(s['dt'].minute - mm) <= 1
             and abs(s['entry'] - entry_px) / TICK <= 8]
    print("=" * 104)
    if not match:
        print(f"{label}: KHONG tim thay signal khop {day} {hh:02d}:{mm:02d} entry~{entry_px}")
        continue
    s = match[0]; i = s['i']
    zp = float(s['zone'].split()[-1])
    print(f"{label}: {s['dt']:%Y-%m-%d %H:%M} {s['side']} {s['scen']}  entry {s['entry']:.1f} SL {s['sl']:.1f}"
          f"  risk {s['risk_t']/10:.1f} gia  VSA {s['vsa']:.1f}")
    print(f"  vung chinh: {s['zone']}  | cac vung gop (confluence): {s['zones']}")
    print(f"  cum >=? quanh {zp:.1f} (±7 tick): {cluster(pool, s['dt'], zp)}")
    print(f"  why: {s['why']}")
    # tim chan pha (broke_up bar) trong 12 nen truoc entry
    print(f"\n  -- Nen tu {B[i-14]['dt']:%H:%M} den {B[i+5]['dt']:%H:%M} (entry o {B[i]['dt']:%H:%M}, vung {zp:.1f}) --")
    dump(B, i - 14, i + 6, zp)
    # do sau hoi: dinh cao nhat giua break va entry so voi vung
    seg = B[max(0, i-12):i+1]
    peak = max(x['hi'] for x in seg)
    retest_low = B[i]['lo']
    leg = peak - zp
    pull = (peak - retest_low) / leg if leg > 0 else 0
    print(f"\n  Do sau hoi: dinh chan pha ~{peak:.1f}, vung {zp:.1f}, chan pha = {peak-zp:.1f} gia; "
          f"retest low {retest_low:.1f} -> hoi lai {100*pull:.0f}% chan pha "
          f"({'NONG <38%' if pull < 0.38 else 'vua/sau'}).")

# LENH 2: soi them 19:00 - 19:40 (user noi 19:20 moi la nhip hoi that)
print("=" * 104)
print("LENH 2 — soi 18:10 -> 19:40 (user: 19:20 moi la entry hoi that):")
t0 = None
for i, b in enumerate(B):
    if b['dt'].strftime('%m/%d') == '07/23' and b['dt'].hour == 18 and b['dt'].minute == 10:
        t0 = i; break
if t0:
    dump(B, t0, t0 + 92, None)
print("=" * 104)
