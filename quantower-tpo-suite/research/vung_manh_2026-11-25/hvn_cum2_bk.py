#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum2_bk.py — bán kính hiển thị hộp HVN (HVN-CUM-V2.md mục 3) và trạng thái cuối dữ liệu NQ (ca người dùng báo).
  python hvn_cum2_bk.py nq|gc
Đếm số hộp HVN được vẽ ở mỗi nến M30 (đã đủ "rời xa", đã bỏ hộp trùng > 50 % như StrongZones.HvnBoxes) theo bán kính.
"""
import os, sys, tempfile
sym = sys.argv[1]
os.environ['VM_CACHE'] = os.path.join(os.environ.get('VM_CACHE_DIR', tempfile.gettempdir()), 'vm1_%s.pkl' % sym)
import numpy as np, pandas as pd
import vm
from vm import Data
import vung_manh as V
if sym == 'nq': vm.SPLICE_JUMP = 1e12
SC = 2.5 if sym == 'nq' else 1.0


def boxes(D, eng, j, p, rad_d, rad_w, cap=0):
    u = D.U[j + 1]; now = float(D.m30['c'][j]); d = int(D.day_of[j + 1])
    cand = []
    for L in eng.levels(d):
        if not L['name'].startswith('hvn') or not V.hvn_ok(D, L, j, u, p): continue
        dist = now - L['hi'] if now > L['hi'] else L['lo'] - now if now < L['lo'] else 0.0
        if dist > (rad_w if L['name'] == 'hvn_w' else rad_d) * u: continue
        cand.append(dict(L, dist=dist))
    out = []
    for c in sorted(cand, key=lambda x: (-x['end'], 0 if x['name'] == 'hvn_d' else 1, -x['ratio'], x['lo'])):
        dup = False
        for k in out:
            inter = min(k['hi'], c['hi']) - max(k['lo'], c['lo']); small = min(k['hi'] - k['lo'], c['hi'] - c['lo'])
            if inter > 0 and inter > 0.5 * small: dup = True
        if not dup: out.append(c)
    if cap:
        now_ = now
        keep = [c for c in out if c['dist'] == 0]
        for sd in (1, -1):
            g = sorted([c for c in out if c['dist'] > 0 and ((c['hi'] < now_) == (sd > 0))], key=lambda c: c['dist'])
            keep += g[:cap]
        out = keep
    return out


def main():
    D = Data(); t = pd.to_datetime(D.m30['t'])
    for mode in ('cum', 'cum2'):
        p = dict(V.P, HVN_MODE=mode); eng = V.Engine(D, p)
        print('\n## %s · %s' % (sym.upper(), 'v1' if mode == 'cum' else 'v2'))
        print('| Bán kính hộp ngày / tuần (× U) | hộp vẽ TB mỗi nến | % nến có 0 / 1 / 2 / 3 / ≥ 4 hộp | nhiều nhất |')
        print('|---|---|---|---|')
        js = [j for j in range(D.n - 1) if np.isfinite(D.U[j + 1]) and D.seg_of[j] == D.seg_of[j + 1]]
        dd = []
        for rd, rw, cap in ((4, 4, 0), (6, 6, 0), (8, 8, 0), (6, 10, 0), (10, 10, 0), (1e9, 1e9, 0), (6, 6, 2), (8, 8, 2), (6, 10, 2), (8, 12, 2), (10, 10, 2), (1e9, 1e9, 2), (8, 8, 1), (10, 10, 1)):
            n = np.array([len(boxes(D, eng, j, p, rd, rw, cap)) for j in js])
            print('| %s / %s%s | %.2f | %s | %d |' % ('∞' if rd > 1e6 else '%g' % rd, '∞' if rw > 1e6 else '%g' % rw, (' · tối đa %d hộp mỗi phía' % cap) if cap else '', n.mean(),
                                                  ' / '.join('%.0f' % (100 * x) for x in [(n == 0).mean(), (n == 1).mean(), (n == 2).mean(), (n == 3).mean(), (n >= 4).mean()]), n.max()))
        # khoảng cách từ giá tới hộp gần nhất mỗi phía
        for j in js:
            for c in boxes(D, eng, j, p, 1e9, 1e9): dd.append((c['dist'] / D.U[j + 1], c['name']))
        a = np.array([x for x, _ in dd])
        print('khoảng cách giá → mép hộp (× U), mọi hộp đủ điều kiện: p25/50/75/90 = %s · %% trong 4 U: %.0f · 6 U: %.0f · 8 U: %.0f · 10 U: %.0f'
              % (np.round(np.percentile(a, [25, 50, 75, 90]), 1).tolist(), 100 * (a <= 4).mean(), 100 * (a <= 6).mean(), 100 * (a <= 8).mean(), 100 * (a <= 10).mean()))
        if sym == 'nq':
            j = D.n - 2
            u = D.U[j + 1]; now = float(D.m30['c'][j]); d = int(D.day_of[j + 1])
            print('cuối dữ liệu: nến j đóng %s · giá %.2f · U %.2f' % (t[j], now * SC, u * SC))
            for L in eng.levels(d):
                if L['name'].startswith('hvn'):
                    dist = now - L['hi'] if now > L['hi'] else L['lo'] - now if now < L['lo'] else 0.0
                    print('   %s %.2f–%.2f · %.1f %% · kỳ kết thúc %s · rời xa %s · cách giá %.0f điểm = %.2f U'
                          % (L['name'], L['lo'] * SC, L['hi'] * SC, 100 * L['ratio'], str(t[L['end']])[:16], V.hvn_ok(D, L, j, u, p), dist * SC, dist / u))
            zs = eng.zones(j)
            for z in sorted(zs, key=lambda z: z['lo']):
                print('   cụm va đập %.2f–%.2f · %d lần · %s' % (z['lo'] * SC, z['hi'] * SC, z['n'], ' + '.join(z['names']) or '—'))
            for z in V.display(D, zs, j, now, p): print('   VẼ %.2f–%.2f %s %s' % (z['lo'] * SC, z['hi'] * SC, z['color'], z['label']))
            wk = int(D.week_of[D.days[d][0]]); a0 = D.weeks[wk][0]
            print('   tuần này: thấp %.2f (%s) · cao %.2f' % (D.m30['l'][a0:j + 1].min() * SC, t[a0 + int(np.argmin(D.m30['l'][a0:j + 1]))], D.m30['h'][a0:j + 1].max() * SC))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
