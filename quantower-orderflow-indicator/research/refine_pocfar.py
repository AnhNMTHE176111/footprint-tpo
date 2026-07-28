#!/usr/bin/env python3
"""Vòng 2: đào sâu phát hiện của ablation — "ô đậm tại cực trị + POC ở XA cực trị".

Cơ chế: giá chạm tới một mức, bị chặn ở đó, nhưng phần lớn giao dịch của nến diễn ra XA mức đó
→ cực trị là nơi bị TỪ CHỐI. Nếu POC nằm ngay cực trị thì thị trường đang CHẤP NHẬN giá đó
(xây value) → tiếp diễn, không phải hấp thụ. Bản v3 cộng điểm cho POC-gần-cực-trị = SAI DẤU.

Kiểm: tách "POC xa" vs "POC không nổi bật", quét ngưỡng, và IN-SAMPLE (T5-6) vs OUT-OF-SAMPLE (T7).
Chạy: python3 refine_pocfar.py
"""
import pickle, statistics as st

TICK = 0.1
BARS = pickle.load(open('data-export/27-7/perlevel_m1.pkl', 'rb'))
N = len(BARS)
TARGET, HORIZON, LB = 1.0, 20, 10
BASELINE_BARS, MIN_BARS, MIN_LVL_FLOOR = 100, 40, 5
SPLIT = '2026-07-01'          # < SPLIT = in-sample, >= SPLIT = out-of-sample


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


# ---------------- đặc trưng ----------------
print("tính đặc trưng...")
F = [None] * N
rl, rrange, rbarvol = Robust(BASELINE_BARS), Robust(BASELINE_BARS), Robust(BASELINE_BARS)
for i, b in enumerate(BARS):
    vols = sorted((x[4] for x in b['lvls']), reverse=True)
    if rl.n >= MIN_BARS:
        poc = max(b['lvls'], key=lambda x: x[4])
        second = vols[1] if len(vols) > 1 else 0.0
        rmed, vmed = rrange.median, rbarvol.median
        span = max(b['hi_t'] - b['lo_t'], 1)
        cands = []
        for pt, pr, bid, ask, v in b['lvls']:
            if v < MIN_LVL_FLOOR: continue
            z = rl.modz(v)
            if z < 1.5: continue
            near_hi, near_lo = (b['hi_t'] - pt) <= 2, (pt - b['lo_t']) <= 2
            if not (near_hi or near_lo): continue
            top = near_hi and (not near_lo or (b['hi_t'] - pt) <= (pt - b['lo_t']))
            dpct = (ask - bid) / v
            cands.append(dict(
                z=z, top=top, price=pr, tickIdx=pt,
                pocDist=abs(poc[0] - pt),                       # khoảng cách POC → ô tín hiệu (tick)
                pocDistRel=abs(poc[0] - pt) / span,             # ... theo tỉ lệ range nến
                pocProm=poc[4] / max(second, 1e-9),
                pocAtExtreme=min(b['hi_t'] - poc[0], poc[0] - b['lo_t']) <= 2,
                rangeRatio=(b['h'] - b['l']) / rmed if rmed > 0 else 0,
                barVolRatio=b['vol'] / vmed if vmed > 0 else 0,
                divergence=(dpct >= 0.10) if top else (dpct <= -0.10),
                lvlShare=v / b['vol'] if b['vol'] > 0 else 0,   # ô này chiếm bao nhiêu % volume nến
                span=span,
            ))
        F[i] = max(cands, key=lambda c: c['z']) if cands else None
    rl.add(vols[:3]); rrange.add([b['h'] - b['l']]); rbarvol.add([b['vol']])


def run(name, cond, quiet=False):
    res = {}
    for tag in ('IS', 'OOS'):
        w = t = 0
        for i in range(LB, N - HORIZON):
            f = F[i]
            if f is None: continue
            is_oos = BARS[i]['t'][:10] >= SPLIT
            if (tag == 'OOS') != is_oos: continue
            top = f['top']
            if not is_ext(i, top): continue
            if not cond(f): continue
            o = outcome(i, short=top)
            if o is None: continue
            t += 1; w += o
        res[tag] = (100 * w / t if t else 0, t, (0.25 / t) ** 0.5 * 100 if t else 0)
    if not quiet:
        a, an, ase = res['IS']; b_, bn, bse = res['OOS']
        print(f"  {name:52s} IS: {a:5.1f}% ±{ase:4.1f} (n={an:5d})   OOS: {b_:5.1f}% ±{bse:4.1f} (n={bn:4d})")
    return res


