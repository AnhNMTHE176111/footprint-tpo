# PLAN — Vùng kháng cự / hỗ trợ MẠNH cho SessionZones

> Fable viết spec + đo (2026-11-25). Opus implement. Số liệu: [`research/vung_manh_2026-11-25/DO-VUNG-MANH.md`](research/vung_manh_2026-11-25/DO-VUNG-MANH.md).
> Bản tham chiếu Python (nguồn sự thật khi spec và code lệch nhau): [`research/vung_manh_2026-11-25/vung_manh.py`](research/vung_manh_2026-11-25/vung_manh.py) + [`vm.py`](research/vung_manh_2026-11-25/vm.py).

## 0. Phải đọc trước khi code

**Vùng này CHƯA có lợi thế đo được.** Trên 589 phiên GC (2024-08 → 2026-11), vùng đúng định nghĩa dưới đây cho kết quả ngang vùng dời ngẫu nhiên: thắng 1:1 48,8 % / 47,2 % (TRAIN / TEST) so với đối chứng 47,9 % / 47,5 %. Vùng vàng chỉ có 60 lần quay lại trong 2,3 năm — chưa kết luận được. Giống kết luận cũ ở `vung-canh-lenh/research/report/HOP-LUU-SZ.md`.

Hệ quả bắt buộc:
- Mô tả indicator, tooltip input, tin Telegram **không được** viết "vùng đảo chiều", "xác suất cao", "đã kiểm chứng". Dùng "vùng va đập nhiều + hợp lưu" và ghi "chưa kiểm định".
- Không sinh signal vào lệnh từ vùng này (CLAUDE.md mục 3).
- Thông số mặc định chọn theo mật độ trên chart và độ rộng giao dịch được, không phải vì "tối ưu".

## 1. Yêu cầu người dùng → cách hiểu đã chốt

| Yêu cầu | Chốt trong spec |
|---|---|
| Va đập nhiều, đúng nghĩa kháng cự/hỗ trợ | ≥ 3 đỉnh/đáy cục bộ M30 (mỗi cái bật lại ≥ 1 U) nằm trong một cụm rộng ≤ 0,30 U, trong 5 phiên đã đóng + phiên đang chạy |
| Hợp lưu ≥ 1 mức, không dùng profile hôm nay | 12 mức, tất cả từ phiên/tuần **đã đóng**; riêng HVN tuần được lấy thêm từ tuần này tính tới **hết hôm qua** |
| HVN đã đấu giá xong, lớn và đều, chữ D, giá đã rời xa | đỉnh ≥ 2,5 × trung bình; profile nguồn hình chữ D; sau khi profile chốt giá từng cách đỉnh ≥ 2 U |
| Xanh = hỗ trợ dưới giá, đỏ = kháng cự trên giá, có chữ | theo phía giá hiện tại; nhãn ghi số lần va đập + tên các mức |
| ≥ 3 mức và có HVN → vàng | ≥ 3 **nhóm** mức (mục 4.6) trong đó có nhóm HVN |
| Độ rộng vừa đủ | khoảng các điểm va đập + 0,05 U mỗi mép, tối thiểu 0,20 U (trung vị 0,36 U ≈ 4,8 giá khi U = 13,4) |
| Không đổi khi đổi khung chart | chỉ dùng history M30 (`_hd30`) + PriceLevels của nến M30; chỉ tính lại khi có nến M30 mới |

Đơn vị dùng suốt file: **U = biên độ (High − Low) trung bình của nến M30 trong 5 phiên đã đóng gần nhất** (mục 4.2). Năm 2026 U trung vị 13,4 giá.

## 2. Kiến trúc

- Thêm `public static class StrongZones` vào `ProfileEngine.cs` (namespace `TpoSuite`), **chỉ nhận mảng thuần** để test được không cần Quantower:
  - `IList<DateTime> t, IList<double> o, h, l, c` — nến M30 theo thứ tự thời gian, giờ UTC (`TimeLeft`);
  - `Func<int, IEnumerable<KeyValuePair<double, double>>> levelsOf` — giá → khối lượng của nến thứ i (từ `VolumeAnalysisData.PriceLevels`, giá thô theo tick, **chưa** snap);
  - `double tick`, `double rowStep` (= tick × RowTicks = 0,2), `double nowPrice`, `StrongZoneParams p`.
- `SessionZones.cs` chỉ làm 3 việc: đổi `_hd30` thành mảng, gọi `StrongZones.Compute`, vẽ.
- **Nến cuối của history luôn coi là nến đang chạy.** Gọi j = chỉ số nến M30 đã đóng cuối cùng = `n − 2`. Mọi tính toán cấu trúc chỉ dùng nến `0..j`. Nến `j + 1` chỉ dùng để biết (a) "hôm nay" là phiên nào, (b) giá hiện tại.
- **Bộ đệm:** kết quả cấu trúc (điểm va đập, cụm, mức, vùng) khoá theo `(n, TimeLeft của nến j)`; chỉ tính lại khi khoá đổi. Mỗi tick chỉ chạy lại bước hiển thị (mục 4.8) với `nowPrice` mới. `Process()` hiện chạy mỗi `OnUpdate` — đừng để phần này chạy lại theo tick.
- History: giữ 45 ngày như hiện tại (cần tối đa ~13 phiên + trọn tuần trước).

