# Chấm bài #14 — Tái tích luỹ (RE-ACC) · 2026-05-06 03:20 → 08:12 (159 nến M1)

**Điểm: 1/10** — Không nên vẽ range ở đây. Đây là một đoạn xu hướng tăng bị cắt ngang bằng một cây doji 3 lot ở phiên Á chết, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Cây mở range không phải climax — luật vi phạm: L1 + mục 3(1) THUẬT TOÁN
- **Thuật toán gắn:** `climax BCLX @4695.2, VSA 0.58x, biên độ nến 1.0 giá, volume = 3 hợp đồng`.
- **Đúng phải là:** ngưỡng mở range của chính thuật toán là biên độ ≥1.4× TB và VSA ≥2.2×. Cây này **trượt cả hai**. Không có cao trào nào chặn move cả — giá chỉ khựng lại vài phút rồi đi tiếp lên 4728.
- **Dấu hiệu quyết định trên chart:** 6 nến quanh climax có volume 1–3 lot, ba nến liền có `thân/biên độ = 0.00` (giá không nhúc nhích); dữ liệu còn thiếu hẳn các phút 03:16, 03:21, 03:22, 03:24–03:26.
- **Nghi phạm trong thuật toán:** cụm climax dời **mức** theo cực trị giá 8 nến nhưng **không kiểm lại** cây được chọn có còn thoả ngưỡng VSA/biên độ hay không. Cây thoả ngưỡng thật (VSA 10.10× lúc 02:56) nằm ngoài cụm.

### 2. Nhãn BCLX nằm ngoài khung range VÀ dưới đáy range — luật vi phạm: L3 + vá v7 #4
- **Thuật toán gắn:** nhãn `BCLX 02:56 @4684.5` trong khi range bắt đầu 03:20 và biên chính dưới là 4687.7.
- **Đúng phải là:** climax phải là **cực trị trên** của range phân phối/tái tích luỹ; ở đây nhãn nằm **thấp hơn cả đáy range 3.2 giá** và lệch 24 phút về bên trái khung.
- **Dấu hiệu quyết định trên chart:** chấm BCLX đỏ nằm hẳn dưới-trái hình chữ nhật range.
- **Nghi phạm trong thuật toán:** vá v7 #4 chỉ kẹp trong "cửa sổ cụm 8 nến" nhưng không kẹp theo `range_start` và **không kẹp theo giá** (nhãn climax phải nằm ở phía biên mà nó tạo ra). Đây là ca nặng nhất của lỗi này trong lô.

### 3. Range chỉ cao 7.5 giá (0.16%) và giá rời khỏi nó ngay sau Phase A — luật vi phạm: L1 (không phải vùng đấu giá) + L9
- **Thuật toán gắn:** Phase B dài 139 nến.
- **Đúng phải là:** nhìn ảnh, từ ~04:05 trở đi toàn bộ nến nằm **trên** biên phụ trên 4699.2 và đi một mạch lên 4728. "Phase B" ở đây là một chân xu hướng nằm ngoài range, không phải giai đoạn cân bằng xây nguyên nhân.
- **Dấu hiệu quyết định trên chart:** biên chính 4687.7–4695.2 chỉ dày bằng ~1/4 chiều cao một nến của đợt tăng ngay sau đó; SOS đặt tại 4728.0, tức **4.4 lần chiều cao range** phía trên biên.
- **Nghi phạm trong thuật toán:** không có sàn chiều cao range tối thiểu (người học đã chốt không đặt sàn **độ dài**, nhưng chiều cao 0.16% ở phiên 1–3 lot là nhiễu thuần tuý). Guard "biên phụ/biên chính > 4.0×" cũng vô dụng vì biên phụ không được nới (lỗi 4).

### 4. Biên phụ trên không được nới bởi cú thăm dò thất bại — luật vi phạm: L3
- **Thuật toán gắn:** `biên phụ trên 4699.2`, trong khi có `mSOS 06:42 @4709.3 (VSA 11.27x)`.
- **Đúng phải là:** biên phụ = cực trị **xa nhất** một thế lực đã đẩy tới; 4709.3 > 4699.2 nên biên phụ trên phải là 4709.3 (thực tế giá còn lên cao hơn nữa).
- **Nghi phạm trong thuật toán:** nhánh đóng băng biên phụ trong `C_pending` (vá v6 #2) đang chặn nhầm — phía đang test chỉ được nới "một lần sau khi biết kết cục", và lần nới đó không xảy ra.

### 5. Phase C thiếu; ST[A] không test được vùng climax — luật vi phạm: L8, L2
- `ST[A] 03:44 @4692.4` cách climax 4695.2 tới 2.8 giá = 37% chiều cao range — không phải một cú test vùng cao trào. Vá v7 #2 (ngưỡng hồi 0.4) cho qua vì tính theo tỷ lệ AR↔climax (0.63) chứ **không** ràng buộc khoảng cách còn lại tới climax — đúng đầu mục "ST[A] vẫn thiếu ràng buộc khoảng cách đáy tới climax" ghi ở 13.1, chưa vá.
- Không có Phase C (A→B→D→E), vi phạm L8 giống bài #13.

### 6. (Trình bày) Dải phase hở nến
- A kết thúc 03:44 nhưng B bắt đầu 03:48; B kết thúc 07:57 nhưng D bắt đầu 07:59. Do dữ liệu khuyết nến, nhưng nên kẹp liền mạch để dải phase không có khe.

## Đạt
- Tên range: BCLX origin + phá lên = Tái tích luỹ, khớp L4 (đây là điều đúng duy nhất về mặt đặt tên).
- Chú thích nỗ lực/kết quả đọc đúng dấu er (er=0.18 → "nhịp HIỆU QUẢ") — vá v7 #1 chạy tốt.

## Cần hỏi người học
- Có chấp nhận đặt **sàn chiều cao range tuyệt đối** (ví dụ ≥ 1.0× ATR20 hoặc ≥ 0.3% giá) không? Người học đã chốt không đặt sàn *độ dài*, nhưng ca này chết vì *chiều cao*, và nó lặp lại ở mọi range phiên Á thanh khoản 1–3 lot.
