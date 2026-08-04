# Chấm bài #11 — Tích luỹ (ACC) · 2026-04-26 23:41 → 2026-04-27 05:49 (146 nến M1)

**Điểm: 2/10** — **không nên vẽ range ở đây.** Cây "climax" chỉ có biên độ **0.6 giá / 3 hợp đồng**, và MOVE dùng để mở range **bắc qua khe cuối tuần ~50 giờ**. Trước climax giá đang đi ngang, tức vi phạm thẳng L1.

## Lỗi (nặng → nhẹ)

### 1. MOVE trước climax bắc qua khe cuối tuần — luật vi phạm: L1, và biến thể của lỗi K (khe > 4 giờ) chưa được vá cho phép đo MOVE
- **Thuật toán gắn:** MOVE 39.0 giá / **28 nến**, hiệu suất 0.63 — con số nhìn qua thì đẹp nhất cả lô.
- **Đúng phải là:** không có move nào. Trục thời gian trên ảnh đi **04-24 19:58 → 04-24 20:49 → 04-26 22:25 → 04-27 00:10**: chân MOVE nằm ở **thứ Sáu 04-24 ~20:00**, climax nằm ở **Chủ Nhật 04-26 23:41**. Giữa hai điểm là khe nghỉ cuối tuần ~50 giờ. "28 nến" là 28 nến **có giao dịch**, không phải 28 phút liên tục.
- **Dấu hiệu quyết định trên chart:** đường xám chân-MOVE trên ảnh vẽ vắt từ cụm nến bên trái (04-24) sang chấm SC — cắt ngang một vùng chart hoàn toàn trống. Ngay trước climax, giá **đi ngang** 4727-4733 suốt cả đoạn 04-26 22:25 → 23:40 (xem cụm nến ngắn nằm sát nhau ở nửa dưới ảnh). Đó chính xác là ca L1 cấm: "giá đang đi ngang mà xuất hiện nến volume cao thì không được mở range".
- **Nghi phạm trong thuật toán:** guard khe > 240 phút hiện chỉ áp cho **range đang chạy** (mục 8). Cửa sổ nhìn lại 240 nến để đo MOVE **không** kiểm khe. Phải cắt cửa sổ MOVE tại khe > 4 giờ giống như cắt range.

### 2. Cây climax là nhiễu: biên độ 0.6 giá, volume 3 hợp đồng — luật vi phạm: L1 (climax phải chặn được một move), THEORY §3.3 (SC = "biên độ mở rộng + khối lượng tăng mạnh")
- **Thuật toán gắn:** climax SC tại 4724.5 (nến 23:41), **VSA 1.94x, biên độ nến 0.6 giá, volume 3**; nhãn SC dời về 23:40 (4724.7, VSA 4.14x, volume **6**, biên độ 0.8 giá).
- **Đúng phải là:** bỏ ứng viên. Cây climax chiếm **1.7% chiều cao range (0.6 / 34.6 giá)** — về mặt vật lý nó không thể "chặn" bất cứ move nào. Sáu nến trước climax là **O=H=L=C** (biên độ **bằng 0**, volume 1) → biên độ TB 20 nến ≈ 0.2-0.3 giá, nên ngưỡng "biên độ ≥ 1.4× TB20" bị thoả bởi một nến 0.6 giá. Đây là nhiễu chia cho nhiễu.
- **Dấu hiệu quyết định trên chart:** panel volume ở vùng climax gần như trống; cột volume cao nhất cả chart nằm ở **00:50-01:04** (cú bung lên), không ở climax.
- **Nghi phạm trong thuật toán:** hai ngưỡng mở range đều **tương đối** (1.4× ATR20, VSA ≥ 2.2x) và người học đã chốt không dùng sàn khối lượng tuyệt đối. Nhưng vẫn cần một sàn **cấu trúc**: biên độ cây climax ≥ X% chiều cao range sẽ tạo ra, hoặc mẫu số ATR20 phải có sàn (loại các nến biên độ 0 ra khỏi TB).

### 3. AR không phải "phản ứng tự động" mà là một cú breakout tăng — luật vi phạm: L2, L3 (biên chính = climax + AR)
- **Thuật toán gắn:** AR tại 4759.1 (01:04), VSA 0.24x → chốt biên chính trên. Chiều cao biên chính **34.6 giá**.
- **Đúng phải là:** AR là nhịp bật ngược **ngay sau** climax do áp lực bán cạn. Ở đây giá lình xình 4727-4733 suốt **60+ nến** sau climax, rồi tới 00:50-01:04 mới bùng một mạch **+30 giá** với cột volume lớn nhất chart. Đó là một cú đẩy có chủ đích (THEORY §8 "nguồn cầu khẩn cấp"), không phải AR. Range dựng từ [nến nhiễu ở dưới, đỉnh cú bung ở trên] không mô tả vùng đấu giá nào.
- **Dấu hiệu quyết định trên chart:** khoảng cách climax → AR là **43 nến**, và toàn bộ 43 nến đó nằm sát biên **dưới** (4727-4733), không có nhịp bật nào. Trên ảnh, cả nửa trái của khung range trống hoàn toàn ở phần giữa/trên.
- **Nghi phạm trong thuật toán:** AR = swing pivot ngược đầu tiên được xác nhận, không có trần thời gian ngoài 300 nến và không kiểm "nhịp bật có liền kề climax không". Nhãn "AR (yếu)" chỉ bắn khi AR **quá gần** climax (1-2 nến); thiếu nhánh đối xứng cho AR **quá xa** climax.

