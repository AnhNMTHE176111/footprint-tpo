# Vùng Canh Lệnh — vòng 3 (chốt thiết kế + bảng tra)

Dữ liệu như vòng 1–2: `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` (28856 nến M1, UTC). Gộp 1,0u, đệm 0,5u, kẹp [1u, 4u].
TRAIN đo 13 phiên (2026-08-18 → 2026-09-03), TEST đo 7 phiên (2026-09-04 → 2026-09-14).
Vòng này **không tìm lợi thế**: 3 lần đo (SR-KET-QUA 65 phiên, VCL v1, VCL v2) đều cho vị trí vùng ≈ đối chứng. Các bảng dưới là **bảng mô tả** (tần suất lịch sử) để hiển thị cạnh vùng, không phải tín hiệu.
Thời gian chạy `vcl3.py`: 40 giây (engine v3 10s; còn lại = bảng tra + chạy lại engine v1, v2 để so vệ sinh).

### Vệ sinh chart — v1 / v2 / v3 (mục tiêu v3: đổi vùng ≤ 4/giờ, tuổi thọ trung vị ≥ 30 phút)

| Chỉ số | v1 TRAIN | v1 TEST | v2 TRAIN | v2 TEST | v3 TRAIN | v3 TEST |
|---|---|---|---|---|---|---|
| vùng hiển thị TB | 6.00 | 6.00 | 6.00 | 6.00 | 6.32 | 6.35 |
| rộng trung vị (u) | 2.36 | 2.46 | 1.00 | 1.30 | 1.00 | 1.25 |
| rộng trung vị (USD) | 3.80 | 3.80 | 2.30 | 2.30 | 2.20 | 2.30 |
| % nến đóng trong vùng hiển thị | 80.1 | 79.5 | 6.9 | 6.8 | 35.3 | 33.9 |
| vùng sống trong ±10u | 8.6 | 8.5 | 6.5 | 6.3 | 6.3 | 6.0 |
| đổi vùng / giờ | 17.1 | 17.7 | 12.4 | 12.1 | 6.0 | 5.2 |
| tuổi thọ trung vị vùng hiển thị (phút) | 4 | 4 | 11 | 12 | 20 | 30 |

Số lần tính lại bộ vùng v3: 2116 (≈ 1 lần / 14 nến). v2: "% trong vùng" thấp do luật gỡ vùng chứa giá; v3 giữ vùng chứa giá nên chỉ số này có nghĩa trở lại.

### 6. Bảng tra P(chạm cạnh gần) theo khoảng cách d × pha phiên

Mẫu: mỗi 5 nến, mỗi vùng đang hiển thị (trừ vùng đang chứa giá); cạnh gần đóng băng tại lúc lấy mẫu; chạm = high/low chạm cạnh gần trong W nến sau, chỉ trong phiên. Ô **đậm** = gộp TRAIN+TEST; (TRAIN/TEST, |Δ|). n < 40 ⇒ "—". Mẫu chồng lấn (cùng vùng lấy mẫu nhiều lần) ⇒ n hiệu dụng nhỏ hơn n ghi.

#### Mọi pha

| d (u) | n gộp | ≤15 nến: gộp (TRAIN/TEST, |Δ|) | ≤30 nến: gộp (TRAIN/TEST, |Δ|) | ≤60 nến: gộp (TRAIN/TEST, |Δ|) | ≤120 nến: gộp (TRAIN/TEST, |Δ|) |
|---|---|---|---|---|---|
| ≤1 | 2308 | **85** (85/85, 1) | **89** (89/90, 1) | **92** (92/93, 1) | **94** (94/95, 1) |
| 1–2 | 2478 | **59** (59/60, 1) | **71** (70/73, 3) | **78** (78/80, 2) | **83** (83/85, 2) |
| 2–3 | 2544 | **39** (40/39, 0) | **54** (53/54, 1) | **65** (65/66, 1) | **73** (74/73, 0) |
| 3–4 | 2513 | **23** (23/23, 0) | **39** (39/39, 0) | **52** (51/53, 2) | **62** (61/64, 3) |
| 4–6 | 4371 | **12** (12/13, 1) | **24** (24/24, 0) | **39** (39/39, 0) | **53** (52/53, 1) |
| 6–8 | 3018 | **6** (5/6, 1) | **13** (13/13, 0) | **27** (27/28, 1) | **43** (43/43, 0) |
| 8–12 | 3486 | **2** (2/2, 0) | **7** (7/6, 0) | **16** (16/15, 1) | **30** (29/32, 3) |

