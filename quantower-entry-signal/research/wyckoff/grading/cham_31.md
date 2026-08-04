# Chấm bài #31 — Phân phối (DIST) · 2026-06-10 06:08 → 08:02 (114 nến M1)

**Điểm: 4/10** — Đọc đúng bối cảnh (đỉnh của một move tăng 38 giá, sau đó sụp thật), nhưng thiếu hẳn Phase C, SOW neo vào cây yếu, và Phase A chốt sai chỗ.

## Lỗi (nặng → nhẹ)

### 1. Thiếu hẳn Phase C — có Phase D mà không gán ngược · luật vi phạm: L8
- **Thuật toán gắn:** dải phase A(20) → B(42) → **D(25)** → E(28). Không có Phase C, không có LPSY[C].
- **Đúng phải là:** L8 nói rõ case khó thì "**chờ SOS/SOW xuất hiện rồi quay lại vẽ Phase C**". SOW đã bắn ở 07:10, nên bắt buộc phải có LPSY[C] gán ngược. Nhìn ảnh, ứng viên rõ ràng là cụm đỉnh nhỏ **06:54–07:00 ở ~4231–4232** (nhịp hồi cuối lên đúng biên chính dưới rồi bị chặn) — đó là LPSY[C], Phase C bắt đầu từ đó. Đây đúng dạng lỗi Ca #20 nguồn 7.pdf (nhảy phase, thiếu một phase) nhưng ở phía thuật toán.
- **Dấu hiệu quyết định trên chart:** giữa mSOW (06:44) và SOW (07:10) có một nhịp hồi rõ lên chạm lại đường `bien CHINH duoi 4231.1` rồi rơi — nhịp đó đang bị bỏ trắng, không nhãn.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược Phase C = `min(60 nến, 1/2 độ dài Phase B)` = min(60, **21**) = 21 nến, cộng yêu cầu swing pivot 5 nến không cực trị mới. Trong 21 nến trước SOW giá trôi xuống đơn điệu nên pivot không xác nhận được → nhánh gán ngược im lặng bỏ qua thay vì hạ tiêu chuẩn (vd lấy đỉnh close cao nhất trong cửa sổ).

### 2. SOW neo vào cây yếu, chỉ vượt biên phụ 0.3 giá · luật vi phạm: L3 (SOS/SOW mạnh phải bứt qua biên phụ) + lỗi B của v5
- **Thuật toán gắn:** SOW 07:10 tại 4228.3, **VSA 1.69x**, thân 0.69.
- **Đúng phải là:** biên phụ dưới đã là 4228.6 (do mSOW 06:44 tạo ra). SOW ở 4228.3 vượt biên phụ đúng **0.3 giá = 3 tick** — bằng nhiễu, không phải "bứt qua". VSA 1.69x còn **thấp hơn cả mSOW 2.42x** trước đó: cú gọi là phá thật lại yếu hơn cú gọi là phá thất bại. Cây phá thật nhìn thấy trên panel volume là cụm **07:38 → 08:00** (hai cột vàng cao nhất khung), tương ứng đoạn giá gãy từ 4214 xuống 4185.
- **Dấu hiệu quyết định trên chart:** nhãn SOW nằm **cao hơn** đường `bien phu duoi 4228.6` trên ảnh, tức mức nhãn còn chưa xuống tới biên phụ; trong khi hai cột volume lớn nhất nằm lệch hẳn về phải, trong Phase E.
- **Nghi phạm trong thuật toán:** nhãn hồi tố chọn "VSA cao nhất **trong đoạn xác nhận 3 nến**" — đoạn quá ngắn nên nếu cả 3 nến đều yếu thì nhãn vẫn rơi vào nến yếu. Thiếu điều kiện tuyệt đối "nến mang nhãn SOS/SOW phải có VSA ≥ ngưỡng climax" hoặc phải là cây VSA cao nhất kể từ ST[A].

