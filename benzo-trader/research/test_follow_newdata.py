# -*- coding: utf-8 -*-
"""Parity follow_newdata.py ↔ follow_combo.py (plan BENZO-FOLLOW-COMBO mục 10.3-3) trên 2 TUẦN CUỐI TRAIN (phiên 2026-09-02 … 09-15).
Nhánh A = đường follow_combo: setup_corven.load_train (cắt TEST) → cắt đoạn → FC.build → FC.eval_post.
Nhánh B = follow_newdata.run trên cùng đoạn (đọc thẳng từ file). Mọi con số bảng chính + F7b + H1–H3 phải trùng.
Chạy: python -m pytest benzo-trader/research/test_follow_newdata.py -q   (≈ 1–3 phút, cần file 90d)"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K                 # noqa: E402
import of_signals as OF            # noqa: E402
import setup_corven as SC          # noqa: E402
import follow_combo as FC          # noqa: E402
import follow_newdata as FN        # noqa: E402

LO, HI = '2026-09-02', '2026-09-15'
NPERM = 200
HAVE = os.path.exists(SC.D90 + '_bars.csv') and os.path.exists(SC.D90 + '.csv')


def branch_a():
    bars, df = SC.load_train()
    day = df['session_id'].str[:10].to_numpy()
    pos = np.flatnonzero((day >= LO) & (day <= HI))
    p0, p1 = int(pos[0]), int(pos[-1])
    assert len(pos) == p1 - p0 + 1
    rawcols = list(pd.read_csv(SC.D90 + '_bars.csv', nrows=0).columns)
    raw = df.iloc[p0:p1 + 1][rawcols].reset_index(drop=True)
    raw['bar_idx'] = np.arange(len(raw))
    dfs = K._enrich(raw)
    bs = [OF.FpBar(i, b.o, b.h, b.l, b.c, b.delta, b.max_delta, b.min_delta, list(b.levels))
          for i, b in enumerate(bars[p0:p1 + 1])]
    good = (~dfs['thin'].to_numpy()) & (~dfs['splice'].to_numpy()) & (dfs['split'].to_numpy() == 'TRAIN')
    sess_good = sorted(set(dfs['session_id'].to_numpy()[good]))
    fp = FC.FP()
    _, d, f, _ = FC.build(bs, dfs, good, fp)
    d = FC.add_halves(d, sess_good)
    return FC.eval_post(d, f, dfs, fp, len(sess_good), n_perm=NPERM), d, len(sess_good)


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, float) and np.isnan(a):
        return isinstance(b, float) and np.isnan(b)
    return abs(a - b) < 1e-12


@pytest.mark.skipif(not HAVE, reason='thiếu file 90d')
def test_parity_last_two_weeks_train():
    Ea, da, nda = branch_a()
    R = FN.run(SC.D90, LO, HI, n_perm=NPERM)
    Eb, db, ndb = R['E'], R['d'], R['nd']
    assert nda == ndb >= 8
    assert len(da) == len(db) > 0
    assert (da['idx_c'].to_numpy() == db['idx_c'].to_numpy()).all()
    for col in ('entry', 'sl_S2', 'tp_S2', 'r_alone', 'Hc', 'Dh', 'cf_body', 'risk_gia', 'move_x_rng', 'half'):
        assert np.allclose(da[col].to_numpy(float), db[col].to_numpy(float), equal_nan=True), col
    assert same(Ea['thr30'], Eb['thr30']) and same(Ea['c1'], Eb['c1'])
    for k in FC.ALL_POST:
        a, b = Ea['res'][k], Eb['res'][k]
        assert a['s'].get('n', 0) == b['s'].get('n', 0), k
        for key in ('avg', 'lo', 'hi', 'sum'):
            assert same(a['s'].get(key), b['s'].get(key)), (k, key)
        for key in ('c2p', 'h1', 'h2', 'obs', 'p_raw', 'p_max30'):
            assert same(a[key], b[key]), (k, key)
        assert a['jd'] == b['jd'], k
    assert [c[:2] for c in Ea['cond']] == [c[:2] for c in Eb['cond']]
    assert Ea['f7b_dat'] == Eb['f7b_dat']
    for key in Ea['hyp']:
        for x, y in zip(Ea['hyp'][key], Eb['hyp'][key]):
            assert x.get('n', 0) == y.get('n', 0) and same(x.get('avg'), y.get('avg')), key
    L = FN.report(R)                                   # báo cáo dựng được, có mục ca ảnh + kiểm F7b
    assert any('Ca ảnh gốc' in s for s in L) and any('F7b:' in s for s in L)


@pytest.mark.skipif(not HAVE, reason='thiếu file 90d')
def test_refuses_locked_test_window():
    with pytest.raises(AssertionError):
        FN.load_segment(SC.D90, '2026-09-10', '2026-09-20')
    with pytest.raises(AssertionError):                 # CLI mặc định: phiên ≥ 22/10 — file 90d không có phiên nào ⇒ từ chối
        FN.load_segment(SC.D90, FN.NEW_FROM)


def test_prefix_of():
    assert FN.prefix_of('a/fp_X_90d.csv') == 'a/fp_X_90d'
    assert FN.prefix_of('a/fp_X_90d_bars.csv') == 'a/fp_X_90d'