## 3. Thông số (input mới, nhóm "Vùng mạnh")

| Input (tên hiển thị) | Thuộc tính | Mặc định | Range / bước | Ghi chú |
|---|---|---|---|---|
| Hiện vùng mạnh (va đập + hợp lưu) | `ShowStrongZones` | true | — | |
| Vùng mạnh · Số lần va đập tối thiểu | `SzMinTouches` | 3 | 2–6 / 1 | 2 thì chart rối gấp đôi |
| Vùng mạnh · Bật lại tối thiểu (×biên độ M30) | `SzBounceU` | 1,0 | 0,5–3,0 / 0,25 | R |
| Vùng mạnh · Số phiên nhìn lại | `SzLookbackDays` | 5 | 2–15 / 1 | phiên đã đóng, cộng phiên đang chạy |
| Vùng mạnh · Bề rộng cụm tối đa (×biên độ M30) | `SzClusterU` | 0,30 | 0,15–0,60 / 0,05 | WC |
| Vùng mạnh · Dung sai hợp lưu (×biên độ M30) | `SzConfluenceTolU` | 0,10 | 0–0,30 / 0,05 | TOL |
| Vùng mạnh · Số nhóm mức hợp lưu tối thiểu | `SzMinConfluence` | 1 | 0–3 / 1 | 0 = vẽ cả cụm không hợp lưu (để kiểm tra) |
| Vùng mạnh · HVN chỉ nhận profile hình chữ D | `SzHvnDOnly` | true | — | tắt thì vùng vàng nhiều gấp ~3 |
| Vùng mạnh · HVN phải từng rời xa (×biên độ M30) | `SzHvnAwayU` | 2,0 | 0–6 / 0,5 | 0 = bỏ điều kiện |
| Vùng mạnh · Gộp VAH/VAL với VWAP ±1σ cùng kỳ thành một nhóm | `SzGroupEdges` | true | — | xem 4.6 — **cần người dùng chốt** |
| Vùng mạnh · Bán kính hiển thị (×biên độ M30) | `SzRadiusU` | 4,0 | 1–12 / 0,5 | tính từ mép gần của vùng |
| Vùng mạnh · Số vùng tối đa mỗi phía | `SzMaxPerSide` | 3 | 1–6 / 1 | |
| Màu vùng rất mạnh (vàng) | `StrongGoldColor` | `#FFD600` | — | xanh/đỏ dùng `SupColor`/`ResColor` sẵn có |

Hằng số không cần input (đặt trong `StrongZoneParams` với giá trị mặc định): K = 2, M = 6, PAD = 0,05, WMIN = 0,20, HVN_DAYS = 5, HVN_RATIO = 2,5, HVN_TOP = 3, D_POC_LO = 0,30, D_POC_HI = 0,70, D_VA_MAX = 0,60, GOLD_MIN = 3, SEP = 0,15, MIN_DAY_BARS = 20, UNIT_DAYS = 5, MIN_WEEK_BARS = 60.

## 4. Thuật toán

### 4.1 Ranh giới phiên, tuần, chỗ nối (dùng lại hàm có sẵn, bản mảng thuần)

- **Phiên (ngày CME):** nến mới cách nến trước > 75 phút ⇒ phiên mới (`GroupByGap`, GapMinutes = 75).
- **Tuần:** cách > 30 giờ ⇒ tuần mới (`WeekSpans`, WeekGapHours = 30).
- **Chỗ nối hợp đồng:** khoảng nghỉ 30–150 phút và `|open[i] − close[i−1]| ≥ 20 giá` (`LastSpliceIndex`). `seg(i)` = số chỗ nối có chỉ số ≤ i. Hai nến khác `seg` nằm trên hai thang giá khác nhau.
- **Hôm nay** = phiên chứa nến `j + 1`; d = chỉ số phiên đó; `a0` = nến đầu của hôm nay.

### 4.2 Đơn vị U của một phiên

`U(k)` = trung bình `(h − l)` của **mọi** nến M30 từ nến đầu phiên `max(0, k − 5)` tới nến cuối phiên `k − 1`. Cần `k − max(0, k − 5) ≥ 2`, thiếu thì `U(k)` không xác định (không có điểm va đập, không có vùng). Không cần cắt ở chỗ nối (chỉ dùng High − Low). `u = U(d)` là đơn vị của hôm nay.

### 4.3 Điểm va đập (trên nến M30 đã đóng)

