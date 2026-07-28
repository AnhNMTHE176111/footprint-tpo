#!/usr/bin/env python3
"""Vòng 4: đo lại MỌI phát hiện với target CHUẨN HOÁ theo biến động.

Vì sao: target cố định 1 USD làm mọi đặc trưng tương quan với biến động trông như có edge.
Volume/nến trung bình T5≈26, T6≈20, T7≈73 → biến động chênh 3-4×. Đo được: nến cực trị
range ≥20 tick cho hit ~59,4% vs range 5-10 tick ~50,5% — chênh 9pp thuần do biến động.

Ở đây: TARGET_i = K × median(range 100 nến trước i)  → mỗi tín hiệu có target riêng.
Và mọi bảng đều chia theo QUARTILE BIẾN ĐỘNG để thấy edge có tồn tại ở mọi chế độ hay không.

Chạy: python3 volnorm_test.py
"""
import pickle, statistics as st

BARS = pickle.load(open(__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'data-export/27-7/perlevel_m1_clean.pkl', 'rb'))
N = len(BARS)
K_TARGET = 2.0          # target = 2 × median range 100 nến
HORIZON, LB = 20, 10
BASELINE_BARS, MIN_BARS, MIN_LVL_FLOOR = 100, 40, 5


class Robust:
    def __init__(s, w): s.w, s.bars, s._c = w, [], None
    def add(s, v):
        s.bars.append(list(v))
        if len(s.bars) > s.w: s.bars.pop(0)
        s._c = None
    def stats(s):
        if s._c: return s._c
        a = [x for b in s.bars for x in b]
        if not a: s._c = (0.0, 0.0); return s._c
        m = st.median(a); s._c = (m, st.median([abs(x - m) for x in a])); return s._c
    def modz(s, x):
        m, mad = s.stats()
        if mad > 1e-9: return 0.6745 * (x - m) / mad
        return (x - m) / m if m > 1e-9 else 0.0
    @property
    def median(s): return s.stats()[0]
    @property
    def n(s): return len(s.bars)


# ---------- đặc trưng + median range động ----------
print("tính đặc trưng...")
F = [None] * N
MEDR = [0.0] * N          # median range 100 nến trước (đơn vị giá)
rl, rrange, rbarvol, rimpact = (Robust(BASELINE_BARS) for _ in range(4))
for i, b in enumerate(BARS):
    MEDR[i] = rrange.median
    vols = sorted((x[4] for x in b['lvls']), reverse=True)
    if rl.n >= MIN_BARS and MEDR[i] > 0:
        poc = max(b['lvls'], key=lambda x: x[4])
        second = vols[1] if len(vols) > 1 else 0.0
        span = max(b['hi_t'] - b['lo_t'], 1)
        vmed = rbarvol.median
        rng = b['h'] - b['l']
        best = None
        for pt, pr, bid, ask, v in b['lvls']:
            if v < MIN_LVL_FLOOR: continue
            z = rl.modz(v)
            if z < 1.5: continue
            near_hi, near_lo = (b['hi_t'] - pt) <= 2, (pt - b['lo_t']) <= 2
            if not (near_hi or near_lo): continue
            top = near_hi and (not near_lo or (b['hi_t'] - pt) <= (pt - b['lo_t']))
            dpct = (ask - bid) / v
            c = dict(z=z, top=top, price=pr,
                     pocDist=abs(poc[0] - pt), pocRel=abs(poc[0] - pt) / span,
                     pocProm=poc[4] / max(second, 1e-9),
                     divergence=(dpct >= 0.10) if top else (dpct <= -0.10),
                     twoSided=min(bid, ask) >= 0.35 * v,
                     lvlShare=v / b['vol'] if b['vol'] > 0 else 0)
            if best is None or z > best['z']: best = c
        F[i] = dict(best=best,
                    rangeRatio=rng / MEDR[i],
                    barVolRatio=b['vol'] / vmed if vmed > 0 else 0,
                    impactZ=rimpact.modz(abs(b['c'] - b['o']) / b['vol']) if b['vol'] > 0 else 0,
                    medr=MEDR[i])
    rl.add(vols[:3]); rrange.add([b['h'] - b['l']]); rbarvol.add([b['vol']])
    if b['vol'] > 0: rimpact.add([abs(b['c'] - b['o']) / b['vol']])

# quartile biến động (theo median range động)
mr = sorted(MEDR[i] for i in range(N) if MEDR[i] > 0)
Q = [mr[int(q * (len(mr) - 1))] for q in (0.25, 0.5, 0.75)]
print(f"median-range quartile: {Q[0]:.2f} / {Q[1]:.2f} / {Q[2]:.2f} USD")


