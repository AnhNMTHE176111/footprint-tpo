# PLAN — Vùng kháng cự / hỗ trợ MẠNH cho SessionZones

> Fable viết spec + đo (2026-11-25). Opus implement. Số liệu: [`research/vung_manh_2026-11-25/DO-VUNG-MANH.md`](research/vung_manh_2026-11-25/DO-VUNG-MANH.md).
> Bản tham chiếu Python (nguồn sự thật khi spec và code lệch nhau): [`research/vung_manh_2026-11-25/vung_manh.py`](research/vung_manh_2026-11-25/vung_manh.py) + [`vm.py`](research/vung_manh_2026-11-25/vm.py).

> **Cập nhật 2026-11-25 (lần 2): mục 10, 11, 12 ở cuối file THAY THẾ mọi chỗ nói về HVN ở mục 1–9** (đỉnh ≥ 2,5 × trung bình, `PeakSharpness` 90 %, `HVN_TOP`, lọc chữ D, input `SzHvnDOnly`) và thay bảng input mục 3. Số liệu: [`research/vung_manh_2026-11-25/HVN-CUM.md`](research/vung_manh_2026-11-25/HVN-CUM.md).

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

## 10. HVN dạng cụm (thay định nghĩa HVN cũ)

> **2026-11-25, bản v2:** thông số (10.1), thuật toán (10.2) và cách vẽ hộp được thay bằng **mục 13** sau khi người dùng báo sót cụm NQ 25.530–25.608. Mục 10.3–10.4 còn hiệu lực trừ chỗ mục 13 ghi khác.

Người dùng định nghĩa HVN là **cụm khối lượng đủ lớn và đều (thân chữ D)** — dấu hiệu đấu giá ở đó đã xong; khi giá quay lại, cụm có giá trị bảo vệ vùng, để canh phản ứng đảo chiều **hoặc** phá vỡ. Không phải từng đỉnh nhọn. Mỗi profile thường một hộp, tối đa hai.

Bản tham chiếu: [`research/vung_manh_2026-11-25/hvn_cum.py`](research/vung_manh_2026-11-25/hvn_cum.py), hàm `clusters()`. Toàn bộ tính trên **số nguyên bước giá** nên C# phải ra đúng từng số.

### 10.1 Thông số (hằng số trong `StrongZoneParams`, KHÔNG có input)

| Hằng | Giá trị | Nghĩa |
|---|---|---|
| `HvnSmooth` (SM) | 0,05 | nửa cửa sổ làm mượt, × up |
| `HvnBody` (X) | 0,80 | **độ đều**: mọi mức giá trong hộp có khối lượng mượt ≥ 80 % đỉnh của hộp |
| `HvnSecond` (PK2) | 0,50 | hộp thứ hai: đỉnh ≥ 50 % đỉnh lớn nhất của profile |
| `HvnMassDay` (Y) | 0,10 | **đủ lớn**: hộp chứa ≥ 10 % khối lượng profile ngày |
| `HvnMassWeek` (Y_W) | 0,08 | như trên cho profile tuần (11–15 tuần dữ liệu, chọn theo mật độ) |
| `HvnMinWidth` (WMIN) | 0,20 | hộp rộng ≥ 0,20 × up (hẹp hơn là đỉnh nhọn) |
| `HvnMaxPerProfile` (MAXC) | 2 | tối đa 2 hộp mỗi profile |
| `HvnDays` | 5 | giữ nguyên |
| `HvnAway` | 2,0 | giữ nguyên, nhưng đo từ MÉP hộp (10.4) |

Xoá khỏi `StrongZoneParams`: `HvnRatio`, `HvnTop`, `DOnly`, `DPocLo`, `DPocHi`, `DVaMax`.

### 10.2 Thuật toán `StrongZones.HvnClusters(levels, tick, up, massMin, p)`

Đầu vào: khối lượng theo **từng mức giá thô** của mọi nến M30 trong profile (cộng dồn theo giá — đúng thứ đang dùng cho VWAP/σ ở 4.6, **không** qua `RowsOver`/`Snap`); `up` = trung bình `(h − l)` của các nến M30 `a..b` của chính profile đó.

1. Đổi giá sang số nguyên bước giá: `k = (long)Math.Round(price / tick)`. `t0 = min k`, `n = max k − t0 + 1`. Mảng `w[0..n−1]`, `w[k − t0] += volume`, chỗ không có giao dịch = 0. `tot = Σ w`. Nếu `n < 3` hoặc `tot ≤ 0` ⇒ không có hộp.
2. `h = max(1, (int)Math.Floor(SM × up / tick + 0.5))`.
3. `S[i] = Σ w[max(0, i−h) .. min(n−1, i+h)]` (tổng, không chia; ngoài mép coi là 0). Dùng mảng cộng dồn.
4. `used[] = false`; `P1 = max S`. Lặp tối đa 200 vòng:
   - `i* =` chỉ số **nhỏ nhất** có `S` lớn nhất trong các ô chưa `used`. Hết ô, hoặc `S[i*] ≤ 0`, hoặc `S[i*] < PK2 × P1` ⇒ dừng.
   - `thr = X × S[i*]`. `lo = hi = i*`. Lùi `lo` khi `lo > 0`, ô `lo−1` chưa `used` và `S[lo−1] ≥ thr`. Tiến `hi` tương tự.
   - `vai = (lo > 0 và used[lo−1] và S[lo−1] ≥ thr) hoặc (hi < n−1 và used[hi+1] và S[hi+1] ≥ thr)`.
   - Đánh dấu `used[lo..hi] = true` (kể cả khi bị loại ở các bước dưới).
   - `vai` ⇒ sang vòng sau (khối này dính liền một khối cao hơn, không có đáy tách).
   - `mass = Σ w[lo..hi] / tot` (khối lượng THÔ). `mass < massMin` ⇒ sang vòng sau.
   - `(hi − lo) < WMIN × up / tick` ⇒ sang vòng sau.
   - Ghi hộp: `Lo = (t0 + lo) × tick`, `Hi = (t0 + hi) × tick`, `Peak = (t0 + i*) × tick`, `Mass = mass`. Đủ `MAXC` hộp ⇒ dừng.
5. Thứ tự trả về = thứ tự tìm thấy (đỉnh cao trước).

`S` là tổng các số nguyên nên so sánh `≥ thr` ổn định; phép nhân `X × S[i*]` làm bằng `double` ở cả hai bên.

### 10.3 Dùng trong mức hợp lưu (thay `AddHvn` ở mục 4.6)

