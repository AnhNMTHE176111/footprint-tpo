"""HAP THU TAI CAC VUNG CUA SessionZones + VWAP ngay/tuan.

Vung dung dung dinh nghia trong quantower-tpo-suite (khong tu bay ra):
  - HVN ngay / HVN tuan (5 phien) / HVN 3 tuan (15 phien) -> port find_hvn cua ProfileEngine,
    cong MinHvnRatio = 2.5, MaxHvn = 3
  - POC / VAH / VAL phien truoc -> port ValueArea(frac=0.70)
  - naked POC (POC cu chua bi gia cham lai)
  - LVN ngay (day rong cua profile phien truoc)
  - VWAP ngay (cong don trong phien) / VWAP tuan (neo dau tuan ISO)

Su kien:
  A  ban thao PHA CUC TRI : vol>=3x trung vi, |delta|>=4x trung vi, cuc tri moi 20 nen
  B  HAP THU dung nghia   : nhu tren nhung KHONG pha cuc tri, bien do <= trung vi, dong nua trong
  AB tat ca cum vol+delta : chi vol>=3x va |delta|>=4x (de co n lon khi chia theo vung)

Thuoc do: RAO CHAN DOI XUNG +-k*u tu gia dong nen su kien (u = trung vi bien do 50 nen truoc),
xem ben nao cham truoc trong 60 nen. Nen chuan = nen ngau nhien (moi nen thu 30) => phai ~50%.
"""
import os, sys, math, pickle, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "quantower-tpo-suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calib_hvn_dense import find_hvn
from kich_ban_hap_thu_load import load

BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
CACHE = os.environ["DENSE_CACHE"]
W, LOOK, HOR, FWD = 50, 20, 60, 30
GATE, MAXHVN = 2.5, 3
NAN = float("nan")


def value_area(rows, frac=0.70):
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    tot = sum(w)
    if tot <= 0:
        return NAN, NAN, NAN
    poc = max(range(len(w)), key=lambda i: w[i])
    acc = w[poc]
    target = tot * frac
    lo = hi = poc
    while acc < target and (lo > 0 or hi < len(w) - 1):
        up = (w[hi + 1] if hi < len(w) - 1 else 0) + (w[hi + 2] if hi < len(w) - 2 else 0)
        dn = (w[lo - 1] if lo > 0 else 0) + (w[lo - 2] if lo > 1 else 0)
        if hi >= len(w) - 1:
            acc += dn; lo = max(0, lo - 2)
        elif lo <= 0:
            acc += up; hi = min(len(w) - 1, hi + 2)
        elif up >= dn:
            acc += up; hi = min(len(w) - 1, hi + 2)
        else:
            acc += dn; lo = max(0, lo - 2)
    return prices[poc], prices[hi], prices[lo]


def find_lvn(rows, smooth=5, max_ratio=0.5, top=2):
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    n = len(w)
    if n < 20:
        return []
    avg = sum(w) / n
    if avg <= 0:
        return []
    sm = []
    for i in range(n):
        a, z = max(0, i - smooth), min(n - 1, i + smooth)
        sm.append(sum(w[a:z + 1]) / (z - a + 1))
    val = [(prices[i], sm[i] / avg) for i in range(1, n - 1)
           if sm[i] <= sm[i - 1] and sm[i] <= sm[i + 1] and sm[i] <= max_ratio * avg]
    val.sort(key=lambda x: x[1])
    out = []
    for p, r in val:
        if all(abs(p - q) >= 2.0 for q, _ in out):
            out.append((p, r))
        if len(out) >= top:
            break
    return out


def session_split(t, bar_dates):
    """chia phien theo gap > 30 phut, ten phien = ngay cua bar CUOI (giong dense_prep)"""
    bounds = []
    start = 0
    for i in range(1, len(t)):
        if t[i] - t[i - 1] > 30:
            bounds.append((start, i - 1))
            start = i
    bounds.append((start, len(t) - 1))
    sid = [0] * len(t)
    names = []
    for k, (a, b) in enumerate(bounds):
        names.append(bar_dates[b])
        for j in range(a, b + 1):
            sid[j] = k
    return sid, names, bounds


