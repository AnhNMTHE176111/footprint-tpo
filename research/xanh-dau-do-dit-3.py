"""Ban CHIA NGU PHAN VI: do MANH cua hinh "xanh dau do dit" co lien he don dieu voi ket qua khong?

Diem hinh = (top_delta / vol_band_tren) - (bot_delta / vol_band_duoi)
  cao  = xanh dau + do dit ro net    | thap = do dau + xanh dit
Nguong ngu phan vi lay tu NUA DAU, ap y nguyen cho NUA SAU (khong nhin truoc).
"""
import os, sys, math, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
from xanh_dau_util import load_feats

BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEAT = os.path.join(ROOT, "research/perlevel_feats.csv")
W, LOOK, HOR, FWD = 50, 20, 60, 30


def q(vals, p):
    s = sorted(vals); k = (len(s)-1)*p; f = int(k)
    return s[f] if f+1 >= len(s) else s[f] + (s[f+1]-s[f])*(k-f)


if __name__ == "__main__":
    t, o, h, l, c, v, dl = load(BARS)
    n = len(t)
    F = load_feats(FEAT, n)
    half = n // 2
    rows = []      # (half, score, lab, at_vwap, famB)
    sid = [0]*n; k = 0
    for i in range(1, n):
        if t[i]-t[i-1] > 30: k += 1
        sid[i] = k
    vwd = [0.0]*n; pv = pvol = 0.0; cur = -1
    for i in range(n):
        if sid[i] != cur: cur = sid[i]; pv = pvol = 0.0
        tp = (h[i]+l[i]+c[i])/3.0; pv += tp*v[i]; pvol += v[i]
        vwd[i] = pv/pvol if pvol > 0 else c[i]

    last = {-1: -10**9, 1: -10**9}
    for i in range(W+LOOK, n-HOR-4):
        seg = t[i-W:i+HOR+4]
        if seg[-1]-seg[0] != len(seg)-1: continue
        if F["lv"][i] < 4: continue
        mv = st.median(v[i-W:i]); md = st.median([abs(x) for x in dl[i-W:i]])
        u = st.median([h[j]-l[j] for j in range(i-W, i)])
        if mv <= 0 or md <= 0 or u <= 0: continue
        R = h[i]-l[i]
        if R <= 0 or v[i] < 2.5*mv: continue
        up = c[i]+2*u; dn = c[i]-2*u; first = 0
        for j in range(i+1, min(i+HOR, n-1)):
            a = h[j] >= up; b = l[j] <= dn
            if a and b: first = 0; break
            if a: first = 1; break
            if b: first = -1; break
        if first == 0: continue
        tv = F["top_ask"][i]+F["top_bid"][i]; bv = F["bot_ask"][i]+F["bot_bid"][i]
        if tv < 5 or bv < 5: continue
        sc = (F["top_ask"][i]-F["top_bid"][i])/tv - (F["bot_ask"][i]-F["bot_bid"][i])/bv
        for side in (-1, 1):
            if side < 0 and dl[i] > -3.0*md: continue
            if side > 0 and dl[i] < 3.0*md: continue
            if i-last[side] < FWD: continue
            last[side] = i
            lab = 1 if (first > 0) == (side < 0) else 0
            newext = (l[i] <= min(l[i-LOOK:i])) if side < 0 else (h[i] >= max(h[i-LOOK:i]))
            inner = (c[i] >= l[i]+0.5*R) if side < 0 else (c[i] <= h[i]-0.5*R)
            famB = (not newext) and R <= u and inner
            ref = l[i] if side < 0 else h[i]
            rows.append((0 if i < half else 1, sc, lab, abs(ref-vwd[i]) <= 2.0, famB))

    for tag, sel in (("TAT CA cum vol lon", lambda r: True),
                     ("chi combo B (hap thu dung nghia)", lambda r: r[4]),
                     ("chi tai VWAP ngay +-2 gia", lambda r: r[3])):
        ds = [r for r in rows if sel(r)]
        tr = [r for r in ds if r[0] == 0]; te = [r for r in ds if r[0] == 1]
        if len(tr) < 50:
            print("\n=== %s === n qua it (%d/%d)" % (tag, len(tr), len(te))); continue
        cuts = [q([r[1] for r in tr], p) for p in (0.2, 0.4, 0.6, 0.8)]
        def bk(x):
            b = 0
            for cc in cuts:
                if x > cc: b += 1
            return b
        A = [[0,0] for _ in range(5)]; Bq = [[0,0] for _ in range(5)]
        for r in tr: bb = bk(r[1]); A[bb][0] += r[2]; A[bb][1] += 1
        for r in te: bb = bk(r[1]); Bq[bb][0] += r[2]; Bq[bb][1] += 1
        pa = [100.0*x[0]/x[1] if x[1] else float('nan') for x in A]
        pb = [100.0*x[0]/x[1] if x[1] else float('nan') for x in Bq]
        print("\n=== %s ===  (Q1 = do dau xanh dit  ...  Q5 = xanh dau do dit ro nhat)" % tag)
        print("  nua dau (n=%5d): %s   | lech Q5-Q1 = %+5.1f" % (len(tr), " ".join("%5.1f" % x for x in pa), pa[4]-pa[0]))
        print("  nua sau (n=%5d): %s   | lech Q5-Q1 = %+5.1f" % (len(te), " ".join("%5.1f" % x for x in pb), pb[4]-pb[0]))
        print("  co so moi o     : %s" % " ".join("%5d" % x[1] for x in A))
