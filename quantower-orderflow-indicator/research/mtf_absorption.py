#!/usr/bin/env python3
"""Kiểm giả thuyết: bộ điểm absorption 12 điểm VÔ NGHĨA trên M1, phải lên khung lớn hơn?

Gộp footprint per-level M1 -> M5/M15/M30 (căn theo mốc đồng hồ), chạy lại ĐÚNG hàm
`analyse` của calibrate_perlevel.py trên từng khung, rồi in:
  1. base rate từng khung
  2. hit-rate luỹ tiến theo mức điểm (>=3 .. >=12) kèm n va +-se
  3. chênh pp của TỪNG thành phần (bật vs tắt)
  4. chiều TIẾP DIỄN (= 100 - hit_reversal, outcome nhị phân)
  5. nếu khung nào vượt base > 2se với n>=100 -> quét eff_z x top-K tìm cấu hình tốt nhất

Chạy:  python3 quantower-orderflow-indicator/research/mtf_absorption.py
"""
import pickle, statistics as st, sys, os
from collections import defaultdict

TICK = 0.1
PKL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', '..', 'data-export', '27-7', 'perlevel_m1.pkl')
BASELINE_BARS, MIN_BARS = 100, 40
MIN_LVL_FLOOR = 5
HORIZON = 20
# TARGET tỉ lệ theo khung (USD; 1 USD = 10 tick) — cột PHỤ, chỉ để so sánh
TFS = [('M1', 1, 1.0), ('M5', 5, 2.0), ('M15', 15, 3.0), ('M30', 30, 4.0)]
# TARGET CHUẨN HOÁ (cột CHÍNH, mọi kết luận dựa vào đây): k × median(range 100 nến trước)
K_NORM = 2.0


