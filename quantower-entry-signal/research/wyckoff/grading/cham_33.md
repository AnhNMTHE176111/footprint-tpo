# Chấm bài #33 — Chưa rõ (BCLX) (DIST?) · 2026-06-12 15:27 → 20:59 (332 nến M1)

**Điểm: 6/10** — Range khoanh đúng vùng, và điểm đáng khen nhất là **không đặt tên khi chưa có cú phá thật**. Phải sửa vị trí nhãn BCLX và ST[A].

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX đặt vào một nến GIẢM giữa đợt rơi, không phải cây cao trào mua · luật vi phạm: THEORY §4.1 (định nghĩa BCLX)
- **Thuật toán gắn:** nhãn BCLX tại **15:35, giá 4247.5, VSA 2.84x**, trong khi mức climax (biên chính trên) = 4256.8 tại 15:27.
- **Đúng phải là:** BCLX theo định nghĩa gốc là "lực **mua** đạt đỉnh, công chúng đổ xô mua — CO lợi dụng bán ra": nó phải là cây của phe MUA ở vùng đỉnh. Cụm cao trào mua thật đọc thẳng từ bảng 12 nến là **15:21 (VSA 2.61x, nến tăng), 15:24 (2.82x, tăng), 15:25 (2.48x, tăng), 15:26 (1.91x, tăng)** — bốn cây tăng volume cao liên tiếp đẩy giá từ 4234 lên 4256.4. Nến 15:35 nằm **8 nến sau đỉnh**, khi giá đã rơi về 4247 — cây volume cao ở đó là **cung**, thuộc đoạn AR, không phải BCLX. Nhãn phải neo vào cụm 15:24–15:26.
- **Dấu hiệu quyết định trên chart:** trên ảnh nhãn BCLX treo **thấp hơn đường `bien CHINH tren 4256.8` tới 9.3 giá**, nằm giữa đợt nến đỏ đi xuống — người đọc chart sẽ hiểu sai vị trí cao trào.
- **Nghi phạm trong thuật toán:** quy tắc mới "nhãn climax = cây VSA cao nhất trong cụm 8 nến, không cần trùng cực trị giá" **không kiểm hướng nến và không kiểm vị trí so với cực trị**. Cần thêm hai điều kiện: (a) nến mang nhãn phải cùng màu với hướng move (xanh cho BCLX, đỏ cho SC — chính điều kiện (3) ở mục 3 spec, hiện chỉ áp cho nến mở range chứ không áp cho nến mang nhãn); (b) cửa sổ cụm nên tính **cả nến trước** cực trị, không chỉ 8 nến sau.

### 2. ST[A] không test lại vùng climax · luật vi phạm: L2
- **Thuật toán gắn:** ST[A] = 4239.3 (15:55), chốt Phase A.
- **Đúng phải là:** đỉnh climax 4256.8, ST[A] cách nó **17.5 giá = 60% chiều cao range 29.4**, tức chỉ hồi 40% từ AR 4227.4 lên. Đây không phải cú "quay lại phía climax rồi bị chặn lần nữa" của L2 mà chỉ là nhịp hồi giữa range. Lỗi này lặp ở cả 4 bài #30/#31/#33/#34 → là lỗi **hệ thống**, không phải lỗi lẻ.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm gần giữa khoảng hai đường biên liền, ngang tầm nhãn BCLX chứ không ngang tầm biên trên.
- **Nghi phạm trong thuật toán:** mục 4.2 chỉ có **trần** (ST[A] không vượt climax quá 1.0× chiều cao) mà không có **sàn** (ST[A] phải vào trong x% chiều cao tính từ mức climax). Đề xuất sàn: ST[A] phải nằm trong 1/3 khung phía climax — đúng bảng THEORY §5 ("ST ở 1/3 nửa trên / 1/3 nửa dưới").

