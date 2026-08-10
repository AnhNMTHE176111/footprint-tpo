# Chấm bài #34 — Phân phối (DIST) · 2026-06-10 06:08 → 08:02 (114 nến M1)

**Điểm: 4/10** — hướng đọc đúng (phân phối sau cú tăng, rồi sụp thật), nhưng ranh giới Phase B/C đảo ngược hoàn toàn và cú SOW chỉ phá biên phụ 3 tick.

## Lỗi (nặng → nhẹ)

### 1. Phase C dài nhất, Phase B ngắn thứ nhì — luật vi phạm: L8 + L9
- **Thuật toán gắn:** A=20n, **B=9n**, **C=33n**, D=25n, E=28n.
- **Đúng phải là:** B dài nhất, C ngắn nhất. Ở đây C dài gấp gần 4 lần B — đảo ngược hẳn. Thực chất 33 nến 06:37→07:09 là giai đoạn xây nguyên nhân (giá trôi ngang 4228-4236 với đỉnh thấp dần) = **Phase B**; Phase C thật chỉ là nhịp hồi nhỏ cuối cùng quanh 07:05-07:09 ngay trước SOW.
- **Dấu hiệu quyết định trên chart:** trong "Phase C" 33 nến đó có tới 25 nến đi ngang bám biên phụ dưới 4228.6 — không có cú shock nào, mà Phase C theo L8 phải là **tín hiệu đầu tiên** chứ không phải một vùng lê thê.
- **Nghi phạm trong thuật toán:** Phase C = [nến LPSY[C] … nến trước SOS/SOW], và LPSY[C] lấy ứng viên **đầu tiên** sau ST[A] (06:37, ngay sát ST[A] 06:27). Sửa: lấy ứng viên C **cuối cùng** trước break (đúng L8 "có Phase D rồi mới xác định được Phase C"), phần còn lại trả về Phase B.

### 2. SOW chỉ đóng cửa qua biên phụ 3 tick — luật vi phạm: L3
- **Thuật toán gắn:** SOW 07:10 @**4228.3**, biên phụ dưới **4228.6** → vượt đúng **0.3 giá**.
- **Đúng phải là:** "SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua biên PHỤ". Vượt 3 tick trên một biên phụ rộng 16.9 giá là vượt trong sai số, không phải bứt phá. Cây SOW này còn chỉ có VSA 1.69x — thấp hơn cả mSOW 06:44 (2.42x).
- **Dấu hiệu quyết định trên chart:** đường đứt cam 4228.6 và marker SOW gần như chồng lên nhau; phải tới 07:35 (Phase E) giá mới thực sự rời vùng.
- **Nghi phạm trong thuật toán:** đệm "biên chính ± 30 tick" được áp cho biên **chính** (4231.1 − 3.0 = 4228.1) nên 4228.3 lọt qua, nhưng lại **không** áp đệm khi so với biên **phụ** đã nới (4228.6). Phải áp cùng một đệm cho mốc thực tế xa nhất, tức max(biên chính+đệm, biên phụ+đệm).

### 3. mSOW ghi Phase B nhưng thời điểm nằm trong Phase C — lỗi nhất quán nội bộ
- **Thuật toán gắn:** `mSOW | 06:44 | 4228.6 | **Phase B**` trong khi bảng phase ghi Phase C = 06:37→07:09.
- **Đúng phải là:** trường phase của sự kiện phải suy ra từ mốc thời gian, không được gán độc lập.
- **Nghi phạm trong thuật toán:** nhãn mSOW được gán trong lượt quét Phase B rồi ranh giới phase bị dịch về sau (do lỗi #1) mà không gán lại phase cho các nhãn đã tạo. Cần một bước re-assign phase cho toàn bộ event sau khi chốt ranh giới.

### 4. ST[A] vừa đủ qua ngưỡng nhưng không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 06:27 @4239.2; BCLX 4245.5, AR 4231.1, biên 14.4 giá → hồi **56%**, sát mép ngưỡng 0.55.
- **Đúng phải là:** ST[A] phải quay lại **vùng BCLX**. 4239.2 còn cách đỉnh climax 6.3 giá = 44% biên độ range — chưa chạm vùng climax.
- **Nghi phạm trong thuật toán:** cùng gốc với bài #33 — `STA_MIN_AR_FRAC=0.55` quá lỏng. Đề nghị đổi sang điều kiện tuyệt đối "cách mức climax ≤ k tick".

### 5. LPSY[C] đặt ở nửa DƯỚI range trong một cấu trúc phân phối — luật vi phạm: L8 (vai trò nhãn)
- **Thuật toán gắn:** LPSY[C] 06:37 @4235.2, gần biên dưới hơn biên trên.
- **Đúng phải là:** trong phân phối, tín hiệu Phase C là cú test **nguồn cầu ở biên trên** (UTAD hoặc một nhịp hồi thất bại sát kháng cự). Một điểm nằm dưới trung điểm range thì đó là hành vi SOW, không phải LPSY[C].

## Đạt
- Điều kiện mở range (L1) đạt: MOVE tăng 38.0 giá / 83 nến bị chặn tại 06:08 với VSA **2.77x** — và nến climax **chính là nến neo range**, high 4245.5 đúng là cực trị của cả đợt tăng. Nhãn cụm climax không lệch ở bài này.
- Tên range đúng L4: MOVE tăng → BCLX → phá xuống = Phân phối.
- Biên chính = climax + AR, cố định, không kéo theo giá; biên phụ dưới 4228.6 đúng là cực trị xa nhất phe bán tạo ra, mỗi bên tối đa 1 (tỷ lệ 1.17x hợp lý).
- LPSY[D] 07:16 @4225.9 nằm **ngoài** biên và giữ được → đúng L10, và Phase E sau đó giá rơi thẳng về 4180: cấu trúc CBR thành công thật.
- Có ghi nhận mSOW ở Phase B (dấu hiệu yếu kém sớm) — đúng §5 THEORY (test ở đáy trong phân phối = dấu hiệu yếu kém).
