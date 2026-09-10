"""DEM DON GIAN — nguoi hoc muon con so tho, khong muon bang thong ke (2026-09-10).

Tra loi dung 5 cau: tong cong bao nhieu stacked imbalance? bao nhieu MUA, bao nhieu BAN?
bao nhieu luot sau do gia DI THEO chieu cua no, bao nhieu KHONG? phan lon roi vao kich ban nao?

Khac cac script truoc: dem MOI nen co imbalance (khong doi hoi nen phai cung chieu imbalance),
va bao ca so tuyet doi.
Chay:  python research/stack-imb-dem.py [YYYY-MM-DD ngay bat dau]
"""
import os
import sys
import csv
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEATS = os.path.join(ROOT, "research/stack_imb_feats.csv")

RUN, MOVE_MIN, PULL_MIN, LOOKBACK, STREAK = 3, 2.0, 0.30, 20, 3
HORIZON = 20
MAX_JUMP, MAX_GAP_MIN = 20.0, 5.0
DATE_FROM = datetime.strptime(sys.argv[1], "%Y-%m-%d") if len(sys.argv) > 1 else None


def session_key(t):
    return (t + timedelta(hours=2)).date()


def load():
    rows = []
    with open(BARS, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append([int(r["bar_idx"]),
                         datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S"),
                         float(r["open"]), float(r["high"]), float(r["low"]),
                         float(r["close"]), float(r["bar_volume"])])
    rows.sort(key=lambda x: x[0])
    feats = {}
    with open(FEATS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["ready"] == "1":
                feats[int(r["bar_idx"])] = (int(r["s_ge"]), int(r["b_ge"]))
    bad, prev_c = set(), None
    for (_bi, t, _o, _h, _l, c, _v) in rows:
        if prev_c is not None and abs(c - prev_c) > MAX_JUMP:
            bad.add(session_key(t))
        prev_c = c
    bad |= {k + timedelta(days=1) for k in bad} | {k - timedelta(days=1) for k in bad}
    return rows, feats, bad


def has_move(rows, i, sgn):
    lo = i - LOOKBACK
    if lo < 0:
        return False
    start = rows[lo][5]
    seg = [rows[j][5] for j in range(lo, i)]
    if sgn < 0:
        ext = min(seg)
        m = lo + seg.index(ext)
        if ext > start - MOVE_MIN:
            return False
        back = max(rows[j][5] for j in range(m, i))
        return m <= i - 2 and back >= ext + PULL_MIN * (start - ext)
    ext = max(seg)
    m = lo + seg.index(ext)
    if ext < start + MOVE_MIN:
        return False
    back = min(rows[j][5] for j in range(m, i))
    return m <= i - 2 and back <= ext - PULL_MIN * (ext - start)


def streak(rows, i, sgn):
    for j in range(i - STREAK + 1, i + 1):
        if j < 0:
            return False
        if sgn < 0 and not rows[j][5] < rows[j][2]:
            return False
        if sgn > 0 and not rows[j][5] > rows[j][2]:
            return False
    return True


def fwd(rows, i):
    pt, pc, c0 = rows[i][1], rows[i][5], rows[i][5]
    for j in range(i + 1, i + HORIZON + 1):
        if j >= len(rows):
            return None
        t, c = rows[j][1], rows[j][5]
        if abs(c - pc) > MAX_JUMP or (t - pt).total_seconds() / 60.0 > MAX_GAP_MIN:
            return None
        pt, pc = t, c
    return pc - c0


def main():
    rows, feats, bad = load()
    n = len(rows)
    tong_nen = 0
    # nhom[(chieu, kichban)] = [theo, nguoc, y_nguyen]
    dem = {}
    tong = {"MUA": [0, 0, 0], "BAN": [0, 0, 0]}
    ca_bo_qua = 0
    t_dau = t_cuoi = None

    for i in range(LOOKBACK, n - HORIZON - 1):
        _bi, t, _o, _h, _l, _c, _v = rows[i]
        if DATE_FROM is not None and t < DATE_FROM:
            continue
        if session_key(t) in bad:
            continue
        f = feats.get(_bi)
        if f is None:
            continue
        tong_nen += 1
        if t_dau is None:
            t_dau = t
        t_cuoi = t
        for sgn, ten in ((1, "MUA"), (-1, "BAN")):
            if (f[1] if sgn > 0 else f[0]) < RUN:
                continue
            d = fwd(rows, i)
            if d is None:
                ca_bo_qua += 1
                continue
            inA = has_move(rows, i, sgn)
            inB = streak(rows, i, sgn)
            kb = ("giua dot di" if inB else "") + ("+sau nhip hoi" if inA else "")
            if not kb:
                kb = "khong thuoc kich ban nao"
            kb = kb.lstrip("+")
            key = (ten, kb)
            if key not in dem:
                dem[key] = [0, 0, 0]
            k = 0 if d * sgn > 0 else (1 if d * sgn < 0 else 2)
            dem[key][k] += 1
            tong[ten][k] += 1

    print("Khoang do: %s -> %s | so nen xet: %d | bo qua vi cua so gian doan: %d"
          % (t_dau, t_cuoi, tong_nen, ca_bo_qua))
    for ten in ("MUA", "BAN"):
        theo, nguoc, yn = tong[ten]
        tot = theo + nguoc + yn
        print("\n===== %s DON (stacked %s imbalance) — tong %d lan =====" % (ten, ten.lower(), tot))
        if tot:
            print("  sau 20 phut: DI THEO chieu %d lan (%.1f%%) | NGUOC %d (%.1f%%) | y nguyen %d (%.1f%%)"
                  % (theo, 100.0 * theo / tot, nguoc, 100.0 * nguoc / tot, yn, 100.0 * yn / tot))
        print("  chia theo kich ban:")
        rowsk = [(k[1], v) for k, v in dem.items() if k[0] == ten]
        rowsk.sort(key=lambda x: -(x[1][0] + x[1][1] + x[1][2]))
        for kb, v in rowsk:
            s = v[0] + v[1] + v[2]
            print("    %-28s %5d lan (%4.1f%% tong) | theo %4d / nguoc %4d / y nguyen %3d -> theo %4.1f%%"
                  % (kb, s, 100.0 * s / max(tot, 1), v[0], v[1], v[2], 100.0 * v[0] / max(s, 1)))


if __name__ == "__main__":
    main()
