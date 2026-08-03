# Chấm bài #25 — Tái phân phối (RE-DIST) · 2026-06-15 12:17 → 20:52 (515 nến M1)

**Điểm: 3/10** — Hướng đọc cuối cùng đúng, nhưng bài này **không thể dùng để dạy**: nhãn AR nằm cách biên chính trên **20.7 giá**, Phase A ôm trọn một leg tăng 46 giá, và cú phá thật bị bỏ qua **145 nến** trước khi máy mới gắn SOW.

## Lỗi (nặng → nhẹ)

### 1. Nhãn AR không khớp biên chính trên — lệch 20.7 giá — luật vi phạm: L3 (biên chính = mức climax + mức AR)
- **Thuật toán gắn:** sự kiện **AR @4370.8 (12:57)**, nhưng đường nét liền vẽ ở **biên chính trên 4391.5**.
- **Đúng phải là:** đỉnh đối diện thật của Phase A là **4391.5 lúc 14:06** — máy đã dời *biên* lên đó nhưng **không dời nhãn AR**. Người đọc chart thấy hai con số khác nhau cho cùng một mốc, không thể đối chiếu được gì.
- **Dấu hiệu quyết định trên chart:** chấm AR nằm lơ lửng **giữa** range, dưới đường liền trên đúng 20.7 giá.
- **Nghi phạm trong thuật toán:** trong state `A_st`, dòng `r.ar_i, r.ar_price = i, b['hi']` cập nhật biên khi AR bị đẩy cao hơn, nhưng sự kiện AR đã `add_event()` từ state `A` **không được cập nhật/xoá**. Cùng bug này làm bài #23 lệch 1.0 giá — ở đây lệch 20.7 giá vì AR bị đẩy tới 3 lần.

### 2. "Phase A" ôm trọn một leg tăng 46 giá — nguyên nhân nhỏ hơn hẳn kết quả — luật vi phạm: L1 + THEORY §2.2 (luật Nhân–Quả)
- **Thuật toán gắn:** MOVE trước climax **23.4 giá / 35 nến**; biên chính **46.0 giá (1.06% giá — cao nhất 5 bài)**; Phase A **166 nến**.
- **Đúng phải là:** cú bật ngược sau climax bằng **196% độ dài move** thì nó không còn là một Automatic Rally *chặn* move đó — nó là một xu hướng tăng mới. Một TR cao gấp đôi cái move nó được cho là đang tiêu hoá thì "nguyên nhân" không đỡ được "kết quả": range này phải bị loại ở cửa vào, hoặc phải mở lại range từ đỉnh 4391.5.
- **Nghi phạm trong thuật toán:** `AR_MIN_RETRACE_OF_MOVE = 0.30` chỉ là **SÀN**, không có **TRẦN** (vd loại nếu AR > 100–120% độ dài move).

### 3. SOW gắn muộn 145 nến so với cú phá thật — luật vi phạm: L5 + L10
- **Thuật toán gắn:** SOW **20:27 @4334.5**, VSA 0.71x, v=**31 lot**.
- **Đúng phải là:** cú phá thật là **18:00–18:02** (18:01 v=166/2.63x, 18:02 v=167/2.46x). Bằng chứng: từ 17:36 tới 20:27 có **129/172 nến (75%) đóng cửa DƯỚI biên chính dưới 4345.5** — theo L5, "đóng cửa hẳn ngoài biên và các nến sau đủ mạnh giữ nó ở ngoài" chính là phá THẬT. Máy lại giữ Phase C tới 20:02 rồi gắn SOW ở một nến 31 lot, thấp hơn cú phá thật 6 giá.
- **Nghi phạm trong thuật toán:** SOS/SOW phải bứt qua **biên phụ**, nhưng biên phụ dưới (4339.1) do **chính cú Shakeout** nới ra → mỗi cú thăm dò lại tự đẩy ngưỡng phá xuống thấp hơn, thành một vòng tự phủ định. Cộng thêm: không có **sàn khối lượng tuyệt đối** cho nến phá (LOI 10 đang chờ vá), nên nhãn SOW rơi được vào nến 31 lot.

