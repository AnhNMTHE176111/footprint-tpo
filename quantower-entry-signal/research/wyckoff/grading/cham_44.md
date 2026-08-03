# Chấm bài #44 — Tái tích luỹ (RE-ACC) · 2026-07-17 13:39 → 15:53 (134 nến M1)

**Điểm: 7/10** — **Bài tốt nhất trong lô.** Cấu trúc đọc đúng từ đầu đến cuối (BCLX chặn move tăng → AR → ST[A] test vượt đỉnh → LPS[C] → phá lên = tái tích luỹ), chỉ cần **dịch mốc SOS về đúng nến phá** và **thêm LPS[D]**.

## Lỗi (nặng → nhẹ)

### 1. SOS gán trễ 24 nến — bỏ mất cây phá biên mạnh nhất cả range — luật vi phạm: L10 + Ca #5 (4.pdf: ranh giới phase neo giá đóng cửa)
- **Thuật toán gắn:** SOS 15:28 tại 4014.8, **VSA 0.66x**, thân 0.56 → Phase D bắt đầu 15:28.
- **Đúng phải là:** SOS tại **15:04** — nến đóng cửa **4016.8** (vượt biên phụ 4008.9 tới 7.9 giá = 79 tick), **VSA 7.46x** (volume 1270), thân 0.76. Đó là cây phá biên đúng nghĩa "spread mở rộng + volume tăng" (THEORY §3.3). Phase C phải kết thúc tại 15:04.
- **Dấu hiệu quyết định trên chart:** trên panel khối lượng, thanh vàng cao nhất nửa sau chart nằm ở 15:04 — chứ không ở 15:28 (nơi nhãn SOS đang đứng, volume chỉ 2/3 trung bình). Nhãn SOS hiện cách biên phụ 5.9 giá, tức giá đã đi 26% chiều cao range trước khi được công nhận.
- **Nghi phạm trong thuật toán:** chuỗi xác nhận "3 nến liên tiếp đóng vượt biên phụ ≥30 tick, thân ≥45%" (mục 5.1). Sau cây 15:04, giá hồi về 4009.8–4011.3 — dưới mốc 4008.9+30tick = 4011.9 — nên nến thứ 2/thứ 3 không thoả, xác nhận bị đẩy tới 15:28. Cần **hồi tố nhãn về nến phá đầu tiên** sau khi chuỗi xác nhận hoàn tất.

### 2. Thiếu LPS[D] — mất đúng nhịp retest làm nên CBR — luật vi phạm: L10 + L7
- **Thuật toán gắn:** không có LPS[D] nào.
- **Đúng phải là:** nhịp **15:06–15:08** hồi về đóng cửa 4010.7 / 4009.8 / 4011.3 — **giữ được trên biên phụ 4008.9** rồi đi tiếp. Đây chính là "phá biên → hồi về retest nhưng giữ được ở ngoài biên" của L10, phải đánh 1 điểm LPS[D] (đáy nhịp).
- **Dấu hiệu quyết định trên chart:** trên ảnh thấy rõ cụm nến nhỏ nằm sát phía trên đường liền 4007.9 / nét đứt 4008.9 trong khoảng 15:06–15:20 trước khi giá bung lên 4020+.
- **Nghi phạm trong thuật toán:** LPS[D] chỉ được tìm **sau** khi SOS được phát (mục 7). Vì SOS phát trễ tới 15:28, nhịp retest thật (15:06–15:08) đã nằm **trước** nhãn SOS nên không bao giờ được xét. Đây là hệ quả trực tiếp của lỗi #1.

### 3. Phase B không phải phase dài nhất — luật vi phạm: L9 (và L8 ở mức nhẹ)
- **Thuật toán gắn:** A 42 · B 34 · C 33 · D 25 · E 1.
- **Đúng phải là:** B phải dài nhất; ở đây A > B, và C (33) ≈ B (34) nên Phase C cũng không phải phase ngắn nhất.
- **Dấu hiệu quyết định trên chart:** với 134 nến thì mỗi phase chỉ còn ~30 nến — cấu trúc chưa "ra hình" ở khung M1. Nếu sửa mốc SOS về 15:04 thì B kéo dài tới 15:03 (43 nến) và C co lại còn ~9 nến → **cả L8 và L9 tự động đúng**. Tức lỗi này cũng là hệ quả của lỗi #1, không phải lỗi độc lập.

## Đạt
- **L1 điều kiện mở range — ca mẫu:** MOVE tăng 44.9 giá / 38 nến (hiệu suất 0.47), 4 nến trước climax volume tăng dần 2.07x → 3.94x → 3.10x → 3.50x, rồi cây climax **VSA 4.61x, biên độ 13.5 giá, thân chỉ 0.12** (high 4007.9, close 3997.4) — nến râu dài chặn đứng đợt tăng. Đúng nghĩa BCLX.
- **Climax neo đúng nến** — khác cả 3 bài #41/#42/#45: 4007.9 là đỉnh thật, các nến sau đều thấp hơn.
- **L2 Phase A:** đủ 3 lần đổi hướng; AR = 3984.8 (bật 23.1 giá = 51% độ dài move, đáy nhịp thật); **ST[A] = 4008.9 vượt qua mức BCLX 1.0 giá** với VSA 1.87x rồi đóng cửa lùi về 4005.1 → đây là test lại vùng climax **đúng chuẩn**, phase A chốt đúng tại đó.
- **L3 biên:** biên chính 3984.8–4007.9 cố định; biên phụ trên 4008.9 sinh ra đúng từ ST[A] vượt climax — đúng nguyên văn L3. Không bị kéo theo giá.
- **L4 tên range:** origin BCLX + phá lên thật = **Tái tích luỹ** — đúng.
- **L8 case khó:** không có cú rũ nào → Phase C gán ngược từ LPS[C] 3997.2 @14:55, **VSA 0.66x** (volume co lại = dấu hiệu test đúng), là đáy nhịp cuối trước cú bứt. Chọn hợp lý.
- **L7:** LPS[C] chỉ 1 điểm, không spam nhãn.
- **Phase E** đạt và range đóng gọn — không có vòng lặp D→B→D.

## Cần hỏi người học
- Không có chỗ bế tắc lý thuyết ở bài này. Chỉ cần chốt quy tắc "nhãn SOS/SOW hồi tố về nến phá đầu tiên" là bài này lên gần 9-10/10.