#### Pha Á (sm 0–450)

| d (u) | n gộp | ≤15 nến: gộp (TRAIN/TEST, |Δ|) | ≤30 nến: gộp (TRAIN/TEST, |Δ|) | ≤60 nến: gộp (TRAIN/TEST, |Δ|) | ≤120 nến: gộp (TRAIN/TEST, |Δ|) |
|---|---|---|---|---|---|
| ≤1 | 733 | **84** (84/84, 0) | **87** (87/88, 1) | **92** (92/93, 1) | **95** (94/95, 1) |
| 1–2 | 802 | **58** (59/57, 3) | **71** (70/73, 3) | **81** (81/83, 2) | **86** (85/89, 4) |
| 2–3 | 775 | **44** (46/41, 5) | **58** (59/55, 5) | **71** (71/69, 2) | **79** (80/77, 3) |
| 3–4 | 766 | **29** (31/26, 5) | **46** (46/44, 2) | **60** (61/59, 2) | **72** (72/72, 0) |
| 4–6 | 1384 | **16** (15/17, 2) | **31** (32/29, 3) | **47** (47/46, 1) | **62** (61/63, 2) |
| 6–8 | 1002 | **7** (7/6, 1) | **17** (18/14, 4) | **35** (36/32, 4) | **51** (53/48, 5) |
| 8–12 | 1164 | **3** (3/3, 0) | **10** (10/8, 2) | **23** (26/18, 7) | **42** (45/37, 7) |

#### Pha Âu (sm 450–840)

| d (u) | n gộp | ≤15 nến: gộp (TRAIN/TEST, |Δ|) | ≤30 nến: gộp (TRAIN/TEST, |Δ|) | ≤60 nến: gộp (TRAIN/TEST, |Δ|) | ≤120 nến: gộp (TRAIN/TEST, |Δ|) |
|---|---|---|---|---|---|
| ≤1 | 612 | **87** (89/84, 5) | **92** (93/91, 2) | **94** (94/93, 1) | **96** (96/95, 1) |
| 1–2 | 655 | **61** (59/64, 4) | **72** (72/73, 1) | **79** (79/79, 0) | **85** (84/86, 1) |
| 2–3 | 698 | **38** (37/39, 2) | **54** (52/57, 5) | **66** (64/70, 7) | **76** (74/79, 5) |
| 3–4 | 722 | **22** (23/21, 1) | **38** (38/37, 1) | **52** (50/55, 5) | **66** (64/69, 6) |
| 4–6 | 1239 | **11** (11/11, 0) | **22** (22/20, 2) | **38** (37/40, 3) | **55** (54/56, 2) |
| 6–8 | 915 | **4** (5/4, 0) | **11** (11/12, 1) | **25** (25/26, 2) | **43** (41/47, 7) |
| 8–12 | 1079 | **1** (1/1, 0) | **5** (6/5, 1) | **15** (15/14, 0) | **34** (29/42, 14) |

#### Pha Mỹ (sm 840–…)

