# Chấm bài #15 — Tái tích lũy (RE-ACC) · 2026-05-06 03:20 → 08:12 (159 nến M1)

**Điểm: 1/10** — Không nên vẽ range ở đây. Nhãn BCLX nằm giữa move tăng, ngoài hẳn khung range; "climax" mở range có VSA 0.58x; biên chính rộng 7.5 giá. Đây là một chỗ nghỉ 7 giá giữa xu hướng tăng 91 giá, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX nằm GIỮA move tăng, ngoài khung range, thấp hơn biên trên 10.7 giá — luật vi phạm: L1 + mục 3(2) THEORY
- **Thuật toán gắn:** nhãn BCLX ở 02:56, giá **4684.5**, VSA 10.10x — nến này nằm **trước nến mở range 24 nến** và **ngoài khung range** (trên ảnh nhãn treo hẳn bên trái, dưới đáy khung).
- **Đúng phải là:** climax phải là **cực trị chặn move**. Cây 02:56 ở 4684.5 không chặn gì — giá tiếp tục leo lên 4695.2 sau nó. Biên chính trên là 4695.2, cách nhãn 10.7 giá.
- **Dấu hiệu quyết định trên chart:** đường biên chính trên (nét liền cam) nằm ở 4695.2; chấm BCLX nằm rõ ràng bên dưới và bên trái khung. Người đọc chart không thể nối được nhãn với biên.
- **Nghi phạm:** đúng lỗi cụm climax đã ghi ở 13.1c (đã thử sửa rồi revert). Ở đây cửa sổ nhãn không chặn phía TRƯỚC nên nhãn trượt ngược 24 nến vào giữa move.

### 2. Nến mở range không phải climax — luật vi phạm: mục 3(1) THEORY
- **Thuật toán gắn:** climax tại 03:20, VSA **0.58x**, biên độ nến **1.0 giá**, volume **3 hợp đồng**.
- **Đúng phải là:** ngưỡng mở range là biên độ ≥1.4× ATR20 **và** VSA ≥2.2x. Nến này thoả không điều kiện nào.
- **Dấu hiệu quyết định:** 12 nến quanh climax volume 2, 8, 1, 6, 2, 3, **3**, 1, 2, 1, 1, 2. Không có cây nào đáng gọi cao trào.

### 3. Cú phá thật bị hạ thành mSOS, SOS gán muộn 77 phút vào cây VSA 1.38x — luật vi phạm: L3 + mục 5.1
- **Thuật toán gắn:** mSOS 06:42 tại **4709.3**, VSA **11.27x** (cây to nhất range); SOS 07:59 tại 4728.0, VSA **1.38x**.
- **Đúng phải là:** cú 06:42 đã đóng cửa vượt biên phụ trên (4699.2) tận **10.1 giá** và trên ảnh giá **không hề lùi lại dưới 4695.2** sau đó — nó lơ lửng 4700-4710 rồi đi tiếp. Đó là **SOS thật**. Nhãn phải hồi tố về cây VSA 11.27x, không phải cây 1.38x cách đó 77 phút.
- **Dấu hiệu quyết định:** đây là ca "hàng trăm nến ngoài biên không được công nhận" mà vòng v7 đã ghi nhận — **vẫn còn nguyên** sau bản vá 13.1c. Từ 06:42 tới 07:59 gần như toàn bộ nến đóng cửa trên 4699.
- **Nghi phạm:** nhánh phân loại decisive/outside sau khi giá thoát ra; và bước hồi tố nhãn SOS quét không tới cây 06:42.

### 4. Thiếu hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** dải phase A(12) → B(139) → **D(7)** → E(2). Không có C.
- **Đúng phải là:** L8 nói khi không có Spring/UTAD thì phải gán ngược Phase C từ SOS/SOW. Range này có SOS mà vẫn không sinh được Phase C.
- **Nghi phạm:** cửa sổ gán ngược `min(60, 0.8×len(B))` chạy trên biên chính chỉ 7.5 giá — mọi pivot đều "quá gần biên" hoặc "quá xa", không lọt điều kiện `_in_range`.

### 5. Phase D 7 nến / Phase E 2 nến — luật vi phạm: L10
- Phase D 7 nến không đủ chỗ cho một nhịp retest có ý nghĩa; LPS[D] 08:01 chỉ cách SOS 2 nến. Phase E 2 nến không mô tả được "đi tìm vùng giá mới" — trong khi trên ảnh giá thực tế chạy tiếp lên 4765 sau đó.

### 6. Range 7.5 giá = 0.16% — vùng đấu giá quá vụn
- Biên chính rộng 7.5 giá, tức khoảng 2 cây nến M1 bình thường của phiên Mỹ. Cả Phase A→E được nhét vào một dải bằng 8% chiều dài move trước đó (91.7 giá). Theo chuẩn chấm: TR M1 quá vụn thì phải nghi là nhiễu, không phải cấu trúc.

### 7. MOVE hiệu suất 0.36 — sát sàn
- Ngưỡng là 0.35, đo được 0.36. Nhìn ảnh move tăng có thật (4590 → 4695) nhưng đường chân MOVE cắt chéo qua rất nhiều nhịp lắc — hiệu suất sát sàn xác nhận đó là một đợt tăng bậc thang, và không có cây nào chặn nó lại.

## Đạt
- **Tên range (L4): ĐẠT về hình thức.** Origin BCLX + phá lên = Tái tích luỹ, khớp bảng 4 pattern và khớp thực tế (giá đi tiếp lên 4765).
- **Tỉ lệ B dài nhất (L9): ĐẠT** (139/159 nến).
- **Biên phụ (L3): ĐẠT hình thức** — chỉ 1 biên phụ trên (4699.2), tỉ lệ 1.53×.

## Cần hỏi người học
- Có nên đặt **sàn tuyệt đối cho chiều cao biên chính** (ví dụ ≥ 0.5× ATR ngày, hoặc ≥ 10 giá với vàng)? Bài này và #14 đều là range dưới 13 giá và cả hai đều là nhiễu. Người học đã chốt "không đặt sàn ĐỘ DÀI (số nến)" — nhưng sàn về CHIỀU CAO là câu hỏi khác, chưa được phân xử.
