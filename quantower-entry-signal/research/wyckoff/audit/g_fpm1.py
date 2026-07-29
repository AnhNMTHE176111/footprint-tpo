#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
g_fpm1.py — MUC G: doi chung 2 NGUON. Chay cau hinh CHOT tren fp-m1 (cua so trung) vs dxFeed.

Sua 2 khiem khuyet cua cach GD6 lam (run_kb12.py:230 step8_kb2_delta_fpm1):
  (1) GD6 chay detect() tren fp-m1 nhan UTC+7 mà KHONG quy doi ve UTC  -> nhan thang lech 7h,
      va khung gio (neu bat) sai hoan toan. Day QUY DOI -7h truoc khi chay (SPEC §1.2).
  (2) GD6 chay CA 6 THANG roi so n=16 voi n=27 cua dxFeed (3 thang) -> khong so duoc.
      Day CAT DUNG 5-7/2026 tren ca 2 nguon.

DATA_CAPABILITY §4.1 tuyen bo 2 nguon la CUNG MOT chuoi gia (khop 1260/1260 nen, 0 tick lech).
Neu dung, ket qua 2 nguon phai gan trung nhau; lech lon => hoac tuyen bo do sai, hoac pipeline lech.
"""
import sys, os
from datetime import timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import imp_reversal_sweep as REV
import reversal_vwap as rv
import loaders

INS = ('2026-05', '2026-06', '2026-07')
TICK = E.TICK


def hdr(t):
    print("\n" + "=" * 118); print(t); print("=" * 118)


def main():
    Bdx = E.load_m1(); V6.prepare(Bdx)
    vf_dx = E.calc_volfloor(Bdx)
    L.months_patch(INS)

    # ---- fp-m1: doc, QUY DOI -7h ve UTC, roi dan xuat lai bang chinh derive() (giong load_m1)
    hdr("G.0 — nap fp-m1 va QUY DOI UTC+7 -> UTC (-7h)")
    raw_fp = loaders.load_fp_m1_full("fp-m1-6-month.csv")
    print(f"  fp-m1 goc (nhan UTC+7): {len(raw_fp)} nen | {raw_fp[0]['dt']} -> {raw_fp[-1]['dt']}")
    src = [dict(dt=b['dt'] - timedelta(hours=7), o=b['o'], hi=b['hi'], lo=b['lo'],
                c=b['c'], v=b['v']) for b in raw_fp]
    src.sort(key=lambda b: b['dt'])
    Bfp = L.derive(src); V6.prepare(Bfp)
    print(f"  fp-m1 sau -7h (UTC):     {len(Bfp)} nen | {Bfp[0]['dt']} -> {Bfp[-1]['dt']}")

    # ---- kiem lai tuyen bo "cung mot chuoi gia" tren TOAN cua so trung, khong chi 1 ngay
    hdr("G.1 — kiem lai DATA_CAPABILITY §4.1 ('cung mot chuoi gia') tren TOAN cua so trung")
    dxm = {b['dt']: b for b in Bdx}
    both = [b for b in Bfp if b['dt'] in dxm]
    diff = [abs(b['c'] - dxm[b['dt']]['c']) for b in both]
    dv = [abs(b['v'] - dxm[b['dt']]['v']) for b in both]
    only_fp = len(Bfp) - len(both)
    fpset = {x['dt'] for x in Bfp}
    only_dx = sum(1 for b in Bdx if Bfp[0]['dt'] <= b['dt'] <= Bfp[-1]['dt'] and b['dt'] not in fpset)
    print(f"  nen trung moc thoi gian = {len(both)}   chi co o fp-m1 = {only_fp}   "
          f"chi co o dxFeed (trong cung khoang) = {only_dx}")
    print(f"  max |close_fp - close_dx| = {max(diff)/TICK:.2f} tick   so nen lech close = "
          f"{sum(1 for d in diff if d > 1e-9)}")
    print(f"  max |vol_fp - vol_dx|     = {max(dv):.0f}          so nen lech volume = "
          f"{sum(1 for d in dv if d > 1e-9)}")
    print(f"  ==> {'XAC NHAN cung mot chuoi gia' if max(diff) < 1e-9 else 'CO LECH GIA — tuyen bo §4.1 khong dung cho toan cua so'}")

    # ---- KB1 tren 2 nguon
    hdr("G.2 — KB1 (cau hinh CHOT) tren 2 nguon, CUNG cua so 5-7/2026")
    C1 = V6.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    S_dx = V6.scan(Bdx, C1, vf_dx, None)
    L.line2(f"KB1 dxFeed (vf={vf_dx})", S_dx, INS)
    vf_fp = E.calc_volfloor(Bfp)
    S_fp = V6.scan(Bfp, C1, vf_fp, None)
    L.line2(f"KB1 fp-m1  (vf={vf_fp})", S_fp, INS)
    S_fp20 = V6.scan(Bfp, C1, 20.0, None)
    L.line2("KB1 fp-m1  (vf=20, C# hardcode)", S_fp20, INS)
    # so trung tung lenh theo moc thoi gian
    tdx = {(s['dt'], s['side']) for s in S_dx}
    tfp = {(s['dt'], s['side']) for s in S_fp}
    print(f"  lenh KHOP moc (dt,side) giua 2 nguon = {len(tdx & tfp)} / dx {len(tdx)} / fp {len(tfp)}")
    print(f"  chi co o dxFeed = {len(tdx - tfp)}   chi co o fp-m1 = {len(tfp - tdx)}")

    # ---- KB2 tren 2 nguon
    hdr("G.3 — KB2 QUAY_DAU (cau hinh CHOT LIVE) tren 2 nguon, CUNG cua so 5-7/2026")
    B2 = REV.bars()
    sg_dx = REV.in_window(B2, REV.detect(B2))
    REV.fmt(REV.score(B2, sg_dx, REV.LIVE['rr']), "KB2 dxFeed")
    sg_fp = REV.in_window(Bfp, REV.detect(Bfp))
    REV.fmt(REV.score(Bfp, sg_fp, REV.LIVE['rr']), "KB2 fp-m1 (da -7h)")
    a = {(s['dt'], s['side']) for s in sg_dx}
    b = {(s['dt'], s['side']) for s in sg_fp}
    print(f"  lenh KHOP moc (dt,side) = {len(a & b)} / dx {len(a)} / fp {len(b)}")
    print(f"  chi dxFeed = {sorted(str(x[0]) for x in (a-b))[:6]}")
    print(f"  chi fp-m1  = {sorted(str(x[0]) for x in (b-a))[:6]}")

    hdr("G.4 — so sanh voi con so 'WR 61% vs 42%' trong DATA_CAPABILITY §4")
    print("  DATA_CAPABILITY §4 da KET LUAN chenh do la ZONE-POOL LANH (build_zones chi thay lich su")
    print("  cua chinh file ngan), KHONG phai du lieu khac nhau. KB1/KB2 o day KHONG dung build_zones")
    print("  (KB1 = box 8 nen; KB2 = VWAP) => du doan: 2 nguon phai gan trung. Ket qua G.2/G.3 la phep")
    print("  kiem doc lap cho ket luan do.")


if __name__ == '__main__':
    main()
