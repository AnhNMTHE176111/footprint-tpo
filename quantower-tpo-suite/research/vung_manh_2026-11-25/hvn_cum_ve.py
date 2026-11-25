#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum_ve.py — vẽ profile + hộp HVN MỚI (dạng cụm) so với dải HVN CŨ ra PNG trong hvn_cum/.
  python hvn_cum_ve.py            (mọi ảnh)
Xám = khối lượng từng bước giá (đã gộp ô để nhìn); đường đen = khối lượng làm mượt S; hộp xanh = HVN dạng cụm;
vạch cam = dải HVN cũ (đỉnh nhọn, nền 90 %); nét đứt = hộp người dùng vẽ tay (chỉ ca NQ 23/11, đã dịch basis).
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import hvn_cum as H

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'hvn_cum')
BLUE, ORANGE, INK, MUTED, SURF = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#fcfcfb'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#c9c8c2', 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF, 'axes.spines.top': False, 'axes.spines.right': False})


def old_hvn(D, vm, V, a, b):
    st = V.profile_stats(D, a, b)
    res, _ = vm.find_hvn(st['pr'], st['w'])
    out = []
    for i, pk, r in res[:3]:
        if r < 2.5: continue
        lo, hi = V.peak_sharpness(st['pr'], st['w'], i); out.append((lo, hi, r))
    return out, st


def fmt(x, sym):
    return ('%.2f' % x) if sym == 'nq' else ('%.1f' % x)


def draw_profile(ax, D, vm, V, sym, a, b, kind='d', hand=None, title=None, legend=True):
    sc = H.SCALE[sym]
    hp = dict(H.HP, Y=H.HP['Y_W'] if kind == 'w' else H.HP['Y'])
    cl, ex = H.prof_clusters(D, a, b, hp)
    S, t0, h, w = ex['S'], ex['t0'], ex['h'], ex['w']
    px = (t0 + np.arange(len(S))) * 0.1 * sc
    g = max(1, h // 2)                                   # gộp ô để vẽ thanh
    nb = len(w) // g
    wb = w[:nb * g].reshape(nb, g).sum(1) / g; pb = px[:nb * g].reshape(nb, g).mean(1)
    ax.barh(pb, wb, height=(px[1] - px[0]) * g * 0.9, color='#c3c2b7', linewidth=0)
    ax.plot(S / (2 * h + 1), px, color=INK, lw=1.2, label='khối lượng làm mượt (± %.2f × biên độ M30)' % H.HP['SM'])
    xm = max(wb.max(), (S / (2 * h + 1)).max()) * 1.05
    old, st = old_hvn(D, vm, V, a, b)
    for k, (lo, hi, r) in enumerate(old):
        ax.axhspan(lo * sc - 0.02 * sc, hi * sc + 0.02 * sc, color=ORANGE, alpha=0.85, lw=0, label='HVN cũ (đỉnh nhọn, nền 90 %)' if k == 0 else None)
    for k, c in enumerate(cl):
        lo, hi = c['lo'] * 0.1 * sc, c['hi'] * 0.1 * sc
        ax.axhspan(lo, hi, color=BLUE, alpha=0.22, lw=0, label='HVN dạng cụm (mới)' if k == 0 else None)
        ax.axhline(lo, color=BLUE, lw=1); ax.axhline(hi, color=BLUE, lw=1)
        ax.text(xm * 0.99, hi, '%s–%s · rộng %s · %.0f %% khối lượng ' % (fmt(lo, sym), fmt(hi, sym), fmt(hi - lo, sym), 100 * c['mass']), ha='right', va='bottom', color=INK, fontsize=8)
    if hand:
        ax.axhline(hand[0], color=INK, lw=1, ls='--', label='hộp người dùng vẽ tay (đã dịch basis)'); ax.axhline(hand[1], color=INK, lw=1, ls='--')
    ax.axhline(st['vah'] * sc, color=MUTED, lw=0.6, ls=':'); ax.axhline(st['val'] * sc, color=MUTED, lw=0.6, ls=':', label='VAH / VAL 70 %')
    ax.set_xlim(0, xm); ax.set_xticks([])
    ax.set_ylim(px[0], px[-1])
    ax.set_title(title or '', loc='left', fontsize=9, color=INK)
    if legend: ax.legend(loc='lower right', fontsize=7, frameon=False)
    return cl, old


def draw_after(ax, D, sym, a, b, cl, nxt=2):
    """Nến M30 (cao–thấp) của phiên nguồn và các phiên sau, kèm hộp HVN kéo ngang."""
    sc = H.SCALE[sym]
    k = int(D.day_of[b]); e = D.days[min(k + nxt, len(D.days) - 1)][1]
    x = np.arange(a, e + 1)
    ax.vlines(x - a, D.m30['l'][a:e + 1] * sc, D.m30['h'][a:e + 1] * sc, color=MUTED, lw=1)
    ax.axvline(b - a + 0.5, color='#c9c8c2', lw=0.8)
    for c in cl:
        ax.axhspan(c['lo'] * 0.1 * sc, c['hi'] * 0.1 * sc, color=BLUE, alpha=0.22, lw=0)
    ax.set_xticks([]); ax.set_title('Nến M30 (cao–thấp): kỳ nguồn, sau vạch dọc là các phiên kế tiếp', loc='left', fontsize=9, color=INK)


def one(sym, date, name, zoom_u=None, hand=None, kind='d', D=None, vm=None):
    import vung_manh as V
    t = pd.to_datetime(D.m30['t'])
    k = H.find_day(D, date)
    if kind == 'd': a, b = D.days[k]
    else:
        wk = int(D.week_of[D.days[k][0]]); a, b = D.weeks[wk]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 6.5), gridspec_kw=dict(width_ratios=[1.25, 1]), sharey=True)
    cl, old = draw_profile(a1, D, vm, V, sym, a, b, kind, hand=hand,
                           title='%s · profile %s %s → %s (UTC)' % (sym.upper() + 'Z26', 'phiên' if kind == 'd' else 'tuần', t[a].strftime('%m-%d %H:%M'), t[b].strftime('%m-%d %H:%M')))
    draw_after(a2, D, sym, a, b, cl)
    if zoom_u and cl:
        up = H.up_of(D, a, b) * H.SCALE[sym]; mid = (cl[0]['lo'] + cl[0]['hi']) / 2 * 0.1 * H.SCALE[sym]
        a1.set_ylim(mid - zoom_u * up, mid + zoom_u * up)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=130); plt.close(fig)
    print(name, '| cụm mới:', [(round(c['lo'] * 0.1 * H.SCALE[sym], 2), round(c['hi'] * 0.1 * H.SCALE[sym], 2), round(c['mass'], 3)) for c in cl],
          '| HVN cũ:', [(round(lo * H.SCALE[sym], 2), round(hi * H.SCALE[sym], 2), round(r, 2)) for lo, hi, r in old])


