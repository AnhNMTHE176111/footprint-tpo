"""Hai thước nhìn lại (PLAN 4.3) — CHỈ để chấm điểm trong nghiên cứu, dùng volume cả trước lẫn sau ô, không dùng giá, không bao giờ vào indicator.
  Thước cùng giờ : giá trị > 0 của cùng khung giờ trong ngày (rộng W), trên các ngày giao dịch d-5..d+5 có trong dữ liệu (ở hai đầu: những ngày có, tối thiểu 6).
  Thước quanh nó : giá trị > 0 của mọi nến cách không quá H = max(60, 4 x phút) phút về hai phía, kể cả chính nó.
Ô thuộc nhóm q lớn nhất của một tập n giá trị  <=>  số giá trị >= nó trong tập <= floor(q x n)   (cùng quy ước "lớn hơn hẳn giá trị lớn thứ K+1").
Dùng chung cho chấm (ds có sside) và Big Trade (một bên)."""
import numpy as np, pandas as pd
from sa_common import nb_window_ge


def rulers(ds):
    """Trả (ge_same, n_same, ge_around, n_around) theo mẫu."""
    V = int(ds.sval.max()) + 1
    nd = len(ds.days); ns_ = ds.nslot
    sday = ds.dayi[ds.sbar].astype(np.int64); sslot = ds.slot[ds.sbar].astype(np.int64)
    H = np.bincount((sday * ns_ + sslot) * V + ds.sval, minlength=nd * ns_ * V).reshape(nd, ns_, V).astype(np.int64)
    C = np.concatenate([np.zeros((1, ns_, V), np.int64), np.cumsum(H, 0)], 0)
    d = np.arange(nd); lo = np.maximum(0, d - 5); hi = np.minimum(nd, d + 6)
    Wn = C[hi] - C[lo]                                   # (nd, nslot, V)
    del C, H
    Suf = np.cumsum(Wn[:, :, ::-1], 2)[:, :, ::-1]        # Suf[d, s, v] = số giá trị >= v
    ge_same = Suf[sday, sslot, ds.sval]; n_same = Suf[sday, sslot, 1] if V > 1 else np.zeros(ds.ns, np.int64)
    del Suf, Wn
    Hm = max(60, 4 * ds.m)
    t = ds.t.values
    lo = np.searchsorted(t, t - np.timedelta64(Hm, 'm'), 'left').astype(np.int64)
    hi = np.searchsorted(t, t + np.timedelta64(Hm, 'm'), 'right').astype(np.int64)
    ge_ar, nn = nb_window_ge(ds.sval, ds.s0, ds.s1, lo, hi, V)
    return ge_same, n_same, ge_ar, nn[ds.sbar]


def top_sets(ds, mask_bars):
    """Chỉ số mẫu của 20 giá trị lớn nhất mỗi ngày giao dịch và 5 lớn nhất mỗi (ngày x phiên), trong các nến mask_bars."""
    sm = mask_bars[ds.sbar]
    idx = np.nonzero(sm)[0]
    day = ds.dayi[ds.sbar[idx]]; ses = ds.ses[ds.sbar[idx]].astype(np.int64); v = ds.sval[idx]
    o = np.lexsort((idx, -v, day))
    dd = day[o]; first = np.r_[0, np.nonzero(np.diff(dd))[0] + 1]
    rank = np.arange(len(o)) - np.repeat(first, np.diff(np.r_[first, len(o)]))
    top20 = idx[o[rank < 20]]
    g = day * 3 + ses
    o = np.lexsort((idx, -v, g))
    gg = g[o]; first = np.r_[0, np.nonzero(np.diff(gg))[0] + 1]
    rank = np.arange(len(o)) - np.repeat(first, np.diff(np.r_[first, len(o)]))
    top5 = idx[o[rank < 5]]
    return top20, top5


def near_dot(ds, res, idx, wbar):
    """Mẫu idx có chấm sau gộp cùng nến, cùng bên, cách <= w tick (kể cả chính nó)?"""
    di = np.nonzero(res.dot)[0]
    side = ds.sside if hasattr(ds, 'sside') else np.zeros(ds.ns, np.int64)
    key = lambda i: (ds.sbar[i].astype(np.int64) * 2 + side[i]) * (1 << 24) + ds.stk[i]
    dk = key(di)
    k = key(idx); w = wbar[ds.sbar[idx]]
    lo = np.searchsorted(dk, k - w, 'left'); hi = np.searchsorted(dk, k + w, 'right')
    return hi > lo


