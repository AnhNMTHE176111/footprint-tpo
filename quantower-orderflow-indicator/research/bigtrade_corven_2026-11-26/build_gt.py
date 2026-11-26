"""raw_bubbles.csv -> gt_bubbles.csv (khu trung giua cac khung chong thoi gian) + gt_visible.csv.
q = r / (trung vi r cua khung)  = co bong so voi cham thuong (cham thuong q ~ 1). 'big' = q >= QBIG."""
import pandas as pd, numpy as np
from common import *
QBIG = 1.5
R = pd.read_csv(HERE + '/raw_bubbles.csv', parse_dates=['t_utc']); V = pd.read_csv(HERE + '/raw_visible.csv', parse_dates=['t_utc'])
R['r0'] = R.groupby('frame').r.transform('median'); R['q'] = R.r / R.r0
R['sample'] = np.where(R.frame == 'IMG13', 'NQ_A', np.where(R.sym == 'NQ', 'NQ_B', 'GC'))
V['sample'] = np.where(V.frame == 'IMG13', 'NQ_A', np.where(V.sym == 'NQ', 'NQ_B', 'GC'))
tick = {'GC': 0.1, 'NQ': 0.25}
R['pos'] = [(p / tick[s] + 0.5 - ROWCFG[s][1]) / ROWCFG[s][0] for p, s in zip(R.price, R.sym)]   # vi tri theo don vi hang (k + 0.5 = tam hang k)
R = R.sort_values('q', ascending=False); keep = []
for r in R.itertuples():
    if any(k.sample == r.sample and k.t_utc == r.t_utc and k.color == r.color and abs(k.pos - r.pos) <= 0.75 for k in keep if k.t_utc == r.t_utc): continue
    keep.append(r)
G = pd.DataFrame(keep).drop(columns=['Index']).sort_values(['sample', 't_utc', 'pos']); G['big'] = G.q >= QBIG
G[['sample', 'sym', 'frame', 't_utc', 'vn', 'color', 'price', 'pos', 'r', 'q', 'big']].round(3).to_csv(HERE + '/gt_bubbles.csv', index=False)
V.drop_duplicates(['sample', 't_utc'])[['sample', 'sym', 't_utc']].to_csv(HERE + '/gt_visible.csv', index=False)
if __name__ == '__main__':
    print(G.groupby(['sample', 'color']).agg(n=('q', 'size'), big=('big', 'sum')).unstack().to_string()); print(V.drop_duplicates(['sample', 't_utc']).groupby('sample').size())
    print(np.histogram(G.q, bins=[0, .8, 1, 1.2, 1.35, 1.5, 1.75, 2, 2.5, 3, 4, 6]))
