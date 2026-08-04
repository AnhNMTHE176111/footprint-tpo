# Chấm bài #32 — Phân phối (DIST) · 2026-06-21 23:10 → 06-22 00:11 (61 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây. Range 61 nến, biên chính 11.1 giá, đủ 5 phase với Phase B dài 5 nến: đây là nhiễu, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range 61 nến / 5 phase — nhiễu chứ không phải vùng đấu giá — luật vi phạm: mục "khung quá thô / range quá vụn" trong CHART_CASES
- **Thuật toán gắn:** đủ A(15) → B(5) → C(5) → D(18) → E(19) trong 61 nến M1, biên chính chỉ **11.1 giá = 0.27%**.
- **Đúng phải là:** không vẽ. Chuẩn chấm đã chốt: một TR M1 chỉ 60-100 nến với đủ Phase A→E thì phải nghi ngay đó là nhiễu. Ở đây còn tệ hơn — **Phase B dài đúng 5 nến**. Phase B là nơi "xây dựng nguyên nhân" (THEORY §4.2), là phase dài nhất (L9). Năm nến M1 không xây được nguyên nhân gì cả.
- **Dấu hiệu quyết định trên chart:** B(5n) = C(5n). Phase dài nhất bằng đúng phase ngắn nhất → hai luật tỉ lệ phase (L8, L9) cùng bị phủ định trong một bài.
- **Nghi phạm trong thuật toán:** quyết định #1 của người học ở v5 — "**không** đặt sàn độ dài tối thiểu cho range" — cộng với việc không có sàn cho **riêng Phase B**. Đề nghị: không cần sàn cho cả range, nhưng phải có ràng buộc **tương đối**: Phase B ≥ Phase A và Phase B ≥ Phase C+D. Ràng buộc tỉ lệ này chính là L8/L9 viết thành code, không phải một hằng số tự đặt.

### 2. Phase B (5 nến) ngắn hơn Phase A (15 nến) và bằng Phase C — luật vi phạm: L9 + L8
- **Thuật toán gắn:** A=15, B=5, C=5, D=18, E=19. Phase **dài nhất là E (19 nến)**, phase B đứng chót cùng C.
- **Đúng phải là:** thứ tự phải là B dài nhất, C ngắn nhất. Ở đây thứ tự thực tế là E > D > A > B = C.
- **Dấu hiệu quyết định trên chart:** đọc thẳng bảng phase trong phiếu số liệu.
- **Nghi phạm trong thuật toán:** máy chốt Phase A tại ST[A] rồi lập tức bắt cú thò biên đầu tiên làm Phase C. Không có bộ lọc nào hỏi "Phase B đã đủ dài để gọi là xây nguyên nhân chưa".

### 3. MOVE trước climax bắc qua khe cuối tuần — luật vi phạm: L1 + lỗi K (đã tuyên bố vá ở v5)
- **Thuật toán gắn:** MOVE dài 24.6 giá, **70 nến**, hiệu suất 0.39, chân move vẽ từ **06-19 16:5x**.
- **Đúng phải là:** nhìn trục thời gian trên ảnh: nhãn "chan MOVE" neo ở vùng 06-19 16:35-16:51, rồi trục nhảy thẳng sang **06-21 22:07**. Đó là khe **hơn 2 ngày lịch** (cuối tuần). Đường xám nối chân move đi xuyên qua khe này. Lỗi K nói "khe > 4 giờ thì cắt range" — nhưng luật đó chỉ áp cho thân range, **không áp cho cửa sổ đo MOVE**.
- **Dấu hiệu quyết định trên chart:** 70 nến M1 mà trải từ 06-19 tới 06-21 = khe ~53 giờ. "MOVE tăng 24.6 giá" này thực chất là hai đoạn khác phiên bị dán lại; hiệu suất hướng 0.39 tính trên chuỗi dán đó là con số vô nghĩa.
- **Nghi phạm trong thuật toán:** hàm đo MOVE (mục 1, cửa sổ nhìn lại 240 nến) đếm bằng **số nến**, chưa áp bộ lọc khe thời gian của lỗi K. Phải áp cùng một guard 4 giờ cho cả cửa sổ MOVE.

