# Chấm bài #24 — Tích luỹ (ACC) · 2026-05-26 08:34 → 11:21 (165 nến M1)

**Điểm: 3/10** — Sửa nặng: Phase C dài gấp 3.7 lần Phase B, Spring gọi sai chỗ, biên phụ dưới không phải đáy thật.

## Lỗi (nặng → nhẹ)

### 1. Phase C (56n) dài gấp 3.7 lần Phase B (15n) — luật vi phạm: L8 **và** L9 cùng lúc
- **Thuật toán gắn:** A 26n, **B 15n**, **C 56n**, D 16n, E 53n.
- **Đúng phải là:** L9 — Phase B là phase **dài nhất**; L8 — Phase C là phase **ngắn nhất**. Ở đây đảo ngược hoàn toàn: C là phase dài nhất trong range (nếu không tính E).
- **Dấu hiệu quyết định trên chart:** Phase C chạy 09:16 → 10:11, tức bao trọn cả cú thủng xuống 4544 lúc ~09:40 lẫn toàn bộ đường bò ngược lên 4560. Đó là nguyên một chu kỳ giá, không phải một cú shock. Phase B chỉ có 15 nến (09:00-09:15) — không đủ để "xây nguyên nhân" gì.
- **Nghi phạm trong thuật toán:** đúng câu hỏi số 2 của đề — bỏ ràng buộc "đúng nửa range" **không** ngăn được Phase C phình; ở bài này còn tệ hơn bài #22. Ràng buộc "gần biên" đơn thuần cho phép Phase C mở tại nến chạm biên dưới rồi kéo dài tới tận nến trước SOS. Cần: Phase C mở **lùi lại** từ SOS/SOW một cửa sổ cứng, và có trần độ dài.

### 2. Spring gọi sai — đây là Shakeout thất bại, và biên phụ dưới sai — luật vi phạm: L5 + L3
- **Thuật toán gắn:** `Spring | 09:16 | 4551.5 | Phase C | confirmed`; biên phụ dưới = **4551.5**.
- **Đúng phải là:** L5 — Spring là phá ra rồi rút vào range **rất nhanh (≈3-4 nến)**. Ở đây sau 09:16 giá không hề rút vào: nó nhùng nhằng rồi rơi tiếp xuống **~4544** quanh 09:40, tức **thấp hơn cái gọi là "Spring" 7.5 giá**. Theo L5, đó là một cú phá xuống lùng bùng ngoài biên = **Shakeout / SOW thất bại**, và điểm shock phải đặt ở đáy 4544, không phải 4551.5.
- **Dấu hiệu quyết định trên chart:** trên ảnh, đường đứt "bien phu duoi 4551.5" bị cả một cụm nến giai đoạn 09:30-09:50 nằm hẳn phía dưới, đáy sâu nhất chạm ~4544. L3 nói biên phụ = **cực trị xa nhất** → 4551.5 sai.
- **Nghi phạm trong thuật toán:** biên phụ bị **đóng băng** ngay khi gán nhãn Spring, không nới tiếp khi xuất hiện đáy sâu hơn; đồng thời phân loại Spring/Shakeout đang dùng tiêu chí độ sâu hoặc "đóng cửa lại trong range", chưa dùng **thời gian quay lại** như L5 yêu cầu.

### 3. LPS[C] đặt trước đáy thật — luật vi phạm: L7 / L8
- **Thuật toán gắn:** LPS[C] 09:31 tại 4552.9.
- **Đúng phải là:** LPS[C] là điểm hỗ trợ **cuối** trước khi bung — nó không thể đứng trước một đáy thấp hơn (4544 lúc ~09:40). Sau khi dời shock về 4544, LPS[C] phải là nhịp lùi ở khoảng 09:55-10:05 quanh 4553-4556.
- **Dấu hiệu quyết định trên chart:** nhãn LPS[C] trên ảnh nằm bên trái vùng trũng sâu nhất của cả range.
- **Nghi phạm trong thuật toán:** cùng gốc với lỗi #2 — chốt nhãn Phase C ngay tại thời điểm phát hiện, không quay lại sửa khi thấy cực trị xa hơn (L8 nói phải "có Phase D rồi mới xác định được Phase C").

