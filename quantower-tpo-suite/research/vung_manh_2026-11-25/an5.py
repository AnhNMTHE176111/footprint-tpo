#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""an5.py — bảng kết quả bt5: python an5.py nqy v0 [v1 ...]"""
import os, sys, tempfile
import numpy as np, pandas as pd
import bt5
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
sym = sys.argv[1]; vongs = sys.argv[2:] or ['v0']
F = lambda x: '—' if x is None or (isinstance(x, float) and np.isnan(x)) else ('%.0f' % x if abs(x) >= 10 else '%.2f' % x)

def tab(df, title, groups):
    print('\n####', title)
    print('| Nhóm | loại | n | đảo trước vùng % | (trong 0,3U) % | đảo trong vùng % | phá % | khớp @mép % | R 1:2 @mép | khớp @+0,1U % | R 1:2 @+0,1 | khớp @+0,2U % | R 1:2 @+0,2 | khớp @+0,3U | R 1:2 @+0,3 |')
    print('|' + '---|' * 15)
    for name, m in groups:
        for r in bt5.summary(df[m], name):
            print('| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                name, 'thật' if r['typ'] == 'that' else 'đối chứng', r['n'], F(r['som']), F(r['som_gan']), F(r['trong']), F(r['pha']),
                F(r['khop0']), F(r['R2_0']), F(r['khop0.1']), F(r['R2_0.1']), F(r['khop0.2']), F(r['R2_0.2']), F(r['khop0.3']), F(r['R2_0.3'])))

for v in vongs:
    df = pd.read_pickle(os.path.join(CDIR, 'bt5_%s_%s.pkl' % (sym, v)))
    print('\n## %s — vòng %s' % (sym, v))
    for tap in ('TRAIN', 'TEST', None):
        d = df if tap is None else df[df['tap'] == tap]
        groups = [('vùng mạnh', d['kind'] == 'z'), ('vùng vàng', (d['kind'] == 'z') & d['gold']), ('hộp HVN', d['kind'] == 'b'),
                  ('lần chạm đầu', d['first']), ('tất cả', d['kind'].notna())]
        tab(d, tap or 'CẢ KỲ', groups)
    # lý do đảo sớm
    print('\n#### Đảo trước vùng: điểm đảo trùng (± 0,10 U) với …  (% số lần đảo sớm)')
    print('| loại | n đảo sớm | đỉnh/đáy M30 cũ (bật ≥1U) | râu M30 bất kỳ 5 phiên | vùng/hộp/đệm khác đang vẽ | cao/thấp hôm qua | số tròn | VWAP phiên đang chạy | không trùng gì |')
    print('|' + '---|' * 9)
    for kind, nm in (('z', 'vùng mạnh'), ('b', 'hộp HVN')):
        for typ in ('that', 'doi'):
            g = df[(df['kind'] == kind) & (df['typ'] == typ) & df['done'] & (df['depth'] < 0)]
            if not len(g): continue
            none = ~(g['pivot'] | g['rau'] | g['vung_khac'] | g['hl_homqua'] | g['so_tron'] | g['vwap_nay'])
            print('| %s %s | %d | %s | %s | %s | %s | %s | %s | %s |' % (nm, 'thật' if typ == 'that' else 'đối chứng', len(g),
                  *[F(g[c].mean() * 100) for c in ('pivot', 'rau', 'vung_khac', 'hl_homqua', 'so_tron', 'vwap_nay')], F(none.mean() * 100)))
    # phân bố điểm đảo
    print('\n#### Phân bố điểm đảo (depth, đơn vị U; âm = chưa tới mép gần) — % lần quay lại đã đảo xong')
    bins = [-9, -0.6, -0.4, -0.2, -0.1, 0, 0.1, 0.25, 0.5, 1, 99]
    print('| loại | ' + ' | '.join('%g..%g' % (bins[i], bins[i + 1]) for i in range(len(bins) - 1)) + ' |')
    print('|' + '---|' * len(bins))
    for kind, nm in (('z', 'vùng mạnh'), ('b', 'hộp HVN')):
        for typ in ('that', 'doi'):
            g = df[(df['kind'] == kind) & (df['typ'] == typ) & df['done']]
            h = np.histogram(g['depth'], bins)[0] / max(1, len(g)) * 100
            print('| %s %s (n %d) | ' % (nm, 'thật' if typ == 'that' else 'đ/c', len(g)) + ' | '.join(F(x) for x in h) + ' |')
    o = pd.read_pickle(os.path.join(CDIR, 'bt5_%s_%s_objs.pkl' % (sym, v)))
    fl = np.array(o['flick'])
    print('\nĐộ ổn định: %d vật thể, %d (%.0f %%) có lúc tắt rồi hiện lại; trung bình rộng vùng mạnh %.2f U, hộp %.2f U' % (
        len(fl), (fl > 0).sum(), (fl > 0).mean() * 100, df.loc[(df.kind == 'z') & (df.typ == 'that'), 'w'].mean(), df.loc[(df.kind == 'b') & (df.typ == 'that'), 'w'].mean()))
