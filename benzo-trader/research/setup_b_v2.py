# -*- coding: utf-8 -*-
"""Setup B-v2 "Hấp thụ" trên 8 loại vùng (plan `plans/BENZO-B-v2-plan.md`). Pipeline đo đầy đủ → report/RESULTS-B-v2.md + report/_eval_b_v2.txt.

Chạy: python3 setup_b_v2.py      (chỉ file 90d GCZ26 — KHÔNG chạy file 2 năm)
Không sửa kernel.py. Thuật toán B = setup_b_hap_thu.detect (y nguyên hằng số); vùng mới = zones_b_v2.build_extra.
Mọi hằng số dưới đây ĐĂNG KÝ TRƯỚC khi chạy lần đầu (commit riêng trước khi có kết quả).
"""
from __future__ import annotations

import os
import sys
import json
import math
import time
from contextlib import contextmanager

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_b_hap_thu as SB  # noqa: E402
import zones_b_v2 as ZB  # noqa: E402
import benzo_vcl as BV  # noqa: E402  (chỉ dùng hàm thống kê/phán quyết dùng chung: rstat, band, verdict, thang_of, GROUPS)

D90 = SB.D90
REPORT = os.path.join(HERE, 'report')
IMG = os.path.join(REPORT, 'img')
OUT_MD = os.path.join(REPORT, 'RESULTS-B-v2.md')
OUT_EVAL = os.path.join(REPORT, '_eval_b_v2.txt')
FIXTURE_OLD = os.path.join(REPORT, '_b_old_idx.json')

# ------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC (plan mục 2.3) ------------------------------------
MAIN = (0.5, 3)                                   # θ 0,5 · N 3 (ô chính vòng 1, không chọn theo kết quả)
RR = 3.0                                          # TP 3R
SHIFT_LO, SHIFT_HI, REPS, SHIFT_SEED = 3.0, 15.0, 100, 20261024   # ĐC1: cùng ma trận δ với BENZO-VCL / A-v4
CTRL_DRAWS = 200                                  # ĐC2: 200 lần rút
BOOT, BOOT_SEED = 10000, 0                        # KTC 95 % bootstrap
MIN_N = 10                                        # phán quyết chỉ khi >= 10 lệnh ở CẢ TRAIN và TEST
EXPECT_OLD = (11, 0.273, 0.00)                    # B cũ ô chính trên 90d (RESULTS-B vòng 1)
EXPECT_N_NEW = (20, 60)                           # kỳ vọng đăng ký trước cho n(B-v2)
BREAKEVEN_WR = 0.27                               # hoà vốn xấp xỉ ở 3R sau chi phí
THETAS, NS = SB.THETAS, SB.NS                     # chỉ cho bảng độ nhạy phụ lục (không chọn lại)
EXPECT_TXT = [
    'n: 11 → **20–60** (6 loại mới; HVN_W/POC_W thường cách giá 20–80 giá ⇒ ít chạm; POC_D/VAH/VAL/HVN_D gần giá hơn ⇒ đóng góp chính). '
    'n không tăng ≥ 2× ⇒ bộ lọc cụm/θ là nút thắt, không phải vùng.',
    'WR ở 3R: **25–35 %** (hoà vốn ~27 %). Kỳ vọng hợp lý: **B-v2 ≈ dải ĐC1** (vị trí vùng không mang thông tin — khớp mọi phép đo S/R trước).',
    'Không ép: không chọn ô độ nhạy đẹp; TP 2R không chạy; không thêm bộ lọc mới giữa chừng.',
]
assert (SHIFT_LO, SHIFT_HI, REPS, SHIFT_SEED) == (BV.SHIFT_LO, BV.SHIFT_HI, BV.REPS, BV.SEED)
assert (BOOT, BOOT_SEED, MIN_N) == (BV.BOOT, BV.BOOT_SEED, BV.MIN_N)

ZONES_OLD, ZONES_V2 = ZB.ZONES_OLD, ZB.ZONES_V2
CONFIGS = [('B-cũ', ZONES_OLD), ('B-v2', ZONES_V2), ('B-mới-thôi', ZB.names_of(ZB.ZTYPES_NEW))] + \
          [('B-cũ + %s' % k, ZONES_OLD + ZB.names_of((k,))) for k in ZB.ZTYPES_NEW] + \
          [('B-v2 − %s' % k, tuple(nm for nm in ZONES_V2 if ZB.ZTYPE_OF[nm] != k)) for k in ZB.ZTYPES_NEW]
GROUPS = BV.GROUPS                                # TRAIN, TEST, GỘP, T8 (gồm 29–31/7), T9, T10


# ------------------------------------------------------------------ dữ liệu
class Data:
    def __init__(self):
        self.df = K.load_bars(D90 + '_bars.csv')
        assert not self.df['splice_jump'].any(), 'file 90d phải là MỘT hợp đồng (không có chỗ nối)'
        self.prof = K.build_profiles(self.df, D90 + '.csv')
        self.ctx = K._Ctx(self.df, self.prof)
        self.lev = ZB.session_table_b(self.df, self.prof, self.ctx)
        self.extra = ZB.build_extra(self.df, self.prof, self.ctx, self.lev)
        self.P = SB.prepare(self.df, self.prof, self.extra)
        self.zc = self.P['zc']
        self.sno = self.df['session_no'].to_numpy()
        st = K.session_table(self.df)
        st['split'] = np.where(st['session_id'].str[:10] <= K.CONST['split_train_end'], 'TRAIN', 'TEST')
        self.st = st
        self.clean = (~st['splice'].to_numpy()) & (~st['thin'].to_numpy()) & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
        self.days = int(self.clean.sum())
        self.days_split = {sp: int((self.clean & (st['split'] == sp).to_numpy()).sum()) for sp in ('TRAIN', 'TEST')}
        self.dsh = ZB.shift_matrix(int(self.sno.max()) + 1, REPS, SHIFT_LO, SHIFT_HI, SHIFT_SEED)


def run(P, zones, theta=MAIN[0], N=MAIN[1], funnel=None):
    ents = SB.detect(P, theta, N, zones=zones, funnel=funnel, rr=RR)
    t = K.simulate(P['df'], ents)
    if len(t):
        t['thang'] = [BV.thang_of(x) for x in t['session_id']]
    return ents, t


