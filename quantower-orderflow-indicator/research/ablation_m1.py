#!/usr/bin/env python3
"""Ablation trên M1 per-level thật: bỏ/đảo từng thành phần của bộ điểm absorption,
và trả lời câu hỏi gốc — PER-LEVEL có thêm giá trị gì so với chỉ dùng volume NẾN?

Chạy: python3 ablation_m1.py
"""
import pickle, statistics as st

TICK = 0.1
BARS = pickle.load(open('data-export/27-7/perlevel_m1.pkl', 'rb'))
N = len(BARS)
TARGET, HORIZON, LB = 1.0, 20, 10
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


def outcome(i, short):
    ref = BARS[i]['c']
    for j in range(i + 1, min(N, i + HORIZON + 1)):
        if short:
            if ref - BARS[j]['l'] >= TARGET: return 1
            if BARS[j]['h'] - ref >= TARGET: return 0
        else:
            if BARS[j]['h'] - ref >= TARGET: return 1
            if ref - BARS[j]['l'] >= TARGET: return 0
    return None


def is_ext(i, top):
    if i < LB: return False
    return BARS[i]['h'] >= max(BARS[j]['h'] for j in range(i - LB, i)) if top \
        else BARS[i]['l'] <= min(BARS[j]['l'] for j in range(i - LB, i))


# ---------------- tính đặc trưng 1 lần cho mọi nến ----------------
print("đang tính đặc trưng per-level...")
feat = [None] * N
rl_top, rl_all = Robust(BASELINE_BARS), Robust(BASELINE_BARS)
rrange, rimpact, rbarvol = Robust(BASELINE_BARS), Robust(BASELINE_BARS), Robust(BASELINE_BARS)
hot = {}
for i, b in enumerate(BARS):
    vols = sorted((x[4] for x in b['lvls']), reverse=True)
    if rl_top.n >= MIN_BARS:
        medt = rl_top.median
        poc = max(b['lvls'], key=lambda x: x[4])
        second = vols[1] if len(vols) > 1 else 0.0
        prom_bar = poc[4] >= 1.5 * max(second, 1e-9)
        rmed, vmed = rrange.median, rbarvol.median
        no_res = rmed > 0 and (b['h'] - b['l']) <= 0.9 * rmed
        if b['vol'] > 0 and rimpact.n >= MIN_BARS:
            no_res = no_res or rimpact.modz(abs(b['c'] - b['o']) / b['vol']) <= -1.0
        hot_now = []
        best = {}
        for pt, pr, bid, ask, v in b['lvls']:
            if v < MIN_LVL_FLOOR: continue
            z = rl_top.modz(v)
            if z < 2.5: continue
            hot_now.append(pt)
            near_hi, near_lo = (b['hi_t'] - pt) <= 2, (pt - b['lo_t']) <= 2
            if not (near_hi or near_lo): continue
            top = near_hi and (not near_lo or (b['hi_t'] - pt) <= (pt - b['lo_t']))
            dpct = (ask - bid) / v
            c = dict(
                effortZ=z, top=top, price=pr,
                noResult=no_res,
                divergence=(dpct >= 0.10) if top else (dpct <= -0.10),
                twoSided=min(bid, ask) >= 0.35 * v,
                prominent=prom_bar and abs(poc[0] - pt) <= 3,
                multi=any(abs(t - pt) <= 2 for j in range(max(0, i - 5), i) for t in hot.get(j, [])),
                pocAtExtreme=min(b['hi_t'] - poc[0], poc[0] - b['lo_t']) <= 2,
                barVolRatio=(b['vol'] / vmed) if vmed > 0 else 0,
            )
            if not best or z > best['effortZ']: best = c
        hot[i] = hot_now
        feat[i] = best or None
        if feat[i] is None:
            feat[i] = dict(effortZ=0, barVolRatio=(b['vol'] / vmed) if vmed > 0 else 0)
    rl_top.add(vols[:3]); rl_all.add(vols)
    rrange.add([b['h'] - b['l']]); rbarvol.add([b['vol']])
    if b['vol'] > 0: rimpact.add([abs(b['c'] - b['o']) / b['vol']])
    if len(hot) > 400:
        for j in [j for j in hot if j < i - 50]: hot.pop(j)


