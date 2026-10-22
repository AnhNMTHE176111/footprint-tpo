# RESULTS-A-V4 — Setup A "Phá hồi": vùng mới + cú phá có đà + bỏ cấm 18:00–19:20

Sinh bởi `setup_a_v4.py` (tất định, hạt cố định) theo đặc tả `plans/BENZO-A-V4-plan.md`. Dữ liệu (QĐ-6): CHỈ `fp_GCZ26_XCEC_Time_20260723-20261021_90d`, giờ UTC (VN = UTC+7). TRAIN = phiên ≤ 2026-09-15, TEST từ 2026-09-16. **61 phiên sạch** (TRAIN 35 / TEST 26) — "lệnh/ngày" chia cho 61. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ tính SL (`kernel.simulate`); 1 lệnh mở cùng lúc (A đứng riêng, KHÔNG gộp với B/C/D). TP 3R (hoà vốn sau phí ≈ 27% WR); 2R chỉ là độ nhạy.

## 0. Đăng ký trước (hằng số commit `4e76f63` TRƯỚC khi chạy lần đầu)

- **Ba tham số tự do mới / tái dùng:** D_MIN = 2.0 giá (cực trị phải cách cạnh ≥ 2 giá mới "đã trang bị" — được canh), T_HOI = 30 nến tính từ CỰC TRỊ CUỐI (hết hạn), độ sâu hủy = 1.0 giá (= vùng chạm, tái dùng). Giữ nguyên: vùng chạm E ± 1, ≥ 3 nến hồi, thân CF 0,5, SL = max(râu CF, mép xa ± 1) + 0,3, sàn 5 nến, trần 4 giá, TP 3R, ≤ 2 lệnh/(phiên, vùng, chiều), bỏ 3 nến sau nến dài nhất phiên, bỏ pha OFF và phiên thin/splice.
- **Vùng A-v4:** VWAP tuần, VWAP ngày (chỉ khi tuần/phiên ≥ 30 nến), HVN tuần ≤ 3 (gộp 3 tuần CME đã đóng; DẢI = PeakSharpness 90%% kẹp ≤ 2 giá), HVN ngày ≤ 3 (phiên đầy đủ trước; điểm), VAH/VAL ngày = VA 70%% của phiên đầy đủ TRƯỚC (cách hiểu (a) của plan; cách (b) "VA đang hình thành" chạy như độ nhạy). A-v4+ thêm VAH/VAL Âu (chốt 19:00) hoặc IB (chốt 20:20) ở pha Mỹ.
- **Đối chứng:** ĐC1 = vào ngẫu nhiên trong cùng trạng thái phá đã trang bị (chạm E, hợp lệ, bỏ nhịp hồi/CF), mỗi lệnh thật 1 nến cùng chiều + loại vùng + TRAIN/TEST, 200 lần; ĐC2 = `kernel.control_sample` (cùng vùng, cùng chế độ kernel, cùng chiều; SL râu + 0,3), 200 lần; ĐC3 = dời cả bản đồ vùng δ ~ U[3, 15] giá dấu ngẫu nhiên theo (phiên, bản), 100 bản, hạt 20261024 (cùng ma trận với BENZO-VCL), chạy lại nguyên máy trạng thái.
- **Ngưỡng "khác đối chứng"** (NGUYÊN `PLAN-LAN-CHAM.md` mục 5): thật ngoài dải 5–95%% đối chứng ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số ở cả hai; chỉ áp dụng khi ≥ 10 lệnh ở CẢ TRAIN và TEST, nếu không ghi "không áp dụng". KTC 95%% = bootstrap 10 000 lần hạt 0 (đánh giá thấp vì lệnh cùng phiên không độc lập).
- **Tiêu chí port (plan mục 4):** T1 = n ≥ 40 · R TEST ≥ R TEST gốc và n TEST ≥ 15 · R TRAIN ≥ −0,30 · không đối chứng nào nói "thật KÉM hơn" · test xanh · khung 18:00–19:20 không tệ hơn phần còn lại quá 0,5R (n ≥ 10). T2 ("có lợi thế đo được") = TRAIN > 0 và TEST > 0, n TEST ≥ 30, vượt CẢ BA đối chứng.
- **Bảng chính KHÔNG chặn** CF trong 19:20–20:30 VN (giống A-V3 gốc của Python); bản CÓ chặn (đúng engine C#) in kèm ở 4.2.

### Chỗ tự quyết (plan không nói rõ — chọn hướng hợp lý nhất, ghi lại)

- Q1 Thứ tự trong một nến M1 i là nến cuối của M5: xử lý sự kiện M5 (mở / hủy) TRƯỚC, rồi mới quét nến i (giống V3 và C#):
     trạng thái vừa mở ở i không xét vào lệnh ở i; trạng thái vừa hủy ở i không vào ở i.
- Q2 Vùng điểm + độ sâu hủy 1 giá: M5 đóng phía bên kia điểm <= 1 giá thì (z,+1) vẫn sống; KHÔNG mở (z,−1) song song
     (giữ bất biến "hai chiều của cùng z không cùng PHA" của plan). Đếm số lần bị chặn kiểu này.
- Q3 Band VA cũ (Z='old') trong logic đà: canh lên = VAH, canh xuống = VAL như V3; SL qua E ∓ 1 (như V3), KHÔNG qua mép xa
     của band (VA rộng 10–30 giá ⇒ mọi lệnh bị trần 4 giá loại); M5 đóng ngoài phía đối diện ⇒ hủy.
- Q4 Chân cú phá (leg) với vùng động: "nến đóng phía trong" so với giá trị vùng TẠI nến đó (VWAP thô, chưa áp Warm).
- Q5 "armed" là cờ dính, chỉ xét lại khi lập cực trị mới (đúng mã giả 2.2 bước 3). Đếm số lệnh mà lúc vào cực trị đã
     không còn cách E(i) >= D_MIN (cạnh động trôi lại gần) — chỉ báo.
- Q6 Hai vùng cùng nến: vùng không được chọn coi như không vào lệnh (đi tiếp bước 3–4 bình thường).
- Q7 Vùng cố định đổi giá trị / nguồn (band cũ đổi EU↔Y↔IB; VA Âu/IB bắt đầu/hết) ⇒ trạng thái về NGỦ ở sự kiện M5 kế tiếp
     (giống V3: V3 hủy khi đổi nguồn ở nến M5 kế tiếp).
- Q9 Plan 2.2 bước 4 viết "hết hạn ⇒ NGỦ; cú M5 ngoài kế tiếp sẽ mở PHA mới". Làm ĐÚNG CHỮ (bản chính): giá vẫn ở ngoài
     thì M5 kế tiếp mở lại ngay (chân lùi 60 nến, cực trị = cực trị trong 60 nến đó). Hệ quả: số "trạng thái PHA" phình lên
     (mở lại liên tục khi giá nằm xa vùng cả phiên) và lệnh có thể vào ở lần hồi về vùng sau một đoạn đi ngang dài. Đăng ký
     TRƯỚC khi chạy một độ nhạy `after_inside=True` (phải có M5 không đóng ngoài rồi mới mở lại) và tách lệnh theo cờ reopen.
- Q8 Nến M5 chỉ tính "đã đóng" khi còn nến sau nó trong dữ liệu hoặc nó là phút thứ 5 (zones_a_v4.m5_close_mask) — để
     chạy trên dữ liệu cắt ra đúng kết quả chạy đầy đủ.
- Q10 Tên file test là `test_setup_a_v4.py` (theo yêu cầu giao việc; plan ghi `test_a_v4.py`). Không tạo `zones` trong kernel: hàm vùng mới ở `zones_a_v4.py`, kernel không đổi.
- Q11 Đối chứng luật 19:20–20:30: plan ghi "24 cửa sổ dời ±10 phút (sm 580..1200)" — không ra đúng 24 cửa sổ được; dùng MỌI cửa sổ 70 phút bắt đầu 580..1130 bước 10 phút, bỏ cửa sổ chồng lên 19:20–20:30 ⇒ 43 cửa sổ.

## 1. Tái tạo gốc

Máy chung `detect()` ở chế độ (band cũ, logic V3, cấm 18:00–19:20) ra **đúng từng lệnh** của `setup_a_pha_hoi.detect(expire=30)` (test `test_reproduce_v3_baseline`): **n = 20, WR 10.0%, R TB -0.68** (KTC 95% [-1.09; -0.09]); TRAIN 12 / -1.08 · TEST 8 / -0.08. ⇒ khớp báo cáo cũ (n=20, WR 10%, −0,68).

## 2. Chẩn đoán của Fable (plan mục 1) — chạy lại bằng script này

Band cũ (VA Âu/IB/VA hôm qua), 61 phiên sạch; mỗi lần M5 đóng ngoài khi chưa có trạng thái = 1 trạng thái.

| số đo | Fable ghi | chạy lại |
|---|---|---|
| số trạng thái phá | 532 | 532 |
| cực trị cuối sau nến phá: trung vị / p75 / p90 (nến) | 7 / 28 / 124 | 7 / 28 / 124 |
| cực trị sau nến phá > 30 nến (bị expire=30 cắt) | 130 (24%) | 130 (24%) |
| khoảng cách cực trị–cạnh: trung vị / p75 (giá) | 7,1 / 16 | 7.1 / 16.4 |
| tỉ lệ cực trị < 2 giá | 12% | 12% |
| kết thúc vì M5 đóng lại trong | 482 (91%) | 482 (91%) |
| tuổi thọ trung vị (nến) | 20 | 20 |
| hết phiên / đảo phía | 46 / 4 | 46 / 4 |
| có chạm lại E trước khi hủy | 92% | 492 (92%) |
| lần chạm đầu: trung vị nến sau nến phá | 2 | 2 |
| chạm lại SAU cực trị cuối | 256 | 256 |
| chạm lần đầu > 30 nến sau nến phá | 16% số ca có chạm | 80 (16%) |
| bị hủy mà chưa từng chạm E (phá hụt thật) | 15 | 15 |

## 3. Công suất thống kê — ĐỌC TRƯỚC bảng chính

Hiệu nhỏ nhất phát hiện được với xác suất 80% (mức 5%, hai phía) ≈ 2,8 × độ lệch chuẩn R × √(1/n₁ + 1/n₂). Với A-v4: độ lệch chuẩn R = **1.60**, n = 218 (TRAIN 119 / TEST 99).

| so sánh | hiệu nhỏ nhất phát hiện được |
|---|---|
| R TB A-v4 so với 0 (một mẫu, 2,8·σ/√n) | **0.30 R** |
| A-v4 so với A-V3 gốc (n = 218 vs 20) | **1.04 R** |
| A-v4 so với một lần rút đối chứng cùng cỡ (n vs n) | **0.43 R** |
| riêng TEST so với đối chứng (n TEST = 99) | **0.64 R** |

⇒ Chênh nhỏ hơn các con số này KHÔNG thể phân biệt với may rủi trên 90 ngày.

## 4. BẢNG CHÍNH (TP 3R, sau phí, 1 lệnh mở cùng lúc)

R TB [KTC 95%]. "thô" = số tín hiệu trước luật 1 lệnh mở. T8 gồm 29–31/7.

| cấu hình | Z vùng | M logic | H 18:00–19:20 | n (lệnh/ngày) | WR | R TB [KTC 95%] | kỳ vọng giá/lệnh | chuỗi thua | TRAIN n / R | TEST n / R | T8 | T9 | T10 | thô |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-V3 gốc | cũ | V3 | cấm | 20 (0.33) | 10.0% | **-0.68** [-1.09; -0.09] | -1.98 | 12 | 12 / -1.08 | 8 / -0.08 | 10 / -1.09 | 6 / +0.27 | 4 / -1.09 | 21 |
| (a) chỉ đổi vùng | mới | V3 | cấm | 101 (1.66) | 23.8% | **-0.13** [-0.45; +0.22] | -0.47 | 11 | 53 / -0.11 | 48 / -0.16 | 30 / -0.28 | 45 / -0.02 | 26 / -0.15 | 107 |
| (b) chỉ đổi logic đà | cũ | đà | cấm | 46 (0.75) | 17.4% | **-0.39** [-0.82; +0.04] | -1.31 | 10 | 25 / -0.44 | 21 / -0.34 | 16 / -0.83 | 16 / +0.42 | 14 / -0.82 | 49 |
| (c) chỉ bỏ cấm giờ | cũ | V3 | không cấm | 21 (0.34) | 9.5% | **-0.70** [-1.08; -0.13] | -2.11 | 14 | 14 / -1.08 | 7 / +0.06 | 11 / -1.08 | 7 / +0.08 | 3 / -1.09 | 22 |
| (d) A-v4 | mới | đà | không cấm | 218 (3.57) | 19.7% | **-0.30** [-0.50; -0.07] | -0.71 | 12 | 119 / -0.11 | 99 / -0.52 | 76 / -0.40 | 78 / -0.00 | 64 / -0.52 | 245 |
| A-v4+ (thêm VA Âu/IB) | mới+ | đà | không cấm | 252 (4.13) | 18.7% | **-0.34** [-0.53; -0.14] | -0.86 | 13 | 136 / -0.17 | 116 / -0.53 | 88 / -0.40 | 90 / -0.10 | 74 / -0.54 | 284 |
| (phụ) vùng mới + V3 + bỏ cấm | mới | V3 | không cấm | 103 (1.69) | 25.2% | **-0.07** [-0.42; +0.27] | -0.32 | 9 | 55 / +0.00 | 48 / -0.17 | 32 / -0.08 | 45 / -0.02 | 26 / -0.15 | 108 |
| (phụ) vùng cũ + đà + bỏ cấm | cũ | đà | không cấm | 48 (0.79) | 16.7% | **-0.42** [-0.83; -0.00] | -1.41 | 10 | 28 / -0.51 | 20 / -0.30 | 17 / -0.85 | 18 / +0.25 | 13 / -0.80 | 51 |
| (phụ) vùng mới + đà + cấm | mới | đà | cấm | 213 (3.49) | 20.7% | **-0.26** [-0.47; -0.03] | -0.59 | 12 | 116 / -0.09 | 97 / -0.46 | 75 / -0.39 | 76 / +0.02 | 62 / -0.44 | 240 |

### 4.1 Tách đóng góp (2×2×2)

Một yếu tố đổi từ A-V3 gốc (giữ hai yếu tố kia như gốc), và hiệu TRUNG BÌNH của yếu tố đó trên cả 4 cặp ô của khối 2×2×2 (vùng cũ/mới × V3/đà × cấm/không). "phần tương tác" = (d) − gốc − tổng ba hiệu một yếu tố.

| yếu tố | Δ n (từ gốc) | Δ lệnh/ngày | Δ WR (điểm %) | Δ R TB | Δ n TB 4 cặp | Δ WR TB 4 cặp | Δ R TB TB 4 cặp |
|---|---|---|---|---|---|---|---|
| đổi vùng (cũ → 6 loại mới) | +81 | +1.33 | +13.8 | +0.55 | +125.0 | +9.0 | +0.36 |
| logic đà (V3 → đà) | +26 | +0.43 | +7.4 | +0.29 | +70.0 | +1.5 | +0.06 |
| bỏ cấm 18:00–19:20 | +1 | +0.02 | -0.5 | -0.02 | +2.5 | -0.2 | -0.01 |
| phần tương tác ((d) − gốc − tổng 3 dòng trên) | +90 | +1.48 | -11.0 | -0.43 | | | |
| **tổng: (d) A-v4 − gốc** | **+198** | **+3.25** | **+9.7** | **+0.39** | | | |

### 4.2 Theo pha, khung giờ, phễu trạng thái, bản có chặn 19:20–20:30

Khung 18:00–19:20 = nến M5 phá HOẶC nến CF rơi trong sm 780..859. Khung 19:20–20:30 = nến CF trong sm 860..929. Phễu: "mở" = số lần mở trạng thái PHA (logic đà: kể cả mở lại ngay sau hết hạn — xem Q9), "trang bị" = trạng thái từng đạt D_MIN, "có lệnh" = trạng thái cho ≥ 1 tín hiệu; cột sau dấu ‖ là riêng trạng thái MỞ MỚI (không phải mở lại): mở / trang bị / có lệnh — con số so được với 532 trạng thái của chẩn đoán mục 2.

| cấu hình | Á n / R | Âu n / R | Mỹ n / R | 18:00–19:20 n · WR · R | phần còn lại R | 19:20–20:30 n · R | phễu mở / trang bị / có lệnh ‖ MỞ MỚI: mở / trang bị / có lệnh | CÓ chặn 19:20–20:30: n · WR · R | TEST |
|---|---|---|---|---|---|---|---|---|---|
| A-V3 gốc | 6 / -0.43 | 3 / -1.08 | 11 / -0.71 | 0 · — · — | -0.68 | 2 · -1.07 | 535 / — / 20 ‖ 535 / — / 20 | 18 · 11.1% · -0.64 | 7 / +0.06 |
| (a) chỉ đổi vùng | 49 / -0.35 | 24 / +0.09 | 28 / +0.06 | 0 · — · — | -0.13 | 5 · -0.26 | 3270 / — / 103 ‖ 3270 / — / 103 | 96 · 24.0% · -0.13 | 47 / -0.15 |
| (b) chỉ đổi logic đà | 22 / -0.37 | 5 / -0.28 | 19 / -0.45 | 1 · 100.0% · +2.90 | -0.47 | 5 · -1.07 | 3603 / 3560 / 43 ‖ 445 / 408 / 41 | 41 · 19.5% · -0.31 | 18 / -0.21 |
| (c) chỉ bỏ cấm giờ | 6 / -0.43 | 3 / -1.08 | 12 / -0.74 | 2 · 0.0% · -1.06 | -0.66 | 1 · -1.06 | 564 / — / 21 ‖ 564 / — / 21 | 20 · 10.0% · -0.68 | 7 / +0.06 |
| (d) A-v4 | 106 / -0.33 | 51 / -0.06 | 61 / -0.43 | 15 · 33.3% · +0.26 | -0.34 | 10 · -0.26 | 50937 / 50784 / 214 ‖ 2577 / 2456 / 177 | 208 · 19.7% · -0.30 | 95 / -0.49 |
| A-v4+ (thêm VA Âu/IB) | 106 / -0.33 | 51 / -0.06 | 95 / -0.49 | 19 · 26.3% · -0.02 | -0.36 | 15 · -0.53 | 56870 / 56703 / 247 ‖ 3060 / 2929 / 207 | 237 · 19.0% · -0.33 | 108 / -0.49 |
| (phụ) vùng mới + V3 + bỏ cấm | 49 / -0.35 | 25 / +0.20 | 29 / +0.16 | 2 · 100.0% · +2.91 | -0.13 | 5 · -0.27 | 3348 / — / 104 ‖ 3348 / — / 104 | 98 · 25.5% · -0.06 | 47 / -0.15 |
| (phụ) vùng cũ + đà + bỏ cấm | 22 / -0.37 | 5 / -0.28 | 21 / -0.51 | 5 · 20.0% · -0.28 | -0.44 | 4 · -1.06 | 3810 / 3766 / 46 ‖ 470 / 432 / 43 | 44 · 18.2% · -0.36 | 19 / -0.26 |
| (phụ) vùng mới + đà + cấm | 106 / -0.33 | 48 / +0.01 | 59 / -0.34 | 5 · 80.0% · +2.12 | -0.32 | 9 · -0.18 | 47964 / 47817 / 209 ‖ 2527 / 2412 / 172 | 204 · 20.6% · -0.26 | 94 / -0.45 |

### 4.3 Độ nhạy TP 2R (cùng tín hiệu, chỉ đổi TP — không dùng để kết luận)

| cấu hình | n | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R |
|---|---|---|---|---|---|
| A-V3 gốc | 20 | 25.0% | -0.33 [-0.80; +0.27] | 12 / -0.33 | 8 / -0.33 |
| (a) chỉ đổi vùng | 102 | 27.5% | -0.26 [-0.52; +0.00] | 54 / -0.20 | 48 / -0.33 |
| (b) chỉ đổi logic đà | 47 | 25.5% | -0.32 [-0.65; +0.06] | 26 / -0.16 | 21 / -0.53 |
| (c) chỉ bỏ cấm giờ | 21 | 28.6% | -0.22 [-0.80; +0.35] | 14 / -0.22 | 7 / -0.23 |
| (d) A-v4 | 222 | 27.5% | -0.26 [-0.43; -0.08] | 121 / -0.17 | 101 / -0.37 |
| A-v4+ (thêm VA Âu/IB) | 256 | 27.3% | -0.26 [-0.43; -0.10] | 138 / -0.17 | 118 / -0.37 |
| (phụ) vùng mới + V3 + bỏ cấm | 104 | 28.8% | -0.22 [-0.48; +0.04] | 56 / -0.12 | 48 / -0.33 |
| (phụ) vùng cũ + đà + bỏ cấm | 49 | 28.6% | -0.23 [-0.60; +0.14] | 29 / -0.15 | 20 / -0.35 |
| (phụ) vùng mới + đà + cấm | 217 | 28.6% | -0.23 [-0.41; -0.05] | 118 / -0.14 | 99 / -0.33 |

## 5. Đối chứng

Mỗi ô: R TB thật · TB đối chứng [5%; 95%]. Phán quyết theo ngưỡng mục 0.

| cấu hình | đối chứng | GỘP | TRAIN | TEST | T8 | T9 | T10 | phán quyết |
|---|---|---|---|---|---|---|---|---|
| A-V3 gốc | ĐC1 cùng trạng thái | -0.68 · -0.22 [-0.70; +0.50] | -1.08 · -0.35 [-1.09; +0.57] | -0.08 · -0.02 [-1.09; +0.92] | -1.09 · -0.33 [-1.09; +0.52] | +0.27 · -0.19 [-1.10; +0.92] | -1.09 · +0.04 [-1.10; +0.93] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| (a) chỉ đổi vùng | ĐC1 cùng trạng thái | -0.13 · -0.10 [-0.38; +0.14] | -0.11 · -0.10 [-0.41; +0.27] | -0.16 · -0.11 [-0.50; +0.33] | -0.28 · -0.08 [-0.56; +0.38] | -0.02 · -0.16 [-0.56; +0.19] | -0.15 · -0.04 [-0.62; +0.60] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| (b) chỉ đổi logic đà | ĐC1 cùng trạng thái | -0.39 · -0.12 [-0.57; +0.22] | -0.44 · -0.25 [-0.79; +0.35] | -0.34 · +0.03 [-0.54; +0.63] | -0.83 · -0.24 [-0.84; +0.42] | +0.42 · -0.10 [-0.84; +0.66] | -0.82 · +0.00 [-0.80; +0.92] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| (c) chỉ bỏ cấm giờ | ĐC1 cùng trạng thái | -0.70 · -0.19 [-0.71; +0.44] | -1.08 · -0.29 [-0.81; +0.35] | +0.06 · +0.00 [-1.09; +1.20] | -1.08 · -0.30 [-1.09; +0.72] | +0.08 · -0.17 [-1.09; +1.20] | -1.09 · +0.15 [-1.11; +1.60] | không áp dụng (n < 10 ở TRAIN hoặc TEST) |
| (d) A-v4 | ĐC1 cùng trạng thái | -0.30 · -0.18 [-0.36; +0.02] | -0.11 · -0.18 [-0.45; +0.05] | -0.52 · -0.17 [-0.41; +0.13] | -0.40 · -0.20 [-0.51; +0.13] | -0.00 · -0.17 [-0.47; +0.10] | -0.52 · -0.16 [-0.53; +0.17] | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| (d) A-v4 | ĐC2 control_sample | -0.30 · -0.08 [-0.28; +0.10] | -0.11 · -0.07 [-0.38; +0.18] | -0.52 · -0.10 [-0.38; +0.23] | -0.40 · -0.07 [-0.43; +0.28] | -0.00 · -0.12 [-0.47; +0.22] | -0.52 · -0.07 [-0.43; +0.32] | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) |
| (d) A-v4 | ĐC3 dời vùng 3–15 giá | -0.30 · -0.13 [-0.28; +0.07] | -0.11 · -0.13 [-0.39; +0.12] | -0.52 · -0.13 [-0.40; +0.14] | -0.40 · -0.18 [-0.50; +0.20] | -0.00 · -0.08 [-0.38; +0.31] | -0.52 · -0.12 [-0.40; +0.11] | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| A-v4+ (thêm VA Âu/IB) | ĐC1 cùng trạng thái | -0.34 · -0.15 [-0.31; +0.02] | -0.17 · -0.16 [-0.36; +0.06] | -0.53 · -0.15 [-0.40; +0.09] | -0.40 · -0.15 [-0.45; +0.14] | -0.10 · -0.18 [-0.47; +0.11] | -0.54 · -0.13 [-0.39; +0.15] | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) |
| A-v4+ (thêm VA Âu/IB) | ĐC2 control_sample | -0.34 · -0.09 [-0.31; +0.11] | -0.17 · -0.08 [-0.34; +0.23] | -0.53 · -0.11 [-0.38; +0.18] | -0.40 · -0.09 [-0.41; +0.29] | -0.10 · -0.11 [-0.43; +0.23] | -0.54 · -0.08 [-0.43; +0.27] | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) |
| A-v4+ (thêm VA Âu/IB) | ĐC3 dời vùng 3–15 giá | -0.34 · -0.13 [-0.30; +0.04] | -0.17 · -0.12 [-0.38; +0.09] | -0.53 · -0.15 [-0.37; +0.09] | -0.40 · -0.17 [-0.49; +0.14] | -0.10 · -0.09 [-0.40; +0.29] | -0.54 · -0.14 [-0.41; +0.07] | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) |

