#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vung_dem.py — BẢN THAM CHIẾU "vùng đệm" của hộp HVN v2 (PLAN-VUNG-MANH.md mục 14, VUNG-DEM.md).

Vùng đệm = phần SƯỜN của cụm khối lượng nằm sát ngoài mép hộp: nới từ mép hộp ra ngoài chừng nào khối lượng mượt S
còn >= BF × đỉnh cụm (BF = 0,50 = đúng sàn HvnWidenFloor của luật nới hộp), tối đa BCAP × up (= HvnWidth),
hẹp hơn BMIN × up thì coi như không có. Khác luật nới hộp ở hai chỗ: KHÔNG dừng vì đã đủ bề rộng đích, KHÔNG có luật
"không leo" (được đi qua một đáy nông rồi lên bướu phụ, miễn chưa xuống dưới 50 % đỉnh).

Chỉ dùng mảng S, chỉ số nguyên và so sánh double như hvn_cum2.clusters ⇒ C# ra y hệt.

  python vung_dem.py ca nq25 2026-11-20       in hộp + vùng đệm của phiên và tuần chứa nó
  python vung_dem.py thongke nq25|gc          bề rộng vùng đệm trên mọi profile
"""
import sys
import numpy as np
import hvn_cum2 as HC2

BP = dict(
    BF=0.50,      # sàn: S >= BF × đỉnh cụm (= HP2["XMIN"])
    BCAP=0.45,    # bề rộng tối đa mỗi phía (× up) (= HP2["WT"])
    BMIN=0.05,    # hẹp hơn thì không có vùng đệm phía đó (× up)
)


def add_buffers(cl, ex, up_ticks, bp=BP):
    """cl, ex = kết quả hvn_cum2.clusters. Thêm vào mỗi hộp: blo, bhi (bước giá nguyên; blo = lo / bhi = hi nếu không có đệm)."""
    if not cl: return cl
    S, t0 = ex["S"], ex["t0"]; n = len(S)
    cap = max(1, int(np.floor(bp["BCAP"] * up_ticks + 0.5)))
    mn = bp["BMIN"] * up_ticks
    for c in cl:
        lo, hi, pk = c["lo"] - t0, c["hi"] - t0, c["peak"] - t0
        thr = bp["BF"] * S[pk]
        i = hi
        while i < n - 1 and (i - hi) < cap and S[i + 1] >= thr: i += 1
        k = lo
        while k > 0 and (lo - k) < cap and S[k - 1] >= thr: k -= 1
        c["bhi"] = t0 + (i if (i - hi) >= mn else hi)
        c["blo"] = t0 + (k if (lo - k) >= mn else lo)
    return cl


def prof_buffers(D, a, b, kind="d", hp=HC2.HP2, bp=BP):
    cl, ex = HC2.prof_clusters(D, a, b, hp, kind)
    return add_buffers(cl, ex, HC2.H1.up_of(D, a, b) / 0.1, bp), ex


def ca(sym, date):
    import pandas as pd
    import vung_dem_lib as L
    D, vm, V = L.load(sym)
    sc, t = L.SCALE[sym] * 0.1, pd.to_datetime(D.m30["t"])
    k = HC2.H1.find_day(D, date)
    wk = int(D.week_of[D.days[k][0]])
    for ten, (a, b), kind in (("phiên", D.days[k], "d"), ("tuần", D.weeks[wk], "w")):
        up = HC2.H1.up_of(D, a, b) * L.SCALE[sym]
        cl, ex = prof_buffers(D, a, b, kind)
        print("\n%s %s %s → %s · up %.2f" % (sym.upper(), ten, t[a], t[b], up))
        for c in cl:
            print("   hộp %.2f–%.2f · đệm dưới %.2f–%.2f (%.2f = %.2f up) · đệm trên %.2f–%.2f (%.2f = %.2f up)"
                  % (c["lo"] * sc, c["hi"] * sc, c["blo"] * sc, c["lo"] * sc, (c["lo"] - c["blo"]) * sc, (c["lo"] - c["blo"]) * sc / up,
                     c["hi"] * sc, c["bhi"] * sc, (c["bhi"] - c["hi"]) * sc, (c["bhi"] - c["hi"]) * sc / up))


def thongke(sym):
    import vung_dem_lib as L
    D, vm, V = L.load(sym)
    for kind, ten in (("d", "ngày"), ("w", "tuần")):
        w, bw = [], []
        for a, b in HC2.H1.spans(D, kind):
            up = HC2.H1.up_of(D, a, b) / 0.1
            cl, _ = prof_buffers(D, a, b, kind)
            for c in cl:
                w += [(c["bhi"] - c["hi"]) / up, (c["lo"] - c["blo"]) / up]
                bw.append((c["hi"] - c["lo"]) / up)
        w = np.array(w)
        cap = int(np.floor(BP["BCAP"] * 1000 + 0.5)) / 1000
        print("%s profile %s: %d hộp · phía có đệm %.0f %% · bề rộng đệm (× up, phía có đệm) p25 / 50 / 75 = %s · chạm trần %.0f %% · hộp có đệm ít nhất một phía %.0f %% · (hộp + 2 đệm) ÷ hộp, trung vị %.2f"
              % (sym.upper(), ten, len(bw), 100 * (w > 0).mean(), np.round(np.percentile(w[w > 0], [25, 50, 75]), 2).tolist(), 100 * (w >= cap - 0.01).mean(),
                 100 * (w.reshape(-1, 2).max(axis=1) > 0).mean(), np.median((w.reshape(-1, 2).sum(axis=1) + np.array(bw)) / np.array(bw))))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "ca": ca(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "thongke": thongke(sys.argv[2])