def run(name, cond, need_top_from_feat=True):
    """cond(i, f, top) -> bool"""
    w = t = 0
    for i in range(LB, N - HORIZON):
        f = feat[i]
        if f is None: continue
        for top in (True, False):
            if not is_ext(i, top): continue
            if need_top_from_feat and f.get('effortZ', 0) > 0 and f.get('top') != top: continue
            if not cond(i, f, top): continue
            o = outcome(i, short=top)
            if o is None: continue
            t += 1; w += o
    se = (0.25 / t) ** 0.5 * 100 if t else 0
    hit = 100 * w / t if t else 0
    print(f"  {name:58s} n={t:5d} hit={hit:5.1f}% ±{se:.1f}")
    return hit, t, se


print(f"\nnến: {N}  |  TARGET {TARGET} USD  |  horizon {HORIZON}")
base, bn, bse = run("BASE — mọi nến cực trị cục bộ", lambda i, f, top: True, False)

print("\n--- A. bar-level thuần (KHÔNG dùng per-level) ---")
for k in (1.5, 2.0, 3.0, 5.0):
    run(f"volume NẾN ≥ {k}× median", lambda i, f, top, k=k: f.get('barVolRatio', 0) >= k, False)

print("\n--- B. bộ điểm absorption v3 hiện tại ---")
def score_of(f):
    return 3 + 2 * f['noResult'] + f['prominent'] + 2 * f['divergence'] + f['twoSided'] + 2 * f['multi']
for s in (5, 6, 7, 8):
    run(f"v3: điểm ≥ {s}", lambda i, f, top, s=s: f.get('effortZ', 0) >= 2.5 and score_of(f) >= s)

print("\n--- C. ablation: bỏ từng thành phần khỏi điểm ---")
COMPS = ['noResult', 'prominent', 'divergence', 'twoSided', 'multi']
W = {'noResult': 2, 'prominent': 1, 'divergence': 2, 'twoSided': 1, 'multi': 2}
for drop in [None] + COMPS:
    def sc(f, drop=drop):
        return 3 + sum(W[c] * f[c] for c in COMPS if c != drop)
    lbl = "giữ tất cả" if drop is None else f"BỎ {drop}"
    run(f"{lbl} (ngưỡng 6)", lambda i, f, top, sc=sc: f.get('effortZ', 0) >= 2.5 and sc(f) >= 6)

print("\n--- D. đảo dấu các thành phần đang gây hại ---")
run("EFFORT + cực trị + KHÔNG prominent", lambda i, f, top: f.get('effortZ', 0) >= 2.5 and not f['prominent'])
run("EFFORT + cực trị + KHÔNG noResult", lambda i, f, top: f.get('effortZ', 0) >= 2.5 and not f['noResult'])
run("EFFORT + cực trị + KHÔNG prominent + KHÔNG noResult",
    lambda i, f, top: f.get('effortZ', 0) >= 2.5 and not f['prominent'] and not f['noResult'])
run("EFFORT + POC KHÔNG ở cực trị (POC giữa nến)",
    lambda i, f, top: f.get('effortZ', 0) >= 2.5 and not f.get('pocAtExtreme', False))

print("\n--- E. câu hỏi gốc: per-level THÊM gì cho volume nến cao? ---")
run("volume nến ≥3× (nhắc lại)", lambda i, f, top: f.get('barVolRatio', 0) >= 3, False)
run("volume nến ≥3×  VÀ  có ô EFFORT z≥2.5 tại cực trị",
    lambda i, f, top: f.get('barVolRatio', 0) >= 3 and f.get('effortZ', 0) >= 2.5)
run("volume nến ≥3×  VÀ  KHÔNG có ô EFFORT tại cực trị",
    lambda i, f, top: f.get('barVolRatio', 0) >= 3 and f.get('effortZ', 0) < 2.5, False)
run("volume nến ≥3×  VÀ  ô cực trị divergence",
    lambda i, f, top: f.get('barVolRatio', 0) >= 3 and f.get('effortZ', 0) >= 2.5 and f.get('divergence', False))
print(f"\n(base = {base:.1f}% ±{bse:.1f}, n={bn})")
