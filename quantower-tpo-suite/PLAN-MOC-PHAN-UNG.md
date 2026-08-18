# PLAN — Mốc phản ứng cho người dừng lỗ 3 giá

> Soạn 2026-08-18 sau Buổi 5 (LVN/HVN). **Đây là plan, chưa code gì.**
> Người thực thi: đọc hết mục 0 và 1 trước khi sửa dòng code đầu tiên.
> Quy ước: **1 "giá" = 10 tick** (vàng tick 0,1). Mọi ngưỡng dưới đây tính bằng "giá".

---

## 0. Bối cảnh — những gì ĐÃ CHỐT, đừng bàn lại

| # | Đã chốt | Nguồn |
|---|---|---|
| 0.1 | Người dùng **dừng lỗ 3 giá, chốt lời 4,5 giá (1,5R)**. Mọi thiết kế phải sống được ở thang này. | người dùng, 2026-08-18 |
| 0.2 | **HVN là MỐC (một mức giá), không phải VÙNG.** Đo ở độ phân giải 1 giá: 108/128 phiên (84%) có đỉnh khối lượng tách hẳn — không mức nào khác trong ±4 giá đạt 90% của đỉnh; bề rộng nền trung vị = 0 giá. Cái "bướu 50 giá" nhìn thấy trên chart là do Optimus Flow gom hàng 10 giá. | đo 2026-08-18 |
| 0.3 | **KHÔNG thêm VWAP** vào SessionZones. Người dùng dùng VWAP sẵn của Optimus Flow trên M1. | D7, `PLAN-ZONES-V2.md` |
| 0.4 | **Mốc gộp 3 tuần chỉ là NAM CHÂM/bối cảnh**, không phải điểm vào: cửa sổ 15 phiên trượt → mốc dời trung vị 20 giá mỗi 5 phiên, có lần nhảy 807 giá khi đổi vùng giá. | đo 2026-08-18 |
| 0.5 | **Nền để so sánh mọi luật: 40%.** Vào lệnh ngẫu nhiên SL3/TP4.5/60 nến M1 → thắng 40,1% (mua) và 44,1% (bán), n=6.526 mỗi phía. Hoà vốn toán học của 1,5R = 40,0%. | đo 2026-08-18 |
| 0.6 | **Mốc HVN ngày, chạm trơn không lọc gì: 41,2% (n=51)** — nằm trong nền. Đối chứng mức ngẫu nhiên 48,7% (n=39), giá đóng cửa hôm trước 41,9% (n=62). ⇒ chưa có bằng chứng HVN hữu ích. | đo 2026-08-18 |
| 0.7 | Luật chưa đo được → **được vẽ để đọc chart, KHÔNG được sinh signal**, và không nói như đã kiểm định. | `CLAUDE.md` §5b |
| 0.8 | Biên độ tham chiếu: nến M1 trung vị **1,2 giá** (phân vị 90 = 3,7); range ngày trung vị **102,5 giá**. Dừng lỗ 3 giá ≈ đúng một nến M1 xấu. | đo 2026-08-18 |

**Hệ quả thiết kế quan trọng nhất:** TPO thu hẹp từ 102 giá (range ngày) xuống ~10 giá; **footprint M1 mới thu nốt 10 → 3**. Indicator này **không** được hứa cho ra điểm vào chính xác 3 giá. Việc của nó: nói *chỗ nào đáng nhìn* và *bật kính lúp M1 lúc nào*.

---

## 1. Dữ liệu và cạm bẫy

**Dùng cặp file này cho mọi phép đo (đã kiểm, khớp `bar_idx`):**
- `data-export/Data_Footprint_Export.csv` — 182.845 dòng, **từng mức giá**, 2026-02-03 → 07-31, 128 phiên.
  Header: `bar_idx,datetime,price,bid_vol,ask_vol,volume,delta,trades,buy_trades,sell_trades,max_one_trade`
- `data-export/Data_Footprint_Export_bars.csv` — 45.736 nến **M1** cùng khoảng, có `open,high,low,close,delta,cum_delta,…`

