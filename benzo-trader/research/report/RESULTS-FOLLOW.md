# Benzo FOLLOW-COMBO — kết quả GĐ-F0 + GĐ-F1 trên TRAIN (+ chấm lại C2’ theo plan 9.3-A)

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

> **Cập nhật 2026-11-09 theo plan mục 9.3-A (hậu kiểm):** thêm cột **C2'** = `controls_corven.c2(after_only=True)` — chỉ nến SAU nến CF, 0 < Δphút ≤ 30, cùng phiên/hướng/rủi ro mbr, 20 nến, pool < 5 ⇒ bỏ lệnh (C2 cũ có thiên lệch dương vì nến trước cú phá "biết trước" hướng). Cột **vòng trong / ĐẠT (C2')** là cột chấm: C2' thay C2, ngưỡng hoán vị = max chỉ trên combo có ≥ 30 F0 (plan 9.1-2). Hai cột "(C2 cũ)" giữ để đối chiếu kết luận GĐ-F1.

Hoán vị thống kê cực đại (4.4): 2000 lần, hoán vị nguyên dòng cờ giữa các F0 cùng phiên (trên 451 F0 đã qua Vk + cổng, dùng `r_alone`), thống kê = R TB(combo) − R TB(F0). Ngưỡng phân vị 95: max trên cả 10 combo = 1,979R (GĐ-F1, cũ) · **max chỉ trên combo có ≥ 30 F0 = 0,314R (ngưỡng CHẤM từ 9.1-2)**.

