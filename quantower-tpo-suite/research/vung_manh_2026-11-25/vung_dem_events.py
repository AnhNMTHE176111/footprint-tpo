#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vung_dem_events.py — sinh MỌI lần giá quay lại hộp HVN v2 (PLAN mục 13) + đặc trưng "vùng đệm" của hộp (VUNG-DEM.md).

  python vung_dem_events.py gc|nq25      → <thư mục đệm>/vung_dem_ev_<sym>.pkl

Hộp: vung_manh.day_levels(HVN_MODE="cum2") của từng phiên; trong một phiên, hộp trùng > 50 % chỉ giữ một (như HvnBoxes).
Lần quay lại (trên nến M1, chỉ để CHẤM): giá vào "dải tiếp cận" = hộp nới TRIG × U mỗi phía, sau khi đã rời mép hộp
>= AWAY × U (lần đầu, tính từ lúc profile chốt = điều kiện "rời xa" của indicator) hoặc >= REARM × U (các lần sau).
Phía tiếp cận = phía giá đứng trước khi vào dải. Điểm đảo = cực trị chạy (đáy nếu tới từ trên) tại lúc giá bật ngược
>= BOUNCE × U lần đầu. depth = (mép gần − điểm đảo) theo hướng đi tới, đơn vị U: âm = đảo TRƯỚC khi chạm mép.
Đối chứng: cùng hộp dời ± 1,5–4 U (3 lần mỗi hộp, cố định theo khoá hộp), mọi thứ khác y hệt.
"""
import os, pickle, sys, zlib, tempfile
import numpy as np
import vung_dem_lib as L
import hvn_cum2 as HC2
import vung_dem as VD

TRIG, AWAY, REARM, N_SHIFT, HORIZON = 0.5, 2.0, 2.0, 3, 4000
BOUNCES = (0.5, 1.0, 1.5)


def out_path(sym):
    return os.path.join(os.environ.get("VM_CACHE_DIR", tempfile.gettempdir()), "vung_dem_ev_%s.pkl" % sym)


def box_list(D, V, p):
    """{khoá: dict(box, days=set)} — khoá = (name, end, lo, hi)."""
    out = {}
    for d in range(len(D.days)):
        a0 = D.days[d][0]
        if not np.isfinite(D.U[a0]): continue
        lv = [x for x in V.day_levels(D, d, p) if x["name"].startswith("hvn")]
        keep = []
        for c in sorted(lv, key=lambda x: (-x["end"], 0 if x["name"] == "hvn_d" else 1, -x["ratio"], x["lo"])):
            dup = False
            for k in keep:
                inter = min(k["hi"], c["hi"]) - max(k["lo"], c["lo"]); small = min(k["hi"] - k["lo"], c["hi"] - c["lo"])
                if inter > 0 and inter > 0.5 * small:
                    dup = True
                    if k["name"] != c["name"]: k["both"] = True
            if not dup: keep.append(dict(c))
        for c in keep:
            key = (c["name"], c["end"], c["lo"], c["hi"])
            if key not in out: out[key] = dict(box=c, days=set(), both=False)
            out[key]["days"].add(d); out[key]["both"] |= bool(c.get("both"))
    return out


def src_span(D, c):
    """Nến M30 [a..b] của profile nguồn."""
    b = c["end"]
    if c["name"] == "hvn_d": return D.days[int(D.day_of[b])][0], b
    last_sp = max([s for s in D.splices if s <= b], default=0)
    return max(D.weeks[int(D.week_of[b])][0], last_sp), b


def profile_S(D, a, b):
    """Khối lượng mượt S của profile [a..b] đúng như hvn_cum2.clusters. Trả (S, t0, up)."""
    m = D.m30
    up = float((m["h"][a:b + 1] - m["l"][a:b + 1]).mean())
    tk, v = D.ticks_over(a, b)
    t0 = int(tk[0]); n = int(tk[-1]) - t0 + 1
    w = np.zeros(n); w[tk - t0] = v
    hh = max(1, int(np.floor(HC2.HP2["SM"] * up / 0.1 + 0.5)))
    return HC2.H1.smooth_sum(w, hh), t0, up


def features(D, c):
    """Đặc trưng vùng đệm của hộp, mỗi phía (+1 = phía TRÊN hộp, −1 = phía DƯỚI). Bề rộng tính bằng đơn vị giá của D."""
    a, b = src_span(D, c)
    m = D.m30
    o, h, l, cl = m["o"][a:b + 1], m["h"][a:b + 1], m["l"][a:b + 1], m["c"][a:b + 1]
    lo, hi = c["lo"], c["hi"]
    S, t0, up = profile_S(D, a, b)
    n = len(S)
    ilo, ihi, ipk = int(round(lo / 0.1)) - t0, int(round(hi / 0.1)) - t0, int(round(c["peak"] / 0.1)) - t0
    P = S[ipk]
    bmin, bmax = np.minimum(o, cl), np.maximum(o, cl)
    f = dict(up=up, a=a, b=b)
    # số nến M30 phủ từng bước giá (TPO)
    tp = np.zeros(n + 1)
    li = np.clip(np.round(l / 0.1).astype(int) - t0, 0, n - 1); hi_i = np.clip(np.round(h / 0.1).astype(int) - t0, 0, n - 1)
    np.add.at(tp, li, 1); np.add.at(tp, hi_i + 1, -1); tp = np.cumsum(tp)[:n]
    tp_box = tp[ilo:ihi + 1].max()
    for s in (1, -1):
        e = {}
        # (1) râu M30: nến có THÂN chạm hộp (w) / ĐÓNG trong hộp (w2) và râu nhô khỏi mép
        if s > 0:
            body = (bmin <= hi) & (bmax >= lo) & (h > hi); tips = (h - hi)[body]
            cin = (cl >= lo) & (cl <= hi) & (h > hi); tips2 = (h - hi)[cin]
        else:
            body = (bmin <= hi) & (bmax >= lo) & (l < lo); tips = (lo - l)[body]
            cin = (cl >= lo) & (cl <= hi) & (l < lo); tips2 = (lo - l)[cin]
        e["n_tip"] = int(len(tips)); e["n_tip2"] = int(len(tips2))
        for nm, tt in (("w", tips), ("w2", tips2)):
            for q in (25, 50, 75):
                e["%s_p%d" % (nm, q)] = float(np.percentile(tt, q)) if len(tt) >= 2 else 0.0
        # (2) sườn profile: nới từ mép ra ngoài khi S >= f × đỉnh
        for fr in (0.3, 0.35, 0.4, 0.45, 0.5):
            i = ihi if s > 0 else ilo
            while 0 <= i + s < n and S[i + s] >= fr * P: i += s
            e["pf%d" % int(round(fr * 100))] = abs(i - (ihi if s > 0 else ilo)) * 0.1
        # (2b) ĐỀ XUẤT (vung_dem.add_buffers): sườn >= 50 % đỉnh, trần 0,45 up, hẹp hơn 0,05 up thì không có
        cap = max(1, int(np.floor(VD.BP["BCAP"] * up / 0.1 + 0.5))); i = ihi if s > 0 else ilo; i_edge = i
        while 0 <= i + s < n and abs(i - i_edge) < cap and S[i + s] >= VD.BP["BF"] * P: i += s
        e["fin"] = abs(i - i_edge) * 0.1 if abs(i - i_edge) >= VD.BP["BMIN"] * up / 0.1 else 0.0
        # (3) TPO: nới khi số nến M30 phủ >= th × số nến phủ lớn nhất trong hộp
        for th in (0.5, 0.67):
            i = ihi if s > 0 else ilo
            while 0 <= i + s < n and tp[i + s] >= th * tp_box: i += s
            e["tpo%d" % int(th * 100)] = abs(i - (ihi if s > 0 else ilo)) * 0.1
        f[s] = e
    return f


def turn(D, i, side, u, B, lo, hi):
    """Điểm đảo: cực trị chạy tại lúc giá bật ngược >= B × u lần đầu (M1)."""
    m1 = D.m1; H, Lw, C = m1["h"], m1["l"], m1["c"]
    N = len(H)
    ext = Lw[i] if side > 0 else H[i]; iE = i; done = False
    for k in range(i, min(N, i + HORIZON)):
        if side > 0:
            if Lw[k] < ext: ext, iE = Lw[k], k
            if (H[k] - ext >= B * u and k > iE) or (k == iE and C[k] - ext >= B * u): done = True; break
        else:
            if H[k] > ext: ext, iE = H[k], k
            if (ext - Lw[k] >= B * u and k > iE) or (k == iE and ext - C[k] >= B * u): done = True; break
    return ext, iE, done


def scan(D, lo, hi, end, days, bounces=BOUNCES):
    """Máy trạng thái trên M1. Trả list dict(i0, side, depth{B}, iE{B}, done{B})."""
    m1 = D.m1; H, Lw = m1["h"], m1["l"]; i30 = m1["i30"]
    s0 = int(D.m1_ptr[end + 1]); dmax = max(days)
    s1 = int(D.m1_ptr[D.days[dmax][1] + 1])
    U = D.U[i30]; dayof = D.day_of[i30]
    ev = []
    state, away, need = 0, 0.0, AWAY        # state 0 = đang trong dải; ±1 = trên / dưới
    for i in range(s0, s1):
        u = U[i]
        if not np.isfinite(u): continue
        zl, zh = lo - TRIG * u, hi + TRIG * u
        if Lw[i] > zh:
            if state != 1: state, away = 1, 0.0
            away = max(away, (H[i] - hi) / u)
        elif H[i] < zl:
            if state != -1: state, away = -1, 0.0
            away = max(away, (lo - Lw[i]) / u)
        else:
            if state != 0 and away >= need and int(dayof[i]) in days:
                side = state
                e = dict(i0=i, side=side, u=u, away=away, first=(need == AWAY))
                for B in bounces:
                    ext, iE, done = turn(D, i, side, u, B, lo, hi)
                    e["depth%g" % B] = ((hi - ext) if side > 0 else (ext - lo)) / u
                    e["iE%g" % B] = iE; e["done%g" % B] = done; e["ext%g" % B] = ext
                ev.append(e)
            if state != 0: need = REARM
            state, away = 0, 0.0
    return ev


def dedupe(ev):
    """Hai sự kiện cùng loại (thật / dời cùng rep), cùng phía, cùng điểm đảo, hộp trùng > 50 % ⇒ giữ sự kiện vào dải sớm hơn
    (hoà: hộp ngày trước hộp tuần)."""
    ev = sorted(ev, key=lambda e: (e["i0"], 0 if e["name"] == "hvn_d" else 1, -e["end"]))
    keep = []
    for e in ev:
        dup = False
        for k in keep[-60:]:
            if k["typ"] != e["typ"] or k["rep"] != e["rep"] or k["side"] != e["side"] or k["iE1"] != e["iE1"]: continue
            inter = min(k["hi"], e["hi"]) - max(k["lo"], e["lo"]); small = min(k["hi"] - k["lo"], e["hi"] - e["lo"])
            if inter > 0.5 * small: dup = True; break
        if not dup: keep.append(e)
    return keep


def main(sym):
    D, vm, V = L.load(sym)
    p = dict(V.P, HVN_MODE="cum2")
    boxes = box_list(D, V, p)
    print(sym, "hộp (khoá khác nhau):", len(boxes), flush=True)
    out = []
    for n, (key, bx) in enumerate(sorted(boxes.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2]))):
        c = bx["box"]; ft = features(D, c)
        variants = [("that", 0.0, -1)]
        u_ref = D.U[min(c["end"] + 1, D.n - 1)]
        for rep in range(N_SHIFT):
            rs = np.random.RandomState(zlib.crc32(("%s_%d_%.3f_%d" % (key[0], key[1], key[2], rep)).encode()) & 0x7fffffff)
            variants.append(("doi", float(rs.choice([-1, 1]) * rs.uniform(1.5, 4.0) * u_ref), rep))
        for typ, dl, rep in variants:
            for e in scan(D, c["lo"] + dl, c["hi"] + dl, c["end"], bx["days"]):
                e.update(typ=typ, rep=rep, name=c["name"], src=c["src"], end=c["end"], lo=c["lo"] + dl, hi=c["hi"] + dl, lo0=c["lo"], hi0=c["hi"], peak=c["peak"],
                         mass=c["ratio"], bars=c.get("bars", np.nan), con=c.get("con", np.nan), both=bx["both"], up=ft["up"], sa=ft["a"], sb=ft["b"])
                for k, v in ft[e["side"]].items(): e[k] = v          # đặc trưng PHÍA TIẾP CẬN
                for k, v in ft[-e["side"]].items(): e["far_" + k] = v
                e["t0"] = D.m1["t"][e["i0"]]
                out.append(e)
    out = dedupe(out)
    with open(out_path(sym), "wb") as f: pickle.dump(out, f, protocol=4)
    nt = sum(1 for e in out if e["typ"] == "that")
    print("lưu", out_path(sym), "thật", nt, "dời", len(out) - nt)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1])
