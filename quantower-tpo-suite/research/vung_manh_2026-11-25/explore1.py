# -*- coding: utf-8 -*-
"""explore1.py — bảng thô đầu tiên: tỉ lệ đảo chiều trong vùng + thắng 1:1 / 1:2 theo loại vùng."""
import sys
from an import *

a = sys.argv[1:]
cfg = (int(a[0]) if a else 2, float(a[1]) if len(a) > 1 else 1.0, int(a[2]) if len(a) > 2 else 5, float(a[3]) if len(a) > 3 else 0.5)
res = load(*cfg)
df = frame(res, pad=0.15, tol=0.0)
A, F, C = res['A'], res['F'], res['C']
off = turn_offset(A, F, 1.0)
df['off'] = off
for h in (0.15, 0.25, 0.4):
    df['in%g' % h] = (np.abs(off) <= h).astype(float)
df['pen'] = (off < -0.4).astype(float)
df['early'] = (off > 0.4).astype(float)
f1, r1, rr1 = trade(A, F, C, 0.25, 0.15, 1.0)
f2, r2, rr2 = trade(A, F, C, 0.25, 0.15, 2.0)
df['fill'] = f1.astype(float); df['R1'] = np.where(f1, rr1, np.nan); df['R2'] = np.where(f2, rr2, np.nan)
df['w1'] = np.where(f1 & (r1 != 0), (r1 == 1).astype(float), np.nan)
df['w2'] = np.where(f2 & (r2 != 0), (r2 == 1).astype(float), np.nan)
print('cấu hình', cfg, 'sự kiện', len(df), df['typ'].value_counts().to_dict())
cols = ['in0.15', 'in0.25', 'in0.4', 'early', 'pen', 'fill', 'w1', 'R1', 'w2', 'R2']


def show(name, m):
    for lab, mm in (('TRAIN', m & ~df['test']), ('TEST', m & df['test'])):
        s = df.loc[mm, cols].mean()
        print('%-34s %-5s n=%5d ' % (name, lab, mm.sum()) + ' '.join('%s=%.3f' % (c, s[c]) for c in cols))


cum, doi, muc = df['typ'] == 'cum', df['typ'] == 'doi', df['typ'] == 'muc'
show('đối chứng dời', doi)
show('cụm n=1', cum & (df['n'] == 1))
show('cụm n=2', cum & (df['n'] == 2))
show('cụm n>=3', cum & (df['n'] >= 3))
show('cụm n>=2 không hợp lưu', cum & (df['n'] >= 2) & (df['nfam'] == 0))
show('cụm n>=2 hợp lưu>=1', cum & (df['n'] >= 2) & (df['nfam'] >= 1))
show('cụm n>=2 hợp lưu>=2', cum & (df['n'] >= 2) & (df['nfam'] >= 2))
show('cụm n>=2 hợp lưu>=3 + HVN', cum & (df['n'] >= 2) & (df['nfam'] >= 3) & df['hvn'])
show('cụm n>=3 hợp lưu>=1', cum & (df['n'] >= 3) & (df['nfam'] >= 1))
show('cụm n>=2 có HVN', cum & (df['n'] >= 2) & df['hvn'])
show('dời, "hợp lưu">=1', doi & (df['nfam'] >= 1))
show('dời, không', doi & (df['nfam'] == 0))
for fam in ['VWAP ngày', 'VWAP tuần', 'VA ngày', 'VA tuần', 'HVN ngày', 'HVN tuần']:
    show('mức: ' + fam, muc & (df['fam'] == fam))
print(df.loc[cum & (df['n'] >= 2), 'span'].describe())
print('số sự kiện cụm n>=2 hợp lưu>=1 mỗi phiên:', (cum & (df['n'] >= 2) & (df['nfam'] >= 1)).sum() / df['day'].nunique())