### 3. AR không phải đáy phản ứng đầu tiên · luật vi phạm: L3 (biên chính = climax + AR) + Ca #12 nguồn 7.pdf
- **Thuật toán gắn:** AR = 4231.1 tại 06:24, tức **16 nến** sau BCLX.
- **Đúng phải là:** đáy phản ứng ngay sau BCLX là **4232.0 (06:12)** — đọc thẳng từ bảng 12 nến (+2 low 4233.8, +3 low 4232.6, rồi 06:12 low 4232.0). Sau đó giá hồi lên 4238.9–4241 trong 06:13–06:20, tức đã có nhịp bật ngược đủ lớn. AR bị dời tới đáy thấp hơn ở 06:24 nên toàn bộ mốc Phase A trượt sang phải, dồn AR và ST[A] chỉ cách nhau **3 nến**. Ca #12 nguồn 7.pdf phát biểu tường minh: "đáy đầu tiên sau BCLX **luôn** là AR".
- **Dấu hiệu quyết định trên chart:** nhãn AR trên ảnh nằm gần như dính vào nhãn ST[A], cả hai đứng ở phần cuối Phase A — Phase A 20 nến nhưng hai mốc định nghĩa biên chỉ dùng 3 nến cuối.
- **Nghi phạm trong thuật toán:** mục 4.2 "nếu trong lúc chờ ST[A] giá phá xa hơn AR thì dời AR tới cực trị mới" — luật này không phân biệt "đáy mới sâu hơn 0.9 giá" (nhiễu) với "AR thật bị phá". Nên có sàn: chỉ dời AR khi cực trị mới sâu hơn cũ ≥ 1.5× ATR.

### 4. ST[A] nằm giữa range, không test lại vùng climax · luật vi phạm: L2
- **Thuật toán gắn:** ST[A] = 4239.2 (06:27).
- **Đúng phải là:** BCLX ở 4245.5; ST[A] cách climax **6.3 giá = 44% chiều cao range 14.4**, tức chỉ hồi được hơn nửa đường. Đây là lỗi giống bài #30 — cùng một nhánh code. Ở đây còn nhẹ hơn vì cụm đỉnh 06:15–06:27 đều nằm quanh 4239–4241 nên có thể coi là vùng cung, nhưng chưa phải test vùng BCLX.
- **Nghi phạm trong thuật toán:** thiếu **sàn** khoảng cách tới mức climax cho ST[A] (xem chi tiết ở bài chấm #30, lỗi 1).

### 5. Diễn giải nhịp nỗ lực/kết quả ngược dấu · lỗi ĐO LƯỜNG (chỉ số v6)
- **Thuật toán gắn:** nhịp 06:31, effort 1.07x, result 1.75, er = 0.61 → "vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** effort 1.07x là volume **xấp xỉ trung bình**, result 1.75 ATR là kết quả lớn → er = 0.61 mô tả nhịp đi **dễ dàng**, không phải hấp thụ. Câu diễn giải là chuỗi tĩnh (xem bài chấm #30 lỗi 5 và #32 lỗi 5 — cả ba bài nhận cùng một câu với er lần lượt 0.63 / 0.61 / 4.79).

## Đạt
- **Mục 1 (mở range):** MOVE tăng 38.0 giá / 83 nến / hiệu suất 0.38 — trên ảnh là một đợt tăng dốc liên tục từ 4197 lên 4245, không thể lẫn với đi ngang. Nến 06:08 là **đỉnh cao nhất** cửa sổ, VSA 2.77x → climax chặn được move. Điều kiện L1 thoả đầy đủ.
- **Mục 4 (tên range):** origin BCLX + phá thật xuống = **Phân phối** — đúng L4, và diễn biến sau đó (rơi 50 giá xuống 4185) xác nhận.
- **Mục 5 (B dài nhất):** B 42 nến so với A 20 / D 25 / E 28 — L9 thoả, dù biên độ chênh mỏng.
- **Mục 3 (biên):** biên chính 14.4 giá cố định; đúng **một** biên phụ dưới 4228.6; tỉ lệ 1.17x — không kéo biên theo giá.
- **Mục 8 (một phần):** LPSY[D] 07:16 VSA 0.44x — volume co lại đúng chiều khi retest, và nến này giữ được dưới biên (4225.9 < 4228.6).

## Cần hỏi người học
- Range chỉ **114 nến** với biên chính **14.4 giá (0.34%)** kẹp giữa một move tăng 38 giá và một cú sụp 50 giá: đây là "phân phối nhanh" hợp lệ (THEORY §4.4 nói phân phối phát triển nhanh hơn tích luỹ nhiều) hay là **đỉnh xu hướng bị cắt ngang** mà đúng ra không nên vẽ range? Với M1 thì ranh giới này quyết định khá nhiều bài trong lô.
