#!/usr/bin/env python3
"""Kiểm định ABSORPTION bằng NHIỀU ĐỊNH NGHĨA OUTCOME (không chỉ "đảo 1 USD trong 20 nến").

Giả thuyết: absorption theo sách KHÔNG phải tín hiệu vào lệnh tức thì — nó XÁC NHẬN
một MỨC GIÁ (S/R). Vậy phải đo "mức đó có giữ được không", chứ không phải "giá có
đảo ngay không".

Chạy:  python3 quantower-orderflow-indicator/research/outcome_variants.py

Bộ tín hiệu: copy nguyên hàm analyse() của calibrate_perlevel.py
(baseline top-3 ô, EFFORT z 2.5, bigZ 3.0, bigMult 4.0) → mỗi nến tối đa 1 tín hiệu
(ô điểm cao nhất), kèm: top (absorption đỉnh / đáy), giá ô, điểm 3..12.

4 phép đo:
  1. LEVEL HOLD  — mức có bị xuyên (close / wick) trong N=5/10/20/60 nến?
  2. MFE/MAE + R kỳ vọng — vào tại close, SL = mức ± 2 tick.
  3. Ma trận TARGET × HORIZON (chiều ĐẢO CHIỀU).
  4. Cùng ma trận cho chiều TIẾP DIỄN.
Mọi bảng đều có NHÓM ĐỐI CHỨNG = nến cực trị cục bộ 10 nến KHÔNG có absorption.
"""
import pickle, statistics as st, sys
from collections import defaultdict

TICK = 0.1
BUF = 2 * TICK                      # ngưỡng "xuyên mức"
PKL = 'data-export/27-7/perlevel_m1.pkl'
BASELINE_BARS, MIN_BARS, MIN_LVL_FLOOR = 100, 40, 5
TARGETS = (0.5, 1.0, 2.0, 3.0)      # target USD tuyệt đối (KHÔNG chuẩn hoá — chỉ để tham chiếu)
NKS = (1.0, 2.0, 3.0)               # target CHUẨN HOÁ = k × median(range 100 nến trước)
HORIZONS = (10, 20, 60, 120)
HOLD_NS = (5, 10, 20, 60)
RKS = (1, 2, 3)
VOLLB = 100                         # cửa sổ chuẩn hoá biến động
BRK_FRAC = 0.2                      # ngưỡng xuyên động = max(2 tick, 0.2 × median range)
MAXW = max(HORIZONS)                # số nến nhìn về trước tối đa
EXTLB = 10                          # cực trị cục bộ = cao/thấp nhất 10 nến trước


def se(n):
    return (0.25 / max(n, 1)) ** 0.5 * 100


# ---------------------------------------------------------------- copy từ calibrate_perlevel.py
class Robust:
    def __init__(s, w): s.w, s.bars, s._c = w, [], None
    def add(s, vals):
        s.bars.append(list(vals))
        if len(s.bars) > s.w: s.bars.pop(0)
        s._c = None
    def stats(s):
        if s._c: return s._c
        allv = [x for b in s.bars for x in b]
        if not allv: s._c = (0.0, 0.0); return s._c
        m = st.median(allv)
        s._c = (m, st.median([abs(x - m) for x in allv])); return s._c
    def modz(s, x):
        m, mad = s.stats()
        if mad > 1e-9: return 0.6745 * (x - m) / mad
        if m > 1e-9: return (x - m) / m
        return 0.0
    @property
    def median(s): return s.stats()[0]
    @property
    def n(s): return len(s.bars)


