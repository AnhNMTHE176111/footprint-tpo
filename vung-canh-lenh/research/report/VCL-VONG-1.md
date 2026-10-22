# Vùng Canh Lệnh — kết quả vòng 1

Dữ liệu: `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` (28856 nến M1, 22 phiên, giờ UTC). u = trung vị biên độ M1 50 nến (trung vị toàn file 1.70 USD).
**TRAIN** = 14 phiên đầu (2026-08-17 → 2026-09-03); phiên đầu (2026-08-17) chỉ để khởi động (chưa có phiên trước) ⇒ **đo trên 13 phiên** (2026-08-18 → 2026-09-03). **TEST** = 7 phiên (2026-09-04 → 2026-09-14); bỏ mẩu cuối 2026-09-15 (148 nến, phiên mỏng).
Không tham số nào được chọn bằng TEST: mọi tham số lấy nguyên từ PLAN (trọng số, đệm 0,5u, kẹp [1u,4u], 2+1 vùng mỗi phía, 1,2×).
Đối chứng: mỗi lần một vùng xuất hiện trên chart, tạo 50 bản sao dời ngẫu nhiên (cùng độ rộng, cùng thời gian hiển thị, tâm lúc xuất hiện ~ đều trong [đáy phiên trước −2, đỉnh phiên trước +2]); mọi phép đo chạy y hệt trên bản sao.
Thời gian chạy `vcl.py`: 83 giây (chuẩn bị 1s).

### Tóm tắt 3 ngưỡng gộp (mọi vùng hiển thị)

| Gộp | Tách | n vào dải | bật % thật / giả (hiệu) | p85 xâm nhập thật / giả | TP % thật / giả | R thực TB thật / giả |
|---|---|---|---|---|---|---|
| 0.7u | TRAIN | 4206 | 62.8 ±0.7 / 66.6 (-3.8 ±0.8 ▼) | 0.12 / 0.02 | 67.0 / 38.2 | +0.00 / -0.01 |
| 0.7u | TEST | 2275 | 63.1 ±1.0 / 67.4 (-4.4 ±1.1 ▼) | 0.10 / 0.00 | 66.9 / 40.2 | -0.01 / -0.01 |
| 1.0u | TRAIN | 3565 | 66.1 ±0.8 / 68.9 (-2.7 ±0.8 ▼) | 0.00 / 0.00 | 66.6 / 39.1 | +0.00 / +0.01 |
| 1.0u | TEST | 1965 | 65.4 ±1.1 / 69.8 (-4.3 ±1.1 ▼) | 0.00 / 0.00 | 67.1 / 40.5 | +0.00 / -0.04 |
| 1.5u | TRAIN | 3389 | 67.4 ±0.8 / 68.9 (-1.5 ±0.8 ≈) | 0.00 / 0.00 | 67.4 / 40.0 | +0.01 / -0.02 |
| 1.5u | TEST | 1848 | 66.6 ±1.1 / 70.1 (-3.5 ±1.1 ▼) | 0.00 / 0.00 | 66.0 / 40.4 | -0.01 / -0.02 |

### 1. Bật / xuyên (Chung&Bellotti, vào dải bằng giá đóng) — gộp 1.0u

| Nhóm vùng | TRAIN bật % ±se (n) | giả % | hiệu | TEST bật % ±se (n) | giả % | hiệu |
|---|---|---|---|---|---|---|
| Mọi vùng hiển thị | 66.1 ±0.8 (n=3565) | 68.9 | -2.7 ±0.8 ▼ | 65.4 ±1.1 (n=1965) | 69.8 | -4.3 ±1.1 ▼ |
| Có loại A | 67.0 ±0.8 (n=3205) | 70.0 | -2.9 ±0.9 ▼ | 66.3 ±1.1 (n=1815) | 70.7 | -4.4 ±1.1 ▼ |
| Có loại B | 68.5 ±1.0 (n=2052) | 71.8 | -3.3 ±1.1 ▼ | 67.3 ±1.4 (n=1152) | 72.6 | -5.3 ±1.4 ▼ |
| Có loại C | 67.9 ±2.0 (n=564) | 73.9 | -6.0 ±2.0 ▼ | 67.9 ±2.5 (n=343) | 74.1 | -6.2 ±2.6 ▼ |
| Có loại D | 67.5 ±1.1 (n=1779) | 70.9 | -3.5 ±1.2 ▼ | 65.6 ±1.6 (n=917) | 72.9 | -7.3 ±1.6 ▼ |
| Có loại E | 69.6 ±1.0 (n=1928) | 72.7 | -3.1 ±1.1 ▼ | 68.2 ±1.5 (n=951) | 73.1 | -4.8 ±1.6 ▼ |
| Hợp lưu 1 loại | 56.6 ±2.0 (n=618) | 55.0 | +1.7 ±2.2 ≈ | 58.5 ±2.5 (n=395) | 56.7 | +1.8 ±2.6 ≈ |
| Hợp lưu 2 loại | 65.1 ±1.5 (n=984) | 64.4 | +0.8 ±1.6 ≈ | 66.2 ±2.0 (n=559) | 61.5 | +4.7 ±2.1 ▲ |
| Hợp lưu ≥3 loại | 69.6 ±1.0 (n=1963) | 72.7 | -3.1 ±1.1 ▼ | 67.8 ±1.5 (n=1011) | 74.0 | -6.3 ±1.5 ▼ |

