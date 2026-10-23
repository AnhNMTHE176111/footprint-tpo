# RESULTS-B-v3 — Setup B "Hấp thụ" thêm vùng hỗ trợ / kháng cự (đỉnh/đáy phiên trước + Vùng Canh Lệnh v5) vào 8 loại vùng của B-v2

Sinh bởi `setup_b_v3.py` (deterministic) theo `plans/BENZO-B-v3-plan.md`. **Chỉ file 90d GCZ26** `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (một hợp đồng, `splice_jump.any() == False` ✔), 86333 nến M1, 61 phiên sạch (TRAIN 35 ≤ 2026-09-15, TEST 26). Giờ UTC (VN = UTC+7). Cấu hình duy nhất: θ 0,5 · N 3 · TP 3R · mono "ends" · biến thể "base" · không bias · mọi pha trừ OFF. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ SL; 1 lệnh mở cùng lúc; tối đa 2 lệnh / (loại vùng, phiên). Cache VCL v5: md5 `b528a60c642bcd934039efaa8150ddf1` (căn hàng `check_align` ✔; 7 khe; 4262 eid).

## 0. Kỳ vọng đăng ký TRƯỚC khi chạy (plan 3.6, chép từ hằng số đã commit c0885f5)

- n(B-v3): 25 → **40–100** (cạnh VCL bị chạm ~33 000 cặp (nến, vùng) mỗi vai trên 90d so với ~20 000 lượt chạm của 12 mức v2; trần 2/phiên chặn trên ở ~122 lệnh VCL; PDHL đóng góp 0–5 lệnh). n không tăng ≥ 1,6× ⇒ bộ lọc cụm/θ/chế độ là nút thắt, không phải vùng.
- WR ở 3R: **24–33 %**, trôi về hoà vốn ~27 %. **B-v3 ≈ dải ĐC1; lệnh chỉ-v3 ≈ ĐC2** (ba lần đo S/R trước — SR-KET-QUA, HVN 474 phiên, VCL 5 vòng — đều ra như vậy: vị trí vùng không mang thông tin, xác suất chạm chỉ phụ thuộc khoảng cách).
- Không ép: không chọn ô độ nhạy đẹp; không chọn biến thể "tâm"; TP 2R không chạy; không thêm bộ lọc giữa chừng.

Tái tạo mốc (điều kiện tiên quyết): B cũ n = 11, WR 27,3 %, R TB 0,00, idx khớp `_b_old_idx.json` ✔; B v2 n = 25, WR 32,0 %, R TB 0,19, danh sách [idx, chiều, entry, SL, TP, vùng] khớp `_b_v2_idx.json` (ghi từ code CHƯA sửa) ✔.

## 1. Tập vùng S/R — có mặt, khoảng cách, trùng với vùng v2

| mức | số nến đo được chạm mức (ấm, \|close − Z\| ≤ 1 hoặc râu chạm) | trung vị \|close − Z\| (giá) |
|---|---|---|
| POC_D | 2867 | 23,0 |
| VAH_D | 2361 | 28,4 |
| VAL_D | 2366 | 27,7 |
| HVN_D1 | 1779 | 23,3 |
| HVN_D2 | 704 | 23,5 |
| HVN_D3 | 283 | 19,1 |
| POC_W | 524 | 72,6 |
| HVN_W1 | 709 | 91,4 |
| HVN_W2 | 258 | 236,8 |
| HVN_W3 | 271 | 263,4 |
| PDH | 1286 | 45,9 |
| PDL | 1306 | 42,0 |
| VCL_R1 | 3330 | 31,1 |
| VCL_R2 | 4633 | 13,7 |
| VCL_R3 | 5332 | 10,3 |
| VCL_R4 | 5659 | 9,9 |
| VCL_R5 | 4958 | 10,0 |
| VCL_R6 | 3684 | 14,7 |
| VCL_R7 | 3344 | 15,5 |
| VCL_S1 | 3282 | 29,1 |
| VCL_S2 | 4294 | 13,5 |
| VCL_S3 | 5374 | 10,1 |
| VCL_S4 | 5238 | 9,9 |
| VCL_S5 | 4954 | 10,1 |
| VCL_S6 | 3831 | 15,1 |
| VCL_S7 | 3449 | 16,1 |

- VCL: 4262 eid, đồng thời tối đa 7 (khe cần 7 ≤ 7 ✔); tuổi thọ trung vị 60 nến; độ rộng trung vị 2,25 giá; cạnh `lo` trôi trong cùng eid: trung vị 0,00, p90 0,02 giá/nến.
- PDH/PDL: có ở 61 / 61 phiên sạch (phiên đầu file không có phiên trước). Phiên 2026-07-29 dựng trên phiên thin 07-28 — như VAH/VAL/POC v2, ghi chú, không sửa kernel.
- Trùng với mức v2 (mô tả, không lọc): tỉ lệ nến chạm cạnh VCL (ấm) mà cũng nằm ≤ 1 giá từ một mức v2 = **17,0 %** (49284 nến chạm); với 33 lệnh thô VCL/PDHL: |Z − mức v2 gần nhất| trung vị 3,2 giá (p25 1,4, p75 6,7).

## 2. Công suất thống kê (in TRƯỚC bảng chính — plan 3.3)

- Sai số WR ≈ √(p(1−p)/n), p = 0,27: n = 25 ⇒ ±8,9 điểm; n = 58 ⇒ ±5,8 điểm.
- Chênh WR nhỏ nhất phát hiện được (80 %, hai phía) giữa B-v2 (n=25) và B-v3 (n=58): ≈ **30 điểm**; chênh R TB nhỏ nhất ≈ **1,16R** (σ_R = 1,73). *So WR v2 ↔ v3 trực tiếp gần như vô nghĩa; phán quyết dựa vào đối chứng và nhóm lệnh chỉ-v3.*

## 3. Bảng chính — 16 cấu hình (plan 3.1)

n = lệnh đã đóng; lệnh/ngày chia 61 phiên sạch; KTC = khoảng tin cậy 95 % bootstrap (10 000, seed 0) của R TB. Hàng 1–3 liền nhau, WR in đậm.

| cấu hình | n | lệnh/ngày | **WR** | R TB | KTC 95 % | kỳ vọng giá/lệnh | tổng R | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| B-cũ | 11 | 0,18 | **27,3 %** | 0,00 | [-1,07 ; 1,10] | 0,07 | 0,0 | 4 |
| B-v2 | 25 | 0,41 | **32,0 %** | 0,19 | [-0,46 ; 0,99] | 0,73 | 4,7 | 5 |
| B-v3 | 58 | 0,95 | **24,1 %** | -0,12 | [-0,54 ; 0,36] | -0,25 | -7,2 | 10 |
| | | | | | | | | |
| Chỉ-S/R | 34 | 0,56 | **17,6 %** | -0,38 | [-0,85 ; 0,20] | -1,01 | -13,0 | 12 |
| Chỉ-VCL | 34 | 0,56 | **17,6 %** | -0,38 | [-0,85 ; 0,20] | -1,01 | -13,0 | 12 |
| Chỉ-PDHL | 0 | 0,00 | **–** | – | [– ; –] | – | 0,0 | 0 |
| B-v2 + VCL | 58 | 0,95 | **24,1 %** | -0,12 | [-0,54 ; 0,36] | -0,25 | -7,2 | 10 |
| B-v2 + PDHL | 25 | 0,41 | **32,0 %** | 0,19 | [-0,46 ; 0,99] | 0,73 | 4,7 | 5 |
| B-v3 − VWAP_W | 57 | 0,93 | **24,6 %** | -0,11 | [-0,53 ; 0,32] | -0,21 | -6,1 | 10 |
| B-v3 − VWAP_D | 51 | 0,84 | **25,5 %** | -0,07 | [-0,54 ; 0,40] | -0,14 | -3,6 | 9 |
| B-v3 − POC_D | 56 | 0,92 | **23,2 %** | -0,16 | [-0,59 ; 0,33] | -0,39 | -9,0 | 10 |
| B-v3 − VAH_D | 52 | 0,85 | **23,1 %** | -0,17 | [-0,62 ; 0,30] | -0,41 | -8,6 | 10 |
| B-v3 − VAL_D | 57 | 0,93 | **24,6 %** | -0,11 | [-0,53 ; 0,32] | -0,21 | -6,1 | 10 |
| B-v3 − HVN_D | 58 | 0,95 | **24,1 %** | -0,12 | [-0,54 ; 0,36] | -0,25 | -7,2 | 10 |
| B-v3 − HVN_W | 55 | 0,90 | **21,8 %** | -0,22 | [-0,65 ; 0,22] | -0,44 | -11,9 | 10 |
| B-v3 − POC_W | 58 | 0,95 | **24,1 %** | -0,12 | [-0,54 ; 0,36] | -0,25 | -7,2 | 10 |

Theo nửa và tháng (`n · WR · R TB`; T8 gồm 29–31/7):

| cấu hình | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| B-cũ | 7 · 28,6 % · 0,04 | 4 · 25,0 % · -0,07 | 4 · 25,0 % · -0,11 | 6 · 16,7 % · -0,41 | 1 · 100,0 % · 2,94 |
| B-v2 | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,45 | 7 · 14,3 % · -0,53 | 8 · 25,0 % · -0,08 | 10 · 50,0 % · 0,91 |
| B-v3 | 32 · 18,8 % · -0,34 | 26 · 30,8 % · 0,14 | 24 · 12,5 % · -0,59 | 15 · 26,7 % · -0,01 | 19 · 36,8 % · 0,38 |
| Chỉ-S/R | 20 · 15,0 % · -0,49 | 14 · 21,4 % · -0,23 | 17 · 11,8 % · -0,61 | 7 · 28,6 % · 0,07 | 10 · 20,0 % · -0,30 |
| Chỉ-VCL | 20 · 15,0 % · -0,49 | 14 · 21,4 % · -0,23 | 17 · 11,8 % · -0,61 | 7 · 28,6 % · 0,07 | 10 · 20,0 % · -0,30 |
| Chỉ-PDHL | 0 · – · – | 0 · – · – | 0 · – · – | 0 · – · – | 0 · – · – |
| B-v2 + VCL | 32 · 18,8 % · -0,34 | 26 · 30,8 % · 0,14 | 24 · 12,5 % · -0,59 | 15 · 26,7 % · -0,01 | 19 · 36,8 % · 0,38 |
| B-v2 + PDHL | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,45 | 7 · 14,3 % · -0,53 | 8 · 25,0 % · -0,08 | 10 · 50,0 % · 0,91 |
| B-v3 − VWAP_W | 31 · 19,4 % · -0,32 | 26 · 30,8 % · 0,14 | 24 · 12,5 % · -0,59 | 14 · 28,6 % · 0,06 | 19 · 36,8 % · 0,38 |
| B-v3 − VWAP_D | 28 · 21,4 % · -0,23 | 23 · 30,4 % · 0,12 | 21 · 14,3 % · -0,51 | 12 · 33,3 % · 0,25 | 18 · 33,3 % · 0,24 |
| B-v3 − POC_D | 30 · 16,7 % · -0,42 | 26 · 30,8 % · 0,14 | 23 · 13,0 % · -0,57 | 14 · 21,4 % · -0,22 | 19 · 36,8 % · 0,38 |
| B-v3 − VAH_D | 31 · 19,4 % · -0,31 | 21 · 28,6 % · 0,05 | 23 · 13,0 % · -0,57 | 15 · 26,7 % · -0,01 | 14 · 35,7 % · 0,33 |
| B-v3 − VAL_D | 31 · 19,4 % · -0,31 | 26 · 30,8 % · 0,14 | 24 · 12,5 % · -0,59 | 14 · 28,6 % · 0,07 | 19 · 36,8 % · 0,38 |
| B-v3 − HVN_D | 32 · 18,8 % · -0,34 | 26 · 30,8 % · 0,14 | 24 · 12,5 % · -0,59 | 15 · 26,7 % · -0,01 | 19 · 36,8 % · 0,38 |
| B-v3 − HVN_W | 32 · 18,8 % · -0,34 | 23 · 26,1 % · -0,04 | 24 · 12,5 % · -0,59 | 15 · 26,7 % · -0,01 | 16 · 31,2 % · 0,16 |
| B-v3 − POC_W | 32 · 18,8 % · -0,34 | 26 · 30,8 % · 0,14 | 24 · 12,5 % · -0,59 | 15 · 26,7 % · -0,01 | 19 · 36,8 % · 0,38 |

Theo pha và chiều (`n · WR · R TB`):

| cấu hình | A | EU | US | BUY | SELL |
|---|---|---|---|---|---|
| B-cũ | 8 · 25,0 % · -0,09 | 2 · 0,0 % · -1,07 | 1 · 100,0 % · 2,90 | 4 · 50,0 % · 0,92 | 7 · 14,3 % · -0,53 |
| B-v2 | 13 · 30,8 % · 0,13 | 10 · 30,0 % · 0,12 | 2 · 50,0 % · 0,90 | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,44 |
| B-v3 | 28 · 17,9 % · -0,37 | 20 · 30,0 % · 0,11 | 10 · 30,0 % · 0,10 | 27 · 18,5 % · -0,35 | 31 · 29,0 % · 0,08 |
| Chỉ-S/R | 15 · 6,7 % · -0,81 | 11 · 27,3 % · -0,01 | 8 · 25,0 % · -0,10 | 15 · 13,3 % · -0,57 | 19 · 21,1 % · -0,24 |
| Chỉ-VCL | 15 · 6,7 % · -0,81 | 11 · 27,3 % · -0,01 | 8 · 25,0 % · -0,10 | 15 · 13,3 % · -0,57 | 19 · 21,1 % · -0,24 |
| Chỉ-PDHL | 0 · – · – | 0 · – · – | 0 · – · – | 0 · – · – | 0 · – · – |
| B-v2 + VCL | 28 · 17,9 % · -0,37 | 20 · 30,0 % · 0,11 | 10 · 30,0 % · 0,10 | 27 · 18,5 % · -0,35 | 31 · 29,0 % · 0,08 |
| B-v2 + PDHL | 13 · 30,8 % · 0,13 | 10 · 30,0 % · 0,12 | 2 · 50,0 % · 0,90 | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,44 |
| B-v3 − VWAP_W | 28 · 17,9 % · -0,37 | 19 · 31,6 % · 0,17 | 10 · 30,0 % · 0,10 | 26 · 19,2 % · -0,32 | 31 · 29,0 % · 0,08 |
| B-v3 − VWAP_D | 22 · 18,2 % · -0,36 | 19 · 31,6 % · 0,17 | 10 · 30,0 % · 0,10 | 25 · 16,0 % · -0,46 | 26 · 34,6 % · 0,30 |
| B-v3 − POC_D | 28 · 17,9 % · -0,37 | 18 · 27,8 % · 0,02 | 10 · 30,0 % · 0,10 | 26 · 19,2 % · -0,32 | 30 · 26,7 % · -0,02 |
| B-v3 − VAH_D | 25 · 16,0 % · -0,44 | 17 · 29,4 % · 0,09 | 10 · 30,0 % · 0,10 | 23 · 21,7 % · -0,22 | 29 · 24,1 % · -0,12 |
| B-v3 − VAL_D | 27 · 18,5 % · -0,34 | 20 · 30,0 % · 0,11 | 10 · 30,0 % · 0,10 | 27 · 18,5 % · -0,35 | 30 · 30,0 % · 0,12 |
| B-v3 − HVN_D | 28 · 17,9 % · -0,37 | 20 · 30,0 % · 0,11 | 10 · 30,0 % · 0,10 | 27 · 18,5 % · -0,35 | 31 · 29,0 % · 0,08 |
| B-v3 − HVN_W | 27 · 14,8 % · -0,49 | 19 · 26,3 % · -0,04 | 9 · 33,3 % · 0,23 | 25 · 16,0 % · -0,45 | 30 · 26,7 % · -0,02 |
| B-v3 − POC_W | 28 · 17,9 % · -0,37 | 20 · 30,0 % · 0,11 | 10 · 30,0 % · 0,10 | 27 · 18,5 % · -0,35 | 31 · 29,0 % · 0,08 |

## 4. Tách đóng góp ở mức LỆNH (plan 3.2)

Chuỗi tập con kiểm bằng assert: lệnh thô B-cũ ⊆ B-v2 ⊆ B-v3, cùng chiều/entry/SL/TP/Z/vùng thắng ✔ (11 ⊆ 25 ⊆ 58 lệnh thô).

| nhóm | n · WR · R TB | KTC 95 % | TRAIN | TEST |
|---|---|---|---|---|
| Lệnh chung v2 ∩ v3 | 25 · 32,0 % · 0,19 | [-0,46 ; 0,99] | 12 · 25,0 % · -0,09 | 13 · 38,5 % · 0,45 |
| **Lệnh chỉ-v3** (nhóm quyết định) | 33 · 18,2 % · -0,36 | [-0,85 ; 0,24] | 20 · 15,0 % · -0,49 | 13 · 23,1 % · -0,17 |
| Lệnh v2 bị MẤT ở v3 (số liệu trong bản v2) | 0 · – · – | [– ; –] | 0 · – · – | 0 · – · – |

Lệnh v2 bị mất do `one_at_a_time` (lệnh vùng mới mở trước chặn): **0** lệnh, trong đó **0** lệnh thắng.

### Theo loại vùng (lệnh B-v3). Nhóm n < 10 chỉ để đọc số, không bình luận.

*Vùng thắng* = ztype ghi trên lệnh (thứ tự ưu tiên). *Bất kỳ vùng* = lệnh tính cho mọi loại có trong `zones_hit` (tổng > n). *Chỉ-v3* = nhóm lệnh chỉ-v3 theo vùng thắng / bất kỳ vùng.

| loại | vùng thắng: n · WR · R TB | bất kỳ vùng: n · WR · R TB | chỉ-v3, vùng thắng | chỉ-v3, bất kỳ vùng |
|---|---|---|---|---|
| VWAP_W | 3 · 33,3 % · 0,24 | 3 · 33,3 % · 0,24 | 0 · – · – | 0 · – · – |
| VWAP_D | 8 · 25,0 % · -0,09 | 10 · 30,0 % · 0,11 | 0 · – · – | 0 · – · – |
| POC_D | 3 · 33,3 % · 0,26 | 3 · 33,3 % · 0,26 | 0 · – · – | 0 · – · – |
| VAH_D | 6 · 33,3 % · 0,24 | 6 · 33,3 % · 0,24 | 0 · – · – | 0 · – · – |
| VAL_D | 1 · 0,0 % · -1,11 | 1 · 0,0 % · -1,11 | 0 · – · – | 0 · – · – |
| HVN_D | 1 · 0,0 % · -1,12 | 3 · 33,3 % · 0,24 | 0 · – · – | 0 · – · – |
| HVN_W | 3 · 66,7 % · 1,56 | 3 · 66,7 % · 1,56 | 0 · – · – | 0 · – · – |
| POC_W | 0 · – · – | 0 · – · – | 0 · – · – | 0 · – · – |
| PDHL | 0 · – · – | 0 · – · – | 0 · – · – | 0 · – · – |
| VCL | 33 · 18,2 % · -0,36 | 34 · 17,6 % · -0,38 | 33 · 18,2 % · -0,36 | 33 · 18,2 % · -0,36 |

Phễu RIÊNG của PDH + PDL (hai chiều): 1 CF dung + cum cham Z: 434; 2 + than/delta giam dan: 130; 3 + cuc tri <= Z+0,5: 13; 4 + khong TREND/pha VA/nen lon nhat: 12; 5 + move >= 3 gia: 10. Số lệnh PDHL cuối cùng = 0.

### Lệnh VCL — mô tả (chỉ mô tả; n < 10 chỉ in số)

| nhóm lệnh VCL | n · WR · R TB |
|---|---|
| SELL tại cạnh dưới (VCL_R) | 18 · 22,2 % · -0,19 |
| BUY tại cạnh trên (VCL_S) | 15 · 13,3 % · -0,57 |
| khe loại K (gần) | 7 · 0,0 % · -1,09 |
| khe loại N (gần-trung) | 26 · 23,1 % · -0,16 |
| khe loại F (xa) | 0 · – · – |
| độ rộng ≤ 2,5 giá | 19 · 26,3 % · -0,04 |
| độ rộng > 2,5 giá | 14 · 7,1 % · -0,79 |

Nguồn trong `mask` của vùng VCL tại lệnh (số lệnh có nguồn đó): A=20, B=10, C=4, D=21, E=0.
Rủi ro 5.5 — cạnh trôi trong cụm: 0 / 33 lệnh VCL có \|Z(i−1) − Z(i−N)\| > 0,5 giá (0,0 %). Chỉ mô tả.

### Phễu lọc (số ứng viên qua từng bước, cộng mọi mức và hai chiều; chưa gồm trần 2 lệnh / one-at-a-time)

| bước | B-v2 | B-v3 |
|---|---|---|
| 1 CF dung + cum cham Z | 3849 | 9797 |
| 2 + than/delta giam dan | 1227 | 3137 |
| 3 + cuc tri <= Z+0,5 | 214 | 489 |
| 4 + khong TREND/pha VA/nen lon nhat | 196 | 428 |
| 5 + move >= 3 gia | 108 | 244 |
| 6 + \|delta_CF\| >= theta*max | 34 | 74 |
| 7 + risk() hop le (SL<=4 gia) | 29 | 64 |

Lệnh thô bị trần 2/(loại, phiên) cắt (trước one_at_a_time; chạy `detect` thêm một lần với trần = 10⁹ chỉ để đếm): tổng 59 → 58. Theo loại (không trần → có trần): VCL 34 → 33; VWAP_D 8 → 8; VAH_D 6 → 6; POC_D 3 → 3; VWAP_W 3 → 3; HVN_W 3 → 3; VAL_D 1 → 1; HVN_D 1 → 1.

## 5. Đối chứng (plan 3.4)

**ĐC1 — dời bản đồ vùng:** mọi mức của phiên (12 v2 + PDH/PDL + 14 cạnh VCL; VWAP động cộng hằng δ) dời cùng δ[phiên, bản], |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, 100 bản, seed 20261024 (ma trận y hệt BENZO-VCL / B-v2). `warm` và `mdirs` KHÔNG đổi (danh tính vùng, không phải vị trí). Chạy NGUYÊN `prepare` + `detect` + `simulate` ⇒ lệnh dời cũng chạm vùng (dời) ≤ 1 giá, cùng cơ chế move → cụm → nến xác nhận; chỉ VỊ TRÍ khác. Nhóm "chỉ-v3" dời = lệnh B-v3 dời mà idx không có trong lệnh thô B-v2 dời cùng bản. Bộ lọc chế độ / VA Âu / IB không dời.

⚠ **Bẫy n của ĐC1:** dời làm đổi phân bố khoảng cách vùng↔giá theo thời gian (VCL vốn chọn vùng SÁT giá), nên **số lệnh n của bản dời CHỈ để tham khảo, KHÔNG dùng phán quyết**; phán quyết chỉ trên WR và R TB mỗi lệnh (điều kiện theo chạm ⇒ khớp khoảng cách). Không diễn giải "n thật > n dời" thành "vùng thật hút giá".

**ĐC2 — vào ngẫu nhiên tại cùng loại mức:** `kernel.control_sample` (không sửa, qua `_patched_map`), mỗi lệnh thật rút 1 nến chạm ĐÚNG mức đó (lệnh VCL: `VCL_R_ANY`/`VCL_S_ANY` = chạm một cạnh kháng cự/hỗ trợ VCL ấm bất kỳ), cùng chế độ, cùng chiều, cùng R:R, SL = râu nến + 0,3; 200 lần.

**Ngưỡng "khác đối chứng"** (nguyên PLAN-LAN-CHAM mục 5, `benzo_vcl.verdict`): ngoài dải 5–95 % ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số ở cả hai; chỉ áp dụng khi nhóm có ≥ 10 lệnh ở CẢ TRAIN và TEST. Số phép so có phán quyết (đăng ký trước) = 9; ở mức 5 % kỳ vọng ~0,45 ô "vượt" do ngẫu nhiên.

### ĐC1 — thật vs dải bản dời (`thật | TB dời [5 % ; 95 %]`)

| nhóm | đo | GỘP | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|---|---|
| B-v2 | n (chỉ tham khảo) | 25 \| 19 [13 ; 26] | 12 \| 10 [5 ; 14] | 13 \| 10 [5 ; 15] | 7 \| 7 [3 ; 11] | 8 \| 7 [3 ; 11] | 10 \| 6 [2 ; 11] |
| B-v2 | WR | 32,0 % \| 27,1 % [14,3 % ; 42,9 %] | 25,0 % \| 28,1 % [9,1 % ; 55,6 %] | 38,5 % \| 26,8 % [0,0 % ; 57,1 %] | 14,3 % \| 21,5 % [0,0 % ; 50,4 %] | 25,0 % \| 36,5 % [0,0 % ; 66,7 %] | 50,0 % \| 23,5 % [0,0 % ; 60,3 %] |
| B-v2 | R TB | 0,19 \| -0,00 [-0,52 ; 0,63] | -0,09 \| 0,04 [-0,73 ; 1,13] | 0,45 \| -0,02 [-1,08 ; 1,20] | -0,53 \| -0,23 [-1,09 ; 0,94] | -0,08 \| 0,38 [-1,07 ; 1,58] | 0,91 \| -0,15 [-1,11 ; 1,32] |
| B-v3 | n (chỉ tham khảo) | 58 \| 47 [36 ; 55] | 32 \| 24 [17 ; 31] | 26 \| 23 [17 ; 30] | 24 \| 16 [11 ; 24] | 15 \| 16 [10 ; 23] | 19 \| 14 [9 ; 20] |
| B-v3 | WR | 24,1 % \| 26,0 % [17,0 % ; 35,9 %] | 18,8 % \| 25,4 % [11,1 % ; 41,0 %] | 30,8 % \| 26,6 % [9,5 % ; 42,3 %] | 12,5 % \| 19,7 % [5,9 % ; 36,5 %] | 26,7 % \| 33,7 % [17,4 % ; 50,1 %] | 36,8 % \| 24,3 % [7,1 % ; 44,5 %] |
| B-v3 | R TB | -0,12 \| -0,05 [-0,40 ; 0,35] | -0,34 \| -0,07 [-0,63 ; 0,54] | 0,14 \| -0,03 [-0,70 ; 0,60] | -0,59 \| -0,30 [-0,84 ; 0,38] | -0,01 \| 0,26 [-0,39 ; 0,93] | 0,38 \| -0,12 [-0,80 ; 0,70] |
| chỉ-v3 | n (chỉ tham khảo) | 33 \| 27 [21 ; 36] | 20 \| 14 [9 ; 20] | 13 \| 13 [9 ; 17] | 17 \| 10 [5 ; 15] | 7 \| 10 [5 ; 14] | 9 \| 8 [5 ; 12] |
| chỉ-v3 | WR | 18,2 % \| 25,0 % [13,0 % ; 39,2 %] | 15,0 % \| 23,7 % [7,6 % ; 42,9 %] | 23,1 % \| 25,9 % [0,0 % ; 50,2 %] | 11,8 % \| 18,7 % [0,0 % ; 40,2 %] | 28,6 % \| 31,8 % [9,5 % ; 60,3 %] | 22,2 % \| 24,9 % [0,0 % ; 60,0 %] |
| chỉ-v3 | R TB | -0,36 \| -0,09 [-0,56 ; 0,47] | -0,49 \| -0,14 [-0,79 ; 0,64] | -0,17 \| -0,05 [-1,08 ; 0,93] | -0,61 \| -0,34 [-1,07 ; 0,54] | 0,07 \| 0,18 [-0,71 ; 1,32] | -0,21 \| -0,10 [-1,10 ; 1,30] |
| Chỉ-S/R | n (chỉ tham khảo) | 34 \| 29 [22 ; 38] | 20 \| 15 [10 ; 21] | 14 \| 14 [9 ; 18] | 17 \| 10 [6 ; 15] | 7 \| 10 [5 ; 15] | 10 \| 8 [5 ; 12] |
| Chỉ-S/R | WR | 17,6 % \| 25,1 % [12,5 % ; 39,1 %] | 15,0 % \| 24,1 % [7,1 % ; 42,9 %] | 21,4 % \| 25,8 % [0,0 % ; 50,2 %] | 11,8 % \| 19,3 % [0,0 % ; 40,1 %] | 28,6 % \| 31,9 % [10,0 % ; 63,8 %] | 20,0 % \| 24,2 % [0,0 % ; 54,7 %] |
| Chỉ-S/R | R TB | -0,38 \| -0,09 [-0,58 ; 0,47] | -0,49 \| -0,12 [-0,81 ; 0,63] | -0,23 \| -0,06 [-1,08 ; 0,93] | -0,61 \| -0,31 [-1,07 ; 0,53] | 0,07 \| 0,19 [-0,69 ; 1,46] | -0,30 \| -0,13 [-1,10 ; 1,09] |
| B-v2 + VCL | n (chỉ tham khảo) | 58 \| 44 [33 ; 52] | 32 \| 23 [16 ; 30] | 26 \| 21 [16 ; 28] | 24 \| 16 [10 ; 23] | 15 \| 15 [10 ; 22] | 19 \| 13 [8 ; 19] |
| B-v2 + VCL | WR | 24,1 % \| 26,3 % [17,3 % ; 37,5 %] | 18,8 % \| 26,1 % [12,0 % ; 42,9 %] | 30,8 % \| 26,7 % [10,0 % ; 43,8 %] | 12,5 % \| 20,3 % [5,9 % ; 38,5 %] | 26,7 % \| 34,3 % [16,7 % ; 53,5 %] | 36,8 % \| 23,8 % [7,6 % ; 44,5 %] |
| B-v2 + VCL | R TB | -0,12 \| -0,04 [-0,40 ; 0,42] | -0,34 \| -0,04 [-0,61 ; 0,63] | 0,14 \| -0,02 [-0,68 ; 0,66] | -0,59 \| -0,27 [-0,84 ; 0,45] | -0,01 \| 0,29 [-0,40 ; 1,06] | 0,38 \| -0,14 [-0,78 ; 0,70] |
| B-v2 + PDHL | n (chỉ tham khảo) | 25 \| 22 [15 ; 28] | 12 \| 11 [6 ; 16] | 13 \| 11 [6 ; 17] | 7 \| 7 [4 ; 12] | 8 \| 7 [4 ; 12] | 10 \| 7 [2 ; 12] |
| B-v2 + PDHL | WR | 32,0 % \| 26,6 % [13,0 % ; 42,1 %] | 25,0 % \| 26,4 % [7,1 % ; 50,0 %] | 38,5 % \| 26,9 % [0,0 % ; 55,6 %] | 14,3 % \| 19,8 % [0,0 % ; 50,0 %] | 25,0 % \| 34,7 % [9,5 % ; 61,8 %] | 50,0 % \| 24,6 % [0,0 % ; 50,4 %] |
| B-v2 + PDHL | R TB | 0,19 \| -0,02 [-0,57 ; 0,60] | -0,09 \| -0,03 [-0,79 ; 0,92] | 0,45 \| -0,02 [-1,07 ; 1,12] | -0,53 \| -0,29 [-1,09 ; 0,92] | -0,08 \| 0,30 [-0,69 ; 1,39] | 0,91 \| -0,11 [-1,10 ; 0,92] |

### Phán quyết theo ngưỡng — 9 phép so đăng ký trước (R TB)

| # | phép so | n TRAIN / TEST | phán quyết |
|---|---|---|---|
| 1 | B-v3 vs ĐC1 (dời) | 32 / 26 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |
| 2 | B-v3 vs ĐC2 (ngẫu nhiên tại loại mức) | 32 / 26 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; \|hiệu\| ≤ 2 sai số) |
| 3 | chỉ-v3 vs ĐC1 (nhóm chỉ-v3 dời) | 20 / 13 | ≈ đối chứng (trong dải 5–95%; \|hiệu\| ≤ 2 sai số) |
| 4 | chỉ-v3 vs ĐC2 | 20 / 13 | ≈ đối chứng (trong dải 5–95%; \|hiệu\| ≤ 2 sai số) |
| 5 | Chỉ-S/R vs ĐC1 | 20 / 14 | ≈ đối chứng (trong dải 5–95%; \|hiệu\| ≤ 2 sai số) |
| 6 | Chỉ-S/R vs ĐC2 | 20 / 14 | ≈ đối chứng (trong dải 5–95%; \|hiệu\| ≤ 2 sai số) |
| 7 | B-v2 + VCL vs ĐC1 | 32 / 26 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |
| 8 | B-v2 + PDHL vs ĐC1 | 12 / 13 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; \|hiệu\| ≤ 2 sai số) |
| 9 | B-v2 + VCL vs ĐC2 | 32 / 26 | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; \|hiệu\| ≤ 2 sai số) |

Số ô "KHÁC đối chứng": **0 / 9** (ở mức 5 % kỳ vọng ~0,45 ô do ngẫu nhiên; một ô lẻ không phải bằng chứng).

### ĐC2 chi tiết (`R TB thật | TB đối chứng [5 % ; 95 %]`; WR thật / WR đối chứng GỘP)

| nhóm | GỘP | TRAIN | TEST | WR thật / WR đối chứng (GỘP) |
|---|---|---|---|---|
| B-v3 | -0,12 \| -0,05 [-0,48 ; 0,34] | -0,34 \| -0,06 [-0,63 ; 0,51] | 0,14 \| -0,03 [-0,65 ; 0,57] | 24,1 % / 26,3 % |
| chỉ-v3 | -0,36 \| -0,09 [-0,59 ; 0,48] | -0,49 \| -0,11 [-0,66 ; 0,68] | -0,17 \| -0,06 [-0,80 ; 0,91] | 18,2 % / 25,2 % |
| Chỉ-S/R | -0,38 \| -0,09 [-0,54 ; 0,44] | -0,49 \| -0,11 [-0,66 ; 0,68] | -0,23 \| -0,07 [-0,76 ; 0,87] | 17,6 % / 25,2 % |
| B-v2 + VCL | -0,12 \| -0,05 [-0,48 ; 0,34] | -0,34 \| -0,06 [-0,63 ; 0,51] | 0,14 \| -0,03 [-0,65 ; 0,57] | 24,1 % / 26,3 % |

## 6. Phán quyết theo tiêu chí đăng ký trước (plan 3.5)

| tiêu chí | điều kiện | kết quả |
|---|---|---|
| 1. "Chỉ tăng số lượng" | n(B-v3)=58 > n(B-v2)=25; B-v3 trong dải ĐC1 về WR hoặc R TB ở TRAIN (ĐẠT) hoặc TEST (ĐẠT) [biến thể "và" chỉ tham khảo: TRAIN ĐẠT, TEST ĐẠT ⇒ ĐẠT]; hoặc chỉ-v3 WR 18,2 % ≤ 27 % + 1 sai số (33,7 %: ĐẠT) | **ĐẠT** |
| 2. "Tệ đi" | chỉ-v3 (n TRAIN 20 / TEST 13, cần ≥ 10) R TB < mốc 5 % ĐC1 hoặc < ĐC2 − 2 sai số ở CẢ hai nửa: không; hoặc mất ≥ 3 lệnh v2 thắng do chặn (mất 0 lệnh thắng) | **không** |
| 3. "Cải thiện thật" | (a) n ≥ 40, ≥ 10 mỗi nửa: ĐẠT · (b) R TB > 0 cả TRAIN (-0,34) và TEST (0,14): không · (c) chỉ-v3 WR ≥ WR B-v2 và R TB > 0 cả hai nửa: không · (d) B-v3 và chỉ-v3 vượt ĐC1 và ĐC2 (▲): không · (e) không loại vùng kéo xuống: ĐẠT | **không** |

**Kết luận (theo thứ tự kiểm 1 → 2 → 3): CHỈ TĂNG SỐ LƯỢNG.**

*"Vùng S/R cho thêm lệnh nhưng không cho thêm lợi thế đo được; B v3 ≈ B v2 chạy ở nhiều chỗ hơn."*

Không đạt 3.5-3(d) ⇒ **chưa có lợi thế đo được trên 61 phiên**. Với 61 phiên, (d) gần như chỉ đạt khi hiệu ≥ ~0,5R.

**So với kỳ vọng đăng ký trước:** n = 58 (kỳ vọng 40–100: trong; tăng 2,3× so với B v2, 5,3× so với B cũ); WR 24,1 % (kỳ vọng 24–33 %: trong); B-v3 nằm trong dải ĐC1 (R TB gộp).

**Đọc kết quả cho đúng:** các con số theo loại vùng (mục 3–4), theo nửa/tháng và nhóm chỉ-v3 dựa trên ít lệnh; KTC 95 % của R TB cần xem cột KTC trước khi nói "tốt hơn / tệ hơn". Không được viết "S/R của VCL giúp B tốt hơn" nếu không có ô "KHÁC đối chứng ▲" ở cả hai đối chứng.

## 7. Phụ lục — chỉ in, KHÔNG phán quyết, KHÔNG chọn (plan 3.7)

### 7.1 Độ nhạy θ × N của B-v3 (`n · WR · R TB`)

| θ \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0,3 | 183 · 26,8 % · -0,02 | 96 · 26,0 % · -0,05 | 57 · 22,8 % · -0,18 |
| 0,5 | 134 · 22,4 % · -0,19 | 58 · 24,1 % · -0,12 | 27 · 29,6 % · 0,10 |
| 0,7 | 99 · 26,3 % · -0,03 | 40 · 25,0 % · -0,09 | 20 · 35,0 % · 0,32 |

### 7.2 Biến thể "VCL tâm hai chiều" (v2 + VCL_M1..7, tâm = (lo+hi)/2)

| cấu hình | n · WR · R TB | TRAIN | TEST |
|---|---|---|---|
| B-v2 + VCL tâm | 58 · 37,9 % · 0,43 | 32 · 34,4 % · 0,29 | 26 · 42,3 % · 0,60 |

### 7.3 Lệnh chỉ-v3 theo pha

| pha | n · WR · R TB |
|---|---|
| A | 15 · 6,7 % · -0,81 |
| EU | 10 · 30,0 % · 0,10 |
| US | 8 · 25,0 % · -0,10 |

## 8. Ví dụ để soi chart — nhóm chỉ-v3 (5 thắng + 5 thua, cách đều theo thời gian)

| UTC | VN | chiều | loại vùng | Z | dải VCL [lo, hi] | zones_hit | move (giá) | \|Δ_CF\| / max | entry | SL | TP | kết quả | R | ảnh |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-18 06:43 | 2026-08-18 13:43 | BUY | VCL | 4452,2 | [4449,00, 4452,20] | VCL_S3 | 3,4 | 0,64 | 4453,3 | 4451,9 | 4457,5 | TP | 2,86 | [ảnh](img/b_v3_VCL_2026-08-18_0643_TP.png) |
| 2026-08-18 10:28 | 2026-08-18 17:28 | BUY | VCL | 4446,4 | [4444,40, 4446,40] | VCL_S4 | 6,1 | 2,11 | 4447,9 | 4445,7 | 4454,5 | TP | 2,91 | [ảnh](img/b_v3_VCL_2026-08-18_1028_TP.png) |
| 2026-09-04 20:57 | 2026-09-05 03:57 | SELL | VCL | 4479,0 | [4479,00, 4481,00] | VCL_R4 | 3,4 | 0,54 | 4477,1 | 4478,8 | 4472,0 | TP | 2,88 | [ảnh](img/b_v3_VCL_2026-09-04_2057_TP.png) |
| 2026-09-30 09:35 | 2026-09-30 16:35 | SELL | VCL | 4221,9 | [4221,90, 4223,90] | VCL_R4 | 7,6 | 1,62 | 4220,2 | 4222,6 | 4213,0 | TP | 2,92 | [ảnh](img/b_v3_VCL_2026-09-30_0935_TP.png) |
| 2026-10-19 15:29 | 2026-10-19 22:29 | SELL | VCL | 4169,0 | [4169,00, 4171,00] | VCL_R5 | 6,6 | 0,69 | 4168,3 | 4171,1 | 4159,9 | TP | 2,93 | [ảnh](img/b_v3_VCL_2026-10-19_1529_TP.png) |
| 2026-07-28 22:31 | 2026-07-29 05:31 | SELL | VCL | 4080,6 | [4080,60, 4082,60] | VCL_R5 | 4,6 | 3,00 | 4077,4 | 4080,8 | 4067,2 | SL | -1,06 | [ảnh](img/b_v3_VCL_2026-07-28_2231_SL.png) |
| 2026-08-10 02:24 | 2026-08-10 09:24 | SELL | VCL | 4388,2 | [4388,20, 4391,12] | VCL_R4 | 10,0 | 0,60 | 4387,0 | 4390,1 | 4377,7 | SL | -1,06 | [ảnh](img/b_v3_VCL_2026-08-10_0224_SL.png) |
| 2026-08-19 19:23 | 2026-08-20 02:23 | BUY | VCL | 4561,0 | [4559,00, 4561,00] | VCL_S6 | 3,2 | 0,68 | 4562,8 | 4560,5 | 4569,7 | SL | -1,09 | [ảnh](img/b_v3_VCL_2026-08-19_1923_SL.png) |
| 2026-09-28 10:47 | 2026-09-28 17:47 | SELL | VCL | 4189,1 | [4189,15, 4193,45] | VCL_R3 | 3,1 | 0,77 | 4187,4 | 4190,1 | 4179,3 | SL | -1,07 | [ảnh](img/b_v3_VCL_2026-09-28_1047_SL.png) |
| 2026-10-21 08:58 | 2026-10-21 15:58 | BUY | VCL | 4138,1 | [4134,80, 4138,10] | VCL_S6 | 3,6 | 1,05 | 4139,1 | 4137,3 | 4144,5 | SL | -1,11 | [ảnh](img/b_v3_VCL_2026-10-21_0858_SL.png) |

## 9. Rủi ro / điểm mơ hồ (plan mục 5) — báo lại

1. Kết quả ≈ đối chứng là khả năng cao nhất; câu kết luận bám 3.5-1, không viết "S/R của VCL giúp B tốt hơn".
2. VCL áp đảo nhóm chỉ-v3: số lệnh chỉ-v3 theo loại ở mục 4 (PDHL nhỏ ⇒ hàng "B-v2 + PDHL" dễ "không áp dụng").
3. Trần 2/(loại, phiên) chung cho 14 cạnh VCL cắt nhiều lệnh thô (số liệu ở mục 4); lệnh giữ = 2 lệnh SỚM nhất phiên. Luật đã chốt, không nới.
4. Bẫy n của ĐC1: chỉ phán quyết trên WR / R TB mỗi lệnh (mục 5).
5. Cạnh trôi trong eid: tỉ lệ lệnh VCL có cạnh trôi > 0,5 giá trong cụm in ở mục 4; chỉ mô tả.
6. Cache VCL = bản v5 trên 90d, md5 ghi ở đầu báo cáo (không phải chạy lại engine).
7. Không gặp ca chưa phủ: K_VCL = 7 ≤ 7, không eid nào xuất hiện lại sau khi biến mất (assert trong `vcl_slots`), căn hàng khớp, PDH/PDL cố định cả phiên.
8. Không chạy file 2 năm; C# (`BenzoDetectors.cs`) KHÔNG đụng — chỉ port khi đạt 3.5-3 và người học duyệt số.
9. Hai commit code/test đã làm tròn: code vùng + 12 test nằm trong commit 77486d8 (bị quét chung vào commit của tiến trình khác), hằng số đăng ký ở c0885f5.

(Thời gian chạy: 149 giây.)
