# Chấm bài #23 — Tái phân phối (RE-DIST) · 2026-05-27 05:33 → 07:50 (137 nến M1)

**Điểm: 7/10** — bài tốt nhất lô. Climax, biên, tên range, SOW và LPSY[D] đều đúng chỗ và đúng volume. Chỉ cần sửa tỉ lệ Phase C/D và bổ sung nhãn Phase B.

## Lỗi (nặng → nhẹ)

### 1. Phase C (10 nến) vẫn dài hơn Phase D (8 nến) — luật vi phạm: L8
- **Thuật toán gắn:** A 12 · B 23 · C 10 · D 8 · E 85.
- **Đúng phải là:** C phải là phase ngắn nhất. Chênh 2 nến nên là lỗi nhẹ, nhưng lặp lại y hệt #19/#21/#22 → là lỗi hệ thống của cửa sổ gán ngược, không phải lỗi lẻ.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược sau vá v7 #3 = min(60, 0.8×23) ≈ 18 nến; nó vẫn lấy pivot xa nhất trong cửa sổ thay vì **nhịp test cuối cùng sát cú phá**.

### 2. Phase A chỉ 12 nến, AR chốt sau climax đúng 4 nến — luật vi phạm: L2 (chất lượng CHoCH)
- **Thuật toán gắn:** SC 05:33 → AR 05:37 → ST[A] 05:44.
- **Đúng phải là:** AR là "cú bật ngược thật". 4 nến sau climax với VSA 1.36× là nhịp hồi kỹ thuật ngay trong cây rơi, biên độ 7.3 giá trên nền một MOVE 19.4 giá. Chấp nhận được nhưng mong manh — đúng ca mà nhãn "AR (yếu)" của chính máy nên bắn ra mà lại không bắn.
- **Nghi phạm trong thuật toán:** điều kiện "AR (yếu)" chỉ kiểm 1–2 nến sát climax; nên nới thành ≤ 5 nến **và** VSA < 1.5×.

### 3. Phase B 23 nến không có nhãn nào — nhãn thiếu
- Trên chart giá chạm biên chính trên 4532.9 hai lần (≈05:50 và ≈06:00) trước LPSY[C]. Phải ghi ít nhất 1 UT[B]. Chỉ số SOT phía trên đã đo được n=2 nhịp rút ngắn với tỷ lệ volume 0.92 (cạn kiệt) — máy *thấy* nhưng không *ghi nhãn*.

### 4. Range mỏng 7.3 giá (0.16%) — cảnh báo khung
- 137 nến cho một dải 7.3 giá. Ở đây tôi vẫn chấp nhận vì volume đủ thật (climax 268 hợp đồng VSA 4.84×, SOW 4.23×, LPSY[D] 3.13×) — khác hẳn #20/#21. Ghi lại như một mốc so sánh: range mỏng không tự động là nhiễu, phải nhìn khối lượng.

## Đạt
- L1: MOVE 19.4 giá / 44 nến, hiệu suất 0.49; climax là đáy thấp nhất cửa sổ, nhãn nằm **đúng nến mở range** (05:33) — vá v7 #4 chạy đúng ở bài này.
- L2: ST[A] 4523.2 quay về xuyên nhẹ climax 4525.6 rồi bị chặn — đúng chất test, Phase A kết thúc đúng tại ST[A].
- L3: biên chính 4525.6–4532.9 = climax + AR, cố định; biên phụ mỗi bên đúng 1 cái, tỷ lệ 1.47×.
- L4: SC + phá **xuống** = Tái phân phối — đúng bảng 4 pattern, không xoá range vì "phá sai hướng".
- L6: không còn nhãn ST[B] rác.
- L8 (case khó): LPSY[C] gán ngược nằm **trong range, đúng nửa trên** (4530.8 > trung điểm 4529.25).
- L10: SOW 06:18 VSA 4.23× đóng cửa dưới cả biên phụ 4523.2 → LPSY[D] 06:21 giữ được bên ngoài → Phase E 85 nến, giá đi tiếp 14 giá ≈ 2× chiều cao range. Đây là một CBR sạch.
- **Vá v7 #1 chạy đúng:** er=0.38 → "nhịp HIỆU QUẢ".
