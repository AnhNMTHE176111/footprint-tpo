# Chấm bài #06 — Chưa rõ (BCLX) (DIST?) · 2026-04-02 14:43 → 20:59 (223 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây. Cây climax là nến 2 hợp đồng, VSA 0.24x — nó không chặn được gì cả.

## Lỗi (nặng → nhẹ)

### 1. Climax không phải climax — VSA 0.24x, volume 2 hợp đồng — luật vi phạm: L1 (điều kiện ĐỦ), THEORY §3.3 (SC/BCLX = "khối lượng tăng mạnh")
- **Thuật toán gắn:** BCLX tại 14:43, giá 4762.2, **VSA = 0.24x**, volume = **2 hợp đồng**, biên độ 3.7 giá.
- **Đúng phải là:** không có climax nào ở đây. Chính phiếu số liệu của bài này ghi ngưỡng mở range là "VSA ≥ 2.2x"; cây được chọn thấp hơn ngưỡng **9 lần**. Nến VSA cao thật nằm ngay cạnh: nến −6 (2.99x, 20 hợp đồng) và nến +1 (2.38x, 22 hợp đồng).
- **Dấu hiệu quyết định trên chart:** trên panel khối lượng, ngay tại vạch Phase A, cột volume gần như **không nhìn thấy** — trong khi hai bên trái phải đều có cột vàng cao. Một "cao trào mua" mà 2 người mua thì không phải cao trào.
- **Nghi phạm trong thuật toán:** logic "cụm climax" ở mục 4.0 — trong 8 nến đầu, mốc climax **dời sang cực trị mới cùng phía** nhưng khi dời thì **không kiểm lại điều kiện VSA/biên độ** trên cây mới. Cây mở range hợp lệ chắc là nến −6 (2.99x); sau đó mốc bị dời lên đỉnh 4762.2 và VSA của cây gốc bị vứt. Sửa: khi dời mốc cụm, hoặc giữ VSA/biên độ của cây kích hoạt, hoặc bắt cây đích cũng phải đạt ngưỡng.

### 2. Climax nằm GIỮA move, không chặn move — luật vi phạm: L1 (điều kiện CẦN)
- **Thuật toán gắn:** BCLX 4762.2 là đỉnh chặn một move tăng 95.5 giá.
- **Đúng phải là:** nhìn ảnh, đỉnh thật của đợt tăng là cụm nến quanh 14:33–14:35 (đỉnh ~4765, cao hơn nhãn BCLX), rồi giá xổ xuống. Nhãn BCLX đặt tại 4762.2 nằm **thấp hơn** đỉnh thật đó. Biên chính trên vì thế cắt ngang thân nến chứ không nằm trên đỉnh — đúng lỗi A của vòng v4 mà v5 khai là đã vá.
- **Dấu hiệu quyết định trên chart:** đường "bien CHINH tren 4762.2" đi xuyên qua 3-4 nến ở khoảng 14:33–14:38 phía bên trái nhãn BCLX.
- **Nghi phạm trong thuật toán:** cửa sổ cụm climax chỉ nhìn **về sau** 8 nến, không nhìn **lùi lại**. Cực trị thật nằm trước nến kích hoạt vài nến thì máy không thấy.

### 3. ST[A] nằm giữa range, không phải test lại vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 4737.6, VSA 0.45x, thân/biên độ = 0.00 (nến doji).
- **Đúng phải là:** ST[A] phải là cú quay lại **tiệm cận vùng climax** (4762.2). 4737.6 nằm ở **41%** chiều cao biên chính (4720.0–4762.2) — tức giữa range, cách climax 24.6 giá. Đây là "một cái ngọ nguậy giữa range", đúng nguyên văn lỗi D của v4; v5 khai đã bỏ ngưỡng % và chuyển sang swing pivot, nhưng swing pivot cũng bắt trúng một cái ngọ nguậy.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm lơ lửng giữa hai đường cam, không chạm đường nào.
- **Nghi phạm trong thuật toán:** mục 4.2 — "swing pivot đầu tiên + nhịp hồi ≥ 1.5× biên độ TB" quá lỏng. Bỏ hết ngưỡng % thì mất luôn ràng buộc "ST phải TEST cái gì". Cần thêm điều kiện tối thiểu: ST[A] phải vào được vùng lân cận mức climax (vd trong 1/3 phía climax của range).

### 4. Range bắc qua khe cuối tuần — luật vi phạm: quyết định #5 người học chốt (cắt range tại khe > 4 giờ)
- **Thuật toán gắn:** range đóng "completed" tại 04-02 20:59.
- **Đúng phải là:** trục thời gian trên ảnh nhảy từ **04-02 20:29 sang 04-05 22:19** — đúng khe cuối tuần. Range danh nghĩa dừng ở 20:59 nên chưa vi phạm, nhưng phần chart bên phải (04-05) vẫn được vẽ liền mạch với biên phụ 4704.8 kéo qua khe, gây ảo giác biên còn hiệu lực sang tuần sau. Đây là **lỗi trình bày**, không phải lỗi cấu trúc.

### 5. Range chết ở Phase B, 179/223 nến không có sự kiện nào — luật vi phạm: L2/L8 (cấu trúc không hoàn thành)
- **Thuật toán gắn:** A (45n) → B (179n), hết. Nhãn duy nhất trong Phase B là mSOW.
- **Đúng phải là:** một range mà 80% thời lượng là Phase B trống rỗng, không có Phase C/D/E, không có tên — thì kết luận đúng là "không đủ bằng chứng để gọi đây là vùng đấu giá". Nhìn ảnh: từ 15:39 tới 19:04 giá bò ngang quanh 4715–4730, sau đó bật lên 4740 rồi lại xuống — không có cấu trúc, chỉ là nhiễu phiên chiều Mỹ. Đúng ca "Tái tích luỹ gượng ép" (Ca #20 nguồn 7.pdf): gò dữ liệu cho khớp mô hình.

## Đạt
- MOVE trước climax có thật: 95.5 giá / 78 nến / hiệu suất 0.36 — trên chart đợt tăng từ ~4650 lên ~4765 là một move xu hướng rõ ràng, không phải đi ngang.
- Không đặt tên range khi chưa có cú phá thật — giữ "Chưa rõ (BCLX)", đúng L4 và đúng lỗi F đã vá.
- mSOW gán đúng vai: cú thọc xuống 4704.8 (VSA 1.20x, thân 0.73) phá biên chính dưới nhưng không giữ được → hạ cấp mSOW, ở lại Phase B. Đúng mục 5.1.
- Biên chính không bị kéo theo giá về sau: 4720.0/4762.2 giữ nguyên suốt 223 nến (L3).
