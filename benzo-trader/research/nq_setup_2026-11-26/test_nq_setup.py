# -*- coding: utf-8 -*-
"""pytest cho nq_setup.py (SPEC-SETUP-NQ mục 5: test tối thiểu)."""
from datetime import datetime, timedelta, timezone

import pytest

import nq_setup as ns


def mk(ohlc, t0=datetime(2026, 10, 1, 14, 0, tzinfo=timezone.utc), deltas=None):
    b = ns.Bars()
    for k, (o, h, l, c) in enumerate(ohlc):
        t = t0 + timedelta(minutes=k)
        b.t.append(t); b.key.append(t.strftime("%Y-%m-%d %H:%M")); b.idx.append(k)
        b.o.append(o); b.h.append(h); b.l.append(l); b.c.append(c)
        b.d.append(deltas[k] if deltas else 0.0); b.v.append(10.0)
    return b


CFG = dict(ns.CFG)


# ---------- mô phỏng lệnh
def test_same_bar_sl_tp_is_sl():
    b = mk([(100, 100, 100, 100), (100, 111, 89, 100)])
    k, px, how = ns.simulate(b, 1, 1, 100, 90, 110, CFG)
    assert (k, px, how) == (1, 90, "SL")


def test_gap_open_past_sl_fills_at_open():
    b = mk([(100, 100, 100, 100), (100, 101, 99, 100), (85, 86, 84, 85)])
    k, px, how = ns.simulate(b, 1, 1, 100, 90, 110, CFG)
    assert (k, px, how) == (2, 85, "SL")


def test_tp_and_sell_side():
    b = mk([(100, 100, 100, 100), (100, 101, 95, 96), (96, 97, 89, 90)])
    assert ns.simulate(b, 1, -1, 100, 105, 90, CFG) == (2, 90, "TP")


def test_close_at_1659_ny():
    # 2026-10-01 là mùa hè: 16:59 NY = 20:59 UTC
    t0 = datetime(2026, 10, 1, 20, 57, tzinfo=timezone.utc)
    b = mk([(100, 100, 100, 100), (100, 101, 99, 100), (100, 102, 99, 101), (101, 101, 100, 100)], t0=t0)
    assert ns.simulate(b, 1, 1, 100, 90, 120, CFG) == (2, 101, "TIME")


# ---------- cấu trúc
def test_structure_close_break_and_pivots():
    # đỉnh pivot ở nến 1 (H 105), đáy pivot nến 3 (L 95); nến 5 đóng 106 > đỉnh gần nhất → tăng; nến 7 đóng 94 < đáy → giảm
    ohlc = [(100, 101, 99, 100), (100, 105, 99, 104), (104, 104, 97, 98), (98, 99, 95, 96), (96, 100, 96, 99),
            (99, 107, 98, 106), (106, 106, 100, 101), (101, 101, 93, 94)]
    m = ns.Machine(mk(ohlc), ns.Sig())
    for i in range(len(ohlc)):
        m._structure(i)
    assert m.ph[:1] == [105] and m.pl[:1] == [95]
    assert m.dir[5] == 1 and m.dir[6] == 1 and m.dir[7] == -1


def test_structure_wick_does_not_break():
    ohlc = [(100, 101, 99, 100), (100, 105, 99, 104), (104, 104, 97, 98), (98, 99, 96, 97), (97, 108, 96, 104)]
    m = ns.Machine(mk(ohlc), ns.Sig())
    for i in range(len(ohlc)):
        m._structure(i)
    assert m.dir[4] != 1      # râu 108 vượt đỉnh 105 nhưng đóng 104 → chưa gãy


# ---------- vùng stacked
def run_zones(ohlc, zone, dirs):
    s = ns.Sig(); s.zones[zone[0]].append(zone[1:])
    m = ns.Machine(mk(ohlc), s)
    m.dir = list(dirs)
    for i in range(len(ohlc)):
        m._zones(i)
    return m.zones[0]


def test_zone_birth_leave_touch_then_expire():
    # vùng buy 100–102 sinh ở nến 0 (thân 99–103 → trong thân), nến 1 Low 103 > hi (rời), nến 3 chạm (Low 101), sau 3 nến hết
    ohlc = [(99, 104, 98, 103), (103, 106, 103, 105), (105, 107, 104, 106), (106, 106, 101, 105), (105, 106, 104, 105),
            (105, 106, 104, 105), (105, 106, 104, 105)]
    z = run_zones(ohlc, (0, 1, 100.0, 102.0), [1] * 7)
    assert z.ok_at == 0 and z.ready_at == 1 and z.touch == 3 and z.dead


def test_zone_dead_when_close_through_far_edge():
    ohlc = [(99, 104, 98, 103), (103, 106, 103, 105), (105, 105, 97, 98)]
    z = run_zones(ohlc, (0, 1, 100.0, 102.0), [1] * 3)
    assert z.dead


def test_zone_in_wick_needs_follow_through():
    # vùng 100–102 nằm ở râu dưới (thân 104–106): nến kế không đóng > 102? có (đóng 107) → đạt ở nến 1
    ohlc = [(104, 107, 99, 106), (106, 108, 105, 107)]
    z = run_zones(ohlc, (0, 1, 100.0, 102.0), [1, 1])
    assert z.ok_at == 1 and not z.dead
    ohlc2 = [(104, 107, 99, 106), (106, 107, 101, 101.5)]
    z2 = run_zones(ohlc2, (0, 1, 100.0, 102.0), [1, 1])
    assert z2.dead


