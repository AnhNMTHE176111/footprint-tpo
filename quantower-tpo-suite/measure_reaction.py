#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measure_reaction.py — do PHAN UNG cua gia tai moc, thay vi thang/thua mot lenh.

Vi sao doi cach do: phep thang/thua (SL 3 / TP 4.5, vao ngay lan cham dau, khong
cho xac nhan) la mot CHIEN LUOC cu the ma nguoi hoc khong he danh nhu vay — ho
doi "hop luu >= 2 + retest giu vung". Phep do do nhi phan nen rat kem nhay: n=116
moi phan biet duoc 45% voi 38%.

Phep do o day lien tuc va nhay hon nhieu:
  - DAM XUYEN: gia di qua moc bao nhieu gia trong 30 nen sau khi cham
  - BAT LAI:   gia quay nguoc lai bao nhieu gia trong 30 nen do
Moc "co that" thi phai DAM XUYEN NONG va BAT LAI XA hon muc boc ngau nhien
trong cung bien do, cung phien. So sanh bat cap: moi ca HVN duoc ghep voi
mot muc ngau nhien trong CUNG PHIEN.
"""
import os, random, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dense_prep import load
from calib_hvn_dense import find_hvn
from measure_dense import EXTRA_ROLL, ROLL_PAD

LOOK = 30          # so nen M1 quan sat sau khi cham
RNG = random.Random(3)


def touch_and_react(bars, level):
    """Tra (dam_xuyen, bat_lai, huong) tai lan cham dau tien, hoac None."""
    for k in range(1, len(bars) - LOOK):
        if bars[k][3] <= level <= bars[k][2]:
            side = 1 if bars[k - 1][4] > level else -1   # +1: toi tu TREN
            seg = bars[k:k + LOOK]
            hi = max(b[2] for b in seg)
            lo = min(b[3] for b in seg)
            if side > 0:
                return (level - lo, hi - level, side)     # xuyen xuong / bat len
            return (hi - level, level - lo, side)         # xuyen len / bat xuong
    return None


def summarize(name, recs):
    if not recs:
        print(f"  {name:<34} chua co ca"); return None
    pen = [r[0] for r in recs]
    bo = [r[1] for r in recs]
    ratio = [b / p if p > 0.05 else 99 for p, b in zip(pen, bo)]
    print(f"  {name:<34} n={len(recs):>4}  "
          f"dam xuyen tv={st.median(pen):5.2f}  bat lai tv={st.median(bo):5.2f}  "
          f"bat/xuyen tv={st.median(ratio):5.2f}")
    return dict(n=len(recs), pen=st.median(pen), bo=st.median(bo),
                ratio=st.median(ratio), pen_m=st.mean(pen), bo_m=st.mean(bo))


def main():
    d = load()
    prof, sess = d['profiles'], d['sessions']
    rolls = set(d['rolls']) | set(EXTRA_ROLL)
    days = sorted(sess); idx = {x: i for i, x in enumerate(days)}
    bad = set()
    for i, dd in enumerate(days):
        if dd in rolls:
            for j in range(max(0, i-ROLL_PAD), min(len(days), i+ROLL_PAD+1)):
                bad.add(days[j])

    hv = {1.5: [], 2.5: [], 3.0: [], 3.5: []}
    allhv, rnd = [], []
    paired = []          # (hvn, ngau nhien) cung phien — de so sanh bat cap
    for dd in days:
        i = idx[dd]
        if i < 1 or dd in bad: continue
        p = days[i-1]
        if p in bad or p not in prof or len(prof[p]) < 50: continue
        ps = sorted(prof[p]); lo_p, hi_p = ps[0], ps[-1]
        bars = sess[dd]
        if len(bars) < LOOK + 10: continue
        for lv, r in find_hvn(prof[p])[:3]:
            t = touch_and_react(bars, lv)
            if t is None: continue
            allhv.append(t)
            for g in hv:
                if r >= g: hv[g].append(t)
            # ghep cap: 1 muc ngau nhien cung phien
            for _ in range(6):
                rl = round(RNG.uniform(lo_p, hi_p), 1)
                tr = touch_and_react(bars, rl)
                if tr is not None:
                    rnd.append(tr)
                    paired.append((t, tr))
                    break

    print("="*96)
    print(f"PHAN UNG TAI MOC — do trong {LOOK} nen M1 sau lan cham dau tien (don vi: gia)")
    print("="*96)
    print("  'dam xuyen' cang NHO cang tot (moc chan duoc gia) — 'bat lai' cang LON cang tot\n")
    base = summarize("MUC NGAU NHIEN (cung phien)", rnd)
    for g in sorted(hv):
        summarize(f"HVN ngay >= x{g}", hv[g])

    # so sanh bat cap: dau hieu co y nghia hay khong
    print(f"\n--- so sanh BAT CAP (cung phien, cung so ca) ---")
    if paired:
        dpen = [a[0] - b[0] for a, b in paired]
        dbo = [a[1] - b[1] for a, b in paired]
        n = len(paired)
        for nm, arr in [('dam xuyen (HVN - ngau nhien)', dpen),
                        ('bat lai   (HVN - ngau nhien)', dbo)]:
            m, s = st.mean(arr), st.pstdev(arr)
            z = m / (s / (n ** 0.5)) if s else 0
            good = ('HVN chan tot hon' if (m < 0 and 'dam' in nm) or (m > 0 and 'bat' in nm)
                    else 'HVN KHONG hon')
            print(f"  {nm}: trung binh {m:+.3f} gia   z={z:+.2f}   "
                  + ("=> khac biet co y nghia, " if abs(z) >= 1.96 else "=> khong co y nghia, ")
                  + good)


if __name__ == '__main__':
    main()
