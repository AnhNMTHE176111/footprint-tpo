# Chấm bài #34 — Tích luỹ (ACC) · 2026-06-15 12:18 → 15:40 (202 nến M1)

**Điểm: 3/10** — Không nên vẽ range ở đây: đây là một cú **đảo chiều V rồi đi luôn**, không có vùng đấu giá. Phase B chỉ 8 nến — phase ngắn nhất, vi phạm trực tiếp L9.

## Lỗi (nặng → nhẹ)

### 1. Phase B là phase NGẮN NHẤT (8 nến) · luật vi phạm: L9
- **Thuật toán gắn:** A = 49 nến · **B = 8 nến** · D = 25 · E = 121. Không có C.
- **Đúng phải là:** L9 nói Phase B là phase **dài nhất** — nó là nơi xây "nguyên nhân". Ở đây B ngắn hơn A **6 lần** và ngắn hơn E **15 lần**. Với B chỉ 8 nến thì không tồn tại giai đoạn cung/cầu đỡ nhau nào; nghĩa là **chưa có nguyên nhân nào được xây**, và theo luật Nhân–Quả (THEORY §2.2) không thể mong một kết quả — điều này khớp với việc cú phá sau đó thất bại (xem lỗi 4).
- **Dấu hiệu quyết định trên chart:** hai vạch tím Phase B và Phase D nằm sát nhau, nhãn `Phase B (8n)` và `Phase D (25n)` chồng lấn nhau ở khu 13:07–13:15; cả "range" chỉ là một cột hẹp bên trái khung, còn 3/4 khung phải là đợt tăng đã rời range.
- **Nghi phạm trong thuật toán:** gốc rễ nằm ở AR/ST[A] (lỗi 2) — Phase A ăn hết 49 nến nên phần còn lại trước cú phá chỉ còn 8 nến. Cần một guard tỉ lệ: nếu độ dài Phase B < độ dài Phase A thì range **chưa đủ hình**, không được cho phép chốt SOS/SOW và đặt tên pattern.

### 2. "AR" thực chất là cả một leg tăng 37 nến, không phải phản ứng tự động · luật vi phạm: L1/L2 + THEORY §3.3 (định nghĩa AR)
- **Thuật toán gắn:** AR = 4370.8 tại **12:57**, tức 37 nến sau mức climax 12:18.
- **Đúng phải là:** AR theo định nghĩa gốc là "sóng mua do áp lực bán giảm mạnh, phần lớn là short chốt lời" — một **phản ứng** ngắn. Nhìn ảnh, từ 12:20 tới 12:57 giá tăng **liên tục, gần như không nghỉ** từ 4345 lên 4371, tức +25.5 giá = **lớn hơn cả MOVE giảm trước climax (20.2 giá)**. Một nhịp bật lớn hơn move nó phản ứng lại thì đó là **leg xu hướng mới**, không phải AR. Kết luận: cây climax 12:18 không mở ra vùng cân bằng, nó mở ra một đợt tăng — theo L1 đây không phải range.
- **Dấu hiệu quyết định trên chart:** mũi xám MOVE (20.2 giá, hiệu suất 0.51) ngắn hơn hẳn đoạn nến xanh liền mạch từ SC lên AR; và trước MOVE đó, cả khung 11:17–12:07 là giá **đi ngang** 4352–4372 — tức MOVE 20.2 giá này chỉ là chân cuối của một vùng đi ngang, không phải xu hướng giảm thật.
- **Nghi phạm trong thuật toán:** ngưỡng MOVE `≥ 20 nến và ≥ 8× biên độ TB, hiệu suất ≥ 0.35` quá lỏng ở phiên biên độ nhỏ: 20.2 giá/36 nến thoả về số nhưng bối cảnh là đi ngang. Thêm nữa mục 4.1 không đặt **trần** cho độ dài/biên độ của AR — cần điều kiện AR ≤ khoảng 1× độ dài MOVE, vượt thì bỏ ứng viên (giá đang đi tiếp, không cân bằng).

### 3. Thiếu hẳn Phase C dù đã có Phase D · luật vi phạm: L8
- **Thuật toán gắn:** dải phase A → B → **D** → E; không có LPS[C].
- **Đúng phải là:** L8 buộc "có Phase D rồi mới xác định được Phase C" — có SOS thì phải gán ngược LPS[C]. Ứng viên rõ trên ảnh là đáy **ST[A] 4362.8 (13:06)** hoặc nhịp nén 13:07–13:14 ngay trước cây SOS.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược = `min(60 nến, 1/2 độ dài Phase B)` = min(60, **4**) = 4 nến, mà xác nhận swing pivot cần 5 nến không tạo cực trị mới → **về mặt số học không bao giờ gán được** khi Phase B < 10 nến. Đây là lỗi hàng rào cứng, không phải lỗi chọn điểm. Đó cũng là lý do 3/5 bài trong lô (31, 32, 34) đều thiếu Phase C.