- `hvn_d`: với mỗi phiên trong 5 phiên đã đóng (luật chọn phiên như cũ) ⇒ `HvnClusters(..., massMin = HvnMassDay)`; mỗi hộp là một mức `[Lo, Hi]`, `Peak`, `Mass`, `End = b`, `Src`.
- `hvn_w`: tuần trước, và tuần này tới hết hôm qua (luật cũ, ≥ 60 nến) ⇒ `massMin = HvnMassWeek`.
- Bỏ khái niệm "profile chữ D" khỏi HVN (`DShape` không còn dùng để lọc; xoá trường nếu không còn ai đọc). Lý do: phiên mẫu của người dùng (NQ 23/11) có POC ở 81 % chiều cao profile nên bị lọc cũ loại; tiêu chí lớn + đều đã nằm trong hộp.
- Nhãn không đổi: `HVN ngày`, `HVN tuần`.

### 10.4 Hợp lưu và điều kiện "đã rời xa"

- Trùng ⇔ vùng va đập **giao hộp** có dung sai, đúng công thức 4.7 hiện có: `L.lo ≤ hi + TOL × u` và `L.hi ≥ lo − TOL × u`. (Đã đo luật "chỉ khi chạm mép hộp": kết quả gần trùng, không dùng.)
- `HvnOk` tại nến j: `a = End + 1`, `a ≤ j`, và `max( max(h[a..j]) − L.Hi , L.Lo − min(l[a..j]) ) ≥ HvnAway × u` — đo từ **mép hộp**, không từ đỉnh. Không còn nhánh `DOnly`.
- Luật vàng giữ nguyên (≥ 3 nhóm và có HVN). **Hệ quả đã đo: thời gian có vùng vàng tăng từ 6–7 % lên 15–19 %** (GC 15,1 %, NQ 19,0 %). Chưa có số liệu nói vàng tốt hơn vùng thường (GC 18 lệnh thắng 22 %, NQ 27 lệnh thắng 48 %).

### 10.5 Test

**a. Mức hàm — `fixture/hvn_cum_cases.json`** (11 profile; mỗi ca có `tick`, `up`, `Y`, `levels = [[giá, khối lượng], …]`, kỳ vọng `h`, `clusters[{lo, hi, peak, mass, rel}]`). So `h`, số hộp, `lo`/`hi`/`peak` bằng đúng (sai số < tick/2), `mass` ≤ 1e-6.

| Ca | up | h | Hộp kỳ vọng (lo – hi · đỉnh · tỉ trọng) |
|---|---|---|---|
| **NQZ26 phiên 2026-11-23** (ca người dùng vẽ) | 166,446 | 33 | 26802,50 – 26874,75 · 26817,75 · 0,285 |
| NQZ26 phiên 2026-11-18 | 125,478 | 25 | 27143,00 – 27206,25 · 27190,25 · 0,276 |
| NQZ26 phiên 2026-11-10 (hai hộp) | 102,717 | 21 | 27768,00 – 27812,00 · 27790,75 · 0,137 ; 27958,25 – 28032,75 · 27995,00 · 0,144 |
| NQZ26 phiên 2026-11-13 | 104,413 | 21 | không có |
| NQZ26 phiên 2026-11-17 | 123,886 | 25 | 26953,00 – 26987,00 · 26977,25 · 0,136 |
| NQZ26 tuần 2026-11-15 → 11-20 (Y = 0,08) | 132,708 | 27 | không có |
| GCZ26 phiên 2026-10-29 | 11,430 | 6 | 4034,5 – 4040,6 · 4037,6 · 0,307 |
| GCZ26 phiên 2026-11-05 (hai hộp) | 15,363 | 8 | 4132,7 – 4137,2 · 4134,3 · 0,142 ; 4122,2 – 4127,9 · 4125,3 · 0,130 |
| GCZ26 phiên 2026-11-03 | 10,241 | 5 | không có |
| GCZ26 phiên 2026-10-28 (đỉnh nhọn nhất bị loại, lấy thềm dưới) | 9,496 | 5 | 4051,3 – 4055,0 · 4054,1 · 0,132 |
| GCZ26 tuần 2026-10-25 → 10-30 (Y = 0,08) | 10,370 | 5 | 4030,2 – 4040,3 · 4037,5 · 0,155 |

**b. Ca dựng tay** (không cần fixture). Số kỳ vọng chính xác lấy bằng cách chạy `hvn_cum.clusters` trên đúng dãy dựng tay rồi chép vào test:
- Một thân phẳng giữa hai đuôi mỏng ⇒ một hộp ôm thân.
- Đỉnh nhọn: một mức giá khối lượng gấp 100 lần các mức khác ⇒ thân hẹp hơn `WMIN × up` ⇒ không có hộp.
- Vai: hai bướu cao 100 và 85, đáy giữa 75 (75 ≥ 0,8 × 85) ⇒ một hộp, bướu thấp không thành hộp riêng.
- Hai hộp: hai bướu cao 100 và 70, đáy giữa 20, mỗi bướu ≥ 10 % khối lượng ⇒ hai hộp, bướu cao trước.
- Bướu thứ hai cao 45 (< 50 % của 100) ⇒ một hộp.
- Hoà: hai bướu y hệt nhau ⇒ bướu giá thấp được tìm trước.
- Tỉ trọng: thân chứa dưới 10 % ⇒ loại; đúng 10 % ⇒ nhận.
- `HvnOk`: giá từng cách **mép trên** hộp đúng 2 U ⇒ đủ; cách đỉnh 2 U nhưng cách mép 1,9 U ⇒ không đủ.

**c. Cả bộ máy — `fixture/expected_cum.json`** thay `expected.json` (cùng `m30_bars.csv`, `m30_levels.csv.gz`; 689 ca; 357 điểm va đập không đổi). Khác cấu trúc cũ: mức HVN có `peak`, `mass`, `src`, `end`, `ok` (không còn `ratio`, `dshape`). So như mục 8.1, HVN so `lo`/`hi`/`peak` bằng đúng, `mass` ≤ 1e-6. Sau khi C# PASS thì **xoá `expected.json` cũ** và các test đọc nó. Trong 689 ca: 128 ca có vùng vàng được vẽ (19 %; định nghĩa cũ khoảng 6 %), 411 ca có vùng dính HVN.

Năm ca ghi số của mục 8.2 đổi thành:

