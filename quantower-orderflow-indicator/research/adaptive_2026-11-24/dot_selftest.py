"""Tự kiểm phần chấm Bid/Ask (công thức chung):
(1) ví dụ nhỏ để viết unit test C#; (2) bản nhanh (dots_fast) trùng bản chuẩn từng nến (run_reference) trên GC M15, NQ M30;
(3) số chấm chuẩn theo mã x khung (đỏ + xanh) để so với perf/Golden, và file dot_golden_<mã>_M<khung>.csv (nến, tick, màu).
Chạy: python dot_selftest.py"""
import numpy as np, pandas as pd
from dot_rule import unified, evaluate_bar, run_reference, dots_fast, window_for
from dot_grid import build
from dot_measure import load, TFS
from common_window import nbase
from dot_rule import PRESET_RECALL, PRESET_QUIET
Q = PRESET_QUIET
UB = {'khong_sot': (dict(k=2.0, wmode='lin', c=6, wmin=4, hmult=0.0, hmin=2, floor=5), PRESET_RECALL), 'it_nhieu': (dict(k=2.8, wmode='lin', c=6, wmin=4, hmult=0.75, hmin=6, floor=9), PRESET_QUIET)}

# ---- (1) ví dụ nhỏ ----
def close(a, b): return a is not None and abs(a[0] - b[0]) < 1e-9 and a[1:] == b[1:]
assert close(unified(8.0, 39, **Q), (22.4, 7, 6))        # w = max(4, round(6,5) = 7); che = max(6, round(5,25) = 5) = 6
assert close(unified(3.0, 16, **Q), (9.0, 4, 6))         # 2,8 x 3 = 8,4 < sàn 9; w = max(4, round(2,67) = 3) = 4
assert close(unified(16.2, 183, **Q), (45.36, 31, 23))   # w = round(30,5) = 31 (nửa lên); che = round(23,25) = 23
assert close(unified(10.0, 0, **Q), (28.0, 4, 6))        # chưa có biên độ -> cửa sổ tối thiểu
assert close(unified(8.0, 39), (16.0, 7, 2)) and close(unified(2.0, 16), (5.0, 4, 2))   # bộ ưu tiên không sót: 2,0 x B, sàn 5, che 2
assert unified(0, 50) is None and unified(None, 50) is None
assert window_for(27, 6, 4) == 5 and window_for(21, 6, 4) == 4      # 4,5 -> 5 ; 3,5 -> 4 (nửa lên, KHÔNG phải làm tròn về số chẵn)
LV = [(100, 5, 30), (101, 2, 3), (104, 25, 1), (108, 40, 26), (112, 3, 24), (120, 1, 23)]   # (tick, Bid, Ask)
# ngưỡng 22,4, w = 7, che 6. Đỏ: 104 (Bid 25) thua 108 (Bid 40) trong ±7 -> chỉ 108. Xanh: 100 (30), 108 (26), 120 (23) đạt; 112 (24) thua 108 (26).
# che: xanh 108 trùng đỏ 108 -> bỏ; xanh 100 cách 8, xanh 120 cách 12 -> giữ.
assert evaluate_bar(LV, 22.4, 7, 6) == ([100, 120], [108])
assert evaluate_bar(LV, 22.4, 7, 8) == ([120], [108])               # che 8: xanh 100 cách đỏ 108 đúng 8 -> bỏ
assert evaluate_bar(LV, 22.4, 3, 6) == ([120], [104, 108])          # w = 3: đỏ 104 và 108 cách 4 -> cả hai nổ; xanh 100, 108, 112 đều cách một chấm đỏ <= 6 -> bỏ
assert evaluate_bar([(100, 30, 0), (102, 30, 0)], 22.4, 4, 6) == ([], [])   # hai Bid bằng nhau trong cửa sổ: không ô nào "lớn hơn hẳn" -> không nổ
assert [nbase(m) for m in (1, 5, 15, 30, 60)] == [20, 20, 8, 5, 5]
# chuỗi nến: 5 nến nền giống nhau (trung vị ô = 4, biên độ = 12 tick) rồi 1 nến xét -> B = 4, R = 12 -> ngưỡng 11,2, w = 4, che 6
BASE = [(100 + i, 2, 2, 4) for i in range(13)]                      # (tick, Bid, Ask, volume)
TEST = [(100, 12, 1, 13), (103, 11, 0, 11), (105, 2, 15, 17), (112, 0, 20, 20)]
r = run_reference([BASE] * 5 + [TEST], N=20, **Q)
assert r[:5] == [None] * 5 and abs(r[5][0] - 11.2) < 1e-9 and r[5][1:] == (4, 6, [112], [100]), r[5]
# đỏ 100 (12 >= 11,2; 103 có 11 < 12). 103: 11 < 11,2. Xanh 105 (15) cách đỏ 100 là 5 <= 6 -> bỏ; xanh 112 giữ.
print('ví dụ nhỏ: ĐẠT')

r = run_reference([BASE] * 5 + [TEST], N=20)                       # bộ ưu tiên không sót: ngưỡng 8, w = 4, che 2
assert abs(r[5][0] - 8.0) < 1e-9 and r[5][1:] == (4, 2, [105, 112], [100]), r[5]   # đỏ 103 (11) thua 100 (12) trong ±4; xanh 105 cách đỏ 100 là 5 > 2 -> giữ
print('ví dụ nhỏ: ĐẠT')

# ---- (2) bản nhanh = bản chuẩn; (3) số chấm chuẩn ----
for pname, (U, preset) in UB.items():
    for sym, m in (('GC', 15), ('NQ', 30)):
        F, S = load(sym, m); thr, w, h = build(S, m, **U)
        fast = dots_fast(F, thr, w, h); a = set(zip(fast.t.values, fast.tk.values, fast.col.values))
        bars = [list(zip(g.tk.values.tolist(), g.bid.values.tolist(), g.ask.values.tolist(), g.vol.values.tolist())) for _, g in F.sort_values(['t', 'tk']).groupby('t', sort=True)]
        ts = np.sort(F.t.unique()); ref = run_reference(bars, N=nbase(m), **preset); b = set()
        for t, x in zip(ts, ref):
            if x is None: continue
            b |= {(t, tk, 'B') for tk in x[3]} | {(t, tk, 'S') for tk in x[4]}
        assert a == b, (pname, sym, m, len(a), len(b), len(a ^ b))
        fast.to_csv(f'dot_golden_{pname}_{sym}_M{m}.csv', index=False)
        print(f'{pname} {sym} M{m}: {len(a)} chấm, bản nhanh = bản chuẩn; ghi dot_golden_{pname}_{sym}_M{m}.csv')
    rows = []
    for sym in ('GC', 'NQ'):
        for m in TFS:
            F, S = load(sym, m); thr, w, h = build(S, m, **U); D = dots_fast(F, thr, w, h)
            rows.append(dict(bo=pname, ma=sym, khung=f'M{m}', nen=len(S), nen_co_nen=int(thr.notna().sum()), N=nbase(m), cham=len(D), do=int((D.col == 'S').sum()), xanh=int((D.col == 'B').sum())))
    print(pd.DataFrame(rows).to_string(index=False), flush=True)
