#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_zones_v2.py — port 1-1 logic M30SessionZones v2 (sau plan D1-D6), kiem
tren du lieu that + BACKTEST so sanh v1 vs v2.

NGUON: data-export/tpo-data/tpo-daily.csv (thuc te la bar M30, 26 ngay 30/6-30/7)
       data-export/tpo-data/tpo-m30.csv   (thuc te la bar M1, 3 ngay 27-30/7)

Chay: python3 quantower-tpo-suite/verify_zones_v2.py
"""
import csv, os
from collections import defaultdict
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M30_FILE = os.path.join(ROOT, 'data-export/tpo-data/tpo-daily.csv')   # bar M30, 26 ngay
M1_FILE = os.path.join(ROOT, 'data-export/tpo-data/tpo-m30.csv')       # bar M1, 3 ngay
TICK = 0.1


def load(path):
    out = []
    with open(path, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            try:
                out.append(dict(
                    dt=datetime.strptime(r['DateTime'], '%m/%d/%Y %I:%M:%S %p'),
                    o=float(r['Open']), h=float(r['High']),
                    l=float(r['Low']), c=float(r['Close']),
                    vol=float(r['Volume'] or 0)))
            except (ValueError, KeyError):
                continue
    out.sort(key=lambda x: x['dt'])
    return out


# ============================================================================
#  Port ProfileEngine
# ============================================================================
def atr(bars, idx, n=20):
    """ProfileEngine.Atr — TB High-Low cua n nen ket thuc tai idx."""
    fr = max(0, idx - n + 1)
    s = bars[fr:idx + 1]
    return sum(b['h'] - b['l'] for b in s) / len(s) if s else 0.0


def rows_of(bars, step=TICK, use_volume=True):
    r = defaultdict(float)
    for b in bars:
        a, z = int(round(b['l'] / step)), int(round(b['h'] / step))
        n = z - a + 1
        if n <= 0:
            continue
        w = (b['vol'] / n) if (use_volume and b['vol'] > 0) else 1.0
        for k in range(a, z + 1):
            r[k * step] += w
    return dict(r)


def value_area(rows, frac=0.70):
    if not rows:
        return (float('nan'),) * 3
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    tot = sum(w)
    if tot <= 0:
        return (float('nan'),) * 3
    poc = max(range(len(w)), key=lambda i: w[i])
    acc, target, lo, hi = w[poc], tot * frac, poc, poc
    while acc < target and (lo > 0 or hi < len(w) - 1):
        up = (w[hi + 1] if hi < len(w) - 1 else 0) + (w[hi + 2] if hi < len(w) - 2 else 0)
        dn = (w[lo - 1] if lo > 0 else 0) + (w[lo - 2] if lo > 1 else 0)
        if hi >= len(w) - 1:
            acc += dn; lo = max(0, lo - 2)
        elif lo <= 0:
            acc += up; hi = min(len(w) - 1, hi + 2)
        elif up >= dn:
            acc += up; hi = min(len(w) - 1, hi + 2)
        else:
            acc += dn; lo = max(0, lo - 2)
    return prices[poc], prices[hi], prices[lo]


def find_peaks(rows, tick_, smooth_ticks=5, ratio_cmp=None, min_sep_ticks=0, take_max=True):
    """Loi chung cho FindHvn/FindLvn — dinh cuc bo (take_max) hoac day cuc bo."""
    if not rows:
        return []
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    n = len(w)
    avg = sum(w) / n
    if avg <= 0:
        return []
    if min_sep_ticks <= 0:
        min_sep_ticks = min(120, max(20, (prices[-1] - prices[0]) / tick_ * 0.08))
    sm = []
    for i in range(n):
        a, z = max(0, i - smooth_ticks), min(n, i + smooth_ticks + 1)
        sm.append(sum(w[a:z]) / (z - a))
    cand = []
    for i in range(1, n - 1):
        ok = (sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1]) if take_max else (sm[i] <= sm[i - 1] and sm[i] <= sm[i + 1])
        if ok and ratio_cmp(sm[i] / avg):
            cand.append((prices[i], sm[i], sm[i] / avg))
    cand.sort(key=lambda x: -x[1] if take_max else x[1])
    keep = []
    for p in cand:
        if all(abs(p[0] - k[0]) >= min_sep_ticks * tick_ for k in keep):
            keep.append(p)
    return keep


def find_hvn(rows, tick_=TICK, min_ratio=1.5):
    return find_peaks(rows, tick_, ratio_cmp=lambda r: r >= min_ratio, take_max=True)


def find_lvn(rows, tick_=TICK, max_ratio=0.5):
    return find_peaks(rows, tick_, ratio_cmp=lambda r: r <= max_ratio, take_max=False)


def cluster_pocs(pocs, tol_ticks, min_count, tick_=TICK):
    if not pocs:
        return []
    tol = tol_ticks * tick_
    s = sorted(pocs)
    out, grp = [], [s[0]]
    for p in s[1:]:
        if p - grp[-1] <= tol:
            grp.append(p)
        else:
            if len(grp) >= min_count:
                out.append((min(grp), max(grp), len(grp)))
            grp = [p]
    if len(grp) >= min_count:
        out.append((min(grp), max(grp), len(grp)))
    return out


def is_naked(bars, poc, to_idx, last_idx):
    for b in bars[to_idx + 1:last_idx + 1]:
        if b['l'] <= poc <= b['h']:
            return False
    return True


# ============================================================================
#  Port M30SessionZones — v1 (truoc plan) vs v2 (sau plan D1-D6)
# ============================================================================
class Zone:
    __slots__ = ('lo', 'hi', 'center', 'type', 'side', 'strength', 'label', 'frames')

    def __init__(self, center, lo, hi, typ, side, strength, label, frames=1):
        self.center, self.lo, self.hi = center, lo, hi
        self.type, self.side, self.strength, self.label = typ, side, strength, label
        self.frames = frames

    def __repr__(self):
        return f'{self.center:.1f}[{self.strength:.0f}]{self.type}'


def side_of(p, now):
    return -1 if p > now else (1 if p < now else 0)


class SP:
    def __init__(self, bars, fr, to, lab, use_volume=True):
        s = bars[fr:to + 1]
        self.lab, self.fr, self.to = lab, fr, to
        self.end = s[-1]['dt']
        self.high, self.low = max(x['h'] for x in s), min(x['l'] for x in s)
        rows = rows_of(s, use_volume=use_volume)
        self.poc, self.vah, self.val = value_area(rows)


def find_zones(bars, sessions, now_price, version='v2', zone_lookback=10,
              max_hvn=3, max_lvn=2, zone_range_atr=3.0, max_zones=5):
    """sessions: list of (lab, fr, to) — cac phien da dong (khong gom phien dang chay)."""
    last = len(bars) - 1
    atr_now = atr(bars, last)
    start = max(0, len(sessions) - zone_lookback)
    completed = [SP(bars, fr, to, lab) for lab, fr, to in sessions[start:]]

    zones, lvn_zones = [], []

    show_hvn = version == 'v2'
    show_lvn = version == 'v2'
    if (show_hvn or show_lvn) and completed:
        wk_fr = sessions[start][1]
        wk_to = sessions[-1][2]
        wk_rows = rows_of(bars[wk_fr:wk_to + 1])
        day_start = completed[-1].end - timedelta(hours=24)
        d_fr = None
        for lab, fr, to in sessions[start:]:
            if bars[fr]['dt'] >= day_start:
                d_fr = fr
                break
        dy_rows = rows_of(bars[d_fr:wk_to + 1]) if d_fr is not None else None

        if show_hvn:
            for p, _, ratio in find_hvn(wk_rows)[:max_hvn]:
                zones.append(Zone(p, p, p, 'hvn_week', side_of(p, now_price),
                                  min(95, 70 + ratio * 6), f'HVN tuần ×{ratio:.1f}'))
            if dy_rows:
                for p, _, ratio in find_hvn(dy_rows)[:max_hvn]:
                    zones.append(Zone(p, p, p, 'hvn_day', side_of(p, now_price),
                                      min(88, 64 + ratio * 6), f'HVN ngày ×{ratio:.1f}'))
        if show_lvn:
            for p, _, ratio in find_lvn(wk_rows)[:max_lvn]:
                lvn_zones.append(Zone(p, p, p, 'lvn', side_of(p, now_price), 30,
                                      f'LVN tuần ×{ratio:.1f} (xuyên nhanh)'))

    for sp in completed:
        if is_naked(bars, sp.poc, sp.to, last):
            zones.append(Zone(sp.poc, sp.poc, sp.poc, 'naked_poc', side_of(sp.poc, now_price),
                              72, f'naked POC {sp.lab}'))

    pocs = [sp.poc for sp in completed]
    for lo, hi, c in cluster_pocs(pocs, 7, 2):
        zones.append(Zone((lo + hi) / 2, lo, hi, 'poc_cluster', side_of((lo + hi) / 2, now_price),
                          78, f'cụm POC ×{c}'))
    for lo, hi, c in cluster_pocs(pocs, 25, 3):
        zones.append(Zone((lo + hi) / 2, lo, hi, 'value_band', side_of((lo + hi) / 2, now_price),
                          55, f'băng giá trị ×{c}'))

    n_sess = 1 if version == 'v2' else 2          # D4: 2 phien -> 1 phien
    va_s, hl_s = (50, 38) if version == 'v2' else (60, 45)   # D4: ha diem
    for sp in list(reversed(completed))[:n_sess]:
        zones.append(Zone(sp.vah, sp.vah, sp.vah, 'va_edge', side_of(sp.vah, now_price), va_s, f'VAH {sp.lab}'))
        zones.append(Zone(sp.val, sp.val, sp.val, 'va_edge', side_of(sp.val, now_price), va_s, f'VAL {sp.lab}'))
        zones.append(Zone(sp.high, sp.high, sp.high, 'priorhl', side_of(sp.high, now_price), hl_s, f'Đỉnh {sp.lab}'))
        zones.append(Zone(sp.low, sp.low, sp.low, 'priorhl', side_of(sp.low, now_price), hl_s, f'Đáy {sp.lab}'))

    merge_tol = (max(atr_now * 0.15, 0.7 * TICK) if version == 'v2' else 7 * TICK)
    if version == 'v2':
        merge_tol = min(merge_tol, 3.0)
    zones = merge_zones(zones, merge_tol, add_frame_bonus=(version == 'v2'))

    if version == 'v2':
        radius = zone_range_atr * max(atr_now, TICK)
        zones = [z for z in zones if abs(z.center - now_price) <= radius]
        zones = limit_and_balance(zones, max_zones)
        lvn_zones = [z for z in lvn_zones if abs(z.center - now_price) <= radius]
        zones = zones + lvn_zones

    return sorted(zones, key=lambda z: -z.strength)


def merge_zones(zones, tol, add_frame_bonus):
    res = []
    for z in sorted(zones, key=lambda x: x.center):
        near = next((r for r in res if abs(r.center - z.center) <= tol), None)
        if near:
            near.lo, near.hi = min(near.lo, z.lo), max(near.hi, z.hi)
            near.center = (near.lo + near.hi) / 2
            bonus = 8 if add_frame_bonus else 0
            near.strength = min(100, max(near.strength, z.strength) + 0.5 * min(near.strength, z.strength) + bonus)
            near.frames += z.frames
            if z.label.split(' ')[0] not in near.label:
                near.label += ' + ' + z.label
        else:
            res.append(z)
    for z in res:
        if z.frames > 1:
            z.label += f' (×{z.frames} khung)'
    return res


def limit_and_balance(zones, cap):
    if len(zones) <= cap:
        return zones
    above = sorted([z for z in zones if z.side < 0], key=lambda z: -z.strength)
    below = sorted([z for z in zones if z.side > 0], key=lambda z: -z.strength)
    res = above[:2] + below[:2]
    rest = sorted([z for z in zones if z not in res], key=lambda z: -z.strength)
    for z in rest:
        if len(res) >= cap:
            break
        res.append(z)
    return res


def label_of(dt, asia=300, europe=750, us=1140):
    m = dt.hour * 60 + dt.minute
    if asia <= m < europe:
        return 'A'
    if europe <= m < us:
        return 'AU'
    return 'MY'


def sessions_of(bars, gap_min=75):
    out, cur, start, prev = [], None, 0, None
    for i, b in enumerate(bars):
        lab = label_of(b['dt'])
        split = prev is None or lab != cur or (b['dt'] - prev).total_seconds() / 60 > gap_min
        if split:
            if prev is not None:
                out.append((cur, start, i - 1))
            cur, start = lab, i
        prev = b['dt']
    if prev is not None:
        out.append((cur, start, len(bars) - 1))
    return out


# ============================================================================
def demo():
    bars = load(M30_FILE)
    print(f'Nap {len(bars)} nen M30  {bars[0]["dt"]:%Y-%m-%d} -> {bars[-1]["dt"]:%Y-%m-%d}\n')
    sessions = sessions_of(bars)
    now = bars[-1]['c']
    print(f'Gia hien tai: {now}   ATR20: {atr(bars, len(bars)-1):.2f} gia\n')

    for ver in ('v1', 'v2'):
        zs = find_zones(bars, sessions[:-1], now, version=ver)   # bo phien dang chay
        print(f'=== {ver.upper()}: {len(zs)} vung ===')
        for z in sorted(zs, key=lambda z: -z.strength):
            d = abs(z.center - now) / TICK
            print(f'  {z.center:8.1f} [{z.strength:5.1f}] cach {d:6.0f}t ({d/10:5.1f} giá)  {z.label}')
        print()


if __name__ == '__main__':
    demo()