**Cạm bẫy phải xử lý:**
1. **Múi giờ cột `datetime` CHƯA XÁC ĐỊNH.** Bước A0.1 bắt buộc: tìm khoảng trống dài nhất trong tuần (CME nghỉ ~60 phút/ngày + ~46 giờ cuối tuần) để suy ra cột này là UTC hay giờ khác. Sai bước này thì mọi bộ lọc theo phiên đều vô nghĩa — **lỗi này đã từng xảy ra** (bộ lọc phiên chết của RunnerSignal v5 vô hiệu vì tưởng giờ VN nhưng thực tế là UTC).
2. **Không nối nhiều file thành chuỗi liên tục.** Giá giữa các file có thể là hợp đồng khác (5086 vs 4041). Chỉ dùng đúng cặp file trên.
3. **Dữ liệu là GCQ26, chart người dùng đọc là GCZ26.** Kết quả đo chỉ áp cho hợp đồng đã đo; muốn chống khớp quá mức (overfit) thì cần một hợp đồng thứ hai — ghi vào phần hạn chế, đừng im lặng.
4. **`max_one_trade`**: kiểm xem đỉnh khối lượng có phải do MỘT lệnh khối lớn (khớp phiên/settlement) tạo ra không. Nếu >30% khối lượng của mức đỉnh đến từ một lệnh thì mốc đó là hiện tượng kỹ thuật, phải loại.
5. **BÀI SỐ 0 chưa xong** (chart TPO neo Globex 05:00 thay vì pit ~19:20 VN). Python **tự neo được** nên vẫn đo IB được; nhưng **mọi kết quả liên quan IB không được đem lên chart** cho tới khi sửa neo phiên.

---

## 2. Nhánh A — ĐO (Python, offline). Làm cái này trước khi tin bất cứ mức nào.

Tạo **một** file dùng chung: `quantower-tpo-suite/measure_levels.py`

### A0 — Hạ tầng đo (làm trước, không có nó thì các bước sau không so sánh được)

**A0.1 Xác định múi giờ** (xem cạm bẫy 1). In ra kết luận, hard-code offset vào một hằng số có tên rõ.

**A0.2 Nạp dữ liệu**
- `daily_profile[ngày][giá_làm_tròn_1] = tổng volume`
- `bars[ngày] = [(high, low, close, delta, ...)]` theo thứ tự thời gian
- Hàm `value_area(profile, 0.70) -> (val, vah, poc)` — VA 70% quanh POC, cần cho A1

**A0.3 Giao thức thử — CỐ ĐỊNH, mọi loại mức dùng y nguyên**
```
SL = 3.0 giá · TP = 4.5 giá · chân trời = 60 nến M1
Chạm = low <= mức <= high
Hướng: tới từ TRÊN (close nến trước > mức) ⇒ thử MUA (đỡ)
       tới từ DƯỚI                        ⇒ thử BÁN (cản)
Cùng một nến chạm cả SL và TP ⇒ tính THUA (thận trọng)
Mỗi phiên chỉ lấy LẦN CHẠM ĐẦU TIÊN (biến thể: cho tối đa 3 lần, cách nhau ≥30 nến)
```
**A0.4 Bắt buộc in kèm mỗi kết quả:** `n`, tỷ lệ thắng, **khoảng tin cậy Wilson 95%**, kỳ vọng giá/lệnh, và **hai đối chứng chạy cùng lúc** (mức ngẫu nhiên trong nửa giữa range hôm trước; giá đóng cửa hôm trước).

**A0.5 Chạy luôn phiên bản ĐẢO HƯỚNG** cho mọi loại mức. Nếu đảo hướng tốt hơn thì mức đó là **mức đi tiếp**, không phải mức bật lại — đó là phát hiện, không phải lỗi.

**Tiêu chí ĐẠT (dùng chung, đừng nới):**
- `n >= 30`, và **biên dưới Wilson 95% > 40%**. Không đạt cả hai ⇒ ghi "CHƯA ĐỦ CA" hoặc "KHÔNG ĐẠT", **không** được viết thành "có hiệu quả".

---

### A1 — Thí nghiệm CHÍNH: điều kiện hoá. Đây là chỗ khả năng cao hiệu ứng đang bị pha loãng.

Giả thuyết: mốc HVN ra 41,2% vì **trộn các chế độ có nghĩa ngược nhau** vào một rổ (Buổi 6).

Chia rổ theo **ba trục, đo từng trục riêng trước, rồi mới bắt cặp**:

**Trục 1 — chế độ thị trường (Buổi 6).** Phân loại phiên D:
- `balance` nếu VA(D−1) và VA(D−2) **chồng nhau ≥ 50%** (tính theo độ dài giao/độ dài hợp)
- `sau_balance` nếu có `balance` ở D−2/D−3 nhưng VA(D−1) **rời hẳn** (giao = 0)
- `khác` = còn lại
Kỳ vọng nếu Buổi 6 đúng: trong `balance` thì bật lại (thuận hướng A0.3); trong `sau_balance` thì đi tiếp (thuận hướng đảo A0.5).

