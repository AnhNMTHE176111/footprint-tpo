# -*- coding: utf-8 -*-
"""Đo luật 'range bị phá thật rồi giá chạy XA ⇒ range kết thúc' (RangeParams.DeadRunMult, bước 1 — chưa bật live).
Quét DeadRunMult ∈ {tắt, 0,5, 1, 1,5, 2, 3} × 2 chế độ SL (cp_live() và cp_live(sl_kieu_cu=True)) trên TRAIN (35 phiên),
rồi kiểm ca 29/10 (range 4064,7–4068,7, file 20260811-20261109, load_segment từ 2026-10-22) cho mức 1 và 2. Opus yêu cầu 2026-11-09."""
import sys, os, dataclasses
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import setup_corven as SC, controls_corven as CC

HERE = os.path.dirname(os.path.abspath(__file__))
MULTS = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]


def summ(R, sg):
    t = R['trades']
    h = t['session_id'].map(lambda s: sg.index(s) < len(sg) // 2)
    c2, _ = CC.c2(R, after_only=True)
    return dict(n=len(t), nA=int((t['setup'] == 'A').sum()), nB=int((t['setup'] == 'B').sum()), R=t['r'].mean(), WR=(t['r'] > 0).mean(),
                h1=t.loc[h, 'r'].mean(), h2=t.loc[~h, 'r'].mean(), C2p=c2['r_c2_tb'].mean(), sumR=t['r'].sum())


def sweep():
    cut = SC.train_cut(); bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sg = sorted(set(df['session_id'].to_numpy()[good]))
    rows = []
    for kc, mode in ((False, 'corven-6 (SL sát cạnh, trần 5 giá)'), (True, 'SL kiểu cũ (= corven-5)')):
        for m in MULTS:
            cp = dataclasses.replace(SC.cp_live(kc), dead_run_mult=m)
            s = summ(SC.run_gd1(bars, df, good, cp), sg)
            s.update(che_do=mode, dead_run_mult=m if m > 0 else 'tắt'); rows.append(s); print(s, flush=True)
    out = pd.DataFrame(rows)[['che_do', 'dead_run_mult', 'n', 'nA', 'nB', 'R', 'WR', 'h1', 'h2', 'C2p', 'sumR']]
    out.to_csv(os.path.join(HERE, 'report', '_variants_dead_run.csv'), index=False)
    print(out.round(3).to_string())


def case_2910():
    import follow_newdata as FN
    pre = os.path.abspath(os.path.join(HERE, '..', '..', 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260811-20261109_90d'))
    bars, df, _ = FN.load_segment(pre, '2026-10-22')
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy())
    for m in (0.0, 1.0, 2.0):
        for kc in (False, True):
            cp = dataclasses.replace(SC.cp_live(kc), dead_run_mult=m)
            R = SC.run_gd1(bars, df, good, cp)
            eng = R['m'].eng
            rg = [r for r in eng.ranges if abs(r.top0 - 40687) <= 3 and abs(r.bottom0 - 40647) <= 3]
            print(f'--- mức {m or "tắt"} · SL {"kiểu cũ" if kc else "corven-6"}')
            for r in rg:
                ev = [(e.bar, e.kind) for e in eng.events if e.start == r.start and e.kind in ('CloseOutside', 'BreakConfirmed', 'ReEntry', 'FailBreak', 'Merge')]
                tm = lambda i: str(pd.Timestamp(df['datetime'].iloc[i]) + pd.Timedelta(hours=7))[5:16]   # giờ VN
                print(f'  range {r.id}: {r.bottom0 / 10:.1f}–{r.top0 / 10:.1f} start {tm(r.start)} state {r.state} exhausted {r.exhausted} ev:',
                      [(tm(b), k) for b, k in ev][:16])
            t = R['trades']
            d = t[t['t_vn'].astype(str).str[:10] == '2026-10-29']
            print(d[['t_vn', 'setup', 'side', 'entry', 'sl', 'tp', 'outcome', 'r']].to_string() if len(d) else '  (không có lệnh 29/10)')


if __name__ == '__main__':
    if 'case' in sys.argv:
        case_2910()
    else:
        sweep()
