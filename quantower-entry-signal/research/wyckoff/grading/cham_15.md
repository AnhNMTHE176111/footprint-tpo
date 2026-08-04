# Chấm bài #15 — Phân phối (DIST) · 2026-05-14 04:36 → 14:01 (352 nến M1)

**Điểm: 3/10** — Khung range đọc được (vùng 4735–4753 có 287 nến đấu giá thật, biên hai đầu được tôn trọng nhiều lần), nhưng cây climax không phải climax và cú phá xuống đã **hỏng ngay** mà range vẫn được đặt tên "Phân phối".

## Lỗi (nặng → nhẹ)

### 1. BCLX VSA 0.91x, volume 4 hợp đồng, biên độ 1.8 giá — không phải cao trào mua — luật vi phạm: L1 + §4.1 THEORY (BCLX)
- **Thuật toán gắn:** BCLX 04:36 tại 4753.0, VSA **0.91x**, volume **4**, biên độ 1.8 giá.
- **Đúng phải là:** BCLX cần "volume + spread tăng rõ rệt". Cây này volume dưới trung bình. Trong 12 nến quanh climax, cây -3 (04:32) có VSA 2.33x và biên độ 5.0 giá — đó là cây gần "cao trào" nhất, và nó cách climax 4 nến (trong cửa sổ cụm 8 nến).
- **Dấu hiệu quyết định trên chart:** trên panel volume, hai cột vàng cao nhất của đoạn Phase A nằm ở khoảng 03:19–04:21, **trái** nhãn BCLX; ngay dưới nhãn BCLX không có cột nào đáng kể.
- **Nghi phạm trong thuật toán:** cùng lỗi với bài #12 — sau khi dời mốc climax theo cực trị giá (mục 4.0), **không kiểm lại** VSA ≥2.2× và biên độ ≥1.4× TB ở cây mới. Ba trong năm bài của lô này có climax VSA < 2.2× (0.58x, 0.91x, 1.51x), tức đây là lỗi hệ thống, không phải ca lẻ.

### 2. Cú phá xuống HỎNG ngay sau SOW mà range vẫn được đặt tên "Phân phối" — luật vi phạm: L10 + lỗi hệ thống F v4
- **Thuật toán gắn:** SOW 13:36 tại 4722.7 → LPSY[D] 13:50 tại 4731.4 → Phase E (7 nến) → đóng range, tên "Phân phối (DIST)".
- **Đúng phải là:** nhìn ảnh, sau SOW giá xuống 4706 rồi **bật thẳng lên 4757** — vượt qua cả biên chính trên 4735.0 và cả biên phụ trên. Đó là cú phá xuống **thất bại hoàn toàn**, đúng nghĩa "Failed Structure" §9 THEORY. Range không được gọi là Phân phối; theo mục 5.1 nó phải bị hạ cấp thành **mSOW**, dải phase trả về B.
- **Dấu hiệu quyết định trên chart:** cụm nến sau LPSY[D] tăng liên tục lên tận 4757 (đọc trên trục giá phải: đỉnh gần 14:08 vượt mức 4753). Range "phân phối" mà giá kết thúc **cao hơn cả mức BCLX** — tự phủ định.
- **Nghi phạm trong thuật toán:** mục 7 — "Dù Phase E có đạt hay không, range vẫn ĐÓNG tại đây". Đúng để tránh vòng lặp, nhưng nó khiến máy **đặt tên** cho một cấu trúc mà cú phá đã bị đảo. Cần tách: đóng range thì được, nhưng chỉ đặt tên khi Phase E đạt ≥50% mục tiêu **và** giá không quay lại vượt biên đối diện.

### 3. SOW VSA 1.07x — luật vi phạm: mục 8 (Effort vs Result) + §4.1 THEORY (SOW = volume tăng)
- **Thuật toán gắn:** SOW 13:36 tại 4722.7, VSA **1.07x**, thân 0.79.
- **Đúng phải là:** SOW theo định nghĩa gốc kèm "chênh lệch/khối lượng tăng". 1.07x là volume trung bình. Trong đoạn 13:31–13:44 panel volume có nhiều cột vàng (VSA ≥2.2x) — nhãn phải rơi vào cây cao nhất trong số đó. Cùng lỗi neo với bài #13 (SOS 0.62x).
- **Nghi phạm trong thuật toán:** nhánh hồi tố lỗi B chưa chạy trên đường đi này.

