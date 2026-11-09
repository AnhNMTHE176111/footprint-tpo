# PLAN C-v3 — Setup C "Fade cạnh": thêm HÀNH LANG HỖ TRỢ / KHÁNG CỰ (S/R) làm nơi fade

Tác giả: kiến trúc sư (chỉ thiết kế). Ngày: 2026-10-23. Người thực hiện + backtest: **Sonnet**.
Dữ liệu DUY NHẤT: `D90 = data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d` (61 phiên sạch; TRAIN ≤ 2026-09-15 = 35 phiên, TEST từ 09-16 = 26 phiên). KHÔNG chạy file 2 năm.
Thuật ngữ: **buy / sell / limit / market** giữ tiếng Anh. "Hợp lưu N vùng", không "cluster". "Hành lang" = khoảng trống giữa vùng hỗ trợ gần nhất bên dưới và vùng kháng cự gần nhất bên trên giá.

---

## 0. Nói thẳng trước khi làm (rủi ro chính)

- **Vị trí vùng S/R ở dự án này đã đo 3 lần độc lập là KHÔNG mang thông tin**: SR-KET-QUA (65 phiên, mọi loại mức ≈ mức ngẫu nhiên), VCL 5 vòng (P(chạm) chỉ phụ thuộc khoảng cách), HVN 474 phiên, Benzo×VCL (0/35 phép so vượt ngưỡng; C "tại vùng VCL" còn kém hơn "ngoài vùng" −0,37 vs +0,01). **Kỳ vọng trước của plan này: S/R ≈ đối chứng.** Plan này được thiết kế để ĐO điều đó cho sạch, không để "tìm ra" lợi thế.
- Ước lượng sơ bộ (mục 1.3): lớp S/R sinh **~470 lệnh** trên 61 phiên, gấp ~4,5 lần C0 ⇒ trong bản gộp, S/R **chiếm phần lớn lệnh** và quyết định kết quả. Ở WR ~12–30% hiện tại, thêm lệnh không có lợi thế = thêm lỗ. Tiêu chí thật là **R TB**, số lệnh chỉ là chỉ số phụ.

---

## 1. Chốt MỘT định nghĩa "vùng S/R" — khảo sát ứng viên

### 1.1 Ứng viên có trong repo

| ứng viên | có sẵn? | ghi chú |
|---|---|---|
| **VCL v5** (`vung-canh-lenh/research/vcl5.py`, cache `report/cache_lc/v5.pkl`, nạp qua `benzo_vcl.load_rec`) | **CÓ** — bộ vùng hiển thị từng nến, rộng [2, 5] giá, có `eid` ổn định, đã test không nhìn trước (`test_vcl.py::test_v4_khong_nhin_truoc`, `test_lan_cham.py::test_v5_…`), đã có C# `VclCore.cs` | gộp sẵn: swing M5 k=5 (B), swing M15 k=3 (B15), **mốc phiên** (đỉnh/đáy/đóng phiên trước, VA hôm qua, biên Á, VA Âu, POC trần) (C), **số tròn** 10/50/100 (D). Bộ hiển thị = vùng chứa giá + 2 gần + 1 xa mỗi phía (~6,4 vùng/nến). |
| `kernel.ZONE_COLS` | có | **không** có đỉnh/đáy phiên trước (cái đó nằm trong VCL loại C và `sr_measure.py`). VA hôm qua / VA Âu / IB **đã là băng của C0**; VWAP ngày/tuần là đường trượt, không phải cạnh tĩnh (SR-KET-QUA: ≈ ngẫu nhiên). |
| naked POC, HVN ngày/tuần (`kernel._zones`) | có | POC trần đã nằm trong VCL. **HVN loại** (đã đo 474 phiên ≈ ngẫu nhiên; VCL cũng bỏ). |
| swing M30/H1 | **chưa có** | gần nhất là B15 (M15 k=3) trong VCL; viết mới + port C# mới mà swing đã đo ≈ ngẫu nhiên ⇒ không làm. |
| số tròn | có (VCL loại D) | 28% dòng hiển thị VCL là vùng **chỉ có số tròn** (`mask == 8`). |

