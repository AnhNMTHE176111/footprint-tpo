"""Cum hap thu co XAY RA nhieu hon o gan VWAP khong? (tan suat, khong phai ty le thanh cong)

So sanh: ty le nen SU KIEN nam trong +-tol quanh VWAP  vs  ty le nen NGAU NHIEN nam trong +-tol.
Neu bang nhau => VWAP khong "hut" su kien, chi la noi gia hay lui toi.
"""
import os, sys, math, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W, LOOK = 50, 20


def zsc(p, p0, n):
    if n <= 0 or p0 <= 0 or p0 >= 1:
        return 0.0
    return (p - p0) / math.sqrt(p0 * (1 - p0) / n)


if __name__ == "__main__":
    t, o, h, l, c, v, dl = load(BARS)
    bar_dates = []
    with open(BARS, encoding="utf-8-sig") as f:
        f.readline()
        for line in f:
            bar_dates.append(line.split(",")[1][:10])
    n = len(t)

    # phien = gap > 30 phut ; tuan = tuan ISO
    import datetime as dtm
    sid = [0] * n
    k = 0
    for i in range(1, n):
        if t[i] - t[i - 1] > 30:
            k += 1
        sid[i] = k
    wk = []
    for i in range(n):
        s = bar_dates[i]
        wk.append(dtm.date(int(s[:4]), int(s[5:7]), int(s[8:10])).isocalendar()[:2])

    vwd = [0.0] * n
    vww = [0.0] * n
    pv = pvol = 0.0
    cur = -1
    for i in range(n):
        if sid[i] != cur:
            cur = sid[i]; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]
        vwd[i] = pv / pvol if pvol > 0 else c[i]
    pv = pvol = 0.0
    curw = None
    for i in range(n):
        if wk[i] != curw:
            curw = wk[i]; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]
        vww[i] = pv / pvol if pvol > 0 else c[i]

    TOLS = (1.0, 2.0, 4.0)
    cnt = {("rand", z, tol): 0 for z in ("ngay", "tuan") for tol in TOLS}
    tot = {"rand": 0, "AB": 0, "A": 0, "B": 0}
    for kk in ("AB", "A", "B"):
        for z in ("ngay", "tuan"):
            for tol in TOLS:
                cnt[(kk, z, tol)] = 0
    last = {"AB": -10 ** 9, "A": -10 ** 9, "B": -10 ** 9}

    for i in range(W + LOOK, n - 4):
        seg = t[i - W:i + 4]
        if seg[-1] - seg[0] != len(seg) - 1:
            continue
        mv = st.median(v[i - W:i])
        md = st.median([abs(x) for x in dl[i - W:i]])
        u = st.median([h[j] - l[j] for j in range(i - W, i)])
        if mv <= 0 or md <= 0 or u <= 0:
            continue
        R = h[i] - l[i]
        if R <= 0:
            continue

        def tally(tag, ref):
            tot[tag] += 1
            for z, arr in (("ngay", vwd), ("tuan", vww)):
                for tol in TOLS:
                    if abs(ref - arr[i]) <= tol:
                        cnt[(tag, z, tol)] += 1

        if i % 30 == 0:
            tally("rand", c[i])
        if v[i] < 3.0 * mv:
            continue
        for side in (-1, +1):
            big_d = (dl[i] <= -4.0 * md) if side < 0 else (dl[i] >= 4.0 * md)
            if not big_d:
                continue
            newext = (l[i] <= min(l[i - LOOK:i])) if side < 0 else (h[i] >= max(h[i - LOOK:i]))
            inner = (c[i] >= l[i] + 0.5 * R) if side < 0 else (c[i] <= h[i] - 0.5 * R)
            ref = l[i] if side < 0 else h[i]
            fams = ["AB"] + (["A"] if newext else []) + (["B"] if (not newext) and R <= u and inner else [])
            for fam in fams:
                if i - last[fam] < 30:
                    continue
                last[fam] = i
                tally(fam, ref)

    print("TAN SUAT nam trong +-tol quanh VWAP (khong phai ty le thanh cong)\n")
    for z in ("ngay", "tuan"):
        print("  --- VWAP %s ---" % z)
        for tol in TOLS:
            p0 = cnt[("rand", z, tol)] / tot["rand"]
            print("    +-%.1f gia | nen ngau nhien %5.1f%%  (n=%d)" % (tol, 100 * p0, tot["rand"]))
            for fam in ("AB", "A", "B"):
                p = cnt[(fam, z, tol)] / tot[fam]
                print("               | ho %-2s %13.1f%%  (n=%5d)  z=%+5.2f"
                      % (fam, 100 * p, tot[fam], zsc(p, p0, tot[fam])))