- (d) A-v4, vùng DỜI 3–15 giá: số lệnh/ngày TB 3.19 [2.82; 3.59] (thật 3.57).
- (d) A-v4, hồ ĐC1 = 9099 nến.
- A-v4+ (thêm VA Âu/IB), vùng DỜI 3–15 giá: số lệnh/ngày TB 3.59 [3.20; 4.00] (thật 4.13).
- A-v4+ (thêm VA Âu/IB), hồ ĐC1 = 10459 nến.

## 6. A-v4 và A-v4+ — tách mô tả (CHỈ MÔ TẢ, không lọc; nhóm n < 10 không nói gì)

### (d) A-v4

| nhóm | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R | 18:00–19:20 n / R |
|---|---|---|---|---|---|---|---|
| vùng VWAP_W | 42 | 0.69 | 26.2% | -0.04 [-0.52; +0.53] | 29 / -0.26 | 13 / +0.46 | 2 / +0.92 |
| vùng VWAP_D | 53 | 0.87 | 22.6% | -0.18 [-0.63; +0.28] | 27 / +0.25 | 26 / -0.62 | 2 / -1.09 |
| vùng HVN_W | 11 | 0.18 | 18.2% | -0.34 [-1.07; +0.75] | 2 / -1.09 | 9 / -0.17 | 1 / -1.06 |
| vùng HVN_D | 44 | 0.72 | 22.7% | -0.18 [-0.63; +0.37] | 29 / +0.01 | 15 / -0.55 | 4 / -0.06 |
| vùng VAH_D | 31 | 0.51 | 9.7% | -0.70 [-1.08; -0.31] | 13 / -0.46 | 18 / -0.87 | 1 / +2.90 |
| vùng VAL_D | 37 | 0.61 | 13.5% | -0.54 [-0.97; -0.10] | 19 / -0.24 | 18 / -0.86 | 5 / +0.54 |
| phá lần 1 (brk_no = 1) | 48 | 0.79 | 16.7% | -0.42 [-0.84; +0.00] | 31 / -0.44 | 17 / -0.39 | 0 / — |
| phá lần ≥ 2 | 170 | 2.79 | 20.6% | -0.26 [-0.50; -0.00] | 88 / +0.01 | 82 / -0.54 | 15 / +0.26 |
| cực trị cách E 2–3 giá | 46 | 0.75 | 26.1% | -0.05 [-0.57; +0.47] | 26 / +0.29 | 20 / -0.50 | 0 / — |
| cực trị cách E 3–5 giá | 64 | 1.05 | 18.8% | -0.33 [-0.71; +0.05] | 30 / -0.29 | 34 / -0.37 | 0 / — |
| cực trị cách E 5–∞ giá | 100 | 1.64 | 19.0% | -0.32 [-0.60; +0.00] | 57 / -0.09 | 43 / -0.61 | 15 / +0.26 |
| cực trị cách E < 2 giá (cạnh động trôi lại gần, Q5) | 8 | 0.13 | 0.0% | -1.12 [-1.13; -1.10] | 6 / -1.12 | 2 / -1.11 | 0 / — |
| trạng thái mở MỚI | 183 | 3.00 | 19.7% | -0.30 [-0.52; -0.06] | 100 / -0.13 | 83 / -0.50 | 14 / +0.08 |
| trạng thái MỞ LẠI sau hết hạn (Q9) | 35 | 0.57 | 20.0% | -0.28 [-0.74; +0.29] | 19 / -0.03 | 16 / -0.58 | 1 / +2.92 |
| lệnh thứ 1 của trạng thái | 204 | 3.34 | 20.1% | -0.28 [-0.49; -0.06] | 109 / -0.09 | 95 / -0.49 | 13 / +0.16 |
| lệnh thứ ≥ 2 của trạng thái | 14 | 0.23 | 14.3% | -0.52 [-1.11; +0.34] | 10 / -0.30 | 4 / -1.09 | 2 / +0.94 |
| nến đà (cực trị − nến phá) > 30 | 26 | 0.43 | 19.2% | -0.31 [-0.92; +0.31] | 12 / -0.09 | 14 / -0.51 | 5 / +0.54 |

