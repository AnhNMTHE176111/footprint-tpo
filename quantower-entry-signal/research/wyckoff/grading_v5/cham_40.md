# Chấm bài #40 — Chưa rõ (BCLX) (DIST?) · 2026-07-14 12:33 → 07-15 01:48 (735 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây. Climax gắn vào cây **thứ tư** sau cây tin thật (bỏ qua một cây VSA 14.64× / biên độ 62 giá), và bài có một lỗi thứ tự thời gian không thể biện hộ: **LPSY[D] được gắn trước LPSY[C] 6 tiếng rưỡi**, trong khi timeline không có đoạn Phase D nào ở chỗ đó.

## Lỗi (nặng → nhẹ)

### 1. LPSY[D] gắn TRƯỚC LPSY[C] 6,5 giờ, ngoài mọi dải Phase D — luật vi phạm: L7, L10, và Ca #3 nguồn 4.pdf
- **Thuật toán gắn:** LPSY[D] tại **07-14 19:00** (giá 4061.5, phase ghi "D") · LPSY[C] tại **07-15 01:29** (giá 4063.1, phase "C"). Bảng phase: B = 13:02 → 07-15 01:28 · C = 01:29 → 01:47 · D = 01:48 (1 nến).
- **Đúng phải là:** LPSY[D] theo định nghĩa là nhịp hồi retest **SAU** SOW (L10, và phân biệt LPS[C]/LPS[D] ở mục 7 spec). Ở đây nó nằm **trước** LPSY[C] và nằm **giữa dải Phase B** — chỗ 19:00 timeline ghi là Phase B, không phải D. Range này còn **chưa có SOW nào cả** (chỉ có 2 nhãn mSOW), nên LPSY[D] về nguyên tắc **không được phép tồn tại**. Phải xoá hẳn nhãn này.
- **Dấu hiệu quyết định trên chart:** đọc trực tiếp bảng sự kiện — LPSY[D] 07-14 19:00 xuất hiện ở dòng **trước** mSOW 23:17 và LPSY[C] 01:29. Trên ảnh, nhãn LPSY[D] màu tím nằm ở giữa chart, cách nhãn LPSY[C] khoảng 6 tiếng về bên trái.
- **Nghi phạm trong thuật toán:** đây là **rác từ một chu trình D trước đó bị lùi state mà không xoá nhãn**. Kịch bản khớp với dữ liệu: khoảng 18:43 có một cú phá biên phụ dưới → máy vào Phase D, đặt LPSY[D] lúc 19:00 → cú phá bị phủ định (mục 7 câu 1) → state lùi về B, **dải Phase D bị xoá khỏi timeline nhưng nhãn LPSY[D] thì không**. Đúng đây là lỗi C của v4 (xoá dải nhưng không xoá nhãn) tái xuất ở nhánh **D→B**, trong khi v5 chỉ vá cho nhánh **C→B**. Cần một hàm "rollback phase" xoá **cả dải cả nhãn** dùng chung cho mọi nhánh lùi state.

### 2. Climax bỏ qua cây tin VSA 14.64× để gắn vào cây thứ tư VSA 1.98× — luật vi phạm: L1, mục 4.0 spec
- **Thuật toán gắn:** BCLX tại 12:33, giá 4112.5, **VSA 1.98×** (dưới ngưỡng 2.2× của chính spec), thân **0.20**.
- **Đúng phải là:** cây cao trào mua thật là **12:30**: mở 4036.1 → cao 4098.4, biên độ **62.4 giá**, volume **4597**, **VSA 14.64×**, thân 0.96. Đó là cây tin. Ba cây sau nó (7.01× · 3.97× · 1.98×) là đuôi cụm với volume và biên độ **giảm dần đều** — cây 12:33 là cây yếu nhất của cụm, và nó chỉ được chọn vì tình cờ có đỉnh cao nhất (4112.5).
- **Dấu hiệu quyết định trên chart:** panel volume — một thanh vàng khổng lồ tại 12:30 cao gấp nhiều lần mọi thanh khác trong 735 nến, còn nhãn BCLX lại nằm cách đó 3 nến về bên phải. Trên trục giá, cây 12:30 một mình đi 62 giá trong 1 phút.
- **Nghi phạm trong thuật toán:** đúng lỗi #1 của bài #36 và #37, lần này lộ rõ nhất: **cụm climax (mục 4.0) dời mốc sang cực trị mới mà không kiểm lại VSA/biên độ tại cây mới**, và tiêu đề chart in VSA của cây đã dời. Sửa: giữ **cây sự kiện** ở cây đủ tiêu chuẩn climax (VSA cao nhất trong cụm), chỉ dời **mức giá biên** tới cực trị của cụm.