“giả %” = cùng nhóm nhưng trên vùng giả (50 lần dời ngẫu nhiên). ≈ = |hiệu| ≤ 2 sai số; ▲/▼ = vượt 2 sai số.

### 2. Độ rộng vs nhiễu — râu xuyên quá biên xa ở các ca BẬT (đơn vị u)

| | n bật | p50 | p85 | p95 | % > 0,5u (SL biên xa+0,5u bị quét) | % = 0 (không chạm biên xa) |
|---|---|---|---|---|---|---|
| TRAIN · Vùng thật | 2358 | 0.00 | 0.00 | 0.42 | 4.4 ±0.4 | 85.2 |
| TRAIN · Vùng giả | 20941 | 0.00 | 0.00 | 0.40 | 3.8 ±0.1 | 87.6 |
| TEST · Vùng thật | 1286 | 0.00 | 0.00 | 0.41 | 3.8 ±0.5 | 87.0 |
| TEST · Vùng giả | 17571 | 0.00 | 0.00 | 0.34 | 3.3 ±0.1 | 88.8 |

### 3. TP = cạnh gần vùng kế tiếp cùng hướng, SL = biên xa + 0,5u, vào ở giá đóng nến bật, tối đa 240 nến, không phí

| Nhóm | Khoảng TP | n thật | TP trước SL % ±se | giả % | R kế hoạch TB (thật/giả) | R thực TB (thật/giả) | phút tới TP (trung vị) |
|---|---|---|---|---|---|---|---|
| TRAIN | tất cả | 2358 | 66.6 ±1.0 | 39.1 | 0.61 / 2.73 | +0.00 / +0.01 | 3 |
| TRAIN | ≤3u | 1913 | 72.0 ±1.0 | 70.6 | 0.44 / 0.44 | -0.00 / -0.02 | 2 |
| TRAIN | 3–6u | 430 | 42.8 ±2.4 | 43.8 | 1.31 / 1.37 | -0.01 / +0.02 | 18 |
| TRAIN | >6u | 15 | 66.7 ±12.2 | 18.2 | 2.25 / 4.67 | +1.22 / +0.02 | 17 |
| TEST | tất cả | 1286 | 67.1 ±1.3 | 40.5 | 0.61 / 2.59 | +0.00 / -0.04 | 3 |
| TEST | ≤3u | 1076 | 71.8 ±1.4 | 72.5 | 0.44 / 0.42 | -0.01 / -0.01 | 3 |
| TEST | 3–6u | 190 | 42.1 ±3.6 | 42.3 | 1.35 / 1.35 | +0.03 / -0.01 | 12 |
| TEST | >6u | 20 | 50.0 ±11.2 | 16.2 | 2.82 / 4.77 | +0.73 / -0.07 | 46 |

R thực: thắng = +R kế hoạch, thua = −1, hết 240 nến = lãi/lỗ tạm theo giá đóng. Ca bật không có vùng kế tiếp cùng hướng thì bỏ.

### 4. Vệ sinh chart

| Gộp | Tách | vùng hiển thị TB | độ rộng trung vị (u / USD) | p90 rộng (u) | % nến đóng TRONG vùng (thật / giả) | đổi vùng / giờ | % thời gian có ≥1 vùng cả 2 phía | % đủ 3+3 |
|---|---|---|---|---|---|---|---|---|
| 0.7u | TRAIN | 6.00 | 1.85 / 3.20 | 3.39 | 78.7 / 10.9 | 20.3 | 100.0 | 100.0 |
| 0.7u | TEST | 6.00 | 1.86 / 3.00 | 3.39 | 77.8 / 17.9 | 20.8 | 100.0 | 100.0 |
| 1.0u | TRAIN | 6.00 | 2.36 / 3.80 | 3.57 | 80.1 / 12.3 | 17.1 | 100.0 | 100.0 |
| 1.0u | TEST | 6.00 | 2.46 / 3.80 | 3.58 | 79.5 / 19.4 | 17.7 | 100.0 | 100.0 |
| 1.5u | TRAIN | 6.00 | 2.55 / 3.95 | 3.63 | 80.9 / 12.9 | 16.2 | 100.0 | 100.0 |
| 1.5u | TEST | 6.00 | 2.65 / 4.03 | 3.62 | 80.2 / 19.7 | 16.7 | 100.0 | 100.0 |

