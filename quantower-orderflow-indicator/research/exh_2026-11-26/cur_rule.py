"""Luật kiệt sức HIỆN TẠI (ExhaustionLogic.cs + OrderFlowBubbles.cs 2026-11-24): bản Python = adaptive_2026-11-24/exh_rule.py run_reference."""
import sys, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../adaptive_2026-11-24'))
from exh_rule import run_reference
import data

def current(bars, N=20):
    bb = [(b['o'], b['h'], b['l'], b['c'], list(zip(b['tk'].tolist(), b['bid'].tolist(), b['ask'].tolist(), b['vol'].tolist()))) for b in bars]
    out = run_reference(bb, N)
    return pd.DataFrame([(b['t'], s, int(v)) for b, (tp, bt) in zip(bars, out) for s, v in (('T', tp), ('B', bt))], columns=['t', 'side', 'hit'])

def score(gt, pred, label=''):
    m = gt.merge(pred, left_on=['t_utc', 'side'], right_on=['t', 'side'], how='left'); m['hit'] = m.hit.fillna(0).astype(int)
    res = {}
    for s, g in m.groupby('sample'):
        tp = int((g.y & g.hit).sum()); fp = int(((1 - g.y) & g.hit).sum()); fn = int((g.y & (1 - g.hit)).sum())
        res[s] = (int(g.y.sum()), int(g.hit.sum()), tp, fp, fn)
    return res

def gt_all():
    g = pd.read_csv(os.path.join(HERE, 'gt_sides.csv'), parse_dates=['t_utc'])
    # GC M5 18/11: 26 nến, 11 dấu
    TOP = {'12:35', '12:45', '12:50', '13:30', '13:45'}; BOT = {'12:15', '13:10', '13:20', '13:40', '13:45', '13:50'}
    r = []
    for t in pd.date_range('2026-11-18 12:15', '2026-11-18 14:20', freq='5min'):
        k = t.strftime('%H:%M'); r.append(('GC18', t, 'T', 1, int(k in TOP), int(k in TOP), 'GC_M5')); r.append(('GC18', t, 'B', 1, int(k in BOT), int(k in BOT), 'GC_M5'))
    return pd.concat([g, pd.DataFrame(r, columns=g.columns)])

def load_sets():
    """Nến cho từng mã quanh các mẫu (có đủ lịch sử trước)."""
    return {'NQ': data.load('NQ', '2026-11-05 12:00', '2026-11-06 16:00')[0], 'GC': data.load('GC', '2026-11-04 12:00', '2026-11-06 14:00')[0], 'GC18': data.load('GC18', '2026-11-17 00:00', '2026-11-18 15:00')[0]}

if __name__ == '__main__':
    G = gt_all(); S = load_sets()
    for sym, N in (('NQ', 20), ('GC', 20), ('GC18', 20)):
        P = current(S[sym], N); print(sym, score(G[G.sym == sym], P))
