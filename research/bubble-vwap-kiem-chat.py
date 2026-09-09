"""Kiem CHAT o duy nhat con nghieng: "xanh dau do dit" TAI VWAP NGAY.

Ba phep kiem doc lap:
  1. So voi nhom DOI CHUNG SAT NHAT: cung tai VWAP, CO bubble nhung KHONG dung hinh.
     (neu hinh khong them gi thi hai nhom bang nhau)
  2. Thay doi ban kinh VWAP (+-1 / +-2 / +-4 gia) — hieu ung that thi phai don dieu.
  3. Bubble o DUNG CUC TRI (muc gia cao/thap nhat) thay vi band 30%.
Chia doi thoi gian o moi phep.
"""
import os, sys, math, csv, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load

BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
BUB = os.path.join(ROOT, "research/bubble_feats.csv")
W, LOOK, HOR, FWD = 50, 20, 60, 30


def two_prop(k1, n1, k2, n2):
    if n1 < 10 or n2 < 10:
        return float("nan")
    p1 = k1 / n1; p2 = k2 / n2; p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (p1 - p2) / se if se > 0 else 0.0


if __name__ == "__main__":
    t, o, h, l, c, v, dl = load(BARS)
    n = len(t)
    K = ("ready", "hvn_g_top", "hvn_r_top", "hvn_g_bot", "hvn_r_bot",
         "imb_g_top", "imb_r_top", "imb_g_bot", "imb_r_bot")
    B = {k: [0] * n for k in K}
    with open(BUB, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f); hd = next(r); ix = {k: i for i, k in enumerate(hd)}
        for row in r:
            b = int(row[0])
            if b < n:
                for k in K:
                    B[k][b] = int(row[ix[k]])
    gt = [B["hvn_g_top"][i] + B["imb_g_top"][i] for i in range(n)]
    rt = [B["hvn_r_top"][i] + B["imb_r_top"][i] for i in range(n)]
    gb = [B["hvn_g_bot"][i] + B["imb_g_bot"][i] for i in range(n)]
    rb = [B["hvn_r_bot"][i] + B["imb_r_bot"][i] for i in range(n)]

    sid = [0] * n; k = 0
    for i in range(1, n):
        if t[i] - t[i - 1] > 30: k += 1
        sid[i] = k
    vwd = [0.0] * n; pv = pvol = 0.0; cur = -1
    for i in range(n):
        if sid[i] != cur: cur = sid[i]; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]
        vwd[i] = pv / pvol if pvol > 0 else c[i]

    half = n // 2
    ev = []      # (half, lab, dist_vwap, shape, anybub)
    last = {-1: -10 ** 9, 1: -10 ** 9}
    for i in range(W + LOOK, n - HOR - 4):
        seg = t[i - W:i + HOR + 4]
        if seg[-1] - seg[0] != len(seg) - 1: continue
        if not B["ready"][i]: continue
        mv = st.median(v[i - W:i]); md = st.median([abs(x) for x in dl[i - W:i]])
        u = st.median([h[j] - l[j] for j in range(i - W, i)])
        if mv <= 0 or md <= 0 or u <= 0: continue
        R = h[i] - l[i]
        if R <= 0 or v[i] < 2.5 * mv: continue
        up = c[i] + 2 * u; dn = c[i] - 2 * u; first = 0
        for j in range(i + 1, min(i + HOR, n - 1)):
            a = h[j] >= up; b = l[j] <= dn
            if a and b: first = 0; break
            if a: first = 1; break
            if b: first = -1; break
        if first == 0: continue
        for side in (-1, 1):
            if side < 0 and dl[i] > -3.0 * md: continue
            if side > 0 and dl[i] < 3.0 * md: continue
            if i - last[side] < FWD: continue
            last[side] = i
            lab = 1 if (first > 0) == (side < 0) else 0
            ref = l[i] if side < 0 else h[i]
            ev.append((0 if i < half else 1, lab, abs(ref - vwd[i]),
                       gt[i] > 0 and rb[i] > 0, gt[i] + rt[i] + gb[i] + rb[i] > 0))

    print("tong su kien: %d\n" % len(ev))
    print("=== 1+2. Doi chung SAT NHAT, theo ban kinh VWAP ngay ===")
    print("  ban kinh | nhom                          | nua dau        | nua sau        | GOP")
    for tol in (1.0, 2.0, 4.0, 1e9):
        nm_tol = "moi khoang" if tol > 1e8 else "+-%.0f gia" % tol
        sub = [e for e in ev if e[2] <= tol]
        grp = {"DUNG HINH xanh dau do dit": [e for e in sub if e[3]],
               "co bubble, KHONG dung hinh": [e for e in sub if e[4] and not e[3]],
               "KHONG co bubble nao": [e for e in sub if not e[4]]}
        for gname in ("DUNG HINH xanh dau do dit", "co bubble, KHONG dung hinh", "KHONG co bubble nao"):
            ds = grp[gname]
            a = [e[1] for e in ds if e[0] == 0]; b = [e[1] for e in ds if e[0] == 1]
            def f(x):
                if len(x) < 25: return "n=%-4d qua it" % len(x)
                return "n=%-4d %5.1f%%" % (len(x), 100.0 * sum(x) / len(x))
            g = a + b
            print("  %-8s | %-30s | %-14s | %-14s | n=%-5d %5.1f%%"
                  % (nm_tol, gname, f(a), f(b), len(g), 100.0 * sum(g) / len(g) if g else 0))
        s = grp["DUNG HINH xanh dau do dit"]; o2 = grp["co bubble, KHONG dung hinh"]
        z = two_prop(sum(e[1] for e in s), len(s), sum(e[1] for e in o2), len(o2))
        print("  %-8s | >>> hinh vs (bubble nhung khac hinh): z = %+5.2f" % (nm_tol, z))
        print()
