# Chấm bài #38 — Tích luỹ (ACC) · 2026-06-30 01:07 → 06:30 (323 nến M1)

**Điểm: 5/10** — bài khá nhất lô: Phase A/B dựng đúng, nhưng nửa sau (SOS → D → E) sai vai hoàn toàn, phải sửa nhãn.

## Lỗi (nặng → nhẹ)

### 1. SOS chọn cú phá đã BỊ VÔ HIỆU — luật vi phạm: L10, mục 5.1 THEORY (breakout phải giữ được)
- **Thuật toán gắn:** SOS 04:30 @ 4000.1 (VSA 4.09x), rồi LPS[D] 04:48 @ 3997.2, Phase D kéo 121 nến tới hết range.
- **Đúng phải là:** cú phá 04:30 **không giữ được**. Sau LPS[D], giá đóng cửa **lùi hẳn vào trong range** — nhìn chart, từ ~04:55 tới ~06:05 (hơn 70 nến) giá lình xình ở 3985–3993, tức là dưới biên chính trên 3994.2, có lúc thủng xuống 3985 (lùi 9.2 giá = hơn 3× dung sai 30 tick). Theo chính luật của thuật toán, đó là cú phá bị vô hiệu → phải hạ cấp thành **mSOS**, trả dải phase về B.
- **Cú phá THẬT nằm ở 06:15–06:25:** giá bứt từ 3995 lên 4045 với cụm volume lớn nhất nửa sau chart. Đó mới là SOS; Phase D/E phải nằm ở đó.
- **Dấu hiệu quyết định trên chart:** đường biên chính trên 3994.2 cắt ngang **giữa thân** cả cụm nến 04:55–06:05 — mắt nhìn thấy ngay giá đang ở trong range chứ không ngoài.
- **Nghi phạm trong thuật toán:** nhánh kiểm tra vô hiệu chỉ chạy trong **cửa sổ 25 nến** sau SOS (mục 7 câu 1). Giá lùi vào trong range ở nến thứ ~28 trở đi nên thoát guard. Cửa sổ 25 nến quá ngắn so với Phase D thực tế 121 nến.

### 2. Thiếu hẳn Phase E — luật vi phạm: L10
- **Thuật toán gắn:** dải phase dừng ở D (121 nến), không có E, range đóng 06:30.
- **Đúng phải là:** giá đã thật sự rời range lên 4045 (đi thêm hơn 1× chiều cao 38.8 giá) trong 06:15–06:30. Đó là Phase E rành rành, nhưng bị nuốt vào trong Phase D vì SOS đã bị chốt nhầm 105 nến trước đó.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của lỗi #1 — mốc đo "đi đủ xa" tính từ SOS sai nên Phase D nuốt trọn cả nhịp lình xình lẫn cú bứt thật.

### 3. Phase D (121 nến) dài thứ nhì, gần bằng Phase B (104) — luật vi phạm: L9, L10
- **Thuật toán gắn:** A=43 · B=104 · C=56 · D=121.
- **Đúng phải là:** D là "phá biên + retest", nó không được dài hơn cả B. Nếu sửa đúng lỗi #1 thì D chỉ còn ~10-15 nến quanh cú bứt 06:15, B kéo dài tới ~06:10 và đúng là phase dài nhất.

### 4. ST[A] không test lại vùng climax, rơi giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 01:49 @ 3974.5. Climax 3955.4, AR 3994.2, chiều cao 38.8 giá.
- **Đúng phải là:** ST[A] là lần thứ 3 đổi hướng, giá **quay về phía climax và bị chặn lần nữa** — nó phải áp sát vùng SC. 3974.5 nằm ở **49% chiều cao range**, cách climax 19.1 giá. Đó là một pivot giữa range, không phải test lại SC.
- **Dấu hiệu quyết định trên chart:** đáy sâu nhất suốt Phase B chỉ tới ~3968, cũng còn cách 3955 hơn 12 giá — nghĩa là cấu trúc này **thực tế không có ST[A]** nào cả. Đúng bài học Ca #2 nguồn 7.pdf: thiếu ST[A].
- **Nghi phạm trong thuật toán:** sửa #2 của v7 nâng ngưỡng hồi tối thiểu 0.2 → 0.4 khoảng AR↔climax; ca này hồi 0.51 nên **lọt qua ngưỡng mới**. Ngưỡng đặt sai chiều: cái cần ràng buộc là **khoảng cách ST[A] tới climax** (nên ≤ 25-30% chiều cao range), không phải độ sâu nhịp hồi so với AR.

### 5. LPS[C] chọn quá xa SOS, Phase C (56 nến) dài hơn Phase A (43) — luật vi phạm: L8
- **Thuật toán gắn:** LPS[C] 03:34 @ 3973.1, Phase C = 56 nến.
- **Đúng phải là:** Phase C là phase **ngắn nhất**. LPS[C] nên là nhịp lùi **cuối cùng** trước cú phá, không phải đáy cuối của Phase B. Trên chart có một nhịp lùi rõ quãng 03:55–04:05 (đỉnh ~3986 lùi về ~3979) — đó là LPS[C] hợp lý hơn, cho Phase C ~25 nến.
- **Nghi phạm trong thuật toán:** sửa #3 của v7 nới cửa sổ gán ngược từ 0.5x lên 0.8x len(B) = 83 nến. Nới rộng đã chữa được ca "Phase C biến mất" nhưng lại đẻ ra ca ngược: chọn pivot **quá xa** khiến Phase C phình. Cần thêm điều kiện chọn **pivot cuối cùng** trong cửa sổ, không phải pivot cực trị nhất.

## Đạt
- **Điều kiện mở range xuất sắc (L1):** MOVE giảm 60.1 giá / 108 nến, hiệu suất 0.38; climax VSA **7.11x**, biên độ nến 25.6 giá, đóng đúng tại đáy 3955.4 — climax thật sự chặn move, là cực trị thật. Đây là ca sạch nhất về mục 1 trong cả lô.
- **Biên chính đúng và cố định:** 3955.4 (SC) – 3994.2 (AR), không kéo theo giá (L3).
- **Không có biên phụ** — đúng, vì trong toàn range không có cú thăm dò nào ra ngoài biên chính (L3).
- **Phase B là phase dài nhất trong nhóm A/B/C** (104 nến) (L9).
- **Tên range đúng:** SC + phá lên thật = Tích luỹ (L4).
- **Chú thích nỗ lực/kết quả và SOT đọc đúng dấu:** er=0.53 → "HIỆU QUẢ"; SOT-up volume 1.36 → "HẤP THỤ", SOT-dn 0.47 → "cạn kiệt". Lỗi hard-code v6 đã hết.
