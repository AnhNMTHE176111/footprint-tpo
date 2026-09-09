"""PASS 1c — trich BUBBLE theo dung luat trong OrderFlowBubbles.cs, cho tung nen M1.

Hai nguon bubble do duoc (nguon thu ba, LENH DON, khong co du lieu):
  HVN cell : vol o >= MinLevelVolFloor(5) VA modZ >= BigZ(3.0) VA vol >= BigVolMult(4.0) x median
             mau = XANH neu ask >= bid, DO neu nguoc lai        (AggColor(buy, sell))
  Stacked imbalance : cheo 3:1, >= 3 muc lien tiep
             mua: ask[k] > 3 x bid[k-1] va ask[k] > imbMinVol  -> XANH tai k
             ban: bid[k-1] > 3 x ask[k] va bid[k-1] > imbMinVol -> DO tai k-1
Nen: RollingRobust(BaselineBars=100) tren volume TUNG O; modZ = 0.6745*(x-median)/MAD.
     Tinh lai median/MAD moi 10 nen (indicator tinh moi nen; sai khac khong dang ke).

Band: 30% TREN / 30% DUOI cua bien do nen (theo gia).
Xuat: so bubble xanh/do trong tung band, tach theo nguon.
"""
import os, csv, statistics as st
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv")
OUT = os.path.join(ROOT, "research/bubble_feats.csv")
BASE_BARS, FLOOR, BIGZ, BIGMULT, IMB_RATIO, IMB_RUN, BAND = 100, 5.0, 3.0, 4.0, 3.0, 3, 0.30
RECALC = 10


class Base:
    def __init__(self, k):
        self.q = deque(maxlen=k)
        self.n = 0
        self.med = 0.0
        self.mad = 0.0
        self.cnt = 0

    def push(self, vals):
        self.q.append(vals)
        self.n += 1
        self.cnt += 1
        if self.cnt >= RECALC or self.med == 0.0:
            self.cnt = 0
            flat = [x for v in self.q for x in v]
            if flat:
                self.med = st.median(flat)
                self.mad = st.median([abs(x - self.med) for x in flat])

    def modz(self, x):
        if self.mad > 1e-9:
            return 0.6745 * (x - self.med) / self.mad
        if self.med > 1e-9:
            return (x - self.med) / self.med
        return 0.0


def emit(w, bidx, lv, base):
    lv.sort()
    lo = lv[0][0]
    hi = lv[-1][0]
    rng = hi - lo
    bot_hi = lo + rng * BAND
    top_lo = hi - rng * BAND
    ready = base.n >= BASE_BARS
    hgt = hrt = hgb = hrb = 0
    igt = irt = igb = irb = 0
    if ready:
        imb_min = max(FLOOR, base.med)
        bid = {p: b for p, b, a in lv}
        ask = {p: a for p, b, a in lv}
        for p, b, a in lv:
            vol = b + a
            # --- HVN cell ---
            if vol >= FLOOR and base.modz(vol) >= BIGZ and vol >= BIGMULT * base.med:
                green = a >= b
                if p >= top_lo:
                    if green: hgt += 1
                    else: hrt += 1
                if p <= bot_hi:
                    if green: hgb += 1
                    else: hrb += 1
        # --- stacked imbalance ---
        run_b = run_s = 0
        for p, b, a in lv:
            bprev = bid.get(p - 1)
            if bprev is None:
                run_b = run_s = 0
                continue
            aprev_lvl = a
            run_b = run_b + 1 if (a > IMB_RATIO * bprev and a > imb_min) else 0
            if run_b >= IMB_RUN:
                if p >= top_lo: igt += 1
                if p <= bot_hi: igb += 1
            run_s = run_s + 1 if (bprev > IMB_RATIO * aprev_lvl and bprev > imb_min) else 0
            if run_s >= IMB_RUN:
                q = p - 1
                if q >= top_lo: irt += 1
                if q <= bot_hi: irb += 1
    w.writerow([bidx, 1 if ready else 0, hgt, hrt, hgb, hrb, igt, irt, igb, irb])
    base.push([b + a for p, b, a in lv])


def main():
    fo = open(OUT, "w", newline="", encoding="utf-8")
    w = csv.writer(fo)
    w.writerow(["bar_idx", "ready", "hvn_g_top", "hvn_r_top", "hvn_g_bot", "hvn_r_bot",
                "imb_g_top", "imb_r_top", "imb_g_bot", "imb_r_bot"])
    base = Base(BASE_BARS)
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
                    emit(w, cur, lv, base)
                    nb += 1
                    if nb % 100000 == 0:
                        print("  ...%d nen" % nb, flush=True)
                cur = bi
                lv = []
            lv.append((int(round(float(row[2]) * 10)), int(row[3]), int(row[4])))
    if lv:
        emit(w, cur, lv, base)
        nb += 1
    fo.close()
    print("xong %d nen -> %s" % (nb, OUT))


if __name__ == "__main__":
    main()
