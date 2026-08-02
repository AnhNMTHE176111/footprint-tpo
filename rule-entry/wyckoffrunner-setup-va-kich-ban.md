# WyckoffRunner — Setup & Kịch bản (mô tả đầy đủ)

> Nguồn: `quantower-entry-signal/WyckoffRunner.cs` (indicator M1, Quantower). Số liệu đối chiếu:
> `quantower-entry-signal/research/wyckoff/BASELINE.md` + `AUDIT_V7.md`. File này mô tả **cơ chế
> thật trong code**, không phải lý thuyết chung chung — mọi ngưỡng số là giá trị mặc định đang chạy.

## Tổng quan

WyckoffRunner có **2 nhánh tín hiệu độc lập**, chạy trên cùng 1 indicator, cùng 1 khung M1:

| Nhánh | Tên trong code | Đang bật? |
|---|---|---|
| 1 | **CBR** — Phá vùng co → Hồi giữ gốc → Vào nến tiếp diễn | ✅ **BẬT** (nhánh duy nhất được cấp vốn) |
| 2 | **QUAY ĐẦU VWAP** — Đảo chiều tại VWAP | ❌ **TẮT** (`EnableReversal=false`) |

Cả 2 chỉ bắn tín hiệu trên **nến M1 đã đóng** (không repaint — không có chuyện tín hiệu biến mất/đổi
sau khi hiện).

---

## Nhánh 1 — CBR: Phá vùng co → Hồi giữ gốc → Vào nến tiếp diễn

Đây là setup Wyckoff kinh điển "consolidation → break → retest → resume", đo bằng range **nội bộ**
giá (không phải zone profile HVN/VWAP). Trình tự đúng như code chạy:

1. **RANGE (vùng co)** — nhìn lại `RangeLen=8` nến trước nến đang xét, lấy đỉnh/đáy của 8 nến đó
   (rhi/rlo). Bề rộng (rhi−rlo) phải nằm trong **[RangeMinPts=3.0 .. RangeMaxPts=7.5] giá**. Quá hẹp
   → nhiễu, bị loại. Quá rộng → không còn là "vùng co" thật, cũng bị loại.
2. **BREAK (phá vùng)** — nến đóng vượt hẳn cạnh range (+ đệm `SlBuf=2` tick), kèm 3 điều kiện cùng
   lúc: volume-so-với-trung-bình (VSA) ≥ `BreakVsa=2.0` (climax), thân nến ≥ `BreakBody=50%` bề rộng
   nến, và đóng cùng chiều phá (nến tăng cho phá lên / nến giảm cho phá xuống).
3. **BREAK SẠCH** (`CleanBreak=BẬT`) — nhìn lại `CleanLook=20` nến trước cú phá: nếu trong đó có một
   cú "quét hụt" cạnh **đối diện** (giá đâm thủng cực trị cục bộ của `CleanWin=5` nến ngay trước nó,
   rồi đóng ngược lại và đóng ở ≥50% thân trên) thì thị trường vẫn đang xoay 2 chiều (Wyckoff Phase B
   chưa sang D) → **loại cú phá này**, dù mọi điều kiện ở bước 2 đều đạt.
4. **HỒI (retrace) giữ vùng** — trong `WaitBars=12` nến sau phá, giá được phép hồi lại nhưng **không**
   được đóng lùi hẳn về trong range quá `HoldTolTicks=2` tick. Mức hồi so với chiều dài đợt phá (từ
   cạnh range tới đỉnh/đáy đã đạt) phải nằm trong **[PullMin=60% .. PullMax=100%]** — hồi sâu mới coi
   là runner thật; hồi nông (đuổi đà kiệt) bị loại.
