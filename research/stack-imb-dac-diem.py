"""BOC DAC DIEM ca stacked imbalance THANH CONG vs THAT BAI — 2,5 thang gan nhat.

Nguoi hoc: "trong so 148 lan gia di len tiep va 165 lan gia di xuong tiep, dac diem chung la gi?"
=> Voi tung ca, trich 16 dac trung roi so nhom DI THEO chieu vs nhom DI NGUOC.

Canh bao phuong phap (bai hoc DAC-DIEM-CA-DAO-CHIEU.md): n chi vai tram, thu 16 dac trung thi
gan nhu chac chan co vai cai "trong nhu that" do ngau nhien. Vi vay moi dac trung deu duoc do
RIENG o nua dau va nua sau cua ky; cai nao doi dau giua hai nua thi bi loai.

Chay:  python research/stack-imb-dac-diem.py [YYYY-MM-DD]   (mac dinh 2026-06-01)
"""
import os
import sys
import csv
import statistics as st
from collections import deque
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEATS = os.path.join(ROOT, "research/stack_imb_feats.csv")

RUN, HORIZON, LOOKBACK = 3, 20, 20
MAX_JUMP, MAX_GAP_MIN = 20.0, 5.0
DATE_FROM = datetime.strptime(sys.argv[1] if len(sys.argv) > 1 else "2026-06-01", "%Y-%m-%d")
# Ngay ket thuc (tuy chon) — de kiem combo NGOAI MAU tren giai doan khong dung de tim luat
DATE_TO = datetime.strptime(sys.argv[2], "%Y-%m-%d") if len(sys.argv) > 2 else None


def session_key(t):
    return (t + timedelta(hours=2)).date()