def analyse(bars, top_k, eff_z, big_z, big_mult, max_displ=2, swing=9, poc_prom=1.5,
            div_pct=0.10, two_sided=0.35, multi_lb=5, range_ratio=0.9, impact_z=1.0):
    rl, rrange, rimpact = Robust(BASELINE_BARS), Robust(BASELINE_BARS), Robust(BASELINE_BARS)
    hot = {}
    fires = {'big': 0, 'abs': 0, 'bars': 0}
    recs = []
    for i, b in enumerate(bars):
        vols = sorted((x[4] for x in b['lvls']), reverse=True)
        if rl.n >= MIN_BARS:
            fires['bars'] += 1
            med = rl.median
            poc = max(b['lvls'], key=lambda x: x[4])
            pocv = poc[4]
            second = vols[1] if len(vols) > 1 else 0.0
            prom_bar = pocv >= poc_prom * max(second, 1e-9)
            rmed = rrange.median
            no_res = (rmed > 0 and (b['h'] - b['l']) <= range_ratio * rmed)
            if b['vol'] > 0 and rimpact.n >= MIN_BARS:
                no_res = no_res or rimpact.modz(abs(b['c'] - b['o']) / b['vol']) <= -impact_z
            sw_hi = swing <= 0 or all(b['h'] >= bars[j]['h'] for j in range(max(0, i - swing), i))
            sw_lo = swing <= 0 or all(b['l'] <= bars[j]['l'] for j in range(max(0, i - swing), i))

            hot_now, big_hit, best = [], False, None
            for pt, pr, bid, ask, v in b['lvls']:
                if v < MIN_LVL_FLOOR: continue
                z = rl.modz(v)
                if z >= big_z and (big_mult <= 0 or v >= big_mult * med): big_hit = True
                if z < eff_z: continue
                hot_now.append(pt)
                near_hi, near_lo = (b['hi_t'] - pt) <= max_displ, (pt - b['lo_t']) <= max_displ
                if not (near_hi or near_lo): continue
                top = near_hi and (not near_lo or (b['hi_t'] - pt) <= (pt - b['lo_t']))
                dpct = (ask - bid) / v
                comp = dict(
                    noResult=no_res,
                    divergence=(dpct >= div_pct) if top else (dpct <= -div_pct),
                    twoSided=min(bid, ask) >= two_sided * v,
                    prominent=prom_bar and abs(poc[0] - pt) <= max_displ + 1,
                    swing=sw_hi if top else sw_lo,
                    multi=any(abs(t - pt) <= 2 for j in range(max(0, i - multi_lb), i)
                              for t in hot.get(j, [])),
                )
                score = 3 + 2 * comp['noResult'] + comp['swing'] + comp['prominent'] \
                    + 2 * comp['divergence'] + comp['twoSided'] + 2 * comp['multi']
                if best is None or score > best[0]: best = (score, top, comp, pr)
            hot[i] = hot_now
            if big_hit: fires['big'] += 1
            if best: fires['abs'] += 1; recs.append((i, best[0], best[1], best[2], best[3]))
        rl.add(vols[:top_k] if top_k > 0 else vols)
        rrange.add([b['h'] - b['l']])
        if b['vol'] > 0: rimpact.add([abs(b['c'] - b['o']) / b['vol']])
        if len(hot) > 400:
            for j in [j for j in hot if j < i - 50]: hot.pop(j)
    return fires, recs


