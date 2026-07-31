# Khung 3 kịch bản của CORVEN (Messenger "Trương Linh", 2026-07-31)

> **Nguồn:** 3 ảnh chat Messenger người học gửi ngày 2026-07-31 (13:30 → 13:43).
>
> ⚠️ **"Trương Linh" = tên Messenger của CORVEN — CÙNG MỘT NGƯỜI** với pro trader trong
> [TRANSCRIPT.md](TRANSCRIPT.md) / [RULES.md](RULES.md) (người học xác nhận 2026-07-31).
> Repo chỉ có **MỘT** pro trader, không phải hai. Không được coi hai file này là hai nguồn độc lập
> xác nhận lẫn nhau.
>
> Vai trò của file này: TRANSCRIPT/RULES cho **chi tiết vi mô** (order flow từng mức giá, SL, RR, bias
> phiên); file này cho **KHUNG XƯƠNG** còn thiếu — hệ chia làm mấy kịch bản và mỗi kịch bản neo vào
> khung thời gian nào. Hai file **ghép lại thành một hệ duy nhất** (xem §3b).
>
> Người học gọi là "chú", tự xưng "t". Ảnh gốc chưa lưu vào repo — nội dung đã trích đủ ở dưới.

---

## 1. Nguyên văn (đã sắp lại theo thứ tự chat)

**Người học hỏi:** "Hệ thống của chú có mấy kịch bản trade thế / Chạm vùng phản ứng đánh — Phá vùng rồi hồi đánh"

**CORVEN:**
> "Có 2"
> "Một là **chạm vùng lớn có thể hold dài**"
> "2 là **scap**"
> "À **có 3 kiểu**."
> "Scap có 2 kiểu — 1 là **đánh vwap**"
> "2 là **đánh follow theo orderflow**"
> "**Ngày phải vài chục lệnh đấy**"

**Người học:** "Vùng phản ứng là vùng lớn hoặc vwap à chú" · "Đánh kiểu này là sẽ như nào chú, thuần bóng nổ à"

**CORVEN:** "**Vwap tuần**" · "**Có chơi đc**" · "**Vwap ngày scap**" ·
> "**Tpo ngày thì hơi nhỏ nên t nhìn hẳn tuần cho bao quát**"

**Người học chốt lại (được xác nhận):**
> "Tức là chú chơi 3 kịch bản:
> • chạm **vùng lớn** phản ứng **hold dài**, vùng này là **vwap tuần hoặc tpo tuần**
> • đánh **scap**:
>   + chạm **vwap, tpo ngày** canh phản ứng
>   + **follow theo footprint, ko cản tàu**"

**CORVEN:** "**Uh**" · "**Đúng r**" ✅

---

## 2. Chưng cất — 3 kịch bản, phân tầng theo KHUNG

| # | Kịch bản | Vùng neo | Khung | Kiểu lệnh | Tần suất |
|---|---|---|---|---|---|
| **KB-A** | Chạm vùng LỚN → phản ứng → **hold dài** | **VWAP tuần** hoặc **TPO tuần** | Tuần | Swing / gồng | Ít |
| **KB-B** | Scalp phản ứng | **VWAP ngày**, **TPO ngày** | Ngày | Mean-revert tại vùng | Cao |
| **KB-C** | Scalp **follow order flow** | Không cần vùng — theo footprint | M1 | **Thuận đà**, "ko cản tàu" | "vài chục lệnh/ngày" |

### Ba điểm cốt lõi phải nhớ

**T1 — Khung quyết định KIỂU LỆNH, không phải kiểu vùng.**
Cùng một công cụ (VWAP, TPO) nhưng **khung tuần → hold dài**, **khung ngày → scalp**. Không phải
"vùng mạnh thì lệnh to hơn" mà là "vùng khung lớn thì **thời gian giữ** dài hơn".

**T2 — "TPO ngày thì hơi nhỏ nên t nhìn hẳn tuần cho bao quát."**
Đây là câu quan trọng nhất của cả đoạn chat. Pro trader chủ động **bỏ TPO ngày làm vùng chính** vì
biên độ quá nhỏ, chuyển lên **TPO tuần** để có cái nhìn bao quát. Khớp với ghi chú cũ trong repo:
"trader pro canh mua/bán ở **HVN tuần/ngày + VWAP**, KHÔNG dùng VAH/VAL/POC từng phiên Á-Âu".

