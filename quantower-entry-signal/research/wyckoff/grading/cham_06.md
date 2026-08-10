# Chấm bài #06 — Chưa rõ (BCLX) (DIST?) · 2026-04-02 14:43 → 2026-04-02 20:59 (223 nến M1)

**Điểm: 2/10** — Đây là bài duy nhất trong lô có thanh khoản thật, và cũng là bài phơi bày rõ nhất cái giá của ngưỡng ST[A] 0.55: Phase A nuốt gần trọn range.

## Lỗi (nặng → nhẹ)

### 1. Phase A = 180 nến, Phase B = 44 nến — luật vi phạm: L2 + L9
- **Thuật toán gắn:** A **180** nến (14:43 → 19:08) · B 44 nến. Phase A dài **gấp 4** Phase B và chiếm 81% cả range.
- **Đúng phải là:** Phase A phải kết thúc tại cú test lại vùng climax **đầu tiên**. Nhìn ảnh: sau AR (16:20, 4704.8) giá bật lên ~4735 lúc **17:05** rồi mới lùi tiếp — đó là ST[A] mà mắt người sẽ chọn, Phase A chỉ nên dài ~140 nến ít hơn, và toàn bộ đoạn 17:05 → 20:59 là Phase B (đủ dài để đọc cung-cầu). Thuật toán bỏ qua nhịp 17:05 rồi bám tiếp đến 19:08 mới chốt ST[A] tại 4742.1.
- **Dấu hiệu quyết định trên chart:** giữa AR và ST[A] có **thêm 3 lần đổi hướng** (lên 4735 → xuống 4710 → lên 4742). Theo L2, Phase A là **đúng 3 lần** đổi hướng; ở đây thuật toán đã đếm tới 5–6 lần mà vẫn coi là Phase A.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC = 0.55`. Ngưỡng cần hồi ≥ 0.55 × 57.4 = **31.6 giá** trên AR, tức ≥ 4736.4; nhịp 17:05 đạt ~4735 — **trượt đúng 1.4 giá**, và cái trượt đó kéo Phase A dài thêm ~120 nến. Đây là bằng chứng trực tiếp: nâng ngưỡng chữa được "ST[A] rơi lửng giữa range" nhưng đẻ ra "Phase A nuốt Phase B". Cần **điều kiện thoát kép**: chấp nhận ST[A] khi hồi ≥ 0.55, **hoặc** khi đã có thêm một cặp pivot đầy đủ sau AR (đủ 3 lần đổi hướng), lấy pivot nào đến trước.

### 2. Nến mở range có VSA 0.24x — không thoả chính điều kiện climax của thuật toán — luật vi phạm: L1
- **Thuật toán gắn:** mốc mở range = nến 14:43: **2 hợp đồng, VSA 0.24x, biên độ 3.7 giá**; mức 4762.2 của nó thành biên chính trên.
- **Đúng phải là:** điều kiện mở range đòi VSA ≥ 2.2x. Cây cao trào thật là **14:37 (20 lot, VSA 2.99x, biên độ 12.4 giá)** hoặc **14:44 (22 lot, VSA 2.38x)**. Đỉnh nên neo ở 4757.6, không phải một cái râu 2 lot.
- **Nghi phạm trong thuật toán:** cụm climax dời mức giá theo cực trị thuần tuý, không kiểm lại tính chất climax của cây được dời tới. Lặp lại đúng ở 4/6 bài lô này (#03, #04, #05, #06).

### 3. Nhãn BCLX rơi trước nến mở range và thấp hơn biên của chính nó — luật vi phạm: L3
- **Thuật toán gắn:** BCLX tại 14:36, giá 4756.0 — thấp hơn "biên CHINH tren 4762.2" 6.2 giá, và trước mốc mở range 7 phút.
- Ở bài này độ lệch nhỏ (6 giá) nên không phá hỏng cách đọc, nhưng vẫn là đúng lỗi cụm climax chưa sửa.

### 4. Range đóng `completed` mà chỉ có Phase A + B — luật vi phạm: mục 9 tài liệu thuật toán
- Không có Phase C/D/E, không kết luận hướng, nhưng trạng thái ghi **completed** chứ không phải "đang chạy" hay "chưa rõ hướng". Range bị khe cuối tuần cắt (04-02 20:59 → 04-05) — đúng luật cắt, nhưng nhãn trạng thái phải phản ánh việc **chưa đưa ra kết luận nào**.

### 5. (nhỏ) Ba chỉ số Phase B đều rỗng
- SOT trên/dưới = `none (n=0)`, không có nhịp nỗ lực↔kết quả nào được ghi, dù Phase B dài 44 nến và trên panel volume có mấy cột vàng rõ. Phase B mà không đọc được gì thì mục 5 (L9) coi như bỏ trống.

## Đạt
- Điều kiện mở range: MOVE 95.5 giá / 78 nến / hiệu suất 0.36, và cây climax **đúng là chặn đỉnh move** — đúng L1 về mặt hình.
- AR tại 4704.8 (VSA 1.20x, thân 0.73) là một cú bật ngược thật, có nỗ lực — đúng L2.
- Biên chính cố định suốt range, không kéo theo giá; không bịa biên phụ (tỷ lệ 1.00x) — đúng L3.
- Không ép đặt tên khi chưa có cú phá: để "Chưa rõ (BCLX)" — đúng L4, đúng thái độ mà Ca #20 nguồn 7.pdf yêu cầu (không gò dữ liệu cho khớp mô hình).
- Không có nhãn dư: chỉ 3 mốc BCLX/AR/ST[A], không spam UT/ST[B] — đúng L6.
