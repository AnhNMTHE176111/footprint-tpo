# Chấm bài #39 — Tích luỹ (ACC) · 2026-06-30 12:58 → 15:14 (136 nến M1)

**Điểm: 4/10** — sửa nhãn: ST[A] chốt sớm một nhịp, kéo theo Phase B teo lại và Phase C phình; LPS[D] sai vai.

## Lỗi (nặng → nhẹ)

### 1. ST[A] chốt sớm một nhịp — cú test thật bị đẩy xuống thành LPS[C] — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:24 @ 4033.0; rồi LPS[C] 13:37 @ 4027.2.
- **Đúng phải là:** ST[A] = 13:37 @ 4027.2. Đó mới là cú quay về **phía climax** và bị chặn: cách climax 4022.1 chỉ 5.1 giá (20% chiều cao range). Còn 4033.0 nằm ở **43% chiều cao**, giữa range — theo Ca #12 nguồn 7.pdf, đó là "một cái ngọ nguậy", không phải ST.
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, đáy 13:37 là đáy **thấp thứ nhì cả range**, gần chạm đường biên chính dưới 4022.1; còn pivot 13:24 chỉ là một cái lún nhẹ giữa hai nhịp tăng.
- **Nghi phạm trong thuật toán:** sửa #2 của v7 (ngưỡng hồi 0.2 → 0.4) không bắt được: nhịp hồi ở đây là 0.57 khoảng AR↔climax nên vẫn qua. Ràng buộc còn thiếu vẫn đúng như v6 đã ghi: **khoảng cách ST[A] tới climax**, chứ không phải độ sâu hồi so với AR.

### 2. Phase B chỉ 12 nến — ngắn nhất trong A/B/C — luật vi phạm: L9 (và L8 kéo theo)
- **Thuật toán gắn:** A=27 · B=12 · C=32 · D=14 · E=52.
- **Đúng phải là:** B dài nhất, C ngắn nhất. Hiện C **gấp gần 3 lần** B.
- **Dấu hiệu quyết định trên chart:** đoạn "Phase C (32n)" trên ảnh trải từ 13:37 tới 14:08 và chứa nguyên một chân tăng 4027 → 4046 — đó là hành trình đi từ biên dưới lên biên trên, tức là **hoạt động của Phase B**, không phải Phase C.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của lỗi #1 cộng với cửa sổ gán ngược Phase C nới lên 0.8× len(B). Với len(B)=12 thì cửa sổ chỉ ~10 nến, nhưng đoạn C thực tế lại lấy mốc từ LPS[C] tận 13:37 — tức mốc bắt đầu Phase C được đặt tại một pivot cũ hơn cả cửa sổ. Cần kiểm lại: Phase C không được bắt đầu trước điểm cách SOS quá 0.8×len(B) nến.

### 3. Nhãn SC dán vào nến TĂNG — luật vi phạm: mục 3.3 THEORY (SC là cao trào bán), mục 9
- **Thuật toán gắn:** nhãn SC tại **13:00** (O 4023.7 → C 4029.6, nến **xanh**, tăng 5.9 giá, VSA 3.33x), trong khi mức climax/biên chính dưới = 4022.1 của nến **12:58**.
- **Đúng phải là:** nhãn SC phải nằm trên một cây **bán** — nến 12:58 (đỏ, C 4022.7, VSA 2.60x, thân 0.70). Dán nhãn cao trào **bán** lên một cây tăng mạnh là mâu thuẫn khái niệm.
- **Dấu hiệu quyết định trên chart:** chấm SC trên ảnh nằm ở 4022.9 nhưng đường biên chính dưới ghi 4022.1 — hai mức lệch nhau, và cây mang nhãn là cây xanh dài nhất cụm.
- **Nghi phạm trong thuật toán:** sửa #4 của v7 mới kẹp **vị trí** nhãn trong cửa sổ cụm, chưa kiểm **màu nến** khớp loại climax. Điều kiện (3) ở mục 3 ("nến đỏ → SC, nến xanh → BCLX") chỉ áp cho nến mở range, không áp cho nến được chọn mang nhãn.

### 4. LPS[D] sai vai — không phải nhịp retest — luật vi phạm: L10, L7
- **Thuật toán gắn:** LPS[D] 14:12 @ 4051.6, chỉ **3 nến** sau SOS (14:09 @ 4058.0).
- **Đúng phải là:** LPS[D] là nhịp hồi **sau** cú phá mà vẫn **giữ được ngoài biên**. Ở 14:12 giá đang bay dở lên 4078 — 4051.6 chỉ là một cái lún trong thân cú phá. Nhịp retest thật là đợt rơi từ 4078 quãng 14:25 trở đi, nhưng lúc đó thuật toán đã sang Phase E.
- **Nghi phạm trong thuật toán:** LPS[D] = "swing pivot ngược hướng đầu tiên xác nhận sau 5 nến, hồi ≥1.5× biên độ TB". Trong một cú phá dốc, ngưỡng 1.5× ATR bị thoả bởi nhiễu nội nhịp. Nên đòi thêm: nhịp hồi phải lùi được về **tiệm cận biên đã phá** (≤ 30% chiều cao range tính từ biên).

### 5. Đặt tên "Tích luỹ" cho một cấu trúc trả lại toàn bộ cú phá — mục 10, tham chiếu §9 THEORY (cấu trúc thất bại)
- **Thuật toán gắn:** ACC, completed.
- **Đúng phải là:** cần dè dặt. Giá phá lên tới 4078 (đi 30 giá ngoài biên) rồi **rơi thẳng về 4040**, tức lùi hẳn vào trong biên chính 4047.5 ngay trong Phase E. Về hình, cú phá này giống một upthrust hơn là kết quả của tích luỹ.
- **Dấu hiệu quyết định trên chart:** cuối ảnh (15:05–15:14) giá đóng cửa nằm **dưới** đường biên chính trên 4047.5.
- **Nghi phạm trong thuật toán:** luật "SOS/SOW đã xác nhận thì range ĐÓNG luôn, không lùi lại" (mục 2). Đúng về mặt engineering, nhưng khiến nhãn cuối không phản ánh kết cục. Cảm nhận cá nhân về mức độ nghiêm trọng; luật hiện hành đang chống lưng cho thuật toán ở điểm này.

## Đạt
- **Điều kiện mở range (L1):** MOVE giảm 25.6 giá / 72 nến, hiệu suất 0.37, climax là cực trị thật của cửa sổ — có move bị chặn thật.
- **Biên chính đúng, cố định** 4022.1 – 4047.5; không có biên phụ vì không cú thăm dò nào ra ngoài (L3).
- **SOS đặt đúng cây phá thật:** 14:09, VSA 4.17x, thân 0.87 — trùng đúng cột volume vàng cao nhất toàn ảnh (mục 8).
- **Tên range khớp origin + hướng phá:** SC + phá lên = Tích luỹ (L4).
- **Chú thích nỗ lực/kết quả và SOT đọc đúng dấu:** er=0.56 → "HIỆU QUẢ"; SOT-dn volume 1.30 → "HẤP THỤ". Lỗi hard-code v6 đã hết.
- **Phase E có độ dài thật** 52 nến (L10, lỗi J không tái phát ở bài này).
