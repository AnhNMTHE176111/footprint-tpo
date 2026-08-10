# Chấm bài #20 — Phân phối (DIST) · 2026-05-21 01:41 → 02:15 (27 nến M1)

**Điểm: 1/10** — không được vẽ range ở đây. 27 nến, Phase A dài **1 nến**, "climax" 2 hợp đồng: đây là nhiễu, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Mở range không có climax và không có MOVE — luật vi phạm: L1
- **Thuật toán gắn:** BCLX? 01:31 tại 4603.8, VSA 1.15×; mức biên trên lấy từ nến 01:41 có **volume = 2 hợp đồng**, VSA **0.29×**, biên độ **0.4 giá**.
- **Đúng phải là:** không mở range. Phiếu số liệu thậm chí không có dòng "MOVE trước climax" — vì range này sinh từ cú phá (SIDEWAYS), tự miễn điều kiện CẦN.
- **Dấu hiệu quyết định trên chart:** 12 nến quanh climax có volume 1–11 hợp đồng, 5 nến biên độ 0.0 giá (nến phẳng). Đây là phiên chết, không có ai đấu giá.
- **Nghi phạm trong thuật toán:** cơ chế `born_from_break` (mục 5.4) cho phép bỏ qua toàn bộ nhóm điều kiện (1) và (2) của mục 3. Phải giữ ít nhất một sàn: dải seed phải có ≥ N nến có giao dịch thật, hoặc buộc seed cũng phải có một cây VSA ≥ 2.2×.

### 2. Phase A = 1 nến, cả CHoCH gói trong 10 nến — luật vi phạm: L2
- **Thuật toán gắn:** A (1n) → B (17n) → D (8n) → E (2n).
- **Đúng phải là:** Phase A là ba lần đổi hướng thật. Ở đây climax 01:31 → AR 01:33 (**2 nến sau**, VSA 0.36×, hồi 6.2 giá) → ST[A] 01:41. Không có lần đổi hướng nào đủ tư cách; dải "Phase A" vẽ ra dài 1 nến là bằng chứng tự thân.

### 3. Biên chính trên lấy từ ST[A] chứ không từ climax — luật vi phạm: L3
- **Thuật toán gắn:** biên chính trên = **4605.4** = giá ST[A]; nhãn BCLX? lại ở 4603.8.
- **Đúng phải là:** biên chính = mức climax + mức AR, chốt tại ST[A] nhưng **không lấy giá ST[A] làm biên**. ST[A] vượt climax thì tạo **biên phụ**, không được ghi đè biên chính.
- **Dấu hiệu quyết định trên chart:** nhãn BCLX? nằm thấp hơn đường "biên CHINH tren 4605.4" — climax nằm *trong* range, chuyện vô lý.

### 4. Thiếu hẳn Phase C — luật vi phạm: L8
- Chuỗi B → D, không có Phase C. Vá v7 #3 (nới cửa sổ lên 0.8× Phase B) không cứu được vì Phase B chỉ 17 nến → cửa sổ 13 nến, lại thêm ràng buộc "pivot phải đúng nửa range" → rỗng. Lỗi lặp v6 **chưa được sửa** ở lớp ca Phase B ngắn.

### 5. Phase E dài 2 nến trong khi giá còn rơi thêm 28 giá — luật vi phạm: L10
- **Thuật toán gắn:** E = 02:14 → 02:15, range đóng `completed`.
- **Đúng phải là:** giá rơi liên tục tới 4564 lúc 03:20 (thêm ~65 nến). Phase E dừng sớm vì chiều cao range chỉ 7.8 giá nên mốc "đi xa 2× chiều cao" chạm ngay lập tức — hệ quả trực tiếp của việc range quá vụn.

## Đạt
- L4: đặt tên đúng theo quy tắc của chính nó (origin BCLX + phá xuống = Phân phối).
- **Vá v7 #1 chạy đúng:** er=0.18 < 1 → ghi "nhịp HIỆU QUẢ", không còn gọi bừa là hấp thụ.
- SOW 02:03 VSA 1.73×, thân 1.00 — nhãn đặt vào nến phá thật.

## Kết luận cấu trúc
Nếu là tôi: **xoá hẳn range này**, trả toàn bộ đoạn 01:15 → 03:20 về cho range #19 và đọc nó là **UTAD → Phase D/E của một cấu trúc Phân phối**. Một cú phá lên giữ được 45 nến rồi xuyên ngược cả range chính là định nghĩa upthrust, không phải cớ để đẻ range con.
