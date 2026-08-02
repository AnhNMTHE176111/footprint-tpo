# EntrySignal (M1) — Mô tả setup, kịch bản, cấu hình mặc định

Nguồn: `quantower-entry-signal/EntrySignal.cs` (bản đang ship). Mục tiêu file này: mô tả CHÍNH XÁC
những gì code đang làm, để đối chiếu với chart thật — không phải mô tả lý thuyết chung chung.

## 1. Vùng (pool) — nơi indicator "canh lệnh"

Vùng tự dựng từ chính M1 (không phải TPO khung ngày/tuần):

- **Theo phiên** (Á/Âu/Mỹ, tách theo giờ + gap>40 phút): POC, VAH, VAL, Đỉnh, Đáy của MỖI phiên đã
  đóng. Hết hạn sau `ZoneExpireDays=3` ngày.
- **D-1** (ngày hôm trước, tách theo gap>45 phút): VAH, VAL, POC, Đỉnh, Đáy. Hết hạn sau 1 ngày 6 giờ
  kể từ đầu ngày hôm sau (đủ dùng trong phiên kế).
- **VWAP động**: 1 vùng, giá cập nhật theo từng nến (VWAP cộng dồn từ đầu phiên, reset khi gap>30
  phút). **VWAP KHÔNG được tính vào hợp lưu** (xem mục 2) — chỉ hiển thị/tham chiếu, không dùng để gate.

Không có HVN tuần/ngày hay POC/VAH/VAL khung tuần trong bản này (đó là hướng CORVEN đã thử nghiệm
riêng — xem `quantower-entry-signal/research/wyckoff/v8/entry/RESULTS_ENTRY_ZONES.md`, kết luận KILL,
chưa đưa vào production).

## 2. Hợp lưu (Cluster) — điều kiện gate chính

Một tín hiệu chỉ được giữ lại nếu tại giá vào lệnh có **≥ `MinConfluence` = 2** vùng KHÁC NHAU (không
kể VWAP) nằm chồng lấp trong bán kính `ConfluenceTol = 7 tick` (0.7 giá). Đây là điều kiện đã backtest
là cốt lõi của edge (vùng lẻ ≈ nhiễu, hợp lưu ≥2 mới có kỳ vọng dương).

Lưu ý 2 số dễ nhầm trong code/JSON xuất ra:
- **Cluster** = số vùng chồng lấp thật quanh giá vào → đây là số dùng để **gate** (`MinConfluence`) và
  để quyết định nhồi lệnh (`NhoiConflGate`).
- **Confl** = số tín hiệu thô bị gộp lại làm một (do trùng hướng, gần nhau ≤6 nến & ≤`DedupTol` tick)
  — chỉ mang tính thống kê, không dùng để gate.

## 3. Hai kịch bản CHÍNH (luôn bật)

### KB1 — phá & hồi (grade A, thuận đà)
1. Giá **phá qua vùng** theo một hướng: đóng nến ngoài vùng ± `SlBuf=2 tick`, thân nến ≥50% range,
   delta cùng chiều phá, VSA ≥ `VsaGate=1.2×` TB volume.
