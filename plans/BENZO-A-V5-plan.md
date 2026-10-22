# BENZO-A-V5 — Setup A "Phá hồi": A-v4 + thêm vùng hỗ trợ/kháng cự của Vùng Canh Lệnh (VCL v5)

Opus viết 2026-10-23 (vai: brainstorm + đặc tả). **Sonnet implement + backtest, làm ĐÚNG CHỮ.** Chỗ nào đặc tả không nói ⇒ xem mục 5
("quyết định mặc định"); vẫn không có ⇒ dừng và báo, không tự chế luật.

Đọc trước (theo thứ tự): `plans/BENZO-A-V4-plan.md` (toàn bộ) · `benzo-trader/research/setup_a_v4.py` (`detect`, `ctrl1/2/3`, `main`) ·
`zones_a_v4.py` · `report/RESULTS-A-V4.md` · `benzo_vcl.py` (`load_rec`, `ZoneMap`) · `report/BENZO-VCL.md` ·
`vung-canh-lenh/research/vcl5.py`, `vcl4.py` (`run_engine`), `vcl.py` (`break_update`) · `vung-canh-lenh/PLAN-LAN-CHAM.md` mục 2.5 + 5 ·
`vung-canh-lenh/research/report/LAN-CHAM.md` (mục Nhận xét).

**Dữ liệu (QĐ-6, như v4):** CHỈ `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d{.csv,_bars.csv}`. TRAIN = phiên ≤ 2026-09-15,
TEST từ 2026-09-16. 61 phiên sạch (TRAIN 35 / TEST 26), "lệnh/ngày" = n ÷ 61. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ SL (`kernel.simulate`).
1 giá = 1 USD = 10 tick. Giờ trong dữ liệu là UTC (VN = UTC+7).

**Thuật ngữ:** *VCL* = indicator Vùng Canh Lệnh · *bộ hiển thị* = các vùng VCL đang vẽ trên chart tại nến i (vùng chứa giá + 2 gần + 1 xa mỗi phía, tối đa 7) ·
*eid* = mã vùng ổn định của VCL · *slot* = ô của vùng trong bộ (K = đang chứa giá, N = gần, F = xa) · *đã trang bị* (armed) = cực trị cú phá đã cách cạnh ≥ D_MIN ·
*đối chứng* = cách vào lệnh "bừa" để so · *công suất thống kê* = chênh nhỏ nhất đo ra được · *bootstrap* = lấy mẫu lại có hoàn lại để ước khoảng tin cậy (KTC).

---

## 0. Tóm tắt quyết định (đọc trước, chi tiết ở mục 2)

| # | Câu hỏi | Chốt |
|---|---|---|
| 1 | Dùng vùng VCL nào? | **Mọi vùng trong bộ hiển thị tại nến đang xét** (K, N, F), kể cả vùng chỉ có số tròn 10 USD. Không lọc theo slot/điểm. |
| 2 | Cạnh E theo chiều phá | Phá lên ⇒ **E = `hi`** (mép trên); phá xuống ⇒ **E = `lo`**. Mép xa (đặt SL) = mép còn lại. Như HVN tuần dải của v4. |
| 3 | Vùng động hay cố định? | **Động** (như VWAP): E, mép xa lấy tại nến đang xét. Lý do đo được: biên một eid gần như đứng yên (đổi giữa hai nến kề: p99 = 0,075 giá). |
| 4 | Thế nào là cú phá trên vùng VCL? | Như v4 (nến M5 đóng ngoài dải) **+ điều kiện CÚ PHÁ THẬT** (chỉ cho VCL): trong chân cú phá phải có một nến M1 mà vùng **đang hiển thị** và giá **đóng ở phía trong** (≤ hi khi phá lên). Không có ⇒ không mở trạng thái. |
| 5 | Vùng rời bộ khi đang có trạng thái | Không vào lệnh khi vắng; trạng thái **hủy ở nến M5 kế tiếp** (đúng nhánh "vùng không có giá trị" của code v4). eid không bao giờ quay lại. |
| 6 | Đổi vai | Không thêm luật. Vai tính theo **chiều phá**. Vùng đã bị phá ngược lại (M5 đóng phía bên kia) mà VCL vẫn hiển thị ⇒ dùng tiếp theo chiều mới (máy v4 đã làm vậy). Luật đổi vai/chết nội bộ của VCL (xuyên ≥ 1u ⇒ đổi vai, điểm ×0,7; lần 2 ⇒ ứng viên chết) **giữ nguyên**, chỉ thể hiện qua việc vùng còn/mất trong bộ. |
| 7 | Trùng với vùng v4 | **Giữ riêng** máy trạng thái (để A-v4 không đổi) + **3 lớp chống đếm hai lần** + **gắn nhãn "trùng"** để tách báo cáo. |
| 8 | Tham số tự do mới | **0.** Mọi số dùng lại từ v4 (`ZONE_HALF` 1,0 · `LEG_LOOKBACK` 60 · trần 2 lệnh · D_MIN 2 · T_HOI 30 · hủy 1,0). |
| 9 | Mục đích trung thực | Thêm vùng VCL là để **TĂNG SỐ LỆNH**. Bằng chứng cũ nói vị trí vùng VCL không mang thông tin ⇒ **không kỳ vọng WR tăng**. Đo cả hai. |

