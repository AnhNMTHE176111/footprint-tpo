# Benzo FOLLOW-COMBO — kết quả GĐ-F0 + GĐ-F1 trên TRAIN

> Opus, 2026-11-09, theo `plans/BENZO-FOLLOW-COMBO-plan.md` (đăng ký trước, commit ee8b252). **Chỉ TRAIN**: 35 phiên dày, nến 0…51318 (tới 2026-09-15 20:59 UTC). **TEST (≥ 2026-09-16) không nạp, không đọc.** `kernel.simulate` (phí 0,2 giá/lệnh, chạm SL+TP cùng nến = SL, vào giá đóng CF), lệnh còn mở tới nến cuối phiên đóng `TIME`.
> ⚠️ Mẫu TRAIN, chưa kiểm định ngoài mẫu — không dùng để vào lệnh thật.

## 1. GĐ-F0 — tần suất (mục 6.i) và phễu (mục 6.vi)

- `CloseOutside` (cú phá bắt đầu): **3408** = 97,37 /ngày.
- Leg được xét: 4379; leg có move hợp lệ (đẩy ≥ 1 mbr ra ngoài + ΣΔ cùng hướng) ở một thời điểm nào đó: **2763** = 78,94 /ngày.
- **F0** (move + nhịp hồi + CF Follow): **772** = **22,06 /ngày** (kỳ vọng sơ bộ của plan 2–6/ngày; > 10/ngày ⇒ 2a quá lỏng — xem câu hỏi).
- F0 bị veto Vk (kiệt sức phe mình ở đỉnh move chưa bị quét): 95 = 12,3 %.

| Cờ | có trên F0 | % F0 | % F0 đã qua Vk |
|---|---|---|---|
| T | 40 | 5,2 % | 4,7 % |
| Bc | 52 | 6,7 % | 7,1 % |
| K | 157 | 20,3 % | 19,4 % |
| S | 486 | 63,0 % | 61,9 % |
| Dh | 170 | 22,0 % | 23,0 % |
| Dc | 263 | 34,1 % | 36,5 % |
| Sh | 368 | 47,7 % | 48,9 % |
| Mv | 638 | 82,6 % | 81,7 % |

Nhãn đo thêm trên F0: CF thoả 4a đầy đủ `cf_4a` 47,5 % · `cf_strict` 46,4 % · nhịp hồi `deep` (> 0,7 move) 26,8 % · leg 2 36,9 % · `b_from_exhausted` 18,9 % · số nến hồi 1/2 = 569/203.

**Phễu** (phiên dày; đơn vị = leg, từ bước CF = F0):

| Bước | số | ghi chú |
|---|---|---|
| CloseOutside | 3408 | mỗi cú phá ≤ 2 leg |
| leg được xét | 4379 | |
| move hợp lệ | 2763 | |
| có nhịp hồi (move hợp lệ) | 1830 | |
| có CF ≤ x + 3 (= F0) | 772 | leg kết thúc: huy_failbreak 1664, het_han 1272, cf 772, huy_reentry 373, cf_move_khong_hop_le 193, hoi_qua_sau 83, huy_het_phien 11, huy_het_tuoi 11 |
| qua Vk | 677 | |
| qua trần SL 4 mbr (S2) | 476 | |
| qua giờ (chặn 19:20–20:30, 15 nến đầu phiên, nến cuối phiên) | 451 | |
| lệnh F0 (1 lệnh mở, 1 lệnh/(range, cạnh, leg)) | 340 | |

## 2. GĐ-F1 — bảng chính (cấu hình chính: S2 · TP 2R không cổng · cf_within 3 · CF lỏng)

Hoán vị thống kê cực đại (4.4): 2000 lần, hoán vị nguyên dòng cờ giữa các F0 cùng phiên (trên 451 F0 đã qua Vk + cổng, dùng `r_alone`), thống kê = R TB(combo) − R TB(F0), lấy max trên 10 combo. **Ngưỡng phân vị 95 = 1,979R** (nếu chỉ lấy max trên các combo có ≥ 30 F0: 0,314R — chỉ để tham khảo, không dùng để chấm).