| d (u) | n gộp | ≤15 nến: gộp (TRAIN/TEST, |Δ|) | ≤30 nến: gộp (TRAIN/TEST, |Δ|) | ≤60 nến: gộp (TRAIN/TEST, |Δ|) | ≤120 nến: gộp (TRAIN/TEST, |Δ|) |
|---|---|---|---|---|---|
| ≤1 | 963 | **83** (82/87, 5) | **89** (87/91, 4) | **91** (90/94, 4) | **93** (92/94, 2) |
| 1–2 | 1021 | **58** (58/59, 1) | **69** (68/72, 4) | **75** (75/77, 3) | **80** (80/81, 2) |
| 2–3 | 1071 | **37** (37/38, 2) | **51** (50/52, 2) | **61** (61/61, 0) | **68** (69/67, 2) |
| 3–4 | 1025 | **20** (18/23, 5) | **34** (33/36, 3) | **45** (44/47, 3) | **53** (52/54, 1) |
| 4–6 | 1748 | **10** (9/11, 2) | **20** (19/22, 3) | **32** (33/32, 0) | **44** (44/44, 1) |
| 6–8 | 1101 | **5** (4/8, 4) | **11** (10/14, 5) | **23** (20/27, 6) | **36** (36/35, 1) |
| 8–12 | 1243 | **2** (1/2, 1) | **5** (4/6, 3) | **9** (8/12, 5) | **16** (15/18, 2) |

### 7. P(bị quét) — sau khi giá đóng VÀO vùng từ ngoài, trong 10 nến râu vượt BIÊN XA thêm ≥ x·u (bảng đặt SL)

| Pha | n gộp (TRAIN/TEST) | ≥0,25u gộp (TR/TE) | ≥0,5u | ≥1,0u |
|---|---|---|---|---|
| Á | 1169 (789/380) | **66** (66/65) | **59** (59/58) | **47** (47/47) |
| Âu | 1004 (659/345) | **64** (64/63) | **58** (58/57) | **45** (44/45) |
| Mỹ | 1537 (1051/486) | **60** (62/57) | **53** (54/51) | **38** (38/39) |
| Mọi pha | 3710 | **63** (64/61) | **56** (57/55) | **43** (43/43) |

Đọc: đặt SL cách biên xa x·u thì bảng cho tỉ lệ bị râu chạm trong 10 nến đầu. Đây là mô tả, không phải lợi thế (v2: vùng giả cùng cỡ ≈ như nhau).

### 8. Kiểm chứng "chỉ khoảng cách": P(chạm) theo loại ứng viên trong vùng (mọi pha, gộp)

| d | Loại | n | ≤15 | ≤30 | ≤60 | ≤120 |
|---|---|---|---|---|---|---|
| 1–2 | mọi vùng | 2478 | 59 ±1 | 71 ±1 | 78 ±1 | 83 ±1 |
| 1–2 | B | 1271 | 60 ±1 | 73 ±1 | 80 ±1 | 85 ±1 |
| 1–2 | B15 | 833 | 59 ±2 | 73 ±2 | 80 ±1 | 85 ±1 |
| 1–2 | C | 497 | 60 ±2 | 74 ±2 | 83 ±2 | 89 ±1 |
| 1–2 | D | 1742 | 58 ±1 | 69 ±1 | 76 ±1 | 82 ±1 |
| 1–2 | chỉ D | 1077 | 58 ±2 | 68 ±1 | 75 ±1 | 80 ±1 |
| 3–4 | mọi vùng | 2513 | 23 ±1 | 39 ±1 | 52 ±1 | 62 ±1 |
| 3–4 | B | 1385 | 23 ±1 | 38 ±1 | 52 ±1 | 64 ±1 |
| 3–4 | B15 | 938 | 22 ±1 | 38 ±2 | 51 ±2 | 63 ±2 |
| 3–4 | C | 483 | 25 ±2 | 43 ±2 | 60 ±2 | 72 ±2 |
| 3–4 | D | 1722 | 22 ±1 | 37 ±1 | 49 ±1 | 60 ±1 |
| 3–4 | chỉ D | 1007 | 23 ±1 | 37 ±2 | 49 ±2 | 58 ±2 |

