"""Bảng từng (nến, phía) của 4 mẫu: CORVEN có dấu (y), luật hiện tại (cur), luật đề xuất (new). Ghi out_compare_marks.csv + out_compare_summary.csv.
Tham số thứ nhất/thứ hai (tuỳ chọn): file marks do ref_rule.py ghi cho NQ và GC -> kiểm bản đọc CSV = bản pandas."""
import sys, pandas as pd
from eval_all import *
rows = []; summ = []
for sym in ('NQ', 'GC', 'GC18'):
    cur = cur_rule.current(S[sym], 20).rename(columns={'hit': 'cur'}); new = pred(sym).rename(columns={'hit': 'new'})
    g = G[G.sym == sym].merge(cur, left_on=['t_utc', 'side'], right_on=['t', 'side'], how='left').merge(new, on=['t', 'side'], how='left').merge(WT[sym], on=['t', 'side'], how='left')
    g[['cur', 'new']] = g[['cur', 'new']].fillna(0).astype(int); rows.append(g[['sample', 'sym', 't_utc', 'side', 'wick', 'y', 'cur', 'new']])
    for s, x in g.groupby('sample'):
        for nm in ('cur', 'new'):
            summ.append(dict(mau=s, so_nen=x.t_utc.nunique(), luat='hien tai' if nm == 'cur' else 'de xuat', CORVEN=int(x.y.sum()), minh=int(x[nm].sum()), trung=int((x.y & x[nm]).sum()), thua=int(((1 - x.y) & x[nm]).sum()), sot=int((x.y & (1 - x[nm])).sum())))
R = pd.concat(rows); R['vn'] = (R.t_utc + pd.Timedelta(hours=7)).dt.strftime('%m-%d %H:%M'); R.to_csv('out_compare_marks.csv', index=False)
Sm = pd.DataFrame(summ); Sm.to_csv('out_compare_summary.csv', index=False); print(Sm.to_string(index=False))
for s, x in R.groupby('sample'):
    print(s, 'DE XUAT thua:', ' '.join(x[(x.y == 0) & (x.new == 1)].apply(lambda r: r.vn[6:] + r.side, axis=1)), '| sot:', ' '.join(x[(x.y == 1) & (x.new == 0)].apply(lambda r: r.vn[6:] + r.side, axis=1)))
for sym, f in zip(('NQ', 'GC'), sys.argv[1:]):
    M = pd.read_csv(f, parse_dates=['t']); cli = set(zip(M.t, M.kind.str[-1]))
    P = pred(sym); t0 = P.t.min() + pd.Timedelta(hours=6); pp = {(t, s) for t, s, h in zip(P.t, P.side, P.hit) if h and t >= t0}; cli = {k for k in cli if t0 <= k[0] <= P.t.max()}
    print(sym, 'ref_rule doc CSV', len(cli), 'ban pandas', len(pp), 'lech', len(cli ^ pp))