| Ca | j · giờ UTC · giá · U | HVN (đều đủ điều kiện) | Vùng được vẽ |
|---|---|---|---|
| A | 1342 · 2026-10-30 02:00 · 4015,3 · 10,028261 | ngày: 4034,5–4040,6 (hôm qua, 30,7 %), 4051,3–4055,0, 4071,2–4074,8, 4007,8–4012,2, 4036,9–4043,2; tuần này: 4032,8–4040,3 (16,6 %) | `4026,4–4028,6` đỏ `Kháng cự · 3 lần · VAL hôm qua + VWAP hôm qua −1σ`; `4032,3–4036,3` đỏ `Kháng cự · 6 lần · HVN tuần + HVN ngày`; `4038,8–4042,0` vàng `★ Kháng cự rất mạnh · 3 lần · HVN tuần + HVN ngày + VAL tuần trước + VWAP hôm qua` |
| B | 1042 · 2026-10-21 13:00 · 4155,3 · 10,070435 | ngày: 4195,0–4198,4, 4195,9–4198,5, 4174,8–4177,3, 4165,5–4168,3, 4114,0–4117,8; không có HVN tuần | `4145,0–4148,3` xanh `Hỗ trợ · 3 lần · VWAP hôm qua`; `4158,4–4162,2` đỏ `Kháng cự · 3 lần · VAL tuần trước + VWAP hôm qua +1σ`; `4163,9–4168,1` đỏ `Kháng cự · 4 lần · HVN ngày + VAL tuần trước`; `4174,3–4177,7` đỏ `Kháng cự · 5 lần · HVN ngày + VWAP tuần trước` |
| C | 935 · 2026-10-19 05:30 · 4204,8 · 9,806087 | 7 hộp ngày: 4195,9–4198,5, 4174,8–4177,3, 4165,5–4168,3, 4114,0–4117,8, 4207,4–4211,1, 4179,6–4183,8, 4193,6–4196,2 | `4180,4–4184,0` xanh `Hỗ trợ · 6 lần · HVN ngày + VAL hôm qua + VWAP hôm qua −1σ`; `4192,0–4194,0` xanh `Hỗ trợ · 3 lần · HVN ngày + VWAP hôm qua`; `4197,2–4200,5` xanh `Hỗ trợ · 3 lần · HVN ngày`; `4206,7–4209,6` đỏ `Kháng cự · 4 lần · HVN ngày + VWAP tuần trước +1σ` |
| D | 1502 · 2026-11-04 14:00 · 4043,6 · 10,927826 | ngày: 4034,5–4040,6, 4051,3–4055,0; tuần trước: 4030,2–4040,3 | `4046,4–4050,4` đỏ `Kháng cự · 6 lần · HVN ngày` |
| E | 1238 · 2026-10-27 19:00 · 4073,9 · 10,236522 | ngày: 4007,8–4012,2, 4036,9–4043,2, 4134,0–4138,0 | `4032,3–4036,3` xanh `Hỗ trợ · 5 lần · HVN ngày + VWAP hôm qua +1σ`; `4042,4–4046,3` xanh `Hỗ trợ · 4 lần · HVN ngày + VAL tuần trước` |

Sinh lại cả hai file: `python hvn_cum_fixture.py` (cần `prep1.py gc`, `prep1.py nq` trước cho phần a).

**d. Kiểm tay trên Quantower:** chart NQZ26, phiên 2026-11-23 ⇒ hộp HVN ngày 26802,50 – 26874,75. Chart GCZ26, phiên 2026-10-29 ⇒ 4034,5 – 4040,6.

## 11. Bỏ hẳn HVN kiểu cũ

Sau thay đổi này trong SessionZones chỉ còn một loại HVN: hộp của mục 10.

| Chỗ | Việc |
|---|---|
| `ProfileEngine.cs` · `StrongZones.AddHvn` (quanh dòng 1545), `FindHvnIdx` (1437), `PeakSharpness` theo chỉ số (1461) | `AddHvn` gọi `HvnClusters`. Xoá `FindHvnIdx` và `PeakSharpness` bản chỉ số nếu không còn ai gọi. |
| `ProfileEngine.cs` · `HvnOk` (1599) | đo từ mép hộp, bỏ nhánh `DOnly` (10.4). |
| `ProfileEngine.cs` · `StrongZoneParams` (1200) | thêm hằng mục 10.1; xoá `HvnRatio`, `HvnTop`, `DOnly`, các `D*`. |
| `ProfileEngine.cs` · `ProfileEngine.FindHvn` (495), `ProfileEngine.PeakSharpness` (472) bản public | **GIỮ** — `DailyTpoBias.cs` dòng 195 còn gọi `FindHvn`, và test cũ của hai hàm này phải tiếp tục PASS. Chỉ SessionZones thôi không gọi nữa. |
| `SessionZones.cs` · khối "HVN/LVN gộp nhiều phiên" (dòng ~595–680): B3 HVN tuần (`FindHvn(wkRows)` + `PeakSharpness`), B4 HVN ngày (mốc 1 giá + viền nền) | Xoá B3, B4. Thay bằng lớp **hộp HVN**: lấy đúng danh sách mức `hvn_d` / `hvn_w` mà `StrongZones.Compute` đã tính (trả thêm ra từ kết quả, không tính lần hai), vẽ mỗi hộp `[Lo, Hi]` khi hộp **đủ điều kiện `HvnOk`** và mép gần cách giá ≤ bán kính vùng mạnh (4 U). Màu `HvnColor`, alpha 30, viền 1 px; nhãn `HVN ngày · 29 % khối lượng` / `HVN tuần · 17 % khối lượng`. Hộp của các phiên khác nhau chồng nhau: vẽ hộp mới nhất, bỏ hộp cũ hơn nếu phần giao > 50 % bề rộng hộp nhỏ hơn. |
| `SessionZones.cs` · gộp tuần `WeekLookbackWeeks` cho HVN tuần | Xoá: HVN tuần giờ là tuần trước + tuần này tới hết hôm qua như vùng mạnh. `wkRows` nếu còn dùng cho LVN tuần thì giữ phần dựng profile với hằng 3 tuần. |
| `SessionZones.cs` · `SharpnessGate`, `MaxLevelThicknessPrices`, `ShowMarkerBand`, `ShowContextBands`, `MinHvnRatio`, `MaxHvn`, trường `Zone.BandLo/BandHi`, `Zone.Ratio` | Xoá cùng B3/B4. |
| `SessionZones.cs` · mục tiêu chốt lời (`ShowTargets`, `TargetMinRatio`, `TargetColor`, `Zone.IsTarget`, dòng ~784) | Sinh từ HVN cũ theo tỉ lệ ⇒ **xoá**. Hộp HVN xa hơn bán kính không vẽ. |
| `SessionZones.cs` · `ZonePolicy` các loại `hvn_week`, `hvn_day` | Thay bằng một loại `hvn_box`: `IsMarker = false`, `KeepType = true`, `Role = "nen"`, không gộp với loại nào, không qua `MergeZones` / `LimitAndBalance` / `MaxZones`. Dòng Telegram "Nền HVN (đi tiếp/mục tiêu)" đổi thành `Hộp HVN (cụm khối lượng, chưa kiểm định): 26802,50–26874,75 · …` (tối đa 3, gần giá trước). |
| `SessionZones.cs` · chú thích đầu file và `Description` | Sửa câu mô tả HVN: "hộp HVN = cụm khối lượng lớn và đều của phiên/tuần đã đóng". Giữ chữ "chưa kiểm định". Giữ cả ghi chú cũ "HVN: đi tiếp / mục tiêu, không fade" bên cạnh cách dùng mới (canh đảo chiều **hoặc** phá vỡ) — phép đo chưa phân xử. |
| `tests/` | Test của `ProfileEngine.FindHvn` / `PeakSharpness` / `FindLvn`: giữ nguyên. Test `StrongZonesTests.cs` đọc `expected.json` (dòng 57), các kiểm `DShape`, `Ratio`, ca `hvn_w 4036,4` (dòng ~437): viết lại theo 10.5. Test `ZonePolicy` cho `hvn_week`/`hvn_day`: đổi sang `hvn_box`. Mọi test không liên quan HVN phải PASS không sửa. |
| LVN (`FindLvn`, `ShowLvn`) | **Không đổi** trong đợt này. |

