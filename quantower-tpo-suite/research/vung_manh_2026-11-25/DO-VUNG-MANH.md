# Vùng kháng cự / hỗ trợ mạnh cho SessionZones — đo đạc (Fable, 2026-11-25)

Spec cho Opus: [`../../PLAN-VUNG-MANH.md`](../../PLAN-VUNG-MANH.md). File này là phần số liệu đứng sau spec.

## 0. Kết luận trước

1. **Không đo được lợi thế.** Vùng "va đập ≥ 3 lần + hợp lưu ≥ 1 mức" (đúng thứ sẽ vẽ) cho kết quả **ngang vùng dời ngẫu nhiên** ở mọi thước đo, cả TRAIN lẫn TEST: thắng 1:1 là 48,8 % / 47,2 % so với đối chứng 47,9 % / 47,5 %; R trung bình ở 1:2 là −0,02 / −0,03 so với −0,01 / −0,05. Khớp với kết luận cũ ở `vung-canh-lenh/research/report/HOP-LUU-SZ.md`.
2. **Điểm đảo chiều không tụ về vùng va đập.** Phân phối "giá quay đầu ở đâu so với tâm vùng" của vùng thật trùng khít với vùng dời (mục 3). Vì vậy **không có độ rộng nào "bắt đỉnh/đáy" tốt hơn độ rộng khác** — độ rộng phải chọn theo mức rủi ro chịu được, không theo số đo.
3. **Vùng vàng (≥ 3 nhóm mức, có HVN): mẫu quá nhỏ** (19 lần TRAIN, 41 lần TEST trong 2,3 năm) — chưa nói được gì. Luật vàng là **chưa kiểm định**.
4. **Một dấu hiệu yếu, chưa đủ chắc:** vùng hợp lưu **≥ 2 nhóm mức độc lập** có R ở 1:2 dương ở 14/16 ô (8 biến thể × TRAIN/TEST), nhưng trên TRAIN khoảng tin cậy luôn chứa 0 và một biến thể (bật lại 1,5 U) đổi dấu trên TEST. Ghi nhận để theo dõi, **không** coi là đã chứng minh.
5. Các tiêu chí người dùng nêu thêm — HVN của profile hình chữ D, "giá đã rời xa", vùng chưa bị phá, đúng vai kháng cự/hỗ trợ — **không cái nào tách được vùng tốt khỏi vùng xấu** trên dữ liệu này (mục 5, 6).

Hệ quả cho spec: indicator vẽ đúng định nghĩa người dùng yêu cầu, thông số chọn theo **mật độ trên chart và độ rộng giao dịch được**, và nhãn/ghi chú không được nói như vùng đã được chứng minh là đảo chiều.

## 1. Dữ liệu và cách chấm

- **Dữ liệu:** chuỗi M1 có khối lượng từng mức giá, 2024-08-01 → 2026-11-09: `fp_GC_XCEC_Time_20240801-20260819` (mã liên tục) tới 2026-08-10, sau đó `fp_GCZ26_*_90d` (một hợp đồng). 803.220 nến M1 → 26.843 nến M30, **589 phiên, 120 tuần, 9 chỗ nối hợp đồng** (không cụm va đập, profile hay đường đi nào vắt qua chỗ nối). Khối lượng trung vị 154.751 hợp đồng/phiên. `prep.py`, `info.py`.
- **TRAIN** = trước 2025-11-01, **TEST** = từ 2025-11-01. Các biến thể ở mục 7 chỉ để xem độ bền, không dùng để chọn lại thông số theo TEST.
- **Đơn vị biến động U** = trung bình (High − Low) của nến M30 trong 5 phiên đã đóng gần nhất, cố định suốt phiên. Trung vị: 2024 **4,7 giá**, 2025 **7,5 giá**, 2026 **13,4 giá** (p10–p90 năm 2026: 10,7–23,4). Vì biên độ vàng tăng gần 3 lần trong hai năm, mọi ngưỡng tính theo U, không theo giá cố định.
- **Lần quay lại vùng:** nến M30 chạm dải tâm ± 0,75 U trong khi nến trước không chạm, và từ lần chạm dải gần nhất giá đã rời tâm ≥ 1,25 U. Sau đó lưu 600 nến M1.
- **Thước đo:**
  - *Đảo trong vùng*: điểm giá quay đầu (mép sâu nhất trước khi bật lại ≥ 1 U) nằm trong vùng.
  - *Thắng 1:1, 1:2*: lệnh chờ ở mép gần, dừng lỗ dưới mép xa 0,1 U, mục tiêu 1 hoặc 2 lần rủi ro; một nến chạm cả hai ⇒ thua. Chưa phí, chưa trượt giá.
