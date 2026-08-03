# Thuật toán vẽ Wyckoff trong WyckoffRunner — giải thích bằng lời để review

> Mục đích: mô tả **đúng những gì code đang làm** bằng ngôn ngữ dễ đọc, để tự chấm điểm xem
> indicator vẽ Wyckoff đúng hay sai. Không phải lý thuyết Wyckoff chung chung.
>
> Code tương ứng: [`quantower-entry-signal/WyckoffRunner.cs`](../quantower-entry-signal/WyckoffRunner.cs)
> — hàm `ScanWyckoff()` (dòng 1208–1522), `WyTryLpsAndPhaseE()` (1153), `WyEmitLps()` (1191),
> `DrawWyckoff()` (2590).
>
> Cập nhật: 2026-08-03 (bản v3, sau khi thêm danh sách range + kính lúp).

---

## 0. Tóm tắt một câu

Máy quét từ nến cũ nhất tới nến mới nhất, tìm **một cú climax** để mở range, chờ **cú bật ngược (AR)**
để có đủ hai biên, rồi theo dõi hai biên đó cho tới khi có **cú rũ được xác nhận** và **cú phá vỡ đi đủ xa** —
lúc đó range mới coi là hoàn tất.

---

## 1. Nguyên liệu: mỗi nến M1 được đo 4 thứ

| Đại lượng | Cách tính | Dùng để làm gì |
|---|---|---|
| **Biên độ nến** | `High − Low` | nhận diện nến climax bất thường |
| **VSA** | khối lượng nến ÷ TB khối lượng **20 nến** gần nhất | 2.2x = climax, 3.3x = climax cực mạnh |
| **Tỉ lệ thân** | `\|Close − Open\| ÷ biên độ` | phân biệt phá vỡ dứt khoát (thân to) vs râu lừa (thân nhỏ) |
| **Xu hướng nền** | Close hiện tại vs Close **480 nến trước** (≈8 giờ) | bộ lọc bối cảnh, thay cho TPO bias |

Xu hướng nền trả về `+1` (tăng), `−1` (giảm) hoặc `0` (đi ngang, chênh ≤ 1 giá).

Dung sai tính bằng **tick**. Với vàng: **1 giá = 10 tick**.

---

## 2. Máy trạng thái tổng thể

```
        [rỗi]
          │  climax + đúng xu hướng nền
          ▼
     ┌─ Phase A ─┐  chờ 40 nến tìm AR
          │
          ▼
     ┌─ Phase B ─┐◄────────────┐  test hai biên (giai đoạn dài nhất)
          │                    │
   Spring/UTAD                 │ cú rũ THẤT BẠI
          ▼                    │ hoặc phá vỡ HỎNG
     ┌─ Phase C ─┐─────────────┤
          │                    │
      SOS / SOW                │
          ▼                    │
     ┌─ Phase D ─┐─────────────┘
          │  giữ biên + đi đủ xa
          ▼
     ┌─ Phase E ─┐  → range HOÀN TẤT, đóng lại
```

Lưu ý: **Phase B ⇄ C ⇄ D có thể quay lui**, không phải đường một chiều. Một range có thể ghi
nhiều Spring thất bại rồi mới có Spring thật.

---

## 3. Chế độ rỗi — điều kiện mở một range mới

Chỉ tìm **một cú climax**, phải thoả **cả ba**:

1. Biên độ nến ≥ **1.4 lần** biên độ trung bình 20 nến trước.
2. VSA ≥ **2.2x**.
3. Màu nến khớp với xu hướng nền:
   - nến **đỏ** + xu hướng nền **giảm** → mở **range TÍCH LUỸ**, đánh dấu **SC** (Selling Climax) tại **đáy** nến.
   - nến **xanh** + xu hướng nền **tăng** → mở **range PHÂN PHỐI**, đánh dấu **BCLX** tại **đỉnh** nến.

> **Vì sao bắt buộc điều kiện 3:** một cú bán tháo giữa xu hướng tăng **không phải** Selling Climax,
> nó chỉ là nhịp chỉnh. Bỏ điều kiện này là lỗi hay gặp nhất khi gán SC/BCLX trong tái tích luỹ.

Range mới bắt đầu ở **Phase A**, mới chỉ có **một biên** (đáy climax cho tích luỹ / đỉnh climax cho phân phối).

---

## 4. Phase A — tìm cú bật ngược AR để có biên thứ hai

Chờ đúng **40 nến** sau climax. Trong cửa sổ đó:

