#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
k_rotation_null.py — bac bo tuyen bo DUY NHAT mang dau DUONG trong RESULTS_KB3.md:
   §4: "48.7% xoay bien vs ~3.7% ngau nhien -> CO edge cau truc ro ret"

Hai loi nghi ngo:
  (L1) LOOK-AHEAD: kb3_range_report._resolve() dung rhi/rlo la BIEN CUOI CUNG cua instance
       (lay tu last[i0], tuc trang thai o nen CUOI doi range) va end_bar (nen chet cua range)
       — ca hai deu la thong tin TUONG LAI so voi nen cham i.
  (L2) NULL SAI: p_null = BUF/(BUF+width) = 0.2/5.2 ~ 3.8% la xac suat first-passage cua buoc
       ngau nhien voi 2 rao chan LECH HAN nhau (0.2 gia vs 5.0 gia). Nhung bien co do KHONG
       phai bien co dang duoc dem: "rotation" = cham bien doi dien truoc khi CLOSE vuot bien gan
       + BUF, va co them nhom 'censored' 35%. So 48.7% (co dieu kien tren 'da phan giai') voi
       3.7% (khong dieu kien, rao chan khac) la so LECH LOAI.
       Nghiem trong hon: bo phat hien range CHI phat ra range khi gia DA nay qua lai >=2 lan moi
       bien trong >=30 nen. Do "co xoay tiep khong" roi so voi null bo qua chinh su CHON LOC do
       la VONG TRON.

