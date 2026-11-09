# -*- coding: utf-8 -*-
"""Test of_signals.py. Chạy: python -m pytest benzo-trader/research/test_of_signals.py -q

Phần PORT lặp lại các ca của quantower-orderflow-indicator/tests (SI-1…SI-8, E1…E14) để chắc bản Python giữ đúng nghĩa;
phần MỚI (nền_ô, bóng, delta, trap) theo plan BENZO-CORVEN mục 1.③. Đối chiếu 100 % trên dữ liệu thật: test cuối
(gọi parity_of_signals — cần dotnet + file 90d, tự bỏ qua nếu thiếu)."""
import math
import os
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import of_signals as OF  # noqa: E402

T = 0.1


def near(a, b):
    return abs(a - b) < 1e-6


def D(ask, bid, pct=250, run=3, mv=1):
    return OF.detect_stacked(100.0, T, ask, bid, pct, run, mv)


# ============================================================ PORT: stacked
def test_si1_pure_buy_edge_250():
    z = D([0, 10, 10, 10, 1], [4, 4, 4, 9, 9])
    assert len(z) == 1 and z[0].side == 1
    assert near(z[0].lo, 100.1) and near(z[0].hi, 100.3) and z[0].levels == 3
    assert near(z[0].min_ratio, 2.5) and near(z[0].dom_volume, 30) and near(z[0].opp_volume, 12)


def test_si2_ratio_threshold():
    assert D([0, 9.9, 10, 10], [4, 4, 4, 0]) == []
    a, b = [0, 11, 11, 11], [4, 4, 4, 0]
    assert len(D(a, b, 250)) == 1 and D(a, b, 300) == []


def test_si3_one_vs_zero_and_minvol():
    zeros = [0, 0, 0, 0]
    z1 = D([0, 1, 1, 1], zeros, mv=1)
    assert len(z1) == 1 and math.isinf(z1[0].min_ratio)
    assert D([0, 1, 1, 1], zeros, mv=5) == []
    assert len(D([0, 5, 5, 5], zeros, mv=5)) == 1
    assert D([0, 5, 4, 5], zeros, mv=5) == []
    assert D(zeros, zeros, mv=0) == []


def test_si4_broken_chain():
    a, b = [0, 10, 10, 0, 10, 10, 10], [2] * 7
    z3 = D(a, b, run=3)
    assert len(z3) == 1 and near(z3[0].lo, 100.4) and near(z3[0].hi, 100.6)
    assert len(D(a, b, run=2)) == 2


def test_si5_pure_sell():
    z = D([0, 4, 4, 4], [10, 10, 10, 0])
    assert len(z) == 1 and z[0].side == -1 and near(z[0].lo, 100.0) and near(z[0].hi, 100.2) and near(z[0].min_ratio, 2.5)
    assert D([0, 4, 4, 4], [10, 10, 10, 0], pct=300) == []


def test_si6_both_sides_diagonal_only():
    z = D([0, 1, 1, 1, 10, 10, 10], [10, 10, 10, 1, 1, 1, 0])
    assert any(q.side == 1 and near(q.lo, 100.4) and near(q.hi, 100.6) for q in z)
    assert any(q.side == -1 and near(q.lo, 100.0) and near(q.hi, 100.2) for q in z)
    assert not any(q.side == 1 for q in D([0, 10, 10, 10], [10, 1, 1, 1]))
    # thứ tự trả về như C#: buy trước, sell sau
    assert [q.side for q in z] == [1, -1]


def test_si7_position_weak():
    assert OF.locate(100.1, 100.3, 100.0, 100.5) == OF.POS_BODY
    assert OF.locate(100.6, 100.8, 100.0, 100.5) == OF.POS_UPPER
    assert OF.locate(99.6, 99.8, 100.5, 100.0) == OF.POS_LOWER
    z = OF.SiZone(1, 0, 0, 100.6, 100.8, 3, 1, 0, 0); OF.classify(z, 100.0, 100.5); assert z.weak
    z = OF.SiZone(-1, 0, 0, 100.6, 100.8, 3, 1, 0, 0); OF.classify(z, 100.0, 100.5); assert not z.weak
    z = OF.SiZone(-1, 0, 0, 99.6, 99.8, 3, 1, 0, 0); OF.classify(z, 100.5, 100.0); assert z.weak
    z = OF.SiZone(1, 0, 0, 100.1, 100.3, 3, 1, 0, 0); OF.classify(z, 100.0, 100.5); assert not z.weak and z.position == OF.POS_BODY