Lưu ý chart đã lưu: Quantower nhớ giá trị input theo tên thuộc tính. Đặt tên thuộc tính mới cho ô bật hộp HVN (`ShowHvnBox`), không dùng lại `ShowHvn`, để giá trị cũ không dính sang.

## 12. Tối giản settings của SessionZones

Hiện có 65 ô. Người dùng không chỉnh con số nào. Sau đợt này còn **19 ô**: bật/tắt lớp, màu, Telegram, lệch giờ. Mọi con số thành hằng (`const` hoặc trường `StrongZoneParams`) với đúng giá trị đang chạy.

### 12.1 Ô còn lại (thứ tự hiển thị)

| Nhóm | Tên hiển thị | Thuộc tính | Mặc định |
|---|---|---|---|
| Hiển thị | Hiện vùng mạnh (va đập nhiều + hợp lưu) | `ShowStrongZones` | bật |
| Hiển thị | Hiện hộp HVN (cụm khối lượng lớn của ngày/tuần trước) | `ShowHvnBox` (mới) | bật |
| Hiển thị | Hiện LVN (chỗ khối lượng mỏng, giá hay xuyên nhanh) | `ShowLvn` | tắt |
| Hiển thị | Hiện VAH/VAL hôm nay | `ShowTodayVa` | tắt |
| Hiển thị | Vẽ đường VWAP tuần và ngày | `DrawVwapLines` | tắt |
| Hiển thị | Hiện bảng chữ tóm tắt phiên | `ShowZones` (đổi tên hiển thị; Opus kiểm ô này đang điều khiển đúng phần nào rồi đặt tên cho khớp) | bật |
| Màu | Màu hỗ trợ | `SupColor` | như cũ |
| Màu | Màu kháng cự | `ResColor` | như cũ |
| Màu | Màu vùng rất mạnh | `StrongGoldColor` | như cũ |
| Màu | Màu hộp HVN | `HvnColor` | như cũ |
| Màu | Màu VWAP tuần | `VwapWeekColor` | như cũ |
| Màu | Màu VWAP ngày | `VwapDayColor` | như cũ |
| Giờ | Lệch giờ so với UTC (Việt Nam = 7) | `TzOffset` | 7 |
| Telegram | Gửi Telegram | `TeleEnabled` | tắt |
| Telegram | Bot token | `TeleBotToken` | trống |
| Telegram | Chat ID | `TeleChatId` | trống |
| Telegram | Tab này được gửi (chỉ bật ở một chart) | `TeleIsSender` | tắt |
| Telegram | Gửi thử ngay (bật rồi tắt) | `TeleTestNow` | tắt |
| Telegram | Kèm lịch tin Forex Factory | `TeleShowNews` | bật |

### 12.2 Ô hiện có → số phận

| Ô hiện có (thuộc tính) | Xử lý | Lý do |
|---|---|---|
| `TzOffset` | giữ | cần cho giờ hiển thị và giờ gửi tin |
| `AsiaStart`, `EuropeStart`, `UsStart` | hằng 300 / 750 / 1140 | giờ phiên theo giờ Việt Nam, người dùng không đổi |
| `RowTicks` | hằng 2 | fixture và mọi phép đo dùng 2 |
| `GapMinutes` | hằng 75 | luật tách phiên của spec |
| `UseVolume` | hằng true | đã có nhánh tự rơi về TPO khi thiếu khối lượng theo giá |
| `ZoneLookbackSessions` | hằng 10 | |
| `ShowHvn`, `MaxHvn`, `MinHvnRatio`, `ShowContextBands`, `ShowMarkerBand`, `SharpnessGate`, `MaxLevelThicknessPrices`, `WeekLookbackWeeks` | **xoá hẳn** | HVN cũ bị bỏ (mục 11); thay bằng `ShowHvnBox` |
| `ShowTargets`, `TargetMinRatio`, `TargetColor` | **xoá hẳn** | mục tiêu sinh từ HVN cũ |
| `ShowLvn` | giữ | |
| `MaxLvn` | hằng 2 | |
| `ShowTodayVa` | giữ | |
| `ShowStrongZones` | giữ | |
| `SzMinTouches`, `SzBounceU`, `SzLookbackDays`, `SzClusterU`, `SzConfluenceTolU`, `SzMinConfluence`, `SzHvnAwayU`, `SzRadiusU`, `SzMaxPerSide` | hằng 3 / 1,0 / 5 / 0,30 / 0,10 / 1 / 2,0 / 4,0 / 3 | giá trị đã đo; tính theo U nên dùng chung cho GC và NQ |
| `SzHvnDOnly` | **xoá hẳn** | lọc chữ D bị bỏ (10.3) |
| `SzGroupEdges` | hằng true | cách đếm nhóm đã dùng trong mọi phép đo |
| `StrongGoldColor`, `SupColor`, `ResColor`, `HvnColor`, `VwapWeekColor`, `VwapDayColor` | giữ | |
| `ZoneRangeAtr`, `ZoneRadiusPrices`, `MaxZones` | hằng 3,0 / 12,0 / 5 | chỉ còn tác dụng với lớp cũ (VA hôm nay, LVN). Lưu ý `ZoneRadiusPrices = 12 giá` là số của vàng (≈ 1 U của GC), trên NQ quá hẹp; đổi sang `1,0 × U` là thay đổi hành vi ⇒ làm riêng, có test, không gộp vào đợt gọt input |
| `WeekGapHours` | hằng 30 | |
| `ShowAllZones` (DEBUG) | xoá hẳn | |
| `SpliceGuard`, `MinSpliceJumpPrices` | **xoá ô, tự động** — mục 12.3 | |
| `ShowSessionHighLow`, `ShowNakedPoc`, `ShowPocClusters`, `ShowWeekLvn` (nhóm "Đo ·") | xoá ô, hằng false (để nguyên code, hoặc xoá code nếu gọn) | ghi chú trong chính tên ô: đã đo không có tác dụng / mẫu quá nhỏ / chưa đo |
| `NakedColor` | xoá ô, thành hằng | lớp naked POC tắt cứng |
| `DrawVwapLines` | giữ | |
| `ShowZones` | giữ, đổi tên hiển thị | |
| `TeleEnabled`, `TeleBotToken`, `TeleChatId`, `TeleIsSender`, `TeleTestNow`, `TeleShowNews` | giữ | vận hành |
| `TeleUsStartMin`, `TelePreUsMin`, `TeleMorningGrace`, `TeleAfternoonMin` | hằng 1160 / 30 / 6 / 840 | |
| `TeleShareDir` | hằng "" (thư mục mặc định) | |

