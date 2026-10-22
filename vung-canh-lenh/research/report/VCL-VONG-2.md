# Vùng Canh Lệnh — kết quả vòng 2

Dữ liệu như vòng 1: `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` (28856 nến M1, 22 phiên, UTC). Gộp 1,0u.
**TRAIN đo 13 phiên** (2026-08-18 → 2026-09-03; 2026-08-17 chỉ khởi động), **TEST đo 7 phiên** (2026-09-04 → 2026-09-14; bỏ mẩu 2026-09-15).
**Đối chứng (mới, dùng cho mọi bảng trừ khi ghi khác):** với mỗi lần một vùng thật xuất hiện cách giá đóng d (cạnh gần, theo u, phía trên/dưới), tạo 50 vùng giả cùng độ rộng, cùng thời gian hiển thị, đặt cạnh gần ở khoảng cách d' bốc ngẫu nhiên từ phân phối d của MỌI vùng thật cùng phía và cùng TRAIN/TEST (không dùng chính d của nó). Vùng giả đi theo đúng chuyển động biên của vùng thật.
Không tham số nào chọn bằng TEST: mọi tham số lấy từ PLAN + review vòng 2 của Fable.
Thời gian chạy `vcl2.py`: 45 giây (engine v2 10s; còn lại = đo 2 kiểu đối chứng + chạy lại engine v1 để so).

### Trước (v1) / sau (v2) — 3 chỉ số vệ sinh ở mục A

| Chỉ số | mục tiêu | v1 TRAIN | v1 TEST | v2 TRAIN | v2 TEST |
|---|---|---|---|---|---|
| % nến đóng trong vùng hiển thị | ≤ 25% | 80.1 | 79.5 | 6.9 | 6.8 |
| số vùng sống trong ±10u | ≤ 8 | 8.6 | 8.5 | 6.5 | 6.3 |
| đổi vùng / giờ | ≤ 4 | 17.1 | 17.7 | 12.4 | 12.1 |
| (tham khảo) % nến đóng trong BẤT KỲ vùng sống nào | – | – | – | 41.4 | 42.2 |

### 8. "Tới được" (nam châm) — mỗi vùng lúc xuất hiện, cạnh gần đóng băng, chạm bằng high/low, chỉ trong phiên

| Tách | Khoảng cách d | n thật | chạm ≤30 nến % thật / giả | ≤60 nến | ≤120 nến | chạm rồi quay lại ≥2u trong 30 nến % thật / giả (n chạm) |
|---|---|---|---|---|---|---|
| TRAIN | ≤3u | 1650 | 70.8 ±1.1 / 70.4 (+0.3 ±1.1 ≈) | 77.5 ±1.0 / 77.8 (-0.3 ±1.0 ≈) | 82.8 ±0.9 / 83.0 (-0.2 ±0.9 ≈) | 64.3 ±1.3 (n=1366) / 65.7 (-1.4 ±1.3 ≈) |
| TRAIN | 3–6u | 854 | 34.0 ±1.6 / 34.1 (-0.1 ±1.6 ≈) | 47.8 ±1.7 / 47.8 (+0.0 ±1.7 ≈) | 59.8 ±1.7 / 59.5 (+0.3 ±1.7 ≈) | 68.1 ±2.1 (n=511) / 67.6 (+0.5 ±2.1 ≈) |
| TRAIN | 6–12u | 765 | 14.0 ±1.3 / 13.2 (+0.8 ±1.3 ≈) | 25.4 ±1.6 / 24.3 (+1.1 ±1.6 ≈) | 39.6 ±1.8 / 37.7 (+1.9 ±1.8 ≈) | 74.6 ±2.5 (n=303) / 73.0 (+1.5 ±2.5 ≈) |
| TEST | ≤3u | 822 | 72.1 ±1.6 / 72.0 (+0.1 ±1.6 ≈) | 79.7 ±1.4 / 79.5 (+0.2 ±1.4 ≈) | 85.6 ±1.2 / 85.3 (+0.3 ±1.2 ≈) | 67.2 ±1.8 (n=704) / 66.0 (+1.1 ±1.8 ≈) |
| TEST | 3–6u | 431 | 38.1 ±2.3 / 36.0 (+2.0 ±2.4 ≈) | 50.8 ±2.4 / 49.5 (+1.3 ±2.4 ≈) | 64.7 ±2.3 / 61.8 (+2.9 ±2.3 ≈) | 67.4 ±2.8 (n=279) / 65.6 (+1.7 ±2.8 ≈) |
| TEST | 6–12u | 425 | 15.5 ±1.8 / 14.7 (+0.8 ±1.8 ≈) | 27.8 ±2.2 / 26.9 (+0.9 ±2.2 ≈) | 41.2 ±2.4 / 41.0 (+0.2 ±2.4 ≈) | 64.6 ±3.6 (n=175) / 70.9 (-6.3 ±3.6 ≈) |

