# Chấm bài #28 — Tái phân phối (RE-DIST) · 2026-06-05 14:06 → 14:50 (44 nến)

**Điểm: 1/10** — **không được vẽ range ở đây.** 44 nến mà nhét đủ A→E, trong đó Phase C dài đúng 1 nến, giữa một đợt giảm liên tục. Đây là nhiễu, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Cây mở range không phải climax — luật vi phạm: mục 3 THUẬT TOÁN (VSA ≥ 2.2×), L1
- **Thuật toán gắn:** climax mở range tại 14:06, mức 4388.1, **VSA = 0.98×**.
- **Đúng phải là:** 0.98× là khối lượng **dưới trung bình**. Không có cao trào nào ở đây. Nhãn "SC" lại được đặt ở nến 13:59 (VSA 4.07×, giá 4390.0) — **7 nến trước** khi range bắt đầu, tức nằm hẳn ngoài khung.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến quanh climax cho thấy đáy các nến −6…−1 là 4388.8 / 4388.3 / 4392.1 / 4399.0 / 4391.0 / 4394.4 — cây "climax" chỉ thấp hơn đáy liền trước **0.2 giá**. Nó không chặn gì cả, nó chỉ là một nến trong chuỗi đi xuống.
- **Nghi phạm trong thuật toán:** cụm climax dời mốc **mức giá** sang cực trị mới (14:06) nhưng giữ nhãn ở nến gốc (13:59) → mức biên và cây climax là **hai nến khác nhau, cách 7 nến**, và cây tạo biên không thoả ngưỡng VSA. Sau khi dời mốc phải **kiểm lại** điều kiện climax trên nến mới, hoặc bỏ ứng viên.

### 2. Range 44 nến với đủ 5 phase, Phase C = 1 nến — luật vi phạm: L8, L9, và bài học "khung quá thô / range quá vụn" (CHART_CASES Ca #4, #6, #19)
- **Thuật toán gắn:** A(10) → B(**5**) → C(**1**) → D(14) → E(15).
- **Đúng phải là:** Phase B phải dài nhất; ở đây nó ngắn hơn A, D và E. "Phase C ngắn nhất" không có nghĩa là 1 nến — 1 nến thì không có test nào để đọc. Toàn bộ cấu trúc là **gò ép** đúng kiểu Ca #20 nguồn 7.pdf ("hình này gượng ép").
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, khung range là một ô nhỏ xíu nằm trên một dốc giảm dài 101.8 giá không đứt đoạn. Không có bất kỳ đoạn đi ngang nào xứng đáng gọi là vùng cân bằng.

### 3. Phase E không hề "đi tìm vùng giá mới" — giá quay ngược vào lại range — luật vi phạm: L10, THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** trạng thái `completed`, Phase E 15 nến, đặt tên RE-DIST.
- **Đúng phải là:** trên ảnh, sau SOW (14:22, 4382.1) giá xuống ~4370 rồi **bật ngược lên trên 4400** khoảng 14:55–15:00 — tức trở lại **trong** biên chính (4388.1–4402.3) và cao hơn. Cú phá đã bị vô hiệu, range phải đóng ở trạng thái "chưa rõ hướng", tuyệt đối không được đặt tên Tái phân phối.
- **Nghi phạm trong thuật toán:** Phase E chốt khi "đi thêm ≥0.5× chiều cao range" — với chiều cao 14.2 giá thì chỉ cần 7 giá là đạt, quá dễ trên M1. Điều kiện chốt E nên yêu cầu giá **không quay lại trong biên chính** trong suốt cửa sổ E, chứ không chỉ chạm mốc khoảng cách một lần.

### 4. LPSY[C] neo trên một nến vô nghĩa — luật vi phạm: L7/L8
- LPSY[C] 14:21 tại 4395.6, VSA 1.12×, và Phase C = đúng nến đó. Một "test cuối cùng ở biên trên" mà nằm ở 53% chiều cao range và chỉ tồn tại 1 nến thì không mang thông tin gì.

### 5. AR và ST[A] đều là nến chết
- AR 14:09 VSA **0.81×** thân 0.08; ST[A] 14:15 VSA **0.42×** thân 0.25. Cả ba mốc Phase A (climax 0.98×, AR 0.81×, ST[A] 0.42×) đều dưới trung bình khối lượng — không có một bằng chứng nỗ lực nào cho thấy có ai đang đấu giá ở đây (THEORY §2.2, Nỗ lực–Kết quả).

## Đạt
- L4: nếu chấp nhận range này thì tên "Tái phân phối" khớp origin SC + phá xuống. (Chỉ đúng về quy tắc đặt tên, không đúng về thực tế vì cú phá sau đó hỏng.)
- Chú thích nỗ lực/kết quả er=0.72 ghi đúng "HIỆU QUẢ" — vá #1 chạy đúng dấu.
