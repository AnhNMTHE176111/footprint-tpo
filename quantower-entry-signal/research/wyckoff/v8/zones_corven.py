#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/zones_corven.py — Zone provider cho khung CORVEN (PLAN_KB_ABC.md §3, pha P1).

CHỈ dựng HVN tuần/ngày + VWAP tuần/ngày, CAUSAL (khong nhin tuong lai). Khong POC/VAH/VAL/
vung theo phien A-Au-My (CORVEN_SPEC_V1.md §2). Neo tuan = phien dau tien co start >= CN
~22:00 UTC (SPEC_V7_3KB.md §1.2: "phien trong he nay bat dau ~22:00 UTC"). Ngay = gap>45'
(dung lai dung cach entry_dxfeed.daily_levels_from_m1 da gom).

Dung lai KHONG SUA: entry_dxfeed (loader dxFeed), verify_zones_v2.find_hvn/rows_of.

Chay: python3 quantower-entry-signal/research/wyckoff/v8/zones_corven.py
"""
import os
import sys
import bisect

HERE = os.path.dirname(os.path.abspath(__file__))
WYCK = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(WYCK)))
sys.path.insert(0, os.path.join(ROOT, 'quantower-entry-signal', 'research'))
sys.path.insert(0, os.path.join(ROOT, 'quantower-tpo-suite'))
sys.path.insert(0, WYCK)

import entry_dxfeed as E             # loader dxFeed, value_area/tpo_counts
import verify_zones_v2 as Z          # rows_of, find_hvn (port 1-1 tu C#)
import imp_reversal_sweep as KB2     # DX path (LIVE dict) — chi lay duong dan file


# ============================================================================
# 1. Gom NGAY / TUAN tu M1 — CAUSAL, chi dung ranh gioi thoi gian (khong nhin gia tri)
# ============================================================================
def group_days(B, gap_min=45):
    """(fr, to) index vao B cho tung NGAY giao dich. Ranh gioi = gap>45' (khop
    entry_dxfeed.daily_levels_from_m1, da do: ngay bat dau ~22:00 UTC)."""
    out, fr = [], 0
    for i in range(1, len(B)):
        if (B[i]['dt'] - B[i - 1]['dt']).total_seconds() > gap_min * 60:
            out.append((fr, i - 1))
            fr = i
    out.append((fr, len(B) - 1))
    return out


def group_weeks(B, days, weekend_gap_hours=30):
    """Gop danh sach ngay (fr,to) thanh TUAN. Ranh gioi tuan = khoang trong > 30h giua
    2 ngay lien tiep (cuoi tuan CME dong T6 toi -> mo lai CN toi, ~46h)."""
    weeks, cur = [], [days[0]]
    for d in days[1:]:
        gap_h = (B[d[0]]['dt'] - B[cur[-1][1]]['dt']).total_seconds() / 3600
        if gap_h > weekend_gap_hours:
            weeks.append(cur)
            cur = [d]
        else:
            cur.append(d)
    weeks.append(cur)
    return weeks


# ============================================================================
# 2. VWAP neo NGAY / TUAN — cumulative tu moc, reset tai moc
# ============================================================================
def _anchor_lookup(spans):
    """spans: list (fr,to). Tra ham idx-bar -> fr cua span chua no (bisect theo fr)."""
    frs = [s[0] for s in spans]

    def anchor_of(i):
        k = bisect.bisect_right(frs, i) - 1
        return frs[max(k, 0)]
    return anchor_of


def vwap_series(B, spans):
    """VWAP cumulative, reset tai fr cua moi span (ngay hoac tuan)."""
    anchor_of = _anchor_lookup(spans)
    out = [0.0] * len(B)
    csum_pv = csum_v = 0.0
    cur_anchor = None
    for i, b in enumerate(B):
        a = anchor_of(i)
        if a != cur_anchor:
            csum_pv = csum_v = 0.0
            cur_anchor = a
        tp = (b['hi'] + b['lo'] + b['c']) / 3.0
        csum_pv += tp * b['v']
        csum_v += b['v']
        out[i] = csum_pv / csum_v if csum_v > 0 else b['c']
    return out


# ============================================================================
# 3. HVN CAUSAL — 2 che do W_CLOSED / W_RUNNING (§3.2)
# ============================================================================
def _as_hlvol(bars):
    """Z.rows_of doi hoi key 'h'/'l'/'vol' (quy uoc M30 cua verify_zones_v2), M1 cua
    entry_dxfeed dung 'hi'/'lo'/'v' -> doi ten, khong dung lai gia tri."""
    return [dict(h=b['hi'], l=b['lo'], vol=b['v']) for b in bars]


def hvn_of(B, fr, to, min_ratio=1.5, max_n=3):
    """HVN (gia, count, ratio) tu M1[fr:to+1], dung lai Z.rows_of + Z.find_hvn nguyen ban."""
    if to - fr < 30:
        return []
    rows = Z.rows_of(_as_hlvol(B[fr:to + 1]))
    return Z.find_hvn(rows, min_ratio=min_ratio)[:max_n]


def build_zone_series(B, mode='week', causal='closed'):
    """
    Tra list (dt_hieu_luc, fr_dung_de_tinh, to_dung_de_tinh, hvn_list) — hieu luc TU
    dt_hieu_luc TRO DI, khong nhin qua khu xa hon fr/to da chot.

    mode: 'week' | 'day'
    causal:
      'closed'  = W_CLOSED/D_CLOSED — chi dung ky da DONG (ky N-1) cho toan bo ky N.
                  An toan tuyet doi, khong bao gio nhin thay du lieu dang chay.
      'running' = W_RUNNING/D_RUNNING — tinh lai HVN cua ky DANG CHAY, chot lai moi lan
                  dong 1 NGAY ben trong no (chi dung du lieu da dong).
    """
    days = group_days(B)
    spans = group_weeks(B, days) if mode == 'week' else [[d] for d in days]
    series = []
    if causal == 'closed':
        for k in range(1, len(spans)):
            fr_prev, to_prev = spans[k - 1][0][0], spans[k - 1][-1][1]
            hvn = hvn_of(B, fr_prev, to_prev)
            eff_from = B[spans[k][0][0]]['dt']
            series.append((eff_from, fr_prev, to_prev, hvn))
    else:  # running: chot lai sau MOI ngay trong ky, dung [dau ky .. cuoi ngay do]
        for span in spans:
            span_fr = span[0][0]
            for (d_fr, d_to) in span:
                hvn = hvn_of(B, span_fr, d_to)
                eff_from = B[d_to]['dt']
                series.append((eff_from, span_fr, d_to, hvn))
    return series


def zone_lookup_series(series):
    """Ham tra (fr, to, hvn) hieu luc tai thoi diem dt (ban ghi chot GAN NHAT truoc dt)."""
    dts = [s[0] for s in series]

    def get(dt):
        k = bisect.bisect_right(dts, dt) - 1
        if k < 0:
            return None
        return series[k][1], series[k][2], series[k][3]
    return get


# ============================================================================
# 4. Demo / diem dung P1 — in 13 moc tuan de mat thuong xac nhan (§5, hang P1)
# ============================================================================
def main():
    B = E.load_m1()
    print(f"M1={len(B)} nen  {B[0]['dt']} -> {B[-1]['dt']} (UTC)")

    days = group_days(B)
    weeks = group_weeks(B, days)
    print(f"\nSo NGAY gom duoc (gap>45'): {len(days)}")
    print(f"So TUAN gom duoc (gap>30h): {len(weeks)}")

    print("\n== 13 MOC TUAN (mat kiem: start co dung ~CN toi khong, dac biet quanh DST) ==")
    for w in weeks:
        fr = w[0][0]
        to = w[-1][1]
        n_days = len(w)
        print(f"  start={B[fr]['dt']}  end={B[to]['dt']}  so_ngay={n_days}")

    print("\n== HVN TUAN (W_CLOSED) — vai tuan gan nhat ==")
    ser_w = build_zone_series(B, mode='week', causal='closed')
    for eff_from, fr, to, hvn in ser_w[-6:]:
        lab = ", ".join(f"{p:.1f}(x{ratio:.1f})" for p, _, ratio in hvn) or "(khong co)"
        print(f"  hieu_luc_tu={eff_from}  nguon=[{B[fr]['dt']} .. {B[to]['dt']}]  HVN: {lab}")

    print("\n== HVN NGAY (D_CLOSED) — vai ngay gan nhat ==")
    ser_d = build_zone_series(B, mode='day', causal='closed')
    for eff_from, fr, to, hvn in ser_d[-6:]:
        lab = ", ".join(f"{p:.1f}(x{ratio:.1f})" for p, _, ratio in hvn) or "(khong co)"
        print(f"  hieu_luc_tu={eff_from}  nguon=[{B[fr]['dt']} .. {B[to]['dt']}]  HVN: {lab}")

    vwap_w = vwap_series(B, [(w[0][0], w[-1][1]) for w in weeks])
    vwap_d = vwap_series(B, days)
    print(f"\nVWAP tuan/ngay tinh xong cho {len(B)} nen. Mau 3 nen cuoi:")
    for i in range(len(B) - 3, len(B)):
        print(f"  {B[i]['dt']}  c={B[i]['c']:.1f}  vwap_ngay={vwap_d[i]:.2f}  vwap_tuan={vwap_w[i]:.2f}")


if __name__ == '__main__':
    main()
