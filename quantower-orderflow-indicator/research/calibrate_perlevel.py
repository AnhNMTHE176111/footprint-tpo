#!/usr/bin/env python3
"""Calibrate ngưỡng cho OrderFlowBubbles bằng footprint PER-LEVEL thật.

Dùng:
    python3 calibrate_perlevel.py <file-per-level.csv> [--tick 0.1] [--target 1.0] [--horizon 20]
    python3 calibrate_perlevel.py <file-per-level.csv> --trades <file-per-trade.csv>

File PER-LEVEL (1 dòng = 1 ô footprint) — tên cột nhận cả các biến thể phổ biến:
    bar_time ; price (hoặc price_ticks) ; bid_vol ; ask_vol ; [trades] ;
    bar_open ; bar_high ; bar_low ; bar_close ; [bar_volume] ; [max_one_trade_vol]

File PER-TRADE (tuỳ chọn, mở khoá tầng tick):
    timestamp_ms ; price ; size ; aggressor

Script mô phỏng ĐÚNG công thức đang chạy trong OrderFlowBubbles.cs (RollingRobust median+MAD,
baseline top-K ô, điểm absorption v3) rồi in ra:
  1. tần suất nổ THẬT của Big Trade / Absorption theo từng ngưỡng  (thay bảng mô phỏng cũ)
  2. hit-rate theo TỪNG MỨC ĐIỂM absorption → chọn AbsScoreMin
  3. đóng góp của từng thành phần điểm (cái nào thật sự có giá trị)
  4. ngưỡng đề xuất để điền vào Settings
"""
import csv, sys, statistics as st
from collections import defaultdict

# ------------------------------------------------------------------ tham số
ARGS = sys.argv[1:]
if not ARGS:
    print(__doc__); sys.exit(1)
PATH = ARGS[0]


def opt(name, default, cast=float):
    return cast(ARGS[ARGS.index(name) + 1]) if name in ARGS else default


TICK = opt('--tick', 0.1)
TARGET = opt('--target', 1.0)
HORIZON = opt('--horizon', 20, int)
TRADES = ARGS[ARGS.index('--trades') + 1] if '--trades' in ARGS else None
FROM = ARGS[ARGS.index('--from') + 1] if '--from' in ARGS else None   # lọc từ ngày YYYY-MM-DD

BASELINE_BARS, MIN_BARS = 100, 40
MIN_LVL_FLOOR = 5

OHLC = ARGS[ARGS.index('--ohlc') + 1] if '--ohlc' in ARGS else None

ALIAS = {
    'bar_time': ['bar_time', 'time', 'datetime', 'bartime', 'time left', 'timeleft'],
    'bar_idx': ['bar_idx', 'baridx', 'bar_index'],
    'price': ['price', 'level_price', 'price_level'],
    'price_ticks': ['price_ticks', 'priceticks', 'tick_index'],
    'bid': ['bid_vol', 'bid', 'bidvolume', 'bid_volume', 'sell_vol', 'sell (bid) volume'],
    'ask': ['ask_vol', 'ask', 'askvolume', 'ask_volume', 'buy_vol', 'buy (ask) volume'],
    # volume THẬT của ô: có thể > bid+ask khi feed không phân loại được phe của một số trade
    'lvlvol': ['level_volume', 'lvl_vol', 'volume', 'vol'],
    'trades': ['trades', 'ticks', 'n_trades'],
    'o': ['bar_open', 'open'], 'h': ['bar_high', 'high'],
    'l': ['bar_low', 'low'], 'c': ['bar_close', 'close'],
    'barvol': ['bar_volume', 'bar_vol'],
    'mot': ['max_one_trade', 'max_one_trade_vol', 'max one trade vol.', 'maxonetradevolume'],
}


def load_ohlc(path):
    """Nạp OHLC từ file bar-level (ghép theo mốc thời gian) — file per-level thường không có."""
    delim = sniff(path)
    rd = csv.DictReader(open(path, encoding='utf-8-sig'), delimiter=delim)
    low = {(f or '').strip().lower(): f for f in (rd.fieldnames or [])}
    ct = low.get('time left') or low.get('datetime') or low.get('time') or low.get('date')
    co, ch, cl, cc = (low.get(k) for k in ('open', 'high', 'low', 'close'))
    if not (ct and co and cc):
        print(f"--ohlc: thiếu cột thời gian/Open/Close. Header: {rd.fieldnames}"); sys.exit(1)
    out = {}
    for row in rd:
        t = norm_time((row.get(ct) or '').strip())
        if not t: continue
        try:
            out[t] = (float(row[co]), float(row[ch]), float(row[cl]), float(row[cc]))
        except (TypeError, ValueError):
            pass
    return out


