# Chấm bài #42 — Phân phối (DIST) · 2026-07-16 11:46 → 13:04 (78 nến M1)

**Điểm: 3/10** — **Không nên vẽ range ở đây.** 78 nến mà nhồi đủ Phase A→E với D = 1 nến, E = 1 nến; giá đi qua vùng này **một chiều** rồi rơi thẳng 28 giá. Đây là một đoạn xu hướng giảm bị cắt ngang bằng khung range, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range quá vụn — 78 nến nhồi 5 phase, Phase B không phải phase dài nhất — luật vi phạm: L9 + lỗi kinh điển "khung quá thô / range quá vụn" (CHART_CASES)
- **Thuật toán gắn:** A 45 nến · **B 16** · C 16 · **D 1** · **E 1**.
- **Đúng phải là:** Phase B phải là phase **dài nhất** (L9) — ở đây A dài gấp gần 3 lần B. Phase C (16) bằng đúng B nên cũng không thoả L8. Một cấu trúc mà D và E mỗi cái 1 nến thì không có "giai đoạn" nào cả.
- **Dấu hiệu quyết định trên chart:** biên dưới 4017.4 được chạm **đúng 1 lần** (chính cây AR), rồi bị xuyên luôn và giá không bao giờ trở lại. Theo CHART_CASES (mục "Cách xác định biên range"), biên dưới thường cần **2-3 lần chạm** mới coi là biên hợp lệ. Chưa có "cân bằng tương đối giữa cung và cầu" (THEORY §3.1) → chưa có TR.
- **Nghi phạm trong thuật toán:** không có ngưỡng tối thiểu về **số nến** hoặc **số lần chạm biên** để công nhận một range; guard duy nhất là chiều cao ≤3.5% và ≤2500 nến (mục 8). Ngoài ra mục 13.3 — chỉ theo dõi một range một lúc — làm bài #41/#42/#43 bị cắt thành 3 range liền kề trong khi trên M5/M15 chúng là **một** vùng.

### 2. Climax neo sai nến — luật vi phạm: L1 + L3
- **Thuật toán gắn:** BCLX 11:46 tại 4045.5.
- **Đúng phải là:** đỉnh cụm climax = **4048.4 (11:48)**, và đỉnh cao nhất cả range = **4048.7 (12:04)**. Biên chính trên phải neo vào đỉnh cụm BCLX, không phải nến đầu tiên đủ ngưỡng.
- **Dấu hiệu quyết định trên chart:** ngay 2 nến sau "climax", giá đóng cửa **4048.2** — trên cả mức được gọi là biên chính. Trên ảnh, cả cụm nến 11:48–11:56 nằm phía trên đường liền 4045.5.
- **Nghi phạm trong thuật toán:** giống bài #41 — mục 3 chỉ kiểm cực trị 240 nến quá khứ, không chốt cực trị của cụm climax.