± = sai số nhị thức (đánh giá thấp vì mẫu chồng lấn).

### 9. Chạm rồi quay lại ≥ 2u trong 30 nến (kỳ vọng "TP rồi đảo") — trong các mẫu ĐÃ chạm trong 120 nến

| d (u) | n chạm gộp | gộp % | TRAIN % | TEST % | |Δ| |
|---|---|---|---|---|---|
| ≤1 | 2171 | **60** | 60 | 60 | 0 |
| 1–2 | 2065 | **60** | 60 | 62 | 3 |
| 2–3 | 1868 | **62** | 63 | 61 | 2 |
| 3–4 | 1565 | **67** | 65 | 69 | 4 |
| 4–6 | 2300 | **64** | 67 | 59 | 8 |
| 6–8 | 1302 | **68** | 71 | 63 | 8 |
| 8–12 | 1057 | **71** | 75 | 65 | 9 |

<!-- NHAN-XET -->
## Nhận xét (≤ 15 dòng)
1. **Vệ sinh: tiến bộ rõ nhưng CHƯA đạt mục tiêu.** Đổi vùng 12 → **6,0 (TRAIN) / 5,2 (TEST) lần/giờ** (mục tiêu ≤ 4). Tuổi thọ trung vị 11 → **20 / 30 phút** (mục tiêu ≥ 30: TEST vừa chạm, TRAIN chưa). Bộ tính lại 2116 lần (≈ 1 lần/14 nến). % nến trong vùng hiển thị 34–35% (giờ hợp lệ vì giữ vùng chứa giá); 6,0–6,3 vùng sống trong ±10u.
2. **Bảng tra 6 rất ổn định giữa TRAIN và TEST.** Bảng "mọi pha": |Δ| ≤ 3 điểm ở mọi ô. Theo pha: phần lớn |Δ| ≤ 5; lệch lớn nhất 14 điểm (Âu, 8–12u, 120 nến). Xác suất giảm đều theo khoảng cách: ≤1u ≈ 85% trong 15 nến, 3–4u ≈ 39% trong 30 nến, 8–12u ≈ 7% trong 30 nến.
3. **Pha Mỹ thấp hơn ở cửa sổ dài** (8–12u, 120 nến: 16% so với 34–42%). Phần lớn là do **cắt cuối phiên**: phiên Mỹ gần lúc đóng phiên, không đủ 120 nến. Đây là hạn chế đo, không phải "giá Mỹ ít đi xa".
4. **Bảng 7 (đặt SL):** sau khi giá đóng vào vùng, trong 10 nến râu vượt biên xa ≥ 0,25u: 63%; ≥ 0,5u: 56%; ≥ 1,0u: 43%. Pha Mỹ thấp hơn ~5–9 điểm. TRAIN/TEST lệch ≤ 5. Bảng này tính MỌI lần vào vùng, kể cả ca sau đó xuyên hẳn. Bảng 2 của v2 chỉ tính ca bật (8%) nên hai số không so trực tiếp được.
5. **Kiểm chứng "chỉ khoảng cách" (bảng 8):** B, B15, D, "chỉ D" ≈ nhau (lệch ≤ 3 điểm). **C cao hơn** ở 3–4u (60 vs 52% trong 60 nến, 72 vs 62% trong 120 nến). Tách thêm (ngoài report): khác biệt đó nằm chủ yếu ở TRAIN (120 nến 77 vs 58%). Ở TEST chỉ 66 vs 63%. Pha Âu ≈ nhau. Mẫu C chỉ ~470 nến khác nhau ⇒ **không nhất quán, chưa chốt**. Phép đo v2 có đối chứng cũng ≈. Đề xuất: giữ một bảng tra chung cho mọi loại.
6. **Bảng 9:** chạm rồi quay lại ≥ 2u trong 30 nến: 60–71%, tăng nhẹ theo d. TRAIN/TEST lệch ≤ 9. Cũng là mô tả: v2 đã cho vùng giả cùng khoảng cách ≈ như nhau.
7. Kết luận: thiết kế đủ ổn để port nếu chấp nhận 5–6 đổi/giờ. Muốn ≤ 4 thì cần thêm một luật (gợi ý ở dưới), chưa thử vì là chọn tham số.