### 4. ST[A] nằm đúng 50% chiều cao range, không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 4741.7 (01:16), VSA 0.29x, thân 1.00.
- **Đúng phải là:** ST[A] phải quay về test vùng SC 4724.5. 4741.7 còn cách **17.2 giá = 50% chiều cao range** — là một cái ngọ nguậy giữa range, chỉ 12 nến sau AR.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] trên ảnh lơ lửng giữa hai đường cam, cách đường "biên CHÍNH dưới 4724.5" gần nửa chart. Đúng lỗi đã gặp ở bài #09.
- **Nghi phạm trong thuật toán:** cùng nghi phạm với #09 — sàn chống nhiễu ST[A] = 1.5× biên độ TB, quá thấp ở phiên Á. Nên neo theo % chiều cao range hoặc yêu cầu ST[A] vào **1/3 phía climax** (THEORY §5 chia 3 phần).

### 5. Thiếu hẳn Phase C — luật vi phạm: L8 + mục 6 (case khó phải gán ngược LPS[C] khi có SOS)
- **Thuật toán gắn:** dải phase A → B → **D** → E.
- **Đúng phải là:** SOS bắn lúc 02:47 mà range chưa từng có Phase C → bắt buộc nhìn ngược lấy nhịp test cuối làm LPS[C]. Trên ảnh, nhịp lùi về ~4744 quanh 01:40-01:50 rồi bò lên là ứng viên LPS[C] rõ ràng.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược = min(60, 1/2 Phase B) = min(60, 22) = 22 nến; nhịp test nói trên nằm ngoài 22 nến đó. Lỗi lặp ở #09 (cửa sổ 6 nến) và #12 — công thức min(...) tự khoá ở mọi range có Phase B ngắn.

### 6. Thiếu LPS[D] dù Phase D dài 25 nến — luật vi phạm: L10, L7
- **Thuật toán gắn:** SOS 02:47 (4766.7) rồi Phase D 25 nến, không nhãn retest nào.
- **Đúng phải là:** trên ảnh, sau SOS giá lên 4773, lùi về ~4762 (vẫn **trên** biên phụ 4760.1), rồi lên 4780. Nhịp lùi đó là LPS[D] chuẩn CBR — phải đánh 1 điểm.
- **Nghi phạm trong thuật toán:** giống #10 — sàn 1.5× biên độ TB tính trên ATR đã bị cây phá kéo lên, nên nhịp hồi thật bị loại.

### 7. Phase E kết thúc trong lúc giá đã lùi vào lại trong biên — luật vi phạm: L10 (Phase E = đi tìm vùng giá mới)
- **Thuật toán gắn:** Phase E 32 nến, range "completed", kết ở 05:49.
- **Đúng phải là:** nửa cuối ảnh cho thấy sau đỉnh 4780 (~04:20) giá đổ về **4757-4762**, tức **lùi lại quanh và dưới biên chính trên 4759.1**. Theo mục 7, Phase E phải chốt ngay khi có nến đóng cửa lùi hẳn vào trong biên đã phá — và về bản chất cú phá này **không giữ được vùng giá mới**.
- **Nghi phạm trong thuật toán:** điều kiện đóng Phase E ("lùi hẳn vào trong biên đã phá") hoặc dùng biên phụ 4760.1 với dung sai 30 tick nên 4757 chưa đủ, hoặc mốc "đi xa 2.0× chiều cao" đã bắn trước đó nên nhánh lùi không được xét.

## Đạt
- **Mục 3 phần biên phụ (L3):** biên phụ mỗi bên tối đa 1, tỷ lệ 1.03x — vẽ trung thực, không phình.
- **Mục 4 (L4):** SC + phá lên = Tích luỹ; tên khớp origin + hướng phá thật.
- **Mục 8 phần SOS:** SOS đặt tại cây VSA **2.33x** thân 1.00, đóng cửa vượt biên phụ 4760.1 — neo đúng cây phá, không rơi vào nến rác (vá lỗi B của v5 chạy đúng).
- **Chỉ số bias = +1** (chạm nổi biên trên, không nổi biên dưới): đo đúng, khớp chart và khớp hướng phá.

## Cần hỏi người học
- Ở phiên Á, chuỗi nến **O=H=L=C** (biên độ 0, volume 1) làm mẫu số ATR20 tụt gần 0 và mọi ngưỡng tương đối mất nghĩa. Người học đã chốt không dùng sàn khối lượng tuyệt đối — vậy chấp nhận cách nào: (a) loại nến biên độ 0 khỏi phép tính TB, (b) đặt sàn tick cho ATR20, hay (c) không mở range khi số nến biên độ 0 trong 20 nến trước > ngưỡng?
