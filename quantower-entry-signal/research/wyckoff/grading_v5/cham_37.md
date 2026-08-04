# Chấm bài #37 — Tái phân phối (RE-DIST) · 2026-07-08 07:19 → 08:54 (95 nến M1)

**Điểm: 1/10** — không nên vẽ range ở đây. Climax VSA 1.29× (không phải climax), range 12.1 giá / 95 nến đủ Phase A→E (nhiễu, không phải vùng đấu giá), và toàn bộ Phase C-D-E được gắn ở vùng giá **cách biên dưới 25-42 giá** — tức bên ngoài range xa gấp đôi chiều cao chính nó.

## Lỗi (nặng → nhẹ)

### 1. Không có climax nào cả — luật vi phạm: L1, mục 3(1) tài liệu thuật toán
- **Thuật toán gắn:** SC tại 07:19, giá 4125.4, **VSA 1.29×**, volume 74.
- **Đúng phải là:** không mở range. Nhìn cả 12 nến quanh climax: volume 93, 47, 78, 61, 22, 45, **74**, 20, 84, 44, 47, 65. Cây được gọi là "cao trào bán" có volume **74** — đứng thứ ba trong cụm, thua cả nến −6 (93) và nến +2 (84). Không có nổ khối lượng, không có mở rộng biên độ (2.1 giá so với TB không đáng kể), thân/biên chỉ 0.29.
- **Dấu hiệu quyết định trên chart:** panel volume phía dưới — **cả đoạn 07:19 gần như không có thanh vàng nào** (vàng = VSA ≥ 2.2×). Thanh vàng duy nhất trên chart nằm ở 08:14, tức cây sụp, chứ không ở chỗ SC.
- **Nghi phạm trong thuật toán:** giống bài #36 — cụm climax (mục 4.0) dời mốc sang cực trị mà không kiểm lại VSA tại cây mới. Nhưng bài này nặng hơn: **không cây nào trong cụm đạt 2.2×**, nghĩa là ứng viên gốc cũng đã lọt cửa. Cần in ra VSA của cây gốc đủ ngưỡng để truy được chỗ rò.

### 2. Phase C/D/E nằm hoàn toàn NGOÀI range, cách biên dưới 22–42 giá — luật vi phạm: L8, L10, L3
- **Thuật toán gắn:** biên chính dưới **4125.4**; LPSY[C] = **4102.8** (dưới biên 22.6 giá), SOW = **4083.7** (dưới biên 41.7 giá), LPSY[D] = **4087.0**.
- **Đúng phải là:** biên chính chỉ cao **12.1 giá**. SOW nằm dưới biên **3.4 lần chiều cao range**. Không có "cú phá biên" nào ở đây — giá đã rơi tự do khỏi vùng từ lâu; SOW gắn ở 08:36 là gắn vào **giữa đợt rơi**, sau khi cây sụp thật (08:14) đã kết thúc. Nếu vẫn muốn giữ range thì SOW phải là **cây 08:14** (thanh vàng duy nhất, biên độ ~15 giá, xuyên thẳng qua biên chính dưới).
- **Dấu hiệu quyết định trên chart:** trên ảnh, cây nến đỏ khổng lồ tại 08:14 rơi từ ~4132 xuống ~4116 kèm thanh volume vàng cao nhất bảng. Ba vạch tím Phase C/D/E đều nằm **bên phải** cây đó, ở vùng giá 4083–4102 — tức máy đặt tên phase sau khi cấu trúc đã tan.
- **Nghi phạm trong thuật toán:** nhánh "gán ngược Phase C, nhìn lại 60 nến lấy đỉnh cao nhất" (mục 6) + nhánh SOS/SOW hồi tố (mục 5.1, lỗi B). Cả hai chọn cực trị trong cửa sổ mà **không ràng buộc khoảng cách tới biên**. Phải thêm điều kiện: LPSY[C] phải nằm trong dung sai (vd 0.5× chiều cao range) của biên; SOW hồi tố phải là cây **đầu tiên** đóng cửa vượt biên, không phải cây VSA cao nhất trong cả đoạn kéo dài.