def test_si8_end_rules_and_follow():
    M, C = OF.MODE_TOUCH, OF.MODE_CLOSE
    ce = OF.check_end
    assert ce(1, 100.1, 100.3, 100.6, 100.35, 100.5, M) == OF.END_ACTIVE
    assert ce(1, 100.1, 100.3, 100.6, 100.3, 100.5, M) == OF.END_TOUCHED
    assert ce(1, 100.1, 100.3, 100.6, 99.9, 100.0, M) == OF.END_CLOSED
    assert ce(1, 100.1, 100.3, 100.6, 100.2, 100.5, C) == OF.END_ACTIVE
    assert ce(1, 100.1, 100.3, 100.6, 99.9, 100.1, C) == OF.END_ACTIVE
    assert ce(1, 100.1, 100.3, 100.6, 99.9, 100.0, C) == OF.END_CLOSED
    assert ce(-1, 100.1, 100.3, 100.05, 99.8, 99.9, M) == OF.END_ACTIVE
    assert ce(-1, 100.1, 100.3, 100.1, 99.8, 99.9, M) == OF.END_TOUCHED
    assert ce(-1, 100.1, 100.3, 100.6, 99.8, 100.4, C) == OF.END_CLOSED
    assert ce(1, 100.1, 100.3, 100.0, 99.5, 99.6, M) == OF.END_CLOSED
    after = [(100.8, 100.5, 100.7), (100.9, 100.6, 100.8), (100.9, 100.4, 100.5), (100.6, 100.25, 100.4), (100.5, 99.8, 99.9)]
    assert OF.follow(1, 100.1, 100.3, after, M, 0) == (4, OF.END_TOUCHED)
    assert OF.follow(1, 100.1, 100.3, after, C, 0) == (5, OF.END_CLOSED)
    assert OF.follow(1, 100.1, 100.3, after, M, 2) == (2, OF.END_EXPIRED)
    assert OF.follow(1, 100.1, 100.3, after[:3], M, 0) == (-1, OF.END_ACTIVE)


# ============================================================ PORT: kiệt sức
def Lv(*xs):
    return [(t, float(b), float(a), float(b + a)) for (t, b, a) in xs]


S0 = OF.ExhSettings()


def top(o, h, l, c, lv, s=S0):
    return OF.detect_exhaustion(True, o, h, l, c, lv, s)


def bot(o, h, l, c, lv, s=S0):
    return OF.detect_exhaustion(False, o, h, l, c, lv, s)


def test_e1_e2_e3_top_ask_bottom_bid():
    lv = Lv((100, 5, 3), (101, 8, 9), (102, 10, 12), (103, 9, 8), (104, 4, 6), (105, 3, 2), (106, 7, 0))
    r = top(101, 106, 100, 103, lv)
    assert r.hit and r.kind == OF.EXH_SMALL and r.top and r.tick == 106 and r.extreme_vol == 0
    assert top(100, 103, 100, 101, Lv((100, 5, 5), (101, 5, 5), (102, 5, 5), (103, 60, 0))).hit
    assert not top(100, 103, 100, 101, Lv((100, 5, 5), (101, 5, 5), (102, 5, 5), (103, 0, 20))).hit
    r = bot(103, 103, 100, 102, Lv((100, 0, 40), (101, 6, 6), (102, 6, 6), (103, 6, 6)))
    assert r.hit and not r.top and r.tick == 100 and r.kind == OF.EXH_SMALL
    assert not bot(103, 103, 100, 102, Lv((100, 20, 0), (101, 6, 6), (102, 6, 6), (103, 6, 6))).hit


def test_e4_e5_e6_fade():
    lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 9), (105, 6, 5), (106, 6, 2))
    r = top(101, 106, 100, 103, lv)
    assert r.kind == OF.EXH_FADE and r.seq == (9.0, 5.0, 2.0)
    lv5 = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 5), (105, 6, 5), (106, 6, 2))
    assert not top(101, 106, 100, 103, lv5).hit
    lv6 = Lv((100, 20, 20), (101, 20, 20), (102, 20, 20), (103, 20, 20), (104, 10, 40), (105, 10, 25), (106, 10, 15))
    assert not top(101, 106, 100, 103, lv6).hit


