# Chấm bài #54 — Chưa rõ (BCLX) (DIST?) · 2026-07-24 14:00 → 20:59 (419 nến M1)

**Điểm: 5/10** — Phase A là bài mẫu của cả lô: climax đúng cây, AR thật, ST[A] về sát climax. Nhưng máy bỏ sót hẳn nửa sau: một cú UTAD ở 4085.2 và một cú SOW giữ được dưới biên suốt hơn 2 giờ, mà range vẫn đóng ở "chưa rõ".

## Lỗi (nặng → nhẹ)

### 1. Không công nhận SOW dù giá giữ dưới biên chính hơn 160 nến — luật vi phạm: L10 (+ vòng lặp biên phụ)
- **Thuật toán gắn:** mSOW 19:25 tại 4051.3, Phase B kéo tới hết range, tên range "Chưa rõ (BCLX) (DIST?)".
- **Đúng phải là:** từ khoảng 18:15 tới 20:59 giá **nằm hẳn dưới** biên chính dưới 4058.4 và không lấy lại được — đó là Phase D (SOW + nhịp hồi thất bại ở 4058-4060) rồi Phase E. Range phải được đặt tên **Phân phối (DIST)** theo L4 (origin BCLX + phá thật xuống).
- **Dấu hiệu quyết định trên chart:** đường nét liền 4058.4 nằm hẳn **phía trên** toàn bộ dải nến từ 18:15 tới cuối; nhịp hồi 19:29 chạm đúng 4058-4060 rồi rơi lại = LPSY[D] kinh điển.
- **Nghi phạm trong thuật toán:** SOW đòi đóng cửa vượt **biên phụ dưới** 4051.3 — mà 4051.3 do **chính nhịp xuống đó** nới ra. Đây đúng là "biên phụ tự nới rồi tự vượt"; nới ngưỡng 10 → 30 tick (fix #6) không phá được vòng lặp, vì vấn đề là **thứ tự**: biên phụ được nới trước khi kết luận cú phá. Phải chốt biên phụ tại mức có **trước** nhịp đang xét, hoặc dùng biên chính làm mốc kết luận (đúng tinh thần fix #3 của v6) và chỉ dùng biên phụ để xếp hạng "mạnh/không mạnh".

### 2. Thiếu Phase C dù có cú upthrust rõ — luật vi phạm: L8
- **Thuật toán gắn:** mSOS 15:20 tại 4085.2 (VSA 1.56x, thân 0.80), Phase B.
- **Đúng phải là:** đây là cú test **cuối cùng** phá đỉnh range trước khi cấu trúc sụp → **UTAD**, và là Phase C. Sau nó không còn đỉnh nào cao hơn; cấu trúc đi xuống một mạch. Đúng tiêu chí phân biệt UT vs UTAD ở Ca #1/#4 nguồn 4.pdf: nếu sau đỉnh vẫn còn hồi giữ được trên đỉnh cũ → UT; ở đây không có.
- **Dấu hiệu quyết định trên chart:** 4085.2 là **cực trị trên cao nhất** toàn range (chính nó là biên phụ trên), kèm cụm khối lượng cao nhất cả chart ở 15:05; sau đó các đỉnh thấp dần và giá không bao giờ trở lại 4085.

### 3. SOT phía trên báo `none` trong khi chart có 3 nhịp rút ngắn liên tiếp — luật vi phạm: §7 THEORY (SOT)
- **Thuật toán gắn:** `SOT-up = none (n=0)`.
- **Đúng phải là:** chuỗi đỉnh 4085.2 (15:20) → ~4083 (15:49) → ~4079 (16:20) → 4073.0 (17:17) là 3 lần đẩy ngắn dần liên tiếp, đúng điều kiện tối thiểu ≥3 lần đẩy. Đây là dấu hiệu cung áp đảo mà máy bỏ qua đúng lúc nó cần nhất (để dám gọi Phase D).
- **Nghi phạm trong thuật toán:** định nghĩa "nhịp" (swing) trong bộ đếm SOT quá thô — với các đỉnh chỉ chênh 2-6 giá trên M1, pivot detector 5 nến nhiều khả năng không tách được nhịp.

### 4. (Trình bày) Không có dòng nỗ lực ↔ kết quả
- Phase B 393 nến mà phiếu không in dòng er nào → mục 8 không có số để đối chiếu. Giống #51 và #55: dòng này chỉ xuất hiện khi range có Phase C.

## Đạt
- **Mục 1 (L1):** MOVE tăng 24.6 giá / 42 nến bị chặn ngay tại 14:00; cụm climax 13:58 (4.24x) – 13:59 (2.32x) – 14:00 (3.09x).
- **Nhãn cụm climax (fix #4):** BCLX neo **đúng nến mở range** 14:00, đúng đỉnh 4073.0 = đúng mức biên chính trên. Đây là ca chứng minh fix #4 chạy được — đối lập hẳn với #53 và #55.
- **Mục 2 (L2):** đủ 3 lần đổi hướng. AR 4058.4 là cú bật thật 14.6 giá. **ST[A] 4072.3 = hồi 95%** khoảng AR↔climax, tức test đúng vùng climax — chuẩn mực cho các bài khác.
- **Mục 3 (L3):** biên chính = climax + AR, cố định; biên phụ mỗi bên đúng 1 (4051.3 / 4085.2), đều là cực trị thật.
- **Fix #5 (mốc mSOS/mSOW):** cả mSOS 4085.2 lẫn mSOW 4051.3 đều neo **đúng cực trị** của nhịp — bài này fix #5 chạy đúng.
