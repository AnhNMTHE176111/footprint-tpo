# Benzo Trader × Vùng Canh Lệnh — đặt setup và bias vào vùng VCL có cải thiện không?

## 0. Quy tắc ĐĂNG KÝ TRƯỚC (viết và chốt trong code `benzo_vcl.py` trước khi chạy lần đầu; không đổi sau khi thấy TEST)

- **Dữ liệu (QĐ-6):** chỉ `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (giờ UTC). TRAIN = phiên ≤ 2026-09-15, TEST từ 2026-09-16. Phiên sạch (không thin/splice, ≥ 300 nến) = **61** (TRAIN 35, TEST 26) — chia "lệnh/ngày" cho số này. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ tính SL (đều là `kernel.simulate`).
- **Tín hiệu gốc** = đúng ô chính đã báo: A V3 (hồi ≥ 3 nến, thân CF 0,5, hết hạn 30 nến, TP 3R) · B (θ 0,5, cụm 3 nến, TP 3R) · C (xuyên ≥ 2 tick, TP 2R cố định) · D V3 (move ≥ 5, hồi ≤ 70%, không cần Z, TP 2R). Gọi thẳng `detect` của từng `setup_*.py`, không sửa.
- **Vùng VCL** = bộ vùng ĐANG HIỂN THỊ của VCL v5 tại nến vào lệnh (rộng 2–5 giá; vùng tại nến i chỉ dùng nến ≤ i — test cắt dữ liệu trong `vung-canh-lenh/research/test_vcl.py`). Lệnh vào ở giá đóng nến tín hiệu, cùng thời điểm vùng được tính.
- **"Tại vùng VCL"** (phép đo A): có ít nhất một vùng mà giá vào nằm trong vùng ±1 giá ĐÚNG PHÍA. Vai theo phía vùng so với giá (không dùng vai chốt): vùng dưới giá = hỗ trợ, trên giá = kháng cự, ôm giá = "đang chứa giá". MUA hợp lệ khi lo ≤ giá vào ≤ hi + 1 (vùng hỗ trợ hoặc chứa giá); BÁN hợp lệ khi lo − 1 ≤ giá vào ≤ hi. Nhiều vùng hợp lệ ⇒ lấy vùng gần nhất, hòa thì vùng hẹp hơn.
- **Đối chứng dời:** toàn bộ bản đồ vùng VCL của mỗi phiên dời δ, |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, cố định trong (phiên, bản), **100 bản, CÙNG một ma trận δ cho mọi setup và mọi phép đo** (hạt giống 20261024); gắn cờ lại y hệt. **Đối chứng "vào ngẫu nhiên tại vùng":** `kernel.control_sample` (không sửa), mỗi lệnh thật tại vùng rút 1 nến cùng chế độ kernel, cùng điều kiện "tại vùng" theo chiều lệnh, cùng TRAIN/TEST, cùng tháng, cùng chiều, cùng R:R; SL = râu nến đó + 0,3; 200 lần.
- **Bias (phép đo B):** dấu (giá đóng − VWAP tuần) ở nến 19:00 VN (đã bù giờ Mỹ), có hiệu lực từ nến đó và **mang sang** tới ảnh chụp 19:00 kế tiếp trong cùng tuần CME (lệnh pha Á/Âu dùng bias 19:00 của phiên trước — thứ duy nhất đã biết lúc đó; đầu tuần chưa có ảnh chụp ⇒ không xếp). THUẬN = chiều lệnh trùng bias. Độ nhạy (chỉ báo): bias đúng như code setup D (dấu ở nến đầu mỗi (phiên, pha)). **"Bias chỉ bằng vùng":** mỗi lần chạm VCL (máy `lan_cham`: τ = 0, E = 2 giá, G = 5) có vai rõ, nếu giá đóng nến bắt đầu nằm trong vùng ±1 giá đúng phía ⇒ vào theo vai (hỗ trợ ⇒ MUA), SL/TP như phép đo C, 1 lệnh mở; đối chứng = cùng máy trên bản đồ dời.
- **Neo SL/TP theo vùng (phép đo C):** cùng tín hiệu tại vùng, SL = biên xa của vùng ± 0,5 giá (MUA: lo − 0,5; BÁN: hi + 0,5), làm tròn ra xa theo tick, **SL > 4 giá ⇒ bỏ lệnh**; TP = 1,5R và 2R — báo cả hai, không chọn. Mô phỏng không chặn chồng lệnh để giữ đúng cặp tín hiệu với lệnh gốc. Đối chứng = neo theo vùng dời.
- **Số lệnh (phép đo D):** (a) lọc tín hiệu THÔ theo vùng rồi mới mô phỏng (1 lệnh mở) = chiến lược "chỉ vào tại vùng"; (b) bản NỚI = **ô lỏng nhất của lưới 3×3 đã đăng ký trong RESULTS của chính setup đó** (A: số nến hồi tối thiểu 3 → 2, thân nến xác nhận 0,5 → 0,4; B: ngưỡng |delta| nến xác nhận 0,5 → 0,3 × max, cụm 3 → 2 nến; C: độ xuyên cạnh 2 → 1 tick (độ rộng range không chặn lệnh nào ở 90d); D: move tối thiểu 5 → 4 giá, độ hồi tối đa 70% → 90%) — chạy ở mọi nơi / chỉ tại vùng VCL / chỉ tại vùng dời; "hỗn hợp" = tín hiệu gốc ∪ tín hiệu nới tại vùng.
- **Ngưỡng "khác đối chứng có ý nghĩa" (NGUYÊN `PLAN-LAN-CHAM.md` mục 5):** giá trị thật ngoài dải 5–95% đối chứng ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng (T8/T9/T10), VÀ |hiệu| > 2 sai số ở cả TRAIN và TEST. Thiếu một ⇒ "≈ đối chứng". **Chỉ áp dụng khi mỗi nhóm so sánh có ≥ 10 lệnh ở CẢ TRAIN và TEST**, nếu không ghi "không áp dụng (n nhỏ)".
- **Số phép so có phán quyết:** A: 5 (hiệu trong−ngoài vs dời) + 5 (tại vùng vs vào ngẫu nhiên tại vùng); B: 5 (thuận−ngược vs dời) + 2 (chỉ bằng vùng 1,5R/2R); C: 10 (5 nhóm × 2 TP); D: 8 (lọc + nới tại vùng, 4 setup) ⇒ **35 phép so**. Nếu mỗi phép có ~5% vượt ngưỡng do ngẫu nhiên thì kỳ vọng ~2 ô "vượt" mà không có thật; ngưỡng nhiều điều kiện chặt hơn 5% nhiều, nhưng vẫn phải đọc với cảnh giác.
- **Khoảng tin cậy 95%:** lấy mẫu lại (bootstrap) theo lệnh, 10000 lần, hạt giống 0. Sai số đánh giá thấp vì lệnh cùng phiên không độc lập.

## 1. Điều kiện tiên quyết — tái tạo tín hiệu gốc

| Setup | n (cũ → nay) | WR (cũ → nay) | R TB (cũ → nay) | khớp |
|---|---|---|---|---|
| A Phá hồi | 20 → 20 | 10.0% → 10.0% | -0.68 → -0.68 | CÓ |
| B Hấp thụ | 11 → 11 | 27.3% → 27.3% | +0.00 → +0.00 | CÓ |
| C Fade cạnh | 121 → 121 | 27.3% → 27.3% | -0.26 → -0.26 | CÓ |
| D Trap | 31 → 31 | 38.7% → 38.7% | +0.08 → +0.08 | CÓ |

Cả 4 khớp đúng báo cáo cũ ⇒ mọi số dưới đây đo trên đúng tín hiệu đã báo. Thời gian chạy toàn bộ: 80 giây.

**Độ phủ của vùng VCL (để hiểu "tại vùng" chọn lọc tới đâu):** trong các nến của phiên sạch (không pha OFF), vào lệnh ở giá đóng thì **50% nến có vùng hợp lệ cho MUA, 50% cho BÁN** (bản đồ dời 3–15 giá: 41% / 41%). Tức là "tại vùng VCL" là điều kiện khá rộng: gần một nửa số nến đã thỏa.

## 2. BẢNG CHÍNH (gộp TRAIN+TEST)

R TB sau phí, [khoảng tin cậy 95%]. "Dời" = cùng phép đo trên bản đồ vùng dời 3–15 giá: TB [5%; 95%] của 100 bản. Lệnh/ngày chia 61 phiên sạch.

| Setup | Lệnh gốc | TẠI vùng VCL | NGOÀI vùng | Hiệu trong − ngoài (thật ± sai số) | Hiệu khi DỜI vùng | R tại vùng DỜI | Vào NGẪU NHIÊN tại vùng VCL |
|---|---|---|---|---|---|---|---|
| A Phá hồi | n=20 · WR 10% · **-0.68** [-1.09; -0.09] · 0.33/ngày | n=11 · WR 9% · **-0.72** [-1.09; +0.01] · 0.18/ngày | n=9 · WR 11% · **-0.64** [-1.10; +0.25] | **-0.08** ± 0.57 | +0.16 [-0.66; +1.15] | -0.58 [-1.09; +0.07] | -0.08 [-1.12; +0.91] |
| B Hấp thụ | n=11 · WR 27% · **+0.00** [-1.07; +1.10] · 0.18/ngày | n=4 · WR 25% · **-0.11** [-1.18; +1.91] · 0.07/ngày | n=7 · WR 29% · **+0.06** [-1.08; +1.22] | **-0.17** ± 1.25 | +0.10 [-1.51; +2.05] | +0.09 [-1.08; +0.97] | -0.17 [-1.12; +1.58] |
| C Fade cạnh | n=121 · WR 27% · **-0.26** [-0.48; -0.01] · 1.98/ngày | n=85 · WR 24% · **-0.37** [-0.62; -0.09] · 1.39/ngày | n=36 · WR 36% · **+0.01** [-0.42; +0.51] | **-0.38** ± 0.28 | -0.02 [-0.40; +0.35] | -0.27 [-0.49; -0.04] | -0.11 [-0.40; +0.15] |
| D Trap | n=31 · WR 39% · **+0.08** [-0.41; +0.57] · 0.51/ngày | n=14 · WR 50% · **+0.41** [-0.44; +1.26] · 0.23/ngày | n=17 · WR 29% · **-0.20** [-0.74; +0.51] | **+0.61** ± 0.54 | +0.01 [-0.72; +0.94] | +0.08 [-0.42; +0.63] | -0.14 [-0.78; +0.52] |
| GỘP 4 setup | n=183 · WR 27% · **-0.23** [-0.43; -0.03] · 3.00/ngày | n=114 · WR 25% · **-0.30** [-0.54; -0.04] · 1.87/ngày | n=69 · WR 30% · **-0.12** [-0.46; +0.23] | **-0.18** ± 0.22 | +0.01 [-0.28; +0.33] | -0.23 [-0.40; -0.05] | -0.10 [-0.35; +0.10] |

**Phán quyết (ngưỡng mục 0):**

| Setup | Hiệu trong − ngoài vs dời | Tại vùng vs vào ngẫu nhiên tại vùng |
|---|---|---|
| A Phá hồi | không áp dụng (n < 10 ở TRAIN hoặc TEST) | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| B Hấp thụ | không áp dụng (n < 10 ở TRAIN hoặc TEST) | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| C Fade cạnh | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) |
| D Trap | không áp dụng (n < 10 ở TRAIN hoặc TEST) | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| GỘP 4 setup | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) |

### 2.1 Theo TRAIN / TEST / tháng (R TB tại vùng · ngoài vùng · hiệu [dải dời 5–95%])

| Setup | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| A Phá hồi | -1.08 (n7) · -1.09 (n5) · +0.01 [-0.03; +0.03] | -0.09 (n4) · -0.08 (n4) · -0.00 [-1.61; +2.00] | -1.08 (n7) · -1.11 (n3) · +0.03 [-0.03; +0.03] | +0.92 (n2) · -0.06 (n4) · +0.98 [-1.98; +3.17] | -1.09 (n2) · -1.09 (n2) · +0.00 [-0.01; +0.02] |
| B Hấp thụ | +0.20 (n3) · -0.08 (n4) · +0.28 [-2.04; +3.34] | -1.05 (n1) · +0.25 (n3) · — [-2.03; +4.02] | +0.20 (n3) · -1.07 (n1) · — [-3.44; +4.03] | -1.05 (n1) · -0.28 (n5) · — [-2.00; +1.58] | — (n0) · +2.94 (n1) · — [—; —] |
| C Fade cạnh | -0.55 (n45) · +0.10 (n18) · -0.64 [-0.46; +0.56] | -0.17 (n40) · -0.08 (n18) · -0.10 [-0.80; +0.64] | -0.84 (n25) · -0.00 (n14) · -0.84 [-0.52; +0.63] | -0.02 (n34) · +0.56 (n11) · -0.58 [-0.62; +0.67] | -0.38 (n26) · -0.53 (n11) · +0.15 [-0.76; +0.52] |
| D Trap | +0.64 (n7) · +0.25 (n9) · +0.38 [-1.32; +1.51] | +0.19 (n7) · -0.71 (n8) · +0.90 [-1.07; +1.23] | +1.92 (n1) · -0.09 (n6) · — [-2.02; +2.02] | +0.05 (n8) · +0.21 (n7) · -0.17 [-1.17; +1.46] | +0.70 (n5) · -1.09 (n4) · +1.79 [-1.78; +1.55] |
| GỘP 4 setup | -0.44 (n62) · -0.05 (n36) · -0.39 [-0.39; +0.43] | -0.14 (n52) · -0.20 (n33) · +0.07 [-0.57; +0.49] | -0.72 (n36) · -0.21 (n24) · -0.51 [-0.46; +0.63] | +0.01 (n45) · +0.22 (n27) · -0.21 [-0.39; +0.46] | -0.26 (n33) · -0.52 (n18) · +0.26 [-0.65; +0.55] |

### 2.2 Công suất thống kê (khả năng phát hiện) — đọc trước khi tin bất kỳ con số nào ở trên

Hiệu nhỏ nhất phát hiện được với xác suất 80% (mức 5%, hai phía) ≈ 2,8 × độ lệch chuẩn R × √(1/n_trong + 1/n_ngoài):

| Setup | độ lệch chuẩn R | n trong / ngoài | hiệu nhỏ nhất phát hiện được |
|---|---|---|---|
| A Phá hồi | 1.23 | 11 / 9 | **1.54 R** |
| B Hấp thụ | 1.87 | 4 / 7 | **3.29 R** |
| C Fade cạnh | 1.35 | 85 / 36 | **0.75 R** |
| D Trap | 1.50 | 14 / 17 | **1.51 R** |
| GỘP 4 setup | 1.40 | 114 / 69 | **0.60 R** |

Với A, B, D (n ≈ 10–30) chỉ một chênh lệch rất lớn (≥ 1R) mới thấy được; chênh < ~0,5R là KHÔNG THỂ phát hiện trên 90 ngày.

## 3. Phép đo B — bias (giá vs VWAP tuần lúc 19:00 VN)

### 3.1 Trong các lệnh TẠI vùng VCL: THUẬN vs NGƯỢC bias (gộp)

| Setup | THUẬN bias | NGƯỢC bias | chưa có bias | Hiệu thuận − ngược ± sai số | Hiệu khi dời vùng | Phán quyết | Bối cảnh: MỌI lệnh, thuận / ngược |
|---|---|---|---|---|---|---|---|
| A Phá hồi | n=4 · WR 25% · **-0.10** [-1.10; +1.90] | n=7 · WR 0% · **-1.07** [-1.08; -1.06] | 0 | **+0.98** ± 1.00 | +0.40 [-0.03; +1.32] | không áp dụng (n < 10 ở TRAIN hoặc TEST) | -0.72 (n11) / -1.08 (n8) |
| B Hấp thụ | n=3 · WR 33% · **+0.26** [-1.07; +2.90] | n=1 · WR 0% · **-1.22** [—; —] | 0 | **—** ± — | +1.62 [+0.17; +2.75] | không áp dụng (n < 10 ở TRAIN hoặc TEST) | +0.43 (n8) / -1.15 (n2) |
| C Fade cạnh | n=39 · WR 23% · **-0.38** [-0.77; +0.00] | n=36 · WR 22% · **-0.41** [-0.75; +0.01] | 10 | **+0.02** ± 0.30 | -0.04 [-0.50; +0.35] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | -0.35 (n54) / -0.23 (n53) |
| D Trap | n=7 · WR 57% · **+0.63** [-0.63; +1.51] | n=6 · WR 33% · **-0.09** [-1.10; +0.93] | 1 | **+0.72** ± 0.88 | +0.25 [-1.12; +1.53] | không áp dụng (n < 10 ở TRAIN hoặc TEST) | +0.08 (n18) / -0.19 (n10) |
| GỘP 4 setup | n=53 · WR 28% · **-0.19** [-0.55; +0.21] | n=50 · WR 20% · **-0.48** [-0.78; -0.12] | 11 | **+0.29** ± 0.26 | +0.15 [-0.24; +0.55] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | -0.24 (n91) / -0.34 (n73) |

TRAIN / TEST (thuận · ngược, R TB và n, lệnh tại vùng):

| Setup | TRAIN | TEST |
|---|---|---|
| A Phá hồi | -1.09 (n2) · -1.07 (n5) | +0.90 (n2) · -1.08 (n2) |
| B Hấp thụ | +0.92 (n2) · -1.22 (n1) | -1.05 (n1) · — (n0) |
| C Fade cạnh | -0.19 (n17) · -0.67 (n22) | -0.53 (n22) · +0.00 (n14) |
| D Trap | +1.19 (n4) · -0.10 (n3) | -0.11 (n3) · -0.08 (n3) |
| GỘP 4 setup | +0.04 (n25) · -0.70 (n31) | -0.40 (n28) · -0.12 (n19) |

Độ nhạy định nghĩa bias (đúng code setup D: dấu ở nến đầu mỗi (phiên, pha)) — lệnh tại vùng, gộp, chỉ báo:

| Setup | THUẬN | NGƯỢC | hiệu |
|---|---|---|---|
| A Phá hồi | n=5 · WR 20% · **-0.29** [-1.10; +1.30] | n=6 · WR 0% · **-1.07** [-1.08; -1.06] | +0.77 |
| B Hấp thụ | n=3 · WR 33% · **+0.26** [-1.07; +2.90] | n=1 · WR 0% · **-1.22** [—; —] | — |
| C Fade cạnh | n=35 · WR 23% · **-0.39** [-0.82; +0.04] | n=50 · WR 24% · **-0.36** [-0.71; +0.01] | -0.04 |
| D Trap | n=14 · WR 50% · **+0.41** [-0.44; +1.26] | n=0 | — |
| GỘP 4 setup | n=57 · WR 30% · **-0.15** [-0.51; +0.23] | n=57 · WR 21% · **-0.45** [-0.76; -0.13] | +0.29 |

### 3.2 "Bias chỉ bằng vùng" — không cần setup: chạm vùng VCL là vào theo vai vùng (hỗ trợ ⇒ MUA)

| TP | Thật: lệnh/ngày · n · WR · R TB [KTC] | TRAIN | TEST | Dời: R TB [5–95] | Dời: lệnh/ngày | Phán quyết |
|---|---|---|---|---|---|---|
| 1.5R | 45.61 · n=2782 · WR 39% · **-0.12** [-0.16; -0.07] | n=1676 · WR 38% · **-0.16** [-0.21; -0.10] | n=1106 · WR 41% · **-0.06** [-0.14; +0.01] | -0.12 [-0.16; -0.08] | 35.50 [34.22; 36.84] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |
| 2.0R | 43.85 · n=2675 · WR 33% · **-0.10** [-0.16; -0.05] | n=1617 · WR 32% · **-0.15** [-0.22; -0.08] | n=1058 · WR 35% · **-0.04** [-0.12; +0.05] | -0.11 [-0.15; -0.07] | 34.09 [32.87; 35.25] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |

## 4. Phép đo C — "đặt setup vào vùng": neo SL/TP theo vùng VCL

Cùng tín hiệu tại vùng; SL = biên xa vùng ± 0,5 giá (bỏ nếu > 4 giá); so với R GỐC của chính các lệnh đó (hiệu theo cặp) và với neo theo vùng dời.

| Setup | TP | n (bỏ vì SL > 4) | SL TB (giá) | R neo: WR · R TB [KTC] | R gốc cùng lệnh | Hiệu neo − gốc [KTC theo cặp] | Neo theo vùng DỜI | Phán quyết |
|---|---|---|---|---|---|---|---|---|
| A Phá hồi | 1.5R | 11 (0) | 2.66 | n=11 · WR 36% · **-0.18** [-0.85; +0.51] | -0.72 | +0.54 [-0.16; +1.33] | -0.22 [-0.81; +0.37] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| A Phá hồi | 2.0R | 11 (0) | 2.66 | n=11 · WR 27% · **-0.27** [-1.07; +0.54] | -0.72 | +0.45 [-0.17; +1.24] | -0.26 [-1.09; +0.45] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| B Hấp thụ | 1.5R | 4 (0) | 2.42 | n=4 · WR 25% · **-0.48** [-1.15; +0.79] | -0.11 | -0.37 [-1.11; +0.02] | -0.46 [-1.16; +0.20] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| B Hấp thụ | 2.0R | 4 (0) | 2.42 | n=4 · WR 25% · **-0.35** [-1.15; +1.17] | -0.11 | -0.24 [-0.74; +0.02] | -0.39 [-1.16; +0.43] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| C Fade cạnh | 1.5R | 79 (6) | 2.30 | n=79 · WR 25% · **-0.48** [-0.71; -0.23] | -0.39 | -0.08 [-0.26; +0.09] | -0.28 [-0.53; -0.04] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| C Fade cạnh | 2.0R | 79 (6) | 2.30 | n=79 · WR 23% · **-0.42** [-0.69; -0.13] | -0.39 | -0.03 [-0.22; +0.16] | -0.23 [-0.49; +0.08] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| D Trap | 1.5R | 14 (0) | 2.23 | n=14 · WR 50% · **+0.13** [-0.57; +0.83] | +0.41 | -0.28 [-0.41; -0.15] | -0.12 [-0.62; +0.54] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| D Trap | 2.0R | 14 (0) | 2.23 | n=14 · WR 43% · **+0.17** [-0.51; +1.02] | +0.41 | -0.25 [-0.68; -0.01] | -0.09 [-0.69; +0.69] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| GỘP 4 setup | 1.5R | 108 (6) | 2.33 | n=108 · WR 30% · **-0.37** [-0.58; -0.15] | -0.31 | -0.05 [-0.21; +0.10] | -0.26 [-0.45; -0.06] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| GỘP 4 setup | 2.0R | 108 (6) | 2.33 | n=108 · WR 26% · **-0.33** [-0.57; -0.08] | -0.31 | -0.02 [-0.18; +0.15] | -0.23 [-0.45; +0.03] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |

TRAIN / TEST (R neo · n):

| Setup | TP | TRAIN | TEST |
|---|---|---|---|
| A Phá hồi | 1.5R | n=7 · WR 43% · **-0.03** [-0.75; +0.99] | n=4 · WR 25% · **-0.44** [-1.07; +0.81] |
| A Phá hồi | 2.0R | n=7 · WR 29% · **-0.25** [-1.09; +0.62] | n=4 · WR 25% · **-0.31** [-1.07; +1.18] |
| B Hấp thụ | 1.5R | n=3 · WR 33% · **-0.29** [-1.18; +1.42] | n=1 · WR 0% · **-1.05** [—; —] |
| B Hấp thụ | 2.0R | n=3 · WR 33% · **-0.12** [-1.18; +1.92] | n=1 · WR 0% · **-1.05** [—; —] |
| C Fade cạnh | 1.5R | n=44 · WR 23% · **-0.53** [-0.82; -0.19] | n=35 · WR 29% · **-0.41** [-0.76; -0.04] |
| C Fade cạnh | 2.0R | n=44 · WR 18% · **-0.55** [-0.89; -0.20] | n=35 · WR 29% · **-0.26** [-0.69; +0.18] |
| D Trap | 1.5R | n=7 · WR 57% · **+0.34** [-0.71; +1.08] | n=7 · WR 43% · **-0.08** [-0.85; +0.71] |
| D Trap | 2.0R | n=7 · WR 43% · **+0.20** [-0.70; +1.47] | n=7 · WR 43% · **+0.14** [-0.78; +1.07] |
| GỘP 4 setup | 1.5R | n=61 · WR 30% · **-0.36** [-0.64; -0.07] | n=47 · WR 30% · **-0.37** [-0.69; -0.04] |
| GỘP 4 setup | 2.0R | n=61 · WR 23% · **-0.41** [-0.71; -0.07] | n=47 · WR 30% · **-0.22** [-0.61; +0.17] |

## 5. Phép đo D — SỐ LỆNH

### 5.1 Lọc theo vùng chỉ có thể GIẢM số lệnh

| Setup | Gốc: lệnh/ngày · R TB | Chỉ vào tại vùng VCL (lọc tín hiệu thô rồi mô phỏng): lệnh/ngày · n · WR · R TB [KTC] | Tại vùng DỜI: lệnh/ngày · R TB [5–95] | Phán quyết |
|---|---|---|---|---|
| A Phá hồi | 0.33 · -0.68 | 0.18 · n=11 · WR 9% · **-0.72** [-1.09; +0.01] | 0.13 · -0.58 [-1.09; +0.07] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| B Hấp thụ | 0.18 · +0.00 | 0.07 · n=4 · WR 25% · **-0.11** [-1.18; +1.91] | 0.08 · +0.09 [-1.08; +0.97] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| C Fade cạnh | 1.98 · -0.26 | 1.41 · n=86 · WR 23% · **-0.38** [-0.63; -0.10] | 0.83 · -0.30 [-0.52; -0.07] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |
| D Trap | 0.51 · +0.08 | 0.23 · n=14 · WR 50% · **+0.41** [-0.44; +1.26] | 0.20 · +0.08 [-0.42; +0.63] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| **Cộng 4 setup** | **3.00** | **1.89** | | |

### 5.2 Nới cổng chỉ khi tại vùng VCL (vùng thay vai trò cổng) — số lệnh có TĂNG không?

Bản nới = ô lỏng nhất của lưới 3×3 đã đăng ký của mỗi setup (không chọn theo kết quả). "Hỗn hợp" = tín hiệu gốc ở mọi nơi + tín hiệu nới chỉ khi tại vùng (đây là cách duy nhất để vùng làm TĂNG số lệnh mà không bỏ lệnh gốc).

| Setup | Cổng được nới | Gốc: lệnh/ngày · R TB | Nới MỌI nơi: lệnh/ngày · R TB | Nới CHỈ tại vùng VCL: lệnh/ngày · n · WR · R TB [KTC] | Nới tại vùng DỜI: lệnh/ngày · R TB [5–95] | Hỗn hợp: lệnh/ngày · R TB | Hỗn hợp với vùng DỜI: lệnh/ngày · R TB [5–95] | Phán quyết (nới tại VCL vs dời) |
|---|---|---|---|---|---|---|---|---|
| A Phá hồi | số nến hồi tối thiểu 3 → 2, thân nến xác nhận 0,5 → 0,4 | 0.33 · -0.68 | 0.46 · -0.80 | 0.21 · n=13 · WR 8% · **-0.77** [-1.09; -0.16] | 0.18 · -0.74 [-1.08; -0.27] | 0.36 · -0.72 | 0.38 · -0.74 [-0.77; -0.70] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| B Hấp thụ | ngưỡng |delta| nến xác nhận 0,5 → 0,3 × max, cụm 3 → 2 nến | 0.18 · +0.00 | 0.54 · -0.13 | 0.25 · n=15 · WR 13% · **-0.58** [-1.13; +0.22] | 0.23 · -0.02 [-0.67; +0.62] | 0.39 · -0.27 | 0.38 · -0.04 [-0.43; +0.37] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| C Fade cạnh | độ xuyên cạnh 2 → 1 tick (độ rộng range không chặn lệnh nào ở 90d) | 1.98 · -0.26 | 2.13 · -0.23 | 1.48 · n=90 · WR 23% · **-0.38** [-0.64; -0.11] | 0.89 · -0.26 [-0.44; -0.01] | 2.13 · -0.27 | 2.07 · -0.25 [-0.30; -0.21] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |
| D Trap | move tối thiểu 5 → 4 giá, độ hồi tối đa 70% → 90% | 0.51 · +0.08 | 1.28 · -0.05 | 0.59 · n=36 · WR 39% · **+0.07** [-0.42; +0.57] | 0.54 · -0.06 [-0.34; +0.28] | 0.85 · +0.01 | 0.83 · -0.01 [-0.17; +0.15] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| **Cộng 4 setup** | | **3.00** · -0.23 | **4.41** · -0.22 | **2.52** · n=154 · WR 25% · **-0.33** [-0.54; -0.11] | 1.83 | **3.74** · n=228 · WR 27% · **-0.25** [-0.43; -0.06] | 3.67 | |

Tín hiệu thô (trước luật 1 lệnh mở): A gốc 21 → nới 30; B gốc 11 → nới 33; C gốc 146 → nới 158; D gốc 31 → nới 82.

Không nới được sạch (ghi rõ, không đo): các luật loại cứng trong code — A: cấm 18:00–19:20 VN, loại hình V; B: loại khi đang phá VA/TREND cùng chiều; C: chỉ chế độ CÂN BẰNG (không có công tắc); D: bias + chế độ ≠ CÂN BẰNG — đều không có tham số trong `detect`, bỏ chúng phải sửa logic setup, nằm ngoài phạm vi "không sửa code Benzo".

## 6. Hình minh hoạ

- TRAIN, phiên 2026-09-15 (7 lệnh tại vùng — phiên NHIỀU lệnh tại vùng nhất của TRAIN, chọn để minh hoạ, KHÔNG phải ca điển hình): [img/benzo_vcl_TRAIN_2026-09-15.png](img/benzo_vcl_TRAIN_2026-09-15.png)
- TEST, phiên 2026-10-02 (6 lệnh tại vùng — phiên NHIỀU lệnh tại vùng nhất của TEST, chọn để minh hoạ, KHÔNG phải ca điển hình): [img/benzo_vcl_TEST_2026-10-02.png](img/benzo_vcl_TEST_2026-10-02.png)

<!-- NHAN-XET -->
## 7. Kết luận (viết tay từ số ở trên; phần này được giữ khi chạy lại script)

**Phán quyết theo ngưỡng đã đăng ký: 0 / 35 phép so vượt ngưỡng; 15 phép "≈ đối chứng"; 20 phép không áp dụng được vì n < 10 ở TRAIN hoặc TEST** (toàn bộ A, B, D đứng riêng).

1. **Đặt setup vào vùng VCL KHÔNG cải thiện.** Gộp 4 setup: lệnh tại vùng −0,30R (n = 114) so với ngoài vùng −0,12R (n = 69); hiệu −0,18 ± 0,22,
   nằm giữa dải bản đồ vùng dời [−0,28; +0,33]. Vào NGẪU NHIÊN tại vùng VCL cho −0,10R [−0,35; +0,10] — setup thật tại vùng không hơn vào bừa tại vùng.
   Lý do dễ hiểu: vùng VCL phủ ~50% số nến (vùng dời vẫn phủ ~41%), nên "tại vùng" gần như không chọn lọc gì.
2. **Từng setup:** C (n đủ nhất) tại vùng còn KÉM hơn ngoài vùng (−0,37 vs +0,01), lệch ngoài dải ở TRAIN nhưng trong dải ở TEST ⇒ ≈ đối chứng.
   D tại vùng đẹp nhất (+0,41R, n = 14, ngoài vùng −0,20R, n = 17) nhưng hiệu +0,61 ± 0,54 nằm trong dải dời [−0,72; +0,94]; với n này chỉ chênh
   ≥ 1,5R mới phát hiện được ⇒ **không được đọc là "D hợp với VCL"**. A (n = 11 tại vùng) và B (n = 4) quá ít để nói gì.
3. **Bias:** trong lệnh tại vùng, thuận bias −0,19R (n = 53) vs ngược −0,48R (n = 50), nhưng TRAIN +0,74 rồi TEST −0,28 đổi dấu, và nằm trong dải dời.
   "Bias chỉ bằng vùng" (chạm vùng là vào theo vai vùng, không setup): −0,12R ở TP 1,5R và −0,10R ở TP 2R, ~44–46 lệnh/ngày — **y hệt** vùng dời
   (−0,12 / −0,11). Vùng VCL tự nó không cho hướng; đúng kỳ vọng ≈ 0 (âm vì phí).
4. **Neo SL/TP theo vùng:** gộp −0,37R (1,5R) / −0,33R (2R) so với −0,31R của chính các lệnh đó khi để SL/TP gốc; hiệu theo cặp ≈ 0. Neo theo vùng DỜI
   cho −0,26 / −0,23, tức không kém hơn neo theo vùng thật. A "tốt lên" +0,54R chỉ vì hạ TP 3R → 1,5R (vùng dời cũng cho y vậy), không nhờ vùng. D kém đi −0,28R.
5. **Số lệnh:** lọc theo vùng chỉ GIẢM: 3,00 → 1,89 lệnh/ngày (−37%), R không tốt lên. Cách duy nhất để TĂNG là nới cổng chỉ khi tại vùng:
   "hỗn hợp" 3,74 lệnh/ngày (+0,74/ngày, +25%) với R −0,25 (gốc −0,23) — nhưng dùng vùng DỜI cũng tăng gần y hệt (3,67/ngày) ⇒ lệnh tăng là do nới cổng,
   không phải do vùng VCL chọn đúng chỗ. Vẫn rất xa mục tiêu 10–20 lệnh/ngày.
6. **Độ chắc:** đủ để nói **không có cải thiện LỚN** ở mức gộp (phát hiện được chênh ≥ ~0,6R, đo ra −0,18R). KHÔNG đủ để nói gì về chênh nhỏ (< 0,5R) hay về
   A/B/D riêng lẻ. Khớp với các phép đo cũ: % đảo chiều của vùng VCL ≈ vùng đặt bừa; hợp lưu SessionZones không mạnh hơn.

### Chỗ tự quyết (ghi rõ)
- Cờ vùng dùng vùng hiển thị TẠI nến tín hiệu (tính cả nến đó), vì lệnh vào ở giá đóng nến đó — cùng thời điểm.
- Nhiều vùng hợp lệ ⇒ vùng gần giá nhất (hòa thì hẹp hơn); chỉ ảnh hưởng phép đo C (neo SL).
- Bias 19:00 cho lệnh pha Á/Âu = bias 19:00 của phiên TRƯỚC (cùng tuần); đầu tuần chưa có ⇒ không xếp (11 lệnh tại vùng). Độ nhạy theo định nghĩa của code D cho cùng bức tranh.
- "Gộp 4 setup" = cộng lệnh của 4 setup đã mô phỏng riêng (không áp luật 1 lệnh mở chéo giữa các setup), như TONG-KET.
- Phép đo C mô phỏng không chặn chồng lệnh để giữ đúng cặp tín hiệu; phép đo D và "bias chỉ bằng vùng" dùng 1 lệnh mở.
- Bản nới = ô lỏng nhất của lưới 3×3 đã có, để không chọn theo kết quả. Các luật loại cứng (giờ cấm, chế độ CÂN BẰNG, phá VA…) không nới vì phải sửa code setup.
- Đối chứng "vào ngẫu nhiên tại vùng" dùng `kernel.control_sample` với mã ghép (chế độ | có vùng cho MUA | cho BÁN | TRAIN/TEST | tháng).

### Điều chưa chắc
- n nhỏ: A 11, B 4, D 14 lệnh tại vùng trên 61 phiên; mọi con số riêng lẻ của ba setup này chỉ là mô tả.
- Một hợp đồng (GCZ26), một mùa, 90 ngày; lệnh cùng phiên không độc lập nên sai số và khoảng tin cậy còn đánh giá THẤP độ bất định.
- Bộ vùng VCL lấy từ cache `vung-canh-lenh/research/report/cache_lc/v5.pkl` (không commit, khớp 4749 lần chạm của LAN-CHAM.md); thiếu cache script tự chạy lại engine.
