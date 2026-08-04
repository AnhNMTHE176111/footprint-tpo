# Chấm bài #02 — Chưa rõ (BCLX) (DIST?) · 2026-01-18 23:56 → 2026-01-19 18:39 (32 nến M1)

**Điểm: 1/10** — Không được vẽ range ở đây. Cây "climax" có **VSA 0,23×** và **biên độ 0,0 giá**, tức là nó vi phạm thẳng cả hai điều kiện mở range mà chính tài liệu thuật toán ghi (biên độ ≥ 1,4× TB, VSA ≥ 2,2×). Đây là lỗi nặng nhất trong cả lô.

## Lỗi (nặng → nhẹ)

### 1. Climax không phải climax — VSA 0,23×, biên độ 0,0 giá — luật vi phạm: L1 + mục 3(1) tài liệu thuật toán + THEORY §3.3 (BCLX = "volume + spread tăng rõ rệt")
- **Thuật toán gắn:** BCLX tại 4786,2, nến 23:56 ngày 18/01.
- **Đúng phải là:** không có climax, không mở range. Nến đó là O=H=L=C=4786,2, **volume 2 hợp đồng**, VSA 0,23×. Định nghĩa gốc của BCLX là "volume và spread tăng rõ rệt, lực mua đạt đỉnh, công chúng đổ xô mua". Một nến 2 lot biên độ 0 là điều ngược lại hoàn toàn.
- **Dấu hiệu quyết định trên chart:** header ảnh tự ghi "climax UP **VSA=0.23x**". Panel volume tại vị trí BCLX không có thanh vàng nào; thanh vàng cao nhất trong vùng lại nằm **trước** BCLX (lúc ~01-18 23:05).
- **Nghi phạm trong thuật toán:** đây không phải lỗi ngưỡng, mà là lỗi **mốc climax bị dời sau khi đã kiểm điều kiện**. Cơ chế "cụm climax" của v5 (lỗi A) dời mốc climax sang cực trị mới trong 8 nến đầu **mà không kiểm lại điều kiện VSA/biên độ trên nến mới**. Nến gốc đủ 2,2× nhưng nến đỉnh của cụm chỉ 0,23× — và nhãn được gán vào nến đỉnh. Cần: sau khi dời mốc, hoặc kiểm lại điều kiện, hoặc giữ **giá** của cực trị nhưng giữ **nến gốc** làm cây climax để báo cáo VSA. Lỗi này lặp ở bài #03 (0,65×) và #04 (0,85×) — là **lỗi hệ thống mới sinh ra bởi chính bản vá v5**.

### 2. MOVE trước climax không đạt chuẩn "move xu hướng" — hiệu suất 0,37, dài 54,4 giá — luật vi phạm: L1
- **Thuật toán gắn:** MOVE 54,4 giá / 43 nến / hiệu suất 0,37, coi là đủ điều kiện CẦN.
- **Đúng phải là:** nhìn ảnh, đoạn "move tăng" mà đường xám nối tới là một đoạn giá đi từ ~4655 lên 4786 **xuyên qua một khe dữ liệu khổng lồ** — trục thời gian nhảy từ 01-16 15:33 thẳng sang 01-18 23:05. Cái gọi là "move 43 nến" thực chất bắc qua **cả cuối tuần**.
- **Dấu hiệu quyết định trên chart:** mũi xám "chân MOVE (54,4 giá, hiệu suất 0,37)" đặt ở nến 01-16 ~15:30; climax ở 01-18 23:56. Hơn 2 ngày lịch cho 43 nến.
- **Nghi phạm trong thuật toán:** guard "khe > 4 giờ thì cắt range" (v5 lỗi K) chỉ áp cho **thân range**, **không** áp cho cửa sổ nhìn lại 240 nến khi đo MOVE. Phải áp cùng guard cho cả đoạn đo MOVE.

### 3. AR là nến 1 lot, VSA 0,11× — luật vi phạm: L2
- **Thuật toán gắn:** AR tại 4764,6, VSA 0,11×, thân 0,00.
- **Đúng phải là:** AR theo định nghĩa gốc là "phản ứng tự động", một đợt bán tháo có lực sau khi lực mua cạn. VSA 0,11× là mức thấp nhất có thể có trên chart này. Không đủ tư cách xác lập một **biên chính cố định vĩnh viễn** (L3).
- **Dấu hiệu quyết định trên chart:** chấm AR nằm giữa một vùng nến mảnh, panel volume phẳng.
- **Nghi phạm trong thuật toán:** giống bài #01 lỗi 3 — bước tìm AR không có điều kiện chất lượng nến.

### 4. ST[A] không test lại vùng climax mà là một cây vượt qua nó — rồi vẫn được nhận — luật vi phạm: L2, L3
- **Thuật toán gắn:** ST[A] tại 4782,6, chốt Phase A tại 19/01 05:33; biên phụ trên 4786,5 (cao hơn climax 4786,2 đúng 0,3 giá).
- **Đúng phải là:** 0,3 giá = 3 tick. Đây không phải một cú "vượt biên tạo biên phụ", nó nằm trong sai số chạm biên 10 tick mà chính tài liệu thuật toán quy định. Vẽ ra một nét đứt "biên phụ" cách nét liền 0,3 giá là nhiễu thị giác, không phải thông tin.
- **Dấu hiệu quyết định trên chart:** hai đường "biên CHÍNH trên 4786,2" và "biên phụ 4786,5" chồng lên nhau tới mức nhãn text đè lên nhau không đọc được.
- **Nghi phạm trong thuật toán:** điều kiện tạo biên phụ không có ngưỡng tối thiểu. Nên yêu cầu vượt ≥ 10 tick (đúng bằng sai số chạm biên) mới ghi biên phụ.

### 5. Range 32 nến, chỉ có Phase A+B, đóng ở trạng thái [completed] — luật vi phạm: L2/L9 (tỉ lệ phase) + lỗi kinh điển "range quá vụn"
- **Thuật toán gắn:** Phase A 17 nến, Phase B 16 nến, hết. Range "[completed]".
- **Đúng phải là:** Phase B phải là phase **dài nhất** (L9). Ở đây B (16) ngắn hơn A (17). Một range 32 nến không bao giờ là một "vùng đấu giá" — nó là 32 cái tick rải rác trong 19 giờ.
- **Dấu hiệu quyết định trên chart:** ngay sau khi range đóng, giá đi thẳng một mạch từ 4786 lên 4830+ mà không hề có SOS nào được ghi. Vùng đó không hề có tính chất cân bằng.
- **Nghi phạm trong thuật toán:** range được đóng khi hết dữ liệu ứng viên chứ không phải khi cấu trúc hoàn tất, và không có kiểm tra hậu nghiệm "B phải dài nhất" trước khi xuất bản range.

## Đạt
- Không đặt tên range khi chưa phá biên — đúng L4.
- Biên chính = climax + AR, không bị kéo theo giá — đúng L3.
- Không có nhãn ST[B] — đúng L6.