---

## 1. Bối cảnh và bằng chứng đã có (không làm lại — chỉ trích)

- **A-v4** (`RESULTS-A-V4.md`): 218 lệnh (3,57/ngày), WR 19,7 %, R TB −0,30 [−0,50; −0,07]; TRAIN −0,11 (119) / TEST −0,52 (99). Cả 3 đối chứng ≈.
  Vùng **dời 3–15 giá** vẫn cho 3,19 lệnh/ngày, R −0,13 ⇒ vùng "đúng chỗ" không tạo ra gì. Không đạt T1 (R TEST −0,52 < mốc −0,08) ⇒ chưa port.
- **VCL vị trí không mang thông tin:** % đảo chiều vùng thật 51,1 % ≈ dời 51,3 % ≈ vùng giả cùng cỡ 48,8 % (`LAN-CHAM.md` mục Nhận xét 1); MAP15 cùng kết luận.
  Lần chạm ngay sau xuyên phá ("đổi vai") ≈ đối chứng (LAN-CHAM mục 7).
- **Benzo × VCL** (`BENZO-VCL.md`): vùng VCL phủ ~50 % số nến ("tại vùng" gần như không chọn lọc); lọc 4 setup theo vùng VCL không cải thiện; "chạm vùng là vào theo vai"
  cho −0,12R ≈ vùng dời. Hợp lưu SessionZones không mạnh hơn (`HOP-LUU-SZ.md`).
- **Số đếm sơ bộ của Opus** (script tạm chỉ đọc dữ liệu, không phải kết quả): trên 61 phiên sạch có **~5 100 lần M5 đóng ra ngoài một vùng VCL sau khi giá vừa ở phía trong
  (≈ 84/ngày)**, so với 2 577 trạng thái mở mới của cả 6 loại vùng v4. Bề rộng vùng bị phá: trung vị 2,25 giá, p75 3,2; 62 % ≤ 2,7 giá.
  Bộ hiển thị trung bình 6,4 vùng/nến; tuổi thọ eid trung vị 60 nến (p90 318); không eid nào biến mất rồi quay lại.

⇒ Người học muốn thêm "vùng hỗ trợ/kháng cự" vào A. Câu hỏi đo được: **(a) thêm được bao nhiêu lệnh, (b) lệnh thêm có tệ hơn lệnh v4 không, (c) có khác đối chứng không.**
Kỳ vọng hợp lý từ bằng chứng: (a) tăng nhiều, (b) ≈, (c) ≈. Và một sự thật phải nói: **thêm lệnh có R TB âm thì lỗ nhanh hơn, không phải tốt hơn.**

---

## 2. ĐẶC TẢ A-v5 = A-v4 (giữ nguyên toàn bộ) + tập vùng VCL

### 2.1 Giữ nguyên 100 % A-v4 (cấu hình (d) của plan v4)

Tập vùng `new` (VWAP_W, VWAP_D có Warm 30; HVN_W ≤ 3 dải PeakSharpness kẹp ≤ 2; HVN_D ≤ 3; VAH_D, VAL_D hôm qua), logic `mom`, **không** cấm 18:00–19:20,
`vblock = False` ở bảng chính, D_MIN 2,0 · T_HOI 30 từ cực trị cuối · hủy khi M5 đóng trong sâu > 1,0 · `n_min` 3 · thân CF 0,5 · SL = max(râu CF, mép xa ± 1) + 0,3, sàn 5 nến,
trần 4 giá · TP 3R · ≤ 2 lệnh/(phiên, vùng, chiều) · bỏ 3 nến sau nến dài nhất phiên · pha OFF · phiên thin/splice · mọi chỗ tự quyết Q1–Q11 của RESULTS-A-V4 (gồm Q9:
hết hạn rồi M5 ngoài kế tiếp mở lại ngay). **Không sửa** `setup_a_v4.py`, `zones_a_v4.py`, `kernel.py`, `benzo_vcl.py`, mọi file trong `vung-canh-lenh/`.

### 2.2 Nguồn vùng VCL

- Bộ hiển thị VCL v5 lấy y như `benzo_vcl.load_rec`: cache `vung-canh-lenh/research/report/cache_lc/v5.pkl` (khoá `'rec'`, cột `bar, lo, hi, score, mask, conf, ncand, eid, side, slot, d10`);
  thiếu cache ⇒ chạy lại `vcl5.run_engine` như hàm đó làm. **Import, không copy, không sửa.**