### 1.2 Định nghĩa chốt
**Vùng S/R = bộ vùng ĐANG HIỂN THỊ của VCL v5 tại nến i** (mọi loại, đúng cái người học thấy trên chart Quantower), lấy từ `benzo_vcl.load_rec(df)`. Lý do: đã gộp gần hết ứng viên, đã chứng minh không nhìn trước, đã có C#, và không phát minh định nghĩa thứ hai. Bit `mask`: B = 1, B15 = 2, C = 4, D = 8.

### 1.3 Ước lượng số lệnh (đã chạy máy rút gọn, CHỈ ĐẾM, không xem WR/R)
Máy rút gọn = máy 2.1 nhưng cạnh bám `eid` thay vì đóng băng; chia 61 phiên.

| biến thể nguồn | cạnh gần (bản chính) | cạnh xa |
|---|---|---|
| VCL đầy đủ | **~467 lệnh (~7,7/ngày)** | ~539 |
| VCL bỏ vùng chỉ-số-tròn | ~373 (~6,1/ngày) | ~274 |
| chỉ swing (B, B15) | ~359 | ~268 |
| chỉ mốc phiên (C) | ~118 (~1,9/ngày) | ~73 |
| chỉ số tròn thuần (D) | ~233 | ~176 |
| ZONE_COLS kernel | ~0 lệnh mới (đã là C0) | — |

Trùng nến với C0: chỉ 3–6 lệnh ⇒ gần như toàn bộ là lệnh MỚI. ~1.400 hành lang sinh trên toàn file (~22/phiên), phủ ~66% số nến.

---

## 2. Đặc tả số học

### 2.1 Từ "vùng" (hộp 2–5 giá) sang "băng cân bằng" cho C
C cần một **băng** [lo, hi] rộng ≥ 6 để: (a) có cạnh để chọc qua rồi đóng lại, (b) có cạnh đối diện làm TP ≥ 2R, (c) chạy `kernel.mode_frame`. Một vùng S/R đơn lẻ không có (b) và (c) ⇒ **băng = HÀNH LANG giữa hai vùng S/R**:

- **Cạnh trên** = mặt DƯỚI của vùng kháng cự gần nhất phía trên (`R.lo`); **cạnh dưới** = mặt TRÊN của vùng hỗ trợ gần nhất phía dưới (`S.hi`). ("Cạnh gần".) Tín hiệu sell = nến chọc vào vùng kháng cự ≥ 2 tick rồi đóng lại dưới `R.lo` — đúng ý "chạm kháng cự bị từ chối", không đòi xuyên cả hộp. Độ nhạy: cạnh xa (`R.hi`, `S.lo`).
- **Độ rộng tối thiểu** = 6 giá (như C0), đo giữa hai cạnh.
- **TP** = cạnh đối diện, phải ≥ 2R (hành lang không có POC — giống L3).
- **Chế độ cân bằng: CÓ áp dụng, trên chính hành lang** (không trên băng C0). Lý do: (1) "cân bằng" của hành lang = chưa có nến M5 đóng ngoài S/R = S/R đang giữ — đúng nghĩa trader; (2) tiền lệ L3 (VA_C) dùng băng cục bộ + `mode_frame`; (3) bắt cân bằng trên băng C0 sẽ xoá hầu hết S/R nằm ngoài VA hôm qua — chạy như **độ nhạy** "+ cân bằng băng chủ". **Bắt buộc ĐÓNG BĂNG hành lang**: nếu tính lại theo giá mỗi nến thì hành lang luôn chứa giá ⇒ luôn BALANCE ⇒ chế độ vô nghĩa.

