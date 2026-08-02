# PLAN — Sửa EntrySignal (M1) v2 theo review chart của người học

Lập 2026-08-02 · **Bản 2** (viết lại sau khi có dữ liệu footprint M1 thật) · Trạng thái: **CHƯA implement**

Nguồn đầu vào:
- Lệnh live: [ENTRY SIGNAL (M1)_2026-08-02.csv](../data-export/signals/ENTRY%20SIGNAL%20(M1)_2026-08-02.csv) — 11 lệnh, 17/07→31/07.
- Review chart: [rule-entry/entry-signal-images/](../rule-entry/entry-signal-images/) — 6 ảnh.
- **Dữ liệu mới (người học xuất 2026-08-02):** [Data_Footprint_Export_bars.csv](../data-export/Data_Footprint_Export_bars.csv) (17.814 nến M1, 03/07→31/07, UTC) + [Data_Footprint_Export.csv](../data-export/Data_Footprint_Export.csv) (115.562 dòng **footprint từng mức giá**).
- Code: [EntrySignal.cs](../quantower-entry-signal/EntrySignal.cs) · Replay: [entry_replay_july.py](../quantower-entry-signal/research/entry_replay_july.py)

> **Giờ:** file dữ liệu và CSV lệnh đều là **UTC**. Chart trong ảnh là **giờ VN = UTC + 7**.
> **Cấu hình live** (người học xác nhận): `RR = 3`, `SlFloor ≈ 3.5 giá` — chọn vì cả tổng R lẫn win rate
> trên panel indicator đều cao hơn. Không phải sai lệch cần sửa.

---

## 0. ✅ Việc quan trọng nhất đã XONG: replay tái hiện 11/11 lệnh live

[entry_replay_july.py](../quantower-entry-signal/research/entry_replay_july.py) dựng lại nguyên máy trạng thái
của `EntrySignal.cs` bằng Python trên bộ dữ liệu mới (profile phiên dùng **volume rows thật** từ file
per-level, giống hệt `ProfileEngine.VolumeRows` live).

Kết quả: **11/11 lệnh khớp tuyệt đối** — cùng giờ, cùng entry, cùng SL, cùng TP, **và cùng kết quả SL/TP**.
Replay **không bắn thừa lệnh nào**. Nghĩa là mọi thay đổi từ đây có thể đo bằng số thật, không phải phỏng đoán.

```
 gio (UTC)          KB            huong   entry     SL  risk    TP1  cum  VSA   KQ    than nen
 2026-07-17 13:50   KB2 chạm&đảo  LONG   4051.2 4047.7  3.5  4061.7   2  2.3   TP    THUẬN
 2026-07-29 16:55   KB1 phá&hồi   LONG   4087.9 4083.6  4.3  4100.8   2  4.6   TP    THUẬN
 2026-07-29 22:41   KB2 chạm&đảo  LONG   4134.5 4131.0  3.5  4145.0   2  2.4   TP    ⚠ NGƯỢC
 2026-07-30 04:44   KB1 phá&hồi   SHORT  4105.6 4109.1  3.5  4095.1   2  1.7   TP    ⚠ NGƯỢC
 2026-07-30 09:30   KB1 phá&hồi   SHORT  4123.2 4126.7  3.5  4112.7   2  2.5   SL    THUẬN
 2026-07-31 07:30   KB2 chạm&đảo  LONG   4129.9 4126.4  3.5  4140.4   2  2.9   SL    ⚠ NGƯỢC
 2026-07-31 13:34   KB2 chạm&đảo  SHORT  4091.9 4095.6  3.7  4080.8   2  2.7   TP    THUẬN
 2026-07-31 17:29   KB2 chạm&đảo  SHORT  4106.6 4110.1  3.5  4096.1   3  8.9   SL    ⚠ NGƯỢC
 2026-07-31 18:41   KB2 chạm&đảo  SHORT  4106.7 4110.2  3.5  4096.2   3  2.4   SL    ⚠ NGƯỢC
 2026-07-31 19:34   KB2 chạm&đảo  SHORT  4106.2 4109.7  3.5  4095.7   3  4.4   SL    ⚠ NGƯỢC
 2026-07-31 20:33   KB2 chạm&đảo  SHORT  4106.6 4110.1  3.5  4096.1   3  3.5  open   ⚠ NGƯỢC
```