def norm_time(s):
    """'2026-07-28 10:51:00.000' | '7/28/2026 10:51:00 AM' → '2026-07-28 10:51'"""
    s = s.strip()
    if not s: return ''
    if '.' in s: s = s.split('.')[0]
    ampm = ''
    for tag in (' AM', ' PM', ' am', ' pm'):
        if s.endswith(tag): ampm = tag.strip().upper(); s = s[:-3].strip()
    parts = s.split()
    if len(parts) < 2: return s
    d, t = parts[0], parts[1]
    tp = t.split(':')
    hh = int(tp[0]); mm = tp[1] if len(tp) > 1 else '00'
    if ampm == 'PM' and hh < 12: hh += 12
    if ampm == 'AM' and hh == 12: hh = 0
    if '/' in d:
        a, b, c = d.split('/')
        d = f"{int(c):04d}-{int(a):02d}-{int(b):02d}"      # M/D/YYYY
    return f"{d} {hh:02d}:{int(mm):02d}"


def sniff(path):
    head = open(path, encoding='utf-8-sig').readline()
    return ';' if head.count(';') > head.count(',') else ','


def colmap(fieldnames):
    low = {(f or '').strip().lower(): f for f in fieldnames}
    out = {}
    for key, names in ALIAS.items():
        for n in names:
            if n in low: out[key] = low[n]; break
    return out


def fnum(row, col):
    if not col: return None
    v = (row.get(col) or '').strip().replace(',', '.')
    try: return float(v)
    except ValueError: return None


# ------------------------------------------------------------------ đọc dữ liệu
def load_bars(path):
    delim = sniff(path)
    rd = csv.DictReader(open(path, encoding='utf-8-sig'), delimiter=delim)
    cm = colmap(rd.fieldnames or [])
    need = ['bar_time', 'bid', 'ask']
    missing = [n for n in need if n not in cm]
    if missing or ('price' not in cm and 'price_ticks' not in cm):
        print(f"THIẾU CỘT: {missing + ([] if ('price' in cm or 'price_ticks' in cm) else ['price'])}")
        print(f"Header đọc được: {rd.fieldnames}"); sys.exit(1)

    ohlc = load_ohlc(OHLC) if OHLC else {}
    bars = defaultdict(lambda: {'lvls': [], 'o': None, 'h': None, 'l': None, 'c': None,
                                'mot': 0.0, 'vol': 0.0, 't': ''})
    order = []
    for row in rd:
        t = (row.get(cm['bar_time']) or '').strip()
        # khoá nến: ưu tiên bar_idx (chắc chắn duy nhất) rồi mới tới mốc thời gian
        key = (row.get(cm['bar_idx']) or '').strip() if 'bar_idx' in cm else t
        if not key: continue
        if key not in bars: order.append(key)
        b = bars[key]
        b['t'] = t
        pt = fnum(row, cm.get('price_ticks'))
        pr = fnum(row, cm.get('price'))
        if pt is None and pr is None: continue
        if pt is None: pt = round(pr / TICK)
        if pr is None: pr = pt * TICK
        bid = fnum(row, cm['bid']) or 0.0
        ask = fnum(row, cm['ask']) or 0.0
        lv = fnum(row, cm.get('lvlvol'))
        lv = lv if (lv is not None and lv > 0) else bid + ask     # volume ô THẬT (có thể > bid+ask)
        b['lvls'].append((int(pt), pr, bid, ask, lv))
        b['vol'] += lv
        for k in ('o', 'h', 'l', 'c'):
            if k in cm and b[k] is None: b[k] = fnum(row, cm[k])
        m = fnum(row, cm.get('mot'))
        if m: b['mot'] = max(b['mot'], m)

    out, joined, skipped = [], 0, 0
    for key in order:
        b = bars[key]
        if not b['lvls']: continue
        pts = [x[0] for x in b['lvls']]
        o = h = l = c = None
        if ohlc:
            q = ohlc.get(norm_time(b['t']))
            if q: o, h, l, c = q; joined += 1
        if b['o'] is not None: o = b['o']
        if b['h'] is not None: h = b['h']
        if b['l'] is not None: l = b['l']
        if b['c'] is not None: c = b['c']
        if h is None: h = max(x[1] for x in b['lvls'])
        if l is None: l = min(x[1] for x in b['lvls'])
        if FROM and b['t'][:10] < FROM: continue          # giai đoạn hợp đồng chưa lỏng
        if o is None or c is None: skipped += 1; continue  # không ghép được OHLC → bỏ
        out.append(dict(t=b['t'], lvls=b['lvls'], lo_t=min(pts), hi_t=max(pts),
                        o=o, c=c, h=h, l=l, mot=b['mot'], vol=b['vol'],
                        delta=sum(x[3] - x[2] for x in b['lvls'])))
    if OHLC:
        print(f"ghép OHLC: {joined} nến khớp, bỏ {skipped} nến không khớp → dùng {len(out)} nến"
              + (f" (từ {FROM})" if FROM else ""))
    return out, cm


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


