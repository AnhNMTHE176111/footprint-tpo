# -*- coding: utf-8 -*-
"""Test follow_combo.py (plans/BENZO-FOLLOW-COMBO-plan.md mục 7, ca 1–10).
Chạy: python -m pytest benzo-trader/research/test_follow_combo.py -q

Dữ liệu tổng hợp dựng tay theo tick (0,1). Mặc định: mbr = 15 tick, medΔ = 20, nền_ô = 5 (⇒ ngưỡng ô lớn = max(15, 10) = 15),
mọi mức giá bid = ask = 5 (không imbalance, không ô lớn, không kiệt sức) trừ khi ghi rõ. Sự kiện range bơm tay (không chạy
RangeEngine) để cô lập máy Follow. Giờ bắt đầu 02:00 UTC = 09:00 VN (không dính chặn 19:20–20:30)."""
import os
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K               # noqa: E402
import of_signals as OF          # noqa: E402
import setup_corven as SC        # noqa: E402
import follow_combo as FC        # noqa: E402

TOP, BOT, TOL = 41310, 41270, 7.5      # range tới 4131,0 (ảnh gốc: cạnh trên ≈ 4131)
REF = 20


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


def world(rows, mbr=15.0, medd=20.0, base=5.0):
    bars = []
    for i, r in enumerate(rows):
        lv = r.get('lv') or uni(r['l'], r['h'])
        bars.append(OF.FpBar(i, r['o'], r['h'], r['l'], r['c'], float(r.get('d', 0)), 0.0, 0.0, lv))
    n = len(bars)
    t = pd.date_range('2026-09-01 02:00', periods=n, freq='min')
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


def ev(kind, side, top=TOP, bottom=BOT, rid=0):
    return SimpleNamespace(kind=kind, side=side, top=top, bottom=bottom, rid=rid)


def run(rows, events=None, fp=None, **kw):
    """events: {bar: [ev]}; mặc định CloseOutside lên tại REF."""
    df, f = world(rows, **kw)
    events = {REF: [ev('CloseOutside', +1)]} if events is None else events
    info = {(i, e.rid): dict(tol=TOL, exhausted=False) for i, es in events.items() for e in es}
    m = FC.FollowMachine(f, fp or FC.FP())
    for i in range(len(rows)):
        m.on_bar(i, events.get(i, []), info)
    return df, f, m


# --------------------------------------------------------------- ca ảnh gốc (mục 0)
def pad():
    return [dict(o=41290, h=41300, l=41282, c=41292) for _ in range(REF)]


def photo_rows(pb_bid_tick=41321, cf=None, tail=True, x_lv=None, cf_extra=None):
    rows = pad()
    rows.append(dict(o=41300, h=41332, l=41298, c=41325, d=20, lv=x_lv))                    # 20 = ref = x, đóng ngoài cạnh 4131
    lv = uni(41313, 41325)
    if pb_bid_tick is not None:
        lv = setlv(lv, pb_bid_tick, bid=30)                                                  # "chấm đỏ" Bid lớn ở nến hồi
    rows.append(dict(o=41324, h=41325, l=41313, c=41315, d=-10, lv=lv))                      # 21 = nến hồi đỏ, 1 nến
    c = dict(o=41315, h=41323, l=41313, c=41322, d=26)                                       # 22 = CF Δ +26, đóng 4132,2
    if cf:
        c.update(cf)
    clv = setlv(uni(c['l'], c['h']), 41314, ask=30)                                          # "chấm xanh" Ask lớn nửa dưới CF
    c['lv'] = clv
    if cf_extra:
        cf_extra(c)
    rows.append(c)
    if tail:
        rows.append(dict(o=41322, h=41330, l=41320, c=41328, d=9))                           # 23: +9 (chưa vượt đỉnh x)
        rows.append(dict(o=41328, h=41356, l=41326, c=41354, d=9))                           # 24: +9 chạm TP 4135,2
        for _ in range(6):
            rows.append(dict(o=41354, h=41358, l=41350, c=41355))
    return rows


def test_1_photo_case_f0_t_bc_and_order():
    df, f, m = run(photo_rows())
    assert len(m.rows) == 1
    r = m.rows[0]
    assert (r['idx_ref'], r['idx_x'], r['idx_c'], r['leg'], r['D']) == (20, 20, 22, 1, 1)
    assert r['T'] == 1 and r['T_nen'] == 21 and abs(r['T_gia'] - 4132.1) < 1e-9
    assert r['Bc'] == 1 and abs(r['Bc_gia'] - 4131.4) < 1e-9
    assert r['K'] == 0 and r['Vk'] == 0 and r['S'] == 0 and r['Dh'] == 0
    assert r['move_h'] == 22 and r['depth'] == 19
    # S2: min(E 41310, đáy nhịp hồi/CF 41313) − đệm 3 = 41307 (dưới cạnh), rủi ro 15 = sàn 1 mbr; TP 2R
    assert r['entry'] == 41322 and r['sl_S2'] == 41307 and r['tp_S2'] == 41352
    assert r['sl_S1'] == 41307                     # S1 = 41313 − 3 = 41310 ⇒ rủi ro 12 < sàn ⇒ đẩy ra 15
    d = pd.DataFrame(m.rows)
    mk = FC.combo_mask(d)
    fired = [k for k in FC.COMBOS if mk[k][0]]
    assert fired == ['F0', 'F1', 'F2', 'F4', 'F10']
    t = SC.sim_one(df, f, FC.to_entry(r))
    assert t['outcome'] == 'TP' and t['exit_idx'] == 24 and abs(t['r'] - (3.0 - 0.2) / 1.5) < 1e-9


