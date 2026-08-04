# Chấm bài #24 — Tái phân phối (RE-DIST) · 2026-06-04 14:53 → 06-05 13:37 (1304 nến M1)

**Điểm: 3/10** — cú phá xuống là thật và tên range đúng, nhưng biên chính vẽ sai chỗ (chỉ bao đoạn đầu), SOW dán muộn và Phase B nuốt trọn một chu kỳ giá độc lập.

## Lỗi (nặng → nhẹ)

### 1. Biên chính chỉ mô tả 3 tiếng đầu, 19 tiếng sau giá sống hẳn dưới nó — luật vi phạm: L3 + L1
- **Thuật toán gắn:** biên chính 4483.8–4502.4 (18.6 giá); biên phụ 4454.8–4513.0 (58.2 giá) = **3.1 lần** biên chính.
- **Đúng phải là:** nhìn ảnh rất rõ — biên chính (hai đường cam liền) chỉ đúng cho đoạn 14:53 → 22:20 ngày 04/06. Từ 00:20 ngày 05/06, giá **đóng cửa hẳn dưới 4483.8** và ở đó liên tục **hơn 6 tiếng** (vùng 4460–4480), rồi mới bò lại lên. Theo L5, "đóng cửa hẳn ngoài biên và các nến sau đủ mạnh giữ nó ở ngoài → đó là phá THẬT". Vậy SOW thật đã xảy ra khoảng 00:20–06:18 ngày 05/06, không phải 13:02.
- **Dấu hiệu quyết định trên chart:** mSOW được gán tại 06:18 ngày 05/06 ở giá 4454.8 — nhưng đó là **cuối** một đợt giảm đã kéo 6 tiếng, không phải một cú thọc rồi rút. Gọi nó là "cú phá thất bại" chỉ vì sau đó giá hồi về range là đọc sai: giá hồi về **sau 6 tiếng ở ngoài** thì đợt đó đã là một SOW hoàn chỉnh + một nhịp retest.
- **Nghi phạm trong thuật toán:** điều kiện Kết cục B (mục 5.1) — "3 nến liên tiếp đóng cửa vượt **biên phụ** thêm ≥ 30 tick". Biên phụ dưới lúc đó đã bị mSOS/mSOW trước đó đẩy ra, nên cú phá thật ở biên **chính** không đủ điều kiện. Điều kiện dự phòng "ở ngoài quá 40 nến và ≥60% nến đóng ngoài biên" cũng lẽ ra phải bắn ở đây (hơn 360 nến ngoài biên) — **cần kiểm xem nhánh này có thật sự chạy khi giá ở ngoài biên CHÍNH nhưng trong biên PHỤ hay không**. Nghi là điều kiện chỉ đo với biên phụ.

### 2. SOW dán tại 4438.8 — dưới biên chính 45 giá, tức 2.4 lần chiều cao range — luật vi phạm: L10 + mục 8
- **Thuật toán gắn:** SOW tại 13:02 ngày 05/06, giá 4438.8, VSA **1.36×**, thân 0.51.
- **Đúng phải là:** nhìn panel volume, cụm nến vàng cao nhất cả range nằm ở **12:20–12:50** ngày 05/06 (rõ ràng trên ảnh: nhóm thanh vàng cao vọt sát mép phải). Đó là cây phá thật, ở khoảng giá 4480–4470. Đến 4438.8 thì đợt bán đã đi 2.4× chiều cao range — Phase E, không phải mốc D.
- **Dấu hiệu quyết định trên chart:** VSA 1.36× cho nhãn SOW trong khi cùng đoạn có nến VSA > 3× ngay trước đó. Lỗi B **chưa vá hết**.
- **Nghi phạm trong thuật toán:** cùng nghi phạm với bài #23 — cửa sổ hồi tố nhãn bị neo vào "vượt biên phụ" (4454.8), nên nó chỉ tìm cây phá **dưới** 4454.8, bỏ qua toàn bộ cụm nổ volume ở 4480–4470.

