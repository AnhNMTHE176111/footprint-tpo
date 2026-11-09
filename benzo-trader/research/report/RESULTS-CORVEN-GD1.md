# Benzo CORVEN — GĐ1: đủ ①–④ + ⛔ trên TRAIN, bộ mặc định (chưa tinh chỉnh)

> Opus, 2026-11-09, theo `plans/BENZO-CORVEN-plan.md` (bản sau quyết định Q1–Q15). **Chỉ TRAIN**: 35 phiên dày, nến bar_idx 0…51318 (tới 2026-09-15 20:59 UTC). TEST chưa chạy, chưa đọc. Mô phỏng `kernel.simulate` (phí 0,2 giá/lệnh, chạm SL+TP cùng nến = SL, vào giá đóng CF, 1 lệnh mở), lệnh còn mở tới nến cuối phiên đóng `TIME`.
> ⚠️ Kết quả trên một mẫu TRAIN, chưa kiểm định ngoài mẫu — không dùng để vào lệnh thật.

## 1. Tổng

| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| Tất cả | 159 | 4,54 | 27,0 % | **-0,30** | [-0,50; -0,09] | -48,1 | 48,1 | 15 |

Lệnh còn mở cuối file: 0 · đóng `TIME` cuối phiên: 2 · hoà vốn ở TP 2R cần WR ≈ 36,4 % (phí 0,2 giá trên rủi ro trung vị 2,20 giá).

Lệnh/ngày: trung vị 5, min 1, max 8; phân bố {1: 2, 2: 3, 3: 4, 4: 7, 5: 10, 6: 4, 7: 3, 8: 2}.

## 2. Phễu thế → ② → ③ → ④ → lệnh

| Thế | số thế | qua ② | qua ③ (≥ 2 loại) | qua ④ + ⛔ + giờ | thành lệnh |
|---|---|---|---|---|---|
| A (fail break) | 1648 | 1489 | 625 | 49 | 42 |
| A "lần 2" | 1128 | 1128 | 454 | 69 | 64 |
| B (phá giữ được) | 1727 | 1621 | 986 | 58 | 53 |

Theo **CF ứng viên** (nến): 12206 qua ② → 4087 qua ③ (33,5 %) → 186 qua ④/⛔/giờ → 159 lệnh (bỏ vì đang có lệnh mở 16, vì thế/khoá đã có lệnh 11).

Số dấu hiệu khác loại trên CF qua ②: 0 loại: 3961, 1 loại: 4158, 2 loại: 2634, 3 loại: 1198, 4 loại: 252, 5 loại: 3

Có mặt từng loại trên CF qua ②: Δ 4246 (34,8 %), bóng 2506 (20,5 %), kiệt sức 2991 (24,5 %), stacked 4036 (33,1 %), trap 264 (2,2 %)

**Cổng bị trượt** trên các CF đã qua ③ (cổng ĐẦU TIÊN theo thứ tự kiểm / tỷ lệ trượt độc lập từng cổng):

| Cổng | trượt đầu tiên | % | trượt (độc lập) | % |
|---|---|---|---|---|
| 4a nến xác nhận | 3324 | 81,3 | 3324 | 81,3 |
| ⛔ kiệt sức chống hướng | 165 | 4,0 | 1131 | 27,7 |
| ⛔ nhịp đẩy do quét stop | 28 | 0,7 | 358 | 8,8 |
| ⛔ range chồng range | 6 | 0,1 | 23 | 0,6 |
| 4b trần SL 4 mbr | 9 | 0,2 | 25 | 0,6 |
| 4c R sẵn < 1,7 | 362 | 8,9 | 2472 | 60,5 |
| 4d chặn 19:20–20:30 VN | 6 | 0,1 | 292 | 7,1 |
| 4d 15 nến đầu phiên | 1 | 0,0 | 24 | 0,6 |
| nến cuối phiên (không vào được) | 0 | 0,0 | 0 | 0,0 |
| **qua hết** | 186 | 4,6 | | |

## 3. Theo thế

| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| A (fail break) | 42 | 1,20 | 21,4 % | **-0,45** | [-0,81; -0,03] | -19,1 | 19,6 | 12 |
| A "lần 2" | 64 | 1,83 | 28,1 % | **-0,29** | [-0,61; 0,03] | -18,7 | 23,9 | 7 |
| B (phá giữ được) — tất cả | 53 | 1,51 | 30,2 % | **-0,19** | [-0,54; 0,19] | -10,3 | 14,4 | 8 |
| B — range còn BROKEN | 38 | 1,09 | 23,7 % | **-0,39** | [-0,79; 0,01] | -14,9 | 14,9 | 6 |
| B — `b_from_exhausted` (range DEAD ngay) | 15 | 0,43 | 46,7 % | **0,31** | [-0,47; 1,10] | 4,7 | 4,3 | 4 |

## 4. Theo tổ hợp dấu hiệu

| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| Δ+stacked | 57 | 1,63 | 24,6 % | **-0,36** | [-0,68; 0,01] | -20,3 | 27,2 | 21 |
| Δ+bóng+stacked | 27 | 0,77 | 40,7 % | **0,06** | [-0,44; 0,62] | 1,7 | 5,7 | 5 |
| kiệt sức+stacked | 16 | 0,46 | 0,0 % | **-1,07** | [-1,09; -1,06] | -17,2 | 17,2 | 16 |
| Δ+kiệt sức+stacked | 15 | 0,43 | 53,3 % | **0,42** | [-0,29; 1,13] | 6,3 | 4,3 | 4 |
| Δ+bóng | 13 | 0,37 | 15,4 % | **-0,65** | [-1,11; 0,04] | -8,4 | 10,3 | 9 |
| bóng+stacked | 8 | 0,23 | 12,5 % | **-0,74** | [-1,14; 0,03] | -5,9 | 6,6 | 6 |
| Δ+bóng+kiệt sức+stacked | 6 | 0,17 | 16,7 % | **-0,60** | [-1,13; 0,41] | -3,6 | 3,6 | 3 |
| Δ+bóng+kiệt sức | 5 | 0,14 | 40,0 % | **0,10** | [-1,11; 1,32] | 0,5 | 2,2 | 2 |
| Δ+bóng+stacked+trap | 4 | 0,11 | 50,0 % | **0,41** | [-1,08; 1,90] | 1,6 | 2,2 | 2 |
| Δ+kiệt sức | 3 | 0,09 | 33,3 % | **-0,12** | [-1,15; 1,92] | -0,4 | 1,2 | 1 |
| stacked+trap | 2 | 0,06 | 50,0 % | **0,43** | [-1,08; 1,94] | 0,9 | 1,1 | 1 |
| bóng+trap | 1 | 0,03 | 0,0 % | **-1,04** | [-1,04; -1,04] | -1,0 | 1,0 | 1 |
| bóng+kiệt sức+stacked | 1 | 0,03 | 0,0 % | **-1,11** | [-1,11; -1,11] | -1,1 | 1,1 | 1 |
| Δ+stacked+trap | 1 | 0,03 | 0,0 % | **-1,11** | [-1,11; -1,11] | -1,1 | 1,1 | 1 |

## 5. Theo giờ VN (giờ mở nến CF)

| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| 00h | 3 | 0,09 | 66,7 % | **0,93** | [-1,03; 1,92] | 2,8 | 1,0 | 1 |
| 01h | 12 | 0,34 | 25,0 % | **-0,36** | [-1,11; 0,40] | -4,3 | 7,8 | 7 |
| 02h | 8 | 0,23 | 25,0 % | **-0,56** | [-1,10; 0,19] | -4,5 | 4,5 | 3 |
| 03h | 4 | 0,11 | 25,0 % | **-0,69** | [-1,13; 0,11] | -2,8 | 3,3 | 3 |
| 05h | 7 | 0,20 | 28,6 % | **-0,28** | [-1,16; 0,60] | -2,0 | 2,7 | 2 |
| 06h | 6 | 0,17 | 16,7 % | **-0,64** | [-1,18; 0,38] | -3,8 | 3,8 | 3 |
| 07h | 7 | 0,20 | 42,9 % | **0,19** | [-0,66; 1,44] | 1,3 | 2,2 | 2 |
| 08h | 9 | 0,26 | 11,1 % | **-0,75** | [-1,11; -0,08] | -6,8 | 7,7 | 7 |
| 09h | 6 | 0,17 | 33,3 % | **-0,08** | [-1,09; 0,94] | -0,5 | 3,2 | 3 |
| 10h | 7 | 0,20 | 0,0 % | **-1,08** | [-1,10; -1,06] | -7,5 | 7,5 | 7 |
| 11h | 9 | 0,26 | 33,3 % | **-0,11** | [-0,80; 0,90] | -1,0 | 3,4 | 3 |
| 12h | 8 | 0,23 | 12,5 % | **-0,72** | [-1,11; 0,05] | -5,8 | 5,8 | 5 |
| 13h | 9 | 0,26 | 11,1 % | **-0,78** | [-1,13; -0,09] | -7,0 | 7,8 | 7 |
| 14h | 7 | 0,20 | 28,6 % | **-0,24** | [-1,10; 0,64] | -1,6 | 3,6 | 3 |
| 15h | 7 | 0,20 | 57,1 % | **0,61** | [-0,26; 1,48] | 4,3 | 2,2 | 2 |
| 16h | 6 | 0,17 | 33,3 % | **-0,10** | [-1,12; 0,92] | -0,6 | 3,3 | 3 |
| 17h | 11 | 0,31 | 27,3 % | **-0,29** | [-1,10; 0,53] | -3,2 | 5,8 | 5 |
| 18h | 4 | 0,11 | 50,0 % | **0,40** | [-1,10; 1,91] | 1,6 | 1,1 | 1 |
| 19h | 2 | 0,06 | 0,0 % | **-1,11** | [-1,14; -1,08] | -2,2 | 2,2 | 2 |
| 20h | 3 | 0,09 | 33,3 % | **-0,05** | [-1,06; 1,94] | -0,2 | 1,1 | 1 |
| 21h | 7 | 0,20 | 57,1 % | **0,67** | [-0,20; 1,53] | 4,7 | 2,1 | 2 |
| 22h | 12 | 0,34 | 16,7 % | **-0,56** | [-1,07; 0,18] | -6,8 | 7,4 | 7 |
| 23h | 5 | 0,14 | 20,0 % | **-0,47** | [-1,07; 0,73] | -2,3 | 3,2 | 3 |

## 6. Theo phiên (A 05:00–12:30 · EU 12:30–19:00 · US 19:00–04:00 VN, neo Mỹ)

| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| A | 56 | 1,60 | 21,4 % | **-0,46** | [-0,78; -0,14] | -25,8 | 25,8 | 10 |
| EU | 47 | 1,34 | 31,9 % | **-0,14** | [-0,53; 0,29] | -6,7 | 10,2 | 6 |
| US | 56 | 1,60 | 28,6 % | **-0,28** | [-0,61; 0,08] | -15,5 | 15,9 | 6 |

## 7. Theo tháng

| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| 2026-07 | 14 | 0,40 | 21,4 % | **-0,46** | [-1,11; 0,19] | -6,5 | 9,2 | 7 |
| 2026-08 | 87 | 2,49 | 25,3 % | **-0,34** | [-0,61; -0,06] | -29,6 | 37,7 | 15 |
| 2026-09 | 58 | 1,66 | 31,0 % | **-0,21** | [-0,54; 0,15] | -12,0 | 14,8 | 9 |

## 8. Nhóm tách riêng (chạy lại chọn lệnh, cùng ứng viên)

| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| Mặc định (chặn 19:20–20:30 BẬT, có "lần 2", có `b_from_exhausted`) | 159 | 4,54 | 27,0 % | **-0,30** | [-0,50; -0,09] | -48,1 | 48,1 | 15 |
| Chặn 19:20–20:30 TẮT | 164 | 4,69 | 27,4 % | **-0,29** | [-0,48; -0,09] | -47,4 | 47,4 | 16 |
| Bỏ "lần 2" | 97 | 2,77 | 26,8 % | **-0,29** | [-0,55; -0,02] | -28,5 | 28,5 | 13 |
| Bỏ `b_from_exhausted` | 146 | 4,17 | 25,3 % | **-0,36** | [-0,56; -0,14] | -52,0 | 52,0 | 14 |

Luật ⛔ range chồng range loại 1,8 % thế A (≤ 30 % ⇒ **giữ luật**).

## 9. Đối chứng (cùng SL/TP/chi phí)

| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |
|---|---|---|---|---|---|---|---|---|
| **CORVEN (≥ 2 dấu hiệu)** | 159 | 4,54 | 27,0 % | **-0,30** | [-0,50; -0,09] | -48,1 | 48,1 | 15 |
| C1 — bỏ ③ (mọi CF hợp lệ tại mốc) | 194 | 5,54 | 29,4 % | **-0,24** | [-0,43; -0,04] | -46,0 | 46,2 | 8 |
| C2 — ngẫu nhiên cùng phiên/giờ ±30′/hướng/rủi ro mbr (20 nến mỗi lệnh, 3180 lệnh giả) | 159 | – | 31,3 % | **-0,16** | [-0,26; -0,07] | – | – | – |
| C3 — chỉ đòi Δ | 99 | 2,83 | 34,3 % | **-0,10** | [-0,38; 0,17] | -10,3 | 13,8 | 9 |
| C3 — chỉ đòi bóng | 40 | 1,14 | 27,5 % | **-0,28** | [-0,66; 0,17] | -11,2 | 13,4 | 7 |
| C3 — chỉ đòi kiệt sức | 49 | 1,40 | 26,5 % | **-0,30** | [-0,67; 0,07] | -14,7 | 15,9 | 13 |
| C3 — chỉ đòi stacked | 123 | 3,51 | 26,8 % | **-0,29** | [-0,52; -0,05] | -35,8 | 35,8 | 13 |
| C3 — chỉ đòi trap | 3 | 0,09 | 33,3 % | **-0,10** | [-1,11; 1,86] | -0,3 | 2,2 | 2 |

C2 theo cặp: R thật − R đối chứng trung bình = -0,14 trên 159 lệnh.

Dấu hiệu stacked có mặt ở 86,2 % số lệnh (> 50 % ⇒ GĐ2 quét run 4 theo plan ③d).

## 10. 5 thắng + 5 thua (rải đều theo thời gian) — ảnh ở `corven_gd1_shots/`

| | UTC | VN | thế | side | mốc | dấu hiệu | vào | SL | TP | R sẵn | kết cục | R | ảnh |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| thang 1 | 2026-07-30 09:28 | 16:28 | A | sell | canh | Δ to -28 = 3,5× medΔ; kiệt sức đỉnh (Ask 0) @4130,3; stacked sell 3 mức 4129,6–4129,8 | 4127.4 | 4130.8 | 4120.6 | 1,85 | TP | 1,94 | [ảnh](corven_gd1_shots/THANG1_20260730_0928_A_SELL.png) |
| thang 2 | 2026-08-10 08:38 | 15:38 | B | sell | stacked 4409,4–4409,6 | Δ to -24 = 2,7× medΔ; bóng đỏ 15 @4409,2 (3,3× nền); stacked sell 5 mức 4408,9–4409,3 | 4408.6 | 4410.0 | 4405.8 | 6,29 | TP | 1,86 | [ảnh](corven_gd1_shots/THANG2_20260810_0838_B_SELL.png) |
| thang 3 | 2026-08-28 18:29 | 01:29 | B | sell | stacked 4509,6–4510,1 | Δ ngược giá ΣΔ -4/2 nến; stacked sell 3 mức 4506,5–4506,7 | 4506.2 | 4510.9 | 4496.8 | 2,22 | TP | 1,96 | [ảnh](corven_gd1_shots/THANG3_20260828_1829_B_SELL.png) |
| thang 4 | 2026-09-04 04:01 | 11:01 | A2 | buy | cuc_tri | Δ to +36 = 6,0× medΔ; stacked buy 3 mức 4512,9–4513,1 | 4515.0 | 4511.3 | 4522.4 | 1,74 | TP | 1,95 | [ảnh](corven_gd1_shots/THANG4_20260904_0401_A2_BUY.png) |
| thang 5 | 2026-09-14 14:06 | 21:06 | A2 | buy | cuc_tri | Δ to +78 = 4,1× medΔ; kiệt sức đáy (Bid 0) @4304,7; stacked buy 3 mức 4306,3–4306,5 | 4308.7 | 4304.0 | 4318.1 | 1,96 | TP | 1,96 | [ảnh](corven_gd1_shots/THANG5_20260914_1406_A2_BUY.png) |
| thua 1 | 2026-07-28 23:59 | 06:59 | A2 | sell | cuc_tri | Δ to -61 = 13,6× medΔ; bóng đỏ 35 @4084,0 (17,5× nền); stacked sell 3 mức 4084,0–4084,2 | 4083.8 | 4085.3 | 4080.8 | 3,40 | SL | -1,13 | [ảnh](corven_gd1_shots/THUA1_20260728_2359_A2_SELL.png) |
| thua 2 | 2026-08-10 05:15 | 12:15 | A | buy | canh | bóng xanh 10 @4395,8 (3,3× nền); stacked buy 3 mức 4394,5–4394,7 | 4395.7 | 4393.6 | 4399.9 | 1,95 | SL | -1,10 | [ảnh](corven_gd1_shots/THUA2_20260810_0515_A_BUY.png) |
| thua 3 | 2026-08-20 18:00 | 01:00 | B | buy | canh | Δ to +26 = 3,2× medΔ; bóng xanh 26 @4577,0 (4,3× nền); stacked buy 3 mức 4576,8–4577,0 | 4577.2 | 4573.6 | 4584.4 | 2,46 | SL | -1,06 | [ảnh](corven_gd1_shots/THUA3_20260820_1800_B_BUY.png) |
| thua 4 | 2026-09-03 23:47 | 06:47 | A | sell | canh | Δ to -36 = 6,0× medΔ; stacked sell 4 mức 4522,7–4523,0 | 4522.5 | 4524.1 | 4519.3 | 2,12 | SL | -1,12 | [ảnh](corven_gd1_shots/THUA4_20260903_2347_A_SELL.png) |
| thua 5 | 2026-09-15 19:58 | 02:58 | A2 | buy | cuc_tri | Δ to +61 = 6,4× medΔ; bóng xanh 30 @4334,2 (5,0× nền) | 4336.4 | 4333.4 | 4342.4 | 1,77 | SL | -1,07 | [ảnh](corven_gd1_shots/THUA5_20260915_1958_A2_BUY.png) |

