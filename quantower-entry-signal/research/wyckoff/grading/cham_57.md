# Chấm bài #57 — Chưa rõ (BCLX) (DIST?) · 2026-07-27 00:14 → 03:51 (217 nến M1, superseded)

**Điểm: 4/10** — Tỉ lệ phase đẹp nhất lô (B dài nhất, C ngắn nhất), nhưng nhãn climax rơi lạc 14 nến vào giữa move, và cái gọi là SOW thực ra là một cú rũ biên dưới.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX nằm giữa move, không phải cây chặn move — luật vi phạm: L1
- **Thuật toán gắn:** nhãn **BCLX tại 00:00, giá 4104.6**, trong khi range mở tại **00:14, mức 4119.3**. Nhãn lệch **14 nến về trước** và **14.7 giá thấp hơn** biên chính trên.
- **Đúng phải là:** nhãn climax phải nằm tại chính cây chặn move — đỉnh 4119.3 (00:13–00:14). Chấm đỏ hiện tại nằm lọt thỏm giữa nhịp tăng, phía dưới nó còn 4 cây nữa mới tới đỉnh.
- **Dấu hiệu quyết định trên chart:** chấm BCLX nằm ngay giữa đoạn dốc lên; các nến −5 → −2 (VSA 3.52× / 2.90× / 2.83×) đều tạo đỉnh cao hơn nó. Nến mở range thật (+0) chỉ có VSA **1.98×**, biên độ 1.8 giá — dưới cả ngưỡng climax 2.2×.
- **Nghi phạm trong thuật toán:** lỗi "nhãn cụm climax" đã biết, thử sửa ở 13.1c rồi revert. Hai cửa sổ tách nhau (giá trượt tự do, nhãn chọn theo VSA cao nhất) cho phép nhãn đi ngược lại tới 14 nến trước mốc mở range. Cần chặn phía **trước** `r.start_i`, không chỉ phía sau.

### 2. "SOW" thực ra là cú rũ biên dưới — luật vi phạm: L5 + L4
- **Thuật toán gắn:** SOW 03:26 tại 4089.5 (VSA 2.37×) → Phase D → range đóng **superseded**, range #58 sinh ra và chạy **LÊN** tới 4108.
- **Đúng phải là:** giá thọc xuống 4087–4089 rồi bật lại vào trong và sau đó đi lên hẳn — đó là **Spring/Shakeout** ở biên dưới, và cấu trúc phải đọc là phân phối **thất bại** → tích luỹ (L4: phá sai hướng không huỷ range, chỉ đổi tên; ở đây phải đổi thành **Tái tích luỹ / Tích luỹ**, không phải bỏ trống tên).
- **Dấu hiệu quyết định trên chart:** LPSY[D] 03:35 tại 4092.6 nằm **cao hơn** biên phụ dưới 4091.0 — nghĩa là nhịp hồi đã lấy lại vùng giá, không hề "giữ được ngoài biên" như L10 đòi. Sau đó giá đi ngang 4090–4096 rồi bung lên.
- **Nghi phạm trong thuật toán:** cơ chế SIDEWAYS cắt vụn một cấu trúc thành cha `superseded` + con — đúng lỗi hệ thống mới liệt kê ở 13.1b, chưa sửa.

### 3. Cây mạnh nhất bị gán minor, SOW đặt vào cây yếu hơn — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** mSOW 03:10 tại 4091.0 với **VSA 4.93×**; SOW 03:26 với VSA 2.37×.
- **Đúng phải là:** nếu công nhận có cú phá xuống thì nhãn chính phải hồi tố về cây 03:10 — nó vừa mạnh nhất vừa tạo ra chính mức biên phụ 4091.0.
- **Nghi phạm trong thuật toán:** `_demote_shock()` / nhánh hồi tố nhãn không chạy khi cú trước bị hạ cấp rồi cú sau mới chốt — lỗi "ăn không đều" ở 13.1b.

### 4. ST[A] vẫn lửng giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 00:51 tại 4111.6.
- **Đúng phải là:** test lại **vùng climax** (4119.3). Đo được: retrace từ AR = (4111.6−4093.2)/26.1 = **0.70**, tức còn cách climax **7.7 giá = 30% chiều cao range**. Vừa lọt ngưỡng 0.55 mới nhưng vẫn không chạm được vùng cần test.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC=0.55` cứu được các ca 0.4–0.55 nhưng không cứu ca 0.55–0.75. Cần thêm điều kiện tuyệt đối "khoảng cách ST[A]→climax ≤ ~25% chiều cao range".

### 5. AR trên nến gần như trống — luật vi phạm: mục 8 (trình bày/đo lường)
- AR 00:28 tại 4093.2: **VSA 0.44×, thân 0.08**. Đây là một cây doji volume rất thấp, không phải "lực đẩy tự động". Bài #55 được gắn cờ "(yếu)" trong ca nhẹ hơn (VSA 1.32×) mà ca này lại không — cờ cảnh báo đang không dùng `ar_vsa`.

### 6. Số đo MOVE lệch với hình — trình bày/đo lường
- Phiếu ghi MOVE "13.2 giá / 50 nến"; trên chart mũi xám xuất phát từ ~4088 (22:58) tới đỉnh 4119.3 = khoảng **31 giá**. Con số hiển thị không mô tả cái mũi tên đang vẽ — người đọc phiếu bị lệch nhận thức về độ mạnh của move.

## Đạt
- **Tỉ lệ phase đúng luật:** A=38 · B=146 · **C=8** · D=26 — Phase B dài nhất (L9), Phase C ngắn nhất (L8). Bản vá bỏ ràng buộc "đúng nửa range" cho kết quả tốt ở đây.
- Biên chính cố định, biên phụ mỗi bên tối đa 1, tỷ lệ 1.08× — không phình (L3 đạt).
- LPSY[C] 03:18 đúng một điểm, không vẽ vùng (L7 đạt).
