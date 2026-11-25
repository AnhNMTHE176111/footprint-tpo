# -*- coding: utf-8 -*-
"""explore2.py — phân phối ĐIỂM ĐẢO CHIỀU so với các cách đặt tâm (giữa cụm / mép cực / điểm mới nhất),
cụm thật so với cụm dời. Nếu vùng va đập thật sự "bắt" đỉnh/đáy thì phải có đỉnh nhọn quanh 0 mà cụm dời không có."""
import sys
from an import *

a = sys.argv[1:]
cfg = (int(a[0]) if a else 2, float(a[1]) if len(a) > 1 else 1.0, int(a[2]) if len(a) > 2 else 5, float(a[3]) if len(a) > 3 else 0.5)
res = load(*cfg)
df = frame(res)
A, F, C = res['A'], res['F'], res['C']
for X in (0.5, 1.0, 2.0):
    df['off%g' % X] = turn_offset(A, F, X)
bins = np.arange(-0.75, 0.7501, 0.15)
cum, doi = (df['typ'] == 'cum') & (df['n'] >= 2), df['typ'] == 'doi'


def hist(m, col, ref):
    x = (df.loc[m, col] - (df.loc[m, ref] if ref else 0)).values
    x = x[~np.isnan(x)]
    hh = np.histogram(x, bins=bins)[0] / max(len(x), 1)
    return ' '.join('%4.1f' % (100 * v) for v in hh) + '  | xuyên<%.2f: %4.1f%%  n=%d' % (bins[0], 100 * (x < bins[0]).mean(), len(x))


print('cấu hình', cfg)
print('ô (×U):', ' '.join('%4.2f' % b for b in bins[:-1]))
for X in (0.5, 1.0, 2.0):
    print('--- bật lại X = %g U' % X)
    for ref, nm in ((None, 'giữa cụm'), ('d_ext', 'mép cực xa'), ('d_last', 'điểm mới nhất'), ('d_mean', 'trung bình')):
        for lab, tm in (('TRAIN', ~df['test']), ('TEST', df['test'])):
            print('%-14s %-5s thật: %s' % (nm, lab, hist(cum & tm, 'off%g' % X, ref)))
            print('%-14s %-5s dời : %s' % (nm, lab, hist(doi & tm, 'off%g' % X, ref)))
# theo đặc trưng: tỉ lệ đảo trong ±0.25U quanh giữa cụm (X=1)
df['in'] = (df['off1'].abs() <= 0.25).astype(float)
f1, r1, rr1 = trade(A, F, C, 0.25, 0.15, 2.0)
df['R2'] = np.where(f1, rr1, np.nan)
base = df.loc[doi].groupby('test')[['in', 'R2']].mean()
print('nền (dời):', base.round(3).to_dict())
for col, cuts in (('same', [-0.01, 0.01, 0.99, 1.0]), ('age', [-1, 6, 24, 60, 1e9]), ('ndays', [0, 1, 2, 9]), ('away', [0, 2, 3, 5, 99]),
                  ('since', [0, 6, 24, 60, 1e9]), ('n', [1, 2, 3, 4, 99]), ('span', [-1, 0.15, 0.3, 0.5]), ('nfam', [-1, 0, 1, 2, 9])):
    g = df.loc[cum].groupby([pd.cut(df.loc[cum, col], cuts), 'test'], observed=True)[['in', 'R2']].agg(['mean', 'count'])
    print('==', col); print(g.round(3).to_string())
hr = pd.to_datetime(df['t']).dt.hour
df['phien'] = np.where((hr >= 22) | (hr < 6), 'A', np.where(hr < 12, 'EU', 'US'))
print(df.loc[cum].groupby(['phien', 'test'])[['in', 'R2']].agg(['mean', 'count']).round(3).to_string())
print(df.loc[doi].groupby(['phien', 'test'])[['in', 'R2']].agg(['mean', 'count']).round(3).to_string())
