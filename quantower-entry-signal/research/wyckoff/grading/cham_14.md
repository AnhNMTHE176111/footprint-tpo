# Chấm bài #14 — Tái tích lũy (RE-ACC) · 2026-05-05 07:36 → 13:35 (188 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây: 12.4 giá bề rộng, phiên Á volume 1-7 hợp đồng, không có climax thật. Và Phase C nuốt trọn đoạn giá đã bùng ra ngoài biên.

## Lỗi (nặng → nhẹ)

### 1. Phase C (60 nến) trùm lên cả đoạn giá đã phá biên và chạy 20 giá — luật vi phạm: L8 + L10
- **Thuật toán gắn:** Phase C = 11:20 → 13:06; Phase D chỉ bắt đầu 13:08 với SOS tại 4625.3.
- **Đúng phải là:** trên ảnh giá đóng cửa vượt biên phụ trên (4603.6) từ khoảng **11:42** và leo liên tục lên 4624 trong khoảng 12:16-13:00. Cú phá thật đã xác nhận từ ~11:45 → **Phase D phải bắt đầu ở đó**, Phase C chỉ được dài vài nến quanh LPS[C].
- **Dấu hiệu quyết định trên chart:** SOS gán ở 4625.3, tức **cao hơn biên chính trên 24.7 giá = gấp 2 lần chiều cao cả range (12.4 giá)**. Một nhãn "phá vỡ" không bao giờ được đặt sau khi giá đã đi hết 2 lần chiều cao range.
- **Nghi phạm:** Phase C không được thoát sớm khi giá đã đóng cửa ngoài biên nhiều nến liên tiếp; điều kiện thoát vẫn là "3 nến liên tiếp + 30 tick" đo tại thời điểm muộn, cộng với trần 120 nến chưa bị chạm nên C cứ kéo dài.

### 2. Không đủ điều kiện mở range — luật vi phạm: L1
- **Thuật toán gắn:** BCLX? tại nến 07:36, VSA **1.59x**, biên độ nến **1.1 giá**; phiếu ghi thẳng "SINH TU CU PHA, khong co cao trao thuc su"; **không có dòng MOVE trước climax**.
- **Đúng phải là:** L1 đòi một MOVE xu hướng bị climax chặn lại. Ở đây không có move nào được đo, và cây "climax" dưới cả ngưỡng 2.2x.
- **Dấu hiệu quyết định:** 12 nến quanh climax có volume 1, 3, 2, 1, 30, 2, **7**, 1, 1, 2, 1, 1 — mười một trên mười hai nến dưới 4 hợp đồng. Cả range chỉ rộng 12.4 giá (0.27%). Đây là dải nhiễu phiên Á, không phải vùng đấu giá.
- **Nghi phạm:** cơ chế SIDEWAYS cho phép mở range mà **miễn hoàn toàn** điều kiện L1. Nếu miễn climax thì tối thiểu phải giữ một sàn về bề rộng dải và về thanh khoản.

### 3. mSOS gán cho nến CHƯA phá biên chính — luật vi phạm: mục 5.1 (định nghĩa mSOS ở v6)
- **Thuật toán gắn:** mSOS 10:34 tại **4599.1**, VSA 5.11x.
- **Đúng phải là:** biên chính trên là **4600.6** — nến này nằm DƯỚI biên, chưa phá gì cả. Định nghĩa v6 nói rõ mSOS là cú "đã bứt hẳn ra ngoài biên chính nhưng không giữ được". Nến chưa chạm biên thì cùng lắm là UT[B].
- **Nghi phạm:** bước quét hồi tố "cây VSA cao nhất trong đoạn" không kiểm lại điều kiện `close > edge` cho chính cây được chọn.

### 4. Nhãn BCLX? nằm trước nến mở range và dưới biên nó tạo ra — lỗi cụm climax (chưa sửa)
- **Thuật toán gắn:** nhãn ở 07:34, giá **4597.2**; biên chính trên là **4600.6**.
- Trên ảnh nhãn BCLX? treo lơ lửng dưới đường biên liền màu cam — người đọc chart không hiểu cây nào tạo ra biên.

### 5. Cả Phase A chạy trên volume rác — luật vi phạm: mục 2.2 THEORY (Effort vs Result)
- AR gắn cờ "(yếu)" VSA 0.47x, ST[A] VSA **0.30x**, climax 1.59x. Ba mốc dựng nên toàn bộ khung range đều không có nỗ lực nào phía sau.
- Ghi nhận đúng: máy CÓ gắn cờ "(yếu)" cho AR. Nhưng không gắn cho ST[A] và climax dù cùng mức tệ.

### 6. Phase E dài 2 nến — luật vi phạm: L10
- Phase E phải là "giá rời range đi tìm vùng giá mới". Hai nến không mô tả được gì; range đóng ở 13:35 trong khi trên ảnh giá còn dao động mạnh 4615-4634 sau đó.

### 7. LPS[C] ở giữa range — L8
- LPS[C] 11:20 tại 4595.5 = **60% chiều cao** (4588.2-4600.6). Lặp đúng lỗi ở bài #13: bỏ ràng buộc nửa range làm pivot rơi vào giữa.

## Đạt
- **Tên range (L4): ĐẠT về hình thức.** Origin BCLX (dù là giả) + phá lên = Tái tích luỹ, đúng bảng 4 pattern.
- **ST[A] (L2):** hồi 64% khoảng AR↔climax, lọt ngưỡng 0.55 mới — về mặt số thì đúng luật (nhưng 64% của 12.4 giá = 7.9 giá, không có ý nghĩa cấu trúc).
- **Tỉ lệ B dài nhất (L9): ĐẠT** (B = 92 nến).

## Cần hỏi người học
- Range sinh từ cú phá (SIDEWAYS) hiện được **miễn hoàn toàn** L1. Có nên đặt sàn tối thiểu cho nó không — ví dụ bề rộng dải ≥ 0.5× chiều cao range cha, hoặc volume trung bình đoạn ≥ một tỷ lệ nào đó so với TB ngày? Bài này (12.4 giá, 1-7 hợp đồng) là ca cho thấy miễn hết là quá lỏng.
