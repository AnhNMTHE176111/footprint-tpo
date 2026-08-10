# Chấm bài #32 — Chưa rõ (BCLX) / DIST? · 2026-06-12 15:27 → 20:59 (332 nến M1)

**Điểm: 5/10** — Range có thật và việc **không** kết luận hướng là trung thực; nhưng 304 nến Phase B chỉ đẻ ra đúng một nhãn, và nhãn đó gán sai cấp.

## Lỗi (nặng → nhẹ)

### 1. mSOW gán cho một cú test nhẹ — vi phạm bảng phân loại mục 5.1
- **Thuật toán gắn:** mSOW 19:35 tại 4223.2, **VSA 1.11x**, thân 0.46.
- **Đúng phải là:** **ST[B]**. Ngưỡng "thăm dò mạnh" của chính thuật toán là sâu ≥ max(15 tick, 15% chiều cao = **4.41 giá**) **hoặc** VSA ≥ 2.2x. Cú này sâu **4.2 giá** dưới biên chính 4227.4 và VSA 1.11x — **trượt cả hai điều kiện**.
- **Dấu hiệu quyết định trên chart:** cột volume tại 19:35 không phải cột vàng (dưới ngưỡng 2.2x); nến chỉ chấm nhẹ xuống dưới đường nét liền rồi bật lại ngay trong 2-3 nến.
- **Nghi phạm trong thuật toán:** nhánh chọn nhãn cho kết cục A hình như so độ sâu với **biên phụ đã nới sẵn** thay vì với ngưỡng max(15 tick, 15% chiều cao); hoặc vá v7 #5 (quét lại cây VSA cao nhất trong đoạn thăm dò) đã chạy nhưng cây cao nhất của đoạn cũng chỉ 1.11x — nếu vậy thì cả đoạn không đủ tư cách mSOW, phải hạ xuống ST[B].

### 2. Nhãn BCLX rơi ngoài khung range, nằm giữa vùng giá — vá v7 #4 chưa ăn
- **Thuật toán gắn:** BCLX tại **15:24**, giá **4251.6**; range bắt đầu tại nến **15:27**, biên chính trên là **4256.8**.
- **Đúng phải là:** nhãn climax phải nằm trong khung và tại đúng đỉnh 4256.8 — mức mà nó dùng làm biên. Hiện chấm BCLX thấp hơn biên nó tạo ra 5.2 giá và lùi 3 nến ra ngoài khung.
- **Nghi phạm:** kẹp nhãn theo nến mở range chỉ chặn hướng trượt **về sau**; khi cây VSA cao nhất của cụm nằm **trước** nến mở range thì nhãn vẫn thoát ra ngoài. Lặp lại y hệt ở bài #31 và #35 → lỗi hệ thống.
- Ghi chú riêng: nến mở range 15:27 có **VSA 1.06x** — tự nó không đạt ngưỡng climax 2.2x, chỉ được nhận nhờ cơ chế dời mốc trong cụm. Nếu cụm climax là một **vùng** (đúng như Ca #12 nguồn 2.pdf: "SC là một vùng TR nhỏ") thì nên vẽ **vùng** 15:24-15:27, đừng chấm một điểm rồi đặt sai chỗ.

### 3. ST[A] đậu ở 40% chiều cao range — chưa phải test vùng climax (L2)
- **Thuật toán gắn:** ST[A] 15:55 tại 4239.3, cách biên chính trên (climax) **17.5 giá** trên range cao 29.4 giá.
- **Đúng phải là:** ST[A] phải quay lại **tiệm cận vùng BCLX** rồi bị chặn. Điểm 4239.3 nằm lửng giữa range, đúng lỗi "ST[A] rơi giữa range" mà chính bảng v6 đã ghi nhận.
- **Nghi phạm:** ngưỡng hồi tối thiểu đã nâng 0.2 → 0.4 (vá v7 #2), nhưng ca này rơi đúng **0.405** — vừa đủ lọt. Nâng ngưỡng chưa đủ; cần thêm ràng buộc **khoảng cách tới mức climax** (ví dụ ST[A] phải nằm trong 1/3 range về phía climax), không chỉ ràng buộc tỷ lệ hồi từ AR.

### 4. Phase B 304 nến trống trơn — vi phạm tinh thần L9
- Ngoài mSOW sai cấp ở trên, không một nhãn nào khác trong hơn 5 tiếng đi ngang. Chart cho thấy giá chạm sát biên trên 4256.8 quanh 18:20-18:40 → phải có **UT[B]**. Phiếu số liệu cũng không có dòng "nhịp nỗ lực/kết quả" (chỉ tính khi Phase B kết thúc) và SOT hai bên đều `none n=0` trên 304 nến — tức toàn bộ phần đọc cung-cầu của Phase B **bằng không**. Đây đúng là chỗ Phase B bị chê "trống hàng trăm nến".

## Đạt
- **Mục 1 (L1):** MOVE 42.5 giá / 40 nến / hiệu suất 0.39, climax là đỉnh cửa sổ — trên ảnh là một đợt tăng dứt khoát từ ~4205 bị chặn tại 4256.
- **Mục 2 (L2):** đủ 3 lần đổi hướng, Phase A 29 nến, kết thúc tại ST[A] (dù vị trí ST[A] đáng bàn ở lỗi 3).
- **Mục 3 (L3):** biên chính = climax + AR, giữ cố định suốt 332 nến; biên phụ dưới 4223.2 đúng một cái, tỷ lệ 1.14x — sạch.
- **Mục 4 (L4):** chưa phá biên nên **không đặt tên** — đúng nguyên tắc, không gò ép (đối chiếu Ca #20 nguồn 7.pdf).
- **Mục 10:** cắt range tại khe cuối tuần đúng — cú nhảy lên 4290+ ở mép phải ảnh là dữ liệu **sau** khe, không bị tính vào range.
