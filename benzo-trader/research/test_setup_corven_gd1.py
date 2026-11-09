# -*- coding: utf-8 -*-
"""Test GĐ1 của setup CORVEN — ③ dấu hiệu, ④ lệnh, ⛔, 4d (plan mục 4, ca 1–7 và 10).
Chạy: python -m pytest benzo-trader/research/test_setup_corven_gd1.py -q

Dữ liệu tổng hợp dựng tay theo tick (0,1). Mặc định: mbr = 15 tick, medΔ = 20, nền_ô = 5 (⇒ ngưỡng bóng = max(15, 10) = 15),
mọi mức giá bid = ask = 5 (không imbalance, không bóng, không kiệt sức) trừ khi ghi rõ. Giờ bắt đầu 02:00 UTC = 09:00 VN."""
import os
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K               # noqa: E402
import of_signals as OF          # noqa: E402
import setup_corven as SC        # noqa: E402


def uni(l, h, v=5.0):
    return [(k, v, v, 2 * v) for k in range(l, h + 1)]


def setlv(lv, tick, bid=None, ask=None):
    out = []
    for (k, b, a, v) in lv:
        if k == tick:
            b = b if bid is None else float(bid)
            a = a if ask is None else float(ask)
            v = b + a
        out.append((k, b, a, v))
    return out


def world(rows, start='2026-09-01 02:00', mbr=15.0, medd=20.0, base=5.0, times=None):
    """rows: list dict(o,h,l,c[,d][,lv]). Trả (df, feat)."""
    bars = []
    for i, r in enumerate(rows):
        lv = r.get('lv') or uni(r['l'], r['h'])
        bars.append(OF.FpBar(i, r['o'], r['h'], r['l'], r['c'], float(r.get('d', 0)), 0.0, 0.0, lv))
    n = len(bars)
    t = pd.DatetimeIndex(times) if times is not None else pd.date_range(start, periods=n, freq='min')
    raw = pd.DataFrame({'bar_idx': range(n), 'datetime': t, 'open': [b.o * 0.1 for b in bars], 'high': [b.h * 0.1 for b in bars],
                        'low': [b.l * 0.1 for b in bars], 'close': [b.c * 0.1 for b in bars], 'volume': 10,
                        'delta': [b.delta for b in bars]})
    df = K._enrich(raw)
    sno = df['session_no'].to_numpy()
    starts = np.r_[0, np.flatnonzero(np.diff(sno)) + 1]
    ends = np.r_[starts[1:] - 1, n - 1]
    f = SimpleNamespace(bars=bars, H=np.array([b.h for b in bars]), L=np.array([b.l for b in bars]),
                        O=np.array([b.o for b in bars]), C=np.array([b.c for b in bars]), Dl=np.array([b.delta for b in bars]),
                        mbr=np.full(n, mbr), medd=np.full(n, medd), base=np.full(n, base),
                        exh=[OF.exhaustion(b) for b in bars], zones=[OF.stacked_zones(b) for b in bars],
                        sm=df['sm'].to_numpy(), sstart=np.repeat(starts, ends - starts + 1),
                        send=np.repeat(ends, ends - starts + 1), good=np.ones(n, bool))
    return df, f


M0 = SimpleNamespace(fb_bars={}, death={}, eng=SimpleNamespace(ranges=[]))
CP = SC.CP()


def evaluate(c, f, m=M0, cp=CP):
    c.signs = SC.find_signs(c, f, cp)
    SC.eval_order(c, f, cp, m, {}, True)
    return c


# =============================================================== ví dụ 1 — thế A sell
T1, B1 = 41358, 41309          # range 4130,9–4135,8


def ex1_rows(cf_delta=-15, extra=None):
    rows = [dict(o=41335, h=41340, l=41328, c=41333) for _ in range(10)]
    rows.append(dict(o=41325, h=41327, l=41318, c=41322, d=-5))                  # 10 = s (đáy nhịp)
    p = 41322
    for k in range(6):                                                          # 11..16: nhịp lên, Δ âm
        rows.append(dict(o=p, h=p + 7, l=p - 1, c=p + 5, d=-3))
        p += 5
    lv = setlv(uni(41350, 41380), 41375, bid=30)                                # 17 = chọc 4138,0, bóng đỏ 30 ở râu trên
    rows.append(dict(o=41352, h=41380, l=41350, c=41362, d=-10, lv=lv))         # đóng ngoài cạnh trên
    rows.append(dict(o=41362, h=41364, l=41354, c=41356, d=cf_delta))           # 18 = CF (FailBreak) đóng trong, gần cạnh
    rows.append(dict(o=41356, h=41420, l=41355, c=41415, d=40))                 # 19: vọt 4142 ⇒ chạm SL
    rows.append(dict(o=41415, h=41418, l=41410, c=41412))
    if extra:
        extra(rows)
    return rows


