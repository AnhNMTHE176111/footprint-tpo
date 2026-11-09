# Mổ SL Follow — vòng 1 (chế độ "khám phá, hậu kiểm")

> Opus, 2026-11-09, theo `plans/BENZO-FOLLOW-COMBO-plan.md` mục 5 + 9.2 + 9.3-B. **Chỉ TRAIN** (35 phiên dày, tới 2026-09-15). Đây là **bài học đọc chart**, không phải bước tới signal: F7 Δ 0,20 < ngưỡng hoán vị 0,31, p cực đại 0,76 (ngưỡng ≥ 30: p 0,23) — **không** được nói "F7 có lợi thế". Mọi luật rút ra ở đây (F7b/F10b) chỉ được đo lại trên TRAIN để báo, xác nhận duy nhất trên dữ liệu mới ≥ 22/10/2026. Tối đa 2 vòng mổ trên TRAIN; đây là vòng 1.

## 0. Ảnh

- Thư mục `report/follow_shots/<combo>/`; tên `SL_<idx_c>.png` / `TP_<idx_c>.png` (F1 có thêm `TIME_<idx_c>.png`). `idx_c` = bar_idx của nến CF trong file `fp_GCZ26_XCEC_Time_20260723-20261021_90d`.
- Mỗi ảnh: nến M1 (~40 trước, ~30 sau), Δ dưới nến; hộp vàng = range tới nến đóng ngoài, đường nâu đậm = cạnh E; đường chấm dọc = nến đóng ngoài (ref); tam giác tím "x" = nến cực trị move; dải xám = nhịp hồi + CF; chữ "hồi" dưới nến hồi; mũi tên "CF"; đường xanh nét đứt = giá vào, đỏ = SL (S2), xanh lá = TP 2R; ô vuông màu = ô trap (đỏ) / bóng (xanh lá) / kiệt sức (cam) đúng mức giá; dải xanh = vùng stacked; vòng tròn + chú thích dưới đáy = cờ bật. Tiêu đề: combo · idx · giờ UTC (VN) · side · leg · cờ · kết cục R. **Không in nhãn máy lên ảnh.**
- Số ảnh: F7 60 (55 SL + 5 TP) · F10 78 (73 SL + 5 TP) · F1 11 (cả 11 lệnh — chỉ soi định nghĩa trap, không rút luật).

## 1. Nhãn tay của Fable (2026-11-09)

**Cách làm.** Gắn nhãn **toàn bộ** 149 ảnh (không lấy mẫu): F7 60 ảnh và F10 34 ảnh SL riêng (39 SL còn lại trùng F7 — cùng lệnh, cùng ảnh) + 5 TP do **hai bản sao của Fable** (fork, cùng ngữ cảnh) gắn song song theo một giao thức cố định viết trước; F1 11 ảnh do Fable gắn trực tiếp. Fable kiểm chéo **16 ảnh có hệ thống** (F7: mỗi ảnh thứ 7 theo tên file + 3 ảnh agent chính nêu; F10: 2 ca fork gọi là "climax"/"TP quá xa" + 4 ca trùng F1): **15/16 khớp**, 1 ca biên (SL_41632: fork SL_QUET, Fable HOI_SAU — giá sau SL thiếu 0,6 giá tới TP). Không ai mở `_mo_sl_follow.csv` trước khi gắn. Công khai: Fable đã thấy **bảng % tổng** của mục 2 (trong đề bài), nhưng không thấy nhãn từng lệnh. Bảng đầy đủ từng ảnh (nhãn chính + 7 cờ phụ): **`report/_mo_sl_fable_tay.csv`**.

Giao thức: 7 nhãn như mục 2, xét bằng mắt theo ưu tiên; cờ phụ **tại CF**: V_XA (move xuất phát từ phía đối diện range / move ≥ 2× range), VAO_XA (vào − E ≥ 1,5 mbr), CF_NHO (thân < 40 %), HOI_CHAM_E (râu hồi chạm/vượt E), NEN_HOI_1; cờ **sau khi vào** (chỉ chẩn đoán): SAU_DUNG_HUONG (sau SL giá tới mức TP trong ảnh), SL_RAU (nến dính SL chỉ quét râu).

### 1.1 F1 — 11 lệnh (soi định nghĩa trap, không rút luật)

