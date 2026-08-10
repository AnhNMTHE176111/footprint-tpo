# Chấm bài #24 — Tích luỹ (ACC) · 2026-06-02 01:01 → 06:26 (325 nến M1)

**Điểm: 3/10** — khung range và cú phá cuối đọc đúng, nhưng bỏ sót hẳn cú rũ sâu nhất của cả range (8.7 giá dưới biên), mất luôn Phase C, và dán nhãn **mSOW ở phía TRÊN** biên chính — nhãn sai bên.

## Lỗi (nặng → nhẹ)

### 1. mSOW đặt ở 4524.2 — phía TRÊN biên chính trên 4521.6 — luật vi phạm: mục 5.1 (nhãn theo BÊN)
- **Thuật toán gắn:** mSOW 03:29 tại 4524.2, VSA 5.38×, thân 0.05.
- **Đúng phải là:** một cú thăm dò **vượt biên trên** rồi tụt lại chỉ có thể là **UT[B]** hoặc **mSOS**. Gọi "dấu hiệu yếu" cho một cây thọc lên là mâu thuẫn khái niệm — đúng loại lỗi giảng viên bắt ở Ca #7 nguồn 7.pdf ("vị trí trong range quyết định tên gọi").
- **Dấu hiệu quyết định trên chart:** nhãn mSOW nằm **trên** đường cam liền "bien CHINH tren 4521.6"; thân nến 0.05 = cây pin thọc lên.
- **Nghi phạm trong thuật toán:** vá v7 #5 (quét lại lấy nến VSA cao nhất trong đoạn thăm dò) quét **không lọc bên/hướng**, nên nhãn hạ cấp của một cú thăm dò xuống bị neo vào cây VSA 5.38× ở phía ngược lại. Phải ràng buộc: nến nhận nhãn mSOW phải có `low` ngoài biên **dưới**.

### 2. Cú thủng 8.7 giá dưới biên không được gắn nhãn nào — luật vi phạm: L3 + L5
- **Thuật toán gắn:** biên phụ dưới 4492.3, không có sự kiện nào tại đó.
- **Đúng phải là:** 4492.3 thấp hơn climax 4501.0 **8.7 giá = 42% chiều cao range** — vượt xa ngưỡng "cú rũ mạnh" (15%). Giá thủng biên khoảng 01:45–01:57 rồi thu lại → đây là **Shakeout**, và nó phải là Phase C (case dễ).
- **Dấu hiệu quyết định trên chart:** cụm nến đỏ dài quanh 01:52 đâm xuống chạm đúng đường đứt 4492.3, cách đường liền 4501.0 một khoảng bằng gần nửa chiều cao range.
- **Nghi phạm trong thuật toán:** vòng lặp "biên phụ tự nới rồi tự vượt" **vẫn còn**: chính cú thủng này nới biên phụ xuống 4492.3, sau đó điều kiện "cú rũ phải vượt qua biên phụ" không bao giờ thoả được. Vá v7 #6 chỉ đổi ngưỡng 10 → 30 tick cho outside/timed-out, không chạm nhánh nới biên phụ trong `C_pending`.

### 3. Thiếu hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** A 18 → B 162 → D 25 → E 121.
- **Đúng phải là:** phải có Phase C. Case dễ đã có sẵn (Shakeout 4492.3, lỗi 2); ngay cả khi bỏ qua nó thì cách gán ngược cũng phải cho ra một LPS[C].
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược 60 nến trước SOS (03:01–04:01) cộng ràng buộc "pivot phải nằm **nửa dưới** range" → rỗng, vì trong đoạn đó giá đã bò lên trên trung điểm 4511.3 rồi. Ràng buộc nửa range (vá v6 #5) đang giết Phase C ở mọi ca giá bò dần lên trước khi phá.

### 4. AR (20.6 giá) lớn hơn cả MOVE bị chặn (18.3 giá) — luật vi phạm: L1 (chất lượng move)
- Range cao 20.6 giá trong khi đợt giảm mà climax được cho là đã chặn chỉ dài 18.3 giá / 29 nến. Nguyên nhân không đủ lớn để sinh ra một vùng cân bằng rộng hơn chính nó; đây là ca nên nghi range vẽ quá to so với nguyên nhân.
- **Nghi phạm:** thiếu ràng buộc `chiều cao biên chính ≤ k × độ dài MOVE`.

### 5. Phase D 25 nến không có LPS[D] — nhãn thiếu
- Sau SOS 04:01 giá có nhịp lùi rõ (khoảng 04:10–04:20 trên chart) nhưng không nhãn nào được đặt, dù mục 7 đã đo LPS[D] bằng swing pivot cấu trúc.

## Đạt
- L1: climax 01:01 là đáy thấp nhất cửa sổ, VSA 5.98× với 272 hợp đồng, nhãn đúng nến mở range (vá v7 #4 chạy đúng ở bài này).
- L3: biên chính 4501.0–4521.6 cố định, tỷ lệ biên phụ 1.83×.
- L4: SC + phá lên = Tích luỹ — đúng, và chart xác nhận (giá chạy tới 4570).
- L9: Phase B 162/325 nến, dài nhất.
- L10: SOS 04:01 VSA **7.45×** thân 0.70, đóng cửa vượt **biên phụ** 4530.0 — đúng chuẩn "SOS mạnh" của L3; Phase E 121 nến đi tìm vùng giá mới.
- **Vá v7 #1 chạy đúng:** er=0.52 → "nhịp HIỆU QUẢ"; SOT phía dưới n=3 gọi đúng là SOT.
