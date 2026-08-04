# Chấm bài #11 — Tích luỹ (ACC) · 2026-05-04 15:22 → 2026-05-05 15:41 (660 nến M1)

**Điểm: 4/10** — Cấu trúc khung có lý (move giảm 52.1 giá hiệu suất 0.70 là move thật, climax chặn ở đáy), nhưng **hai biên chính đã mất hết vai trò từ giữa Phase B** và cụm nhãn cuối (LPS[C]/SOS/LPS[D]) bị nén vào 1 phút — sửa nhãn nặng.

## Lỗi (nặng → nhẹ)

### 1. Range đã bị bỏ lại phía sau từ 05-05 05:13, thuật toán vẫn giữ nguyên hai biên chính — luật vi phạm: L3 + mục 8 THEORY (huỷ range)
- **Thuật toán gắn:** biên chính 4559.8–4588.3 (28.5 giá), giữ nguyên tới tận 05-05 15:41; Phase B dài 477 nến.
- **Đúng phải là:** nhìn ảnh, từ khoảng 05-05 05:13 trở đi giá **đóng cửa hẳn trên biên chính trên 4588.3** và không quay lại nữa — nó bò lên 4604 → 4636 trong hơn 400 nến. Đó là **SOS thật**, xảy ra khoảng 05-05 05:00-07:00, không phải ở 12:10. Vùng đấu giá 4559.8–4588.3 đã chết từ đó; mọi thứ sau đó là **một xu hướng tăng**, không phải "Phase B của range cũ".
- **Dấu hiệu quyết định trên chart:** nến sau 05-05 05:13 nằm **toàn bộ** trên đường liền 4588.3; mSOS ghi tại 05-05 09:08 giá 4603.8 — tức máy tự thừa nhận giá đã ở ngoài biên chính 15.5 giá suốt nhiều giờ mà vẫn xếp là "Phase B".
- **Nghi phạm trong thuật toán:** nhánh Kết cục B (mục 5.1) yêu cầu 3 nến đóng vượt **biên PHỤ** (4603.8), không phải biên chính. Vì biên phụ trên bị mSOS đẩy lên đúng đỉnh mà giá cần vượt, điều kiện SOS tự khoá chính nó. Đây là vòng lặp logic: cú thăm dò tạo biên phụ → biên phụ chặn SOS → không có SOS → Phase B kéo dài vô hạn.

### 2. SOS neo sai chỗ, đặt sau khi cú phá đã xong 7 tiếng — luật vi phạm: L10 (D+E = CBR)
- **Thuật toán gắn:** SOS tại 05-05 12:10, giá 4607.1, VSA 4.36x.
- **Đúng phải là:** 4607.1 chỉ nhỉnh hơn mSOS 4603.8 đúng **3.3 giá**. Cú phá thật đã diễn ra sớm hơn nhiều. Nhãn SOS phải nằm ở cây bứt qua 4588.3 lần đầu tiên và giữ được (quanh 05-05 05:00), không phải ở một cây lẻ giữa xu hướng.
- **Dấu hiệu quyết định trên chart:** đoạn "Phase D (25n)" nằm ở nửa dốc lên của một đợt tăng đã chạy 40+ giá, không phải ở điểm gãy cấu trúc.
- **Nghi phạm trong thuật toán:** mục 5.1 lỗi B — đặt hồi tố vào cây VSA cao nhất, nhưng cây đó được chọn **trong đoạn 3 nến xác nhận** chứ không phải trong cả cú phá.