def closed(t):
    return BV.closed(t)


def gstats(t):
    """{nhóm: (n, wr, R TB)} trên lệnh đã đóng (dùng cho bản dời / đối chứng)."""
    c = closed(t)
    out = {}
    for g, col, val in GROUPS:
        m = np.ones(len(c), bool) if (col is None or not len(c)) else (c[col] == val).to_numpy()
        r = c['r'].to_numpy(float)[m] if len(c) else np.zeros(0)
        out[g] = (len(r), float((r > 0).mean()) if len(r) else np.nan, float(r.mean()) if len(r) else np.nan)
    return out


def rs(t, mask=None):
    c = closed(t)
    if not len(c):
        return BV.rstat([])
    r = c['r'].to_numpy(float)
    return BV.rstat(r if mask is None else r[mask(c)])


@contextmanager
def _patched_map(extra):
    """Tạm cho kernel.control_sample nhìn thấy cột vùng mới (tên mức → cột cùng tên). Không sửa kernel: khôi phục dict cũ ở finally."""
    old = dict(K.ZONE_NAME2COL)
    K.ZONE_NAME2COL.update({nm: nm for nm in extra})
    try:
        yield
    finally:
        K.ZONE_NAME2COL.clear()
        K.ZONE_NAME2COL.update(old)


def ctrl_zcols(D):
    return pd.concat([D.zc, ZB.zone_table(D.extra).set_index(D.zc.index)], axis=1)


def dc2(D, t, draws=CTRL_DRAWS):
    """ĐC2 — vào ngẫu nhiên tại ĐÚNG mức của lệnh thật (|close − mức| <= 1 hoặc râu chạm), cùng chế độ kernel, cùng chiều, cùng R:R,
    SL = râu nến + 0,3 (kernel.control_sample, không sửa). Trả {nhóm: (dải R TB), (dải WR)} theo nhóm của lệnh thật gốc."""
    c = closed(t)
    if not len(c):
        return {}, {}
    recs = [dict(idx=int(x.idx), side=int(x.side), entry=float(x.entry), sl=float(x.sl), tp=float(x.tp), setup='B', zone=str(x.zone))
            for x in c.itertuples()]
    grp = {int(x.idx): (x.split, x.thang) for x in c.itertuples()}
    zcols = ctrl_zcols(D)
    perR = {g: [] for g, _, _ in GROUPS}
    perW = {g: [] for g, _, _ in GROUPS}
    with _patched_map(D.extra):
        for sd in range(draws):
            ce = K.control_sample(D.df, zcols, D.P['modecode'], entries=recs, n_random=1, seed=sd)
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
                perR[g].append(rv[m].mean() if m.any() else np.nan)
                perW[g].append((rv[m] > 0).mean() if m.any() else np.nan)
    return {g: BV.band(v) for g, v in perR.items()}, {g: BV.band(v) for g, v in perW.items()}


def cmp_vs(t_sel, bandsR):
    """cmp cho BV.verdict: nhóm → (R TB thật, sai số, n, TB đối chứng, q5, q95)."""
    out, ns = {}, {}
    for g, col, val in GROUPS:
        c = t_sel if col is None else t_sel[t_sel[col] == val] if len(t_sel) else t_sel
        s = BV.rstat(c['r'].to_numpy(float) if len(c) else [])
        ns[g] = s['n']
        out[g] = (s['m'], s['se'], s['n'], *bandsR.get(g, (np.nan,) * 3))
    return out, (ns['TRAIN'] >= MIN_N and ns['TEST'] >= MIN_N)


def v2only_mask(t_v2, t_old):
    old_idx = set(t_old['idx'].tolist()) if len(t_old) else set()
    return ~t_v2['idx'].isin(old_idx).to_numpy() if len(t_v2) else np.zeros(0, bool)


# ------------------------------------------------------------------ đối chứng dời (ĐC1)
def dc1(D, cfgs):
    """Chạy nguyên detect + simulate trên bản đồ vùng dời (mọi mức kể cả VWAP + δ[phiên, bản]) cho mọi cấu hình.
    Trả {tên cấu hình: list gstats theo bản} + 'chỉ-v2' (lệnh v2 dời không có trong B-cũ dời cùng bản)."""
    res = {name: [] for name, _ in cfgs}
    res['chỉ-v2'] = []
    for k in range(REPS):
        Pk = SB.prepare(D.df, D.prof, ZB.shifted(D.extra, D.zc, D.dsh[:, k], D.sno))
        tt = {}
        for name, zones in cfgs:
            tt[name] = run(Pk, zones)[1]
            res[name].append(gstats(tt[name]))
        tv, to = closed(tt['B-v2']), closed(tt['B-cũ'])
        res['chỉ-v2'].append(gstats(tv[v2only_mask(tv, to)] if len(tv) else tv))
    return res


def bands_of(reps, which):
    """reps = list gstats; which 0=n, 1=wr, 2=R TB. Trả {nhóm: (TB, q5, q95)}."""
    return {g: BV.band([r[g][which] for r in reps]) for g, _, _ in GROUPS}


# ------------------------------------------------------------------ định dạng
def f(x, p=2):
    return ('%.*f' % (p, x)).replace('.', ',') if x == x else '–'


def pct(x, p=1):
    return (f(100 * x, p) + ' %') if x == x else '–'


def nwr(s):
    return '%d · %s · %s' % (s['n'], pct(s['wr']), f(s['m']))


def ci(s):
    return '[%s ; %s]' % (f(s['lo']), f(s['hi']))