def ex1_cand(cf=18):
    inst = SimpleNamespace(top=T1, bottom=B1, fb=18)
    return SC.Cand(cf, 'A', -1, 0, inst, (0, 1, 'A'), 17, 17,
                   [dict(kind='canh', level=T1, tol=7.5, band=(T1 - 7.5, T1 + 7.5), zid=None)], [T1])


def test_ex1_theA_sell_signal_sl_r_and_hits_sl():
    df, f = world(ex1_rows())
    c = evaluate(ex1_cand(), f)
    assert set(c.types) == {'delta', 'bong'}, c.signs
    assert 'ngược giá' in c.signs['delta'][0] and c.signs['delta'][1] == 17
    assert c.gates == [], c.gates
    assert c.entry == 41356 and c.sl == 41383                     # SL 4138,3 = đỉnh 4138,0 + đệm 3 tick
    assert abs(c.r_avail - 47 / 27) < 1e-9 and 1.7 <= c.r_avail < 1.8
    assert abs(c.tp - (41356 - 2 * 27)) < 1e-9                     # TP 2R
    t = SC.sim_one(df, f, SC.to_entry(c))
    assert t['outcome'] == 'SL' and t['exit_idx'] == 19 and t['r'] < -1


# =============================================================== ví dụ 2 — thế B sell, mốc stacked
E2, TOP2 = 41274, 41325         # cạnh dưới 4127,4 vừa phá; range cao 51 tick


def ex2_rows(cf_zone=False):
    rows = [dict(o=41300, h=41305, l=41295, c=41300) for _ in range(10)]
    lv = uni(41268, 41292)
    for k in (41286, 41287, 41288):
        lv = setlv(lv, k, bid=20)                                               # stacked sell 4128,6–4128,8 trong cú phá
    rows.append(dict(o=41290, h=41292, l=41268, c=41270, d=-40, lv=lv))         # 10 = nến đóng ngoài
    rows.append(dict(o=41270, h=41272, l=41255, c=41258, d=-30))                # 11
    rows.append(dict(o=41258, h=41262, l=41250, c=41255, d=-20))                # 12 = đáy cú đẩy (s)
    rows.append(dict(o=41255, h=41270, l=41253, c=41268, d=-30))                # 13 hồi, Δ −30
    rows.append(dict(o=41268, h=41284, l=41266, c=41280, d=-32,
                     lv=setlv(uni(41266, 41284), 41283, bid=25)))               # 14 hồi, Δ −32, bóng đỏ 25
    lv15 = uni(41264, 41281)
    if cf_zone:
        for k in (41270, 41271, 41272):
            lv15 = setlv(lv15, k, bid=20)                                       # vùng sell MỚI giữa thân CF
    rows.append(dict(o=41279, h=41281, l=41264, c=41266, d=-25, lv=lv15))       # 15 = CF
    rows.append(dict(o=41266, h=41268, l=41240, c=41242, d=-30))
    rows.append(dict(o=41242, h=41244, l=41200, c=41205, d=-50))                # chạm TP
    return rows


def ex2_cand(mocs=None, cf=15):
    inst = SimpleNamespace(top=TOP2, bottom=E2, E=E2, rid=0)
    if mocs is None:
        mocs = [dict(kind='stacked', level=41286, tol=7.5, band=(41286 - 7.5, 41288 + 7.5), zid=(10, 41286, 41288))]
    return SC.Cand(cf, 'B', -1, 0, inst, (0, -1, 'B'), 10, max(cf - 2, 11), mocs, [E2])


