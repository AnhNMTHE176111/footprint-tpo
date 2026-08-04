# Chấm bài #05 — Phân phối (DIST) · 2026-01-28 23:41 → 2026-01-29 17:05 (183 nến M1)

**Điểm: 6/10** — Cấu trúc tổng thể đọc đúng và đẹp nhất trong lô (tỉ lệ phase A<B, C ngắn nhất, D+E là CBR). Hai lỗi phải sửa: biên chính cao 136 giá (2,39%) là **quá rộng để gọi là vùng cân bằng**, và LPSY[C] lại gán ngược sai chỗ.

## Lỗi (nặng → nhẹ)

### 1. Biên chính cao 136 giá = 2,39% giá — không phải "vùng cân bằng hẹp" — luật vi phạm: THEORY §2.3 (TR = vùng cân bằng) + mục 8 tài liệu thuật toán (guard 3,5%)
- **Thuật toán gắn:** biên chính 5560,0 - 5696,0 = **136,0 giá**, và vẫn cho qua vì guard đặt ở 3,5%.
- **Đúng phải là:** trung vị chiều cao biên chính mà chính tài liệu thuật toán ghi nhận là **21,6 giá**. Range này cao gấp **6,3 lần trung vị**. Nhìn ảnh: AR ở 5560,0 là **đáy của một cú rơi thẳng 136 giá ngay sau BCLX** — cú rơi đó là một move giảm, không phải một "phản ứng tự động" xác lập biên dưới của vùng cân bằng. Vùng giá mà giá thật sự dành thời gian là 5620-5700 (≈80 giá), không phải 5560-5696.
- **Dấu hiệu quyết định trên chart:** nét liền "biên CHÍNH dưới 5560,0" bị giá chạm **đúng một lần duy nhất** (ngay tại AR, đầu Phase A) rồi trong suốt 116 nến Phase B **không nến nào xuống gần nó**. Toàn bộ Phase B dao động ở nửa trên. Theo THEORY §9, cấu trúc hợp lệ cần "lần chạm" ở **hai** vùng cung/cầu đối lập — biên dưới này chỉ có 1 lần chạm.
- **Nghi phạm trong thuật toán:** guard 3,5% quá lỏng (tài liệu tự thừa nhận "guard tự đặt, KHÔNG có trong tài liệu Wyckoff gốc"). Nhưng gốc rễ sâu hơn: **AR được lấy là cực trị của cú rơi đầu tiên** thay vì là pivot mà giá thật sự tôn trọng về sau. Đề nghị: sau khi Phase A chốt, kiểm lại — nếu biên chính có một bên **không được chạm lại lần nào** trong Phase B thì biên đó đang đặt sai, nên xét dời AR vào pivot thứ hai.

### 2. LPSY[C] tại 5663,2 — giữa range, cách biên dưới 103 giá — luật vi phạm: L8, lỗi kinh điển Ca #3 nguồn 4.pdf
- **Thuật toán gắn:** LPSY[C] tại 5663,2 lúc 14:29, Phase C = 10 nến (14:29 → 15:22).
- **Đúng phải là:** LPSY[C] phải là nhịp phục hồi **yếu, biên hẹp** ở gần biên **dưới** trước cú phá. Điểm 5663,2 nằm ở **76% chiều cao range tính từ dưới** — tức gần biên **trên**. Nó không phải "last point of supply" của cú phá xuống; nó chỉ là đỉnh cao nhất trong 60 nến trước SOW.
- **Dấu hiệu quyết định trên chart:** chấm LPSY[C] nằm cao hơn cả ST[A] (5660,0), gần đường nét liền biên trên; trong khi SOW nằm ở 5410,0 — thấp hơn nó **253 giá**. Khoảng cách này lớn hơn cả chiều cao range.
- **Nghi phạm trong thuật toán:** cùng một nghi phạm với bài #03 và #04 — nhánh "Phase C gán ngược, nhìn lại 60 nến, lấy cực trị" (mục 6 case KHÓ). Tài liệu thuật toán tự ghi ở mục 12.8 rằng cách chọn này "chưa chắc trùng với nhịp test mà mắt người sẽ chọn" — vòng chấm này xác nhận **nó sai ở 3/3 ca dùng nó**. Phải thêm điều kiện vị trí (điểm gán ngược phải nằm trong dải sát biên bị phá) và cho phép kết luận "range không có Phase C".

