# -*- coding: utf-8 -*-
"""Vẽ minh hoạ "một lần chạm" trên 2 phiên (1 TRAIN, 1 TEST): nến M1 + vùng v5 (xanh nhạt) + từng lần chạm
(khung từ nến bắt đầu tới nến thoát cuối, màu theo kết cục, chữ Đ/X/? + số nến neo). Cửa sổ 300 nến nhiều lần chạm nhất.
Chạy sau lan_cham.py (đọc report/cache_lc/v5.pkl + report/lan_cham_episodes.csv.gz) → report/img/lan_cham_<split>_<phiên>.png"""
import os, pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.patches import Rectangle
import vcl5 as V5
import lan_cham as LC

SESS = {'TRAIN': '2026-09-08', 'TEST': '2026-10-14'}
WIN = 300
OUT = os.path.join(V5.REPORT, 'img')
INK, MUTED, ZONE = '#0b0b0b', '#52514e', '#2a78d6'
KCOL = {LC.DAO: '#1baf7a', LC.XUYEN: '#eb6834', LC.CHUA_RO: '#8a8984', LC.KRP: '#8a8984'}
KCH = {LC.DAO: 'Đ', LC.XUYEN: 'X', LC.CHUA_RO: '?', LC.KRP: '?'}


def draw(ctx, rec, ep, sid, split):
    df, st = ctx['df'], ctx['st']
    s = int(st.index[st['session_id'] == sid][0])
    a, b = int(st.loc[s, 'start_pos']), int(st.loc[s, 'end_pos'])
    e = ep[(ep['bat_dau'] >= a) & (ep['bat_dau'] <= b)]
    # cửa sổ 300 nến có nhiều lần chạm nhất (cần có cả đảo và xuyên)
    best, w0 = -1, a
    for x in range(a, b - WIN, 10):
        ee = e[(e['bat_dau'] >= x) & (e['bat_dau'] < x + WIN - 10)]
        sc = len(ee) + 100 * ((ee['ket'] == LC.DAO).any() and (ee['ket'] == LC.XUYEN).any())
        if sc > best:
            best, w0 = sc, x
    w1 = w0 + WIN
    d = df.iloc[w0:w1]
    x = np.arange(len(d))
    O, H, L, C = (d[c].to_numpy(float) for c in ('open', 'high', 'low', 'close'))
    r = rec[(rec['bar'] >= w0) & (rec['bar'] < w1)]
    fig, ax = plt.subplots(figsize=(22, 10), dpi=110)
    fig.patch.set_facecolor('#fcfcfb')
    ax.set_facecolor('#fcfcfb')
    polys = [[(b_ - w0 - .5, lo), (b_ - w0 + .5, lo), (b_ - w0 + .5, hi), (b_ - w0 - .5, hi)]
             for b_, lo, hi in zip(r['bar'].to_numpy(), r['lo'].to_numpy(), r['hi'].to_numpy())]
    ax.add_collection(PolyCollection(polys, facecolors=ZONE, edgecolors='none', alpha=0.13))
    ee = e[(e['bat_dau'] >= w0) & (e['bat_dau'] < w1)]
    for t in ee.itertuples():
        x0 = t.bat_dau - w0 - .5
        x1 = (t.thoat_cuoi if t.thoat_cuoi >= 0 else t.chot) - w0 - .5
        col = KCOL[t.ket]
        ax.add_patch(Rectangle((x0, t.lo_bd), max(x1 - x0, 1), t.hi_bd - t.lo_bd, fill=False, edgecolor=col, linewidth=2.0))
        ax.axvline(min(t.chot, w1 - 1) - w0, ymin=0, ymax=0.025, color=col, linewidth=2)
        ax.text(x0 + 0.5, t.hi_bd + 0.25, f'{KCH[t.ket]}{t.dwell}', color=INK, fontsize=9, fontweight='bold', va='bottom', ha='left', clip_on=True)
    upc = C >= O
    ax.add_collection(LineCollection([[(xx, l), (xx, h)] for xx, l, h in zip(x, L, H)], colors=INK, linewidths=0.6))
    ax.bar(x[upc], (C - O)[upc], bottom=O[upc], width=0.7, color='white', edgecolor=INK, linewidth=0.5)
    ax.bar(x[~upc], (O - C)[~upc], bottom=C[~upc], width=0.7, color=INK, edgecolor=INK, linewidth=0.5)
    ax.set_xlim(-2, len(d) + 1)
    ax.set_ylim(L.min() - 3, H.max() + 3)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(1))
    ax.grid(True, which='major', color='#e6e5e0', linewidth=0.6)
    tv = d['t_vn'].dt.strftime('%H:%M').to_numpy()
    tick = np.flatnonzero(d['t_vn'].dt.minute.to_numpy() % 30 == 0)
    ax.set_xticks(tick)
    ax.set_xticklabels([tv[k] for k in tick], fontsize=9, color=MUTED)
    ax.tick_params(axis='y', labelsize=9, labelright=True, colors=MUTED)
    ax.set_xlabel('giờ VN (UTC+7)', color=MUTED)
    n_ = len(ee)
    cnt = {k: int((ee['ket'] == k).sum()) for k in (LC.DAO, LC.XUYEN)}
    ax.set_title(f'Lần chạm (neo nhiều nến) · GCZ26 M1 · phiên {sid} ({split}) · {n_} lần chạm: {cnt[LC.DAO]} đảo chiều, {cnt[LC.XUYEN]} xuyên phá\n'
                 'Nền xanh nhạt = vùng hiển thị (rộng 2–5 giá). Khung = một lần chạm, từ nến giá tới vùng đến nến cuối còn neo; '
                 'chữ = kết cục + số nến neo (Đ = đảo chiều, X = xuyên phá, ? = chưa rõ); vạch dưới đáy = nến chốt (sau 5 nến yên).',
                 fontsize=11, loc='left', color=INK)
    for k, lab in ((LC.DAO, 'đảo chiều (Đ)'), (LC.XUYEN, 'xuyên phá (X)'), (LC.CHUA_RO, 'chưa rõ (?)')):
        ax.plot([], [], color=KCOL[k], linewidth=2, label=lab)
    ax.legend(loc='upper left', frameon=False, fontsize=10)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f'lan_cham_{split}_{sid}.png')
    fig.tight_layout()
    fig.savefig(p, facecolor=fig.get_facecolor())
    plt.close(fig)
    return p


def main():
    bars, lv = V5.load(V5.BASE90)
    ctx = V5.prepare(bars, lv)
    with open(os.path.join(LC.CACHE, 'v5.pkl'), 'rb') as f:
        rec = pickle.load(f)['rec'].reset_index(drop=True)
    ep, r, _ = LC.episodes(LC.bar_arrays(ctx['df']), rec)
    ep = ep[ep['ket'] != LC.HDL].copy()
    ep['lo_bd'] = r['lo'].to_numpy()[ep['srow'].to_numpy()]
    ep['hi_bd'] = r['hi'].to_numpy()[ep['srow'].to_numpy()]
    for split, sid in SESS.items():
        print(draw(ctx, rec, ep, sid, split))


if __name__ == '__main__':
    main()
