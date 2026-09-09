"""COMBO CORVEN + "XANH DAU DO DIT" — do tren du lieu THEO MUC GIA (file 583 MB).

"Xanh dau do dit" dich sang so do duoc: trong cung mot nen M1,
  - band 30% TREN cua nen: ask > bid  (mua chu dong day len dinh nen)  => "xanh dau"
  - band 30% DUOI cua nen: bid > ask  (ban chu dong day xuong day nen) => "do dit"
Hinh nay KHONG phu thuoc chieu: no noi "hai dau nen deu do lenh CHU DONG tao ra roi bi hap thu".
Nen ap dung y nguyen cho ca hap thu ban (o day) va hap thu mua (o dinh).

Ba muc chat:
  P1 (long)  : top_delta > 0 va bot_delta < 0
  P2 (chat)  : P1 + chuoi mat can bang cheo >= 2 o CA HAI dau
  P3 (rat chat): P1 + so mat can bang cheo >= 2 o ca hai dau + chuoi >= 2
  PN (doi chung, NGUOC hinh): top_delta < 0 va bot_delta > 0

Thuoc do: rao chan doi xung +-2u tu gia dong nen su kien, 60 nen, ben nao cham truoc.
Nen ngau nhien = 50%. Chia doi thoi gian: nua dau / nua sau.
"""
import os, sys, math, csv, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load

BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEAT = os.path.join(ROOT, "research/perlevel_feats.csv")
W, LOOK, HOR, FWD = 50, 20, 60, 30
TOL = 2.0


def zsc(p, p0, n):
    if n <= 0 or p0 <= 0 or p0 >= 1:
        return 0.0
    return (p - p0) / math.sqrt(p0 * (1 - p0) / n)


def load_feats(path, n):
    K = ("lv", "bot_bid", "bot_ask", "top_bid", "top_ask", "mid_bid", "mid_ask",
         "nbuy_top", "nsell_bot", "stk_buy_top", "stk_sell_bot", "loB", "loA", "hiB", "hiA", "poc_pos")
    F = {k: [0] * n for k in K}
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        hd = next(r)
        ix = {k: i for i, k in enumerate(hd)}
        for row in r:
            b = int(row[0])
            if b >= n:
                continue
            for k in K:
                F[k][b] = int(row[ix[k]])
    return F


def outcome(i, u, side, h, l, c):
    up = c[i] + 2 * u
    dn = c[i] - 2 * u
    for j in range(i + 1, min(i + HOR, len(h) - 1)):
        a = h[j] >= up
        b = l[j] <= dn
        if a and b:
            return None
        if a:
            return 1 if side < 0 else 0
        if b:
            return 0 if side < 0 else 1
    return None


def rep(tag, tr, te):
    out = []
    for nm, ds in (("nua dau", tr), ("nua sau", te)):
        if len(ds) < 15:
            out.append("%s n=%-4d qua it        " % (nm, len(ds)))
        else:
            p = 100.0 * sum(ds) / len(ds)
            out.append("%s n=%-5d %5.1f%% z=%+5.2f" % (nm, len(ds), p, zsc(p / 100, 0.5, len(ds))))
    tot = tr + te
    ptot = 100.0 * sum(tot) / len(tot) if tot else 0.0
    print("  %-34s | %s | %s | GOP n=%-5d %5.1f%%"
          % (tag, out[0], out[1], len(tot), ptot))


