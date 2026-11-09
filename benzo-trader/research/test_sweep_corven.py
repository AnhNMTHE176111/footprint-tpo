# -*- coding: utf-8 -*-
"""Test sweep_corven.py (GĐ2 vòng 2). Chạy: python -m pytest benzo-trader/research/test_sweep_corven.py -q"""
import os
import sys
from dataclasses import asdict

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_corven as SC        # noqa: E402
import sweep_corven as SW        # noqa: E402


def test_base_is_round1_and_each_cell_changes_exactly_one_param():
    cs = SW.cells()
    base = asdict(cs[0][1])
    assert base['sl_anchor'] == 'cu_thung' and base['a2_on'] is False      # bộ gốc = vòng 1
    assert len(cs) == 1 + len(SW.GRID) == 12
    for name, cp in cs[1:]:
        d = {k for k, v in asdict(cp).items() if v != base[k]}
        assert len(d) == 1, (name, d)                                         # đúng MỘT tham số khác bộ gốc
    assert len({n for n, _ in cs}) == len(cs)                                  # không ô trùng


def test_ok_flags_logic():
    r = dict(s=dict(n=40, avg=-0.10), c1=dict(avg=-0.20), c2=-0.05)
    a = r['s']['avg'] >= r['c1']['avg'] and r['s']['avg'] >= r['c2']
    assert not a                                                               # thua C2 ⇒ không đạt (a)


D90 = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'data-export', 'data-footprint',
                   'fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv')
TR = os.path.join(HERE, 'report', '_corven_trades.csv')


@pytest.mark.skipif(not (os.path.exists(D90) and os.path.exists(TR)), reason='thiếu dữ liệu 90d hoặc _corven_trades.csv')
def test_base_cell_through_sweep_reproduces_round1_trades():
    cut = SC.train_cut()
    bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    nd = len(set(df['session_id'].to_numpy()[good]))
    r = SW.run_cell(bars, df, good, SW.BASE, nd)
    ref = pd.read_csv(TR)
    assert r['s']['n'] == len(ref) == 97
    assert list(r['trades']['idx']) == list(ref['idx'])
    assert np.allclose(r['trades']['r'].round(3).to_numpy(), ref['r'].to_numpy())
    assert abs(r['s']['avg'] - (-0.294)) < 0.001
