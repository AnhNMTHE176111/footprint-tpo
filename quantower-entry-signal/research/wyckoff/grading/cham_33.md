# Chấm bài #33 — Chưa rõ (SC) / ACC? · 2026-06-15 12:18 → 20:46 (508 nến M1, superseded)

**Điểm: 3/10** — Không phải một vùng đấu giá: đây là một nhịp tăng 46 giá rồi một nhịp giảm 46 giá, bị đóng khung lại thành "range". Phase A dài 165 nến với "AR" là cả một chân xu hướng.

## Lỗi (nặng → nhẹ)

### 1. AR không phải cú bật ngược, mà là một chân xu hướng dài 108 phút — vi phạm L2 + THEORY §3.3
- **Thuật toán gắn:** AR 14:06 tại 4391.5, tức **46.2 giá** và **108 nến** sau climax.
- **Đúng phải là:** AR = "lực đẩy tự động", một sóng bật ngược nhanh do áp lực bán cạn, rồi tắt. Trên ảnh, đoạn 12:20 → 13:50 là một chuỗi đỉnh-đáy cao dần đều đặn — đó là một **move tăng có cấu trúc**, không phải phản ứng tự động. Đúng nghĩa thì climax 4345 chỉ chặn được một nhịp giảm nhỏ 20 giá rồi thị trường **đi tiếp lên**; không có vùng cân bằng nào được sinh ra ở đây.
- **Dấu hiệu quyết định trên chart:** Phase A **165 nến / 508 nến = 33% cả range**, gần bằng nửa Phase B. Range Wyckoff mà Phase A chiếm 1/3 là dấu hiệu AR đo sai.
- **Nghi phạm:** AR = "swing pivot ngược đầu tiên được xác nhận (5 nến không cực trị mới)" + sàn tương đối 0.5× nhịp hồi lớn nhất trong move. Trong một đợt tăng bậc thang, pivot "đầu tiên được xác nhận" bị đẩy tới tận đỉnh cuối cùng của cả chân. Cần thêm trần: AR quá N nến hoặc quá k× độ dài MOVE trước climax (ở đây AR = **2.3× độ dài MOVE 20.2 giá**) thì bỏ ứng viên.

### 2. Điều kiện mở range yếu — MOVE 20.2 giá không tương xứng range 46.2 giá (L1)
- **Thuật toán gắn:** MOVE giảm 20.2 giá / 36 nến trước climax, range sinh ra sau đó cao **46.2 giá**.
- **Đúng phải là:** climax phải **chặn** một move; ở đây cái bị chặn nhỏ hơn một nửa cái range mà nó sinh ra. Nhìn ảnh: trước climax giá đang lắc 4355-4368 rồi trượt xuống 4345 — chưa đủ tư cách "một MOVE xu hướng rõ ràng bị chặn lại".
- **Nghi phạm:** ngưỡng MOVE tuyệt đối (≥8× ATR20) không có ràng buộc **tương quan với chiều cao range** hình thành sau đó.

### 3. ST[A] ở 60% chiều cao range — không phải test vùng climax (L2)
- **Thuật toán gắn:** ST[A] 15:02 tại 4373.0, cách climax 4345.3 tới **27.7 giá** trên range 46.2 giá.
- **Đúng phải là:** ST[A] phải quay về tiệm cận vùng SC. 4373 là một nhịp chỉnh giữa range, không test gì cả. Vá v7 #2 (0.2→0.4) không cứu: ca này đo đúng **0.40**, vừa lọt cửa. Lỗi giống hệt bài #32 → ngưỡng "tỷ lệ hồi từ AR" là **sai thước đo**; phải đo **khoảng cách còn lại tới mức climax**.

### 4. Thiếu Phase C — vi phạm L8 (cùng nguyên nhân với bài #31)
- **Thuật toán gắn:** A → B → D, không có C.
- **Đúng phải là:** trước cú SOW 20:21 có nhịp hồi 18:20-19:00 (bật từ ~4341 lên ~4348 rồi tắt dần) — đó là LPSY[C].
- **Nghi phạm:** ràng buộc "LPSY[C] phải nằm **nửa trên** range" (v6 mục 1.5). Trong 60 nến trước cú phá, giá đã dán vào biên dưới 4345 → không có pivot nào ở nửa trên → bỏ Phase C. Ràng buộc này **ngược lý thuyết**: LPSY theo THEORY §4.1 là "đợt phục hồi yếu **sau khi test kháng cự cục bộ ở biên dưới**". Phải cho phép LPSY[C] nằm ở nửa dưới / ngay tại biên bị phá.

### 5. Phân cấp ST[B] vs mSOW mâu thuẫn nhau về độ sâu
- **Thuật toán gắn:** ST[B] 17:52 tại **4341.7** (sâu hơn biên chính 3.6 giá) — nhưng mSOW 19:22 tại **4342.4** (nông hơn, chỉ 2.9 giá) lại được gán cấp **cao hơn**.
- **Đúng phải là:** một cú thăm dò **không đi xa hơn** cú trước thì không được nâng cấp (đúng tinh thần Ca #19 nguồn 2.pdf: cú rũ phải là cực trị của cả TR). Ở đây nhãn cấp cao được quyết bởi **mỗi VSA** (7.87x), bỏ qua độ sâu tương đối.
- **Nghi phạm:** điều kiện "mạnh" là **hoặc** sâu **hoặc** VSA ≥ 2.2x — nhánh VSA đơn độc cho phép nâng cấp một cú nông hơn cú cũ. Nên thêm điều kiện chặn: cú mới phải ít nhất bằng cực trị cú cũ cùng bên.

## Đạt
- **Mục 3 (L3):** biên chính cố định sau Phase A, biên phụ đúng 1 cái mỗi bên (4339.1 / 4391.5), tỷ lệ 1.13x — sạch.
- **Mục 4 (L4):** không đặt tên (superseded) — trung thực, không gò.
- **Mục 5 (L9):** Phase B 318 nến, dài nhất.
- **Mục 7:** SOW 20:21 đặt đúng cây VSA 5.81x thân 0.83 (không rơi vào cây yếu như bài #31) và có LPSY[D] — phần này làm đúng.
- **Mục 8:** chỉ số SOT phía dưới đọc "HẤP THỤ (volume ≥ nhịp đầu)" với tỷ lệ volume 1.13 — đúng dấu.

## Cần hỏi người học
- Với ca "climax chặn move nhỏ rồi giá đi tiếp 46 giá theo hướng ngược lại": anh muốn coi đây là **bỏ ứng viên** (climax không chặn được gì) hay vẫn mở range và chấp nhận Phase A dài? Luật L1/L2 hiện chưa phân xử được ca này.