# ---------------------------------------------------------------- một lần đi về trước / tín hiệu
def forward(bars, i, top, level, entry, rmed):
    """Đi tối đa MAXW nến, ghi lại MỌI mốc cần cho cả 4 phép đo (1 vòng lặp).

    rmed = median range 100 nến trước i → dùng cho target chuẩn hoá & ngưỡng xuyên động.
    """
    n = len(bars)
    end = min(n, i + 1 + MAXW)
    walked = end - (i + 1)
    up_hit = {t: None for t in TARGETS}       # high - entry >= t (chiều lên)
    dn_hit = {t: None for t in TARGETS}       # entry - low  >= t (chiều xuống)
    nt = {k: max(k * rmed, TICK) for k in NKS}   # target chuẩn hoá theo biến động
    nup_hit = {k: None for k in NKS}
    ndn_hit = {k: None for k in NKS}
    dbuf = max(BUF, BRK_FRAC * rmed)          # ngưỡng xuyên CHUẨN HOÁ
    brk_close = {N: 0 for N in HOLD_NS}       # 1 = mức bị xuyên bằng CLOSE trong N nến (buf cố định)
    brk_wick = {N: 0 for N in HOLD_NS}
    brk_dc = {N: 0 for N in HOLD_NS}          # xuyên CLOSE với buf động
    brk_dw = {N: 0 for N in HOLD_NS}
    # SL = mức absorption ± 2 tick ; risk có sàn 2 tick để R không nổ
    sl = level + BUF if top else level - BUF
    risk_raw = (sl - entry) if top else (entry - sl)
    floored = risk_raw < BUF
    risk = max(risk_raw, BUF)
    stop_j = None
    rtgt_j = {k: None for k in RKS}           # chạm k*risk theo chiều ĐẢO CHIỀU
    mfe = {N: 0.0 for N in (20, 60)}          # excursion thuận chiều đảo chiều
    mae = {N: 0.0 for N in (20, 60)}
    lastc = {N: None for N in (20, 60)}
    for j in range(i + 1, end):
        d = j - i
        bj = bars[j]
        up, dn = bj['h'] - entry, entry - bj['l']
        for t in TARGETS:
            if up_hit[t] is None and up >= t: up_hit[t] = d
            if dn_hit[t] is None and dn >= t: dn_hit[t] = d
        for k in NKS:
            if nup_hit[k] is None and up >= nt[k]: nup_hit[k] = d
            if ndn_hit[k] is None and dn >= nt[k]: ndn_hit[k] = d
        fav, adv = (dn, up) if top else (up, dn)
        for N in (20, 60):
            if d <= N:
                if fav > mfe[N]: mfe[N] = fav
                if adv > mae[N]: mae[N] = adv
                lastc[N] = bj['c']
        # xuyên mức
        cv = bj['c']
        wv = bj['h'] if top else bj['l']
        b_c = (cv > level + BUF) if top else (cv < level - BUF)
        b_w = (wv > level + BUF) if top else (wv < level - BUF)
        d_c = (cv > level + dbuf) if top else (cv < level - dbuf)
        d_w = (wv > level + dbuf) if top else (wv < level - dbuf)
        for N in HOLD_NS:
            if d <= N:
                if b_c: brk_close[N] = 1
                if b_w: brk_wick[N] = 1
                if d_c: brk_dc[N] = 1
                if d_w: brk_dw[N] = 1
        # đường đi có SL
        if stop_j is None and adv >= risk: stop_j = d
        for k in RKS:
            if rtgt_j[k] is None and fav >= k * risk: rtgt_j[k] = d
    return dict(i=i, top=top, level=level, entry=entry, walked=walked, rmed=rmed,
                up=up_hit, dn=dn_hit, nup=nup_hit, ndn=ndn_hit,
                brk_c=brk_close, brk_w=brk_wick, brk_dc=brk_dc, brk_dw=brk_dw,
                risk=risk, floored=floored, stop=stop_j, rt=rtgt_j,
                mfe=mfe, mae=mae, lastc=lastc, month=bars[i]['t'][5:7])


def grid_out(f, target, H, reverse=True, norm=False):
    """Thắng/thua theo target & horizon. reverse=True: chiều đảo chiều.
    norm=True → target là hệ số k của median range 100 nến."""
    if f['walked'] < H: return None
    if norm:
        fav = f['ndn'] if f['top'] else f['nup']
        adv = f['nup'] if f['top'] else f['ndn']
    else:
        fav = f['dn'] if f['top'] else f['up']
        adv = f['up'] if f['top'] else f['dn']
    if not reverse: fav, adv = adv, fav
    a, b = fav[target], adv[target]
    a = a if (a is not None and a <= H) else None
    b = b if (b is not None and b <= H) else None
    if a is None and b is None: return None
    if a is None: return 0
    if b is None: return 1
    return 1 if a <= b else 0        # cùng nến → tính THẮNG (đúng quy ước script cũ)


def pct(w, t):
    return 100 * w / max(t, 1)


def row(name, w, t):
    return f"{name:<26} n={t:>6}  {pct(w,t):5.1f}% ±{se(t):.1f}"


# ---------------------------------------------------------------- nạp & dựng nhóm
print("nạp cache…", file=sys.stderr)
bars = pickle.load(open(PKL, 'rb'))
n = len(bars)
print(f"=== DỮ LIỆU === {n} nến M1  ({bars[0]['t']} → {bars[-1]['t']})")