---

## 1. Ba ca SL đã review — người học nói ĐÚNG, đã xác minh bằng số

| Ảnh | Giờ UTC | Hướng | Open → Close | Thân nến | Nhận xét của người học |
|---|---|---|---|---|---|
| [image copy 4.png](../rule-entry/entry-signal-images/image%20copy%204.png) | 31/07 07:30 | LONG | 4130.2 → **4129.9** | **ĐỎ** | "nến entry vẫn là nến đỏ… Cần 1 nến tăng để xác nhận" |
| [image copy.png](../rule-entry/entry-signal-images/image%20copy.png) | 31/07 17:29 | SHORT | 4105.5 → **4106.6** | **TRẮNG** | "nến vẫn là nến ngược xu hướng rút râu" |
| [image.png](../rule-entry/entry-signal-images/image.png) | 31/07 19:34 | SHORT | 4105.8 → **4106.2** | **TRẮNG** | "xu hướng giảm, nến entry lại là nến tăng" |

**Nguyên nhân gốc** — [EntrySignal.cs:689-714](../quantower-entry-signal/EntrySignal.cs#L689-L714):

```
LongSignal:  ur = LW ≥ WickFrac*Rng  &&  Cpos ≥ 0.55  &&  Delta ≥ 0     ← KHÔNG kiểm C vs O
ShortSignal: dr = UW ≥ WickFrac*Rng  &&  Cpos ≤ 0.45  &&  Delta ≤ 0     ← KHÔNG kiểm C vs O
```

Nhánh "rút râu" không kiểm thân nến ⇒ nến đỏ vẫn bắn LONG, nến trắng vẫn bắn SHORT.
Nhánh "thân mạnh" thì đã ngầm thuận màu (`Brat≥0.55` + `Cpos≥0.6` + dấu delta), nên lỗi **chỉ ở nhánh rút râu**.

### Thống kê trên 11 lệnh live (đây là toàn bộ mẫu, n rất nhỏ — đọc theo hướng, đừng đọc theo con số)

| Nhóm | n | Đã xong | WR | Tổng R | exp R/lệnh |
|---|---:|---:|---:|---:|---:|
| Tất cả (V0 hiện tại) | 11 | 10 | 50.0% | **+10.0R** | +1.00R |
| Nến entry **thuận màu** | 4 | 4 | 75.0% | +8.0R | **+2.00R** |
| Nến entry **ngược màu** | 7 | 6 | 33.3% | +2.0R | +0.33R |

4/5 lệnh dính SL là nến ngược màu. Nhưng nhóm ngược màu **vẫn dương** (+2R) vì có 2 lệnh thắng ở RR=3.

---

## 2. Ba ca BỎ SÓT — nguyên nhân KHÁC hẳn giả thuyết ban đầu

Đã định vị chính xác cả 3 trong dữ liệu (khớp delta tới từng đơn vị):

| Ảnh | Nến (UTC) | O / H / L / C | vol | delta | VSA |
|---|---|---|---:|---:|---:|
| [image copy 5.png](../rule-entry/entry-signal-images/image%20copy%205.png) | 31/07 **07:59** SHORT | 4129.3 / 4129.3 / 4124.7 / **4125.1** | 171 | **−67** | 2.53x |
| [image copy 3.png](../rule-entry/entry-signal-images/image%20copy%203.png) | 31/07 **12:36** SHORT | 4106.4 / 4107.8 / 4103.2 / **4104.2** | 499 | **−109** | 2.47x |
| [image copy 2.png](../rule-entry/entry-signal-images/image%20copy%202.png) | 31/07 **15:38** LONG | 4096.8 / 4099.1 / 4096.1 / **4098.4** | 151 | **+23** | 1.38x |

> Bản plan trước đoán 3 ca này bị sót vì luật nến entry. **Sai.** Soi từng điều kiện thì lý do chính là **VÙNG**:

### Ca 1 — 07:59 SHORT (ảnh copy 5)
- Nến entry **ĐẠT** `short_sig` (thân mạnh, brat 0.91, VSA 2.5x tím, Δ−67). Nến không phải vấn đề.
- **Hợp lưu tại giá vào = 0.** Vùng gần nhất: POC Âu 4125.9 (cách 8 tick, cụm **1**), POC Á 4124.0 (cách 11 tick, cụm **1**). Gate `MinConfluence = 2` chặn.
- Vùng "range" mà người học nói (~4129.7 = Đáy Á, cụm 2) **chưa từng vào trạng thái `broke_dn`**: nến chọc thủng đầu tiên (07:31) có `Brat = 0.22 < 0.5` nên không tính là phá; các nến sau đã ở `prev_rel = "below"` nên điều kiện phá (`prev_rel ∈ {above, in}`) không còn thoả.
- Kể cả nếu đã ghi nhận phá: nhịp "hồi lại yếu, loanh quanh range" kéo **28 nến** (07:31→07:58) — vượt xa `RetestBars = 12`.

### Ca 2 — 12:36 SHORT (ảnh copy 3)
- Nến entry **TRƯỢT CẢ HAI** nhánh: `Brat = 0.48 < BodyStrong 0.55` (không đủ "thân mạnh") và `UW/Rng = 0.30 < WickFrac 0.50` (không đủ "rút râu").
- **Hợp lưu = 0.** Vùng gần nhất VAL Âu 4103.3 (cách 9 tick, cụm **1**).
- Người học chấp nhận nến này chỉ vì *giảm + VSA tím + delta âm mạnh* — luật nến **rộng hơn** luật đang code.

### Ca 3 — 15:38 LONG (ảnh copy 2)
- Nến entry trượt cả hai nhánh: `LW/Rng = 0.23`, `Brat = 0.53`, `Ddom = 0.15 < DeltaDom 0.25`.
- **Không có vùng nào trong ±1.5 giá.** Gần nhất Đỉnh Á 4096.7 cách 17 tick, cụm 1.
- Nến rút râu làm ARM (15:34) cũng trượt: `VSA 0.9 < 1.2` và `delta −29 < 0`.
- ⇒ Ca này nằm **ngoài hẳn mô hình hiện tại** (thiếu cả vùng, cả nến ARM, cả nến CONFIRM).

### 👉 Kết luận phải nhớ
**Không có bản sửa luật nến nào bắt được 3 ca này.** Cả ba đều bị `MinConfluence = 2` chặn vì hợp lưu chỉ 0–1.
Cái thiếu là **nguồn vùng**: người học giao dịch theo **range cục bộ trên M1** (biên vùng tích luỹ vừa hình
thành), còn EntrySignal chỉ có POC/VAH/VAL/Đỉnh/Đáy theo phiên + D-1 + VWAP.

---

## 3. Lỗi phụ tìm thêm

### 3.1 🐞 BUG — cột `kich_ban` trong CSV luôn ghi sai
[EntrySignal.cs:838](../quantower-entry-signal/EntrySignal.cs#L838):
```csharp
private static bool IsBreak(Sig s) => s.Scen != null && s.Scen.StartsWith("1");   // "1 pha&hoi" vs "2 cham&dao"
```
Nhưng `Scen` truyền vào `Emit` là `"KB1 phá&hồi"` / `"KB2 chạm&đảo"` — **không chuỗi nào bắt đầu bằng `"1"`**
(chuỗi `"1 pha&hoi"` là của bản Python). ⇒ `IsBreak` **luôn false**.

Hậu quả: CSV ghi `CHAM_DAO` cho **tất cả** lệnh (replay cho thấy 3/11 thật ra là **KB1 phá&hồi**);
tin nhắn Telegram luôn nói "chạm&đảo"; id lệnh gửi MT5 luôn mang cờ `D`.
**Sửa:** `s.Scen.StartsWith("KB1")` (hoặc `Contains("phá&hồi")`).

### 3.2 Bắn lặp cùng một mức sau khi đã thua *(Claude tìm, người học chưa nêu)*
4/11 lệnh là SHORT tại **cùng mức 4106.2–4106.7** trong 3 giờ (17:29, 18:41, 19:34, 20:33) — 3 lệnh đã đóng
đều SL. `Cooldown = 15` nến không chặn được vì cách nhau 60+ nến.

### 3.3 Thiếu tính năng stacked imbalance
Người học nêu ở ảnh copy 5. Grep toàn repo: **không indicator nào có**. Giờ đã có dữ liệu per-level M1
(115k dòng) nên **đo được offline**, không còn phải chờ live.

---

## 4. Thiết kế fix

### 4.1 Fix A — nến entry phải thuận màu (ARM → CONFIRM)

**Tham số mới** (thêm quanh [dòng 54-114](../quantower-entry-signal/EntrySignal.cs#L54-L114)):

| Tham số | Kiểu | Mặc định | Ý nghĩa |
|---|---|---:|---|
| `RequireEntryBodyDir` | bool | `true` | Nến vào lệnh phải thuận chiều (`C>O` cho LONG, `C<O` cho SHORT) |
| `ConfirmWindow` | int | `3` | 0 = bỏ hẳn lệnh ngược màu (biến thể **A1**); >0 = chờ nến xác nhận (**A2**) |
| `ConfirmVsa` | double | `1.2` | VSA tối thiểu của nến xác nhận |
| `ConfirmNeedDelta` | bool | `true` | Delta nến xác nhận phải thuận chiều |
| `ConfirmKillOnZoneCross` | bool | **`false`** | Huỷ ARM khi đóng nến xuyên vùng ngược hướng — **xem cảnh báo bên dưới** |
| `ConfirmKillOnAnchorBreak` | bool | **`false`** | Huỷ ARM khi cực trị thủng neo SL — **xem cảnh báo bên dưới** |

**Trạng thái mới trên `PZone`** (cạnh `ArmLBar/ArmSBar`, [dòng 356](../quantower-entry-signal/EntrySignal.cs#L356)):
```csharp
public int PendBar = -999; public int PendSide;
public double PendAnchor, PendZonePrice;      // VWAP là vùng ĐỘNG → phải chốt giá lúc arm
public string PendScen; public char PendGrade; public List<string> PendWhy;
```

**Luồng mỗi nến `i`, mỗi vùng `z`:**
```
1. Xử lý PENDING trước:
   a. i - z.PendBar > ConfirmWindow                                   → xoá pending
   b. (nếu bật) đóng nến xuyên vùng ngược hướng quá SlBuf             → xoá pending
   c. (nếu bật) cực trị nến thủng PendAnchor                          → xoá pending
   d. XÁC NHẬN: thân nến cùng chiều PendSide
                && Vratio >= ConfirmVsa
                && (!ConfirmNeedDelta || dấu(Delta) == PendSide)
      → Emit tại close nến i (anchor = cực trị gộp ARM+CONFIRM), z.Cool = i, xoá pending
      → Emit tự loại nếu risk > SlCap (không đuổi giá) — cơ chế đã có sẵn

2. KB1/KB2 giữ nguyên, chỉ thay chỗ gọi Emit:
     thân nến cùng chiều (hoặc RequireEntryBodyDir=false) → Emit ngay (hành vi cũ)
     ngược lại                                            → ĐẶT PENDING, không Emit
```

### 4.2 Fix B — nguồn vùng còn thiếu: **range cục bộ M1** ⭐ (đây mới là cái bắt 3 ca bỏ sót)

Thêm một loại vùng mới dựng từ chính M1, ngoài POC/VAH/VAL phiên:

```
Range cục bộ = cửa sổ N nến gần nhất (N ≈ 20-40) mà (max High − min Low) <= RangeMaxHeight (vd 5 giá)
             → sinh 2 vùng: BIÊN TRÊN (max High) và BIÊN DƯỚI (min Low), sức mạnh ~55,
               hết hạn sau RangeExpireBars nến (vd 120).
```
Tham số: `EnableLocalRange` (bool, **bật để test**), `RangeBars = 30`, `RangeMaxHeight = 5.0` giá,
`RangeExpireBars = 120`, `RangeStrength = 55`.

**Vì sao cần:** cả 3 ca bỏ sót đều nằm ở biên một vùng tích luỹ M1 vừa hình thành, và đó chính là
"range" trong lời người học ("phá range dưới, hồi lại"). Có nguồn vùng này thì hợp lưu tại các giá đó
mới có cơ hội đạt ≥2 — **điều kiện cần trước khi bàn tới luật nến**.

> Phải kiểm ngay: sau khi bật `EnableLocalRange`, hợp lưu tại 4125.1 / 4104.2 / 4098.4 có lên ≥2 không.
> Nếu vẫn không ⇒ nguồn vùng vẫn chưa đúng cái người học nhìn, **phải hỏi lại người học vẽ vùng từ đâu**
> trước khi code tiếp (đừng tự bịa thêm nguồn vùng cho khớp 3 ca).

### 4.3 Fix C — nới nhịp hồi của KB1

| Tham số | Hiện tại | Đề xuất quét |
|---|---:|---|
| `RetestBars` | 12 | 12 / 20 / **30** (ca 1 cần ≥ 28) |
| `RetestKillBuf` (mới, đang dùng `SlBuf`=2) | 2 tick | 2 / 10 / 20 tick |
| `BreakBrat` (mới, đang cứng `0.5`) | 0.5 | 0.35 / 0.5 — ca 1 phá hụt vì nến phá có `Brat = 0.22` |
| `RetestHoldBuf` | 0 | 0 / 3 / 6 ⚠️ research cũ kết luận 0 tốt nhất ([dòng 84](../quantower-entry-signal/EntrySignal.cs#L84)) — nếu quét lại vẫn ra 0 thì **giữ 0** |

Ngoài ra: điều kiện phá hiện chỉ nhận khi `prev_rel ∈ {above, in}`. Cân nhắc trạng thái "đã ở dưới vùng
liên tục ≤ K nến" cũng tính là vừa phá, để không mất ca giá **rò rỉ** qua vùng thay vì phá dứt khoát.

### 4.4 Fix D — luật nến entry rộng hơn cho ca momentum
Ca 2 (`Brat 0.48`, `UW/Rng 0.30`) trượt cả hai nhánh. Thêm nhánh thứ ba, **cờ riêng, mặc định TẮT**:
```
momentum: Vratio >= VsaClimax(2.2) && thân nến cùng chiều && |Ddom| >= MomDdom(0.20) && Brat >= MomBrat(0.45)
```
Tham số `EnableMomentumEntry = false`, `MomDdom = 0.20`, `MomBrat = 0.45`.

### 4.5 Fix E — stacked imbalance *(giờ đã đo được offline)*
Thêm cạnh [Absorption()](../quantower-entry-signal/EntrySignal.cs#L671):
```csharp
// Imbalance chéo: so ask(p) với bid(p − 1 tick).
//   mua : ask(p)       >= ImbRatio * bid(p-1tick)  && ask(p)       >= ImbMinVol
//   bán : bid(p-1tick) >= ImbRatio * ask(p)        && bid(p-1tick) >= ImbMinVol
// Stacked = >= ImbStack mức LIÊN TIẾP cùng chiều.
private bool StackedImbalance(HistoryItemBar bar, int side)
```
Tham số `ImbRatio = 3.0`, `ImbMinVol = 5`, `ImbStack = 3`, cờ `RequireStackImb = false`.
Python đối chiếu: đọc `Data_Footprint_Export.csv` theo `bar_idx` (đã có sẵn hàm `load_levels()` trong replay).

### 4.6 Fix F — khoá vùng sau N lần thua *(ý Claude, mặc định TẮT)*
`EnableZoneLossLock = false`, `ZoneLossLock = 2`, `ZoneLockBars = 240`.
Khoá theo **giá vùng làm tròn `ConfluenceTol`** để 4106.2 và 4106.7 tính là cùng mức.
`Simulate()` ([dòng 817](../quantower-entry-signal/EntrySignal.cs#L817)) đã có sẵn kết quả lệnh đã đóng.

### 4.7 Sửa bug `IsBreak` (mục 3.1) — sửa luôn, không cần test.

---

## 5. Số đo đã chạy — đọc kỹ, KHÔNG cái nào đủ mẫu để kết luận

Tất cả trên replay 03–31/07, cấu hình live (`RR=3`, `SlFloor=3.5`, `SlCap=6.0`).
Đo ở 2 mức gate: `≥2` (đúng live, 11 lệnh) và `≥1` (nới ra cho có mẫu, 35 lệnh).

### Gate hợp lưu ≥ 2 — 11 lệnh

| Biến thể | n | Đã xong | WR | Tổng R | exp R/lệnh |
|---|---:|---:|---:|---:|---:|
| V0 hiện tại | 11 | 10 | 50.0% | +10.0R | +1.00R |
| **A1** bỏ hẳn lệnh ngược màu | 4 | 4 | 75.0% | +8.0R | **+2.00R** |
| **A2** chờ xác nhận, W=3, **không huỷ ARM** | 6 | 5 | 80.0% | **+11.0R** | **+2.20R** |
| A2 W=6, không huỷ ARM | 7 | 6 | 66.7% | +10.0R | +1.67R |
| A2 (bật huỷ ARM khi xuyên vùng / thủng neo) | 4 | 4 | 75.0% | +8.0R | +2.00R |

### Gate hợp lưu ≥ 1 — 35 lệnh (mẫu lớn hơn, edge yếu đi rõ)

| Biến thể | n | Đã xong | WR | Tổng R | exp R/lệnh |
|---|---:|---:|---:|---:|---:|
| V0 hiện tại | 35 | 32 | 28.1% | +4.0R | +0.12R |
| **A1** bỏ hẳn lệnh ngược màu | 19 | 17 | 29.4% | +3.0R | **+0.18R** |
| A2 W=3, không huỷ ARM | 24 | 21 | 28.6% | +3.0R | +0.14R |
| A2 W=6, không huỷ ARM | 25 | 22 | 27.3% | +2.0R | +0.09R |

### Điều rút ra
1. **Quy tắc huỷ ARM quan trọng hơn `ConfirmWindow`.** Bật "huỷ khi xuyên vùng / thủng neo" thì
   **0/7** ca ngược màu tìm được nến xác nhận — cơ chế A2 coi như không chạy. Vì vậy hai cờ
   `ConfirmKillOn*` phải mặc định **TẮT**.
2. Cả A1 lẫn A2 đều **tăng exp R/lệnh** so với V0 ở cả hai mức gate. Đó là tín hiệu tốt nhất hiện có.
3. Nhưng A1 **giảm tổng R** ở gate ≥2 (+10R → +8R) vì cắt mất 2 lệnh thắng ngược màu.
   Chỉ A2 W=3 vừa tăng exp vừa giữ tổng R (+11R).
4. **n = 4–11 lệnh không kết luận được gì.** Đây là toàn bộ mẫu live hiện có. Muốn chốt phải có thêm dữ liệu.

### Soi tay từng ca ngược màu (gate ≥2, W=10, không huỷ ARM)

| Lệnh live | KQ live | Nếu chờ nến xác nhận |
|---|---|---|
| 29/07 22:41 LONG | TP +3R | vào lại 4138.5, risk **7.5 giá > SlCap 6.0** ⇒ **bỏ lệnh** (mất 3R) |
| 30/07 04:44 SHORT | TP +3R | vào 4106.1 (tốt hơn 0.5 giá) ⇒ vẫn **TP** |
| 31/07 07:30 LONG | SL −1R | **không có nến xác nhận** ⇒ tránh được |
| 31/07 17:29 SHORT | SL −1R | vào 4104.3 ⇒ vẫn **SL** |
| 31/07 18:41 SHORT | SL −1R | **không có nến xác nhận** ⇒ tránh được |
| 31/07 19:34 SHORT | SL −1R | **không có nến xác nhận** ⇒ tránh được |
| 31/07 20:33 SHORT | open | vào 4107.7 ⇒ open |

Tránh được 3/4 lệnh SL, giữ 1/2 lệnh thắng, mất 1 lệnh thắng vì giá chạy quá xa (đúng tinh thần "không đuổi giá").

---

## 6. Kế hoạch test

### 6.1 Dữ liệu
- ✅ **Đã đủ để bắt đầu**: 03–31/07 M1 + footprint từng mức.
- ⚠️ **Vẫn cần thêm để chốt tham số**: mẫu 11 lệnh quá nhỏ. Xin người học xuất thêm
  `Data_Footprint_Export*` cho **tháng 5 và 6/2026** (cùng indicator, cùng khung M1) → sẽ có ~3 tháng,
  đủ tách **dò tham số trên 5–6, kiểm trên 7** (holdout thật).

### 6.2 Các bước
| Bước | Việc | Đầu ra |
|---|---|---|
| T0 ✅ | Replay tái hiện live | **XONG — 11/11** ([entry_replay_july.py](../quantower-entry-signal/research/entry_replay_july.py)) |
| T1 | Bật `EnableLocalRange`, kiểm hợp lưu tại 4125.1 / 4104.2 / 4098.4 | ≥2 hay không. **Nếu không → dừng, hỏi lại người học** |
| T2 | A/B Fix A (A1 vs A2, quét `ConfirmWindow`) trong Python | bảng n/WR/R/exp theo từng gate |
| T3 | A/B Fix C (`RetestBars`, `RetestKillBuf`, `BreakBrat`) | nt |
| T4 | Đo Fix E (stacked imbalance) trên dữ liệu per-level: lệnh **có** vs **không có** stacked imbalance | nt |
| T5 | Gộp, chốt bộ mặc định | bảng tổng |
| T6 | Port C#, sửa bug `IsBreak`, build sạch, đối chiếu Python↔C# | replay khớp 100% |
| T7 | Deploy Quantower 1 tuần, xuất CSV, đối chiếu mắt trên chart | — |

### 6.3 Tiêu chí PASS/FAIL — chốt TRƯỚC, không đổi sau khi thấy số
- Bật mặc định một fix chỉ khi: **n ≥ 30 lệnh đã xong** và exp R/lệnh **cao hơn V0** và **không tháng nào lật từ dương sang âm**.
- Chưa đạt ⇒ vẫn ship nhưng **cờ TẮT mặc định**, ghi số đo vào `rule-entry/`.
- Mọi tham số quét phải kiểm holdout (dò 5–6, kiểm 7). Chênh lệch lớn giữa hai nửa ⇒ coi là overfit, giữ mặc định cũ.
- ⛔ **Không** dùng 6 ca review làm bằng chứng edge. Chúng là **test hồi quy** (bắt được / tránh được hay không), không phải mẫu thống kê.

---

## 7. Thứ tự triển khai đề nghị

1. Sửa bug `IsBreak` (mục 3.1) — 1 dòng, không cần test.
2. **Fix B (range cục bộ M1)** trước tiên — không có vùng thì mọi fix nến đều vô nghĩa với 3 ca bỏ sót. Chạy T1.
3. Fix A trong Python, A/B theo 6.2–6.3. Mặc định đề nghị: `RequireEntryBodyDir = true`, `ConfirmWindow = 3`, hai cờ `ConfirmKillOn*` = **false**.
4. Fix C (nhịp hồi KB1), quét + holdout.
5. Fix D, E, F: thêm dưới dạng cờ **TẮT**, chỉ ghi vào cột `chi_tiet` của CSV để quan sát.
6. Port C# + parity + build sạch.
7. Cập nhật [rule-entry/EntrySignal-cau-hinh-va-kich-ban.md](../rule-entry/EntrySignal-cau-hinh-va-kich-ban.md) + `progress.md`, commit + push.

## 8. Cạm bẫy đã biết
- **Không sửa `LongSignal`/`ShortSignal` tại chỗ** — giữ nguyên để tắt cờ là về đúng hành vi cũ, phục vụ A/B.
- **VWAP là vùng động** — phải chốt `PendZonePrice` lúc ARM.
- **Cổng hợp lưu tính tại nến CONFIRM**, không phải nến ARM (vùng có thể hết hạn giữa chừng).
- **`z.Cool` set tại nến CONFIRM**, không phải ARM — nếu không sẽ bắn chồng.
- **Repaint** — vòng quét bỏ nến đang hình thành ([`nClosed = B.Count - 1`](../quantower-entry-signal/EntrySignal.cs#L536)). Pending chỉ được dùng nến đã đóng.
- **Đừng dùng `entry_month.py` để A/B nữa** — nó thiếu cổng hợp lưu và chạy trên dữ liệu cũ (tới 25/07).
  Dùng [entry_replay_july.py](../quantower-entry-signal/research/entry_replay_july.py), đã chứng minh khớp live 11/11.
