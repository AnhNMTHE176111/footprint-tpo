# Chấm bài #33 — Tích lũy (ACC) · 2026-07-06 12:41 → 18:23 (342 nến M1)

**Điểm: 4/10** — Vùng đấu giá là thật và tên range đúng, nhưng **Spring bị gắn oan chữ "thất bại"** dù nó đã đi hết sang biên đối diện, Phase C phình 121 nến, cú phá thật thì **không có Phase C nào**, và SOS neo vào nến 64 lot của phiên chết.

## Lỗi (nặng → nhẹ)

### 1. Spring 14:44 bị gắn "(thất bại)" trong khi nó đã VƯỢT biên đối diện — luật vi phạm: THEORY §5 (mục tiêu tối thiểu của cú rũ) + L8
- **Thuật toán gắn:** `Spring (thất bại)`, status `failed`, tại 14:44 giá 4140.6 (VSA **5.13x**, thân 0.58).
- **Đúng phải là:** **Spring xác nhận**. Mục tiêu tối thiểu của một cú rũ là "đi đến đầu đối diện của cấu trúc" — giá từ 4140.6 leo tới **4164.0 (15:31)**, tức **vượt cả biên chính trên 4162.6**, tiến độ ≈ **106%** (ngưỡng cần chỉ 50%).
- **Dấu hiệu quyết định trên chart:** cây Spring là thanh khối lượng cao nhất nửa trái panel (676 lot / VSA 5.13x), và cụm nến 15:25-15:35 chạm đúng đường nét liền 4162.6.
- **Nghi phạm trong thuật toán:** trong state `C_pending`, nhánh `if (i - shock['start_i']) > SHOCK_MAX_WAIT` được kiểm **TRƯỚC** và ghi đè `status` thành `'failed'` **kể cả khi đã là `'confirmed'`**. Phải: đã confirmed thì không được hạ xuống failed; timeout chỉ nên đóng Phase C, không phủ định cú rũ.

### 2. Cú phá thật (SOS 17:58) không có Phase C — chuỗi phase A-B-C-B-D — luật vi phạm: L8 (case khó: "có Phase D rồi mới xác định được Phase C")
- **Thuật toán gắn:** A 66 · B 57 · **C 121** · B 73 · D 26 — Phase C duy nhất thuộc cú Spring đã chết **3 giờ 14 phút** trước cú phá.
- **Đúng phải là:** gán ngược Phase C ngay trước SOS (nhịp test cuối trong vùng 17:20-17:55), hoặc — đọc đúng hơn — công nhận Spring 14:44 là Phase C **hợp lệ** rồi coi đoạn 16:45→17:57 là Phase D kéo dài. Cách nào cũng được, nhưng không được để cú phá vỡ đứng trơ không có Phase C.
- **Dấu hiệu quyết định trên chart:** dải phase trên ảnh đọc thành A→B→C→B→D, thiếu hẳn một mốc C ở khu vực SOS.
- **Nghi phạm trong thuật toán:** `_fire_break()` chỉ gọi `_retro_phase_c()` khi `not any(p[0] == 'C' for p in r.phases)`. Range đã từng có Phase C (dù đã thất bại) → guard chặn, không gán ngược nữa.

### 3. SOS neo vào nến 64 lot; cây khối lượng thật ở biên lại là cây BÁN — luật vi phạm: mục 8 (Effort vs Result) + L10
- **Thuật toán gắn:** SOS 17:58, giá 4172.2, VSA 1.90x — nhưng khối lượng tuyệt đối chỉ **64 lot**, trong khi trong range giờ Mỹ các nến bình thường 100-600 lot.
- **Đúng phải là:** giá đã ở **trên** biên phụ 4168.1 liên tục từ **17:24**; cú đẩy có khối lượng thật là 17:24-17:28 (118-161 lot, VSA ~2x). Quan trọng hơn: nến **17:29 có 622 lot (VSA 6.18x)** là một nến **GIẢM** kéo giá về 4167.5, tức **quay lại dưới biên** — đó là "nỗ lực lớn, kết quả nghịch" tại đúng mức phá vỡ, cảnh báo cung xuất hiện. Bài bỏ qua hoàn toàn tín hiệu này.
- **Dấu hiệu quyết định trên chart:** thanh vàng cao gần nhất nửa phải panel khối lượng nằm ở 17:29 và là thanh **đỏ**; chấm SOS thì đứng ở chỗ khối lượng gần như bằng 0.
- **Nghi phạm trong thuật toán:** SOS/SOW bắn theo `BREAK_HOLD_BARS`/`BREAK_MAX_WAIT` và stamp tại nến xác nhận; VSA lại chuẩn hoá theo TB 20 nến nên trong phiên chết (18h UTC) một nến 64 lot vẫn "1.90x". Cần thêm sàn khối lượng **tuyệt đối** (so với TB của cả range, không phải 20 nến gần nhất).

