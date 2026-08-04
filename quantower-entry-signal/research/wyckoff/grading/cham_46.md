# Chấm bài #46 — Chưa rõ (BCLX) (DIST?) · 2026-07-24 14:00 → 20:59 (419 nến M1)

**Điểm: 5/10** — việc **để ngỏ tên range là ĐÚNG** và đáng khen, nhưng biên chính vẽ quá hẹp so với
vùng đấu giá thật nên toàn bộ nửa sau của range bị đọc sai: một cú SOW thật bị hạ cấp thành mSOW.

## Việc để ngỏ tên "Chưa rõ" — ĐÚNG, nhưng đúng vì lý do sai

Trước hết trả lời câu hỏi chính: **để ngỏ tên là đúng nguyên tắc**. L4 nói hướng phá THẬT mới quyết
định tên range, và range này chạy tới nến cuối dữ liệu chưa có SOS/SOW xác nhận → gọi "Chưa rõ
(BCLX)" là trung thực, không gò dữ liệu cho khớp mô hình (đúng tinh thần Ca #20 nguồn 7.pdf). Đây là
tiến bộ thật so với v4 nơi máy mặc định BCLX ⇒ phân phối.

**Nhưng** trong bài này việc "chưa rõ" là **hệ quả của biên vẽ sai**, không phải vì thị trường thật
sự chưa quyết. Xem lỗi #1: nếu biên chính vẽ đúng thì cú sụp 17:20→19:25 đã là một SOW đủ tư cách và
range này phải mang tên **Phân phối (DIST)**. Máy đúng về mặt thủ tục nhưng lý do "chưa rõ" là do nó
tự bịt mắt mình.

## Lỗi (nặng → nhẹ)

### 1. Biên chính chỉ 14.6 giá trong khi vùng đấu giá thật rộng 33.9 — luật vi phạm: L3 + THEORY §3.1
- **Thuật toán gắn:** biên chính 4058.4 – 4073.0 = **14.6 giá (0.36%)**; biên phụ 4051.3 – 4085.2 =
  **33.9 giá**. Biên phụ rộng gấp **2.3 lần** biên chính.
- **Đúng phải là:** khi biên phụ rộng gấp hơn hai lần biên chính, điều đó nói rằng cặp climax+AR đã
  KHÔNG bắt được vùng cân bằng thật. Vùng đấu giá thật của phiên này là 4051–4085 (thấy rõ trên ảnh:
  giá lấp đầy toàn bộ dải giữa hai nét đứt suốt 7 tiếng). Cặp biên chính 4058.4/4073.0 chỉ là hai
  mức bên trong vùng đó — giá cắt qua chúng hàng chục lần, không có mức nào hành xử như một biên.
- **Dấu hiệu quyết định trên chart:** đường liền cam trên 4073.0 bị giá cắt qua khoảng **8 lần** (các
  đỉnh 15:20, 15:40, 16:05, 17:20 đều ở trên nó, các đáy 16:40, 17:00 ở dưới). Một mức bị cắt 8 lần
  không phải biên.
- **Nghi phạm trong thuật toán:** mục 4.1 — AR được nhận là "swing pivot ngược đầu tiên giữ được 5
  nến, nhịp bật ≥ 1.5× biên độ TB". Ngưỡng đó quá dễ đạt: AR ở đây có VSA chỉ **1.00×** và chỉ cách
  climax 17 nến. Nó bắt được cái pivot ĐẦU TIÊN, không phải cái pivot có ý nghĩa cấu trúc. Cần thêm
  điều kiện: nhịp AR phải đạt tối thiểu một tỉ lệ của độ dài MOVE (ở đây move 24.6 giá, AR chỉ hồi
  14.6 = 59% — chấp nhận được), HOẶC hậu kiểm: nếu biên phụ nới quá 1.8× biên chính thì phải **xét
  lại Phase A** thay vì giữ nguyên biên chính vĩnh viễn.

### 2. Cú sụp 4073 → 4051 bị hạ thành mSOW — luật vi phạm: L5, L3 (SOS/SOW phải bứt biên phụ)
- **Thuật toán gắn:** mSOW tại 19:25, giá 4051.3, VSA 2.52× — tức "một cú phá thất bại", Phase B
  tiếp tục.
