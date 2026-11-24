"""Tự kiểm phần Big Trade:
(1) các ví dụ nhỏ (đầu vào -> kết quả mong đợi) để viết unit test C#;
(2) bản nhanh numpy (simulate) trùng bản chuẩn từng nến (run_reference) trên nhật ký thật;
(3) ghi file chuẩn bt_golden_<mã>_M<khung>.csv (nến, tick, lệnh đơn, ngưỡng, khoảng gộp) để so C# = Python.
Chạy: python bt_selftest.py"""
import pandas as pd
from bt_rule import kth_threshold, merge_cap, merge_ticks, run_reference, simulate, round_half_up
from bt_common import load_m1, to_tf, bars_of
from common_window import nbase

DEFAULT = dict(density=1.0, floor=5, ceil=0, fixed=10, cap=3, div=8, gmin=2)

# ---- (1) ví dụ nhỏ ----
assert [nbase(m) for m in (1, 2, 5, 10, 15, 20, 30, 60, 240)] == [20, 20, 20, 12, 8, 6, 5, 5, 5] and nbase(0) == 20
assert [max(1, round_half_up(0.75 * n)) for n in (20, 12, 8, 6, 5)] == [15, 9, 6, 5, 4]        # K theo N khi mật độ 0,75 (mật độ 1,0 thì K = N)
# giá trị lớn thứ K trong gộp các top-K của các nến trước
assert kth_threshold([[12, 7, 3], [9, 2], [30]], 3) == 9.0          # gộp: 30 12 9 7 3 2 -> thứ 3 = 9
assert kth_threshold([[12], [9]], 3) == 0.0                         # chưa đủ 3 giá trị -> 0
# gộp vòng gần nhau (<= g tick) rồi giới hạn số vòng; thứ tự trả về: lệnh đơn giảm dần, hòa thì tick thấp trước
C = [(100, 20), (101, 30), (110, 20), (104, 25)]
assert merge_cap([(100, 20), (101, 30), (110, 20), (103, 25)], 2, 3) == [(101, 30), (110, 20)]   # 103 và 100 cách 101 <= 2 -> bỏ
assert merge_cap(C, 2, 3) == [(101, 30), (104, 25), (110, 20)]      # 104 cách 101 là 3 -> giữ; 100 bỏ
assert merge_cap(C, 2, 2) == [(101, 30), (104, 25)]                 # tối đa 2 vòng
assert merge_cap(C, 0, 0) == [(101, 30), (104, 25), (100, 20), (110, 20)]   # không gộp, không giới hạn
assert merge_cap([(105, 9), (100, 9), (103, 9)], 2, 0) == [(100, 9), (103, 9)]   # hòa: tick thấp trước; 105 cách 103 là 2 -> bỏ
# khoảng gộp theo biên độ nến TB
assert merge_ticks(3.6, 8, 2) == 2 and merge_ticks(183, 8, 2) == 23 and merge_ticks(20, 8, 2) == 3 and merge_ticks(0, 8, 2) == 2 and merge_ticks(50, 0, 2) == 2
# chuỗi 8 nến, N = 5, mật độ 0,6 (K = 3), sàn 5, cố định 10 khi chưa đủ 5 nến, tối đa 3 vòng, gộp max(2, R/8)
BARS = [[(100, 1), (101, 6), (102, 2)], [(100, 3), (104, 8)], [(99, 12), (100, 1)], [(101, 2), (102, 4)], [(100, 7), (103, 5), (110, 1)],
        [(100, 7), (101, 9), (102, 7), (105, 6), (108, 15), (109, 7)], [(100, 0), (101, 0)], [(100, 9), (103, 9), (106, 9), (109, 30)]]
EXPECT = [(10, 2, []), (10, 2, []), (10, 2, [(99, 12)]), (10, 2, []), (10, 2, []),
          (7.0, 2, [(108, 15), (101, 9)]),          # hàng đợi: 12 8 7 | 6 5 4 ... -> thứ 3 = 7; đạt: 108(15) 101(9) 100 102 109 (7); 100, 102 gộp vào 101; 109 gộp vào 108
          (9.0, 2, []),                             # nến không có số liệu lệnh đơn: không nổ, KHÔNG vào hàng đợi
          (9.0, 2, [(109, 30), (100, 9), (103, 9)])]   # hàng đợi (nến 1..5): 15 12 9 | 8 7 7 ... -> 9; 106 bị chặn bởi giới hạn 3 vòng
got = run_reference(BARS, N=5, density=0.6, floor=5, cap=3, div=8, gmin=2)
assert got == EXPECT, got
assert run_reference(BARS, N=5, density=0.6, floor=5, cap=3, div=2, gmin=2)[-1] == (9.0, 3, [(109, 30), (100, 9)])   # R TB = 5 -> g = round(2,5) = 3: 103 gộp vào 100; 106 cách 109 là 3 -> bỏ
assert run_reference(BARS, N=5, density=0.6, floor=8, cap=3, div=8, gmin=2)[5][0] == 8                                # sàn 8 > ngưỡng hạng K 7
assert run_reference(BARS, N=5, density=0.6, floor=5, ceil=6, cap=3, div=8, gmin=2)[5][0] == 6                        # trần 6 < 7
print('ví dụ nhỏ: ĐẠT')

# ---- (2)(3) bản nhanh = bản chuẩn, ghi file chuẩn ----
for key, m in (('NQ', 1), ('NQ', 15), ('GC', 5), ('GC', 30)):
    c = to_tf(load_m1(key), m); b = bars_of(c); N = nbase(m)
    fast, thr = simulate(c, b, N=N, **DEFAULT)
    bars = [list(zip(g.tk.values.tolist(), g.mot.values.tolist())) for _, g in c.groupby('t', sort=True)]
    ref = run_reference(bars, N=N, **DEFAULT)
    rows = [(t, tk, mot, th, g) for t, (th, g, kept) in zip(b.t.values, ref) for tk, mot in kept]
    R = pd.DataFrame(rows, columns=['t', 'tk', 'mot', 'thr', 'g']).sort_values(['t', 'tk']).reset_index(drop=True)
    a = set(zip(fast.t.values, fast.tk.values, fast.mot.values)); r = set(zip(R.t.values, R.tk.values, R.mot.values))
    assert a == r, (key, m, len(a), len(r), len(a ^ r))
    R.to_csv(f'bt_golden_{key}_M{m}.csv', index=False)
    print(f'{key} M{m}: N = {N}, {len(b)} nến, {len(R)} vòng, bản nhanh = bản chuẩn; ghi bt_golden_{key}_M{m}.csv')
