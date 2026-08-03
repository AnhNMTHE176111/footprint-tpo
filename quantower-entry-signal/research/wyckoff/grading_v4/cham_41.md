# Chấm bài #41 — Phân phối (DIST) · 2026-07-15 18:29 → 2026-07-16 01:56 (387 nến M1)

**Điểm: 5/10** — Đọc đúng bản chất (đây là một vùng phân phối thật, phá xuống), nhưng **cả 3 mốc neo của Phase A đều lệch** và mốc Phase D trễ 32 nến → phải sửa nhãn, không phải bỏ range.

## Lỗi (nặng → nhẹ)

### 1. Climax neo sai nến — biên chính trên thiếu 6.3 giá, sinh ra một "biên phụ" giả — luật vi phạm: L1 (climax phải CHẶN move) + L3 (biên chính = mức climax)
- **Thuật toán gắn:** BCLX tại 18:29, giá 4082.8 (VSA 3.32x) → biên CHÍNH trên = 4082.8, biên PHỤ trên = 4089.1.
- **Đúng phải là:** BCLX là **cụm 18:29–18:32**, đỉnh cụm = **4089.1 (18:31)**. Biên chính trên phải là 4089.1; và khi đó **không có biên phụ trên nào cả**.
- **Dấu hiệu quyết định trên chart:** 18:30 high 4086.6 **VSA 4.52x** (volume 436 — cao hơn hẳn nến được gọi climax: 254), 18:31 high 4089.1. Nến 18:29 không chặn được gì — giá còn đi thêm 6.3 giá trong 2 nến kế tiếp, cây nổ volume mạnh nhất nằm SAU nó. Cái "biên phụ 4089.1" không phải "một thế lực cố phá range" (L3) mà chính là đỉnh của cụm climax, xuất hiện khi range còn chưa có AR.
- **Nghi phạm trong thuật toán:** mục 3 chỉ kiểm "climax là cực trị của **240 nến quá khứ**"; không có cửa sổ xác nhận vài nến SAU để chốt cực trị của cụm. Range mở ngay tại nến đầu tiên đủ ngưỡng (1.4× biên độ + VSA 2.2x).

