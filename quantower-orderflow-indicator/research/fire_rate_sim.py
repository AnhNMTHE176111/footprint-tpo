"""Tần suất kích hoạt Big Trade vs Absorption với ngưỡng đang dùng trong OrderFlowBubbles.

Export của Quantower KHÔNG có per-level, nên footprint được DỰNG LẠI bằng mô phỏng
vi cấu trúc, hiệu chỉnh theo số thật của TỪNG nến (V, H, L, O, C, buy/sell volume):
  - mỗi trade ~1 lot (dữ liệu thật: Average size ≈ 1.07, Trades ≈ Volume)
  - mô hình A: random walk phản xạ trong [Low, High] (phân bố VOLUME PHẲNG hơn -> bất lợi cho fire)
  - mô hình B: hình chuông quanh POC (POC lệch ngẫu nhiên quanh giữa nến -> giống footprint thật)
  - phe mua/bán tại mỗi mức: nhị thức quanh tỉ lệ buy/sell THẬT của nến
Sau đó chạy ĐÚNG công thức trong OrderFlowBubbles.cs: RollingRobust median+MAD trên 100 nến,
modified z-score, và toàn bộ điều kiện AND/OR của từng detector.
"""
import csv, math, random, statistics as st

random.seed(7)
TICK = 0.1
NBARS = 6000          # ~6000 nến M1 gần nhất (tháng 7/2026, thanh khoản cao nhất)

# ---- ngưỡng ĐANG DÙNG trong code ----
BASELINE_BARS = 100
MIN_BARS = 40
MIN_LVL_FLOOR = 5
ABS_Z = 4.0
ABS_DOM = 0.60
ABS_MAX_DISPL_TICKS = 2
BIG_Z = 4.5

rows = []
for r in csv.DictReader(open('data-export/fp-m1-6-month.csv', encoding='utf-8-sig')):
    d = r['DateTime'].split()[0]
    mm, dd, yy = d.split('/')
    if yy != '2026' or int(mm) < 5:
        continue
    try:
        v = float(r['Volume'])
        rows.append(dict(t=r['DateTime'], o=float(r['Open']), h=float(r['High']),
                         l=float(r['Low']), c=float(r['Close']), v=v,
                         buy=float(r['Buy (Ask) volume']), sell=float(r['Sell (Bid) volume'])))
    except ValueError:
        pass
rows = rows[-NBARS:]


def levels_walk(b):
    """mô hình A: random walk phản xạ, mỗi bước 1 lot"""
    lo = round(b['l'] / TICK); hi = round(b['h'] / TICK)
    L = hi - lo + 1
    vol = [0] * L
    if L <= 0 or b['v'] <= 0:
        return vol
    pos = min(max(round(b['o'] / TICK) - lo, 0), L - 1)
    drift = 0.5 + 0.5 * ((b['c'] - b['o']) / max(b['h'] - b['l'], TICK)) * 0.5
    for _ in range(int(b['v'])):
        vol[pos] += 1
        pos += 1 if random.random() < drift else -1
        if pos < 0: pos = min(1, L - 1)
        if pos > L - 1: pos = max(L - 2, 0)
    return vol


def levels_bell(b):
    """mô hình B: hình chuông quanh POC (POC ~ giữa nến, lệch ngẫu nhiên)"""
    lo = round(b['l'] / TICK); hi = round(b['h'] / TICK)
    L = hi - lo + 1
    if L <= 0 or b['v'] <= 0:
        return [0] * L
    poc = (L - 1) * (0.5 + random.uniform(-0.25, 0.25))
    sig = max(L / 4.0, 0.8)
    w = [math.exp(-0.5 * ((i - poc) / sig) ** 2) + 0.05 for i in range(L)]
    s = sum(w)
    vol = [0] * L
    left = int(b['v'])
    for i in range(L):
        q = int(round(left * w[i] / s)) if s > 0 else 0
        vol[i] = q
        s -= w[i]; left -= q
        if left <= 0: break
    return vol


def split_sides(b, vol):
    """chia buy/sell mỗi mức: nhị thức quanh tỉ lệ buy thật của nến"""
    tot = b['buy'] + b['sell']
    p = b['buy'] / tot if tot > 0 else 0.5
    out = []
    for v in vol:
        if v <= 0:
            out.append((0, 0)); continue
        buy = sum(1 for _ in range(v) if random.random() < p)
        out.append((buy, v - buy))
    return out


