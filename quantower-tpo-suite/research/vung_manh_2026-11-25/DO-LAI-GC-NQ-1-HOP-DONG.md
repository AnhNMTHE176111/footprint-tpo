# Vùng mạnh — đo lại trên MỘT hợp đồng, GC và NQ (Fable, 2026-11-25)

Đo lần đầu (2,3 năm, phần lớn là mã liên tục): [`DO-VUNG-MANH.md`](DO-VUNG-MANH.md). Spec: [`../../PLAN-VUNG-MANH.md`](../../PLAN-VUNG-MANH.md).
Lần này: **thông số mặc định của spec, không chỉnh gì**, cách chấm và đối chứng y như cũ, chỉ đổi dữ liệu.

## 0. Kết luận trước

1. **Dữ liệu sạch.** Trong phần dùng để đo (GCZ26 và NQZ26 khi đã là hợp đồng chính): 0 nến volume 0, 0 nến thiếu khối lượng theo giá, tổng khối lượng theo giá = volume nến ở 100 % số nến, không có lỗ thời gian nào trong phiên. File 2,3 năm (agent chính kiểm): cũng không tháng nào có nến volume 0 hay nến thiếu khối lượng theo giá.
2. **GC một hợp đồng cho cùng kết luận với 2,3 năm: vùng được vẽ ngang đối chứng.** Thắng 1:1 **49,3 %** so với đối chứng 48,8 %; R ở 1:2 −0,02 so với −0,06; khoảng 5–95 % của hiệu chứa 0 rộng rãi.
3. **Mã liên tục không làm sai kết quả cũ.** Cắt đúng kỳ này ra khỏi lần chạy 2,3 năm: 324 lần quay lại, thắng 47,8 %, R 1:2 −0,02 — gần trùng với lần chạy một hợp đồng (314 lần, 49,3 %, −0,02).
4. **NQ: vùng được vẽ nhỉnh hơn đối chứng ở R 1:2 (+0,26 so với −0,01), nhưng chưa đủ để gọi là lợi thế.** Chỉ 165 lần quay lại trong 42 phiên; thắng 1:1 50,7 % so với 46,5 % (khoảng 5–95 % của hiệu: −3,8 đến +12,3 điểm %, chứa 0); khoảng của ΔR 1:2 chạm đúng 0 ([+0,00; +0,50]). Trên GC, từng quý riêng lẻ cũng có lệch cỡ này theo cả hai chiều (mục 4). **Trạng thái: chưa kiểm định**, đo lại khi có thêm ≥ 3 tháng NQ.
5. **Vùng vàng: không nói được gì** — 8 lần trên GC, 4 lần trên NQ.
6. **Độ rộng / dung sai theo U dùng được nguyên cho NQ** — không đề xuất đổi (mục 5).
7. **Có một chỗ cần sửa cho NQ, không thuộc thông số vùng:** bộ phát hiện "chỗ nối hợp đồng" bắt nhầm khoảng trống giá thật qua giờ nghỉ ngày — 3 lần trong 11 tuần NQ, làm tháng 11 mất gần nửa số vùng (mục 6).

## 1. Dữ liệu