2. Trong tối đa `RetestBars=12` nến sau đó, giá **hồi về gần vùng** (chạm trong `RetestTol=4 tick`) mà
   **không chọc quá vùng** (`RetestHoldBuf=0` → low/high phải giữ đúng phía vùng vừa phá, không "bắt
   dao rơi").
3. Nến hồi phải là **nến tín hiệu tiếp diễn**: rút râu ngược hướng phá (≥50% range, cpos xác nhận) HOẶC
   thân mạnh cùng chiều (`BodyStrong=0.55`, delta-dominance ≥`DeltaDom=0.25`, |Delta|≥`DeltaAbsMin=15`),
   kèm VSA≥1.2×.
→ Vào lệnh THEO HƯỚNG PHÁ BAN ĐẦU (tiếp diễn xu hướng vừa phá).

### KB2 — chạm & đảo (grade B, cần hấp thụ)
1. Giá **chạm vùng** (tagged, trong `SlBuf` quanh vùng) từ một phía, **chưa phá hẳn**.
2. Xuất hiện nến đảo chiều tại vùng (rút râu/thân mạnh + delta + VSA≥1.2×, ngược hướng tiếp cận).
3. Bắt buộc có **bằng chứng hấp thụ** tại vùng (`RequireWallForS2=true`), là MỘT trong hai:
   - **Tường hấp thụ per-level** (footprint thật): tại 1 mức giá cực trị có volume ≥1.5× TB các mức
     và delta-dominance ngược hướng tiếp cận ≥ `AbsDom=0.60`.
   - **HOẶC** nến climax tím (`VSA ≥ VsaClimax=2.2×`) — `S2ClimaxOverride=true` cho phép nến climax
     thay thế yêu cầu tường hấp thụ per-level (đa số lệnh SL/TP trong log hiện tại rơi vào nhánh này,
     ghi chú "climax-abs").
→ Vào lệnh NGƯỢC hướng tiếp cận (đảo chiều tại vùng).

### 3b. NẾN VÀO LỆNH PHẢI THUẬN MÀU (thêm 2026-08-02 theo review chart của người học)

Áp cho **cả KB1 lẫn KB2**, mặc định **BẬT** (`RequireEntryBodyDir=true`).

- Nến kích hoạt **thuận màu** (`C>O` cho LONG, `C<O` cho SHORT) → vào lệnh ngay như trước.
- Nến kích hoạt **ngược màu hoặc doji** → **KHÔNG vào**, chuyển sang trạng thái chờ (ARM). Trong tối đa
  `ConfirmWindow=3` nến, nến nào **thuận màu** + `VSA ≥ ConfirmVsa=1.2` + delta thuận chiều
  (`ConfirmNeedDelta=true`) thì **nến đó** mới là nến vào lệnh. SL neo theo cực trị gộp của cả nến ARM
  lẫn nến xác nhận; nếu lúc đó rủi ro vượt `SlCap` thì **bỏ lệnh** (không đuổi giá).
- `ConfirmWindow=0` ⇒ bỏ hẳn lệnh ngược màu. `RequireEntryBodyDir=false` ⇒ về đúng hành vi cũ (dùng để A/B).
- Hai cờ `ConfirmKillOnZoneCross` / `ConfirmKillOnAnchorBreak` mặc định **TẮT**: bật lên thì hầu như
  không ca nào tìm được nến xác nhận (đã đo), cơ chế coi như vô hiệu.

**Vì sao:** nhánh "rút râu" của `LongSignal`/`ShortSignal` không kiểm thân nến ⇒ nến ĐỎ vẫn bắn LONG,
nến TRẮNG vẫn bắn SHORT. 4/5 lệnh dính SL trong log 17–31/07 rơi đúng vào lỗi này.

## 4. Hai kịch bản PHỤ — mặc định TẮT

| Kịch bản | Cờ bật/tắt | Trạng thái | Vì sao tắt |
|---|---|:---:|---|
| KB3 — climax phá cụm | `EnableS3ClimaxBreak` | **TẮT** | Edge yếu (~hòa vốn ở backtest), grade C |
| KB4 — đảo chiều arm→confirm | `EnableS4ArmConfirm` | **TẮT** | Edge dương nhẹ (+0.15R@1.5R) nhưng yếu hơn lõi KB1/KB2, thêm nhiễu |

Cả hai chỉ bắn khi tự tay bật trong Input Parameters.

## 5. Bộ lọc tuỳ chọn — mặc định TẮT

| Lọc | Cờ | Mặc định | Vì sao tắt |
|---|---|:---:|---|
| Lọc hấp thụ (né delta cùng phía) | `AbsorptionFilter` | **TẮT** | Backtest cho WR 45%→52% nhưng cần dữ liệu delta live để A/B, chưa đủ tin cậy để bật mặc định |
| Lọc thuận xu hướng (proxy TPO) | `TrendFilter` | **TẮT** | Giúp nhánh phá&hồi nhưng CẮT bớt nhánh chạm&đảo ngược-trend đang thắng → hại tổng thể |
| Nới TP tới vùng kế (`ExtendToNextZone`) | — | **BẬT** | Đây là phần lõi, không phải lọc phụ — TP1 theo `RR=1.5`, nếu vùng mạnh kế cho RR≥`NextZoneMinR=2.0` thì nới TP2 runner |

## 6. Kết nối ra ngoài — mặc định TẮT hết

- `Mt5Bridge` (tự động gửi lệnh MT5): **TẮT**. Nếu bật, `Mt5DryRun=true` mặc định (ghi log, KHÔNG vào lệnh thật).
- `TeleAlerts` (báo Telegram mở/đóng lệnh): **TẮT**.
- `ExportCsv`: **TẮT**.
- `NhoiMult` (nhân lot khi hợp lưu ≥`NhoiConflGate=3`): mặc định `1.0` = không nhồi, dù cơ chế tính sẵn.

## 7. Tham số rủi ro / lọc nến mặc định

| Tham số | Giá trị mặc định | Ý nghĩa |
|---|---:|---|
| `SlFloor` | 4.0 giá | SL tối thiểu — chống stop sát bị nhiễu quét |
| `SlCap` | 6.0 giá | SL tối đa — quá thì bỏ lệnh (không vào) |
| `RR` | 1.5 | TP1 = entry ± 1.5×risk |
| `MinConfluence` | 2 | Số vùng hợp lưu tối thiểu để giữ lệnh |
| `ConfluenceTol` | 7 tick | Bán kính tính "cùng cụm" |
| `VolFloor` | 20 | Volume tối thiểu của nến để xét tín hiệu |
| `WarmupBars` | 20 | Bỏ qua N nến đầu sau mỗi khoảng trống dữ liệu (gap) |
| `VsaGate` / `VsaClimax` | 1.2× / 2.2× | Ngưỡng "nến mạnh" / "nến climax (tím)" so với TB volume 20 nến |
| `Cooldown` | 15 nến | Một vùng không bắn 2 lệnh liên tiếp trong 15 nến |

## 8. Kết quả lệnh (SL/TP) mô phỏng thế nào

`Simulate()` đi từng nến SAU nến vào lệnh: nếu nến đó chạm CẢ SL lẫn TP cùng lúc thì tính là SL trước
(giả định bi quan). Đây là cách tính dùng để dán nhãn SL/TP trong `rule-entry/SL_TRADES_REVIEW.md` —
khi đối chiếu chart, nếu thấy 1 nến chạm cả hai mức, cần tự nhìn wick/thứ tự thật trong nến đó (dữ liệu
1 phút không phân giải được thứ tự bên trong nến).
