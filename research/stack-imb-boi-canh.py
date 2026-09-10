"""STACKED IMBALANCE trong BOI CANH — theo dung 3 rule nguoi hoc dat ra (2026-09-10).

Nguoi hoc KHONG muon bien no thanh signal; chi muon biet: dat vao boi canh thi stacked
imbalance co phai DAU HIEU cua phe chu dong that (gia di tiep theo chieu cua no) hay khong.

Rule 1 — BIAS theo VWAP NGAY:  close > vwap  -> chi xet BUY imbalance
                               close < vwap  -> chi xet SELL imbalance
   VWAP reset dau phien CME = 22:00 UTC (data-export/README.md: file ghi UTC, gio nghi 21-22h UTC).

Rule 2 — KICH BAN A "tiep dien sau nhip hoi":
   co 1 MOVE theo chieu bias trong 20 nen truoc, roi 1 NHIP HOI, roi nen tin hieu di theo
   chieu move VA co stacked imbalance cung chieu.

Rule 3 — KICH BAN B "giua move":
   nen tin hieu nam trong chuoi >= 3 nen lien tiep cung chieu (vd 3 nen giam) va co stacked
   imbalance cung chieu.

DOI CHUNG (bat buoc): cung boi canh, cung chieu, cung bias — nhung KHONG co stacked imbalance.
Chi so nay tra loi dung cau hoi "imbalance co THEM gi so voi chinh boi canh do".

Nguon: research/stack_imb_feats.csv (da trich tu file per-level 583 MB) + file _bars.csv.
Bien the nguong dung o day: `>=` (s_ge/b_ge) — ban da nới theo de xuat cua nguoi hoc.
Chong bay: bo phien co buoc nhay noi hop dong (>20 gia/nen); cua so forward phai lien tuc
(<=5 phut/nen, khong nhay gia); TACH DOI THOI GIAN.
"""
import os, csv, statistics as st
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEATS = os.path.join(ROOT, "research/stack_imb_feats.csv")

RUN = 3            # so muc lien tiep de goi la stacked
MOVE_MIN = 2.0     # gia — do lon toi thieu cua MOVE (20 tick GC)
PULL_MIN = 0.30    # nhip hoi >= 30% bien do move
LOOKBACK = 20      # cua so tim move
STREAK = 3         # kich ban B: chuoi n nen lien tiep cung chieu
HORIZONS = [3, 5, 10, 20]
MAX_JUMP = 20.0
MAX_GAP_MIN = 5.0


def session_key(t):
    """Phien CME bat dau 22:00 UTC -> gan nen vao ngay phien."""
    return (t + timedelta(hours=2)).date()


