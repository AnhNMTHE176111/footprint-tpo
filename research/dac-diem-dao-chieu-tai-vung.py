"""DAC DIEM CHUNG cua cac ca DAO CHIEU — CHI XET SU KIEN XAY RA TAI VUNG.

Vung = HVN ngay / HVN tuan / HVN 3 tuan / POC phien truoc / bien VA / LVN / naked POC /
       VWAP ngay / VWAP tuan  (ban kinh +-2 gia), dung dinh nghia port tu ProfileEngine.

Nhan: DAO CHIEU = gia cham 2u NGUOC huong chu dong truoc khi cham 2u thuan huong.
QUAN TRONG: neo do tai gia dong NEN SAU va bat dau tu nen i+2 => nen xac nhan KHONG nam trong
duong do (neu neo tai nen su kien thi nen xac nhan tu dong "du bao" chinh no => vong lap).

Chia doi thoi gian: nua dau tim luat, nua sau kiem tra.
"""
import os, sys, math, csv, pickle, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "quantower-tpo-suite"))
from calib_hvn_dense import find_hvn

BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
CACHE = os.environ["DENSE_CACHE"]
W, LOOK, HOR, FWD = 50, 20, 60, 30
TICK, GATE, MAXHVN, TOL = 0.1, 2.5, 3, 2.0
NAN = float("nan")


def days_from_civil(y, m, d):
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def load_full(path):
    cols = ("open", "high", "low", "close", "volume", "delta", "cum_delta", "trades",
            "avg_size", "levels", "poc_price", "poc_volume")
    out = {k: [] for k in cols}
    t, ds = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        hd = next(r)
        ix = {k: i for i, k in enumerate(hd)}
        for row in r:
            s = row[ix["datetime"]]
            t.append(days_from_civil(int(s[0:4]), int(s[5:7]), int(s[8:10])) * 1440
                     + int(s[11:13]) * 60 + int(s[14:16]))
            ds.append(s[:10])
            for k in cols:
                out[k].append(float(row[ix[k]]))
    return t, ds, out


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
        if all(abs(p - qq) >= 2.0 for qq, _ in out):
            out.append((p, r))
        if len(out) >= top:
            break
    return out


def q(vals, p):
    s = sorted(vals)
    k = (len(s) - 1) * p
    f = int(k)
    return s[f] if f + 1 >= len(s) else s[f] + (s[f + 1] - s[f]) * (k - f)