Với mỗi nến i (`i ≥ 6`), lấy `ui = U(phiên chứa nến i)`; bỏ qua nếu `ui` không xác định hoặc `seg(i − 6) ≠ seg(i)`.

**Đỉnh va đập** tại i nếu đủ cả ba:
1. `h[i] > max(h[i−2], h[i−1])` (lớn hơn hẳn) và `h[i] ≥ max(h[i+1], h[i+2])`;
2. đi tới: `h[i] − min(l[i−6 .. i]) ≥ R × ui` (cửa sổ gồm cả nến i);
3. bật lại: duyệt `q = i+1 .. i+6`; gặp `h[q] > h[i]` hoặc `seg(q) ≠ seg(i)` thì dừng (không thành); gặp `h[i] − l[q] ≥ R × ui` thì thành.

Nến xác nhận `conf = max(i + 2, q)`. Giá điểm = `h[i]`, loại = đỉnh.

**Đáy va đập** đối xứng: `l[i] < min(l[i−2], l[i−1])`, `l[i] ≤ min(l[i+1], l[i+2])`; đi tới `max(h[i−6 .. i]) − l[i] ≥ R × ui`; bật lại: dừng khi `l[q] < l[i]`, thành khi `h[q] − l[i] ≥ R × ui`. Một nến có thể vừa là đỉnh vừa là đáy.

Điểm chỉ được dùng khi `conf ≤ j` (không vẽ lại lùi). Kiểm tra điều kiện 1 theo đúng thứ tự trên; điều kiện 3 kiểm `h[q] > h[i]` **trước** khi kiểm bật lại trong cùng nến q.

### 4.4 Gom cụm

- Tập điểm đang dùng: `conf ≤ j`, `i ≥` nến đầu của phiên `max(0, d − LB)`, và `seg(i) = seg(j + 1)`.
- Sắp tăng dần theo giá (thứ tự giữa các điểm cùng giá không ảnh hưởng kết quả).
- `wc = WC × u`. Lặp tới khi hết điểm: với mỗi điểm còn lại p đếm số điểm còn lại có giá trong `[p, p + wc + 1e-9]`; chọn p có số đếm lớn nhất (hoà → p giá thấp nhất); nhóm đó thành một cụm, bỏ ra khỏi tập.
- Giữ cụm có số điểm `n ≥ NMIN`.

### 4.5 Biên vùng

```
lo = pmin − PAD × u ; hi = pmax + PAD × u            (pmin, pmax = giá thấp/cao nhất trong cụm)
nếu hi − lo < WMIN × u:  mid = (pmin + pmax) / 2 ; lo = mid − WMIN × u / 2 ; hi = mid + WMIN × u / 2
lo = floor(lo / tick + 1e-6) × tick ; hi = ceil(hi / tick − 1e-6) × tick        (nới ra mép tick)
```

Mức hợp lưu **không** kéo giãn biên vùng — biên chỉ do các điểm giá đã thật sự quay đầu quyết định.

### 4.6 Mức hợp lưu của hôm nay (tính một lần mỗi phiên, cố định suốt phiên)

Profile dùng hai dạng:
- **theo tick** (giá thô): cho VWAP và σ. `VWAP = Σ p·v / Σ v`; `σ = sqrt(Σ v·(p − VWAP)² / Σ v)` trên **từng mức giá** của mọi nến trong kỳ. (Không dùng `VwapAt` kiểu giá điển hình: lệch trung vị 0,2 giá, và không có σ.)
- **theo hàng** rowStep: `RowsOver` như cũ → `ValueArea` (70 %, luật 2 hàng), `FindHvn` (tham số mặc định), `PeakSharpness` (90 %, khối lượng thô).

`poc_pos = (POC − hàng thấp nhất) / (hàng cao nhất − hàng thấp nhất)`; `va_frac = (VAH − VAL) / (hàng cao nhất − hàng thấp nhất)`. **Hình chữ D** ⇔ `0,30 ≤ poc_pos ≤ 0,70` và `va_frac ≤ 0,60` (47 % số phiên đạt).

HVN của một profile: lấy 3 đỉnh đầu của `FindHvn` (mạnh trước), giữ đỉnh có tỉ lệ ≥ 2,5; dải = `PeakSharpness(rows, đỉnh, rowStep, 0.90)`; ghi kèm `peak`, `end` (nến cuối của profile nguồn), `dshape` của profile nguồn.