def test_2_pullback_closes_inside_range_is_failbreak():
    rows = photo_rows()
    rows[21] = dict(o=41324, h=41325, l=41300, c=41308, d=-10)        # nến hồi đóng 4130,8 ≤ cạnh ⇒ FailBreak
    _, _, m = run(rows)
    assert m.rows == []
    assert m.all[0].end == 'failbreak'


def test_3_cf_at_x_plus_4_expires():
    rows = pad()
    rows.append(dict(o=41300, h=41332, l=41298, c=41325, d=20))
    rows.append(dict(o=41324, h=41325, l=41316, c=41320, d=-5))       # 21 hồi
    rows.append(dict(o=41320, h=41322, l=41315, c=41318, d=-5))       # 22 hồi (giảm ⇒ không CF)
    rows.append(dict(o=41318, h=41320, l=41314, c=41316, d=-5))       # 23 hồi
    rows.append(dict(o=41316, h=41324, l=41315, c=41323, d=20))       # 24 = x+4: đạt CF nhưng quá hạn
    rows += [dict(o=41323, h=41326, l=41320, c=41322) for _ in range(5)]
    _, _, m = run(rows)
    assert m.rows == []
    assert any(lg['end'] == 'het_han' for lg in m.legs)
    _, _, m4 = run(rows, fp=FC.FP(cf_within=4))                       # biến thể cf_within 4 thì bắt
    assert len(m4.rows) == 1 and m4.rows[0]['idx_c'] == 24


def flat_tail(rows):
    return rows + [dict(o=41318, h=41320, l=41316, c=41318) for _ in range(5)]    # nến đứng (o = c) ⇒ không bao giờ là CF


def test_4_cf_needs_green_delta_and_higher_close():
    _, _, m = run(flat_tail(photo_rows(cf=dict(d=-5), tail=False)))
    assert m.rows == []
    _, _, m = run(flat_tail(photo_rows(cf=dict(c=41315, o=41314), tail=False)))   # đóng 4131,5 = đóng nến hồi ⇒ không "cao hơn"
    assert m.rows == []
    _, _, m = run(flat_tail(photo_rows(cf=dict(o=41323, c=41320, d=10), tail=False)))   # nến giảm ⇒ không CF
    assert m.rows == []
    _, _, m = run(flat_tail(photo_rows(tail=False)))                   # đối chứng: CF gốc thì bắt
    assert len(m.rows) == 1
    # CF Δ âm ở x+2 vẫn là nến hồi ⇒ nến x+3 đạt CF thì được tính (nhịp hồi 2 nến)
    _, _, m = run(photo_rows(cf=dict(d=-5)))
    assert [(r['idx_c'], r['n_hoi']) for r in m.rows] == [(23, 2)]


def test_5_vk_veto_unswept_vs_swept():
    xlv = setlv(uni(41298, 41332), 41332, ask=0)                       # kiệt sức ĐỈNH ở x (Ask 0 ở đỉnh, râu 0,7)
    _, f, m = run(photo_rows(x_lv=xlv))
    assert f.exh[20][0].hit
    assert len(m.rows) == 1 and m.rows[0]['Vk'] == 1
    # CF quét qua đỉnh x ≥ 1 tick ⇒ mức kiệt sức đã bị quét ⇒ không veto
    _, _, m = run(photo_rows(x_lv=xlv, cf=dict(h=41334)))
    assert len(m.rows) == 1 and m.rows[0]['Vk'] == 0


def test_6_leg2_only_on_new_extreme_max_two():
    rows = photo_rows(tail=False)
    rows.append(dict(o=41322, h=41340, l=41320, c=41338, d=9))        # 23: cực trị mới 4134,0 > 4133,2 ⇒ leg 2
    rows.append(dict(o=41338, h=41339, l=41330, c=41332, d=-4))       # 24: hồi
    rows.append(dict(o=41332, h=41337, l=41331, c=41336, d=10))       # 25: CF leg 2
    rows.append(dict(o=41336, h=41350, l=41335, c=41348, d=10))       # 26: cực trị mới nữa ⇒ đã hết 2 leg
    rows.append(dict(o=41348, h=41349, l=41340, c=41342, d=-4))       # 27: hồi
    rows.append(dict(o=41342, h=41347, l=41341, c=41346, d=10))       # 28: "CF" — không được tính
    rows += [dict(o=41346, h=41348, l=41344, c=41347) for _ in range(4)]
    _, _, m = run(rows)
    assert [(r['leg'], r['idx_x'], r['idx_c']) for r in m.rows] == [(1, 20, 22), (2, 23, 25)]
    # không có cực trị mới ⇒ không có leg 2
    rows = photo_rows(tail=False)
    rows.append(dict(o=41322, h=41330, l=41320, c=41328, d=9))
    rows.append(dict(o=41328, h=41329, l=41318, c=41320, d=-4))
    rows.append(dict(o=41320, h=41327, l=41319, c=41326, d=10))
    rows += [dict(o=41326, h=41328, l=41324, c=41327) for _ in range(4)]
    _, _, m = run(rows)
    assert [r['leg'] for r in m.rows] == [1]


