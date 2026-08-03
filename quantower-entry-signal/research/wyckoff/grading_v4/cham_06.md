# Chấm bài #06 — Phân phối (DIST) · 2026-04-17 13:10 → 2026-04-21 17:19 (1631 nến M1)

**Điểm: 4/10** — Cấu trúc phân phối đọc đúng về đại thể, nhưng **cả hai biên chính đều neo sai nến**: nhãn AR không nằm trên biên mà chính thuật toán vẽ, và cây gọi là BCLX không phải cực trị của move. Giữ range, vẽ lại Phase A.

## Lỗi (nặng → nhẹ)

### 1. Nhãn AR bị bỏ rơi — biên chính dưới 4793.0 không phải mức AR — luật vi phạm: L2, L3
- **Thuật toán gắn:** AR tại 2026-04-17 20:05, giá **4903.8** (VSA 1.33x). Biên CHÍNH dưới vẽ ở **4793.0**.
- **Đúng phải là:** AR = đáy của cú phản ứng tự động = **4793.0** (cú rơi mở phiên 04-19 22:44). Cây 4903.8 chỉ là một nhịp nghỉ giữa đường rơi, không phải đáy phản ứng.
- **Dấu hiệu quyết định trên chart:** hai con số tự tố nhau — biên chính dưới ghi 4793.0 nhưng nhãn AR ghi 4903.8, lệch **110.8 giá**. Trên ảnh, nét liền cam dưới đi qua đúng đáy cú rơi 04-19, còn chấm AR treo lơ lửng giữa đoạn giảm 04-17 tối. Theo L3 biên chính = mức climax + **mức AR**, nên một trong hai con số bắt buộc sai.
- **Nghi phạm trong thuật toán:** cửa sổ tìm AR cố định **40 nến** sau climax (mục 4.1 tài liệu thuật toán). Sau 40 nến giá mới xuống 4903.8 nên AR chốt ở đó; biên vẫn nới thụ động tới 4793.0 nhưng **nhãn AR không được dời**, dù mục 4.2 spec ghi rõ "giá phá xa hơn AR → AR được dời tới cực trị mới". Đây là lỗi parity giữa spec và code, xuất hiện lại ở bài #07 và #09.

### 2. Cây climax không chặn được move — nó nằm giữa move — luật vi phạm: L1, L3
- **Thuật toán gắn:** BCLX tại 13:10, đỉnh **4936.9**, VSA 4.10x → làm biên CHÍNH trên.
- **Đúng phải là:** BCLX ở nến **13:13** (đỉnh **4953.8**, VSA 3.31x, thân/biên **0.16**) — nến râu dài từ chối giá, đúng hình cao trào mua. Biên chính trên phải là 4953.8; cái thuật toán đang vẽ nét đứt mới là biên chính thật.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu, 3 nến ngay sau climax có đỉnh **4941.8 / 4944.3 / 4953.8** — đều cao hơn "climax" 4936.9, tối đa **+16.9 giá**. Giá vượt biên chính chỉ 3 phút sau khi mở range, tức chưa có range nào để mà "thăm dò" → đây là phần đuôi của cùng một cú đẩy, không phải cú test tạo biên phụ theo L3.
- **Nghi phạm trong thuật toán:** điều kiện (2) mục 3 chỉ kiểm "climax là cực trị của **cửa sổ 240 nến nhìn lại**", không kiểm về phía trước. Cần thêm ràng buộc: trong N nến sau climax không được có cực trị mới cùng phía.