- Range tích luỹ → tìm **đỉnh cao nhất** = **AR** (Automatic Rally) → thành **biên trên**.
- Range phân phối → tìm **đáy thấp nhất** = **AR** (Automatic Reaction) → thành **biên dưới**.

Song song, biên **cùng phía climax** vẫn được nới thụ động mỗi nến (giá còn xuống thấp hơn thì đáy hạ theo).

**Nhãn "AR (yếu)":** nếu AR rơi vào 1–2 nến ngay sát climax → nhiều khả năng chỉ là một cây râu
nhiễu chứ không phải cú bật thật. Đây **chỉ là cảnh báo hiển thị**, không đổi logic.

Xong: range có đủ 2 biên → chuyển **Phase B**, mốc bắt đầu là **nến ngay sau AR** (không phải cuối cửa sổ 40 nến).

---

## 5. Phase B — test hai biên, giai đoạn dài nhất

Mỗi nến xét **biên dưới và biên trên độc lập nhau**, cả hai trong cùng một vòng lặp.
Mọi sự kiện đều yêu cầu cách sự kiện trước **≥ 5 nến** (tránh đánh dấu chi chít cùng một cú).

### 5.1 Biên dưới

| Nến làm gì | Range TÍCH LUỸ | Range PHÂN PHỐI |
|---|---|---|
| Xuyên thủng đáy rồi **đóng cửa quay lại trong range** | **Spring** → Phase C<br>(xuyên sâu ≥ 15 tick **hoặc** VSA ≥ 3.3x → gọi **Shakeout**) | **DA** — test không quyết định, **ở lại Phase B**<br>(sâu → "DA (sâu)") |
| Chạm đáy trong sai số **10 tick** | **ST** (Secondary Test) | **ST** |
| **Đóng cửa hẳn** dưới đáy quá **30 tick**, thân ≥ **45%** | Giả thuyết tích luỹ **SAI** → **huỷ cả range** | **SOW** (Sign of Weakness) → Phase D |
| Chỉ xuống thấp hơn bình thường | nới đáy range xuống | nới đáy range xuống |

### 5.2 Biên trên (đối xứng)

| Nến làm gì | Range TÍCH LUỸ | Range PHÂN PHỐI |
|---|---|---|
| Vượt đỉnh rồi **đóng cửa thụt lại trong range** | **UA** — test không quyết định, **ở lại Phase B**<br>(mạnh → "UA (mạnh)") | **UT**; nếu vượt ≥ 15 tick **hoặc** VSA ≥ 3.3x → **UTAD** → Phase C |
| Chạm đỉnh trong sai số **10 tick** | **ST** | **ST** |
| **Đóng cửa hẳn** trên đỉnh quá **30 tick**, thân ≥ **45%** | **SOS** (Sign of Strength) → Phase D | Giả thuyết phân phối **SAI** → **huỷ cả range** |
| Chỉ lên cao hơn bình thường | nới đỉnh range lên | nới đỉnh range lên |

> **Điểm cần soi kỹ khi chấm:** Spring/UTAD **chỉ được gọi khi nến đó thật sự phá đáy/đỉnh
> thấp/cao nhất từ trước tới giờ**, vì hai biên được cập nhật liên tục suốt Phase B. Gọi Spring cho
> một cái đáy **không** phá đáy cũ là lỗi phổ biến nhất khi chấm Wyckoff bằng mắt — code không mắc lỗi này.

> **Chỉ một phía là "quyết định":** với tích luỹ, chỉ cú rũ ở **biên dưới** mới mở Phase C
> (biên trên chỉ ghi UA). Với phân phối thì ngược lại. Đây là bản chất Wyckoff: chân của cấu trúc
> tích luỹ nằm ở dưới.

---

## 6. Phase C — chờ xác nhận cú rũ (không tin ngay)

Sau Spring/Shakeout/UTAD, máy đo giá đã đi được **bao nhiêu phần đường từ điểm rũ sang biên đối diện**:

- Đi được **≥ 50% quãng đường** → cú rũ **XÁC NHẬN** (chấm viền trắng đậm).
- Giá quay lại **đóng cửa vượt qua điểm rũ** trong khi **chưa đi nổi 50%** → cú rũ **THẤT BẠI**:
  nhãn thêm "(thất bại)", vẽ **xám**, range **lùi về Phase B** chờ cú rũ mới — **không huỷ range**.
- Đang chờ mà giá quay về test đúng vùng điểm rũ → đánh dấu **LPS[C]** (tích luỹ) / **LPSY[C]** (phân phối).

