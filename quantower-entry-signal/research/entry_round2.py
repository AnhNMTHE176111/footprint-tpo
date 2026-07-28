#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ROUND 2 — stress-test cluster>=3 (co overfit khong?) + trend + RR sensitivity."""
import entry_dxfeed as E

E.B=E.load_m1()
E.VOLFLOOR_AUTO=E.calc_volfloor(E.B)
pool=E.build_zones(E.B)
E.USE_DELTA=False
print(f"M1={len(E.B)} zones={len(pool)} volfloor={E.VOLFLOOR_AUTO:.0f}")

def go(C,label,months=('2026-05','2026-06','2026-07')):
    C=E.prep(dict(C))
    raw=E.run(E.B,pool,C);sig=E.dedup(raw,pool,C)
    if months:sig=[s for s in sig if s['ym'] in months]
    E.evalset(E.B,sig,label,C,by_month=True)
    return sig

mk=E.make
print("\n##### CLUSTER>=3 chi tiet (co bi 1 bucket keo khong?)")
go(mk(MIN_CONFL=3),"G1 cluster>=3")
print("\n##### cluster>=3 + trend (robust khong?)")
go(mk(MIN_CONFL=3,TREND_ON=True),"G2 cluster>=3 +trend")
print("\n##### cluster>=3 tach KB1 / KB2")
go(mk(MIN_CONFL=3,KB2_CLIMAX=False),"G3 cluster>=3 KB1-only")
print("\n##### cluster>=4 (day toi han xem sup do dau)")
go(mk(MIN_CONFL=4),"G4 cluster>=4")
print("\n##### RR sensitivity tren cluster>=3")
go(mk(MIN_CONFL=3,RR=1.0),"G5 cluster>=3 RR1.0")
go(mk(MIN_CONFL=3,RR=2.0),"G6 cluster>=3 RR2.0")
print("\n##### cluster>=2 + trend, RR variants (giu nhieu lenh hon)")
go(mk(TREND_ON=True,RR=1.0),"G7 cluster>=2 +trend RR1.0")
go(mk(TREND_ON=True,RR=2.0),"G8 cluster>=2 +trend RR2.0")