| Combo | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD | chuỗi thua | C1 toàn F0 | C1 F0∖combo | C2 | R nửa 1 / nửa 2 | Δ r_alone vs F0 (n F0) | p thô / p cực đại | vòng trong? | ĐẠT? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **F0** nền = C1 | 340 | 9,71 | 34,1 % | **-0,05** | [-0,20; 0,10] | -16,9 | 46,2 | 10 | -0,05 | – | 0,28 | -0,09 / -0,00 | – (451) | – / – | – | đối chứng |
| **F1** nguyên thủy (T) | 11 | 0,31 | 45,5 % | **0,31** | [-0,51; 1,13] | 3,4 | 3,2 | 3 | -0,05 | -0,06 | 0,84 | 0,07 / 0,95 | 0,360 (11) | 0,226 / 0,633 | không | n < 30 — không đo được |
| **F2** bóng CF (Bc) | 26 | 0,74 | 23,1 % | **-0,36** | [-0,83; 0,11] | -9,5 | 9,8 | 8 | -0,05 | -0,03 | 0,12 | -0,50 / -0,15 | -0,312 (26) | 0,889 / 1,000 | không | n < 30 — không đo được |
| **F3** kiệt sức hồi (K) | 82 | 2,34 | 35,4 % | **0,00** | [-0,29; 0,33] | 0,3 | 15,7 | 7 | -0,05 | -0,07 | 0,31 | 0,28 / -0,21 | 0,102 (84) | 0,205 / 0,889 | không | < C1+0,15; < C2+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F4** trap + bóng CF (T∧Bc) | 0 | – | – | – | – | – | – | – | -0,05 | – | – | – | – | – | – | không đo được |
| **F5** trap + kiệt sức (T∧K) | 2 | 0,06 | 50,0 % | **0,42** | [-1,04; 1,87] | 0,8 | 1,0 | 1 | -0,05 | -0,05 | 0,19 | 0,42 / – | 0,468 (2) | 0,453 / 0,522 | không | n < 30 — không đo được |
| **F6** stacked giữ (S) | 226 | 6,46 | 34,1 % | **-0,04** | [-0,23; 0,14] | -10,1 | 19,9 | 11 | -0,05 | -0,05 | 0,28 | -0,08 / -0,01 | 0,011 (272) | 0,469 / 0,990 | không | < C1+0,15; < C2+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F7** Δ ngược hồi (Dh) | 96 | 2,74 | 42,7 % | **0,20** | [-0,10; 0,51] | 19,2 | 9,1 | 4 | -0,05 | -0,13 | 0,33 | 0,29 / 0,08 | 0,201 (110) | 0,049 / 0,764 | không | < C2+0,15; không vượt ngưỡng hoán vị |
| **F8** hồi nông + lực CF (Sh∧(Bc∨Dc)) | 49 | 1,40 | 30,6 % | **-0,16** | [-0,53; 0,23] | -7,8 | 10,4 | 6 | -0,05 | -0,07 | 0,20 | -0,26 / -0,07 | 0,016 (52) | 0,420 / 0,987 | không | < C1+0,15; < C2+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F9** move mạnh + 1 dấu hiệu (Mv∧(T∨Bc∨K∨S)) | 214 | 6,11 | 33,2 % | **-0,07** | [-0,26; 0,11] | -15,6 | 24,3 | 10 | -0,05 | -0,03 | 0,29 | -0,09 / -0,05 | -0,015 (258) | 0,611 / 0,996 | không | < C1+0,15; < C2+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F10** ≥ 2 dấu hiệu khác loại {T,Bc,K,S,Dh} | 120 | 3,43 | 39,2 % | **0,12** | [-0,14; 0,37] | 14,0 | 9,7 | 5 | -0,05 | -0,11 | 0,35 | 0,16 / 0,07 | 0,143 (128) | 0,147 / 0,843 | không | < C2+0,15; KTC dưới ≤ −0,10; không vượt ngưỡng hoán vị |

