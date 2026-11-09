# -*- coding: utf-8 -*-
"""Đo luật vị trí bóng/trap theo 1/3–2/3 nến (người học đề xuất, Opus yêu cầu 2026-11-09). Chưa sửa C#, chưa bật live.
Biến thể (cờ CP mặc định tắt): bong_23 (③b luật 2/3), trap_hoi_13 (③f), trap_quet_13 (③e). Mỗi biến thể × 2 chế độ SL
trên TRAIN (35 phiên) + holdout từ 2026-10-22 (chỉ tham khảo) + danh sách lệnh thêm/bớt của biến thể tốt nhất.
Chạy: python variants_vi_tri_bong.py  (TRAIN + holdout + diff)."""
import sys, os, dataclasses
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import setup_corven as SC, controls_corven as CC

HERE = os.path.dirname(os.path.abspath(__file__))
VARS = [('gốc', {}),
        ('bong_23', dict(bong_23=True)),
        ('trap_hoi_13', dict(trap_hoi_13=True)),
        ('trap_quet_13', dict(trap_quet_13=True)),
        ('trap_hoi_13+trap_quet_13', dict(trap_hoi_13=True, trap_quet_13=True)),
        ('cả 3', dict(bong_23=True, trap_hoi_13=True, trap_quet_13=True))]
MODES = [(False, 'corven-6 (SL sát cạnh, trần 5 giá)'), (True, 'SL kiểu cũ (= corven-5)')]


def summ(R, sg):
    t = R['trades']
    h = t['session_id'].map(lambda s: sg.index(s) < len(sg) // 2)
    c2, _ = CC.c2(R, after_only=True)
    a, b = t[t['setup'] == 'A'], t[t['setup'] == 'B']
    return dict(n=len(t), nA=len(a), nB=len(b), R=t['r'].mean(), R_A=a['r'].mean(), R_B=b['r'].mean(), WR=(t['r'] > 0).mean(),
                h1=t.loc[h, 'r'].mean(), h2=t.loc[~h, 'r'].mean(), C2p=c2['r_c2_tb'].mean(), sumR=t['r'].sum())


def key(t):
    return list(zip(t['t_vn'].astype(str), t['side'], t['setup']))


def sweep():
    cut = SC.train_cut(); bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sg = sorted(set(df['session_id'].to_numpy()[good]))
    rows, runs = [], {}
    for kc, mode in MODES:
        for name, kw in VARS:
            cp = dataclasses.replace(SC.cp_live(kc), **kw)
            R = SC.run_gd1(bars, df, good, cp)
            runs[(kc, name)] = R
            s = summ(R, sg); s.update(che_do=mode, bien_the=name); rows.append(s); print(s, flush=True)
    out = pd.DataFrame(rows)[['che_do', 'bien_the', 'n', 'nA', 'nB', 'R', 'R_A', 'R_B', 'WR', 'h1', 'h2', 'C2p', 'sumR']]
    out.to_csv(os.path.join(HERE, 'report', '_variants_vi_tri_bong.csv'), index=False)
    print(out.round(3).to_string())
    return bars, df, good, runs, out


def holdout():
    import follow_newdata as FN
    pre = os.path.abspath(os.path.join(HERE, '..', '..', 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260811-20261109_90d'))
    bars, df, _ = FN.load_segment(pre, '2026-10-22')
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy())
    print('--- HOLDOUT từ 2026-10-22 (chỉ tham khảo)')
    for kc, mode in MODES:
        for name, kw in VARS:
            R = SC.run_gd1(bars, df, good, dataclasses.replace(SC.cp_live(kc), **kw))
            t = R['trades']
            print(f'{mode[:12]:12s} {name:26s} n={len(t):3d} WR={(t["r"] > 0).mean() if len(t) else float("nan"):.3f} R TB={t["r"].mean() if len(t) else float("nan"):+.3f}')


def diff(bars, df, good, runs, out):
    for kc, mode in MODES:
        sub = out[(out['che_do'] == mode) & (out['bien_the'] != 'gốc')].sort_values('R', ascending=False)
        # bỏ biến thể cho đúng tập lệnh như gốc (không đổi gì) — lấy biến thể tốt nhất THỰC SỰ khác gốc
        sub = sub[[set(key(runs[(kc, b)]['trades'])) != set(key(runs[(kc, 'gốc')]['trades'])) for b in sub['bien_the']]]
        best = sub.iloc[0]['bien_the']
        print(f'\n=== {mode}: biến thể tốt nhất theo R TB = {best}')
        g, v = runs[(kc, 'gốc')]['trades'], runs[(kc, best)]['trades']
        kg, kv = set(key(g)), set(key(v))
        cols = ['t_vn', 'setup', 'side', 'r']
        add = v[[k not in kg for k in key(v)]]; rem = g[[k not in kv for k in key(g)]]
        def show(tag, d):
            for _, r in d.head(20).iterrows():
                print(f'  {tag} {str(pd.Timestamp(r["t_vn"]))[:16]} {"Fail Break" if r["setup"] == "A" else "Break"} {"buy" if r["side"] > 0 else "sell"} R={r["r"]:+.2f}')
        print(f'THÊM {len(add)} (sumR {add["r"].sum():+.2f}), BỚT {len(rem)} (sumR {rem["r"].sum():+.2f})')
        show('+', add); show('-', rem)
        # lệnh gốc dựa vào dấu hiệu bóng/trap ở vị trí bị luật mới loại
        R0 = runs[(kc, 'gốc')]; cp_new = dataclasses.replace(SC.cp_live(kc), **dict(VARS)[best])
        lost = {'bong': 0, 'trap': 0}; fall = 0; ntb = 0
        for c in R0['chosen']:
            old = c.types
            new = SC.find_signs(c, R0['feat'], cp_new)
            gone = [x for x in ('bong', 'trap') if x in c.signs and x not in new]
            for x in gone: lost[x] += 1
            if gone:
                ntb += 1
                if len([x for x in old if x in new]) + 0 < 2: fall += 1
        print(f'Lệnh gốc ({len(R0["chosen"])}) mất dấu hiệu: bong {lost["bong"]}, trap {lost["trap"]}; có ít nhất 1 dấu hiệu mất: {ntb}; trong đó tụt dưới 2 dấu hiệu: {fall}')


if __name__ == '__main__':
    r = sweep()
    diff(*r)
    holdout()
