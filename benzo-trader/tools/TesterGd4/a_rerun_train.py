# -*- coding: utf-8 -*-
"""
GĐ4 (a) — TESTER ĐỘC LẬP: chạy lại setup_corven.run_gd1 TỪ ĐẦU trên TRAIN (bộ gốc vòng 1), KHÔNG ghi đè file báo cáo nào.
So với report/_corven_trades.csv (từng ô) và các số chính ghi trong RESULTS-CORVEN.md (n 97, A 43/B 54, WR 26,8 %,
R TB −0,29 [−0,55; −0,02], ΣR −28,5, C1 −0,24, C2 −0,08). Chỉ đọc phần bar_idx ≤ cut (TRAIN) — TEST không nạp.
Chạy: PYTHONIOENCODING=utf-8 python benzo-trader/tools/TesterGd4/a_rerun_train.py
"""
import os, sys, tempfile
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', '..', 'research')
sys.path.insert(0, RES)
import setup_corven as SC          # noqa: E402
import results_corven as RC        # noqa: E402  (chỉ dùng hàm stats/trades_csv, không gọi main)
import controls_corven as CC       # noqa: E402

cut = SC.train_cut()
bars, df = SC.load_train(cut=cut)
assert df['bar_idx'].max() <= cut if 'bar_idx' in df else len(df) == cut + 1
good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
nd = len(set(df['session_id'].to_numpy()[good]))
R = SC.run_gd1(bars, df, good)
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 't.csv')
    mine = RC.trades_csv(R, p)
    mine = pd.read_csv(p)
ref = pd.read_csv(os.path.join(RES, 'report', '_corven_trades.csv'))
same_shape = mine.shape == ref.shape
diff_cells = 0
if same_shape:
    for col in ref.columns:
        a, b = mine[col], ref[col]
        if a.dtype.kind == 'f' or b.dtype.kind == 'f':
            diff_cells += int((~np.isclose(a.astype(float), b.astype(float), atol=1e-9)).sum())
        else:
            diff_cells += int((a.astype(str) != b.astype(str)).sum())
s = RC.stats(R['trades'], nd)
the = np.array([c.the for c in R['chosen']])
c1 = RC.stats(CC.c1(R), nd)
c2df, c2all = CC.c2(R)
print(f'cut={cut} · phiên dày TRAIN={nd} · max bar_idx nạp={len(df) - 1}')
print(f'n={s["n"]} A={int((the == "A").sum())} B={int((the == "B").sum())} per_day={s["per_day"]:.2f} WR={100 * s["wr"]:.1f}% '
      f'avg={s["avg"]:.3f} CI=[{s["lo"]:.2f}; {s["hi"]:.2f}] sum={s["sum"]:.1f} dd={s["dd"]:.1f} streak={s["streak"]}')
print(f'TP={int((R["trades"]["outcome"] == "TP").sum())} SL={int((R["trades"]["outcome"] == "SL").sum())} TIME={s["n_time"]}')
print(f'C1 avg={c1["avg"]:.3f} (n {c1["n"]}) · C2 avg={c2all.mean():.3f} (theo cặp: {(c2df["r_that"] - c2df["r_c2_tb"]).mean():.3f})')
print(f'so với _corven_trades.csv: shape {mine.shape} vs {ref.shape} · ô lệch = {diff_cells if same_shape else "khác shape"}')
