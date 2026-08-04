# Chấm bài #34 — Tái phân phối (RE-DIST) · 2026-06-30 00:09 → 00:56 (47 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây. 47 nến, biên chính 10.4 giá, đủ 5 phase, phase dài nhất là B với 12 nến: đây là một chỗ nghỉ chân giữa đợt giảm, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range 47 nến / 5 phase — vụn nhất cả lô — luật vi phạm: mục "range quá vụn" trong CHART_CASES + L9
- **Thuật toán gắn:** A(10) → B(12) → C(11) → D(9) → E(6) trong **47 nến**, biên chính **10.4 giá = 0.26%**.
- **Đúng phải là:** không vẽ. Năm phase Wyckoff nhồi vào 47 nến M1 (47 phút) thì mỗi phase trung bình 9 nến. Phase B — nơi "xây dựng nguyên nhân" cho cả xu hướng sau đó — dài **12 nến**, chỉ hơn Phase C (11 nến) đúng 1 nến. Nhân-Quả (THEORY §2.2): nguyên nhân 12 phút không sinh ra được kết quả nào đáng gọi tên.
- **Dấu hiệu quyết định trên chart:** A=10, B=12, C=11, D=9, E=6 — năm phase gần như **bằng nhau**. Khi cả 5 phase đều dài như nhau thì việc chia phase không mang thông tin gì; nó chỉ là chia đều một đoạn 47 nến thành 5 khúc.
- **Nghi phạm trong thuật toán:** như bài #32 — không có ràng buộc **tỉ lệ** giữa các phase. L8 (C ngắn nhất) và L9 (B dài nhất) hiện chỉ là mô tả trong tài liệu, chưa thành điều kiện chặn trong code. Đề nghị chặn: Phase B ≥ 2× Phase C và Phase B ≥ Phase A, nếu không thoả thì không đóng range có tên.

### 2. Climax nằm GIỮA move, không chặn được move — luật vi phạm: L1 + lỗi A
- **Thuật toán gắn:** SC tại 00:09, giá 4017.1, VSA 2.66×; MOVE giảm 16.3 giá / 50 nến / hiệu suất 0.39.
- **Đúng phải là:** climax phải là **cực trị chặn move**. Nhưng nhìn ảnh: sau range, giá tiếp tục rơi thẳng xuống **3958** — thấp hơn "SC" tới **59 giá**, gấp gần 6 lần chiều cao biên chính. SC 4017.1 chỉ là một chỗ ngừng giữa một đợt giảm dài đang chạy. Đúng như lỗi A đã mô tả: "giá còn vượt mức climax quá 3× biên độ TB → climax không chặn được move, bỏ range". Guard đó **đã không bắn** ở đây.
- **Dấu hiệu quyết định trên chart:** trục giá bên phải — range nằm ở 4017-4027, đáy chart là 3950.5, và giá thật sự đi tới ~3958. Cây "climax" nằm ở **1/3 trên** của cả đoạn giảm hiển thị trên ảnh.
- **Nghi phạm trong thuật toán:** guard "vượt mức climax quá 3× biên độ TB" ở mục 4.0 chỉ chạy trong **cửa sổ cụm 8 nến** đầu. Sau khi Phase A chốt, giá vượt climax bao xa cũng không bị kiểm lại. Guard này phải chạy suốt vòng đời range, không chỉ 8 nến đầu.

### 3. Climax không phải cây nỗ lực lớn nhất trong cụm — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** SC tại 00:09 với VSA 2.66×.
- **Đúng phải là:** đọc 6 nến trước: nến −3 (00:06) có **VSA 4.47×** — cao hơn hẳn cây được gán nhãn; nến −6 có 3.13×, nến −2 có 2.67×, nến −1 có 2.34×. Cả 6 nến trước climax đều đã ở mức climax hoặc cao hơn. "Cụm cao trào" ở đây bắt đầu từ 00:03, và cây nỗ lực đỉnh là 00:06, không phải 00:09.
- **Dấu hiệu quyết định trên chart:** 4.47× > 2.66×. Máy chọn cây có giá thấp hơn thay vì cây có nỗ lực lớn hơn.
- **Nghi phạm trong thuật toán:** mục 4.0 dời mốc climax theo **cực trị giá**, không theo VSA. Khi giá còn đang rơi đều thì mốc luôn trượt tới cây cuối cụm. Nên chọn mốc bằng cực trị giá **nhưng chỉ trong các nến VSA ≥ ngưỡng**, và ưu tiên cây VSA đỉnh khi hai tiêu chí lệch nhau.