### 3. LPS[C] → SOS → LPS[D] gói trong 17 phút, LPS[D] chỉ cách SOS đúng 1 nến — luật vi phạm: L7 + L10
- **Thuật toán gắn:** LPS[C] 11:54 (4604.6), SOS 12:10 (4607.1), LPS[D] 12:11 (4603.5).
- **Đúng phải là:** LPS[D] là nhịp **retest sau khi phá** — phải có một nhịp hồi thật, không phải cây kế tiếp. LPS[D] ở 4603.5 lại **thấp hơn** LPS[C] ở 4604.6, tức "retest sau phá" nằm dưới "test trước phá". Vô nghĩa về vai.
- **Dấu hiệu quyết định trên chart:** 3 vạch tím dọc chồng lên nhau thành một cụm trong 17 phút; Phase C 11 nến / Phase D 25 nến.
- **Nghi phạm trong thuật toán:** mục 7, gom LPS[D] bằng sai số 20 tick quanh biên vừa phá, không yêu cầu khoảng cách tối thiểu 5 nến kể từ SOS (bảng tham số có "giãn cách tối thiểu 5 nến" nhưng rõ ràng không áp cho cặp SOS/LPS[D]).

### 4. Climax VSA 1.51x, trong khi cây ngay trước nó VSA 8.04x và 2.70x — luật vi phạm: mục 6.2 THEORY (Effort vs Result)
- **Thuật toán gắn:** SC tại 15:22, VSA 1.51x, volume 18.
- **Đúng phải là:** cây 15:19 có volume 76 / VSA **8.04x** và cây 15:21 volume 30 / VSA 2.70x — đó mới là cao trào bán. Cây 15:22 chỉ là cây cuối của cụm, nó cho **đáy thấp nhất** nhưng không phải cây "nỗ lực".
- **Dấu hiệu quyết định trên chart:** cột volume vàng cao vọt nằm lệch **trái** so với nhãn SC trên panel dưới.
- **Nghi phạm trong thuật toán:** mục 4.0 dời mốc climax theo **cực trị giá** trong 8 nến, không cân nhắc VSA. Nên chốt cụm climax = cây VSA cao nhất trong cụm, còn **mức biên** thì lấy cực trị của cụm (hai thứ tách nhau).

### 5. mSOW 4545.6 có VSA 0.78x vẫn được nới biên phụ — luật vi phạm: L3 (biên phụ = cực trị của một thế lực cố phá range)
- **Thuật toán gắn:** mSOW tại 16:10, 4545.6, VSA **0.78x**, thân 0.79.
- **Đúng phải là:** một cú thọc xuống 14.2 giá dưới biên chính với volume **dưới trung bình** không phải "một thế lực cố phá range" — đó là thanh khoản mỏng. Không nên nới biên phụ xuống 4545.6.
- **Nghi phạm trong thuật toán:** điều kiện "mạnh" ở mục 5.1 là **hoặc** sâu ≥15% chiều cao **hoặc** VSA ≥2.2×. Với range 28.5 giá thì 15% = 4.3 giá — quá dễ đạt. Nên đổi thành **VÀ**, hoặc ít nhất chặn VSA < 1.0×.

## Đạt
- L1 mở range: move giảm 52.1 giá / 32 nến / hiệu suất 0.70 — move thật, climax nằm ở đáy chặn move. Đúng.
- L2 Phase A đủ 3 lần đổi hướng, kết thúc tại ST[A] 15:51 (4556.0). Đúng khuôn.
- ST[A] 4556.0 nằm dưới mức climax 4559.8 → tạo biên phụ dưới. Đúng L3.
- L9 Phase B (477n) là phase dài nhất, L8 Phase C (11n) là phase ngắn nhất. Tỉ lệ phase đúng.
- Tên "Tích luỹ" khớp L4: origin SC + phá lên = ACC.

## Cần hỏi người học
- Khi giá đóng cửa hẳn ngoài **biên chính** hàng trăm nến nhưng chưa vượt **biên phụ**, có nên coi range đã chết (đóng ở trạng thái "chưa rõ") thay vì kéo Phase B tiếp không? Hiện luật L3 nói SOS "mạnh" cần vượt biên phụ, nhưng không nói phải làm gì khi giá đi ngoài biên chính mãi mà không chạm biên phụ.
