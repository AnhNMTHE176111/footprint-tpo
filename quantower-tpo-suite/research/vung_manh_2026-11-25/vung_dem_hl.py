#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vung_dem_hl.py — nếu luật hợp lưu của vùng mạnh tính cả VÙNG ĐỆM (hộp HVN nới ra tới mép đệm) thì mật độ đổi thế nào
(VUNG-DEM.md mục 6). Điều kiện "rời xa" vẫn đo từ mép HỘP.
  python vung_dem_hl.py gc|nq25
"""
import sys
import numpy as np
import vung_dem_lib as L
import vung_dem as VD
import vung_dem_events as E


def run(sym):
    D, vm, V = L.load(sym)
    base_levels = V.day_levels
    base_ok = V.hvn_ok

    def ok(D_, Lv, j, u, p):
        if "lo0" in Lv: Lv = dict(Lv, lo=Lv["lo0"], hi=Lv["hi0"])
        return base_ok(D_, Lv, j, u, p)

    def levels_buf(D_, d, p):
        out = []
        for x in base_levels(D_, d, p):
            if x["name"].startswith("hvn"):
                a, b = E.src_span(D_, x)
                cl, _ = VD.prof_buffers(D_, a, b, "w" if x["name"] == "hvn_w" else "d")
                for c in cl:
                    if abs(c["peak"] * 0.1 - x["peak"]) < 1e-6:
                        x = dict(x, lo0=x["lo"], hi0=x["hi"], lo=round(c["blo"] * 0.1, 6), hi=round(c["bhi"] * 0.1, 6))
            out.append(x)
        return out

    V.hvn_ok = ok
    print("\n## %s" % sym.upper())
    print("| Luật hợp lưu HVN | % cụm va đập có hợp lưu | % cụm có HVN | vùng vẽ TB | % thời gian có vùng dính HVN | % thời gian có vàng |")
    print("|---|---|---|---|---|---|")
    for ten, fn in (("chỉ hộp (hiện tại)", base_levels), ("hộp + vùng đệm", levels_buf)):
        V.day_levels = fn
        p = dict(V.P, HVN_MODE="cum2"); eng = V.Engine(D, p)
        rows = []
        for j in range(D.n - 1):
            u = D.U[j + 1]
            if not np.isfinite(u) or D.seg_of[j] != D.seg_of[j + 1]: continue
            zs = eng.zones(j)
            sh = V.display(D, zs, j, float(D.m30["c"][j]), p)
            rows.append((len(zs), sum(z["ngroup"] >= 1 for z in zs), sum(z["hvn"] for z in zs), len(sh), sum(z["gold"] for z in sh), sum(z["hvn"] for z in sh)))
        a = np.array(rows, float)
        print("| %s | %.0f | %.0f | %.2f | %.0f | %.1f |" % (ten, 100 * a[:, 1].sum() / a[:, 0].sum(), 100 * a[:, 2].sum() / a[:, 0].sum(), a[:, 3].mean(),
                                                      100 * (a[:, 5] >= 1).mean(), 100 * (a[:, 4] >= 1).mean()))
    V.day_levels = base_levels; V.hvn_ok = base_ok


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    run(sys.argv[1])