- **Khớp chuỗi nến (bắt buộc, dừng nếu sai):** `rec['bar']` là vị trí nến trong `V5.prepare(...)['df']`. Chạy `V5.load` + `V5.prepare` (không chạy engine) và assert
  `datetime` của df đó == `datetime` của `P.df` (setup_a_v4.load) từng phần tử, cùng độ dài 86 333. (benzo_vcl chỉ kiểm độ dài — chưa đủ.)
- Vùng tại nến i = các dòng `rec` có `bar == i` (tính từ nến ≤ i; không nhìn trước đã chứng minh bằng `test_lan_cham.py::test_v5_va_lan_cham_khong_nhin_truoc`).

### 2.3 Vùng VCL → vùng E của máy trạng thái

Mỗi eid là **một vùng riêng** của máy v4 với thuộc tính:

| thuộc tính (như dict vùng của `zones_a_v4`) | giá trị cho VCL | lý do |
|---|---|---|
| `name` (khoá đếm ≤ 2 lệnh) | `'VCL_%d' % eid` | trạng thái và đếm theo mã vùng ổn định |
| `ztype` | `'VCL'` | một loại cho báo cáo/đối chứng |
| `lo`, `hi` tại nến i | `lo`, `hi` của dòng `rec` (bar = i, eid); **NaN** khi eid không có trong bộ ở nến i | đúng thứ người học thấy trên chart tại nến i |
| `lo_raw`, `hi_raw` (chân cú phá) | = `lo`, `hi` (không có Warm) | |
| `dyn` | **True** — E lấy tại nến đang xét | biên gần như đứng yên (mục 1); `dyn=False` của v4 sẽ HỦY trạng thái mỗi khi biên nhích 0,025 giá (16 % số cặp nến kề) ⇒ sai |
| `band` | **True** — M5 đóng ngoài phía đối diện ⇒ hủy | là dải 2–5 giá, như HVN tuần |
| `sl_far` | **True** — SL qua mép xa ± 1 + 0,3 | "vùng được bảo vệ tới khi bị phá": hỗ trợ mới chỉ hỏng khi giá đóng qua **cả vùng** — đúng luật đổi vai của VCL. Hệ quả: vùng rộng > ~2,7 giá thường bị trần SL 4 giá loại (báo số, mục 3.3). Bản SL qua cạnh gần là độ nhạy S2. |
| `rank` | **7** (thấp nhất, sau mọi loại v4) | hoà khoảng cách cùng nến ⇒ vùng v4 thắng, A-v4 bị chen ít nhất |
| thứ tự `zi` | mọi vùng v4 trước (đúng thứ tự `build_zones('new')`), rồi VCL theo **eid tăng dần** | khoá phụ khi hoà (dist, rank, zi) — giữ nguyên khoá sắp xếp của v4 |

### 2.4 Luật CÚ PHÁ THẬT (chỉ áp cho vùng VCL — luật cấu trúc, không có số mới)

Trong `open_state` (mở trạng thái khi M5 đóng ngoài, chiều `out`), sau vòng lùi tìm chân cú phá của nhánh `dyn` (dừng ở nến `k`, `lim = max(đầu phiên, i − 60)`):
mở trạng thái **chỉ khi** tại nến `k` vùng **có giá trị** (eid có trong bộ ở `k`) **và** giá đóng ở phía trong: `out = +1 ⇒ C[k] ≤ hi[k]`; `out = −1 ⇒ C[k] ≥ lo[k]`.
Ba ca trượt: vòng dừng vì vùng vắng ở `k` (vùng sinh ra trong/sau cú phá) · vòng chạy hết 60 nến mà giá vẫn ngoài · đầu phiên. Ca trượt ⇒ **không mở**, đếm `vcl_khong_pha_that`;
`need_in` (Q9) không đổi. Mọi thứ khác của `open_state` (L, cực trị, armed, brk_no) giữ nguyên.

**Vì sao chỉ VCL, không áp cho vùng v4:** máy v4 mở trạng thái bất cứ khi nào M5 đóng ngoài vùng, kể cả khi giá **chưa từng ở phía trong** (vd giá nằm dưới VAH_D cả buổi ⇒ mở trạng thái
"phá xuống" và vào BÁN khi giá chạm VAH từ dưới — đó là bật khỏi kháng cự, không phải phá-hồi). Với vùng v4 (mức cố định, ít vùng) đó là đặc điểm đã báo của v4, người học bảo giữ.
Nhưng bộ hiển thị VCL **luôn có 2 vùng ngay trên và 2 vùng ngay dưới giá** ⇒ không có luật này thì mọi vùng VCL gần giá đều mở trạng thái ở mỗi nến M5 và A-v5 thành
"chạm vùng là vào theo vai" (đã đo: ≈ vùng dời, BENZO-VCL 3.2). Ý người học là "**phá xong đổi vai**" ⇒ phải có cú phá thật. Bản không có luật này là độ nhạy S1 (in, không chọn).

