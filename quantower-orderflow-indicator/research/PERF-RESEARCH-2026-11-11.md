# PERF-RESEARCH 2026-11-11 — vì sao indicator "OrderFlow Bubbles" LOAD CHẬM và cách làm nhanh mà KHÔNG đổi kết quả

> Phạm vi: CHỈ ĐỌC + ĐO. Không sửa `OrderFlowBubbles.cs`, `CellBigLogic.cs`, không commit.
> Mọi số `[ĐO]` lấy từ harness chạy trên máy này (20 lõi, .NET 10.0.12, Release) với dữ liệu thật
> `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv` (87.362 nến M1, 1.569.296 ô giá, TB 18 ô/nến, max 510).
> Mọi chỗ `[SUY LUẬN]` là suy ra từ đọc code / quan sát gián tiếp, CHƯA đo được vì nằm trong nội bộ Quantower.
> Harness: `C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\14112285-cd5a-4717-90f2-b4fe405421be\scratchpad\perf\`
> (`Engine.cs` = bản port trung thực ComputeBar/Process có cờ bật từng tối ưu; `Robust.cs`; `Ctx.cs`; `Program.cs`; `paint/` = đo GDI+). Chạy: `dotnet out/Harness.dll robust|engine|ablate|persist|live|cache|mem|refl`.

---------------------------------------------------------------------------------------------------

## 0. TÓM TẮT

Chi phí lớn nhất phụ thuộc **đường nào** indicator đi qua khi nạp:

| Kịch bản (87.362 nến) | Hiện tại | Sau tối ưu | Ghi chú |
|---|---|---|---|
| **Nguội (cold)**: cache không khớp dấu vân tay tham số (đổi tham số / bump `cellbig-v3`) → tính lại + niêm phong | **34,3 s** `[ĐO]` | **2,9 s** `[ĐO]` | 25,4 s riêng là `File.AppendAllText` mỗi nến (108.636 lần × 234 µs) |
| Nguội, bỏ qua ghi file (chỉ tính) | 5,8 – 7,0 s `[ĐO]` | 1,2 – 1,3 s `[ĐO]` | tính toán thuần |
| **Ấm (warm)**: đọc file cache + khôi phục | đọc 0,73 s (lần đầu trong process 1,65 s) + Process 0,92 s `[ĐO]` | đọc 0,37 – 0,48 s + Process 0,42 s `[ĐO]` | |
| Mỗi tick/OnUpdate sống | 11,4 µs `[ĐO]` | 4,4 µs `[ĐO]` | không phải điểm nghẽn |

=> Nếu người dùng thấy "load rất chậm" (chục giây), nguyên nhân khả dĩ nhất là **đường nguội sau mỗi lần đổi tham số/cập nhật bản DLL** (dấu vân tay đổi → mọi nến tính lại + ghi file từng nến), cộng thời gian Volume Analysis do chính Quantower nạp (không đo được). Đường ấm chỉ ~1,7 s trong harness.

Tất cả tối ưu dưới đây đã được kiểm **y hệt kết quả**: so chuỗi `Digest()` (mọi bóng: giá, hình, màu, cỡ, SizeFrac, tooltip, Confirm, PriceHi + mọi vùng stacked: Idx/EndIdx/End) giữa bản gốc và bản tối ưu trên 87.362 nến: `identical=True` ở **mọi** tổ hợp (xem §6); `RollingRobust` mới so từng bit 1.000.000 phép (`Median`, `ModZ`) trên 5 kiểu dữ liệu: 0 sai lệch.

---------------------------------------------------------------------------------------------------

## 1. LUỒNG LOAD VÀ THREAD

```
Quantower
 ├─ (A) Indicator.Refresh()/Init → Update(HistoricalBar) × N        [OnUpdate :556]   (thread tính của Quantower [SUY LUẬN: tác giả đã dịch ngược, chú thích :489-494])
 │     └─ nếu VA chưa Finished → return ngay (rẻ)
 │     └─ nếu VA đã Finished và !_vaLoaded → ResetState + _vaLoaded=true  [:563]
 │     └─ Process()
 ├─ (B) VolumeAnalysisData_Loaded()  [:472]  gọi lại NHIỀU lần/phiên (chú thích :56-60)    (thread không rõ [CHƯA ĐO])
 │     └─ lock(_calcLock){ ResetState(); _vaLoaded=true }  →  Process()
 └─ (C) OnPaintChart [:1110]  (thread vẽ/UI)  — chỉ ĐỌC dưới lock(_sync) rồi vẽ ngoài lock

