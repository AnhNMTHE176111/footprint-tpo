"""Dac trung tung HANG cua moi nen nhin thay trong mau (kem nen), luu _rows.pkl. Dung cho variants.py."""
import pandas as pd, numpy as np, pickle
from common import *
def rows_table(sym, t0, t1, need, n=None, ph=None, mins=1):
    """need: set thoi gian nen can xuat. -> DataFrame moi hang cua cac nen do."""
    bars, tick, n, ph = load_rows(sym, t0, t1, n, ph, mins); out = []
    st = []   # moi nen: (mean row vol, median row vol, tong vol, so hang)
    for i, b in enumerate(bars):
        rv = [x[0] + x[1] for x in b['rows'].values()]
        if b['t'] in need and i >= 5:
            p20 = st[-20:]; p120 = st[-120:]; p5 = st[-5:]
            Bm = np.mean([s[0] for s in p20]); Bmed = np.mean([s[1] for s in p20]); B120 = np.mean([s[0] for s in p120]); B5 = np.mean([s[0] for s in p5]); Bvol = np.mean([s[2] for s in p20])
            top = max(rv); barmean = np.mean(rv)
            for k, (bd, ak) in b['rows'].items():
                out.append((b['t'], k, bd, ak, Bm, Bmed, B120, B5, Bvol, top, barmean, sum(rv), len(rv)))
        st.append((np.mean(rv), np.median(rv), sum(rv), len(rv)))
    return pd.DataFrame(out, columns=['t', 'k', 'bid', 'ask', 'Bm', 'Bmed', 'B120', 'B5', 'Bvol', 'top', 'barmean', 'barvol', 'nrows'])
if __name__ == '__main__':
    V = pd.read_csv(HERE + '/gt_visible.csv', parse_dates=['t_utc']); T = {}
    for sym in ('GC', 'NQ'):
        need = set(V[V.sym == sym].t_utc); T[sym] = rows_table(sym, '2026-11-04', '2026-11-07 12:00', need)
        T[sym + '_tick'] = rows_table(sym, '2026-11-04', '2026-11-07 12:00', need, n=1, ph=0)
        print(sym, len(T[sym]), T[sym].t.nunique())
    pickle.dump(T, open(HERE + '/_rows.pkl', 'wb'))