### 2.5 Vùng rời bộ

- Tại nến quét i, eid vắng ⇒ E = NaN ⇒ không vào lệnh, không cập nhật armed (đúng hành vi code v4 khi E là NaN; **kiểm bằng test**).
- Tại nến M5 kế tiếp, eid vắng ⇒ trạng thái kết thúc lý do **`roi_bo`** (tách khỏi `reset_value` trong phễu). Không giữ biên cuối, không nối sang eid mới chồng chỗ:
  vùng không còn vẽ trên chart thì người học không canh được.
- Báo: số trạng thái **đã trang bị** bị hủy vì `roi_bo`, và trong đó bao nhiêu có eid mới chồng lên dải cũ trong ≤ 5 nến (LAN-CHAM đã thấy 36 % vùng mới chồng lên vùng vừa rời bộ).
  Nếu > 30 % trạng thái đã trang bị chết vì `roi_bo` ⇒ ghi rủi ro "mất lệnh vì đổi mã", đề xuất vòng sau khoá theo mức giá — **không** tự sửa vòng này.

### 2.6 Đổi vai

Không thêm luật. Vai = chiều phá: phá lên qua vùng (kháng cự cũ) ⇒ trạng thái `S = +1` ⇒ chờ hồi về `hi` để MUA (vùng đóng vai hỗ trợ). Nếu sau đó M5 đóng xuống dưới `lo`
⇒ trạng thái `+1` bị hủy (hủy sâu / phía đối diện) và cùng nến M5 đó mở `(eid, −1)` nếu qua luật 2.4 (nến trước chân phá xuống phải đóng ≥ `lo` — thường đúng vì giá vừa ở trên).
Không dùng cột `side` của `rec` để quyết định gì; chỉ in mô tả (mục 3.3).

### 2.7 Chống trùng với vùng v4 — giữ riêng + 3 lớp

Giữ **máy trạng thái riêng** cho từng eid; **không gộp** vào vùng v4 (gộp sẽ đổi trạng thái của vùng v4 ⇒ A-v4 không còn nguyên). Ba lớp chặn đếm hai lần:
1. **Cùng nến:** luật sẵn có của v4 — chọn |C − E| nhỏ nhất, hoà ⇒ hạng (VCL = 7 thua mọi vùng v4) ⇒ zi.
2. **Một lệnh mở cùng lúc** (`kernel.simulate(one_at_a_time=True)`, như v4).
3. **Khoá mức giá — CHỈ cho tín hiệu VCL:** tín hiệu VCL ở nến i, chiều S, cạnh E bị bỏ nếu trong cùng (phiên, S) **đã có ≥ 2 tín hiệu đã ghi** (bất kỳ vùng nào, v4 hay VCL)
   có |E_cũ − E| ≤ `ZONE_HALF`. Đếm `vcl_khoa_muc`. Tín hiệu v4 **không** xét khoá này (để A-v4 không đổi) ⇒ một mức vẫn có thể > 2 lệnh/phiên khi v4 vào sau VCL — báo số ca.

**Nhãn "trùng"** (chỉ mô tả, không lọc): tín hiệu VCL là **trùng** nếu tại nến vào có ít nhất một vùng v4 (6 loại, có giá trị tại i, VWAP đã qua Warm) mà dải `[lo, hi]` của nó
giao `[lo_VCL − 1, hi_VCL + 1]`; ghi kèm loại vùng v4 trùng (nhiều thì liệt kê). Không trùng ⇒ **VCL-riêng**.

### 2.8 Đếm tham số

Tham số tự do **mới = 0**. Luật mới đều là luật cấu trúc không có số: cú phá thật (2.4, dùng lại `LEG_LOOKBACK` 60), rời bộ ⇒ hủy (2.5), khoá mức (2.7, dùng lại `ZONE_HALF` và trần 2).
Slot còn dư (≤ 1) **không dùng** — mọi tham số thêm đều là chỗ để chọn sau khi thấy số.

### 2.9 Cài đặt (gợi ý bắt buộc về kết quả, tự do về cách)

- File mới `research/setup_a_v5.py`: **copy** `detect` của v4 thành `detect5` rồi thêm đúng 4 thứ: vùng thưa (sparse) VCL, luật 2.4, lý do `roi_bo`, khoá mức 2.7 (+ nhãn trùng).
  Không import-rồi-vá `setup_a_v4.detect`.
- **Vùng thưa:** không tạo mảng dày 86 333 nến cho ~4 300 eid (≈ 6 GB). Lưu theo eid: nến đầu + mảng lo/hi trên đoạn sống; truy cập `LO[zi][i]` trả NaN ngoài đoạn.
  Ở sự kiện M5 chỉ lặp **các vùng có giá trị tại i ∪ các vùng đang có trạng thái** — tương đương vòng lặp đầy đủ vì vùng NaN không có trạng thái thì code v4 không làm gì (`continue`).
  Chứng minh bằng test (3.6 mục 3).
