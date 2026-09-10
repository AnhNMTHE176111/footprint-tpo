"""STACKED IMBALANCE -> gia co di TIEP theo chieu cua no khong?

Cau hoi cua nguoi hoc (2026-09-10):
  1) Neu doi dieu kien min-vol tu  >  thanh  >=  thi so ca tang bao nhieu?
  2) Sau mot STACKED SELL imbalance, gia co di XUONG tiep khong (va nguoc lai voi BUY)?
     -> co dang de code thanh signal entry follow-trend khong?

Luat lay dung tu quantower-orderflow-indicator/OrderFlowBubbles.cs:
  imbMinVol = max(MinLevelVolFloor=5, median volume/o cua BASELINE)
  BASELINE  = RollingRobust(100 nen), moi nen chi nap  BaselineTopLevels=3  o DAM NHAT  (dong 1061-1065)
  cheo      : buy  imb tai muc k   neu ask[k]   > 300% * bid[k-1]  va ask[k]   > imbMinVol
              sell imb tai muc k-1 neu bid[k-1] > 300% * ask[k]    va bid[k-1] > imbMinVol
  stacked   = >= 3 muc lien tiep (ImbalanceRun=3)
  Bien the GE: doi ca hai dau  >  thanh  >=  (dung cho cau hoi 1)

Chong bay:
  - /GC:XCEC la ma lien tuc noi tho -> cua so nao vat qua buoc nhay gia (>20 gia/nen) hoac
    qua khoang nghi (>5 phut/nen) deu bi LOAI.
  - Tach doi thoi gian (nua dau / nua sau) — luat repo.
"""
import os, csv, statistics as st
from collections import deque
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv")
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
OUT = os.path.join(ROOT, "research/stack_imb_feats.csv")

BASE_BARS, TOPK, FLOOR, RATIO, RUN, RECALC = 100, 3, 5.0, 3.0, 3, 10
HORIZONS = [1, 3, 5, 10, 20]
MAX_JUMP = 20.0      # gia/nen -> nghi noi hop dong
MAX_GAP_MIN = 5.0    # phut/nen -> nghi nghi phien


class Base:
    """Median cua volume/o tren 100 nen gan nhat, moi nen chi nap TOPK o dam nhat."""

    def __init__(self, k):
        self.q = deque(maxlen=k)
        self.n = 0
        self.med = 0.0
        self.cnt = 0

    def push(self, vals):
        vals = sorted(vals, reverse=True)[:TOPK]
        self.q.append(vals)
        self.n += 1
        self.cnt += 1
        if self.cnt >= RECALC or self.med == 0.0:
            self.cnt = 0
            flat = [x for v in self.q for x in v]
            if flat:
                self.med = st.median(flat)

    @property
    def ready(self):
        return self.n >= BASE_BARS


def scan(lv, imb_min, ge):
    """Tra ve (run_sell_max, run_buy_max) cua nen. lv da sort theo gia tang."""
    ask = {p: a for p, b, a in lv}
    bid = {p: b for p, b, a in lv}
    run_s = run_b = 0
    max_s = max_b = 0
    for p, b, a in lv:
        bprev = bid.get(p - 1)
        if bprev is None:                 # muc duoi khong co giao dich -> dut chuoi
            run_s = run_b = 0
            continue
        if ge:
            ok_b = a >= RATIO * bprev and a >= imb_min
            ok_s = bprev >= RATIO * a and bprev >= imb_min
        else:
            ok_b = a > RATIO * bprev and a > imb_min
            ok_s = bprev > RATIO * a and bprev > imb_min
        run_b = run_b + 1 if ok_b else 0
        run_s = run_s + 1 if ok_s else 0
        max_b = max(max_b, run_b)
        max_s = max(max_s, run_s)
    return max_s, max_b


