# Chấm bài #32 — Tái phân phối (RE-DIST) · 2026-06-05 14:06 → 14:50 (44 nến M1)

**Điểm: 2/10** — không được vẽ range ở đây. 44 nến, biên rộng 14.2 giá (0.32%), climax có volume **dưới trung bình**: đây là nhiễu trong một đợt giảm, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Nến mở range KHÔNG phải climax — luật vi phạm: L1 (điều kiện ĐỦ), §6.2 THEORY
- **Thuật toán gắn:** "Climax mo range: SC tai gia 4388.1, **VSA=0.98x**", volume 652 trên nền TB ~665.
- **Đúng phải là:** climax = volume nổ + spread mở rộng chặn đứng move. Nến 14:06 có volume **thấp hơn trung bình 20 nến**. Không có bất kỳ tiêu chí climax nào được thoả.
- **Dấu hiệu quyết định trên chart:** cây volume cao nhất trong cụm là 13:59 (VSA 4.07x) và 14:00 (VSA 2.58x) — cách nến mở range 6-7 nến, ở mức giá 4390.0. Panel volume dưới ảnh cho thấy đúng chỗ 14:06 là một thanh lùn giữa hai cụm vàng.
- **Nghi phạm trong thuật toán:** range được neo vào **cực trị giá** của cụm chứ không vào **nến climax**; điều kiện VSA chỉ kiểm ở cấp cụm (max trong cụm ≥ ngưỡng) rồi cho phép neo sang nến khác. Phải bắt buộc nến neo range tự nó đạt VSA ≥ ngưỡng climax.

### 2. Range quá vụn — luật vi phạm: cảnh báo "khung quá thô / range quá vụn" (CHART_CASES Ca #4, #6, #19)
- **Thuật toán gắn:** 44 nến M1, biên chính 14.2 giá, đủ 5 phase A→E.
- **Đúng phải là:** một TR M1 dài 60-100 nến với đủ A→E đã đáng nghi; 44 nến thì chắc chắn là nhiễu. Chia ra: A=10, B=5, C=1, D=14, E=15 — tức "vùng đấu giá" thật chỉ 16 nến.
- **Dấu hiệu quyết định trên chart:** biên phụ = biên chính (tỷ lệ 1.00x) — không bên nào từng cố phá range. Không có lần chạm biên nào đáng kể trong 16 nến.
- **Nghi phạm trong thuật toán:** thiếu ngưỡng tối thiểu về **số nến trong range** và **biên độ range so với ATR**. Đề xuất gate cứng: bỏ range nếu (số nến A→D < ~60) hoặc (biên chính < k×ATR).

### 3. Phase B 5 nến, Phase C 1 nến — luật vi phạm: L9, L8
- **Thuật toán gắn:** B=5n trong khi D=14n và E=15n.
- **Đúng phải là:** B phải dài nhất. Ở đây B ngắn hơn cả D lẫn E → không có nguyên nhân nào được xây.
- **Nghi phạm trong thuật toán:** cùng gốc với bài #31 — LPSY[C] lấy ứng viên đầu tiên sau ST[A] (14:21, ngay trước SOW 14:22), khiến B bị cắt cụt. Ở đây triệu chứng ngược lại bài #31 (C=1n thay vì C phình), chứng tỏ vị trí C hoàn toàn phụ thuộc thời điểm SOW chứ không phải phụ thuộc hành vi giá ở biên.

### 4. Phase E không thoả "giá rời range đi tìm vùng giá mới" — luật vi phạm: L10
- **Thuật toán gắn:** Phase E 14:36→14:50 (15 nến), coi như phá xuống thành công.
- **Đúng phải là:** phá thật thì giá phải giữ được ngoài biên. Trên ảnh, giá chạm đáy ~4372 lúc ~14:37 rồi **hồi thẳng lên trên 4402** (biên chính trên) vào khoảng 14:55-14:57 — tức toàn bộ cú phá bị lấy lại chỉ sau ~20 nến.
- **Dấu hiệu quyết định trên chart:** cụm nến xanh liên tiếp từ 14:41 đến 14:57 đưa giá vượt qua cả biên trên 4402.3.
- **Nghi phạm trong thuật toán:** trạng thái range đóng bằng "completed" sau N nến kể từ SOW mà không kiểm điều kiện **giữ được ngoài biên**. Theo L5, cú này là **Shakeout** (SOW thất bại), không phải SOW thật.

### 5. Nhãn SC nằm ngoài range — lỗi nhãn cụm climax (đã biết, chưa sửa)
- SC gắn tại 13:59, giá 4390.0, trong khi range mở 14:06. Nhãn nằm trước cả nến đầu range, lại ở mức giá khác mức climax 4388.1.

## Đạt
- ST[A] 14:15 hồi 91% khoảng AR↔climax — ngưỡng 0.55 làm việc đúng, ST[A] về sát vùng climax (4389.4 vs 4388.1), không lửng giữa range.
- Tên range đúng L4 nếu chấp nhận cấu trúc: MOVE giảm → phá xuống = Tái phân phối.
- Không có nhãn dư/nhãn sai vai; không có UTAD gọi bừa.

## Cần hỏi người học
- Có muốn đặt **ngưỡng cứng tối thiểu** cho một range (số nến và/hoặc biên độ/ATR) để chặn hẳn nhóm range vụn kiểu này không, hay muốn giữ và lọc ở tầng sau?