Trong lúc chờ, hai biên vẫn được nới thụ động theo cực trị thật (nếu không, một SOS sau đó sẽ bị
so với biên **cũ** — sai).

Từ Phase C, nến đóng cửa vượt biên với thân ≥ 45% → **SOS/SOW** → **Phase D**.

---

## 7. Phase D → E — kiểm tra cú phá có thật không

Ngay khi có SOS/SOW, máy nhìn tới **25 nến kế tiếp** và hỏi hai câu:

**Câu 1 — giá có GIỮ được biên vừa phá không?**
Nếu có một nến **đóng cửa lùi hẳn** quay vào trong range quá **30 tick** → phá vỡ hỏng → quay lại Phase B.
(Chỉ tính khi **đóng cửa** lùi qua; một cây râu chạm nhẹ không tính.)

**Câu 2 — giá có đi ĐỦ XA không?**
Mốc: đi thêm **bằng đúng chiều cao range**. Đạt → chốt **Phase E**, range **hoàn tất và đóng lại**.

**Nếu hết 25 nến mà chưa đạt:**
- Đã đi được **≥ 50% chiều cao range** → vẫn cho chốt Phase E.
- **< 50%** → coi như SOS/SOW quá yếu → **quay lại Phase B** chờ cú phá khác.

**LPS[D] / LPSY[D]:** những nến trong 25 nến đó đóng cửa loanh quanh biên vừa phá (trong **20 tick**)
được gom lại — hồi về test lại biên. Từ **3 nến trở lên** vẽ thành **một vùng**, dưới 3 nến vẽ **một điểm**.

> Phân biệt hai loại LPS (đặt tên khác nhau có chủ đích):
> - **LPS[C] / LPSY[C]** = test **trong lúc chờ xác nhận cú rũ**, tức **trước** SOS/SOW.
> - **LPS[D] / LPSY[D]** = hồi test **sau** SOS/SOW.

---

## 8. Ba điều kiện huỷ range giữa chừng

| Điều kiện | Ngưỡng | Lý do |
|---|---|---|
| Range quá cao | chiều cao > **3.5% giá** | range Wyckoff là vùng **cân bằng hẹp**, không phải cả một xu hướng dài |
| Kéo quá dài ở Phase A/B/C | > **2500 nến** | như trên |
| Kéo quá dài ở Phase D | > **2000 nến** | như trên |

⚠️ Ba mốc này là **guard tự đặt, KHÔNG có trong tài liệu Wyckoff gốc**. Muốn chỉnh độ nhạy thì đây là chỗ chỉnh.

---

## 9. Range chưa xong

Nếu quét tới nến cuối cùng mà range chưa đạt Phase E, nó **vẫn được vẽ** nhưng:
- gắn nhãn **"(đang chạy)"** trong danh sách range của bảng,
- Phase cuối cùng kéo dài tới nến hiện tại.

Nến **đang hình thành** (nến cuối chưa đóng) luôn bị bỏ qua, giống phần quét tín hiệu vào lệnh.

---

## 10. Phần vẽ trên chart

- **Khung range**: chữ nhật kéo từ nến climax tới nến kết thúc. **Xanh = tích luỹ, đỏ = phân phối**.
- **Dải Phase**: các đoạn **A / B / C / D / E** theo trục thời gian, nằm dưới khung.
- **Sự kiện**: một chấm + nhãn tại **đúng giá** của nó, màu theo nhóm (climax / bật ngược / test /
  rũ / phá vỡ / hồi test). Chú giải 7 màu vẽ sẵn trên chart.
- **Viền chấm = trạng thái**: trắng đậm = **đã xác nhận**, nét đứt = **đang chờ**, xám = **thất bại**.

> **Một điểm quan trọng để chấm cho đúng:** biên range hiển thị là **biên CUỐI CÙNG**, tức đã gồm
> mọi lần Spring/UT nới rộng ra. Nên một cú Spring nhìn trên chart sẽ **nằm ngay trên mép dưới**
> chứ không thò hẳn ra ngoài — vì chính nó đã đẩy mép xuống. **Đây là hành vi cố ý, không phải lỗi vẽ.**

---

## 11. Bảng tham số — tra nhanh khi muốn chỉnh