- **Đối chứng:** chính các vùng đó **dời đi 1,5–4 U** (dấu ngẫu nhiên, 3 bản mỗi vùng), cùng độ rộng, cùng bộ máy chấm. Khoảng 5–95 % của hiệu lấy mẫu lại theo khối ngày.

## 2. Kết quả chính — cấu hình chốt

Va đập: đỉnh/đáy cục bộ M30 (2 nến mỗi bên) bật lại ≥ 1 U trong 6 nến; cụm rộng ≤ 0,30 U, ≥ 3 lần trong 5 phiên đã đóng + phiên đang chạy; hợp lưu trong 0,10 U. `final_eval.py chot2`, `final_an.py chot2`.

| Nhóm | n TRAIN | đảo trong vùng | thắng 1:1 | R 1:2 | ΔR 1:2 so đối chứng [5–95 %] | n TEST | đảo trong vùng | thắng 1:1 | R 1:2 | ΔR 1:2 so đối chứng [5–95 %] |
|---|---|---|---|---|---|---|---|---|---|---|
| đối chứng (vùng dời) | 6329 | 16,0 % | 47,9 % | −0,008 | — | 5557 | 15,1 % | 47,5 % | −0,045 | — |
| mọi cụm ≥ 3 lần va đập | 2414 | 16,3 % | 48,9 % | −0,013 | [−0,07; +0,06] | 2229 | 15,1 % | 46,7 % | −0,032 | [−0,06; +0,09] |
| KHÔNG hợp lưu | 1203 | 15,3 % | 48,6 % | −0,009 | [−0,09; +0,08] | 1030 | 15,8 % | 44,2 % | −0,078 | [−0,13; +0,07] |
| hợp lưu ≥ 1 nhóm | 1211 | 17,3 % | 49,1 % | −0,016 | [−0,10; +0,09] | 1199 | 14,5 % | 48,8 % | +0,008 | [−0,04; +0,15] |
| **vùng ĐƯỢC VẼ** (sau lọc chồng, bán kính, trần) | 1050 | 17,4 % | 48,8 % | −0,021 | [−0,11; +0,09] | 1017 | 14,7 % | 47,2 % | −0,029 | [−0,08; +0,12] |
| hợp lưu ≥ 2 nhóm | 234 | 20,1 % | 55,1 % | +0,032 | [−0,15; +0,22] | 321 | 18,7 % | 52,6 % | +0,132 | [+0,01; +0,36] |
| có HVN đủ điều kiện | 294 | 16,0 % | 46,2 % | −0,173 | [−0,35; +0,02] | 399 | 16,8 % | 53,1 % | +0,157 | [+0,03; +0,36] |
| **VÀNG** (≥ 3 nhóm, có HVN) | 19 | 15,8 % | 75,0 % | −0,250 | n quá nhỏ | 41 | 22,0 % | 45,2 % | +0,161 | [−0,29; +0,66] |

Đọc bảng:
- Dòng "vùng ĐƯỢC VẼ" là thứ người dùng sẽ thấy: **không khác đối chứng**.
- "Có HVN": TRAIN âm, TEST dương ⇒ **trái dấu, là nhiễu**.
- "Hợp lưu ≥ 2 nhóm": cùng dấu dương, TEST vượt 0, TRAIN không ⇒ xem mục 7.
- Vùng vàng: 60 lần trong 2,3 năm; thắng 1:1 nhảy từ 75 % (TRAIN, 19 lần) xuống 45 % (TEST) cho thấy chỉ là dao động mẫu nhỏ.

