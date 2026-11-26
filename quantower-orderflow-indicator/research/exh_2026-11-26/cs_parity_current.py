"""So dấu kiệt sức luật HIỆN TẠI: C# (perf/Golden stophunt --marks, file marks_*.csv) với Python (cur_rule.current) trên các nến của mẫu."""
import sys, pandas as pd, cur_rule
G = cur_rule.gt_all(); S = cur_rule.load_sets()
for sym, f in (('NQ', sys.argv[1]), ('GC', sys.argv[2])):
    M = pd.read_csv(f, parse_dates=['t']); M = M[M.kind.isin(['exhT', 'exhB'])]
    cs = set(zip(M.t, M.kind.str[-1]))
    P = cur_rule.current(S[sym], 20); g = G[G.sym == sym]
    keys = set(zip(g.t_utc, g.side)); py = {(t, s) for t, s, h in zip(P.t, P.side, P.hit) if h and (t, s) in keys}; cs = cs & keys
    print(sym, 'nen-phia trong mau', len(keys), '| C#', len(cs), 'Python', len(py), 'chung', len(cs & py), 'chi C#', sorted(cs - py)[:5], 'chi Python', sorted(py - cs)[:5])
