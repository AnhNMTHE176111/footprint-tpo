# Chấm bài #47 — Chưa rõ (SC) (ACC?) · 2026-07-27 12:23 → 15:56 (213 nến M1)

**Điểm: 2/10** — **không nên vẽ range ở đây theo cách này.** Climax không phải cây climax, biên chính
7.5 giá nằm lọt giữa một vùng 24.7 giá, và bài có nhãn LPS[C] trong khi timeline không có Phase C.

## Việc để ngỏ tên "Chưa rõ" — đúng thủ tục, nhưng ở bài này nó che một lỗi nặng hơn

Giống bài #46, để ngỏ tên là đúng nguyên tắc L4. Nhưng ở bài #47 range vẫn đang "[active]" nên chưa
rõ là **bắt buộc**, không phải một quyết định. Điểm cần chấm không phải là "để ngỏ đúng hay sai" mà
là: cái range này lẽ ra **không được mở**.

## Lỗi (nặng → nhẹ)

### 1. Cây SC có VSA 1.18× — không phải climax — luật vi phạm: L1 + THEORY §3.3 (SC), mục 3 nhóm (1) của chính thuật toán
- **Thuật toán gắn:** SC = nến 12:23, giá 4083.1, **VSA = 1.18×**, biên độ 4.0 giá, thân/biên 0.38.
- **Đúng phải là:** SC theo định nghĩa gốc là "chênh lệch biên độ mở rộng + khối lượng **tăng mạnh**".
  Cây 12:19 có VSA **4.08×** (432 volume) và đẩy giá 4088.4 → 4083.9; cây 12:20 có VSA **2.61×**. Đó
  là cụm cao trào bán thật. Cây 12:23 với VSA 1.18× là cây **sau** cao trào — nó đã ở trong pha lặng.
  Nếu phải chọn, SC = 12:19.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến quanh climax, cột VSA: 0.51 / 1.31 / **4.08** /
  **2.61** / 0.76 / 0.78 / **1.18 ← climax**. Máy bỏ qua cây 4.08× để chọn cây 1.18× cách đó 4 nến.
  Ngưỡng climax do chính tài liệu thuật toán đặt là **VSA ≥ 2.2×** — cây được chọn không đạt ngưỡng
  của chính nó.
- **Nghi phạm trong thuật toán:** luật "cụm climax" mục 4.0 — mốc climax được **dời** trong 8 nến đầu
  sang cực trị GIÁ mới cùng phía. Đáy thấp nhất của cụm là 4083.1 (nến 12:23) nên mốc bị dời tới đó và
  nhãn SC dời theo, **kéo cả VSA của climax rơi từ 4.08× xuống 1.18×**. Đây là cùng một lỗi với bài
  #45 (ở đó 2.20× → 1.79×), tức không phải ngẫu nhiên mà là lỗi hệ thống: **luật dời cụm climax phải
  giữ lại cây có VOLUME cao nhất trong cụm làm cây climax, chỉ dùng cực trị GIÁ để đặt MỨC biên.**
  Hai thứ đó phải tách ra: mức biên = cực trị giá của cụm; nhãn + VSA climax = cây volume lớn nhất
  của cụm.

### 2. Biên chính 7.5 giá (0.18%) trong khi biên phụ 24.7 giá — range gấp 3.3 lần biên của nó — luật vi phạm: L3, THEORY §3.1
- **Thuật toán gắn:** biên chính 4083.1 – 4090.6 = **7.5 giá (0.18%)**; biên phụ 4067.1 – 4091.8 =
  **24.7 giá**.
- **Đúng phải là:** biên chính phải là hai biên **quan trọng nhất** của vùng đấu giá. Ở đây chúng chỉ
  bao được **30%** biên độ mà giá thực sự đi. Đường liền dưới 4083.1 bị giá xuyên qua và ở dưới nó
  suốt **hơn nửa** thời gian range (từ 13:47 tới hết chart). Một biên bị giá sống ở phía ngoài trong
  nửa thời gian không còn là biên.
- **Dấu hiệu quyết định trên chart:** đọc ảnh — sau 13:47 toàn bộ nến nằm **dưới** đường liền cam
  4083.1, giá xuống tận 4067 rồi hồi về 4081, không một lần đóng lại trên 4083.1 cho tới cuối chart.
  Trong khi đó nhãn phase vẫn ghi "Phase B (203n)" chạy tới 15:56.
- **Nghi phạm trong thuật toán:** hai chỗ cộng dồn — (a) AR được nhận quá sớm và quá gần (mục 4.1:
  AR 12:27, chỉ **4 nến** sau climax, VSA **0.60×**, tức một nhịp nảy nhỏ trong nhiễu chứ không phải
  Automatic Rally); (b) không có hậu kiểm khi biên phụ vượt biên chính nhiều lần. Luật "AR (yếu)" ở
  mục 4.1 đã nhận diện được ca này (AR rơi vào 1–2 nến sát climax) nhưng theo tài liệu nó **chỉ là
  cảnh báo hiển thị, không đổi logic** — đó chính là chỗ cần đổi thành **loại bỏ ứng viên**.

### 3. Có nhãn LPS[C] nhưng timeline KHÔNG có Phase C — luật vi phạm: L8, và tự mâu thuẫn nội bộ
- **Thuật toán gắn:** bảng sự kiện ghi `LPS[C] · 13:56 · 4077.3 · Phase C`, nhưng bảng Phase chỉ có
  A (11 nến) và B (203 nến). `index.json` cũng chỉ liệt kê phases A và B.