## 3. Điểm đảo chiều nằm ở đâu so với vùng? (câu hỏi độ rộng)

`explore2.py`, cụm ≥ 2 lần va đập, rộng ≤ 0,5 U. Mỗi ô = % số lần quay lại có điểm đảo (bật ≥ 1 U) rơi vào khoảng bắt đầu từ mốc đó (rộng 0,15 U) tính từ **giữa cụm**; dương = quay đầu trước khi tới tâm, âm = đã xuyên qua tâm.

| Khoảng (×U) | −0,75 | −0,60 | −0,45 | −0,30 | −0,15 | 0,00 | +0,15 | +0,30 | +0,45 | +0,60 | xuyên quá −0,75 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TRAIN vùng thật (n = 4202) | 3,4 | 4,5 | 4,9 | 5,6 | 6,3 | 7,5 | 9,3 | 11,0 | 11,2 | 14,2 | 22,1 |
| TRAIN vùng dời (n = 11396) | 3,5 | 4,1 | 4,8 | 5,9 | 6,4 | 7,9 | 9,1 | 10,4 | 12,3 | 13,9 | 21,8 |
| TEST vùng thật (n = 3598) | 3,6 | 3,7 | 4,5 | 4,7 | 6,8 | 7,9 | 8,6 | 10,7 | 12,2 | 14,6 | 22,7 |
| TEST vùng dời (n = 9164) | 3,6 | 4,1 | 4,4 | 5,6 | 6,3 | 7,6 | 8,6 | 10,7 | 12,4 | 14,2 | 22,3 |

Nếu vùng va đập thật sự hút điểm đảo chiều thì quanh ô 0 phải có **đỉnh nhọn** mà vùng dời không có. Không có: hai phân phối trùng nhau, đều dốc đều từ ngoài vào (càng xa tâm càng nhiều, đơn giản vì giá tới đó trước). Đổi tâm sang mép cực của cụm, điểm va đập mới nhất, hay trung bình các điểm cũng cho cùng hình dạng. Với ngưỡng bật lại 0,5 U và 2 U cũng vậy.

Bảng độ rộng trên cấu hình chốt (`rong.py chot2`, vùng hợp lưu ≥ 1 nhóm, đặt vùng đối xứng nửa rộng h quanh tâm):

| Nửa rộng h (×U) | Cả vùng ≈ giá khi U = 13,4 | Vùng thật: % điểm đảo trong ±h | Vùng dời | Thật: % khớp lệnh ở mép gần | Thật: thắng 1:2 / R | Dời: thắng 1:2 / R |
|---|---|---|---|---|---|---|
| 0,05 | 1,3 | 5,2 | 4,9 | 76 | 33,7 % / +0,010 | 31,7 % / −0,049 |
| 0,10 | 2,7 | 9,4 | 9,4 | 78 | 32,3 % / −0,029 | 32,9 % / −0,011 |
| 0,15 | 4,0 | 13,2 | 14,0 | 79 | 31,5 % / −0,049 | 32,9 % / −0,011 |
| 0,20 | 5,4 | 18,6 | 18,8 | 82 | 33,0 % / +0,002 | 32,4 % / −0,020 |
| 0,25 | 6,7 | 23,3 | 23,5 | 83 | 33,6 % / +0,021 | 33,1 % / +0,001 |
| 0,30 | 8,0 | 28,0 | 28,3 | 85 | 33,1 % / +0,010 | 33,2 % / +0,007 |
| 0,40 | 10,7 | 38,4 | 38,1 | 88 | 32,4 % / +0,004 | 32,1 % / −0,004 |
| 0,50 | 13,4 | 50,1 | 48,4 | 92 | 33,1 % / +0,044 | 31,5 % / −0,001 |

