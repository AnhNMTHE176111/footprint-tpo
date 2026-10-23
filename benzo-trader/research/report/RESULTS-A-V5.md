# RESULTS-A-V5 — Setup A "Phá hồi": A-v4 + vùng hỗ trợ/kháng cự của Vùng Canh Lệnh (VCL v5)

Sinh bởi `setup_a_v5.py` (tất định, hạt cố định) theo đặc tả `plans/BENZO-A-V5-plan.md` (Opus). Dữ liệu: CHỈ `fp_GCZ26_XCEC_Time_20260723-20261021_90d`, giờ UTC (VN = UTC+7). TRAIN = phiên ≤ 2026-09-15, TEST từ 2026-09-16. **61 phiên sạch** (TRAIN 35 / TEST 26) — "lệnh/ngày" chia cho 61. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ tính SL; **1 lệnh mở cùng lúc chung cho vùng v4 và VCL** (A đứng riêng, không gộp B/C/D); TP 3R (hoà vốn sau phí ≈ 27% WR). Tham số tự do MỚI = 0 (mọi số dùng lại từ v4).

Thuật ngữ: **VCL** = indicator Vùng Canh Lệnh · **eid** = mã vùng ổn định · **bộ hiển thị** = các vùng VCL đang vẽ tại nến i · **cú phá thật** = trong chân cú phá có một nến M1 mà vùng đang hiển thị và giá đóng ở phía trong · **rời bộ** = eid không còn trong bộ hiển thị · **khoá mức** = chống đếm hai lần một mức giá · **đối chứng** = cách vào lệnh "bừa" để so · **công suất thống kê** = chênh nhỏ nhất đo ra được.

## 1. Công suất thống kê — ĐỌC TRƯỚC bảng chính (plan 3.1)

Hiệu nhỏ nhất phát hiện được (xác suất 80%, mức 5%, hai phía) ≈ 2,8 × σ_R × √(1/n₁ + 1/n₂). σ_R của A-v5 = **1.67**; n = 324 (TRAIN 175 / TEST 149); lệnh VCL n = 131 (TRAIN 71 / TEST 60), lệnh vùng v4 trong A-v5 n = 193 (TRAIN 104 / TEST 89).

| so sánh | hiệu nhỏ nhất phát hiện được |
|---|---|
| R TB A-v5 so với 0 (một mẫu) | **0.26 R** |
| A-v5 so với A-v4 (n = 324 vs 218) | **0.41 R** |
| **lệnh VCL so lệnh vùng v4 trong A-v5** (cả hai đợt / TRAIN / TEST) | **0.53 / 0.72 / 0.78 R** |
| riêng TEST so với đối chứng (n TEST = 149 vs 149) | **0.54 R** |
| riêng lệnh VCL, TEST so với đối chứng (n TEST = 60) | **0.85 R** |

⇒ **Chênh nhỏ hơn các con số này không phân biệt được với may rủi trên 90 ngày.**

## 2. BẢNG CHÍNH (TP 3R, sau phí, 1 lệnh mở, không chặn 19:20–20:30)

R TB [KTC 95%] = bootstrap 10 000 lần hạt 0 (đánh giá THẤP độ bất định vì lệnh cùng phiên không độc lập).

| bản | số lệnh (tổng · /ngày) | WR | R TB sau phí [KTC 95%] |
|---|---|---|---|
| A cũ (V3 gốc) | 20 · 0.33 | 10.0% | -0.68 [-1.09; -0.09] |
| A-v4 | 218 · 3.57 | 19.7% | -0.30 [-0.50; -0.07] |
| **A-v5 (A-v4 + vùng VCL)** | 324 · 5.31 | 22.2% | -0.18 [-0.36; +0.01] |

1. Lệnh VCL thêm: **+106** lệnh (+1.74/ngày) so với A-v4 (+304 so với A cũ); lệnh VCL riêng: 131 lệnh, WR 23.7%, R TB -0.11; lệnh A-v4 bị chen mất: 25.
2. Đối chứng A-v5 (ĐC1 / ĐC2 / ĐC3): **không hơn / không hơn / không hơn**.
3. Đối chứng riêng lệnh VCL (ĐC1-VCL / ĐC2-VCL / ĐC3-chỉ-dời-VCL): **không hơn / không hơn / không hơn**.
4. T1-v5: **không đạt** (trượt: (2) R TB TEST(A-v5) ≥ -0.08 và n TEST ≥ 15); T2: **không đạt**.

Lệnh VCL (131 lệnh) tách thành VCL-riêng / trùng vùng v4 ở mục 5.2. Số lệnh/ngày dùng mẫu số 61 phiên sạch.

## 3. Chỗ tự quyết của Sonnet (plan không nói rõ — chọn hướng hợp lý nhất, ghi lại)