| Tên trong code | Nhãn | Nguồn | Nhóm |
|---|---|---|---|
| `vwap_d` | VWAP hôm qua | VWAP của hôm qua | giữa ngày |
| `vwap_d_tren` | VWAP hôm qua +1σ | VWAP + σ | trên ngày |
| `vah_d` | VAH hôm qua | ValueArea hôm qua | trên ngày |
| `vwap_d_duoi` | VWAP hôm qua −1σ | VWAP − σ | dưới ngày |
| `val_d` | VAL hôm qua | ValueArea hôm qua | dưới ngày |
| `hvn_d` | HVN ngày | HVN của từng phiên trong 5 phiên đã đóng gần nhất | HVN ngày |
| `vwap_w` | VWAP tuần trước | VWAP tuần trước | giữa tuần |
| `vwap_w_tren` | VWAP tuần trước +1σ | | trên tuần |
| `vah_w` | VAH tuần trước | ValueArea tuần trước | trên tuần |
| `vwap_w_duoi` | VWAP tuần trước −1σ | | dưới tuần |
| `val_w` | VAL tuần trước | | dưới tuần |
| `hvn_w` | HVN tuần | HVN của tuần trước **và** của tuần này tính tới hết hôm qua | HVN tuần |

Chi tiết nguồn:
- **Hôm qua** = phiên đã đóng gần nhất trước d có ≥ 20 nến M30 (bỏ qua phiên lễ ngắn). Nếu nến đầu của nó khác `seg` với `a0` ⇒ không có 5 mức ngày.
- **HVN ngày:** lùi từ phiên `d − 1`; gặp phiên khác `seg` với `a0` thì dừng hẳn; phiên < 20 nến bỏ qua không đếm; lấy đủ 5 phiên.
- **Tuần trước** = tuần ngay trước tuần chứa `a0`; nến đầu = `max(nến đầu tuần đó, chỗ nối gần nhất ≤ a0)`; cần ≥ 60 nến, thiếu thì không có 5 mức tuần và không có HVN tuần trước.
- **Tuần này tới hết hôm qua:** từ `max(nến đầu tuần này, chỗ nối gần nhất ≤ a0)` tới `a0 − 1`; cần ≥ 60 nến (tức từ khoảng thứ Tư). Chỉ sinh HVN.

**Nhóm** (để đếm hợp lưu): VAH và VWAP +1σ của cùng một kỳ gần như trùng nhau do cấu tạo (vùng giá trị 70 % ≈ ±1σ), đếm thành hai thì "≥ 3 mức có HVN" chỉ còn nghĩa "HVN cạnh VAH". Nên khi `SzGroupEdges = true` có 8 nhóm như cột cuối. Khi `false`: mỗi tên là một nhóm riêng (12 nhóm) — đúng cách đếm theo chữ của người dùng. Trong 3 tuần của fixture: có ít nhất một cụm vàng ở 6 % số nến khi gộp, 19 % khi không gộp.

### 4.7 Hợp lưu, vàng

Với mỗi vùng `[lo, hi]` và mỗi mức `[L.lo, L.hi]` (mức điểm thì lo = hi):
- trùng ⇔ `L.lo ≤ hi + TOL × u` và `L.hi ≥ lo − TOL × u`;
- nếu là HVN thì còn phải **đủ điều kiện tại nến j**: (`SzHvnDOnly` tắt hoặc `dshape`) và, với `a = end + 1`, `a ≤ j` và `max( max(h[a..j]) − peak , peak − min(l[a..j]) ) ≥ HVN_AWAY × u`.
- `names` = các tên trùng, không lặp, theo thứ tự cố định: `hvn_w, hvn_d, vah_w, val_w, vwap_w, vwap_w_tren, vwap_w_duoi, vah_d, val_d, vwap_d, vwap_d_tren, vwap_d_duoi`.
- `ngroup` = số nhóm khác nhau; `hvn` = có `hvn_d` hoặc `hvn_w`; **`gold` ⇔ `ngroup ≥ 3` và `hvn`**.

### 4.8 Hiển thị (chạy lại mỗi khi giá đổi; rẻ)

1. Giữ vùng có `ngroup ≥ SzMinConfluence`.
2. **Vùng sát/chồng nhau:** sắp theo (vàng trước, `ngroup` giảm, `n` giảm, điểm va đập mới nhất trước, `lo` tăng). Duyệt lần lượt, giữ vùng nếu với mọi vùng đã giữ k: `max(lo, k.lo) − min(hi, k.hi) ≥ SEP × u`. (Một vùng giằng co 10–15 giá hay bị chia thành 3–4 cụm liền kề; chỉ vẽ cụm mạnh nhất.)
3. **Phía:** `nowPrice > hi` ⇒ hỗ trợ (+1), khoảng cách = `nowPrice − hi`; `nowPrice < lo` ⇒ kháng cự (−1), khoảng cách = `lo − nowPrice`; **giá đang trong vùng** ⇒ khoảng cách 0, phía = lùi từ nến j về trước (tối đa 400 nến) tới nến đầu tiên có `close > hi` (⇒ +1) hoặc `close < lo` (⇒ −1); không tìm thấy ⇒ 0.
4. Bỏ vùng có khoảng cách > `SzRadiusU × u`.
5. **Trần:** vùng chứa giá luôn vẽ. Mỗi phía: sắp (vàng trước, gần trước), lấy `SzMaxPerSide` vùng.
6. **Màu:** vàng nếu `gold`; không thì xanh (`SupColor`) cho +1, đỏ (`ResColor`) cho −1, xám cho 0.
7. **Nhãn:** `"{đầu} · {n} lần · {tên các mức nối bằng ' + '}"`, thêm `" (giá đang trong vùng)"` khi giá trong vùng.
   - `đầu` = `Hỗ trợ` / `Kháng cự` / `Vùng`; vùng vàng: `★ Hỗ trợ rất mạnh` / `★ Kháng cự rất mạnh`.
   - Ví dụ: `Kháng cự · 5 lần · HVN tuần + VWAP tuần trước`; `★ Kháng cự rất mạnh · 3 lần · HVN ngày + VAL tuần trước + VWAP hôm qua`.
   - Không có mức nào (chỉ khi `SzMinConfluence = 0`): `Hỗ trợ · 4 lần`.

