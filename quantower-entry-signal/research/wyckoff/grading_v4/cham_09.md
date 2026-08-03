# Chấm bài #09 — Tái phân phối (RE-DIST) · 2026-05-01 06:19 → 2026-05-04 08:36 (690 nến M1)

**Điểm: 3/10** — Vùng cân bằng 4642-4707 là **thật**, nhưng mọi mốc neo đều sai: "SC" 6 hợp đồng không chặn được move (giá xuống thấp hơn nó 36 giá ngay sau đó), AR bỏ rơi, ST[A] rơi đúng giữa range, và **3 lần gọi Spring cho những đáy không phải đáy thấp nhất TR** — đúng lỗi bị giảng viên sửa nhiều nhất trong cả bộ tài liệu. Giữ range, xoá sạch nhãn Phase A và Phase C, vẽ lại.

## Lỗi (nặng → nhẹ)

### 1. Ba nhãn Spring đều sai — Spring phải là giá THẤP NHẤT của cả TR — luật vi phạm: CHART_CASES Ca #19 nguồn 2.pdf (lỗi lặp nhiều nhất, 4/22 ca), L5
- **Thuật toán gắn:** Spring (thất bại) ×3 tại **4639.6** (05-04 01:30), **4639.3** (02:32), **4636.9** (06:07).
- **Đúng phải là:** cả ba là **LPS[C]/test biên dưới**, không phải Spring. Giảng viên phát biểu tường minh ở Ca #19: *"Spring phải có giá thấp nhất trong suốt TR"* — và nhắc lại ở Ca #4, #16, #20 cùng nguồn.
- **Dấu hiệu quyết định trên chart:** giá thấp nhất của TR là **4605.6** (chính là biên phụ dưới thuật toán tự vẽ, nét đứt cam ở đáy ảnh). Ba "Spring" nằm cao hơn mức đó **31.3 / 32.0 / 34.0 giá** — chúng còn chưa xuống nổi nửa đường. Trên ảnh thấy rõ: ba nhãn Spring dính chùm quanh nét liền 4642.0, còn nét đứt 4605.6 nằm cách xa bên dưới.
- **Nghi phạm trong thuật toán:** mục 10 tài liệu thuật toán ghi thẳng *"Cách đo một cú Spring cho đúng: đo với **nét liền** (biên chính), không phải nét đứt"*. Chính câu đó gây ra lỗi — nó **trái** với luật giảng viên. Phải đo Spring bằng **cực trị thấp nhất của TR** (tức biên phụ nếu có), giống như L3 đã yêu cầu cho SOS/SOW ("phải đóng cửa bứt qua biên PHỤ"). Đối xứng hai chiều.

### 2. Climax không chặn move — biên chính dưới nằm giữa vùng giá — luật vi phạm: L1, L3
- **Thuật toán gắn:** SC 05-01 06:19 đáy **4642.0**, VSA 2.45x → biên CHÍNH dưới.
- **Đúng phải là:** SC thật ở vùng **4605.6** (đáy 05-01 sáng). Cây 06:19 không chặn được gì.
- **Dấu hiệu quyết định trên chart:** ngay sau "SC", giá rơi tiếp và dành khoảng **5 giờ** (05-01 07:00 → 12:00) ở dưới mức 4642.0, sâu nhất **36.4 giá** = 55% chiều cao range. Trên ảnh, nét liền cam dưới đi xuyên giữa đám nến, dưới nó là cả một khối giá. Đây là ca nặng nhất trong 5 bài về lỗi này.
- **Nghi phạm trong thuật toán:** điều kiện (2) mục 3 chỉ kiểm cực trị trong **cửa sổ 240 nến nhìn lại**, không kiểm phía trước. Cùng lỗi ở #06, #07, #08.

