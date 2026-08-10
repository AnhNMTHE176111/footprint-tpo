# Chấm bài #36 — Phân phối (DIST) · 2026-06-12 08:20 → 11:54 (214 nến M1)

**Điểm: 3/10** — biên chính đặt sai chỗ nên cả bài lệch: giá sống **ngoài** biên chính suốt Phase B, SOW phá biên phụ đúng 1 tick, và LPSY[D] lại nằm trong range.

## Lỗi (nặng → nhẹ)

### 1. Biên chính vô nghĩa — nến neo range không phải climax, biên rộng 9.2 giá trong khi giá đi 24.1 giá — luật vi phạm: L1 + L3
- **Thuật toán gắn:** climax = nến 08:20, **VSA 0.96x** (volume 154, dưới trung bình), high 4242.0; biên chính 4232.8-4242.0 = **9.2 giá (0.22%)**; biên phụ 4223.6-4247.7 = 24.1 giá → tỷ lệ **2.62x**.
- **Đúng phải là:** BCLX thật là nến 08:18 (volume 474, VSA **2.89x**, thân/biên 0.85) — chính nó chặn đứng move tăng 42.3 giá. Neo range vào nến 08:20 làm biên trên tụt xuống 4242.0 trong khi đỉnh thật của vùng là 4247.7.
- **Dấu hiệu quyết định trên chart:** từ 08:40 đến ~10:10 (gần 90 nến, tức 2/3 Phase B) giá **giao dịch hoàn toàn phía trên đường biên chính trên 4242.0**, bám sát đường đứt 4247.7. Một biên chính mà giá sống ở ngoài suốt Phase B thì không còn là biên.
- **Nghi phạm trong thuật toán:** nhánh "nhãn climax = cây volume cao nhất trong cụm nhưng range neo vào cực trị giá của nến khác" (đã biết, chưa sửa). Ở bài này nó không chỉ làm lệch nhãn mà làm hỏng toàn bộ hệ biên → hỏng luôn mọi phép so sánh phá biên bên dưới.

### 2. SOW đóng cửa qua biên phụ đúng 1 tick — luật vi phạm: L3
- **Thuật toán gắn:** SOW 11:29 @**4223.5**; biên phụ dưới **4223.6**. Vượt **0.1 giá**.
- **Đúng phải là:** đây không phải bứt phá, đây là chạm lại đúng mức cũ. Cây này còn chỉ VSA 1.84x, thấp hơn nhiều so với mSOS/mSOW trước đó (6.18x / 5.29x).
- **Nghi phạm trong thuật toán:** giống bài #34 — đệm 30 tick chỉ áp cho biên **chính** (4232.8 − 3.0 = 4229.8, nên 4223.5 lọt) mà không áp cho biên **phụ** đã nới. Phải so với `min(biên chính, biên phụ) − đệm`.

### 3. LPSY[D] nằm TRONG range, cú phá bị lấy lại → Shakeout chứ không phải SOW — luật vi phạm: L5, L10
- **Thuật toán gắn:** SOW 11:29 → LPSY[D] 11:46 @**4232.8** → Phase E **1 nến**.
- **Đúng phải là:** L10 đòi retest phải **giữ được ở ngoài biên**. 4232.8 chính là **biên chính dưới** — tức giá đã hồi hẳn vào trong range. Trên ảnh, sau đáy ~11:33 giá bật lên tận ~4237 rồi mới đi tiếp. Theo L5, phá ra rồi quay lại vào trong = Shakeout (SOW thất bại), phải trả cấu trúc về Phase C.
- **Dấu hiệu quyết định trên chart:** marker LPSY[D] nằm ngay trên đường liền cam 4232.8, cụm nến xanh 11:38-11:46 rõ ràng ở phía trong range.
- **Nghi phạm trong thuật toán:** không có kiểm tra "LPSY[D]/LPS[D] phải nằm ngoài biên" — chỉ cần một nhịp hồi sau SOW là gán nhãn.

### 4. Hai nhãn mâu thuẫn trên cùng một nến 10:58 — lỗi nhãn sai vai (CHART_CASES Ca #8)
- **Thuật toán gắn:** `mSOW | 10:58 | 4231.7 | Phase B | provisional` **và** `LPSY[C] | 10:58 | 4236.7 | Phase C` — cùng một nến, hai nhãn, hai phase khác nhau.
- **Đúng phải là:** một nến chỉ thuộc một phase. Đúng lỗi giảng viên đã bắt ở Ca #8 (gắn cả UT lẫn UTAD cho một điểm) — mâu thuẫn logic phase.
- **Nghi phạm trong thuật toán:** nhãn `provisional` không được dọn khi ranh giới phase chốt lại. Cần bước dọn: nếu một nến nhận nhãn ở hai phase khác nhau thì giữ nhãn của phase mà nến thực sự thuộc về.

### 5. Phase C 31 nến, dài hơn Phase A (20n) và Phase D (25n) — luật vi phạm: L8
- Cùng gốc với bài #34/#35: Phase C = [LPSY[C] … trước SOW], LPSY[C] lấy ứng viên đầu tiên (10:58) nên phase phình ra 31 nến. Phase C thật ở đây là nhịp hồi thất bại quanh 11:20-11:28.

### 6. mSOS rồi mSOW cách nhau 3 nến — nhãn nhiễu
- `mSOS 10:55 @4234.2 (6.18x)` rồi `mSOW 10:58 @4231.7 (5.29x)`. Hai nhãn ngược chiều sát nhau trong Phase B chỉ mô tả một nhịp giật hai chiều, không mang thông tin cấu trúc. Nên có khoảng cách tối thiểu giữa hai nhãn minor ngược dấu.

## Đạt
- Điều kiện MOVE (L1) đạt: 42.3 giá / 47 nến, hiệu suất 0.52 — move tăng thật, bị chặn thật ở vùng 4240-4247.
- Tên range đúng L4: MOVE tăng → BCLX → phá xuống = Phân phối (giá sau đó về 4210).
- Phase B 138 nến = dài nhất, đúng L9.
- ST[A] 08:39 @4244.9 hồi 132% khoảng AR↔climax, vượt qua mức climax — đúng L2, và đúng ra phải tạo biên phụ trên (biên phụ 4247.7 sau đó nới thêm, hợp lệ).
- Đọc SOT có nội dung và trung thực: SOT-dn `xu hướng quá mạnh` (n=5) — đúng cảnh báo §7 THEORY, và SOT-up `HẤP THỤ` (volume nhịp cuối/đầu 1.25) khớp với việc phe mua không giữ nổi vùng 4247.

## Cần hỏi người học
- Khi nến volume cao nhất của cụm và nến cực trị giá **không trùng nhau** (bài này lệch 2 nến, 5.7 giá), muốn neo BIÊN theo nến nào: nến cực trị giá (giữ biên rộng, đúng L3 "mức climax") hay nến volume (đúng định nghĩa climax)? Chọn sai một trong hai là hỏng cả bài — cần chốt để sửa code dứt điểm.