### 3. Range 36.3 giá / 735 nến, biên phụ 68.7 giá — cả một xu hướng giảm bị gọi là vùng cân bằng — luật vi phạm: L1, L3
- **Thuật toán gắn:** biên chính 4076.2–4112.5 = 36.3 giá (0.88% giá); biên phụ 4043.8–4112.5 = **68.7 giá**, gấp **1.9 lần**. Range kéo 735 nến ≈ 13 tiếng.
- **Đúng phải là:** nhìn ảnh, sau ST[A] (13:01) giá **không hề đi ngang** — nó trôi xuống liên tục: 4098 (14:37) → 4066 (15:59) → 4050 (18:43) → 4043 (01:48). Đó là một downtrend có bậc, không phải một vùng đấu giá quanh hai biên. Cả nửa dưới của "range" (từ 4076.2 xuống 4043.8) là giá đã ở **ngoài** biên chính suốt hơn 10 tiếng.
- **Dấu hiệu quyết định trên chart:** đường cam nét liền dưới (4076.2) — trên ảnh giá cắt xuống dưới nó tại ~15:59 và **không bao giờ quay lại trên nó** cho tới hết range. Hơn 550 nến nằm dưới biên chính dưới mà range vẫn "đang chờ cú phá".
- **Nghi phạm trong thuật toán:** không có luật nào phủ định range khi giá **ở hẳn** một phía biên quá lâu. Mục 5.1 kết cục B có nhánh "ở ngoài quá 40 nến **và** ≥60% nến đóng cửa ngoài biên → SOW", nhưng nhánh đó rõ ràng không bắn (range vẫn "Chưa rõ"). Cần truy vì sao: nghi là điều kiện "vượt **biên phụ** thêm ≥30 tick" — mà biên phụ tự nới theo từng bậc giảm, nên giá không bao giờ vượt được cái biên đang chạy trước nó. **Biên phụ nới theo giá rồi lại dùng chính nó làm điều kiện phá là logic vòng tròn** — đây là lỗi nặng nhất về mặt code trong bài.

