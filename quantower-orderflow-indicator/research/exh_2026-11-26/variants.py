"""Đo độ khớp của các phương án luật trên 4 mẫu CORVEN (trùng / thừa / sót). Ghi out_variants.csv."""
import pandas as pd, numpy as np, data, feats, cur_rule
from split import enrich
G = cur_rule.gt_all(); S = cur_rule.load_sets()
GRID = {'NQ': (8, 4), 'GC': (2, 1), 'GC18': (2, 1)}
def table(sym, g, off):
    X = feats.build(sym, g, off, bars=S[sym]); gg = G[G.sym == sym]
    X = X.merge(gg[['t_utc', 'side', 'y', 'sample']], left_on=['t', 'side'], right_on=['t_utc', 'side'], how='left')
    X = enrich(X); X['wick_g'] = X.wick / g
    # dấu của nến liền trước cùng phía (để thử "một dấu mỗi nhóm nến") tính sau trong từng phương án
    return X
ROW = {s: table(s, *GRID[s]) for s in GRID}; TICK = {s: table(s, 1, 0) for s in GRID}
CUR = {s: cur_rule.current(S[s], 20) for s in GRID}
def prop(X, a=.35, c=.8, w=2): return (X.r012 <= a) & (X.vol_rel >= c) & (X.wick_r >= w)
VAR = {
 '0. Hiện tại (từng tick: râu >= 3 tick, tổng 6 tick <= 1,1 x nền, <= 0,8 x trung vị đuôi)': None,
 '1. Hiện tại nhưng đổi tick thành hàng (râu >= 3 hàng, tổng 6 hàng <= 1,1 x nền hàng)': lambda X, T: (X.wick_r >= 3) & (X.cs6 <= 1.1 * X.Bmean),
 '2. Hàng cực trị bằng 0 (râu >= 2 hàng)': lambda X, T: (X.s0 == 0) & (X.wick_r >= 2),
 '3. Giảm dần về cực trị: S0 <= S1 <= S2 và S0 <= 0,35 x nền (râu >= 2 hàng)': lambda X, T: (X.inc == 1) & (X.r0 <= .35) & (X.wick_r >= 2),
 '4. 3 hàng sát cực trị đều <= 0,35 x nền hàng (râu >= 2 hàng), KHÔNG lọc volume': lambda X, T: (X.r012 <= .35) & (X.wick_r >= 2),
 '5. Như 4 nhưng so với chính nến: 3 hàng <= 0,35 x volume TB mỗi hàng của nến': lambda X, T: (X.ms3 <= .35 * X.v_mean) & (X.wick_r >= 2),
 '6. Như 5 + volume nến >= 0,8 x TB 20 nến': lambda X, T: (X.ms3 <= .35 * X.v_mean) & (X.wick_r >= 2) & (X.vol_rel >= .8),
 '7. ĐỀ XUẤT: 3 hàng <= 0,35 x nền hàng + volume nến >= 0,8 x TB 20 nến + râu >= 2 hàng': lambda X, T: prop(X),
 '8. Đề xuất nhưng tính theo từng tick (không gom hàng)': lambda X, T: prop(T),
 '9. Đề xuất với 2 hàng': lambda X, T: (X.r01 <= .35) & (X.vol_rel >= .8) & (X.wick_r >= 2),
 '10. Đề xuất với 4 hàng': lambda X, T: (X[['r0', 'r1', 'r2', 'r3']].max(1) <= .35) & (X.vol_rel >= .8) & (X.wick_r >= 2),
 '11. Đề xuất nhưng TỔNG 3 hàng <= 0,7 x nền (thay vì từng hàng)': lambda X, T: (X.rc3 <= .7) & (X.vol_rel >= .8) & (X.wick_r >= 2),
 '12. Đề xuất + chỉ ở đỉnh/đáy cục bộ (cực trị vượt 3 nến trước)': lambda X, T: prop(X) & (X.hh3 == 1),
 '13. Đề xuất + bỏ dấu nếu nến sau quét qua ngay': lambda X, T: prop(X) & (X.nxt_sweep != 1),
 '14. Đề xuất râu >= 1 hàng': lambda X, T: prop(X, w=1),
 '15. Đề xuất râu >= 3 hàng': lambda X, T: prop(X, w=3),
 '16. Đề xuất A = 0,30 / C = 0,80': lambda X, T: prop(X, a=.30),
 '17. Đề xuất A = 0,35 / C = 0,90': lambda X, T: prop(X, c=.90),
}
rows = []
for name, fn in VAR.items():
    r = dict(phuong_an=name); TP = FP = FN = 0
    for sym in GRID:
        X = ROW[sym]; T = TICK[sym]
        if fn is None:
            h = X[['t', 'side']].merge(CUR[sym], on=['t', 'side'], how='left').hit.fillna(0).values.astype(bool)
        else: h = np.asarray(fn(X, T)).astype(bool)
        for smp, idx in X.groupby('sample').groups.items():
            y = X.loc[idx, 'y'].values.astype(bool); hh = h[X.index.get_indexer(idx)]
            tp = int((y & hh).sum()); fp = int((~y & hh).sum()); fn_ = int((y & ~hh).sum()); TP += tp; FP += fp; FN += fn_
            r[smp] = f'{int(y.sum())}/{tp + fp}/{tp}/{fp}/{fn_}'
    r['tong_trung'] = TP; r['tong_thua'] = FP; r['tong_sot'] = FN; r['F1'] = round(2 * TP / max(1, 2 * TP + FP + FN), 3); rows.append(r)
R = pd.DataFrame(rows)[['phuong_an', 'NQ_A', 'NQ_B', 'GC', 'GC_M5', 'tong_trung', 'tong_thua', 'tong_sot', 'F1']]
R.to_csv('out_variants.csv', index=False, encoding='utf-8-sig')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 95); print(R.to_string(index=False))
