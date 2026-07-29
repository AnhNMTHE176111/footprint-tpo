#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_kb12.py — script chinh cua luot GD4->GD6 (KB1 + KB2), theo SPEC_V7_3KB.md §4.10/§5.10.
Chay: python3 research/wyckoff/v7/run_kb12.py
In toan bo bang (GOLDEN, RangeMode A/B, bias A/B, WY04, KB2 ExtremeWin, KB2 ZoneExtend,
KB2 delta-confirm tren fp-m1). KHONG bia so — moi dong la ket qua that cua engine.
"""
import sys, os, statistics as st
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "research"))
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")

import entry_dxfeed as E
import cbr_v6 as V
import engine, features, report, loaders

MONTHS = ('2026-05', '2026-06', '2026-07')


def section(title):
    print("\n" + "=" * 124)
    print(title)
    print("=" * 124)


# ===================================================================================== BUOC 0 — GOLDEN
def step0_golden(B, vf):
    section("BUOC 0 — GOLDEN TEST (engine v7, feature moi TAT, phai khop BASELINE.md)")
    C = V.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    S_base = V.scan(B, C, vf, None)
    S_v7 = engine.scan_box(B, C, vf, bias_at=None)
    print("cbr_v6.scan (BASELINE dong bang):")
    d_base = report.line("B4 baseline (cbr_v6)", S_base)
    print("engine.scan_box (v7, RangeMode=0/BIAS_ON=off = NO-OP):")
    d_v7 = report.line("B4 v7-box (feature tat)", S_v7)
    ids_b = sorted((s['i'], s['side']) for s in S_base)
    ids_v = sorted((s['i'], s['side']) for s in S_v7)
    same = ids_b == ids_v
    print(f"\n{len(S_base)} vs {len(S_v7)} tin hieu, cung bo (i,side)? {same}")
    verdict = "GOLDEN OK" if (same and d_base == d_v7) else "GOLDEN MISMATCH — DUNG TOAN BO"
    print(f"==> {verdict}")
    assert same, "GOLDEN TEST THAT BAI — dung lai, khong di tiep (theo luat chung)"
    return S_v7   # dung ban engine (co them field 'pext' can cho WY04 o buoc 4) — da chung minh == S_base


# ===================================================================================== BUOC 1 — range_struct vs probe
def step1_range_struct(B):
    section("BUOC 1 — range_struct.py doi chieu probe (SPEC §4.3/§4.10-1), muc tieu n_range~322")
    states, arms, valids = features.range_struct_scan(B)
    valids37 = [v for v in valids if B[v['i']]['ym'] in MONTHS]
    arms37 = [a for a in arms if B[a['i']]['ym'] in MONTHS]
    PROBE_N = 322
    lech = abs(len(valids37) - PROBE_N) / PROBE_N
    print(f"n_range (VALID lan dau, state machine bar-by-bar) 5-7/2026 = {len(valids37)}")
    print(f"n_range probe (scan-cua-so, FORM=30/TOUCH=2/WMAX=6.0, §11.B) = {PROBE_N}")
    print(f"lech = {lech*100:.0f}%  (nguong dung: 25%)")
    if valids37:
        ws = sorted(v['width'] for v in valids37)
        print(f"  do rong (gia) tai VALID: min={ws[0]:.1f} med={st.median(ws):.1f} max={ws[-1]:.1f}")
    print(f"so ARM event (KB1 se dung, 5-7/2026) = {len(arms37)}")
    if lech > 0.25:
        print("==> LECH > 25% -> THEO SPEC §4.3: DUNG buoc nay, KHONG dung ket qua RangeMode=1 "
              "lam H5 hop le. Van chay tiep de xem so (chi de THONG TIN), xem RESULTS_KB12.md muc 'da thu va bo'.")
    return states, arms, valids


# ===================================================================================== BUOC 2 — RangeMode 0 vs 1 (H5, THONG TIN — xem buoc 1)
def step2_rangemode(B, vf, arms):
    section("BUOC 2 — RangeMode 0 (box, v6) vs 1 (struct) — H5 (CANH BAO: buoc 1 da lech >25%)")
    C = V.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    S0 = engine.scan_box(B, C, vf, bias_at=None)
    S1 = engine.scan_struct(B, C, vf, arms, bias_at=None)
    report.line("RangeMode=0 (box, mac dinh)", S0)
    report.line("RangeMode=1 (struct, THONG TIN)", S1)
    if not S1 or len(S1) < 25:
        print(f"==> n(RangeMode=1) = {len(S1)} < 25 -> KHONG KET LUAN / KILL theo nguong n. "
              "Giu mac dinh RangeMode=0. (H5 KHONG PASS)")


# ===================================================================================== BUOC 3 — bias A/B (H6, §2.6)
def step3_bias(B, vf):
    section("BUOC 3 — A/B bias TPO (session_bias) vs proxy trend[-480] tren KB1 (H6, SPEC §2.6)")
    bias_at, blog = features.session_bias_series(B)
    zero_frac = sum(1 for l in blog if l['bias'] == 0) / len(blog) if blog else 0
    print(f"so phien co the tinh bias (s>=2, co D-1&D-2) = {len(blog)} "
          f"(tong so phien 9 thang = {len(loaders.sessions_from_m1(B))})")
    print(f"phan bo bias theo PHIEN (KHOA sau ready_at): {dict(Counter(l['bias'] for l in blog))}")
    print(f"ty le phien bias==0 = {zero_frac*100:.0f}%  (proxy trend[-480] chi 2-4% theo SPEC §2.1)")

    Cbase = dict(CLEAN=True, PMAX=1.00, RR=4.0)
    branches = {}
    for tag, trend_on, bias_on in [('A0 (baseline: TrendProxy ON, Bias OFF)', True, False),
                                    ('A1 (Bias THAY THE: TrendProxy OFF, Bias ON)', False, True),
                                    ('A2 (Bias CONG THEM: ca 2 ON)', True, True),
                                    ('A3 (khong loc gi: ca 2 OFF)', False, False)]:
        C = V.cfg(TREND=trend_on, BIAS_ON=bias_on, **Cbase)
        S = engine.scan_box(B, C, vf, bias_at=bias_at)
        d = report.line(tag, S)
        branches[tag] = (S, d)

    a0n = branches['A0 (baseline: TrendProxy ON, Bias OFF)'][1]
    a1n = branches['A1 (Bias THAY THE: TrendProxy OFF, Bias ON)'][1]
    a2n = branches['A2 (Bias CONG THEM: ca 2 ON)'][1]
    print("\nPhan xu (SPEC §2.6): chon EV cao nhat voi n>=25; A1~A2 chenh <0.15R thi chon A1 (it tham so hon).")
    for tag, (S, d) in branches.items():
        ok = (d is not None and d['n'] >= 25)
        print(f"  {tag:<48} n={d['n'] if d else 0:3d} EV={d['ev'] if d else 0:+.3f}  {'(n<25, khong ket luan)' if not ok else ''}")

    # ---- partition bat buoc: tren pool RONG NHAT (A3: khong loc gi), tach theo bias co dong y side khong
    section("BUOC 3b — PARTITION bat buoc cho bias (SPEC §2.6): tach pool A3 theo bias co dung side khong")
    C3 = V.cfg(TREND=False, BIAS_ON=False, **Cbase)
    raw3 = engine.run_box(B, C3, vf, bias_at=None)
    sig3 = V.post(V.cooldown(V.dedup(raw3), C3['COOL']), C3)
    keep, drop = [], []
    for s in sig3:
        sd = 1 if s['side'] == 'LONG' else -1
        j = s['i']
        (keep if bias_at[j] == sd else drop).append(s)
    S_keep = engine.evaluate_v7(B, keep, C3)
    S_drop = engine.evaluate_v7(B, drop, C3)
    report.partition("GIU (bias dung side)", S_keep, "LOAI (bias sai/0)", S_drop)

    section("BUOC 3c — sweep TOL/MIN_SCORE cua bias (SPEC §2.4) — bias da KILL o partition tren, "
            "sweep de kiem co 'diem dep' don le nao khong (dau hieu overfit) hay deu kem nhu nhau")
    rows = []
    for tol_v in (0.2, 0.5, 1.0):
        for ms in (1, 2, 3):
            bat, _ = features.session_bias_series(B, tol=tol_v, min_score=ms)
            C2 = V.cfg(TREND=False, BIAS_ON=True, **Cbase)
            S2 = engine.scan_box(B, C2, vf, bias_at=bat)
            tag = f"TOL={tol_v} MIN_SCORE={ms}"
            d = report.line(f"  bias {tag}", S2)
            rows.append((tag, d))
    report.sweep("bias TOL x MIN_SCORE (A1-style: TrendProxy OFF, Bias ON)", rows)
    return bias_at, blog


# ===================================================================================== BUOC 4 — WY04 (H7, §4.10-4)
def step4_wy04(B, S0):
    section("BUOC 4 — WY04 No Supply/No Demand o nhip hoi — partition tren 33 lenh v6 (H7)")
    ok = engine.wy04_ok(B, S0)
    keep = [s for s, k in zip(S0, ok) if k]
    drop = [s for s, k in zip(S0, ok) if not k]
    print(f"so lenh co WY04 tai nen pext = {len(keep)} / {len(S0)}")
    report.partition("CO WY04 (no_supply/no_demand)", keep, "KHONG CO WY04", drop)


# ===================================================================================== KB2 §5.10
def kb2_load():
    sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/wyckoff")
    sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
    import imp_reversal_sweep as S
    return S


def step5_kb2_baseline(S):
    section("KB2 BASELINE (QUAY_DAU, LIVE params) — moc so BASELINE.md")
    B = S.bars()
    sigs = S.in_window(B, S.detect(B))
    res = S.score(B, sigs, S.LIVE['rr'])
    S.fmt(res, "QUAY_DAU LIVE params (moc BASELINE)")
    return B, sigs, res


def step6_kb2_extremewin(S, B, sigs):
    section("KB2 BUOC 1 — Kb2ExtremeWin (CHART_CASES loi #6: cuc tri phai la cuc tri N nen gan nhat)")
    for win in (10, 20, 60):
        keep, drop = [], []
        for s in sigs:
            i = s['i']
            w = B[max(0, i - win):i + 1]
            if s['side'] == 'SHORT':
                is_extreme = B[i]['hi'] >= max(x['hi'] for x in w) - 1e-9
            else:
                is_extreme = B[i]['lo'] <= min(x['lo'] for x in w) + 1e-9
            (keep if is_extreme else drop).append(s)

        def sc(SS):
            return S.score(B, SS, S.LIVE['rr'])
        rk, rd = sc(keep), sc(drop)
        print(f"-- Kb2ExtremeWin={win} --")
        S.fmt(rk, f"  GIU (dinh/day cua so {win})")
        S.fmt(rd, f"  LOAI (khong phai cuc tri {win})")
        if rd['closed'] >= 10:
            gap = rk['ev'] - rd['ev']
            print(f"     => EV_giu-EV_loai={gap:+.3f}  {'PASS' if gap>=0.30 else 'KILL - nhieu'}")
        else:
            print(f"     => KHONG KET LUAN (n_loai={rd['closed']} < 10)")


def step7_kb2_zoneextend(S, B, sigs):
    section("KB2 BUOC 2 — Kb2ZoneExtend (mo rong pool: D-1 VAH/VAL/POC/Dinh/Day + session POC/VAH/VAL, tol 7 tick)")
    pool = E.build_zones(B)
    CONFL_TOL_T = 7
    TICK = E.TICK
    zone_kinds = Counter()
    extended = []
    for s in sigs:
        t = s['dt']
        cands = [z for z in pool if z['ready'] <= t <= z['expire']
                 and abs(z['price'] - s['entry']) / TICK <= CONFL_TOL_T]
        if cands:
            best = max(cands, key=lambda z: z['strength'])
            zone_kinds[best['kind'].split()[0]] += 1
            extended.append(s)
    print(f"trong {len(sigs)} lenh QUAY_DAU (VWAP-only), so lenh CUNG luc hop luu vung D-1/session (+-{CONFL_TOL_T} tick) = {len(extended)}")
    print(f"phan loai vung hop luu: {dict(zone_kinds)}")
    res_all = S.score(B, sigs, S.LIVE['rr'])
    res_ext = S.score(B, extended, S.LIVE['rr'])
    S.fmt(res_all, "TOAN BO (VWAP-only, hien dang ship)")
    S.fmt(res_ext, "CHI lenh co hop luu them vung D-1/session")
    print("Kb2ZoneExtend O DAY = do XEM zone D-1/session co lam VWAP-touch manh hon (hop luu), "
          "KHONG PHAI mo rong sang arm-tai-zone-khac-VWAP (chua co detector rieng cho zone-only trong luot nay).")
    if res_ext['closed'] >= 10:
        print(f"n neu CHI lay lenh co hop luu = {res_ext['closed']} "
              f"({'>= 40 -> co the xem xet' if res_ext['closed']>=40 else '< 40'}) EV={res_ext['ev']:+.3f}")


def step8_kb2_delta_fpm1(S):
    section("KB2 BUOC 3 — Delta confirm tren fp-m1 (bao RIENG, KHONG so voi dxFeed)")
    Bf = loaders.load_fp_m1_full("fp-m1-6-month.csv")
    print(f"fp-m1-6-month.csv: {len(Bf)} nen | {Bf[0]['dt']} -> {Bf[-1]['dt']} (UTC+7, KHONG quy doi ve UTC)")
    # dung DUNG replicator LIVE (imp_reversal_sweep.detect), KHONG dung reversal_vwap.vwap_reversal()
    # (file do tu canh bao: "dung so tu detect() trong FILE NAY la SAI").
    sigs = S.detect(Bf)
    print(f"so tin hieu QUAY_DAU tren fp-m1 (LIVE params, ca 6 thang, CHUA cat 5-7) = {len(sigs)}")
    res_all = S.score(Bf, sigs, S.LIVE['rr'])
    S.fmt(res_all, "fp-m1 KHONG loc delta (= detect() nguyen ban)")

    def delta_ok(s):
        b = Bf[s['i']]
        sd = 1 if s['side'] == 'LONG' else -1
        return (b['delta'] > 0 if sd > 0 else b['delta'] < 0) and abs(b['delta_pct']) >= 20.0

    sigs_d = [s for s in sigs if delta_ok(s)]
    res_d = S.score(Bf, sigs_d, S.LIVE['rr'])
    S.fmt(res_d, "fp-m1 CO loc delta (sign dung huong + |Delta%|>=20)")
    if res_d['closed'] < 10:
        print(f"   => n={res_d['closed']} qua nho de ket luan (< 10), chi bao THONG TIN.")
    print("=> so o day CHI de doi chung NOI BO fp-m1 (bat/tat delta tren CUNG feed, CUNG detect() LIVE) — "
          "KHONG duoc so truc tiep voi n=27 cua dxFeed (SPEC §3: feature fp-only, fp-m1 chi ~6 thang + nhan UTC+7).")


def main():
    B = E.load_m1()
    vf = E.VOLFLOOR_FROZEN          # AUDIT_V7 §1.2: khong dung calc_volfloor() (look-ahead)
    E.VOLFLOOR_AUTO = vf
    V.prepare(B)
    print(f"dxFeed M1={len(B)} nen | {B[0]['dt']} -> {B[-1]['dt']} (UTC) | volfloor={vf}")

    S0 = step0_golden(B, vf)
    states, arms, valids = step1_range_struct(B)
    step2_rangemode(B, vf, arms)
    bias_at, blog = step3_bias(B, vf)
    step4_wy04(B, S0)

    S = kb2_load()
    Bq, sigs, res = step5_kb2_baseline(S)
    step6_kb2_extremewin(S, Bq, sigs)
    step7_kb2_zoneextend(S, Bq, sigs)
    step8_kb2_delta_fpm1(S)

    section("HET run_kb12.py")


if __name__ == '__main__':
    main()