# ------------------------------------------------------------------ chạy chỉ báo
def analyse(bars, top_k, eff_z, big_z, big_mult, max_displ=2, swing=9, poc_prom=1.5,
            div_pct=0.10, two_sided=0.35, multi_lb=5, range_ratio=0.9, impact_z=1.0):
    n = len(bars)
    rl, rrange, rimpact = Robust(BASELINE_BARS), Robust(BASELINE_BARS), Robust(BASELINE_BARS)
    hot = {}
    fires = {'big': 0, 'abs': 0, 'bars': 0}
    recs = []      # (bar_idx, score, top, components)
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


def outcome(bars, i, short):
    ref = bars[i]['c']
    for j in range(i + 1, min(len(bars), i + HORIZON + 1)):
        if short:
            if ref - bars[j]['l'] >= TARGET: return 1
            if bars[j]['h'] - ref >= TARGET: return 0
        else:
            if bars[j]['h'] - ref >= TARGET: return 1
            if ref - bars[j]['l'] >= TARGET: return 0
    return None


def base_rate(bars, lb=10):
    w = t = 0
    for i in range(lb, len(bars) - HORIZON):
        for top in (True, False):
            ok = bars[i]['h'] >= max(bars[j]['h'] for j in range(i - lb, i)) if top \
                else bars[i]['l'] <= min(bars[j]['l'] for j in range(i - lb, i))
            if not ok: continue
            o = outcome(bars, i, short=top)
            if o is None: continue
            t += 1; w += o
    return 100 * w / max(t, 1), t


# ------------------------------------------------------------------ main
bars, cm = load_bars(PATH)
if len(bars) < MIN_BARS + 50:
    print(f"Quá ít nến ({len(bars)}) — cần ≥ {MIN_BARS + 50}."); sys.exit(1)

nl = [len(b['lvls']) for b in bars]
allv = [x[4] for b in bars for x in b['lvls']]
print(f"=== DỮ LIỆU ===\nnến: {len(bars)}  |  ô footprint: {len(allv)}")
print(f"ô/nến: median {st.median(nl):.0f} (min {min(nl)}, max {max(nl)})")
print(f"volume/ô: median {st.median(allv):.1f}  p90 {sorted(allv)[int(.9*len(allv))]:.0f}  max {max(allv):.0f}")
print(f"volume/nến: median {st.median([b['vol'] for b in bars]):.0f}")
mot_ok = sum(1 for b in bars if b['mot'] > 0)
print(f"MaxOneTradeVolume có số: {100*mot_ok/len(bars):.1f}% nến"
      + ("  → Big Trade dùng được lệnh đơn THẬT" if mot_ok > len(bars) * .5
         else "  → xác nhận: phải chạy chế độ HVN cell"))

br, bn = base_rate(bars)
print(f"\nBASE (mọi cực trị cục bộ 10 nến, target {TARGET}, horizon {HORIZON}): {br:.1f}%  n={bn}")

print("\n=== 1. TẦN SUẤT NỔ theo baseline & ngưỡng ===")
print(f"{'baseline':>10} {'effZ':>5} {'bigZ':>5} {'bigMult':>8} {'BigTrade':>10} {'Absorption':>11}")
grids = []
for top_k in (0, 3):
    for eff_z, big_z in ((2.5, 3.0), (3.0, 3.5), (4.0, 4.5)):
        f, recs = analyse(bars, top_k, eff_z, big_z, 4.0)
        nb = max(f['bars'], 1)
        print(f"{('tất cả ô' if top_k == 0 else 'top-3 ô'):>10} {eff_z:5.1f} {big_z:5.1f} {4.0:8.1f}"
              f" {100*f['big']/nb:9.1f}% {100*f['abs']/nb:10.1f}%")
        grids.append((top_k, eff_z, big_z, f, recs))

print("\n=== 2. HIT-RATE THEO ĐIỂM ABSORPTION (baseline top-3, effZ 2.5) ===")
_, _, _, f, recs = [g for g in grids if g[0] == 3 and g[1] == 2.5][0]
by_score = defaultdict(lambda: [0, 0])
for i, score, top, comp, pr in recs:
    if i < 10 or i >= len(bars) - HORIZON: continue
    o = outcome(bars, i, short=top)
    if o is None: continue
    by_score[score][0] += o; by_score[score][1] += 1
