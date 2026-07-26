# PLAN — Entry Signal Indicator (footprint M1) cho Quantower

> **Trạng thái: PLAN — đã research + backtest 28 ngày dữ liệu thật, CHƯA implement.**
> Bản này viết ở effort cao. Người implement phiên sau bám plan này; mọi ngưỡng đã calibrate theo
> GC vàng ~4000–4160, tick 0.1. Chạy `research/*.py` để tái lập số.

---

## 0. Tóm tắt & phát hiện then chốt (đọc trước khi làm)

Indicator **M1 real-time** gợi ý **điểm vào lệnh (Entry/SL/TP)** cho vàng, theo đúng cách người dùng
đánh: **xác định bias + vùng mạnh (TPO/VWAP) → chờ giá tới vùng → đọc phản ứng footprint → vào theo
2 kịch bản** (phá&hồi thuận đà / chạm&đảo). RR mặc định **1:3**, SL **≤6 giá (đẹp 2–4 giá)** dưới
nến hoặc dưới vùng, TP nới tới **vùng mạnh kế** (có thể 1:4+).

### ⚠️ Phát hiện quyết định từ backtest 28 ngày (6/26→7/25, 28.071 nến M1)
Đây là lý do plan này KHÁC hẳn "auto-signal 2 kịch bản" ban đầu:

1. **Tín hiệu cơ học THÔ (bắn ở mọi vùng) KHÔNG có edge — tệ hơn ngẫu nhiên.** 330 tín hiệu:
   MFE/MAE = **0.86 < baseline ngẫu nhiên 1.05**; kỳ vọng âm ở MỌI target (1R −0.04 … 3R −0.09);
   nới SL 2→6đ không cứu. Lý do: máy bắn ~12 lệnh/ngày, và **offline không có footprint theo từng
   mức giá** — đúng thứ người dùng dùng mắt để lọc "climax bị hấp thụ (đảo)" vs "climax phá tiếp".
2. **NHƯNG "hợp lưu ≥2 vùng" là bộ lọc THẬT** — qua 3 kiểm chống overfit:

   | Confluence | n | 2R kỳ vọng | 3R kỳ vọng |
   |---|---|---|---|
   | =1 vùng | 256 | **−0.20R** | −0.23R |
   | **≥2 vùng** | 74 | **+0.30R** | **+0.41R** |
   | ≥3 vùng | 21 | +0.29R | +0.52R |

   - **Đơn điệu** theo bậc confluence (càng chồng càng tốt) → cơ chế thật, không phải nhiễu.
   - **Chia đôi 28 ngày**: confluence≥2 dương ở **CẢ 2 nửa** (nửa đầu +0.32R, nửa sau +0.27R);
     confluence=1 âm ở cả 2 nửa. Đây là kiểm out-of-sample → edge ổn định.
   - Tần suất confluence≥2 = **3.0 lệnh/ngày** (chọn lọc, đúng kiểu người dùng).
3. **Phá&hồi (Kịch bản 1) > Chạm&đảo (Kịch bản 2)** trong confluence≥2: S1 **+0.61R@2R** (28 lệnh),
   S2 +0.11R@2R / +0.30R@3R (46 lệnh). S2 (đảo) cần footprint-wall nhất → **live mới đủ**.
4. **KHÔNG thêm edge offline:** VSA/climax đứng một mình, phân kỳ CVD (proxy), **VWAP-đứng-một-mình
   (−0.51R, TỆ NHẤT)**, lọc theo phiên. → Các thứ này chỉ là **thành phần hợp lưu / bối cảnh**,
   KHÔNG được dùng làm trigger đơn lẻ. (VWAP-trong-confluence thì tốt: Entry-1 mẫu = VWAP+VAH Á+VAL Âu.)
5. **SL 2–4 giá tốt hơn 6 giá** (6đ: kỳ vọng về ~0). Khớp trực giác "4 giá đẹp".

### Hệ quả thiết kế (spine)
- **Trigger = HỢP LƯU ≥2 vùng mạnh** chồng nhau (≤~7 tick). Chạm 1 vùng lẻ → **không bắn** (hoặc chỉ
  hiện xám "info", không phải tín hiệu). Đây là lõi đã validate, cho kỳ vọng dương **không cần footprint**.
