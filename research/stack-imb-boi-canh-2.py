"""STACKED IMBALANCE + BOI CANH — tach dong gop cua BIAS VWAP (2026-09-10, lan 2).

Phep do truoc (stack-imb-boi-canh.py) DA lot bias VWAP vao ca kich ban A va B. Lan nay do
ba bien the de THAY dong gop rieng cua VWAP:
   THEO   : buy chi khi close > vwap ngay | sell chi khi close < vwap    (nhu lan truoc)
   BO     : khong quan tam vwap
   NGUOC  : buy khi close < vwap | sell khi close > vwap                 (kiem chieu nguoc)

Kich ban giu nguyen dinh nghia lan truoc:
   A = co move >= 2,0 gia theo chieu trong 20 nen truoc, roi hoi >= 30% bien do, nen tin hieu
       di theo chieu move
   B = nen tin hieu nam trong chuoi >= 3 nen lien tiep cung chieu
Doi chung moi o: CUNG kich ban + CUNG bien the vwap + cung chieu nen, nhung KHONG co imbalance.

Khac lan truoc ve ky thuat: chi mot pass tinh co (flag) cho tung nen roi tong hop moi to hop
=> nhanh hon nhieu lan quet lai.
"""
import os
import sys
import csv
import statistics as st
from datetime import datetime, timedelta

# Tham so dong lenh: ngay bat dau (YYYY-MM-DD). Vd  python stack-imb-boi-canh-2.py 2026-06-01
# Nen truoc ngay nay VAN duoc dung de tinh vwap/lookback, chi khong duoc tinh la ca do.
DATE_FROM = datetime.strptime(sys.argv[1], "%Y-%m-%d") if len(sys.argv) > 1 else None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEATS = os.path.join(ROOT, "research/stack_imb_feats.csv")

RUN, MOVE_MIN, PULL_MIN, LOOKBACK, STREAK = 3, 2.0, 0.30, 20, 3
HORIZONS = [5, 10, 20]
MAX_JUMP, MAX_GAP_MIN = 20.0, 5.0


def session_key(t):
    """Phien CME bat dau 22:00 UTC."""
    return (t + timedelta(hours=2)).date()


def load():
    """Doc bars + feats, tinh vwap phien, danh dau phien dinh cho noi hop dong."""
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
    vwap = [0.0] * len(rows)
    bad, cs, pv, vol, prev_c = set(), None, 0.0, 0.0, None
    for i, (_bi, t, _o, h, l, c, v) in enumerate(rows):
        k = session_key(t)
        if k != cs:
            cs, pv, vol = k, 0.0, 0.0
        pv += (h + l + c) / 3.0 * v
        vol += v
        vwap[i] = pv / vol if vol > 0 else c
        if prev_c is not None and abs(c - prev_c) > MAX_JUMP:
            bad.add(k)
        prev_c = c
    bad |= {k + timedelta(days=1) for k in bad} | {k - timedelta(days=1) for k in bad}
    return rows, feats, vwap, bad


def has_move(rows, i, sgn):
    """Kich ban A: move theo chieu sgn roi nhip hoi >= PULL_MIN."""
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
    """Kich ban B: STREAK nen lien tiep cung chieu, ket thuc tai i."""
    for j in range(i - STREAK + 1, i + 1):
        if j < 0:
            return False
        if sgn < 0 and not rows[j][5] < rows[j][2]:
            return False
        if sgn > 0 and not rows[j][5] > rows[j][2]:
            return False
    return True


def fwd_all(rows, i):
    """close[i+k]-close[i] cho moi k trong HORIZONS; None neu cua so bi gian doan."""
    out, pt, pc = {}, rows[i][1], rows[i][5]
    c0 = pc
    kmax = max(HORIZONS)
    for j in range(i + 1, i + kmax + 1):
        if j >= len(rows):
            break
        t, c = rows[j][1], rows[j][5]
        if abs(c - pc) > MAX_JUMP or (t - pt).total_seconds() / 60.0 > MAX_GAP_MIN:
            break
        pt, pc = t, c
        k = j - i
        if k in HORIZONS:
            out[k] = c - c0
    return out


def main():
    rows, feats, vwap, bad = load()
    n = len(rows)
    half = n // 2
    print("nen: %d | phien loai: %d" % (n, len(bad)), flush=True)

    # ---- mot pass: gom du lieu tung nen thoa "nen di theo chieu" ----
    recs = []          # (i, sgn, above_vwap, has_imb, in_A, in_B, {k: move})
    for i in range(LOOKBACK, n - max(HORIZONS) - 1):
        _bi, t, o, _h, _l, c, _v = rows[i]
        if DATE_FROM is not None and t < DATE_FROM:
            continue
        if session_key(t) in bad:
            continue
        f = feats.get(_bi)
        if f is None:
            continue
        sgn = -1 if c < o else (1 if c > o else 0)
        if sgn == 0:
            continue
        imb = (f[0] if sgn < 0 else f[1]) >= RUN
        mv = fwd_all(rows, i)
        if len(mv) < len(HORIZONS):
            continue
        recs.append((i, sgn, c > vwap[i], imb, has_move(rows, i, sgn), streak(rows, i, sgn), mv))
        if len(recs) % 200000 == 0:
            print("  ...%d nen thu thap" % len(recs), flush=True)
    print("tong ca: %d" % len(recs), flush=True)
    # chia doi theo TAP CA thuc te (khong theo toan file) — de con dung khi loc theo ngay
    if recs:
        half = recs[len(recs) // 2][0]
        print("khoang do: %s -> %s | moc chia doi: %s"
              % (rows[recs[0][0]][1], rows[recs[-1][0]][1], rows[half][1]), flush=True)

    def group(scen, sgn, vwmode, want_imb, lo, hi, k):
        vals = []
        for (i, s, above, imb, inA, inB, mv) in recs:
            if s != sgn or imb != want_imb or not lo <= i < hi:
                continue
            if scen == "A" and not inA:
                continue
            if scen == "B" and not inB:
                continue
            if vwmode == "THEO" and above != (sgn > 0):
                continue
            if vwmode == "NGUOC" and above == (sgn > 0):
                continue
            vals.append(mv[k] * sgn)
        if not vals:
            return 0, float("nan"), float("nan")
        return len(vals), 100.0 * sum(1 for x in vals if x > 0) / len(vals), st.median(vals)

    for scen, sname in (("A", "KICH BAN A (sau move + nhip hoi)"),
                        ("B", "KICH BAN B (giua move)")):
        for sgn, dname in ((1, "BUY"), (-1, "SELL")):
            print("\n############ %s | %s ############" % (sname, dname))
            for vw in ("THEO", "BO", "NGUOC"):
                print("  --- bias VWAP: %s ---" % vw)
                print("    k |   CO imb: nua dau / nua sau        | KHONG imb: nua dau / nua sau      | LECH")
                for k in HORIZONS:
                    a1 = group(scen, sgn, vw, True, 0, half, k)
                    a2 = group(scen, sgn, vw, True, half, n, k)
                    b1 = group(scen, sgn, vw, False, 0, half, k)
                    b2 = group(scen, sgn, vw, False, half, n, k)
                    d1 = a1[1] - b1[1]
                    d2 = a2[1] - b2[1]
                    print("   %2d | %5d %5.1f%% %+5.2f / %5d %5.1f%% %+5.2f | %6d %5.1f%% / %6d %5.1f%% | %+5.1f / %+5.1f"
                          % (k, a1[0], a1[1], a1[2], a2[0], a2[1], a2[2],
                             b1[0], b1[1], b2[0], b2[1], d1, d2))


if __name__ == "__main__":
    main()
