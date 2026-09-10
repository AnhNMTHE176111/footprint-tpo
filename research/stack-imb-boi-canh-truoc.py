"""BOI CANH TRUOC nen tin hieu — cai gi phan biet 148 ca mua don THANG vs 166 ca THUA?
(va 165 ca ban don thang vs 195 thua). Chi do 2,5 THANG GAN NHAT — nguoi hoc bo giai doan cu.

Khac cac script truoc: o day KHONG do dac diem cua chinh nen tin hieu (delta, co lenh, dong cua...)
ma do BOI CANH DA XAY RA TRUOC NO: da co move chua, move dai bao nhieu, move co thang khong,
da hoi lai bao nhieu phan tram, hoi cach day may nen, dang o dau trong bien do 60 nen, da pha
dinh/day cu chua, truoc do thi truong dang di ngang hay dang chay.

Chay: python research/stack-imb-boi-canh-truoc.py [YYYY-MM-DD]   (mac dinh 2026-06-01)
"""
import os
import sys
import csv
import statistics as st
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEATS = os.path.join(ROOT, "research/stack_imb_feats.csv")

RUN, HORIZON, LOOK = 3, 20, 60
MAX_JUMP, MAX_GAP_MIN = 20.0, 5.0
DATE_FROM = datetime.strptime(sys.argv[1] if len(sys.argv) > 1 else "2026-06-01", "%Y-%m-%d")


def session_key(t):
    return (t + timedelta(hours=2)).date()


