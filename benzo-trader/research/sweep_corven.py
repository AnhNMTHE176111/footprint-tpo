# -*- coding: utf-8 -*-
"""
sweep_corven.py — GĐ2 vòng 2 (plans/BENZO-CORVEN-plan.md mục 8.4): quét TỪNG tham số một quanh bộ vòng 1
(neo SL cú thủng / mốc, "lần 2" tắt). Mỗi ô đổi đúng MỘT tham số; C1 và C2 chạy lại cho đúng ô đó. Không lưới chéo.

Chạy:  PYTHONIOENCODING=utf-8 python sweep_corven.py     (≈ 5 phút) → chèn mục "GĐ2 vòng 2" vào report/RESULTS-CORVEN.md
                                                                     + report/_sweep_gd2v2.csv
⛔ CHỈ TRAIN (setup_corven.load_train cắt file trước khi tính).
"""
from __future__ import annotations

import os
import sys
from dataclasses import replace, asdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_corven as SC        # noqa: E402
import controls_corven as CC     # noqa: E402
from results_corven import stats, f2, TYPE_VN  # noqa: E402

REPORT = os.path.join(HERE, 'report')
NAN = float('nan')

# Lưới plan 8.4 (giá trị in đậm = ô mới). Plan ghi "14 ô mới" nhưng danh sách in đậm chỉ có 11 giá trị — làm đúng danh sách.
BASE = SC.CP()                                   # = bộ vòng 1: sl_anchor 'cu_thung', a2_on False
GRID = [('si_run', 4), ('bubble_mult', 4.0), ('delta_mult', 3.0), ('near_mbr', 0.5), ('near_mbr', 1.5),
        ('win_b', 2), ('win_b', 4), ('sl_buf_ticks', 2.0), ('sl_buf_ticks', 5.0), ('b_from_exhausted', False),
        ('need_signs', 3)]
PHASE_VN = dict(A='Á', EU='Âu', US='Mỹ')


def cells():
    """[(tên ô, CP)] — ô 0 là bộ gốc; mỗi ô sau đổi đúng một tham số."""
    out = [('gốc (vòng 1)', BASE)]
    for k, v in GRID:
        out.append((f'{k} = {v}', replace(BASE, **{k: v})))
    return out


def run_cell(bars, df, good, cp, nd):
    R = SC.run_gd1(bars, df, good, cp)
    t, ch = R['trades'], R['chosen']
    s = stats(t, nd)
    t1 = CC.c1(R)
    d2, all2 = CC.c2(R)
    c2 = float(d2['r_c2_tb'].mean()) if len(d2) else NAN
    the = np.array([c.the for c in ch])
    nsg = np.array([len(c.types) for c in ch])
    ph = t['phase'].to_numpy() if len(t) else np.array([])
    risk_px = np.array([c.risk * SC.TICK for c in ch])
    out = dict(s=s, c1=stats(t1, nd), c2=c2, c2_pair=float((d2['r_that'] - d2['r_c2_tb']).mean()) if len(d2) else NAN,
               A=stats(t[the == 'A'], nd), B=stats(t[the == 'B'], nd),
               phase={p: dict(st=stats(t[ph == p], nd), risk=float(np.median(risk_px[ph == p])) if (ph == p).any() else NAN)
                      for p in ('A', 'EU', 'US')},
               nsig={int(k): stats(t[nsg == k], nd) for k in sorted(set(nsg))},
               stacked=float(np.mean(['stacked' in c.types for c in ch])) if ch else NAN,
               trades=t, chosen=ch)
    a = s.get('n', 0) > 0 and s['avg'] >= out['c1'].get('avg', NAN) - 1e-12 and s['avg'] >= c2 - 1e-12
    out['ok_a'] = bool(a)
    out['ok_c'] = s.get('n', 0) >= 35
    return out


def _g(s, k='avg', p=2):
    v = s.get(k, NAN) if s else NAN
    return f2(v, p) if v == v else '–'


