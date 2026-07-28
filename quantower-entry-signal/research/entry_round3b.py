#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ROUND 3b — test CONG BANG hon:
  - SWEEP STRICT: nen TRUOC da DONG han qua vung (pha that bai) roi nen sau rut manh => hiem, dut khoat
  - VWAP bias CHI ap cho pha&hoi (momentum), tha reversal
"""
import entry_dxfeed as E
E.B=E.load_m1();E.VOLFLOOR_AUTO=E.calc_volfloor(E.B);pool=E.build_zones(E.B);E.USE_DELTA=False
print(f"M1={len(E.B)} zones={len(pool)}")
def go(C,label):
    C=E.prep(dict(C))
    raw=E.run(E.B,pool,C)
    if C['SWEEP_ON']:raw=raw+E.scan_sweep(E.B,pool,C)
    sig=E.dedup(raw,pool,C)
    sig=[s for s in sig if s['ym'] in ('2026-05','2026-06','2026-07')]
    E.evalset(E.B,sig,label,C,by_month=True)
mk=E.make
go(mk(),"BASE hop luu>=2")
print("\n===== SWEEP STRICT (pha that bai + rut manh) =====")
go(mk(SWEEP_ON=True,SWEEP_STRICT=True,SWEEP_SPIKE=0.3,SWEEP_REJECT=0.3),"S-strict 0.3/0.3")
go(mk(SWEEP_ON=True,SWEEP_STRICT=True,SWEEP_SPIKE=0.5,SWEEP_REJECT=0.5),"S-strict 0.5/0.5")
go(mk(MIN_CONFL=3,SWEEP_ON=True,SWEEP_STRICT=True),"S-strict + hop luu>=3")
print("\n===== VWAP bias CHI cho pha&hoi (momentum) =====")
go(mk(VWAP_ON=True,VWAP_KB1ONLY=True,VWAP_MARGIN=0.0),"vwap-KB1only m0")
go(mk(VWAP_ON=True,VWAP_KB1ONLY=True,VWAP_MARGIN=2.0),"vwap-KB1only m2")
go(mk(MIN_CONFL=3,VWAP_ON=True,VWAP_KB1ONLY=True,VWAP_MARGIN=2.0),"vwap-KB1only m2 + hop luu>=3")
