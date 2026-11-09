# -*- coding: utf-8 -*-
"""Setup C-v7 (plan `research/PLAN-C-v3.md`): C "Fade cạnh" + lớp L4 = HÀNH LANG hỗ trợ / kháng cự từ bộ vùng VCL v5.

Chạy:  python3 setup_c_v7.py            → report/RESULTS-C-V7.md + report/img/c_v7_sr_*.png (tất định, hạt cố định)
Test:  python3 -m pytest test_setup_c_v7.py -q

CHỈ file D90. Không sửa kernel.py / setup_c_fade_canh.py / setup_c_v6.py / zones_c_v6.py / benzo_vcl.py: chỉ import.
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_c_v6 as S6  # noqa: E402
import zones_c_v7 as Z7  # noqa: E402
import benzo_vcl as BV  # noqa: E402

REPORT = os.path.join(HERE, 'report')
IMG = os.path.join(REPORT, 'img')
OUT_MD = os.path.join(REPORT, 'RESULTS-C-V7.md')

# ------------------------------------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC (PLAN-C-v3 mục 4.2)
PEN = 2
MIN_W = 6.0
EXCL = (780, 860)
EXCL_VO = (780, 930)
REPS = 100
SEED = 20261024
CTRL_DRAWS = 200
DIST_DRAWS = 200
MIN_N = 10
SIGMA_R = 1.6
EXPECT_C4 = dict(poc=(191, -0.31, -58.8), fixed2=(220, -0.17))
EXPECT_C0 = S6.EXPECT_C0

closed, full_stats, gstats, bands_of, cmp_vs, rs = S6.closed, S6.full_stats, S6.gstats, S6.bands_of, S6.cmp_vs, S6.rs
fs, f, pct, nwr, split_cells, band_txt = S6.fs, S6.f, S6.pct, S6.nwr, S6.split_cells, S6.band_txt


class Data7(S6.Data):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.rec = Z7.load_sr(self.df)
        self.mode_c0 = self.P['mf']['mode'].to_numpy()


def corridors(D, shift=None, mask_ok=None, face=Z7.FACE, min_w=Z7.MIN_W):
    return Z7.sr_corridors(D.df, None, shift=shift, mask_ok=mask_ok, face=face, min_w=min_w, rec=D.rec)


def build_l4(D, corr):
    zc, names, mf = Z7.layer_sr(D.df, D.zc0, corr)
    return dict(kind='L4', zc=zc, names=names, mf=mf, corr=corr)


def entries_l4(D, L, tp_mode='poc', min_w=MIN_W, excl=EXCL, gate=None):
    e = S6.detect(D.df, L['zc'], L['mf'], pen_ticks=PEN, min_width=min_w, tp_mode=tp_mode, mad=D.P['mad'], excl=excl,
                  zone_name=L['names'], gate=gate)
    for x in e:
        x['layer'] = 'L4'
    return e


def merge_add(base, new):
    """Nến nào base có entry ⇒ giữ base, bỏ L4 ở nến đó; còn lại thêm L4 (PLAN 2.3)."""
    have = {e['idx'] for e in base}
    out = list(base) + [e for e in new if e['idx'] not in have]
    out.sort(key=lambda e: e['idx'])
    return out


def base_cells(D, tp_mode, shapes, ch, layers):
    """C0 và C4 nguyên xi của v6."""
    R = S6.run_all(D, shapes, ch, tp_mode=tp_mode, layers=layers)
    return R


def run_all_v7(D, tp_mode='poc', sr_kw=None, base=None, shapes=None, ch=None, layers=None):
    """Trả dict C0, C4, C5, C0+SR, C6 → (entries, trades) + 'L4' + 'corr'. sr_kw: face, mask_ok, gate, min_w, excl."""
    kw = dict(sr_kw or {})
    gate, excl = kw.pop('gate', None), kw.pop('excl', EXCL)
    mw = kw.get('min_w', MIN_W)
    if base is None:
        shapes = shapes if shapes is not None else D.shapes()
        ch = ch if ch is not None else D.choch()
        base = S6.run_all(D, shapes, ch, tp_mode=tp_mode, layers=layers)
    corr = corridors(D, **kw)
    L4 = build_l4(D, corr)
    e5 = entries_l4(D, L4, tp_mode, mw, excl, gate)
    out = dict(C0=base['C0'], C4=base['C4'], L4=L4, corr=corr, base=base)
    out['C5'] = (e5, S6.sim(D, e5, base['shapes']))
    e05 = merge_add(base['C0'][0], e5)
    out['C0+SR'] = (e05, S6.sim(D, e05, base['shapes']))
    e6 = merge_add(base['C4'][0], e5)
    out['C6'] = (e6, S6.sim(D, e6, base['shapes']))
    return out


def dc_a_sr(D, base, tp_mode='poc', reps=REPS, sr_kw=None):
    """ĐC-a: dời toàn bộ vùng VCL theo δ[phiên, bản], chạy LẠI máy hành lang + mode + detect. Trả (C5 list gstats, C6 list gstats)."""
    kw = dict(sr_kw or {})
    gate, excl = kw.pop('gate', None), kw.pop('excl', EXCL)
    mw = kw.get('min_w', MIN_W)
    r5, r6 = [], []
    for k in range(reps):
        corr = corridors(D, shift=D.dsh[:, k], **kw)
        L4 = build_l4(D, corr)
        e5 = entries_l4(D, L4, tp_mode, mw, excl, gate)
        r5.append(gstats(S6.sim(D, e5, base['shapes'])))
        e6 = merge_add(base['C4'][0], e5)
        r6.append(gstats(S6.sim(D, e6, base['shapes'])))
    return r5, r6


def prereg_hash():
    try:
        r = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%h', '--', 'research/zones_c_v7.py'], cwd=os.path.dirname(HERE),
                           capture_output=True, text=True, timeout=10)
        h = r.stdout.strip().splitlines()
        return h[-1] if h else '(chưa commit)'
    except Exception:
        return '(không đọc được git)'


def edge_kind(mask):
    if mask & 3:
        return 'có swing (B/B15)'
    if mask & 4:
        return 'có mốc phiên (C)'
    return 'chỉ số tròn (D)'


def _plt():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt


def plot_corr(D, x, trades, path):
    plt = _plt()
    df = D.df
    a = max(int(D.st['start_pos'].loc[x['sno']]), x['birth'] - 40)
    b = min(len(df), x['end'] + 30, x['birth'] + 400)
    seg = df.iloc[a:b]
    fig, ax = plt.subplots(figsize=(15, 6.5))
    xs = np.arange(len(seg))
    o, h, l, c = (seg[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
    col = np.where(c >= o, '#1a7f37', '#cf222e')
    ax.vlines(xs, l, h, color=col, lw=0.8)
    ax.bar(xs, np.maximum(np.abs(c - o), 0.05), bottom=np.minimum(o, c), color=col, width=0.6)
    ax.add_patch(plt.Rectangle((x['birth'] - a, x['lo']), max(x['end'] - x['birth'], 1), x['hi'] - x['lo'], color='orange', alpha=.15))
    ax.add_patch(plt.Rectangle((x['birth'] - a, x['s_lo']), x['end'] - x['birth'], x['s_hi'] - x['s_lo'], color='green', alpha=.25))
    ax.add_patch(plt.Rectangle((x['birth'] - a, x['r_lo']), x['end'] - x['birth'], x['r_hi'] - x['r_lo'], color='red', alpha=.25))
    if len(trades):
        for t in trades.itertuples():
            if a <= t.idx < b:
                ax.scatter([t.idx - a], [t.entry], marker='^' if t.side > 0 else 'v', s=60, color='b', zorder=5)
                ax.text(t.idx - a, t.entry, ' %s %+.1fR' % (t.outcome, t.r), fontsize=7)
    ticks = list(range(0, len(seg), 15))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(seg['t_vn'].iloc[t])[5:16] for t in ticks], rotation=60, fontsize=6)
    ax.set_title('hành lang #%d · phiên %s · sinh %s VN · [%.1f ; %.1f] rộng %.1f · chết: %s · tuổi %d' % (
        x['id'], x['session'], x['t_birth'], x['lo'], x['hi'], x['width'], x['why'], x['life']), fontsize=9)
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


QS = [
    'Q1 — Hành lang CHỈ dùng dòng VCL của đúng nến i (`bar == i`); hộp VCL có thể dịch giữa các nến nhưng cạnh hành lang đóng băng lúc sinh. '
    'Số hành lang mà hộp S/R dịch > 0,1 giá trong đời ghi ở mục 2 (chỉ báo).',
    'Q2 — Chọn "gần nhất" = vùng có `lo` nhỏ nhất trong các vùng nằm hẳn trên close (kháng cự), `hi` lớn nhất trong các vùng nằm hẳn dưới '
    'close (hỗ trợ); hoà ⇒ eid nhỏ hơn. Nếu close nằm TRONG một vùng nào đó ⇒ không sinh.',
    'Q3 — Tô (`band`) trước khi cập nhật; hành lang sinh ở i chỉ có hiệu lực từ i+1. Bước TREND dùng ảnh chụp "đã tô" (không dùng hành lang vừa '
    'sinh trong cùng nến) để khớp đúng `kernel.mode_frame` (band đọc tại `last_pos`).',
    'Q4 — Tên lệnh `SR_HI`/`SR_LO` gán theo nến nào mode có band (nến M5 đã đóng gần nhất), không theo nến đang tô: hành lang vừa chết vẫn có thể '
    'được đọc tối đa 4 nến M1 (PLAN R5) và lệnh đó vẫn mang tên SR.',
    'Q5 — Hành lang sinh khi nến i không splice/thin; không lọc theo pha giờ (excl 18:00–19:20 VN áp ở `detect`).',
    'Q6 — ĐC-a: cộng δ[phiên của dòng VCL, bản] vào `lo/hi` MỌI dòng VCL; chạy lại máy hành lang (sinh theo giá thật) + mode + detect; C6 dùng C4 '
    'thật cộng L4 dời.',
    'Q7 — "Gate cân bằng băng chủ" (độ nhạy 3) = `P[mf][mode][i] == BALANCE` trên băng C0 tại nến vào lệnh.',
    'Q8 — Phép tách loại vùng của cạnh bị fade (có B/B15 · có C · chỉ D) lấy theo hành lang gần nhất đã tô tới nến fade; chỉ báo.',
]


def main():
    t0 = time.time()
    os.makedirs(IMG, exist_ok=True)
    D = Data7()
    shapes = D.shapes()
    ch = D.choch()
    Ls = {k: S6.build_layer(D, k, shapes, ch) for k in ('L0', 'L1', 'L2', 'L3')}
    BASE = {tm: S6.run_all(D, shapes, ch, tp_mode=tm, layers=Ls) for tm in ('poc', 'fixed2')}
    print('chuẩn bị %.1fs' % (time.time() - t0), flush=True)
    R = {tm: run_all_v7(D, tm, base=BASE[tm]) for tm in ('poc', 'fixed2')}
    Rp = R['poc']
    L = []
    w = L.append
    w('# RESULTS C-v7 — hành lang S/R (VCL v5) làm lớp L4 cho setup C (sinh bởi `setup_c_v7.py`, tất định)')
    w('')
    w('Plan: `research/PLAN-C-v3.md`. Dữ liệu DUY NHẤT: `%s`. %d phiên sạch (TRAIN %d ≤ 2026-09-15, TEST %d từ 2026-09-16). Giờ trong dữ liệu = UTC, '
      'VN = UTC+7. Chi phí 0,2 giá/lệnh, 1 lệnh mở cùng lúc.' % (os.path.basename(S6.D90), D.days, D.days_split['TRAIN'], D.days_split['TEST']))
    w('')
    w('## 0. Hằng số đăng ký trước')
    w('')
    w('Commit hằng số + máy + test (TRƯỚC lần chạy kết quả đầu tiên): **%s**. Hằng số: xuyên %d tick, rộng ≥ %s giá, cạnh `near`, TREND %d nến M5 / %s giá, '
      'ĐC %d bản dời (δ ~ U[3, 15] giá, hạt %d), ĐC-b %d lần, ĐC-c khớp khoảng cách %d lần, n tối thiểu phán quyết %d.' % (
          prereg_hash(), PEN, f(MIN_W, 1), Z7.TREND_RUNS, f(Z7.TREND_DIST, 1), REPS, SEED, CTRL_DRAWS, DIST_DRAWS, MIN_N))
    w('')
    w('Thuật ngữ: buy / sell / limit / market giữ tiếng Anh. "Hành lang" = khoảng giữa vùng hỗ trợ gần nhất bên dưới và vùng kháng cự gần nhất bên trên. '
      'KTC = khoảng tin cậy 95% lấy mẫu lại theo lệnh (10.000 lần, hạt 0).')
    w('')
    # ---------------------------------------------------------------- công suất
    w('## 1. Công suất thống kê (in TRƯỚC bảng chính)')
    w('')
    w('σ_R ≈ %s. Hiệu R TB nhỏ nhất phát hiện được (80%% công suất, mức 5%%, hai phía) = 2,8·σ/√n:' % f(SIGMA_R, 1))
    w('')
    w('| n | 20 | 60 | 100 | 170 | 470 |\n|---|---|---|---|---|---|')
    w('| hiệu tối thiểu (R) | ' + ' | '.join(f(2.8 * SIGMA_R / math.sqrt(k)) for k in (20, 60, 100, 170, 470)) + ' |')
    w('')
    w('Số phép so có phán quyết: 3 đối chứng × C5 + 2 đối chứng × C6 = **5** ⇒ một ô "vượt" đơn lẻ chưa đủ tin. Kỳ vọng trước: vị trí S/R đã đo 3 lần '
      'độc lập là không mang thông tin ⇒ C5 ≈ ĐC-c.')
    w('')
    # ---------------------------------------------------------------- phễu + nhật ký
    corr = Rp['corr']
    fu, lg = corr['funnel'], pd.DataFrame(corr['log'])
    w('## 2. Phễu + nhật ký hành lang (in TRƯỚC bảng lệnh)')
    w('')
    w('| lần thử sinh | close nằm trong vùng | thiếu một phía | hẹp < 6 | **sinh** | chết: hết phiên | chết: TREND | chết: mất vùng | còn sống cuối dữ liệu |\n'
      '|---|---|---|---|---|---|---|---|---|')
    w('| %d | %d | %d | %d | %d | %d | %d | %d | %d |' % (fu['thu'], fu['trong_vung'], fu['thieu_phia'], fu['hep'], fu['sinh'], fu['het_phien'],
                                                          fu['trend'], fu['mat_vung'], fu['het_du_lieu']))
    w('')
    clean_set = set(D.st['session_id'].loc[D.clean_snos])
    lg['clean'] = lg['session'].isin(clean_set)
    lg['split'] = ['TRAIN' if str(s)[:10] <= K.CONST['split_train_end'] else 'TEST' for s in lg['session']]
    w('Hành lang sinh: **%d** (phiên sạch %d; TRAIN %d / TEST %d; ~%s/phiên sạch). Rộng lúc sinh: trung vị %s giá (p10 %s, p90 %s). Tuổi (nến M1): trung vị %d, '
      'p90 %d. Lý do chết: %s. Hộp S/R dịch > 0,1 giá trong đời: %d hành lang. Phủ %s%% số nến.' % (
          len(lg), int(lg['clean'].sum()), int((lg['split'] == 'TRAIN').sum()), int((lg['split'] == 'TEST').sum()), f(len(lg) / max(D.days, 1), 1),
          f(lg['width'].median(), 1), f(lg['width'].quantile(.1), 1), f(lg['width'].quantile(.9), 1), int(lg['life'].median()),
          int(lg['life'].quantile(.9)), ', '.join('%s %d' % (k, v) for k, v in lg['why'].value_counts().items()), int(lg['moved'].sum()),
          f(100 * float((corr['frame']['sr_id'].to_numpy() >= 0).mean()), 0)))
    w('')
    # ---------------------------------------------------------------- bảng chính
    w('## 3. Bảng chính (ô 3.1)')
    w('')
    names = {'C0': 'C0 = tái tạo vòng 1', 'C4': 'C4 = v6 (D + P/b + CHoCH)', 'C5': 'C5 = L4 riêng (S/R)', 'C0+SR': 'C0+SR = C0 ∪ L4',
             'C6': 'C6 = C4 + SR'}
    for tm, lab in (('poc', 'TP chính: cạnh đối diện / POC ≥ 2R'), ('fixed2', 'TP cố định 2R')):
        w('### %s' % lab)
        w('')
        w(S6.HDR_FULL)
        for cell in ('C0', 'C4', 'C5', 'C0+SR', 'C6'):
            w(S6.row_full(names[cell], full_stats(R[tm][cell][1], D.days)))
        w('')
        w('| ô | TRAIN n · WR · R TB | TEST n · WR · R TB | A | EU | US | T8 | T9 | T10 |')
        w('|---|---|---|---|---|---|---|---|---|')
        for cell in ('C0', 'C4', 'C5', 'C0+SR', 'C6'):
            t = closed(R[tm][cell][1])
            sp = split_cells(t)
            ph = [BV.rstat(t[t['phase'] == p]['r'].to_numpy(float) if len(t) else []) for p in ('A', 'EU', 'US')]
            th = [BV.rstat(t[t['thang'] == m]['r'].to_numpy(float) if len(t) else []) for m in ('T8', 'T9', 'T10')]
            w('| %s | %s | %s | %s |' % (cell, nwr(sp['TRAIN']), nwr(sp['TEST']), ' | '.join(nwr(x) for x in ph + th)))
        w('')
    ok_c0 = all(len(closed(R[tm]['C0'][1])) == EXPECT_C0[tm][0] for tm in ('poc', 'fixed2'))
    ok_c4 = all(len(closed(R[tm]['C4'][1])) == EXPECT_C4[tm][0] for tm in ('poc', 'fixed2'))
    if not (ok_c0 and ok_c4):
        w('**CẢNH BÁO: C0 / C4 không tái tạo đúng v6.**')
        w('')
    # C5 theo loại vùng
    t5 = closed(Rp['C5'][1])
    w('C5 tách theo loại vùng của cạnh bị fade (chỉ báo, không phán): ')
    w('')
    if len(t5):
        cid_ff = pd.Series(corr['frame']['sr_id'].to_numpy()).replace(-1, np.nan).ffill().fillna(-1).astype(int).to_numpy()
        byid = {x['id']: x for x in corr['log']}
        kinds = []
        for x in t5.itertuples():
            c = byid.get(int(cid_ff[x.poke_idx]))
            if c is None:
                kinds.append('không rõ')
            else:
                kinds.append(edge_kind(c['r_mask'] if x.side < 0 else c['s_mask']))
        t5 = t5.assign(kind=kinds)
        w('| loại | n · WR · R TB |\n|---|---|')
        for k in ('có swing (B/B15)', 'có mốc phiên (C)', 'chỉ số tròn (D)', 'không rõ'):
            x = t5[t5['kind'] == k]
            if len(x):
                w('| %s | %s |' % (k, nwr(BV.rstat(x['r'].to_numpy(float)))))
        w('')
    # ---------------------------------------------------------------- tách đóng góp
    w('## 4. Tách đóng góp (TP chính)')
    w('')
    S = {c: full_stats(Rp[c][1], D.days) for c in ('C0', 'C4', 'C5', 'C0+SR', 'C6')}
    t4, t6 = closed(Rp['C4'][1]), closed(Rp['C6'][1])
    kept = set(t6['idx'].tolist())
    lost = t4[~t4['idx'].isin(kept)] if len(t4) else t4
    l4_in6 = {e['idx'] for e in Rp['C6'][0] if e.get('layer') == 'L4'}
    n_l4_in6 = int(t6['idx'].isin(l4_in6).sum()) if len(t6) else 0
    r_l4_in6 = float(t6[t6['idx'].isin(l4_in6)]['r'].sum()) if len(t6) else 0.0
    w('| phần | Δ n | Δ tổng R | ghi chú |\n|---|---|---|---|')
    w('| Δ(C0+SR − C0) | %+d | %s | |' % (S['C0+SR']['n'] - S['C0']['n'], fs(S['C0+SR']['sum_r'] - S['C0']['sum_r'], 1)))
    w('| Δ(C6 − C4) | %+d | %s | |' % (S['C6']['n'] - S['C4']['n'], fs(S['C6']['sum_r'] - S['C4']['sum_r'], 1)))
    w('| lệnh C4 bị chặn vì L4 đang mở | −%d | %s | Δ tổng R do mất chúng (dương = chúng là lệnh thua) |' % (len(lost), fs(-float(lost['r'].sum()) if len(lost) else 0.0, 1)))
    w('| lệnh L4 trong C6 | %d | %s | |' % (n_l4_in6, fs(r_l4_in6, 1)))
    w('')
    print('ô chính xong %.0fs' % (time.time() - t0), flush=True)
    # ---------------------------------------------------------------- đối chứng
    w('## 5. Đối chứng (TP chính)')
    w('')
    w('Phán quyết `benzo_vcl.verdict`: ngoài dải 5–95%% ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ≥ 2/3 tháng, |hiệu| > 2 sai số; chỉ khi ≥ %d lệnh mỗi nửa.' % MIN_N)
    w('')
    A5, A6 = dc_a_sr(D, BASE['poc'], 'poc')
    print('ĐC-a xong %.0fs' % (time.time() - t0), flush=True)
    VER = {}
    w('| nguồn | ĐC | TRAIN thật · đối chứng | TEST thật · đối chứng | phán quyết |\n|---|---|---|---|---|')

    def line(src, kind, tsel, bands):
        cmp, ok = cmp_vs(tsel, bands)
        v = BV.verdict(cmp, ok)
        VER[(src, kind)] = (v, cmp, S6.beats_half(cmp))
        w('| %s | %s | %s · %s | %s · %s | %s |' % (src, kind, fs(cmp['TRAIN'][0]) + ' (n %d)' % cmp['TRAIN'][2], band_txt(cmp['TRAIN'][3:]),
                                                   fs(cmp['TEST'][0]) + ' (n %d)' % cmp['TEST'][2], band_txt(cmp['TEST'][3:]), v))

    L4 = Rp['L4']
    line('C5', 'ĐC-a dời bản đồ S/R (%d bản)' % REPS, Rp['C5'][1], bands_of(A5))
    line('C5', 'ĐC-b vào ngẫu nhiên tại vùng (%d)' % CTRL_DRAWS, Rp['C5'][1], S6.dc_b(D, L4, Rp['C5'][1], flt=lambda t: t))
    line('C5', 'ĐC-c khớp khoảng cách (%d)' % DIST_DRAWS, Rp['C5'][1], S6.dc_dist(D, Rp['C5'][1]))
    line('C6', 'ĐC-a dời bản đồ S/R (%d bản)' % REPS, Rp['C6'][1], bands_of(A6))
    line('C6', 'ĐC-c khớp khoảng cách (%d)' % DIST_DRAWS, Rp['C6'][1], S6.dc_dist(D, Rp['C6'][1]))
    print('đối chứng xong %.0fs' % (time.time() - t0), flush=True)
    w('')
    # ---------------------------------------------------------------- độ nhạy
    w('## 6. Lưới độ nhạy (khai báo trước, in ĐỦ, mỗi dòng đổi MỘT thứ, không chọn ô)')
    w('')
    w('Ô: n · WR · R TB; TR = R TB TRAIN, TE = R TB TEST.')
    w('')
    w('| biến thể | C5 | C6 |\n|---|---|---|')
    mode_c0 = D.mode_c0

    def vrow(name, RR):
        w('| %s | %s |' % (name, ' | '.join('%s; TR %s / TE %s' % (nwr(rs(RR[c][1])), fs(split_cells(RR[c][1])['TRAIN']['m']),
                                                                  fs(split_cells(RR[c][1])['TEST']['m'])) for c in ('C5', 'C6'))))

    vrow('**bản chính**', Rp)
    for nm, kw in (('1. cạnh xa (R.hi, S.lo)', dict(face='far')),
                   ('2. bỏ vùng chỉ-số-tròn', dict(mask_ok=lambda m: m != Z7.MASK_ROUND_ONLY)),
                   ('3. + cân bằng băng chủ (C0)', dict(gate=lambda i, j, s: mode_c0[i] == 'BALANCE')),
                   ('4. rộng tối thiểu 8', dict(min_w=8.0)),
                   ('5. chặn thêm 19:20–20:30 VN', dict(excl=EXCL_VO))):
        vrow(nm, run_all_v7(D, 'poc', sr_kw=kw, base=BASE['poc']))
    w('')
    print('độ nhạy xong %.0fs' % (time.time() - t0), flush=True)
    # ---------------------------------------------------------------- tiêu chí
    w('## 7. Tiêu chí khai báo trước (mục 3.5, máy chấm)')
    w('')
    sp = {c: split_cells(Rp[c][1]) for c in ('C0', 'C4', 'C5', 'C6')}
    worse = [k for k, v in VER.items() if '▼' in v[0]]
    a1 = all(sp['C5'][k]['m'] == sp['C5'][k]['m'] and sp['C5'][k]['m'] >= sp['C0'][k]['m'] for k in ('TRAIN', 'TEST'))
    a2 = all(sp['C6'][k]['m'] == sp['C6'][k]['m'] and sp['C6'][k]['m'] >= sp['C4'][k]['m'] for k in ('TRAIN', 'TEST'))
    a3 = S['C6']['wr'] == S['C6']['wr'] and S['C6']['wr'] >= S['C4']['wr'] - 0.03
    S0 = a1 and a2 and a3 and not worse
    w('**S0** — R TB C5 ≥ C0 ở TRAIN (%s vs %s) và TEST (%s vs %s) → %s · R TB C6 ≥ C4 ở TRAIN (%s vs %s) và TEST (%s vs %s) → %s · WR C6 ≥ WR C4 − 3 điểm '
      '(%s vs %s) → %s · không đối chứng nào "kém hơn thật" → %s. ⇒ **S0 %s**.' % (
          fs(sp['C5']['TRAIN']['m']), fs(sp['C0']['TRAIN']['m']), fs(sp['C5']['TEST']['m']), fs(sp['C0']['TEST']['m']), 'đạt' if a1 else 'KHÔNG',
          fs(sp['C6']['TRAIN']['m']), fs(sp['C4']['TRAIN']['m']), fs(sp['C6']['TEST']['m']), fs(sp['C4']['TEST']['m']), 'đạt' if a2 else 'KHÔNG',
          pct(S['C6']['wr']), pct(S['C4']['wr']), 'đạt' if a3 else 'KHÔNG', 'đạt' if not worse else 'KHÔNG (%s)' % '; '.join('%s / %s' % k for k in worse),
          'ĐẠT' if S0 else 'KHÔNG ĐẠT'))
    w('')
    b1 = sp['C5']['TRAIN']['m'] == sp['C5']['TRAIN']['m'] and sp['C5']['TRAIN']['m'] >= -0.10
    b2 = sp['C5']['TEST']['m'] == sp['C5']['TEST']['m'] and sp['C5']['TEST']['m'] >= 0
    b3 = sp['C5']['TEST']['n'] >= 30
    kd = [k for k in VER if k[0] == 'C5' and 'ĐC-c' in k[1]][0]
    b4 = VER[kd][2]
    S1 = S0 and b1 and b2 and b3 and b4
    w('**S1** — S0 (%s) · C5 TRAIN ≥ −0,10 (%s) → %s · C5 TEST ≥ 0 (%s) → %s · n TEST C5 ≥ 30 (%d) → %s · C5 vượt ĐC-c khớp khoảng cách (R TB > p95) ở ≥ 1 nửa '
      'với n ≥ 10 → %s. ⇒ **S1 %s**.' % ('đạt' if S0 else 'không', fs(sp['C5']['TRAIN']['m']), 'đạt' if b1 else 'KHÔNG', fs(sp['C5']['TEST']['m']),
                                           'đạt' if b2 else 'KHÔNG', sp['C5']['TEST']['n'], 'đạt' if b3 else 'KHÔNG', 'đạt' if b4 else 'KHÔNG',
                                           'ĐẠT' if S1 else 'KHÔNG ĐẠT'))
    w('')
    v5 = [v for k, v in VER.items() if k[0] == 'C5']
    allv = len(v5) == 3 and all('KHÁC đối chứng ▲' in v[0] for v in v5)
    S2 = sp['C5']['TRAIN']['m'] > 0 and sp['C5']['TEST']['m'] > 0 and sp['C5']['TEST']['n'] >= 60 and allv
    w('**S2** — C5 TRAIN %s > 0, TEST %s > 0, n TEST %d ≥ 60, vượt CẢ ba đối chứng theo verdict → **%s**.' % (
        fs(sp['C5']['TRAIN']['m']), fs(sp['C5']['TEST']['m']), sp['C5']['TEST']['n'], 'ĐẠT' if S2 else 'KHÔNG ĐẠT'))
    w('')
    kl = ('S2 đạt: có lợi thế đo được.' if S2 else 'S1 đạt ⇒ được port C# để ghi log live (vẫn TẮT mặc định).' if S1 else
          'không đạt S1 ⇒ **KHÔNG port C#**; ' + ('đạt S0 nên hướng đáng theo dõi tiếp.' if S0 else
                                                  'không đạt S0 ⇒ ghi "không", KHÔNG thêm S/R vào C, không mở vòng tinh chỉnh trên cùng dữ liệu.'))
    w('**Kết luận máy:** %s' % kl)
    w('')
    # ---------------------------------------------------------------- BẢNG TÓM TẮT
    w('## 8. Chỗ tự quyết (plan không nói rõ)')
    w('')
    for q in QS:
        w('- ' + q)
    w('')
    w('## 9. BẢNG TÓM TẮT (TP chính)')
    w('')
    w('| | C cũ (trước thay đổi, C0) | C4 v6 (D + P/b + CHoCH) | C4 + S/R mới (C6) |\n|---|---|---|---|')

    def cell(c):
        s = S[c]
        return '%d (%s/ngày) | %s | %s | %s' % (s['n'], f(s['per_day']), pct(s['wr']), fs(s['m']), fs(s['sum_r'], 1))
    cs = {c: cell(c).split(' | ') for c in ('C0', 'C4', 'C6')}
    for k, lab in enumerate(('Số lệnh (lệnh/ngày)', 'Winrate', 'R TB', 'Tổng R')):
        w('| %s | %s | %s | %s |' % (lab, cs['C0'][k], cs['C4'][k], cs['C6'][k]))
    w('')
    w('Kết luận: %s Chỉ đo trên %d phiên D90, chưa kiểm ngoài mẫu.' % (
        'đạt S2.' if S2 else 'đạt S1 (chưa phải S2).' if S1 else 'đạt S0, KHÔNG đạt S1.' if S0 else 'KHÔNG đạt S0 ⇒ chưa chứng minh S/R có lợi cho C.', D.days))
    w('')
    # ---------------------------------------------------------------- ảnh
    imgs = []
    byid = {x['id']: x for x in corr['log']}
    tt = closed(Rp['C5'][1])
    if len(tt):
        cid_ff = pd.Series(corr['frame']['sr_id'].to_numpy()).replace(-1, np.nan).ffill().fillna(-1).astype(int).to_numpy()
        tt = tt.assign(cid=[int(cid_ff[i]) for i in tt['poke_idx']])
        for spn in ('TRAIN', 'TEST'):
            ids = sorted({c for c in tt[tt['split'] == spn]['cid'] if c in byid and byid[c]['session'] in clean_set})
            pick = [ids[int(k)] for k in np.linspace(0, len(ids) - 1, min(5, len(ids))).round()] if ids else []
            for cid_ in sorted(set(pick)):
                x = dict(byid[cid_])
                fn = 'c_v7_sr_%s_%03d_%s.png' % (spn, cid_, x['t_birth'][:10])
                plot_corr(D, x, tt[tt['cid'] == cid_], os.path.join(IMG, fn))
                imgs.append('[%s #%d %s](img/%s)' % (spn, cid_, x['t_birth'][5:16], fn))
    w('Ảnh 5 hành lang có lệnh TRAIN + 5 TEST (chọn đều theo thời gian): ' + (' · '.join(imgs) if imgs else '(không có)') + '.')
    w('')
    w('## Phụ lục — nhật ký hành lang (ĐỪNG mở trước khi tự tìm 5 ca trên Optimus Flow)')
    w('')
    w('| # | phiên | sinh (VN) | S [lo ; hi] mask | R [lo ; hi] mask | hành lang | rộng | chết | tuổi |\n|---|---|---|---|---|---|---|---|---|')
    for x in corr['log']:
        w('| %d | %s | %s | %s ; %s (%d) | %s ; %s (%d) | %s ; %s | %s | %s | %d |' % (
            x['id'], x['session'], x['t_birth'][5:], f(x['s_lo'], 2), f(x['s_hi'], 2), x['s_mask'], f(x['r_lo'], 2), f(x['r_hi'], 2), x['r_mask'],
            f(x['lo'], 2), f(x['hi'], 2), f(x['width'], 1), x['why'], x['life']))
    w('')
    with open(OUT_MD, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('ghi %s (%.0fs)' % (OUT_MD, time.time() - t0))


if __name__ == '__main__':
    main()
