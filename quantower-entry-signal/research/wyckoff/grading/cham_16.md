# Chấm bài #16 — Tích luỹ (ACC) · 2026-05-12 13:16 → 2026-05-13 02:05 (430 nến M1)

**Điểm: 4/10** — Phase A và cách đặt tên đều đúng, nhưng biên phụ dưới bỏ sót cú thọc sâu nhất của cả range, kéo theo nhãn Shakeout gán sai chỗ. Sửa nhãn nặng ở Phase B/C.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới bỏ sót cực trị thật (~4682) — luật vi phạm: L3
- **Thuật toán gắn:** `biên phụ dưới = 4710.8` (chính là giá của nhãn Shakeout).
- **Đúng phải là:** trên ảnh, quanh `05-12 15:23` có một cú sụp thẳng đứng xuống ~**4682** — thấp hơn biên phụ đang vẽ tới ~29 giá và thấp hơn biên chính dưới 4722.5 tới 40 giá. Đó mới là cực trị xa nhất mà phe bán đẩy tới, tức biên phụ dưới thật.
- **Dấu hiệu quyết định trên chart:** cây nến dài nhất toàn bài, đáy nằm giữa mốc trục 4692.0 và 4675.5; panel volume cùng lúc có thanh vàng cao nhất chart.
- **Nghi phạm trong thuật toán:** cơ chế "đóng băng biên phụ ở phía đang test trong `C_pending`" (vá v6 #2) chặn nhầm — cú thọc này rơi vào lúc một thăm dò khác đang chờ kết cục nên biên phụ **không bao giờ** được nới cho nó.

### 2. Nhãn "Shakeout" gán vào cú thọc NÔNG hơn — luật vi phạm: L3 + L5 + mục 5.1 (cú rũ phải vượt biên phụ)
- **Thuật toán gắn:** `Shakeout 16:54 @4710.8 (confirmed)`, mở Phase C tại đó.
- **Đúng phải là:** cú rũ thật là cú xuống 4682 lúc ~15:23 (phá sâu, lùng bùng ngoài biên khá lâu rồi mới về = đúng định nghĩa Shakeout theo L5). Cú 16:54 chỉ chạm 4710.8, **không** vượt được cực trị cũ → theo đúng quy tắc của chính thuật toán ("cú rũ phải vượt biên phụ") nó chỉ được là **ST[B]** hoặc **LPS[C]**.
- **Dấu hiệu quyết định trên chart:** đáy 16:54 nằm cao hơn đáy 15:23 rõ rệt; đây chính là lỗi kinh điển "gọi Spring/Shakeout cho một đáy không phá đáy cũ" (Ca #4/#16/#19/#20 nguồn 2.pdf, 4/22 ca).
- **Nghi phạm trong thuật toán:** vì biên phụ bị kẹt ở 4710.8 (lỗi 1) nên phép so "vượt biên phụ" cho kết quả **đúng-giả**: cú thăm dò tự nó đặt biên phụ rồi tự nó vượt. Đây là biến thể còn sót của lỗi "biên phụ tự nới rồi tự vượt" (vá v7 #6 chưa chạm tới nhánh này).

### 3. mSOW cũng không neo vào cây mạnh nhất/sâu nhất — luật vi phạm: vá v7 #5
- **Thuật toán gắn:** `mSOW 15:10 @4712.6, VSA 10.51x`.
- **Đúng phải là:** VSA 10.51× thì cây được chọn đã đủ mạnh (điểm cộng so với bài #13/#15), nhưng cực trị của chính đợt thăm dò đó là 4682 lúc 15:23 — nhãn mSOW đứng cách đáy thật 30 giá về giá và 13 phút về thời gian.
- **Nghi phạm trong thuật toán:** quét lại VSA cao nhất (v7 #5) chạy **trước** khi đợt thăm dò kết thúc, nên bỏ qua đoạn sâu nhất nằm sau đó. Nên chốt nhãn sau khi biết kết cục.

### 4. Phase C dài 87 nến, dài hơn cả Phase D — luật vi phạm: L8
- **Thuật toán gắn:** A 45 · B 153 · **C 87** · D 25 · E 121.
- **Đúng phải là:** Phase C là phase ngắn nhất. Nếu chốt đúng cú rũ ở 15:23 thì Phase C chỉ nên bao đoạn 15:23 → nhịp test cuối trước SOS, và Phase B phải kéo dài hơn 153 nến.
- **Nghi phạm trong thuật toán:** trần chờ 120 nến của Phase C quá rộng so với thực tế; và vì cú rũ được gán muộn (16:54) nên Phase B bị cắt ngắn oan.

### 5. (Nhẹ) Phase E dài đúng 121 nến = trần
- Phase E chạm đúng trần 120 nến → không phải độ dài đo bằng cấu trúc. Trên ảnh giá thật sự đi tiếp lên 4770 rồi mới quay đầu; chốt E ở trần là hợp lý nhưng nên ghi rõ "(chạm trần)" để người đọc không hiểu nhầm là đo được.

## Đạt
- Điều kiện mở range (L1): MOVE 23.6 giá / 23 nến / hiệu suất 0.57; cây climax VSA **6.34×**, biên độ 5.2 giá, đúng là cây chặn move và đúng là đáy — bài climax sạch nhất lô.
- **Nhãn SC neo đúng nến climax** (13:16, cùng nến, VSA 6.34×) — vá v7 #4 chạy đúng ở bài này (khác hẳn #13/#14/#15/#17).
- Phase A đủ 3 lần đổi hướng, kết thúc tại ST[A]; ST[A] @4719.1 thủng nhẹ dưới climax 4722.5 → hợp lệ và sinh biên phụ đúng theo L3.
- ST[B] @4721.2 gán đúng vai (test nhẹ biên dưới, không phá) — không lạm dụng nhãn Spring.
- Tên range: SC + phá lên = Tích luỹ, khớp L4. SOS 19:25 @4746.6 VSA 2.44× thân 1.00, đóng trên biên chính 4744.4.
- Chú thích nỗ lực/kết quả đúng dấu er (0.45 → "nhịp HIỆU QUẢ") — vá v7 #1 tốt.
