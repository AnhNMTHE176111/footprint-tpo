#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval5.py — so cách vào lệnh / biến thể: python eval5.py VONG [loc]
Chỉ số chính: R 1:2 TRUNG BÌNH MỖI LẦN QUAY LẠI (không khớp = 0) — gộp cả 'khớp nhiều hơn' lẫn 'R mỗi lệnh'.
Δ = thật − đối chứng; [5–95 %] bootstrap theo phiên."""
import os, sys, tempfile
import numpy as np, pandas as pd
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
v = sys.argv[1]; loc = sys.argv[2] if len(sys.argv) > 2 else None
ENTRIES = [('0', 'mép'), ('0.1', '+0,1U'), ('0.2', '+0,2U'), ('0.3', '+0,3U'), ('b', 'đệm/râu')]

def ev(g, e):
    return np.where(g['fill' + e] == 1, g['r2_' + e].fillna(0), 0.0)

def delta_ci(g, e, B=600, seed=5):
    g = g.assign(x=ev(g, e))
    by = {d: (x[x.typ == 'that']['x'].values, x[x.typ == 'doi']['x'].values) for d, x in g.groupby(['sym', 'day'])}
    keys = list(by); rs = np.random.RandomState(seed); out = []
    for _ in range(B):
        ks = [keys[i] for i in rs.randint(0, len(keys), len(keys))]
        a = np.concatenate([by[k][0] for k in ks]); b = np.concatenate([by[k][1] for k in ks])
        out.append(a.mean() - b.mean())
    return np.percentile(out, [5, 95])

def ld(s):
    d = pd.read_pickle(os.path.join(CDIR, 'bt5_%s_%s.pkl' % (s, v))); d['sym'] = s; return d
df = pd.concat([ld('nqy'), ld('gc')], ignore_index=True)
if loc: df = df.query(loc)
print('### %s %s — R 1:2 mỗi lần quay lại: thật / đối chứng / Δ [5–95 %%]' % (v, loc or ''))
print('| tập | loại | n thật | ' + ' | '.join(n for _, n in ENTRIES) + ' |'); print('|' + '---|' * (3 + len(ENTRIES)))
for nm, m in (('NQ TRAIN', (df.sym == 'nqy') & (df.tap == 'TRAIN')), ('NQ TEST', (df.sym == 'nqy') & (df.tap == 'TEST')),
              ('GC (cả kỳ)', df.sym == 'gc'), ('NQ + GC', df.sym.notna())):
    for k, kn in (('z', 'vùng mạnh'), ('b', 'hộp HVN')):
        g = df[m & (df.kind == k)]
        if not len(g): continue
        cells = []
        for e, _ in ENTRIES:
            a = ev(g[g.typ == 'that'], e).mean(); b = ev(g[g.typ == 'doi'], e).mean()
            if nm == 'NQ + GC':
                lo, hi = delta_ci(g, e); cells.append('%+.3f / %+.3f / **%+.3f** [%+.2f, %+.2f]' % (a, b, a - b, lo, hi))
            else:
                cells.append('%+.3f / %+.3f / %+.3f' % (a, b, a - b))
        print('| %s | %s | %d | %s |' % (nm, kn, (g.typ == 'that').sum(), ' | '.join(cells)))
