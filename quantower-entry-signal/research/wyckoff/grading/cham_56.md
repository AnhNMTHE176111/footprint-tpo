# Chấm bài #56 — Chưa rõ (BCLX) (DIST?) · 2026-07-24 14:00 → 20:59 (419 nến M1)

**Điểm: 3/10** — Phase A vẽ đúng, nhưng bỏ sót hoàn toàn cú phá xuống thật: một cấu trúc Phân phối rành rành bị đóng ở trạng thái "chưa rõ", thiếu cả Phase C, D lẫn E.

## Lỗi (nặng → nhẹ)

### 1. Bỏ sót SOW — hơn 120 nến đóng cửa dưới biên chính vẫn chỉ được gọi mSOW — luật vi phạm: L10 + L3
- **Thuật toán gắn:** mSOW 19:16 (4051.8) và mSOW 19:23 (4052.5, provisional); range đóng "Chưa rõ (BCLX)", Phase B kéo 393/419 nến tới hết.
- **Đúng phải là:** SOW tại nhịp phá 18:45–19:16 (đóng cửa dưới biên chính dưới 4058.4), LPSY[D] ở nhịp hồi 19:29–19:35 (bật lên ~4061 rồi thất bại, không lấy lại được vùng giá), rồi Phase E khi giá trôi tiếp và ở lì vùng 4053–4058 tới hết range. Tên range phải là **Phân phối**.
- **Dấu hiệu quyết định trên chart:** từ 18:45 tới 20:59 giá gần như không có nến nào đóng cửa lại trên 4058.4; đáy 4051.3 nằm dưới biên chính **7.1 giá = 49% chiều cao range**. Chỉ số phiếu cũng nói cùng một chuyện: SOT phía dưới `n=2`, tỷ lệ volume nhịp cuối/đầu **1.10 = hấp thụ** — cung vẫn giữ nguyên nỗ lực mà kết quả co lại.
- **Nghi phạm trong thuật toán:** điều kiện "phá THẬT" vẫn neo vào **biên phụ** (3 nến đóng vượt biên phụ + 30 tick) — biên phụ dưới 4051.3 chính là do cú thăm dò 19:16 nới ra. Bản vá 13.1c chỉ đổi decisive/outside/timed-out sang biên CHÍNH trong `B_brk`, **chưa** đổi ngưỡng chốt SOS/SOW. Gốc rễ "nới trước, so sau" còn nguyên. Cộng thêm luật "cú sau phải vượt qua chính cực trị đã thất bại" khiến 90 nến sau đó vĩnh viễn không đủ tư cách.

### 2. Thiếu Phase C — luật vi phạm: L8
- **Thuật toán gắn:** chỉ có A (27) và B (393).
- **Đúng phải là:** vì có Phase D (mục 1) nên phải gán ngược Phase C — nhịp test cuối cùng lên biên trên trước khi sụp là cụm 17:17–17:25 (đỉnh ~4073, đúng biên chính trên) → **LPSY[C]** ở đó.
- **Dấu hiệu quyết định trên chart:** đỉnh 17:17 chạm đúng nét liền 4073.0 rồi quay đầu, sau đó không đỉnh nào chạm lại được — kinh điển "test cuối trước khi cấu trúc sụp".
- **Nghi phạm trong thuật toán:** Phase C gán ngược chỉ chạy khi SOS/SOW bắn ra; SOW không bắn (lỗi 1) nên C mất theo. Đây là lỗi dây chuyền, không phải lỗi riêng của nhánh Phase C.

### 3. Nhãn mSOS neo vào cây yếu, bỏ qua cây phá thật — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** mSOS 15:40 tại 4082.5, **VSA 0.63×**.
- **Đúng phải là:** cú phá lên biên trên nằm ở 15:05–15:07 — thanh volume **cao nhất toàn chart** (nhìn panel dưới, cột vàng cao vọt), nến bung từ 4066 lên 4085.2. Nhãn phải hồi tố về đó.
- **Dấu hiệu quyết định trên chart:** cây 15:05 tạo đúng mức biên phụ trên 4085.2 mà máy đang dùng; nến 15:40 chỉ là một nhịp trôi xuống sau đó.
- **Nghi phạm trong thuật toán:** đúng "mSOS/mSOW hạ cấp không đi qua bước quét lại nến VSA cao nhất" đã ghi ở 13.1b — chưa sửa.

### 4. MOVE mở range mỏng — luật vi phạm: L1 (mức nhẹ)
- Hiệu suất hướng **0.42**, chỉ hơn sàn 0.35 một chút; move 24.6 giá / 42 nến. Nhìn chart, đoạn 12:53–14:00 giá lên nhưng lắc rất nhiều. Không đủ để bác range, nhưng là ca sát ranh — ghi nhận.

## Đạt
- **Phase A chuẩn nhất trong cả lô.** ST[A] 14:26 tại 4072.3, cách climax 4073.0 đúng **0.7 giá** = retrace **95%** khoảng AR↔climax. Đây chính là hiệu quả của việc nâng `STA_MIN_AR_FRAC` lên 0.55 — đủ 3 lần đổi hướng, Phase A kết thúc đúng tại ST[A] (L2 đạt).
- Biên chính = climax 4073.0 + AR 4058.4, cố định suốt range, không bị kéo theo giá (L3 đạt).
- Phase B là phase dài nhất (L9 đạt).
- Biên phụ mỗi bên đúng 1 cái, đúng cực trị xa nhất (4085.2 / 4051.3).