| Combo | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD | chuỗi thua | C1 toàn F0 | C1 F0∖combo | C2 cũ | **C2'** | R nửa 1 / nửa 2 | Δ r_alone vs F0 (n F0) | p thô / p cực đại (10 combo) / p cực đại (≥ 30) | vòng trong (C2 cũ) | ĐẠT (C2 cũ) | **vòng trong (C2')** | **ĐẠT (C2')** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **F0** nền = C1 | 340 | 9,71 | 34,1 % | **-0,05** | [-0,20; 0,10] | -16,9 | 46,2 | 10 | -0,05 | – | 0,28 | **-0,02** | -0,09 / -0,00 | – (451) | – / – / – | – | đối chứng | – | đối chứng |
| **F1** nguyên thủy (T) | 11 | 0,31 | 45,5 % | **0,31** | [-0,51; 1,13] | 3,4 | 3,2 | 3 | -0,05 | -0,06 | 0,84 | **0,51** | 0,07 / 0,95 | 0,360 (11) | 0,226 / 0,633 / – | không | n < 30 — không đo được | không | n < 30 — không đo được |
| **F2** bóng CF (Bc) | 26 | 0,74 | 23,1 % | **-0,36** | [-0,83; 0,11] | -9,5 | 9,8 | 8 | -0,05 | -0,03 | 0,12 | **-0,34** | -0,50 / -0,15 | -0,312 (26) | 0,889 / 1,000 / – | không | n < 30 — không đo được | không | n < 30 — không đo được |
| **F3** kiệt sức hồi (K) | 82 | 2,34 | 35,4 % | **0,00** | [-0,29; 0,33] | 0,3 | 15,7 | 7 | -0,05 | -0,07 | 0,31 | **-0,06** | 0,28 / -0,21 | 0,102 (84) | 0,205 / 0,889 / 0,598 | không | < C1+0,15; < C2+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị | **có** | < C1+0,15; < C2'+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F4** trap + bóng CF (T∧Bc) | 0 | – | – | – | – | – | – | – | -0,05 | – | – | – | – | – | – | – | không đo được | – | không đo được |
| **F5** trap + kiệt sức (T∧K) | 2 | 0,06 | 50,0 % | **0,42** | [-1,04; 1,87] | 0,8 | 1,0 | 1 | -0,05 | -0,05 | 0,19 | **0,12** | 0,42 / – | 0,468 (2) | 0,453 / 0,522 / – | không | n < 30 — không đo được | không | n < 30 — không đo được |
| **F6** stacked giữ (S) | 226 | 6,46 | 34,1 % | **-0,04** | [-0,23; 0,14] | -10,1 | 19,9 | 11 | -0,05 | -0,05 | 0,28 | **-0,04** | -0,08 / -0,01 | 0,011 (272) | 0,469 / 0,990 / 0,937 | không | < C1+0,15; < C2+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị | không | < C1+0,15; < C2'+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F7** Δ ngược hồi (Dh) | 96 | 2,74 | 42,7 % | **0,20** | [-0,10; 0,51] | 19,2 | 9,1 | 4 | -0,05 | -0,13 | 0,33 | **0,05** | 0,29 / 0,08 | 0,201 (110) | 0,049 / 0,764 / 0,232 | không | < C2+0,15; không vượt ngưỡng hoán vị | **có** | không vượt ngưỡng hoán vị |
| **F8** hồi nông + lực CF (Sh∧(Bc∨Dc)) | 49 | 1,40 | 30,6 % | **-0,16** | [-0,53; 0,23] | -7,8 | 10,4 | 6 | -0,05 | -0,07 | 0,20 | **-0,08** | -0,26 / -0,07 | 0,016 (52) | 0,420 / 0,987 / 0,927 | không | < C1+0,15; < C2+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị | không | < C1+0,15; < C2'+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F9** move mạnh + 1 dấu hiệu (Mv∧(T∨Bc∨K∨S)) | 214 | 6,11 | 33,2 % | **-0,07** | [-0,26; 0,11] | -15,6 | 24,3 | 10 | -0,05 | -0,03 | 0,29 | **-0,05** | -0,09 / -0,05 | -0,015 (258) | 0,611 / 0,996 / 0,978 | không | < C1+0,15; < C2+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị | không | < C1+0,15; < C2'+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F10** ≥ 2 dấu hiệu khác loại {T,Bc,K,S,Dh} | 120 | 3,43 | 39,2 % | **0,12** | [-0,14; 0,37] | 14,0 | 9,7 | 5 | -0,05 | -0,11 | 0,35 | **0,01** | 0,16 / 0,07 | 0,143 (128) | 0,147 / 0,843 / 0,421 | không | < C2+0,15; KTC dưới ≤ −0,10; không vượt ngưỡng hoán vị | **có** | < C2'+0,15; KTC dưới ≤ −0,10; không vượt ngưỡng hoán vị |

**Kết luận GĐ-F1 (C2 cũ): 0 combo ĐẠT** · lọt vòng trong: không combo nào.

**Chấm lại theo C2' (9.3-A, hậu kiểm): 0 combo ĐẠT** · lọt vòng trong (n ≥ 30, ≥ C1, ≥ C2'): F3, F7, F10 · chưa đo được (n < 30): F1, F2, F4, F5.

