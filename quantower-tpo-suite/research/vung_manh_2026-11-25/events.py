#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
events.py — sinh "lần giá quay lại vùng" cho 3 loại tâm vùng, cùng một bộ máy chấm:
  'cum'  : cụm điểm va đập (n điểm, n >= 1) — vùng đề xuất khi n >= ngưỡng và có hợp lưu
  'muc'  : từng mức hợp lưu đứng một mình (VWAP hôm qua ±1σ, VWAP tuần trước ±1σ, VAH/VAL, HVN)
  'doi'  : đối chứng — tâm cụm (n >= 2) DỜI đi 1,5–4 U ngẫu nhiên (cố định theo điểm neo của cụm)

Nhân quả: vùng tại nến M30 j chỉ dùng điểm va đập đã XÁC NHẬN (conf <= j) và mức của các phiên ĐÃ ĐÓNG.
Lần quay lại = nến M30 j+1 chạm dải [c − HT, c + HT] trong khi nến j không chạm, và kể từ lần chạm dải
gần nhất giá đã rời tâm >= AWAY_MIN × U. Đường đi M1 sau lúc chạm được lưu (đơn vị U, đã đổi dấu:
dương = phía giá đi tới = phía kỳ vọng bật lại) để chấm mọi độ rộng / dừng lỗ / mục tiêu về sau.

