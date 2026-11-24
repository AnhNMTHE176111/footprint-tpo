import sys, os, numpy as np, pandas as pd
R = r'c:/Users/anhla/OneDrive/Documents/footprint-tpo/quantower-orderflow-indicator/research/stat_anomaly_2026-11-24'
sys.path.insert(0, R); os.chdir(R)
pd.set_option('display.width', 300); pd.set_option('display.max_colwidth', 90); pd.set_option('display.max_rows', 200)
S = pd.read_csv('out_r1_dot_summary.csv')
k = S[(S.doan == 'kiem') & S.cau_hinh.isin(['cung_gio_K10_lc_p2', 'cung_gio_K10_lc_p1', 'cung_gio_K10_lc_p0.5', 'cung_gio_K10_lc_lam2', 'cung_gio_K10_lc_lam1'])]
print(k[['cau_hinh', 'ma', 'khung', 'nen_chua_co_nguong', 'cham_nen', 'cham_nen_p95', 'cham_nen_max', 'khop_chung', 'khop_phien', 'khop_ngay']].to_string(index=False))
P = pd.read_csv('out_r1_dot_pick.csv'); print(P.columns.tolist())
print(P[P.cau_hinh.isin(['cung_gio_K10_lc_lam2', 'cung_gio_K10_lc_lam1', 'cung_gio_K10_lc_p2']) & P.khung.isin([1, 5, 15])].to_string(index=False))
# BT
sys.path.insert(0, os.path.join(R, '..', 'adaptive_2026-11-24'))
import bt_common as B
for nm in ('GC', 'NQ', 'GClive'):
    M = B.load_m1(nm)
    print(nm, type(M), getattr(M, 'shape', None)); print(M.head(3).to_string())
    t = pd.DatetimeIndex(M['t'] if 't' in M.columns else M.index)
    bars = pd.Series(1, index=pd.DatetimeIndex(sorted(set(t))))
    day = (bars.index + pd.Timedelta(hours=2)).normalize()
    c = bars.groupby(day).size()
    print(nm, 'so ngay', len(c), 'nen M1 moi ngay:', c.values.tolist())
    print(nm, 'gio co nen:', sorted(set(bars.index.hour)))
