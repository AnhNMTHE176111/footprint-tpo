# Mổ SL Follow — vòng 1 (chế độ "khám phá, hậu kiểm")

> Opus, 2026-11-09, theo `plans/BENZO-FOLLOW-COMBO-plan.md` mục 5 + 9.2 + 9.3-B. **Chỉ TRAIN** (35 phiên dày, tới 2026-09-15). Đây là **bài học đọc chart**, không phải bước tới signal: F7 Δ 0,20 < ngưỡng hoán vị 0,31, p cực đại 0,76 (ngưỡng ≥ 30: p 0,23) — **không** được nói "F7 có lợi thế". Mọi luật rút ra ở đây (F7b/F10b) chỉ được đo lại trên TRAIN để báo, xác nhận duy nhất trên dữ liệu mới ≥ 22/10/2026. Tối đa 2 vòng mổ trên TRAIN; đây là vòng 1.

## 0. Ảnh

- Thư mục `report/follow_shots/<combo>/`; tên `SL_<idx_c>.png` / `TP_<idx_c>.png` (F1 có thêm `TIME_<idx_c>.png`). `idx_c` = bar_idx của nến CF trong file `fp_GCZ26_XCEC_Time_20260723-20261021_90d`.
- Mỗi ảnh: nến M1 (~40 trước, ~30 sau), Δ dưới nến; hộp vàng = range tới nến đóng ngoài, đường nâu đậm = cạnh E; đường chấm dọc = nến đóng ngoài (ref); tam giác tím "x" = nến cực trị move; dải xám = nhịp hồi + CF; chữ "hồi" dưới nến hồi; mũi tên "CF"; đường xanh nét đứt = giá vào, đỏ = SL (S2), xanh lá = TP 2R; ô vuông màu = ô trap (đỏ) / bóng (xanh lá) / kiệt sức (cam) đúng mức giá; dải xanh = vùng stacked; vòng tròn + chú thích dưới đáy = cờ bật. Tiêu đề: combo · idx · giờ UTC (VN) · side · leg · cờ · kết cục R. **Không in nhãn máy lên ảnh.**
- Số ảnh: F7 60 (55 SL + 5 TP) · F10 78 (73 SL + 5 TP) · F1 11 (cả 11 lệnh — chỉ soi định nghĩa trap, không rút luật).

## 1. Nhãn tay của Fable

> *(Để trống — Fable điền vòng sau. Quy tắc 9.2: Fable xem ≤ 10 ảnh SL + 5 ảnh TP mỗi combo và gắn nhãn tay **TRƯỚC** khi đọc mục 2.)*

| Combo | ảnh | nhãn tay | ghi chú |
|---|---|---|---|
| | | | |

## 2. Nhãn máy (`mo_sl_follow.py`, chi tiết từng lệnh ở `report/_mo_sl_follow.csv`)

> ⚠️ Fable: gắn nhãn tay ở mục 1 trước khi đọc mục này.

Danh mục 7 nhãn, ưu tiên từ trên xuống, mỗi lệnh đúng 1 nhãn: `MOVE_GIA` → `SL_QUET` → `HOI_SAU` → `CF_YEU` → `NGUOC_1H` → `PHIEN_MONG` → `KHONG_RO`. **`TIN` không đo được** (9.1-5: `NewsCalendar` chỉ có lịch tuần hiện tại, không có lịch sử 07–09/2026) ⇒ bỏ hạng này. Nhãn in đậm = đạt tiêu chí 5.3 (≥ 40 % lệnh SL **và** ≤ 20 % lệnh TP).

### F7 — 1 nhãn/lệnh theo ưu tiên

Lệnh: 96 (SL 55 · TP 40 · TIME 1 — TIME không vào bảng %).

| Nhãn | % lệnh SL (n 55) | % lệnh TP (n 40) | đạt 5.3 (≥ 40 % SL và ≤ 20 % TP)? |
|---|---|---|---|
| **MOVE_GIA** | **47,3 %** | 0,0 % | **có** |
| SL_QUET | 5,5 % | 0,0 % | không |
| HOI_SAU | 18,2 % | 27,5 % | không |
| CF_YEU | 14,5 % | 42,5 % | không |
| NGUOC_1H | 1,8 % | 10,0 % | không |
| PHIEN_MONG | 5,5 % | 15,0 % | không |
| KHONG_RO | 7,3 % | 5,0 % | không |

### F10 — 1 nhãn/lệnh theo ưu tiên

Lệnh: 120 (SL 73 · TP 47 · TIME 0 — TIME không vào bảng %).

| Nhãn | % lệnh SL (n 73) | % lệnh TP (n 47) | đạt 5.3 (≥ 40 % SL và ≤ 20 % TP)? |
|---|---|---|---|
| MOVE_GIA | 28,8 % | 0,0 % | không |
| SL_QUET | 2,7 % | 0,0 % | không |
| HOI_SAU | 21,9 % | 36,2 % | không |
| CF_YEU | 24,7 % | 36,2 % | không |
| NGUOC_1H | 4,1 % | 4,3 % | không |
| PHIEN_MONG | 6,8 % | 12,8 % | không |
| KHONG_RO | 11,0 % | 10,6 % | không |

### F0 — 1 nhãn/lệnh theo ưu tiên

Lệnh: 340 (SL 222 · TP 113 · TIME 5 — TIME không vào bảng %).

