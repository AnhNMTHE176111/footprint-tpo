#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backtest_zones_v1v2.py — BACKTEST so sanh suc chan cua vung v1 vs v2, tren du
lieu THAT, KHONG nhin tuong lai (walk-forward tung ngay).

Sua loi cua hvn_research.py (do "gia bat bao xa" -> 100% moi vung, vi do bien
dong thi truong khong phai suc chan) va n qua nho cua hvn_research2.py (chi
gop theo TUAN -> 4 diem). Ban nay WALK-FORWARD THEO NGAY: moi ngay, dung du
lieu CHI toi ngay hom truoc de tinh vung, roi kiem phan ung trong ngay hien
tai. Voi 26 ngay du lieu, moi vung/loai co ~20 ngay quan sat -> n lon hon.

Do dung: THUAN (gia bi day theo huong vung dang chan) TRU NGHICH (gia xuyen
qua), chuan hoa theo ATR, CHI o LAN CHAM DAU TIEN moi huong (dung tinh than
sach: "chi giao dich o lan cham dau tien"). So voi MOC NGAU NHIEN lam doi
chung trong CUNG ngay, CUNG so luong cham, de loai tru viec "ngay bien dong
manh thi vung nao cung thang".

NGUON: data-export/tpo-data/tpo-daily.csv (bar M30, 26 ngay 30/6-30/7)
Chay: python3 quantower-tpo-suite/backtest_zones_v1v2.py
"""
import os
from collections import defaultdict
from datetime import timedelta

from verify_zones_v2 import (load, M30_FILE, atr, sessions_of, find_zones, TICK)

HORIZON = 8       # so nen M30 quan sat sau khi cham (~4 tieng)
TOL_T = 5         # dung sai coi la "cham" (tick)


def first_touches(bars, level, i0, i1):
    tol = TOL_T * TICK
    seen_up = seen_dn = False
    out, prev = [], -99
    for i in range(max(i0, 1), min(i1, len(bars))):
        b = bars[i]
        if not (b['l'] - tol <= level <= b['h'] + tol):
            continue
        if i - prev <= 1:
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
    bars = load(M30_FILE)
    sessions = sessions_of(bars)
    print(f'Nap {len(bars)} nen M30  {bars[0]["dt"]:%Y-%m-%d} -> {bars[-1]["dt"]:%Y-%m-%d}')
    print(f'{len(sessions)} phien (Á/Âu/Mỹ theo gap)\n')

    # ngay giao dich (ranh gioi 00:00) de walk-forward
    days = sorted(set(b['dt'].date() for b in bars))
    print(f'{len(days)} ngay giao dich\n')

    res = defaultdict(lambda: defaultdict(list))   # res[version][type] = [(fav,opp),...]
    n_days_used = 0

    for di in range(3, len(days) - 1):        # can >=3 ngay truoc de co du phien
        day = days[di]
        day_bars_idx = [i for i, b in enumerate(bars) if b['dt'].date() == day]
        if len(day_bars_idx) < 10:
            continue
        i0, i1 = day_bars_idx[0], day_bars_idx[-1] + 1
        now_price = bars[i0]['o']    # gia mo ngay = "gia hien tai" luc tinh vung

        # phien da dong TRUOC ngay nay (khong nhin tuong lai)
        closed_sessions = [(lab, fr, to) for lab, fr, to in sessions if to < i0]
        if len(closed_sessions) < 4:
            continue
        n_days_used += 1

        for ver in ('v1', 'v2'):
            zs = find_zones(bars, closed_sessions, now_price, version=ver)
            # doi chung ngau nhien: N muc gia rai deu trong range 5 ngay truoc
            lookback = bars[max(0, i0 - 5 * 20):i0]
            if not lookback:
                continue
            lo, hi = min(b['l'] for b in lookback), max(b['h'] for b in lookback)
            n_rand = max(3, len(zs))
            rand_levels = [lo + (hi - lo) * (k + 0.5) / n_rand for k in range(n_rand)]

            for z in zs:
                for i, side in first_touches(bars, z.center, i0, i1):
                    if i + HORIZON >= len(bars):
                        continue
                    s = score(bars, i, z.center, side)
                    if s:
                        res[ver][z.type].append(s)
                        res[ver]['__ALL__'].append(s)
            for lv in rand_levels:
                for i, side in first_touches(bars, lv, i0, i1):
                    if i + HORIZON >= len(bars):
                        continue
                    s = score(bars, i, lv, side)
                    if s:
                        res[ver]['~random'].append(s)

    print(f'Walk-forward tren {n_days_used} ngay (moi ngay chi dung du lieu QUA KHU de tinh vung)\n')
    print('=== KET QUA: thuan/nghich chuan hoa ATR, lan cham DAU TIEN moi huong ===\n')

    for ver in ('v1', 'v2'):
        print(f'--- {ver.upper()} ---')
        print(f'{"loai vung":16} {"n":>4} {"thuan":>7} {"nghich":>7} {"chenh":>7} {"% thang":>8}')
        order = sorted(res[ver], key=lambda k: -len(res[ver][k]))
        rand_edge = None
        for typ in order:
            v = res[ver][typ]
            if not v:
                continue
            n = len(v)
            f = sum(x[0] for x in v) / n
            o = sum(x[1] for x in v) / n
            held = 100 * sum(1 for x in v if x[0] > x[1]) / n
            tag = ' <== TONG' if typ == '__ALL__' else (' <== DOI CHUNG' if typ == '~random' else '')
            print(f'{typ:16} {n:4} {f:7.2f} {o:7.2f} {f-o:+7.2f} {held:7.0f}%{tag}')
            if typ == '~random':
                rand_edge = f - o
        print()

    print('=== SO SANH TONG (loai __ALL__, khong tinh doi chung) ===')
    for ver in ('v1', 'v2'):
        v = res[ver].get('__ALL__', [])
        vr = res[ver].get('~random', [])
        if not v:
            continue
        n = len(v)
        f = sum(x[0] for x in v) / n
        o = sum(x[1] for x in v) / n
        held = 100 * sum(1 for x in v if x[0] > x[1]) / n
        rn = len(vr)
        rf = sum(x[0] for x in vr) / rn if rn else float('nan')
        ro = sum(x[1] for x in vr) / rn if rn else float('nan')
        rheld = 100 * sum(1 for x in vr if x[0] > x[1]) / rn if rn else float('nan')
        beats_random = 'CO' if (f - o) > (rf - ro) else 'KHONG'
        print(f'{ver.upper()}: vung thuc n={n:3} chenh={f-o:+.2f} thang={held:.0f}%  |  '
              f'ngau nhien n={rn:3} chenh={rf-ro:+.2f} thang={rheld:.0f}%  '
              f'=> vung co hon ngau nhien? {beats_random}')

    print('\nLUU Y: day la KHAO SAT tren 26 ngay. So lan cham moi loai vung van nho.')
    print('Khong dung ket qua nay de sua cau hinh dong bang (v7 WyckoffRunner).')


if __name__ == '__main__':
    main()
