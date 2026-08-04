# Chấm bài #38 — Tích lũy (ACC) · 2026-07-09 00:54 → 06:22 (328 nến M1)

**Điểm: 6/10** — vẽ đúng khung, sửa vài nhãn. Đây là bài khá nhất trong lô: climax thật, tên range đúng, cú phá thật. Lỗi còn lại nằm ở **biên chính quá hẹp so với vùng giá thật** và **Phase C gán ngược lệch chỗ**.

## Lỗi (nặng → nhẹ)

### 1. Biên chính 9.0 giá nhưng vùng đấu giá thật là 28.9 giá — luật vi phạm: L3
- **Thuật toán gắn:** biên chính 4079.2–4088.2 = **9.0 giá** (0.22%); biên phụ 4063.4–4092.3 = **28.9 giá**, gấp **3.2 lần**.
- **Đúng phải là:** AR chốt tại 4088.2 chỉ 7 nến sau climax (00:54 → 01:01) — đó là một cú bật rất nông, và ST[A] tại 4076.1 đã **thấp hơn cả mức climax 4079.2**. Nghĩa là ngay trong Phase A, giá đã vượt biên chính dưới. Vùng cân bằng thật của phiên này là **4063–4092** (nhìn ảnh: giá đi ngang trong dải đó suốt 264 nến Phase B). Biên chính đang nằm ở nửa trên của vùng thật.
- **Dấu hiệu quyết định trên chart:** trên ảnh, hai đường cam **nét liền** cắt ngang qua thân đám nến Phase B, còn hai đường **nét đứt** mới là cái bao trọn dao động. Đáy 4063.4 (03:26) và đỉnh 4092.3 (05:51) đều là những mức giá được test rõ.
- **Nghi phạm trong thuật toán:** AR là "swing pivot ngược đầu tiên được xác nhận, 5 nến không cực trị mới + ≥1.5× biên độ TB" (mục 4.1). Trong phiên Á thanh khoản mỏng, biên độ TB nhỏ nên **1.5× biên độ TB rất dễ đạt** → AR bị chốt vào cú bật 9 giá đầu tiên thay vì cú bật thật. Nhãn "AR (yếu)" đã có trong spec nhưng ở đây AR cách climax 7 nến nên không bị đánh dấu yếu — điều kiện "1–2 nến sát climax" quá hẹp.