### 3. Range quá cao và quá dài cho khung M1 — luật vi phạm: cảnh báo "khung quá thô" trong CHART_CASES
- **Thuật toán gắn:** biên chính cao **143.9 giá = 2.92% giá**, 1631 nến (~27 giờ giao dịch, trải 4 ngày).
- **Đúng phải là:** đây là range **cao nhất toàn lịch sử** theo chính đo đạc của thuật toán (trung vị 21.6 giá) và sát ngưỡng huỷ 3.5%. Cấu trúc cỡ này phải vẽ trên M15/M30 mới ra hình — đúng lời giảng viên nhiều lần nhắc học viên đổi khung (Ca #4, #6, #19 nguồn 7.pdf).
- **Dấu hiệu quyết định trên chart:** nửa phải của ảnh (04-21 00:59 → 16:00) là một đoạn **giảm liên tục** đỉnh thấp dần 4890 → 4770, không phải dao động quanh một trục cân bằng. Hệ quả đo được: đích Phase E = 1.0 × 143.9 giá là bất khả thi trong 26 nến, nên Phase E không bao giờ đạt.
- **Nghi phạm trong thuật toán:** guard "cao > 3.5% giá" (mục 8) quá lỏng khi tính theo % giá tuyệt đối; nên thêm guard tương đối theo ATR khung đang vẽ, hoặc chặn range dài quá một phiên trên M1.

### 4. DA gán cho một cú thủng sâu 15.4 giá — đó là mSOW[B] — luật vi phạm: nhãn sai vai, THEORY §4.4
- **Thuật toán gắn:** DA tại 04-21 14:48, giá **4777.6**.
- **Đúng phải là:** **mSOW[B]** (minor Sign of Weakness trong Phase B). THEORY §4.4 nói rõ "minor SOW xuất hiện ở Phase B"; CHART_CASES dùng nhãn này nhiều lần (Ca #2 nguồn 4.pdf, Ca #J23).
- **Dấu hiệu quyết định trên chart:** 4793.0 − 4777.6 = **15.4 giá = 154 tick**, gấp 10 lần ngưỡng "thăm dò NHẸ < 15 tick" của chính thuật toán. Một cú xuyên biên sâu như vậy mang thông tin cung áp đảo, gọi "DA" là làm mất thông tin đó.
- **Nghi phạm trong thuật toán:** bảng mục 5.1 — cạnh AR luôn ra UA/DA bất kể độ sâu ("vẫn không quyết định"). Nên tách: cạnh AR + thủng sâu + VSA cao → mSOW/mSOS.

### 5. Thiếu Phase E và thiếu LPSY[D] — luật vi phạm: L10
- Phase D chỉ 26 nến, không có nhịp hồi retest nào được đánh dấu, không có Phase E. Mô hình CBR của L10 (phá → hồi retest **giữ được** ngoài biên → đi tiếp) **chưa được chứng minh** trên bài này; range đóng ở D theo guard chứ không theo diễn biến giá. Đây là hệ quả trực tiếp của lỗi #3 (range quá cao ⇒ đích Phase E vô lý).

## Đạt
- **Tên range đúng (L4):** BCLX chặn move tăng + phá thật xuống = Phân phối. Khớp bảng 4 pattern.
- **Có MOVE thật trước climax (L1, phần điều kiện CẦN):** 100.3 giá / 137 nến / hiệu suất hướng 0.36 — trên ảnh mũi xám là một đoạn tăng liền mạch, không phải đi ngang.
- **Tỉ lệ phase đúng chiều (L9, L8):** B = 1147 nến dài nhất, C = 60 nến ngắn nhất trong A/B/C. Không có ST[B] (đúng L6). LPSY[C] chỉ 1 điểm (đúng L7).
- **Đọc Phase B khớp THEORY §5:** suốt 1147 nến Phase B giá chỉ test được **đáy** (DA 4777.6) và không lần nào chạm lại biên trên 4936.9 (cao nhất chỉ ~4890) → đúng ca "test đáy + không chạm được đỉnh ⇒ LPSY sẽ là event Phase C", và đó chính là những gì xảy ra. Chuỗi Phase B→C ở đây hợp lý.
- **SOW đủ chất lượng (mục 8, L3):** VSA **4.95x** (nỗ lực tăng rõ), thân 0.59, và đóng cửa bứt qua **biên phụ** 4777.6 xuống 4766.9 — đúng yêu cầu "SOS/SOW mạnh phải qua biên phụ".
- **Biên phụ đúng quy tắc L3:** mỗi bên đúng 1 cái (4953.8 trên / 4777.6 dưới), là cực trị xa nhất.

## Cần hỏi người học
- Với range trải nhiều phiên như bài này (1631 nến M1, 2.92% giá), có muốn thuật toán **tự chặn** không vẽ trên M1 và để dành cho khung cao hơn, hay vẫn giữ để phục vụ vào lệnh M1?
