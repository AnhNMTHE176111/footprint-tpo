# RunnerSignal.cs — Mô tả setup, kịch bản & cấu hình mặc định

> Chỉ mô tả **file `RunnerSignal.cs`** (indicator "Runner Signal (CBR M1)", chạy M1, cần Volume Analysis).
> Không phải EntrySignal.cs hay WyckoffRunner.cs (2 file khác, người khác phụ trách).
> Cập nhật: 2026-08-01, sau khi thêm cờ `CorvenZoneAdd`.

## 0. Bức tranh tổng quát

RunnerSignal quét **2 nhánh tín hiệu độc lập** trên cùng 1 chuỗi nến M1, mỗi bar đóng quét 1 lần:

| Nhánh | Ý tưởng 1 câu | TP mặc định | Bật/tắt |
|---|---|---|---|
| **CBR** (phá vùng → hồi → tiếp diễn) | Giá phá 1 vùng co hẹp, hồi lại nhưng KHÔNG mất vùng, rồi đi tiếp | RR = 3.0 (giữ runner) | Luôn bật (không có cờ tắt riêng) |
| **QUAY ĐẦU** (đảo chiều tại VWAP) | Giá chạm VWAP, rút râu từ chối, đảo chiều | RR = 1.5 | `EnableReversal` (mặc định **BẬT**) |

Cả 2 nhánh gộp tín hiệu vào **chung 1 danh sách**, rồi lọc trùng (Dedup) + giãn cách (Cooldown) theo **PHÍA** (LONG/SHORT), **KHÔNG phân biệt nhánh** — nghĩa là nếu CBR vừa bắn LONG thì trong `Cooldown` nến tiếp theo, QUAY ĐẦU cũng không được bắn LONG mới (đây là hành vi CÓ SẴN từ trước, không phải lỗi mới).

Chỉ bắn tín hiệu trên **nến đã đóng** (không repaint).

---

## 1. Nhánh CBR — phá vùng co → hồi giữ leg → tiếp diễn

Cơ chế 4 bước, đúng thứ tự:

1. **RANGE** — lấy `RangeLen` = **8** nến M1 liền trước, đo biên độ (high cao nhất − low thấp nhất). Biên độ phải nằm trong `[RangeMinPts, RangeMaxPts]` = **[3.0 , 7.5] giá** (đơn vị "giá" = 10 tick). Ngoài khoảng này (quá hẹp = nhiễu, quá rộng = không phải vùng co) → bỏ.
2. **BREAK** — 1 nến đóng vượt hẳn cạnh range (+ đệm `SlBuf`=2 tick), kèm **VSA ≥ `BreakVsa`=2.0×** trung bình volume và **thân nến ≥ `BreakBody`=50%** biên độ nến. Đây là cú phá có lực, không phải phá lẹt đẹt.
3. **HỒI + GIỮ** — trong `WaitBars`=**12** nến sau break, giá được phép hồi lại nhưng:
   - Hồi sâu phải nằm trong `[PullMin, PullMax]` = **[60% , 90%]** độ dài nhịp phá (leg) — hồi nông quá (<60%) coi là đuổi giá kiệt đà, hồi sâu quá (>90%) coi là thất bại.
   - Không được đóng lùi hẳn vào trong vùng cũ quá `HoldTolTicks`=**2 tick** (giữ được cạnh vùng).
4. **TIẾP DIỄN (vào lệnh)** — 1 nến đóng vượt lại đỉnh/đáy của nhịp hồi, thân ≥ `ResumeBody`=**35%**, **VSA ≥ `ResumeVsa`=0.80×** (thêm 2026-08-02). Vào tại giá đóng nến đó. Nến hồi không đủ VSA thì **bỏ qua nến đó và chờ tiếp** trong cửa sổ 12 nến, KHÔNG huỷ cả leg.

