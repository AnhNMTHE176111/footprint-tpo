#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_research.py — HVN tuan/ngay co that su la vung phan ung tot khong?

BOI CANH: trader pro (ban cua nguoi dung) noi:
  - KHONG quan tam VAH/VAL/POC/dong-mo cua tung phien A/Au
  - Canh gia o HVN cua TPO TUAN va NGAY, cong VWAP
  - Lenh dep gan day: canh mua o HVN weekly

M30SessionZones hien tai lam NGUOC LAI: no dung bien VA phien + dinh/day phien,
va KHONG co dong code nao tinh HVN (comment dau ProfileEngine noi doi).

Script nay do bang so, tren du lieu that, xem vung nao phan ung tot hon.

NGUON: data-export/tpo-data/tpo-daily.csv  (thuc te la bar M30, 26 ngay 30/6-30/7)
Chay: python3 quantower-tpo-suite/hvn_research.py
"""
import csv, os
from collections import defaultdict
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data-export/tpo-data/tpo-daily.csv')
TICK = 0.1


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


def rows_of(bars, step=TICK, use_volume=True):
    """Hang gia -> trong so. Volume rai deu tren range nen (xap xi: CSV khong co
    footprint tung muc gia). TPO = dem nen phu."""
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
    """ProfileEngine.ValueArea — rule 2 hang 70%."""
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


def find_hvn(rows, smooth_ticks=5, min_ratio=1.5, min_sep_ticks=20):
    """HVN = dinh CUC BO cua phan bo khoi luong theo gia.

    Khac POC: POC chi co 1 (dinh cao nhat). HVN co the co nhieu — moi noi
    khoi luong tu tap thanh 'nut'. Day la thu trader pro canh gia.

    Cach lam:
      1. Lam muot phan bo bang cua so +-smooth_ticks (khu rang cua tick le)
      2. Lay diem cao hon ca 2 ben (dinh cuc bo)
      3. Giu dinh co trong so >= min_ratio * trung binh (du 'cao' de goi la nut)
      4. Hai dinh cach nhau < min_sep_ticks thi giu cai manh hon
    Tra ve [(gia, trong_so, ty_le_so_voi_TB)] sap theo do manh giam dan.
    """
    if not rows:
        return []
    prices = sorted(rows)
    w = [rows[p] for p in prices]
    n = len(w)
    avg = sum(w) / n
    if avg <= 0:
        return []
    # lam muot
    sm = []
    for i in range(n):
        a, z = max(0, i - smooth_ticks), min(n, i + smooth_ticks + 1)
        sm.append(sum(w[a:z]) / (z - a))
    # dinh cuc bo
    peaks = []
    for i in range(1, n - 1):
        if sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] >= min_ratio * avg:
            peaks.append((prices[i], sm[i], sm[i] / avg))
    # gop dinh gan nhau
    peaks.sort(key=lambda x: -x[1])
    keep = []
    for p in peaks:
        if all(abs(p[0] - k[0]) >= min_sep_ticks * TICK for k in keep):
            keep.append(p)
    return keep


def week_key(dt):
    """Thu 2 cua tuan chua dt."""
    d = dt.date() - timedelta(days=dt.weekday())
    return d


def touches(bars, level, start_idx, tol_ticks=5):
    """Tra ve list index cac nen CHAM muc gia (lan dau moi lan tiep can).

    'Cham' = [Low,High] cua nen phu level +- tol. Gop cac nen lien tiep cung
    mot lan cham thanh 1 su kien (khong dem trung).
    """
    tol = tol_ticks * TICK
    ev, prev = [], -99
    for i in range(start_idx, len(bars)):
        b = bars[i]
        if b['l'] - tol <= level <= b['h'] + tol:
            if i - prev > 1:
                ev.append(i)
            prev = i
    return ev


def reaction(bars, i, level, horizon=8):
    """Do phan ung sau khi cham level tai nen i.

    Tra ve (bat_len_gia, bat_xuong_gia) = khoang cach xa nhat gia di duoc
    len/xuong trong `horizon` nen ke tiep, tinh tu level.
    """
    up = dn = 0.0
    for b in bars[i + 1:i + 1 + horizon]:
        up = max(up, b['h'] - level)
        dn = max(dn, level - b['l'])
    return up, dn


def main():
    bars = load()
    print(f'Nap {len(bars)} nen  {bars[0]["dt"]} -> {bars[-1]["dt"]}')
    step = (bars[1]['dt'] - bars[0]['dt']).total_seconds() / 60
    print(f'Khoang cach nen: {step:.0f} phut (file ten "daily" nhung la bar M{step:.0f})\n')

    # ---- gom theo tuan / ngay -------------------------------------------
    wk, dy = defaultdict(list), defaultdict(list)
    for b in bars:
        wk[week_key(b['dt'])].append(b)
        dy[b['dt'].date()].append(b)

    print('=== PROFILE TUAN: POC vs HVN ===')
    print(f'{"tuan bat dau":13} {"nen":>4} {"POC":>8} {"VAH":>8} {"VAL":>8}  HVN (gia × ty le so TB)')
    weeks = sorted(wk)
    for w in weeks:
        bs = wk[w]
        rows = rows_of(bs)
        poc, vah, val = value_area(rows)
        hv = find_hvn(rows)
        hs = '  '.join(f'{p:.1f}×{r:.1f}' for p, _, r in hv[:5])
        print(f'{w!s:13} {len(bs):4} {poc:8.1f} {vah:8.1f} {val:8.1f}  {hs}')

    # ---- so suc phan ung: HVN tuan  vs  bien VA phien -------------------
    print('\n=== DO SUC PHAN UNG CUA TUNG LOAI VUNG ===')
    print('Cach do: moi lan gia cham vung (±5t), xem 8 nen sau do gia bat ra bao xa.')
    print('"bat thuan" = bat theo huong DUNG cua vung (chan tren -> xuong, chan duoi -> len).\n')

    # dung vung cua tuan TRUOC de test tren tuan SAU (khong nhin tuong lai)
    res = defaultdict(list)
    for wi in range(len(weeks) - 1):
        prev_bars = wk[weeks[wi]]
        next_bars = wk[weeks[wi + 1]]
        if len(prev_bars) < 20 or len(next_bars) < 20:
            continue
        i0 = bars.index(next_bars[0])
        rows = rows_of(prev_bars)
        poc, vah, val = value_area(rows)
        hv = find_hvn(rows)

        cand = [('POC tuan', poc), ('VAH tuan', vah), ('VAL tuan', val)]
        for j, (p, _, r) in enumerate(hv[:3]):
            cand.append((f'HVN tuan #{j+1}', p))

        for name, lv in cand:
            if lv != lv:
                continue
            for i in touches(bars, lv, i0):
                if i + 8 >= len(bars):
                    continue
                up, dn = reaction(bars, i, lv)
                res[name].append((up, dn, max(up, dn)))

    print(f'{"vung":14} {"so lan cham":>11} {"bat TB (gia)":>13} {"bat >=3 gia":>12} {"bat >=5 gia":>12}')
    for name in sorted(res, key=lambda k: -len(res[k])):
        v = res[name]
        if not v:
            continue
        n = len(v)
        avg = sum(x[2] for x in v) / n
        p3 = 100 * sum(1 for x in v if x[2] >= 3.0) / n
        p5 = 100 * sum(1 for x in v if x[2] >= 5.0) / n
        print(f'{name:14} {n:11} {avg:13.2f} {p3:11.0f}% {p5:11.0f}%')

    print('\nLUU Y: n nho, 26 ngay / 4 tuan. Day la KHAO SAT dinh huong, chua ket luan.')


if __name__ == '__main__':
    main()
