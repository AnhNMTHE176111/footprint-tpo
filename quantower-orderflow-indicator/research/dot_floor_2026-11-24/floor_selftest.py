"""Spec cho C#: (1) ví dụ nhỏ cho unit test với sàn lấy từ ô người dùng; (2) bản nhanh = bản chuẩn từng nến (run_reference) trên GC M1 và NQ M1 với sàn 7;
(3) số chấm chuẩn (đỏ + xanh) theo sàn x bộ số trên GC M1, GC M15, NQ M1, NQ M15, NQ M30, cả khi bật "nổ ở mọi mức giá"; (4) số chấm theo ngày (out_golden_by_day.csv) để dò chỗ lệch.
Chạy: python floor_selftest.py"""
from floor_lib import *
def close(a, b): return a is not None and abs(a[0] - b[0]) < 1e-9 and a[1:] == b[1:]
# ---- (1) ví dụ nhỏ: unified(B, R, k, floor, hide_ratio, hide_min) -> (ngưỡng, w, h)
assert close(unified(2.75, 88, k=2.0, floor=7, hide_ratio=0.0, hide_min=2), (7.0, 15, 2))     # đoạn chart 24/11: 2,0 x 2,75 = 5,5 < sàn 7 -> ngưỡng 7; w = round(88/6 = 14,67) = 15
assert close(unified(2.75, 88, k=2.0, floor=9, hide_ratio=0.0, hide_min=2), (9.0, 15, 2))
assert close(unified(2.75, 88, k=2.0, floor=5, hide_ratio=0.0, hide_min=2), (5.5, 15, 2))     # lỗi cũ: sàn 5 của bộ số -> ngưỡng 5,5
assert close(unified(4.0, 20, k=2.0, floor=7, hide_ratio=0.0, hide_min=2), (8.0, 4, 2))       # k x B > sàn -> sàn không có tác dụng
assert close(unified(3.0, 16, k=2.8, floor=7, hide_ratio=0.75, hide_min=6), (8.4, 4, 6))      # bộ Ít nhiễu với sàn 7: 8,4 > 7
assert close(unified(2.0, 16, k=2.8, floor=7, hide_ratio=0.75, hide_min=6), (7.0, 4, 6))      # 5,6 < 7
assert close(unified(3.5, 30, k=2.0, floor=7, hide_ratio=0.0, hide_min=2), (7.0, 5, 2))       # 2,0 x 3,5 = 7,0 = sàn (bằng nhau)
assert close(unified(3.0, 16, k=2.0, floor=0, hide_ratio=0.0, hide_min=2), (6.0, 4, 2))       # tắt "Dùng sàn tối thiểu" -> sàn 0
# một nến: (tick, Bid, Ask). Chấm kiểu "Sell - 6 Bid (Ask 1)" ở tick 100.
LV = [(100, 6, 1), (101, 1, 2), (106, 2, 7), (112, 9, 0), (113, 3, 8), (120, 1, 6)]
assert evaluate_bar(LV, 5.5, 4, 2) == ([106, 120], [100, 112])   # ngưỡng 5,5: đỏ 100 (6), 112 (9); xanh 106 (7), 113 (8), 120 (6) đạt; xanh 113 cách đỏ 112 là 1 <= 2 -> bỏ
assert evaluate_bar(LV, 7.0, 4, 2) == ([106], [112])             # sàn 7: đỏ 100 (6 < 7) mất; xanh 120 (6) mất; xanh 106 (7 >= 7) giữ; xanh 113 vẫn bị đỏ 112 che
assert evaluate_bar(LV, 9.0, 4, 2) == ([], [112])                # sàn 9: chỉ còn đỏ 112 (9 >= 9); xanh 113 (8) không đạt
assert evaluate_bar(LV, 7.0, 0, 2) == ([106], [112])             # "nổ ở mọi mức giá" (w = 0): nến này không đổi
LV2 = [(100, 8, 0), (102, 9, 0), (103, 7, 0), (110, 0, 7)]
assert evaluate_bar(LV2, 7.0, 4, 2) == ([110], [102])            # w = 4: Bid 8 và 7 thua Bid 9 trong ±4 -> 1 chấm đỏ
assert evaluate_bar(LV2, 7.0, 0, 2) == ([110], [100, 102, 103])  # w = 0: cả ba ô Bid >= 7 đều nổ
# chuỗi nến: 5 nến nền (trung vị ô = 3, biên độ 12 tick) -> B = 3, R = 12 -> 2,0 x B = 6 < sàn 7 -> ngưỡng 7, w = 4, che 2
BASE = [(100 + i, 2, 1, 3) for i in range(13)]
TEST = [(100, 6, 1, 7), (105, 7, 0, 7), (112, 1, 6, 7), (118, 0, 9, 9)]
r = run_reference([BASE] * 5 + [TEST], N=20, k=2.0, floor=7, hide_ratio=0.0, hide_min=2)
assert r[:5] == [None] * 5 and close(r[5][:3], (7.0, 4, 2)) and r[5][3:] == ([118], [105]), r[5]
r = run_reference([BASE] * 5 + [TEST], N=20, k=2.0, floor=5, hide_ratio=0.0, hide_min=2)   # sàn 5 (lỗi cũ): ngưỡng 6 -> thêm đỏ 100 (6), xanh 112 (6)
assert close(r[5][:3], (6.0, 4, 2)) and r[5][3:] == ([112, 118], [100, 105]), r[5]
print('ví dụ nhỏ: ĐẠT')