5. **TIẾP DIỄN (resume)** — nến đóng vượt cực trị của nhịp hồi (thuận hướng phá ban đầu) + thân ≥
   `ResumeBody=35%` + **VSA ≥ `ResumeVsa=0.80×`** (thêm 2026-08-02) → **VÀO LỆNH tại giá đóng nến đó**.
   Nến hồi không đủ VSA thì **bỏ qua nến đó và chờ tiếp** trong cửa sổ 12 nến, KHÔNG huỷ cả leg.

   > **Sửa 2026-08-02 — người học phát hiện trên chart.** Trước đó nến vào lệnh **không có điều kiện VSA
   > nào** (chỉ nến PHÁ mới đòi VSA ≥ 2.0). Đo thật: VSA nến vào trung vị chỉ **1.04×**, 56% số lệnh vào
   > nến dưới ngưỡng "high" 1.2×, nhóm VSA < 0.8 có WR 35% (toàn bộ 47%). Với cấu hình WyckoffRunner
   > (RR4 + break sạch): n 29→21, WR 48.3%→**57.1%**, EV +1.414→**+1.857**.
   >
   > **Kèm một lỗi HIỂN THỊ đã sửa cùng lúc:** cột `VSA` và cờ "tím" trong panel/CSV/Telegram trước đây
   > lấy từ **nến PHÁ** (trung vị 2.86×, gần như luôn "tím") chứ không phải nến vào lệnh — nên log trông
   > đẹp trong khi nến vào trên chart lại nhỏ. Nay báo VSA **nến VÀO**; VSA nến phá xuống dòng lý do.
   > ⚠ File `WyckoffRunner-lenh-dinh-SL.md` ghi VSA nến phá nên **không so trực tiếp** với log mới.
   > Chi tiết + đối chứng: [`RESULTS_ENTRY_VSA.md`](../quantower-entry-signal/research/wyckoff/RESULTS_ENTRY_VSA.md).
6. **3 gate lọc tại đúng nến VÀO** (không phải nến phá — sửa lỗi parity 2026-07-29):
   - **Lọc THUẬN xu hướng** (`TrendFilter=BẬT`): xu hướng chậm = so giá đóng hiện tại với giá đóng
     `TrendBars=480` nến trước (~8 tiếng), ngưỡng đổi hướng `TrendTolPts=1.0` giá. Lệnh chỉ vào khi
     thuận hướng này.
   - **Đúng phía VWAP** (`VwapAlign=BẬT`): LONG chỉ vào khi giá ≥ VWAP phiên; SHORT khi ≤ VWAP. *Lưu
     ý đã đo thực nghiệm: trên cửa sổ 5–7/2026 gate này là NO-OP tuyệt đối (0 lệnh khác biệt bật/tắt)
     — giữ bật vì có thể khác trên dữ liệu khác, nhưng đừng coi đây là 1 lớp lọc đã được chứng minh.*
   - **Lọc thanh khoản** (`LiquidityFilter=BẬT`): thanh khoản cuộn (trung bình volume `LiquidityWindow
     =1000` nến) phải ≥ `LiquidityRatio=0.75`× — loại các phiên mỏng (điển hình phiên Á).
7. **SL** — đặt ngoài cực trị của nhịp hồi ± `SlBuf=2` tick. Sàn `SlFloorPts=3.0` giá (SL ngắn hơn thì
   kéo ra đúng 3.0), trần `SlCapPts=7.0` giá (SL xa hơn thì **bỏ lệnh**, không vào).
8. **TP** — `RR=4.0`, giữ runner (không chốt sớm). Lý do chọn RR4 thay vì RR3 cũ: SL càng ngắn thì tỉ
   lệ lệnh chạy được 5–6R càng cao (quan sát của pro trader CORVEN), sweep dữ liệu xác nhận đơn điệu
   tăng tới RR8 nhưng RR4 giữ được WR ~50% + MDD thấp (3R).
9. **Lọc PHIÊN CHẾT** (`SkipDeadSession=BẬT`, `DeadUseUtc=true`) — bỏ mọi lệnh CBR có nến vào rơi vào
   khung giờ **UTC [DeadStartHour=2, DeadEndHour=8)** (giờ CME nghỉ/settlement quanh 17–18h ET). Khung
   này đo được WR chỉ ~10%, lỗ nặng cả 3 tháng. Nhánh QUAY ĐẦU **được miễn** khung này (thắng 4/4 trong
   khung đó khi test).
10. **Dedup + Cooldown** — gộp tín hiệu trùng trong `DedupBars=6` nến, và sau khi vào 1 lệnh phải chờ
    `Cooldown=15` nến mới cho vào lệnh tiếp theo **cùng phía**.