### 2.2 Máy hành lang (mỗi phiên, tối đa 1 hành lang sống; chỉ dùng nến ≤ i và dòng VCL `bar ≤ i`)
Đầu vào: `df` (kernel), `rec` (VCL: bar, lo, hi, eid, mask), `shift` (δ theo phiên, mặc định 0), `mask_ok` (bộ lọc, mặc định nhận hết), `face` ('near'|'far'), `min_w = 6.0`. `m5 = K.m5_bars(df)` ⇒ tập `last_pos`.
Trạng thái: `cur` (None hoặc hành lang: id, sno, lo_face, hi_face, eid_s, eid_r, S/R lo-hi-mask, birth) + `(r, prev_side)` **chép đúng ngữ nghĩa `kernel.mode_frame`**.
Với mỗi nến i theo thứ tự:
1. Nến đầu phiên ⇒ `cur` chết (`het_phien`), `r = 0, prev_side = 0`.
2. **Tô**: `band_lo[i], band_hi[i], cid[i]` = của `cur` (NaN/−1 nếu không có). Tô TRƯỚC khi cập nhật ⇒ hành lang sinh ở i chỉ có hiệu lực từ i+1.
3. Nếu i là `last_pos` của một nến M5: có `cur` ⇒ `out = +1 nếu close[i] > hi_face, −1 nếu < lo_face, 0 nếu trong`; `out == 0` ⇒ `r = 0, prev = 0`; ngược lại `r = r+1 nếu out == prev else 1`, `prev = out`; `TREND` khi `r ≥ 2` và khoảng vượt ≥ 3,0 (`CONST m5_trend_runs / m5_trend_dist`) ⇒ `cur` CHẾT (`trend`). Không có `cur` ⇒ `r = 0, prev = 0` (đúng nhánh `band_src == ''` của kernel). **Không reset `r` khi sinh hành lang mới** (kernel cũng không) — test 4.3 #7 kiểm khớp.
4. `cur` còn sống mà `eid_s` hoặc `eid_r` không còn trong dòng VCL của nến i (sau lọc `mask_ok`) ⇒ CHẾT (`mat_vung`).
5. Không có `cur` (kể cả vừa chết ở bước 1/3/4), nến i không splice/thin ⇒ thử SINH: lấy các dòng VCL `bar == i` (cộng δ, lọc mask); `c = close[i]`; có vùng chứa c (`lo ≤ c ≤ hi`) ⇒ không sinh; `R` = vùng có `lo > c` nhỏ nhất (hoà ⇒ eid nhỏ hơn), `S` = vùng có `hi < c` lớn nhất (hoà ⇒ eid nhỏ hơn); thiếu một ⇒ không sinh; cạnh theo `face`; `hi_face − lo_face ≥ min_w` ⇒ sinh, `birth = i`.
6. **Cạnh ĐÓNG BĂNG** từ lúc sinh (không bám eid khi VCL dịch hộp) ⇒ khoá đếm "≤ 2 lệnh / (phiên, cạnh)" của `detect` dùng nguyên. Ghi số hành lang mà hộp eid đã dịch > 1 tick trong đời (chỉ báo).
Đầu ra: `frame` (sr_lo, sr_hi, sr_id), `log` (mỗi hành lang: phiên, giờ VN sinh, S/R lo-hi-mask, rộng, chết lúc nào, vì sao, tuổi, số lệnh), `funnel` (số lần thử sinh, bị chặn vì trong vùng / thiếu phía / hẹp < 6, chết theo lý do).

Chỉ 2 tham số tự do mới: chọn cạnh (gần) và luật chết `mat_vung`. Còn lại tái dùng (rộng 6, TREND 2 nến M5 / 3 giá, xuyên 2 tick, TP ≥ 2R).

### 2.3 Cắm vào C
- **L4** = hành lang S/R: `zc = zones_c_v6.band_zcols(D.zc0, sr_lo, sr_hi, poc=None)`; `mf = K.mode_frame(df, zc, K.m5_bars(df, zc))`; tên cạnh `('SR_HI', 'SR_LO')` khi `sr_id ≥ 0`. Gọi **`setup_c_v6.detect` nguyên xi** (đã có `zone_name`), xuyên 2 tick, rộng ≥ 6, trừ 18:00–19:20 VN, mọi luật lọc nến giữ nguyên.
- Lưu ý (ghi Q trong report): `detect` đọc band + mode từ nến M5 ĐÃ ĐÓNG gần nhất ⇒ hành lang mới chỉ fade được sau nến M5 đầu tiên của nó, và hành lang vừa chết vì `mat_vung` có thể còn được đọc tối đa 4 nến M1 — giống L3 v6, chấp nhận.
- **Gộp thêm (`merge_add(base, new)`)**: nến nào base có entry ⇒ giữ base, bỏ L4 ở nến đó; còn lại thêm L4; rồi `K.simulate(one_at_a_time=True)`. (Lớp cũ thắng mọi trùng nến ⇒ Δ sạch; phần mất do "1 lệnh mở" báo riêng.)

---

## 3. Thiết kế đo

