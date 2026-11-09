# -*- coding: utf-8 -*-
"""Setup B-v3 "Hấp thụ" = 8 loại vùng v2 + vùng S/R (đỉnh/đáy phiên trước + Vùng Canh Lệnh v5) — plan `plans/BENZO-B-v3-plan.md`.
Pipeline đo đầy đủ → report/RESULTS-B-v3.md + report/_eval_b_v3.txt (+ report/img/b_v3_*.png).

Chạy: python3 setup_b_v3.py      (chỉ file 90d GCZ26 — KHÔNG chạy file 2 năm; KHÔNG sửa kernel.py)

Mọi hằng số / ngưỡng / kỳ vọng dưới đây ĐĂNG KÝ TRƯỚC khi chạy lần đầu (commit riêng, trước khi có kết quả). Không chỉnh theo kết quả.
Quy ước đã chốt trước khi chạy (chỗ plan để mở):
  * "Lệnh chỉ-v3" = lệnh B-v3 mà idx KHÔNG có trong danh sách lệnh thô của B-v2 (so ở mức detect, cùng một P).
  * Tiêu chí 3.5-1 đọc ĐÚNG CHỮ plan v3: B-v3 trong dải 5–95 % ĐC1 về WR **hoặc** R TB ở TRAIN **hoặc** TEST (nới hơn B-v2 dùng "và");
    báo cáo in thêm biến thể "và" chỉ để tham khảo, KHÔNG dùng để quyết.
  * "Tệ đi" 3.5-2 (c): mất >= 3 lệnh v2 THẮNG do lệnh vùng mới chặn (one_at_a_time).
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC (plan mục 2.3) ------------------------------------
MAIN = (0.5, 3)                                   # θ 0,5 · N 3 (ô chính, như v2; không chọn theo kết quả)
RR = 3.0                                          # TP 3R
SHIFT_LO, SHIFT_HI, REPS, SHIFT_SEED = 3.0, 15.0, 100, 20261024   # ĐC1: cùng ma trận δ với BENZO-VCL / B-v2
CTRL_DRAWS = 200                                  # ĐC2: 200 lần rút
BOOT, BOOT_SEED = 10000, 0                        # KTC 95 % bootstrap
MIN_N = 10                                        # phán quyết chỉ khi >= 10 lệnh ở CẢ TRAIN và TEST
EXPECT_OLD = (11, 0.273, 0.00)                    # B cũ ô chính trên 90d
EXPECT_V2 = (25, 0.320, 0.19)                     # B v2 ô chính trên 90d
EXPECT_N_V3 = (40, 100)                           # kỳ vọng đăng ký trước cho n(B-v3)
BREAKEVEN_WR = 0.27                               # hoà vốn xấp xỉ ở 3R sau chi phí
VCL_WARM = 4                                      # khe VCL phải giữ cùng một eid >= 4 nến
EXPECT_TXT = [
    'n(B-v3): 25 → **40–100** (cạnh VCL bị chạm ~33 000 cặp (nến, vùng) mỗi vai trên 90d so với ~20 000 lượt chạm của 12 mức v2; trần 2/phiên chặn trên ở ~122 lệnh VCL; '
    'PDHL đóng góp 0–5 lệnh). n không tăng ≥ 1,6× ⇒ bộ lọc cụm/θ/chế độ là nút thắt, không phải vùng.',
    'WR ở 3R: **24–33 %**, trôi về hoà vốn ~27 %. **B-v3 ≈ dải ĐC1; lệnh chỉ-v3 ≈ ĐC2** (ba lần đo S/R trước — SR-KET-QUA, HVN 474 phiên, VCL 5 vòng — đều ra như vậy: '
    'vị trí vùng không mang thông tin, xác suất chạm chỉ phụ thuộc khoảng cách).',
    'Không ép: không chọn ô độ nhạy đẹp; không chọn biến thể "tâm"; TP 2R không chạy; không thêm bộ lọc giữa chừng.',
]

import json  # noqa: E402
import math  # noqa: E402
import time  # noqa: E402
import hashlib  # noqa: E402
from contextlib import contextmanager  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import kernel as K  # noqa: E402
import setup_b_hap_thu as SB  # noqa: E402
import zones_b_v2 as ZB  # noqa: E402
import zones_b_v3 as Z3  # noqa: E402
import setup_b_v2 as B2  # noqa: E402
import benzo_vcl as BV  # noqa: E402

D90 = SB.D90
REPORT = os.path.join(HERE, 'report')
IMG = os.path.join(REPORT, 'img')
OUT_MD = os.path.join(REPORT, 'RESULTS-B-v3.md')
OUT_EVAL = os.path.join(REPORT, '_eval_b_v3.txt')
FIX_OLD = os.path.join(REPORT, '_b_old_idx.json')
FIX_V2 = os.path.join(REPORT, '_b_v2_idx.json')
assert (SHIFT_LO, SHIFT_HI, REPS, SHIFT_SEED) == (BV.SHIFT_LO, BV.SHIFT_HI, BV.REPS, BV.SEED)
assert (BOOT, BOOT_SEED, MIN_N) == (BV.BOOT, BV.BOOT_SEED, BV.MIN_N)
assert MAIN == B2.MAIN and RR == B2.RR and VCL_WARM == Z3.VCL_WARM

ZONES_OLD, ZONES_V2, ZONES_V3 = Z3.ZONES_OLD, Z3.ZONES_V2, Z3.ZONES_V3
ZT8 = Z3.ZTYPES_V2
CONFIGS = [('B-cũ', ZONES_OLD), ('B-v2', ZONES_V2), ('B-v3', ZONES_V3),
           ('Chỉ-S/R', Z3.names_of3(Z3.ZTYPES_SR)), ('Chỉ-VCL', Z3.names_of3(('VCL',))), ('Chỉ-PDHL', Z3.names_of3(('PDHL',))),
           ('B-v2 + VCL', Z3.names_of3(ZT8 + ('VCL',))), ('B-v2 + PDHL', Z3.names_of3(ZT8 + ('PDHL',)))] + \
          [('B-v3 − %s' % k, tuple(nm for nm in ZONES_V3 if Z3.ZTYPE_OF_V3[nm] != k)) for k in ZT8]
CFG = dict(CONFIGS)
DC1_CFGS = ['B-v2', 'B-v3', 'Chỉ-S/R', 'B-v2 + VCL', 'B-v2 + PDHL']
GROUPS = BV.GROUPS
f, pct, nwr, ci, esc = B2.f, B2.pct, B2.nwr, B2.ci, B2.esc


# ------------------------------------------------------------------ dữ liệu
class Data3:
    def __init__(self):
        self.df = K.load_bars(D90 + '_bars.csv')
        assert not self.df['splice_jump'].any(), 'file 90d phải là MỘT hợp đồng (không có chỗ nối)'
        Z3.check_align(self.df)
        self.prof = K.build_profiles(self.df, D90 + '.csv')
        self.ctx = K._Ctx(self.df, self.prof)
        self.lev = ZB.session_table_b(self.df, self.prof, self.ctx)
        import lan_cham as LC
        self.cache_md5 = hashlib.md5(open(os.path.join(LC.CACHE, 'v5.pkl'), 'rb').read()).hexdigest()
        self.rec = BV.load_rec(self.df)
        self.slots = Z3.vcl_slots(self.rec, len(self.df))
        assert self.slots['K'] <= Z3.VCL_SLOTS_MAX
        self.extra3 = Z3.build_extra3(self.df, self.prof, self.ctx, self.lev, self.rec, self.slots)
        self.tab = Z3.zone_table3(self.extra3, self.df)
        self.P = SB.prepare(self.df, self.prof, self.extra3)
        self.zc = self.P['zc']
        self.sno = self.df['session_no'].to_numpy()
        st = K.session_table(self.df)
        st['split'] = np.where(st['session_id'].str[:10] <= K.CONST['split_train_end'], 'TRAIN', 'TEST')
        self.st = st
        self.clean = (~st['splice'].to_numpy()) & (~st['thin'].to_numpy()) & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
        self.days = int(self.clean.sum())
        self.days_split = {sp: int((self.clean & (st['split'] == sp).to_numpy()).sum()) for sp in ('TRAIN', 'TEST')}
        self.dsh = ZB.shift_matrix(int(self.sno.max()) + 1, REPS, SHIFT_LO, SHIFT_HI, SHIFT_SEED)
        self.recidx = self.rec.set_index(['bar', 'eid'])


def only_v3_mask(c_v3, raw_v2_idx):
    """Lệnh đã đóng của B-v3 mà idx KHÔNG có trong danh sách lệnh thô của B-v2."""
    return ~c_v3['idx'].isin(raw_v2_idx).to_numpy() if len(c_v3) else np.zeros(0, bool)


# ------------------------------------------------------------------ ĐC1 (dời)
def dc1_v3(D, reps):
    res = {nm: [] for nm in DC1_CFGS}
    res['chỉ-v3'] = []
    t0 = time.time()
    for k in range(reps):
        Pk = SB.prepare(D.df, D.prof, Z3.shifted3(D.extra3, D.zc, D.dsh[:, k], D.sno))
        ents, tt = {}, {}
        for nm in DC1_CFGS:
            ents[nm], tt[nm] = B2.run(Pk, CFG[nm])
            res[nm].append(B2.gstats(tt[nm]))
        c3 = B2.closed(tt['B-v3'])
        raw2 = {e['idx'] for e in ents['B-v2']}
        res['chỉ-v3'].append(B2.gstats(c3[only_v3_mask(c3, raw2)] if len(c3) else c3))
        if k == 2:
            res['_eta'] = (time.time() - t0) / 3 * reps
        if k % 10 == 9:
            print('  ĐC1 %d/%d %.0fs' % (k + 1, reps, time.time() - t0), flush=True)
    return res


def eta_dc1(D, probe=3):
    t0 = time.time()
    for k in range(probe):
        Pk = SB.prepare(D.df, D.prof, Z3.shifted3(D.extra3, D.zc, D.dsh[:, k], D.sno))
        for nm in DC1_CFGS:
            B2.run(Pk, CFG[nm])
    return (time.time() - t0) / probe


# ------------------------------------------------------------------ ĐC2 (vào ngẫu nhiên tại cùng loại mức)
def ctrl_zone(name):
    return 'VCL_R_ANY' if name.startswith('VCL_R') else 'VCL_S_ANY' if name.startswith('VCL_S') else name


def dc2_v3(D, t, draws=CTRL_DRAWS):
    c = B2.closed(t)
    if not len(c):
        return {}, {}
    recs = [dict(idx=int(x.idx), side=int(x.side), entry=float(x.entry), sl=float(x.sl), tp=float(x.tp), setup='B', zone=ctrl_zone(str(x.zone)))
            for x in c.itertuples()]
    grp = {int(x.idx): (x.split, x.thang) for x in c.itertuples()}
    zcols = pd.concat([D.zc, D.tab.set_index(D.zc.index)], axis=1)
    perR = {g: [] for g, _, _ in GROUPS}
    perW = {g: [] for g, _, _ in GROUPS}
    with B2._patched_map({nm: None for nm in D.tab.columns}):
        for sd in range(draws):
            ce = K.control_sample(D.df, zcols, D.P['modecode'], entries=recs, n_random=1, seed=sd)
            if not ce:
                continue
            cc = B2.closed(K.simulate(D.df, ce, one_at_a_time=False))
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


@contextmanager
def no_cap():
    old = SB.MAX_PER_ZONE_SESSION
    SB.MAX_PER_ZONE_SESSION = 10 ** 9
    try:
        yield
    finally:
        SB.MAX_PER_ZONE_SESSION = old


def plot_trade3(df, e, path, zlevels, bands, before=45, after=30):
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
    for lo_b, hi_b in bands:
        ax.axhspan(lo_b, hi_b, color='#4c78a8', alpha=0.15)
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
    ax.set_title('B-v3 %s %s r=%+.2f | vào %s VN | vùng %s Z=%.1f | entry %.1f SL %.1f TP %.1f' % (
        'BUY' if e['side'] > 0 else 'SELL', e['outcome'], e['r'], str(e['t_vn'])[:16], e['zone'], e['zprice'], e['entry'], e['sl'], e['tp']), fontsize=9)
    ax.set_ylim(seg['low'].min() - 0.8, seg['high'].max() + 0.8)
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


def vcl_info(D, zone, i, N=MAIN[1]):
    """Thông tin vùng VCL của lệnh (tại nến i−1): khe, loại khe K/N/F, độ rộng, mask nguồn, trôi cạnh trong cụm."""
    k = int(zone[5]) - 1
    eid = int(D.slots['eid'][k, i - 1])
    row = D.recidx.loc[(i - 1, eid)]
    z = D.P['Z'][zone]
    return dict(k=k + 1, eid=eid, slot=str(row['slot']), lo=float(D.slots['lo'][k, i - 1]), hi=float(D.slots['hi'][k, i - 1]),
                w=float(D.slots['hi'][k, i - 1] - D.slots['lo'][k, i - 1]), mask=int(row['mask']), drift=float(abs(z[i - 1] - z[i - N])))


MASK_BITS = {'A': 1, 'B': 2, 'C': 4, 'D': 8, 'E': 16}


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    D = Data3()
    df, P = D.df, D.P
    days = D.days
    L = []
    A = L.append
    # ---------- tái tạo gốc (điều kiện tiên quyết)
    ent, RES, FUN = {}, {}, {}
    for name, zones in CONFIGS:
        fn = {}
        ent[name], RES[name] = B2.run(P, zones, funnel=fn)
        FUN[name] = fn
    s_old, s_v2 = B2.rs(RES['B-cũ']), B2.rs(RES['B-v2'])
    fo, fv = json.load(open(FIX_OLD)), json.load(open(FIX_V2))
    ok_old = s_old['n'] == EXPECT_OLD[0] and abs(s_old['wr'] - EXPECT_OLD[1]) < 0.0015 and abs(s_old['m'] - EXPECT_OLD[2]) <= 0.005 \
        and [e['idx'] for e in ent['B-cũ']] == fo['idx']
    ok_v2 = s_v2['n'] == EXPECT_V2[0] and abs(s_v2['wr'] - EXPECT_V2[1]) < 0.0015 and abs(s_v2['m'] - EXPECT_V2[2]) <= 0.005 \
        and [[int(e['idx']), int(e['side']), float(e['entry']), float(e['sl']), float(e['tp']), e['zone']] for e in ent['B-v2']] == fv['entries_raw']
    if not (ok_old and ok_v2):
        raise SystemExit('KHÔNG tái tạo được mốc: B cũ %s (%d, %.3f, %.3f) · B v2 %s (%d, %.3f, %.3f) — dừng.' % (
            ok_old, s_old['n'], s_old['wr'], s_old['m'], ok_v2, s_v2['n'], s_v2['wr'], s_v2['m']))
    print('tái tạo B cũ + B v2 OK', flush=True)
    # tập con (assert)
    io, i2, i3 = ({e['idx']: e for e in ent[k]} for k in ('B-cũ', 'B-v2', 'B-v3'))
    assert set(io) <= set(i2) <= set(i3)
    for a_, b_ in ((io, i2), (i2, i3)):
        for i, e in a_.items():
            x = b_[i]
            assert (x['side'], x['entry'], x['sl'], x['tp'], x['zprice'], x['zone']) == (e['side'], e['entry'], e['sl'], e['tp'], e['zprice'], e['zone'])
    t_old, t_v2, t_v3 = RES['B-cũ'], RES['B-v2'], RES['B-v3']
    c_old, c_v2, c_v3 = B2.closed(t_old), B2.closed(t_v2), B2.closed(t_v3)
    raw2 = set(i2)
    m_only = only_v3_mask(c_v3, raw2)
    c_only, c_common = c_v3[m_only], c_v3[~m_only]
    lost = c_v2[~c_v2['idx'].isin(set(t_v3['idx'].tolist()))] if len(c_v2) else c_v2
    lost_w = int((lost['r'] > 0).sum()) if len(lost) else 0
    print('16 cấu hình %.0fs' % (time.time() - t0), flush=True)
    # ---------- ĐC2 (trước ĐC1 vì nhanh)
    DC2 = {'B-v3': dc2_v3(D, t_v3), 'Chỉ-S/R': dc2_v3(D, RES['Chỉ-S/R']), 'chỉ-v3': dc2_v3(D, c_only), 'B-v2 + VCL': dc2_v3(D, RES['B-v2 + VCL'])}
    print('ĐC2 %.0fs' % (time.time() - t0), flush=True)
    # ---------- ĐC1
    eta = eta_dc1(D) * REPS
    reps = REPS
    note_reps = ''
    if eta > 45 * 60:
        reps = 50
        note_reps = ('**Lưu ý (plan 3.9):** thời gian ước tính %.0f phút > 45 phút ⇒ ĐC1 chạy %d bản (ma trận δ lấy %d cột đầu) thay vì %d.' % (eta / 60, reps, reps, REPS))
    print('ĐC1 ước %.0f phút, chạy %d bản' % (eta / 60, reps), flush=True)
    R1 = dc1_v3(D, reps)
    R1.pop('_eta', None)
    print('ĐC1 %.0fs' % (time.time() - t0), flush=True)

    # ======================================================== báo cáo
    A('# RESULTS-B-v3 — Setup B "Hấp thụ" thêm vùng hỗ trợ / kháng cự (đỉnh/đáy phiên trước + Vùng Canh Lệnh v5) vào 8 loại vùng của B-v2')
    A('')
    A('Sinh bởi `setup_b_v3.py` (deterministic) theo `plans/BENZO-B-v3-plan.md`. **Chỉ file 90d GCZ26** `fp_GCZ26_XCEC_Time_20260723-20261021_90d` '
      '(một hợp đồng, `splice_jump.any() == False` ✔), %d nến M1, %d phiên sạch (TRAIN %d ≤ 2026-09-15, TEST %d). Giờ UTC (VN = UTC+7). '
      'Cấu hình duy nhất: θ 0,5 · N 3 · TP 3R · mono "ends" · biến thể "base" · không bias · mọi pha trừ OFF. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ SL; '
      '1 lệnh mở cùng lúc; tối đa 2 lệnh / (loại vùng, phiên). Cache VCL v5: md5 `%s` (căn hàng `check_align` ✔; %d khe; %d eid).' % (
          len(df), days, D.days_split['TRAIN'], D.days_split['TEST'], D.cache_md5, D.slots['K'], D.rec['eid'].nunique()))
    A('')
    A('## 0. Kỳ vọng đăng ký TRƯỚC khi chạy (plan 3.6, chép từ hằng số đã commit c0885f5)')
    A('')
    for x in EXPECT_TXT:
        A('- ' + x)
    A('')
    A('Tái tạo mốc (điều kiện tiên quyết): B cũ n = %d, WR %s, R TB %s, idx khớp `_b_old_idx.json` ✔; B v2 n = %d, WR %s, R TB %s, danh sách '
      '[idx, chiều, entry, SL, TP, vùng] khớp `_b_v2_idx.json` (ghi từ code CHƯA sửa) ✔.' % (s_old['n'], pct(s_old['wr']), f(s_old['m']), s_v2['n'], pct(s_v2['wr']), f(s_v2['m'])))
    A('')
    # ---------- 1. tập vùng
    A('## 1. Tập vùng S/R — có mặt, khoảng cách, trùng với vùng v2')
    A('')
    okb = P['okbar']
    A('| mức | số nến đo được chạm mức (ấm, \\|close − Z\\| ≤ 1 hoặc râu chạm) | trung vị \\|close − Z\\| (giá) |')
    A('|---|---|---|')
    for nm in ZONES_V3[2:]:
        z = P['Z'][nm]
        with np.errstate(invalid='ignore'):
            dd = np.abs(P['cl'] - z)[okb & ~np.isnan(z) & P['warm'][nm]]
        A('| %s | %d | %s |' % (nm, int((P['touch'][nm] & okb & P['warm'][nm]).sum()), f(float(np.median(dd)), 1) if len(dd) else '–'))
    A('')
    rec = D.rec
    sl = D.slots
    life = rec.groupby('eid').size()
    wid = (rec['hi'] - rec['lo']).to_numpy()
    drift = []
    for k in range(sl['K']):
        e_ = sl['eid'][k]
        lo_, hi_ = sl['lo'][k], sl['hi'][k]
        same = (e_[1:] == e_[:-1]) & (e_[1:] >= 0)
        drift.append(np.abs(lo_[1:] - lo_[:-1])[same])
    drift = np.concatenate(drift)
    A('- VCL: %d eid, đồng thời tối đa %d (khe cần %d ≤ %d ✔); tuổi thọ trung vị %s nến; độ rộng trung vị %s giá; cạnh `lo` trôi trong cùng eid: trung vị %s, p90 %s giá/nến.' % (
        rec['eid'].nunique(), int(rec.groupby('bar').size().max()), sl['K'], Z3.VCL_SLOTS_MAX, f(float(life.median()), 0), f(float(np.median(wid))),
        f(float(np.median(drift))), f(float(np.quantile(drift, .9)))))
    pdh = P['Z']['PDH']
    cl_snos = [int(s) for s in D.st.index[D.clean]]
    pd_have = sum(1 for s in cl_snos if not np.isnan(pdh[int(D.st['start_pos'].loc[s])]))
    A('- PDH/PDL: có ở %d / %d phiên sạch (phiên đầu file không có phiên trước). Phiên 2026-07-29 dựng trên phiên thin 07-28 — như VAH/VAL/POC v2, ghi chú, không sửa kernel.' % (pd_have, len(cl_snos)))
    ov = Z3.overlap3(P, ent['B-v3'], D.extra3)
    dist = ov['dist'][~np.isnan(ov['dist'])]
    A('- Trùng với mức v2 (mô tả, không lọc): tỉ lệ nến chạm cạnh VCL (ấm) mà cũng nằm ≤ 1 giá từ một mức v2 = **%s** (%d nến chạm); với %d lệnh thô VCL/PDHL: '
      '|Z − mức v2 gần nhất| trung vị %s giá (p25 %s, p75 %s).' % (
          pct(ov['frac_touch_near_v2']), ov['n_touch'], len(dist), f(float(np.median(dist)), 1) if len(dist) else '–',
          f(float(np.quantile(dist, .25)), 1) if len(dist) else '–', f(float(np.quantile(dist, .75)), 1) if len(dist) else '–'))
    A('')
    # ---------- 2. công suất
    n2, n3 = s_v2['n'], B2.rs(t_v3)['n']
    sdR = float(c_v3['r'].std(ddof=1)) if len(c_v3) > 1 else np.nan
    mdw = 2.8 * math.sqrt(.27 * .73) * math.sqrt(1 / max(n2, 1) + 1 / max(n3, 1))
    mdr = 2.8 * sdR * math.sqrt(1 / max(n2, 1) + 1 / max(n3, 1)) if sdR == sdR else np.nan
    A('## 2. Công suất thống kê (in TRƯỚC bảng chính — plan 3.3)')
    A('')
    A('- Sai số WR ≈ √(p(1−p)/n), p = 0,27: n = %d ⇒ ±%s điểm; n = %d ⇒ ±%s điểm.' % (n2, f(100 * math.sqrt(.27 * .73 / max(n2, 1)), 1), n3, f(100 * math.sqrt(.27 * .73 / max(n3, 1)), 1)))
    A('- Chênh WR nhỏ nhất phát hiện được (80 %%, hai phía) giữa B-v2 (n=%d) và B-v3 (n=%d): ≈ **%s điểm**; chênh R TB nhỏ nhất ≈ **%sR** (σ_R = %s). '
      '*So WR v2 ↔ v3 trực tiếp gần như vô nghĩa; phán quyết dựa vào đối chứng và nhóm lệnh chỉ-v3.*' % (n2, n3, f(100 * mdw, 0), f(mdr), f(sdR)))
    A('')
    # ---------- 3. bảng chính
    A('## 3. Bảng chính — 16 cấu hình (plan 3.1)')
    A('')
    A('n = lệnh đã đóng; lệnh/ngày chia %d phiên sạch; KTC = khoảng tin cậy 95 %% bootstrap (10 000, seed 0) của R TB. Hàng 1–3 liền nhau, WR in đậm.' % days)
    A('')
    A('| cấu hình | n | lệnh/ngày | **WR** | R TB | KTC 95 % | kỳ vọng giá/lệnh | tổng R | chuỗi thua |')
    A('|---|---|---|---|---|---|---|---|---|')
    for name, _ in CONFIGS:
        t = RES[name]
        s = B2.rs(t)
        k = K._stats(t) if len(t) else dict(exp_pts=np.nan, sum_r=0.0, max_loss_streak=0)
        A('| %s | %d | %s | **%s** | %s | %s | %s | %s | %d |' % (name, s['n'], f(s['n'] / days), pct(s['wr']), f(s['m']), ci(s), f(k['exp_pts']), f(k['sum_r'], 1), k['max_loss_streak']))
        if name == 'B-v3':
            A('| | | | | | | | | |')
    A('')
    A('Theo nửa và tháng (`n · WR · R TB`; T8 gồm 29–31/7):')
    A('')
    A('| cấu hình | TRAIN | TEST | T8 | T9 | T10 |')
    A('|---|---|---|---|---|---|')
    for name, _ in CONFIGS:
        c = B2.closed(RES[name])
        row = [nwr(BV.rstat(c[c[col] == val]['r'].to_numpy(float) if len(c) else [])) for col, val in (('split', 'TRAIN'), ('split', 'TEST'), ('thang', 'T8'), ('thang', 'T9'), ('thang', 'T10'))]
        A('| %s | %s |' % (name, ' | '.join(row)))
    A('')
    A('Theo pha và chiều (`n · WR · R TB`):')
    A('')
    A('| cấu hình | A | EU | US | BUY | SELL |')
    A('|---|---|---|---|---|---|')
    for name, _ in CONFIGS:
        c = B2.closed(RES[name])
        row = [nwr(BV.rstat(c[c[col] == val]['r'].to_numpy(float) if len(c) else [])) for col, val in (('phase', 'A'), ('phase', 'EU'), ('phase', 'US'), ('side', 1), ('side', -1))]
        A('| %s | %s |' % (name, ' | '.join(row)))
    A('')
    # ---------- 4. tách đóng góp
    A('## 4. Tách đóng góp ở mức LỆNH (plan 3.2)')
    A('')
    A('Chuỗi tập con kiểm bằng assert: lệnh thô B-cũ ⊆ B-v2 ⊆ B-v3, cùng chiều/entry/SL/TP/Z/vùng thắng ✔ (%d ⊆ %d ⊆ %d lệnh thô).' % (len(ent['B-cũ']), len(ent['B-v2']), len(ent['B-v3'])))
    A('')
    A('| nhóm | n · WR · R TB | KTC 95 % | TRAIN | TEST |')
    A('|---|---|---|---|---|')
    for lab, c in (('Lệnh chung v2 ∩ v3', c_common), ('**Lệnh chỉ-v3** (nhóm quyết định)', c_only), ('Lệnh v2 bị MẤT ở v3 (số liệu trong bản v2)', lost)):
        s = BV.rstat(c['r'].to_numpy(float) if len(c) else [])
        tr_ = BV.rstat(c[c['split'] == 'TRAIN']['r'].to_numpy(float) if len(c) else [])
        te_ = BV.rstat(c[c['split'] == 'TEST']['r'].to_numpy(float) if len(c) else [])
        A('| %s | %s | %s | %s | %s |' % (lab, nwr(s), ci(s), nwr(tr_), nwr(te_)))
    A('')
    A('Lệnh v2 bị mất do `one_at_a_time` (lệnh vùng mới mở trước chặn): **%d** lệnh, trong đó **%d** lệnh thắng.' % (len(lost), lost_w))
    A('')
    A('### Theo loại vùng (lệnh B-v3). Nhóm n < 10 chỉ để đọc số, không bình luận.')
    A('')
    A('*Vùng thắng* = ztype ghi trên lệnh (thứ tự ưu tiên). *Bất kỳ vùng* = lệnh tính cho mọi loại có trong `zones_hit` (tổng > n). *Chỉ-v3* = nhóm lệnh chỉ-v3 theo vùng thắng / bất kỳ vùng.')
    A('')
    A('| loại | vùng thắng: n · WR · R TB | bất kỳ vùng: n · WR · R TB | chỉ-v3, vùng thắng | chỉ-v3, bất kỳ vùng |')
    A('|---|---|---|---|---|')
    zt = c_v3['ztype'].to_numpy() if len(c_v3) else np.array([])
    anyz = [set(Z3.ZTYPE_OF_V3[x] for x in h) for h in c_v3['zones_hit']] if len(c_v3) else []
    rv3 = c_v3['r'].to_numpy(float) if len(c_v3) else np.zeros(0)
    by_ztype = {}
    for k in ZT8 + Z3.ZTYPES_SR:
        sw = BV.rstat(rv3[zt == k])
        sa = BV.rstat(rv3[np.array([k in h for h in anyz], bool)] if len(anyz) else [])
        mo = m_only if len(m_only) else np.zeros(0, bool)
        swo = BV.rstat(rv3[(zt == k) & mo]) if len(rv3) else BV.rstat([])
        sao = BV.rstat(rv3[np.array([k in h for h in anyz], bool) & mo] if len(anyz) else [])
        by_ztype[k] = sw
        A('| %s | %s | %s | %s | %s |' % (k, nwr(sw), nwr(sa), nwr(swo), nwr(sao)))
    A('')
    fpd = {}
    SB.detect(P, MAIN[0], MAIN[1], zones=('PDH', 'PDL'), funnel=fpd, rr=RR)
    A('Phễu RIÊNG của PDH + PDL (hai chiều): ' + '; '.join('%s: %d' % (esc(k), fpd[k]) for k in sorted(fpd)) + '. Số lệnh PDHL cuối cùng = %d.' % by_ztype['PDHL']['n'])
    A('')
    A('### Lệnh VCL — mô tả (chỉ mô tả; n < 10 chỉ in số)')
    A('')
    vc = c_v3[c_v3['ztype'] == 'VCL'] if len(c_v3) else c_v3
    info = [vcl_info(D, x.zone, int(x.idx)) for x in vc.itertuples()]
    vc = vc.assign(slotk=[i['slot'] for i in info], w=[i['w'] for i in info], drift=[i['drift'] for i in info])
    rows = []
    for lab, m in (('SELL tại cạnh dưới (VCL_R)', vc['side'] == -1), ('BUY tại cạnh trên (VCL_S)', vc['side'] == 1),
                   ('khe loại K (gần)', vc['slotk'] == 'K'), ('khe loại N (gần-trung)', vc['slotk'] == 'N'), ('khe loại F (xa)', vc['slotk'] == 'F'),
                   ('độ rộng ≤ 2,5 giá', vc['w'] <= 2.5), ('độ rộng > 2,5 giá', vc['w'] > 2.5)):
        c = vc[m.to_numpy()] if len(vc) else vc
        rows.append((lab, nwr(BV.rstat(c['r'].to_numpy(float) if len(c) else []))))
    A('| nhóm lệnh VCL | n · WR · R TB |')
    A('|---|---|')
    for lab, v in rows:
        A('| %s | %s |' % (lab, v))
    A('')
    nm_ = np.array([i['mask'] for i in info]) if info else np.zeros(0, int)
    A('Nguồn trong `mask` của vùng VCL tại lệnh (số lệnh có nguồn đó): ' + ', '.join('%s=%d' % (k, int(((nm_ & b) > 0).sum())) for k, b in MASK_BITS.items()) + '.')
    dr = np.array([i['drift'] for i in info]) if info else np.zeros(0)
    A('Rủi ro 5.5 — cạnh trôi trong cụm: %d / %d lệnh VCL có \\|Z(i−1) − Z(i−N)\\| > 0,5 giá (%s). Chỉ mô tả.' % (int((dr > 0.5).sum()), len(dr), pct((dr > 0.5).mean()) if len(dr) else '–'))
    A('')
    A('### Phễu lọc (số ứng viên qua từng bước, cộng mọi mức và hai chiều; chưa gồm trần 2 lệnh / one-at-a-time)')
    A('')
    A('| bước | B-v2 | B-v3 |')
    A('|---|---|---|')
    for k in sorted(set(FUN['B-v2']) | set(FUN['B-v3'])):
        A('| %s | %d | %d |' % (esc(k), FUN['B-v2'].get(k, 0), FUN['B-v3'].get(k, 0)))
    A('')
    with no_cap():
        e_nc = SB.detect(P, MAIN[0], MAIN[1], zones=ZONES_V3, rr=RR)
    e_c = ent['B-v3']
    cnt_nc, cnt_c = pd.Series([e['ztype'] for e in e_nc]).value_counts(), pd.Series([e['ztype'] for e in e_c]).value_counts()
    A('Lệnh thô bị trần 2/(loại, phiên) cắt (trước one_at_a_time; chạy `detect` thêm một lần với trần = 10⁹ chỉ để đếm): tổng %d → %d. Theo loại (không trần → có trần): %s.' % (
        len(e_nc), len(e_c), '; '.join('%s %d → %d' % (k, int(cnt_nc.get(k, 0)), int(cnt_c.get(k, 0))) for k in cnt_nc.index)))
    A('')
    # ---------- 5. đối chứng
    A('## 5. Đối chứng (plan 3.4)')
    A('')
    A('**ĐC1 — dời bản đồ vùng:** mọi mức của phiên (12 v2 + PDH/PDL + 14 cạnh VCL; VWAP động cộng hằng δ) dời cùng δ[phiên, bản], |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, '
      '%d bản, seed %d (ma trận y hệt BENZO-VCL / B-v2). `warm` và `mdirs` KHÔNG đổi (danh tính vùng, không phải vị trí). Chạy NGUYÊN `prepare` + `detect` + `simulate` ⇒ lệnh dời cũng chạm '
      'vùng (dời) ≤ 1 giá, cùng cơ chế move → cụm → nến xác nhận; chỉ VỊ TRÍ khác. Nhóm "chỉ-v3" dời = lệnh B-v3 dời mà idx không có trong lệnh thô B-v2 dời cùng bản. '
      'Bộ lọc chế độ / VA Âu / IB không dời.' % (reps, SHIFT_SEED))
    A('')
    if note_reps:
        A(note_reps)
        A('')
    A('⚠ **Bẫy n của ĐC1:** dời làm đổi phân bố khoảng cách vùng↔giá theo thời gian (VCL vốn chọn vùng SÁT giá), nên **số lệnh n của bản dời CHỈ để tham khảo, KHÔNG dùng phán quyết**; '
      'phán quyết chỉ trên WR và R TB mỗi lệnh (điều kiện theo chạm ⇒ khớp khoảng cách). Không diễn giải "n thật > n dời" thành "vùng thật hút giá".')
    A('')
    A('**ĐC2 — vào ngẫu nhiên tại cùng loại mức:** `kernel.control_sample` (không sửa, qua `_patched_map`), mỗi lệnh thật rút 1 nến chạm ĐÚNG mức đó '
      '(lệnh VCL: `VCL_R_ANY`/`VCL_S_ANY` = chạm một cạnh kháng cự/hỗ trợ VCL ấm bất kỳ), cùng chế độ, cùng chiều, cùng R:R, SL = râu nến + 0,3; %d lần.' % CTRL_DRAWS)
    A('')
    A('**Ngưỡng "khác đối chứng"** (nguyên PLAN-LAN-CHAM mục 5, `benzo_vcl.verdict`): ngoài dải 5–95 %% ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số ở cả hai; '
      'chỉ áp dụng khi nhóm có ≥ %d lệnh ở CẢ TRAIN và TEST. Số phép so có phán quyết (đăng ký trước) = 9; ở mức 5 %% kỳ vọng ~0,45 ô "vượt" do ngẫu nhiên.' % MIN_N)
    A('')
    A('### ĐC1 — thật vs dải bản dời (`thật | TB dời [5 % ; 95 %]`)')
    A('')
    A('| nhóm | đo | GỘP | TRAIN | TEST | T8 | T9 | T10 |')
    A('|---|---|---|---|---|---|---|---|')
    real_g = {'B-v2': B2.gstats(t_v2), 'B-v3': B2.gstats(t_v3), 'chỉ-v3': B2.gstats(c_only), 'Chỉ-S/R': B2.gstats(RES['Chỉ-S/R']),
              'B-v2 + VCL': B2.gstats(RES['B-v2 + VCL']), 'B-v2 + PDHL': B2.gstats(RES['B-v2 + PDHL'])}
    for nm in ('B-v2', 'B-v3', 'chỉ-v3', 'Chỉ-S/R', 'B-v2 + VCL', 'B-v2 + PDHL'):
        for wi, lab, fmt in ((0, 'n (chỉ tham khảo)', lambda x: f(x, 0) if x == x else '–'), (1, 'WR', pct), (2, 'R TB', f)):
            bd = B2.bands_of(R1[nm], wi)
            cells = []
            for g in ('GỘP', 'TRAIN', 'TEST', 'T8', 'T9', 'T10'):
                b = bd[g]
                cells.append('%s \\| %s [%s ; %s]' % (fmt(real_g[nm][g][wi]), fmt(b[0]), fmt(b[1]), fmt(b[2])))
            A('| %s | %s | %s |' % (nm, lab, ' | '.join(cells)))
    A('')
    A('### Phán quyết theo ngưỡng — 9 phép so đăng ký trước (R TB)')
    A('')
    A('| # | phép so | n TRAIN / TEST | phán quyết |')
    A('|---|---|---|---|')
    VER, rows9 = {}, []

    def add(key, lab, csel, bandsR):
        cc, okc = B2.cmp_vs(csel, bandsR)
        VER[key] = BV.verdict(cc, okc)
        rows9.append((lab, cc, VER[key]))
    add('v3_dc1', 'B-v3 vs ĐC1 (dời)', c_v3, B2.bands_of(R1['B-v3'], 2))
    add('v3_dc2', 'B-v3 vs ĐC2 (ngẫu nhiên tại loại mức)', c_v3, DC2['B-v3'][0])
    add('only_dc1', 'chỉ-v3 vs ĐC1 (nhóm chỉ-v3 dời)', c_only, B2.bands_of(R1['chỉ-v3'], 2))
    add('only_dc2', 'chỉ-v3 vs ĐC2', c_only, DC2['chỉ-v3'][0])
    add('sr_dc1', 'Chỉ-S/R vs ĐC1', B2.closed(RES['Chỉ-S/R']), B2.bands_of(R1['Chỉ-S/R'], 2))
    add('sr_dc2', 'Chỉ-S/R vs ĐC2', B2.closed(RES['Chỉ-S/R']), DC2['Chỉ-S/R'][0])
    add('v2vcl_dc1', 'B-v2 + VCL vs ĐC1', B2.closed(RES['B-v2 + VCL']), B2.bands_of(R1['B-v2 + VCL'], 2))
    add('v2pd_dc1', 'B-v2 + PDHL vs ĐC1', B2.closed(RES['B-v2 + PDHL']), B2.bands_of(R1['B-v2 + PDHL'], 2))
    add('v2vcl_dc2', 'B-v2 + VCL vs ĐC2', B2.closed(RES['B-v2 + VCL']), DC2['B-v2 + VCL'][0])
    for j, (lab, cc, v) in enumerate(rows9, 1):
        A('| %d | %s | %d / %d | %s |' % (j, lab, cc['TRAIN'][2], cc['TEST'][2], esc(v)))
    A('')
    n_out = sum(1 for _, _, v in rows9 if v.startswith('KHÁC'))
    A('Số ô "KHÁC đối chứng": **%d / 9** (ở mức 5 %% kỳ vọng ~0,45 ô do ngẫu nhiên; một ô lẻ không phải bằng chứng).' % n_out)
    A('')
    A('### ĐC2 chi tiết (`R TB thật | TB đối chứng [5 % ; 95 %]`; WR thật / WR đối chứng GỘP)')
    A('')
    A('| nhóm | GỘP | TRAIN | TEST | WR thật / WR đối chứng (GỘP) |')
    A('|---|---|---|---|---|')
    for nm, c in (('B-v3', c_v3), ('chỉ-v3', c_only), ('Chỉ-S/R', B2.closed(RES['Chỉ-S/R'])), ('B-v2 + VCL', B2.closed(RES['B-v2 + VCL']))):
        bR, bW = DC2[nm]
        cells = []
        for g in ('GỘP', 'TRAIN', 'TEST'):
            sub = c if g == 'GỘP' else c[c['split'] == g]
            b = bR.get(g, (np.nan,) * 3)
            cells.append('%s \\| %s [%s ; %s]' % (f(sub['r'].mean() if len(sub) else np.nan), f(b[0]), f(b[1]), f(b[2])))
        A('| %s | %s | %s / %s |' % (nm, ' | '.join(cells), pct((c['r'] > 0).mean() if len(c) else np.nan), pct(bW.get('GỘP', (np.nan,))[0])))
    A('')
    # ---------- 6. tiêu chí
    A('## 6. Phán quyết theo tiêu chí đăng ký trước (plan 3.5)')
    A('')
    sv3 = B2.rs(t_v3)
    g_v3, g_only = B2.gstats(t_v3), B2.gstats(c_only)
    bW, bR = B2.bands_of(R1['B-v3'], 1), B2.bands_of(R1['B-v3'], 2)

    def inb(val, b):
        return val == val and b[1] <= val <= b[2]
    in_tr_or = inb(g_v3['TRAIN'][1], bW['TRAIN']) or inb(g_v3['TRAIN'][2], bR['TRAIN'])
    in_te_or = inb(g_v3['TEST'][1], bW['TEST']) or inb(g_v3['TEST'][2], bR['TEST'])
    in_tr_and = inb(g_v3['TRAIN'][1], bW['TRAIN']) and inb(g_v3['TRAIN'][2], bR['TRAIN'])
    in_te_and = inb(g_v3['TEST'][1], bW['TEST']) and inb(g_v3['TEST'][2], bR['TEST'])
    s_only = BV.rstat(c_only['r'].to_numpy(float) if len(c_only) else [])
    wr_only = s_only['wr']
    se_only = math.sqrt(wr_only * (1 - wr_only) / s_only['n']) if s_only['n'] else np.nan
    wr_low = wr_only == wr_only and wr_only <= BREAKEVEN_WR + se_only
    c1 = (sv3['n'] > s_v2['n']) and (in_tr_or or in_te_or or wr_low)
    c1_and = (sv3['n'] > s_v2['n']) and (in_tr_and or in_te_and or wr_low)
    b1o, b2o = B2.bands_of(R1['chỉ-v3'], 2), DC2['chỉ-v3'][0]
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
    ca = sv3['n'] >= EXPECT_N_V3[0] and g_v3['TRAIN'][0] >= MIN_N and g_v3['TEST'][0] >= MIN_N
    cb = (g_v3['TRAIN'][2] > 0) and (g_v3['TEST'][2] > 0)
    wr_v2 = s_v2['wr']
    cc_ = all(g_only[g][1] >= wr_v2 and g_only[g][2] > 0 for g in ('TRAIN', 'TEST'))
    cd = VER['v3_dc1'].startswith('KHÁC đối chứng ▲') and VER['v3_dc2'].startswith('KHÁC đối chứng ▲') and \
        VER['only_dc1'].startswith('KHÁC đối chứng ▲') and VER['only_dc2'].startswith('KHÁC đối chứng ▲')
    bad_types = []
    for k, other in (('VCL', 'B-v2 + PDHL'), ('PDHL', 'B-v2 + VCL')):
        sk = by_ztype[k]
        if sk['n'] >= MIN_N and sk['m'] < -0.5 and B2.rs(RES[other])['m'] - sv3['m'] > 2 * sv3['se']:
            bad_types.append(k)
    ce = not bad_types
    c3 = ca and cb and cc_ and cd and ce
    yn = lambda b: 'ĐẠT' if b else 'không'  # noqa: E731
    A('| tiêu chí | điều kiện | kết quả |')
    A('|---|---|---|')
    A('| 1. "Chỉ tăng số lượng" | n(B-v3)=%d > n(B-v2)=%d; B-v3 trong dải ĐC1 về WR hoặc R TB ở TRAIN (%s) hoặc TEST (%s) [biến thể "và" chỉ tham khảo: TRAIN %s, TEST %s ⇒ %s]; '
      'hoặc chỉ-v3 WR %s ≤ 27 %% + 1 sai số (%s: %s) | **%s** |' % (
          sv3['n'], s_v2['n'], yn(in_tr_or), yn(in_te_or), yn(in_tr_and), yn(in_te_and), yn(c1_and), pct(wr_only), pct(BREAKEVEN_WR + se_only) if se_only == se_only else '–', yn(wr_low), yn(c1)))
    A('| 2. "Tệ đi" | chỉ-v3 (n TRAIN %d / TEST %d, cần ≥ 10) R TB < mốc 5 %% ĐC1 hoặc < ĐC2 − 2 sai số ở CẢ hai nửa: %s; hoặc mất ≥ 3 lệnh v2 thắng do chặn (mất %d lệnh thắng) | **%s** |' % (
        g_only['TRAIN'][0], g_only['TEST'][0], yn(c2a) if n_only_ok else 'không áp dụng (n nhỏ)', lost_w, yn(c2)))
    A('| 3. "Cải thiện thật" | (a) n ≥ %d, ≥ 10 mỗi nửa: %s · (b) R TB > 0 cả TRAIN (%s) và TEST (%s): %s · (c) chỉ-v3 WR ≥ WR B-v2 và R TB > 0 cả hai nửa: %s · '
      '(d) B-v3 và chỉ-v3 vượt ĐC1 và ĐC2 (▲): %s · (e) không loại vùng kéo xuống: %s | **%s** |' % (
          EXPECT_N_V3[0], yn(ca), f(g_v3['TRAIN'][2]), f(g_v3['TEST'][2]), yn(cb), yn(cc_), yn(cd), yn(ce) + ((' (' + ', '.join(bad_types) + ')') if bad_types else ''), yn(c3)))
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
        A('*"Vùng S/R cho thêm lệnh nhưng không cho thêm lợi thế đo được; B v3 ≈ B v2 chạy ở nhiều chỗ hơn."*')
    if c1 and c2:
        A('')
        A('Lưu ý: tiêu chí 2 ("tệ đi") CŨNG đạt — xem bảng trên; không ship.')
    if not c3:
        A('')
        A('Không đạt 3.5-3(d) ⇒ **chưa có lợi thế đo được trên %d phiên**. Với %d phiên, (d) gần như chỉ đạt khi hiệu ≥ ~0,5R.' % (days, days))
    A('')
    A('**So với kỳ vọng đăng ký trước:** n = %d (kỳ vọng %d–%d: %s; tăng %s× so với B v2, %s× so với B cũ); WR %s (kỳ vọng 24–33 %%: %s); B-v3 %s dải ĐC1 (R TB gộp).' % (
        sv3['n'], EXPECT_N_V3[0], EXPECT_N_V3[1], 'trong' if EXPECT_N_V3[0] <= sv3['n'] <= EXPECT_N_V3[1] else 'NGOÀI', f(sv3['n'] / max(s_v2['n'], 1), 1),
        f(sv3['n'] / max(s_old['n'], 1), 1), pct(sv3['wr']), 'trong' if 0.24 <= sv3['wr'] <= 0.33 else 'NGOÀI', 'nằm trong' if inb(g_v3['GỘP'][2], bR['GỘP']) else 'nằm NGOÀI'))
    A('')
    A('**Đọc kết quả cho đúng:** các con số theo loại vùng (mục 3–4), theo nửa/tháng và nhóm chỉ-v3 dựa trên ít lệnh; KTC 95 % của R TB cần xem cột KTC trước khi nói "tốt hơn / tệ hơn". '
      'Không được viết "S/R của VCL giúp B tốt hơn" nếu không có ô "KHÁC đối chứng ▲" ở cả hai đối chứng.')
    A('')
    # ---------- 7. phụ lục
    A('## 7. Phụ lục — chỉ in, KHÔNG phán quyết, KHÔNG chọn (plan 3.7)')
    A('')
    A('### 7.1 Độ nhạy θ × N của B-v3 (`n · WR · R TB`)')
    A('')
    A('| θ \\ N | ' + ' | '.join(str(x) for x in SB.NS) + ' |')
    A('|---|' + '---|' * len(SB.NS))
    for th in SB.THETAS:
        A('| %s | %s |' % (f(th, 1), ' | '.join(nwr(B2.rs(B2.run(P, ZONES_V3, th, N_)[1])) for N_ in SB.NS)))
    A('')
    mid = Z3.vcl_mid_extra(D.slots)
    ex_mid = {nm: D.extra3[nm] for nm in ZB.EXTRA_NAMES}
    ex_mid.update(mid)
    Pm = SB.prepare(df, D.prof, ex_mid)
    t_mid = B2.run(Pm, ZONES_V2 + Z3.M_NAMES)[1]
    c_mid = B2.closed(t_mid)
    A('### 7.2 Biến thể "VCL tâm hai chiều" (v2 + VCL_M1..7, tâm = (lo+hi)/2)')
    A('')
    A('| cấu hình | n · WR · R TB | TRAIN | TEST |')
    A('|---|---|---|---|')
    A('| B-v2 + VCL tâm | %s | %s | %s |' % (nwr(B2.rs(t_mid)), nwr(BV.rstat(c_mid[c_mid['split'] == 'TRAIN']['r'].to_numpy(float) if len(c_mid) else [])),
                                          nwr(BV.rstat(c_mid[c_mid['split'] == 'TEST']['r'].to_numpy(float) if len(c_mid) else []))))
    A('')
    A('### 7.3 Lệnh chỉ-v3 theo pha')
    A('')
    A('| pha | n · WR · R TB |')
    A('|---|---|')
    for ph in ('A', 'EU', 'US'):
        A('| %s | %s |' % (ph, nwr(BV.rstat(c_only[c_only['phase'] == ph]['r'].to_numpy(float) if len(c_only) else []))))
    A('')
    # ---------- 8. ví dụ
    A('## 8. Ví dụ để soi chart — nhóm chỉ-v3 (5 thắng + 5 thua, cách đều theo thời gian)')
    A('')
    A('| UTC | VN | chiều | loại vùng | Z | dải VCL [lo, hi] | zones_hit | move (giá) | \\|Δ_CF\\| / max | entry | SL | TP | kết quả | R | ảnh |')
    A('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    os.makedirs(IMG, exist_ok=True)
    zl_names = ZONES_V2[2:] + ('PDH', 'PDL')
    for lab, g in (('THẮNG', c_only[c_only['r'] > 0]), ('THUA', c_only[c_only['r'] <= 0])):
        g = g.iloc[np.unique(np.linspace(0, len(g) - 1, 5).astype(int))] if len(g) > 5 else g
        for x in g.to_dict('records'):
            mv, ratio = B2.cf_ratio(P, x)
            i = int(x['idx'])
            fn = 'b_v3_%s_%s_%s.png' % (x['ztype'], str(x['t_utc'])[:16].replace(':', '').replace(' ', '_'), x['outcome'])
            zl = {nm: P['Z'][nm][i] for nm in zl_names}
            zl['VWAP_W'], zl['VWAP_D'] = P['Z']['VWAP_W'][i], P['Z']['VWAP_D'][i]
            bands, bandtxt = [], '–'
            if x['ztype'] == 'VCL':
                inf = vcl_info(D, x['zone'], i)
                bands, bandtxt = [(inf['lo'], inf['hi'])], '[%s, %s]' % (f(inf['lo'], 2), f(inf['hi'], 2))
                zl[x['zone']] = x['zprice']
            plot_trade3(df, x, os.path.join(IMG, fn), zl, bands)
            A('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | [ảnh](img/%s) |' % (
                str(x['t_utc'])[:16], str(x['t_vn'])[:16], 'BUY' if x['side'] > 0 else 'SELL', x['ztype'], f(x['zprice'], 1), bandtxt, ', '.join(x['zones_hit']),
                f(mv, 1), f(ratio), f(x['entry'], 1), f(x['sl'], 1), f(x['tp'], 1), x['outcome'], f(x['r']), fn))
    A('')
    A('## 9. Rủi ro / điểm mơ hồ (plan mục 5) — báo lại')
    A('')
    A('1. Kết quả ≈ đối chứng là khả năng cao nhất; câu kết luận bám 3.5-1, không viết "S/R của VCL giúp B tốt hơn".')
    A('2. VCL áp đảo nhóm chỉ-v3: số lệnh chỉ-v3 theo loại ở mục 4 (PDHL nhỏ ⇒ hàng "B-v2 + PDHL" dễ "không áp dụng").')
    A('3. Trần 2/(loại, phiên) chung cho 14 cạnh VCL cắt nhiều lệnh thô (số liệu ở mục 4); lệnh giữ = 2 lệnh SỚM nhất phiên. Luật đã chốt, không nới.')
    A('4. Bẫy n của ĐC1: chỉ phán quyết trên WR / R TB mỗi lệnh (mục 5).')
    A('5. Cạnh trôi trong eid: tỉ lệ lệnh VCL có cạnh trôi > 0,5 giá trong cụm in ở mục 4; chỉ mô tả.')
    A('6. Cache VCL = bản v5 trên 90d, md5 ghi ở đầu báo cáo (không phải chạy lại engine).')
    A('7. Không gặp ca chưa phủ: K_VCL = %d ≤ 7, không eid nào xuất hiện lại sau khi biến mất (assert trong `vcl_slots`), căn hàng khớp, PDH/PDL cố định cả phiên.' % D.slots['K'])
    A('8. Không chạy file 2 năm; C# (`BenzoDetectors.cs`) KHÔNG đụng — chỉ port khi đạt 3.5-3 và người học duyệt số.')
    A('9. Hai commit code/test đã làm tròn: code vùng + 12 test nằm trong commit 77486d8 (bị quét chung vào commit của tiến trình khác), hằng số đăng ký ở c0885f5.')
    A('')
    A('(Thời gian chạy: %.0f giây.)' % (time.time() - t0))
    open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')

    # ---------- báo cáo ngắn (đúng MỘT bảng)
    def row(lab, t, bold=False):
        s = B2.rs(t) if not isinstance(t, dict) else t
        w = pct(s['wr'])
        return '| %s | %d (%s) | %s | %s |' % (lab, s['n'], f(s['n'] / days), ('**%s**' % w) if bold else w, f(s['m']))
    E = []
    E.append('| Phiên bản setup | Số lệnh (lệnh/ngày) | Winrate (TP 3R, hoà vốn ~27 %) | R TB |')
    E.append('|---|---|---|---|')
    E.append(row('B cũ — 2 VWAP', t_old))
    E.append(row('B v2 — 8 loại vùng', t_v2))
    E.append(row('**B v3 — v2 + đỉnh/đáy phiên trước + Vùng Canh Lệnh**', t_v3, True))
    E.append(row('— trong đó lệnh chỉ có ở v3', c_only))
    E.append(row('Chỉ S/R (đỉnh/đáy phiên trước + VCL, không vùng v2)', RES['Chỉ-S/R']))
    E.append(row('Chỉ Vùng Canh Lệnh', RES['Chỉ-VCL']))
    E.append(row('Chỉ đỉnh/đáy phiên trước', RES['Chỉ-PDHL']))
    E.append(row('B v2 + Vùng Canh Lệnh', RES['B-v2 + VCL']))
    E.append(row('B v2 + đỉnh/đáy phiên trước', RES['B-v2 + PDHL']))
    for k in ZT8:
        E.append(row('B v3 bỏ %s' % k, RES['B-v3 − %s' % k]))
    bn, bw, br_ = B2.bands_of(R1['B-v3'], 0), B2.bands_of(R1['B-v3'], 1), B2.bands_of(R1['B-v3'], 2)
    E.append('| B v3 trên bản đồ vùng DỜI 3–15 giá (%d bản): TB [5 %%–95 %%] | %s (chỉ tham khảo) | %s [%s – %s] | %s [%s – %s] |' % (
        reps, f(bn['GỘP'][0], 0), pct(bw['GỘP'][0]), pct(bw['GỘP'][1]), pct(bw['GỘP'][2]), f(br_['GỘP'][0]), f(br_['GỘP'][1]), f(br_['GỘP'][2])))
    E.append('')
    s_tr = BV.rstat(c_v3[c_v3['split'] == 'TRAIN']['r'].to_numpy(float) if len(c_v3) else [])
    s_te = BV.rstat(c_v3[c_v3['split'] == 'TEST']['r'].to_numpy(float) if len(c_v3) else [])
    E.append('1. R TB B v3 = %s %s; TRAIN %s (n=%d) / TEST %s (n=%d).' % (f(sv3['m']), ci(sv3), f(s_tr['m']), s_tr['n'], f(s_te['m']), s_te['n']))
    E.append('2. Đối chứng: B v3 vs ĐC1 = %s; vs ĐC2 = %s; nhóm chỉ-v3 vs ĐC1 = %s; vs ĐC2 = %s (%d/9 ô "khác đối chứng").' % (VER['v3_dc1'], VER['v3_dc2'], VER['only_dc1'], VER['only_dc2'], n_out))
    E.append('3. Chênh WR nhỏ nhất thấy được với n này ≈ %s điểm (v2 n=%d vs v3 n=%d); lệnh v2 bị chặn mất: %d (thắng %d).' % (f(100 * mdw, 0), n2, n3, len(lost), lost_w))
    E.append('4. Kết luận 3.5: %s.%s' % (final, ' Chưa có lợi thế đo được trên %d phiên.' % days if not c3 else ''))
    open(OUT_EVAL, 'w', encoding='utf-8').write('\n'.join(E) + '\n')
    print('\n'.join(E))
    print('xong %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
