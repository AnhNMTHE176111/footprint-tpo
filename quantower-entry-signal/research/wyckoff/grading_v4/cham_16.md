# Chấm bài #16 — Tái phân phối (RE-DIST) · 2026-05-26 11:35 → 18:35 (420 nến M1)

**Điểm: 3/10** — Ở đây CÓ một vùng đấu giá thật và cú phá xuống thật, nhưng cả hai biên chính, mốc Phase A và nhãn SOW đều đặt sai chỗ; phải vẽ lại chứ không chỉ sửa vài nhãn.

## Lỗi (nặng → nhẹ)

### 1. Cây climax KHÔNG chặn được move — mốc SC đặt sai, kéo theo biên chính dưới sai — luật vi phạm: L1
- **Thuật toán gắn:** SC tại 4540.4 (11:35, VSA 5.62x) và lấy luôn mức đó làm biên CHÍNH dưới.
- **Đúng phải là:** SC phải là điểm move giảm **thật sự bị chặn**. Sau 11:35 giá còn tạo bốn đáy thấp hơn liên tiếp: 4538.0 (11:43), 4536.0 (11:58), **4533.1 (12:31, VSA 3.31x)**, 4534.4 (12:39). Mốc SC hợp lý là 12:31 @4533.1 — hoặc phải coi cả cụm 11:35–12:39 là **vùng SC** (đúng như Ca #12 nguồn 2.pdf: "SC có thể là cả một vùng TR nhỏ"). Biên chính dưới phải là 4533, không phải 4540.4.
- **Dấu hiệu quyết định trên chart:** biên chính dưới 4540.4 bị xuyên qua liên tục ngay trong Phase A; suốt 3 lần Phase C (15:18–17:35) có **107/138 nến đóng cửa dưới 4540.4** — một "biên" mà 78% thời gian giá nằm dưới thì không phải biên.
- **Nghi phạm trong thuật toán:** điều kiện mở range chỉ kiểm climax là cực trị của **240 nến TRƯỚC**, không kiểm gì phía **sau**. Cần thêm: nếu trong K nến sau climax có đáy thấp hơn > X tick thì dời mốc climax (và biên chính) xuống đáy đó.

### 2. Phase A chưa xong CHoCH — ST[A] là một cái ngọ nguậy giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 4549.9 (13:13), đóng Phase A sau 99 nến.
- **Đúng phải là:** ST[A] phải là cú **quay về phía climax rồi bị chặn lần nữa**. 4549.9 nằm giữa range (cách climax 9.5 giá, cách biên trên 9.8 giá) và ngay sau đó giá đi **lên** tiếp tới 4565.3 (UA) — tức lần đổi hướng thứ ba chưa xảy ra ở đó. ST[A] thật là nhịp về vùng 4533–4538 (12:31/12:39), tức Phase A phải **kết thúc trước AR**, và AR mới là mốc đóng Phase A theo nghĩa ngược lại — nói cách khác chuỗi sự kiện của máy bị lệch một nhịp.
- **Dấu hiệu quyết định trên chart:** ST[A] chỉ là pullback 9.8 giá trong một nhịp tăng còn đang tiếp diễn; không có 5 nến nào bị chặn ở vùng climax.
- **Nghi phạm trong thuật toán:** ngưỡng "ST[A] phải hồi ≥ **40%** chiều cao climax↔AR" quá lỏng — 40% chỉ đưa giá về giữa range. Nên đòi ST[A] **chạm dung sai vùng climax** (vd ≥ 75% chiều cao, hoặc trong 15 tick của mức climax).

### 3. Nhãn AR không nằm trên biên chính của chính nó — luật vi phạm: L3
- **Thuật toán gắn:** nhãn AR ở 4554.0 (12:49) nhưng biên CHÍNH trên vẽ ở **4559.7**.
- **Đúng phải là:** biên chính trên = **mức AR**. Ở đây AR đã được dời ngầm tới cực trị mới (4559.7 @13:02) nhưng **nhãn không dời theo**, để lại một nhãn AR nằm 5.7 giá (30% chiều cao range) dưới biên của nó.
- **Dấu hiệu quyết định trên chart:** đọc phiếu số liệu thấy "biên chính 4540.4–4559.7" trong khi hàng sự kiện ghi AR = 4554.0.
- **Nghi phạm trong thuật toán:** nhánh "dời AR tới cực trị mới" (mục 4.2) chỉ cập nhật **mức**, không cập nhật **nến/nhãn** AR.

### 4. Phase C ba lần, tổng 130 nến — C không còn là phase ngắn nhất — luật vi phạm: L8, L9
- **Thuật toán gắn:** B(124) → C(13) → B(6) → C(38) → B(2) → C(79) → B(34) → D(25) → E(1). Ba cú rũ đều mang trạng thái **thất bại**.
- **Đúng phải là:** cú rũ thất bại nghĩa là **phe phá thua** — đoạn đó thuộc **Phase B** (giai đoạn test cung/cầu), không được giữ nhãn Phase C. Toàn bộ 15:18–17:35 là Phase B với ba lần test biên dưới; Phase C thật chỉ là nhịp cuối trước SOW (LPS[C] 17:30 hoặc đoạn 17:36–18:09).
- **Dấu hiệu quyết định trên chart:** Phase C dài nhất 79 nến, dài hơn cả ba Phase B kề nó (2, 6, 34 nến) — trái hẳn L8/L9.
- **Nghi phạm trong thuật toán:** khi cú rũ thất bại, máy "lùi về Phase B" **từ nến hiện tại** mà không **trả lại** nhãn Phase B cho đoạn đã sơn C. Cần viết lại đoạn phase khi shock bị đánh dấu thất bại.

### 5. Nhãn SOW đặt trên ba nến TĂNG volume cực thấp — luật vi phạm: mục 8 Effort vs Result (THEORY §2.2)
- **Thuật toán gắn:** SOW tại 18:10, giá 4521.8, **VSA 0.23x** (18 lot), nến **tăng** (o 4520.2 → c 4521.8).
- **Đúng phải là:** SOW/MSOW là nến phá đáy range với biên độ lớn + volume tăng (Ca #2 nguồn 4.pdf). Nến đó là **18:05**: 4520.2 → 4515.2, low 4512.8, **VSA 2.65x**. Lúc máy dán nhãn SOW thì giá đã bật lại 9 giá từ đáy.
- **Dấu hiệu quyết định trên chart:** ba nến xác nhận 18:08 / 18:09 / 18:10 đều **xanh** (4516.1→4518.2, 4518.1→4520.2, 4520.2→4521.8), volume 20/27/18 lot (VSA 0.26 / 0.35 / 0.23x). Panel khối lượng: cột lớn nằm ở 17:40–18:05, không ở chỗ dán nhãn.
- **Nghi phạm trong thuật toán:** điều kiện phá thật "3 nến liên tiếp đóng cửa vượt biên phụ ≥30 tick **và** thân ≥45%" **không kiểm hướng nến** → ba nến tăng vẫn xác nhận một SOW. Nến đẩy thật (18:05) lại bị loại vì thân/biên độ 0.62 nhưng nến 18:06–18:07 phá chuỗi. Sửa: đặt nhãn tại **nến phá có volume/biên độ lớn nhất trong cụm**, và bắt buộc nến SOS/SOW đúng hướng + VSA ≥ 1.

### 6. LPS[C] gắn ba lần — luật vi phạm: L7
- Mỗi lần vào Phase C máy lại sinh một LPS[C] (15:23 / 16:06 / 17:30). L7 nói LPS[C] chỉ đánh **một điểm**. Giữ đúng cái cuối (17:30, ngay trước SOW).

### 7. Phase E chỉ 1 nến, chốt lúc giá đang hồi vào trong — luật vi phạm: L10
- LPSY[D] 18:33 đóng cửa **4530.0**, tức đã **quay vào trong** biên phụ dưới 4528.4 (16 tick, vừa lọt dung sai 30 tick); Phase E chốt tại 18:35 khi giá ở 4528.3 — sát biên, không phải "rời range đi tìm vùng giá mới".

## Đạt
- Điều kiện MOVE trước climax: 33.3 giá / 44 nến / hiệu suất 0.73 — một move giảm thật, không phải đi ngang (L1, phần điều kiện CẦN).
- Tên range **Tái phân phối** khớp origin SC + hướng phá xuống thật (L4) — không xoá range vì "phá sai hướng", đúng tinh thần L4.
- Biên phụ mỗi bên đúng 1 cái (4528.4 / 4565.3), đều là cực trị xa nhất — đúng L3.
- Có ghi trạng thái "(thất bại)" cho cú rũ thay vì lặng lẽ giữ nhãn — trung thực, đúng tinh thần đánh giá cú rũ bằng kết quả (THEORY §5, WY10/WY12).

## Cần hỏi người học
- Khi cụm nến quanh climax tạo **nhiều đáy thấp dần** trong 1 giờ (11:35–12:39), anh muốn máy lấy **nến VSA cao nhất** làm SC (như hiện nay) hay lấy **đáy thấp nhất của cụm** làm mốc SC + biên chính?
