# Chấm bài #21 — Tích lũy (ACC) · 2026-05-26 08:34 → 11:21 (165 nến M1)

**Điểm: 4/10** — Range đặt đúng chỗ và tên ACC đúng, nhưng **phần giữa đọc sai hẳn**: Spring gán vào cú thất bại, biên phụ dưới bỏ mất cực trị thật, và độ dài Phase B/C đảo ngược so với luật.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới bỏ mất cực trị xa nhất — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới = **4551.5** (điểm Spring 09:16).
- **Đúng phải là:** sau 09:16 giá còn rơi tiếp và tạo đáy khoảng **4543.5** (quanh 09:45). Theo L3 "có điểm xa hơn thì biên phụ cũ biến mất, biên phụ mới nới ra" → biên phụ dưới phải là **~4543.5**, tức range thật rộng ~23 giá chứ không phải 14.6 giá.
- **Dấu hiệu quyết định trên chart:** cụm nến đỏ dài quanh 09:40–09:50 nằm **hẳn bên dưới** đường nét đứt "biên phụ dưới 4551.5" — mắt thường thấy ngay là đường biên phụ bị cắt xuyên qua, cách đáy ~8 giá. Trên panel volume, cú rơi đó kèm thanh vàng (VSA ≥ 2.2x).
- **Nghi phạm trong thuật toán:** biên phụ chỉ được nới bởi các **nhãn đã phát hiện** (mSOW/Spring/UT) chứ không quét cực trị thô của mọi nến trong range. Phải nới biên phụ bằng `min(low)` / `max(high)` toàn range.

### 2. "Spring confirmed" gán vào một cú THẤT BẠI — luật vi phạm: L5 + THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** Spring 09:16 tại 4551.5, trạng thái **confirmed**; rồi LPS[C] 09:31 tại 4552.9.
- **Đúng phải là:** một Spring chỉ được "confirmed" nếu giá **không quay lại phá đáy đó nữa**. Ở đây giá bật lên tới ~4560 rồi **rơi sâu hơn Spring 8 giá** (4543.5) — theo THEORY §3.5 và L5, cấu trúc thật là: 09:16 là một **Shakeout thất bại**, và **cú rơi 09:45 mới là Spring/Terminal Shakeout thật** (phá sâu, volume nổ, rồi bật thẳng lên SOS). Kèm theo đó, LPS[C] 09:31 (4552.9) **không phải LPS** — nó là nhịp hồi bị phủ định ngay sau; đúng vai nó là một No-Demand/nhịp hồi trong Shakeout.
- **Dấu hiệu quyết định trên chart:** 4543.5 < 4551.5 và < 4552.9 — LPS bị xuyên qua thì hết là "điểm hỗ trợ cuối cùng".
- **Nghi phạm trong thuật toán:** trạng thái `confirmed` của Spring được chốt ngay khi giá thu vào trong range (3-4 nến) mà **không invalidate hồi tố** khi xuất hiện đáy thấp hơn trong cùng Phase C. Cần: `if new_low < spring_low → spring cũ chuyển thành Shakeout thất bại, dời nhãn Spring xuống đáy mới`.

### 3. Phase B (15n) NGẮN NHẤT, Phase C (56n) DÀI NHẤT — đảo ngược cả hai luật: L9 và L8
- **Thuật toán gắn:** A 26n · **B 15n** · **C 56n** · D 16n · E 53n.
- **Đúng phải là:** B phải dài nhất, C phải ngắn nhất. Ở đây B chỉ 15 nến rồi nhảy sang C ngay từ 09:16, khiến toàn bộ đoạn đấu giá 09:16–10:11 (56 nến, hơn 1/3 range) bị dồn vào Phase C. Đọc lại: đoạn 09:00–09:50 mới là Phase B (test cả 2 biên, cung/cầu đỡ nhau), Phase C = cú Shakeout ~09:45–09:55 (~10 nến), Phase D bắt đầu từ nhịp bò lên trước SOS.
- **Dấu hiệu quyết định trên chart:** vạch tím "Phase C (56n)" phủ trọn cả cú rơi 8 giá xuống 4543.5 và cả nhịp bò lên 20 giá — một Phase C không thể chứa hai chuyển động ngược chiều lớn như vậy.
- **Nghi phạm trong thuật toán:** Phase C được mở ngay tại nến shock đầu tiên (Spring) và đóng tại SOS, nên mọi thứ giữa hai mốc đó bị hút vào C. Sửa cùng với lỗi 2: dời mốc mở Phase C về shock **cuối cùng** trước SOS.