### 3. "Climax" chỉ 6 hợp đồng — luật vi phạm: mục 8 Effort vs Result, THEORY §2.2
- **Thuật toán gắn:** SC với VSA 2.45x, biên độ 3.0 giá.
- **Đúng phải là:** không mở range ở đây. Khối lượng nến là **6 hợp đồng**, TB 20 nến ≈ **2.45 hợp đồng** (6 ÷ 2.45). Sáu nến trước climax có khối lượng **2, 1, 1, 1, 1, 3** và năm nến trong đó là nến chết (O=H=L=C).
- **Dấu hiệu quyết định trên chart:** panel khối lượng nửa trái ảnh gần như phẳng; các cột vàng thật sự chỉ xuất hiện từ 05-01 13:08 trở đi. Cao trào bán bằng 6 hợp đồng là không có cao trào.
- **Nghi phạm trong thuật toán:** VSA thuần tương đối, cần sàn khối lượng tuyệt đối (giống ghi nhận ở bài #07).

### 4. Nhãn AR bỏ rơi, lệch 53.6 giá so với biên chính trên — luật vi phạm: L2, L3
- **Thuật toán gắn:** AR 05-01 13:44 giá **4654.1**, VSA **0.46x**, thân 0.00; biên CHÍNH trên **4707.7**.
- **Đúng phải là:** AR = đỉnh cú bật ngược = **4707.7** (05-01 ~14:00, chỗ có cột khối lượng lớn trên ảnh). Cây 4654.1 là một nến doji giữa đường đi lên, khối lượng bằng nửa trung bình.
- **Dấu hiệu quyết định trên chart:** nhãn AR và biên chính trên lệch **53.6 giá** = 82% chiều cao range. Theo L3 biên chính = climax + AR ⇒ hai con số không thể cùng đúng. Trên ảnh, chấm AR nằm lọt giữa đoạn nến tăng dốc, còn nét liền cam trên nằm cao hơn hẳn.
- **Nghi phạm trong thuật toán:** cửa sổ AR cố định 40 nến + không dời nhãn AR khi biên nới (mục 4.2 spec yêu cầu dời nhưng code không làm). Lỗi hệ thống, lặp ở #06, #07, #09 — sửa một chỗ được cả ba.

### 5. ST[A] rơi đúng giữa range, không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 05-01 14:50 giá **4674.9**.
- **Đúng phải là:** ST[A] phải là cú quay lại **test vùng climax** rồi bị chặn lần nữa (lần đổi hướng thứ 3 của CHoCH).
- **Dấu hiệu quyết định trên chart:** trung điểm range = (4642.0 + 4707.7) / 2 = **4674.85**. ST[A] = 4674.9, tức đúng **50.0%** range — không thể nào là test biên. Đây chính là ca "một cái ngọ nguậy giữa range" mà mục chấm số 2 cảnh báo.
- **Nghi phạm trong thuật toán:** ST[A] chỉ cần "hồi ≥ 40% chiều cao climax↔AR" rồi 5 nến không tạo cực trị mới (mục 4.2). Ngưỡng 40% cho phép ST[A] đứng giữa range. Nên siết: ST[A] phải nằm trong 1/3 range về phía climax (khớp THEORY §5 — vị trí ST trong 3 phần của range mới cho biết ai đang kiểm soát).

### 6. SOW không bứt qua biên phụ — luật vi phạm: L3
- **Thuật toán gắn:** SOW 05-04 07:59 giá **4624.2**, VSA 2.70x, thân 1.00.
- **Đúng phải là:** L3 nói rõ "SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua biên **PHỤ**". Biên phụ dưới là **4605.6**; SOW đóng ở 4624.2, tức còn **18.6 giá** phía trên nó. Vậy đây chỉ là mSOW (phá biên chính), chưa phải SOW mạnh.
- **Dấu hiệu quyết định trên chart:** chấm SOW nằm rõ **trên** nét đứt 4605.6. Giá chỉ thực sự phá 4605.6 sau khi range đã đóng (đoạn rơi thẳng xuống 4571 ở mép phải ảnh).
- **Nghi phạm trong thuật toán:** điều kiện phá THẬT ở mục 5.1 ghi là "vượt **biên phụ** thêm ≥ 30 tick", nhưng kết quả cho thấy code đang so với **biên chính** — lỗi parity giữa spec và code, kiểm lại chỗ chọn biên trong nhánh xác nhận SOS/SOW.

### 7. Spam nhãn và Phase B 1-2 nến — luật vi phạm: L3 (mỗi bên 1 biên phụ / cú nông hơn không ghi), L7
- **Thuật toán gắn:** chuỗi phase C(27) → B(**1**) → C(60) → B(**2**) → C(6) → B(42) → D(26), kèm 3 Spring + 2 LPS[C] dồn trong khoảng 4636-4640.
- **Đúng phải là:** ba cú thăm dò cách nhau **≤ 2.7 giá** là **một vùng test duy nhất**, không phải ba sự kiện. Tinh thần L3 ("cú thăm dò mới nông hơn cú cũ thì không ghi gì cả") và L7 (LPS chỉ 1 điểm) đều chống lại việc này. Giảng viên xử ca tương tự bằng cách gom thành 1 vùng hoặc lấy lần cuối (Ca #5, #11, #20 nguồn 7.pdf).
- **Dấu hiệu quyết định trên chart:** góc phải ảnh có 6 nhãn chồng lên nhau đến mức che nhau, và hai dải "Phase B (1n)", "Phase B (2n)" — một phase dài 1 nến là vô nghĩa về mặt cấu trúc.
- **Nghi phạm trong thuật toán:** vòng lui B⇄C (mục 5, "Phase B ⇄ C có thể quay lui") không có điều kiện chống lặp theo **mức giá**. Đề xuất: cú rũ mới chỉ được ghi nếu vượt cú rũ cũ (thấp hơn với Spring), y hệt quy tắc biên phụ.

## Đạt
- **Range này có thật (mục 1):** 690 nến, biên chính 65.7 giá (1.41%), và trên ảnh giá thật sự dao động hai chiều trong vùng 4642-4707 suốt 05-01 tới 05-04 rồi mới phá xuống. Đây là điểm mạnh nhất của bài — khác hẳn bài #08.
- **Có MOVE thật trước climax:** 40.3 giá / 75 nến / hiệu suất 0.38, mũi xám là một đoạn giảm liền mạch.
- **Tên range đúng (L4):** origin SC + phá thật xuống = Tái phân phối; khớp bối cảnh giá vàng đang xuống.
- **Tỉ lệ Phase B/C đúng chiều (L9):** tổng B = 307 nến (dài nhất), tổng C = 93 nến.
- **SOW có nỗ lực (mục 8):** VSA **2.70x**, thân **1.00** — cây phá biên đúng chất, chỉ tiếc là chưa qua biên phụ (lỗi #6).
- **Ba cú rũ được đánh dấu "thất bại" và tô xám, không bị nhận là xác nhận** — cơ chế theo dõi kết cục cú rũ hoạt động đúng, chỉ sai ở chỗ chọn tên và chọn mức.
- **Không có ST[B] (L6).**

## Cần hỏi người học
- Chốt lại giúp: **đo Spring bằng biên nào?** Mục 10 tài liệu thuật toán đang ghi "đo với nét liền (biên chính)", còn giảng viên trong CHART_CASES Ca #19 đòi Spring phải là **giá thấp nhất toàn TR** (tức phải qua biên phụ). Hai cái xung đột trực tiếp; em đang chấm theo giảng viên. Nếu anh muốn giữ cách đo theo biên chính thì phải sửa câu trong CHART_CASES-standard, không thể để cả hai.
- Nhãn ở biên dưới của range **tái phân phối**: bài #08 (cùng origin SC, cùng RE-DIST) gọi **LPSY[C]**, bài #09 gọi **LPS[C]**. Muốn thống nhất theo origin (SC ⇒ LPS) hay theo tên range cuối cùng (RE-DIST ⇒ LPSY)?
