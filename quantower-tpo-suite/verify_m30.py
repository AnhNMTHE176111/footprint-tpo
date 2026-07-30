#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_m30.py — doi chieu logic M30SessionZones (C#) voi du lieu that.

NGUON: data-export/tpo-data/tpo-m30.csv  (thuc te la bar M1, khong phai M30)
       data-export/tpo-data/tpo-daily.csv

Muc dich: chay lai ProfileEngine bang Python tren cung du lieu, so:
  (a) POC/VAH/VAL Python  vs  cot POC/VAH/VAL Quantower tinh san trong CSV
  (b) vung Python sinh ra  vs  vung tren anh chart nguoi dung gui

KHONG suy dien so. Chi in cai tinh duoc.
"""
import csv, sys, os
from collections import defaultdict
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M30 = os.path.join(ROOT, 'data-export/tpo-data/tpo-m30.csv')

TICK = 0.1
ROW_TICKS = 1            # RowTicks mac dinh -> rowStep = tick
ROWSTEP = TICK * ROW_TICKS
TZ = 7                   # TzOffset mac dinh trong M30SessionZones
ASIA, EUROPE, US = 300, 750, 1140   # 05:00 / 12:30 / 19:00 (phut/ngay, gio local)
GAP_MIN = 75
LOOKBACK = 10


def load(path):
    rows = []
    with open(path, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            try:
                dt = datetime.strptime(r['DateTime'], '%m/%d/%Y %I:%M:%S %p')
                rows.append(dict(
                    dt=dt,
                    o=float(r['Open']), h=float(r['High']),
                    l=float(r['Low']), c=float(r['Close']),
                    vol=float(r['Volume'] or 0),
                    # cot profile Quantower tinh san (dap an de doi chieu)
                    qt_vah=float(r['VAH'] or 'nan'), qt_val=float(r['VAL'] or 'nan'),
                    qt_poc=float(r['POC'] or 'nan'),
                    qt_ibh=float(r['IB High'] or 'nan'), qt_ibl=float(r['IB Low'] or 'nan'),
                ))
            except (ValueError, KeyError):
                continue
    rows.sort(key=lambda x: x['dt'])
    return rows


def label_of(dt):
    """LabelOf() trong M30SessionZones.cs:112 — CSV da la gio local (+07:00)."""
    m = dt.hour * 60 + dt.minute
    if ASIA <= m < EUROPE:
        return 'A'
    if EUROPE <= m < US:
        return 'AU'
    return 'MY'


def blocks_of(bars):
    """Process() M30SessionZones.cs:131 — doi label HOAC gap>75' -> block moi."""
    out, cur, start, prev = [], None, 0, None
    for i, b in enumerate(bars):
        lab = label_of(b['dt'])
        split = prev is None or lab != cur or (b['dt'] - prev).total_seconds() / 60 > GAP_MIN
        if split:
            if prev is not None:
                out.append((cur, start, i - 1))
            cur, start = lab, i
        prev = b['dt']
    if prev is not None:
        out.append((cur, start, len(bars) - 1))
    return out


def tpo_rows(bars, fr, to):
    """ProfileEngine.TpoRows — gia -> so nen phu."""
    rows = defaultdict(float)
    for b in bars[fr:to + 1]:
        a, z = round(b['l'] / ROWSTEP), round(b['h'] / ROWSTEP)
        for r in range(int(a), int(z) + 1):
            rows[r * ROWSTEP] += 1
    return dict(rows)


def volume_rows(bars, fr, to):
    """Xap xi VolumeRows: khong co footprint tung muc gia trong CSV nay,
    nen rai volume deu tren range nen (ghi ro day la XAP XI)."""
    rows = defaultdict(float)
    for b in bars[fr:to + 1]:
        a, z = int(round(b['l'] / ROWSTEP)), int(round(b['h'] / ROWSTEP))
        n = z - a + 1
        if n <= 0 or b['vol'] <= 0:
            continue
        share = b['vol'] / n
        for r in range(a, z + 1):
            rows[r * ROWSTEP] += share
    return dict(rows)


def value_area(rows, frac=0.70):
    """ProfileEngine.ValueArea — rule 2 hang, 70%. Port 1-1 tu C#."""
    if not rows:
        return (float('nan'),) * 3
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    tot = sum(w)
    if tot <= 0:
        return (float('nan'),) * 3
    poc = max(range(len(w)), key=lambda i: w[i])
    # C# dung '>' nen giu POC dau tien khi hoa -> max() cua Python cung vay
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


class SP:
    """SessionProfile."""
    def __init__(self, bars, fr, to, lab, use_volume):
        s = bars[fr:to + 1]
        self.lab, self.fr, self.to = lab, fr, to
        self.start, self.end = s[0]['dt'], s[-1]['dt']
        self.open, self.close = s[0]['o'], s[-1]['c']
        self.high, self.low = max(x['h'] for x in s), min(x['l'] for x in s)
        self.bars = len(s)
        self.vol = sum(x['vol'] for x in s)
        rows = volume_rows(bars, fr, to) if use_volume else None
        if not rows:
            rows = tpo_rows(bars, fr, to)
        self.poc, self.vah, self.val = value_area(rows)
        self.mid = (self.high + self.low) / 2

    @property
    def valid(self):
        return self.bars > 0 and self.poc == self.poc


