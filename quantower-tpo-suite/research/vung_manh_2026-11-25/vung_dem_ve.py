#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vung_dem_ve.py — PNG nến M15 các lần giá quay lại hộp HVN, kèm hộp + vùng đệm đề xuất (VUNG-DEM.md mục 5).
  python vung_dem_ve.py            → vung_dem/*.png
Cần: vung_dem_prep.py, prep1.py gc, vung_dem_events.py nq25|gc.
"""
import os, pickle, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import vung_dem_lib as L
import vung_dem as VD
import vung_dem_events as E

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vung_dem")
INK, MUTED, GRID = "#1f2328", "#6b7280", "#e5e7eb"
UPC, DNC = "#3d8f6e", "#c2554d"
BOX, BUF = "#d9822b", "#d9822b"


def m15(D, i0, i1, sc):
    m = D.m1
    df = pd.DataFrame(dict(t=pd.to_datetime(m["t"][i0:i1]), o=m["o"][i0:i1] * sc, h=m["h"][i0:i1] * sc, l=m["l"][i0:i1] * sc, c=m["c"][i0:i1] * sc))
    g = df.groupby(df.t.dt.floor("15min"))
    return pd.DataFrame(dict(o=g.o.first(), h=g.h.max(), l=g.l.min(), c=g.c.last())).reset_index()


def candles(ax, b):
    for k, r in b.iterrows():
        col = UPC if r.c >= r.o else DNC
        ax.plot([k, k], [r.l, r.h], color=col, lw=0.8, zorder=3)
        ax.add_patch(Rectangle((k - 0.32, min(r.o, r.c)), 0.64, max(abs(r.c - r.o), 1e-9), color=col, zorder=4, lw=0))
    # nhãn trục thời gian: đầu mỗi ngày UTC + mỗi 6 giờ
    step = max(4, len(b) // 10)
    idx = list(range(0, len(b), step))
    ax.set_xticks(idx); ax.set_xticklabels([b.t[i].strftime("%d/%m %H:%M") for i in idx], fontsize=8, color=MUTED)
    ax.set_xlim(-1, len(b) + 12)


def draw(D, sym, lo, hi, blo, bhi, sa, sb, i_from, i_to, title, fn, marks=(), dec=2, note=None, show_src=True):
    sc = L.SCALE[sym]
    b = m15(D, i_from, i_to, sc)
    fig, ax = plt.subplots(figsize=(13, 6.2), dpi=110)
    candles(ax, b)
    n = len(b)
    lo, hi, blo, bhi = lo * sc, hi * sc, blo * sc, bhi * sc
    ax.add_patch(Rectangle((-1, lo), n + 13, hi - lo, color=BOX, alpha=0.30, lw=0, zorder=1))
    if bhi > hi: ax.add_patch(Rectangle((-1, hi), n + 13, bhi - hi, color=BUF, alpha=0.12, lw=0, zorder=1, hatch="////", ec=BUF))
    if blo < lo: ax.add_patch(Rectangle((-1, blo), n + 13, lo - blo, color=BUF, alpha=0.12, lw=0, zorder=1, hatch="////", ec=BUF))
    f = lambda x: (("%%.%df" % dec) % x).replace(".", ",")
    lab = "hộp HVN " + f(lo) + " – " + f(hi)
    if bhi > hi: lab += " · đệm trên tới " + f(bhi)
    if blo < lo: lab += " · đệm dưới tới " + f(blo)
    ax.text(n + 11.5, max(hi, bhi), lab, ha="right", va="bottom", fontsize=8.5, color=INK, zorder=6)
    # phiên nguồn
    if show_src:
        ts, te = pd.Timestamp(D.m30["t"][sa]), pd.Timestamp(D.m30["t"][sb]) + pd.Timedelta(minutes=30)
        ks = b.index[(b.t >= ts) & (b.t < te)]
        if len(ks):
            ax.axvspan(ks[0] - 0.5, ks[-1] + 0.5, color="#9ca3af", alpha=0.10, lw=0, zorder=0)
            ax.text((ks[0] + ks[-1]) / 2, ax.get_ylim()[1], "", ha="center")
    for i_m1, price, txt, above in marks:
        tt = pd.Timestamp(D.m1["t"][i_m1]).floor("15min")
        k = b.index[b.t == tt]
        if not len(k): continue
        k = k[0]
        ax.annotate(txt, xy=(k, price * sc), xytext=(k, price * sc + (1 if above else -1) * 0.09 * (b.h.max() - b.l.min())), ha="center", va="bottom" if above else "top",
                    fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=INK, lw=0.8), zorder=7)
        ax.plot([k], [price * sc], marker="o", ms=6, mfc="white", mec=INK, mew=1.4, zorder=8)
    ax.set_title(title, fontsize=11, color=INK, loc="left")
    if note: ax.text(0.0, -0.11, note, transform=ax.transAxes, fontsize=8.5, color=MUTED, va="top")
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID); ax.tick_params(axis="y", labelsize=8, colors=MUTED, length=0); ax.tick_params(axis="x", length=0)
    ax.yaxis.tick_right()
    fig.tight_layout()
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, fn)); plt.close(fig)
    print("ghi", fn)


def box_buf(D, e):
    """Vùng đệm đề xuất của hộp trong sự kiện e (đơn vị giá của D)."""
    c = dict(name=e["name"], end=int(e["end"]))
    a, b = E.src_span(D, c)
    cl, _ = VD.prof_buffers(D, a, b, "w" if e["name"] == "hvn_w" else "d")
    for q in cl:
        if abs(q["lo"] * 0.1 - e["lo0"]) < 1e-6: return q["blo"] * 0.1, q["bhi"] * 0.1, a, b
    return e["lo0"], e["hi0"], a, b


def ca_nq(D):
    sym = "nq25"; t1 = D.m1["t"]
    ix = lambda s: int(np.searchsorted(t1, np.datetime64(s)))
    k = VD.HC2.H1.find_day(D, "2026-11-20"); a, b = D.days[k]
    cl, _ = VD.prof_buffers(D, a, b, "d"); c = cl[0]
    lo, hi, blo, bhi = c["lo"] * 0.1, c["hi"] * 0.1, c["blo"] * 0.1, c["bhi"] * 0.1
    i_lo25 = ix("2026-11-25T07:30") + int(np.argmin(D.m1["l"][ix("2026-11-25T07:30"):ix("2026-11-25T08:00")]))
    i_lo23 = ix("2026-11-23T02:30") + int(np.argmin(D.m1["l"][ix("2026-11-23T02:30"):ix("2026-11-23T03:00")]))
    marks = [(i_lo23, D.m1["l"][i_lo23], "23/11: đáy %.2f\n(trên mép hộp 1 điểm)" % (D.m1["l"][i_lo23] * 2.5), False),
             (i_lo25, D.m1["l"][i_lo25], "25/11: đáy %.2f\n(trên mép hộp 27,5 điểm,\ntrong vùng đệm)" % (D.m1["l"][i_lo25] * 2.5), False)]
    draw(D, sym, lo, hi, blo, bhi, a, b, ix("2026-11-20T13:00"), len(t1), "NQZ26 M15 · hộp HVN phiên 20/11 và vùng đệm đề xuất · 20/11 → 25/11 08:47 UTC (nền xám = phiên nguồn)",
         "nq_2026-11-20_den_11-25_m15.png", marks, note="Hộp cam = hộp HVN v2 đang vẽ. Gạch chéo nhạt = vùng đệm đề xuất (sườn cụm còn ≥ 50 % đỉnh). Giờ UTC.")
    draw(D, sym, lo, hi, blo, bhi, a, b, ix("2026-11-20T16:00"), ix("2026-11-20T20:00"), "NQZ26 M15 · phiên nguồn 20/11 16:00–20:00 UTC · các nến rút râu trên quanh mép trên của hộp",
         "nq_2026-11-20_phien_nguon_m15.png", (), note="Vùng đệm trên 25609,75 – 25652,25. Đầu râu M30 của các nến có thân chạm hộp: 25648,75 · 25653,25 · 25656,50 · 25721,50 · 25762,50.", show_src=False)
    draw(D, sym, lo, hi, blo, bhi, a, b, ix("2026-11-24T23:00"), len(t1), "NQZ26 M15 · 25/11 · giá đảo ở 25637,25 trong vùng đệm, chưa chạm hộp",
         "nq_2026-11-25_dao_trong_vung_dem_m15.png", marks[1:], note="Đáy 25637,25 lúc 07:30–07:45 UTC, bật lên 25915,00.", show_src=False)
    profile_png(D, a, b, c)


def profile_png(D, a, b, c):
    S, t0, up = E.profile_S(D, a, b)
    sc = 0.25
    px = (t0 + np.arange(len(S))) * sc
    P = S[c["peak"] - t0]
    m = (px >= 25440) & (px <= 25820)
    fig, ax = plt.subplots(figsize=(7.5, 6.2), dpi=110)
    ax.fill_betweenx(px[m], 0, 100 * S[m] / P, color="#9ca3af", alpha=0.55, lw=0)
    ax.axhspan(c["lo"] * sc, c["hi"] * sc, color=BOX, alpha=0.30, lw=0)
    ax.axhspan(c["hi"] * sc, c["bhi"] * sc, color=BUF, alpha=0.12, lw=0, hatch="////", ec=BUF)
    ax.axvline(50, color=INK, lw=0.9, ls=(0, (4, 3)))
    ax.text(51, 25448, "50 % đỉnh", fontsize=8.5, color=INK)
    ax.text(101, (c["lo"] + c["hi"]) / 2 * sc, "hộp HVN 25538,50 – 25609,75", fontsize=8.5, color=INK, va="center", ha="right")
    ax.text(101, (c["hi"] + c["bhi"]) / 2 * sc, "vùng đệm tới 25652,25", fontsize=8.5, color=INK, va="center", ha="right")
    ax.axhline(25637.25, color=INK, lw=1.0); ax.text(2, 25639, "đáy 25/11: 25637,25", fontsize=8.5, color=INK, va="bottom")
    ax.set_xlabel("khối lượng mượt, % so với đỉnh cụm", fontsize=9, color=MUTED); ax.set_xlim(0, 104)
    ax.set_title("NQZ26 · profile phiên 20/11 quanh cụm 25583", fontsize=11, color=INK, loc="left")
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(GRID)
    ax.tick_params(labelsize=8, colors=MUTED, length=0)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "nq_2026-11-20_profile_vung_dem.png")); plt.close(fig)
    print("ghi nq_2026-11-20_profile_vung_dem.png")


def tieu_bieu(D, sym, n_each=2):
    """Chọn tự động (không lựa bằng mắt): mỗi loại kết cục lấy n_each lần quay lại GẦN NHẤT của hộp thật có vùng đệm phía tiếp cận."""
    ev = [e for e in pickle.load(open(E.out_path(sym), "rb")) if e["typ"] == "that" and e["done1"] and e["fin"] > 0]
    ev.sort(key=lambda e: -e["i0"])
    sc = L.SCALE[sym]; dec = 2 if sc != 1 else 1
    kinds = (("dao_trong_dem", "đảo trong vùng đệm", lambda e: -e["fin"] / e["u"] <= e["depth1"] < 0),
             ("dao_truoc_dem", "đảo trước khi tới vùng đệm", lambda e: e["depth1"] < -e["fin"] / e["u"]),
             ("dao_trong_hop", "đảo trong hộp", lambda e: 0 <= e["depth1"] <= (e["hi"] - e["lo"]) / e["u"]),
             ("xuyen", "xuyên qua hộp", lambda e: e["depth1"] > (e["hi"] - e["lo"]) / e["u"]))
    used = set()
    for tag, ten, f in kinds:
        k = 0
        for e in ev:
            key = (e["name"], e["end"], round(e["lo0"], 3))
            if not f(e) or key in used: continue
            if sym == "nq25" and abs(e["lo0"] * sc - 25538.5) < 1: continue      # ca người dùng đã có ảnh riêng
            used.add(key); k += 1
            blo, bhi, a, b = box_buf(D, e)
            i0, iE = int(e["i0"]), int(e["iE1"])
            tday = str(pd.Timestamp(D.m1["t"][i0]))[:10]
            draw(D, sym, e["lo0"], e["hi0"], blo, bhi, a, b, max(0, i0 - 600), min(len(D.m1["t"]), iE + 480),
                 "%s M15 · %s · %s · tiếp cận %s (%s)" % ("NQZ26" if sc != 1 else "GCZ26", tday, ten, "từ trên xuống" if e["side"] > 0 else "từ dưới lên", "HVN ngày" if e["name"] == "hvn_d" else "HVN tuần"),
                 "%s_%s_%s_%d.png" % (sym[:2], tday, tag, k),
                 [(iE, e["ext1"], "điểm đảo %s" % (("%%.%df" % dec) % (e["ext1"] * sc)), e["side"] < 0)], dec=dec,
                 note="Điểm đảo = cực trị trước khi giá bật ngược ≥ 1 U (U = %s). Chọn tự động: lần gần nhất của mỗi loại kết cục." % (("%%.%df" % dec) % (e["u"] * sc)), show_src=False)
            if k >= n_each: break


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    D, vm, V = L.load("nq25")
    ca_nq(D); tieu_bieu(D, "nq25", 1)
    D, vm, V = L.load("gc")
    tieu_bieu(D, "gc", 1)
