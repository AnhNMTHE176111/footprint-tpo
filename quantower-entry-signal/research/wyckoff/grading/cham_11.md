# Chấm bài #11 — Phân phối (DIST) · 2026-04-23 12:06 → 17:40 (240 nến M1)

**Điểm: 5/10** — Khung range và Phase C/D/E đọc được, nhưng mắc đúng lỗi kinh điển số 1 của khoá: gọi UTAD ở giữa Phase B.

## Lỗi (nặng → nhẹ)

### 1. UTAD gọi sai chỗ — luật vi phạm: L8 + Ca #1/#4 CHART_CASES
- **Thuật toán gắn:** `UTAD 12:43 · 4795.6 · Phase C · confirmed`.
- **Đúng phải là:** UTAD là cú test **cuối cùng** phá đỉnh range **ngay trước khi cấu trúc sụp**. Cú 12:43 nằm cách cú sụp thật (SOW 17:05) tận **262 phút / gần 180 nến**, và sau nó giá còn quay lại đi ngang trong range suốt cả Phase B, còn tạo thêm mSOS 4792.4 lúc 15:19. Theo đúng Ca #4 ("nếu sau đỉnh vẫn còn dao động đi ngang/hồi lại trong range → đó chưa phải UTAD"), nhãn này phải đổi thành **UT** (test biên trên trong Phase B, và là điểm sinh biên phụ trên 4795.6).
- **Dấu hiệu quyết định trên chart:** trên ảnh, nhãn UTAD nằm sát mốc bắt đầu Phase B, còn khung Phase C (6 nến) nằm tận 16:51 ở phía bên phải — cách nhau gần trọn chiều ngang range.
- **Nghi phạm trong thuật toán:** điều kiện UTAD chỉ kiểm "vượt biên trên rồi đóng lại trong range", thiếu ràng buộc **hồi tố**: chỉ được gán UTAD nếu SOW/Phase D xảy ra trong vòng N nến sau đó và không còn nhịp hồi nào giữ được trong range.

### 2. Nhãn mang Phase "C" nhưng nằm ngoài khoảng Phase C — lỗi nhất quán nội bộ
- **Thuật toán gắn:** UTAD ghi cột Phase = **C**, trong khi bảng phase ghi Phase C = 16:51 → 17:04. Cùng một phiếu, hai chỗ mâu thuẫn.
- **Đúng phải là:** hoặc kéo Phase C về bao UTAD (sai, xem lỗi #1), hoặc sửa nhãn thành UT thuộc Phase B. Phải có assert: `phase(label) == phase_at(time(label))`.

### 3. Phase C có tới 2 sự kiện nhưng cách nhau 4 giờ — luật vi phạm: L8 (Phase C là phase ngắn nhất)
- Phase C được vẽ 6 nến (đúng: ngắn nhất), nhưng danh sách sự kiện của Phase C gồm UTAD (12:43) **và** LPSY[C] (16:51). Về hình thì Phase C 6 nến, về nhãn thì Phase C trải 4 giờ. Chỉ **LPSY[C] 16:51 · 4789.8** mới là Phase C thật — nó là cú hồi cuối lên sát biên chính trên 4790.9 rồi rơi, đúng vai.

### 4. mSOW 4768.9 gán nhầm vai — luật vi phạm: L5
- **Thuật toán gắn:** `mSOW 16:05 · 4768.9 · Phase B`.
- **Đúng phải là:** mức 4768.9 thấp hơn biên chính dưới 4779.2 tới **10.3 giá — gần bằng trọn chiều cao range (11.7 giá)**. Đó không phải "minor SOW" trong range, đó là một cú **shakeout xuống thất bại** (giá lùng bùng dưới biên rồi quay lại tận 4789.8). Đặt tên theo L5 phải phân biệt bằng thời gian quay lại, không gộp mọi cú thủng biên thành mSOW.
- **Nghi phạm trong thuật toán:** phân loại sự kiện dưới biên chưa dùng tiêu chí "số nến ở ngoài biên trước khi quay lại" (Spring ≤3-4 nến vs shakeout lâu hơn).

### 5. SOW chưa bứt biên phụ — ghi nhận, không trừ nặng
- `SOW 17:05 · 4774.7` đóng dưới biên chính 4779.2 nhưng **chưa qua biên phụ dưới 4768.9**. Theo L3, đây là SOW hợp lệ nhưng **chưa phải SOW mạnh**. Kết cục giá rơi tới ~4718 nên hướng đúng; chỉ nên hạ cấp nhãn, không xoá.

### 6. Biên chính hẹp bất thường — cảnh báo cấu trúc
- Biên chính 11.7 giá (0.24%) trong khi biên phụ 26.7 giá → tỷ lệ **2.28x**: range thật rộng gấp hơn hai lần khung biên chính. Nguyên nhân là AR quá nông (bật đúng 11.7 giá trong 10 nến). Không sai luật (L3 buộc biên chính = climax + AR) nhưng phải hiểu: mọi phán quyết "phá biên" ở bài này đều dựa trên một khung rất mỏng.

## Đạt
- **L1:** MOVE tăng 43.0 giá / 64 nến bị chặn đúng tại BCLX 12:06 (high 4790.9 = cực trị), VSA 3.68x. Nhãn climax đặt đúng nến mở range.
- **L2:** đủ 3 lần đổi hướng — BCLX 4790.9 → AR 4779.2 (12:16) → ST[A] 4794.1 (12:31), hồi **127%** khoảng AR↔climax, vượt hẳn mức climax → ST[A] test đúng vùng climax, không lửng. Phase A kết thúc đúng tại ST[A].
- **L3:** biên chính cố định = climax + AR; mỗi bên đúng 1 biên phụ (4795.6 trên, 4768.9 dưới) và cả hai đúng là cực trị xa nhất.
- **L4:** move tăng → BCLX, phá xuống thật → **DIST**. Tên đúng.
- **L8/L9:** Phase B 178 nến dài nhất, Phase C 6 nến ngắn nhất — trật tự chuẩn.
- **L7:** LPSY[C] đánh 1 điểm.
- **Khối lượng:** SOW 17:05 VSA 3.21x, LPSY[C] VSA 2.92x thân 0.00 (nến chối bỏ ở biên trên) — đọc effort/result ở Phase C/D đúng.