def plot_trade(df, e, path, zlevels, before=45, after=30):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    i, ex = int(e['idx']), int(e['exit_idx'])
    a, b = max(0, i - before), min(len(df), max(ex, i) + after)
    seg = df.iloc[a:b]
    fig, ax = plt.subplots(figsize=(15, 7))
    for k, r in enumerate(seg.itertuples()):
        col = '#1a7f37' if r.close >= r.open else '#cf222e'
        ax.plot([k, k], [r.low, r.high], color=col, lw=1)
        ax.add_patch(plt.Rectangle((k - 0.3, min(r.open, r.close)), 0.6, max(abs(r.close - r.open), 0.05), color=col))
        ax.text(k, r.low - 0.2, '%+d' % int(r.delta), ha='center', va='top', fontsize=5, color=('g' if r.delta > 0 else 'r'))
    ax.axhline(e['entry'], color='b', lw=1, ls='--')
    ax.axhline(e['sl'], color='r', lw=1)
    ax.axhline(e['tp'], color='g', lw=1)
    ax.axvline(i - a, color='b', lw=0.8, alpha=.5)
    ax.axvline(ex - a, color='m', lw=0.8, alpha=.5)
    lo_, hi_ = seg['low'].min() - 1.5, seg['high'].max() + 1.5
    for nm, v in zlevels.items():
        if v == v and lo_ < v < hi_:
            ax.axhline(v, color='orange', lw=0.8, ls=':')
            ax.text(len(seg) - 1, v, nm, fontsize=7, color='darkorange', va='bottom', ha='right')
    ticks = list(range(0, len(seg), 5))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(seg['t_vn'].iloc[t])[5:16] for t in ticks], rotation=60, fontsize=6)
    ax.set_title('B-v2 %s %s r=%+.2f | vào %s VN | vùng %s Z=%.1f | entry %.1f SL %.1f TP %.1f' % (
        'BUY' if e['side'] > 0 else 'SELL', e['outcome'], e['r'], str(e['t_vn'])[:16], e['zone'], e['zprice'], e['entry'], e['sl'], e['tp']), fontsize=9)
    ax.set_ylim(seg['low'].min() - 0.8, seg['high'].max() + 0.8)
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


