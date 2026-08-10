# Chấm bài #09 — Chưa rõ (SC) (ACC?) · 2026-04-19 23:43 → 2026-04-21 16:59 (1288 nến M1)

**Điểm: 2/10** — Không nên vẽ range như thế này. AR bắt trễ 23 tiếng làm biên trên và Phase A sai hẳn, kéo theo toàn bộ cấu trúc phía sau.

## Lỗi (nặng → nhẹ)

### 1. AR bắt trễ 23 giờ → Phase A 881 nến, biên chính trên bị kéo theo giá — luật vi phạm: L2, L3
- **Thuật toán gắn:** `SC 04-19 23:43 · 4793.0` → `AR (yếu) 04-20 22:21 · 4890.7`. Phase A = 881 nến.
- **Đúng phải là:** AR là **cú bật ngược đầu tiên** bị chặn ngay sau climax. Trên ảnh, ngay sau SC giá bật một mạch lên vùng ~4866 trong khoảng 04-20 01:00–02:00 rồi bị chặn — **đó** mới là AR, biên chính trên phải là mức đó. Mức 4890.7 lúc 22:21 là đỉnh của cả một ngày dao động, lấy nó làm AR = kéo biên chính chạy theo giá, đúng cái L3 cấm.
- **Dấu hiệu quyết định trên chart:** giữa SC và "AR" có ít nhất 4-5 chu kỳ lên-xuống đầy đủ (đọc trên ảnh vùng 04-20 01:00 → 04-20 18:00), tức đã có nhiều hơn 3 lần đổi hướng từ lâu.
- **Nghi phạm trong thuật toán:** AR đang lấy **cực trị ngược hướng trong cửa sổ tìm kiếm**, không lấy **swing đầu tiên bị chặn**. Cần chốt AR tại đảo chiều đầu tiên vượt ngưỡng biên độ tối thiểu, và đóng cửa sổ AR sau N nến.

### 2. Phase A (881) dài gấp gần 3 lần Phase B (322) — luật vi phạm: L2, L9
- Phase B **phải là phase dài nhất**; ở đây Phase A nuốt 68% range. Hệ quả trực tiếp của lỗi #1.

### 3. ST[A] rơi lửng giữa range — luật vi phạm: L2 (ngưỡng 55% chưa cứu được ca này)
- **Thuật toán gắn:** `ST[A] 04-21 06:02 · 4830.8`.
- **Đúng phải là:** ST[A] là cú quay lại **test vùng climax**. Climax 4793.0, AR 4890.7 → 4830.8 nằm cách đáy 37.8 giá, tức ở **39% chiều cao range** — giữa range, không phải vùng climax. Nó thoả 61% ngưỡng hồi mới (≥55%) nhưng vẫn sai bản chất.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] trên ảnh nằm ngang tầm 4830, cách xa hẳn đường biên chính dưới 4793.0.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC` đo hồi **từ phía AR**, nên range càng cao thì ST[A] càng dễ dừng giữa đường. Phải thêm ràng buộc tuyệt đối phía climax: ST[A] chỉ hợp lệ khi nằm trong ~25–30% chiều cao range tính từ mức climax (hoặc trong K×ATR quanh climax).

### 4. Không đặt tên range dù đã phá xuống rõ — luật vi phạm: L4
- **Thuật toán gắn:** tên = "Chưa rõ (SC) (ACC?)", trạng thái `superseded` — "không đặt tên 4 mẫu hình".
- **Đúng phải là:** L4 nói rõ phá sai hướng **không huỷ range, chỉ đổi tên**. Move trước là giảm → SC; phá **xuống** thật (SOW 4776.8, dưới cả biên phụ 4777.6) → range này là **Tái phân phối (RE-DIST)**. Việc một range con mới sinh ra từ cú phá không xoá tên của range mẹ.
- **Nghi phạm trong thuật toán:** nhánh `superseded` đang bỏ qua bước đặt tên. Đặt tên và "bị thay thế" là hai thuộc tính độc lập.

### 5. Nhãn mSOW gắn sai Phase — luật vi phạm: tính nhất quán phase (THEORY §4.2)
- `mSOW 04-21 16:03` ghi Phase **B**, nhưng bảng Phase cho thấy Phase B kết thúc 15:23 và 16:03 nằm trong **Phase C** (15:24–16:32). Nhãn và khung phase mâu thuẫn nhau trong cùng một phiếu.

### 6. Range 1288 nến không phải một vùng đấu giá — cảnh báo cấu trúc (Ca #20 CHART_CASES)
- Nhìn ảnh: giá đi từ 4793 lên 4890 rồi xuống 4776 — đó là **một sóng tăng rồi một sóng giảm**, không phải một vùng cân bằng. Vẽ TR bao trọn 21 giờ như thế là gò dữ liệu cho khớp mô hình. Nếu là tôi: không vẽ range ở đây, hoặc chỉ vẽ TR nhỏ quanh vùng 04-21 05:00–17:00.

## Đạt
- **L1:** có move giảm 34.1 giá / 43 nến bị chặn đúng tại cây SC (low 4793.0, VSA 11.74x, biên độ 22 giá) — cây climax này là climax thật, rất rõ.
- **L8:** Phase C 60 nến < Phase B 322 nến; LPSY[C] 4804.8 nằm cách biên chính dưới 11.8 giá (12% chiều cao range) — đúng "gần biên", đây là điểm sáng của bản vá bỏ ràng buộc nửa range.
- **L7:** LPSY[C] chỉ đánh 1 điểm, không vẽ vùng.
- **L6:** không còn ST[B].
