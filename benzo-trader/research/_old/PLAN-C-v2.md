# PLAN C-v2 — Setup C "Fade cạnh" mở rộng: cổng hình dạng D/P/b + VA nhỏ từ 3 lần đổi hành vi (CHoCH)

Tác giả: Fable (kiến trúc sư, chỉ thiết kế). Ngày: 2026-10-22. Người thực hiện: Opus. Dữ liệu duy nhất: `D90 = data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d` (61 phiên sạch, TRAIN ≤ 2026-09-15 = 35 phiên, TEST từ 09-16 = 26 phiên). KHÔNG chạy file 2 năm.

Thuật ngữ: **buy / sell / limit / market** giữ tiếng Anh. "Đổi hành vi" = CHoCH (Change of Character). "Nến cao trào" = climax. "Nhịp bật tự động" = AR (automatic rally). "Nhịp thử lại" = ST (secondary test). "Hợp lưu N vùng", không "cluster".

---

## 0. Mốc so sánh và mục tiêu thật

Số C hiện tại trên D90, ô khởi điểm (xuyên 2 tick, rộng ≥ 6, `report/RESULTS-C.round1.md`):

| | n | lệnh/ngày | WR | R TB | tổng R |
|---|---|---|---|---|---|
| TP cạnh/POC ≥ 2R | 103 | 1,69 | 12,6% | −0,43 | −44,7 |
| TP cố định 2R | 121 | 1,98 | 27,3% | −0,26 | −31 |
| riêng A/EU (fade VA hôm qua), TP poc | 63 | 1,03 | 9,5% | −0,49 | −31 |
| riêng US (VA Âu/IB), TP poc | 40 | 0,66 | 17,5% | −0,34 | −13,8 |

Kết luận vòng 1–3: C **tắt mặc định**, chưa biến thể nào dương ở cả TRAIN lẫn TEST. Hoà vốn sau phí ở TP 2R ≈ 36% WR.

**Yêu cầu người dùng:** tăng số lệnh, WR không giảm. **Nói thẳng một câu:** ở WR 12–27% hiện tại, tăng lệnh = tăng lỗ; nên tiêu chí thật của plan này là **R TB không âm hơn C0 và tiến về ≥ 0**, số lệnh chỉ là chỉ số phụ. Phần 1 (cổng hình dạng) là bộ **LỌC** → giảm lệnh A/EU, kỳ vọng tăng WR. Phần 2 (VA nhỏ CHoCH) là **NGUỒN VÙNG MỚI** → tăng lệnh. Gộp lại mới có cơ hội "nhiều lệnh hơn, WR cao hơn". Phải tách đóng góp từng phần (mục 3).

---

## 1. Research CHoCH — nguồn, đối chiếu, chốt định nghĩa

