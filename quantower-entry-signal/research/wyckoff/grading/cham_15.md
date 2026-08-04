# Chấm bài #15 — Tích luỹ (ACC) · 2026-05-07 16:19 → 2026-05-08 14:06 (630 nến M1)

**Điểm: 6/10** — Cấu trúc đọc được, Phase C gán ngược đúng chỗ, SOS neo đúng cây phá. Lỗi chính: **biên chính đặt quá hẹp so với vùng đấu giá thật** nên nửa bên dưới của range trở thành "biên phụ" tận 42 giá.

## Lỗi (nặng → nhẹ)

### 1. Climax không chặn được move — biên chính hẹp gấp 3.85 lần vùng giá thật — luật vi phạm: L1 / L3, mục 4.0 guard "climax không chặn được move"
- **Thuật toán gắn:** biên chính 4750.0–4768.4 = 18.4 giá; biên phụ 4708.0–4778.8 = 70.8 giá, **tỷ lệ 3.85x**, sát trần huỷ range 4.0x.
- **Đúng phải là:** cây climax 16:19 (VSA 1.90x, 14 lot, biên độ 2.6 giá) chỉ chặn được đà giảm 4 giờ; đến 05-07 20:30 giá phá xuống thêm **42 giá** dưới mức climax và ở ngoài range suốt ~200 nến (20:30 → 23:54). Cây climax thật của cấu trúc này là cái đáy 4708, không phải 4750. Nếu giữ cách vẽ hiện tại thì phải nói thẳng: mức 4750 không còn là biên, nó chỉ là một mức trong range.
- **Dấu hiệu quyết định trên chart:** cả cụm nến từ 05-07 20:30 tới 23:54 nằm dưới đường "biên CHÍNH dưới 4750.0", đáy cụm ăn xuống 4708 — nhìn trên ảnh là một chân giảm hoàn chỉnh, không phải một cú thọc.
- **Nghi phạm trong thuật toán:** guard "sau cửa sổ cụm, giá vượt mức climax quá 3× biên độ TB → bỏ range" chỉ áp trong **8 nến** đầu. Cần một guard chạy suốt Phase B: nếu biên phụ/biên chính vượt ngưỡng (đã có trần 4.0x nhưng quá lỏng — 3.85x vẫn được nhận) thì hoặc bỏ range, hoặc **dời climax xuống cực trị mới và vẽ lại Phase A**.

### 2. Đoạn 200 nến ngoài biên bị thu về đúng một nhãn mSOW trên nến rỗng — luật vi phạm: L5 (Shakeout = phá ra, lùng bùng ngoài, rồi mới quay lại) + THEORY §2.2
- **Thuật toán gắn:** mSOW tại 4708.0, 05-07 22:00, **VSA 0.13x, thân 0.00**.
- **Đúng phải là:** theo L5 đây đúng là **Shakeout** (một SOW thất bại) — phá ra, lùng bùng ngoài nhiều giờ, rồi quay vào. Nhãn hạ cấp thành mSOW là hợp lý về mặt luật (cú rũ cách SOS 14 giờ, quá trần 120 nến của Phase C), nhưng nhãn **neo vào nến rỗng VSA 0.13x** thì vô nghĩa: cả cụm giảm đó có nhiều cây volume cao mà không cây nào được đánh dấu.
- **Dấu hiệu quyết định trên chart:** panel volume quanh 05-07 20:30 có nhiều thanh vàng (VSA ≥2.2x) — nỗ lực bán thật ở đó; nhãn lại nằm ở 22:00 nơi volume gần bằng 0.
- **Nghi phạm trong thuật toán:** giống bài #13 lỗi 3 — mSOS/mSOW neo cực trị giá, chưa áp cơ chế hồi tố về cây VSA cao nhất.

### 3. Kết luận "Tích luỹ hoàn tất" đáng ngờ — cú phá chết ngay sau Phase E — đối chiếu Ca #22 nguồn 2.pdf
- **Thuật toán gắn:** Phase E 9 nến, range đóng `completed` với tên Tích luỹ.
- **Đúng phải là:** nhìn phần cuối ảnh, sau LPS[D] 4784.5 giá đổ về 4755, tức **lùi hẳn xuống dưới cả biên chính trên 4768.4**. Cú SOS này đi được 65% chiều cao rồi tắt. Giảng viên trong Ca #22 (2.pdf) cảnh báo đúng tình huống này: "cấu trúc chưa chạy hết, có thể phân phối".
- **Nghi phạm:** mốc "đi ≥50% chiều cao là đủ chốt Phase E" (mục 7) quá dễ đạt khi chiều cao range chỉ 18.4 giá; nên đo bằng biên PHỤ (70.8 giá) cho ngưỡng "đi đủ xa", vì chính biên phụ mới là vùng đấu giá thật.

### 4. Phase C (60 nến) dài hơn Phase D + E (34 nến) — luật vi phạm: L8 (mức nhẹ)
- Không sai bằng bài #16 (C vẫn ngắn hơn nhiều so với B = 518 nến), nhưng LPS[C] 12:12 cách SOS 13:30 tới 78 phút; nhìn chart nhịp test cuối thật sự trước SOS nằm quanh 13:10–13:25.

## Đạt
- Điều kiện mở range (L1): MOVE giảm 53.5 giá / 70 nến / hiệu suất 0.48 — move thật, climax là đáy chặn move. Đạt.
- Phase A (L2): 3 lần đổi hướng, SC 4753.2 → AR 4768.4 → ST[A] 4757.2, 19 nến, chốt đúng tại ST[A]. ST[A] ở nửa dưới range = "lực bán còn nhất định" (THEORY §5) — hợp lệ.
- Biên phụ (L3): đúng mỗi bên 1 cái, đúng cực trị xa nhất 4708.0 / 4778.8.
- Phase C gán ngược (L8 case khó): **LPS[C] 4749.9 rơi đúng biên chính dưới 4750.0** ở nhịp lùi cuối trước cú bứt — đây là kiểu điểm mà giảng viên gọi "Test là LPS[C] tiềm năng" (Ca #3, #13 nguồn 2.pdf). Gán tốt.
- SOS neo đúng cây phá: 4780.7, **VSA 4.66x, thân 1.00**, đóng cửa vượt biên phụ trên 4778.8. Lỗi B của v5 đã vá đúng ở bài này.
- Tên range (L4): SC + phá lên = Tích luỹ. Khớp.
- Chỉ số Phase B: SOT dưới trạng thái SOT, n=3, thrust cuối/đầu 0.22, volume 0.38 → "cạn kiệt" — **đo đúng bản chất**, khớp với hình đáy nâng dần sau cú thọc 4708.

## Cần hỏi người học
- Khi tỷ lệ biên phụ/biên chính lên tới ~3.8x, người học muốn xử thế nào: (a) bỏ range, (b) dời climax xuống cực trị mới và vẽ lại Phase A, hay (c) giữ nguyên và chỉ coi biên phụ là vùng làm việc thật? Hiện code chọn (c) và guard 4.0x gần như không bao giờ bắn.
