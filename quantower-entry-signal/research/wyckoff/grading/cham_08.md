# Chấm bài #08 — Tái phân phối (RE-DIST) · 2026-04-28 02:00 → 05:39 (83 nến M1)

**Điểm: 2/10** — **Không nên vẽ range ở đây.** 83 nến, biên chính cao 12.7 giá (0.27%), Phase D và Phase E mỗi cái đúng **1 nến**. Đây là một nhịp nghỉ 3 tiếng giữa đợt giảm, không phải vùng đấu giá. Cộng thêm cú phá biên thật bị bỏ qua và SOW gán vào nến sai.

## Lỗi (nặng → nhẹ)

### 1. Range là nhiễu, không phải vùng đấu giá — luật vi phạm: mục 1 (điều kiện mở range), cảnh báo "range quá vụn" trong CHART_CASES
- **Thuật toán gắn:** một range đủ **Phase A→E** trong 83 nến M1, biên chính 4715.8–4728.5 = **12.7 giá = 0.27% giá**.
- **Đúng phải là:** không vẽ. Chuẩn chấm đã chốt: một TR M1 dài 60-100 nến mà có đủ Phase A→E thì phải nghi ngay là nhiễu. Ở đây còn tệ hơn — Phase D = **1 nến**, Phase E = **1 nến**. Một phase 1 nến không phải phase.
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, cả cái range gói trong một dải mỏng ở đúng vùng 4715-4728 giữa một đợt giảm rõ ràng: trước range giá từ 4747 rơi xuống (mũi xám 35.7 giá), sau range giá đi thẳng xuống 4670. Vùng "cân bằng" chỉ là 3 tiếng nghỉ. Chiều cao 12.7 giá còn nhỏ hơn biên độ **một nến** climax của bài #10 (19.0 giá).
- **Nghi phạm trong thuật toán:** thiếu **sàn dưới** cho range: hiện chỉ có guard trần (3.5% giá, 2500 nến), không có guard "range quá thấp / quá ngắn". Đề xuất: chiều cao biên chính ≥ k × ATR20 và số nến từ climax tới ST[A] ≥ ngưỡng, nếu không thì bỏ ứng viên.

### 2. Cú phá biên thật bị bỏ qua, SOW gán muộn 39 phút vào nến 0.71x — luật vi phạm: mục 8 Effort vs Result, THEORY §4.1
- **Thuật toán gắn:** SOW tại 05:38, giá 4687.6, VSA **0.71x**, thân 0.55.
- **Đúng phải là:** SOW ở nến **04:59** — trên ảnh đó là cây nến đỏ dài xuyên thẳng qua biên dưới, kèm **cột khối lượng cao nhất toàn chart** (thanh vàng cao vượt trội trong panel dưới). Đó là chỗ "nguồn cung chiếm ưu thế rõ ràng" theo THEORY §4.1. Nến 05:38 chỉ là phần đuôi, khối lượng dưới trung bình.
- **Dấu hiệu quyết định trên chart:** từ 04:59 giá **không bao giờ quay lại trong range nữa** (biên dưới 4715.8, giá về 4700 rồi 4687 rồi 4670), vậy kết cục "ở hẳn ngoài biên" đã xong ngay tại đó. Thuật toán vẫn giữ Phase B tới 05:22 rồi mở Phase C sau khi cấu trúc đã sập.
- **Nghi phạm trong thuật toán:** điều kiện xác nhận phá THẬT ở mục 5.1 (**3 nến liên tiếp** đóng cửa vượt biên phụ thêm ≥ 30 tick, thân ≥ 45%) cộng với "giãn cách tối thiểu 5 nến giữa 2 sự kiện". Nhịp hồi nhẹ ngay sau cây 04:59 làm đứt chuỗi 3 nến, đẩy SOW xuống rất muộn. Nên cho phép xác nhận bằng **một nến duy nhất** nếu nến đó vừa phá biên vừa có VSA cao và thân lớn (nến 04:59 thoả cả ba).