### 3. Phase B 1228 nến nuốt trọn một chu kỳ giảm-hồi hoàn chỉnh — luật vi phạm: L9 (lạm dụng) + mục 13.3
- **Thuật toán gắn:** A=25, B=**1228** (94%), C=16, D=19, E=17.
- **Đúng phải là:** trong 1228 nến đó giá đi 4502 → 4455 → 4500, tức một đợt giảm 47 giá và một đợt hồi 45 giá — mỗi đợt đủ tư cách mở range riêng. Gộp cả vào "Phase B" của một range 18.6 giá là mô tả sai bản chất.
- **Dấu hiệu quyết định trên chart:** đoạn 00:20 → 06:20 ngày 05/06 trên ảnh là một vùng đi ngang **riêng biệt** ở 4460–4480, có biên trên/biên dưới của chính nó, hoàn toàn ngoài biên chính của range đang vẽ.

### 4. ST[A] neo tại 4499.2 — cách biên chính trên chỉ 3.2 giá, không phải test lại vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 15:17, giá **4499.2** (AR ở 4502.4, climax ở 4483.8). ST[A] nằm ở **83%** chiều cao range, tính từ climax.
- **Đúng phải là:** ST[A] là lần thứ 3 đổi hướng, giá **quay về phía climax** rồi bị chặn — nó phải nằm ở nửa **dưới** range (THEORY §5: ST ở 1/3 nửa dưới = lực bán nhất định; ở nửa trên = phe mua rất mạnh, nhưng vẫn phải là một nhịp hồi *về phía climax*). Ngọ nguậy 3.2 giá dưới AR sau khi vừa lên AR không phải một lần đổi hướng — đó là cùng một nhịp tăng.
- **Dấu hiệu quyết định trên chart:** VSA nến ST[A] = **0.38×**, thân 0.31. Cây rỗng. Và trên ảnh nhãn ST[A] nằm cao hơn cả nhãn AR — trực quan sai ngay.
- **Nghi phạm trong thuật toán:** mục 4.2 bỏ hết ngưỡng % theo yêu cầu người học ("đo bằng cấu trúc") và chỉ giữ "swing pivot 5 nến + nhịp ≥ 1.5× biên độ TB". Với biên độ TB nhỏ, 3.2 giá đã qua ngưỡng nhiễu → bắt pivot quá sớm. Cần thêm gate **định tính** (không phải %): ST[A] phải nằm **cùng phía climax so với trung điểm** biên chính. Đây là điều kiện cấu trúc, không phải ngưỡng %, nên không xung đột với quyết định của người học.

### 5. LPSY[C] 4475.7 nằm dưới biên chính dưới 8 giá — luật vi phạm: L8 (nhẹ)
- **Thuật toán gắn:** LPSY[C] tại 12:46, 4475.7, VSA 0.46×.
- **Đúng phải là:** LPSY là nhịp phục hồi yếu **tại vùng kháng cự** — phải sát biên bị mất (4483.8) hoặc cao hơn. Ở đây điểm được chọn đã nằm hẳn trong vùng phá. Cùng lỗi cơ chế "gán ngược 60 nến" như bài #21/#22.

## Đạt
- MOVE trước climax rất rõ: **50.6 giá / 68 nến / hiệu suất 0.46** — đây là một đợt giảm thật, đúng chất điều kiện CẦN của L1.
- Climax là đáy của cửa sổ (4483.8 thấp nhất bảng 12 nến), VSA 2.31×, biên độ 8.7 giá, volume 800 hợp đồng — climax thanh khoản thật, không phải nhiễu phiên Á.
- Phase A đủ 3 lần đổi hướng và kết thúc đúng tại ST[A] (dù ST[A] chọn sai chỗ, cấu trúc 3 nhịp thì có).
- **Tên range đúng (L4):** origin SC + phá xuống thật = Tái phân phối. Cú phá này là **thật** — giá đi từ 4483 xuống 4375 và không quay lại. Đây là điểm mạnh nhất của bài: v4 hay đặt tên cho cú phá đã hỏng, ở đây tên đúng.
- Biên phụ mỗi bên đúng 1 cái, là cực trị xa nhất. Không spam nhãn, không có ST[B]. L6 đạt.
- LPSY[D] một điểm duy nhất (L7 đạt).
- mSOS/mSOW ở Phase B gán đúng loại (cú phá thất bại, không hạ thành "test nhẹ") — **lỗi H đã hết**.
