# SPEC hệ CORVEN — bản chốt để code (2026-07-31)

> Nguồn: [TRANSCRIPT.md](TRANSCRIPT.md) (vi mô) + [TRUONG_LINH_3_KICH_BAN.md](TRUONG_LINH_3_KICH_BAN.md)
> (khung) + **câu trả lời của người học 2026-07-31** ([CAU_HOI_CAN_THONG_NHAT.md](CAU_HOI_CAN_THONG_NHAT.md)).
> Đây là file **duy nhất** cần đọc khi bắt tay code. Hai file kia là nguyên văn để đối chiếu.
>
> ⚠️ Mọi con số dưới đây là **thiết kế**, chưa có số backtest nào. Không được nhắc lại chúng như thành tích.
>
> 🆕 **Bổ sung 2026-08-10 (batch Messenger Aug 7–8, [TRANSCRIPT.md §13](TRANSCRIPT.md)):** SPEC này còn
> **thiếu tầng BỐI CẢNH**. Cụ thể phải thêm vào trước khi code tiếp:
> 1. **Chế độ thị trường quyết định BẬT engine nào** — *trong balance* thì chỉ "xác định range rồi vả 2 cạnh"
>    (KB-B); *sau balance* mới có move để follow (KB-C). Hiện SPEC cho cả 3 KB chạy song song mọi lúc.
> 2. **Phân kỳ delta là tín hiệu CÓ ĐIỀU KIỆN** (R11+R12): "tăng mà delta âm" ở **đầu sóng sau balance**
>    = chờ squeeze (thuận); ở **cuối sóng / nhịp hồi** = suy yếu (ngược). Một ngưỡng delta duy nhất là sai.
> 3. **Vùng khung lớn của CORVEN = TPO gộp 3 TUẦN, period 30 phút** (không phải profile 1 tuần) —
>    §2 dưới ghi "HVN tuần" là chưa đủ chính xác; phải đo lại HVN trên cửa sổ 3 tuần.
> 4. Kiểm chất lượng đấu giá bằng **tail / single print** — chưa có trong SPEC.

---

## 1. Bất biến của cả hệ (áp cho cả 3 kịch bản)

| Hạng mục | Chốt | Nguồn |
|---|---|---|
| **Khung vào lệnh** | **M1 cho cả 3 kịch bản.** Không có nhánh nào vào lệnh ở khung lớn | "Cả 3 kịch bản đều trade ở M1" |
| **Xác nhận** | **Bắt buộc chờ nến xác nhận trên M1** rồi mới vào — không vào khi giá vừa chạm | A5 + R8 |
| **RR** | **Cố định 1:3** cho mọi kịch bản | Q9 |
| **WR mục tiêu** | **40–50%** (hoà vốn tại RR3 = 25% → EV thiết kế +0.6 … +1.0R) | Q9 |
| **TP** | **Theo R cố định**, không "hết lực thì ra" | Q10 |
| **Thời gian giữ** | **Chỉ trong ngày.** Không qua đêm, kể cả nhánh vùng tuần | A3 |
| **SL** | Neo **dưới/trên cây M1 vào lệnh**, ~2–4 giá. Giống nhau ở cả 3 kịch bản | A4 + R7 |
| **Bỏ** | Con số WR 80% của CORVEN — không dùng làm mốc nữa | Q9 |

**Điểm cấu trúc quan trọng:** KB-A **không** phải nhánh swing. Nó là **cùng một cú scalp M1**, chỉ khác
là **vùng neo thuộc khung tuần** nên tỉ lệ thắng cao hơn. Trước đây tôi hiểu sai thành "hold nhiều
ngày, SL rộng" — sai hoàn toàn.

---

## 2. Vùng — CHỈ HVN và VWAP, không gì khác