### 3.1 Ô đo (TP chính: C0/C4 như cũ, L4 = cạnh đối diện ≥ 2R; chạy thêm TP cố định 2R)
| ô | nội dung |
|---|---|
| **C0** | tái tạo vòng 1 (n 103, R TB −0,43; fixed2 121, −0,26) |
| **C4** | tái tạo v6 (n 191, WR 12,6%, R TB −0,31, tổng −58,8; fixed2 220, −0,17) |
| **C5** | L4 riêng (S/R) |
| **C0+SR** | `merge_add(C0, L4)` |
| **C6 = C4+SR** | `merge_add(C4, L4)` — "setup mới gồm mọi phần người dùng bảo thêm" |

Chỉ số mỗi ô: n, lệnh/ngày (÷61), WR, R TB + KTC bootstrap 95% (10.000, hạt 0), tổng R, chuỗi thua, TRAIN/TEST, pha A/EU/US, tháng T8/T9/T10. C5 tách thêm theo loại vùng của cạnh bị fade (có B/B15 · có C · chỉ D) — chỉ báo, không phán.
**Tách đóng góp:** Δ(C0+SR − C0); Δ(C6 − C4); số lệnh C4 bị chặn vì L4 đang mở (khớp `idx`) và tổng R của chúng; số lệnh L4 trong C6.

### 3.2 Đối chứng (cho C5; hạt 20261024, cùng ma trận δ `D.dsh`)
- **ĐC-a dời bản đồ S/R**: cộng δ[phiên của dòng, bản] ~ U[3, 15] dấu ngẫu nhiên vào `lo/hi` mọi dòng VCL, chạy LẠI cả máy 2.2 (sinh theo giá thật) + mode + detect. 100 bản.
- **ĐC-b vào ngẫu nhiên tại vùng**: `setup_c_v6.dc_b(D, L4, t, flt=lambda t: t)` (dùng `ctrl_columns` cho tên SR_HI/SR_LO), 200 lần.
- **ĐC-c khớp khoảng cách**: `setup_c_v6.dc_dist(D, t)` — nến ngẫu nhiên cùng phiên + pha, cùng chiều, SL/TP cách entry đúng như lệnh thật, 200 lần. **Đây là đối chứng chính** (bài học VCL: đối chứng không khớp khoảng cách cho dấu giả).
- Áp thêm ĐC-a và ĐC-c cho **C6** để biết bản gộp có khác gộp-trên-vùng-dời không.
- Phán quyết: `BV.verdict` (ngoài dải 5–95% ở CẢ TRAIN và TEST, cùng dấu, ≥ 2/3 tháng cùng dấu, |hiệu| > 2 sai số; chỉ khi ≥ 10 lệnh mỗi nửa).

### 3.3 Công suất (in TRƯỚC bảng chính)
σ_R ≈ 1,6; hiệu nhỏ nhất phát hiện được = 2,8·σ/√n: n 170 (TEST C5) ⇒ ~0,34R; n 470 ⇒ ~0,21R. Số phép so có phán quyết: 3 ĐC × C5 + 2 ĐC × C6 = **5** ⇒ một ô "vượt" đơn lẻ chưa đủ tin.

### 3.4 Lưới độ nhạy (khai báo trước, in ĐỦ, mỗi dòng đổi MỘT thứ, không chọn ô)
1. cạnh xa (`R.hi`, `S.lo`); 2. bỏ vùng chỉ-số-tròn (`mask_ok = mask != 8`); 3. + cân bằng băng chủ (`gate`: `D.P['mf']['mode'][i] == 'BALANCE'`); 4. rộng tối thiểu 8; 5. chặn thêm 19:20–20:30 VN (`EXCL_VO`). In cho C5 và C6.

### 3.5 Tiêu chí (khai báo trước, R TB là chính)
- **S0 — giữ hướng:** R TB(C5) ≥ R TB(C0) ở CẢ TRAIN và TEST **và** R TB(C6) ≥ R TB(C4) ở CẢ TRAIN và TEST **và** WR(C6) ≥ WR(C4) − 3 điểm **và** không đối chứng nào nói "kém hơn thật".
- **S1 — đáng port C# để ghi log live (vẫn tắt mặc định):** S0 + C5 TRAIN ≥ −0,10 và TEST ≥ 0, n TEST ≥ 30 **và** C5 vượt **ĐC-c khớp khoảng cách** (R TB > p95) ở ≥ 1 nửa với n ≥ 10.
- **S2 — lợi thế đo được (mới được nói "có"):** C5 TRAIN > 0 và TEST > 0, n TEST ≥ 60, vượt CẢ ba đối chứng theo `BV.verdict`.
- Không đạt S0 ⇒ ghi **"không"**, KHÔNG thêm S/R vào C, KHÔNG mở vòng tinh chỉnh trên cùng dữ liệu.

