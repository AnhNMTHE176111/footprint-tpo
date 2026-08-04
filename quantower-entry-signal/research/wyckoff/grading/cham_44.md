# Chấm bài #44 — Tích lũy (ACC) · 2026-07-12 22:48 → 07-13 00:22 (93 nến M1)

**Điểm: 2/10** — **Không nên vẽ range ở đây.** 93 nến M1 nhồi đủ Phase A→E, MOVE mở range được đo **bắc qua khe cuối tuần ~49 giờ**, và cú SOS gọi là "Tích luỹ" thì 30 nến sau giá sập xuyên qua cả biên phụ dưới. Đây là nhiễu bị chia phase cơ học.

## Lỗi (nặng → nhẹ)

### 1. MOVE trước climax đo bắc qua khe cuối tuần — L1, lỗi K vá chưa đủ
- **Thuật toán gắn:** "chân MOVE (24.2 giá, hiệu suất 0.37)", 47 nến, chân đặt tại **2026-07-10 20:36**, climax tại **2026-07-12 22:48**.
- **Đúng phải là:** giữa hai mốc đó là **khe ~49 giờ** (đóng cửa thứ Sáu → mở cửa Chủ Nhật 22:00 UTC). Đọc ngay trên trục thời gian của ảnh: nhãn nhảy từ `07-10 20:53` sang `07-12 22:10`. Một "MOVE giảm 47 nến" mà 2 ngày lịch nằm trong đó không phải một move xu hướng bị climax chặn — nó là hai đoạn giá khác phiên bị nối liền. Điều kiện CẦN của L1 **không thoả** ⇒ không mở range.
- **Nghi phạm trong thuật toán:** guard khe > 240 phút (lỗi K của v5) chỉ áp cho **range đang chạy**, **không** áp cho cửa sổ nhìn lại 240 nến khi đo MOVE. Phải cắt cửa sổ MOVE tại khe đầu tiên > 240 phút, và khi đó đoạn còn lại (07-12 22:10 → 22:48, ~38 nến, ~14 giá) mới là move được xét.

### 2. Range 93 nến mà đủ 5 phase — nghi nhiễu, không phải vùng đấu giá — L8, L9, CHART_CASES "range quá vụn"
- **Thuật toán gắn:** A 17 · B **30** · C **21** · D 25 · E **1**.
- **Đúng phải là:** Phase B phải là phase **dài nhất** một cách rõ rệt (L9) và Phase C phải là **ngắn nhất** (L8). Ở đây B chỉ hơn C 9 nến, và **D (25) dài hơn C (21)**. Năm phase gần đều nhau trong 93 nến = cấu trúc bị chia cơ học, không phải 5 giai đoạn đấu giá thật. Đúng cảnh báo trong CHART_CASES: một TR M1 chỉ 60–100 nến với đủ A→E thì phải nghi nhiễu trước khi nghi cấu trúc.

