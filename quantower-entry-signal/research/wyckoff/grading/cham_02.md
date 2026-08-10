# Chấm bài #02 — Tái tích lũy (RE-ACC) · 2026-01-08 23:07 → 2026-01-09 15:23 (67 nến M1)

**Điểm: 7/10** — Vẽ đúng về căn bản, chỉ sửa vài chỗ: cây climax neo sai, Phase C hơi phình, Phase E cụt.

## Lỗi (nặng → nhẹ)

### 1. Nến neo climax chỉ có biên độ 0.4 giá — luật vi phạm: L1 (climax phải CHẶN được move) + THEORY §4.1 (BCLX = volume **và** spread mở rộng)
- **Thuật toán gắn:** BCLX tại nến 23:07, VSA 4.88x, **biên độ 0.4 giá**, 20 hợp đồng.
- **Đúng phải là:** một BCLX phải có spread mở rộng. Cây 0.4 giá chỉ qua được ngưỡng "≥1.4× biên độ TB" vì biên độ TB của phiên đêm đó gần bằng 0. Cây đáng chú ý thật nằm ở **-6 (18:29, 37 lot, VSA 12.13x, biên độ 2.7 giá)** — bị bỏ qua vì nằm ngoài cửa sổ cụm.
- **Dấu hiệu quyết định trên chart:** ở mốc BCLX trên panel volume không có cột vàng nào nổi bật; cột vàng lớn nhất của cả đoạn Phase A nằm lệch sang trái.
- **Nghi phạm trong thuật toán:** ngưỡng biên độ climax đo tương đối theo ATR 20 nến, không có sàn tuyệt đối nào — trong phiên chết ATR ~0.25 giá thì mọi cây 0.4 giá đều "mở rộng biên độ".

### 2. Phase C (14 nến) dài hơn Phase D (9 nến) — luật vi phạm: L8
- **Thuật toán gắn:** A 16 · B 27 · C 14 · D 9 · E 2.
- **Đúng phải là:** C là phase ngắn nhất. Ở đây C bằng hơn nửa Phase B và dài hơn cả D.
- **Dấu hiệu quyết định trên chart:** vạch Phase C mở tại 12:54 ngay tại LPS[C], nhưng SOS mãi 14:10 mới bắn — 14 nến "chờ" đó thực chất vẫn là Phase B (giá còn bò ngang trong range).
- **Nghi phạm trong thuật toán:** Phase C gán ngược lấy pivot test **cuối cùng** trong cửa sổ 0.8×len(B); sau khi bỏ ràng buộc nửa-range (13.1c) nó lấy được pivot xa hơn về bên trái. Cần trần cứng `len(C) ≤ min(len(B), len(D))`.

### 3. Phase E dài 2 nến trong khi giá chạy tiếp gần 100 giá — luật vi phạm: L10 (Phase E = giá đi tìm vùng giá mới)
- **Thuật toán gắn:** E = 2 nến (15:09 → 15:23), range đóng tại 4601.9+.
- **Đúng phải là:** trên ảnh giá chạy một mạch từ 4600 lên **~4685** sau khi range đóng — đó mới là "kết quả" của cause vừa xây. Phase E cắt ở mốc 2× chiều cao (38 giá) là quá sớm với một range chỉ cao 19 giá.
- **Nghi phạm trong thuật toán:** mốc dừng Phase E "đi xa 2.0× chiều cao range" tỉ lệ thuận với chiều cao range — range càng hẹp Phase E càng cụt. Nên dùng min(2× chiều cao, N×ATR).

### 4. (trình bày) Chỉ số nỗ lực↔kết quả vẫn lệch đơn vị
- `effort` = VSA (thang 0.2–5) chia cho `result` = biên độ/ATR (thang 5–35) → er = 0.07 và diễn giải luôn ra "nhịp HIỆU QUẢ". Đây đúng là lỗi đã ghi ở 13.1b, **chưa sửa**. Nhịp 12:54 có VSA TB 2.36x ngay tại LPS[C] trước SOS — đó là **hấp thụ** rõ ràng, nhãn đang nói ngược.

## Đạt
- Điều kiện mở range: MOVE 53.7 giá / 21 nến / hiệu suất 0.53, climax chặn đúng đỉnh move — đúng L1.
- Phase A đủ 3 lần đổi hướng, ST[A] tại 4584.0 = hồi **84%** khoảng AR↔climax, sát mức climax 4587 — đúng L2, đây là ST[A] tốt nhất trong cả lô.
- Biên chính = climax 4587.0 + AR 4568.0, không kéo theo giá; không có biên phụ nào và bài không bịa ra biên phụ — đúng L3.
- Tên **Tái tích luỹ**: origin BCLX + phá thật lên trên = đúng bảng L4.
- Phase B là phase dài nhất (27 nến) — đúng L9.
- Case khó (không có Spring/UTAD), Phase C gán ngược từ SOS — đúng L8; LPS[C] chỉ **một điểm** — đúng L7.
- SOS neo đúng cây phá thật (VSA 8.14x, thân 0.89, đóng cửa vượt hẳn 4587) — đúng L10 và đúng mục 8 (effort có, result có).
- LPSY/LPS không spam, không có nhãn ST[B] thừa — đúng L6.