Yêu cầu khi làm:
- Giá trị hằng phải **bằng đúng mặc định hiện tại** ⇒ mọi test hiện có (ngoài phần HVN) PASS không sửa kỳ vọng.
- Chart đã lưu giá trị cho ô bị xoá: kiểm bằng cách mở một workspace cũ, phải không lỗi.
- Sắp `InputParameter` theo thứ tự bảng 12.1; tên hiển thị không còn tiền tố "Vùng mạnh ·", "TG ·", "Đo ·", "Cổng:", "DEBUG:".
- `Description` của indicator viết lại ngắn, giữ câu "chưa kiểm định; không phải tín hiệu vào lệnh".

### 12.3 Chỗ nối hợp đồng: tự bật/tắt

Bộ chặn chỗ nối chỉ có nghĩa với mã liên tục. Trên một hợp đồng cụ thể nó chỉ có thể sai: NQZ26 bị bắt nhầm 3 lần trong 11 tuần (khoảng trống giá thật qua giờ nghỉ), tháng 11 mất gần nửa số vùng.

- Thêm hàm thuần `ZonePolicy.IsSingleContract(string symbolName)`:
  1. `null` hoặc rỗng ⇒ `false`; bỏ khoảng trắng, đổi sang chữ hoa; nếu bắt đầu bằng `/` ⇒ `false` (mã liên tục kiểu `/GC:XCEC`);
  2. cắt phần từ dấu `:` hoặc `.` hoặc `@` đầu tiên trở đi;
  3. `true` ⇔ phần còn lại khớp `^[A-Z0-9]{1,4}[FGHJKMNQUVXZ][0-9]{1,2}$` (gốc + mã tháng + năm).
- `spliceJump = IsSingleContract(Symbol.Name) ? 0 : 20,0 × 10 × tick` ở cả ba chỗ đang dùng (`SessionZones.cs` dòng ~468, ~606, ~732). Dòng cảnh báo "chỗ nối" chỉ hiện khi bộ chặn đang bật.
- Test: `GCZ26`, `NQZ26`, `MGCZ26`, `GCZ6`, `6EZ26`, `NQZ26:XCME` ⇒ true; `/GC:XCEC`, `/NQ`, `GC`, `NQ`, `XAUUSD`, `NAS100USD`, `USTEC`, chuỗi rỗng, `null` ⇒ false.
- Opus kiểm `Symbol.Name` thật trên Quantower với một hợp đồng và một mã liên tục (tên có thể nằm ở thuộc tính khác hoặc có hậu tố khác) rồi chỉnh bước 2 cho khớp; nếu Quantower có thuộc tính nói thẳng mã là liên tục thì dùng thuộc tính đó thay regex.
- Chưa giải quyết: mã liên tục của NQ vẫn dùng ngưỡng 50 điểm và vẫn có thể bắt nhầm khoảng trống thật. Ngưỡng theo U (khoảng 3 U) mới chỉ có 3 mẫu NQ và 1 chỗ nối thật của GC để so — **chưa đo đủ, chưa đổi**.

### 12.4 Thứ tự làm đề nghị

1. `HvnClusters` + test 10.5 a, b.
2. Nối vào `StrongZones` (10.3, 10.4) + test 10.5 c; xoá `expected.json` cũ.
3. Lớp hộp HVN trong `SessionZones.cs`, xoá B3/B4/mục tiêu (mục 11).
4. `IsSingleContract` + tự tắt bộ chặn (12.3).
5. Gọt input (12.1, 12.2).
6. Test toàn bộ → build `./build-tpo.sh zones` → kiểm tay 10.5 d và 4 khung M1/M5/M15/M30.

### 12.5 Cần người dùng chốt

1. Vùng vàng sẽ có mặt 15–19 % thời gian (trước 6–7 %). Giữ luật "≥ 3 nhóm và có HVN", hay siết lại?
2. Ô "Hiện hộp HVN" mặc định bật: chart sẽ có thêm tối đa vài hộp cam bên cạnh vùng mạnh.
3. Mục tiêu chốt lời (đường tím) bị xoá cùng HVN cũ.
4. Hộp NQ 23/11 mới là 26802,50 – 26874,75; cần người dùng nhìn ảnh cận cảnh xác nhận biên, nhất là mép trên (có bậc thềm tới 26.895).

## 13. HVN dạng cụm v2 — tiêu chí không phụ thuộc biên độ profile (thay mục 10.1–10.2, sửa 10.3 và mục 11 phần hộp HVN)

Lý do, số đo, ảnh trước/sau: [`research/vung_manh_2026-11-25/HVN-CUM-V2.md`](research/vung_manh_2026-11-25/HVN-CUM-V2.md). Bản tham chiếu: [`hvn_cum2.py`](research/vung_manh_2026-11-25/hvn_cum2.py) hàm `clusters()`; hộp được vẽ: `vung_manh.hvn_boxes()`.

Ca người dùng báo sót (NQZ26): cụm 25.530–25.608 của phiên 2026-11-20 và của tuần 15→20/11. Bản mục 10 loại nó vì "đủ lớn" đo bằng % cả profile và hộp thứ hai so với đỉnh lớn nhất cả profile — hai phép so đều yếu đi khi profile chạy rộng. Trạng thái của cả lớp vẫn là **chưa kiểm định**.

### 13.1 Thông số (hằng trong `StrongZoneParams`, không có input)

| Hằng | Giá trị | Nghĩa | So với mục 10 |
|---|---|---|---|
| `HvnSmooth` | 0,05 | nửa cửa sổ làm mượt, × up | giữ |
| `HvnBody` | 0,80 | **lõi**: khối lượng mượt ≥ 80 % đỉnh | giữ (trước là cả hộp, giờ là lõi) |
| `HvnWidth` | 0,45 | bề rộng đích của hộp, × up: lõi hẹp hơn thì nới | mới |
| `HvnWidenFloor` | 0,50 | khi nới không lấy mức giá có khối lượng mượt < 50 % đỉnh | mới |
| `HvnWidenClimb` | 0,05 | khi nới không lấy mức giá cao hơn (đáy đã đi qua ở phía đó + 5 % đỉnh) — không leo sang bướu bên cạnh | mới |
| `HvnAround` | 3,0 | "vùng xung quanh" = ± 3 × up; dùng cho cả luật đỉnh cục bộ lẫn luật nổi bật | mới |
| `HvnContrast` | 2,0 | nổi bật: mật độ hộp ≥ 2 × mật độ phần profile trong vùng xung quanh, ngoài hộp | mới |
| `HvnBars` | 4,5 | nổi bật: khối lượng hộp ≥ 4,5 lần khối lượng trung bình một nến M30 của profile | mới |
| `HvnMassDay` | **0,12** | hoặc hộp chứa ≥ 12 % khối lượng profile ngày | 0,10 → 0,12 (hộp giờ rộng hơn khoảng 1,2 lần) |
| `HvnMassWeek` | 0,08 | … profile tuần | giữ |
| `HvnMinWidth` | 0,20 | hộp sau khi nới vẫn hẹp hơn 0,20 × up ⇒ bỏ | giữ |
| `HvnMaxPerProfile` | 2 | số hộp tối đa khi profile hẹp | giữ |
| `HvnMaxStep` | 6,0 | số hộp tối đa = `min(HvnMaxCap, max(HvnMaxPerProfile, floor(biên độ profile / (6 × up))))` | mới |
| `HvnMaxCap` | 4 | | mới |
| `HvnFloor` | 0,10 | dừng khi đỉnh còn lại < 10 % đỉnh lớn nhất (chỉ để chặn vòng lặp; đo: đặt 0 hay 0,2 kết quả không đổi) | mới |
| `HvnRadius` | 8,0 | hiển thị hộp HVN: mép gần cách giá ≤ 8 U (vùng mạnh vẫn `Radius` = 4) | mới |
| `HvnMaxSide` | 2 | hiển thị hộp HVN: tối đa 2 hộp gần nhất mỗi phía giá | mới |