- **Footprint live (`PriceLevels`) là lớp CHỒNG LÊN** lõi confluence: xác nhận hấp thụ/imbalance/big-trade
  tại mức — **bắt buộc cho Kịch bản 2 (đảo)**, tăng hạng cho Kịch bản 1. Phần này **không backtest được**
  → validate LIVE bằng log. Lõi confluence là "sàn" đã có edge; footprint kỳ vọng nâng thêm.
- **Bắn trên nến M1 ĐÃ ĐÓNG** (không repaint) — người dùng đã chốt.
- **VSA/climax/delta/bias/VWAP = bối cảnh & thành phần hợp lưu**, không phải trigger đơn lẻ.

---

## 1. Nền dữ liệu & bằng chứng (số THẬT — từ `research/`)

### 1.1 Dữ liệu dùng được / cột chết (fp-m1-1-month-data.csv, 28.071 nến)
- **Dùng được (per nến):** OHLC, Volume, Buy(Ask) vol, Sell(Bid) vol, **Delta (=Buy−Sell, đúng 100%)**,
  Delta%, **Cumulative delta**, **VSA Volume** (=Volume thô), DMA.
- **CHẾT (toàn 0):** Buy/Sell **trades**, **Max/Min delta** (⇒ không có delta-excursion intrabar offline),
  **Max one trade Vol.** (⇒ không dò iceberg/lệnh đơn lớn), Delta trades, Filt.*, Average buy/sell size,
  Open interest, Buy+Sell **≠** Volume ở 62% nến (có phần KL không phân loại → chỉ tin Delta & Volume).
- **KHÔNG có footprint theo mức giá** (bid/ask từng nấc) trong mọi file export → absorption/stacked-imbalance/
  big-trade **chỉ làm được LIVE** qua `bar.VolumeAnalysisData.PriceLevels`.