def load():
    """Doc bars (giu day du cot can dung) + feats."""
    rows = []
    with open(BARS, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append({
                "i": int(r["bar_idx"]), "t": datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S"),
                "o": float(r["open"]), "h": float(r["high"]), "l": float(r["low"]),
                "c": float(r["close"]), "vol": float(r["bar_volume"]),
                "delta": float(r["delta"]), "cum": float(r["cum_delta"]),
                "trades": float(r["trades"] or 0), "avg": float(r["avg_size"] or 0),
                "poc": float(r["poc_price"] or 0), "levels": float(r["levels"] or 0),
                "oi": float(r["open_interest"] or 0),
            })
    rows.sort(key=lambda x: x["i"])
    feats = {}
    with open(FEATS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["ready"] == "1":
                feats[int(r["bar_idx"])] = (int(r["s_ge"]), int(r["b_ge"]))
    bad, prev = set(), None
    for r in rows:
        if prev is not None and abs(r["c"] - prev) > MAX_JUMP:
            bad.add(session_key(r["t"]))
        prev = r["c"]
    bad |= {k + timedelta(days=1) for k in bad} | {k - timedelta(days=1) for k in bad}
    return rows, feats, bad


def fwd(rows, i):
    pt, pc, c0 = rows[i]["t"], rows[i]["c"], rows[i]["c"]
    for j in range(i + 1, i + HORIZON + 1):
        if j >= len(rows):
            return None
        t, c = rows[j]["t"], rows[j]["c"]
        if abs(c - pc) > MAX_JUMP or (t - pt).total_seconds() / 60.0 > MAX_GAP_MIN:
            return None
        pt, pc = t, c
    return pc - c0


def main():
    rows, feats, bad = load()
    n = len(rows)

    # ---- vwap phien, bien do ngay, trung vi volume/bien do 100 nen ----
    vwap = [0.0] * n
    day_hi = [0.0] * n
    day_lo = [0.0] * n
    cs, pv, vv, dh, dl = None, 0.0, 0.0, -1e9, 1e9
    qv, qr = deque(maxlen=100), deque(maxlen=100)
    med_v = [0.0] * n
    med_r = [0.0] * n
    for i, r in enumerate(rows):
        k = session_key(r["t"])
        if k != cs:
            cs, pv, vv, dh, dl = k, 0.0, 0.0, -1e9, 1e9
        pv += (r["h"] + r["l"] + r["c"]) / 3.0 * r["vol"]
        vv += r["vol"]
        vwap[i] = pv / vv if vv > 0 else r["c"]
        dh, dl = max(dh, r["h"]), min(dl, r["l"])
        day_hi[i], day_lo[i] = dh, dl
        med_v[i] = st.median(qv) if len(qv) >= 20 else 0.0
        med_r[i] = st.median(qr) if len(qr) >= 20 else 0.0
        qv.append(r["vol"])
        qr.append(r["h"] - r["l"])

    # ---- thu thap ca ----
    cases = []   # (chieu, thanh_cong, dict dac trung, index)
    for i in range(LOOKBACK, n - HORIZON - 1):
        r = rows[i]
        if r["t"] < DATE_FROM or session_key(r["t"]) in bad:
            continue
        if DATE_TO is not None and r["t"] >= DATE_TO:
            continue
        f = feats.get(r["i"])
        if f is None or med_v[i] <= 0 or med_r[i] <= 0:
            continue
        for sgn, ten in ((1, "MUA"), (-1, "BAN")):
            run = f[1] if sgn > 0 else f[0]
            if run < RUN:
                continue
            d = fwd(rows, i)
            if d is None or d == 0:
                continue
            rng = max(r["h"] - r["l"], 1e-9)
            # vi tri dong cua trong nen, tinh theo chieu tin hieu (1 = dong o dau nen theo chieu)
            pos = (r["c"] - r["l"]) / rng if sgn > 0 else (r["h"] - r["c"]) / rng
            streak_n = 0
            for j in range(i, max(i - 10, 0), -1):
                if (rows[j]["c"] > rows[j]["o"]) == (sgn > 0) and rows[j]["c"] != rows[j]["o"]:
                    streak_n += 1
                else:
                    break
            move20 = (r["c"] - rows[i - 20]["c"]) * sgn
            drange = max(day_hi[i] - day_lo[i], 1e-9)
            # vi tri trong bien do ngay theo chieu tin hieu (1 = dang o dau bien do theo chieu)
            dpos = (r["c"] - day_lo[i]) / drange if sgn > 0 else (day_hi[i] - r["c"]) / drange
            cases.append((ten, d * sgn > 0, {
                "so muc don": run,
                "delta nen (theo chieu)": r["delta"] * sgn,
                "delta/khoi luong nen": r["delta"] * sgn / max(r["vol"], 1),
                "khoi luong / trung vi": r["vol"] / med_v[i],
                "bien do nen / trung vi": rng / med_r[i],
                "dong cua o dau nen (0-1)": pos,
                "nen cung chieu lien tiep": streak_n,
                "da di duoc 20 nen (gia)": move20,
                "cach vwap ngay (gia, +la dung phia)": (r["c"] - vwap[i]) * sgn,
                "vi tri trong bien do ngay (0-1)": dpos,
                "bien do ngay den gio (gia)": drange,
                "so lenh trong nen": r["trades"],
                "co lenh trung binh": r["avg"],
                "so muc gia trong nen": r["levels"],
                "gio UTC": r["t"].hour,
                "poc nen so close (gia, +la dung phia)": (r["c"] - r["poc"]) * sgn,
            }, i))

    print("Khoang: %s -> %s | tong ca: %d" % (DATE_FROM.date(), rows[-1]["t"].date(), len(cases)))

    for ten in ("MUA", "BAN"):
        sub = [c for c in cases if c[0] == ten]
        if not sub:
            continue
        ok = sum(1 for c in sub if c[1])
        print("\n" + "=" * 100)
        print("%s DON — %d ca | di theo chieu %d | di nguoc %d" % (ten, len(sub), ok, len(sub) - ok))
        print("=" * 100)
        mid = len(sub) // 2
        keys = list(sub[0][2].keys())
        out = []
        for key in keys:
            vals = sorted(c[2][key] for c in sub)
            thr = vals[len(vals) // 2]
            # ro CAO (>= trung vi) vs ro THAP
            def rate(items, hi):
                g = [c for c in items if (c[2][key] >= thr) == hi]
                if not g:
                    return 0, 0.0
                return len(g), 100.0 * sum(1 for c in g if c[1]) / len(g)
            n_hi, p_hi = rate(sub, True)
            n_lo, p_lo = rate(sub, False)
            h1, h2 = sub[:mid], sub[mid:]
            _, p_hi1 = rate(h1, True)
            _, p_lo1 = rate(h1, False)
            _, p_hi2 = rate(h2, True)
            _, p_lo2 = rate(h2, False)
            d_all, d1, d2 = p_hi - p_lo, p_hi1 - p_lo1, p_hi2 - p_lo2
            song_sot = (d1 > 0 and d2 > 0) or (d1 < 0 and d2 < 0)
            out.append((abs(d_all), key, thr, n_hi, p_hi, n_lo, p_lo, d1, d2, song_sot))
        out.sort(reverse=True)
        print("  %-42s %8s | %-22s | %-22s | nua dau/nua sau" % ("dac trung", "nguong", "ro CAO", "ro THAP"))
        for _, key, thr, n_hi, p_hi, n_lo, p_lo, d1, d2, ss in out:
            if n_hi == 0 or n_lo == 0:      # ro rong (vd "so muc don" khi hau het = 3) -> vo nghia
                continue
            print("  %-42s %8.2f | %4d ca, theo %5.1f%% | %4d ca, theo %5.1f%% | %+5.1f / %+5.1f %s"
                  % (key, thr, n_hi, p_hi, n_lo, p_lo, d1, d2, "  <== SONG SOT" if ss else ""))

    # ---------------- COMBO: ghep cac dac trung song sot ----------------
    print("\n" + "#" * 100)
    print("# COMBO — ghep dac trung song sot ca hai nua (n nho, coi la GIA THUYET)")
    print("#" * 100)
    combos = [
        ("MUA · gia CHUA chay xa (<2,5) + nen KHONG dong sat dinh (<0,75)", "MUA",
         lambda x: x["da di duoc 20 nen (gia)"] < 2.5 and x["dong cua o dau nen (0-1)"] < 0.75),
        ("MUA · chi 'chua chay xa' (<2,5)", "MUA",
         lambda x: x["da di duoc 20 nen (gia)"] < 2.5),
        ("MUA · chi 'khong dong sat dinh' (<0,75)", "MUA",
         lambda x: x["dong cua o dau nen (0-1)"] < 0.75),
        ("MUA · TAT CA (doi chung)", "MUA", lambda x: True),
        ("BAN · dong SAT DAY (>=0,71) + bien do ngay rong (>=52)", "BAN",
         lambda x: x["dong cua o dau nen (0-1)"] >= 0.71 and x["bien do ngay den gio (gia)"] >= 52.0),
        ("BAN · dong SAT DAY + bien do rong + sau 9h UTC", "BAN",
         lambda x: x["dong cua o dau nen (0-1)"] >= 0.71 and x["bien do ngay den gio (gia)"] >= 52.0
         and x["gio UTC"] >= 9),
        ("BAN · chi 'dong sat day' (>=0,71)", "BAN",
         lambda x: x["dong cua o dau nen (0-1)"] >= 0.71),
        ("BAN · TAT CA (doi chung)", "BAN", lambda x: True),
        # --- combo rut ra tu 22 THANG (n lon), kiem lai tren 2,5 thang gan nhat ---
        ("MUA-22T · co lenh TB >=1,15 + delta nen >=65 + dong sat dinh >=0,77", "MUA",
         lambda x: x["co lenh trung binh"] >= 1.15 and x["delta nen (theo chieu)"] >= 65
         and x["dong cua o dau nen (0-1)"] >= 0.77),
        ("MUA-22T · co lenh TB >=1,15 + dong sat dinh >=0,77", "MUA",
         lambda x: x["co lenh trung binh"] >= 1.15 and x["dong cua o dau nen (0-1)"] >= 0.77),
        ("MUA-22T · chi co lenh TB >=1,15", "MUA", lambda x: x["co lenh trung binh"] >= 1.15),
        ("BAN-22T · chua giam nhieu (<1,3) + it lenh (<162) + ngay yen (<21,9)", "BAN",
         lambda x: x["da di duoc 20 nen (gia)"] < 1.3 and x["so lenh trong nen"] < 162
         and x["bien do ngay den gio (gia)"] < 21.9),
        ("BAN-22T · chua giam nhieu (<1,3) + ngay yen (<21,9)", "BAN",
         lambda x: x["da di duoc 20 nen (gia)"] < 1.3 and x["bien do ngay den gio (gia)"] < 21.9),
        ("BAN-22T · chi chua giam nhieu (<1,3)", "BAN", lambda x: x["da di duoc 20 nen (gia)"] < 1.3),
    ]
    for ten_combo, chieu, pred in combos:
        sub = [c for c in cases if c[0] == chieu and pred(c[2])]
        if not sub:
            print("  %-62s  0 ca" % ten_combo)
            continue
        allc = [c for c in cases if c[0] == chieu]
        mid_i = allc[len(allc) // 2][3]
        h1 = [c for c in sub if c[3] < mid_i]
        h2 = [c for c in sub if c[3] >= mid_i]

        def r(items):
            if not items:
                return 0, 0, 0.0
            ok = sum(1 for c in items if c[1])
            return len(items), ok, 100.0 * ok / len(items)
        n0, ok0, p0 = r(sub)
        n1, ok1, p1 = r(h1)
        n2, ok2, p2 = r(h2)
        print("  %-62s %4d ca | theo %4d / nguoc %4d = %5.1f%% | nua dau %5.1f%% (n=%d) / nua sau %5.1f%% (n=%d)"
              % (ten_combo, n0, ok0, n0 - ok0, p0, p1, n1, p2, n2))


if __name__ == "__main__":
    main()