### 4.9 Vẽ

- Mỗi vùng: hình chữ nhật `[lo, hi]` kéo hết bề ngang cửa sổ, tô màu alpha 40 (vàng: alpha 70), viền 1 px cùng màu alpha 160; nhãn sát mép phải, trong dải (dải mỏng hơn chữ thì đặt ngay trên dải), kèm khoảng cách tới giá như các mốc hiện tại.
- Vẽ **sau** lớp nền cũ, **trước** bảng chữ. Vùng mạnh là `Zone` loại mới `Type = "strong"`, `IsMarker = false`; **không** đi qua `MergeZones`, `LimitAndBalance`, lọc `ZoneRadiusPrices`, `MaxZones`.
- `ZonePolicy`: `KeepType("strong") = true`, `Role("strong") = "manh"`, `BaseStrength` = 90 (vàng 98). `CanMerge("strong", x) = false` với mọi x.
- Bảng chữ / Telegram: thêm một dòng `Vùng mạnh (va đập + hợp lưu, chưa kiểm định): R 4158,4–4162,2 · S 4145,0–4148,3 …` (tối đa 4 vùng, gần giá trước, vùng vàng thêm ★).

## 5. Bất biến theo khung chart

- `StrongZones.Compute` không nhận tham số nào của khung chart; đầu vào duy nhất là `_hd30`.
- Chart M30: `_hd30 = HistoricalData` (nến cuối đang chạy). Chart khác: `_hd30` là history phụ — cùng dữ liệu, cùng nến cuối đang chạy ⇒ cùng j ⇒ cùng vùng.
- Cấu trúc vùng chỉ đổi khi có nến M30 mới (khoá bộ đệm ở mục 2). Giữa hai nến M30 chỉ màu/phía/lọc bán kính đổi theo giá.
- Kiểm tay sau khi build: mở cùng lúc M1, M5, M15, M30 của một symbol → danh sách vùng (lo, hi, nhãn) phải y hệt.

## 6. Ca biên

| Tình huống | Xử lý |
|---|---|
| Vùng bị phá (nến đóng xuyên qua) | **Không ẩn.** Vùng đổi màu theo phía giá. Đo: 91 % lần quay lại là vào vùng đã bị xuyên ≥ 2 lần; vùng "còn nguyên" hiếm và không tốt hơn. Vùng tự mất khi các điểm va đập trôi khỏi 5 phiên nhìn lại. |
| Giá đang trong vùng | Giữ màu của phía giá đi vào (mục 4.8 bước 3), nhãn thêm "(giá đang trong vùng)". |
| Vùng chồng / sát nhau | Mục 4.8 bước 2. |
| Đầu tuần | Mức tuần trước có ngay từ nến đầu tuần. HVN "tuần này" chỉ có khi đã đủ 60 nến. Thứ Hai: "hôm qua" = phiên thứ Sáu. |
| Sau kỳ nghỉ lễ (phiên < 20 nến) | Phiên ngắn không làm "hôm qua", không đếm vào 5 phiên HVN; nến của nó vẫn nằm trong profile tuần, U và điểm va đập. |
| Hôm nay chưa có profile | Không liên quan: không dùng profile hôm nay. Điểm va đập của hôm nay vẫn được dùng khi đã xác nhận. |
| Vừa qua chỗ nối hợp đồng | Điểm va đập trước chỗ nối bị loại (`seg` khác); mức ngày/tuần của kỳ trước chỗ nối bị bỏ hoặc cắt (mục 4.6). Vài phiên đầu sau chỗ nối sẽ ít hoặc không có vùng — giữ dòng cảnh báo sẵn có. |
| Market Replay | Dùng `ZonePolicy.AuxHistoryFrom` sẵn có (neo nến cuối của chart). Không đủ ~13 phiên M30 trước nến cuối ⇒ ít vùng; không báo lỗi. |
| History thiếu PriceLevels | Profile theo hàng rơi về TPO như `RowsOver`. VWAP/σ: nếu không nến nào trong kỳ có PriceLevels thì dùng giá điển hình × khối lượng nến (khối lượng 0 thì trọng số 1). Thêm ghi chú trên chart: "⚠ Thiếu khối lượng theo giá — mức hợp lưu tính gần đúng". |
| Chưa đủ dữ liệu cho U (dưới 2 phiên đã đóng) | Không vẽ vùng mạnh. |
| Giờ nghỉ (không có nến đang chạy) | Nến đã đóng cuối cùng bị coi là "đang chạy" ⇒ vùng trễ một nến cho tới khi phiên mới mở. Chấp nhận. |
| Biên độ đổi đột ngột | U lấy 5 phiên nên chậm ~2–3 phiên; chấp nhận, không thêm kẹp. |

