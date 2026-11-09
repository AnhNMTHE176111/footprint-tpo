# -*- coding: utf-8 -*-
"""VÙNG cho setup A-v4 (plan `plans/BENZO-A-V4-plan.md` mục 2.1). KHÔNG sửa kernel.py — chỉ gọi hàm của kernel.

Mỗi vùng là một dict:
    name   tên vùng (khoá đếm "≤ 2 lệnh/(phiên, vùng, chiều)"), vd 'VWAP_D', 'HVN_W1', 'VAH_D'
    ztype  loại vùng để báo cáo: VWAP_W, VWAP_D, HVN_W, HVN_D, VAH_D, VAL_D, VAH_EU, VAL_EU, IB_H, IB_L, BAND_CU, VAH_DEV, VAL_DEV
    lo, hi mảng giá theo nến M1 (NaN = vùng chưa có / không dùng ở nến đó). Vùng điểm: lo = hi.
    dyn    True = vùng ĐỘNG (VWAP, VA đang hình thành): cạnh E lấy giá trị TẠI nến đang xét.
           False = vùng CỐ ĐỊNH: E chốt lúc mở trạng thái phá; đổi giá trị ⇒ trạng thái về NGỦ.
    band   True = dải có bề rộng (HVN tuần, band VA cũ): M5 đóng ngoài phía ĐỐI DIỆN ⇒ hủy trạng thái.
    sl_far True = SL đặt qua MÉP XA của dải (HVN tuần). False = SL qua E ± 1 (vùng điểm; band VA cũ như V3).
    rank   hạng hoà khi hai vùng cùng nến cùng khoảng cách (nhỏ = ưu tiên): VWAP_W > VWAP_D > HVN_W > HVN_D > VAH/VAL_D > VA Âu/IB.
    lab    (chỉ band cũ) mảng nhãn nguồn theo nến: 'EU' / 'IB' / 'Y' (để khoá đếm giống V3).

Không nhìn trước: HVN tuần chỉ từ tuần CME đã đóng (kernel.week_hvn: tuần W−3..W−1); HVN ngày / VA ngày từ phiên đầy đủ gần
nhất TRƯỚC phiên này (kernel._zones 'yday'/'hvn_day'); VWAP gồm nến hiện tại (đã đóng); VA Âu chốt 19:00, IB chốt 20:20
(kernel.zone_columns). VA đang hình thành tại nến i = VA của profile các nến <= nến cuối của M5 gần nhất đã đóng.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import kernel as K

WARM = 30                 # VWAP chỉ làm E khi phiên/tuần đã >= 30 nến (mượn Warm=30 của setup B; vị trí trong phiên >= 30)
HVN_BAND_FRAC = 0.90      # dải HVN tuần: nới từ đỉnh tới khi volume hàng < 90% đỉnh (ProfileEngine.PeakSharpness)
HVN_BAND_MAX = 2.0        # kẹp bề rộng dải HVN tuần <= 2,0 giá đối xứng quanh đỉnh (dẫn từ trần SL 4 giá; không phải tham số tự do)
VA_DEV_MIN_BARS = 120     # VA đang hình thành: chỉ dùng khi phiên đã >= 120 nến
RANK = {'VWAP_W': 1, 'VWAP_D': 2, 'HVN_W': 3, 'HVN_D': 4, 'VAH_D': 5, 'VAL_D': 5, 'VAH_DEV': 5, 'VAL_DEV': 5,
        'VAH_EU': 6, 'VAL_EU': 6, 'IB_H': 6, 'IB_L': 6, 'BAND_CU': 6}
ZTYPES_NEW = ('VWAP_W', 'VWAP_D', 'HVN_W', 'HVN_D', 'VAH_D', 'VAL_D')
ZTYPES_PLUS = ZTYPES_NEW + ('VAH_EU', 'VAL_EU', 'IB_H', 'IB_L')


def peak_sharpness(rows_int, vol, peak_price, frac=HVN_BAND_FRAC):
    """Port ProfileEngine.PeakSharpness: từ hàng đỉnh nới lên/xuống từng hàng (0,2 giá) chừng nào hàng kề TỒN TẠI và
    volume >= frac × volume hàng đỉnh (volume THÔ, không làm mượt). Đỉnh không có trong profile ⇒ (đỉnh, đỉnh)."""
    step = K.CONST['tick'] * K.CONST['row_ticks']
    d = dict(zip(np.asarray(rows_int).tolist(), np.asarray(vol, float).tolist()))
    pr = int(round(peak_price / step))
    if pr not in d:
        return float(peak_price), float(peak_price)
    thr = frac * d[pr]
    lo = hi = pr
    while (lo - 1) in d and d[lo - 1] >= thr:
        lo -= 1
    while (hi + 1) in d and d[hi + 1] >= thr:
        hi += 1
    return round(lo * step, 6), round(hi * step, 6)


def clamp_band(lo, hi, peak, width=HVN_BAND_MAX):
    """Kẹp dải về rộng <= width, đối xứng quanh đỉnh."""
    h = width / 2.0
    return max(lo, peak - h), min(hi, peak + h)


def week_profile(ctx, sno, sp):
    """Profile gộp 3 tuần CME đã đóng — ĐÚNG cách chọn phiên của kernel._Ctx.week_hvn (copy công thức, không gọi lại
    để lấy được profile). Trả (rows, vol) hoặc None."""
    st = ctx.st
    W = int(st['week_no'].loc[sno])
    wk = st['week_no'].to_numpy()
    inwin = (wk >= W - K.CONST['week_lookback']) & (wk <= W - 1)
    m = inwin & (st.index.to_numpy() >= max(sp, 0)) & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
    snos = [int(x) for x in st.index[m] if int(x) in ctx.prof.full]
    return K._agg_profiles([ctx.prof.full[x] for x in snos])


def session_levels(df, prof, ctx=None):
    """{session_no: dict(hvn_w=[(peak, lo, hi, lo_raw, hi_raw)], hvn_w_partial, hvn_d=[gia], vah_d, val_d)} — chỉ dữ liệu TRƯỚC phiên."""
    ctx = ctx or K._Ctx(df, prof)
    out = {}
    for s in ctx.st.index:
        s = int(s)
        z = K._zones(ctx, s, None, naked=False)
        sp = ctx.last_splice(s)
        rec = dict(hvn_w=[], hvn_w_partial=None, hvn_d=[p for p, _ in (z['hvn_day'] or [])], vah_d=np.nan, val_d=np.nan)
        if z['yday']:
            rec['vah_d'], rec['val_d'] = z['yday']['vah'], z['yday']['val']
        if z['hvn_week'] is not None:
            rec['hvn_w_partial'] = bool(z['hvn_week']['partial'])
            agg = week_profile(ctx, s, sp)
            peaks = [p for p, _ in z['hvn_week']['hvn']]
            if peaks:
                # kiểm: HVN tính lại trên profile gộp phải trùng kernel.week_hvn
                p2 = [x for x in K.find_hvn(K.Profiles.row_price(agg[0]), agg[1])[:K.CONST['hvn_max']] if x[1] >= K.CONST['hvn_gate']]
                assert [round(a, 6) for a, _ in p2] == [round(a, 6) for a in peaks], (s, p2, peaks)
            for p in peaks:
                lr, hr = peak_sharpness(agg[0], agg[1], p)
                lo, hi = clamp_band(lr, hr, p)
                rec['hvn_w'].append((float(p), float(lo), float(hi), float(lr), float(hr)))
        out[s] = rec
    return out


def dev_va(df, levels):
    """VA 70% ĐANG HÌNH THÀNH của phiên hiện tại tại mỗi nến i = VA của profile các nến từ đầu phiên tới nến CUỐI của M5 gần
    nhất đã đóng (<= i); NaN khi phiên < VA_DEV_MIN_BARS nến. levels = DataFrame per-level (bar_idx, price, volume).
    Trả (vah, val) mảng theo nến."""
    n = len(df)
    vah = np.full(n, np.nan)
    val = np.full(n, np.nan)
    step = K.CONST['tick'] * K.CONST['row_ticks']
    pos = pd.Index(df['bar_idx'].to_numpy()).get_indexer(levels['bar_idx'].to_numpy())
    ok = pos >= 0
    lv = pd.DataFrame({'pos': pos[ok], 'r': np.rint(levels['price'].to_numpy()[ok] / step).astype(np.int64),
                       'v': levels['volume'].to_numpy(float)[ok]}).groupby(['pos', 'r'], sort=True)['v'].sum().reset_index()
    lp_pos = lv['pos'].to_numpy()
    a_idx = np.searchsorted(lp_pos, np.arange(n), 'left')
    b_idx = np.searchsorted(lp_pos, np.arange(n), 'right')
    R, V = lv['r'].to_numpy(), lv['v'].to_numpy()
    closed_lp = set(np.flatnonzero(m5_close_mask(df)).tolist())
    st = K.session_table(df)
    for s in st.index:
        a, b = int(st['start_pos'].loc[s]), int(st['end_pos'].loc[s])
        acc = {}
        cur = (np.nan, np.nan)
        for i in range(a, b + 1):
            for k in range(a_idx[i], b_idx[i]):
                acc[R[k]] = acc.get(R[k], 0.0) + V[k]
            if i in closed_lp and (i - a) >= VA_DEV_MIN_BARS and acc:
                rows = np.array(sorted(acc))
                _, h, l = K.value_area(K.Profiles.row_price(rows), [acc[r] for r in rows])
                cur = (h, l)
            if (i - a) >= VA_DEV_MIN_BARS:
                vah[i], val[i] = cur
    return vah, val


def m5_close_mask(df):
    """True tại nến M1 là nến CUỐI của một nến M5 (gộp như kernel.m5_bars: mốc 5 phút UTC, không xuyên phiên) VÀ nến M5 đó đã
    biết là đóng: còn nến sau nó trong dữ liệu, hoặc chính nó là phút thứ 5 (phút % 5 == 4). Quy tắc này giữ cho chạy trên
    dữ liệu bị cắt cho đúng kết quả của chạy đầy đủ (nến M5 dở dang ở cuối đoạn cắt chưa tính là đóng)."""
    n = len(df)
    if n == 0:
        return np.zeros(0, bool)
    m5 = K.m5_bars(df)
    lp = m5['last_pos'].to_numpy()
    out = np.zeros(n, bool)
    out[lp] = True
    if not (df['t_utc'].iloc[n - 1].minute % 5 == 4):
        out[n - 1] = False
    return out


def _arr(n):
    return np.full(n, np.nan)


def build_zones(df, zc, slev, zset='new', hvn_w_band=True, va_dev=None):
    """Danh sách vùng (xem docstring module).
    zset: 'old' = band V3 (VA Âu/IB ở pha Mỹ, VA hôm qua ở pha khác) | 'new' = 6 loại mục 2.1 | 'plus' = 6 loại + VA Âu/IB (pha Mỹ).
    hvn_w_band=False: HVN tuần là ĐIỂM (độ nhạy). va_dev=(vah, val): thay VAH_D/VAL_D bằng VA đang hình thành (biến thể chỉ báo)."""
    n = len(df)
    sno = df['session_no'].to_numpy()
    st = K.session_table(df)
    start = st['start_pos'].to_numpy()[sno] if n else np.zeros(0, int)
    wk = df['week_no'].to_numpy()
    wstart = pd.Series(np.arange(n)).groupby(wk).transform('min').to_numpy()
    posin, wposin = np.arange(n) - start, np.arange(n) - wstart
    Z = []
    if zset == 'old':
        ph = df['phase'].to_numpy()
        us = ph == 'US'
        eh, el = zc['eu_vah'].to_numpy(float), zc['eu_val'].to_numpy(float)
        ih, il = zc['ib_hi'].to_numpy(float), zc['ib_lo'].to_numpy(float)
        yh, yl = zc['yd_vah'].to_numpy(float), zc['yd_val'].to_numpy(float)
        use_eu = us & ~np.isnan(eh)
        use_ib = us & np.isnan(eh) & ~np.isnan(ih)
        use_y = (~us) & ~np.isnan(yh)
        bh = np.where(use_eu, eh, np.where(use_ib, ih, np.where(use_y, yh, np.nan)))
        bl = np.where(use_eu, el, np.where(use_ib, il, np.where(use_y, yl, np.nan)))
        lab = np.where(use_eu, 'EU', np.where(use_ib, 'IB', np.where(use_y, 'Y', '')))
        Z.append(dict(name='BAND', ztype='BAND_CU', lo=bl, hi=bh, dyn=False, band=True, sl_far=False, rank=RANK['BAND_CU'], lab=lab))
        return Z
    vw_w = np.where(wposin >= WARM, zc['vwap_w'].to_numpy(float), np.nan)
    vw_d = np.where(posin >= WARM, zc['vwap_d'].to_numpy(float), np.nan)
    Z.append(dict(name='VWAP_W', ztype='VWAP_W', lo=vw_w, hi=vw_w, dyn=True, band=False, sl_far=False, rank=RANK['VWAP_W']))
    Z.append(dict(name='VWAP_D', ztype='VWAP_D', lo=vw_d, hi=vw_d, dyn=True, band=False, sl_far=False, rank=RANK['VWAP_D']))
    hw = [(_arr(n), _arr(n)) for _ in range(K.CONST['hvn_max'])]
    hd = [_arr(n) for _ in range(K.CONST['hvn_max'])]
    vah, val = _arr(n), _arr(n)
    for s in st.index:
        a, b = int(st['start_pos'].loc[s]), int(st['end_pos'].loc[s]) + 1
        rec = slev[int(s)]
        for k, x in enumerate(rec['hvn_w'][:K.CONST['hvn_max']]):
            p, lo, hi = x[0], x[1], x[2]
            if not hvn_w_band:
                lo = hi = p
            hw[k][0][a:b], hw[k][1][a:b] = lo, hi
        for k, p in enumerate(rec['hvn_d'][:K.CONST['hvn_max']]):
            hd[k][a:b] = p
        vah[a:b], val[a:b] = rec['vah_d'], rec['val_d']
    for k in range(K.CONST['hvn_max']):
        Z.append(dict(name='HVN_W%d' % (k + 1), ztype='HVN_W', lo=hw[k][0], hi=hw[k][1], dyn=False, band=hvn_w_band, sl_far=hvn_w_band,
                      rank=RANK['HVN_W']))
    for k in range(K.CONST['hvn_max']):
        Z.append(dict(name='HVN_D%d' % (k + 1), ztype='HVN_D', lo=hd[k], hi=hd[k], dyn=False, band=False, sl_far=False, rank=RANK['HVN_D']))
    if va_dev is None:
        Z.append(dict(name='VAH_D', ztype='VAH_D', lo=vah, hi=vah, dyn=False, band=False, sl_far=False, rank=RANK['VAH_D']))
        Z.append(dict(name='VAL_D', ztype='VAL_D', lo=val, hi=val, dyn=False, band=False, sl_far=False, rank=RANK['VAL_D']))
    else:
        dh, dl = va_dev
        Z.append(dict(name='VAH_DEV', ztype='VAH_DEV', lo=dh, hi=dh, dyn=True, band=False, sl_far=False, rank=RANK['VAH_DEV']))
        Z.append(dict(name='VAL_DEV', ztype='VAL_DEV', lo=dl, hi=dl, dyn=True, band=False, sl_far=False, rank=RANK['VAL_DEV']))
    if zset == 'plus':
        us = df['phase'].to_numpy() == 'US'
        eh, el = zc['eu_vah'].to_numpy(float), zc['eu_val'].to_numpy(float)
        ih, il = zc['ib_hi'].to_numpy(float), zc['ib_lo'].to_numpy(float)
        use_eu = us & ~np.isnan(eh)
        use_ib = us & np.isnan(eh) & ~np.isnan(ih)
        for nm, arr, m in (('VAH_EU', eh, use_eu), ('VAL_EU', el, use_eu), ('IB_H', ih, use_ib), ('IB_L', il, use_ib)):
            v = np.where(m, arr, np.nan)
            Z.append(dict(name=nm, ztype=nm, lo=v, hi=v, dyn=False, band=False, sl_far=False, rank=RANK[nm]))
    return Z


def zone_table(Z):
    """Bảng cột (DataFrame) lo/hi của mọi vùng — dùng cho test cắt dữ liệu và đối chứng ĐC2."""
    d = {}
    for z in Z:
        d[z['name'] + '_lo'] = z['lo']
        d[z['name'] + '_hi'] = z['hi']
    return pd.DataFrame(d)