Phep kiem: PLACEBO — giu Y NGUYEN hinh hoc (do rong, thoi luong) va dung CHINH ham _resolve,
nhung neo dai bang gia o mot moc thoi gian NGAU NHIEN khac (tam bang = close tai moc do).
Neu placebo cung cho ~48% => 48.7% la he qua cua HINH HOC + tinh chat M1 cua vang, KHONG phai
bang chung cho "range Wyckoff".
"""
import sys, os, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v7"))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import features
import kb3_range_report as KR

INS = ('2026-05', '2026-06', '2026-07')
random.seed(20260729)


def hdr(t):
    print("\n" + "=" * 114); print(t); print("=" * 114)


def touches(B, vb, end, rhi, rlo, P):
    """Dem lan cham + phan giai, DUNG CHINH KR._resolve (khong viet lai luat)."""
    width = rhi - rlo
    tol = max(P['TOLMIN'], P['TOLF'] * width)
    lu = ld = -999
    out = []
    for i in range(vb + 1, end + 1):
        b = B[i]
        if b['hi'] >= rhi - tol and i - lu >= P['SEP']:
            lu = i
            out.append(KR._resolve(B, i, end, rlo, rhi, tol, P['BUF'], True, width))
        if b['lo'] <= rlo + tol and i - ld >= P['SEP']:
            ld = i
            out.append(KR._resolve(B, i, end, rlo, rhi, tol, P['BUF'], False, width))
    return out


def rates(ev):
    rot = sum(1 for e in ev if e['outcome'] == 'rotation')
    brk = sum(1 for e in ev if e['outcome'] == 'broke_same_side')
    cen = sum(1 for e in ev if e['outcome'] == 'censored')
    res = rot + brk
    return len(ev), rot, brk, cen, (100 * rot / res if res else 0.0), (100 * rot / len(ev) if ev else 0.0)


def main():
    B = E.load_m1(); V6.prepare(B)
    P = dict(features.DEFAULT_P)
    states, arms, valids = features.range_struct_scan(B, P)
    eps = KR.episodes_from_states(states, valids)
    eps37 = [e for e in eps if B[e['valid_bar']]['ym'] in INS]

    hdr("K.1 — tai lap so THAT cua RESULTS_KB3.md §4 (dung chinh ham cua GD7)")
    ev_real = []
    for e in eps37:
        ev_real += touches(B, e['valid_bar'], e['end_bar'], e['rhi'], e['rlo'], P)
    n, rot, brk, cen, r_res, r_all = rates(ev_real)
    print(f"  so range (episode) 5-7/2026 = {len(eps37)}")
    print(f"  so lan cham = {n}   rotation={rot}  broke_same_side={brk}  censored={cen}")
    print(f"  ty le xoay / da phan giai = {r_res:.1f}%   |  / toan bo = {r_all:.1f}%")
    pn = [P['BUF'] / (P['BUF'] + e['width']) for e in ev_real]
    print(f"  null gambler's-ruin cua bao cao = {100*st.mean(pn):.1f}%")
    print(f"  (RESULTS_KB3.md §4 bao: 175 cham, rot=55, brk=58, cen=62, 48.7% / 31.4%, null 3.7%)")

    hdr("K.2 — PLACEBO: cung do rong + cung thoi luong, neo o moc thoi gian NGAU NHIEN")
    pool = [i for i, b in enumerate(B) if b['ym'] in INS]
    lo, hi = pool[0], pool[-1]
    NSIM = 200
    res_rates, all_rates, ns = [], [], []
    for _ in range(NSIM):
        ev = []
        for e in eps37:
            dur = e['end_bar'] - e['valid_bar']
            w = e['width']
            s = random.randint(lo, max(lo, hi - dur - 1))
            ctr = B[s]['c']
            ev += touches(B, s, min(hi, s + dur), ctr + w / 2.0, ctr - w / 2.0, P)
        nn, rr, bb, cc, a, b2 = rates(ev)
        res_rates.append(a); all_rates.append(b2); ns.append(nn)
    res_rates.sort(); all_rates.sort()
    print(f"  {NSIM} mo phong placebo (moi lan tai tao {len(eps37)} 'range' gia):")
    print(f"  so lan cham placebo: med={st.median(ns):.0f} (that = {n})")
    print(f"  ty le xoay / da phan giai:  med={st.median(res_rates):.1f}%  "
          f"p05={res_rates[int(.05*NSIM)]:.1f}%  p95={res_rates[int(.95*NSIM)]:.1f}%   (THAT = {r_res:.1f}%)")
    print(f"  ty le xoay / toan bo:       med={st.median(all_rates):.1f}%  "
          f"p05={all_rates[int(.05*NSIM)]:.1f}%  p95={all_rates[int(.95*NSIM)]:.1f}%   (THAT = {r_all:.1f}%)")
    p = sum(1 for x in res_rates if x >= r_res) / NSIM
    print(f"  p-value (placebo dat >= ty le THAT) = {p:.3f}")
    if p >= 0.05:
        print("  ==> THAT KHONG vuot placebo => tuyen bo '48.7% vs 3.7% => CO edge cau truc' KHONG DUNG VUNG.")
    else:
        print("  ==> THAT vuot placebo => co edge cau truc that (nhung null 3.7% cua bao cao van sai loai).")

    hdr("K.3 — do rieng phan LOOK-AHEAD: bien CUOI CUNG vs bien TAI THOI DIEM CHAM")
    ev_causal = []
    for e in eps37:
        vb, end = e['valid_bar'], e['end_bar']
        lu = ld = -999
        for i in range(vb + 1, end + 1):
            s = states[i]
            if s is None or s.get('i0') != e['i0']:
                continue
            rhi_i, rlo_i = s['rhi'], s['rlo']        # bien TAI NEN i (nhan-qua)
            w = rhi_i - rlo_i
            tol = max(P['TOLMIN'], P['TOLF'] * w)
            if B[i]['hi'] >= rhi_i - tol and i - lu >= P['SEP']:
                lu = i
                ev_causal.append(KR._resolve(B, i, end, rlo_i, rhi_i, tol, P['BUF'], True, w))
            if B[i]['lo'] <= rlo_i + tol and i - ld >= P['SEP']:
                ld = i
                ev_causal.append(KR._resolve(B, i, end, rlo_i, rhi_i, tol, P['BUF'], False, w))
    n2, rot2, brk2, cen2, a2, b3 = rates(ev_causal)
    print(f"  dung bien CUOI CUNG (nhu GD7):        n={n:3d} rot={rot:3d} brk={brk:3d} cen={cen:3d} "
          f"-> xoay/phan giai = {r_res:.1f}%")
    print(f"  dung bien TAI NEN CHAM (nhan-qua):    n={n2:3d} rot={rot2:3d} brk={brk2:3d} cen={cen2:3d} "
          f"-> xoay/phan giai = {a2:.1f}%")
    print(f"  chenh do LOOK-AHEAD bien = {r_res - a2:+.1f} diem")
    print("  (Luu y: end_bar VAN la thong tin tuong lai o ca 2 dong — chi co the bo hoan toan neu")
    print("   viet lai phep do; day chi tach RIENG phan do bien cuoi cung gay ra.)")


if __name__ == '__main__':
    main()
