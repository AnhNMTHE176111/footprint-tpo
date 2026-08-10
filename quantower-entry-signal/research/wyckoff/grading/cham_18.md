# Chấm bài #18 — Chưa rõ (SC) (ACC?) · 2026-05-12 16:59 → 2026-05-14 19:56 (1648 nến M1)

**Điểm: 1/10** — Không nên vẽ range ở đây. Một cây 2 hợp đồng mở range, rồi 2 ngày rưỡi giá bị nhét vào một khung duy nhất với đúng 3 nhãn ở giữa. Cái gọi là "AR" thực chất là một đợt tăng 55 giá kéo 7 tiếng.

## Lỗi (nặng → nhẹ)

### 1. Mở range trên một nến 2 hợp đồng, không có MOVE nào — luật vi phạm: L1
- **Thuật toán gắn:** climax tại 16:59, VSA **0.39x**, biên độ nến **0.4 giá**, volume **2**. Phiếu không có dòng "MOVE trước climax"; ghi "SINH TU CU PHA, khong co cao trao thuc su".
- **Đúng phải là:** L1 đòi một MOVE xu hướng bị climax chặn. Ở đây không có move được đo, và "climax" là nến gần như đứng yên.
- **Bối cảnh làm nặng thêm:** range này sinh từ chính cú phá mà bài #17 đã đánh giá sai (cú SOW giả). Một lỗi ở #17 đẻ ra một range rác ở #18.

### 2. "AR" thực chất là một xu hướng tăng 7 tiếng, không phải cú bật ngược — luật vi phạm: L2
- **Thuật toán gắn:** AR 2026-05-13 **00:23** tại 4769.4 — cách climax (12/05 16:59) **7 tiếng 24 phút**, đi được **55.1 giá**.
- **Đúng phải là:** AR là cú **bật ngược tự động ngay sau climax** khi áp lực bán vừa cạn. Một đợt đi lên 55 giá suốt 7 tiếng là một MOVE xu hướng — nó phải mở range MỚI ở đỉnh của nó, chứ không phải làm biên trên cho một "range" bắt đầu từ 7 tiếng trước.
- **Dấu hiệu quyết định trên chart:** Phase A dài **253 nến**, dài hơn cả toàn bộ Phase A+B+C+D của 5 bài còn lại cộng lại.
- **Nghi phạm:** AR chỉ có trần thời gian 300 nến, không có trần về **độ dài tương đối so với move gốc**. Ở đây không có move gốc để so nên trần biến mất hoàn toàn.

### 3. ST[A] lửng giữa range, cách climax 33% chiều cao — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13/05 03:02 tại **4732.6**, VSA 1.11x.
- **Đúng phải là:** test lại vùng climax (4714.3). Điểm này còn cách climax **18.3 giá**.
- **Dấu hiệu quyết định:** retrace từ AR đo được **67%** — **lọt thoải mái** ngưỡng `STA_MIN_AR_FRAC=0.55` mới, nhưng vẫn nằm ở **33% chiều cao range** tính từ biên dưới. Trên ảnh ST[A] treo giữa vùng trắng, không chạm biên nào. Đây là bằng chứng trực tiếp: **nâng 0.4 → 0.55 KHÔNG giải quyết được lỗi ST[A]** — vì đại lượng bị đo (retrace từ AR) và đại lượng cần chặn (khoảng cách tới climax) chỉ trùng nhau khi AR đúng là AR. Ở range có AR sai như bài này, hai đại lượng tách hẳn nhau.

### 4. Một khung bao trọn 2,5 ngày với 3 nhãn ở giữa — khung quá thô
- **Thuật toán gắn:** Phase B **1312 nến** (~22 tiếng) với đúng **2 nhãn mSOW**.
- **Đúng phải là:** nhìn ảnh, vùng 4680-4770 này chứa ít nhất 3-4 chu kỳ đấu giá riêng biệt (mỗi chu kỳ có đỉnh/đáy/nhịp hồi riêng). Ép tất cả vào một range M1 duy nhất là đúng lỗi kinh điển "khung quá thô, cấu trúc không ra hình" — ở đây phải tách range hoặc lên M15.
- **Vi phạm L9 theo chiều ngược:** Phase B là nơi đọc nỗ lực↔kết quả, không phải chỗ để trống 1312 nến.