| | GC | NQ |
|---|---|---|
| File | `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (tới 10-21) + `…20260811-20261109_90d` (từ 10-21) | `fp_NQZ26_XCME_Time_20260826-20261124_90d` |
| Kỳ đo | 2026-07-28 22:00 → 2026-11-09 08:00 UTC | 2026-09-13 22:00 → 2026-11-24 12:00 UTC |
| Phiên / tuần | 74 / 16 | 52 / 11 |
| Nến M1 → M30 | 100.124 → 3.372 | 71.167 → 2.373 |
| Chỗ nối hợp đồng thật | 0 (một hợp đồng) | 0 (một hợp đồng) |

Phần bị bỏ, và lý do:
- **GCZ26 trước 2026-07-28 22:00** (4 phiên): hợp đồng chưa là hợp đồng chính, 2.672–21.081 hợp đồng/phiên (bình thường ~135.000), có 28 lỗ 6–12 phút. Dữ liệu đúng nhưng mỏng.
- **NQZ26 trước 2026-09-13 22:00** (15 phiên): cùng lý do, 4–33.346 hợp đồng/phiên (bình thường ~500.000), 578 lỗ 6–55 phút.
- **`fp_GCZ26_XCEC_Time_20261108-20261118_9d16h`: là nến M5** (276 nến/phiên), không phải M1 → không ghép vào chuỗi chấm bằng M1 được. GC vì vậy dừng ở 2026-11-09.
- File NQ `…_8d13h` không cần: file 90 ngày đã phủ tới 2026-11-24.

### Chất lượng theo tháng (phần dùng để đo, nến M1) — `prep1.py`

**GC**

| Tháng | nến M1 | volume = 0 | không có khối lượng theo giá | tổng theo giá ≠ volume nến | số mức giá ≠ cột `levels` | lỗ 6–55 phút trong phiên | phiên | hợp đồng/phiên: thấp nhất / trung vị |
|---|---|---|---|---|---|---|---|---|
| 2026-07 | 4.137 | 0 | 0 | 0 | 0 | 0 | 3 | 101.780 / 113.757 |
| 2026-08 | 28.674 | 0 | 0 | 0 | 0 | 0 | 22 | 85.940 / 135.569 |
| 2026-09 | 29.785 | 0 | 0 | 0 | 0 | 0 | 22 | 66.305 / 145.348 |
| 2026-10 | 30.121 | 0 | 0 | 0 | 0 | 0 | 21 | 95.939 / 130.469 |
| 2026-11 | 7.407 | 0 | 0 | 0 | 0 | 0 | 6 | 46.070 / 149.845 |

**NQ**

| Tháng | nến M1 | volume = 0 | không có khối lượng theo giá | tổng theo giá ≠ volume nến | số mức giá ≠ cột `levels` | lỗ 6–55 phút trong phiên | phiên | hợp đồng/phiên: thấp nhất / trung vị |
|---|---|---|---|---|---|---|---|---|
| 2026-09 | 18.059 | 0 | 0 | 0 | 0 | 0 | 14 | 341.924 / 525.806 |
| 2026-10 | 30.240 | 0 | 0 | 0 | 0 | 0 | 21 | 444.622 / 653.958 |
| 2026-11 | 22.868 | 0 | 0 | 0 | 0 | 0 | 17 | 161.492 / 848.759 |

- Cũng bằng 0 ở cả hai mã: nến có OHLC mâu thuẫn, giá lệch bước giá, nến trùng giờ.
- Phiên đủ dài: trung vị 1.377–1.380 nến M1/phiên (tối đa 1.380). Hai giá trị "thấp nhất" ở tháng 11 là phiên cuối file đang chạy dở.
- Khoảng nghỉ: GC 57 lần nghỉ ngày 60 phút + 15 cuối tuần + 1 lần 211 phút (2026-09-07, Labor Day). NQ 41 lần nghỉ ngày + 10 cuối tuần, không có gì khác. Nghỉ ngày rơi 21:00–22:00 UTC, từ 2026-11-02 là 22:00–23:00 UTC (Mỹ hết giờ mùa hè) — ở cả hai mã.
- **Tách phiên / tuần trên NQ vẫn đúng** với ngưỡng cũ (nghỉ > 75 phút = phiên mới, > 30 giờ = tuần mới): NQ nghỉ cùng giờ với GC, 46 nến M30/phiên, không phiên nào dưới 20 nến.
- Lưu ý khi đọc "volume = 0: không có": file export chỉ ghi nến có giao dịch, nên phép kiểm có nghĩa hơn là **lỗ thời gian** và **tổng khối lượng theo giá khớp volume nến** — cả hai đều sạch.

### Thứ buộc phải đổi cho NQ (và chỉ những thứ này)

| | GC | NQ | Ghi chú |
|---|---|---|---|
| Bước giá | 0,1 | 0,25 | |
| Hàng profile (`RowTicks` = 2) | 0,2 giá | 0,5 điểm | đúng như C# sẽ tính, kể cả cách làm tròn của `Snap` (mục 7) |
| Ngưỡng chỗ nối | 20 giá | 50 điểm (= `MinSpliceJumpPrices × 10 × tick`) | chạy hai bản: **để nguyên** (đúng indicator hiện tại) và **tắt** (đúng với dữ liệu một hợp đồng) |
| Mọi thông số vùng (R, WC, PAD, WMIN, TOL, …) | theo U | theo U, giữ nguyên | |

`vm.py` viết cứng bước giá 0,1; để không sửa bản tham chiếu, `prep1.py` chia giá NQ cho 2,5 khi lưu — tương đương hoàn toàn vì mọi ngưỡng tính theo U hoặc theo số bước giá.

## 2. Kết quả — cả kỳ (`do_lai.py bang gc`, `do_lai.py bang nq tatnoi`)

Thắng 1:1, R 1:2: lệnh chờ ở mép gần, dừng lỗ dưới mép xa 0,1 U, chưa phí, chưa trượt giá. Đối chứng: chính các vùng đó dời 1,5–4 U. Ngoặc vuông: khoảng 5–95 % của hiệu so với đối chứng, lấy mẫu lại theo khối ngày.

**GC — 71 phiên có sự kiện**

| Nhóm | n | đảo trong vùng | thắng 1:1 | Δ thắng 1:1 (điểm %) | thắng 1:2 | R 1:2 | ΔR 1:2 |
|---|---|---|---|---|---|---|---|
| đối chứng (vùng dời) | 1.817 | 14,8 % | 48,8 % | — | 31,0 % | −0,063 | — |
| mọi cụm ≥ 3 lần va đập | 687 | 14,7 % | 48,0 % | [−5,3; +3,6] | 33,0 % | −0,004 | [−0,06; +0,18] |
| KHÔNG hợp lưu | 321 | 14,6 % | 45,2 % | [−10,3; +2,3] | 33,5 % | +0,005 | [−0,11; +0,23] |
| hợp lưu ≥ 1 nhóm | 366 | 14,8 % | 50,5 % | [−4,9; +7,6] | 32,6 % | −0,012 | [−0,13; +0,23] |
| **vùng ĐƯỢC VẼ** | 314 | 15,6 % | **49,3 %** | [−6,8; +7,2] | 32,3 % | −0,018 | [−0,15; +0,25] |
| hợp lưu ≥ 2 nhóm | 97 | 22,7 % | 51,8 % | [−8,3; +13,7] | 35,7 % | +0,090 | [−0,16; +0,45] |
| có HVN đủ điều kiện | 104 | 18,3 % | 51,2 % | [−9,2; +13,2] | 35,3 % | +0,078 | [−0,24; +0,47] |
| **VÀNG** | 8 | 0 % | 33 % (6 lệnh) | n nhỏ | 0 % | −1,000 | n nhỏ |

**NQ, tắt phát hiện chỗ nối — 42 phiên có sự kiện**

| Nhóm | n | đảo trong vùng | thắng 1:1 | Δ thắng 1:1 (điểm %) | thắng 1:2 | R 1:2 | ΔR 1:2 |
|---|---|---|---|---|---|---|---|
| đối chứng (vùng dời) | 979 | 15,1 % | 46,5 % | — | 32,8 % | −0,011 | — |
| mọi cụm ≥ 3 lần va đập | 340 | 15,3 % | 47,2 % | [−5,3; +7,6] | 35,3 % | +0,064 | [−0,09; +0,26] |
| KHÔNG hợp lưu | 163 | 13,5 % | 44,3 % | [−8,7; +5,8] | 29,5 % | −0,107 | [−0,28; +0,12] |
| hợp lưu ≥ 1 nhóm | 177 | 16,9 % | 50,0 % | [−3,8; +11,8] | 41,0 % | +0,230 | [+0,02; +0,47] |
| **vùng ĐƯỢC VẼ** | 165 | 17,6 % | **50,7 %** | [−3,8; +12,3] | 41,8 % | +0,255 | [+0,00; +0,50] |
| hợp lưu ≥ 2 nhóm | 48 | 22,9 % | 47,5 % | [−11,6; +12,5] | 47,5 % | +0,425 | [+0,06; +0,78] |
| có HVN đủ điều kiện | 38 | 21,1 % | 37,5 % | [−19,6; +2,4] | 37,5 % | +0,125 | [−0,17; +0,46] |
| **VÀNG** | 4 | 25 % | 25 % (4 lệnh) | n nhỏ | 25 % | −0,250 | n nhỏ |

NQ để nguyên ngưỡng chỗ nối (đúng indicator hiện tại): vùng được vẽ 146 lần, thắng 1:1 50,4 % (đối chứng 47,5 %), R 1:2 +0,258 (đối chứng +0,029), ΔR [−0,03; +0,50]. Cùng hình dạng, ít mẫu hơn.

Đọc bảng:
- **GC:** mọi dòng đủ mẫu đều có khoảng chứa 0. Không khác đối chứng.
- **NQ:** phần hơn nằm ở R 1:2, không nằm ở tỉ lệ thắng 1:1. Hai dòng liên quan nhau lại trái chiều: "hợp lưu ≥ 2 nhóm" R 1:2 +0,43 nhưng thắng 1:1 chỉ 47,5 %; "có HVN" thắng 1:1 37,5 %, thấp hơn đối chứng. Một hiệu ứng thật thường không cho hình như vậy.
- Sai số riêng của tỉ lệ thắng: GC 268 lệnh ⇒ ± 5 điểm %; NQ 134 lệnh ⇒ ± 7 điểm % (mức 90 %).
- "Hợp lưu ≥ 2 nhóm" — giả thuyết ghi lại từ lần trước: GC R 1:2 +0,09 (97 lần), NQ +0,43 (48 lần). Cùng dấu dương nhưng **cả hai đều chưa tách khỏi nhiễu** ở mẫu cỡ này; chưa đổi trạng thái "giả thuyết".

## 3. Theo tháng (vùng được vẽ so với đối chứng)

**GC**

| Tháng | phiên | vẽ: n | thắng 1:1 | R 1:2 | đối chứng: n | thắng 1:1 | R 1:2 | ≥ 2 nhóm: n | thắng 1:1 | vàng: n |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08 | 22 | 63 | 48,3 % | −0,172 | 345 | 42,7 % | −0,244 | 27 | 44,0 % | 4 |
| 2026-09 | 22 | 96 | 43,8 % | −0,257 | 579 | 43,8 % | −0,171 | 33 | 37,9 % | 3 |
| 2026-10 | 22 | 146 | 52,8 % | +0,168 | 822 | 56,3 % | +0,129 | 37 | 71,0 % | 1 |
| 2026-11 | 6 | 9 | 57,1 % | +0,714 | 71 | 31,1 % | −0,534 | 0 | — | 0 |
| **gộp** | 71 | 314 | 49,3 % | −0,018 | 1.817 | 48,8 % | −0,063 | 97 | 51,8 % | 8 |

**NQ (tắt phát hiện chỗ nối)**

| Tháng | phiên | vẽ: n | thắng 1:1 | R 1:2 | đối chứng: n | thắng 1:1 | R 1:2 | ≥ 2 nhóm: n | thắng 1:1 | vàng: n |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09 | 8 | 43 | 50,0 % | +0,167 | 216 | 51,6 % | +0,219 | 17 | 50,0 % | 3 |
| 2026-10 | 19 | 90 | 50,0 % | +0,292 | 516 | 47,1 % | +0,023 | 26 | 45,0 % | 1 |
| 2026-11 | 16 | 32 | 53,8 % | +0,274 | 247 | 41,0 % | −0,286 | 5 | 50,0 % | 0 |
| **gộp** | 42 | 165 | 50,7 % | +0,255 | 979 | 46,5 % | −0,011 | 48 | 47,5 % | 4 |

- Vùng thật và đối chứng **lên xuống cùng nhau** theo tháng (GC tháng 10 cả hai cùng tốt, tháng 9 cả hai cùng xấu): cái đổi là thị trường tháng đó, không phải vùng.
- Mỗi ô tháng chỉ 9–146 lần; tháng 11 của GC (9 lần) không đọc được.
- Tháng đầu của mỗi mã ít phiên hơn lịch vì cần ~7 phiên khởi động (U, 5 phiên nhìn lại, tuần trước).

## 4. So với kết quả 2,3 năm (`do_lai.py full`)

Chạy lại nguyên lần đo cũ (16.529 sự kiện, trùng số cũ) rồi cắt.

| Vùng ĐƯỢC VẼ, GC | n | thắng 1:1 | đối chứng | R 1:2 | đối chứng |
|---|---|---|---|---|---|
| 2,3 năm, tất cả | 2.067 | 48,1 % | 47,7 % | −0,025 | −0,025 |
| 2,3 năm, TEST (từ 2025-11) | 1.017 | 47,2 % | 47,5 % | −0,029 | −0,045 |
| 2,3 năm, cắt riêng từ 2026-07-28 | 324 | 47,8 % | 44,6 % | −0,021 | −0,112 |
| **một hợp đồng, từ 2026-07-28** | 314 | 49,3 % | 48,8 % | −0,018 | −0,063 |

- Hai dòng cuối là cùng một kỳ, tính bằng hai chuỗi dữ liệu: **vùng thật gần như trùng** (324 so với 314 lần; chênh do vài phiên khởi động). Chỗ nối hợp đồng trong chuỗi 2,3 năm không rò vào kết quả.
- Đối chứng của cùng kỳ đó lại lệch 4 điểm % (44,6 % so với 48,8 %) chỉ vì bốc ngẫu nhiên khác nhau. Đó là **cỡ nhiễu của một kỳ 3 tháng** — mọi chênh lệch dưới ~5 điểm % ở mục 2–3 nằm trong nhiễu này.

Từng quý của 2,3 năm, vùng được vẽ:

| Quý | n | thắng 1:1 | đối chứng | R 1:2 | đối chứng |
|---|---|---|---|---|---|
| 2024 Q3 | 156 | 46,2 % | 46,2 % | +0,000 | −0,082 |
| 2024 Q4 | 230 | 42,9 % | 49,1 % | −0,127 | −0,010 |
| 2025 Q1 | 236 | 47,7 % | 48,4 % | −0,002 | +0,026 |
| 2025 Q2 | 208 | 51,1 % | 47,1 % | −0,055 | −0,046 |
| 2025 Q3 | 177 | 57,7 % | 48,0 % | +0,117 | −0,008 |
| 2025 Q4 | 223 | 52,2 % | 50,0 % | +0,162 | +0,121 |
| 2026 Q1 | 221 | 41,0 % | 50,0 % | −0,176 | +0,017 |
| 2026 Q2 | 226 | 49,7 % | 48,2 % | −0,017 | −0,085 |
| 2026 Q3 | 235 | 42,3 % | 43,2 % | −0,246 | −0,146 |
| 2026 Q4 (tới 11-09) | 155 | 53,1 % | 47,2 % | +0,198 | −0,049 |

Một quý riêng lẻ lệch khỏi đối chứng từ **−9 đến +10 điểm %** và ΔR 1:2 từ −0,19 đến +0,25, cả hai chiều, trong khi gộp lại bằng 0. Kết quả NQ (+4 điểm %, ΔR +0,27 trên 2,5 tháng) nằm ở mép trên của dải này — chưa phân biệt được với một quý may.

## 5. Mật độ và độ rộng — thông số theo U có hợp với NQ không?

| | GC 2,3 năm | GC một hợp đồng | NQ (tắt chỗ nối) | NQ (để nguyên) |
|---|---|---|---|---|
| U trung vị (p10–p90) | 13,4 giá (năm 2026) | 11,9 giá (9,9–13,8) | 75,9 điểm (53–122) | như bên |
| U / giá | — | 0,28 % | 0,26 % | |
| Điểm va đập / phiên | ≈ 10 | 10,5 | 10,3 | 10,2 |
| Khoảng va đập của cụm (×U) p10 / 50 / 90 | — | 0,14 / 0,24 / 0,29 | 0,15 / 0,24 / 0,29 | |
| Cụm ≥ 3 lần trên chart | 6,9 | 7,8 | 6,6 | 5,7 |
| % cụm có hợp lưu ≥ 1 / ≥ 2 nhóm | 48 / — | 48 / 12 | 45 / 11 | 45 / 11 |
| **Vùng được vẽ, trung bình** | 1,47 | 1,78 | 1,22 | 1,07 |
| % thời gian có ≥ 1 vùng | 65 % | 71 % | 57 % | 48 % |
| % thời gian có > 4 vùng | 2,5 % | 4,3 % | 3,4 % | 3,4 % |
| Giá đang trong vùng | 7,8 % | 9,5 % | 5,5 % | 5,2 % |
| % thời gian có vùng vàng | 4,8 % | 6,9 % | 6,0 % | 6,0 % |
| Số vùng khác nhau được vẽ trong một phiên (TB / trung vị) | — | 3,9 / 4 | 2,7 / 2 | 2,4 / 1 |
| Lần quay lại vùng được vẽ / phiên | 3,8 | 4,4 | 3,9 | 3,8 |
| **Bề rộng vùng được vẽ (×U) p10 / 50 / 90** | 0,26 / 0,36 / 0,41 | 0,26 / 0,35 / 0,40 | 0,28 / 0,36 / 0,40 | 0,27 / 0,37 / 0,40 |
| Bề rộng trung vị theo giá thật | 4,8 giá | 4,2 giá | 27 điểm | |

Câu hỏi "điểm đảo chiều có tụ về vùng không" (nửa rộng cần để phủ 70 % điểm đảo trong ± 0,75 U quanh tâm): GC thật 0,57 U / dời 0,56 U; NQ thật 0,50 U / dời 0,55 U. Như lần trước: vùng thật không hút điểm đảo rõ hơn vùng dời, nên **không có độ rộng nào "đúng hơn"** — vẫn chọn theo rủi ro.

**Kết luận cho mục 3 của đề bài: giữ nguyên `SzClusterU` 0,30, PAD 0,05, WMIN 0,20, `SzConfluenceTolU` 0,10 cho NQ.** Tính theo U, hình dạng trên NQ trùng GC: cùng số điểm va đập mỗi phiên, cùng bề rộng cụm, cùng bề rộng vùng, cùng tỉ lệ cụm có hợp lưu. Vùng NQ rộng 15–49 điểm tuỳ biên độ (trung vị 27).

NQ ít vùng hơn GC (1,2 so với 1,8) nhưng trong kỳ này GC cũng nhiều hơn chính mức 2,3 năm của nó (1,47); chênh lệch nằm ở số cụm, không ở dung sai. Độ nhạy (chỉ để xem, **không** chọn lại):

| TOL | WC | GC: vùng vẽ TB / % có vùng / % có vàng | NQ: vùng vẽ TB / % có vùng / % có vàng |
|---|---|---|---|
| 0,05 | 0,30 | 1,56 / 66 / 2,9 | 1,07 / 56 / 6,0 |
| **0,10** | **0,30** | **1,78 / 71 / 6,9** | **1,22 / 57 / 6,0** |
| 0,15 | 0,30 | 1,94 / 71 / 8,9 | 1,33 / 59 / 6,4 |
| 0,20 | 0,30 | 2,04 / 75 / 10,0 | 1,45 / 60 / 7,6 |
| 0,10 | 0,20 | 1,38 / 61 / 4,1 | 0,68 / 38 / 4,4 |
| 0,10 | 0,40 | 2,01 / 76 / 10,6 | 1,49 / 64 / 8,8 |

Đổi TOL hay WC chỉ dịch mật độ từ từ, không có điểm gãy nào gợi ý NQ cần số khác.

Một khác biệt cấu tạo, **ghi nhận, chưa đề xuất đổi**: HVN không tự co giãn theo U vì tính theo số hàng (hàng = 2 bước giá).

| HVN ngày | GC | NQ |
|---|---|---|
| Một hàng profile | 0,017 U | 0,007 U |
| Số hàng của profile ngày (trung vị) | 413 | 1.186 |
| HVN đạt tỉ lệ ≥ 2,5 mỗi phiên | 0,99 (68 % phiên có) | 2,14 (94 % phiên có) |
| Bề rộng dải HVN (×U), trung vị | 0,17 | 0,06 |
| Mức HVN đưa vào xét mỗi phiên | 6,8 | 14,4 |
| Phiên có profile hình chữ D | 51 % | 46 % |

Trên NQ, HVN nhiều gấp đôi và nhọn hơn, nhưng thứ hiện ra chart gần như không đổi (cụm có hợp lưu 45 % so với 48 %; vùng vàng 6,0 % so với 6,9 % thời gian). Muốn HVN của NQ "to ngang" GC theo U thì `RowTicks` ≈ 5 (1,25 điểm) — **chưa đo**, và với 38 lần quay lại vùng có HVN thì không đo được là tốt hơn hay không. Không đổi.

## 6. Chỗ cần sửa cho NQ: bộ phát hiện chỗ nối bắt nhầm

Luật hiện tại: nghỉ 30–150 phút và giá mở lệch giá đóng trước đó ≥ `MinSpliceJumpPrices × 10 × tick` = **50 điểm NQ**. Trên NQZ26 (một hợp đồng, không có chỗ nối nào) luật này nổ 3 lần trong 11 tuần — đều là khoảng trống giá thật qua giờ nghỉ ngày:

| Nến mở lại (UTC) | Bước nhảy | Theo U |
|---|---|---|
| 2026-11-11 23:00 | −138,0 điểm | 1,1 U |
| 2026-11-17 23:00 | +256,0 điểm | 2,5 U |
| 2026-11-19 23:00 | +94,5 điểm | 0,8 U |

GC cùng kỳ: bước nhảy lớn nhất qua giờ nghỉ ngày 5,2 giá, không lần nào bị bắt nhầm (ngưỡng 20 giá).

Mỗi lần bắt nhầm, indicator bỏ hết điểm va đập trước đó và các mức ngày/tuần cũ. Mật độ vùng được vẽ (`do_lai.py thang nq`):

| Tháng | Để nguyên: vùng vẽ TB / % thời gian có vùng | Tắt: vùng vẽ TB / % thời gian có vùng |
|---|---|---|
| 2026-09 | 1,25 / 57 % | 1,25 / 57 % |
| 2026-10 | 1,51 / 58 % | 1,51 / 58 % |
| 2026-11 | **0,36 / 30 %** | **0,81 / 56 %** |

Kết quả chấm gần như không đổi (mục 2); cái mất là **vùng trên chart** — đúng lúc thị trường vừa nhảy giá.

Việc cho Opus / người dùng:
- **Không cần code, làm được ngay:** trên chart NQ dùng mã một hợp đồng (NQZ26), tắt input `SpliceGuard`.
- **Nếu sửa code:** ngưỡng 20 giá là số đo riêng cho vàng; `× 10 × tick` không chuyển được sang NQ. Hai hướng, **cả hai chưa đo đủ để chốt**: (a) tự tắt khi symbol là một hợp đồng cụ thể, chỉ bật với mã liên tục; (b) đặt ngưỡng theo U. Với (b) lưu ý số có sẵn: chỗ nối thật của GC 2026-07-29 là +61,2 giá ≈ 4,6 U; khoảng trống thật lớn nhất của NQ ở đây là 2,5 U — ngưỡng ~3 U tách được hai trường hợp này nhưng biên rất mỏng và mới chỉ có 3 mẫu NQ.
- Dòng cảnh báo "chỗ nối" sẵn có của SessionZones cũng sẽ hiện nhầm trên NQ ở ba ngày trên.

## 7. Ghi chú kỹ thuật: hàng profile không đều (có sẵn từ trước, tác động nhỏ)

`ProfileEngine.Snap = Math.Round(giá / rowStep) × rowStep`, và `Math.Round` làm tròn nửa-về-chẵn. Với `RowTicks = 2`, bước giá lẻ rơi đúng giữa hai hàng:
- **NQ** (0,25 và 0,5 biểu diễn chính xác): hàng **3 bước giá xen hàng 1 bước giá**, đều đặn.
- **GC** (0,1 không biểu diễn chính xác, tuỳ sai số số thực): trong 2.000 hàng liên tiếp quanh 4.000 có 704 hàng 2 bước giá, 648 hàng 1 bước, 648 hàng 3 bước.

Hệ quả: POC, VAH/VAL theo hàng lệch tối đa 1 bước giá; dải HVN (`PeakSharpness`, 90 % trên khối lượng thô) dễ bị cắt ngắn. So với dung sai hợp lưu 0,10 U (1,2 giá GC, 7,6 điểm NQ) thì không đáng kể, và phép đo NQ ở đây đã chia hàng đúng kiểu C# này. Sửa (chia hàng bằng số nguyên bước giá) là việc riêng, sẽ đổi fixture `expected.json` — **không gấp, không thuộc vùng mạnh**.

## 8. Giới hạn

- **Cỡ mẫu nhỏ, không có TRAIN/TEST.** GC 314 lần quay lại vùng được vẽ / 71 phiên; NQ 165 / 42. Đây là một lần đo trên một kỳ, không phải kiểm định.
- GC ở đây **không độc lập** với lần đo cũ: cùng dữ liệu từ 2026-08-11 trở đi. Nó xác nhận mã liên tục không gây sai, không phải là mẫu mới.
- NQ là mẫu mới thật, nhưng chỉ 2,5 tháng và một chế độ thị trường (tháng 11 có ba lần nhảy giá lớn qua đêm).
- Như cũ: chưa phí, chưa trượt giá; "một nến M1 chạm cả hai mốc = thua"; không xét xác nhận order flow tại vùng.
- Nhiều lần quay lại cùng một vùng không độc lập; khoảng tin cậy theo khối ngày chỉ bù một phần.

## 9. File

| File | Việc |
|---|---|
| `prep1.py` | ghép file một hợp đồng, bảng chất lượng dữ liệu, dựng bộ đệm (`gc` / `nq`) |
| `do_lai.py` | `eval` (chạy bản tham chiếu + chấm), `bang` (mục 2, 3, 5), `thang` (mục 6), `full` (mục 4); thêm `tatnoi` để tắt phát hiện chỗ nối |

Chạy lại: `python prep1.py gc` → `python prep1.py nq` → `python do_lai.py eval gc` → `python do_lai.py bang gc` → `python do_lai.py eval nq tatnoi` → `python do_lai.py bang nq tatnoi` (bỏ `tatnoi` để ra bản "để nguyên"). Mục 4 cần chạy `prep.py` + `final_eval.py chot2` trước với `VM_CACHE` trỏ vào `<thư mục tạm>/vm_full/vung_manh_cache.pkl`, rồi `python do_lai.py full`. Bộ đệm nằm ở thư mục tạm, không vào repo. `vm.py`, `vung_manh.py`, `final_eval.py` không bị sửa.
