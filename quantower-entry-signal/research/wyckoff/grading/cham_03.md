# Chấm bài #03 — Phân phối (DIST) · 2026-01-21 06:34 → 2026-01-22 05:50 (127 nến M1)

**Điểm: 2/10** — vị trí range chấp nhận được nhưng phải vẽ lại từ đầu: cây mở range không phải cao trào, nhãn BCLX dán vào một cây **đỏ** giữa range, thiếu hẳn Phase C, và SOW neo trong vùng đã phá hụt.

## Lỗi (nặng → nhẹ)

### 1. Cây mở range không thoả CHÍNH điều kiện climax của thuật toán — luật vi phạm: mục 3(1) tài liệu thuật toán, THEORY §4.1
- **Thuật toán gắn:** "Climax mở range: BCLX tại giá 4989.4, **VSA = 0.85×**, **biên độ nến = 0.0 giá**" (nến 06:34, volume **2**, O=H=L=C=4989.4).
- **Đúng phải là:** biên chính trên phải neo vào một sự kiện có nỗ lực. Cây 06:34 là **một lần in giá duy nhất, 2 hợp đồng**, biên độ 0 — không đạt cả hai ngưỡng của chính thuật toán (VSA ≥ 2.2×, biên độ ≥ 1.4× TB). Đỉnh 4989.4 có thể vẫn là mức kháng cự hợp lệ, nhưng khi đó nó là một **đỉnh cạn kiệt** (THEORY §6.2), phải gọi khác và biên chính trên nên neo theo **giá đóng cửa** vùng đỉnh (~4985) chứ không theo một tick lẻ.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến — volume 1,2,4,1,11,2,**2**,2,10,**111**,1,3. Cây thật sự có nỗ lực là cây **+3 (06:57) với 111 hợp đồng, VSA 13.62×**.
- **Nghi phạm trong thuật toán:** cụm climax v5/v6 dời **mốc giá** sang cực trị của cụm nhưng không kiểm lại điều kiện climax trên nến đã dời tới. Phải: giữ nến đạt ngưỡng làm mốc, hoặc bắt nến cực trị **cũng** phải đạt ngưỡng, nếu không thì bỏ ứng viên.

### 2. Nhãn BCLX dán vào một cây GIẢM, nằm 27.8 giá trong lòng range — luật vi phạm: THEORY §4.1 (BCLX = "lực mua đạt đỉnh"), L3
- **Thuật toán gắn:** nhãn `BCLX` tại 06:57, giá **4961.6**, VSA 13.62×, thân 0.72. Nến đó là **O 4961.6 / H 4961.6 / L 4954.2 / C 4956.3** — một cây **đỏ**, đóng cửa gần đáy.
- **Đúng phải là:** cây 111 hợp đồng đó là **cây cung đầu tiên** — nó là nến khởi phát AR (phản ứng tự động), hoặc nếu muốn nhãn thì là **SOW nhỏ đầu tiên**. Gọi một cây bán tháo thân đỏ 0.72 là "cao trào **mua**" là lỗi khái niệm, cùng loại với Ca #9 và Ca #14 nguồn 7.pdf ("tại sao gắn SC trong tái tích luỹ") — dán nhãn ngược bối cảnh cung/cầu.
- **Dấu hiệu quyết định trên chart:** chấm BCLX nằm **dưới** chấm ST[A] và ở gần giữa khung range, cách biên chính trên 27.8 giá. Người đọc chart thấy "cao trào mua" không nằm ở đỉnh.
- **Nghi phạm trong thuật toán:** nhánh v6 "tách nhãn/mức climax" — nhãn lấy cây VSA cao nhất trong cụm **không kiểm màu nến/hướng**. Mục 3(3) của tài liệu đã yêu cầu "nến xanh chặn move tăng → BCLX"; điều kiện màu này bị bỏ khi chọn nhãn. Tối thiểu phải áp lại điều kiện màu + phải là cực trị phía climax.