## 11. Tham số (bộ mặc định, chưa tinh chỉnh)

```
{'near_mbr': 1.0, 'win_b': 3, 'win_a_max': 5, 'cf_after_fb': 2, 'age_b': 30, 'si_ratio': 250.0, 'si_run': 3, 'si_minvol': 1.0, 'b_from_exhausted': True, 'same_session': True, 'exc_max_age': 30, 'delta_mult': 2.0, 'bubble_mult': 3.0, 'bubble_min': 10.0, 'div_min_len': 2, 'div_max_len': 8, 'need_signs': 2, 'cf_body': 0.4, 'cf_close_ext': 0.3, 'cf_min_rng_mbr': 0.5, 'cf_min_delta': 0.5, 'sl_buf_ticks': 3.0, 'sl_buf_mbr': 0.2, 'sl_floor_mbr': 1.0, 'sl_cap_mbr': 4.0, 'r_min': 1.7, 'tp_r': 2.0, 'dead_look': 300, 'block_us_open': True, 'block_first_bars': 15, 'veto_window': 5, 'stop_run_k': 3, 'overlap_bars': 30, 'overlap_frac': 0.5, 'overlap_max_drop': 0.3}
```

## 12. Nhận định (Opus) — số đo, chưa phải kết luận

- **Chưa thấy lợi thế trên TRAIN:** R TB −0,30 [−0,50; −0,09] — KTC nằm hẳn dưới 0. **Kém cả hai đối chứng**: C1 (bỏ ③) −0,24, C2 (ngẫu nhiên cùng giờ/hướng/rủi ro) −0,16; theo cặp R thật − R C2 = −0,14. Như vậy, ở bộ mặc định, ③ không cải thiện so với vào bừa tại mốc. C3: chỉ đòi Δ (−0,10, 99 lệnh) là loại đơn lẻ đỡ tệ nhất; chỉ đòi stacked −0,29.
- **Lệnh rất ngắn, SL sát:** giữ lệnh trung vị 5 nến; rủi ro trung vị 1,29 mbr (≈ 2,2 giá); 18 % lệnh bị sàn 1 mbr đẩy SL ra. WR 27 % so với mức hoà vốn ≈ 36 % ở TP 2R.
- **Phễu:** ③ là cổng rẻ (33 % CF qua ② có ≥ 2 loại dấu hiệu); cổng lọc thật là **4a** (81 % CF qua ③ trượt nến xác nhận) và **R ≥ 1,7** (61 % trượt độc lập). 4,5 lệnh/ngày (trung vị 5, tối đa 8) — trong khoảng kỳ vọng ≤ 8 của plan.
- **Stacked có mặt ở 86 % số lệnh** (> 50 %) ⇒ theo plan ③d, GĐ2 quét run 4. Tổ hợp hay gặp nhất "Δ+stacked" (57 lệnh, −0,36).
- Nhóm `b_from_exhausted` (15 lệnh) +0,31 nhưng KTC [−0,47; 1,10] — mẫu quá nhỏ, không đọc được gì.
- Chặn 19:20–20:30 gần như không đổi gì (bật −0,30 / tắt −0,29; chỉ khác 5 lệnh).