| Loại vùng | Dùng? | Ghi chú |
|---|---|---|
| **HVN tuần** | ✅ vùng chính của KB-A | TPO tuần **chỉ lấy HVN** |
| **HVN ngày** | ✅ vùng của KB-B | |
| **VWAP tuần** | ✅ | **Neo từ ĐẦU TUẦN, reset 1 lần/tuần** |
| **VWAP ngày** | ✅ vùng scalp | |
| POC / VAH / VAL (tuần hoặc ngày) | ❌ | "Chỉ quan tâm HVN thôi" (A2) |
| VAH/VAL/POC **từng phiên Á-Âu-Mỹ** | ❌ **"Tất nhiên là không rồi"** (Q14) | |
| naked POC, cụm POC, băng giá trị, prior H/L | ❌ | Không hề được nhắc |
| LVN | ❓ chưa hỏi | |

**Hệ quả cho indicator M30SessionZones:** nó đang vẽ 7 loại vùng, trong đó **5 loại CORVEN không dùng**.
Phải cắt còn **HVN tuần + HVN ngày + VWAP**. Thang điểm "VÙNG CANH" hiện tại xếp naked POC 72 / cụm POC
78 / băng giá trị 55 — toàn thứ không nằm trong hệ.

---

## 3. Hai cách đánh tại MỘT vùng (đây là chỗ tôi hiểu sai trước đó)

Người học đã nói ngay câu đầu đoạn chat với CORVEN: *"Chạm vùng phản ứng đánh — Phá vùng rồi hồi đánh"*.
Đó là **hai play**, không phải hai kịch bản:

**Play 1 — CHẠM → ĐẢO CHIỀU tại HVN.**
> Q12: "Đánh theo giá chạm phá rồi hồi **hoặc giá đảo chiều ở HVN**."

Giá tới HVN, có nến xác nhận M1 ngược lại → vào ngược. RR 1:3.

**Play 2 — PHÁ VÙNG → HỒI VỀ → ĐÁNH TIẾP (break-retest).**
> Q11: "đánh break tức là **giá break ra khỏi vùng giá, chờ hồi về + có tín hiệu** rồi đánh."

Giá phá HVN đi ra, hồi lại về mép vùng, có tín hiệu → vào **thuận** hướng phá. RR 1:3.

⚠️ **Sửa lỗi của tôi:** trước đó tôi suy luận W5 "đánh break thôi chú" nghĩa là break **biên range M1**,
và viết vào RULES.md rằng nó "cấm fade tại VWAP". **Cả hai đều sai.** "Vùng" ở đây là **vùng HVN**, và
CORVEN dùng **cả** play đảo chiều **lẫn** play break-retest tại cùng vùng đó. Không có luật nào cấm fade.

---

## 4. Ba kịch bản sau khi chốt

### KB-A — vùng khung TUẦN (WR cao nhất)
- Vùng: **HVN tuần**, **VWAP tuần** (neo đầu tuần).
- Cả 2 play (chạm-đảo, phá-hồi). Vào ở M1 có nến xác nhận.
- RR **1:3** (xem §6 về mâu thuẫn 1:4). Đóng trong ngày.
- Tần suất: **~10 lệnh/tuần** → ~120 lệnh/3 tháng (đủ n để có ý nghĩa thống kê).
- Kỳ vọng: **WR cao hơn hai nhánh scalp** ("lệnh canh tuần sẽ winrate cao hơn 2 cách scap kia").

### KB-B — vùng khung NGÀY (scalp)
- Vùng: **HVN ngày**, **VWAP ngày**. Cùng 2 play, cùng RR 1:3, cùng xác nhận M1.
- Khác KB-A **chỉ ở khung của vùng**. WR thấp hơn KB-A.

### KB-C — follow order flow trong MOVE (không cần vùng)
- **Không dùng VSA / không cần volume climax** — Q7 nói rõ.
- Điều kiện tiền đề: đang trong **một move có xu hướng**. Nhận biết (Q8): **chuỗi nến cùng chiều +
  delta liên tiếp cùng dấu**. **Không** đòi delta phải tăng dần.