- Muốn phủ **70 %** các điểm đảo nằm trong ±0,75 U quanh tâm cần nửa rộng **0,53 U** (vùng thật) — vùng dời cũng cần 0,55 U. Tức là "phủ 70–80 % điểm đảo" chỉ đạt được bằng vùng rộng ~1 U (13 giá năm 2026), và vùng ngẫu nhiên rộng cỡ đó cũng phủ được bấy nhiêu.
- **Chốt độ rộng theo rủi ro:** vùng = khoảng các điểm va đập (≤ 0,30 U) nới 0,05 U mỗi mép, tối thiểu 0,20 U. Thực tế vùng được vẽ rộng 0,26 / 0,36 / 0,41 U (p10 / trung vị / p90) ≈ **3,5 / 4,8 / 5,5 giá** khi U = 13,4; ≈ 2,6 / 3,6 / 4,1 giá khi U = 10. Hẹp hơn thì tỉ lệ khớp tụt mà kết quả không tốt lên; rộng hơn thì dừng lỗ vượt cỡ người dùng đang đi.

## 4. Mật độ trên chart (cấu hình chốt, `mat_do.py`, 26.746 nến M30)

- Trung bình **1,47 vùng** được vẽ; 0 vùng 34,7 % thời gian, 1 vùng 22,0 %, 2 vùng 17,5 %, 3 vùng 16,3 %, 4 vùng 7,0 %, ≥ 5 vùng 2,5 %.
- 65 % thời gian có ít nhất 1 vùng; trung bình 0,72 kháng cự + 0,67 hỗ trợ; giá đang nằm trong một vùng 7,8 % thời gian.
- **Vùng vàng có mặt 4,8 % thời gian.**
- Trước lọc hiển thị: 6,9 cụm đủ 3 lần va đập trên chart, 3,3 cụm có hợp lưu, 1,5 cụm trong bán kính 3 U. Cụm sát nhau rất hay gặp (một vùng giằng co 10–15 giá bị chia thành 3–4 cụm liền kề) ⇒ cần luật "hai vùng cách nhau dưới 0,15 U chỉ giữ vùng mạnh hơn".
- Nếu hạ xuống ≥ 2 lần va đập (cụm ≤ 0,35 U): 13,8 cụm, 5,7 có hợp lưu, 17,5 % thời gian có hơn 4 vùng trong 3 U — rối, và kết quả không tốt hơn (mục 7).

## 5. Từng mức hợp lưu đứng một mình (không cần va đập)

`explore3.py`. Vùng thử = mức ± 0,25 U, dừng lỗ thêm 0,15 U. Đối chứng: thắng 1:1 49,5 % / 49,2 %, R 1:2 −0,015 / −0,006.

| Mức | n TRAIN | thắng 1:1 | R 1:2 | ΔR 1:2 [5–95 %] | n TEST | thắng 1:1 | R 1:2 | ΔR 1:2 [5–95 %] |
|---|---|---|---|---|---|---|---|---|
| VWAP hôm qua | 570 | 54,7 % | +0,088 | [−0,04; +0,24] | 439 | 50,6 % | +0,008 | [−0,13; +0,16] |
| VWAP hôm qua +1σ | 541 | 52,9 % | +0,020 | [−0,08; +0,17] | 433 | 50,0 % | +0,013 | [−0,14; +0,19] |
| VWAP hôm qua −1σ | 466 | 48,2 % | −0,098 | [−0,21; +0,06] | 435 | 56,5 % | +0,126 | [−0,00; +0,28] |
| VWAP tuần trước | 217 | 49,5 % | −0,066 | [−0,22; +0,11] | 218 | 52,2 % | +0,187 | [−0,04; +0,41] |
| VWAP tuần trước +1σ | 211 | 46,4 % | −0,070 | [−0,26; +0,13] | 175 | 48,2 % | +0,095 | [−0,14; +0,33] |
| VWAP tuần trước −1σ | 159 | 43,7 % | −0,167 | [−0,38; +0,13] | 209 | 49,1 % | +0,027 | [−0,18; +0,21] |
| VAH hôm qua | 533 | 48,6 % | −0,004 | [−0,12; +0,14] | 405 | 50,3 % | +0,149 | [−0,01; +0,34] |
| VAL hôm qua | 474 | 50,8 % | −0,080 | [−0,20; +0,09] | 453 | 57,0 % | +0,076 | [−0,05; +0,23] |
| VAH tuần trước | 202 | 44,2 % | −0,155 | [−0,32; +0,04] | 151 | 47,1 % | −0,096 | [−0,33; +0,16] |
| VAL tuần trước | 194 | 54,8 % | +0,237 | [+0,03; +0,50] | 183 | 49,0 % | +0,062 | [−0,17; +0,29] |
| HVN ngày (5 phiên gần nhất) | 1059 | 48,9 % | +0,038 | [−0,06; +0,18] | 1514 | 50,0 % | +0,026 | [−0,06; +0,13] |
| HVN tuần | 535 | 43,5 % | −0,021 | [−0,15; +0,14] | 579 | 50,0 % | +0,056 | [−0,08; +0,21] |