def grid(sym, kind, name, D, vm, last=12):
    import vung_manh as V
    t = pd.to_datetime(D.m30['t'])
    sp = H.spans(D, kind)[-last:]
    nc = 4 if len(sp) > 9 else 3; nr = int(np.ceil(len(sp) / nc))
    fig, axs = plt.subplots(nr, nc, figsize=(4.2 * nc, 4.6 * nr))
    axs = np.atleast_1d(axs).ravel()
    for ax, (a, b) in zip(axs, sp):
        draw_profile(ax, D, vm, V, sym, a, b, kind, title='%s %s' % (sym.upper(), t[b].strftime('%Y-%m-%d')), legend=False)
    for ax in axs[len(sp):]: ax.axis('off')
    fig.suptitle('%sZ26 · %d profile %s gần nhất — hộp xanh = HVN dạng cụm (mới) · vạch cam = HVN cũ · chấm chấm = VAH/VAL' % (sym.upper(), len(sp), 'phiên' if kind == 'd' else 'tuần'),
                 x=0.01, ha='left', fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(os.path.join(OUT, name), dpi=110); plt.close(fig)
    print(name)


def main(args=()):
    os.makedirs(OUT, exist_ok=True)
    D, vm = H.load('nq')
    # hộp người dùng vẽ trên NAS100USD: 26.755 → 26.820; basis ước 48 điểm (HVN-CUM.md mục 3)
    one('nq', '2026-11-23', 'nq_2026-11-23_phien.png', D=D, vm=vm)
    one('nq', '2026-11-23', 'nq_2026-11-23_phien_can_canh.png', zoom_u=1.5, hand=(26755 + 48, 26820 + 48), D=D, vm=vm)
    one('nq', '2026-11-20', 'nq_tuan_2026-11-16.png', kind='w', D=D, vm=vm)
    for d in ('2026-11-18', '2026-11-13', '2026-10-27'):
        one('nq', d, 'nq_%s_phien.png' % d, D=D, vm=vm)
    grid('nq', 'd', 'luoi_nq_phien.png', D, vm); grid('nq', 'w', 'luoi_nq_tuan.png', D, vm, last=9)
    D, vm = H.load('gc')
    for d in ('2026-10-29', '2026-11-03', '2026-10-21'):
        one('gc', d, 'gc_%s_phien.png' % d, D=D, vm=vm)
    one('gc', '2026-10-30', 'gc_tuan_2026-10-26.png', kind='w', D=D, vm=vm)
    grid('gc', 'd', 'luoi_gc_phien.png', D, vm); grid('gc', 'w', 'luoi_gc_tuan.png', D, vm, last=9)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
