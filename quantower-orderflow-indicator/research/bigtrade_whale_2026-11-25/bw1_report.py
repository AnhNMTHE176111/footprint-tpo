"""Bảng số cụ thể (mã x khung x phiên) cho R1-KET-QUA.md. python bw1_report.py -> r1_results.md
Đọc SCRATCH/bw1_runs.pkl, out_bw1_grid.csv, out_bw1_score.csv."""
import os, sys, pickle
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bw1_common as C
import bw1_rules as RU

with open(os.path.join(C.SCRATCH, 'bw1_runs.pkl'), 'rb') as f:
    RUNS = pickle.load(f)
store, LOGS, fcal = RUNS['store'], RUNS['logs'], RUNS['fcal']
sc = pd.read_csv(os.path.join(C.HERE, 'out_bw1_score.csv'))
L = []
SES = [('A', 'Á'), ('Au', 'Âu'), ('My', 'Mỹ')]
CFGS = [('A_D5_R8', 'W1380'), ('A_D3_R8', 'W1380'), ('A_D10_R8', 'W1380'), ('C_q15_k3', 'W1380'), ('D_k200_R10', 'W1380'),
        ('E_75', 'tu_nhien'), ('E_50', 'tu_nhien'), ('A_D5_R10', 'W1380'), ('A_D5_R6', 'W1380'), ('CUR', 'tu_nhien'), ('ADAPT', 'tu_nhien')]
NAME = {'CUR': 'Luật hiện tại "Không theo CORVEN" (1% của 240 phút)', 'ADAPT': 'Luật hiện tại "Theo CORVEN" (BigTradeAdaptive mặc định)'}


def b(x):
    return 'đạt' if str(x) == 'True' else ('—' if str(x) in ('nan', 'None') else 'rớt')


L.append('# r1_results — bảng số vòng 1 (Opus, 2026-11-25)\n')
L.append('Nguồn: `out_bw1_grid.csv`, `out_bw1_score.csv` (script `bw1_rules.py`, `bw1_score.py`, `bw1_report.py`). Mọi số tính SAU gộp vòng, trên ngày đánh giá '
         '(ngày đủ ≥ 1170 phút nến mà mọi nến có ngưỡng). Vàng tháng 11 (`_GCZ26` M1) không có ngày đủ: dòng "ngoài mẫu" dùng ngày phần ≥ 400 phút nến.\n')
L.append('## 1. Số ngày đủ từng nhật ký\n')
L.append('| Nhật ký | Khung | Ngày đủ | Ghi chú |\n|---|---|---|---|')
for k in ['GCX_M1', 'GCX_M5', 'NQ_M1', 'NQ_M15', 'GCZ_M1']:
    log = LOGS[k]
    part = [f'{C.fmt_day(d)} ({v})' for d, v in sorted(log.daymin.items()) if v < C.FULLMIN]
    L.append(f'| {C.LOGS[k][0]} | M{log.m} | {len(log.full_days)}: {", ".join(C.fmt_day(d) for d in log.full_days)} | ngày thiếu (phút nến): {", ".join(part)} |')
L.append('')
L.append('## 2. Trước / sau theo mã × khung × phiên\n')
L.append('Cột "ngưỡng Á/Âu/Mỹ" = trung vị ngưỡng (hợp đồng) trên các nến của phiên đó trong các ngày đánh giá. "vòng/ngày" = trung vị (nhỏ nhất–lớn nhất). '
         'Ngưỡng của ứng viên D là số thực, in làm tròn 1 chữ số.\n')
