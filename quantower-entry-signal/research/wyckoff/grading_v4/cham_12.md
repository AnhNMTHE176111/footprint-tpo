# Chấm bài #12 — Tái phân phối (RE-DIST) · 2026-05-12 13:15 → 18:47 (265 nến M1)

**Điểm: 1/10** — Bài sai nặng nhất trong lô. Cú sụp thật 46 giá bị xếp vào "Phase C", còn nhãn SOW lại dán lên một nến 4 lot; kết cục thật là giá đi LÊN nên cả tên range cũng ngược.

## Lỗi (nặng → nhẹ)

### 1. Bỏ mất cú phá thật: giá rơi xuống 4680.8 mà máy vẫn đang "chờ Phase C" — luật vi phạm: L8, L10 + THEORY §4.2 Phase D
- **Thuật toán gắn:** đoạn 14:33 → 16:51 = **Phase C dài 121 nến** (đúng trần chờ 120 nến rồi timeout, lùi về Phase B).
- **Đúng phải là:** trong chính đoạn đó giá đóng cửa xuống tận **4680.8 (15:25)** — thấp hơn biên chính dưới 4726.5 **45.7 giá**, tức **2.6 lần** chiều cao biên chính (17.9 giá), kèm chuỗi nến VSA 10.51x (15:10) và 8.35x (15:54). Đó là **SOW/MSOW** không thể tranh luận, tức Phase D bắt đầu ở đây.
- **Dấu hiệu quyết định trên chart:** cây rơi thẳng xuống ~4681 quanh 15:25 nằm hoàn toàn dưới cả nét đứt biên phụ, và panel volume có 2 thanh vàng cao nhất chart nằm đúng đoạn đó.
- **Nghi phạm trong thuật toán:** khi `state = Phase C` (mục 6) máy chỉ đo "đã đi được bao nhiêu % sang biên đối diện" và "có đóng cửa vượt lại điểm rũ chưa" — **không còn kiểm điều kiện phá thật của mục 5.1 Kết cục B**. Nghĩa là máy bị mù tới 120 nến. Đây là lỗi gốc, cùng cơ chế gây Phase C = 121 nến ở cả bài #11 và #13.

### 2. Biên phụ dưới ghi 4714.5 trong khi đáy thật là 4680.8 — luật vi phạm: L3 (biên phụ = cực trị XA NHẤT)
- **Thuật toán gắn:** biên phụ dưới = 4714.5 (điểm Spring thất bại 14:33).
- **Đúng phải là:** 4680.8. Sai **33.7 giá**, gần gấp đôi chiều cao biên chính.
- **Dấu hiệu quyết định trên chart:** nét đứt "bien phu duoi 4714.5" bị hàng chục nến xuyên qua bên dưới — nhìn bằng mắt là thấy ngay.
- **Nghi phạm trong thuật toán:** cùng gốc với lỗi 1 — việc nới biên phụ chỉ chạy trong nhánh Phase B (mục 5), không chạy khi đang ở Phase C. Phải nới biên phụ **ở mọi state**.

### 3. SOW dán lên nến 4 lot, không bứt được cả biên phụ — luật vi phạm: L3 (SOS/SOW phải đóng cửa bứt biên PHỤ) + THEORY §2.2 Effort vs Result
- **Thuật toán gắn:** SOW tại 4721.0, 17:46. Nến đó: O4721.4 H4721.4 L4721.0 C4721.0, **volume 4 lot, VSA 0.56x**.
- **Đúng phải là:** không có SOW ở đây. 4721.0 vẫn **cao hơn** biên phụ 4714.5 (chưa nói tới đáy thật 4680.8), và nỗ lực bằng 0.56x TB — đúng nghĩa "no supply", ngược hẳn định nghĩa SOW ("spread + volume tăng").
- **Dấu hiệu quyết định trên chart:** nhãn SOW nằm phía trên nét đứt biên phụ, panel volume tại đó gần như phẳng.
- **Nghi phạm trong thuật toán:** ngưỡng phá thật (3 nến đóng cửa vượt biên phụ ≥30 tick, thân ≥45%) đã đúng về hình thức, nhưng vì biên phụ bị ghi sai (lỗi 2) nên hàng rào tụt xuống mức vô nghĩa. Ngoài ra không có sàn VSA/khối lượng cho SOS/SOW.

