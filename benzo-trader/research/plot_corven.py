# -*- coding: utf-8 -*-
"""plot_corven.py — vẽ một lệnh CORVEN để soi chart: nến M1 (~40 trước, ~30 sau), delta dưới nến, cạnh range, dải mốc,
dấu hiệu ③ đã đếm (đánh dấu tại nến neo), entry/SL/TP, nến CF. Không đọc dữ liệu ngoài những gì được truyền vào."""
from __future__ import annotations

import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

TICK = 0.1
SIGN_COLOR = dict(delta='#7b3fb5', bong='#0a7d38', kiet_suc='#c96a00', stacked='#1f5fbf', trap='#b5121b')
SIGN_LABEL = dict(delta='Δ', bong='bóng', kiet_suc='kiệt sức', stacked='stacked', trap='trap')


def plot_trade(df, f, t, c, outdir, tag, before=40, after=30):
    i = int(c.cf)
    ex = int(t['exit_idx'])
    a = max(0, min(i, c.ref) - before + 10, i - before)
    b = min(len(df), max(ex, i) + after)
    fig, ax = plt.subplots(figsize=(17, 8.5))
    xs = np.arange(a, b)
    for k in xs:  # noqa: B007
        o, h, l, cl = f.O[k] * TICK, f.H[k] * TICK, f.L[k] * TICK, f.C[k] * TICK
        up = cl >= o
        col = '#1b8a3a' if up else '#c0262d'
        ax.plot([k, k], [l, h], color=col, lw=1)
        ax.add_patch(plt.Rectangle((k - 0.32, min(o, cl)), 0.64, max(abs(cl - o), 0.03), color=col, fill=True,
                                   alpha=0.9 if not up else 0.55))
        ax.text(k, l - 0.12, f"{int(f.Dl[k]):+d}", ha='center', va='top', fontsize=5.5,
                color=('#1b8a3a' if f.Dl[k] > 0 else '#c0262d'))
    inst = c.inst
    top, bot = inst.top * TICK, inst.bottom * TICK
    ymin = min(f.L[a:b]) * TICK
    ymax = max(f.H[a:b]) * TICK
    for y in (top, bot, float(t['sl']), float(t['tp'])):
        if ymin - 3 <= y < ymin:
            ymin = y
        if ymax < y <= ymax + 3:
            ymax = y
    y0 = ymin - 0.8 - 0.45 * max(1, len(c.signs))
    y1 = ymax + 0.6
    ax.set_ylim(y0, y1)
    ax.axhline(top, color='#555', lw=1.0, ls='-', alpha=.7)
    ax.axhline(bot, color='#555', lw=1.0, ls='-', alpha=.7)
    if y0 < top < y1:
        ax.text(a, top, f" cạnh trên {top:.1f}", fontsize=7, va='bottom', color='#333')
    if y0 < bot < y1:
        ax.text(a, bot, f" cạnh dưới {bot:.1f}", fontsize=7, va='top', color='#333')
    for mo in c.mocs:
        lo, hi = mo['band'][0] * TICK, mo['band'][1] * TICK
        ax.axhspan(lo, hi, xmin=0, xmax=1, color='#f2c14e', alpha=0.18)
        lbl = 'mốc cạnh' if mo['kind'] == 'canh' else ('mốc stacked' if mo['kind'] == 'stacked' else 'mốc cực trị lần 1')
        if y0 < (lo + hi) / 2 < y1:
            ax.text(b - 1, (lo + hi) / 2, lbl + ' ±tol', fontsize=7, ha='right', va='center', color='#8a6d00')
        if mo['zid'] is not None:
            zb, zlo, zhi = mo['zid']
            ax.add_patch(plt.Rectangle((zb - 0.4, zlo * TICK - 0.05), i - zb + 0.8, (zhi - zlo) * TICK + 0.1,
                                       color='#1f5fbf' if c.S > 0 else '#c0262d', alpha=0.25))
    # cửa sổ test
    ax.axvspan(c.w0 - 0.5, i + 0.5, color='#999', alpha=0.08)
    ax.axvline(c.ref, color='#888', lw=0.8, ls=':')
    ax.text(c.ref, y1, ' nến đóng ngoài', fontsize=6, color='#666', va='top')
    # dấu hiệu
    for n, (typ, (desc, k, pt)) in enumerate(c.signs.items()):
        y = pt * TICK
        ax.plot([k], [y], marker='o', ms=9, mfc='none', mec=SIGN_COLOR[typ], mew=2)
        ax.annotate(f"{SIGN_LABEL[typ]}: {desc}", xy=(k, y), xytext=(a + 1, ymin - 0.6 - 0.45 * n), fontsize=7.5,
                    color=SIGN_COLOR[typ], arrowprops=dict(arrowstyle='-', color=SIGN_COLOR[typ], lw=0.6, alpha=.6))
    # lệnh
    e, sl, tp = float(t['entry']), float(t['sl']), float(t['tp'])
    ax.hlines(e, i, ex, color='#1f5fbf', lw=1.4, ls='--')
    ax.hlines(sl, i, ex, color='#c0262d', lw=1.4)
    ax.hlines(tp, i, ex, color='#1b8a3a', lw=1.4)
    ax.text(ex + 0.5, e, f"vào {e:.1f}", fontsize=7, color='#1f5fbf', va='center')
    ax.text(ex + 0.5, sl, f"SL {sl:.1f}", fontsize=7, color='#c0262d', va='center')
    ax.text(ex + 0.5, tp, f"TP {tp:.1f}", fontsize=7, color='#1b8a3a', va='center')
    ax.axvline(i, color='#1f5fbf', lw=0.8, alpha=.5)
    ax.axvline(ex, color='#9b27b0', lw=0.8, alpha=.5)
    ticks = list(range(a, b, 5))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(df['t_utc'].iloc[k])[5:16] for k in ticks], rotation=60, fontsize=6)
    ax.set_xlabel('giờ UTC (VN = UTC+7)', fontsize=7)
    side = 'BUY' if c.S > 0 else 'SELL'
    ax.set_title(f"{tag} · thế {c.the} {side} · {t['outcome']} R={float(t['r']):+.2f} · CF {str(t['t_utc'])[:16]} UTC "
                 f"({str(t['t_vn'])[11:16]} VN) · mốc {c.moc_used} · R sẵn {c.r_avail:.2f}"
                 + (" · range DEAD-ngay" if c.exhausted else ''), fontsize=9)
    ax.grid(alpha=.15)
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, f"{tag}_{str(t['t_utc'])[:16].replace(':', '').replace(' ', '_').replace('-', '')}_{c.the}_{side}.png")
    fig.tight_layout()
    fig.savefig(fn, dpi=85)
    plt.close(fig)
    return fn