### 5. Đóng góp từng loại ứng viên (gộp 1,0u; vùng có chứa loại đó)

| Loại | Tách | n | bật % − giả % | xâm nhập p85 (u) thật / giả | TP % thật / giả | R thực TB thật / giả |
|---|---|---|---|---|---|---|
| A | TRAIN | 3205 | -2.9 ±0.9 ▼ | 0.00 / 0.00 | 67.5 ±1.0 / 39.3 | +0.01 / +0.01 |
| A | TEST | 1815 | -4.4 ±1.1 ▼ | 0.00 / 0.00 | 67.4 ±1.4 / 41.0 | -0.00 / -0.04 |
| B | TRAIN | 2052 | -3.3 ±1.1 ▼ | 0.00 / 0.00 | 69.0 ±1.2 / 40.6 | +0.01 / +0.00 |
| B | TEST | 1152 | -5.3 ±1.4 ▼ | 0.00 / 0.00 | 67.9 ±1.7 / 42.4 | -0.01 / -0.03 |
| C | TRAIN | 564 | -6.0 ±2.0 ▼ | 0.00 / 0.00 | 68.7 ±2.4 / 42.1 | +0.01 / -0.01 |
| C | TEST | 343 | -6.2 ±2.6 ▼ | 0.00 / 0.00 | 68.2 ±3.0 / 45.5 | -0.04 / -0.03 |
| D | TRAIN | 1779 | -3.5 ±1.2 ▼ | 0.00 / 0.00 | 66.6 ±1.4 / 42.0 | -0.02 / +0.00 |
| D | TEST | 917 | -7.3 ±1.6 ▼ | 0.00 / 0.00 | 67.9 ±1.9 / 45.0 | -0.02 / -0.01 |
| E | TRAIN | 1928 | -3.1 ±1.1 ▼ | 0.00 / 0.00 | 68.4 ±1.3 / 40.2 | -0.00 / -0.03 |
| E | TEST | 951 | -4.8 ±1.6 ▼ | 0.00 / 0.00 | 67.5 ±1.8 / 43.8 | -0.02 / -0.02 |

### Ứng viên (gộp 1,0u)

| Loại | số ứng viên sinh ra cả file | sống trung bình mỗi nến |
|---|---|---|
| A swing M1 k=5 | 3506 | 107 |
| B swing M5 k=3 | 1073 | 55 |
| C mốc phiên (+POC trần) | 210 (+45) | 10 |
| D số tròn | sinh động | 42 |
| E lệnh lớn footprint | 2377 (TB 113/phiên, min 11, max 282) | 57 |

| Gộp | tổng số vùng (trước khi lọc hiển thị) TB mỗi nến | % của dải [giá ±5u] bị vùng phủ |
|---|---|---|
| 0.7u | 81 | 77% |
| 1.0u | 70 | 78% |
| 1.5u | 64 | 79% |

<!-- NHAN-XET -->

## Nhận xét (≤ 15 dòng)
1. **Bật/xuyên: không hơn đối chứng.** Ở cả 3 ngưỡng gộp, cả TRAIN lẫn TEST, vùng thật bật 63–67%, vùng giả 67–70%: thật thấp hơn 1,5–4,4 điểm (▼). Không loại A-E nào, không mức hợp lưu nào vượt đối chứng ở cả TRAIN và TEST (hợp lưu 2 loại +4,7 ▲ chỉ ở TEST, TRAIN ≈ ⇒ coi là nhiễu). Khớp SR-KET-QUA.md.
2. Dấu ▼ nhiều khả năng do đối chứng không cùng vị trí (vùng thật luôn sát giá, vùng giả rải trong biên phiên trước), không phải "vùng thật đẩy giá xuyên". Đọc là **"không hơn ngẫu nhiên"**, không đọc là "ngược".
3. **Độ rộng vs nhiễu: đạt mục tiêu nhưng ≈ đối chứng.** SL ở biên xa + 0,5u chỉ bị quét 3,8–4,4% ca bật (mục tiêu ≤ 15%), p85 xâm nhập = 0u. Vùng giả cùng độ rộng cũng 3,3–3,8% ⇒ đây là tính chất của **độ rộng ~2,4u** và cách đo bằng giá đóng, không phải vị trí vùng.
4. **TP tới vùng kế tiếp: không có lợi thế.** "TP % thật 67 vs giả 39" là ảo: vùng thật kế tiếp thường chỉ cách ≤ 3u (R kế hoạch 0,6) còn vùng giả ở xa (R 2,7). Cùng khoảng cách TP thì TP% ≈ đối chứng (≤3u: 72,0 vs 70,6; 3–6u: 42,8 vs 43,8) và **R thực TB ≈ 0** ở mọi nhóm (chưa trừ phí ⇒ có phí sẽ âm). Nhóm > 6u chỉ n = 15–20, không kết luận được.
5. **Vệ sinh chart: TRƯỢT nặng.** Giá đóng nằm TRONG vùng 78–81% số nến (mục tiêu < 25%; vùng giả 11–20%). Lý do: trung bình 64–81 vùng sống mỗi nến phủ ~78% dải giá ±5u (A ~107, E ~57, B ~55 ứng viên sống) ⇒ vùng lát kín trục giá, "2 vùng gần nhất" gần như luôn là vùng chứa giá + vùng sát bên. Nhấp nháy 16–21 vùng mới/giờ dù đã có luật 1,2×.
6. Kết luận vòng 1: thuật toán đúng PLAN nhưng **quá dày ứng viên**; không chỉ số nào cho thấy vị trí vùng mang thông tin. Gợi ý vòng 2 (để Fable quyết): cắt hẳn A (swing M1) và lọc E mạnh hơn để vùng thưa ra, rồi đo lại mục 4 trước; mục 1–3 nhiều khả năng vẫn ≈ đối chứng.

