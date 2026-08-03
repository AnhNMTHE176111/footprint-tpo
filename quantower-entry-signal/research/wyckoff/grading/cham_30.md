# Chấm bài #30 — Tái phân phối (RE-DIST) · 2026-06-30 00:06 → 01:08 (62 nến M1)

**Điểm: 1/10** — **KHÔNG NÊN VẼ RANGE Ở ĐÂY.** Đây không phải vùng đấu giá mà là **một đoạn xu hướng giảm liên tục** bị cắt ngang: sau nhịp hồi 6 nến (9.3 giá), giá đóng cửa dưới biên dưới từ nến thứ 26 và **không bao giờ quay lại**, rơi tiếp 60 giá. Thuật toán vẫn gọi cả đoạn rơi đó là "Phase A", và đặt nhãn **ST[A]** — một cú test nhẹ — lên cây giảm 8.9 giá đóng cửa sát đáy.

## Lỗi (nặng → nhẹ)

### 1. Climax không chặn được move → không đủ điều kiện CẦN để mở range — luật vi phạm: L1
- **Thuật toán gắn:** SC tại 00:06 giá 4018.2 (VSA 4.47×) chặn MOVE giảm 18.5 giá / 47 nến.
- **Đúng phải là:** không mở range. Cây 00:06 chỉ tạm dừng đợt giảm 6 nến rồi đợt giảm **tiếp tục và mạnh hơn nhiều** — từ 4027.5 (00:12) xuống 3955.4 (01:07), tức **72 giá**, gấp **7.7 lần** chiều cao biên chính (9.3 giá). Một cây climax mà move sau nó dài gấp 4 lần move trước nó thì nó không chặn gì cả.
- **Dấu hiệu quyết định trên chart:** giá đóng cửa dưới biên chính dưới 4018.2 từ **00:31 (C=4016.1)** và **không có một nến nào** đóng lại trên 4018.2 trong 37 nến còn lại. Đường liền dưới bị bỏ lại phía trên toàn bộ hành động giá. Bậc thang giảm đọc thẳng trên số: 4016.1 → 4013.8 → 4010.1 → 4005.8 → 4001.2 → 3992.9 → 3980.3 → 3959.1.
- **Nghi phạm trong thuật toán:** điều kiện L1 chỉ kiểm **quá khứ** của cây climax (là cực trị của 240 nến trước, hiệu suất MOVE ≥ 0.35) mà **không kiểm tương lai** — không có bước xác nhận "move đã thật sự bị chặn". Thêm nữa VSA 4.47× ở đây là 138 lot trên nền trung bình ~31 lot của giờ 00:xx UTC: mỏng, nên VSA tương đối vô nghĩa. Cần thêm ngưỡng volume tuyệt đối theo phiên.

### 2. ST[A] đặt lên cây bán mạnh, cách biên 2.75 lần chiều cao range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 00:56, giá **3992.6** — dưới mức climax **25.6 giá = 2.75× chiều cao biên chính (9.3 giá)**.
- **Đúng phải là:** ST[A] là cú quay về **bị chặn nhẹ** ở vùng climax. Nến 00:56 là ngược lại hoàn toàn: O=4001.3 → L=3992.6, **C=3992.9 (đóng sát đáy)**, thân **0.94**, volume **623 = 4.31×**. Đó là một cây SOW/bán tháo. Không có ST[A] nào ở đây → theo L2 Phase A **chưa hoàn thành** → phải bỏ ứng viên range.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] và đường đứt "bien phu duoi 3992.6" nằm **thấp hơn cả cụm nến giữa chart**, cách xa hẳn khung range. Biên phụ 34.9 giá / biên chính 9.3 giá = **3.75 lần** — biên phụ không còn là "một thế lực cố phá range" mà là bằng chứng range đã không tồn tại.
- **Nghi phạm trong thuật toán:** dòng 375–395, `retrace` không có giới hạn trên (ở đây ≈ 3.8) và ST[A] vượt climax chỉ lặng lẽ nới biên phụ. Cần guard: `biên phụ / biên chính > ~2` ⇒ huỷ range; hoặc ST[A] vượt mức climax > 50% chiều cao biên chính ⇒ huỷ.

### 3. Phase A = 51/62 nến (82%) — luật vi phạm: L9
- **Thuật toán gắn:** A=51 · B=7 · C=3 · D=1 · E=1.
- **Đúng phải là:** Phase B phải là phase dài nhất. Ở đây "Phase A" là **cả đoạn xu hướng giảm**, còn B/C/D/E cộng lại chỉ 11 nến — cấu trúc bị gò cho khớp đủ 5 phase, đúng lỗi "gò ép" mà giảng viên phê ở Ca #20 nguồn 7.pdf.
- **Nghi phạm trong thuật toán:** lỗi hệ thống của cả lô — Phase A không thể ngắn hơn `AR_LOOKBACK + 1 = 41` nến vì nhánh tìm AR chỉ chốt tại nến cố định `climax_i + 41`.

### 4. LPSY[C] và SOW đều nằm ngoài range, cách 20–60 giá — luật vi phạm: L8 + L10
- **Thuật toán gắn:** LPSY[C] tại 01:04 giá 3998.4 (thân **0.02** — một cây doji) → Phase C 3 nến; SOW tại 01:07 giá 3959.1.
- **Đúng phải là:** SOW 01:07 là một cây bán **thật** (volume **2097 = 7.11×**, biên độ 25.6 giá) nhưng nó ở **59 giá dưới** biên chính — đó là một đợt xu hướng mới, không phải Phase D của cái range 9.3 giá này. "Phase E 1 nến" không thể diễn tả được "giá rời range đi tìm vùng giá mới" khi giá đã rời range từ 36 nến trước.
- **Dấu hiệu quyết định trên chart:** cả ba dải Phase C/D/E chen nhau trong 5 nến ở góc phải, trong khi mọi hành động có ý nghĩa (cây 01:06 volume 789, cây 01:07 volume 2097) đều xảy ra bên ngoài khung range.

### 5. [Trình bày] Ba nhãn phase chồng nhau — mức nhẹ
- Phase C (3n), Phase D (1n), Phase E (1n) chỉ cách nhau 1–3 nến nên ba hộp nhãn chồng lên nhau ở góc trên phải, không đọc được nếu không tra phiếu số liệu. Chỉ là lỗi trình bày, nhưng nó là **triệu chứng** của lỗi cấu trúc số 3–4: phase 1 nến thì không nên vẽ dải phase.

## Đạt
- **Mục 4 (L4):** tên range gọi đúng theo quy tắc — origin SC + phá xuống = **Tái phân phối** (nếu chấp nhận range này tồn tại).
- **Mục 3 (một phần):** biên chính giữ cố định sau Phase A, không bị kéo theo giá; biên phụ đúng một cái mỗi bên.
- **Mục 8 (một phần):** cây SOW 01:07 được chọn đúng là cây nỗ lực lớn nhất khu vực (7.11×, 2097 lot) — máy đọc volume đúng, chỉ gán nó vào sai cấu trúc.

## Cần hỏi người học
- Bài này là ca **rõ nhất** để chốt một guard mới: khi **biên phụ / biên chính > 2** (ở đây 3.75) thì huỷ range luôn, hay vẫn vẽ và chỉ hạ mức tin cậy? Guard hiện có ("biên chính > 3.5% giá") không bắt được ca này vì biên chính chỉ 0.23%.
