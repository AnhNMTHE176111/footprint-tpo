"""PASS 1 — quet file per-level 583 MB, trich dac trung THEO MUC GIA cho tung nen M1.

Chi dung thong tin CO TAI LUC NEN DONG (khong nhin truoc).
Xuat ra CSV nho de cac phep do sau chay nhanh.

Cot xuat:
  bar_idx, lv, lo_t, hi_t                 (lo_t/hi_t = gia thap/cao nhat, don vi tick)
  bot_bid, bot_ask, top_bid, top_ask      (band 30% duoi / 30% tren theo GIA)
  mid_bid, mid_ask
  nbuy_top, nsell_bot                     (so mat can bang cheo trong band)
  stk_buy_top, stk_sell_bot               (chuoi mat can bang lien tiep dai nhat trong band)
  loB, loA, hiB, hiA                      (bid/ask tai muc gia thap nhat / cao nhat)
  poc_pos                                 (vi tri POC trong bien do, 0=day 1=dinh, x1000)
"""
import os, sys, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv")
OUT = os.path.join(ROOT, "research/perlevel_feats.csv")
IMB = 3.0          # ty le mat can bang cheo (chuan footprint)
MINV = 2           # khoi luong toi thieu de tinh mat can bang (loai o 0 vs 1)
BAND = 0.30        # 30% duoi / tren


def flush(w, bidx, lv):
    lv.sort()
    n = len(lv)
    lo_t = lv[0][0]
    hi_t = lv[-1][0]
    rng = hi_t - lo_t
    bot_hi = lo_t + rng * BAND
    top_lo = hi_t - rng * BAND
    bb = ba = tb = ta = mb = ma = 0
    pocv = -1
    pocp = lo_t
    for p, b, a in lv:
        if b + a > pocv:
            pocv = b + a
            pocp = p
        if p <= bot_hi:
            bb += b; ba += a
        if p >= top_lo:
            tb += b; ta += a
        if bot_hi < p < top_lo:
            mb += b; ma += a
    # mat can bang cheo: mua tai p neu ask[p] >= IMB*bid[p-1]; ban tai p neu bid[p] >= IMB*ask[p+1]
    bid = {p: b for p, b, a in lv}
    ask = {p: a for p, b, a in lv}
    nbt = nsb = 0
    stk_b = run_b = 0
    stk_s = run_s = 0
    for p, b, a in lv:
        bprev = bid.get(p - 1, 0)
        anext = ask.get(p + 1, 0)
        buy_i = a >= MINV and a >= IMB * max(bprev, 1) and (bprev > 0 or a >= MINV * 2)
        sell_i = b >= MINV and b >= IMB * max(anext, 1) and (anext > 0 or b >= MINV * 2)
        if buy_i and p >= top_lo:
            nbt += 1
        if sell_i and p <= bot_hi:
            nsb += 1
        run_b = run_b + 1 if buy_i else 0
        run_s = run_s + 1 if sell_i else 0
        if p >= top_lo and run_b > stk_b:
            stk_b = run_b
        if p <= bot_hi and run_s > stk_s:
            stk_s = run_s
    w.writerow([bidx, n, lo_t, hi_t, bb, ba, tb, ta, mb, ma, nbt, nsb, stk_b, stk_s,
                bid[lo_t], ask[lo_t], bid[hi_t], ask[hi_t],
                int(1000.0 * (pocp - lo_t) / rng) if rng > 0 else 500])


def main():
    fo = open(OUT, "w", newline="", encoding="utf-8")
    w = csv.writer(fo)
    w.writerow(["bar_idx", "lv", "lo_t", "hi_t", "bot_bid", "bot_ask", "top_bid", "top_ask",
                "mid_bid", "mid_ask", "nbuy_top", "nsell_bot", "stk_buy_top", "stk_sell_bot",
                "loB", "loA", "hiB", "hiA", "poc_pos"])
    cur = None
    lv = []
    nb = 0
    with open(SRC, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            bi = int(row[0])
            if bi != cur:
                if lv:
                    flush(w, cur, lv)
                    nb += 1
                    if nb % 100000 == 0:
                        print("  ...%d nen" % nb, flush=True)
                cur = bi
                lv = []
            lv.append((int(round(float(row[2]) * 10)), int(row[3]), int(row[4])))
    if lv:
        flush(w, cur, lv)
        nb += 1
    fo.close()
    print("xong: %d nen -> %s" % (nb, OUT))


if __name__ == "__main__":
    main()
