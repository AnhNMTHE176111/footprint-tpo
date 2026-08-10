# Chấm bài #26 — Tái phân phối (RE-DIST) · 2026-05-27 05:33 → 07:50 (137 nến M1)

**Điểm: 6/10** — Chuỗi nhãn chuẩn, nhưng range quá vụn để gọi là một vùng đấu giá thật; đây là nhiễu được gán đủ 5 phase.

## Lỗi (nặng → nhẹ)

### 1. Range quá vụn — đủ Phase A→E trong 53 nến, biên chính 0.16% giá — luật vi phạm: mục 1 tiêu chí chấm ("khung quá thô / range quá vụn"), THEORY §2.3
- **Thuật toán gắn:** TR hợp lệ, biên chính 4525.6–4532.9 = **7.3 giá (0.16%)**, Phase A 12 + B 23 + C 10 + D 8 = **53 nến** cho toàn bộ cấu trúc; 85 nến còn lại là Phase E (đã ngoài range).
- **Đúng phải là:** không vẽ range ở đây, hoặc đọc lại trên khung lớn hơn. Giảng viên đã nhiều lần yêu cầu đổi khung khi cấu trúc "không ra hình" (Ca #4, #6, #19 nguồn 7.pdf). Tiêu chí đã chốt: TR M1 chỉ 60-100 nến mà đủ A→E thì phải nghi là nhiễu — bài này còn **dưới** ngưỡng đó.
- **Dấu hiệu quyết định trên chart:** biên trên–dưới cách nhau 7.3 giá, trong khi riêng nến climax 05:33 đã có biên độ 5.5 giá. Tức **một cây nến duy nhất chiếm 75% chiều cao cả trading range**. Không có chỗ cho "đàm phán giá" — đó không phải vùng cân bằng, đó là một đoạn rơi bị cắt ngang.
- **Nghi phạm trong thuật toán:** thiếu guard tối thiểu về **chiều cao biên chính so với biên độ nến climax** (đề xuất: yêu cầu biên chính ≥ 2× biên độ nến climax) và guard tối thiểu về **số nến từ climax đến SOS/SOW**.

### 2. Biên phụ trên 4533.9 chỉ hơn biên chính 1.0 giá — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ trên 4533.9, biên chính trên 4532.9 → chênh **1.0 giá = 10 tick**.
- **Đúng phải là:** phía trên không có biên phụ. Một cú vượt biên 10 tick trên vàng M1 là bóng nến, không phải "một thế lực đã cố phá range". Ngưỡng công nhận outside 30 tick mà v7.1 đưa vào cho SOS/SOW **chưa được áp cho việc tạo biên phụ**.
- **Dấu hiệu quyết định trên chart:** hai đường (liền cam 4532.9 và đứt cam 4533.9) gần như dính vào nhau ở đầu chart, không phân biệt được bằng mắt.
- **Nghi phạm:** nhánh dựng biên phụ dùng ngưỡng 0 tick; phải dùng chung hằng số 30 tick với nhánh outside.

### 3. Phase C (10 nến) dài hơn Phase D (8 nến) — luật vi phạm: L8
- Sát ranh giới, nhưng vẫn sai chiều: C phải ngắn nhất. LPSY[C] rơi vào 06:08, còn SOW ở 06:18 — 10 nến ở giữa là đoạn giá trượt dần xuống, thực chất đã là quá trình phá biên chứ không còn là Phase C.
- **Đúng phải là:** kết Phase C ngay sau nến LPSY[C] (06:08-06:10), đẩy phần trượt dốc còn lại sang Phase D.

## Đạt
- **Mục 1 (L1) — phần MOVE:** move giảm 19.4 giá / 44 nến / hiệu suất 0.49, bị nến 05:33 VSA 4.84x chặn đúng tại cực trị. Chuỗi -2/-1/+0 (VSA 2.24x → 4.42x → 4.84x) là một cao trào bán tăng dần rất sạch. Điều kiện CẦN thoả — vấn đề nằm ở kích thước range, không ở move.
- **Mục 2 (L2):** đủ 3 lần đổi hướng. ST[A] 05:44 tại 4523.2 hồi vượt 100% khoảng AR↔climax, VSA 1.01x, thân/biên 0.23 — đúng chất "test lại vùng climax với volume co lại" (THEORY §3.3). Phase A kết thúc đúng tại ST[A].
- **Mục 3 (L3) — biên dưới:** ST[A] xuyên climax → tạo biên phụ dưới 4523.2, đúng luật, mỗi bên 1 biên.
- **Mục 4 (L4):** move giảm + SC + phá **xuống** = Tái phân phối. Đây là ô khó nhất trong bảng 4 pattern và thuật toán đặt đúng — không huỷ range vì "phá sai hướng".
- **Mục 6 (L8) — case khó:** Phase C không có UTAD/Spring, chỉ có LPSY[C], và được gán ngược sau khi thấy SOW. Đúng đúng quy trình L8 case khó.
- **Mục 7 (L10):** SOW 06:18 VSA 4.23x, giá 4520.2 — đóng cửa dưới **cả** biên chính (4525.6) **và** biên phụ (4523.2) → SOW mạnh thật theo L3. LPSY[D] 06:21 tại 4521.7 vẫn **giữ được dưới** biên phụ → retest hợp lệ. Phase E 85 nến đi tìm vùng giá mới xuống 4508. Cụm D+E này là một CBR sách vở.
- **Mục 9:** không có nhãn spam, không lẫn vai LPSY[C]/LPSY[D] (đúng bài học Ca #3 nguồn 4.pdf).
