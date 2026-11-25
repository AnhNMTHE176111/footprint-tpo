#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""final5.py — bảng chốt v0 (trước) vs v5 (sau 5 vòng) + độ bền (bật 1,5U, dừng 0,3U, R 1:1, theo tháng)."""
import os, sys, tempfile
import numpy as np, pandas as pd
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
def ld(v, sfx=''):
    out = []
    for s in ('nqy', 'gc'):
        d = pd.read_pickle(os.path.join(CDIR, 'bt5_%s_%s%s.pkl' % (s, v, sfx))); d['sym'] = s; out.append(d)
    d = pd.concat(out, ignore_index=True)
    d['ev2'] = np.where(d['fill0'] == 1, d['r2_0'].fillna(0), 0.0)
    d['ev1'] = np.where(d['fill0'] == 1, d['r1_0'].fillna(0), 0.0)
    d['som'] = d['done'] & (d['depth'] < 0); d['trong'] = d['done'] & (d['depth'] >= 0) & (d['depth'] <= d['w'] + 0.25)
    d['pha'] = ~d['done'] | (d['depth'] > d['w'] + 0.25)
    d['thang'] = pd.DatetimeIndex(d['t0']).strftime('%Y-%m')
    return d
def boot(g, col, B=600, seed=5):
    by = {d: (x[x.typ == 'that'][col].values, x[x.typ == 'doi'][col].values) for d, x in g.groupby(['sym', 'day'])}
    keys = list(by); rs = np.random.RandomState(seed); out = []
    for _ in range(B):
        ks = [keys[i] for i in rs.randint(0, len(keys), len(keys))]
        out.append(np.concatenate([by[k][0] for k in ks]).mean() - np.concatenate([by[k][1] for k in ks]).mean())
    return np.percentile(out, [5, 95])
SUB = [('NQ TRAIN', lambda d: (d.sym == 'nqy') & (d.tap == 'TRAIN')), ('NQ TEST', lambda d: (d.sym == 'nqy') & (d.tap == 'TEST')),
       ('GC', lambda d: d.sym == 'gc'), ('NQ + GC', lambda d: d.sym.notna())]
print('### Trước (v0) và sau 5 vòng (v5): lệnh limit ở mép gần (v5: mép dải chờ 0,2U của hộp), dừng mép xa + 0,15U')
print('| tập | loại | bản | n thật | đảo trước mép % | đảo trong vùng % | phá % | khớp % | R 1:2 / lần quay lại: thật | đối chứng | Δ [5–95 %] | R 1:1 Δ |')
print('|' + '---|' * 12)
for sub, f in SUB:
    for k, kn in (('z', 'vùng mạnh'), ('b', 'hộp HVN')):
        for v in ('v0', 'v5'):
            d = ld(v); g = d[f(d) & (d.kind == k)]; a = g[g.typ == 'that']; b = g[g.typ == 'doi']
            ci = boot(g, 'ev2') if sub == 'NQ + GC' else None
            print('| %s | %s | %s | %d | %.0f | %.0f | %.0f | %.0f | %+.3f | %+.3f | %+.3f%s | %+.3f |' % (
                sub, kn, v, len(a), a.som.mean() * 100, a.trong.mean() * 100, a.pha.mean() * 100, (a.fill0 == 1).mean() * 100,
                a.ev2.mean(), b.ev2.mean(), a.ev2.mean() - b.ev2.mean(), (' [%+.2f, %+.2f]' % tuple(ci)) if ci is not None else '',
                a.ev1.mean() - b.ev1.mean()))
print('\n### Độ bền (NQ + GC, Δ R 1:2 mỗi lần quay lại, thật − đối chứng)')
print('| biến thể chấm | vùng mạnh v0 | vùng mạnh v5 | hộp v0 | hộp v5 |'); print('|---|---|---|---|---|')
for sfx, nm in (('', 'chuẩn (bật 1U, dừng 0,15U)'), ('_B15', 'đảo = bật 1,5U'), ('_S30', 'dừng mép xa + 0,30U')):
    cells = []
    for k in ('z', 'b'):
        for v in ('v0', 'v5'):
            d = ld(v, sfx); g = d[d.kind == k]
            cells.append('%+.3f' % (g[g.typ == 'that'].ev2.mean() - g[g.typ == 'doi'].ev2.mean()))
    print('| %s | %s |' % (nm, ' | '.join(cells)))
print('\n### Theo tháng (v5, Δ R 1:2; n thật)')
d = ld('v5')
print('| tháng | NQ vùng mạnh | NQ hộp | GC vùng mạnh | GC hộp |'); print('|---|---|---|---|---|')
for th in sorted(d.thang.unique()):
    cells = []
    for s in ('nqy', 'gc'):
        for k in ('z', 'b'):
            g = d[(d.thang == th) & (d.sym == s) & (d.kind == k)]
            a = g[g.typ == 'that']
            cells.append('—' if len(a) < 10 else '%+.2f (n %d)' % (a.ev2.mean() - g[g.typ == 'doi'].ev2.mean(), len(a)))
    print('| %s | %s |' % (th, ' | '.join(cells)))
