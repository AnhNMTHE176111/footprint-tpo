# Chấm bài #39 — Tích lũy (ACC) · 2026-07-12 22:48 → 07-13 00:34 (105 nến M1)

**Điểm: 5/10** — sửa vài nhãn, và phải xét lại chuyện MOVE bắc qua khe cuối tuần. Cây climax là cây tốt nhất cả lô (VSA 7.19×), nhưng "MOVE 41.6 giá" mà nó chặn thì nằm **bên kia phiên nghỉ cuối tuần** — không phải một move liền mạch.

## Lỗi (nặng → nhẹ)

### 1. MOVE trước climax bắc qua khe cuối tuần — luật vi phạm: L1 (điều kiện CẦN), quyết định 5 của người học
- **Thuật toán gắn:** MOVE dài 41.6 giá, **49 nến**, hiệu suất 0.45, chân move ở 4118+ lúc ~07-10 20:52.
- **Đúng phải là:** đọc trục thời gian trên ảnh: nhãn đi **07-10 20:52 → 07-12 22:10**. Giữa hai mốc đó là **hơn 49 giờ lịch** không có nến. Đường xám "chân MOVE" trên ảnh nối thẳng từ đỉnh thứ Sáu sang đáy Chủ Nhật — nó đo một **khe giá**, không đo một đợt bán. Người học đã chốt "khe > 4 giờ thì **cắt range**" (quyết định 5, v5); luật đó đang được áp cho range nhưng **không áp cho phép đo MOVE**.
- **Dấu hiệu quyết định trên chart:** trục x của ảnh nhảy từ `07-10 20:52` sang `07-12 22:10` mà chỉ cách nhau một khoảng pixel như các mốc khác. Move 41.6 giá trong 49 nến = 0.85 giá/nến, nhưng phần lớn độ dài đó là gap cuối tuần chứ không do 49 nến kia tạo ra.
- **Nghi phạm trong thuật toán:** hàm đo MOVE nhìn lại **240 nến theo index**, không theo **thời gian lịch**. Cùng loại lỗi K của v4 (đã vá cho range) nhưng chưa vá cho MOVE. Phải áp cùng luật: gặp khe > 4 giờ thì cắt cửa sổ nhìn lại tại đó.

### 2. Biên chính 12.0 giá nhưng nửa dưới bị xuyên liên tục — luật vi phạm: L3
- **Thuật toán gắn:** biên chính 4076.8–4088.8 = 12.0 giá; ST[A] tại **4075.8**, tức **dưới** mức climax 4076.8; biên phụ dưới 4075.8.
- **Đúng phải là:** giống lỗi ở bài #38 — ST[A] mà đóng thấp hơn mức climax thì cú "test lại vùng climax" đã biến thành cú phá nhẹ. Ở đây độ vượt chỉ 1.0 giá (8% chiều cao) nên còn chấp nhận được, nhưng nó cho thấy AR 4088.8 được chốt chỉ **4 nến** sau climax (22:48 → 22:52) trên một nến **VSA 0.36×**. Một biên chính quan trọng không nên sinh ra từ một nến volume bằng 1/3 trung bình.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu — AR tại 22:52 có VSA **0.36×**, thân 0.90, và chỉ cách climax 4 nến. Chính spec có nhãn "AR (yếu)" cho AR rơi vào 1–2 nến sát climax; 4 nến thì lọt.
- **Nghi phạm trong thuật toán:** mục 4.1 — AR = swing pivot đầu tiên xác nhận (5 nến + 1.5× biên độ TB). Không có điều kiện nào về **khối lượng tại cây AR**. Nên thêm: AR không được rơi vào nến VSA < ~0.5× (cú bật không có ai tham gia thì không tạo được biên).

### 3. LPS[C] 4088.0 gán ngay dưới biên trên — sai vai, đó là đỉnh chứ không phải điểm hỗ trợ — luật vi phạm: L8, mục 3.3 THEORY (định nghĩa LPS)
- **Thuật toán gắn:** LPS[C] tại 23:56, giá **4088.0** — cách biên chính **trên** (4088.8) đúng 0.8 giá, tức nằm ở **99% chiều cao range**.
- **Đúng phải là:** LPS = "Last Point of Support" — nhịp **thoái lui** trước khi bứt lên, phải nằm ở nửa dưới hoặc ít nhất là dưới biên trên một khoảng đáng kể. Ở 4088.0 nó nằm sát nóc range, sau khi mSOS 4091.4 đã vượt biên trên. Cái ở đây đúng hơn là **nhịp hồi sau mSOS thất bại**, và nếu phải gọi Phase C thì điểm test thật là nhịp lùi về **~4083** ngay trước cú SOS (nhìn ảnh: có một nhịp đỏ lùi xuống trước cụm nến xanh bứt lên).
- **Dấu hiệu quyết định trên chart:** LPS[C] 4088.0 vs biên chính trên 4088.8 — chênh 0.8 giá trên range 12.0 giá. VSA 0.64×, thân 0.10 (nến doji). Trên ảnh, chấm LPS[C] nằm **trên** đường cam nét liền dưới tới 11 giá và sát đường cam trên.
- **Nghi phạm trong thuật toán:** "gán ngược Phase C, nhìn lại 60 nến lấy **đáy sâu nhất** nếu phá lên". Nhưng 60 nến trước SOS (00:09) là đoạn 23:09–00:09, trong đó giá đã leo lên nửa trên range — đáy sâu nhất của **đoạn đó** là 4088.0, không phải đáy của range. Lỗi này là hệ quả trực tiếp của việc dùng cực trị trong cửa sổ cố định thay vì tìm pivot.

