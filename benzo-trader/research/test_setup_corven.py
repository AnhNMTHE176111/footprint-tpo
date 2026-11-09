# -*- coding: utf-8 -*-
"""Test setup_corven.py — phần GĐ0 (bước ①–②). Chạy: python -m pytest benzo-trader/research/test_setup_corven.py -q

Dữ liệu tổng hợp: 120 nến dao động đều trong hộp [B, T] (T − B = 49 tick, biên độ nến ~25 tick ⇒ mbr ≈ 25, cao ≈ 2 mbr,
tol range = 12,5 tick) để RangeEngine nguyên trạng sinh range, rồi nối các kịch bản fail break / phá thật.
Danh sách ca theo plan mục 4 (phần thuộc GĐ0): 8 (ReEntry huỷ thế B, CloseThrough huỷ mốc stacked, tuổi 31 ⇒ hết),
9 (cửa sổ test W=3), 11 (chạy một mạch = chạy từng phần, không nhìn tương lai), cộng 2a/2b/1c/ngoại lệ lần 2."""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import of_signals as OF          # noqa: E402
import setup_corven as SC        # noqa: E402

B0, T0 = 41000, 41049            # cạnh dưới / trên (tick) = 4100,0 / 4104,9


def mk(i, o, h, l, c, levels=None, delta=0.0):
    if levels is None:
        levels = [(k, 1.0, 1.0, 2.0) for k in range(l, h + 1)]   # bid = ask = 1 ⇒ không imbalance, không bóng
    return OF.FpBar(i, o, h, l, c, delta, delta, delta, levels)


def base_bars(n=120):
    cyc = [(B0 + 20, B0 + 25, B0, B0 + 15), (B0 + 15, B0 + 35, B0 + 10, B0 + 30),
           (B0 + 30, T0, B0 + 28, T0 - 8), (T0 - 8, T0 - 3, B0 + 18, B0 + 22)]
    return [mk(i, *cyc[i % 4]) for i in range(n)]


def add(bars, o, h, l, c, levels=None, delta=0.0):
    bars.append(mk(len(bars), o, h, l, c, levels, delta))
    return len(bars) - 1


def run(bars, cp=None):
    return SC.run_step2(bars, None, cp or SC.CP())


def the_range(m):
    r = m.eng.ranges[-1]
    return r


def test_base_range_born():
    m = run(base_bars())
    assert m.eng.ranges, 'phải sinh range'
    r = the_range(m)
    assert r.top == T0 and r.bottom == B0 and r.state == SC.ACTIVE
    assert 20 <= m.mbr[-1] <= 30


# ------------------------------------------------------------------ thế A
def test_A_failbreak_near_edge_passes_2a():
    bars = base_bars()
    add(bars, T0 - 8, T0 + 20, T0 - 10, T0 + 5)          # đóng ngoài cạnh trên
    fb = add(bars, T0 + 5, T0 + 8, T0 - 15, T0 - 6)      # đóng lại trong, cách cạnh 6 tick ≤ 1 mbr
    m = run(bars)
    a = [x for x in m.A if x.fb == fb]
    assert len(a) == 1 and a[0].S == -1 and a[0].E == 1
    assert a[0].passed == [fb] and a[0].fail == ''


def test_A_failbreak_deep_close_rejected_2a():
    bars = base_bars()
    add(bars, T0 - 8, T0 + 20, T0 - 10, T0 + 5)
    fb = add(bars, T0 + 5, T0 + 8, B0 + 8, B0 + 10)      # đóng sâu: cách cạnh 39 tick > 1 mbr
    add(bars, B0 + 10, B0 + 20, B0 + 5, B0 + 12)
    add(bars, B0 + 12, B0 + 22, B0 + 6, B0 + 14)
    m = run(bars)
    a = [x for x in m.A if x.fb == fb][0]
    assert a.passed == [] and a.fail == '2a_xa' and len(a.cands) == 3       # FB + 2 nến sau


