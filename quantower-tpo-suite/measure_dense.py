#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measure_dense.py — chay lai bo do "moc nao dang ve" tren DU LIEU DAY 748 ngay.

Khac ban cu (measure_levels.py) o 4 diem:
  1. Nguon: /GC:XCEC 529 phien, ~143k hop dong/phien (ban cu: 127 phien, 657 HD/phien)
  2. Phien chia theo gio nghi CME, khong theo ngay lich UTC (xem dense_prep.py)
  3. LOAI phien nhiem cho noi hop dong cua ma lien tuc
  4. Do theo TUNG BUOC ti le (x1.5-2, x2-2.5, x2.5-3, x3+) de tra loi thang cau hoi
     cua cong MinHvnRatio: cong cao hon co that su loc ra moc tot hon khong?

Giao thuc giu NGUYEN de so sanh duoc: SL 3 gia / TP 4.5 gia / toi da 60 nen M1,
vao lenh tai lan CHAM DAU TIEN trong phien, danh NGUOC huong tiep can (fade).
Nen hoa von = 40%.

Chay:  DENSE_CACHE=... python3 quantower-tpo-suite/measure_dense.py
"""
import math
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dense_prep import load                                    # noqa: E402
from calib_hvn_dense import find_hvn, peak_sharpness           # noqa: E402

SL, TP, HORIZON = 3.0, 4.5, 60
FLOOR = 0.40
RNG = random.Random(7)
ROLL_PAD = 2          # loai +-N phien quanh cho noi hop dong
# cho noi KHONG bat duoc bang buoc nhay (chenh lech hai hop dong qua nho)
# nhung van roi vao cua so doi hop dong -> loai thu cong cho chac
EXTRA_ROLL = ['2024-11-26', '2025-01-28', '2026-03-25']


def wilson(w, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = w / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - a) / d, (c + a) / d)


def first_touch(bars, level):
    """bars = [(dt, o, h, l, c)]. Tra (k, side) lan cham dau tien."""
    for k in range(1, len(bars)):
        if bars[k][3] <= level <= bars[k][2]:
            return k, (1 if bars[k - 1][4] > level else -1)
    return None


def try_level(bars, k0, side):
    entry = bars[k0][4]
    sl_p = entry - SL * side
    tp_p = entry + TP * side
    for j in range(k0 + 1, min(k0 + 1 + HORIZON, len(bars))):
        h, l = bars[j][2], bars[j][3]
        if (l <= sl_p) if side > 0 else (h >= sl_p):
            return 0
        if (h >= tp_p) if side > 0 else (l <= tp_p):
            return 1
    return None


def evaluate(cases):
    """cases = [(bars, level)] -> thong ke."""
    w = l = t = 0
    for bars, lv in cases:
        if len(bars) < HORIZON + 5:
            continue
        touch = first_touch(bars, lv)
        if touch is None:
            continue
        r = try_level(bars, touch[0], touch[1])
        if r == 1:
            w += 1
        elif r == 0:
            l += 1
        else:
            t += 1
    n = w + l
    if n == 0:
        return dict(n=0)
    lo, hi = wilson(w, n)
    return dict(n=n, wr=w / n, lo=lo, hi=hi, timeout=t,
                exp=(w * TP - l * SL) / n)


def row(name, r, floor=FLOOR):
    if not r.get('n'):
        return f"{name:<44} {'—':>6}  chua co ca"
    v = 'DAT' if (r['n'] >= 30 and r['lo'] > floor) else 'khong'
    return (f"{name:<44} n={r['n']:>5}  thang={100*r['wr']:5.1f}%  "
            f"CI95=[{100*r['lo']:4.1f}%,{100*r['hi']:5.1f}%]  "
            f"ky vong={r['exp']:+5.2f} gia  {v}")


def main():
    d = load()
    prof, sess = d['profiles'], d['sessions']
    rolls = set(d['rolls']) | set(EXTRA_ROLL)
    days = sorted(sess)

    # loai phien nhiem cho noi hop dong (+- ROLL_PAD phien)
    bad = set()
    for i, dd in enumerate(days):
        if dd in rolls:
            for j in range(max(0, i - ROLL_PAD), min(len(days), i + ROLL_PAD + 1)):
                bad.add(days[j])
    use = [x for x in days if x not in bad]

    print("=" * 100)
    print("DO LAI TREN DU LIEU DAY — /GC:XCEC 2024-08-01 -> 2026-08-19")
    print("=" * 100)
    print(f"phien co du lieu: {len(days)}   loai vi cho noi hop dong: {len(bad)}   "
          f"con dung duoc: {len(use)}")
    print(f"cho noi phat hien tu buoc nhay: {', '.join(d['rolls'])}")
    print(f"cho noi them thu cong (chenh qua nho de bat): {', '.join(EXTRA_ROLL)}")
    print(f"\nGiao thuc: SL {SL} gia / TP {TP} gia / toi da {HORIZON} nen M1, "
          f"fade lan cham dau tien. Nen hoa von {100*FLOOR:.0f}%.")

    idx = {dd: i for i, dd in enumerate(days)}

    def prev_ok(dd):
        """phien lien truoc, chi nhan khi ca hai deu sach cho noi."""
        i = idx[dd]
        if i == 0:
            return None
        p = days[i - 1]
        return None if (dd in bad or p in bad) else p

    # ---------- gom moc HVN ngay hom truoc, kem ti le -------------------
    hvn_cases = []          # (bars, level, ratio, band)
    for dd in use:
        p = prev_ok(dd)
        if p is None or p not in prof:
            continue
        rows_ = prof[p]
        if len(rows_) < 50:
            continue
        for lv, ratio in find_hvn(rows_)[:3]:
            lo, hi = peak_sharpness(rows_, lv)
            hvn_cases.append((sess[dd], lv, ratio, hi - lo))

    print(f"\n--- A. HVN phien truoc, chia theo TI LE (cong MinHvnRatio) ---")
    print(f"tong so moc thu: {len(hvn_cases)}")
    buckets = [('x1.5-2.0', 1.5, 2.0), ('x2.0-2.5', 2.0, 2.5),
               ('x2.5-3.0', 2.5, 3.0), ('x3.0+', 3.0, 99)]
    for nm, a, b in buckets:
        cs = [(bb, lv) for bb, lv, r, _ in hvn_cases if a <= r < b]
        print(row(f"  HVN {nm}", evaluate(cs)))
    print(row("  HVN tat ca (>=x1.5)", evaluate([(b_, lv) for b_, lv, _, _ in hvn_cases])))
    print(row("  HVN qua cong x2.0 (B8)", evaluate([(b_, lv) for b_, lv, r, _ in hvn_cases if r >= 2.0])))
    print(row("  HVN qua cong x2.5 (B9)", evaluate([(b_, lv) for b_, lv, r, _ in hvn_cases if r >= 2.5])))

    print(f"\n--- B. HVN chia theo BE RONG NEN (bướu nhọn có hơn bướu bẹt không?) ---")
    for nm, a, b in [('nen <=0.5 gia', 0, 0.51), ('nen 0.5-2 gia', 0.51, 2.01),
                     ('nen >2 gia', 2.01, 999)]:
        cs = [(bb, lv) for bb, lv, _, w in hvn_cases if a <= w < b]
        print(row(f"  HVN {nm}", evaluate(cs)))

    # ---------- doi chung ------------------------------------------------
    print(f"\n--- C. DOI CHUNG (phai vuot duoc may cai nay moi goi la co gia tri) ---")
    rnd_cases, close_cases, mid_cases = [], [], []
    for dd in use:
        p = prev_ok(dd)
        if p is None or p not in prof:
            continue
        rows_ = prof[p]
        if len(rows_) < 50:
            continue
        ps = sorted(rows_)
        lo_p, hi_p = ps[0], ps[-1]
        for _ in range(3):      # cung so luong voi HVN (toi da 3 moc/phien)
            rnd_cases.append((sess[dd], round(RNG.uniform(lo_p, hi_p), 1)))
        close_cases.append((sess[dd], sess[p][-1][4]))
        mid_cases.append((sess[dd], round((lo_p + hi_p) / 2, 1)))
    print(row("  muc NGAU NHIEN trong bien do phien truoc", evaluate(rnd_cases)))
    print(row("  gia dong cua phien truoc", evaluate(close_cases)))
    print(row("  trung diem bien do phien truoc", evaluate(mid_cases)))

    # ---------- kiem dinh hoan vi: HVN co hon ngau nhien khong? ----------
    print(f"\n--- D. HVN co thuc su hon MUC NGAU NHIEN khong? ---")
    h = evaluate([(b_, lv) for b_, lv, r, _ in hvn_cases if r >= 2.5])
    rr = evaluate(rnd_cases)
    if h.get('n') and rr.get('n'):
        diff = h['wr'] - rr['wr']
        se = math.sqrt(h['wr'] * (1 - h['wr']) / h['n'] + rr['wr'] * (1 - rr['wr']) / rr['n'])
        z = diff / se if se else 0
        print(f"  HVN(x2.5+) {100*h['wr']:.1f}%  vs  ngau nhien {100*rr['wr']:.1f}%  "
              f"=> lech {100*diff:+.1f} diem, z={z:+.2f}")
        print("  " + ("=> KHAC BIET CO Y NGHIA" if abs(z) >= 1.96 else
                      "=> KHONG khac biet (|z| < 1.96) — HVN ngang muc boc dai"))


if __name__ == '__main__':
    main()