- Dời bản đồ (ĐC3): cộng δ của phiên vào lo/hi VCL y như vùng v4 (`shift[P.sno]`).

---

## 3. BACKTEST (Sonnet, Python)

### 3.0 Điều kiện tiên quyết — dừng và báo nếu lệch
1. `setup_a_pha_hoi.detect(expire=30)` (qua máy v4) ⇒ **n = 20, WR 10,0 %, R −0,68** (A cũ).
2. `detect5` **với tập VCL rỗng** ⇒ **đúng từng lệnh** của `setup_a_v4.detect` cấu hình (d): **n = 218, WR 19,7 %, R −0,30**, TRAIN 119 / TEST 99 (test).
3. `detect5` với VCL, phiên 2026-09-08 và 2026-10-02: kết quả vòng lặp thưa == vòng lặp dày (test).

### 3.1 Công suất thống kê — in TRƯỚC bảng chính
Như v4 mục 3: hiệu nhỏ nhất phát hiện được ≈ 2,8 × σ_R × √(1/n₁ + 1/n₂) cho: A-v5 so 0 · A-v5 so A-v4 · **lệnh VCL so lệnh vùng v4 trong A-v5** · riêng TEST so đối chứng.
Câu bắt buộc: "chênh nhỏ hơn các số này không phân biệt được với may rủi trên 90 ngày".

### 3.2 BẢNG CHÍNH — một bảng ngắn (TP 3R, sau phí, 1 lệnh mở, không chặn 19:20–20:30)

| bản | số lệnh (tổng · /ngày) | WR | R TB sau phí [KTC 95 %] |
|---|---|---|---|
| A cũ (V3 gốc) | 20 · 0,33 | 10,0 % | −0,68 [−1,09; −0,09] |
| A-v4 | 218 · 3,57 | 19,7 % | −0,30 [−0,50; −0,07] |
| **A-v5 (A-v4 + vùng VCL)** | … | … | … |

Ngay dưới bảng, đúng 3–4 dòng:
1. Lệnh VCL thêm: +k lệnh (+x/ngày), WR …, R …; lệnh A-v4 bị chen mất: m.
2. Đối chứng A-v5 (ĐC1 / ĐC2 / ĐC3): **hơn / không hơn / n quá nhỏ** từng cái.
3. Đối chứng riêng lệnh VCL (ĐC1-VCL / ĐC2-VCL / ĐC3-chỉ-dời-VCL): hơn / không hơn / n quá nhỏ.
4. T1/T2: đạt / không (nêu điều kiện trượt).

KTC 95 % = bootstrap 10 000 lần hạt 0 (ghi: đánh giá thấp vì lệnh cùng phiên không độc lập).

### 3.3 Chi tiết (cho hồ sơ, sau bảng chính)
1. **Phân rã số lệnh:** n(A-v5) = n(A-v4) − mất + v4 mới xuất hiện + VCL. "Mất" tách: bị lệnh VCL đang mở chặn · thua tranh cùng nến (VCL gần hơn). "v4 mới" = tín hiệu v4 trước bị
   lệnh v4 khác chặn nay được vào. Số tín hiệu thô trước luật 1 lệnh mở của từng phần.
2. **Lệnh VCL: VCL-riêng vs trùng** — n, /ngày, WR, R [KTC], TRAIN n/R, TEST n/R; trùng tách theo loại vùng v4 trùng (loại nào n < 10 thì gộp "khác").
3. **A-v5, lệnh vùng v4, lệnh VCL** × TRAIN / TEST / T8 / T9 / T10 / pha Á–Âu–Mỹ / khung 18:00–19:20 / khung 19:20–20:30 / bản CÓ chặn 19:20–20:30. Cột như bảng 4 của RESULTS-A-V4.
4. **Phễu VCL:** số lần M5 đóng ngoài vùng VCL · bị luật cú phá thật chặn (theo 3 ca trượt) · mở · mở mới / mở lại (Q9) · đã trang bị · hủy sâu · hủy phía đối diện · `roi_bo`
   (và `roi_bo` khi đã trang bị, có eid mới chồng ≤ 5 nến) · hết hạn · có CF · bị trần SL loại · bị khoá mức · thua tranh cùng nến · thành lệnh.
5. **Mô tả lệnh VCL (chỉ mô tả, không lọc; nhóm n < 10 không bình):** bề rộng vùng 2–2,5 / 2,5–3,5 / 3,5–5 giá (kèm số tín hiệu bị trần SL loại theo từng nhóm) · slot của vùng
   ở nến `k` (K = giá ở trong vùng rồi phá / N–F = giá xuyên từ phía kia sang) · vùng chỉ số tròn (`d10`) hay có mốc khác · `brk_no` 1 / ≥ 2 · khoảng cách cực trị 2–3 / 3–5 / > 5.