### 4. SOS 4096.8 đúng cây nhưng LPS[D] rơi vào 4088.2 = trong range — luật vi phạm: L10
- **Thuật toán gắn:** SOS 00:09 giá 4096.8 (VSA 1.79×, thân 0.48) → LPS[D] 00:18 giá **4088.2**.
- **Đúng phải là:** CBR (L10) yêu cầu nhịp retest **giữ được ở NGOÀI biên**. LPS[D] 4088.2 nằm **dưới** biên chính trên 4088.8 — tức giá đã lùi vào **trong** range. Theo mục 7 câu 1 của chính spec ("một nến đóng cửa lùi hẳn vào trong range quá 30 tick → cú phá hỏng"), 0.6 giá = 6 tick nên chưa đủ hỏng, nhưng nó cũng có nghĩa cú retest **không giữ được ngoài biên** → không đủ tư cách LPS[D] theo L10.
- **Dấu hiệu quyết định trên chart:** LPS[D] 4088.2 < biên chính trên 4088.8. Và nhìn tiếp bên phải ảnh: sau Phase E (1 nến) giá **rơi thẳng xuống 4070** lúc 00:35 — thấp hơn cả biên chính dưới. Cú "phá lên" này hỏng ngay sau đó.
- **Nghi phạm trong thuật toán:** dung sai gom LPS[D] là **20 tick quanh biên vừa phá** (mục 11) — dung sai đó cho phép LPS[D] nằm cả hai phía biên. Phải bắt LPS[D] nằm **ngoài** biên (phía cú phá), không được nằm trong.

### 5. Phase E dài 1 nến, và range đóng ngay trước khi cú phá bị phủ định — luật vi phạm: L10
- **Thuật toán gắn:** Phase E = 00:34 → 00:34 = **1 nến**.
- **Đúng phải là:** L10 nói Phase E là "giá thuận lực đi tiếp để tìm vùng giá mới". Một nến không phải Phase E. Lỗi J của v4 (Phase E luôn 1 nến) **vẫn còn ở bài này** — ở bài #36 và #38 đã hết (121 và 11 nến), nên đây là nhánh "hết 25 nến mà mới đi được ≥50% thì vẫn cho chốt Phase E" đang tạo ra Phase E 1 nến.
- **Dấu hiệu quyết định trên chart:** bảng phase — E bắt đầu và kết thúc cùng nến 00:34. Ngay sau đó giá đổ về 4070.
- **Nghi phạm trong thuật toán:** mục 7 — khi mốc "đi thêm 1.0× chiều cao range" đạt đúng tại nến cuối cửa sổ, Phase E bị chốt tại chính nến đó với độ dài 1. Nên: Phase E phải kéo tới khi giá lùi vào biên / đi xa 2× / hết 120 nến (đúng như spec đã ghi cho các ca khác) — nhánh này chưa áp đồng nhất.

## Đạt
- Cây climax tốt nhất cả lô: SC 22:48 VSA **7.19×**, biên độ **7.9 giá**, volume 359 so với TB ~35 — không thể tranh cãi đây là cao trào bán. Đúng L1.
- Climax đúng là cực trị chặn move: nến +1 bật ngay 4082.4 → 4087.1 với VSA 2.43×. Climax chặn được move, không nằm giữa move.
- Tên ACC khớp L4 (origin SC, phá lên).
- Phase B (50n) dài nhất, Phase C (13n) ngắn hơn D (25n) và B — đúng L8/L9.
- mSOS 4091.4 (vượt biên trên 2.6 giá, VSA 1.08×) được để lại **Phase B** thay vì gọi SOS — đúng: nó không đóng cửa bứt qua được, đúng ý L3 + lỗi H v4.
- Bỏ ST[B], mỗi bên 1 biên phụ — đúng L3, L6.
- LPS[C]/LPS[D] tách vai trước/sau SOS, mỗi cái 1 điểm — đúng L7.

## Cần hỏi người học
- Move bắc qua khe cuối tuần: cắt cửa sổ nhìn lại tại khe (bài này sẽ **không mở range**, vì move còn lại trong ngày 07-12 chỉ khoảng 10-12 giá), hay vẫn tính move qua gap? Tôi nghiêng về cắt, đồng nhất với quyết định 5.
