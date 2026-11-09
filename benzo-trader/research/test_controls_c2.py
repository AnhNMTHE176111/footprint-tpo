# -*- coding: utf-8 -*-
"""Test C2' (controls_corven.c2 after_only) — plans/BENZO-FOLLOW-COMBO-plan.md 9.3-A1.
Chạy: python -m pytest benzo-trader/research/test_controls_c2.py -q
(i) after_only=True không bao giờ chọn nến j ≤ i (và pool < 5 ⇒ bỏ lệnh);
(ii) after_only=False cho kết quả BIT-GIỐNG bản c2 cũ (bản cũ chép nguyên văn dưới đây làm chuẩn)."""
import os
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import controls_corven as CC     # noqa: E402
import setup_corven as SC        # noqa: E402
from test_setup_corven_gd1 import world   # noqa: E402

TICK = SC.TICK


def c2_old(R, n_random=20, seed=0, minutes=30):
    """Nguyên văn controls_corven.c2 trước 2026-11-09 (commit 9697f63) — chuẩn so bit-giống."""
    f, df, cp = R['feat'], R['df'], R['cp']
    rng = np.random.default_rng(seed)
    rows, allr = [], []
    for c, (_, t) in zip(R['chosen'], R['trades'].iterrows()):
        i, S = c.cf, c.S
        s0, s1 = int(f.sstart[i]), int(f.send[i])
        pool = [j for j in range(s0, s1) if j != i and abs(int(f.sm[j]) - int(f.sm[i])) <= minutes and f.good[j]
                and f.mbr[j] > 0]
        if not pool:
            continue
        pick = rng.choice(pool, size=min(n_random, len(pool)), replace=False)
        rm = c.risk / f.mbr[i]
        rs = []
        for j in sorted(int(x) for x in pick):
            ent = int(f.C[j])
            risk = rm * f.mbr[j]
            sl = ent - S * risk
            sl = int(np.floor(sl + 1e-9)) if S > 0 else int(np.ceil(sl - 1e-9))
            risk = (ent - sl) * S
            if risk <= 0:
                continue
            e = dict(idx=j, side=S, entry=round(ent * TICK, 6), sl=round(sl * TICK, 6),
                     tp=round((ent + S * cp.tp_r * risk) * TICK, 6), setup='C2', zone='', note='')
            x = SC.sim_one(df, f, e)
            if x is not None and x['outcome'] in ('TP', 'SL', 'TIME'):
                rs.append(float(x['r']))
        if rs:
            rows.append(dict(idx=i, r_that=float(t['r']), r_c2_tb=float(np.mean(rs)), n_c2=len(rs)))
            allr += rs
    return pd.DataFrame(rows), np.array(allr)


def rand_world(n=180, seed=7):
    rng = np.random.default_rng(seed)
    p = 41000
    rows = []
    for _ in range(n):
        o = p
        c = o + int(rng.integers(-12, 13))
        h = max(o, c) + int(rng.integers(0, 6))
        l = min(o, c) - int(rng.integers(0, 6))
        rows.append(dict(o=o, h=h, l=l, c=c, d=int(rng.integers(-30, 31))))
        p = c
    return world(rows, start='2026-09-01 02:00')


def make_R(df, f, idxs, sides, risks):
    chosen = [SimpleNamespace(cf=i, S=s, risk=float(r)) for i, s, r in zip(idxs, sides, risks)]
    tr = pd.DataFrame({'r': np.linspace(-1, 2, len(idxs))})
    return dict(feat=f, df=df, cp=SimpleNamespace(tp_r=2.0), chosen=chosen, trades=tr)


def test_after_only_never_picks_j_le_i(monkeypatch):
    df, f = rand_world()
    idxs, sides, risks = [40, 70, 100, 130], [1, -1, 1, -1], [15, 20, 25, 30]
    R = make_R(df, f, idxs, sides, risks)
    seen = []
    real = SC.sim_one

    def spy(df_, f_, e):
        seen.append(int(e['idx']))
        return real(df_, f_, e)
    monkeypatch.setattr(SC, 'sim_one', spy)
    d2, allr = CC.c2(R, after_only=True)
    assert len(d2) == 4 and len(allr) > 0
    # mỗi lệnh giả gán theo thứ tự: các nến đã mô phỏng của lệnh thứ k nằm trong (i_k, i_k + 30′]
    k = 0
    for i in idxs:
        mine = seen[k:k + 20]
        k += 20
        assert all(j > i for j in mine), (i, mine)
        assert all(0 < int(f.sm[j]) - int(f.sm[i]) <= 30 for j in mine)
    # bản cũ có chọn nến TRƯỚC i (để chắc test (i) phân biệt được hai chế độ)
    seen.clear()
    CC.c2(R, after_only=False)
    assert any(j < 40 for j in seen[:20])


def test_after_only_pool_lt5_dropped():
    df, f = rand_world()
    n = len(f.C)
    R = make_R(df, f, [n - 4], [1], [15])          # chỉ còn ≤ 3 nến sau i trong phiên ⇒ pool < 5 ⇒ bỏ
    d2, allr = CC.c2(R, after_only=True)
    assert len(d2) == 0 and len(allr) == 0


def test_default_bit_identical_to_old():
    df, f = rand_world(seed=11)
    R = make_R(df, f, [35, 60, 90, 120, 150], [1, -1, -1, 1, 1], [12, 18, 22, 15, 40])
    a_df, a_r = c2_old(R)
    b_df, b_r = CC.c2(R)
    c_df, c_r = CC.c2(R, after_only=False)
    assert len(a_df) > 0
    pd.testing.assert_frame_equal(a_df, b_df, check_exact=True)
    pd.testing.assert_frame_equal(a_df, c_df, check_exact=True)
    assert np.array_equal(a_r, b_r) and np.array_equal(a_r, c_r)
