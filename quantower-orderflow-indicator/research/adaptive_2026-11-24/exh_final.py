"""Kiệt sức: luật đề xuất = luật hiện tại VÀ thêm điều kiện "đuôi mỏng so với đuôi của các nến trước":
  râu >= 3 tick;  S6 <= 1,1 x (volume TB mỗi ô, 20 nến trước)  [giữ nguyên]  VÀ  S6 <= c x trung vị S6 của N nến trước (cả đỉnh lẫn đáy, N = nbase(phút)).
In: khớp CORVEN (26 nến M5 GC 18/11: trùng / thừa / sót trên 11 dấu), dấu/nến theo mã x khung x phiên, trước / sau. Chạy: python exh_final.py"""
import numpy as np, pandas as pd
from exh_common import corven_gt, tail_base
from common_window import nbase
from bt_common import ses_of, SES, SES_VN
pd.set_option('display.width', 280)
G = corven_gt(full=True); gt = G['gt'].values; y = G['y'].values
A = lambda X: ((X.wick >= 3) & (X.S6 <= 1.1 * X.Bm20)).values
print('--- khớp CORVEN (26 nến M5 GC, 11 dấu)')
T = tail_base(G, 6, nbase(5))
ratio = (G.S6.values / T)[gt & y]; print('S6 / trung vị đuôi của 11 dấu CORVEN:', np.round(np.sort(ratio), 2))
for name, h in [('hiện tại', A(G))] + [(f'hiện tại VÀ S6 <= {c} x trung vị đuôi', A(G) & (G.S6.values <= c * T)) for c in (0.8, 0.9, 1.0, 1.2)]:
    h = h & gt; print(f'{name}: {h.sum()} dấu, trùng {(h & y).sum()}/11, thừa {(h & ~y).sum()}, sót {(y & gt & ~h).sum()}')
rows = []
for sym in ('GC', 'NQ'):
    for m in (1, 5, 15, 30, 60):
        X = pd.read_pickle(f'X_{sym}_m{m}.pkl'); X = X[X.Bm20.notna()].reset_index(drop=True); T = tail_base(X, 6, nbase(m)); ses = ses_of(pd.DatetimeIndex(X.t)); nb = X.t.nunique()
        for name, h in [('hiện tại', A(X))] + [(f'+ đuôi {c}', A(X) & (X.S6.values <= c * T)) for c in (0.8, 1.0, 1.2)]:
            per = pd.Series(h).groupby(X.t.values).sum()
            rows.append(dict(ma=sym, khung=f'M{m}', luat=name, **{SES_VN[s]: round(h[ses == s].sum() / X.t[ses == s].nunique(), 2) for s in SES}, dau_nen=round(h.sum() / nb, 2), dau=int(h.sum()),
                             nen_co_dau=f'{(per > 0).mean():.2f}', hai_dau=f'{(per == 2).mean():.2f}', nguong_cu_tv=round((1.1 * X.Bm20).median(), 1), duoi_tv=round(np.nanmedian(T), 1)))
R = pd.DataFrame(rows); R.to_csv('out_exh_final.csv', index=False); print(R.to_string(index=False))