### 3. Tên "Tích luỹ" gán cho cú phá sập ngược ngay sau — L4, L10
- **Thuật toán gắn:** SOS 23:57 → Phase D 25 nến → Phase E **1 nến** → `completed`, tên **Tích lũy**.
- **Đúng phải là:** trên ảnh, sau đỉnh 4099.2 (00:14) giá **đổ thẳng xuống 4070** lúc 00:35 — dưới cả biên phụ dưới 4075.8 — rồi mới lùng bùng lại. Theo L10, Phase E phải là "giá rời range đi tìm vùng giá mới"; ở đây giá **quay lại xuyên qua toàn bộ range**. Theo L4, hướng phá **thật** là xuống ⇒ range này đọc bằng mắt là một **Phân phối / cú upthrust cuối** (nhãn SOS đúng ra là **UTAD** nếu cấu trúc được giữ), hoặc tối thiểu cú phá phải bị vô hiệu (lỗi F) và range đóng ở trạng thái chưa rõ.
- **Dấu hiệu quyết định trên chart:** Phase E dài **đúng 1 nến** — chính máy đã phát hiện "giá lùi hẳn vào trong biên" ở nến đầu Phase E, nhưng vẫn dùng cột mốc đó để đặt tên pattern. (Lỗi giống bài #40 — lặp trên 2/5 bài của lô.)
- **Nghi phạm:** đích Phase E tối thiểu **0.5× chiều cao** = 6 giá; giá lên 4099.2 tức vượt biên trên 10.4 giá nên "đạt" ⇒ chốt E. Đề nghị: Phase E ≤ 2 nến ⇒ **không đặt tên pattern**, hạ SOS thành mSOS.

### 4. SOS chỉ vượt biên phụ 0.1 giá, và mSOS 5 nến trước ở đúng cùng mức — L3, L5
- **Thuật toán gắn:** `mSOS` 23:52 tại **4091.4** (VSA 1.08×, thân 0.33) rồi `SOS` 23:57 tại **4091.5** (VSA 2.79×, thân 0.63).
- **Đúng phải là:** biên phụ trên **chính là 4091.4** do cây mSOS tạo ra, nên SOS "bứt qua biên phụ" đúng **1 tick** — về bản chất SOS chưa bứt qua gì (L3: SOS mạnh phải **đóng cửa** bứt qua biên phụ). Và hai nhãn trái nghĩa (một "thất bại", một "thật") cách nhau 5 nến ở cùng một mức giá là mô tả sai một cú phá đơn lẻ; 23:52 nên là **UT[B]** hoặc bỏ hẳn.
- **Nghi phạm:** thứ tự cập nhật — cây thăm dò tự nới biên phụ rồi cây kế tiếp lại được so với biên phụ **vừa bị nó nới**. Nên so SOS với biên phụ **tại thời điểm trước cú phá hiện hành**, cộng một sàn tuyệt đối (vd 30 tick) thay vì 1 tick.

### 5. AR yếu: chốt sau 4 nến với volume 20 lot — L2, L3
- **Thuật toán gắn:** `AR` 22:52 tại 4088.8, **VSA 0.36×** (20 hợp đồng), thân 0.90.
- **Đúng phải là:** AR là *"sóng mua đẩy giá lên sau khi áp lực bán giảm mạnh"* — một nến 20 lot ở phiên Á giờ chết không phải "lực đẩy tự động", chỉ là giá dạt lên khi không còn ai bán. Nó vẫn quyết định **biên chính trên** cho cả range. Đây đúng là điểm đánh đổi mà người học đã chốt (không dùng sàn khối lượng tuyệt đối) — ghi nhận, nhưng hệ quả thấy rõ ở đây.

### 6. Ba chỉ số Phase B mới — gần như không đo được gì ở range 30 nến
- **SOT trên:** `none, n=0`. **SOT dưới:** `chớm, n=1, thrust 0.00, volume 0.00`. Với Phase B chỉ 30 nến thì không có đủ 3 lần đẩy để SOT có nghĩa (THEORY §7) — đúng ra nên in `n/a (Phase B quá ngắn)` thay vì "chớm".
- **Nỗ lực/kết quả:** `effort=2.24x, result=6.04, er=0.37` → "**hấp thụ NGHI VẤN (volume nhiều, kết quả ít)**". er = 0.37 là trường hợp **ngược hẳn**: nỗ lực nhỏ mà kết quả rất lớn (biên độ 6× ATR) — dấu hiệu **thiếu đối lực**, không phải hấp thụ. Đây là bằng chứng rõ nhất trong lô rằng câu diễn giải là **hằng số dán cứng**, không suy từ er (4/5 bài có er < 1 vẫn nhận đúng câu này).
- **Bias:** `+0` — trùng cả 5 bài 40–44.

## Đạt
- **Nến climax là climax thật:** VSA **7.19×** (359 lot so với 12–47 lot các nến trước), biên độ 7.9 giá, và low 4076.8 **là đáy thật** — mốc climax neo đúng cực trị, nhãn và mức trùng nhau.
- **Phase A đủ 3 lần đổi hướng (L2):** SC 4076.8 → AR 4088.8 → ST[A] 23:04 tại **4075.8**, tức ST[A] test lại đúng vùng climax (và vượt nhẹ, đúng L3 nên tạo biên phụ dưới 4075.8). Phase A kết thúc đúng tại ST[A].
- **Biên (L3):** biên chính = climax + AR, cố định; mỗi bên đúng 1 biên phụ, tỉ lệ 1.30× — hẹp, không phình.
- **LPS[C] 23:36** đặt ở vùng hợp lý (4079.3, sát biên dưới, nhịp test cuối trước nhịp lên), VSA 1.23× — chấp nhận được cho một mốc gán ngược.

## Cần hỏi người học
- Với range mà cú phá đạt đích Phase E rồi **lập tức** sập ngược xuyên qua cả range (bài #40 và #44): giữ nguyên tên pattern theo hướng phá đầu tiên, hay đổi tên theo hướng đi thật sau đó? Luật L4 nói "hướng phá **thật** quyết định tên" nhưng chưa định nghĩa cửa sổ quan sát "thật" là bao lâu sau Phase E.
