# Chấm bài #10 — Tích luỹ (ACC) · 2026-05-04 15:21 → 2026-05-05 08:45 (421 nến M1)

**Điểm: 4/10** — Bài có **nền tốt nhất trong 5 bài**: MOVE sạch nhất (hiệu suất 0.73), climax là một nến thật, và lần đầu **AR khớp đúng biên chính**. Nhưng tỉ lệ phase bị đảo ngược hẳn (Phase C dài nhất, đúng bằng 2 lần timeout 121 nến), cú Spring thật bị gọi là ST[A] trong khi hai cú nông hơn được gọi Spring/Shakeout, và SOS gán vào một nến doji 0.30x. Giữ range, vẽ lại nhãn.

## Lỗi (nặng → nhẹ)

### 1. Phase C dài nhất range, và cả hai đoạn C đúng bằng mốc timeout — luật vi phạm: L8, L9
- **Thuật toán gắn:** A(45) → B(**5**) → C(**121**) → B(23) → C(**121**) → B(81) → D(26). Tổng C = **242 nến = 57% cả range**; tổng B = 109 nến.
- **Đúng phải là:** L8 — Phase C là phase **ngắn nhất**; L9 — Phase B là phase **dài nhất**. Ở đây ngược hẳn cả hai.
- **Dấu hiệu quyết định trên chart:** hai đoạn Phase C dài **đúng 121 nến** — bằng chính mốc "chờ quá 120 nến thì coi là thất bại" của thuật toán. Nghĩa là hai dải Phase C trên ảnh không phải cấu trúc đọc được từ giá, mà là **hai lần đếm hết đồng hồ**. Thêm nữa "Phase B (5n)" dài 5 nến thì không phải phase.
- **Nghi phạm trong thuật toán:** khi cú rũ hết hạn 120 nến (mục 6), đoạn chờ đó **vẫn bị tính là Phase C** trước khi lùi về B. Phải xử lý ngược lại: cú rũ thất bại thì **xoá luôn đoạn Phase C** đó, trả cả đoạn về Phase B — đúng như giảng viên sửa ở Ca #10 nguồn 2.pdf (Failed SOS vẫn thuộc Phase B, chưa sang C) và Ca #1/#8 (thu hẹp Phase C lại quanh đúng nhịp test cuối).

### 2. Cú Spring thật bị gọi ST[A]; hai cú không phải Spring lại được gọi Spring/Shakeout — luật vi phạm: CHART_CASES Ca #19 nguồn 2.pdf, L2
- **Thuật toán gắn:** ST[A] tại 16:10 giá **4545.6**; Spring (thất bại) tại 16:16 giá **4554.4**; Shakeout (thất bại) tại 20:20 giá **4556.5**.
- **Đúng phải là:** 4545.6 **là giá thấp nhất của cả TR** (chính là biên phụ dưới) ⇒ theo luật tường minh của giảng viên, **chỉ nó** đủ điều kiện Spring/Terminal Shakeout. Hai điểm 4554.4 và 4556.5 nằm cao hơn nó **8.8 và 10.9 giá**, chúng là **LPS[C] / test biên dưới**, không phải Spring.
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm ST[A] là điểm thấp nhất toàn bộ range (nằm sát nét đứt 4545.6), còn hai nhãn "Spring (thất bại)" và "Shakeout (thất bại)" đều nằm **cao hơn** nó rõ rệt. Về vai: một "ST[A]" chọc xuống dưới mức SC tới **15.2 giá = 55% chiều cao range** thì không phải test (test phải có spread/volume co lại khi *tiệm cận* SC — THEORY §3.3), nó là cú rũ.
- **Nghi phạm trong thuật toán:** hai chỗ. (a) Bước tìm ST[A] (mục 4.2) không chặn ST[A] vượt quá mức climax bao nhiêu — nên thêm trần, vượt quá thì phải đổi vai thành Spring/Shakeout hoặc dời chính climax. (b) Cú rũ đang được đo với **biên chính** (mục 10) thay vì với cực trị thấp nhất TR — cùng lỗi gốc như bài #09.