### 1.2 Hằng số vàng (calibrate)
- Nến M1: Range **med 13t / p90 30t / max ~90t**; Volume **med 44 / p90 155 / max 4663**; |Delta| med 7/p75 16/p90 31.
- 1 khe bảo trì/ngày ~**61 phút** (M1 KHÔNG tách ngày bằng gap 75' — xem lỗi DailyTpoBias M1 §1.4).
- VWAP anchor: reset ở khe >30' (mỗi phiên/ngày giao dịch).

### 1.3 VSA — khớp indicator `VsaVolume` (BẮT BUỘC tính giống để số khớp màn hình)
`ratio = vol / SMA(vol, 20 nến, GỒM nến hiện tại)`. Bậc (input, user xác nhận **High=1.2**):
`≥2.2 Ultra High = TÍM/magenta (climax)` · `≥1.8 Very High = đỏ` · **`≥1.2 High = cam`** ·
`≥0.8 Normal = xanh lá` · `≥0.4 Low = xanh dương` · `<0.4 Very Low = xám`.
→ **Cổng tối thiểu nến tín hiệu = High (≥1.2)**; **climax tím (≥2.2) = booster** (2 ví dụ thật của user
đều dùng nến tím). Indicator entry nên **đọc/căn theo cùng công thức này** (hoặc lý tưởng: đọc lại đúng
series của indicator VSA đang chạy) — KHÔNG tự chế baseline lệch (từng ra artifact "VSA 15.3x").

### 1.4 Gắn với 2 indicator TPO đã có
- **M30SessionZones** (đã chạy tốt, clock-based) = nguồn vùng phiên Á/Âu/Mỹ + naked POC + biên VA + target.
- **DailyTpoBias** = nguồn **bias ngày** (dùng lean/nhãn). ⚠ Chỉ đúng trên **M30** (lỗi mega-day trên M1) →
  entry indicator ở M1 **tự kéo lịch sử M30/Daily** để dựng bias/vùng (đừng đọc bias từ chart M1).

---

## 2. Kiến trúc Quantower

### 2.1 Một indicator M1 tự cấp dữ liệu
- Add vào **chart M1** có Volume Analysis. `IVolumeAnalysisIndicator`, `IsRequirePriceLevelsCalculation=>true`,
  chỉ chạy sau `VolumeAnalysisData_Loaded` + `VolumeAnalysisCalculationProgress.State==Finished`.
- **Tự kéo 2 khung phụ để dựng vùng/bias** (không phụ thuộc chart hiện tại):
  ```csharp
  var hdM30 = Symbol.GetHistory(Period.MIN30, fromUtc);   // dựng session zones + bias engine
  var hdDay = Symbol.GetHistory(Period.DAY1,  fromUtc);    // mức D-1 VAH/VAL/POC/H/L
  ```
  Dùng chung **`ProfileEngine`** (đã có) cho POC/VA/IB/naked-POC/cluster. Cache, chỉ tính lại khi có nến
  M30/Day mới đóng. Guard `GetHistory` null/thiếu → fallback vùng từ chính M1.
- **Footprint live tại M1:** đọc `bar.VolumeAnalysisData.PriceLevels` (Dictionary giá→item có
  `Volume/BuyVolume/SellVolume/Delta`) cho lớp hấp thụ/imbalance. (Max/MinDelta/MaxOneTradeVol có thể 0
  tùy feed → guard, hạ cấp nếu thiếu.)

### 2.2 Threading & render (theo mẫu OrderFlowBubbles/2 indicator TPO)
- `Process()` serialize bằng `_calcLock`; publish `RenderState` bất biến dưới `lock(_sync)`; paint đọc snapshot.
- Tính tín hiệu **chỉ trên nến đã đóng** (`_processedClosedCount`); nến đang chạy KHÔNG bắn (không repaint).
- Vẽ ở **main window** (`IsMainWindow`), map giá bằng `GetChartY`.

---

## 3. THUẬT TOÁN — Confluence-gated Entry Engine

### 3.1 Dựng POOL vùng (mỗi vùng: price, kind, strength, ready, expire, side=auto)
Nguồn (đã test): **session POC/VAH/VAL/High/Low** (Á/Âu/Mỹ) · **naked POC** (nam châm) · **cụm POC** ·
**D-1 VAH/VAL/POC/High/Low** · **VWAP (động)** · (tùy) IB extreme. Vùng có **hạn dùng** (session ~3 ngày,
D-1 ~1.25 ngày) để không kích hoạt bằng mức quá cũ.

### 3.2 ⭐ HỢP LƯU (gate chính — lõi đã validate)
Tại mỗi nến đóng, quanh giá: gom các vùng có band chồng/cách nhau ≤ **`ConfluenceTol` (mặc định 7 tick)**
thành **1 cụm hợp lưu**. **`confluence = số vùng DISTINCT trong cụm`** (đếm nguồn khác loại; VWAP tính 1).
- **confluence ≥ 2 → đủ điều kiện bắn** (A/B-grade tùy kịch bản).
- confluence = 1 → **KHÔNG bắn** (tùy chọn: hiện chấm xám "vùng đơn, chờ thêm xác nhận").
`strength_cluster = max(strength) + 0.5·Σ(còn lại)`, cap 100. (Dùng `ProfileEngine.ClusterPocs` mở rộng.)

### 3.3 Máy trạng thái 2 kịch bản (chỉ xét khi giá ở trong `ArmDist`=20t quanh cụm hợp lưu)

**KỊCH BẢN 1 — Phá & hồi (A-grade, thuận đà) — mạnh nhất offline:**
1. *Nến phá*: đóng qua cụm (≥`Buf`=2t), thân ≥50%, **delta thuận** chiều phá, VSA ≥ High(1.2).
2. *Hồi* trong ≤`RetestBars`=12 nến về sát mức phá (≤`RetestTol`=4t), **không đóng ngược lại** (đóng
   ngược = hủy).
3. *Nến tín hiệu* (mục 3.4) thuận chiều phá → **VÀO**. TP nới tới **vùng mạnh kế** (như Entry-2 → Đỉnh Á, 1:4).

**KỊCH BẢN 2 — Chạm & đảo (B-grade, cần footprint-wall) — offline yếu, live mới đủ:**
1. Giá tiến vào cụm nhưng **không đóng được qua** (bị đẩy ra).
2. **Tường hấp thụ (LIVE, bắt buộc):** tại mức cực trị chạm, `PriceLevels` cho **1–2 mức volume vượt trội
   (≥ p85 per-level của nến) + dominance |Δ|/vol ≥ 0.6 ngược chiều tiếp cận + giá KHÔNG xuyên** (stall).
   *(Offline chỉ có proxy VSA≥High + delta ngược → yếu; vì vậy S2 phải chờ live.)*
3. *Nến tín hiệu* đảo (mục 3.4) → **VÀO** chiều đảo.

### 3.4 Nến tín hiệu (cổng VSA + hình + delta)
`vsa=ratio(§1.3)`; long: (**rút râu dưới** lw≥50% range & đóng ≥55% & delta≥0) **hoặc** (**thân mạnh**
body≥55% & |Δ|/vol≥0.25 & Δ>0 & đóng ≥60%). Short đối xứng. **Cổng: vsa ≥ High(1.2)**. **Climax tím
(≥2.2) → +1 hạng tin cậy.** (Backtest: cổng High cho tần suất hợp lý; climax là điểm cộng, không phải điều kiện.)

### 3.5 Footprint live layer (chồng lên confluence)
- **Absorption** (mục 3.3-S2) — trigger bắt buộc cho S2, booster cho S1.
- **Stacked imbalance** (bid×ask chéo ≥3:1, run≥3 mức) tại/ą gần cụm → booster mạnh (đây là "tường").
- **Big trade / big per-level volume** tại mức (fallback `MaxOneTradeVol`=0 → dùng volume/mức) → booster.
- Thiếu `PriceLevels` (feed mỏng) → **hạ cấp**: chỉ cho A-grade (S1) chạy bằng lõi confluence; S2 tạm ẩn.

### 3.6 Bias & VWAP (bối cảnh — filter/booster, KHÔNG phải trigger)
- **Bias** (từ DailyTpoBias engine, kéo M30): trade thuận bias → +hạng; ngược bias → hạ hạng/ẩn (tùy chọn
  `BiasFilter`). *(Offline lọc bias không đổi edge nhiều trên mẫu nhỏ → để TUỲ CHỌN, mặc định BẬT nhẹ.)*
- **VWAP**: là **1 vùng trong pool** (đóng góp confluence). Thêm bối cảnh: long ưu tiên khi giá ≥ VWAP hoặc
  bật lên từ VWAP; short đối xứng. **KHÔNG bắn chỉ vì chạm VWAP** (VWAP-đơn = −0.51R).

### 3.7 SL / TP / RR (calibrate theo backtest)
- **SL** = dưới nến tín hiệu **hoặc** dưới biên cụm hợp lưu (chọn cái an toàn hơn), **sàn 2đ, trần 6đ,
  đẹp 3–4đ**. `risk = |entry−SL|`; **risk > 6đ → BỎ setup**. (SL 2–4đ > 6đ theo backtest.)
- **TP1 = 3R** (mặc định). **TP2 = vùng mạnh kế** trong chiều lệnh (nếu ≥3R → dùng, cho 1:4+ như Entry-2).
  Chốt **trước vùng nặng 2–3 tick**.
- **Hủy (invalidation):** đóng M1 ngược qua biên cụm (S1 mất mức phá / S2 đóng xuyên vùng).

### 3.8 Chấm hạng & độ tin cậy
`grade`: **A** = confluence≥2 + Kịch bản 1 + (live) footprint booster; **B** = confluence≥2 + Kịch bản 2 +
tường hấp thụ live; **info** = confluence=1 (không bắn, chỉ xám). `confidence 0–100` =
`40(confluence: 2→40,≥3→55) + 20(footprint xác nhận) + 15(nến tím/climax) + 15(thuận bias) + 10(VWAP bối cảnh)`.
Chỉ hiển thị **A/B**; cooldown 15 nến/cụm; hợp lưu càng cao càng ưu tiên.

---

## 4. Render & UX (nến đóng, ẩn/hiện linh hoạt)
- **Trên chart (main window):** tại nến bắn — mũi tên (▲ long/▼ short) + **nhãn gọn** `LONG A · E 4049.1 ·
  SL 4046.8 (−2.3đ) · TP 4056.0 (3R)→4067 (4R) · lý do`. Đường SL/TP mảnh kéo ngang tới hiện tại; xóa/mờ khi
  hủy hoặc chạm TP.
- **Panel nhỏ góc** (tái dùng mẫu hộp chữ): "Setup đang chờ/đang chạy" + checklist (confluence n, VSA bậc,
  footprint ✓/–, bias, VWAP). **Toggle bật/tắt** panel & marker (input). "Vừa đủ" như user muốn.
- **Cảnh báo** (tùy chọn): `Core.Instance.Alert`/âm thanh khi A-grade.
- Màu hạng: A = đậm, B = nhạt, info = xám. Tránh đè 2 indicator TPO (góc panel khác).

## 5. Config (InputParameter) — ưu tiên ngưỡng tương đối/portable
Nhóm **Confluence**: `ConfluenceTol=7t`, `MinConfluence=2`, `ArmDist=20t`, `Buf=2t`.
Nhóm **Nến tín hiệu**: `VsaGate=1.2`, `VsaClimax=2.2`, `BodyStrong=0.55`, `DeltaDom=0.25`, `WickFrac=0.5`.
Nhóm **Retest**: `RetestBars=12`, `RetestTol=4t`. Nhóm **Rủi ro**: `SLFloor=2đ`, `SLCap=6đ`, `RR=3`,
`ExtendToNextZone=true`, `NextZoneMinR=3`. Nhóm **Footprint**: `RequireWallForS2=true`, `ImbRatio=3`,
`AbsDom=0.6`. Nhóm **Lọc**: `BiasFilter=on`, `SessionFilter=off`. Nhóm **Hiển thị**: toggles + màu + góc panel.
Nhóm **Warm-up**: `VolFloor=20`, `WarmupBars=20` (chống nến đêm mỏng / sau gap).

## 6. Verification (vì footprint không backtest được)
1. **Build Linux sạch** (`~/quantower-libs/qw-build.sh`, concat ProfileEngine) → 0 warning.
2. **Rà tay:** confluence đếm đúng, gate ≥2, nến-đóng-only (không repaint), SL floor/cap, chia-0, warm-up.
3. **Lõi confluence = sàn đã validate** (research/): kỳ vọng dương KHÔNG cần footprint → nếu live mà lõi này
   ra kết quả tệ hơn nhiều backtest ⇒ có bug feed/tính vùng, soi lại.
4. **Deploy Windows + LOG:** ghi mọi tín hiệu A/B (thời điểm, confluence, footprint, entry/SL/TP, kết quả) trong
   **1–2 tuần** → đối chiếu; calibrate `ConfluenceTol`, ngưỡng footprint, `RequireWallForS2`.
5. Đối chiếu với **lệnh tay** của user (Entry-1/2 mẫu) — máy phải gắn cờ đúng các setup đó.

## 7. Giới hạn TRUNG THỰC
- **Edge đã chứng minh = confluence≥2** (74 lệnh/28 ngày, +0.30R@2R, giữ ở cả 2 nửa) — **thật nhưng KHIÊM
  TỐN**; 74 lệnh vẫn nhỏ, cần thêm data + xác nhận live. Không hứa "máy in tiền".
- **Kịch bản 2 (đảo) chưa tự đứng offline** — phụ thuộc tường hấp thụ live; coi là B-grade tới khi log live xác nhận.
- **Footprint layer chưa test được** trên data hiện có (không có ladder) → validate live.
- **Không dò iceberg/lệnh đơn lớn** (`MaxOneTradeVol`=0); Max/Min delta=0 → không có excursion intrabar offline.
- Feed dxFeed demo có thể mỏng history/PriceLevels → guard + fallback.

## 8. Thứ tự triển khai (cho phiên effort thấp)
- **P0:** khung indicator M1 + VA gating + kéo M30/Day + dựng pool vùng (dùng ProfileEngine) + VWAP. Vẽ vùng
  để mắt kiểm.
- **P1:** **Confluence engine** (gom cụm, đếm, gate ≥2) + render cụm hợp lưu. (Đây là lõi edge — làm chắc trước.)
- **P2:** Kịch bản 1 (phá&hồi) + nến tín hiệu (VSA gate) + SL/TP/RR + marker/nhãn nến-đóng. Log.
- **P3:** Footprint live layer (absorption/imbalance/big-trade) + Kịch bản 2 (đảo, gate tường). Hạ cấp nếu thiếu PriceLevels.
- **P4:** Bias/VWAP context + chấm hạng A/B + panel + toggles + cảnh báo.
- **P5:** Deploy + log 1–2 tuần + calibrate; cập nhật memory (ghi phát hiện confluence + giới hạn footprint).
Mỗi phase: build Linux sạch → deploy → chụp/log → chỉnh. **Commit + push sau mỗi phase.**

## 9. Nguồn
- Data: `data-export/fp-m1-1-month-data.csv` (28 ngày, chính), `tpo-chart-m30.csv`, `TPO-chart-daily.csv`.
- Research tái lập: `research/entry_month.py` (backtest chính), `research/research.py` (MFE/MAE + subset),
  `research/research2.py` (chống overfit: đơn điệu + chia đôi), `research/profile_data.py` (mổ cột).
- Tái dùng: `quantower-tpo-suite/ProfileEngine.cs`; VSA `quantower-vsa-volume/VsaVolume.cs`.
- Lý thuyết: `ebook/text/orderflow-full.md`, `glossary.md`.