class Robust:
    def __init__(s, w): s.w = w; s.bars = []
    def add(s, vals):
        s.bars.append(list(vals))
        if len(s.bars) > s.w: s.bars.pop(0)
        s._c = None
    def stats(s):
        if getattr(s, '_c', None): return s._c
        allv = [x for b in s.bars for x in b]
        if not allv: s._c = (0.0, 0.0); return s._c
        m = st.median(allv)
        mad = st.median([abs(x - m) for x in allv])
        s._c = (m, mad); return s._c
    def modz(s, x):
        m, mad = s.stats()
        if mad > 1e-9: return 0.6745 * (x - m) / mad
        if m > 1e-9: return (x - m) / m
        return 0.0
    @property
    def median(s): return s.stats()[0]
    @property
    def nbars(s): return len(s.bars)


def run(model):
    rl = Robust(BASELINE_BARS)
    nbig = nabs = ndone = 0
    nabs_z_ok = 0            # có mức đạt z volume nhưng rớt các điều kiện khác
    nabs_z_at_extreme = 0    # ... và mức đó nằm sát cực trị
    thr_big, thr_abs = [], []
    for b in rows:
        vol = model(b)
        if not vol:
            continue
        sides = split_sides(b, vol)
        lo = round(b['l'] / TICK); hi = round(b['h'] / TICK)
        ready = rl.nbars >= MIN_BARS
        if ready:
            ndone += 1
            med = rl.median
            big = False; ab = False; zok = False; zext = False
            for i, v in enumerate(vol):
                if v <= 0: continue
                price_ticks = lo + i
                z = rl.modz(v)
                # --- BIG TRADE (fallback vol/mức vì feed không có MaxOneTradeVolume) ---
                if v >= MIN_LVL_FLOOR and (z >= BIG_Z or v >= 3 * med):
                    big = True
                # --- ABSORPTION ---
                if v >= MIN_LVL_FLOOR and z >= ABS_Z:
                    zok = True
                    buy, sell = sides[i]; sm = buy + sell
                    near_hi = (hi - price_ticks) <= ABS_MAX_DISPL_TICKS
                    near_lo = (price_ticks - lo) <= ABS_MAX_DISPL_TICKS
                    if near_hi or near_lo: zext = True
                    if sm > 0:
                        if buy / sm >= ABS_DOM and near_hi and (b['h'] - b['c']) >= TICK:
                            ab = True
                        elif sell / sm >= ABS_DOM and near_lo and (b['c'] - b['l']) >= TICK:
                            ab = True
            nbig += big; nabs += ab; nabs_z_ok += zok; nabs_z_at_extreme += zext
            # ngưỡng volume/mức tương đương (để hiểu con số thực tế)
            m, mad = rl.stats()
            if mad > 1e-9:
                thr_big.append(m + BIG_Z * mad / 0.6745)
                thr_abs.append(m + ABS_Z * mad / 0.6745)
        rl.add([v for v in vol if v > 0] or [0])
    return ndone, nbig, nabs, nabs_z_ok, nabs_z_at_extreme, thr_big, thr_abs


for name, model in (('A · random-walk (phẳng)', levels_walk), ('B · bell/POC (tập trung)', levels_bell)):
    n, big, ab, zok, zext, tb, ta = run(model)
    med3 = st.median([r['v'] for r in rows])
    print(f"\n=== mô hình {name} — {n} nến có baseline ===")
    print(f"  BIG TRADE  fire ở {100*big/n:5.1f}% số nến")
    print(f"  ABSORPTION fire ở {100*ab/n:5.1f}% số nến")
    print(f"  (có mức đạt z≥{ABS_Z} bất kỳ đâu: {100*zok/n:5.1f}%  |  mức đó nằm ≤2 tick cực trị: {100*zext/n:5.1f}%)")
    if tb:
        print(f"  ngưỡng volume/mức tương đương: BigTrade z≥{BIG_Z} ⇒ ~{st.median(tb):.0f} lot | "
              f"Absorption z≥{ABS_Z} ⇒ ~{st.median(ta):.0f} lot | cửa OR '3×median' ⇒ ~{3*st.median([0]) if False else 0:.0f}")
print(f"\nvolume/nến median giai đoạn test: {st.median([r['v'] for r in rows]):.0f}")
