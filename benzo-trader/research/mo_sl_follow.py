# -*- coding: utf-8 -*-
"""
mo_sl_follow.py — plans/BENZO-FOLLOW-COMBO-plan.md mục 5.2 + 9.3-B2 (mổ SL vòng 1, chế độ "khám phá, hậu kiểm").

Nhãn máy, danh mục cố định, ƯU TIÊN TỪ TRÊN XUỐNG, mỗi lệnh đúng 1 nhãn (bỏ `TIN` — 9.1-5: không có lịch tin lịch sử):
  MOVE_GIA   trong ≤ 5 nến sau c có nến đóng về phía trong cạnh E ((close − E)·D ≤ 0) — cú phá là giả
  SL_QUET    lệnh SL, nến dính SL chỉ xuyên SL ≤ 2 tick, rồi giá chạm TP gốc trong 30 nến sau — SL quá sát
  HOI_SAU    nhịp hồi `deep` (depth > 0,7 move_h)
  CF_YEU     c không thoả 4a phần hình nến: thân < 0,4 biên độ hoặc (đỉnh − đóng) > 0,3 biên độ (D = +1; lật cho D = −1)
  NGUOC_1H   (close[c] − close[c−60])·D < 0 — đẩy ngược xu hướng 1 giờ
  PHIEN_MONG phiên Á, hoặc volume nến c < p25 volume các nến của chính phiên đó
  KHONG_RO   còn lại
Tính cho MỌI lệnh (SL, TP, và TIME để đủ) của F7, F10, F0 (lệnh thật, one_at_a_time = report/_follow_trades_<combo>.csv).
Xuất report/_mo_sl_follow.csv (combo, idx_c, outcome, r, nhãn, số đo nền + cờ thô từng nhãn) và report/MO-SL-FOLLOW.md.
⛔ Nhãn máy KHÔNG in lên ảnh (plot_follow.py); Fable gắn nhãn tay trước khi đọc mục "Nhãn máy".
⛔ Chỉ TRAIN (nến cắt tại 2026-09-15 qua plot_follow.load_bars_train).

Chạy:  PYTHONIOENCODING=utf-8 python mo_sl_follow.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plot_follow import load_bars_train, flags_of, REPORT, SHOTS   # noqa: E402

LABELS = ('MOVE_GIA', 'SL_QUET', 'HOI_SAU', 'CF_YEU', 'NGUOC_1H', 'PHIEN_MONG', 'KHONG_RO')
COMBOS = ('F7', 'F10', 'F0')
EPS = 1e-9


def measure(r, df, f, vol_p25) -> dict:
    """Số đo nền + cờ thô của từng nhãn cho một lệnh (r = dòng _follow_trades_*.csv; giá theo tick)."""
    D, c, E = int(r.D), int(r.idx_c), int(r.E)
    se = int(f.send[c])
    out = dict(combo='', idx_c=c, t_utc=str(r.t_utc), t_vn=str(r.t_vn), side='buy' if D > 0 else 'sell', leg=int(r.leg),
               co=flags_of(r), outcome=r.outcome_alone, r=float(r.r_alone))
    # MOVE_GIA
    back = [j for j in range(c + 1, min(c + 5, se) + 1) if (int(f.C[j]) - E) * D <= 0]
    out['nen_dong_trong'] = (back[0] - c) if back else -1
    out['f_MOVE_GIA'] = int(bool(back))
    # SL_QUET
    ex = int(r.exit_alone)
    sl, tp = int(r.sl_S2), int(r.tp_S2)
    if r.outcome_alone == 'SL':
        pen = (sl - int(f.L[ex])) if D > 0 else (int(f.H[ex]) - sl)
        seg = range(ex + 1, min(len(f.C), ex + 31))
        hit = next((j - ex for j in seg if ((f.H[j] >= tp) if D > 0 else (f.L[j] <= tp))), -1)
        out['sl_xuyen_tick'] = int(pen)
        out['cham_tp_sau_sl_nen'] = int(hit)
        out['f_SL_QUET'] = int(pen <= 2 and hit > 0)
    else:
        out['sl_xuyen_tick'] = np.nan
        out['cham_tp_sau_sl_nen'] = np.nan
        out['f_SL_QUET'] = 0
    # HOI_SAU
    out['depth_frac'] = float(r.depth_frac)
    out['f_HOI_SAU'] = int(r.deep)
    # CF_YEU (phần hình nến của 4a)
    o, h, l, cl = int(f.O[c]), int(f.H[c]), int(f.L[c]), int(f.C[c])
    rng = h - l
    body = abs(cl - o) / rng if rng > 0 else 0.0
    ext = ((h - cl) if D > 0 else (cl - l)) / rng if rng > 0 else 1.0
    out['cf_than'] = round(body, 3)
    out['cf_dong_cuc_tri'] = round(ext, 3)
    out['f_CF_YEU'] = int(body < 0.4 - EPS or ext > 0.3 + EPS)
    # NGUOC_1H
    d1h = (int(f.C[c]) - int(f.C[c - 60])) * D if c >= 60 else np.nan
    out['d1h_tick_theo_D'] = d1h
    out['f_NGUOC_1H'] = int(d1h == d1h and d1h < 0)
    # PHIEN_MONG
    ph = str(df['phase'].iloc[c])
    out['phase'] = ph
    out['vol_c'] = float(f.V[c])
    out['vol_p25_phien'] = float(vol_p25[c])
    out['f_PHIEN_MONG'] = int(ph == 'A' or f.V[c] < vol_p25[c] - EPS)
    lab = next((k for k in LABELS[:-1] if out['f_' + k]), 'KHONG_RO')
    out['nhan'] = lab
    return out


def pct_table(m: pd.DataFrame, col: str) -> list:
    sl, tp = m[m['outcome'] == 'SL'], m[m['outcome'] == 'TP']
    L = [f"| Nhãn | % lệnh SL (n {len(sl)}) | % lệnh TP (n {len(tp)}) | đạt 5.3 (≥ 40 % SL và ≤ 20 % TP)? |", '|---|---|---|---|']
    for k in LABELS:
        if col == 'nhan':
            a = float((sl['nhan'] == k).mean()) if len(sl) else np.nan
            b = float((tp['nhan'] == k).mean()) if len(tp) else np.nan
        else:
            if k == 'KHONG_RO':
                continue
            a = float(sl['f_' + k].mean()) if len(sl) else np.nan
            b = float(tp['f_' + k].mean()) if len(tp) else np.nan
        ok = a == a and b == b and a >= 0.40 - EPS and b <= 0.20 + EPS
        nm = f'**{k}**' if ok else k
        L.append(f"| {nm} | {'**' if ok else ''}{100 * a:.1f} %{'**' if ok else ''} | {100 * b:.1f} % | {'**có**' if ok else 'không'} |"
                 .replace('.', ','))
    return L


def main():
    df, f = load_bars_train()
    # p25 volume theo phiên (toàn bộ nến của phiên)
    sid = df['session_no'].to_numpy()
    vol_p25 = pd.Series(f.V).groupby(sid).transform(lambda v: np.percentile(v, 25)).to_numpy()
    rows = []
    for combo in COMBOS:
        t = pd.read_csv(os.path.join(REPORT, f'_follow_trades_{combo}.csv')).sort_values('idx_c')
        for r in t.itertuples():
            x = measure(r, df, f, vol_p25)
            x['combo'] = combo
            rows.append(x)
    m = pd.DataFrame(rows)
    first = ['combo', 'idx_c', 'outcome', 'r', 'nhan']
    m = m[first + [c for c in m.columns if c not in first]]
    m.to_csv(os.path.join(REPORT, '_mo_sl_follow.csv'), index=False, encoding='utf-8')
    # ------------------------------------------------------------------ MO-SL-FOLLOW.md
    shots = {}
    for combo in ('F7', 'F10', 'F1'):
        od = os.path.join(SHOTS, combo)
        shots[combo] = sorted(x for x in os.listdir(od) if x.endswith('.png')) if os.path.isdir(od) else []
    L = ['# Mổ SL Follow — vòng 1 (chế độ "khám phá, hậu kiểm")', '',
         '> Opus, 2026-11-09, theo `plans/BENZO-FOLLOW-COMBO-plan.md` mục 5 + 9.2 + 9.3-B. **Chỉ TRAIN** (35 phiên dày, tới 2026-09-15). '
         'Đây là **bài học đọc chart**, không phải bước tới signal: F7 Δ 0,20 < ngưỡng hoán vị 0,31, p cực đại 0,76 (ngưỡng ≥ 30: p 0,23) — '
         '**không** được nói "F7 có lợi thế". Mọi luật rút ra ở đây (F7b/F10b) chỉ được đo lại trên TRAIN để báo, xác nhận duy nhất trên '
         'dữ liệu mới ≥ 22/10/2026. Tối đa 2 vòng mổ trên TRAIN; đây là vòng 1.', '',
         '## 0. Ảnh', '',
         '- Thư mục `report/follow_shots/<combo>/`; tên `SL_<idx_c>.png` / `TP_<idx_c>.png` (F1 có thêm `TIME_<idx_c>.png`). '
         '`idx_c` = bar_idx của nến CF trong file `fp_GCZ26_XCEC_Time_20260723-20261021_90d`.',
         '- Mỗi ảnh: nến M1 (~40 trước, ~30 sau), Δ dưới nến; hộp vàng = range tới nến đóng ngoài, đường nâu đậm = cạnh E; '
         'đường chấm dọc = nến đóng ngoài (ref); tam giác tím "x" = nến cực trị move; dải xám = nhịp hồi + CF; chữ "hồi" dưới nến hồi; '
         'mũi tên "CF"; đường xanh nét đứt = giá vào, đỏ = SL (S2), xanh lá = TP 2R; ô vuông màu = ô trap (đỏ) / bóng (xanh lá) / kiệt sức '
         '(cam) đúng mức giá; dải xanh = vùng stacked; vòng tròn + chú thích dưới đáy = cờ bật. Tiêu đề: combo · idx · giờ UTC (VN) · '
         'side · leg · cờ · kết cục R. **Không in nhãn máy lên ảnh.**',
         f"- Số ảnh: F7 {len(shots['F7'])} ({sum(x.startswith('SL') for x in shots['F7'])} SL + {sum(x.startswith('TP') for x in shots['F7'])} TP) · "
         f"F10 {len(shots['F10'])} ({sum(x.startswith('SL') for x in shots['F10'])} SL + {sum(x.startswith('TP') for x in shots['F10'])} TP) · "
         f"F1 {len(shots['F1'])} (cả 11 lệnh — chỉ soi định nghĩa trap, không rút luật).", '',
         '## 1. Nhãn tay của Fable', '',
         '> *(Để trống — Fable điền vòng sau. Quy tắc 9.2: Fable xem ≤ 10 ảnh SL + 5 ảnh TP mỗi combo và gắn nhãn tay **TRƯỚC** khi đọc mục 2.)*', '',
         '| Combo | ảnh | nhãn tay | ghi chú |', '|---|---|---|---|', '| | | | |', '',
         '## 2. Nhãn máy (`mo_sl_follow.py`, chi tiết từng lệnh ở `report/_mo_sl_follow.csv`)', '',
         '> ⚠️ Fable: gắn nhãn tay ở mục 1 trước khi đọc mục này.', '',
         'Danh mục 7 nhãn, ưu tiên từ trên xuống, mỗi lệnh đúng 1 nhãn: `MOVE_GIA` → `SL_QUET` → `HOI_SAU` → `CF_YEU` → `NGUOC_1H` → '
         '`PHIEN_MONG` → `KHONG_RO`. **`TIN` không đo được** (9.1-5: `NewsCalendar` chỉ có lịch tuần hiện tại, không có lịch sử 07–09/2026) ⇒ '
         'bỏ hạng này. Nhãn in đậm = đạt tiêu chí 5.3 (≥ 40 % lệnh SL **và** ≤ 20 % lệnh TP).', '']
    for combo in COMBOS:
        mm = m[m['combo'] == combo]
        n_time = int((mm['outcome'] == 'TIME').sum())
        L += [f'### {combo} — 1 nhãn/lệnh theo ưu tiên', '', f'Lệnh: {len(mm)} (SL {int((mm["outcome"] == "SL").sum())} · '
              f'TP {int((mm["outcome"] == "TP").sum())} · TIME {n_time} — TIME không vào bảng %).', '']
        L += pct_table(mm, 'nhan') + ['']
    L += ['### Phụ — tỷ lệ lệnh MANG từng đặc điểm (không áp ưu tiên, một lệnh có thể mang nhiều)', '',
          '> Chỉ để thấy nhãn ưu tiên cao có "che" nhãn dưới không. Tiêu chí 5.3 chấm trên bảng 1 nhãn/lệnh ở trên.', '']
    for combo in COMBOS:
        L += [f'**{combo}**', ''] + pct_table(m[m['combo'] == combo], 'flag') + ['']
    # ghi chú: MOVE_GIA so với thời điểm dính SL (nhãn đo SAU khi vào lệnh)
    L += ['### Ghi chú Opus — `MOVE_GIA` gần như trùng "SL nhanh" (đọc trước khi rút luật từ nhãn này)', '',
          '| Combo | lệnh SL mang MOVE_GIA | nến đóng trong range TRƯỚC nến dính SL | CÙNG nến dính SL | SAU nến dính SL | lệnh TP thoát ≤ 5 nến |',
          '|---|---|---|---|---|---|']
    for combo in COMBOS:
        mm = m[m['combo'] == combo]
        t = pd.read_csv(os.path.join(REPORT, f'_follow_trades_{combo}.csv'))[['idx_c', 'exit_alone']]
        x = mm.merge(t, on='idx_c')
        k_exit = x['exit_alone'] - x['idx_c']
        g = (x['outcome'] == 'SL') & (x['f_MOVE_GIA'] == 1)
        nd = x['nen_dong_trong']
        tp = x['outcome'] == 'TP'
        L.append(f"| {combo} | {int(g.sum())} | {int((g & (nd < k_exit)).sum())} | {int((g & (nd == k_exit)).sum())} | "
                 f"{int((g & (nd > k_exit)).sum())} | {int((tp & (k_exit <= 5)).sum())}/{int(tp.sum())} |")
    L += ['', 'S2 đặt SL ngay dưới cạnh E (min(E, đáy nhịp hồi) − đệm), nên "có nến đóng về trong range trong 5 nến" phần lớn xảy ra '
          '**ở chính nến dính SL**; còn lệnh TP muốn mang nhãn thì phải có nến đóng ≤ E mà râu không chạm SL (SL chỉ cách E một đệm ≈ 3 tick) — gần như không thể. Vì vậy `% TP = 0` của `MOVE_GIA` '
          'một phần là **cơ học**, và nhãn này đo **sau khi vào lệnh** (không quan sát được lúc vào). Luật suy từ nó (5.5: "đòi CF ≥ x+2 và '
          'nến hồi không chạm E") phải là điều kiện **biết được tại nến CF**. Opus chỉ ghi số, không đề xuất luật.', '']
    L += ['### Cách Opus hiểu các chỗ plan chưa ghi rõ', '',
          '- `MOVE_GIA`: xét nến c+1 … c+5 (cùng phiên), "đóng trong range" = (close − E)·D ≤ 0, giống cách máy Follow kết thúc cú phá.',
          '- `SL_QUET`: "râu ≤ 2 tick quá SL" đo ở nến dính SL (`exit_alone`): D = +1 là SL − low ≤ 2 tick. "Chạm TP gốc trong 30 nến" = '
          'nến exit+1 … exit+30 (theo chỉ số nến, có thể vắt qua khoảng trống phiên — như `controls_corven.sl_then_tp`). Lệnh TP/TIME không mang nhãn này.',
          '- `CF_YEU`: chỉ hai điều kiện hình nến plan ghi trong ngoặc (thân < 0,4 biên độ; đóng–cực trị > 0,3 biên độ), không xét biên độ ≥ 0,5 mbr '
          'và Δ ≥ 0,5 medΔ của 4a.',
          '- `NGUOC_1H`: c − 60 theo chỉ số nến (có thể vắt qua khoảng trống phiên); c < 60 thì không gắn.',
          '- `PHIEN_MONG`: phiên Á = cột `phase` = A (05:00–12:30 VN); p25 volume tính trên **mọi nến của phiên đó** (kể cả nến sau c — '
          'nhãn mô tả hậu kiểm, không dùng để vào lệnh).', '',
          '## 3. Luật đề xuất', '',
          '> *(Để trống — Fable điền vòng sau: tối đa 1 luật/combo, suy trực tiếp từ nhãn đạt 5.3 → `F7b`/`F10b`, đo lại trên TRAIN chỉ để báo.)*', '']
    with open(os.path.join(REPORT, 'MO-SL-FOLLOW.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('\n'.join(L[L.index('## 2. Nhãn máy (`mo_sl_follow.py`, chi tiết từng lệnh ở `report/_mo_sl_follow.csv`)'):]))
    return m


if __name__ == '__main__':
    main()