def zsc(p, p0, n):
    if n <= 0:
        return 0.0
    return (p - p0) / math.sqrt(p0 * (1 - p0) / n)


def barrier(i, u, k, h, l, c, side):
    """side=-1: ky vong gia LEN (ban bi hap thu o day). side=+1: ky vong gia XUONG."""
    up = c[i] + k * u
    dn = c[i] - k * u
    for j in range(i + 1, min(i + HOR, len(h) - 1)):
        a = h[j] >= up
        b = l[j] <= dn
        if a and b:
            return "cung nen"
        if a:
            return "thuan" if side < 0 else "nguoc"
        if b:
            return "nguoc" if side < 0 else "thuan"
    return "khong toi"


if __name__ == "__main__":
    d = pickle.load(open(CACHE, "rb"))
    prof = d["profiles"]
    rolls = set(d["rolls"])
    t, o, h, l, c, v, dl = load(BARS)
    bar_dates = []
    with open(BARS, encoding="utf-8-sig") as f:
        f.readline()
        for line in f:
            bar_dates.append(line.split(",")[1][:10])
    sid, snames, bounds = session_split(t, bar_dates)
    print("so nen %d, so phien %d, cho noi %d" % (len(t), len(snames), len(rolls)), flush=True)

    zones = {}
    for k in range(len(snames)):
        if k < 16:
            continue
        prev = snames[k - 1]
        if prev not in prof:
            continue
        if any(nm in rolls for nm in snames[max(0, k - 15):k + 1]):
            continue
        z = {}
        z["HVN ngay"] = [p for p, r in find_hvn(prof[prev])[:MAXHVN] if r >= GATE]
        agg5 = defaultdict(float)
        for nm in snames[max(0, k - 5):k]:
            for p, x in prof.get(nm, {}).items():
                agg5[p] += x
        z["HVN tuan"] = [p for p, r in find_hvn(agg5)[:MAXHVN] if r >= GATE]
        agg15 = defaultdict(float)
        for nm in snames[max(0, k - 15):k]:
            for p, x in prof.get(nm, {}).items():
                agg15[p] += x
        z["HVN 3 tuan"] = [p for p, r in find_hvn(agg15)[:MAXHVN] if r >= GATE]
        poc, vah, val = value_area(prof[prev])
        z["POC phien truoc"] = [poc]
        z["bien VA (VAH/VAL)"] = [vah, val]
        z["LVN ngay"] = [p for p, _ in find_lvn(prof[prev])]
        zones[k] = z
    print("da dung vung cho %d phien" % len(zones), flush=True)

    poc_of = {}
    for k in range(len(snames)):
        nm = snames[k]
        if nm in prof and nm not in rolls:
            poc_of[k] = value_area(prof[nm])[0]
    touched_at = {}
    for k, p in poc_of.items():
        end = bounds[k][1]
        touched_at[k] = 10 ** 9
        for j in range(end + 1, min(end + 1 + 20000, len(t))):
            if l[j] <= p <= h[j]:
                touched_at[k] = j
                break

    def naked_pocs(i, k):
        out = []
        for kk in range(max(0, k - 30), k):
            if kk in poc_of and touched_at.get(kk, 0) > i:
                out.append(poc_of[kk])
        return out[-3:]

    vwd = [0.0] * len(t)
    vww = [0.0] * len(t)
    pv = pvol = 0.0
    cur = -1
    for i in range(len(t)):
        if sid[i] != cur:
            cur = sid[i]; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]
        vwd[i] = pv / pvol if pvol > 0 else c[i]
    import datetime as dtm
    wk = []
    for i in range(len(t)):
        s = bar_dates[i]
        wk.append(dtm.date(int(s[:4]), int(s[5:7]), int(s[8:10])).isocalendar()[:2])
    pv = pvol = 0.0
    curw = None
    for i in range(len(t)):
        if wk[i] != curw:
            curw = wk[i]; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]
        vww[i] = pv / pvol if pvol > 0 else c[i]

    ZTYPES = ["HVN ngay", "HVN tuan", "HVN 3 tuan", "POC phien truoc", "bien VA (VAH/VAL)",
              "LVN ngay", "naked POC", "VWAP ngay", "VWAP tuan"]
    TOLS = (1.0, 2.0)
    res = defaultdict(lambda: defaultdict(int))
    base = defaultdict(int)
    last = defaultdict(lambda: -10 ** 9)
    for i in range(W + LOOK, len(t) - HOR - 4):
        seg = t[i - W:i + HOR + 4]
        if seg[-1] - seg[0] != len(seg) - 1:
            continue
        mv = st.median(v[i - W:i])
        md = st.median([abs(x) for x in dl[i - W:i]])
        u = st.median([h[j] - l[j] for j in range(i - W, i)])
        if mv <= 0 or md <= 0 or u <= 0:
            continue
        if i % 30 == 0:
            for kk in TOLS:
                base[(kk, barrier(i, u, kk, h, l, c, -1))] += 1
        k = sid[i]
        if k not in zones or snames[k] in rolls:
            continue
        R = h[i] - l[i]
        if v[i] < 3.0 * mv or R <= 0:
            continue
        for side in (-1, +1):
            big_d = (dl[i] <= -4.0 * md) if side < 0 else (dl[i] >= 4.0 * md)
            if not big_d:
                continue
            newext = (l[i] <= min(l[i - LOOK:i])) if side < 0 else (h[i] >= max(h[i - LOOK:i]))
            inner = (c[i] >= l[i] + 0.5 * R) if side < 0 else (c[i] <= h[i] - 0.5 * R)
            ref = l[i] if side < 0 else h[i]
            fams = ["AB"]
            if newext:
                fams.append("A")
            if (not newext) and R <= u and inner:
                fams.append("B")
            zl = dict(zones[k])
            zl["naked POC"] = naked_pocs(i, k)
            zl["VWAP ngay"] = [vwd[i]]
            zl["VWAP tuan"] = [vww[i]]
            for fam in fams:
                key = (fam, side)
                if i - last[key] < FWD:
                    continue
                last[key] = i
                for kk in TOLS:
                    oc = barrier(i, u, kk, h, l, c, side)
                    anyhit = False
                    for zt in ZTYPES:
                        lv = [x for x in zl.get(zt, []) if x == x]
                        hit = any(abs(ref - x) <= kk for x in lv)
                        if hit:
                            anyhit = True
                        res[(fam, zt, kk, hit)][oc] += 1
                    res[(fam, "BAT KY VUNG", kk, anyhit)][oc] += 1

    for kk in TOLS:
        dec0 = base[(kk, "thuan")] + base[(kk, "nguoc")]
        p0 = base[(kk, "thuan")] / dec0
        print("\n########## ban kinh vung +-%.1f gia | rao chan +-%.1fx trung vi bien do ##########" % (kk, kk))
        print("  nen chuan (ngau nhien): thuan %.1f%%  n=%d" % (100 * p0, dec0))
        for fam in ("AB", "A", "B"):
            print("  --- ho %s ---" % fam)
            for zt in ZTYPES + ["BAT KY VUNG"]:
                for hit in (True, False):
                    a = res[(fam, zt, kk, hit)]
                    tot = sum(a.values())
                    dec = a["thuan"] + a["nguoc"]
                    if dec < 40:
                        continue
                    p = a["thuan"] / dec
                    tag = "TAI VUNG " if hit else "khong vung"
                    print("    %-20s %s n=%6d thuan %5.1f%%  z=%+5.2f" % (zt, tag, tot, 100 * p, zsc(p, p0, dec)))