Xoá: `HvnSecond`.

### 13.2 Thuật toán `StrongZones.HvnClusters(levels, tick, up, nBars, massMin, p)`

Thêm tham số `nBars` = số nến M30 của profile (`b − a + 1`). Bước 1–3 của 10.2 giữ nguyên (`w`, `tot`, `h`, `S`). Tiếp:

4. `upT = up / tick` (double). `dn = max(1, (int)Math.Floor(HvnAround × upT + 0.5))`. `wt = HvnWidth × upT` (double). `maxBoxes = min(HvnMaxCap, max(HvnMaxPerProfile, (int)Math.Floor((n − 1) / (HvnMaxStep × upT))))`. `P1 = max S`. `used[] = false`.
5. Lặp tối đa 2000 vòng:
   1. `i*` = chỉ số **nhỏ nhất** có `S` lớn nhất trong các ô chưa `used`; `P = S[i*]`. Hết ô, hoặc `P ≤ 0`, hoặc `P < HvnFloor × P1` ⇒ dừng.
   2. **Lõi**: `thr = HvnBody × P`; nới `lo`, `hi` từ `i*` khi ô kề chưa `used` và `S ≥ thr` (y như 10.2). `vai` như 10.2. `vai` ⇒ `used[lo..hi] = true`, sang vòng sau.
   3. **Đỉnh cục bộ**: nếu `P < max(S[max(0, i* − dn) .. min(n − 1, i* + dn)])` (xét mọi ô, kể cả đã `used`) ⇒ `used[lo..hi] = true`, sang vòng sau. Bằng nhau thì qua.
   4. Ghi `coreLo = lo`, `coreHi = hi`. **Nới**: `fl = HvnWidenFloor × P`; `vd = HvnWidenClimb × P`; `mL = min S[lo..i*]`; `mR = min S[i*..hi]`. Lặp khi `(hi − lo) < wt`:
      - `okL = lo > 0 && !used[lo−1] && S[lo−1] ≥ fl && S[lo−1] ≤ mL + vd`; `okR = hi < n−1 && !used[hi+1] && S[hi+1] ≥ fl && S[hi+1] ≤ mR + vd`.
      - cả hai sai ⇒ thoát; `okL && (!okR || S[lo−1] ≥ S[hi+1])` ⇒ `lo−−`, `mL = min(mL, S[lo])`; ngược lại ⇒ `hi++`, `mR = min(mR, S[hi])`.
   5. `used[lo..hi] = true` (kể cả khi bị loại ở dưới).
   6. `(hi − lo) < HvnMinWidth × upT` ⇒ sang vòng sau.
   7. `vIn = Σ w[lo..hi]`, `nIn = hi − lo + 1`; `A = max(0, lo − dn)`, `Z = min(n − 1, hi + dn)`; `nOut = (lo − A) + (Z − hi)`; `vOut = Σ w[A..lo−1] + Σ w[hi+1..Z]`.
      - `lon = vIn ≥ massMin × tot`
      - `noi = vIn × nBars ≥ HvnBars × tot && vIn × nOut ≥ HvnContrast × vOut × nIn`
      - `!(lon || noi)` ⇒ sang vòng sau.
   8. Ghi hộp: `Lo`, `Hi`, `Peak` như 10.2, `Mass = vIn / tot`, thêm `CoreLo`, `CoreHi`. Đủ `maxBoxes` ⇒ dừng.

Mọi vế so sánh là tích các số nguyên (khối lượng, số ô, số nến) với một hằng ⇒ làm bằng `double`, không chia.

### 13.3 Dùng trong mức hợp lưu

Như 10.3, chỉ đổi lời gọi: `HvnClusters(..., nBars = b − a + 1, massMin = HvnMassDay | HvnMassWeek, p)`. Luật chọn phiên, tuần, `HvnOk` (đo từ mép hộp), luật giao hộp, luật vàng: **không đổi**.

### 13.4 Hộp HVN được vẽ — `StrongZones.HvnBoxes` (sửa dòng "lớp hộp HVN" của mục 11)

1. Ứng viên: mức HVN đủ `HvnOk` và mép gần cách giá ≤ **`HvnRadius` × U** (trước: `Radius`).
2. Bỏ hộp trùng như hiện có (sắp `End` giảm dần → `hvn_d` trước → `Mass` giảm dần → `Lo` tăng dần; trùng khi phần giao > 50 % bề rộng hộp nhỏ hơn). **Thêm**: hộp bị bỏ khác loại với hộp giữ lại (một `hvn_d`, một `hvn_w`) ⇒ nhãn hộp giữ lại thành `HVN ngày + tuần`.
3. **Thêm**: giữ mọi hộp đang chứa giá (`Dist = 0`); mỗi phía giá chỉ giữ `HvnMaxSide` hộp gần nhất (sắp `Dist` tăng dần, rồi `Lo` tăng dần). "Dưới giá" ⇔ `Hi < now`.
4. Trả về sắp theo `Lo`.

Dòng Telegram "Hộp HVN" dùng đúng danh sách này.

### 13.5 Test

**a. Mức hàm — `fixture/hvn_cum2_cases.json`** (19 profile; mỗi ca có `tick`, `up`, `so_nen_m30`, `mass_min`, `levels`, kỳ vọng `h`, `dn`, `max_boxes`, `clusters[{lo, hi, peak, core_lo, core_hi, mass, bars, con, lon, noi}]`; thông số ở `params`). So `h`, `dn`, `max_boxes`, số hộp, `lo`/`hi`/`peak`/`core_lo`/`core_hi` bằng đúng, `mass` ≤ 1e-6, `lon`/`noi` đúng.