| Tham số | Giá trị | Nơi dùng |
|---|---|---|
| Biên độ climax | ≥ **1.4×** TB 20 nến | mở range |
| VSA climax | ≥ **2.2x** | mở range |
| VSA climax cực mạnh | ≥ **3.3x** (1.5 × 2.2) | phân biệt Spring↔Shakeout, UT↔UTAD |
| Cửa sổ tìm AR | **40 nến** | Phase A |
| Sai số chạm biên (ST) | **10 tick** | Phase B |
| Giãn cách tối thiểu giữa 2 sự kiện | **5 nến** | mọi Phase |
| Độ sâu để gọi Shakeout/UTAD | **15 tick** | Phase B |
| Đóng cửa "lùi hẳn" qua biên | **30 tick** | Phase B, D |
| Thân nến tối thiểu để công nhận SOS/SOW | **45%** | Phase B, C, D |
| Tiến độ để xác nhận cú rũ | **50%** quãng đường sang biên đối diện | Phase C |
| Cửa sổ chờ sau SOS/SOW | **25 nến** | Phase D |
| Đích Phase E | đi thêm **1.0 × chiều cao range** | Phase D |
| Đích Phase E tối thiểu (khi hết giờ) | **0.5 × chiều cao range** | Phase D |
| Số nến tối thiểu để LPS[D] thành **vùng** | **3 nến** | Phase D |
| Sai số gom LPS[D] | **20 tick** | Phase D |
| Chiều cao range tối đa | **3.5% giá** | huỷ range |
| Số nến tối đa Phase A/B/C · Phase D | **2500 · 2000** | huỷ range |
| Số range gần nhất hiển thị | **40** (chỉnh được tới 300) | phần vẽ |

---

## 12. Danh sách những chỗ nên nghi ngờ khi review

1. **Ngưỡng 1.4× biên độ + 2.2x VSA** — có thể quá lỏng ở phiên Á (thanh khoản thấp, VSA dễ vọt),
   khiến mở range rác. Xem có range nào mở giữa đêm không.
2. **Cửa sổ AR cố định 40 nến** — nếu AR thật xảy ra ở nến thứ 45 thì máy bắt nhầm.
3. **Xu hướng nền 480 nến** — proxy TPO thô, chỉ so hai điểm đầu-cuối, không nhìn hình dạng ở giữa.
4. **Ba guard huỷ range** (3.5%, 2500, 2000 nến) — hoàn toàn tự đặt, chưa hiệu chỉnh bằng số liệu.
5. **Ngưỡng 15 tick phân biệt Spring↔Shakeout** — con số cứng, không co giãn theo biến động thị trường.
6. **Không dùng dữ liệu order flow** — toàn bộ phần Wyckoff này chỉ đọc OHLC + khối lượng, **chưa**
   dùng delta / bid-ask từng mức giá, dù indicator có sẵn dữ liệu đó.

---

## 13. ĐO THẬT trên dữ liệu tháng 7/2026 — kết quả gây bất ngờ

Đã dựng chart M1 thật của tháng 7 rồi chạy đúng thuật toán này lên đó:
**[wyckoff-chart-thang7.html](wyckoff-chart-thang7.html)** (mở bằng trình duyệt, cuộn/zoom được).

Dữ liệu: dxFeed **GCQ26**, 2026-06-29 → **2026-07-27 15:56 UTC**, 27.316 nến M1.
dxFeed chỉ xuất tới 27/7; file footprint export có tới 31/7 nhưng là **hợp đồng khác**
(giá lệch ~59 điểm: 4080 vs 4138) nên **không nối vào** — nối sẽ tạo khe giá giả.

![toàn cảnh tháng 7](wyckoff-schematic-examples/html-thang7-toan-canh.png)

### 13.1 Con số

| | Toàn lịch sử (11/2025 → 27/7/2026, 103.857 nến) | Riêng tháng 7 (25.493 nến) |
|---|---|---|
| Nến thoả **biên độ ≥1.4×** | 21.683 | — |
| Nến thoả **VSA ≥2.2x** | 8.738 | — |
| Thoả **cả hai + đúng xu hướng nền** | 3.491 | 816 |
| Range thực sự **được mở** | **120** | ~13 |
| Range **được vẽ** | **3** | **1** |
| Range **bị bỏ giữa chừng** | **117** | **12** |

Lý do bỏ (toàn lịch sử): **61** vì "Phase B đóng cửa phá sai hướng → bỏ giả thuyết",
**56** vì guard quá cao/quá dài. Chỉ **2** range đi hết tới Phase E — và cả hai đều ở **tháng 1–2**.

### 13.2 Tháng 7 chỉ có ĐÚNG 1 range được vẽ