### A-v4+ (thêm VA Âu/IB)

| nhóm | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R | 18:00–19:20 n / R |
|---|---|---|---|---|---|---|---|
| vùng VWAP_W | 41 | 0.67 | 26.8% | -0.01 [-0.50; +0.57] | 28 / -0.23 | 13 / +0.46 | 2 / +0.92 |
| vùng VWAP_D | 52 | 0.85 | 23.1% | -0.16 [-0.62; +0.30] | 26 / +0.30 | 26 / -0.62 | 2 / -1.09 |
| vùng HVN_W | 10 | 0.16 | 20.0% | -0.27 [-1.07; +0.93] | 1 / -1.10 | 9 / -0.17 | 1 / -1.06 |
| vùng HVN_D | 43 | 0.70 | 20.9% | -0.25 [-0.72; +0.22] | 28 / -0.09 | 15 / -0.55 | 4 / -0.06 |
| vùng VAH_D | 31 | 0.51 | 9.7% | -0.70 [-1.08; -0.31] | 13 / -0.46 | 18 / -0.87 | 1 / +2.90 |
| vùng VAL_D | 37 | 0.61 | 13.5% | -0.54 [-0.97; -0.10] | 19 / -0.24 | 18 / -0.86 | 5 / +0.54 |
| vùng VAH_EU | 16 | 0.26 | 18.8% | -0.33 [-1.07; +0.42] | 12 / -0.07 | 4 / -1.09 | 2 / -1.06 |
| vùng VAL_EU | 22 | 0.36 | 9.1% | -0.72 [-1.08; -0.18] | 9 / -1.08 | 13 / -0.47 | 2 / -1.08 |
| phá lần 1 (brk_no = 1) | 55 | 0.90 | 14.5% | -0.51 [-0.87; -0.14] | 34 / -0.49 | 21 / -0.52 | 4 / -1.07 |
| phá lần ≥ 2 | 197 | 3.23 | 19.8% | -0.29 [-0.51; -0.07] | 102 / -0.06 | 95 / -0.53 | 15 / +0.26 |
| cực trị cách E 2–3 giá | 49 | 0.80 | 24.5% | -0.11 [-0.60; +0.38] | 28 / +0.19 | 21 / -0.52 | 0 / — |
| cực trị cách E 3–5 giá | 76 | 1.25 | 18.4% | -0.35 [-0.67; +0.02] | 34 / -0.38 | 42 / -0.32 | 1 / -1.11 |
| cực trị cách E 5–∞ giá | 117 | 1.92 | 17.9% | -0.36 [-0.63; -0.08] | 68 / -0.13 | 49 / -0.67 | 18 / +0.04 |
| cực trị cách E < 2 giá (cạnh động trôi lại gần, Q5) | 10 | 0.16 | 0.0% | -1.12 [-1.13; -1.11] | 6 / -1.12 | 4 / -1.12 | 0 / — |
| trạng thái mở MỚI | 215 | 3.52 | 18.6% | -0.34 [-0.54; -0.13] | 117 / -0.20 | 98 / -0.51 | 18 / -0.18 |
| trạng thái MỞ LẠI sau hết hạn (Q9) | 37 | 0.61 | 18.9% | -0.32 [-0.76; +0.22] | 19 / -0.03 | 18 / -0.63 | 1 / +2.92 |
| lệnh thứ 1 của trạng thái | 234 | 3.84 | 18.8% | -0.33 [-0.52; -0.12] | 125 / -0.19 | 109 / -0.49 | 17 / -0.13 |
| lệnh thứ ≥ 2 của trạng thái | 18 | 0.30 | 16.7% | -0.43 [-1.10; +0.25] | 11 / -0.00 | 7 / -1.10 | 2 / +0.94 |
| nến đà (cực trị − nến phá) > 30 | 27 | 0.44 | 18.5% | -0.34 [-0.93; +0.26] | 13 / -0.16 | 14 / -0.51 | 5 / +0.54 |