def test_e7_e8_wick_required():
    lv = Lv((100, 5, 5), (101, 5, 5), (102, 5, 5), (103, 4, 0))
    assert not top(100, 103, 100, 103, lv).hit
    assert not bot(103, 103, 100, 100, Lv((100, 0, 4), (101, 5, 5), (102, 5, 5), (103, 5, 5))).hit
    assert top(100, 103, 100, 103, lv, OF.ExhSettings(require_wick=False)).hit
    lv8 = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 9), (105, 6, 5), (106, 6, 2))
    assert not top(101, 106, 100, 104, lv8).hit
    assert top(101, 106, 100, 104, lv8, OF.ExhSettings(fade_levels=2)).kind == OF.EXH_FADE


def test_e9_e10_e11_edge_cases():
    one = Lv((100, 0, 0))
    assert not top(100, 100, 100, 100, one).hit and not bot(100, 100, 100, 100, one).hit
    assert not top(100, 102, 100, 101, []).hit
    assert not OF.detect_exhaustion(True, 100, 102, 100, 101, Lv((100, 1, 1), (102, 0, 0)), None).hit
    heavy = Lv((100, 60, 60), (101, 60, 60), (102, 60, 60), (103, 60, 60), (104, 40, 5))
    assert top(101, 104, 100, 102, heavy).kind == OF.EXH_SMALL
    thin = Lv((100, 2, 2), (101, 2, 2), (102, 2, 2), (103, 2, 2), (104, 3, 1))
    assert not top(101, 104, 100, 102, thin).hit
    s0 = OF.ExhSettings(small_rel=0, fade_levels=0)
    assert not top(101, 104, 100, 102, heavy, s0).hit
    assert top(101, 104, 100, 102, Lv((100, 60, 60), (101, 60, 60), (102, 60, 60), (103, 60, 60), (104, 40, 0)), s0).hit
    gap = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 9), (106, 6, 3))
    assert not top(101, 106, 100, 103, gap).hit
    gap2 = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (105, 6, 3), (106, 6, 0))
    assert top(101, 106, 100, 103, gap2).kind == OF.EXH_SMALL


def test_e12_e13_e14_both_and_sweep():
    lv = Lv((100, 0, 3), (101, 8, 8), (102, 9, 9), (103, 8, 8), (104, 3, 0))
    assert top(102, 104, 100, 102, lv).hit and bot(102, 104, 100, 102, lv).hit
    sw = OF.is_swept
    assert not sw(True, 106, 106, 100, 1) and sw(True, 106, 107, 100, 1) and sw(True, 106, 106, 100, 0)
    assert not sw(True, 106, 107, 100, 2)
    assert not sw(False, 100, 110, 100, 1) and sw(False, 100, 110, 99, 1)
    assert not sw(True, 106, 105, 90, 1)
    highs = [105, 106, 104, 107, 103]
    killed = next(i for i, hh in enumerate(highs) if sw(True, 106, hh, 90, 1))
    assert killed == 3


# ============================================================ tiện ích nến
def bar(o, h, l, c, levels, delta=0.0, mx=None, mn=None, idx=0):
    return OF.FpBar(idx, o, h, l, c, delta, delta if mx is None else mx, delta if mn is None else mn, levels)


def test_ladder_and_stacked_zones_classified():
    b = bar(100, 104, 100, 104, Lv((100, 4, 0), (101, 4, 10), (102, 4, 10), (103, 0, 10), (104, 9, 1)))
    ask, bid = OF.ladder(b)
    assert ask == [0, 10, 10, 10, 1] and bid == [4, 4, 4, 0, 9]
    zs = OF.stacked_zones(b)
    assert len(zs) == 1 and zs[0].position == OF.POS_BODY and not zs[0].weak


def test_price_x10_same_zone_indices():
    """Nhân giá ×10 với tick ×10 ⇒ cùng chỉ số mức, cùng vị trí (plan test 11, phần dấu hiệu)."""
    ask, bid = [0, 10, 10, 10, 1], [4, 4, 4, 9, 9]
    a = OF.detect_stacked(100.0, 0.1, ask, bid, 250, 3, 1)
    b = OF.detect_stacked(1000.0, 1.0, ask, bid, 250, 3, 1)
    assert [(z.lo_idx, z.hi_idx, z.side) for z in a] == [(z.lo_idx, z.hi_idx, z.side) for z in b]
    assert near(a[0].lo * 10, b[0].lo) and near(a[0].hi * 10, b[0].hi)