### 4. Range đóng ở trạng thái "Chưa rõ" sau 735 nến — luật vi phạm: L4
- **Thuật toán gắn:** tên range = "Chưa rõ (BCLX) (DIST?)", màu xám, nhưng trạng thái `[completed]`.
- **Đúng phải là:** L4 có đủ 4 pattern để **luôn** đặt được tên khi có cú phá thật. Range này giá rơi **68.7 giá dưới đỉnh climax**, đóng cửa hẳn dưới mọi biên — nếu range hợp lệ thì đây là **Phân phối (DIST)** không phải "chưa rõ". Việc nó đóng mà không đặt được tên là bằng chứng nhánh xác nhận SOW đã bị chặn (xem lỗi #3), chứ không phải bằng chứng "thị trường mơ hồ".
- **Dấu hiệu quyết định trên chart:** tiêu đề ghi `[completed]` + `Chưa rõ`; sự kiện cuối cùng là **mSOW** (cú phá thất bại) tại đúng nến cuối range 01:48. Range đóng ngay tại một cú phá "thất bại" — nghĩa là nó đóng vì hết dữ liệu/hết guard, không vì cấu trúc hoàn tất.
- **Nghi phạm trong thuật toán:** nhánh "3 lần vô hiệu thì đóng range ở trạng thái chưa rõ" (lỗi F v4). Nhánh này chạy đúng như thiết kế, nhưng thiết kế đó đang che một lỗi khác thay vì báo lỗi.

### 5. Hai nhãn mSOW cùng tên, cùng cạnh — luật vi phạm: L3 (mỗi bên tối đa 1 biên phụ ⇒ mỗi bên 1 nhãn thăm dò)
- **Thuật toán gắn:** mSOW 07-14 23:17 (4052.7) và mSOW 07-15 01:48 (**4045.8**) — cả hai cùng cạnh dưới.
- **Đúng phải là:** theo mục 5.1 spec, nhãn thăm dò mỗi bên chỉ giữ **một** cái, cú mới nông hơn thì không ghi. Cú 01:48 sâu hơn (4045.8 < 4052.7) nên đúng là nó phải thay thế cú 23:17 — nhưng cú cũ **không bị xoá**. Cùng họ lỗi với #1: cơ chế "thay thế nhãn" không xoá nhãn cũ.
- **Dấu hiệu quyết định trên chart:** hai nhãn "mSOW" hiển thị đồng thời trên ảnh, một ở ~4052 và một ở ~4046.
- **Nghi phạm trong thuật toán:** hàm nới biên phụ có xoá mức cũ (chỉ còn 1 đường nét đứt dưới = 4043.8) nhưng **không xoá sự kiện cũ**. Mức và nhãn phải cùng một tham chiếu — đúng bài học lỗi E của v4, chưa áp cho nhãn mSOS/mSOW.

### 6. ST[A] 4091.4 rơi vào giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 13:01, giá **4091.4** — nằm ở **42%** chiều cao range (4076.2 → 4112.5), cách mức climax **21.1 giá**.
- **Đúng phải là:** ST[A] là cú quay lại **test vùng climax** (L2 lần đổi hướng thứ 3). Ở 42% chiều cao, cách climax 21 giá trên một range 36 giá, nó là một cú ngọ nguậy giữa range chứ không phải test biên. Đây đúng là lỗi mà giảng viên bắt ở vòng v4 (lỗi D: "ST[A] rơi giữa range, đo được 41%–179%") — **vẫn còn nguyên ở bài này**, đo được 42%.
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm ST[A] nằm lơ lửng giữa hai đường cam, không chạm đường nào. Phiếu số liệu: 4091.4 so với climax 4112.5 và AR 4076.2.
- **Nghi phạm trong thuật toán:** mục 4.2 đã **bỏ hết ngưỡng %** theo quyết định 4 của người học ("đo bằng cấu trúc"), chỉ còn "swing pivot đầu tiên + 5 nến + 1.5× biên độ TB". Trên một range 36 giá, 1.5× biên độ TB (cỡ 2-3 giá) là quá nhỏ → pivot đầu tiên bắt được là một cái nhấp nhô 15 giá dưới đỉnh. "Đo bằng cấu trúc" cần thêm ràng buộc **cấu trúc**: pivot đó phải là pivot **cùng bậc** với AR, hoặc phải nằm trong nửa range phía climax.

## Đạt
- Không có nhãn UTAD nào bị gán bừa trong Phase B — tránh được lỗi kinh điển Ca #1/#4 nguồn 4.pdf.
- Không có ST[B] — đúng L6.
- Máy **không** đặt tên range khi cú phá chưa hợp lệ (giữ "Chưa rõ") — về mặt kỷ luật là đúng lỗi F v4, dù ở đây nó che một lỗi khác.
- Phase C (19n) ngắn, Phase B dài nhất — đúng tỉ lệ L8/L9 về mặt số học.
- Biên chính giữ cố định 4076.2/4112.5 suốt 735 nến, không bị kéo theo giá — đúng L3, lỗi E v4 đã hết ở phần biên chính.

## Cần hỏi người học
- Khi giá đã đóng cửa ở hẳn **một phía** biên chính liên tục quá N nến (ở đây >550 nến dưới biên dưới) mà nhánh SOW vẫn không xác nhận, nên (a) cưỡng chế đặt tên range theo phía đó, hay (b) huỷ range vì hai biên chính đã mất nghĩa? Tôi nghiêng về (b).
