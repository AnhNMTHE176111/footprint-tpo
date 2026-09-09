"""BOC DAC DIEM: trong so cac ca DAO CHIEU, cai gi khac voi ca THAT BAI?

Muc tieu: tim DIEU KIEN NHAN DANG hap thu (chua ban entry).

Cach lam:
  1. Lay tap su kien RONG: vol >= 2,5x trung vi 50 nen  VA  |delta| >= 3x trung vi 50 nen,
     ca hai chieu (ban chu dong / mua chu dong). Khong doi pha cuc tri.
  2. Gan nhan: DAO CHIEU = gia cham c +- 2u NGUOC huong chu dong TRUOC (u = trung vi bien do 50 nen).
  3. Tinh ~14 dac trung cho tung ca, tat ca da chuan hoa theo chieu (cao = giong hap thu hon).
  4. CHIA DOI THOI GIAN: nua dau = tim luat, nua sau = kiem tra. Nguong ngu phan vi lay tu nua dau.
  5. Bao ty le dao chieu theo tung ngu phan vi + kiem lai o nua sau.

Cot dung duoc trong file bars: volume, bar_ticks, bid_vol, ask_vol, delta, cum_delta, trades,
avg_size, levels, poc_price, poc_volume. (buy_trades/sell_trades/max_one_trade = 0, khong dung.)
"""
import os, sys, math, csv, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W, LOOK, HOR, FWD = 50, 20, 60, 30
TICK = 0.1


def days_from_civil(y, m, d):
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def load_full(path):
    cols = ("open", "high", "low", "close", "volume", "delta", "cum_delta", "trades",
            "avg_size", "levels", "poc_price", "poc_volume", "bar_ticks")
    out = {k: [] for k in cols}
    t = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        hd = next(r)
        ix = {k: i for i, k in enumerate(hd)}
        for row in r:
            s = row[ix["datetime"]]
            t.append(days_from_civil(int(s[0:4]), int(s[5:7]), int(s[8:10])) * 1440
                     + int(s[11:13]) * 60 + int(s[14:16]))
            for k in cols:
                out[k].append(float(row[ix[k]]))
    return t, out


MODE = int(os.environ.get("MODE", "0"))


def outcome(i, u, side, h, l, c):
    """DAO CHIEU = cham 2u nguoc huong chu dong truoc. side=-1: ban chu dong => dao chieu la LEN.
    MODE=0: neo tai gia dong nen su kien (nen xac nhan NAM TRONG duong do => vong lap).
    MODE=1: neo tai gia dong NEN SAU, bat dau do tu nen i+2 => loai vong lap."""
    a0 = i if MODE == 0 else i + 1
    up = c[a0] + 2 * u
    dn = c[a0] - 2 * u
    for j in range(a0 + 1, min(i + HOR, len(h) - 1)):
        a = h[j] >= up
        b = l[j] <= dn
        if a and b:
            return None
        if a:
            return 1 if side < 0 else 0
        if b:
            return 0 if side < 0 else 1
    return None


def q(vals, p):
    s = sorted(vals)
    k = (len(s) - 1) * p
    f = int(k)
    return s[f] if f + 1 >= len(s) else s[f] + (s[f + 1] - s[f]) * (k - f)


