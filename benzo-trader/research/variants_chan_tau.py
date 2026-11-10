# -*- coding: utf-8 -*-
"""Đo luật "chặn tàu" (Opus thiết kế 2026-11-10): Fail Break buy bị chặn khi cấu trúc đang GIẢM chưa gãy (sell: TĂNG).
Cờ CP: chan_tau_n (0 = tắt), chan_tau_break. Chưa sửa C#. Chạy: python variants_chan_tau.py"""
import sys, os, dataclasses
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import setup_corven as SC, controls_corven as CC
from variants_vi_tri_bong import summ

HERE = os.path.dirname(os.path.abspath(__file__))
NS = [0, 1, 2, 3, 5, 8]
MODES = [(False, 'corven-6 (SL sát cạnh, trần 5 giá)'), (True, 'SL kiểu cũ (= corven-5)')]
PRE = os.path.abspath(os.path.join(HERE, '..', '..', 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260811-20261109_90d'))
STATE = {-1: 'GIẢM', 0: 'TRUNG TÍNH', 1: 'TĂNG'}


def blocked(R0, N, cp0):
    """Fail Break của lượt GỐC (N=0) bị luật N chặn: (bảng lệnh, DataFrame)."""
    st = SC.struct_states(R0['feat'], N)
    rows = []
    for c, (_, t) in zip(R0['chosen'], R0['trades'].iterrows()):
        if c.the in ('A', 'A2') and st[c.cf] == -c.S:
            rows.append(dict(t_vn=str(pd.Timestamp(t['t_vn']))[:16], side='buy' if c.S > 0 else 'sell', r=t['r'], state=STATE[int(st[c.cf])]))
    return pd.DataFrame(rows, columns=['t_vn', 'side', 'r', 'state'])


def stats(b):
    return f"{len(b)} chặn: thắng {(b['r'] > 0).sum()}, thua {(b['r'] <= 0).sum()}, tổng R {b['r'].sum():+.2f}"


def main():
    cut = SC.train_cut(); bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sg = sorted(set(df['session_id'].to_numpy()[good]))
    import follow_newdata as FN
    hb, hdf, _ = FN.load_segment(PRE, '2026-10-22')
    hgood = (~hdf['thin'].to_numpy()) & (~hdf['splice'].to_numpy())
    rows, hrows, runs, hruns = [], [], {}, {}
    for kc, mode in MODES:
        for N in NS:
            cp = dataclasses.replace(SC.cp_live(kc), chan_tau_n=N)
            R = SC.run_gd1(bars, df, good, cp); runs[(kc, N, False)] = R
            s = summ(R, sg); s.update(che_do=mode, bien_the=f'N={N}' if N else 'tắt'); rows.append(s)
            H = SC.run_gd1(hb, hdf, hgood, cp); hruns[(kc, N, False)] = H
            t = H['trades']
            hrows.append(dict(che_do=mode, bien_the=s['bien_the'], n=len(t), nA=int((t['setup'] == 'A').sum()), WR=(t['r'] > 0).mean(),
                              R=t['r'].mean(), R_A=t.loc[t['setup'] == 'A', 'r'].mean()))
        trs = [r for r in rows if r['che_do'] == mode and r['bien_the'] != 'tắt']
        bestN = int(max(trs, key=lambda r: r['R'])['bien_the'][2:])
        cp = dataclasses.replace(SC.cp_live(kc), chan_tau_n=bestN, chan_tau_break=True)
        R = SC.run_gd1(bars, df, good, cp); s = summ(R, sg); s.update(che_do=mode, bien_the=f'N={bestN}+Break'); rows.append(s)
        H = SC.run_gd1(hb, hdf, hgood, cp); t = H['trades']
        hrows.append(dict(che_do=mode, bien_the=s['bien_the'], n=len(t), nA=int((t['setup'] == 'A').sum()), WR=(t['r'] > 0).mean(),
                          R=t['r'].mean(), R_A=t.loc[t['setup'] == 'A', 'r'].mean()))
        runs[(kc, bestN, 'best')] = bestN
    cols = ['che_do', 'bien_the', 'n', 'nA', 'nB', 'R', 'R_A', 'R_B', 'WR', 'h1', 'h2', 'C2p', 'sumR']
    out = pd.DataFrame(rows)[cols]
    # WR riêng Fail Break
    for i, r in out.iterrows():
        kc = r['che_do'] == MODES[1][1]
        N = int(r['bien_the'][2:].split('+')[0]) if r['bien_the'] != 'tắt' else 0
        if '+Break' in r['bien_the']:
            continue
        t = runs[(kc, N, False)]['trades']; a = t[t['setup'] == 'A']
        out.loc[i, 'WR_A'] = (a['r'] > 0).mean()
    out.to_csv(os.path.join(HERE, 'report', '_variants_chan_tau.csv'), index=False)
    pd.set_option('display.width', 250)
    print('=== TRAIN'); print(out.round(3).to_string())
    ho = pd.DataFrame(hrows); print('=== HOLDOUT >= 2026-10-22 (tham khảo)'); print(ho.round(3).to_string())
    for kc, mode in MODES:
        print(f'\n=== LỆNH FAIL BREAK BỊ CHẶN — {mode}')
        for N in NS[1:]:
            print(f' N={N}: TRAIN {stats(blocked(runs[(kc, 0, False)], N, None))} | HOLDOUT {stats(blocked(hruns[(kc, 0, False)], N, None))}')
        trs = out[(out['che_do'] == mode) & out['bien_the'].str.match(r'^N=\d$')]
        bestN = int(trs.sort_values('R').iloc[-1]['bien_the'][2:])
        for tag, R in (('TRAIN', runs[(kc, 0, False)]), ('HOLDOUT', hruns[(kc, 0, False)])):
            b = blocked(R, bestN, None); print(f' -- N tốt nhất={bestN}, {tag}:')
            for _, r in b.iterrows(): print(f'    {r["t_vn"]} {r["side"]} R={r["r"]:+.2f} ({r["state"]})')
    # ca người học: Fail Break buy holdout, stacked N mức
    print('\n=== FAIL BREAK BUY HOLDOUT (SL corven-6, N=0): dấu hiệu + trạng thái cấu trúc')
    H0 = hruns[(False, 0, False)]
    for c, (_, t) in zip(H0['chosen'], H0['trades'].iterrows()):
        if c.the in ('A', 'A2') and c.S > 0:
            sts = {N: STATE[int(SC.struct_states(H0['feat'], N)[c.cf])] for N in NS[1:]}
            print(f' {str(pd.Timestamp(t["t_vn"]))[:16]} entry={c.entry*SC.TICK:.1f} R={t["r"]:+.2f} signs={ {k: v[0] for k, v in c.signs.items()} } cấu trúc={sts}')


if __name__ == '__main__':
    main()