# ============================================================ MỚI: nền_ô + bóng
def test_cell_value_median_top3_sidevol():
    b = bar(100, 104, 100, 102, Lv((100, 1, 20), (101, 7, 2), (102, 3, 3), (103, 0, 15), (104, 5, 0)))
    # side-volume = 20, 7, 3, 15, 5 → top-3 = 20, 15, 7 → trung vị 15
    assert OF.cell_value(b) == 15
    assert OF.cell_value(bar(100, 101, 100, 101, Lv((100, 0, 4)))) == 4
    assert OF.cell_value(bar(100, 101, 100, 101, [(100, 0.0, 0.0, 3.0)])) is None


def test_cell_baseline_rolling_before_bar():
    cb = OF.CellBaseline(window=3)
    vals = [10, 20, 30, 40]
    for v in vals[:3]:
        cb.push(bar(100, 101, 100, 101, Lv((100, 0, v))))
    assert cb.ready() and cb.value() == 20
    cb.push(bar(100, 101, 100, 101, Lv((100, 0, 40))))     # 10 rơi khỏi cửa sổ
    assert cb.value() == 30
    cb.push(bar(100, 101, 100, 101, [(100, 0.0, 0.0, 5.0)]))   # nến không có ô bid/ask → không nạp
    assert cb.value() == 30 and len(cb.q) == 3


def test_bubbles_threshold_3x_and_10_contracts():
    lv = Lv((100, 30, 2), (101, 9, 18), (102, 2, 12), (103, 1, 9))
    b = bar(101, 103, 100, 102, lv)
    # nền 4 → ngưỡng max(12, 10) = 12
    assert OF.bubbles(b, +1, 4.0) == [(101, 18.0), (102, 12.0)]
    assert OF.bubbles(b, -1, 4.0) == [(100, 30.0)]
    # nền 2 → 3× = 6 nhưng sàn 10 hợp đồng giữ ngưỡng 10 ⇒ ô ask 9 KHÔNG là bóng
    assert (103, 9.0) not in OF.bubbles(b, +1, 2.0)
    assert OF.bubbles(b, +1, 4.0, mult=4) == [(101, 18.0)]


def test_bubble_in_place_half_or_band():
    b = bar(100, 110, 100, 108, [])
    assert OF.bubble_in_place(b, +1, 104)           # buy: ô ≤ trung điểm 105
    assert not OF.bubble_in_place(b, +1, 108)
    assert OF.bubble_in_place(b, +1, 108, band=(107, 109))
    assert OF.bubble_in_place(b, -1, 106) and not OF.bubble_in_place(b, -1, 102)


# ============================================================ MỚI: delta
def test_delta_strong():
    assert OF.delta_strong(bar(0, 1, 0, 1, [], delta=40), +1, 20)
    assert not OF.delta_strong(bar(0, 1, 0, 1, [], delta=39), +1, 20)
    assert not OF.delta_strong(bar(0, 1, 0, 1, [], delta=40), -1, 20)
    assert OF.delta_strong(bar(0, 1, 0, 1, [], delta=-60), -1, 20, mult=3)
    # 'thẳng': buy cần delta ≥ 0,8 × max_delta
    assert not OF.delta_strong(bar(0, 1, 0, 1, [], delta=40, mx=60), +1, 20)
    assert OF.delta_strong(bar(0, 1, 0, 1, [], delta=48, mx=60), +1, 20)
    assert not OF.delta_strong(bar(0, 1, 0, 1, [], delta=-40, mn=-60), -1, 20)
    assert not OF.delta_strong(bar(0, 1, 0, 1, [], delta=40), +1, 0)


def test_delta_divergence_example2_shape():
    # sell: nến đáy (s) rồi 2 nến hồi lên Δ −30 / −32 (ví dụ 2), biên độ 18 tick ≥ 1 mbr (15)
    H = [120, 112, 118, 125]
    L = [110, 107, 111, 116]
    Dl = [-50, -80, -30, -32]
    ok, s, sd = OF.delta_divergence(H, L, Dl, 3, -1, 15)
    assert ok and s == 1 and sd == -62
    # tổng Δ dương ⇒ không phải ngược giá
    assert not OF.delta_divergence(H, L, [-50, -80, 30, 5], 3, -1, 15)[0]
    # biên độ < 1 mbr ⇒ không
    assert not OF.delta_divergence(H, L, Dl, 3, -1, 19)[0]
    # nến neo không phải cực trị nhịp ⇒ không
    assert not OF.delta_divergence([120, 112, 130, 125], L, Dl, 3, -1, 15)[0]


