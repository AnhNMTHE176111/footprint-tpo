#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum2_ve.py — vẽ TRƯỚC/SAU: hộp HVN v1 (mục 10) so với v2 (mục 13) ra PNG trong hvn_cum/ (tên file bắt đầu bằng v2_).
  python hvn_cum2_ve.py
Xám = khối lượng (gộp ô); đường đen = khối lượng làm mượt; hộp xanh = v2 (vạch xanh đậm bên trái = lõi 80 %);
khung cam nét liền = v1; nét đứt đen = hộp người dùng mô tả.
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import hvn_cum as H1, hvn_cum2 as H2
import hvn_cum_ve as VE

OUT = VE.OUT
BLUE, ORANGE, INK, MUTED = VE.BLUE, VE.ORANGE, VE.INK, VE.MUTED


def draw(ax, D, sym, a, b, kind, hand=None, title='', legend=True, ylim=None, small=False):
    sc = H1.SCALE[sym] * 0.1
    v1, _ = H2.prof_v1(D, a, b, kind)
    v2, ex = H2.prof_clusters(D, a, b, H2.HP2, kind)
    S, t0, h, w = ex['S'], ex['t0'], ex['h'], ex['w']
    px = (t0 + np.arange(len(S))) * sc
    g = max(1, h // 2); nb = len(w) // g
    wb = w[:nb * g].reshape(nb, g).sum(1) / g; pb = px[:nb * g].reshape(nb, g).mean(1)
    ax.barh(pb, wb, height=(px[1] - px[0]) * g * 0.9, color='#c3c2b7', linewidth=0)
    ax.plot(S / (2 * h + 1), px, color=INK, lw=1.0, label='khối lượng làm mượt')
    xm = max(wb.max(), (S / (2 * h + 1)).max()) * 1.05
    f = (lambda x: '%.2f' % x) if sym == 'nq' else (lambda x: '%.1f' % x)
    for k, c in enumerate(v2):
        lo, hi = c['lo'] * sc, c['hi'] * sc
        ax.axhspan(lo, hi, color=BLUE, alpha=0.22, lw=0, label='v2: hộp HVN (mới)' if k == 0 else None)
        ax.plot([0, 0], [c['clo'] * sc, c['chi'] * sc], color=BLUE, lw=5, solid_capstyle='butt', label='v2: lõi 80 %' if k == 0 else None)
        if small: lab = '%s–%s · %.0f %% · %.1f nến' % (f(lo), f(hi), 100 * c['mass'], c['bars'])
        else: lab = '%s–%s · rộng %s · %.1f %% = %.1f nến · dày ×%.1f' % (f(lo), f(hi), f(hi - lo), 100 * c['mass'], c['bars'], c['con'])
        ax.text(xm * 0.99, hi, lab + ' ', ha='right', va='bottom', color=INK, fontsize=7)
    for k, c in enumerate(v1):
        lo, hi = c['lo'] * sc, c['hi'] * sc
        ax.plot([xm * 0.02, xm * 0.98, xm * 0.98, xm * 0.02, xm * 0.02], [lo, lo, hi, hi, lo], color=ORANGE, lw=1.3, label='v1: hộp HVN (đang chạy)' if k == 0 else None)
    if hand:
        ax.axhline(hand[0], color=INK, lw=1, ls='--', label='hộp người dùng mô tả'); ax.axhline(hand[1], color=INK, lw=1, ls='--')
    ax.set_xlim(0, xm); ax.set_xticks([]); ax.set_ylim(*(ylim or (px[0], px[-1])))
    ax.set_title(title, loc='left', fontsize=9, color=INK)
    if legend: ax.legend(loc='lower right', fontsize=7, frameon=False)
    return v1, v2


def span(D, date, kind):
    k = H1.find_day(D, date)
    return D.days[k] if kind == 'd' else D.weeks[int(D.week_of[D.days[k][0]])]


def one(D, sym, date, kind, name, hand=None, zoom=None):
    t = pd.to_datetime(D.m30['t']); a, b = span(D, date, kind)
    fig, axs = plt.subplots(1, 3 if zoom else 2, figsize=(16 if zoom else 11, 6.5), gridspec_kw=dict(width_ratios=[1.25, 1, 1.1] if zoom else [1.25, 1]))
    ttl = '%sZ26 · profile %s %s → %s (UTC)' % (sym.upper(), 'phiên' if kind == 'd' else 'tuần', t[a].strftime('%m-%d %H:%M'), t[b].strftime('%m-%d %H:%M'))
    v1, v2 = draw(axs[0], D, sym, a, b, kind, hand=hand, title=ttl)
    VE.draw_after(axs[1], D, sym, a, b, v2); axs[1].set_ylim(axs[0].get_ylim()); axs[1].set_title('Nến M30: kỳ nguồn, sau vạch dọc là 2 phiên kế', loc='left', fontsize=9, color=INK)
    if hand:
        axs[1].axhline(hand[0], color=INK, lw=0.8, ls='--'); axs[1].axhline(hand[1], color=INK, lw=0.8, ls='--')
    if zoom:
        draw(axs[2], D, sym, a, b, kind, hand=hand, title='Phóng vào cụm', legend=False, ylim=zoom)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=130); plt.close(fig)
    sc = H1.SCALE[sym] * 0.1
    print(name, '| v1:', [(c['lo'] * sc, c['hi'] * sc) for c in v1], '| v2:', [(c['lo'] * sc, c['hi'] * sc, round(c['mass'], 3)) for c in v2])


