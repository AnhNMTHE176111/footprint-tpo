import pandas as pd, numpy as np, pickle
from grid1 import f1
from base_scan import baselines
TT, SS = pickle.load(open('_bt.pkl', 'rb'))
def best(S, T, den, volb, As, Cs=(0, .6, .7, .75, .8, .85, .9, .95, 1.0, 1.1), Ws=(1, 2, 3), num=('s0', 's1', 's2'), agg='max'):
    vb = S.t.map(volb).values; vol = S.t.map(T.vol).values; d = S.t.map(den).values if hasattr(den, 'index') else den
    m = S[list(num)].max(1).values if agg == 'max' else S[list(num)].sum(1).values
    m3 = m / d; vr = vol / vb; y = S.y.values.astype(bool); res = []
    for a in As:
        for c in Cs:
            for w in Ws: res.append((f1(y, (m3 <= a) & (vr >= c) & (S.wick_r.values >= w)), a, c, w))
    r = max(res, key=lambda z: z[0][0]); return '%.3f tp%d fp%d fn%d a=%.3f c=%.2f w=%d' % (r[0] + r[1:])
if __name__ == '__main__':
    A = np.round(np.arange(0.15, 0.6, 0.025), 3)
    print('--- nen volume N thay doi, nen hang N=20 (mean)')
    for Nv in (5, 10, 14, 20, 30, 50):
        print(Nv, ' | '.join(s + ' ' + best(SS[s], TT[s], baselines(TT[s], 20, 'mean', 0)[0], baselines(TT[s], Nv, 'mean', 0)[1], A) for s in TT))
    print('--- nen hang N thay doi, nen volume N=20')
    for Nr in (5, 10, 14, 20, 30, 50):
        print(Nr, ' | '.join(s + ' ' + best(SS[s], TT[s], baselines(TT[s], Nr, 'mean', 0)[0], baselines(TT[s], 20, 'mean', 0)[1], A) for s in TT))
    print('--- mau so la chinh nen (vmean / vmax / vol), loc volume N=20')
    for nm, sc in (('vmean', 1), ('vmed', 1.4), ('vmax', .4), ('vol', .08)):
        print(nm, ' | '.join(s + ' ' + best(SS[s], TT[s], TT[s][nm], baselines(TT[s], 20, 'mean', 0)[1], np.round(A * sc, 4)) for s in TT))
    print('--- mau so = TB volume nen 20 nen (khong can so hang)')
    print(' | '.join(s + ' ' + best(SS[s], TT[s], baselines(TT[s], 20, 'mean', 0)[1], baselines(TT[s], 20, 'mean', 0)[1], np.round(A * .08, 4)) for s in TT))
    print('--- so hang xet: 1,2,3,4 (max) va tong 2,3')
    for num, agg in ((('s0',), 'max'), (('s0', 's1'), 'max'), (('s0', 's1', 's2'), 'max'), (('s0', 's1', 's2', 's3'), 'max'), (('s0', 's1'), 'sum'), (('s0', 's1', 's2'), 'sum')):
        print(num, agg, ' | '.join(s + ' ' + best(SS[s], TT[s], baselines(TT[s], 20, 'mean', 0)[0], baselines(TT[s], 20, 'mean', 0)[1], np.round(A * (1 if agg == 'max' else 2), 3), num=num, agg=agg) for s in TT))