Process() [:569-631]  — TOÀN BỘ nằm trong lock(_calcLock)
  EnsureCvd(total)                                               :581
  EnsureCache()  — chỉ lần đầu: SignalCache.Load() đọc CẢ file jsonl   :587 → :1516-1558
  _settingsFingerprint = ComputeSettingsFingerprint()            :588   ← string.Join ~90 giá trị đóng hộp, MỖI lần gọi
  for i = processed .. closedCount-1:                            :590
      ├─ cache khớp (TimeLeft + fingerprint + FitsBar)?  :602
      │     có  → RestoreFromCache(i)       :1590   (FromCachedBarData: tạo lại List<Bubble>, thêm _exhRecs/_absRecs)
      │     không → ComputeBar(i,…)  :636  rồi PersistBar(i) :1616 → SignalCache.Put → File.AppendAllText  (:103)
      ├─ UpdateZones(i)            :1498   lock(_sync) + duyệt TOÀN BỘ _zones
      ├─ RegisterZones(i)          :1483   lock(_sync) + _zones.RemoveAll(...) quét TOÀN BỘ _zones (:1487) (+ :1492 khi >4000)
      ├─ AddToBaseline(bar)        :1403   9 baseline cuốn, có Select/ToArray
      ├─ UpdateAbsorptionConfirms  :1454   (gọi RePersistBar → AppendAllText khi chốt giữ/vỡ)
      └─ UpdateExhaustionSweeps    :992    (gọi RePersistBar khi quét; duyệt _exhRecs tới 3000 phần tử)
  nến đang chạy (total-1): ComputeBar(cur, isClosed:false) + UpdateExhaustionSweeps  :620-629   ← MỖI lần OnUpdate/tick