Giả = cùng nhóm khoảng cách d (theo khoảng cách của chính vùng giả). Hết phiên trước khi chạm ⇒ tính "không chạm".

### 1. Bật / xuyên (Chung&Bellotti, vào dải bằng giá đóng) — đối chứng khớp khoảng cách

| Nhóm vùng | TRAIN bật % ±se (n) | giả % | hiệu | TEST bật % ±se (n) | giả % | hiệu |
|---|---|---|---|---|---|---|
| Mọi vùng hiển thị | 58.4 ±1.4 (n=1225) | 60.8 | -2.4 ±1.4 ≈ | 60.0 ±1.9 (n=635) | 59.8 | +0.2 ±2.0 ≈ |
| Có loại B | 62.3 ±1.9 (n=652) | 63.9 | -1.7 ±1.9 ≈ | 63.3 ±2.6 (n=346) | 62.5 | +0.8 ±2.6 ≈ |
| Có loại B15 | 61.9 ±2.4 (n=407) | 65.4 | -3.5 ±2.4 ≈ | 66.5 ±3.1 (n=233) | 63.4 | +3.1 ±3.1 ≈ |
| Có loại C | 62.9 ±3.1 (n=240) | 66.0 | -3.0 ±3.2 ≈ | 72.2 ±3.6 (n=151) | 64.4 | +7.8 ±3.7 ▲ |
| Có loại D | 57.5 ±1.8 (n=760) | 60.2 | -2.7 ±1.8 ≈ | 60.1 ±2.5 (n=383) | 60.9 | -0.9 ±2.5 ≈ |
| Có loại E | 64.8 ±3.2 (n=219) | 65.4 | -0.5 ±3.3 ≈ | 60.3 ±4.5 (n=116) | 59.4 | +0.9 ±4.6 ≈ |
| Có loại F | 68.9 ±5.4 (n=74) | 68.9 | +0.0 ±5.4 ≈ | 75.0 ±7.2 (n=36) | 72.9 | +2.1 ±7.3 ≈ |
| E đúng vai (giá tới từ phía khớp vai) | 63.6 ±4.8 (n=99) | 65.7 | -2.1 ±4.9 ≈ | 50.0 ±8.1 (n=38) | 58.7 | -8.7 ±8.3 ≈ |
| E ngược vai | 67.3 ±4.4 (n=113) | 65.5 | +1.7 ±4.5 ≈ | 66.2 ±5.5 (n=74) | 60.0 | +6.2 ±5.6 ≈ |
| Hợp lưu 1 loại | 53.7 ±2.0 (n=609) | 57.0 | -3.3 ±2.0 ≈ | 54.6 ±2.8 (n=317) | 55.9 | -1.4 ±2.8 ≈ |
| Hợp lưu 2 loại | 62.4 ±2.9 (n=282) | 61.2 | +1.2 ±2.9 ≈ | 61.2 ±4.2 (n=134) | 58.2 | +3.0 ±4.3 ≈ |
| Hợp lưu ≥3 loại | 63.5 ±2.6 (n=334) | 67.1 | -3.6 ±2.7 ≈ | 68.5 ±3.4 (n=184) | 66.0 | +2.5 ±3.5 ≈ |
| Hợp lưu ≥2 loại, có C hoặc E | 64.4 ±2.7 (n=326) | 66.0 | -1.6 ±2.7 ≈ | 69.3 ±3.4 (n=189) | 64.3 | +5.0 ±3.4 ≈ |

