#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stat_null.py — MUC D (bo tro): ket qua co phan biet duoc voi MAY MAN khong?

Vi OOS that KHONG chay duoc (muc F: cua so 2025-11->2026-04 chi co 171 nen qua gate), day la
phep kiem thay the manh nhat con lai. 3 lop:

  (1) Binomial vs WR hoa von: RR=4 => hoa von o WR 20%; RR=1.5 => 40%. Quan sat co vuot khong?
  (2) NULL VAO LENH NGAU NHIEN (Monte Carlo): giu NGUYEN hinh hoc rui ro (cung phan bo risk_t,
      cung phan bo side, cung so lenh, cung tap nen hop le) nhung CHON NEN VAO NGAU NHIEN.
      Tra loi cau hoi that: "co phai chi can RR 4:1 trong thi truong co xu huong la du?"
  (3) NULL DAO PHIA (sign-flip): giu y nguyen nen vao va risk, DAO side => do loi the huong.

Ket qua khong phai bang chung cho GD6/GD7; day la phep BAC BO.
"""
import sys, os, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import imp_reversal_sweep as REV
import reversal_vwap as rv

INS = ('2026-05', '2026-06', '2026-07')
TICK = E.TICK
NSIM = 3000
random.seed(20260729)


def hdr(t):
    print("\n" + "=" * 118); print(t); print("=" * 118)


def binom_tail(n, k, p):
    """P(X >= k) voi X~Bin(n,p), tinh chinh xac bang so nguyen lon."""
    from math import comb
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def hit_simple(B, i, side, sl, tp):
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl):
            return 'SL'
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp):
            return 'TP'
    return 'open'


def mc_random_entry(B, pool_idx, sides, risks, rr, nsim=NSIM):
    """Chon ngau nhien nen vao tu pool_idx, gan (side, risk) lay ngau nhien tu phan bo THAT.
    Tra ve list EV cua tung mo phong."""
    n = len(sides)
    evs = []
    for _ in range(nsim):
        tot = cnt = 0
        for k in range(n):
            i = random.choice(pool_idx)
            side = random.choice(sides)
            rt = random.choice(risks)
            entry = B[i]['c']
            r = rt * TICK
            sl = entry - r if side == 'LONG' else entry + r
            tp = entry + rr * r if side == 'LONG' else entry - rr * r
            o = hit_simple(B, i, side, sl, tp)
            if o == 'open':
                continue
            tot += rr if o == 'TP' else -1.0
            cnt += 1
        if cnt:
            evs.append(tot / cnt)
    return evs


def main():
    B = E.load_m1(); V6.prepare(B); vf = E.calc_volfloor(B)
    L.months_patch(INS)
    C1 = V6.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    S1 = V6.scan(B, C1, vf, None)
    B2 = REV.bars()
    sg2 = REV.in_window(B2, REV.detect(B2))
    r2 = REV.score(B2, sg2, REV.LIVE['rr'])

    hdr("D.1 — Binomial vs WR hoa von (null: vao lenh vo nghia, chi hinh hoc RR quyet dinh)")
    for tag, n, k, rr in [("KB1 (RR=4.0)", len(S1), sum(1 for s in S1 if s['r'] > 0), 4.0),
                          ("KB2 (RR=1.5)", r2['closed'], r2['tp'], 1.5)]:
        pbe = 1.0 / (1.0 + rr)
        p = binom_tail(n, k, pbe)
        print(f"  {tag:<16s} n={n:3d} thang={k:3d} WR={100*k/n:5.1f}%  WR hoa von={100*pbe:4.1f}%  "
              f"P(X>={k}|p={pbe:.2f}) = {p:.2e}  {'CO Y NGHIA (p<0.05)' if p < 0.05 else 'KHONG CO Y NGHIA'}")
    print("\n  Luu y: null nay CHI bac 'vao lenh hoan toan vo nghia'. No KHONG bac 'thi truong co xu huong")
    print("  manh nen bat ky lenh thuan huong nao cung dat WR cao voi RR 4:1' — do la NULL D.2 duoi day.")

    hdr("D.2 — NULL VAO LENH NGAU NHIEN (Monte Carlo, giu nguyen hinh hoc rui ro)")
    pool = [i for i, b in enumerate(B)
            if b['ym'] in INS and V6._gate(b, vf) and not (2 <= b['dt'].hour < 8)]
    print(f"  pool nen hop le (qua _gate, 5-7/2026, ngoai phien chet) = {len(pool)}")
    for tag, S, rr, Barr, pl in [("KB1", S1, 4.0, B, pool)]:
        sides = [s['side'] for s in S]
        risks = [s['risk_t'] for s in S]
        obs = L.ev(S)
        evs = mc_random_entry(Barr, pl, sides, risks, rr)
        evs.sort()
        pct = sum(1 for e in evs if e >= obs) / len(evs)
        print(f"  {tag}: EV quan sat = {obs:+.3f}")
        print(f"      null ngau nhien ({len(evs)} mo phong, cung {len(sides)} lenh, cung phan bo side/risk):")
        print(f"      EV null: med={st.median(evs):+.3f}  p05={evs[int(.05*len(evs))]:+.3f}  "
              f"p95={evs[int(.95*len(evs))]:+.3f}  max={evs[-1]:+.3f}")
        print(f"      p-value (ty le mo phong dat >= EV quan sat) = {pct:.4f}  "
              f"{'-> QUAN SAT VUOT NULL RO RET' if pct < 0.05 else '-> KHONG phan biet duoc voi may man'}")
    # KB2 tren bar array rieng
    pool2 = [i for i, b in enumerate(B2)
             if b['dt'].strftime('%Y-%m') in INS and b['v'] >= 20 and b['since_gap'] >= 20]
    print(f"\n  pool nen hop le cho KB2 (v>=20, warmup, 5-7/2026) = {len(pool2)}")
    sides2 = [s['side'] for s in sg2]; risks2 = [s['risk_t'] for s in sg2]
    obs2 = r2['ev']
    evs2 = mc_random_entry(B2, pool2, sides2, risks2, REV.LIVE['rr'])
    evs2.sort()
    pct2 = sum(1 for e in evs2 if e >= obs2) / len(evs2)
    print(f"  KB2: EV quan sat = {obs2:+.3f}")
    print(f"      EV null: med={st.median(evs2):+.3f}  p05={evs2[int(.05*len(evs2))]:+.3f}  "
          f"p95={evs2[int(.95*len(evs2))]:+.3f}  max={evs2[-1]:+.3f}")
    print(f"      p-value = {pct2:.4f}  "
          f"{'-> VUOT NULL' if pct2 < 0.05 else '-> KHONG phan biet duoc voi may man'}")

    hdr("D.3 — NULL DAO PHIA (cung nen vao, cung risk, DAO side) — do loi the huong cua regime")
    for tag, S, rr, Barr in [("KB1", S1, 4.0, B)]:
        tot = cnt = 0
        for s in S:
            side = 'SHORT' if s['side'] == 'LONG' else 'LONG'
            entry = s['entry']; r = s['risk_t'] * TICK
            sl = entry - r if side == 'LONG' else entry + r
            tp = entry + rr * r if side == 'LONG' else entry - rr * r
            o = hit_simple(Barr, s['i'], side, sl, tp)
            if o == 'open':
                continue
            tot += rr if o == 'TP' else -1.0; cnt += 1
        print(f"  {tag} dao phia: n={cnt} tong={tot:+.1f}R EV={tot/cnt:+.3f}  "
              f"(that: n={len(S)} tong={sum(x['r'] for x in S):+.1f}R EV={L.ev(S):+.3f})")
    tot = cnt = 0
    for s in sg2:
        side = 'SHORT' if s['side'] == 'LONG' else 'LONG'
        entry = s['entry']; r = s['risk_t'] * TICK
        sl = entry - r if side == 'LONG' else entry + r
        tp = entry + REV.LIVE['rr'] * r if side == 'LONG' else entry - REV.LIVE['rr'] * r
        o = hit_simple(B2, s['i'], side, sl, tp)
        if o == 'open':
            continue
        tot += REV.LIVE['rr'] if o == 'TP' else -1.0; cnt += 1
    print(f"  KB2 dao phia: n={cnt} tong={tot:+.1f}R EV={tot/cnt:+.3f}  "
          f"(that: n={r2['closed']} tong={r2['net']:+.1f}R EV={r2['ev']:+.3f})")

    hdr("D.4 — TACH LONG/SHORT (SPEC §9 #1a bat buoc, ca 2 bao cao GD6/GD7 DEU THIEU)")
    for tag, S in [("KB1", S1)]:
        for sd in ('LONG', 'SHORT'):
            ss = [s for s in S if s['side'] == sd]
            L.line2(f"{tag} {sd}", ss, INS)
    for sd in ('LONG', 'SHORT'):
        ss = [s for s in sg2 if s['side'] == sd]
        rr = REV.score(B2, ss, REV.LIVE['rr'])
        REV.fmt(rr, f"KB2 {sd}")


if __name__ == '__main__':
    main()
