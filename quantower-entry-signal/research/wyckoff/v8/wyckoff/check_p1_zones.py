#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_p1_zones.py — P1 (PLAN_KB_ABC.md §3.1/§3.2/§5): kiem chung zones_corven.py truoc khi tin.

Lam 3 viec (khong sua zones_corven.py — file do dong bang, xem PHAN 2 cua prompt):
  1. In 13 moc TUAN cua 5-7/2026 (da co trong zones_corven.main(), o day loc rieng de doc
     de) + dem so ngay that trong week span (dung cach dem KHAC group_days cua ho, vi
     group_days dem theo gap>45' -> ra so "block" chu khong phai so ngay lich, xem canh bao).
  2. Sweep min_ratio in {1.3, 1.5, 1.8} cho HVN tuan/ngay, dem so vung/tuan, so vung/ngay.
  3. Kiem NHAN QUA bang so: cat chuoi B[:t], tinh lai HVN tuan/ngay tai mot so moc, so voi
     HVN tinh tu build_zone_series chay tren FULL B (chi tinh 1 lan) -> phai TRUNG KHIT.
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))          # .../v8/wyckoff
V8 = os.path.dirname(HERE)                                  # .../v8
WYCK = os.path.dirname(V8)                                   # .../research/wyckoff
RESEARCH = os.path.dirname(WYCK)                             # .../research
sys.path.insert(0, V8)
sys.path.insert(0, RESEARCH)

import entry_dxfeed as E
import zones_corven as Z


def in_sample(B):
    return [b for b in B if b['ym'] in ('2026-05', '2026-06', '2026-07')]


def part1_weeks(B):
    print("=" * 100)
    print("PHAN 1 — 13 moc TUAN cua 5-7/2026 (loc tu danh sach day cua zones_corven)")
    print("=" * 100)
    days = Z.group_days(B)
    weeks = Z.group_weeks(B, days)
    # loc week co start nam trong 2026-05..07 (hoac giao voi cua so nay)
    in_weeks = [w for w in weeks if B[w[0][0]]['dt'].strftime('%Y-%m') in ('2026-05', '2026-06', '2026-07')]
    print(f"so tuan loc duoc trong cua so 5-7/2026: {len(in_weeks)}")
    for w in in_weeks:
        fr, to = w[0][0], w[-1][1]
        st = B[fr]['dt']
        wd = st.strftime('%A')
        print(f"  start={st} ({wd})  end={B[to]['dt']}  n_block(gap>45')={len(w)}")
    # dem so NGAY LICH thuc su (phan biet voi n_block) — dem theo set ngay duong lich cua cac bar
    print("\n  --> doi chieu: so NGAY LICH thuc (set ngay cua tat ca bar trong tuan), khong phai n_block:")
    for w in in_weeks:
        fr, to = w[0][0], w[-1][1]
        days_set = sorted(set(b['dt'].strftime('%Y-%m-%d') for b in B[fr:to + 1]))
        print(f"    start={B[fr]['dt']}  so ngay lich that = {len(days_set)}  ({days_set[0]}..{days_set[-1]})")


def part2_sweep_ratio(B):
    print("\n" + "=" * 100)
    print("PHAN 2 — sweep min_ratio {1.3,1.5,1.8} cho HVN tuan/ngay (dem so vung TRUNG BINH/ky)")
    print("=" * 100)
    days = Z.group_days(B)
    weeks = Z.group_weeks(B, days)
    week_spans = [(w[0][0], w[-1][1]) for w in weeks if B[w[0][0]]['dt'].strftime('%Y-%m') in ('2026-05', '2026-06', '2026-07')]
    day_spans = [d for d in days if B[d[0]]['dt'].strftime('%Y-%m') in ('2026-05', '2026-06', '2026-07')]
    for min_ratio in (1.3, 1.5, 1.8):
        wc = [len(Z.hvn_of(B, fr, to, min_ratio=min_ratio)) for fr, to in week_spans]
        dc = [len(Z.hvn_of(B, fr, to, min_ratio=min_ratio)) for fr, to in day_spans]
        w_empty = sum(1 for c in wc if c == 0)
        d_empty = sum(1 for c in dc if c == 0)
        print(f"  min_ratio={min_ratio}: TUAN n={len(wc)} trungbinh={sum(wc)/len(wc):.2f} "
              f"vung/tuan (0-vung={w_empty}/{len(wc)})  |  NGAY n={len(dc)} trungbinh={sum(dc)/len(dc):.2f} "
              f"vung/ngay (0-vung={d_empty}/{len(dc)})")


def part3_causal_check(B):
    print("\n" + "=" * 100)
    print("PHAN 3 — KIEM NHAN QUA: cat chuoi tai t, tinh lai HVN tuan/ngay W_CLOSED/D_CLOSED, so voi FULL")
    print("=" * 100)
    # build tren FULL B mot lan (bao gom ca sau moc cat)
    series_w_full = Z.build_zone_series(B, mode='week', causal='closed')
    series_d_full = Z.build_zone_series(B, mode='day', causal='closed')
    lookup_w_full = Z.zone_lookup_series(series_w_full)
    lookup_d_full = Z.zone_lookup_series(series_d_full)

    # chon 5 moc thoi gian rai deu trong 5-7/2026 de kiem
    sample_idx = in_sample(B)
    checkpoints = [sample_idx[int(len(sample_idx) * f)]['dt'] for f in (0.1, 0.3, 0.5, 0.7, 0.9)]

    mismatches = 0
    for dt in checkpoints:
        # tim index t = bar cuoi cung co dt <= checkpoint (chuoi CAT tai day)
        t = max(i for i, b in enumerate(B) if b['dt'] <= dt)
        B_cut = B[:t + 1]
        series_w_cut = Z.build_zone_series(B_cut, mode='week', causal='closed')
        series_d_cut = Z.build_zone_series(B_cut, mode='day', causal='closed')
        lookup_w_cut = Z.zone_lookup_series(series_w_cut)
        lookup_d_cut = Z.zone_lookup_series(series_d_cut)

        rw_full = lookup_w_full(dt)
        rw_cut = lookup_w_cut(dt)
        rd_full = lookup_d_full(dt)
        rd_cut = lookup_d_cut(dt)

        ok_w = (rw_full == rw_cut)
        ok_d = (rd_full == rd_cut)
        if not ok_w:
            mismatches += 1
        if not ok_d:
            mismatches += 1
        print(f"  t_cut={dt}  W_CLOSED khop={ok_w}  D_CLOSED khop={ok_d}"
              + ("" if (ok_w and ok_d) else f"   !!! LECH: full_w={rw_full} cut_w={rw_cut} full_d={rd_full} cut_d={rd_cut}"))

    print(f"\n  => TONG SO LECH (look-ahead) = {mismatches} / {2*len(checkpoints)} phep kiem")
    print("     (0 la BAT BUOC — lech nghia la zone_lookup_series dang doc du lieu TUONG LAI so voi t_cut)")


def main():
    B = E.load_m1()
    part1_weeks(B)
    part2_sweep_ratio(B)
    part3_causal_check(B)


if __name__ == '__main__':
    main()
