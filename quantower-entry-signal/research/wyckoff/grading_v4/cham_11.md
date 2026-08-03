# Chấm bài #11 — Tích luỹ (ACC) · 2026-05-07 16:18 → 2026-05-08 13:58 (623 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây theo cách này: cây gọi là SC không hề chặn được đợt giảm, nên cả hai biên chính đều đặt sai, và mọi nhãn phía sau kế thừa cái sai đó.

## Lỗi (nặng → nhẹ)

### 1. SC gán sai chỗ — giá đi tiếp 45 giá thấp hơn sau khi đã gọi SC — luật vi phạm: L1 (climax phải CHẶN move) + THEORY §3.3 (SC)
- **Thuật toán gắn:** SC tại 4753.2, 16:18, VSA 2.94x, coi đây là đáy chặn đợt giảm 57.1 giá.
- **Đúng phải là:** đợt giảm chưa hề bị chặn. Sau nến này giá còn rơi tiếp tới **4708.0 lúc 22:00** — thấp hơn "SC" **45.2 giá**, tức gấp **2.0 lần** cả chiều cao biên chính (22.7 giá). Cây climax thật nằm trong đoạn 17:25–19:52 (VSA 7.69x / 9.10x / **11.22x** — đều lớn hơn nhiều nến 2.94x được chọn).
- **Dấu hiệu quyết định trên chart:** đáy toàn range = 4708.0 @ 22:00; biên phụ dưới bị đẩy xuống 4708.0 nằm cách biên chính dưới 45 giá — bản thân con số đó đã tự tố rằng biên chính dưới không phải biên.
- **Nghi phạm trong thuật toán:** mục 3(2) chỉ kiểm nến climax là cực trị của **cửa sổ NHÌN LẠI 240 nến**, không có bất kỳ kiểm tra hướng về sau. Cần thêm điều kiện huỷ ứng viên nếu trong N nến kế tiếp giá tạo cực trị mới sâu hơn climax quá X (vd sâu hơn 30% độ dài move).

### 2. AR cách climax 278 nến — không còn là "lực đẩy tự động" — luật vi phạm: L2 + THEORY §3.3 (AR)
- **Thuật toán gắn:** AR tại 4775.9 lúc **02:03 hôm sau**, tức 278 nến (~10 giờ) sau climax.
- **Đúng phải là:** AR là sóng bật ngay sau khi áp lực bán tắt. Cú bật 4775.9 này xuất phát từ đáy 4708.0 lúc 22:00 chứ không từ 4753.2 — nó là AR của một cấu trúc khác, không phải của cây được gọi SC.
- **Dấu hiệu quyết định trên chart:** nến AR là nến đơn 4770.8 → 4775.9, VSA 2.08x, thân 1.00; nằm cuối một đợt hồi 68 giá kéo từ 22:00 tới 02:03.
- **Nghi phạm trong thuật toán:** mục 4.1 cho phép chờ AR tới **300 nến** và chỉ lấy cực trị phía đối diện. Trần 300 nến quá rộng cho M1: nó cho phép nối climax của phiên Mỹ với AR của phiên Á.

### 3. Phase A dài 292 nến — gấp 2.7 lần Phase B — luật vi phạm: L2, L9
- **Thuật toán gắn:** A = 292n, B = 108+1+14 = 123n, C = 2+121+60 = 183n.
- **Đúng phải là:** Phase A đúng ĐÚNG 3 lần đổi hướng (L2) và Phase B phải là phase dài nhất (L9). Đoạn 292 nến này chứa ít nhất 5 lần đổi hướng (xuống 4753 → xuống 4708 → lên 4775.9 → về 4753.5), tức đã bao trọn cả một cấu trúc khác vào trong "Phase A".
- **Dấu hiệu quyết định trên chart:** vạch tím Phase A trải hết nửa trái chart, che nguyên đoạn giá lao xuống 4708 rồi hồi 68 giá.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của lỗi 1 + 2; không có guard "Phase A không được dài hơn Phase B".