**T3 — "follow theo footprint, KO CẢN TÀU."**
Nhánh scalp thứ hai là **thuận đà**, tuyệt đối không đứng chặn xu hướng. "Cản tàu" = fade một cú
đẩy đang có lực. Đây là lời cấm rõ ràng đối với kiểu lệnh quay đầu ngược đà.

---

## 3. Đối chiếu với số đã đo trong repo (quan trọng — đây là chỗ để học)

Khung này **trùng với kết quả backtest thật**, không phải trùng cảm tính:

| Lời pro trader | Số đo được | Nguồn |
|---|---|---|
| Vùng lớn = **khung TUẦN** | `hvn_week` là **loại vùng duy nhất dương**: n=7 WR 57% EV **+0.429** | [RESULTS_KB2_ZONES.md](../../quantower-entry-signal/research/wyckoff/RESULTS_KB2_ZONES.md) |
| "TPO **ngày** thì hơi nhỏ" | `hvn_day` là loại vùng **tệ nhất**: n=16 WR 25% EV **−0.375** | cùng trên |
| "**ko cản tàu**" | Nhánh fade KB2 = **FAIL** (EV sụp về ≈0); nhánh thuận đà KB1 = PASS (+47R) | [AUDIT_V7.md](../../quantower-entry-signal/research/wyckoff/AUDIT_V7.md) |
| Scalp neo **VWAP ngày** | KB2 gốc neo VWAP phiên là bản DUY NHẤT còn dương (+10.5R); thay VWAP bằng vùng thì chết | RESULTS_KB2_ZONES §2 |
| "vài chục lệnh/ngày" | Cả 3 engine hiện chỉ **60 lệnh / 3 tháng** ≈ 1 lệnh/ngày | [BASELINE.md](../../quantower-entry-signal/research/wyckoff/BASELINE.md) |

**Kết luận đối chiếu:** cấu trúc 3 kịch bản này được số liệu ủng hộ ở 4/5 dòng. Dòng cuối là
**khoảng cách lớn nhất** giữa hệ hiện tại và hệ của pro trader: họ đánh vài chục lệnh/ngày, hệ này
đánh ~1 lệnh/ngày — thiếu hẳn **KB-C (follow order flow)**, nhánh sinh ra phần lớn số lệnh đó.

---

## 3b. GHÉP với RULES.md — một hệ duy nhất, giờ mới thấy đủ hình

Vì cùng một người, các luật rời trong [RULES.md](RULES.md) phải **gắn vào đúng kịch bản** mới hiểu
được. Trước đây ta đọc chúng như một danh sách phẳng nên bị lẫn: có luật thuộc KB-C lại đem áp cho
KB-B. Ánh xạ đúng:

| Kịch bản | Các luật RULES.md thuộc về nó |
|---|---|
| **KB-A** vùng tuần → hold dài | **Chưa có luật nào.** Cả TRANSCRIPT 36 ảnh không nói về nhánh này → đây là **vùng tối** lớn nhất trong hiểu biết hiện tại về hệ của CORVEN |
| **KB-B** scalp phản ứng VWAP/TPO ngày | **R2** (buy-limit ở *chân* sóng thì ngon, ở đỉnh là lỏ) · **R10** (vol thấp KHÔNG phải tín hiệu đảo; chỉ fade khi có cây từ chối CÓ volume) · **R8** (chờ xác nhận M5/M1) |
| **KB-C** scalp follow order flow | **R1** (leg phải do lệnh CHỦ ĐỘNG đẩy, không phải limit kê) · **R3** (loại leg do quét stop) · **R9** (chất lượng nến trong leg) · **W3/W5** ("đừng đánh UT sớm", "đánh break thôi chú") · **R7** (bóp SL 2-4 giá, RR 5-6) |
| **Xuyên suốt cả 3** | **R5** (mỗi phiên một bias, khoá theo phiên) · **R6** (RR theo entry time) · **C1** (score ~70% checklist, không AND-gate cứng) · **C2** (WR 65-70%) |

**Hai điều tôi suy ra khi ghép — CẢ HAI ĐỀU SAI, người học đã đính chính 2026-07-31:**

1. ❌ Tôi suy: *"W5 'đánh break thôi' nói về range M1 của KB-C, cấm fade biên range M1, không cấm fade
   tại VWAP ngày."* → **Sai.** "Break" nghĩa là **phá ra khỏi VÙNG (HVN) rồi chờ HỒI về + có tín hiệu**
   = break-retest, và nó là **một trong HAI play tại cùng vùng HVN** (play kia là chạm → đảo chiều).
   Không hề có chuyện "cấm fade".
