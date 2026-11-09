"""Quét N của luật corven-4: nhịp hồi (không chạm cạnh) chỉ nhận khi nến hồi đầu tiên cách nến phá ≤ N nến.
Chạy bằng mã thật (cờ CP.hoi_trong_n_nen / hoi_max_nen), chỉ TRAIN. N=99 = không giới hạn (= corven-3)."""
import sys, os, dataclasses
sys.path.insert(0, os.getcwd())
import pandas as pd, setup_corven as SC, controls_corven as CC
cut = SC.train_cut(); bars, df = SC.load_train(cut=cut)
good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
sg = sorted(set(df['session_id'].to_numpy()[good]))
rows = []
for n in (1, 2, 3, 4, 5, 6, 7, 8, 10, 99):
    cp = dataclasses.replace(SC.cp_live(), hoi_trong_n_nen=n != 99, hoi_max_nen=n)
    R = SC.run_gd1(bars, df, good, cp); t = R['trades']; c2, _ = CC.c2(R, after_only=True)
    h = t['session_id'].map(lambda s: sg.index(s) < len(sg) // 2)
    rows.append(dict(N=n, n=len(t), nB=int((t.setup == 'B').sum()), R=t['r'].mean(), WR=(t['r'] > 0).mean(),
                     h1=t.loc[h, 'r'].mean(), h2=t.loc[~h, 'r'].mean(), C2p=c2['r_c2_tb'].mean()))
    print(rows[-1], flush=True)
print(pd.DataFrame(rows).round(3).to_string())
