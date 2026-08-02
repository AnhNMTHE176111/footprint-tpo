# PLAN — Sửa EntrySignal (M1) v2 theo review chart của người học

Ngày lập: 2026-08-02 · Người lập: Claude · Trạng thái: **CHƯA implement** (plan để chuyển model khác code)

Nguồn đầu vào:
- Danh sách lệnh: [ENTRY SIGNAL (M1)_2026-08-02.csv](../data-export/signals/ENTRY%20SIGNAL%20(M1)_2026-08-02.csv) — 11 lệnh, 17/07→31/07.
- Review chart của người học: [rule-entry/entry-signal-images/](../rule-entry/entry-signal-images/) — 6 ảnh.
- Code đang ship: [EntrySignal.cs](../quantower-entry-signal/EntrySignal.cs) · bản song sinh Python: [entry_month.py](../quantower-entry-signal/research/entry_month.py)

> **Quy ước giờ:** CSV ghi giờ **UTC**; chart trong ảnh ghi giờ **VN (UTC+7)**. Giờ chart = giờ CSV + 7.

---

## 1. Đối chiếu 6 ảnh review ↔ dòng CSV

| Ảnh | Giờ trên chart (VN) | Giờ UTC | Loại | Dòng CSV | Kết luận của người học |
|---|---|---|---|---|---|
| [image copy 4.png](../rule-entry/entry-signal-images/image%20copy%204.png) | 31/07 14:30 | 31/07 07:30 | Lệnh SL | dòng 7 — LONG 4129.9, VSA 2.9x, climax | "nến entry vẫn là nến **đỏ**, chưa đủ điều kiện thuận chiều rút râu. Cần 1 nến tăng để xác nhận làm nến entry" |
| [image copy.png](../rule-entry/entry-signal-images/image%20copy.png) | 01/08 00:29 | 31/07 17:29 | Lệnh SL | dòng 9 — SHORT 4106.6, VSA 8.9x, climax | "nến vẫn là nến **ngược** xu hướng rút râu. Phải cần nến xác nhận thuận xu hướng thì nến xác nhận đó mới là nến entry" |
| [image.png](../rule-entry/entry-signal-images/image.png) | 01/08 02:34 | 31/07 19:34 | Lệnh SL | dòng 11 — SHORT 4106.2, VSA 4.4x, climax | "xu hướng giảm, nến entry lại là nến **tăng** → phải cần 1 nến giảm để xác nhận" |
| [image copy 5.png](../rule-entry/entry-signal-images/image%20copy%205.png) | 31/07 14:37 | 31/07 ~07:37 | **Bỏ sót** | — | "Phá range, hồi lại, hồi lại **yếu vẫn loanh quanh range, ko bứt hẳn lên**. Nến entry: giảm mạnh, VSA ≥ high (climax tím), delta âm, có **stack imbalance** giảm" |
| [image copy 2.png](../rule-entry/entry-signal-images/image%20copy%202.png) | 31/07 ~22:45 | 31/07 ~15:45 | **Bỏ sót** | — | "Rút râu vùng hợp lưu → **chờ nến thuận chiều rút râu có VSA high ⇒ nến entry**. Nến entry có delta dương (+23)". Entry 4098.4 / SL 4094.9 / TP 4108.9 |
| [image copy 3.png](../rule-entry/entry-signal-images/image%20copy%203.png) | ~19:35 (chưa rõ ngày) | ? | **Bỏ sót** | — | "**Phá range dưới, hồi lại**. Nến entry có delta đỏ (−109), VSA = tím > high". Entry 4104.2 / SL 4108.1 / TP 4092.2 |

> ⚠️ **Việc cần người học xác nhận trước khi implement:** ngày + giờ chính xác (UTC) của 3 ca bỏ sót,
> nhất là ảnh `image copy 3.png` (ảnh không hiện ngày). Không có mốc này thì không viết được test hồi quy
> cho ca bỏ sót.

---

## 2. Bốn lỗi tìm được (2 lỗi người học chỉ ra, 2 lỗi Claude tìm thêm)

### Lỗi A — Nến entry được phép NGƯỢC MÀU với hướng lệnh *(3/3 ảnh lệnh SL đều là lỗi này)*