cum = [0, 0]
for s in sorted(by_score, reverse=True):
    w, t = by_score[s]; cum[0] += w; cum[1] += t
    se = (0.25 / max(cum[1], 1)) ** 0.5 * 100
    print(f"  điểm ≥{s:2d}: n={cum[1]:5d}  hit={100*cum[0]/max(cum[1],1):5.1f}% ±{se:.1f}"
          f"   (riêng điểm {s}: n={t}, {100*w/max(t,1):.1f}%)")

print("\n=== 3. GIÁ TRỊ TỪNG THÀNH PHẦN (bật vs tắt, cùng tập tín hiệu) ===")
for key in ('noResult', 'divergence', 'twoSided', 'prominent', 'swing', 'multi'):
    on = [0, 0]; off = [0, 0]
    for i, score, top, comp, pr in recs:
        if i < 10 or i >= len(bars) - HORIZON: continue
        o = outcome(bars, i, short=top)
        if o is None: continue
        tgt = on if comp[key] else off
        tgt[0] += o; tgt[1] += 1
    a = 100 * on[0] / max(on[1], 1); b = 100 * off[0] / max(off[1], 1)
    print(f"  {key:11s} CÓ: {a:5.1f}% (n={on[1]:4d})   KHÔNG: {b:5.1f}% (n={off[1]:4d})   chênh {a-b:+5.1f}pp")

print("\n=== 4. ĐỀ XUẤT ĐIỀN VÀO SETTINGS ===")
# chỉ đề xuất mức điểm VỪA đủ mẫu VỪA vượt base quá 1 sai số chuẩn — nếu không có thì nói thẳng
best = None
for s in sorted(by_score, reverse=True):
    w = t = 0
    for sc in by_score:
        if sc >= s: w += by_score[sc][0]; t += by_score[sc][1]
    if t < 100: continue
    hit = 100 * w / t
    se = (0.25 / t) ** 0.5 * 100
    if hit - br < se: continue                      # không phân biệt được với base → bỏ
    if best is None or hit - br > best[1] - br: best = (s, hit, t, se)
if best:
    print(f"  Absorption · Điểm tối thiểu = {best[0]}   "
          f"(hit {best[1]:.1f}% ±{best[3]:.1f}, n={best[2]}, base {br:.1f}% → +{best[1]-br:.1f}pp)")
else:
    print("  ⚠ KHÔNG mức điểm nào vừa đủ mẫu (n≥100) vừa vượt base quá 1σ.")
    print("    → hoặc dữ liệu còn ngắn, hoặc bộ điểm chưa có giá trị dự báo trên khung/thị trường này.")
    print("    Đừng chốt ngưỡng theo bảng 2 lúc này; xem bảng 3 để bỏ thành phần đang làm hại.")
print("  Baseline · Số ô đậm nhất/nến = 3   (so POC với POC, xem bảng 1)")
print("  Big Trade · z + ×median: chọn hàng ở bảng 1 cho tần suất nổ ~5-15% số nến")

# ------------------------------------------------------------------ per-trade (tầng tick)
if TRADES:
    delim = sniff(TRADES)
    rd = csv.DictReader(open(TRADES, encoding='utf-8-sig'), delimiter=delim)
    low = {(f or '').strip().lower(): f for f in (rd.fieldnames or [])}
    cs = low.get('size') or low.get('volume') or low.get('qty')
    cp = low.get('price')
    sizes, runs, cur_p, cur_v, cur_n = [], [], None, 0.0, 0
    for row in rd:
        try: s = float((row.get(cs) or '0').replace(',', '.')); p = float((row.get(cp) or '0').replace(',', '.'))
        except ValueError: continue
        sizes.append(s)
        if cur_p is not None and abs(p - cur_p) < TICK / 2: cur_v += s; cur_n += 1
        else:
            if cur_n: runs.append((cur_v, cur_n))
            cur_p, cur_v, cur_n = p, s, 1
    if cur_n: runs.append((cur_v, cur_n))
    print(f"\n=== 5. TẦNG TICK ({len(sizes)} trade) ===")
    ss = sorted(sizes)
    print(f"  size: median {st.median(ss):.1f}  p99 {ss[int(.99*len(ss))]:.0f}  max {max(ss):.0f}"
          f"  |  >1 lot: {100*sum(1 for x in sizes if x > 1)/len(sizes):.1f}%")
    print("  → CÓ lệnh lớn thật, gộp lệnh/Big Trade đáng làm" if max(sizes) >= 10
          else "  → hầu như toàn lệnh nhỏ: 'lệnh lớn' phải dựng bằng GỘP theo cửa sổ thời gian")
    rv = sorted(r[0] for r in runs)
    print(f"  absorption run (volume liên tiếp tại CÙNG giá): median {st.median(rv):.0f}"
          f"  p95 {rv[int(.95*len(rv))]:.0f}  max {max(rv):.0f}  |  {len(runs)} run")
