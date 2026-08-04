# Chấm bài #19 — Chưa rõ (BCLX) (DIST?) · 2026-05-20 15:16 → 2026-05-21 01:56 (421 nến M1)

**Điểm: 6/10** — Khung range vẽ đúng chỗ (đây là một vùng đấu giá thật, 421 nến đi ngang rõ), nhưng phải sửa ST[A], phải sửa độ dài Phase C, và có 2 lỗi đo/gán phase của phần mềm.

## Lỗi (nặng → nhẹ)

### 1. ST[A] không test lại vùng climax — chỉ là một cái ngọ nguậy giữa range — luật vi phạm: L2 (+ THEORY §5 bảng vị trí ST)
- **Thuật toán gắn:** ST[A] tại 15:40, giá **4576.4**, kết Phase A ở đó.
- **Đúng phải là:** ST[A] phải là cú quay lại **vùng climax 4591.2**. 4576.4 nằm ở **42% biên chính** (4565.6–4591.2) — đúng giữa range. Phase A ở đây **chưa xong**; ST[A] thật là cú lên test lại 4589–4592 (nhìn trên chart: cụm nến áp biên chính trên quanh 19:44), hoặc phải công nhận cấu trúc này không có ST[A] rõ và range chưa đủ điều kiện mở theo L2.
- **Dấu hiệu quyết định trên chart:** 4576.4 − 4565.6 = 10.8 giá trên tổng biên 25.6 giá; nến ST[A] VSA 1.20x, thân/biên 0.53 — không có gì cho thấy nó là một cú test biên.
- **Nghi phạm trong thuật toán:** nhánh `A_st` chỉ đòi "hồi ngược lại phía climax" theo **tương đối** (v6 đã đổi sang AR/ST[A] tương đối) mà không có ngưỡng "phải đạt ≥ x% đường về mức climax". Cần gate kiểu `|st − climax| ≤ 0.35 × biên chính`.

### 2. Phase C = 53 nến, dài gấp đôi Phase A — luật vi phạm: L8
- **Thuật toán gắn:** A 25n · B 318n · **C 53n** · D 26n.
- **Đúng phải là:** Phase C là phase **ngắn nhất**. Ở đây C (53n) > A (25n) và > D (26n). Đọc lại chart: từ LPS[C] 00:27 (4572.4) giá còn lùng bùng gần 45 nến rồi mới có mSOS/SOS — nghĩa là LPS[C] bị đặt **quá sớm**. LPS[C] thật là nhịp lùi cuối cùng ngay trước cú bung (quanh 01:05–01:10, sát biên chính trên), Phase C chỉ nên dài ~10-15 nến.
- **Dấu hiệu quyết định trên chart:** LPS[C] 00:27 tại 4572.4 = 26% từ biên dưới, sau nó giá còn tạo thêm một nhịp xuống nữa (~4568 quanh 00:45) rồi mới lên — một LPS thật không được bị xuyên qua sau đó.
- **Nghi phạm trong thuật toán:** LPS[C] được gán bằng "đáy cục bộ đầu tiên sau khi Phase B kết thúc" thay vì gán **ngược từ SOS** (L8 case khó: "có Phase D rồi mới xác định được Phase C"). Cần: tìm SOS trước, rồi lùi lại tìm đáy cục bộ **cuối cùng** trước SOS.

### 3. mSOS bị gán vào Phase B trong khi thời điểm của nó nằm trong Phase C — luật vi phạm: lỗi nhất quán nội bộ (không phải Wyckoff)
- **Thuật toán gắn:** mSOS 2026-05-21 **01:11**, cột Phase = **B**. Nhưng Phase B kết thúc **00:26**, và 01:11 rơi vào Phase C (00:27–01:24).
- **Đúng phải là:** nhãn phải mang phase theo mốc thời gian của chính nó. mSOS 01:11 thuộc Phase C (và thực chất nó là phần đầu của cú phá — xem lỗi 4).
- **Dấu hiệu quyết định trên chart:** trên ảnh nhãn `mSOS` nằm hẳn bên trong khung vạch tím của Phase C.
- **Nghi phạm trong thuật toán:** phase của nhãn được ghi lúc **phát hiện** (khi đó range còn đang ở Phase B) và không được cập nhật lại sau khi ranh giới phase được kẻ hồi tố.