Không mức nào vượt đối chứng ở **cả** TRAIN lẫn TEST. Mức nào dương ở nửa này thì ở nửa kia về 0 hoặc đổi dấu.

Tiêu chí HVN người dùng nêu (dải HVN ở bảng này = 70 % đỉnh đã làm mượt):

| HVN ngày | n TRAIN | R 1:2 | n TEST | R 1:2 |
|---|---|---|---|---|
| profile hình chữ D | 319 | −0,007 | 472 | −0,041 |
| profile không phải chữ D | 740 | +0,057 | 1042 | +0,056 |
| là POC của ngày | 789 | +0,098 | 823 | +0,032 |
| không phải POC | 270 | −0,128 | 691 | +0,020 |
| giá đã rời xa ≥ 3 U | 449 | +0,016 | 554 | +0,090 |
| rời xa < 3 U | 610 | +0,055 | 960 | −0,011 |
| của hôm qua | 372 | +0,244 | 448 | −0,050 |
| của 2–5 ngày trước | 687 | −0,078 | 1066 | +0,058 |
| HVN tuần: tuần trước | 237 | +0,040 | 275 | +0,172 |
| HVN tuần: tuần này (tới hết hôm qua) | 298 | −0,066 | 304 | −0,047 |

- **Chữ D không giúp** (còn hơi kém hơn, trong sai số). "Giá đã rời xa" không tách được. "HVN của hôm qua" đẹp ở TRAIN rồi mất ở TEST.
- 47 % số phiên có profile đạt định nghĩa chữ D dùng trong spec (POC nằm trong 30–70 % biên độ ngày và vùng giá trị ≤ 60 % biên độ). Ở bảng trên ngưỡng vùng giá trị là ≤ 50 % (vòng thăm dò đầu).
- Lưu ý với phép đo cũ: `ZonePolicy` xếp HVN vào vai "đi tiếp / mục tiêu, không fade". Yêu cầu mới dùng HVN làm hợp lưu cho vùng đảo chiều — số liệu ở đây **không ủng hộ cũng không bác** (ngang đối chứng).

## 6. Vùng bị phá, đúng vai, tuổi vùng (cấu hình chốt, vùng hợp lưu ≥ 1)

| Lát cắt | n TRAIN | thắng 1:1 | R 1:2 | n TEST | thắng 1:1 | R 1:2 |
|---|---|---|---|---|---|---|
| chưa lần nào bị nến M30 đóng xuyên hẳn | 34 | 44,8 % | −0,069 | 37 | 32,3 % | −0,226 |
| bị xuyên 1 lần | 76 | 50,0 % | +0,031 | 63 | 33,9 % | −0,518 |
| bị xuyên ≥ 2 lần | 1101 | 49,2 % | −0,018 | 1099 | 50,3 % | +0,050 |
| đúng vai (vd toàn đáy, giá từ trên xuống) | 284 | 49,1 % | +0,069 | 244 | 49,0 % | +0,017 |
| lẫn cả đỉnh lẫn đáy | 762 | 47,9 % | −0,070 | 847 | 48,6 % | −0,004 |
| đổi vai (vd toàn đỉnh cũ, nay giá từ trên xuống) | 165 | 54,8 % | +0,095 | 108 | 50,0 % | +0,076 |
| điểm va đập mới nhất ≤ 12 giờ | 601 | 48,3 % | −0,023 | 602 | 44,9 % | −0,064 |
| điểm va đập mới nhất > 12 giờ | 610 | 49,9 % | −0,009 | 597 | 52,5 % | +0,076 |