for cfg, warm in CFGS:
    rows = sc[(sc.cau_hinh == cfg) & (sc.khoi_dong == warm)]
    if not len(rows): continue
    par = store[(rows.nhat_ky.iloc[0], cfg, warm)]['params']
    L.append(f'### {NAME.get(cfg, cfg)} — `{cfg}` [{warm}] ({par})\n')
    L.append('| Nhật ký | Đoạn | Ngày | Vòng/ngày | Á / Âu / Mỹ (TV vòng) | Ngưỡng Á / Âu / Mỹ | Vòng nhỏ nhất | T1 | T2 (min/TV tỉ số) | T3a cv | T3b lệch | T3c trùng | T4 a/b/c |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for _, r in rows.sort_values(['nhat_ky', 'doan']).iterrows():
        log = LOGS[r.nhat_ky]; st = store[(r.nhat_ky, cfg, warm)]
        thr = st['thr'].astype(float)
        days = RU.eval_days(log, RU.seg_days(log, r.doan), thr)
        g = pd.read_csv(os.path.join(C.HERE, 'out_bw1_grid.csv')) if 'G' not in globals() else G
        globals()['G'] = g
        gg = g[(g.nhat_ky == r.nhat_ky) & (g.cau_hinh == cfg) & (g.khoi_dong == warm) & (g.doan == r.doan)].iloc[0]
        sthr = []
        for s, _ in SES:
            mm = np.isin(log.day, days) & (log.ses == s)
            sthr.append(f'{np.nanmedian(thr[mm]):.1f}' if mm.any() and (~np.isnan(thr[mm])).any() else '—')
        L.append(f'| {r.nhat_ky} | {r.doan} | {r.so_ngay} | {gg.vong_ngay_tv:g} ({gg.vong_ngay_min:g}–{gg.vong_ngay_max:g}) | {gg.tv_A:g} / {gg.tv_Au:g} / {gg.tv_My:g} | '
                 f'{" / ".join(sthr)} | {gg.co_vong_min:g} | {b(r.T1)} | {b(r.T2)} ({r.get("t2_min", np.nan)}/{r.get("t2_tv", np.nan)}) | {r.get("nguong_cv", np.nan):.2f} | '
                 f'{r.get("t3b_lech", np.nan)} | {r.get("t3c_trung", np.nan)} | {r.get("t4a", np.nan)}/{r.get("t4b", np.nan)}/{r.get("t4c", np.nan)} (Á {r.get("t4c_A", "")}, Âu {r.get("t4c_Au", "")}, Mỹ {r.get("t4c_My", "")}) |')
    L.append('')

# 3. Bảng tốt nhất mỗi ứng viên: chọn theo out_bw1_pick (đọc lại logic: ít tiêu chí rớt nhất trên đoạn chọn)
L.append('## 3. Cấu hình tốt nhất của từng ứng viên (đoạn chọn) và số đoạn kiểm\n')
CRIT = ['T1', 'T2', 'T3a', 'T3c', 'T4']
PL = ['GCX_M1', 'GCX_M5', 'NQ_M1', 'NQ_M15']
ch = sc[(sc.doan == 'chon') & sc.nhat_ky.isin(PL)]
best = {}
for (cfg, warm), g in ch.groupby(['cau_hinh', 'khoi_dong']):
    fails = [f'{r.nhat_ky}:{c}' for _, r in g.iterrows() for c in CRIT if str(r[c]) != 'True']
    nf = len(fails) + 5 * (len(PL) - len(g))
    code = g.ung_vien.iloc[0]
    x = g[g.nhat_ky == 'GCX_M1']
    gap = abs(x.vong_tv.iloc[0] - 8) if len(x) and not np.isnan(x.vong_tv.iloc[0]) else 99
    if code not in best or (nf, gap) < best[code][0]: best[code] = ((nf, gap), cfg, warm, fails)
L.append('| Ứng viên | Cấu hình | Khởi động | Rớt ở đoạn chọn | GC M1 vòng/ngày chọn → kiểm | NQ M1 chọn → kiểm | GC tháng 11 (ngoài mẫu) | Ngưỡng TV GC M1 chọn / kiểm | Ngưỡng TV NQ M1 chọn / kiểm | Đoạn kiểm đạt T1–T4 |\n|---|---|---|---|---|---|---|---|---|---|')
for code in ['A', 'B', 'C', 'Cx', 'D', 'E', 'F', 'G', 'CUR', 'ADAPT']:
    if code not in best: continue
    (nf, _), cfg, warm, fails = best[code]
    rr = sc[(sc.cau_hinh == cfg) & (sc.khoi_dong == warm)]
    def v(k, s, c):
        x = rr[(rr.nhat_ky == k) & (rr.doan == s)]
        return x[c].iloc[0] if len(x) else np.nan
    kiem_ok = [k for k in PL if len(rr[(rr.nhat_ky == k) & (rr.doan == 'kiem')]) and all(str(rr[(rr.nhat_ky == k) & (rr.doan == 'kiem')][c].iloc[0]) == 'True' for c in CRIT)]
    L.append(f'| {code} | `{cfg}` | {warm} | {", ".join(fails) if fails else "không"} | {v("GCX_M1","chon","vong_tv"):g} → {v("GCX_M1","kiem","vong_tv"):g} | '
             f'{v("NQ_M1","chon","vong_tv"):g} → {v("NQ_M1","kiem","vong_tv"):g} | {v("GCZ_M1","ngoai","vong_tv"):g} | {v("GCX_M1","chon","nguong_p50"):g} / {v("GCX_M1","kiem","nguong_p50"):g} | '
             f'{v("NQ_M1","chon","nguong_p50"):g} / {v("NQ_M1","kiem","nguong_p50"):g} | {", ".join(kiem_ok) if kiem_ok else "không có"} |')
L.append('')
L.append('## 4. Hệ số f của ứng viên F (hiệu chỉnh trên đoạn chọn M1, giữ nguyên ở khung khác)\n')
L.append('| Mã | T | f cho 6 / 10 / 15 vòng mỗi ngày |\n|---|---|---|')
for sym in ('GC', 'NQ'):
    for T in RU.F_T:
        L.append(f'| {sym} | {T} | {" / ".join(str(fcal[(sym, T, t)]) for t in RU.F_TARGET)} |')
L.append('')
with open(os.path.join(C.HERE, 'r1_results.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(L) + '\n')
print('\n'.join(L))
