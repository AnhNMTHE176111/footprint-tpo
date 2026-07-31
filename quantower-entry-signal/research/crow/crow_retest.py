#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THI NGHIEM 2b — muc bubble co thanh HO TRO/KHANG CU that khong (co KIEM SOAT thien lech)?
================================================================================
Vi sao can: thi nghiem 2 trong crow_bubble.py do "muc bubble co bi dong vuot khong" -> BI THIEN
LECH HINH HOC: bubble o day nen (pos thap) thi NAM XA close hon => tat nhien kho bi xuyen hon.
Ket qua +12pp cho pos<0.2 KHONG the dung de ket luan gi.

Cach do dung cho cau hoi "muc do co thanh ho tro khong": CHI XET nhung lan gia DA QUAY LAI
CHAM muc do (retest), roi hoi: no BAT LEN hay XUYEN QUA?
  - Nen i co bubble (o aggressor lon nhat, aggressor thuan huong nen), vratio>=1.5.
  - Tim nen j dau tien trong RETEST_W nen sau co: (buy bubble) lo_j <= px  |  (sell) hi_j >= px.
    Bo qua neu chinh nen i+1.. da o phia sai (gia chua bao gio roi khoi muc).
  - Tu j: BAT = cham px + H*medrng truoc khi DONG vuot px - PEN*tick.  XUYEN = nguoc lai.
    Cung nen ca hai -> loai (mo ho).
  - Do P(BAT) theo bin pos_n. Kiem soat them: phan tang theo DIST = (close_i - px)/medrng
    (khoang cach chuan hoa) — neu hieu ung con song trong cung tang DIST thi moi la that.
Doi chung ngau nhien: lay muc GIA NGAU NHIEN trong chinh nen i (uniform trong [lo,hi]) rôi do
  P(BAT) y het cach tren -> base "muc bat ky trong nen", tach hieu ung 'bubble' khoi 'muc nao cung the'.

