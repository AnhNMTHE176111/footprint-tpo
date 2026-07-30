# CROWCONCEP × DFT — concept scalping momentum follow-trend (pro trader)

> **Nguồn:** video "leak bộ não training" của pro trader (cùng người trong [TRANSCRIPT.md](TRANSCRIPT.md) / [RULES.md](RULES.md)),
> người học capture 7 ảnh màn hình ngày **2026-07-31**. File này là bản chép + chưng dịch sang dạng **code được**.
> Ảnh gốc nằm trong chat, **chưa lưu vào repo** — nếu còn file thì bỏ vào `data-export/messages-with-pro-trader/crowconcep-img/`.
>
> ⚠️ **Chưa backtest.** Mọi con số/ngưỡng dưới đây là suy ra từ mô tả, chưa đo trên data.

---

## 0. Chú ý thuật ngữ (quan trọng, dễ hiểu sai)

| Từ trong video | Nghĩa thật | Ghi chú |
|---|---|---|
| **"bóng nổ"** | **bubble order flow** (đốm khối lượng lớn nổ ra trên chart bubble) — chính là indicator [OrderFlowBubbles](../../quantower-orderflow-indicator/) | **KHÔNG phải "bóng nến"/wick.** Ảnh 5–6 vẽ nến xanh + một đốm xanh nhạt = bubble, và luật là **vị trí bubble trên thân nến** |
| **DMA** | **Delta Moving Average** — trung bình động của delta | Có sẵn indicator [quantower-dma](../../quantower-dma/) |
| **Vwap D** | VWAP phiên ngày (daily) | Đã dùng trong RunnerSignal v5 |
| **Model entry** | Bộ mẫu vào lệnh có sẵn của anh ấy (zone trap / phe chủ động / hấp thụ / …) | Danh sách đầy đủ **chưa biết** → xem §6 |

---

## 1. Giới thiệu (Phần 1 trong video)

- Đây là **1 trong 2 concept scalping** dùng **Momentum** để **follow theo trend**.
- Vì follow trend nên: **RR 1:2**, **chấp nhận nhiều SL**, **tâm lý phải cực kỳ ổn định, không để cảm xúc chi phối**.

→ Hệ đúng kiểu **win rate trung bình, RR cố định 1:2, tần suất cao**. Đây là hệ **khác** với hệ RR 1:5–1:6 trong RULES.md (R6/R7) — cùng một người nhưng **hai concept khác nhau**, không được trộn tham số.

## 2. Ý tưởng hệ thống (Phần 2)

**Bước 1 — xác định "lực phát đi":**
> "Đầu tiên chúng ta cần xác định một lực phát đi có thể là tăng hoặc giảm, lực này đủ lớn và tạo ra **nến thân to ít râu**."
> "Một lực phát đi đủ lớn kèm nến thân to, khi này chúng ta sẽ thực hiện follow theo dòng chảy."

Ảnh chart thật (chart footprint có số delta, ngày 2026-07-30, có cả VWAP đen trên + đường xanh dưới):
sau một đoạn lình xình biên hẹp, xuất hiện cây xanh thân dài **delta +374**, rồi cây xanh **+271** → đó là "lực phát đi";
mũi tên đỏ đánh dấu từ chân cây +374 đi lên. Sau đó có các cây điều chỉnh delta âm (−77, −76, −72) nhưng giá giữ được.

**Bước 2 — điều kiện độ sâu của nhịp hồi:**
> "Vì follow trend nên giá **không được phép test quá sâu**; nếu giá có dấu hiệu **sideway biên hẹp** thì **DMA phải > 0 nếu muốn buy** và **< 0 nếu muốn sell**."

**Bước 3 — cây quyết định (ảnh 4):**

```
                       ┌─ giá KHÔNG test quá sâu ──────────► follow luôn (test nông)
Điều kiện đủ để follow ─┤
                       └─ giá sideway biên hẹp ở vùng test sâu
                            └─ chỉ follow NẾU DMA > 0 (buy) / < 0 (sell)
```

