# -*- coding: utf-8 -*-
"""VÙNG cho setup C-v6 (plan `research/PLAN-C-v2.md` mục 2.1, 2.2, 2.3). KHÔNG sửa kernel.py / setup_c_fade_canh.py.

Ba phần:
  (a) Hình dạng profile TPO của phiên hôm qua (D / P / b / KHÁC-B / KHÁC-thin / KHÁC-close) + vùng dày T (mục 2.1).
  (b) Máy trạng thái VA nhỏ từ 3 lần đổi hành vi (CHoCH): climax → AR → ST (mục 2.2).
  (c) Lớp (layer) = bộ cột vùng (zcols) riêng để tái dùng nguyên `detect()` của setup C (mục 2.3).

Không nhìn trước: hình dạng phiên s chỉ dùng phiên q < s đã đóng (đúng phiên 'yday' kernel._zones chọn); máy CHoCH chỉ dùng
nến <= i và pivot zigzag từ `confirm_pos`; chế độ (mode) chỉ dùng nến M5 đã đóng (kernel.mode_frame).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import kernel as K
import zones_a_v4 as ZA

STEP = K.CONST['tick'] * K.CONST['row_ticks']          # 0,2 giá / hàng

# ------------------------------------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC (mục 2.1)
BRACKET = '30min'          # bracket TPO = 30 phút UTC
ASYM_THR = 0.25            # |asym| <= 0,25 ⇒ D (tham số tự do mới; độ nhạy 0,20 / 0,30)
BULGE_THR = 0.20           # bulge < 0,20 ⇒ KHÁC-thin (tham số tự do mới; độ nhạy 0,15 / 0,25)
BULGE_FRAC = 0.5           # vùng dày: hàng kề >= 50% TPO của POC (độ nhạy 0,4 / 0,6)

# ------------------------------------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC (mục 2.2)
ZZ = 2.0                   # zigzag kernel 2,0 giá, reset theo phiên (R5)
MOVE_U = 6.0               # move >= 6·u (tham số tự do mới)
MOVE_MIN_EFF = 0.35        # hiệu suất move (tái dùng wyckoff_schematic)
MOVE_LOOKBACK = 240        # chưa có pivot H trong phiên ⇒ chân = high lớn nhất 240 nến (trong phiên)
VSA_CLIMAX = 2.2           # volume >= 2,2·vma (tái dùng; độ nhạy 1,8)
CLIMAX_RANGE_MULT = 1.4    # HOẶC biên độ >= 1,4·TB biên độ 20 nến trước (tái dùng)
RANGE_AVG_N = 20
VMA_N = 20                 # SMA volume 20 nến GỒM nến i
CLIMAX_EXT_BARS = 8        # cụm cao trào: 8 nến sau mốc (tái dùng)
BLOCK_FRAC = 0.4           # bị chặn: close >= low + 0,4·range (tham số tự do mới; độ nhạy: bỏ điều kiện)
AR_MIN = 2.0               # H1 − L1 >= max(2,0 ; 0,5·max_pullback)
AR_RETRACE_MULT = 0.5      # (tái dùng)
UNDERCUT_U = 1.0           # ST được thủng L1 tối đa 1,0·u (tham số tự do mới)
STA_MIN_AR_FRAC = 0.55     # ST phải về >= 55% đường AR→climax (tái dùng)
AR_WAIT_BARS = 300         # chờ AR tối đa 300 nến từ climax
ST_WAIT_BARS = 400         # chờ ST tối đa 400 nến từ H1
MIN_HEIGHT = 6.0           # VA_C sống khi cao >= 6 giá (độ nhạy 4)
EXT_FRAC = 0.25            # nới cạnh khi pivot vượt 0 < d <= 0,25·height; vượt hơn ⇒ CHẾT (tham số tự do mới; độ nhạy 0,15 / không nới)
NO_TOUCH = None            # bản chính: không hạn tuổi; độ nhạy 240 nến không chạm cạnh ⇒ CHẾT

CHOCH_DEFAULT = dict(vsa=VSA_CLIMAX, block=True, ext_frac=EXT_FRAC, extend=True, min_h=MIN_HEIGHT, no_touch=NO_TOUCH)

LABELS = ('D', 'P', 'b', 'KHÁC-B', 'KHÁC-thin', 'KHÁC-close')


# =============================================================================================
# (a) HÌNH DẠNG PROFILE TPO
# =============================================================================================
def tpo_profile(df, sno, us_only=False):
    """Profile TPO của phiên sno từ nến M1: bracket 30' UTC, mỗi bracket phủ các hàng 0,2 giá từ rint(low/0,2) tới rint(high/0,2)
    (= ProfileEngine.TpoRows trên nến M30). us_only: chỉ nến pha Mỹ (độ nhạy R1).
    Trả (rows_int, tpo_count, L, H, close) — chỉ các hàng có TPO > 0 — hoặc None."""
    m = df['session_no'].to_numpy() == sno
    if us_only:
        m &= df['phase'].to_numpy() == 'US'
    if not m.any():
        return None
    seg = df.loc[m, ['t_utc', 'high', 'low', 'close']]
    br = seg['t_utc'].dt.floor(BRACKET).to_numpy()
    g = seg.groupby(br, sort=True)
    bh = np.rint(g['high'].max().to_numpy(float) / STEP).astype(np.int64)
    bl = np.rint(g['low'].min().to_numpy(float) / STEP).astype(np.int64)
    r0, r1 = int(bl.min()), int(bh.max())
    cnt = np.zeros(r1 - r0 + 1, np.int64)
    for a, b in zip(bl, bh):
        cnt[a - r0:b - r0 + 1] += 1
    rows = np.arange(r0, r1 + 1)
    keep = cnt > 0
    return rows[keep], cnt[keep], float(seg['low'].min()), float(seg['high'].max()), float(seg['close'].iloc[-1])


def classify_shape(rows, cnt, L, H, close, asym_thr=ASYM_THR, bulge_thr=BULGE_THR, frac=BULGE_FRAC):
    """Phân loại (mục 2.1), xét theo thứ tự: KHÁC-B (hai đỉnh có LVN ở giữa) → KHÁC-thin (bulge < bulge_thr) → KHÁC-close (close ngoài
    VA) → D (|asym| <= asym_thr) → P (asym > asym_thr) → b. Trả dict(label, poc, vah, val, t_lo, t_hi, asym, bulge, L, H, close,
    close_in, two_peaks)."""
    rows = np.asarray(rows)
    cnt = np.asarray(cnt, float)
    prices = K.Profiles.row_price(rows)
    poc, vah, val = K.value_area(prices, cnt)
    t_lo, t_hi = ZA.peak_sharpness(rows, cnt, poc, frac=frac)
    R = H - L
    hv = K.find_hvn(prices, cnt)
    lv = K.find_lvn(prices, cnt)
    two = False
    for a in range(len(hv)):
        for b in range(a + 1, len(hv)):
            lo_, hi_ = sorted((hv[a][0], hv[b][0]))
            if any(lo_ < p < hi_ for p, _ in lv):
                two = True
    close_in = bool(val - 1e-9 <= close <= vah + 1e-9)
    if R <= 0:
        bulge, asym = 0.0, 0.0
    else:
        bulge = (t_hi - t_lo) / R
        asym = ((t_lo - L) - (H - t_hi)) / R
    if two:
        lab = 'KHÁC-B'
    elif bulge < bulge_thr:
        lab = 'KHÁC-thin'
    elif not close_in:
        lab = 'KHÁC-close'
    elif abs(asym) <= asym_thr:
        lab = 'D'
    elif asym > 0:
        lab = 'P'
    else:
        lab = 'b'
    return dict(label=lab, poc=float(poc), vah=float(vah), val=float(val), t_lo=float(t_lo), t_hi=float(t_hi), asym=float(asym),
                bulge=float(bulge), L=float(L), H=float(H), close=float(close), close_in=close_in, two_peaks=two)


def yday_of(ctx):
    """{session_no: session_no của phiên hôm qua} — ĐÚNG phiên kernel._zones chọn ('yday'), None nếu không có."""
    out = {}
    for s in ctx.st.index:
        z = K._zones(ctx, int(s), None, naked=False)
        out[int(s)] = int(z['yday']['session_no']) if z['yday'] else None
    return out


def shape_by_session(df, ctx, source='tpo', asym_thr=ASYM_THR, bulge_thr=BULGE_THR, frac=BULGE_FRAC, yd=None):
    """{sno: dict hình dạng của phiên q = yday(sno)} (+ khoá 'q'). source: 'tpo' (bản chính) | 'vol' (độ nhạy S1: profile volume
    per-level của kernel, cùng công thức) | 'tpo_us' (độ nhạy R1: chỉ cửa sổ Mỹ 19:00–04:00 của phiên q)."""
    yd = yd if yd is not None else yday_of(ctx)
    cache, out = {}, {}
    for s, q in yd.items():
        if q is None:
            out[s] = None
            continue
        if q not in cache:
            if source == 'vol':
                r, v = ctx.prof.full[q]
                m = df['session_no'].to_numpy() == q
                seg = df.loc[m]
                prof = (r, v, float(seg['low'].min()), float(seg['high'].max()), float(seg['close'].iloc[-1]))
            else:
                prof = tpo_profile(df, q, us_only=(source == 'tpo_us'))
            cache[q] = None if prof is None else classify_shape(*prof, asym_thr=asym_thr, bulge_thr=bulge_thr, frac=frac)
        d = cache[q]
        out[s] = None if d is None else dict(d, q=q)
    return out


# =============================================================================================
# (b) MÁY TRẠNG THÁI VA NHỎ CHoCH
# =============================================================================================
def vma_series(df, n=VMA_N):
    """SMA volume n nến GỒM nến i (đủ n nến mới có giá trị)."""
    return df['volume'].rolling(n, min_periods=n).mean()


def avg_range_before(df, n=RANGE_AVG_N):
    """TB biên độ n nến TRƯỚC nến i (không gồm i)."""
    return (df['high'] - df['low']).shift(1).rolling(n, min_periods=n).mean()


class _VA:
    __slots__ = ('id', 'dir', 'sno', 'climax', 'anchor', 'vsa', 'dclimax', 'L1', 'H1', 'L2', 'birth', 'lo', 'hi', 'segs', 'n_ext',
                 'end', 'why', 'last_touch', 'touches', 'inside_prev')

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))


def _one_dir(X, piv_at, sess_first, p, u, vma, avgr, vol, dl, d, log_cand, funnel, vas, next_id):
    """Chạy máy cho MỘT chiều trên khung giá đã đổi dấu (d=+1: chiều 'DN' climax bán ở đáy, giá thật; d=−1: chiều 'UP', giá âm).
    X = (xl, xh, xc, rng) trong khung đó. piv_at: confirm_pos → (pos, price, kind) trong khung đó. Ghi VA vào vas (list _VA, giá
    trong KHUNG — đổi về giá thật ở ngoài)."""
    xl, xh, xc, rng = X
    n = len(xl)
    tag = 'DN' if d > 0 else 'UP'
    st = 'NGU'
    cd = None                    # ứng viên / máy đang xây
    live = None                  # VA_C đang sống của chiều này
    last_H = None                # pivot H (trong khung) gần nhất đã xác nhận trong phiên
    s0 = 0

    def climax_ok(c):
        """Điều kiện bước 1 + 2 tại nến c (chỉ dữ liệu <= c). Trả (ok, mp) ."""
        vm = vma[c]
        ar = avgr[c]
        cond = (vm == vm and vol[c] >= p['vsa'] * vm) or (ar == ar and rng[c] >= CLIMAX_RANGE_MULT * ar)
        if not cond:
            return False, 0.0
        if last_H is not None and last_H[0] < c:
            ch = last_H[0]
            top = last_H[1]
        else:
            a = max(s0, c - MOVE_LOOKBACK)
            if c - a < 1:
                return False, 0.0
            ch = a + int(np.argmax(xh[a:c]))
            top = xh[ch]
        if xl[c] > xl[ch:c].min() + 1e-12:
            return False, 0.0
        length = top - xl[c]
        uc = u[c]
        if not (uc == uc) or length < MOVE_U * uc:
            return False, 0.0
        path = np.abs(np.diff(xc[ch:c + 1])).sum()
        eff = length / path if path > 1e-9 else 0.0
        if eff < MOVE_MIN_EFF:
            return False, 0.0
        run_min = np.minimum.accumulate(xl[ch:c])
        mp = float((xh[ch:c] - run_min).max()) if c > ch else 0.0
        return True, mp

    def blocked_now(c):
        return xc[c] >= xl[c] + BLOCK_FRAC * rng[c] - 1e-12

    def kill_live(i, why):
        nonlocal live
        if live is not None:
            live.end, live.why = i, why
            live = None

    for i in range(n):
        if sess_first[i]:
            kill_live(i, 'het_phien')
            st, cd, last_H, s0 = 'NGU', None, None, i
        pv = piv_at.get(i)
        if pv is not None and pv[2] == 'H':
            last_H = (pv[0], pv[1])
        ui = u[i]
        # ---------------- VA đang sống: nới / chết theo pivot, theo không chạm
        if live is not None:
            if pv is not None:
                h = live.hi - live.lo
                if pv[2] == 'L' and pv[1] < live.lo - 1e-9:
                    dd = live.lo - pv[1]
                    if dd > p['ext_frac'] * h + 1e-9:
                        kill_live(i, 'pha_bien')
                    elif p['extend']:
                        live.lo = pv[1]
                        live.n_ext += 1
                        live.segs.append((i, live.lo, live.hi))
                elif pv[2] == 'H' and pv[1] > live.hi + 1e-9:
                    dd = pv[1] - live.hi
                    if dd > p['ext_frac'] * h + 1e-9:
                        kill_live(i, 'pha_bien')
                    elif p['extend']:
                        live.hi = pv[1]
                        live.n_ext += 1
                        live.segs.append((i, live.lo, live.hi))
            if live is not None:
                touch = (xh[i] >= live.hi - 1e-9) or (xl[i] <= live.lo + 1e-9)
                if touch:
                    live.touches += 1 if live.inside_prev else 0          # đếm LẦN chạm (từ trong ra chạm cạnh)
                    live.last_touch = i
                live.inside_prev = not touch
                if p['no_touch'] and i - live.last_touch > p['no_touch']:
                    kill_live(i, 'khong_cham')
        # ---------------- máy xây: mở ứng viên TRƯỚC rồi mới xét pivot cùng nến (pivot L có thể xác nhận ngay trong nến climax);
        # ứng viên cũ hỏng ở nến này ⇒ thử mở ứng viên mới ngay tại nến này (một lần).
        for attempt in (0, 1):
            fresh = False
            if st == 'NGU':
                ok, mp = climax_ok(i)
                if not ok:
                    break
                vm = vma[i]
                cd = dict(anchor=i, c=i, low=xl[i], cmin=xl[i], mp=mp, blk=(True if (not p['block'] or blocked_now(i)) else None),
                          vsa=float(vol[i] / vm) if vm == vm and vm > 0 else float('nan'), dcl=float(dl[i]))
                st, fresh = 'CAND', True
                funnel['climax'] += 1
                log_cand.append((tag, i))
            fail = False
            if st == 'CAND':
                if i <= cd['anchor'] + CLIMAX_EXT_BARS:
                    if xl[i] < cd['low'] - 1e-12:
                        ok, mp = climax_ok(i)
                        if ok:
                            vm = vma[i]
                            cd.update(c=i, low=xl[i], mp=mp, blk=(True if (not p['block'] or blocked_now(i)) else None),
                                      vsa=float(vol[i] / vm) if vm == vm and vm > 0 else float('nan'), dcl=float(dl[i]))
                    cd['cmin'] = min(cd['cmin'], xl[i])
                elif xl[i] < cd['cmin'] - 1e-12:
                    fail = True
                if not fail and cd['blk'] is None and i == cd['c'] + 1:
                    cd['blk'] = bool(xc[i] > (xh[cd['c']] + xl[cd['c']]) / 2.0 + 1e-12)
                    if not cd['blk']:
                        fail = True
                if not fail and pv is not None and pv[2] == 'L':
                    # L1 = pivot L zigzag nằm trong cửa sổ cụm ⇒ đổi hành vi #1 đã xác nhận (giá đã lên >= 2 từ đáy). Giá L1 = ĐÁY CỤM thật:
                    # zigzag kernel có thể bỏ đáy của nến vừa tạo đỉnh (nến biên độ >= 2 giá) nên giá pivot có thể cao hơn đáy cụm (Q5).
                    if pv[0] <= cd['anchor'] + CLIMAX_EXT_BARS and cd['blk'] is not False:
                        cd.update(L1=min(pv[1], cd['cmin']), tL1=i)
                        st = 'WAIT_AR'
                        funnel['L1'] += 1
                    else:
                        fail = True
            elif st == 'WAIT_AR':
                if cd['blk'] is None and i == cd['c'] + 1:
                    cd['blk'] = bool(xc[i] > (xh[cd['c']] + xl[cd['c']]) / 2.0 + 1e-12)
                    if not cd['blk']:
                        fail = True
                if not fail and ((ui == ui and xl[i] < cd['L1'] - UNDERCUT_U * ui - 1e-12) or i - cd['c'] > AR_WAIT_BARS):
                    fail = True
                if not fail and pv is not None and pv[2] == 'H':
                    if pv[1] - cd['L1'] >= max(AR_MIN, AR_RETRACE_MULT * cd['mp']) - 1e-9:
                        cd.update(H1=pv[1], tH1=i)
                        st = 'WAIT_ST'
                        funnel['AR'] += 1
                    else:
                        funnel['AR_nho'] += 1
            elif st == 'WAIT_ST':
                if (ui == ui and xl[i] < cd['L1'] - UNDERCUT_U * ui - 1e-12):
                    fail = True
                    funnel['ST_thung'] += 1
                elif i - cd['tH1'] > ST_WAIT_BARS:
                    fail = True
                elif pv is not None and pv[2] == 'H' and pv[1] > cd['H1'] + 1e-9:
                    cd.update(H1=pv[1], tH1=i)                                   # AR mở rộng (chỗ tự quyết Q4)
                elif pv is not None and pv[2] == 'L':
                    span = cd['H1'] - cd['L1']
                    if pv[1] <= cd['H1'] - STA_MIN_AR_FRAC * span + 1e-9:
                        lo, hi = min(cd['L1'], pv[1]), cd['H1']
                        funnel['ST'] += 1
                        if hi - lo >= p['min_h'] - 1e-9:
                            kill_live(i, 'thay_the')
                            live = _VA(id=next_id[0], dir=tag, sno=None, climax=cd['c'], anchor=cd['anchor'], vsa=cd['vsa'],
                                       dclimax=cd['dcl'], L1=cd['L1'], H1=cd['H1'], L2=pv[1], birth=i, lo=lo, hi=hi,
                                       segs=[(i, lo, hi)], n_ext=0, end=n, why='het_du_lieu', last_touch=i, touches=0, inside_prev=True)
                            next_id[0] += 1
                            vas.append(live)
                            funnel['sinh'] += 1
                        else:
                            funnel['hep'] += 1
                        st, cd = 'NGU', None
            if fail:
                st, cd = 'NGU', None
                if attempt == 0 and not fresh:
                    continue
            break
    if live is not None:
        live.end, live.why = n, 'het_du_lieu'


def choch_machine(df, u, vma, params=None, avgr=None, pivots=None):
    """Máy trạng thái mục 2.2 cho cả hai chiều (DN = climax bán ở đáy; UP = gương). Chưa áp chế độ TREND (xem choch_va).
    Trả (vas, cands, funnel): vas = list _VA (giá THẬT; segs = [(pos_từ, lo, hi)]; end = vị trí nến đầu tiên VA không còn sống
    theo máy giá — trước khi xét TREND); cands = [(chiều, nến mốc climax)]; funnel = đếm từng bước."""
    p = dict(CHOCH_DEFAULT, **(params or {}))
    hi, lo, cl = (df[c].to_numpy(float) for c in ('high', 'low', 'close'))
    rng = hi - lo
    vol, dl = df['volume'].to_numpy(float), df['delta'].to_numpy(float)
    sno = df['session_no'].to_numpy()
    n = len(df)
    sess_first = np.r_[True, sno[1:] != sno[:-1]] if n else np.zeros(0, bool)
    u = np.asarray(u, float)
    vma = np.asarray(vma, float)
    avgr = np.asarray(avg_range_before(df) if avgr is None else avgr, float)
    piv = K.zigzag(df, ZZ, by_session=True) if pivots is None else pivots
    pa_dn = {x['confirm_pos']: (x['pos'], x['price'], x['kind']) for x in piv}
    pa_up = {x['confirm_pos']: (x['pos'], -x['price'], 'L' if x['kind'] == 'H' else 'H') for x in piv}
    vas, cands = [], []
    funnel = {}
    nid = [0]
    for d, X, pa in ((1, (lo, hi, cl, rng), pa_dn), (-1, (-hi, -lo, -cl, rng), pa_up)):
        f = dict(climax=0, L1=0, AR=0, AR_nho=0, ST=0, ST_thung=0, sinh=0, hep=0)
        tmp = []
        _one_dir(X, pa, sess_first, p, u, vma, avgr, vol, dl, d, cands, f, tmp, nid)
        for v in tmp:
            v.sno = int(sno[v.birth])
            if d < 0:                                                     # đổi về giá thật
                v.lo, v.hi = -v.hi, -v.lo
                v.L1, v.H1, v.L2 = -v.L1, -v.H1, -v.L2
                v.segs = [(a, -h, -l) for a, l, h in v.segs]
        vas += tmp
        funnel['DN' if d > 0 else 'UP'] = f
    vas.sort(key=lambda v: (v.birth, v.id))
    return vas, cands, funnel


def paint(n, vas, kills=None, shift=None, sno=None):
    """Mảng theo nến (lo, hi, src, id, n_ext, birth) của VA_C ĐANG HIỆN: VA sống tại nến i; hai VA cùng sống ⇒ cái sinh SAU.
    kills: {id: vị trí chết do TREND}; shift: mảng δ theo session_no (đối chứng dời) — cộng vào cả hai cạnh."""
    kills = kills or {}
    lo, hi = np.full(n, np.nan), np.full(n, np.nan)
    src = np.full(n, '', dtype=object)
    vid = np.full(n, -1, np.int64)
    nex = np.zeros(n, np.int64)
    for v in sorted(vas, key=lambda v: (v.birth, v.id)):
        end = min(v.end, kills.get(v.id, n))
        dlt = 0.0 if shift is None else float(shift[v.sno])
        for k, (a, l, h) in enumerate(v.segs):
            b = v.segs[k + 1][0] if k + 1 < len(v.segs) else end
            b = min(b, end)
            if b <= a:
                continue
            lo[a:b], hi[a:b] = l + dlt, h + dlt
            src[a:b] = 'CHOCH_' + v.dir
            vid[a:b] = v.id
            nex[a:b] = k
    return lo, hi, src, vid, nex


def band_zcols(template, lo, hi, poc=None):
    """zcols cho mode_frame/detect: eu_vah/eu_val = band, eu_poc = poc (NaN mặc định), ib = NaN (band_src 'va_eu' khi có band)."""
    z = template.copy()
    z['eu_vah'], z['eu_val'] = hi, lo
    z['eu_poc'] = np.full(len(z), np.nan) if poc is None else poc
    z['ib_hi'] = np.nan
    z['ib_lo'] = np.nan
    return z


def mode_kills(df, template, vas, shift=None, max_iter=200):
    """Bước 8: chạy kernel.mode_frame trên band VA_C đang hiện; VA đang hiện mà chế độ (từ M5 đã đóng, cùng VA) là TREND_* ⇒ CHẾT
    từ nến đó. Lặp: mỗi vòng chỉ áp lần chết SỚM NHẤT của mỗi phiên (đúng thứ tự thời gian ⇒ nhân quả). Trả (kills, paint, zc, mf)."""
    n = len(df)
    kills = {}
    t1 = df['t_utc'].to_numpy()
    s1 = df['session_no'].to_numpy()
    for _ in range(max_iter):
        lo, hi, src, vid, nex = paint(n, vas, kills, shift)
        zc = band_zcols(template, lo, hi)
        m5 = K.m5_bars(df, zc)
        mf = K.mode_frame(df, zc, m5)
        te = m5['t5_end'].to_numpy()
        j = np.searchsorted(te, t1, side='right') - 1
        ok = (j >= 0) & (m5['session_no'].to_numpy()[np.maximum(j, 0)] == s1)
        lp = m5['last_pos'].to_numpy()[np.maximum(j, 0)]
        vm = np.where(ok, vid[lp], -1)
        tr = mf['mode'].astype(str).str.startswith('TREND').to_numpy() & ok & (vid >= 0) & (vm == vid)
        cand = np.flatnonzero(tr)
        new = {}
        seen_s = set()
        for i in cand:
            s = int(s1[i])
            if s in seen_s:
                continue
            seen_s.add(s)
            v = int(vid[i])
            if v not in kills:
                new[v] = int(i)
        if not new:
            return kills, (lo, hi, src, vid, nex), zc, mf
        kills.update(new)
    raise RuntimeError('mode_kills không hội tụ')


def choch_va(df, u, vma, params=None, template=None, pivots=None, avgr=None, shift=None, vas=None):
    """Mục 2.2 đầy đủ: máy giá (choch_machine) + chết theo TREND (mode_kills). template = zcols nền (cột ZONE_COLS) cho band_zcols.
    Trả dict(frame=DataFrame[choch_lo, choch_hi, choch_src, choch_id, n_ext], log=list dict, mf=mode_frame, zc=zcols, vas, funnel, cands)."""
    if vas is None:
        vas, cands, funnel = choch_machine(df, u, vma, params, avgr=avgr, pivots=pivots)
    else:
        cands, funnel = [], {}
    if template is None:
        template = pd.DataFrame({c: np.full(len(df), np.nan) for c in K.ZONE_COLS}, index=df.index)
    kills, (lo, hi, src, vid, nex), zc, mf = mode_kills(df, template, vas, shift=shift)
    fr = pd.DataFrame({'choch_lo': lo, 'choch_hi': hi, 'choch_src': src, 'choch_id': vid, 'n_ext': nex}, index=df.index)
    sid = df['session_id'].to_numpy()
    tv = df['t_vn'].to_numpy()
    ph = df['phase'].to_numpy()
    log = []
    for v in vas:
        k = kills.get(v.id)
        end, why = (k, 'trend') if (k is not None and k < v.end) else (v.end, v.why)
        log.append(dict(id=v.id, dir=v.dir, session=sid[v.birth], climax=int(v.climax), t_climax=str(tv[v.climax])[:16], vsa=v.vsa,
                        delta_climax=v.dclimax, L1=v.L1, H1=v.H1, L2=v.L2, birth=int(v.birth), t_birth=str(tv[v.birth])[:16],
                        phase=ph[v.birth], lo0=v.segs[0][1], hi0=v.segs[0][2], height0=v.segs[0][2] - v.segs[0][1],
                        lo=v.segs[-1][1], hi=v.segs[-1][2], n_ext=v.n_ext, end=int(end), why=why, life=int(end - v.birth),
                        touches=v.touches))
    return dict(frame=fr, log=log, mf=mf, zc=zc, vas=vas, funnel=funnel, cands=cands, kills=kills)


# =============================================================================================
# (c) LỚP (LAYER)
# =============================================================================================
def _pre_mask(df):
    return df['sm'].to_numpy() < K.CONST['sm_us_start']          # A + EU (trước 19:00 neo Mỹ) — đúng mask của prepare()


def label_by_bar(df, shapes):
    """Nhãn hình dạng của ngày (phiên) theo nến ('' nếu không có)."""
    sno = df['session_no'].to_numpy()
    lab = {s: (d['label'] if d else '') for s, d in shapes.items()}
    return np.array([lab.get(int(s), '') for s in sno], dtype=object)


def layer_zcols(df, zc2, kind, shapes=None, choch=None, d_band='vol'):
    """Bộ cột vùng cho một lớp (mục 2.3). zc2 = zcols của C0 (prepare(): A/EU = VA hôm qua, US = VA Âu/IB).
    kind: 'L0' (C0) | 'L1' (VA_Y chỉ ngày D) | 'L2' (D: VA_Y, P/b: T) | 'L3' (VA_C).
    d_band: 'vol' = ngày D dùng VA volume hôm qua (= C0) | 'tpo' = VAH_T/VAL_T/POC_T (độ nhạy).
    Trả (zc, names) — names = (mảng tên cạnh trên, mảng tên cạnh dưới) theo nến ('' = tên mặc định của detect C)."""
    n = len(df)
    hn = np.full(n, '', dtype=object)
    ln = np.full(n, '', dtype=object)
    if kind == 'L0':
        return zc2.copy(), None
    if kind in ('L1', 'L2'):
        z = zc2.copy()
        pre = _pre_mask(df)
        sno = df['session_no'].to_numpy()
        eh, el, ep = (z[c].to_numpy(float).copy() for c in ('eu_vah', 'eu_val', 'eu_poc'))
        for s, d in shapes.items():
            m = pre & (sno == s)
            if not m.any():
                continue
            lab = d['label'] if d else ''
            if lab == 'D':
                if d_band == 'tpo':
                    eh[m], el[m], ep[m] = d['vah'], d['val'], d['poc']
                hn[m], ln[m] = 'VAH_Y_D', 'VAL_Y_D'
            elif kind == 'L2' and lab in ('P', 'b'):
                eh[m], el[m], ep[m] = d['t_hi'], d['t_lo'], d['poc']
                sfx = 'P' if lab == 'P' else 'B'
                hn[m], ln[m] = 'T_HI_' + sfx, 'T_LO_' + sfx
            else:
                eh[m], el[m], ep[m] = np.nan, np.nan, np.nan
        z['eu_vah'], z['eu_val'], z['eu_poc'] = eh, el, ep
        return z, (hn, ln)
    if kind == 'L3':
        fr = choch['frame']
        z = choch['zc'].copy()
        src = fr['choch_src'].to_numpy()
        has = src != ''
        hn[has] = np.char.add(src[has].astype(str), '_HI')
        ln[has] = np.char.add(src[has].astype(str), '_LO')
        return z, (hn, ln)
    raise ValueError(kind)


def zone_table(zc, names):
    """Bảng (DataFrame) cho test cắt dữ liệu: cạnh/POC của lớp + tên."""
    d = {'eu_vah': zc['eu_vah'].to_numpy(float), 'eu_val': zc['eu_val'].to_numpy(float), 'eu_poc': zc['eu_poc'].to_numpy(float)}
    out = pd.DataFrame(d)
    if names is not None:
        out['hn'], out['ln'] = names[0], names[1]
    return out


def ctrl_columns(zc, names):
    """Cột riêng cho từng tên vùng mới (giá cạnh khi tên đó đang áp dụng, NaN nơi khác) — cho kernel.control_sample (ĐC-b).
    Trả (DataFrame cột 'z_<tên>', {tên: 'z_<tên>'})."""
    if names is None:
        return pd.DataFrame(index=zc.index), {}
    hn, ln = names
    eh, el = zc['eu_vah'].to_numpy(float), zc['eu_val'].to_numpy(float)
    cols, mp = {}, {}
    for arr, val in ((hn, eh), (ln, el)):
        for nm in sorted(set(arr.tolist()) - {''}):
            c = 'z_' + nm
            v = np.where(arr == nm, val, np.nan)
            cols[c] = v if c not in cols else np.where(np.isnan(cols[c]), v, cols[c])
            mp[nm] = c
    return pd.DataFrame(cols, index=zc.index), mp


def shift_matrix(nS, reps, lo, hi, seed):
    """Ma trận δ (nS, reps) — Y HỆT zones_b_v2.shift_matrix / benzo_vcl (cùng hạt ⇒ cùng δ)."""
    rng = np.random.default_rng(seed)
    return rng.uniform(lo, hi, (nS, reps)) * rng.choice([-1.0, 1.0], (nS, reps))


def time_shifted_vas(df, vas, rng):
    """'VA giả' (ĐC-c): mỗi VA_C giữ chiều cao, quỹ đạo cạnh (nới), tuổi thọ theo máy giá, cùng phiên; thời điểm sinh dời ngẫu nhiên
    đều trong phiên; giá dời sao cho close tại nến sinh giả nằm ĐÚNG vị trí tương đối như close tại nến sinh thật. Trả list _VA."""
    st = K.session_table(df)
    cl = df['close'].to_numpy(float)
    out = []
    for v in vas:
        a, b = int(st['start_pos'].loc[v.sno]), int(st['end_pos'].loc[v.sno]) + 1
        nb = int(rng.integers(a, b))
        life = v.end - v.birth
        dt = nb - v.birth
        off = cl[nb] - cl[v.birth]
        segs = [(max(a, s + dt), l + off, h + off) for s, l, h in v.segs if s + dt < b]
        if not segs:
            continue
        out.append(_VA(id=v.id, dir=v.dir, sno=v.sno, climax=v.climax, anchor=v.anchor, vsa=v.vsa, dclimax=v.dclimax, L1=v.L1, H1=v.H1,
                       L2=v.L2, birth=nb, lo=segs[0][1], hi=segs[0][2], segs=segs, n_ext=v.n_ext, end=min(nb + life, b), why='gia',
                       last_touch=nb, touches=0, inside_prev=True))
    return out
