#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_va.py — KIEM DUNG/SAI cua ProfileEngine.ValueArea() tren DAP AN THAT.

Phat hien: cot POC/VAH/VAL trong tpo-m30.csv doi moi 30 phut dung dau gio
=> do la profile cua TUNG NEN M30, khong phai ca phien.

=> Co dap an cho ~139 nen M30. Gop bar M1 theo dung khung 30' roi chay
   ValueArea() cua ta, so voi dap an Quantower. Day la kiem code DUNG hay SAI,
   khong phai kiem hieu qua giao dich.

Chay: python3 quantower-tpo-suite/verify_va.py
"""
import csv, os
from collections import defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data-export/tpo-data/tpo-m30.csv')
TICK = 0.1


def load():
    out = []
    with open(SRC, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            try:
                out.append(dict(
                    dt=datetime.strptime(r['DateTime'], '%m/%d/%Y %I:%M:%S %p'),
                    h=float(r['High']), l=float(r['Low']),
                    vol=float(r['Volume'] or 0),
                    poc=float(r['POC']), vah=float(r['VAH']), val=float(r['VAL']),
                    tpo=float(r['TPO'] or 0)))
            except (ValueError, KeyError):
                continue
    out.sort(key=lambda x: x['dt'])
    return out


def value_area(rows, frac=0.70):
    """Port 1-1 ProfileEngine.ValueArea (rule 2 hang 70%)."""
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


def tpo_rows(bs, step):
    r = defaultdict(float)
    for b in bs:
        for k in range(int(round(b['l'] / step)), int(round(b['h'] / step)) + 1):
            r[k * step] += 1
    return dict(r)


def vol_rows(bs, step):
    """Xap xi: rai volume nen deu tren range cua no (CSV khong co footprint/muc gia)."""
    r = defaultdict(float)
    for b in bs:
        a, z = int(round(b['l'] / step)), int(round(b['h'] / step))
        n = z - a + 1
        if n <= 0 or b['vol'] <= 0:
            continue
        for k in range(a, z + 1):
            r[k * step] += b['vol'] / n
    return dict(r)


def main():
    bars = load()
    # gom theo khung 30' that (dung moc dau gio, giong cach Quantower dong nen M30)
    g = defaultdict(list)
    for b in bars:
        key = b['dt'].replace(minute=(b['dt'].minute // 30) * 30, second=0)
        g[key].append(b)

    groups = []
    for k in sorted(g):
        bs = g[k]
        ans = bs[-1]           # dap an QT o nen M1 cuoi cung cua khung
        if len(bs) >= 25:      # chi lay khung gan du 30 nen M1 (khong thieu du lieu)
            groups.append((k, bs, ans))

    print(f'Nen M30 co du du lieu de kiem: {len(groups)}')
    print('So sanh: Python ValueArea() vs dap an POC/VAH/VAL cua Quantower\n')

    for mode, rowf in (('TPO ', tpo_rows), ('VOL ', vol_rows)):
        for rt, tag in ((1, 'rowStep=1 tick'), (5, 'rowStep=5 tick')):
            dp = dv = dl = 0.0
            okp = 0
            n = 0
            worst = None
            for k, bs, ans in groups:
                rows = rowf(bs, TICK * rt)
                p, vh, vl = value_area(rows)
                if p != p:
                    continue
                n += 1
                ep = abs(p - ans['poc']) / TICK
                dp += ep
                dv += abs(vh - ans['vah']) / TICK
                dl += abs(vl - ans['val']) / TICK
                if ep <= 5:
                    okp += 1
                if worst is None or ep > worst[1]:
                    worst = (k, ep, p, ans['poc'])
            if n:
                print(f'{mode}{tag:16} n={n:3} | POC lech TB {dp/n:6.1f}t  '
                      f'VAH {dv/n:6.1f}t  VAL {dl/n:6.1f}t | POC trong 5t: '
                      f'{100*okp/n:5.1f}% | te nhat {worst[1]:.0f}t @ {worst[0]:%m-%d %H:%M} '
                      f'({worst[2]:.1f} vs {worst[3]:.1f})')


if __name__ == '__main__':
    main()
