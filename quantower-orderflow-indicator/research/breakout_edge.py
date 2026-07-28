#!/usr/bin/env python3
"""Vòng 5: khai thác hiệu ứng NGƯỢC DẤU — "ô đậm tại cực trị + range hẹp + POC nổi bật ngay mức"
đo được là mức DỄ VỠ (−6,6pp hold-20, 3,7σ). Nếu vậy nó là setup BREAKOUT, không phải hấp thụ.

Đo 3 cách, luôn so với ĐỐI CHỨNG ghép cặp (nến cực trị cục bộ không có tín hiệu):
  1. BREAK RATE  — mức có bị xuyên (close) trong N nến
  2. E[R] breakout — entry stop tại mức ± 1 tick, SL = phía đối diện nến tín hiệu, TP = 2R
  3. ổn định theo tháng + quartile biến động

Chạy: python3 breakout_edge.py [cache.pkl]
"""
import pickle, statistics as st, sys

BARS = pickle.load(open(sys.argv[1] if len(sys.argv) > 1
                        else 'data-export/27-7/perlevel_m1_clean.pkl', 'rb'))
N = len(BARS)
TICK = 0.1
LB = 10
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


print("tính đặc trưng...")
F = [None] * N
MEDR = [0.0] * N
rl, rrange, rbarvol = Robust(BASELINE_BARS), Robust(BASELINE_BARS), Robust(BASELINE_BARS)
for i, b in enumerate(BARS):
    MEDR[i] = rrange.median
    vols = sorted((x[4] for x in b['lvls']), reverse=True)
    if rl.n >= MIN_BARS and MEDR[i] > 0:
        poc = max(b['lvls'], key=lambda x: x[4])
        second = vols[1] if len(vols) > 1 else 0.0
        vmed = rbarvol.median
        cands = []
        for pt, pr, bid, ask, v in b['lvls']:
            if v < MIN_LVL_FLOOR: continue
            z = rl.modz(v)
            if z < 1.0: continue
            near_hi, near_lo = (b['hi_t'] - pt) <= 2, (pt - b['lo_t']) <= 2
            if not (near_hi or near_lo): continue
            top = near_hi and (not near_lo or (b['hi_t'] - pt) <= (pt - b['lo_t']))
            cands.append(dict(z=z, top=top, price=pr, tickIdx=pt,
                              pocDist=abs(poc[0] - pt),
                              pocProm=poc[4] / max(second, 1e-9)))
        best = max(cands, key=lambda c: c['z']) if cands else None
        F[i] = dict(best=best,
                    rangeRatio=(b['h'] - b['l']) / MEDR[i],
                    barVolRatio=b['vol'] / vmed if vmed > 0 else 0)
    rl.add(vols[:3]); rrange.add([b['h'] - b['l']]); rbarvol.add([b['vol']])

mr = sorted(m for m in MEDR if m > 0)
Q = [mr[int(q * (len(mr) - 1))] for q in (0.25, 0.5, 0.75)]
volq = lambda i: 0 if MEDR[i] < Q[0] else 1 if MEDR[i] < Q[1] else 2 if MEDR[i] < Q[2] else 3


def is_ext(i, top):
    if i < LB: return False
    return BARS[i]['h'] >= max(BARS[j]['h'] for j in range(i - LB, i)) if top \
        else BARS[i]['l'] <= min(BARS[j]['l'] for j in range(i - LB, i))


def buf(i):
    return max(2 * TICK, 0.2 * MEDR[i])


def broke(i, price, top, n):
    """mức bị XUYÊN bằng close trong n nến sau"""
    bf = buf(i)
    for j in range(i + 1, min(N, i + n + 1)):
        if top and BARS[j]['c'] > price + bf: return 1
        if not top and BARS[j]['c'] < price - bf: return 0 if False else 1
    return 0


def r_breakout(i, price, top, hor=20, tp_r=2.0):
    """entry stop tại mức ±1 tick theo chiều xuyên; SL = phía đối diện nến tín hiệu.
       Trả None nếu không kích hoạt trong 5 nến."""
    b = BARS[i]
    entry = price + TICK if top else price - TICK
    sl = b['l'] - TICK if top else b['h'] + TICK
    risk = abs(entry - sl)
    if risk <= 0: return None
    tp = entry + tp_r * risk if top else entry - tp_r * risk
    started = None
    for j in range(i + 1, min(N, i + 6)):          # cửa sổ kích hoạt 5 nến
        if (top and BARS[j]['h'] >= entry) or (not top and BARS[j]['l'] <= entry):
            started = j; break
    if started is None: return None
    for j in range(started, min(N, started + hor + 1)):
        hitTp = BARS[j]['h'] >= tp if top else BARS[j]['l'] <= tp
        hitSl = BARS[j]['l'] <= sl if top else BARS[j]['h'] >= sl
        if hitSl: return -1.0                       # tie → SL (bảo thủ)
        if hitTp: return tp_r
    # hết horizon: chốt theo giá close
    last = BARS[min(N - 1, started + hor)]['c']
    return ((last - entry) if top else (entry - last)) / risk


