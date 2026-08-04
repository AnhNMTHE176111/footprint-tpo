# Chấm bài #01 — Chưa rõ (SC) (ACC?) · 2025-12-29 15:22 → 2025-12-31 21:55 (118 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây. Dữ liệu quá thưa (118 nến trải 2,5 ngày lịch, phần lớn nến volume 1-2 hợp đồng); cái được gọi là "range" thực chất là đoạn giá vẫn đang trôi xuống, và Phase A bị dựng sai thứ tự.

## Lỗi (nặng → nhẹ)

### 1. Range vẽ trên dữ liệu rỗng — 118 "nến" trải 2,5 ngày lịch, volume 1-2 lot/nến — luật vi phạm: L1 (không phải vùng đấu giá thật) + lỗi kinh điển "range quá vụn"
- **Thuật toán gắn:** một TR đủ Phase A→C với biên chính 4411,4-4511,7.
- **Đúng phải là:** không mở range. Đọc bảng 12 nến quanh climax: volume các nến là 2, 2, 1, 1, 2, 1, **7**, 1, 1, 1, 1, 1. Cây "climax" 3,33× là một nến **7 hợp đồng**. Đây là kỳ nghỉ cuối năm (29-31/12), thị trường gần như không giao dịch — không có Composite Man nào phân phối/tích luỹ bằng 7 lot.
- **Dấu hiệu quyết định trên chart:** trục thời gian dưới ảnh chạy từ 12-26 tới 01-05 — hơn 10 ngày lịch cho toàn cửa sổ, trong khi tổng số nến hiển thị chỉ vài trăm. Panel volume gần như phẳng sát đáy suốt toàn range, chỉ bật lên ở ngày 01-02 (**ngoài** range).
- **Nghi phạm trong thuật toán:** người học đã chốt "không dùng sàn khối lượng tuyệt đối, lọc bằng cấu trúc". Nhưng ở đây **cấu trúc cũng không lọc được** vì VSA là tỉ lệ với TB 20 nến — mà TB 20 nến ở phiên chết là ~2 lot. Guard duy nhất có thể cứu là **guard khe thời gian** (lỗi K ở v5: "khe > 4 giờ thì cắt range"). Guard này rõ ràng **chưa chạy đúng**: từ nến -1 (15:21) sang +3 (15:51) là 30 phút cho 4 nến, và trong Phase B có những đoạn nhảy nhiều giờ. Đề nghị đổi guard từ "khe > 4h" sang "**mật độ nến**": số nến / số phút lịch trong range phải ≥ một ngưỡng (vd 0,2 nến/phút), nếu không thì bỏ range.

### 2. Climax không chặn được move — giá tiếp tục xuống sâu hơn climax 27,8 giá — luật vi phạm: L1 (climax phải là cực trị chặn move)
- **Thuật toán gắn:** SC tại 4411,4, coi đó là biên chính dưới, cố định.
- **Đúng phải là:** SC này không chặn được gì. Điểm thấp nhất của range là 4383,6 (biên phụ) — thấp hơn SC **27,8 giá**, tức **28% chiều cao biên chính** (100,3 giá). Một cây climax mà giá sau đó xuyên qua gần 1/3 chiều cao range thì nó chỉ là một nến trên đường đi xuống, không phải điểm dừng của move.
- **Dấu hiệu quyết định trên chart:** nét đứt "biên phụ dưới 4383,6" nằm hẳn dưới nét liền "biên chính dưới 4411,4"; và nhìn ra ngoài range, giá ngày 01-02 còn xuống tiếp tới ~4400 rồi mới bật. Move giảm 245,4 giá chưa hề bị chặn tại 4411,4.
- **Nghi phạm trong thuật toán:** v5 có guard "sau cửa sổ cụm 8 nến, giá vượt mức climax quá 3× biên độ TB → bỏ range" (lỗi A). Biên độ nến climax là 14,2 giá, nhưng biên độ **TB 20 nến** ở phiên chết này gần bằng 0 (đa số nến O=H=L=C). Vậy 3× TB là một số cực nhỏ, đáng lẽ phải bắn ngay. Nghi ngờ guard này đo bằng ATR tính trên dữ liệu thưa nên vô hiệu, hoặc chỉ áp trong cửa sổ 8 nến rồi thôi. Nên đổi mốc so sánh sang **% chiều cao biên chính** (vd vượt > 20% chiều cao → bỏ range) thay vì bội số ATR.