## 7. Các lớp vùng cũ — đề xuất mặc định (cần người dùng đồng ý trước khi đổi)

| Lớp | Hiện tại | Đề xuất | Lý do |
|---|---|---|---|
| Vùng mạnh (mới) | — | **bật** | yêu cầu mới |
| VWAP tuần/ngày (dòng trên bảng) | bật | giữ | không vẽ gì lên chart |
| VAH/VAL hôm nay (`va_edge`) | bật | **tắt mặc định**, thêm input "Hiện VAH/VAL hôm nay" | người dùng nêu không dùng profile hôm nay vì đang phát triển |
| Dải HVN ngày/tuần (`ShowHvn`) | bật | **tắt mặc định** | HVN đã đi vào vùng mạnh dưới dạng hợp lưu; để cả hai thì chồng dải |
| LVN ngày (`ShowLvn`) | bật | giữ | vai trò khác (chỗ giá xuyên nhanh) |
| Mục tiêu chốt lời (`ShowTargets`) | bật | tắt theo `ShowHvn` | sinh từ HVN |
| Các lớp "Đo ·" | tắt | giữ tắt | |

Lưu ý mâu thuẫn cần nói với người dùng: `ZonePolicy` hiện ghi HVN là "nền — đi tiếp / mục tiêu, **không fade**" (kết luận đo cũ). Yêu cầu mới dùng HVN làm hợp lưu cho vùng canh đảo chiều và tô vàng. Phép đo lần này không phân xử được (vùng có HVN: TRAIN −0,17 R, TEST +0,16 R ở 1:2). Chú thích trong code giữ cả hai ý, không xoá ý cũ.

## 8. Test phải viết (`tests/Program.cs`)

Dữ liệu đối chiếu nằm ở `research/vung_manh_2026-11-25/fixture/` (GCZ26, 2026-09-20 22:00 → 2026-11-06, giờ UTC, 1610 nến M30):
- `m30_bars.csv` — `idx,time_utc,open,high,low,close,volume`
- `m30_levels.csv.gz` — `idx,price,volume` (khối lượng từng mức giá của nến idx)
- `expected.json` — `params`; `days` (start, end, U từng phiên); `weeks`; `pivots` (357 điểm: i, price, kind, conf); `cases` (689 ca, mỗi nến j từ 2026-10-18): `j, time_utc, now, U, levels, clusters, shown`.

Kết quả kỳ vọng tính **chỉ từ hai file fixture**, và đã kiểm trùng 689/689 với kết quả tính trên toàn bộ 2 năm dữ liệu. Sinh lại: `python parity_cases.py` (cần chạy `prep.py` trước).

Quy ước một ca: đưa nến `0..j+1` vào (nến `j+1` là nến đang chạy), `nowPrice = close[j]` (= trường `now`).

### 8.1 So C# = Python trên fixture (bắt buộc PASS toàn bộ)

1. `days`: ranh giới 35 phiên + U từng phiên (sai số ≤ 1e-6; 2 phiên đầu U = null).
2. `pivots`: đủ 357 điểm, đúng `i`, `price`, `kind`, `conf`.
3. Mỗi ca: `U` (≤ 1e-6); `levels` đúng số lượng và `name` (so theo tập, không cần đúng thứ tự); `lo`/`hi` sai số ≤ 1e-4 (VWAP, σ) — VAH/VAL/HVN phải bằng đúng; HVN đúng `peak`, `ratio` (≤ 1e-4), `dshape`, `ok`.
4. Mỗi ca: `clusters` (mọi cụm ≥ 3 điểm, sắp theo `lo`): đúng `lo`, `hi`, `n`, `pmin`, `pmax`, `names`, `ngroup`, `hvn`, `gold`; và `ngroup_khong_gop`, `gold_khong_gop` khi chạy với `SzGroupEdges = false`.
5. Mỗi ca: `shown` (sắp theo `lo`): đúng `lo`, `hi`, `side`, `color` (`xanh`/`do`/`vang`/`xam`), `label` (so chuỗi UTF-8 nguyên văn, dấu trừ trong "−1σ" là U+2212, dấu "·" là U+00B7, "★" là U+2605).

### 8.2 Năm ca ghi số để dò tay khi lệch

