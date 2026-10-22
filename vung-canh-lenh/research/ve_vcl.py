# -*- coding: utf-8 -*-
"""Vẽ 4 phiên (2 TRAIN, 2 TEST): nến M1 + vùng hiển thị (gộp 1,0u) + nhãn loại·điểm.
Đỏ = vùng phía trên giá (kháng cự), xanh = phía dưới (hỗ trợ); tô đậm = 2 vùng gần, tô nhạt viền đứt = vùng xa vừa phải.
Chạy sau vcl.py (đọc report/vcl_records_1.0.csv.gz; chưa có thì tự chạy engine).  python3 ve_vcl.py
Vòng 2: python3 ve_vcl.py --vong 2  (đọc report/vcl2_records.csv.gz) → report/img/v2_*.png"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
import vcl
import vcl2
import vcl3
import vcl4

VONG = int(sys.argv[sys.argv.index('--vong') + 1]) if '--vong' in sys.argv else 1

SESSIONS = {'TRAIN': ['2026-08-20', '2026-09-01'], 'TEST': ['2026-09-08', '2026-09-11']}
OUT = os.path.join(vcl.REPORT, 'img')
UP, DN, INK, MUTED, KCOL = '#c0392b', '#1e8449', '#222222', '#888888', '#d68910'


def types_of(mask):
    T, B = {1: (vcl.TYPES, vcl.BIT), 2: (vcl2.TYPES, vcl2.BIT), 3: (vcl3.TYPES, vcl3.BIT), 4: (vcl3.TYPES, vcl3.BIT)}[VONG]
    return '+'.join(t for t in T if mask & B[t])


def draw(ctx, rec, sid, split):
    df, st = ctx['df'], ctx['st']
    s = int(st.index[st['session_id'] == sid][0])
    a, b = int(st.loc[s, 'start_pos']), int(st.loc[s, 'end_pos'])
    d = df.iloc[a:b + 1]
    x = np.arange(len(d))
    O, H, L, C = (d[c].to_numpy(float) for c in ('open', 'high', 'low', 'close'))
    r = rec[(rec['bar'] >= a) & (rec['bar'] <= b)]
    fig, ax = plt.subplots(figsize=(30, 12), dpi=110)
    # vùng: mỗi nến một ô chữ nhật
    for slot, alpha in (('F', 0.13), ('N', 0.28), ('K', 0.35)):
        rr = r[r['slot'] == slot]
        xs = rr['bar'].to_numpy() - a
        polys = [[(xx - .5, lo), (xx + .5, lo), (xx + .5, hi), (xx - .5, hi)]
                 for xx, lo, hi in zip(xs, rr['lo'].to_numpy(), rr['hi'].to_numpy())]
        cols = [UP if sd == 1 else (DN if sd == -1 else KCOL) for sd in rr['side'].to_numpy()]
        ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors='none', alpha=alpha,
                                         linestyle='--' if slot == 'F' else '-'))
    # nhãn: đầu mỗi vùng hiển thị >= 30 nến
    g = r.groupby('eid')
    for eid, e in g:
        if len(e) < 30:
            continue
        f = e.iloc[0]
        ax.text(f['bar'] - a, f['hi'], f"{types_of(int(f['mask']))}·{f['score']:.0f}", fontsize=7.5,
                color=INK, va='bottom', ha='left', clip_on=True)
    # nến
    upc = C >= O
    ax.add_collection(LineCollection([[(xx, l), (xx, h)] for xx, l, h in zip(x, L, H)], colors=INK, linewidths=0.6))
    ax.bar(x[upc], (C - O)[upc], bottom=O[upc], width=0.7, color='white', edgecolor=INK, linewidth=0.5)
    ax.bar(x[~upc], (O - C)[~upc], bottom=C[~upc], width=0.7, color=INK, edgecolor=INK, linewidth=0.5)
    ax.set_xlim(-2, len(d) + 1)
    ax.set_ylim(L.min() - 2, H.max() + 2)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(1))
    ax.grid(True, which='major', color='#dddddd', linewidth=0.6)
    ax.grid(True, which='minor', axis='y', color='#f2f2f2', linewidth=0.4)
    tv = d['t_vn'].dt.strftime('%H:%M').to_numpy()
    tick = np.flatnonzero(d['t_vn'].dt.minute.to_numpy() == 0)
    ax.set_xticks(tick)
    ax.set_xticklabels([tv[t] for t in tick], fontsize=9)
    ax.tick_params(axis='y', labelsize=9, labelright=True)
    ax.set_xlabel('giờ VN (UTC+7)', color=MUTED)
    u = vcl.K.median_range(df).to_numpy()[a:b + 1]
    ax.set_title(f'VCL vòng {VONG} · GCZ26 M1 · phiên {sid} ({split}) · gộp 1,0u · u trung vị {np.nanmedian(u):.2f} USD · '
                 'đỏ = vùng trên giá, xanh = vùng dưới giá' + (', cam = vùng đang chứa giá' if VONG >= 3 else '') + '; đậm = 2 vùng gần, nhạt = vùng xa vừa phải; nhãn = loại·điểm',
                 fontsize=11, loc='left')
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, (f'v{VONG}_{split}_{sid}.png' if VONG >= 2 else f'vcl_{split}_{sid}.png'))
    fig.tight_layout()
    fig.savefig(p)
    plt.close(fig)
    return p


def main():
    bars, lv = vcl.load_all()
    ctx = vcl.prepare(bars, lv)
    if VONG == 4:
        path = os.path.join(vcl.REPORT, 'vcl4_records.csv.gz')
        rec = pd.read_csv(path) if os.path.exists(path) else vcl4.run_engine(ctx)['rec']
    elif VONG == 3:
        path = os.path.join(vcl.REPORT, 'vcl3_records.csv.gz')
        rec = pd.read_csv(path) if os.path.exists(path) else vcl3.run_engine(ctx)['rec']
    elif VONG == 2:
        path = os.path.join(vcl.REPORT, 'vcl2_records.csv.gz')
        rec = pd.read_csv(path) if os.path.exists(path) else vcl2.run_engine(ctx)['rec']
    else:
        path = os.path.join(vcl.REPORT, f'vcl_records_{vcl.MAIN_LINK}.csv.gz')
        rec = pd.read_csv(path) if os.path.exists(path) else vcl.run_engine(ctx, vcl.MAIN_LINK)['rec']
    for split, sids in SESSIONS.items():
        for sid in sids:
            print(draw(ctx, rec, sid, split))


if __name__ == '__main__':
    main()