**Nguyên nhân gốc** — [EntrySignal.cs:689-714](../quantower-entry-signal/EntrySignal.cs#L689-L714):

```
LongSignal:  ur = LW ≥ WickFrac*Rng  &&  Cpos ≥ 0.55  &&  Delta ≥ 0
ShortSignal: dr = UW ≥ WickFrac*Rng  &&  Cpos ≤ 0.45  &&  Delta ≤ 0
```

Nhánh "rút râu" (`ur`/`dr`) **không hề kiểm thân nến** (`C` so với `O`). Một nến rút râu dưới nhưng
đóng cửa **thấp hơn** mở cửa (nến đỏ) vẫn thoả `ur` → bắn LONG. Đó chính xác là 3 ca SL đã review.

Nhánh "thân mạnh" (`su`/`sd`) thì đã ngầm thuận màu (`Brat ≥ 0.55` + `Cpos ≥ 0.6` + `Delta > 0`), nên
lỗi chỉ nằm ở nhánh rút râu.

**Luật đúng theo người học:** nến rút râu = tín hiệu **chuẩn bị (ARM)**, không phải lệnh.
Nến ENTRY phải **thuận chiều lệnh** (`C > O` cho LONG, `C < O` cho SHORT). Nếu nến rút râu tự nó đã
thuận chiều → nó chính là nến entry (vào ngay, như hiện tại). Nếu ngược chiều → **chờ** nến kế thuận
chiều và đủ điều kiện (VSA ≥ High, delta thuận) thì mới vào.

### Lỗi B — Bỏ sót "phá & hồi" khi nhịp hồi chui ngược lại vào range

**Nguyên nhân gốc** — [EntrySignal.cs:579-590](../quantower-entry-signal/EntrySignal.cs#L579-L590):

```csharp
if (z.State == "broke_dn" ...) {
    if (b.C > zp + buf * _tick) z.State = "idle";        // ❶ chỉ 1 nến đóng trên vùng +2 tick là HUỶ setup
    else if (b.H >= zp - RetestTol*_tick && b.H <= zp + RetestHoldBuf*_tick   // ❷ RetestHoldBuf = 0
             && ShortSignal(b, ...))                                          // ❸ CÙNG 1 nến vừa chạm vừa phải là nến tín hiệu
```

Ba chỗ chặn cộng lại:
- ❶ `RetestBars = 12` nến + huỷ ngay khi đóng vượt vùng 2 tick → đúng ca ảnh 5 mô tả ("hồi lại yếu
  **vẫn loanh quanh range**, ko bứt hẳn lên") bị giết trước khi nến entry xuất hiện.
- ❷ `RetestHoldBuf = 0` → nhịp hồi chỉ nhô 1 tick qua vùng là mất tín hiệu.
- ❸ Bắt buộc **một nến** vừa chạm vùng vừa là nến tín hiệu. Thực tế nến chạm và nến động lượng thường
  là **hai nến khác nhau** — cùng gốc với lỗi A.

### Lỗi C — Cơ chế ARM→CONFIRM đã có nhưng đang TẮT và đặt sai điều kiện

[EntrySignal.cs:608-635](../quantower-entry-signal/EntrySignal.cs#L608-L635) có sẵn KB4 arm→confirm nhưng:
- `EnableS4ArmConfirm = false` (mặc định tắt, lý do ghi trong code: edge chỉ +0.15R@1.5R);
- điều kiện CONFIRM **khắt khe hơn** mô tả của người học: KB4 đòi `Brat ≥ BodyStrong(0.55)` **và**
  `Cpos ≥ 0.6`; người học chỉ đòi *thuận chiều + VSA ≥ High + delta thuận* (ảnh `image copy 2.png`:
  nến entry chỉ có delta +23, không mô tả là "thân mạnh");
- KB4 là **kịch bản CỘNG THÊM** (sinh thêm lệnh), còn cái người học muốn là **SỬA nến entry của
  KB1/KB2 hiện có** (dời/huỷ lệnh, không sinh thêm). Đây là khác biệt quan trọng: kết quả backtest cũ
  của KB4 **không** áp dụng được cho fix này.

### Lỗi D — Bắn lặp nhiều lệnh cùng một mức sau khi đã thua *(Claude tìm thêm, người học chưa nêu)*

Trong CSV, 4/11 lệnh là SHORT tại **cùng mức 4106.2–4106.7** trong 3 giờ: 17:29, 18:41, 19:34, 20:33
(dòng 9–12). Ba lệnh đã đóng đều LOSS. `Cooldown = 15` nến không chặn được vì các lệnh cách nhau 60+ nến.
→ đề xuất thêm **khoá vùng sau N lần thua** (chi tiết ở mục 3.4). Đây là ý của Claude, **chưa có bằng
chứng backtest**, nên phải để mặc định TẮT cho tới khi đo xong.

### Thiếu tính năng — stacked imbalance

Người học nêu ở ảnh `image copy 5.png`: *"Footprint: delta âm, có **stack imbalance** giảm"*.
Grep toàn repo: **không indicator nào có imbalance/stacked imbalance**. Có thể tính live từ
`bar.VolumeAnalysisData.PriceLevels` (chỗ [Absorption()](../quantower-entry-signal/EntrySignal.cs#L671-L687) đang đọc).

---

## 3. Thiết kế fix

### 3.1 Fix A+B+C gộp thành MỘT cơ chế: ARM → CONFIRM cho nến entry

Thay vì `Emit` ngay tại nến kích hoạt, đưa vào trạng thái chờ trên từng vùng.

**Tham số mới** (thêm vào block Input Parameters, quanh [dòng 54-114](../quantower-entry-signal/EntrySignal.cs#L54-L114)):

| Tham số | Kiểu | Mặc định đề xuất | Ý nghĩa |
|---|---|---:|---|
| `RequireEntryBodyDir` | bool | `true` | Nến vào lệnh phải thuận chiều (`C>O` cho LONG, `C<O` cho SHORT) |
| `ConfirmWindow` | int | `3` | Số nến tối đa chờ nến xác nhận sau nến ARM |
| `ConfirmVsa` | double | `1.2` | VSA tối thiểu của nến xác nhận (= VsaGate) |
| `ConfirmNeedDelta` | bool | `true` | Delta nến xác nhận phải thuận chiều lệnh |
| `ConfirmAnchorMode` | enum/int | `0` | 0 = SL neo theo cực trị nến ARM; 1 = neo theo cực trị của cả cụm ARM→CONFIRM |

**Trạng thái mới trên `PZone`** (thêm cạnh `ArmLBar/ArmSBar` tại [dòng 356](../quantower-entry-signal/EntrySignal.cs#L356)):

```csharp
public int PendBar = -999;      // nến ARM
public int PendSide;            // +1 / -1
public double PendAnchor;       // cực trị dùng neo SL
public double PendZonePrice;    // giá vùng lúc arm (VWAP là vùng động → phải chốt lại)
public string PendScen; public char PendGrade; public List<string> PendWhy;
```

**Luồng xử lý mỗi nến `i`, mỗi vùng `z`** (giữ nguyên thứ tự ưu tiên KB1 → KB2 hiện có):

```
1. XỬ LÝ PENDING TRƯỚC (nếu z.PendBar >= 0):
   a. Hết hạn: nếu i - z.PendBar > ConfirmWindow  → xoá pending.
   b. Vô hiệu: nếu nến i đóng xuyên vùng NGƯỢC hướng lệnh quá SlBuf
        (LONG: b.C < zp - SlBuf*tick | SHORT: b.C > zp + SlBuf*tick)  → xoá pending.
   c. Vô hiệu: nếu cực trị nến i đã phá qua PendAnchor (LONG: b.L < PendAnchor) → xoá pending
        (setup đã sai, không đuổi theo).
   d. XÁC NHẬN: nếu  huong_than(b) == PendSide
                && b.Vratio >= ConfirmVsa
                && (!ConfirmNeedDelta || dau(b.Delta) == PendSide)
        → Emit(i, PendSide, PendScen + " (xác nhận)", anchor, PendWhy + ["xác nhận N nến"], PendGrade, PendZonePrice)
          rồi z.Cool = i; z.State = "idle"; xoá pending.

2. KB1 / KB2 như hiện tại, NHƯNG thay chỗ gọi Emit(...) bằng:
     if (!RequireEntryBodyDir || huong_than(b) == side)   → Emit ngay (hành vi cũ)
     else                                                 → ĐẶT PENDING (arm), không Emit.

   huong_than(b) = +1 nếu b.C > b.O; -1 nếu b.C < b.O; 0 nếu doji (0 KHÔNG khớp side nào → arm).
```

**Chi tiết quan trọng, dễ sai:**
- Cổng hợp lưu (`ClusterCount ≥ MinConfluence` trong [Emit()](../quantower-entry-signal/EntrySignal.cs#L757)) phải được tính **tại nến CONFIRM**, không phải tại nến ARM — vùng có thể hết hạn giữa chừng.
- Vùng VWAP là **động** (giá đổi mỗi nến, [dòng 537](../quantower-entry-signal/EntrySignal.cs#L537)). Phải chốt `PendZonePrice` lúc arm, không đọc `z.Price` lúc confirm.
- Không đụng vào `LongSignal`/`ShortSignal` — giữ nguyên để `RequireEntryBodyDir=false` tái lập chính xác hành vi cũ (cần cho A/B).
- KB4 (`EnableS4ArmConfirm`) giữ nguyên, độc lập — **không** trộn hai cơ chế.

### 3.2 Fix B — nới điều kiện nhịp hồi của KB1

**Tham số mới / đổi mặc định:**

| Tham số | Hiện tại | Đề xuất | Ghi chú |
|---|---:|---:|---|
| `RetestKillBuf` (mới) | — (đang dùng `SlBuf`=2) | quét 2 / 10 / 20 tick | Chỉ huỷ `broke_*` khi đóng nến vượt ngược qua vùng **quá** ngần này |
| `RetestBars` | 12 | quét 12 / 18 / 24 | Cho nhịp hồi "loanh quanh range" lâu hơn |
| `RetestHoldBuf` | 0 | quét 0 / 3 / 6 | ⚠️ research cũ kết luận 0 là tốt nhất ([EntrySignal.cs:84](../quantower-entry-signal/EntrySignal.cs#L84)) — nếu quét lại vẫn ra 0 thì **giữ 0**, đừng nới chỉ vì 1 ảnh |

Sửa tại [EntrySignal.cs:581](../quantower-entry-signal/EntrySignal.cs#L581) và [:588](../quantower-entry-signal/EntrySignal.cs#L588): đổi `buf` trong nhánh huỷ state thành `RetestKillBuf`.

### 3.3 Fix — Stacked imbalance (tính năng mới, mặc định TẮT)

Thêm hàm cạnh [Absorption()](../quantower-entry-signal/EntrySignal.cs#L671):

```csharp
// Imbalance chéo (chuẩn footprint): so ask(p) với bid(p - 1 tick).
//   mua : ask(p)      >= ImbRatio * bid(p-1tick)  && ask(p)      >= ImbMinVol
//   bán : bid(p-1tick)>= ImbRatio * ask(p)        && bid(p-1tick)>= ImbMinVol
// Stacked = >= ImbStack mức LIÊN TIẾP cùng chiều.
private bool StackedImbalance(HistoryItemBar bar, int side)
```

Tham số: `ImbRatio = 3.0`, `ImbMinVol = 5`, `ImbStack = 3`, cờ `RequireStackImb = false`.

> ⚠️ Không thể backtest offline với dữ liệu hiện có: [data-footprint/Data_Footprint_Export.csv](../data-export/data-footprint/Data_Footprint_Export.csv)
> là **khung M30**, 30/06→30/07, không phải M1. Muốn đo offline phải chạy lại FootprintExport ở **M1**.
> Trước khi có số: **để cờ TẮT**, chỉ ghi vào cột `chi_tiet` của CSV để quan sát.

### 3.4 Fix D — khoá vùng sau N lần thua *(ý Claude, mặc định TẮT)*

Tham số: `ZoneLossLock = 2` (số lệnh thua liên tiếp), `ZoneLockBars = 240` (cửa sổ ~4 giờ),
cờ `EnableZoneLossLock = false`.

`Simulate()` ([dòng 817](../quantower-entry-signal/EntrySignal.cs#L817)) đã tính sẵn outcome của lệnh đã đóng
→ đếm được. Khoá theo **giá vùng làm tròn `ConfluenceTol`** để 4106.2 và 4106.7 tính là cùng một mức.

---

## 4. Kế hoạch test

### 4.1 Dữ liệu cần bổ sung — LÀM TRƯỚC, không có thì không test được đúng ca đã review

| Việc | Lý do |
|---|---|
| **Xuất lại M1 có delta cho 01/07 → 02/08/2026**, cùng format [fp-m1-1-month-data.csv](../data-export/fp-m1-1-month-data.csv) | File delta hiện có chỉ tới **25/07** — cả 6 ca review (29/07–31/07) đều **nằm ngoài** dữ liệu. Không có file này thì không replay được. |
| Xuất lại TPO daily cho cùng cửa sổ | [TPO-chart-daily.csv](../data-export/TPO-chart-daily.csv) chỉ phủ 25/06→25/07 → vùng D-1 sẽ thiếu |
| *(chỉ khi muốn test imbalance)* FootprintExport khung **M1** cho cửa sổ trên | bản có sẵn là M30 |

### 4.2 T0 — test hồi quy 6 ca review (viết TRƯỚC khi sửa code)

Tạo `quantower-entry-signal/research/entry_review_cases.py`: danh sách 6 ca (giờ UTC, hướng, entry/SL/TP kỳ vọng).
Chạy trên code **chưa sửa** → phải tái hiện đúng:
- 3 ca SL **có bắn** (7/31 07:30 LONG · 17:29 SHORT · 19:34 SHORT UTC);
- 3 ca bỏ sót **không bắn**.

Nếu không tái hiện được ⇒ dữ liệu hoặc cấu hình chưa khớp live, **dừng lại xử lý trước khi sửa logic**.
(Cấu hình live đọc ngược từ CSV: `RR = 3`, SL ≈ 3.5 giá ⇒ `SlFloor ≈ 3.5`, khác mặc định trong code là
`RR=1.5`/`SlFloor=4.0` — phải hỏi người học lấy đúng cấu hình đang chạy.)

### 4.3 T1 — A/B trong Python trước, C# sau

Bản song sinh Python là [entry_month.py](../quantower-entry-signal/research/entry_month.py) (cùng máy trạng thái với C#).
Cài từng fix, đo **riêng lẻ rồi mới gộp**, trên 3 bộ dữ liệu:

| Bộ | File | Có delta? | Vai trò |
|---|---|:---:|---|
| 28 ngày | `fp-m1-1-month-data.csv` (26/06→25/07) | ✅ | bộ chính |
| ~3 tháng lỏng | `fp-m1-6-month.csv` (tháng 5–7, ~31k nến có vol≥20) | ✅ | mở rộng mẫu |
| 9 tháng | `27-7/…dxFeed…11_3_2025-7_27_2026.csv` | ❌ | chỉ đo phần **cấu trúc** (KB1 retest), qua [entry_dxfeed.py](../quantower-entry-signal/research/entry_dxfeed.py) |

Báo cáo bắt buộc cho mỗi biến thể: `n`, WR, tổng R, exp R/lệnh, **tách theo KB1/KB2 và theo tháng**.

### 4.4 Tiêu chí PASS/FAIL (chốt trước khi chạy, không đổi sau khi thấy số)

- Bật mặc định một fix chỉ khi: `n ≥ 30` lệnh có kết quả **và** exp R/lệnh **cao hơn baseline** trên **≥ 2/3 bộ dữ liệu** **và** không có tháng nào bị lật từ dương sang âm.
- Không đạt ⇒ vẫn ship nhưng **cờ TẮT mặc định**, ghi rõ số đo vào `rule-entry/`.
- Mọi tham số quét (`RetestBars`, `RetestKillBuf`, `ConfirmWindow`…) phải kiểm bằng **holdout**: dò trên tháng 5–6, kiểm trên tháng 7 (hoặc ngược lại). Chênh lệch quá lớn giữa 2 nửa ⇒ coi là overfit, giữ mặc định cũ.

### 4.5 T2 — port C# + parity

- Port đúng logic đã chốt sang `EntrySignal.cs`.
- Chạy đối chiếu Python ↔ C# (khung có sẵn: [research/wyckoff/parity/](../quantower-entry-signal/research/wyckoff/parity/), [reconcile_live.py](../quantower-entry-signal/research/reconcile_live.py)) — số lệnh và giờ vào phải khớp.
- Build sạch 0 lỗi / 0 cảnh báo (`build-entry.sh`).

### 4.6 T3 — kiểm live

Deploy Quantower → chạy 1 tuần → xuất CSV → mở lại 6 ảnh review và các ca mới, đối chiếu bằng mắt.

---

## 5. Số đo sơ bộ Claude đã chạy (2026-08-02) — đọc kỹ trước khi kỳ vọng

Chạy trên `fp-m1-6-month.csv` + cổng hợp lưu ≥2, SL floor 35 tick, RR = 3 (gần cấu hình live):

**(a) Tách theo màu nến entry** — 78 lệnh:

| Nhóm | n | WR@3R | Tổng R | exp R/lệnh |
|---|---:|---:|---:|---:|
| Tất cả | 78 | 28.6% | +11.0 | +0.14 |
| Nến entry **thuận màu** | 53 | 30.8% | +12.0 | **+0.23** |
| Nến entry **ngược màu** | 19 | 21.1% | −3.0 | **−0.16** |
| Doji | 6 | 33.3% | +2.0 | +0.33 |

→ Hướng đúng như người học nói, nhưng **n = 19, chưa đủ để kết luận**.

**(b) Thử "chờ nến xác nhận" (thay vì bỏ lệnh) — kết quả XẤU trên mẫu này:**
trong 25 ca ngược màu/doji, chỉ 4–6 ca tìm được nến xác nhận, và **tất cả đều thua**
(exp −1.00R). Bỏ hẳn lệnh ngược màu (+0.23R) tốt hơn chờ xác nhận (+0.14R).

**(c) Quét lại nhịp hồi KB1** (chỉ nhánh KB1, n = 13–23):

| RetestKillBuf | RetestBars | n | WR | Tổng R | exp |
|---:|---:|---:|---:|---:|---:|
| 2 (hiện tại) | 12 (hiện tại) | 16 | 31.2% | +4.0 | +0.25 |
| 2 | **24** | 21 | 42.9% | +15.0 | **+0.71** |
| 10 | 24 | 22 | 40.9% | +14.0 | +0.64 |
| 20 | 24 | 23 | 39.1% | +13.0 | +0.57 |

→ Cái ăn tiền là **`RetestBars` 12 → 24**, không phải `RetestKillBuf`. Nhưng n = 16→21, **rất nhỏ** và
rất dễ là overfit — bắt buộc kiểm holdout ở bước 4.4.

**Nói thẳng:** không có số nào ở trên đủ mạnh để hứa cải thiện. Chúng chỉ đủ để nói *hướng sửa hợp lý* và
*phải test lại trên dữ liệu 26/07→02/08 mới lấy về*. Ba ca SL đã review thì fix A chắc chắn tránh được —
nhưng ba ca không phải là bằng chứng thống kê.

---

## 6. Thứ tự triển khai đề nghị

1. **[Người học]** Xuất dữ liệu ở mục 4.1 + xác nhận giờ UTC của 3 ca bỏ sót + gửi cấu hình EntrySignal đang chạy live.
2. Viết `entry_review_cases.py` (T0), chạy trên code cũ → tái hiện đúng 3 bắn / 3 sót.
3. Cài **Fix A** (`RequireEntryBodyDir` + ARM→CONFIRM) trong Python, A/B theo 4.3–4.4.
   Đo riêng 2 biến thể: **A1 = bỏ hẳn lệnh ngược màu** · **A2 = chờ nến xác nhận**. Số hiện có nghiêng về A1.
4. Cài **Fix B** (`RetestKillBuf`, `RetestBars`, `RetestHoldBuf`) trong Python, quét + holdout.
5. Gộp A+B, đo lại, chốt bộ mặc định.
6. Port C# + parity + build sạch (4.5).
7. Thêm **stacked imbalance** và **khoá vùng sau N lần thua** dưới dạng cờ **TẮT**, chỉ ghi ra CSV để quan sát.
8. Cập nhật [rule-entry/EntrySignal-cau-hinh-va-kich-ban.md](../rule-entry/EntrySignal-cau-hinh-va-kich-ban.md) + `progress.md`, commit + push.

## 7. Cạm bẫy đã biết

- **Không sửa `LongSignal`/`ShortSignal` tại chỗ** — giữ nguyên để tắt cờ là về đúng hành vi cũ, phục vụ A/B.
- **VWAP là vùng động** — phải chốt giá vùng lúc ARM.
- **Cổng hợp lưu tính tại nến CONFIRM**, không phải nến ARM.
- **`Cooldown` đang tính theo nến** — sau khi thêm pending, nhớ set `z.Cool` tại nến CONFIRM (không phải ARM), nếu không sẽ bắn chồng.
- **Repaint** — vòng quét bỏ nến đang hình thành ([`nClosed = B.Count - 1`](../quantower-entry-signal/EntrySignal.cs#L536)). Pending phải chỉ dùng nến đã đóng, giữ nguyên tính chất này.
- `entry_month.py` **chưa có** cổng hợp lưu ≥2 (nó chỉ tính `confl` = số tín hiệu bị gộp). Khi A/B phải tự thêm `ClusterCount` như C#, nếu không số sẽ lệch ~5 lần (323 lệnh vs 66 lệnh).