### 3.6 Chống tự lừa
- Commit hằng số + máy + test TRƯỚC lần chạy kết quả đầu; report in hash commit đó.
- In phễu + nhật ký hành lang TRƯỚC bảng lệnh. Người học tìm 5 hành lang trên Optimus Flow (bật indicator VCL) và ghi phán đoán TRƯỚC khi mở nhật ký (`tpo/EVIDENCE-DRILLS.md`).
- "Chỗ tự quyết" ghi thành mục Q riêng như v6.

---

## 4. Việc cho Sonnet (thứ tự)

KHÔNG sửa: `kernel.py`, `setup_c_fade_canh.py`, `setup_c_v6.py`, `zones_c_v6.py`, `benzo_vcl.py`, mọi file trong `vung-canh-lenh/`. Chỉ import.

### 4.1 `research/zones_c_v7.py` (mới)
- Hằng số: `MIN_W = 6.0`, `FACE = 'near'`, `TREND_RUNS = K.CONST['m5_trend_runs']`, `TREND_DIST = K.CONST['m5_trend_dist']`, `MASK_ROUND_ONLY = 8`.
- `load_sr(df) -> DataFrame` = `benzo_vcl.load_rec(df)` sắp theo (bar, lo, eid); assert `bar.max() < len(df)` và có đủ cột `bar, lo, hi, eid, mask`.
- `class SrIndex(rec)`: mảng numpy + `start/end` theo bar (searchsorted) để lấy dòng của nến i O(1).
- `sr_corridors(df, idx, shift=None, mask_ok=None, face=FACE, min_w=MIN_W) -> dict(frame, log, funnel, internal_mode5)` — máy 2.2, thuần vòng lặp, không nhìn trước. `internal_mode5` = mode tính trong máy theo từng nến M5 (cho test khớp kernel).
- `layer_sr(df, template, corr) -> (zc, names, mf)` như 2.3.

### 4.2 `research/setup_c_v7.py` (mới)
- Hằng số đầu file: `PEN 2`, `MIN_W 6`, `EXCL`, `EXCL_VO`, `REPS 100`, `SEED 20261024`, `CTRL_DRAWS 200`, `DIST_DRAWS 200`, `MIN_N 10`, `SIGMA_R 1.6`, `EXPECT_C4 = dict(poc=(191, -0.31, -58.8), fixed2=(220, -0.17))`.
- `run_all_v7(D, tp_mode, sr_kw)`: gọi `setup_c_v6.run_all(D, tp_mode=tp_mode)` lấy C0/C4 nguyên xi; dựng L4; `entries_of` (của v6) cho L4; `merge_add`; trả C0, C4, C5, C0+SR, C6.
- `merge_add(base, new)`; `dc_a_sr(D, ...)`; tái dùng `setup_c_v6.dc_b`, `dc_dist`, `gstats`, `bands_of`, `cmp_vs`, `full_stats`, `BV.verdict`.
- Ảnh: 5 hành lang có lệnh TRAIN + 5 TEST (chọn đều theo thời gian) → `report/img/c_v7_sr_*.png`.
- Ghi `report/RESULTS-C-V7.md`: 0 hash · 1 công suất · 2 phễu + nhật ký hành lang · 3 bảng ô 3.1 (TP chính + fixed2) · 4 tách đóng góp · 5 đối chứng · 6 lưới 3.4 · 7 tiêu chí S0/S1/S2 (máy chấm) · 8 chỗ tự quyết Q · **9 BẢNG TÓM TẮT** (mục 5).

