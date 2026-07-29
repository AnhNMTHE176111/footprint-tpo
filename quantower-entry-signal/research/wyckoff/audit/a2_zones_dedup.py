#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
a2_zones_dedup.py — MUC A (tiep): 3 kiem con con lai.

A.8b build_zones — kiem LAI cho dung huong.
   a1_truncate.py bao "LECH 5 zone" nhung do la ARTIFACT cua chinh phep cat: khi cat tai nen i,
   BLOCK dang hinh thanh bi DONG SOM => sinh 5 zone (POC/VAH/VAL/Dinh/Day) voi ready=dt[i] <= t.
   Tren chuoi day du, block do con keo dai => ready > t => khong duoc dem. Tuc chuoi DAY DU
   (= cai backtest dung) la ban BAO THU hon. Phep kiem DUNG phai la:
       moi zone trong pool DAY DU co ready<=t, PHAI ton tai trong pool CAT  (full ⊆ cut)
   Neu dung => backtest khong dung thong tin nao chua biet tai t.

A.9  dedup/cooldown — co dung tin hieu SAU de loai tin hieu TRUOC khong?

A.10 KB3 dead_at — nen thoat co nam trong tuong lai cua chinh nen do khong (nhan-qua)?
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import features, engine
import s3_edge2edge as K3


def hdr(t):
    print("\n" + "=" * 110); print(t); print("=" * 110)


def main():
    RAW = L.raw_rows()
    B = L.derive(RAW); V6.prepare(B)
    idx_is = [i for i, b in enumerate(B) if b['ym'] in ('2026-05', '2026-06', '2026-07')]
    CUTS = [idx_is[int(len(idx_is) * f)] for f in (0.10, 0.30, 0.50, 0.70, 0.90)]

    hdr("A.8b — build_zones: kiem huong DUNG  (full_ready<=t  PHAI  ⊆  cut)")
    pool_full = E.build_zones(B)
    ok = True
    print(f"  {'cut i':>8s} {'zone full ready<=t':>19s} {'trong so do CO trong pool cat':>31s} {'THIEU':>7s}")
    for i in CUTS:
        t = B[i]['dt']
        pc = E.build_zones(L.derive(RAW[:i + 1]))
        key = lambda z: (round(z['price'], 6), z['kind'], z['ready'])
        setc = set(key(z) for z in pc)
        fz = [z for z in pool_full if z['ready'] <= t <= z['expire']]
        have = sum(1 for z in fz if key(z) in setc)
        miss = len(fz) - have
        ok &= (miss == 0)
        print(f"  {i:8d} {len(fz):19d} {have:31d} {miss:7d}")
    msg = ("MOI zone backtest dung tai t DEU tinh duoc tu B[0..t] => NHAN-QUA, khong look-ahead"
           if ok else "CO zone backtest dung ma chua the biet tai t => LOOK-AHEAD")
    print(f"  ==> {msg}")
    print("  (Ghi chu: chenh 5 zone o a1_truncate.py la artifact cua phep cat — block cuoi bi dong som "
          "tren chuoi cat, KHONG phai loi cua backtest.)")

    hdr("A.9 — dedup / cooldown: co dung tin hieu SAU de loai tin hieu TRUOC?")
    C = V6.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    vf = E.calc_volfloor(B)
    raw = V6.run(B, C, vf, None)
    d1 = V6.dedup(raw)
    c1 = V6.cooldown(d1, C['COOL'])
    # kiem: cat danh sach raw tai moc thoi gian T, dedup+cooldown tren tien to -> phai la TIEN TO
    # cua ket qua tren toan bo (khong duoc co tin hieu bi 'huy hoi to' khi biet tuong lai)
    allok = True
    print(f"  {'cat raw <= i':>13s} {'n_prefix':>9s} {'la tien to cua ket qua day du?':>33s}")
    for i in CUTS:
        pre = [s for s in raw if s['i'] <= i]
        r_pre = V6.cooldown(V6.dedup(pre), C['COOL'])
        ids_pre = [(s['i'], s['side']) for s in r_pre]
        ids_full = [(s['i'], s['side']) for s in c1 if s['i'] <= i]
        same = ids_pre == ids_full
        allok &= same
        print(f"  {i:13d} {len(ids_pre):9d} {str(same):>33s}")
    print(f"  ==> {'NHAN-QUA (dedup/cooldown chi nhin tin hieu truoc)' if allok else 'LOOK-AHEAD'}")

    hdr("A.10 — KB3 dead_at / maxbars: nen thoat co o TUONG LAI cua nen vao khong (nhan-qua)?")
    states, arms, valids = features.range_struct_scan(B)
    C3 = K3.cfg(); C3['_states'] = states
    raw3 = K3.post_months(K3.find_touch_events(B, states, C3, range_P=dict(features.DEFAULT_P)))
    n_bad = n_have = 0
    for e in raw3:
        da = K3.find_dead_at(states, e, cap_bars=C3['Kb3MaxHoldBars'] + 5)
        if da is None:
            continue
        n_have += 1
        if da <= e['i']:
            n_bad += 1
    print(f"  so lan cham co dead_at = {n_have} / {len(raw3)}")
    print(f"  so ca dead_at <= nen vao (=se la look-ahead) = {n_bad}")
    msg2 = ("dead_at LUON o tuong lai => la LUAT THOAT nhan-qua, khong phai look-ahead"
            if n_bad == 0 else "CO dead_at <= nen vao => LOI")
    print(f"  ==> {msg2}")
    print("  ⚠ NHUNG: `dead_at` la mot luat THOAT nhan-qua; con phep PHAN HOACH "
          "'vo THUAN huong scalp' (run_kb3.py:146 find_favorable_break) dung THONG TIN TUONG LAI "
          "de chia mau => KHONG trien khai duoc live. Xem phan tich o AUDIT_V7.md muc A/K.")

    hdr("A.11 — gate ap o nen VAO hay nen PHA?")
    print("  engine._wait_entry (v7/engine.py:102-105): okT/okB/okV/okL doc bj = NEN VAO (j), "
          "khong phai b = nen pha (i)  -> DUNG (khop cbr_v6.py:242-245 va RunnerSignal.cs:570).")
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v7", "engine.py")).read()
    seg = src[src.index("okT = "):src.index("if okT and okB")]
    print("  nguyen van:")
    for ln in seg.strip().splitlines():
        print("    " + ln.strip())
    print(f"  ==> so lan doc b['...'] (nen pha) trong doan gate = {seg.count(chr(98)+'[')}  (phai = 0)")


if __name__ == '__main__':
    main()
