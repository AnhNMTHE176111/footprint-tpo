import sys, pandas as pd, numpy as np
import ref_rule, cur_rule
G = cur_rule.gt_all(); S = cur_rule.load_sets()
TUP = {k: ref_rule.to_tuples(v) for k, v in S.items()}
GRID = {'NQ': (8, 4), 'GC': (2, 1), 'GC18': (2, 1)}
MINW = {'NQ': 8, 'GC': 4, 'GC18': 4}     # râu (tick) đủ dài để tam giác CORVEN không bị thân nến che
def wick_tbl(sym):
    return pd.DataFrame([(b['t'], s, w) for b in S[sym] for s, w in (('T', b['h'] - max(b['o'], b['c'])), ('B', min(b['o'], b['c']) - b['l']))], columns=['t', 'side', 'wick'])
WT = {k: wick_tbl(k) for k in S}
def pred(sym, grid=None, **kw):
    g, off = grid or GRID[sym]; out = ref_rule.run(TUP[sym], g, off, **kw)
    return pd.DataFrame([(b['t'], s, int(v)) for b, (tp, bt) in zip(S[sym], out) for s, v in (('T', tp), ('B', bt))], columns=['t', 'side', 'hit'])
def score(P, sym, reliable=False):
    g = G[G.sym == sym].merge(P, left_on=['t_utc', 'side'], right_on=['t', 'side'], how='left').merge(WT[sym], on=['t', 'side'], how='left'); g['hit'] = g.hit.fillna(0).astype(int)
    if reliable: g = g[(g.wick >= MINW[sym]) | (g.y == 1)]
    return {s: (int(x.y.sum()), int(x.hit.sum()), int((x.y & x.hit).sum()), int(((1 - x.y) & x.hit).sum()), int((x.y & (1 - x.hit)).sum())) for s, x in g.groupby('sample')}
if __name__ == '__main__':
    print('mau: (CORVEN, minh, trung, thua, sot)')
    for sym in ('NQ', 'GC', 'GC18'):
        cur = cur_rule.current(S[sym], 20); new = pred(sym)
        print(sym, 'HIEN TAI', score(cur, sym), '| rau du dai', score(cur, sym, True))
        print(sym, 'DE XUAT ', score(new, sym), '| rau du dai', score(new, sym, True))
    for grid in ((1, 0), (2, 0), (2, 1), (3, 0), (4, 0), (5, 0), (10, 0)):
        for a in (.25, .33, .4, .5):
            print('GC M5 hang', grid, 'A', a, score(pred('GC18', grid, a=a), 'GC18'), 'C=0:', score(pred('GC18', grid, a=a, cmin=0), 'GC18'), 'C=0,w=1:', score(pred('GC18', grid, a=a, cmin=0, wick_rows=1), 'GC18'))