**Trục 2 — phiên trong ngày.** Á / Âu / Mỹ theo mốc đã xác định ở A0.1. Giả thuyết: chạm trong phiên Á là nhiễu.

**Trục 3 — hướng bias.** Chỉ giữ ca mà mốc nằm **cùng phía** với xu hướng (proxy đã dùng ở RunnerSignal v5: `close` so với `close` 480 nến trước).

Sau khi có kết quả từng trục: **chỉ bắt cặp trục nào tự nó đã có dấu hiệu**, và **báo số rổ đã thử** để người đọc tự chiết khấu khả năng bịa (thử 20 rổ thì 1 rổ "đạt" là chuyện bình thường).

---

### A2 — So sánh các loại mốc (cùng giao thức A0)

| Loại mốc | Lấy từ đâu | Ghi chú |
|---|---|---|
| HVN ngày | đỉnh volume phiên trước, bin 1 giá | đã đo: 41,2% n=51 |
| **POC theo THỜI GIAN** | mức có nhiều nến M1 chạm nhất phiên trước | **khác HVN** — TPO đo thời gian, không đo khối lượng. Chưa từng đo riêng |
| naked POC | POC phiên cũ chưa bị giá chạm lại | code đã có `ProfileEngine.IsNaked` |
| Cụm POC | POC ≥2 phiên nằm trong ±7 tick | code đã có `ClusterPocs` |
| Đỉnh/đáy phiên trước | high/low | mức chính xác bẩm sinh |
| Biên IB | 60 phút đầu phiên pit | ⚠ chỉ đo, chưa được lên chart (cạm bẫy 5) |
| Mép single print | dải chỉ có 1 bracket TPO (Buổi 4) | cần dựng TPO từ M1 |
| **Số tròn $10 và $50** | 4100, 4110… và 4100, 4150… | rẻ nhất, chưa từng đo, đáng nghi là mạnh với vàng |
| Mép LVN | nơi khối lượng chuyển từ mỏng sang dày | Buổi 5 |
| **S/R thực nghiệm (đối chứng mạnh)** | mức mà trong 20 phiên trước giá đã đảo ≥5 giá **từ 2 lần trở lên** | không dùng lý thuyết gì. **Nếu cái này thắng HVN thì indicator nên vẽ cái này** |

---

### A3 — Độ nhọn của mốc, dùng làm bộ lọc (đây là cầu nối sang giao diện)

Với mỗi mốc, tính `nen_90` = bề rộng (giá) của tập các mức có volume ≥ 90% đỉnh.
Chia rổ `nen_90 ≤ 1` / `2–4` / `> 4` và đo riêng.

Giả thuyết: **mốc nhọn phản ứng tốt hơn mốc bẹt.** Nếu đúng → indicator có được **một con số độ tin để hiển thị**, và có cơ sở để **từ chối vẽ** mốc bẹt (mục B4). Nếu sai → bỏ ý tưởng này, đừng vẫn code cho đẹp.

### A4 — Độ ổn định của mốc, dùng làm bộ lọc

`do_doi` = |mốc(D−1) − mốc(D−2)|. Chia rổ `≤2 giá` (xác nhận 2 phiên) / `>2 giá`. Đây là kiểm định cho ý tưởng "cụm POC" đã có trong code.

### A5 — Chỉ làm nếu A1–A4 tìm ra rổ nào ĐẠT: thêm xác nhận M1

Trên các ca đã ĐẠT, thêm điều kiện bấm nút và xem tỷ lệ thắng tăng thêm bao nhiêu: phân kỳ delta tại điểm chạm · hấp thụ (khối lượng lớn, giá không đi) · dùng lại logic hợp lưu của dự án Entry Signal M1. **Không làm bước này trước A1** — tối ưu điểm vào cho một mức vô giá trị chỉ ra khớp quá mức.

### A6 — Báo cáo
- Ghi `quantower-tpo-suite/MEASURE-LEVELS-RESULTS.md`: một bảng, đủ `n` + Wilson + verdict `ĐẠT / KHÔNG ĐẠT / CHƯA ĐỦ CA`, **và số rổ đã thử**.
- Cập nhật bảng theo dõi cuối `tpo/EVIDENCE-DRILLS.md` (các dòng LVN⇒trend, HVN vùng canh lệnh).
- Ghi tiến độ vào `progress.md`.