### 4. LPSY[C] 4737.7 nằm **trong** range, không phải ở biên trên — luật vi phạm: §4.1 THEORY (LPSY) + L8
- **Thuật toán gắn:** LPSY[C] 13:26 tại 4737.7 — chỉ cao hơn biên chính dưới 4735.0 đúng **2.7 giá**, tức ở **15% chiều cao range** tính từ đáy.
- **Đúng phải là:** LPSY là "đợt phục hồi yếu trên biên hẹp, nguồn cầu cạn kiệt, đợt bán cuối của CO" — nó phải nằm ở **nửa trên** range, gần kháng cự. Một điểm sát biên dưới không phải "điểm cung cuối cùng", nó chỉ là cây trước khi phá.
- **Nghi phạm trong thuật toán:** mục 6 case khó lấy "đỉnh cao nhất trong 60 nến trước cú phá" — nhưng 60 nến trước cú phá này giá đã rơi từ 4750 về 4735, nên "đỉnh cao nhất" của một đoạn rơi lại nằm sát đáy. Cần chặn: LPSY[C] phải ở nửa trên range (với phân phối) mới được nhận nhãn, nếu không thì bỏ Phase C, để range ở case "không có Phase C".

### 5. mSOW 4728.8 VSA 2.67x đặt biên phụ dưới, rồi chính SOW chỉ vượt biên phụ đó 6.1 giá — luật vi phạm: L3 (mức độ)
- **Thuật toán gắn:** mSOW 06:02 tại 4728.8 (VSA 2.67x, thân 0.96) → biên phụ dưới 4728.8; SOW sau đó ở 4722.7.
- **Đúng phải là:** mSOW này hợp lệ (VSA 2.67x, thân 0.96 — một thế lực thật cố phá), việc nó tạo biên phụ là đúng L3. Nhưng SOW chỉ vượt nó 6.1 giá = **34% chiều cao range** trước khi bị đảo. Theo L3, "SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua biên phụ" — vượt 6.1 giá rồi bị đẩy về là bứt hụt.
- **Ghi chú:** đây là hệ quả của lỗi 2, ghi riêng để chỉ rõ chỗ đo.

### 6. AR VSA 4.17x nhưng đến ở nến thứ 54 sau climax, cách climax 18 giá — trình bày/cấu trúc biên giới
- **Thuật toán gắn:** AR 05:30 tại 4735.0, VSA 4.17x.
- **Đúng phải là:** AR có nỗ lực thật (4.17x) — điểm này **đạt**. Nhưng Phase A dài 30 nến trong khi AR ở nến thứ 54 kể từ climax (04:36 → 05:30, có khe nến) và ST[A] ở 05:48. Số nến Phase A (30) không khớp với khoảng thời gian 72 phút — dấu hiệu dữ liệu có khe. Cần kiểm mục K (cắt range ở khe > 4 giờ) có tính đúng nến hay tính đồng hồ.

## Đạt
- L1 phần move: move tăng 38.0 giá / 23 nến / **hiệu suất 0.86** — move xu hướng rõ nhất trong cả lô 5 bài, climax nằm ở đỉnh chặn move. Đúng.
- L2 Phase A đủ 3 lần đổi hướng, kết thúc tại ST[A] 05:48 (4743.3), ST[A] nằm giữa BCLX và AR. Đúng khuôn.
- AR có volume thật (4.17x) — khác 4 bài kia.
- L3 biên chính = mức climax (4753.0) + mức AR (4735.0), cố định suốt range, **không bị kéo theo giá**. Đúng. Đây là bài duy nhất trong lô mà biên chính giữ được vai trò: nhìn ảnh, giá tôn trọng cả hai đường liền nhiều lần trong 287 nến Phase B.
- L9/L8: B (287n) dài nhất, C (10n) ngắn nhất. Đúng tỉ lệ.
- Biên phụ mỗi bên đúng 1 cái (4728.8 dưới / 4757.7 trên), là cực trị xa nhất. Đúng L3.

## Cần hỏi người học
- (không có)