**Kết luận GĐ-F1: 0 combo ĐẠT** · lọt vòng trong (n ≥ 30, ≥ C1, ≥ C2): không combo nào · chưa đo được (n < 30): F1, F2, F4, F5.

Ghi chú cột: n/WR/R TB… là lệnh thật (1 lệnh mở, 1 lệnh/(range, cạnh, leg)). "C1 toàn F0" = mọi F0 cùng cấu hình; "C1 F0∖combo" = F0 không thuộc combo, chọn lệnh cùng cách. C2 = `controls_corven.c2` (20 nến ngẫu nhiên cùng phiên ±30′, cùng hướng, cùng rủi ro theo mbr) cho các lệnh của combo. "Δ r_alone" = R TB(combo) − R TB(F0) trên F0 mô phỏng độc lập (thống kê của kiểm hoán vị; n F0 trong ngoặc). p thô = so với phân bố hoán vị của chính combo; p cực đại = so với phân bố max của 10 combo.

## 3. Biến thể báo cáo — **không có sức chọn** (mục 4.2), chỉ để biết

| Biến thể | Combo | n | WR | R TB | KTC 95 % | ΣR | C1 (F0 cùng biến thể) |
|---|---|---|---|---|---|---|---|
| S1 (SL sát nhịp hồi) | F0 | 487 | 35,3 % | -0,03 | [-0,16; 0,09] | -15,4 | -0,03 |
| S1 (SL sát nhịp hồi) | F1 | 25 | 48,0 % | 0,36 | [-0,23; 0,96] | 9,1 | -0,03 |
| S1 (SL sát nhịp hồi) | F2 | 36 | 38,9 % | 0,08 | [-0,36; 0,59] | 3,0 | -0,03 |
| S1 (SL sát nhịp hồi) | F3 | 110 | 38,2 % | 0,05 | [-0,22; 0,33] | 5,9 | -0,03 |
| S1 (SL sát nhịp hồi) | F4 | 1 | 0,0 % | -1,08 | [-1,08; -1,08] | -1,1 | -0,03 |
| S1 (SL sát nhịp hồi) | F5 | 6 | 50,0 % | 0,42 | [-0,58; 1,44] | 2,5 | -0,03 |
| S1 (SL sát nhịp hồi) | F6 | 319 | 35,7 % | -0,01 | [-0,17; 0,15] | -4,4 | -0,03 |
| S1 (SL sát nhịp hồi) | F7 | 128 | 35,9 % | -0,02 | [-0,27; 0,23] | -2,8 | -0,03 |
| S1 (SL sát nhịp hồi) | F8 | 105 | 32,4 % | -0,11 | [-0,37; 0,15] | -11,2 | -0,03 |
| S1 (SL sát nhịp hồi) | F9 | 320 | 36,2 % | -0,00 | [-0,16; 0,16] | -0,1 | -0,03 |
| S1 (SL sát nhịp hồi) | F10 | 169 | 41,4 % | 0,15 | [-0,07; 0,37] | 25,9 | -0,03 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F0 | 21 | 14,3 % | -0,67 | [-1,10; -0,22] | -14,1 | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F1 | 0 | – | – | – | – | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F2 | 0 | – | – | – | – | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F3 | 4 | 25,0 % | -0,31 | [-1,11; 1,14] | -1,2 | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F4 | 0 | – | – | – | – | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F5 | 0 | – | – | – | – | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F6 | 8 | 12,5 % | -0,74 | [-1,15; 0,02] | -5,9 | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F7 | 2 | 0,0 % | -1,16 | [-1,20; -1,12] | -2,3 | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F8 | 0 | – | – | – | – | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F9 | 7 | 14,3 % | -0,70 | [-1,15; 0,18] | -4,9 | -0,67 |
| gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range) | F10 | 2 | 50,0 % | 0,38 | [-1,12; 1,89] | 0,8 | -0,67 |
| cf_strict (CF đóng > high nhịp hồi) | F0 | 175 | 38,3 % | 0,09 | [-0,12; 0,31] | 15,7 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F1 | 11 | 27,3 % | -0,24 | [-1,04; 0,57] | -2,6 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F2 | 12 | 25,0 % | -0,30 | [-1,05; 0,46] | -3,6 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F3 | 34 | 44,1 % | 0,27 | [-0,18; 0,80] | 9,2 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F4 | 0 | – | – | – | – | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F5 | 2 | 50,0 % | 0,42 | [-1,04; 1,87] | 0,8 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F6 | 109 | 36,7 % | 0,06 | [-0,22; 0,34] | 6,4 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F7 | 46 | 45,7 % | 0,28 | [-0,15; 0,70] | 12,8 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F8 | 31 | 35,5 % | 0,00 | [-0,48; 0,50] | 0,0 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F9 | 99 | 36,4 % | 0,05 | [-0,23; 0,34] | 5,0 | 0,09 |
| cf_strict (CF đóng > high nhịp hồi) | F10 | 54 | 35,2 % | 0,00 | [-0,38; 0,39] | 0,1 | 0,09 |
| cf_within 4 | F0 | 373 | 33,5 % | -0,07 | [-0,21; 0,07] | -25,4 | -0,07 |
| cf_within 4 | F1 | 16 | 43,8 % | 0,25 | [-0,49; 1,00] | 4,1 | -0,07 |
| cf_within 4 | F2 | 30 | 20,0 % | -0,43 | [-0,83; 0,04] | -12,9 | -0,07 |
| cf_within 4 | F3 | 92 | 35,9 % | 0,02 | [-0,28; 0,31] | 1,6 | -0,07 |
| cf_within 4 | F4 | 0 | – | – | – | – | -0,07 |
| cf_within 4 | F5 | 3 | 66,7 % | 0,91 | [-1,04; 1,91] | 2,7 | -0,07 |
| cf_within 4 | F6 | 252 | 33,7 % | -0,06 | [-0,23; 0,12] | -14,3 | -0,07 |
| cf_within 4 | F7 | 110 | 40,9 % | 0,15 | [-0,12; 0,42] | 16,5 | -0,07 |
| cf_within 4 | F8 | 50 | 30,0 % | -0,18 | [-0,54; 0,21] | -8,9 | -0,07 |
| cf_within 4 | F9 | 245 | 32,7 % | -0,09 | [-0,26; 0,09] | -21,3 | -0,07 |
| cf_within 4 | F10 | 133 | 36,8 % | 0,05 | [-0,18; 0,30] | 6,3 | -0,07 |
| cf_4a (CF thoả 4a đầy đủ) | F0 | 191 | 34,6 % | -0,03 | [-0,22; 0,18] | -5,0 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F1 | 10 | 30,0 % | -0,16 | [-1,04; 0,74] | -1,6 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F2 | 16 | 31,2 % | -0,12 | [-0,70; 0,63] | -1,9 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F3 | 38 | 42,1 % | 0,21 | [-0,27; 0,68] | 7,8 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F4 | 0 | – | – | – | – | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F5 | 2 | 50,0 % | 0,42 | [-1,04; 1,87] | 0,8 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F6 | 119 | 32,8 % | -0,07 | [-0,31; 0,19] | -7,8 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F7 | 45 | 44,4 % | 0,23 | [-0,20; 0,67] | 10,4 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F8 | 29 | 34,5 % | -0,06 | [-0,53; 0,45] | -1,8 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F9 | 121 | 32,2 % | -0,08 | [-0,32; 0,17] | -9,9 | -0,03 |
| cf_4a (CF thoả 4a đầy đủ) | F10 | 59 | 40,7 % | 0,16 | [-0,20; 0,52] | 9,6 | -0,03 |
| chặn 19:20–20:30 TẮT | F0 | 358 | 34,1 % | -0,05 | [-0,19; 0,10] | -17,6 | -0,05 |
| chặn 19:20–20:30 TẮT | F1 | 12 | 41,7 % | 0,20 | [-0,55; 0,95] | 2,3 | -0,05 |
| chặn 19:20–20:30 TẮT | F2 | 28 | 21,4 % | -0,41 | [-0,84; 0,03] | -11,6 | -0,05 |
| chặn 19:20–20:30 TẮT | F3 | 87 | 36,8 % | 0,05 | [-0,26; 0,36] | 4,1 | -0,05 |
| chặn 19:20–20:30 TẮT | F4 | 0 | – | – | – | – | -0,05 |
| chặn 19:20–20:30 TẮT | F5 | 3 | 33,3 % | -0,07 | [-1,04; 1,87] | -0,2 | -0,05 |
| chặn 19:20–20:30 TẮT | F6 | 239 | 33,9 % | -0,05 | [-0,23; 0,13] | -11,7 | -0,05 |
| chặn 19:20–20:30 TẮT | F7 | 103 | 40,8 % | 0,14 | [-0,14; 0,43] | 14,9 | -0,05 |
| chặn 19:20–20:30 TẮT | F8 | 51 | 31,4 % | -0,14 | [-0,51; 0,24] | -6,9 | -0,05 |
| chặn 19:20–20:30 TẮT | F9 | 226 | 33,2 % | -0,07 | [-0,25; 0,12] | -16,1 | -0,05 |
| chặn 19:20–20:30 TẮT | F10 | 131 | 37,4 % | 0,06 | [-0,19; 0,32] | 8,5 | -0,05 |