- **91 % lần quay lại là vào vùng đã bị giá đóng nến xuyên qua ít nhất 2 lần** kể từ lần va đập đầu — vì cụm thường gồm cả đỉnh lẫn đáy (giá đi qua lại). Vùng "nguyên, chưa bị phá" rất hiếm (71 lần) và không tốt hơn (TEST còn tệ hơn). ⇒ **không ẩn vùng khi bị phá**; vùng chỉ đổi màu theo phía giá.
- Đúng vai / đổi vai / tuổi vùng: không lát nào vượt đối chứng ở cả hai nửa. Không thêm lọc nào trong số này vào spec.

## 7. Độ bền qua biến thể (R ở 1:2; trong ngoặc vuông là khoảng 5–95 % của hiệu so với đối chứng)

| Biến thể | Vùng hợp lưu ≥ 1: TRAIN | TEST | Hợp lưu ≥ 2 nhóm: TRAIN (n) | TEST (n) | Vàng: n TRAIN / TEST |
|---|---|---|---|---|---|
| **chốt** (cụm ≤ 0,30 U, ≥ 3 lần, 5 phiên) | −0,016 | +0,008 | +0,032 (234) [−0,15; +0,22] | +0,132 (321) [+0,01; +0,36] | 19 / 41 |
| cụm ≤ 0,35 U | +0,015 | +0,057 | +0,135 (272) [−0,03; +0,30] | +0,194 (354) [+0,01; +0,39] | 21 / 52 |
| cụm ≤ 0,25 U | −0,053 | −0,014 | −0,010 (198) [−0,20; +0,23] | +0,191 (275) [+0,06; +0,43] | 20 / 32 |
| cụm ≤ 0,50 U | +0,001 | +0,026 | +0,002 (409) [−0,16; +0,12] | +0,183 (449) [+0,06; +0,35] | 38 / 69 |
| ≥ 2 lần va đập (cụm ≤ 0,35 U) | −0,009 | +0,019 | +0,051 (433) [−0,06; +0,22] | +0,109 (508) [−0,04; +0,28] | 35 / 70 |
| nhìn lại 10 phiên (cụm ≤ 0,35 U) | +0,006 | +0,001 | +0,097 (388) [−0,05; +0,24] | +0,090 (471) [−0,07; +0,26] | 25 / 68 |
| bật lại ≥ 1,5 U (cụm ≤ 0,35 U) | +0,023 | −0,034 | +0,099 (161) [−0,12; +0,35] | −0,044 (207) [−0,31; +0,20] | 12 / 22 |
| nhận mọi HVN, không cần chữ D (cụm ≤ 0,35 U) | +0,024 | +0,029 | +0,043 (426) [−0,09; +0,19] | +0,149 (598) [+0,02; +0,29] | 99 / 145 |

Đối chứng ở mọi biến thể nằm trong −0,05…+0,02.

- Vùng hợp lưu ≥ 1: quanh 0 ở mọi biến thể ⇒ **kết luận "không có lợi thế" không phụ thuộc cách chọn thông số**.
- Hợp lưu ≥ 2 nhóm: R dương ở 14/16 ô, nhưng các biến thể dùng chung phần lớn sự kiện (không phải 16 phép thử độc lập), TRAIN chưa lần nào tách khỏi 0, và đã soi hàng chục lát cắt trước khi thấy lát này. **Trạng thái: giả thuyết, chưa kiểm định.** Cách kiểm đúng: giữ nguyên định nghĩa, đợi dữ liệu mới (≥ 3 tháng sau 2026-11-09) rồi đo lại một lần.
- Bỏ điều kiện chữ D làm vùng vàng nhiều gấp ~3 lần (244 so với 73 lần ở cùng bề rộng cụm) nhưng thắng 1:1 của vùng vàng vẫn trái chiều giữa hai nửa (TRAIN 64,3 %, TEST 45,9 %).