def test_ex2_theB_sell_stacked_moc_two_signs_tp():
    df, f = world(ex2_rows())
    c = evaluate(ex2_cand(), f)
    assert set(c.types) == {'delta', 'bong'}, c.signs
    assert 'ΣΔ -62/2 nến' in c.signs['delta'][0]
    assert c.gates == [], c.gates
    assert c.sl == 41291 and c.entry == 41266                    # SL 4129,1 = mép xa vùng 4128,8 + 3 tick
    assert abs(c.r_avail - (41266 - (E2 - 51)) / 25) < 1e-9 and c.r_avail >= 1.7
    t = SC.sim_one(df, f, SC.to_entry(c))
    assert t['outcome'] == 'TP' and t['r'] > 1.9


# =============================================================== ví dụ 3 — "lần 2", R 1,3 bị loại
def ex3_world():
    rows = [dict(o=41240, h=41245, l=41235, c=41240) for _ in range(16)]
    rows.append(dict(o=41230, h=41231, l=41222, c=41224, d=-20))                # 16 đóng ngoài cạnh dưới 4123,2
    lv_y = setlv(uni(41208, 41224), 41208, bid=0, ask=3)                        # 17 = LẦN 1: chỉ kiệt sức đáy
    rows.append(dict(o=41224, h=41224, l=41208, c=41218, d=5, lv=lv_y))
    lv = uni(41206, 41230)
    lv = setlv(lv, 41206, bid=0, ask=3)                                         # kiệt sức đáy (Bid 0)
    lv = setlv(lv, 41207, bid=25)                                               # bóng đỏ 25 ở râu dưới = SL phe sell khớp
    rows.append(dict(o=41215, h=41230, l=41206, c=41229, d=15, lv=lv))          # 18 = LẦN 2 (x): quét đáy y, đóng lùi
    rows.append(dict(o=41229, h=41232, l=41225, c=41230))
    return world(rows)


def ex3_cand(cf, ext=41208):
    inst = SimpleNamespace(top=41263, bottom=41232)
    return SC.Cand(cf, 'A2', +1, 0, inst, (0, -1, 'A'), 16, max(16, cf - 4),
                   [dict(kind='cuc_tri', level=ext, tol=7.5, band=(ext - 7.5, ext + 7.5), zid=None)], [ext])


def test_ex3_second_confirmation_trap_plus_exhaustion_but_R_13_rejected():
    df, f = ex3_world()
    first = evaluate(SC.Cand(17, 'A2', +1, 0, SimpleNamespace(top=41263, bottom=41232), (0, -1, 'A'), 16, 16,
                             [dict(kind='cuc_tri', level=41222, tol=7.5, band=(41214.5, 41229.5), zid=None)], [41222]), f)
    assert len(first.types) == 1 and not SC.sign_ok(first, 'main', CP)          # lần 1 chỉ 1 dấu hiệu ⇒ không
    c = evaluate(ex3_cand(18), f)
    assert {'trap', 'kiet_suc'} <= set(c.types) and SC.sign_ok(c, 'main', CP)
    assert c.sl == 41206 - 3 and c.entry == 41229
    assert abs(c.r_avail - 34 / 26) < 1e-9                                      # R tới cạnh trên ≈ 1,3
    assert c.gates == ['r_nho']                                                  # ⇒ bị loại (ngoại lệ mục tiêu không code)


# =============================================================== ca 4 — cách đếm
def test_stacked_used_as_moc_not_counted_but_new_one_is():
    df, f = world(ex2_rows(cf_zone=True))
    c = evaluate(ex2_cand(), f)
    assert 'stacked' in c.types                                                  # vùng mới giữa thân CF, đóng dưới Lo
    zid = (15, 41270, 41272)
    mocs = [dict(kind='stacked', level=41270, tol=7.5, band=(41262.5, 41279.5), zid=zid)]
    c2 = evaluate(ex2_cand(mocs=mocs), f)
    assert 'stacked' not in c2.types                                             # cùng vùng nhưng đang làm mốc ⇒ không đếm


def test_trap_and_exhaustion_same_bar_count_two():
    df, f = ex3_world()
    c = evaluate(ex3_cand(18), f)
    assert c.signs['trap'][1] == c.signs['kiet_suc'][1] == 18
    assert len(c.types) >= 2


def test_delta_strong_plus_divergence_counts_one():
    df, f = world(ex1_rows(cf_delta=-45))                                        # CF Δ −45 ≥ 2 × 20 ⇒ Δ to; nhịp vẫn ngược giá
    c = evaluate(ex1_cand(), f)
    assert 'Δ to' in c.signs['delta'][0]
    ok, _, _ = OF.delta_divergence(f.H, f.L, f.Dl, 17, -1, 15)
    assert ok                                                                    # dạng ngược giá cũng có…
    assert c.types == ('delta', 'bong')                                          # …nhưng chỉ tính 1 loại Δ