| ảnh | side | leg | nhãn tay | V_XA | VAO_XA | CF_NHO | HOI_CHAM_E | ghi chú |
|---|---|---|---|---|---|---|---|---|
| SL_9677 | sell | 1 | HOI_SAU | 1 | 1 | 0 | 0 | hồi 74 %; đi 0,3R rồi đóng hẳn vào range (không phải râu) |
| SL_11825 | buy | 1 | HOI_SAU | 0 | 0 | 0 | 1 | hồi chạm E; 1 giờ trước giảm 11 giá (NGUOC_1H cũng đúng); đi +1,3R rồi quay |
| SL_18993 | sell | 1 | KHONG_RO | 0 | 1 | 0 | 0 | CF −121 ở đáy move; đảo về range ở nến **6** (biên MOVE_GIA) |
| SL_25804 | sell | 2 | CF_YEU | 1 | 1 | 1 | 0 | leg 2, CF thân nhỏ; đi +1,6R (thiếu 1,6 giá tới TP) rồi quay |
| SL_27864 | buy | 2 | KHONG_RO | 1 | 1 | 0 | 0 | move xuyên range 5,5 giá; đi +1R rồi quay |
| SL_47877 | sell | 1 | MOVE_GIA | 1 | 1 | 0 | 0 | CF −53 to; đóng về range ở nến 4 |
| TP_22686 | buy | 1 | HOI_SAU | 1 | 0 | 1 | 1 | mbr 0,8; hồi chạm E vẫn TP |
| TP_27201 | buy | 2 | CF_YEU | 1 | 1 | 1 | 0 | CF doji trên move 2,8× range |
| TP_42754 | buy | 1 | HOI_SAU | 0 | 1 | 0 | 0 | hồi 80 %, CF thân vừa |
| TP_44403 | sell | 1 | CF_YEU | 0 | 1 | 1 | 0 | CF thân nhỏ |
| TP_8116 | buy | 1 | CF_YEU | 0 | 1 | 1 | 0 | CF +1 doji, sau đó +17 |

Định nghĩa **T** (ô ngược ≥ 3× nền ở cực trị nhịp hồi, CF đóng qua ô) bắt đúng cơ chế trong cả 11 ảnh — không ca nào ô trap nằm sai chỗ. Nhưng 6 SL / 5 TP **không khác nhau ở bất kỳ cờ nào tại CF**; 3/6 SL thuộc kiểu "đã đi +1R…+1,6R rồi quay". Với n 11 không nói thêm gì.

### 1.2 Nhãn tay vs nhãn máy (lệnh có ảnh; nhãn máy đọc SAU khi gắn xong)

| | F7 (55 SL + 5 TP) | F10 (73 SL + 8 TP) |
|---|---|---|
| khớp tay = máy | **46/60 = 77 %** (SL 78 %, TP 60 %) | **55/81 = 68 %** (SL 70 %, TP 50 %) |
| MOVE_GIA tay → máy cũng MOVE_GIA | 24/24 | 19/19 |
| máy MOVE_GIA mà tay không | 2 (SL_17384 nến 5–6; SL_18181 nến 3 đóng sát E) | 2 |
| máy CF_YEU mà tay KHONG_RO/PHIEN_MONG/HOI_SAU | 5 | 11 |
| tay HOI_SAU mà máy khác | 3 | 7 |

Đếm nhãn chính — tay / máy, chỉ lệnh SL: F7: MOVE_GIA 24/26 · SL_QUET 4/3 · HOI_SAU 11/10 · CF_YEU 4/8 · NGUOC_1H 0/1 · PHIEN_MONG 5/3 · KHONG_RO 7/4. F10: MOVE_GIA 19/21 · SL_QUET 2/2 · HOI_SAU 22/16 · CF_YEU 8/18 · NGUOC_1H 1/3 · PHIEN_MONG 5/5 · KHONG_RO 16/8.

Kết luận đối chiếu: (i) **MOVE_GIA bằng mắt và bằng máy trùng nhau gần tuyệt đối** — định nghĩa vững, con số 47 % của máy là thật. (ii) Lệch chủ yếu ở **CF_YEU**: máy gắn nhiều gấp đôi vì vế "đóng cách cực trị > 0,3 biên độ" mắt không thấy; mắt chỉ bắt "thân nhỏ". (iii) Cờ **V_XA bằng mắt không dùng được**: fork F7 gắn 51 %, fork F10 gắn 91 % trên cùng định nghĩa ⇒ thay bằng số đo (mục 4: "move xuyên range" 71 % SL vs 65 % TP — không tách).