### 4. Phase E dài 6 nến — luật vi phạm: L10 + lỗi J
- **Thuật toán gắn:** Phase E từ 00:51 đến 00:56 = **6 nến**, rồi range đóng "completed".
- **Đúng phải là:** Phase E là "giá rời TR đi tìm vùng giá mới". Sáu nến M1 chưa đi tìm được gì. Trên ảnh, cú rơi thật sự (cây đỏ khổng lồ với thanh volume vàng cao nhất chart) xảy ra ở **~01:02-01:04**, tức **sau khi range đã đóng**. Máy đóng range ngay trước lúc cái mà nó đang dự đoán thực sự xảy ra.
- **Dấu hiệu quyết định trên chart:** thanh volume cao nhất toàn chart nằm ở ~01:02, ngoài phạm vi range. Phase E chỉ 6 nến vì đích Phase E = 1.0 × chiều cao biên chính = chỉ **10.4 giá**.
- **Nghi phạm trong thuật toán:** đích Phase E đo bằng chiều cao range (mục 7). Range vụn → đích thấp → Phase E đạt tức thì. Cùng một nghi phạm với bài #32 lỗi #5; range càng vụn thì càng dễ "hoàn tất".

### 5. LPSY[C] nằm trên biên chính dưới, VSA 2.25× thân 1.00 — sai vai — luật vi phạm: L7 + THEORY §4.1
- **Thuật toán gắn:** LPSY[C] tại 00:31, giá **4019.0**, VSA 2.25×, thân **1.00**.
- **Đúng phải là:** LPSY theo định nghĩa gốc là "một đợt **phục hồi yếu** trên biên hẹp → nguồn cầu cạn kiệt". Cây này có thân 1.00 (nến toàn thân, không râu) và VSA 2.25× — tức là một cây **mạnh**, không phải phục hồi yếu. Với volume 2.25× và thân đầy như vậy, đúng vai của nó là **mSOW** (cú phá thất bại) hoặc chính là cây khởi phát cú phá.
- **Dấu hiệu quyết định trên chart:** thân/biên độ = 1.00 là giá trị tối đa — nến không có bóng nào. Đối lập hoàn toàn với "biên hẹp, cầu cạn kiệt".
- **Nghi phạm trong thuật toán:** nhánh "Phase C gán ngược" (mục 6) lấy **cực trị** trong 60 nến trước cú phá làm LPSY[C], không kiểm tính chất nến. Cần thêm điều kiện: nhịp test làm LPS/LPSY phải có volume **co lại** (VSA thấp), đúng theo định nghĩa test — nếu cực trị tìm được lại là cây VSA cao thì đó là cú phá, không phải test.

## Đạt
- Biên chính = climax 4017.1 + AR 4027.5, cố định, không kéo theo giá. Đúng L3.
- Biên phụ 1 cái ở dưới (4016.1), không spam. Đúng L3.
- SOW neo đúng cây: VSA **2.48×**, thân 0.69 — nỗ lực trên trung bình, đúng hướng. Lỗi B không tái xuất ở bài này.
- Tên "Tái phân phối" khớp L4 về logic đặt tên: origin SC + phá xuống. (Vấn đề không phải tên, mà là có nên vẽ range hay không.)
- Phase C 11 nến ngắn hơn Phase B 12 nến — đúng thứ tự L8, dù khoảng cách chỉ 1 nến nên gần như vô nghĩa.

## Kết luận cấu trúc
Nếu là tôi: **không vẽ range ở đây**. Đây là ca kinh điển "climax nằm giữa move": giá đang rơi, ngừng 47 phút trong một khoảng 10 giá, rồi rơi tiếp 59 giá nữa. Muốn đọc chỗ này thì phải **lên khung lớn hơn** — trên M5/M15 cả đoạn này chỉ là 3-4 cây nến trong một chân giảm, và range thật (nếu có) phải là cái range 833 nến ở bài #35 ngay sau đó. Cứ vẽ range M1 cho mọi chỗ giá ngừng 40 phút thì sẽ ra hàng trăm range mà không cái nào là vùng đấu giá thật.
