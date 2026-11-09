# -*- coding: utf-8 -*-
"""VÙNG cho setup B-v2 (plan `plans/BENZO-B-v2-plan.md` mục 1 + 2.2). KHÔNG sửa kernel.py — chỉ gọi hàm của kernel / zones_a_v4.

12 mức / 8 loại, mỗi mức là ĐIỂM (không dải), thứ tự = thứ tự ưu tiên trong setup_b_hap_thu.detect:
    VWAP_W, VWAP_D (động, đã có trong prepare) · POC_D, VAH_D, VAL_D (phiên đầy đủ gần nhất đã đóng = cột yd_* của kernel) ·
    HVN_D1..3 (kernel._zones['hvn_day']) · POC_W (MỚI: POC profile gộp các phiên tuần CME W−1) · HVN_W1..3 (đỉnh, kernel.week_hvn).
Không nhìn trước: mọi mức cố định được gán từ nến đầu phiên = kết quả của phiên/tuần ĐÃ ĐÓNG trước đó.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import kernel as K
import zones_a_v4 as ZA

ZONE_ORDER = ('VWAP_W', 'VWAP_D', 'POC_D', 'VAH_D', 'VAL_D', 'HVN_D1', 'HVN_D2', 'HVN_D3', 'POC_W', 'HVN_W1', 'HVN_W2', 'HVN_W3')
ZTYPE_OF = {nm: ('HVN_D' if nm.startswith('HVN_D') else 'HVN_W' if nm.startswith('HVN_W') else nm) for nm in ZONE_ORDER}
ZTYPES_NEW = ('POC_D', 'VAH_D', 'VAL_D', 'HVN_D', 'HVN_W', 'POC_W')
ZONES_OLD = ('VWAP_W', 'VWAP_D')
ZONES_V2 = ZONE_ORDER
MIN_WEEK_SESSIONS = 3            # POC_W cần >= 3 phiên đầy đủ, không thin, trong tuần W−1
EXTRA_NAMES = ZONE_ORDER[2:]     # các mức thêm (không gồm VWAP)


def names_of(ztypes):
    """Tên mức (theo thứ tự ưu tiên) thuộc các loại ztypes."""
    return tuple(nm for nm in ZONE_ORDER if ZTYPE_OF[nm] in ztypes)


def week_poc(ctx, sno, sp):
    """POC của profile gộp các phiên thuộc tuần CME W−1 (tuần đã đóng ngay trước tuần của phiên sno). Chỉ phiên >= 300 nến,
    không thin, sau chỗ nối (>= sp). Cần >= MIN_WEEK_SESSIONS phiên, không thì NaN. Cách chọn phiên sao chép kernel._Ctx.week_hvn."""
    st = ctx.st
    W = int(st['week_no'].loc[sno])
    wk = st['week_no'].to_numpy()
    m = (wk == W - 1) & (st.index.to_numpy() >= max(sp, 0)) & (st['n'].to_numpy() >= K.CONST['min_bars_prof']) & (~st['thin'].to_numpy())
    snos = [int(x) for x in st.index[m] if int(x) in ctx.prof.full]
    if len(snos) < MIN_WEEK_SESSIONS:
        return np.nan
    a = K._agg_profiles([ctx.prof.full[x] for x in snos])
    if a is None:
        return np.nan
    return float(K.value_area(K.Profiles.row_price(a[0]), a[1])[0])


def session_table_b(df, prof, ctx=None):
    """{session_no: dict(poc_d, vah_d, val_d, hvn_d=[..], poc_w, hvn_w=[đỉnh..], hvn_w_partial)} — chỉ dữ liệu TRƯỚC phiên."""
    ctx = ctx or K._Ctx(df, prof)
    slev = ZA.session_levels(df, prof, ctx)
    out = {}
    for s in ctx.st.index:
        s = int(s)
        z = K._zones(ctx, s, None, naked=False)
        rec = slev[s]
        out[s] = dict(poc_d=(z['yday']['poc'] if z['yday'] else np.nan), vah_d=rec['vah_d'], val_d=rec['val_d'],
                      hvn_d=list(rec['hvn_d'][:K.CONST['hvn_max']]), poc_w=week_poc(ctx, s, ctx.last_splice(s)),
                      hvn_w=[x[0] for x in rec['hvn_w'][:K.CONST['hvn_max']]], hvn_w_partial=rec['hvn_w_partial'])
    return out


def build_extra(df, prof, ctx=None, levels=None):
    """dict name -> (mảng giá theo nến, ztype) cho 10 mức thêm (POC_D..HVN_W3), theo thứ tự ưu tiên. NaN = mức không có ở phiên đó."""
    ctx = ctx or K._Ctx(df, prof)
    lev = levels or session_table_b(df, prof, ctx)
    n = len(df)
    arr = {nm: np.full(n, np.nan) for nm in EXTRA_NAMES}
    st = ctx.st
    for s in st.index:
        a, b = int(st['start_pos'].loc[s]), int(st['end_pos'].loc[s]) + 1
        r = lev[int(s)]
        arr['POC_D'][a:b], arr['VAH_D'][a:b], arr['VAL_D'][a:b], arr['POC_W'][a:b] = r['poc_d'], r['vah_d'], r['val_d'], r['poc_w']
        for k, p in enumerate(r['hvn_d']):
            arr['HVN_D%d' % (k + 1)][a:b] = p
        for k, p in enumerate(r['hvn_w']):
            arr['HVN_W%d' % (k + 1)][a:b] = p
    return {nm: (arr[nm], ZTYPE_OF[nm]) for nm in EXTRA_NAMES}


def zone_table(extra):
    """DataFrame cột = tên mức (cho test cắt dữ liệu + đối chứng ĐC2)."""
    return pd.DataFrame({nm: v[0] for nm, v in extra.items()})


def shifted(extra, zc, delta_by_sno, sno):
    """Bản đồ vùng DỜI: mọi mức (gồm VWAP động: zc + δ) cộng hằng δ[phiên]. delta_by_sno: mảng δ theo session_no;
    sno: mảng session_no theo nến. Trả dict name -> (mảng, ztype) theo ZONE_ORDER (VWAP_W, VWAP_D đầu)."""
    d = np.asarray(delta_by_sno, float)[np.asarray(sno)]
    out = {'VWAP_W': (zc['vwap_w'].to_numpy(float) + d, 'VWAP_W'), 'VWAP_D': (zc['vwap_d'].to_numpy(float) + d, 'VWAP_D')}
    for nm, (a, zt) in extra.items():
        out[nm] = (np.asarray(a, float) + d, zt)
    return out


def shift_matrix(nS, reps, lo, hi, seed):
    """Ma trận δ (nS, reps) sinh Y HỆT benzo_vcl.Data (dsh[:, 1:])."""
    rng = np.random.default_rng(seed)
    return rng.uniform(lo, hi, (nS, reps)) * rng.choice([-1.0, 1.0], (nS, reps))


def overlap_stats(lev, zc, df, clean_snos, tol=1.0):
    """Tỉ lệ trùng giữa các mức KHÁC loại (≤ tol giá) theo phiên sạch + trung vị khoảng cách giữa các loại + số phiên có từng mức.
    VWAP lấy giá trị tại nến CUỐI phiên (chỉ để mô tả, không dùng làm tín hiệu)."""
    st = K.session_table(df)
    pairs_close = pairs_tot = 0
    nlev = []
    dist = {}
    have = {nm: 0 for nm in ZONE_ORDER}
    for s in clean_snos:
        r = lev[int(s)]
        e = int(st['end_pos'].loc[s])
        L = [('VWAP_W', zc['vwap_w'].iloc[e]), ('VWAP_D', zc['vwap_d'].iloc[e]), ('POC_D', r['poc_d']), ('VAH_D', r['vah_d']),
             ('VAL_D', r['val_d'])] + [('HVN_D%d' % (k + 1), p) for k, p in enumerate(r['hvn_d'])] + [('POC_W', r['poc_w'])] + \
            [('HVN_W%d' % (k + 1), p) for k, p in enumerate(r['hvn_w'])]
        L = [(nm, float(p)) for nm, p in L if p == p]
        for nm, _ in L:
            have[nm] += 1
        nlev.append(len(L))
        for i in range(len(L)):
            for j in range(i + 1, len(L)):
                a, b = L[i], L[j]
                ta, tb = ZTYPE_OF[a[0]], ZTYPE_OF[b[0]]
                if ta == tb:
                    continue
                pairs_tot += 1
                dd = abs(a[1] - b[1])
                pairs_close += dd <= tol
                key = tuple(sorted((ta, tb)))
                dist.setdefault(key, []).append(dd)
    return dict(pairs_close=pairs_close, pairs_tot=pairs_tot, frac=pairs_close / max(pairs_tot, 1),
                med_dist={k: float(np.median(v)) for k, v in dist.items()}, have=have, n_sessions=len(clean_snos),
                levels_per_session=float(np.mean(nlev)) if nlev else np.nan)
