# -*- coding: utf-8 -*-
"""VÙNG cho setup B-v3 (plan `plans/BENZO-B-v3-plan.md` mục 1 + 2.2): thêm vùng HỖ TRỢ / KHÁNG CỰ (S/R) vào 12 mức / 8 loại của B-v2.
KHÔNG sửa kernel.py / zones_b_v2.py.

Hai họ mới (đều SAU 12 mức v2 trong thứ tự ưu tiên):
  PDH, PDL            : đỉnh / đáy của phiên đầy đủ gần nhất đã đóng (cùng phiên `q` mà kernel dùng cho VAH/VAL/POC hôm qua). Hai chiều. ztype 'PDHL'.
  VCL_R1..7, VCL_S1..7: cạnh GẦN của vùng hiển thị Vùng Canh Lệnh v5, gán KHE theo eid (trực tuyến, chỉ nhìn lùi).
                        VCL_Rk = `lo` của eid ở khe k, chỉ chiều M = +1 (giá đi lên chạm cạnh dưới ⇒ SELL).
                        VCL_Sk = `hi` của eid ở khe k, chỉ chiều M = −1 (giá đi xuống chạm cạnh trên ⇒ BUY). ztype 'VCL'.
Không nhìn trước: rec tại nến t chỉ dùng nến <= t; gán khe + runlen chỉ nhìn lùi.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import zones_b_v2 as ZB  # noqa: E402

VCL_SLOTS_MAX = 7            # số vùng hiển thị tối đa mỗi nến của engine v5
VCL_WARM = 4                 # khe phải giữ CÙNG một eid >= 4 nến liên tiếp (cụm + Z tại i−1 cùng một eid, đúng cho N <= 4)
R_NAMES = tuple('VCL_R%d' % k for k in range(1, VCL_SLOTS_MAX + 1))
S_NAMES = tuple('VCL_S%d' % k for k in range(1, VCL_SLOTS_MAX + 1))
M_NAMES = tuple('VCL_M%d' % k for k in range(1, VCL_SLOTS_MAX + 1))
ZONE_ORDER_V3 = ZB.ZONE_ORDER + ('PDH', 'PDL') + R_NAMES + S_NAMES
ZTYPE_OF_V3 = dict(ZB.ZTYPE_OF)
ZTYPE_OF_V3.update({'PDH': 'PDHL', 'PDL': 'PDHL'})
ZTYPE_OF_V3.update({nm: 'VCL' for nm in R_NAMES + S_NAMES + M_NAMES})
ZTYPES_V2 = ('VWAP_W', 'VWAP_D') + ZB.ZTYPES_NEW        # 8 loại
ZTYPES_SR = ('PDHL', 'VCL')
ZONES_OLD, ZONES_V2, ZONES_V3 = ZB.ZONES_OLD, ZB.ZONES_V2, ZONE_ORDER_V3
EXTRA3_NAMES = ZONE_ORDER_V3[2:]


def names_of3(ztypes):
    """Tên mức (theo thứ tự ưu tiên v3) thuộc các loại ztypes."""
    return tuple(nm for nm in ZONE_ORDER_V3 if ZTYPE_OF_V3[nm] in ztypes)


# ------------------------------------------------------------------ căn hàng rec ↔ df
def check_align(df, base=None):
    """Assert: chuỗi nến mà engine VCL (vcl5.load + K._enrich, sort theo datetime) dựng ra cùng độ dài và cùng `datetime` với df."""
    import benzo_vcl as BV  # noqa: F401  (thêm vung-canh-lenh/research vào sys.path)
    import vcl5 as V5
    base = base or V5.BASE90
    raw = pd.read_csv(base + '_bars.csv', parse_dates=['datetime'])
    ref = K._enrich(raw.sort_values('datetime').reset_index(drop=True))
    assert len(ref) == len(df), 'lệch độ dài nến: engine VCL %d vs df %d' % (len(ref), len(df))
    assert (ref['datetime'].to_numpy() == df['datetime'].to_numpy()).all(), 'lệch datetime giữa engine VCL và df'


# ------------------------------------------------------------------ gán khe theo eid (trực tuyến)
def vcl_slots(rec, n):
    """rec: bảng VCL (cột bar, lo, hi, eid, …; bar = VỊ TRÍ nến). Trả dict lo[K,n], hi[K,n], eid[K,n] (−1 trống), runlen[K,n], K.
    Duyệt nến t tăng dần: khe giữ eid không còn ở nến t ⇒ giải phóng; eid mới (sắp theo lo tăng, rồi eid tăng) nhận khe trống số nhỏ nhất;
    eid đã giữ khe thì giữ tới hết đời; eid xuất hiện lại sau khi biến mất ⇒ raise. Chỉ dùng nến <= t."""
    rec = rec.sort_values(['bar', 'lo', 'eid'], kind='mergesort').reset_index(drop=True)
    bars = rec['bar'].to_numpy(np.int64)
    lo_a, hi_a, eid_a = rec['lo'].to_numpy(float), rec['hi'].to_numpy(float), rec['eid'].to_numpy(np.int64)
    Kmax = VCL_SLOTS_MAX
    lo = np.full((Kmax, n), np.nan)
    hi = np.full((Kmax, n), np.nan)
    eid = np.full((Kmax, n), -1, np.int64)
    runlen = np.zeros((Kmax, n), np.int64)
    holder = [-1] * Kmax          # eid đang giữ khe
    run = [0] * Kmax
    seen = set()
    where = {}                    # eid -> khe
    kused = 0
    starts = np.flatnonzero(np.r_[True, bars[1:] != bars[:-1]])
    ends = np.r_[starts[1:], len(bars)]
    prev_bar = -1
    for a, b in zip(starts, ends):
        t = int(bars[a])
        if t >= n:
            raise ValueError('rec.bar vượt chiều dài df')
        if t != prev_bar + 1:                      # nến không có vùng nào ⇒ mọi khe giải phóng (eid quay lại sẽ raise)
            for k in range(Kmax):
                holder[k], run[k] = -1, 0
            where.clear()
        prev_bar = t
        cur = {int(e): j for j, e in zip(range(a, b), eid_a[a:b])}
        for k in range(Kmax):                      # giải phóng khe có eid không còn
            if holder[k] != -1 and holder[k] not in cur:
                where.pop(holder[k], None)
                holder[k], run[k] = -1, 0
        for j in range(a, b):                      # đã sắp theo (lo, eid) ⇒ eid mới nhận khe trống nhỏ nhất theo thứ tự này
            e = int(eid_a[j])
            if e in where:
                continue
            if e in seen:
                raise ValueError('eid %d xuất hiện lại sau khi biến mất (nến %d)' % (e, t))
            k = next((q for q in range(Kmax) if holder[q] == -1), None)
            if k is None:
                raise ValueError('cần > %d khe VCL tại nến %d — dừng' % (Kmax, t))
            holder[k], run[k] = e, 0
            where[e] = k
            seen.add(e)
        for j in range(a, b):
            e = int(eid_a[j])
            k = where[e]
            run[k] += 1
            lo[k, t], hi[k, t], eid[k, t], runlen[k, t] = lo_a[j], hi_a[j], e, run[k]
            kused = max(kused, k + 1)
    assert kused <= VCL_SLOTS_MAX
    return dict(lo=lo, hi=hi, eid=eid, runlen=runlen, K=kused)


# ------------------------------------------------------------------ PDH / PDL
def pdhl(df, prof, ctx=None):
    """(pdh[n], pdl[n]): đỉnh / đáy phiên đầy đủ gần nhất đã đóng, hằng cho mọi nến phiên s. Không có `yday` ⇒ NaN."""
    ctx = ctx or K._Ctx(df, prof)
    n = len(df)
    pdh, pdl = np.full(n, np.nan), np.full(n, np.nan)
    hi, lo = df['high'].to_numpy(float), df['low'].to_numpy(float)
    st = ctx.st
    for s in st.index:
        a, b = int(st['start_pos'].loc[s]), int(st['end_pos'].loc[s]) + 1
        y = K._zones(ctx, int(s), None, naked=False)['yday']
        if y is None:
            continue
        q = int(y['session_no'])
        qa, qb = int(st['start_pos'].loc[q]), int(st['end_pos'].loc[q]) + 1
        pdh[a:b], pdl[a:b] = hi[qa:qb].max(), lo[qa:qb].min()
    return pdh, pdl


# ------------------------------------------------------------------ bảng vùng v3
def build_extra3(df, prof, ctx, lev, rec, slots=None):
    """dict tên -> (mảng, ztype, warm, mdirs) theo ZONE_ORDER_V3[2:]. 10 mức v2 + PDH/PDL: warm None, mdirs None. VCL_Rk: warm = runlen >= 4, (1,);
    VCL_Sk: warm = runlen >= 4, (−1,)."""
    ex2 = ZB.build_extra(df, prof, ctx, lev)
    sl = slots if slots is not None else vcl_slots(rec, len(df))
    pdh, pdl = pdhl(df, prof, ctx)
    out = {nm: (ex2[nm][0], ex2[nm][1], None, None) for nm in ZB.EXTRA_NAMES}
    out['PDH'] = (pdh, 'PDHL', None, None)
    out['PDL'] = (pdl, 'PDHL', None, None)
    for k in range(VCL_SLOTS_MAX):
        out[R_NAMES[k]] = (sl['lo'][k], 'VCL', sl['runlen'][k] >= VCL_WARM, (1,))
    for k in range(VCL_SLOTS_MAX):
        out[S_NAMES[k]] = (sl['hi'][k], 'VCL', sl['runlen'][k] >= VCL_WARM, (-1,))
    assert tuple(out) == EXTRA3_NAMES
    return out


def vcl_mid_extra(slots):
    """Phụ lục 3.7: 7 mức 'VCL_M1..7' = (lo+hi)/2, ztype 'VCL', warm = runlen >= 4, hai chiều."""
    return {M_NAMES[k]: ((slots['lo'][k] + slots['hi'][k]) / 2.0, 'VCL', slots['runlen'][k] >= VCL_WARM, None) for k in range(VCL_SLOTS_MAX)}


def vcl_any(extra3, df, tol=1.0):
    """(r_any[n], s_any[n]): trong các cạnh VCL_Rk (VCL_Sk) ĐANG ẤM tại j mà nến j CHẠM (|close − Z| <= tol hoặc râu chứa Z), lấy cạnh gần close
    nhất; không cạnh nào chạm ⇒ NaN. Dùng làm cột vùng cho ĐC2 (kernel.control_sample)."""
    cl, hi, lo = df['close'].to_numpy(float), df['high'].to_numpy(float), df['low'].to_numpy(float)
    res = []
    for names in (R_NAMES, S_NAMES):
        best = np.full(len(df), np.nan)
        bd = np.full(len(df), np.inf)
        for nm in names:
            z, _, warm, _ = extra3[nm]
            with np.errstate(invalid='ignore'):
                touch = ((np.abs(cl - z) <= tol) | ((lo <= z) & (z <= hi))) & np.asarray(warm, bool)
                d = np.abs(cl - z)
            take = touch & (d < bd)
            best[take] = z[take]
            bd[take] = d[take]
        res.append(best)
    return res[0], res[1]


def zone_table3(extra3, df):
    """DataFrame cột = mọi tên mức + 'VCL_R_ANY', 'VCL_S_ANY' (cho ĐC2 và test cắt dữ liệu)."""
    t = pd.DataFrame({nm: v[0] for nm, v in extra3.items()})
    r_any, s_any = vcl_any(extra3, df)
    t['VCL_R_ANY'], t['VCL_S_ANY'] = r_any, s_any
    return t


def shifted3(extra3, zc, delta_by_sno, sno):
    """Bản đồ vùng DỜI (ĐC1): mọi mức (VWAP động: zc + δ) cộng hằng δ[phiên]; GIỮ NGUYÊN warm và mdirs (danh tính vùng, không phải vị trí).
    Trả dict tên -> (mảng, ztype, warm, mdirs) theo ZONE_ORDER_V3."""
    d = np.asarray(delta_by_sno, float)[np.asarray(sno)]
    out = {'VWAP_W': (zc['vwap_w'].to_numpy(float) + d, 'VWAP_W', None, None), 'VWAP_D': (zc['vwap_d'].to_numpy(float) + d, 'VWAP_D', None, None)}
    for nm, (a, zt, w, m) in extra3.items():
        out[nm] = (np.asarray(a, float) + d, zt, w, m)
    return out


def overlap3(P, ents, extra3):
    """Số liệu mục 1.5.5 cho lệnh có ztype VCL / PDHL: (i) |Z − mức v2 gần nhất| tại i−1; (ii) tỉ lệ nến chạm cạnh VCL cũng nằm <= 1 giá từ một mức v2.
    Chỉ mô tả."""
    v2 = [P['Z'][nm] for nm in ZB.ZONE_ORDER]
    dist = []
    for e in ents:
        if e['ztype'] not in ZTYPES_SR:
            continue
        i = int(e['idx'])
        z = float(e['zprice'])
        ds = [abs(z - float(a[i - 1])) for a in v2 if a[i - 1] == a[i - 1]]
        dist.append(min(ds) if ds else np.nan)
    cl = P['cl']
    okb = P['okbar']
    near_v2 = np.zeros(P['n'], bool)
    for a in v2:
        with np.errstate(invalid='ignore'):
            near_v2 |= np.abs(cl - a) <= 1.0
    touch_any = np.zeros(P['n'], bool)
    for nm in R_NAMES + S_NAMES:
        touch_any |= P['touch'][nm] & P['warm'][nm]
    m = touch_any & okb
    return dict(dist=np.array(dist, float), frac_touch_near_v2=float((m & near_v2).sum() / max(m.sum(), 1)), n_touch=int(m.sum()))
