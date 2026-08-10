# Chấm bài #59 — Chưa rõ (SC) (ACC?) · 2026-07-27 12:23 → 15:56 (213 nến M1, active)

**Điểm: 2/10** — Sửa nhãn không cứu được: cả một cú sụp 14 giá với cây VSA 5,29× bị gọi là "thăm dò", nên range đứng nguyên ở Phase B suốt 203/213 nến trong khi giá đã bỏ đi từ lâu.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới KHÔNG nới tới cực trị thật — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới **4074.8**, trong khi cực trị thật của cú thăm dò là **4068.6** (14:28) — thấp hơn nét đứt **6.2 giá**, tức gần **83% chiều cao biên chính**.
- **Đúng phải là:** biên phụ = mức cực trị xa nhất mà một thế lực đã tạo ra ngoài range gốc. Cả cụm nến 14:20–14:45 nằm dưới nét đứt mà nét đứt vẫn đứng yên.
- **Dấu hiệu quyết định trên chart:** nhãn mSOW 14:28 được vẽ ở 4068.6, **thấp hơn hẳn đường "biên phụ duoi 4074.8"** ngay trên nó — máy tự mâu thuẫn với chính nó trong một khung hình.
- **Nghi phạm trong thuật toán:** cơ chế "trong lúc `C_pending` chỉ nới biên phụ phía đối diện, phía đang test nới **một lần duy nhất** sau khi biết kết cục" — lần nới duy nhất đó đã dùng cho cú nông hơn (4074.8) nên cú sâu 4068.6 không còn lượt.

### 2. Bỏ sót SOW dù giá không hề quay lại trong biên — luật vi phạm: L10 + L3
- **Thuật toán gắn:** mSOW 14:28 (VSA **5.29×**, thân 0.04) và mSOW 15:45; range vẫn "Chưa rõ (SC)", Phase B kéo tới nến cuối.
- **Đúng phải là:** **SOW** tại cây 14:28, LPSY[D] ở nhịp hồi 15:31–15:45 (bật lên ~4082, vẫn **dưới** biên chính dưới 4083.1 → giữ được ngoài biên), tên range phải là **Tái phân phối** (origin SC + phá xuống thật, L4).
- **Dấu hiệu quyết định trên chart:** từ 14:00 tới 15:56 (**≈115 nến**) không có một nến nào đóng cửa trở lại trên biên chính dưới 4083.1; đáy 4068.6 cách biên chính **14.5 giá = 1,9× chiều cao range**.
- **Nghi phạm trong thuật toán:** đây là bằng chứng bản vá 13.1c **chưa chạm gốc rễ**. Quyết định decisive/outside/timed-out đã đổi sang biên chính, nhưng ngưỡng chốt SOS/SOW ("3 nến đóng vượt **biên phụ** + 30 tick", mục 5.1) vẫn neo biên phụ — mà biên phụ 4074.8 chính là do cú thăm dò trước nới ra. Vòng lặp "tự nới rồi tự vượt" còn nguyên ở nhánh này.

### 3. Phase A quá vội, AR/ST[A] đều trên nến gần như trống — luật vi phạm: L2
- **Thuật toán gắn:** Phase A **11 nến** (12:23→12:33). AR 12:27 (4 nến sau climax) VSA **0.60×**; ST[A] 12:33 VSA **0.41×**.
- **Đúng phải là:** AR phải là cú bật ngược thật sau move giảm 23 giá. Bật 7.5 giá trong 4 nến trên volume dưới trung bình là nhịp thở, không phải "lực đẩy tự động" — biên trên 4090.6 dựng trên nền yếu, và quả nhiên giá sau đó xuyên qua nó (4091.8) rồi lại xuyên xuống biên dưới.
- **Dấu hiệu quyết định trên chart:** Phase A chiếm **5%** độ dài range; cả AR lẫn ST[A] nằm gọn trong 11 nến sát climax, panel volume ở đoạn đó thấp hơn đường trung bình.
- **Nghi phạm trong thuật toán:** sàn AR "≥1.5× biên độ TB" và "≥0.5× nhịp hồi lớn nhất trong lòng move" đều chỉ đo GIÁ, không đo volume. `ar_vsa` đã tính sẵn (mục 13.1b) nhưng chưa dùng để gắn cờ hay chặn.

### 4. Thiếu Phase C và D — luật vi phạm: L8
- Không có Phase C dù cấu trúc đã phá hẳn xuống. Lỗi dây chuyền từ mục 2: Phase C gán ngược chỉ chạy khi SOS/SOW bắn ra. Nếu công nhận SOW 14:28 thì LPSY[C] phải là đỉnh 13:47 (4091.8, chạm đúng biên phụ trên) — cú test cuối cùng trước khi sụp.

### 5. Nhãn SC lệch 3 nến trước nến mở range — lỗi cụm climax
- Nhãn SC tại 12:20 (4083.4, VSA 2.61×) trong khi range mở 12:23 tại 4083.1. Mức giá gần đúng nên tác hại nhỏ, nhưng vẫn là lỗi "nhãn nằm trước nến mở range" chưa sửa.

### 6. MOVE sát sàn — L1 (ghi nhận)
- Hiệu suất hướng **0.37** so với sàn 0.35. Move giảm 23.1 giá / 73 nến là có thật (nhìn chart rõ), nhưng đây là ca biên — nếu siết sàn thì range này rụng.

## Đạt
- **ST[A] đúng vị trí (phần đo được của L2):** 4085.0, cách climax 4083.1 chỉ **1.9 giá = 25% chiều cao**, retrace 75% khoảng AR↔climax. Ngưỡng 0.55 mới làm đúng việc của nó ở đây.
- Biên chính = climax + AR, cố định suốt range, không bị kéo theo giá.
- Trạng thái "active" là trung thực — nến 15:56 là nến cuối của bộ dữ liệu, không phải máy bỏ dở (mục 9 spec).
- Phase B là phase dài nhất (L9 đạt, dù chỉ vì thiếu C/D/E).