if __name__ == "__main__":
    d = pickle.load(open(CACHE, "rb"))
    prof = d["profiles"]; rolls = set(d["rolls"])
    t, ds, D = load_full(BARS)
    o, h, l, c = D["open"], D["high"], D["low"], D["close"]
    v, dl, cd = D["volume"], D["delta"], D["cum_delta"]
    avgsz, levels, pocp, pocv = D["avg_size"], D["levels"], D["poc_price"], D["poc_volume"]
    n = len(t)

    bounds = []; start = 0
    for i in range(1, n):
        if t[i] - t[i - 1] > 30:
            bounds.append((start, i - 1)); start = i
    bounds.append((start, n - 1))
    sid = [0] * n; snames = []
    for k, (a, b) in enumerate(bounds):
        snames.append(ds[b])
        for j in range(a, b + 1):
            sid[j] = k

    zones = {}
    for k in range(len(snames)):
        if k < 16:
            continue
        prev = snames[k - 1]
        if prev not in prof or any(nm in rolls for nm in snames[max(0, k - 15):k + 1]):
            continue
        z = {}
        z["HVN ngay"] = [p for p, r in find_hvn(prof[prev])[:MAXHVN] if r >= GATE]
        for tag, back in (("HVN tuan", 5), ("HVN 3 tuan", 15)):
            agg = defaultdict(float)
            for nm in snames[max(0, k - back):k]:
                for p, x in prof.get(nm, {}).items():
                    agg[p] += x
            z[tag] = [p for p, r in find_hvn(agg)[:MAXHVN] if r >= GATE]
        poc, vah, val = value_area(prof[prev])
        z["POC phien truoc"] = [poc]
        z["bien VA"] = [vah, val]
        z["LVN ngay"] = [p for p, _ in find_lvn(prof[prev])]
        zones[k] = z
    print("vung dung cho %d phien" % len(zones), flush=True)

    poc_of = {}
    for k in range(len(snames)):
        if snames[k] in prof and snames[k] not in rolls:
            poc_of[k] = value_area(prof[snames[k]])[0]
    touched = {}
    for k, p in poc_of.items():
        end = bounds[k][1]
        touched[k] = 10 ** 9
        for j in range(end + 1, min(end + 20001, n)):
            if l[j] <= p <= h[j]:
                touched[k] = j
                break

    vwd = [0.0] * n; vww = [0.0] * n; slo = [0.0] * n; shi = [0.0] * n
    pv = pvol = 0.0; lo = 1e18; hi2 = -1e18; cur = -1
    for i in range(n):
        if sid[i] != cur:
            cur = sid[i]; pv = pvol = 0.0; lo = 1e18; hi2 = -1e18
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]; vwd[i] = pv / pvol if pvol > 0 else c[i]
        lo = min(lo, l[i]); hi2 = max(hi2, h[i]); slo[i] = lo; shi[i] = hi2
    import datetime as dtm
    pv = pvol = 0.0; curw = None
    for i in range(n):
        s = ds[i]
        wk = dtm.date(int(s[:4]), int(s[5:7]), int(s[8:10])).isocalendar()[:2]
        if wk != curw:
            curw = wk; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]; vww[i] = pv / pvol if pvol > 0 else c[i]

    def label(i, u, side):
        a0 = i + 1
        up = c[a0] + 2 * u
        dn = c[a0] - 2 * u
        for j in range(a0 + 1, min(i + HOR, n - 1)):
            a = h[j] >= up
            b = l[j] <= dn
            if a and b:
                return None
            if a:
                return 1 if side < 0 else 0
            if b:
                return 0 if side < 0 else 1
        return None

    FEATS = ["dong nguoc phia (%)", "|delta|/khoi luong", "khoi luong /nen", "no luc/ket qua",
             "POC hut (%vol)", "POC sat cuc tri", "co lenh (avg_size)", "so muc gia /bien do",
             "sat tam vung (gia)", "chan truoc do dai", "da chu dong 5 nen", "nen sau xac nhan",
             "cuc tri phien", "delta phan ky", "so lan cham vung"]
    rows_all = []
    per_zone = defaultdict(lambda: [0, 0])
    last = {-1: -10 ** 9, 1: -10 ** 9}
    half = n // 2
    for i in range(W + LOOK, n - HOR - 4):
        seg = t[i - W:i + HOR + 4]
        if seg[-1] - seg[0] != len(seg) - 1:
            continue
        k = sid[i]
        if k not in zones or snames[k] in rolls:
            continue
        mv = st.median(v[i - W:i]); md = st.median([abs(x) for x in dl[i - W:i]])
        u = st.median([h[j] - l[j] for j in range(i - W, i)]); ma = st.median(avgsz[i - W:i])
        if mv <= 0 or md <= 0 or u <= 0 or ma <= 0:
            continue
        R = h[i] - l[i]
        if R <= 0 or v[i] < 2.5 * mv:
            continue
        for side in (-1, 1):
            if side < 0 and dl[i] > -3.0 * md:
                continue
            if side > 0 and dl[i] < 3.0 * md:
                continue
            if i - last[side] < FWD:
                continue
            ref = l[i] if side < 0 else h[i]
            zl = dict(zones[k])
            zl["VWAP ngay"] = [vwd[i]]
            zl["VWAP tuan"] = [vww[i]]
            zl["naked POC"] = [poc_of[kk] for kk in range(max(0, k - 30), k)
                               if kk in poc_of and touched.get(kk, 0) > i][-3:]
            hits = {}
            for zt, lv in zl.items():
                cand = [x for x in lv if x == x and abs(ref - x) <= TOL]
                if cand:
                    hits[zt] = min(cand, key=lambda x: abs(ref - x))
            if not hits:
                continue
            lab = label(i, u, side)
            if lab is None:
                continue
            last[side] = i
            best = min(hits.values(), key=lambda x: abs(ref - x))
            for zt in hits:
                per_zone[zt][0] += lab
                per_zone[zt][1] += 1
            f = []
            f.append((c[i] - l[i]) / R if side < 0 else (h[i] - c[i]) / R)
            f.append(abs(dl[i]) / v[i])
            f.append(v[i] / mv)
            f.append((v[i] / mv) / max(1e-9, R / u))
            f.append(pocv[i] / v[i])
            f.append(-(abs(pocp[i] - ref) / R))
            f.append(avgsz[i] / ma)
            f.append(levels[i] / max(1e-9, R / TICK))
            f.append(-abs(ref - best))
            f.append((max(h[i - LOOK:i]) - l[i]) / u if side < 0 else (h[i] - min(l[i - LOOK:i])) / u)
            run5 = sum(dl[i - 5:i]) / (5 * md)
            f.append(-run5 if side < 0 else run5)
            f.append((dl[i + 1] / abs(dl[i])) * (-1 if side > 0 else 1))
            rng = max(1e-9, shi[i] - slo[i])
            f.append((1.0 - (ref - slo[i]) / rng) if side < 0 else ((ref - slo[i]) / rng))
            if side < 0:
                jl = min(range(i - LOOK, i), key=lambda j: l[j])
                f.append((cd[i] - cd[jl]) / (LOOK * md))
            else:
                jh = max(range(i - LOOK, i), key=lambda j: h[j])
                f.append(-(cd[i] - cd[jh]) / (LOOK * md))
            f.append(sum(1 for j in range(max(0, i - 120), i) if l[j] - 0.5 <= best <= h[j] + 0.5))
            rows_all.append((0 if i < half else 1, f, lab))

    tr = [r for r in rows_all if r[0] == 0]
    te = [r for r in rows_all if r[0] == 1]
    print("so ca TAI VUNG: nua dau %d, nua sau %d" % (len(tr), len(te)))
    if not tr or not te:
        sys.exit(0)
    b1 = 100.0 * sum(r[2] for r in tr) / len(tr)
    b2 = 100.0 * sum(r[2] for r in te) / len(te)
    print("ty le dao chieu nen: nua dau %.1f%%, nua sau %.1f%%" % (b1, b2))

    print("\n=== ty le dao chieu theo tung LOAI VUNG (ca 2 nua) ===")
    for zt in sorted(per_zone, key=lambda x: -per_zone[x][1]):
        s, cnt = per_zone[zt]
        if cnt < 60:
            print("    %-18s n=%5d (qua it)" % (zt, cnt)); continue
        print("    %-18s n=%5d  dao chieu %5.1f%%" % (zt, cnt, 100.0 * s / cnt))

    print("\n=== ty le DAO CHIEU theo ngu phan vi tung dac trung (nguong tu NUA DAU) ===")
    print("    dac trung                    | nua dau Q1..Q5             | nua sau Q1..Q5            | lech Q5-Q1")
    keep = []
    for fi, name in enumerate(FEATS):
        vals = [r[1][fi] for r in tr]
        cuts = [q(vals, p) for p in (0.2, 0.4, 0.6, 0.8)]

        def bucket(x):
            bb = 0
            for cc in cuts:
                if x > cc:
                    bb += 1
            return bb
        A = [[0, 0] for _ in range(5)]
        B = [[0, 0] for _ in range(5)]
        for _, f, lab in tr:
            j = bucket(f[fi]); A[j][0] += lab; A[j][1] += 1
        for _, f, lab in te:
            j = bucket(f[fi]); B[j][0] += lab; B[j][1] += 1
        pa = [100.0 * x[0] / x[1] if x[1] else float("nan") for x in A]
        pb = [100.0 * x[0] / x[1] if x[1] else float("nan") for x in B]
        d1, d2 = pa[4] - pa[0], pb[4] - pb[0]
        print("    %-28s | %s | %s | %+5.1f / %+5.1f"
              % (name, " ".join("%5.1f" % x for x in pa), " ".join("%5.1f" % x for x in pb), d1, d2))
        if abs(d1) >= 4.0 and d1 * d2 > 0:
            keep.append((name, fi, cuts, d1, d2))

    print("\n=== dac trung SONG SOT ca hai nua (|lech| >= 4 diem, cung dau) ===")
    if not keep:
        print("    KHONG CO dac trung nao song sot.")
    for name, fi, cuts, d1, d2 in sorted(keep, key=lambda x: -abs(x[4])):
        print("    %-28s nua dau %+5.1f  nua sau %+5.1f" % (name, d1, d2))
        top = sorted(keep, key=lambda x: -abs(x[4]))[:3]

    if keep:
        top = sorted(keep, key=lambda x: -abs(x[4]))[:3]
        print("\n=== LUAT GOP tu %d dac trung ===" % len(top))
        for nm, fi, cuts, d1, d2 in top:
            print("    - %s : %s %.4f" % (nm, "cao hon" if d1 > 0 else "thap hon",
                                          cuts[3] if d1 > 0 else cuts[0]))

        def ok(f):
            for nm, fi, cuts, d1, d2 in top:
                if d1 > 0 and f[fi] <= cuts[3]:
                    return False
                if d1 < 0 and f[fi] >= cuts[0]:
                    return False
            return True
        for tag, dsx, base in (("nua dau", tr, b1), ("nua sau", te, b2)):
            sel = [r for r in dsx if ok(r[1])]
            if len(sel) < 20:
                print("    %s: n=%d qua it" % (tag, len(sel))); continue
            p = 100.0 * sum(r[2] for r in sel) / len(sel)
            se = math.sqrt(base / 100 * (1 - base / 100) / len(sel)) * 100
            print("    %s: n=%5d  dao chieu %5.1f%%  (nen %5.1f%%)  z=%+5.2f"
                  % (tag, len(sel), p, base, (p - base) / se if se else 0))
