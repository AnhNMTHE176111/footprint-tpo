# Chấm bài #36 — Tái phân phối (RE-DIST) · 2026-07-08 07:05 → 08:37 (92 nến M1)

**Điểm: 4/10** — Khung range, tên range và Phase A vẽ đúng; nhưng toàn bộ đoạn phá vỡ (Phase B cuối → C → D → E) bị dán nhãn sai chỗ: cú SOW thật xảy ra ở 08:16 mà máy chỉ ghi nhận ở 08:36, muộn 20 nến và 33 giá.

## Lỗi (nặng → nhẹ)

### 1. SOW gán muộn 20 nến — cú phá thật bị bỏ qua hoàn toàn — luật vi phạm: L10 / THEORY §4.1 (SOW = "biên độ + khối lượng tăng")
- **Thuật toán gắn:** SOW tại 08:36, giá 4083.7, VSA 1.12x, thân 0.80.
- **Đúng phải là:** SOW tại **08:16** (O 4131.6 → C 4116.8, biên độ 16.4 giá, volume 681 = **VSA 8.50x**, thân 0.90), xác nhận ngay bởi nến 08:17 (C 4097.8, volume 1592 = **VSA 10.06x**, thân 0.88). Hai nến này đóng cửa vượt biên phụ dưới 4125.4 tới 8.6 và 27.6 giá.
- **Dấu hiệu quyết định trên chart:** cột khối lượng vàng cao nhất toàn chart nằm đúng ở 08:16-08:17; nến 08:36 mà máy chọn có volume chỉ 1.12× trung bình, tức nến bình thường giữa đợt giảm đã chạy xong.
- **Nghi phạm trong thuật toán:** nhãn SOW được đặt tại nến **xác nhận** (nến thứ 3 của chuỗi "đóng cửa vượt biên phụ ≥30 tick, thân ≥45%") thay vì tại **nến phá**. Trong cú rơi thẳng đứng, nến +2 (08:18, thân 0.09) và +3 (08:19, thân 0.18) đều không đủ thân 45% nên chuỗi bị ngắt liên tục, đẩy nhãn trôi tới 08:36.

### 2. LPSY[C] sai vai — đây là LPSY[D] — luật vi phạm: L7 / lỗi kinh điển Ca #3 nguồn 4.pdf
- **Thuật toán gắn:** LPSY[C] tại 08:20, giá 4108.4, mở Phase C từ đó.
- **Đúng phải là:** 4108.4 là đỉnh nhịp hồi **sau** cú sụp 08:16-08:18 → đúng vai là **LPSY[D]**. LPSY[C] (test trước SOW) phải là nhịp test cuối cùng còn **trong** range: đỉnh 4132.2 ở 08:15 hoặc đáy 4127.6 ở 08:13.
- **Dấu hiệu quyết định trên chart:** 4108.4 nằm **20 giá dưới biên chính dưới 4128.4**, tức gần 2 lần chiều cao range (10.6 giá). Một điểm cách range 2 lần chiều cao không thể là test trong range.
- **Nghi phạm trong thuật toán:** cơ chế "Phase C gán ngược, nhìn lại 60 nến trước cú phá, lấy cực trị" (mục 6 case khó) **không kiểm điều kiện điểm đó phải nằm trong biên range**. Vì SOW đã bị trôi tới 08:36 (lỗi 1), cửa sổ 60 nến chứa toàn bộ vùng ngoài range, nên nó lấy đỉnh của nhịp hồi.

### 3. Dải phase sai thứ tự: cú sụp nằm trong "Phase B", Phase C đứng SAU cú phá — luật vi phạm: L8 (Phase C là tín hiệu ĐẦU TIÊN trước khi phá biên)
- **Thuật toán gắn:** Phase B = 08:02→08:19; Phase C = 08:20→08:35.
- **Đúng phải là:** Phase C phải nằm **trước** SOW. Ở đây "Phase B" chứa cả cú sụp (đáy Phase B đo được là 4091.3 ở 08:18 — 37 giá dưới biên dưới), rồi Phase C mới bắt đầu ở 08:20 khi giá đã rời range.
- **Dấu hiệu quyết định trên chart:** vạch dọc tím "Phase C (16n)" nằm bên phải cây nến đỏ khổng lồ, không phải bên trái nó.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của lỗi 1 — mọi ranh giới phase đều neo vào thời điểm SOW, nên SOW trôi thì cả dải phase trôi theo.

### 4. Phase B không phải phase dài nhất; Phase D và E mỗi phase 1 nến — luật vi phạm: L9, L10
- **Thuật toán gắn:** A 57 · B 18 · C 16 · D 1 · E 1.
- **Đúng phải là:** B là phase dài nhất (L9). Phase D+E là CBR (phá → hồi retest giữ ngoài biên → đi tiếp), không thể gói trong 2 nến.
- **Dấu hiệu quyết định trên chart:** nhãn "Phase D (1n)" và "Phase E (1n)" chồng lên nhau ở góc phải, dải phase không còn đọc được.
- **Nghi phạm trong thuật toán:** Phase E được chốt theo mốc "hết 25 nến mà đi được ≥50% chiều cao range" — với range chỉ 10.6 giá và cú sụp 45 giá, mốc này đạt ngay nến kế tiếp, nên D và E thu về 1 nến.

## Đạt
- **Điều kiện mở range (L1):** có MOVE giảm thật — 16.3 giá / 41 nến / hiệu suất hướng 0.56; nến climax 07:05 là đáy của cửa sổ, VSA 3.19x, biên độ 3.5 giá. Đúng "climax chặn move".
- **Tên range (L4):** origin SC + phá xuống thật = Tái phân phối. Chính xác.
- **Biên (L3):** biên chính 4128.4 (climax) + 4139.0 (AR), cố định sau Phase A. Biên phụ dưới 4125.4 = cực trị xa nhất (đáy 07:19), mỗi bên tối đa 1, không có biên phụ trên. Đúng luật.
- **Phase A (L2):** đủ 3 lần đổi hướng, ST[A] 08:01 (giá 4127.5, VSA 0.59x — volume co lại đúng chuẩn test) thủng nhẹ mức climax rồi bị chặn, Phase A kết thúc đúng tại ST[A].

## Lưu ý (không tính lỗi)
- AR 07:45 là đỉnh **nến thứ 40** của cửa sổ tìm AR; cú bật ngược thật trong 20 nến đầu chỉ lên 4131.9 (3.5 giá). Với range 10.6 giá thì lấy 4139.0 vẫn cho một vùng cân bằng đọc được, nên chưa thành lỗi — nhưng đây là cùng một cơ chế đã phá hỏng bài #39 và #40.
