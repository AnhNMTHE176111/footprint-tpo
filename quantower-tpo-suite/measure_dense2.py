#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measure_dense2.py — dao sau sau khi measure_dense.py cho thay:
  - HVN >= x3.0 thang 44.8% (n=116) trong khi muc ngau nhien chi 33.8%
  - cac buoc ti le thap hon deu ~36-37%, khong hon gi ngau nhien
Cau hoi tiep: (1) HVN TUAN co hon HVN ngay khong — day la thu trader pro thuc dung;
(2) danh nguoc (fade) hay danh thuan (follow); (3) mua va ban co khac nhau;
(4) nang nguong len nua thi sao.

DEM SO RO DA THU va in ra cuoi cung — de khong tu lua minh bang khop qua muc.
"""
import math, os, random, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dense_prep import load
from calib_hvn_dense import find_hvn
from measure_dense import (SL, TP, HORIZON, FLOOR, wilson, first_touch,
                           try_level, evaluate, row, EXTRA_ROLL, ROLL_PAD)

RNG = random.Random(11)
TRIED = []


def ev(name, cases, note=''):
    r = evaluate(cases)
    TRIED.append(name)
    print(row('  ' + name, r) + (('  ' + note) if note else ''))
    return r


def evaluate_side(cases, want):
    """chi giu ca co huong tiep can = want (+1 mua/-1 ban)."""
    w = l = 0
    for bars, lv in cases:
        if len(bars) < HORIZON + 5:
            continue
        t = first_touch(bars, lv)
        if t is None or t[1] != want:
            continue
        r = try_level(bars, t[0], t[1])
        if r == 1: w += 1
        elif r == 0: l += 1
    n = w + l
    if n == 0: return dict(n=0)
    lo, hi = wilson(w, n)
    return dict(n=n, wr=w/n, lo=lo, hi=hi, timeout=0, exp=(w*TP-l*SL)/n)


def evaluate_follow(cases):
    """danh THUAN huong tiep can (xuyen qua) thay vi fade."""
    w = l = 0
    for bars, lv in cases:
        if len(bars) < HORIZON + 5:
            continue
        t = first_touch(bars, lv)
        if t is None:
            continue
        r = try_level(bars, t[0], -t[1])
        if r == 1: w += 1
        elif r == 0: l += 1
    n = w + l
    if n == 0: return dict(n=0)
    lo, hi = wilson(w, n)
    return dict(n=n, wr=w/n, lo=lo, hi=hi, timeout=0, exp=(w*TP-l*SL)/n)


def zdiff(a, b):
    if not a.get('n') or not b.get('n'):
        return None
    se = math.sqrt(a['wr']*(1-a['wr'])/a['n'] + b['wr']*(1-b['wr'])/b['n'])
    return (a['wr']-b['wr'])/se if se else 0


def main():
    d = load()
    prof, sess = d['profiles'], d['sessions']
    rolls = set(d['rolls']) | set(EXTRA_ROLL)
    days = sorted(sess)
    idx = {x: i for i, x in enumerate(days)}
    bad = set()
    for i, dd in enumerate(days):
        if dd in rolls:
            for j in range(max(0, i-ROLL_PAD), min(len(days), i+ROLL_PAD+1)):
                bad.add(days[j])
    use = [x for x in days if x not in bad]

    print("="*100)
    print("DAO SAU — du lieu day 748 ngay, giao thuc SL 3 / TP 4.5 / 60 nen M1")
    print("="*100)

    # ---- gom moc ------------------------------------------------------
    day_cases, wk_cases = [], []      # (bars, level, ratio)
    for dd in use:
        i = idx[dd]
        if i < 6:
            continue
        p = days[i-1]
        if p in bad:
            continue
        # HVN NGAY
        if p in prof and len(prof[p]) >= 50:
            for lv, r in find_hvn(prof[p])[:3]:
                day_cases.append((sess[dd], lv, r))
        # HVN TUAN — gop 5 phien sach lien truoc
        wk = defaultdict(float)
        cnt = 0
        for j in range(i-1, max(-1, i-9), -1):
            dj = days[j]
            if dj in bad or dj not in prof:
                continue
            for k, v in prof[dj].items():
                wk[k] += v
            cnt += 1
            if cnt == 5:
                break
        if cnt == 5 and len(wk) >= 50:
            for lv, r in find_hvn(dict(wk))[:3]:
                wk_cases.append((sess[dd], lv, r))

    # ---- doi chung ----------------------------------------------------
    rnd = []
    for dd in use:
        i = idx[dd]
        if i < 1: continue
        p = days[i-1]
        if p in bad or p not in prof or len(prof[p]) < 50: continue
        ps = sorted(prof[p])
        for _ in range(3):
            rnd.append((sess[dd], round(RNG.uniform(ps[0], ps[-1]), 1)))
    base = evaluate(rnd)
    print(f"\nNEN SO SANH — muc ngau nhien trong bien do phien truoc: "
          f"n={base['n']}, thang {100*base['wr']:.1f}%")

    print("\n--- 1. HVN TUAN (gop 5 phien) so voi HVN NGAY, theo buoc ti le ---")
    for nm, cs in [('NGAY', day_cases), ('TUAN', wk_cases)]:
        print(f"  [{nm}]  tong moc={len(cs)}")
        for lbl, a, b in [('x1.5-2.5', 1.5, 2.5), ('x2.5-3.0', 2.5, 3.0),
                          ('x3.0-4.0', 3.0, 4.0), ('x4.0+', 4.0, 99)]:
            r = ev(f"HVN {nm} {lbl}", [(bb, lv) for bb, lv, rr in cs if a <= rr < b])
        for g in (2.5, 3.0, 3.5):
            sub = [(bb, lv) for bb, lv, rr in cs if rr >= g]
            r = ev(f"HVN {nm} >= x{g}", sub)
            z = zdiff(r, base)
            if z is not None:
                print(f"        so voi ngau nhien: z={z:+.2f}"
                      + ("  <== KHAC BIET" if abs(z) >= 1.96 else ""))

    print("\n--- 2. Fade hay Follow? (dung moc manh >= x3.0) ---")
    for nm, cs in [('NGAY', day_cases), ('TUAN', wk_cases)]:
        sub = [(bb, lv) for bb, lv, rr in cs if rr >= 3.0]
        TRIED.append(f'follow {nm}')
        print(row(f"  HVN {nm} >=x3.0  FADE (danh nguoc)", evaluate(sub)))
        print(row(f"  HVN {nm} >=x3.0  FOLLOW (danh thuan)", evaluate_follow(sub)))

    print("\n--- 3. Mua hay Ban? (moc manh >= x3.0, fade) ---")
    for nm, cs in [('NGAY', day_cases), ('TUAN', wk_cases)]:
        sub = [(bb, lv) for bb, lv, rr in cs if rr >= 3.0]
        for side, lb in [(1, 'toi tu TREN -> MUA do'), (-1, 'toi tu DUOI -> BAN can')]:
            TRIED.append(f'side {nm} {lb}')
            print(row(f"  HVN {nm} >=x3.0 {lb}", evaluate_side(sub, side)))

    print(f"\n>>> TONG SO RO DA THU trong file nay: {len(TRIED)}")
    print(">>> Voi ngan ay ro, mot ro ngau nhien cung co the 'dat' — ro nao dat phai")
    print("    kiem lai tren khoang thoi gian khac truoc khi tin.")


if __name__ == '__main__':
    main()
