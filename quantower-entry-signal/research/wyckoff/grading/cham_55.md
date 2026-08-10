# Chấm bài #55 — Chưa rõ (BCLX) (DIST?) · 2026-07-22 13:33 → 20:04 (391 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây theo cách này: hai biên chính chỉ ôm 8.9 giá trong một vùng đấu giá thật rộng 35 giá, nên toàn bộ chuỗi phase phía sau đều đo trên một cái khung sai.

## Lỗi (nặng → nhẹ)

### 1. Biên chính không ôm được vùng đấu giá — luật vi phạm: L3 + L1
- **Thuật toán gắn:** biên chính 4143.2–4152.1 = **8.9 giá**; biên phụ 4133.9–4168.8 = **34.9 giá**, tỷ lệ **3.92×**.
- **Đúng phải là:** biên chính phải là mức climax + mức AR của một cú bật ngược THẬT. Ở đây AR nằm cách climax đúng **2 nến** (13:33 → 13:35), hồi vỏn vẹn 8.9 giá sau một MOVE dài 39 giá — đó là râu nhiễu trong cụm climax, không phải "lực đẩy tự động". Phải chờ cú bật ngược thật (giá về 4133–4136 lúc 13:5x, hoặc nhịp lùi lớn sau đó) mới có biên dưới.
- **Dấu hiệu quyết định trên chart:** nhãn máy tự ghi **"AR (yếu)"** ngay trên chart, VSA nến AR = 1.32×, thân 0.42. Suốt 391 nến giá đi lại giữa 4133.9 và 4168.8; hai nét liền cam chỉ chiếm **25%** dải đó và nằm lệch hẳn về giữa.
- **Nghi phạm trong thuật toán:** guard tỷ lệ biên phụ/biên chính **4.0×** — ca này đo 3.92×, lách qua đúng 0.08. Lỗi "guard 4.0× quá lỏng với range hẹp" đã ghi ở mục 13.1b tái xuất nguyên vẹn. Kèm theo: nhãn cảnh báo "AR (yếu)" chỉ hiển thị, **không** chặn.

### 2. ST[A] không phải test mà là giá đi tiếp — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:48 tại **4156.5**, tức **cao hơn climax 4152.1 tận 4.4 giá**.
- **Đúng phải là:** ST[A] là cú quay về phía climax rồi **bị chặn** — nó phải ở dưới hoặc sát mức climax. Ở đây giá vượt qua climax rồi chạy tiếp lên 4168.8. Nghĩa là cây BCLX **không chặn được move** → theo L1 ứng viên này lẽ ra bị bỏ ngay từ Phase A.
- **Dấu hiệu quyết định trên chart:** đo retrace từ AR = (4156.5−4143.2)/8.9 = **1.49 = 149%** khoảng AR↔climax. Sau ST[A] giá còn lên tiếp 12 giá nữa (đỉnh 4168.8 lúc 15:49).
- **Nghi phạm trong thuật toán:** ngưỡng mới `STA_MIN_AR_FRAC=0.55` là **sàn**, không chặn được ca vượt trần. Trần duy nhất đang có là "ST[A] vượt climax ≤ **1.0× chiều cao range**" — với range 8.9 giá thì được phép vượt 8.9 giá, quá rộng. Đề xuất siết trần xuống ~0.15–0.2× chiều cao, và cho guard "climax không chặn được move" (4× ATR) chạy cả sau ST[A].

### 3. Phase D mồ côi — không có SOS/SOW nào trong đó — luật vi phạm: L10
- **Thuật toán gắn:** Phase D 19:54 → 20:04 (11 nến), sự kiện duy nhất là LPSY[D] 4140.0. Nhãn phá vỡ tại đúng mốc mở Phase D (19:54, VSA **3.97×**) lại mang tên **mSOW (provisional)**.
- **Đúng phải là:** Phase D chỉ tồn tại **sau** một SOW được xác nhận. Cú phá đã bị hạ cấp thành mSOW thì đoạn Phase D phải bị xoá và dải phase trả về B — đúng như v5 đã làm với Phase C hết hạn.
- **Dấu hiệu quyết định trên chart:** cả Phase D không có một chấm SOW nào; LPSY[D] ở 4140.0 nằm **trong** vùng biên phụ, chẳng "giữ được ngoài biên" gì cả.
- **Nghi phạm trong thuật toán:** nhánh hạ cấp SOW→mSOW không dọn đoạn phase D (biến thể của lỗi #6 vòng v6: "nhãn mồ côi còn treo lại").

### 4. Phase C dài gấp 5,5 lần Phase D — luật vi phạm: L8
- **Thuật toán gắn:** A=16 · B=305 · **C=60** · D=11.
- **Đúng phải là:** C là phase NGẮN NHẤT. 60 nến C so với 11 nến D là ngược hẳn.
- **Nghi phạm trong thuật toán:** sau khi v7.1 bỏ ràng buộc "đúng nửa range", Phase C gán ngược không còn trần tuyệt đối. Cần chốt `len(C) ≤ min(len(B), len(D))` như 13.1b đã đề xuất mà chưa làm.

### 5. Spam nhãn minor — luật vi phạm: mục 9 (nhãn dư)
- 2 mSOS + 3 mSOW trên một range, trong đó mSOS 16:06 đặt trên nến **VSA 0.31×, thân 0.33** — nến đó không phá gì cả. Cây phá thật của nhịp đó là 15:49 (VSA 3.07×) đã mang nhãn riêng rồi.

## Đạt
- Điều kiện mở range về MOVE: 39 giá / 37 nến / hiệu suất **0.72** — một move tăng thật, không phải đi ngang (L1 phần MOVE đạt).
- Nhãn BCLX neo đúng nến mở range (13:33), đúng đỉnh cụm, VSA 3.89× — không dính lỗi nhãn cụm climax.
- Phase B là phase dài nhất (305/391 nến) — L9 đạt.
