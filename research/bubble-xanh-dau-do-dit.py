"""COMBO + "xanh dau do dit" theo dung dinh nghia BUBBLE cua indicator.

Bubble = HVN cell HOAC stacked imbalance (nguon thu 3 - lenh don - khong co du lieu).
Hinh CORVEN: bubble XANH trong band 30% TREN  VA  bubble DO trong band 30% DUOI.

Thuoc do: rao chan doi xung +-2u tu gia dong nen su kien, 60 nen, ben nao cham truoc.
Nen ngau nhien = 50%. Chia doi thoi gian (nua dau / nua sau).
"""
import os, sys, math, csv, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load

BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
BUB = os.path.join(ROOT, "research/bubble_feats.csv")
W, LOOK, HOR, FWD = 50, 20, 60, 30


def zsc(p, p0, n):
    return (p - p0) / math.sqrt(p0 * (1 - p0) / n) if n > 0 else 0.0


if __name__ == "__main__":
    t, o, h, l, c, v, dl = load(BARS)
    n = len(t)
    K = ("ready", "hvn_g_top", "hvn_r_top", "hvn_g_bot", "hvn_r_bot",
         "imb_g_top", "imb_r_top", "imb_g_bot", "imb_r_bot")
    B = {k: [0] * n for k in K}
    with open(BUB, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        hd = next(r)
        ix = {k: i for i, k in enumerate(hd)}
        for row in r:
            b = int(row[0])
            if b < n:
                for k in K:
                    B[k][b] = int(row[ix[k]])
    gt = [B["hvn_g_top"][i] + B["imb_g_top"][i] for i in range(n)]
    rt = [B["hvn_r_top"][i] + B["imb_r_top"][i] for i in range(n)]
    gb = [B["hvn_g_bot"][i] + B["imb_g_bot"][i] for i in range(n)]
    rb = [B["hvn_r_bot"][i] + B["imb_r_bot"][i] for i in range(n)]
    print("nen %d | co nen chuan %d" % (n, sum(B["ready"])), flush=True)
    print("tan suat co bubble bat ky: %.1f%%" % (100.0 * sum(1 for i in range(n) if gt[i]+rt[i]+gb[i]+rb[i] > 0) / n))

    SHAPES = [
        ("XANH dau + DO dit  (CORVEN)", lambda i: gt[i] > 0 and rb[i] > 0),
        ("  - chi nguon HVN cell", lambda i: B["hvn_g_top"][i] > 0 and B["hvn_r_bot"][i] > 0),
        ("  - chi nguon stacked imbalance", lambda i: B["imb_g_top"][i] > 0 and B["imb_r_bot"][i] > 0),
        ("DO dau + XANH dit (doi chung)", lambda i: rt[i] > 0 and gb[i] > 0),
        ("co bubble bat ky (doi chung)", lambda i: gt[i] + rt[i] + gb[i] + rb[i] > 0),
        ("KHONG co bubble nao (doi chung)", lambda i: gt[i] + rt[i] + gb[i] + rb[i] == 0),
    ]

    sid = [0] * n
    k = 0
    for i in range(1, n):
        if t[i] - t[i - 1] > 30:
            k += 1
        sid[i] = k
    vwd = [0.0] * n
    pv = pvol = 0.0
    cur = -1
    for i in range(n):
        if sid[i] != cur:
            cur = sid[i]; pv = pvol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3.0
        pv += tp * v[i]; pvol += v[i]
        vwd[i] = pv / pvol if pvol > 0 else c[i]

    half = n // 2
    res = defaultdict(lambda: ([], []))
    cnt = defaultdict(lambda: [0, 0])
    lastS = -10 ** 9
    lastV = {-1: -10 ** 9, 1: -10 ** 9}

    for i in range(W + LOOK, n - HOR - 4):
        seg = t[i - W:i + HOR + 4]
        if seg[-1] - seg[0] != len(seg) - 1:
            continue
        if not B["ready"][i]:
            continue
        mv = st.median(v[i - W:i]); md = st.median([abs(x) for x in dl[i - W:i]])
        u = st.median([h[j] - l[j] for j in range(i - W, i)])
        if mv <= 0 or md <= 0 or u <= 0:
            continue
        R = h[i] - l[i]
        if R <= 0:
            continue
        up = c[i] + 2 * u; dn = c[i] - 2 * u; first = 0
        for j in range(i + 1, min(i + HOR, n - 1)):
            a = h[j] >= up; b = l[j] <= dn
            if a and b: first = 0; break
            if a: first = 1; break
            if b: first = -1; break
        if first == 0:
            continue
        hf = 0 if i < half else 1
        if i - lastS >= FWD:
            lastS = i
            for nm, fn in SHAPES:
                ok = fn(i)
                cnt[("S", nm)][0] += ok; cnt[("S", nm)][1] += 1
                if ok:
                    res[("S", nm)][hf].append(1 if first > 0 else 0)
        if v[i] < 2.5 * mv:
            continue
        for side in (-1, 1):
            if side < 0 and dl[i] > -3.0 * md: continue
            if side > 0 and dl[i] < 3.0 * md: continue
            if i - lastV[side] < FWD: continue
            lastV[side] = i
            lab = 1 if (first > 0) == (side < 0) else 0
            newext = (l[i] <= min(l[i - LOOK:i])) if side < 0 else (h[i] >= max(h[i - LOOK:i]))
            inner = (c[i] >= l[i] + 0.5 * R) if side < 0 else (c[i] <= h[i] - 0.5 * R)
            famB = (not newext) and R <= u and inner
            ref = l[i] if side < 0 else h[i]
            atv = abs(ref - vwd[i]) <= 2.0
            taps = ["V"]
            if famB: taps.append("B")
            if atv: taps.append("VW")
            if famB and atv: taps.append("BVW")
            for tp2 in taps:
                for nm, fn in SHAPES:
                    ok = fn(i)
                    cnt[(tp2, nm)][0] += ok; cnt[(tp2, nm)][1] += 1
                    if ok:
                        res[(tp2, nm)][hf].append(lab)

    TAPS = [("S", "MOI NEN (nhan = gia LEN 2u truoc)"),
            ("V", "CUM VOL LON + DELTA LECH (nhan = THUAN hap thu)"),
            ("VW", "cum vol lon TAI VWAP NGAY +-2 gia"),
            ("B", "COMBO B (hap thu dung nghia)"),
            ("BVW", "COMBO B TAI VWAP NGAY")]
    for tag, title in TAPS:
        print("\n=== %s ===" % title)
        for nm, fn in SHAPES:
            tr, te = res[(tag, nm)]
            a, b = cnt[(tag, nm)]
            def f(ds):
                if len(ds) < 30:
                    return "n=%-5d qua it       " % len(ds)
                p = 100.0 * sum(ds) / len(ds)
                return "n=%-5d %5.1f%% z=%+5.2f" % (len(ds), p, zsc(p / 100, 0.5, len(ds)))
            tot = tr + te
            pt = "%5.1f%%" % (100.0 * sum(tot) / len(tot)) if tot else "  -  "
            print("  %-34s | %s | %s | GOP %s | tan suat %5.1f%%"
                  % (nm, f(tr), f(te), pt, 100.0 * a / b if b else 0))
