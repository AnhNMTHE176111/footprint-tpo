# Chấm bài #41 — Phân phối (DIST) · 2026-07-15 18:31 → 2026-07-16 03:54 (503 nến M1)

**Điểm: 6/10** — Khung range đọc được, đúng tên, đúng tỉ lệ phase; nhưng SOW neo sai cây và Phase C/D nằm ở chỗ giá đã rơi khỏi range từ lâu.

## Lỗi (nặng → nhẹ)

### 1. SOW neo sai cây — luật vi phạm: L10 / mục 5.1 "nhãn hồi tố vào cây phá thật" (lỗi B của vòng v4, CHƯA hết)
- **Thuật toán gắn:** SOW tại 01:29, giá 4042.7, **VSA = 0.94×**, thân 0.50.
- **Đúng phải là:** cây phá thật là nhịp sụp bắt đầu ngay sau 00:47 — trên panel volume có cụm thanh vàng (VSA ≥ 2.2×) đúng lúc giá xuyên biên chính dưới 4064.4 rồi xuyên tiếp biên phụ 4055.2. SOW phải nằm ở cây đó, không phải ở cây 0.94× thấp hơn TB.
- **Dấu hiệu quyết định trên chart:** giá tại nhãn SOW là 4042.7 — **thấp hơn biên phụ 4055.2 tới 12.5 giá**. Một SOW đúng nghĩa là cây *phá* biên, không phải cây đã ở sâu 12 giá bên ngoài. Ngược lại cây LPSY[D] lại có VSA 2.88× — nỗ lực lớn nhất của cả đoạn D lại bị gán vai "hồi test".
- **Nghi phạm trong thuật toán:** vá lỗi B mới chỉ chọn "VSA cao nhất trong đoạn xác nhận", nhưng cửa sổ hồi tố hình như chỉ tính từ nến vượt **biên phụ** trở đi, nên bỏ mất cây phá **biên chính** đứng trước. Cần mở cửa sổ hồi tố về tới nến đầu tiên đóng cửa dưới biên chính.

### 2. Phase C 7 nến gán ngược quá muộn, LPSY[C] nằm ngoài range — luật vi phạm: L8
- **Thuật toán gắn:** LPSY[C] tại 01:22, giá **4049.9**; Phase C = 7 nến, ngay sát SOW.
- **Đúng phải là:** LPSY[C] là **cú test cuối trước khi cấu trúc sụp**, phải nằm **trong** hoặc sát biên. Ở 4049.9 giá đã nằm dưới cả biên chính (4064.4) lẫn biên phụ (4055.2) — tức là nó thuộc nhịp rơi, không phải nhịp test. Nhịp test đúng là đỉnh 01:00-00:47 khi giá bật lại chạm biên chính dưới 4064.4 từ bên trong rồi mới rơi (nhìn trên ảnh: cụm nến quanh 4064-4066 ngay trước cú sụp).
- **Dấu hiệu quyết định trên chart:** khoảng cách 14.5 giá từ LPSY[C] tới biên chính. Phase C phải bắt đầu **trước** cú phá, ở đây nó bắt đầu **sau**.
- **Nghi phạm trong thuật toán:** cửa sổ "nhìn ngược 60 nến, lấy đỉnh cao nhất" của Phase C gán ngược chọn cực trị theo giá tuyệt đối mà **không ràng buộc cực trị đó phải nằm trong/sát biên**. Thêm điều kiện: LPSY[C] phải cách biên chính ≤ vài tick, nếu không thì lùi cửa sổ.

### 3. Climax VSA 2.00× nhưng cây thật là cây liền trước (VSA 4.52×) — luật vi phạm: mục 4.0 "cụm climax"
- **Thuật toán gắn:** BCLX tại 18:31, đỉnh 4089.1, VSA 2.00×.
- **Đúng phải là:** cây −1 (18:30) có VSA **4.52×**, thân 0.81, đẩy giá từ 4081.4 lên 4085.9 — đó là cây nỗ lực thật. Cây +0 chỉ nối thêm 2.5 giá với volume bằng nửa. Mốc giá đỉnh 4089.1 thì đúng, nhưng nhãn nên đọc là **cụm 18:30-18:31**, và VSA hiển thị 2.00× khiến người đọc tưởng climax yếu.
- **Dấu hiệu quyết định trên chart:** panel volume — thanh cao nhất của cả cụm nằm ở nến TRƯỚC nến bị đánh dấu BCLX.
- **Nghi phạm trong thuật toán:** logic cụm climax chỉ dời mốc **về phía sau** (8 nến sau) khi có cực trị mới, không nhìn lui. Đây là lỗi nhẹ vì mức giá vẫn đúng.

### 4. (trình bày) Chưa hết đoạn "cụm phá" mà nhãn LPSY[C]/SOW/LPSY[D] chồng nhau
Ba nhãn nằm trong 19 nến, đè lên nhau trên ảnh. Lỗi trình bày, không phải lỗi cấu trúc.

## Đạt
- **Mở range (L1):** MOVE tăng 49.8 giá / 107 nến, hiệu suất 0.35, climax là đỉnh cao nhất cửa sổ — climax đúng là đang CHẶN move. Đạt.
- **Phase A (L2):** đủ 3 lần đổi hướng BCLX(4089.1) → AR(4064.4) → ST[A](4069.7); ST[A] nằm trong range, sát nửa trên, kết thúc Phase A đúng tại ST[A]. Đạt.
- **Biên (L3):** biên chính = climax + AR, giữ nguyên suốt 503 nến; đúng 1 biên phụ dưới 4055.2 do mSOW tạo ra. Đạt.
- **Tên range (L4):** origin BCLX + phá xuống thật = Phân phối. Đúng.
- **Phase B (L9):** 309/503 nến = phase dài nhất. Đạt. Đọc effort↔result trên ảnh: suốt Phase B giá kẹp giữa 4055-4070, phe mua nhiều lần thử biên chính trên 4089.1 mà **không lần nào chạm** — đỉnh cao nhất Phase B chỉ ~4071. Phe bán thì đã đi được tới 4055.2. Bên đi xa hơn là bên bán → nghiêng phân phối. Thuật toán không nói ra được điều này nhưng cũng không gán nhãn sai.
- **Không có Spring/UTAD giả:** một mSOW duy nhất, đúng L3 (mỗi bên tối đa 1 biên phụ).
- **Phase C ngắn nhất (7 nến), Phase E dài (121 nến), giá rời hẳn range đi tìm vùng 4037** — đúng L8, L10 về mặt tỉ lệ.

## Cần hỏi người học
- Khi cú phá diễn ra thành **một mạch** (không có nhịp test lại biên trước khi phá, như ở đây từ 00:47 rơi thẳng), có nên **không vẽ Phase C** thay vì gán ngược một LPSY[C] nằm ngoài range không? Hiện thuật toán bị ép phải sinh ra Phase C.
