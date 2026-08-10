# Chấm bài #38 — Chưa rõ (SC) (ACC?) · 2026-06-15 12:18 → 19:47 (449 nến M1)

**Điểm: 2/10** — Phase A dài hơn Phase B, ST[A] rơi lửng giữa range, nhãn SC nằm trên nến XANH, và một cấu trúc đã phá xuống rõ ràng lại bị bỏ không đặt tên còn gợi ý "(ACC?)". Không nên nhận bài này.

## Lỗi (nặng → nhẹ)

### 1. ST[A] rơi lửng giữa range → Phase A nuốt 248/449 nến, dài hơn Phase B — luật vi phạm: L2 + L9
- **Thuật toán gắn:** ST[A] tại 16:25, giá 4360.5; Phase A = 248 nến, Phase B = 163 nến.
- **Đúng phải là:** ST[A] phải là cú **test lại vùng climax** (4345.3). Cú test thật xảy ra lúc 17:52 tại 4341.7 — chỗ thuật toán đang gọi ST[B]. Phase A phải kết thúc ở đó, và Phase B chỉ còn đoạn sau.
- **Dấu hiệu quyết định trên chart:** 4360.5 nằm ở **33% chiều cao range** tính từ climax (15.2 giá / 46.2 giá) — đúng giữa range. Trên ảnh nhãn ST[A] treo lơ lửng giữa hai đường biên, không chạm cái nào. Ngưỡng mới `STA_MIN_AR_FRAC=0.55` bị lách vì retrace-từ-AR đo được 0.67.
- **Nghi phạm trong thuật toán:** đúng chẩn đoán ở 13.1b — 0.55 vẫn chưa chạm gốc rễ. Cần ràng buộc **khoảng cách tới climax ≤ ~25-30% chiều cao**, không chỉ retrace từ AR.

### 2. Range đã phá xuống thật nhưng không được đặt tên, còn ghi "(ACC?)" — luật vi phạm: L4 + L10
- **Thuật toán gắn:** trạng thái `superseded`, tiêu đề "Chưa rõ (SC) (ACC?)".
- **Đúng phải là:** **Tái phân phối (RE-DIST)** — origin SC, phá xuống thật. Đã có LPSY[C] → SOW (VSA 7.87x) → LPSY[D] đủ chuỗi Phase C-D.
- **Dấu hiệu quyết định trên chart:** sau 19:47 giá rơi thẳng xuống 4329, tức **16 giá dưới biên chính dưới 4345.3 và 10 giá dưới biên phụ 4339.1**, không một lần hồi vào range. Đó là Phase E sách vở.
- **Nghi phạm trong thuật toán:** cơ chế SIDEWAYS đánh dấu `superseded` rồi cấm đặt tên — đúng lỗi "SIDEWAYS cắt vụn cấu trúc thật" đã ghi ở 13.1b, chưa sửa.

### 3. Nhãn SC nằm trên nến XANH — luật vi phạm: mục 3(3) "màu nến khớp hướng move"
- **Thuật toán gắn:** SC tại 12:20 (O 4348.0 → C 4348.8, **nến tăng**, VSA 3.20x).
- **Đúng phải là:** cây bán tháo thật là 12:17 — O 4349.6 → C 4345.5, thân 0.95, VSA 3.14x, chính nó tạo đáy 4345.5. Nhãn SC thuộc về cây đó.
- **Dấu hiệu quyết định trên chart:** cả nến mở range (12:18) lẫn nến mang nhãn (12:20) đều là nến xanh; nến đỏ duy nhất trong cụm là 12:17.
- **Nghi phạm trong thuật toán:** kiểm màu nến chỉ chạy ở nến ứng viên ban đầu, không kiểm lại sau khi cụm climax dời mốc.

### 4. ST[B] và mSOW trùng mức giá, cách nhau 9 nến — luật vi phạm: mục 5.0 ("mỗi bên chỉ giữ MỘT nhãn")
- **Thuật toán gắn:** ST[B] 17:52 @ 4341.7 và mSOW 18:01 @ 4341.6.
- **Đúng phải là:** một nhãn duy nhất cho cả cụm test biên dưới đó (chênh **0.1 giá** = 1 tick thì không phải hai sự kiện).
- **Dấu hiệu quyết định trên chart:** hai nhãn chồng nhau trên ảnh, cùng nằm ngay dưới đường biên chính dưới.
- **Nghi phạm trong thuật toán:** quy tắc "cú thăm dò mới nông hơn cú cũ thì không ghi" chỉ áp cho cùng loại nhãn; ST[B] và mSOW đi qua hai nhánh khác nhau nên cả hai cùng ghi.

### 5. Biên phụ dưới 4339.1 không có sự kiện nào neo vào — nhãn thiếu
- Cực trị xa nhất tạo ra biên phụ không được gắn nhãn; hai nhãn có mặt (4341.7 / 4341.6) đều nông hơn 2.5 giá. Vi phạm L3 ở khía cạnh "biên phụ = cực trị xa nhất mà một thế lực đã cố phá range".

### 6. LPSY[D] nằm TRONG range — luật vi phạm: L10
- LPSY[D] @ 4345.6, cao hơn biên chính dưới 4345.3. Nhịp retest phải **giữ được ở ngoài biên**; điểm này ở trong.

## Đạt
- L8: Phase C = 13 nến, ngắn nhất — đúng tỉ lệ, và LPSY[C] @ 4345.1 nằm sát biên chính dưới, đúng vai test trước cú phá.
- SOW đặt hồi tố vào cây VSA **7.87x** — đúng cây phá thật, không rơi vào nến xác nhận yếu.
- Chỉ số nỗ lực↔kết quả đã đọc đúng dấu (không còn hard-code "hấp thụ nghi vấn").

## Kết luận cấu trúc
Nếu là tôi: giữ range nhưng dời ST[A] xuống 17:52, Phase A ~334 nến (range này Phase A dài là do bản chất — AR 46.2 giá lớn gấp **2.3 lần** chính MOVE 20.2 giá mà nó phản ứng lại, đó là dấu hiệu cấu trúc chưa chín), và **bắt buộc đặt tên Tái phân phối**.
