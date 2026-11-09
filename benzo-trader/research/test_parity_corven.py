# -*- coding: utf-8 -*-
"""Khoá lớp 2 của ranh giới TEST trong parity_corven.py (plan 12.1 #1) + bỏ cổng cuoi_phien hai phía (12.2-Q2) + chong_rate (Q4).
Chạy: python -m pytest benzo-trader/research/test_parity_corven.py -q   (không đọc file dữ liệu)"""
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_corven as PC      # noqa: E402


def _test_part(r='', ket='', ex=''):
    return pd.DataFrame(dict(idx=[60000, 60001], ket_cuc=['', ket], r=['', r], exit_idx=['', ex]))


def test_test_part_all_empty_passes():
    PC.assert_test_hidden(_test_part())


def test_test_part_with_one_r_cell_raises_and_removes_tmp(tmp_path):
    d = tmp_path / 'replay'
    d.mkdir()
    (d / 'cs_trades.csv').write_text('x', encoding='utf-8')
    with pytest.raises(RuntimeError, match='RANH GIỚI TEST'):
        PC.assert_test_hidden(_test_part(r='-1.1'), str(d))
    assert not d.exists()


@pytest.mark.parametrize('col', ['ket_cuc', 'exit_idx'])
def test_any_outcome_column_raises(col):
    kw = {'ket': 'SL'} if col == 'ket_cuc' else {'ex': '61000'}
    with pytest.raises(RuntimeError):
        PC.assert_test_hidden(_test_part(**kw))


def test_strip_cuoi_phien_both_sides():
    assert PC.strip_cuoi_phien('g4a_cf;cuoi_phien') == 'g4a_cf'
    assert PC.strip_cuoi_phien('cuoi_phien') == ''
    assert PC.strip_cuoi_phien('') == ''


def test_chong_rate_over_030_raises():
    assert PC.check_chong(dict(chong_rate=0.018), 'x') == pytest.approx(0.018)
    with pytest.raises(RuntimeError):
        PC.check_chong(dict(chong_rate=0.31), 'x')