> **Sửa 2026-08-02 — người học phát hiện trên chart.** Trước đó nến vào lệnh **không có điều kiện VSA nào**
> (chỉ nến PHÁ mới đòi VSA ≥ 2.0). Đo thật: VSA nến vào trung vị chỉ **1.04×**, 56% số lệnh vào nến dưới
> ngưỡng "high" 1.2×, và nhóm VSA < 0.8 là nhóm tệ nhất (WR 35% so với 47% toàn bộ). Thêm gate 0.80:
> n 55→42, WR 47.3%→**54.8%**, tổng R +49→+50, EV +0.891→**+1.190**. Chi tiết + đối chứng:
> [`RESULTS_ENTRY_VSA.md`](../quantower-entry-signal/research/wyckoff/RESULTS_ENTRY_VSA.md).
>
> **Kèm theo là một lỗi HIỂN THỊ đã sửa cùng lúc:** cột `VSA` và cờ "tím" trong panel/CSV/Telegram trước
> đây lấy từ **nến PHÁ** (trung vị 2.86×, gần như luôn "tím") chứ không phải nến vào lệnh. Vì vậy log
> trông rất đẹp trong khi nến vào trên chart lại nhỏ — hai bên đang nói về hai cây nến khác nhau. Nay cột
> VSA báo **nến VÀO LỆNH**; VSA nến phá chuyển xuống dòng lý do (`VSA phá …`). ⚠ Các file review cũ ghi
> VSA nến phá nên **không so trực tiếp** với log mới.

**SL/TP:**
- SL = cực trị nhịp hồi ± đệm `SlBuf`=2 tick, ép trong khoảng sàn/trần `SlFloorPts`/`SlCapPts` = **[3.0 , 7.0] giá** (dưới sàn thì kéo lên sàn; vượt trần thì HUỶ tín hiệu).
- TP = entry ± `RR`×risk, RR mặc định **3.0**.

**3 bộ lọc bắt buộc ở đúng nến vào lệnh** (không phải nến break):
- **Thuận xu hướng** (`TrendFilter`, mặc định **BẬT**): so giá đóng hiện tại với giá đóng cách `TrendBars`=480 nến (~8 giờ) trước, lệch quá `TrendTolPts`=1.0 giá mới tính là có xu hướng; lệnh phải cùng chiều xu hướng đó.
- **Đúng phía VWAP** (`VwapAlign`, mặc định **BẬT**): LONG chỉ vào khi giá ≥ VWAP phiên; SHORT chỉ khi giá ≤ VWAP phiên.
- **Thanh khoản đủ** (`LiquidityFilter`, mặc định **BẬT**): volume trung bình hiện tại phải ≥ `LiquidityRatio`=0.75 lần trung bình cuộn `LiquidityWindow`=1000 nến — tránh vào lệnh lúc thị trường quá mỏng (đêm/phiên Á).

**Lọc phiên chết** (`SkipDeadSession`, mặc định **BẬT**, CHỈ áp cho nhánh CBR, KHÔNG áp QUAY ĐẦU): bỏ lệnh CBR có nến vào rơi vào khung giờ UTC `[DeadStartHour, DeadEndHour)` = **[02h, 08h) UTC** = **09h–15h chiều giờ VN** (không phải sáng sớm VN như tên gọi "phiên chết" dễ gây hiểu lầm — đã có lần sửa lỗi vì nhầm giờ, xem comment trong code). `DeadUseUtc` mặc định **true** (so theo giờ UTC, đúng khung đã đo).

---

## 2. Nhánh QUAY ĐẦU — đảo chiều tại VWAP

Cơ chế: giá **tiếp cận** VWAP phiên từ 1 phía trong `RevApproachBars`=**6** nến, rồi **chạm + bị từ chối** (rút râu):

- **SHORT**: giá đẩy lên chạm/vượt VWAP (trong dung sai `VwapTolTicks`=12 tick), nến có râu trên ≥ `WickFrac`=50% biên độ, đóng cửa dưới nửa dưới thân nến (cpos ≤ 0.45), đóng cửa dưới VWAP, thân ≥ 30%, VSA ≥ `RevVsaConf`=1.8×.
- **LONG**: đối xứng, giá đạp xuống chạm VWAP rồi bật lên.
- Phải **đến từ đúng phía** (trong 6 nến trước có giá đóng ở phía đối diện VWAP) — tránh bắt dao khi giá đã nằm sẵn 1 bên.
- ⚠ **Nhánh này KHÔNG kiểm màu thân nến** ⇒ nến TRẮNG vẫn bắn SHORT, nến ĐỎ vẫn bắn LONG (đúng loại lỗi đã sửa ở EntrySignal). Đã thêm input `RevRequireBodyDir` để bật luật thuận màu, nhưng **mặc định TẮT**: MFE trung vị của nến thuận màu là 3.78R so với 1.13R của nến ngược màu, song kiểm định hoán vị cho **p=0.288** ở RR 1.5 đang ship (không có ý nghĩa) và bật lên còn làm **giảm** tổng R (+10.5R → +8.5R). Xem [`RESULTS_ENTRY_VSA.md`](../quantower-entry-signal/research/wyckoff/RESULTS_ENTRY_VSA.md) §6.
- **Thuận xu hướng** (`TrendOk`, dùng chung field trend với CBR) — bắt buộc, không có cờ tắt riêng.

