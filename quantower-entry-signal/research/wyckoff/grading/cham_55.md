# Chấm bài #55 — Chưa rõ (BCLX) (DIST?) · 2026-07-27 00:14 → 15:56 (941 nến M1, đang chạy)

**Điểm: 2/10** — Không nên vẽ range ở đây theo cách này. Cả Phase A dựng trên hai cây nến khối lượng dưới trung bình, nhãn climax rơi giữa move, biên chính dưới nằm lọt giữa hành động giá cả ngày, và cú sụp lớn nhất trong ngày được gán cho một cây VSA 0.57x.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX rơi giữa move, trước nến mở range 14 nến — luật vi phạm: L1/L3
- **Thuật toán gắn:** BCLX tại **00:00**, giá **4104.6**, VSA 6.36x.
- **Đúng phải là:** climax mở range là **00:14 tại 4119.3** (phiếu ghi rõ, và đó cũng là biên chính trên). Nhãn phải nằm tại/sát nến đó.
- **Dấu hiệu quyết định trên chart:** chấm BCLX nằm **bên trái vạch Phase A** và **thấp hơn đỉnh 14.7 giá**, đúng giữa đoạn dốc còn đang đi lên (00:09 → 00:14 giá còn tăng liên tục 4110 → 4119). Cây 00:00 không chặn được gì cả. Nó cũng nằm ngoài cửa sổ 12 nến (-6..+5) mà chính phiếu in ra.
- **Nghi phạm trong thuật toán:** đúng chỗ fix #4 tuyên bố đã vá. Ở đây bộ chọn nhãn vẫn ưu tiên **VSA cao nhất** (6.36x) trên một cửa sổ quét lùi quá rộng, không kẹp `idx_label ≥ idx_range_start`. Lặp lại y hệt bài #53 → không phải ca lẻ, là lỗi hệ thống còn nguyên.

### 2. Phase A dựng trên hai cây nến rỗng — luật vi phạm: L2 + §2.2 THEORY (Effort vs Result)
- **Thuật toán gắn:** AR 4093.2 VSA **0.44x**; ST[A] 4104.9 VSA **0.22x**.
- **Đúng phải là:** AR là "phản ứng tự động" sau cao trào — phải có nỗ lực đi kèm. Hai cây dưới nửa khối lượng trung bình không chứng minh được lần đổi hướng nào. Đây là CHoCH tự phong.
- **Dấu hiệu quyết định trên chart:** cả AR lẫn ST[A] không có thanh vàng nào (VSA < 2.2x) ở panel khối lượng, trong khi cụm 00:09-00:12 (3.52x / 2.90x / 2.83x) mới là chỗ có nỗ lực thật.
- **Nghi phạm trong thuật toán:** `ar_vsa`/`sta_vsa` mới **chỉ đo để hiển thị, chưa gate** (mục 0c #9 của v6). Đến v7 vẫn chưa gate. Đây là ca đòi gate.

### 3. ST[A] không test được vùng climax — luật vi phạm: L2 (fix #2 chưa đủ)
- **Thuật toán gắn:** ST[A] 4104.9, tức hồi **(4104.9−4093.2)/(4119.3−4093.2) = 0.448** khoảng AR↔climax.
- **Đúng phải là:** ST[A] phải quay lại **kiểm tra vùng climax**; ở 44.8% nó dừng ngay giữa range, cách climax 14.4 giá.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm gần đúng nửa chiều cao giữa hai đường nét liền.
- **Nghi phạm trong thuật toán:** fix #2 nâng ngưỡng 0.2 → 0.4 và ca này lọt qua với **0.448** — chỉ hơn ngưỡng 0.048. Nâng từ 0.2 lên 0.4 không giải quyết được vấn đề "ST[A] rơi ở 40-70% chiều cao"; muốn đúng L2 thì ngưỡng phải ở vùng 0.7-0.8, hoặc đo bằng cấu trúc (ST[A] phải là swing pivot nằm trong 1/3 phía climax).

### 4. mSOW neo vào cây VSA 0.57x trong khi nhịp sụp có cây 4-6x — luật vi phạm: §2.2 THEORY, fix #5 thất bại
- **Thuật toán gắn:** mSOW 14:43 tại 4067.1, VSA **0.57x**.
- **Đúng phải là:** nhịp sụp 13:00 → 14:24 (4100 → 4067) là chỗ có cụm khối lượng lớn nhất toàn chart (nhiều thanh vàng liên tiếp trên panel). Nhãn phải rơi vào cây phá thật trong cụm đó, không phải cây gần như không giao dịch ở đáy.
- **Nghi phạm trong thuật toán:** fix #5 ("quét lại lấy nến VSA cao nhất trong đoạn thăm dò") không có tác dụng ở đây — có vẻ nhánh này vẫn neo theo **cực trị giá** thay vì VSA. Chú ý: ở bài #51/#52 thì ngược lại (neo theo VSA, trôi vào giữa range). Hai nhánh đang mâu thuẫn nhau; phải hợp nhất thành một luật: **VSA cao nhất trong số các nến nằm ngoài biên của nhịp đó**.

### 5. Biên chính dưới nằm giữa hành động giá, range không kết thúc — luật vi phạm: L3, L9, L10
- **Thuật toán gắn:** biên chính dưới 4093.2, Phase B = 917/941 nến, trạng thái vẫn `active`.
- **Đúng phải là:** giá sống **dưới** 4093.2 gần như liên tục từ 03:11 đến 06:00 và từ 12:00 tới hết range (xuống tận 4067) — đó không còn là "dao động trong range" mà là SOW đã xảy ra từ lâu. Cấu trúc đúng: Phân phối, Phase D bắt đầu ở nhịp sụp 13:00.
- **Nghi phạm trong thuật toán:** cùng vòng lặp biên phụ như bài #54 — biên phụ dưới 4067.1 do chính nhịp sụp nới ra, nên nhịp đó không bao giờ "vượt qua biên phụ" được.

## Đạt
- **Mục 1 (L1) một phần:** có move tăng thật trước climax (13.2 giá / 50 nến) và cụm khối lượng cao ở 00:09-00:12 — điều kiện mở range về nguyên tắc thoả, dù mốc climax và nhãn đặt sai.
- **Mục 3 (L3) một phần:** biên phụ đúng 1 bên (dưới, 4067.1), không có biên phụ trên vì giá chưa bao giờ vượt 4119.3 — nhất quán.
- Không có nhãn spam: cả range chỉ 4 nhãn, không lặp UTAD/LPS bừa.

## Cần hỏi người học
- Range này vẫn `active` sau 941 nến (gần 16 giờ) và đã đi 52 giá — có nên đặt **trần thời gian/biên độ** để tự đóng range ở trạng thái "hỏng" thay vì giữ nó chạy mãi? THEORY không phân xử được chỗ này.
