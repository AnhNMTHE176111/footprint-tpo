"""Chấm: mật độ toàn bộ dữ liệu của bộ trung gian (2,4 · sàn 5 · che 2 tick). Chạy: python dot_mid.py"""
import pandas as pd
from dot_measure import load, TFS
from dot_grid import build
from dot_rule import dots_fast
from bt_common import ses_of, SES, SES_VN
rows = []
for sym in ('GC', 'NQ'):
    for m in TFS:
        F, S = load(sym, m); thr, w, h = build(S, m, k=2.4, wmode='lin', c=6, wmin=4, hmult=0, hmin=2, floor=5); ok = thr.notna(); D = dots_fast(F, thr, w, h)
        per = D.groupby('t').size().reindex(S.index[ok], fill_value=0); ses = ses_of(per.index)
        rows.append(dict(ma=sym, khung=f'M{m}', **{SES_VN[s]: round(per.values[ses == s].mean(), 2) for s in SES}, tat_ca=round(per.mean(), 2), cham=len(D), do=int((D.col == 'S').sum()), xanh=int((D.col == 'B').sum())))
print(pd.DataFrame(rows).to_string(index=False))
