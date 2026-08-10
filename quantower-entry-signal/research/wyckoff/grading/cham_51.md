# Chấm bài #51 — Tích lũy (ACC) · 2026-07-12 22:48 → 2026-07-13 00:22 (93 nến M1)

**Điểm: 5/10** — bài tốt nhất trong lô: Phase A đúng khuôn, tỉ lệ phase đúng, biên chính ôm đúng vùng giá. Trừ điểm vì mSOS/SOS chồng nhau 1 tick và Phase E chỉ 1 nến rồi cấu trúc sập ngược.

## Lỗi (nặng → nhẹ)

### 1. mSOS và SOS là cùng MỘT cú phá, đặt hai nhãn cách nhau 0.1 giá — luật vi phạm: mục 9 (nhãn sai vai) + L3
- **Thuật toán gắn:** mSOS 23:52 tại **4091.4** (VSA 1.08x, Phase B) — SOS 23:57 tại **4091.5** (VSA 2.79x, Phase D). Cách nhau 5 nến, **0.1 giá**.
- **Đúng phải là:** một cú phá, một nhãn. Cây 23:52 chỉ là nến thò đầu ra; cây phá thật là 23:57. Không có nhịp "thu hẳn vào trong range rồi hướng sang biên đối diện" giữa hai nhãn — tức không thoả định nghĩa mSOS của chính tài liệu.
- **Dấu hiệu quyết định trên chart:** hai nhãn mSOS (cam) và SOS (xanh) dính sát nhau ngay trên biên chính trên 4088.8; giá giữa 23:52 và 23:57 không hề lùi về dưới 4088.8.
- **Nghi phạm:** đúng ca "SOS cách mSOS 1 tick" đã báo ở bài #45 vòng v7 — mSOS tự nới biên phụ lên 4091.4 rồi cú phá thật chỉ cần vượt 0.1 giá là qua. Bản vá 13.1c đổi mốc quyết định sang biên CHÍNH nhưng **nhánh gán nhãn mSOS vẫn chạy trước**, nên vẫn đẻ nhãn thừa.

### 2. Phase E = 1 nến, và cấu trúc sập ngay sau đó — luật vi phạm: L10
- **Thuật toán gắn:** Phase E 00:22 → 00:22 = **1 nến**, range đóng `completed`, tên "Tích luỹ".
- **Đúng phải là:** L10 đòi Phase E là "giá rời range đi tìm vùng giá mới". Trên ảnh, sau đỉnh ~4099 lúc 00:10 giá quay đầu, **thủng cả biên chính dưới 4076.8** xuống ~4070 lúc 00:30. Cấu trúc thất bại (§9 THEORY) chứ không phải tích luỹ hoàn tất.
- **Dấu hiệu quyết định:** khoảng cách từ SOS (4091.5) tới đỉnh thật 4099 = 7.5 giá, chỉ 0.6× chiều cao range 12.0 — vừa đủ mốc "0.5× khi hết giờ" rồi đóng ngay, đúng nghĩa gò cho đủ điều kiện.
- **Nghi phạm:** mốc Phase E tối thiểu 0.5× chiều cao quá rẻ với range 12 giá; và không có kiểm tra hậu nghiệm "giá có lùi lại vào range trong N nến sau khi chốt E hay không".

### 3. AR volume 0.36x mà không gắn cờ "(yếu)" — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** AR 22:52 tại 4088.8, **VSA 0.36x** — thấp hơn 1/3 trung bình.
- **Đúng phải là:** biên chính trên của cả range được dựng bởi một cây gần như không có ai giao dịch. Bài #50 có cờ "AR (yếu)" cho VSA 1.86x, còn ca 0.36x này lại không có cờ — tiêu chuẩn không nhất quán.
- **Nghi phạm:** cờ "(yếu)" đang xét theo *khoảng cách nến tới climax* chứ không theo `ar_vsa` (biến đã đo sẵn nhưng chưa dùng — đúng như 13.1b đã ghi).

### 4. LPS[C] rơi giữa range — luật vi phạm: L8 (Phase C là tín hiệu ở biên)
- LPS[C] 23:45 tại **4083.7**, tức 58% chiều cao range (4076.8–4088.8), không gần biên nào. Sau khi v7.1 bỏ ràng buộc "đúng nửa range", pivot gán ngược trôi vào giữa. Ràng buộc "gần biên đang bị kiểm" rõ ràng chưa siết đủ.

## Đạt
- Điều kiện mở range (L1): MOVE giảm 24.2 giá / 47 nến, climax 22:48 **VSA 7.19x**, biên độ 7.9 giá, là đáy thật của cửa sổ — climax chặn move rõ ràng. Nhãn SC nằm đúng nến mở range (khác #49/#52).
- Phase A (L2) chuẩn: SC → AR (22:52) → ST[A] (23:04 tại 4075.8, hồi hết 108% khoảng AR↔climax, test đúng vùng climax và nới biên phụ dưới xuống 4075.8). Đây là ST[A] đúng nhất trong cả lô — mốc 0.55 mới ăn đúng ở đây.
- Biên chính 12.0 giá / biên phụ 15.6 giá = **1.30×** — hai nét liền ôm đúng vùng dao động, không bị kéo theo giá (L3).
- Tỉ lệ phase đúng: B (39n) dài nhất, C (12n) ngắn nhất trong B/C/D (L8, L9).
- Tên range khớp origin SC + phá lên = Tích luỹ (L4).
