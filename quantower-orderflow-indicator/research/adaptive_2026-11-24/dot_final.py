"""Câu B: bảng trước/sau của chấm theo mã x khung x phiên.
  (1) HIỆN TẠI; (2) hiện tại + cửa sổ nền theo khung; (3) CÔNG THỨC CHUNG = 2,8 x B, w = max(4, round(R/6)), che max(6, round(0,75 w)), sàn 9, nền N = min(20, max(5, round(120/phút)));
  (4) như (3) nhưng bội số 3,2 (nếu muốn NQ thưa như GC).
Chạy: python dot_final.py"""
import numpy as np, pandas as pd
from bt_common import ses_of, SES, SES_VN
from dot_measure import load, TFS
from dot_grid import build, nbase
from dot_rule import dots_fast, params_for
pd.set_option('display.width', 250)
U = dict(k=2.8, wmode='lin', c=6, wmin=4, hmult=0.75, hmin=6, floor=9)
def cur(sym, S, N=20): return (params_for(S, 2.8, 0, 4, hfix=6, N=N) if sym == 'GC' else params_for(S, 3.5, 14, 8, hfix=12, N=N))[:3]
rows = []
for sym in ('GC', 'NQ'):
    for m in TFS:
        F, S = load(sym, m)
        for name, (thr, w, h) in (('1 hiện tại', cur(sym, S)), ('2 hiện tại + nền theo khung', cur(sym, S, nbase(m))),
                                  ('3 chung, bộ ÍT NHIỄU (2,8 · sàn 9 · che max(6; 0,75w))', build(S, m, **U)), ('4 chung, bộ KHÔNG SÓT (2,0 · sàn 5 · che 2)', build(S, m, **dict(U, k=2.0, floor=5, hmult=0, hmin=2)))):
            ok = thr.notna(); D = dots_fast(F, thr, w, h)
            per = D.groupby('t').size().reindex(S.index[ok], fill_value=0); ses = ses_of(per.index)
            red = (D.col == 'S').sum() / ok.sum()
            mins = per.index.hour * 60 + per.index.minute
            rows.append(dict(ma=sym, khung=f'M{m}', luat=name, nen_nen=20 if name[0] == '1' else nbase(m), **{SES_VN[s]: round(per.values[ses == s].mean(), 2) for s in SES},
                             tat_ca=round(per.mean(), 2), do=round(red, 2), xanh=round(per.mean() - red, 2),
                             nen_co_cham='/'.join(f'{(per.values[ses == s] > 0).mean():.2f}' for s in SES), p95=int(per.quantile(.95)), mx=int(per.max()),
                             w='/'.join(f'{np.median(w[ok].values[ses == s]):.0f}' for s in SES), nguong='/'.join(f'{np.median(thr[ok].values[ses == s]):.0f}' for s in SES),
                             nen_1330=round(per[mins == 810].mean(), 2)))
        print(pd.DataFrame(rows[-4:]).to_string(index=False, header=(m == 1 and sym == 'GC')), flush=True)
pd.DataFrame(rows).to_csv('out_dot_final.csv', index=False)