Ghi chú cột: n/WR/R TB… là lệnh thật (1 lệnh mở, 1 lệnh/(range, cạnh, leg)). "C1 toàn F0" = mọi F0 cùng cấu hình; "C1 F0∖combo" = F0 không thuộc combo, chọn lệnh cùng cách. C2 cũ = `controls_corven.c2` (20 nến ngẫu nhiên cùng phiên ±30′, cùng hướng, cùng rủi ro theo mbr) cho các lệnh của combo; C2' = cùng hàm với `after_only=True` (chỉ nến trong 30′ SAU CF). "Δ r_alone" = R TB(combo) − R TB(F0) trên F0 mô phỏng độc lập (thống kê của kiểm hoán vị; n F0 trong ngoặc). p thô = so với phân bố hoán vị của chính combo; p cực đại (10 combo) = so với phân bố max của 10 combo; p cực đại (≥ 30) = so với phân bố max chỉ trên combo có ≥ 30 F0.

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
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F0 | 409 | 34,2 % | -0,05 | [-0,19; 0,09] | -20,3 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F1 | 20 | 45,0 % | 0,28 | [-0,32; 0,89] | 5,6 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F2 | 30 | 30,0 % | -0,16 | [-0,66; 0,34] | -4,9 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F3 | 97 | 35,1 % | -0,02 | [-0,30; 0,27] | -1,5 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F4 | 1 | 0,0 % | -1,08 | [-1,08; -1,08] | -1,1 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F5 | 4 | 50,0 % | 0,41 | [-1,08; 1,90] | 1,6 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F6 | 278 | 35,3 % | -0,01 | [-0,18; 0,15] | -4,1 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F7 | 112 | 40,2 % | 0,12 | [-0,15; 0,40] | 12,9 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F8 | 73 | 30,1 % | -0,18 | [-0,48; 0,14] | -12,9 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F9 | 269 | 34,9 % | -0,02 | [-0,20; 0,15] | -6,7 | -0,05 |
| S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm) | F10 | 147 | 39,5 % | 0,11 | [-0,13; 0,34] | 16,6 | -0,05 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F0 | 297 | 35,0 % | -0,02 | [-0,18; 0,14] | -5,8 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F1 | 8 | 37,5 % | 0,08 | [-0,68; 1,20] | 0,6 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F2 | 23 | 17,4 % | -0,54 | [-0,93; -0,01] | -12,3 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F3 | 71 | 33,8 % | -0,04 | [-0,37; 0,30] | -2,6 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F4 | 0 | – | – | – | – | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F5 | 1 | 0,0 % | -1,04 | [-1,04; -1,04] | -1,0 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F6 | 205 | 34,1 % | -0,04 | [-0,23; 0,16] | -8,1 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F7 | 82 | 41,5 % | 0,16 | [-0,15; 0,48] | 13,5 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F8 | 46 | 30,4 % | -0,17 | [-0,53; 0,23] | -7,6 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F9 | 201 | 33,8 % | -0,05 | [-0,25; 0,15] | -10,3 | -0,02 |
| move_mbr 1,5 (9.1-1, hậu kiểm) | F10 | 105 | 36,2 % | 0,03 | [-0,25; 0,29] | 3,3 | -0,02 |

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

**F3 theo giờ VN (giờ mở nến CF):** 00h -1,11 (1) · 01h -0,56 (6) · 02h 0,73 (5) · 03h -1,00 (3) · 05h -1,20 (1) · 06h 1,90 (2) · 07h 1,35 (5) · 08h -0,04 (3) · 09h -0,29 (4) · 10h -0,47 (5) · 11h -1,09 (4) · 12h 0,44 (2) · 13h 0,46 (2) · 14h -0,07 (9) · 15h 1,92 (1) · 16h 0,13 (5) · 17h -0,08 (3) · 18h 0,12 (5) · 19h -1,04 (2) · 20h -0,27 (4) · 21h -0,02 (6) · 22h 0,98 (3) · 23h -1,04 (1)

**F3 theo tháng:** 2026-07 0,73 (5) · 2026-08 0,04 (49) · 2026-09 -0,20 (28)

**F7 theo giờ VN (giờ mở nến CF):** 00h 1,94 (2) · 01h -1,09 (4) · 02h 0,66 (6) · 03h -1,14 (1) · 05h -1,13 (3) · 06h 0,42 (4) · 07h 0,65 (7) · 08h 0,16 (5) · 09h -0,46 (5) · 10h -0,06 (6) · 11h 1,17 (4) · 12h 0,23 (7) · 13h -1,08 (4) · 14h 0,94 (6) · 15h 1,96 (2) · 16h 0,90 (3) · 17h 0,42 (4) · 18h -0,06 (6) · 19h -1,03 (1) · 20h -1,01 (1) · 21h 0,25 (7) · 22h -0,03 (3) · 23h 0,15 (5)

**F7 theo tháng:** 2026-07 0,80 (8) · 2026-08 0,10 (54) · 2026-09 0,21 (34)

**F10 theo giờ VN (giờ mở nến CF):** 00h 0,42 (2) · 01h -1,06 (6) · 02h 0,81 (8) · 03h -1,05 (2) · 05h -1,13 (4) · 06h 0,91 (3) · 07h 0,95 (6) · 08h 0,16 (5) · 09h 0,24 (7) · 10h -0,06 (6) · 11h -0,59 (6) · 12h 0,23 (7) · 13h -0,05 (6) · 14h -0,21 (7) · 15h 0,96 (3) · 16h 0,20 (7) · 17h 1,16 (4) · 18h 0,06 (8) · 19h -0,04 (3) · 20h -1,02 (2) · 21h 0,48 (10) · 22h -0,43 (5) · 23h 0,95 (3)