def cf_ratio(P, e, N=MAIN[1]):
    """|Δ_CF| / |delta| lớn nhất của move — tính lại đúng công thức detect (chỉ để in ví dụ)."""
    i, s = int(e['idx']), int(e['side'])
    M = -s
    a = i - N
    s0 = max(a - SB.LOOKBACK, int(i - P['posin'][i]))
    lo, hi, dl, adl = P['lo'], P['hi'], P['dl'], P['adl']
    z = float(e['zprice'])
    if M > 0:
        k = s0 + int(np.argmin(lo[s0:a]))
        move = z - lo[k]
    else:
        k = s0 + int(np.argmax(hi[s0:a]))
        move = hi[k] - z
    seg = slice(k, a)
    same = dl[seg] * M > 0
    mad = adl[seg][same].max() if same.any() else adl[seg].max()
    return move, adl[i] / mad


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    D = Data()
    df, P = D.df, D.P
    L = []
    A = L.append
    # ---------- tái tạo gốc (điều kiện tiên quyết)
    e_old, t_old = run(P, ZONES_OLD)
    s_old = rs(t_old)
    fx = json.load(open(FIXTURE_OLD)) if os.path.exists(FIXTURE_OLD) else None
    ok_old = s_old['n'] == EXPECT_OLD[0] and abs(s_old['wr'] - EXPECT_OLD[1]) < 0.0015 and abs(s_old['m'] - EXPECT_OLD[2]) <= 0.005 \
        and (fx is None or [e['idx'] for e in e_old] == fx['idx'])
    if not ok_old:
        raise SystemExit('KHÔNG tái tạo được B cũ: n=%d WR=%.3f R=%.3f — dừng.' % (s_old['n'], s_old['wr'], s_old['m']))
    print('tái tạo B cũ OK', flush=True)
    # ---------- 15 cấu hình
    RES, ENTS, FUN = {}, {}, {}
    for name, zones in CONFIGS:
        fn = {}
        ENTS[name], RES[name] = run(P, zones, funnel=fn)
        FUN[name] = fn
    e_v2, t_v2 = ENTS['B-v2'], RES['B-v2']
    # tính chất tập con (plan 3.2)
    io, iv = {e['idx']: e for e in e_old}, {e['idx']: e for e in e_v2}
    assert set(io) <= set(iv)
    for i, e in io.items():
        x = iv[i]
        assert (x['side'], x['entry'], x['sl'], x['tp'], x['zprice']) == (e['side'], e['entry'], e['sl'], e['tp'], e['zprice'])
    c_old, c_v2 = closed(t_old), closed(t_v2)
    m_only = v2only_mask(c_v2, c_old)
    c_only, c_common = c_v2[m_only], c_v2[~m_only]
    lost = c_old[~c_old['idx'].isin(set(t_v2['idx'].tolist()))] if len(c_old) else c_old
    print('15 cấu hình %.0fs' % (time.time() - t0), flush=True)
    # ---------- ĐC1
    R1 = dc1(D, CONFIGS)
    print('ĐC1 %.0fs' % (time.time() - t0), flush=True)
    # ---------- ĐC2
    DC2 = {'B-cũ': dc2(D, t_old), 'B-v2': dc2(D, t_v2), 'chỉ-v2': dc2(D, c_only)}
    print('ĐC2 %.0fs' % (time.time() - t0), flush=True)

    # ======================================================== báo cáo
    days = D.days
    A('# RESULTS-B-v2 — Setup B "Hấp thụ" mở từ 2 vùng VWAP lên 8 loại vùng (12 mức)')
    A('')
    A('Sinh bởi `setup_b_v2.py` (deterministic) theo `plans/BENZO-B-v2-plan.md`. **Chỉ file 90d GCZ26** `fp_GCZ26_XCEC_Time_20260723-20261021_90d` '
      '(một hợp đồng, kiểm `splice_jump.any() == False` ✔), %d nến M1, %d phiên sạch (TRAIN %d ≤ 2026-09-15, TEST %d). Giờ UTC (VN = UTC+7). '
      'Cấu hình duy nhất: θ 0,5 · N 3 · TP 3R · mono "ends" · biến thể "base" · không bias · mọi pha trừ OFF. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ SL; '
      '1 lệnh mở cùng lúc; tối đa 2 lệnh / (loại vùng, phiên).' % (len(df), days, D.days_split['TRAIN'], D.days_split['TEST']))
    A('')
    A('## 0. Kỳ vọng đăng ký TRƯỚC khi chạy (plan 3.6, chép nguyên từ hằng số đã commit)')
    A('')
    for x in EXPECT_TXT:
        A('- ' + x)
    A('')
    A('Tái tạo B cũ (điều kiện tiên quyết): n = %d, WR %s, R TB %s, danh sách idx khớp fixture `report/_b_old_idx.json` ✔.' % (s_old['n'], pct(s_old['wr']), f(s_old['m'])))
    A('')
    # ---------- tập vùng
    A('## 1. Tập vùng — có mặt, trùng nhau, khoảng cách')
    A('')
    cl_snos = [int(s) for s in D.st.index[D.clean]]
    ov = ZB.overlap_stats(D.lev, D.zc, df, cl_snos)
    okb = P['okbar']
    A('| mức | số phiên sạch có mức (/%d) | số nến đo được chạm mức (|close−Z| ≤ 1 hoặc râu chạm) | trung vị |close − Z| (giá) |' % len(cl_snos))
    A('|---|---|---|---|')
    for nm in ZONES_V2:
        z = P['Z'][nm]
        with np.errstate(invalid='ignore'):
            dd = np.abs(P['cl'] - z)[okb & ~np.isnan(z)]
        A('| %s | %d | %d | %s |' % (nm, ov['have'][nm], int((P['touch'][nm] & okb & P['warm'][nm]).sum()), f(float(np.median(dd)), 1) if len(dd) else '–'))
    A('')
    pw = [(D.lev[s]['poc_w'], D.lev[s]['hvn_w'][0]) for s in cl_snos if D.lev[s]['poc_w'] == D.lev[s]['poc_w'] and D.lev[s]['hvn_w']]
    dpw = np.array([abs(a - b) for a, b in pw])
    st = D.st
    nopocw = [st.loc[s, 'session_id'] for s in cl_snos if D.lev[s]['poc_w'] != D.lev[s]['poc_w']]
    thin_hw = [st.loc[s, 'session_id'] for s in cl_snos if D.lev[s]['hvn_w'] and
               bool(st[(st['week_no'] >= st.loc[s, 'week_no'] - K.CONST['week_lookback']) & (st['week_no'] < st.loc[s, 'week_no'])]['thin'].any())]
    part = [st.loc[s, 'session_id'] for s in cl_snos if D.lev[s]['hvn_w_partial']]
    A('- Phiên sạch **không có POC_W**: %s (tuần đầu file không có tuần trước; tuần 07-27…07-31 dựng trên tuần 07-23/24 chỉ có 2 phiên, đều thin ⇒ NaN theo luật ≥ 3 phiên không thin). '
      'Tuần 08-03…08-07 có POC_W = POC của 3 phiên 07-29/30/31 (không thin).' % (', '.join(nopocw) or 'không'))
    A('- |POC_W − HVN_W1| trên %d phiên có cả hai: trung vị %s giá (min %s, max %s) — POC_W (1 tuần) KHÁC HVN_W1 (gộp 3 tuần) nên không trùng lặp.' % (
        len(dpw), f(float(np.median(dpw)), 1) if len(dpw) else '–', f(float(dpw.min()), 1) if len(dpw) else '–', f(float(dpw.max()), 1) if len(dpw) else '–'))
    A('- HVN_W dựng trên cửa sổ có phiên thin (kernel không loại thin ở `week_hvn`): %d phiên sạch (%s). Cờ `hvn_w_partial` (cửa sổ cắt bởi chỗ nối): %d phiên.' % (
        len(thin_hw), ', '.join(thin_hw) or '–', len(part)))
    A('- POC_D/VAH_D/VAL_D/HVN_D của 2026-07-29 dựng trên phiên thin 07-28 (kernel không loại thin ở "hôm qua") — 1 phiên, ghi chú, không sửa.')
    A('- **Tỉ lệ trùng** (plan 1.4.5): %d / %d cặp mức KHÁC loại cách nhau ≤ 1 giá (%s); trung bình %s mức/phiên. VWAP lấy giá trị nến cuối phiên (chỉ để mô tả).' % (
        ov['pairs_close'], ov['pairs_tot'], pct(ov['frac']), f(ov['levels_per_session'], 1)))
    A('')
    A('Trung vị khoảng cách giữa các loại (giá):')
    A('')
    A('| cặp loại | trung vị |')
    A('|---|---|')
    for k, v in sorted(ov['med_dist'].items(), key=lambda kv: kv[1]):
        A('| %s ↔ %s | %s |' % (k[0], k[1], f(v, 1)))
    A('')
    # ---------- công suất
    n1, n2 = s_old['n'], rs(t_v2)['n']
    sdR = float(c_v2['r'].std(ddof=1)) if len(c_v2) > 1 else np.nan
    A('## 2. Công suất thống kê (in TRƯỚC bảng chính — plan 3.3)')
    A('')
    A('- Sai số WR ≈ √(p(1−p)/n), p = 0,27: n = %d ⇒ ±%s điểm; n = %d ⇒ ±%s điểm.' % (n1, f(100 * math.sqrt(.27 * .73 / max(n1, 1)), 1), n2, f(100 * math.sqrt(.27 * .73 / max(n2, 1)), 1)))
    mdw = 2.8 * math.sqrt(.27 * .73) * math.sqrt(1 / max(n1, 1) + 1 / max(n2, 1))
    mdr = 2.8 * sdR * math.sqrt(1 / max(n1, 1) + 1 / max(n2, 1)) if sdR == sdR else np.nan
    A('- Chênh WR nhỏ nhất phát hiện được (80 %%, hai phía) giữa B-cũ (n=%d) và B-v2 (n=%d): ≈ **%s điểm**; chênh R TB nhỏ nhất ≈ **%sR** (σ_R = %s). '
      '⇒ **so WR cũ ↔ mới trực tiếp gần như vô nghĩa**; phán quyết dựa vào dải đối chứng và nhóm lệnh chỉ-v2.' % (n1, n2, f(100 * mdw, 0), f(mdr), f(sdR)))
    A('')
    # ---------- bảng chính
    A('## 3. Bảng chính — 15 cấu hình (plan 3.1)')
    A('')
    A('n = lệnh đã đóng; lệnh/ngày chia %d phiên sạch; KTC = khoảng tin cậy 95 %% bootstrap (10 000, seed 0) của R TB.' % days)
    A('')
    A('| cấu hình | n | lệnh/ngày | **WR** | R TB | KTC 95 % | kỳ vọng giá/lệnh | tổng R | chuỗi thua |')
    A('|---|---|---|---|---|---|---|---|---|')
    for name, _ in CONFIGS:
        t = RES[name]
        s = rs(t)
        c = closed(t)
        k = K._stats(t) if len(t) else dict(exp_pts=np.nan, sum_r=0.0, max_loss_streak=0)
        A('| %s | %d | %s | **%s** | %s | %s | %s | %s | %d |' % (name, s['n'], f(s['n'] / days), pct(s['wr']), f(s['m']), ci(s),
                                                             f(k['exp_pts']), f(k['sum_r'], 1), k['max_loss_streak']))
        if name == 'B-v2':
            A('| | | | | | | | | |')
    A('')
    A('Theo nửa và tháng (`n · WR · R TB`; T8 gồm 29–31/7):')
    A('')
    A('| cấu hình | TRAIN | TEST | T8 | T9 | T10 |')
    A('|---|---|---|---|---|---|')
    for name, _ in CONFIGS:
        c = closed(RES[name])
        row = []
        for col, val in (('split', 'TRAIN'), ('split', 'TEST'), ('thang', 'T8'), ('thang', 'T9'), ('thang', 'T10')):
            row.append(nwr(BV.rstat(c[c[col] == val]['r'].to_numpy(float) if len(c) else [])))
        A('| %s | %s |' % (name, ' | '.join(row)))
    A('')
    A('Theo pha và chiều (`n · WR · R TB`):')
    A('')
    A('| cấu hình | A | EU | US | BUY | SELL |')
    A('|---|---|---|---|---|---|')
    for name, _ in CONFIGS:
        c = closed(RES[name])
        row = []
        for col, val in (('phase', 'A'), ('phase', 'EU'), ('phase', 'US'), ('side', 1), ('side', -1)):
            row.append(nwr(BV.rstat(c[c[col] == val]['r'].to_numpy(float) if len(c) else [])))
        A('| %s | %s |' % (name, ' | '.join(row)))
    A('')
    # ---------- tách đóng góp mức lệnh
    A('## 4. Tách đóng góp ở mức LỆNH (plan 3.2)')
    A('')
    A('Tính chất tập con kiểm bằng assert: mọi lệnh thô của B-cũ đều có trong B-v2 với cùng chiều/entry/SL/TP/Z ✔ (%d ⊆ %d lệnh thô).' % (len(e_old), len(e_v2)))
    A('')
    s_only, s_common = BV.rstat(c_only['r'].to_numpy(float)), BV.rstat(c_common['r'].to_numpy(float))
    lost_w = int((lost['r'] > 0).sum()) if len(lost) else 0
    A('| nhóm | n · WR · R TB | KTC 95 % | TRAIN | TEST |')
    A('|---|---|---|---|---|')
    for lab, c in (('Lệnh chung (có ở cả hai bản đã mô phỏng)', c_common), ('**Lệnh chỉ-v2** (nhóm quyết định)', c_only), ('Lệnh cũ bị MẤT ở v2 (số liệu trong bản cũ)', lost)):
        s = BV.rstat(c['r'].to_numpy(float) if len(c) else [])
        tr_ = BV.rstat(c[c['split'] == 'TRAIN']['r'].to_numpy(float) if len(c) else [])
        te_ = BV.rstat(c[c['split'] == 'TEST']['r'].to_numpy(float) if len(c) else [])
        A('| %s | %s | %s | %s | %s |' % (lab, nwr(s), ci(s), nwr(tr_), nwr(te_)))
    A('')
    A('Lệnh cũ bị mất do `one_at_a_time` (lệnh vùng mới mở trước chặn): %d lệnh, trong đó %d lệnh thắng.' % (len(lost), lost_w))
    A('')
    A('### Theo loại vùng (lệnh B-v2). Loại n < 10 chỉ in số, không bình luận.')
    A('')
    A('*Vùng thắng* = ztype ghi trên lệnh (thứ tự ưu tiên VWAP trước). *Bất kỳ vùng* = lệnh tính cho mọi loại có trong `zones_hit` (tổng > n).')
    A('')
    A('| loại | vùng thắng: n · WR · R TB | bất kỳ vùng: n · WR · R TB |')
    A('|---|---|---|')
    zt = c_v2['ztype'].to_numpy() if len(c_v2) else np.array([])
    anyz = [set(ZB.ZTYPE_OF[x] for x in h) for h in c_v2['zones_hit']] if len(c_v2) else []
    rv2 = c_v2['r'].to_numpy(float) if len(c_v2) else np.zeros(0)
    by_ztype = {}
    for k in ('VWAP_W', 'VWAP_D') + ZB.ZTYPES_NEW:
        sw = BV.rstat(rv2[zt == k])
        sa = BV.rstat(rv2[np.array([k in h for h in anyz], bool)] if len(anyz) else [])
        by_ztype[k] = sw
        A('| %s | %s | %s |' % (k, nwr(sw), nwr(sa)))
    A('')
    A('### Số mức cùng khớp tại nến xác nhận (`n_hit`, chỉ mô tả, không lọc)')
    A('')
    nh = np.array([len(h) for h in c_v2['zones_hit']]) if len(c_v2) else np.zeros(0, int)
    A('| n_hit | n · WR · R TB |')
    A('|---|---|')
    for lab, m in (('1', nh == 1), ('2', nh == 2), ('≥ 3', nh >= 3)):
        A('| %s | %s |' % (lab, nwr(BV.rstat(rv2[m]))))
    A('')
    A('### Phễu lọc (số ứng viên qua từng bước, cộng mọi mức và hai chiều; chưa gồm trần 2 lệnh / one-at-a-time)')
    A('')
    A('| bước | B-cũ | B-v2 |')
    A('|---|---|---|')
    for k in sorted(set(FUN['B-cũ']) | set(FUN['B-v2'])):
        A('| %s | %d | %d |' % (k, FUN['B-cũ'].get(k, 0), FUN['B-v2'].get(k, 0)))
    A('')
    # ---------- đối chứng
    A('## 5. Đối chứng (plan 3.4)')
    A('')
    A('**ĐC1 — dời bản đồ vùng:** mọi mức của phiên (12 mức, kể cả VWAP động: cộng hằng δ) dời cùng δ[phiên, bản], |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, '
      '%d bản, seed %d (ma trận y hệt BENZO-VCL, test `test_shift_matrix_same_as_vcl`). Chạy NGUYÊN `detect` + `simulate` trên mảng dời ⇒ lệnh dời cũng chạm '
      'vùng (dời) ≤ 1 giá, cùng cơ chế move → cụm → nến xác nhận; chỉ VỊ TRÍ khác (= đối chứng khớp khoảng cách theo xây dựng). Bộ lọc chế độ/VA Âu/IB không dời. '
      'Nhóm "chỉ-v2" ở bản dời = lệnh B-v2 dời không có trong B-cũ dời cùng bản.' % (REPS, SHIFT_SEED))
    A('')
    A('**ĐC2 — vào ngẫu nhiên tại đúng mức:** `kernel.control_sample` (không sửa, qua `_patched_map`), mỗi lệnh thật rút 1 nến chạm ĐÚNG mức đó '
      '(|close − mức| ≤ 1 hoặc râu chạm), cùng chế độ kernel, cùng chiều, cùng R:R, SL = râu nến + 0,3; %d lần.' % CTRL_DRAWS)
    A('')
    A('**Ngưỡng "khác đối chứng"** (nguyên PLAN-LAN-CHAM mục 5): ngoài dải 5–95 %% ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số ở cả hai; '
      'chỉ áp dụng khi nhóm có ≥ %d lệnh ở CẢ TRAIN và TEST.' % MIN_N)
    A('')
    A('### ĐC1 — thật vs dải 100 bản dời (`thật | TB dời [5 % ; 95 %]`)')
    A('')
    A('| nhóm | đo | GỘP | TRAIN | TEST | T8 | T9 | T10 |')
    A('|---|---|---|---|---|---|---|---|')
    real_g = {'B-cũ': gstats(t_old), 'B-v2': gstats(t_v2), 'chỉ-v2': gstats(c_only)}
    for nm in ('B-cũ', 'B-v2', 'chỉ-v2'):
        for wi, lab, fmt in ((0, 'n', lambda x: f(x, 0) if x == x else '–'), (1, 'WR', pct), (2, 'R TB', f)):
            bd = bands_of(R1[nm], wi)
            cells = []
            for g, _, _ in (('GỘP', 0, 0),) + tuple(x for x in GROUPS if x[0] != 'GỘP'):
                b = bd[g]
                cells.append('%s \\| %s [%s ; %s]' % (fmt(real_g[nm][g][wi]), fmt(b[0]), fmt(b[1]), fmt(b[2])))
            A('| %s | %s | %s |' % (nm, lab, ' | '.join(cells)))
    A('')
    # ---------- phán quyết 15 phép so
    A('### Phán quyết theo ngưỡng — 15 phép so (R TB)')
    A('')
    A('| # | phép so | n TRAIN / TEST | phán quyết |')
    A('|---|---|---|---|')
    VER = {}
    rows = []
    cv2, okv2 = cmp_vs(c_v2, bands_of(R1['B-v2'], 2))
    VER['v2_dc1'] = BV.verdict(cv2, okv2)
    rows.append(('B-v2 vs ĐC1 (dời)', cv2, VER['v2_dc1']))
    cv2b, okv2b = cmp_vs(c_v2, DC2['B-v2'][0])
    VER['v2_dc2'] = BV.verdict(cv2b, okv2b)
    rows.append(('B-v2 vs ĐC2 (ngẫu nhiên tại mức)', cv2b, VER['v2_dc2']))
    co, oko = cmp_vs(c_only, DC2['chỉ-v2'][0])
    VER['only_dc2'] = BV.verdict(co, oko)
    rows.append(('chỉ-v2 vs ĐC2', co, VER['only_dc2']))
    for name, _ in CONFIGS[3:]:
        cc, okc = cmp_vs(closed(RES[name]), bands_of(R1[name], 2))
        VER[name] = BV.verdict(cc, okc)
        rows.append(('%s vs ĐC1 (dời, cùng cấu hình)' % name, cc, VER[name]))
    for j, (lab, cc, v) in enumerate(rows, 1):
        A('| %d | %s | %d / %d | %s |' % (j, lab, cc['TRAIN'][2], cc['TEST'][2], v))
    A('')
    n_out = sum(1 for _, _, v in rows if v.startswith('KHÁC'))
    A('Số ô "KHÁC đối chứng": **%d / %d** (ở mức 5 %% kỳ vọng ~0,75 ô do ngẫu nhiên; một ô lẻ không phải bằng chứng).' % (n_out, len(rows)))
    A('')
    A('Tham khảo (không tính vào 15 phép so): B-cũ vs ĐC2 = %s; chỉ-v2 vs ĐC1 (nhóm chỉ-v2 dời) = %s.' % (
        BV.verdict(*cmp_vs(c_old, DC2['B-cũ'][0])), BV.verdict(*cmp_vs(c_only, bands_of(R1['chỉ-v2'], 2)))))
    A('')
    A('### ĐC2 chi tiết (`R TB thật | TB đối chứng [5 % ; 95 %]`, WR đối chứng TB)')
    A('')
    A('| nhóm | GỘP | TRAIN | TEST | WR thật / WR đối chứng (GỘP) |')
    A('|---|---|---|---|---|')
    for nm, c in (('B-cũ', c_old), ('B-v2', c_v2), ('chỉ-v2', c_only)):
        bR, bW = DC2[nm]
        cells = []
        for g in ('GỘP', 'TRAIN', 'TEST'):
            sub = c if g == 'GỘP' else c[c['split'] == g]
            b = bR.get(g, (np.nan,) * 3)
            cells.append('%s \\| %s [%s ; %s]' % (f(sub['r'].mean() if len(sub) else np.nan), f(b[0]), f(b[1]), f(b[2])))
        A('| %s | %s | %s / %s |' % (nm, ' | '.join(cells), pct((c['r'] > 0).mean() if len(c) else np.nan), pct(bW.get('GỘP', (np.nan,))[0])))
    A('')
    # ---------- tiêu chí 3.5
    A('## 6. Phán quyết theo tiêu chí đăng ký trước (plan 3.5)')
    A('')
    sv2 = rs(t_v2)
    g_v2 = gstats(t_v2)
    bW, bR = bands_of(R1['B-v2'], 1), bands_of(R1['B-v2'], 2)

    def inb(val, b):
        return val == val and b[1] <= val <= b[2]
    in_tr = inb(g_v2['TRAIN'][1], bW['TRAIN']) and inb(g_v2['TRAIN'][2], bR['TRAIN'])
    in_te = inb(g_v2['TEST'][1], bW['TEST']) and inb(g_v2['TEST'][2], bR['TEST'])
    wr_only = s_only['wr']
    se_only = math.sqrt(wr_only * (1 - wr_only) / s_only['n']) if s_only['n'] else np.nan
    c1 = (sv2['n'] > s_old['n']) and (in_tr or in_te or (wr_only == wr_only and wr_only <= BREAKEVEN_WR + se_only))
    # 2. tệ đi
    g_only = gstats(c_only)
    b1o = bands_of(R1['chỉ-v2'], 2)
    b2o = DC2['chỉ-v2'][0]
    n_only_ok = g_only['TRAIN'][0] >= MIN_N and g_only['TEST'][0] >= MIN_N
    worse = []
    for g in ('TRAIN', 'TEST'):
        sub = c_only[c_only['split'] == g]
        se = BV.rstat(sub['r'].to_numpy(float))['se'] if len(sub) else np.nan
        r_ = g_only[g][2]
        worse.append((r_ == r_) and (r_ < b1o[g][1] or (b2o.get(g, (np.nan,))[0] == b2o.get(g, (np.nan,))[0] and r_ < b2o[g][0] - 2 * se)))
    c2a = n_only_ok and all(worse)
    c2b = lost_w >= 3
    c2 = c2a or c2b
    # 3. cải thiện thật
    ca = sv2['n'] >= 30 and g_v2['TRAIN'][0] >= MIN_N and g_v2['TEST'][0] >= MIN_N
    cb = (g_v2['TRAIN'][2] > 0) and (g_v2['TEST'][2] > 0)
    cc_ = all(g_only[g][1] >= s_old['wr'] and g_only[g][2] > 0 for g in ('TRAIN', 'TEST'))
    cd = VER['v2_dc1'].startswith('KHÁC đối chứng ▲') and VER['v2_dc2'].startswith('KHÁC đối chứng ▲')
    bad_types = []
    for k in ZB.ZTYPES_NEW:
        sk = by_ztype[k]
        if sk['n'] >= MIN_N and sk['m'] < -0.5:
            s_minus = rs(RES['B-v2 − %s' % k])
            if s_minus['m'] - sv2['m'] > 2 * sv2['se']:
                bad_types.append(k)
    ce = not bad_types
    c3 = ca and cb and cc_ and cd and ce
    yn = lambda b: 'ĐẠT' if b else 'không'  # noqa: E731
    A('| tiêu chí | điều kiện | kết quả |')
    A('|---|---|---|')
    A('| 1. "Chỉ tăng số lượng" | n(B-v2)=%d > n(B-cũ)=%d; B-v2 trong dải ĐC1 về WR **và** R TB ở TRAIN (%s) hoặc TEST (%s); hoặc chỉ-v2 WR %s ≤ 27 %% + 1 sai số (%s) | **%s** |' % (
        sv2['n'], s_old['n'], yn(in_tr), yn(in_te), pct(wr_only), pct(BREAKEVEN_WR + se_only) if se_only == se_only else '–', yn(c1)))
    A('| 2. "Tệ đi" | chỉ-v2 (n TRAIN %d / TEST %d, cần ≥ 10) R TB < mốc 5 %% ĐC1 (nhóm chỉ-v2 dời) hoặc < ĐC2 − 2 sai số ở CẢ hai nửa: %s; hoặc mất ≥ 3 lệnh cũ thắng do chặn (mất %d lệnh thắng) | **%s** |' % (
        g_only['TRAIN'][0], g_only['TEST'][0], yn(c2a) if n_only_ok else 'không áp dụng (n nhỏ)', lost_w, yn(c2)))
    A('| 3. "Cải thiện thật" | (a) n ≥ 30, ≥ 10 mỗi nửa: %s · (b) R TB > 0 cả TRAIN (%s) và TEST (%s): %s · (c) chỉ-v2 WR ≥ WR B-cũ và R TB > 0 cả hai nửa: %s · (d) vượt ĐC1 và ĐC2: %s · (e) không loại vùng kéo xuống: %s | **%s** |' % (
        yn(ca), f(g_v2['TRAIN'][2]), f(g_v2['TEST'][2]), yn(cb), yn(cc_), yn(cd), yn(ce) + ((' (' + ', '.join(bad_types) + ')') if bad_types else ''), yn(c3)))
    A('')
    if c1:
        final = 'CHỈ TĂNG SỐ LƯỢNG'
    elif c2:
        final = 'TỆ ĐI'
    elif c3:
        final = 'CẢI THIỆN THẬT'
    elif ca and cb and cc_:
        final = 'ỨNG VIÊN, chưa có lợi thế đo được; cần ≥ 3 tháng dữ liệu mới'
    else:
        final = 'không khớp tiêu chí 1–3 (ghi nguyên số, không diễn giải thêm)'
    A('**Kết luận (theo thứ tự kiểm 1 → 2 → 3): %s.**' % final)
    if c1:
        A('')
        A('*"Vùng mới cho thêm lệnh nhưng không cho thêm lợi thế đo được; B v2 ≈ B cũ chạy ở nhiều chỗ hơn."*')
    if c1 and c2:
        A('')
        A('Lưu ý: tiêu chí 2 ("tệ đi") CŨNG đạt — xem bảng trên; không ship.')
    if not c3:
        A('')
        A('Không đạt 3.5-3(d) ⇒ **chưa có lợi thế đo được trên %d phiên**. Với %d phiên, (d) gần như chỉ đạt khi hiệu ≥ ~0,6R.' % (days, days))
    A('')
    # ---------- độ nhạy
    A('## 7. Phụ lục — độ nhạy θ × N của B-v2 (CHỈ in, không chọn lại ô)')
    A('')
    A('`n · WR · R TB` toàn bộ.')
    A('')
    A('| θ \\ N | ' + ' | '.join(str(x) for x in NS) + ' |')
    A('|---|' + '---|' * len(NS))
    for th in THETAS:
        A('| %s | %s |' % (f(th, 1), ' | '.join(nwr(rs(run(P, ZONES_V2, th, N_)[1])) for N_ in NS)))
    A('')
    # ---------- ví dụ
    A('## 8. Ví dụ để soi chart — nhóm chỉ-v2 (5 thắng + 5 thua, chọn cách đều theo thời gian)')
    A('')
    A('| UTC | VN | chiều | loại vùng | Z | zones_hit | move (giá) | |Δ_CF|/max | entry | SL | TP | kết quả | R | ảnh |')
    A('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    os.makedirs(IMG, exist_ok=True)
    zt_all = ctrl_zcols(D)
    for lab, g in (('THẮNG', c_only[c_only['r'] > 0]), ('THUA', c_only[c_only['r'] <= 0])):
        g = g.iloc[np.unique(np.linspace(0, len(g) - 1, 5).astype(int))] if len(g) > 5 else g
        for x in g.to_dict('records'):
            mv, ratio = cf_ratio(P, x)
            fn = 'b_v2_%s_%s_%s.png' % (x['ztype'], str(x['t_utc'])[:16].replace(':', '').replace(' ', '_'), x['outcome'])
            i = int(x['idx'])
            zl = {nm: (zt_all['vwap_w'].iloc[i] if nm == 'VWAP_W' else zt_all['vwap_d'].iloc[i] if nm == 'VWAP_D' else zt_all[nm].iloc[i]) for nm in ZONES_V2}
            plot_trade(df, x, os.path.join(IMG, fn), zl)
            A('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | [ảnh](img/%s) |' % (
                str(x['t_utc'])[:16], str(x['t_vn'])[:16], 'BUY' if x['side'] > 0 else 'SELL', x['ztype'], f(x['zprice'], 1), ', '.join(x['zones_hit']),
                f(mv, 1), f(ratio), f(x['entry'], 1), f(x['sl'], 1), f(x['tp'], 1), x['outcome'], f(x['r']), fn))
    A('')
    A('## 9. Rủi ro / điểm mơ hồ (plan mục 5) — báo lại')
    A('')
    A('- Thứ tự ưu tiên VWAP-trước làm "vùng thắng" nghiêng về VWAP khi trùng — vì vậy in cả "bất kỳ vùng" và bỏ-một.')
    A('- Bộ lọc `trend_bad`/`edge_bad` dùng band VA Âu/IB cho mọi vùng; pha A chế độ NA nên không lọc được (như B cũ). Không thêm lọc.')
    A('- Biến thể "đang hình thành" (POC/VAH/VAL_D_DEV) **không làm** trong vòng này.')
    A('- Không gặp ca chưa phủ (mức NaN giữa phiên: không có vì mức cố định cả phiên; hai mức cùng loại cùng giá: không thể vì HVN cách nhau ≥ 2 giá).')
    A('- C# (`BenzoDetectors.cs` / `BenzoTrader.cs`) **không đụng** — chỉ port khi đạt 3.5-3 và được duyệt số.')
    A('')
    A('(Thời gian chạy: %.0f giây.)' % (time.time() - t0))
    open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')

    # ---------- báo cáo ngắn
    s_tr, s_te = BV.rstat(c_v2[c_v2['split'] == 'TRAIN']['r'].to_numpy(float)), BV.rstat(c_v2[c_v2['split'] == 'TEST']['r'].to_numpy(float))
    big = [k for k in ZB.ZTYPES_NEW if by_ztype[k]['n'] >= MIN_N]
    small = [k for k in ZB.ZTYPES_NEW if by_ztype[k]['n'] < MIN_N]
    E = []
    E.append('1. Số lệnh: B cũ %d (%s/ngày) → B v2 %d (%s/ngày); lệnh chung %d, lệnh chỉ-v2 %d, lệnh cũ bị chặn %d (thắng %d).' % (
        s_old['n'], f(s_old['n'] / days), sv2['n'], f(sv2['n'] / days), len(c_common), len(c_only), len(lost), lost_w))
    E.append('2. WR (TP 3R, hoà vốn ~27 %%): %s → %s (sai số ± %s điểm); lệnh chỉ-v2: %s.' % (
        pct(s_old['wr']), pct(sv2['wr']), f(100 * math.sqrt(sv2['wr'] * (1 - sv2['wr']) / max(sv2['n'], 1)), 1), pct(wr_only)))
    E.append('3. R TB: %s → %s %s; TRAIN %s (n=%d) / TEST %s (n=%d).' % (f(s_old['m']), f(sv2['m']), ci(sv2), f(s_tr['m']), s_tr['n'], f(s_te['m']), s_te['n']))
    E.append('4. Đối chứng dời vùng (100 bản): B v2 WR %s, R %s — dải WR %s–%s, R %s–%s ⇒ %s.' % (
        pct(g_v2['GỘP'][1]), f(g_v2['GỘP'][2]), pct(bW['GỘP'][1]), pct(bW['GỘP'][2]), f(bR['GỘP'][1]), f(bR['GỘP'][2]), VER['v2_dc1']))
    E.append('5. Vào ngẫu nhiên tại cùng mức: B v2 %s; lệnh chỉ-v2 %s.' % (VER['v2_dc2'], VER['only_dc2']))
    E.append('6. Từng loại vùng (vùng thắng): ' + ('; '.join('%s n=%d, WR %s, R %s, bỏ-một Δ %s' % (
        k, by_ztype[k]['n'], pct(by_ztype[k]['wr']), f(by_ztype[k]['m']), f(rs(RES['B-v2 − %s' % k])['m'] - sv2['m'])) for k in big) or 'không loại nào đủ 10 lệnh') +
        ('; chưa đủ mẫu: ' + ', '.join('%s (%d)' % (k, by_ztype[k]['n']) for k in small) if small else '') + '.')
    E.append('7. Công suất: chênh WR nhỏ nhất thấy được ≈ %s điểm ⇒ chưa thể nói gì về chênh dưới %s điểm.' % (f(100 * mdw, 0), f(100 * mdw, 0)))
    E.append('8. Kết luận 3.5: %s.%s' % (final, ' Chưa có lợi thế đo được trên %d phiên.' % days if not c3 else ''))
    open(OUT_EVAL, 'w', encoding='utf-8').write('\n'.join(E) + '\n')
    print('\n'.join(E))
    print('xong %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
