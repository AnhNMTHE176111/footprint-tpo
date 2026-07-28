#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CROSS-CHECK: gia XAP XI cua viec BO DELTA la bao nhieu?
Chay CUNG config shipped tren CUNG data fp-m1 (co delta), 2 che do:
  (A) delta-ful  (dung dung EntrySignal live)
  (B) delta-free (proxy c>o) — nhu dxFeed buoc phai dung.
Chenh (A)-(B) = gia phai tra khi mat delta. Roi so voi dxFeed cung ky (6-7/2026).
"""
import entry_dxfeed as E

def cfg():return E.make()

def eval_mode(B,pool,use_delta,label,months):
    E.USE_DELTA=use_delta
    C=E.prep(dict(cfg()))
    raw=E.run(B,pool,C)
    sig=E.dedup(raw,pool,C)
    if months:sig=[s for s in sig if s['ym'] in months]
    E.evalset(B,sig,label,C,by_month=True)
    return sig

if __name__=='__main__':
    print("="*100);print("CROSS-CHECK delta-ful vs delta-free tren fp-m1 (co delta)")
    Bf=E.load_fpm1()
    # dung machinery cua entry_dxfeed nhung tren B=fp-m1
    E.B=Bf                      # cho add_liqbase/prep tham chieu dung
    E.VOLFLOOR_AUTO=20.0        # fp-m1 la front-month lien tuc, floor 20 nhu backtest goc
    pool=E.build_zones(Bf)
    print(f"  fp-m1: {len(Bf)} nen {Bf[0]['dt']} -> {Bf[-1]['dt']} | zones={len(pool)}")
    months=None  # tat ca (fp-m1 chi ~1 thang 6/26-7/25)
    eval_mode(Bf,pool,True ,"(A) DELTA-FUL  — dung EntrySignal live",months)
    eval_mode(Bf,pool,False,"(B) DELTA-FREE — proxy c>o (nhu dxFeed)",months)
    print("\n"+"="*100)
    print("So sanh dxFeed cung ky 6-7/2026 (chay lai delta-free tren dxFeed):")
    E.B=E.load_m1();E.VOLFLOOR_AUTO=E.calc_volfloor(E.B)
    pool2=E.build_zones(E.B)
    E.USE_DELTA=False
    C=E.prep(dict(cfg()))
    raw=E.run(E.B,pool2,C);sig=E.dedup(raw,pool2,C)
    sig=[s for s in sig if s['ym'] in ('2026-06','2026-07')]
    E.evalset(E.B,sig,"(C) dxFeed delta-free 6-7/2026",C,by_month=True)