## 4. Tách nhóm (cấu hình chính, lệnh thật): R TB (n)

| Combo | leg 1 | leg 2 | Á | Âu | Mỹ | OFF | b_from_exhausted | không exhausted |
|---|---|---|---|---|---|---|---|---|
| F0 | -0,06 (274) | -0,01 (66) | -0,13 (131) | 0,02 (102) | -0,02 (107) | – (0) | 0,29 (58) | -0,12 (282) |
| F1 | 0,44 (8) | -0,04 (3) | 0,93 (3) | -0,29 (4) | 0,44 (4) | – (0) | 0,95 (3) | 0,07 (8) |
| F2 | -0,20 (21) | -1,05 (5) | 0,06 (8) | -0,79 (11) | -0,19 (7) | – (0) | -0,30 (4) | -0,38 (22) |
| F3 | 0,12 (66) | -0,48 (16) | 0,09 (26) | 0,13 (25) | -0,17 (31) | – (0) | 0,01 (17) | 0,00 (65) |
| F4 | – | – | – | – | – | – | – | – |
| F5 | 1,87 (1) | -1,04 (1) | 1,87 (1) | – (0) | -1,04 (1) | – (0) | – (0) | 0,42 (2) |
| F6 | -0,06 (157) | -0,01 (69) | -0,14 (85) | 0,01 (67) | 0,01 (74) | – (0) | 0,01 (31) | -0,05 (195) |
| F7 | 0,21 (76) | 0,15 (20) | 0,19 (38) | 0,33 (28) | 0,09 (30) | – (0) | 0,54 (15) | 0,14 (81) |
| F8 | 0,05 (34) | -0,64 (15) | -0,52 (17) | 0,19 (17) | -0,15 (15) | – (0) | -0,38 (9) | -0,11 (40) |
| F9 | -0,09 (152) | -0,03 (62) | -0,20 (77) | -0,09 (74) | 0,10 (63) | – (0) | 0,23 (28) | -0,12 (186) |
| F10 | 0,20 (93) | -0,16 (27) | 0,11 (41) | 0,20 (38) | 0,05 (41) | – (0) | 0,14 (20) | 0,11 (100) |

