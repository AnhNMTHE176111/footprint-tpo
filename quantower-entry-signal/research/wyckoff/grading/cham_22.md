# Chấm bài #22 — Tái phân phối (RE-DIST) · 2026-05-25 01:47 → 06:40 (257 nến M1)

**Điểm: 2.5/10** — Không nên vẽ range ở đây. Biên chính 7.7 giá cho 257 nến là một sợi chỉ, không phải vùng đấu giá; và bài này vẫn còn nhãn ST[B] đã bị bỏ.

## Lỗi (nặng → nhẹ)

### 1. Còn nguyên nhãn ST[B] — luật vi phạm: L6
- **Thuật toán gắn:** `ST[B] | 2026-05-25 02:59 | 4593.4 | Phase B`.
- **Đúng phải là:** L6 đã **bỏ hẳn** nhãn ST[B] ("nó chả dùng làm gì cả"). Test nhẹ ở biên chỉ còn UA / DA / UT. Điểm 4593.4 nằm **dưới** biên chính dưới 4594.7 → đây là **DA** (test xuống dưới biên), không phải ST[B].
- **Dấu hiệu quyết định trên chart:** nhãn "ST[B]" hiện rõ trên ảnh ở khoảng 02:59, nằm ngay dưới đường liền cam 4594.7.
- **Nghi phạm trong thuật toán:** nhánh sinh nhãn ST[B] chưa bị gỡ khỏi code — đây là lỗi hồi quy so với L6 đã chốt, và là lỗi rẻ nhất để sửa trong cả 6 bài.

### 2. Phase C dài 58 nến, gấp hơn 2 lần Phase D — luật vi phạm: L8
- **Thuật toán gắn:** A 28n, B 146n, **C 58n**, D 25n, E 1n.
- **Đúng phải là:** L8 — Phase C là phase **ngắn nhất**. 58 nến là một phase B thu nhỏ, không phải một cú shock.
- **Dấu hiệu quyết định trên chart:** trong khoảng Phase C (05:05 → 06:11), giá đi từ 4599.6 xuyên thẳng xuống ~4586, tức **cú phá thật đã nằm gọn trong Phase C**. Trên ảnh, từ khoảng 05:19 toàn bộ nến đã ở dưới đường đứt biên phụ dưới 4590.8.
- **Nghi phạm trong thuật toán:** đúng câu hỏi số 2 của đề — bỏ ràng buộc "đúng nửa range" **chưa** ngăn được Phase C phình. Cần thêm trần cứng cho độ dài Phase C (ví dụ ≤ min(Phase D, Phase B/4)).

### 3. Cú phá thật bị nhận muộn ~50 nến; SOW gán vào cây volume cạn — luật vi phạm: L10 / mục 8 Effort-Result
- **Thuật toán gắn:** SOW 06:12 tại 4585.7, **VSA 0.61x**; LPSY[D] 06:26 tại 4591.0, VSA 0.36x.
- **Đúng phải là:** SOW phải là cây bứt biên **có nỗ lực**. Cú bứt thật là nhịp 05:19–05:30 (giá rời 4597 xuống dưới 4590.8, thấy rõ trên ảnh và trên panel volume). Cây 06:12 với VSA 0.61x là nến cuối của đợt rơi, không phải cây phá.
- **Dấu hiệu quyết định trên chart:** LPSY[D] 4591.0 nằm **trên** biên phụ dưới 4590.8 — tức nhịp retest **không giữ được ngoài biên**, vi phạm điều kiện CBR của L10. Ngay sau đó (Phase E dài đúng 1 nến) giá bật lên 4600+.
- **Nghi phạm trong thuật toán:** điều kiện xác nhận SOW đang chờ quá lâu (timed-out so với biên chính) nên bắt trượt cây phá; đồng thời không kiểm tra "LPSY[D] phải nằm ngoài biên".

### 4. Biên phụ dưới không phải cực trị xa nhất — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới **4590.8**.
- **Đúng phải là:** L3 — biên phụ = mức cực trị **xa nhất** mà một thế lực đã cố phá range gốc tạo ra. Giá đã xuống 4585.7 (SOW) và trên ảnh còn thấp hơn nữa (~4584).
- **Dấu hiệu quyết định trên chart:** đường đứt 4590.8 bị hàng chục nến nằm phía dưới xuyên qua, kéo dài từ ~05:19 tới 06:30.
- **Nghi phạm trong thuật toán:** thứ tự "nới biên phụ" bị đóng băng khi range chuyển sang Phase C/D. Chấp nhận được về mặt thiết kế, nhưng khi đó phải **thôi vẽ** đường đứt đó như một biên còn hiệu lực.

### 5. Không có climax thật, biên chính 0.17% cho 257 nến — luật vi phạm: L1 + "range quá vụn"
- **Thuật toán gắn:** tiêu đề tự ghi *"SINH TU CHINH MOT CU PHA, khong co cao trao thuc su"*; phiếu **không có dòng MOVE trước climax**; biên chính 4594.7–4602.4 = **7.7 giá (0.17%)**.
- **Đúng phải là:** thiếu MOVE là thiếu điều kiện CẦN của L1 → không mở range. Thêm nữa, một "vùng đấu giá" 257 nến mà chỉ rộng 7.7 giá trong khi giá thực tế dao động 4583–4611 trên cùng khung ảnh thì biên đó không mô tả được gì.
- **Dấu hiệu quyết định trên chart:** trên ảnh, hai đường liền cam nằm sát nhau ở giữa, còn phần lớn hành động giá diễn ra bên ngoài chúng.

## Đạt
- **L2 đạt:** AR 02:09 (4602.4) bật ngược thật; ST[A] 02:17 tại 4592.6 hồi **126%** khoảng AR↔climax — vượt luôn mức climax, và theo L3 nó tạo biên phụ dưới hợp lệ. Ngưỡng 55% mới không bị hụt ở đây.
- **L9 đạt:** Phase B 146 nến, dài nhất.
- Đọc effort↔result tốt: nhịp 02:48 ghi effort 1.42x / result 0.19, tỷ lệ er = **7.58 — vùng hấp thụ nghi vấn**. Đây là chỉ số duy nhất trong bài thực sự nói lên chuyện gì đang xảy ra, thuật toán bắt đúng.
- **L7 đạt:** LPSY[C] và LPSY[D] mỗi cái 1 điểm.
