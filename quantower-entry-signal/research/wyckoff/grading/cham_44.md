# Chấm bài #44 — Tích luỹ (ACC) · 2026-07-09 00:54 → 06:22 (328 nến M1)

**Điểm: 2/10** — cú SOS cuối cùng đọc rất đúng, nhưng **biên range vẽ sai vùng**: hai biên chính chỉ bao 9 giá trong khi vùng đấu giá thật rộng 26 giá, nên gần một nửa range nằm ngoài biên mà máy coi như không có chuyện gì. Phải vẽ lại range, không chỉ sửa nhãn.

## Lỗi (nặng → nhẹ)

### 1. Biên chính neo trên một dao động 14 nến, không bao được vùng đấu giá — luật vi phạm: L2, L3
- **Thuật toán gắn:** Phase A dài **14 nến** (00:54→01:07), biên chính 4079.2–4088.2 = **9.0 giá (0.22%)**; biên phụ 4065.9–4092.3 = 26.4 giá, tỷ lệ **2.93x**.
- **Đúng phải là:** vùng cân bằng thật của phiên này là **4066–4092**. AR bị chốt ngay ở nến **01:01** — chỉ 7 nến sau nhãn SC (01:00) — nên biên trên bị đóng đinh ở 4088.2 quá sớm. Phase A cần chờ nhịp bật thật (đỉnh 4091.7 lúc 02:14 trên ảnh).
- **Dấu hiệu quyết định trên chart:** tỷ lệ biên phụ/biên chính 2.93x tự nó đã tố cáo — biên phụ hai bên đều xa hơn biên chính, tức "cực trị mà một thế lực tạo ra" lớn gần gấp 3 vùng được coi là range. Nhìn ảnh, hai đường liền cam nằm gọn ở giữa đám nến chứ không ôm lấy nó.
- **Nghi phạm trong thuật toán:** AR = "swing pivot ngược đầu tiên xác nhận sau 5 nến, nhịp bật ≥1.5× ATR". Trên M1 phiên Á volume 3–45 lot, 1.5× ATR là ngưỡng gần như vô nghĩa → AR chốt ngay nhịp nảy đầu tiên. Cần thêm ràng buộc tương đối: AR phải ≥ một tỷ lệ độ dài MOVE, hoặc phải là pivot còn đứng vững sau N nến kế tiếp.

### 2. 130/130 nến đóng dưới biên chính dưới chỉ được ghi 1 nhãn mSOW — luật vi phạm: L5
- **Thuật toán gắn:** mSOW 04:44 tại 4065.9, toàn bộ đoạn nằm trong Phase B.
- **Đúng phải là:** giá đóng cửa dưới biên suốt hơn 2 giờ thì đó là cú phá **xuống** thật (hoặc chí ít là Shakeout lớn kéo dài), không phải một cú thăm dò lẻ.
- **Dấu hiệu quyết định trên chart:** đếm trên dữ liệu gốc, từ 02:50 đến 05:00 có **130/130 nến đóng cửa DƯỚI 4079.2**. Trên ảnh cả một mảng nến nằm hẳn dưới đường liền dưới.
- **Nghi phạm trong thuật toán:** lại là biên phụ tự nới (4065.9 do chính cú này tạo) + hệ quả của lỗi #1 (biên chính đặt quá cao nên giá "ngoài biên" là chuyện thường xuyên). Lỗi #6 của vòng v7 **chưa hết**.

### 3. mSOS 05:51 sai vai — luật vi phạm: mục 5.1 (định nghĩa mSOS)
- **Thuật toán gắn:** mSOS tại 4092.3 (05:51, VSA 2.07x), rồi SOS 06:00.
- **Đúng phải là:** mSOS nghĩa là "phá được rồi **thu hẳn vào trong range** rồi hướng sang biên đối diện". Trong 9 nến giữa 05:51 và 06:00 giá không hề thu vào trong range — nó chỉ đi ngang 4089–4092 rồi bung. Nến 05:51 là một phần của **chính cú phá SOS**, không phải cú phá thất bại.
- **Dấu hiệu quyết định trên chart:** hai nhãn mSOS và SOS dính sát nhau ở góc phải ảnh, cùng một đoạn tăng liền mạch.
- **Nghi phạm trong thuật toán:** hạ cấp mSOS chạy trước khi biết kết cục; điều kiện hạ cấp phải là "đóng cửa lùi hẳn qua **biên chính**", đúng như mốc 30 tick đã chốt cho Phase D.

### 4. Phase C (37 nến) dài hơn Phase D (12) và E (11) — luật vi phạm: L8
LPS[C] 05:23 tại 4078.3 (VSA 0.11x — test cạn cung, chọn điểm đúng tinh thần) nhưng đoạn C kéo 37 nến, thành phase dài thứ nhì. Hệ quả cửa sổ gán ngược 0.8× Phase B = 204 nến, máy lấy pivot xa thay vì nhịp test cuối.

### 5. MOVE trước climax sát sàn — luật vi phạm: L1 (biên)
17.4 giá / 39 nến / hiệu suất **0.37** (sàn 0.35). Nhìn ảnh, đoạn "move" này thực chất là giá lắc 4084–4099 rồi trôi xuống, không phải một đợt giảm dứt khoát. Ca này nằm đúng ranh giới "climax nổ khi giá đang đi ngang" mà L1 muốn loại. Ghi nhận là ca biên, chưa đủ chắc để bảo phải bỏ range.

## Đạt
- Nhãn SOS 06:00 neo **rất đúng**: VSA **8.08x**, thân 0.93, volume 989 — cây phá mạnh nhất cả range. Đây là bằng chứng vá "nhãn hồi tố về cây phá thật" hoạt động tốt.
- L4: origin SC + phá lên thật = **Tích luỹ** — tên đúng.
- L10: LPS[D] 06:07 tại 4097.8 hồi về giữ trên biên rồi đi tiếp lên 4120 — CBR đúng.
- L9: Phase B 255 nến, dài nhất.
- Chú thích er=0.94 "nhịp HIỆU QUẢ, không phải hấp thụ" — đúng dấu.

## Cần hỏi người học
- Khi biên phụ rộng gấp ~3 lần biên chính (như ca này) thì nên **vẽ lại biên chính theo cực trị thật**, hay giữ nguyên climax+AR và chấp nhận range mỏng? Guard hiện tại chỉ huỷ khi tỷ lệ >4.0x, nên ca 2.93x này lọt qua nhưng hình thì rõ ràng sai.
