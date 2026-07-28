#!/usr/bin/env python3
"""Vòng 3: kiểm hiệu ứng "vị trí POC trong nến" bằng BIN trên toàn bộ nến cực trị (n lớn).

Ngưỡng rời rạc + nhiều biến thể = dễ overfit. Ở đây đo quan hệ LIÊN TỤC:
  pocPos = (poc_tick − lo_t) / (hi_t − lo_t)   ∈ [0,1]   (0 = POC ở đáy nến, 1 = POC ở đỉnh)
Với setup SHORT (nến là đỉnh cục bộ): pocRel = pocPos  (1 = POC ngay tại đỉnh)
Với setup LONG  (nến là đáy cục bộ):  pocRel = 1 − pocPos
Giả thuyết: pocRel THẤP (POC ở xa cực trị) → đảo chiều tốt; pocRel CAO → tiếp diễn.
Hiệu ứng thật thì phải ĐƠN ĐIỆU và ổn định qua từng tháng.

Chạy: python3 pocpos_monotonic.py
"""
import pickle, statistics as st
from collections import defaultdict

BARS = pickle.load(open('data-export/27-7/perlevel_m1.pkl', 'rb'))
N = len(BARS)
TARGET, HORIZON, LB = 1.0, 20, 10


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


# đặc trưng nến (không cần baseline → dùng được mọi nến)
print("tính pocPos...")
POC = [None] * N
for i, b in enumerate(BARS):
    span = b['hi_t'] - b['lo_t']
    if span <= 0 or not b['lvls']: continue
    poc = max(b['lvls'], key=lambda x: x[4])
    vols = sorted((x[4] for x in b['lvls']), reverse=True)
    POC[i] = dict(pos=(poc[0] - b['lo_t']) / span,
                  prom=poc[4] / max(vols[1] if len(vols) > 1 else 0.0, 1e-9),
                  span=span, vol=b['vol'])

# thu thập mẫu
samples = []      # (month, pocRel, prom, span, vol, win)
for i in range(LB, N - HORIZON):
    p = POC[i]
    if p is None: continue
    for top in (True, False):
        if not is_ext(i, top): continue
        o = outcome(i, short=top)
        if o is None: continue
        rel = p['pos'] if top else 1 - p['pos']
        samples.append((BARS[i]['t'][:7], rel, p['prom'], p['span'], p['vol'], o))

print(f"mẫu: {len(samples)}")


def table(rows, key, bins, label, fmt="{:.2f}"):
    print(f"\n--- {label} ---")
    hdr = f"{'nhóm':>16} {'n':>6} {'hit':>7} {'±se':>5}"
    months = sorted({r[0] for r in rows})
    for m in months: hdr += f" {m:>9}"
    print(hdr)
    edges = bins + [float('inf')]
    for a, b in zip([-float('inf')] + bins, edges):
        sel = [r for r in rows if a <= key(r) < b]
        if not sel: continue
        n = len(sel); w = sum(r[5] for r in sel)
        se = (0.25 / n) ** 0.5 * 100
        line = f"{('[' + fmt.format(a) if a != -float('inf') else '[-inf') + ',' + (fmt.format(b) if b != float('inf') else 'inf') + ')':>16}" \
               f" {n:6d} {100*w/n:6.1f}% {se:4.1f}"
        for m in months:
            s2 = [r for r in sel if r[0] == m]
            line += f" {100*sum(r[5] for r in s2)/len(s2):8.1f}%" if len(s2) >= 30 else f" {'-':>9}"
        print(line)


allw = sum(r[5] for r in samples); alln = len(samples)
print(f"BASE tổng: {100*allw/alln:.1f}%  (n={alln})")
for m in sorted({r[0] for r in samples}):
    s = [r for r in samples if r[0] == m]
    print(f"   {m}: {100*sum(r[5] for r in s)/len(s):.1f}%  (n={len(s)})")

table(samples, lambda r: r[1], [0.2, 0.4, 0.6, 0.8],
      "pocRel = khoảng cách POC tới cực trị đang xét (0 = POC ở XA, 1 = POC NGAY cực trị)")

table(samples, lambda r: r[2], [1.2, 1.5, 2.0, 3.0],
      "độ nổi bật POC (poc / ô nhì)", "{:.1f}")

# tương tác: pocRel × độ rộng nến (nến hẹp thì pocRel nhiễu)
print("\n--- pocRel × độ rộng nến (tick) ---")
for lo, hi in ((1, 5), (5, 10), (10, 20), (20, 10**9)):
    sel = [r for r in samples if lo <= r[3] < hi]
    if len(sel) < 100: continue
    print(f"  nến rộng {lo}-{hi if hi < 10**9 else '∞'} tick (n={len(sel)}):", end='')
    for a, b in ((0, 0.34), (0.34, 0.67), (0.67, 1.01)):
        s2 = [r for r in sel if a <= r[1] < b]
        if len(s2) < 50: print(f"   [{a:.2f},{b:.2f}) n<50", end=''); continue
        print(f"   [{a:.2f},{b:.2f}) {100*sum(r[5] for r in s2)/len(s2):.1f}% (n={len(s2)})", end='')
    print()

# chỉ nến đủ rộng + kiểm theo tháng
print("\n--- CHỐT: nến rộng ≥ 8 tick, chia theo pocRel, từng tháng ---")
sel = [r for r in samples if r[3] >= 8]
table(sel, lambda r: r[1], [0.25, 0.5, 0.75], f"nến ≥8 tick (n={len(sel)})")
