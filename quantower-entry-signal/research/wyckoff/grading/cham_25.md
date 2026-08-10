# Chấm bài #25 — Tích lũy (ACC) · 2026-05-26 11:43 → 13:52 (129 nến M1)

**Điểm: 7/10** — Khung range vẽ đúng, chỉ cần sửa nhãn Phase C và cách dựng biên phụ trên.

## Lỗi (nặng → nhẹ)

### 1. Gọi "Spring" cho một cú phá lùng bùng ngoài biên hơn chục nến — luật vi phạm: L5
- **Thuật toán gắn:** `Spring` tại 12:31, giá 4533.1, trạng thái confirmed, mở Phase C dài 18 nến.
- **Đúng phải là:** **Shakeout** (một SOW thất bại), không phải Spring.
- **Dấu hiệu quyết định trên chart:** biên chính dưới = 4538.0. Trên ảnh, cụm nến từ khoảng 12:29 đến 12:42 nằm trọn **dưới** đường 4538.0 — tức giá ở ngoài biên khoảng 13 nến trước khi hồi vào. L5 nói rõ: Spring = quay vào trong ≈3-4 nến hoặc ít hơn; lùng bùng ngoài một lúc = Shakeout. Chính Phase C dài 18 nến đã tự tố cáo điều này.
- **Bằng chứng đối chiếu nội bộ:** bài #30 có cú phá tương tự (dưới biên ~15 nến) lại được gán **Shakeout**. Cùng một hiện tượng, hai tên gọi → tiêu chí phân loại đang không nhất quán.
- **Nghi phạm trong thuật toán:** bộ đếm "số nến quay lại" nhiều khả năng tính từ **nến cực trị** (nến tạo đáy 4533.1) chứ không tính từ **nến đầu tiên đóng cửa ngoài biên**. Phải đổi mốc đếm về nến phá biên đầu tiên.

### 2. Biên phụ trên do chính cú phá THÀNH CÔNG sinh ra — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ trên 4556.8, vẽ đường đứt kéo ngược về tận đầu Phase A.
- **Đúng phải là:** phía trên **không có biên phụ**. Định nghĩa L3: biên phụ = cực trị xa nhất mà một thế lực **cố phá range gốc** tạo ra (UA/UT/DA, ST[A] vượt climax) — tức một nỗ lực bị đẩy về. 4556.8 là đỉnh đạt được **sau khi** SOS đã phá thật và giá đã sang Phase D/E; đó là kết quả của cú phá, không phải một nỗ lực bị chặn.
- **Dấu hiệu quyết định trên chart:** trong toàn bộ Phase A→C giá chưa từng chạm 4556.8 (đỉnh Phase B chỉ ~4549). Đường đứt 4556.8 vắt ngang một vùng thời gian mà giá chưa bao giờ tới → vô nghĩa về mặt đọc chart.
- **Hệ quả kèm theo:** SOS ở 4552.5 bị so với một biên phụ 4556.8 mà chính nó sinh ra → không bao giờ "đủ mạnh" theo L3. Đây đúng là vòng lặp "biên phụ tự nới rồi tự vượt" mà v7.1 nói đã sửa cho SOS/SOW; nhưng phần **vẽ** biên phụ vẫn chưa được sửa theo.
- **Nghi phạm trong thuật toán:** hàm cập nhật biên phụ vẫn chạy trên toàn bộ range (kể cả sau khi Phase D được chốt). Phải khoá cập nhật biên phụ tại thời điểm SOS/SOW được xác nhận.

### 3. Phase C (18 nến) dài hơn Phase D (13 nến) — luật vi phạm: L8
- **Thuật toán gắn:** A 16 / B 32 / C 18 / D 13.
- **Đúng phải là:** C phải là phase ngắn nhất. Nếu sửa lỗi #1 (Shakeout thay Spring) thì mốc kết thúc Phase C nên là nến đầu tiên đóng cửa trở lại **trên** 4538.0 (~12:42), tức C ≈ 11-12 nến, ngắn hơn D — cấu trúc lập tức hợp lệ.
- **Nghi phạm:** Phase C đang kết thúc tại thời điểm phát hiện SOS trừ đi một offset cố định, thay vì kết thúc tại nến hồi về trong biên.

### 4. Nhãn SC nằm trước nến mở range (lỗi đã biết, chưa sửa)
- SC ghi 11:35 giá 4540.4 (VSA 5.62x) trong khi range mở tại 11:43 (low 4538.0, VSA 2.71x). Nhãn climax đứng **ngoài** khung range, và giá nhãn 4540.4 **không** trùng biên chính dưới 4538.0 → người đọc chart không hiểu đường biên dưới lấy từ đâu. Ghi nhận theo yêu cầu, không tính vào điểm.

## Đạt
- **Mục 1 (L1):** MOVE giảm 23.0 giá / 52 nến / hiệu suất 0.60, bị nến 11:43 (VSA 2.71x, biên độ 5.6 giá) chặn tại cực trị — điều kiện mở range thoả rõ.
- **Mục 2 (L2):** đủ 3 lần đổi hướng, ST[A] 11:58 tại 4536.0 hồi trọn khoảng AR↔climax (>100%, thừa ngưỡng 55%), Phase A kết thúc đúng tại ST[A]. Ngưỡng 0.55 hoạt động tốt ở bài này.
- **Mục 4 (L4):** move giảm + SC + phá lên thật = Tích luỹ. Tên đúng.
- **Mục 5 (L9):** Phase B 32 nến, dài nhất trong A–D. Bias test biên = 0 (chạm cả hai biên) — range cân, đọc đúng.
- **Mục 7 (L10):** SOS 12:49 đóng cửa vượt biên chính trên; Phase E 51 nến đi tìm vùng giá mới lên 4561. Không có LPS[D] nhưng theo Ca #21 (7.pdf) Phase D **không bắt buộc** có BU — không trừ điểm.
- **Mục 8:** climax VSA 2.71x, SOS VSA 2.15x có volume tăng, Shakeout VSA 3.31x — đọc effort/result hợp lý.