# =============================================================== ca 5 — veto kiệt sức chống hướng
def _ex1_with_bottom_exh(low16, low17=None):
    def ex(rows):
        r = rows[16]
        lv = setlv(uni(low16, r['h']), low16, bid=0, ask=3)
        rows[16] = dict(o=r['o'], h=r['h'], l=low16, c=r['c'], d=r['d'], lv=lv)
        if low17 is not None:
            r = rows[17]
            rows[17] = dict(o=r['o'], h=r['h'], l=low17, c=r['c'], d=r['d'], lv=setlv(uni(low17, r['h']), 41375, bid=30))
    return ex


def test_exhaustion_against_direction_vetoes_until_swept():
    df, f = world(ex1_rows(extra=_ex1_with_bottom_exh(41340)))                   # đáy 4134,0 kiệt sức sell, chưa bị quét
    assert f.exh[16][1].hit
    c = evaluate(ex1_cand(), f)
    assert 'v_kiet_suc_chong' in c.gates
    df, f = world(ex1_rows(extra=_ex1_with_bottom_exh(41346, 41345)))            # đáy 4134,6; nến 17 low 4134,5 quét qua
    assert f.exh[16][1].hit
    c = evaluate(ex1_cand(), f)
    assert 'v_kiet_suc_chong' not in c.gates


# =============================================================== ca 6, 7 — R, SL
def geo_world(ref_high, mbr=15.0, cf=19):
    rows = [dict(o=41300, h=41305, l=41295, c=41300) for _ in range(cf - 1)]
    rows.append(dict(o=41340, h=ref_high, l=41338, c=41362))                    # nến đóng ngoài
    rows.append(dict(o=41362, h=41364, l=41354, c=41356, d=-15))                # CF
    rows.append(dict(o=41356, h=41357, l=41350, c=41351))
    return world(rows, mbr=mbr)


def geo_cand(bottom, cf=19, top=41358):
    return SC.Cand(cf, 'A', -1, 0, SimpleNamespace(top=top, bottom=bottom, fb=cf), (0, 1, 'A'), cf - 1, cf - 1,
                   [dict(kind='canh', level=top, tol=7.5, band=(top - 7.5, top + 7.5), zid=None)], [top])


def test_r_169_rejected_170_accepted_tp_2R():
    df, f = geo_world(41377)                                                     # SL = 41377 + 3 = 41380 ⇒ rủi ro 24
    c = evaluate(geo_cand(41356 - 40), f)                                        # 40 / 24 = 1,667 < 1,7
    assert c.risk == 24 and 'r_nho' in c.gates
    c = evaluate(geo_cand(41356 - 41), f)                                        # 41 / 24 = 1,708 ≥ 1,7
    assert 'r_nho' not in c.gates and abs(c.tp - (41356 - 48)) < 1e-9           # TP 2R dù R sẵn < 2
    # biên đúng 1,7: rủi ro 20, mục tiêu 34
    df, f = geo_world(41373)
    c = evaluate(geo_cand(41356 - 34), f)
    assert c.risk == 20 and abs(c.r_avail - 1.7) < 1e-12 and 'r_nho' not in c.gates


def test_sl_floor_cap_buffer_rounding():
    df, f = geo_world(41364, mbr=15.5)                                           # SL thô 41364 + 3,1 = 41367,1 ⇒ rủi ro 11,1 < 1 mbr
    c = evaluate(geo_cand(41200), f)
    assert c.sl == 41372 and c.risk == 16                                        # dời ra 15,5 rồi làm tròn RA XA lên tick ⇒ 16
    df, f = geo_world(41380, mbr=20.0)                                           # đệm = max(3, 0,2 × 20) = 4
    c = evaluate(geo_cand(41200), f)
    assert c.sl == 41384 and c.risk == 28
    df, f = geo_world(41430, mbr=15.0)                                           # rủi ro 77 > 4 mbr = 60 ⇒ bỏ
    c = evaluate(geo_cand(41000), f)
    assert 'tran_sl' in c.gates
    df, f = geo_world(41410, mbr=15.0)                                           # rủi ro 57 ≤ 60 ⇒ giữ
    c = evaluate(geo_cand(41000), f)
    assert 'tran_sl' not in c.gates