print("chạy indicator…", file=sys.stderr)
fires, recs = analyse(bars, 3, 2.5, 3.0, 4.0)
print(f"tín hiệu absorption: {len(recs)}  ({pct(fires['abs'], fires['bars']):.1f}% số nến hợp lệ)")

# cực trị cục bộ 10 nến
ext_hi = [False] * n
ext_lo = [False] * n
for i in range(EXTLB, n):
    ext_hi[i] = bars[i]['h'] >= max(bars[j]['h'] for j in range(i - EXTLB, i))
    ext_lo[i] = bars[i]['l'] <= min(bars[j]['l'] for j in range(i - EXTLB, i))

# median range 100 nến TRƯỚC i → chuẩn hoá biến động (tháng 5/6/7 chênh 3-4× volume)
RMED = [0.0] * n
win = []
for i in range(n):
    RMED[i] = st.median(win) if len(win) >= 20 else 0.0
    win.append(bars[i]['h'] - bars[i]['l'])
    if len(win) > VOLLB: win.pop(0)
print(f"median range 100 nến: T5 {st.median([RMED[i] for i in range(n) if bars[i]['t'][5:7]=='05' and RMED[i]>0]):.2f}"
      f"  T6 {st.median([RMED[i] for i in range(n) if bars[i]['t'][5:7]=='06' and RMED[i]>0]):.2f}"
      f"  T7 {st.median([RMED[i] for i in range(n) if bars[i]['t'][5:7]=='07' and RMED[i]>0]):.2f} USD")

abs_by_bar = {}
for i, score, top, comp, pr in recs:
    abs_by_bar[i] = (top, pr, score, comp)

print("đo outcome…", file=sys.stderr)
# nhóm 1: MỌI tín hiệu absorption (mức = giá ô absorption)
A_ALL, A_EXT, A_ALL_X, CTRL = [], [], [], []
for i, score, top, comp, pr in recs:
    if i < EXTLB or i >= n - 1 or RMED[i] <= 0: continue
    f = forward(bars, i, top, pr, bars[i]['c'], RMED[i])
    f['score'] = score; f['comp'] = comp
    A_ALL.append(f)
    if (ext_hi[i] if top else ext_lo[i]):
        A_EXT.append(f)
        # cùng tín hiệu nhưng mức = CỰC TRỊ NẾN (so sánh táo-với-táo với đối chứng)
        g = forward(bars, i, top, bars[i]['h'] if top else bars[i]['l'], bars[i]['c'], RMED[i])
        g['score'] = score; g['comp'] = comp
        A_ALL_X.append(g)

# nhóm đối chứng: nến cực trị cục bộ KHÔNG có absorption (cùng chiều), mức = cực trị nến
for i in range(EXTLB, n - 1):
    if RMED[i] <= 0: continue
    sig = abs_by_bar.get(i)
    for top in (True, False):
        if not (ext_hi[i] if top else ext_lo[i]): continue
        if sig and sig[0] == top: continue          # có absorption cùng chiều → không phải đối chứng
        CTRL.append(forward(bars, i, top, bars[i]['h'] if top else bars[i]['l'], bars[i]['c'], RMED[i]))

GROUPS = [('ABS mọi tín hiệu (giá ô)', A_ALL),
          ('ABS tại cực trị (giá ô)', A_EXT),
          ('ABS tại cực trị (cực trị nến)', A_ALL_X),
          ('ĐỐI CHỨNG cực trị, ko abs', CTRL)]
for name, g in GROUPS:
    print(f"  {name:<32} n={len(g)}")