2. ❌ Tôi suy: *"R7 SL 2-4 giá chỉ cho KB-C; KB-A hold dài theo vùng tuần thì SL 2-4 giá là vô nghĩa,
   áp vào sẽ bị đá stop liên tục."* → **Sai, vì tiền đề sai.** KB-A **không** phải swing: nó vào lệnh
   **trên M1** y như scalp, đóng **trong ngày**, SL neo **giống nhánh scalp chạm vùng**. Khác biệt duy
   nhất là **vùng thuộc khung tuần** nên tỉ lệ thắng cao hơn.

**Bài học chung của hai lỗi:** tôi lấy chữ "hold dài" và "break" rồi **suy diễn thêm ngữ cảnh không có
trong nguyên văn** (hold dài → swing đa ngày → SL rộng; break → range M1). Lần sau gặp từ mơ hồ thì
**hỏi**, đừng dựng ngữ cảnh. Bản chốt đúng: [CORVEN_SPEC_V1.md](CORVEN_SPEC_V1.md).

**Hệ quả về mặt bằng chứng:** vì chỉ có **một** pro trader, sự trùng khớp ở §3 **không phải hai nguồn
độc lập xác nhận nhau**. Nó là: một hệ thống chủ quan (CORVEN) + một phép đo khách quan (backtest
trong repo) cho cùng kết luận. Vẫn có giá trị, nhưng yếu hơn hai nguồn độc lập, và backtest vẫn
100% in-sample trên một cửa sổ 3 tháng.

## 4. Ánh xạ sang 3 engine đang có

| Kịch bản pro trader | Engine trong repo | Trạng thái |
|---|---|---|
| **KB-A** vùng tuần → hold dài | **CHƯA CÓ.** Gần nhất là M30SessionZones nhưng nó chỉ VẼ, không vào lệnh; và RR4 của KB1 vẫn là intraday | ⬜ trống |
| **KB-B** scalp phản ứng VWAP/TPO ngày | **KB2 QUAY_DAU** + **EntrySignal** | ⚠️ KB2 = FAIL; EntrySignal = EV +0.36R |
| **KB-C** scalp follow order flow | **KB1 / CBR Wyckoff v6** (thuận đà) — nhưng KB1 lọc rất ngặt nên chỉ ra 33 lệnh/3 tháng | ✅ dương, ❌ quá ít lệnh |

Ba khoảng trống rút ra (**giả thuyết, CHƯA đo**):
1. **Không có nhánh khung TUẦN nào cả.** Mọi thứ đang là intraday. Đây là kịch bản pro trader xếp
   **đầu tiên** và cũng là kịch bản duy nhất họ nói "hold dài".
2. **KB-C thiếu bản scalp tần suất cao.** KB1 đang là bản "follow đà" siêu chọn lọc; pro trader mô tả
   một bản follow đà **ăn ít, đánh nhiều**.
3. **KB-B nên neo VWAP, không nên neo HVN/POC** — đã có số chứng minh (§3).

---

## 5. Điều KHÔNG được suy diễn từ đoạn chat này

- **Không có con số nào**: không WR, không RR, không SL, không tiêu chí vào lệnh cụ thể. Đoạn chat này
  là **kiến trúc**, không phải luật code được. Đừng biến "hold dài" thành một RR cụ thể rồi tưởng là
  lời pro trader.
- "vài chục lệnh/ngày" là **mô tả tần suất của họ**, không phải mục tiêu đã kiểm chứng cho hệ này.
  Tăng số lệnh mà không giữ EV thì chính là cái bẫy KB2 × vùng vừa mắc.
- Chưa rõ **VWAP tuần** của họ neo mốc nào (mở tuần? rolling 5 ngày?) và **TPO tuần** gộp mấy phiên.
  Cần hỏi lại trước khi code.

---

## 6. Câu nên hỏi lại pro trader

1. VWAP tuần tính từ **mốc nào** — mở tuần (Chủ nhật 22:00 UTC?) hay rolling 5 ngày?
2. TPO tuần: dùng **POC/VAH/VAL của cả tuần**, hay chỉ dùng POC?
3. KB-A "hold dài" là bao lâu — trong ngày, qua đêm, hay vài ngày?
4. KB-C "follow theo orderflow": tín hiệu vào là gì — imbalance xếp tầng, delta bùng, hay khối lượng đột biến?
5. Ba kịch bản đó **đóng góp tỉ lệ lợi nhuận** thế nào — cái nào ra tiền chính?
