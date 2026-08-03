# Chấm bài #22 — Phân phối (DIST) · 2026-06-10 06:00 → 07:55 (115 nến M1)

**Điểm: 4/10** — Đọc đúng hướng (đây thật là một vùng phân phối và nó phá xuống thật), nhưng **vẽ sai khung**: cây gọi là BCLX nằm giữa move, nên biên chính chỉ bao được nửa vùng đấu giá và Phase A phình ra dài hơn Phase B.

## Lỗi (nặng → nhẹ)

### 1. Climax không chặn move — nó nằm GIỮA move — luật vi phạm: L1, mục chấm 1
- **Thuật toán gắn:** BCLX 06:00 @4232.9, VSA 2.29x, biên độ nến chỉ **4.5 giá**, đóng 4232.2 **sát đỉnh nến**.
- **Đúng phải là:** BCLX ở **06:08 @4245.5** — v=362 (VSA 2.77x, **lớn hơn** cây được gọi climax: 241 lot), thân **0.21** (đóng cửa rơi hẳn khỏi đỉnh) = chân dung cao trào mua chuẩn. Chỉ 3–4 nến sau "climax" giá đã tạo đỉnh cao hơn (06:03 H4233.4, 06:04 H4235.9) và còn đi thêm **12.6 giá** nữa.
- **Dấu hiệu quyết định trên chart:** đường nét đứt "biên phụ trên 4245.5" nằm cao hơn đường nét liền "biên chính trên 4232.9" ngay từ đầu range — biên phụ hình thành *trong Phase A*, tức chính cây climax đã bị vượt.
- **Nghi phạm trong thuật toán:** điều kiện (2) khi mở range chỉ kiểm climax là cực trị của cửa sổ **240 nến quá khứ**; không có bước xác nhận về sau (vd 20–30 nến sau không được tạo cực trị mới).

### 2. Biên chính chỉ bao 49% vùng đấu giá thật — luật vi phạm: L3
- **Thuật toán gắn:** biên chính 4220.6–4232.9 = 12.3 giá (0.29%); biên phụ 4220.6–4245.5 = 24.9 giá.
- **Đúng phải là:** TR thật là **4220.6–4245.5**; nét liền phải nằm ở 4245.5. Hệ quả kéo theo: mọi phép đo dựa trên chiều cao range (mục tiêu Phase E, ngưỡng "lùi hẳn") đều bị chia đôi.

### 3. ST[A] gán sai → Phase A dài hơn Phase B — luật vi phạm: L2 + L9
- **Thuật toán gắn:** ST[A] 07:16 @4225.9 (VSA 0.44x, thân 0.96), chỉ **3 nến** sau AR (07:13).
- **Đúng phải là:** đó là một nhịp nảy 3 nến / 5.3 giá giữa đà rơi, cách mức climax 7.0 giá và cách đỉnh thật 19.6 giá — **không phải test lại vùng climax**. ST[A] thật phải là nhịp hồi lên thử lại dải 4232.9–4245.5.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm *giữa* hai đường liền, ngay sát nhãn AR, chỉ cách 3 cây nến.
- **Nghi phạm trong thuật toán:** `STA_MIN_RETRACE = 0.40` đo theo chiều cao climax↔AR vốn đã bị co lại còn 12.3 giá → chỉ cần nảy 5 giá là "đạt" (43%); cộng `STA_CONFIRM_BARS = 5` quá ngắn.
- **Hệ quả:** Phase A **77 nến = 67% cả range**, Phase B chỉ 19 nến → vi phạm L9 (Phase B phải là phase dài nhất).

### 4. Nhãn SOW neo cây xác nhận, không neo cây phá — luật vi phạm: mục 9
- **Thuật toán gắn:** SOW 07:54 @4205.4, VSA 1.31x.
- **Đúng phải là:** cây **07:52** — L4205.1 **C4205.3**, v=348 (**VSA 3.17x**), thân **0.92**, đóng cửa 15.3 giá dưới biên chính dưới. Đó là MSOW.
- **Nghi phạm:** cùng gốc với bài #21 — `BREAK_HOLD_BARS = 3`.

### 5. Phase D = 1 nến, Phase E = 1 nến — trình bày, nhẹ
- Mục tiêu Phase E (12.3 giá dưới 4220.6 = 4208.3) đã bị vượt ngay tại cây SOW, nên D và E mỗi cái 1 nến. Nhãn D/E vì thế chỉ mang tính hình thức, **không có nhịp retest nào** — trái với mô tả CBR ở L10. Nếu chiều cao range được đo đúng (24.9 giá), mốc Phase E là 4195.7 và cấu trúc D→E sẽ có nội dung thật.

## Đạt
- **L1 (phần MOVE):** move tăng thật 38.7 giá / 75 nến / hiệu suất 0.38.
- **L4:** tên **Phân phối** đúng — origin move tăng + phá xuống, và kết cục xác nhận: giá rơi tiếp về **4178.5** lúc 10:08 (≈3× chiều cao biên chính).
- **L10:** cú phá là phá THẬT — đóng cửa hẳn ngoài biên và không quay lại (không có nến nào đóng trên 4220.6 sau 07:54).
- **L7:** LPSY[C] chỉ 1 điểm, đúng vai (nhịp hồi yếu trước cú rơi cuối).
- **L3 (phần quy tắc):** mỗi bên tối đa 1 biên phụ — chấp hành đúng.
