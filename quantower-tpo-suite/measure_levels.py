#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measure_levels.py — do bang so xem loai moc nao dang danh de ve len chart, cho
nguoi dung dung lo 3 gia / chot loi 4.5 gia (1.5R).

Theo PLAN-MOC-PHAN-UNG.md (muc 2, Nhanh A). KHONG doan — moi con so deu in kem
n va khoang tin cay Wilson 95%, va so sanh voi NEN 40% (hoa von toan hoc cua 1.5R).

Nguon du lieu (CO DINH, xem PLAN §1):
  data-export/Data_Footprint_Export.csv       — tung muc gia, 128 phien, GCQ26
  data-export/Data_Footprint_Export_bars.csv  — nen M1 cung khoang

Chay:  python3 quantower-tpo-suite/measure_levels.py
"""
import csv
import math
import os
import random
import statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVEL_CSV = os.path.join(ROOT, 'data-export/Data_Footprint_Export.csv')
BAR_CSV = os.path.join(ROOT, 'data-export/Data_Footprint_Export_bars.csv')

SL, TP, HORIZON = 3.0, 4.5, 60          # PLAN §A0.3 — CO DINH, moi loai muc dung chung
RNG = random.Random(7)                   # hat giong co dinh — ket qua lap lai duoc


# ============================================================================
# A0.2 — Nap du lieu
# ============================================================================

def load_levels():
    """tra ve day[ngay][gia_lam_tron_1] = volume, va day_max_trade[ngay][gia] = max_one_trade lon nhat."""
    day_vol = defaultdict(lambda: defaultdict(float))
    day_maxtrade = defaultdict(lambda: defaultdict(float))
    with open(LEVEL_CSV, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            d = r['datetime'][:10]
            p = round(float(r['price']))
            v = float(r['volume'])
            day_vol[d][p] += v
            mt = float(r.get('max_one_trade') or 0)
            if mt > day_maxtrade[d][p]:
                day_maxtrade[d][p] = mt
    return day_vol, day_maxtrade


def load_bars():
    """tra ve day_bars[ngay] = [(high, low, close), ...] theo thu tu thoi gian."""
    day_bars = defaultdict(list)
    with open(BAR_CSV, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            d = r['datetime'][:10]
            day_bars[d].append((float(r['high']), float(r['low']), float(r['close'])))
    return day_bars


# ============================================================================
# A0.2 (tiep) — Value Area 70% (giong ProfileEngine.ValueArea, POC + mo rong 2 hang)
# ============================================================================

def value_area(rows, frac=0.70):
    if not rows:
        return (float('nan'),) * 3
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    tot = sum(w)
    if tot <= 0:
        return (float('nan'),) * 3
    poc_i = max(range(len(w)), key=lambda i: w[i])
    acc, target, lo, hi = w[poc_i], tot * frac, poc_i, poc_i
    while acc < target and (lo > 0 or hi < len(w) - 1):
        up = (w[hi + 1] if hi < len(w) - 1 else 0) + (w[hi + 2] if hi < len(w) - 2 else 0)
        dn = (w[lo - 1] if lo > 0 else 0) + (w[lo - 2] if lo > 1 else 0)
        if hi >= len(w) - 1:
            acc += dn
            lo = max(0, lo - 2)
        elif lo <= 0:
            acc += up
            hi = min(len(w) - 1, hi + 2)
        elif up >= dn:
            acc += up
            hi = min(len(w) - 1, hi + 2)
        else:
            acc += dn
            lo = max(0, lo - 2)
    return prices[poc_i], prices[hi], prices[lo]     # poc, vah, val


def poc_of(rows):
    return value_area(rows)[0]


# ============================================================================
# A0.3 — Giao thuc thu, CO DINH cho moi loai muc
# ============================================================================

def wilson_ci(wins, n, z=1.96):
    """Bien duoi/tren Wilson 95% cho ty le thang. Tra (lo, hi)."""
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    adj = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - adj) / denom, (centre + adj) / denom)


def try_level(bars, level, k0, side, sl=SL, tp=TP, horizon=HORIZON):
    """Tu diem chi (k0, muc), thu 1 lenh theo `side` (+1 mua/-1 ban).
    Tra 1 (thang) / 0 (thua) / None (het gio, khong tinh)."""
    entry = bars[k0][2]
    if side > 0:
        sl_p, tp_p = entry - sl, entry + tp
    else:
        sl_p, tp_p = entry + sl, entry - tp
    for j in range(k0 + 1, min(k0 + 1 + horizon, len(bars))):
        h, l, _ = bars[j]
        hit_sl = (l <= sl_p) if side > 0 else (h >= sl_p)
        hit_tp = (h >= tp_p) if side > 0 else (l <= tp_p)
        if hit_sl:               # cham ca 2 trong 1 nen -> tinh thua (than trong, PLAN §A0.3)
            return 0
        if hit_tp:
            return 1
    return None


def first_touch(bars, level):
    """Lan CHAM DAU TIEN trong ngay: tra (k, side) hoac None.
    side = +1 neu toi tu TREN (dong nen truoc > muc, tuc dang danh MUA/do),
           -1 neu toi tu DUOI (dang danh BAN/can)."""
    for k in range(1, len(bars)):
        h, l, _ = bars[k]
        if l <= level <= h:
            prev_close = bars[k - 1][2]
            side = 1 if prev_close > level else -1
            return k, side
    return None


def eval_level_series(level_by_day, day_bars, days, reverse_side=False, min_n=1):
    """Voi level_by_day[ngay] = muc can thu TRONG ngay do (da tinh tu du lieu
    truoc do), chay giao thuc A0.3 tren tat ca ngay co du lieu.
    Tra dict {n, win, lose, timeout, win_rate, ci_lo, ci_hi, expectancy}."""
    win = lose = timeout = 0
    for d in days:
        level = level_by_day.get(d)
        if level is None or (isinstance(level, float) and math.isnan(level)):
            continue
        bars = day_bars.get(d)
        if not bars or len(bars) < HORIZON + 5:
            continue
        touch = first_touch(bars, level)
        if touch is None:
            continue
        k, side = touch
        if reverse_side:
            side = -side
        r = try_level(bars, level, k, side)
        if r == 1:
            win += 1
        elif r == 0:
            lose += 1
        else:
            timeout += 1
    n = win + lose
    if n < min_n:
        return dict(n=n, win=win, lose=lose, timeout=timeout, win_rate=None,
                     ci_lo=None, ci_hi=None, expectancy=None)
    wr = win / n
    lo, hi = wilson_ci(win, n)
    exp = (win * TP - lose * SL) / n
    return dict(n=n, win=win, lose=lose, timeout=timeout, win_rate=wr,
                ci_lo=lo, ci_hi=hi, expectancy=exp)


def verdict(res, floor=0.40, min_n=30):
    """PLAN §A0.4 — tieu chi DAT: n>=30 VA bien duoi Wilson > 40%. Khong noi nuoc doi."""
    if res['n'] < min_n:
        return 'CHUA DU CA'
    if res['ci_lo'] is not None and res['ci_lo'] > floor:
        return 'DAT'
    return 'KHONG DAT'


def fmt_row(name, res, n_baskets_tried=None):
    if res['n'] == 0:
        s = f"  {name:38s} n=   0  (khong co ca)"
    else:
        wr = f"{res['win_rate']:.1%}" if res['win_rate'] is not None else '  -  '
        ci = f"[{res['ci_lo']:.1%},{res['ci_hi']:.1%}]" if res['ci_lo'] is not None else ''
        exp = f"{res['expectancy']:+.2f} gia" if res['expectancy'] is not None else ''
        v = verdict(res)
        s = f"  {name:38s} n={res['n']:4d}  thang {wr:6s} CI95 {ci:16s} {exp:10s}  -> {v}"
    if n_baskets_tried:
        s += f"   [da thu {n_baskets_tried} ro]"
    return s


# ============================================================================
# A2 — cac loai moc
# ============================================================================

def sharpness_width(rows, peak_price, frac=0.90):
    """PLAN §A3 — be rong (gia) cua tap muc co volume >= frac*dinh, LIEN TUC
    quanh dinh (khong nhay qua khe trong)."""
    if peak_price not in rows:
        return None
    peak_v = rows[peak_price]
    thr = frac * peak_v
    lo = hi = peak_price
    prices = set(rows)
    while (lo - 1) in prices and rows[lo - 1] >= thr:
        lo -= 1
    while (hi + 1) in prices and rows[hi + 1] >= thr:
        hi += 1
    return hi - lo


def round_number_level(now_close, step):
    """Muc tron gan nhat (step=10 hoac 50) so voi gia dong cua hom truoc."""
    return round(now_close / step) * step


def empirical_sr_levels(day_vol, days, upto_idx, lookback=20, min_touches=2, min_reversal=5):
    """PLAN §A2 'S/R thuc nghiem' — khong dung ly thuyet gi: muc nao trong
    `lookback` phien truoc da bi gia CHAM roi DAO >= min_reversal gia, tu
    2 NGAY KHAC NHAU tro len. Tra list gia, manh nhat (nhieu lan cham) truoc."""
    # gia re, dung xap xi tu day_vol thay vi doc lai bar-by-bar de nhanh
    return None  # xem ham empirical_sr_from_bars ben duoi (dung bar that, chinh xac hon)


def empirical_sr_from_bars(day_bars, days, end_i, lookback=20, min_touches=2, min_reversal=5.0):
    """Nhu tren nhung do THAT tren nen M1: voi moi ngay trong lookback, tim cac
    'diem xoay' (local extreme) roi dao >= min_reversal gia trong <=30 nen tiep
    theo. Gop diem xoay cac ngay khac nhau cach nhau <=1 gia thanh 1 muc, giu
    muc co >= min_touches ngay khac nhau xac nhan. Tra gia MANH NHAT (nhieu
    ngay xac nhan nhat), None neu khong co."""
    start = max(0, end_i - lookback)
    pivots = []   # (gia, ngay)
    for di in range(start, end_i):
        d = days[di]
        bars = day_bars.get(d)
        if not bars or len(bars) < 10:
            continue
        highs = [b[0] for b in bars]
        lows = [b[1] for b in bars]
        n = len(bars)
        for i in range(2, n - 2):
            # dinh cuc bo: cao hon 2 nen truoc/sau
            if highs[i] >= max(highs[max(0, i - 2):i] + highs[i + 1:i + 3], default=-1e9):
                future_min = min(lows[i:min(n, i + 30)])
                if highs[i] - future_min >= min_reversal:
                    pivots.append((round(highs[i]), d))
            if lows[i] <= min(lows[max(0, i - 2):i] + lows[i + 1:i + 3], default=1e9):
                future_max = max(highs[i:min(n, i + 30)])
                if future_max - lows[i] >= min_reversal:
                    pivots.append((round(lows[i]), d))
    if not pivots:
        return None
    # gop gia cach nhau <=1 thanh 1 nhom, dem SO NGAY KHAC NHAU
    by_price = defaultdict(set)
    for p, d in pivots:
        by_price[p].add(d)
    # gop nhom lien ke
    merged = {}
    for p in sorted(by_price):
        placed = False
        for mp in list(merged):
            if abs(p - mp) <= 1:
                merged[mp] |= by_price[p]
                placed = True
                break
        if not placed:
            merged[p] = set(by_price[p])
    strong = [(p, len(ds)) for p, ds in merged.items() if len(ds) >= min_touches]
    if not strong:
        return None
    strong.sort(key=lambda x: -x[1])
    return strong[0][0]


# ============================================================================
# A1 — Truc 1: che do balance / sau-balance (Buoi 6)
# ============================================================================

def va_overlap_ratio(va1, va2):
    lo = max(va1[0], va2[0])
    hi = min(va1[1], va2[1])
    inter = max(0.0, hi - lo)
    union = max(va1[1], va2[1]) - min(va1[0], va2[0])
    return inter / union if union > 0 else 0.0


def classify_regime(day_vol, days, i):
    """i = chi so ngay D can xet CHE DO cua no (dua tren VA cua D-1, D-2, D-3).
    'balance'      : VA(D-1) va VA(D-2) chong nhau >=50%
    'sau_balance'  : VA(D-2),VA(D-3) chong nhau >=50% (balance) NHUNG VA(D-1) roi han (giao=0)
    'khac'         : con lai
    Tra None neu khong du du lieu (i<3)."""
    if i < 3:
        return None

    def va_range(d):
        rows = day_vol.get(d)
        if not rows:
            return None
        _, vah, val = value_area(rows)
        if math.isnan(vah) or math.isnan(val):
            return None
        return (val, vah)

    va1, va2, va3 = va_range(days[i - 1]), va_range(days[i - 2]), va_range(days[i - 3])
    if va1 is None or va2 is None:
        return None
    ov_12 = va_overlap_ratio(va1, va2)
    if ov_12 >= 0.50:
        return 'balance'
    if va3 is not None:
        ov_23 = va_overlap_ratio(va2, va3)
        if ov_23 >= 0.50 and va_overlap_ratio(va1, va2) == 0.0:
            return 'sau_balance'
    return 'khac'


# ============================================================================
# Chay toan bo
# ============================================================================

def main():
    print("=" * 78)
    print("measure_levels.py — do moc nao dang canh, cho SL 3 / TP 4.5 (1.5R)")
    print("Nguon:", os.path.relpath(LEVEL_CSV, ROOT), "+", os.path.relpath(BAR_CSV, ROOT))
    print("=" * 78)

    day_vol, day_maxtrade = load_levels()
    day_bars = load_bars()
    days = sorted(set(day_vol) & set(day_bars))
    print(f"\nSo ngay dung duoc (co ca level-csv va bar-csv): {len(days)}"
          f"  ({days[0]} -> {days[-1]})")

    # ---- A0 baseline: vao lenh NGAU NHIEN ----
    print("\n--- A0 baseline: vao lenh NGAU NHIEN moi ngay (doi chung 'hoa von') ---")
    for side, name in [(1, 'MUA ngau nhien'), (-1, 'BAN ngau nhien')]:
        win = lose = 0
        for d in days:
            bars = day_bars[d]
            if len(bars) < HORIZON + 5:
                continue
            for k in range(0, len(bars) - HORIZON, 7):
                r = try_level(bars, bars[k][2], k, side)
                if r == 1:
                    win += 1
                elif r == 0:
                    lose += 1
        n = win + lose
        res = dict(n=n, win=win, lose=lose, timeout=0, win_rate=win / n,
                   ci_lo=wilson_ci(win, n)[0], ci_hi=wilson_ci(win, n)[1],
                   expectancy=(win * TP - lose * SL) / n)
        print(fmt_row(name, res))

    baskets_tried = 0

    # ------------------------------------------------------------------
    # A2 — so sanh cac loai moc (chua dieu kien hoa), tren TOAN BO 128 phien
    # ------------------------------------------------------------------
    print("\n--- A2: so sanh cac loai moc (chua dieu kien hoa che do) ---")
    print(f"    Nen 40% (hoa von 1.5R) · doi chung ngau nhien ~41-49% (da do lan truoc)")

    def build_level_by_day(fn):
        out = {}
        for i in range(1, len(days)):
            out[days[i]] = fn(i)
        return out

    level_defs = {}

    # HVN ngay (da do lan truoc, lam lai de doi chieu)
    level_defs['HVN ngay hom truoc (dinh volume)'] = build_level_by_day(
        lambda i: max(day_vol[days[i - 1]], key=day_vol[days[i - 1]].get) if day_vol.get(days[i - 1]) else None)

    # POC theo TPO (dem SO NEN M1 cham moi gia) khac HVN (dem VOLUME)
    def tpo_poc(i):
        d = days[i - 1]
        bars = day_bars.get(d)
        if not bars:
            return None
        cnt = defaultdict(int)
        for h, l, _ in bars:
            a, z = math.floor(l), math.ceil(h)
            for p in range(a, z + 1):
                cnt[p] += 1
        return max(cnt, key=cnt.get) if cnt else None
    level_defs['POC theo THOI GIAN (TPO) hom truoc'] = build_level_by_day(tpo_poc)

    # naked POC gan nhat (POC 1 trong so ~10 phien truoc chua bi cham lai)
    def naked_poc(i):
        touched = set()
        pocs = []
        for j in range(max(0, i - 10), i):
            rows = day_vol.get(days[j])
            if not rows:
                continue
            p = poc_of(rows)
            if not math.isnan(p):
                pocs.append((j, p))
        for j, p in pocs:
            hit = False
            for k in range(j + 1, i):
                bars = day_bars.get(days[k])
                if bars and any(l <= p <= h for h, l, _ in bars):
                    hit = True
                    break
            if not hit:
                touched = None  # (giu bien, khong dung)
        naked = None
        for j, p in reversed(pocs):
            hit = any(
                bars and any(l <= p <= h for h, l, _ in bars)
                for k in range(j + 1, i)
                for bars in [day_bars.get(days[k])]
            )
            if not hit:
                naked = p
                break
        return naked
    level_defs['naked POC gan nhat (<=10 phien)'] = build_level_by_day(naked_poc)

    # dinh/day phien truoc
    def prior_high(i):
        bars = day_bars.get(days[i - 1])
        return max(b[0] for b in bars) if bars else None

    def prior_low(i):
        bars = day_bars.get(days[i - 1])
        return min(b[1] for b in bars) if bars else None
    level_defs['Dinh phien truoc'] = build_level_by_day(prior_high)
    level_defs['Day phien truoc'] = build_level_by_day(prior_low)

    # so tron $10 / $50 (gan gia dong cua hom truoc)
    def round10(i):
        bars = day_bars.get(days[i - 1])
        return round_number_level(bars[-1][2], 10) if bars else None

    def round50(i):
        bars = day_bars.get(days[i - 1])
        return round_number_level(bars[-1][2], 50) if bars else None
    level_defs['So tron $10 gan nhat'] = build_level_by_day(round10)
    level_defs['So tron $50 gan nhat'] = build_level_by_day(round50)

    # S/R thuc nghiem (khong ly thuyet)
    level_defs['S/R thuc nghiem (>=2 ngay xac nhan, 20 phien)'] = build_level_by_day(
        lambda i: empirical_sr_from_bars(day_bars, days, i))

    # doi chung: gia dong cua hom truoc, va muc ngau nhien trong range
    level_defs['DOI CHUNG: gia dong cua hom truoc'] = build_level_by_day(
        lambda i: day_bars[days[i - 1]][-1][2] if day_bars.get(days[i - 1]) else None)

    def rnd_level(i):
        rows = day_vol.get(days[i - 1])
        if not rows:
            return None
        ps = sorted(rows)
        if len(ps) < 4:
            return None
        return RNG.choice(ps[len(ps) // 4: 3 * len(ps) // 4])
    level_defs['DOI CHUNG: muc ngau nhien trong range'] = build_level_by_day(rnd_level)

    results_a2 = {}
    for name, lv in level_defs.items():
        res = eval_level_series(lv, day_bars, days)
        baskets_tried += 1
        results_a2[name] = res
        print(fmt_row(name, res))

    # ---- A0.5: dao huong cho moc dang chu y nhat ----
    print("\n--- A0.5: dao huong (kiem 'moc di tiep' thay vi 'moc bat lai') ---")
    for name in ['HVN ngay hom truoc (dinh volume)', 'S/R thuc nghiem (>=2 ngay xac nhan, 20 phien)']:
        lv = level_defs[name]
        res = eval_level_series(lv, day_bars, days, reverse_side=True)
        baskets_tried += 1
        print(fmt_row(name + ' [DAO HUONG]', res))

    # ------------------------------------------------------------------
    # A1 — dieu kien hoa theo che do balance / sau-balance
    # ------------------------------------------------------------------
    print("\n--- A1: dieu kien hoa moc HVN ngay theo CHE DO THI TRUONG (Buoi 6) ---")
    regime_of = {}
    for i in range(3, len(days)):
        regime_of[days[i]] = classify_regime(day_vol, days, i)
    cnt = defaultdict(int)
    for r in regime_of.values():
        cnt[r] += 1
    print("  Phan bo che do:", dict(cnt))

    hvn_lv = level_defs['HVN ngay hom truoc (dinh volume)']
    for regime in ['balance', 'sau_balance', 'khac']:
        days_in_regime = [d for d in days if regime_of.get(d) == regime]
        sub_lv = {d: hvn_lv[d] for d in days_in_regime if d in hvn_lv}
        res = eval_level_series(sub_lv, day_bars, days_in_regime)
        baskets_tried += 1
        print(fmt_row(f'  HVN ngay, che do={regime}', res))
        # sau_balance: thu ca chieu DAO (di tiep) vi Buoi 6 du doan "theo, khong fade"
        if regime == 'sau_balance' and res['n'] > 0:
            res_rev = eval_level_series(sub_lv, day_bars, days_in_regime, reverse_side=True)
            baskets_tried += 1
            print(fmt_row(f'  HVN ngay, che do={regime} [DAO HUONG=theo xu huong]', res_rev))

    # ------------------------------------------------------------------
    # A3 — do nhon co lam moc tot hon khong?
    # ------------------------------------------------------------------
    print("\n--- A3: moc CANG NHON (nen 90% hep) co phan ung tot hon khong? ---")
    sharp_by_day = {}
    for i in range(1, len(days)):
        d_prev = days[i - 1]
        rows = day_vol.get(d_prev)
        if not rows:
            continue
        p = max(rows, key=rows.get)
        w = sharpness_width(rows, p)
        sharp_by_day[days[i]] = (p, w)

    buckets = {'nhon (nen<=1 gia)': [], 'vua (nen 2-4 gia)': [], 'bet (nen>4 gia)': []}
    for d, (p, w) in sharp_by_day.items():
        if w is None:
            continue
        key = 'nhon (nen<=1 gia)' if w <= 1 else ('vua (nen 2-4 gia)' if w <= 4 else 'bet (nen>4 gia)')
        buckets[key].append(d)
    for key, ds in buckets.items():
        sub_lv = {d: sharp_by_day[d][0] for d in ds}
        res = eval_level_series(sub_lv, day_bars, ds)
        baskets_tried += 1
        print(fmt_row(f'  {key}', res))

    # ------------------------------------------------------------------
    # A4 — moc ON DINH (D-1 gan D-2) co tot hon khong?
    # ------------------------------------------------------------------
    print("\n--- A4: moc ON DINH (|HVN(D-1) - HVN(D-2)| <= 2 gia) co tot hon khong? ---")
    stable_days, unstable_days = [], []
    for i in range(2, len(days)):
        p1 = hvn_lv.get(days[i])
        r2 = day_vol.get(days[i - 2])
        if p1 is None or not r2:
            continue
        p2 = max(r2, key=r2.get)
        (stable_days if abs(p1 - p2) <= 2 else unstable_days).append(days[i])
    for name, ds in [('ON DINH (<=2 gia doi)', stable_days), ('KHONG on dinh (>2 gia)', unstable_days)]:
        sub_lv = {d: hvn_lv[d] for d in ds if d in hvn_lv}
        res = eval_level_series(sub_lv, day_bars, ds)
        baskets_tried += 1
        print(fmt_row(f'  {name}', res))

    print(f"\n=> TONG SO RO da thu trong toan bo phien do: {baskets_tried}")
    print("   (PLAN §5 rui ro khop qua muc: ro nao 'DAT' phai kiem lai tren hop dong/khoang thoi gian khac)")


if __name__ == '__main__':
    main()
