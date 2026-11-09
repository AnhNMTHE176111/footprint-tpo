# -*- coding: utf-8 -*-
"""Test nhãn máy mổ SL Follow (mo_sl_follow.measure) — plan 5.2 / 9.3-B2. Dữ liệu tổng hợp theo tick.
Chạy: python -m pytest benzo-trader/research/test_mo_sl_follow.py -q"""
import os
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mo_sl_follow as MS        # noqa: E402

N = 120
E = 1000


def mk(bars, phase='EU', vol=50.0):
    """bars: {i: (o,h,l,c)}; còn lại nến đứng 1010 (trên cạnh E, buy)."""
    O = np.full(N, 1010); H = np.full(N, 1012); L = np.full(N, 1008); C = np.full(N, 1010)
    for i, (o, h, l, c) in bars.items():
        O[i], H[i], L[i], C[i] = o, h, l, c
    f = SimpleNamespace(O=O, H=H, L=L, C=C, V=np.full(N, vol), send=np.full(N, N - 1))
    df = pd.DataFrame({'phase': [phase] * N})
    return df, f


def row(outcome='SL', exit_idx=70, sl=997, tp=1030, deep=0, c=65, D=1):
    return SimpleNamespace(D=D, idx_c=c, E=E, t_utc='', t_vn='', leg=1, T=0, Bc=0, K=0, S=0, Dh=1, Dc=0, Sh=0, Mv=0,
                           outcome_alone=outcome, r_alone=-1.0 if outcome == 'SL' else 2.0, exit_alone=exit_idx, sl_S2=sl, tp_S2=tp,
                           depth_frac=0.3, deep=deep)


CF = {65: (1002, 1011, 1001, 1010)}                    # CF khoẻ: thân 8/10, đóng–đỉnh 1/10
P25 = np.full(N, 10.0)


def test_move_gia_first_priority():
    df, f = mk({**CF, 67: (1010, 1011, 996, 999)})     # nến c+2 đóng 999 ≤ E ⇒ MOVE_GIA (dù cũng dính SL)
    x = MS.measure(row(exit_idx=67), df, f, P25)
    assert x['f_MOVE_GIA'] == 1 and x['nen_dong_trong'] == 2 and x['nhan'] == 'MOVE_GIA'
    # đóng trong ở c+6 ⇒ ngoài cửa sổ 5 nến
    df, f = mk({**CF, 71: (1010, 1011, 990, 995)})
    x = MS.measure(row(exit_idx=71), df, f, P25)
    assert x['f_MOVE_GIA'] == 0


def test_sl_quet_needs_le2_tick_and_tp_within_30():
    # nến 70 râu xuống 995 (xuyên SL 997 đúng 2 tick), đóng lại trên E; nến 90 chạm TP 1030
    df, f = mk({**CF, 70: (1010, 1011, 995, 1005), 90: (1010, 1031, 1009, 1029)})
    x = MS.measure(row(), df, f, P25)
    assert x['sl_xuyen_tick'] == 2 and x['cham_tp_sau_sl_nen'] == 20 and x['nhan'] == 'SL_QUET'
    df, f = mk({**CF, 70: (1010, 1011, 994, 1005), 90: (1010, 1031, 1009, 1029)})     # xuyên 3 tick ⇒ không
    assert MS.measure(row(), df, f, P25)['f_SL_QUET'] == 0
    df, f = mk({**CF, 70: (1010, 1011, 995, 1005), 101: (1010, 1031, 1009, 1029)})    # TP ở nến thứ 31 ⇒ không
    assert MS.measure(row(), df, f, P25)['f_SL_QUET'] == 0
    assert MS.measure(row(outcome='TP'), df, f, P25)['f_SL_QUET'] == 0               # lệnh TP không mang nhãn này


def test_priority_chain_and_khong_ro():
    df, f = mk(CF)
    assert MS.measure(row(deep=1), df, f, P25)['nhan'] == 'HOI_SAU'
    df, f = mk({65: (1005, 1011, 1001, 1008)})         # thân 3/10 < 0,4 ⇒ CF_YEU
    assert MS.measure(row(), df, f, P25)['nhan'] == 'CF_YEU'
    df, f = mk({**CF, 5: (1020, 1021, 1019, 1020)})    # close[c−60] = 1020 > close[c] 1010 ⇒ ngược 1 giờ
    assert MS.measure(row(), df, f, P25)['nhan'] == 'NGUOC_1H'
    df, f = mk(CF, phase='A')
    assert MS.measure(row(), df, f, P25)['nhan'] == 'PHIEN_MONG'
    df, f = mk(CF, vol=5.0)                            # volume 5 < p25 10 ⇒ phiên mỏng
    assert MS.measure(row(), df, f, P25)['nhan'] == 'PHIEN_MONG'
    df, f = mk(CF)
    assert MS.measure(row(), df, f, P25)['nhan'] == 'KHONG_RO'


def test_sell_side_mirror():
    # D = −1, cạnh dưới E = 1000, giá dưới E; CF giảm khoẻ; c+1 đóng 1001 ≥ E ⇒ MOVE_GIA
    df, f = mk({i: (990, 992, 988, 990) for i in range(N)} | {65: (998, 999, 989, 990), 66: (990, 1003, 989, 1001)})
    x = MS.measure(row(D=-1, sl=1003, tp=970, exit_idx=66), df, f, P25)
    assert x['f_MOVE_GIA'] == 1 and x['cf_than'] == 0.8 and x['f_CF_YEU'] == 0