### 3. Biên trên chỉ được chạm đúng một lần trong suốt 332 nến · luật vi phạm: CHART_CASES mục "Cách xác định biên range" (biên trên cần 1–2 lần chạm)
- **Thuật toán gắn:** biên chính trên 4256.8 giữ nguyên suốt range.
- **Đúng phải là:** sau nến climax, đỉnh cao nhất của cả Phase B chỉ tới ~4252–4253 (cụm 18:34), tức **thiếu ~4 giá = 13% chiều cao** mới chạm biên. Biên trên vì thế chỉ có **1 lần chạm** — mức tối thiểu, và theo THEORY §9 ("cấu trúc được xác nhận bởi lần chạm ở 2 khu vực đối lập") thì phía trên gần như chưa được xác nhận. Vùng đấu giá thật hẹp hơn: khoảng **4227–4253**.
- **Dấu hiệu quyết định trên chart:** đường liền biên trên chạy trống, không có nến nào chạm lại nó trong toàn bộ nửa phải khung.
- **Nghi phạm trong thuật toán:** không có bước "co biên về vùng thực sự được đấu giá" sau Phase B; đây là hệ quả của L3 (biên chính cố định) nên có thể là **đánh đổi có chủ ý** — ghi nhận để người học phân xử, không tính là lỗi code chắc chắn.

### 4. Bias báo "test CẢ HAI biên" trong khi biên trên chưa từng được test lại · lỗi ĐO LƯỜNG (chỉ số v6)
- **Thuật toán gắn:** `bias = +0` → "test CẢ HAI biên — ca THƯỜNG".
- **Đúng phải là:** phía dưới có mSOW thật (4223.2, xuyên qua biên chính dưới), phía trên không có gì trong dung sai chạm 10 tick. Trạng thái đúng là **−1** (chạm nổi biên dưới, không nổi biên trên) — mà đúng ra chỉ số này lại **khớp với thực tế cấu trúc** (áp lực nghiêng về phía cung, khớp nhãn `DIST?`). Việc nó trả +0 làm mất luôn tín hiệu đúng.
- **Nghi phạm trong thuật toán:** ngưỡng "chạm biên" hiện dùng dung sai 10 tick cho cả hai phía nhưng có vẻ đang tính cả nến climax (chạm biên trên tại chính nến sinh biên) — cần loại nến sinh biên khỏi phép đếm, và loại luôn các sự kiện ngoài Phase B.

### 5. Thiếu hẳn chỉ số nhịp nỗ lực/kết quả · lỗi ĐO LƯỜNG (chỉ số v6) — trình bày/đo lường
- **Thuật toán gắn:** phiếu có SOT trên/dưới (`none`, n=0) nhưng **không có dòng "Nhịp nỗ lực/kết quả cao nhất"** — trong khi 4 bài còn lại của lô đều có.
- **Đúng phải là:** Phase B dài **304 nến** là mẫu lớn nhất cả lô; không đo được nhịp effort/result nào là bất thường. Nhìn panel volume có ít nhất 4 cột vàng (VSA ≥ 2.2x) trong Phase B (~16:10, 17:22, 18:30, 19:20) — đủ nguyên liệu để đo.
- **Nghi phạm trong thuật toán:** hàm tính nhịp effort/result nhả rỗng khi range **không có Phase C/D** (bài này dừng ở B) hoặc khi Phase B chưa "đóng" — nên nhánh đo bị bỏ qua thay vì đo tới nến cuối.

## Đạt
- **Mục 1 (mở range):** MOVE tăng 42.5 giá / 40 nến / hiệu suất 0.39 — trên ảnh là cú tăng dốc từ 4205 lên 4256, rất rõ. Nến 15:27 là đỉnh cửa sổ. VSA của chính nến đỉnh chỉ 1.06x nhưng đó là **climax dạng cạn kiệt** (THEORY §6.2), hợp lệ — không được coi thiếu volume lớn là "chưa phải climax".
- **Mục 4 (tên range) — điểm sáng nhất của bài:** chưa có cú phá thật thì để **"Chưa rõ (BCLX)"**, tô xám, không ép đặt tên 4 mẫu hình. Đây đúng tinh thần Ca #20/#22 (đừng gò dữ liệu cho khớp mô hình, đừng chốt cấu trúc quá sớm) và là hành vi trung thực nhất trong cả lô 30–34.
- **Mục 3 (biên):** biên chính cố định sau Phase A; đúng **một** biên phụ dưới 4223.2; tỉ lệ biên phụ/biên chính 1.14x — không phình theo giá.
- **Mục 5 (B dài nhất):** B 304 nến so với A 29 — L9 thoả áp đảo.
- **Mục 2 (một phần):** AR = 4227.4 (15:49) là đáy phản ứng đầu tiên thật sau đợt rơi, đọc đúng; nhịp bật ngược sau đó rõ ràng.
- **Cắt range tại khe cuối tuần:** range đóng ở 20:59 ngay trước khe (trục thời gian nhảy từ 06-12 20:58 sang 06-14 22:34) — cơ chế lỗi K hoạt động đúng.
