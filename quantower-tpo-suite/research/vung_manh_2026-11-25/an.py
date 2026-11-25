#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
an.py — chấm kết quả các "lần quay lại vùng" do events.py sinh ra.

Đơn vị: U = TB (High−Low) nến M30 của 5 phiên đã đóng gần nhất. Đường đi đã đổi dấu:
  A = mép bất lợi của nến M1 (thấp = xuyên sâu), F = mép có lợi, C = giá đóng; 0 = tâm vùng; dương = phía giá đi tới.
"""
import pickle, sys
import numpy as np
import pandas as pd
from vm import *
from events import out_path

FAM = {'vwap_d': 'VWAP ngày', 'vwap_d_tren': 'VWAP ngày', 'vwap_d_duoi': 'VWAP ngày',
       'vwap_w': 'VWAP tuần', 'vwap_w_tren': 'VWAP tuần', 'vwap_w_duoi': 'VWAP tuần',
       'vah_d': 'VA ngày', 'val_d': 'VA ngày', 'vah_w': 'VA tuần', 'val_w': 'VA tuần',
       'hvn_d': 'HVN ngày', 'hvn_w': 'HVN tuần'}
SPLIT_DATE = np.datetime64('2025-11-01')


def load(k=2, r=1.0, LB=5, wc=0.5):
    with open(out_path(k, r, LB, wc), 'rb') as f:
        return pickle.load(f)


def confl(e, pad, tol, hvn_filter=None):
    """Các họ mức trùng dải cụm [pmin−pad, pmax+pad] (đơn vị giá; pad, tol ×U). Trả (set họ, list tên)."""
    z = e['z']; u = e['u']
    off = e.get('delta', 0.0)
    lo, hi = z['pmin'] + off - (pad + tol) * u, z['pmax'] + off + (pad + tol) * u
    fam, names = set(), []
    for L in e['levels']:
        if L['lo'] <= hi and L['hi'] >= lo:
            if L['name'].startswith('hvn') and hvn_filter is not None and not hvn_filter(L, e): continue
            fam.add(FAM[L['name']]); names.append(L['name'])
    return fam, names


def frame(res, pad=0.15, tol=0.0, hvn_filter=None):
    rows = []
    for i, e in enumerate(res['ev']):
        r = dict(i=i, typ=e['typ'], t=e['t'], day=e['day'], side=e['side'], u=e['u'], away=e['away'], since=e['since'],
                 plen=e['plen'], cen=e['cen'])
        if e['typ'] in ('cum', 'doi'):
            z = e['z']
            fam, names = confl(e, pad, tol, hvn_filter)
            r.update(n=z['n'], span=(z['pmax'] - z['pmin']) / e['u'], n_hi=z['n_hi'], ndays=z['ndays'],
                     age=e['j'] - z['newest'], nfam=len(fam), hvn=any(f.startswith('HVN') for f in fam),
                     fams='+'.join(sorted(fam)), names='+'.join(sorted(set(names))),
                     same=(z['n'] - z['n_hi'] if e['side'] > 0 else z['n_hi']) / z['n'],
                     d_mean=(z['pmean'] - e['cen']) * e['side'] / e['u'], d_med=(z['pmed'] - e['cen']) * e['side'] / e['u'],
                     d_last=(z['plast'] - e['cen']) * e['side'] / e['u'],
                     d_ext=((z['pmin'] if e['side'] > 0 else z['pmax']) - e['cen']) * e['side'] / e['u'])
        else:
            L = e['level']
            r.update(name=L['name'], fam=FAM[L['name']], lw=(L['hi'] - L['lo']) / e['u'],
                     ratio=L.get('ratio', np.nan), share=L.get('share', np.nan), src=L.get('src', -1),
                     poc_pos=L.get('poc_pos', np.nan), va_frac=L.get('va_frac', np.nan), is_poc=L.get('is_poc', False))
        rows.append(r)
    df = pd.DataFrame(rows)
    df['test'] = df['t'].values >= SPLIT_DATE
    return df


def turn_offset(A, F, X=1.0):
    """Điểm đảo chiều đầu tiên sau khi chạm dải: mép bất lợi sâu nhất trước khi giá bật lại >= X×U từ đó.
    Trả offset so với tâm (×U; dương = quay đầu trước khi tới tâm, âm = xuyên qua tâm). NaN = hết đường đi chưa bật."""
    A = np.where(np.isnan(A), np.inf, A)
    rm = np.minimum.accumulate(A, axis=1)
    Fz = np.where(np.isnan(F), -np.inf, F)
    ok = (Fz[:, 1:] - rm[:, :-1]) >= X
    first = ok.argmax(axis=1)
    has = ok.any(axis=1)
    off = rm[np.arange(len(A)), first]
    return np.where(has, off, np.nan)


def trade(A, F, C, h, buf, R, h_lo=None):
    """Lệnh chờ ở mép gần (tâm + h), dừng lỗ ở mép xa − buf (tâm − h_lo − buf), mục tiêu R lần rủi ro.
    h, h_lo: vô hướng hoặc mảng theo sự kiện (×U). Trả (khớp?, kết quả: 1 thắng / -1 thua / 0 hết giờ, R thực)."""
    n, T = A.shape
    h = np.broadcast_to(np.asarray(h, float), (n,))
    hl = h if h_lo is None else np.broadcast_to(np.asarray(h_lo, float), (n,))
    An = np.where(np.isnan(A), np.inf, A); Fn = np.where(np.isnan(F), -np.inf, F)
    ent = An <= h[:, None]
    filled = ent.any(axis=1)
    e = ent.argmax(axis=1)
    idx = np.arange(T)[None, :]
    risk = h + hl + buf
    stop = (An <= (-hl - buf)[:, None]) & (idx >= e[:, None])
    tgt = (Fn >= (h + R * risk)[:, None]) & (idx > e[:, None])
    si = np.where(stop.any(axis=1), stop.argmax(axis=1), T + 1)
    ti = np.where(tgt.any(axis=1), tgt.argmax(axis=1), T + 2)
    res = np.where(ti < si, 1, np.where(si <= T, -1, 0))
    last = np.array([C[i, np.where(~np.isnan(C[i]))[0][-1]] if (~np.isnan(C[i])).any() else np.nan for i in range(n)]) if (res == 0).any() else np.zeros(n)
    rr = np.where(res == 1, R, np.where(res == -1, -1.0, (last - h) / risk))
    rr = np.clip(rr, -1, R)
    return filled, res, rr


def boot_diff(x, gx, y, gy, B=1000, seed=7):
    """Khoảng 5–95% của hiệu trung bình (x − y), lấy mẫu lại theo KHỐI NGÀY (gx, gy = mã ngày)."""
    rs = np.random.RandomState(seed)
    days = np.unique(np.r_[gx, gy])
    sx = pd.Series(x).groupby(gx).agg(['sum', 'count']).reindex(days).fillna(0).values
    sy = pd.Series(y).groupby(gy).agg(['sum', 'count']).reindex(days).fillna(0).values
    out = []
    for _ in range(B):
        k = rs.randint(0, len(days), len(days))
        a, b = sx[k].sum(0), sy[k].sum(0)
        if a[1] > 0 and b[1] > 0: out.append(a[0] / a[1] - b[0] / b[1])
    return np.percentile(out, [5, 95])
