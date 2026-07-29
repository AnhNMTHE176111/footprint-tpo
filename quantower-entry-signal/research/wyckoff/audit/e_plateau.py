#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
e_plateau.py — MUC E: vung bang phang vs diem nhon, cho MOI tham so se bi DONG BANG de port C#.

GD6/GD7 KHONG chot tham so moi nao (moi ung vien deu KILL) => cai thuc su duoc dong bang la
cau hinh v6. Do la cai sap duoc port => phai kiem cao nguyen o CHINH nhung tham so do.

Luat phan xu (SPEC §6.9 / brief muc E): quanh gia tri mac dinh, lech 1 buoc moi phia phai con
>= 60% EV cua diem tot nhat. Chi 1 diem dep = FAIL tham so do.

Kem: kiem lai chinh ham report.sweep() — no dem "lang gieng" ke ca cac cau hinh TRUNG LAP
(truc TOL cua bias la no-op) nen bao "co cao nguyen" mot cach sai.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import imp_reversal_sweep as REV

INS = ('2026-05', '2026-06', '2026-07')


def hdr(t):
    print("\n" + "=" * 118); print(t); print("=" * 118)


def verdict(rows, default):
    """rows = [(val, ev, n)]. Tra ve chuoi phan xu cao nguyen quanh `default`."""
    d = {v: e for v, e, _ in rows}
    vals = [v for v, _, _ in rows]
    if default not in d:
        return "khong co diem mac dinh trong sweep"
    best = max(e for _, e, _ in rows)
    k = vals.index(default)
    neigh = [vals[k - 1]] if k > 0 else []
    neigh += [vals[k + 1]] if k < len(vals) - 1 else []
    ok = [v for v in neigh if best > 0 and d[v] >= 0.60 * best]
    if best <= 0:
        return "EV tot nhat <= 0"
    return (f"lang gieng dat >=60%EV_best: {len(ok)}/{len(neigh)} "
            f"({'BANG PHANG' if len(ok) == len(neigh) and len(neigh) > 0 else 'DIEM NHON — FAIL'})")


