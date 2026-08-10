# Chấm bài #29 — "Chưa rõ (SC) (ACC?)" [superseded] · 2026-06-04 14:53 → 06-05 02:56 (663 nến M1)

**Điểm: 3/10** — Phase A nuốt 430 nến, dài gấp 3 Phase B. Cấu trúc phase sai từ gốc; phải vẽ lại.

## Lỗi (nặng → nhẹ)

### 1. Phase A = 430 nến, dài gấp 3 Phase B — luật vi phạm: L2 + L9
- **Thuật toán gắn:** A 14:53→23:02 = **430 nến**; B 23:03→01:30 = 148 nến; C 60; D 26.
- **Đúng phải là:** Phase A chỉ là **một CHoCH = 3 lần đổi hướng** (L2). Ở đây: SC 14:53 → AR 16:19 → cú lùi đầu tiên về vùng climax. Cú lùi đó nằm quanh **16:40-17:00**, tức Phase A đúng khoảng **120 nến**, và Phase B phải chạy từ đó tới ~01:30 (≈ 460 nến) — khi đó B mới là phase dài nhất theo L9.
- **Dấu hiệu quyết định trên chart:** từ 16:19 (AR) đến 23:02 (ST[A] mà thuật toán chọn) là **hơn 6 tiếng rưỡi giá đi ngang** trong dải 4495-4513, dao động lên xuống hàng chục nhịp. Đó là hình ảnh kinh điển của Phase B ("xây dựng nguyên nhân", THEORY §3.2), không đời nào là Phase A. Nhìn ảnh: vạch tím "Phase B" đặt mãi ở 23:03, tức 3/4 chiều ngang chart đều bị sơn là Phase A.
- **Nghi phạm trong thuật toán:** **đây là tác dụng phụ trực tiếp của việc nâng `STA_MIN_AR_FRAC` từ 0.40 lên 0.55.** Ngưỡng 55% đòi giá hồi xuống ≤ 4513.2 − 0.55×29.4 = **4497.0**. Trong khoảng 16:30-22:00 giá nhiều lần chạm 4495-4498 nhưng có vẻ không đủ sâu/không đúng nến để qua cửa, nên ST[A] bị đẩy tới tận 23:02 (4491.2, hồi 75%). Ngưỡng cứng theo % là sai công cụ cho ca này. Đề xuất: chọn ST[A] là **cú lùi đầu tiên** thoả ngưỡng, và thêm trần cứng "ST[A] không được cách AR quá K nến (K ≈ 3× số nến từ climax đến AR)"; nếu quá K mà chưa có ST[A] đủ sâu thì hạ ngưỡng động thay vì kéo dài Phase A vô hạn.

### 2. Phase C (60 nến) dài hơn Phase D (26 nến), và ôm trọn đoạn giá đã ở ngoài biên — luật vi phạm: L8 + L5
- **Thuật toán gắn:** C = 01:31→02:30 (60 nến), LPSY[C] tại 01:31 (4486.2); SOW mãi 02:31 (4470.7).
- **Đúng phải là:** Phase C là phase **ngắn nhất** (L8). Ở đây từ khoảng 01:35 giá đã đóng cửa dưới biên chính dưới 4483.8 **và** dưới cả biên phụ 4477.5, rồi ở ngoài liên tục ~55 nến. Theo L5, đó là phá THẬT → SOW phải chốt quanh 01:35-01:40, Phase C chỉ còn ~5 nến, Phase D bắt đầu ngay sau đó.
- **Dấu hiệu quyết định trên chart:** trong toàn bộ khoảng x của "Phase C (60n)", các nến nằm dưới cả đường liền cam 4483.8 lẫn đường đứt 4477.5 — không có nến nào quay lại trong range. Vẽ một Phase C dài 60 nến ở vị trí đó là mô tả sai hoàn toàn cái đang xảy ra.
- **Nghi phạm:** cùng nghi phạm với bài #28 — thiếu luật timed-out theo **số nến** đóng cửa ngoài biên. SOW hiện chỉ chốt được ở cây volume nổ (02:31, VSA 5.11x), tức thuật toán đang đợi climax thay vì đợi bằng chứng cấu trúc.

### 3. Không đặt tên range dù đủ bằng chứng — luật vi phạm: L4
- **Thuật toán gắn:** "Chưa rõ (SC) (ACC?)", `superseded`.
- **Đúng phải là:** **Tái phân phối (RE-DIST)** — origin là move giảm 50.6 giá bị SC chặn, hướng phá thật là **xuống** (SOW 4470.7, LPSY[D] 4476.1, giá tiếp tục về 4456). Bảng L4 phân xử thẳng, không có gì mơ hồ.
- **Nghi phạm:** giống bài #27 — cờ `superseded` chặn bước đặt tên. Hai bước phải tách rời.

### 4. Nhãn SC nằm trước nến mở range (lỗi đã biết, chưa sửa)
- SC ghi 14:51 (4487.0, VSA 3.32x); nến mở range là 14:53 (low 4483.8, VSA 2.31x). Ghi nhận, không tính điểm.

## Đạt
- **Mục 1 (L1):** MOVE giảm **50.6 giá / 68 nến / hiệu suất 0.46**, bị chặn tại cực trị. Đây là range có "nguyên nhân" lớn nhất trong lô — hoàn toàn xứng đáng được vẽ. Vấn đề nằm ở cách chia phase, không ở việc mở range.
- **Mục 3 (L3):** biên chính 4483.8–4513.2 cố định, không bị kéo theo giá; biên phụ chỉ có **một** phía dưới (4477.5), phía trên không có — đúng L3 "có thể có 2, có 1, hoặc không có".
- **Mục 7 (L10) — phần D:** SOW 02:31 VSA 5.11x đóng cửa dưới cả biên chính lẫn biên phụ; LPSY[D] 02:50 tại 4476.1 **giữ được dưới** biên phụ 4477.5 → retest hợp lệ. Cặp D này đúng (chỉ sai thời điểm bắt đầu).
- **Mục 8:** đọc SOT phía trên = `SOT` (n=3, thrust cuối/đầu 0.20, volume 1.08 → hấp thụ) kèm bias test biên −1 (chạm nổi biên dưới, không nổi biên trên) — hai chỉ số này chỉ đúng hướng gãy xuống. Thuật toán **đo đúng** nhưng lại không dùng để kết luận tên range (xem lỗi #3).
- **Mục 9:** không có nhãn spam; mSOW đặt trong Phase B đúng vai.

## Cần hỏi người học
- Khi Phase A kéo dài bất thường vì không tìm được ST[A] đủ sâu, ưu tiên nào đúng hơn: (a) hạ ngưỡng hồi để bắt ST[A] sớm, hay (b) huỷ range vì AR không được test lại nghiêm túc? Hai cách cho ra hai bức tranh rất khác nhau và L2 không nói rõ ca này.