### 3. Range 12.1 giá / 95 nến mà đủ 5 phase = nhiễu — luật vi phạm: L1, chuẩn "khung quá thô / range quá vụn"
- **Thuật toán gắn:** A=20 · B=51 · C=6 · D=17 · E=2 nến. Tổng 95 nến, biên chính 0.29% giá.
- **Đúng phải là:** một TR M1 dài 95 nến với đủ A→E thì theo chuẩn chấm phải nghi ngay là nhiễu. Ở đây còn tệ hơn: Phase E dài **2 nến**. Hai nến không đủ để gọi là "giá rời range đi tìm vùng giá mới".
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, cả cấu trúc A+B (71 nến, từ 07:19 đến 08:29) chiếm một dải giá hẹp chưa tới 14 giá, còn cú rơi sau đó đi 50 giá trong 20 nến. Cái "range" là chỗ giá nghỉ giữa hai đoạn giảm, không phải chỗ đấu giá.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range" (quyết định 1, v5). Quyết định đó đúng về nguyên tắc, nhưng cần đi kèm điều kiện **chất lượng climax** — mà điều kiện đó đang bị lỗi #1 vô hiệu hoá.

### 4. MOVE trước climax chỉ 13.5 giá — luật vi phạm: L1
- **Thuật toán gắn:** MOVE dài 13.5 giá / 55 nến / hiệu suất 0.50.
- **Đúng phải là:** move 13.5 giá mà chỉ chặn được bằng một range 12.1 giá thì "nguyên nhân" và "kết quả" gần bằng nhau — không có gì đáng chặn. Điều kiện spec là move ≥ 8× biên độ TB 20 nến; với biên độ TB cỡ 1.5-2 giá ở phiên này thì 13.5 giá là **vừa đủ lọt cửa**, không phải một xu hướng thật.
- **Dấu hiệu quyết định trên chart:** đường xám "chân MOVE" trên ảnh nghiêng rất thoải, đi qua 55 nến để tụt 13.5 giá — trung bình 0.25 giá/nến. Đó là drift, không phải move.
- **Nghi phạm trong thuật toán:** ngưỡng "8× biên độ TB" (mục 11) quá lỏng ở phiên Á/sáng châu Âu thanh khoản mỏng, đúng như mục 12.1 tự nghi.

### 5. UA tại 4139.0 — nhãn duy nhất trong Phase B, đúng vai nhưng vô nghĩa
- **Thuật toán gắn:** UA tại 07:45, giá 4139.0, VSA 2.12× — vượt biên chính trên (4137.5) đúng **1.5 giá**.
- **Đúng phải là:** vượt 1.5 giá trên một range 12.1 giá là chạm biên, gọi UA là hợp lệ theo L3/L6 (không còn ST[B] — đúng). Nhưng cả Phase B 51 nến chỉ có **một** nhãn này thì phần "đọc effort↔result trong Phase B" (L9) thực tế là trống.
- **Nghi phạm trong thuật toán:** không có lỗi logic, chỉ là range quá nhỏ nên không có gì để đọc.

## Đạt
- Bỏ hẳn ST[B], dùng UA cho test nhẹ ở biên trên — đúng L6.
- Phase A kết thúc tại ST[A], đủ 3 lần đổi hướng SC→AR→ST[A] — đúng L2 về mặt trình tự.
- Phase C (6n) là phase ngắn nhất, Phase B (51n) dài nhất — đúng tỉ lệ L8/L9.
- LPSY[C] và LPSY[D] tách đúng vai trước/sau SOW, mỗi cái 1 điểm — đúng L7, không lặp lỗi kinh điển Ca #3 nguồn 4.pdf.
- Tên RE-DIST khớp L4 (origin SC, phá xuống).

## Cần hỏi người học
- Không có. Bài này sai ở gốc (climax không tồn tại), mọi thứ phía sau chỉ là hệ quả.
