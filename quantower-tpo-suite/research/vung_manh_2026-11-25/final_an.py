#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""final_an.py — đọc kết quả final_eval.py, in bảng mật độ + hiệu quả (vùng thật so với vùng dời). python final_an.py ten [chi_tiet]"""
import pickle, sys
import numpy as np
import pandas as pd
from an import turn_offset, trade, boot_diff, SPLIT_DATE
from final_eval import out_path

BUF = 0.10


def load(tag):
    with open(out_path(tag), 'rb') as f:
        res = pickle.load(f)
    df = pd.DataFrame(res['ev'])
    df['test'] = df['t'].values >= SPLIT_DATE
    A, F, C = res['A'], res['F'], res['C']
    df['off'] = turn_offset(A, F, 1.0)
    df['in'] = (df['off'].abs() <= df['hw']).astype(float)
    df['truoc'] = (df['off'] > df['hw']).astype(float)
    df['xuyen'] = ((df['off'] < -df['hw']) | df['off'].isna()).astype(float)
    for R in (1.0, 2.0):
        f, r, rr = trade(A, F, C, df['hw'].values, BUF, R)
        df['fill'] = f.astype(float)
        df['R%g' % R] = np.where(f, rr, np.nan)
        df['w%g' % R] = np.where(f & (r != 0), (r == 1).astype(float), np.nan)
    df['same'] = np.where(df['side'] > 0, (df['n'] - df['n_hi']) / df['n'], df['n_hi'] / df['n'])
    return res, df


def row(df, name, m, base, md=False):
    cells = [name]
    for tm in (~df['test'], df['test']):
        mm = m & tm; bb = base & tm
        s = df.loc[mm, ['fill', 'in', 'xuyen', 'w1', 'R1', 'w2', 'R2']].mean()
        ci = ''
        if mm.sum() >= 40 and name != 'đối chứng (vùng dời)':
            x = df.loc[mm, 'R2'].dropna(); y = df.loc[bb, 'R2'].dropna()
            lo, hi = boot_diff(x.values, df.loc[x.index, 'day'].values, y.values, df.loc[y.index, 'day'].values, B=600)
            ci = '[%+.2f; %+.2f]' % (lo, hi)
        cells += ['%d' % mm.sum(), '%.0f' % (100 * s['fill']), '%.1f' % (100 * s['in']), '%.1f' % (100 * s['xuyen']), '%.1f' % (100 * s['w1']),
                  '%+.3f' % s['R1'], '%.1f' % (100 * s['w2']), '%+.3f' % s['R2'], ci]
    return '| ' + ' | '.join(cells) + ' |'


HEAD = ('| Nhóm | n TRAIN | khớp % | đảo trong vùng % | xuyên % | thắng 1:1 % | R 1:1 | thắng 1:2 % | R 1:2 | ΔR 1:2 so đối chứng [5–95%] '
        '| n TEST | khớp % | đảo trong vùng % | xuyên % | thắng 1:1 % | R 1:1 | thắng 1:2 % | R 1:2 | ΔR 1:2 so đối chứng [5–95%] |\n|' + '---|' * 19)


def table(df):
    t, d = df['typ'] == 'that', df['typ'] == 'doi'
    out = [HEAD, row(df, 'đối chứng (vùng dời)', d, d)]
    out.append(row(df, 'mọi cụm va đập đủ số lần', t, d))
    out.append(row(df, 'KHÔNG hợp lưu', t & (df['ngroup'] == 0), d))
    out.append(row(df, 'hợp lưu ≥ 1', t & (df['ngroup'] >= 1), d))
    if 'shown' in df:
        out.append(row(df, '**vùng ĐƯỢC VẼ (sau lọc chồng, bán kính, trần)**', t & df['shown'].astype(bool), d))
    out.append(row(df, 'hợp lưu ≥ 2', t & (df['ngroup'] >= 2), d))
    out.append(row(df, 'có HVN đủ điều kiện', t & df['hvn'], d))
    out.append(row(df, '**VÀNG (≥ 3 nhóm, có HVN)**', t & df['gold'], d))
    return '\n'.join(out)


def density(res, df):
    dn = res['dens']
    s = []
    s.append('cụm đủ số lần va đập trên chart (TB mỗi nến M30): %.2f · trong đó có hợp lưu: %.2f · có hợp lưu và cách giá ≤ 3 U: %.2f (dưới giá %.2f, trên giá %.2f)'
             % (dn[:, 1].mean(), dn[:, 2].mean(), dn[:, 3].mean(), dn[:, 6].mean(), dn[:, 7].mean()))
    s.append('%% thời gian có ≥ 1 vùng hợp lưu trong 3 U: %.0f%% · có > 4 vùng: %.1f%% · vùng vàng trên chart TB: %.2f (trong 3 U: %.2f); %% thời gian có ≥ 1 vùng vàng trong 3 U: %.0f%%'
             % (100 * (dn[:, 3] >= 1).mean(), 100 * (dn[:, 3] > 4).mean(), dn[:, 4].mean(), dn[:, 5].mean(), 100 * (dn[:, 5] >= 1).mean()))
    t = (df['typ'] == 'that') & (df['ngroup'] >= 1)
    s.append('lần quay lại vùng hợp lưu: %.2f / phiên · nửa bề rộng vùng (×U) pct 10/50/90: %s'
             % (t.sum() / df['day'].nunique(), df.loc[t, 'hw'].quantile([.1, .5, .9]).round(3).tolist()))
    return '\n'.join(s)


if __name__ == '__main__':
    tag = sys.argv[1]
    res, df = load(tag)
    print('##', tag, {k: v for k, v in res['p'].items() if k in ('R', 'LB', 'WC', 'NMIN', 'TOL', 'D_ONLY', 'HVN_AWAY')})
    print(density(res, df)); print(table(df))
    if len(sys.argv) > 2:
        t, d = (df['typ'] == 'that') & (df['ngroup'] >= 1), df['typ'] == 'doi'
        print(HEAD)
        for nm, m in (('đã bị đóng nến xuyên 0 lần', df['cross'] == 0), ('xuyên 1 lần', df['cross'] == 1), ('xuyên ≥ 2 lần', df['cross'] >= 2),
                      ('đúng vai (same = 1)', df['same'] == 1), ('lẫn vai', (df['same'] > 0) & (df['same'] < 1)), ('đổi vai (same = 0)', df['same'] == 0),
                      ('điểm mới nhất ≤ 12 giờ', df['age'] <= 24), ('điểm mới nhất > 12 giờ', df['age'] > 24),
                      ('n = 3', df['n'] == 3), ('n = 4', df['n'] == 4), ('n ≥ 5', df['n'] >= 5),
                      ('va đập trải ≥ 2 phiên', df['ndays'] >= 2), ('va đập trong 1 phiên', df['ndays'] == 1)):
            print(row(df, nm, t & m, d))
            print(row(df, nm + ' — dời', d & m, d))
