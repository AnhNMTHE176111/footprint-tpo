# Chấm bài #07 — Phân phối (DIST) · 2026-04-23 12:00 → 2026-04-24 05:19 (541 nến M1)

**Điểm: 3/10** — Câu chuyện phân phối dốc xuống thì đọc đúng, nhưng **biên chính trên nằm lọt trong đám nến**: giá giao dịch phía TRÊN nó suốt mấy tiếng. Cây climax lại là một nến 15 hợp đồng. Phải vẽ lại Phase A từ đầu, giữ nguyên hướng đọc.

## Lỗi (nặng → nhẹ)

### 1. Biên chính trên 4778.6 nằm giữa vùng giá — climax không chặn move — luật vi phạm: L1, L3
- **Thuật toán gắn:** BCLX 04-23 12:00 đỉnh **4778.6** → biên CHÍNH trên; biên phụ trên 4796.4.
- **Đúng phải là:** biên chính trên phải ở vùng **4796.4** (đỉnh thật của cú đẩy). Cây 12:00 không chặn được gì cả.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu — 5 nến ngay sau climax có đỉnh **4783.6 / 4784.5 / 4783.6 / 4784.1 / 4786.7**, tất cả cao hơn "climax". Trên ảnh, nét liền cam trên đi xuyên qua thân đám nến: gần như toàn bộ Phase A (12:00 → 16:10) và một phần Phase B nằm **phía trên** biên chính. Một đường mà giá ở trên nó hàng giờ thì không phải biên.
- **Nghi phạm trong thuật toán:** điều kiện (2) mục 3 chỉ kiểm climax là cực trị của **cửa sổ 240 nến nhìn lại**, không kiểm phía trước. Lỗi giống bài #06 và #09.

### 2. "Climax" chỉ có 15 hợp đồng — không có nỗ lực nào ở đây — luật vi phạm: mục 8 Effort vs Result, THEORY §2.2
- **Thuật toán gắn:** BCLX VSA **5.45x**, biên độ nến 6.7 giá.
- **Đúng phải là:** không mở range ở nến này. VSA 5.45x đến từ việc TB khối lượng 20 nến chỉ ≈ **2.75 hợp đồng** (15 ÷ 5.45), không phải vì có tay to nhảy vào. THEORY §2.2: nỗ lực = khối lượng; 15 hợp đồng là không có nỗ lực.
- **Dấu hiệu quyết định trên chart:** 6 nến trước climax có khối lượng **4, 4, 1, 2, 2, 2** hợp đồng, ba nến trong đó là nến chết (O=H=L=C). So sánh: cú rơi 04-23 17:41 trên cùng chart có cột khối lượng **cao nhất toàn ảnh** — đó mới là chỗ có tay to. Cao trào mua thật (nếu có) phải ở vùng khối lượng đó, không phải ở nến 15 hợp đồng.
- **Nghi phạm trong thuật toán:** VSA là tỉ lệ **tương đối** nên vô nghĩa khi mẫu số ~2-3 hợp đồng. Cần thêm sàn **khối lượng tuyệt đối** cho nến climax (ví dụ ≥ X hợp đồng, hoặc ≥ phân vị 80 của cả ngày) trước khi cho phép mở range.

### 3. Nhãn AR bị bỏ rơi, lệch 45.9 giá so với biên chính dưới — luật vi phạm: L2, L3
- **Thuật toán gắn:** AR 04-23 17:09 giá **4762.4**; biên CHÍNH dưới **4716.5**.
- **Đúng phải là:** AR = đáy cú rơi 04-23 **17:41** ở **4716.5** — cú rơi đó vừa là đáy phản ứng vừa là chỗ khối lượng lớn nhất chart. Cây 4762.4 chỉ là một nhịp nghỉ giữa đường rơi, VSA 2.03x.
- **Dấu hiệu quyết định trên chart:** biên chính dưới (4716.5) và nhãn AR (4762.4) lệch nhau **45.9 giá**, tức 74% chiều cao range. Theo L3 biên chính = climax + AR, hai con số này không thể cùng đúng.
- **Nghi phạm trong thuật toán:** cửa sổ AR cố định 40 nến; AR không được dời khi biên nới ra, dù mục 4.2 spec yêu cầu dời. Lặp lại ở #06 và #09 → sửa một chỗ được cả ba.

