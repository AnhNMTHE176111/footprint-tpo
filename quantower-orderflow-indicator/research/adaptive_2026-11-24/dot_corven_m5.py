"""Câu B: 26 nến M5 của chart CORVEN 18/11 (GC, 12:15-14:20 UTC): luật chấm hiện tại so với công thức chung.
Nguồn ô: ../corven_m5_2026-11-18/F_m5.pkl (footprint M5 08-18/11). Chạy: python dot_corven_m5.py"""
import numpy as np, pandas as pd
from dot_rule import dots_fast, params_for
from dot_grid import build
F0 = pd.read_pickle('../corven_m5_2026-11-18/F_m5.pkl')
F = pd.DataFrame(dict(t=pd.to_datetime(F0.datetime), tk=np.round(F0.price / 0.1).astype(np.int64), bid=F0.bid, ask=F0.ask))
F['vol'] = F0.volume.values if 'volume' in F0 else (F0.vol.values if 'vol' in F0 else F.bid + F.ask); F = F[F.vol > 0]
S = F.groupby('t').agg(med=('vol', 'median'), hi=('tk', 'max'), lo=('tk', 'min')); S['rng'] = S.hi - S.lo
win = (S.index >= '2026-11-18 12:15') & (S.index <= '2026-11-18 14:20')
def run(name, thr, w, h):
    D = dots_fast(F, thr, w, h); D = D[(D.t >= '2026-11-18 12:15') & (D.t <= '2026-11-18 14:20')]
    print(f'{name}: {len(D)} chấm ({(D.col == "B").sum()} xanh + {(D.col == "S").sum()} đỏ) trên {win.sum()} nến; w trung vị {np.median(w[win]):.0f}, ngưỡng trung vị {np.median(thr[win]):.1f}')
    return set(zip(D.t, D.tk, D.col))
thr, w, h, _, _ = params_for(S, 2.8, 0, 4, hfix=6); a = run('hiện tại (2,8/±4/che 6/sàn 9, nền 20 nến)', thr, w, h)
thr, w, h = build(S, 5, k=2.8, wmode='lin', c=6, wmin=4, hmult=0.75, hmin=6, floor=9); b = run('công thức chung (2,8 · w=max(4,R/6) · che max(6; 0,75w) · sàn 9)', thr, w, h)
print(f'chung nhau {len(a & b)}, chỉ hiện tại {len(a - b)}, chỉ công thức chung {len(b - a)}')
m = pd.read_csv('../corven_m5_2026-11-18/marks_python_26bars.csv'); print('marks_python_26bars.csv (chuẩn cũ):', (m.type == 'dot').sum(), 'chấm')