### 4. Cây climax bị tách quá xa mức climax, và move trước climax quá mỏng — luật vi phạm: L1 (biên)
- **Thuật toán gắn:** mức climax **4553.4** (nến 08:34, VSA **0.67x**, biên độ 2.3 giá); nhãn SC lại đặt ở **08:29** (4554.1, VSA 2.96x) — cách nhau 5 nến. Move trước climax chỉ **16.6 giá / 37 nến** (0.36%).
- **Đúng phải là:** cơ chế tách nhãn/mức của v6 là hợp lệ, nhưng ở đây nến mang mức climax có VSA **0.67x** — dưới trung bình. Cây cao trào thật là 08:29–08:30 (2.96x rồi 2.13x) và đáy của cụm đó là **4553.6**, gần như trùng 4553.4 → nên lấy 4553.6 cho cả nhãn và mức, khỏi tách. Ngoài ra move 16.6 giá / 0.36% là mức mỏng, sát ranh "đi ngang xuất hiện nến volume cao" mà L1 cấm mở range.
- **Dấu hiệu quyết định trên chart:** trên ảnh, nhãn `SC` nằm bên **ngoài** khung vạch tím Phase A; move giảm phía trước chỉ là một nhịp điều chỉnh trong dao động 4555–4573.
- **Nghi phạm trong thuật toán:** cửa sổ tách nhãn/mức climax cho phép lệch tới ≥5 nến mà không kiểm "nến mang mức climax có VSA tối thiểu".

### 5. Chỉ số nỗ lực/kết quả diễn giải NGƯỢC (lỗi ĐO) — THEORY §2.2
- **Thuật toán in:** effort 2.81x, result **5.78**, er = **0.49** → "vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** er = 0.49 < 1 nghĩa là **kết quả gấp đôi nỗ lực** — giá đi xa với volume tương đối vừa. Đây là nhịp **thuận lực/rỗng cản**, không phải hấp thụ. Câu kết luận bị hardcode (xem bài #19/#20/#23/#24 in y hệt bất kể er).
- **Nghi phạm trong thuật toán:** câu diễn giải nằm ngoài nhánh so ngưỡng er.

### 6. Bias test biên = +0 nhưng Phase B (15 nến) không chạm biên nào (lỗi ĐO)
- Phase B 09:00–09:15: nhìn ảnh giá chỉ dao động ~4555–4557, **không chạm biên trên 4560.7 lẫn biên dưới 4553.4**. Bias phải là "không đủ dữ liệu", không phải "+0 = test CẢ HAI biên". Nghi phạm: bias tính trên toàn range chứ không riêng Phase B, hoặc dung sai chạm biên quá rộng.

### 7. SOT phía trên: n=1 kèm tỷ lệ 0.00 (trình bày)
- THEORY §7 yêu cầu **≥3 nhịp** mới nói được SOT. In "chớm n=1, thrust cuối/đầu=0.00, volume 0.00" là gây hiểu sai; nên in `chưa đủ nhịp (n<3)`.

## Đạt
- **L4 — tên range:** origin SC (move giảm bị chặn) + phá **lên** thật (SOS 4563.6 → giá lên 4571) → **Tích lũy (ACC)**, đúng bảng 4 mẫu hình.
- **L2 (một phần):** đủ 3 lần đổi hướng — climax → AR 4560.7 (bật 7.3 giá) → ST[A] 4555.7 quay lại **sát vùng climax** (cách mức climax 2.3 giá, tức 32% biên chính). ST[A] ở đây làm đúng việc của nó, khác hẳn bài #19/#24.
- **L3 (một phần):** biên chính = climax 4553.4 + AR 4560.7, cố định, không kéo theo giá; biên phụ trên 4566.1 là cực trị xa nhất phía trên và chỉ có 1.
- **L10:** SOS 10:12 (4563.6, VSA 2.00x) đóng cửa **trên biên phụ trên 4566.1** ở các nến kế, LPS[D] 10:19 hồi về 4560.7 (đúng biên chính trên) rồi giữ được → Phase E đi tiếp lên 4571. Đây là CBR đọc đúng.
- **L7:** LPS[C] và LPS[D] đều 1 điểm.
- **SOT phía dưới** đo đúng bản chất: thrust cuối/đầu 0.73 + volume 0.51 → gọi "cạn kiệt" là khớp THEORY §7 (rút ngắn + volume yếu = cạn kiệt thật).