**F0 theo giờ VN (giờ mở nến CF):** 00h 0,20 (12) · 01h -0,64 (14) · 02h 0,61 (17) · 03h -0,56 (13) · 05h -0,70 (15) · 06h -0,10 (15) · 07h 0,29 (20) · 08h -0,18 (21) · 09h -0,62 (14) · 10h -0,36 (17) · 11h 0,42 (16) · 12h 0,03 (22) · 13h -0,45 (15) · 14h 0,01 (14) · 15h 0,34 (15) · 16h -0,67 (15) · 17h 0,44 (16) · 18h 0,43 (18) · 19h -0,30 (8) · 20h 0,47 (8) · 21h 0,10 (16) · 22h -0,13 (10) · 23h -0,05 (9)

**F0 theo tháng:** 2026-07 0,06 (24) · 2026-08 -0,14 (203) · 2026-09 0,09 (113)

## 5. 5 thắng + 5 thua (rải đều theo thời gian) — combo lọt vòng trong

Không combo nào lọt vòng trong ⇒ không có danh sách (mục 5 plan chỉ áp cho combo lọt vòng trong). Để Fable soi chart, liệt kê 5 thắng + 5 thua của **F0** thay thế:

### F0

| | UTC | VN | side | leg | E | vào | SL | TP | cờ | kết cục | R |
|---|---|---|---|---|---|---|---|---|---|---|---|
| thắng 1 | 2026-07-29 00:36 | 07:36 | buy | 1 | 4082,7 | 4084,0 | 4082,3 | 4087,4 | – | TP | 1,88 |
| thắng 2 | 2026-08-12 10:41 | 17:41 | sell | 1 | 4476,6 | 4473,4 | 4476,9 | 4466,4 | S+Mv | TP | 1,94 |
| thắng 3 | 2026-08-24 17:47 | 00:47 | sell | 2 | 4698,8 | 4693,5 | 4699,3 | 4681,9 | S+Sh | TP | 1,97 |
| thắng 4 | 2026-09-04 17:29 | 00:29 | sell | 1 | 4479,2 | 4476,0 | 4480,3 | 4467,4 | Bc+Dc+Mv | TP | 1,95 |
| thắng 5 | 2026-09-15 19:17 | 02:17 | sell | 1 | 4343,7 | 4341,4 | 4344,0 | 4336,2 | K+S+Mv | TP | 1,92 |
| thua 1 | 2026-07-29 00:06 | 07:06 | buy | 1 | 4078,5 | 4081,9 | 4078,2 | 4089,3 | Sh+Mv | SL | -1,05 |
| thua 2 | 2026-08-11 02:57 | 09:57 | sell | 1 | 4474,4 | 4471,5 | 4474,9 | 4464,7 | Mv | SL | -1,06 |
| thua 3 | 2026-08-21 05:29 | 12:29 | sell | 2 | 4591,0 | 4586,7 | 4591,3 | 4577,5 | S+Dh+Sh+Mv | SL | -1,04 |
| thua 4 | 2026-09-02 22:20 | 05:20 | sell | 1 | 4434,1 | 4432,9 | 4434,4 | 4429,9 | S+Dh+Mv | SL | -1,13 |
| thua 5 | 2026-09-15 20:29 | 03:29 | sell | 1 | 4335,2 | 4334,1 | 4335,5 | 4331,3 | Dh+Sh+Mv | SL | -1,14 |