def oracle_row(ds, res, R, mask_bars, wbar, small=(3, 5)):
    """Một dòng PLAN 4.3 cho (cấu hình, đoạn). R = rulers(ds). wbar = cửa sổ gộp theo nến (w với chấm, g với Big Trade)."""
    ge_s, n_s, ge_a, n_a = R
    sm = mask_bars[ds.sbar]
    hs = sm & res.has[ds.sbar]
    p = res.exc[hs].sum() / max(hs.sum(), 1)
    out = dict(p_hat=p, so_gia_tri=int(sm.sum()))
    strict_s = ge_s <= np.floor(p / 2 * n_s); strict_a = ge_a <= np.floor(p / 2 * n_a)
    loose_s = ge_s <= np.floor(2 * p * n_s); loose_a = ge_a <= np.floor(2 * p * n_a)
    top20, top5 = top_sets(ds, mask_bars)
    groups = {'top20_ngay': top20, 'top5_phien': top5,
              'chat_ca_hai': np.nonzero(sm & strict_s & strict_a)[0],
              'chat_cung_gio': np.nonzero(sm & strict_s)[0], 'chat_quanh_no': np.nonzero(sm & strict_a)[0]}
    for g, idx in groups.items():
        out[f'{g}_so_o'] = len(idx)
        if len(idx) == 0:
            out[f'{g}_tho'] = np.nan; out[f'{g}_gop'] = np.nan; continue
        raw = res.exc[idx]
        nd = near_dot(ds, res, idx, wbar)
        out[f'{g}_tho'] = raw.mean(); out[f'{g}_gop'] = (raw | nd).mean()
    dots = res.dot & sm
    nd_ = dots.sum(); out['so_cham'] = int(nd_)
    if nd_:
        out['nhieu_ngoai_ca_hai'] = (dots & ~loose_s & ~loose_a).sum() / nd_
        out['nhieu_khong_ca_hai'] = (dots & ~(loose_s & loose_a)).sum() / nd_
        out['chi_cung_gio'] = (dots & loose_s & ~loose_a).sum() / nd_
        out['chi_quanh_no'] = (dots & ~loose_s & loose_a).sum() / nd_
        out[f'cham_le_{small[0]}'] = (dots & (ds.sval <= small[0])).sum() / nd_
        out[f'cham_le_{small[1]}'] = (dots & (ds.sval <= small[1])).sum() / nd_
    else:
        for c in ('nhieu_ngoai_ca_hai', 'nhieu_khong_ca_hai', 'chi_cung_gio', 'chi_quanh_no', f'cham_le_{small[0]}', f'cham_le_{small[1]}'):
            out[c] = np.nan
    f = lambda x: 'nan' if not np.isfinite(x) else f'{x:.3f}'
    out['v_top20'] = ('ĐẠT ' if out['top20_ngay_gop'] >= 0.99 else 'TRƯỢT ') + f(out['top20_ngay_gop'])
    out['v_top5'] = ('ĐẠT ' if out['top5_phien_gop'] >= 0.97 else 'TRƯỢT ') + f(out['top5_phien_gop'])
    x = out['chat_ca_hai_gop']
    out['v_cuc_tri'] = (('ĐẠT ' if x >= 0.97 else 'TRƯỢT ') + f(x)) if np.isfinite(x) else 'TRƯỢT nan (không có ô)'
    x = out['nhieu_ngoai_ca_hai']
    out['v_khong_nhieu'] = ('ĐẠT ' if np.isfinite(x) and x <= 0.05 else 'TRƯỢT ') + f(x)
    x = out[f'cham_le_{small[0]}']
    out['v_ti_hon'] = ('ĐẠT ' if np.isfinite(x) and x <= 0.02 else 'TRƯỢT ') + f(x)
    out['so_truot_43'] = sum(str(out[c]).startswith('TRƯỢT') for c in ('v_top20', 'v_top5', 'v_cuc_tri', 'v_khong_nhieu', 'v_ti_hon'))
    return out
