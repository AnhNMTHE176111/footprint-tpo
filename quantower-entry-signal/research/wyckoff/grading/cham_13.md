# Chấm bài #13 — Tích luỹ (ACC) · 2026-05-04 15:22 → 2026-05-05 15:41 (660 nến M1)

**Điểm: 3/10** — Range mở đúng chỗ, nhưng nửa sau bài hỏng: giá đã rời hẳn biên trên từ 05-05 05:13 mà máy vẫn ghi "Phase B" thêm gần 7 tiếng, và bài thiếu hẳn Phase C.

## Lỗi (nặng → nhẹ)

### 1. Giá ở ngoài biên chính trên ~350 nến mà vẫn tính là Phase B — luật vi phạm: L10 + mục 5.1 (Kết cục B)
- **Thuật toán gắn:** Phase B kéo từ 15:52 (04/05) tới 12:09 (05/05) = 488 nến; SOS mãi tới 05-05 12:10.
- **Đúng phải là:** trên ảnh, giá cắt lên biên CHÍNH trên 4588.3 quanh 05-05 04:30–05:13 và giao dịch liên tục **phía trên** nó tới tận 11:00 (chỉ chạm hụt xuống một lần). Đó là SOS thật; Phase D/E phải bắt đầu ở đó, không phải 7 tiếng sau.
- **Dấu hiệu quyết định trên chart:** toàn bộ cụm nến từ `05-05 05:13` tới `05-05 09:39` nằm trên đường liền 4588.3; biên phụ trên lại chỉ là 4603.8 — tức là nó **được nới dần bởi chính đợt tăng đang xét**, rồi lại trở thành mốc mà đợt tăng đó phải vượt.
- **Nghi phạm trong thuật toán:** điều kiện "Kết cục B" so với **biên phụ** (3 nến đóng vượt biên phụ ≥30 tick). Vá v7 mục 6 mới nâng ngưỡng outside/timed-out lên 30 tick chứ **chưa** đổi mốc so sánh; vòng lặp "biên phụ tự nới rồi tự vượt" **vẫn còn** ở đúng ca này. Nhánh dự phòng "ngoài >40 nến và ≥60% đóng ngoài" cũng không bắn.

### 2. Thiếu hoàn toàn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** dải phase A → B → D → E, không có C.
- **Đúng phải là:** Phase B dài 488 nến thì cửa sổ gán ngược = min(60, 0.8×488) = 60 nến, thừa chỗ. Nhịp test cuối trước cú bứt là đáy quanh `05-05 11:00` (giá lùi về ~4583, sát biên chính trên) — đó là LPS[C].
- **Dấu hiệu quyết định trên chart:** ngay trước SOS 12:10 có một nhịp lùi rõ về vùng 4583–4588 rồi bật lên.
- **Nghi phạm trong thuật toán:** ràng buộc v6 "pivot phải nằm **trong range** và đúng **nửa dưới** range" — nhịp test này nằm **ngoài** biên chính trên nên bị loại sạch. Nới cửa sổ lên 0.8×len(B) (vá v7 #3) không cứu được vì lỗi nằm ở ràng buộc vị trí, không ở độ dài cửa sổ.

### 3. Nhãn mSOS neo vào cây doji VSA 0.51× — luật vi phạm: mục 8 (Effort vs Result), vá v7 #5
- **Thuật toán gắn:** `mSOS 05-05 09:08 @ 4603.8, VSA 0.51x, thân/biên độ 0.00`.
- **Đúng phải là:** nến đại diện cho một cú thăm dò phải là cây có nỗ lực; trong đoạn đó có nhiều cây vàng (VSA ≥2.2×) trên panel khối lượng.
- **Dấu hiệu quyết định trên chart:** thân/biên độ = 0.00 → đó là một cây doji 1 tick, đúng bằng cực trị giá 4603.8.
- **Nghi phạm trong thuật toán:** vá v7 #5 ("quét lại lấy nến VSA cao nhất trong đoạn thăm dò") **không chạy** cho nhánh mSOS/mSOW sinh từ nới biên phụ — nhãn vẫn neo theo **cực trị giá**.

### 4. Nhãn SC rơi ra ngoài khung range — luật vi phạm: vá v7 #4 (kẹp nhãn theo nến mở range)
- **Thuật toán gắn:** range bắt đầu 15:22, nhưng nhãn `SC` đặt tại **15:21** (4560.8, VSA 2.70×).
- **Đúng phải là:** nhãn climax phải nằm trong khung range; hoặc mốc mở range dời về 15:21 cho khớp.
- **Dấu hiệu quyết định trên chart:** chấm SC nằm bên trái vạch tím "Phase A".
- **Nghi phạm trong thuật toán:** kẹp `climax_ev ≥ range_start` chưa áp; cây VSA cao nhất của cụm nằm **trước** cây cực trị giá nên nhãn lùi ra ngoài. (Lặp lại y hệt ở bài #15, #17 → lỗi hệ thống, không phải ca lẻ.)

### 5. LPS[D] chỉ cách SOS đúng 1 nến và lùi vào trong biên phụ — luật vi phạm: L10
- **Thuật toán gắn:** `SOS 12:10 @4607.1` → `LPS[D] 12:11 @4603.5`.
- **Đúng phải là:** LPS[D] là nhịp retest **giữ được ngoài** biên; 4603.5 < biên phụ 4603.8 tức đã tụt lại vào trong.
- **Nghi phạm trong thuật toán:** swing pivot 5 nến + sàn 1.5× ATR quá lỏng khi nến sau SOS biến động mạnh; nên thêm điều kiện "đáy retest phải ≥ biên phụ".

## Đạt
- Điều kiện mở range (L1): MOVE 52.1 giá / 32 nến / hiệu suất 0.70, cây climax là **đáy** của cửa sổ — đúng chuẩn "chặn move".
- Phase A đủ 3 lần đổi hướng, kết thúc đúng tại ST[A] (27 nến), ST[A] 4556.0 thủng xuống dưới climax 4559.8 nên sinh biên phụ dưới — đúng L3.
- Tên range: SC origin + phá lên = Tích luỹ, khớp L4.
- Phase B là phase dài nhất (488n) — đúng L9.
- Chú thích nỗ lực/kết quả đã đọc **đúng dấu** (er=0.50 → "nhịp HIỆU QUẢ", không còn hard-code "hấp thụ nghi vấn") — vá v7 #1 chạy tốt.
