# Chấm bài #42 — Tích lũy (ACC) · 2026-06-30 01:07 → 06:30 (323 nến M1)

**Điểm: 6/10** — Bài tốt nhất trong lô: climax thật, MOVE thật, ST[A] đúng chỗ, tên range đúng, CBR đủ SOS→LPS[D]. Sửa vài nhãn: Phase B trống 116 nến, LPS[C] rơi giữa range, SOS lẽ ra đã bị vô hiệu.

## Lỗi (nặng → nhẹ)

### 1. Phase B 116 nến không có một nhãn nào — luật vi phạm: L9
- **Thuật toán gắn:** B = 02:12 → 04:07, không UT[B], không ST[B], không mSOS/mSOW.
- **Đúng phải là:** bias ghi `+1` (chạm nổi biên trên, không với nổi biên dưới) — vậy phải có ít nhất một **UT[B]** ghi lại lần chạm biên trên đó. Trên ảnh giá nhiều lần đẩy lên vùng 3988–3992 rồi dội (quanh 02:45, 03:20, 03:55) mà không nhãn nào được đặt.
- **Dấu hiệu quyết định trên chart:** 116/323 nến (36% range) trắng nhãn, đúng lời chê "Phase B trống hàng trăm nến".
- **Nghi phạm trong thuật toán:** nhãn nhẹ chỉ sinh khi giá **thò ra ngoài biên chính quá 10 tick**; ở range này giá chưa lần nào thò ra nên Phase B im lặng hoàn toàn. Cần cho phép UT[B]/ST[B] ở cú **chạm** biên trong dung sai, không bắt buộc phải thò ra.

### 2. LPS[C] nằm ở 67% chiều cao range — sai nửa — luật vi phạm: L8
- **Thuật toán gắn:** LPS[C] @ 04:08, giá 3981.3.
- **Đúng phải là:** trong tích luỹ, LPS[C] là nhịp test **nửa dưới / gần biên dưới** — nơi chứng minh cung đã cạn. 3981.3 = (3981.3 − 3955.4) / 38.8 = **67% chiều cao**, tức nửa trên.
- **Dấu hiệu quyết định trên chart:** trên ảnh chấm LPS[C] nằm lửng giữa hai đường biên, ngay trên một nhịp pullback nhỏ của đoạn giá đang bò lên — nó không test biên nào.
- **Nghi phạm trong thuật toán:** v7.1 bỏ hẳn `_right_half` mà chỉ giữ `_in_range`. Ràng buộc "gần biên đang bị kiểm" rõ ràng chưa đủ chặt — 67% vẫn lọt.

### 3. SOS không bị vô hiệu dù giá lùi hẳn vào trong range — luật vi phạm: L10 + mục 7 câu 1 của chính thuật toán
- **Thuật toán gắn:** SOS 04:30 @ 4000.1 giữ nguyên hiệu lực suốt Phase D 121 nến.
- **Đúng phải là:** theo chính luật "đóng cửa lùi hẳn qua biên **chính** quá 30 tick trước khi đi được 50% tiến độ → cú phá BỊ VÔ HIỆU". Trên ảnh, đoạn 05:03–05:44 giá nằm dưới đường biên chính 3994.2, xuống tới ~**3986** (≈80 tick dưới biên) và ở đó gần 60 nến.
- **Dấu hiệu quyết định trên chart:** đọc từ ảnh (không có trong phiếu số liệu) — cụm nến giữa hai mốc 05:03 và 05:44 nằm rõ ràng bên dưới đường "biên CHÍNH trên 3994.2".
- **Nghi phạm trong thuật toán:** cửa sổ kiểm vô hiệu chỉ chạy **25 nến** sau SOS; giá lùi vào ở nến thứ ~35 nên không ai kiểm nữa. Kiểm vô hiệu nên chạy suốt Phase D, không chỉ trong cửa sổ retest.

### 4. Thiếu Phase E dù giá cuối cùng đi rất xa — luật vi phạm: L10
- Range đóng ở Phase D hết trần **121 nến**, không có Phase E. Nhưng trên ảnh, đúng sau đó (từ 06:25) giá bung lên **4045**, tức +51 giá trên biên chính = hơn 1.3× chiều cao range. Đó chính là Phase E, bị cắt mất vì trần cứng.

### 5. AR neo vào nến râu — nhẹ
- AR @ 01:29, VSA 1.37x, **thân 0.03**. Mức 3994.2 thì đúng (đỉnh nhịp bật 38.8 giá), nhưng cây neo là pin bar; đáng gắn cờ "(yếu)" như chính tài liệu mô tả mà không thấy gắn.

## Đạt
- **Climax đẹp nhất cả lô:** SC 01:07 — volume 2097 (VSA **7.11x**), biên độ **25.6 giá**, thân 0.86, nhãn đặt **đúng nến mở range**. Không có lỗi nhãn cụm climax ở bài này.
- L1: MOVE giảm 60.1 giá / 108 nến / hiệu suất 0.38, chân move rõ trên ảnh (4038 → 3955); climax là đáy chặn move.
- L2: ST[A] @ 3965.5 — cách climax **10.1 giá = 26% chiều cao**, nằm nửa dưới, đúng vai test lại vùng SC. Đây là ST[A] đúng nhất trong lô cùng với #37 và #41.
- L9: Phase B = 116 nến, dài nhất — đúng tỉ lệ.
- L3: không có biên phụ (tỷ lệ 1.00x) — trung thực, giá chưa lần nào thò ra ngoài biên chính. Đúng tinh thần "có thể không có biên phụ nào".
- L4: **ACC đúng** — origin SC, phá lên thật.
- L10 phần retest: SOS VSA 4.09x thân 0.69 → LPS[D] @ 3997.2 VSA **0.44x** (volume co lại) **giữ trên biên chính** — mẫu CBR sạch, đúng bài.

## Kết luận cấu trúc
Vẽ đúng chỗ, hai biên đúng. Tôi chỉ sửa nhãn: bổ sung UT[B] cho Phase B, dời LPS[C] xuống nhịp test nửa dưới (vùng 3970–3975 quanh 03:30), và kéo Phase E ra tới cú bung 06:25 thay vì đóng range ở trần Phase D.