### 4. Range được đóng `completed` và đặt tên "Tích luỹ" trong khi cú phá thất bại · luật vi phạm: L10 + THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** SOS 13:15 (4373.8) → LPS[D] 13:33 → Phase E 121 nến → `completed`, tên **Tích luỹ (ACC)**.
- **Đúng phải là:** đích Phase E là +1.0× chiều cao = 4370.8 + 25.5 = **4396.3**. Giá cao nhất chỉ tới ~4391 rồi thoái lui suốt 2 tiếng, và tới cuối khung (~16:17) **rơi về ~4358 — dưới cả biên chính trên 4370.8**, tức thu hẳn trở lại vào trong range. Phase E chốt vì **hết trần 120 nến**, không vì đạt đích. Theo THEORY §9, giá không đến được mục tiêu rồi quay đầu = **cấu trúc thất bại**; theo L10 thì "giá thuận lực đi tìm vùng giá mới" đã không xảy ra. Đúng ra: hạ SOS thành mSOS, trả phase về B, **không đặt tên pattern**.
- **Dấu hiệu quyết định trên chart:** nửa phải ảnh, sau đỉnh 4391 là chuỗi đỉnh thấp dần 4386 → 4381 → 4379, và cây đỏ cuối cùng xuyên xuống dưới đường `bien CHINH tren 4370.8` rồi đóng ở ~4360.
- **Nghi phạm trong thuật toán:** Phase E hết 120 nến thì chốt vô điều kiện (mục 7, lỗi J) — không kiểm lại "đã đạt bao nhiêu phần đích" tại thời điểm hết hạn, và cơ chế vô hiệu hoá cú phá (lỗi F) chỉ chạy trong cửa sổ 25 nến của Phase D, không chạy trong Phase E.

### 5. LPS[D] không phải nhịp retest biên · luật vi phạm: L10
- **Thuật toán gắn:** LPS[D] = 4378.4 (13:33), VSA 1.67x.
- **Đúng phải là:** LPS[D] trong CBR là nhịp hồi **về gần biên vừa phá** để chứng minh giữ được ở ngoài. 4378.4 cao hơn biên phụ trên 4371.5 tới **6.9 giá = 27% chiều cao range** và còn cao hơn cả chính điểm SOS (4373.8) — nó chỉ là một pullback giữa lưng đợt tăng, không test gì cả.
- **Dấu hiệu quyết định trên chart:** nhãn LPS[D] nằm lơ lửng phía trên hai đường biên, cách hẳn chúng; nhịp thật sự về sát biên phụ chỉ xảy ra mãi ~14:57 (đáy ~4372), đã ngoài Phase D.
- **Nghi phạm trong thuật toán:** LPS[D] định nghĩa là "swing pivot ngược hướng phá đầu tiên, nhịp hồi ≥ 1.5× biên độ TB" — thuần cấu trúc, **không có điều kiện khoảng cách tới biên**. Cần thêm: pivot phải nằm trong x% chiều cao range tính từ biên vừa phá, nếu không thì Phase D chưa hoàn tất.

### 6. Nhịp nỗ lực/kết quả lấy nến NGOÀI Phase B + diễn giải ngược dấu · lỗi ĐO LƯỜNG (chỉ số v6)
- **Thuật toán gắn:** "Nhịp nỗ lực/kết quả cao nhất **trong Phase B**: nến 62854..62862 (**13:15**), effort 1.27x, result 5.26, er 0.24 — vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** hai lỗi cùng lúc. (a) Phase B kết thúc **13:14**, nến 13:15 chính là cây SOS — nhịp được báo "trong Phase B" nằm hẳn ngoài Phase B; nhịp dài 9 nến trong khi Phase B chỉ 8 nến nên cửa sổ trượt tràn sang phải. (b) er = 0.24 với result 5.26 ATR là **nỗ lực ít, kết quả rất lớn** — dấu hiệu SỨC MẠNH (THEORY §6.3: nguồn cung nổi thấp nên không cần volume cao), **ngược hoàn toàn** với "volume nhiều, kết quả ít". Đối chiếu cả lô: er = 0.63 / 0.61 / 4.79 / 0.24 đều in **cùng một câu** → chuỗi diễn giải là hằng số.
- **Nghi phạm trong thuật toán:** (a) vòng lặp nhịp effort/result không kẹp `end` vào nến cuối Phase B; (b) chuỗi mô tả tĩnh, thiếu phân nhánh theo er và thiếu sàn effort.

## Đạt
- **Mục 3 (biên):** biên chính = climax 4345.3 + AR 4370.8, cố định; đúng một biên phụ trên 4371.5; tỉ lệ 1.03x.
- **Chọn nhãn SC hợp lý:** mức climax lấy đáy 12:18 (4345.3), nhãn SC đặt ở 12:20 — nến VSA 3.20x, thân 0.24, doji ngay tại đáy, tức **cây hấp thụ** đúng bản chất cao trào bán; lệch nhãn/mức chỉ 0.3 giá nên không gây lệch đọc trên chart. Cơ chế mới dùng đúng ở ca này.
- **Mục 8 (một phần):** cây SOS 13:15 có VSA 3.57x, thân 0.58 — cột vàng cao nhất khu vực trên panel volume, nhãn neo đúng cây phá (lỗi B của v5 đã vá tốt ở bài này).
- **Mục 4 (tên range, có điều kiện):** nếu chấp nhận cú phá là thật thì origin SC + phá lên = **Tích luỹ**, khớp bảng L4.
- **Bias = +1** ("chạm nổi biên trên, không nổi biên dưới") — đo **đúng** ở bài này: đáy 4345.3 chỉ chạm đúng một lần tại climax rồi giá không bao giờ về lại, còn biên trên bị phá. Đây là ca chỉ số bias phản ánh đúng bản chất.

## Cần hỏi người học
- Một cú đảo chiều V (rơi 20 giá → bật 25 giá liền mạch → đi tiếp) có được coi là mở range không? Theo L1 thì "climax chặn move" đã thoả về câu chữ, nhưng không có giai đoạn cân bằng nào (THEORY §2.3 giai đoạn 3). Nếu câu trả lời là "không" thì cần thêm điều kiện trần cho AR như đề xuất ở lỗi 2, và điều đó sẽ loại luôn nhiều range dạng này trên M1.