- **Đúng phải là:** đọc trên ảnh, giá rời đỉnh 4073 lúc 17:20 và **đi xuống liên tục 2 tiếng** qua
  các nhịp thấp dần (4068 → 4062 → 4058 → 4053 → 4051), đóng cửa dưới biên chính dưới 4058.4 suốt
  khoảng **100 nến** liền — đó là **SOW thật** theo L5 ("đóng cửa hẳn ngoài biên và các nến sau đủ
  mạnh giữ nó ở ngoài → phá THẬT"), không phải một cú thọc rồi rút.
- **Dấu hiệu quyết định trên chart:** từ 18:45 tới 20:59 (khoảng 135 nến) **toàn bộ** hành động giá
  nằm dưới đường liền cam 4058.4, không một nến nào đóng lại trên nó. Đây chính xác là điều kiện
  "≥ 60% số nến trong đoạn đóng cửa ngoài biên" của mục 5.1 kết cục B — đạt tới ~100%.
- **Nghi phạm trong thuật toán:** điều kiện SOW của mục 5.1 yêu cầu đóng cửa vượt **biên phụ** thêm
  ≥ 30 tick. Biên phụ dưới ở đây là 4051.3 — chính là ĐÁY của cú sụp. Đây là một vòng lặp logic tự
  huỷ: cú sụp tự nới biên phụ xuống đáy của chính nó, rồi bị đo bằng biên phụ mới đó nên không bao giờ
  "vượt" được. **Phải chốt biên phụ TẠI THỜI ĐIỂM bắt đầu cú phá và không cho cú phá đang được xét tự
  nới biên phụ của chính nó.** Đây là lỗi nặng nhất về mặt code trong cả ba bài.

### 3. Phase B 393 nến = 94% cả range, không có Phase C/D/E — luật vi phạm: L9 (đúng chữ nhưng sai thần)
- **Thuật toán gắn:** A = 27 nến, B = **393 nến**, hết.
- **Đúng phải là:** L9 nói Phase B là phase dài nhất — đúng, nhưng khi B chiếm 94% và không có phase
  nào khác thì cấu trúc không được đọc, chỉ được **khoanh**. Với biên đúng (lỗi #1) và SOW đúng
  (lỗi #2), phân bố phải là: A ~27 · B ~180 (14:27→17:20, đúng là phase dài nhất) · C ~10 (đỉnh
  17:20 = LPSY[C], nhịp test biên trên cuối cùng trước khi sụp) · D ~100 · E phần còn lại.
- **Dấu hiệu quyết định trên chart:** đỉnh 17:20 ở mức ~4073 là **đỉnh cuối cùng** của cấu trúc, và
  ngay sau nó là chuỗi giảm không hồi — đúng khuôn LPSY[C] rồi SOW.
- **Nghi phạm trong thuật toán:** cơ chế gán ngược Phase C (mục 6 case KHÓ, nhìn lại 60 nến trước cú
  phá) chưa bao giờ được kích hoạt vì SOS/SOW không bao giờ được xác nhận (lỗi #2).

### 4. mSOS 15:20 nới biên phụ trên lên 4085.2 rồi biên đó không bao giờ được test lại — luật vi phạm: L3
- **Thuật toán gắn:** mSOS tại 15:20 giá 4085.2 VSA 1.56×, tạo biên phụ trên 4085.2.
- **Đúng phải là:** biên phụ này về nguyên tắc L3 là hợp lệ (một thế lực đã cố phá lên và tạo được
  cực trị 4085.2 ngoài range). Nhưng nhãn **mSOS** đặt vào cây VSA **1.56×** thì yếu — mục 5.1 quy
  định mSOS cần "mạnh: sâu ≥ max(15 tick, 15% chiều cao range) hoặc VSA ≥ 2.2×". Sâu = 4085.2 − 4073.0
  = 12.2 giá = 122 tick, vượt xa 15 tick nên điều kiện "sâu" đạt — nhưng chính vì vậy nó cho thấy
  ngưỡng "15% chiều cao range" (= 2.2 giá) là **quá dễ** khi biên chính chỉ 14.6 giá. Ngưỡng tương
  đối buộc phải neo vào biên PHỤ hoặc vào ATR, không neo vào một biên chính có thể bị vẽ quá hẹp.
- **Dấu hiệu quyết định trên chart:** cú lên 15:20 là cây volume vàng cao nhất nửa đầu chart và giá
  giữ trên 4073 thêm ~60 nến sau đó — nếu tính theo L5 thì đây là một **Shakeout phía trên** (lùng
  bùng ngoài biên một lúc rồi mới quay lại = một SOS thất bại), không phải mSOS đơn thuần. Đó là một
  Phase C bị bỏ sót.
- **Nghi phạm trong thuật toán:** bảng nhãn ở mục 5.1 chỉ cho phép **UTAD** ở cạnh climax phía trên,
  không có ô nào cho "Shakeout phía trên" (SOS thất bại lùng bùng lâu). Bảng L5 của người học thì có
  — Shakeout được định nghĩa đối xứng cho cả hai phía. Bảng trong code đang thiếu một ô.

## Đạt
- **Để ngỏ tên range là ĐÚNG** (L4) — không đoán khi chưa có cú phá xác nhận. Đây là mục tiêu thiết
  kế v5 và nó hoạt động.
- **Điều kiện mở range (L1):** MOVE tăng 24.6 giá / 42 nến, hiệu suất 0.42 (> 0.35), climax 14:00 là
  **đỉnh** của move (H 4073.0 = C 4073.0, đóng cửa ở đỉnh). ĐẠT.
- **Climax chọn đúng cây lần này:** VSA **3.09×**, thân 0.70, biên độ 4.4 giá — đúng khuôn BCLX
  "volume + spread tăng rõ rệt". Đối lập hẳn với bài #45. ĐẠT.
- **Phase A (L2):** đủ 3 lần đổi hướng, kết thúc đúng tại ST[A] 14:26 (4072.3 — test lại đúng mức
  climax 4073.0, lệch 0.7 giá, đúng là một cú test vùng climax). ĐẠT, Phase A 27 nến là hợp lý.
- **Không có nhãn ST[B]** (L6) · không có nhãn nào bị spam.
- **Có hai biên phụ, mỗi bên đúng 1** (L3) — số lượng đúng.

## Cần hỏi người học
- Khi biên phụ nới rộng quá ~1.8× biên chính (ở đây 2.3×), có nên coi đó là bằng chứng Phase A đã bắt
  sai vùng cân bằng và **vẽ lại range** (huỷ ứng viên, mở lại từ cực trị mới), thay vì giữ biên chính
  "cố định vĩnh viễn" theo L3? Hiện L3 nói biên chính không được kéo theo giá — nhưng ca này cho thấy
  cần một cửa thoát khi biên chính rõ ràng nằm giữa vùng đấu giá.