# ---- (2) bản nhanh = bản chuẩn từng nến, sàn 7, bộ Không sót
for sym in ('GC', 'NQ'):
    F, S = load(sym, 1); D, _ = cands(F, S, 1, 'Không sót'); X = apply_floor(D, 7); a = set(zip(X.t.values, X.tk.values, X.col.values))
    F = F.sort_values(['t', 'tk']); cnt = F.groupby('t', sort=True).size().values; ends = np.cumsum(cnt); st = ends - cnt
    tk, bd, ak, vl = F.tk.values.tolist(), F.bid.values.tolist(), F.ask.values.tolist(), F.vol.values.tolist()
    bars = [list(zip(tk[s:e], bd[s:e], ak[s:e], vl[s:e])) for s, e in zip(st, ends)]
    ts = np.sort(F.t.unique()); ref = run_reference(bars, N=nbase(1), k=2.0, floor=7, hide_ratio=0.0, hide_min=2); b = set()
    for t, x in zip(ts, ref):
        if x is None: continue
        b |= {(t, q, 'B') for q in x[3]} | {(t, q, 'S') for q in x[4]}
    assert a == b, (sym, len(a), len(b), len(a ^ b)); print(f'{sym} M1 Không sót sàn 7: {len(a)} chấm, bản nhanh = bản chuẩn', flush=True)

# ---- (3) số chấm chuẩn
rows = []; byday = []
for sym, m in (('GC', 1), ('GC', 15), ('NQ', 1), ('NQ', 15), ('NQ', 30)):
    F, S = load(sym, m)
    for pn in PRESETS:
        for al in (False, True):
            D, thr = cands(F, S, m, pn, al)
            for f in (5, 7, 9, 12):
                X = apply_floor(D, f); nr = int((X.col == 'S').sum())
                rows.append(dict(ma=sym, khung=f'M{m}', bo=pn, moi_muc_gia=int(al), san=f, nen=len(S), cham=len(X), do=nr, xanh=len(X) - nr))
                if f == 7 and pn == 'Không sót' and not al:
                    g = X.groupby([X.t.dt.date, 'col']).size().unstack(fill_value=0)
                    for d, r in g.iterrows(): byday.append(dict(ma=sym, khung=f'M{m}', ngay=d, do=int(r.get('S', 0)), xanh=int(r.get('B', 0))))
R = pd.DataFrame(rows); R.to_csv('out_golden_counts.csv', index=False); pd.DataFrame(byday).to_csv('out_golden_by_day.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
R['s'] = R.cham.astype(str) + ' (' + R.do.astype(str) + ' + ' + R.xanh.astype(str) + ')'
for al in (0, 1):
    print(f'\n=== số chấm chuẩn: tổng (đỏ + xanh), nổ ở mọi mức giá = {"BẬT" if al else "tắt"}')
    print(R[R.moi_muc_gia == al].pivot_table(index=['ma', 'khung', 'bo'], columns='san', values='s', aggfunc='first', sort=False).to_string())