```

Khóa: `_calcLock` giữ suốt cả Process (kể cả vòng lịch sử dài) → mọi `OnUpdate` tick sống bị chặn trong lúc tính lại (đường nguội ~35 s). `_sync` chỉ giữ ngắn (nhưng `UpdateZones`/`RegisterZones` giữ nó trong lúc quét hết `_zones`, mỗi nến một lần → thread vẽ có thể bị chặn lặt vặt trong lúc load).

---------------------------------------------------------------------------------------------------

## 2. ĐỘ PHỨC TẠP + SỐ ĐO TỪNG BƯỚC

N = số nến, L = số ô/nến (TB 18), W = 100 (BaselineBars), Z = số vùng stacked đang giữ (tới 4000 — đo `maxZones=4000`).

### 2.1 Chia thời gian của Process nguội — bản gốc `[ĐO]` (87.362 nến, 6,0 – 7,0 s, không ghi file)

| Bước | ms | % | Dòng |
|---|---|---|---|
| ComputeBar | 4.500 – 5.500 | ~78% | 636-953 |
| UpdateZones | 540 | 8% | 1498-1511 |
| RegisterZones | 450 | 7% | 1483-1494 |
| AddToBaseline | 230 – 265 | 4% | 1403-1437 |
| UpdateExhaustionSweeps | 70 | 1% | 992-1008 |
| PersistBar (chỉ ToCachedBarData, chưa ghi file) | 70 | 1% | 1616-1622 |
| UpdateAbsorptionConfirms | 8 | ~0 | 1454-1480 |

Cấp phát bản gốc: **1.732 MB** (≈ 20 KB/nến), 147 lần GC gen0. Bản tối ưu: 531 MB, 47 lần.

### 2.2 `RollingRobust.Recompute` — thủ phạm số 1 `[ĐO]`

Chỗ: `OrderFlowBubbles.cs:1710-1723`. Mỗi khi có nến mới (`_dirty`), truy vấn đầu tiên (`Median`/`ModZ`) gom **toàn bộ** giá trị cửa sổ vào mảng mới, `Array.Sort` rồi tạo mảng `dev` và `Array.Sort` lần nữa. Có 9 đối tượng; 5 cái được truy vấn MỖI nến đóng (ComputeBar :657/:658/:699/:702/:725 + :679):

- `_rLvlVol` (top-3 ô/nến ⇒ 300 giá trị), `_rBarVol`, `_rBarAbsDelta`, `_rBarRange`, `_rBarImpact` (100 giá trị mỗi cái).
- Đo riêng (20.000 nến, W=100): `_rLvlVol`-kiểu 3 giá trị/nến **20,1 µs/nến**; kiểu 1 giá trị/nến 9,0 µs/nến ⇒ 5 cái ≈ 55 – 60 µs/nến ≈ **4,3 s / 87k nến** — khớp phần dư của ComputeBar (4,5 s → 1,0 s khi thay bộ này).
- `_rLvlSideVol` (:1426): **không có chỗ nào đọc** (grep: chỉ khai báo :143, tạo :531, `AddBar` :1426) ⇒ chỉ tốn cấp phát (`Select().ToArray()`).
- `_rLvlAbsDelta` (:1430): mảng `|Delta|` của MỌI ô nạp mỗi nến, chỉ được đọc khi `DLineEnabled` (mặc định TẮT, :368).
- `_rLvlMot`: `Median` được gọi MỖI nến (:679). Lịch sử thường mot=0 nên rỗng; nến sống có mot>0 thì cửa sổ ~W×50 giá trị: bản gốc 348 µs/nến (đo mô phỏng 50/nến). Chỉ ảnh hưởng nến sống (1 lần/phút) — không đáng kể.

### 2.3 Các điểm O(N·Z), O(N·L) khác

- `UpdateZones` :1503 duyệt cả `_zones` (Z lên 4000) mỗi nến, trong lock(_sync): **540 ms** `[ĐO]`. Phần lớn là vùng đã kết thúc (`EndIdx>=0`) bị `continue` mà vẫn phải duyệt.
- `RegisterZones` :1487 `_zones.RemoveAll(z => z.Idx == idx)` quét hết Z mỗi nến dù gần như không bao giờ có trùng: **450 ms** `[ĐO]`; :1492 thêm 1 `RemoveAll` nữa khi Z>4000.
- `ComputeBar`: `Dictionary<long,(double,VolumeAnalysisItem)> byTick` mới mỗi nến (:664); `OrderByDescending/Take/ToList` (:884-887, :895-897, :908), `new[] { true, false }` (:968), `new ExhSettings` mỗi nến (:965), list tạm (`levels` :962), `hotThisBar`, 4 list ứng viên mới mỗi nến. Gộp lại ≈ 100 ms riêng cho `byTick`→mảng và ≈ 100 ms cho bỏ LINQ `[ĐO]` (ablation §6) — nhỏ so với 2 mục trên.
- `IsLocalHigh/Low` (:706-707 → :1636-1649): 40 lần `Bar(i)` mỗi nến. Trong harness `Bar(i)` là mảng O(1) nên thấp; **nếu `HistoricalData[i, SeekOriginHistory.Begin]` (+ ép kiểu `as HistoryItemBar`, :1376-1378) đắt trong Quantower thì chỗ này nhân lên** — `[SUY LUẬN, CHƯA ĐO]`. Nên thay bằng cửa sổ cuốn high/low (O(1) mỗi nến). Tương tự `UpdateAbsorptionConfirms` :1462-1465 (tối đa 3 `Bar()` mỗi bản ghi chờ), `HasRecentHotLevel` :1441-1450 (rẻ).
- `UpdateExhaustionSweeps`: duyệt `_exhRecs` (đo max 146 phần tử, trần 3000): 70 ms tổng — chưa đáng sửa.
- `ModZ` gọi trong vòng ô (:725): O(L) lần gọi nhưng mỗi lần O(1) sau khi Recompute xong — ổn.
- String tooltip: dựng CHỈ khi bóng thực sự nổ (:762-767, :788-789) — không phải nghẽn.
- `ComputeSettingsFingerprint` (:505-526) gọi MỖI `Process()` (:588): `string.Join` với ~90 tham số đóng hộp ⇒ **5,4 µs/lần** `[ĐO]`.

### 2.4 Ghi file niêm phong — thủ phạm số 2 `[ĐO]`

`SignalCache.Put` (SignalCache.cs:94-105) mỗi nến: `JsonSerializer.Serialize` + `Directory.CreateDirectory` + `File.AppendAllText` (mở-ghi-đóng file). Gọi từ `PersistBar` (:1621) và `RePersistBar` (:1004, :1475).

- `File.AppendAllText` 100.000 dòng × 600 B lần lẻ: **17.961 ms = 179,6 µs/lần** (gom 1 lần: 195 ms) `[ĐO]`. (Chậm bất thường — rất có thể do quét thời gian thực của antivirus; `[SUY LUẬN]` về nguyên nhân, số đo là thật.)
- Nạp nguội 87.362 nến với đúng `FileSink` (bắt chước `Put`): **34.256 ms tổng, trong đó persist 25.431 ms**, 108.636 lần ghi (87.361 nến + 21.275 lần `RePersistBar` do chốt giữ/vỡ mức & quét kiệt sức), file 100 MB.
- Gom ghi 1 lần: **2.896 ms tổng**, cùng 108.636 bản ghi, file giống hệt theo luật "dòng sau thắng" (`identical-last-wins=True`).
- `BigTradeLog.TryAppend` (SignalCache.cs:210-229): cũng `AppendAllText` từng dòng, và gọi trong vòng ô (:814) khi `isClosed && fromSingleTrade`. Lịch sử mot=0 nên không chạy; **nếu feed lịch sử nào đó có `MaxOneTradeVolume>0` thì lần nạp đầu có thể ghi hàng triệu dòng × 180 µs ≈ chục phút** `[SUY LUẬN từ đơn giá đo được]`.

### 2.5 Đọc cache lúc khởi động `[ĐO]`

`SignalCache.Load` (:79-91): `File.ReadLines` + `JsonSerializer.Deserialize<CachedBarData>` từng dòng (dùng phản chiếu), gán vào Dictionary, **không có nén file**, dòng thừa không bao giờ bị dọn.

File thật `_GCZ26_XCEC_Time_1Minute.jsonl`: 76 MB, 134.944 dòng, 104.263 nến duy nhất ⇒ **22,7% dòng là rác bị ghi đè**; 4 dấu vân tay khác nhau (95.877 dòng `10|…2.5|2…` cũ, 13.167 `15|…`, ~12.950 mỗi cái của 2 bản `cellbig`). File 15 phút: 40.641 dòng / 6.036 nến duy nhất ⇒ **85% rác**, và **không nến nào** khớp dấu vân tay "top". File `_GCZ26_XCEC_Time.jsonl` 335 MB (cũ, không khung) vẫn nằm đó nhưng chỉ đọc khi `fresh && isM1` (:1537).

| Cách đọc | ms |
|---|---|
| Hiện tại (ReadLines + Deserialize từng dòng, đã khởi động ấm) | 689 – 754 |
| Hiện tại, LẦN ĐẦU trong process (JIT + phản chiếu) | **1.654 – 1.732** |
| Chỉ ReadLines, không parse | 179 |
| Chỉ lập chỉ mục TimeTicks (bản ghi thắng cuối), parse lười | 300 – 350 (+ ~97 ms / 50.000 dòng khi cần) |
| `ReadAllBytes` + System.Text.Json **source-generated** (span) | 470 – 513 |
| `ReadAllBytes` + chỉ mục byte, giải mã CHỈ dòng thắng | **370 – 412** |
| File sau nén (chỉ bản cuối/nến: 76 MB → 49 MB, ghi 232 ms) + đọc kiểu hiện tại | 425 – 517 |

Bộ nhớ: sau `Load` giữ lại **74 MB** (104.276 nến) mãi trong `_byTime`, nhưng tạm thời cấp phát **329 MB** `[ĐO]`; thêm bản sao `List<Bubble>` trong `_bubbles` cho nến hiển thị.

### 2.6 Đường sống (OnUpdate mỗi tick) `[ĐO]`

Process khi KHÔNG có nến đóng mới: 7,4 µs (ComputeBar nến sống + sweeps) → 11,4 µs kèm fingerprint. Không đáng kể ở nhịp tick vàng (vài chục tick/giây).

**Nhưng** nếu Quantower gọi `OnUpdate(HistoricalBar)` cho từng nến lịch sử khi VA đã `Finished` (tác giả viết "Update(HistoricalBar)×N", :489-494 `[SUY LUẬN, không đo được số lần gọi]`) thì mỗi lần gọi là 1 Process thừa: 87.362 × 11,4 µs ≈ **1,0 s** (đo từng lần + nhân N). Bản tối ưu (không fingerprint, hàm nến sống tinh gọn) 4,4 µs ⇒ 0,38 s.

### 2.7 OnPaintChart (:1110-1295)

- Chỉ duyệt nến **hiển thị** `li..ri` (:1196) — tốt. Vùng stacked: duyệt cả `_zones` dưới `lock` mỗi frame (:1150) = **11,6 µs/frame với 4000 vùng** `[ĐO]` — không đáng.
- Mỗi nến: `lock(_sync)` + `new List<Bubble>(l)` (:1205-1209) — lock rất ngắn; cấp phát nhỏ.
- Tạo `Font` mỗi frame (:1136): **0,5 µs**; `SolidBrush` mỗi bóng: **0,2 µs** `[ĐO]` — KHÔNG phải vấn đề, cache brush/pen không đáng làm.
- Chi phí thật nằm ở **số lượng primitive GDI+ có alpha**: FillEllipse 12 px ≈ 8 – 9 µs, DrawEllipse ≈ 15 – 20 µs, FillRectangle thân nến ≈ 12 µs, vùng stacked 600×8 px ≈ 21 – 28 µs, **DrawString số delta ≈ 12 – 13 µs/chữ** `[ĐO trên Bitmap CPU, không phải chart thật của Quantower]`. Frame mô phỏng 400 nến, 2,5 bóng/nến: ≈ 15 ms không số delta, ≈ 20 – 25 ms có số delta. `ShowDeltaNumbers` (:1253-1269) chiếm ~25% thời gian frame; ngoài ra `d.ToString("+0;-0;0")` cấp phát mỗi nến mỗi frame (cache chuỗi giảm DrawString từ ~12 → ~4 µs `[ĐO]`, vì dùng lại Font/Brush/format).
- `MeasureString` (:1262) chỉ chạy khi `DeltaBackground` bật (mặc định tắt).
- Kết luận: vẽ **không** làm chậm lúc nạp (nó chạy sau). Chỉ là "lag lúc kéo/zoom" nếu hiển thị rất nhiều nến; có thể giảm bằng cache chuỗi delta và lớp bitmap tĩnh — ưu tiên thấp.

---------------------------------------------------------------------------------------------------

## 3. CÓ TÍNH LẠI TOÀN BỘ LỊCH SỬ NHIỀU LẦN KHÔNG? (mục 4 yêu cầu)

Có, theo thiết kế:

1. `VolumeAnalysisData_Loaded` (:472) → `ResetState()` (:541) xoá `_bubbles`, baseline, zones, v.v. → `Process()` đi lại **toàn bộ** N nến. Gọi nhiều lần mỗi phiên (chú thích :56-60) ⇒ mỗi lần ≈ 0,9 s (ấm, `[ĐO]`) hoặc ≈ 35 s (nguội). Cache (niêm phong) đã chặn **việc tính lại tín hiệu**, nhưng không chặn việc **khôi phục + nạp lại baseline** cho cả N nến.
2. `OnSettingsUpdated` → `Refresh` → `Clear` → `OnClear` → `ResetState` (:480-483) và N lần `OnUpdate` (:556).
3. Đổi tham số làm đổi `_settingsFingerprint` ⇒ **mọi** nến cache có dấu vân tay cũ bị coi là chưa niêm phong ⇒ nạp nguội toàn bộ (đúng thiết kế, nhưng đắt vì §2.4) và **cache file phình ra thêm 1 dòng/nến mỗi lần** (đo: 15 phút: 40.641 dòng cho 6.036 nến).

Chặn được thêm bằng cache? Với tín hiệu: đã chặn. Với **baseline**: khôi phục nến không cần tính tín hiệu nhưng vẫn gọi `AddToBaseline` cho mọi nến (0,23 s / 87k, `[ĐO]`). Chỉ cần nạp baseline cho ~W (100) nến cuối trước nến đầu tiên cần tính; muốn chính xác từng bit phải đi ngược để chọn đủ nến "góp mặt" cho từng chuỗi (mot chỉ góp khi mot>0, impact chỉ khi vol>0, CellBig chỉ khi có ô) — làm được nhưng lợi ích chỉ ~0,2 s nên ưu tiên thấp.

Phương án B (đổi hành vi, cần người học chốt, KHÔNG phải tối ưu "y hệt"): nếu timeline nến không đổi thì `VolumeAnalysisData_Loaded` không `ResetState` mà chỉ xử lý phần mới. Lưu ý baseline hiện bị tính lại từ dữ liệu VA nạp lại (mỏng hơn lúc live) nên hành vi hiện tại và hành vi B có thể cho baseline khác nhau cho nến mới.

---------------------------------------------------------------------------------------------------

## 4. NHỮNG GÌ CHƯA ĐO ĐƯỢC (nói rõ)

- Thời gian Volume Analysis do Quantower tự tính + chi phí `HistoricalData[i, SeekOriginHistory.Begin]`, `VolumeAnalysisData.PriceLevels` (kiểu `Dictionary<double, VolumeAnalysisItem>`, đã xác nhận qua phản chiếu) và các thuộc tính `VolumeAnalysisItem` trong Quantower thật — harness dùng đối tượng thường, `Bar(i)` O(1).
- Thread nào gọi `VolumeAnalysisData_Loaded`/`OnUpdate`, và `OnUpdate` có thật sự bị gọi N lần khi VA đã xong.
- GDI+ trên cửa sổ chart thật (đã đo trên Bitmap trong bộ nhớ).
- Harness chỉ port các tính năng **mặc định bật**: Absorption (có `HasRecentHotLevel`, swing), Ô lớn (có gộp ±1 tick), Big Trade (mot luôn =0 trong CSV nên nhánh thật sự không chạy), Nến delta, Stacked Imbalance, Exhaustion, các baseline. Divergence/Sweep/Unfinished/StopHunt/DLine (đều tắt mặc định) không port.
- `BigTradeLog.TryAppend` và việc ghi file trên **máy khác/không có antivirus** (179 µs/lần ghi có thể thấp hơn nhiều ở máy khác).

---------------------------------------------------------------------------------------------------

## 5. ĐỀ XUẤT XẾP THEO (lợi ích / rủi ro sai dữ liệu / công sức)

Ký hiệu: **L** = lợi ích ước tính (đo trong harness), **R** = rủi ro sai data, **C** = công sức.

### Đề xuất 1 — Gom ghi niêm phong thành lô (L rất cao · R rất thấp · C thấp)
- **Chỗ:** `SignalCache.cs:94-105` (`Put`), `OrderFlowBubbles.cs:1616-1631` (`PersistBar`/`RePersistBar`), gọi ở :609, :1004, :1475.
- **Vấn đề:** `File.AppendAllText` + `CreateDirectory` + mở/đóng file mỗi nến, 234 µs/lần `[ĐO]`; 25,4 s trong lần nạp nguội 34 s; `RePersistBar` ghi lại **cả nến** mỗi lần chốt một bóng (21.275 lần dư).
- **Cách sửa:** `Put` chỉ cập nhật `_byTime` + thêm vào bộ đệm `StringBuilder`/danh sách "bẩn" (khoá = TimeTicks để một nến bị chốt nhiều lần chỉ ghi 1 dòng cuối); `Flush()` ghi 1 lần bằng một `FileStream` mở một lần, gọi ở cuối `Process()` (trong `finally`) và khi `OnClear`/dispose, và cứ mỗi ~500 dòng. Mất điện giữa chừng chỉ mất ≤ 1 lô chưa flush (hiện tại mỗi dòng cũng chỉ `AppendAllText` không fsync).
- **Chứng minh không đổi dữ liệu:** `Persist` trong harness: 2 file (từng nến vs gom 1 lần) đọc theo "dòng sau thắng" ⇒ **87.361 nến, nội dung giống hệt** `[ĐO]`. Thêm test trong `tests/`: sinh chuỗi Put/RePut ngẫu nhiên → file gom và file từng dòng phải `Load()` ra cùng Dictionary.
- **Lợi:** nguội 34,3 s → 2,9 s (cùng các tối ưu khác).

### Đề xuất 2 — `RollingRobust` bằng mảng đã sắp xếp + MAD merge-walk, và NGỪNG nạp baseline không ai đọc (L cao · R thấp (đã chứng minh bit-exact) · C thấp)
- **Chỗ:** `OrderFlowBubbles.cs:1689-1742` (class), `:1403-1437` (`AddToBaseline`), `:143-145, :531-534`.
- **Vấn đề:** mỗi nến sort 2 lần cửa sổ (300 hoặc 100 giá trị) cho 5 đối tượng ≈ 4,3 s / 87k nến; `_rLvlSideVol` không được đọc ở đâu; `_rLvlAbsDelta` chỉ đọc khi `DLineEnabled`.
- **Cách sửa:** giữ một mảng `double[]` đã sắp xếp; chèn/xoá giá trị bằng tìm nhị phân + `Array.Copy` (đã có code ở `Robust.cs: FastRobust`). Trung vị lấy trực tiếp từ mảng. MAD = trung vị của `|x − median|` = lấy phần tử giữa của phép **trộn hai dãy tăng** (nửa trái đi ngược, nửa phải đi xuôi) — O(n/2), không sort; dùng đúng `Math.Abs(x − median)` và `0.5*(a+b)` nên KHÔNG đổi từng bit. Không tạo `_rLvlSideVol` (hoặc nạp theo cờ); chỉ nạp `_rLvlAbsDelta` khi `DLineEnabled`. `AddToBaseline` chọn top-3 ô bằng một lượt duyệt thay vì tạo `List` + `Sort` + 2×`Select.ToArray()` (kết quả là TẬP giá trị, thứ tự chèn không ảnh hưởng median/MAD).
- **⚠ Phải làm cả hai cùng lúc:** chỉ thay `RollingRobust` mà vẫn nạp mảng `|Delta|` của mọi ô (≈18/nến, cửa sổ ≈1800 giá trị) thì **tệ hơn** (tổng 8,9 s, baseline 6,5 s) vì chèn/xoá 36 lần/nến vào mảng dài `[ĐO]`. Ablation: `ALL-NoDead` = 7,2 s; `ALL-Robust` = 4,6 s; `ALL` = 1,2 s.
- **Chứng minh:** `robust` trong harness: 5 kiểu dữ liệu × 20.000 nến × 5 điểm hỏi × (Median + ModZ) = 1.000.000 phép so `BitConverter.DoubleToInt64Bits` → **0 sai lệch**; và `Digest` toàn bộ 87.362 nến y hệt (§6). Với dữ liệu nguyên (khối lượng hợp đồng) còn có thể dùng histogram đếm O(maxVal) — không cần, vì số đo đã đủ.
- **Lợi:** ComputeBar 4,5 s → 1,0 s (−3,5 s).

### Đề xuất 3 — Danh sách vùng stacked "đang hoạt động" (L trung bình · R thấp · C thấp)
- **Chỗ:** `OrderFlowBubbles.cs:1483-1494` (`RegisterZones`), `:1498-1511` (`UpdateZones`), `:159`.
- **Vấn đề:** O(N·Z): mỗi nến quét hết `_zones` (tới 4000) 2 lần dưới `lock(_sync)`: 0,99 s `[ĐO]`, đồng thời chặn thread vẽ.
- **Cách sửa:** thêm `List<ZoneRec> _active` (vùng chưa kết thúc); `UpdateZones` chỉ duyệt `_active` và gỡ ra khi `EndIdx` được gán; `RegisterZones` bỏ `RemoveAll(z => z.Idx == idx)` trừ khi phần tử cuối đã có `Idx >= idx`. `_zones` giữ nguyên thứ tự để vẽ không đổi. Giữ nguyên quy tắc cắt tỉa :1492 (đã kiểm: không bị ảnh hưởng).
- **Chứng minh:** `Digest` gồm cả `Z{Idx},{EndIdx},{End}` của mọi vùng: `identical=True`; zones 918 ms → 23 ms.

### Đề xuất 4 — Đọc cache nhanh hơn + dọn file (L trung bình · R thấp · C trung bình)
- **Chỗ:** `SignalCache.cs:79-91` (`Load`), `OrderFlowBubbles.cs:1516-1558` (`EnsureCache`).
- **Cách sửa (xếp theo dễ → khó):** (a) `ReadAllBytes` + chỉ mục byte theo `TimeTicks` (bản ghi thắng cuối) rồi giải mã CHỈ dòng thắng bằng `System.Text.Json` **source-generated** (`[JsonSerializable(typeof(CachedBarData))]`) — 730 → 370-410 ms và tránh chi phí phản chiếu/JIT ở lần đầu (1,65 s) `[ĐO phần ấm; phần "tránh JIT" là SUY LUẬN]`; (b) **nén file** khi nạp nếu số dòng > 1,2 × số nến duy nhất: ghi tệp tạm rồi thay (76 → 49 MB, ghi 232 ms, lần sau đọc nhanh hơn); (c) xoá/ghi chú file `_GCZ26_XCEC_Time.jsonl` 335 MB & `_GC_XCEC_Time.jsonl` 67 MB không còn dùng; (d) lười: chỉ giải mã khi `TryGet` (hữu ích nếu một ngày chỉ khôi phục phần hiển thị).
- **Chứng minh:** test `Load()` cũ vs mới trên chính file thật: hai `Dictionary<long, CachedBarData>` bằng nhau từng trường (so `JsonSerializer.Serialize` của từng phần tử) — chạy trên cả 3 file khung 1/5/15 phút.
- **Lợi:** −0,3 s đến −1,2 s mỗi lần khởi động; file không phình.

### Đề xuất 5 — Bỏ việc làm thừa mỗi lần `OnUpdate` (L thấp-trung bình · R thấp · C thấp)
- **Chỗ:** `OrderFlowBubbles.cs:588` (fingerprint), `:620-629` (nến sống), `:556-567`.
- **Cách sửa:** tính `_settingsFingerprint` một lần trong `OnSettingsUpdated`/`OnClear`/lần đầu, không tính mỗi tick (đổi tham số luôn đi qua `Refresh` ⇒ cờ bẩn đủ) — hoặc cache chuỗi và chỉ tính lại khi `Settings` thay đổi; bỏ qua `ComputeBar(cur)` nếu "dấu thời đại" của nến sống không đổi (idx, số nến đóng, Volume, số ô, High/Low/Close); nếu `args.Reason == HistoricalBar` mà không có nến đóng mới thì thoát sớm.
- **Chứng minh:** golden test: phát lại chuỗi tick giả (từ CSV, tăng dần từng ô trong nến cuối) vào bản cũ và mới, so `_bubbles[cur]` sau mỗi bước.
- **Lợi:** 11,4 → ≤4,4 µs/lần; nếu có N lần gọi lịch sử: −0,6 s.

### Đề xuất 6 — Tối ưu cấp phát trong ComputeBar (L thấp · R thấp · C thấp)
- **Chỗ:** :664 (`byTick`), :884-887, :895-897, :908, :962-968, :1423-1430.
- **Cách sửa:** `Dictionary` → mảng theo `k − minTick` (có `has[]`; phải trải theo **min..max của mọi ô**, không theo Low..High, vì vòng POC :687 duyệt mọi ô kể cả ngoài biên; chặn nếu span > ~10.000 thì quay về Dictionary); bỏ LINQ chọn top-1 bằng vòng for (giữ đúng thứ tự phá hoà: điểm rồi z; ô lớn theo `magnitude` giảm dần rồi `k` tăng); tái dùng `ExhSettings`/list. Ablation: mỗi cái ≈ −0,1 s (`ALL-ArrByTick` 1,32 s; `ALL-NoLinq` 1,24 s so với `ALL` 1,22 s) — làm sau cùng.
- **Chứng minh:** `Digest` y hệt (đã đo cho từng cờ riêng lẻ).

### Đề xuất 7 — Cửa sổ cuốn cho swing và `Bar(i)` (L chưa biết · R thấp · C thấp)
- **Chỗ:** :706-707, :1636-1649, :1462-1465.
- **Vấn đề:** 40 lần `Bar()` mỗi nến chỉ để tính max/min 20 nến trước. Nếu `HistoricalData[i, Begin]` trong Quantower không phải O(1) rẻ thì đây là điểm nghẽn ẩn **`[SUY LUẬN]`**. Làm một lần `PrefetchBars` (mảng high/low đã đệm) trước vòng lặp Process.
- **Chứng minh:** so `afterSwingHigh/Low` cũ vs mới từng nến trên CSV (hai mảng bool bằng nhau).

### Đề xuất 8 — `BigTradeLog` gom ghi (L chưa biết · R rất thấp · C thấp)
- **Chỗ:** SignalCache.cs:210-229, OrderFlowBubbles.cs:813-814. Cùng cách với Đề xuất 1 (bộ đệm + flush cuối Process). Đây là phòng ngừa cho feed có mot>0 trong lịch sử.

### Đề xuất 9 (tái cấu trúc, làm sau) — tách LÕI TÍNH THUẦN khỏi Quantower
- Tạo `BarEngine` thuần (không tham chiếu `TradingPlatform.BusinessLayer`): vào là `IBarSource` (O/H/L/C, thời gian, mảng ô `(price, buy, sell, vol, mot)`), ra là `List<BubbleData>` + vùng + `Tint`. `OrderFlowBubbles` chỉ còn: lấy bar từ `HistoricalData`, gọi lõi, giữ khoá, vẽ. Harness hiện tại (`Engine.cs`) chính là phác thảo của lõi này.
- Lợi: (1) golden test chạy được trong `tests/` không cần DLL Quantower, dùng `fp_GCZ26_XCEC_Time_*.csv`: sinh `Digest`, so hash với bản trước khi sửa — bắt mọi thay đổi vô ý trong từng commit; (2) benchmark vào CI; (3) có thể xử lý lịch sử theo lô ở thread nền (mỗi lô khoá `_calcLock` ngắn, thread vẽ thấy bóng hiện dần) thay vì giữ khoá 35 s; (4) chỉ tính cửa sổ hiển thị trước rồi phần còn lại nền.
- Nhắc: `CellBigLogic.cs`/`OrderFlowBubbles.cs` đang được agent khác sửa phần gộp ô liền kề — chỉ nên triển khai sau khi hai bên khoá phiên bản.

### Bảng tóm lược thứ tự làm

| # | Việc | Lợi (đo) | Rủi ro data | Công sức |
|---|---|---|---|---|
| 1 | Gom ghi niêm phong | nguội −25 s | rất thấp | thấp |
| 2 | RollingRobust sorted + bỏ baseline chết | −3,5 s | thấp (bit-exact) | thấp |
| 3 | `_active` cho vùng stacked | −0,95 s | thấp | thấp |
| 4 | Đọc cache source-gen + nén file | −0,3…−1,2 s mỗi lần mở | thấp | trung bình |
| 5 | Bỏ fingerprint/nến sống thừa | −0,6 s nếu có N lần gọi | thấp | thấp |
| 6 | Bỏ cấp phát ComputeBar | −0,1…−0,2 s | thấp | thấp |
| 7 | Cửa sổ cuốn swing | chưa biết | thấp | thấp |
| 8 | Gom ghi BigTradeLog | phòng ngừa | rất thấp | thấp |
| 9 | Tách lõi thuần + golden test + nền | nền tảng | — | cao |

---------------------------------------------------------------------------------------------------

## 6. BẰNG CHỨNG KẾT QUẢ Y HỆT (harness)

`Digest()` gồm mọi bóng của mọi nến (giá `R`, hình, màu, cỡ, SizeFrac, tooltip, Confirm, PriceHi) + mọi vùng stacked (Idx, EndIdx, End) — 14.163 KB chuỗi.

Cold, 87.362 nến, không ghi file (min của 2 lần):

| Tổ hợp | tổng ms | compute | baseline | zones | identical |
|---|---|---|---|---|---|
| legacy (bản gốc) | 5.795 | 4.511 | 226 | 918 | (mốc) |
| Robust + NoDeadBaseline | 2.256 | 1.037 | 253 | 835 | True |
| + Zones | 1.363 | 1.028 | 206 | 23 | True |
| ALL − ArrByTick | 1.323 | 979 | 211 | 22 | True |
| ALL − NoLinq | 1.239 | 915 | 199 | 19 | True |
| ALL − Zones | 2.118 | 911 | 228 | 853 | True |
| ALL − NoDeadBaseline (Robust nhưng vẫn nạp hết) | 7.243 | 922 | **6.170** | 24 | True |
| ALL − Robust | 4.637 | 4.420 | 64 | 24 | True |
| **ALL** | **1.223** | 891 | 206 | 18 | True |

Lần chạy đầu tiên riêng (có JIT): legacy 7.001 ms, ALL 1.317 ms. Cấp phát 1.732 MB → 531 MB.

Warm (khôi phục từ Dictionary trong bộ nhớ): legacy 921 ms (restore 29, baseline 231, zonesUpd 278, zonesReg 300) → ALL 421 ms (restore 67, baseline 225, zones 48); cấp phát 196 MB → 42 MB.

Test hồi quy nên đưa vào `tests/` (đề xuất): (a) `Robust` bit-exact (`Robust.cs` đã có sẵn so sánh); (b) `Digest` golden trên CSV GCZ26 90 ngày (hash SHA-256 của chuỗi Digest trước khi sửa, ghi cứng vào test; mỗi lần sửa phải trùng hash — nếu cố ý đổi luật như gộp ô liền kề thì cập nhật hash có chủ ý kèm giải thích); (c) `SignalCache` gom ghi vs từng dòng; (d) `Load` cũ vs mới trên file thật.

---------------------------------------------------------------------------------------------------

## 7. CÁC PHÁT HIỆN PHỤ (không phải nghẽn nhưng nên biết)

- File cache không bao giờ dọn ⇒ phình theo mỗi lần đổi tham số/bump phiên bản (15 phút: 85% dòng rác; 1 phút 22,7%). Đề xuất nén ở Đề xuất 4(b).
- `_exhRecs` có trần 3000 (:1007) nhưng đo `maxExh=146`, và `_absRecs` `maxAbs=3` — các vòng quét chúng không đáng ngại.
- `_hotLvls` dọn bằng `Keys.Where(...).ToList()` khi >400 (:927-928) mỗi nến khi đã vượt 400 — 400 là cỡ đỉnh nên gần như mỗi nến một lần `ToList`; nhỏ, nhưng thay bằng `Remove(idx-51)` là O(1) chính xác (nên kèm test).
- `ToCachedBarData` luôn sao chép toàn bộ bóng mỗi lần `RePersistBar` (:1560-1573) — sẽ nhẹ hơn nếu gom (Đề xuất 1).
- Quy trình `ResetState` + `Process` giữ `_calcLock` suốt (:471-476, :571) — nếu thread gọi `VolumeAnalysisData_Loaded` là thread giao diện thì chính nó đóng băng UI theo đúng thời gian ở §0 `[SUY LUẬN]`.