| Ca | up | h | dn | hộp tối đa | Hộp kỳ vọng (lo – hi · đỉnh · tỉ trọng · số nến · nổi bật) |
|---|---|---|---|---|---|
| **NQZ26 phiên 2026-11-20** (ca báo sót) | 158,043 | 32 | 1897 | 2 | 25538,50 – 25609,75 · 25583,00 · 0,111 · 5,1 · ×2,80 |
| **NQZ26 tuần 2026-11-15 → 11-20** (ca báo sót) | 132,708 | 27 | 1592 | 4 | 27239,25 – 27299,00 · 27268,50 · 0,083 · 19,1 · ×2,12 ; 25544,25 – 25604,00 · 25583,25 · 0,026 · 6,1 · ×2,78 |
| **NQZ26 phiên 2026-11-23** (ca người dùng vẽ) | 166,446 | 33 | 1997 | 2 | 26801,50 – 26876,50 · 26817,75 · 0,294 · 13,5 · ×6,03 |
| NQZ26 phiên 2026-11-18 | 125,478 | 25 | 1506 | 2 | 27143,00 – 27206,25 · 27190,25 · 0,276 · 12,7 · ×3,61 (lõi đã đủ rộng, không nới) |
| NQZ26 phiên 2026-11-10 | 102,717 | 21 | 1233 | 2 | 27707,50 – 27753,75 · 27717,75 · 0,134 · 6,2 · ×1,70 (qua nhờ ≥ 12 %, không nổi bật) |
| NQZ26 phiên 2026-11-13 | 104,413 | 21 | 1253 | 2 | 27794,50 – 27841,50 · 27811,75 · 0,134 · 6,2 · ×2,14 |
| NQZ26 phiên 2026-11-17 | 123,886 | 25 | 1487 | 2 | 26946,25 – 27002,00 · 26977,25 · 0,195 · 9,0 · ×3,12 |
| NQZ26 phiên 2026-11-11 (nới bị chặn, hộp hẹp hơn đích) | 73,201 | 15 | 878 | 2 | 28345,50 – 28378,50 · 28366,75 · 0,106 · 4,9 · ×2,02 |
| NQZ26 phiên 2026-10-08 (hai hộp) | 72,609 | 15 | 871 | 2 | 31220,50 – 31253,25 · 31246,75 · 0,171 · 7,9 · ×4,77 ; 30921,75 – 30954,50 · 30933,50 · 0,115 · 5,3 · ×3,47 |
| NQZ26 tuần 2026-10-11 → 10-16 (bốn hộp) | 70,454 | 14 | 845 | 4 | 30755,00 – 30786,75 ; 30140,50 – 30176,75 ; 29806,50 – 29843,00 ; 29375,50 – 29403,75 |
| NQZ26 tuần 2026-11-08 → 11-13 | 102,667 | 21 | 1232 | 3 | 28340,00 – 28386,25 · 28354,75 · 0,065 · 14,9 · ×2,01 |
| GCZ26 phiên 2026-10-29 | 11,430 | 6 | 343 | 2 | 4034,5 – 4040,6 · 4037,6 · 0,307 · 14,1 · ×3,87 (không đổi so với mục 10) |
| GCZ26 phiên 2026-11-05 | 15,363 | 8 | 461 | 2 | 4131,2 – 4138,2 · 4134,3 · 0,201 · 9,2 · ×2,34 (mục 10: hai hộp) |
| GCZ26 phiên 2026-11-03 | 10,241 | 5 | 307 | 2 | không có |
| GCZ26 phiên 2026-10-28 | 9,496 | 5 | 285 | 2 | 4058,7 – 4063,0 · 4060,3 · 0,179 · 8,2 · ×2,52 (mục 10 lấy thềm 4051,3 – 4055,0) |
| GCZ26 phiên 2026-11-02 (hai hộp) | 10,678 | 5 | 320 | 2 | 3966,5 – 3971,4 · 3969,5 · 0,142 ; 3906,6 – 3911,5 · 3909,5 · 0,147 |
| GCZ26 tuần 2026-10-25 → 10-30 | 10,370 | 5 | 311 | 3 | 4030,2 – 4040,3 · 4037,5 · 0,155 · 35,6 · ×1,79 (qua nhờ ≥ 8 %, không nổi bật) |
| GCZ26 tuần 2026-08-16 → 08-21 (ba hộp) | 12,286 | 6 | 369 | 4 | 4542,8 – 4548,4 ; 4447,7 – 4453,3 ; 4637,4 – 4642,9 |
| GCZ26 tuần 2026-08-09 → 08-14 | 11,931 | 6 | 358 | 2 | không có |

**b. Ca dựng tay** (số kỳ vọng lấy bằng cách chạy `hvn_cum2.clusters` trên đúng dãy dựng tay rồi chép vào test). Các ca của 10.5 b viết lại theo luật mới, thêm:
- Lõi hẹp, hai sườn thoải ⇒ hộp nới đúng tới `HvnWidth × up`, phía dày hơn được lấy trước; hoà thì lấy phía giá thấp.
- Sườn tụt dưới 50 % đỉnh trước khi đủ rộng ⇒ nới dừng ở đó, hộp hẹp hơn đích.
- Bướu bên cạnh cách một đáy: nới dừng trước khi leo quá đáy + 5 % đỉnh.
- Hai bướu cách nhau dưới 3 up ⇒ chỉ bướu cao thành hộp; cách nhau trên 3 up ⇒ hai hộp.
- Bướu nhỏ (cao 30 % đỉnh lớn nhất) nằm xa, xung quanh mỏng, chứa ≥ 4,5 nến ⇒ thành hộp (nhánh nổi bật); cùng bướu đó đặt giữa vùng dày ⇒ không.
- Hộp ≥ `massMin` nhưng không nổi bật ⇒ vẫn nhận (nhánh lớn).
- Profile rộng 13 up ⇒ tối đa 2 hộp; 19 up ⇒ 3; 30 up ⇒ 4.
- `HvnBoxes`: hộp cách giá 7,9 U được vẽ, 8,1 U không; ba hộp cùng phía ⇒ giữ hai hộp gần; hộp ngày trùng hộp tuần ⇒ một hộp nhãn `HVN ngày + tuần`.

**c. Cả bộ máy — `fixture/expected_cum2.json`** thay `expected_cum.json` (cùng `m30_bars.csv`, `m30_levels.csv.gz`; 689 ca; 357 điểm va đập không đổi). Thêm trường `hvn_boxes[{name, lo, hi, peak, mass, label}]` mỗi ca = kết quả `HvnBoxes` với giá = `now`. Trong 689 ca: 232 ca có vùng vàng được vẽ (bản mục 10: 128), 393 ca có vùng dính HVN, trung bình 2,49 hộp HVN được vẽ (nhiều nhất 5).

Năm ca ghi số (thay bảng ở 10.5 c):