### 1.3 Điều mắt thấy mà 7 nhãn không có tên

- **"Đi đúng hướng +1R rồi quay về SL"**: fork F7 đếm ~8/55, fork F10 ~7/34, F1 3/6. Đo bằng số (mục 4.3): **25–32 % lệnh SL** có MFE ≥ 1R trước khi dính SL. Hiện tượng sau vào lệnh — không làm luật vào lệnh.
- **Rủi ro tuyệt đối lớn (≥ 7 giá) ⇒ TP 2R = 15–40 giá** — fork F10 nêu 6 ca đều SL; số đo mục 4.2 xác nhận chiều (R TB âm ở cả F7/F10/F0) nhưng n nhỏ.
- **Vào đúng nến climax** (CF −342, −121 ở đáy move: SL_26422, SL_18993) rồi giá bật ngay — 2 ca, chỉ ghi.

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

## 3. Luật đề xuất (Fable, 2026-11-09 — hậu kiểm, chỉ xác nhận trên dữ liệu ≥ 22/10)

Nhãn duy nhất đạt 5.3 là **MOVE_GIA ở F7** (47 % SL / 0 % TP). Opus đúng rằng nhãn này đo **sau** khi vào lệnh và % TP = 0 một phần là cơ học; vì vậy luật phải là điều kiện **tại nến CF** mà MOVE_GIA tập trung vào. Đo trên toàn bộ lệnh thật (mục 4.4): MOVE_GIA tập trung ở nhóm **nhịp hồi chạm cạnh E** — F7: 13/33 = 39 % trong nhóm chạm so với 13/62 = 21 % nhóm không chạm; F0: 41 % so với 15 %. Hai ảnh tiêu biểu: [SL_21604](follow_shots/F7/SL_21604.png), [SL_49030](follow_shots/F7/SL_49030.png).

