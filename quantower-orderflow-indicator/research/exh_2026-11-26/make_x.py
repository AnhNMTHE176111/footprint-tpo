"""Dựng lại X_GC.pkl / X_NQ.pkl (bảng đặc trưng theo hàng CORVEN) cho grid2.py, grid3.py. Chạy sau feats.py."""
from rowscan import get
for sym, G, off in (('GC', 2, 1), ('NQ', 8, 4)):
    get(sym, G, off).to_pickle(f'X_{sym}.pkl'); print(sym, 'xong')