≈ = |hiệu| ≤ 2 sai số; ▲/▼ = vượt 2 sai số. "giả %" = cùng nhóm (theo loại của vùng thật được dời) trên vùng giả.

### 1b. Quét thanh khoản (giả thuyết F): trong 10 nến từ lúc vào dải, râu vượt biên xa ≤ 1,5u rồi đóng lại về phía cũ

| Nhóm vùng | TRAIN quét % ±se (n) | giả % | hiệu | TEST quét % ±se (n) | giả % | hiệu |
|---|---|---|---|---|---|---|
| Mọi vùng hiển thị | 25.1 ±1.2 (n=1227) | 24.3 | +0.8 ±1.3 ≈ | 22.0 ±1.6 (n=635) | 23.0 | -0.9 ±1.7 ≈ |
| Có loại B | 20.8 ±1.6 (n=653) | 20.1 | +0.7 ±1.6 ≈ | 17.6 ±2.0 (n=346) | 19.8 | -2.2 ±2.1 ≈ |
| Có loại B15 | 17.4 ±1.9 (n=408) | 18.2 | -0.8 ±1.9 ≈ | 14.6 ±2.3 (n=233) | 18.1 | -3.5 ±2.3 ≈ |
| Có loại F | 17.6 ±4.4 (n=74) | 17.3 | +0.3 ±4.5 ≈ | 5.6 ±3.8 (n=36) | 14.0 | -8.5 ±3.9 ▼ |

### 2. Độ rộng vs nhiễu — râu xuyên quá biên xa ở các ca BẬT (đơn vị u)

| | n bật | p50 | p85 | p95 | % > 0,5u (SL biên xa+0,5u bị quét) |
|---|---|---|---|---|---|
| TRAIN · Vùng thật | 715 | 0.00 | 0.25 | 0.75 | 8.5 ±1.0 |
| TRAIN · Vùng giả | 28256 | 0.00 | 0.29 | 0.77 | 9.2 ±0.2 |
| TEST · Vùng thật | 381 | 0.00 | 0.17 | 0.64 | 8.1 ±1.4 |
| TEST · Vùng giả | 14380 | 0.00 | 0.29 | 0.82 | 9.3 ±0.2 |

### 3. TP = cạnh gần vùng kế tiếp cùng hướng, SL = biên xa + 0,5u, vào ở giá đóng nến bật, tối đa 240 nến, **trừ phí 0,2 giá**

| Tách | Khoảng TP | n thật | TP trước SL % ±se | giả % | R kế hoạch TB (thật/giả) | R sau phí TB (thật/giả) | ± R thật | phút tới TP (trung vị) |
|---|---|---|---|---|---|---|---|---|
| TRAIN | tất cả | 715 | 56.6 ±1.9 | 51.6 | 0.98 / 1.49 | -0.08 / -0.06 | ±0.04 | 3 |
| TRAIN | ≤3u | 508 | 65.4 ±2.1 | 64.9 | 0.56 / 0.60 | -0.08 / -0.07 | ±0.03 | 3 |
| TRAIN | 3–6u | 174 | 35.6 ±3.6 | 35.7 | 1.75 / 1.87 | -0.12 / -0.07 | ±0.10 | 16 |
| TRAIN | >6u | 33 | 33.3 ±8.2 | 20.9 | 3.27 / 4.80 | +0.20 / -0.00 | ±0.32 | 12 |
| TEST | tất cả | 381 | 55.6 ±2.5 | 50.8 | 1.00 / 1.47 | -0.09 / -0.10 | ±0.05 | 4 |
| TEST | ≤3u | 255 | 64.7 ±3.0 | 65.7 | 0.54 / 0.58 | -0.12 / -0.07 | ±0.05 | 2 |
| TEST | 3–6u | 103 | 39.8 ±4.8 | 34.0 | 1.63 / 1.80 | -0.07 / -0.15 | ±0.12 | 13 |
| TEST | >6u | 23 | 26.1 ±9.2 | 18.9 | 3.20 / 4.56 | +0.17 / -0.08 | ±0.45 | 14 |

R sau phí: thắng = +R kế hoạch, thua = −1, hết giờ = lãi/lỗ tạm; trừ 0,2 giá / khoảng SL. Không có vùng kế tiếp ⇒ bỏ.