6. **Ví dụ để soi chart:** 5 lệnh VCL thắng + 5 thua (cách đều theo thời gian; giờ VN và UTC, eid, lo–hi, E, cực trị, nến đà, nến hồi, L, pbmax, vào/SL/TP, trùng/riêng)
   + 2 ảnh phiên (`_plot_run.py`/hàm vẽ v4; thêm dải VCL tím nhạt) lưu `report/img/a_v5_*.png`. Ghi rõ ảnh là minh hoạ, không phải ca điển hình.
7. Rủi ro số kiểm (mục 5): tỉ lệ `roi_bo`, số mức > 2 lệnh/phiên/chiều, tỉ lệ lệnh VCL trùng.

### 3.4 Đối chứng (ngưỡng NGUYÊN `PLAN-LAN-CHAM.md` mục 5)
**Cho A-v5 (toàn bộ):** ĐC1, ĐC2, ĐC3 **y hệt v4** (`ctrl1/ctrl2/ctrl3` — copy sang file mới nếu cần đổi), với ztype `'VCL'` thêm vào tầng (strata) của ĐC1; ĐC3 dời **cả** vùng v4 lẫn VCL cùng δ.
**Cho riêng lệnh VCL** (đây là câu "thêm vùng VCL có đáng không"):
- **ĐC1-VCL:** hồ = nến trong trạng thái VCL đã trang bị, chưa quá T_HOI, chạm E, hợp lệ; bỏ nhịp hồi/CF. Mỗi lệnh VCL thật rút 1 nến cùng chiều, cùng TRAIN/TEST; 200 lần.
- **ĐC2-VCL:** `control_sample` với hai cột theo nến: cột MUA = `hi` của vùng VCL trong bộ có `hi` gần giá đóng nhất; cột BÁN = `lo` gần nhất (vùng VCL tồn tại ngắn, cột theo
  từng eid quá thưa để rút). Cùng chế độ kernel, cùng chiều, tol 1,0; 200 lần.
- **ĐC3-chỉ-dời-VCL:** dời **chỉ** bản đồ VCL (cùng ma trận δ hạt 20261024), vùng v4 để nguyên; chạy nguyên máy A-v5; so R TB lệnh VCL thật với R TB lệnh VCL trên bản dời
  (+ số lệnh VCL/ngày trên bản dời).

Ngưỡng "khác": thật ngoài dải 5–95 % đối chứng ở **cả TRAIN và TEST**, cùng dấu, cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số ở cả hai; thiếu một ⇒ "≈ đối chứng".
Chỉ áp dụng khi nhóm có ≥ 10 lệnh ở **cả** TRAIN và TEST, không thì "không áp dụng (n nhỏ)". Tổng **6 phép so có phán quyết** ⇒ ghi: với ~5 % mỗi phép, ~0,3 ô "khác" có thể do ngẫu nhiên.
Ghi chữ cho báo cáo người học: "khác ▲" = **hơn**, "khác ▼" = **kém hơn**, "≈" = **không hơn**, "không áp dụng" = **n quá nhỏ**.

### 3.5 Độ nhạy — đổi MỘT thứ một lần, IN RA, KHÔNG chọn lại
S1 bỏ luật cú phá thật (máy v4 nguyên xi trên VCL) · S2 SL vùng VCL qua cạnh gần (`sl_far=False`, SL = E ∓ 1 + 0,3) · S3 bỏ khoá mức 2.7 · S4 TP 2R ·
S5 chỉ vùng VCL **không** trùng vùng v4 (bỏ hẳn tín hiệu VCL trùng trước luật 1 lệnh mở). Mỗi dòng: n, /ngày, WR, R [KTC], TRAIN n/R, TEST n/R, và số lệnh VCL.

### 3.6 Kiểm không nhìn trước + test (`research/test_setup_a_v5.py`, phải xanh trước khi chạy kết quả)
1. Tái tạo 3.0 (1)(2)(3).
2. **Cắt dữ liệu:** ≥ 5 vị trí cắt i (giữa phiên; ngay sau 19:00 VN; ngay sau đổi tuần; giữa một nhịp hồi của trạng thái VCL; ngay sau nến M5 phá một vùng VCL):
   `detect5(P[:i+1], rec[bar ≤ i])` cho **đúng** các lệnh idx ≤ i của bản đầy đủ. (Bộ VCL tại nến i đã được chứng minh không nhìn trước bởi `test_lan_cham.py` — chạy lại test đó, không viết lại.)
