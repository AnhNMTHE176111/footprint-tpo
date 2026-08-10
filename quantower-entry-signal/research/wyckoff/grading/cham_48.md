# Chấm bài #48 — Phân phối (DIST) · 2026-07-08 03:13 → 07:37 (264 nến M1) · sinh từ cú phá

**Điểm: 2/10** — Biên chính nằm lọt giữa vùng giá, không chặn gì. Không nên vẽ range ở đây; và cú sụp thật thì bị bỏ lỡ.

## Lỗi (nặng → nhẹ)

### 1. Biên chính nằm GIỮA vùng giá, không phải biên của vùng đấu giá — luật vi phạm: L3, L1
- **Thuật toán gắn:** biên chính 4135.7–4141.5 = **5.8 giá**; biên phụ 4128.4–4144.6 = **16.2 giá** (tỷ lệ 2.79x).
- **Đúng phải là:** vùng cân bằng thật là **4128–4145**. Hai đường liền cam phải nằm ở hai mép đó.
- **Dấu hiệu quyết định:** trên ảnh, hai đường liền cam nằm sát nhau ở **giữa** khối nến, còn giá dao động rộng gấp gần 3 lần ra cả hai phía suốt 264 nến. Đây là lỗi A của vòng v4 ("biên chính nằm giữa vùng giá") tái xuất qua cửa SIDEWAYS.
- **Nghi phạm:** range con sinh từ cú phá neo biên bằng **cực trị của chính cú phá** (5 nến đầu tiên: climax 03:13, AR 03:18) rồi khoá cứng. Với 5 nến thì cực trị đó không mang thông tin gì về vùng cân bằng sắp hình thành. Guard "biên phụ/chính ≤ 4.0×" quá lỏng, 2.79x lách qua thoải mái — đúng như 13.1b đã cảnh báo với range hẹp.

### 2. Phase A chỉ 16 nến, AR yếu, ST[A] xuyên qua climax — luật vi phạm: L2
- **Thuật toán gắn:** BCLX? 03:13 → AR (yếu) 03:18 (**5 nến sau**, VSA 0.68x) → ST[A] 03:28 tại **4142.3**, vượt trên mức climax 4141.5.
- **Dấu hiệu quyết định:** hồi từ AR = (4142.3−4135.7)/5.8 = **114% khoảng AR↔climax**. Ba lần đổi hướng của L2 ở đây chỉ là ba cây nến lắc trong 5.8 giá — không phải một CHoCH.
- **Nghi phạm:** thuật toán tự gắn cờ "AR (yếu)" nhưng cờ đó **không đổi logic gì** (spec mục 4.1 ghi rõ "chỉ là cảnh báo hiển thị"). Đây đúng là ca phải bỏ ứng viên, không phải ca cảnh báo.

### 3. SOW neo vào cây VSA 0.68x, và chỉ hơn biên phụ 1 tick — luật vi phạm: L3, L10
- **Thuật toán gắn:** SOW 07:12 tại **4128.3**, **VSA 0.68x**; biên phụ dưới **4128.4**.
- **Dấu hiệu quyết định:** vượt biên phụ đúng **0.1 giá = 1 tick**. Trong khi mSOS 06:41 có **VSA 3.70x** — nhãn *minor* lại đang đeo cây mạnh gấp 5 lần cây mang nhãn phá thật. Ca "cách biên phụ 1 tick" mà 13.1b bắt ở bài #45 vòng trước, tái xuất nguyên vẹn.

### 4. LPSY[D] hồi hẳn vào TRONG range mà vẫn đặt tên Phân phối — luật vi phạm: L10 (retest phải GIỮ được ngoài biên)
- **Thuật toán gắn:** LPSY[D] 07:32 tại **4137.5**, rồi Phase E, rồi đặt tên "Phân phối (DIST)".
- **Đúng phải là:** 4137.5 nằm **bên trong biên chính 4135.7–4141.5** — giá đã hồi vượt qua cả biên vừa phá. Theo chính spec (mục 7, Câu 1) đóng cửa lùi hẳn qua biên chính = **cú phá BỊ VÔ HIỆU**, phải hạ cấp mSOW và **không đặt tên**.
- **Dấu hiệu quyết định:** trên ảnh, sau SOW giá bật lên tận 4140 (07:30) — cao hơn cả điểm khởi phát cú phá. Không có "giữ ngoài biên" ở bất kỳ nghĩa nào.
- **Nghi phạm:** nhánh vô hiệu hoá dùng `edge` + `fail_tol` 30 tick; hồi từ 4128.3 lên 4137.5 là 92 tick, quá thừa — nghi bước kiểm này bị bỏ qua khi LPSY[D] đã được ghi nhận, tức thứ tự xét sai (ghi retest trước, kiểm vô hiệu sau).

### 5. Bỏ lỡ cú sụp thật ngay sau khi đóng range — luật vi phạm: L10 (Phase E = đi tìm vùng giá mới)
- **Dấu hiệu quyết định:** Phase E dài đúng **1 nến** (07:37). Nhưng trên ảnh, cây sụp thật là nến ~08:10: rơi thẳng từ 4128 xuống **4092** với thanh volume vàng cao nhất toàn chart. MSOW thật nằm **ngoài** range, sau khi range đã đóng 30 phút.
- **Đúng phải là:** nếu vẽ đúng biên (4128–4145 theo lỗi #1), cây 08:10 mới là SOW/MSOW và Phase E mới có nghĩa.

### 6. Phase B 203 nến chỉ có 2 nhãn — luật vi phạm: L9
- **Dấu hiệu quyết định:** với biên chính 5.8 giá, giá vượt lên trên 4141.5 và xuống dưới 4135.7 hàng chục lần (đỉnh 04:58 ~4145, 06:25 ~4144.6, đáy 04:17 ~4131, 07:00 ~4129). Quy tắc "mỗi bên chỉ giữ 1 nhãn" khiến toàn bộ diễn biến này biến mất, chỉ còn mSOW + mSOS.

## Đạt
- **Phase C ngắn hơn Phase B (L8):** 20 vs 203 nến.
- **Phase B dài nhất (L9):** 203/264 nến.
- **Nhãn `BCLX?` + "AR (yếu)" + dòng "khong co cao trao that":** thuật toán khai báo trung thực mức tin cậy của mình. Nếu có guard chặn theo các cờ này thì range đã không bị vẽ.
- **Tên range (L4):** giả sử cú phá là thật thì origin BCLX + phá xuống = Phân phối, gọi tên đúng luật (nhưng tiền đề sai, xem lỗi #4).
- Chú thích effort/result đọc đúng dấu (`er=0.78 — nhịp HIỆU QUẢ`).