def volq(i):
    m = MEDR[i]
    return 0 if m < Q[0] else 1 if m < Q[1] else 2 if m < Q[2] else 3


def outcome(i, short):
    """target riêng theo biến động tại i"""
    tgt = K_TARGET * MEDR[i]
    if tgt <= 0: return None
    ref = BARS[i]['c']
    for j in range(i + 1, min(N, i + HORIZON + 1)):
        if short:
            if ref - BARS[j]['l'] >= tgt: return 1
            if BARS[j]['h'] - ref >= tgt: return 0
        else:
            if BARS[j]['h'] - ref >= tgt: return 1
            if ref - BARS[j]['l'] >= tgt: return 0
    return None


def is_ext(i, top):
    if i < LB: return False
    return BARS[i]['h'] >= max(BARS[j]['h'] for j in range(i - LB, i)) if top \
        else BARS[i]['l'] <= min(BARS[j]['l'] for j in range(i - LB, i))


# gom mẫu 1 lần
SAMP = []      # (i, top, win, month, volq)
for i in range(LB, N - HORIZON):
    if F[i] is None: continue
    for top in (True, False):
        if not is_ext(i, top): continue
        o = outcome(i, short=top)
        if o is None: continue
        SAMP.append((i, top, o, BARS[i]['t'][:7], volq(i)))
print(f"mẫu: {len(SAMP)}")

BASE = 100 * sum(s[2] for s in SAMP) / len(SAMP)
print(f"\nBASE (target = {K_TARGET}× median range): {BASE:.1f}%   n={len(SAMP)}")
for m in sorted({s[3] for s in SAMP}):
    g = [s for s in SAMP if s[3] == m]
    print(f"   {m}: {100*sum(x[2] for x in g)/len(g):.1f}% (n={len(g)})")
for q in range(4):
    g = [s for s in SAMP if s[4] == q]
    if g: print(f"   quartile biến động {q}: {100*sum(x[2] for x in g)/len(g):.1f}% (n={len(g)})")


def show(name, cond, need_side=True):
    sel = [s for s in SAMP if cond(s[0], F[s[0]], s[1])] if need_side else \
          [s for s in SAMP if cond(s[0], F[s[0]], s[1])]
    n = len(sel)
    if n == 0: print(f"  {name:50s} n=0"); return
    hit = 100 * sum(s[2] for s in sel) / n
    se = (0.25 / n) ** 0.5 * 100
    sig = (hit - BASE) / se if se > 0 else 0
    line = f"  {name:50s} n={n:5d} hit={hit:5.1f}% ±{se:4.1f}  ({sig:+.1f}σ)"
    # theo quartile biến động
    parts = []
    for q in range(4):
        g = [s for s in sel if s[4] == q]
        parts.append(f"q{q}:{100*sum(x[2] for x in g)/len(g):.0f}%({len(g)})" if len(g) >= 50 else f"q{q}:-")
    print(line + "  | " + " ".join(parts))


print("\n=== A. bar-level: volume & range (sau chuẩn hoá còn edge không?) ===")
for k in (1.5, 2.0, 3.0, 5.0):
    show(f"volume nến ≥ {k}× median", lambda i, f, top, k=k: f['barVolRatio'] >= k)
for k in (1.0, 1.5, 2.0, 3.0):
    show(f"range nến ≥ {k}× median", lambda i, f, top, k=k: f['rangeRatio'] >= k)
for k in (0.5, 0.8):
    show(f"range nến ≤ {k}× median (nến hẹp)", lambda i, f, top, k=k: f['rangeRatio'] <= k)

print("\n=== B. per-level: ô đậm tại cực trị ===")
show("có ô z≥2.5 tại cực trị", lambda i, f, top: f['best'] and f['best']['z'] >= 2.5 and f['best']['top'] == top)
show("có ô z≥4.0 tại cực trị", lambda i, f, top: f['best'] and f['best']['z'] >= 4.0 and f['best']['top'] == top)
show("KHÔNG có ô đậm tại cực trị", lambda i, f, top: not (f['best'] and f['best']['z'] >= 2.5 and f['best']['top'] == top))

print("\n=== C. phát hiện cần kiểm lại: POC xa cực trị ===")
for d in (2, 3, 5):
    show(f"ô z≥2.5 tại cực trị + pocDist>{d}",
         lambda i, f, top, d=d: f['best'] and f['best']['z'] >= 2.5 and f['best']['top'] == top and f['best']['pocDist'] > d)