# ---------------------------------------------------------------- 1. LEVEL HOLD
print("\n=== 1. LEVEL HOLD — mức KHÔNG bị xuyên (mức ± 2 tick) trong N nến ===")
print("(absorption đỉnh: xuyên = close/wick > mức + 2 tick; đáy: ngược lại)")
for mode, key in (('CLOSE, buf 2 tick', 'brk_c'), ('WICK, buf 2 tick', 'brk_w'),
                  ('CLOSE, buf CHUẨN HOÁ = max(2tick, 0.2×medRange)', 'brk_dc'),
                  ('WICK, buf CHUẨN HOÁ', 'brk_dw')):
    print(f"\n-- xuyên bằng {mode} --")
    print(f"{'nhóm':<32}" + ''.join(f"{'N='+str(N):>15}" for N in HOLD_NS))
    for name, g in GROUPS:
        cells = []
        for N in HOLD_NS:
            gg = [f for f in g if f['walked'] >= N]
            hold = sum(1 for f in gg if not f[key][N])
            cells.append(f"{pct(hold,len(gg)):6.1f}%±{se(len(gg)):3.1f}")
        print(f"{name:<32}" + ''.join(f"{c:>15}" for c in cells)
              + f"   n≈{len([f for f in g if f['walked']>=HOLD_NS[-1]])}")

print("\n-- HOLD (close, buf CHUẨN HOÁ, N=20) theo ĐIỂM absorption, mức = giá ô, mọi tín hiệu --")
by_s = defaultdict(lambda: [0, 0])
for f in A_ALL:
    if f['walked'] < 20: continue
    by_s[f['score']][0] += (0 if f['brk_dc'][20] else 1); by_s[f['score']][1] += 1
cw = ct = 0
for s in sorted(by_s, reverse=True):
    w, t = by_s[s]; cw += w; ct += t
    print(f"  điểm ≥{s:2d}: n={ct:6d}  hold={pct(cw,ct):5.1f}% ±{se(ct):.1f}"
          f"   (riêng {s}: n={t}, {pct(w,t):.1f}%)")
ctrl20 = [f for f in CTRL if f['walked'] >= 20]
print(f"  ĐỐI CHỨNG : n={len(ctrl20)}  hold={pct(sum(1 for f in ctrl20 if not f['brk_dc'][20]), len(ctrl20)):5.1f}%"
      f" ±{se(len(ctrl20)):.1f}")

# ---------------------------------------------------------------- 2. MFE / MAE / R
print("\n=== 2. MFE/MAE — vào tại close chiều ĐẢO CHIỀU, SL = mức ± 2 tick ===")
print("MFE/MAE tính theo USD và theo R (R = khoảng cách entry→SL).")
for N in (20, 60):
    print(f"\n-- horizon {N} nến --")
    print(f"{'nhóm':<32}{'risk med':>9}{'MFE med':>9}{'MAE med':>9}{'MFE/R':>7}{'MAE/R':>7}"
          f"{'≥1R':>7}{'≥2R':>7}{'≥3R':>7}{'E[R]|1R':>9}{'E[R]|2R':>9}{'E[R]|3R':>9}{'n':>7}")
    for name, g in GROUPS:
        gg = [f for f in g if f['walked'] >= N]
        if not gg: continue
        risks = [f['risk'] for f in gg]
        mfes = [f['mfe'][N] for f in gg]
        maes = [f['mae'][N] for f in gg]
        mfr = st.mean(f['mfe'][N] / f['risk'] for f in gg)
        mar = st.mean(f['mae'][N] / f['risk'] for f in gg)
        hits, ers, ers_c = [], [], []
        for k in RKS:
            # đường đi thật: chạm k*risk trước khi bị SL trong N nến?
            # tie = TP và SL rơi CÙNG nến M1 → 'win' (lạc quan) vs 'stop' (bảo thủ)
            wins = tot = 0; rs = []; rs_c = []
            for f in gg:
                tj, sj = f['rt'][k], f['stop']
                tj = tj if (tj is not None and tj <= N) else None
                sj = sj if (sj is not None and sj <= N) else None
                tot += 1
                c = f['lastc'][N]
                mtm = ((f['entry'] - c) if f['top'] else (c - f['entry'])) / f['risk']
                if tj is not None and (sj is None or tj <= sj):
                    wins += 1; rs.append(k)
                elif sj is not None: rs.append(-1.0)
                else: rs.append(mtm)
                if tj is not None and (sj is None or tj < sj): rs_c.append(k)
                elif sj is not None: rs_c.append(-1.0)
                else: rs_c.append(mtm)
            hits.append(pct(wins, tot)); ers.append(st.mean(rs)); ers_c.append(st.mean(rs_c))
        print(f"{name:<32}{st.median(risks):9.2f}{st.median(mfes):9.2f}{st.median(maes):9.2f}"
              f"{mfr:7.2f}{mar:7.2f}" + ''.join(f"{h:6.1f}%" for h in hits)
              + ''.join(f"{e:+9.3f}" for e in ers) + f"{len(gg):7d}"
              + '  | bảo thủ ' + ' '.join(f"{e:+.3f}" for e in ers_c))
