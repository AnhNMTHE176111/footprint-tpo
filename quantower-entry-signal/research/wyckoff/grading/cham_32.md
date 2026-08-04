# Chấm bài #32 — Tái phân phối (RE-DIST) · 2026-06-10 14:58 → 22:02 (364 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây theo cách này: cái được gọi là "Phase B 275 nến" chính là một **đợt giảm 50 giá**, và biên chính dưới nằm lọt giữa vùng giá. Đây là lỗi A của v5 tái diễn ở dạng dài hạn.

## Lỗi (nặng → nhẹ)

### 1. Climax không chặn được move — biên chính dưới nằm GIỮA vùng giá · luật vi phạm: L1 + lỗi A của v5
- **Thuật toán gắn:** mức climax = 4139.7 (14:58) làm biên chính dưới; range chạy tiếp 364 nến.
- **Đúng phải là:** giá **không hề dừng** ở 4139.7. Nó phá xuống 4135.9 ngay tại ST[A] (15:19), rồi 4131.5 (mSOW 15:48), rồi 4126.6 (mSOW 17:50), rồi trôi tiếp xuống **4107.4** ở SOW và cuối cùng ~4060 trong Phase E. Tổng cộng giá đi thêm **~80 giá dưới mức climax**, gấp **4 lần** chiều cao biên chính (19.5 giá). Một cây climax bị vượt như vậy **không chặn được move** → theo L1 range này không hợp lệ; đúng ra phải bỏ ứng viên và mở range mới ở một cây climax thật phía dưới.
- **Dấu hiệu quyết định trên chart:** đường liền `bien CHINH duoi 4139.7` chạy ngang giữa khung, và **từ khoảng 18:15 tới hết range toàn bộ nến nằm dưới nó** — không còn một nến nào chạm lại. Nửa phải ảnh là một kênh giảm rõ ràng, không phải vùng cân bằng.
- **Nghi phạm trong thuật toán:** guard "climax không chặn được move: vượt hẳn quá 3× biên độ TB" chỉ chạy **trong cửa sổ cụm 8 nến** (mục 4.0). Sau khi Phase A đã chốt thì không còn phép kiểm nào tương tự. Cần thêm guard chạy suốt vòng đời range: nếu giá đóng cửa vượt mức climax quá k× chiều cao biên chính mà vẫn chưa có SOS/SOW → huỷ range hoặc tái sinh range mới.

### 2. Phase B 275 nến là một xu hướng giảm, không phải giai đoạn cân bằng · luật vi phạm: L9 + THEORY §2.3 (giai đoạn đi ngang vs giai đoạn xu hướng)
- **Thuật toán gắn:** Phase B = 15:20 → 19:54, 275 nến, "quan hệ nỗ lực ↔ kết quả".
- **Đúng phải là:** trong 275 nến đó giá đi từ ~4160 xuống ~4110 = **giảm 50 giá**, tức 2.5× chiều cao biên chính, với đỉnh sau luôn thấp hơn đỉnh trước. Phase B theo L9 là đoạn cung/cầu đỡ nhau trong một vùng; đây là **Phase E của một cấu trúc khác**. Bài học Ca #20 nguồn 7.pdf (giảng viên phê "gượng ép") áp trực tiếp: khi phải nhét 275 nến xu hướng vào ô "Phase B" thì phải nghi lại toàn bộ cách đọc.
- **Dấu hiệu quyết định trên chart:** hai nhãn mSOW cách nhau 2 giờ và **mSOW thứ hai thấp hơn mSOW thứ nhất 4.9 giá**, đúng mô tả "đáy mới thấp hơn đáy cũ" của một downtrend.
- **Nghi phạm trong thuật toán:** cùng nghi phạm lỗi 1 — không có guard nào cho phép **kết thúc hoặc cắt** một range mà giá đã bỏ đi hẳn khỏi vùng.

### 3. Nhãn SOW chậm ~90 nến so với cú phá thật · luật vi phạm: L3 + lỗi B của v5 (chưa vá xong cho cú phá trôi chậm)
- **Thuật toán gắn:** SOW tại 19:55, giá 4107.4, VSA 2.60x; Phase D dài **đúng 1 nến**.
- **Đúng phải là:** biên phụ dưới là 4126.6 (17:50). Giá đóng cửa hẳn dưới 4126.6 và không quay lại từ khoảng **18:15–18:30** — đó là mốc SOW. Đến 19:55 giá đã ở **19 giá dưới biên phụ**, nghĩa là nhãn "dấu hiệu yếu kém" được dán khi thị trường đã yếu xong từ lâu.
- **Dấu hiệu quyết định trên chart:** vạch Phase D nằm sát bên phải, sau khi đường giá đã rời hẳn đường `bien phu duoi 4126.6` một đoạn dài; toàn bộ đoạn 18:15→19:55 bị đếm vào Phase B.
- **Nghi phạm trong thuật toán:** điều kiện phá thật nhánh nhanh cần "**3 nến liên tiếp** đóng cửa vượt biên phụ thêm ≥30 tick với thân ≥45%" — một cú trôi dốc thoải trên M1 gần như không bao giờ thoả, nên phải rơi xuống nhánh chậm "40 nến **và** ≥60% nến đóng ngoài biên", và nhãn hồi tố chọn VSA cao nhất trong **cả đoạn dài đó** nên trúng sai cây. Cần thêm nhánh: khi giá đã đi quá 1× chiều cao range ngoài biên phụ thì chốt SOS/SOW ngay và neo hồi tố về nến **đầu tiên** đóng cửa vượt biên phụ mà không còn bị lấy lại.