## 6. Cách Opus hiểu các chỗ plan chưa ghi rõ (chọn cách khớp ảnh gốc, cố định TRƯỚC khi nhìn R)

1. **FailBreak sau khi CF đã bắn không huỷ lệnh.** Ca ảnh vào ở nến thứ 2 sau nến đóng ngoài, còn FailBreak/BreakConfirmed chỉ biết ở nến thứ 3 ⇒ "huỷ mọi ứng viên" chỉ áp cho ứng viên **chưa có CF**; huỷ lệnh đã vào = nhìn trước. Lệnh vào rồi mà cú phá thành giả sẽ là nhãn `MOVE_GIA` lúc mổ SL.
2. **Kết thúc cú phá** khi có nến đóng về phía trong cạnh, tức `(close − E)·D ≤ 0` (đóng trong range = FailBreak trong K nến / ReEntry sau đó; đóng xuyên cạnh đối diện cũng tính), hoặc khi range Merge, hết tuổi 30 nến tính từ nến đóng ngoài, hoặc sang phiên mới. Range BROKEN rồi DEAD ngay vì hết lượt ReEntry vẫn bị kết thúc theo cách đóng giá này.
3. **Leg.** Có cực trị mới trước khi xuất hiện CF thì **cùng leg đó kéo dài**: x dời sang nến mới, nhịp hồi tính lại. Leg kết thúc khi gặp một trong ba trường hợp: (a) có CF; (b) tới x + 3 mà chưa có CF (hết hạn); (c) nhịp hồi quá sâu. Có CF mà move chưa hợp lệ (đẩy ra < 1 mbr hoặc ΣΔ ngược hướng) thì **không có F0** nhưng leg vẫn kết thúc (193 leg, xem phễu). Leg 2 được mở khi một nến vượt cực trị của leg trước; nếu chính nến CF đã vượt thì leg 2 bắt đầu ngay tại nến CF. Move của leg 2 vẫn tính từ nến đóng ngoài gốc (ΣΔ tính trên ref…x′, cùng E).
4. **Nhịp hồi và CF.** CF phải đứng ngay sau một chuỗi nến hồi **liền nhau** bắt đầu từ x + 1. Nếu x + 2 chưa đạt CF nhưng vẫn là nến hồi thì chuỗi nối dài, và x + 3 vẫn có thể là CF. Bản thân nến CF được phép cũng thoả điều kiện nến hồi (đóng < close[x]), vì plan chỉ đòi CF đóng cao hơn **nhịp hồi**.
5. **Cú phá kiểu whipsaw** (một nến vừa FailBreak vừa CloseOutside sang cạnh đối diện, khoảng 38 ca trên TRAIN theo GĐ0) vẫn được tính là cú phá mới theo hướng ngược lại.
6. **`b_from_exhausted`** được xác định ngay ở nến đóng ngoài: range đã có ≥ 2 lần phá thật thì lần này, nếu giữ được, sẽ làm range DEAD ngay. Biết được tại thời điểm đó nên không nhìn trước.
7. **Hai dung sai (tol).** Điều kiện "hồi không quá sâu" dùng tol của range (RangeEngine chốt lúc range sinh, giống `setup_corven` thế B). Cờ S dùng tol = max(2 tick, 0,5 mbr của nến CF).
8. **Cờ S** chỉ kiểm hai thứ: nhịp hồi có râu chạm [Lo − tol, Hi + tol], và không nến nào trong nhịp hồi ∪ CF đóng xuyên mép. Opus **không** thêm điều kiện "vùng chưa bị chạm trước đó" hay "nến tạo vùng phải đóng vượt Hi", vì plan không ghi. Hệ quả: S có ở 62 % F0, nên gần như không lọc được gì.
9. **Cờ Mv:** nhánh "nến thân ≥ 0,7 biên độ và |Δ| ≥ 2 medΔ" không đòi nến đó cùng hướng D (plan không ghi). Mv có ở 82 % F0.
10. **Tập F0 dùng để hoán vị** = F0 trên phiên dày, đã qua Vk, trần SL và các cổng giờ, đồng thời mô phỏng đóng được (TP/SL/TIME). Cột "C1 toàn F0" dùng lệnh thật của chính tập này (1 lệnh mở cùng lúc).

