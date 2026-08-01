#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/entry/harness.py — do EntrySignal (M1) TRUOC/SAU khi doi tang vung sang CORVEN.
Pha P0 (PLAN_KB_ABC.md doi tuong EntrySignal, xem chi dan phien nay): do cot TRUOC.

NGUON DU LIEU: dxFeed (research/entry_dxfeed.py), KHONG dung fp-m1.
Ly do (khac voi goi y "entry_month.load_m1()" trong brief — entry_month.py dung
fp-m1-1-month-data.csv chi 28 ngay VA co delta; nhung fp-m1-6-month.csv co cot Volume
hong 04/06->26/06 (BASELINE.md §8), va moi feature volume (vma/vratio/VSA/volfloor) sai
trong khoang do. entry_dxfeed.py la ban PORT delta-free CHINH XAC cua EntrySignal.cs
(BASE dict khop shipped: SL floor4-cap6 = 40/60 tick, RR=1.5, MIN_CONFL=2, KB2_CLIMAX=True,
EXTEND+NEXTZONE_MINR=2.0) va da la lua chon chuan trong DATA_CAPABILITY §4.3 vi dxFeed co
lich su tu 2025-11 -> pool KHONG "lanh" o dau ky scored (khac han fp-m1). Vi vay harness
nay goi entry_dxfeed.load_m1()/build_zones()/run()/dedup(), KHONG goi entry_month.py.

Canh bao NHAN QUA volfloor (AUDIT_V7.md §1.2): calc_volfloor() cua entry_dxfeed la
LOOK-AHEAD (percentile-30 tren TOAN BO du lieu >=2026-05). Harness nay dung thang
VOLFLOOR_FROZEN=20.0 (hang so nhan qua, khop EntrySignal.cs VolFloor=20 mac dinh),
KHONG goi calc_volfloor()/prep().

R dung de tinh EV/WR/MDD = r3p (RR CO DINH toi tp3, KHONG dung tpx/nong-vung-ke) — vi
CORVEN_SPEC bat buoc "TP theo R co dinh, khong het luc thi ra". Day la lua chon CHU DICH
de TRUOC/SAU so duoc voi nhau tren cung mot dinh nghia R (SAU cung se dung RR co dinh).
"""
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))            # .../v8/entry
V8 = os.path.dirname(HERE)                                     # .../v8
WYCK = os.path.dirname(V8)                                      # .../wyckoff
RESEARCH = os.path.dirname(WYCK)                                # .../research
sys.path.insert(0, RESEARCH)
sys.path.insert(0, os.path.join(WYCK, 'v7'))

import entry_dxfeed as E     # noqa: E402
import report as RPT          # noqa: E402  (v7/report.py — line/partition/sweep/mdd/_half_split)

MONTHS = ('2026-05', '2026-06', '2026-07')
WARMUP_DAYS = 5   # bo N ngay giao dich dau cua CUA SO SCORED (khong phai dau lich su B)


def load_dx():
    B = E.load_m1()
    pool = E.build_zones(B)
    return B, pool


def warmup_cutoff(B, n_days=WARMUP_DAYS):
    """Moc thoi gian = sau N ngay giao dich dau tien cua thang 2026-05 (dau cua so scored).
    Ap dung CHUNG mot quy tac cho ca TRUOC va SAU (P0 §, DATA_CAPABILITY §4)."""
    dates = sorted({b['dt'].date() for b in B if b['ym'] == '2026-05'})
    if len(dates) <= n_days:
        return None
    return dates[n_days]


def run_before(label="P0 TRUOC (pool cu: session POC/VAH/VAL/D-1 + VWAP)"):
    B, pool = load_dx()
    C = E.make(VOL_FLOOR=E.VOLFLOOR_FROZEN)   # nhan qua, khop EntrySignal.cs VolFloor=20
    raw = E.run(B, pool, C)
    sig = E.dedup(raw, pool, C)
    sig = [s for s in sig if s['ym'] in MONTHS]

    cutoff = warmup_cutoff(B)
    n_before_cut = len(sig)
    if cutoff is not None:
        sig = [s for s in sig if s['dt'].date() >= cutoff]
    n_dropped = n_before_cut - len(sig)

    # chuan hoa key cho report.line(): 'r' = ket qua RR CO DINH (tp3), giu nguyen 'dt'/'ym'
    for s in sig:
        _, r = E.sim(B, s, 'tp3', C['RR'])
        s['r'] = r

    print("=" * 100)
    print(f"{label}")
    print(f"  M1(dxFeed)={len(B)} nen | pool cu = {len(pool)} vung | volfloor(nhan qua)={C['VOL_FLOOR']:.0f}")
    print(f"  warm-up: bo {WARMUP_DAYS} ngay giao dich dau cua thang 05/2026 (cutoff={cutoff}) "
          f"-> loai {n_dropped} tin hieu, con {len(sig)}")
    print("-" * 100)

    d_all = RPT.line("TONG", sig, MONTHS)

    longs = [s for s in sig if s['side'] == 'LONG']
    shorts = [s for s in sig if s['side'] == 'SHORT']
    d_long = RPT.line("LONG", longs, MONTHS)
    d_short = RPT.line("SHORT", shorts, MONTHS)

    # PLAY1 CORVEN = cham->dao (code: scen bat dau bang '2') ; PLAY2 CORVEN = pha->hoi (code: '1')
    play1 = [s for s in sig if s['scen'].startswith('2')]
    play2 = [s for s in sig if s['scen'].startswith('1')]
    d_p1 = RPT.line("PLAY1 cham-dao (code '2 cham&dao*')", play1, MONTHS)
    d_p2 = RPT.line("PLAY2 pha-hoi (code '1 pha&hoi*')", play2, MONTHS)

    print("-" * 100)
    return dict(B=B, pool=pool, C=C, sig=sig, all=d_all, long=d_long, short=d_short,
                play1=d_p1, play2=d_p2, cutoff=cutoff, n_dropped=n_dropped)


if __name__ == '__main__':
    run_before()
