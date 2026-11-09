# -*- coding: utf-8 -*-
"""Test plan BENZO-FOLLOW-COMBO mục 10.3-1/2 (hậu kiểm vòng mổ 1): cờ Hc, F7b ⊆ F7, bảng chính F0…F10 bit-giống cũ, cột H1–H3.
Chạy: python -m pytest benzo-trader/research/test_follow_post.py -q"""
import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import follow_combo as FC              # noqa: E402
from test_follow_combo import photo_rows, run   # noqa: E402

REPORT = os.path.join(HERE, 'report')


def _row_with_pb_low(low, mbr=15.0):
    """Ca ảnh gốc, đổi đáy nến hồi (nến 21); E = 41310, tol = max(2, 0,5·mbr)."""
    rows = photo_rows()
    rows[21] = dict(rows[21], l=low)
    rows[22] = dict(rows[22], l=min(rows[22]['l'], low + 1))
    _, _, m = run(rows, mbr=mbr)
    assert len(m.rows) == 1
    return m.rows[0]


def test_hc_inside_outside_and_on_edge():
    # mbr 15 ⇒ tol 7,5 tick
    r = _row_with_pb_low(41317)                    # cách cạnh 7 tick ≤ 7,5 ⇒ chạm
    assert r['Hc'] == 1 and abs(r['hc_ext_mbr'] - (-7 / 15)) < 1e-3
    r = _row_with_pb_low(41318)                    # 8 tick > 7,5 ⇒ không chạm
    assert r['Hc'] == 0 and abs(r['hc_ext_mbr'] - (-8 / 15)) < 1e-3
    r = _row_with_pb_low(41310)                    # đúng cạnh
    assert r['Hc'] == 1 and r['hc_ext_mbr'] == 0
    # mbr 3 ⇒ tol = sàn 2 tick: 2 tick chạm, 3 tick không
    assert _row_with_pb_low(41312, mbr=3.0)['Hc'] == 1
    assert _row_with_pb_low(41313, mbr=3.0)['Hc'] == 0


def test_photo_case_has_hc_and_hyp_columns():
    _, _, m = run(photo_rows())
    r = m.rows[0]
    # ca ảnh gốc: đáy nến hồi 4131,3 cách cạnh 4131,0 đúng 3 tick ≤ tol 7,5 ⇒ Hc = 1 (và Dh = 0) ⇒ ca ảnh KHÔNG thuộc F7b
    assert r['Hc'] == 1 and r['Dh'] == 0
    assert abs(r['cf_body'] - 7 / 10) < 1e-9                    # CF 41315→41322, biên độ 41313–41323
    assert abs(r['move_x_rng'] - 22 / 40) < 1e-9                # move_h 22 / range 40 tick
    assert r['risk_gia'] == r['risk_S2'] / 10.0


def test_post_mask_f7b_subset_of_f7_synthetic():
    rng = np.random.default_rng(1)
    d = pd.DataFrame({k: rng.integers(0, 2, 500) for k in FC.FLAGS + ('Hc',)})
    m = FC.post_mask(d)
    assert not (m['F7b'] & ~m['F7']).any()
    assert ((m['F7b'] | m['F7Hc']) == m['F7']).all() and not (m['F7b'] & m['F7Hc']).any()
    assert not (m['F10nHc'] & ~m['F10']).any()
    for k in FC.COMBOS:                                         # 11 combo cũ không đổi
        assert (m[k] == FC.combo_mask(d)[k]).all()


@pytest.mark.skipif(not os.path.exists(os.path.join(REPORT, '_follow_trades_F7b.csv')), reason='chưa chạy follow_combo.py')
def test_f7b_trades_subset_of_f7_candidates():
    c = pd.read_csv(os.path.join(REPORT, '_follow_cands.csv'))
    t = pd.read_csv(os.path.join(REPORT, '_follow_trades_F7b.csv'))
    f7 = set(c.loc[c['Dh'] == 1, 'idx_c'])
    f7b = set(c.loc[(c['Dh'] == 1) & (c['Hc'] == 0), 'idx_c'])
    assert set(t['idx_c']) <= f7b <= f7
    assert (t['Dh'] == 1).all() and (t['Hc'] == 0).all()


# bảng chính commit 798de45 / aa3d078 (trước khi thêm Hc) — n, R TB, C2' phải BIT-giống
OLD = dict(F0=(340, -0.04974673259608278, -0.021970909959780453), F1=(11, 0.30733193726402097, 0.5121949435740152),
           F2=(26, -0.36431549539108665, -0.3435044700900148), F3=(82, 0.0035449481204424763, -0.06015962802722098),
           F4=(0, None, None), F5=(2, 0.4157894736842098, 0.11519964684438377), F6=(226, -0.044849973990058, -0.038001593719562035),
           F7=(96, 0.19983175018875474, 0.046342708320823746), F8=(49, -0.15955020263707326, -0.07998306111130865),
           F9=(214, -0.07280018657850035, -0.047179000553239335), F10=(120, 0.11638894643865202, 0.012935689274362743))


@pytest.mark.skipif(not os.path.exists(os.path.join(REPORT, '_follow_summary.json')), reason='chưa chạy follow_combo.py')
def test_main_table_bit_identical_to_before_hc():
    s = json.load(open(os.path.join(REPORT, '_follow_summary.json'), encoding='utf-8'))
    for k, (n, avg, c2p) in OLD.items():
        assert s[k]['n'] == n, k
        assert s[k]['avg'] == avg, k
        assert s[k]['c2p'] == c2p, k
    assert s['thr30'] == 0.31367602229949537 and s['n_f0'] == 772 and s['nd'] == 35