## 7. Câu hỏi cho Fable

1. **F0 = 22,1/ngày, vượt ngưỡng 10/ngày của GĐ-F0** (plan: "2a quá lỏng ⇒ báo lại trước khi đổi"). Opus **không đổi định nghĩa**, vì việc của lượt này là chạy F0 + F1. Nguyên nhân gốc: `CloseOutside` = 97/ngày. Số này khớp GĐ0: FailBreak 1.681 + BreakConfirmed 1.727 = 3.408 sự kiện, ứng với 24,7 range/ngày. Sau trần SL và các cổng giờ còn 451 F0; sau khi chọn lệnh còn 340 lệnh (9,7/ngày). Nếu muốn siết 2a thì đây là sửa định nghĩa **sau khi đã nhìn R** ⇒ phải ghi là hậu kiểm.
2. **Ngưỡng hoán vị bị phồng vì các combo n nhỏ.** Làm đúng chữ plan (max trên cả 10 combo, combo nào rỗng ở một lần hoán vị thì bỏ qua) thì ngưỡng P95 ≈ 1,98R (2.000 lần), do F1 (n F0 = 11) và F5 (n = 2) dao động rất mạnh. Nếu chỉ lấy max trên các combo có ≥ 30 F0 thì ngưỡng ≈ 0,31R. Ở lượt này không combo nào vượt **cả hai** ngưỡng, nên kết luận không đổi. Fable có muốn chốt cách thứ hai cho các vòng sau không (combo có n < 30 đằng nào cũng không được chấm)?
3. **C2 dương rõ (+0,28R ở F0) trong khi F0 −0,05R.** Vào ngẫu nhiên cùng hướng cú phá, ±30′ quanh CF, lại có lời. Opus nghi C2 có thiên lệch dương với setup đi theo cú phá: tập nến ngẫu nhiên gồm cả nến **trước** cú phá, mà hướng vào lại lấy theo cú phá đã xảy ra, nên các nến đó "biết trước" cú phá. Plan chính dùng C2 cho Thế A/B (cùng cơ chế). Nếu Fable thấy đúng, có thể cần C2 chỉ lấy nến **sau** CF. Lượt này giữ nguyên C2 theo plan.
4. **S2 khi leg 2 cách xa cạnh:** SL = min(E, đáy nhịp hồi) − đệm, nên rủi ro thường > 4 mbr và lệnh bị trần SL loại (677 → 476 F0 qua trần SL). S1 giữ được nhiều lệnh hơn (487 lệnh so với 340). Đây là đặc điểm của định nghĩa, không phải lỗi.
5. Danh mục mổ SL (mục 5) có hạng `TIN`, nhưng Python chưa có lịch tin ⇒ GĐ-F2 sẽ phải bỏ hạng này (plan đã cho phép), trừ khi Fable muốn port `NewsCalendar` trước.

