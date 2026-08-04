# Chấm bài #08 — Chưa rõ (BCLX) (DIST?) · 2026-04-17 13:13 → 20:59 (266 nến M1)

**Điểm: 4/10** — Mở range đúng chỗ, nhưng Phase A hỏng (AR bắt sai cây) và range chết ở B với 236/266 nến trống trơn.

## Lỗi (nặng → nhẹ)

### 1. Phase B dài 236/266 nến mà KHÔNG có một nhãn nào — luật vi phạm: L9 + L8 (cấu trúc không hoàn thành)
- **Thuật toán gắn:** A (31n) → B (236n). Toàn range chỉ có 3 nhãn: BCLX, AR, ST[A] — tất cả trong Phase A.
- **Đúng phải là:** 89% thời lượng range không sinh ra một sự kiện nào là dấu hiệu thuật toán **mù trong Phase B**. Nhìn ảnh: từ 13:44 tới 19:16 giá dao động 4911–4941, chạm biên chính dưới 4909.2 nhiều lần (đoạn 15:57, 17:27, 19:16) — mỗi lần chạm biên đều đáng là một DA/mSOW. Rồi từ 20:29 giá **sụp thẳng** xuống 4886 và xa hơn, xuyên biên dưới rất dứt khoát — đó là **SOW thật**, range phải sang Phase D và mang tên **Phân phối**, chứ không được đóng ở trạng thái "Chưa rõ".
- **Dấu hiệu quyết định trên chart:** đoạn cuối bên phải ảnh (04-17 19:16 → 20:59) là một chuỗi nến đỏ liên tiếp đi từ 4911 xuống 4886, đóng cửa hẳn dưới đường liền cam "bien CHINH duoi 4909.2". Không có nhãn nào ở đó.
- **Nghi phạm trong thuật toán:** range bị cắt tại 20:59 (khớp giờ đóng phiên) **trước khi** cú phá kịp thoả 3 nến xác nhận. Xem lỗi #4. Nếu range không bị cắt, SOW đã bắn.

### 2. AR bắt vào cây rác VSA 0.35x, thân 0.35 — luật vi phạm: L2 (AR phải là "cú bật ngược thật")
- **Thuật toán gắn:** AR tại 13:30, giá 4909.2, VSA **0.35x**, thân/biên độ **0.35**.
- **Đúng phải là:** AR là đáy của một đợt bán tháo phản ứng sau BCLX — theo THEORY §4.1 nó phải là một **cú bật ngược thật**, tạo biên dưới của TR. Cây 0.35x thân 0.35 là một nến nhiễu. Đối chiếu: chỉ 5 nến sau climax, nến +5 (13:18) có VSA **5.30x**, volume 124 — đó mới là cây có lực. AR nên neo vào vùng đó.
- **Dấu hiệu quyết định trên chart:** trên panel volume, cột cao nhất toàn ảnh nằm ngay sau nhãn BCLX (đúng nến 13:18, 124 hợp đồng); nhãn AR lại đặt ở chỗ cột volume thấp lè tè.
- **Nghi phạm trong thuật toán:** mục 4.1 — AR = "swing pivot ngược đầu tiên được xác nhận (5 nến không cực trị mới) + nhịp bật ≥ 1.5× biên độ TB". Điều kiện thuần **hình học**, không có một chữ nào về khối lượng. Nên thêm: cây AR (hoặc một cây trong nhịp tạo AR) phải có VSA đáng kể, hoặc chọn cây VSA cao nhất trong nhịp làm mốc nhãn — đúng cách đã làm cho SOS/SOW ở lỗi B.

### 3. Climax không nằm ở đỉnh thật của move — luật vi phạm: L1 (climax phải CHẶN move)
- **Thuật toán gắn:** BCLX tại 13:13, giá 4953.8 (đỉnh nến), VSA 3.31x — nến này có **thân chỉ 0.16**, tức râu trên dài, đóng cửa 4943.9.
- **Đúng phải là:** chỗ này **về mức giá thì đúng** — 4953.8 là đỉnh cao nhất, biên chính trên nằm gọn trên tất cả nến. Nhưng cần chú ý: máy neo biên chính vào **đỉnh râu** 4953.8 trong khi giá đóng cửa cao nhất chỉ 4943.9. Ca #5 nguồn 4.pdf: giảng viên bắt lỗi "ranh giới phải neo GIÁ ĐÓNG CỬA, không neo bóng nến". Chênh 9.9 giá là đáng kể trên một range cao 44.6 giá (22%) — nó làm biên trên **không bao giờ bị chạm lại**, giết luôn khả năng có UT/UTAD.
- **Dấu hiệu quyết định trên chart:** đường "bien CHINH tren 4953.8" chạy suốt 266 nến mà **không một nến nào chạm tới** — biên chết.
- **Nghi phạm trong thuật toán:** mục 3(3) đánh dấu climax "tại **đỉnh** nến" (high). Cân nhắc dùng close hoặc max(close, thân trên) cho biên chính, giữ high cho biên phụ.

### 4. Range bị cắt tại 20:59 giữa lúc cú phá đang diễn ra — luật vi phạm: lỗi K của v4 (cắt range theo khe), quyết định #5 người học chốt
- **Thuật toán gắn:** kết thúc "completed" tại 04-17 20:59, trạng thái "Chưa rõ".
- **Đúng phải là:** trục thời gian ảnh nhảy từ 04-17 20:54 sang **04-19 23:09** — khe cuối tuần. Luật cắt range tại khe > 4 giờ là đúng, nhưng ở đây nó cắt đúng lúc giá đang sụp qua biên. Kết quả: một range **hoàn toàn đúng về nhận dạng** (BCLX chặn move tăng 107.7 giá, rồi phân phối, rồi sụp) bị đóng ở trạng thái "chưa rõ" và **mất tên**.
- **Nghi phạm trong thuật toán:** khi cắt range vì khe, nếu tại thời điểm cắt giá **đang đóng cửa ngoài biên chính**, nên chốt SOS/SOW hồi tố và đặt tên range thay vì trả về "chưa rõ".

### 5. Biên chính dưới và biên phụ dưới trùng nhau (4909.2 vs 4908.8) — luật vi phạm: L3 (trình bày)
- Chênh **0.4 giá**. Trên chart hai đường nét liền và nét đứt chồng lên nhau, chữ "bien CHINH duoi 4909.2" và số 4908.8 đè lên nhau không đọc được. Biên phụ chênh dưới 1 giá thì không mang thông tin gì — nên bỏ, đừng vẽ. **Lỗi trình bày.**

## Đạt
- Điều kiện mở range chuẩn nhất lô này: VSA **3.31x**, biên độ 11.8 giá, MOVE **107.7 giá / 140 nến / hiệu suất 0.37**. Trên chart đợt tăng từ ~4830 lên 4953 là move xu hướng rất rõ, cây climax nằm đúng đỉnh chặn nó (L1 đủ cả cần lẫn đủ).
- ST[A] tại 4933.0 (VSA 1.83x, thân 0.68) — nằm ở **53%** chiều cao range, hướng về phía climax, là một cú test có lực. Chấp nhận được, tuy hơi nông so với vùng climax.
- Phase A 31 nến, gọn — không còn bệnh Phase A dài hơn Phase B của v4 (lỗi D).
- Biên chính cố định suốt range, không kéo theo giá (L3).
- Không đặt tên range khi cú phá chưa xác nhận — đúng L4/lỗi F, dù ở ca này sự thận trọng đó lại làm mất một cái tên đáng lẽ có.
