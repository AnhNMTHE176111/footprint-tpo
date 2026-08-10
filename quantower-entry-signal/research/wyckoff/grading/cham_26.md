# Chấm bài #26 — Tích luỹ (ACC) · 2026-06-05 02:41 → 09:11 (390 nến)

**Điểm: 7/10** — bài tốt nhất lô này: đủ A→E, tỷ lệ phase đúng, Shakeout đặt đúng chỗ và được xác nhận. Chỉ phải sửa một nhãn mSOW đặt sai bên.

## Lỗi (nặng → nhẹ)

### 1. mSOW thứ nhất đặt sai bên và neo vào nến nằm TRONG range — luật vi phạm: mục 5.1 THUẬT TOÁN (mSOS/mSOW = cú phá CÓ THẬT ra ngoài biên)
- **Thuật toán gắn:** mSOW 05:03 tại **4472.8** (VSA 4.08×, thân 0.64).
- **Đúng phải là:** 4472.8 nằm **trong** biên chính (4464.5–4476.1), cao hơn biên dưới 8.3 giá. Một cây chưa hề ra khỏi biên thì không được mang nhãn phá biên. Nhìn ảnh: chấm mSOW này nằm ngay **dưới đỉnh** một nhịp đẩy lên chạm ~4477.5 — tức cú thăm dò đó là thăm dò **biên TRÊN**, nếu phải đặt tên thì là **mSOS** (hoặc UT[B]), tuyệt đối không phải mSOW.
- **Dấu hiệu quyết định trên chart:** khoảng 04:55–05:10 giá dao động 4468–4477, không có nến nào chạm 4464.5; cú phá xuống thật chỉ xảy ra ở 05:55–06:04 (mSOW thứ hai tại 4461.6 — cái này **đúng**).
- **Nghi phạm trong thuật toán:** vá #5 vòng này ("quét lại lấy nến VSA cao nhất trong đoạn thăm dò") lấy `argmax(VSA)` mà **không** ràng buộc nến đó phải nằm ngoài biên và đúng phía bị thăm dò. Thêm điều kiện: nến neo phải có `low < biên_dưới` (mSOW) / `high > biên_trên` (mSOS), và tên nhãn phải lấy theo **bên** bị phá, không theo hướng nến.

### 2. Biên chính hẹp hơn nhiều so với vùng đấu giá thật — luật vi phạm: L3
- **Thuật toán gắn:** biên chính 4464.5–4476.1 = **11.6 giá**; biên phụ 4454.8–4483.2 = 28.4 giá, tỷ lệ **2.45×**.
- **Đúng phải là:** hai biên phụ mỗi bên chỉ được sinh từ **một** cú cố phá — điều đó thoả. Nhưng khi vùng thật rộng gấp 2.5 lần vùng "chính", phải đặt câu hỏi liệu climax/AR có neo đúng chỗ không. Ở đây range sinh từ cú phá (`SC?`, không có cao trào thật) nên climax chỉ là cực trị của một cú phá — biên chính vì thế mỏng.
- **Dấu hiệu quyết định trên chart:** Phase A chỉ 23 nến, AR chỉ VSA 1.17×; hai đường liền cam nằm lọt thỏm giữa vùng dao động.
- **Nghi phạm trong thuật toán:** cơ chế SIDEWAYS (mục 5.4) neo biên bằng cực trị cú phá; nên cho phép **mở rộng biên chính một lần** khi ST[A] hoặc AR của range con vượt ra ngoài, thay vì đẩy hết sang biên phụ.

### 3. (nhẹ) SOS không bứt qua một biên phụ có sẵn — luật vi phạm: L3 (câu "SOS mạnh phải đóng cửa bứt qua biên phụ")
- SOS neo tại 4479.3, trong khi biên phụ trên hiển thị 4483.2 — tức chính cú phá này mới tạo ra 4483.2. Về mặt logic không sai (biên phụ do chính nó nới), nhưng đường nét đứt 4483.2 được vẽ trải suốt bề ngang range làm người đọc tưởng nó tồn tại từ Phase B. Nên vẽ biên phụ **bắt đầu từ nến sinh ra nó**.

## Đạt
- L8/L9: B(194) > E(121) > C(28) ≈ D(25) > A(23). Phase B dài nhất, Phase C ngắn nhất trong nhóm B/C/D — đúng cả hai luật tỷ lệ.
- L5: Shakeout tại 4454.8 (06:18) — giá ra ngoài biên rồi lùng bùng chứ không rút vào trong ≤4 nến, gọi Shakeout (không phải Spring) là **đúng**; trạng thái `confirmed` khớp với việc giá đi thẳng sang biên đối diện sau đó.
- L4: origin SC + phá **lên** = Tích luỹ — đặt tên đúng bảng 4 mẫu hình.
- L10: SOS (06:46) → LPS[D] (06:55) giữ được trên biên → Phase E 121 nến đi tìm vùng giá mới ở 4490. Đúng khuôn CBR.
- Chú thích nỗ lực/kết quả er=0.75 ghi "HIỆU QUẢ" — đúng dấu, vá #1 chạy tốt.
