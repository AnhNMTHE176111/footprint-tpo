"""Do MOI kieu sap xep mau trong nen, tren mau LON — de khong the noi la "dich sai hinh".

Bon goc:
  top>0 & bot<0  = xanh dau, do dit  (CORVEN noi)
  top<0 & bot>0  = do dau, xanh dit
  top>0 & bot>0  = xanh ca hai dau
  top<0 & bot<0  = do ca hai dau
Bien the "dung o cuc tri" (khong dung band 30%): ask>bid tai muc gia CAO NHAT, bid>ask tai muc THAP NHAT.
Bien the "imbalance xep tang": chuoi mat can bang cheo >= 2 o hai dau.

Hai tap su kien:
  (S) MOI NEN (cach nhau >=30 nen)      -> n lon nhat, du luc thong ke
  (V) cum khoi luong lon + delta lech    -> tap CORVEN quan tam
Thuoc do: rao chan doi xung +-2u, 60 nen. Nen ngau nhien = 50%. Chia doi thoi gian.
"""
import os, sys, math, csv, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
from xanh_dau_util import load_feats

BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEAT = os.path.join(ROOT, "research/perlevel_feats.csv")
W, LOOK, HOR, FWD = 50, 20, 60, 30


def zsc(p, p0, n):
    if n <= 0:
        return 0.0
    return (p - p0) / math.sqrt(p0 * (1 - p0) / n)


if __name__ == "__main__":
    t, o, h, l, c, v, dl = load(BARS)
    n = len(t)
    F = load_feats(FEAT, n)
    botd = [F["bot_ask"][i] - F["bot_bid"][i] for i in range(n)]
    topd = [F["top_ask"][i] - F["top_bid"][i] for i in range(n)]
    exhi = [F["hiA"][i] - F["hiB"][i] for i in range(n)]
    exlo = [F["loA"][i] - F["loB"][i] for i in range(n)]
    print("nen %d" % n, flush=True)

    SHAPES = [
        ("xanh dau + do dit  (CORVEN)", lambda i: topd[i] > 0 and botd[i] < 0),
        ("do dau + xanh dit", lambda i: topd[i] < 0 and botd[i] > 0),
        ("xanh ca hai dau", lambda i: topd[i] > 0 and botd[i] > 0),
        ("do ca hai dau", lambda i: topd[i] < 0 and botd[i] < 0),
        ("cuc tri: ask>bid dinh, bid>ask day", lambda i: exhi[i] > 0 and exlo[i] < 0),
        ("cuc tri: nguoc lai", lambda i: exhi[i] < 0 and exlo[i] > 0),
        ("xep tang >=2 hai dau", lambda i: F["stk_buy_top"][i] >= 2 and F["stk_sell_bot"][i] >= 2),
        ("xep tang >=3 hai dau", lambda i: F["stk_buy_top"][i] >= 3 and F["stk_sell_bot"][i] >= 3),
        ("xanh dau+do dit MANH (>=25% vol band)",
         lambda i: (topd[i] > 0.25 * max(1, F["top_ask"][i] + F["top_bid"][i])
                    and -botd[i] > 0.25 * max(1, F["bot_ask"][i] + F["bot_bid"][i]))),
    ]

    half = n // 2
    # (tap, ten hinh, side) -> [nua dau], [nua sau]
    res = defaultdict(lambda: ([], []))
    cnt = defaultdict(lambda: [0, 0])
    lastS = -10 ** 9
    lastV = {-1: -10 ** 9, 1: -10 ** 9}

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
        if R <= 0:
            continue
        up = c[i] + 2 * u
        dn = c[i] - 2 * u
        first = 0
        for j in range(i + 1, min(i + HOR, n - 1)):
            a = h[j] >= up
            b = l[j] <= dn
            if a and b:
                first = 0; break
            if a:
                first = 1; break
            if b:
                first = -1; break
        if first == 0:
            continue
        hf = 0 if i < half else 1

        # tap S: moi nen, gan nhan "LEN truoc" (khong co chieu chu dong)
        if i - lastS >= FWD:
            lastS = i
            for nm, fn in SHAPES:
                ok = fn(i)
                cnt[("S", nm)][0] += 1 if ok else 0
                cnt[("S", nm)][1] += 1
                if ok:
                    res[("S", nm)][hf].append(1 if first > 0 else 0)

        # tap V: cum khoi luong lon + delta lech han
        if v[i] < 2.5 * mv:
            continue
        for side in (-1, 1):
            if side < 0 and dl[i] > -3.0 * md:
                continue
            if side > 0 and dl[i] < 3.0 * md:
                continue
            if i - lastV[side] < FWD:
                continue
            lastV[side] = i
            lab = 1 if (first > 0) == (side < 0) else 0     # thuan = nguoc chieu chu dong
            for nm, fn in SHAPES:
                ok = fn(i)
                cnt[("V", nm)][0] += 1 if ok else 0
                cnt[("V", nm)][1] += 1
                if ok:
                    res[("V", nm)][hf].append(lab)

    for tap, title, base_note in (("S", "TAP S — MOI NEN (nhan = gia LEN 2u truoc)", "nen 50%"),
                                  ("V", "TAP V — CUM VOL LON + DELTA LECH (nhan = THUAN hap thu)", "nen 50%")):
        print("\n=== %s ===" % title)
        allv = res[(tap, SHAPES[0][0])][0] + res[(tap, SHAPES[0][0])][1]
        print("  %-38s | %-24s | %-24s | tan suat" % ("hinh", "nua dau", "nua sau"))
        for nm, fn in SHAPES:
            tr, te = res[(tap, nm)]
            a, b = cnt[(tap, nm)]
            def f(ds):
                if len(ds) < 30:
                    return "n=%-5d qua it        " % len(ds)
                p = 100.0 * sum(ds) / len(ds)
                return "n=%-5d %5.1f%%  z=%+5.2f" % (len(ds), p, zsc(p / 100, 0.5, len(ds)))
            print("  %-38s | %s | %s | %5.1f%%" % (nm, f(tr), f(te), 100.0 * a / b if b else 0))
