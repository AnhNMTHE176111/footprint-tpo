"""PHA -> HOI VE MOC -> DI TIEP: co that o HVN / VWAP khong?

Chi xet ho A (cum khoi luong lon + delta cuc doan PHA CUC TRI 20 nen), tai tung nhom vung.
Phan loai 60 nen ke tiep, u = trung vi bien do 50 nen:
  DAO CHIEU     : cham c +- 2u NGUOC huong pha truoc
  HOI ROI TIEP  : hoi ve trong +-1 gia quanh MOC roi moi cham 2u theo huong pha
  DI LUON       : cham 2u theo huong pha ma KHONG hoi ve moc
  KHONG TOI     : khong ben nao trong 60 nen
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
TOL = 2.0          # ban kinh coi la "tai vung"
RETOL = 1.0        # ban kinh coi la "hoi ve moc"


def value_area(rows, frac=0.70):
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    tot = sum(w)
    if tot <= 0:
        return NAN, NAN, NAN
    poc = max(range(len(w)), key=lambda i: w[i])
    acc = w[poc]; target = tot * frac; lo = hi = poc
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


def session_split(t, bar_dates):
    bounds = []; start = 0
    for i in range(1, len(t)):
        if t[i] - t[i - 1] > 30:
            bounds.append((start, i - 1)); start = i
    bounds.append((start, len(t) - 1))
    sid = [0] * len(t); names = []
    for k, (a, b) in enumerate(bounds):
        names.append(bar_dates[b])
        for j in range(a, b + 1):
            sid[j] = k
    return sid, names, bounds


def classify(i, u, lvl, side, h, l, c):
    """side=-1: pha DAY => huong pha la XUONG. lvl = moc vung (None neu khong vung)."""
    cont = c[i] - 2 * u if side < 0 else c[i] + 2 * u
    rev = c[i] + 2 * u if side < 0 else c[i] - 2 * u
    seen_retest = False
    for j in range(i + 1, min(i + HOR, len(h) - 1)):
        hit_rev = (h[j] >= rev) if side < 0 else (l[j] <= rev)
        hit_cont = (l[j] <= cont) if side < 0 else (h[j] >= cont)
        if hit_rev and hit_cont:
            return "cung nen"
        if hit_rev:
            return "DAO CHIEU"
        if hit_cont:
            return "HOI ROI TIEP" if seen_retest else "DI LUON"
        if lvl is not None and (l[j] - RETOL) <= lvl <= (h[j] + RETOL):
            seen_retest = True
    return "KHONG TOI"


if __name__ == "__main__":
    d = pickle.load(open(CACHE, "rb"))
    prof = d["profiles"]; rolls = set(d["rolls"])
    t, o, h, l, c, v, dl = load(BARS)
    bar_dates = []
    with open(BARS, encoding="utf-8-sig") as f:
        f.readline()
        for line in f:
            bar_dates.append(line.split(",")[1][:10])
    sid, snames, bounds = session_split(t, bar_dates)

    zones = {}
    for k in range(len(snames)):
        if k < 16:
            continue
        prev = snames[k - 1]
        if prev not in prof or any(nm in rolls for nm in snames[max(0, k - 15):k + 1]):
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
        zones[k] = z
    print("vung dung cho %d phien" % len(zones), flush=True)

    vwd = [0.0] * len(t); vww = [0.0] * len(t)
    pv = pvol = 0.0; cur = -1
    for i in range(len(t)):
        if sid[i] != cur:
            cur = sid[i]; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]; vwd[i] = pv / pvol if pvol > 0 else c[i]
    import datetime as dtm
    pv = pvol = 0.0; curw = None
    for i in range(len(t)):
        s = bar_dates[i]
        wkk = dtm.date(int(s[:4]), int(s[5:7]), int(s[8:10])).isocalendar()[:2]
        if wkk != curw:
            curw = wkk; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]; vww[i] = pv / pvol if pvol > 0 else c[i]

    GROUPS = ["HVN bat ky", "HVN ngay", "HVN tuan", "HVN 3 tuan", "VWAP ngay", "VWAP tuan", "KHONG vung"]
    res = defaultdict(lambda: defaultdict(int))
    last = {-1: -10 ** 9, 1: -10 ** 9}
    for i in range(W + LOOK, len(t) - HOR - 4):
        seg = t[i - W:i + HOR + 4]
        if seg[-1] - seg[0] != len(seg) - 1:
            continue
        k = sid[i]
        if k not in zones or snames[k] in rolls:
            continue
        mv = st.median(v[i - W:i]); md = st.median([abs(x) for x in dl[i - W:i]])
        u = st.median([h[j] - l[j] for j in range(i - W, i)])
        if mv <= 0 or md <= 0 or u <= 0 or v[i] < 3.0 * mv:
            continue
        for side in (-1, 1):
            big_d = (dl[i] <= -4.0 * md) if side < 0 else (dl[i] >= 4.0 * md)
            if not big_d:
                continue
            newext = (l[i] <= min(l[i - LOOK:i])) if side < 0 else (h[i] >= max(h[i - LOOK:i]))
            if not newext:
                continue
            if i - last[side] < FWD:
                continue
            last[side] = i
            ref = l[i] if side < 0 else h[i]
            zl = dict(zones[k])
            zl["VWAP ngay"] = [vwd[i]]
            zl["VWAP tuan"] = [vww[i]]
            hits = {}
            for zt, lv in zl.items():
                cand = [x for x in lv if x == x and abs(ref - x) <= TOL]
                if cand:
                    hits[zt] = min(cand, key=lambda x: abs(ref - x))
            hvn_any = None
            for zt in ("HVN ngay", "HVN tuan", "HVN 3 tuan"):
                if zt in hits:
                    hvn_any = hits[zt]; break
            if hvn_any is not None:
                res["HVN bat ky"][classify(i, u, hvn_any, side, h, l, c)] += 1
            for zt in ("HVN ngay", "HVN tuan", "HVN 3 tuan", "VWAP ngay", "VWAP tuan"):
                if zt in hits:
                    res[zt][classify(i, u, hits[zt], side, h, l, c)] += 1
            if not hits:
                res["KHONG vung"][classify(i, u, ref, side, h, l, c)] += 1

    print("\n=== ho A (pha cuc tri) — hinh dang 60 nen sau, theo nhom vung ===")
    print("    (moc hoi ve = chinh moc vung; voi 'KHONG vung' lay day/dinh nen su kien)")
    for g in GROUPS:
        a = res[g]; tot = sum(a.values())
        if tot < 40:
            print("  %-12s n=%d (qua it)" % (g, tot)); continue
        f = lambda kk: 100.0 * a[kk] / tot
        cont = a["DI LUON"] + a["HOI ROI TIEP"]
        print("  %-12s n=%5d | DAO CHIEU %5.1f%% | DI LUON %5.1f%% | HOI ROI TIEP %5.1f%% "
              "| KHONG TOI %5.1f%% || tong di tiep %5.1f%%  (trong do co hoi ve moc: %4.1f%%)"
              % (g, tot, f("DAO CHIEU"), f("DI LUON"), f("HOI ROI TIEP"), f("KHONG TOI"),
                 100.0 * cont / tot, 100.0 * a["HOI ROI TIEP"] / max(1, cont)))