- V1 Luật cú phá thật khi vòng lùi dừng vì chạm giới hạn `lim` (k == lim): vẫn kiểm nến k — nếu tại k vùng có giá trị và giá đóng phía trong thì MỞ (chân cú phá có nến trong đúng ở nến giới hạn); nếu giá vẫn ngoài thì trượt, ghi `het60` (lim = i − 60 > đầu phiên) hoặc `dau_phien` (đầu phiên a ≥ i − 60).
- V2 "Số lần M5 đóng ngoài vùng VCL" của phễu = số lần ĐẾN bước thử mở trạng thái (M5 đóng ngoài, chưa có trạng thái cùng chiều, không bị chặn vì chiều kia còn sống). Số M5 đóng ngoài kể cả khi đã có trạng thái in riêng (`m5_ngoai_tat_ca`).
- V3 Thứ tự trong khâu ứng viên của VCL: chạm vùng → hồi/CF → trần 2 lệnh theo mã vùng → trần SL 4 giá → khoá mức (và S5: bỏ trùng) → tranh cùng nến. Khoá mức đếm chỉ các tín hiệu ĐÃ GHI (thắng tranh cùng nến), cùng (phiên, chiều), |E cũ − E| ≤ ZONE_HALF.
- V4 `roi_bo` có eid mới chồng: eid MỚI có nến đầu trong [L+1, L+5] (L = nến cuối của eid cũ) và dải giao dải CUỐI của eid cũ (lo' < hi_cũ và hi' > lo_cũ).
- V5 Nhãn "trùng" tính ở nến VÀO lệnh (nến của tín hiệu) với dải v4 tại chính nến đó (đã dời nếu ĐC3).
- V6 Phép so 'lệnh VCL so lệnh v4 trong A-v5' (mục 3.1 và T1-(8)) dùng độ lệch chuẩn R của MỌI lệnh A-v5 và n của hai nhóm ở đúng tập đang xét (TRAIN / TEST); hiệu nhỏ nhất phát hiện được = 2,8 · σ · √(1/n_VCL + 1/n_v4).
- V7 Bảng chính và mọi lệnh dùng chế độ 1 lệnh mở CHUNG cho v4 + VCL (A đứng riêng, không gộp với B/C/D) — như v4.
- V8 ĐC2 cho A-v5 toàn bộ: lệnh vùng v4 dùng cột vùng như v4; lệnh VCL dùng 2 cột chung (MUA = hi, BÁN = lo của vùng VCL trong bộ có cạnh gần giá đóng nhất tại từng nến).
- V9 Thứ tự mục: plan 3.1 đòi in công suất TRƯỚC bảng chính, plan mục 7 đòi bảng chính đầu tiên ⇒ để mục công suất (ngắn, 5 dòng) ngay sau tiêu đề rồi tới bảng chính.
- V10 Trước lần commit test, tôi đã chạy thử `detect5` MỘT lần để bắt lỗi (in số lệnh/phễu); KHÔNG đổi luật hay hằng số nào theo số đó. Hai sửa sau lần chạy thử chỉ là cách ĐẾM phễu (`roi_bo` bị đếm đôi; "hủy phía đối diện" bị che bởi "hủy sâu" vì M5 đóng ngoài mép xa luôn sâu hơn 1 giá ⇒ nay ưu tiên nhãn "đối diện"). Lịch sử git (`eed1c6d` test + máy, trước kết quả) là bằng chứng.
- V11 Ca "hủy +1 mở −1 cùng nến" của plan 2.6: khi M5 đóng dưới `lo`, trạng thái +1 luôn bị hủy ở nhãn "đối diện" (không bao giờ ở nhãn "hủy sâu"); trạng thái −1 mở cùng nến nếu qua luật cú phá thật.
- V12 Mỗi lần thử mở trạng thái bị luật cú phá thật chặn được đếm MỘT lần cho MỖI nến M5 (cùng một eid có thể bị đếm lại ở nến M5 sau) — phễu 3.3(4) là số lần thử, không phải số cú phá khác nhau.
- V13 Vùng VCL ĐÃ có độ rộng 2–5 giá (engine kẹp), nhưng test tổng hợp dùng vùng hẹp hơn (1,5 giá) cho vừa trần SL 4 giá — chỉ là dữ liệu giả, không ảnh hưởng kết quả thật.

## 4. Điều kiện tiên quyết (plan 3.0) — đã đạt

- (1) A cũ qua máy mới (band cũ, logic V3, cấm 18:00–19:20): **n = 20, WR 10.0%, R TB -0.68** [-1.09; -0.09] — khớp từng lệnh `setup_a_pha_hoi.detect(expire=30)` (test).
- (2) `detect5` với VCL TẮT khớp từng trường của từng lệnh `setup_a_v4.detect` cấu hình (d): **n = 218, WR 19.7%, R TB -0.30**, TRAIN 119 / -0.11 · TEST 99 / -0.52 (test, cả `None` lẫn bộ VCL rỗng).
- (3) Phiên 2026-09-08 và 2026-10-02: vòng lặp THƯA == vòng lặp DÀY (cùng lệnh, cùng phễu, cùng danh sách `roi_bo`) — test.
- Test toàn bộ `test_setup_a_v5.py` chạy lại lúc sinh báo cáo: **15 passed in 32.81s**. Khớp chuỗi nến cache VCL ↔ dữ liệu: độ dài 86333 và datetime từng phần tử (`zones_a_v5.load_rec_checked`).