| Nhãn | % lệnh SL (n 222) | % lệnh TP (n 113) | đạt 5.3 (≥ 40 % SL và ≤ 20 % TP)? |
|---|---|---|---|
| MOVE_GIA | 34,2 % | 0,0 % | không |
| SL_QUET | 3,6 % | 0,0 % | không |
| HOI_SAU | 16,7 % | 35,4 % | không |
| CF_YEU | 15,3 % | 33,6 % | không |
| NGUOC_1H | 5,9 % | 5,3 % | không |
| PHIEN_MONG | 12,2 % | 14,2 % | không |
| KHONG_RO | 12,2 % | 11,5 % | không |

### Phụ — tỷ lệ lệnh MANG từng đặc điểm (không áp ưu tiên, một lệnh có thể mang nhiều)

> Chỉ để thấy nhãn ưu tiên cao có "che" nhãn dưới không. Tiêu chí 5.3 chấm trên bảng 1 nhãn/lệnh ở trên.

**F7**

| Nhãn | % lệnh SL (n 55) | % lệnh TP (n 40) | đạt 5.3 (≥ 40 % SL và ≤ 20 % TP)? |
|---|---|---|---|
| **MOVE_GIA** | **47,3 %** | 0,0 % | **có** |
| SL_QUET | 14,5 % | 0,0 % | không |
| HOI_SAU | 45,5 % | 27,5 % | không |
| CF_YEU | 43,6 % | 50,0 % | không |
| NGUOC_1H | 25,5 % | 27,5 % | không |
| PHIEN_MONG | 47,3 % | 47,5 % | không |

**F10**

| Nhãn | % lệnh SL (n 73) | % lệnh TP (n 47) | đạt 5.3 (≥ 40 % SL và ≤ 20 % TP)? |
|---|---|---|---|
| MOVE_GIA | 28,8 % | 0,0 % | không |
| SL_QUET | 5,5 % | 0,0 % | không |
| HOI_SAU | 34,2 % | 36,2 % | không |
| CF_YEU | 46,6 % | 46,8 % | không |
| NGUOC_1H | 20,5 % | 25,5 % | không |
| PHIEN_MONG | 38,4 % | 46,8 % | không |

**F0**

| Nhãn | % lệnh SL (n 222) | % lệnh TP (n 113) | đạt 5.3 (≥ 40 % SL và ≤ 20 % TP)? |
|---|---|---|---|
| MOVE_GIA | 34,2 % | 0,0 % | không |
| SL_QUET | 9,0 % | 0,0 % | không |
| HOI_SAU | 39,2 % | 35,4 % | không |
| CF_YEU | 41,0 % | 44,2 % | không |
| NGUOC_1H | 28,8 % | 21,2 % | không |
| PHIEN_MONG | 50,5 % | 47,8 % | không |

### Ghi chú Opus — `MOVE_GIA` gần như trùng "SL nhanh" (đọc trước khi rút luật từ nhãn này)

| Combo | lệnh SL mang MOVE_GIA | nến đóng trong range TRƯỚC nến dính SL | CÙNG nến dính SL | SAU nến dính SL | lệnh TP thoát ≤ 5 nến |
|---|---|---|---|---|---|
| F7 | 26 | 4 | 17 | 5 | 3/40 |
| F10 | 21 | 2 | 14 | 5 | 6/47 |
| F0 | 76 | 14 | 51 | 11 | 14/113 |

S2 đặt SL ngay dưới cạnh E (min(E, đáy nhịp hồi) − đệm), nên "có nến đóng về trong range trong 5 nến" phần lớn xảy ra **ở chính nến dính SL**; còn lệnh TP muốn mang nhãn thì phải có nến đóng ≤ E mà râu không chạm SL (SL chỉ cách E một đệm ≈ 3 tick) — gần như không thể. Vì vậy `% TP = 0` của `MOVE_GIA` một phần là **cơ học**, và nhãn này đo **sau khi vào lệnh** (không quan sát được lúc vào). Luật suy từ nó (5.5: "đòi CF ≥ x+2 và nến hồi không chạm E") phải là điều kiện **biết được tại nến CF**. Opus chỉ ghi số, không đề xuất luật.

### Cách Opus hiểu các chỗ plan chưa ghi rõ

- `MOVE_GIA`: xét nến c+1 … c+5 (cùng phiên), "đóng trong range" = (close − E)·D ≤ 0, giống cách máy Follow kết thúc cú phá.
- `SL_QUET`: "râu ≤ 2 tick quá SL" đo ở nến dính SL (`exit_alone`): D = +1 là SL − low ≤ 2 tick. "Chạm TP gốc trong 30 nến" = nến exit+1 … exit+30 (theo chỉ số nến, có thể vắt qua khoảng trống phiên — như `controls_corven.sl_then_tp`). Lệnh TP/TIME không mang nhãn này.
- `CF_YEU`: chỉ hai điều kiện hình nến plan ghi trong ngoặc (thân < 0,4 biên độ; đóng–cực trị > 0,3 biên độ), không xét biên độ ≥ 0,5 mbr và Δ ≥ 0,5 medΔ của 4a.
- `NGUOC_1H`: c − 60 theo chỉ số nến (có thể vắt qua khoảng trống phiên); c < 60 thì không gắn.
- `PHIEN_MONG`: phiên Á = cột `phase` = A (05:00–12:30 VN); p25 volume tính trên **mọi nến của phiên đó** (kể cả nến sau c — nhãn mô tả hậu kiểm, không dùng để vào lệnh).

## 3. Luật đề xuất

> *(Để trống — Fable điền vòng sau: tối đa 1 luật/combo, suy trực tiếp từ nhãn đạt 5.3 → `F7b`/`F10b`, đo lại trên TRAIN chỉ để báo.)*

