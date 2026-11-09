# -*- coding: utf-8 -*-
"""Đo (TRAIN ≤ 15/9) luật người học 2026-11-09: Break không vào nếu giá entry nằm TRONG một range khác còn sống
(phải phá hẳn khỏi cả range chồng). Xấp xỉ: range còn sống = đã sinh ≤ nến xác nhận < nến chết; biên = top/bottom cuối của range.
Hậu xử lý ứng viên corven-6 (cả 2 chế độ SL) → chọn lệnh. Opus đo."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import setup_corven as SC, controls_corven as CC


def apply(R, also_fail_break=False, pad_ticks=0):
    m, f, cp, df = R['m'], R['feat'], R['cp'], R['df']
    rng = m.eng.ranges
    out = []
    for c0 in R['cands']:
        c = SC.Cand(**{k: getattr(c0, k) for k in ('cf', 'the', 'S', 'rid', 'inst', 'key', 'ref', 'w0', 'mocs', 'trap_levels', 'exhausted')})
        for k in ('signs', 'entry', 'sl', 'risk', 'tp', 'moc_used', 'r_avail', 'target'):
            setattr(c, k, getattr(c0, k))
        c.gates = list(c0.gates)
        if c.the == 'B' or (also_fail_break and c.the == 'A'):
            for rid, bi in m.birth.items():
                if rid == c.rid or bi > c.cf or m.death.get(rid, 10 ** 9) <= c.cf:
                    continue
                r = rng[rid]
                if r.bottom - pad_ticks <= c.entry <= r.top + pad_ticks:
                    c.gates.append('trong_range_khac'); break
        out.append(c)
    tr, ch, why = SC.select_and_simulate(out, df, f, cp)
    return dict(R, cands=out, trades=tr, chosen=ch, why=why)


def summ(R, sg):
    t = R['trades']
    h = t['session_id'].map(lambda s: sg.index(s) < len(sg) // 2)
    c2, _ = CC.c2(R, after_only=True)
    b = t['setup'] == 'B'
    return dict(n=len(t), nB=int(b.sum()), R=t['r'].mean(), RB=t.loc[b, 'r'].mean(), WR=(t['r'] > 0).mean(),
                h1=t.loc[h, 'r'].mean(), h2=t.loc[~h, 'r'].mean(), C2p=c2['r_c2_tb'].mean(), sumR=t['r'].sum())


if __name__ == '__main__':
    cut = SC.train_cut(); bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sg = sorted(set(df['session_id'].to_numpy()[good]))
    rows = []
    for mode in (False, True):
        R0 = SC.run_gd1(bars, df, good, SC.cp_live(sl_kieu_cu=mode))
        for name, kw in (('hiện tại', None), ('Break: entry trong range khác ⇒ bỏ', {}),
                         ('… + cả Fail Break', dict(also_fail_break=True))):
            R = R0 if kw is None else apply(R0, **kw)
            s = summ(R, sg); s.update(sl='cũ' if mode else 'mới', bien_the=name); rows.append(s); print(s, flush=True)
    out = pd.DataFrame(rows)[['sl', 'bien_the', 'n', 'nB', 'R', 'RB', 'WR', 'h1', 'h2', 'C2p', 'sumR']]
    print(out.round(3).to_string())
    out.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report', '_variants_range_chong.csv'), index=False)