**Ca A — vùng vàng.** j = 1342, nến 2026-10-30 02:00 UTC, giá 4015,3, U = 10,028261. Mức: VWAP hôm qua 4041,8706 (σ = 12,9160 ⇒ +1σ 4054,7866, −1σ 4028,9546), VAH 4052,8, VAL 4029,2; VWAP tuần trước 4111,5234 (±1σ 4168,5253 / 4054,5215), VAH 4176,4, VAL 4042,8; HVN ngày [4038,0–4039,2] đỉnh 4039,0 tỉ lệ 3,6734 (hôm qua, chữ D, đủ điều kiện); HVN tuần này [4036,4–4037,2] đỉnh 4037,0 (chữ D, đủ điều kiện). 10 cụm. Vẽ 3 vùng:

| lo–hi | màu | nhãn |
|---|---|---|
| 4026,4–4028,6 | đỏ | `Kháng cự · 3 lần · VAL hôm qua + VWAP hôm qua −1σ` |
| 4032,3–4036,3 | đỏ | `Kháng cự · 6 lần · HVN tuần` |
| 4038,8–4042,0 | vàng | `★ Kháng cự rất mạnh · 3 lần · HVN ngày + VAL tuần trước + VWAP hôm qua` |

Vùng vàng dò tay: 3 điểm va đập — i = 1179 (2026-10-26 12:30, đỉnh 4039,4, conf 1181), i = 1183 (14:30, đỉnh 4041,4, conf 1185), i = 1260 (2026-10-28 07:00, đáy 4040,5, conf 1262). `lo = 4039,4 − 0,05 × 10,028 = 4038,899 → 4038,8`; `hi = 4041,4 + 0,501 = 4041,901 → 4042,0`. Dung sai 1,003: HVN ngày (4039,2 ≥ 4037,8), VAL tuần trước (4042,8 ≤ 4043,0), VWAP hôm qua. Ba nhóm: HVN ngày, dưới tuần, giữa ngày. Hai cụm bị loại vì sát vùng mạnh hơn: 4035,6–4039,6 (5 lần, HVN tuần + HVN ngày) và 4042,4–4046,3 (5 lần, VAL tuần trước + VWAP hôm qua).

**Ca B — nhiều kháng cự, lọc chồng.** j = 1042, 2026-10-21 13:00 UTC, giá 4155,3, U = 10,070435. 12 cụm. Vẽ: `4145,0–4148,3` xanh `Hỗ trợ · 3 lần · VWAP hôm qua`; `4158,4–4162,2` đỏ `Kháng cự · 3 lần · VAL tuần trước + VWAP hôm qua +1σ`; `4163,9–4168,1` đỏ `Kháng cự · 4 lần · VAL tuần trước`; `4174,3–4177,7` đỏ `Kháng cự · 5 lần · HVN tuần + VWAP tuần trước`. Cụm 4154,9–4158,6 (chứa giá, 1 nhóm) bị loại vì sát cụm 4158,4–4162,2 (2 nhóm).

**Ca C — giá đang trong vùng.** j = 935, 2026-10-19 05:30 UTC, giá 4204,8, U = 9,806087. Vẽ: `4180,4–4184,0` xanh `Hỗ trợ · 6 lần · HVN tuần + VAL hôm qua + VWAP hôm qua −1σ` (2 nhóm ⇒ không vàng; nếu `SzGroupEdges = false` thì là 3 nhóm ⇒ vàng — viết thêm một test cho nhánh này); `4192,0–4194,0` xanh `Hỗ trợ · 3 lần · HVN tuần + VWAP hôm qua`; `4197,2–4200,5` xanh `Hỗ trợ · 3 lần · HVN tuần`; `4202,4–4206,0` đỏ `Kháng cự · 4 lần · VWAP hôm qua +1σ (giá đang trong vùng)`.

**Ca D — một vùng.** j = 1502, 2026-11-04 14:00 UTC, giá 4043,6, U = 10,927826. 7 cụm, chỉ vẽ `4059,4–4062,8` đỏ `Kháng cự · 3 lần · HVN ngày` (HVN ngày 4059,6–4061,2 của 5 phiên trước, chữ D). HVN tuần trước 4036,4–4037,2 không đủ điều kiện (profile tuần không phải chữ D).

**Ca E — chỉ hỗ trợ.** j = 1238, 2026-10-27 19:00 UTC, giá 4073,9, U = 10,236522. 13 cụm. Vẽ: `4032,3–4036,3` xanh `Hỗ trợ · 5 lần · VWAP hôm qua +1σ`; `4042,4–4046,3` xanh `Hỗ trợ · 4 lần · VAL tuần trước`.

### 8.3 Ca dựng tay (không cần fixture)