## Vấn đề / giới hạn gặp phải
- **Mục tiêu ≤ 4 đổi/giờ chưa đạt.** Nguồn đổi còn lại: (a) vùng hiển thị nhập với ứng viên mới (swing mới sinh sát vùng) ⇒ "2 vùng cũ khớp 1 vùng mới" hoặc vùng đổi hình ⇒ tính lại; (b) mỗi lần ra khỏi hành lang thì khe gần phía bên kia đổi.
  Hướng vòng 4 (cần Fable chọn):
  - đóng băng tập ứng viên của vùng đang hiển thị;
  - KEEP_BONUS áp cả cho khe gần;
  - hành lang nới thêm 1u.
- **Mẫu bảng tra chồng lấn**: lấy mẫu mỗi 5 nến trên cùng vùng ⇒ n ghi trong bảng lớn hơn n hiệu dụng; ± trong bảng 8 đánh giá thấp. Chỉ ~20 phiên dữ liệu.
- **Chạm tính trong phiên**: mẫu sát cuối phiên bị cắt ⇒ cửa sổ 60/120 nến của pha Mỹ thấp hơn thực. Port C# nên ghi chú hoặc chỉ hiển thị cửa sổ 15/30 cho pha Mỹ.
- **Màu/vai của vùng** được chốt lúc tính lại bộ. Giá đi vào vùng gần-1 mà chưa vượt cạnh xa thì vùng vẫn mang vai cũ (vd đỏ) dù giá đang ở trong. Trên ảnh v3 có các dải đỏ có giá chạy bên trong — đúng luật, không phải lỗi. C# có thể đổi sang màu "đang kiểm tra" khi giá đóng trong vùng.
- **Khe xa có thể rất xa** (ví dụ dưới: 26,7u) vì biên trên = 1,5 × biên độ phiên trước. Bảng tra không phủ > 12u ⇒ dòng tra để trống.
- **Ví dụ cụ thể**: không có nến 20:35 VN nào đúng close 4440,0 VÀ u = 1,7. Tôi lấy nến thật gần nhất (2026-09-08, close 4442,0, u = 2,50), nên ví dụ có 6 vùng (không có vùng chứa giá lúc đó).

## Chỗ phải tự quyết
- KEEP_BONUS ×1,5 chỉ có tác dụng ở khe xa: khe gần chọn theo khoảng cách, không theo điểm.
- "Vùng chết" (luật 3a) = vùng hiển thị có ứng viên vừa bị xuyên ở nến này (cờ từ luật chuyển vai), hoặc vùng biến mất / nhập nhau.
- Hành lang dùng biên HIỆN TẠI của vùng gần-1 (biên có thể dịch nhẹ khi ứng viên mới nhập vào). Thiếu vùng gần-1 phía nào thì dùng giá lúc chốt bộ ± 4u.
- Khe xa đo từ cạnh ngoài vùng gần-2. Thiếu vùng gần-2 thì đo từ vùng gần-1, thiếu nữa thì từ cạnh vùng chứa giá hoặc giá.
- Bảng tra 6/8/9 lấy mẫu mỗi 5 nến trên mọi vùng hiển thị trừ vùng chứa giá, d ≤ 12u. Bảng 7 tính mọi lần giá đóng vào vùng hiển thị từ ngoài; vùng đó chỉ được đếm lại sau khi giá đóng ra ngoài.
- "Chỉ D-10$" = mọi ứng viên trong vùng là D trọng số 1.
- E, F đã bỏ khỏi ứng viên, nhưng `vcl3.gen_candidates` vẫn gọi `vcl2.gen_candidates` rồi lọc (thêm ~0,5 giây, không ảnh hưởng kết quả).