def pass1():
    fo = open(OUT, "w", newline="", encoding="utf-8")
    w = csv.writer(fo)
    w.writerow(["bar_idx", "ready", "s_gt", "b_gt", "s_ge", "b_ge", "imb_min"])
    base = Base(BASE_BARS)
    cur, lv, nb = None, [], 0

    def emit():
        lv.sort()
        if base.ready:
            imb_min = max(FLOOR, base.med)
            s_gt, b_gt = scan(lv, imb_min, False)
            s_ge, b_ge = scan(lv, imb_min, True)
            w.writerow([cur, 1, s_gt, b_gt, s_ge, b_ge, imb_min])
        else:
            w.writerow([cur, 0, 0, 0, 0, 0, 0])
        base.push([b + a for p, b, a in lv])

    with open(SRC, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            bi = int(row[0])
            if bi != cur:
                if lv:
                    emit()
                    nb += 1
                    if nb % 200000 == 0:
                        print("  ...%d nen" % nb, flush=True)
                cur, lv = bi, []
            lv.append((int(round(float(row[2]) * 10)), int(row[3]), int(row[4])))
    if lv:
        emit()
        nb += 1
    fo.close()
    print("pass1 xong %d nen -> %s" % (nb, OUT), flush=True)


def load_bars():
    bars = {}
    with open(BARS, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            bars[int(row["bar_idx"])] = (
                datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S"),
                float(row["close"]),
            )
    return bars


def analyse():
    bars = load_bars()
    idxs = sorted(bars)
    pos = {b: i for i, b in enumerate(idxs)}
    feats = {}
    with open(OUT, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            feats[int(row["bar_idx"])] = row

    def fwd(b, k):
        """close[b+k]-close[b], None neu cua so co buoc nhay gia hoac khoang nghi."""
        i = pos.get(b)
        if i is None or i + k >= len(idxs):
            return None
        t0, c0 = bars[idxs[i]]
        prev_t, prev_c = t0, c0
        for j in range(i + 1, i + k + 1):
            t, c = bars[idxs[j]]
            if abs(c - prev_c) > MAX_JUMP:
                return None
            if (t - prev_t).total_seconds() / 60.0 > MAX_GAP_MIN:
                return None
            prev_t, prev_c = t, c
        return prev_c - c0

    half = idxs[len(idxs) // 2]

    def bucket(pred, k):
        """tra ve (n, %theo chieu, trung vi dich chuyen) tach doi thoi gian"""
        out = []
        for lo, hi in ((idxs[0], half), (half, idxs[-1] + 1)):
            moves, n_fav = [], 0
            for b in idxs:
                if b < lo or b >= hi:
                    continue
                fr = feats.get(b)
                if not fr or fr["ready"] != "1":
                    continue
                sgn = pred(fr)
                if sgn == 0:
                    continue
                d = fwd(b, k)
                if d is None:
                    continue
                moves.append(d * sgn)          # sgn=-1 voi sell: >0 nghia la di dung chieu
                if d * sgn > 0:
                    n_fav += 1
            if moves:
                out.append((len(moves), 100.0 * n_fav / len(moves), st.median(moves)))
            else:
                out.append((0, float("nan"), float("nan")))
        return out

    tests = [
        ("SELL stacked (>=3, dk >)", lambda r: -1 if int(r["s_gt"]) >= RUN else 0),
        ("SELL stacked (>=3, dk >=)", lambda r: -1 if int(r["s_ge"]) >= RUN else 0),
        ("BUY  stacked (>=3, dk >)", lambda r: 1 if int(r["b_gt"]) >= RUN else 0),
        ("BUY  stacked (>=3, dk >=)", lambda r: 1 if int(r["b_ge"]) >= RUN else 0),
        ("SELL stacked >=4 muc (dk >=)", lambda r: -1 if int(r["s_ge"]) >= 4 else 0),
        ("BUY  stacked >=4 muc (dk >=)", lambda r: 1 if int(r["b_ge"]) >= 4 else 0),
        ("DOI CHUNG: moi nen, chieu XUONG", lambda r: -1),
        ("DOI CHUNG: moi nen, chieu LEN", lambda r: 1),
    ]

    ready = [b for b in idxs if feats.get(b, {}).get("ready") == "1"]
    print("\n=== TAN SUAT (tren %d nen ready) ===" % len(ready))
    for name, key in (("s_gt", "s_gt"), ("s_ge", "s_ge"), ("b_gt", "b_gt"), ("b_ge", "b_ge")):
        c3 = sum(1 for b in ready if int(feats[b][key]) >= 3)
        c4 = sum(1 for b in ready if int(feats[b][key]) >= 4)
        print("  %-5s : >=3 muc %7d nen (%.2f%%) | >=4 muc %6d (%.2f%%)"
              % (key, c3, 100.0 * c3 / len(ready), c4, 100.0 * c4 / len(ready)))
    mins = [float(feats[b]["imb_min"]) for b in ready]
    print("  imbMinVol: trung vi %.1f | phan vi 10%% %.1f | 90%% %.1f"
          % (st.median(mins), st.quantiles(mins, n=10)[0], st.quantiles(mins, n=10)[8]))

    for name, pred in tests:
        print("\n--- %s ---" % name)
        print("  k |      nua dau (n, %dung chieu, trung vi diem) |      nua sau")
        for k in HORIZONS:
            (n1, p1, m1), (n2, p2, m2) = bucket(pred, k)
            print("  %2d | %7d  %5.1f%%  %+6.2f | %7d  %5.1f%%  %+6.2f"
                  % (k, n1, p1, m1, n2, p2, m2))


if __name__ == "__main__":
    if not os.path.exists(OUT):
        pass1()
    analyse()