def test_cf_rules_body_close_range_delta():
    base = dict(o=41362, h=41364, l=41354, c=41356, d=-15)
    for bad, why in ((dict(c=41360), 'thân 0,2 < 0,4'), (dict(l=41350, c=41358, o=41363), 'đóng cách đáy 0,57 > 0,3'),
                     (dict(d=5), 'Δ ngược dấu'), (dict(d=-9), 'Δ < 0,5 medΔ'), (dict(h=41359, o=41359, l=41354, c=41355), 'biên độ 5 < 0,5 mbr')):
        rows = ex1_rows()
        rows[18] = {**base, **bad}
        df, f = world(rows)
        c = evaluate(ex1_cand(), f)
        assert 'g4a_cf' in c.gates, why


# =============================================================== ca 10 — giờ, đầu phiên, TIME
def test_block_us_open_and_switch():
    # CF (nến 18) mở lúc 12:25 UTC = 19:25 VN (giờ hè Mỹ ⇒ sm 865)
    rows = ex1_rows()
    df, f = world(rows, start='2026-09-01 12:07')
    assert 860 <= f.sm[18] < 930
    c = evaluate(ex1_cand(), f)
    assert c.gates == ['chan_1920']
    tr_on, _, _ = SC.select_and_simulate([c], df, f, CP)
    tr_off, _, _ = SC.select_and_simulate([c], df, f, CP, block_us=False)
    assert len(tr_on) == 0 and len(tr_off) == 1


def test_first_15_bars_of_session_blocked():
    rows = ex1_rows()
    times = list(pd.date_range('2026-09-01 01:00', periods=5, freq='min')) + \
        list(pd.date_range('2026-09-01 02:00', periods=len(rows) - 5, freq='min'))   # khoảng trống 55′ ⇒ phiên mới ở nến 5
    df, f = world(rows, times=times)
    c = evaluate(ex1_cand(), f)
    assert f.sstart[18] == 5 and 'dau_phien' in c.gates                          # nến 18 là nến thứ 14 của phiên


def test_open_trade_closed_TIME_at_session_gap():
    rows = ex1_rows()
    rows[19] = dict(o=41356, h=41358, l=41350, c=41352)                          # không chạm SL/TP
    rows[20] = dict(o=41352, h=41354, l=41348, c=41349)
    rows += [dict(o=41349, h=41351, l=41345, c=41347) for _ in range(5)]
    times = list(pd.date_range('2026-09-01 02:00', periods=22, freq='min')) + \
        list(pd.date_range('2026-09-01 03:00', periods=len(rows) - 22, freq='min'))
    df, f = world(rows, times=times)
    c = evaluate(ex1_cand(), f)
    t = SC.sim_one(df, f, SC.to_entry(c))
    assert t['outcome'] == 'TIME' and t['exit_idx'] == 21 and abs(t['exit_price'] - 41347 * 0.1) < 1e-9


# =============================================================== 4d — chọn lệnh
def test_one_trade_per_instance_and_one_open_position():
    df, f = world(ex1_rows())
    a1 = evaluate(ex1_cand(18), f)
    a1b = evaluate(ex1_cand(18), f)
    a1b.inst = a1.inst                                                           # cùng thế, cùng nến
    other = evaluate(ex1_cand(18), f)
    other.key = (9, 1, 'A')                                                      # thế khác nhưng đang có lệnh mở
    other.inst = SimpleNamespace(top=T1, bottom=B1, fb=18)
    tr, chosen, why = SC.select_and_simulate([a1, a1b, other], df, f, CP)
    assert len(tr) == 1 and chosen[0] is a1
    assert why.get('the_da_co_lenh', 0) + why.get('dang_co_lenh', 0) == 2


def test_modes_C1_and_C3():
    df, f = world(ex1_rows())
    c = evaluate(ex1_cand(), f)
    c.signs = {}                                                                 # không dấu hiệu nào
    assert not SC.sign_ok(c, 'main', CP) and SC.sign_ok(c, 'C1', CP)
    c.signs = {'bong': ('x', 17, 0)}
    assert SC.sign_ok(c, ('C3', 'bong'), CP) and not SC.sign_ok(c, ('C3', 'trap'), CP)
