#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ROUND 3 — 3 y tuong tu feedback user (2026-07-28):
  (1) Kieu1 'loanh quanh vung'  = HOVER_H (cho gia dao quanh vung, huy khi pha xa)
  (2) Kieu2 'quet roi rut'      = SWEEP (false-break + rut manh nguoc lai)
  (3) VWAP bias co margin        = 'nam han' tren/duoi VWAP
Chay tren dxFeed 5-7/2026. Baseline = hop luu>=2, RR1.5."""
import entry_dxfeed as E

E.B=E.load_m1()
E.VOLFLOOR_AUTO=E.calc_volfloor(E.B)
pool=E.build_zones(E.B)
E.USE_DELTA=False
print(f"M1={len(E.B)} zones={len(pool)} volfloor={E.VOLFLOOR_AUTO:.0f}")

def go(C,label):
    C=E.prep(dict(C))
    raw=E.run(E.B,pool,C)
    if C['SWEEP_ON']:raw=raw+E.scan_sweep(E.B,pool,C)
    sig=E.dedup(raw,pool,C)
    sig=[s for s in sig if s['ym'] in ('2026-05','2026-06','2026-07')]
    E.evalset(E.B,sig,label,C,by_month=True)

mk=E.make
go(mk(),"BASE hop luu>=2 (tham chieu)")

print("\n===== Y1: HOVER_H 'loanh quanh vung' (Kieu1) =====")
go(mk(HOVER_H=1.0),"Y1a HOVER 1.0 gia")
go(mk(HOVER_H=2.0),"Y1b HOVER 2.0 gia")
go(mk(HOVER_H=3.0),"Y1c HOVER 3.0 gia")

print("\n===== Y2: SWEEP 'quet roi rut' (Kieu2b) — them vao baseline =====")
go(mk(SWEEP_ON=True,SWEEP_SPIKE=0.3,SWEEP_REJECT=0.3),"Y2a sweep 0.3/0.3")
go(mk(SWEEP_ON=True,SWEEP_SPIKE=0.5,SWEEP_REJECT=0.5),"Y2b sweep 0.5/0.5")
go(mk(SWEEP_ON=True,SWEEP_SPIKE=0.2,SWEEP_REJECT=0.4),"Y2c sweep 0.2/0.4")

print("\n===== Y3: VWAP bias co MARGIN 'nam han' =====")
go(mk(VWAP_ON=True,VWAP_MARGIN=0.0),"Y3a vwap margin 0 (nhu F2 cu)")
go(mk(VWAP_ON=True,VWAP_MARGIN=2.0),"Y3b vwap margin 2 gia")
go(mk(VWAP_ON=True,VWAP_MARGIN=5.0),"Y3c vwap margin 5 gia")

print("\n===== KET HOP tot nhat (se dien sau khi xem tung y) =====")
go(mk(HOVER_H=2.0,SWEEP_ON=True,SWEEP_SPIKE=0.3,SWEEP_REJECT=0.3),"C1 hover2 + sweep")
go(mk(MIN_CONFL=3,HOVER_H=2.0,SWEEP_ON=True),"C2 hop luu>=3 + hover2 + sweep")