### 2. Nhãn AR đứng sai chỗ — lệch 9.2 giá và 35 nến so với AR mà biên chính đang dùng — luật vi phạm: L2 (AR phải là cú bật ngược thật) + lỗi kinh điển Ca #12 (7.pdf, nhầm vai AR/ST)
- **Thuật toán gắn:** AR tại 19:00, giá 4064.4 (VSA 1.09x); nhưng **biên chính dưới lại vẽ ở 4055.2**.
- **Đúng phải là:** AR = **4055.2 tại 19:35**. Phiếu số liệu và biên chính đang **mâu thuẫn nội bộ**: biên đã dời theo AR mới, nhãn thì đứng ở điểm cũ.
- **Dấu hiệu quyết định trên chart:** đáy thật của nhịp phản ứng sau BCLX là 4055.2 @19:35 (kiểm trên dữ liệu M1). Điểm 4064.4 @19:00 nằm **giữa đường giảm** — sau nó giá còn rơi thêm 9.2 giá. Trên ảnh, nhãn AR treo lơ lửng cách đường "biên CHINH duoi 4055.2" gần 9 giá, thấy bằng mắt.
- **Nghi phạm trong thuật toán:** cửa sổ tìm AR **cố định 40 nến** (mục 4.1 — chính là điểm nghi ngờ #2 của mục 12): AR thật ở nến thứ **66**. Sau đó nhánh "dời AR tới cực trị mới" có cập nhật biên nhưng **không cập nhật lại nhãn** đã phát.

### 3. ST[A] đứng đúng giữa range, không phải test lại vùng climax — luật vi phạm: L2 + THEORY §5 (vị trí ST chia 3 phần)
- **Thuật toán gắn:** ST[A] 4069.0 @20:26.
- **Đúng phải là:** ST[A] phải là cú quay lại **vùng climax** (4082–4089), hoặc ít nhất nằm trong 1/3 phía climax. 4069.0 = **50.0% chiều cao range** (4055.2–4082.8) → đúng 1/3 giữa, cách biên trên 13.8 giá. THEORY §5 chỉ gán ý nghĩa cho ST ở 1/3 dưới hoặc 1/3 trên; ST giữa range không có vai nào. Phase A do đó **chưa chốt xong** tại 20:26.
- **Dấu hiệu quyết định trên chart:** VSA nến ST[A] = 1.08x (không co lại rõ như một test), và nhìn ảnh thì nhãn ST[A] nằm chính giữa hộp range, cách xa mức BCLX.
- **Nghi phạm trong thuật toán:** ngưỡng "ST[A] phải hồi ≥ **40%** chiều cao climax↔AR" (mục 4.2) quá lỏng. Test lại vùng climax nghĩa là ~80–100%, hoặc phải chạm mức climax trong dung sai tick.

### 4. Mốc Phase D trễ 32 nến — bỏ mất đúng cây SOW thật — luật vi phạm: L10 + Ca #5 (4.pdf: ranh giới phase neo GIÁ ĐÓNG CỬA)
- **Thuật toán gắn:** SOW tại 01:31, giá 4046.4, **VSA 0.98x**, thân 0.71 → Phase C kéo tới 01:30 (56 nến), Phase D chỉ 26 nến.
- **Đúng phải là:** SOW tại **00:59** — nến đầu tiên **đóng cửa** dưới biên chính 4055.2: close 4050.4, **VSA 4.46x**, thân 0.81. Phase C phải kết thúc ở đó.
- **Dấu hiệu quyết định trên chart:** nhãn SOW hiện đang nằm **8.8 giá (88 tick) dưới** biên chính dưới, trên một nến volume chỉ ngang trung bình — trong khi cây phá biên thật có nỗ lực gấp 4.5 lần trung bình. Trên panel khối lượng, thanh vàng lớn quanh 00:59 chính là nó.
- **Nghi phạm trong thuật toán:** điều kiện xác nhận phá thật = **3 nến liên tiếp** đóng vượt biên +30 tick thân ≥45% (mục 5.1) rồi lấy **nến thứ 3 (hoặc muộn hơn)** làm mốc SOW. Xác nhận thì cần 3 nến, nhưng **nhãn và ranh giới phase phải hồi tố về nến phá đầu tiên**.

### 5. Thiếu Phase E dù giá đã rời range đi rất xa — luật vi phạm: L10
- **Thuật toán gắn:** range đóng ở Phase D, không có Phase E.
- **Đúng phải là:** đích Phase E = 1.0 × 27.6 giá tính từ 4055.2 → 4027.6. Trên ảnh giá xuống ~4027 lúc 02:31, tức **đã đạt**, chỉ là muộn hơn cửa sổ.
- **Nghi phạm trong thuật toán:** cửa sổ chờ sau SOW = **25 nến**. Vì mốc SOW đã trễ 32 nến (lỗi #4), cửa sổ 25 nến bị "đốt" ở đoạn giá đi ngang → mất Phase E.

## Đạt
- **L1 điều kiện mở range:** có MOVE tăng thật — 49.8 giá / 105 nến, hiệu suất hướng 0.35; nhìn ảnh là một đợt tăng thẳng từ ~4033.
- **L4 tên range:** origin BCLX + phá xuống thật = **Phân phối** — đúng.
- **L9:** Phase B (188 nến) là phase dài nhất — đúng.
- **L8 case khó:** không có cú rũ nào, Phase C gán ngược từ LPSY[C] @00:35 (4067.1) = đỉnh nhịp hồi cuối trước khi rơi — chọn hợp lý.
- **L7:** LPSY[C] chỉ đánh 1 điểm — đúng.
- Không có nhãn spam, không có nhãn sai vai (không nhầm UT/UTAD).

## Cần hỏi người học
- Khi mốc SOW/SOS được **xác nhận** bằng 3 nến, nhãn nên vẽ ở nến **phá đầu tiên** (hồi tố) hay nến **thứ 3** (thời điểm thật sự biết)? Cách vẽ hiện tại là nến thứ 3 trở đi, và nó làm ranh giới C/D lệch hàng chục nến ở mọi bài.