## 5. Chi tiết (plan 3.3)

### 5.1 Phân rã số lệnh

n(A-v5) = n(A-v4) − mất + v4 mới xuất hiện + VCL:  **324 = 218 − 25 + 0 + 131**  (kiểm: 324).

- Lệnh A-v4 bị MẤT trong A-v5: **25** — thua tranh cùng nến (VCL gần hơn): 15; bị lệnh VCL đang mở chặn: 9; khác (trạng thái v4 đổi dây chuyền): 1.
- "v4 mới xuất hiện" (tín hiệu v4 trước bị lệnh v4 khác chặn, nay được vào): **0**.
- Tín hiệu THÔ (trước luật 1 lệnh mở): A-v4 = 245; A-v5 phần v4 = 231, phần VCL = 156.
- Lệnh mất tính điểm: R TB của 25 lệnh v4 bị mất = -0.78; R TB của 0 lệnh v4 mới = — (đó là phần "đổi lệnh" mà luật 1 lệnh mở gây ra, ngoài lệnh VCL thêm).

### 5.2 Lệnh VCL: VCL-riêng vs trùng vùng v4

"Trùng" = tại nến vào có ≥ 1 vùng v4 (6 loại, có giá trị, VWAP đã qua Warm) mà dải giao [lo_VCL − 1, hi_VCL + 1]. CHỈ MÔ TẢ, không lọc.

| nhóm | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R |
|---|---|---|---|---|---|---|
| tất cả lệnh VCL | 131 | 2.15 | 23.7% | -0.11 [-0.39; +0.19] | 71 / -0.16 | 60 / -0.06 |
| **VCL-riêng** (không trùng vùng v4) | 89 | 1.46 | 23.6% | -0.12 [-0.43; +0.24] | 49 / -0.08 | 40 / -0.16 |
| **trùng** vùng v4 | 42 | 0.69 | 23.8% | -0.11 [-0.58; +0.46] | 22 / -0.33 | 20 / +0.14 |
| · trùng VWAP_D (một lệnh có thể trùng nhiều loại) | 17 | 0.28 | 23.5% | -0.12 [-0.82; +0.82] | 8 / -0.56 | 9 / +0.27 |
| · trùng VAH_D (một lệnh có thể trùng nhiều loại) | 10 | 0.16 | 60.0% | +1.34 [+0.14; +2.54] | 5 / +1.34 | 5 / +1.34 |
| · trùng loại khác (mỗi loại n < 10, gộp) | 24 | 0.39 | 8.3% | -0.73 [-1.06; -0.22] | 14 / -1.06 | 10 / -0.26 |

### 5.3 A-v5 · lệnh vùng v4 · lệnh VCL theo TRAIN / TEST / tháng / pha / khung giờ / bản có chặn

