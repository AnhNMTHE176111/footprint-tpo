#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
final_eval.py — chạy BẢN THAM CHIẾU (vung_manh.Engine) trên toàn bộ dữ liệu, ghi:
  (a) mật độ vùng trên chart ở mỗi nến M30;
  (b) mọi "lần giá quay lại" vùng thật ('that') và vùng đối chứng dời 1,5–4 U ('doi'), kèm đường đi M1.
Chạy: python final_eval.py ten [KHOA=giatri ...]    vd: python final_eval.py goc   |   python final_eval.py n2 NMIN=2
"""
import os, pickle, sys, zlib
import numpy as np
from vm import *
import vung_manh as V

HT, AWAY_MIN, H_PATH, BACK, N_SHIFT = 0.75, 1.25, 600, 1500, 3


def out_path(tag):
    return os.path.join(os.path.dirname(CACHE), 'vm_final_%s.pkl' % tag)


def run(tag, over):
    p = dict(V.P); p.update(over)
    D = Data()
    eng = V.Engine(D, p)
    h, l, c = D.m30['h'], D.m30['l'], D.m30['c']
    m1 = D.m1
    m1gap = np.r_[0, np.diff(m1['t'].astype('datetime64[s]').astype(np.int64))] / 60.0
    ev, paths, dens = [], [], []

    def add_event(j, cen, typ, z, extra):
        u = D.U[j + 1]
        lo, hi = cen - HT * u, cen + HT * u
        if not (l[j + 1] <= hi and h[j + 1] >= lo): return
        if l[j] <= hi and h[j] >= lo: return
        s = 1 if l[j] > hi else -1
        a0 = max(j - BACK, 0)
        segm = D.seg_of[a0:j + 1] == D.seg_of[j + 1]
        ov = (l[a0:j + 1] <= hi) & (h[a0:j + 1] >= lo) & segm
        w = np.where(ov)[0]
        b = a0 + (w[-1] if len(w) else int(np.argmax(segm)) - 1)
        if b + 1 > j: return
        away = ((h[b + 1:j + 1].max() - cen) if s > 0 else (cen - l[b + 1:j + 1].min())) / u
        if away < AWAY_MIN: return
        s1, e1 = D.m1_ptr[j + 1], D.m1_ptr[j + 2]
        hit = np.where(m1['l'][s1:e1] <= hi)[0] if s > 0 else np.where(m1['h'][s1:e1] >= lo)[0]
        if len(hit) == 0: return
        st = s1 + hit[0]
        en = min(st + H_PATH, len(m1['t']))
        brk = np.where((m1gap[st + 1:en] > 100) | (D.seg_of[m1['i30'][st + 1:en]] != D.seg_of[j + 1]))[0]
        if len(brk): en = st + 1 + brk[0]
        A = np.full(H_PATH, np.nan, np.float32); F = A.copy(); C = A.copy()
        if s > 0:
            A[:en - st] = (m1['l'][st:en] - cen) / u; F[:en - st] = (m1['h'][st:en] - cen) / u; C[:en - st] = (m1['c'][st:en] - cen) / u
        else:
            A[:en - st] = (cen - m1['h'][st:en]) / u; F[:en - st] = (cen - m1['l'][st:en]) / u; C[:en - st] = (cen - m1['c'][st:en]) / u
        # số lần giá đóng nến M30 XUYÊN HẲN qua vùng kể từ điểm va đập đầu tiên
        cc = c[z['oldest']:j + 1]; off = cen - (z['lo'] + z['hi']) / 2
        stt = np.where(cc > z['hi'] + off, 1, np.where(cc < z['lo'] + off, -1, 0)); stt = stt[stt != 0]
        e = dict(j=j, t=D.m30['t'][j + 1], day=int(D.day_of[j + 1]), typ=typ, cen=cen, u=u, side=s, away=away, since=j - b,
                 hw=(z['hi'] - z['lo']) / 2 / u, n=z['n'], n_hi=z['n_hi'], ngroup=z['ngroup'], hvn=z['hvn'], gold=z['gold'],
                 names='+'.join(z['names']), age=j - z['newest'], ndays=z['ndays'], cross=int((np.diff(stt) != 0).sum()) if len(stt) > 1 else 0)
        e.update(extra)
        ev.append(e); paths.append((A, F, C))

    for j in range(D.n - 2):
        u = D.U[j + 1]
        if not np.isfinite(u) or D.seg_of[j] != D.seg_of[j + 1]: continue
        zs = eng.zones(j)
        px = c[j]
        conf = [z for z in zs if z['ngroup'] >= 1]
        near = [z for z in conf if min(abs(z['lo'] - px), abs(z['hi'] - px)) <= 3 * u or (z['lo'] <= px <= z['hi'])]
        dens.append((j, len(zs), len(conf), len(near), sum(z['gold'] for z in conf), sum(z['gold'] for z in near),
                     sum(1 for z in near if z['hi'] < px), sum(1 for z in near if z['lo'] > px)))
        shown = set((q['lo'], q['hi']) for q in V.display(D, zs, j, float(px), p))
        for z in zs:
            cen = (z['lo'] + z['hi']) / 2
            add_event(j, cen, 'that', z, dict(shown=(z['lo'], z['hi']) in shown))
            for rep in range(N_SHIFT):
                rs = np.random.RandomState(zlib.crc32(('%d_%d' % (z['oldest'], rep)).encode()) & 0x7fffffff)
                delta = rs.choice([-1, 1]) * rs.uniform(1.5, 4.0) * u
                add_event(j, cen + delta, 'doi', z, dict(rep=rep, shown=False))
        if j % 5000 == 0: print('  nến', j, 'sự kiện', len(ev), flush=True)
    A = np.stack([q[0] for q in paths]); F = np.stack([q[1] for q in paths]); C = np.stack([q[2] for q in paths])
    with open(out_path(tag), 'wb') as f:
        pickle.dump(dict(ev=ev, A=A, F=F, C=C, dens=np.array(dens), p=p), f, protocol=4)
    print('lưu', out_path(tag), len(ev))


if __name__ == '__main__':
    tag = sys.argv[1]
    over = {}
    for a in sys.argv[2:]:
        k, v = a.split('=')
        over[k] = (v == 'True') if v in ('True', 'False') else (float(v) if '.' in v else int(v))
    run(tag, over)