def test_7_trap_needs_cf_close_above_cell_and_upper_half():
    _, _, m = run(photo_rows(pb_bid_tick=41323))                       # ô 4132,3 > đóng CF 4132,2 ⇒ phe sell chưa bị kẹt
    assert m.rows[0]['T'] == 0
    _, _, m = run(photo_rows(pb_bid_tick=41315))                       # ô ở nửa DƯỚI nến hồi (trung điểm 4131,9)
    assert m.rows[0]['T'] == 0
    _, _, m = run(photo_rows(pb_bid_tick=41319))                       # đúng trung điểm ⇒ tính nửa trên
    assert m.rows[0]['T'] == 1


def test_8_one_trade_per_range_edge_leg():
    d = pd.DataFrame(dict(idx_c=[10, 50, 60, 90], range_id=[0, 0, 0, 1], D=[1, 1, 1, 1], leg=[1, 1, 2, 1],
                          exit_alone=[20, 55, 70, 95]))
    t = FC.select(d, np.ones(4, bool))
    assert list(t['idx_c']) == [10, 60, 90]                           # 50 trùng (range 0, cạnh trên, leg 1)
    d2 = d.copy()
    d2.loc[0, 'exit_alone'] = 65                                      # lệnh đầu còn mở tới 65 ⇒ 50, 60 bị bỏ vì đang có lệnh
    assert list(FC.select(d2, np.ones(4, bool))['idx_c']) == [10, 90]


def mirror_rows(rows, M=82600):
    out = []
    for r in rows:
        lv = r.get('lv') or uni(r['l'], r['h'])
        out.append(dict(o=M - r['o'], h=M - r['l'], l=M - r['h'], c=M - r['c'], d=-r.get('d', 0),
                        lv=sorted((M - k, a, b, v) for (k, b, a, v) in lv)))
    return out


def test_9_mirror_sell_side():
    M = 82600
    rows = mirror_rows(photo_rows(), M)
    events = {REF: [ev('CloseOutside', -1, top=M - BOT, bottom=M - TOP)]}
    df, f, m = run(rows, events)
    assert len(m.rows) == 1
    r = m.rows[0]
    assert (r['idx_c'], r['D'], r['E']) == (22, -1, M - TOP)
    assert r['T'] == 1 and r['Bc'] == 1 and r['K'] == 0 and r['Vk'] == 0
    assert r['entry'] == M - 41322 and r['sl_S2'] == M - 41307 and r['tp_S2'] == M - 41352
    t = SC.sim_one(df, f, FC.to_entry(r))
    assert t['outcome'] == 'TP' and t['exit_idx'] == 24
    # Vk lật: kiệt sức ĐÁY ở x
    rows = mirror_rows(photo_rows(x_lv=setlv(uni(41298, 41332), 41332, ask=0)), M)
    _, _, m = run(rows, events)
    assert m.rows[0]['Vk'] == 1


def test_10_permutation_null_flags_independent_of_r():
    rng = np.random.default_rng(7)
    praws, n_dat = [], 0
    for rep in range(12):
        n_s, per = 35, 12
        N = n_s * per
        flags = pd.DataFrame({k: rng.random(N) < q for k, q in zip(FC.FLAGS, (0.1, 0.3, 0.2, 0.25, 0.4, 0.3, 0.5, 0.3))})
        r = rng.choice([-1.07, 1.87], size=N, p=[0.62, 0.38])             # R độc lập với cờ
        grp = np.repeat(np.arange(n_s), per)
        mk = FC.combo_mask(flags)
        Mx = np.column_stack([mk[k] for k in FC.SEL_COMBOS])
        obs, perm, maxs = FC.perm_test(Mx, r, grp, n_perm=300, seed=rep)
        thr = float(np.percentile(maxs, 95))
        p_raw, p_max = FC.perm_pvalues(obs, perm, maxs)
        praws += list(p_raw[~np.isnan(p_raw)])
        for j, k in enumerate(FC.SEL_COMBOS):
            rk = r[mk[k]]
            s = FC.stats_r(rk, n_s)
            half = grp[mk[k]] < 18
            jd = FC.judge(s, float(r.mean()), float(r.mean()), rk[half].mean(), rk[~half].mean(), obs[j], thr)
            n_dat += jd['dat']
        assert thr > 0
    praws = np.array(praws)
    # p thô ≈ đều: trung bình ≈ 0,5, tỷ lệ < 0,05 không vượt xa 5 %
    assert 0.35 < praws.mean() < 0.65
    assert (praws < 0.05).mean() < 0.15
    assert n_dat == 0