| Ca | j · giờ UTC · giá | Vùng được vẽ | Hộp HVN được vẽ |
|---|---|---|---|
| A | 1342 · 2026-10-30 02:00 · 4015,3 | `4020,6–4024,7` đỏ `Kháng cự · 4 lần · HVN ngày`; `4026,4–4028,6` đỏ `Kháng cự · 3 lần · HVN ngày + VAL hôm qua + VWAP hôm qua −1σ`; `4038,8–4042,0` vàng `★ Kháng cự rất mạnh · 3 lần · HVN tuần + HVN ngày + VAL tuần trước + VWAP hôm qua` | 4007,6–4012,6 ; 4021,8–4025,9 ; 4028,5–4032,7 (đều HVN ngày) |
| B | 1042 · 2026-10-21 13:00 · 4155,3 | `4145,0–4148,3` xanh `Hỗ trợ · 3 lần · VWAP hôm qua`; `4158,4–4162,2` đỏ `Kháng cự · 3 lần · VAL tuần trước + VWAP hôm qua +1σ`; `4163,9–4168,1` đỏ `Kháng cự · 4 lần · HVN ngày + VAL tuần trước`; `4174,3–4177,7` vàng `★ Kháng cự rất mạnh · 5 lần · HVN tuần + HVN ngày + VWAP tuần trước` | 4113,9–4118,4 `HVN ngày + tuần` ; 4165,8–4172,0 ; 4173,6–4177,9 |
| C | 935 · 2026-10-19 05:30 · 4204,8 | `4174,8–4178,6` vàng `★ Hỗ trợ rất mạnh · 6 lần · HVN tuần + HVN ngày + VWAP tuần trước`; `4192,0–4194,0` xanh `Hỗ trợ · 3 lần · HVN ngày + VWAP hôm qua`; `4197,2–4200,5` xanh `Hỗ trợ · 3 lần · HVN ngày`; `4206,7–4209,6` đỏ `Kháng cự · 4 lần · HVN ngày + VWAP tuần trước +1σ` | 4177,7–4182,2 `HVN tuần` ; 4192,6–4196,4 ; 4207,3–4211,4 |
| D | 1502 · 2026-11-04 14:00 · 4043,6 | `4059,4–4062,8` đỏ `Kháng cự · 3 lần · HVN ngày` | 3966,5–3971,4 ; 4030,2–4040,3 `HVN ngày + tuần` ; 4058,7–4063,0 |
| E | 1238 · 2026-10-27 19:00 · 4073,9 | `4032,3–4036,3` xanh `Hỗ trợ · 5 lần · HVN ngày + VWAP hôm qua +1σ`; `4042,4–4046,3` xanh `Hỗ trợ · 4 lần · VAL tuần trước` | 4007,6–4012,6 ; 4028,5–4032,7 ; 4103,5–4108,8 ; 4140,6–4145,2 `HVN ngày + tuần` |

**d. NQZ26 — `fixture/nq_expected2.json`** thay `nq_expected.json` (cùng `nq_m30_bars.csv`, `nq_m30_levels.csv.gz`; `splice_jump = 0` — bộ chặn chỗ nối **tắt**, đúng như indicator chạy trên NQZ26; bản cũ để 50 điểm nên mất lịch sử trước 23/11). 13 ca: nến đóng giờ chẵn ngày 2026-11-24 và nến áp chót. Ca cuối (`2026-11-24 11:30`, giá 26.442,75, U 143,467):
- mức HVN: ngày 26801,50–26876,50 · **25538,50–25609,75** · 27664,75–27750,50 · 27143,00–27206,25 · 26946,25–27002,00; tuần trước 27239,25–27299,00 · **25544,25–25604,00**; tất cả đủ "rời xa";
- vùng được vẽ: `26909,00–26959,00` đỏ `Kháng cự · 5 lần · HVN ngày + VAH hôm qua`;
- hộp HVN được vẽ: `25538,50–25609,75` nhãn `HVN ngày + tuần` (cách giá 5,81 U — với bán kính 4 U cũ sẽ không vẽ) ; `26801,50–26876,50` ; `26946,25–27002,00`.

**e. Kiểm tay trên Quantower:** chart NQZ26 ⇒ hộp `HVN ngày + tuần` 25538,50 – 25609,75 và hộp `HVN ngày` 26801,50 – 26876,50. Chart GCZ26 phiên 2026-10-29 ⇒ 4034,5 – 4040,6.

Sinh lại: `python hvn_cum2_fixture.py` (cần `prep1.py gc`, `prep1.py nq`). Sau khi C# PASS: xoá `hvn_cum_cases.json`, `expected_cum.json`, `nq_expected.json` và test đọc chúng.

### 13.6 Việc của Opus

1. `StrongZoneParams`: hằng 13.1, xoá `HvnSecond`. `SzHvnBox` thêm `CoreLo`, `CoreHi`.
2. `HvnClusters`: thêm `nBars`, viết lại vòng lặp theo 13.2; cả hai overload; `AddHvn` truyền `nBars`.
3. `HvnBoxes`: bán kính riêng, trần mỗi phía, nhãn gộp (13.4). Nhãn trên chart: `HVN ngày + tuần · 11 % khối lượng` (số % của hộp được giữ).
4. Test 13.5 a–d; test cũ không liên quan HVN phải PASS không sửa kỳ vọng.
5. Build `./build-tpo.sh zones`, kiểm tay 13.5 e trên 4 khung M1/M5/M15/M30.

### 13.7 Cần người dùng chốt (đều đã đo, xem HVN-CUM-V2.md)

1. **Hộp đổi chỗ ở một phần số phiên** so với bản đang chạy: trong các phiên bản cũ có hộp, NQ 7/36 phiên và GC 13/45 phiên hộp chuyển sang chỗ khác hoặc mất; thêm NQ 13 phiên, GC 20 phiên trước không có hộp nay có. Lý do chính: mỗi vùng ± 3 up giờ chỉ lấy đỉnh cao nhất, nên hộp "thứ hai" và hộp nằm ở thềm dưới một đỉnh nhọn không còn. Xem ảnh lưới trước/sau.
2. **Vùng vàng trên GC tăng từ 15 % lên 23 % thời gian** (NQ giảm 19 % → 15 %), vì profile tuần giờ có nhiều hộp hơn và một cụm thường được đếm hai lần (HVN ngày + HVN tuần). Phương án đã đo: coi HVN ngày và HVN tuần là **một** nhóm khi đếm "≥ 3 nhóm" ⇒ vàng còn GC 10,5 %, NQ 6,8 %. Đây là đổi luật vàng gốc nên **chưa đưa vào spec**; fixture sinh theo luật hiện tại.
3. **Đáy/đỉnh tuần làm mức hợp lưu**: mở rộng so với yêu cầu gốc, đã đo thử, mẫu quá nhỏ (GC 38 lệnh, NQ 20 lệnh) ⇒ **chưa đưa vào spec**.