### 4. Phase D = 1 nến, không có LPSY[D], thiếu hẳn Phase C · luật vi phạm: L10 + L8
- **Thuật toán gắn:** dải phase A(22) → B(275) → **D(1)** → E(67). Không có Phase C, không có nhãn retest nào.
- **Đúng phải là:** L10 định nghĩa D + E chính là CBR — **phá biên → hồi retest → giữ ngoài biên**. Phase D dài 1 nến nghĩa là không có nhịp retest nào được nhận diện, tức phần "CBR" của cấu trúc trống rỗng. Và như bài #31, có Phase D thì L8 buộc phải gán ngược Phase C.
- **Dấu hiệu quyết định trên chart:** hai vạch tím Phase D và Phase E dính liền nhau ở 19:55, nhãn chồng lên nhau — nhìn ảnh gần như không phân biệt được.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của lỗi 3 — vì SOW bắn muộn, nhịp retest thật (nếu có) đã nằm lại trong Phase B; LPS[D] là "swing pivot ngược hướng phá đầu tiên", mà sau 19:55 giá đi thẳng nên không tìm được pivot trong 25 nến chờ.

### 5. Chỉ số nỗ lực/kết quả gọi "volume nhiều" khi effort chỉ 0.94x · lỗi ĐO LƯỜNG (chỉ số v6)
- **Thuật toán gắn:** nhịp 17:28, effort (VSA TB) = **0.94x**, result = 0.20, er = 4.79 → "vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** effort 0.94x là volume **dưới trung bình** — không có "nỗ lực lớn" nào ở đây, er cao chỉ vì mẫu số result = 0.20 quá nhỏ. Đúng THEORY §2.2, effort/result chỉ có nghĩa khi **nỗ lực thật sự đáng kể**. Đối chiếu ngang lô: cùng một câu diễn giải được in cho er = 0.63 (#30), 0.61 (#31), 4.79 (#32), 0.24 (#34) → chuỗi mô tả là hằng số, không phản ánh số đo.
- **Nghi phạm trong thuật toán:** (a) chuỗi diễn giải tĩnh, không phân nhánh theo er; (b) thiếu **sàn effort** (đề xuất ≥1.5x) trước khi cho một nhịp lọt vào ô "nghi vấn hấp thụ".

## Đạt
- **Mục 1 (một phần):** MOVE trước climax là thật — 53.1 giá / 65 nến / hiệu suất 0.37, đọc rõ trên ảnh (đợt rơi từ 4200 xuống 4140). Điều kiện CẦN của L1 thoả; chỉ phần "climax chặn được move" là sai.
- **Cơ chế tách nhãn/mức climax hoạt động đúng ý:** nhãn SC đặt ở cây volume cao nhất cụm (14:56, VSA 3.83x, 969 lot) trong khi mức biên lấy đáy cụm — đúng cơ chế mới, không tính là lỗi.
- **Mục 4 (tên range):** origin SC + phá thật xuống = **Tái phân phối** — tên gọi khớp L4 và khớp diễn biến; đây là điểm hiếm hoi bài này làm đúng.
- **Mục 3 (một phần):** mỗi bên tối đa 1 biên phụ được tôn trọng (biên phụ dưới nới từ 4131.5 lên 4126.6, cú cũ biến mất); biên chính không bị kéo theo giá.
- **Trình bày:** panel volume cho thấy đúng các cột vàng VSA ≥ 2.2x tại 15:48 và 17:50 khớp với hai nhãn mSOW.

## Cần hỏi người học
- Khi giá đã bỏ đi hẳn khỏi range (ở đây 80 giá dưới mức climax) mà chưa có SOS/SOW xác nhận: nên **huỷ** range đó, hay nên **đóng ở trạng thái chưa rõ** rồi mở range mới từ cây climax kế tiếp? Cơ chế `superseded` mới đã có sẵn, nhưng ca này không kích hoạt nó.
