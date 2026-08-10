# Chấm bài #20 — Tích luỹ (ACC) · 2026-05-20 01:36 → 12:48 (489 nến M1)

**Điểm: 6/10** — Vẽ đúng khung, sửa vài nhãn: Phase C đặt sai phía, UT[B] lạc phase, thiếu Phase E.

## Lỗi (nặng → nhẹ)

### 1. Phase C nằm ở biên TRÊN của một cấu trúc tích luỹ — luật vi phạm: L8
- **Thuật toán gắn:** Phase C = 09:59 → 10:16, nhãn duy nhất là **LPS[C] tại 4520.7**.
- **Đúng phải là:** L8 định nghĩa Phase C là tín hiệu đầu tiên cho thấy giá **ở biên này** bắt đầu phá **biên kia**. Trong tích luỹ, đó phải là cú test cuối ở **biên dưới** (Spring/Shakeout hoặc LPS[C] gần đáy) trước khi bung lên.
- **Dấu hiệu quyết định trên chart:** biên chính = 4491.0 – 4523.2. LPS[C] 4520.7 nằm cách biên **trên** đúng 2.5 giá, tức ở **92% chiều cao range**. Đó không phải "điểm hỗ trợ cuối", đó là một nhịp lùi nông ngay dưới trần. Cú test đáy thật gần nhất là vùng 4495-4497 lúc ~08:20 (đọc trên ảnh), cách đó hơn 90 nến.
- **Nghi phạm trong thuật toán:** đây chính là **hệ quả của việc bỏ ràng buộc "đúng nửa range"** ở v7.1. Ràng buộc "chỉ gần biên" là chưa đủ — phải là "gần biên **đối diện** với hướng phá sắp tới", tức LPS[C] của ACC phải ở nửa dưới.

### 2. UT[B] gán phase B nhưng thời điểm nằm trong Phase C — luật vi phạm: mâu thuẫn nội tại, L8
- **Thuật toán gắn:** UT[B] 10:08, giá 4528.0, cột Phase ghi **B**. Nhưng Phase B đã kết thúc 09:58 và Phase C chạy 09:59–10:16.
- **Đúng phải là:** một nhãn không thể mang tag [B] khi nó rơi vào khoảng thời gian Phase C. Cú này vượt biên chính 4523.2 lên 4528.0 rồi quay lại — theo L3 nó là cú **tạo biên phụ trên**, và theo L8 nó chính là **shock của Phase C** (case dễ). Phải gọi UT[C], hoặc nhập thẳng vào chuỗi Phase C thay cho LPS[C].
- **Dấu hiệu quyết định trên chart:** giá UT[B] 4528.0 **trùng khít** biên phụ trên 4528.0 ghi trong phiếu → chính nó tạo ra biên phụ đó. Trên ảnh, vạch tím Phase C đứng bên trái nhãn UT[B].
- **Nghi phạm trong thuật toán:** nhãn được gán phase tại thời điểm phát hiện rồi **không gán lại** khi biên phase C bị dời ngược (L8 case khó: "có Phase D rồi mới xác định được Phase C"). Cần một bước re-tag phase cho toàn bộ nhãn sau khi chốt biên phase.

### 3. Thiếu Phase E — luật vi phạm: L10
- **Thuật toán gắn:** Phase D = 10:17 → 12:48 = **122 nến**, không có Phase E.
- **Đúng phải là:** L10 — D là phá biên + retest giữ được ngoài biên; E là giá **rời range đi tìm vùng giá mới**. Ở đây LPS[D] xong lúc 10:21, còn lại 117 nến giá chạy tự do 4527 → 4544, đó là Phase E.
- **Dấu hiệu quyết định trên chart:** từ ~10:30 trở đi toàn bộ nến nằm **trên** cả biên phụ 4528.0, không còn quay lại range lần nào; volume nửa cuối ảnh nở rõ so với Phase B.
- **Nghi phạm trong thuật toán:** điều kiện kết thúc Phase D thiếu — đang để D chạy tới hết range.

### 4. SOS chưa đóng cửa qua biên phụ — luật vi phạm: L3
- **Thuật toán gắn:** SOS 10:17 tại 4526.8, VSA 1.94x.
- **Đúng phải là:** L3 — SOS thực sự mạnh phải đóng bứt qua **biên phụ** (4528.0), không chỉ qua biên chính (4523.2). SOS ở 4526.8 còn thấp hơn biên phụ 1.2 giá.
- **Dấu hiệu quyết định trên chart:** cây bứt thật qua 4528 nằm vài nến sau đó (khoảng 10:22-10:30 trên ảnh).
- **Nghi phạm trong thuật toán:** đúng theo mô tả sửa v7.1, SOS/SOW nay so với biên **CHÍNH** cố định. Nhưng L3 đòi so với biên **PHỤ** để phong "SOS mạnh". Cần tách 2 mức: `SOS` (qua biên chính) vs `MSOS` (qua biên phụ).

## Đạt
- **L1 đạt rõ:** MOVE giảm 34.6 giá / 39 nến, hiệu suất 0.41; climax SC VSA **6.97x**, biên độ nến **14.1 giá** — cao trào thật, chặn đúng đáy move. Mũi xám trên ảnh vẽ đúng chân move.
- **L2 đạt:** AR 01:50 (4523.2, VSA 5.57x) là cú bật ngược thật; ST[A] 02:37 hồi (4523.2−4501.2)/32.2 = **68%** khoảng AR↔climax, vượt ngưỡng 55% mới. ST[A] không còn lửng giữa range — chỗ này vá v7.1 **ăn tiền**.
- **L9 đạt:** Phase B 313 nến, dài nhất tuyệt đối. Phase C 12 nến, ngắn nhất. Tỷ lệ độ dài phase lành mạnh.
- **L4 đạt:** SC + phá lên thật = ACC, tên đúng.
- **L3 (biên chính) đạt:** 4491.0 / 4523.2 đúng climax + AR, cố định suốt range, không bị kéo theo giá.
- Đọc effort↔result hợp lý: mSOW 04:20 VSA 6.15x với thân/biên = 0.00 (nến doji volume khủng) — đúng dấu hiệu hấp thụ ở đáy Phase B, thuật toán bắt được.
