# -*- coding: utf-8 -*-
"""Vẽ 2 phiên (một đi ngang, một xu hướng) — nến M1 + khối vùng lịch sử (lich_su.track = port LichSuTracker) + signal Benzo.
Mô phỏng lớp tiêu điểm (PLAN-LICH-SU 2.5): tiêu điểm = nến signal đầu tiên của phiên; khối sống tại đó tô đậm + nhãn lo–hi, khối khác mờ.
Thêm (PLAN-LOC-VUNG 3.2) bản 2 hạng → report/img/loc_vung_*.png: hạng 1 tô từ nến lên hạng (đuôi trước đó viền mờ), hạng 2 chỉ viền mảnh khi
sống tại tiêu điểm (khối khác ẩn).
Chạy: python3 ve_lich_su.py  (cần report/vcl5_cs_replay_v5.csv — chạy lich_su.py trước)  → report/img/lich_su_*.png + loc_vung_*.png"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import lich_su as LS

RES, SUP, GREY = '#dc463c', '#28aa64', '#8c8c8c'


def pick_sessions(D, mins, sig_idx):
    dt = np.diff(mins, prepend=mins[0])
    sess = np.cumsum(dt > LS.GAP_MINUTES)
    rows = []
    for s in np.unique(sess):
        ii = np.where(sess == s)[0]
        if len(ii) < 600:
            continue
        sg = [i for i in sig_idx if ii[0] <= i <= ii[-1]]
        if not sg:
            continue
        rng = D['H'][ii].max() - D['L'][ii].min()
        net = abs(D['C'][ii[-1]] - D['O'][ii[0]])
        rows.append((net / rng, int(s), ii[0], ii[-1], sg))
    rows.sort()
    return [('di-ngang',) + rows[0][1:], ('xu-huong',) + rows[-1][1:]]


def draw(D, allz, kind, s, a, b, sg, out):
    t = pd.to_datetime(D['t'])
    O, H, L, C = D['O'], D['H'], D['L'], D['C']
    n = D['n']
    tf = sg[0]
    fig, ax = plt.subplots(figsize=(22, 10), dpi=110)
    fig.patch.set_facecolor('#0e1016'); ax.set_facecolor('#0e1016')
    x = np.arange(a, b + 1)
    up = C[a:b + 1] >= O[a:b + 1]
    ax.vlines(x, L[a:b + 1], H[a:b + 1], color='#9aa0aa', lw=0.5)
    ax.vlines(x[up], O[a:b + 1][up], C[a:b + 1][up], color='#cfd3da', lw=1.6)
    ax.vlines(x[~up], C[a:b + 1][~up], O[a:b + 1][~up], color='#5c6270', lw=1.6)
    nshow = 0; nfocus = 0
    for h in allz:
        e = h['end'] if h['end'] >= 0 else n - 1
        if e < a or h['start'] > b:
            continue
        nshow += 1
        x0, x1 = max(a, h['start']), min(b, e) + 1
        col = RES if h['vai'] == 1 else (SUP if h['vai'] == -1 else GREY)
        focus = h['start'] <= tf <= e
        nfocus += focus
        ax.add_patch(Rectangle((x0, h['lo']), x1 - x0, h['hi'] - h['lo'], facecolor=col, alpha=55 / 255 if focus else 18 / 255,
                               edgecolor=col, lw=0.8 if focus else 0.4))
        if focus and (D['t'][e] - D['t'][h['start']]) / np.timedelta64(1, 'm') >= LS.LS_LABEL_MIN:
            ax.text(x0 + 1, (h['lo'] + h['hi']) / 2, f"{h['lo']:.1f}–{h['hi']:.1f}".replace('.', ','), color='white', fontsize=7, va='center')
    for i in sg:
        ax.plot([i], [L[i] - 0.8], marker='^', color='#ffd166', ms=8)
    ax.axvline(tf, color='white', alpha=60 / 255, lw=1)
    ticks = np.linspace(a, b, 12).astype(int)
    ax.set_xticks(ticks); ax.set_xticklabels([t[i].strftime('%m-%d %H:%M') for i in ticks], color='#9aa0aa', fontsize=8)
    ax.tick_params(colors='#9aa0aa')
    ax.set_xlim(a - 2, b + 2)
    ax.set_ylim(L[a:b + 1].min() - 3, H[a:b + 1].max() + 3)
    ax.set_title(f"Vùng lịch sử — phiên {kind} {t[a]:%Y-%m-%d} (UTC): {nshow} khối trong phiên · tiêu điểm {t[tf]:%H:%M} (signal Benzo) có {nfocus} khối sống",
                 color='white', fontsize=11)
    fig.tight_layout(); fig.savefig(out, facecolor=fig.get_facecolor()); plt.close(fig)
    return nshow, nfocus


def draw_hang(D, allz, kind, s, a, b, sg, out):
    """Mô phỏng PaintLichSu 2 hạng (PLAN-LOC-VUNG 3.2), tiêu điểm = signal đầu tiên của phiên. Trả (khối hạng 1 thấy trong phiên, đậm, mảnh tại tF)."""
    t = pd.to_datetime(D['t'])
    O, H, L, C = D['O'], D['H'], D['L'], D['C']
    n = D['n']
    tf = sg[0]
    fig, ax = plt.subplots(figsize=(22, 10), dpi=110)
    fig.patch.set_facecolor('#0e1016'); ax.set_facecolor('#0e1016')
    x = np.arange(a, b + 1)
    up = C[a:b + 1] >= O[a:b + 1]
    ax.vlines(x, L[a:b + 1], H[a:b + 1], color='#9aa0aa', lw=0.5)
    ax.vlines(x[up], O[a:b + 1][up], C[a:b + 1][up], color='#cfd3da', lw=1.6)
    ax.vlines(x[~up], C[a:b + 1][~up], O[a:b + 1][~up], color='#5c6270', lw=1.6)
    nh1 = 0; ndam = 0; nmong = 0
    def box(x0, x1, lo, hi, col, fa, ea, lw):
        if x1 <= x0:
            return
        ax.add_patch(Rectangle((x0, lo), x1 - x0, hi - lo, facecolor=col if fa else 'none', alpha=None, edgecolor=col, lw=lw))
        if fa:
            ax.patches[-1].set_facecolor(matplotlib.colors.to_rgba(col, fa / 255))
        ax.patches[-1].set_edgecolor(matplotlib.colors.to_rgba(col, ea / 255))
    def lbl(x0, h):
        ax.text(x0 + 1, (h['lo'] + h['hi']) / 2, f"{h['lo']:.1f}–{h['hi']:.1f}".replace('.', ','), color='white', fontsize=7, va='center')
    for h in allz:
        e = h['end'] if h['end'] >= 0 else n - 1
        if e < a or h['start'] > b:
            continue
        col = RES if h['vai'] == 1 else (SUP if h['vai'] == -1 else GREY)
        alive = h['start'] <= tf <= e
        h1 = h['tq'] >= 0
        ve = 0 if not alive else (1 if h1 and h['tq'] <= tf else 2)
        ndam += ve == 1; nmong += ve == 2
        if h1 and h['tq'] <= b:
            nh1 += 1
        if not h1 and ve == 0:
            continue
        x0, x1 = max(a, h['start']), min(b, e) + 1
        xq = max(a, h['tq']) if h1 else x1
        life = (D['t'][e] - D['t'][h['start']]) / np.timedelta64(1, 'm')
        if xq > x0:
            box(x0, min(xq, x1), h['lo'], h['hi'], col, 0, 90 if ve == 2 else 40, 0.6)
        if h1 and xq < x1:
            box(xq, x1, h['lo'], h['hi'], col, 55 if ve == 1 else 35, 150 if ve == 1 else 110, 0.8)
        if life >= LS.LS_LABEL_MIN:
            if ve == 2:
                lbl(x0, h)
            elif h1 and xq < x1:
                lbl(xq, h)
    for i in sg:
        ax.plot([i], [L[i] - 0.8], marker='^', color='#ffd166', ms=8)
    ax.axvline(tf, color='white', alpha=60 / 255, lw=1)
    ticks = np.linspace(a, b, 12).astype(int)
    ax.set_xticks(ticks); ax.set_xticklabels([t[i].strftime('%m-%d %H:%M') for i in ticks], color='#9aa0aa', fontsize=8)
    ax.tick_params(colors='#9aa0aa')
    ax.set_xlim(a - 2, b + 2)
    ax.set_ylim(L[a:b + 1].min() - 3, H[a:b + 1].max() + 3)
    ax.set_title(f"Lọc 2 hạng — phiên {kind} {t[a]:%Y-%m-%d} (UTC): {nh1} khối hạng 1 (tô từ nến lên hạng; đuôi trước đó viền mờ) · "
                 f"tiêu điểm {t[tf]:%H:%M} (signal Benzo): {ndam} khối đậm + {nmong} viền mảnh (hạng 2 / chưa lên hạng)", color='white', fontsize=11)
    fig.tight_layout(); fig.savefig(out, facecolor=fig.get_facecolor()); plt.close(fig)
    return nh1, ndam, nmong


def main():
    D = LS.load(LS.BASE90, os.path.join(LS.REP, 'vcl5_cs_replay_v5.csv'))
    allz, st, mins = LS.track(D)
    sig = pd.read_csv(LS.SIGNALS)
    stt = pd.to_datetime(sig['time_utc']).to_numpy()
    stt = stt[(stt >= D['t'][0]) & (stt <= D['t'][-1])]
    sig_idx = sorted(set(np.searchsorted(D['t'], stt).tolist()))
    os.makedirs(os.path.join(LS.REP, 'img'), exist_ok=True)
    for kind, s, a, b, sg in pick_sessions(D, mins, sig_idx):
        out = os.path.join(LS.REP, 'img', f"lich_su_{kind}_{pd.Timestamp(D['t'][a]):%Y-%m-%d}.png")
        nshow, nfocus = draw(D, allz, kind, s, a, b, sg, out)
        print(f'{kind}: phiên {s}, nến {a}–{b}, {len(sg)} signal, {nshow} khối, tiêu điểm {nfocus} khối → {out}')
        out2 = os.path.join(LS.REP, 'img', f"loc_vung_{kind}_{pd.Timestamp(D['t'][a]):%Y-%m-%d}.png")
        nh1, ndam, nmong = draw_hang(D, allz, kind, s, a, b, sg, out2)
        print(f'  2 hạng: {nh1} khối hạng 1 trong phiên, tiêu điểm {ndam} đậm + {nmong} viền mảnh → {out2}')


if __name__ == '__main__':
    main()
