# Chấm bài #37 — Chưa rõ (BCLX) (DIST?) · 2026-06-12 15:27 → 20:59 (332 nến M1)

**Điểm: 5/10** — Khung range vẽ đúng chỗ, Phase A sạch; nhưng nhãn climax neo sai cây, mSOW gán sai vai, và 283 nến Phase B bỏ trống chỉ một nhãn.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX neo vào nến TRƯỚC nến mở range, thấp hơn biên chính 5.2 giá — luật vi phạm: L3 (biên chính = mức climax)
- **Thuật toán gắn:** BCLX tại 15:24, giá 4251.6, VSA 2.82x.
- **Đúng phải là:** nhãn phải nằm trên cây tạo ra biên chính trên 4256.8 — tức nến 15:27 (hoặc 15:26, high 4256.4).
- **Dấu hiệu quyết định trên chart:** phiếu ghi range bắt đầu 15:27 nhưng nhãn ở 15:24; trên ảnh chấm BCLX nằm hẳn **dưới** đường "biên CHÍNH trên 4256.8" — người đọc chart không thể hiểu vì sao biên trên lại ở một mức không có nhãn nào.
- **Nghi phạm trong thuật toán:** cửa sổ "cụm climax" 8 nến tách riêng mốc giá và mốc nhãn — đúng chỗ mục 13.1c ghi là **đã thử sửa rồi revert**.

### 2. Cây neo biên chính trên chỉ có VSA 1.06x — không phải climax — luật vi phạm: mục 3(1) THEORY / L1
- **Thuật toán gắn:** nến mở range 15:27 (VSA 1.06x, thân 0.40) làm mức climax 4256.8.
- **Đúng phải là:** nếu cây đỉnh chỉ 1.06x thì đây là **climax dạng cạn kiệt** (THEORY §6.2), không phải BCLX nổ volume — và không được đồng thời dán nhãn BCLX của cây 2.82x cách đó 3 nến vào nó.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến — cụm volume thật là −3/−2/−1 (2.82x / 2.48x / 1.91x), nến climax +0 chỉ 232 lot (1.06x), thấp hơn cả 3 nến trước nó.
- **Nghi phạm trong thuật toán:** mốc giá climax được phép trượt tự do theo cực trị trong 8 nến, không kiểm lại VSA của cây đích.

### 3. mSOW gán sai vai — phải là ST[B] — luật vi phạm: mục 5.1 bảng phân loại (ngưỡng "cú thăm dò mạnh")
- **Thuật toán gắn:** mSOW tại 19:35, giá 4223.2, VSA 1.11x.
- **Đúng phải là:** **ST[B]** (test nhẹ biên dưới). mSOW theo định nghĩa v6 là cú **đã phá được** nhưng không giữ được — cú này không phá được gì.
- **Dấu hiệu quyết định trên chart:** độ sâu = 4227.4 − 4223.2 = **4.2 giá**, ngưỡng "mạnh" = max(1.5 giá, 15% × 29.4 = **4.41 giá**) → **không đạt**; VSA 1.11x cũng dưới 2.2x. Trượt cả hai điều kiện mà vẫn được nhãn mSOW.
- **Nghi phạm trong thuật toán:** nhánh phân loại kết cục A đo độ sâu bằng **biên phụ đã bị chính cú đó nới ra** (4223.2 = đúng mức mSOW), nên phép so "sâu ≥ 15%" thành so chính nó với chính nó — lỗi thứ tự nới-biên mà 13.1c nói đã sửa, ở đây **còn dấu vết**.

### 4. Phase B 283 nến chỉ có đúng 1 nhãn — luật vi phạm: L9
- **Thuật toán gắn:** không UT[B] nào, SOT trên/dưới đều `none`, phiếu không có cả dòng nỗ lực↔kết quả.
- **Đúng phải là:** bias ghi `0` (test cả hai biên) thì phải có ít nhất **1 UT[B] + 1 ST[B]**. Trên ảnh, quanh 18:30 giá đẩy sát biên trên 4256.8 rồi dội — đó là UT[B] bị bỏ.
- **Dấu hiệu quyết định trên chart:** 283/332 nến (85% range) không có sự kiện nào; panel volume có ít nhất 4 thanh vàng (VSA ≥2.2x) trong Phase B không được đọc.
- **Nghi phạm trong thuật toán:** nhãn nhẹ chỉ sinh khi giá **thò ra ngoài biên chính quá 10 tick**; cú test dội **ngay dưới** biên không bao giờ được ghi.

## Đạt
- L1: MOVE tăng 42.5 giá / 40 nến / hiệu suất 0.39, chân move đọc được trên ảnh (~4200 → 4256) — climax đúng là cực trị chặn move, không nằm giữa move.
- L2: đủ 3 lần đổi hướng; **ST[A] 4254.1 chỉ cách mức climax 2.7 giá** (91% khoảng AR↔climax) — đây là ST[A] đúng nghĩa nhất trong cả lô, ngưỡng 0.55 mới ăn đúng ở ca này.
- L3: biên chính cố định suốt 332 nến; đúng 1 biên phụ dưới, tỷ lệ 1.14x.
- L4: không đặt tên khi range bị khe cuối tuần cắt — trung thực, không gò tên (đúng tinh thần Ca #20 nguồn 7.pdf).
- Range này **đáng vẽ**: 332 nến lùng bùng trong 29.4 giá là một vùng đấu giá thật, không phải nhiễu.

## Kết luận cấu trúc
Tôi vẫn vẽ range ở đây, cùng hai biên này. Sửa: dời nhãn BCLX về đúng cây đỉnh, hạ mSOW → ST[B], bổ sung UT[B] ở nhịp chạm biên trên quanh 18:30.
