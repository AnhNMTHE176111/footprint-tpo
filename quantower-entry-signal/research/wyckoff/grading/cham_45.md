# Chấm bài #45 — Chưa rõ (BCLX) (DIST?) · 2026-07-14 12:33 → 16:32 (239 nến M1)

**Điểm: 5/10** — Vùng đấu giá là THẬT, biên chính đặt đúng, cú SOW đọc được; nhưng phải sửa 3 nhãn: ST[A] rơi giữa range, LPSY[C] sai vai, và Phase C dài gấp hơn 2 lần Phase D.

## Lỗi (nặng → nhẹ)

### 1. Phase C (59 nến) DÀI HƠN Phase D (26 nến) — luật vi phạm: L8
- **Thuật toán gắn:** Phase C = 15:08 → 16:06 (59 nến), Phase D = 16:07 → 16:32 (26 nến).
- **Đúng phải là:** Phase C phải là phase ngắn nhất. Ở đây cái được gọi là "Phase C" chính là toàn bộ đoạn giá tuột từ 4108.7 xuống 4073.5 — đó là **đoạn phá vỡ**, tức Phase D đang bắt đầu, không phải giai đoạn "test cuối trong range".
- **Dấu hiệu quyết định trên chart:** trong đoạn 15:08→16:06 giá đi một chiều 35 giá xuống, xuyên qua biên chính dưới 4076.2 và tạo cả biên phụ 4073.5 (mSOW 15:42). Một phase mà giá đi hết chiều cao range thì không còn là Phase C.
- **Nghi phạm trong thuật toán:** mốc bắt đầu Phase C được đặt tại LPS[C]/LPSY[C] gán ngược (mục 6 case khó, cửa sổ 60 nến), nhưng không có trần "Phase C ≤ độ dài Phase D" hay "Phase C phải kết thúc trước nến phá biên đầu tiên". mSOW 15:42 nằm vật lý trong dải C nhưng bảng lại ghi Phase=B — hai bộ đếm không nhất quán.

### 2. LPSY[C] gán sai vai — luật vi phạm: L6/L7 + THEORY §4.1 (định nghĩa LPSY)
- **Thuật toán gắn:** LPSY[C] tại 15:08, giá 4108.7, VSA 3.02x.
- **Đúng phải là:** đây là **UT[B]** — cú test biên trên. Nó là ĐỈNH cao nhất của toàn bộ Phase B/C, chạm sát biên chính trên 4112.5 (thiếu 3.8 giá, không phá biên nên chưa phải UTAD).
- **Dấu hiệu quyết định trên chart:** LPSY theo định nghĩa gốc là "một đợt phục hồi **yếu** trên biên hẹp, nguồn cầu cạn kiệt". Cú này VSA 3.02x (nổ volume, thanh vàng rõ trên panel dưới) và tạo đỉnh cao nhất range — không có gì "yếu". Gọi LPSY cho một đỉnh mới nổ volume là ngược nghĩa.
- **Nghi phạm trong thuật toán:** nhánh gán ngược Phase C lấy "đỉnh cao nhất trong 60 nến trước cú phá" làm LPSY[C] — chọn theo CỰC TRỊ GIÁ, không kiểm tra tính chất "hồi yếu, volume co". Cần thêm điều kiện volume/spread giảm so với nhịp trước, nếu không thì gọi UT[B] chứ đừng gọi LPSY.

### 3. ST[A] rơi giữa range, không test lại vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 13:02, giá 4091.0.
- **Đúng phải là:** ST[A] phải là cú quay về **phía climax** (4112.5) rồi bị chặn. 4091.0 nằm ở **41% chiều cao** tính từ AR 4076.2 lên (range 36.3 giá) — đúng cái "ngọ nguậy giữa range" mà L2 loại trừ. Phase A ở đây thực chất chưa hoàn thành 3 lần đổi hướng.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm lơ lửng giữa hai đường cam, không tiệm cận đường nào.
- **Nghi phạm trong thuật toán:** vá lỗi D của v5 đã bỏ HẾT ngưỡng %, chỉ còn "swing pivot 5 nến + sàn 1.5× biên độ TB". Sàn nhiễu quá thấp nên pivot đầu tiên bất kỳ cũng thành ST[A]. Cần thêm điều kiện tối thiểu "ST[A] phải vào được 1/3 phía climax" (THEORY §5 chia range 3 phần) hoặc "cách mức climax ≤ 1/3 chiều cao".

