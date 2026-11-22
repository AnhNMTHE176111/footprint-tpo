"""Vòng 4: mọi setup của sách ĐÚNG KHUNG SÁCH (M30 / profile ngày) trên GC 2 năm.
DEV = 08/2024-07/2025 (dò), VALID = 08/2025-08/10/2026 (kiểm). Loại lệnh có bước nhảy giá giả trong cửa sổ dữ liệu."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, '.'); sys.stdout.reconfigure(encoding='utf-8')
from core import Data, stats, to_df
import setup_a as A, setups_other as S, r2

d = Data(base='fp_GC_XCEC_Time_20240801-20260819_748d9h', cache_name='cache_2y.npz')
jump = np.abs(d.o[1:] - d.c[:-1]) > np.maximum(15, 4 * np.nan_to_num(d.atr1[:-1], nan=1.0))
jidx = np.flatnonzero(jump) + 1
MID, CUT = pd.Timestamp('2025-08-01'), pd.Timestamp('2026-08-11')
rows = []


def rep(name, tr, window_min=2 * 1440):
    df = to_df(tr, d)
    if len(df) == 0:
        rows.append(dict(setup=name, n_dev=0)); return
    bad = np.array([np.any((jidx > i - window_min) & (jidx <= i)) for i in df.i.values])
    df = df[~bad & (df.date < CUT)]
    dv, va = stats(df[df.date < MID]), stats(df[df.date >= MID])
    rows.append(dict(setup=name, n_dev=dv.get('n'), wr_dev=dv.get('wr'), R_dev=dv.get('expR'), ci_dev=dv.get('ci90'),
                     n_val=va.get('n'), wr_val=va.get('wr'), R_val=va.get('expR'), ci_val=va.get('ci90')))
    print(rows[-1], flush=True)


# A: POC vùng tích lũy (p25-28), M30, SL/TP 1.3/1.1 ATR30, theo sách đầy đủ
for trend in ('none', 'day'):
    tr, _ = A.run(d, tf=30, trend=trend, flip=True, expire_days=30)
    rep(f'A tf30 {trend}', [t for t in tr if t['setup'] == 'A'], 31 * 1440)
    rep(f'A-flip tf30 {trend}', [t for t in tr if t['setup'] == 'A-flip'], 31 * 1440)
    tr, _ = A.run(d, tf=30, trend=trend, flip=False, expire_days=30, fast=0, near=-1)
    rep(f'A tf30 {trend} no-cancel', tr, 31 * 1440)
# B: P/b và D (p21-23, p30-34)
for kind in ('globex', 'rth'):
    rep(f'B-Pb {kind}', S.setup_B(d, kind=kind))
    rep(f'B-Pb {kind} trend', S.setup_B(d, kind=kind, trend='day'))
    rep(f'B-D {kind}', S.setup_B(d, kind=kind, mode='D'))
    # E: 80% (p83-86)
    rep(f'E-80 {kind} atr', S.setup_E(d, kind=kind))
    rep(f'E-80 {kind} va', S.setup_E(d, kind=kind, sl_mode='va'))
    # I: fake out M30 (p90-92)
    rep(f'I-fake30 {kind}', S.setup_I(d, kind=kind))
    # F: open drive (p77-78)
    rep(f'F-drive {kind}', S.setup_F(d, kind=kind))
    rep(f'F-drive {kind} 2R', S.setup_F(d, kind=kind, tp_R=2))
# D: LVN khung sách (M30 trigger, profile ghép nhiều phiên)
for ns in (1, 3, 5):
    rep(f'D-lvn M30 ns{ns}', S.setup_D(d, nsess=ns), (ns + 1) * 1440)
    rep(f'D-lvn M30 ns{ns} retest', S.setup_D(d, nsess=ns, entry='retest'), (ns + 1) * 1440)
# POC phiên bị phá -> retest (p53, p55)
for brk in (0.5, 1.0):
    rep(f'flip sess brk{brk}', r2.flip(d, src='sess', tf=30, brk=brk), 31 * 1440)

pd.DataFrame(rows).to_csv('r4_book_scale.csv', index=False)
print(pd.DataFrame(rows).to_string())