## 7. Các rủi ro plan mục 5 — số kiểm

- **(d) A-v4:** VWAP chiếm **26%** số lần mở trạng thái và **43.6%** số lệnh (plan cảnh báo nếu > 70% trạng thái nhưng < 30% lệnh). Tín hiệu thô 245 → 218 lệnh sau luật 1 lệnh mở (chặn **11%**). Lệnh có vùng KHÁC trong ±1 giá quanh E: **42/245 (17%)**. Hai vùng hợp lệ cùng nến (chọn gần hơn): 31 lần. Mở chiều ngược bị chặn vì chiều kia còn sống (Q2): 934 lần. Lệnh vào khi cực trị đã KHÔNG còn cách E(i) ≥ D_MIN (cạnh động trôi, Q5): 13. pbmax/L của lệnh vào: trung vị 0.73, p90 0.92, max 1.00. Tín hiệu bị trần SL 4 giá loại: 116.
  Mở trạng thái theo loại vùng: VWAP_W 7285, VWAP_D 5927, HVN_W 14690, HVN_D 7535, VAH_D 7645, VAL_D 7855. Trang bị: VWAP_W 7257, VWAP_D 5873, HVN_W 14668, HVN_D 7515, VAH_D 7633, VAL_D 7838. Có lệnh: VWAP_W 42, VWAP_D 54, HVN_W 11, HVN_D 41, VAH_D 30, VAL_D 36.
