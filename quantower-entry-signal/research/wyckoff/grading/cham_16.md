# Chấm bài #16 — Tích lũy (ACC) · 2026-05-20 01:36 → 17:04 (742 nến M1)

**Điểm: 4/10** — Range mở đúng chỗ, Phase A sạch, nhưng biên chính bị bỏ rơi giữa chừng: giá sống hẳn TRÊN biên trên suốt ~5 tiếng mà vẫn bị gọi là Phase B. Sửa được, không phải bỏ.

## Lỗi (nặng → nhẹ)

### 1. Giá rời hẳn range từ ~08:40 nhưng thuật toán vẫn giữ Phase B tới 14:23 — luật vi phạm: L9 + L10, THEORY §3.2 Phase D/E
- **Thuật toán gắn:** Phase B kéo 561 nến (01:59 → 14:23); SOS mãi tới 14:39 tại 4559.9.
- **Đúng phải là:** biên chính trên = 4523.2. Nhìn chart, từ khoảng 05-20 08:40 giá đã leo lên trên 4523.2 và **không quay lại** — cả đoạn 09:00–13:15 dao động trong vùng 4525–4542, tức nằm trọn ngoài biên chính. Đó không còn là "đấu giá trong range" mà là giá đã đi. SOS thật phải neo vào cú bứt đầu tiên giữ được trên 4523.2, và mọi thứ sau đó là Phase D/E, không phải Phase B.
- **Dấu hiệu quyết định trên chart:** biên CHÍNH trên 4523.2 nằm **dưới đáy** của toàn bộ vùng dao động 09:00–13:15. Chính mSOS 13:14 ở 4542.2 — cao hơn biên chính 19 giá, gần bằng 60% chiều cao range (32.2 giá) — cũng bị xếp là "thăm dò trong Phase B".
- **Nghi phạm trong thuật toán:** điều kiện Kết cục B ở mục 5.1 buộc phải có **3 nến liên tiếp đóng cửa vượt BIÊN PHỤ thêm ≥30 tick với thân ≥45%**. Biên phụ trên bị mSOW/mSOS nới ra rất sớm, nên giá phải leo tới 4542+ mới đủ điều kiện. Nhánh cứu "ở ngoài quá 40 nến VÀ ≥60% nến đóng ngoài biên" cũng đo theo biên phụ nên không bắn. Kết quả là range mất hẳn khả năng nhận ra giá đã rời vùng. Cần: nhánh dự phòng đo theo **biên chính** khi giá ở ngoài biên chính quá lâu (ở đây ~330 nến).

### 2. Nhãn SOS neo vào cây VSA 0.55x — luật vi phạm: mục 8 (Effort vs Result), lỗi hệ thống B của v4 chưa hết
- **Thuật toán gắn:** SOS tại 14:39, giá 4559.9, **VSA 0.55x** (dưới trung bình!), thân 0.92.
- **Đúng phải là:** cây phá thật nằm ngay trước đó — panel volume cho thấy cụm thanh vàng rất cao quanh 14:17–14:25 (nến cao nhất cả phiên), đúng lúc giá bật từ ~4505 lên 4530+. SOS phải neo vào cây volume nổ đó, không phải cây 0.55x sau khi mọi chuyện đã xong.
- **Dấu hiệu quyết định trên chart:** cột volume tại ~14:20 cao gấp nhiều lần đường TB20; cột tại nến SOS 14:39 thấp hơn cả đường TB.
- **Nghi phạm trong thuật toán:** v5 nói nhãn SOS được đặt **hồi tố vào cây VSA cao nhất trong đoạn, đúng hướng, đóng cửa vượt biên**. Ở đây rõ ràng hồi tố không chạy, hoặc cửa sổ hồi tố chỉ tính từ nến bắt đầu đếm 3 nến xác nhận (14:37→14:39) chứ không lùi về đầu cú bứt. Cần mở rộng cửa sổ hồi tố về tới nến đầu tiên vượt biên của cú phá.