### 4. Climax không phải cực trị của cửa sổ move — luật vi phạm: L1 + lỗi A
- **Thuật toán gắn:** BCLX tại 23:10, giá 4181.5, VSA 2.69×.
- **Đúng phải là:** climax phải **chặn** move. Nhưng đọc 6 nến trước climax: nến −6 (23:04) có **VSA 4.48×** và nến −2 (23:08) có **VSA 3.80×** — cả hai đều cao hơn hẳn cây được gọi là climax (2.69×). Cây "climax" chỉ là cây cuối của một cụm đã nổ volume từ 6 phút trước.
- **Dấu hiệu quyết định trên chart:** VSA 4.48× > 3.80× > 2.69×. Cây có nỗ lực lớn nhất không phải cây được gán nhãn.
- **Nghi phạm trong thuật toán:** cửa sổ "cụm climax" 8 nến (mục 4.0) chỉ dời mốc khi có **cực trị GIÁ mới cùng phía**, không xét volume. Ở đây giá vẫn leo đều nên mốc bị đẩy tới cây cuối cụm, bỏ lại cây nỗ lực thật phía sau.

### 5. Phase E "hoàn tất" trong khi giá bắn ngược lên phá đỉnh range — luật vi phạm: L10
- **Thuật toán gắn:** Phase E 19 nến (23:53 → 00:11), range **completed**, tên **Phân phối**.
- **Đúng phải là:** trên ảnh, ngay sau khi range đóng giá **dựng đứng từ ~4157 lên 4213** — vượt qua cả biên trên 4181.5 và đi tiếp rất xa. Đây là một cấu trúc **thất bại** theo THEORY §9 ("tích luỹ thất bại sẽ luôn là một cấu trúc phân phối và ngược lại"). Gọi nó là "Phân phối hoàn tất" là kết luận ngược hẳn với cái xảy ra ngay sau đó.
- **Dấu hiệu quyết định trên chart:** SOW ở 4159.8, LPSY[D] ở 4156.7, rồi giá đóng ở 4213 — cao hơn **cả BCLX**. Toàn bộ cú giảm bị phủ định trong vòng chưa tới một giờ.
- **Nghi phạm trong thuật toán:** đích Phase E = "đi thêm 1.0 × chiều cao biên chính". Chiều cao đây chỉ **11.1 giá**, nên chỉ cần rơi thêm 11 giá là đạt Phase E. Ngưỡng đo bằng chiều cao range khiến **range càng vụn thì càng dễ đạt Phase E** — đúng ngược với mong muốn. Nên chặn bằng sàn tuyệt đối theo biên độ TB, hoặc bằng chính ràng buộc tỉ lệ phase ở lỗi #1.

## Đạt
- Biên chính = climax 4181.5 + AR 4170.4, cố định, không kéo theo giá. Đúng L3.
- Biên phụ 1 cái (4170.3), gần trùng biên chính — trung thực, không thổi phồng.
- SOW neo đúng cây: VSA **2.92×**, thân 0.75 — đây là lỗi B đã được vá thật, khác hẳn bài #31.
- LPSY[C] và LPSY[D] mỗi cái đúng 1 điểm, đúng vai trước/sau SOW. Đúng L7.
- Tên "Phân phối" khớp origin BCLX + phá xuống. Đúng L4 về mặt logic đặt tên.

## Kết luận cấu trúc
Nếu là tôi: **không vẽ range ở đây**. 61 nến, 11 giá chiều cao, Phase B 5 nến, MOVE đo xuyên khe cuối tuần, và giá phủ định toàn bộ cấu trúc ngay sau khi range đóng. Đây đúng là ca "gượng ép" mà giảng viên đã chê ở Ca #20 nguồn 7.pdf — cố nhét đủ 5 nhãn vào một đoạn không có gì.
