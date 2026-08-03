# Chấm bài #26 — Tái phân phối (RE-DIST) · 2026-06-16 13:22 → 14:29 (67 nến M1)

**Điểm: 4/10** — cấu trúc mở range hợp lệ, nhưng ST[A], Phase C và SOW đều gắn sai chỗ; với biên chính chỉ 7.6 giá (0.17%) thì đây là **nhiễu, không phải một vùng đấu giá thật** — tôi sẽ không vẽ range ở khung M1 này.

## Lỗi (nặng → nhẹ)

### 1. ST[A] gắn sai điểm — bỏ qua cú test thật đã xuyên biên climax — luật vi phạm: L2 + L3
- **Thuật toán gắn:** ST[A] tại 14:03, giá 4355.4 (cao **hơn** mức SC 4354.3 1.1 giá).
- **Đúng phải là:** ST[A] tại **14:00, giá 4352.4**. Đó là điểm cực trị của nhịp quay về phía climax, và nó **xuyên xuống dưới** mức SC → theo L3 chính nó tạo biên phụ 4352.4 mà thuật toán đang vẽ.
- **Dấu hiệu quyết định trên chart:** bốn nến **đóng cửa dưới** mức climax 4354.3 liên tiếp — 13:56 C=4353.8 · 13:57 C=4352.7 · 13:58 C=4353.5 · 13:59 C=4352.7 — rồi nến 14:00 (L=4352.4, volume 212, C=4358.0) bật ngược 5.6 giá ngay trong nến = cú chặn rõ ràng. Nhãn 14:03 nằm **sau** cú chặn đó 3 nến và **nông hơn** 3.0 giá.
- **Nghi phạm trong thuật toán:** `wyckoff_schematic.py` dòng 354 — `r.st_ext` chỉ được khởi tạo **tại nến `i = climax_i + AR_LOOKBACK + 1`** (đúng 14:03), nên mọi diễn biến trong cửa sổ tìm AR 40 nến (gồm cả nhịp xuyên biên 13:56–14:00) **không được xét** làm ứng viên ST[A].

### 2. Phase A dài gấp 3.5 lần Phase B — luật vi phạm: L9 (Phase B dài nhất)
- **Thuật toán gắn:** A=42 nến (63% cả range) · B=12 · C=12 · D=1 · E=1.
- **Đúng phải là:** Phase A phải kết thúc tại cú chặn 14:00 (≈39 nến, hoặc ngắn hơn nữa nếu AR lấy đúng cú bật 13:24) và Phase B phải là phần dài nhất.
- **Dấu hiệu quyết định trên chart:** vạch tím Phase A chiếm gần 2/3 khung range trong khi đoạn đi ngang 4355–4362 thực sự (13:32 → 14:15) lại bị cắt làm hai.
- **Nghi phạm trong thuật toán:** Phase A **không bao giờ ngắn hơn `AR_LOOKBACK + 1 = 41` nến** vì nhánh tìm AR chỉ chốt tại nến cố định đó (dòng 326–355). Đo trên cả 5 bài #26–#30: A = 42/58/45/44/51 nến — không bài nào dưới 42. Đây là lỗi hệ thống, không phải cá biệt.

### 3. LPSY[C] rơi đúng vào cây phá vỡ, không phải cú test — luật vi phạm: L8
- **Thuật toán gắn:** LPSY[C] tại 14:16, giá 4354.2 → Phase C bắt đầu từ đó.
- **Đúng phải là:** nhịp test cuối trước cú phá là cụm nến 14:09–14:15 bám sát biên dưới (đỉnh 4357.3, các đáy 4353.5–4354.2). Nếu phải chọn một điểm thì lấy đỉnh 14:14 (4357.0) — điểm giá bị chặn lần cuối **bên trong** range.
- **Dấu hiệu quyết định trên chart:** nến 14:16 có C=4351.1, tức **đã đóng cửa dưới biên chính 3.2 giá** với thân 0.74 và volume 1.88× — đó là nến bắt đầu phá vỡ, không phải một cú test.
- **Nghi phạm trong thuật toán:** `_retro_phase_c()` dòng 623 — cửa sổ nhìn lại bị chặn bởi **một nửa độ dài Phase B**: (14:28 − 14:04)/2 = 12 nến → chỉ được nhìn từ 14:16 trở đi, và cực trị trong cửa sổ đó chính là nến phá vỡ. Càng siết cho Phase C ngắn thì càng đẩy Phase C vào chính cú phá.

### 4. SOW gắn lên nến TĂNG, sau khi nỗ lực bán đã hết — luật vi phạm: mục 8 THEORY (Effort vs Result)
- **Thuật toán gắn:** SOW tại 14:28, giá 4344.6, VSA 1.46×.
- **Đúng phải là:** SOW tại **14:27** (O 4344.4 → L 4338.2, C 4340.0, volume **587 = 3.35×**) — cây bán quyết định của cả chart; hoặc sớm hơn nữa ở 14:17–14:18 (VSA 2.52× và 2.71×) khi giá bứt hẳn biên phụ.
- **Dấu hiệu quyết định trên chart:** nến 14:28 có O=4339.8 → C=4344.6, tức là **nến xanh hồi lại 4.8 giá**; thanh volume vàng cao nhất khu vực nằm ở 14:27, ngay **trước** nhãn.
- **Nghi phạm trong thuật toán:** điều kiện xác nhận phá vỡ (3 nến đóng cửa ngoài biên phụ + thân ≥ 45%) chỉ chốt ở nến thoả cuối cùng, và `_fire_break()` gắn nhãn tại đúng nến đó — nên nhãn luôn trễ và dễ rơi vào nến hồi.

### 5. [Cấu trúc] Range quá vụn để gọi là vùng đấu giá — luật vi phạm: CHART_CASES mục "khung quá thô / range quá vụn"
- Biên chính **7.6 giá = 0.17% giá**, tổng 67 nến mà nhồi đủ A→E; Phase D và Phase E mỗi phase **1 nến**. Đúng cảnh báo trong CHART_CASES: TR M1 dài 60–100 nến mà đủ 5 phase thì phải nghi là nhiễu. Một "Phase E" 1 nến không thể hiện được ý "giá rời range đi tìm vùng giá mới".

## Đạt
- **Mục 1 (L1):** MOVE trước climax là thật — 22.2 giá / 23 nến, hiệu suất hướng 0.74; nến climax 13:22 là **đáy** của cả cửa sổ và chặn move lại (VSA 2.77×, volume 355 vs TB 20 nến ≈ 128, phiên Mỹ nên volume tuyệt đối có nghĩa).
- **Mục 3 (L3):** biên chính = climax 4354.3 + AR 4361.9, cố định sau Phase A, không bị kéo theo giá; biên phụ đúng một cái mỗi bên và đúng bằng cực trị xa nhất (4352.4).
- **Mục 4 (L4):** tên range đúng — origin SC + phá xuống = **Tái phân phối**, không xoá range vì "phá sai hướng".
- **Mục 7 (một phần):** cú phá đi tiếp 16 giá (≈2× chiều cao biên chính) nên Phase E đạt về mặt cơ học.
- **Trình bày:** biên liền/đứt, dải phase, panel volume có đường TB 20 nến — đọc được effort/result bằng mắt, không phải sửa gì.
