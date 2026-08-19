#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_window.py — SessionZones dang lay "ngay" = 24 GIO CUOI
(`dayStart = completed.Last.End.AddHours(-24)`), khong phai PHIEN that
(nghi -> nghi). Cua so 24h truot vat qua gio nghi nen tron duoi phien truoc
vao dau phien hien tai.

Script nay tra loi: co khac that khong, va cach nao cho moc tot hon?
"""
import os, sys, random, statistics as st
from collections import defaultdict
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dense_prep import load, load_hours
from calib_hvn_dense import find_hvn
from measure_dense import (HORIZON, first_touch, try_level, wilson,
                           EXTRA_ROLL, ROLL_PAD, TP, SL)


def hkey(dt):
    return dt.strftime('%Y-%m-%d %H')


def wr(cases):
    w = l = 0
    for bars, lv in cases:
        if len(bars) < HORIZON + 5: continue
        t = first_touch(bars, lv)
        if t is None: continue
        r = try_level(bars, t[0], t[1])
        if r == 1: w += 1
        elif r == 0: l += 1
    n = w + l
    if not n: return dict(n=0)
    lo, hi = wilson(w, n)
    return dict(n=n, wr=w/n, lo=lo, hi=hi, exp=(w*TP-l*SL)/n)


def show(nm, r):
    if not r.get('n'):
        print(f"  {nm:<40} chua co ca"); return
    print(f"  {nm:<40} n={r['n']:>4}  thang={100*r['wr']:5.1f}%  "
          f"CI95=[{100*r['lo']:4.1f}%,{100*r['hi']:5.1f}%]  ky vong={r['exp']:+5.2f} gia")


def main():
    d = load(); hours = load_hours()
    sess, prof = d['sessions'], d['profiles']
    rolls = set(d['rolls']) | set(EXTRA_ROLL)
    days = sorted(sess); idx = {x: i for i, x in enumerate(days)}
    bad = set()
    for i, dd in enumerate(days):
        if dd in rolls:
            for j in range(max(0, i-ROLL_PAD), min(len(days), i+ROLL_PAD+1)):
                bad.add(days[j])

    sess_cases, roll_cases = [], []
    same = tot = 0
    dists = []
    for dd in days:
        i = idx[dd]
        if i < 1 or dd in bad: continue
        p = days[i-1]
        if p in bad or p not in prof or len(prof[p]) < 50: continue

        # (a) PHIEN that
        a = find_hvn(prof[p])[:3]
        # (b) cua so 24 GIO cuoi, ket thuc o bar cuoi cua phien p
        end = datetime.strptime(sess[p][-1][0], '%Y-%m-%d %H:%M:%S')
        agg = defaultdict(float)
        for k in range(24):
            hk = hkey(end - timedelta(hours=k))
            for pr, v in hours.get(hk, {}).items():
                agg[pr] += v
        b = find_hvn(dict(agg))[:3] if len(agg) >= 50 else []

        if a and b:
            tot += 1
            if abs(a[0][0] - b[0][0]) <= 1.0:
                same += 1
            dists.append(abs(a[0][0] - b[0][0]))
        for lv, r in a:
            sess_cases.append((sess[dd], lv, r))
        for lv, r in b:
            roll_cases.append((sess[dd], lv, r))

    print("="*92)
    print("PHIEN THAT (nghi->nghi)  vs  CUA SO 24 GIO TRUOT (cach SessionZones dang dung)")
    print("="*92)
    print(f"\nso phien so sanh duoc: {tot}")
    print(f"moc manh nhat trung nhau (lech <= 1 gia): {same}/{tot} ({100*same/tot:.0f}%)")
    print(f"khoang cach 2 moc: trung vi {st.median(dists):.1f} gia   "
          f"trung binh {st.mean(dists):.1f} gia   max {max(dists):.1f} gia")

    print(f"\n--- ket qua giao dich (SL 3 / TP 4.5 / 60 nen, fade lan cham dau) ---")
    for gate in (1.5, 2.5, 3.0, 3.5):
        print(f"  [cong >= x{gate}]")
        show(f"  PHIEN that", wr([(b_, lv) for b_, lv, r in sess_cases if r >= gate]))
        show(f"  24h truot", wr([(b_, lv) for b_, lv, r in roll_cases if r >= gate]))

    # so moc sinh ra
    print(f"\n--- so moc sinh ra moi phien ---")
    ns = len({0})
    for nm, cs in [('PHIEN that', sess_cases), ('24h truot', roll_cases)]:
        for gate in (2.5, 3.0):
            k = sum(1 for _, _, r in cs if r >= gate)
            print(f"  {nm:<12} cong x{gate}: {k/tot:.2f} moc/phien")


if __name__ == '__main__':
    main()