### 4. Biên phụ trên 4566.1 sinh từ hành động Phase D/E, không phải nỗ lực phá range gốc — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ trên 4566.1, trong khi biên chính trên 4560.7; SOS 10:12 tại 4563.6.
- **Đúng phải là:** L3 — biên phụ ghi nhận nỗ lực phá **range gốc**. Mức 4566.1 chỉ đạt được **sau** khi SOS đã bứt, tức nó thuộc hành trình Phase D/E, không phải một cú thử biên. Vẽ nó thành biên khiến SOS 4563.6 bị đánh giá là "chưa qua biên phụ" một cách oan.
- **Dấu hiệu quyết định trên chart:** đường đứt 4566.1 chỉ bắt đầu có nến chạm từ ~10:25 trở đi, tức sau SOS 13 nến.
- **Nghi phạm trong thuật toán:** biên phụ tiếp tục được nới trong Phase D/E — đúng loại lỗi "tự nới rồi tự vượt" mà v7.1 nói đã sửa; ở bài này **vẫn còn** ở phía trên.

### 5. Climax mở range VSA 0.67x, nhãn SC lệch 5 nến — luật vi phạm: L1 (nhẹ)
- **Thuật toán gắn:** nến mở range 08:34 có VSA **0.67x**, biên độ 2.3 giá; nhãn SC lại đặt ở 08:29 (VSA 2.96x, giá 4554.1).
- **Đúng phải là:** hai cây này khác nhau. Cây có nỗ lực thật là 08:29-08:30 (volume 64 và 48, VSA 2.96x/2.13x); đáy thật là 08:34. Chấp nhận được nếu gọi là "climax cạn kiệt" (THEORY §6.2), nhưng khi đó biên chính nên neo theo cụm, không neo cây volume rời.
- **Dấu hiệu quyết định trên chart:** MOVE trước chỉ 16.6 giá / 37 nến — move mỏng nhất trong 6 bài lô này, nên nghi vấn L1 là chính đáng.
- **Nghi phạm trong thuật toán:** lỗi nhãn cụm climax chưa vá (ghi nhận, không phải trọng tâm).

## Đạt
- **L2 đạt:** AR 08:46 (4560.7) bật ngược thật; ST[A] 08:59 tại 4555.7 hồi **(4560.7−4555.7)/7.3 = 68%** khoảng AR↔climax → qua ngưỡng 55%, test đúng vùng climax. Ngưỡng mới hoạt động.
- **L3 (biên chính) đạt:** 4553.4 / 4560.7 = climax + AR, cố định.
- **L4 đạt tại thời điểm:** SC + phá lên thật = ACC. (Lưu ý: sau Phase E giá sụp từ 4573 về 4535 — về sau đây là một **cấu trúc thất bại** theo THEORY §9, nhưng tên gán tại thời điểm phá là đúng luật.)
- **L7 đạt:** LPS[C] và LPS[D] mỗi cái đúng 1 điểm.
- **L6 đạt:** không có nhãn ST[B].
- **L10 một phần đạt:** LPS[D] 10:19 tại 4560.7 = đúng mức biên chính trên, retest giữ được → CBR đọc được, Phase E 53 nến giá đi tiếp lên 4573.

## Cần hỏi người học
- Khi Phase E của một ACC bị đảo ngược hoàn toàn ngay sau đó (ở đây giá sụp 40 giá, sâu hơn cả biên dưới range), thuật toán có nên **đổi tên range thành DIST hồi tố** hay giữ nguyên ACC + gắn cờ "cấu trúc thất bại"? L4 chỉ nói phá sai hướng thì đổi tên, chưa nói về ca phá đúng hướng rồi thất bại.