show("ô z≥2.5 tại cực trị + POC không nổi bật",
     lambda i, f, top: f['best'] and f['best']['z'] >= 2.5 and f['best']['top'] == top and f['best']['pocProm'] < 1.5)
show("ô z≥2.5 + pocRel>0.5 (POC ở nửa xa)",
     lambda i, f, top: f['best'] and f['best']['z'] >= 2.5 and f['best']['top'] == top and f['best']['pocRel'] > 0.5)

print("\n=== D. delta divergence tại ô cực trị (luật của Valtos) ===")
show("ô z≥2.5 tại cực trị + divergence",
     lambda i, f, top: f['best'] and f['best']['z'] >= 2.5 and f['best']['top'] == top and f['best']['divergence'])
show("ô z≥1.5 tại cực trị + divergence",
     lambda i, f, top: f['best'] and f['best']['z'] >= 1.5 and f['best']['top'] == top and f['best']['divergence'])
show("ô z≥2.5 tại cực trị + KHÔNG divergence",
     lambda i, f, top: f['best'] and f['best']['z'] >= 2.5 and f['best']['top'] == top and not f['best']['divergence'])

print("\n=== E. delta NẾN (bar-level) — đối chứng với per-level ===")
for dp in (0.10, 0.20, 0.30):
    show(f"delta nến thuận đà cũ ≥{dp:.2f} (bar-level)",
         lambda i, f, top, dp=dp: (BARS[i]['delta'] / BARS[i]['vol'] if BARS[i]['vol'] > 0 else 0) >= dp if top
         else (BARS[i]['delta'] / BARS[i]['vol'] if BARS[i]['vol'] > 0 else 0) <= -dp)

print("\n=== F. price impact thấp (Kyle lambda) ===")
for z in (-1.0, -1.5):
    show(f"impact z ≤ {z}", lambda i, f, top, z=z: f['impactZ'] <= z)
show("impact z ≥ +1", lambda i, f, top: f['impactZ'] >= 1.0)

print("\n=== G. các thành phần còn lại của bộ điểm (sau chuẩn hoá) ===")
def sw(i, top, n=9):
    if i < n: return False
    return BARS[i]['h'] >= max(BARS[j]['h'] for j in range(i-n, i)) if top \
        else BARS[i]['l'] <= min(BARS[j]['l'] for j in range(i-n, i))
show("swing 9 nến (nến là cực trị của 9 nến trước)", lambda i, f, top: sw(i, top, 9))
show("swing 20 nến", lambda i, f, top: sw(i, top, 20))
show("ô z≥2.5 tại cực trị + swing 9",
     lambda i, f, top: f['best'] and f['best']['z']>=2.5 and f['best']['top']==top and sw(i, top, 9))
show("ô z≥2.5 tại cực trị + twoSided",
     lambda i, f, top: f['best'] and f['best']['z']>=2.5 and f['best']['top']==top and f['best']['twoSided'])
show("ô z≥2.5 tại cực trị + ô chiếm ≥15% vol nến",
     lambda i, f, top: f['best'] and f['best']['z']>=2.5 and f['best']['top']==top and f['best']['lvlShare']>=0.15)

print("\n=== H. đối chứng: ĐẢO CHIỀU có tồn tại ở khung dài hơn? (horizon 60) ===")
def outcome_h(i, short, hor):
    tgt = K_TARGET * MEDR[i]
    if tgt <= 0: return None
    ref = BARS[i]['c']
    for j in range(i+1, min(N, i+hor+1)):
        if short:
            if ref - BARS[j]['l'] >= tgt: return 1
            if BARS[j]['h'] - ref >= tgt: return 0
        else:
            if BARS[j]['h'] - ref >= tgt: return 1
            if ref - BARS[j]['l'] >= tgt: return 0
    return None
for hor in (60, 120):
    w=t=0; w2=t2=0
    for i in range(LB, N-hor):
        if F[i] is None: continue
        for top in (True, False):
            if not is_ext(i, top): continue
            o = outcome_h(i, top, hor)
            if o is None: continue
            t+=1; w+=o
            if F[i]['best'] and F[i]['best']['z']>=2.5 and F[i]['best']['top']==top:
                t2+=1; w2+=o
    print(f"  horizon {hor}: BASE {100*w/max(t,1):.1f}% (n={t})   ô đậm tại cực trị {100*w2/max(t2,1):.1f}% (n={t2})")
