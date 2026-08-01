#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1 — kiem zone provider CORVEN truoc khi tin no (PLAN §5, pha P1).
Sweep min_ratio HVN + kiem nhan qua bang cat chuoi."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)
sys.path.insert(0, WYCK)
sys.path.insert(0, V8)

import entry_dxfeed as E   # noqa: E402
import zones_corven as ZC  # noqa: E402


def count_report(B):
    print("\n== So vung/tuan va vung/ngay (min_ratio mac dinh 1.5, max_n=3) ==")
    ser_w = ZC.build_zone_series(B, mode='week', causal='closed')
    ser_d = ZC.build_zone_series(B, mode='day', causal='closed')
    nw = [len(h) for _, _, _, h in ser_w]
    nd = [len(h) for _, _, _, h in ser_d]
    print(f"  TUAN : {len(ser_w)} tuan co hieu luc | so HVN/tuan min={min(nw)} max={max(nw)} "
          f"trung binh={sum(nw)/len(nw):.2f} | so tuan 0-HVN={sum(1 for x in nw if x==0)}")
    print(f"  NGAY : {len(ser_d)} ngay co hieu luc | so HVN/ngay min={min(nd)} max={max(nd)} "
          f"trung binh={sum(nd)/len(nd):.2f} | so ngay 0-HVN={sum(1 for x in nd if x==0)}")


def sweep_min_ratio(B):
    print("\n== Sweep min_ratio {1.3, 1.5, 1.8} — HVN TUAN, cua so scored 5-7/2026 ==")
    days = ZC.group_days(B)
    weeks = ZC.group_weeks(B, days)
    # chi xet cac tuan co bar nam trong 5-7/2026
    for mr in (1.3, 1.5, 1.8):
        cnts = []
        for k in range(1, len(weeks)):
            fr_prev, to_prev = weeks[k - 1][0][0], weeks[k - 1][-1][1]
            eff_from = B[weeks[k][0][0]]['dt']
            if not (eff_from.strftime('%Y-%m') in ('2026-05', '2026-06', '2026-07')):
                continue
            hvn = ZC.hvn_of(B, fr_prev, to_prev, min_ratio=mr)
            cnts.append(len(hvn))
        avg = sum(cnts) / len(cnts) if cnts else 0
        print(f"  min_ratio={mr}: {len(cnts)} tuan trong 5-7/2026 | so HVN/tuan: {cnts} | TB={avg:.2f}")


def causal_check(B):
    print("\n== Kiem nhan qua: cat chuoi tai t, tinh lai, so voi ban day du ==")
    # chon 2 moc: 1 o giua tuan (mode week), 1 o giua ngay (mode day), trong cua so 5-7/2026
    days = ZC.group_days(B)
    weeks = ZC.group_weeks(B, days)
    # chon tuan thu 30 (nam trong 5-7/2026) lam moc kiem
    target_week_idx = None
    for k, w in enumerate(weeks):
        if B[w[0][0]]['dt'].strftime('%Y-%m') == '2026-06':
            target_week_idx = k
            break
    w = weeks[target_week_idx]
    mid_bar = w[0][0] + (w[-1][1] - w[0][0]) // 2   # nen giua tuan do

    full_series_w = ZC.build_zone_series(B, mode='week', causal='closed')
    full_lookup_w = ZC.zone_lookup_series(full_series_w)
    t = B[mid_bar]['dt']
    got_full = full_lookup_w(t)

    B_cut = B[:mid_bar + 1]   # cat het du lieu SAU t (chi giu <= t)
    cut_series_w = ZC.build_zone_series(B_cut, mode='week', causal='closed')
    cut_lookup_w = ZC.zone_lookup_series(cut_series_w)
    got_cut = cut_lookup_w(t)

    def hvn_prices(x):
        if x is None:
            return None
        fr, to, hvn = x
        return sorted(round(p, 2) for p, _, _ in hvn)

    ok_w = hvn_prices(got_full) == hvn_prices(got_cut)
    print(f"  WEEK  t={t}  full={hvn_prices(got_full)}  cat={hvn_prices(got_cut)}  "
          f"{'TRUNG KHIT (nhan qua OK)' if ok_w else '!!! LECH -> LOOK-AHEAD'}")

    # tuong tu cho DAY
    days_in_window = [d for d in days if B[d[0]]['dt'].strftime('%Y-%m') == '2026-06']
    d_target = days_in_window[len(days_in_window) // 2]
    mid_bar_d = d_target[0] + (d_target[1] - d_target[0]) // 2
    full_series_d = ZC.build_zone_series(B, mode='day', causal='closed')
    full_lookup_d = ZC.zone_lookup_series(full_series_d)
    td = B[mid_bar_d]['dt']
    got_full_d = full_lookup_d(td)
    B_cut_d = B[:mid_bar_d + 1]
    cut_series_d = ZC.build_zone_series(B_cut_d, mode='day', causal='closed')
    cut_lookup_d = ZC.zone_lookup_series(cut_series_d)
    got_cut_d = cut_lookup_d(td)
    ok_d = hvn_prices(got_full_d) == hvn_prices(got_cut_d)
    print(f"  DAY   t={td}  full={hvn_prices(got_full_d)}  cat={hvn_prices(got_cut_d)}  "
          f"{'TRUNG KHIT (nhan qua OK)' if ok_d else '!!! LECH -> LOOK-AHEAD'}")

    # kiem them che do RUNNING (phai TU thay doi trong tuan/ngay, khong duoc trung full-history
    # tai moi thoi diem — nhung van phai nhan qua: cat tai t phai ra dung snapshot da chot GAN NHAT)
    full_series_wr = ZC.build_zone_series(B, mode='week', causal='running')
    full_lookup_wr = ZC.zone_lookup_series(full_series_wr)
    got_full_wr = full_lookup_wr(t)
    cut_series_wr = ZC.build_zone_series(B_cut, mode='week', causal='running')
    cut_lookup_wr = ZC.zone_lookup_series(cut_series_wr)
    got_cut_wr = cut_lookup_wr(t)
    ok_wr = hvn_prices(got_full_wr) == hvn_prices(got_cut_wr)
    print(f"  WEEK(running) t={t}  full={hvn_prices(got_full_wr)}  cat={hvn_prices(got_cut_wr)}  "
          f"{'TRUNG KHIT (nhan qua OK)' if ok_wr else '!!! LECH -> LOOK-AHEAD'}")


if __name__ == '__main__':
    B = E.load_m1()
    count_report(B)
    sweep_min_ratio(B)
    causal_check(B)