**Kết quả in-sample** (dxFeed GCQ26, 3 tháng 5–7/2026 — xem `BASELINE.md`): **n=33, WR 48.5%, tổng
+47.0R, EV +1.424R/lệnh**. ⚠️ Đã qua audit (Opus xhigh, 12 hướng phản biện) và **PASS có điều kiện**,
nhưng khuyến nghị dùng **EV +0.7R** (không phải +1.424R) để tính khối lượng vào lệnh thật — vì toàn bộ
số liệu là **1 cửa sổ 3 tháng, 1 regime giá (vàng tạo đỉnh), 1 hợp đồng (GCQ26)**, chưa có 1 điểm dữ
liệu out-of-sample nào. Xem `BASELINE.md §0` và `AUDIT_V7.md` trước khi cấp vốn thật.

---

## Nhánh 2 — QUAY ĐẦU VWAP: Đảo chiều tại VWAP (ĐANG TẮT MẶC ĐỊNH)

`EnableReversal=false`. Lý do tắt: `AUDIT_V7.md §13` kết luận nhánh này **FAIL**:
- So với đối chứng ngẫu nhiên (vào lệnh random cùng hình học rủi ro): EV quan sát +0.389R đúng bằng
  mức p95 của phân phối ngẫu nhiên ⟹ **p=0.072**, không có ý nghĩa thống kê.
- Sau hiệu chỉnh cho ≥61 cấu hình đã thử (Bonferroni): p vọt lên **>1**.
- Tách theo phía (chưa từng báo cáo trước đó): **LONG chỉ EV +0.154R** (n=13, gần như 0) — gần như
  toàn bộ 8.5R/10.5R lãi đến từ **SHORT**, đúng lúc thị trường đang trong regime "vàng tạo đỉnh" ⟹ rất
  có thể đây là ăn theo regime, không phải một edge bền vững.
- Điểm dữ liệu out-of-sample duy nhất từng có: n=9, WR 33%, EV **−0.167R**.

Cơ chế (nếu bật lại — chỉ nên dùng để **thu log**, không cấp vốn thật):
- Giá chạm VWAP phiên (dung sai `VwapTolTicks=12` tick) sau khi tiếp cận đúng phía trong
  `RevApproachBars=6` nến — **lưu ý**: tham số này đã tự kiểm là *tautology* (ra đúng cùng 27 lệnh ở
  MỌI giá trị từ 1→999 nến), tức **không lọc gì thật cả**, chỉ giữ lại để không đổi hành vi ngoài phạm
  vi đã duyệt.
- Rút râu ngược ≥ `WickFrac=50%` bề rộng nến, đóng vượt qua VWAP theo hướng đảo, thân ≥30%, VSA ≥
  `RevVsaConf=1.8`.
- Phải **thuận xu hướng chậm** (dùng chung `TrendFilter` với nhánh CBR).
- SL: ngoài cực trị/VWAP ± `SlBuf=2` tick — **không có sàn 3 giá** như CBR, chỉ có trần
  `SlCapPts=7.0`.
- TP: `RevRR=1.5` — đảo chiều có trần MFE thực đo chỉ ~1.3R, khác hẳn CBR (runner, giữ tới 4R).
- "Hấp thụ" per-level (`AbsDom=0.60`, `RevClimaxOverride=BẬT`) chỉ tạo nhãn hiển thị **"hấp thụ ✓"**
  trong phần lý do, **không** ảnh hưởng Grade hay việc có vào lệnh hay không.

---

## Grade A/B và "TP vướng vùng" — CHỈ là thông tin hiển thị, KHÔNG lọc lệnh

- `Cluster` = số vùng volume-profile (POC/VAH/VAL/Đỉnh/Đáy của phiên Á/Âu/Mỹ + phiên ngày hôm trước)
  trùng quanh giá vào trong dung sai `ConfluenceTol=7` tick.
- `Grade = A` nếu `Cluster ≥ MinConfluence=2`, ngược lại `B`. Đây **chỉ là nhãn hiển thị** trên chart/
  panel — không hề chặn hay cho phép lệnh nào vào.
- "TP vướng vùng" (`BlockR`) — cảnh báo TP có thể bị 1 vùng mạnh (strength≥58) cản đường, cách entry
  bao nhiêu R. Cũng chỉ để tham khảo, không đổi Entry/SL/TP thật.

---

## Bảng cấu hình mặc định — cái gì đang BẬT / TẮT