**Bước 4 — vào lệnh bằng Model entry:**
> "Cách entry sử dụng **Model entry**: **bỏ đi model zone trap** và sử dụng các model còn lại để entry, kèm theo một vài điều kiện."

---

## 3. ⭐ Kỹ thuật đọc VỊ TRÍ BUBBLE trên nến (phần người học nhấn mạnh)

### 3.1 Model "Phe chủ động" (aggressor)
> "+Đối với model **Phe chủ động** thì điều kiện sẽ cần **bóng nổ không được ở quá sát high or low**.
> Ví dụ trường hợp **buy follow**, thì **bóng nổ buy không được ở sát high** của cây nến."

Ảnh 5 vẽ hai nến xanh giống nhau, khác duy nhất vị trí bubble:

```
   ❌ KHÔNG follow                ✅ ĐƯỢỢC follow
   ┌──────┐                       ┌──────┐
   │ ●    │ ← bubble sát HIGH     │      │
   │      │                       │  ●   │ ← bubble ở GIỮA thân
   │      │                       │      │
   └──────┘                       └──────┘
      │                              │
   "Nổ gần high là không được       "Bóng phải được nổ ở khoảng
    follow theo"                     giữa giữa or low của cây nến"
```

**Cơ chế (Claude diễn giải, không có trong video):** bubble buy khổng lồ nằm **sát đỉnh nến** = phe chủ động mua **ở giá xấu nhất**, tức là bị **hấp thụ** bởi sell-limit đặt sẵn ở đó → khả năng cao là người mua muộn bị kẹt, giá quay đầu. Bubble nằm **giữa hoặc phía low** = lệnh chủ động vào **trước** khi giá chạy, và giá còn **đi tiếp được sau bubble** → lực thật, follow được.

→ Đây chính là cầu nối sang **hấp thụ / hỗ trợ**: *vị trí bubble so với cực trị nến* = thước đo "lệnh chủ động đó có bị hấp thụ hay không". Bubble sát cực trị + giá không đi thêm = **hấp thụ tại đó → mức đó thành kháng cự (buy bị hấp thụ) hoặc hỗ trợ (sell bị hấp thụ)**. Nhất quán với **R2** trong RULES.md ("hấp thụ chỉ có giá trị ở cực trị").

### 3.2 Model "Hấp thụ"
> "+Đối với model **Hấp thụ** **không cần** điều kiện cây hấp thụ big volume."

→ Với mẫu hấp thụ thì **không đòi hỏi volume lớn**. Khớp **R10** trong RULES.md ("volume thấp không phải tín hiệu đảo" — và ngược lại, hấp thụ không cần vol to mới tính).

### 3.3 Các lưu ý khi chơi concept này
> "+Lưu ý các mốc **Vwap D**, các **vùng quan trọng**: nếu giá phản ứng ở đó thì **sẽ không follow nữa**, mà **chờ phát lực để follow theo hướng mốc lớn**."
> "+Khi giá **sideway biên rộng**, cần chờ **một nhịp phát lực break rõ ràng** thì mới follow."

Ảnh 7 vẽ range biên rộng (2 đường đỏ ngang), giá dập lên xuống 2–3 lần rồi **break cạnh trên và đi thẳng** → chỉ điểm break đó mới được follow. Trùng ý **W5** ("đánh break thôi") và **W3** ("đừng đánh UT sớm").

---

## 4. Chưng thành LUẬT CODE ĐƯỢC

