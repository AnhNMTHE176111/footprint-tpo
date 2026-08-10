# Chấm bài #45 — Tích luỹ (ACC) · 2026-07-12 22:48 → 07-13 00:22 (93 nến M1)

**Điểm: 2/10** — cả range chỉ 93 nến mà nhét đủ A→E, trong đó Phase B chỉ 14 nến còn Phase C tới 37: hai luật tỷ lệ phase bị vi phạm cùng lúc. Đây là **nhiễu phiên mở cửa Chủ nhật**, không phải một vùng đấu giá thật — tôi sẽ không vẽ range ở đây.

## Lỗi (nặng → nhẹ)

### 1. Phase B (14 nến) ngắn hơn Phase C (37 nến) — luật vi phạm: L9 **và** L8 cùng lúc
- **Thuật toán gắn:** A=17 · B=14 · C=37 · D=25 · E=1.
- **Đúng phải là:** B phải dài nhất, C phải ngắn nhất. Ở đây C dài **gấp 2.6 lần** B, và B là phase ngắn thứ nhì cả range.
- **Dấu hiệu quyết định trên chart:** trên ảnh, ba vạch tím "Phase A / Phase B / Phase C" chen nhau trong chưa đầy 40 phút; đoạn được gọi Phase C (23:20→23:56) chính là đoạn giá bò lên từ 4077 tới 4088 — đó là hành vi xây nguyên nhân (Phase B), không phải một cú test cuối.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược Phase C nới lên 0.8× Phase B; nhưng khi Phase B ngắn (14 nến) thì cửa sổ vẫn cho phép LPS[C] ở 23:20 — cách SOS tới 37 nến, tức máy **không** kẹp Phase C vào cửa sổ đã tính. Cần trần cứng: Phase C ≤ min(Phase B, Phase D).

### 2. mSOS và SOS cách nhau 5 nến và **1 tick** — luật vi phạm: mục 5.1, L5
- **Thuật toán gắn:** mSOS 23:52 tại **4091.4** (VSA 1.08x), SOS 23:57 tại **4091.5** (VSA 2.79x).
- **Đúng phải là:** chỉ một nhãn SOS tại 23:57. Nến 23:52 là nến **đỏ** (O=4090.0 C=4089.3, volume 38 lot) chỉ chạm 4091.4 bằng bóng rồi đóng cửa xuống — không đủ tư cách gọi là một cú phá "có thật" theo định nghĩa mSOS ở v6.
- **Dấu hiệu quyết định trên chart:** hai nhãn dính vào nhau ở góc phải ảnh; chênh lệch giá 0.1 = **1 tick**. Đúng ca mà vòng chấm v6 đã bắt (bài cham_44 cũ) — **lỗi chưa được sửa**, ngưỡng 30 tick không chặn được vì nó áp cho việc "lùi hẳn qua biên", không áp cho khoảng cách mSOS↔SOS.
- **Nghi phạm trong thuật toán:** biên phụ trên bị nới bởi chính bóng nến 23:52 (4091.4), khiến nến đó bị hạ cấp mSOS rồi ngay sau đó cây thật vượt qua. Phải: (a) chỉ nới biên phụ bằng **giá đóng cửa** chứ không bằng bóng, hoặc (b) không phát nhãn mSOS/mSOW khi cú phá kế tiếp thành công trong vòng < 10 nến.

### 3. Range 93 nến với đủ 5 phase = nhiễu, không phải vùng đấu giá — luật vi phạm: tiêu chí "range quá vụn" (CHART_CASES, góp ý đổi khung)
- **Thuật toán gắn:** ACC hoàn chỉnh A→E, Phase E dài **1 nến**.
- **Đúng phải là:** đây là 1,5 giờ đầu phiên mở cửa Chủ nhật với volume 12–47 lot/nến. Một cấu trúc Wyckoff đủ 5 phase trong 93 nến M1 phải bị nghi ngay. Nếu muốn đọc vùng này thì phải lên M5/M15.
- **Dấu hiệu quyết định trên chart:** Phase E dài đúng **1 nến** — giá không hề "rời range đi tìm vùng giá mới": ngay sau 00:22 giá quay đầu rơi về 4071 (thấy rõ nửa phải ảnh), tức cú phá lên **thất bại** chỉ vài phút sau khi range được đặt tên ACC.
- **Nghi phạm trong thuật toán:** đích Phase E = 1.0× chiều cao range, mà chiều cao chỉ **12.0 giá** → chỉ cần đi 12 giá là "xong cấu trúc". Với range mỏng, mốc này quá dễ đạt. Nên đặt sàn tuyệt đối (vd ≥ 1.5× ATR ngày) cho đích Phase E, hoặc sàn độ dài range.

### 4. AR chốt trên nến volume 20 lot — luật vi phạm: L2 (AR phải là cú bật ngược thật)
AR 22:52 tại 4088.8 với **VSA 0.36x** — nhịp bật không có nỗ lực nào đứng sau, chỉ 4 nến sau climax. Phiếu không gắn cảnh báo "AR (yếu)" dù đúng ca đó. Effort ↔ Result: climax bán 359 lot mà cú hồi chỉ 20 lot — biên trên dựng trên hư không.

## Đạt
- L1: MOVE giảm 24.2 giá / 47 nến, hiệu suất 0.37; kiểm dữ liệu gốc: phiên trước nghỉ từ 07-10 21:00 tới 07-12 22:00 (49 giờ) và cửa sổ đo **dừng đúng tại khe**, không bắc qua cuối tuần — vá #7 của v6 hoạt động.
- Climax SC 22:48 là cây thật đẹp: VSA **7.19x**, biên độ 7.9 giá, đúng đáy cửa sổ, nến đỏ chặn move. Nhãn neo đúng nến, không lệch.
- **L2 — ST[A] lần này ĐÚNG:** 23:04 tại 4075.8, thấp hơn mức climax 4076.8 → test đúng vùng SC và tạo biên phụ dưới hợp lệ. Đây là bài duy nhất trong lô 41–45 đặt ST[A] đúng chỗ.
- L3: biên phụ mỗi bên 1 cái, tỷ lệ 1.30x — sạch.
- L4: origin SC + phá lên = **Tích luỹ**, tên khớp hướng phá.
- Chú thích er=0.37 ghi "nhịp HIỆU QUẢ, không phải hấp thụ" — đúng dấu.