- **A-v4+ (thêm VA Âu/IB):** VWAP chiếm **23%** số lần mở trạng thái và **36.9%** số lệnh (plan cảnh báo nếu > 70% trạng thái nhưng < 30% lệnh). Tín hiệu thô 284 → 252 lệnh sau luật 1 lệnh mở (chặn **11%**). Lệnh có vùng KHÁC trong ±1 giá quanh E: **55/284 (19%)**. Hai vùng hợp lệ cùng nến (chọn gần hơn): 39 lần. Mở chiều ngược bị chặn vì chiều kia còn sống (Q2): 1088 lần. Lệnh vào khi cực trị đã KHÔNG còn cách E(i) ≥ D_MIN (cạnh động trôi, Q5): 17. pbmax/L của lệnh vào: trung vị 0.74, p90 0.92, max 1.00. Tín hiệu bị trần SL 4 giá loại: 150.
  Mở trạng thái theo loại vùng: VWAP_W 7286, VWAP_D 5927, HVN_W 14690, HVN_D 7535, VAH_D 7645, VAL_D 7855, VAH_EU 2931, VAL_EU 3001. Trang bị: VWAP_W 7258, VWAP_D 5873, HVN_W 14668, HVN_D 7515, VAH_D 7633, VAL_D 7838, VAH_EU 2924, VAL_EU 2994. Có lệnh: VWAP_W 41, VWAP_D 53, HVN_W 10, HVN_D 40, VAH_D 30, VAL_D 36, VAH_EU 17, VAL_EU 20.
