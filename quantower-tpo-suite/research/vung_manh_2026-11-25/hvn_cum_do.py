#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum_do.py — đo ảnh hưởng của "HVN dạng cụm" lên vùng mạnh (HVN-CUM.md mục 4), trên MỘT hợp đồng.
Cách chấm và đối chứng y như final_eval.py / do_lai.py; chỉ đổi cách định nghĩa HVN và luật hợp lưu với hộp HVN.

  python prep1.py gc ; python prep1.py nq
  python hvn_cum_do.py gc          (GCZ26)
  python hvn_cum_do.py nq          (NQZ26, tắt phát hiện chỗ nối — dữ liệu một hợp đồng)
"""
import os, sys, pickle, tempfile
sym = sys.argv[1]
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
os.environ['VM_CACHE'] = os.path.join(CDIR, 'vm1_%s.pkl' % sym)
import numpy as np
import pandas as pd
import vm
from vm import Data
import vung_manh as V
import final_eval
from an import turn_offset, trade, boot_diff

if sym == 'nq':
    vm.SPLICE_JUMP = 1e12
    def rows_over_nq(self, a, b, row=vm.ROW):
        tk, v = self.ticks_over(a, b)
        if len(tk) == 0: return np.array([]), np.array([])
        rid = np.round((tk * 0.25) / 0.5).astype(np.int64)
        u, inv = np.unique(rid, return_inverse=True)
        return u * row, np.bincount(inv, weights=v)
    Data.rows_over = rows_over_nq

VARIANTS = [
    ('cũ: đỉnh nhọn, chỉ chữ D', dict(HVN_MODE='dinh', D_ONLY=True)),
    ('cụm · giao hộp', dict(HVN_MODE='cum', HVN_HL='giao', D_ONLY=False)),
    ('cụm · chỉ mép hộp', dict(HVN_MODE='cum', HVN_HL='mep', D_ONLY=False)),
    ('cụm · giao hộp · chỉ chữ D', dict(HVN_MODE='cum', HVN_HL='giao', D_ONLY=True)),
    ('cụm · chỉ mép hộp · chỉ chữ D', dict(HVN_MODE='cum', HVN_HL='mep', D_ONLY=True)),
]
BUF = 0.10


def density(D, p):
    eng = V.Engine(D, p)
    rows, nlev, nok, cover, wbox = [], [], [], [], []
    for j in range(D.n - 1):
        u = D.U[j + 1]
        if not np.isfinite(u) or D.seg_of[j] != D.seg_of[j + 1]: continue
        zs = eng.zones(j)
        px = float(D.m30['c'][j])
        sh = V.display(D, zs, j, px, p)
        rows.append((len(zs), sum(z['ngroup'] >= 1 for z in zs), sum(z['hvn'] for z in zs), sum(z['gold'] for z in zs),
                     len(sh), sum(z['gold'] for z in sh), sum(z['hvn'] for z in sh), sum(z['ngroup'] >= 2 for z in sh)))
        d = int(D.day_of[j + 1])
        hv = [L for L in eng.levels(d) if L['name'].startswith('hvn')]
        ok = [L for L in hv if V.hvn_ok(D, L, j, u, p)]
        nlev.append(len(hv)); nok.append(len(ok))
        wbox += [(L['hi'] - L['lo']) / u for L in ok]
        # phần của dải giá ± 4 U quanh giá hiện tại nằm trong một hộp HVN đủ điều kiện (đã nới dung sai)
        g = np.linspace(px - 4 * u, px + 4 * u, 401); m = np.zeros(len(g), bool)
        for L in ok: m |= (g >= L['lo'] - p['TOL'] * u) & (g <= L['hi'] + p['TOL'] * u)
        cover.append(m.mean())
    a = np.array(rows, float)
    return dict(cum=a[:, 0].mean(), hl=100 * a[:, 1].sum() / a[:, 0].sum(), hvn=100 * a[:, 2].sum() / a[:, 0].sum(), gold=100 * a[:, 3].sum() / a[:, 0].sum(),
                ve=a[:, 4].mean(), co=100 * (a[:, 4] >= 1).mean(), tg=100 * (a[:, 5] >= 1).mean(), th=100 * (a[:, 6] >= 1).mean(), t2=100 * (a[:, 7] >= 1).mean(),
                nlev=np.mean(nlev), nok=np.mean(nok), cover=100 * np.mean(cover), wbox=np.percentile(wbox, [10, 50, 90]) if wbox else [np.nan] * 3)


def events(tag):
    with open(final_eval.out_path(tag), 'rb') as f:
        res = pickle.load(f)
    df = pd.DataFrame(res['ev'])
    A, F, C = res['A'], res['F'], res['C']
    for R in (1.0, 2.0):
        f, r, rr = trade(A, F, C, df['hw'].values, BUF, R)
        df['R%g' % R] = np.where(f, rr, np.nan)
        df['w%g' % R] = np.where(f & (r != 0), (r == 1).astype(float), np.nan)
    return df


def row(df, m, base):
    if m.sum() == 0: return '0 | — | — | — | —'
    s = df.loc[m, ['w1', 'R2']].mean()
    def ci(col):
        x = df.loc[m, col].dropna(); y = df.loc[base, col].dropna()
        if len(x) < 30: return 'n nhỏ'
        lo, hi = boot_diff(x.values, df.loc[x.index, 'day'].values, y.values, df.loc[y.index, 'day'].values, B=1000)
        return ('[%+.1f; %+.1f]' % (100 * lo, 100 * hi)) if col == 'w1' else ('[%+.2f; %+.2f]' % (lo, hi))
    return '%d | %.1f %% (%d lệnh) | %s | %+.3f | %s' % (m.sum(), 100 * s['w1'], df.loc[m, 'w1'].notna().sum(), ci('w1'), s['R2'], ci('R2'))


def main():
    D = Data()
    dens, evs = [], []
    for i, (ten, over) in enumerate(VARIANTS):
        p = dict(V.P); p.update(over)
        tag = 'hc_%s_%d' % (sym, i)
        if not os.path.exists(final_eval.out_path(tag)) or 'lai' in sys.argv:
            final_eval.run(tag, over)
        dens.append(density(D, p)); evs.append(events(tag))
    print('\n## %s — mật độ' % sym.upper())
    print('| Cách định nghĩa HVN | HVN đưa vào xét / phiên | trong đó đủ điều kiện | bề rộng hộp đủ điều kiện (×U) p10 / 50 / 90 | % dải ± 4 U quanh giá nằm trong hộp HVN | cụm ≥ 3 lần / nến | % cụm có hợp lưu | % cụm có HVN | % cụm vàng | vùng vẽ TB | % thời gian có vùng | % thời gian có vùng dính HVN | % thời gian có vùng ≥ 2 nhóm | % thời gian có vàng |')
    print('|' + '---|' * 14)
    for (ten, _), d in zip(VARIANTS, dens):
        print('| %s | %.1f | %.1f | %s | %.0f | %.1f | %.0f | %.0f | %.1f | %.2f | %.0f | %.0f | %.0f | %.1f |'
              % (ten, d['nlev'], d['nok'], ' / '.join('%.2f' % q for q in d['wbox']), d['cover'], d['cum'], d['hl'], d['hvn'], d['gold'], d['ve'], d['co'], d['th'], d['t2'], d['tg']))
    print('\n## %s — kết quả chấm (thắng 1:1, R 1:2; ngoặc vuông = khoảng 5–95 %% của hiệu so với đối chứng)' % sym.upper())
    print('| Cách định nghĩa HVN | Nhóm | n | thắng 1:1 | Δ thắng (điểm %) | R 1:2 | ΔR 1:2 |')
    print('|---|---|---|---|---|---|---|')
    for (ten, _), df in zip(VARIANTS, evs):
        base = df['typ'] == 'doi'; that = df['typ'] == 'that'
        s = df.loc[base, ['w1', 'R2']].mean()
        print('| %s | đối chứng (vùng dời) | %d | %.1f %% | — | %+.3f | — |' % (ten, base.sum(), 100 * s['w1'], s['R2']))
        for nm, m in (('vùng ĐƯỢC VẼ', that & df['shown'].astype(bool)), ('cụm có HVN', that & df['hvn'].astype(bool)),
                      ('cụm KHÔNG có HVN', that & ~df['hvn'].astype(bool)), ('hợp lưu ≥ 2 nhóm', that & (df['ngroup'] >= 2)), ('VÀNG', that & df['gold'].astype(bool))):
            print('| | %s | %s |' % (nm, row(df, m, base)))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