### 1.1 Từ internet
- **LuxAlgo, khái niệm BOS/CHoCH** ([luxalgo.com/library/indicator/v2IhxlWK…](https://www.luxalgo.com/library/indicator/v2IhxlWK-market-structures-zigzag-choch-bos-mss-msb), [JGSQx5tt](https://www.luxalgo.com/library/indicator/JGSQx5tt-market-structure-bos-choch/), [yhK46cdb](https://www.luxalgo.com/library/indicator/yhK46cdb-market-structures-smc-bos-choch-major-minor/)): BOS = phá cấu trúc **cùng chiều** xu hướng (tiếp diễn); CHoCH = phá cấu trúc **ngược chiều** xu hướng (cảnh báo đảo). "Cùng cơ chế, ngược thông điệp". Quy ước râu/đóng cửa **không thống nhất**: nhiều script LuxAlgo cho CHoCH kích hoạt bằng **râu** xuyên đỉnh/đáy swing, BOS cần **đóng cửa**; script khác cho chọn. Đỉnh/đáy swing lấy bằng **pivot cửa sổ đối xứng** (pivot period / swing sensitivity), tín hiệu **trễ đúng bằng period** đó.
- **Công thức pivot chuẩn** ([prorealcode Market Structure Algo](https://www.prorealcode.com/prorealtime-indicators/market-structure-algo/)): đỉnh swing = nến có high cao nhất trong cửa sổ 2·prd+1, **chỉ được xác nhận sau prd nến** đóng.
- **Script SMC TradingView** ([hY8stoih](https://vn.tradingview.com/script/hY8stoih-Smart-Money-Concept-Change-of-Character-Break-of-Structure)): cùng định nghĩa; tác giả nói CHoCH là **xác nhận**, không phải tín hiệu vào lệnh đứng một mình.
- **Wyckoff Phase A** ([LuxAlgo Wyckoff accumulation schematic](https://www.luxalgo.com/library/concept/wyckoff-accumulation-schematic/), [Wyckoff Schematics PDF](https://www.prorealcode.com/wp-content/uploads/2019/11/WyckoffSchematics-VisualTemplatesForMarketTimingDecisions.pdf)): SC (cao trào bán: biên độ rộng, volume lớn, **đóng cửa cách xa đáy**) → AR (bật tự động vì lực bán cạn + short covering, đỉnh AR = **biên trên** range) → ST (thử lại vùng SC, volume thấp hơn, biên độ hẹp hơn; **có thể nhiều ST**). Đáy SC/ST + đỉnh AR = **biên range ban đầu**.

### 1.2 Của trader (nguyên ý)
Giá lao mạnh (100→50); nến tại đáy volume rất lớn (selling climax) **bị chặn**; quán tính hồi (75) do chốt lời hoặc **buy limit** cản; seller đẩy xuống (55) lại bị chặn, lại lên… Đủ **3 lần đổi hành vi** mới thành VA (50–75). VA này nhỏ hơn VA của TPO nhưng cũng làm cú move bị chặn rồi đi ngang. Sau đó **chờ fade cạnh** tại hai biên; **có thể nới rộng** khi thêm đợt thử.

### 1.3 Suy luận của tôi (đối chiếu)
- Mô tả của trader **chính là Wyckoff Phase A**: climax (50) = SC, hồi 75 = AR, xuống 55 bị chặn = ST, lên lại = xác nhận ST. "3 lần đổi hành vi" = **3 điểm xoay (pivot) được xác nhận liên tiếp sau cao trào**: đáy L1 (climax) → đỉnh H1 (AR) → đáy L2 (ST). VA nhỏ = [min(L1, L2), H1].
- Khác CHoCH kiểu SMC: SMC đếm **một** cú phá swing ngược xu hướng; trader đếm **ba** lần đổi hướng — nghiêm hơn, và không cần "phá" gì cả, chỉ cần giá **không đi tiếp**. Vì thế tôi **không** dùng định nghĩa "phá đỉnh swing ngược xu hướng" của SMC làm lõi; chỉ mượn **cách xác nhận pivot có trễ** (cửa sổ/ngưỡng) để không nhìn trước.
- Repo đã có đúng máy này: `quantower-entry-signal/research/wyckoff/v8/wyckoff/wyckoff_schematic.py` (Python, đã chấm 49 range qua 7 vòng) và port C# trong `WyckoffRunner.cs` (ArIdx/ArPrice/StExt, biên phụ = nới rộng). **Không có** mã CHoCH nào trong indicator VWAP (EntrySignal/RunnerSignal chỉ có "quay đầu tại VWAP" bằng râu + VSA) — người dùng nhớ nhầm hoặc nhớ WyckoffRunner; cần xác nhận lại 1 câu. Tái dùng **hằng số đã đo** của schematic: `MOVE_MIN_EFF 0.35`, `AR_RETRACE_MULT 0.5`, `STA_MIN_AR_FRAC 0.55`, `CLIMAX_EXT_BARS 8`, `VSA_CLIMAX 2.2`, `SHOCK_DEPTH_FRAC 0.15`.
- Xác nhận pivot: dùng **`kernel.zigzag`** (ngưỡng 2,0 giá, trả `confirm_pos`, reset theo phiên) thay vì pivot cửa sổ đối xứng — cùng tính chất "trễ, không nhìn trước", đã có test và đã port C# (`BenzoZones.Pivots`, DetectorD dùng). Không thêm cách tìm pivot thứ hai vào dự án.

### 1.4 Định nghĩa chốt (MỘT, tất định, chỉ dùng thông tin tới nến i) — xem máy trạng thái mục 2.2.

---

## 2. Đặc tả số học

Ký hiệu chung: `u(i)` = trung vi biên độ 50 nến (`kernel.median_range`), `vma(i)` = SMA volume 20 nến gồm nến i, `TICK 0,1`, hàng profile 0,2 giá. Mọi hằng số dưới đây **khai báo trước, commit trước lần chạy đầu**, kèm lưới độ nhạy nhỏ (≤ 2 giá trị thay thế / tham số).

### 2.1 (a) Hình dạng profile TPO hôm qua + vùng dày

**Nguồn profile.** Kernel chỉ có profile **volume**; phải dựng profile **TPO** trong `zones_c_v6.py` từ nến M1 của phiên hôm qua `q` (phiên "yday" mà `kernel._zones` đã chọn: ≥ 300 nến, không dính chỗ nối):
- Bracket = 30 phút UTC (`t_utc.floor('30min')`), cùng phiên. Mỗi bracket có [min low, max high] của các M1 trong nó.
- TPO(hàng r) = số bracket có khoảng [low, high] phủ hàng r (hàng 0,2 giá, `rint(price/0.2)`). Đây chính là `ProfileEngine.TpoRows` chạy trên nến M30 — khớp cách Optimus Flow vẽ, và **chính xác** (hợp của M1 = biên độ bracket).
- POC_T, VAH_T, VAL_T = `kernel.value_area(rows, tpo_count)` (70%, luật 2 hàng). Range [L, H] = min low / max high phiên. Phiên hôm qua của kernel = ngày Globex (05:00 VN → 04:00 VN), **trùng với neo chart TPO người học đang nhìn** (Bài số 0 chưa sửa — ghi rủi ro R1).
- Độ nhạy khai báo trước: (S1) dùng profile volume per-level thay TPO (cùng công thức).

**Vùng dày (bulge).** `T = [t_lo, t_hi] = zones_a_v4.peak_sharpness(rows, tpo_count, POC_T, frac=0.5)` không kẹp: từ hàng POC nới lên/xuống chừng nào hàng kề còn ≥ 50% TPO của POC. Độ nhạy: frac 0,4 / 0,6.

**Phân loại** (tính trên range R = H − L > 0):
- `bulge = (t_hi − t_lo) / R` ; `asym = ((t_lo − L) − (H − t_hi)) / R` ∈ [−1, 1] (dương = đuôi dưới dài = bulge nằm trên).
- Hai đỉnh: `find_hvn(rows, tpo_count)` cho ≥ 2 đỉnh VÀ giữa chúng có hàng `find_lvn` ≤ 0,5 trung bình ⇒ **B** (hai vòm).
- `close_in`: giá đóng phiên q nằm trong [VAL_T, VAH_T] (luật "chốt sổ bằng giá đóng", Syllabus Buổi 2 §2.3).

| nhãn | điều kiện (xét theo thứ tự) | vùng fade A/EU | nguồn luật |
|---|---|---|---|
| **KHÁC-B** | hai đỉnh | không fade | Syllabus 2.1 (DD khó lường) |
| **KHÁC-thin** | `bulge < 0.20` | không fade | Syllabus 2.1 (trend: chưa xong ở đâu) |
| **KHÁC-close** | `close_in == False` | không fade | Syllabus 2.3 |
| **D** | `|asym| ≤ 0.25` | **VA_Y** (VAH_T/VAL_T) — giống C0 nhưng chỉ ở ngày D | trader (1), Syllabus 2.1 |
| **P** | `asym > 0.25` | **T** (t_lo, t_hi) — cạnh của phần dày | trader (1): "phần TPO dày" |
| **b** | `asym < −0.25` | **T** | gương P |

Ngưỡng 0,20 và 0,25 là **2 tham số tự do mới**; độ nhạy: asym 0,20 / 0,30; bulge 0,15 / 0,25. Độ rộng tối thiểu giữ **6 giá** (như C0) — vùng T có thể hẹp hơn VA nên lần đầu min_width thực sự có tác dụng; báo phân bố rộng T và số lệnh bị chặn vì < 6.
POC cho TP ở ngày P/b = POC_T (nằm trong T theo định nghĩa) ⇒ TP thường là cạnh đối diện của T.

**Bắt buộc báo TRƯỚC khi xem lệnh:** bảng đếm nhãn trên 61 phiên (D / P / b / KHÁC-*), kèm 1 ảnh profile TPO mỗi nhãn (người học kiểm bằng mắt trên Optimus Flow — bài săn bằng chứng mức ĐẾM: người học gắn nhãn 15 phiên bằng mắt TRƯỚC, so với máy; lệch = một bên hiểu sai định nghĩa).

### 2.2 (b) Máy trạng thái VA-nhỏ CHoCH (mỗi phiên, hai chiều độc lập; mô tả chiều "climax bán" = đáy; chiều đỉnh là gương)

Trạng thái: `NGỦ → ỨNG_VIÊN (có climax) → CHỜ_AR → CHỜ_ST → SỐNG (có VA_C) → CHẾT`. Chỉ dùng nến ≤ i; mọi pivot lấy từ `kernel.zigzag(df, 2.0, by_session=True)` và chỉ được dùng từ `confirm_pos` trở đi.

1. **Move mạnh** (điều kiện cần để nhận climax tại nến c): chân move = pivot H gần nhất đã xác nhận trước c (hoặc high lớn nhất 240 nến nếu chưa có pivot); `len = high(chân) − low(c)`; yêu cầu `len ≥ 6·u(c)` và hiệu suất `len / Σ|close_k − close_{k−1}| ≥ 0.35` (MOVE_MIN_EFF, tái dùng). `max_pullback` = nhịp hồi lớn nhất trong lòng move (như `_find_move` v6).
2. **Nến climax**: `low(c)` = thấp nhất của move; `volume(c) ≥ 2.2 · vma(c)` (VSA_CLIMAX tái dùng; độ nhạy 1.8) HOẶC `range(c) ≥ 1.4 · TB range 20 nến` (CLIMAX_RANGE_MULT tái dùng). Trong 8 nến sau (CLIMAX_EXT_BARS) có đáy thấp hơn thoả cùng điều kiện ⇒ **dời climax** sang đó (cao trào là một cụm).
3. **Bị chặn**: `close(c) ≥ low(c) + 0.4·range(c)` HOẶC nến c+1 đóng trên `(high(c)+low(c))/2`. Độ nhạy: bỏ điều kiện này (chỉ cần AR). Không gate delta (bài học dự án: gate delta làm tệ); chỉ ghi delta(c) để báo cáo.
4. **Đổi hành vi #1 — AR**: pivot L1 = đáy zigzag tại cụm climax được xác nhận (giá đã lên ≥ 2 giá) ⇒ đếm 1. Sau đó pivot H1 (đỉnh zigzag) được xác nhận ⇒ **đổi hành vi #2**, với ràng buộc `H1 − L1 ≥ max(2.0, 0.5·max_pullback)` (AR_RETRACE_MULT tái dùng) — nhịp bật phải lớn hơn mọi nhịp hồi trong move (nguyên lý CHoCH "hồi không đủ lớn so với bối cảnh" mà giảng viên Wyckoff đã bác). Không thoả ⇒ về NGỦ (giữ climax làm ứng viên tới khi giá phá `low(L1) − 1,0·u` hoặc 300 nến).
5. **Đổi hành vi #3 — ST**: pivot L2 được xác nhận, với `L2 ≥ L1 − 1.0·u` (được thủng nhẹ) và `L2 ≤ H1 − 0.55·(H1 − L1)` (STA_MIN_AR_FRAC: phải quay về ≥ 55% đường tới climax, không "treo giữa"). Thủng sâu hơn 1,0·u ⇒ climax thất bại: về NGỦ, nến tạo L2 thành ứng viên climax mới nếu thoả bước 2. Chưa đủ 55% ⇒ chờ pivot L tiếp theo (tối đa 400 nến từ H1).
6. **SINH VA_C** tại nến `birth = confirm_pos(L2)`: `lo = min(L1, L2)`, `hi = H1`, `src = 'CHOCH_DN'`, `height = hi − lo`. Fade được từ nến `birth + 1`. Điều kiện sống: `height ≥ 6` (min_width C0; độ nhạy 4).
7. **Nới rộng**: pivot mới (đã xác nhận) vượt cạnh một đoạn `0 < d ≤ 0.25·height` ⇒ cạnh := giá pivot, `height` tính lại, đánh dấu `n_ext += 1`. `d > 0.25·height` ⇒ CHẾT (biên bị phá thật). Độ nhạy 0,15 (SHOCK_DEPTH_FRAC) / không nới.
8. **Chế độ cân bằng & chết**: chạy `kernel.mode_frame` trên band (lo, hi) này (cột `eu_vah/eu_val` của một zcols riêng, mẹo đã dùng trong `prepare()`): fade chỉ khi `BALANCE`; `TREND_*` ⇒ CHẾT; `BREAK_*` ⇒ tạm không fade (như C0). Hết phiên ⇒ CHẾT (zigzag reset theo phiên). Không có hạn tuổi theo thời gian ở bản chính; độ nhạy: 240 nến không chạm cạnh ⇒ CHẾT.
9. **Đồng thời**: tối đa 1 VA_C sống mỗi chiều gốc (DN/UP); VA_C mới (từ climax khác) thay VA_C cũ cùng chiều. Hai VA_C (DN và UP) chồng nhau ⇒ dùng cái sinh sau.
10. **Nhật ký** mỗi VA_C: phiên, nến climax, VSA, delta climax, L1/H1/L2, birth, height, n_ext, lý do chết, số lần chạm cạnh, số lệnh. Đây là đầu ra cho bài săn bằng chứng (người học tìm 5 ca trên Optimus Flow TRƯỚC khi xem log máy).

Tham số tự do **mới** của máy: `6·u` (move), `0.4` (bị chặn), `1.0·u` (thủng), `0.25` (nới) — 4 cái; còn lại tái dùng hằng số đã đo của schematic/kernel. Lưới độ nhạy ghi ở từng bước, chạy **đủ lưới và in đủ**, không chọn ô đẹp.

### 2.3 (c) Cắm vào `detect()` của C

Không sửa `kernel.py`, không sửa `setup_c_fade_canh.py`. Module mới `setup_c_v6.py` tái dùng `setup_c_fade_canh.detect()` nguyên xi bằng cách **đổi đầu vào** (cách `prepare()` đã làm): detect chỉ đọc `mode['band_hi'/'band_lo'/'band_src'/'mode']`, `zones['eu_poc']`, `df`. Vậy mỗi **nguồn vùng = một "lớp" (layer)** gồm (zcols riêng → `m5_bars` → `mode_frame`) rồi gọi `detect()` một lần cho lớp đó:

| lớp | band theo nến (A/EU) | band (US) | POC cho TP | nhãn zone |
|---|---|---|---|---|
| L0 = C0 | VA_Y | VA Âu / IB | yd_poc / eu_poc | như cũ (tái tạo đúng từng lệnh — test) |
| L1 D-gate | VA_Y **chỉ ngày D**, NaN ngày khác | như L0 | yd_poc | `VAH_Y_D/VAL_Y_D` |
| L2 D + P/b | ngày D: VA_Y; ngày P/b: T; khác: NaN | như L0 | POC_T | `..._D`, `T_HI_P/T_LO_P`, `T_HI_B/T_LO_B` |
| L3 CHoCH | VA_C khi sống (mọi pha A/EU/US) | VA_C | **cạnh đối diện** (không POC; độ nhạy fixed2) | `CHOCH_DN_HI/LO`, `CHOCH_UP_HI/LO` |

Gộp (C4) = L2 ∪ L3: nối danh sách entry, `kernel.simulate(one_at_a_time=True)` theo thứ tự thời gian; cùng nến hai lớp cùng bắn ⇒ lấy lớp có cạnh **gần giá đóng hơn**, hoà ⇒ L3 (vùng mới sinh gần thời điểm hơn). Đếm "≤ 2 lệnh/(phiên, cạnh)" giữ nguyên trong detect từng lớp; với VA_C đã nới thì cạnh đổi giá ⇒ khoá đếm đổi — chấp nhận, ghi rõ.
Độ rộng tối thiểu: giữ 6 giá cho cả ba lớp (bản chính); 4 giá chỉ là độ nhạy cho L2/L3. Xuyên 2 tick, delta cùng chiều, loại nến dài nhất phiên, râu ngược ≤ thân, trừ 18:00–19:20 VN: **giữ nguyên** để so sánh được với C0. Báo thêm bản chặn 19:20–20:30 (luật cứng C# `InVirtualOpen`).
`band_src` cho mode_frame hiện chỉ 'va_eu'/'ib'/'' — với lớp mới, đặt cột eu_* = band ⇒ src 'va_eu'; nhãn zone thật ghi riêng trong `detect(... )` qua tham số mới `zone_name` (thêm 1 tham số tuỳ chọn vào bản copy của detect trong setup_c_v6, KHÔNG sửa file cũ).

---

## 3. Thiết kế backtest

### 3.1 Ô đo (mỗi ô chạy cả TP 'poc' và 'fixed2'; chỉ TP poc là bản chính như C0)

| ô | nội dung | câu hỏi trả lời |
|---|---|---|
| C0 | tái tạo round 1 (n 103 / −0,43; fixed2 121 / −0,26) | mốc, test parity |
| C1 | L1 D-gate + US cũ | cổng D có nâng WR A/EU không, mất bao nhiêu lệnh |
| C2 | L2 (D + P/b dày) + US cũ | vùng dày P/b có cho lệnh tốt hơn VA_Y không |
| C3 | L3 CHoCH đứng một mình | nguồn vùng mới có lợi thế riêng không |
| C4 | L2 ∪ L3 | bản gộp — "nhiều lệnh hơn, WR cao hơn?" |
| C0-nhãn | C0 tách theo nhãn hình dạng của ngày (D / P / b / KHÁC) | **kiểm cổng không cần chạy lệnh mới**: WR(D) > WR(KHÁC)? |
| C3-tách | C3 theo chiều gốc (DN/UP) × cạnh fade (phía climax / phía AR) × pha | trader kỳ vọng fade cả hai cạnh — đo xem cạnh nào |

Chỉ số mỗi ô: n, lệnh/ngày (÷61), WR, R TB + KTC bootstrap 95% (10.000, hạt 0), kỳ vọng giá/lệnh, tổng R, chuỗi thua, TRAIN/TEST, theo pha, theo tháng. Bảng **tách đóng góp**: Δ(C1−C0) = D-gate; Δ(C2−C1) = P/b; Δ(C3) = CHoCH; Δ(C4−C2−C3) = tương tác (trùng nến / 1 lệnh mở).

### 3.2 Đối chứng (bắt buộc cho từng nguồn, hạt cố định 20261024, cùng ma trận với A-v4/VCL)
- **ĐC-a dời vùng** ±3–15 giá, 100 bản: dời cả band của lớp (VA_Y/T/VA_C) theo δ ~ U[3,15] dấu ngẫu nhiên theo (phiên, bản), chạy lại nguyên máy (mode + detect). Nếu vùng thật không khác dải 5–95% của bản dời ⇒ vị trí vùng không mang thông tin (đúng kết luận VCL/HVN trước đây).
- **ĐC-b vào ngẫu nhiên tại vùng**: `kernel.control_sample` 200 lần, mỗi lệnh thật 1 nến cùng vùng/chế độ/chiều/R:R. Vùng mới cần tên→cột: thêm cột `t_hi/t_lo/choch_hi/choch_lo` vào zcols của lớp và `K.ZONE_NAME2COL.update({...})` **tại runtime trong setup_c_v6** (không sửa file kernel).
- **ĐC-c khớp khoảng cách / thời gian**:
  - cho cổng hình dạng: **hoán vị nhãn** D/P/b/KHÁC giữa 61 phiên 1.000 lần, phân phối của WR(ngày D) và R TB(ngày D) ⇒ p của nhãn thật. Đây là phép thử chính của phần 1 vì không cần thêm lệnh nào.
  - cho VA_C: **"VA giả"** cùng chiều cao, cùng tuổi thọ, cùng phiên nhưng **dời thời gian sinh** ngẫu nhiên trong phiên (100 bản) ⇒ cấu trúc 3 lần đổi hành vi có hơn một dải bất kỳ cùng cỡ không. Thêm: đối chứng khớp khoảng cách kiểu VCL (P(chạm cạnh đối diện) theo khoảng cách) cho lệnh C3.
- Ngưỡng "khác đối chứng": nguyên `PLAN-LAN-CHAM.md` mục 5 (ngoài dải 5–95% ở cả TRAIN và TEST, cùng dấu, |hiệu| > 2 sai số; chỉ áp khi ≥ 10 lệnh mỗi nửa, không thì ghi "không áp dụng").

### 3.3 Công suất thống kê — in TRƯỚC bảng chính
σ_R ≈ 1,6 (đo ở A-v4). Hiệu nhỏ nhất phát hiện được (80%, 5%): n=30 ⇒ ~0,8R; n=60 ⇒ ~0,58R; n=100 ⇒ ~0,45R. **Kết luận trước:** với 61 phiên, phần 1 (A/EU còn ~20–30 lệnh sau cổng) **gần như không thể chứng minh**; chỉ có thể nói "không tệ hơn" và "hướng đúng/sai". Viết câu này vào đầu report.

### 3.4 Tiêu chí (khai báo trước)
- **T0 — giữ hướng, đáng chạy tiếp:** C4 có n ≥ 1,3·n(C0) **và** R TB(C4) ≥ R TB(C0) ở CẢ TRAIN và TEST **và** WR(C4) ≥ WR(C0) − 3 điểm; không đối chứng nào nói "thật kém hơn".
- **T1 — đáng port để ghi log live (vẫn tắt mặc định):** T0 + C3 riêng có TRAIN ≥ −0,10 và TEST ≥ 0, n TEST ≥ 15; vượt ĐC-b hoặc ĐC-c ở ≥ 1 nửa; hoán vị nhãn cho p ≤ 0,10 cho cổng D.
- **T2 — lợi thế đo được (mới được nói "có"):** TRAIN > 0 và TEST > 0, n TEST ≥ 30, vượt cả ba đối chứng theo ngưỡng 3.2.
- Không đạt T0 ⇒ **ghi "không", C vẫn tắt**, không mở thêm vòng tinh chỉnh tham số trên cùng dữ liệu.

### 3.5 Chống tự lừa khi n nhỏ
- Mọi hằng số (2.1, 2.2) commit TRƯỚC lần chạy đầu (như A-v4 commit `4e76f63`); report in lại hash đó.
- Lưới độ nhạy chỉ các giá trị đã liệt kê; in **đủ** lưới; không chọn ô theo TEST; không thêm tham số sau khi xem số.
- Bảng đếm nhãn hình dạng và nhật ký VA_C in TRƯỚC bảng lệnh (kiểm bằng mắt trước khi tin số).
- "Chỗ tự quyết" (plan không nói rõ) ghi thành mục riêng trong report, như A-v4 Q1–Q11.
- Người học chấm 5 ca VA_C + 15 nhãn hình dạng bằng mắt **trước** khi đọc kết quả lệnh (`tpo/EVIDENCE-DRILLS.md`); lệch máy↔mắt phải được giải thích trước khi diễn giải lệnh.

---

## 4. Việc cho Opus (thứ tự)

1. **`research/zones_c_v6.py`** (mới, chỉ import kernel + zones_a_v4):
   - `tpo_profile(df, sno) -> (rows, cnt, L, H, close)`; `classify_shape(rows, cnt, L, H, close, asym_thr=0.25, bulge_thr=0.20, frac=0.5) -> dict(label, poc, vah, val, t_lo, t_hi, asym, bulge)`; `shape_by_session(df, ctx) -> {sno: dict cho phiên q = yday}`.
   - `choch_va(df, u, vma, params) -> DataFrame theo nến: choch_lo, choch_hi, choch_src, choch_id, n_ext` + `log` (list dict mỗi VA_C). Máy trạng thái mục 2.2, thuần vòng lặp, không nhìn trước.
   - `layer_zcols(df, zc, kind, shapes|choch) -> zcols` (bản sao zc với eu_vah/eu_val/eu_poc thay bằng band của lớp; ib NaN cho lớp mới) và `zone_table()` để test cắt dữ liệu.
2. **`research/setup_c_v6.py`**: copy `detect()` của setup_c_fade_canh + tham số `zone_name`; `prepare()` dùng lại của file cũ; `run_layer()`, `merge()`, các ô 3.1, đối chứng 3.2, công suất 3.3, tiêu chí 3.4 → `report/RESULTS-C-V6.md` + `report/img/c_v6_*.png` (1 ảnh/nhãn hình dạng + 5 VA_C đầu tiên TRAIN + 5 TEST). Hằng số đăng ký trước ở đầu file.
3. **`research/test_setup_c_v6.py`** (pytest):
   - `test_reproduce_c0`: L0 ra đúng từng lệnh `setup_c_fade_canh.run(P, pen_ticks=2, min_width=6, tp_mode='poc')` (n 103, −0,43) và fixed2.
   - `test_tpo_profile_exact`: profile TPO từ M1 = từ bracket 30' dựng tay trên phiên tổng hợp.
   - `test_classify_shapes`: 4 profile tổng hợp D / P / b / thin / B ra đúng nhãn; T đối xứng khi profile đối xứng; close ngoài VA ⇒ KHÁC-close.
   - `test_choch_birth`: chuỗi tổng hợp 100→50 (climax volume 3×)→75→55→65… sinh VA_C = [50, 75] đúng tại `confirm_pos(L2)`, không sớm hơn.
   - `test_choch_fail_deep_undercut`: ST thủng > 1,0·u ⇒ không sinh; nến thủng thành ứng viên mới.
   - `test_choch_extend_and_die`: pivot vượt 0,2·height ⇒ nới; vượt 0,3·height ⇒ chết; TREND ⇒ chết; hết phiên ⇒ chết.
   - `test_no_lookahead_cut`: với mọi k trong một lưới, chạy trên `df[:k]` cho nhãn/band/VA_C y hệt bản đầy đủ tới nến k (mẫu `test_setup_a_v4.test_no_lookahead_cut`).
   - `test_min_width_blocks`: T hẹp < 6 ⇒ 0 lệnh ở lớp đó.
4. Chạy, viết đánh giá tay `RESULTS-C-V6.danhgia.md` theo đúng T0/T1/T2; commit + push mỗi mốc (hằng số → kết quả → đánh giá).
5. **Chỉ khi đạt T1**: port C# — `BenzoZones`: thêm `TpoShape` (dựng từ nến M30 của phiên trước qua `ProfileEngine.TpoRows` + `ValueArea` + `PeakSharpness(frac 0.5)`) và `ChochTracker` (dùng `Pivots` sẵn có); `DetectorC`: chọn band theo lớp + nhãn zone; `tests/Program.cs`: replay parity theo cơ chế `report/PARITY.md` (cột `_replay_cs.csv`), khớp 100% lệnh với Python. Build `build.sh`, test, commit, push — không hỏi.

---

## 5. Rủi ro / điểm chưa chắc

- **R1 Neo phiên.** Hình dạng tính trên ngày Globex (05:00 VN) vì kernel và chart người học đều neo vậy; nếu sau Bài số 0 chart chuyển neo pit 19:20, nhãn sẽ đổi. Khai báo độ nhạy: profile chỉ cửa sổ Mỹ 19:00–04:00.
- **R2 n quá nhỏ.** Ngày D có thể chỉ ~20–30/61 phiên ⇒ A/EU còn ~20 lệnh; mọi kết luận phần 1 là "hướng", không phải "kiểm định". Đã khai báo ở 3.3.
- **R3 Baseline âm sâu.** C0 −0,43R; kể cả +0,3R cải thiện vẫn âm. Phải sẵn sàng kết luận "có hướng đúng nhưng chưa dùng được".
- **R4 Climax theo volume ở pha Á.** vma 20 nến ở phiên Á thấp ⇒ ngưỡng 2,2× dễ thoả bởi nến tầm thường; vì thế bước 2 kèm điều kiện cực trị của move và bước 4 kèm AR tương đối. Báo số VA_C theo pha.
- **R5 Zigzag 2,0 giá cố định** (kernel) quyết định "đổi hành vi"; biên độ vàng đổi theo tháng. Không thêm tham số; chỉ ghi nhận hạn chế, độ nhạy không mở.
- **R6 "Indicator VWAP có CHoCH"** không tồn tại trong repo; nếu người dùng muốn nói WyckoffRunner thì định nghĩa ở 2.2 đã bám đúng hằng số của nó. Cần người dùng xác nhận 1 câu trước khi Opus chạy.
- **R7 Vùng dày P/b hẹp** ⇒ nhiều lệnh bị min_width 6 hoặc TP < 2R loại; có thể P/b gần như không cho lệnh — đó là kết quả hợp lệ, không hạ ngưỡng để "có lệnh".
- **R8 Trùng lặp với setup D (bẫy)** và CBR WyckoffRunner: VA_C sinh ngay sau climax — nơi D và runner cũng hoạt động; khi gộp vào Benzo sau này phải tính 1 lệnh mở chung, chưa xét ở plan này.
