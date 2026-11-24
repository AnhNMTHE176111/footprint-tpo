import pandas as pd, numpy as np
from dots import dots
def run(s, m, k, w, fl, h):
    F = pd.read_pickle(f'F_{s}_m{m}.pkl'); S = pd.read_pickle(f'S_{s}_m{m}.pkl')
    n = S.B_med.notna().sum()
    R = dots(F, k, w, fl, h, key=(s, m))
    per = R.groupby('t').size().reindex(S.index[S.B_med.notna()], fill_value=0)
    return dict(sym=s, M=m, k=k, w=w, floor=fl, h=h, dots_bar=round(len(R)/n, 2), red=round((R.col=='S').sum()/n, 2), blue=round((R.col=='B').sum()/n, 2),
                pct_bar_co_cham=round((per > 0).mean()*100), p90=int(per.quantile(.9)), floor_bind=round((2.8*F.B_med < fl).mean()*100))
rows = []
for m in (5, 1):
    rows.append(run('GC', m, 2.8, 4, 9, 6))
    for w, h in ((4, 6), (8, 12), (11, 16), (14, 20)):
        for k in (2.8, 3.5):
            rows.append(run('NQ', m, k, w, 9, h))
print(pd.DataFrame(rows).to_string(index=False))