### 3. Hai nhãn mSOS/mSOW đều rơi vào nến gần như không có khối lượng — luật vi phạm: mục 8
- **Thuật toán gắn:** mSOW 03:08 VSA **0.93x**; mSOS 13:14 VSA **0.04x** thân 0.00.
- **Đúng phải là:** mSOS/mSOW theo định nghĩa v5 là "cú phá **mạnh** nhưng thất bại". Một nến VSA 0.04x (gần như không giao dịch) và thân 0.00 (doji) thì không mạnh ở bất kỳ nghĩa nào — nó chỉ là cái râu mỏng ở đỉnh nhịp. Đây là điểm cực trị của một nhịp, nên gắn nhãn thì là **UA** (test nhẹ biên trên), hoặc không gắn gì.
- **Dấu hiệu quyết định trên chart:** thân/biên độ = 0.00 và VSA = 0.04x đọc thẳng từ phiếu.
- **Nghi phạm trong thuật toán:** điều kiện "mạnh" ở mục 5.1 là `sâu ≥ max(15 tick, 15% chiều cao range) **HOẶC** VSA ≥ 2.2×`. Nhánh "sâu" một mình đủ để phong mSOS, không cần khối lượng nào cả. Với range cao 32.2 giá thì ngưỡng sâu chỉ 4.8 giá — quá dễ. Nên bắt buộc **VÀ** một điều kiện khối lượng tối thiểu, hoặc ít nhất loại nến thân ~0.

### 4. Phase A = 21 nến, Phase C = 15 nến, Phase E = 121 nến — tỉ lệ phase méo — luật vi phạm: L8, L9
- **Thuật toán gắn:** A 21 · B 561 · C 15 · D 25 · E 121.
- **Đúng phải là:** riêng B dài nhất và C ngắn nhất thì **đúng luật**. Nhưng B dài 561 nến chủ yếu vì lỗi #1 (nuốt cả Phase D/E thật vào trong). Sau khi sửa lỗi #1, B sẽ ngắn lại còn ~400 nến và D/E dài ra — lúc đó tỉ lệ mới phản ánh cấu trúc thật.
- **Dấu hiệu quyết định trên chart:** vạch Phase C/D/E dồn cục vào 40 phút cuối trong khi cú bứt thật đã bắt đầu từ 6 tiếng trước.

### 5. ST[A] neo vào nến doji VSA 0.58x — luật vi phạm: L2 (trình bày/độ tin cậy)
- **Thuật toán gắn:** ST[A] 01:58 tại 4515.0, VSA 0.58x, thân **0.00**.
- **Đúng phải là:** ST[A] là cú quay lại test vùng climax. Vị trí 4515.0 so với climax 4491.0 và AR 4523.2 nghĩa là nó chỉ hồi xuống 25% chiều cao range — mới rời AR chút xíu, chưa test được gì ở vùng SC. Về cấu trúc thì nó là swing pivot hợp lệ nên chấp nhận được, nhưng đây là ST[A] **yếu**, nên có nhãn cảnh báo giống "AR (yếu)".
- **Dấu hiệu quyết định trên chart:** ST[A] nằm sát ngay dưới AR, cách climax 24 giá trong một range chỉ cao 32.2 giá.
- **Nghi phạm trong thuật toán:** mục 4.2 đã bỏ hết ngưỡng %, chỉ còn "swing pivot 5 nến + nhịp ≥1.5× biên độ TB". Ở phiên Á biên độ TB rất nhỏ nên ngưỡng này gần như luôn thoả. Nên thêm nhãn "(yếu)" khi ST[A] không đi quá nửa chiều cao range về phía climax.

## Đạt
- **Mục 1 — mở range:** đúng. MOVE 34.6 giá / 39 nến / hiệu suất 0.41 là move giảm thật; climax VSA 6.97x, biên độ 14.1 giá, và nến climax là đáy thấp nhất cửa sổ. Đúng L1.
- **Mục 2 — Phase A đủ 3 lần đổi hướng:** SC 4491.0 → AR 4523.2 → ST[A] 4515.0, kết thúc đúng tại ST[A]. Đúng L2.
- **Mục 3 — biên chính:** = climax + AR, không bị kéo theo giá. Biên phụ mỗi bên đúng 1 cái (4488.0 / 4542.2), đúng cực trị xa nhất. Đúng L3.
- **Mục 4 — tên range:** origin SC + phá lên = Tích luỹ. Đúng L4, và giá đi tiếp lên 4590+ xác nhận.
- **Mục 6 — Phase C ngắn nhất (15 nến):** đúng L8, và dùng đúng cách gán ngược case khó (chỉ có LPS[C], không có Spring).
- **Mục 9 — không spam nhãn:** mỗi bên đúng 1 nhãn thăm dò, LPS[C] một điểm. Đúng L6, L7.