def test_A_cf_window_max_two_bars_after_fb():
    bars = base_bars()
    add(bars, T0 - 8, T0 + 20, T0 - 10, T0 + 5)
    fb = add(bars, T0 + 5, T0 + 8, B0 + 8, B0 + 10)      # FB xa
    add(bars, B0 + 10, B0 + 20, B0 + 5, B0 + 12)
    add(bars, B0 + 12, B0 + 22, B0 + 6, B0 + 14)
    late = add(bars, B0 + 14, T0 - 2, B0 + 14, T0 - 5)   # nến thứ 3 sau FB đóng sát cạnh — ngoài cửa sổ
    m = run(bars)
    a = [x for x in m.A if x.fb == fb][0]
    assert late not in a.passed and all(c[0] <= fb + 2 for c in a.cands)


# ------------------------------------------------------------------ thế B
def break_up(bars, levels_push=None):
    """Phá lên: đóng ngoài rồi 3 nến giữ ⇒ BreakConfirmed ở nến thứ 4. Trả (ref, bc)."""
    ref = add(bars, T0 - 8, T0 + 12, T0 - 10, T0 + 8, levels_push)
    add(bars, T0 + 8, T0 + 30, T0 + 6, T0 + 25)
    add(bars, T0 + 25, T0 + 45, T0 + 20, T0 + 40)
    bc = add(bars, T0 + 40, T0 + 60, T0 + 35, T0 + 55)
    return ref, bc


def test_B_break_confirmed_and_edge_retest_passes():
    bars = base_bars()
    ref, bc = break_up(bars)
    add(bars, T0 + 55, T0 + 58, T0 + 30, T0 + 34)
    cf = add(bars, T0 + 34, T0 + 36, T0 + 10, T0 + 15)   # râu chạm dải cạnh ± tol (≤ T0+12,5), đóng cách cạnh 15 ≤ 1 mbr
    m = run(bars)
    b = [x for x in m.B if x.bc == bc]
    assert len(b) == 1 and b[0].D == 1 and b[0].E == T0 and b[0].ref == ref
    assert cf in b[0].passed_edge


def test_B_reentry_kills_instance_2b():
    bars = base_bars()
    ref, bc = break_up(bars)
    re = add(bars, T0 + 55, T0 + 56, T0 - 10, T0 - 5)    # đóng lại TRONG range = ReEntry
    add(bars, T0 - 5, T0 + 14, T0 - 6, T0 + 10)
    m = run(bars)
    b = [x for x in m.B if x.bc == bc][0]
    assert b.end == 'reentry' and b.end_bar == re
    assert all(j < re for j in b.passed_edge)


def test_B_age_31_expires():
    bars = base_bars()
    ref, bc = break_up(bars)
    p = T0 + 55
    while len(bars) - 1 - ref < 30:                       # trôi xa dần lên, không chạm lại cạnh
        p += 3
        add(bars, p, p + 12, p - 8, p + 5)
    last_ok = len(bars) - 1
    late = add(bars, p, p + 2, T0 + 5, T0 + 14)          # tuổi 31: chạm cạnh nhưng thế đã hết
    m = run(bars)
    b = [x for x in m.B if x.bc == bc][0]
    assert last_ok - ref == 30
    assert b.end == 'het_tuoi' and b.end_bar == late and late not in b.passed_edge


def test_B_window_W3_touch_4th_bar_back_not_counted():
    bars = base_bars()
    ref, bc = break_up(bars)
    k = add(bars, T0 + 55, T0 + 56, T0 + 8, T0 + 20)     # chạm dải cạnh (low ≤ T0+12,5)
    a1 = add(bars, T0 + 20, T0 + 30, T0 + 14, T0 + 22)   # không chạm, đóng gần (22 ≤ 25)
    a2 = add(bars, T0 + 22, T0 + 30, T0 + 15, T0 + 21)
    a3 = add(bars, T0 + 21, T0 + 30, T0 + 16, T0 + 20)   # = nến thứ 4 tính từ k ⇒ cửa sổ 3 nến không còn chứa k
    m = run(bars)
    b = [x for x in m.B if x.bc == bc][0]
    assert {k, a1, a2} <= set(b.passed_edge) and a3 not in b.passed_edge
    m4 = run(bars, SC.CP(win_b=4))
    b4 = [x for x in m4.B if x.bc == bc][0]
    assert a3 in b4.passed_edge