### 3. SOS gán vào nến doji khối lượng 0.30x, trong khi cây SOS thật bị gọi UA — luật vi phạm: mục 8 Effort vs Result, L3, THEORY §3.3
- **Thuật toán gắn:** UA 05-05 06:01 giá 4596.1, VSA **4.00x**, thân **0.91** → coi là thăm dò nhẹ. SOS 05-05 08:05 giá **4596.1**, VSA **0.30x**, thân **0.00**.
- **Đúng phải là:** đảo lại. Cây 06:01 đóng cửa vượt biên chính trên 4588.3 với khối lượng **gấp 4 lần** trung bình và thân 0.91 — đó là **SOS (tối thiểu là minor SOS)**, đúng ca "hành động ở UT được xem là minor SOS" (Ca #16 nguồn 7.pdf) và "SOS phải ở đỉnh mới cao hơn" (Ca #18 nguồn 2.pdf), vì 4596.1 là đỉnh mới cao nhất của cả range. Cây 08:05 là nến doji khối lượng bằng **1/3 trung bình**, không mang nỗ lực nào.
- **Dấu hiệu quyết định trên chart:** hai nhãn UA và SOS ghi **cùng một giá 4596.1** nhưng cách nhau 2 tiếng và khác nhau một trời một vực về chất: 4.00x/thân 0.91 so với 0.30x/thân 0.00. Thêm nữa theo L3, SOS phải **đóng cửa bứt qua biên phụ** (4596.1) — cây 08:05 chỉ *bằng* mức đó, chưa qua.
- **Nghi phạm trong thuật toán:** định nghĩa "thăm dò NHẸ" ở mục 5.1 là `< 15 tick **và** VSA < 3.3x`. Cây 06:01 xuyên **78 tick** và VSA 4.00x nên **không** phải thăm dò nhẹ, nhưng bảng 5.1 lại quy định cạnh AR thì luôn ra UA/DA "vẫn không quyết định". Chính dòng đó chặn không cho nó thành SOS. Cần cho phép cạnh AR sinh SOS/mSOS khi cú phá đủ sâu + đủ khối lượng + thân lớn.

### 4. Climax nên là VÙNG 15:19-15:21, không phải một điểm — luật vi phạm: CHART_CASES Ca #12 nguồn 2.pdf ("SC là một vùng TR nhỏ")
- **Thuật toán gắn:** SC tại 15:21 (khối lượng 30, VSA 2.70x, biên độ 19.0 giá, thân 1.00).
- **Đúng phải là:** đỉnh nỗ lực nằm ở nến **15:19**: khối lượng **76**, VSA **8.04x** — cao gấp 3 lần nến được gọi climax. Cặp 15:19 + 15:21 (một cây nổ khối lượng, một cây mở rộng biên độ tạo đáy) là **một vùng cao trào bán**, giảng viên khoanh vùng cho ca này chứ không chấm điểm.
- **Dấu hiệu quyết định trên chart:** panel khối lượng có một cột vàng vượt trội hẳn ngay trước cột của nến climax — thấy rõ trên ảnh ở mốc 05-04 15:05-15:21.
- **Nghi phạm trong thuật toán:** chọn climax theo **cực trị giá**, không đối chiếu với **đỉnh khối lượng** trong vài nến quanh đó. Đây là lỗi nhẹ (vị trí lệch 2 nến, mức giá vẫn đúng), xếp sau ba lỗi trên.

### 5. Thiếu Phase E và LPS[D] — luật vi phạm: L10
- Phase D 26 nến, không nhãn LPS[D], không Phase E. Đích Phase E = 1.0 × 27.5 giá ⇒ 4615.8; giá chỉ lên tới ~4605 trong cửa sổ 25 nến. Trên ảnh giá **giữ được** trên biên 4588.3 sau cú phá (đúng tinh thần CBR của L10), nhưng nhịp hồi retest ở 07:13-07:30 lại không được đánh dấu ⇒ CBR chỉ đúng một nửa trên nhãn.

## Đạt
- **Điều kiện mở range tốt nhất trong 5 bài (L1):** MOVE 68.9 giá / 31 nến / hiệu suất hướng **0.73** — trên ảnh là một cú rơi thẳng đứng từ 4630 xuống 4560, không thể lẫn với đi ngang. Climax là nến thật: biên độ **19.0 giá**, thân **1.00**, khối lượng 30.
- **AR khớp đúng biên chính trên (L3) — lần duy nhất trong 5 bài:** AR 4588.3 = biên CHÍNH trên 4588.3, hồi 27.5 giá = 40% độ dài move, VSA 2.38x. Đây là bằng chứng chẩn đoán quan trọng: lỗi "AR bỏ rơi" ở #06/#07/#09 xảy ra vì AR thật nằm **ngoài** cửa sổ 40 nến, còn ở đây nó nằm ở nến +17 nên bắt đúng.
- **Tên range đúng (L4):** SC chặn move giảm + phá thật lên = Tích luỹ.
- **Biên phụ đúng L3:** đúng 1 cái mỗi bên (4545.6 dưới / 4596.1 trên), cả hai là cực trị xa nhất thật.
- **Đọc được hấp thụ trên ảnh (mục 8):** từ 05-04 19:00 đến 05-05 03:00 khối lượng co lại rõ trong khi đáy nâng dần 4556 → 4572 → 4588 — đúng hình "hấp thụ theo chiều ngang" (THEORY §8: `S<, D>`, đỉnh/đáy cao dần ở gần cuối TR). Cấu trúc tích luỹ này là thật, không gò ép.
- **Không có ST[B] (L6); LPS[C] chỉ một điểm (L7).**

## Cần hỏi người học
- Khi ST[A] chọc **sâu hơn** mức climax quá nhiều (ở đây 15.2 giá = 55% chiều cao range), anh muốn thuật toán xử thế nào: (a) dời luôn climax về đáy mới, (b) giữ climax và đổi vai ST[A] thành Spring/Terminal Shakeout của Phase A, hay (c) bỏ ứng viên? Tài liệu không phân xử ca này.
