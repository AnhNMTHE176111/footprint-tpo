#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reconcile_live.py — DOI CHIEU C# live vs Python replay.

Muc dich: kiem CODE DUNG hay SAI, KHONG phai kiem EV (n=5, qua nho de ket luan).

Cach lam: lay entry/SL/TP ma C# da ghi ra CSV, roi dung du lieu M1 that
(data-export/tpo-data/tpo-m30.csv — thuc te la M1) di lai tung nen ke tu luc
vao lenh, xem cham SL truoc hay TP truoc, so voi cot KQ cua C#.

Neu LECH => co bug that trong C# (hoac trong cach ta hieu logic) => dang sua.
Neu KHOP => C# chay dung nhu thiet ke.

Chay: python3 quantower-entry-signal/research/reconcile_live.py
"""
import csv, os, sys
from datetime import datetime, timedelta

# CSV bar ghi gio VN (+07:00), CSV tin hieu ghi gio UTC.
# Kiem chung: voi offset +7 thi ca 5/5 entry nam gon trong [Low,High] cua nen
# tuong ung; moi offset khac deu <=1/5. => TZ_SHIFT = 7.
TZ_SHIFT = 7

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BARS = os.path.join(ROOT, 'data-export/tpo-data/tpo-m30.csv')
SIGS = [('v7-Wyckoff', os.path.join(ROOT, 'data-export/signals/WyckoffRunner_signals.csv')),
        ('v5-Runner ', os.path.join(ROOT, 'data-export/signals/RunnerSignal_signals.csv'))]


def load_bars():
    out = []
    with open(BARS, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            try:
                out.append((datetime.strptime(r['DateTime'], '%m/%d/%Y %I:%M:%S %p'),
                            float(r['High']), float(r['Low']), float(r['Close'])))
            except (ValueError, KeyError):
                continue
    out.sort()
    return out


def replay(bars, t0, side, entry, sl, tp):
    """Di lai tung nen M1 tu t0. Tra ve (KQ, thoi diem ket thuc, so nen giu).

    Quy uoc than trong: neu 1 nen cham CA SL va TP thi tinh SL (worst case) —
    du lieu M1 khong cho biet cai nao den truoc.
    """
    n = 0
    for dt, h, l, c in bars:
        if dt <= t0:      # bo qua chinh nen vao lenh: C# vao o gia dong nen do
            continue
        n += 1
        if side == 'SHORT':
            hit_sl, hit_tp = h >= sl, l <= tp
        else:
            hit_sl, hit_tp = l <= sl, h >= tp
        if hit_sl:
            return 'LOSS', dt, n
        if hit_tp:
            return 'WIN', dt, n
    return 'DANG_CHAY', None, n


def main():
    bars = load_bars()
    print(f'Du lieu M1: {len(bars)} nen  {bars[0][0]} -> {bars[-1][0]}\n')
    tot = ok = 0
    for tag, path in SIGS:
        rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
        print(f'=== {tag}  ({len(rows)} tin hieu) ===')
        print(f'{"thoi diem":16} {"kich ban":9} {"huong":5} {"entry":>8} {"SL":>8} {"TP":>8} '
              f'| {"C#":>9} {"Python":>9} {"khop":>5} | ket thuc C# / Python')
        for r in rows:
            t0 = (datetime.strptime(r['ngay_gio'].strip()[:16], '%Y-%m-%d %H:%M')
                  + timedelta(hours=TZ_SHIFT))
            side = r['huong'].strip()
            e, sl, tp = float(r['entry']), float(r['SL']), float(r['TP'])
            kq_cs = r['KQ'].strip().upper()
            kq_py, end_py, held = replay(bars, t0, side, e, sl, tp)
            same = (kq_cs == kq_py)
            tot += 1
            ok += same
            mark = 'OK' if same else '*** LECH'
            ep = f'{end_py:%m-%d %H:%M}' if end_py else '—'
            try:   # ket thuc cua C# cung la gio UTC -> doi sang gio VN de so
                ec = (datetime.strptime(r['ket_thuc_luc'].strip()[:16], '%Y-%m-%d %H:%M')
                      + timedelta(hours=TZ_SHIFT)).strftime('%m-%d %H:%M')
            except ValueError:
                ec = '—'
            print(f'{t0:%Y-%m-%d %H:%M} {r["nhanh"]:9} {side:5} {e:8.1f} {sl:8.1f} {tp:8.1f} '
                  f'| {kq_cs:>9} {kq_py:>9} {mark:>9} | {ec} / {ep} ({held}n)')
        print()
    print(f'TONG: {ok}/{tot} khop'
          + ('  => C# chay dung nhu mo phong.' if ok == tot else '  => CO LECH, phai dieu tra.'))
    print('\nLUU Y: day la kiem CODE DUNG/SAI. n=%d qua nho de noi gi ve EV.' % tot)


if __name__ == '__main__':
    main()