if __name__ == "__main__":
    t, D = load_full(BARS)
    o, h, l, c = D["open"], D["high"], D["low"], D["close"]
    v, dl, cd = D["volume"], D["delta"], D["cum_delta"]
    trades, avgsz, levels = D["trades"], D["avg_size"], D["levels"]
    pocp, pocv = D["poc_price"], D["poc_volume"]
    n = len(t)
    print("so nen %d" % n, flush=True)

    # phien + VWAP ngay
    sid = [0] * n
    k = 0
    for i in range(1, n):
        if t[i] - t[i - 1] > 30:
            k += 1
        sid[i] = k
    vwd = [0.0] * n
    slo = [0.0] * n
    shi = [0.0] * n
    pv = pvol = 0.0
    lo = 1e18
    hi = -1e18
    cur = -1
    for i in range(n):
        if sid[i] != cur:
            cur = sid[i]; pv = pvol = 0.0; lo = 1e18; hi = -1e18
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]
        vwd[i] = pv / pvol if pvol > 0 else c[i]
        lo = min(lo, l[i]); hi = max(hi, h[i])
        slo[i] = lo; shi[i] = hi

    FEATS = ["dong nguoc phia (%)", "|delta|/khoi luong", "khoi luong /nen", "no luc/ket qua",
             "POC hut (%vol)", "POC sat cuc tri", "co lenh (avg_size)", "so muc gia /bien do",
             "gan VWAP ngay", "chan truoc do dai", "da chu dong 5 nen", "nen sau xac nhan",
             "cuc tri phien", "delta phan ky"]
    rows = []          # (half, feat_vector, label)
    last = {-1: -10 ** 9, 1: -10 ** 9}
    half_bar = n // 2
    for i in range(W + LOOK, n - HOR - 4):
        seg = t[i - W:i + HOR + 4]
        if seg[-1] - seg[0] != len(seg) - 1:
            continue
        mv = st.median(v[i - W:i])
        md = st.median([abs(x) for x in dl[i - W:i]])
        u = st.median([h[j] - l[j] for j in range(i - W, i)])
        ma = st.median(avgsz[i - W:i])
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
            lab = outcome(i, u, side, h, l, c)
            if lab is None:
                continue
            last[side] = i
            ref = l[i] if side < 0 else h[i]
            # dac trung, tat ca: CAO = giong hap thu hon
            f = []
            f.append((c[i] - l[i]) / R if side < 0 else (h[i] - c[i]) / R)   # dong nguoc phia
            f.append(abs(dl[i]) / v[i])
            f.append(v[i] / mv)
            f.append((v[i] / mv) / max(1e-9, R / u))
            f.append(pocv[i] / v[i])
            f.append(-(abs(pocp[i] - ref) / R))                              # POC cang sat cuc tri cang cao
            f.append(avgsz[i] / ma)
            f.append(levels[i] / max(1e-9, R / TICK))
            f.append(-(abs(ref - vwd[i]) / u))                               # cang gan VWAP cang cao
            prev_leg = (max(h[i - LOOK:i]) - l[i]) / u if side < 0 else (h[i] - min(l[i - LOOK:i])) / u
            f.append(prev_leg)
            run5 = sum(dl[i - 5:i]) / (5 * md)
            f.append(-run5 if side < 0 else run5)                            # da chu dong cung chieu
            f.append((dl[i + 1] / abs(dl[i])) * (-1 if side > 0 else 1))     # nen sau dao dau
            rng = max(1e-9, shi[i] - slo[i])
            f.append((1.0 - (ref - slo[i]) / rng) if side < 0 else ((ref - slo[i]) / rng))
            # delta phan ky: cum_delta hien tai so voi cum_delta tai cuc tri truoc do
            if side < 0:
                jlow = min(range(i - LOOK, i), key=lambda j: l[j])
                f.append((cd[i] - cd[jlow]) / (LOOK * md))
            else:
                jhigh = max(range(i - LOOK, i), key=lambda j: h[j])
                f.append(-(cd[i] - cd[jhigh]) / (LOOK * md))
            rows.append((0 if i < half_bar else 1, f, lab))

    tr = [r for r in rows if r[0] == 0]
    te = [r for r in rows if r[0] == 1]
    print("so ca: nua dau %d, nua sau %d" % (len(tr), len(te)))
    print("ty le dao chieu nen: nua dau %.1f%%, nua sau %.1f%%"
          % (100.0 * sum(r[2] for r in tr) / len(tr), 100.0 * sum(r[2] for r in te) / len(te)))

    print("\n=== ty le DAO CHIEU theo ngu phan vi tung dac trung (nguong lay tu NUA DAU) ===")
    print("    dac trung                    | nua dau: Q1..Q5            | nua sau: Q1..Q5           | do lech Q5-Q1 (dau/sau)")
    keep = []
    for fi, name in enumerate(FEATS):
        vals = [r[1][fi] for r in tr]
        cuts = [q(vals, p) for p in (0.2, 0.4, 0.6, 0.8)]

        def bucket(x):
            b = 0
            for cc in cuts:
                if x > cc:
                    b += 1
            return b
        a = [[0, 0] for _ in range(5)]
        b = [[0, 0] for _ in range(5)]
        for hf, f, lab in tr:
            bb = bucket(f[fi]); a[bb][0] += lab; a[bb][1] += 1
        for hf, f, lab in te:
            bb = bucket(f[fi]); b[bb][0] += lab; b[bb][1] += 1
        pa = [100.0 * x[0] / x[1] if x[1] else float("nan") for x in a]
        pb = [100.0 * x[0] / x[1] if x[1] else float("nan") for x in b]
        d1 = pa[4] - pa[0]
        d2 = pb[4] - pb[0]
        print("    %-28s | %s | %s | %+5.1f / %+5.1f"
              % (name, " ".join("%5.1f" % x for x in pa), " ".join("%5.1f" % x for x in pb), d1, d2))
        if abs(d1) >= 3.0 and d1 * d2 > 0:
            keep.append((name, fi, cuts, d1, d2))

    print("\n=== dac trung SONG SOT ca hai nua (|lech| >= 3 diem o nua dau VA cung dau o nua sau) ===")
    for name, fi, cuts, d1, d2 in sorted(keep, key=lambda x: -abs(x[4])):
        print("    %-28s lech nua dau %+5.1f  nua sau %+5.1f" % (name, d1, d2))
    if not keep:
        print("    KHONG CO dac trung nao song sot.")

    # luat gop: lay toi da 3 dac trung song sot manh nhat, doi vao ngu phan vi cao nhat (hoac thap nhat)
    if keep:
        top = sorted(keep, key=lambda x: -abs(x[4]))[:3]
        print("\n=== LUAT GOP: dong thoi vao phia tot cua %d dac trung ===" % len(top))
        for nm, fi, cuts, d1, d2 in top:
            print("    - %s : %s nguong %.4f" % (nm, "cao hon" if d1 > 0 else "thap hon",
                                                 cuts[3] if d1 > 0 else cuts[0]))

        def ok(f):
            for nm, fi, cuts, d1, d2 in top:
                if d1 > 0 and f[fi] <= cuts[3]:
                    return False
                if d1 < 0 and f[fi] >= cuts[0]:
                    return False
            return True
        for tag, ds in (("nua dau", tr), ("nua sau", te)):
            sel = [r for r in ds if ok(r[1])]
            base = 100.0 * sum(r[2] for r in ds) / len(ds)
            if len(sel) < 20:
                print("    %s: n=%d qua it" % (tag, len(sel)))
                continue
            p = 100.0 * sum(r[2] for r in sel) / len(sel)
            se = math.sqrt(base / 100 * (1 - base / 100) / len(sel)) * 100
            print("    %s: n=%5d  dao chieu %5.1f%%  (nen %5.1f%%)  z=%+5.2f"
                  % (tag, len(sel), p, base, (p - base) / se if se else 0))