def test_delta_divergence_buy_mirror_and_length():
    H = [130, 135, 131, 126]
    L = [120, 127, 122, 115]
    ok, s, sd = OF.delta_divergence(H, L, [10, 40, 25, 20], 3, +1, 15)
    assert ok and s == 1 and sd == 45                # giá xuống, ΣΔ ≥ 0
    assert not OF.delta_divergence(H, L, [10, 40, -25, -20], 3, +1, 15)[0]
    # x quá sớm (không đủ 2 nến) ⇒ không
    assert not OF.delta_divergence(H, L, [0, 0, 0, 0], 1, +1, 1)[0]


# ============================================================ MỚI: trap
def test_trap_sell_sweep_close_back_and_green_bubble_in_wick():
    # mốc 105; nến quét lên 108, đóng 103 (dưới mốc); râu trên 105..108 có ask 30 ≥ 3 × nền 6
    lv = Lv((101, 5, 5), (102, 5, 5), (103, 6, 4), (104, 4, 4), (105, 3, 5), (106, 2, 30), (107, 1, 6), (108, 0, 2))
    b = bar(104, 108, 101, 103, lv)
    ok, k, v = OF.trap(b, -1, 105, 6.0)
    assert ok and k == 106 and v == 30
    assert not OF.trap(b, -1, 105, 11.0)[0]                       # 30 < 3 × 11
    assert not OF.trap(bar(104, 105, 101, 103, lv), -1, 105, 6.0)[0]  # không quét qua mốc ≥ 1 tick
    assert not OF.trap(bar(104, 108, 101, 106, lv), -1, 105, 6.0)[0]  # đóng trên mốc
    # ô to nằm trong THÂN (không phải râu) ⇒ không tính
    lv2 = Lv((101, 5, 5), (102, 5, 30), (103, 6, 4), (106, 2, 2), (107, 1, 1), (108, 0, 1))
    assert not OF.trap(bar(102, 108, 101, 104, lv2), -1, 105, 6.0)[0]


def test_trap_min_contracts_floor_q10():
    lv = Lv((101, 5, 5), (102, 5, 5), (103, 6, 4), (104, 4, 4), (105, 3, 5), (106, 2, 8), (107, 1, 3), (108, 0, 2))
    b = bar(104, 108, 101, 103, lv)
    assert OF.trap(b, -1, 105, 2.0)[0]                                  # 8 ≥ 3 × 2, không sàn
    assert not OF.trap(b, -1, 105, 2.0, min_contracts=10)[0]            # Q10: sàn 10 hợp đồng


def test_trap_buy_and_same_bar_exhaustion_counts_separately():
    # buy: mốc 105, quét xuống 101, đóng 107; râu dưới có bid 40; đáy bid = 0 ⇒ cũng là kiệt sức đáy
    lv = Lv((101, 0, 3), (102, 40, 2), (103, 6, 6), (104, 8, 8), (105, 9, 9), (106, 8, 8), (107, 8, 8), (108, 5, 6))
    b = bar(106, 108, 101, 107, lv)
    ok, k, v = OF.trap(b, +1, 105, 8.0)
    assert ok and k == 102 and v == 40
    t, bo = OF.exhaustion(b)
    assert bo.hit                                 # trap + kiệt sức trên CÙNG nến — plan: là 2 dấu hiệu khác loại


# ============================================================ đối chiếu C# trên dữ liệu thật
D90 = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'data-export', 'data-footprint',
                   'fp_GCZ26_XCEC_Time_20260723-20261021_90d.csv')


@pytest.mark.skipif(not (os.path.exists(D90) and shutil.which('dotnet')), reason='thiếu file 90d hoặc dotnet')
def test_parity_with_csharp_on_train():
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'parity_of_signals.py')], env=env, capture_output=True,
                       text=True, encoding='utf-8', timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert 'KHỚP 100 %' in r.stdout
