# Chấm bài #45 — Chưa rõ (SC) (ACC?) · 2026-07-06 12:43 → 17:15 (272 nến M1) · superseded

**Điểm: 3/10** — Range đáng vẽ, nhưng Phase C đặt sai chỗ hoàn toàn: cú rũ đẹp nhất của cả cấu trúc bị vứt xuống làm mSOW ở Phase B.

## Lỗi (nặng → nhẹ)

### 1. Cú rũ thật bị gán mSOW, Phase C dời đi chỗ khác — luật vi phạm: L5, L8
- **Thuật toán gắn:** mSOW 14:44 tại 4140.6, VSA **5.13x**, xếp vào Phase B. Phase C bị đẩy tới 16:29 với LPS[C] VSA 0.57x.
- **Đúng phải là:** 14:44 chính là **Spring/Shakeout** — thủng biên chính dưới 4143.3 xuống 4140.6, rồi bật ngược. Phase C phải bắt đầu tại đó.
- **Dấu hiệu quyết định:** ba con số cùng chỉ về một chỗ. (a) VSA 5.13x là **cây volume cao nhất toàn range** — trên panel volume đó là thanh vàng cao vọt duy nhất. (b) Độ sâu 2.7 giá = 27 tick, so ngưỡng rũ max(15 tick, 15%×17.4 giá = 26 tick) → **đạt**. (c) Sau cú đó giá đi thẳng lên 4164.0, tức **vượt hẳn biên đối diện** = 134% quãng đường — thừa mức 50% để xác nhận cú rũ theo mục 6 spec.
- **Nghi phạm:** cú này đi vào nhánh "outside → SOW → lùi vào trong → hạ cấp mSOW" thay vì nhánh phân loại cú rũ. Với v7.1, quyết định outside giờ so với **biên CHÍNH** nên một cú thủng 2.7 giá dễ bị coi là "đã ra ngoài" rồi hạ cấp, thay vì được xét làm Spring trước. Thứ tự xét sai: **phải phân loại cú rũ TRƯỚC khi kết luận outside**.

### 2. Nhãn SC nằm TRƯỚC nến mở range và lệch khỏi biên chính — luật vi phạm: L3 (biên chính = mức climax)
- **Thuật toán gắn:** nhãn SC tại **12:41**, giá 4145.8; range mở tại 12:43; biên chính dưới 4143.3.
- **Dấu hiệu quyết định:** nhãn nằm ngoài khung range 2 nến về thời gian và cao hơn chính biên nó tạo ra **2.5 giá** — trên ảnh thấy rõ chấm SC treo lơ lửng phía trên đường liền cam.
- **Nghi phạm:** đúng lỗi 13.1c đã tự ghi nhận "thử sửa rồi revert". Cửa sổ nhãn chỉ kẹp một phía (sau), không chặn phía trước.

### 3. ST[A] lơ lửng 42% chiều cao range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:15 tại 4150.7.
- **Dấu hiệu quyết định:** (4150.7−4143.3)/17.4 = **42.5% chiều cao**; retrace từ AR = 0.575, lại **vừa lọt 0.55**. Lỗi giống hệt bài #43 và #47 — ba bài liên tiếp rơi vào đúng dải 42–44%.
- **Đúng phải là:** không có nhịp nào về sát 4143.3 trước 14:44, nên hoặc phải chờ lâu hơn, hoặc thừa nhận Phase A chưa đóng.

### 4. Nến mở range không đủ tính chất climax — luật vi phạm: mục 3(1) spec
- **Dấu hiệu quyết định:** nến 12:43 có **VSA 1.28x** (ngưỡng 2.2x) và biên độ chỉ **1.9 giá**, thân 0.16. Nó chỉ được chọn vì là đáy cụm. Cây climax thật là 12:41 (VSA 3.27x, biên độ 5.6 giá).
- Hệ quả: mức biên chính dưới và nhãn climax tách rời nhau (lỗi #2).

### 5. LPS[C] nằm ở nửa TRÊN range — hệ quả tiêu cực của bản vá v7.1
- **Thuật toán gắn:** LPS[C] 16:29 tại 4155.8 = **72% chiều cao**, VSA 0.57x.
- **Nghi phạm:** v7.1 bỏ hẳn ràng buộc `_right_half` để chữa "thiếu Phase C". Đổi bệnh: giờ LPS[C] của một range phá LÊN lại nằm ở nửa trên, không còn là "điểm hỗ trợ cuối".

### 6. Range không được đặt tên dù cấu trúc đã rõ — luật vi phạm: L4, L10
- **Dấu hiệu quyết định:** có SOS 16:50 VSA **3.42x** thân 0.85, có LPS[D] 17:01 giữ trên biên phụ 4164.0, giá sau đó lên 4175. Đủ mọi bằng chứng của một **Tích luỹ** phá lên. Nhưng range bị đóng `superseded` vì range #46 sinh ra tại 16:58 — **trước cả khi range này kết thúc (17:15)**.
- **Nghi phạm:** cơ chế SIDEWAYS cắt vụn cấu trúc thật (đã liệt ở 13.1b, chưa sửa). Range con không được phép sinh khi range cha đang ở Phase D và cú phá của cha còn chưa kết thúc.

## Đạt
- **Mở range (L1):** MOVE giảm 21.8 giá / 76 nến / hiệu suất 0.36 — có move thật, climax chặn được.
- **Phase B dài nhất (L9):** 193/272 nến. Đúng tỉ lệ.
- **Biên phụ (L3):** đúng mỗi bên 1 cái (4140.6 dưới / 4164.0 trên), đều là cực trị xa nhất thật.
- **SOS:** neo đúng cây mạnh (3.42x, thân 0.85), khác hẳn bài #44/#46.
- SOT phía dưới đo được `n=3` = SOT thật, khớp với việc đáy sau cao dần trước khi bung — đọc effort/result đúng dấu.

## Cần hỏi người học
- Khi range cha còn đang chạy Phase D và cú phá của nó **thành công** (SOS + LPS[D] giữ được), có nên cấm hẳn việc sinh range con từ cú phá đó không? Ở bài này việc sinh con làm mất tên của một cấu trúc đã hoàn chỉnh.