### 3. AR và ST[A] đều là nến chết (VSA 1.00×, thân/biên độ 0.00) — luật vi phạm: L2 (AR phải là cú bật ngược THẬT)
- **Thuật toán gắn:** AR tại 4511,7 (VSA 1,00×, thân 0,00), ST[A] tại 4476,0 (VSA 1,00×, thân 0,00).
- **Đúng phải là:** cả hai đều là nến O=H=L=C — một tick đơn lẻ, không có giao dịch hai chiều. AR trong định nghĩa gốc (THEORY §3.3) là "sóng mua đẩy giá lên" sau khi áp lực bán giảm mạnh; một cái tick 4511,7 không phải sóng mua.
- **Dấu hiệu quyết định trên chart:** cả hai chấm AR/ST[A] nằm trên các nến vẽ ra chỉ là một gạch ngang mảnh; panel volume tại vị trí đó không có thanh vàng nào.
- **Nghi phạm trong thuật toán:** bước tìm AR/ST[A] bằng "swing pivot + 1,5× biên độ TB" (v5 lỗi D) không kèm bất kỳ điều kiện chất lượng nến nào. Nên thêm: nến làm mốc AR/ST[A] phải có biên độ > 0 và VSA ≥ 1,0× (tối thiểu không được là nến O=H=L=C).

### 4. Spring gắn sai loại theo L5 — và đang ở trạng thái "pending" khi range đã đóng — luật vi phạm: L5, L8
- **Thuật toán gắn:** Spring tại 4383,6 lúc 31/12 06:01, trạng thái **pending**, Phase C dài 25 nến, range kết thúc [completed] tại 31/12 21:55.
- **Đúng phải là:** nếu cú rũ này chưa bao giờ xác nhận (chưa đi nổi 50% sang biên đối diện, hết hạn chờ) thì theo chính spec v5 (lỗi C) nó phải bị **đổi nhãn thành mSOW và xoá đoạn Phase C**. Ở đây nhãn vẫn là "Spring", trạng thái vẫn "pending", đoạn Phase C vẫn nằm trên timeline, và range vẫn được đóng là "[completed]" — ba thứ mâu thuẫn nhau.
- **Dấu hiệu quyết định trên chart:** dải "Phase C (25n)" chạy tới hết range mà không có SOS/SOW nào theo sau; chấm Spring vẽ viền đứt (đang chờ) trong một range đã đóng.
- **Nghi phạm trong thuật toán:** nhánh "quét tới nến cuối / đóng range" không chạy lại thủ tục hạ cấp shock hết hạn. Vá lỗi C mới xử lý trường hợp timeout 120 nến, chưa xử lý trường hợp **range đóng khi shock còn pending**.

### 5. Nhãn "Spring" nhưng VSA 0,50× và thân 0,00 — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** Spring, VSA 0,50×.
- **Đúng phải là:** cây tạo đáy 4383,6 nhìn trên ảnh là một nến đỏ thân dài (nến rơi rõ nhất trong cả range, có thanh volume vàng ngay dưới nó lúc ~12-30 23:25). Nhưng nhãn Spring lại được neo vào một nến VSA 0,50× thân 0,00. Đây đúng là **lỗi B của vòng v4 tái xuất ở dạng khác**: nhãn shock neo sai cây, không neo vào cây phá thật.
- **Dấu hiệu quyết định trên chart:** cụm nến đỏ dài quanh 12-30 23:25 có thanh volume vàng (VSA ≥ 2,2×); chấm "Spring" lại nằm lệch sang phải, ở đáy một nến gần như không có thân.
- **Nghi phạm trong thuật toán:** v5 chỉ đặt hồi tố cho **SOS/SOW** (lỗi B), chưa áp cùng cơ chế cho **Spring/Shakeout/UTAD**. Nên dùng chung một hàm "chọn cây đại diện cho cú phá" cho cả hai nhóm nhãn.

## Đạt
- Phép đo MOVE trước climax chạy đúng: 245,4 giá / 64 nến / hiệu suất 0,47 — đây là một move giảm thật, không phải đi ngang. Điều kiện CẦN của L1 về phía move là ĐẠT.
- Không đặt tên range khi chưa có cú phá thật ("Chưa rõ (SC) (ACC?)", tô xám) — đúng L4, đúng tinh thần vá lỗi F.
- Phase B (68 nến) dài hơn Phase A (26) và Phase C (25) — đúng L9/L8 về tỉ lệ.
- Biên chính vẽ nét liền, biên phụ nét đứt, mỗi bên đúng 1 cái — đúng L3 về hình thức.
- Không có nhãn ST[B] — đúng L6.

## Cần hỏi người học
- Có chấp nhận thêm một **guard mật độ nến** (số nến / phút lịch) để loại hẳn các range hình thành trong phiên nghỉ lễ không? Guard này không có trong lý thuyết Wyckoff, nhưng nếu không có thì mọi kỳ nghỉ đều sinh range rác, mà người học lại đã chốt "không dùng sàn khối lượng tuyệt đối".