## 8. Ghi chú kỹ thuật

- **VWAP và ±1σ** tính từ khối lượng từng mức giá (chính xác, không phụ thuộc khung). So với cách cũ `VwapAt` (giá điển hình nến M30): VWAP lệch trung vị 0,21 giá (p90 0,82), σ lệch trung vị 0,62 giá trên σ trung vị 18,9 giá (80 phiên cuối).
- **VAH hôm qua và VWAP hôm qua +1σ gần như cùng một mức** do cấu tạo (vùng giá trị 70 % ≈ ±1σ). Nếu đếm thành hai mức thì "hợp lưu ≥ 3 có HVN" gần như chỉ còn là "HVN nằm cạnh VAH". Spec gộp chúng thành một nhóm; đây là chỗ **lệch với cách đếm theo chữ của người dùng** — cần người dùng chốt. Trong 3 tuần fixture (689 nến M30): có ít nhất một cụm vàng ở 42 nến khi gộp, 131 nến khi đếm theo chữ.
- Điểm va đập: 5.941 điểm trong 589 phiên (≈ 10/phiên), xác nhận trễ trung bình 2,15 nến M30.
- Dải HVN: `PeakSharpness` 90 % trên khối lượng thô (hàm sẵn có) cho dải 0,4–4 giá; dải 70 % trên phân bố đã làm mượt rộng trung vị 0,6 U (8 giá) — quá rộng để làm mức hợp lưu nên không dùng trong spec.

## 9. Giới hạn

- Chấm bằng lệnh chờ ở mép vùng, chưa phí, chưa trượt giá; "một nến M1 chạm cả hai mốc = thua" kéo số tuyệt đối xuống dưới 50 % / 33 %. Chỉ so tương đối với đối chứng.
- Không dùng tín hiệu order flow lúc giá vào vùng (hấp thụ, delta). Phép đo này trả lời "vùng tự nó có giữ giá không", **không** trả lời "vùng + xác nhận order flow có lợi thế không".
- Nhiều lần quay lại cùng một vùng và các vùng liền kề không độc lập; khoảng tin cậy theo khối ngày đã bù một phần.
- Mã liên tục trước 2025-03 không thấy bước nhảy ≥ 9 giá ở giờ nghỉ (README ghi 11 chỗ nối, ở đây bắt được 9 với ngưỡng 20 giá) — có thể còn chỗ nối nhỏ chưa lọc trong TRAIN.
- TEST gồm cả giai đoạn biên độ rất lớn (U tới 51 giá đầu 2026); kết quả tính theo U nên so được, nhưng chưa tách riêng theo chế độ biến động.
- Lọc hiển thị (chồng vùng, bán kính, trần) được thêm sau các biến thể ở mục 7; chỉ dòng "vùng ĐƯỢC VẼ" ở mục 2 đã tính đủ lọc này.

## 10. File

| File | Việc |
|---|---|
| `prep.py` | nạp CSV → bộ đệm M1/M30/khối lượng từng mức giá (đặt biến môi trường `VM_CACHE` để chọn chỗ lưu) |
| `vm.py` | lõi: phiên, tuần, chỗ nối, U, profile, vùng giá trị, HVN, điểm va đập |
| `vung_manh.py` | **bản tham chiếu của spec** (mức hợp lưu, vùng, lọc hiển thị, nhãn) |
| `final_eval.py`, `final_an.py` | chạy bản tham chiếu trên toàn bộ dữ liệu + bảng mục 2, 6, 7 |
| `rong.py`, `mat_do.py` | bảng độ rộng (mục 3), mật độ (mục 4) |
| `events.py`, `an.py`, `explore1.py`–`explore3.py`, `info.py` | vòng thăm dò đầu (mục 1, 3, 5) |
| `parity_cases.py` → `fixture/` | dữ liệu + kết quả kỳ vọng để so C# = Python |

Chạy lại: `python prep.py` → `python final_eval.py chot2` → `python final_an.py chot2 x` → `python rong.py chot2` → `python mat_do.py` → `python parity_cases.py`.