### 3. Thiếu hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** dải phase chỉ có A(18) → B(70) → D(25) → E(15). Không có C.
- **Đúng phải là:** L8 case khó nói rõ — khi SOS/SOW bắn ra mà chưa từng có Phase C thì **nhìn ngược 60 nến lấy nhịp test cuối cùng làm LPSY[C]**. Ở đây SOW ở 21:00, trong 60 nến trước đó có nhịp hồi lên biên chính dưới 4941.5 sau khi mSOW (17:31) thất bại — đó chính là LPSY[C] và Phase C phải bắt đầu từ đó. Kịch bản này trùng khít Ca #10 nguồn 2.pdf: "sau khi Failed SOS chuyển thành UT[B] thì LPS[C] tiềm năng" — chỉ đổi chiều.
- **Dấu hiệu quyết định trên chart:** giữa mSOW (4916.4, 17:31) và SOW (21:00) có một nhịp giá bò lại lên sát 4941.5 rồi bị chặn — nhịp đó bị bỏ trắng, Phase B chạy thẳng sang Phase D.
- **Nghi phạm trong thuật toán:** nhánh "Phase C gán ngược" không chạy khi trước đó range đã có một **mSOW** ghi nhận (có lẽ bị coi là đã xử lý cú phá nên bỏ qua bước gán ngược), hoặc cửa sổ `min(60 nến, 1/2 độ dài Phase B)` = 35 nến không chứa nhịp test.

### 4. SOW neo cao hơn biên phụ dưới 12.1 giá — luật vi phạm: L3 ("SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua biên PHỤ")
- **Thuật toán gắn:** biên phụ dưới **4916.4** (do mSOW tạo lúc 17:31); nhãn `SOW` tại **4928.5** (21:00, VSA 5.00×, thân 0.77).
- **Đúng phải là:** SOW phải nằm ở cây đóng cửa **vượt qua 4916.4**. Cây 4928.5 vẫn ở trong vùng mà cú phá trước đã đi qua và **thất bại** — nó chưa chứng minh gì thêm. Nhãn phải dời xuống cây đóng cửa dưới 4916.4 đầu tiên có thân đủ, hoặc chốt SOW muộn hơn.
- **Dấu hiệu quyết định trên chart:** chấm SOW xanh nằm **rõ ràng phía trên** đường nét đứt "biên phụ dưới 4916.4".
- **Nghi phạm trong thuật toán:** vá lỗi B (đặt nhãn hồi tố vào cây VSA cao nhất trong đoạn) chạy trên **toàn đoạn phá**, không kẹp thêm điều kiện "cây được chọn phải đóng cửa ngoài biên phụ". Cần thêm bộ lọc đó vào bước hồi tố.

### 5. AR neo trên nến 1 hợp đồng, VSA 0.12× — luật vi phạm: mục 2 (AR phải là cú bật ngược thật)
- AR = 4941.5 tại 07:20, VSA **0.12×**, biên độ 0, volume 1. Cả biên chính dưới của range — mức quan trọng thứ hai của cấu trúc — đang treo trên một tick lẻ. Cấu trúc không sai (đáy phản ứng đúng vị trí), nhưng mức thì nên neo theo giá đóng cửa vùng đáy phản ứng, không theo một print.

### 6. Nhãn chồng nhau ở góc phải trên (trình bày)
- Chuỗi chữ `bien CHINH tren 4989.4` bị nhãn `Phase E` và chữ `4989.4` đè lên nhau, không đọc được. Lỗi trình bày, xếp cuối.

## Đạt
- **ST[A] đúng chuẩn:** 4985.9 (09:31) — chỉ 3.5 giá dưới mức climax 4989.4, VSA co còn 0.13×. Đây là test lại đúng vùng climax với volume/spread thu hẹp, khớp THEORY §3.3/§4.1. Phase A kết thúc đúng tại ST[A] (L2 ✓).
- **Tên range (L4):** origin BCLX + phá **xuống** thật = **Phân phối**. Đúng.
- **Biên phụ (L3):** đúng một biên phụ dưới 4916.4 = cực trị xa nhất; mSOW được giữ **ở lại Phase B** thay vì bị hạ thành "test nhẹ" — đây là vá lỗi H chạy đúng.
- **Phase B (L9):** 70 nến, dài nhất. Bias test biên `+0` (test cả hai biên) — đọc đúng: chart cho thấy giá lên chạm 4989 rồi xuống chạm 4941/4916, đúng là ca thường.
- **Chỉ số SOT phía trên đo đúng bản chất:** `chớm, n=2, thrust cuối/đầu 0.93, volume 0.69× → cạn kiệt`. Volume nhịp cuối giảm còn 69% mà lực đẩy không dài thêm = cầu rút lui ở biên trên (THEORY §7, biến thể "rút ngắn + volume yếu"). Range sau đó phá xuống — chỉ số này đọc đúng hướng.

## Cần hỏi người học
- Khi cây volume lớn nhất của cụm climax là cây **ngược màu** (ở đây: cây đỏ 111 hợp đồng ngay sau đỉnh), anh muốn máy gọi nó là gì: bỏ nhãn, gọi "cây cung đầu tiên", hay coi đó là nến khởi phát AR? Hiện nó đang bị gọi BCLX.
