# Chấm bài #45 — Tái tích lũy (RE-ACC) · 2026-07-22 12:30 → 16:08 (218 nến M1)

**Điểm: 4/10** — khung xương Phase A vẽ đúng lần đầu tiên trong vòng này, nhưng cây climax chọn sai
cây và toàn bộ nửa sau (SOS/Phase D/E) là một cú phá được gán nhãn ngược hoàn toàn với khối lượng.

## Lỗi (nặng → nhẹ)

### 1. SOS gắn vào cây VSA 0.59× — Effort ngược Result — luật vi phạm: THEORY §2.2 (Nỗ lực–Kết quả), §3.3 (SOS)
- **Thuật toán gắn:** SOS tại 13:43, giá 4150.8, **VSA = 0.59×** (nửa khối lượng trung bình).
- **Đúng phải là:** SOS theo định nghĩa gốc là "spread + volume tăng đều". Cây phá thật của đoạn này
  nằm ở cụm 13:29–13:42 nơi panel volume có hai thanh vàng cao nhất cả chart (VSA ≥ 2.2×) — chính là
  cụm nến bứt qua 4139.5. Nhãn SOS phải hồi tố về cây đó, không phải cây 13:43.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu ghi SOS VSA 0.59×; trên panel khối lượng, hai
  thanh vàng cao vọt nằm ngay dưới nhãn LPS[C] (13:29–13:33), tức TRƯỚC nhãn SOS 10 nến. Cây phá thật
  đã đi qua trước khi máy dán nhãn.
- **Nghi phạm trong thuật toán:** mục 5.1 kết cục B nói nhãn SOS được đặt **hồi tố vào cây VSA cao
  nhất trong đoạn, đúng hướng, đóng cửa vượt biên**. Ở đây cửa sổ hồi tố rõ ràng bị giới hạn trong
  3 nến xác nhận, chưa lùi về cây phá thật. Lỗi B của v4 chưa vá xong.

### 2. Climax chọn sai cây — chọn doji VSA 1.79× trong khi cây 2.20× nằm ngay cạnh — luật vi phạm: L1 + THEORY §3.3 (BCLX)
- **Thuật toán gắn:** BCLX = nến 12:30, VSA **1.79×**, thân/biên độ **0.08** (gần như doji chân
  nhang, O 4137.8 → C 4137.6).
- **Đúng phải là:** BCLX phải là "volume + spread tăng rõ rệt, lực mua đạt đỉnh". Nến 12:28 có VSA
  **2.20×**, thân 0.68, đẩy giá 4135.8 → 4137.3 — đó mới là cây nỗ lực. Nến 12:30 chỉ là cây kiệt
  sức nối theo. Nếu chấp nhận cụm climax (mục 4.0) thì phải neo cụm 12:28–12:30, không neo mỗi cây
  cuối cùng.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến quanh climax — VSA cột: 1.34 / **2.20** / 1.12 /
  **1.79 (climax)**. Cây được chọn không phải cây volume cao nhất trong cụm.
- **Nghi phạm trong thuật toán:** mục 3 nhóm (1) đặt ngưỡng climax VSA ≥ **2.2×**, nhưng cây được
  chọn chỉ 1.79× → hoặc ngưỡng đang được áp trên một cây khác rồi mốc bị dời bởi luật "cụm climax"
  8 nến (mục 4.0) sang cây có **cực trị giá** mới mà không kiểm lại volume. Luật dời cụm đang dời
  theo GIÁ mà bỏ qua VOLUME.

### 3. Biên phụ trên vô nghĩa (0.3 giá) nhưng SOS vẫn được coi là "bứt qua biên phụ" — luật vi phạm: L3
- **Thuật toán gắn:** biên chính trên 4139.5, biên phụ trên **4139.8** — cách nhau **0.3 giá** trên
  một range cao 29.1 giá (1%).
- **Đúng phải là:** biên phụ phải là "cực trị xa nhất mà một thế lực đã cố phá range gốc tạo ra".
  Một cái râu thò 0.3 giá không phải là một thế lực cố phá range — nó là nhiễu tick. Ở đây đúng ra
  **không có biên phụ trên**, và luật "SOS phải đóng cửa bứt qua biên phụ" mất hết tác dụng lọc.
- **Dấu hiệu quyết định trên chart:** nét đứt cam nằm chồng khít lên nét liền cam ở phía trên, hai
  nhãn "bien CHINH tren 4139.5" và "bien phu" đè lên nhau không đọc được.
- **Nghi phạm trong thuật toán:** mục 5.0 nới biên phụ không có ngưỡng tối thiểu. Cần điều kiện thò
  ra ≥ 10 tick (đúng như ngưỡng đã dùng để kích hoạt theo dõi cú phá ở mục 5) mới được ghi biên phụ,
  nếu không thì mọi râu nến đều sinh ra một biên phụ giả.