def main():
    B = E.load_m1(); V6.prepare(B); vf = E.calc_volfloor(B)
    L.months_patch(INS)
    BASE = dict(CLEAN=True, PMAX=1.00, RR=4.0)

    hdr("E.1 — KB1: sweep 1 tham so moi lan quanh gia tri DA CHOT (v6)")
    SWEEPS = [
        ("RR",         [2.0, 3.0, 4.0, 5.0, 6.0],      4.0),
        ("PMAX",       [0.80, 0.90, 1.00, 1.10, 1.20], 1.00),
        ("PMIN",       [0.40, 0.50, 0.60, 0.70, 0.80], 0.60),
        ("RANGE_LEN",  [6, 7, 8, 9, 10],               8),
        ("RMIN",       [20, 25, 30, 35, 40],           30),
        ("RMAX",       [55, 65, 75, 85, 95],           75),
        ("BVSA",       [1.5, 1.75, 2.0, 2.25, 2.5],    2.0),
        ("BBODY",      [0.40, 0.45, 0.50, 0.55, 0.60], 0.50),
        ("LIQ_K",      [0.50, 0.65, 0.75, 0.85, 1.00], 0.75),
        ("COOL",       [5, 10, 15, 20, 30],            15),
        ("WAIT",       [8, 10, 12, 15, 20],            12),
        ("RBODY",      [0.25, 0.30, 0.35, 0.40, 0.45], 0.35),
        ("HOLD_TOL",   [0, 1, 2, 3, 4],                2),
        ("FLOOR",      [20, 25, 30, 35, 40],           30),
        ("CAP",        [50, 60, 70, 80, 90],           70),
        ("CL_LOOK",    [10, 15, 20, 25, 30],           20),
        ("CL_W",       [3, 4, 5, 6, 7],                5),
        ("CL_CLOSE",   [0.40, 0.45, 0.50, 0.55, 0.60], 0.50),
    ]
    n_run = 0
    for name, vals, dflt in SWEEPS:
        rows = []
        for v in vals:
            C = V6.cfg(**dict(BASE, **{name: v}))
            S = V6.scan(B, C, vf, None)
            n_run += 1
            rows.append((v, L.ev(S), len(S)))
        cells = "  ".join(f"{v}:EV{e:+.2f}(n{n})" + ("*" if v == dflt else "") for v, e, n in rows)
        print(f"  {name:<11s} {cells}")
        print(f"  {'':<11s} -> {verdict(rows, dflt)}")
    print(f"\n  (* = gia tri dang chot.  So lan chay engine chi trong muc E.1 nay = {n_run})")

    hdr("E.2 — KB2: sweep 1 tham so moi lan quanh gia tri LIVE")
    B2 = REV.bars()
    K2 = [
        ("rr",            [1.0, 1.25, 1.5, 2.0, 2.5],     1.5),
        ("vwap_tol_t",    [6, 9, 12, 16, 20],             12),
        ("vsa_conf",      [1.4, 1.6, 1.8, 2.0, 2.2],      1.8),
        ("approach_bars", [3, 4, 6, 8, 12],               6),
        ("wick_frac",     [0.40, 0.45, 0.50, 0.55, 0.60], 0.50),
        ("body_min",      [0.20, 0.25, 0.30, 0.35, 0.40], 0.30),
        ("cpos_h",        [0.00, 0.02, 0.05, 0.10, 0.15], 0.05),
        ("cooldown",      [5, 10, 15, 20, 30],            15),
        ("trend_tol_t",   [0, 5, 10, 20, 30],             10),
        ("sl_cap_t",      [40, 55, 70, 85, 100],          70),
    ]
    n2 = 0
    for name, vals, dflt in K2:
        rows = []
        for v in vals:
            if name == 'rr':
                sg = REV.in_window(B2, REV.detect(B2))
                r = REV.score(B2, sg, v)
            else:
                sg = REV.in_window(B2, REV.detect(B2, **{name: v}))
                r = REV.score(B2, sg, REV.LIVE['rr'])
            n2 += 1
            rows.append((v, r['ev'], r['closed']))
        cells = "  ".join(f"{v}:EV{e:+.2f}(n{n})" + ("*" if v == dflt else "") for v, e, n in rows)
        print(f"  {name:<14s} {cells}")
        print(f"  {'':<14s} -> {verdict(rows, dflt)}")
    print(f"\n  So lan chay detect/score trong muc E.2 = {n2}")

    hdr("E.3 — KIEM LAI CHINH report.sweep(): no co bi lua boi cau hinh TRUNG LAP khong?")
    print("  Sweep bias o GD6 la 3 TOL x 3 MIN_SCORE = 9 dong, NHUNG TOL la NO-OP")
    print("  (log kb12: TOL=0.2/0.5/1.0 cho EV y HET nhau o moi MIN_SCORE).")
    print("  => 9 dong that ra chi la 3 cau hinh KHAC BIET, moi cai lap 3 lan.")
    print("  report.sweep() (v7/report.py:75) dem: neigh_ok = so dong co EV >= 0.6*best, tru 1.")
    print("     MIN_SCORE=1 -> EV+1.500 (x3 dong) | MIN_SCORE=2 -> +1.222 (x3) | MIN_SCORE=3 -> 0.000 (x3)")
    print("     0.6*best = 0.900  => cac dong dat: 3 dong (MS=1) + 3 dong (MS=2) = 6, tru 1 = 5")
    print("     -> in ra '5 cau hinh khac dat >=60% EV cua diem tot nhat (co cao nguyen)'")
    print("  NHUNG theo TRUC THAM SO THAT (MIN_SCORE): 1 -> 2 -> 3 = +1.500 -> +1.222 -> 0.000")
    print("     lang gieng cua diem tot nhat (MS=1) chi co MS=2 (+1.222 >= 0.9 OK), con MS=3 = 0.000 SUP.")
    print("  ==> report.sweep() DEM TRUNG LAP la lang gieng => cao nguyen BI THOI PHONG.")
    print("      O lan nay khong gay hai (bias da KILL bang partition), nhung ham nay SE chung nhan")
    print("      sai mot 'diem nhon' thanh 'cao nguyen' o bat ky sweep nao co truc no-op. Can sua.")


if __name__ == '__main__':
    main()