### 4. Phase A dài hơn Phase B — luật vi phạm: L9
- **Thuật toán gắn:** A = **268 nến** (50% cả range), B = **189 nến**, C = 59, D = 26.
- **Đúng phải là:** L9 — Phase B là phase dài nhất. Phase A chiếm nửa range là dấu hiệu climax bị gán quá sớm: nếu neo BCLX ở vùng 4796.4 (04-23 ~13:00-16:00) và AR ở 4716.5 (17:41), Phase A co lại còn ~1/3 và Phase B thành phase dài nhất như phải thế.
- **Dấu hiệu quyết định trên chart:** vạch tím Phase B chỉ bắt đầu ở 18:02, sau khi cú rơi lớn nhất chart đã xảy ra — tức toàn bộ đoạn kịch tính nhất bị nhét vào Phase A.
- **Nghi phạm trong thuật toán:** hệ quả của lỗi #1 và #3, không phải một tham số riêng.

### 5. SOW không có khối lượng — luật vi phạm: mục 8, THEORY §4.1
- **Thuật toán gắn:** SOW 04-24 04:27 giá 4710.9, VSA **0.69x**, thân 1.00.
- **Đúng phải là:** THEORY §4.1 — SOW "thường kèm chênh lệch/khối lượng **tăng**". Ở đây khối lượng dưới trung bình. THEORY §6.3 cho phép breakout không cần volume (khi nguồn cung nổi đã cạn) nên **không bác bỏ** cú phá, nhưng phải hạ mức tin cậy và không được gọi là MSOW.
- **Dấu hiệu quyết định trên chart:** cột khối lượng tại SOW thấp hơn đường TB 20 nến, trong khi trước đó ở 04-24 02:33 và 04:37 có mấy cột vàng cao hơn nhiều.

### 6. LPSY[C] nằm giữa range, chọn máy móc — luật vi phạm: THEORY §4.1 (định nghĩa LPSY)
- **Thuật toán gắn:** LPSY[C] 04-24 02:18 giá **4744.9**, VSA 0.61x, thân **0.00** (nến doji).
- **Đúng phải là:** LPSY = "đợt phục hồi **yếu** sau khi test kháng cự cục bộ ở biên dưới, trên biên hẹp". 4744.9 cách biên dưới 4716.5 tới **28.4 giá** = 46% chiều cao range — đây là giữa range, không phải nhịp hồi sát biên.
- **Dấu hiệu quyết định trên chart:** vị trí thời gian thì chấp nhận được (đúng đỉnh cục bộ mà từ đó giá rơi liền một mạch xuống SOW), nhưng độ cao thì không phải vai LPSY.
- **Nghi phạm trong thuật toán:** mục 6 case KHÓ — "lấy đỉnh cao nhất trong 60 nến trước cú phá". Cách chọn thuần cực trị không kiểm khoảng cách tới biên. Nên thêm điều kiện LPSY phải nằm trong nửa dưới range (hoặc trong X giá tính từ biên bị phá).

### 7. Bỏ mất nhãn ở cú rơi 04-23 17:41 — luật vi phạm: mục 9 nhãn thiếu
- Cú rơi có **khối lượng lớn nhất toàn chart** không được gắn nhãn gì. Dù gọi là AR (theo lỗi #3) hay mSOW, đây là sự kiện quan trọng nhất của range và đang bị để trống.

## Đạt
- **Tên range đúng (L4):** BCLX + phá thật xuống = Phân phối; hình trên ảnh đúng dạng "phân phối dốc xuống" (THEORY §4.3) — đỉnh thấp dần 4796 → 4774 → 4752 → 4736 rồi sập.
- **Có MOVE thật trước climax:** 43.0 giá / 58 nến / hiệu suất 0.37 — mũi xám là một đoạn tăng liền mạch từ ~4735.
- **ST[A] đặt đúng vai:** 4774.6 nằm sát dưới vùng climax, VSA 0.76x và thân 0.08 — đúng chuẩn "spread/volume giảm khi quay lại tiệm cận kháng cự" (THEORY §4.1). Đây là nhãn tốt nhất của bài.
- **Phase C ngắn (L8):** 59 nến, ngắn hơn B — đúng chiều.
- **Không có ST[B] (L6), LPSY[C] một điểm (L7), biên phụ mỗi bên tối đa 1 (L3).**
- **Không bịa Spring/UTAD:** bài này không có cú rũ nào và thuật toán **không** gán bừa — đúng THEORY §3.5 "không phải cấu trúc nào cũng có Spring/Shakeout".

## Cần hỏi người học
- Có đồng ý thêm **sàn khối lượng tuyệt đối** cho nến climax không? Nếu có thì đặt theo con số cố định (vd ≥ 30 hợp đồng cho GC M1) hay theo phân vị của chính ngày đó?