fl = sum(1 for f in A_ALL if f['floored'])
print(f"\n(risk bị áp sàn 2 tick vì close đã vượt mức: ABS {pct(fl,len(A_ALL)):.1f}% "
      f"({fl}/{len(A_ALL)}) | ĐỐI CHỨNG {pct(sum(1 for f in CTRL if f['floored']),len(CTRL)):.1f}%)")

# ---------------------------------------------------------------- 3 & 4. TARGET × HORIZON
def matrix(title, tlist, norm, rev):
    print(f"\n=== {title} ===")
    print("mỗi ô: ABS% (n) | ĐỐI CHỨNG% | chênh pp ±se(abs)")
    for name, g in (('ABS mọi tín hiệu', A_ALL), ('ABS tại cực trị', A_EXT)):
        print(f"-- {name} vs ĐỐI CHỨNG --")
        print(f"{'target':>7}" + ''.join(f"{'H='+str(H):>26}" for H in HORIZONS))
        for t in tlist:
            cells = []
            for H in HORIZONS:
                aw = an = cw2 = cn = 0
                for f in g:
                    o = grid_out(f, t, H, rev, norm)
                    if o is None: continue
                    an += 1; aw += o
                for f in CTRL:
                    o = grid_out(f, t, H, rev, norm)
                    if o is None: continue
                    cn += 1; cw2 += o
                a, c = pct(aw, an), pct(cw2, cn)
                cells.append(f"{a:5.1f}({an:5d}) {c:5.1f} {a-c:+5.1f}±{se(an):.1f}")
            print(f"{t:7.1f}" + ''.join(f"{c:>26}" for c in cells))


matrix('3a. TARGET CHUẨN HOÁ (k × medRange100) × HORIZON — ĐẢO CHIỀU  ⭐ bảng kết luận',
       NKS, True, True)
matrix('3b. target USD tuyệt đối × HORIZON — ĐẢO CHIỀU (chỉ tham chiếu, bị nhiễu biến động)',
       TARGETS, False, True)
matrix('4a. TARGET CHUẨN HOÁ × HORIZON — TIẾP DIỄN', NKS, True, False)
matrix('4b. target USD tuyệt đối × HORIZON — TIẾP DIỄN (tham chiếu)', TARGETS, False, False)

# ---------------------------------------------------------------- 5. theo ĐIỂM, mọi outcome
print("\n=== 5. THEO NGƯỠNG ĐIỂM (mọi tín hiệu) — 4 outcome cạnh nhau ===")
print("hold20 = mức giữ 20 nến (close, buf chuẩn hoá) | rev/cont = target 1×medRange, H=20"
      " | E[R] = SL mức±2tick, TP 2R, H=20, tie→SL (bảo thủ)")
print(f"{'ngưỡng':>8}{'n':>7}{'hold20':>10}{'rev1x/20':>10}{'cont1x/20':>11}{'E[R]|2R':>10}")


def block(g, N=20):
    gg = [f for f in g if f['walked'] >= N]
    if not gg: return 0, 0.0, 0.0, 0.0, 0.0
    hold = pct(sum(1 for f in gg if not f['brk_dc'][N]), len(gg))
    rw = rt = cw2 = ct2 = 0
    for f in gg:
        o = grid_out(f, 1.0, N, True, True)
        if o is not None: rt += 1; rw += o
        o = grid_out(f, 1.0, N, False, True)
        if o is not None: ct2 += 1; cw2 += o
    rs = []
    for f in gg:
        tj, sj = f['rt'][2], f['stop']
        tj = tj if (tj is not None and tj <= N) else None
        sj = sj if (sj is not None and sj <= N) else None
        if tj is not None and (sj is None or tj < sj): rs.append(2.0)   # tie → SL (bảo thủ)
        elif sj is not None: rs.append(-1.0)
        else:
            c = f['lastc'][N]
            rs.append(((f['entry'] - c) if f['top'] else (c - f['entry'])) / f['risk'])
    return len(gg), hold, pct(rw, rt), pct(cw2, ct2), st.mean(rs) if rs else 0.0