### 5. Cả 2 nhãn mSOW trong Phase B đều gán cho nến CHƯA phá biên — luật vi phạm: định nghĩa mSOW (mục 5.1)
- **Thuật toán gắn:** mSOW 14/05 06:22 tại **4730.5** (VSA 8.91x, thân **0.10**) và 14:51 tại **4728.6** (VSA 10.59x).
- **Đúng phải là:** biên chính dưới là **4714.3** — cả hai nến đều nằm **trên** biên 14-16 giá, chưa phá gì cả. Thêm nữa nến 06:22 có thân chỉ 0.10 (râu nến), không đủ 45% để công nhận bất cứ nhãn phá vỡ nào.
- Lỗi này lặp ở #14, #16, #18 → **lỗi hệ thống**, không phải ca lẻ.

### 6. LPSY[C] đặt sát biên dưới trong một range phá XUỐNG — luật vi phạm: L8
- **Thuật toán gắn:** LPSY[C] 14/05 17:50 tại **4721.9** = **14% chiều cao** (4714.3-4769.4), tức sát ngay biên đang bị phá.
- **Đúng phải là:** LPSY[C] là **điểm cung cuối** — nhịp hồi lên test lại kháng cự trước khi rơi, phải ở nửa TRÊN. Đặt ở 14% chiều cao thì đó không phải "điểm cung cuối", đó chỉ là một điểm trên đường rơi.
- **Nghi phạm:** đây là **tác dụng phụ trực tiếp của bản vá 13.1c** — bỏ hẳn `_right_half`. Ràng buộc cần thiết không phải "nửa cố định" mà là **"nửa đối diện hướng phá"**; gỡ sạch thì pivot rơi vào đúng phía sai.

### 7. Phase C (58 nến) dài hơn Phase D (26 nến) — L8
- Lặp đúng lỗi ở #13 và #14. 3/6 bài trong lô có C > D.

### 8. mSOW thứ ba nằm trong dải Phase C nhưng gắn phase B — lỗi timeline
- mSOW 14/05 **18:04** ghi `Phase B`, trong khi Phase C chạy 17:50 → 19:27. Sự kiện và dải phase mâu thuẫn nhau trên cùng một chart.

### 9. Không đặt tên dù đã có SOW + Phase D — luật vi phạm: L4
- Tiêu đề "Chưa rõ (SC) **(ACC?)**". Origin SC + phá xuống (SOW 4703.9, giá sau đó rơi tiếp xuống 4685) → phải là **Tái phân phối**. Gợi ý "(ACC?)" ngược hẳn hướng thật.

### 10. Nhãn SC? lệch khỏi biên nó tạo ra — lỗi cụm climax (chưa sửa)
- Nhãn ở 17:06 giá **4720.3**, sau nến mở range 7 nến, cao hơn biên chính dưới (4714.3) 6.0 giá.

## Đạt
- **SOW cuối (L3, L10): ĐẠT.** SOW 19:29 tại 4703.9, VSA 4.00x, đóng cửa vượt **cả biên chính (10.4 giá) lẫn biên phụ 4706.8 (29 tick)**; trên ảnh giá đi tiếp xuống 4685 sau đó. Đây là cú phá duy nhất trong bài được gắn nhãn đúng chỗ.
- **Biên chính (L3): ĐẠT hình thức** — cố định, không bị kéo theo giá suốt 1648 nến.
- **Guard chiều cao không bắn sai:** 55.1 giá = 1.17% < 3.5%, tỉ lệ biên phụ/chính 1.14× — các guard hoạt động đúng như thiết kế (vấn đề là chúng không đủ để bắt ca này).
