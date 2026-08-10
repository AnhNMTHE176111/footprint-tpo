# Chấm bài #27 — "Chưa rõ (SC) (ACC?)" [superseded] · 2026-06-02 01:01 → 03:54 (173 nến M1)

**Điểm: 6/10** — Tỷ lệ phase lần này rất đẹp, nhưng climax chọn sai điểm nên biên chính dưới thành đường chết, và range đủ bằng chứng mà không dám đặt tên.

## Lỗi (nặng → nhẹ)

### 1. Climax chọn sai điểm → biên chính dưới 4501.0 là đường chết — luật vi phạm: L2 + L3
- **Thuật toán gắn:** SC tại 01:01 (low 4501.0, VSA 5.98x) → biên chính dưới 4501.0. ST[A] tại 01:52 (low 4492.3, VSA 2.40x, thân/biên 0.15).
- **Đúng phải là:** cây thật sự chặn move và làm đảo hành vi là nến **01:52** — nó mới là đáy cấu trúc. Range nên mở lại từ đó, hoặc chí ít biên chính dưới phải là 4492.3.
- **Dấu hiệu quyết định trên chart:** ST[A] xuyên **8.7 giá** dưới climax = **41% chiều cao biên chính (21.0 giá)**. Đó không phải "test lại vùng climax" theo L2 mà là một cú phá xuống mới. Hệ quả nhìn thấy ngay trên ảnh: đường liền cam 4501.0 chạy suốt chart mà **không có một nến nào trong Phase B chạm tới** (đáy Phase B chỉ ~4506) — một biên chính không bao giờ được test là biên vẽ sai. Thêm nữa, thanh volume vàng cao nhất khu vực nằm ở nến 01:52 chứ không ở 01:01.
- **Nghi phạm trong thuật toán:** ST[A] hiện chỉ có ngưỡng **sàn** (hồi ≥55%) mà không có ngưỡng **trần**. Cần thêm luật: nếu ST[A] xuyên qua mức climax quá X% chiều cao range (đề xuất 25-30%) thì **dời climax về ST[A]** và dựng lại Phase A, thay vì giữ climax cũ.

### 2. Không đặt tên range dù đã đủ bằng chứng phá thật — luật vi phạm: L4
- **Thuật toán gắn:** tiêu đề "Chưa rõ (SC) (ACC?)", trạng thái `superseded — không đặt tên 4 mẫu hình`.
- **Đúng phải là:** **Tích luỹ (ACC)**. L4 phân xử bằng đúng hai dữ kiện: origin = move giảm bị SC chặn, hướng phá thật = **lên**. Cả hai đều đã có trên chart.
- **Dấu hiệu quyết định trên chart:** SOS 03:29 giá 4525.4 (VSA 5.38x) đóng cửa trên biên chính 4522.0; LPS[D] 03:34 tại 4523.1 giữ được trên biên; sau đó giá đi thẳng lên 4540. Đây là CBR hoàn chỉnh theo L10 — không có gì "chưa rõ".
- **Nghi phạm:** cờ `superseded` (range bị range mới thay thế) đang **chặn** bước đặt tên. Hai việc này độc lập: một range bị thay thế vẫn phải được đặt tên theo L4.

### 3. Thiếu hẳn Phase E — luật vi phạm: L10
- Bảng phase chỉ có A/B/C/D. Trong khi trên chart, sau LPS[D] giá rời range đi tìm vùng giá mới rất rõ (4525 → 4540, hơn 60 nến). Đó đúng định nghĩa Phase E.
- **Nghi phạm:** cùng cờ `superseded` — range bị cắt tại thời điểm range mới sinh ra, nên Phase E không kịp mở.

### 4. Biên phụ trên 4522.5 chỉ hơn biên chính 0.5 giá — luật vi phạm: L3
- Chênh **5 tick**. Không phải một nỗ lực phá biên, chỉ là bóng nến. Trên ảnh hai đường dính vào nhau, chữ "biên phụ trên 4522.5" đè lên chữ "biên CHÍNH trên 4522.0". Cùng nghi phạm với bài #26: nhánh dựng biên phụ không dùng ngưỡng 30 tick.

## Đạt
- **Mục 1 (L1):** MOVE giảm 18.3 giá / 29 nến / hiệu suất 0.59, chuỗi -1 (VSA 3.91x) → climax (VSA 5.98x) rất dứt khoát. Điều kiện mở range thoả.
- **Mục 5 (L9):** Phase B 89 nến — dài nhất, cách biệt rõ. Đúng L9.
- **Mục 6 (L8):** Phase C **7 nến** — phase ngắn nhất, cách biệt rõ với D (26 nến). Đây là kết quả tốt nhất trong 6 bài lô này; việc bỏ ràng buộc "đúng nửa range" ở v7.1 cho thấy tác dụng. LPS[C] VSA 0.80x (volume co lại) đúng chất test, và được gán ngược từ SOS theo đúng quy trình L8 case khó.
- **Mục 7 (L10) — phần D:** SOS + LPS[D] giữ ngoài biên = cặp chuẩn.
- **Mục 8:** SOS volume nổ 5.38x, test LPS[C] volume co 0.80x — đọc effort/result đúng chiều.
- **Mục 9:** không nhãn dư, không lẫn vai LPS[C]/LPS[D].
- Nhãn AR ghi kèm "(yếu)" — trung thực, AR mất 28 nến mới thành hình nên đánh dấu yếu là hợp lý.
