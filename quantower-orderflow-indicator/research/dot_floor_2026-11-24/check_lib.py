"""Tự kiểm floor_lib: cands + apply_floor phải ra đúng số chấm chuẩn của ../adaptive_2026-11-24 (mục 6.2):
GC M1 không sót (sàn 5) 80.386; ít nhiễu (sàn 9) 39.918; NQ M15 không sót 11.061; ít nhiễu 5.118; NQ M30 5.722 / 2.652."""
from floor_lib import *
exp = {('GC', 1): (80386, 39918), ('NQ', 15): (11061, 5118), ('NQ', 30): (5722, 2652), ('GC', 15): (10238, 4747), ('NQ', 1): (106953, 47895)}
for (sym, m), (a, b) in exp.items():
    F, S = load(sym, m)
    D, _ = cands(F, S, m, 'Không sót'); x = len(apply_floor(D, 5))
    D, _ = cands(F, S, m, 'Ít nhiễu'); y = len(apply_floor(D, 9))
    print(sym, m, x, a, y, b, 'ĐẠT' if (x, y) == (a, b) else 'LỆCH'); assert (x, y) == (a, b)
