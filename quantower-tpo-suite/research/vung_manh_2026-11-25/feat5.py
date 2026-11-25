#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""feat5.py — tách kết quả bt5 theo bối cảnh: python feat5.py v0 [cột]"""
import os, sys, tempfile
import numpy as np, pandas as pd
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
v = sys.argv[1]
E = sys.argv[2] if len(sys.argv) > 2 else '0.2'
def ld(s):
    d = pd.read_pickle(os.path.join(CDIR, 'bt5_%s_%s.pkl' % (s, v))); d['sym'] = s; return d
df = pd.concat([ld('nqy'), ld('gc')], ignore_index=True)
df['react'] = df['done'] & (df['depth'] >= -0.3) & (df['depth'] <= df['w'] + 0.25)
df['sess'] = pd.cut(df['hour'], [-1, 6, 12, 20, 24], labels=['Á 0–6', 'Âu 7–12', 'Mỹ 13–20', 'tối 21–23'])
df['spb'] = pd.cut(df['sp30'], [-99, 0.5, 1.0, 1.5, 99], labels=['<0,5', '0,5–1', '1–1,5', '>1,5'])
df['vwb'] = pd.cut(df['vw'], [-99, -1, 0, 1, 99], labels=['sai phía >1U', 'sai phía 0–1U', 'đúng phía 0–1U', 'đúng phía >1U'])
df['npvb'] = pd.cut(df['npv'], [0, 3, 4, 6, 99], labels=['3', '4', '5–6', '7+'])
df['wb'] = pd.cut(df['w'], [0, 0.25, 0.4, 0.6, 9], labels=['<0,25', '0,25–0,4', '0,4–0,6', '>0,6'])
df['ageb'] = pd.cut(df['age'], [-1, 2, 12, 48, 1e9], labels=['≤2 nến', '3–12', '13–48', '>48'])
df['sideb'] = np.where(df['side'] > 0, 'hỗ trợ', 'kháng cự')
col = 'r2_%s' % E; fcol = 'fill%s' % E
def cell(g):
    t = g[g.typ == 'that']; c = g[g.typ == 'doi']
    a = t.loc[t[fcol] == 1, col].mean(); b = c.loc[c[fcol] == 1, col].mean()
    return '%d: %+.2f vs %+.2f (pư %.0f/%.0f)' % (len(t), a, b, t['react'].mean() * 100, c['react'].mean() * 100)
feats = sys.argv[3:] or ['sess', 'spb', 'vwb', 'sideb', 'wb', 'ageb', 'first', 'npvb', 'ngroup', 'hvn', 'bname', 'both']
for f in feats:
    print('\n### %s   (ô = n thật: R 1:2 @+%sU thật vs đối chứng (phản ứng %% thật/đối chứng))' % (f, E))
    print('| giá trị | NQ vùng mạnh | NQ hộp HVN | GC vùng mạnh | GC hộp HVN |'); print('|---|---|---|---|---|')
    for val, g in df.groupby(f, observed=True):
        cells = []
        for s in ('nqy', 'gc'):
            for k in ('z', 'b'):
                gg = g[(g.sym == s) & (g.kind == k)]
                cells.append(cell(gg) if (gg.typ == 'that').sum() >= 8 else '—')
        print('| %s | %s |' % (val, ' | '.join(cells)))
