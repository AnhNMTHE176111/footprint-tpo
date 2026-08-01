#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_combo_random_control.py — doi chung ngau nhien cho cau hoi cua nguoi hoc: "giu nguyen
CBR+QUAY_DAU (baseline), CONG THEM (union) tin hieu neo HVN/VWAP tuan+ngay (CORVEN) — tang n/WR/R
that hay chi vi THEM tin hieu bat ky (kha nang zone dat SAI cho van tang y het)?"

Dung lai KHONG SUA: v8/runner/combo_scan.py (sess_raw/zone_raw/evaluate_rev/B/C/vf/zone_w/zone_d),
v8/runner/cbr_hvn.py (run/run_zone/dedup/cooldown/post/evaluate/MONTHS), v8/runner/zone_engine.py
(shifted_zone_lookup_seeded — dich MOI zone +-3 gia, dau ngau nhien theo seed, CO THE TAI LAP).

Chay: python3 check_combo_random_control.py
"""
import os
import sys
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
RUNNER = os.path.join(V8, 'runner')
sys.path.insert(0, RUNNER)

import combo_scan as CS   # noqa: E402  (B, C, vf, zone_w, zone_d, sess_raw, zone_raw, evaluate_rev)
import cbr_hvn as CBR     # noqa: E402
import zone_engine as ZE  # noqa: E402

B, C, vf = CS.B, CS.C, CS.vf
SEEDS = (1, 2, 3, 4, 5)
SHIFT_PTS = 3.0


def cbr_combo_shifted(seed):
    zw = ZE.shifted_zone_lookup_seeded(CS.zone_w, seed, shift_pts=SHIFT_PTS)
    zd = ZE.shifted_zone_lookup_seeded(CS.zone_d, seed + 100, shift_pts=SHIFT_PTS)
    raw = CBR.run(B, C, vf, None) + CBR.run_zone(B, C, vf, zw) + CBR.run_zone(B, C, vf, zd)
    return CBR.evaluate(B, CBR.post(CBR.cooldown(CBR.dedup(raw), C['COOL']), C), C)


def rev_combo_shifted(seed):
    zw = ZE.shifted_zone_lookup_seeded(CS.zone_w, seed, shift_pts=SHIFT_PTS)
    zd = ZE.shifted_zone_lookup_seeded(CS.zone_d, seed + 100, shift_pts=SHIFT_PTS)
    raw = CS.sess_raw(B, vf) + CS.zone_raw(B, zw, vf) + CS.zone_raw(B, zd, vf)
    sig = [s for s in CBR.cooldown(CBR.dedup(raw), ZE.LIVE1['cooldown']) if s['ym'] in CBR.MONTHS]
    return CS.evaluate_rev(B, sig, rr=1.5)


def ev_of(S):
    return (sum(s['r'] for s in S) / len(S)) if S else 0.0


def stat_line(tag, S):
    n = len(S)
    if n == 0:
        print(f"  {tag}: n=0")
        return 0, 0.0, 0.0
    w = sum(1 for s in S if s['r'] > 0)
    tot = sum(s['r'] for s in S)
    print(f"  {tag}: n={n:3d}  WR={100*w/n:5.1f}%  tong={tot:+7.1f}R  EV={tot/n:+.3f}")
    return n, tot, tot / n


def main():
    print("=" * 100)
    print("DOI CHUNG NGAU NHIEN — dich HVN/VWAP tuan+ngay +-3 gia, 5 seed, giu NGUYEN logic phat hien")
    print("=" * 100)

    real_cbr = CS.cbr_combo()
    real_rev = CS.rev_combo()
    print("\n[CBR / PLAY2 — SAU (that, + HVN/VWAP tuan+ngay THAT)]")
    n_r1, tot_r1, ev_r1 = stat_line("  THAT", real_cbr)

    print("\n[CBR / PLAY2 — SAU nhung vung BI DICH NGAU NHIEN (+-3 gia)]")
    cbr_rand = []
    for sd in SEEDS:
        S = cbr_combo_shifted(sd)
        n, tot, ev = stat_line(f"  seed={sd}", S)
        cbr_rand.append((n, tot, ev))
    ev_cbr_rand_mean = st.mean(x[2] for x in cbr_rand)
    tot_cbr_rand_mean = st.mean(x[1] for x in cbr_rand)
    n_cbr_rand_mean = st.mean(x[0] for x in cbr_rand)
    gap_cbr = ev_r1 - ev_cbr_rand_mean
    print(f"  -> TB 5 seed: n={n_cbr_rand_mean:.0f}  tong={tot_cbr_rand_mean:+.1f}R  EV={ev_cbr_rand_mean:+.3f}")
    print(f"  -> GAP (EV that - EV ngau nhien) = {gap_cbr:+.3f}")

    print("\n[QUAY_DAU / PLAY1 — SAU (that, + HVN/VWAP tuan+ngay THAT)]")
    n_r2, tot_r2, ev_r2 = stat_line("  THAT", real_rev)

    print("\n[QUAY_DAU / PLAY1 — SAU nhung vung BI DICH NGAU NHIEN (+-3 gia)]")
    rev_rand = []
    for sd in SEEDS:
        S = rev_combo_shifted(sd)
        n, tot, ev = stat_line(f"  seed={sd}", S)
        rev_rand.append((n, tot, ev))
    ev_rev_rand_mean = st.mean(x[2] for x in rev_rand)
    tot_rev_rand_mean = st.mean(x[1] for x in rev_rand)
    n_rev_rand_mean = st.mean(x[0] for x in rev_rand)
    gap_rev = ev_r2 - ev_rev_rand_mean
    print(f"  -> TB 5 seed: n={n_rev_rand_mean:.0f}  tong={tot_rev_rand_mean:+.1f}R  EV={ev_rev_rand_mean:+.3f}")
    print(f"  -> GAP (EV that - EV ngau nhien) = {gap_rev:+.3f}")

    print("\n" + "=" * 100)
    print("KET LUAN (nguong PLAN_KB_ABC.md §5 P4: PASS gap>=+0.25R | KILL gap<+0.10R):")
    for tag, gap in (("CBR/PLAY2", gap_cbr), ("QUAY_DAU/PLAY1", gap_rev)):
        v = "PASS" if gap >= 0.25 else ("KILL" if gap < 0.10 else "VUNG GIUA (khong du manh)")
        print(f"  {tag}: gap={gap:+.3f} => {v}")


if __name__ == '__main__':
    main()