### 3. BCLX VSA 1,13× trong khi nến −3 có VSA 6,53× — luật vi phạm: L1 + mục 3(1) tài liệu thuật toán
- **Thuật toán gắn:** BCLX tại 5696,0, VSA **1,13×** (dưới ngưỡng 2,2× của chính thuật toán).
- **Đúng phải là:** nến −3 (23:23) có volume 16, **VSA 6,53×**; nến −4 có 2,29×; nến −1 có 1,96×. Cụm cao trào thật là 23:13-23:40, còn nến 23:41 chỉ là cây đóng lại ở đỉnh với 3 lot.
- **Dấu hiệu quyết định trên chart:** header ảnh ghi "climax UP **VSA=1.13x**" — dưới ngưỡng. Panel volume có thanh vàng cao ngay trước mốc BCLX, không phải tại mốc.
- **Nghi phạm trong thuật toán:** lặp lỗi cụm climax như bài #02/#03/#04. Ghi nhận: nến BCLX này **có** biên độ thật (20,6 giá) và thân 0,34, nên nó đỡ vô lý hơn ba bài kia; nhưng VSA vẫn dưới ngưỡng.

### 4. UT gắn tại một cú vượt biên 4,0 giá với VSA 0,19× — luật vi phạm: L3 (biên phụ phải là cực trị có ý nghĩa) + mục 8 Effort vs Result
- **Thuật toán gắn:** UT tại 5700,0 (VSA **0,19×**), tạo biên phụ trên 5700,0 — cao hơn biên chính đúng **4,0 giá** (2,9% chiều cao range).
- **Đúng phải là:** một cú thò ra 4 giá trên một range cao 136 giá, bằng một nến VSA 0,19×, không đáng ghi nhãn. Nó cũng không xứng làm biên phụ — nét đứt 5700,0 và nét liền 5696,0 chồng lên nhau trên ảnh tới mức nhãn text đè nhau.
- **Dấu hiệu quyết định trên chart:** hai đường "biên phụ trên 5700,0" và "biên CHÍNH trên 5696,0" không phân biệt được bằng mắt; nhãn text đè lên nhau ở góc phải.
- **Nghi phạm trong thuật toán:** ngưỡng tạo biên phụ không có sàn tối thiểu (cùng lỗi #4 bài #02). Nên yêu cầu vượt ≥ max(10 tick, 5% chiều cao range).

### 5. Phase E dài 2 nến trong khi giá còn chạy rất xa — luật vi phạm: L10
- **Thuật toán gắn:** E = 17:01 → 17:05, **2 nến**, rồi range đóng.
- **Đúng phải là:** Phase E là "giá rời range đi tìm vùng giá mới". Trên ảnh, sau SOW giá xuống tới ~5230 rồi đi ngang quanh 5400-5450 — cả đoạn đó là Phase E thật, dài hàng chục nến, nhưng bị bỏ ngoài range.
- **Dấu hiệu quyết định trên chart:** vạch "Phase E (2n)" nằm ở mép, còn hành động giá thực sự của Phase E (cụm nến quanh 5410-5450 ngày 01-29 18:03 trở đi) nằm ngoài khung range.
- **Nghi phạm trong thuật toán:** đích Phase E = "đi thêm 1,0 × chiều cao range". Chiều cao ở đây là 136 giá, và SOW rơi từ 5560 xuống 5410 = 150 giá — vượt đích ngay lập tức nên E chốt tức thì. Lỗi J của v4 chưa hết hẳn: Phase E vẫn bị nén khi cú phá quá bạo. Nên để Phase E chạy tới khi giá **đi ngang lại** (hình thành range mới) chứ không chốt ngay khi đạt mốc khoảng cách.

## Đạt
- **Tên range đúng theo L4:** move tăng 418,3 giá bị chặn → BCLX; phá thật xuống → Phân phối.
- **Tỉ lệ phase đúng cả hai luật:** A=34 < **B=116 (dài nhất, L9)**, **C=10 (ngắn nhất, L8)**. Đây là bài duy nhất trong lô đạt trọn hai luật tỉ lệ. So với v4 (Phase C dài 121 nến = trần timeout), vá lỗi C **có tác dụng rõ**.
- **ST[A] đúng nghĩa (L2):** 5660,0 nằm trong biên chính, thấp hơn climax 36 giá — quay về phía climax rồi bị chặn, không vượt qua. Phase A kết thúc đúng tại ST[A].
- **SOW neo đúng cây phá thật:** VSA **3,67×**, thân/biên độ 1,00. Vá lỗi B của v4 hoạt động đúng — không còn nhãn rơi vào nến VSA 0,3×.
- **Phase D+E là CBR (L10):** SOW 15:24 → LPSY[D] 16:32 tại 5417,0 (retest giữ được **dưới** biên) → Phase E. Có nhịp hồi thật.
- **UT dùng đúng vai, không nhầm thành UTAD** — đúng bài học Ca #8 nguồn 7.pdf. Cú thăm dò nhẹ trên đỉnh giữa Phase B được gọi UT và **ở lại Phase B**, không bị nâng lên UTAD rồi mở Phase C sớm. Đây đúng là lỗi kinh điển mà v5 đã tránh được.
- LPSY[C] / LPSY[D] tách hai vai, mỗi cái một điểm — đúng L6, L7.
