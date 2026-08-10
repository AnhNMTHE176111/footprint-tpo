# Chấm bài #41 — Tái phân phối (RE-DIST) · 2026-06-30 00:09 → 00:56 (47 nến M1)

**Điểm: 2/10** — **Không nên vẽ range ở đây.** 47 nến M1 nhét đủ Phase A→E, biên chính 10.4 giá: đây là một nhịp pullback giữa đợt rơi, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range 47 nến với đủ 5 phase = nhiễu, không phải TR — luật vi phạm: L1 + THEORY §2.3 (giai đoạn đi ngang) + §2.2 (Nhân–Quả)
- **Thuật toán gắn:** A=10 · B=6 · C=12 · D=14 · E=6, tổng 47 nến, biên chính 10.4 giá (0.26%).
- **Đúng phải là:** không mở range. "Phạm vi giao dịch là nơi chuyển động trước đã bị dừng lại và có **cân bằng tương đối** giữa cung và cầu" — ở đây không có gì dừng lại cả.
- **Dấu hiệu quyết định trên chart:** trên ảnh, đoạn 00:09–00:56 là một cái gợn 10 giá nằm giữa một đợt rơi liên tục từ **4035 (23:12) xuống 3955 (01:05)**. Nhân nhỏ (47 nến) không thể là nguyên nhân cho kết quả 60 giá — cú rơi đó có nguyên nhân ở nơi khác, không phải ở đây.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range". Quyết định đó đang đẻ ra loại range này. Nếu không muốn đặt sàn số nến thì phải đặt sàn **quan hệ**: chiều cao range so với độ dài move sau đó, hoặc số nến so với số nến của MOVE (ở đây MOVE 50 nến > cả range 47 nến).

### 2. Phase A gói trong 10 nến, AR cách climax đúng 3 nến — luật vi phạm: L2
- **Thuật toán gắn:** SC 00:09 → AR 00:12 → ST[A] 00:18.
- **Đúng phải là:** một CHoCH cần 3 lần đổi hướng có sức nặng. 3 nến M1 giữa climax và AR là mức mà chính tài liệu thuật toán gọi là "**AR (yếu)** — nhiều khả năng chỉ là râu nhiễu"; ở đây nó vẫn được dùng làm biên chính trên.
- **Dấu hiệu quyết định trên chart:** AR @ 4027.5, VSA 2.55x, nhịp bật chỉ 10.4 giá — nhỏ hơn **chính một nến climax của bài #42 cùng ngày** (biên độ 25.6 giá).

### 3. Phase C (12 nến) DÀI HƠN Phase B (6 nến) — luật vi phạm: L8 + L9
- **Thuật toán gắn:** B = 00:19 → 00:24 (6 nến), C = 00:25 → 00:36 (12 nến).
- **Đúng phải là:** C ngắn nhất, B dài nhất. Ở đây C gấp đôi B.
- **Nghi phạm trong thuật toán:** v7.1 bỏ ràng buộc "pivot đúng nửa range" cho Phase C gán ngược nhưng **không thêm trần tuyệt đối** `len(C) ≤ min(len(B), len(D))` — đúng khuyến nghị đã ghi ở 13.1b mà chưa làm.

### 4. LPSY[C] nằm giữa range, không phải test biên — luật vi phạm: L8
- **Thuật toán gắn:** LPSY[C] @ 00:25, giá 4022.6.
- **Đúng phải là:** LPSY[C] là cú phục hồi yếu **lên biên trên** (nơi cầu cạn) ngay trước khi phá xuống. 4022.6 nằm ở **53% chiều cao range** (5.5 / 10.4) — chính giữa, không đọc được vai gì.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của việc bỏ `_right_half` mà không thay bằng ràng buộc "gần biên đang bị kiểm" đủ chặt.

### 5. Biên phụ dưới chỉ cách biên chính 1.0 giá — luật vi phạm: L3 (tinh thần)
- Biên phụ 4016.1 vs biên chính 4017.1. Một đường nét đứt cách nét liền 10 tick không nói lên "có thế lực đã cố phá range". Nên không vẽ biên phụ ở ca này. (Lỗi trình bày kèm khái niệm.)

### 6. Nhãn SC nằm trước nến mở range 3 nến — L3 (ghi nhận, đã biết chưa sửa)
- SC @ 00:06 giá 4018.2 vs range mở 00:09 @ 4017.1.

### 7. Phase E cắt sau 6 nến trong khi giá còn rơi thêm 50 giá — L10
- Range đóng lúc 00:56 @ ~4007; trên ảnh giá rơi tiếp tới **3955 lúc 01:05**. Phase E lẽ ra bao trọn đoạn đó.

## Đạt
- L2 phần vị trí: **ST[A] @ 4018.3 chỉ cách climax 1.2 giá** — đúng là test lại vùng climax. Ngưỡng 0.55 mới ăn đúng ở ca này.
- L4: RE-DIST đúng tên theo origin SC + phá xuống.
- SOW @ 00:37 VSA **6.90x** thân 0.55, dưới biên chính 7 giá — cây phá đọc đúng.
- LPS Y[D] @ 00:46 VSA 0.42x giữ dưới biên — đúng mẫu CBR của L10.

## Kết luận cấu trúc
Tôi **không vẽ range ở đây**. Đoạn này nên để trống, hoặc gộp vào phần đầu của cấu trúc lớn hơn kết thúc bằng cây SC 7.11x lúc 01:07 (bài #42). Vẽ một TR 47 nến rồi tuyên bố đủ A→E là gò dữ liệu cho khớp mô hình — đúng lỗi Ca #20 nguồn 7.pdf.
