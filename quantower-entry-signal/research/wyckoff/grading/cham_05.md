# Chấm bài #05 — Tái phân phối (RE-DIST) · 2026-03-18 13:16 → 2026-03-19 03:31 (143 nến M1)

**Điểm: 5/10** — Khung range và tên gọi đúng, tỉ lệ phase đẹp; hỏng ở nhãn climax, ở LPSY[D] nằm trong range và Phase E cụt còn 1 nến.

## Lỗi (nặng → nhẹ)

### 1. LPSY[D] nằm hẳn TRONG range — luật vi phạm: L10 (retest phải **giữ được** ngoài biên)
- **Thuật toán gắn:** LPSY[D] tại 01:40, giá **4940.0**, trong khi biên chính dưới là **4918.1**.
- **Đúng phải là:** nhịp hồi sau SOW leo lại **22 giá vào trong range** thì đó không phải "retest giữ ngoài biên" — theo đúng khuôn CBR, đó là cú phá đang bị nghi ngờ. Hoặc gọi nó là nhịp hồi thất bại (và chờ nhịp tiếp theo mới đặt LPSY[D]), hoặc thừa nhận cú SOW này chưa đủ tiêu chuẩn Phase D tại thời điểm đó.
- **Dấu hiệu quyết định trên chart:** chấm tím LPSY[D] nằm rõ **phía trên** đường "bien CHINH duoi 4918.1", cùng cao độ với thân range.
- **Nghi phạm trong thuật toán:** LPS[D]/LPSY[D] đo bằng swing pivot (5 nến + 1.5× biên độ TB) **không kèm ràng buộc "phải ở ngoài biên"**. Thêm điều kiện: pivot retest phải đóng cửa ở phía ngoài biên chính, nếu lùi vào trong thì chạy nhánh vô hiệu.

### 2. Nhãn SC nằm trên đỉnh của move giảm, cao hơn biên dưới 36 giá — luật vi phạm: L3
- **Thuật toán gắn:** SC tại 12:43, giá **4953.9** (VSA 2.26x) — trước nến mở range 33 phút, cao hơn mức climax 4918.1 tới 35.8 giá, tức nằm **giữa** đoạn giảm.
- **Đúng phải là:** SC phải ở 4918.1 (đáy đang được vẽ làm biên chính dưới). Trên ảnh, chấm SC treo lơ lửng trên đường dốc trắng, ngoài khung range.
- **Nghi phạm trong thuật toán:** lỗi cụm climax (13.1c, revert).

### 3. Nến mở range không phải cây climax — luật vi phạm: L1
- **Thuật toán gắn:** nến 13:16 làm mốc mở range: **VSA 1.05x, 3 lot, biên độ 2.4 giá**.
- **Đúng phải là:** trong bảng 12 nến, cây có volume thật là **+4 (13:30, 11 lot, VSA 3.61x)**, xuất hiện **sau** đáy — tức đáy 4918.1 hình thành trước, cao trào bán đến sau. Có thể chấp nhận (cao trào dạng "cạn kiệt", THEORY §6.2) nhưng khi đó phải gắn cờ, không được để một cây 3 lot làm mốc.

### 4. Phase E dài 1 nến — luật vi phạm: L10 + tái phát lỗi J của v5
- **Thuật toán gắn:** E = **1 nến** (03:31).
- **Đúng phải là:** nhìn ảnh, sau khi range đóng giá còn rơi từ ~4915 xuống **4820** trong khoảng 100 nến kế tiếp — toàn bộ "kết quả" của cause nằm ngoài range vẽ. Phase E 1 nến chính là bệnh mà lỗi J đã vá ở v5 nhưng nay quay lại trên range hẹp.
- **Nghi phạm trong thuật toán:** ba mốc dừng E (lùi vào biên / 2× chiều cao / 120 nến) đều tính từ chiều cao range 51.9 giá; mốc 2× ăn ngay.

### 5. (nhỏ) mSOS 4978.0 gắn cho nến VSA 0.54x
- Cú thăm dò biên trên bằng nến 0.54x, thân 0.00 mà được gọi **mSOS** (theo định nghĩa v6, mSOS = đã phá được thật) là quá nặng tay; nó vẫn nới biên phụ trên lên 4978. Cùng loại lỗi với UT[B] ở bài #04.

## Đạt
- Điều kiện mở range: MOVE 137.1 giá / 91 nến / hiệu suất 0.37 — move giảm thật bị chặn, đúng L1.
- ST[A] tại 4937.0 = hồi **64%** khoảng AR↔climax, đi về đúng phía climax và Phase A đóng ngay tại đó — đúng L2.
- Tỉ lệ phase: A 27 · B **86** · C **5** · D 25 · E 1 → B dài nhất, C ngắn nhất — đúng L9 và L8.
- Biên chính = climax 4918.1 + AR 4970.0, cố định suốt range; đúng một biên phụ trên (4978.0) — đúng L3.
- Tên **Tái phân phối**: origin SC + phá thật xuống = đúng bảng L4, và đây chính là ca mà bản cũ hay xoá oan.
- SOW neo đúng cây phá (VSA 4.00x, thân 0.65) và đóng cửa dưới cả biên chính lẫn cực trị cũ — đúng L3/L10.
- SOT phía trên n=3 kèm tỷ lệ volume 0.60 (cạn kiệt) đo đúng theo THEORY §7 và khớp với hướng phá thật.
