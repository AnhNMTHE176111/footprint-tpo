# RESULTS-B-v2 — Setup B "Hấp thụ" mở từ 2 vùng VWAP lên 8 loại vùng (12 mức)

Sinh bởi `setup_b_v2.py` (deterministic) theo `plans/BENZO-B-v2-plan.md`. **Chỉ file 90d GCZ26** `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (một hợp đồng, kiểm `splice_jump.any() == False` ✔), 86333 nến M1, 61 phiên sạch (TRAIN 35 ≤ 2026-09-15, TEST 26). Giờ UTC (VN = UTC+7). Cấu hình duy nhất: θ 0,5 · N 3 · TP 3R · mono "ends" · biến thể "base" · không bias · mọi pha trừ OFF. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ SL; 1 lệnh mở cùng lúc; tối đa 2 lệnh / (loại vùng, phiên).

## 0. Kỳ vọng đăng ký TRƯỚC khi chạy (plan 3.6, chép nguyên từ hằng số đã commit)

- n: 11 → **20–60** (6 loại mới; HVN_W/POC_W thường cách giá 20–80 giá ⇒ ít chạm; POC_D/VAH/VAL/HVN_D gần giá hơn ⇒ đóng góp chính). n không tăng ≥ 2× ⇒ bộ lọc cụm/θ là nút thắt, không phải vùng.
- WR ở 3R: **25–35 %** (hoà vốn ~27 %). Kỳ vọng hợp lý: **B-v2 ≈ dải ĐC1** (vị trí vùng không mang thông tin — khớp mọi phép đo S/R trước).
- Không ép: không chọn ô độ nhạy đẹp; TP 2R không chạy; không thêm bộ lọc mới giữa chừng.

Tái tạo B cũ (điều kiện tiên quyết): n = 11, WR 27,3 %, R TB 0,00, danh sách idx khớp fixture `report/_b_old_idx.json` ✔.

## 1. Tập vùng — có mặt, trùng nhau, khoảng cách

| mức | số phiên sạch có mức (/61) | số nến đo được chạm mức (\|close − Z\| ≤ 1 hoặc râu chạm) | trung vị \|close − Z\| (giá) |
|---|---|---|---|
| VWAP_W | 61 | 2827 | 20,5 |
| VWAP_D | 61 | 5105 | 10,9 |
| POC_D | 61 | 2867 | 23,0 |
| VAH_D | 61 | 2361 | 28,4 |
| VAL_D | 61 | 2366 | 27,7 |
| HVN_D1 | 40 | 1779 | 23,3 |
| HVN_D2 | 15 | 704 | 23,5 |
| HVN_D3 | 4 | 283 | 19,1 |
| POC_W | 58 | 524 | 72,6 |
| HVN_W1 | 51 | 709 | 91,4 |
| HVN_W2 | 31 | 258 | 236,8 |
| HVN_W3 | 23 | 271 | 263,4 |

- Phiên sạch **không có POC_W**: 2026-07-29, 2026-07-30, 2026-07-31 (tuần đầu file không có tuần trước; tuần 07-27…07-31 dựng trên tuần 07-23/24 chỉ có 2 phiên, đều thin ⇒ NaN theo luật ≥ 3 phiên không thin). Tuần 08-03…08-07 có POC_W = POC của 3 phiên 07-29/30/31 (không thin).
- |POC_W − HVN_W1| trên 48 phiên có cả hai: trung vị 71,0 giá (min 1,0, max 244,2) — POC_W (1 tuần) KHÁC HVN_W1 (gộp 3 tuần) nên không trùng lặp.
- HVN_W dựng trên cửa sổ có phiên thin (kernel không loại thin ở `week_hvn`): 13 phiên sạch (2026-07-29, 2026-07-30, 2026-07-31, 2026-08-10, 2026-08-11, 2026-08-12, 2026-08-13, 2026-08-14, 2026-08-17, 2026-08-18, 2026-08-19, 2026-08-20, 2026-08-21). Cờ `hvn_w_partial` (cửa sổ cắt bởi chỗ nối): 0 phiên.
- POC_D/VAH_D/VAL_D/HVN_D của 2026-07-29 dựng trên phiên thin 07-28 (kernel không loại thin ở "hôm qua") — 1 phiên, ghi chú, không sửa.
- **Tỉ lệ trùng** (plan 1.4.5): 88 / 1980 cặp mức KHÁC loại cách nhau ≤ 1 giá (4,4 %); trung bình 8,6 mức/phiên. VWAP lấy giá trị nến cuối phiên (chỉ để mô tả).

Trung vị khoảng cách giữa các loại (giá):

| cặp loại | trung vị |
|---|---|
| HVN_D ↔ POC_D | 1,0 |
| VWAP_D ↔ VWAP_W | 14,3 |
| HVN_D ↔ VWAP_W | 17,4 |
| POC_D ↔ VAH_D | 18,8 |
| POC_D ↔ VWAP_W | 19,5 |
| HVN_D ↔ VWAP_D | 19,7 |
| POC_D ↔ VAL_D | 20,0 |
| VAH_D ↔ VWAP_W | 20,6 |
| POC_D ↔ VWAP_D | 20,8 |
| HVN_D ↔ VAH_D | 22,2 |
| HVN_D ↔ VAL_D | 22,6 |
| VAL_D ↔ VWAP_W | 22,8 |
| VAH_D ↔ VWAP_D | 29,0 |
| VAL_D ↔ VWAP_D | 30,1 |
| VAH_D ↔ VAL_D | 39,6 |
| POC_W ↔ VAL_D | 56,2 |
| POC_D ↔ POC_W | 56,4 |
| POC_W ↔ VAH_D | 63,2 |
| POC_W ↔ VWAP_D | 68,0 |
| POC_W ↔ VWAP_W | 71,0 |
| HVN_D ↔ POC_W | 86,2 |
| HVN_W ↔ POC_W | 115,0 |
| HVN_D ↔ HVN_W | 127,4 |
| HVN_W ↔ POC_D | 135,0 |
| HVN_W ↔ VAH_D | 149,8 |
| HVN_W ↔ VWAP_D | 151,2 |
| HVN_W ↔ VWAP_W | 158,3 |
| HVN_W ↔ VAL_D | 158,6 |

## 2. Công suất thống kê (in TRƯỚC bảng chính — plan 3.3)

- Sai số WR ≈ √(p(1−p)/n), p = 0,27: n = 11 ⇒ ±13,4 điểm; n = 25 ⇒ ±8,9 điểm.
- Chênh WR nhỏ nhất phát hiện được (80 %, hai phía) giữa B-cũ (n=11) và B-v2 (n=25): ≈ **45 điểm**; chênh R TB nhỏ nhất ≈ **1,93R** (σ_R = 1,91). ⇒ **so WR cũ ↔ mới trực tiếp gần như vô nghĩa**; phán quyết dựa vào dải đối chứng và nhóm lệnh chỉ-v2.

## 3. Bảng chính — 15 cấu hình (plan 3.1)

n = lệnh đã đóng; lệnh/ngày chia 61 phiên sạch; KTC = khoảng tin cậy 95 % bootstrap (10 000, seed 0) của R TB.

| cấu hình | n | lệnh/ngày | **WR** | R TB | KTC 95 % | kỳ vọng giá/lệnh | tổng R | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| B-cũ | 11 | 0,18 | **27,3 %** | 0,00 | [-1,07 ; 1,10] | 0,07 | 0,0 | 4 |
| B-v2 | 25 | 0,41 | **32,0 %** | 0,19 | [-0,46 ; 0,99] | 0,73 | 4,7 | 5 |
| | | | | | | | | |
| B-mới-thôi | 15 | 0,25 | **40,0 %** | 0,51 | [-0,56 ; 1,58] | 1,61 | 7,6 | 3 |
| B-cũ + POC_D | 14 | 0,23 | **28,6 %** | 0,06 | [-0,81 ; 0,93] | 0,39 | 0,8 | 4 |
| B-cũ + VAH_D | 17 | 0,28 | **29,4 %** | 0,09 | [-0,64 ; 1,03] | 0,47 | 1,5 | 4 |
| B-cũ + VAL_D | 12 | 0,20 | **25,0 %** | -0,09 | [-1,08 ; 0,92] | -0,11 | -1,1 | 5 |
| B-cũ + HVN_D | 13 | 0,21 | **23,1 %** | -0,17 | [-1,08 ; 0,77] | -0,33 | -2,2 | 4 |
| B-cũ + HVN_W | 14 | 0,23 | **35,7 %** | 0,33 | [-0,54 ; 1,47] | 0,75 | 4,7 | 4 |
| B-cũ + POC_W | 11 | 0,18 | **27,3 %** | 0,00 | [-1,07 ; 1,10] | 0,07 | 0,0 | 4 |
| B-v2 − POC_D | 23 | 0,38 | **30,4 %** | 0,12 | [-0,58 ; 0,83] | 0,46 | 2,9 | 5 |
| B-v2 − VAH_D | 19 | 0,31 | **31,6 %** | 0,17 | [-0,67 ; 1,02] | 0,58 | 3,3 | 5 |
| B-v2 − VAL_D | 24 | 0,39 | **33,3 %** | 0,24 | [-0,43 ; 1,07] | 0,85 | 5,8 | 4 |
| B-v2 − HVN_D | 24 | 0,39 | **33,3 %** | 0,24 | [-0,43 ; 1,07] | 0,84 | 5,8 | 5 |
| B-v2 − HVN_W | 22 | 0,36 | **27,3 %** | 0,00 | [-0,73 ; 0,74] | 0,39 | 0,0 | 5 |
| B-v2 − POC_W | 25 | 0,41 | **32,0 %** | 0,19 | [-0,46 ; 0,99] | 0,73 | 4,7 | 5 |

Theo nửa và tháng (`n · WR · R TB`; T8 gồm 29–31/7):

| cấu hình | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| B-cũ | 7 · 28,6 % · 0,04 | 4 · 25,0 % · -0,07 | 4 · 25,0 % · -0,11 | 6 · 16,7 % · -0,41 | 1 · 100,0 % · 2,94 |
| B-v2 | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,45 | 7 · 14,3 % · -0,53 | 8 · 25,0 % · -0,08 | 10 · 50,0 % · 0,91 |
| B-mới-thôi | 6 · 33,3 % · 0,25 | 9 · 44,4 % · 0,68 | 3 · 0,0 % · -1,09 | 3 · 66,7 % · 1,58 | 9 · 44,4 % · 0,68 |
| B-cũ + POC_D | 10 · 30,0 % · 0,11 | 4 · 25,0 % · -0,07 | 6 · 16,7 % · -0,44 | 7 · 28,6 % · 0,07 | 1 · 100,0 % · 2,94 |
| B-cũ + VAH_D | 8 · 25,0 % · -0,10 | 9 · 33,3 % · 0,25 | 5 · 20,0 % · -0,31 | 6 · 16,7 % · -0,41 | 6 · 50,0 % · 0,92 |
| B-cũ + VAL_D | 8 · 25,0 % · -0,10 | 4 · 25,0 % · -0,07 | 4 · 25,0 % · -0,11 | 7 · 14,3 % · -0,51 | 1 · 100,0 % · 2,94 |
| B-cũ + HVN_D | 8 · 25,0 % · -0,10 | 5 · 20,0 % · -0,28 | 5 · 20,0 % · -0,30 | 6 · 16,7 % · -0,41 | 2 · 50,0 % · 0,91 |
| B-cũ + HVN_W | 7 · 28,6 % · 0,04 | 7 · 42,9 % · 0,63 | 4 · 25,0 % · -0,11 | 6 · 16,7 % · -0,41 | 4 · 75,0 % · 1,90 |
| B-cũ + POC_W | 7 · 28,6 % · 0,04 | 4 · 25,0 % · -0,07 | 4 · 25,0 % · -0,11 | 6 · 16,7 % · -0,41 | 1 · 100,0 % · 2,94 |
| B-v2 − POC_D | 10 · 20,0 % · -0,30 | 13 · 38,5 % · 0,45 | 6 · 16,7 % · -0,44 | 7 · 14,3 % · -0,51 | 10 · 50,0 % · 0,91 |
| B-v2 − VAH_D | 11 · 27,3 % · -0,00 | 8 · 37,5 % · 0,41 | 6 · 16,7 % · -0,44 | 8 · 25,0 % · -0,08 | 5 · 60,0 % · 1,30 |
| B-v2 − VAL_D | 11 · 27,3 % · -0,00 | 13 · 38,5 % · 0,45 | 7 · 14,3 % · -0,53 | 7 · 28,6 % · 0,07 | 10 · 50,0 % · 0,91 |
| B-v2 − HVN_D | 12 · 25,0 % · -0,09 | 12 · 41,7 % · 0,58 | 7 · 14,3 % · -0,53 | 8 · 25,0 % · -0,08 | 9 · 55,6 % · 1,13 |
| B-v2 − HVN_W | 12 · 25,0 % · -0,09 | 10 · 30,0 % · 0,12 | 7 · 14,3 % · -0,53 | 8 · 25,0 % · -0,08 | 7 · 42,9 % · 0,63 |
| B-v2 − POC_W | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,45 | 7 · 14,3 % · -0,53 | 8 · 25,0 % · -0,08 | 10 · 50,0 % · 0,91 |

Theo pha và chiều (`n · WR · R TB`):

| cấu hình | A | EU | US | BUY | SELL |
|---|---|---|---|---|---|
| B-cũ | 8 · 25,0 % · -0,09 | 2 · 0,0 % · -1,07 | 1 · 100,0 % · 2,90 | 4 · 50,0 % · 0,92 | 7 · 14,3 % · -0,53 |
| B-v2 | 13 · 30,8 % · 0,13 | 10 · 30,0 % · 0,12 | 2 · 50,0 % · 0,90 | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,44 |
| B-mới-thôi | 6 · 50,0 % · 0,89 | 8 · 37,5 % · 0,42 | 1 · 0,0 % · -1,10 | 9 · 22,2 % · -0,20 | 6 · 66,7 % · 1,57 |
| B-cũ + POC_D | 8 · 25,0 % · -0,09 | 5 · 20,0 % · -0,27 | 1 · 100,0 % · 2,90 | 6 · 33,3 % · 0,26 | 8 · 25,0 % · -0,09 |
| B-cũ + VAH_D | 11 · 27,3 % · -0,00 | 5 · 20,0 % · -0,28 | 1 · 100,0 % · 2,90 | 8 · 25,0 % · -0,09 | 9 · 33,3 % · 0,24 |
| B-cũ + VAL_D | 9 · 22,2 % · -0,21 | 2 · 0,0 % · -1,07 | 1 · 100,0 % · 2,90 | 4 · 50,0 % · 0,92 | 8 · 12,5 % · -0,60 |
| B-cũ + HVN_D | 8 · 25,0 % · -0,09 | 4 · 0,0 % · -1,08 | 1 · 100,0 % · 2,90 | 5 · 40,0 % · 0,53 | 8 · 12,5 % · -0,60 |
| B-cũ + HVN_W | 9 · 33,3 % · 0,23 | 3 · 33,3 % · 0,26 | 2 · 50,0 % · 0,90 | 6 · 50,0 % · 0,92 | 8 · 25,0 % · -0,10 |
| B-cũ + POC_W | 8 · 25,0 % · -0,09 | 2 · 0,0 % · -1,07 | 1 · 100,0 % · 2,90 | 4 · 50,0 % · 0,92 | 7 · 14,3 % · -0,53 |
| B-v2 − POC_D | 13 · 30,8 % · 0,13 | 8 · 25,0 % · -0,08 | 2 · 50,0 % · 0,90 | 11 · 27,3 % · 0,01 | 12 · 33,3 % · 0,23 |
| B-v2 − VAH_D | 10 · 30,0 % · 0,10 | 7 · 28,6 % · 0,07 | 2 · 50,0 % · 0,90 | 8 · 37,5 % · 0,42 | 11 · 27,3 % · -0,01 |
| B-v2 − VAL_D | 12 · 33,3 % · 0,23 | 10 · 30,0 % · 0,12 | 2 · 50,0 % · 0,90 | 12 · 25,0 % · -0,09 | 12 · 41,7 % · 0,57 |
| B-v2 − HVN_D | 13 · 30,8 % · 0,13 | 9 · 33,3 % · 0,26 | 2 · 50,0 % · 0,90 | 12 · 25,0 % · -0,09 | 12 · 41,7 % · 0,57 |
| B-v2 − HVN_W | 12 · 25,0 % · -0,10 | 9 · 22,2 % · -0,19 | 1 · 100,0 % · 2,90 | 10 · 20,0 % · -0,29 | 12 · 33,3 % · 0,24 |
| B-v2 − POC_W | 13 · 30,8 % · 0,13 | 10 · 30,0 % · 0,12 | 2 · 50,0 % · 0,90 | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,44 |

## 4. Tách đóng góp ở mức LỆNH (plan 3.2)

Tính chất tập con kiểm bằng assert: mọi lệnh thô của B-cũ đều có trong B-v2 với cùng chiều/entry/SL/TP/Z ✔ (11 ⊆ 25 lệnh thô).

| nhóm | n · WR · R TB | KTC 95 % | TRAIN | TEST |
|---|---|---|---|---|
| Lệnh chung (có ở cả hai bản đã mô phỏng) | 11 · 27,3 % · 0,00 | [-1,07 ; 1,10] | 7 · 28,6 % · 0,04 | 4 · 25,0 % · -0,07 |
| **Lệnh chỉ-v2** (nhóm quyết định) | 14 · 35,7 % · 0,34 | [-0,53 ; 1,47] | 5 · 20,0 % · -0,29 | 9 · 44,4 % · 0,68 |
| Lệnh cũ bị MẤT ở v2 (số liệu trong bản cũ) | 0 · – · – | [– ; –] | 0 · – · – | 0 · – · – |

Lệnh cũ bị mất do `one_at_a_time` (lệnh vùng mới mở trước chặn): 0 lệnh, trong đó 0 lệnh thắng.

### Theo loại vùng (lệnh B-v2). Loại n < 10 chỉ in số, không bình luận.

*Vùng thắng* = ztype ghi trên lệnh (thứ tự ưu tiên VWAP trước). *Bất kỳ vùng* = lệnh tính cho mọi loại có trong `zones_hit` (tổng > n).

| loại | vùng thắng: n · WR · R TB | bất kỳ vùng: n · WR · R TB |
|---|---|---|
| VWAP_W | 3 · 33,3 % · 0,24 | 3 · 33,3 % · 0,24 |
| VWAP_D | 8 · 25,0 % · -0,09 | 10 · 30,0 % · 0,11 |
| POC_D | 3 · 33,3 % · 0,26 | 3 · 33,3 % · 0,26 |
| VAH_D | 6 · 33,3 % · 0,24 | 6 · 33,3 % · 0,24 |
| VAL_D | 1 · 0,0 % · -1,11 | 1 · 0,0 % · -1,11 |
| HVN_D | 1 · 0,0 % · -1,12 | 3 · 33,3 % · 0,24 |
| HVN_W | 3 · 66,7 % · 1,56 | 3 · 66,7 % · 1,56 |
| POC_W | 0 · – · – | 0 · – · – |

### Số mức cùng khớp tại nến xác nhận (`n_hit`, chỉ mô tả, không lọc)

| n_hit | n · WR · R TB |
|---|---|
| 1 | 21 · 28,6 % · 0,05 |
| 2 | 4 · 50,0 % · 0,91 |
| ≥ 3 | 0 · – · – |

### Phễu lọc (số ứng viên qua từng bước, cộng mọi mức và hai chiều; chưa gồm trần 2 lệnh / one-at-a-time)

| bước | B-cũ | B-v2 |
|---|---|---|
| 1 CF dung + cum cham Z | 1528 | 3849 |
| 2 + than/delta giam dan | 498 | 1227 |
| 3 + cuc tri <= Z+0,5 | 82 | 214 |
| 4 + khong TREND/pha VA/nen lon nhat | 78 | 196 |
| 5 + move >= 3 gia | 45 | 108 |
| 6 + \|delta_CF\| >= theta*max | 15 | 34 |
| 7 + risk() hop le (SL<=4 gia) | 13 | 29 |

## 5. Đối chứng (plan 3.4)

**ĐC1 — dời bản đồ vùng:** mọi mức của phiên (12 mức, kể cả VWAP động: cộng hằng δ) dời cùng δ[phiên, bản], |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, 100 bản, seed 20261024 (ma trận y hệt BENZO-VCL, test `test_shift_matrix_same_as_vcl`). Chạy NGUYÊN `detect` + `simulate` trên mảng dời ⇒ lệnh dời cũng chạm vùng (dời) ≤ 1 giá, cùng cơ chế move → cụm → nến xác nhận; chỉ VỊ TRÍ khác (= đối chứng khớp khoảng cách theo xây dựng). Bộ lọc chế độ/VA Âu/IB không dời. Nhóm "chỉ-v2" ở bản dời = lệnh B-v2 dời không có trong B-cũ dời cùng bản.

**ĐC2 — vào ngẫu nhiên tại đúng mức:** `kernel.control_sample` (không sửa, qua `_patched_map`), mỗi lệnh thật rút 1 nến chạm ĐÚNG mức đó (|close − mức| ≤ 1 hoặc râu chạm), cùng chế độ kernel, cùng chiều, cùng R:R, SL = râu nến + 0,3; 200 lần.

**Ngưỡng "khác đối chứng"** (nguyên PLAN-LAN-CHAM mục 5): ngoài dải 5–95 % ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số ở cả hai; chỉ áp dụng khi nhóm có ≥ 10 lệnh ở CẢ TRAIN và TEST.

### ĐC1 — thật vs dải 100 bản dời (`thật | TB dời [5 % ; 95 %]`)

| nhóm | đo | GỘP | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|---|---|
| B-cũ | n | 11 \| 7 [4 ; 12] | 7 \| 4 [1 ; 7] | 4 \| 4 [1 ; 7] | 4 \| 2 [0 ; 5] | 6 \| 2 [0 ; 5] | 1 \| 2 [0 ; 5] |
| B-cũ | WR | 27,3 % \| 31,3 % [10,6 % ; 60,3 %] | 28,6 % \| 36,3 % [0,0 % ; 100,0 %] | 25,0 % \| 28,2 % [0,0 % ; 100,0 %] | 25,0 % \| 26,5 % [0,0 % ; 100,0 %] | 16,7 % \| 39,6 % [0,0 % ; 100,0 %] | 100,0 % \| 28,3 % [0,0 % ; 100,0 %] |
| B-cũ | R TB | 0,00 \| 0,16 [-0,68 ; 1,33] | 0,04 \| 0,37 [-1,10 ; 2,91] | -0,07 \| 0,04 [-1,10 ; 2,88] | -0,11 \| -0,03 [-1,12 ; 2,92] | -0,41 \| 0,51 [-1,09 ; 2,92] | 2,94 \| 0,03 [-1,12 ; 2,92] |
| B-v2 | n | 25 \| 19 [13 ; 26] | 12 \| 10 [5 ; 14] | 13 \| 10 [5 ; 15] | 7 \| 7 [3 ; 11] | 8 \| 7 [3 ; 11] | 10 \| 6 [2 ; 11] |
| B-v2 | WR | 32,0 % \| 27,1 % [14,3 % ; 42,9 %] | 25,0 % \| 28,1 % [9,1 % ; 55,6 %] | 38,5 % \| 26,8 % [0,0 % ; 57,1 %] | 14,3 % \| 21,5 % [0,0 % ; 50,4 %] | 25,0 % \| 36,5 % [0,0 % ; 66,7 %] | 50,0 % \| 23,5 % [0,0 % ; 60,3 %] |
| B-v2 | R TB | 0,19 \| -0,00 [-0,52 ; 0,63] | -0,09 \| 0,04 [-0,73 ; 1,13] | 0,45 \| -0,02 [-1,08 ; 1,20] | -0,53 \| -0,23 [-1,09 ; 0,94] | -0,08 \| 0,38 [-1,07 ; 1,58] | 0,91 \| -0,15 [-1,11 ; 1,32] |
| chỉ-v2 | n | 14 \| 12 [7 ; 18] | 5 \| 6 [2 ; 9] | 9 \| 6 [2 ; 10] | 3 \| 4 [1 ; 7] | 2 \| 4 [2 ; 7] | 9 \| 4 [1 ; 7] |
| chỉ-v2 | WR | 35,7 % \| 25,1 % [6,6 % ; 46,8 %] | 20,0 % \| 25,4 % [0,0 % ; 50,5 %] | 44,4 % \| 25,9 % [0,0 % ; 55,8 %] | 0,0 % \| 19,2 % [0,0 % ; 66,7 %] | 50,0 % \| 32,7 % [0,0 % ; 73,0 %] | 44,4 % \| 22,0 % [0,0 % ; 60,0 %] |
| chỉ-v2 | R TB | 0,34 \| -0,09 [-0,83 ; 0,78] | -0,29 \| -0,07 [-1,09 ; 0,96] | 0,68 \| -0,05 [-1,10 ; 1,14] | -1,09 \| -0,32 [-1,11 ; 1,58] | 0,92 \| 0,22 [-1,10 ; 1,83] | 0,68 \| -0,21 [-1,11 ; 1,30] |

### Phán quyết theo ngưỡng — 15 phép so (R TB)

| # | phép so | n TRAIN / TEST | phán quyết |
|---|---|---|---|
| 1 | B-v2 vs ĐC1 (dời) | 12 / 13 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |
| 2 | B-v2 vs ĐC2 (ngẫu nhiên tại mức) | 12 / 13 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |
| 3 | chỉ-v2 vs ĐC2 | 5 / 9 | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| 4 | B-cũ + POC_D vs ĐC1 (dời, cùng cấu hình) | 10 / 4 | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| 5 | B-cũ + VAH_D vs ĐC1 (dời, cùng cấu hình) | 8 / 9 | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| 6 | B-cũ + VAL_D vs ĐC1 (dời, cùng cấu hình) | 8 / 4 | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| 7 | B-cũ + HVN_D vs ĐC1 (dời, cùng cấu hình) | 8 / 5 | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| 8 | B-cũ + HVN_W vs ĐC1 (dời, cùng cấu hình) | 7 / 7 | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| 9 | B-cũ + POC_W vs ĐC1 (dời, cùng cấu hình) | 7 / 4 | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| 10 | B-v2 − POC_D vs ĐC1 (dời, cùng cấu hình) | 10 / 13 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |
| 11 | B-v2 − VAH_D vs ĐC1 (dời, cùng cấu hình) | 11 / 8 | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| 12 | B-v2 − VAL_D vs ĐC1 (dời, cùng cấu hình) | 11 / 13 | ≈ đối chứng (trong dải 5–95%; < 2/3 tháng cùng dấu; \|hiệu\| ≤ 2 sai số) |
| 13 | B-v2 − HVN_D vs ĐC1 (dời, cùng cấu hình) | 12 / 12 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |
| 14 | B-v2 − HVN_W vs ĐC1 (dời, cùng cấu hình) | 12 / 10 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |
| 15 | B-v2 − POC_W vs ĐC1 (dời, cùng cấu hình) | 12 / 13 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |

Số ô "KHÁC đối chứng": **0 / 15** (ở mức 5 % kỳ vọng ~0,75 ô do ngẫu nhiên; một ô lẻ không phải bằng chứng).

Tham khảo (không tính vào 15 phép so): B-cũ vs ĐC2 = không áp dụng (n < 10 ở TRAIN hoặc TEST); chỉ-v2 vs ĐC1 (nhóm chỉ-v2 dời) = không áp dụng (n < 10 ở TRAIN hoặc TEST).

### ĐC2 chi tiết (`R TB thật | TB đối chứng [5 % ; 95 %]`, WR đối chứng TB)

| nhóm | GỘP | TRAIN | TEST | WR thật / WR đối chứng (GỘP) |
|---|---|---|---|---|
| B-cũ | 0,00 \| 0,00 [-1,10 ; 1,13] | 0,04 \| 0,01 [-1,13 ; 1,31] | -0,07 \| -0,05 [-1,15 ; 1,61] | 27,3 % / 27,8 % |
| B-v2 | 0,19 \| 0,06 [-0,53 ; 0,70] | -0,09 \| -0,03 [-0,78 ; 0,72] | 0,45 \| 0,14 [-0,73 ; 1,09] | 32,0 % / 29,1 % |
| chỉ-v2 | 0,34 \| 0,08 [-0,76 ; 1,04] | -0,29 \| -0,09 [-1,12 ; 1,31] | 0,68 \| 0,17 [-1,11 ; 1,19] | 35,7 % / 29,4 % |

## 6. Phán quyết theo tiêu chí đăng ký trước (plan 3.5)

| tiêu chí | điều kiện | kết quả |
|---|---|---|
| 1. "Chỉ tăng số lượng" | n(B-v2)=25 > n(B-cũ)=11; B-v2 trong dải ĐC1 về WR **và** R TB ở TRAIN (ĐẠT) hoặc TEST (ĐẠT); hoặc chỉ-v2 WR 35,7 % ≤ 27 % + 1 sai số (39,8 %) | **ĐẠT** |
| 2. "Tệ đi" | chỉ-v2 (n TRAIN 5 / TEST 9, cần ≥ 10) R TB < mốc 5 % ĐC1 (nhóm chỉ-v2 dời) hoặc < ĐC2 − 2 sai số ở CẢ hai nửa: không áp dụng (n nhỏ); hoặc mất ≥ 3 lệnh cũ thắng do chặn (mất 0 lệnh thắng) | **không** |
| 3. "Cải thiện thật" | (a) n ≥ 30, ≥ 10 mỗi nửa: không · (b) R TB > 0 cả TRAIN (-0,09) và TEST (0,45): không · (c) chỉ-v2 WR ≥ WR B-cũ và R TB > 0 cả hai nửa: không · (d) vượt ĐC1 và ĐC2: không · (e) không loại vùng kéo xuống: ĐẠT | **không** |

**Kết luận (theo thứ tự kiểm 1 → 2 → 3): CHỈ TĂNG SỐ LƯỢNG.**

*"Vùng mới cho thêm lệnh nhưng không cho thêm lợi thế đo được; B v2 ≈ B cũ chạy ở nhiều chỗ hơn."*

Không đạt 3.5-3(d) ⇒ **chưa có lợi thế đo được trên 61 phiên**. Với 61 phiên, (d) gần như chỉ đạt khi hiệu ≥ ~0,6R.

**So với kỳ vọng đăng ký trước:** n = 25 (kỳ vọng 20–60: trong; tăng 2,3× so với B cũ); WR 32,0 % (kỳ vọng 25–35 %: trong); B-v2 nằm trong dải ĐC1.

**Đọc kết quả cho đúng:** mọi con số theo từng loại vùng ở mục 3–4 (vd "B-mới-thôi", "B-cũ + HVN_W", nhóm chỉ-v2 TEST) dựa trên vài lệnh, KTC 95 % của R TB đều chứa 0 và mọi phép so có phán quyết đều "≈ đối chứng" hoặc "không áp dụng" ⇒ **không được đọc thành "vùng X tốt hơn"**. R TB dương của B-v2 đến từ TEST (TRAIN âm) — hai nửa ngược dấu, đúng kiểu nhiễu.

## 7. Phụ lục — độ nhạy θ × N của B-v2 (CHỈ in, không chọn lại ô)

`n · WR · R TB` toàn bộ.

| θ \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0,3 | 89 · 27,0 % · -0,01 | 44 · 29,5 % · 0,09 | 26 · 19,2 % · -0,32 |
| 0,5 | 54 · 27,8 % · 0,02 | 25 · 32,0 % · 0,19 | 10 · 40,0 % · 0,52 |
| 0,7 | 39 · 28,2 % · 0,05 | 21 · 33,3 % · 0,24 | 9 · 33,3 % · 0,25 |

## 8. Ví dụ để soi chart — nhóm chỉ-v2 (5 thắng + 5 thua, chọn cách đều theo thời gian)

| UTC | VN | chiều | loại vùng | Z | zones_hit | move (giá) | \|Δ_CF\| / max | entry | SL | TP | kết quả | R | ảnh |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-01 07:05 | 2026-09-01 14:05 | SELL | POC_D | 4483,2 | POC_D | 6,5 | 0,87 | 4481,0 | 4484,5 | 4470,5 | TP | 2,94 | [ảnh](img/b_v2_POC_D_2026-09-01_0705_TP.png) |
| 2026-10-08 09:05 | 2026-10-08 16:05 | SELL | VAH_D | 4155,2 | VAH_D | 8,1 | 1,07 | 4152,3 | 4155,5 | 4142,7 | TP | 2,94 | [ảnh](img/b_v2_VAH_D_2026-10-08_0905_TP.png) |
| 2026-10-12 04:18 | 2026-10-12 11:18 | SELL | VAH_D | 4225,2 | VAH_D | 3,2 | 2,70 | 4223,8 | 4226,1 | 4216,9 | TP | 2,91 | [ảnh](img/b_v2_VAH_D_2026-10-12_0418_TP.png) |
| 2026-10-14 04:55 | 2026-10-14 11:55 | SELL | HVN_W | 4190,2 | HVN_W1 | 5,7 | 0,89 | 4189,4 | 4190,7 | 4185,5 | TP | 2,85 | [ảnh](img/b_v2_HVN_W_2026-10-14_0455_TP.png) |
| 2026-10-16 06:17 | 2026-10-16 13:17 | BUY | HVN_W | 4190,2 | HVN_W1 | 8,1 | 1,55 | 4192,2 | 4189,4 | 4200,6 | TP | 2,93 | [ảnh](img/b_v2_HVN_W_2026-10-16_0617_TP.png) |
| 2026-08-10 11:38 | 2026-08-10 18:38 | BUY | POC_D | 4395,2 | POC_D, HVN_D2 | 3,2 | 1,00 | 4397,6 | 4394,6 | 4406,6 | SL | -1,07 | [ảnh](img/b_v2_POC_D_2026-08-10_1138_SL.png) |
| 2026-08-20 09:29 | 2026-08-20 16:29 | BUY | POC_D | 4545,2 | POC_D | 5,8 | 1,48 | 4546,8 | 4544,5 | 4553,7 | SL | -1,09 | [ảnh](img/b_v2_POC_D_2026-08-20_0929_SL.png) |
| 2026-10-08 04:44 | 2026-10-08 11:44 | BUY | VAH_D | 4155,2 | VAH_D | 4,8 | 0,56 | 4156,4 | 4154,4 | 4162,4 | SL | -1,10 | [ảnh](img/b_v2_VAH_D_2026-10-08_0444_SL.png) |
| 2026-10-13 08:40 | 2026-10-13 15:40 | BUY | VAH_D | 4211,6 | VAH_D | 6,3 | 1,28 | 4213,1 | 4211,1 | 4219,1 | SL | -1,10 | [ảnh](img/b_v2_VAH_D_2026-10-13_0840_SL.png) |
| 2026-10-21 11:49 | 2026-10-21 18:49 | BUY | VAH_D | 4155,6 | VAH_D | 4,3 | 0,59 | 4157,2 | 4154,9 | 4164,1 | SL | -1,09 | [ảnh](img/b_v2_VAH_D_2026-10-21_1149_SL.png) |

## 9. Rủi ro / điểm mơ hồ (plan mục 5) — báo lại

- Thứ tự ưu tiên VWAP-trước làm "vùng thắng" nghiêng về VWAP khi trùng — vì vậy in cả "bất kỳ vùng" và bỏ-một.
- Bộ lọc `trend_bad`/`edge_bad` dùng band VA Âu/IB cho mọi vùng; pha A chế độ NA nên không lọc được (như B cũ). Không thêm lọc.
- Biến thể "đang hình thành" (POC/VAH/VAL_D_DEV) **không làm** trong vòng này.
- Không gặp ca chưa phủ (mức NaN giữa phiên: không có vì mức cố định cả phiên; hai mức cùng loại cùng giá: không thể vì HVN cách nhau ≥ 2 giá).
- C# (`BenzoDetectors.cs` / `BenzoTrader.cs`) **không đụng** — chỉ port khi đạt 3.5-3 và được duyệt số.

(Thời gian chạy: 163 giây.)
