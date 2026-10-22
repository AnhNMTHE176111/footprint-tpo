# -*- coding: utf-8 -*-
"""
HỢP LƯU VCL × SESSIONZONES (người học hỏi 2026-10-22): vùng Vùng Canh Lệnh (v5, rộng 2–5 giá, đang hiển thị) mà TRÙNG một mức
của SessionZones thì giá có ĐẢO CHIỀU nhiều hơn / XUYÊN PHÁ ít hơn / cho "thắng 1:1" nhiều hơn vùng không trùng không?

Tái dùng: vcl5 (bộ vùng, cache report/cache_lc/v5.pkl), lan_cham (máy đếm lần chạm τ=0, E=2 giá, G=5 nến; tỉ lệ, verdict),
kernel (VWAP, VA Âu, HVN/LVN — KHÔNG nhìn trước). Không sửa file nào khác.

Mức SessionZones (= cái SessionZones.cs VẼ MẶC ĐỊNH, ZonePolicy) ↔ bản Python:
  VWAP_D  VWAP ngày (reset mỗi phiên CME)        kernel.vwap_series['vwap_d'] tại nến i (gồm nến i đã đóng)
  VWAP_W  VWAP tuần (neo sau khoảng nghỉ > 30 h)  kernel.vwap_series['vwap_w']
  VA_EU   VAH + VAL phiên Âu đã CHỐT gần nhất    kernel._zones(...)['va_eu'] (chốt 19:00 VN = ready_pos), MANG SANG tới khi
                                                 phiên Âu kế tiếp chốt (C#: VaEdgeSessionIndex = block "AU" đã đóng gần nhất)
  HVN_D   HVN ngày (≤ 3, cổng tỉ lệ ≥ 2,5)       kernel._zones['hvn_day'] (profile PHIÊN TRƯỚC) + dải PeakSharpness 90% (port C#)
  HVN_W   HVN tuần (3 tuần CME đã đóng, ≤ 3)     kernel._zones['hvn_week'] + dải PeakSharpness 90% trên profile gộp
  LVN_D   LVN ngày (≤ 2)                         kernel._zones['lvn_day'] (điểm)
  Mức tĩnh chỉ tính khi tâm cách giá đóng ≤ 12 giá (ZoneRadiusPrices — SessionZones chỉ vẽ trong bán kính này); VWAP luôn vẽ.
  KHÔNG mô phỏng: trần 5 vùng (LimitAndBalance), gộp vùng (MergeZones), mục tiêu xa (IsTarget).
  KHÁC C#: HVN/LVN ngày của C# = profile 24 giờ cuối (cập nhật khi mỗi block Á/Âu/Mỹ đóng); kernel = profile phiên CME trước.

Chạy: python3 hop_luu_sz.py  → report/HOP-LUU-SZ.md + report/img/hop_luu_sz_<split>_<phiên>.png
"""
import os, sys, time, math, pickle
import numpy as np
import pandas as pd
import vcl as V
import vcl2 as V2
import vcl5 as V5
import lan_cham as LC

K = V.K
REPORT = V.REPORT
IMG = os.path.join(REPORT, 'img')

# ------------------------------- HẰNG SỐ ĐĂNG KÝ TRƯỚC (không đổi sau khi nhìn kết quả) -------------------------------
TOL = 0.5                      # dung sai hợp lưu (giá) — chốt
TOLS = (0.0, 0.5, 1.5)         # độ nhạy, chỉ báo
RADIUS = 12.0                  # SessionZones.ZoneRadiusPrices
SHIFT_LO, SHIFT_HI = 3.0, 15.0 # Đ1: |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, cố định trong (phiên, bản)
REPS, SEED = 100, 20261023
WIN_R, WIN_N = 4.0, 30         # "thắng 1:1": đi đúng hướng ≥ 4 giá trước khi ngược ≥ 4 giá, trong 30 nến
LV_HALF = 1.0                  # mục 5a: mức SessionZones một mình = vùng giả rộng 2 giá (tâm ± 1)
D_EDGES = (3.0, 6.0, 12.0)     # Đ2: bin khoảng cách giá đóng → cạnh gần lúc vùng hiện: ≤3 / 3–6 / 6–12 / >12
GRPS = ['VWAP_D', 'VWAP_W', 'VA_EU', 'HVN_D', 'HVN_W', 'LVN_D']
STATIC = ['VA_EU', 'HVN_D', 'HVN_W', 'LVN_D']
GTEN = {'VWAP_D': 'VWAP ngày', 'VWAP_W': 'VWAP tuần', 'VA_EU': 'VAH/VAL Âu', 'HVN_D': 'HVN ngày', 'HVN_W': 'HVN tuần',
        'LVN_D': 'LVN ngày', 'ANY': 'BẤT KỲ (gộp)'}
ALLG = GRPS + ['ANY']
WIN, LOSS, TIMEOUT, NOSIDE = 1, 0, -1, -2
ROW = K.CONST['tick'] * K.CONST['row_ticks']   # 0,2 giá


# =====================================================================================================================
# 1. MỨC SESSIONZONES (không nhìn trước)
# =====================================================================================================================
def peak_band(rows_int, vol, p, frac=0.90):
    """Port ProfileEngine.PeakSharpness: từ hàng đỉnh nới LIÊN TỤC 2 phía (hàng phải có mặt) khi volume ≥ frac × volume hàng đỉnh.
    rows_int: chỉ số hàng (× 0,2 = giá); vol: volume thô (KHÔNG làm mượt). Đỉnh không có trong hàng ⇒ (p, p)."""
    d = dict(zip(np.asarray(rows_int).tolist(), np.asarray(vol, float).tolist()))
    rp = int(round(p / ROW))
    if rp not in d:
        return p, p
    thr = frac * d[rp]
    lo = hi = rp
    while lo - 1 in d and d[lo - 1] >= thr:
        lo -= 1
    while hi + 1 in d and d[hi + 1] >= thr:
        hi += 1
    return round(lo * ROW, 6), round(hi * ROW, 6)