### 3. Bỏ hẳn cú rũ ở biên trên (12:04–12:06) — luật vi phạm: mục 5.1 của chính spec + THEORY §6.4 (No Demand)
- **Thuật toán gắn:** không nhãn nào trong khoảng 11:47–12:15.
- **Đúng phải là:** nến 12:04 vượt biên chính 4045.5 lên **4048.7 (32 tick)** rồi 2 nến sau sụp — theo bảng mục 5.1 (cạnh climax BCLX, thăm dò > 15 tick) đây phải là **UT/UTAD**. Đọc theo lý thuyết thì càng rõ: nến 12:04 là nến **tăng, biên độ hẹp 2.0 giá, volume 76 (0.49x)** trong khi 2 nến sau đó volume 422 (2.52x) và 521 (2.94x) **giảm** — mẫu No Demand ở đỉnh rồi cung áp đảo, dấu hiệu yếu mạnh nhất của cả bài.
- **Dấu hiệu quyết định trên chart:** trên panel khối lượng, 2 thanh cao đầu tiên của range nằm ngay sau đỉnh 4048.7 và đều là nến đỏ.
- **Nghi phạm trong thuật toán:** mục 5 chỉ bắt đầu theo dõi cú thò biên **sau khi Phase A đã chốt**; Phase A ở đây kéo tới 12:30 nên cú rũ 12:04 nằm trong "vùng mù". Đây là hệ quả trực tiếp của việc Phase A quá dài (xem lỗi #4).

### 4. ST[A] giữa range, không test được vùng BCLX — luật vi phạm: L2 + THEORY §5
- **Thuật toán gắn:** ST[A] 4034.5 @12:30.
- **Đúng phải là:** 4034.5 = **60.8% chiều cao range**, cách biên trên 11.0 giá → 1/3 giữa, không có vai. Đúng ra tín hiệu ở đây phải đọc là "**ST không chạm nổi đỉnh → LPSY sẽ là event của Phase C**" (THEORY §5, dòng Phase B phân phối) — tức dấu hiệu yếu, chứ không phải mốc chốt Phase A.
- **Nghi phạm trong thuật toán:** ngưỡng ST[A] hồi ≥40% chiều cao (mục 4.2) — quá lỏng, giống bài #41/#45.

### 5. LPSY[C] đặt **bên ngoài** biên dưới, sau khi biên đã bị phá — luật vi phạm: L8 (Phase C là tín hiệu TRƯỚC cú phá) + Ca #3 (4.pdf: LPSY[C] vs LPSY[D])
- **Thuật toán gắn:** LPSY[C] 4012.9 @12:47.
- **Đúng phải là:** 4012.9 **thấp hơn biên chính dưới 4017.4 4.5 giá** → lúc đó cú phá đã xảy ra rồi, nhãn này thuộc vai **LPSY[D]** (hồi retest sau SOW), không phải LPSY[C].
- **Dấu hiệu quyết định trên chart:** nến 12:40 đã **đóng cửa 4013.7** dưới biên (VSA 3.15x, thân 0.93), rồi 12:43 đóng 4007.5 (VSA 3.36x, thân 0.94). Nhìn ảnh, nhãn LPSY[C] nằm hẳn dưới đường liền 4017.4.

### 6. SOW trễ 23 nến / 24.6 giá — luật vi phạm: L10 + Ca #5 (4.pdf, neo giá đóng cửa)
- **Thuật toán gắn:** SOW 13:03 tại 3989.1 (VSA 1.18x) → Phase D và E mỗi cái 1 nến.
- **Đúng phải là:** SOW tại **12:40** (close 4013.7, VSA 3.15x, thân 0.93). Nhãn hiện tại nằm đúng **1.0 lần chiều cao range (28.3 giá)** dưới biên — tức mục tiêu Phase E đã hoàn tất trước khi nhãn SOW được vẽ.
- **Nghi phạm trong thuật toán:** chuỗi xác nhận 3 nến + 30 tick (mục 5.1) cộng với việc Phase C phải "sống" đủ trước khi sang D.

## Đạt
- **L1 (hình thức):** có MOVE tăng trước climax — 19.3 giá / 21 nến, hiệu suất **0.73** (cao nhất trong 5 bài); AR là cú bật ngược thật (28.1 giá, VSA 8.14x — cây bán tháo lớn nhất chart).
- **L4:** nếu buộc phải đặt tên thì origin BCLX + phá xuống = Phân phối — đúng logic 4 pattern.
- **L7:** LPSY chỉ 1 điểm, không spam.
- Không nhầm UT ↔ UTAD, không gán SC trong tái tích luỹ.

## Cần hỏi người học
- Có nên đặt **ngưỡng cứng tối thiểu** cho một range (ví dụ ≥150 nến M1, hoặc biên dưới/biên trên mỗi bên phải có ≥2 lần chạm) trước khi cho phép vẽ? Bài này thoả mọi luật L1-L10 về mặt chuỗi sự kiện nhưng nhìn mắt thì rõ ràng chỉ là một đoạn markdown.