| Nhóm | Input (tên trong code) | Giá trị mặc định | Trạng thái |
|---|---|---|---|
| CBR — vùng co | `RangeLen` / `RangeMinPts` / `RangeMaxPts` | 8 nến / 3.0 / 7.5 giá | (cấu trúc, luôn áp) |
| CBR — phá | `BreakVsa` / `BreakBody` | 2.0× / 50% | (cấu trúc, luôn áp) |
| CBR — hồi + tiếp diễn | `WaitBars` / `PullMin` / `PullMax` / `HoldTolTicks` / `ResumeBody` | 12 / 60% / 100% / 2 tick / 35% | (cấu trúc, luôn áp) |
| **CBR — VSA nến VÀO LỆNH** | `ResumeVsa` | **0.80×** | ✅ **BẬT** (mới 2026-08-02; đặt 0 = tắt) |
| **Break sạch** | `CleanBreak` (+`CleanLook`/`CleanWin`/`CleanClosePos`) | 20 nến / 5 nến / đóng ≥50% | ✅ **BẬT** |
| **Lọc thuận trend** | `TrendFilter` (+`TrendBars`/`TrendTolPts`) | 480 nến / 1.0 giá | ✅ **BẬT** |
| **Đúng phía VWAP** | `VwapAlign` | — | ✅ **BẬT** (đo được: NO-OP trên cửa sổ test) |
| **Lọc thanh khoản** | `LiquidityFilter` (+`LiquidityRatio`/`LiquidityWindow`) | 0.75× / 1000 nến | ✅ **BẬT** |
| **Lọc phiên chết** | `SkipDeadSession` (+`DeadUseUtc`/`DeadStartHour`/`DeadEndHour`) | UTC / 2 / 8 | ✅ **BẬT** (chỉ cắt CBR, QUAY ĐẦU miễn) |
| Risk/TP nhánh CBR | `SlFloorPts` / `SlCapPts` / `SlBuf` / `RR` | 3.0 / 7.0 giá / 2 tick / **4.0** | (luôn áp cho CBR) |
| Dedup / Cooldown | `DedupBars` / `Cooldown` | 6 nến / 15 nến | (luôn áp) |
| **Nhánh QUAY ĐẦU VWAP** | `EnableReversal` | — | ❌ **TẮT** (FAIL theo AUDIT_V7 — không cấp vốn) |
| Risk/TP QUAY ĐẦU (nếu bật) | `RevRR` / `VwapTolTicks` / `RevApproachBars`* / `WickFrac` / `RevVsaConf` | 1.5 / 12 tick / 6 (*tautology*) / 50% / 1.8 | (chỉ áp khi bật) |
| QUAY ĐẦU — nến vào thuận màu | `RevRequireBodyDir` | — | ❌ **TẮT** (hoán vị p=0.288 ở RR1.5 — chưa qua đối chứng) |
| Volume / warm-up | `VolFloor` / `WarmupBars` | 20 / 20 nến | (luôn áp, chống nến mỏng/gap) |
| Xuất CSV đối chiếu | `ExportCsv` | — | ❌ TẮT mặc định |
| Cầu nối MT5 (Exness) | `Mt5Bridge` (+`Mt5DryRun`) | — | ❌ TẮT (nếu bật: mặc định **dry-run**, chưa vào lệnh thật) |
| Báo Telegram | `TeleAlerts` | — | ❌ TẮT |

---

## Giới hạn cần nhớ khi review (đọc trước khi soi từng lệnh trên chart)

- Toàn bộ số liệu trong `BASELINE.md`/file review lệnh là **IN-SAMPLE**: dxFeed GCQ26, đúng 3 tháng
  5–7/2026, đúng 1 regime (vàng tạo đỉnh), đúng 1 hợp đồng. **Chưa có 1 điểm out-of-sample nào.**
- dxFeed là **proxy yếu** cho feed live thật (không có delta) — số liệu là *tương đối* để so sánh nội
  bộ, không phải dự báo chính xác cho WR/EV khi chạy live.
- Backtest không mô hình hoá spread/slippage/phí, và kiểm SL **trước** TP trong cùng 1 nến (thiên về
  bi quan — nếu cả SL và TP cùng nằm trong 1 nến thì tính là thua).
