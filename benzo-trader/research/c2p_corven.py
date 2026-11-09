# -*- coding: utf-8 -*-
"""
c2p_corven.py — plans/BENZO-FOLLOW-COMBO-plan.md 9.3-A3: đo C2' (controls_corven.c2 after_only=True: chỉ nến trong 30′ SAU CF)
cho BỘ GỐC VÒNG 1 của setup CORVEN (neo SL cú thủng / mốc, "lần 2" tắt — ô đang in −0,29R trên Benzo corven-1), trên TRAIN.
Báo C2 cũ / C2' / R thật / C1 trong một bảng + nhánh (a)/(b) của 9.1-3 theo đúng công thức đăng ký trước.

Chạy:  PYTHONIOENCODING=utf-8 python c2p_corven.py   → in bảng markdown + report/_c2p_corven.json
⛔ CHỈ TRAIN (setup_corven.load_train cắt file trước khi tính).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_corven as SC        # noqa: E402
import controls_corven as CC     # noqa: E402
from results_corven import stats, f2  # noqa: E402

REPORT = os.path.join(HERE, 'report')


def ci(x, seed=0):
    x = np.asarray(x, float)
    bs = np.random.default_rng(seed).choice(x, size=(10000, len(x))).mean(axis=1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def branch(r_that: float, c2p: float) -> str:
    """9.1-3: (a) nếu R < C2' − 0,05 ⇒ nhãn "kém vào ngẫu nhiên" GIỮ; (b) nếu R ≥ C2' − 0,05 ⇒ đổi nhãn."""
    return 'a' if r_that < c2p - 0.05 else 'b'


def main():
    cut = SC.train_cut()
    bars, df = SC.load_train(cut=cut)
    assert str(df['datetime'].iloc[-1])[:10] <= '2026-09-15'
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    nd = len(set(df['session_id'].to_numpy()[good]))
    R = SC.run_gd1(bars, df, good, SC.CP())            # bộ gốc vòng 1 (sl_anchor 'cu_thung', a2_on False)
    t = R['trades']
    s = stats(t, nd)
    s1 = stats(CC.c1(R), nd)
    out = dict(n=int(s['n']), r=float(s['avg']), c1=float(s1['avg']), n_c1=int(s1['n']))
    rows = []
    for nm, kw in (('C2 cũ (±30′ quanh CF)', {}), ("C2' (chỉ 30′ SAU CF)", dict(after_only=True))):
        d2, allr = CC.c2(R, **kw)
        m = float(d2['r_c2_tb'].mean())
        lo, hi = ci(d2['r_c2_tb'].to_numpy())
        pair = float((d2['r_that'] - d2['r_c2_tb']).mean())
        # theo thế (A / B) — cùng chỉ số lệnh
        the = {c.cf: c.the for c in R['chosen']}
        byt = {}
        for th in ('A', 'B'):
            sel = d2[[the.get(int(i), '')[:1] == th for i in d2['idx']]]
            byt[th] = (float(sel['r_c2_tb'].mean()) if len(sel) else float('nan'), len(sel))
        rows.append(dict(ten=nm, n_lenh=len(d2), n_gia=len(allr), avg=m, lo=lo, hi=hi, pair=pair,
                         wr=float((allr > 0).mean()), byA=byt['A'], byB=byt['B']))
    out['c2_old'] = rows[0]['avg']
    out['c2p'] = rows[1]['avg']
    out['c2p_n_lenh'] = rows[1]['n_lenh']
    out['branch'] = branch(out['r'], out['c2p'])
    # R thật theo thế
    rA = t[[c.the[:1] == 'A' for c in R['chosen']]]['r']
    rB = t[[c.the[:1] == 'B' for c in R['chosen']]]['r']
    L = ['| Đo trên bộ gốc vòng 1 (TRAIN 35 phiên) | n lệnh thật đối chứng được | lệnh giả | WR lệnh giả | R TB | KTC 95 % | '
         'R thật − đối chứng (theo cặp) | thế A | thế B |', '|---|---|---|---|---|---|---|---|---|',
         f"| **R thật CORVEN** | {s['n']} | – | {f2(100 * s['wr'], 1)} % | **{f2(s['avg'])}** | [{f2(s['lo'])}; {f2(s['hi'])}] | – | "
         f"{f2(rA.mean())} ({len(rA)}) | {f2(rB.mean())} ({len(rB)}) |",
         f"| C1 — bỏ ③ | {s1['n']} | – | {f2(100 * s1['wr'], 1)} % | {f2(s1['avg'])} | [{f2(s1['lo'])}; {f2(s1['hi'])}] | – | – | – |"]
    for r in rows:
        L.append(f"| {r['ten']} | {r['n_lenh']} | {r['n_gia']} | {f2(100 * r['wr'], 1)} % | **{f2(r['avg'])}** | [{f2(r['lo'])}; {f2(r['hi'])}] | "
                 f"{f2(r['pair'])} | {f2(r['byA'][0])} ({r['byA'][1]}) | {f2(r['byB'][0])} ({r['byB'][1]}) |")
    out['rows'] = rows
    with open(os.path.join(REPORT, '_c2p_corven.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
    print('\n'.join(L))
    print()
    print(f"R thật {f2(out['r'], 3)} · C2' {f2(out['c2p'], 3)} · C2' − 0,05 = {f2(out['c2p'] - 0.05, 3)} ⇒ nhánh ({out['branch']})")
    return out, L


if __name__ == '__main__':
    main()
