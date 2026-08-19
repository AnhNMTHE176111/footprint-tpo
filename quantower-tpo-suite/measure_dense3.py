#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measure_dense3.py — KIEM DINH cai duy nhat co ve co that o buoc 2:
"HVN NGAY co ti le >= x3.0 (nhat la >= x3.5) thang cao hon han moc yeu va hon muc ngau nhien".

Ba phep kiem, lam theo dung thu tu, va DUNG LAI neu phep truoc khong qua:
  P1. NEN NGAU NHIEN ON DINH — chay 200 lan boc muc ngau nhien de biet nen that
      su nam o dau va dao dong bao nhieu. (O buoc 2 chi doi hat giong ma nen nhay
      33.8% -> 37.5%, tuc nen mot lan boc la KHONG dang tin.)
  P2. TACH DOI THOI GIAN — nua dau (2024-08..2025-08) va nua sau (2025-08..2026-08).
      Luat that thi phai co o CA HAI nua. Chi co o mot nua = khop qua muc.
  P3. HOAN VI — gan moc HVN cua phien nay cho phien khac 500 lan. Neu ket qua that
      khong nam ngoai phan bo hoan vi thi "loi the" chi la ngau nhien.
"""
import math, os, random, sys, statistics as st
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dense_prep import load
from calib_hvn_dense import find_hvn
from measure_dense import (SL, TP, HORIZON, wilson, first_touch, try_level,
                           evaluate, row, EXTRA_ROLL, ROLL_PAD)


def collect(d):
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
    cases = []       # (ngay, bars, level, ratio)
    ranges = {}      # ngay -> (lo, hi) bien do phien truoc
    for dd in use:
        i = idx[dd]
        if i < 1: continue
        p = days[i-1]
        if p in bad or p not in prof or len(prof[p]) < 50: continue
        ps = sorted(prof[p])
        ranges[dd] = (ps[0], ps[-1])
        for lv, r in find_hvn(prof[p])[:3]:
            cases.append((dd, sess[dd], lv, r))
    return cases, ranges, sess


def wr_of(cases):
    w = l = 0
    for _, bars, lv, _ in cases:
        if len(bars) < HORIZON + 5: continue
        t = first_touch(bars, lv)
        if t is None: continue
        r = try_level(bars, t[0], t[1])
        if r == 1: w += 1
        elif r == 0: l += 1
    n = w + l
    return (w/n if n else None), n


def main():
    d = load()
    cases, ranges, sess = collect(d)
    strong = [c for c in cases if c[3] >= 3.0]
    vstrong = [c for c in cases if c[3] >= 3.5]
    print("="*100)
    print("KIEM DINH — HVN NGAY manh co that su hon ngau nhien khong?")
    print("="*100)

    # ---------------- P1: nen ngau nhien on dinh ----------------------
    print("\n--- P1. Nen ngau nhien chay 200 lan (moi lan boc lai muc) ---")
    wrs = []
    for seed in range(200):
        rng = random.Random(seed)
        rc = []
        for dd, bars, _, _ in strong:            # cung so ca, cung phien
            lo, hi = ranges[dd]
            rc.append((dd, bars, round(rng.uniform(lo, hi), 1), 0))
        w, n = wr_of(rc)
        if w is not None: wrs.append(w)
    m, s = st.mean(wrs), st.pstdev(wrs)
    print(f"  nen ngau nhien: trung binh {100*m:.1f}%  do lech chuan {100*s:.1f} diem")
    print(f"  khoang 95% cua nen: [{100*(m-1.96*s):.1f}%, {100*(m+1.96*s):.1f}%]")
    for nm, cs in [('HVN >= x3.0', strong), ('HVN >= x3.5', vstrong)]:
        w, n = wr_of(cs)
        z = (w - m) / s if s else 0
        print(f"  {nm}: n={n}  thang {100*w:.1f}%   lech nen {100*(w-m):+.1f} diem  z={z:+.2f}"
              + ("   <== NGOAI khoang nen" if abs(z) >= 1.96 else "   (trong khoang nen)"))

    # ---------------- P2: tach doi thoi gian --------------------------
    print("\n--- P2. Tach doi thoi gian (luat that phai co o CA HAI nua) ---")
    alld = sorted({c[0] for c in cases})
    mid = alld[len(alld)//2]
    print(f"  moc chia: {mid}")
    for nm, cs in [('HVN >= x3.0', strong), ('HVN >= x3.5', vstrong)]:
        for half, sel in [('nua DAU', [c for c in cs if c[0] < mid]),
                          ('nua SAU', [c for c in cs if c[0] >= mid])]:
            w, n = wr_of(sel)
            # nen ngau nhien cung nua
            rw = []
            for seed in range(50):
                rng = random.Random(1000+seed)
                rc = [(dd, bars, round(rng.uniform(*ranges[dd]), 1), 0)
                      for dd, bars, _, _ in sel]
                x, _ = wr_of(rc)
                if x is not None: rw.append(x)
            rm = st.mean(rw) if rw else float('nan')
            print(f"  {nm:<12} {half}: n={n:>4}  thang {100*w:5.1f}%   "
                  f"(nen ngau nhien cung ky {100*rm:.1f}%)  lech {100*(w-rm):+5.1f} diem")

    # ---------------- P3: hoan vi -------------------------------------
    print("\n--- P3. Hoan vi 500 lan (gan moc cua phien A cho phien B) ---")
    for nm, cs in [('HVN >= x3.0', strong), ('HVN >= x3.5', vstrong)]:
        real, n = wr_of(cs)
        lvls = [c[2] for c in cs]
        barsl = [(c[0], c[1]) for c in cs]
        perm = []
        for seed in range(500):
            rng = random.Random(seed)
            sh = lvls[:]
            rng.shuffle(sh)
            # chi giu muc roi vao bien do phien truoc cua phien duoc gan, cho cong bang
            pc = [(dd, bars, lv, 0) for (dd, bars), lv in zip(barsl, sh)]
            x, _ = wr_of(pc)
            if x is not None: perm.append(x)
        pm, ps = st.mean(perm), st.pstdev(perm)
        pval = sum(1 for x in perm if x >= real) / len(perm)
        print(f"  {nm}: that {100*real:.1f}%   hoan vi {100*pm:.1f}% ± {100*ps:.1f}   "
              f"p={pval:.3f}" + ("   <== VUOT" if pval <= 0.05 else "   (khong vuot)"))


if __name__ == '__main__':
    main()