### 4. Phase C 14 nến nhưng chỉ có LPS[C] — case khó gán ngược chưa chuẩn — luật vi phạm: L8
- **Thuật toán gắn:** Phase C 13:29–13:42, LPS[C] tại 13:29 giá 4135.8 (VSA 0.84×).
- **Đúng phải là:** L8 nói case khó thì "chờ SOS/SOW xuất hiện rồi quay lại vẽ Phase C", lấy
  **nhịp test cuối cùng** trước cú phá. Ở đây LPS[C] 13:29 nằm ở giá 4135.8, tức **trong** range dưới
  biên trên 3.7 giá — đây là nhịp test hợp lệ về nguyên tắc. Nhưng vì SOS bị neo sai cây (lỗi #1),
  ranh giới C/D lệch theo: đoạn 13:30–13:33 (cụm volume vàng) đúng ra thuộc **Phase D** chứ không
  phải Phase C. Phase C thật chỉ nên dài 1–4 nến.
- **Dấu hiệu quyết định trên chart:** hai thanh volume vàng cao nhất chart nằm **bên trong** vạch dọc
  Phase C — nỗ lực phá biên lớn nhất của cả range bị xếp vào phase "chờ", không phải phase "phá".
- **Nghi phạm trong thuật toán:** hệ quả dây chuyền của lỗi #1, sửa nhãn SOS thì ranh giới này tự về.

### 5. Phase E 121 nến = 55% cả range — luật vi phạm: L10, L9
- **Thuật toán gắn:** Phase E 14:08 → 16:08, **121 nến**, dài hơn A+B+C+D cộng lại (98 nến).
- **Đúng phải là:** L10 — Phase E là "giá rời range đi tìm vùng giá mới". Nhìn ảnh: từ 14:08 giá
  không đi tìm vùng nào cả, nó dao động 4152–4172 suốt 2 tiếng và cuối cùng quay về 4152 — đó là một
  **vùng đấu giá MỚI** (một range mới), không phải đuôi của range cũ. L9 nói Phase B là phase dài
  nhất; ở đây B chỉ 27 nến còn E 121 nến, tỉ lệ phase bị lộn ngược.
- **Dấu hiệu quyết định trên chart:** nửa phải chart (từ 14:10 tới hết) là một dải sideway biên độ
  ~20 giá hoàn toàn nằm ngoài mọi biên của range 45 — hình dạng của một range mới, thuật toán vẫn
  tô là Phase E của range cũ.
- **Nghi phạm trong thuật toán:** mục 7 chốt Phase E khi đi thêm bằng chiều cao biên chính (29.1
  giá) hoặc hết 25 nến mà đi được ≥ 50%. Cả hai điều kiện đều đã đạt sớm hơn nhiều, nhưng đoạn E vẫn
  kéo tới 121 nến → điểm KẾT THÚC range không được cắt tại lúc chốt Phase E, mà kéo tới lúc range
  sau mở. Cần đóng range ngay tại nến chốt Phase E.

### 6. (trình bày) Hai nhãn biên trên chồng chữ
Nhãn "bien CHINH tren 4139.5" và nhãn biên phụ in đè lên nhau, không đọc được số nào. Hệ quả trực
tiếp của lỗi #3 — sửa lỗi #3 thì lỗi này tự hết.

## Đạt
- **Điều kiện mở range (L1):** có MOVE thật — 15.6 giá / 47 nến, hiệu suất hướng 0.50 (rất cao,
  ngưỡng 0.35), và climax nằm ở **đỉnh** của move chứ không nằm giữa. Mũi xám bên trái vẽ đúng chân
  move. ĐẠT.
- **Phase A (L2):** đủ 3 lần đổi hướng — BCLX 4139.5 (chặn move tăng) → AR 4110.4 (bật ngược thật,
  VSA **5.03×**, cú bật rõ nhất chart) → ST[A] 4124.6 quay về phía climax rồi bị chặn. Phase A kết
  thúc đúng tại ST[A]. ĐẠT — đây là Phase A sạch nhất trong lô này.
- **Tên range (L4):** BCLX (move tăng) + phá **lên** = **Tái tích luỹ**. Đúng bảng L4. ĐẠT.
- **Không có nhãn ST[B]** — L6 đã được tuân thủ.
- **LPS[C] và LPS[D] đều là 1 điểm** — L7 đã được tuân thủ, và hai nhãn được phân vai đúng
  trước/sau SOS (không lặp lỗi kinh điển Ca #3 nguồn 4.pdf).
- **Không spam nhãn:** 6 nhãn cho 218 nến, không nhãn nào lặp.

## Cần hỏi người học
- Khi Phase E đã chốt (giá đã đi đủ chiều cao range), range có nên **đóng ngay tại nến đó** không,
  hay cố ý kéo dài Phase E tới lúc range kế tiếp mở? Hiện tại cách kéo dài làm Phase E thành phase
  dài nhất ở phần lớn bài, phá vỡ luật tỉ lệ phase (L9).