## 8. Đối chiếu dự đoán đăng ký trước của Fable (mục 8 plan)

- F0 âm (−0,1…−0,3R): thực tế **−0,05R** (KTC [−0,20; 0,10]), tức âm nhẹ hơn dự đoán.
- F1/F5 n < 30: **đúng**; F2 và F4 cũng n < 30 (F4 không có lệnh nào: T và Bc không trùng nhau trên F0 nào qua được cổng).
- "1–2 combo dương nhưng không qua hoán vị": **đúng**. F7 (+0,20, dương cả hai nửa) và F10 (+0,12) dương, nhưng không qua C2 + 0,15 và không qua ngưỡng hoán vị (p cực đại 0,76 / 0,84). F7 có p thô 0,049 (< 0,05) nhưng không qua p cực đại; theo plan mục 8.2, combo như vậy **không** được gọi là có lợi thế. Hai combo này không nằm trong nhóm Fable đoán {F2, F4, F8, F9}.
- Có combo ĐẠT: **không** ⇒ theo 4.7 **không mở TEST**. Theo 4.5 cũng không combo nào lọt vòng trong, vì tất cả đều thua C2 của chính mình ⇒ GĐ-F2 (mổ SL) không có đối tượng hợp lệ. Fable quyết bước tiếp theo.