- **Đúng phải là:** một nhãn `[C]` không thể tồn tại khi Phase C không tồn tại. Hoặc Phase C phải
  được ghi vào timeline, hoặc nhãn phải bị xoá cùng với đoạn C. Mục 6 của tài liệu thuật toán nói rõ
  khi shock thất bại thì "**đoạn Phase C bị xoá hẳn khỏi timeline**" — nhưng ở đây đoạn C bị xoá mà
  **nhãn LPS[C] còn nằm lại**. Vá nửa vời.
- **Dấu hiệu quyết định trên chart:** trên ảnh chỉ có 2 vạch dọc tím (A và B), nhưng nhãn LPS[C] màu
  xanh vẫn hiện ở 13:56. Người đọc chart không thể biết nó thuộc phase nào.
- **Nghi phạm trong thuật toán:** đường dọn dẹp khi shock/Phase C thất bại (lỗi C của v4) xoá đoạn
  phase nhưng không xoá/đổi tên các nhãn con đã sinh ra trong đoạn đó. Cần: khi xoá đoạn C, mọi nhãn
  `LPS[C]`/`LPSY[C]` sinh trong đoạn đó phải bị xoá luôn (chúng vô nghĩa nếu không có cú rũ để test lại).

### 4. LPS[C] gắn vào cây VSA 4.91× — sai bản chất "test" — luật vi phạm: THEORY §3.3 (LPS), §6.4
- **Thuật toán gắn:** LPS[C] tại 13:56, VSA **4.91×** — cây volume cao nhất cả range.
- **Đúng phải là:** LPS là "thoái lui với volume nguồn cung **giảm dần**", test là chỗ volume **co
  lại** (§6.4: volume nến test phải thấp hơn 2 nến liền trước). Một cây 4.91× không bao giờ là LPS —
  nó là cây **nỗ lực**, tức là một mSOW/SOW. Nhìn ảnh: cây đó là cây đỏ dài rơi từ 4088 xuống 4072,
  đúng nghĩa một cú xả.
- **Dấu hiệu quyết định trên chart:** thanh volume vàng cao nhất toàn bộ panel nằm đúng dưới nhãn
  LPS[C]. Nhãn "test nhẹ" đặt lên cây nỗ lực lớn nhất chart — đây là lỗi ngược dấu, không phải lệch
  vị trí.
- **Nghi phạm trong thuật toán:** mục 6 gán LPS[C] cho "nhịp test cuối cùng: đáy sâu nhất trong 60
  nến trước cú phá" — tiêu chí chỉ có GIÁ, không có điều kiện volume. Phải thêm: nhãn LPS/LPSY chỉ
  được gán cho nến có VSA **thấp** (≤ ~1.0×, hoặc thấp hơn 2 nến trước theo §6.4); cây VSA cao phải
  đi vào nhánh SOW/mSOW.

### 5. mSOW 13:32 — nhãn đúng loại nhưng đo bằng biên sai — luật vi phạm: L3
- **Thuật toán gắn:** mSOW 13:32, giá 4077.4, VSA 1.35×.
- **Đúng phải là:** so với biên chính dưới 4083.1 thì 4077.4 sâu 5.7 giá = **76%** chiều cao biên
  chính. Một cú thọc sâu bằng 3/4 cả range mà chỉ được gọi "cú phá thất bại" là dấu hiệu biên chính
  quá hẹp (lỗi #2), không phải lỗi của nhãn mSOW. Ghi nhận là hệ quả, không tính là lỗi độc lập.

## Đạt
- **Có MOVE thật trước climax (L1, phần move):** 23.1 giá / 73 nến, hiệu suất 0.37 — vượt ngưỡng 0.35
  nhưng chỉ vừa đủ; nhìn ảnh thì đúng là một đợt giảm rõ ràng từ 4106 xuống 4083. Phần này ĐẠT.
- **Để ngỏ tên range (L4)** — không đoán tên khi chưa phá. ĐẠT về thủ tục.
- **Không có nhãn ST[B]** (L6).
- **Phase A 11 nến — ngắn, đúng tinh thần** (Phase A không được dài hơn B). Về tỉ lệ thì đạt, dù nội
  dung sai (lỗi #2).
- **Biên phụ đúng số lượng: mỗi bên 1** (L3).

## Kết luận cấu trúc
Nếu là tôi thì **không vẽ range tại 12:23**. Cách đọc đúng đoạn này: cụm 12:19–12:23 là chỗ đợt giảm
bị chặn (một PS/SC tiềm năng), nhưng nhịp nảy sau đó chỉ **4 nến / 7.5 giá** — quá nhỏ để gọi là
Automatic Rally, tức Phase A **chưa hình thành**. Đúng ra phải chờ: đợi tới khi có một cú bật ngược đủ
lớn (ở đây là nhịp 13:32 → 13:47 lên 4091.8, biên độ ~14 giá) thì mới có cặp biên đáng gọi là biên, và
range thật nên là **4067 – 4092**. Với biên đó, cú rơi sau 13:47 xuống 4067 rồi hồi lại chính là hành
động đáng đọc, chứ không phải một "Phase B 203 nến" phẳng lặng.

## Cần hỏi người học
- Nhãn "AR (yếu)" (AR cách climax 1–4 nến, nhịp hồi nhỏ) hiện chỉ là cảnh báo hiển thị. Có nên nâng
  thành **điều kiện loại ứng viên** không? Ca này cho thấy một AR 4 nến / VSA 0.60× tạo ra một range
  0.18% và toàn bộ phần sau đọc sai theo.