<!-- DAC-TA -->
## ĐẶC TẢ PORT C# (vòng 4)

### Hằng số

| Tên | Giá trị | Ghi chú |
|---|---|---|
| TICK | 0,1 | 1 giá = 1 USD = 10 tick |
| U_N | 50 | u = TRUNG VỊ (high−low) của 50 nến M1 gần nhất, GỒM nến vừa đóng; cần ≥ 10 nến; chạy xuyên phiên |
| SESSION_GAP_MIN | 30 | khoảng trống > 30 phút giữa 2 nến M1 ⇒ phiên mới |
| SESS_BARS | 1380 | 1 "phiên" khi tính tuổi ứng viên |
| LINK_U | 1,0 | gộp đơn liên kết khi 2 mức liền kề cách ≤ 1,0u |
| PAD_U | 0,5 | biên vùng = min/max mức trong cụm ± 0,5u |
| WMIN_U / WMAX_U | 1,0 / 4,0 | rộng < 1u ⇒ nới đều quanh tâm; rộng > 4u ⇒ tách tại khe lớn nhất (đệ quy) |
| Overlap | cắt giữa | 2 vùng kề chồng nhau ⇒ cả hai dùng điểm giữa đoạn chồng làm biên |
| SWING_M5_K | 5 | đỉnh/đáy M5: cao/thấp nhất 5 nến M5 mỗi bên (đỉnh: 5 nến trước THẤP HƠN hẳn) |
| SWING_M15_K | 3 | như trên với nến M15, 3 nến mỗi bên |
| W_B / W_B15 / W_C / W_NPOC | 2 / 3 / 2 / 3 | trọng số loại |
| W_D10 / W_D50 / W_D100 | 1 / 2 / 3 | số tròn bội 10 / 50 / 100 USD |
| D_WINDOW | 40 USD | sinh mức D bội 10 trong [close−40, close+40] khi lần đầu lọt cửa sổ; D không chết, không suy giảm, không chuyển vai |
| TOUCH_K / TOUCH_CAP | 0,3 / 5 | điểm ứng viên × (1 + 0,3 × min(số lần chạm, 5)); chạm = giá đóng vào vùng từ ngoài (cùng phiên) |
| FLIP_MULT / BREAK_U | 0,7 / 1,0 | đóng xuyên qua CẢ vùng ≥ 1u ⇒ chuyển vai, điểm ×0,7; lần xuyên thứ 2 ⇒ chết (B, B15, C, POC trần) |
| NEAR_N | 2 | 2 vùng gần mỗi phía |
| FAR_LO_U / FAR_RANGE_K | 2,0 / 1,5 | khe xa: khoảng cách từ cạnh ngoài vùng gần-2 nằm trong [2u, 1,5 × biên độ phiên trước] |
| KEEP_BONUS | 1,5 | khi tính lại bộ, vùng đang hiển thị được nhân điểm ×1,5 lúc tranh khe xa |
| CORRIDOR_FALLBACK_U | 4,0 | thiếu vùng gần-1 ở phía nào thì biên hành lang phía đó = giá lúc chốt bộ ± 4u |

### Pha phiên (sm = số phút kể từ 05:00 VN, khi Mỹ dùng giờ mùa đông thì các mốc lùi +1h theo giờ VN — như kernel)

- Á: sm < 450 (05:00–12:30 VN) · Âu: 450 ≤ sm < 840 (12:30–19:00 VN) · Mỹ: sm ≥ 840 (19:00 VN → hết phiên).

### Ứng viên — sinh / sống / chết

