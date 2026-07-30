#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_research2.py — do suc phan ung cua vung, BAN SUA LOI.

LOI CUA BAN TRUOC (hvn_research.py): do "gia bat ra bao xa trong 8 nen M30" roi
thay 100% moi vung deu bat >=5 gia. Do la do BIEN DONG THI TRUONG, khong phai
do vung: 8 nen M30 = 4 tieng, vang di 30 gia la binh thuong. Vung nao cung 100%.

BAN NAY do dung cai can do — vung co CHAN gia lai khong:
  1. Chi xet lan cham DAU TIEN theo moi huong tiep can (test dau — dung nhu sach
     day setup Nhieu nut: "Chi giao dich o lan cham dau tien").
  2. Do BAT THUAN (theo huong vung dang chan) tru BAT NGHICH (xuyen qua vung).
     Vung tot = chan duoc gia => bat thuan > bat nghich.
  3. Chuan hoa theo BIEN DONG NEN (ATR) de khong bi thi truong danh lua.
  4. So voi MUC GIA NGAU NHIEN lam doi chung — neu vung khong hon ngau nhien
     thi no vo dung.

NGUON: data-export/tpo-data/tpo-daily.csv (bar M30, 26 ngay)
Chay: python3 quantower-tpo-suite/hvn_research2.py
"""
import csv, os
from collections import defaultdict
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data-export/tpo-data/tpo-daily.csv')
TICK = 0.1
HORIZON = 8          # so nen M30 quan sat sau khi cham
TOL_T = 5            # dung sai coi la "cham" (tick)


def load():
    out = []
    with open(SRC, encoding='utf-8-sig') as f:
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


def atr(bars, i, n=20):
    """Bien do trung binh n nen truoc i — dung de chuan hoa."""
    s = bars[max(0, i - n):i]
    return (sum(b['h'] - b['l'] for b in s) / len(s)) if s else 1.0


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


def find_hvn(rows, smooth_ticks=5, min_ratio=1.5, min_sep_ticks=0):
    """HVN = dinh cuc bo cua phan bo khoi luong (xem hvn_research.py).

    min_sep_ticks<=0 -> tu co gian 8% do rong profile, kep [20,120] tick.
    (Co dinh 20t lam profile tuan bi tach 1 nut thanh 3 HVN sat nhau.)
    """
    if not rows:
        return []
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    n = len(w)
    avg = sum(w) / n
    if avg <= 0:
        return []
    if min_sep_ticks <= 0:
        min_sep_ticks = min(120, max(20, (prices[-1] - prices[0]) / TICK * 0.08))
    sm = []
    for i in range(n):
        a, z = max(0, i - smooth_ticks), min(n, i + smooth_ticks + 1)
        sm.append(sum(w[a:z]) / (z - a))
    peaks = [(prices[i], sm[i], sm[i] / avg) for i in range(1, n - 1)
             if sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] >= min_ratio * avg]
    peaks.sort(key=lambda x: -x[1])
    keep = []
    for p in peaks:
        if all(abs(p[0] - k[0]) >= min_sep_ticks * TICK for k in keep):
            keep.append(p)
    return keep


def week_key(dt):
    return dt.date() - timedelta(days=dt.weekday())


def first_touches(bars, level, i0, i1):
    """Lan cham DAU TIEN theo moi huong tiep can, trong [i0,i1).

    Tra ve list (idx, huong_tiep_can) — huong = +1 neu gia di tu DUOI len cham
    (vung dong vai KHANG CU), -1 neu tu TREN xuong (vung dong vai HO TRO).
    Chi lay lan dau moi huong (dung tinh than 'first test' cua sach).
    """
    tol = TOL_T * TICK
    seen_up = seen_dn = False
    out, prev = [], -99
    for i in range(max(i0, 1), min(i1, len(bars))):
        b = bars[i]
        if not (b['l'] - tol <= level <= b['h'] + tol):
            continue
        if i - prev <= 1:      # cung mot lan cham keo dai
            prev = i
            continue
        prev = i
        side = 1 if bars[i - 1]['c'] < level else -1
        if side > 0 and not seen_up:
            seen_up = True
            out.append((i, side))
        elif side < 0 and not seen_dn:
            seen_dn = True
            out.append((i, side))
    return out


def score(bars, i, level, side):
    """Diem phan ung, chuan hoa theo ATR.

    side=+1: gia tu duoi len cham (khang cu) -> muon gia BI DAY XUONG
    side=-1: gia tu tren xuong cham (ho tro)  -> muon gia BI DAY LEN
    Tra ve (thuan, nghich) tinh bang so lan ATR.
    """
    a = atr(bars, i)
    if a <= 0:
        return None
    up = dn = 0.0
    for b in bars[i + 1:i + 1 + HORIZON]:
        up = max(up, b['h'] - level)
        dn = max(dn, level - b['l'])
    fav, opp = (dn, up) if side > 0 else (up, dn)
    return fav / a, opp / a


def main():
    bars = load()
    print(f'Nap {len(bars)} nen M30  {bars[0]["dt"]:%Y-%m-%d} -> {bars[-1]["dt"]:%Y-%m-%d}')
    print(f'Bien do nen TB (ATR20 cuoi ky): {atr(bars, len(bars)-1):.2f} gia\n')

    wk = defaultdict(list)
    for b in bars:
        wk[week_key(b['dt'])].append(b)
    weeks = sorted(wk)

    res = defaultdict(list)
    for wi in range(len(weeks) - 1):
        prev_bars, next_bars = wk[weeks[wi]], wk[weeks[wi + 1]]
        if len(prev_bars) < 20 or len(next_bars) < 20:
            continue
        i0 = bars.index(next_bars[0])
        i1 = i0 + len(next_bars)
        rows = rows_of(prev_bars)
        poc, vah, val = value_area(rows)
        hv = find_hvn(rows)

        cand = [('POC tuan', poc), ('VAH tuan', vah), ('VAL tuan', val)]
        for j, (p, _, r) in enumerate(hv[:3]):
            cand.append((f'HVN tuan #{j+1}', p))
        # doi chung: 5 muc gia NGAU NHIEN trong range tuan truoc
        lo = min(b['l'] for b in prev_bars)
        hi = max(b['h'] for b in prev_bars)
        for k in range(5):
            cand.append(('~ngau nhien', lo + (hi - lo) * (k + 0.5) / 5))

        for name, lv in cand:
            if lv != lv:
                continue
            for i, side in first_touches(bars, lv, i0, i1):
                if i + HORIZON >= len(bars):
                    continue
                s = score(bars, i, lv, side)
                if s:
                    res[name].append(s)

    print('=== SUC CHAN CUA VUNG (lan cham DAU TIEN, chuan hoa theo ATR) ===')
    print('thuan = gia bat theo huong vung dang chan · nghich = gia xuyen qua')
    print('vung co gia tri khi  thuan > nghich  VA hon muc ngau nhien\n')
    print(f'{"vung":14} {"n":>3} {"thuan":>7} {"nghich":>7} {"chenh":>7} {"% chan duoc":>12}')
    base = None
    order = ['HVN tuan #1', 'HVN tuan #2', 'HVN tuan #3', 'POC tuan',
             'VAH tuan', 'VAL tuan', '~ngau nhien']
    for name in order:
        v = res.get(name)
        if not v:
            continue
        n = len(v)
        f = sum(x[0] for x in v) / n
        o = sum(x[1] for x in v) / n
        held = 100 * sum(1 for x in v if x[0] > x[1]) / n
        if name == '~ngau nhien':
            base = (f - o, held)
        print(f'{name:14} {n:3} {f:7.2f} {o:7.2f} {f-o:+7.2f} {held:11.0f}%')

    if base:
        print(f'\nMoc ngau nhien: chenh {base[0]:+.2f}, chan duoc {base[1]:.0f}%')
        print('Vung nao khong vuot moc nay => khong chung minh duoc gia tri.')

    print(f'\nLUU Y: chi {len(weeks)-1} cap tuan, n moi vung rat nho. '
          'Day la KHAO SAT, khong phai bang chung.')


if __name__ == '__main__':
    main()