def render(res, nd):
    L = ['# GĐ2 vòng 2 — quét từng tham số quanh bộ vòng 1 (plan 8.4)', '',
         '> Bộ gốc = vòng 1: neo SL cú thủng / mốc, "lần 2" tắt. Mỗi ô đổi **đúng một** tham số; C1 (bỏ ③) và C2 (ngẫu nhiên cùng '
         'phiên/giờ ±30′/hướng/rủi ro mbr, 20 nến mỗi lệnh) **chạy lại cho từng ô**. Không lưới chéo. Chỉ TRAIN (35 phiên dày).',
         '> (a) = R TB ≥ C1 **và** ≥ C2 của chính ô · (c) = n ≥ 35. Điều kiện (b) (hai hàng xóm không đổi dấu) xét ở vòng 3.',
         '> Plan 8.4 ghi "14 ô mới" nhưng danh sách giá trị in đậm chỉ có **11** ô — đã làm đúng 11 ô của danh sách (xem mục cuối).', '',
         '| Ô | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD | C1 | C2 | (a) | (c) | thế A | thế B | Á | Âu | Mỹ |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for name, cp, r in res:
        s = r['s']
        hint = ' *(hậu kiểm)*' if name.startswith('need_signs') else ''
        L.append(f"| {name}{hint} | {s.get('n', 0)} | {_g(s, 'per_day')} | {f2(100 * s['wr'], 1) + ' %' if s.get('n') else '–'} | "
                 f"**{_g(s)}** | [{_g(s, 'lo')}; {_g(s, 'hi')}] | {_g(s, 'sum', 1)} | {_g(s, 'dd', 1)} | {_g(r['c1'])} | "
                 f"{f2(r['c2']) if r['c2'] == r['c2'] else '–'} | {'✅' if r['ok_a'] else '✗'} | {'✅' if r['ok_c'] else '✗'} | "
                 f"{_g(r['A'])} ({r['A'].get('n', 0)}) | {_g(r['B'])} ({r['B'].get('n', 0)}) | "
                 + ' | '.join(f"{_g(r['phase'][p]['st'])} ({r['phase'][p]['st'].get('n', 0)})" for p in ('A', 'EU', 'US')) + ' |')
    both = [name for name, _, r in res if r['ok_a'] and r['ok_c']]
    L += ['', f"**Ô đạt cả (a) và (c): {', '.join(both) if both else 'không có'}.**", '']
    L += ['## Phụ lục — chi tiết theo ô', '']
    for name, cp, r in res:
        s = r['s']
        L += [f'### {name}', '',
              f"n {s.get('n', 0)} · lệnh/ngày {_g(s, 'per_day')} · WR {f2(100 * s['wr'], 1) + ' %' if s.get('n') else '–'} · "
              f"R TB {_g(s)} [{_g(s, 'lo')}; {_g(s, 'hi')}] · ΣR {_g(s, 'sum', 1)} · max DD {_g(s, 'dd', 1)} · chuỗi thua {s.get('streak', '–')} · "
              f"C1 {_g(r['c1'])} (n {r['c1'].get('n', 0)}) · C2 {f2(r['c2']) if r['c2'] == r['c2'] else '–'} (theo cặp R thật − C2 = "
              f"{f2(r['c2_pair']) if r['c2_pair'] == r['c2_pair'] else '–'}) · stacked có mặt {f2(100 * r['stacked'], 1) if r['stacked'] == r['stacked'] else '–'} % lệnh", '',
              '| Nhóm | n | WR | R TB | KTC 95 % | rủi ro trung vị (giá) |', '|---|---|---|---|---|---|']
        for lab, st, rk in [('thế A', r['A'], None), ('thế B', r['B'], None)] + \
                [(f'phiên {PHASE_VN[p]}', r['phase'][p]['st'], r['phase'][p]['risk']) for p in ('A', 'EU', 'US')] + \
                [(f'{k} loại dấu hiệu', v, None) for k, v in r['nsig'].items()]:
            L.append(f"| {lab} | {st.get('n', 0)} | {f2(100 * st['wr'], 1) + ' %' if st.get('n') else '–'} | {_g(st)} | "
                     f"[{_g(st, 'lo')}; {_g(st, 'hi')}] | {f2(rk) if rk is not None and rk == rk else ''} |")
        L.append('')
    return L


def insert_into_results(L, path=os.path.join(REPORT, 'RESULTS-CORVEN.md')):
    """Chèn (hoặc thay) mục '# GĐ2 vòng 2' ngay trước '# GĐ2 vòng 1'."""
    old = open(path, encoding='utf-8').read().splitlines()
    if any(x.startswith('# GĐ2 vòng 2') for x in old):
        a = next(i for i, x in enumerate(old) if x.startswith('# GĐ2 vòng 2'))
        b = next(i for i, x in enumerate(old) if x.startswith('# GĐ2 vòng 1'))
        old = old[:a] + old[b:]
    k = next(i for i, x in enumerate(old) if x.startswith('# GĐ2 vòng 1'))
    new = old[:k] + L + ['---', ''] + old[k:]
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(new) + '\n')


def main():
    cut = SC.train_cut()
    bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    nd = len(set(df['session_id'].to_numpy()[good]))
    res = []
    rows = []
    for name, cp in cells():
        r = run_cell(bars, df, good, cp, nd)
        res.append((name, cp, r))
        s = r['s']
        rows.append(dict(o=name, n=s.get('n', 0), per_day=s.get('per_day', NAN), wr=s.get('wr', NAN), r_tb=s.get('avg', NAN),
                         ktc_lo=s.get('lo', NAN), ktc_hi=s.get('hi', NAN), sum_r=s.get('sum', NAN), max_dd=s.get('dd', NAN),
                         c1=r['c1'].get('avg', NAN), c2=r['c2'], dat_a=r['ok_a'], dat_c=r['ok_c'],
                         r_A=r['A'].get('avg', NAN), r_B=r['B'].get('avg', NAN),
                         **{f'r_{PHASE_VN[p]}': r['phase'][p]['st'].get('avg', NAN) for p in ('A', 'EU', 'US')},
                         **{f'rui_ro_{PHASE_VN[p]}': r['phase'][p]['risk'] for p in ('A', 'EU', 'US')}))
        print(name, s.get('n', 0), round(s.get('avg', NAN), 3), 'C1', round(r['c1'].get('avg', NAN), 3), 'C2', round(r['c2'], 3), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(REPORT, '_sweep_gd2v2.csv'), index=False, encoding='utf-8')
    L = render(res, nd)
    L += open(os.path.join(REPORT, '_corven_gd2v2_notes.md'), encoding='utf-8').read().splitlines() + ['']
    insert_into_results(L)
    return res


if __name__ == '__main__':
    main()