**F10 theo tháng:** 2026-07 0,21 (7) · 2026-08 0,11 (69) · 2026-09 0,11 (44)

## 5. 5 thắng + 5 thua (rải đều theo thời gian) — combo lọt vòng trong

### F3

| | UTC | VN | side | leg | E | vào | SL | TP | cờ | kết cục | R |
|---|---|---|---|---|---|---|---|---|---|---|---|
| thắng 1 | 2026-07-29 03:15 | 10:15 | sell | 1 | 4088,0 | 4086,2 | 4088,3 | 4082,0 | K+Dh+Sh | TP | 1,90 |
| thắng 2 | 2026-08-10 11:06 | 18:06 | sell | 1 | 4396,8 | 4393,7 | 4397,1 | 4386,9 | K+S+Dc+Sh+Mv | TP | 1,94 |
| thắng 3 | 2026-08-18 00:26 | 07:26 | buy | 1 | 4480,8 | 4484,5 | 4480,5 | 4492,5 | Bc+K+S+Mv | TP | 1,95 |
| thắng 4 | 2026-09-01 07:26 | 14:26 | sell | 1 | 4479,5 | 4476,4 | 4479,8 | 4469,6 | K+S+Dh+Mv | TP | 1,94 |
| thắng 5 | 2026-09-15 19:17 | 02:17 | sell | 1 | 4343,7 | 4341,4 | 4344,0 | 4336,2 | K+S+Mv | TP | 1,92 |
| thua 1 | 2026-07-29 20:02 | 03:02 | sell | 2 | 4125,0 | 4106,4 | 4126,1 | 4067,0 | K+S+Sh+Mv | SL | -1,01 |
| thua 2 | 2026-08-14 13:56 | 20:56 | sell | 1 | 4448,2 | 4441,3 | 4448,7 | 4426,5 | K+Sh+Mv | SL | -1,03 |
| thua 3 | 2026-08-28 02:51 | 09:51 | buy | 1 | 4635,7 | 4639,5 | 4635,3 | 4647,9 | K+Dc+Sh+Mv | SL | -1,05 |
| thua 4 | 2026-09-04 03:46 | 10:46 | sell | 1 | 4518,0 | 4515,7 | 4518,3 | 4510,5 | K+Sh+Mv | SL | -1,08 |
| thua 5 | 2026-09-15 18:15 | 01:15 | buy | 1 | 4339,4 | 4344,8 | 4339,1 | 4356,2 | K+S+Dc+Sh+Mv | SL | -1,04 |

### F7

| | UTC | VN | side | leg | E | vào | SL | TP | cờ | kết cục | R |
|---|---|---|---|---|---|---|---|---|---|---|---|
| thắng 1 | 2026-07-29 03:15 | 10:15 | sell | 1 | 4088,0 | 4086,2 | 4088,3 | 4082,0 | K+Dh+Sh | TP | 1,90 |
| thắng 2 | 2026-08-06 05:21 | 12:21 | sell | 1 | 4317,1 | 4313,8 | 4317,4 | 4306,6 | K+S+Dh | TP | 1,94 |
| thắng 3 | 2026-08-21 05:46 | 12:46 | buy | 2 | 4593,3 | 4599,0 | 4593,0 | 4611,0 | T+S+Dh+Sh+Mv | TP | 1,97 |
| thắng 4 | 2026-09-07 08:44 | 15:44 | sell | 1 | 4464,1 | 4460,4 | 4464,5 | 4452,2 | S+Dh+Sh+Mv | TP | 1,95 |
| thắng 5 | 2026-09-15 15:50 | 22:50 | buy | 1 | 4326,4 | 4331,4 | 4324,8 | 4344,6 | Dh+Dc+Mv | TP | 1,97 |
| thua 1 | 2026-07-29 06:17 | 13:17 | buy | 1 | 4095,6 | 4097,5 | 4095,3 | 4101,9 | Bc+Dh+Dc+Mv | SL | -1,09 |
| thua 2 | 2026-08-12 15:16 | 22:16 | buy | 1 | 4482,6 | 4486,3 | 4481,9 | 4495,1 | Dh+Dc+Mv | SL | -1,05 |
| thua 3 | 2026-08-21 11:24 | 18:24 | buy | 1 | 4650,8 | 4655,4 | 4650,4 | 4665,4 | S+Dh+Mv | SL | -1,04 |
| thua 4 | 2026-09-04 02:59 | 09:59 | buy | 1 | 4522,1 | 4523,8 | 4521,7 | 4528,0 | Dh+Mv | SL | -1,10 |
| thua 5 | 2026-09-15 20:29 | 03:29 | sell | 1 | 4335,2 | 4334,1 | 4335,5 | 4331,3 | Dh+Sh+Mv | SL | -1,14 |