Chay: python3 crow_retest.py
"""
import sys, os, random, statistics as st
from collections import defaultdict

R = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research"
sys.path.insert(0, R)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entry_dxfeed as E
import fp_merged
import crow_v1 as K

TICK = E.TICK
VF = E.VOLFLOOR_FROZEN
RETEST_W = 60      # cua so cho retest
AFTER_W = 60       # cua so phan xu sau khi cham
H = 1.5            # muc TP = px + H*medrng
PEN = 5            # xuyen = dong vuot px 5 tick
BINS = ((0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01))
rnd = random.Random(20260731)


def se(p, n):
    return (p * (1 - p) / n) ** 0.5 if n > 0 else 9.9


def verdict(B, i, up, px, medrng):
    """Tra ('BAT'|'XUYEN'|None, dist_bars). None = khong retest / mo ho / het data."""
    j0 = None
    for j in range(i + 1, min(len(B), i + 1 + RETEST_W)):
        b = B[j]
        if (b['lo'] <= px) if up else (b['hi'] >= px):
            j0 = j
            break
    if j0 is None:
        return None, None
    tgt = px + H * medrng if up else px - H * medrng
    lim = px - PEN * TICK if up else px + PEN * TICK
    for j in range(j0, min(len(B), j0 + AFTER_W)):
        b = B[j]
        hitT = (b['hi'] >= tgt) if up else (b['lo'] <= tgt)
        hitS = (b['c'] < lim) if up else (b['c'] > lim)
        if hitT and hitS:
            return None, None
        if hitT:
            return 'BAT', j0 - i
        if hitS:
            return 'XUYEN', j0 - i
    return None, None


def bub_price(b, up, mode='aggr'):
    lv = b.get('levels') or {}
    if not lv:
        return None
    if mode == 'poc':
        return max(lv, key=lambda k: lv[k]['vol'])
    key = 'ask' if up else 'bid'
    if max(lv[k][key] for k in lv) <= 0:
        return None
    return max(lv, key=lambda k: lv[k][key])


def main():
    B = fp_merged.load_merged()
    K.prep(B)
    rows = []
    for i, b in enumerate(B):
        if not b.get('has_delta') or b['rng'] <= 0 or b['medrng'] is None:
            continue
        if b['v'] < VF or b['since_gap'] < E.WARMUP_AFTER_GAP or (b.get('v_fp') or 0) <= 0:
            continue
        if b['medrng'] <= 0:
            continue
        if not (b['up'] or b['dn']) or b['vratio'] < 1.5:
            continue
        up = b['up']
        px = bub_price(b, up, 'aggr')
        if px is None:
            continue
        pos = (px - b['lo']) / b['rng']
        pos_n = pos if up else 1 - pos
        v, dbars = verdict(B, i, up, px, b['medrng'])
        # doi chung: muc ngau nhien trong nen
        rpx = round(b['lo'] + rnd.random() * b['rng'], 1)
        rv, _ = verdict(B, i, up, rpx, b['medrng'])
        rows.append(dict(i=i, ym=b['ym'], up=up, pos_n=pos_n, px=px,
                         dist=abs(b['c'] - px) / b['medrng'], v=v, rv=rv,
                         rpos_n=((rpx - b['lo']) / b['rng']) if up else (1 - (rpx - b['lo']) / b['rng'])))
    ok = [r for r in rows if r['v'] is not None]
    print(f"[retest] nen co bubble & vratio>=1.5: {len(rows)} | co phan xu (retest+ket cuc ro): {len(ok)}")
    base = sum(1 for r in ok if r['v'] == 'BAT') / len(ok)
    print(f"\n=========== P(BAT khi gia quay lai CHAM muc bubble)   BASE = {100*base:.1f}%  (n={len(ok)})")
    for lo, hi in BINS:
        s2 = [r for r in ok if lo <= r['pos_n'] < hi]
        if len(s2) < 50:
            print(f"   pos_n [{lo:.1f},{hi:.1f})  n={len(s2):5d} (qua it)")
            continue
        p = sum(1 for r in s2 if r['v'] == 'BAT') / len(s2)
        d = p - base
        print(f"   pos_n [{lo:.1f},{hi:.1f})  n={len(s2):5d}  P(BAT)={100*p:.1f}%  lech={100*d:+.1f}pp "
              f"({d/se(p,len(s2)):+.1f}se) {'***' if abs(d) >= 2*se(p,len(s2)) else ''}")

    print("\n=========== KIEM SOAT: cung tang khoang cach DIST=(|close-px|/medrng)")
    for dlo, dhi in ((0.0, 0.3), (0.3, 0.6), (0.6, 1.0), (1.0, 9.9)):
        sub = [r for r in ok if dlo <= r['dist'] < dhi]
        if len(sub) < 200:
            continue
        b2 = sum(1 for r in sub if r['v'] == 'BAT') / len(sub)
        print(f"  -- DIST [{dlo:.1f},{dhi:.1f})  n={len(sub):5d}  base={100*b2:.1f}%")
        for lo, hi in ((0.0, 0.4), (0.4, 0.7), (0.7, 1.01)):
            s2 = [r for r in sub if lo <= r['pos_n'] < hi]
            if len(s2) < 50:
                continue
            p = sum(1 for r in s2 if r['v'] == 'BAT') / len(s2)
            d = p - b2
            print(f"     pos_n [{lo:.1f},{hi:.2f})  n={len(s2):5d}  P(BAT)={100*p:.1f}%  lech={100*d:+.1f}pp "
                  f"({d/se(p,len(s2)):+.1f}se) {'***' if abs(d) >= 2*se(p,len(s2)) else ''}")

    print("\n=========== DOI CHUNG: muc NGAU NHIEN trong cung nen (khong phai bubble)")
    okr = [r for r in rows if r['rv'] is not None]
    br = sum(1 for r in okr if r['rv'] == 'BAT') / len(okr)
    print(f"   muc ngau nhien: n={len(okr)}  P(BAT)={100*br:.1f}%   | bubble: {100*base:.1f}% "
          f"(chenh {100*(base-br):+.1f}pp)")
    for lo, hi in BINS:
        s2 = [r for r in okr if lo <= r['rpos_n'] < hi]
        if len(s2) < 50:
            continue
        p = sum(1 for r in s2 if r['rv'] == 'BAT') / len(s2)
        print(f"   [ngau nhien] pos_n [{lo:.1f},{hi:.1f})  n={len(s2):5d}  P(BAT)={100*p:.1f}%  "
              f"lech={100*(p-br):+.1f}pp ({(p-br)/se(p,len(s2)):+.1f}se)")

    print("\n=========== ON DINH THEO THANG (pos_n<0.4 vs >=0.7)")
    bym = defaultdict(lambda: [[], []])
    for r in ok:
        if r['pos_n'] < 0.4:
            bym[r['ym']][0].append(1 if r['v'] == 'BAT' else 0)
        elif r['pos_n'] >= 0.7:
            bym[r['ym']][1].append(1 if r['v'] == 'BAT' else 0)
    for ym in sorted(bym):
        a, b2 = bym[ym]
        if len(a) < 30 or len(b2) < 30:
            continue
        print(f"   {ym}: bubble PHIA SAU n={len(a):4d} P={100*sum(a)/len(a):.1f}%  |  "
              f"SAT CUC TRI n={len(b2):4d} P={100*sum(b2)/len(b2):.1f}%  chenh={100*(sum(a)/len(a)-sum(b2)/len(b2)):+.1f}pp")


if __name__ == '__main__':
    main()