### 4. Tên range ngược với kết cục thật — luật vi phạm: L4 (tên theo hướng phá THẬT)
- **Thuật toán gắn:** Tái phân phối (phá xuống).
- **Đúng phải là:** trong 60 nến sau khi range đóng, giá đi **lên** tới 4761.4, đóng cửa 4756.3 — cao hơn cả biên chính trên 4744.4. Cấu trúc thật: cú sụp 4680.8 là Spring/Shakeout ở đáy (một SOW thất bại), sau đó giá gom lại và phá LÊN → đây là **Tích luỹ** (hoặc chính xác hơn: cấu trúc phân phối **thất bại** theo THEORY §9).
- **Dấu hiệu quyết định trên chart:** cả góc phải chart là một chuỗi nến xanh leo dốc từ 4711 lên 4760.
- **Nghi phạm trong thuật toán:** tên được chốt tại nến SOW giả (lỗi 3). Sửa lỗi 1–3 thì tên tự đúng.

### 5. ST[A] có VSA 4.71x — lớn gần gấp đôi cây climax — luật vi phạm: THEORY §3.3 (ST: spread/volume phải GIẢM)
- **Thuật toán gắn:** ST[A] tại 4719.1 (14:00), VSA **4.71x**; climax SC 4726.5 chỉ 2.60x.
- **Đúng phải là:** một cú test phải co lại. Nến 4.71x phá xuống dưới climax 7.4 giá không phải test mà là **bán tiếp** — bằng chứng nữa cho thấy đợt giảm chưa dừng, tức Phase A chưa xong.
- **Dấu hiệu quyết định trên chart:** thanh volume vàng cao nhất nửa trái chart nằm đúng tại ST[A].
- **Nghi phạm trong thuật toán:** mục 4.2 chỉ kiểm "hồi ≥40% chiều cao" + "5 nến không cực trị mới", **không kiểm volume co lại**. Nên thêm điều kiện VSA(ST[A]) < VSA(climax).

### 6. Chọn sai nến climax ngay từ đầu — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** SC = nến 13:15, VSA 2.60x (17 lot).
- **Đúng phải là:** nến liền trước 13:14 có **6.27x (37 lot)** và nến liền sau 13:16 có **6.34x (59 lot)** — cả hai mạnh gấp 2.4 lần nến được chọn, và 13:16 mới là nến tạo đáy 4722.5. Máy chọn cây yếu nhất trong cụm 3 nến.
- **Nghi phạm trong thuật toán:** điều kiện mở range xét từng nến độc lập rồi lấy nến **đầu tiên** thoả (biên độ ≥1.4× TB, VSA ≥2.2x). Nên lấy nến **VSA/biên độ lớn nhất trong cụm** làm climax.

## Đạt
- MOVE trước climax đo đúng và thật: 28.2 giá / 22 nến / hiệu suất 0.63 — thoả điều kiện CẦN của L1.
- AR 4744.4 hồi 63% độ dài move → là cú bật ngược thật, thoả L3/mục 4.1.
- Phase A 46 nến, gọn, không kéo dài — khác hẳn bài #11.
- LPS[C] chỉ 1 điểm, đúng L7.

## Cần hỏi người học
- Ca này giá phá **xuống rất sâu rồi phá LÊN**. Anh muốn tính đây là **một range đổi tên thành Tích luỹ**, hay **hai range nối nhau** (range phân phối thất bại → range tích luỹ mới bắt đầu từ đáy 4680.8)? Hiện thuật toán chỉ theo dõi một range một lúc nên không thể diễn tả cách thứ hai.
