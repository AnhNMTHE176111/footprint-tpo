"""Tự kiểm kiệt sức: ví dụ nhỏ + bản chuẩn từng nến (exh_rule.run_reference) trùng bản bảng (exh_final.py) trên GC M15 và NQ M30; in số dấu chuẩn theo mã x khung.
Chạy: python exh_selftest.py"""
import numpy as np, pandas as pd
from exh_rule import tail_sum, median, run_reference
from exh_common import ohlc, tail_base, P
from common_window import nbase
# ---- ví dụ nhỏ ----
LV = {100: (4, 0), 101: (3, 1), 102: (0, 2), 103: (5, 6), 104: (2, 9), 105: (1, 3), 110: (7, 2), 111: (0, 1)}     # tick -> (Bid, Ask)
assert tail_sum(LV, 111, True) == 1 + 2 + 0 + 0 + 0 + 0 == 3          # đỉnh 111: Ask của 111, 110, 109..106 (trống = 0)
assert tail_sum(LV, 100, False) == 4 + 3 + 0 + 5 + 2 + 1 == 15        # đáy 100: Bid của 100..105
assert median([3, 15, 1, 8]) == 5.5 and median([3, 15, 1]) == 3
# 5 nến nền giống nhau: o=103 h=111 l=100 c=104, ô như LV (volume TB mỗi ô = 46/8 = 5,75; đuôi đỉnh 3, đuôi đáy 15 -> trung vị đuôi = 9)
cells = [(t, b, a, b + a) for t, (b, a) in LV.items()]
B0 = (103, 111, 100, 104, cells)
# nến xét 1: như nền -> đỉnh: râu 111-104 = 7 >= 3, S = 3 <= 1,1 x 5,75 = 6,325 và <= 0,8 x 9 = 7,2 -> CÓ; đáy: S = 15 > 6,325 -> không
# nến xét 2: đỉnh râu chỉ 2 tick (o=109) -> không dù S = 3
r = run_reference([B0] * 5 + [B0, (109, 111, 100, 108, cells)], N=20)
assert r[:5] == [(False, False)] * 5 and r[5] == (True, False) and r[6] == (False, False), r
# điều kiện (2) chặn: nền có đuôi rất mỏng (trung vị đuôi = 2) -> nến có S = 3 không còn "mỏng hơn bình thường": 3 > 0,8 x 2
THIN = {100: (1, 0), 101: (1, 0), 106: (9, 9), 107: (9, 9), 112: (0, 1), 113: (0, 1)}   # đuôi đỉnh (113..108) = 2, đuôi đáy (100..105) = 2, TB mỗi ô = 40/6
tc = [(t, b, a, b + a) for t, (b, a) in THIN.items()]
r = run_reference([(104, 113, 100, 105, tc)] * 5 + [B0], N=20)
assert r[5] == (False, False), r                                       # (1) đạt: 3 <= 1,1 x 6,67 = 7,33 nhưng (2) không: 3 > 0,8 x 2 = 1,6
assert run_reference([(104, 113, 100, 105, tc)] * 5 + [B0], N=20, c=0)[5] == (True, False)   # c = 0 = tắt điều kiện (2) -> như luật cũ
print('ví dụ nhỏ: ĐẠT')
# ---- bản chuẩn = bản bảng ----
rows = []
for sym, m in (('GC', 15), ('NQ', 30), ('GC', 5), ('NQ', 5)):
    F = pd.read_pickle(f'{P}F_{sym}_m{m}.pkl').sort_values(['t', 'tk']); O = ohlc(sym, m)
    bars = []; ts = []
    for t, g in F.groupby('t', sort=True):
        if t not in O.index: continue
        o, h, l, c = O.loc[t].values
        bars.append((o, h, l, c, list(zip(g.tk.values.tolist(), g.bid.values.tolist(), g.ask.values.tolist(), g.vol.values.tolist())))); ts.append(t)
    ref = run_reference(bars, N=nbase(m)); n_ref = sum(a + b for a, b in ref)
    X = pd.read_pickle(f'X_{sym}_m{m}.pkl'); X = X[X.Bm20.notna()].reset_index(drop=True); T = tail_base(X, 6, nbase(m))
    hit = ((X.wick >= 3) & (X.S6 <= 1.1 * X.Bm20)).values & ~(X.S6.values > 0.8 * T)
    old = int(((X.wick >= 3) & (X.S6 <= 1.1 * X.Bm20)).sum())
    print(f'{sym} M{m}: bản chuẩn {n_ref} dấu, bản bảng {int(hit.sum())} dấu (luật cũ {old})')
    pd.DataFrame([(t, a, b) for t, (a, b) in zip(ts, ref) if a or b], columns=['t', 'dinh', 'day']).to_csv(f'exh_golden_{sym}_M{m}.csv', index=False)
