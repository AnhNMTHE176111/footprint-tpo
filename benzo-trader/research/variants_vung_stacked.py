# -*- coding: utf-8 -*-
"""Đo các luật siết nhánh 'vùng stacked làm mốc' của Break (corven-4) + gán lệnh cho range gần nhất. Chỉ TRAIN ≤ 15/9.
Hậu xử lý ứng viên: lọc mốc stacked theo luật → tính lại dấu hiệu + lệnh → chọn lệnh. Opus đo 2026-11-09."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import setup_corven as SC, controls_corven as CC


def apply(R, K=None, born=None, pull=False, latest=False):
    f, cp, m, df = R['feat'], R['cp'], R['m'], R['df']
    out = []
    for c0 in R['cands']:
        c = SC.Cand(**{k: getattr(c0, k) for k in ('cf', 'the', 'S', 'rid', 'inst', 'key', 'ref', 'w0', 'mocs', 'trap_levels', 'exhausted')})
        if c.the == 'B':
            keep = []
            for mo in c.mocs:
                if mo['kind'] != 'stacked':
                    keep.append(mo); continue
                zb, lo, hi = mo['zid']
                E, S = c.inst.E, c.S
                near = (lo - E) if S > 0 else (E - hi)          # khoảng từ cạnh vừa phá tới mép gần của vùng
                if K is not None and near > K * f.mbr[c.cf] + 1e-9: continue
                if born is not None and zb - c.ref > born: continue
                if pull:
                    ws = max(c.w0, zb + 1)
                    if not any(f.H[k] >= lo - mo['tol'] and f.L[k] <= hi + mo['tol'] for k in range(ws, c.cf)): continue
                keep.append(mo)
            if not keep: continue
            c.mocs = keep
        out.append(c)
    chong = SC.compute_chong(m, cp)
    for c in out:
        c.signs = SC.find_signs(c, f, cp)
        SC.eval_order(c, f, cp, m, chong, R['use_chong'])
    key = (lambda c: (c.cf, SC.THE_ORDER[c.the], -c.ref)) if latest else (lambda c: (c.cf, SC.THE_ORDER[c.the], c.rid))
    out.sort(key=key)
    tr, ch, why = SC.select_and_simulate(out, df, f, cp)
    return dict(R, cands=out, trades=tr, chosen=ch, why=why)


def summ(R, sg):
    t = R['trades']
    h = t['session_id'].map(lambda s: sg.index(s) < len(sg) // 2)
    c2, _ = CC.c2(R, after_only=True)
    zone = t['zone'].astype(str).str.startswith('stacked')
    return dict(n=len(t), R=t['r'].mean(), WR=(t['r'] > 0).mean(), h1=t.loc[h, 'r'].mean(), h2=t.loc[~h, 'r'].mean(),
                C2p=c2['r_c2_tb'].mean(), n_vung=int(zone.sum()), R_vung=t.loc[zone, 'r'].mean(), R_canh=t.loc[~zone, 'r'].mean())


if __name__ == '__main__':
    cut = SC.train_cut(); bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sg = sorted(set(df['session_id'].to_numpy()[good]))
    R0 = SC.run_gd1(bars, df, good, SC.cp_live())
    V = [('corven-4 (hiện tại)', {}), ('gán range gần nhất', dict(latest=True))]
    V += [(f'vùng cách cạnh ≤ {k} biên độ', dict(K=k)) for k in (0, 0.5, 1, 1.5, 2, 3, 4, 6)]
    V += [('vùng sinh ≤ 5 nến sau phá', dict(born=5)), ('vùng sinh ≤ 10 nến sau phá', dict(born=10)),
          ('có nến hồi chạm vùng trước nến vào', dict(pull=True)),
          ('bỏ hẳn nhánh vùng stacked', dict(K=-999))]
    rows = []
    for name, kw in V:
        s = summ(apply(R0, **kw), sg); s['bien_the'] = name; rows.append(s); print(s, flush=True)
    out = pd.DataFrame(rows)[['bien_the', 'n', 'R', 'WR', 'h1', 'h2', 'C2p', 'n_vung', 'R_vung', 'R_canh']]
    print(out.round(3).to_string())
    out.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report', '_variants_vung_stacked.csv'), index=False)
