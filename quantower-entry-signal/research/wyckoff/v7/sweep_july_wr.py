#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUET CHAN DOAN — "nhoi lenh / WR cao hon thi tong R thang 7 bao nhieu?"  (yeu cau nguoi hoc 2026-07-29)

⚠⚠ DAY KHONG PHAI PHA TIM CAU HINH DE PORT. Doc truoc khi tin bat ky so nao o day:
  - Thang 7/2026 la 1/3 CUA CHINH IN-SAMPLE. AUDIT_V7 §4: KB1 da la ke song sot cua >=94 cau hinh
    tren dung cua so nay. Toi uu them tren 1 thang cua in-sample => LAM DAY OVERFIT, khong phai
    tim ra su that. Moi so "tot hon baseline" duoi day phai coi la NHIEU cho den khi co OOS.
  - Cau hinh dong bang o AUDIT_V7 §14 KHONG DOI vi file nay.
  - n cua 1 thang rat nho (baseline chi 12 lenh). Nguong SPEC: n<25 => KHONG KET LUAN.
    Vi vay moi dong deu in kem n va co danh dau [n<25].

Chay: python3 sweep_july_wr.py
"""
import sys, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import entry_dxfeed as E
import cbr_v6 as V6

JULY = ('2026-07',)
BASE = dict(CLEAN=True, PMAX=1.00, RR=4.0)      # = cau hinh dong bang AUDIT_V7 §14


def stat(S, months=JULY):
    S = [s for s in S if s['ym'] in months]
    if not S:
        return None
    rs = [s['r'] for s in S]
    w = sum(1 for r in rs if r > 0)
    return dict(n=len(S), wr=100.0 * w / len(S), tot=sum(rs), ev=sum(rs) / len(S),
                mdd=V6.mdd(rs), w=w, l=len(S) - w)


def show(tag, st_, base_tot=None):
    if st_ is None:
        print(f"  {tag:<40} n=  0  (khong co lenh)")
        return
    flag = " [n<25 KHONG KET LUAN]" if st_['n'] < 25 else ""
    d = ""
    if base_tot is not None:
        d = f"  (vs baseline {st_['tot'] - base_tot:+.1f}R)"
    print(f"  {tag:<40} n={st_['n']:3} WR={st_['wr']:5.1f}% ({st_['w']}T/{st_['l']}L) "
          f"tong={st_['tot']:+6.1f}R EV={st_['ev']:+6.3f} MDD={st_['mdd']:4.1f}R{d}{flag}")


def main():
    B = E.load_m1()
    vf = E.VOLFLOOR_FROZEN
    E.VOLFLOOR_AUTO = vf
    V6.prepare(B)
    print(f"dxFeed M1={len(B)} nen | volfloor={vf} | CHI TINH THANG 7/2026\n")

    base = stat(V6.scan(B, V6.cfg(**BASE), vf, None))
    print("=" * 118)
    print("BASELINE (cau hinh dong bang AUDIT_V7 §14) — moc de so")
    print("=" * 118)
    show("BASELINE RR=4.0 CLEAN=on PMAX=1.00", base)
    bt = base['tot']

    # ---------------------------------------------------------------- 1. Truc RR
    print()
    print("=" * 118)
    print("1. TRUC RR — 'muon WR cao hon': ha RR thi WR len, nhung TONG R xuong")
    print("   (cung BO LENH y nguyen, chi doi muc tieu chot loi => n KHONG doi)")
    print("=" * 118)
    for rr in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0):
        show(f"RR={rr}", stat(V6.scan(B, V6.cfg(**{**BASE, 'RR': rr}), vf, None)), bt)

    # ---------------------------------------------------------------- 2. Noi long => nhieu lenh
    print()
    print("=" * 118)
    print("2. 'NHOI LENH' — noi tung bo loc de co NHIEU lenh hon (n tang)")
    print("=" * 118)
    looses = [
        ("CLEAN off (bo loc break sach)",        dict(CLEAN=False)),
        ("TREND off (bo loc thuan xu huong)",    dict(TREND=False)),
        ("VWAP off (bo loc dung phia VWAP)",     dict(VWAP=False)),
        ("LIQ off (bo loc thanh khoan)",         dict(LIQ=False)),
        ("DEAD off (bo loc phien chet UTC 2-8)", dict(DEAD=False)),
        ("BVSA 2.0->1.5 (break de hon)",         dict(BVSA=1.5)),
        ("BVSA 2.0->1.2",                        dict(BVSA=1.2)),
        ("BBODY 0.50->0.35 (than nen de hon)",   dict(BBODY=0.35)),
        ("PMIN 0.60->0.40 (retrace nong hon)",   dict(PMIN=0.40)),
        ("WAIT 12->20 (cho hoi lau hon)",        dict(WAIT=20)),
        ("COOL 15->5 (vao lai nhanh hon)",       dict(COOL=5)),
        ("RANGE_LEN 8->6 (range ngan hon)",      dict(RANGE_LEN=6)),
        ("RMAX 75->110 (chap range rong hon)",   dict(RMAX=110)),
    ]
    for name, kw in looses:
        show(name, stat(V6.scan(B, V6.cfg(**{**BASE, **kw}), vf, None)), bt)

    # ---------------------------------------------------------------- 3. Nhoi toi da
    print()
    print("=" * 118)
    print("3. NHOI TOI DA — tat het loc, va tim RR tot nhat CHO RIENG bo lenh do")
    print("   (day la cho de nhin thay overfit ro nhat: n lon, nhung EV/lenh sup)")
    print("=" * 118)
    ALLOFF = {**BASE, 'CLEAN': False, 'TREND': False, 'VWAP': False, 'LIQ': False, 'DEAD': False,
              'BVSA': 1.2, 'BBODY': 0.35, 'PMIN': 0.40, 'WAIT': 20, 'COOL': 5}
    for rr in (1.0, 1.5, 2.0, 3.0, 4.0):
        show(f"TAT HET LOC + RR={rr}", stat(V6.scan(B, V6.cfg(**{**ALLOFF, 'RR': rr}), vf, None)), bt)

    # ---------------------------------------------------------------- 4. Doi chieu 3 thang
    print()
    print("=" * 118)
    print("4. DOI CHIEU — cung cac cau hinh do nhung tren CA 3 THANG (5-7/2026)")
    print("   Muc dich: xem cai 'thang o thang 7' co song tren 3 thang khong. Neu khong => nhieu.")
    print("=" * 118)
    ALL3 = ('2026-05', '2026-06', '2026-07')

    def show3(tag, S):
        s3 = stat(S, ALL3)
        if s3 is None:
            print(f"  {tag:<40} n=  0")
            return
        bym = defaultdict(float)
        for x in [y for y in S if y['ym'] in ALL3]:
            bym[x['ym']] += x['r']
        mm = " ".join(f"{m[-2:]}:{bym.get(m, 0.0):+6.1f}" for m in ALL3)
        neg = [m[-2:] for m in ALL3 if bym.get(m, 0.0) <= 0]
        warn = f"  ⚠ THANG AM: {','.join(neg)}" if neg else "  (ca 3 thang duong)"
        print(f"  {tag:<40} n={s3['n']:3} WR={s3['wr']:5.1f}% tong={s3['tot']:+6.1f}R "
              f"EV={s3['ev']:+6.3f} | {mm}{warn}")

    show3("BASELINE RR=4.0", V6.scan(B, V6.cfg(**BASE), vf, None))
    for rr in (1.5, 2.0, 3.0):
        show3(f"RR={rr}", V6.scan(B, V6.cfg(**{**BASE, 'RR': rr}), vf, None))
    for name, kw in looses[:5]:
        show3(name, V6.scan(B, V6.cfg(**{**BASE, **kw}), vf, None))
    show3("TAT HET LOC + RR=2.0", V6.scan(B, V6.cfg(**{**ALLOFF, 'RR': 2.0}), vf, None))

    print()
    print("=" * 118)
    print("NHAC LAI: khong dong nao o tren duoc dung lam cau hinh port. Cau hinh port = AUDIT_V7 §14.")
    print("=" * 118)


if __name__ == '__main__':
    main()