def week_rows(kc, sno, sp=-1):
    """Profile gộp đúng như kernel._Ctx.week_hvn (3 tuần CME đã đóng, phiên ≥ 300 nến) — để lấy dải PeakSharpness."""
    st = kc.st
    W = int(st['week_no'].loc[sno])
    wk = st['week_no'].to_numpy()
    m = (wk >= W - K.CONST['week_lookback']) & (wk <= W - 1) & (st.index.to_numpy() >= max(sp, 0)) & \
        (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
    snos = [int(x) for x in st.index[m] if int(x) in kc.prof.full]
    return K._agg_profiles([kc.prof.full[x] for x in snos])


def sz_levels(ctx):
    """Trả (lev, vw): lev = DataFrame mức tĩnh [grp, start, end, lo, hi, c, src] — mức dùng được ở nến start..end (đã chốt);
    vw = dict(VWAP_D, VWAP_W) mảng theo nến (cộng dồn tới nến i, gồm nến i)."""
    df, st, prof = ctx['df'], ctx['st'], ctx['prof']
    n = len(df)
    kc = K._Ctx(df, prof)
    rows, va = [], []
    for s in st.index:
        s = int(s)
        a, e = int(st.loc[s, 'start_pos']), int(st.loc[s, 'end_pos'])
        z = K._zones(kc, s, None, naked=False)
        if z['yday']:
            r_, v_ = prof.full[z['yday']['session_no']]
            for p, _ in z['hvn_day']:
                lo, hi = peak_band(r_, v_, p)
                rows.append(('HVN_D', a, e, lo, hi, p, s))
            for p, _ in z['lvn_day']:
                rows.append(('LVN_D', a, e, p, p, p, s))
        if z['hvn_week'] and z['hvn_week']['hvn']:
            agg = week_rows(kc, s)
            for p, _ in z['hvn_week']['hvn']:
                lo, hi = peak_band(agg[0], agg[1], p)
                rows.append(('HVN_W', a, e, lo, hi, p, s))
        if z['va_eu']:
            va.append((int(z['va_eu']['ready_pos']), z['va_eu']['vah'], z['va_eu']['val'], s))
    for k, (rp, vah, val, s) in enumerate(va):
        end = va[k + 1][0] - 1 if k + 1 < len(va) else n - 1
        rows.append(('VA_EU', rp, end, vah, vah, vah, s))
        rows.append(('VA_EU', rp, end, val, val, val, s))
    lev = pd.DataFrame(rows, columns=['grp', 'start', 'end', 'lo', 'hi', 'c', 'src'])
    w = K.vwap_series(df)
    return lev, {'VWAP_D': w['vwap_d'].to_numpy(float), 'VWAP_W': w['vwap_w'].to_numpy(float)}


def shifts(nS, reps=REPS, seed=SEED):
    """δ[phiên, bản] ~ ±U[3, 15] giá. Cùng δ cho mọi nhóm trong một (phiên, bản) ⇒ nhóm 'bất kỳ' dời đồng bộ."""
    rng = np.random.default_rng(seed)
    return rng.uniform(SHIFT_LO, SHIFT_HI, (nS, reps)) * rng.choice([-1.0, 1.0], (nS, reps))


# =====================================================================================================================
# 2. CỜ HỢP LƯU
# =====================================================================================================================
def static_flag(b0, zlo, zhi, c0, sh0, lev, grp, tol=TOL):
    """Cờ tĩnh cho từng vùng: tại nến b0 (vùng lần đầu hiện) có mức nhóm grp đang dùng được (start ≤ b0 ≤ end), tâm (đã dời sh0)
    cách giá đóng c0 ≤ RADIUS, và [zlo, zhi] giao [lo − tol, hi + tol] (đã dời). sh0: mảng dời theo vùng (0 = thật)."""
    L = lev[lev['grp'] == grp]
    if not len(L):
        return np.zeros(len(b0), bool)
    s_, e_ = L['start'].to_numpy(), L['end'].to_numpy()
    llo, lhi, lc = L['lo'].to_numpy(), L['hi'].to_numpy(), L['c'].to_numpy()
    sh = np.asarray(sh0, float)[:, None]
    act = (s_[None, :] <= b0[:, None]) & (b0[:, None] <= e_[None, :])
    near = np.abs(lc[None, :] + sh - c0[:, None]) <= RADIUS
    inter = (zlo[:, None] <= lhi[None, :] + sh + tol) & (zhi[:, None] >= llo[None, :] + sh - tol)
    return (act & near & inter).any(1)


def vwap_flag(t, zlo, zhi, vwap, sh, tol=TOL):
    """Cờ động cho từng lần chạm: VWAP tại NẾN BẮT ĐẦU t (đã dời sh) nằm trong [zlo − tol, zhi + tol] (biên vùng tại nến t)."""
    v = vwap[t] + sh
    return (v >= zlo - tol) & (v <= zhi + tol)


# =====================================================================================================================
# 3. "THẮNG 1:1" — mô tả, chưa phải chiến lược
# =====================================================================================================================
def win11(B, t, vai, lo, hi, R=WIN_R, N=WIN_N):
    """Tham chiếu = biên GẦN của vùng tại nến bắt đầu (kháng cự: lo, hỗ trợ: hi) — như lệnh chờ đặt ở biên.
    Nến t: nếu đã đi ngược ≥ R thì THUA (giá tới từ phía cũ nên chắc chắn đã qua biên trước khi đi ngược); phần đi đúng hướng
    trong nến t KHÔNG tính (không biết thứ tự). Nến t+1..t+N cùng phiên: nến đầu tiên chạm mốc; cùng một nến chạm cả hai = THUA.
    Trả mã: 1 thắng, 0 thua, −1 hết 30 nến, −2 không rõ phía."""
    H, L, sno, n = B['H'], B['L'], B['sno'], B['n']
    t = np.asarray(t, np.int64)
    kc = np.asarray(vai) == LC.KC
    ht = np.asarray(vai) == LC.HT
    edge = np.where(kc, lo, hi)
    adv0 = np.where(kc, H[t] >= edge + R, L[t] <= edge - R)
    idx = t[:, None] + np.arange(1, N + 1)[None, :]
    ci = np.minimum(idx, n - 1)
    ok = (idx < n) & (sno[ci] == sno[t][:, None])
    Hk, Lk = H[ci], L[ci]
    e2 = edge[:, None]
    k2 = kc[:, None]
    fav = ok & np.where(k2, Lk <= e2 - R, Hk >= e2 + R)
    adv = ok & np.where(k2, Hk >= e2 + R, Lk <= e2 - R)
    big = N + 5
    ff = np.where(fav.any(1), fav.argmax(1), big)
    fa = np.where(adv.any(1), adv.argmax(1), big)
    out = np.where(adv0, LOSS, np.where((fa < big) & (fa <= ff), LOSS, np.where(ff < big, WIN, TIMEOUT)))
    return np.where(kc | ht, out, NOSIDE)


# =====================================================================================================================
# 4. SO SÁNH: thật / Đ1 (dời mức) / Đ2 (khớp độ rộng × khoảng cách)
# =====================================================================================================================
SPLITS = [('TRAIN', 'split', 'TRAIN'), ('TEST', 'split', 'TEST'), ('GỘP', None, None),
          ('T8', 'thang', 'T8'), ('T9', 'thang', 'T9'), ('T10', 'thang', 'T10')]


def dbin(d):
    return np.digitize(np.asarray(d, float), D_EDGES, right=True)      # 0: ≤3 (gồm 'trong vùng'), 1: (3,6], 2: (6,12], 3: >12


def matched(y, f, cell, nc=12):
    """Đ2: so lần chạm CÓ cờ với KHÔNG cờ CÙNG ô (bin rộng × bin khoảng cách), trọng số = số lần có cờ trong ô; chỉ dùng ô có cả hai.
    Trả (p_có, se_có, n_có_dùng, p_không_cùng_ô, se_không, phủ = % lần có cờ nằm trong ô dùng được)."""
    y = y.astype(float)
    nf = np.bincount(cell[f], minlength=nc).astype(float)
    nn = np.bincount(cell[~f], minlength=nc).astype(float)
    sf = np.bincount(cell[f], y[f], minlength=nc)
    sn = np.bincount(cell[~f], y[~f], minlength=nc)
    ok = (nf > 0) & (nn > 0)
    if not ok.any():
        return (np.nan,) * 6
    w = np.where(ok, nf, 0) / nf[ok].sum()
    pf = np.where(ok, sf / np.where(nf > 0, nf, 1), 0)
    pn = np.where(ok, sn / np.where(nn > 0, nn, 1), 0)
    p1, p0 = (w * pf).sum(), (w * pn).sum()
    se1 = math.sqrt((w ** 2 * pf * (1 - pf) / np.where(nf > 0, nf, 1)).sum())
    se0 = math.sqrt((w ** 2 * pn * (1 - pn) / np.where(nn > 0, nn, 1)).sum())
    return p1, se1, int(nf[ok].sum()), p0, se0, nf[ok].sum() / max(nf.sum(), 1)


def compare_flags(D, y, f_real, F_ctrl, base):
    """D: lần chạm (đã lọc theo base), y: kết cục bool, f_real: cờ thật, F_ctrl: (R, n) cờ dưới mức dời.
    Trả dict nhóm → số đo + 2 phán quyết (đúng ngưỡng plan mục 5, dùng lan_cham.verdict)."""
    res = {}
    cell = D['cell'].to_numpy()
    for name, col, val in SPLITS:
        s = base & (np.ones(len(D), bool) if col is None else (D[col] == val).to_numpy())
        yf, yn = y[s & f_real], y[s & ~f_real]
        pf, sef, nf = LC.rate(yf)
        pn, sen, nn = LC.rate(yn)
        dlt = pf - pn if nf and nn else np.nan
        sed = math.sqrt(sef ** 2 + sen ** 2) if nf and nn else np.nan
        # Đ1: Δ dưới mức dời
        Fs = F_ctrl[:, s]
        ys = y[s].astype(float)
        cf = Fs.sum(1)
        cn = (~Fs).sum(1)
        with np.errstate(invalid='ignore', divide='ignore'):
            dc = (Fs @ ys) / cf - ((~Fs) @ ys) / cn
        b1 = LC.band(dc)
        m = matched(y[s], f_real[s], cell[s])
        res[name] = dict(pf=pf, sef=sef, nf=nf, pn=pn, sen=sen, nn=nn, d=dlt, sed=sed, d1=b1, cf=float(np.mean(cf)), m=m)
    v1 = LC.verdict({k: (x['d'], x['sed'], x['nf'], *x['d1']) for k, x in res.items()})
    v2 = LC.verdict({k: (x['m'][0], x['m'][1], x['m'][2], x['m'][3], x['m'][3] - 1.645 * x['m'][4], x['m'][3] + 1.645 * x['m'][4])
                     for k, x in res.items()})
    return res, v1, v2


def pc(x, d=1):
    return '—' if x is None or (isinstance(x, float) and np.isnan(x)) else f'{100 * x:.{d}f}'


def sg(x, d=1):
    return '—' if x is None or (isinstance(x, float) and np.isnan(x)) else f'{100 * x:+.{d}f}'


# =====================================================================================================================
# 5. DỰNG DỮ LIỆU LẦN CHẠM + CỜ
# =====================================================================================================================
def zone_table(rec, df):
    """Mỗi vùng (eid): nến lần đầu hiện b0, biên lúc đó, bin rộng, khoảng cách giá đóng → cạnh gần, bin khoảng cách, mask loại mốc."""
    C = df['close'].to_numpy(float)
    f = rec.sort_values(['eid', 'bar'], kind='stable').groupby('eid', sort=True).head(1)
    b0 = f['bar'].to_numpy()
    lo, hi = f['lo'].to_numpy(float), f['hi'].to_numpy(float)
    c0 = C[b0]
    d0 = np.where(c0 < lo, lo - c0, np.where(c0 > hi, c0 - hi, 0.0))
    return pd.DataFrame(dict(eid=f['eid'].to_numpy(), b0=b0, lo0=lo, hi0=hi, c0=c0, d0=d0, wb0=LC.wbin(hi - lo), db0=dbin(d0),
                             mask=f['mask'].to_numpy()))


def build(ctx, rec, lev, vw, dsh, tol=TOL):
    """Lần chạm thật (đã đo được) + cờ thật theo nhóm + cờ dưới REPS bản dời. Trả (D, Freal{g}, Fctrl{g}, Z, Zflag{g})."""
    df = ctx['df']
    B = LC.bar_arrays(df)
    sno = B['sno']
    ep, r, _ = LC.episodes(B, rec)
    D = LC.enrich(ep, ctx, r)
    D = D[D['meas'] & (D['ket'] != LC.HDL)].reset_index(drop=True)
    sr = D['srow'].to_numpy()
    D['lo_s'], D['hi_s'] = r['lo'].to_numpy()[sr], r['hi'].to_numpy()[sr]
    Z = zone_table(rec, df)
    D = D.merge(Z, on='eid', how='left')
    D['cell'] = D['wb0'].to_numpy() * 4 + D['db0'].to_numpy()
    D['win'] = win11(B, D['bat_dau'].to_numpy(), D['vai'].to_numpy(), D['lo_s'].to_numpy(), D['hi_s'].to_numpy())
    # cờ tĩnh theo VÙNG (tại b0), rồi gắn xuống lần chạm
    zb0, zlo, zhi, zc0 = Z['b0'].to_numpy(), Z['lo0'].to_numpy(), Z['hi0'].to_numpy(), Z['c0'].to_numpy()
    zpos = pd.Index(Z['eid']).get_indexer(D['eid'])
    Zflag = {g: static_flag(zb0, zlo, zhi, zc0, np.zeros(len(Z)), lev, g, tol) for g in STATIC}
    Fr = {g: Zflag[g][zpos] for g in STATIC}
    t = D['bat_dau'].to_numpy()
    for g in ('VWAP_D', 'VWAP_W'):
        Fr[g] = vwap_flag(t, D['lo_s'].to_numpy(), D['hi_s'].to_numpy(), vw[g], 0.0, tol)
        Zflag[g] = vwap_flag(zb0, zlo, zhi, vw[g], 0.0, tol)          # chỉ để đếm vùng (mục 5b)
    Fr['ANY'] = np.logical_or.reduce([Fr[g] for g in GRPS])
    Zflag['ANY'] = np.logical_or.reduce([Zflag[g] for g in GRPS])
    # đối chứng Đ1
    Fc = {g: np.zeros((dsh.shape[1], len(D)), bool) for g in ALLG}
    if dsh is not None:
        zs, ts = sno[zb0], sno[t]
        for k in range(dsh.shape[1]):
            for g in STATIC:
                Fc[g][k] = static_flag(zb0, zlo, zhi, zc0, dsh[zs, k], lev, g, tol)[zpos]
            for g in ('VWAP_D', 'VWAP_W'):
                Fc[g][k] = vwap_flag(t, D['lo_s'].to_numpy(), D['hi_s'].to_numpy(), vw[g], dsh[ts, k], tol)
            Fc['ANY'][k] = np.logical_or.reduce([Fc[g][k] for g in GRPS])
    return D, Fr, Fc, Z, Zflag, B, r


# =====================================================================================================================
# 6. MỤC 5a — MỨC SESSIONZONES MỘT MÌNH (vùng giả rộng 2 giá quanh mức)
# =====================================================================================================================
def level_rec(ctx, lev, vw, grp, half=LV_HALF):
    df, st = ctx['df'], ctx['st']
    parts = []
    if grp in ('VWAP_D', 'VWAP_W'):
        for s in st.index:
            a, e = int(st.loc[s, 'start_pos']), int(st.loc[s, 'end_pos'])
            b = np.arange(a, e + 1)
            parts.append(pd.DataFrame(dict(bar=b, lo=vw[grp][b] - half, hi=vw[grp][b] + half, eid=int(s))))
    else:
        L = lev[lev['grp'] == grp].reset_index(drop=True)
        for k, x in L.iterrows():
            b = np.arange(int(x['start']), int(x['end']) + 1)
            parts.append(pd.DataFrame(dict(bar=b, lo=x['c'] - half, hi=x['c'] + half, eid=k)))
    rr = pd.concat(parts, ignore_index=True)
    rr['score'] = 0.0
    return rr


def level_alone(ctx, lev, vw, grp, dsh):
    """Mức grp một mình qua cùng máy lần chạm; thật vs mức dời (cùng δ theo phiên của nến). Trả (bảng so cho đảo/xuyên/thắng)."""
    df = ctx['df']
    B = LC.bar_arrays(df)
    rr = level_rec(ctx, lev, vw, grp)
    sno_r = B['sno'][rr['bar'].to_numpy()]
    off = np.hstack([np.zeros((len(rr), 1)), dsh[sno_r]])
    order = rr.sort_values(['eid', 'bar'], kind='stable').index.to_numpy()
    ep, r, _ = LC.episodes(B, rr, off)
    E = LC.enrich(ep, ctx, r)
    E = E[E['meas'] & (E['ket'] != LC.HDL)].reset_index(drop=True)
    off_r = off[order]
    sr, rp = E['srow'].to_numpy(), E['rep'].to_numpy()
    lo = r['lo'].to_numpy()[sr] + off_r[sr, rp]
    hi = r['hi'].to_numpy()[sr] + off_r[sr, rp]
    E['win'] = win11(B, E['bat_dau'].to_numpy(), E['vai'].to_numpy(), lo, hi)
    real = E[E['rep'] == 0]
    ctrl = E[E['rep'] >= 1].copy()
    ctrl['rep'] -= 1
    out = {}
    for what in ('dao', 'xuyen', 'win'):
        res = {}
        for name, col, val in SPLITS:
            rs = real if col is None else real[real[col] == val]
            cs = ctrl if col is None else ctrl[ctrl[col] == val]
            if what == 'win':
                rs, cs = rs[rs['win'] >= 0], cs[cs['win'] >= 0]
                yr, yc = rs['win'].to_numpy() == WIN, cs['win'].to_numpy() == WIN
            else:
                kk = LC.DAO if what == 'dao' else LC.XUYEN
                yr, yc = rs['ket'].to_numpy() == kk, cs['ket'].to_numpy() == kk
            p, se, n = LC.rate(yr)
            res[name] = (p, se, n, *LC.band(LC.ctrl_rates(cs, yc, reps=dsh.shape[1])))
        out[what] = (res, LC.verdict(res))
    return out, len(real)


# =====================================================================================================================
# 7. HÌNH MINH HOẠ
# =====================================================================================================================
def draw(ctx, rec, D, Fr, lev, vw, sid, split, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection, LineCollection
    from matplotlib.patches import Rectangle
    df, st = ctx['df'], ctx['st']
    s = int(st.index[st['session_id'] == sid][0])
    a, b = int(st.loc[s, 'start_pos']), int(st.loc[s, 'end_pos'])
    W_ = 300
    flag = Fr['ANY']
    e = D[(D['bat_dau'] >= a) & (D['bat_dau'] <= b)]
    ef = e[flag[e.index.to_numpy()]]
    best, w0 = -1, a
    for x in range(a, max(a + 1, b - W_), 10):
        sc = int(((ef['bat_dau'] >= x) & (ef['bat_dau'] < x + W_ - 10)).sum())
        if sc > best:
            best, w0 = sc, x
    w1 = min(w0 + W_, b + 1)
    d = df.iloc[w0:w1]
    x = np.arange(len(d))
    O, H, L, C = (d[c].to_numpy(float) for c in ('open', 'high', 'low', 'close'))
    INK, MUTED = '#0b0b0b', '#52514e'
    KCOL = {LC.DAO: '#1baf7a', LC.XUYEN: '#eb6834', LC.CHUA_RO: '#8a8984', LC.KRP: '#8a8984'}
    KCH = {LC.DAO: 'Đ', LC.XUYEN: 'X', LC.CHUA_RO: '?', LC.KRP: '?'}
    fig, ax = plt.subplots(figsize=(22, 10), dpi=110)
    fig.patch.set_facecolor('#fcfcfb')
    ax.set_facecolor('#fcfcfb')
    r = rec[(rec['bar'] >= w0) & (rec['bar'] < w1)]
    fe = set(D.loc[flag, 'eid'].tolist()) | set()
    # vùng VCL: hợp lưu (ít nhất 1 lần chạm có cờ) đậm, còn lại nhạt
    for strong in (False, True):
        rr = r[r['eid'].isin(fe) == strong]
        polys = [[(bb - w0 - .5, lo), (bb - w0 + .5, lo), (bb - w0 + .5, hi), (bb - w0 - .5, hi)]
                 for bb, lo, hi in zip(rr['bar'].to_numpy(), rr['lo'].to_numpy(), rr['hi'].to_numpy())]
        ax.add_collection(PolyCollection(polys, facecolors='#2a78d6', edgecolors='none', alpha=0.30 if strong else 0.08))
    # mức SessionZones
    bars = np.arange(w0, w1)
    ax.plot(x, vw['VWAP_D'][bars], color='#d4a017', linewidth=1.8, label='VWAP ngày')
    ax.plot(x, vw['VWAP_W'][bars], color='#1e88e5', linewidth=1.8, label='VWAP tuần')
    sty = {'VA_EU': ('#7b3fa0', '--', 'VAH/VAL Âu'), 'HVN_D': ('#e67e22', '-', 'HVN ngày (dải)'),
           'HVN_W': ('#8d5524', '-', 'HVN tuần (dải)'), 'LVN_D': ('#7f7f7f', ':', 'LVN ngày')}
    C_ = df['close'].to_numpy(float)
    seen = set()
    for g, (col, ls, lab) in sty.items():
        Lg = lev[(lev['grp'] == g) & (lev['end'] >= w0) & (lev['start'] < w1)]
        for _, z in Lg.iterrows():
            xs = np.arange(max(int(z['start']), w0), min(int(z['end']), w1 - 1) + 1)
            vis = np.abs(z['c'] - C_[xs]) <= RADIUS
            if not vis.any():
                continue
            xx = xs - w0
            kw = dict(label=lab) if g not in seen else {}
            seen.add(g)
            if z['hi'] - z['lo'] > 1e-9:
                ax.fill_between(xx, z['lo'], z['hi'], where=vis, color=col, alpha=0.25, linewidth=0, **kw)
            else:
                ax.plot(xx, np.where(vis, z['c'], np.nan), color=col, linestyle=ls, linewidth=1.4, **kw)
    # lần chạm của vùng hợp lưu
    ee = ef[(ef['bat_dau'] >= w0) & (ef['bat_dau'] < w1)]
    for t in ee.itertuples():
        x0 = t.bat_dau - w0 - .5
        x1 = (t.thoat_cuoi if t.thoat_cuoi >= 0 else t.chot) - w0 - .5
        col = KCOL[t.ket]
        ax.add_patch(Rectangle((x0, t.lo_s), max(x1 - x0, 1), t.hi_s - t.lo_s, fill=False, edgecolor=col, linewidth=2.2))
        gs = '+'.join(GTEN[g] for g in GRPS if Fr[g][t.Index])
        wl = {WIN: 'thắng', LOSS: 'thua', TIMEOUT: 'hết 30 nến', NOSIDE: ''}[int(t.win)]
        ax.text(x0 + 0.5, t.hi_s + 0.25, f'{KCH[t.ket]}{t.dwell} · {gs} · 1:1 {wl}', color=INK, fontsize=8.5, fontweight='bold',
                va='bottom', ha='left', clip_on=True)
    upc = C >= O
    ax.add_collection(LineCollection([[(xx, l), (xx, h)] for xx, l, h in zip(x, L, H)], colors=INK, linewidths=0.6))
    ax.bar(x[upc], (C - O)[upc], bottom=O[upc], width=0.7, color='white', edgecolor=INK, linewidth=0.5)
    ax.bar(x[~upc], (O - C)[~upc], bottom=C[~upc], width=0.7, color=INK, edgecolor=INK, linewidth=0.5)
    ax.set_xlim(-2, len(d) + 1)
    ax.set_ylim(L.min() - 4, H.max() + 4)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    ax.grid(True, which='major', color='#e6e5e0', linewidth=0.6)
    tv = d['t_vn'].dt.strftime('%H:%M').to_numpy()
    tick = np.flatnonzero(d['t_vn'].dt.minute.to_numpy() % 30 == 0)
    ax.set_xticks(tick)
    ax.set_xticklabels([tv[k] for k in tick], fontsize=9, color=MUTED)
    ax.tick_params(axis='y', labelsize=9, labelright=True, colors=MUTED)
    ax.set_xlabel('giờ VN (UTC+7)', color=MUTED)
    cnt = {k: int((ee['ket'] == k).sum()) for k in (LC.DAO, LC.XUYEN)}
    ax.set_title(f'Vùng Canh Lệnh HỢP LƯU SessionZones · GCZ26 M1 · phiên {sid} ({split}) · {len(ee)} lần chạm của vùng hợp lưu: '
                 f'{cnt[LC.DAO]} đảo chiều, {cnt[LC.XUYEN]} xuyên phá\n'
                 'Xanh đậm = vùng VCL có hợp lưu (dung sai ±0,5 giá), xanh nhạt = vùng VCL khác. Khung = một lần chạm của vùng hợp lưu; '
                 'chữ = kết cục + số nến neo · mức trùng · kết quả "1:1" (4 giá trước khi ngược 4 giá, 30 nến).',
                 fontsize=11, loc='left', color=INK)
    for k, lab in ((LC.DAO, 'đảo chiều (Đ)'), (LC.XUYEN, 'xuyên phá (X)'), (LC.CHUA_RO, 'chưa rõ (?)')):
        ax.plot([], [], color=KCOL[k], linewidth=2, label=lab)
    ax.legend(loc='upper left', frameon=False, fontsize=9, ncol=2)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


# =====================================================================================================================
# 8. MAIN + REPORT
# =====================================================================================================================
OUTC = [('dao', 'ĐẢO CHIỀU'), ('xuyen', 'XUYÊN PHÁ'), ('win', 'THẮNG 1:1 (4 giá trước −4 giá, 30 nến) = thắng/(thắng+thua)')]


def outcome(D, what):
    k = D['ket'].to_numpy()
    if what == 'dao':
        return k == LC.DAO, np.ones(len(D), bool)
    if what == 'xuyen':
        return k == LC.XUYEN, np.ones(len(D), bool)
    w = D['win'].to_numpy()
    return w == WIN, w >= 0


def main():
    t0 = time.time()
    bars, lv = V5.load(V5.BASE90)
    ctx = V5.prepare(bars, lv)
    df, st = ctx['df'], ctx['st']
    meas = ctx['meas']
    with open(os.path.join(LC.CACHE, 'v5.pkl'), 'rb') as f:
        rec = pickle.load(f)['rec'].reset_index(drop=True)
    lev, vw = sz_levels(ctx)
    dsh = shifts(len(st))
    D, Fr, Fc, Z, Zflag, B, r = build(ctx, rec, lev, vw, dsh)
    t1 = time.time()
    md = ['# Hợp lưu Vùng Canh Lệnh × SessionZones — vùng VCL trùng mức SessionZones có MẠNH hơn không?', '']
    md += ['## 0. Định nghĩa ĐĂNG KÝ TRƯỚC (viết trước khi chạy, không đổi sau khi thấy TEST)', '',
           '- **Câu hỏi:** vùng VCL v5 (rộng 2–5 giá, đang hiển thị) mà TRÙNG một mức SessionZones thì lần chạm của nó có đảo chiều nhiều hơn, '
           'xuyên phá ít hơn, "thắng 1:1" nhiều hơn vùng VCL không trùng không?',
           '- **Lần chạm, đảo chiều, xuyên phá:** y hệt `PLAN-LAN-CHAM.md` mục 2 (τ = 0, E = 2 giá, G = 5 nến), máy `lan_cham.episodes`. '
           'Mẫu số %đảo/%xuyên = MỌI lần chạm đã chốt (gồm "chưa rõ", "không rõ phía"), như bảng chính LAN-CHAM.md.',
           '- **Mức SessionZones** = những gì `SessionZones.cs` vẽ MẶC ĐỊNH (`ZonePolicy`): VWAP ngày, VWAP tuần, VAH/VAL phiên Âu, HVN ngày, '
           'HVN tuần, LVN ngày. Bản Python: `kernel.vwap_series` (VWAP), `kernel._zones` (va_eu, hvn_day, lvn_day, hvn_week). '
           'VA Âu chốt lúc 19:00 VN và **mang sang** tới khi phiên Âu kế tiếp chốt (đúng `VaEdgeSessionIndex` của C#). HVN ngày/tuần có '
           '**dải** = PeakSharpness 90% (port đúng C#: nới liên tục tới khi volume hàng < 90% hàng đỉnh); VAH/VAL, LVN là **điểm**. '
           'Mức tĩnh chỉ tính khi tâm cách giá đóng ≤ 12 giá (`ZoneRadiusPrices` — SessionZones chỉ vẽ trong bán kính này); VWAP luôn vẽ.',
           '- **Hợp lưu:** vùng [lo, hi] giao [mức_lo − 0,5 ; mức_hi + 0,5] (mức điểm: lo = hi). **Mức tĩnh: cờ chốt ở nến vùng LẦN ĐẦU hiện** '
           '(biên lúc đó), gắn cho mọi lần chạm của vùng. **VWAP (mức động): cờ chốt ở NẾN BẮT ĐẦU từng lần chạm** (VWAP tại nến đó, biên vùng tại '
           'nến đó) — vì VWAP trôi suốt phiên, cờ lúc vùng mới hiện không nói gì về lúc giá tới. Nhóm **BẤT KỲ** = có ít nhất 1 cờ trong 6 nhóm. '
           'Độ nhạy dung sai 0 / 0,5 / 1,5 giá — chỉ báo, không chọn lại.',
           '- **"Thắng 1:1" (mục 6, MÔ TẢ, chưa phải chiến lược — chưa phí, chưa trượt giá, chưa xét có vào được lệnh không):** tham chiếu = biên '
           'GẦN của vùng tại nến bắt đầu (như lệnh chờ ở biên). Thắng = giá đi đúng hướng đảo ≥ 4 giá trước khi đi ngược ≥ 4 giá, trong 30 nến '
           'cùng phiên. Nến bắt đầu: đã đi ngược ≥ 4 giá ⇒ thua; phần đi đúng hướng trong nến này không tính. Một nến chạm cả hai mốc ⇒ THUA '
           '(thận trọng). Số đo = thắng / (thắng + thua); "hết 30 nến" báo riêng. Lần chạm "không rõ phía" không tính.',
           f'- **Đ1 — dời mức:** mọi mức SessionZones (cả đường VWAP) dời δ, |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, cố định trong (phiên, bản), {REPS} bản; '
           'gắn cờ lại y hệt (kể cả lọc bán kính 12 giá). So **Δ = %(có cờ) − %(không cờ)** thật với dải 5–95% của Δ dưới mức dời.',
           '- **Đ2 — khớp độ rộng × khoảng cách:** so lần chạm có cờ với lần chạm KHÔNG cờ **cùng ô** (bin rộng 2–3/3–4/4–5 giá × bin khoảng cách '
           'giá đóng → cạnh gần lúc vùng hiện ≤3/3–6/6–12/>12 giá), trọng số = số lần có cờ trong ô. "Dải đối chứng" Đ2 = % không cờ cùng ô '
           '± 1,645 sai số (≈ 5–95%).',
           '- **Ngưỡng "khác đối chứng" (`PLAN-LAN-CHAM.md` mục 5, dùng NGUYÊN, hàm `lan_cham.verdict`):** ngoài dải 5–95% ở CẢ TRAIN và TEST, '
           'cùng dấu, cùng dấu ở ≥ 2/3 tháng, VÀ |hiệu| > 2 sai số nhị thức ở cả TRAIN và TEST. Thiếu một ⇒ "≈ đối chứng". '
           '**Chỉ gọi là CÓ khi vượt CẢ Đ1 lẫn Đ2 cùng chiều VÀ Δ cùng dấu ở cả 3 mức dung sai.**',
           f'- **Số phép so:** 7 nhóm × 3 kết cục × 2 đối chứng = 42 phán quyết (+ mục 5a: 6 nhóm × 3 kết cục = 18). Với chừng ấy phép so, '
           'một vài ô "vượt" do ngẫu nhiên là chuyện bình thường (nếu mỗi phép so có ~5% vượt ngẫu nhiên thì kỳ vọng ~2 ô trong 42) — '
           'ngưỡng nhiều điều kiện ở trên chặt hơn 5% nhiều, nhưng vẫn phải đọc với cảnh giác đó.',
           '- **Tự quyết (ghi rõ):** (a) VA Âu mang sang ngày sau như C#; (b) HVN/LVN ngày từ profile PHIÊN CME TRƯỚC (kernel), còn C# dùng 24 giờ '
           'cuối cập nhật mỗi khi block Á/Âu/Mỹ đóng — **khác C#**; (c) không mô phỏng trần 5 vùng / gộp vùng / mục tiêu xa của SessionZones; '
           '(d) mục 5a dùng vùng giả rộng 2 giá (tâm ± 1) cho MỌI mức (đề bài ghi cả "±0,5" lẫn "rộng 2 giá" — chọn 2 giá để cùng cỡ vùng VCL '
           'hẹp nhất); (e) Đ1 dời theo (phiên, bản), cùng δ cho mọi nhóm.', '']
    ntr = int((meas & (st['split'] == 'TRAIN').to_numpy()).sum())
    nte = int((meas & (st['split'] == 'TEST').to_numpy()).sum())
    md += ['## 1. Dữ liệu', '',
           f'`fp_GCZ26_XCEC_Time_20260723-20261021_90d` ({len(df)} nến M1, giờ UTC, một hợp đồng). Phiên đo **{int(meas.sum())}** '
           f'(TRAIN {ntr} đến 2026-09-15, TEST {nte}); loại 4 phiên đầu (phiên 0 + thin) như LAN-CHAM.md. '
           f'Lần chạm đã chốt trong phiên đo: **{len(D)}** (TRAIN {int((D["split"] == "TRAIN").sum())}, TEST {int((D["split"] == "TEST").sum())}) '
           f'— khớp LAN-CHAM.md (4749). Vùng (mã) có ≥ 1 lần chạm: {D["eid"].nunique()}.',
           f'Mức SessionZones dựng được: ' + ', '.join(f"{GTEN[g]} {int((lev['grp'] == g).sum())}" for g in STATIC) +
           ' (số mức-phiên; VA Âu = 2 mức mỗi phiên Âu). VWAP ngày/tuần: mỗi nến. Độ rộng dải HVN (p10 / trung vị / p90 / lớn nhất, giá): ' +
           ' · '.join(f"{GTEN[g]} " + ' / '.join(f'{x:.1f}' for x in np.quantile((lev[lev['grp'] == g]['hi'] - lev[lev['grp'] == g]['lo']).to_numpy(), [.1, .5, .9, 1]))
                      for g in ('HVN_D', 'HVN_W')) +
           '. (Trên chart có lúc thấy "mảng HVN tuần" ~20 giá: đó là 2–3 dải HVN tuần nằm sát nhau, không phải một dải.)',
           f'Thời gian: dựng + {REPS} bản dời {t1 - t0:.0f}s.', '']

    # ---------------- 5b: số vùng
    zmeas = meas[B['sno'][Z['b0'].to_numpy()]]
    nses = int(meas.sum())
    md += ['## 2. Còn bao nhiêu vùng nếu chỉ giữ vùng hợp lưu? (mục 5b)', '',
           'Hai cách đếm: (i) **vùng mới** (mã vùng) hiện trong phiên đo, cờ tại nến vùng lần đầu hiện (VWAP: tại nến đó); '
           '(ii) **trên chart tại mỗi nến**: số vùng VCL đang hiển thị trùng mức SessionZones ĐANG có ở nến đó (VWAP tại nến đó, mức tĩnh '
           'trong bán kính 12 giá) — đây là con số người học sẽ thấy.', '',
           '| Nhóm | vùng mới hợp lưu / tổng | % | vùng mới hợp lưu / phiên | vùng hợp lưu đang hiện / nến (TB) | % nến có ≥ 1 vùng hợp lưu |',
           '|---|---|---|---|---|---|']
    # (ii) theo nến
    rb, rlo, rhi = rec['bar'].to_numpy(), rec['lo'].to_numpy(float), rec['hi'].to_numpy(float)
    C_ = df['close'].to_numpy(float)
    rowmeas = meas[B['sno'][rb]]
    rowflag = {}
    for g in STATIC:
        fl = np.zeros(len(rec), bool)
        for z in lev[lev['grp'] == g].itertuples():
            m = (rb >= z.start) & (rb <= z.end)
            if not m.any():
                continue
            idx = np.flatnonzero(m)
            ok = (np.abs(z.c - C_[rb[idx]]) <= RADIUS) & (rlo[idx] <= z.hi + TOL) & (rhi[idx] >= z.lo - TOL)
            fl[idx[ok]] = True
        rowflag[g] = fl
    for g in ('VWAP_D', 'VWAP_W'):
        v = vw[g][rb]
        rowflag[g] = (v >= rlo - TOL) & (v <= rhi + TOL)
    rowflag['ANY'] = np.logical_or.reduce([rowflag[g] for g in GRPS])
    nb = np.bincount(rb[rowmeas], minlength=len(df))
    barm = meas[B['sno']] & (nb > 0)
    md.append(f'| (mọi vùng VCL) | {int(zmeas.sum())} / {int(zmeas.sum())} | 100 | {zmeas.sum() / nses:.1f} | {nb[barm].mean():.2f} | — |')
    ZB = {}
    for g in ALLG:
        zf = Zflag[g][zmeas]
        cnt = np.bincount(rb[rowmeas & rowflag[g]], minlength=len(df))[barm]
        ZB[g] = (zf.sum(), zf.mean(), zf.sum() / nses, cnt.mean(), (cnt > 0).mean())
        md.append(f'| {GTEN[g]} | {int(zf.sum())} / {len(zf)} | {100 * zf.mean():.1f} | {zf.sum() / nses:.1f} | {cnt.mean():.2f} | {100 * (cnt > 0).mean():.0f} |')
    cbit = V2.BIT['C']
    vaz = Z[zmeas & Zflag['VA_EU']]
    md += ['', f'Ghi chú cấu tạo: VCL lấy chính VAH/VAL Âu làm mốc loại C (`vcl.gen_candidates`) ⇒ một phần hợp lưu VA Âu là **tự trùng do '
           f'cấu tạo**: {100 * ((vaz["mask"].to_numpy() & cbit) > 0).mean():.0f}% vùng hợp lưu VA Âu có mốc loại C (so với '
           f'{100 * ((Z[zmeas]["mask"].to_numpy() & cbit) > 0).mean():.0f}% mọi vùng). VWAP và HVN/LVN KHÔNG nằm trong ứng viên VCL.', '']

    # ---------------- 1 + 2 + 3: bảng chính
    VER = {}
    RES = {}
    md += ['## 3. Kết quả chính — có cờ vs không cờ, thật vs Đ1 (dời mức) vs Đ2 (khớp rộng × khoảng cách)', '',
           'Đọc: **Δ = % có cờ − % không cờ** (điểm %). Đ1 = Δ khi dời mức SessionZones 3–15 giá [5%–95%]. Đ2 = % có cờ (chỉ ô có cặp) so với '
           '% không cờ CÙNG ô. n = lần chạm. Sai số nhị thức đánh giá THẤP (nhiều lần chạm cùng một vùng).', '']
    for what, nm in OUTC:
        y, base = outcome(D, what)
        md += [f'### {nm} — GỘP TRAIN+TEST', '',
               '| Nhóm | n có cờ (vùng) | % có cờ | % không cờ (n) | **Δ thật** ±se | Đ1: Δ dời TB [5–95] | Đ2: có cờ vs không cờ cùng ô (phủ) | Phán quyết Đ1 | Phán quyết Đ2 |',
               '|---|---|---|---|---|---|---|---|---|']
        for g in ALLG:
            res, v1, v2 = compare_flags(D, y, Fr[g] & base, Fc[g] & base[None, :], base)
            # (cờ & base: chỉ để đếm; mẫu đã lọc base trong compare_flags)
            RES[(what, g)] = res
            VER[(what, g)] = (v1, v2)
            x = res['GỘP']
            nz = D.loc[Fr[g] & base, 'eid'].nunique()
            m = x['m']
            md.append(f"| {GTEN[g]} | {x['nf']} ({nz}) | {pc(x['pf'])} | {pc(x['pn'])} ({x['nn']}) | **{sg(x['d'])}** ±{pc(x['sed'])} | "
                      f"{sg(x['d1'][0])} [{sg(x['d1'][1])}; {sg(x['d1'][2])}] | {pc(m[0])} vs {pc(m[3])} ({pc(m[5], 0)}%) | {v1} | {v2} |")
        md.append('')
        md += [f'#### {nm} — Δ thật [dải Đ1] theo TRAIN / TEST / tháng', '', '| Nhóm | TRAIN | TEST | T8 | T9 | T10 |', '|---|---|---|---|---|---|']
        for g in ALLG:
            res = RES[(what, g)]
            cells = []
            for nm_ in ('TRAIN', 'TEST', 'T8', 'T9', 'T10'):
                x = res[nm_]
                cells.append(f"{sg(x['d'])} ±{pc(x['sed'])} [{sg(x['d1'][1], 0)}; {sg(x['d1'][2], 0)}] (n={x['nf']})")
            md.append(f'| {GTEN[g]} | ' + ' | '.join(cells) + ' |')
        md += ['', f'#### {nm} — Đ2 theo TRAIN / TEST / tháng: % có cờ vs % không cờ cùng ô', '', '| Nhóm | TRAIN | TEST | T8 | T9 | T10 |',
               '|---|---|---|---|---|---|']
        for g in ALLG:
            res = RES[(what, g)]
            md.append(f'| {GTEN[g]} | ' + ' | '.join(f"{pc(res[n_]['m'][0])} vs {pc(res[n_]['m'][3])}" for n_ in ('TRAIN', 'TEST', 'T8', 'T9', 'T10')) + ' |')
        md.append('')
    # bảng "chưa rõ" (kiểm tra cơ chế hiển thị — A2 của LAN-CHAM)
    k_ = D['ket'].to_numpy()
    md += ['### Phần còn lại: % "chưa rõ" (vùng rời bộ/hết phiên khi giá còn neo) và % "hết 30 nến" — có cờ vs không cờ (GỘP, chỉ mô tả)', '',
           'Cột cuối = đảo / (đảo + xuyên): bỏ "chưa rõ" và "không rõ phía" — THÊM SAU khi thấy "chưa rõ" chênh nhau, KHÔNG đăng ký trước, '
           'không phán quyết, chỉ để biết chênh %đảo có phải do "chưa rõ" không.', '',
           '| Nhóm | chưa rõ % có cờ | chưa rõ % không cờ | hết 30 nến % có cờ | hết 30 nến % không cờ | đảo/(đảo+xuyên) % có cờ vs không cờ |',
           '|---|---|---|---|---|---|']
    wv = D['win'].to_numpy()
    sidem = wv != NOSIDE
    cls = np.isin(k_, (LC.DAO, LC.XUYEN))
    for g in ALLG:
        f = Fr[g]
        md.append(f"| {GTEN[g]} | {pc((k_[f] == LC.CHUA_RO).mean())} | {pc((k_[~f] == LC.CHUA_RO).mean())} | "
                  f"{pc((wv[f & sidem] == TIMEOUT).mean())} | {pc((wv[~f & sidem] == TIMEOUT).mean())} | "
                  f"{pc((k_[f & cls] == LC.DAO).mean())} (n={int((f & cls).sum())}) vs {pc((k_[~f & cls] == LC.DAO).mean())} |")
    md.append('')

    # ---------------- độ nhạy dung sai
    md += ['## 4. Độ nhạy dung sai hợp lưu (chỉ báo, không chọn lại) — Δ thật GỘP (TRAIN / TEST)', '',
           '| Nhóm | Kết cục | tol 0 | **tol 0,5 (chốt)** | tol 1,5 |', '|---|---|---|---|---|']
    SENS = {}
    Dt = {}
    for tol in TOLS:
        Dx, Frx, _, _, Zx, _, _ = build(ctx, rec, lev, vw, np.zeros((len(st), 1)), tol)
        Dt[tol] = (Dx, Frx, Zx)
    for g in ALLG:
        for what, nm in OUTC:
            cells = []
            for tol in TOLS:
                Dx, Frx, _ = Dt[tol]
                y, base = outcome(Dx, what)
                vals = []
                for sp in (None, 'TRAIN', 'TEST'):
                    s = base & (True if sp is None else (Dx['split'] == sp).to_numpy())
                    a_, b_ = y[s & Frx[g]], y[s & ~Frx[g]]
                    vals.append(a_.mean() - b_.mean() if len(a_) and len(b_) else np.nan)
                SENS[(g, what, tol)] = vals
                n_ = int((base & Frx[g]).sum())
                cell = f"{sg(vals[0])} ({sg(vals[1], 0)} / {sg(vals[2], 0)}) n={n_}"
                cells.append(f'**{cell}**' if tol == TOL else cell)
            md.append(f'| {GTEN[g]} | {nm.split(" ")[0].lower()} | ' + ' | '.join(cells) + ' |')
    md.append('')

    # ---------------- kết luận theo luật đăng ký
    md += ['## 5. Phán quyết theo luật đã đăng ký', '', '| Nhóm | Kết cục | Đ1 | Đ2 | Δ cùng dấu ở 3 mức dung sai? | **KẾT LUẬN** |', '|---|---|---|---|---|---|']
    YES = []
    for g in ALLG:
        for what, nm in OUTC:
            v1, v2 = VER[(what, g)]
            sv = [SENS[(g, what, tol)][0] for tol in TOLS]
            same = all(np.sign(x) == np.sign(sv[1]) for x in sv if not np.isnan(x)) and not any(np.isnan(sv))
            ok = v1.startswith('KHÁC') and v2.startswith('KHÁC') and v1[-1] == v2[-1] and same
            if ok:
                YES.append((g, what, v1[-1]))
            md.append(f"| {GTEN[g]} | {nm.split(' ')[0].lower()} | {v1} | {v2} | {'có' if same else 'KHÔNG'} | "
                      f"{'**CÓ ' + v1[-1] + '**' if ok else '≈ đối chứng'} |")
    md += ['', f"Số ô vượt Đ1: {sum(1 for k in VER if VER[k][0].startswith('KHÁC'))} / 21 · vượt Đ2: "
           f"{sum(1 for k in VER if VER[k][1].startswith('KHÁC'))} / 21 · vượt cả hai + bền dung sai: **{len(YES)} / 21**.", '']

    # ---------------- 5a: mức SessionZones một mình
    md += ['## 6. Bối cảnh (mục 5a): CHÍNH mức SessionZones một mình (không cần vùng VCL)', '',
           'Mỗi mức = vùng giả rộng 2 giá (tâm ± 1), cùng máy lần chạm; đối chứng = cùng mức dời 3–15 giá (cùng δ theo phiên, '
           f'{REPS} bản). Không lọc bán kính. Đây là "mức một mình", để biết hợp lưu có thêm gì so với từng mức riêng.', '',
           '| Mức | n lần chạm | % đảo: thật · Đ1 TB [5–95] | % xuyên: thật · Đ1 TB [5–95] | thắng 1:1: thật · Đ1 TB [5–95] | phán quyết đảo · xuyên · thắng |', '|---|---|---|---|---|---|']
    LA = {}
    for g in GRPS:
        out, nre = level_alone(ctx, lev, vw, g, dsh)
        LA[g] = out
        cells = []
        for what in ('dao', 'xuyen', 'win'):
            res, v = out[what]
            x = res['GỘP']
            cells.append(f"**{pc(x[0])}** ±{pc(x[1])} · Đ1 {pc(x[3])} [{pc(x[4])}; {pc(x[5])}]")
        md.append(f"| {GTEN[g]} | {nre} | " + ' | '.join(cells) + ' | ' + ' · '.join(out[w_][1] for w_ in ('dao', 'xuyen', 'win')) + ' |')
    md += ['', 'TRAIN / TEST (thật · Đ1 trung bình [5–95]):', '', '| Mức | Kết cục | TRAIN | TEST |', '|---|---|---|---|']
    for g in GRPS:
        for what in ('dao', 'xuyen', 'win'):
            res, _ = LA[g][what]
            md.append(f"| {GTEN[g]} | {what} | " + ' | '.join(f"{pc(res[s_][0])} · Đ1 {pc(res[s_][3])} [{pc(res[s_][4])}; {pc(res[s_][5])}] (n={res[s_][2]})"
                                                          for s_ in ('TRAIN', 'TEST')) + ' |')
    md.append('')

    # ---------------- hình
    os.makedirs(IMG, exist_ok=True)
    imgs = []
    for split in ('TRAIN', 'TEST'):
        Ds = D[(D['split'] == split) & Fr['ANY']]
        cnt = Ds.groupby('sno').size()
        s_best = int(cnt.idxmax())
        sid = st.loc[s_best, 'session_id']
        p = os.path.join(IMG, f'hop_luu_sz_{split}_{sid}.png')
        draw(ctx, rec, D, Fr, lev, vw, sid, split, p)
        imgs.append((split, sid, os.path.basename(p)))
    md += ['## 7. Hình minh hoạ', ''] + [f'- {sp} phiên {sid}: [img/{fn}](img/{fn})' for sp, sid, fn in imgs] + \
          ['', 'Chọn phiên có nhiều lần chạm của vùng hợp lưu nhất trong mỗi tách (chọn để minh hoạ, KHÔNG phải ca điển hình).', '']
    md += ['<!-- NHAN-XET -->', '']
    path = os.path.join(REPORT, 'HOP-LUU-SZ.md')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    tail = old.split('<!-- NHAN-XET -->', 1)[1] if '<!-- NHAN-XET -->' in old else '\n## Kết luận\n(chưa viết)\n'
    open(path, 'w', encoding='utf-8').write('\n'.join(md[:-2]) + '\n<!-- NHAN-XET -->' + tail)
    print('\n'.join(md))
    print(f'TỔNG THỜI GIAN: {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