3. Ca tổng hợp (dữ liệu giả hoặc cắt): vùng VCL giá ở trong rồi M5 đóng trên ⇒ mở; vùng sinh ra ngay trong chân cú phá ⇒ không mở; giá ở dưới vùng 60 nến rồi M5 đóng dưới
   ⇒ không mở (khác vùng v4: mở); eid vắng ở nến quét ⇒ không vào; eid vắng ở M5 ⇒ hủy `roi_bo`; phá lên E = hi, SL qua lo − 1 − 0,3; vùng rộng 4 giá ⇒ trần SL loại;
   phá lên rồi M5 đóng dưới lo ⇒ hủy `+1` và mở `−1` cùng nến; VCL và VWAP_D cùng nến cùng khoảng cách ⇒ VWAP_D được chọn; mức đã có 2 tín hiệu ⇒ tín hiệu VCL thứ 3 bị khoá,
   tín hiệu v4 thứ 3 vẫn vào; khoá đếm theo `VCL_<eid>`.
4. Hằng số + test commit **trước** lần chạy kết quả đầu tiên (lịch sử git là bằng chứng không chọn sau).

### 3.7 DỰ ĐOÁN ĐĂNG KÝ TRƯỚC (Opus, trước khi có số)
- **Số lệnh tăng rõ:** A-v5 ≈ **300–450 lệnh (≈ 5–7,5/ngày)**, tức VCL thêm khoảng +80 đến +230 (sau khi trừ lệnh A-v4 bị chen). Phễu: ~5 100 cú phá thật, đổi ra lệnh ở tỉ lệ
  thấp hơn v4 (trang bị khó hơn vì phải đi ≥ 2 giá từ mép, trần SL loại vùng rộng).
- **WR không tăng:** A-v5 **17–22 %** (A-v4 19,7 %); R TB **−0,20 đến −0,45**; lệnh VCL và lệnh vùng v4 chênh nhau nhỏ hơn mức phát hiện được.
- **Đối chứng:** cả 6 phép so **≈** (không hơn). ĐC3-chỉ-dời-VCL cho số lệnh VCL/ngày gần bằng thật.
- **T1 không đạt:** muốn R TEST A-v5 ≥ −0,08 khi lệnh v4 giữ −0,52 trên 99 lệnh TEST, ~100 lệnh VCL ở TEST phải có R TB ≈ **+0,36R** — trái với mọi phép đo vùng VCL trước.
- Dự đoán sai theo hướng tốt (vd lệnh VCL R > 0 ở cả TRAIN và TEST) ⇒ **vẫn** chỉ là ứng viên kiểm lại trên dữ liệu mới, không phải lợi thế, trừ khi đạt T2.

---

## 4. TIÊU CHÍ "ĐÁNG PORT C#" (đăng ký trước)

A-v4 đã **không đạt T1** (trượt điều kiện 2: R TEST −0,52 < −0,08). A-v5 được đánh giá **lại từ đầu** bằng cùng T1/T2 của v4, cộng hai điều kiện riêng cho phần VCL:

- **T1-v5 (port để chạy thử thời gian thực = forward test)** — đồng thời:
  (1) n(A-v5) ≥ 40 · (2) **R TB TEST(A-v5) ≥ −0,08 và n TEST ≥ 15** (mốc A cũ, như v4) · (3) R TB TRAIN(A-v5) ≥ −0,30 · (4) không đối chứng nào (6 phép) ra "thật **kém hơn**" ·
  (5) test 3.6 xanh, tái tạo 3.0 đúng · (6) khung 18:00–19:20 không âm hơn phần còn lại quá 0,5R (n ≥ 10) ·
  **(7) phần VCL có ích về số lệnh:** VCL thêm ròng ≥ +0,5 lệnh/ngày (≥ +31 lệnh trên 61 phiên) · **(8) phần VCL không kéo tụt:** R TB lệnh VCL ≥ R TB lệnh vùng v4 trong A-v5
  trừ hiệu nhỏ nhất phát hiện được của phép so đó (mục 3.1), ở **cả** TRAIN và TEST.
  Điều kiện (2) là điều kiện A-v4 trượt; muốn qua, phần VCL phải dương rõ ở TEST (mục 3.7) ⇒ khả năng thấp, nói thẳng trong báo cáo.
- **T2 — được viết "có lợi thế đo được":** TRAIN > 0 và TEST > 0, n TEST ≥ 30, vượt **cả ba** đối chứng của A-v5 theo ngưỡng 3.4. Không đạt ⇒ câu bắt buộc
  "**chưa có lợi thế đo được** trên 61 phiên".