def base_of():
    out = {}
    for tag in ('IS', 'OOS'):
        w = t = 0
        for i in range(LB, N - HORIZON):
            is_oos = BARS[i]['t'][:10] >= SPLIT
            if (tag == 'OOS') != is_oos: continue
            for top in (True, False):
                if not is_ext(i, top): continue
                o = outcome(i, short=top)
                if o is None: continue
                t += 1; w += o
        out[tag] = (100 * w / t, t)
    return out


B = base_of()
print(f"\nBASE  IS: {B['IS'][0]:.1f}% (n={B['IS'][1]})   OOS: {B['OOS'][0]:.1f}% (n={B['OOS'][1]})")
print(f"chia: IS = trước {SPLIT}, OOS = từ {SPLIT}\n")

print("--- 1. tách hai yếu tố: POC XA vs POC KHÔNG nổi bật (effort z≥2.5) ---")
run("chỉ EFFORT z≥2.5 tại cực trị (không lọc gì)", lambda f: f['z'] >= 2.5)
run("+ POC xa ô tín hiệu > 3 tick", lambda f: f['z'] >= 2.5 and f['pocDist'] > 3)
run("+ POC KHÔNG nổi bật (<1.5× ô nhì)", lambda f: f['z'] >= 2.5 and f['pocProm'] < 1.5)
run("+ POC không ở cực trị nào (cách 2 biên >2)", lambda f: f['z'] >= 2.5 and not f['pocAtExtreme'])

print("\n--- 2. quét khoảng cách POC (tick) ---")
for d in (0, 2, 3, 5, 8, 12):
    run(f"EFFORT z≥2.5 + pocDist > {d}", lambda f, d=d: f['z'] >= 2.5 and f['pocDist'] > d)

print("\n--- 3. quét theo tỉ lệ range nến (bền vững hơn với biến động) ---")
for r in (0.3, 0.5, 0.6, 0.75):
    run(f"EFFORT z≥2.5 + pocDistRel > {r}", lambda f, r=r: f['z'] >= 2.5 and f['pocDistRel'] > r)

print("\n--- 4. quét EFFORT z (giữ pocDist > 3) ---")
for z in (1.5, 2.0, 2.5, 3.0, 4.0):
    run(f"EFFORT z≥{z} + pocDist>3", lambda f, z=z: f['z'] >= z and f['pocDist'] > 3)

print("\n--- 5. thêm/bớt điều kiện quanh cấu hình lõi (z≥2.5, pocDist>3) ---")
core = lambda f: f['z'] >= 2.5 and f['pocDist'] > 3
run("lõi + delta divergence", lambda f: core(f) and f['divergence'])
run("lõi + KHÔNG divergence", lambda f: core(f) and not f['divergence'])
run("lõi + range nến ≥ 1.0× median", lambda f: core(f) and f['rangeRatio'] >= 1.0)
run("lõi + range nến ≤ 0.9× median (kiểu VSA)", lambda f: core(f) and f['rangeRatio'] <= 0.9)
run("lõi + volume nến ≥ 2× median", lambda f: core(f) and f['barVolRatio'] >= 2)
run("lõi + volume nến ≥ 3× median", lambda f: core(f) and f['barVolRatio'] >= 3)
run("lõi + ô chiếm ≥ 15% volume nến", lambda f: core(f) and f['lvlShare'] >= 0.15)
run("lõi + nến rộng ≥ 8 tick", lambda f: core(f) and f['span'] >= 8)

print("\n--- 6. ứng viên tổng hợp ---")
run("z≥2.5 + pocDist>3 + range≥1.0× + vol nến≥2×",
    lambda f: core(f) and f['rangeRatio'] >= 1.0 and f['barVolRatio'] >= 2)
run("z≥2.5 + pocDistRel>0.5 + vol nến≥2×",
    lambda f: f['z'] >= 2.5 and f['pocDistRel'] > 0.5 and f['barVolRatio'] >= 2)
run("z≥2.0 + pocDist>3 + vol nến≥1.5×",
    lambda f: f['z'] >= 2.0 and f['pocDist'] > 3 and f['barVolRatio'] >= 1.5)
