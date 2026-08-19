#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calib_hvn_dense.py — hieu chinh lai cong HVN cua SessionZones tren DU LIEU DAY.

Ly do: cong MinHvnRatio = 2.0 (B8) duoc hieu chinh tren file MONG
(Data_Footprint_Export.csv, ~18k hop dong/ngay). File moi GC:XCEC 2026-07-20..08-19
day gap 5 lan (~101k hop dong/ngay) -> hinh dang profile khac -> ti le HVN/trung binh
co the lech han. Script nay do lai:
  1. So MOC HVN moi phien truoc/sau cong, phan bo ti le
  2. Be rong "nen" quanh dinh (PeakSharpness 90%)
  3. HAI MA cung 27 ngay (/GC:XCEC lien tuc vs GCZ26 hop dong that) co ra
     cung moc HVN khong — quan trong vi nguoi dung vua doi chart sang /GC:XCEC

Port 1-1 tu ProfileEngine.FindHvn + ProfileEngine.PeakSharpness (C#).
Chay:  python3 quantower-tpo-suite/calib_hvn_dense.py
"""
import csv
import os
import statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICK = 0.1
MAX_HVN = 3          # SessionZones.MaxHvn
GATE = 2.0           # SessionZones.MinHvnRatio (B8)
TARGET_GATE = 2.5    # SessionZones.TargetMinRatio


def load_day_profiles(path):
    """day[ngay][gia] = volume, gom theo tung tick."""
    day = defaultdict(lambda: defaultdict(float))
    with open(path, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            day[r['datetime'][:10]][round(float(r['price']), 1)] += float(r['volume'])
    return day


def find_hvn(rows, tick=TICK, smooth_ticks=5, min_ratio=1.5, min_sep_ticks=0):
    """Port cua ProfileEngine.FindHvn — tra [(price, ratio)] da sap theo do manh."""
    if not rows or len(rows) < 3:
        return []
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    n = len(w)
    avg = sum(w) / n
    if avg <= 0:
        return []

    if min_sep_ticks <= 0:
        width_ticks = (prices[-1] - prices[0]) / tick
        min_sep_ticks = min(120, max(20, width_ticks * 0.08))

    sm = []
    for i in range(n):
        a, z = max(0, i - smooth_ticks), min(n - 1, i + smooth_ticks)
        sm.append(sum(w[a:z + 1]) / (z - a + 1))

    peaks = []
    for i in range(1, n - 1):
        if sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] >= min_ratio * avg:
            peaks.append((prices[i], sm[i], sm[i] / avg))

    res = []
    for p, weight, ratio in sorted(peaks, key=lambda x: -x[1]):
        if all(abs(p - k[0]) / tick >= min_sep_ticks for k in res):
            res.append((p, ratio))
    return res


def peak_sharpness(rows, peak_price, tick=TICK, frac=0.90):
    """Port cua ProfileEngine.PeakSharpness — noi 2 ben tu dinh toi khi tut duoi frac."""
    prices = sorted(rows)
    if peak_price not in rows:
        return (peak_price, peak_price)
    top = rows[peak_price]
    i = prices.index(peak_price)
    lo = hi = i
    while lo > 0 and rows[prices[lo - 1]] >= frac * top:
        lo -= 1
    while hi < len(prices) - 1 and rows[prices[hi + 1]] >= frac * top:
        hi += 1
    return (prices[lo], prices[hi])


def q(vals, p):
    if not vals:
        return float('nan')
    s = sorted(vals)
    k = (len(s) - 1) * p
    f = int(k)
    return s[f] if f + 1 >= len(s) else s[f] + (s[f + 1] - s[f]) * (k - f)


def report(name, path):
    day = load_day_profiles(path)
    days = sorted(day)
    n_before, n_after, n_target, ratios, bands = [], [], [], [], []
    hvn_by_day = {}
    for d in days:
        rows = day[d]
        if len(rows) < 50:            # bo phien cut (nghi le / du lieu vun)
            continue
        hv = find_hvn(rows)[:MAX_HVN]
        hvn_by_day[d] = hv
        n_before.append(len(hv))
        kept = [(p, r) for p, r in hv if r >= GATE]
        n_after.append(len(kept))
        n_target.append(sum(1 for _, r in hv if r >= TARGET_GATE))
        for p, r in hv:
            ratios.append(r)
            lo, hi = peak_sharpness(rows, p)
            bands.append(hi - lo)

    print(f"\n=== {name} ===")
    print(f"  phien dung duoc: {len(n_before)}  ({days[0]} -> {days[-1]})")
    print(f"  moc HVN/phien:  truoc cong = {st.mean(n_before):.2f}   "
          f"sau cong x{GATE} = {st.mean(n_after):.2f}   "
          f"dat muc tieu x{TARGET_GATE} = {st.mean(n_target):.2f}")
    print(f"  ti le HVN/TB:   trung vi x{st.median(ratios):.2f}   "
          f"p25 x{q(ratios,.25):.2f}   p75 x{q(ratios,.75):.2f}   max x{max(ratios):.2f}")
    print(f"  qua cong x{GATE}: {100*sum(1 for r in ratios if r>=GATE)/len(ratios):.0f}% so moc")
    print(f"  nen quanh dinh (gia): trung vi {st.median(bands):.1f}   "
          f"p75 {q(bands,.75):.1f}   <=1 gia: {100*sum(1 for b in bands if b<=1.0)/len(bands):.0f}%")
    return hvn_by_day


def compare(a, b, name_a, name_b, tol=1.0):
    """Hai ma co ra cung moc HVN manh nhat trong cung ngay khong?"""
    common = sorted(set(a) & set(b))
    same, diffs = 0, []
    for d in common:
        if not a[d] or not b[d]:
            continue
        pa, pb = a[d][0][0], b[d][0][0]
        if abs(pa - pb) <= tol:
            same += 1
        else:
            diffs.append((d, pa, pb, pb - pa))
    n = sum(1 for d in common if a[d] and b[d])
    print(f"\n=== {name_a} vs {name_b}: moc HVN MANH NHAT co trung nhau? ===")
    print(f"  ngay chung: {n}   lech <= {tol} gia: {same}/{n} ({100*same/n:.0f}%)")
    if diffs:
        print(f"  {len(diffs)} ngay lech:")
        for d, pa, pb, dl in diffs[:12]:
            print(f"    {d}  {name_a}={pa:.1f}  {name_b}={pb:.1f}  lech {dl:+.1f} gia")


if __name__ == "__main__":
    base = os.path.join(ROOT, 'data-export')
    thin = report('MONG — Data_Footprint_Export (128 phien, ~18k HD/ngay)',
              os.path.join(base, 'Data_Footprint_Export.csv'))
    xcec = report('DAY — /GC:XCEC 2026-07-20..08-19 (~101k HD/ngay)',
              os.path.join(base, 'data-footprint/fp_GC_XCEC_Time_20260720-20260819_30d.csv'))
    gcz = report('DAY — GCZ26 cung khoang',
             os.path.join(base, 'data-footprint/fp_GCZ26_XCEC_Time_20260720-20260819_29d23h.csv'))
    compare(xcec, gcz, '/GC:XCEC', 'GCZ26')
