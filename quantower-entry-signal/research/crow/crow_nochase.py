#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHUYEN PHAT HIEN TIEU CUC THANH CAI TIEN CHO HE DANG CHAY.
================================================================================
Phat hien tu crow_run.py: vao lenh o CLOSE cua mot nen bien dong lon, khi close nam SAT
CUC TRI theo huong vao ("chase") la nhom te nhat (EV -0.24..-0.29 so voi -0.05 khi close
nam giua nen). Cau hoi: luat "KHONG CHASE" co cai thien CBR v5 dang ship khong?

Cach do (KHONG sua cbr_v6.py — file dong bang): chay baseline CBR v5 y nguyen, roi PARTITION
tap lenh theo 2 tieu chi tinh tai NEN VAO LENH:
  chase_rng  = rng_nen_vao >= CH_K * medrng(100 nen truoc)      (nen vao la nen bien dong lon)
  chase_pos  = cpos >= CH_POS (LONG) / <= 1-CH_POS (SHORT)      (close sat cuc tri thuan huong)
  CHASE = chase_rng AND chase_pos
Neu nhom CHASE co EV thap hon ro (>= 0.30 theo quy tac partition cua repo) va n du lon
=> de xuat them gate. Neu khong => bao KHONG, khong sua indicator.

Chay: python3 crow_nochase.py
"""
import sys, os, statistics as st
from collections import deque, defaultdict

R = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research"
sys.path.insert(0, R)
sys.path.insert(0, os.path.join(R, "wyckoff"))
import entry_dxfeed as E
import cbr_v6
from v7 import report

TICK = E.TICK


def add_medrng(B, lb=100):
    dq = deque()
    for b in B:
        b['medrng'] = st.median(dq) if len(dq) >= 20 else None
        dq.append(b['rng'])
        if len(dq) > lb:
            dq.popleft()


def is_chase(B, s, k, pos):
    b = B[s['i']]
    if b['medrng'] is None or b['medrng'] <= 0:
        return False
    big = b['rng'] >= k * b['medrng']
    cp = b['cpos'] if s['side'] == 'LONG' else 1 - b['cpos']
    return big and cp >= pos


def main():
    B = E.load_m1()
    vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf
    cbr_v6.prepare(B)
    add_medrng(B)
    print(f"M1={len(B)} bars volfloor={vf}")
    S0 = cbr_v6.scan(B, cbr_v6.cfg(), vf, None)
    S0 = [s for s in S0 if s['ym'] in report.MONTHS]
    print("\n=== BASELINE CBR v5 shipped (RR3, loc phien chet) ===")
    report.line("v5 baseline", S0)
    print("\n=== PARTITION theo CHASE (nen vao lenh bien dong lon + close sat cuc tri) ===")
    for k in (1.5, 2.0, 2.5):
        for pos in (0.70, 0.80, 0.90):
            keep = [s for s in S0 if not is_chase(B, s, k, pos)]
            drop = [s for s in S0 if is_chase(B, s, k, pos)]
            print(f"\n-- CH_K={k} CH_POS={pos}")
            report.partition(f"KHONG chase (giu)", keep, "CHASE (bi loai)", drop, min_n_drop=8)
    print("\n=== DOI CHUNG: chi rieng tung thanh phan ===")
    for k in (1.5, 2.0, 2.5):
        keep = [s for s in S0 if not (B[s['i']]['medrng'] and B[s['i']]['rng'] >= k * B[s['i']]['medrng'])]
        drop = [s for s in S0 if (B[s['i']]['medrng'] and B[s['i']]['rng'] >= k * B[s['i']]['medrng'])]
        print(f"\n-- chi 'nen vao bien dong lon' K={k}")
        report.partition("nen vao binh thuong", keep, "nen vao rat to", drop, min_n_drop=8)
    for pos in (0.70, 0.80, 0.90):
        keep, drop = [], []
        for s in S0:
            cp = B[s['i']]['cpos'] if s['side'] == 'LONG' else 1 - B[s['i']]['cpos']
            (drop if cp >= pos else keep).append(s)
        print(f"\n-- chi 'close sat cuc tri' POS={pos}")
        report.partition("close khong sat cuc tri", keep, "close sat cuc tri", drop, min_n_drop=8)


if __name__ == '__main__':
    main()