- **B** (swing M5 k=5): nến M5 gộp theo mốc đồng hồ (UTC, floor 5 phút), không gộp xuyên phiên. Đỉnh xác nhận khi nến M5 thứ 5 sau nó ĐÓNG (theo đồng hồ: nến M1 cuối cùng là phút thứ 5; nếu thiếu phút thì đợi nến M1 kế tiếp). Sống 4 phiên (5520 nến M1); từ 2 phiên trở đi điểm ×0,5.
- **B15** (swing M15 k=3): như B với nến M15, 3 nến mỗi bên. Sống 3 phiên (4140 nến), không suy giảm.
- **C** (sống 1380 nến từ lúc sinh): đỉnh/đáy/đóng phiên trước (sinh ở nến đầu phiên); VAH/VAL/POC hôm qua (profile hàng 0,2 giá, VA 70%, phiên trước ≥ 300 nến); biên Á = đỉnh/đáy các nến sm < 450 (cần ≥ 60 nến), sinh ở nến đầu có sm ≥ 450; VAH/VAL Âu (cửa sổ 450 ≤ sm < 840, cần ≥ 60 nến), sinh ở nến đầu có sm ≥ 840.
- **POC trần** (w3): POC các phiên trước (≤ 30 phiên) chưa bị chạm tính tới đầu phiên này; giữ 3 cái gần nhất; chết ở nến đầu tiên high ≥ POC ≥ low.
- **D**: xem D_WINDOW. Vùng mà MỌI mức trong nó là D bội 10 (không 50/100, không loại khác) = "chỉ D-10$".
- **Phía (side) của ứng viên** lúc sinh: close − giá ≥ 0,5u ⇒ +1 (hỗ trợ); ≤ −0,5u ⇒ −1 (kháng cự); còn lại 0, gán khi giá đóng ra khỏi vùng chứa nó.

### Mỗi nến đóng (thứ tự)

1. Nạp ứng viên sinh tại nến này + sinh D mới; bỏ ứng viên hết tuổi.
2. Gộp → vùng (dùng u hiện tại). Đếm chạm (giá đóng vào vùng từ ngoài, nến trước cùng phiên).
3. Luật xuyên cho B/B15/C/POC trần trong từng vùng: side +1 và close < lo − 1u, hoặc side −1 và close > hi + 1u ⇒ breaks+1, đổi side; breaks ≥ 2 ⇒ chết. Ghi cờ "vùng có ứng viên vừa bị xuyên".
4. Gộp lại sau khi bỏ ứng viên chết. Điểm vùng = Σ w × (0,5 nếu quá mốc suy giảm) × (1 + 0,3·min(chạm,5)) × 0,7^breaks.
5. Khớp từng vùng đang hiển thị với vùng mới chồng lấn nhiều nhất. **Tính lại bộ** nếu: chưa có bộ; có vùng hiển thị không khớp (biến mất) hoặc 2 vùng cũ nhập vào 1; vùng hiển thị có cờ vừa bị xuyên; hoặc close > cạnh trên vùng gần-1 phía trên, hoặc close < cạnh dưới vùng gần-1 phía dưới (hành lang, dùng biên HIỆN TẠI của các vùng đã khớp). Không tính lại ⇒ giữ nguyên bộ (biên cập nhật theo vùng khớp).
6. Chọn bộ mới: vùng chứa close (lo ≤ close ≤ hi) = "đang kiểm tra"; 2 vùng gần phía trên = 2 vùng có lo > cạnh trên vùng chứa giá (hoặc > close), lo nhỏ nhất; gương phía dưới; khe xa mỗi phía như hằng số; ưu tiên vùng không phải "chỉ D-10$". Tối đa 7 vùng.
7. Vùng giữ nguyên mã (ID) nếu khớp vùng cũ ⇒ đếm "đổi vùng" = số ID mới.

### Bảng tra nhúng code (giá trị %, gộp TRAIN+TEST; −1 = không đủ mẫu, hiển thị "—")