Không áp thêm `VwapOk`/`LiquidityFilter` cho nhánh này (VWAP đã là trung tâm của chính setup).

**SL/TP:**
- SL đặt SÁT cực trị nến chạm / VWAP + đệm `SlBuf`=2 tick (KHÔNG có sàn 3 giá như CBR — SL của quay đầu vốn đã nhỏ, đặt ngay tại VWAP mới đúng ý nghĩa "quay đầu").
- Risk phải > 5 tick, ≤ `SlCapPts`=7.0 giá, ngoài khoảng này thì huỷ lệnh.
- TP = entry ± `RevRR`×risk, RevRR mặc định **1.5** (đảo chiều thường hụt hơi ở ~1.3R, đặt 3R như CBR sẽ cắt lãi non/kẹt lệnh).

**Bonus (không bắt buộc, chỉ nâng "grade" hiển thị A/B):**
- `Absorption` — hấp thụ theo footprint LIVE tại cực trị (cần Volume Analysis per-level), hoặc
- `RevClimaxOverride` (mặc định **BẬT**) — VSA ≥ `VsaClimax`=2.2× cũng coi như có "tường hấp thụ".

---

## 3. Bộ lọc chung cho MỌI tín hiệu (cả 2 nhánh)

- **Gate volume** (`Gate`): volume nến ≥ `VolFloor`=**20**, số nến kể từ gap gần nhất ≥ `WarmupBars`=**20**, volume trung bình ≥ 60% sàn — chặn nến quá mỏng/mới sau khoảng trống dữ liệu.
- **Dedup** (`DedupBars`=**6** nến): 2 tín hiệu CÙNG PHÍA cách nhau ≤ 6 nến → chỉ giữ tín hiệu đến trước.
- **Cooldown** (`Cooldown`=**15** nến): sau khi đã có 1 tín hiệu 1 phía, phải cách ≥ 15 nến mới cho tín hiệu CÙNG PHÍA tiếp theo (áp DÙNG CHUNG cho cả CBR lẫn QUAY ĐẦU, xem lưu ý ở mục 0).

---

## 4. CORVEN — 2 chế độ neo vùng HVN/VWAP tuần·ngày (MẶC ĐỊNH TẮT CẢ HAI)

Xuất phát từ trao đổi với pro trader "CORVEN": họ chỉ canh lệnh quanh **HVN (vùng khối lượng cao) tuần/ngày** và **VWAP tuần/ngày**, KHÔNG dùng range nội bộ hay VWAP-phiên như code gốc. Đã backtest offline (`quantower-entry-signal/research/wyckoff/v8/runner/`), có 2 cách đưa ý tưởng này vào code, **là 2 cờ độc lập, không nên bật cùng lúc**:

| Cờ | Ý nghĩa | Mặc định | Kết luận backtest |
|---|---|---|---|
| `CorvenZoneAnchor` | **THAY HẲN** — CBR neo vào mép HVN tuần/ngày thay vì range nội bộ; QUAY ĐẦU fade vào HVN+VWAP tuần/ngày thay vì chỉ VWAP phiên | **TẮT** | Đối chứng ngẫu nhiên (dịch vùng đi chỗ khác) đa số KHÔNG vượt qua → **không khuyến nghị bật**, xem `RESULTS_RUNNER_ZONES.md` |
| `CorvenZoneAdd` | **CỘNG THÊM** — giữ nguyên CBR/QUAY ĐẦU y hệt code gốc, cộng thêm tín hiệu tại HVN/VWAP tuần **VÀ** ngày làm nguồn bổ sung (không xoá tín hiệu cũ) | **TẮT** | Số lệnh + tổng R tăng (test offline: CBR 54→120 lệnh, QUAY ĐẦU 27→40 lệnh) nhưng winrate giảm nhẹ; phần lệnh CORVEN thêm vào phần lớn KHÔNG vượt đối chứng ngẫu nhiên → tăng chủ yếu do có thêm lượt vào, chưa chắc do vị trí vùng thật sự tốt. **Đang ở giai đoạn BẬT để REVIEW THỦ CÔNG**, chưa khuyến nghị chạy live |

Tín hiệu sinh ra từ 2 cờ này được đánh dấu riêng để dễ nhận diện khi xem lịch sử/CSV:
- CBR: `"CBR phá→hồi→tiếp diễn (CORVEN)"` (so với gốc `"CBR phá→hồi→tiếp diễn"`)
- QUAY ĐẦU: `"quay đầu VWAP (CORVEN)"` (so với gốc `"quay đầu VWAP"`)