### 2. ST[A] xuyên qua mức climax mà không tạo biên phụ đúng lúc — luật vi phạm: L3
- **Thuật toán gắn:** ST[A] tại 01:07, giá **4076.1**, tức **dưới mức climax 4079.2 đúng 3.1 giá**.
- **Đúng phải là:** theo L3, "ST[A] vượt qua mức climax cũng tạo biên phụ". Vậy biên phụ dưới lẽ ra phải là **4076.1 ngay từ 01:07**, rồi mới bị cú 03:26 nới ra 4063.4. Trên phiếu số liệu chỉ thấy biên phụ cuối cùng nên không truy được, nhưng vấn đề thật là khác: ST[A] phá mức climax ngay trong Phase A là dấu hiệu **AR chốt sai** (lỗi #1), không phải một ST hợp lệ. Một cú "test lại vùng climax" mà đi xuyên qua nó thì cái được test không phải là biên.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu — ST[A] 4076.1 < SC 4079.2. Trên ảnh, chấm ST[A] nằm rõ **dưới** đường cam nét liền dưới.
- **Nghi phạm trong thuật toán:** mục 4.2 có trần "nhịp hồi vượt mức climax hơn **một lần chiều cao range** thì bỏ ứng viên". Chiều cao range = 9.0 giá, ST[A] vượt 3.1 giá = 34% → lọt. Trần 100% quá rộng; ST[A] mà vượt mức climax là đã đáng nghi, nên trần cỡ 20-30% hợp lý hơn — hoặc tốt hơn: khi ST[A] vượt climax thì **dời mức climax** xuống đó và coi Phase A chưa xong.

### 3. LPS[C] gán ở 4073.8 — dưới cả biên chính dưới, không phải test biên — luật vi phạm: L8
- **Thuật toán gắn:** LPS[C] tại 05:32, giá **4073.8** — thấp hơn biên chính dưới (4079.2) **5.4 giá**, tức nằm dưới đáy range chính.
- **Đúng phải là:** Phase C phải là "tín hiệu đầu tiên giá ở biên này bắt đầu phá biên kia". Cú test thật trước SOS là nhịp lùi về **4079-4081** lúc ~05:20 (nhìn ảnh: giá lùi về đúng đường cam dưới rồi mới bật). LPS[C] 4073.8 là một cú thọc nông ngoài biên — nếu muốn gọi tên thì đó gần với một **Spring nhỏ** hơn là LPS[C] (nó phá biên chính dưới rồi rút vào nhanh).
- **Dấu hiệu quyết định trên chart:** VSA của LPS[C] chỉ **0.85×**, thân 0.42 — volume co lại, đúng tính chất test. Nhưng vị trí 4073.8 nằm giữa biên chính dưới (4079.2) và biên phụ dưới (4063.4), tức không chạm biên nào.
- **Nghi phạm trong thuật toán:** vẫn là "nhìn ngược 60 nến lấy đáy sâu nhất" (mục 6). Đáy sâu nhất trong 60 nến trước SOS không nhất thiết là nhịp test biên — cần ràng buộc "trong dung sai của một biên" hoặc "là pivot cuối cùng trước cú phá", không phải cực trị thô.

### 4. mSOS 05:51 nằm sau LPS[C] 05:32 nhưng bị ghi Phase B — thứ tự phase lộn — luật vi phạm: L8
- **Thuật toán gắn:** LPS[C] 05:32 (Phase C) → mSOS 05:51 (**Phase B**) → SOS 06:04 (Phase D). Bảng phase ghi C = 05:32–06:03.
- **Đúng phải là:** mSOS ở 05:51 nằm **trong khoảng thời gian Phase C** (05:32–06:03) nhưng cột Phase của nó ghi "B". Một sự kiện không thể thuộc Phase B khi timeline chỗ đó là Phase C. Nếu mSOS 4092.3 (đúng bằng biên phụ trên) là cú thăm dò thất bại thì nó phải nằm **trước** Phase C; nếu nó nằm trong Phase C thì nó chính là bước đầu của cú phá, phải gọi khác.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu — cột Phase của mSOS ghi "B" trong khi Phase C = 05:32→06:03. Đây là lỗi ghi nhãn phase, đọc trực tiếp từ bảng.
- **Nghi phạm trong thuật toán:** phase của sự kiện được gán **tại thời điểm phát sinh** (lúc đó máy đang ở state B vì Phase C mới được gán ngược sau này), rồi khi gán ngược Phase C thì **không cập nhật lại phase của các sự kiện đã nằm trong dải mới**. Sửa: sau khi gán ngược Phase C, quét lại mọi sự kiện trong dải và gán lại phase.

### 5. SOS neo vào cây VSA 0.75× — luật vi phạm: mục 8 chấm (Effort vs Result)
- **Thuật toán gắn:** SOS tại 06:04, giá 4102.4, **VSA 0.75×**, thân 0.69.
- **Đúng phải là:** cú phá thật ở đây là cây **05:53-05:55** (nhìn panel volume: thanh vàng **cao nhất toàn chart** nằm ngay chỗ giá bứt từ 4092 lên ~4100). SOS phải neo vào cây đó, không phải cây 06:04 với volume dưới trung bình. Lỗi hệ thống B của v4 (nhãn rơi vào nến xác nhận thứ 3, VSA 0.30–0.69×) **vẫn còn ở bài này** — 0.75× nằm đúng trong dải đó.
- **Dấu hiệu quyết định trên chart:** thanh volume vàng cao nhất cả 328 nến nằm ở ~05:53; nhãn SOS lại đặt cách đó 11 nến về sau, trên một nến volume 0.75×.
- **Nghi phạm trong thuật toán:** mục 5.1 nói nhãn SOS/SOW đặt **hồi tố vào cây VSA cao nhất trong đoạn, đúng hướng, đóng cửa vượt biên**. Điều kiện "đóng cửa vượt **biên phụ** (4092.3)" đã loại cây 05:53 nếu nó đóng cửa dưới 4092.3 — nên máy đành lấy cây sau. Cần cho phép hồi tố tới cây **đóng cửa vượt biên chính** khi cây đó là cây khối lượng vượt trội, hoặc mở rộng cửa sổ hồi tố về trước điểm chốt.

## Đạt
- Climax thật: SC 00:54 VSA **2.69×**, biên độ 3.3 giá, thân 0.82, và là đáy của cụm — đúng L1 về chất lượng cây climax (khác hẳn bài #36, #37).
- Climax **chặn** move thật: MOVE 17.4 giá / 39 nến, hiệu suất 0.37, và giá không đi thấp hơn nữa ngay sau đó (nến +1 đã bật lên 2.4 giá với VSA 2.60×) — đúng L1.
- Tên range ACC khớp L4: origin SC + phá lên thật = Tích luỹ. Đúng.
- Tỉ lệ phase đẹp: A=14 · B=**264** · C=32 · D=8 · E=11. Phase B dài nhất (L9), Phase C ngắn (L8), Phase E không còn bị ép 1 nến (lỗi J v4 đã hết).
- LPS[C] / LPS[D] tách đúng vai trước/sau SOS, mỗi cái đúng 1 điểm — đúng L7.
- mSOW 04:44 (VSA **3.67×**, thân 0.74) ở lại Phase B thay vì bị hạ thành "DA test nhẹ" — đúng ý lỗi H v4, đã hết.
- Mỗi bên đúng 1 biên phụ — đúng L3.
- LPS[D] 4097.8 nằm **trên** biên vừa phá, giá sau đó tiếp tục lên 4123 — đúng CBR của L10.

## Cần hỏi người học
- Khi ST[A] đóng cửa **vượt qua** mức climax (ở đây 3.1 giá / 34% chiều cao range), nên (a) chấp nhận và mở biên phụ, hay (b) coi là Phase A chưa xong và dời mức climax xuống? Spec hiện chọn (a) với trần 100% chiều cao — tôi nghiêng về (b) nhưng đây là chỗ luật chưa phân xử được.
