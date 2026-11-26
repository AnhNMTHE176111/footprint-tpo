import pandas as pd, numpy as np, sys
from common import *
R = pd.read_csv('raw_bubbles.csv', parse_dates=['t_utc'])
def build(coef, off=0.0, save=False):
    out = []
    for sym in ('GC', 'NQ'):
        bars, tick, n, ph = load_rows(sym, '2026-11-04', '2026-11-07 12:00')
        idx = {b['t']: i for i, b in enumerate(bars)}
        for r in R[R.sym == sym].itertuples():
            i = idx.get(r.t_utc)
            if i is None: continue
            b = bars[i]; price = r.price + coef * r.r / r.px_per_unit + off * n * tick
            tkf = price / tick + 0.5; k = int(np.floor((tkf - ph) / n)); frac = (tkf - ph) / n - k   # +0.5: tick tk chiem [tk-0.5, tk+0.5]
            rw = b['rows']; g = lambda kk: rw.get(kk, [0, 0])
            prev = bars[max(0, i - 20):i]
            base = np.mean([np.mean([sum(v) for v in p['rows'].values()]) for p in prev]) if prev else np.nan
            out.append(dict(frame=r.frame, sym=sym, t=r.t_utc, color=r.color, r=r.r, rs=r.r / r.s, k=k, frac=round(frac, 2), bid=g(k)[0], ask=g(k)[1],
                            volU=sum(g(k + 1)), volD=sum(g(k - 1)), base=base, barvol=b['vol'].sum(), nrows=len(rw), barmax=max(sum(v) for v in rw.values()), i=i))
    F = pd.DataFrame(out); F['vol'] = F.bid + F.ask
    return F
if __name__ == '__main__':
    for coef in (0, 0.15, 0.3, 0.45, 0.6):
        F = build(coef); s = []
        for sym in ('GC', 'NQ'):
            f = F[F.sym == sym]; v = f[f.color == 'V']
            s.append('%s frac %s | V: vol>=max(U,D) %.2f, medvol %.0f, spear(r,vol) %.2f | empty rows %.3f' % (sym, np.histogram(f.frac, bins=5, range=(0, 1))[0], ((v.vol >= v.volU) & (v.vol >= v.volD)).mean(), v.vol.median(), v.r.corr(v.vol, method='spearman'), (f.vol == 0).mean()))
        print(coef, ' || '.join(s))
