# -*- coding: utf-8 -*-
"""explore3.py — từng MỨC hợp lưu đứng một mình (không cần va đập) + đặc trưng HVN ("lớn và đều", chữ D, đã rời xa)."""
import sys
from an import *

a = sys.argv[1:]
cfg = (int(a[0]) if a else 2, float(a[1]) if len(a) > 1 else 1.0, int(a[2]) if len(a) > 2 else 5, float(a[3]) if len(a) > 3 else 0.5)
res = load(*cfg)
df = frame(res)
A, F, C = res['A'], res['F'], res['C']
df['off'] = turn_offset(A, F, 1.0)
df['in'] = (df['off'].abs() <= 0.25).astype(float)
for R in (1.0, 2.0):
    f, r, rr = trade(A, F, C, 0.25, 0.15, R)
    df['R%g' % R] = np.where(f, rr, np.nan)
    df['w%g' % R] = np.where(f & (r != 0), (r == 1).astype(float), np.nan)
doi, muc = df['typ'] == 'doi', df['typ'] == 'muc'
df['is_poc'] = df['is_poc'].fillna(False).astype(bool)
cols = ['in', 'w1', 'R1', 'w2', 'R2']


def line(name, m):
    out = '%-30s' % name
    for tm in (~df['test'], df['test']):
        mm = m & tm; bb = doi & tm
        s = df.loc[mm, cols].mean()
        x = df.loc[mm, 'R2'].dropna(); y = df.loc[bb, 'R2'].dropna()
        lo, hi = boot_diff(x.values, df.loc[x.index, 'day'].values, y.values, df.loc[y.index, 'day'].values, B=400) if len(x) > 30 else (np.nan, np.nan)
        out += ' | n=%4d in=%.3f w1=%.3f R1=%+.3f w2=%.3f R2=%+.3f dR2=[%+.2f;%+.2f]' % (mm.sum(), s['in'], s['w1'], s['R1'], s['w2'], s['R2'], lo, hi)
    print(out)


print('%-30s | TRAIN %s | TEST' % ('', ' ' * 60))
line('đối chứng dời', doi)
for nm in ['vwap_d', 'vwap_d_tren', 'vwap_d_duoi', 'vwap_w', 'vwap_w_tren', 'vwap_w_duoi', 'vah_d', 'val_d', 'vah_w', 'val_w', 'hvn_d', 'hvn_w']:
    line(nm, muc & (df['name'] == nm))
h = muc & df['name'].isin(['hvn_d', 'hvn_w'])
print('--- HVN: bề rộng dải 70%% (×U) pct 10/50/90:', df.loc[h, 'lw'].quantile([.1, .5, .9]).round(2).tolist(),
      '| tỉ lệ đỉnh/TB:', df.loc[h, 'ratio'].quantile([.1, .5, .9]).round(2).tolist(), '| phần KL trong dải:', df.loc[h, 'share'].quantile([.1, .5, .9]).round(3).tolist())
hd = muc & (df['name'] == 'hvn_d')
line('hvn_d là POC ngày', hd & df['is_poc'])
line('hvn_d không phải POC', hd & ~df['is_poc'])
line('hvn_d của hôm qua (src=1)', hd & (df['src'] == 1))
line('hvn_d 2–5 ngày trước', hd & (df['src'] >= 2))
line('hvn_d rộng (lw>=0.3U)', hd & (df['lw'] >= 0.3))
line('hvn_d hẹp (lw<0.3U)', hd & (df['lw'] < 0.3))
line('hvn_d share>=15%', hd & (df['share'] >= 0.15))
line('hvn_d ratio>=3.5', hd & (df['ratio'] >= 3.5))
dsh = (df['poc_pos'].between(0.3, 0.7)) & (df['va_frac'] <= 0.5)
line('hvn_d ngày chữ D', hd & dsh)
line('hvn_d ngày không chữ D', hd & ~dsh)
line('hvn_d rời xa >=3U', hd & (df['away'] >= 3))
line('hvn_d rời xa <3U', hd & (df['away'] < 3))
line('hvn_d lần đầu quay lại (since>=24)', hd & (df['since'] >= 24))
hw = muc & (df['name'] == 'hvn_w')
line('hvn_w tuần trước', hw & (df['src'] == 1))
line('hvn_w tuần này', hw & (df['src'] == 0))
line('hvn_w rời xa >=3U', hw & (df['away'] >= 3))
line('HVN (d+w) chữ D + POC + xa>=3U', h & dsh & df['is_poc'] & (df['away'] >= 3))
