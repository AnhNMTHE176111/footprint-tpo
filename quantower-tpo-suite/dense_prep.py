#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dense_prep.py — nap export DAY 748 ngay va CHIA PHIEN CHO DUNG.

Hai viec khac han cac script cu:
  1. Phien = khoang giua 2 lan nghi cua CME (bar cach nhau > 30 phut), KHONG phai
     ngay lich UTC. Ngay lich cat doi phien: 2 tieng dau phien (22:00-24:00 UTC)
     bi tinh sang ngay hom truoc -> hinh dang profile sai ngay tu doan MO CUA.
     Phien duoc dat ten theo ngay cua bar CUOI (dung quy uoc CME: phien mo
     22:00 CN -> dong 21:00 T2 la phien "thu Hai").
  2. Danh dau phien nhiem CHO NOI HOP DONG cua /GC:XCEC (mat lien tuc gia).

Xuat ra pickle trong scratchpad de cac script do dung lai, khoi doc lai 557 MB.
"""
import os, pickle, sys
from collections import defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVEL = os.path.join(ROOT, 'data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv')
BARS  = os.path.join(ROOT, 'data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv')
CACHE = os.environ.get('DENSE_CACHE', '/tmp/dense_sessions.pkl')

GAP_MIN = 30          # bar cach nhau qua nhieu phut thi coi la sang phien moi
ROLL_JUMP = 20.0      # buoc nhay tai gio nghi 1 tieng >= nguong nay => nghi cho noi
TICK = 0.1


def _p(s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')


def build():
    # ---- 1. doc bars, chia phien, tim cho noi ----------------------------
    bars = []
    with open(BARS, encoding='utf-8-sig') as f:
        hdr = f.readline().rstrip('\n').split(',')
        ix = {k: i for i, k in enumerate(hdr)}
        for line in f:
            c = line.rstrip('\n').split(',')
            bars.append((c[ix['datetime']], float(c[ix['open']]), float(c[ix['high']]),
                         float(c[ix['low']]), float(c[ix['close']]), int(c[ix['bar_idx']])))
    bars.sort(key=lambda r: r[0])

    sess_of_bar = {}          # bar_idx -> ten phien
    sessions = []             # [(ten, [bar,...])]
    cur = [bars[0]]
    rolls = set()
    for i in range(1, len(bars)):
        gap = (_p(bars[i][0]) - _p(bars[i - 1][0])).total_seconds() / 60
        if gap > GAP_MIN:
            sessions.append(cur)
            # cho noi hop dong: chi xet gio nghi 1 TIENG (bo cuoi tuan/le, vi
            # khoang trong cuoi tuan that cung to bang cho noi)
            if gap < 120 and abs(bars[i][1] - bars[i - 1][4]) >= ROLL_JUMP:
                rolls.add(bars[i][0][:10])
            cur = []
        cur.append(bars[i])
    sessions.append(cur)

    named = {}
    for s in sessions:
        name = s[-1][0][:10]              # dat ten theo bar CUOI phien
        named.setdefault(name, []).extend(s)
    for name, bs in named.items():
        for b in bs:
            sess_of_bar[b[5]] = name

    # ---- 2. doc file tung muc gia, gom volume theo phien ------------------
    prof = defaultdict(lambda: defaultdict(float))
    n = 0
    with open(LEVEL, encoding='utf-8-sig') as f:
        hdr = f.readline().rstrip('\n').split(',')
        ix = {k: i for i, k in enumerate(hdr)}
        bi, pi, vi = ix['bar_idx'], ix['price'], ix['volume']
        for line in f:
            c = line.rstrip('\n').split(',')
            s = sess_of_bar.get(int(c[bi]))
            if s is None:
                continue
            prof[s][round(float(c[pi]), 1)] += float(c[vi])
            n += 1
            if n % 2_000_000 == 0:
                print(f"  ...{n:,} dong", file=sys.stderr)

    data = {
        'sessions': {k: [(b[0], b[1], b[2], b[3], b[4]) for b in sorted(v, key=lambda x: x[0])]
                     for k, v in named.items()},
        'profiles': {k: dict(v) for k, v in prof.items()},
        'rolls': sorted(rolls),
    }
    pickle.dump(data, open(CACHE, 'wb'), protocol=4)
    return data


def load():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, 'rb'))
    return build()


if __name__ == '__main__':
    d = build()
    ss = sorted(d['sessions'])
    print(f"phien: {len(ss)}   {ss[0]} -> {ss[-1]}")
    print(f"cho noi hop dong phat hien: {len(d['rolls'])}")
    for r in d['rolls']:
        print(f"   {r}")


# ---------------------------------------------------------------------------
# Bo sung: profile theo TUNG GIO, de dung lai duoc CA HAI cach gom:
#   - phien that (nghi -> nghi), va
#   - cua so 24h truot (cach ma SessionZones dang dung: dayStart = End - 24h)
# Vi gio nghi CME roi dung dau gio (21:00-22:00 / 21:59-23:00) nen ranh gioi
# phien trung ranh gioi gio => gop tu gio la khong mat gi.
# ---------------------------------------------------------------------------
HOUR_CACHE = os.environ.get('DENSE_HOURS', '/tmp/dense_hours.pkl')


def build_hours():
    bar_time = {}
    with open(BARS, encoding='utf-8-sig') as f:
        hdr = f.readline().rstrip('\n').split(',')
        ix = {k: i for i, k in enumerate(hdr)}
        for line in f:
            c = line.rstrip('\n').split(',')
            bar_time[int(c[ix['bar_idx']])] = c[ix['datetime']]
    hours = defaultdict(lambda: defaultdict(float))
    n = 0
    with open(LEVEL, encoding='utf-8-sig') as f:
        hdr = f.readline().rstrip('\n').split(',')
        ix = {k: i for i, k in enumerate(hdr)}
        bi, pi, vi = ix['bar_idx'], ix['price'], ix['volume']
        for line in f:
            c = line.rstrip('\n').split(',')
            t = bar_time.get(int(c[bi]))
            if t is None:
                continue
            hours[t[:13]][round(float(c[pi]), 1)] += float(c[vi])
            n += 1
            if n % 3_000_000 == 0:
                print(f"  ...{n:,} dong", file=sys.stderr)
    out = {k: dict(v) for k, v in hours.items()}
    pickle.dump(out, open(HOUR_CACHE, 'wb'), protocol=4)
    return out


def load_hours():
    if os.path.exists(HOUR_CACHE):
        return pickle.load(open(HOUR_CACHE, 'rb'))
    return build_hours()
