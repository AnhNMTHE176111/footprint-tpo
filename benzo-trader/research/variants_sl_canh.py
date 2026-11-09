# -*- coding: utf-8 -*-
"""Đo (TRAIN ≤ 15/9) feedback người học 2026-11-09: SL Break = cạnh vừa phá ± 3 tick (bỏ râu nhịp hồi, bỏ đệm theo biên độ),
và trần SL theo GIÁ (mặc định 5). Hậu xử lý ứng viên corven-5 → chọn lệnh. Opus đo."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import setup_corven as SC, controls_corven as CC


def apply(R, sl_canh=False, floor=True, cap_gia=None, keep_mbr_cap=True):
    f, cp, df = R['feat'], R['cp'], R['df']
    out = []
    for c0 in R['cands']:
        c = SC.Cand(**{k: getattr(c0, k) for k in ('cf', 'the', 'S', 'rid', 'inst', 'key', 'ref', 'w0', 'mocs', 'trap_levels', 'exhausted')})
        c.signs = c0.signs
        c.gates = [g for g in c0.gates if g != 'tran_sl']
        c.entry, c.sl, c.risk, c.tp, c.moc_used = c0.entry, c0.sl, c0.risk, c0.tp, c0.moc_used
        mbr, S, ent = f.mbr[c.cf], c.S, c.entry
        if sl_canh and c.the == 'B' and c.moc_used == 'canh':
            raw = c.inst.E - S * 3
            risk = (ent - raw) * S
            if floor and risk < cp.sl_floor_mbr * mbr:
                risk = cp.sl_floor_mbr * mbr
            sl = ent - S * risk
            c.sl = int(np.floor(sl + 1e-9)) if S > 0 else int(np.ceil(sl - 1e-9))
            c.risk = float((ent - c.sl) * S)
            c.tp = ent + S * cp.tp_r * c.risk
        if keep_mbr_cap and c.risk > cp.sl_cap_mbr * mbr + 1e-9:
            c.gates.append('tran_sl')
        if cap_gia is not None and c.risk > cap_gia * 10 + 1e-9:
            c.gates.append('tran_sl_gia')
        if c.risk <= 0:
            c.gates.append('sl_sai')
        out.append(c)
    tr, ch, why = SC.select_and_simulate(out, df, f, cp)
    return dict(R, cands=out, trades=tr, chosen=ch, why=why)


def summ(R, sg):
    t = R['trades']
    h = t['session_id'].map(lambda s: sg.index(s) < len(sg) // 2)
    c2, _ = CC.c2(R, after_only=True)
    return dict(n=len(t), R=t['r'].mean(), WR=(t['r'] > 0).mean(), h1=t.loc[h, 'r'].mean(), h2=t.loc[~h, 'r'].mean(),
                C2p=c2['r_c2_tb'].mean(), risk_med=t['risk_pts'].median(), risk_max=t['risk_pts'].max(), sumR=t['r'].sum())


if __name__ == '__main__':
    cut = SC.train_cut(); bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sg = sorted(set(df['session_id'].to_numpy()[good]))
    R0 = SC.run_gd1(bars, df, good, SC.cp_live())
    V = [('corven-5', {}),
         ('trần SL 5 giá', dict(cap_gia=5)),
         ('SL = cạnh ± 3 tick', dict(sl_canh=True)),
         ('SL = cạnh ± 3 tick + trần 5 giá', dict(sl_canh=True, cap_gia=5)),
         ('… + bỏ sàn 1 biên độ', dict(sl_canh=True, cap_gia=5, floor=False)),
         ('… + bỏ trần 4 biên độ (chỉ trần 5 giá)', dict(sl_canh=True, cap_gia=5, keep_mbr_cap=False)),
         ('SL cạnh ± 3 tick + trần 3 giá', dict(sl_canh=True, cap_gia=3)),
         ('SL cạnh ± 3 tick + trần 4 giá', dict(sl_canh=True, cap_gia=4)),
         ('SL cạnh ± 3 tick + trần 6 giá', dict(sl_canh=True, cap_gia=6)),
         ('SL cạnh ± 3 tick + trần 8 giá', dict(sl_canh=True, cap_gia=8))]
    rows = []
    for name, kw in V:
        s = summ(apply(R0, **kw), sg); s['bien_the'] = name; rows.append(s); print(name, s, flush=True)
    out = pd.DataFrame(rows)[['bien_the', 'n', 'R', 'WR', 'h1', 'h2', 'C2p', 'sumR', 'risk_med', 'risk_max']]
    print(out.round(3).to_string())
    out.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report', '_variants_sl_canh.csv'), index=False)