def push_levels(lo, hi, z0):
    """Mức cho nến đẩy lên có vùng stacked BUY 3 mức z0..z0+2 (ask 10 vs bid 1) giữa thân."""
    lv = []
    for k in range(lo, hi + 1):
        a = 10.0 if z0 <= k <= z0 + 2 else 1.0
        lv.append((k, 1.0, a, 1.0 + a))
    return lv


def test_B_stacked_moc_untouched_then_closethrough_kills():
    bars = base_bars()
    ref = add(bars, T0 - 8, T0 + 12, T0 - 10, T0 + 8)
    z = add(bars, T0 + 8, T0 + 40, T0 + 6, T0 + 38, push_levels(T0 + 6, T0 + 40, T0 + 20))   # vùng buy 4106,9–4107,1
    add(bars, T0 + 38, T0 + 60, T0 + 36, T0 + 58)
    bc = add(bars, T0 + 58, T0 + 75, T0 + 55, T0 + 70)
    assert any(zz.side == 1 and zz.position == OF.POS_BODY for zz in OF.stacked_zones(bars[z]))
    add(bars, T0 + 70, T0 + 72, T0 + 45, T0 + 50)
    t = add(bars, T0 + 50, T0 + 52, T0 + 28, T0 + 33)    # râu chạm vùng ± tol lần đầu ⇒ mốc stacked hợp lệ
    ct = add(bars, T0 + 33, T0 + 35, T0 + 15, T0 + 17)   # đóng dưới mép dưới vùng (T0+20) ⇒ CloseThrough
    after = add(bars, T0 + 17, T0 + 26, T0 + 16, T0 + 24)
    m = run(bars)
    b = [x for x in m.B if x.bc == bc][0]
    zb = [p for p in b.passed_zone if p[1] == z]
    assert any(p[0] == t for p in zb)
    assert not any(p[0] in (ct, after) for p in zb)
    assert b.zone_ct >= 1


def test_B_stacked_moc_touched_before_window_rejected():
    bars = base_bars()
    ref = add(bars, T0 - 8, T0 + 12, T0 - 10, T0 + 8)
    z = add(bars, T0 + 8, T0 + 40, T0 + 6, T0 + 38, push_levels(T0 + 6, T0 + 40, T0 + 20))
    add(bars, T0 + 38, T0 + 39, T0 + 21, T0 + 30)        # chạm ĐÚNG vùng ngay (lần chạm đầu)
    bc = add(bars, T0 + 30, T0 + 60, T0 + 30, T0 + 58)   # nến thứ 3 sau nến đóng ngoài ⇒ BreakConfirmed
    add(bars, T0 + 58, T0 + 75, T0 + 55, T0 + 70)
    add(bars, T0 + 70, T0 + 85, T0 + 66, T0 + 80)
    add(bars, T0 + 80, T0 + 82, T0 + 60, T0 + 65)
    t = add(bars, T0 + 65, T0 + 66, T0 + 30, T0 + 36)    # chạm lại vùng ± tol — nhưng đã bị chạm trước ⇒ vứt
    m = run(bars)
    bs = [x for x in m.B if x.bc == bc]
    assert bs, 'phải có thế B'
    assert not any(p[1] == z and p[0] == t for p in bs[0].passed_zone)