| # | Luật (nguyên văn) | Feature code | Data có test được? |
|---|---|---|---|
| **X1** | "lực phát đi đủ lớn và tạo ra **nến thân to ít râu**" | `impulse_bar`: `body/range ≥ 0.65` **và** `range ≥ k × ATR(M1)` **và** `|delta| ≥ k₂ × delta_ma`. Đã có sẵn khái niệm gần giống trong RunnerSignal (BREAK SẠCH) | ✅ OHLCV + delta |
| **X2** | "giá **không được phép test quá sâu**" | `retrace_pct ≤ τ` — Runner v5 hiện cho **60–90%**, concept này ngược lại đòi **NÔNG**. Cần đo lại: khả năng τ ≈ 0.5 | ✅ |
| **X3** | "sideway biên hẹp thì **DMA > 0 nếu buy**, **< 0 nếu sell**" | `narrow_range_flag` (range N nến ≤ ε × ATR) **⇒ bắt buộc** `DMA(delta, n) > 0` cho LONG | ✅ có delta per-bar |
| **X4** | "**bỏ model zone trap**" | Không vào lệnh khi tín hiệu nằm trong vùng đã đánh dấu là bẫy (biên range chưa xác nhận). Cần định nghĩa "zone trap" từ concept DFT gốc → **chưa đủ thông tin** | ❓ |
| **X5** | "**bóng nổ buy không được ở sát high** của cây nến" (model phe chủ động) | `bubble_pos` = `(price_bubble − low) / (high − low)` của cây tín hiệu, tính từ mức giá có **volume/delta lớn nhất** trong cây. LONG cần `bubble_pos ≤ 0.6` (giữa hoặc dưới); SHORT cần `≥ 0.4` | ✅ có `perlevel_m1_clean.pkl` (bid/ask từng mức giá) |
| **X6** | "model **Hấp thụ** không cần điều kiện big volume" | Nhánh absorption: **bỏ** gate `volume ≥ x × TB`. Chỉ cần delta ngược hướng + giá không đi tiếp | ✅ |
| **X7** | "giá **phản ứng ở Vwap D / vùng quan trọng** thì không follow, chờ phát lực theo hướng mốc lớn" | `at_key_level`: nếu giá đang trong ±δ của VWAP-D / POC / VA edge (TPO suite đã có) **và** cây phản ứng ngược → **veto** tín hiệu follow; chỉ mở lại sau khi có `impulse_bar` phá qua mốc | ✅ VWAP + TPO |
| **X8** | "sideway **biên rộng** cần chờ **break rõ ràng** mới follow" | `wide_range_flag` ⇒ chỉ nhận tín hiệu sau `break_clean` khỏi biên (đã có logic BREAK SẠCH trong WyckoffRunner) | ✅ |
| **X9** | "RR **1:2**", "chấp nhận nhiều SL" | Nhánh scalp riêng: **TP = 2R cố định**, không dùng 3R/1.5R của v5. WR mục tiêu ≥ 40% để dương | ✅ |

## 5. Ghép vào code hiện có

| Feature | Chỗ để cắm |
|---|---|
| X1, X2, X8 | [WyckoffRunner.cs](../../quantower-entry-signal/WyckoffRunner.cs) — đã có impulse/break sạch/retrace, chỉ đổi ngưỡng |
| X3 | [quantower-dma](../../quantower-dma/) — đã có DMA, chỉ cần đọc dấu |
| X5 | [quantower-orderflow-indicator](../../quantower-orderflow-indicator/) (bubbles) + [quantower-footprint-export](../../quantower-footprint-export/) để backtest offline |
| X6 | Nhánh hấp thụ chưa tồn tại → viết mới |
| X7 | [quantower-tpo-suite](../../quantower-tpo-suite/) (VWAP-D, POC, VA) |

**Đề xuất:** concept này là **hệ thứ 3**, ĐỪNG nhét vào RunnerSignal v5 (RR 3R, retrace sâu 60–90%) — hai bộ tham số **xung đột trực tiếp** ở X2. Nên tách indicator/nhánh riêng, ví dụ `CrowFollowSignal`.

## 6. Còn thiếu — cần hỏi lại pro trader

1. **Danh sách đầy đủ "Model entry"** của DFT là gì (ngoài *zone trap*, *phe chủ động*, *hấp thụ*)?
2. **"Zone trap"** định nghĩa chính xác thế nào?
3. **DMA** dùng chu kỳ mấy nến, khung nào (M1/M5)?
4. **"Test quá sâu"** = quá bao nhiêu % nhịp phát?
5. **"Sát high"** = trong bao nhiêu % trên của thân/range nến?
6. **"Nến thân to"** đo bằng ATR bao nhiêu lần, hay bằng mắt?
7. Khung thời gian chính của concept (chart trong video trông như **M1** có footprint delta)?