### 4. Nhãn AR (4160.7) không trùng biên chính trên (4162.6) — luật vi phạm: L3
- **Thuật toán gắn:** AR tại 13:08 giá 4160.7; biên chính trên vẽ ở **4162.6**.
- **Đúng phải là:** L3 định nghĩa biên chính = **mức climax + mức AR**. Hai số phải bằng nhau; ở đây lệch **1.9 giá**.
- **Dấu hiệu quyết định trên chart:** chấm AR nằm rõ ràng **dưới** đường nét liền màu cam phía trên.
- **Nghi phạm trong thuật toán:** trong state `A_st`, khi giá tạo cực trị mới thì `r.ar_i, r.ar_price` được **dời**, nhưng **event AR đã `add_event()` từ state A không được cập nhật**. `r.solid_high` lấy `ar_price` mới → nhãn và biên lệch nhau. (Lỗi này lặp lại ở bài #34.)

### 5. ST[A] dừng đúng giữa range, không test vùng SC — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:46 giá 4153.7 (hồi **53%** chiều cao 4145.8-4162.6; điểm giữa range = 4154.2).
- **Đúng phải là:** ST[A] phải là cú **test lại vùng climax**. Test thật xảy ra ở **14:07-14:08** (low 4146.0 rồi 4145.8 — chạm đúng mức SC, VSA 2.61x). ST[A] gắn ở 13:46 chỉ là một nhịp ngọ nguậy giữa range, và ngay sau nó giá còn đi xuống thêm **8 giá**.
- **Dấu hiệu quyết định trên chart:** chấm ST[A] treo lơ lửng giữa hai đường nét liền.
- **Nghi phạm trong thuật toán:** `STA_MIN_RETRACE = 0.40` + `STA_CONFIRM_BARS = 5` quá lỏng cho M1. Ca #31 (ST[A] hồi 87%) cho thấy ngưỡng ~0.7 mới ra đúng vai.

### 6. Mức SC không phải đáy thật — L3 (lặp lỗi của bài #31)
- SC = 4145.8 (12:41) nhưng nến **kế tiếp** đã có L = 4144.1, nến +2 L = 4143.3. Biên chính dưới bị phá ngay nến sau khi lập.

### 7. Phase C 121 nến > Phase B 57 nến — L8 + L9
- Cùng nguyên nhân với bài #32: `SHOCK_MAX_WAIT = 120` biến **cửa sổ chờ** thành **độ dài phase**.

## Đạt
- **L1:** MOVE giảm 26.4 giá / 74 nến / hiệu suất 0.41 bị cây VSA 3.27x chặn — điều kiện CẦN thoả rõ.
- **L5 — phân loại Spring vs Shakeout đúng:** giá phá xuống ở 14:44 và đóng cửa quay lại trên 4145.8 ở **14:48 = 4 nến** → đúng là Spring, không phải Shakeout.
- **CHART_CASES lỗi #6 (điểm khó nhất):** Spring 4140.6 **đúng là mức thấp nhất toàn TR** — đúng yêu cầu tường minh nhất của giảng viên trong nguồn 2.pdf.
- **L4:** origin SC + phá lên = Tích luỹ. Đúng.
- **L3 (biên phụ) + L7:** mỗi bên 1 biên phụ, UA giữ đúng 1 cái ở cực trị (4168.1), LPS[D] chỉ 1 điểm.
- Chuỗi UA (16:58, test đỉnh trong Phase B) → SOS đúng với THEORY §5: test ở đỉnh mà không chạm lại đáy = dấu hiệu sức mạnh, có thể bứt phá **không cần** Spring mới.

## Cần hỏi người học
- Khi một Spring đã đạt biên đối diện (như ca này) nhưng cấu trúc còn lượn thêm 3 giờ mới phá thật: giữ **một** Phase C ở Spring và coi phần sau là Phase D dài, hay đóng Phase C rồi **gán ngược một Phase C thứ hai** ngay trước SOS?
