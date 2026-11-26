"""Chọn tham số luật đề xuất: lưới A x C x râu, điểm F1 gộp; kiểm chéo bỏ từng mẫu."""
import itertools, pandas as pd, numpy as np, pickle, os
from eval_all import *
SAMPLES = [('NQ', 'NQ_A'), ('NQ', 'NQ_B'), ('GC', 'GC'), ('GC18', 'GC_M5')]
AS = (.25, .28, .30, .33, .35, .38, .40, .45); CS = (0, .6, .7, .75, .8, .85, .9, .95, 1.0); WS = (1, 2, 3)
if os.path.exists('_tune.pkl'): R = pickle.load(open('_tune.pkl', 'rb'))
else:
    R = {}
    for a, c, w in itertools.product(AS, CS, WS):
        for sym in ('NQ', 'GC', 'GC18'):
            for s, v in score(pred(sym, a=a, cmin=c, wick_rows=w), sym).items(): R[(a, c, w, s)] = v
    pickle.dump(R, open('_tune.pkl', 'wb'))
def f1(keys, p):
    tp = sum(R[p + (s,)][2] for s in keys); fp = sum(R[p + (s,)][3] for s in keys); fn = sum(R[p + (s,)][4] for s in keys)
    return 2 * tp / max(1, 2 * tp + fp + fn)
names = [s for _, s in SAMPLES]; P = list(itertools.product(AS, CS, WS))
allb = sorted(P, key=lambda p: -np.mean([f1([s], p) for s in names]))
print('TOP theo F1 trung binh 4 mau:')
for p in allb[:12]: print('  ', p, 'F1 tb %.3f' % np.mean([f1([s], p) for s in names]), ' '.join('%s %s' % (s, R[p + (s,)]) for s in names))
print('KIEM CHEO bo tung mau (chon tren 3 mau con lai, cham tren mau bo ra):')
for s in names:
    rest = [x for x in names if x != s]; p = max(P, key=lambda p: np.mean([f1([x], p) for x in rest]))
    print('  bo', s, 'chon', p, '-> mau bo ra', R[p + (s,)], 'F1 %.3f' % f1([s], p))
print('DE XUAT (0.33, 0.85, 2):', ' '.join('%s %s F1 %.2f' % (s, R[(.33, .85, 2, s)], f1([s], (.33, .85, 2))) for s in names))