def test_zone_dead_on_structure_flip():
    ohlc = [(99, 104, 98, 103), (103, 106, 103, 105), (105, 107, 104, 106)]
    z = run_zones(ohlc, (0, 1, 100.0, 102.0), [1, 1, -1])
    assert z.dead


def test_zone_too_old():
    ohlc = [(99, 104, 98, 103)] + [(110, 111, 109, 110)] * 33
    z = run_zones(ohlc, (0, 1, 100.0, 102.0), [1] * 34)
    assert z.dead and z.touch < 0


# ---------- tín hiệu
def test_exh_validity_by_wick():
    b = mk([(100, 101, 95, 100), (100, 101, 96, 100), (100, 101, 94.75, 100)])
    m = ns.Machine(b, ns.Sig())
    assert m._exh_valid(0, 1, 1) and not m._exh_valid(0, 2, 1)


def test_delta_threshold():
    d = [10.0] * 20 + [9.0, 10.0]
    b = mk([(100, 101, 99, 100.5)] * 22, deltas=d)
    m = ns.Machine(b, ns.Sig())
    assert not m._delta_ok(20, 1) and m._delta_ok(21, 1) and not m._delta_ok(21, -1)


def test_candle_ok():
    b = mk([(100, 104, 99, 103), (100, 104, 99, 101)])
    m = ns.Machine(b, ns.Sig())
    assert m._candle_ok(0, 1) and not m._candle_ok(1, 1) and not m._candle_ok(0, -1)


def test_session_and_trade_day():
    t = datetime(2026, 11, 6, 23, 30, tzinfo=timezone.utc)     # 18:30 NY → phiên Á của ngày 07/11
    assert ns.session_of(t)[0] == "A" and str(ns.trade_day(t)) == "2026-11-07"
    assert ns.session_of(datetime(2026, 11, 6, 14, 31, tzinfo=timezone.utc))[0] == "U"   # 09:31 NY
    assert ns.session_of(datetime(2026, 11, 6, 14, 29, tzinfo=timezone.utc))[0] == "E"


# ---------- không nhìn trước (dữ liệu thật): cắt dữ liệu ở giữa, các lệnh đã đóng trước điểm cắt phải giống hệt
@pytest.mark.slow
def test_no_lookahead_on_real_data():
    start = datetime(2026, 9, 14, tzinfo=timezone.utc)
    bars, sig = ns.build(start)
    full = ns.Machine(bars, sig); full.run(start, until=datetime(2026, 10, 24, tzinfo=timezone.utc))
    cut = datetime(2026, 10, 8, tzinfo=timezone.utc)
    nb = sum(1 for t in bars.t if t < cut)
    b2 = ns.Bars(**{k: getattr(bars, k)[:nb] for k in ("t", "key", "o", "h", "l", "c", "d", "v", "idx")})
    part = ns.Machine(b2, sig); part.run(start)
    a = [(t.sig, t.kind, t.side, t.entry, t.sl, t.tp, t.exit_i, t.how) for t in full.trades if t.exit_i < nb - 1]
    p = [(t.sig, t.kind, t.side, t.entry, t.sl, t.tp, t.exit_i, t.how) for t in part.trades if t.exit_i < nb - 1]
    assert a and a == p


# ---------- bản 3: Follow trend = nhịp hồi nông của move đang đi
def follow_machine(ohlc, mbr_ticks=20.0, d=1):
    m = ns.Machine(mk(ohlc), ns.Sig())
    m.dir = [d] * len(ohlc)
    m.eng.mbr = mbr_ticks            # mbr = 20 tick = 5 điểm → move tối thiểu 10 điểm
    return m


def up_leg(pb_low=108.0):
    # đáy 100 (nến 1) → đỉnh 120 (nến 5), hồi 2 nến về pb_low, nến 8 là nến tín hiệu
    return [(101, 102, 100.5, 101), (101, 101, 100, 100.5), (100.5, 106, 100.5, 105), (105, 112, 104, 111), (111, 116, 110, 115),
            (115, 120, 114, 119), (119, 119, pb_low + 2, pb_low + 3), (pb_low + 3, pb_low + 4, pb_low, pb_low + 1), (pb_low + 1, 116, pb_low + 1, 115)]


def test_follow_shallow_pullback_ok():
    m = follow_machine(up_leg(112.0))
    c = m._follow(8)
    assert c is not None and c[0] == "Follow trend" and c[1] == 1 and c[2] == 6 and c[3] == 112.0 and c[5] == ("leg", 5)


def test_follow_too_deep():
    m = follow_machine(up_leg(108.0))      # hồi 12 / move 20 = 60 % > 50 %
    assert m._follow(8) is None


def test_follow_move_too_small_or_no_pullback():
    m = follow_machine(up_leg(112.0), mbr_ticks=48.0)   # mbr 12 điểm → cần move ≥ 24
    assert m._follow(8) is None
    m2 = follow_machine(up_leg(112.0))
    assert m2._follow(6) is None                      # chưa có nến hồi nào trước nến tín hiệu


def test_follow_leg_used_once_and_needs_structure():
    m = follow_machine(up_leg(112.0))
    m.used_legs.add(5)
    assert m._follow(8) is None
    m2 = follow_machine(up_leg(112.0), d=-1)
    assert m2._follow(8) is None or m2._follow(8)[1] == -1