### F10

| | UTC | VN | side | leg | E | vào | SL | TP | cờ | kết cục | R |
|---|---|---|---|---|---|---|---|---|---|---|---|
| thắng 1 | 2026-07-29 03:15 | 10:15 | sell | 1 | 4088,0 | 4086,2 | 4088,3 | 4082,0 | K+Dh+Sh | TP | 1,90 |
| thắng 2 | 2026-08-13 14:25 | 21:25 | sell | 1 | 4432,9 | 4431,0 | 4434,6 | 4423,8 | K+S | TP | 1,94 |
| thắng 3 | 2026-08-21 16:50 | 23:50 | buy | 1 | 4679,0 | 4681,9 | 4678,5 | 4688,7 | S+Dh+Sh+Mv | TP | 1,94 |
| thắng 4 | 2026-09-07 05:01 | 12:01 | buy | 1 | 4443,0 | 4446,0 | 4442,7 | 4452,6 | S+Dh | TP | 1,94 |
| thắng 5 | 2026-09-15 19:17 | 02:17 | sell | 1 | 4343,7 | 4341,4 | 4344,0 | 4336,2 | K+S+Mv | TP | 1,92 |
| thua 1 | 2026-07-29 06:17 | 13:17 | buy | 1 | 4095,6 | 4097,5 | 4095,3 | 4101,9 | Bc+Dh+Dc+Mv | SL | -1,09 |
| thua 2 | 2026-08-07 15:20 | 22:20 | buy | 2 | 4410,8 | 4415,6 | 4410,0 | 4426,8 | K+S | SL | -1,04 |
| thua 3 | 2026-08-24 18:18 | 01:18 | sell | 1 | 4689,5 | 4686,6 | 4690,1 | 4679,6 | S+Dh | SL | -1,06 |
| thua 4 | 2026-09-04 02:31 | 09:31 | sell | 2 | 4524,4 | 4518,7 | 4524,9 | 4506,3 | K+S+Mv | SL | -1,03 |
| thua 5 | 2026-09-15 18:15 | 01:15 | buy | 1 | 4339,4 | 4344,8 | 4339,1 | 4356,2 | K+S+Dc+Sh+Mv | SL | -1,04 |

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

## 9. Lượt 9.3-A (Opus, 2026-11-09, hậu kiểm — chỉ TRAIN)

- **C2' đã thay C2 làm cột chấm.** Cấu hình chính, số lệnh và R TB của mọi combo **không đổi** (cùng 340 lệnh F0, F7 +0,20, F10 +0,12…); chỉ đối chứng đổi.
  C2 → C2': F0 +0,28 → **−0,02** · F1 +0,84 → +0,51 · F3 +0,31 → −0,06 · F7 +0,33 → **+0,05** · F10 +0,35 → **+0,01**. Dự đoán đăng ký trước của Fable
  (C2' của F0 rơi về −0,10…+0,05): **đúng** (−0,02).
- **Lọt vòng trong theo C2' (n ≥ 30, ≥ C1, ≥ C2'): F3, F7, F10.** Không combo nào ĐẠT: F7 chỉ vướng đúng một điều kiện — Δ 0,201 < ngưỡng hoán vị
  ≥ 30 F0 = 0,314 (p cực đại ≥ 30 = 0,23); F10 vướng < C2'+0,15, KTC dưới ≤ −0,10, hoán vị; F3 vướng mọi tiêu chí trừ n.
