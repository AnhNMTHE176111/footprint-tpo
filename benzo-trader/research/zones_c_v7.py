# -*- coding: utf-8 -*-
"""VÙNG cho setup C-v7 (plan `research/PLAN-C-v3.md` mục 2, 4.1): HÀNH LANG hỗ trợ / kháng cự (S/R) từ bộ vùng hiển thị VCL v5.

Hành lang = khoảng giữa mặt dưới vùng kháng cự gần nhất phía trên và mặt trên vùng hỗ trợ gần nhất phía dưới (cạnh 'near'),
ĐÓNG BĂNG từ lúc sinh. Máy chỉ dùng nến <= i và dòng VCL `bar <= i`. KHÔNG sửa kernel.py / zones_c_v6.py / benzo_vcl.py.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import benzo_vcl as BV  # noqa: E402
import zones_c_v6 as Z6  # noqa: E402

# ------------------------------------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC (PLAN-C-v3 mục 4.1)
MIN_W = 6.0
FACE = 'near'
TREND_RUNS = K.CONST['m5_trend_runs']
TREND_DIST = K.CONST['m5_trend_dist']
MASK_ROUND_ONLY = 8
NAME_HI, NAME_LO = 'SR_HI', 'SR_LO'


def load_sr(df) -> pd.DataFrame:
    """Bộ vùng hiển thị VCL v5 theo nến, sắp theo (bar, lo, eid)."""
    rec = BV.load_rec(df)
    for c in ('bar', 'lo', 'hi', 'eid', 'mask'):
        assert c in rec.columns, c
    assert int(rec['bar'].max()) < len(df)
    return rec.sort_values(['bar', 'lo', 'eid'], kind='stable').reset_index(drop=True)


class SrIndex:
    """Mảng numpy + [start, end) theo bar (searchsorted) để lấy dòng của nến i."""

    def __init__(self, rec, n, shift_by_bar=None, mask_ok=None):
        r = rec[rec['bar'] < n]
        if mask_ok is not None:
            r = r[mask_ok(r['mask'].to_numpy())]
        r = r.sort_values(['bar', 'lo', 'eid'], kind='stable')
        self.bar = r['bar'].to_numpy()
        d = np.zeros(len(r)) if shift_by_bar is None else np.asarray(shift_by_bar, float)[self.bar]
        self.lo = r['lo'].to_numpy(float) + d
        self.hi = r['hi'].to_numpy(float) + d
        self.eid = r['eid'].to_numpy()
        self.mask = r['mask'].to_numpy()
        ar = np.arange(n + 1)
        self.start = np.searchsorted(self.bar, ar, side='left')
        self.end = np.searchsorted(self.bar, ar, side='right')

    def rows(self, i):
        a, b = self.start[i], self.end[i]
        return slice(a, b)


def sr_corridors(df, idx, shift=None, mask_ok=None, face=FACE, min_w=MIN_W, rec=None) -> dict:
    """Máy hành lang (PLAN mục 2.2). idx = SrIndex (đã áp shift/mask) HOẶC None (khi đó dùng rec + shift + mask_ok).
    Trả dict(frame=DataFrame[sr_lo, sr_hi, sr_id], log, funnel, internal_mode5 (theo hàng M5 của K.m5_bars(df)))."""
    n = len(df)
    if idx is None:
        sh = None if shift is None else np.asarray(shift, float)[df['session_no'].to_numpy()]
        idx = SrIndex(rec, n, sh, mask_ok)
    cl = df['close'].to_numpy(float)
    sno = df['session_no'].to_numpy()
    first = np.r_[True, sno[1:] != sno[:-1]]
    bad = df['splice'].to_numpy() | df['thin'].to_numpy()
    m5 = K.m5_bars(df)
    last_pos = m5['last_pos'].to_numpy()
    is_last = np.full(n, -1, np.int64)
    is_last[last_pos] = np.arange(len(m5))
    band_lo = np.full(n, np.nan)
    band_hi = np.full(n, np.nan)
    cid = np.full(n, -1, np.int64)
    mode5 = np.empty(len(m5), object)
    mode5[:] = 'NA'
    log, funnel = [], dict(thu=0, trong_vung=0, thieu_phia=0, hep=0, sinh=0, het_phien=0, trend=0, mat_vung=0, het_du_lieu=0)
    cur = None
    r, prev = 0, 0
    nid = 0
    for i in range(n):
        if first[i]:
            if cur is not None:
                cur['end'], cur['why'] = i, 'het_phien'
                funnel['het_phien'] += 1
                cur = None
            r, prev = 0, 0
        painted = cur                                              # bước 2: tô TRƯỚC khi cập nhật
        if painted is not None:
            band_lo[i], band_hi[i], cid[i] = painted['lo'], painted['hi'], painted['id']
        j = is_last[i]
        if j >= 0:                                                 # bước 3: nến M5 vừa đóng ở i
            if painted is None:
                mode5[j] = 'NA'
                r, prev = 0, 0
            else:
                c = cl[i]
                if c > painted['hi']:
                    out, dist = 1, c - painted['hi']
                elif c < painted['lo']:
                    out, dist = -1, painted['lo'] - c
                else:
                    out, dist = 0, 0.0
                if out == 0:
                    mode5[j] = 'BALANCE'
                    r, prev = 0, 0
                else:
                    r = r + 1 if out == prev else 1
                    prev = out
                    trend = r >= TREND_RUNS and dist >= TREND_DIST
                    mode5[j] = ('TREND_' if trend else 'BREAK_') + ('UP' if out > 0 else 'DN')
                    if trend and cur is not None:
                        cur['end'], cur['why'] = i, 'trend'
                        funnel['trend'] += 1
                        cur = None
        sl = idx.rows(i)
        if cur is not None:                                        # bước 4: mất vùng
            e = idx.eid[sl]
            ms = np.flatnonzero(e == cur['eid_s'])
            mr = np.flatnonzero(e == cur['eid_r'])
            if not len(ms) or not len(mr):
                cur['end'], cur['why'] = i, 'mat_vung'
                funnel['mat_vung'] += 1
                cur = None
            else:
                k = sl.start
                if abs(idx.lo[k + ms[0]] - cur['s_lo']) > 0.1 + 1e-9 or abs(idx.hi[k + mr[0]] - cur['r_hi']) > 0.1 + 1e-9 or \
                        abs(idx.hi[k + ms[0]] - cur['s_hi']) > 0.1 + 1e-9 or abs(idx.lo[k + mr[0]] - cur['r_lo']) > 0.1 + 1e-9:
                    cur['moved'] = True
        if cur is None and not bad[i]:                             # bước 5: thử sinh
            lo_, hi_, ei, mk = idx.lo[sl], idx.hi[sl], idx.eid[sl], idx.mask[sl]
            if len(lo_):
                funnel['thu'] += 1
                c = cl[i]
                if ((lo_ <= c) & (c <= hi_)).any():
                    funnel['trong_vung'] += 1
                else:
                    ab = np.flatnonzero(lo_ > c)
                    be = np.flatnonzero(hi_ < c)
                    if not len(ab) or not len(be):
                        funnel['thieu_phia'] += 1
                    else:
                        a = ab[np.lexsort((ei[ab], lo_[ab]))[0]]
                        b = be[np.lexsort((ei[be], -hi_[be]))[0]]
                        lof = hi_[b] if face == 'near' else lo_[b]
                        hif = lo_[a] if face == 'near' else hi_[a]
                        if hif - lof < min_w - 1e-9:
                            funnel['hep'] += 1
                        else:
                            cur = dict(id=nid, sno=int(sno[i]), lo=float(lof), hi=float(hif), eid_s=int(ei[b]), eid_r=int(ei[a]),
                                       s_lo=float(lo_[b]), s_hi=float(hi_[b]), r_lo=float(lo_[a]), r_hi=float(hi_[a]),
                                       s_mask=int(mk[b]), r_mask=int(mk[a]), birth=i, end=n, why='het_du_lieu', moved=False)
                            nid += 1
                            funnel['sinh'] += 1
                            log.append(cur)
    if cur is not None:
        funnel['het_du_lieu'] += 1
    sid = df['session_id'].to_numpy()
    tv = df['t_vn'].to_numpy()
    for x in log:
        x['session'] = sid[x['birth']]
        x['t_birth'] = str(tv[x['birth']])[:16]
        x['width'] = x['hi'] - x['lo']
        x['life'] = x['end'] - x['birth']
    fr = pd.DataFrame({'sr_lo': band_lo, 'sr_hi': band_hi, 'sr_id': cid}, index=df.index)
    return dict(frame=fr, log=log, funnel=funnel, internal_mode5=mode5, m5=m5)


def layer_sr(df, template, corr):
    """L4 (PLAN 2.3): (zc, names, mf) với band = hành lang. names theo nến lấy từ band của mode (nến M5 đã đóng gần nhất)."""
    fr = corr['frame']
    zc = Z6.band_zcols(template, fr['sr_lo'].to_numpy(float), fr['sr_hi'].to_numpy(float), poc=None)
    mf = K.mode_frame(df, zc, K.m5_bars(df, zc))
    has = (mf['band_src'].to_numpy() != '')
    hn = np.where(has, NAME_HI, '').astype(object)
    ln = np.where(has, NAME_LO, '').astype(object)
    return zc, (hn, ln), mf
