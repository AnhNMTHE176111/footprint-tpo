# -*- coding: utf-8 -*-
"""Setup C-v6 (plan `research/PLAN-C-v2.md`): C "Fade cạnh" + cổng hình dạng D/P/b + VA nhỏ từ 3 lần đổi hành vi (CHoCH).

Chạy:  python3 setup_c_v6.py            → report/RESULTS-C-V6.md + report/img/c_v6_*.png (tất định, hạt cố định)
Test:  python3 -m pytest test_setup_c_v6.py -q

CHỈ file D90 (`fp_GCZ26_XCEC_Time_20260723-20261021_90d`), người dùng chốt. KHÔNG sửa kernel.py / setup_c_fade_canh.py:
`detect()` dưới đây là BẢN SAO nguyên văn của setup_c_fade_canh.detect + một tham số tuỳ chọn `zone_name` (test chứng minh khớp từng lệnh).
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
import time
from contextlib import contextmanager

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_c_fade_canh as C  # noqa: E402
import zones_c_v6 as Z  # noqa: E402
import benzo_vcl as BV  # noqa: E402

D90 = C.D90
TICK = K.CONST['tick']
REPORT = os.path.join(HERE, 'report')
IMG = os.path.join(REPORT, 'img')
OUT_MD = os.path.join(REPORT, 'RESULTS-C-V6.md')
EVAL_MD = os.path.join(REPORT, 'RESULTS-C-V6.danhgia.md')

# ------------------------------------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC (mục 3)
PEN, MIN_W = 2, 6.0                       # ô khởi điểm C0: xuyên 2 tick, rộng >= 6 giá
EXCL = (780, 860)                         # trừ 18:00–19:20 VN (như C0)
EXCL_VO = (780, 930)                      # bản thêm: chặn tới 20:30 VN (luật cứng C# InVirtualOpen 19:20–20:30)
SHIFT_LO, SHIFT_HI, REPS, SEED = 3.0, 15.0, 100, 20261024   # ĐC-a: cùng ma trận δ với A-v4 / VCL / B-v2
CTRL_DRAWS = 200                          # ĐC-b: kernel.control_sample 200 lần
PERM = 1000                               # ĐC-c cổng: hoán vị nhãn 1.000 lần
FAKE_REPS = 100                           # ĐC-c VA_C: 100 bản "VA giả"
DIST_DRAWS = 200                          # ĐC-c VA_C: khớp khoảng cách 200 lần
MIN_N = 10                                # phán quyết đối chứng chỉ khi >= 10 lệnh ở CẢ TRAIN và TEST
SIGMA_R = 1.6                             # σ_R đo ở A-v4 (mục 3.3)
EXPECT_C0 = dict(poc=(103, -0.43), fixed2=(121, -0.26))
GROUPS = BV.GROUPS                        # TRAIN, TEST, GỘP, T8, T9, T10


# =============================================================================================
# detect — BẢN SAO setup_c_fade_canh.detect + zone_name
# =============================================================================================
def detect(df: pd.DataFrame, zones: pd.DataFrame, mode: pd.DataFrame, pen_ticks: int = 2, min_width: float = 6.0,
           tp_mode: str = 'poc', confirm: bool = False, second_touch: bool = False, strong_delta: bool = False,
           mad: pd.Series | None = None, conf=None, min_conf: int = 0, v4: bool = False, u: pd.Series | None = None,
           excl: tuple = (780, 860), gate=None, zone_name=None) -> list:
    """Như setup_c_fade_canh.detect. zone_name = (mảng tên cạnh trên, mảng tên cạnh dưới) theo nến; '' ⇒ tên mặc định."""
    n = len(df)
    hi, lo, cl, op, dl = (df[c].to_numpy(float) for c in ('high', 'low', 'close', 'open', 'delta'))
    rng = hi - lo
    sm, sno = df['sm'].to_numpy(), df['session_no'].to_numpy()
    phase = df['phase'].to_numpy()
    bh, bl = mode['band_hi'].to_numpy(float), mode['band_lo'].to_numpy(float)
    bsrc = mode['band_src'].to_numpy()
    poc = zones['eu_poc'].to_numpy(float)
    pen = pen_ticks * TICK - 1e-9
    with np.errstate(invalid='ignore'):
        width = bh - bl
        base = (mode['mode'].to_numpy() == 'BALANCE') & (width >= min_width - 1e-9) & (~df['splice'].to_numpy()) & \
               (~df['thin'].to_numpy()) & ~((sm >= excl[0]) & (sm < excl[1])) & np.isin(phase, ['A', 'EU', 'US'])
    cm = pd.Series(rng).groupby(sno).cummax().to_numpy()
    prev = np.r_[-np.inf, cm[:-1]]
    first = np.r_[True, sno[1:] != sno[:-1]]
    prev = np.where(first, -np.inf, prev)
    notbig = rng < prev
    body = np.abs(cl - op)
    with np.errstate(invalid='ignore'):
        sell = base & notbig & (hi >= bh + pen) & (cl < bh) & (dl < 0) & ((np.minimum(op, cl) - lo) <= body)
        buy = base & notbig & (lo <= bl - pen) & (cl > bl) & (dl > 0) & ((hi - np.maximum(op, cl)) <= body)
    if strong_delta:
        md = (mad if mad is not None else K.med_abs_delta(df)).to_numpy(float)
        with np.errstate(invalid='ignore'):
            sd = np.abs(dl) >= md
        sell &= sd
        buy &= sd
    sstart = df.groupby('session_no').cumcount().to_numpy()
    sstart = np.arange(n) - sstart
    cands = []
    for j in np.flatnonzero(sell | buy):
        side = -1 if sell[j] else 1
        E = bh[j] if side < 0 else bl[j]
        if second_touch:
            s0 = sstart[j]
            if j - 5 < s0:
                continue
            seg_b = bh[s0:j - 4] if side < 0 else bl[s0:j - 4]
            seg_x = hi[s0:j - 4] >= E - TICK + 1e-9 if side < 0 else lo[s0:j - 4] <= E + TICK - 1e-9
            if not np.any((np.abs(seg_b - E) < 1e-6) & seg_x):
                continue
        i = j
        if confirm:
            i = j + 1
            if i >= n or sno[i] != sno[j] or not base[i] or not notbig[i] or abs((bh[i] if side < 0 else bl[i]) - E) > 1e-6:
                continue
            if side < 0 and not (cl[i] < E and hi[i] <= hi[j]):
                continue
            if side > 0 and not (cl[i] > E and lo[i] >= lo[j]):
                continue
        cands.append((i, j, side, E))
    cands.sort()
    out, count = [], {}
    for i, j, side, E in cands:
        key = (int(sno[j]), round(float(E), 1))
        if count.get(key, 0) >= 2:
            continue
        struct = max(hi[j], hi[i]) if side < 0 else min(lo[j], lo[i])
        r = K.risk(df, i, side, float(struct), rr=2.0)
        if r is None:
            continue
        ent, d = r['entry'], r['risk']
        opp = bl[i] if side < 0 else bh[i]
        if tp_mode == 'poc':
            lv = [opp] + ([poc[i]] if poc[i] == poc[i] else [])
            lv = [x for x in lv if (ent - x) * side * -1 > 0]
            if not lv:
                continue
            tp = max(lv) if side < 0 else min(lv)
            if abs(tp - ent) < 2.0 * d - 1e-9:
                continue
            tp = round(float(tp), 6)
        else:
            tp = r['tp']
        if phase[i] == 'US':
            nm = ('IB_H' if side < 0 else 'IB_L') if bsrc[i] == 'ib' else ('VAH_EU' if side < 0 else 'VAL_EU')
        else:
            nm = 'VAH_Y' if side < 0 else 'VAL_Y'
        if zone_name is not None:
            zn = zone_name[0][i] if side < 0 else zone_name[1][i]
            if zn:
                nm = zn
        if gate is not None and not gate(int(i), int(j), int(side)):
            continue
        nconf = 1
        if conf is not None:
            nconf = conf.count(int(i), float(E))
            if nconf < min_conf:
                continue
        if v4:
            vd, vw = zones['vwap_d'].to_numpy(float)[i], zones['vwap_w'].to_numpy(float)[i]
            yv, yl = conf.zc0['yd_vah'].to_numpy(float)[i], conf.zc0['yd_val'].to_numpy(float)[i]
            ui = float(u.iloc[i]) if u is not None else float('nan')
            if not (abs(vd - vw) <= 2 * ui and yl <= cl[i] <= yv):
                continue
        count[key] = count.get(key, 0) + 1
        out.append(dict(nconf=nconf, idx=int(i), side=int(side), entry=ent, sl=r['sl'], tp=tp, setup='C', zone=nm, edge=float(E),
                        poke_idx=int(j), width=float(width[i]), note='fade %s E=%.1f' % (nm, E)))
    return out


# =============================================================================================
# DỮ LIỆU + LỚP
# =============================================================================================
def prep_from(df, prof):
    """Y HỆT setup_c_fade_canh.prepare nhưng nhận (df, prof) sẵn có — dùng cho test cắt dữ liệu (test kiểm khớp với prepare)."""
    ctx = K._Ctx(df, prof)
    zc = K.zone_columns(df, prof, ctx)
    zc2 = zc.copy()
    pre = (df['sm'].to_numpy() < K.CONST['sm_us_start'])
    for a, b in (('eu_vah', 'yd_vah'), ('eu_val', 'yd_val'), ('eu_poc', 'yd_poc')):
        zc2.loc[pre, a] = zc.loc[pre, b].to_numpy()
    m5 = K.m5_bars(df, zc2)
    mf = K.mode_frame(df, zc2, m5)
    st = K.session_table(df)
    ok = (~st['splice'].to_numpy()) & (~st['thin'].to_numpy()) & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
    return dict(df=df, zc=zc2, zc0=zc, mf=mf, st=st, days=int(ok.sum()), mad=K.med_abs_delta(df), prof=prof, ctx=ctx, u=K.median_range(df))


class Data:
    def __init__(self, base=D90, P=None):
        self.P = P if P is not None else C.prepare(base)
        df = self.df = self.P['df']
        self.zc2, self.zc0, self.ctx = self.P['zc'], self.P['zc0'], self.P['ctx']
        self.u = self.P['u'].to_numpy(float)
        self.vma = Z.vma_series(df).to_numpy(float)
        self.avgr = Z.avg_range_before(df).to_numpy(float)
        self.piv = K.zigzag(df, Z.ZZ, by_session=True)
        self.yd = Z.yday_of(self.ctx)
        self.sno = df['session_no'].to_numpy()
        st = K.session_table(df)
        st['split'] = np.where(st['session_id'].str[:10] <= K.CONST['split_train_end'], 'TRAIN', 'TEST')
        self.st = st
        self.clean = (~st['splice'].to_numpy()) & (~st['thin'].to_numpy()) & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
        self.clean_snos = [int(s) for s in st.index[self.clean]]
        self.days = int(self.clean.sum())
        self.days_split = {sp: int((self.clean & (st['split'] == sp).to_numpy()).sum()) for sp in ('TRAIN', 'TEST')}
        self.dsh = Z.shift_matrix(int(self.sno.max()) + 1, REPS, SHIFT_LO, SHIFT_HI, SEED)

    def shapes(self, **kw):
        return Z.shape_by_session(self.df, self.ctx, yd=self.yd, **kw)

    def choch(self, params=None, shift=None, vas=None):
        return Z.choch_va(self.df, self.u, self.vma, params, template=self.zc0, pivots=self.piv, avgr=self.avgr, shift=shift, vas=vas)


def build_layer(D, kind, shapes=None, choch=None, d_band='vol', shift=None):
    """Lớp = (zc, names, mf). shift: δ theo session_no cộng vào band + POC của lớp L0/L1/L2 (ĐC-a). L3 dời qua choch(shift=…)."""
    zc, names = Z.layer_zcols(D.df, D.zc2, kind, shapes, choch, d_band)
    if shift is not None and kind != 'L3':
        d = np.asarray(shift, float)[D.sno]
        zc = zc.copy()
        for c in ('eu_vah', 'eu_val', 'eu_poc', 'ib_hi', 'ib_lo'):
            zc[c] = zc[c].to_numpy(float) + d
    if kind == 'L0' and shift is None:
        mf = D.P['mf']
    elif kind == 'L3':
        mf = choch['mf']
    else:
        mf = K.mode_frame(D.df, zc, K.m5_bars(D.df, zc))
    return dict(kind=kind, zc=zc, names=names, mf=mf)


def entries_of(D, L, tp_mode='poc', min_width=MIN_W, excl=EXCL):
    e = detect(D.df, L['zc'], L['mf'], pen_ticks=PEN, min_width=min_width, tp_mode=tp_mode, mad=D.P['mad'], excl=excl,
               zone_name=L['names'])
    for x in e:
        x['layer'] = L['kind']
    return e


def sim(D, ents, labels=None, one=True):
    t = K.simulate(D.df, ents, one_at_a_time=one)
    if len(t):
        t['thang'] = [BV.thang_of(x) for x in t['session_id']]
        sn = D.sno[t['idx'].to_numpy()]
        t['label'] = [((labels.get(int(s)) or {}).get('label', '') if labels else '') for s in sn]
        t['sno'] = sn
    return t


def merge(D, e2, e3):
    """C4 = L2 ∪ L3: cùng nến hai lớp cùng bắn ⇒ lớp có cạnh gần close hơn, hoà ⇒ L3."""
    cl = D.df['close'].to_numpy(float)
    by2, by3 = {}, {}
    for e in e2:
        by2.setdefault(e['idx'], []).append(e)
    for e in e3:
        by3.setdefault(e['idx'], []).append(e)
    out = []
    for i in sorted(set(by2) | set(by3)):
        a, b = by2.get(i, []), by3.get(i, [])
        if a and b:
            da = min(abs(cl[i] - x['edge']) for x in a)
            db = min(abs(cl[i] - x['edge']) for x in b)
            out += a if da < db - 1e-12 else b
        else:
            out += a or b
    return out


def closed(t):
    return t[t['outcome'].isin(['TP', 'SL', 'TIME'])] if len(t) else t


def aeu(t):
    return t[t['phase'].isin(['A', 'EU'])] if len(t) else t


def choch_dir(t):
    """'DN' / 'UP' theo tên vùng CHOCH_*."""
    return t['zone'].str.slice(6, 8)


def edge_role(t):
    """Cạnh fade của lệnh L3: 'phía climax' (DN: cạnh dưới, UP: cạnh trên) / 'phía AR'."""
    d = choch_dir(t).to_numpy()
    lo_edge = t['zone'].str.endswith('_LO').to_numpy()
    clim = np.where(d == 'DN', lo_edge, ~lo_edge)
    return np.where(clim, 'phía climax', 'phía AR')


def run_all(D, shapes=None, choch=None, tp_mode='poc', min_width=MIN_W, min_width_new=None, excl=EXCL, d_band='vol', layers=None):
    """Chạy các ô C0..C4 (một cấu hình). Trả dict tên ô → (entries, trades) + 'L' (các lớp)."""
    shapes = shapes if shapes is not None else D.shapes()
    choch = choch if choch is not None else D.choch()
    mwn = min_width if min_width_new is None else min_width_new
    Ls = layers or {k: build_layer(D, k, shapes, choch, d_band) for k in ('L0', 'L1', 'L2', 'L3')}
    out = dict(L=Ls, shapes=shapes, choch=choch)
    E = {}
    for cell, k, mw in (('C0', 'L0', min_width), ('C1', 'L1', min_width), ('C2', 'L2', mwn), ('C3', 'L3', mwn)):
        E[cell] = entries_of(D, Ls[k], tp_mode, mw, excl)
        out[cell] = (E[cell], sim(D, E[cell], shapes))
    e4 = merge(D, E['C2'], E['C3'])
    out['C4'] = (e4, sim(D, e4, shapes))
    return out


# =============================================================================================
# THỐNG KÊ
# =============================================================================================
def rs(t):
    c = closed(t)
    return BV.rstat(c['r'].to_numpy(float) if len(c) else [])


def full_stats(t, days):
    c = closed(t)
    s = rs(t)
    k = K._stats(c) if len(c) else dict(n=0, exp_pts=np.nan, sum_r=0.0, max_loss_streak=0)
    s.update(per_day=s['n'] / max(days, 1), exp=k['exp_pts'], sum_r=k['sum_r'], streak=k['max_loss_streak'])
    return s


def gstats(t):
    c = closed(t)
    out = {}
    for g, col, val in GROUPS:
        m = np.ones(len(c), bool) if (col is None or not len(c)) else (c[col] == val).to_numpy()
        r = c['r'].to_numpy(float)[m] if len(c) else np.zeros(0)
        out[g] = (len(r), float((r > 0).mean()) if len(r) else np.nan, float(r.mean()) if len(r) else np.nan)
    return out


def bands_of(reps, which=2):
    return {g: BV.band([r[g][which] for r in reps]) for g, _, _ in GROUPS}


def cmp_vs(t, bands):
    c = closed(t)
    out, ns = {}, {}
    for g, col, val in GROUPS:
        cc = c if (col is None or not len(c)) else c[c[col] == val]
        s = BV.rstat(cc['r'].to_numpy(float) if len(cc) else [])
        ns[g] = s['n']
        out[g] = (s['m'], s['se'], s['n'], *bands.get(g, (np.nan,) * 3))
    return out, (ns['TRAIN'] >= MIN_N and ns['TEST'] >= MIN_N)


def beats_half(cmp):
    """Vượt đối chứng ở >= 1 nửa: R TB thật > phân vị 95% ở TRAIN hoặc TEST, với n nửa đó >= MIN_N."""
    for g in ('TRAIN', 'TEST'):
        m, se, n, mu, q5, q95 = cmp[g]
        if n >= MIN_N and m == m and q95 == q95 and m > q95:
            return True
    return False


def verdict(cmp, ok):
    return BV.verdict(cmp, ok)


# =============================================================================================
# ĐỐI CHỨNG
# =============================================================================================
SUBSETS = {                                                   # nguồn → (ô, bộ lọc lệnh)
    'C0 A/EU (mốc)': ('C0', lambda t: aeu(t)),
    'D-gate (C1 A/EU)': ('C1', lambda t: aeu(t)),
    'P/b dày (C2 A/EU ngày P/b)': ('C2', lambda t: aeu(t)[aeu(t)['label'].isin(['P', 'b'])] if len(t) else t),
    'CHoCH (C3)': ('C3', lambda t: t),
    'Gộp C4': ('C4', lambda t: t),
}


def dc_a(D, shapes, choch, tp_mode='poc'):
    """ĐC-a: dời band của lớp (mọi pha) + POC theo δ[phiên, bản]; VA_C dời quỹ đạo cạnh rồi chạy lại TREND + detect. 100 bản."""
    res = {k: [] for k in SUBSETS}
    vas = choch['vas']
    for k in range(REPS):
        dl = D.dsh[:, k]
        Ls = {kk: build_layer(D, kk, shapes, None, shift=dl) for kk in ('L0', 'L1', 'L2')}
        chs = D.choch(shift=dl, vas=vas)
        Ls['L3'] = build_layer(D, 'L3', shapes, chs)
        R = run_all(D, shapes, chs, tp_mode=tp_mode, layers=Ls)
        for nm, (cell, flt) in SUBSETS.items():
            t = R[cell][1]
            res[nm].append(gstats(flt(t) if len(t) else t))
    return res


@contextmanager
def patched_map(mp):
    old = dict(K.ZONE_NAME2COL)
    K.ZONE_NAME2COL.update(mp)
    try:
        yield
    finally:
        K.ZONE_NAME2COL.clear()
        K.ZONE_NAME2COL.update(old)


def dc_b(D, L, t, flt, draws=CTRL_DRAWS):
    """ĐC-b: kernel.control_sample — mỗi lệnh thật 1 nến ngẫu nhiên cùng vùng (cột riêng theo tên vùng mới), cùng chế độ của lớp, cùng
    chiều, cùng R:R. Dải theo nhóm của lệnh thật gốc; chỉ các lệnh thuộc bộ lọc flt."""
    c = closed(t)
    if not len(c):
        return {}
    keep = set(closed(flt(c))['idx'].tolist()) if len(c) else set()
    recs = [dict(idx=int(x.idx), side=int(x.side), entry=float(x.entry), sl=float(x.sl), tp=float(x.tp), setup='C', zone=str(x.zone))
            for x in c.itertuples() if int(x.idx) in keep]
    if not recs:
        return {}
    grp = {int(x.idx): (x.split, x.thang) for x in c.itertuples()}
    extra, mp = Z.ctrl_columns(L['zc'], L['names'])
    zcols = pd.concat([L['zc'], extra], axis=1)
    per = {g: [] for g, _, _ in GROUPS}
    with patched_map(mp):
        for sd in range(draws):
            ce = K.control_sample(D.df, zcols, L['mf']['mode'], entries=recs, n_random=1, seed=sd)
            if not ce:
                continue
            cc = closed(K.simulate(D.df, ce, one_at_a_time=False))
            if not len(cc):
                continue
            src = cc['note'].str.extract(r'idx (\d+)')[0].astype(int).map(grp)
            spv = np.array([x[0] for x in src])
            thv = np.array([x[1] for x in src])
            rv = cc['r'].to_numpy(float)
            for g, col, val in GROUPS:
                m = np.ones(len(cc), bool) if col is None else (spv == val if col == 'split' else thv == val)
                per[g].append(rv[m].mean() if m.any() else np.nan)
    return {g: BV.band(v) for g, v in per.items()}


def dc_perm(D, t_c0, shapes, reps=PERM, seed=SEED):
    """ĐC-c cổng hình dạng: hoán vị nhãn giữa các phiên sạch có nhãn; thống kê = WR và R TB của lệnh C0 pha A/EU ở 'ngày D'."""
    c = closed(aeu(t_c0))
    snos = [s for s in D.clean_snos if shapes.get(s)]
    labs = np.array([shapes[s]['label'] for s in snos], dtype=object)
    pos = {s: k for k, s in enumerate(snos)}
    tk = np.array([pos.get(int(s), -1) for s in c['sno']])
    ok = tk >= 0
    r = c['r'].to_numpy(float)[ok]
    tk = tk[ok]

    def stat(lv):
        m = lv[tk] == 'D'
        return (float(r[m].mean()) if m.any() else np.nan, float((r[m] > 0).mean()) if m.any() else np.nan, int(m.sum()),
                float(r[~m].mean()) if (~m).any() else np.nan)
    real = stat(labs)
    rng = np.random.default_rng(seed)
    pr, pw = [], []
    for _ in range(reps):
        s = stat(rng.permutation(labs))
        pr.append(s[0])
        pw.append(s[1])
    pr, pw = np.array(pr), np.array(pw)
    return dict(real_r=real[0], real_wr=real[1], n_d=real[2], real_r_other=real[3], n_tot=len(r),
                p_r=float(np.nanmean(pr >= real[0] - 1e-12)), p_wr=float(np.nanmean(pw >= real[1] - 1e-12)),
                perm_r=BV.band(pr), perm_wr=BV.band(pw))


def dc_fake(D, shapes, choch, tp_mode='poc', reps=FAKE_REPS):
    """ĐC-c VA_C: 'VA giả' cùng chiều cao / quỹ đạo / tuổi thọ / phiên, dời thời gian sinh ngẫu nhiên (hạt SEED + bản)."""
    out = []
    for k in range(reps):
        fv = Z.time_shifted_vas(D.df, choch['vas'], np.random.default_rng(SEED + k))
        ch = D.choch(vas=fv)
        L3 = build_layer(D, 'L3', shapes, ch)
        t = sim(D, entries_of(D, L3, tp_mode), shapes)
        out.append(gstats(t))
    return out


def dc_dist(D, t, draws=DIST_DRAWS, seed=SEED):
    """ĐC-c khớp khoảng cách: mỗi lệnh thật → nến ngẫu nhiên CÙNG PHIÊN + CÙNG PHA (không splice/thin, khác nến thật), cùng chiều,
    vào ở close, SL / TP cách entry ĐÚNG bằng khoảng của lệnh thật. Dải R TB theo nhóm của lệnh thật."""
    c = closed(t)
    if not len(c):
        return {}
    df = D.df
    cl = df['close'].to_numpy(float)
    okbar = (~df['splice'].to_numpy()) & (~df['thin'].to_numpy())
    ph = df['phase'].to_numpy()
    rng = np.random.default_rng(seed)
    pools = {}
    per = {g: [] for g, _, _ in GROUPS}
    recs = list(c.itertuples())
    for _ in range(draws):
        ents, meta = [], []
        for x in recs:
            key = (int(x.sno), x.phase)
            if key not in pools:
                pools[key] = np.flatnonzero((D.sno == key[0]) & (ph == key[1]) & okbar)
            pool = pools[key]
            pool = pool[pool != int(x.idx)]
            if not len(pool):
                continue
            i = int(rng.choice(pool))
            s = int(x.side)
            dsl, dtp = abs(x.entry - x.sl), abs(x.tp - x.entry)
            ents.append(dict(idx=i, side=s, entry=cl[i], sl=cl[i] - s * dsl, tp=cl[i] + s * dtp, setup='DIST', zone=x.zone))
            meta.append((x.split, x.thang))
        if not ents:
            continue
        order = np.argsort([e['idx'] for e in ents], kind='stable')
        tt = K.simulate(df, ents, one_at_a_time=False)
        if not len(tt):
            continue
        mt = [meta[j] for j in order]
        oc = tt['outcome'].isin(['TP', 'SL', 'TIME']).to_numpy()
        rv = tt['r'].to_numpy(float)[oc]
        spv = np.array([m[0] for m in mt])[oc]
        thv = np.array([m[1] for m in mt])[oc]
        for g, col, val in GROUPS:
            m = np.ones(len(rv), bool) if col is None else (spv == val if col == 'split' else thv == val)
            per[g].append(rv[m].mean() if m.any() else np.nan)
    return {g: BV.band(v) for g, v in per.items()}


# =============================================================================================
# ẢNH
# =============================================================================================
def _plt():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt


def plot_shape(D, s, d, path):
    plt = _plt()
    q = d['q']
    prof = Z.tpo_profile(D.df, q)
    rows, cnt = prof[0], prof[1]
    pr = K.Profiles.row_price(rows)
    fig, ax = plt.subplots(figsize=(6, 9))
    ax.barh(pr, cnt, height=0.18, color='#8c959f')
    ax.axhspan(d['t_lo'], d['t_hi'], color='orange', alpha=.25, label='vùng dày T')
    for v, nm, col in ((d['vah'], 'VAH_T', 'b'), (d['val'], 'VAL_T', 'b'), (d['poc'], 'POC_T', 'r'), (d['close'], 'close', 'k')):
        ax.axhline(v, color=col, lw=1, ls='--' if nm == 'close' else '-')
        ax.text(cnt.max() * 1.01, v, nm, fontsize=7, va='center')
    ax.set_title('%s · phiên %s (dùng cho %s)\nasym %+.2f · bulge %.2f' % (d['label'], D.st['session_id'].loc[q], D.st['session_id'].loc[s],
                                                                           d['asym'], d['bulge']), fontsize=9)
    ax.set_xlabel('số TPO (bracket 30\')')
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


def plot_va(D, v, log, trades, path):
    plt = _plt()
    df = D.df
    a = max(int(D.st['start_pos'].loc[v.sno]), v.climax - 40)
    b = min(len(df), max(log['end'], v.birth) + 25, v.climax + 360)
    seg = df.iloc[a:b]
    fig, ax = plt.subplots(figsize=(15, 6.5))
    xs = np.arange(len(seg))
    o, h, l, c = (seg[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
    col = np.where(c >= o, '#1a7f37', '#cf222e')
    ax.vlines(xs, l, h, color=col, lw=0.8)
    ax.bar(xs, np.maximum(np.abs(c - o), 0.05), bottom=np.minimum(o, c), color=col, width=0.6)
    for k, (s, lo_, hi_) in enumerate(v.segs):
        e = v.segs[k + 1][0] if k + 1 < len(v.segs) else log['end']
        if e <= s:
            continue
        ax.add_patch(plt.Rectangle((s - a, lo_), e - s, hi_ - lo_, color='orange', alpha=.18))
    ax.axvline(v.climax - a, color='purple', lw=1, ls=':')
    ax.text(v.climax - a, (l.min()), ' climax', color='purple', fontsize=8)
    ax.axvline(v.birth - a, color='b', lw=1, ls=':')
    ax.text(v.birth - a, h.max(), ' sinh VA_C', color='b', fontsize=8, va='top')
    for nm, y in (('L1', v.L1), ('H1', v.H1), ('L2', v.L2)):
        ax.axhline(y, color='gray', lw=0.6, ls='--')
        ax.text(0, y, nm, fontsize=7, color='gray')
    if len(trades):
        for x in trades.itertuples():
            if a <= x.idx < b:
                ax.scatter([x.idx - a], [x.entry], marker='^' if x.side > 0 else 'v', s=60, color='b', zorder=5)
                ax.text(x.idx - a, x.entry, ' %s %+.1fR' % (x.outcome, x.r), fontsize=7)
    ticks = list(range(0, len(seg), 15))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(seg['t_vn'].iloc[t])[5:16] for t in ticks], rotation=60, fontsize=6)
    ax.set_title('VA_C #%d %s · phiên %s · climax %s VN (VSA %.1f) · VA [%.1f ; %.1f] cao %.1f · nới %d · chết: %s · %d lệnh' % (
        v.id, v.dir, log['session'], log['t_climax'], log['vsa'], log['lo0'], log['hi0'], log['height0'], log['n_ext'], log['why'],
        log.get('n_trades', 0)), fontsize=9)
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


# =============================================================================================
# ĐỊNH DẠNG
# =============================================================================================
def f(x, p=2):
    return ('%.*f' % (p, x)).replace('.', ',') if x == x else '–'


def fs(x, p=2):
    return (('%+.*f' % (p, x)).replace('.', ',').replace('-', '−')) if x == x else '–'


def pct(x, p=1):
    return (f(100 * x, p) + ' %') if x == x else '–'


def row_full(label, s):
    return '| %s | %d | %s | %s | %s [%s ; %s] | %s | %s | %d |' % (label, s['n'], f(s['per_day']), pct(s['wr']), fs(s['m']), fs(s['lo']),
                                                                   fs(s['hi']), fs(s['exp']), fs(s['sum_r'], 1), s['streak'])


HDR_FULL = ('| ô | n | lệnh/ngày | WR | R TB [KTC 95%] | kỳ vọng giá/lệnh | tổng R | chuỗi thua |\n'
            '|---|---|---|---|---|---|---|---|')


def nwr(s):
    return '%d · %s · %s' % (s['n'], pct(s['wr']), fs(s['m']))


def split_cells(t):
    c = closed(t)
    out = {}
    for k in ('TRAIN', 'TEST'):
        out[k] = BV.rstat(c[c['split'] == k]['r'].to_numpy(float) if len(c) else [])
    return out


def band_txt(b):
    return '%s [%s ; %s]' % (fs(b[0]), fs(b[1]), fs(b[2])) if b and b[0] == b[0] else '–'


def prereg_hash():
    try:
        r = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%h', '--', 'research/zones_c_v6.py'], cwd=os.path.dirname(HERE),
                           capture_output=True, text=True, timeout=10)
        h = r.stdout.strip().splitlines()
        return h[-1] if h else '(chưa commit)'
    except Exception:
        return '(không đọc được git)'


# =============================================================================================
# MAIN
# =============================================================================================
QS = [
    'Q1 — L1/L2 ngày D dùng VA **volume** hôm qua (yd_vah/yd_val, đúng C0) để Δ(C1−C0) chỉ là tác dụng của CỔNG. Bảng 2.1 ghi "VA_Y (VAH_T/VAL_T)" '
    '⇒ bản dùng VA TPO (VAH_T/VAL_T/POC_T) chạy như một dòng độ nhạy.',
    'Q2 — L2: ngày D giữ POC hôm qua (như L1); ngày P/b dùng POC_T (nằm trong T).',
    'Q3 — "Hai đỉnh" = có ít nhất một CẶP đỉnh `find_hvn` (mặc định 1,5×TB, làm mượt ±5 hàng) mà giữa chúng có một đáy `find_lvn` (≤ 0,5×TB).',
    'Q4 — Đang chờ ST mà có pivot H CAO HƠN H1 ⇒ H1 := pivot đó (AR mở rộng), đếm 400 nến lại từ đó. Plan không nói; bỏ qua thì '
    'mọi ca "hồi cạn rồi lên tiếp" bị kẹt ở H1 thấp.',
    'Q5 — Cụm climax tính từ nến climax ĐẦU TIÊN (mốc): dời climax khi trong 8 nến sau mốc có đáy thấp hơn thoả lại bước 1+2. L1 = pivot L '
    'zigzag có giá = đáy cụm và nằm trong 8 nến sau mốc; đáy mới thấp hơn cụm SAU cửa sổ (trước khi có L1) ⇒ hỏng, về NGỦ.',
    'Q6 — Chờ AR: pivot H chưa đủ lớn ⇒ vẫn chờ pivot H tiếp theo (L1 giữ nguyên) tới khi thủng L1 − 1,0·u hoặc quá 300 nến từ climax.',
    'Q7 — Chân move = pivot H zigzag gần nhất đã xác nhận tới nến c (gồm xác nhận ngay tại c), cùng phiên; chưa có ⇒ high lớn nhất 240 '
    'nến trong phiên. Độ dài move GỒM nến climax (đúng câu chữ plan "high(chân) − low(c)"; khác `_find_move` v6 loại nến climax).',
    'Q8 — "TB range 20 nến" = 20 nến TRƯỚC c (không gồm c, như `_avg_range`); vma gồm c, cần đủ 20 nến.',
    'Q9 — VA_C cao < 6 lúc sinh ⇒ KHÔNG sinh (ghi "hẹp"), máy về NGỦ tìm climax mới.',
    'Q10 — Độ nhạy "không nới": pivot vượt cạnh ≤ 0,25·h ⇒ giữ nguyên cạnh; vượt > 0,25·h vẫn CHẾT.',
    'Q11 — DN và UP cùng sống ⇒ dùng VA sinh SAU kể cả khi không chồng nhau (detect chỉ nhận một band); VA cũ hiện lại khi VA mới chết.',
    'Q12 — TREND chỉ giết VA khi chế độ được tính trên CHÍNH VA đang hiện (nến M5 đóng gần nhất thuộc cùng VA). Lặp theo thứ tự thời gian.',
    'Q13 — L1/L2 chạy lại `mode_frame` trên band của lớp ⇒ ngày bị cổng chặn (A/EU = trống) làm bộ đếm M5-ngoài-band reset khi sang pha Mỹ ⇒ '
    'vài lệnh US có thể khác C0. Báo riêng số lệnh US mỗi ô.',
    'Q14 — ĐC-a: dời CẢ band của lớp (mọi pha) và POC theo δ[phiên]; VA_C dời quỹ đạo cạnh của máy giá rồi chạy lại TREND + detect '
    '(không chạy lại máy pivot — "vị trí" là thứ bị kiểm).',
    'Q15 — VA giả: thời điểm sinh rút đều trong phiên, giữ quỹ đạo cạnh + tuổi thọ, dời giá sao cho close tại nến sinh giả ở đúng vị trí '
    'tương đối như thật; cắt ở cuối phiên.',
    'Q16 — ĐC khớp khoảng cách: nến ngẫu nhiên cùng phiên + cùng pha, cùng chiều, khoảng SL và TP (giá) đúng bằng lệnh thật, 200 lần.',
    'Q17 — Gộp C4: cùng nến L2 và L3 cùng bắn ⇒ lớp có cạnh gần close hơn, hoà ⇒ L3; xong `simulate(one_at_a_time=True)`.',
    'Q18 — Hoán vị nhãn: chỉ lệnh C0 pha A/EU (cổng chỉ tác động A/EU), hoán vị giữa các phiên sạch có nhãn; p một phía (thật ≥).',
    'Q19 — T1 "vượt ĐC-b hoặc ĐC-c ở ≥ 1 nửa" = R TB thật > phân vị 95% đối chứng ở TRAIN hoặc TEST, với n nửa đó ≥ 10.',
    'Q20 — Bản chính zigzag 2,0 giá (kernel) — với biên độ M1 hiện tại (u ≈ 1,5) zigzag này rất dày: không mở thêm tham số (R5).',
]


def main():
    t0 = time.time()
    os.makedirs(IMG, exist_ok=True)
    D = Data()
    shapes = D.shapes()
    ch = D.choch()
    print('chuẩn bị %.1fs' % (time.time() - t0), flush=True)
    L = []
    w = L.append
    w('# RESULTS C-v6 — cổng hình dạng D/P/b + VA nhỏ CHoCH (sinh bởi `setup_c_v6.py`, tất định)')
    w('')
    w('Plan: `research/PLAN-C-v2.md`. Dữ liệu DUY NHẤT: `%s` (người dùng chốt; không chạy file 2 năm). %d phiên sạch (TRAIN %d ≤ 2026-09-15, '
      'TEST %d từ 2026-09-16). Giờ trong dữ liệu = UTC, VN = UTC+7. Chi phí 0,2 giá/lệnh, 1 lệnh mở cùng lúc. Hằng số đăng ký trước ở commit '
      '**%s** (commit thêm `zones_c_v6.py` + `setup_c_v6.py` + test, TRƯỚC lần chạy kết quả đầu tiên).'
      % (os.path.basename(D90), D.days, D.days_split['TRAIN'], D.days_split['TEST'], prereg_hash()))
    w('')
    w('Thuật ngữ: buy / sell / limit / market giữ tiếng Anh. "Đổi hành vi" = CHoCH. "Nến cao trào" = climax. AR = nhịp bật tự động. '
      'ST = nhịp thử lại. KTC = khoảng tin cậy 95%% lấy mẫu lại theo lệnh (10.000 lần, hạt 0). Ô chính: TP = gần nhất trong {cạnh đối diện, POC} '
      'và ≥ 2R (L3: chỉ cạnh đối diện).')
    w('')
    # ---------------------------------------------------------------- công suất
    w('## 1. Công suất thống kê (in TRƯỚC bảng chính)')
    w('')
    w('σ_R ≈ %s (đo ở A-v4). Hiệu R TB nhỏ nhất phát hiện được (80%% công suất, mức 5%%, hai phía) = 2,8·σ/√n:' % f(SIGMA_R, 1))
    w('')
    w('| n | 20 | 30 | 60 | 100 | 150 |\n|---|---|---|---|---|---|')
    w('| hiệu tối thiểu (R) | ' + ' | '.join(f(2.8 * SIGMA_R / math.sqrt(k)) for k in (20, 30, 60, 100, 150)) + ' |')
    w('')
    w('**Kết luận trước:** với %d phiên, phần 1 (A/EU còn vài chục lệnh sau cổng) **gần như không thể chứng minh** — chỉ nói được "không tệ hơn" '
      'và "hướng đúng / sai". Mọi chữ "tốt hơn" dưới đây là HƯỚNG, không phải kiểm định, trừ khi ghi rõ vượt đối chứng.' % D.days)
    w('')
    # ---------------------------------------------------------------- nhãn hình dạng
    w('## 2. Đếm nhãn hình dạng profile TPO hôm qua (in TRƯỚC lệnh)')
    w('')
    lab_clean = [shapes[s]['label'] if shapes.get(s) else 'không có hôm qua' for s in D.clean_snos]
    w('| nhãn | số phiên (trong %d phiên sạch) | TRAIN | TEST | vùng fade A/EU |' % D.days)
    w('|---|---|---|---|---|')
    spl = {s: D.st['split'].loc[s] for s in D.clean_snos}
    fade = {'D': 'VA hôm qua (như C0)', 'P': 'T (cạnh phần dày)', 'b': 'T', 'KHÁC-B': 'không fade', 'KHÁC-thin': 'không fade',
            'KHÁC-close': 'không fade', 'không có hôm qua': 'không fade'}
    for lab in Z.LABELS + ('không có hôm qua',):
        ss = [s for s, lb in zip(D.clean_snos, lab_clean) if lb == lab]
        w('| %s | %d | %d | %d | %s |' % (lab, len(ss), sum(spl[s] == 'TRAIN' for s in ss), sum(spl[s] == 'TEST' for s in ss), fade[lab]))
    w('')
    tw = [shapes[s]['t_hi'] - shapes[s]['t_lo'] for s in D.clean_snos if shapes.get(s) and shapes[s]['label'] in ('P', 'b')]
    if tw:
        w('Bề rộng vùng dày T ở ngày P/b: trung vị %s giá, nhỏ nhất %s, lớn nhất %s; số ngày P/b có T < 6 giá (bị chặn bởi rộng tối thiểu): **%d / %d**.'
          % (f(float(np.median(tw)), 1), f(min(tw), 1), f(max(tw), 1), sum(x < 6 - 1e-9 for x in tw), len(tw)))
        w('')
    imgs = []
    for lab in Z.LABELS:
        ss = [s for s in D.clean_snos if shapes.get(s) and shapes[s]['label'] == lab]
        if ss:
            fn = 'c_v6_shape_%s.png' % lab.replace('KHÁC-', 'KHAC_')
            plot_shape(D, ss[0], shapes[ss[0]], os.path.join(IMG, fn))
            imgs.append('[%s](img/%s)' % (lab, fn))
    w('Ảnh profile TPO (phiên đầu tiên mỗi nhãn): ' + ' · '.join(imgs) + '. Danh sách nhãn từng phiên ở **Phụ lục A** (người học gắn nhãn 15 phiên '
      'bằng mắt TRƯỚC khi mở phụ lục).')
    w('')
    # ---------------------------------------------------------------- nhật ký VA_C
    log = ch['log']
    w('## 3. Nhật ký VA_C (in TRƯỚC lệnh)')
    w('')
    fu = ch['funnel']
    w('Phễu máy trạng thái (đếm số lần qua từng bước):')
    w('')
    w('| chiều | ứng viên climax | L1 (đổi hành vi #1) | AR đủ lớn (#2) | AR quá nhỏ (bỏ qua) | ST đạt 55% (#3) | ST thủng sâu (hỏng) | VA sinh (cao ≥ 6) | hẹp < 6 (không sinh) |')
    w('|---|---|---|---|---|---|---|---|---|')
    for d in ('DN', 'UP'):
        x = fu[d]
        w('| %s | %d | %d | %d | %d | %d | %d | %d | %d |' % (d, x['climax'], x['L1'], x['AR'], x['AR_nho'], x['ST'], x['ST_thung'], x['sinh'], x['hep']))
    w('')
    lg = pd.DataFrame(log)
    if len(lg):
        lg['split'] = ['TRAIN' if str(s)[:10] <= K.CONST['split_train_end'] else 'TEST' for s in lg['session']]
        clean_set = set(D.st['session_id'].loc[D.clean_snos])
        lg['clean'] = lg['session'].isin(clean_set)
        w('VA_C sinh: **%d** (phiên sạch %d; TRAIN %d / TEST %d). Theo pha lúc sinh: %s. Chiều cao lúc sinh: trung vị %s giá (p10 %s, p90 %s). '
          'Tuổi thọ (nến): trung vị %d. Lý do chết: %s. Số lần nới: %s.' % (
              len(lg), int(lg['clean'].sum()), int((lg['split'] == 'TRAIN').sum()), int((lg['split'] == 'TEST').sum()),
              ', '.join('%s %d' % (p, int((lg['phase'] == p).sum())) for p in ('A', 'EU', 'US', 'OFF')),
              f(lg['height0'].median(), 1), f(lg['height0'].quantile(.1), 1), f(lg['height0'].quantile(.9), 1), int(lg['life'].median()),
              ', '.join('%s %d' % (k, v) for k, v in lg['why'].value_counts().items()),
              ', '.join('%d lần: %d' % (k, v) for k, v in lg['n_ext'].value_counts().sort_index().items())))
    else:
        w('VA_C sinh: **0**.')
    w('')
    # ---------------------------------------------------------------- ô chính
    R = {tm: run_all(D, shapes, ch, tp_mode=tm) for tm in ('poc', 'fixed2')}
    t3 = R['poc']['C3'][1]
    if len(lg):
        idmap = {}
        if len(t3):
            fr = ch['frame']
            for x in closed(t3).itertuples():
                vid = int(fr['choch_id'].to_numpy()[x.poke_idx])
                idmap[vid] = idmap.get(vid, 0) + 1
        lg['n_trades'] = [idmap.get(int(i), 0) for i in lg['id']]
        for x, rec in zip(ch['log'], lg.to_dict('records')):
            x['n_trades'] = rec['n_trades']
        w('VA_C có ≥ 1 lệnh (TP chính): %d / %d.' % (int((lg['n_trades'] > 0).sum()), len(lg)))
        w('')
        imgs = []
        for sp in ('TRAIN', 'TEST'):
            sub = lg[(lg['split'] == sp) & lg['clean']].head(5)
            for rec in sub.to_dict('records'):
                v = next(vv for vv in ch['vas'] if vv.id == rec['id'])
                fn = 'c_v6_vac_%s_%03d_%s.png' % (sp, rec['id'], rec['t_birth'][:10])
                plot_va(D, v, rec, closed(t3), os.path.join(IMG, fn))
                imgs.append('[%s #%d %s](img/%s)' % (sp, rec['id'], rec['t_birth'][5:16], fn))
        w('Ảnh 5 VA_C đầu tiên TRAIN + 5 TEST (phiên sạch): ' + ' · '.join(imgs) + '. Nhật ký đầy đủ ở **Phụ lục B** (người học tìm 5 ca trên '
          'Optimus Flow TRƯỚC khi mở).')
        w('')
    # ---------------------------------------------------------------- bảng chính
    w('## 4. Bảng chính (ô 3.1)')
    w('')
    names = {'C0': 'C0 = tái tạo vòng 1', 'C1': 'C1 = cổng D (A/EU) + US cũ', 'C2': 'C2 = D + P/b dày + US cũ', 'C3': 'C3 = CHoCH riêng',
             'C4': 'C4 = C2 ∪ C3 (gộp)'}
    for tm, lab in (('poc', 'TP chính: cạnh/POC ≥ 2R (L3: cạnh đối diện ≥ 2R)'), ('fixed2', 'TP cố định 2R')):
        w('### %s' % lab)
        w('')
        w(HDR_FULL)
        for cell in ('C0', 'C1', 'C2', 'C3', 'C4'):
            w(row_full(names[cell], full_stats(R[tm][cell][1], D.days)))
        w('')
        w('| ô | TRAIN n · WR · R TB | TEST n · WR · R TB | A | EU | US | T8 | T9 | T10 |')
        w('|---|---|---|---|---|---|---|---|---|')
        for cell in ('C0', 'C1', 'C2', 'C3', 'C4'):
            t = closed(R[tm][cell][1])
            sp = split_cells(t)
            ph = [BV.rstat(t[t['phase'] == p]['r'].to_numpy(float) if len(t) else []) for p in ('A', 'EU', 'US')]
            th = [BV.rstat(t[t['thang'] == m]['r'].to_numpy(float) if len(t) else []) for m in ('T8', 'T9', 'T10')]
            w('| %s | %s | %s | %s |' % (cell, nwr(sp['TRAIN']), nwr(sp['TEST']), ' | '.join(nwr(x) for x in ph + th)))
        w('')
    if not (len(closed(R['poc']['C0'][1])) == EXPECT_C0['poc'][0] and len(closed(R['fixed2']['C0'][1])) == EXPECT_C0['fixed2'][0]):
        w('**CẢNH BÁO: C0 không tái tạo đúng vòng 1.**')
        w('')
    # ---------------------------------------------------------------- tách đóng góp
    w('## 5. Tách đóng góp (TP chính)')
    w('')
    S = {c: full_stats(R['poc'][c][1], D.days) for c in ('C0', 'C1', 'C2', 'C3', 'C4')}
    w('| phần | Δ n | Δ tổng R | ghi chú |\n|---|---|---|---|')
    w('| Δ(C1 − C0) = cổng D | %+d | %s | lệnh A/EU C0 %d → C1 %d; US C0 %d → C1 %d (Q13) |' % (
        S['C1']['n'] - S['C0']['n'], fs(S['C1']['sum_r'] - S['C0']['sum_r'], 1), len(aeu(closed(R['poc']['C0'][1]))),
        len(aeu(closed(R['poc']['C1'][1]))), int((closed(R['poc']['C0'][1])['phase'] == 'US').sum()),
        int((closed(R['poc']['C1'][1])['phase'] == 'US').sum())))
    t2 = closed(R['poc']['C2'][1])
    w('| Δ(C2 − C1) = vùng dày P/b | %+d | %s | lệnh ngày P/b trong C2: %d |' % (
        S['C2']['n'] - S['C1']['n'], fs(S['C2']['sum_r'] - S['C1']['sum_r'], 1), int((aeu(t2)['label'].isin(['P', 'b'])).sum()) if len(t2) else 0))
    w('| C3 = CHoCH | %+d | %s | |' % (S['C3']['n'], fs(S['C3']['sum_r'], 1)))
    w('| Δ(C4 − C2 − C3) = tương tác (trùng nến / 1 lệnh mở) | %+d | %s | |' % (
        S['C4']['n'] - S['C2']['n'] - S['C3']['n'], fs(S['C4']['sum_r'] - S['C2']['sum_r'] - S['C3']['sum_r'], 1)))
    w('')
    # ---------------------------------------------------------------- C0-nhãn + hoán vị
    w('## 6. C0 tách theo nhãn hình dạng của ngày (kiểm cổng KHÔNG cần lệnh mới)')
    w('')
    t0c = closed(R['poc']['C0'][1])
    w('| nhãn | A/EU n · WR · R TB [KTC] | US n · WR · R TB |\n|---|---|---|')
    for lab in Z.LABELS + ('',):
        a_ = aeu(t0c)
        a_ = a_[a_['label'] == lab] if len(a_) else a_
        u_ = t0c[(t0c['phase'] == 'US') & (t0c['label'] == lab)] if len(t0c) else t0c
        sa = BV.rstat(a_['r'].to_numpy(float) if len(a_) else [])
        su = BV.rstat(u_['r'].to_numpy(float) if len(u_) else [])
        w('| %s | %s [%s ; %s] | %s |' % (lab or '(không có hôm qua)', nwr(sa), fs(sa['lo']), fs(sa['hi']), nwr(su)))
    w('')
    pm = dc_perm(D, R['poc']['C0'][1], shapes)
    w('**Hoán vị nhãn (ĐC-c cổng, %d lần, hạt %d):** lệnh C0 A/EU ngày D: n %d, R TB %s, WR %s (ngày khác: R TB %s, tổng %d lệnh). '
      'Phân phối hoán vị R TB(D) %s; WR(D) %s. **p(R TB) = %s, p(WR) = %s** (một phía, thật ≥).'
      % (PERM, SEED, pm['n_d'], fs(pm['real_r']), pct(pm['real_wr']), fs(pm['real_r_other']), pm['n_tot'], band_txt(pm['perm_r']),
         '%s [%s ; %s]' % (pct(pm['perm_wr'][0]), pct(pm['perm_wr'][1]), pct(pm['perm_wr'][2])), f(pm['p_r'], 3), f(pm['p_wr'], 3)))
    w('')
    # ---------------------------------------------------------------- C3 tách
    w('## 7. C3 tách: chiều gốc × cạnh fade × pha (TP chính)')
    w('')
    c3 = closed(R['poc']['C3'][1])
    if len(c3):
        c3 = c3.assign(dir=choch_dir(c3).to_numpy(), role=edge_role(c3))
        w('| chiều gốc | cạnh | tổng | A | EU | US |\n|---|---|---|---|---|---|')
        for d in ('DN', 'UP'):
            for ro in ('phía climax', 'phía AR'):
                x = c3[(c3['dir'] == d) & (c3['role'] == ro)]
                w('| %s | %s | %s | %s |' % (d, ro, nwr(BV.rstat(x['r'].to_numpy(float))),
                                             ' | '.join(nwr(BV.rstat(x[x['phase'] == p]['r'].to_numpy(float))) for p in ('A', 'EU', 'US'))))
    else:
        w('C3 có **0** lệnh.')
    w('')
    print('ô chính xong %.0fs' % (time.time() - t0), flush=True)
    # ---------------------------------------------------------------- đối chứng
    w('## 8. Đối chứng (TP chính)')
    w('')
    w('Ngưỡng "khác đối chứng" (PLAN-LAN-CHAM mục 5, `benzo_vcl.verdict`): ngoài dải 5–95%% ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ≥ 2/3 tháng, '
      '|hiệu| > 2 sai số; chỉ áp khi ≥ %d lệnh mỗi nửa. Ô: R TB thật vs TB đối chứng [5%% ; 95%%].' % MIN_N)
    w('')
    A = dc_a(D, shapes, ch)
    print('ĐC-a xong %.0fs' % (time.time() - t0), flush=True)
    Lp = R['poc']['L']
    lay_of = {'C0': 'L0', 'C1': 'L1', 'C2': 'L2', 'C3': 'L3'}
    VER = {}
    w('| nguồn | ĐC | TRAIN thật · đối chứng | TEST thật · đối chứng | phán quyết |\n|---|---|---|---|---|')

    def line(src, kind, tsel, bands):
        cmp, ok = cmp_vs(tsel, bands)
        v = verdict(cmp, ok)
        VER[(src, kind)] = (v, cmp, beats_half(cmp))
        w('| %s | %s | %s · %s | %s · %s | %s |' % (src, kind, fs(cmp['TRAIN'][0]) + ' (n %d)' % cmp['TRAIN'][2], band_txt(cmp['TRAIN'][3:]),
                                                   fs(cmp['TEST'][0]) + ' (n %d)' % cmp['TEST'][2], band_txt(cmp['TEST'][3:]), v))

    for src, (cell, flt) in SUBSETS.items():
        tt = R['poc'][cell][1]
        tsel = flt(tt) if len(tt) else tt
        line(src, 'ĐC-a dời vùng (%d bản)' % REPS, tsel, bands_of(A[src]))
        if cell in lay_of:
            line(src, 'ĐC-b vào ngẫu nhiên tại vùng (%d)' % CTRL_DRAWS, tsel, dc_b(D, Lp[lay_of[cell]], tt, flt))
    print('ĐC-b xong %.0fs' % (time.time() - t0), flush=True)
    FK = dc_fake(D, shapes, ch)
    line('CHoCH (C3)', 'ĐC-c VA giả (%d bản)' % FAKE_REPS, R['poc']['C3'][1], bands_of(FK))
    line('CHoCH (C3)', 'ĐC-c khớp khoảng cách (%d)' % DIST_DRAWS, R['poc']['C3'][1], dc_dist(D, R['poc']['C3'][1]))
    print('ĐC-c xong %.0fs' % (time.time() - t0), flush=True)
    w('')
    w('Hoán vị nhãn cho cổng D: p(R TB) = %s, p(WR) = %s (mục 6).' % (f(pm['p_r'], 3), f(pm['p_wr'], 3)))
    w('')
    # ---------------------------------------------------------------- độ nhạy
    w('## 9. Lưới độ nhạy (khai báo trước, in ĐỦ, không chọn ô)')
    w('')
    w('Mỗi dòng đổi MỘT thứ so với bản chính. Ô: n · WR · R TB (tổng) | R TB TRAIN | R TB TEST.')
    w('')
    w('| biến thể | C1 | C2 | C3 | C4 |\n|---|---|---|---|---|')

    def vrow(name, RR):
        w('| %s | %s |' % (name, ' | '.join('%s; TR %s / TE %s' % (nwr(rs(RR[c][1])), fs(split_cells(RR[c][1])['TRAIN']['m']),
                                                                  fs(split_cells(RR[c][1])['TEST']['m'])) for c in ('C1', 'C2', 'C3', 'C4'))))

    vrow('**bản chính**', R['poc'])
    for nm, kw in (('S1 profile volume thay TPO', dict(source='vol')), ('R1 profile chỉ cửa sổ Mỹ', dict(source='tpo_us')),
                   ('vùng dày frac 0,4', dict(frac=0.4)), ('vùng dày frac 0,6', dict(frac=0.6)),
                   ('asym 0,20', dict(asym_thr=0.20)), ('asym 0,30', dict(asym_thr=0.30)),
                   ('bulge 0,15', dict(bulge_thr=0.15)), ('bulge 0,25', dict(bulge_thr=0.25))):
        vrow(nm, run_all(D, D.shapes(**kw), ch))
    vrow('ngày D dùng VA TPO (Q1)', run_all(D, shapes, ch, d_band='tpo'))
    vrow('rộng tối thiểu 4 cho L2/L3 (VA_C sinh khi cao ≥ 4)', run_all(D, shapes, D.choch(dict(min_h=4.0)), min_width_new=4.0))
    for nm, prm in (('VSA climax 1,8', dict(vsa=1.8)), ('bỏ điều kiện "bị chặn"', dict(block=False)), ('nới 0,15', dict(ext_frac=0.15)),
                    ('không nới (Q10)', dict(extend=False)), ('240 nến không chạm cạnh ⇒ chết', dict(no_touch=240))):
        vrow(nm, run_all(D, shapes, D.choch(prm)))
    vrow('chặn thêm 19:20–20:30 VN (luật C# InVirtualOpen)', run_all(D, shapes, ch, excl=EXCL_VO))
    w('')
    w('TP cố định 2R của bản chính: xem bảng mục 4 (TP cố định).')
    w('')
    print('độ nhạy xong %.0fs' % (time.time() - t0), flush=True)
    # ---------------------------------------------------------------- tiêu chí
    w('## 10. Tiêu chí khai báo trước (mục 3.4)')
    w('')
    s0, s4, s3 = S['C0'], S['C4'], S['C3']
    sp0, sp4, sp3 = split_cells(R['poc']['C0'][1]), split_cells(R['poc']['C4'][1]), split_cells(R['poc']['C3'][1])
    worse = [k for k, v in VER.items() if '▼' in v[0]]
    c_n = s4['n'] >= 1.3 * s0['n']
    c_r = all(sp4[k]['m'] == sp4[k]['m'] and sp4[k]['m'] >= sp0[k]['m'] for k in ('TRAIN', 'TEST'))
    c_w = s4['wr'] == s4['wr'] and s4['wr'] >= s0['wr'] - 0.03
    T0 = c_n and c_r and c_w and not worse
    w('**T0** — n(C4) ≥ 1,3·n(C0): %d vs %s → %s · R TB C4 ≥ C0 ở TRAIN (%s vs %s) và TEST (%s vs %s) → %s · WR C4 ≥ WR C0 − 3 điểm (%s vs %s) → %s · '
      'không đối chứng nào "kém hơn thật" → %s. ⇒ **T0 %s**.' % (
          s4['n'], f(1.3 * s0['n'], 1), 'đạt' if c_n else 'KHÔNG', fs(sp4['TRAIN']['m']), fs(sp0['TRAIN']['m']), fs(sp4['TEST']['m']),
          fs(sp0['TEST']['m']), 'đạt' if c_r else 'KHÔNG', pct(s4['wr']), pct(s0['wr']), 'đạt' if c_w else 'KHÔNG',
          'đạt' if not worse else 'KHÔNG (%s)' % '; '.join('%s / %s' % k for k in worse), 'ĐẠT' if T0 else 'KHÔNG ĐẠT'))
    w('')
    c3a = sp3['TRAIN']['m'] == sp3['TRAIN']['m'] and sp3['TRAIN']['m'] >= -0.10
    c3b = sp3['TEST']['m'] == sp3['TEST']['m'] and sp3['TEST']['m'] >= 0
    c3n = sp3['TEST']['n'] >= 15
    beat = [k for k, v in VER.items() if k[0] == 'CHoCH (C3)' and ('ĐC-b' in k[1] or 'ĐC-c' in k[1]) and v[2]]
    c_p = pm['p_r'] <= 0.10
    T1 = T0 and c3a and c3b and c3n and bool(beat) and c_p
    w('**T1** — T0 (%s) · C3 TRAIN ≥ −0,10 (%s) → %s · C3 TEST ≥ 0 (%s) → %s · n TEST C3 ≥ 15 (%d) → %s · C3 vượt ĐC-b hoặc ĐC-c ở ≥ 1 nửa → %s · '
      'hoán vị cổng D p ≤ 0,10 (%s) → %s. ⇒ **T1 %s**.' % (
          'đạt' if T0 else 'không', fs(sp3['TRAIN']['m']), 'đạt' if c3a else 'KHÔNG', fs(sp3['TEST']['m']), 'đạt' if c3b else 'KHÔNG',
          sp3['TEST']['n'], 'đạt' if c3n else 'KHÔNG', ('đạt (%s)' % ', '.join(k[1] for k in beat)) if beat else 'KHÔNG', f(pm['p_r'], 3),
          'đạt' if c_p else 'KHÔNG', 'ĐẠT' if T1 else 'KHÔNG ĐẠT'))
    w('')
    T2 = {}
    for cell, src in (('C3', 'CHoCH (C3)'), ('C4', 'Gộp C4')):
        sp = split_cells(R['poc'][cell][1])
        vs = [v for k, v in VER.items() if k[0] == src]
        allv = len(vs) >= 2 and all('KHÁC đối chứng ▲' in v[0] for v in vs)
        T2[cell] = (sp['TRAIN']['m'] > 0 and sp['TEST']['m'] > 0 and sp['TEST']['n'] >= 30 and allv)
        w('**T2 (%s)** — TRAIN %s > 0, TEST %s > 0, n TEST %d ≥ 30, vượt mọi đối chứng → **%s**.' % (
            cell, fs(sp['TRAIN']['m']), fs(sp['TEST']['m']), sp['TEST']['n'], 'ĐẠT' if T2[cell] else 'KHÔNG ĐẠT'))
        w('')
    w('**Kết luận máy:** %s' % ('T1 đạt ⇒ được port C# để ghi log live (vẫn TẮT mặc định).' if T1 else
                                'không đạt T1 ⇒ **KHÔNG port C#**; ' + ('đạt T0 nên hướng đáng theo dõi tiếp.' if T0 else
                                                                        'không đạt T0 ⇒ ghi "không", C vẫn tắt, không mở thêm vòng tinh chỉnh trên cùng dữ liệu.')))
    w('')
    # ---------------------------------------------------------------- chỗ tự quyết
    w('## 11. Chỗ tự quyết (plan không nói rõ)')
    w('')
    for q in QS:
        w('- ' + q)
    w('')
    # ---------------------------------------------------------------- phụ lục
    w('## Phụ lục A — nhãn từng phiên (máy) — ĐỪNG mở trước khi tự gắn nhãn 15 phiên')
    w('')
    w('| phiên | hôm qua | nhãn | asym | bulge | VAL_T – VAH_T | T | close |\n|---|---|---|---|---|---|---|---|')
    for s in D.clean_snos:
        d = shapes.get(s)
        if not d:
            w('| %s | – | (không có) | | | | | |' % D.st['session_id'].loc[s])
            continue
        w('| %s | %s | %s | %s | %s | %s – %s | %s – %s | %s |' % (D.st['session_id'].loc[s], D.st['session_id'].loc[d['q']], d['label'], fs(d['asym']),
                                                               f(d['bulge']), f(d['val'], 1), f(d['vah'], 1), f(d['t_lo'], 1), f(d['t_hi'], 1), f(d['close'], 1)))
    w('')
    w('## Phụ lục B — nhật ký VA_C đầy đủ — ĐỪNG mở trước khi tự tìm 5 ca trên Optimus Flow')
    w('')
    w('| # | chiều | phiên | climax (VN) | VSA | Δ climax | L1 | H1 | L2 | sinh (VN) | pha | VA lúc sinh | cao | nới | chết | tuổi | lần chạm | lệnh |')
    w('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for x in ch['log']:
        w('| %d | %s | %s | %s | %s | %+d | %s | %s | %s | %s | %s | %s – %s | %s | %d | %s | %d | %d | %d |' % (
            x['id'], x['dir'], x['session'], x['t_climax'][5:], f(x['vsa'], 1), int(x['delta_climax']), f(x['L1'], 1), f(x['H1'], 1), f(x['L2'], 1),
            x['t_birth'][5:], x['phase'], f(x['lo0'], 1), f(x['hi0'], 1), f(x['height0'], 1), x['n_ext'], x['why'], x['life'], x['touches'],
            x.get('n_trades', 0)))
    w('')
    if os.path.exists(EVAL_MD):
        w(open(EVAL_MD, encoding='utf-8').read())
    with open(OUT_MD, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('ghi %s (%.0fs)' % (OUT_MD, time.time() - t0))


if __name__ == '__main__':
    main()