def load():
    rows = []
    with open(BARS, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append({"i": int(r["bar_idx"]),
                         "t": datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S"),
                         "o": float(r["open"]), "h": float(r["high"]), "l": float(r["low"]),
                         "c": float(r["close"]), "vol": float(r["bar_volume"]),
                         "cum": float(r["cum_delta"] or 0)})
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


def boi_canh(rows, i, sgn):
    """Cac dac trung ve BOI CANH TRUOC nen i, tinh theo chieu tin hieu sgn."""
    seg = rows[i - LOOK:i]                      # 60 nen truoc, KHONG gom nen tin hieu
    cl = [r["c"] for r in seg]
    hi60 = max(r["h"] for r in seg)
    lo60 = min(r["l"] for r in seg)
    rng60 = max(hi60 - lo60, 1e-9)
    c = rows[i]["c"]

    # cuc tri THEO CHIEU trong 60 nen (buy -> dinh cao nhat; sell -> day thap nhat)
    if sgn > 0:
        ext = max(cl); k_ext = cl.index(ext)
        chan = min(cl[:k_ext + 1])              # chan cua dot day len
        amp = max(ext - chan, 1e-9)
        hoi = (ext - c) / amp                   # da hoi lai bao nhieu phan doan day
        pha_moc = c - hi60                      # >0 = dang pha dinh 60 nen
        vi_tri = (c - lo60) / rng60
    else:
        ext = min(cl); k_ext = cl.index(ext)
        chan = max(cl[:k_ext + 1])
        amp = max(chan - ext, 1e-9)
        hoi = (c - ext) / amp
        pha_moc = lo60 - c
        vi_tri = (hi60 - c) / rng60

    tuoi = len(seg) - k_ext                     # bao nhieu nen ke tu cuc tri
    tong_dong = sum(abs(cl[j] - cl[j - 1]) for j in range(1, len(cl))) or 1e-9
    hieu_suat = abs(cl[-1] - cl[0]) / tong_dong  # 1 = di thang, 0 = lình xình
    n_cung_chieu = sum(1 for r in seg[-20:] if (r["c"] > r["o"]) == (sgn > 0))
    bien_do_tb = st.mean(r["h"] - r["l"] for r in seg[-20:])

    return {
        "move 20 nen truoc (gia)": (c - cl[-20]) * sgn,
        "move 60 nen truoc (gia)": (c - cl[0]) * sgn,
        "do lon dot day gan nhat (gia)": amp,
        "da hoi lai bao nhieu (0=chua, 1=het)": hoi,
        "so nen ke tu dinh/day dot day": tuoi,
        "move di THANG hay lình xình (0-1)": hieu_suat,
        "bien do 60 nen (gia)": rng60,
        "vi tri trong bien do 60 nen (0-1)": vi_tri,
        "pha dinh/day 60 nen (gia, >0 la pha)": pha_moc,
        "so nen cung chieu trong 20 nen": n_cung_chieu,
        "bien do nen trung binh 20 nen": bien_do_tb,
        "delta luy ke phien (theo chieu)": rows[i]["cum"] * sgn,
    }


def main():
    rows, feats, bad = load()
    n = len(rows)
    cases = []
    for i in range(LOOK, n - HORIZON - 1):
        r = rows[i]
        if r["t"] < DATE_FROM or session_key(r["t"]) in bad:
            continue
        f = feats.get(r["i"])
        if f is None:
            continue
        # bo qua neu 60 nen truoc khong lien tuc (qua dem / nghi phien)
        gap = any((rows[j + 1]["t"] - rows[j]["t"]).total_seconds() / 60.0 > MAX_GAP_MIN
                  for j in range(i - LOOK, i))
        if gap:
            continue
        for sgn, ten in ((1, "MUA"), (-1, "BAN")):
            if (f[1] if sgn > 0 else f[0]) < RUN:
                continue
            d = fwd(rows, i)
            if d is None or d == 0:
                continue
            cases.append((ten, d * sgn > 0, boi_canh(rows, i, sgn), i))

    print("Khoang: %s -> %s | tong ca: %d" % (DATE_FROM.date(), rows[-1]["t"].date(), len(cases)))

    for ten in ("MUA", "BAN"):
        sub = [c for c in cases if c[0] == ten]
        if not sub:
            continue
        ok = sum(1 for c in sub if c[1])
        print("\n" + "=" * 104)
        print("%s DON — %d ca | THANG (di theo chieu) %d | THUA %d" % (ten, len(sub), ok, len(sub) - ok))
        print("=" * 104)
        mid = sub[len(sub) // 2][3]
        out = []
        for key in sub[0][2]:
            vals = sorted(c[2][key] for c in sub)
            thr = vals[len(vals) // 2]

            def dem(items, hi, key=key, thr=thr):
                g = [c for c in items if (c[2][key] >= thr) == hi]
                w = sum(1 for c in g if c[1])
                return len(g), w, (100.0 * w / len(g) if g else 0.0)
            n_hi, w_hi, p_hi = dem(sub, True)
            n_lo, w_lo, p_lo = dem(sub, False)
            h1 = [c for c in sub if c[3] < mid]
            h2 = [c for c in sub if c[3] >= mid]
            d1 = dem(h1, True)[2] - dem(h1, False)[2]
            d2 = dem(h2, True)[2] - dem(h2, False)[2]
            ss = (d1 > 0 and d2 > 0) or (d1 < 0 and d2 < 0)
            if n_hi == 0 or n_lo == 0:
                continue
            out.append((abs(p_hi - p_lo), key, thr, n_hi, w_hi, p_hi, n_lo, w_lo, p_lo, d1, d2, ss))
        out.sort(reverse=True)
        print("  %-40s %8s | %-24s | %-24s | 2 nua" % ("boi canh truoc do", "nguong", "ro CAO", "ro THAP"))
        for _, key, thr, n_hi, w_hi, p_hi, n_lo, w_lo, p_lo, d1, d2, ss in out:
            print("  %-40s %8.2f | %3d ca, thang %3d = %4.1f%% | %3d ca, thang %3d = %4.1f%% | %+5.1f/%+5.1f%s"
                  % (key, thr, n_hi, w_hi, p_hi, n_lo, w_lo, p_lo, d1, d2,
                     "  <== BEN" if ss else ""))


    # ---------------- COMBO tu cac dac trung BEN ----------------
    print("\n" + "#" * 104)
    print("# COMBO boi canh (chi tu dac trung ben ca hai nua)")
    print("#" * 104)
    combos = [
        ("MUA · con xa dinh 60 nen (>4 gia) + bien do 60 nen rong (>=15,5)", "MUA",
         lambda x: x["pha dinh/day 60 nen (gia, >0 la pha)"] < -4.0
         and x["bien do 60 nen (gia)"] >= 15.5),
        ("MUA · them: 20 nen truoc KHONG toan nen tang (<10)", "MUA",
         lambda x: x["pha dinh/day 60 nen (gia, >0 la pha)"] < -4.0
         and x["bien do 60 nen (gia)"] >= 15.5
         and x["so nen cung chieu trong 20 nen"] < 10),
        ("MUA · chi 'con xa dinh 60 nen'", "MUA",
         lambda x: x["pha dinh/day 60 nen (gia, >0 la pha)"] < -4.0),
        ("MUA · TAT CA (doi chung)", "MUA", lambda x: True),
        ("BAN · cuc tri dot day da cu (>=26 nen) + bien do 60 nen hep (<15,2)", "BAN",
         lambda x: x["so nen ke tu dinh/day dot day"] >= 26
         and x["bien do 60 nen (gia)"] < 15.2),
        ("BAN · them: phien chua ban rong nhieu", "BAN",
         lambda x: x["so nen ke tu dinh/day dot day"] >= 26
         and x["bien do 60 nen (gia)"] < 15.2
         and x["delta luy ke phien (theo chieu)"] < 459),
        ("BAN · chi 'cuc tri da cu (>=26 nen)'", "BAN",
         lambda x: x["so nen ke tu dinh/day dot day"] >= 26),
        ("BAN · TAT CA (doi chung)", "BAN", lambda x: True),
    ]
    for ten_c, chieu, pred in combos:
        sub = [c for c in cases if c[0] == chieu and pred(c[2])]
        allc = [c for c in cases if c[0] == chieu]
        mid_i = allc[len(allc) // 2][3]
        h1 = [c for c in sub if c[3] < mid_i]
        h2 = [c for c in sub if c[3] >= mid_i]

        def r(items):
            w = sum(1 for c in items if c[1])
            return len(items), w, (100.0 * w / len(items) if items else 0.0)
        n0, w0, p0 = r(sub)
        n1, w1, p1 = r(h1)
        n2, w2, p2 = r(h2)
        print("  %-64s %3d ca | thang %3d / thua %3d = %4.1f%% | nua dau %4.1f%% (%d) / nua sau %4.1f%% (%d)"
              % (ten_c, n0, w0, n0 - w0, p0, p1, n1, p2, n2))


if __name__ == "__main__":
    main()
