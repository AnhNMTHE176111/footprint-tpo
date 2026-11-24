"""Mật độ chấm theo phiên (giờ UTC): Á 23-07, Âu 07-13:30, Mỹ 13:30-20. So GC (2.8/4/6) với NQ (3.5/8/12) trên M5."""
import pandas as pd, numpy as np
from dots import dots
def ses(t):
    h = t.hour + t.minute/60
    return 'My' if 13.5 <= h < 20 else ('Au' if 7 <= h < 13.5 else 'A')
for s, k, w, h in (('GC', 2.8, 4, 6), ('NQ', 3.5, 8, 12), ('NQ', 2.8, 4, 6)):
    F = pd.read_pickle(f'F_{s}_m5.pkl'); S = pd.read_pickle(f'S_{s}_m5.pkl'); S = S[S.B_med.notna()]
    R = dots(F, k, w, 9, h)
    per = R.groupby('t').size().reindex(S.index, fill_value=0)
    g = pd.Series([ses(t) for t in S.index], index=S.index)
    print(s, k, w, h, {x: round(per[g == x].mean(), 2) for x in ('A', 'Au', 'My')})
