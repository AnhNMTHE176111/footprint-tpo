# Chấm bài #23 — Phân phối (DIST) · 2026-06-12 08:18 → 13:31 (313 nến M1)

**Điểm: 3/10** — Hướng cuối cùng đúng (vùng này phân phối thật), nhưng **cả ba mốc quan trọng đều sai chỗ**: climax nằm giữa move, SOW gắn vào một nến rác, và Phase D thực chất là nhịp hồi ngược *vào trong* range — cây phá vỡ thật xảy ra 9 nến sau khi range đã bị đóng.

## Lỗi (nặng → nhẹ)

### 1. SOW gán vào nến yếu nhất vùng, bỏ mất cây phá thật — luật vi phạm: mục 9 + L5 (phá THẬT phải đóng cửa hẳn ngoài biên và giữ được)
- **Thuật toán gắn:** SOW 13:06 @4215.6, **VSA 0.61x**, v=95, thân 0.47.
- **Đúng phải là:** vào lúc 13:06 giá đã **hồi lên 8.3 giá từ đáy 4207.3 (13:00)** tạo trước đó — không có gì bị phá tại nến này. Cây phá thật là **13:40**: O4228.0 H4228.6 L4211.5 **C4212.0**, v=**1172** (VSA **5.58x**), biên độ 17.1 giá, thân **0.94** → đó là MSOW. Nhưng 13:40 nằm **9 nến sau** thời điểm range bị đóng (13:31).
- **Dấu hiệu quyết định trên chart:** thanh khối lượng cao nhất toàn ảnh nằm ở mép phải, **ngoài** khung range đã vẽ.
- **Nghi phạm trong thuật toán:** SOS/SOW phải vượt **biên phụ**, mà biên phụ dưới (4218.1) lại do chính cú thăm dò DA ở Phase B nới ra → điều kiện phá bị đẩy xuống thấp hơn; đến khi đủ 3 nến giữ ngoài biên thì cú rơi đã kết thúc và giá đang bật lên.

### 2. Phase D là nhịp hồi VÀO TRONG range, không phải CBR — luật vi phạm: L10
- **Thuật toán gắn:** Phase D 26 nến (13:06 → 13:31), range "completed".
- **Đúng phải là:** **11/26 nến Phase D đóng cửa TRÊN biên chính dưới 4223.6** (cao nhất C4229.8 lúc 13:38, đỉnh 4231.2) — cú phá 12:35–13:00 đã bị **từ chối**. Theo L5 đó là một SOW **thất bại** → phải lùi về Phase B và chờ, chứ không được chốt Phase D rồi đóng range.
- **Dấu hiệu quyết định trên chart:** đoạn nến ngay dưới nhãn Phase D leo lên **cắt qua** đường liền 4223.6 rồi đi tiếp lên 4231.
- **Nghi phạm trong thuật toán:** `_try_lps_and_phase_e()` **đã phát hiện** thất bại (nến 13:08 đóng 4221.5 > biên phụ 4218.1 + dung sai 3.0 → `failed = True`, hàm trả `False`), nhưng call site (dòng ~604) **bỏ giá trị trả về**, nên range vẫn được đóng và vẫn được đặt tên "Phân phối".

### 3. Climax nằm giữa move — luật vi phạm: L1, mục chấm 1
- **Thuật toán gắn:** BCLX 08:18 @4240.3, VSA 2.89x — nến này **đóng cửa đúng bằng đỉnh nến (C = H = 4240.3)**, tức không có bên bán nào chặn nó.
- **Đúng phải là:** nến +1 đã tạo H4241.5 và đỉnh thật của Phase A là **4249.6 lúc 09:48** — 90 phút và 9.3 giá sau "climax". Cây 08:18 là một cây bứt phá, không phải cây cao trào. Biên chính trên 4240.3 vì thế nằm 9.3 giá dưới kháng cự thật.
- **Nghi phạm:** cùng gốc bài #22 — điều kiện climax chỉ kiểm cực trị của cửa sổ quá khứ, không xác nhận về sau; thêm việc **không kiểm vị trí đóng cửa trong nến** (một cây climax chặn move phải đóng cửa lùi khỏi cực trị).

### 4. DA gán cho một minor SOW — luật vi phạm: THEORY §4.4 / §5 (test ở đáy trong phân phối = dấu hiệu yếu kém, mSOW ở Phase B)
- **Thuật toán gắn:** DA 11:32 @4218.1, VSA 2.44x.
- **Đúng phải là:** **mSOW[B]** — cú này thọc **5.5 giá (55 tick)** dưới biên chính dưới 4223.6 và có nến đóng cửa dưới biên (min close Phase B = 4220.1), kèm volume trên trung bình. Đó không phải "thăm dò nhẹ" (ngưỡng nhẹ của chính thuật toán là < 15 tick).
- **Nghi phạm:** bảng 5.1 gán **mọi** cú phá cạnh AR thành UA/DA bất kể độ sâu và volume — nên một mSOW rõ ràng bị hạ cấp thành test nhẹ, và tệ hơn: nó nới biên phụ, làm hỏng luôn điều kiện xác nhận SOW (lỗi 1).

### 5. Phase A 135 nến > Phase B 102 nến — luật vi phạm: L9
- Hệ quả trực tiếp của lỗi 3: vì climax bị đặt sớm 90 phút, toàn bộ vùng tạo đỉnh bị gộp vào Phase A (43% cả range).

### 6. Nhãn AR lệch khỏi biên chính 1.0 giá — trình bày/logic, nhẹ
- Nhãn AR ghi 4224.6 (10:26) nhưng biên chính dưới vẽ ở **4223.6** (đáy 10:28). Cùng một bug với bài #25 (ở đó lệch 20.7 giá): trong state `A_st`, dòng `r.ar_i, r.ar_price = i, b['lo']` cập nhật biên nhưng **không cập nhật sự kiện AR đã vẽ**.

## Đạt
- **L1 (phần MOVE):** move tăng thật 49.2 giá / 45 nến / hiệu suất **0.55** — cao nhất trong 5 bài.
- **L2 (mức ST[A]):** ST[A] 4239.4 đúng là test lại **mức climax 4240.3** (lệch 0.9 giá) — chọn đúng vùng, chỉ sai vì mức climax gốc đã sai.
- **L4:** tên **Phân phối** khớp kết cục — giá về **4197.5** lúc 14:47.
- **L3 (quy tắc biên phụ):** mỗi bên đúng 1 biên phụ (4218.1 / 4249.6), giữ cái xa nhất.
- **L8:** Phase C 51 nến, ngắn hơn cả A và B.