### 4. mSOS 4596.0 không phải "phá rồi thu hẳn vào trong range" — luật vi phạm: định nghĩa mSOS v6 + L5
- **Thuật toán gắn:** mSOS 01:11 tại 4596.0 (VSA 3.21x), rồi SOS 01:25 tại 4600.3 — cách nhau **14 nến**.
- **Đúng phải là:** mSOS theo nghĩa v6 phải **hồi về thu hẳn vào trong range**. Ở đây giá vượt 4591.2, chỉ co nhẹ, rồi bung tiếp lên 4600.3 và đi thẳng tới 4607 — đó là **một cú phá liên tục**, mSOS chỉ là nến đầu của SOS. Đúng ra không nên có nhãn mSOS ở đây; 4596.0 vẫn là biên phụ trên hợp lệ nhưng phải mang nhãn SOS (nến khởi phát).
- **Dấu hiệu quyết định trên chart:** giữa 01:11 và 01:25 giá không lần nào đóng cửa lại dưới 4591.2 (nhìn cụm nến xanh sát biên chính trên trên ảnh).
- **Nghi phạm trong thuật toán:** điều kiện "thu hẳn vào trong range" đang được kiểm bằng **bóng nến / cực trị** hoặc bằng cửa sổ quá ngắn, chưa neo **giá đóng cửa** (Ca #5 nguồn 4.pdf: ranh giới phải neo close, không neo wick).

### 5. Cây được chọn làm climax không phải cây cao trào — luật vi phạm: THEORY §3.3 (SC/BCLX = volume + spread lớn nhất)
- **Thuật toán gắn:** climax = nến 15:16 (vol 91, VSA **4.45x**, biên độ 10.1 giá); phiếu ghi "nhãn climax mang VSA=4.45x (cây volume cao nhất trong cụm)".
- **Đúng phải là:** nến liền trước 15:15 có vol **133, VSA 7.69x, biên độ 22.2 giá** — cao hơn hẳn. Câu "cây volume cao nhất trong cụm" **tự mâu thuẫn với bảng 12 nến do chính nó in ra**. Mức climax 4591.2 giữ nguyên là đúng (cực trị), nhưng cây cao trào phải là 15:15.
- **Nghi phạm trong thuật toán:** cửa sổ tìm "cây volume cao nhất trong cụm" chỉ quét từ nến climax **trở đi** (hoặc bán kính 0), không quét nến trước. Mở rộng cụm sang ±3 nến.

### 6. Chỉ số nỗ lực/kết quả in nhãn diễn giải cứng (lỗi ĐO) — luật vi phạm: THEORY §2.2 Effort vs Result
- **Thuật toán in:** effort 2.17x, result 1.65, er = 1.32 → "vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** riêng bài này diễn giải **đúng** (er > 1 = nỗ lực > kết quả). Nhưng đối chiếu bài #20 (er=0.18), #21 (0.49), #23 (0.38), #24 (0.52) đều in **cùng một câu** "volume nhiều, kết quả ít" → chuỗi này bị **hardcode**, không rẽ theo ngưỡng er. Đây là lỗi hệ thống, phải sửa ở tất cả các bài.
- **Nghi phạm trong thuật toán:** câu diễn giải nằm ngoài nhánh `if er > 1`.

### 7. SOT phía trên: n=1 mà vẫn báo "chớm" kèm tỷ lệ 0.00 (lỗi trình bày)
- Với n=1 không có gì để so sánh (THEORY §7: cần **≥3 lần đẩy** SOT mới có nghĩa). In "chớm n=1, thrust cuối/đầu=0.00" gây hiểu sai là lực đẩy triệt tiêu. Nên in `chưa đủ dữ liệu (n<3)`.

## Đạt
- **L1 — điều kiện mở range:** move tăng 81.5 giá / 63 nến, hiệu suất 0.44, bị nến 15:15–15:16 (VSA 7.69x/4.45x) chặn tại đúng cực trị 4591.2. Đây là climax **chặn** move, không nằm giữa move.
- **L3 — biên:** biên chính 4565.6 (AR) + 4591.2 (climax), cố định, không bị kéo theo giá. Biên phụ mỗi bên đúng 1: trên 4596.0, dưới 4561.2 (mSOW) — đều là cực trị xa nhất.
- **L9 — Phase B là phase dài nhất:** 318/421 nến. Đúng tinh thần.
- **L6:** không còn nhãn ST[B] rác, không spam UA/UT.
- **Bias test biên = +0** đo đúng: trong Phase B giá chạm cả biên trên (cụm ~4592 quanh 19:44) và biên dưới (mSOW 4561.2).
- **Cơ chế `superseded`** dùng hợp lý: cú phá 01:25 sinh ra range mới (bài #20) nên range này không bị gán tên 4 mẫu hình.
- **L7:** LPS[C] và LPS[D] đều chỉ 1 điểm, không vẽ vùng.