def grid(D, sym, kind, name, last=12):
    t = pd.to_datetime(D.m30['t'])
    sp = H1.spans(D, kind)[-last:]
    nc = 4 if len(sp) > 9 else 3; nr = int(np.ceil(len(sp) / nc))
    fig, axs = plt.subplots(nr, nc, figsize=(4.2 * nc, 4.6 * nr)); axs = np.atleast_1d(axs).ravel()
    for ax, (a, b) in zip(axs, sp):
        draw(ax, D, sym, a, b, kind, title='%s %s' % (sym.upper(), t[b].strftime('%Y-%m-%d')), legend=False, small=True)
    for ax in axs[len(sp):]: ax.axis('off')
    fig.suptitle('%sZ26 · %d profile %s gần nhất — hộp xanh = v2 (mới) · khung cam = v1 (đang chạy)' % (sym.upper(), len(sp), 'phiên' if kind == 'd' else 'tuần'), x=0.01, ha='left', fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(os.path.join(OUT, name), dpi=110); plt.close(fig)
    print(name)


def main():
    D, _ = H1.load('nq')
    one(D, 'nq', '2026-11-20', 'd', 'v2_nq_2026-11-20_phien.png', hand=(25530, 25608), zoom=(25380, 25760))
    one(D, 'nq', '2026-11-20', 'w', 'v2_nq_tuan_2026-11-16.png', hand=(25530, 25608), zoom=(25380, 25760))
    one(D, 'nq', '2026-11-23', 'd', 'v2_nq_2026-11-23_phien.png', hand=(26755 + 48, 26820 + 48), zoom=(26650, 27000))
    one(D, 'nq', '2026-11-17', 'd', 'v2_nq_2026-11-17_phien.png')
    one(D, 'nq', '2026-11-10', 'd', 'v2_nq_2026-11-10_phien.png')
    grid(D, 'nq', 'd', 'v2_luoi_nq_phien.png'); grid(D, 'nq', 'w', 'v2_luoi_nq_tuan.png', last=9)
    D, _ = H1.load('gc')
    one(D, 'gc', '2026-10-28', 'd', 'v2_gc_2026-10-28_phien.png')
    one(D, 'gc', '2026-11-05', 'd', 'v2_gc_2026-11-05_phien.png')
    grid(D, 'gc', 'd', 'v2_luoi_gc_phien.png'); grid(D, 'gc', 'w', 'v2_luoi_gc_tuan.png', last=9)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