for s in range(12, 2, -1):
    g = [f for f in A_ALL if f['score'] >= s]
    if not g: continue
    m, hold, rv, cv, er = block(g)
    print(f"{'≥'+str(s):>8}{m:7d}{hold:9.1f}%{rv:9.1f}%{cv:9.1f}%{er:+10.3f}")
m, hold, rv, cv, er = block(CTRL)
print(f"{'ĐốiCh':>8}{m:7d}{hold:9.1f}%{rv:9.1f}%{cv:9.1f}%{er:+10.3f}")

print("\n=== 6. HOLD20 (close) THEO TỪNG THÀNH PHẦN ĐIỂM (cùng tập tín hiệu ABS) ===")
for key in ('noResult', 'divergence', 'twoSided', 'prominent', 'swing', 'multi'):
    on = [0, 0]; off = [0, 0]
    for f in A_ALL:
        if f['walked'] < 20: continue
        tgt = on if f['comp'][key] else off
        tgt[0] += (0 if f['brk_dc'][20] else 1); tgt[1] += 1
    a, b = pct(*on), pct(*off)
    print(f"  {key:11s} CÓ: {a:5.1f}% (n={on[1]:5d})  KHÔNG: {b:5.1f}% (n={off[1]:5d})  chênh {a-b:+5.1f}pp")

print("\n=== 7. HIỆU ỨNG NGƯỢC: điểm CAO (≥9) → mức DỄ VỠ. Đo chiều TIẾP DIỄN ===")
HI = [f for f in A_ALL if f['score'] >= 9]
print(f"n={len(HI)}  (điểm ≥9) — target CHUẨN HOÁ. ⚠ n<500 → chỉ là gợi ý, không kết luận.")
print(f"{'target':>7}" + ''.join(f"{'H='+str(H):>24}" for H in HORIZONS))
for t in NKS:
    cells = []
    for H in HORIZONS:
        aw = an = cw2 = cn = 0
        for f in HI:
            o = grid_out(f, t, H, False, True)
            if o is None: continue
            an += 1; aw += o
        for f in CTRL:
            o = grid_out(f, t, H, False, True)
            if o is None: continue
            cn += 1; cw2 += o
        a, c = pct(aw, an), pct(cw2, cn)
        cells.append(f"{a:5.1f}({an:4d}) {c:5.1f} {a-c:+5.1f}±{se(an):.1f}")
    print(f"{t:7.1f}" + ''.join(f"{c:>24}" for c in cells))
print("  → mỗi ô: ABS≥9% (n) | ĐỐI CHỨNG% | chênh pp ± se. Cần chênh > 2σ mới đáng tin.")

# ---------------------------------------------------------------- 8. ổn định theo tháng
print("\n=== 8. ỔN ĐỊNH THEO THÁNG (T5 / T6 / T7 riêng) ===")
print("cùng 4 outcome của bảng 5, chạy riêng từng tháng, ABS mọi tín hiệu vs ĐỐI CHỨNG")
print(f"{'tháng':>6}{'nhóm':>12}{'n':>7}{'hold20':>10}{'rev1x/20':>10}{'cont1x/20':>11}{'E[R]|2R':>10}")
for mo in ('05', '06', '07'):
    for lbl, g in (('ABS', A_ALL), ('ĐốiCh', CTRL)):
        sub = [f for f in g if f['month'] == mo]
        m, hold, rv, cv, er = block(sub)
        print(f"{mo:>6}{lbl:>12}{m:7d}{hold:9.1f}%{rv:9.1f}%{cv:9.1f}%{er:+10.3f}")
print("  se cho ABS theo tháng ≈ " + ', '.join(
    f"T{mo}: ±{se(len([f for f in A_ALL if f['month']==mo])):.1f}" for mo in ('05', '06', '07')))

print("\n=== XONG ===")