### 4. Chuỗi C→B→C→B, Phase C 145 nến, 2 LPS[C] — luật vi phạm: L8 + L7
- **Thuật toán gắn:** C 24 nến → B 1 nến → **C 121 nến** → B 24 nến → D 26 nến; hai nhãn **LPS[C]** (17:42 @4343.0 và 19:42 @4341.1).
- **Đúng phải là:** L8 nói Phase C là phase **ngắn nhất**; ở đây tổng 145 nến (28% range) và đoạn thứ hai dài **đúng 121 nến = trần `SHOCK_MAX_WAIT` (120)**, nghĩa là nó kết thúc vì hết giờ chờ chứ không vì đọc được gì. L7 chỉ cho **1 điểm** LPS[C] — ở đây có 2.
- **Dấu hiệu quyết định trên chart:** dải Phase C bị cắt vụn bởi hai vạch tím sát nhau (C 24n / B 1n), một cách trình bày không mang thông tin nào.

### 5. "Spring (thất bại)" thực chất là một test cạn cung — luật vi phạm: L6 (bỏ hẳn ST[B]) + L5
- **Thuật toán gắn:** Spring (thất bại) 17:37 @4343.0 — chọc **2.5 giá** dưới biên, v=**74 lot (VSA 0.53x = nửa trung bình)**, thân 0.38, đóng lại trong range.
- **Đúng phải là:** một cú chọc 2.5 giá với **nửa** khối lượng trung bình là test cạn cung ở biên dưới — theo L6 thì **không ghi nhãn gì** (đó chính là ST[B] đã bị bỏ). Gắn "Spring" ở đây mở Phase C sớm và sinh ra toàn bộ chuỗi C→B→C ở lỗi 4.
- **Nghi phạm trong thuật toán:** ngưỡng "thăm dò NHẸ" = **< 15 tick** (1.5 giá) quá nhỏ với vàng — biên độ nến trung bình vùng này đã 2–3 giá, nên gần như **mọi** cú chọc biên đều bị xếp là "thăm dò THẬT" → Spring/Shakeout.

### 6. LPS[C] 17:42 trùng đúng giá của "Spring" 17:37 — nhãn dư, nhẹ — mục chấm 9
- Hai nhãn cùng giá **4343.0**, cách nhau 5 nến. Một cú rũ và cái test của chính nó không nên chiếm hai nhãn ở cùng một mức giá.

### 7. ST[A] hồi đúng 40.2% — vừa sát ngưỡng, không phải test vùng climax — luật vi phạm: L2, mục chấm 2
- **Thuật toán gắn:** ST[A] 15:02 @**4373.0**; ngưỡng yêu cầu là 40% của 46.0 giá → mốc 4373.1. Đạt nhờ **0.1 giá**.
- **Đúng phải là:** 4373.0 nằm ở **60% chiều cao range**, cách climax 27.5 giá, và sau nó giá còn tăng lại tới **4382.8 (15:45)** → đây là một nhịp ngọ nguậy giữa range, không phải cú quay về bị chặn ở vùng climax. Test thật của vùng SC là **17:36 (4343.2)**.

## Đạt
- **L1 (phần cây climax):** SC VSA 3.14x, thân 0.95, đóng cửa ngay tại đáy nến — đúng là một cây bán tháo chặn nhịp giảm.
- **L4:** tên **Tái phân phối** khớp kết cục — sau khi range đóng, giá trôi tiếp xuống **4326.7 (22:28)** và đỉnh cao nhất 8 giờ sau chỉ 4346.8, tức **không lấy lại được biên dưới 4345.5**.
- **L3 (quy tắc biên phụ):** đúng 1 biên phụ mỗi bên, giữ cực trị xa nhất (4339.1) — cú Spring nông hơn đã bị bỏ đúng luật.
- **L9:** Phase B tổng 179 nến — vẫn là phase dài nhất.
- **Phase E:** máy **không** ép chốt Phase E khi cú phá chỉ đi 10.5/46.0 giá (23% chiều cao range) — đúng tinh thần bản vá CR-K.
