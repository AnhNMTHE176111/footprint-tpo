# -*- coding: utf-8 -*-
"""
controls_corven.py — 3 đối chứng của setup CORVEN (plans/BENZO-CORVEN-plan.md mục 3.4), cùng SL/TP/chi phí:
  C1  bỏ ③      — vào ở mọi CF hợp lệ tại mốc (qua ② và ④/⛔/4d) mà không đòi dấu hiệu
  C2  ngẫu nhiên — mỗi lệnh thật: 20 nến ngẫu nhiên cùng phiên, cùng giờ ±30′, cùng hướng, rủi ro cùng số mbr, TP 2R
  C3  từng dấu hiệu đơn lẻ — chỉ đòi 1 dấu hiệu loại t (5 lần chạy), báo R theo loại
Chỉ dùng TRAIN (đầu vào do setup_corven.run_gd1 dựng).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import setup_corven as SC

TICK = SC.TICK


def c1(R: dict) -> pd.DataFrame:
    tr, _, _ = SC.select_and_simulate(R['cands'], R['df'], R['feat'], R['cp'], mode='C1')
    return tr


def c3(R: dict) -> dict:
    out = {}
    for t in SC.SIGN_TYPES:
        tr, _, _ = SC.select_and_simulate(R['cands'], R['df'], R['feat'], R['cp'], mode=('C3', t))
        out[t] = tr
    return out


def c2(R: dict, n_random: int = 20, seed: int = 0, minutes: int = 30):
    """Trả (DataFrame mỗi lệnh thật: idx, r_that, r_c2_tb, n_c2), mảng mọi R đối chứng."""
    f, df, cp = R['feat'], R['df'], R['cp']
    rng = np.random.default_rng(seed)
    rows, allr = [], []
    for c, (_, t) in zip(R['chosen'], R['trades'].iterrows()):
        i, S = c.cf, c.S
        s0, s1 = int(f.sstart[i]), int(f.send[i])
        pool = [j for j in range(s0, s1) if j != i and abs(int(f.sm[j]) - int(f.sm[i])) <= minutes and f.good[j]
                and f.mbr[j] > 0]
        if not pool:
            continue
        pick = rng.choice(pool, size=min(n_random, len(pool)), replace=False)
        rm = c.risk / f.mbr[i]
        rs = []
        for j in sorted(int(x) for x in pick):
            ent = int(f.C[j])
            risk = rm * f.mbr[j]
            sl = ent - S * risk
            sl = int(np.floor(sl + 1e-9)) if S > 0 else int(np.ceil(sl - 1e-9))
            risk = (ent - sl) * S
            if risk <= 0:
                continue
            e = dict(idx=j, side=S, entry=round(ent * TICK, 6), sl=round(sl * TICK, 6),
                     tp=round((ent + S * cp.tp_r * risk) * TICK, 6), setup='C2', zone='', note='')
            x = SC.sim_one(df, f, e)
            if x is not None and x['outcome'] in ('TP', 'SL', 'TIME'):
                rs.append(float(x['r']))
        if rs:
            rows.append(dict(idx=i, r_that=float(t['r']), r_c2_tb=float(np.mean(rs)), n_c2=len(rs)))
            allr += rs
    return pd.DataFrame(rows), np.array(allr)