### 4. Vệ sinh chart (v2)

| Tách | vùng hiển thị TB | rộng trung vị (u / USD) | p90 rộng (u) | % nến đóng trong vùng HIỂN THỊ (thật / giả) | % nến đóng trong BẤT KỲ vùng sống nào | vùng sống trong ±10u | đổi vùng / giờ | tuổi thọ trung vị vùng hiển thị (phút) | % có ≥1 vùng cả 2 phía | % đủ 3+3 |
|---|---|---|---|---|---|---|---|---|---|---|
| TRAIN | 6.00 | 1.00 / 2.30 | 2.70 | 6.9 / 5.0 | 41.4 | 6.5 | 12.4 | 11 | 100.0 | 100.0 |
| TEST | 6.00 | 1.30 / 2.30 | 2.89 | 6.8 / 4.9 | 42.2 | 6.3 | 12.1 | 12 | 100.0 | 100.0 |

### 5. Đóng góp từng loại ứng viên (vùng có chứa loại đó)

| Loại | Tách | n | bật % − giả % | xâm nhập p85 (u) thật / giả | TP % thật / giả | R sau phí TB thật / giả |
|---|---|---|---|---|---|---|
| B | TRAIN | 652 | -1.7 ±1.9 ≈ | 0.17 / 0.21 | 61.6 ±2.4 / 52.9 | -0.06 / -0.06 |
| B | TEST | 346 | +0.8 ±2.6 ≈ | 0.09 / 0.21 | 60.3 ±3.3 / 53.9 | -0.06 / -0.06 |
| B15 | TRAIN | 407 | -3.5 ±2.4 ≈ | 0.15 / 0.16 | 63.9 ±3.0 / 54.8 | -0.05 / -0.05 |
| B15 | TEST | 233 | +3.1 ±3.1 ≈ | 0.06 / 0.17 | 62.6 ±3.9 / 56.2 | -0.05 / -0.03 |
| C | TRAIN | 240 | -3.0 ±3.2 ≈ | 0.09 / 0.18 | 70.9 ±3.7 / 53.1 | -0.03 / -0.11 |
| C | TEST | 151 | +7.8 ±3.7 ▲ | 0.08 / 0.17 | 62.4 ±4.6 / 54.5 | -0.06 / -0.10 |
| D | TRAIN | 760 | -2.7 ±1.8 ≈ | 0.24 / 0.26 | 55.1 ±2.4 / 52.8 | -0.08 / -0.04 |
| D | TEST | 383 | -0.9 ±2.5 ≈ | 0.12 / 0.23 | 55.2 ±3.3 / 52.6 | -0.10 / -0.08 |
| E | TRAIN | 219 | -0.5 ±3.3 ≈ | 0.11 / 0.23 | 58.5 ±4.1 / 54.4 | -0.15 / -0.10 |
| E | TEST | 116 | +0.9 ±4.6 ≈ | 0.33 / 0.29 | 57.1 ±5.9 / 47.5 | -0.06 / -0.19 |
| F | TRAIN | 74 | +0.0 ±5.4 ≈ | 0.02 / 0.00 | 66.7 ±6.6 / 56.1 | +0.05 / -0.07 |
| F | TEST | 36 | +2.1 ±7.3 ≈ | 0.00 / 0.00 | 70.4 ±8.8 / 61.1 | +0.07 / +0.01 |
| E đúng vai (giá tới từ phía khớp vai) | TRAIN | 99 | -2.1 ±4.9 ≈ | 0.00 / 0.23 | 60.3 ±6.2 / 54.2 | -0.11 / -0.10 |
| E đúng vai (giá tới từ phía khớp vai) | TEST | 38 | -8.7 ±8.3 ≈ | 0.28 / 0.20 | 52.6 ±11.5 / 45.4 | -0.14 / -0.23 |
| E ngược vai | TRAIN | 113 | +1.7 ±4.5 ≈ | 0.19 / 0.23 | 59.2 ±5.6 / 54.2 | -0.15 / -0.11 |
| E ngược vai | TEST | 74 | +6.2 ±5.6 ≈ | 0.30 / 0.33 | 59.2 ±7.0 / 49.1 | -0.02 / -0.16 |

