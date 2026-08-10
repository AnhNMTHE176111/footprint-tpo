# Chấm bài #40 — Tích luỹ (ACC) · 2026-07-06 00:01 → 01:57 (116 nến M1)

**Điểm: 2/10** — vẽ lại từ đầu: biên chính trên nằm **giữa** vùng giá, nên toàn bộ phần Phase B trở đi đọc sai.

## Lỗi (nặng → nhẹ)

### 1. AR là pivot nhiễu → biên chính trên cắt ngang giữa vùng giá — luật vi phạm: L2, L3
- **Thuật toán gắn:** AR 00:17 @ 4193.9, **VSA 0.59x**, thân/biên độ **0.24**. Biên chính = 4182.4 – 4193.9 (11.5 giá).
- **Đúng phải là:** AR phải là một **cú bật ngược thật** xác lập biên. Nến 00:17 volume dưới trung bình, gần như doji — đó là đỉnh của một nhịp lún, không phải Automatic Rally.
- **Dấu hiệu quyết định trên chart:** đường "biên CHÍNH trên 4193.9" **cắt ngang thân** gần như toàn bộ cụm nến từ 00:33 tới 01:30 — suốt Phase B và Phase C giá sống chủ yếu **ở trên** đường đó (4195–4204), thỉnh thoảng mới lún xuống dưới. Một mức mà giá qua lại tự do hàng chục lần thì không phải biên.
- **Biên đúng của vùng này** đọc bằng mắt: dưới ≈ 4182–4184 (climax + LPS[C]), trên ≈ 4204–4205 (cụm đỉnh 01:09–01:16). Tức là biên chính trên đang bị đặt thấp hơn biên thật ~11 giá, đúng bằng cả chiều cao range mà thuật toán khai báo.
- **Nghi phạm trong thuật toán:** AR = swing pivot đầu tiên xác nhận sau 5 nến + sàn 1.5× biên độ TB + (v6) ≥0.5× nhịp hồi lớn nhất trong lòng move. Cả ba đều là ràng buộc **giá**, không có ràng buộc **chất lượng volume** — `ar_vsa` đã được đo (mục 0c #9) nhưng chưa gate. Đây đúng là ca cần gate: AR VSA 0.59x.

### 2. SOS không vượt được biên phụ, lại nằm THẤP HƠN mSOS trước đó — luật vi phạm: L3
- **Thuật toán gắn:** mSOS 01:16 @ **4204.8** (= đúng mức biên phụ trên 4204.8), rồi SOS 01:32 @ **4203.7**, VSA 2.33x, **thân 0.26**.
- **Đúng phải là:** "SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua **biên phụ**". SOS ở 4203.7 thấp hơn biên phụ 4204.8 — nó chưa bứt qua cực trị mà chính cú thăm dò trước đã tạo. Ngoài ra thân 0.26 < ngưỡng 45% mà chính spec đòi để công nhận SOS.
- **Cây phá thật** nằm ở 01:41–01:45 (cụm volume vàng cao nhất nửa sau ảnh, đẩy giá lên 4215) — nhãn SOS phải hồi tố về đó.
- **Nghi phạm trong thuật toán:** vẫn là biến thể của "biên phụ tự nới rồi tự vượt" (sửa #6). Nâng ngưỡng outside/timed-out từ 10 lên 30 tick **không chạm** vào lỗi này, vì lỗi nằm ở chỗ mốc so sánh của SOS đã bị v6 đổi từ biên phụ sang **biên chính** (mục 5.1) — nên SOS chỉ cần vượt 4193.9 là đủ. Hai luật đang đá nhau: spec v6 nói "mốc = biên chính", L3 của người học nói "phải bứt qua biên phụ".

### 3. Nhãn mSOS rơi vào nến gần như doji — luật vi phạm: mục 8 (effort/result), mục 9
- **Thuật toán gắn:** mSOS 01:16, **VSA 0.72x**, thân/biên độ **0.04**.
- **Đúng phải là:** mSOS phải neo vào cây **phá thật** của đoạn thăm dò — nến mạnh nhất, không phải nến cao nhất về giá. Trong đoạn 01:09–01:16 có cây volume rõ hơn hẳn (cột vàng ~01:09 trên panel khối lượng).
- **Nghi phạm trong thuật toán:** sửa #5 của v7 ("quét lại lấy nến VSA cao nhất trong đoạn thăm dò") **chưa có hiệu lực ở ca này** — nhãn vẫn nằm đúng nến cực trị **giá** (4204.8 = đỉnh) chứ không phải nến cực trị **volume**. Nghi ngờ nhánh hạ cấp từ pending-shock đi đường khác, bỏ qua bước quét lại.

### 4. Phase E dài đúng 1 nến — luật vi phạm: L10 (và lỗi J của v5 tái phát)
- **Thuật toán gắn:** D = 25 nến (= đúng trần cửa sổ chờ retest), E = **1 nến**, range đóng 01:57.
- **Đúng phải là:** Phase E là đoạn giá rời range đi tìm vùng giá mới. 1 nến thì không mô tả được gì; và ngay sau đó giá **rơi thẳng** từ 4215 về 4180 — thấp hơn cả mức climax.
- **Dấu hiệu quyết định trên chart:** nửa phải ảnh (02:00–02:39) là một chân giảm liên tục, nằm hoàn toàn ngoài khung range.
- **Nghi phạm trong thuật toán:** Phase D chạm đúng trần 25 nến rồi Phase E mở ở nến kế và lập tức bị chốt vì giá đã lùi vào trong biên — vá lỗi J chỉ xử lý ca "giá chạy tiếp", chưa xử lý ca "E mở ra đúng lúc giá quay đầu".

### 5. LPS[D] sai vai — luật vi phạm: L10, L7
- **Thuật toán gắn:** LPS[D] 01:37 @ 4206.6 — **cao hơn** SOS 4203.7.
- **Đúng phải là:** LPS[D] là nhịp hồi **ngược** hướng phá, giữ được ngoài biên. Một điểm cao hơn cả SOS thì nằm trong thân cú phá, không phải retest.

### 6. Kết cục thực tế là một upthrust, không phải tích luỹ hoàn tất — mục 10, §9 THEORY
- Giá phá lên 4215 rồi trả lại toàn bộ, xuyên qua cả biên chính dưới 4182.4 xuống 4180. Gọi "Tích luỹ (ACC) completed" là đọc ngược kết cục.
- Ghi nhận: luật thuật toán "SOS xác nhận thì đóng range" đang chống lưng cho nhãn này, nên đây là lỗi thiết kế chứ không phải lỗi thực thi.

## Đạt
- **ST[A] tốt (L2):** 00:26 @ 4183.0, cách climax 4182.4 đúng 0.6 giá — test lại **đúng vùng climax**, hồi 0.95 khoảng AR↔climax, VSA 3.43x. Đây là ST[A] chuẩn nhất cả lô.
- **Điều kiện mở range (L1):** MOVE giảm 24.3 giá / 33 nến, hiệu suất 0.45; climax VSA 3.72x, biên độ 11.1 giá, đóng đúng đáy — climax chặn được move thật.
- **Mỗi bên tối đa 1 biên phụ** (chỉ có trên, 4204.8), tỷ lệ 1.95× nằm trong guard (L3).
- **Chú thích nỗ lực/kết quả và SOT đọc đúng dấu:** er=0.46 → "HIỆU QUẢ"; SOT-up volume 0.72 → "cạn kiệt". Lỗi hard-code v6 đã hết.
- **LPS[C] đặt hợp lý:** 01:00 @ 4184.3, sát biên chính dưới, đúng một điểm duy nhất (L7, L8).
