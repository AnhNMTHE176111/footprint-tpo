# Chấm bài #17 — Tái phân phối (RE-DIST) · 2026-05-27 05:33 → 07:33 (120 nến M1)

**Điểm: 2/10** — **Không nên vẽ range ở đây.** Đây không phải một vùng đấu giá mà là một chỗ nghỉ 45 phút giữa dòng của một đợt giảm; cái mà máy gọi là "ST[A]" chính là cú phá xuống thật.

## Lỗi (nặng → nhẹ)

### 1. Climax không chặn được move — giá đi thẳng qua range — luật vi phạm: L1
- **Thuật toán gắn:** SC 4525.6 (05:33, VSA 4.84x) mở range, biên chính 4525.6–4533.9.
- **Đúng phải là:** không mở range. Sau climax giá chỉ đi ngang **48 nến** rồi rơi tiếp: nến **06:18** đóng cửa 4520.2 (**VSA 4.23x**) — đã ở dưới biên chính dưới, rồi 06:21 xuống 4515.5 (VSA 3.13x), 06:31 xuống **4511.0** (VSA 2.76x), và sau khi range "hoàn tất" còn xuống 4507. Move giảm chưa hề bị chặn; cây climax chỉ là một nến trong đợt giảm đó.
- **Dấu hiệu quyết định trên chart:** biên chính cao **8.3 giá (0.18%)** — nhỏ hơn cả biên độ hai nến climax cộng lại (5.5 + 5.8 giá), trong khi riêng "ST[A]" chọc xuống **10.1 giá dưới biên dưới** = 122% chiều cao range. Một cấu trúc mà một sự kiện đơn lẻ đi xa hơn cả chiều cao range thì range đó không tồn tại.
- **Nghi phạm trong thuật toán:** không có **sàn tuyệt đối cho chiều cao biên chính**. Guard duy nhất là "cao > 3.5% giá thì huỷ" (chặn trên), không có chặn dưới. Trên M1 vàng, biên chính < ~0.3% giá (hoặc < 3× biên độ trung bình 20 nến) nên bị loại là nhiễu — đúng cảnh báo "range quá vụn" của CHART_CASES.

### 2. ST[A] thực chất là SOW — gán nhãn test cho một cú phá vỡ — luật vi phạm: L2, L3
- **Thuật toán gắn:** ST[A] tại 4515.5 (06:21, VSA 3.13x, thân/biên độ 0.82), và dùng chính nó để nới **biên phụ dưới 4515.5**.
- **Đúng phải là:** ST[A] theo L2 là cú quay về phía climax **rồi bị chặn nhẹ lần nữa**. Nến 06:21 không bị chặn: nó là nến đỏ thân 0.82, volume gấp 3 lần trung bình, nối tiếp nến 06:18 volume gấp 4.2 lần đã đóng cửa dưới biên — đây là **SOW/MSOW**, tức range kết thúc ngay ở Phase A. THEORY §5 cho phép ST[A] nằm **ngoài** range, nhưng "ngoài range" nghĩa là chọc qua rồi bị chặn, không phải đi tiếp 14.6 giá nữa.
- **Dấu hiệu quyết định trên chart:** sau "ST[A]" giá **không** quay lại trong biên chính lần nào nữa cho đến hết range; đáy đi tiếp 4511.0 (06:31) rồi 4507 sau đó.
- **Nghi phạm trong thuật toán:** bước tìm ST[A] (mục 4.2) chỉ kiểm "hồi ≥40% chiều cao climax↔AR" + "5 nến không tạo cực trị mới", **không có trần cho việc ST[A] đi quá xa ngoài mức climax**. Cần: nếu cực trị đó vượt mức climax quá (vd) 50% chiều cao climax↔AR thì đó là phá vỡ Phase A → bỏ ứng viên hoặc chuyển thẳng sang SOW.

### 3. LPSY[C] thực chất là LPSY[D] — sai vai trước/sau cú phá — luật vi phạm: lỗi kinh điển Ca #3 nguồn 4.pdf
- **Thuật toán gắn:** LPSY[C] tại 4522.0 (06:48).
- **Đúng phải là:** LPSY[C] là test **trước** SOW; nhịp 06:48 diễn ra **sau** cú phá 06:18–06:31 nên là **LPSY[D]** (hồi retest sau phá, và nó thất bại — chỉ hồi tới 4522.0 rồi rơi tiếp).
- **Dấu hiệu quyết định trên chart:** 4522.0 nằm **dưới** biên chính dưới 4525.6 — một "test" không chạm được vào range thì không thể là test trước phá.
- **Nghi phạm trong thuật toán:** vì cú phá thật bị dán nhãn ST[A] (lỗi #2), mọi vai sau đó lùi một bậc: LPSY[D] thành LPSY[C], SOW thật thành ST[A].

### 4. Nhãn SOW muộn 47 nến, đặt gần như đúng chỗ đã phá — luật vi phạm: mục 8 Effort vs Result
- **Thuật toán gắn:** SOW 07:08 @4515.1 (VSA 2.06x, thân 0.89 — bản thân nến này ổn).
- **Đúng phải là:** SOW đã xảy ra ở 06:18–06:21. Nhãn 07:08 chỉ thấp hơn "ST[A]" **0.4 giá** và còn cao hơn đáy 06:31 (4511.0) **4.1 giá** — nó không phá thêm gì cả.
- **Nghi phạm trong thuật toán:** chuỗi xác nhận 3 nến tính từ **biên phụ** (đã bị chính ST[A] đẩy xuống 4515.5) nên cú phá thật tự vô hiệu hoá điều kiện phá: biên phụ chạy theo cú phá, khiến máy phải đợi giá phá **thấp hơn cả cú phá** mới chịu gọi SOW.

### 5. Phase B không phải phase dài nhất — luật vi phạm: L9
- A(49) > B(26) = D(26) > C(20). Phase A dài gấp đôi Phase B. Đây là dấu hiệu định lượng cho thấy cấu trúc chưa từng thành vùng đi ngang — hệ quả trực tiếp của lỗi #1/#2.

## Đạt
- Phép đo MOVE trước climax hợp lệ: 23.6 giá / 44 nến / hiệu suất 0.57 (đúng là một đợt giảm, không phải đi ngang).
- Biên chính = climax + AR khớp đúng (4525.6 và 4533.9 = mức AR, không bị kéo theo giá) — đúng L3.
- Không dựng thêm Phase E khống khi cú phá không đi đủ xa — range đóng ở Phase D, đúng mục 7.
- Không có nhãn ST[B] (đúng L6), không spam nhãn.

## Cần hỏi người học
- Anh muốn đặt **sàn chiều cao biên chính** cho M1 vàng là bao nhiêu (theo % giá, hay theo số lần biên độ trung bình 20 nến) để loại thẳng những "range" 8 giá như bài này?