### So 2 kiểu đối chứng (mọi vùng hiển thị)

| Tách | bật % thật | giả khớp khoảng cách (hiệu) | giả cũ: biên phiên trước (hiệu) | TP % thật | TP % giả khớp k/c | TP % giả cũ |
|---|---|---|---|---|---|---|
| TRAIN | 58.4 ±1.4 (n=1225) | 60.8 (-2.4 ±1.4 ≈) | 61.8 (-3.5 ±1.5 ▼) | 56.6 | 51.6 | 34.4 |
| TEST | 60.0 ±1.9 (n=635) | 59.8 (+0.2 ±2.0 ≈) | 62.7 (-2.7 ±2.0 ≈) | 55.6 | 50.8 | 36.0 |

### Ứng viên v2

| Loại | số sinh ra cả file | sống TB mỗi nến |
|---|---|---|
| B swing M5 k=5 | 668 | 36.1 |
| B15 swing M15 k=3 | 372 | 19.0 |
| C mốc phiên (+POC trần) | 210 (+45) | 10.3 |
| D số tròn | sinh động | 41.6 |
| E top-5 chạy | 415 (đủ điều kiện thô TB 113/phiên; sinh ra TB 19.8/phiên, max 33) | 2.3 |
| F đỉnh/đáy bằng nhau | 38 | 2.4 |
| (số lần tính lại bộ vùng) | 4061 | |

<!-- NHAN-XET -->

## Nhận xét (≤ 15 dòng)
1. **Mục 8 "tới được" (phép đo chính): ≈ đối chứng ở MỌI ô.** Vùng thật cách ≤3u được chạm trong 30 nến 70,8% (TRAIN) / 72,1% (TEST), vùng giả cùng khoảng cách 70,4% / 72,0%. Ở 3–6u và 6–12u cũng vậy. "Chạm rồi quay lại ≥2u" cũng ≈. ⇒ Xác suất giá tới một vùng **chỉ phụ thuộc khoảng cách**, không phụ thuộc vùng đó là gì. Kỳ vọng TP có thể dựng từ khoảng cách (bảng này dùng được làm bảng tra), nhưng vùng không thêm thông tin.
2. **Bật/xuyên với đối chứng khớp khoảng cách: dấu ▼ của vòng 1 biến mất** (−2,4 ±1,4 TRAIN, +0,2 ±2,0 TEST) ⇒ ▼ cũ đúng là do đối chứng đặt xa giá. Không nhóm nào vượt đối chứng ở cả hai nửa. C có +7,8 ▲ ở TEST nhưng −3,0 ở TRAIN; hợp lưu ≥2 có C/E +5,0 ở TEST, −1,6 ở TRAIN ⇒ không nhất quán, chưa phải bằng chứng.
3. **E có vai:** đúng vai không bật hơn ngược vai (TRAIN 63,6 vs 67,3; TEST 50,0 vs 66,2, n=38). Giả thuyết "delta>0 ⇒ kháng cự" **không được ủng hộ**. **F:** bật ≈ đối chứng, quét ≈ đối chứng (TEST thậm chí ▼, n=36). Giả thuyết dồn stop ⇒ quét **không được ủng hộ**, n quá nhỏ (38 mức F cả file).
4. **TP/SL sau phí: R TB −0,08 / −0,09** (±0,04–0,05), ≈ vùng giả (−0,06 / −0,10). TP% thật cao hơn giả ở hàng "tất cả" chỉ vì TP thật gần hơn (R kế hoạch 0,98 vs 1,49); cùng khoảng TP thì ≈.
5. **Vệ sinh:** vùng sống trong ±10u 8,6 → **6,4 (đạt ≤8)**. % nến đóng trong vùng hiển thị 80% → **6,9% (đạt ≤25%) nhưng phần lớn là do luật 6** (vùng chứa giá bị gỡ ngay). Thước đo trung thực hơn: **41–42% nến đóng nằm trong một vùng sống nào đó**. Đổi vùng 17 → **12/giờ: vẫn TRƯỢT mục tiêu ≤4**. Tuổi thọ trung vị vùng hiển thị chỉ 11–12 phút.
6. Kết luận vòng 2: chart đã thưa và sạch hơn rõ (xem ảnh v2), nhưng **cả 4 thước đo vị trí (bật, quét, tới được, TP sau phí) đều ≈ đối chứng khớp khoảng cách.** Giá trị còn lại của indicator là tổ chức việc quan sát và bảng tra "khoảng cách → xác suất chạm", không phải lợi thế vào lệnh.