Bin khoảng cách d (u, tới cạnh gần): 0: ≤1 · 1: 1–2 · 2: 2–3 · 3: 3–4 · 4: 4–6 · 5: 6–8 · 6: 8–12 (> 12u: không hiển thị). Cột cửa sổ: 15 / 30 / 60 / 120 nến. Pha: 0 Á · 1 Âu · 2 Mỹ.

```csharp
static readonly int[,] REACH_PHASE0 = {
    { 84, 87, 92, 95 },
    { 58, 71, 81, 86 },
    { 44, 58, 71, 79 },
    { 29, 46, 60, 72 },
    { 16, 31, 47, 62 },
    { 7, 17, 35, 51 },
    { 3, 10, 23, 42 }
};
static readonly int[,] REACH_PHASE1 = {
    { 87, 92, 94, 96 },
    { 61, 72, 79, 85 },
    { 38, 54, 66, 76 },
    { 22, 38, 52, 66 },
    { 11, 22, 38, 55 },
    { 4, 11, 25, 43 },
    { 1, 5, 15, 34 }
};
static readonly int[,] REACH_PHASE2 = {
    { 83, 89, 91, 93 },
    { 58, 69, 75, 80 },
    { 37, 51, 61, 68 },
    { 20, 34, 45, 53 },
    { 10, 20, 32, 44 },
    { 5, 11, 23, 36 },
    { 2, 5, 9, 16 }
};
static readonly int[,] REACH_ALL = {
    { 85, 89, 92, 94 },
    { 59, 71, 78, 83 },
    { 39, 54, 65, 73 },
    { 23, 39, 52, 62 },
    { 12, 24, 39, 53 },
    { 6, 13, 27, 43 },
    { 2, 7, 16, 30 }
};
// pha × {≥0,25u, ≥0,5u, ≥1,0u}
static readonly int[,] SWEEP = {
    { 66, 59, 47 },
    { 64, 58, 45 },
    { 60, 53, 38 }
};
// theo bin d, mọi pha
static readonly int[] REVERT2U = { 60, 60, 62, 67, 64, 68, 71 };
```

### Ví dụ cụ thể (nến thật gần đề bài nhất): phiên 2026-09-08, 20:35 VN, close 4442.0, u = 2.50, pha Mỹ

| # | vùng (lo–hi) | vai | loại · điểm | d tới cạnh gần (u) | dòng tra hiển thị |
|---|---|---|---|---|---|
| 1 | 4508.8–4514.2 | kháng cự (xa) | B+B15+D · 32 | 26.7 | xa > 12u: không tra |
| 2 | 4456.6–4462.1 | kháng cự | B+B15+D · 15 | 5.9 | chạm ≤15/30/60/120 nến: 10% / 20% / 32% / 44%; chạm rồi quay ≥2u: 64% |
| 3 | 4447.6–4455.2 | kháng cự | B+B15+C+D · 68 | 2.3 | chạm ≤15/30/60/120 nến: 37% / 51% / 61% / 68%; chạm rồi quay ≥2u: 62% |
| 4 | 4438.8–4441.2 | hỗ trợ | D · 2 | 0.3 | chạm ≤15/30/60/120 nến: 83% / 89% / 91% / 93%; chạm rồi quay ≥2u: 60% |
| 5 | 4428.2–4433.2 | hỗ trợ | B+B15+C+D · 32 | 3.5 | chạm ≤15/30/60/120 nến: 20% / 34% / 45% / 53%; chạm rồi quay ≥2u: 67% |
| 6 | 4408.8–4413.2 | hỗ trợ (xa) | B+B15+D · 12 | 11.5 | chạm ≤15/30/60/120 nến: 2% / 5% / 9% / 16%; chạm rồi quay ≥2u: 71% |

Ví dụ này có 6 vùng (tối đa 7: 1 đang kiểm tra + 2 gần + 1 xa mỗi phía; thiếu vùng chứa giá hoặc thiếu khe xa thì ít hơn).