### 4. "Spring" xác nhận không phải đáy thấp nhất của TR — luật vi phạm: CHART_CASES lỗi chung #6 (2.pdf, 4/22 ca — lỗi lặp nhiều nhất của nguồn đó)
- **Thuật toán gắn:** Spring (confirmed) tại **4749.9**, 12:12.
- **Đúng phải là:** Spring bắt buộc là mức giá **thấp nhất trong suốt TR**. Ở đây đã có 4743.8 (07:25) và 4708.0 (22:00) thấp hơn → điểm 12:12 chỉ là một **LPS** thường, không phải Spring.
- **Dấu hiệu quyết định trên chart:** nến 12:12 = O4749.9 H4751.0 L4749.9 C4751.0, volume **4 lot**, VSA 2.00x — một nến 4 lot không rũ được ai.
- **Nghi phạm trong thuật toán:** nhánh phân loại ở mục 5.1 so điểm thò ra với **biên chính** chứ không so với **đáy thấp nhất từng có của range**. Thêm điều kiện `low < min(low toàn range trước đó)` là sửa được ngay.

### 5. Ba Phase C, trong đó một Phase C dài 121 nến — luật vi phạm: L8 (Phase C là phase NGẮN NHẤT)
- **Thuật toán gắn:** C(2n) → B(1n) → C(121n) → B(14n) → C(60n).
- **Đúng phải là:** một Phase C duy nhất, ngắn, ngay trước SOS. Phase C 121 nến là đúng trần chờ 120 nến rồi timeout — tức máy đã ngồi trong Phase C suốt 2 giờ mà không kết luận được gì; theo L8 thì đó tự động không còn là Phase C.
- **Dấu hiệu quyết định trên chart:** dải phase vụn thành 5 đoạn A-B-C-B-C-B-C-D-E, có đoạn Phase B dài **1 nến**.
- **Nghi phạm trong thuật toán:** vòng B⇄C ở mục 5/6 không giới hạn số lần quay lui. Cần: hoặc chốt 1 Phase C duy nhất (lấy cú rũ cuối cùng trước SOS, đúng cách 4.pdf chữa UTAD), hoặc cấm đoạn phase ngắn hơn ~5 nến.

### 6. Spring và Shakeout đặt cách nhau 3 nến, cả hai đều thất bại — luật vi phạm: L5 + tham số giãn cách 5 nến (mục 11)
- **Thuật toán gắn:** Spring (thất bại) 07:23 @4749.4 và Shakeout (thất bại) 07:26 @4745.7.
- **Đúng phải là:** một cú thăm dò duy nhất. Riêng nến 07:26 là **O=H=L=C=4745.7, volume 1 lot, VSA 0.29x** — gọi Shakeout cho nó là sai hẳn định nghĩa, vì Shakeout phải có biên độ/volume **lớn hơn** Spring (THEORY §3.5).
- **Dấu hiệu quyết định trên chart:** hai nhãn chồng đè nhau ngay dưới biên chính dưới, cùng một cụm nến.
- **Nghi phạm trong thuật toán:** tham số "giãn cách tối thiểu 5 nến giữa 2 sự kiện" không được áp cho nhãn cú rũ; và nhánh Shakeout không kiểm điều kiện volume/biên độ, chỉ kiểm thời gian quay về.

### 7. Nền volume quá mỏng để VSA có nghĩa — cảm nhận cá nhân, không có luật chống lưng (nhưng đo được)
- Toàn bộ nhãn của bài này đứng trên nến **1–9 lot**. VSA = tỉ số của hai số rất nhỏ nên vọt lên 2–3x rất dễ. Đề nghị thêm **sàn khối lượng tuyệt đối** trước khi cho phép gọi climax/SOS/Spring.

## Đạt
- Nhận đúng có một MOVE giảm thật trước đó (57.1 giá / 69 nến / hiệu suất 0.49) — điều kiện CẦN của L1 thoả.
- SOS 13:30 làm đúng bài: VSA 4.66x, thân 1.00, đóng cửa **4780.7 = đúng mức biên phụ trên** → thoả yêu cầu L3 "SOS phải bứt qua biên phụ".
- ST[A] 02:39 đọc đúng tinh thần test: VSA 0.45x, co lại rõ so với AR 2.08x.
- Không vẽ vùng cho LPS[C], chỉ 1 điểm — đúng L7.
- Tên range (Tích luỹ = SC + phá lên) khớp L4.

## Cần hỏi người học
- Khi phát hiện climax bị "phá hậu kỳ" (giá tạo cực trị mới sâu hơn climax như ca này), anh muốn máy **huỷ ứng viên** hay **dời climax xuống cực trị mới rồi tính lại Phase A**? Hai cách cho ra range rất khác nhau và lý thuyết không phân xử.