def load():
    rows = []
    with open(BARS, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append((
                int(r["bar_idx"]),
                datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S"),
                float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]),
                float(r["bar_volume"]),
            ))
    rows.sort(key=lambda x: x[0])

    feats = {}
    with open(FEATS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["ready"] == "1":
                feats[int(r["bar_idx"])] = (int(r["s_ge"]), int(r["b_ge"]))

    # VWAP theo phien + danh dau phien co buoc nhay noi hop dong
    bad = set()
    vwap = [0.0] * len(rows)
    cs = None
    pv = vol = 0.0
    prev_c = None
    for i, (bi, t, o, h, l, c, v) in enumerate(rows):
        k = session_key(t)
        if k != cs:
            cs, pv, vol = k, 0.0, 0.0
        tp = (h + l + c) / 3.0
        pv += tp * v
        vol += v
        vwap[i] = pv / vol if vol > 0 else c
        if prev_c is not None and abs(c - prev_c) > MAX_JUMP:
            bad.add(k)
        prev_c = c
    # loai ca phien lien ke chuc noi
    bad |= {k + timedelta(days=1) for k in bad} | {k - timedelta(days=1) for k in bad}
    return rows, feats, vwap, bad


def fwd(rows, i, k):
    if i + k >= len(rows):
        return None
    c0 = rows[i][5]
    pt, pc = rows[i][1], c0
    for j in range(i + 1, i + k + 1):
        t, c = rows[j][1], rows[j][5]
        if abs(c - pc) > MAX_JUMP or (t - pt).total_seconds() / 60.0 > MAX_GAP_MIN:
            return None
        pt, pc = t, c
    return pc - c0


def has_move(rows, i, sgn):
    """Kich ban A: co move theo chieu sgn trong LOOKBACK nen, roi nhip hoi >= PULL_MIN."""
    lo = i - LOOKBACK
    if lo < 0:
        return False
    start = rows[lo][5]
    seg = [rows[j][5] for j in range(lo, i)]
    if sgn < 0:
        ext = min(seg); m = lo + seg.index(ext)
        if ext > start - MOVE_MIN:
            return False
        amp = start - ext
        back = max(rows[j][5] for j in range(m, i))
        return m <= i - 2 and back >= ext + PULL_MIN * amp
    ext = max(seg); m = lo + seg.index(ext)
    if ext < start + MOVE_MIN:
        return False
    amp = ext - start
    back = min(rows[j][5] for j in range(m, i))
    return m <= i - 2 and back <= ext - PULL_MIN * amp


def streak(rows, i, sgn):
    """Kich ban B: STREAK nen lien tiep cung chieu, ket thuc tai i."""
    for j in range(i - STREAK + 1, i + 1):
        if j < 0:
            return False
        o, c = rows[j][2], rows[j][5]
        if sgn < 0 and not c < o:
            return False
        if sgn > 0 and not c > o:
            return False
    return True


def main():
    rows, feats, vwap, bad = load()
    n = len(rows)
    half = n // 2
    print("nen: %d | phien loai vi noi hop dong: %d" % (n, len(bad)))

    def collect(scenario, sgn, want_imb):
        """tra ve list (i) thoa dieu kien"""
        out = []
        for i in range(LOOKBACK, n - max(HORIZONS) - 1):
            bi, t, o, h, l, c, v = rows[i]
            if session_key(t) in bad:
                continue
            f = feats.get(bi)
            if f is None:
                continue
            s_ge, b_ge = f
            # bias VWAP
            if sgn < 0 and not c < vwap[i]:
                continue
            if sgn > 0 and not c > vwap[i]:
                continue
            # nen tin hieu di theo chieu
            if sgn < 0 and not c < o:
                continue
            if sgn > 0 and not c > o:
                continue
            imb = (s_ge if sgn < 0 else b_ge) >= RUN
            if imb != want_imb:
                continue
            if scenario == "A" and not has_move(rows, i, sgn):
                continue
            if scenario == "B" and not streak(rows, i, sgn):
                continue
            out.append(i)
        return out

    def stat(idx, sgn, k, lo, hi):
        moves = []
        for i in idx:
            if not (lo <= i < hi):
                continue
            d = fwd(rows, i, k)
            if d is None:
                continue
            moves.append(d * sgn)
        if not moves:
            return 0, float("nan"), float("nan")
        return len(moves), 100.0 * sum(1 for m in moves if m > 0) / len(moves), st.median(moves)

    for scenario, title in (("A", "KICH BAN A — sau MOVE + NHIP HOI, nen theo chieu move"),
                            ("B", "KICH BAN B — GIUA MOVE (>=%d nen lien tiep cung chieu)" % STREAK),
                            ("-", "KHONG DIEU KIEN BOI CANH (chi bias VWAP + nen theo chieu)")):
        for sgn, sname in ((-1, "SELL (duoi VWAP)"), (1, "BUY (tren VWAP)")):
            withi = collect(scenario, sgn, True)
            wout = collect(scenario, sgn, False)
            print("\n=== %s | %s ===" % (title, sname))
            print("  n tin hieu (co imbalance): %d | doi chung (khong imbalance): %d"
                  % (len(withi), len(wout)))
            print("   k |  CO imbalance: nua dau / nua sau      |  KHONG imbalance: nua dau / nua sau")
            for k in HORIZONS:
                a1 = stat(withi, sgn, k, 0, half)
                a2 = stat(withi, sgn, k, half, n)
                b1 = stat(wout, sgn, k, 0, half)
                b2 = stat(wout, sgn, k, half, n)
                print("  %2d | %5d %5.1f%% %+5.2f / %5d %5.1f%% %+5.2f | %6d %5.1f%% %+5.2f / %6d %5.1f%% %+5.2f"
                      % (k, a1[0], a1[1], a1[2], a2[0], a2[1], a2[2],
                         b1[0], b1[1], b1[2], b2[0], b2[1], b2[2]))


if __name__ == "__main__":
    main()