`ACC 23/07 22:42 → 27/07 15:56 · 4024.0–4119.3 · Phase A→B→C→B→D→B→D→B · 46 mốc · đang chạy`

Nghĩa là: lời phàn nàn "chỉ thấy range mới nhất" **không phải lỗi hiển thị** — cả tháng 7
thật sự chỉ có **một** range, và nó là cái cuối cùng, vẫn đang chạy. Việc nâng trần hiển thị
từ 6 lên 40 range ở bản v3 **không giải quyết được gì**, vì có tới 40 range đâu mà hiện.

### 13.3 Cơ chế thoái hoá — đây mới là vấn đề thật

12 ứng viên bị bỏ trong tháng 7 nối đuôi nhau **phủ gần kín cả tháng**, và **8/12 chết đúng
tại mốc 2501 nến** (trần 2500):

```
29/06 16:32 → 01/07 12:18   2501 nến   quá dài
01/07 13:17 → 03/07 01:08   2027 nến   Phase B phá sai hướng
03/07 01:09 → 05/07 23:28   1037 nến   Phase B phá sai hướng
06/07 00:01 → 07/07 18:56   2501 nến   quá dài   ← Phase A→B→C→B→C→B→C→B→C→B→C→B→C
08/07 09:43 → 10/07 05:35   2501 nến   quá dài
10/07 06:00 → 14/07 01:47   2501 nến   quá dài
...
```

Ba điều đọc được từ đây:

1. **Mỗi lúc chỉ có ĐÚNG MỘT range được theo dõi.** Khi một ứng viên đang mở, mọi climax mới
   đều bị bỏ qua. Ứng viên đó sống tới 2500 nến (~2 ngày) rồi mới bị guard giết → suốt 2 ngày
   đó thuật toán **mù**. Đây là lý do 816 nến climax hợp lệ trong tháng 7 chỉ đẻ ra ~13 range.
2. **Range phình quá to.** Ứng viên `22/07` cao 128.9 giá, range được vẽ cao 95.3 giá — trên nền
   giá ~4050 là 2.4–3.2%, lọt guard 3.5% nhưng **không còn là "vùng cân bằng hẹp"** nữa. Nó
   đang bao trọn cả một xu hướng, đúng thứ mà chú thích trong code nói là phải tránh.
3. **Vòng lặp C→B không thoát được.** Ứng viên `06/07` chạy `A→B→C→B→C→B→C→B→C→B→C→B→C` —
   Spring/UTAD liên tục được gán rồi liên tục thất bại, không lần nào đủ 50% tiến độ.
   Range chỉ chết vì hết hạn 2500 nến, chứ tự nó không bao giờ kết luận.

### 13.4 Trang HTML có gì để review

Hai tab bên trái: **Được vẽ (1)** và **Bị bỏ (12)** — tab thứ hai là thứ đáng xem, vì đó là
những chỗ thuật toán đã thử và đầu hàng, kèm **lý do bỏ** ghi thẳng trên từng dòng.
Bấm một dòng thì chart nhảy tới và fit đúng range đó; bật "Vẽ cả ứng viên bị bỏ" để thấy
chúng nằm xám mờ trên nền chart. Mỗi dòng có 3 nút ✓ / ? / ✗ để tự chấm, lưu trong trình
duyệt, bấm "Xuất ghi chú chấm điểm" để lấy ra JSON.

![tab ứng viên bị bỏ](wyckoff-schematic-examples/html-thang7-ung-vien-bi-bo.png)

⚠️ Trang HTML dựng từ **bản Python** của thuật toán (`wyckoff_schematic.py`), chạy song song
với `ScanWyckoff()` bên C#. Hai bên đã được đồng bộ theo cùng một spec nhưng **chưa có test
đối chiếu tự động** — nếu thấy chỗ nào lệch với chart Quantower thì báo, đó là lỗi parity.

Script dựng lại trang: `quantower-entry-signal/research/wyckoff/v8/wyckoff/render_wyckoff_html.py`.

---

## 14. Liên quan

- [wyckoff-schematic-tinh-nang-moi.md](wyckoff-schematic-tinh-nang-moi.md) — lịch sử tính năng, bản v2/v3, bảng tương tác.
- [wyckoffrunner-setup-va-kich-ban.md](wyckoffrunner-setup-va-kich-ban.md) — phần **vào lệnh** (CBR, quay đầu), **tách hẳn** khỏi phần vẽ Wyckoff này.
- [wyckoff-schematic-examples/](wyckoff-schematic-examples/) — ảnh minh hoạ.