- **Điểm va đập:** dãy nến dựng tay có một đỉnh rõ (đi tới ≥ 1 U, bật ≥ 1 U trong 6 nến) ⇒ đúng i và conf; bật lại chỉ 0,9 U ⇒ không có; bật ở nến thứ 7 ⇒ không có; hai nến cùng High ⇒ nến sau không thành đỉnh (đòi lớn hơn hẳn bên trái); giá vượt đỉnh trước khi bật đủ ⇒ không có; chỗ nối nằm giữa cửa sổ ⇒ không có.
- **Gom cụm:** giá `[100; 100,2; 100,4; 103; 103,1]`, wc = 0,5 ⇒ `{100; 100,2; 100,4}`, `{103; 103,1}`. Hoà: `[100; 100,3; 100,6; 100,9]`, wc = 0,3 ⇒ `{100; 100,3}` rồi `{100,6; 100,9}`.
- **Biên:** cụm 1 điểm giá trị 100, u = 10 ⇒ 99,0–101,0 (tối thiểu 0,20 U). Cụm 100,0–102,0, u = 10 ⇒ 99,5–102,5. Kiểm làm tròn ra mép tick với u lẻ.
- **VWAP/σ:** mức `{100: 1, 102: 3}` ⇒ VWAP 101,5, σ = 0,8660254.
- **Chữ D:** `poc_pos = 0,29` ⇒ không; `0,30` ⇒ có; `va_frac = 0,61` ⇒ không.
- **HVN đủ điều kiện:** giá chưa từng cách đỉnh 2 U ⇒ không; vừa đủ ⇒ có; `end ≥ j` ⇒ không; `SzHvnDOnly = false` + profile không chữ D ⇒ có.
- **Nhóm / vàng:** `{vah_d, vwap_d_tren, hvn_d}` ⇒ 2 nhóm, không vàng (gộp) / 3 nhóm, vàng (không gộp); `{vah_d, val_w, vwap_w}` ⇒ 3 nhóm, không HVN ⇒ không vàng; `{hvn_d, hvn_w, vwap_d}` ⇒ vàng.
- **Phía khi giá trong vùng:** nến trước đóng trên ⇒ hỗ trợ; đóng dưới ⇒ kháng cự; không có nến nào đóng ngoài ⇒ 0, màu xám, đầu nhãn `Vùng`.
- **Lọc chồng:** hai vùng cách 0,10 U ⇒ giữ vùng nhiều nhóm hơn; cùng nhóm ⇒ nhiều lần va đập hơn; cách đúng 0,15 U ⇒ giữ cả hai.
- **Trần mỗi phía:** 5 hỗ trợ, trần 3 ⇒ 3 vùng gần nhất; có 1 vùng vàng xa nhất trong bán kính ⇒ vàng + 2 vùng gần nhất.
- **Bán kính:** mép gần cách giá 4,0 U ⇒ vẽ; 4,01 U ⇒ không.
- **Không vẽ lại lùi:** tính ở j rồi ở j + 5; mọi điểm va đập có `conf ≤ j` ở lần đầu phải còn nguyên ở lần sau.
- **Bộ đệm:** gọi hai lần cùng `(n, thời gian nến j)` với `nowPrice` khác ⇒ cụm không đổi, chỉ `shown` đổi.
- **`ZonePolicy`:** `KeepType("strong")`, `Role("strong") == "manh"`, không gộp được với loại nào.

### 8.4 Sau khi PASS

Build theo quy trình repo (`./build-tpo.sh zones`), mở Quantower: so 4 khung M1/M5/M15/M30 cùng lúc (mục 5); chạy Market Replay một phiên trong tháng 10/2026 và đối chiếu bằng mắt với ca A–E.

## 9. Điểm chưa chắc — báo người dùng

1. **Chưa có lợi thế đo được** (mục 0). Dấu hiệu duy nhất đáng theo dõi: vùng hợp lưu ≥ 2 nhóm (R ở 1:2 dương 14/16 ô, TRAIN chưa tách khỏi 0). Nếu muốn dùng, đặt `SzMinConfluence = 2` — nhưng đó là **giả thuyết chưa kiểm định**; kiểm bằng dữ liệu sau 2026-11-09.
2. **Cách đếm "≥ 3 mức"**: spec gộp VAH với VWAP +1σ cùng kỳ (8 nhóm). Đếm theo chữ (12 mức) thì vùng vàng nhiều gấp ~3 (6 % → 19 % số nến trong 3 tuần fixture). Cần người dùng chốt `SzGroupEdges`.
3. **Chữ D**: bật theo yêu cầu, nhưng đo không thấy HVN của profile chữ D tốt hơn; bật thì vùng vàng chỉ có mặt ~5 % thời gian.
4. **Độ rộng**: không có độ rộng nào "bắt đỉnh đáy" tốt hơn (điểm đảo chiều không tụ về vùng). Độ rộng hiện tại là lựa chọn theo rủi ro.
5. **35 % thời gian không có vùng nào được vẽ** với mặc định — đúng thiết kế, không phải lỗi.
6. Phép đo chưa xét xác nhận order flow tại vùng (hấp thụ, delta) — đó mới là cách người dùng thực sự vào lệnh, và chưa được đo ở đây.
