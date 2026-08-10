# Chấm bài #51 — Chưa rõ (SC) (ACC?) · 2026-07-16 13:05 → 2026-07-17 20:59 (1853 nến M1)

**Điểm: 4/10** — Phase A vẽ đúng và biên chính đặt đúng chỗ, nhưng cả 1819 nến còn lại bị nhét hết vào Phase B: cú rũ sâu nhất của range không có nhãn, cú phá lên không được kết luận, range đóng ở trạng thái "chưa rõ".

## Lỗi (nặng → nhẹ)

### 1. Cực trị sâu nhất của range không được gắn nhãn — luật vi phạm: L3 + L8
- **Thuật toán gắn:** mSOW tại 07-17 13:39, giá **3994.4** (VSA 4.61x).
- **Đúng phải là:** nhãn phải neo tại **3963.0** (đáy của chính nhịp đó, ngày 07-17 quanh 13:10-13:25) — đó là mức đã tạo ra **biên phụ dưới 3963.0** mà chính phiếu số liệu ghi. Đó là cú rũ (Shakeout) sâu nhất toàn range, ứng viên Phase C số một.
- **Dấu hiệu quyết định trên chart:** biên phụ dưới = 3963.0; nhãn mSOW đứng ở 3994.4, tức **cách đáy thật 31.4 giá**, gần đúng giữa biên chính (3977.1–4012.6). Một mSOW nằm giữa range là vô nghĩa: theo định nghĩa nó phải là một cú thò ra ngoài biên.
- **Nghi phạm trong thuật toán:** đúng chỗ vừa vá ở v7 (#5) — "quét lại lấy nến VSA cao nhất trong đoạn thăm dò". Lấy VSA cao nhất mà **không ràng buộc nến đó phải nằm ngoài biên / gần cực trị của nhịp** thì nhãn trôi vào giữa range. Phải giao hai điều kiện: VSA cao nhất **trong số các nến đóng/chạm ngoài biên**.

### 2. Không kết luận cấu trúc dù đã có đủ chuỗi rũ → phá — luật vi phạm: L8, L10
- **Thuật toán gắn:** Phase A (35n) → Phase B (1819n), hết. Tên range "Chưa rõ (SC)".
- **Đúng phải là:** rũ xuống 3963.0 (07-17 ~13:20) rồi quay lên **rất nhanh** → Phase C; cú lên đóng cửa vượt biên chính trên và chạm 4028.9 (mSOS, VSA 2.41x, thân 0.90) → ứng viên SOS/Phase D. L8 nói rõ: case khó thì **chờ SOS xuất hiện rồi quay lại vẽ Phase C**. Ở đây SOS đã xuất hiện mà máy vẫn không quay lại vẽ.
- **Dấu hiệu quyết định trên chart:** sau mSOS, giá dao động 4012–4028, tức **quanh và trên** biên chính trên 4012.6 suốt phần còn lại; chỉ có một nhịp thụt xuống ~4003 gần cuối. Đây là hành vi "giữ được ngoài biên" chứ không phải phá hụt.
- **Nghi phạm trong thuật toán:** điều kiện SOS bắt buộc đóng cửa vượt **biên phụ trên**, mà biên phụ trên 4028.9 lại do **chính cây mSOS đó** tạo ra → không bao giờ vượt được chính mình. Đúng lỗi "biên phụ tự nới rồi tự vượt"; ngưỡng 30 tick (fix #6) không cứu được ca này vì cây phá dừng đúng tại mức nó vừa nới.

### 3. Phase B chiếm 98% range, không có Phase C/D/E — luật vi phạm: L9 (hệ quả của lỗi 1-2)
- **Thuật toán gắn:** B = 1819/1853 nến.
- **Đúng phải là:** B dài nhất là đúng tinh thần L9, nhưng "dài nhất" không có nghĩa "nuốt hết". Một range 1853 nến M1 (hơn 30 giờ) mà không sinh nổi một phase nào sau B thì đó là dấu hiệu máy đang **không đọc được** chứ không phải thị trường không cho tín hiệu.

### 4. (Trình bày) Thiếu hẳn dòng nỗ lực ↔ kết quả
- Phiếu #52 và #53 đều có dòng "Nhịp nỗ lực/kết quả cao nhất"; #51 — bài có Phase B **dài nhất cả lô** — lại không có dòng nào. Mục 8 (Effort vs Result) không chấm được. Nghi phạm: nhánh tính er bị bỏ qua khi Phase B quá dài hoặc khi range không có Phase C.

## Đạt
- **Mục 1 (L1):** MOVE trước climax thật — 67.7 giá / 61 nến, hiệu suất 0.45, bị cụm nến 13:02 (VSA 2.91x) + 13:04 (2.34x) chặn lại. Mở range hợp lệ.
- **Mục 2 (L2):** đủ 3 lần đổi hướng. AR 4012.6 là cú bật thật (35.5 giá). ST[A] 3985.5 = hồi **76%** khoảng AR↔climax, tức quay về sát vùng SC — đây là ST[A] đúng nghĩa, không phải ngọ nguậy giữa range. Ngưỡng 0.4 mới (fix #2) không bị lạm dụng ở bài này.
- **Mục 3 (L3):** biên chính = climax 3977.1 + AR 4012.6, cố định, không kéo theo giá. Biên phụ mỗi bên đúng 1 (3963.0 / 4028.9), đều là cực trị xa nhất thật.
- **Nhãn cụm climax (fix #4):** SC neo tại 13:04, lệch đúng 1 nến so với nến mở range, giá 3979.1 vs mức climax 3977.1 — chấp nhận được.
