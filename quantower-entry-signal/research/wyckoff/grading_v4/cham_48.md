# Chấm bài #48 — Tái tích luỹ (RE-ACC) · 2026-07-24 13:58 → 15:47 (109 nến M1)

**Điểm: 6/10** — Bài tốt nhất trong lô: cấu trúc thật, tên range đúng, retest Phase D đúng vị trí. Cần **sửa 3 nhãn**: mức climax không phải đỉnh, ST[A] gắn muộn nên Phase A ăn lấn Phase B, và nhãn SOS gắn sau khi giá đã đi hết đà.

## Lỗi (nặng → nhẹ)

### 1. Mức climax không phải cực trị — biên chính trên nằm GIỮA vùng đấu giá — luật vi phạm: mục 1 + L3
- **Thuật toán gắn:** BCLX @4069.7 (13:58) → biên chính trên = 4069.7.
- **Đúng phải là:** đỉnh thật của move là **4073.0 lúc 14:00**, tức **2 nến SAU** cây climax (bảng 12 nến: +1 H=4071.5, +2 H=4073.0). Cây climax vì thế **không chặn** move — move còn chạy thêm 3.3 giá. Biên trên đúng phải là 4073.0, và khi đó biên phụ trên biến mất (đúng L3: có thể không có biên phụ nào).
- **Dấu hiệu quyết định trên chart:** đường liền cam 4069.7 bị nến **xuyên qua nhiều lần trong Phase B** (cụm 14:05 và 14:23 đều vượt lên trên nó). Một mức bị xuyên đi xuyên lại trong Phase B thì không phải biên chính; nó là mức giữa range.
- **Nghi phạm trong thuật toán:** mục 3(2) chỉ kiểm "nến climax là cực trị của **cửa sổ 240 nến nhìn lại**" — hoàn toàn nhìn **về sau**, không kiểm vài nến **phía trước**. Cần thêm điều kiện: sau climax N nến (vd 3–5) không được có cực trị mới xa hơn, nếu có thì dời mức climax tới đó.

### 2. Nhãn SOS gắn muộn, rơi vào nến VSA 0.38x sau khi đà đã hết — luật vi phạm: mục 8 (Effort vs Result), THEORY §3.3
- **Thuật toán gắn:** SOS @4077.6 lúc 15:22, **VSA 0.38x**.
- **Đúng phải là:** nỗ lực thật nằm ở **15:17–15:20** — cụm thanh vàng cao nhất của cả chart trên panel khối lượng. Nhãn SOS phải nằm ở cây phá đầu tiên trong cụm đó, không phải cây xác nhận sau.
- **Dấu hiệu quyết định trên chart:** đỉnh xung lực (~4086) xảy ra **trước** chấm SOS; tới lúc nhãn SOS được đóng dấu, giá đã đi hết 16 giá kể từ biên. Volume tại nhãn chỉ bằng 38% trung bình 20 nến, trái thẳng với định nghĩa SOS ("spread + volume tăng đều"). Lưu ý phân xử: THEORY §6.3 / WY08 cho phép breakout volume thấp là hợp lệ — nhưng đây **không** phải ca đó, vì nỗ lực lớn có thật, chỉ là nhãn đặt lệch chỗ.
- **Nghi phạm trong thuật toán:** mục 5.1 kết cục B — code yêu cầu 3 nến liên tiếp đóng cửa vượt biên phụ rồi mới **gắn nhãn tại nến thứ 3**. Sửa: giữ nguyên điều kiện xác nhận 3 nến, nhưng **hồi tố nhãn về nến phá đầu tiên**. Lỗi này lặp ở cả #46 (SOW 0.37x) và #47 → lỗi hệ thống.

### 3. Phase B (25 nến) ngắn hơn Phase A (44 nến) — luật vi phạm: L9, hệ quả của ST[A] gắn muộn (L2)
- **Thuật toán gắn:** A = 44 nến, B = 25 nến, C = 15, D = 25, E = 1. ST[A] @4065.4 lúc 14:41.
- **Đúng phải là:** L9 nói Phase B là phase **dài nhất** — ở đây B thậm chí chỉ **ngang Phase D**. Nguyên nhân: lần đổi hướng thứ 3 của CHoCH (L2) là **đỉnh 14:23 (~4071.5)** — cú quay về phía climax, **vượt qua** biên chính 4069.7 rồi bị chặn. Đó là ST[A]. Nhãn thật lại rơi vào 14:41 @4065.4, tức 18 nến muộn hơn và ở **62% chiều cao range** — đúng cái "ngọ nguậy giữa range" mà L2 cấm. Dời ST[A] về 14:23 thì A ≈ 26 nến, B ≈ 43 nến, trật tự độ dài phase trở lại đúng L9.
- **Dấu hiệu quyết định trên chart:** cụm nến 14:23 đội lên trên đường liền cam 4069.7 rồi bị bán xuống ngay; sau nó có đủ 5 nến không tạo đỉnh mới (điều kiện đổi hướng của mục 4.2 đã thoả tại đó).
- **Nghi phạm trong thuật toán:** mục 4.2 — bước "hồi ≥ 40% chiều cao climax↔AR rồi 5 nến không cực trị mới" có vẻ đang chờ **cực trị mới nhất** thay vì **cực trị đầu tiên thoả điều kiện**, nên bỏ qua đỉnh 14:23.

### 4. Phase E không có nội dung thật — luật vi phạm: L10 (nhẹ, ghi nhận)
- **Thuật toán gắn:** Phase E = 1 nến tại 15:47, đóng range.
- **Thực tế trên chart:** sau 15:47 giá **không rời đi tìm vùng giá mới**, nó lình xình 4074–4082 tới 16:29 rồi tụt về 4073, tức quay lại đúng biên phụ vừa phá. Đích Phase E được tính đạt nhờ cú xung lực **trước đó** (mục 7: đi thêm 1.0 × chiều cao range = 11.3 giá), nên nhãn hợp spec nhưng không mô tả đúng hành vi. Đây là lỗi cách đo, không phải lỗi cấu trúc nặng.

## Đạt
- **L1 thoả thật:** MOVE tăng 22.8 giá / 40 nến, hiệu suất 0.40, đọc rõ trên chart (từ ~4047 lúc 13:11 lên đỉnh 13:58–14:00). Cây climax là nến xanh thân 0.86, biên độ 7.7 giá, 703 lot so với TB ~166 (VSA 4.24x) — đúng một cây BCLX thật, không phải râu.
- **AR là cú bật ngược thật:** 4058.4, cách climax 11.3 giá = **50% độ dài move**, thoải mái vượt ngưỡng 30%.
- **L4 đúng:** origin BCLX + phá lên thật = Tái tích luỹ; bối cảnh (giá đi từ 4047 lên, nghỉ trong hộp 11 giá, rồi bung lên 4086) đúng là chỗ nghỉ giữa đợt tăng.
- **L10 đúng phần retest:** LPS[D] @4073.5 nằm **ngay trên biên phụ 4073.0** — nhịp hồi giữ được ở ngoài biên vừa phá. Đây là nhãn đẹp nhất của cả lô 4 bài.
- **L7 + L8 đúng:** LPS[C] và LPS[D] mỗi cái 1 điểm; Phase C (15 nến) ngắn nhất trong A/B/C.
- Effort↔result hậu thuẫn tên range: hai cụm volume lớn nhất chart nằm ở cây BCLX (13:58–14:01) và ở cú phá lên (15:17–15:20), còn giữa range volume co lại — đúng khuôn hấp thụ rồi bung.