## Vấn đề / giới hạn gặp phải
- **% trong vùng hiển thị đạt mục tiêu chủ yếu nhờ định nghĩa.** Luật 6 gỡ vùng ngay khi giá đóng vượt cạnh gần nên tối đa chỉ còn nến vào dải. Để công bằng, vùng giả cũng chỉ được tính tới lần giá đóng vào đầu tiên (5,0% giả vs 6,9% thật). Bật/xuyên cũng chỉ đếm **lần vào dải đầu tiên** của mỗi vùng hiển thị, cho cả thật lẫn giả. Vì thế n thật giảm còn 1225 (TRAIN) / 635 (TEST).
- **Nhấp nháy 12/giờ.** Mỗi lần giá đi 2u hoặc chạm cạnh gần, bộ vùng được tính lại (4061 lần cả file, ≈ 1 lần/7 nến). Mỗi lần tính lại thường đổi ≥1 vùng gần. Luật "ô" chưa đủ; muốn ≤4/giờ cần trễ thay vùng (vd chỉ thêm vùng mới khi vùng cũ bị gỡ) hoặc ô rộng hơn 2u. Tôi chưa thử vì đó là chọn tham số.
- **E top-5 "chạy" trong phiên** (không thể biết top-5 cả phiên khi phiên chưa xong). Mức bị đẩy khỏi top-5 thì chết ngay. Sinh TB 19,8 mức/phiên (tối đa 33) nhưng chỉ sống TB 2,3 mức/nến. `max_one_trade` vẫn = 0 cả file.
- **F hiếm:** 38 mức cả file, 74 + 36 ca vào dải ⇒ sai số ±5–7 điểm, không kết luận được.
- **"Quét" dùng cùng sự kiện vào dải bằng giá đóng.** Ca râu xuyên rồi rút mà không có nến nào đóng trong vùng thì không được tính. Như vậy phép đo quét thiên về ca có đóng trong vùng.
- **Đối chứng khớp khoảng cách** bốc d theo u từ phân phối d thật cùng phía, cùng TRAIN/TEST. Các vùng giả của 50 lần không độc lập (cùng lộ trình giá) ⇒ ± cột giả thực tế lớn hơn công thức.
- **Mục 8:** chạm tính trong phiên. Vùng xuất hiện sát cuối phiên mà hết phiên chưa chạm ⇒ tính "không chạm", áp như nhau cho thật và giả.

## Chỗ phải tự quyết
- B15 sống 3 phiên, không suy giảm. F sống như B (×0,5 sau 2 phiên, chết sau 4), áp luật chuyển vai. F chỉ ghép khi giữa hai đỉnh (đáy) giá chưa vượt quá đỉnh cao hơn + 0,3u. Một swing mới ghép với swing cũ gần giá nhất. Bỏ F trùng (cùng phía, lệch ≤0,3u, còn sống).
- Vai của vùng chứa E = dấu của tổng vai các mức E trong vùng (một vùng có thể có E hai vai, khi đó lấy phần nặng hơn; hòa ⇒ 0, không xếp nhóm).
- Khi tính lại bộ vùng: chọn mới hoàn toàn (2 gần + 1 xa vừa phải mỗi phía), không giữ luật 1,2× của vòng 1. Vùng trùng với vùng cũ (chồng lấn) giữ nguyên mã để đếm đổi vùng cho đúng. Hai vùng cũ khớp vào cùng một vùng mới (nhập nhau) cũng tính là "có vùng chết" ⇒ tính lại.
- Thêm cột "% nến đóng trong BẤT KỲ vùng sống nào" vì chỉ số cũ không còn đo được độ dày.
- Chỉ số "trước (v1)" lấy bằng cách chạy lại engine vòng 1 (gộp 1,0u), chỉ thêm đếm số vùng trong ±10u; kết quả VONG-1 không đổi.