### 3. Phase C nằm SAU khi cấu trúc đã sập, LPSY[C] nằm ngoài range — luật vi phạm: L8
- **Thuật toán gắn:** Phase C = 05:24 → 05:37; LPSY[C] tại 05:24 giá **4707.5**.
- **Đúng phải là:** L8 — Phase C là "tín hiệu **đầu tiên** cho thấy giá ở biên này bắt đầu phá biên kia", tức nó phải đứng **trước** cú phá. Ở đây Phase C mở sau khi giá đã rơi ra ngoài range 8.3 giá.
- **Dấu hiệu quyết định trên chart:** LPSY[C] 4707.5 thấp hơn biên chính dưới 4715.8 tới **8.3 giá** — nhãn nằm hẳn dưới nét liền cam, thấy rõ trên ảnh. Một Phase C nằm ngoài range là Phase C không tồn tại; cùng họ lỗi với Ca #10 nguồn 2.pdf (Failed SOS xong vẫn còn là Phase B, chưa phải C).
- **Nghi phạm trong thuật toán:** hệ quả của lỗi #2 — vì SOW bị gán muộn nên nhánh "gán ngược Phase C từ 60 nến trước cú phá" (mục 6 case KHÓ) lấy cửa sổ đã trôi ra ngoài range.

### 4. Phase A dài hơn Phase B — luật vi phạm: L9
- A = **49 nến**, B = **26 nến**, C = 7, D = 1, E = 1. L9 nói Phase B là phase dài nhất. Ở đây Phase A chiếm 59% cả range. Trên ảnh, "Phase A (49n)" trải từ 02:00 tới 04:30 gồm cả một đoạn đi ngang dài — đoạn đó là quan hệ cung/cầu của Phase B chứ không phải Phase A.

### 5. AR là một nến doji khối lượng 0.25x — luật vi phạm: L2 (AR phải là cú bật ngược thật)
- **Thuật toán gắn:** AR 02:16 giá 4728.5, VSA **0.25x**, thân **0.00**.
- **Đúng phải là:** "lực đẩy tự động" phải là một sóng mua thật (THEORY §3.3). Cú bật 12.7 giá trên khối lượng bằng **1/4 trung bình**, kết ở một nến doji, chỉ vừa đủ vượt cửa ải 30% độ dài move (12.7 / 35.7 = 36%). Đây là AR trên giấy tờ, không phải trên thị trường.
- **Nghi phạm trong thuật toán:** ngưỡng "AR phải hồi ≥ 30% độ dài move" không kèm điều kiện chất lượng nào. Nên thêm: nến/nhịp AR phải có khối lượng ≥ trung bình, hoặc bỏ ứng viên.

### 6. Climax vẫn không phải cực trị (nhẹ) — luật vi phạm: L1
- Climax 02:00 đáy 4715.8, nhưng nến +1 và +2 có đáy **4715.1 / 4715.0**. Lệch nhỏ (0.8 giá) nên không đổi cách đọc, nhưng cùng một lỗi gốc như bài #06/#07/#09: chỉ kiểm cực trị về phía sau, không kiểm phía trước.

## Đạt
- **Tên range nhất quán với L4:** SC chặn move giảm + phá thật xuống = Tái phân phối. Đúng bảng 4 pattern, và đúng bối cảnh (giá đang trong đợt giảm, range chỉ là chỗ nghỉ).
- **Có MOVE thật trước climax:** 35.7 giá / 56 nến / hiệu suất **0.45** — cao nhất trong 5 bài chấm lần này sau #10. Mũi xám trên ảnh là một đoạn giảm liền mạch.
- **ST[A] tạo biên phụ đúng L3:** ST[A] 4715.2 vượt nhẹ dưới mức climax 4715.8 → sinh biên phụ dưới 4715.0, đúng quy tắc "ST[A] vượt qua mức climax cũng tạo biên phụ", mỗi bên đúng 1 cái.
- **Không có ST[B] (L6), LPSY[C] một điểm (L7).**
- **Không bịa Spring/UTAD** dù rất dễ bịa ở một range hẹp như vậy.

## Cần hỏi người học
- Ngưỡng **sàn** cho range nên đặt theo cái gì: số nến tối thiểu (vd ≥ 200 nến M1), chiều cao tối thiểu theo ATR, hay cả hai? Đây là chỗ tài liệu Wyckoff không phân xử được (THEORY §10 mục 2 ghi rõ "không có định nghĩa số học cho phạm vi TR hợp lệ").
