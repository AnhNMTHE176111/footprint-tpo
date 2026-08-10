# Chấm bài #21 — Tích luỹ (ACC) · 2026-05-26 08:34 → 11:21 (165 nến M1)

**Điểm: 2/10** — tỉ lệ phase lộn ngược (B ngắn nhất, C dài nhất), và nặng nhất: một cú thủng ~6 giá dưới biên bị bỏ qua hoàn toàn, biên phụ dưới đứng yên. Cấu trúc phải vẽ lại từ Phase B.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới đóng băng ở 4551.5 trong khi giá xuống tới ~4547 — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới **4551.5** (đúng bằng đáy của cây "Spring" 09:16).
- **Đúng phải là:** biên phụ = **cực trị xa nhất**. Sau LPS[C] (09:31) giá rơi tiếp xuống ~4547, tức **6.4 giá dưới biên chính 4553.4** và 4.5 giá dưới biên phụ đang vẽ, rồi lùng bùng ngoài đó tới ~10:00. Biên phụ phải nới xuống ~4547 và cú rũ thật phải là cú này.
- **Dấu hiệu quyết định trên chart:** cụm nến đỏ vùng 09:40–09:55 nằm hẳn dưới cả hai đường cam (liền và đứt) — đọc trên trục giá ≈ 4547, thấp hơn nhãn "bien phu duoi 4551.5" rõ rệt.
- **Nghi phạm trong thuật toán:** đúng cái vá v6 #2 — trong trạng thái `C_pending` phía đang test **ngừng nới biên phụ**. Kết quả: cú sâu hơn xảy ra *trong lúc* chờ Phase C thì vô hình. Vá v7 #6 (đổi 10 → 30 tick) không chạm tới nhánh này.

### 2. "Spring" gán sai loại và sai chỗ — luật vi phạm: L5 + THEORY §9
- **Thuật toán gắn:** Spring 09:16 tại 4551.5, trạng thái `confirmed`.
- **Đúng phải là:** cú rũ thật là đáy ~4547, và giá **ở ngoài range hơn 20 nến** trước khi quay lại → theo L5 đó là **Shakeout**, không phải Spring. Ngoài ra trạng thái `confirmed` là sai: sau "Spring" giá không đi về biên đối diện mà đi **sâu hơn nữa** — theo THEORY §9 đây là cấu trúc thất bại tại thời điểm đó.
- **Nghi phạm trong thuật toán:** luật "mỗi range chỉ MỘT cú rũ, cú sâu hơn hạ cấp cú trước" không chạy được vì cú sâu hơn không bao giờ được nhận diện (lỗi 1).

### 3. Phase B (15 nến) ngắn hơn Phase A (26) và Phase C (56) — luật vi phạm: L8 + L9
- **Thuật toán gắn:** A 26 · B 15 · C 56 · D 16 · E 53.
- **Đúng phải là:** B dài nhất, C ngắn nhất. Ở đây đảo ngược hoàn toàn cả hai luật cùng lúc.
- **Nghi phạm trong thuật toán:** Phase C mở ngay tại cú rũ 09:16 rồi treo tới 10:11 vì cú rũ được đánh `confirmed` sai (lỗi 2) — đoạn 40 nến giá lang thang ngoài range đáng lẽ vẫn là Phase B.

### 4. Nhãn SC nằm ngoài khung range — luật vi phạm: L3 (trình bày + mốc)
- **Thuật toán gắn:** SC tại 08:29 giá 4554.1; range bắt đầu 08:34; biên chính dưới 4553.4 lấy từ nến 08:34.
- **Đúng phải là:** mốc bắt đầu range = nến climax. Trên ảnh, nhãn SC đứng **bên trái vạch Phase A**, tức climax nằm ngoài range của chính nó, và nhãn treo ở 4554.1 — cao hơn biên chính dưới.
- **Nghi phạm trong thuật toán:** vá v7 #4 kẹp nhãn theo nến mở range, nhưng ở đây mốc mở range **dời tiến** theo cực trị cụm còn nhãn giữ tại cây VSA cao (08:29) → hai mốc tách nhau 5 nến. Phải kẹp cả hai: nếu nhãn nằm trước nến mở range thì kéo mốc mở range lùi về nhãn.

### 5. Biên phụ trên 4566.1 do chính Phase E tạo ra — luật vi phạm: L3
- 4566.1 chỉ đạt được sau 10:28 (trong Phase E). Biên phụ theo định nghĩa là mức mà một thế lực **cố phá mà không được**; giá đã phá thành công và đi tiếp thì đó là Phase E, không phải biên phụ. Hệ quả: SOS 4563.6 bị hiển thị như chưa vượt biên phụ, sai lệch phép đánh giá "SOS mạnh" của L3.

### 6. Range quá vụn — cảnh báo khung
- Chiều cao biên chính **7.3 giá (0.16%)**, MOVE trước climax chỉ 16.6 giá, climax thật là nến 15 hợp đồng VSA 0.67×. Đủ 5 phase trên một dải 7 giá của vàng M1 là dấu hiệu đang gắn nhãn cho nhiễu.

## Đạt
- L4: SC + phá lên = Tích luỹ — tên đúng.
- L7: LPS[C], LPS[D] mỗi cái một điểm.
- **Vá v7 #1 chạy đúng:** er=0.49 → "nhịp HIỆU QUẢ".
- SOT phía dưới ghi "cạn kiệt" (tỷ lệ volume 0.51) — đọc đúng dấu.