- **F3 lọt vòng trong** nhưng plan 9.2/9.3-B chỉ giao mổ F7, F10 (+ F1 xem) ⇒ lượt này **chưa** mổ F3 (R TB +0,00 [−0,29; 0,33], dương nửa 1 / âm nửa 2) — Fable quyết.
- **S3** (leg 2 neo cực trị leg 1): giữ được nhiều lệnh hơn S2 (F0 409 so với 340, vì ít lệnh vượt trần 4 mbr) nhưng R TB F0 như nhau (−0,05); F7 +0,12 (n 112), F10 +0,11 (n 147).
- **move_mbr 1,5**: F0 −0,02 (n 297), F7 +0,16 (n 82), F10 +0,03 (n 105). Cả hai biến thể **không có sức chọn**, chỉ báo.
- C2' bỏ lệnh khi pool < 5 nến sau CF (cuối phiên): F0 còn 6.778/6.800 lệnh giả.
- Mổ SL vòng 1 (F7, F10; F1 chỉ xem): `report/MO-SL-FOLLOW.md`, ảnh `report/follow_shots/`, nhãn máy `report/_mo_sl_follow.csv`.

## 10. Hậu kiểm vòng mổ 1 — F7b (Opus, 2026-11-09, plan mục 10.3; chỉ TRAIN)

> **Hậu kiểm**: F7b = Dh ∧ ¬Hc sinh ra SAU khi đã nhìn R trên TRAIN (mổ SL vòng 1). Số TRAIN dưới đây **chỉ để báo**, không mở TEST; F7b chỉ được xác nhận trên dữ liệu ≥ 22/10 bằng `follow_newdata.py` (cấu hình đóng băng, cùng hàm `eval_post`). **Hc** (D = +1) = `min(low[x+1 … c−1]) ≤ E + tol`, tol = max(2 tick, 0,5 mbr tại c); cột `Hc`, `hc_ext_mbr` = (E − min low)·D / mbr trong `_follow_cands.csv`. Cấu hình chính không đổi; F0…F10 bên dưới trùng bảng mục 2 về n / R TB / C1 / C2' (script tự assert), chỉ p cực đại khác vì family hoán vị giờ là 11 combo.

Hoán vị thống kê cực đại: 2000 lần trên 451 F0 đã qua Vk + cổng; **family 11 combo = F1…F10 + F7b** (F7b hậu kiểm). Ngưỡng phân vị 95: max trên 11 combo = 1,979R · **max chỉ trên combo có ≥ 30 F0 = 0,326R (ngưỡng chấm)**. Ba dòng F7∧Hc / F10∧¬Hc / F0∧¬Hc chỉ báo cáo (có p thô, không vào max).

