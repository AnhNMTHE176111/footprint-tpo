# Chấm bài #15 — Tích luỹ (ACC) · 2026-05-07 16:19 → 2026-05-08 14:06 (630 nến M1)

**Điểm: 3/10** — Khung range đọc được, nhưng cả hai biên phụ lẫn hai nhãn m-SOS/m-SOW đều neo vào nến rác, và LPS[D] đặt cao hơn cả SOS. Sửa nhãn nặng.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới 4708.0 do một cây rác 1 tick tạo ra — luật vi phạm: L3 + mục 8 (Effort vs Result)
- **Thuật toán gắn:** `mSOW 05-07 22:00 @4708.0, VSA 0.13x, thân/biên độ 0.00` → biên phụ dưới = 4708.0, đẩy tỷ lệ biên phụ/biên chính lên **3.85×** (sát guard 4.0×).
- **Đúng phải là:** trên ảnh, quanh 22:00 giá đang giao dịch vùng 4740–4750; **không có nến nào** vẽ được gần 4708. Đáy thật của Phase B là cụm 4732–4735 lúc 05-07 20:30. Biên phụ dưới đúng phải là ~4732.
- **Dấu hiệu quyết định trên chart:** chấm mSOW nằm lơ lửng trên đường nét đứt, cách xa mọi thân nến; VSA 0.13× (1 lot) + thân 0.00 = một print lạc.
- **Nghi phạm trong thuật toán:** biên phụ nới theo `low` thô, không lọc outlier (không đòi cây tạo cực trị phải có VSA/biên độ tối thiểu, không đòi nến kế tiếp xác nhận). Vá v7 #5 không cứu vì nhãn vẫn neo theo **cực trị giá** chứ không quét lại cây mạnh nhất.

### 2. mSOS cũng neo vào doji VSA 0.65× — luật vi phạm: vá v7 #5, mục 8
- **Thuật toán gắn:** `mSOS 05-08 06:29 @4778.8, VSA 0.65x, thân 0.00`.
- **Đúng phải là:** đợt thăm dò lên đó có cây nỗ lực thật (panel volume có thanh vàng quanh 05-08 06:02); nhãn phải hồi tố về cây đó.
- **Nghi phạm trong thuật toán:** giống bài #13 — nhánh mSOS/mSOW sinh từ nới biên phụ **không** đi qua bước quét lại VSA cao nhất. Lỗi này xuất hiện ở 4/6 bài trong lô (13, 15, 17, 18) → chưa vá được.

### 3. LPS[D] nằm CAO HƠN SOS — không phải nhịp retest — luật vi phạm: L10
- **Thuật toán gắn:** `SOS 13:30 @4780.7` → `LPS[D] 13:33 @4784.5`.
- **Đúng phải là:** LPS[D] là nhịp hồi **ngược hướng phá** rồi giữ được ngoài biên. Một điểm cao hơn cây phá 3.8 giá và chỉ sau 3 nến là phần **tiếp diễn** của cú phá, không phải retest.
- **Dấu hiệu quyết định trên chart:** nhãn LPS[D] vẽ nằm phía trên nhãn SOS.
- **Nghi phạm trong thuật toán:** `WyTryLpsAndPhaseE` lấy swing pivot 5 nến nhưng không kiểm dấu (`lps_price < sos_price` khi phá lên).

### 4. Nhãn SC rơi ra ngoài khung range — luật vi phạm: vá v7 #4
- **Thuật toán gắn:** range mở 16:19, nhãn `SC` đặt tại **16:18** (@4753.2, VSA 2.94×) trong khi biên chính dưới lấy từ nến 16:19 (@4750.0).
- **Nghi phạm trong thuật toán:** y hệt bài #13/#17 — không kẹp `climax_ev ≥ range_start`. Lỗi hệ thống.

### 5. Độ dài Phase C bằng đúng trần cửa sổ gán ngược — luật vi phạm: L8 (đo bằng tham số, không bằng giá)
- **Thuật toán gắn:** Phase C = **60 nến** (12:12 → 13:29), đúng bằng `min(60, 0.8×518)`.
- **Đúng phải là:** Phase C phải là phase **ngắn nhất**; ở đây C (60) dài hơn cả D (25) và E (9). Nhịp test thật chỉ là cụm nến quanh LPS[C] @4749.9 lúc 12:12–12:26, khoảng 15–20 nến.
- **Nghi phạm trong thuật toán:** Phase C gán ngược lấy **toàn bộ cửa sổ nhìn lại** làm độ dài phase thay vì chỉ lấy đoạn từ pivot test tới cú phá. Nới cửa sổ 0.5→0.8×len(B) (vá v7 #3) làm lỗi này **nặng thêm** ở các range có Phase B dài.

## Đạt
- Điều kiện mở range (L1): MOVE 53.5 giá / 70 nến / hiệu suất 0.48; cây climax là đáy của cửa sổ — đúng.
- Phase A đủ 3 lần đổi hướng, kết thúc tại ST[A] (19 nến), ST[A] @4757.2 hồi 74% khoảng AR↔climax — qua ngưỡng 0.4 mới, hợp lý.
- Biên chính 4750.0–4768.4 đọc đúng trên ảnh: giá test cả hai phía nhiều lần trong 518 nến Phase B (bias=0, đúng ca thường).
- LPS[C] @4749.9 đặt sát biên chính dưới 4750.0 — vị trí test rất đẹp, đúng vai LPS[C] (không phá biên nên **không** gọi Spring — tránh được đúng lỗi kinh điển Ca #19 nguồn 2.pdf).
- Tên range: SC + phá lên = Tích luỹ, khớp L4. SOS VSA 4.66× thân 1.00 — cây phá thật, nhãn neo đúng.
- Chú thích nỗ lực/kết quả lần này ghi "vùng hấp thụ NGHI VẤN" với er=1.14 (≥1) — **đúng dấu**, vá v7 #1 chạy tốt.