Chạy: python events.py [k] [r] [LB] [wc]   (mặc định 2 1.0 5 0.5)  → pickle trong thư mục đệm.
"""
import os, pickle, sys, zlib
import numpy as np
from vm import *

HT = 0.75          # nửa dải kích hoạt (×U)
AWAY_MIN = 1.25    # tối thiểu đã rời tâm (×U) kể từ lần chạm dải gần nhất
H_PATH = 600       # số nến M1 lưu sau lúc chạm
BACK = 1500        # nhìn lại tối đa (nến M30) để tìm lần chạm gần nhất
HVN_DAYS = 5       # HVN ngày: lấy từ 5 phiên đã đóng gần nhất
HVN_MIN_RATIO = 2.5
HVN_TOP = 3
N_SHIFT = 3


def day_levels(D, d):
    """Mức hợp lưu dùng trong phiên d — chỉ từ dữ liệu ĐÃ ĐÓNG trước phiên d. Trả list dict(name, lo, hi, ...)."""
    out = []
    a0 = D.days[d][0]
    seg = D.seg_of[a0]
    last_sp = max([s for s in D.splices if s <= a0], default=0)

    def hvn_of(a, b, tag, src):
        pr, w = D.rows_over(a, b)
        res, sm = find_hvn(pr, w)
        if sm is None: return
        tot = w.sum()
        poc, vah, val = value_area(pr, w)
        for i, p, ratio in res[:HVN_TOP]:
            if ratio < HVN_MIN_RATIO: continue
            lo, hi = node_band(pr, sm, i, 0.70)
            out.append(dict(name=tag, lo=pr[lo], hi=pr[hi], peak=p, ratio=ratio, share=w[lo:hi + 1].sum() / tot,
                            src=src, end=b, poc_pos=(poc - pr[0]) / max(pr[-1] - pr[0], 1e-9),
                            va_frac=(vah - val) / max(pr[-1] - pr[0], 1e-9), is_poc=abs(p - poc) <= 1.0,
                            rng=pr[-1] - pr[0]))

    # ---- ngày hôm qua = phiên đã đóng gần nhất có >= MIN_DAY_BARS nến, cùng hợp đồng
    y = d - 1
    while y >= 0 and (D.days[y][1] - D.days[y][0] + 1) < MIN_DAY_BARS: y -= 1
    if y >= 0 and D.seg_of[D.days[y][0]] == seg:
        a, b = D.days[y]
        m, s = D.vwap_sigma(a, b)
        pr, w = D.rows_over(a, b)
        poc, vah, val = value_area(pr, w)
        for nm, v in (('vwap_d', m), ('vwap_d_tren', m + s), ('vwap_d_duoi', m - s), ('vah_d', vah), ('val_d', val)):
            out.append(dict(name=nm, lo=v, hi=v))
    # ---- HVN ngày: các phiên đã đóng trong HVN_DAYS phiên gần nhất
    cnt, yy = 0, d - 1
    while yy >= 0 and cnt < HVN_DAYS:
        a, b = D.days[yy]
        if D.seg_of[a] != seg: break
        if b - a + 1 >= MIN_DAY_BARS:
            hvn_of(a, b, 'hvn_d', d - yy); cnt += 1
        yy -= 1
    # ---- tuần trước (cắt phần trước chỗ nối như C#)
    w = D.week_of[a0]
    if w >= 1:
        a, b = D.weeks[w - 1]
        a = max(a, last_sp)
        if b - a + 1 >= 60:
            m, s = D.vwap_sigma(a, b)
            pr, ww = D.rows_over(a, b)
            poc, vah, val = value_area(pr, ww)
            for nm, v in (('vwap_w', m), ('vwap_w_tren', m + s), ('vwap_w_duoi', m - s), ('vah_w', vah), ('val_w', val)):
                out.append(dict(name=nm, lo=v, hi=v))
            hvn_of(a, b, 'hvn_w', 1)
    # ---- tuần này tính tới hết hôm qua (>= 60 nến M30)
    a = max(D.weeks[w][0], last_sp); b = a0 - 1
    if b - a + 1 >= 60:
        hvn_of(a, b, 'hvn_w', 0)
    return out


def fast_cluster(p, wc):
    """Như vm.cluster nhưng nhanh hơn; p đã sắp tăng dần. Trả list (lo_idx, hi_idx_exclusive mask)."""
    alive = np.ones(len(p), bool)
    res = []
    while alive.any():
        ids = np.where(alive)[0]
        q = p[ids]
        cnt = np.searchsorted(q, q + wc + 1e-9, side='right') - np.arange(len(q))
        a = int(np.argmax(cnt))                 # hoà → neo giá thấp hơn
        mem = ids[a:a + cnt[a]]
        res.append(mem)
        alive[mem] = False
    return res


def run(k=2, r=1.0, LB=5, wc=0.5, verbose=True):
    D = Data()
    h, l, c = D.m30['h'], D.m30['l'], D.m30['c']
    pv = pivots(D, k=k, r=r)
    order = np.argsort(pv['conf'], kind='stable')
    pv = pv[order]
    conf = pv['conf']
    m1 = D.m1
    m1gap = np.r_[0, np.diff(m1['t'].astype('datetime64[s]').astype(np.int64))] / 60.0
    ev, paths = [], []
    levels_cache = {}
    last_key, zones = None, []

    def add_event(j, cen, typ, meta):
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
        if s > 0: hit = np.where(m1['l'][s1:e1] <= hi)[0]
        else: hit = np.where(m1['h'][s1:e1] >= lo)[0]
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
        e = dict(j=j, t=D.m30['t'][j + 1], day=int(D.day_of[j + 1]), typ=typ, cen=cen, u=u, side=s, away=away, since=j - b, plen=en - st)
        e.update(meta)
        ev.append(e); paths.append((A, F, C))

    for j in range(D.n - 2):
        d = D.day_of[j + 1]
        u = D.U[j + 1]
        if not np.isfinite(u): continue
        if D.seg_of[j] != D.seg_of[j + 1]: continue
        if d not in levels_cache:
            levels_cache.clear(); levels_cache[d] = day_levels(D, d)
        lv = levels_cache[d]
        # ---- cụm va đập
        hi_ptr = np.searchsorted(conf, j, side='right')
        lb_start = D.days[max(0, d - LB)][0]
        key = (hi_ptr, lb_start, d)
        if key != last_key:
            last_key = key
            act = pv[:hi_ptr]
            act = act[(act['idx'] >= lb_start) & (D.seg_of[act['idx']] == D.seg_of[j + 1])]
            zones = []
            if len(act):
                o = np.argsort(act['price'], kind='stable'); act = act[o]
                for mem in fast_cluster(act['price'], wc * u):
                    g = act[mem]
                    zones.append(dict(n=len(g), pmin=g['price'].min(), pmax=g['price'].max(), pmean=g['price'].mean(),
                                      pmed=float(np.median(g['price'])), n_hi=int((g['kind'] > 0).sum()),
                                      anchor=int(g['idx'].min()), newest=int(g['idx'].max()),
                                      ndays=len(set(D.day_of[g['idx']].tolist())),
                                      plast=float(g['price'][np.argmax(g['idx'])]),
                                      pidx=g['idx'].tolist(), pprice=g['price'].tolist(), pkind=g['kind'].tolist()))
        for z in zones:
            cen = (z['pmin'] + z['pmax']) / 2
            add_event(j, cen, 'cum', dict(z=z, levels=lv))
            if z['n'] >= 2:
                for rep in range(N_SHIFT):
                    rs = np.random.RandomState(zlib.crc32(('%d_%d' % (z['anchor'], rep)).encode()) & 0x7fffffff)
                    delta = rs.choice([-1, 1]) * rs.uniform(1.5, 4.0) * u
                    add_event(j, cen + delta, 'doi', dict(z=z, levels=lv, rep=rep, delta=delta))
        for q, L in enumerate(lv):
            add_event(j, (L['lo'] + L['hi']) / 2, 'muc', dict(level=L, levels=lv))
        if verbose and j % 5000 == 0: print('  nến', j, 'sự kiện', len(ev), flush=True)
    A = np.stack([p[0] for p in paths]); F = np.stack([p[1] for p in paths]); C = np.stack([p[2] for p in paths])
    return dict(ev=ev, A=A, F=F, C=C, cfg=dict(k=k, r=r, LB=LB, wc=wc, HT=HT, AWAY_MIN=AWAY_MIN))


def out_path(k, r, LB, wc):
    return os.path.join(os.path.dirname(CACHE), 'vm_ev_k%d_r%s_LB%d_wc%s.pkl' % (k, r, LB, wc))


if __name__ == '__main__':
    a = sys.argv[1:]
    k = int(a[0]) if len(a) > 0 else 2
    r = float(a[1]) if len(a) > 1 else 1.0
    LB = int(a[2]) if len(a) > 2 else 5
    wc = float(a[3]) if len(a) > 3 else 0.5
    res = run(k, r, LB, wc)
    from collections import Counter
    print(Counter(e['typ'] for e in res['ev']))
    with open(out_path(k, r, LB, wc), 'wb') as f:
        pickle.dump(res, f, protocol=4)
    print('lưu', out_path(k, r, LB, wc))