### F7b — "nhịp hồi không chạm cạnh E"
- **Định nghĩa (D = +1):** `min(low[nến hồi x+1 … c−1]) > E + tol`, `tol = max(2 tick, 0,5 mbr)` (tol của plan 2b; mbr tại c như các cờ khác). Cờ mới **Hc** = nhịp hồi chạm E; **F7b = Dh ∧ ¬Hc**. Vế "CF ≥ x+2" trong gợi ý 5.5 **bỏ** vì luôn đúng theo định nghĩa 2c (c ∈ [x+2, x+3]). Phiên bản "chạm đúng cạnh (≤ 2 tick)" quá hiếm (11/95 lệnh F7) để làm luật.
- **TRAIN, chỉ để báo** (lọc hậu kiểm trên 95 lệnh thật đã khớp — Opus phải chạy lại đúng pipeline one_at_a_time, số sẽ lệch chút): F7 ∧ ¬Hc **n 62 · WR 48 % · R TB +0,40 · KTC [0,02; 0,77] · ΣR 24,7 · nửa 1/2 +0,45 (36) / +0,33 (26)**; F7 ∧ Hc: n 33, R TB −0,17. Chênh +0,57R giữa hai nhóm là thứ cần lặp lại, không phải mức +0,40.
- **Tiêu chí đăng ký trước trên dữ liệu mới ≥ 22/10 (để gọi F7b "ĐẠT"):** đúng bộ tiêu chí bảng chính (n ≥ 30; ≥ C1 + 0,15; ≥ C2' + 0,15; KTC dưới > −0,10; dương cả hai nửa; vượt ngưỡng hoán vị ≥ 30) **và thêm** điều kiện cơ chế: trên dữ liệu mới, `R TB(F7 ∧ ¬Hc) − R TB(F7 ∧ Hc) ≥ +0,20`. Thiếu một trong hai ⇒ F7b chết, không sửa tiếp. **Dự đoán đăng ký trước của Fable:** R TB F7b trên dữ liệu mới rơi về **0,00 … +0,30** (co lại ít nhất một nửa); xác suất ĐẠT theo tôi dưới 1/3.

### F10 — không rút luật
Không nhãn nào của F10 đạt 5.3 (MOVE_GIA 28,8 % SL). Theo plan 5.5 không có F10b. Chỉ chạy **biến thể báo cáo** `F10 ∧ ¬Hc` (TRAIN lọc hậu kiểm: n 85, +0,19 [−0,13; 0,50]) và `F0 ∧ ¬Hc` (n 237, +0,01) để xem cơ chế có nhất quán — **không có sức chọn**.

### Ba giả thuyết hậu kiểm — ĐĂNG KÝ ĐỂ ĐO, KHÔNG PHẢI LUẬT (phát hiện khi cắt 9 ngưỡng ở mục 4.2 ⇒ đã nhìn số rồi mới thấy; không được cộng vào F7b)
| | giả thuyết | TRAIN (R TB hai phía) | dự đoán trên dữ liệu mới |
|---|---|---|---|
| H1 | **CF thân nhỏ thắng hơn** (`|close−open|/(high−low) < 0,4`) — ngược hẳn nhãn CF_YEU | F7 +0,64 (30) vs 0,00 (65) · F10 +0,39 (35) vs 0,00 (85) · F0 +0,10 (77) vs −0,10 (258) | chênh ≥ +0,10 trên F0; nếu đảo dấu ⇒ bỏ |
| H2 | rủi ro S2 ≥ 7 giá thua (TP 2R quá xa) | F7 −0,27 (8) · F10 −0,27 (16) · F0 −0,19 (36) | R TB nhóm ≥ 7 giá < 0 |
| H3 | move_h ≥ 2× chiều cao range thua (move kéo dài — ý "V_XA" của agent chính, đo bằng số) | F7 −0,55 (6) · F10 −0,40 (14) · F0 −0,08 (31) | R TB nhóm này < phần còn lại |

Giả thuyết của agent chính **"vào xa cạnh / move từ phía đối diện"**: số không ủng hộ ở dạng tổng quát — vào − E ≥ 2 mbr lại **dương hơn** ở F7 (+0,32 vs +0,10) và F0 (+0,06 vs −0,17); "move xuyên range" 71 % SL vs 65 % TP. Chỉ đuôi cực đoan (H3, ≥ 2× range) âm, n nhỏ.

## 4. Đo số của Fable (`mo_sl_fable.py` → `_mo_sl_fable_feats.csv`; toàn bộ lệnh thật F7 / F10 / F0, chỉ TRAIN)

### 4.1 Đặc điểm biết được tại nến CF — trung vị SL | TP (% với cờ nhị phân)

| đặc điểm | F7 SL | F7 TP | F10 SL | F10 TP | F0 SL | F0 TP |
|---|---|---|---|---|---|---|
| rủi ro S2 (giá) | 3,30 | 3,45 | 4,30 | 3,50 | 3,60 | 3,60 |
| rủi ro S2 (mbr) | 2,10 | 2,23 | 2,62 | 2,27 | 2,27 | 2,33 |
| vào − E (mbr) | 1,80 | 2,00 | 2,36 | 2,07 | 2,00 | 2,09 |
| move_h / chiều cao range | 0,92 | 0,84 | 1,03 | 0,91 | 0,97 | 0,96 |
| % move xuyên range (chạm cạnh đối diện ≤ 15 nến trước ref) | 71 % | 65 % | 64 % | 62 % | 71 % | 72 % |
| depth_frac (hồi / move) | 0,67 | 0,52 | 0,62 | 0,61 | 0,65 | 0,58 |
| % nhịp hồi đúng 1 nến | 75 % | 82 % | 74 % | 83 % | 70 % | 82 % |
| thân CF / biên độ | 0,63 | 0,50 | 0,61 | 0,50 | 0,65 | 0,59 |
| CF đóng cách cực trị / biên độ | 0,25 | 0,23 | 0,22 | 0,17 | 0,18 | 0,22 |
| xu hướng 1 giờ theo hướng lệnh (mbr) | 3,73 | 2,89 | 4,00 | 3,94 | 2,75 | 2,86 |
| % leg 2 | 22 % | 20 % | 26 % | 17 % | 19 % | 19 % |
| % phiên Á | 40 % | 40 % | 34 % | 34 % | 41 % | 36 % |
| **% nhịp hồi chạm E (tol)** | **42 %** | **25 %** | 32 % | 26 % | 31 % | 26 % |

Không đặc điểm nào tách SL khỏi TP rõ ở cả ba bộ; hai đặc điểm lệch cùng chiều ở cả ba: **thân CF** (SL to hơn TP) và **nhịp hồi 1 nến** (TP nhiều hơn).

### 4.2 Cắt theo ngưỡng — R TB (n) hai phía (hậu kiểm, CHỈ BÁO)

| ngưỡng | F7 đạt | F7 không | F10 đạt | F10 không | F0 đạt | F0 không |
|---|---|---|---|---|---|---|
| rủi ro S2 ≥ 5 giá | 0,25 (28) | 0,18 (67) | −0,16 (45) | 0,28 (75) | −0,08 (92) | −0,04 (243) |
| rủi ro S2 ≥ 7 giá | −0,27 (8) | 0,24 (87) | −0,27 (16) | 0,18 (104) | −0,19 (36) | −0,03 (299) |
| rủi ro S2 ≥ 2,5 mbr | 0,11 (34) | 0,25 (61) | −0,15 (54) | 0,33 (66) | −0,02 (138) | −0,07 (197) |
| vào − E ≥ 2 mbr | 0,32 (44) | 0,10 (51) | 0,05 (66) | 0,20 (54) | 0,06 (177) | −0,17 (158) |
| vào − E ≥ 3 mbr | 0,17 (15) | 0,21 (80) | −0,19 (25) | 0,20 (95) | −0,21 (69) | −0,01 (266) |
| move_h ≥ 1 × range | 0,10 (39) | 0,27 (56) | −0,07 (55) | 0,27 (65) | −0,07 (162) | −0,03 (173) |
| move_h ≥ 2 × range | −0,55 (6) | 0,25 (89) | −0,40 (14) | 0,19 (106) | −0,08 (31) | −0,05 (304) |
| depth_frac > 0,7 | −0,16 (36) | 0,42 (59) | 0,14 (42) | 0,10 (78) | −0,13 (127) | 0,00 (208) |
| thân CF < 0,4 | **0,64 (30)** | 0,00 (65) | **0,39 (35)** | 0,00 (85) | 0,10 (77) | −0,10 (258) |

### 4.3 Giả thuyết "SL sát cạnh bị quét rồi giá đi đúng hướng" — KHÔNG ĐỨNG

Nền = với mỗi lệnh SL rút 20 nến ngẫu nhiên cùng phiên sau CF, đích cách close nến đó đúng 3R (= khoảng từ SL tới TP), đo cùng hướng và ngược hướng.

| combo | n SL | SL chỉ râu (≤ 2 tick quá SL) | MFE ≥ 1R trước SL | MFE ≥ 1,5R | chạm TP sau SL ≤ 15 nến | ≤ 30 | ≤ 60 | nền cùng hướng 15/30/60 | nền ngược hướng 15/30/60 |
|---|---|---|---|---|---|---|---|---|---|
| F7 | 55 | 33 % | 25 % | 4 % | 9 % | 24 % | 31 % | 12 / 21 / 33 % | 13 / 21 / 31 % |
| F10 | 73 | 33 % | 32 % | 5 % | 4 % | 11 % | 22 % | 10 / 17 / 27 % | 10 / 21 / 30 % |
| F0 | 222 | 32 % | 29 % | 7 % | 8 % | 17 % | 31 % | 11 / 20 / 30 % | 12 / 20 / 31 % |

Sau khi dính SL, giá tới mức TP **không nhiều hơn nến ngẫu nhiên** (F7 24 % so với nền 21 %; F10 còn thấp hơn nền). Ca "SL râu ≤ 2 tick và chạm TP ≤ 30 nến" (đúng định nghĩa SL_QUET): F7 7/55 = 13 %, F10 4/73 = 5 %. ⇒ Không nới đệm SL, không thử S2 đệm 5 tick. Điều thật sự có: **25–32 % lệnh SL đã đi được ≥ 1R rồi mới quay** — là chuyện quản lý lệnh, ghi nhận, chưa đụng.

### 4.4 Nhịp hồi chạm E (cờ Hc, tol = max(2 tick, 0,5 mbr)) — nền của F7b

| combo | % SL chạm | % TP chạm | R TB chạm (n) | R TB không chạm (n) | MOVE_GIA trong chạm | MOVE_GIA trong không chạm |
|---|---|---|---|---|---|---|
| F7 | 42 % | 25 % | −0,17 (33) | **+0,40 (62)** | 13/33 = 39 % | 13/62 = 21 % |
| F10 | 32 % | 26 % | −0,06 (35) | +0,19 (85) | 10/35 = 29 % | 11/85 = 13 % |
| F0 | 31 % | 26 % | −0,20 (98) | +0,01 (237) | 40/98 = 41 % | 36/237 = 15 % |

Ghi chú: Hc và H1 (thân CF nhỏ) gần như độc lập (F7: chỉ 4/33 ca chạm có thân < 0,4); "không chạm ∧ thân nhỏ" F7 +0,67 (26) / F10 +0,55 (28) / F0 +0,24 (60) — **không** cộng dồn thành luật, chỉ ghi để dữ liệu mới kiểm.

## 5. Trả lời 3 câu của Opus + quyết định

1. **Mổ F3? KHÔNG.** R TB 0,00, nửa 2 −0,21, vướng mọi tiêu chí trừ n; mổ SL chỉ dành cho combo có triển vọng và quỹ chỉ còn 1 vòng trên TRAIN. F3 chỉ đo lại cùng bảng trên dữ liệu mới.
2. **Dạng luật cho MOVE_GIA:** `¬Hc` — "nhịp hồi không chạm cạnh E trong tol" (mục 3, F7b). Bỏ vế "CF ≥ x+2" (luôn đúng). Không dùng "đóng về range ≤ 5 nến" làm bất cứ gì vì đó là mô tả cách thua.
3. **Chạy lại lưới GĐ2 vòng 2 (CORVEN) bằng C2'? KHÔNG.** Không ô nào qua C1 nên C2' không đổi được kết luận; chạy lại chỉ thêm một lần nhìn số. Giữ ghi chú đã có trong RESULTS-CORVEN.md; từ nay mọi bảng so với C2 **theo thế** dùng C2'.
4. **Vòng mổ 2 trên TRAIN: KHÔNG mở.** Vòng 1 đã cho 1 luật (F7b) + 3 giả thuyết; vòng 2 trên cùng dữ liệu chỉ tăng khớp quá tay. Chờ dữ liệu ≥ 22/10.

Việc giao Opus: **plan mục 10.3** (nguyên văn, chuyển thẳng).

## 6. Cho người học — lệnh thua của Follow thường sai ở đâu

Soi 149 ảnh lệnh Follow thì lệnh thua thường **không** thua vì SL quá sát: sau khi dính SL, giá chạm được mức TP cũng chỉ ngang một nến ngẫu nhiên (F7: 24 % so với nền 21 %), nên ý "SL bị quét rồi giá đi đúng hướng" không đứng. Kiểu thua lớn nhất là **cú phá giả**: giá đóng về lại trong range chỉ vài nến sau CF (gần một nửa lệnh thua của F7), và dấu hiệu thấy được **trước khi vào** là nhịp hồi đã kéo râu chạm lại cạnh range — xem [F7/SL_21604.png](benzo-trader/research/report/follow_shots/F7/SL_21604.png) và [F7/SL_49030.png](benzo-trader/research/report/follow_shots/F7/SL_49030.png). Kiểu thua thứ hai (khoảng 1/4 lệnh thua) là giá đã đi được +1R rồi quay về dính SL — xem [F10/SL_15482.png](benzo-trader/research/report/follow_shots/F10/SL_15482.png); cái này chưa có luật, chỉ ghi nhận. Bất ngờ: nến CF **thân nhỏ** lại thắng nhiều hơn CF thân to (F7: +0,64R so với 0,00R), ngược với nhãn "CF yếu" — ví dụ [F7/TP_4012.png](benzo-trader/research/report/follow_shots/F7/TP_4012.png). Tất cả đều là nhìn lại sau khi đã biết kết quả trên TRAIN nên chưa được tin; luật duy nhất đề xuất (F7b: bỏ lệnh khi nhịp hồi chạm cạnh E) chỉ được xác nhận trên dữ liệu từ 22/10 trở đi.