T8 gồm 29–31/7. Khung 18:00–19:20 = nến M5 phá HOẶC nến CF rơi trong sm 780..859; 19:20–20:30 = nến CF trong sm 860..929. "CÓ chặn" = chạy lại cả máy với luật cấm CF trong 19:20–20:30 (đúng engine C#), rồi tách theo nhóm.

| nhóm | n (lệnh/ngày) | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R | T8 n / R | T9 n / R | T10 n / R | Á n / R | Âu n / R | Mỹ n / R | 18:00–19:20 n · WR · R | 19:20–20:30 n · R | CÓ chặn 19:20–20:30 n · WR · R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-v5 (tất cả) | 324 (5.31) | 22.2% | -0.18 [-0.36; +0.01] | 175 / -0.07 | 149 / -0.32 | 113 / -0.15 | 118 / -0.06 | 93 / -0.38 | 141 / -0.23 | 87 / +0.08 | 96 / -0.36 | 27 · 25.9% · -0.02 | 12 · -0.40 | 312 · 22.4% · -0.18 |
| · lệnh vùng v4 | 193 (3.16) | 21.2% | -0.23 [-0.46; -0.00] | 104 / -0.01 | 89 / -0.50 | 64 / -0.34 | 72 / +0.09 | 57 / -0.52 | 92 / -0.30 | 48 / +0.01 | 53 / -0.33 | 14 · 35.7% · +0.36 | 10 · -0.26 | 183 · 21.3% · -0.23 |
| · lệnh VCL | 131 (2.15) | 23.7% | -0.11 [-0.39; +0.19] | 71 / -0.16 | 60 / -0.06 | 49 / +0.08 | 46 / -0.28 | 36 / -0.17 | 49 / -0.08 | 39 / +0.17 | 43 / -0.41 | 13 · 15.4% · -0.44 | 2 · -1.05 | 129 · 24.0% · -0.10 |
| (tham chiếu) A-v4 | 218 (3.57) | 19.7% | -0.30 [-0.50; -0.07] | 119 / -0.11 | 99 / -0.52 | 76 / -0.40 | 78 / -0.00 | 64 / -0.52 | 106 / -0.33 | 51 / -0.06 | 61 / -0.43 | 15 · 33.3% · +0.26 | 10 · -0.26 | 208 · 19.7% · -0.30 |

### 5.4 Phễu VCL

| bước | số |
|---|---|
| lần M5 đóng ngoài một vùng VCL (tất cả, kể cả đã có trạng thái) | 106103 |
| lần THỬ mở trạng thái (chưa có trạng thái cùng chiều) | 82945 |
| · bị luật CÚ PHÁ THẬT chặn — tổng | 76912 |
|    · vùng vắng ở nến chân cú phá (sinh ra trong/sau cú phá) | 25186 |
|    · chạy hết 60 nến mà giá vẫn ngoài (giá chưa từng ở trong) | 48517 |
|    · chạm đầu phiên | 3209 |
| · MỞ trạng thái — tổng | 6033 |
|    · mở mới / mở lại sau hết hạn (Q9) | 5097 / 936 |
| · ĐÃ TRANG BỊ (cực trị cách cạnh ≥ 2 giá, một lúc nào đó) | 5327 |
| · hủy sâu (M5 đóng trong sâu > 1 giá) | 1503 |
| · hủy phía đối diện (M5 đóng ngoài mép xa) | 1406 |
| · hết hạn T_HOI | 1574 |
| · hết phiên | 89 |
| · rời bộ (`roi_bo`) | 1461 |
|    · trong đó ĐÃ TRANG BỊ | 1305 |
|    · có eid MỚI chồng lên dải cũ trong ≤ 5 nến (tổng / đã trang bị) | 86 / 75 |
| · lần ứng viên có CF hợp lệ (theo nến) | 669 |
| · bị trần SL 4 giá loại (theo nến / số trạng thái) | 489 / 420 |
| · bị khoá mức | 6 |
| · thua tranh cùng nến (VCL xa hơn / hạng kém) | 8 |
| · TÍN HIỆU ghi nhận (thắng tranh cùng nến) | 156 |
| · LỆNH sau luật 1 lệnh mở (đã đóng) | 131 |

**Rủi ro "mất lệnh vì đổi mã" (plan 2.5):** 1305 / 5327 trạng thái ĐÃ TRANG BỊ chết vì `roi_bo` = **24.5%** (ngưỡng cảnh báo 30%) — không vượt ngưỡng. Trong số trạng thái bị `roi_bo`, 86/1461 (6%) có eid mới chồng lên dải cũ trong ≤ 5 nến.

### 5.5 Mô tả lệnh VCL (CHỈ MÔ TẢ, không lọc; nhóm n < 10 ghi "n nhỏ")

| nhóm | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R |
|---|---|---|---|---|---|---|
| bề rộng vùng 2–2,5 giá (kèm: tín hiệu bị trần SL loại 231 theo nến, 213 trạng thái) | 121 | 1.98 | 22.3% | -0.17 [-0.46; +0.13] | 66 / -0.15 | 55 / -0.19 |
| bề rộng vùng 2,5–3,5 giá (kèm: tín hiệu bị trần SL loại 139 theo nến, 120 trạng thái) | 9 | n nhỏ | | | | |
| bề rộng vùng 3,5–5 giá (kèm: tín hiệu bị trần SL loại 119 theo nến, 99 trạng thái) | 1 | n nhỏ | | | | |
| slot K ở nến chân cú phá (giá ở trong vùng rồi phá) | 38 | 0.62 | 15.8% | -0.43 [-0.85; +0.10] | 17 / -0.59 | 21 / -0.29 |
| slot N/F ở nến chân cú phá (giá xuyên từ phía kia sang) | 93 | 1.52 | 26.9% | +0.01 [-0.33; +0.40] | 54 / -0.02 | 39 / +0.07 |
| vùng chỉ có số tròn 10 USD (d10) | 49 | 0.80 | 32.7% | +0.25 [-0.24; +0.82] | 24 / +0.27 | 25 / +0.22 |
| vùng có mốc khác (không chỉ số tròn) | 82 | 1.34 | 18.3% | -0.33 [-0.67; +0.01] | 47 / -0.38 | 35 / -0.26 |
| phá lần 1 (brk_no = 1) | 66 | 1.08 | 22.7% | -0.15 [-0.52; +0.27] | 33 / +0.03 | 33 / -0.33 |
| phá lần ≥ 2 | 65 | 1.07 | 24.6% | -0.07 [-0.50; +0.36] | 38 / -0.32 | 27 / +0.27 |
| cực trị cách E 2–3 giá | 26 | 0.43 | 30.8% | +0.17 [-0.45; +0.94] | 14 / +0.09 | 12 / +0.27 |
| cực trị cách E 3–5 giá | 50 | 0.82 | 22.0% | -0.18 [-0.58; +0.30] | 29 / -0.09 | 21 / -0.30 |
| cực trị cách E 5–∞ giá | 55 | 0.90 | 21.8% | -0.19 [-0.62; +0.25] | 28 / -0.35 | 27 / -0.02 |
| trạng thái mở MỚI | 124 | 2.03 | 23.4% | -0.12 [-0.41; +0.17] | 66 / -0.15 | 58 / -0.09 |
| trạng thái MỞ LẠI sau hết hạn (Q9) | 7 | n nhỏ | | | | |
| lệnh thứ 1 của trạng thái | 131 | 2.15 | 23.7% | -0.11 [-0.39; +0.19] | 71 / -0.16 | 60 / -0.06 |
| lệnh thứ ≥ 2 của trạng thái | 0 | n nhỏ | | | | |

### 5.6 Ví dụ để soi chart (lệnh VCL; giờ VN, kèm giờ UTC)

"nến đà" = vị trí cực trị cuối − nến M5 phá. Với lệnh thứ 2 của một trạng thái, cực trị được đặt lại ở nến vào lệnh 1. Chọn cách đều theo thời gian, không chọn lọc.

**5 lệnh VCL THẮNG**

| giờ VN (UTC) | chiều | eid [lo; hi] | E | cực trị (cách E) | nến đà | nến hồi | L | pbmax | vào | SL | TP | kết quả | R | trùng / riêng |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-06 15:43 (08:43) | MUA | 690 [4329.00; 4331.00] | 4331.00 | 4334.0 (3.0) | 1 | 7 | 3.9 | 2.7 | 4331.4 | 4327.7 | 4342.5 | TP | +2.95 | trùng VAH_D |
| 2026-08-17 23:12 (16:12) | BÁN | 1176 [4483.90; 4485.90] | 4483.90 | 4481.4 (2.5) | -1 | 8 | 2.8 | 2.4 | 4483.7 | 4487.2 | 4473.2 | TP | +2.94 | riêng |
| 2026-09-04 06:17 (23:17) | MUA | 2127 [4519.15; 4521.15] | 4521.15 | 4524.8 (3.7) | 20 | 7 | 4.4 | 2.1 | 4520.3 | 4517.8 | 4527.8 | TP | +2.92 | trùng VWAP_D |
| 2026-09-30 17:23 (10:23) | BÁN | 3317 [4219.00; 4221.00] | 4219.00 | 4216.1 (2.9) | 5 | 3 | 3.1 | 2.5 | 4218.8 | 4222.3 | 4208.3 | TP | +2.94 | riêng |
| 2026-10-20 06:25 (23:25) | BÁN | 4162 [4154.80; 4157.90] | 4154.80 | 4152.1 (2.7) | 8 | 7 | 2.3 | 2.0 | 4155.2 | 4159.2 | 4143.2 | TP | +2.95 | trùng VAL_D+VWAP_D |

**5 lệnh VCL THUA**

| giờ VN (UTC) | chiều | eid [lo; hi] | E | cực trị (cách E) | nến đà | nến hồi | L | pbmax | vào | SL | TP | kết quả | R | trùng / riêng |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-29 06:39 (23:39) | BÁN | 234 [4078.60; 4080.60] | 4078.60 | 4074.0 (4.6) | 6 | 13 | 4.0 | 1.8 | 4078.6 | 4081.9 | 4068.7 | SL | -1.06 | trùng VAL_D+VWAP_D |
| 2026-08-18 16:52 (09:52) | BÁN | 1209 [4449.00; 4451.00] | 4449.00 | 4443.0 (6.0) | 56 | 6 | 2.7 | 2.6 | 4449.6 | 4452.3 | 4441.5 | SL | -1.07 | riêng |
| 2026-09-14 07:48 (00:48) | BÁN | 2547 [4378.85; 4381.15] | 4378.85 | 4373.4 (5.5) | 1 | 7 | 6.4 | 4.0 | 4379.7 | 4383.2 | 4369.2 | SL | -1.06 | trùng VAL_D |
| 2026-10-01 19:57 (12:57) | MUA | 3399 [4208.90; 4211.10] | 4211.10 | 4217.8 (6.7) | 13 | 9 | 4.8 | 2.6 | 4211.0 | 4207.6 | 4221.2 | SL | -1.06 | riêng |
| 2026-10-21 18:49 (11:49) | MUA | 4251 [4154.60; 4156.60] | 4156.60 | 4159.9 (3.3) | -1 | 5 | 3.9 | 3.0 | 4157.2 | 4153.3 | 4168.9 | SL | -1.05 | trùng VAH_D |

Ảnh minh hoạ (KHÔNG phải ca điển hình, chỉ để soi tay):

- [a_v5_2026-09-04.png](img/a_v5_2026-09-04.png): dải tím đậm = vùng VCL của lệnh, tím nhạt = các vùng VCL khác đang hiển thị, vạch cam = cạnh E, tam giác tím = cực trị cuối, vùng tím nhạt dọc = nhịp hồi, xanh dương = vào, đỏ đứt = SL, xanh lá đứt = TP; chấm xám = nến M5 phá đóng.
- [a_v5_2026-09-14.png](img/a_v5_2026-09-14.png): dải tím đậm = vùng VCL của lệnh, tím nhạt = các vùng VCL khác đang hiển thị, vạch cam = cạnh E, tam giác tím = cực trị cuối, vùng tím nhạt dọc = nhịp hồi, xanh dương = vào, đỏ đứt = SL, xanh lá đứt = TP; chấm xám = nến M5 phá đóng.

### 5.7 Số kiểm các rủi ro (plan mục 5)

- **Tỉ lệ `roi_bo`:** 24.5% trạng thái đã trang bị chết vì rời bộ (xem 5.4).
- **Mức có > 2 tín hiệu / (phiên, chiều):** số tín hiệu là tín hiệu thứ ≥ 3 ở cùng mức (|ΔE| ≤ 1) — A-v4 một mình: 3; A-v5: phần v4 5, phần VCL 0 (khoá mức chặn phần VCL; phần v4 không xét khoá nên vẫn có thể thứ ≥ 3).
- **Tỉ lệ lệnh VCL trùng vùng v4:** 42 / 131 = 32%.
- **Hai trạng thái trên hai vùng VCL kề:** giữ cả hai (plan mục 5-7); cặp lệnh VCL cùng phiên cùng chiều cách nhau ≤ 5 nến: 0.
- **Lệnh VCL mở lại (Q9):** 7 / 131 lệnh VCL; trạng thái VCL mở lại = 936 / 6033 lần mở.

## 6. Đối chứng (6 phép so có phán quyết; ngưỡng NGUYÊN PLAN-LAN-CHAM mục 5)

Mỗi ô: R TB thật · TB đối chứng [5%; 95%]. "khác ▲" = **hơn**, "khác ▼" = **kém hơn**, "≈" = **không hơn**, "không áp dụng" = **n quá nhỏ** (cần ≥ 10 lệnh ở CẢ TRAIN và TEST). Tổng 6 phép ⇒ với ~5% mỗi phép, ~0,3 ô "khác" có thể do ngẫu nhiên.

| nhóm lệnh | đối chứng | GỘP | TRAIN | TEST | T8 | T9 | T10 | phán quyết | chữ |
|---|---|---|---|---|---|---|---|---|---|
| A-v5 toàn bộ | ĐC1 cùng trạng thái | -0.18 · -0.15 [-0.30; -0.00] | -0.07 · -0.15 [-0.34; +0.04] | -0.32 · -0.15 [-0.38; +0.08] | -0.15 · -0.14 [-0.37; +0.10] | -0.06 · -0.15 [-0.40; +0.14] | -0.38 · -0.15 [-0.43; +0.17] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | **không hơn** |
| A-v5 toàn bộ | ĐC2 control_sample | -0.18 · -0.09 [-0.27; +0.08] | -0.07 · -0.09 [-0.31; +0.17] | -0.32 · -0.10 [-0.33; +0.17] | -0.15 · -0.09 [-0.36; +0.22] | -0.06 · -0.10 [-0.40; +0.17] | -0.38 · -0.10 [-0.39; +0.26] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | **không hơn** |
| A-v5 toàn bộ | ĐC3 dời cả bản đồ 3–15 giá | -0.18 · -0.09 [-0.24; +0.05] | -0.07 · -0.09 [-0.31; +0.12] | -0.32 · -0.09 [-0.31; +0.10] | -0.15 · -0.10 [-0.33; +0.16] | -0.06 · -0.06 [-0.36; +0.15] | -0.38 · -0.12 [-0.38; +0.09] | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | **không hơn** |
| riêng lệnh VCL | ĐC1-VCL | -0.11 · -0.12 [-0.36; +0.10] | -0.16 · -0.13 [-0.44; +0.18] | -0.06 · -0.10 [-0.40; +0.21] | +0.08 · -0.13 [-0.49; +0.25] | -0.28 · -0.11 [-0.45; +0.24] | -0.17 · -0.10 [-0.51; +0.27] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | **không hơn** |
| riêng lệnh VCL | ĐC2-VCL | -0.11 · -0.10 [-0.38; +0.19] | -0.16 · -0.09 [-0.43; +0.30] | -0.06 · -0.10 [-0.52; +0.27] | +0.08 · -0.11 [-0.52; +0.34] | -0.28 · -0.09 [-0.55; +0.35] | -0.17 · -0.09 [-0.53; +0.47] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | **không hơn** |
| riêng lệnh VCL | ĐC3-chỉ-dời-VCL | -0.11 · -0.10 [-0.34; +0.16] | -0.16 · -0.04 [-0.38; +0.30] | -0.06 · -0.16 [-0.45; +0.16] | +0.08 · +0.03 [-0.44; +0.47] | -0.28 · -0.12 [-0.55; +0.28] | -0.17 · -0.25 [-0.71; +0.21] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | **không hơn** |

- ĐC3 (dời cả bản đồ): số lệnh/ngày TB 4.71 [4.34; 5.18] (thật 5.31).
- ĐC3-chỉ-dời-VCL: số lệnh VCL/ngày TB 1.71 [1.47; 1.97] (thật 2.15).
- A-v5 toàn bộ — ĐC1 cùng trạng thái: hồ ĐC1 = 17423 nến.
- riêng lệnh VCL — ĐC1-VCL: hồ ĐC1 = 17668 nến.

## 7. Độ nhạy quanh A-v5 — đổi MỘT thứ một lần, IN RA, KHÔNG chọn lại

| biến thể | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R | số lệnh VCL |
|---|---|---|---|---|---|---|---|
| **A-v5 ô chính** | 324 | 5.31 | 22.2% | -0.18 [-0.36; +0.01] | 175 / -0.07 | 149 / -0.32 | 131 |
| S1 bỏ luật cú phá thật (máy v4 nguyên xi trên VCL) | 347 | 5.69 | 22.5% | -0.17 [-0.34; +0.00] | 185 / -0.12 | 162 / -0.23 | 157 |
| S2 SL vùng VCL qua cạnh gần (E ∓ 1 + 0,3) | 533 | 8.74 | 26.1% | -0.04 [-0.18; +0.11] | 302 / +0.07 | 231 / -0.18 | 356 |
| S3 bỏ khoá mức giá | 326 | 5.34 | 22.1% | -0.19 [-0.36; +0.01] | 176 / -0.07 | 150 / -0.33 | 134 |
| S4 TP 2R (không gộp vào kết luận) | 337 | 5.52 | 29.4% | -0.19 [-0.34; -0.04] | 181 / -0.11 | 156 / -0.28 | 139 |
| S5 chỉ vùng VCL KHÔNG trùng vùng v4 (bỏ tín hiệu VCL trùng trước luật 1 lệnh mở) | 302 | 4.95 | 20.9% | -0.24 [-0.42; -0.06] | 163 / -0.10 | 139 / -0.41 | 90 |
| (tham chiếu) A-v4 — VCL tắt | 218 | 3.57 | 19.7% | -0.30 [-0.50; -0.07] | 119 / -0.11 | 99 / -0.52 | 0 |

## 8. Tiêu chí "đáng port C#" (đăng ký trước, plan mục 4) — chấm tự động

| điều kiện T1-v5 | đạt? | số |
|---|---|---|
| (1) n(A-v5) ≥ 40 | ĐẠT | n = 324 |
| (2) R TB TEST(A-v5) ≥ -0.08 và n TEST ≥ 15 | **KHÔNG** | R TEST = -0.32, n TEST = 149 (R TEST của A cũ đo lại = -0.08, n = 8) |
| (3) R TB TRAIN(A-v5) ≥ -0.30 | ĐẠT | R TRAIN = -0.07 |
| (4) không đối chứng nào (6 phép) ra "thật kém hơn" | ĐẠT | ĐC1 cùng trạng thái: không hơn; ĐC2 control_sample: không hơn; ĐC3 dời cả bản đồ 3–15 giá: không hơn; ĐC1-VCL: không hơn; ĐC2-VCL: không hơn; ĐC3-chỉ-dời-VCL: không hơn |
| (5) test 3.6 xanh, tái tạo 3.0 đúng | ĐẠT | 15 passed in 32.81s |
| (6) 18:00–19:20 không tệ hơn phần còn lại > 0.5R (n ≥ 10) | ĐẠT | n = 27, R -0.02 vs phần còn lại -0.20 |
| (7) VCL thêm ròng ≥ +31 lệnh (≥ +0,5/ngày) | ĐẠT | n(A-v5) − n(A-v4) = +106 (+1.74/ngày); lệnh VCL = 131 |
| (8) R TB lệnh VCL ≥ R TB lệnh v4 trừ hiệu nhỏ nhất phát hiện được, ở CẢ TRAIN và TEST | ĐẠT | TRAIN: VCL -0.16 vs v4 -0.01 (hiệu nhỏ nhất 0.72); TEST: VCL -0.06 vs v4 -0.50 (hiệu nhỏ nhất 0.78) |

- **T1-v5: KHÔNG ĐẠT.** Điều kiện trượt: (2) R TB TEST(A-v5) ≥ -0.08 và n TEST ≥ 15.
- **T2: KHÔNG ĐẠT** (TRAIN -0.07, TEST -0.32, n TEST 149, vượt đối chứng A-v5: 0/3). **Chưa có lợi thế đo được** trên 61 phiên.

## 9. So với DỰ ĐOÁN ĐĂNG KÝ TRƯỚC của Opus (plan 3.7)

| dự đoán | đo được | đúng? |
|---|---|---|
| Số lệnh tăng rõ: A-v5 ≈ 300–450 (≈ 5–7,5/ngày), VCL thêm ≈ +80…+230 sau khi trừ lệnh A-v4 bị chen | 324 lệnh (5.31/ngày); VCL thêm ròng +106 (lệnh VCL 131, A-v4 mất 25, v4 mới 0) | ĐÚNG |
| WR không tăng: A-v5 17–22% (A-v4 19,7%) | 22.2% (+2.5 điểm so A-v4) | **SAI** |
| R TB −0,20 … −0,45 | -0.18 | **SAI** |
| lệnh VCL và lệnh vùng v4 chênh nhỏ hơn mức phát hiện được | VCL -0.11 · v4 -0.23 · hiệu nhỏ nhất phát hiện được 0.53 | ĐÚNG |
| cả 6 phép so ≈ (không hơn) | ĐC1 cùng trạng thái: không hơn, ĐC2 control_sample: không hơn, ĐC3 dời cả bản đồ 3–15 giá: không hơn, ĐC1-VCL: không hơn, ĐC2-VCL: không hơn, ĐC3-chỉ-dời-VCL: không hơn | ĐÚNG |
| T1 không đạt | T1 KHÔNG ĐẠT | ĐÚNG |

## 10. Đánh giá (viết tay sau khi đọc số — `report/_eval_a_v5.txt`)

Viết tay sau khi đọc số (không đổi luật/hằng số nào theo số này).

1. **Thêm vùng VCL làm tăng số lệnh, đúng như dự đoán, nhưng không thêm chất lượng.** A-v5 có 324 lệnh (5,31/ngày) so với A-v4 218 (3,57/ngày): +106 lệnh ròng (131 lệnh VCL, 25 lệnh A-v4 bị chen mất). WR 22,2% (A-v4 19,7%), R TB −0,18 (A-v4 −0,30). Cả hai đều âm, hoà vốn cần WR ≈ 27%.
2. **Phần "R tốt hơn" không phải do lệnh VCL.** Lệnh VCL riêng R TB −0,11 (tổng −14,8R), lệnh vùng v4 trong A-v5 R TB −0,23. Tổng R của A-v5 là −59,7R so với A-v4 −64,3R: chênh +4,6R, và chênh đó đến từ 25 lệnh A-v4 bị VCL chen mất có R TB −0,78 (tổng −19,4R, chỉ 8% thắng). Đó là may rủi của việc lệnh nào bị chen, không phải bằng chứng vùng VCL tốt: nếu 25 lệnh bị chen đó là lệnh thắng thì A-v5 tệ hơn A-v4. Không được viết "vùng hỗ trợ/kháng cự giúp A tốt hơn".
3. **Câu bắt buộc:** số lệnh tăng nhưng mỗi lệnh vẫn lỗ trung bình (−0,18R), nên lỗ của phần thêm cộng dồn theo số lệnh (lệnh VCL riêng −14,8R trên 131 lệnh).
4. **Đối chứng:** cả 6 phép "không hơn" (A-v5: ĐC1, ĐC2, ĐC3; riêng lệnh VCL: ĐC1-VCL, ĐC2-VCL, ĐC3-chỉ-dời-VCL). Vùng VCL bị dời 3–15 giá vẫn cho 1,71 lệnh VCL/ngày (thật 2,15) và R tương đương ⇒ vị trí vùng không tạo ra gì, như bằng chứng cũ. Công suất: lệnh VCL so lệnh v4 chỉ phân biệt được chênh ≥ 0,53R (TEST ≥ 0,78R), nên "VCL tốt hơn/tệ hơn v4" không kết luận được. 
5. **Các nhóm con đẹp/xấu chỉ để mô tả, không kết luận:** ví dụ lệnh VCL trùng VAH_D (n = 10, R +1,34) hay vùng chỉ số tròn (n = 49, R +0,25 [−0,24; +0,82]) có khoảng tin cậy chứa 0 và chọn sau khi thấy số (nhiều nhóm đã cắt); lệnh "trùng loại khác" n = 24 R −0,73 ngược chiều. Không nhóm nào vượt đối chứng.
6. **Độ nhạy S1–S5 (không chọn lại):** bỏ luật cú phá thật (S1) chỉ thêm 26 lệnh VCL và R gần như không đổi (−0,17); SL qua cạnh gần (S2) cho 356 lệnh VCL, 533 lệnh tổng, R −0,04 (TRAIN +0,07, TEST −0,18) — cho thấy trần SL 4 giá đang loại phần lớn vùng rộng (vùng 2,5–5 giá hầu như không ra lệnh nào: 9 + 1 lệnh), nhưng SL gần hơn không cải thiện TEST. Không đổi bản chính theo S2.
7. **Rủi ro đổi mã vùng:** 24,5% trạng thái đã trang bị chết vì rời bộ (dưới ngưỡng 30%); chỉ 6% trong số rời bộ có eid mới chồng lên ≤ 5 nến.
8. **Port:** T1 KHÔNG ĐẠT, chỉ trượt điều kiện (2): R TB TEST −0,32 < −0,08 (n TEST 149); T2 không đạt ("chưa có lợi thế đo được" trên 61 phiên). Các điều kiện (1), (3)–(8) đều đạt (kể cả (7) +106 lệnh và (8) lệnh VCL không kém lệnh v4), nhưng đó chỉ nói thêm VCL không làm tệ hơn mức đo được, không nói A có lợi thế. Port C# chỉ làm khi người học xác nhận.
9. **Dự đoán của Opus:** đúng ở số lệnh (324 trong 300–450; VCL ròng +106 trong +80…+230), lệnh VCL ≈ lệnh v4, cả 6 phép "không hơn", T1 không đạt. Sai nhẹ ở hai chỗ: WR 22,2% (dự đoán 17–22%) và R TB −0,18 (dự đoán −0,20…−0,45) đều lệch ra ngoài khoảng 0,2–2,5 điểm theo hướng TỐT hơn, và độ lệch đó (nằm trong sai số, mục 2 ở trên) đến từ việc 25 lệnh thua bị chen mất.


_Thời gian chạy toàn bộ: 374 giây._
