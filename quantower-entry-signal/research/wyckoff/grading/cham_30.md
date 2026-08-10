# Chấm bài #30 — Phân phối (DIST) · 2026-06-10 06:08 → 08:02 (114 nến)

**Điểm: 5/10** — bối cảnh đúng (BCLX chặn đúng đỉnh của đợt tăng, sau đó giá sụp thật), nhưng Phase A bị nén còn 3 nến giữa AR và ST[A], mất hẳn Phase C, và nhãn SOW neo vào cây yếu.

## Lỗi (nặng → nhẹ)

### 1. Mất hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** A(20) → B(42) → D(25) → E(28). Không có Phase C.
- **Đúng phải là:** trước SOW phải có **LPSY[C]** — nhịp hồi cuối cùng bị chặn. Trên ảnh nhịp đó rất rõ: khoảng 06:58–07:06 giá hồi lên ~4234 rồi gãy. Đó là LPSY[C], và Phase C phải bắt đầu từ đó.
- **Dấu hiệu quyết định trên chart:** cửa sổ gán ngược = min(60, 0.8×42) = 33 nến trước SOW (tức từ 06:37). Trong đoạn đó giá dao động 4227–4234, **toàn bộ nằm dưới trung điểm range 4238.3** → ràng buộc v6 "pivot phải ở **nửa trên**" loại sạch ứng viên.
- **Nghi phạm trong thuật toán:** vá #3 (nới cửa sổ 0.5→0.8×B) không giải quyết được vì nút thắt là **ràng buộc nửa range**, không phải độ dài cửa sổ. Khi cấu trúc dốc xuống (THEORY §4.3 "phân phối dốc xuống"), nhịp hồi cuối tự nhiên nằm ở nửa dưới. Nên đo "nửa" theo **nửa trên của đoạn cửa sổ**, không phải nửa trên của range.

### 2. Nhãn SOW neo vào cây VSA 1.69× và chỉ vượt biên phụ 3 tick — luật vi phạm: L3 + THEORY §4.1 (SOW = volume tăng)
- **Thuật toán gắn:** SOW 07:10 tại **4228.3**, VSA 1.69×, thân 0.69. Biên phụ dưới là **4228.6** (do mSOW 06:44 tạo ra).
- **Đúng phải là:** L3 đòi SOS/SOW mạnh phải **đóng cửa bứt qua biên phụ**. Vượt 0.3 giá = 3 tick thì không phải bứt, đó là chạm. Cây phá thật với khối lượng nằm muộn hơn — nhìn panel khối lượng, hai cột vàng lớn nhất của cả chart nằm ở ~07:55 và ~08:40, đúng lúc giá sụp từ 4215 xuống 4185.
- **Nghi phạm trong thuật toán:** khâu neo hồi tố quét từ nến đầu tiên thò ra tới nến xác nhận thứ 3 — cửa sổ này kết thúc quá sớm nên không với tới cây phá thật. Vá #5 vòng này chỉ áp cho hạ cấp mSOS/mSOW, chưa áp cho SOS/SOW đã chốt.

### 3. Phase A nén còn 3 nến giữa AR và ST[A], AR là nến chết — luật vi phạm: L2
- **Thuật toán gắn:** AR 06:24 (VSA **0.96×**, thân 0.69) → ST[A] 06:27 (VSA 1.24×) tại 4239.2.
- **Đúng phải là:** AR là "lực đẩy tự động" — một cú bật ngược **thật**, phải đọc được trên khối lượng. Ở đây AR chỉ là một đáy tạm trong nhịp trôi xuống từ BCLX, khối lượng dưới trung bình; và chỉ 3 nến sau đã có ST[A]. Ba lần đổi hướng nằm gọn trong 20 nến thì CHoCH chưa kịp hình thành.
- **Dấu hiệu quyết định trên chart:** ST[A] 4239.2 nằm ở **56% chiều cao** range (biên 4231.1–4245.5, cao 14.4) — lại là nhịp giữa range chứ không phải test lại vùng BCLX 4245.5. Cùng gốc lỗi với bài #25/#29: ngưỡng 0.4 đo từ AR không ràng buộc khoảng cách tới climax.

### 4. (nhẹ) Range 14.4 giá / 114 nến trên M1 — luật vi phạm: cảnh báo "range quá vụn"
- Biên chính chỉ cao 0.34% giá và cả cấu trúc gói trong chưa đầy 2 tiếng. Vẫn còn chấp nhận được (khác hẳn bài #27/#28) vì Phase B 42 nến có test cả hai biên, nhưng đây là ngưỡng dưới của cái gọi là vùng đấu giá.

## Đạt
- L1: MOVE tăng 38.0 giá / 83 nến / hiệu suất 0.38, và BCLX (VSA 2.77×) là **đỉnh cao nhất** chặn đúng đợt tăng đó. Điều kiện CẦN thoả rõ — nhìn ảnh thấy ngay đường chân MOVE chạy từ 4207 lên 4245.
- L4: origin BCLX + phá **xuống** = Phân phối. Đúng, và lần này hướng phá là thật: giá đi từ 4231 xuống 4185, tức hơn 3× chiều cao range.
- L3: một biên phụ duy nhất phía dưới (4228.6, do mSOW tạo), tỷ lệ 1.17× — đúng luật "mỗi bên nhiều nhất 1".
- L10: SOW → LPSY[D] (07:16, 4225.9) giữ được **dưới** biên → Phase E 28 nến đi tiếp. Khuôn CBR đúng.
- Chú thích nỗ lực/kết quả er=0.61 ghi "HIỆU QUẢ" — đúng dấu.
