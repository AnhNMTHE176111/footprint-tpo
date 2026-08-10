# Chấm bài #16 — Tái phân phối (RE-DIST) · 2026-05-07 16:19 → 22:06 (189 nến M1)

**Điểm: 4/10** — Bài khá nhất về khung: mở range đúng, tên đúng, tỉ lệ phase đúng. Nhưng mất hẳn cú rũ Phase C thật, và nhãn SOW đặt vào cây chỉ hơn biên chính 1 giá trong khi biên phụ nằm cách đó 16 giá.

## Lỗi (nặng → nhẹ)

### 1. Cú rũ thật ở 17:25 bị hạ thành mSOW → range mất Phase C đúng chỗ — luật vi phạm: L5 + bảng mục 5.1
- **Thuật toán gắn:** mSOW 17:25 tại 4747.7, VSA **7.69x**.
- **Đúng phải là:** cú này thọc xuống tận **4734.0** (chính nó tạo biên phụ dưới), tức sâu **16 giá dưới biên chính** = 87% chiều cao range, rồi bật hẳn trở lại vào trong range và ở lại đó suốt 3 tiếng. Đủ cả 3 điều kiện của bảng 5.1 (vượt biên phụ + mạnh + sâu nhất range) → phải là **Shakeout** (lùng bùng ngoài biên >4 nến, không phải Spring), và Phase C phải đặt tại đây.
- **Dấu hiệu quyết định trên chart:** trên panel volume, cụm 17:21-17:30 là cụm volume cao nhất toàn range (cây vàng cao nhất ảnh). Effort lớn nhất của cả range mà bị dán nhãn "minor".
- **Nghi phạm:** điều kiện "vượt biên phụ" — tại thời điểm 17:25 biên phụ dưới còn CHƯA tồn tại (chính cú này tạo ra), nên phép so `exceeded_outer` không thoả. Đây đúng là gốc rễ "biên phụ nới trước, so sau" mà 13.1c mới chỉ sửa cho nhánh decisive/outside, **chưa sửa cho nhánh phân loại cú rũ**.

### 2. SOW đặt tại cây chỉ vượt biên chính 1.0 giá, không chạm biên phụ — luật vi phạm: L3
- **Thuật toán gắn:** SOW 20:43 tại **4749.0**, VSA 2.97x. Biên chính dưới 4750.0, biên phụ dưới **4734.0**.
- **Đúng phải là:** L3 chốt "SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua biên PHỤ". Cây này hơn biên chính đúng **10 tick** và còn cách biên phụ **15 giá**. Cây phá thật nằm ở đoạn 20:45-21:00 (chuỗi nến đỏ dài rơi thẳng từ 4750 xuống 4734, thấy rõ trên ảnh).
- **Nghi phạm:** đây là **tác dụng phụ ngược** của bản vá 13.1c — đổi mốc decisive/outside từ `out_edge` sang `edge` (biên chính) đã cứu được các ca "không công nhận cú phá", nhưng đồng thời làm rơi mất yêu cầu L3 "phải qua biên phụ". Hai luật này phải tách: **công nhận** cú phá dùng biên chính, **xếp hạng mạnh/yếu và chọn cây gắn nhãn** vẫn phải dùng biên phụ.

### 3. mSOW thứ hai gán cho nến CHƯA phá biên — luật vi phạm: định nghĩa mSOW (mục 5.1)
- **Thuật toán gắn:** mSOW 19:52 tại **4749.8**, VSA 11.22x.
- **Đúng phải là:** biên chính dưới là 4750.0 → nến này nằm **trên** biên, chưa phá gì. Cùng lắm là ST[B]. Lỗi này lặp ở bài #14 và #18 → là lỗi hệ thống, không phải ca lẻ.
- **Nghi phạm:** bước hồi tố "chọn cây VSA cao nhất trong đoạn" không kiểm lại `close vượt biên` cho chính cây được chọn.

### 4. ST[A] vẫn lửng, cách climax 39% chiều cao — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 16:43 tại **4757.2**, VSA 0.17x.
- **Đúng phải là:** ST[A] là cú test lại **vùng climax** (4750.0). Điểm này còn cách climax **7.2 giá = 39% chiều cao range** — nằm gần giữa range hơn là gần biên.
- **Dấu hiệu quyết định:** retrace từ AR đo được **61%**, tức **vừa lọt** ngưỡng `STA_MIN_AR_FRAC=0.55` mới. Ngưỡng 0.55 đã chặn được ca >70% nhưng không chặn được cụm 0.55-0.65 — đúng vấn đề mà 13.1b đã mô tả và 13.1c chưa giải quyết.
- **Nghi phạm:** cần thêm ràng buộc TUYỆT ĐỐI song song: khoảng cách ST[A] → climax ≤ ~25% chiều cao range.

### 5. Khoảng trống 61 phút không thuộc phase nào — lỗi timeline
- Phase D kết thúc **20:59**, Phase E bắt đầu **22:00**. Một giờ đồng hồ (đúng đoạn giá rơi sâu nhất, xuống 4730) không được gán phase nào. Trên ảnh dải phase bị đứt quãng.

### 6. AR volume 0.27x không được gắn cờ "(yếu)"
- AR 16:28 VSA **0.27x** — máy có biến `ar_vsa` nhưng chỉ gắn cờ cho ca AR sát climax, không gắn theo volume. Lỗi đã ghi ở 13.1b, chưa sửa.

## Đạt
- **Mở range (L1): ĐẠT.** MOVE giảm 53.5 giá / 70 nến / hiệu suất 0.48; climax là đáy chặn move, thấy rõ trên ảnh (giá rơi 4810 → 4750 rồi dừng hẳn).
- **Tên range (L4): ĐẠT.** Origin SC + phá xuống = **Tái phân phối** — đúng bảng 4 pattern và đúng thực tế (giá đi tiếp xuống 4730).
- **Tỉ lệ phase (L8 + L9): ĐẠT — bài duy nhất trong lô làm đúng.** B = 143 (dài nhất), **C = 9 nến (ngắn nhất)**, D = 17. Bỏ ràng buộc nửa range không gây hại ở ca này.
- **LPSY[C] đúng vai:** 20:31 tại 4761.0 = 60% chiều cao, **nửa trên** — đúng vị trí điểm cung cuối trước cú rơi, và VSA 2.52x.
- **Biên chính (L3): ĐẠT**, cố định 4750.0-4768.4 suốt range; đúng 1 biên phụ mỗi bên.
- **Khối lượng:** SOT phía dưới đo được n=3, thrust cuối/đầu 0.22, volume 0.38 (cạn kiệt) — đọc đúng cạn cung ở đáy trước khi rơi.
