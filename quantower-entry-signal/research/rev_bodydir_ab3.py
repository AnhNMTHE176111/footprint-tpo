#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REV_BODYDIR_AB3 — phat hien vong 2: mau nen kich hoat KHONG chi doi WR, no doi CA DO DAI
di duoc cua lenh.

  nen THUAN mau : EV tang deu theo RR (1.0 -> 3.0 : +0.43 -> +1.00)  => co DA THAT, de chay xa
  nen NGUOC mau : EV giam theo RR (+0.23 -> -0.39)                   => chi bat ky thuat ngan

=> thay vi BO nen nguoc mau (mat nua so lenh), phan HANG va dat TP KHAC NHAU cho 2 nhom.
File nay quet RR min cho tung nhom + kiem xem diem toi uu la DINH NHON (fit) hay CAO NGUYEN (that).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imp_reversal_sweep as S
import rev_bodydir_ab as A

LIVE = S.LIVE
RRS = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5, 4.0, 5.0]


def main():
    B = S.bars()
    sig = S.in_window(B, A.detect2(B))
    same = [x for x in sig if x['same']]
    diff = [x for x in sig if not x['same']]
    print(f"tin hieu 5-7/2026: tong {len(sig)}  (thuan mau {len(same)} / nguoc mau {len(diff)})")

    print("\n" + "=" * 100)
    print("(1) QUET RR RIENG TUNG NHOM — diem toi uu la dinh nhon hay cao nguyen?")
    print(f"  {'RR':>5} | {'THUAN mau: WR / EV / net':>34} | {'NGUOC mau: WR / EV / net':>34}")
    best = {}
    for rr in RRS:
        a = S.score(B, same, rr); d = S.score(B, diff, rr)
        print(f"  {rr:5.2f} | {a['wr']*100:5.0f}% {a['ev']:+7.3f}R {a['net']:+7.1f}R (n={a['closed']:2d}) | "
              f"{d['wr']*100:5.0f}% {d['ev']:+7.3f}R {d['net']:+7.1f}R (n={d['closed']:2d})")
        best[rr] = (a, d)

    print("\n" + "=" * 100)
    print("(2) SO SANH 4 THIET KE (tong R tren 3 thang, cung 1 bo tin hieu goc)")
    v0 = S.score(B, sig, 1.5)
    print(f"  V0  giu het, TP 1.5R cho tat ca          net {v0['net']:+6.1f}R  n={v0['closed']:2d}  EV {v0['ev']:+.3f}")
    a1 = S.score(B, same, 1.5)
    print(f"  A1  BO nguoc mau, TP 1.5R                net {a1['net']:+6.1f}R  n={a1['closed']:2d}  EV {a1['ev']:+.3f}")
    a3 = S.score(B, same, 3.0)
    print(f"  A3  BO nguoc mau, TP 3.0R                net {a3['net']:+6.1f}R  n={a3['closed']:2d}  EV {a3['ev']:+.3f}")
    for rr_hi in (2.0, 2.5, 3.0):
        for rr_lo in (1.0, 1.5):
            hi = S.score(B, same, rr_hi); lo = S.score(B, diff, rr_lo)
            n = hi['closed'] + lo['closed']; net = hi['net'] + lo['net']
            print(f"  B   PHAN HANG: thuan {rr_hi}R + nguoc {rr_lo}R      net {net:+6.1f}R  n={n:2d}  "
                  f"EV {net/n:+.3f}")

    print("\n" + "=" * 100)
    print("(3) ON DINH THEO THANG cua thiet ke PHAN HANG (thuan 3.0R / nguoc 1.5R)")
    hi = S.score(B, same, 3.0); lo = S.score(B, diff, 1.5)
    months = sorted(set(hi['bym']) | set(lo['bym']))
    for m in months:
        h = hi['bym'].get(m, (0, 0, 0.0, 0, 0)); l = lo['bym'].get(m, (0, 0, 0.0, 0, 0))
        print(f"  {m}: thuan {h[2]:+5.1f}R ({h[1]}/{h[0]})  nguoc {l[2]:+5.1f}R ({l[1]}/{l[0]})  "
              f"=> tong {h[2]+l[2]:+5.1f}R")

    print("\n" + "=" * 100)
    print("(4) MFE — nen thuan mau co thuc su di XA hon khong? (do truc tiep, khong qua TP)")
    import reversal_vwap as rv
    TICK = S.TICK
    def mfe(s):
        r = s['risk_t'] * TICK
        best_r = 0.0
        for j in range(s['i'] + 1, len(B)):
            b = B[j]
            if s['side'] == 'LONG':
                if b['lo'] <= s['sl']: break
                best_r = max(best_r, (b['hi'] - s['entry']) / r)
            else:
                if b['hi'] >= s['sl']: break
                best_r = max(best_r, (s['entry'] - b['lo']) / r)
        return best_r
    for nm, grp in (("THUAN mau", same), ("NGUOC mau", diff)):
        m = sorted(mfe(x) for x in grp)
        med = m[len(m)//2]
        print(f"  {nm}: MFE trung vi {med:.2f}R  |  >=1.5R: {sum(v>=1.5 for v in m)}/{len(m)}  "
              f">=2R: {sum(v>=2 for v in m)}/{len(m)}  >=3R: {sum(v>=3 for v in m)}/{len(m)}")


if __name__ == "__main__":
    main()