### 4.3 `research/test_setup_c_v7.py` (pytest)
1. `test_reproduce_c0` — L0 ra đúng từng lệnh C0 (103 / −0,43; fixed2 121 / −0,26).
2. `test_reproduce_c4_v6` — C4 = 191 lệnh, R TB −0,31, tổng R −58,8 (±0,05); fixed2 220.
3. `test_vcl_alignment` — `rec.bar.max() < len(df)`, mỗi nến phiên sạch có ≥ 1 dòng, eid kiểu int.
4. `test_birth_synthetic` — df tổng hợp + rec tay: S [100, 102], R [110, 112], close 105 ⇒ hành lang [102, 110] sinh ở i, tô từ i+1 (ở i là NaN); `face='far'` ⇒ [100, 112].
5. `test_no_birth` — close nằm trong hộp; thiếu phía trên; rộng 5,8 < 6 ⇒ không sinh.
6. `test_death` — 2 nến M5 đóng trên `hi_face` ≥ 3 giá ⇒ chết sau `last_pos` thứ hai (`trend`); cách < 3 ⇒ sống (BREAK); eid R biến mất ⇒ `mat_vung`; sang phiên ⇒ `het_phien`.
7. `test_mode_parity` (D90 thật) — `internal_mode5` == `K.mode_frame(painted)` trên MỌI nến M5 có band; và không nến nào có `cid[i] == cid[last_pos]` mà kernel báo TREND.
8. `test_no_lookahead_cut` — với ~10 điểm cắt k: máy trên `df[:k]` + `rec[rec.bar < k]` cho `frame` y hệt bản đầy đủ tới k−1, và entries L4 `idx < k` y hệt (mẫu `test_setup_c_v6.test_no_lookahead_cut`).
9. `test_merge_add_keeps_base` — base không mất entry nào; trùng nến ⇒ base.
10. `test_shift_zero_equals_real` — shift toàn 0 ⇒ y hệt bản thật.

### 4.4 Quy trình
Viết code + test → `pytest` xanh → **commit hằng số (TRƯỚC khi chạy kết quả)** → chạy `python3 setup_c_v7.py` → commit kết quả → viết `RESULTS-C-V7.danhgia.md` theo S0/S1/S2 → commit + `git push origin main`, báo hash.

### 4.5 Port C#
**Chỉ khi đạt S1.** Khi đó: `BenzoZones` thêm `SrCorridor` đọc bộ vùng hiển thị từ `VclCore` (đã có C#), `DetectorC` thêm lớp L4 + tên `SR_HI/SR_LO`, replay parity theo `report/PARITY.md` khớp 100% lệnh, `build.sh` + test, commit, push. Không đạt S1 ⇒ **không port**, không đụng C#.

---

## 5. Định dạng BẢNG TÓM TẮT cuối (mục 9 của report — MỘT bảng, cho người dùng)

| | Setup cũ (C0, trước mọi thay đổi) | Setup mới (C4 + S/R: cổng D/P/b + VA nhỏ CHoCH + hành lang S/R) |
|---|---|---|
| Số lệnh (lệnh/ngày) | | |
| Winrate | | |
| R TB | | |
| Tổng R | | |

Dưới bảng: đúng 1 câu kết luận theo tiêu chí (đạt S0/S1/S2 hay không) + 1 câu "chỉ đo trên 61 phiên D90, chưa kiểm ngoài mẫu".

---

## 6. Rủi ro / điểm chưa chắc
- **R1** Vị trí S/R không mang thông tin (đo 3 lần) ⇒ khả năng cao nhất là C5 ≈ ĐC-c.
- **R2** L4 áp đảo số lệnh ⇒ C6 ≈ C5; phải đọc Δ, không đọc tổng.
- **R3** "1 lệnh mở" ⇒ lệnh L4 chặn lệnh C4; báo số lệnh C4 bị mất và R của chúng.
- **R4** Bộ hiển thị VCL đổi ~3 lần/giờ ⇒ hành lang sống ngắn (~22 lần sinh/phiên); luật `mat_vung` là quyết định tự do — đã ghi; không thêm độ nhạy cho nó.
- **R5** `detect` đọc band từ M5 đã đóng (trễ ≤ 4 nến) — như L3.
- **R6** Cache `v5.pkl` phải khớp D90; thiếu thì `load_rec` chạy lại engine (vài phút).
- **R7** 28% vùng chỉ là số tròn — có dòng độ nhạy bỏ chúng; không chọn theo kết quả.
- **R8** Chart người học phải chạy VCL đúng tham số v5 (`PARITY-VCL.md`) thì bài săn bằng chứng mới so được.