- **HVN tuần:** 0/61 phiên sạch có HVN tuần dựng trên cửa sổ `partial` (thiếu tuần do đầu file); 10 phiên không có HVN tuần nào qua cổng ×2,5. Khoảng cách giá mở phiên → HVN tuần gần nhất: trung vị **83.7 giá**, p75 185.4, p90 267.8. Bề rộng dải PeakSharpness trước kẹp: trung vị 3.6 giá, max 6.8; sau kẹp ≤ 2: trung vị 2.0.
- **Hai lệnh/vùng/phiên với vùng động (VWAP_D, (d)):** 15 phiên có 2 lệnh VWAP_D; chênh E giữa hai lệnh: 11.0, 40.5, 0.0, 19.9, 35.2, 16.7, 0.2, 17.8, 0.1, 0.5, 1.5, 7.6, 0.8, 1.4, 3.5 giá.
- A mô phỏng đứng riêng; khi gộp 4 setup với 1 lệnh mở chung thì số lệnh thực tế THẤP hơn (chưa chạy ở đây).

## 8. Độ nhạy quanh (d) A-v4 — đổi MỘT thứ một lần, IN RA, KHÔNG chọn lại

| biến thể | n | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R |
|---|---|---|---|---|---|
| **(d) ô chính** (D_MIN 2, T_HOI 30, hủy 1,0) | 218 | 19.7% | -0.30 [-0.50; -0.07] | 119 / -0.11 | 99 / -0.52 |
| D_MIN = 1.5 | 229 | 19.2% | -0.32 [-0.52; -0.11] | 125 / -0.16 | 104 / -0.51 |
| D_MIN = 3.0 | 185 | 17.3% | -0.39 [-0.60; -0.15] | 96 / -0.25 | 89 / -0.54 |
| T_HOI = 20 | 182 | 22.0% | -0.21 [-0.43; +0.04] | 98 / -0.02 | 84 / -0.42 |
| T_HOI = 60 | 259 | 21.6% | -0.22 [-0.42; -0.02] | 141 / -0.15 | 118 / -0.30 |
| CANCEL_DEPTH = 0.5 | 188 | 21.8% | -0.21 [-0.44; +0.04] | 100 / -0.00 | 88 / -0.44 |
| CANCEL_DEPTH = 1.5 | 236 | 19.5% | -0.30 [-0.49; -0.10] | 133 / -0.18 | 103 / -0.46 |
| HVN tuần là ĐIỂM (không dải) | 224 | 20.5% | -0.26 [-0.46; -0.05] | 121 / -0.09 | 103 / -0.46 |
| VA ngày ĐANG HÌNH THÀNH thay VA hôm qua (cách hiểu (b)) | 268 | 20.9% | -0.25 [-0.44; -0.05] | 158 / -0.20 | 110 / -0.32 |
| — riêng lệnh ở VAH/VAL đang hình thành | 116 | 19.0% | -0.32 [-0.59; -0.01] | 69 / -0.38 | 47 / -0.23 |
| mở lại sau hết hạn CHỈ khi M5 đã về trong (Q9) | 188 | 20.2% | -0.28 [-0.49; -0.04] | 102 / -0.14 | 86 / -0.43 |
| CÓ chặn 19:20–20:30 (đúng engine C#) | 208 | 19.7% | -0.30 [-0.51; -0.08] | 113 / -0.13 | 95 / -0.49 |
| TP 2R | 222 | 27.5% | -0.26 [-0.43; -0.08] | 121 / -0.17 | 101 / -0.37 |

## 9. Luật cứng engine 19:20–20:30 VN — chỉ báo (KHÔNG đổi engine)

Hiệu R TB (lệnh có CF trong 19:20–20:30) − (ngoài) so với cùng hiệu của 43 cửa sổ 70 phút khác (bắt đầu sm 580..1130, bước 10', không chồng khung). File 90d toàn mùa hè Mỹ ⇒ nhánh mùa đông (20:20–21:30 VN) CHƯA kiểm.

| setup | n trong khung | WR · R trong | WR · R ngoài | hiệu | dải 5–95% các cửa sổ khác | phán |
|---|---|---|---|---|---|---|
| A-v4 (d), không chặn | 10 | 20.0% · -0.26 | 19.7% · -0.30 | +0.03 | [-0.82; +1.21] | trong dải 5–95% |
| A-V3 gốc | 2 | 0.0% · -1.07 | 11.1% · -0.64 | -0.43 | [-0.42; +1.78] | không áp dụng (n = 2 < 10 trong khung) |
| B Hấp thụ | 1 | 100.0% · +2.90 | 20.0% · -0.29 | +3.19 | [-1.19; -1.19] | không áp dụng (n = 1 < 10 trong khung) |
| C Fade cạnh | 22 | 9.1% · -0.79 | 31.3% · -0.14 | -0.65 | [-0.86; +1.27] | trong dải 5–95% |
| D Trap | 0 | — · — | 38.7% · +0.08 | — | [-1.21; +1.93] | không áp dụng (n = 0 < 10 trong khung) |

## 10. Ví dụ để soi chart (giờ VN, kèm giờ UTC)

"nến đà" = vị trí cực trị cuối − nến M5 phá; âm/0 = cực trị nằm trong chân cú phá (trước/đúng nến phá). Với lệnh thứ 2 của một trạng thái, cực trị được đặt lại ở nến vào lệnh 1.

### 10.1 (d) A-v4 — 5 lệnh THẮNG (cách đều theo thời gian)

| giờ VN (UTC) | chiều | vùng | E | cực trị (cách E) | nến đà | nến hồi | L | pbmax | vào | SL | TP | kết quả | R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-29 14:23 (07:23) | BÁN | VWAP_W | 4105.0 | 4102.6 (2.4) | 3 | 5 | 2.0 | 1.9 | 4105.3 | 4107.2 | 4099.6 | TP | +2.89 |
| 2026-08-27 15:59 (08:59) | BÁN | HVN_D1 | 4652.6 | 4647.9 (4.7) | 0 | 14 | 4.5 | 2.1 | 4652.3 | 4654.5 | 4645.7 | TP | +2.91 |
| 2026-09-08 20:19 (13:19) | BÁN | VWAP_W | 4453.1 | 4446.6 (6.5) | 0 | 14 | 7.4 | 3.3 | 4452.4 | 4456.0 | 4441.6 | TP | +2.94 |
| 2026-09-28 05:29 (22:29) | BÁN | VAL_D | 4304.4 | 4300.6 (3.8) | 4 | 10 | 4.0 | 2.1 | 4303.5 | 4305.7 | 4296.9 | TP | +2.91 |
| 2026-10-20 01:51 (18:51) | BÁN | HVN_W3 | 4167.2 | 4162.9 (4.3) | 17 | 19 | 1.8 | 1.3 | 4168.0 | 4170.5 | 4160.5 | TP | +2.92 |

### 10.2 (d) A-v4 — 5 lệnh THUA

| giờ VN (UTC) | chiều | vùng | E | cực trị (cách E) | nến đà | nến hồi | L | pbmax | vào | SL | TP | kết quả | R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-29 05:31 (22:31) | BÁN | VAL_D | 4079.2 | 4076.0 (3.2) | -1 | 7 | 3.3 | 2.0 | 4077.4 | 4080.6 | 4067.8 | SL | -1.06 |
| 2026-08-19 06:08 (23:08) | BÁN | VWAP_D | 4390.0 | 4385.8 (4.2) | 6 | 27 | 3.9 | 2.0 | 4388.3 | 4391.4 | 4379.0 | SL | -1.06 |
| 2026-09-15 16:11 (09:11) | MUA | VAL_D | 4304.4 | 4307.8 (3.4) | 1 | 5 | 3.5 | 2.6 | 4305.9 | 4303.1 | 4314.3 | SL | -1.07 |
| 2026-10-07 11:17 (04:17) | MUA | VAL_D | 4167.6 | 4174.5 (6.9) | 20 | 27 | 3.1 | 3.0 | 4168.3 | 4166.3 | 4174.3 | SL | -1.10 |
| 2026-10-21 20:16 (13:16) | BÁN | VAH_D | 4155.6 | 4151.6 (4.0) | 1 | 5 | 3.0 | 1.9 | 4155.6 | 4157.5 | 4149.9 | SL | -1.11 |

### 10.3 "V3 bỏ sót mà A-v4 bắt" — lệnh (d) có cực trị > 30 nến sau nến phá (V3 hết hạn 30 nến tính từ nến phá ⇒ không thể vào)

| giờ VN (UTC) | chiều | vùng | E | cực trị (cách E) | nến đà | nến hồi | L | pbmax | vào | SL | TP | kết quả | R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-31 06:14 (23:14) | MUA | VWAP_D | 4166.7 | 4170.7 (4.0) | 31 | 7 | 2.3 | 1.7 | 4166.1 | 4164.4 | 4171.2 | SL | -1.12 |
| 2026-08-18 06:17 (23:17) | BÁN | VAH_D | 4473.6 | 4466.0 (7.6) | 56 | 16 | 3.0 | 2.9 | 4473.0 | 4475.9 | 4464.3 | SL | -1.07 |
| 2026-09-17 07:02 (00:02) | MUA | VWAP_D | 4305.4 | 4313.7 (8.3) | 31 | 11 | 6.0 | 3.7 | 4307.0 | 4303.3 | 4318.1 | TP | +2.95 |
| 2026-10-08 13:46 (06:46) | BÁN | VWAP_D | 4148.3 | 4138.1 (10.2) | 43 | 8 | 3.4 | 2.8 | 4148.2 | 4150.6 | 4141.0 | SL | -1.08 |
| 2026-10-21 07:08 (00:08) | BÁN | VAL_D | 4135.2 | 4130.3 (4.9) | 41 | 7 | 3.2 | 2.3 | 4135.0 | 4137.3 | 4128.1 | SL | -1.09 |

### 10.4 "V3 vào mà A-v4 từ chối" — lệnh A-V3 gốc không có trong (b) (cùng vùng cũ, cùng cấm giờ, chỉ đổi logic) và lý do theo trạng thái của logic đà tại nến đó

| giờ VN | chiều | E | kết quả V3 | R V3 | lý do A-v4 không vào |
|---|---|---|---|---|---|
| 2026-08-01 01:52 | BÁN | 4106.4 | SL | -1.11 | đã đủ 2 lệnh ở cạnh này trong phiên (A-v4 vào sớm hơn lúc 00:42, 01:40) |
| 2026-08-27 23:45 | MUA | 4665.6 | SL | -1.06 | CHƯA trang bị (cực trị chỉ cách E 1.3 giá < 2) |
| 2026-09-01 02:58 | MUA | 4499.2 | SL | -1.08 | CHƯA trang bị (cực trị chỉ cách E 0.6 giá < 2) |
| 2026-09-17 00:24 | MUA | 4385.2 | TP | +2.90 | CHƯA trang bị (cực trị chỉ cách E 1.5 giá < 2) |
| 2026-10-21 13:19 | BÁN | 4135.2 | SL | -1.08 | đã đủ 2 lệnh ở cạnh này trong phiên (A-v4 vào sớm hơn lúc 07:08, 08:31) |

### 10.5 Ảnh minh hoạ

- [a_v4_2026-09-08.png](img/a_v4_2026-09-08.png): vạch cam = cạnh E (VWAP thì là đường cong), dải cam = dải HVN tuần, tam giác tím = cực trị cuối, vùng tím nhạt = nhịp hồi, xanh dương = vào, đỏ đứt = SL, xanh lá đứt = TP; vạch chấm xám = nến M5 phá đóng.
- [a_v4_2026-09-15.png](img/a_v4_2026-09-15.png): vạch cam = cạnh E (VWAP thì là đường cong), dải cam = dải HVN tuần, tam giác tím = cực trị cuối, vùng tím nhạt = nhịp hồi, xanh dương = vào, đỏ đứt = SL, xanh lá đứt = TP; vạch chấm xám = nến M5 phá đóng.

## 11. Tiêu chí port (đăng ký trước, plan mục 4) — chấm tự động

| điều kiện T1 | đạt? | số |
|---|---|---|
| (1) n ≥ 40 | ĐẠT | n = 218 |
| (2) R TEST ≥ R TEST gốc (-0.08, n=8) và n TEST ≥ 15 | **KHÔNG** | R TEST = -0.52, n TEST = 99 |
| (3) R TRAIN ≥ -0.30 | ĐẠT | R TRAIN = -0.11 |
| (4) không đối chứng nào "thật KÉM hơn" | ĐẠT | ĐC1 cùng trạng thái: ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số); ĐC2 control_sample: ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số); ĐC3 dời vùng 3–15 giá: ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| (5) test 3.6 xanh | ĐẠT | 9 passed in 13.38s |
| (6) 18:00–19:20 không tệ hơn phần còn lại > 0,5R (n ≥ 10) | ĐẠT | n = 15, R +0.26 vs phần còn lại -0.34 |