- **Port C# làm sau, chỉ khi người học xác nhận** (người học chưa yêu cầu port). Kể cả đạt T1, Sonnet **không** đụng C# vòng này; chỉ ghi vào báo cáo "đủ điều kiện đề xuất port".
  Phác thảo để vòng sau ước công: Benzo phải chạy kèm `VclCore` (engine VCL C# đã có) để lấy bộ hiển thị từng nến; `DetectorA` thêm vùng thưa theo eid + luật 2.4/2.5/2.7;
  parity theo `PARITY.md` (thêm cột eid, state, armed); cần parity VCL Python ↔ C# đã có (`PARITY-VCL.md`) còn đúng trên file 90d.

---

## 5. RỦI RO / CHỖ MƠ HỒ — QUYẾT ĐỊNH MẶC ĐỊNH (Sonnet làm theo, báo lại số từng mục)

1. **Kết quả ≈ đối chứng (khả năng cao nhất).** Nói thẳng: vùng VCL thêm lệnh chứ không thêm chất lượng; không được viết "vùng hỗ trợ/kháng cự giúp A tốt hơn".
2. **Thêm lệnh âm = lỗ nhanh hơn.** Nếu R TB A-v5 < 0, báo cáo người học phải có câu: "số lệnh tăng nhưng mỗi lệnh vẫn lỗ trung bình ⇒ tổng lỗ tăng theo số lệnh".
3. **Trần SL 4 giá loại vùng rộng** (sl_far). Mặc định: giữ, báo số tín hiệu bị loại theo bề rộng; S2 cho thấy cái giá của lựa chọn này. Không đổi bản chính theo S2.
4. **Đổi mã vùng (eid) làm chết trạng thái** (`roi_bo`). Mặc định: hủy, báo tỉ lệ (2.5). Không nối mã vòng này.
5. **Vùng VCL hay chồng lên vùng v4** ⇒ nhãn trùng, khoá mức. Mức > 2 lệnh/phiên/chiều do tín hiệu v4 đến sau: chấp nhận, báo số ca.
6. **VCL chen mất lệnh A-v4** (1 lệnh mở). Mặc định: chấp nhận (đó là chi phí thật của việc canh thêm vùng khi chỉ được 1 lệnh), báo trong phân rã 3.3(1).
7. **Hai trạng thái cùng một cú giá trên hai vùng VCL kề nhau** (dải kề, cú phá xuyên cả hai): giữ cả hai trạng thái; cùng nến ⇒ luật gần nhất; khác nến ⇒ 1 lệnh mở + khoá mức xử lý.
8. **Vùng VCL vắt qua phiên:** trạng thái reset hết phiên như v4; luật 2.4 tìm chân cú phá chỉ trong phiên (`lim` ≥ đầu phiên).
9. **Q9 "mở lại sau hết hạn" với VCL:** áp như v4 nhưng vẫn phải qua luật 2.4 (nến trong ≤ 60 nến trước). Tách lệnh mở lại trong mô tả.
10. **Vùng VCL bị dời (ĐC3) có thể không còn "bao quanh giá"** như bộ thật — đó chính là điều đối chứng muốn kiểm; không chỉnh.
11. **Thời gian chạy:** vùng thưa + 100 bản dời × 2 (ĐC3 toàn, ĐC3-chỉ-VCL). Mục tiêu ≤ 20 phút. Quá ⇒ giảm còn 50 bản, ghi rõ.
12. **Lệch chuỗi nến cache VCL ↔ P.df** ⇒ dừng, không "căn chỉnh" tay.
13. **Ca máy trạng thái không phủ** (ngoài các ca trên) ⇒ dừng và báo, không tự chế.

---

## 6. BÁO CÁO CUỐI CHO NGƯỜI HỌC (Sonnet, `report/_eval_a_v5.txt` + tin nhắn cuối)

Đúng **một bảng** như mục 3.2 (3 hàng: A cũ · A-v4 · A-v5; cột: số lệnh tổng và /ngày · WR · R TB sau phí) + **tối đa 5 dòng**, tiếng Việt, không từ lạ:
1. Vùng VCL thêm bao nhiêu lệnh (+k, +x/ngày) và WR/R của riêng lệnh thêm.
2. **Đối chứng: hơn / không hơn / n quá nhỏ** (A-v5 và riêng lệnh VCL, mỗi cái một chữ).
3. Port: đạt / không đạt T1 (điều kiện trượt) — "port C# chỉ làm khi anh xác nhận".
4. Câu bắt buộc nếu R < 0: số lệnh tăng nhưng tổng lỗ tăng theo.
5. Dự đoán của Opus đúng/sai ở điểm nào.

Không viết "có xu hướng", không chọn ô độ nhạy đẹp, không gộp TP 2R vào kết luận.

---

## 7. Giao nộp + thứ tự commit (commit + push mỗi bước, message tiếng Việt)

1. `research/zones_a_v5.py` (nạp + kiểm khớp + vùng thưa VCL) · `research/setup_a_v5.py` (hằng số, `detect5`, đối chứng, báo cáo) · `research/test_setup_a_v5.py` — **test xanh, commit TRƯỚC khi chạy kết quả.**
2. Chạy ⇒ `report/RESULTS-A-V5.md` (bảng chính đầu tiên, chi tiết sau), `report/_eval_a_v5.txt`, `report/img/a_v5_*.png` — commit kết quả.
3. Không sửa C#, không sửa file v4/VCL/kernel. Báo hash + kết quả push.
