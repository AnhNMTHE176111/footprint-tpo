#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measure_confluence.py — kiem dinh dung CAI NGUOI HOC THUC SU DANH.

Hai phep do truoc (thang/thua va phan ung lien tuc) deu tra loi: HVN phien truoc,
dung MOT MINH, khong hon muc boc ngau nhien. Nhung do KHONG phai cach CORVEN danh.
Theo ghi chu: pro trader canh lenh o **HVN tuan / HVN gop 3 tuan + VWAP**, tuc
HOP LUU hai thu, chu khong phai cham HVN la vao.

Script nay do dung the:
  - HVN gop 15 phien (~3 tuan) va HVN gop 5 phien (~1 tuan), khong chi 1 phien
  - loc HOP LUU: moc phai nam gan VWAP phien tai dung luc cham
  - so voi: moc do nhung KHONG hop luu, va muc ngau nhien cung phien
"""
import os, random, sys, statistics as st
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dense_prep import load, BARS
from calib_hvn_dense import find_hvn
from measure_dense import EXTRA_ROLL, ROLL_PAD, wilson, TP, SL, HORIZON

LOOK = 30
RNG = random.Random(5)


def load_bar_vol():
    """bar_idx -> (datetime, volume)  va  datetime -> volume."""
    vol = {}
    with open(BARS, encoding='utf-8-sig') as f:
        hdr = f.readline().rstrip('\n').split(',')
        ix = {k: i for i, k in enumerate(hdr)}
        for line in f:
            c = line.rstrip('\n').split(',')
            try:
                vol[c[ix['datetime']]] = float(c[ix['bar_volume']])
            except ValueError:
                vol[c[ix['datetime']]] = 0.0
    return vol


def session_vwap(bars, volmap):
    """VWAP neo dau phien, tra list cung do dai bars."""
    pv = v = 0.0
    out = []
    for b in bars:
        typ = (b[2] + b[3] + b[4]) / 3.0
        vv = volmap.get(b[0], 0.0)
        pv += typ * vv
        v += vv
        out.append(pv / v if v > 0 else b[4])
    return out


def trade(bars, k0, side):
    entry = bars[k0][4]
    sl_p, tp_p = entry - SL*side, entry + TP*side
    for j in range(k0+1, min(k0+1+HORIZON, len(bars))):
        h, l = bars[j][2], bars[j][3]
        if (l <= sl_p) if side > 0 else (h >= sl_p): return 0
        if (h >= tp_p) if side > 0 else (l <= tp_p): return 1
    return None


def touch(bars, level):
    for k in range(1, len(bars) - LOOK):
        if bars[k][3] <= level <= bars[k][2]:
            return k, (1 if bars[k-1][4] > level else -1)
    return None


def react(bars, k, side, level):
    seg = bars[k:k+LOOK]
    hi = max(b[2] for b in seg); lo = min(b[3] for b in seg)
    return (level-lo, hi-level) if side > 0 else (hi-level, level-lo)


def stat(nm, recs):
    if not recs:
        print(f"  {nm:<46} chua co ca"); return
    w = sum(1 for r in recs if r['res'] == 1)
    l = sum(1 for r in recs if r['res'] == 0)
    n = w + l
    pen = st.median([r['pen'] for r in recs]); bo = st.median([r['bo'] for r in recs])
    if n:
        lo, hi = wilson(w, n)
        print(f"  {nm:<46} n={n:>4}  thang={100*w/n:5.1f}% CI=[{100*lo:4.1f},{100*hi:5.1f}]  "
              f"xuyen={pen:4.2f} bat={bo:4.2f} bat/xuyen={bo/pen if pen else 0:4.2f}")
    else:
        print(f"  {nm:<46} n=0")


def main():
    d = load(); volmap = load_bar_vol()
    prof, sess = d['profiles'], d['sessions']
    rolls = set(d['rolls']) | set(EXTRA_ROLL)
    days = sorted(sess); idx = {x: i for i, x in enumerate(days)}
    bad = set()
    for i, dd in enumerate(days):
        if dd in rolls:
            for j in range(max(0, i-ROLL_PAD), min(len(days), i+ROLL_PAD+1)):
                bad.add(days[j])

    TOL = 3.0        # "gan VWAP" = trong 3 gia (dung bang dung lo cua nguoi hoc)
    out = defaultdict(list)
    for dd in days:
        i = idx[dd]
        if i < 20 or dd in bad: continue
        bars = sess[dd]
        if len(bars) < LOOK + HORIZON + 10: continue
        vw = session_vwap(bars, volmap)

        def agg(nsess):
            a = defaultdict(float); c = 0
            for j in range(i-1, -1, -1):
                dj = days[j]
                if dj in bad or dj not in prof: continue
                for k, v in prof[dj].items(): a[k] += v
                c += 1
                if c == nsess: break
            return dict(a) if c == nsess and len(a) >= 50 else None

        srcs = [('HVN ngay', agg(1)), ('HVN tuan (5 phien)', agg(5)),
                ('HVN 3 tuan (15 phien)', agg(15))]
        ps = sorted(prof[days[i-1]]) if days[i-1] in prof else None

        for nm, rows in srcs:
            if not rows: continue
            for lv, r in find_hvn(rows)[:3]:
                t = touch(bars, lv)
                if t is None: continue
                k, side = t
                pen, bo = react(bars, k, side, lv)
                rec = dict(res=trade(bars, k, side), pen=pen, bo=bo, r=r)
                near = abs(lv - vw[k]) <= TOL
                out[nm].append(rec)
                out[f"{nm} + gan VWAP"].append(rec) if near else out[f"{nm} + XA VWAP"].append(rec)
        # doi chung ngau nhien
        if ps:
            for _ in range(3):
                rl = round(RNG.uniform(ps[0], ps[-1]), 1)
                t = touch(bars, rl)
                if t is None: continue
                k, side = t
                pen, bo = react(bars, k, side, rl)
                rec = dict(res=trade(bars, k, side), pen=pen, bo=bo, r=0)
                out['NGAU NHIEN'].append(rec)
                if abs(rl - vw[k]) <= TOL:
                    out['NGAU NHIEN + gan VWAP'].append(rec)

    print("="*104)
    print(f"HOP LUU HVN x VWAP — 'gan VWAP' = trong {TOL:.0f} gia. "
          f"xuyen/bat do trong {LOOK} nen M1.")
    print("="*104)
    stat('NGAU NHIEN (nen so sanh)', out['NGAU NHIEN'])
    stat('NGAU NHIEN + gan VWAP', out['NGAU NHIEN + gan VWAP'])
    for nm in ['HVN ngay', 'HVN tuan (5 phien)', 'HVN 3 tuan (15 phien)']:
        print()
        stat(nm, out[nm])
        stat(nm + ' + gan VWAP', out[nm + ' + gan VWAP'])
        stat(nm + ' + XA VWAP', out[nm + ' + XA VWAP'])
        strong = [r for r in out[nm + ' + gan VWAP'] if r['r'] >= 2.5]
        stat(nm + ' + gan VWAP + ti le >=x2.5', strong)


if __name__ == '__main__':
    main()


# ---------------------------------------------------------------------------
# Phu luc: nguoi hoc KHONG vao ngay lan cham dau — luat cua ho la "RETEST GIU
# VUNG". Do lai voi dieu kien do: bo lan cham dau, chi vao o lan cham THU HAI,
# va chi khi lan cham dau da bat len duoc it nhat 2 gia (tuc vung co giu).
# ---------------------------------------------------------------------------
def touch_all(bars, level, maxn=4):
    ks = []
    k = 1
    while k < len(bars) - LOOK and len(ks) < maxn:
        if bars[k][3] <= level <= bars[k][2]:
            ks.append((k, 1 if bars[k-1][4] > level else -1))
            k += 15          # phai roi khoi moc it nhat 15 nen moi tinh la lan cham moi
        k += 1
    return ks


def retest_main():
    d = load(); volmap = load_bar_vol()
    prof, sess = d['profiles'], d['sessions']
    rolls = set(d['rolls']) | set(EXTRA_ROLL)
    days = sorted(sess); idx = {x: i for i, x in enumerate(days)}
    bad = set()
    for i, dd in enumerate(days):
        if dd in rolls:
            for j in range(max(0, i-ROLL_PAD), min(len(days), i+ROLL_PAD+1)):
                bad.add(days[j])
    rng = random.Random(23)
    out = defaultdict(list)
    for dd in days:
        i = idx[dd]
        if i < 20 or dd in bad: continue
        bars = sess[dd]
        if len(bars) < LOOK + HORIZON + 10: continue

        def agg(nsess):
            a = defaultdict(float); c = 0
            for j in range(i-1, -1, -1):
                dj = days[j]
                if dj in bad or dj not in prof: continue
                for k, v in prof[dj].items(): a[k] += v
                c += 1
                if c == nsess: break
            return dict(a) if c == nsess and len(a) >= 50 else None

        def push(tag, bars, lv):
            ks = touch_all(bars, lv)
            if len(ks) < 2: return
            k1, s1 = ks[0]
            pen, bo = react(bars, k1, s1, lv)
            if bo < 2.0: return                    # lan cham dau khong giu duoc vung
            k2, s2 = ks[1]
            r = trade(bars, k2, s2)
            p2, b2 = react(bars, k2, s2, lv)
            out[tag].append(dict(res=r, pen=p2, bo=b2, r=0))

        for nm, rows in [('HVN ngay', agg(1)), ('HVN tuan', agg(5)), ('HVN 3 tuan', agg(15))]:
            if not rows: continue
            for lv, rr in find_hvn(rows)[:3]:
                push(nm, bars, lv)
        if days[i-1] in prof:
            ps = sorted(prof[days[i-1]])
            for _ in range(3):
                push('NGAU NHIEN', bars, round(rng.uniform(ps[0], ps[-1]), 1))

    print("\n" + "="*104)
    print("PHU LUC — vao o lan cham THU HAI (retest), chi khi lan cham dau bat len >= 2 gia")
    print("="*104)
    for nm in ['NGAU NHIEN', 'HVN ngay', 'HVN tuan', 'HVN 3 tuan']:
        stat(nm + ' [retest]', out[nm])


if __name__ == '__main__':
    retest_main()