- **T1: KHÔNG ĐẠT.** **T2: KHÔNG ĐẠT** (TRAIN -0.11, TEST -0.52, n TEST 99, vượt đối chứng: 0/3).

## 12. Đánh giá (viết tay sau khi đọc số — `report/_eval_a_v4.txt`)

1. **Số lệnh:** gốc 20 (0,33/ngày) → A-v4 **218 (3,57/ngày)**, tăng **+198 lệnh / +3,25/ngày**; nếu đổi riêng từng thứ từ gốc: đổi vùng +81, logic đà +26, bỏ cấm 18:00–19:20 +1; phần còn lại (+90) chỉ xuất hiện khi đổi vùng VÀ logic đà cùng lúc.
2. **WR:** 10% → **19,7% (+9,7 điểm)** ở TP 3R; vẫn dưới mức hoà vốn 27%.
3. **R TB:** −0,68 → **−0,30** [−0,50; −0,07]; TRAIN −0,11 (n 119) / TEST **−0,52** (n 99). Nửa sau xấu hơn nửa đầu.
4. **Độ tin cậy:** theo ngưỡng đã đăng ký, cả ba đối chứng đều ra "≈ đối chứng": vào ngẫu nhiên trong cùng trạng thái phá (≈), vào ngẫu nhiên ở vùng (≈), dời cả bản đồ vùng 3–15 giá (≈). Vùng dời vẫn cho 3,2 lệnh/ngày và R TB −0,13, tức vùng "đúng chỗ" không tạo ra gì. Riêng nửa TEST, A-v4 nằm DƯỚI dải 5% của cả ba đối chứng, nhưng nửa TRAIN thì nằm trong dải ⇒ không đủ điều kiện để nói "kém hơn". Với n này, chênh nhỏ hơn khoảng 0,4R (riêng TEST 0,6R) không thể phân biệt với may rủi.
5. **Khung 18:00–19:20:** 15 lệnh, WR 33%, R +0,26 (phần còn lại −0,34). n quá nhỏ, khoảng tin cậy rất rộng — chỉ là số để người học tự quyết, chưa phải bằng chứng.
6. **Từng loại vùng** (chỉ mô tả, mỗi nửa TRAIN/TEST đều < 30 lệnh): VWAP tuần 42 lệnh R −0,04 · VWAP ngày 53 lệnh R −0,18 · HVN ngày 44 lệnh R −0,18 · HVN tuần 11 lệnh R −0,34 · VAH ngày 31 lệnh R −0,70 · VAL ngày 37 lệnh R −0,54. Không loại nào dương ở cả hai nửa.
7. **Kết luận T1/T2:** T1 KHÔNG đạt (điều kiện 2: R TEST −0,52 thấp hơn mốc −0,08 của bản gốc) ⇒ **KHÔNG port C#, giữ A V3 trong indicator**. T2 không đạt. **Chưa có lợi thế đo được** trên 61 phiên.
8. **VA Âu/IB:** A-v4+ (thêm VA Âu/IB) 252 lệnh, WR 18,7%, R −0,34 (TEST −0,53) — không tốt hơn A-v4; riêng VAL Âu 22 lệnh R −0,72. Người học quyết, nhưng số không ủng hộ giữ.
Ghi chú thêm (không thay kết luận): bản chỉ đổi vùng mà giữ logic V3 cho R TB −0,13 (101 lệnh) — logic đà thêm lệnh nhưng không thêm R; mọi chênh giữa các ô đều nhỏ hơn mức phát hiện được. Bản chính làm đúng chữ plan "hết hạn rồi M5 ngoài kế tiếp mở lại ngay" (Q9); bản bắt buộc giá về trong trước khi mở lại cho 188 lệnh, R −0,28 — cùng kết luận.


_Thời gian chạy toàn bộ: 268 giây._