Tham số dùng chung cho cả 2 cờ:
- `CorvenZoneTier` (0=Tuần, 1=Ngày) — **chỉ có tác dụng khi `CorvenZoneAnchor` bật** (chọn 1 tầng); `CorvenZoneAdd` luôn dùng CẢ HAI tầng.
- `CorvenTolTicks`=12 tick (dung sai chạm vùng), `CorvenHvnMinRatio`=1.5× (ngưỡng coi là HVN), `CorvenHvnMaxN`=3 (tối đa 3 mức HVN/tuần hoặc ngày).
- Vùng HVN dùng cơ chế **W_CLOSED/D_CLOSED**: chỉ dùng HVN của tuần/ngày ĐÃ ĐÓNG cho toàn bộ tuần/ngày kế tiếp (không nhìn trộm tương lai).

---

## 5. Bảng toàn bộ cấu hình mặc định (để đối chiếu khi mở Quantower)

### Đang BẬT (true)
| Tham số | Giá trị | Vai trò |
|---|---|---|
| `EnableReversal` | true | Bật nhánh QUAY ĐẦU |
| `TrendFilter` | true | Lọc thuận xu hướng (CBR + QUAY ĐẦU) |
| `VwapAlign` | true | CBR vào đúng phía VWAP |
| `LiquidityFilter` | true | Lọc thanh khoản CBR |
| `SkipDeadSession` | true | Cắt CBR khung giờ chết |
| `DeadUseUtc` | true | Khung giờ chết tính theo UTC |
| `RevClimaxOverride` | true | VSA climax = bonus grade cho QUAY ĐẦU |
| `ShowSignals`, `ShowZones`, `ShowPanel`, `ShowAllHistory`, `ShowRiskBox`, `ShowArrows`, `ShowLines`, `ShowChips`, `ShowLabels`, `ShowClosed`, `DashedSlTp` | true | Hiển thị (không ảnh hưởng tín hiệu) |

### Đang TẮT (false)
| Tham số | Vai trò |
|---|---|
| `CorvenZoneAnchor` | Chế độ THAY vùng CORVEN — tắt |
| `CorvenZoneAdd` | Chế độ CỘNG THÊM vùng CORVEN — tắt (bật để review thủ công) |
| `ExportCsv` | Xuất CSV toàn bộ tín hiệu ra file |
| `Mt5Bridge` | Cầu nối gửi lệnh sang MetaTrader 5/Exness |
| `TeleAlerts` | Báo Telegram khi mở/đóng lệnh |

### Số chính (tóm tắt nhanh)
| CBR | | QUAY ĐẦU | |
|---|---|---|---|
| RangeLen | 8 nến | RevRR | 1.5 |
| RangeMinPts / RangeMaxPts | 3.0 / 7.5 giá | RevVsaConf | 1.8× |
| BreakVsa / BreakBody | 2.0× / 50% | VwapTolTicks | 12 tick |
| WaitBars | 12 nến | RevApproachBars | 6 nến |
| PullMin / PullMax | 60% / 90% | WickFrac | 50% |
| ResumeBody | 35% | RevRequireBodyDir | **TẮT** |
| **ResumeVsa** (nến vào) | **0.80×** | | |
| SlFloorPts / SlCapPts | 3.0 / 7.0 giá | | |
| RR | 3.0 | | |

Chung: `VolFloor`=20, `WarmupBars`=20, `Cooldown`=15 nến, `DedupBars`=6 nến, `SlBuf`=2 tick, `VsaPeriod`=20, `VsaClimax`=2.2×.

---

## 6. Kênh xuất/thông báo (không phải logic tín hiệu, chỉ là nơi đẩy kết quả ra)

- **CSV** (`ExportCsv`, tắt mặc định): ghi mọi tín hiệu ra file `RunnerSignal_signals.csv` — đây là nguồn dữ liệu THẬT dùng để làm file review SL (xem file thứ 2 trong cùng thư mục `rule-entry/`).
- **MT5 Bridge** (`Mt5Bridge`, tắt): gửi khoảng cách SL + RR (không gửi giá tuyệt đối, vì Quantower chạy GC/MGC futures còn MT5 chạy XAUUSD spot) sang EA `RunnerBridge.mq5` để vào lệnh thật trên Exness.
- **Telegram** (`TeleAlerts`, tắt): báo khi mở lệnh mới và khi lệnh đóng do chạm SL/TP.
