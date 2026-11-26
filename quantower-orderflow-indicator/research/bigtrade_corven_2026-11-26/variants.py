"""Do cac phuong an 'vong lon' so voi bong CO LON cua CORVEN (q >= 1.5). Fit nguong tren GC, kiem tren NQ_B va NQ_A.
Khop: cung nen, |vi tri GT - tam hang| <= 1 hang, mot-mot. 'du' KHONG tinh neu trung mot bong GT co q >= 1.25 (vung khong chac)."""
import pandas as pd, numpy as np, pickle, sys
from common import *
T = pickle.load(open(HERE + '/_rows.pkl', 'rb')); G = pd.read_csv(HERE + '/gt_bubbles.csv', parse_dates=['t_utc']); V = pd.read_csv(HERE + '/gt_visible.csv', parse_dates=['t_utc'])
SAMPLES = {'GC': 'GC', 'NQ_B': 'NQ', 'NQ_A': 'NQ'}
for s in list(T):
    d = T[s]; d['tot'] = d.bid + d.ask; d['mx'] = d[['bid', 'ask']].max(axis=1); d['mn'] = d[['bid', 'ask']].min(axis=1)
# Nen 'cham duoc' = nam trong khoang nhin thay VA (co it nhat 1 bong GT, hoac khong co hang nao ben lon >= 2 x nen):
# nen rat soi dong ma khong co bong nao tren anh la nen bi che / nam ngoai khung gia (CORVEN no cham tu ~1,3 x nen).
_ok = []
for smp, sym in SAMPLES.items():
    d = T[sym]; act = set(d[d.mx / d.Bm >= 2].t); has = set(G[G['sample'] == smp].t_utc)
    v = V[V['sample'] == smp]; _ok.append(v[v.t_utc.isin(has) | ~v.t_utc.isin(act)])
V = pd.concat(_ok)
def score(pred, sample, tol=1.0, scale=1.0, qbig=1.5, qsoft=1.25):
    """pred: DataFrame (t, k). scale: so tick moi hang cua pred / so tick moi hang GT (de so phuong an theo tick)."""
    vis = set(V[V['sample'] == sample].t_utc); g = G[G['sample'] == sample]; P = pred[pred.t.isin(vis)]
    hit = extra = miss = soft = 0; gb = {t: x for t, x in g.groupby('t_utc')}
    for t, p in P.groupby('t'):
        x = gb.get(t); cand = []
        if x is not None:
            for i, k in enumerate(p.k.values):
                c = (k + 0.5) * scale if scale == 1 else (k + 0.5) * scale   # vi tri theo don vi hang GT
                for j, (pos, q) in enumerate(zip(x.pos.values, x.q.values)):
                    if abs(pos - c) <= tol and q >= qsoft: cand.append((0 if q >= qbig else 1, abs(pos - c), i, j, q))
        cand.sort(); ui = set(); uj = set()
        for _, d, i, j, q in cand:
            if i in ui or j in uj: continue
            ui.add(i); uj.add(j)
            if q >= qbig: hit += 1
            else: soft += 1
        extra += len(p) - len(ui)
    miss = int((g.q >= qbig).sum()) - hit
    return hit, extra, miss, soft
def f1(h, e, m): return 2 * h / (2 * h + e + m) if h else 0.0
VAR = {
 'V1 tong hang / nen TB20': lambda d: d.tot / d.Bm,
 'V2 ben lon hang / nen TB20': lambda d: d.mx / d.Bm,
 'V3 ben lon hang / nen trung vi20': lambda d: d.mx / d.Bmed,
 'V4 ben lon hang, tuyet doi (hop dong)': lambda d: d.mx,
 'V5 tong hang / TB hang cua chinh nen': lambda d: d.tot / d.barmean,
 'V6 ben lon hang / nen TB120': lambda d: d.mx / d.B120,
 'V7 ben lon hang / nen TB5': lambda d: d.mx / d.B5,
 'V8 hang lon nhat nen & ben lon / TB20': lambda d: np.where(d.tot >= d.top, d.mx / d.Bm, 0),
 'V9 ben lon hang / (volume nen TB20)': lambda d: d.mx / d.Bvol * 20,
 'V10 tong hang, tuyet doi': lambda d: d.tot,
}
def grid(name):
    if 'tuyet doi' in name: return [10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 100, 120, 150]
    return [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7, 8, 10]
if __name__ == '__main__':
    rows = []
    for name, fn in VAR.items():
        best = None
        for K in grid(name):
            d = T['GC']; h, e, m, s = score(d[fn(d) >= K][['t', 'k']], 'GC')
            if best is None or f1(h, e, m) > best[0]: best = (f1(h, e, m), K, h, e, m, s)
        _, K, h, e, m, s = best; line = [name, K, 'GC %d/%d/%d (F1 %.2f)' % (h, e, m, f1(h, e, m))]; tot = np.array([h, e, m])
        for smp in ('NQ_B', 'NQ_A'):
            d = T['NQ']; K2 = K
            if 'tuyet doi' in name:   # tuyet doi: khong chuyen ma duoc -> fit rieng tren NQ_B (lac quan)
                K2 = max([10, 20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200, 250, 300], key=lambda k: f1(*score(d[fn(d) >= k][['t', 'k']], 'NQ_B')[:3]))
            h, e, m, s = score(d[fn(d) >= K2][['t', 'k']], smp); line.append('%s %d/%d/%d (F1 %.2f)%s' % (smp, h, e, m, f1(h, e, m), ' [K=%s fit rieng]' % K2 if K2 != K else '')); tot += [h, e, m]
        line.append('Tong %d/%d/%d F1 %.2f' % (*tot, f1(*tot))); rows.append(line); print(' | '.join(map(str, line)))
    # theo tung tick (khong gom hang)
    for sym, smp in (('GC', 'GC'), ('NQ', 'NQ_B'), ('NQ', 'NQ_A')):
        d = T[sym + '_tick']; n = ROWCFG[sym][0]; ph = ROWCFG[sym][1]; best = None
        for K in [2, 3, 4, 5, 6, 8, 10, 12, 15, 20]:
            p = d[d.mx / d.Bm >= K][['t', 'k']].copy(); p['k'] = (p.k + 0.5 - ph) / n - 0.5
            h, e, m, s = score(p, smp)
            if best is None or f1(h, e, m) > best[0]: best = (f1(h, e, m), K, h, e, m)
        print('V11 ben lon TUNG TICK / nen tick TB20 (fit rieng tung mau)', smp, best)
    pd.DataFrame(rows).to_csv(HERE + '/out_variants.csv', index=False, header=False)