def test_B_1c_structure_break_suspends_until_new_extreme():
    bars = base_bars()
    ref, bc = break_up(bars)
    add(bars, T0 + 55, T0 + 70, T0 + 50, T0 + 65)
    piv = add(bars, T0 + 65, T0 + 80, T0 + 60, T0 + 62)  # đỉnh
    add(bars, T0 + 62, T0 + 66, T0 + 40, T0 + 44)        # xác nhận pivot đáy? (đáy thấp hơn) — tạo pivot đáy ở nến sau
    pl = add(bars, T0 + 44, T0 + 50, T0 + 30, T0 + 48)   # đáy nhịp (pivot đáy khi nến sau có low ≥)
    add(bars, T0 + 48, T0 + 60, T0 + 40, T0 + 58)        # xác nhận pivot đáy tại pl
    brk = add(bars, T0 + 58, T0 + 59, T0 + 20, T0 + 25)  # ĐÓNG dưới pivot đáy (T0+30) ⇒ cấu trúc gãy, thế B tạm huỷ
    m = run(bars)
    b = [x for x in m.B if x.bc == bc][0]
    assert b.n_suspend == 1 and b.broken_at == brk and b.suspended
    assert brk not in b.passed_edge
    # cú đẩy mới lập đỉnh mới ⇒ sống lại
    bars2 = list(bars)
    add(bars2, T0 + 25, T0 + 100, T0 + 24, T0 + 95)
    m2 = run(bars2)
    b2 = [x for x in m2.B if x.bc == bc][0]
    assert not b2.suspended


def test_B_exhausted_range_flag():
    """BreakConfirmed làm range DEAD ngay (hết lượt ReEntry) ⇒ mặc định KHÔNG lập thế B (chờ Fable), có đếm."""
    cp = SC.CP()
    assert cp.b_include_exhausted is False


# ------------------------------------------------------------------ ngoại lệ "xác nhận lần 2"
def test_A_exception_second_confirmation_candidate():
    bars = base_bars()
    add(bars, B0 + 22, B0 + 23, B0 - 20, B0 - 15)        # đóng ngoài cạnh dưới
    add(bars, B0 - 15, B0 - 10, B0 - 25, B0 - 20)        # cực trị cú thủng = B0 − 25
    x = add(bars, B0 - 20, B0 - 9, B0 - 27, B0 - 10)     # râu quét qua cực trị 2 tick, đóng cao hơn 15 ≥ tol 12,5, vẫn ngoài range
    m = run(bars)
    e = [q for q in m.EXC if q.bar == x]
    assert len(e) == 1 and e[0].p == -1 and e[0].ext == B0 - 25
    # chỉ 1 lần mỗi cú thủng
    bars.append(mk(len(bars), B0 - 10, B0 - 9, B0 - 30, B0 - 11))
    m2 = run(bars)
    assert len([q for q in m2.EXC if q.breach_start == e[0].breach_start]) == 1


# ------------------------------------------------------------------ không nhìn tương lai
def test_streaming_equals_prefix_run():
    """Chạy một mạch rồi cắt = chạy trên phần đầu: mọi thế đã KẾT THÚC trước chỗ cắt phải giống hệt."""
    rng = np.random.default_rng(7)
    bars = base_bars()
    p = T0 - 20
    for _ in range(600):
        o = p
        p = int(p + rng.integers(-12, 13))
        h = max(o, p) + int(rng.integers(0, 10))
        l = min(o, p) - int(rng.integers(0, 10))
        add(bars, o, h, l, p)
    full = run(bars)
    cut = 500
    part = run(bars[:cut])

    def sigA(m):
        return [(a.fb, a.rid, tuple(a.passed)) for a in m.A if a.fb + 3 < cut]

    def sigB(m):
        return [(b.bc, b.rid, tuple(b.passed_edge), tuple(sorted(b.passed_zone)), b.end) for b in m.B
                if b.alive is False and b.end != 'het_file' and b.end_bar < cut]

    assert sigA(full) == sigA(part)
    assert [x for x in sigB(full) if x[0] < cut - 40] == [x for x in sigB(part) if x[0] < cut - 40]
    assert len(full.A) > 0 and len(full.B) > 0
