"""Kiệt sức, luật HIỆN TẠI (râu >= 3 tick, tổng bên soi 6 tick từ cực trị <= 1,1 x volume TB mỗi ô của 20 nến trước): dấu/nến theo mã x khung x phiên,
và vì sao nến rộng nổ nhiều: tỉ lệ phía nến có râu >= 3 tick, tỉ lệ đạt điều kiện mỏng. Chạy: python exh_now.py"""
import numpy as np, pandas as pd
from bt_common import ses_of, SES, SES_VN
pd.set_option('display.width', 250)
rows = []
for sym in ('GC', 'NQ'):
    for m in (1, 5, 15, 30, 60):
        X = pd.read_pickle(f'X_{sym}_m{m}.pkl'); X = X[X.Bm20.notna()]
        hit = (X.wick >= 3) & (X.S6 <= 1.1 * X.Bm20)
        nb = X.t.nunique(); ses = ses_of(pd.DatetimeIndex(X.t))
        r = dict(ma=sym, khung=f'M{m}', nen=nb, dau=int(hit.sum()), **{SES_VN[s]: round(hit[ses == s].sum() / (X.t[ses == s].nunique()), 2) for s in SES}, dau_nen=round(hit.sum() / nb, 2),
                 rau_ge3=f'{(X.wick >= 3).mean() * 100:.0f}%', mong_khi_co_rau=f'{hit.sum() / (X.wick >= 3).sum() * 100:.0f}%',
                 bien_do=X.rng.median(), rau_tv=X.wick.median(), S6_tv=X.S6.median(), nguong_tv=round((1.1 * X.Bm20).median(), 1), so0_tv=X.zeros.median(),
                 cuc_tri_bang0=f'{(X.S1 == 0).mean() * 100:.0f}%')
        rows.append(r)
print(pd.DataFrame(rows).to_string(index=False))