| Combo | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD | chuỗi thua | C1 toàn F0 | C1 F0∖combo | **C2'** | R nửa 1 / nửa 2 | Δ r_alone vs F0 (n F0) | p thô / p cực đại (≥ 30, 11 combo) | vòng trong (C2') | ĐẠT (C2') |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **F0** nền = C1 | 340 | 9,71 | 34,1 % | **-0,05** | [-0,20; 0,10] | -16,9 | 46,2 | 10 | -0,05 | – | **-0,02** | -0,09 / -0,00 | – (451) | – / – | – | đối chứng |
| **F1** nguyên thủy (T) | 11 | 0,31 | 45,5 % | **0,31** | [-0,51; 1,13] | 3,4 | 3,2 | 3 | -0,05 | -0,06 | **0,51** | 0,07 / 0,95 | 0,360 (11) | 0,226 / – | không | n < 30 — không đo được |
| **F2** bóng CF (Bc) | 26 | 0,74 | 23,1 % | **-0,36** | [-0,83; 0,11] | -9,5 | 9,8 | 8 | -0,05 | -0,03 | **-0,34** | -0,50 / -0,15 | -0,312 (26) | 0,889 / – | không | n < 30 — không đo được |
| **F3** kiệt sức hồi (K) | 82 | 2,34 | 35,4 % | **0,00** | [-0,29; 0,33] | 0,3 | 15,7 | 7 | -0,05 | -0,07 | **-0,06** | 0,28 / -0,21 | 0,102 (84) | 0,205 / 0,637 | **có** | < C1+0,15; < C2'+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F4** trap + bóng CF (T∧Bc) | 0 | – | – | – | – | – | – | – | -0,05 | – | – | – | – | – | – | không đo được |
| **F5** trap + kiệt sức (T∧K) | 2 | 0,06 | 50,0 % | **0,42** | [-1,04; 1,87] | 0,8 | 1,0 | 1 | -0,05 | -0,05 | **0,12** | 0,42 / – | 0,468 (2) | 0,453 / – | không | n < 30 — không đo được |
| **F6** stacked giữ (S) | 226 | 6,46 | 34,1 % | **-0,04** | [-0,23; 0,14] | -10,1 | 19,9 | 11 | -0,05 | -0,05 | **-0,04** | -0,08 / -0,01 | 0,011 (272) | 0,469 / 0,944 | không | < C1+0,15; < C2'+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F7** Δ ngược hồi (Dh) | 96 | 2,74 | 42,7 % | **0,20** | [-0,10; 0,51] | 19,2 | 9,1 | 4 | -0,05 | -0,13 | **0,05** | 0,29 / 0,08 | 0,201 (110) | 0,049 / 0,272 | **có** | không vượt ngưỡng hoán vị |
| **F8** hồi nông + lực CF (Sh∧(Bc∨Dc)) | 49 | 1,40 | 30,6 % | **-0,16** | [-0,53; 0,23] | -7,8 | 10,4 | 6 | -0,05 | -0,07 | **-0,08** | -0,26 / -0,07 | 0,016 (52) | 0,420 / 0,935 | không | < C1+0,15; < C2'+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F9** move mạnh + 1 dấu hiệu (Mv∧(T∨Bc∨K∨S)) | 214 | 6,11 | 33,2 % | **-0,07** | [-0,26; 0,11] | -15,6 | 24,3 | 10 | -0,05 | -0,03 | **-0,05** | -0,09 / -0,05 | -0,015 (258) | 0,611 / 0,981 | không | < C1+0,15; < C2'+0,15; KTC dưới ≤ −0,10; không dương cả 2 nửa; không vượt ngưỡng hoán vị |
| **F10** ≥ 2 dấu hiệu khác loại {T,Bc,K,S,Dh} | 120 | 3,43 | 39,2 % | **0,12** | [-0,14; 0,37] | 14,0 | 9,7 | 5 | -0,05 | -0,11 | **0,01** | 0,16 / 0,07 | 0,143 (128) | 0,147 / 0,471 | **có** | < C2'+0,15; KTC dưới ≤ −0,10; không vượt ngưỡng hoán vị |
| **F7b** Dh ∧ ¬Hc (hậu kiểm) | 66 | 1,89 | 47,0 % | **0,33** | [-0,03; 0,69] | 21,8 | 3,4 | 3 | -0,05 | -0,15 | **0,07** | 0,37 / 0,28 | 0,395 (74) | 0,003 / 0,016 | **có** | **ĐẠT** |
| **F7Hc** F7 ∧ Hc (đối chiếu cơ chế) | 35 | 1,00 | 28,6 % | **-0,22** | [-0,66; 0,21] | -7,9 | 14,3 | 11 | -0,05 | -0,03 | **-0,06** | -0,09 / -0,37 | -0,196 (36) | 0,887 / – | – | báo cáo — không có sức chọn |
| **F10nHc** F10 ∧ ¬Hc (báo cáo) | 85 | 2,43 | 41,2 % | **0,19** | [-0,13; 0,51] | 16,0 | 6,8 | 5 | -0,05 | -0,12 | **0,08** | 0,12 / 0,26 | 0,225 (91) | 0,070 / – | – | báo cáo — không có sức chọn |
| **F0nHc** F0 ∧ ¬Hc (báo cáo) | 254 | 7,26 | 36,2 % | **0,02** | [-0,16; 0,19] | 4,9 | 24,9 | 11 | -0,05 | -0,17 | **0,03** | -0,09 / 0,14 | 0,054 (320) | 0,053 / – | – | báo cáo — không có sức chọn |

**Kiểm F7b theo 10.2-1** (đủ mọi điều kiện mới ĐẠT):

| điều kiện | đạt? | số |
|---|---|---|
| n ≥ 30 | có | 66 |
| R TB ≥ C1 + 0,15 | có | 0,33 vs 0,10 |
| R TB ≥ C2' + 0,15 | có | 0,33 vs 0,22 |
| KTC dưới > −0,10 | có | -0,03 |
| dương cả hai nửa | có | 0,37 / 0,28 |
| vượt ngưỡng hoán vị ≥ 30 (family 11) | có | Δ 0,395 vs ngưỡng 0,326 |
| R TB(F7∧¬Hc) − R TB(F7∧Hc) ≥ +0,20 | có | 0,33 − -0,22 = 0,56 |

⇒ **F7b: ĐẠT**.

Cách lọc của Fable (tách 96 lệnh F7 đã chọn theo Hc, KHÔNG chọn lại one_at_a_time): F7 ∧ ¬Hc n 63 · R TB 0,40 · nửa 1/2 0,45 (36) / 0,33 (27); F7 ∧ Hc n 33 · R TB -0,17.

**Giả thuyết H1–H3 (chỉ đo, không có sức chọn) — R TB (n) hai phía trên lệnh pipeline của từng combo:**

| giả thuyết | F0 đạt | F0 không | F7 đạt | F7 không | F7b đạt | F7b không | F10 đạt | F10 không |
|---|---|---|---|---|---|---|---|---|
| H1 thân CF < 0,4 | 0,12 (77) | -0,10 (263) | 0,64 (30) | 0,00 (66) | 0,67 (26) | 0,11 (40) | 0,39 (35) | 0,00 (85) |
| H2 rủi ro S2 ≥ 7 giá | -0,19 (36) | -0,03 (304) | -0,27 (8) | 0,24 (88) | -0,27 (8) | 0,41 (58) | -0,27 (16) | 0,18 (104) |
| H3 move_h ≥ 2 × chiều cao range | -0,07 (32) | -0,05 (308) | -0,55 (6) | 0,25 (90) | -0,55 (6) | 0,42 (60) | -0,40 (14) | 0,19 (106) |

> ⚠️ Chữ "ĐẠT" của F7b ở trên là **trên chính dữ liệu đã sinh ra luật** (Hc chọn sau khi nhìn R TRAIN) ⇒ **không phải bằng chứng**, chỉ cho biết F7b không chết ngay trong mẫu. Kết luận ĐẠT / KHÔNG duy nhất được tính là lần chạy `follow_newdata.py` trên dữ liệu ≥ 22/10. Bảng H1–H3 tính trên mọi lệnh pipeline (kể cả TIME) nên dòng F0 lệch nhẹ so với `MO-SL-FOLLOW.md` 4.2 (chỉ SL/TP).

**Đối chiếu số lọc của Fable** (`MO-SL-FOLLOW.md` mục 3: F7 ∧ ¬Hc n 62, R TB +0,40, nửa 1/2 +0,45 (36) / +0,33 (26); F7 ∧ Hc n 33, −0,17):

- Pipeline (chọn lại one_at_a_time trên mask F7b): n **66** (lệch +4), R TB **0,33** (lệch -0,07R). F7 ∧ Hc pipeline n 35, R TB -0,22.
- Cách lọc của Fable tái hiện từ lệnh F7: ¬Hc n 63 · 0,40; Hc n 33 · -0,17.
- Lệch trong ngưỡng 10.3-5 (≤ 0,10R và n ≤ 10) ⇒ không cần mục 7 `MO-SL-FOLLOW.md`.