### 4. Nến mở range không phải cây climax thật — luật vi phạm: L1/mục 4.0 spec
- **Thuật toán gắn:** range mở tại 12:33 (VSA 1.98x, biên độ 11.3 giá); nhãn BCLX đặt ở 12:31 (7.01x).
- **Đúng phải là:** cây cao trào thật là **12:30** — 4036.0 → 4098.4, biên độ 62 giá, volume 4597, **VSA 14.64x**. Đó là cây tin tức tạo ra toàn bộ move; ba cây sau nó (7.01x, 3.97x, 1.98x) là volume tàn dư đang giảm dần.
- **Dấu hiệu quyết định trên chart:** trên panel volume có đúng MỘT cột vàng cao vượt trội, cột đó nằm trước nến mở range.
- **Nghi phạm trong thuật toán:** cửa sổ "cụm climax 8 nến" chỉ dời mốc **về sau**, không nhìn lại. Cây 12:30 bị loại vì bản thân nó không thoả điều kiện "climax phải là cực trị của cửa sổ 240 nến" (đỉnh 4098.4 thấp hơn 4112.5 sau đó). Hệ quả nữa: "MOVE 78.3 giá, hiệu suất 0.36" — 62/78 giá của move đó nằm trong đúng một nến, hiệu suất chỉ vừa qua ngưỡng 0.35. Đây là ca biên của L1 mà thước đo hiện tại không phân biệt được: **gap tin tức 1 nến** vs **xu hướng 179 nến**.

### 5. (trình bày) Nhãn "biên phụ dưới 4073.5" chồng lên nhãn LPSY[D]
Góc phải chart, hai nhãn đè nhau, không đọc được mức. Lỗi trình bày, không ảnh hưởng cấu trúc.

## Đạt
- **Mục 3 (biên):** biên chính 4076.2–4112.5 = climax + AR, không bị kéo theo giá; biên phụ dưới 4073.5 đúng là cực trị xa nhất, mỗi bên tối đa 1. Tỷ lệ phụ/chính 1.07x — vùng cân bằng hẹp, hợp lý.
- **Mục 5 (Phase B):** 125 nến, dài nhất trong range → đúng L9.
- **Mục 7 (D/E):** SOW 16:07 đóng cửa 4065.4 — bứt qua **biên phụ** 4073.5 chứ không chỉ biên chính, đúng yêu cầu L3. LPSY[D] 16:16 hồi lên 4072.3 vẫn giữ **ngoài** biên, đúng CBR (L10).
- **Mục 4 (tên):** trạng thái `superseded` không đặt tên 4 mẫu hình — cơ chế mới, hợp lệ; ghi chú "(DIST?)" khớp đúng origin BCLX + phá xuống theo L4.
- **Mục 8 (volume):** SOW VSA 2.31x, LPSY[D] VSA 0.57x — nỗ lực nổ ở cú phá, co lại ở nhịp test. Đọc đúng effort↔result.
- **Chỉ số Phase B mới:** "nhịp nỗ lực/kết quả er=36.67 (effort 1.05x, result 0.03)" — đo ĐÚNG bản chất: 16 nến volume trung bình mà biên độ gần bằng 0, đúng là vùng hấp thụ đáng nghi. Bias=+0 (test cả hai biên) khớp với hình.

## Cần hỏi người học
- Một cây tin tức nổ 62 giá rồi bị chặn ngay tại đó: cây đó là **MOVE** hay là **CLIMAX**? Nếu tính là climax thì L1 không còn "MOVE xu hướng" nào phía trước; nếu tính là move thì climax là cây nào trong 3 cây tàn dư sau nó? Đây là ca biên mà thước "hiệu suất hướng ≥ 0.35" không phân xử được.
