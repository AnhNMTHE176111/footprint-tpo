# -*- coding: utf-8 -*-
"""
parity_corven.py — đối chiếu setup_corven.py (Python, chuẩn) với DetectorCorven (C#, tools/ReplayCorven) — plan 10.6.

Ranh giới TEST (plan 10.6): TEST chưa "mở" = chưa ai đọc R/WR của lệnh sau 2026-09-15. Parity là kiểm MÃ, không kiểm lợi thế:
  * TRAIN (bar_idx ≤ cut): so ĐỦ — định danh (giờ, thế, hướng, range, mốc, dấu hiệu, entry/SL/TP, R sẵn) + kết cục + R + nến thoát.
  * TEST  (bar_idx > cut): CHỈ so định danh. Cột ket_cuc / r / exit_idx của phần TEST bị BỎ trước khi so, không in, không ghi file;
    không liệt kê từng lệnh TEST, chỉ in số đếm "m/m khớp định danh".
Ngoài lệnh, so luôn MỌI CF ứng viên đã qua ② (dấu hiệu + cổng + giá) — kiểm chặt hơn nhiều so với chỉ 97 lệnh.
Lệch có chủ đích: (1) cổng tin USD (C# có, Python không — ReplayCorven không có lịch tin nên không phát sinh);
(2) cổng 'cuoi_phien' của Python không có trong danh sách cổng C# (C# huỷ lệnh ở BenzoEngine khi thấy khoảng trống) — bỏ khỏi
cột gates của Python trước khi so ứng viên; lệnh thì so thẳng.

Chạy:  PYTHONIOENCODING=utf-8 python parity_corven.py        (≈ 3–5 phút; cần dotnet để build ReplayCorven)
Ghi:   report/PARITY-CORVEN.md + report/_parity_corven_train.csv (chỉ TRAIN).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_corven as SC        # noqa: E402

REPORT = os.path.join(HERE, 'report')
TOOL = os.path.join(os.path.dirname(HERE), 'tools', 'ReplayCorven')
TYPE_VN = dict(delta='Δ', bong='bóng', kiet_suc='kiệt sức', stacked='stacked', trap='trap')
ID_COLS = ['idx', 't_utc', 'the', 'side', 'range_id', 'b_from_exhausted', 'moc', 'so_dau_hieu', 'loai', 'dau_hieu', 'entry', 'sl', 'tp', 'r_san']
OUT_COLS = ['ket_cuc', 'r', 'exit_idx']
CAND_COLS = ['cf', 't_utc', 'the', 'side', 'rid', 'b_from_exhausted', 'n', 'loai', 'dau_hieu', 'gates', 'entry', 'sl', 'tp', 'r_san', 'moc']
FLOAT_COLS = {'entry': 1e-6, 'sl': 1e-6, 'tp': 1e-6, 'r_san': 0.0051, 'r': 0.0011}


def py_rows(R, lo: int, hi: int, with_outcome: bool):
    """Lệnh + ứng viên Python có cf trong [lo, hi], đúng cột ReplayCorven."""
    good, df = R['good'], R['df']
    trades = []
    if with_outcome:
        it = zip(R['chosen'], (t for _, t in R['trades'].iterrows()))
    else:
        it = ((c, None) for c in R['chosen'])        # phần TEST: không đụng tới cột kết cục
    for c, t in it:
        if not (lo <= c.cf <= hi):
            continue
        row = dict(idx=c.cf, t_utc=str(df['datetime'].iloc[c.cf])[:16], the=c.the, side='buy' if c.S > 0 else 'sell',
                   range_id=c.rid, b_from_exhausted=int(c.exhausted), moc=c.moc_used, so_dau_hieu=len(c.types),
                   loai='+'.join(TYPE_VN[x] for x in c.types),
                   dau_hieu=' | '.join(f"{TYPE_VN[k]}: {v[0]} (nến {v[1]})" for k, v in c.signs.items()),
                   entry=round(c.entry * SC.TICK, 6), sl=round(c.sl * SC.TICK, 6), tp=round(c.tp * SC.TICK, 6), r_san=round(c.r_avail, 2))
        if with_outcome:
            row.update(ket_cuc=t['outcome'], r=round(float(t['r']), 3), exit_idx=int(t['exit_idx']))
        trades.append(row)
    cands = []
    for c in R['cands']:
        if c.the == 'A2' or not good[c.cf] or not (lo <= c.cf <= hi):
            continue
        cands.append(dict(cf=c.cf, t_utc=str(df['datetime'].iloc[c.cf])[:16], the=c.the, side='buy' if c.S > 0 else 'sell', rid=c.rid,
                          b_from_exhausted=int(c.exhausted), n=len(c.types), loai='+'.join(TYPE_VN[x] for x in c.types),
                          dau_hieu=' | '.join(f"{TYPE_VN[k]}: {v[0]} (nến {v[1]})" for k, v in c.signs.items()),
                          gates=';'.join(g for g in c.gates if g != 'cuoi_phien'), entry=int(c.entry), sl=int(c.sl), tp=float(c.tp),
                          r_san=round(c.r_avail, 2), moc=c.moc_used))
    return pd.DataFrame(trades), pd.DataFrame(cands)


def run_cs(prefix: str, out: str, maxbar: int, deny: int, hide_after: int = -1):
    dll = os.path.join(TOOL, 'bin', 'Release', 'net10.0', 'ReplayCorven.dll')
    subprocess.run(['dotnet', 'build', TOOL, '-c', 'Release', '-v', 'q', '-nologo'], check=True, capture_output=True)
    args = ['dotnet', dll, prefix, out, '--deny-below', str(deny)] + (['--maxbar', str(maxbar)] if maxbar >= 0 else []) \
        + (['--hide-after', str(hide_after)] if hide_after >= 0 else [])
    subprocess.run(args, check=True, capture_output=True)
    t = pd.read_csv(os.path.join(out, 'cs_trades.csv'), keep_default_na=False)
    c = pd.read_csv(os.path.join(out, 'cs_cands.csv'), keep_default_na=False)
    return t, c


def _norm(df: pd.DataFrame, cols):
    d = df[cols].copy()
    for k in cols:
        if k in FLOAT_COLS:
            d[k] = pd.to_numeric(d[k], errors='coerce').astype(float)
        else:
            d[k] = d[k].astype(str).replace({'nan': ''})
    return d.reset_index(drop=True)


def compare(py: pd.DataFrame, cs: pd.DataFrame, key: str, cols):
    """Trả (số khớp, tổng, danh sách lệch [(key, cột, py, cs)]) — so theo khoá, mọi cột trong cols."""
    if len(py) == 0 and len(cs) == 0:
        return 0, 0, []
    p = _norm(py, cols).set_index(key, drop=False)
    c = _norm(cs, cols).set_index(key, drop=False)
    diffs = []
    keys = sorted(set(p.index) | set(c.index), key=lambda x: (int(x) if str(x).lstrip('-').isdigit() else x))
    ok = 0
    for k in keys:
        if k not in p.index or k not in c.index:
            diffs.append((k, '<thiếu>', 'có' if k in p.index else '—', 'có' if k in c.index else '—'))
            continue
        pr, cr = p.loc[[k]], c.loc[[k]]
        if len(pr) != len(cr):
            diffs.append((k, '<số dòng>', len(pr), len(cr)))
            continue
        good = True
        for (_, a), (_, b) in zip(pr.iterrows(), cr.iterrows()):
            for col in cols:
                x, y = a[col], b[col]
                if col in FLOAT_COLS:
                    same = (np.isnan(x) and np.isnan(y)) or abs(x - y) <= FLOAT_COLS[col]
                else:
                    same = x == y
                if not same:
                    good = False
                    diffs.append((k, col, x, y))
        ok += good
    return ok, len(keys), diffs


def main():
    prefix = SC.D90
    cut = SC.train_cut(prefix)
    # ---------------- Python TRAIN (chuẩn — 97 lệnh) ----------------
    bars, df = SC.load_train(prefix, cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    deny = int(np.flatnonzero(good)[0])
    assert good[deny:].all(), 'mặt nạ phiên dày TRAIN không liền một khối — ReplayCorven --deny-below không đủ'
    R = SC.run_gd1(bars, df, good)
    py_tr, py_c = py_rows(R, 0, cut, True)
    print(f'Python TRAIN: {len(py_tr)} lệnh, {len(py_c)} ứng viên (cut {cut}, phiên dày từ nến {deny})')
    del bars
    with tempfile.TemporaryDirectory() as tmp:
        # ---------------- C# TRAIN (cùng phần đầu file) ----------------
        cs_tr, cs_c = run_cs(prefix, os.path.join(tmp, 'train'), cut, deny)
        a_ok, a_n, a_d = compare(py_tr, cs_tr, 'idx', ID_COLS + OUT_COLS)
        c_ok, c_n, c_d = compare(py_c, cs_c, 'cf', CAND_COLS)
        # ---------------- C# toàn file (một lần chạy) ----------------
        full_tr, full_c = run_cs(prefix, os.path.join(tmp, 'full'), -1, deny, hide_after=cut)   # TEST: C# ghi trống kết cục
        full_tr['idx'] = full_tr['idx'].astype(int)
        full_c['cf'] = full_c['cf'].astype(int)
        f_ok, f_n, f_d = compare(py_tr, full_tr[full_tr['idx'] <= cut], 'idx', ID_COLS + OUT_COLS)
        fc_ok, fc_n, fc_d = compare(py_c, full_c[full_c['cf'] <= cut], 'cf', CAND_COLS)
        cs_test_tr = full_tr[full_tr['idx'] > cut].drop(columns=OUT_COLS)          # cột đã trống từ C#; bỏ hẳn
        cs_test_c = full_c[full_c['cf'] > cut]
        del full_tr
    # ---------------- Python toàn file — chỉ định danh phần TEST ----------------
    n_all = len(pd.read_csv(prefix + '_bars.csv', usecols=['bar_idx']))
    bars_f, df_f = SC.load_train(prefix, cut=n_all - 1)
    good_f = (~df_f['thin'].to_numpy()) & (~df_f['splice'].to_numpy())
    assert (good_f[:cut + 1] == good).all() and good_f[deny:].all(), 'mặt nạ phiên dày toàn file khác TRAIN'
    Rf = SC.run_gd1(bars_f, df_f, good_f)
    Rf['trades'] = None                                                            # ⛔ không giữ bảng kết cục của toàn file
    py_test_tr, py_test_c = py_rows(Rf, cut + 1, n_all - 1, False)
    t_ok, t_n, t_d = compare(py_test_tr, cs_test_tr, 'idx', ID_COLS)
    tc_ok, tc_n, tc_d = compare(py_test_c, cs_test_c, 'cf', CAND_COLS)
    # lệch TEST: chỉ in KHOÁ + TÊN CỘT (không in giá trị, không in kết cục)
    t_diag = [(k, col) for (k, col, _, _) in t_d][:20]
    tc_diag = [(k, col) for (k, col, _, _) in tc_d][:20]

    # ---------------- báo cáo ----------------
    os.makedirs(REPORT, exist_ok=True)
    m = py_tr.merge(cs_tr, on='idx', how='outer', suffixes=('_py', '_cs'))
    m.to_csv(os.path.join(REPORT, '_parity_corven_train.csv'), index=False, encoding='utf-8')
    nA = int((py_tr['the'] == 'A').sum()); nB = int((py_tr['the'] == 'B').sum())
    L = ['# Parity Python ↔ C# — setup CORVEN (corven-1)', '',
         '> Opus, GĐ3 (plan mục 10.6). `research/parity_corven.py` chạy `setup_corven.run_gd1` (chuẩn) và `tools/ReplayCorven` '
         '(mã C# sản phẩm: BenzoEngine + DetectorCorven + RangeLogic/StackedImbalance/ExhaustionLogic nối nguồn) trên '
         '`fp_GCZ26_XCEC_Time_20260723-20261021_90d`. Phiên mỏng đầu file (nến < %d) không vào lệnh ở cả hai bên.' % deny, '',
         '**Ranh giới TEST:** phần TEST (nến > %d, sau 2026-09-15) chỉ so **định danh** (giờ, thế, hướng, range, mốc, dấu hiệu, '
         'entry/SL/TP, R sẵn); cột kết cục/R/nến thoát bị bỏ trước khi so, không in, không ghi file; không liệt kê từng lệnh TEST.' % cut, '',
         '## Kết quả', '',
         '| Phép so | khớp / tổng |', '|---|---|',
         f'| **TRAIN lệnh (kể cả kết cục, R, nến thoát)** — C# chạy phần TRAIN | **{a_ok}/{a_n}** |',
         f'| TRAIN ứng viên (mọi CF qua ②: dấu hiệu, cổng, entry/SL/TP, R sẵn) | {c_ok}/{c_n} |',
         f'| **TRAIN lệnh (kể cả kết cục)** — C# chạy TOÀN file một lần | **{f_ok}/{f_n}** |',
         f'| TRAIN ứng viên — C# toàn file | {fc_ok}/{fc_n} |',
         f'| **TEST lệnh — CHỈ định danh** | **{t_ok}/{t_n}** |',
         f'| TEST ứng viên — chỉ định danh | {tc_ok}/{tc_n} |', '',
         f'Hồi quy TRAIN: Python {len(py_tr)} lệnh (thế A {nA}, thế B {nB}) = C# {len(cs_tr)} lệnh.', '',
         '## Lệch có chủ đích', '',
         '- **Tin USD** (`IsNewsBlocked`, ±15′ tin mức cao): chỉ C# có; ReplayCorven không có lịch tin nên không phát sinh trong phép so.',
         '- **Nến cuối phiên**: Python gắn cổng `cuoi_phien` (biết trước nến cuối). C# không biết trước ⇒ vào lệnh rồi **huỷ** ở BenzoEngine '
         'khi nến đầu phiên sau tới (trả khoá 4d) — kết quả lệnh giống hệt; cột `gates` của ứng viên Python bỏ `cuoi_phien` trước khi so.',
         '- **Range chồng range / mục tiêu thế B**: Python đọc cạnh range cũ ở CUỐI file (nhìn trước nhẹ), C# đọc tại lúc xét. '
         'Không gây lệch nào trên file này (số khớp ở trên).', '']
    if a_d or c_d or f_d or fc_d:
        L += ['## Lệch TRAIN (tối đa 30)', '', '| khoá | cột | Python | C# |', '|---|---|---|---|']
        for (k, col, x, y) in (a_d + c_d + f_d + fc_d)[:30]:
            L.append(f'| {k} | {col} | {str(x)[:80]} | {str(y)[:80]} |')
        L.append('')
    if t_diag or tc_diag:
        L += ['## Lệch TEST (chỉ khoá nến + tên cột, không giá trị)', '', ', '.join(f'{k}:{c}' for k, c in t_diag + tc_diag), '']
    L += ['File đối chiếu TRAIN từng lệnh: `report/_parity_corven_train.csv`.', '']
    with open(os.path.join(REPORT, 'PARITY-CORVEN.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print(f'TRAIN lệnh {a_ok}/{a_n} · TRAIN ứng viên {c_ok}/{c_n} · C# toàn file TRAIN {f_ok}/{f_n} ({fc_ok}/{fc_n} ứng viên) · '
          f'TEST định danh {t_ok}/{t_n} ({tc_ok}/{tc_n} ứng viên)')
    for d in (a_d + c_d + f_d + fc_d)[:15]:
        print('  TRAIN lệch:', d)
    if t_diag or tc_diag:
        print('  TEST lệch (khoá, cột):', (t_diag + tc_diag)[:15])
    ok = a_ok == a_n and c_ok == c_n and f_ok == f_n and fc_ok == fc_n and t_ok == t_n and tc_ok == tc_n and len(py_tr) == 97
    print('PARITY 100 %' if ok else 'PARITY CHƯA ĐẠT')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
