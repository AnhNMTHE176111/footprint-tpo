"""Mật độ dấu kiệt sức mỗi nến trên toàn bộ dữ liệu 90 ngày: luật hiện tại và luật đề xuất, M1 / M5 / M15."""
import sys, numpy as np, pandas as pd, data, ref_rule, cur_rule
sys.path.insert(0, '../adaptive_2026-11-24'); from common_window import nbase
ref_rule.A, ref_rule.C = 0.35, 0.80
rows = []
for sym in ('NQ', 'GC'):
    G, off = ref_rule.GRID[sym]
    for m in (1, 5, 15):
        bars, _ = data.load(sym, mins=m); N = nbase(m)
        cur = cur_rule.current(bars, N); new = ref_rule.run(ref_rule.to_tuples(bars), G, off, n=N, a=0.35, cmin=0.80, wick_rows=2)
        nc = int(cur.hit.sum()); nn = sum(int(a) + int(b) for a, b in new); nb = len(bars)
        both = sum(1 for a, b in new if a and b)
        rows.append((sym, m, nb, nc, round(nc / nb, 3), nn, round(nn / nb, 3), round(nc / max(1, nn), 1)))
        print(rows[-1], flush=True)
pd.DataFrame(rows, columns=['ma', 'phut', 'so_nen', 'dau_hien_tai', 'hien_tai_moi_nen', 'dau_de_xuat', 'de_xuat_moi_nen', 'giam_lan']).to_csv('out_density.csv', index=False)