# ------------------------------------------------------------------ gộp khung
def aggregate(bars, k):
    """Gộp k nến M1 -> 1 nến, căn theo phút chia hết cho k (bucket theo mốc đồng hồ)."""
    if k == 1:
        return bars
    out, cur, key = [], None, None

    def flush(c):
        if not c:
            return
        lv = c['lv']
        lvls = [(pt, pt * TICK, v[0], v[1], v[2]) for pt, v in sorted(lv.items())]
        pts = [x[0] for x in lvls]
        out.append(dict(t=c['t'], o=c['o'], h=c['h'], l=c['l'], c=c['c'],
                        lo_t=min(pts), hi_t=max(pts), lvls=lvls,
                        vol=sum(x[4] for x in lvls),
                        delta=sum(x[3] - x[2] for x in lvls)))

    for b in bars:
        t = b['t']
        kk = (t[:10], int(t[11:13]), int(t[14:16]) // k)
        if kk != key:
            flush(cur)
            key = kk
            cur = dict(t=t, o=b['o'], h=b['h'], l=b['l'], c=b['c'], lv=defaultdict(lambda: [0.0, 0.0, 0.0]))
        cur['h'] = max(cur['h'], b['h'])
        cur['l'] = min(cur['l'], b['l'])
        cur['c'] = b['c']
        for pt, pr, bid, ask, v in b['lvls']:
            a = cur['lv'][pt]
            a[0] += bid; a[1] += ask; a[2] += v
    flush(cur)
    return out


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


# ------------------------------------------------------------------ bộ điểm 12 (copy calibrate_perlevel.analyse)
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


def outcome(bars, i, short, target):
    ref = bars[i]['c']
    for j in range(i + 1, min(len(bars), i + HORIZON + 1)):
        if short:
            if ref - bars[j]['l'] >= target: return 1
            if bars[j]['h'] - ref >= target: return 0
        else:
            if bars[j]['h'] - ref >= target: return 1
            if ref - bars[j]['l'] >= target: return 0
    return None


def norm_targets(bars, k=K_NORM, lb=BASELINE_BARS):
    """TARGET CHUẨN HOÁ theo biến động: k × median(range 100 nến TRƯỚC nến i).

    Lý do bắt buộc phải có: target USD cố định bị nhiễu bởi chế độ biến động
    (vol/nến M1 tháng 5 ≈ 26, tháng 6 ≈ 20, tháng 7 ≈ 73). Mọi tín hiệu tương quan với
    'nến sôi động' sẽ trông như có edge chỉ vì target cố định dễ đạt hơn khi biến động cao.
    """
    out = [None] * len(bars)
    rng = [b['h'] - b['l'] for b in bars]
    for i in range(len(bars)):
        if i >= MIN_BARS:
            out[i] = max(k * st.median(rng[max(0, i - lb):i]), TICK)
    return out


def base_rate(bars, target, tgts=None, lb=10):
    """target: số USD cố định (nếu tgts=None) | tgts: list target riêng cho từng nến."""
    w = t = 0
    for i in range(lb, len(bars) - HORIZON):
        tg = target if tgts is None else tgts[i]
        if tg is None: continue
        for top in (True, False):
            ok = bars[i]['h'] >= max(bars[j]['h'] for j in range(i - lb, i)) if top \
                else bars[i]['l'] <= min(bars[j]['l'] for j in range(i - lb, i))
            if not ok: continue
            o = outcome(bars, i, short=top, target=tg)
            if o is None: continue
            t += 1; w += o
    return 100 * w / max(t, 1), t


def se(n):
    return (0.25 / max(n, 1)) ** 0.5 * 100


def score_table(bars, recs, target, tgts=None):
    by = defaultdict(lambda: [0, 0])
    for i, sc, top, comp, pr in recs:
        if i < 10 or i >= len(bars) - HORIZON: continue
        tg = target if tgts is None else tgts[i]
        if tg is None: continue
        o = outcome(bars, i, short=top, target=tg)
        if o is None: continue
        by[sc][0] += o; by[sc][1] += 1
    cum = {}
    w = t = 0
    for s in sorted(by, reverse=True):
        w += by[s][0]; t += by[s][1]
        cum[s] = (w, t, 100 * w / max(t, 1), se(t), by[s][1], 100 * by[s][0] / max(by[s][1], 1))
    return by, cum


def comp_table(bars, recs, target, tgts=None):
    rows = []
    for key in ('noResult', 'divergence', 'twoSided', 'prominent', 'swing', 'multi'):
        on = [0, 0]; off = [0, 0]
        for i, sc, top, comp, pr in recs:
            if i < 10 or i >= len(bars) - HORIZON: continue
            tg = target if tgts is None else tgts[i]
            if tg is None: continue
            o = outcome(bars, i, short=top, target=tg)
            if o is None: continue
            g = on if comp[key] else off
            g[0] += o; g[1] += 1
        a = 100 * on[0] / max(on[1], 1); b = 100 * off[0] / max(off[1], 1)
        rows.append((key, a, on[1], b, off[1], a - b))
    return rows


# ------------------------------------------------------------------ main
m1 = pickle.load(open(os.path.normpath(PKL), 'rb'))
print(f"M1 nạp: {len(m1)} nến  ({m1[0]['t']} → {m1[-1]['t']})")

results = {}
for name, k, target in TFS:
    bars = aggregate(m1, k)
    tg = norm_targets(bars)
    brN, bnN = base_rate(bars, None, tgts=tg)          # CHÍNH: target chuẩn hoá
    brF, bnF = base_rate(bars, target)                 # PHỤ: target USD cố định
    f, recs = analyse(bars, 3, 2.5, 3.0, 4.0)
    byN, cumN = score_table(bars, recs, None, tgts=tg)
    byF, cumF = score_table(bars, recs, target)
    results[name] = dict(bars=bars, tg=tg, target=target, br=brN, bn=bnN, brF=brF,
                         fires=f, recs=recs, cum=cumN, cumF=cumF)
    nl = [len(b['lvls']) for b in bars]
    medr = st.median([b['h'] - b['l'] for b in bars])
    print(f"\n{'='*78}\n### {name}  (gộp {k} nến M1, horizon {HORIZON} nến)")
    print(f"nến: {len(bars)}  |  ô/nến median {st.median(nl):.0f}  |  vol/nến median "
          f"{st.median([b['vol'] for b in bars]):.0f}  |  range/nến median {medr:.2f} USD")
    print(f"target CHUẨN HOÁ = {K_NORM}× median(range 100 nến trước)  ~{K_NORM*medr:.2f} USD ở mức median")
    print(f"BASE chuẩn hoá : {brN:.1f}% ±{se(bnN):.1f}  n={bnN}   <-- mọi kết luận dùng cột này")
    print(f"BASE target {target} USD cố định: {brF:.1f}% ±{se(bnF):.1f}  n={bnF}   (chỉ để so sánh)")
    nb = max(f['bars'], 1)
    print(f"tần suất nổ absorption: {100*f['abs']/nb:.1f}% số nến ({f['abs']}/{nb})")
    print(f"\n{'điểm':>6} | {'CHUẨN HOÁ: n':>13} {'hit đảo':>8} {'±se':>5} {'vs base':>8} {'tiếp diễn':>10}"
          f" | {'USD cố định: n':>15} {'hit':>7} {'vs base':>8}")
    for s in sorted(cumN, reverse=True):
        w, t, hit, s_e, n_own, hit_own = cumN[s]
        flag = ''
        if t >= 100 and hit - brN > 2 * s_e: flag = ' ***'
        elif t >= 100 and brN - hit > 2 * s_e: flag = ' xxx'
        cF = cumF.get(s)
        f2 = ('%15d %6.1f%% %+7.1fpp' % (cF[1], cF[2], cF[2] - brF)) if cF else ' ' * 31
        print(f"  ≥{s:2d} | {t:13d} {hit:7.1f}% {s_e:5.1f} {hit-brN:+7.1f}pp {100-hit:9.1f}%"
              f" |{f2}{flag}")
    print("  (*** = vượt base >2se & n≥100 ; xxx = DƯỚI base >2se & n≥100 ; n<500 → coi là gợi ý, không kết luận)")

    print(f"\n  thành phần — cột CHUẨN HOÁ (cùng tập tín hiệu, {name}):")
    comp_rows = comp_table(bars, recs, None, tgts=tg)
    comp_rowsF = {r[0]: r for r in comp_table(bars, recs, target)}
    for key, a, non, b, noff, d in comp_rows:
        dF = comp_rowsF[key][5]
        print(f"    {key:11s} CÓ {a:5.1f}% (n={non:5d})  KHÔNG {b:5.1f}% (n={noff:5d})"
              f"  chênh {d:+5.1f}pp   [USD cố định: {dF:+5.1f}pp]")
    results[name]['comp'] = comp_rows

# ---------------------------------------------- 4b. đặc trưng LIÊN TỤC theo quantile (n lớn)
def zbin(bars, tgts, top_k=3, lb=10, nbins=5, max_displ=2):
    """Thay ngưỡng rời rạc bằng QUANTILE trên toàn bộ nến cực trị cục bộ.

    Đặc trưng liên tục = z của ô volume mạnh nhất nằm ≤2 tick từ cực trị (lõi EFFORT).
    Nếu absorption có giá trị thì hit-rate phải TĂNG ĐƠN ĐIỆU theo bin.
    """
    rl = Robust(BASELINE_BARS)
    samples = []
    for i, b in enumerate(bars):
        vols = sorted((x[4] for x in b['lvls']), reverse=True)
        if rl.n >= MIN_BARS and lb <= i < len(bars) - HORIZON and tgts[i]:
            zt = zb = None
            for pt, pr, bid, ask, v in b['lvls']:
                if v < MIN_LVL_FLOOR: continue
                z = rl.modz(v)
                if (b['hi_t'] - pt) <= max_displ: zt = z if zt is None else max(zt, z)
                if (pt - b['lo_t']) <= max_displ: zb = z if zb is None else max(zb, z)
            for top, zz in ((True, zt), (False, zb)):
                if zz is None: continue
                ok = b['h'] >= max(bars[j]['h'] for j in range(i - lb, i)) if top \
                    else b['l'] <= min(bars[j]['l'] for j in range(i - lb, i))
                if not ok: continue
                o = outcome(bars, i, short=top, target=tgts[i])
                if o is None: continue
                samples.append((zz, o))
        rl.add(vols[:top_k] if top_k > 0 else vols)
    samples.sort(key=lambda x: x[0])
    out = []
    n = len(samples)
    for q in range(nbins):
        seg = samples[n * q // nbins:n * (q + 1) // nbins]
        if not seg: continue
        w = sum(x[1] for x in seg)
        out.append((seg[0][0], seg[-1][0], len(seg), 100 * w / len(seg), se(len(seg))))
    return out, n


print(f"\n{'='*78}\n### 4b. ĐẶC TRƯNG LIÊN TỤC: z của ô mạnh nhất tại cực trị, chia quintile")
print("    (target CHUẨN HOÁ; nếu absorption có giá trị → hit phải tăng đơn điệu theo bin)")
for name, k, target in TFS:
    r = results[name]
    rows, ntot = zbin(r['bars'], r['tg'])
    print(f"\n  {name} — base {r['br']:.1f}%, n tổng {ntot}")
    for q, (z0, z1, nn, hit, s_e) in enumerate(rows, 1):
        print(f"    Q{q} z∈[{z0:6.2f},{z1:6.2f}]  n={nn:6d}  hit {hit:5.1f}% ±{s_e:.1f}"
              f"  ({hit-r['br']:+5.1f}pp)")

# ------------------------------------------------------------------ 5. quét grid cho khung có edge
print(f"\n{'='*78}\n### QUÉT GRID cho khung vượt base >2se (n≥100)")
qual = []
for name, k, target in TFS:
    r = results[name]
    for s, (w, t, hit, s_e, n_own, hit_own) in r['cum'].items():
        if t >= 100 and hit - r['br'] > 2 * s_e:
            qual.append(name); break
if not qual:
    print("  KHÔNG khung nào có mức điểm vừa n≥100 vừa vượt base >2 sai số chuẩn.")
print("  → quét grid CHẨN ĐOÁN cho MỌI khung: nới eff_z / đổi baseline top-K để kéo n lên ≥100")
print("    (in ĐẦY ĐỦ mọi cell, không chỉ cell tốt nhất — tránh cherry-pick)")
GRID_TFS = [t for t in TFS if t[0] in ('M5', 'M15', 'M30')]   # M1 đã thua ở MỌI mức điểm → khỏi quét
for name, k, target in GRID_TFS:
    bars = results[name]['bars']; br = results[name]['br']; tg = results[name]['tg']
    print(f"\n  --- {name} (base chuẩn hoá {br:.1f}%) ---")
    print(f"  {'topK':>6} {'effZ':>5} {'nổ%':>6} | {'≥3 (mọi tín hiệu)':>26} | mức tốt nhất n≥100")
    for top_k in (0, 2, 3, 5):
        for eff_z in (1.5, 2.0, 2.5, 3.0, 4.0):
            f, recs = analyse(bars, top_k, eff_z, eff_z + 0.5, 4.0)
            by, cum = score_table(bars, recs, None, tgts=tg)
            lo = min(cum) if cum else None
            allc = cum[lo] if lo is not None else None
            best = None
            for s in sorted(cum, reverse=True):
                w, t, hit, s_e, n_own, hit_own = cum[s]
                if t < 100: continue
                if best is None or hit - br > best[2] - br: best = (s, t, hit, s_e)
            nb = max(f['bars'], 1)
            c1 = ('%.1f%% ±%.1f n=%d (%+.1fpp)' % (allc[2], allc[3], allc[1], allc[2] - br)) \
                if allc else '-'
            c2 = ('≥%d: %.1f%% ±%.1f n=%d (%+.1fpp)%s'
                  % (best[0], best[2], best[3], best[1], best[2] - br,
                     ' ***' if best[2] - br > 2 * best[3] else
                     (' xxx' if br - best[2] > 2 * best[3] else ''))) if best else 'không mức nào n≥100'
            print(f"  {('tất cả' if top_k==0 else top_k):>6} {eff_z:5.1f} {100*f['abs']/nb:5.1f}%"
                  f" | {c1:>26} | {c2}")

# ------------------------------------------------------------------ tổng hợp
print(f"\n{'='*78}\n### TỔNG HỢP: hit-rate luỹ tiến theo khung × mức điểm"
      f" (baseline top-3, effZ 2.5, target CHUẨN HOÁ {K_NORM}×median range)")
hdr = f"{'mức':>5}"
for name, _, _ in TFS: hdr += f" | {name+' hit (n)':>20}"
print(hdr)
for s in range(12, 2, -1):
    row = f"  ≥{s:2d}"
    for name, _, _ in TFS:
        c = results[name]['cum'].get(s)
        row += f" | {(f'{c[2]:.1f}% ±{c[3]:.1f} (n={c[1]})' if c else '-'):>20}"
    print(row)
row = f"{'BASE':>5}"
for name, _, _ in TFS:
    r = results[name]
    cell = '%.1f%% (n=%d)' % (r['br'], r['bn'])
    row += f" | {cell:>20}"
print(row)