---

## 3. Nhánh B — SỬA INDICATOR (C#). B1–B4 không cần chờ nhánh A.

File: `quantower-tpo-suite/SessionZones.cs` (677 dòng) + `ProfileEngine.cs` (929 dòng).

### B1 — Sửa bán kính lọc tầm với ⭐ tác động lớn nhất, rẻ nhất
- **Hiện trạng:** `SessionZones.cs:545` → `radius = ZoneRangeAtr * Math.Max(atr, tick)` với `ZoneRangeAtr = 3.0`. Biên độ M30 khoảng 16,7 giá ⇒ **bán kính ≈ 50 giá**. Với dừng lỗ 3 giá thì mức cách 50 giá là chuyện tuần sau — đây là lý do chart đầy mà không dùng được.
- **Sửa:** thêm input `ZoneRadiusPrices` (double, mặc định **12**, đơn vị "giá"; `0` = quay về cách cũ ×ATR). `radius = ZoneRadiusPrices * 10 * tick` khi >0.
- Áp cho cả dòng 545 và dòng 555 (LVN).

### B2 — Nhãn phải nói khoảng cách
- `SessionZones.cs:650` đang vẽ `z.Label` trơn. Thêm hậu tố `· cách {d:0.0} giá` với `d = |z.Center − nowPrice| / (10*tick)`.
- Trong bảng phiên (`SessionZones.cs` khối panel ~248-265) sắp xếp mốc **theo khoảng cách tăng dần**, không theo điểm mạnh — người dừng lỗ 3 giá cần biết cái gần nhất trước.

### B3 — Tách HAI LỚP hiển thị
- **Lớp MỐC** (vẽ đường mảnh + nhãn): naked POC · HVN ngày · cụm POC · đỉnh/đáy phiên. Giữ nguyên `Lo = Hi = p` — **không cần sửa `FindHvn`** cho lớp này (chốt 0.2).
- **Lớp NỀN** (vẽ dải mờ, không nhãn hoặc nhãn nhỏ): HVN gộp 3 tuần · LVN. Đây là chỗ **duy nhất** cần Lo/Hi thật.
- Thêm input `ShowContextBands` (bool, mặc định true) và một màu riêng rất nhạt.
- `OnPaintChart` (`SessionZones.cs:602`): vẽ lớp nền TRƯỚC (FillRectangle như dòng 634), lớp mốc SAU, để mốc không bị nền phủ.

### B4 — Độ nhọn, và indicator TỪ CHỐI vẽ mốc bẹt ⭐ đây là câu trả lời cho "50 giá thì quá to"
- Thêm `ProfileEngine.PeakSharpness(rows, peakPrice, tick, frac = 0.90) -> double` trả bề rộng nền tính bằng **giá** (không phải tick).
- Thêm input `MaxLevelThicknessPrices` (double, mặc định **4** — bằng đúng dừng lỗ của người dùng).
- Luật: `nen_90 <= MaxLevelThicknessPrices` ⇒ được làm **mốc**; lớn hơn ⇒ **tự động hạ xuống lớp nền**, và bảng phiên ghi rõ *"không có mốc rõ ở vùng này"*.
- Nhãn ghi kèm: `HVN ngày 4402 · nền 1 giá` (nhọn) hoặc `· nền 22 giá` (bẹt).
- ⚠ Chỉ bật luật hạ cấp này thành **mặc định** sau khi A3 xác nhận mốc nhọn thật sự tốt hơn. Trước đó để input `SharpnessGate` mặc định **tắt**, chỉ hiển thị con số.

### B5 — Cảnh báo tiếp cận (sau A1)
> Với dừng lỗ 3 giá, thứ quyết định không phải là biết mức, mà là **có đang nhìn màn hình đúng lúc**.
- Input: `AlertApproachPrices` (mặc định 3) · `AlertCooldownMinutes` (mặc định 15).
- Điều kiện: `|nowPrice − mốc| <= AlertApproachPrices` và chưa báo mốc đó trong thời gian nguội.
- Nội dung tin: mốc · khoảng cách · độ nhọn · chế độ balance/sau-balance (nếu A1 dùng được) · câu chốt "bật M1".
- **Bắt buộc tôn trọng `TeleIsSender`** — chỉ 1 tab được gửi, nếu không sẽ ra 3 tin trùng.

