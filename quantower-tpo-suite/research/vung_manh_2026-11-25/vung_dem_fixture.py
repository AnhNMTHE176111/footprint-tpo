#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vung_dem_fixture.py — dữ liệu đối chiếu C# = Python cho VÙNG ĐỆM của hộp HVN (PLAN-VUNG-MANH.md mục 14).
  python vung_dem_fixture.py      (cần: python vung_dem_prep.py)

Ghi vào fixture/ (không đụng file đã có):
  vung_dem_cases.json       mức HÀM: với từng profile của hvn_cum2_cases.json (cùng thứ tự, cùng `ten`) → hộp + buf_lo, buf_hi.
                            Đọc `levels`, `up`, `tick`, `so_nen_m30`, `mass_min` từ hvn_cum2_cases.json; file này chỉ chứa kỳ vọng.
  nq25_m30_bars.csv         NQZ26 giá thật, nến M30 từ 2026-11-08 tới 2026-11-25 08:30 UTC (nến cuối chưa đóng)
  nq25_m30_levels.csv.gz    khối lượng từng mức giá của các nến đó
  nq25_expected.json        mức CẢ BỘ MÁY (bộ chặn chỗ nối TẮT): mọi nến đóng từ 2026-11-24 23:00 UTC; `hvn` có buf_lo/buf_hi (cả hai phía),
                            `hvn_boxes` có buf_lo/buf_hi ĐƯỢC VẼ (chỉ phía giá đang đứng).