def evaluate(name, cond, n_hold=20):
    sig_break = [0, 0]; ctl_break = [0, 0]
    sig_r = []; ctl_r = []
    per_month = {}
    per_q = {}
    for i in range(LB, N - 40):
        f = F[i]
        if f is None: continue
        for top in (True, False):
            if not is_ext(i, top): continue
            price = BARS[i]['h'] if top else BARS[i]['l']
            hit = cond(i, f, top)
            grp_b = sig_break if hit else ctl_break
            grp_r = sig_r if hit else ctl_r
            grp_b[0] += broke(i, price, top, n_hold); grp_b[1] += 1
            r = r_breakout(i, price, top)
            if r is not None: grp_r.append(r)
            if hit:
                m = BARS[i]['t'][:7]
                per_month.setdefault(m, [0, 0])
                per_month[m][0] += broke(i, price, top, n_hold); per_month[m][1] += 1
                q = volq(i)
                per_q.setdefault(q, [0, 0])
                per_q[q][0] += broke(i, price, top, n_hold); per_q[q][1] += 1
    if sig_break[1] == 0:
        print(f"  {name}: n=0"); return
    sb = 100 * sig_break[0] / sig_break[1]
    cb = 100 * ctl_break[0] / ctl_break[1]
    se = (0.25 / sig_break[1]) ** 0.5 * 100
    print(f"\n  {name}")
    print(f"    BREAK-{n_hold}: tín hiệu {sb:5.1f}% (n={sig_break[1]:5d}) vs đối chứng {cb:5.1f}%"
          f" (n={ctl_break[1]:5d})  →  {sb-cb:+5.1f}pp ({(sb-cb)/se:+.1f}σ)")
    if sig_r and ctl_r:
        print(f"    E[R] breakout: tín hiệu {st.mean(sig_r):+.3f} (n={len(sig_r)})"
              f"  vs đối chứng {st.mean(ctl_r):+.3f} (n={len(ctl_r)})")
    print("    theo tháng: " + "  ".join(
        f"{m}: {100*v[0]/v[1]:.1f}% ({v[1]})" for m, v in sorted(per_month.items())))
    print("    theo quartile biến động: " + "  ".join(
        f"q{q}: {100*v[0]/v[1]:.1f}% ({v[1]})" for q, v in sorted(per_q.items()) if v[1] >= 30))


print(f"nến: {N}  |  quartile median-range: {Q[0]:.2f}/{Q[1]:.2f}/{Q[2]:.2f}")

print("\n=== tổ hợp 'DỄ VỠ' — nới dần để tăng n ===")
evaluate("z≥2.5 + range≤0.9× + pocDist≤3 (bản gốc)",
         lambda i, f, top: f['best'] and f['best']['top'] == top and f['best']['z'] >= 2.5
         and f['rangeRatio'] <= 0.9 and f['best']['pocDist'] <= 3 and f['best']['pocProm'] >= 1.5)
evaluate("z≥2.0 + range≤1.0× + pocDist≤3",
         lambda i, f, top: f['best'] and f['best']['top'] == top and f['best']['z'] >= 2.0
         and f['rangeRatio'] <= 1.0 and f['best']['pocDist'] <= 3 and f['best']['pocProm'] >= 1.5)
evaluate("z≥1.5 + range≤1.0× + pocDist≤3 (bỏ điều kiện POC nổi bật)",
         lambda i, f, top: f['best'] and f['best']['top'] == top and f['best']['z'] >= 1.5
         and f['rangeRatio'] <= 1.0 and f['best']['pocDist'] <= 3)

print("\n=== tách từng yếu tố (xem cái nào tạo ra hiệu ứng) ===")
evaluate("chỉ range hẹp ≤0.9× (bar-level, không cần per-level)",
         lambda i, f, top: f['rangeRatio'] <= 0.9)
evaluate("chỉ POC nằm sát cực trị (pocDist≤3, POC nổi bật)",
         lambda i, f, top: f['best'] and f['best']['top'] == top
         and f['best']['pocDist'] <= 3 and f['best']['pocProm'] >= 1.5)
evaluate("chỉ có ô đậm z≥2.5 tại cực trị",
         lambda i, f, top: f['best'] and f['best']['top'] == top and f['best']['z'] >= 2.5)
