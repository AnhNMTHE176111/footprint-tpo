#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIEM CHUNG DIEU DUY NHAT CON SONG: "vao lenh khi CLOSE nen sat CUC TRI thuan huong thi te".
================================================================================
crow_nochase.py thay hieu ung nay tren CBR v5 (EV +1.40 vs +0.00) nhung n nhom bi loai chi 20
=> khong the ket luan. File nay do CUNG cau hoi o muc NEN THUAN (n ~ 30k), khong phu thuoc setup:

  Voi moi nen i "kieu nen vao lenh" (thuan huong, vratio>=1.5, than>=0.35, qua gate thanh khoan):
  tu close nen i dat 2 moc +-H*medrng (H=1.5, chuan hoa bien dong), trong 60 nen sau moc nao
  cham truoc => P(di tiep thuan huong). Do theo bin cpos_thuan = cpos (nen tang) | 1-cpos (giam).
  Neu P giam dan theo cpos => "close sat cuc tri" that su la vi tri vao lenh xau.
Doi chung: cung phep do nhung tinh tu HIGH/LOW nen (khong phai close) de tach hieu ung
  "diem vao xau" khoi "nen nay xu huong xau".

Chay: python3 crow_cpos.py
"""
import sys, os, statistics as st
from collections import defaultdict, deque

R = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research"
sys.path.insert(0, R)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entry_dxfeed as E
import crow_v1 as K

TICK = E.TICK
VF = E.VOLFLOOR_FROZEN
H = 1.5
FWD = 60
BINS = ((0.0, 0.5), (0.5, 0.65), (0.65, 0.8), (0.8, 0.9), (0.9, 1.01))


def se(p, n):
    return (p * (1 - p) / n) ** 0.5 if n > 0 else 9.9


def barrier(B, i, up, px, h):
    tgt = px + h if up else px - h
    stp = px - h if up else px + h
    for j in range(i + 1, min(len(B), i + 1 + FWD)):
        b = B[j]
        hitT = (b['hi'] >= tgt) if up else (b['lo'] <= tgt)
        hitS = (b['lo'] <= stp) if up else (b['hi'] >= stp)
        if hitT and hitS:
            return None
        if hitT:
            return 1
        if hitS:
            return 0
    return None


def main():
    B = K.prep(E.load_m1())
    rows = []
    for i, b in enumerate(B):
        if b['medrng'] is None or b['medrng'] <= 0 or b['rng'] <= 0:
            continue
        if b['v'] < VF or b['since_gap'] < E.WARMUP_AFTER_GAP or b['vma'] < VF * 0.6:
            continue
        if b['vratio'] < 1.5 or b['brat'] < 0.35 or not (b['up'] or b['dn']):
            continue
        up = b['up']
        h = H * b['medrng']
        rows.append(dict(ym=b['ym'], up=up, cposn=(b['cpos'] if up else 1 - b['cpos']),
                         rng_k=b['rng'] / b['medrng'],
                         from_close=barrier(B, i, up, b['c'], h),
                         from_ext=barrier(B, i, up, (b['hi'] if up else b['lo']), h)))
    print(f"[cpos] n nen kieu 'nen vao lenh' = {len(rows)}  ({rows[0]['ym']} -> {rows[-1]['ym']})")

    for key, lab in (('from_close', "moc tinh tu CLOSE nen (= diem vao lenh that)"),
                     ('from_ext', "DOI CHUNG: moc tinh tu HIGH/LOW nen")):
        sub = [r for r in rows if r[key] is not None]
        base = sum(r[key] for r in sub) / len(sub)
        print(f"\n=========== {lab}   n={len(sub)}  BASE P(di tiep)={100*base:.1f}%")
        for lo, hi in BINS:
            s2 = [r for r in sub if lo <= r['cposn'] < hi]
            if len(s2) < 100:
                continue
            p = sum(r[key] for r in s2) / len(s2)
            d = p - base
            print(f"   cpos_thuan [{lo:.2f},{hi:.2f})  n={len(s2):5d}  P={100*p:.1f}%  lech={100*d:+.1f}pp "
                  f"({d/se(p,len(s2)):+.1f}se) {'***' if abs(d) >= 2*se(p,len(s2)) else ''}")

    print("\n=========== KIEM SOAT: chi nen TO (rng>=2*medrng) — dung lop ma CBR v5 hay vao")
    sub = [r for r in rows if r['from_close'] is not None and r['rng_k'] >= 2.0]
    base = sum(r['from_close'] for r in sub) / len(sub)
    print(f"   n={len(sub)}  BASE={100*base:.1f}%")
    for lo, hi in BINS:
        s2 = [r for r in sub if lo <= r['cposn'] < hi]
        if len(s2) < 100:
            continue
        p = sum(r['from_close'] for r in s2) / len(s2)
        d = p - base
        print(f"   cpos_thuan [{lo:.2f},{hi:.2f})  n={len(s2):5d}  P={100*p:.1f}%  lech={100*d:+.1f}pp "
              f"({d/se(p,len(s2)):+.1f}se) {'***' if abs(d) >= 2*se(p,len(s2)) else ''}")

    print("\n=========== ON DINH THEO THANG (cpos<0.65 vs >=0.9, moc tu CLOSE)")
    bym = defaultdict(lambda: [[], []])
    for r in rows:
        if r['from_close'] is None:
            continue
        if r['cposn'] < 0.65:
            bym[r['ym']][0].append(r['from_close'])
        elif r['cposn'] >= 0.9:
            bym[r['ym']][1].append(r['from_close'])
    for ym in sorted(bym):
        a, c = bym[ym]
        if len(a) < 40 or len(c) < 40:
            continue
        print(f"   {ym}: close GIUA n={len(a):4d} P={100*sum(a)/len(a):.1f}%  |  "
              f"close SAT CUC TRI n={len(c):4d} P={100*sum(c)/len(c):.1f}%  "
              f"chenh={100*(sum(a)/len(a)-sum(c)/len(c)):+.1f}pp")


if __name__ == '__main__':
    main()