if __name__ == "__main__":
    t, o, h, l, c, v, dl = load(BARS)
    n = len(t)
    F = load_feats(FEAT, n)
    print("nen: %d | co dac trung per-level: %d" % (n, sum(1 for x in F["lv"] if x > 0)), flush=True)

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

    botd = [F["bot_ask"][i] - F["bot_bid"][i] for i in range(n)]
    topd = [F["top_ask"][i] - F["top_bid"][i] for i in range(n)]

    def pat(i, lvl):
        if F["lv"][i] < 4:
            return False
        p1 = topd[i] > 0 and botd[i] < 0
        if lvl == 1:
            return p1
        if lvl == 2:
            return p1 and F["stk_buy_top"][i] >= 2 and F["stk_sell_bot"][i] >= 2
        if lvl == 3:
            return (p1 and F["stk_buy_top"][i] >= 2 and F["stk_sell_bot"][i] >= 2
                    and F["nbuy_top"][i] >= 2 and F["nsell_bot"][i] >= 2)
        if lvl == 0:
            return topd[i] < 0 and botd[i] > 0
        return False

    half = n // 2
    BUCK = ["combo B tai VWAP ngay", "combo B bat ky dau", "cum vol lon bat ky"]
    res = defaultdict(lambda: ([], []))
    freq = defaultdict(lambda: [0, 0])
    last = {-1: -10 ** 9, 1: -10 ** 9}

    for i in range(W + LOOK, n - HOR - 4):
        seg = t[i - W:i + HOR + 4]
        if seg[-1] - seg[0] != len(seg) - 1:
            continue
        if F["lv"][i] < 4:
            continue
        mv = st.median(v[i - W:i])
        md = st.median([abs(x) for x in dl[i - W:i]])
        u = st.median([h[j] - l[j] for j in range(i - W, i)])
        if mv <= 0 or md <= 0 or u <= 0:
            continue
        R = h[i] - l[i]
        if R <= 0 or v[i] < 2.5 * mv:
            continue
        for side in (-1, 1):
            if side < 0 and dl[i] > -3.0 * md:
                continue
            if side > 0 and dl[i] < 3.0 * md:
                continue
            if i - last[side] < FWD:
                continue
            newext = (l[i] <= min(l[i - LOOK:i])) if side < 0 else (h[i] >= max(h[i - LOOK:i]))
            inner = (c[i] >= l[i] + 0.5 * R) if side < 0 else (c[i] <= h[i] - 0.5 * R)
            famB = (not newext) and R <= u and inner
            ref = l[i] if side < 0 else h[i]
            atvwap = abs(ref - vwd[i]) <= TOL
            lab = outcome(i, u, side, h, l, c)
            if lab is None:
                continue
            last[side] = i
            groups = ["cum vol lon bat ky"]
            if famB:
                groups.append("combo B bat ky dau")
                if atvwap:
                    groups.append("combo B tai VWAP ngay")
            hf = 0 if i < half else 1
            for g in groups:
                for lvl, nmp in ((None, "TAT CA (khong loc hinh)"), (1, "co P1 xanh dau do dit"),
                                 (2, "co P2 (imbalance xep tang >=2)"), (3, "co P3 (rat chat)"),
                                 (0, "hinh NGUOC (doi chung)")):
                    if lvl is None:
                        ok = True
                    else:
                        ok = pat(i, lvl)
                    if lvl is not None:
                        freq[(g, nmp)][0] += 1 if ok else 0
                        freq[(g, nmp)][1] += 1
                    if ok:
                        res[(g, nmp)][hf].append(lab)

    for g in BUCK:
        print("\n=== %s ===" % g.upper())
        for nmp in ("TAT CA (khong loc hinh)", "co P1 xanh dau do dit", "co P2 (imbalance xep tang >=2)",
                    "co P3 (rat chat)", "hinh NGUOC (doi chung)"):
            tr, te = res[(g, nmp)]
            if not tr and not te:
                continue
            rep(nmp, tr, te)
        print("  -- tan suat xuat hien hinh trong nhom --")
        for nmp in ("co P1 xanh dau do dit", "co P2 (imbalance xep tang >=2)", "co P3 (rat chat)",
                    "hinh NGUOC (doi chung)"):
            a, b = freq[(g, nmp)]
            if b:
                print("     %-34s %5.1f%%  (%d/%d)" % (nmp, 100.0 * a / b, a, b))
