# Khung 3 kịch bản của pro trader "Trương Linh" (Messenger, 2026-07-31)

> **Nguồn:** 3 ảnh chat Messenger người học gửi ngày 2026-07-31 (13:30 → 13:43).
> Pro trader thứ **hai** trong repo — khác CORVEN ([TRANSCRIPT.md](TRANSCRIPT.md) / [RULES.md](RULES.md)).
> CORVEN cho **chi tiết vi mô** (order flow từng mức giá, SL, RR). Trương Linh cho **KHUNG XƯƠNG**:
> hệ thống chia làm mấy kịch bản và mỗi kịch bản neo vào khung thời gian nào.
> Người học gọi là "chú", tự xưng "t". Ảnh gốc chưa lưu vào repo — nội dung đã trích đủ ở dưới.

---

## 1. Nguyên văn (đã sắp lại theo thứ tự chat)

**Người học hỏi:** "Hệ thống của chú có mấy kịch bản trade thế / Chạm vùng phản ứng đánh — Phá vùng rồi hồi đánh"

**Trương Linh:**
> "Có 2"
> "Một là **chạm vùng lớn có thể hold dài**"
> "2 là **scap**"
> "À **có 3 kiểu**."
> "Scap có 2 kiểu — 1 là **đánh vwap**"
> "2 là **đánh follow theo orderflow**"
> "**Ngày phải vài chục lệnh đấy**"

**Người học:** "Vùng phản ứng là vùng lớn hoặc vwap à chú" · "Đánh kiểu này là sẽ như nào chú, thuần bóng nổ à"

**Trương Linh:** "**Vwap tuần**" · "**Có chơi đc**" · "**Vwap ngày scap**" ·
> "**Tpo ngày thì hơi nhỏ nên t nhìn hẳn tuần cho bao quát**"

**Người học chốt lại (được xác nhận):**
> "Tức là chú chơi 3 kịch bản:
> • chạm **vùng lớn** phản ứng **hold dài**, vùng này là **vwap tuần hoặc tpo tuần**
> • đánh **scap**:
>   + chạm **vwap, tpo ngày** canh phản ứng
>   + **follow theo footprint, ko cản tàu**"

**Trương Linh:** "**Uh**" · "**Đúng r**" ✅

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
