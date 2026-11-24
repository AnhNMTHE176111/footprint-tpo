import pandas as pd, numpy as np
for m in (1, 5):
    for s in ('GC', 'NQ'):
        S = pd.read_pickle(f'S_{s}_m{m}.pkl')
        q = lambda c: S[c].quantile([.25, .5, .75]).round(1).tolist()
        print(f'{s} M{m}: nến {len(S)} | biên độ (tick) {q("rng")} | số mức/nến {q("nl")} | trung vị vol/mức {q("med")} | B_med {q("B_med")} | vol nến {q("tot")}')