### B6 — Mốc gộp 3 tuần (ưu tiên thấp nhất)
- `SessionZones.cs:466-478` đang lấy **một** tuần CME đã đóng (`weekSpans[Count-2]`). Đổi sang gộp **3 tuần** đã đóng.
- **Chỉ dùng cho lớp NỀN** (chốt 0.4 — nó trôi 20 giá/tuần).
- Cần ≥4 tuần nến M30 trong `hd`; không đủ thì rơi về cách hiện tại và ghi chú trên bảng.

### B7 — KHÔNG làm
- Không thêm VWAP (chốt 0.3).
- Không code luật "LVN⇒trend / HVN⇒sideway" thành signal (chốt 0.7) — chỉ hiển thị.
- Không đổi `RowTicks` (2 tick = 0,2 giá, không phải điểm nghẽn).
- Không nới `FindHvn` thành vùng cho lớp mốc (chốt 0.2).

---

## 4. Thứ tự thực thi

| Giai đoạn | Việc | Điều kiện xong |
|---|---|---|
| **1** | B1, B2, B3, B4 (phần hiển thị số nhọn, cổng còn tắt) | Build sạch; chart chỉ còn mốc trong 12 giá; mọi nhãn có khoảng cách; nền và mốc phân biệt được bằng mắt |
| **2** | A0 → A1 → A2 (song song được với việc deploy giai đoạn 1) | `MEASURE-LEVELS-RESULTS.md` có bảng đủ Wilson + số rổ đã thử |
| **3** | A3, A4 | Biết mốc nhọn/ổn định có tốt hơn không ⇒ quyết bật `SharpnessGate` hay bỏ |
| **4** | Theo kết quả: nâng/hạ loại mốc trong `FindZones`; B5 cảnh báo | Loại nào không ĐẠT thì xuống lớp nền, không được làm mốc |
| **5** | A5, B6 | — |

**Đối soát Python ↔ C# (bắt buộc, dự án đã có tiền lệ lệch):** sau B4, chọn 3 phiên cụ thể, in `nen_90` và mốc từ Python, so với giá trị C# in ra bảng. Lệch ⇒ dừng, sửa, đừng đi tiếp.

**Build & deploy:** `./build-tpo.sh zones` → `dist/SessionZones.dll` → chép sang máy Windows tay. Nhớ: **chưa từng test live**, phải nhìn mắt vài phiên rồi hiệu chỉnh `ZoneRadiusPrices` và `MaxLevelThicknessPrices`.

**Commit + push sau MỖI bước có sửa file** (kể cả file Python và DLL) — `CLAUDE.md` §4.

---

## 5. Rủi ro và cách phát hiện sớm

| Rủi ro | Dấu hiệu | Xử |
|---|---|---|
| **Khớp quá mức do thử nhiều rổ** — nguy hiểm nhất ở A1 | có rổ đạt 55% với n=31 sau khi thử 20 rổ | luôn báo số rổ đã thử; rổ nào đạt thì kiểm lại trên hợp đồng/khoảng thời gian khác trước khi lên chart |
| Bán kính 12 giá quá chặt ⇒ chart trống nhiều hôm | nhiều phiên không mốc nào | **không phải lỗi** — đó là indicator nói thật "không có gì đáng canh gần đây". Chỉ nới nếu nhìn mắt thấy bỏ sót ca thật |
| `n` nhỏ ở mọi rổ (chỉ 128 phiên, mỗi phiên 1 lần chạm) | n < 30 khắp nơi | dùng biến thể 3 lần chạm/phiên ở A0.3; hoặc xuất thêm dữ liệu — **không** hạ tiêu chí |
| Đỉnh volume là do một lệnh khối lớn | `max_one_trade` chiếm >30% mức đỉnh | loại ca đó, ghi số ca bị loại |
| Tưởng đã kiểm định trong khi chưa | văn viết "HVN hiệu quả" | tuân 0.7 — chỉ có `ĐẠT/KHÔNG ĐẠT/CHƯA ĐỦ CA` |

## 6. Câu còn treo, cần người dùng trả lời (không chặn giai đoạn 1)

Dừng lỗ 3 giá là **cố định**, hay **đặt ra ngoài mép mốc**? Nếu đặt ngoài mép thì bề rộng mốc **chính là** dừng lỗ, và `MaxLevelThicknessPrices = 4` trở thành ràng buộc cứng chứ không phải tuỳ chọn.
