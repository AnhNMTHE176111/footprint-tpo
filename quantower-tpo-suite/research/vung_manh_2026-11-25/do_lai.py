#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
do_lai.py — đo lại "vùng mạnh" trên MỘT HỢP ĐỒNG (GCZ26, NQZ26), thông số mặc định của spec, cách chấm y như lần trước
(final_eval.py: lần quay lại = chạm tâm ± 0,75 U sau khi đã rời ≥ 1,25 U; đối chứng = vùng dời 1,5–4 U, 3 bản/vùng).

  python prep1.py gc ; python prep1.py nq        (dựng bộ đệm + bảng chất lượng dữ liệu)
  python do_lai.py eval gc ; python do_lai.py eval nq
  python do_lai.py bang gc ; python do_lai.py bang nq      (bảng kết quả theo tháng + gộp, mật độ, độ rộng)
  python do_lai.py eval nq tatnoi ; python do_lai.py bang nq tatnoi   (tắt phát hiện chỗ nối hợp đồng)
  python do_lai.py thang nq [tatnoi]                        (mật độ vùng vẽ theo tháng)
  python do_lai.py full                                     (cắt kết quả 2,3 năm 'chot2' theo quý để so — cần VM_FULL)
"""
import os, sys, pickle, tempfile
from collections import Counter

CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
cmd = sys.argv[1]
sym = sys.argv[2] if len(sys.argv) > 2 else 'full'
if cmd == 'full':
    os.environ['VM_CACHE'] = os.environ.get('VM_FULL', os.path.join(CDIR, 'vm_full', 'vung_manh_cache.pkl'))
else:
    os.environ['VM_CACHE'] = os.path.join(CDIR, 'vm1_%s.pkl' % sym)     # phải đặt TRƯỚC khi import vm

import numpy as np
import pandas as pd
import vm
from vm import Data
import vung_manh as V
import final_eval
from an import turn_offset, trade, boot_diff

BUF = 0.10
SCALE = {'gc': 1.0, 'nq': 2.5, 'full': 1.0}[sym]      # nhân lại để ra giá thật (xem prep1.py)
TAG = {'gc': 'gc1', 'nq': 'nq1', 'full': 'chot2'}[sym]
# Thêm 'tatnoi' ở cuối dòng lệnh: TẮT phát hiện chỗ nối hợp đồng (dữ liệu một hợp đồng không có chỗ nối nào;
# trên NQ ngưỡng mặc định 50 điểm bắt nhầm khoảng trống giá thật qua giờ nghỉ ngày).
if 'tatnoi' in sys.argv:
    vm.SPLICE_JUMP = 1e12
    TAG += '_tatnoi'

if sym == 'nq':
    # Hàng profile ĐÚNG như C# sẽ chia trên NQ: Snap = Math.Round(giá / 0,5) — với giá NQ phép chia ra đúng x,5 nên làm tròn
    # nửa-về-chẵn cho hàng 3 bước giá xen hàng 1 bước giá. vm.rows_over (viết cho GC) chia theo số thực nên ra kiểu khác.
    def rows_over_nq(self, a, b, row=vm.ROW):
        tk, v = self.ticks_over(a, b)
        if len(tk) == 0: return np.array([]), np.array([])
        rid = np.round((tk * 0.25) / 0.5).astype(np.int64)
        u, inv = np.unique(rid, return_inverse=True)
        return u * row, np.bincount(inv, weights=v)
    Data.rows_over = rows_over_nq


def load():
    with open(final_eval.out_path(TAG), 'rb') as f:
        res = pickle.load(f)
    df = pd.DataFrame(res['ev'])
    A, F, C = res['A'], res['F'], res['C']
    df['off'] = turn_offset(A, F, 1.0)
    df['in'] = (df['off'].abs() <= df['hw']).astype(float)
    for R in (1.0, 2.0):
        f, r, rr = trade(A, F, C, df['hw'].values, BUF, R)
        df['fill'] = f.astype(float)
        df['R%g' % R] = np.where(f, rr, np.nan)
        df['w%g' % R] = np.where(f & (r != 0), (r == 1).astype(float), np.nan)
    df['thang'] = pd.to_datetime(df['t']).dt.strftime('%Y-%m')
    df['quy'] = pd.to_datetime(df['t']).dt.to_period('Q').astype(str)
    return res, df


def ci(df, m, base, col, B=1000):
    x = df.loc[m, col].dropna(); y = df.loc[base, col].dropna()
    if len(x) < 30 or len(y) < 30: return 'n nhỏ'
    lo, hi = boot_diff(x.values, df.loc[x.index, 'day'].values, y.values, df.loc[y.index, 'day'].values, B=B)
    k = 100 if col.startswith('w') else 1
    return ('[%+.1f; %+.1f]' if k == 100 else '[%+.2f; %+.2f]') % (lo * k, hi * k)


GROUPS = [
    ('đối chứng (vùng dời)', lambda d: d['typ'] == 'doi'),
    ('mọi cụm ≥ 3 lần va đập', lambda d: d['typ'] == 'that'),
    ('KHÔNG hợp lưu', lambda d: (d['typ'] == 'that') & (d['ngroup'] == 0)),
    ('hợp lưu ≥ 1 nhóm', lambda d: (d['typ'] == 'that') & (d['ngroup'] >= 1)),
    ('**vùng ĐƯỢC VẼ**', lambda d: (d['typ'] == 'that') & d['shown'].astype(bool)),
    ('hợp lưu ≥ 2 nhóm', lambda d: (d['typ'] == 'that') & (d['ngroup'] >= 2)),
    ('có HVN đủ điều kiện', lambda d: (d['typ'] == 'that') & d['hvn'].astype(bool)),
    ('**VÀNG** (≥ 3 nhóm, có HVN)', lambda d: (d['typ'] == 'that') & d['gold'].astype(bool)),
]
HEAD = '| Nhóm | n | khớp lệnh | đảo trong vùng | thắng 1:1 | Δ thắng 1:1 so đối chứng, điểm % [5–95 %] | R 1:1 | thắng 1:2 | R 1:2 | ΔR 1:2 so đối chứng [5–95 %] |\n|' + '---|' * 10


def table(df, sel=None, with_ci=True):
    d = df if sel is None else df[sel]
    base = d['typ'] == 'doi'
    out = [HEAD]
    for name, fn in GROUPS:
        m = fn(d)
        if m.sum() == 0:
            out.append('| %s | 0 | — | — | — | — | — | — | — | — |' % name); continue
        s = d.loc[m, ['fill', 'in', 'w1', 'R1', 'w2', 'R2']].mean()
        n1 = int(d.loc[m, 'w1'].notna().sum())
        c1 = c2 = '—'
        if with_ci and name != GROUPS[0][0]:
            c1, c2 = ci(d, m, base, 'w1'), ci(d, m, base, 'R2')
        out.append('| %s | %d | %.0f %% | %.1f %% | %.1f %% (%d lệnh) | %s | %+.3f | %.1f %% | %+.3f | %s |'
                   % (name, m.sum(), 100 * s['fill'], 100 * s['in'], 100 * s['w1'], n1, c1, s['R1'], 100 * s['w2'], s['R2'], c2))
    return '\n'.join(out)


def mini(df, key):
    """Bảng gọn theo tháng/quý: vùng được vẽ so với đối chứng."""
    out = ['| Kỳ | phiên | vẽ: n | thắng 1:1 | R 1:2 | đối chứng: n | thắng 1:1 | R 1:2 | ≥ 2 nhóm: n | thắng 1:1 | R 1:2 | vàng: n | thắng 1:1 |',
           '|' + '---|' * 13]
    for k, d in list(df.groupby(key)) + [('**gộp**', df)]:
        cells = [str(k), str(d['day'].nunique())]
        for name in ('**vùng ĐƯỢC VẼ**', 'đối chứng (vùng dời)', 'hợp lưu ≥ 2 nhóm'):
            m = dict(GROUPS)[name](d)
            s = d.loc[m, ['w1', 'R2']].mean()
            cells += ['%d' % m.sum(), ('%.1f %%' % (100 * s['w1'])) if m.sum() else '—', ('%+.3f' % s['R2']) if m.sum() else '—']
        m = dict(GROUPS)['**VÀNG** (≥ 3 nhóm, có HVN)'](d)
        cells += ['%d' % m.sum(), ('%.0f %%' % (100 * d.loc[m, 'w1'].mean())) if d.loc[m, 'w1'].notna().sum() else '—']
        out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)


def density(D, eng, p):
    """Mật độ vùng ĐƯỢC VẼ ở mỗi nến M30 (như mat_do.py) + thống kê theo phiên."""
    rows, wid, seen = [], [], {}
    for j in range(D.n - 1):
        if not np.isfinite(D.U[j + 1]) or D.seg_of[j] != D.seg_of[j + 1]: continue
        zs = eng.zones(j)
        sh = V.display(D, zs, j, float(D.m30['c'][j]), p)
        d = int(D.day_of[j + 1])
        rows.append((d, len(sh), sum(z['gold'] for z in sh), sum(z['inside'] for z in sh),
                     sum(1 for z in sh if z['side'] < 0 and not z['inside']), sum(1 for z in sh if z['side'] > 0 and not z['inside']),
                     len(zs), sum(1 for z in zs if z['ngroup'] >= 1), sum(1 for z in sh if z['ngroup'] >= 2)))
        wid += [(z['hi'] - z['lo']) / z['u'] for z in sh]
        seen.setdefault(d, set()).update((z['lo'], z['hi']) for z in sh)
    a = np.array(rows); cnt = a[:, 1]
    print('nến M30 xét: %d (%d phiên có U)' % (len(a), len(seen)))
    dist = Counter(np.minimum(cnt, 5).tolist())
    print('số vùng được vẽ: TB %.2f · 0 vùng %.1f %% · 1: %.1f %% · 2: %.1f %% · 3: %.1f %% · 4: %.1f %% · ≥ 5: %.1f %%'
          % ((cnt.mean(),) + tuple(100 * dist.get(k, 0) / len(cnt) for k in range(6))))
    print('có ≥ 1 vùng: %.0f %% thời gian · TB kháng cự %.2f + hỗ trợ %.2f · giá đang trong vùng %.1f %% · có vùng VÀNG %.1f %% · có vùng ≥ 2 nhóm %.1f %%'
          % (100 * (cnt >= 1).mean(), a[:, 4].mean(), a[:, 5].mean(), 100 * (a[:, 3] >= 1).mean(), 100 * (a[:, 2] >= 1).mean(), 100 * (a[:, 8] >= 1).mean()))
    print('trước lọc hiển thị: %.1f cụm đủ 3 lần va đập, %.1f cụm có hợp lưu' % (a[:, 6].mean(), a[:, 7].mean()))
    nz = np.array([len(v) for v in seen.values()])
    print('số vùng KHÁC NHAU được vẽ trong một phiên: TB %.1f · trung vị %d · p10–p90 %d–%d · phiên không có vùng nào: %d/%d'
          % (nz.mean(), np.median(nz), np.percentile(nz, 10), np.percentile(nz, 90), (nz == 0).sum(), len(nz)))
    w = np.percentile(wid, [10, 50, 90])
    print('bề rộng vùng được vẽ (×U) p10/50/90: %.2f / %.2f / %.2f' % tuple(w))
    return w


def structure(D, eng, p):
    """Các con số cấu tạo để so GC ↔ NQ theo đơn vị U (kiểm thông số độ rộng / dung sai có còn hợp lý không)."""
    t = pd.to_datetime(D.m30['t'])
    u = D.unit_day[np.isfinite(D.unit_day)]
    px = np.median(D.m30['c']) * SCALE
    print('giá trung vị %.1f · U (giá thật) p10/50/90: %s · U/giá = %.3f %% · bước giá = %.4f U · hàng profile (2 bước giá) = %.4f U'
          % (px, np.round(np.percentile(u, [10, 50, 90]) * SCALE, 1).tolist(), 100 * np.median(u) * SCALE / px, vm.TICK / np.median(u), vm.ROW / np.median(u)))
    print('phiên %d · tuần %d · "chỗ nối" bị bắt nhầm (nghỉ 30–150 phút + nhảy ≥ %s): %d %s'
          % (len(D.days), len(D.weeks), 'TẮT' if vm.SPLICE_JUMP > 1e9 else '%g giá thật' % (vm.SPLICE_JUMP * SCALE), len(D.splices), [str(t[s]) for s in D.splices]))
    gapm = np.diff(D.ts) / 60.0
    big = np.where((gapm >= 30) & (gapm <= 150) & (np.abs(D.m30['o'][1:] - D.m30['c'][:-1]) >= 20.0))[0] + 1
    for s in big:
        print('   nhảy qua giờ nghỉ ngày: %s  %+.1f giá thật = %.1f U' % (t[s], (D.m30['o'][s] - D.m30['c'][s - 1]) * SCALE, abs(D.m30['o'][s] - D.m30['c'][s - 1]) / D.U[s]))
    gap = np.diff(D.ts) / 60.0
    jump = np.abs(D.m30['o'][1:] - D.m30['c'][:-1])[(gap >= 30) & (gap <= 150)] * SCALE
    print('bước nhảy giá qua giờ nghỉ ngày (giá thật): trung vị %.1f · p90 %.1f · lớn nhất %.1f (n = %d)' % (np.median(jump), np.percentile(jump, 90), jump.max(), len(jump)))
    nb = np.array([b - a + 1 for a, b in D.days])
    print('nến M30/phiên: trung vị %d · phiên < 20 nến: %d' % (np.median(nb), (nb < 20).sum()))
    pv = eng.pv
    ok = np.isfinite(D.unit_day).sum()
    print('điểm va đập: %d (%.1f / phiên có U) · trễ xác nhận TB %.2f nến' % (len(pv), len(pv) / ok, (pv['conf'] - pv['idx']).mean()))
    # profile ngày: chữ D, số hàng, HVN
    dsh, nrow, nh, nh25, bw, va_u, sg_u = [], [], [], [], [], [], []
    for k, (a, b) in enumerate(D.days):
        if b - a + 1 < 20 or not np.isfinite(D.unit_day[k]): continue
        st = V.profile_stats(D, a, b)
        if st is None: continue
        uu = D.unit_day[k]
        dsh.append(V.is_d_shape(st, p)); nrow.append(len(st['w']))
        res, sm = vm.find_hvn(st['pr'], st['w'])
        nh.append(len(res)); top = [r for r in res[:p['HVN_TOP']] if r[2] >= p['HVN_RATIO']]
        nh25.append(len(top))
        for i, pk, ratio in top:
            lo, hi = V.peak_sharpness(st['pr'], st['w'], i); bw.append((hi - lo) / uu)
        va_u.append((st['vah'] - st['val']) / uu); sg_u.append(st['sigma'] / uu)
    print('profile ngày: số hàng trung vị %d · chữ D %.0f %% số phiên · đỉnh FindHvn/phiên TB %.1f · HVN đạt tỉ lệ ≥ 2,5 (3 đỉnh đầu)/phiên TB %.2f, %.0f %% phiên có ≥ 1'
          % (np.median(nrow), 100 * np.mean(dsh), np.mean(nh), np.mean(nh25), 100 * np.mean(np.array(nh25) >= 1)))
    if bw: print('bề rộng dải HVN ngày (×U) p10/50/90: %s · vùng giá trị ngày (×U) trung vị %.1f · σ ngày (×U) trung vị %.2f'
                 % (np.round(np.percentile(bw, [10, 50, 90]), 3).tolist(), np.median(va_u), np.median(sg_u)))
    # cụm: bề rộng khoảng va đập, tỉ lệ có hợp lưu, số mức mỗi phiên
    span, ng, nlev, nhv = [], [], [], []
    for j in range(D.n - 1):
        if not np.isfinite(D.U[j + 1]): continue
        for z in eng.zones(j):
            span.append((z['pmax'] - z['pmin']) / z['u']); ng.append(z['ngroup'])
    for d in range(len(D.days)):
        if not np.isfinite(D.unit_day[d]): continue
        lv = V.day_levels(D, d, p); nlev.append(len(lv)); nhv.append(sum(L['name'].startswith('hvn') for L in lv))
    span, ng = np.array(span), np.array(ng)
    print('cụm ≥ 3 lần (mỗi nến M30 đếm một lần): khoảng va đập pmax − pmin (×U) p10/50/90: %s · %% cụm có hợp lưu ≥ 1 / ≥ 2 / ≥ 3 nhóm: %.0f / %.0f / %.1f'
          % (np.round(np.percentile(span, [10, 50, 90]), 3).tolist(), 100 * (ng >= 1).mean(), 100 * (ng >= 2).mean(), 100 * (ng >= 3).mean()))
    print('số mức hợp lưu mỗi phiên: TB %.1f (trong đó HVN %.1f)' % (np.mean(nlev), np.mean(nhv)))


def rong(res, df):
    """Bảng độ rộng như rong.py: % điểm đảo trong ±h quanh tâm, vùng thật (hợp lưu ≥ 1) so với vùng dời."""
    A, F, C = res['A'], res['F'], res['C']
    t = ((df['typ'] == 'that') & (df['ngroup'] >= 1)).values; d = (df['typ'] == 'doi').values
    off = df['off'].values
    print('| Nửa rộng h (×U) | thật: % điểm đảo trong ±h | dời | thật: % khớp ở mép gần | thật: thắng 1:2 / R | dời: thắng 1:2 / R |')
    print('|---|---|---|---|---|---|')
    for h in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50):
        f, r, rr = trade(A, F, C, h, BUF, 2.0)
        def wr(m):
            mm = m & f; dec = mm & (r != 0)
            return '%.1f %% / %+.3f' % (100 * (r[dec] == 1).mean(), rr[mm].mean())
        print('| %.2f | %.1f | %.1f | %.0f | %s | %s |' % (h, 100 * (np.abs(off[t]) <= h).mean(), 100 * (np.abs(off[d]) <= h).mean(), 100 * f[t].mean(), wr(t), wr(d)))
    for nm, m in (('vùng thật', t), ('vùng dời', d)):
        x = np.abs(off[m]); x = x[~np.isnan(x) & (x <= 0.75)]
        print('%s: trong các lần đảo cách tâm ≤ 0,75 U, nửa rộng phủ 50/70/80 %% = %s (n = %d)' % (nm, np.percentile(x, [50, 70, 80]).round(2).tolist(), len(x)))


def tol_scan(D, p):
    """Dung sai hợp lưu / bề rộng cụm: tỉ lệ cụm có hợp lưu và mật độ vẽ khi đổi TOL, WC (chỉ để xem độ nhạy, KHÔNG chọn lại)."""
    print('| TOL (×U) | WC (×U) | cụm ≥ 3 lần / nến | % cụm có hợp lưu | % cụm ≥ 2 nhóm | vùng vẽ TB | % thời gian có vùng | % thời gian có vàng |')
    print('|---|---|---|---|---|---|---|---|')
    for tol, wc in ((0.05, 0.30), (0.10, 0.30), (0.15, 0.30), (0.20, 0.30), (0.10, 0.20), (0.10, 0.40)):
        q = dict(p); q['TOL'] = tol; q['WC'] = wc
        eng = V.Engine(D, q)
        nz, n1, n2, ns, hs, hg, nb = 0, 0, 0, 0, 0, 0, 0
        for j in range(D.n - 1):
            if not np.isfinite(D.U[j + 1]): continue
            zs = eng.zones(j); sh = V.display(D, zs, j, float(D.m30['c'][j]), q)
            nb += 1; nz += len(zs); n1 += sum(z['ngroup'] >= 1 for z in zs); n2 += sum(z['ngroup'] >= 2 for z in zs)
            ns += len(sh); hs += len(sh) >= 1; hg += any(z['gold'] for z in sh)
        print('| %.2f | %.2f | %.1f | %.0f | %.0f | %.2f | %.0f | %.1f |' % (tol, wc, nz / nb, 100 * n1 / max(nz, 1), 100 * n2 / max(nz, 1), ns / nb, 100 * hs / nb, 100 * hg / nb))


if cmd == 'eval':
    final_eval.run(TAG, {})
elif cmd == 'bang':
    D = Data(); p = dict(V.P); eng = V.Engine(D, p)
    t = pd.to_datetime(D.m30['t'])
    print('# %s — %s → %s · %d nến M30' % (sym.upper(), t[0], t[-1], D.n))
    print('\n## Cấu tạo'); structure(D, eng, p)
    print('\n## Mật độ'); density(D, eng, p)
    res, df = load()
    print('\nsự kiện: %d · phiên có sự kiện: %d · lần quay lại vùng được vẽ / phiên: %.2f'
          % (len(df), df['day'].nunique(), ((df['typ'] == 'that') & df['shown'].astype(bool)).sum() / df['day'].nunique()))
    print('\n## Gộp cả kỳ'); print(table(df))
    print('\n## Theo tháng (gọn)'); print(mini(df, 'thang'))
    for th, d in df.groupby('thang'):
        print('\n### %s' % th); print(table(df, df['thang'] == th, with_ci=False))
    print('\n## Độ rộng'); rong(res, df)
    print('\n## Độ nhạy TOL / WC'); tol_scan(D, p)
elif cmd == 'full':
    res, df = load()
    print('# 2,3 năm (chot2) cắt theo quý'); print(mini(df, 'quy'))
    late = df['t'].values >= np.datetime64('2026-07-28T21:30')
    print('\n## 2,3 năm, riêng phần từ 2026-07-28 21:30 (cùng kỳ với GC một hợp đồng)'); print(table(df, late))
    print('\n## 2,3 năm, TEST (từ 2025-11-01)'); print(table(df, df['t'].values >= np.datetime64('2025-11-01'), with_ci=False))
    print('\n## 2,3 năm, tất cả'); print(table(df, with_ci=False))
elif cmd == 'thang':
    # mật độ vùng được vẽ theo tháng (để thấy tác động của "chỗ nối" bắt nhầm trên NQ tháng 11)
    D = Data(); p = dict(V.P); eng = V.Engine(D, p)
    t = pd.to_datetime(D.m30['t'])
    rows = []
    for j in range(D.n - 1):
        if not np.isfinite(D.U[j + 1]) or D.seg_of[j] != D.seg_of[j + 1]: continue
        sh = V.display(D, eng.zones(j), j, float(D.m30['c'][j]), p)
        rows.append((t[j + 1].strftime('%Y-%m'), len(sh)))
    a = pd.DataFrame(rows, columns=['thang', 'n'])
    print('| Tháng | nến M30 | vùng vẽ TB | % thời gian có ≥ 1 vùng |'); print('|---|---|---|---|')
    for th, g in a.groupby('thang'):
        print('| %s | %d | %.2f | %.0f |' % (th, len(g), g['n'].mean(), 100 * (g['n'] >= 1).mean()))