"""
import gzip, json, os, sys
import numpy as np
import pandas as pd
import vung_dem_lib as L
import vung_dem as VD
import hvn_cum2 as H2

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "fixture")
SC, TK = 2.5, 0.25
T_FROM = np.datetime64("2026-11-08T00:00")
T_CASE = np.datetime64("2026-11-24T23:00")


def func_cases():
    src = json.load(open(os.path.join(FX, "hvn_cum2_cases.json"), encoding="utf-8"))
    out = []
    for c in src["cases"]:
        tick = c["tick"]; dec = 2 if tick == 0.25 else 1
        tk = np.array([int(round(p / tick)) for p, _ in c["levels"]], np.int64); v = np.array([q for _, q in c["levels"]], float)
        up_ticks = c["up"] / tick
        cl, ex = H2.clusters(tk, v, up_ticks, c["so_nen_m30"], H2.HP2, c["mass_min"])
        r = lambda x: round(int(x) * tick, dec)
        assert [(r(q["lo"]), r(q["hi"])) for q in cl] == [(q["lo"], q["hi"]) for q in c["clusters"]], c["ten"]
        VD.add_buffers(cl, ex, up_ticks)
        cap = max(1, int(np.floor(VD.BP["BCAP"] * up_ticks + 0.5)))
        out.append(dict(ten=c["ten"], cap=cap, min_ticks=round(VD.BP["BMIN"] * up_ticks, 6),
                        clusters=[dict(lo=r(q["lo"]), hi=r(q["hi"]), peak=r(q["peak"]), buf_lo=r(q["blo"]), buf_hi=r(q["bhi"])) for q in cl]))
        print("| %s | %d | %s |" % (c["ten"], cap, " ; ".join("%s – %s → đệm dưới tới %s · đệm trên tới %s" % (q["lo"], q["hi"], q["buf_lo"] if q["buf_lo"] != q["lo"] else "—", q["buf_hi"] if q["buf_hi"] != q["hi"] else "—") for q in out[-1]["clusters"]) or "không có hộp"))
    with open(os.path.join(FX, "vung_dem_cases.json"), "w", encoding="utf-8") as f:
        json.dump(dict(ghi_chu="PLAN-VUNG-MANH.md mục 14. Cùng thứ tự ca với hvn_cum2_cases.json (đọc levels/up/tick ở đó). buf_lo = lo / buf_hi = hi nghĩa là phía đó không có vùng đệm. cap = trần (số bước giá).",
                       params=VD.BP, cases=out), f, ensure_ascii=False, indent=0)


def engine_nq25():
    D0, vm, V = L.load("nq25")
    t = D0.m30["t"]
    s0 = int(np.searchsorted(t, T_FROM)); n = D0.n
    with open(os.path.join(FX, "nq25_m30_bars.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("idx,time_utc,open,high,low,close,volume\n")
        for i in range(s0, n):
            f.write("%d,%s,%.2f,%.2f,%.2f,%.2f,%.1f\n" % (i - s0, str(pd.Timestamp(t[i]))[:19], D0.m30["o"][i] * SC, D0.m30["h"][i] * SC, D0.m30["l"][i] * SC, D0.m30["c"][i] * SC, D0.m30["v"][i]))
    idx, tick, vol = [], [], []
    with gzip.open(os.path.join(FX, "nq25_m30_levels.csv.gz"), "wt", encoding="utf-8", newline="\n") as f:
        f.write("idx,price,volume\n")
        for i in range(s0, n):
            a, b = D0.lv_ptr[i], D0.lv_ptr[i + 1]
            for k, v in zip(D0.lv_tick[a:b], D0.lv_vol[a:b]):
                f.write("%d,%.2f,%d\n" % (i - s0, int(k) * TK, int(round(float(v)))))
                idx.append(i - s0); tick.append(int(k)); vol.append(float(v))
    # bộ máy chạy trên ĐÚNG dữ liệu fixture (cắt từ T_FROM) — như C# sẽ thấy
    d = dict(m1=None, m30={k: D0.m30[k][s0:].copy() for k in ("t", "o", "h", "l", "c", "v")},
             lv=(np.array(idx, np.int32), np.array(tick, np.int32), np.array(vol, np.float32)))
    D = vm.Data(d=d)
    p = dict(V.P, HVN_MODE="cum2")
    eng = V.Engine(D, p); eng0 = V.Engine(D0, p)
    cases = []
    for j in range(D.n - 1):
        if D.m30["t"][j] < T_CASE: continue
        zs = eng.zones(j); now = float(D.m30["c"][j]); u = D.U[j + 1]
        shown = V.display(D, zs, j, now, p)
        lv = eng.levels(int(D.day_of[j + 1]))
        # kiểm: dữ liệu cắt cho đúng kết quả của dữ liệu đầy đủ
        z0 = V.display(D0, eng0.zones(j + s0), j + s0, now, p)
        assert [(z["lo"], z["hi"], z["label"]) for z in shown] == [(z["lo"], z["hi"], z["label"]) for z in z0], "dữ liệu cắt lệch dữ liệu đầy đủ ở j=%d" % j
        assert abs(u - D0.U[j + s0 + 1]) < 1e-12
        cases.append(dict(j=j, time_utc=str(pd.Timestamp(D.m30["t"][j])), now=round(now * SC, 2), U=float(u) * SC,
                          hvn=[dict(name=x["name"], lo=round(x["lo"] * SC, 2), hi=round(x["hi"] * SC, 2), peak=round(x["peak"] * SC, 2), mass=round(float(x["ratio"]), 6), src=int(x["src"]),
                                    ok=bool(V.hvn_ok(D, x, j, u, p)), buf_lo=round(x["blo"] * SC, 2), buf_hi=round(x["bhi"] * SC, 2)) for x in lv if "peak" in x],
                          shown=[dict(lo=round(float(z["lo"]) * SC, 2), hi=round(float(z["hi"]) * SC, 2), side=int(z["side"]), color=z["color"], label=z["label"]) for z in shown],
                          hvn_boxes=[dict(name=c["name"], lo=round(c["lo"] * SC, 2), hi=round(c["hi"] * SC, 2), peak=round(c["peak"] * SC, 2), mass=round(float(c["mass"]), 6), label=c["label"],
                                          buf_lo=round(c["buf_lo"] * SC, 2), buf_hi=round(c["buf_hi"] * SC, 2)) for c in V.hvn_boxes(D, lv, j, now, p)]))
    with open(os.path.join(FX, "nq25_expected.json"), "w", encoding="utf-8") as f:
        json.dump(dict(ghi_chu="NQZ26 giá thật tới 2026-11-25 08:30 UTC; Python chạy trên giá chia 2,5 rồi nhân lại. Bộ chặn chỗ nối TẮT (splice_jump = 0). HVN v2 + vùng đệm (PLAN mục 14). hvn[].buf_* = vùng đệm cả hai phía; hvn_boxes[].buf_* = phần ĐƯỢC VẼ.",
                       tick=TK, splice_jump=0.0, params=dict(VD.BP), cases=cases), f, ensure_ascii=False, indent=0)
    print("\nnq25: nến M30 %d (%s → %s) · %d ca" % (D.n, str(pd.Timestamp(D.m30["t"][0])), str(pd.Timestamp(D.m30["t"][-1])), len(cases)))
    for c in cases:
        if c["time_utc"][11:16] in ("07:00", "07:30", "08:00"):
            print(c["time_utc"], "giá", c["now"], "U", round(c["U"], 3))
            for h in c["hvn"]: print("   HVN", h["name"], h["lo"], h["hi"], "đệm", h["buf_lo"], h["buf_hi"], "ok" if h["ok"] else "chưa rời xa")
            for s_ in c["shown"]: print("   VẼ", s_["lo"], s_["hi"], s_["color"], s_["label"])
            for s_ in c["hvn_boxes"]: print("   HỘP", s_["lo"], s_["hi"], s_["label"], "· đệm vẽ", s_["buf_lo"], s_["buf_hi"])


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    func_cases()
    engine_nq25()