## 13. Điểm vẫn mơ hồ — CẦN FABLE QUYẾT (đang chạy theo lựa chọn in đậm)
1. **G1 — "Lần 2" (Q12) vẫn lỏng và là nhóm đông nhất:** 1.128 ứng viên (32/ngày, còn nhiều hơn bản GĐ0 25/ngày) và **64/159 lệnh (40 %)**. Lý do: "đóng lùi ≥ tol so với cực trị **mới**" (đáy của chính x) dễ hơn bản cũ (so với cực trị cú thủng), và "lần 1" (râu ≥ 1 tick + đóng lùi ≥ tol) xuất hiện ở hầu hết nến trong cú thủng. Plan coi đây là ngoại lệ. Có siết không (vd y phải là nến lập cực trị cú thủng; hoặc x đóng lại ≥ tol so với cực trị của y)? **Đang: theo chữ plan, y = nến thoả gần nhất trước x.**
2. **G2 — CF của "lần 2":** **đang lấy CF = chính nến x** (phải qua 4a), cửa sổ ③ = [max(nến đóng ngoài, x−4), x], mốc (dải ±tol, mức trap, mức "tới mốc" của Δ ngược giá) = cực trị của y. Plan không nói CF có được là 1–2 nến sau x không.
3. **G3 — Mốc trap thế B "cực trị của cú đẩy":** với thế B sell, cực trị cú đẩy là một đáy; quét đáy rồi đóng lên là ngược phe S ⇒ không dùng được làm mốc trap. **Đang dùng {cạnh vừa phá E, pivot 1c gần nhất ngược S}.** Có thể Fable muốn "đỉnh của nến đóng ngoài"?
4. **G4 — ⛔ nhịp quét stop:** "bóng ngược D ở cực trị cú đẩy" **đang hiểu là ô phía −D (≥ 3 × nền, ≥ 10) nằm ở nửa phía D của nến cực trị**; "K nến sau không lập cực trị mới" chỉ xét được khi CF ≥ cực trị + K (trước đó chưa biết ⇒ chưa veto). Cực trị cú đẩy = cực trị từ nến đóng ngoài tới CF. Loại 8,8 % CF qua ③ (độc lập).
5. **G5 — ⛔ range chồng range áp cho "lần 2":** **đang: chỉ cho khi range đã có ≥ 2 FailBreak tính tới x.** Luật chỉ loại 1,8 % thế A (< 30 % ⇒ giữ).
6. **G6 — Thế B có cả mốc cạnh và mốc stacked cùng lúc (16/53 lệnh B):** SL **đang lấy theo mốc cạnh**; chỉ có stacked thì lấy vùng mới nhất. Mốc stacked dùng cho 43/53 lệnh B.
7. **G7 — Chọn lệnh khi đang có lệnh mở:** **đang: ứng viên của một thế bị bỏ vì đang có lệnh thì các CF sau của CÙNG thế vẫn được vào** (nếu còn hợp lệ); một thế đã có lệnh thì hết. C# live phải làm y hệt (ghi để port GĐ3).
8. **G8 — Khoá "mỗi (range, cạnh, thế)":** A và "lần 2" **đang dùng chung nhóm thế A** (cùng cạnh thì chỉ 1 lệnh cho cả hai).
9. **G9 — Δ ngược giá với ΣΔ = 0:** plan viết "ΣΔ ≤ 0" ⇒ **đang tính cả = 0** (2/31 lệnh có dấu hiệu này). Biên độ nhịp so với mbr **tại nến neo x**.
10. **G10 — Q5 đóng TRONG vùng stacked:** **đang coi là "gần"** (khoảng cách âm, chưa xuyên mép xa).
11. **G11 — Tin USD (`IsNewsBlocked`):** Python không có lịch tin ⇒ không chặn (lệch có chủ đích, như plan mục parity).
12. **G12 — Lệnh còn mở qua khoảng trống phiên:** `kernel.simulate` không đổi; đóng `TIME` cuối phiên làm bằng cách gọi `simulate` từng lệnh với `max_hold_bars` = số nến tới hết phiên (`setup_corven.sim_one`). Chỉ 2 lệnh `TIME`.