def is_naked(bars, sp, last_idx):
    """ProfileEngine.IsNaked:328 — CHI nen SAU khi phien dong (i = ToIdx+1)."""
    for b in bars[sp.to + 1:last_idx + 1]:
        if b['l'] <= sp.poc <= b['h']:
            return False
    return True


def cluster_pocs(pocs, tol_ticks, min_count):
    """ProfileEngine.ClusterPocs — gom POC gan nhau."""
    if not pocs:
        return []
    tol = tol_ticks * TICK
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


VN = {'A': 'Á', 'AU': 'Âu', 'MY': 'Mỹ'}


def find_zones(bars, blks, now_price, use_volume):
    """FindZones() M30SessionZones.cs:318 — port 1-1."""
    last = len(bars) - 1
    start = max(0, len(blks) - 1 - LOOKBACK)
    done = []
    for lab, fr, to in blks[start:len(blks) - 1]:      # bo block dang chay
        sp = SP(bars, fr, to, lab, use_volume)
        if sp.valid:
            done.append(sp)
    side = lambda p: -1 if p > now_price else (1 if p < now_price else 0)
    Z = []
    for sp in done:
        if is_naked(bars, sp, last):
            Z.append(dict(c=sp.poc, lo=sp.poc, hi=sp.poc, t='naked_poc',
                          s=72, lb=f'naked POC {VN[sp.lab]} (nam châm)'))
    pocs = [x.poc for x in done]
    for lo, hi, c in cluster_pocs(pocs, 7, 2):
        Z.append(dict(c=(lo + hi) / 2, lo=lo, hi=hi, t='poc_cluster', s=78, lb=f'cụm POC ×{c}'))
    for lo, hi, c in cluster_pocs(pocs, 25, 3):
        Z.append(dict(c=(lo + hi) / 2, lo=lo, hi=hi, t='value_band', s=55, lb=f'băng giá trị ×{c}'))
    for sp in list(reversed(done))[:2]:
        for val, t, st, lb in ((sp.vah, 'va_edge', 60, f'VAH {VN[sp.lab]}'),
                               (sp.val, 'va_edge', 60, f'VAL {VN[sp.lab]}'),
                               (sp.high, 'priorhl', 45, f'Đỉnh {VN[sp.lab]}'),
                               (sp.low, 'priorhl', 45, f'Đáy {VN[sp.lab]}')):
            Z.append(dict(c=val, lo=val, hi=val, t=t, s=st, lb=lb))
    return merge(Z, 7 * TICK), done


def merge(zones, tol):
    """MergeZones() M30SessionZones.cs:363 — gop <=7 tick, strength = max + 0.5*min."""
    res = []
    for z in sorted(zones, key=lambda x: x['c']):
        near = next((r for r in res if abs(r['c'] - z['c']) <= tol), None)
        if near:
            near['lo'], near['hi'] = min(near['lo'], z['lo']), max(near['hi'], z['hi'])
            near['c'] = (near['lo'] + near['hi']) / 2
            near['s'] = min(100, max(near['s'], z['s']) + 0.5 * min(near['s'], z['s']))
            if z['lb'].split(' ')[0] not in near['lb']:
                near['lb'] += ' + ' + z['lb']
        else:
            res.append(dict(z))
    return sorted(res, key=lambda x: -x['s'])


# ============================================================================
def main():
    bars = load(M30)
    print(f'Nap {len(bars)} nen: {bars[0]["dt"]} -> {bars[-1]["dt"]}')
    step = (bars[1]['dt'] - bars[0]['dt']).total_seconds() / 60
    print(f'Khoang cach nen dau: {step:.0f} phut  '
          f'(=> file ten "m30" nhung thuc te la M{step:.0f})')

    blks = blocks_of(bars)
    print(f'\n=== {len(blks)} BLOCK PHIEN (label + gap>{GAP_MIN}p) ===')
    print(f'{"#":>2} {"phien":5} {"tu":16} {"den":16} {"nen":>4} '
          f'{"POC":>8} {"VAH":>8} {"VAL":>8} | {"QT POC":>8} {"QT VAH":>8} {"QT VAL":>8}')
    for i, (lab, fr, to) in enumerate(blks):
        sp = SP(bars, fr, to, lab, use_volume=True)
        qb = bars[to]
        print(f'{i:2} {VN[lab]:5} {sp.start:%m-%d %H:%M} {sp.end:%m-%d %H:%M} {sp.bars:4} '
              f'{sp.poc:8.1f} {sp.vah:8.1f} {sp.val:8.1f} | '
              f'{qb["qt_poc"]:8.1f} {qb["qt_vah"]:8.1f} {qb["qt_val"]:8.1f}')

    now = bars[-1]['c']
    print(f'\nGia hien tai (close nen cuoi) = {now}')

    for use_vol, tag in ((True, 'VOLUME (xap xi: rai deu tren range nen)'),
                         (False, 'TPO (dem nen phu — khong can footprint)')):
        Z, done = find_zones(bars, blks, now, use_vol)
        print(f'\n=== VUNG — nguon {tag} ===')
        print(f'{"gia":>10} {"manh":>5} {"phia":>5}  nhan')
        for z in Z:
            side = 'trên' if z['c'] > now else 'dưới'
            rng = f'{z["lo"]:.1f}-{z["hi"]:.1f}' if z['hi'] - z['lo'] > 1e-9 else f'{z["c"]:.1f}'
            print(f'{rng:>10} {z["s"]:5.0f} {side:>5}  {z["lb"]}')


if __name__ == '__main__':
    main()