## Vấn đề / giới hạn gặp phải
- **E (lệnh lớn footprint):** cột `max_one_trade` (và `buy_trades`/`sell_trades`) trong file = 0 ở mọi dòng ⇒ nhánh "hoặc max_one_trade lớn" không dùng được; E chỉ dựa vào volume ≥ p99 (3 phiên trước) VÀ |delta|/volume ≥ 0,6. Sinh **TB 113 mức/phiên** (min 11 ở mẩu 09-15, 23 ở phiên lễ 09-07, max 282 ở 08-19); sống TB 57 mức mỗi nến — quá nhiều để gọi là "dấu vết lệnh lớn".
- Phiên 2026-09-07 (Lễ Lao động Mỹ): 1220 nến, volume 66k (≈ 40% phiên thường) — vẫn giữ trong TEST.
- Phiên 2026-08-17 chỉ khởi động (không có phiên trước cho C, E, biên độ phiên trước) ⇒ TRAIN đo 13 phiên, TEST đo 7 phiên. n nhỏ: sai số bật% ±0,8 (TRAIN) / ±1,1 (TEST).
- Đối chứng 50 lần không độc lập hoàn toàn (cùng nến, cùng lộ trình giá) ⇒ ± của cột "giả" thực tế lớn hơn công thức; hiệu < 2 sai số coi là ≈.
- Đo TP không trừ phí (0,2 giá/lệnh); vào lệnh ở giá đóng nến bật; SL và TP cùng nến ⇒ tính thua.
- Môi trường: máy không có lệnh `python`, chỉ `python3`; đã cài numpy/pandas/matplotlib/pytest bằng `pip3 install --user`.

## Chỗ phải tự quyết (PLAN chưa nói rõ)
- Tuổi thọ: A chết sau 2 phiên (2760 nến); B, E ×0,5 sau 2 phiên và chết sau 4 phiên; C sống 1380 nến từ lúc sinh; POC trần chết khi bị chạm; D không chết, không suy giảm, **không áp luật chuyển vai/chết** (nếu áp thì số tròn sẽ biến mất vĩnh viễn sau 2 lần xuyên).
- E không chuyển vai: chỉ chết khi giá đóng phía bên kia mức ≥ 2u (đúng câu PLAN 2.1-E); A/B/C dùng luật vùng chết của mục 2.2.
- Số lần chạm (= giá đóng vào vùng từ ngoài) **trần 5** trong hệ số (1 + 0,3 × chạm), để số tròn sống mãi không tích điểm vô hạn.
- D: bội 10$ trong khoảng giá đóng ±40$, sinh khi lần đầu lọt cửa sổ. Biên Á: chốt ở nến đầu có sm ≥ 450, cần ≥ 60 nến. VA Âu: chỉ VAH/VAL (như sr_measure).
- Vùng chồng nhau sau khi đệm/kẹp: cắt ở điểm giữa (có thể làm vùng hẹp hơn 1u một chút).
- Nhận diện vùng qua các nến (để chống nhấp nháy, đếm "đổi vùng/giờ" và dựng đối chứng): vùng nến trước khớp vùng nến này nếu chồng lấn > 0 (chọn chồng lấn lớn nhất). Vùng chứa giá được xếp phía theo TÂM vùng so với giá đóng.
- Đối chứng mục 3: TP của vùng giả = cạnh gần vùng giả kế tiếp (các vùng hiển thị cùng nến, cùng lần dời).
- Sự kiện chỉ đếm khi nến vào dải cùng phiên với nến trước; theo dõi tối đa 120 nến, không vượt phiên.