- Tín hiệu vào = **một nến có dấu hiệu ĐẨY CHỦ ĐỘNG**. Ví dụ nguyên văn cho move tăng:
  - **bubble big trade nằm ở 30% DƯỚI của nến**, và
  - **delta của nến xanh**, và
  - **thân nến vừa đủ dài, đóng đẹp**.
  → vào LONG thuận move. (SHORT: đối xứng — big trade ở 30% TRÊN, delta đỏ.)
- Các dấu hiệu đẩy chủ động khác được phép dùng: **imbalance**, big trade. Tra sách để liệt kê đủ.
- **"KO CẢN TÀU"** — tuyệt đối không vào ngược move.
- RR 1:3, TP theo R.

**Feature cần cho KB-C** (đã có data): `perlevel_m1_clean.pkl` có bid/ask từng mức giá →
tính được vị trí bubble big trade trong nến (%range), delta nến, imbalance. Đây là nhánh **duy nhất**
cần dữ liệu per-level; KB-A/KB-B chỉ cần OHLCV + profile.

---

## 5. Ánh xạ luật RULES.md → kịch bản (bản sửa)

| Kịch bản | Luật thuộc về |
|---|---|
| **KB-A + KB-B** (giống nhau, khác khung vùng) | **R2** (hấp thụ chỉ có giá trị ở cực trị) · **R10** (vol thấp ≠ tín hiệu đảo) · **R8/A5** (chờ xác nhận M1) · **R7** (SL dưới cây M1, 2–4 giá) |
| **KB-C** | **R1** (leg do lệnh CHỦ ĐỘNG, không phải limit kê) · **R3** (loại leg do quét stop) · **R9** (chất lượng nến trong leg) · **R7** |
| **Xuyên suốt** | **R5** (bias theo phiên) · **C1** (score ~70%, không AND-gate cứng) · **W4** (không cần gán nhãn Wyckoff) |
| **Bỏ / sửa** | **W5** — không phải "chỉ đánh break"; là break-retest **một trong hai play** tại vùng. **R6** (RR theo giờ) và **C2** (WR 65-70%, RR 5-6) — thay bằng **RR 1:3 cố định, WR mục tiêu 40-50%** |

---

## 6. Điểm duy nhất còn vênh — và cách tôi xử lý

**RR của KB-A: 1:4 hay 1:3?**
- A3: *"những lệnh này chắc ăn dài nên sẽ ưu tiên 1:5, nhưng thôi ta cứ 1:4"* → 1:4 cho KB-A.
- Q9 (nói sau, phạm vi rộng hơn): *"lệnh của **mỗi kịch bản** mình vẫn sẽ **cố định 1:3**"* → 1:3 cho tất cả.

**Xử lý:** lấy **1:3 làm mặc định** (câu Q9 bao trùm cả hệ và nói sau), nhưng **quét cả 1:3 / 1:4 / 1:5
cho riêng KB-A** — đây chỉ là một tham số, quét thêm gần như không tốn gì, và nếu bề mặt RR của KB-A
là một **cao nguyên** chứ không phải mũi nhọn thì chính nó trả lời câu này bằng số. Không cần hỏi lại.

---

## 7. Chưa hỏi (không chặn — sẽ hỏi khi cần)

- LVN có dùng không?
- Điều kiện **đứng ngoài không đánh cả ngày**.
- Đáo hạn hợp đồng: đổi mã thế nào (GCQ26 vừa qua First Notice Day 31/07).
- "HVN tuần" định nghĩa vận hành: dựng profile tuần từ M1 hay từ M30? Ngưỡng đỉnh khối lượng bao nhiêu?
  → Tôi sẽ dùng `FindHvn` đã có trong M30SessionZones, mở rộng cửa sổ sang cả tuần, rồi kiểm bằng mắt
  trên chart trước khi tin.
