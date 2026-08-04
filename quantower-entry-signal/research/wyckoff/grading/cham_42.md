# Chấm bài #42 — Tái phân phối (RE-DIST) · 2026-07-07 19:18 → 07-08 10:56 (877 nến M1)

**Điểm: 5/10** — Cấu trúc lớn đọc **đúng** (move giảm bị chặn, đi ngang 13 tiếng, sụp tiếp = tái phân phối, tên đúng L4, Phase B dài nhất, Phase E có độ dài thật). Sai ở nội bộ: ST[A] nằm ở 70% chiều cao, biên chính không bao được nửa sau của range, và LPSY[C] gán cho một cây bán VSA 10× — ngược hẳn định nghĩa LPSY.

## Lỗi (nặng → nhẹ)

### 1. LPSY[C] gán cho cây bán VSA 10.06× — sai vai nhãn — THEORY §4.1, L8
- **Thuật toán gắn:** `LPSY[C]` 08:17 tại 4117.7, **VSA 10.06×**, thân **0.88**.
- **Đúng phải là:** LPSY theo định nghĩa gốc là *"một đợt phục hồi **yếu** trên biên hẹp → nguồn cầu cạn kiệt"* — tức nhịp hồi **ngược** hướng phá, volume **co lại**. Cây 08:17 là cây thân dài, volume gấp **10 lần** trung bình, đi **cùng** hướng phá. Đó là **MSOW / cây phá vỡ**, không phải LPSY. Nếu muốn giữ Phase C thì LPSY[C] phải là nhịp hồi lên vùng 4118–4125 **trước** cú sụp (nhìn ảnh: nhịp 07:10–07:50 hồi về 4128 rồi rớt — đó mới là điểm cung cuối).
- **Dấu hiệu quyết định trên chart:** panel volume — thanh vàng cao nhất toàn bộ 877 nến nằm đúng tại 08:17, cùng lúc giá xuyên từ 4118 xuống 4091. Không có "phục hồi yếu" nào ở đây.
- **Nghi phạm trong thuật toán:** Phase C gán ngược chọn "**đỉnh cao nhất trong 60 nến trước cú phá**" — thuần theo cực trị giá, **không kiểm tính chất nến**. Phải thêm điều kiện: nến LPSY[C] phải ngược hướng phá (nến xanh khi sẽ phá xuống) **và** VSA ≤ ~1.0× (test cạn cầu), nếu không tìm được thì để range không có Phase C.

### 2. Biên chính không bao được vùng đấu giá nửa sau — L3 (hệ quả), L1
- **Thuật toán gắn:** biên chính 4102.7–4125.9 (**23.2 giá**), biên phụ 4091.3–4144.7 (**53.4 giá**, 2.30×).
- **Đúng phải là:** trên ảnh, từ 07-08 01:21 đến 07:10 (~350 nến, tức nửa Phase B) giá dao động **4128–4145 — hoàn toàn phía trên biên chính trên**. Một biên chính bị bỏ ra ngoài suốt 6 tiếng thì không còn là biên. Đọc bằng mắt đây là **hai vùng cân bằng nối tiếp**: 4100–4126 (19:18 → 01:20) rồi 4128–4145 (01:21 → 07:10), vùng thứ hai chính là tái phân phối cấp trên, và cú sụp 08:17 phá **vùng thứ hai**, không phá vùng thứ nhất.
- **Dấu hiệu quyết định trên chart:** nét liền trên (4125.9) đi xuyên giữa thân cụm nến suốt đoạn 02:48–07:10; toàn bộ nhãn mSOS nằm trên nét liền 19 giá.
- **Nghi phạm trong thuật toán:** mục 13.3.1 — chỉ theo dõi **đúng một range một lúc**, nên climax mở vùng thứ hai bị bỏ qua và range thứ nhất bị kéo dài 877 nến. Cần một guard đơn giản trước khi có range lồng nhau: nếu ≥ N nến liên tiếp (vd 120) **đóng cửa ngoài biên chính** mà chưa thành SOS/SOW thì **đóng range** ở trạng thái chưa rõ và mở lại từ vùng mới.

### 3. ST[A] ở 70% chiều cao range — Phase A chưa hoàn thành — L2
- **Thuật toán gắn:** `ST[A]` 19:43 tại **4118.9**, VSA 0.68×, thân 0.07.
- **Đúng phải là:** (4118.9 − 4102.7)/23.2 = **70%** chiều cao — ST[A] nằm ngay dưới AR, chưa quay về vùng climax chút nào. Đó chỉ là một nến doji ngay sau AR. Test lại vùng climax thật xuất hiện muộn hơn (nhìn ảnh: nhịp ~21:00–21:40 xuống vùng 4098–4105, thọc dưới biên chính dưới).
- **Nghi phạm:** cùng gốc với bài #41 — ST[A] là "swing pivot đầu tiên về phía climax" mà **không có ràng buộc phải chạm vùng climax**; với sàn nhiễu chỉ 1.5× ATR thì một nến doji sát AR cũng đủ chốt Phase A.

### 4. mSOW 08:18 gọi là cú phá "thất bại" trong khi 22 nến sau là SOW thật — L5
- **Thuật toán gắn:** `mSOW` 08:18 tại 4091.3 (VSA 5.32×, thân 0.09) rồi `SOW` 08:40 tại 4075.8 (VSA 3.18×).
- **Đúng phải là:** theo L5, phá ra → lùng bùng ngoài một lúc → **đi tiếp** = phá **THẬT**. Cú 08:18 phá xuống 4091.3, giá lùng bùng 4092–4105 khoảng 20 nến rồi đi tiếp xuống 4048. Vậy 08:18 là **khởi đầu của MSOW**, không phải một SOW thất bại; nhãn mSOW ở đây là nhãn **dư** và nó làm ranh giới C/D lệch 22 nến.
- **Dấu hiệu quyết định trên chart:** ba nhãn LPSY[C] (08:17), mSOW (08:18), SOW (08:40) chồng chất trong **23 phút** trên cùng một cú sụp 42 giá — một sự kiện bị xé thành ba vai.
- **Nghi phạm:** nhánh "kết cục A — giá rút về trong range" xét theo **đóng cửa quay lại phía bên kia biên chính**; với biên chính đặt quá cao (lỗi #2) thì giá chỉ cần bật nhẹ đã tính là "thu vào", nên cú phá thật bị gắn mSOW.

### 5. mSOS 06:24 gán cho cây râu VSA 1.68×, thân 0.20 — THEORY §6.4
- Nghĩa v6 của mSOS là "phá hẳn ra ngoài rồi thu hẳn vào trong range", nhưng lúc 06:24 giá **đã ở ngoài biên chính trên suốt nhiều giờ** — mô tả "phá ra rồi thu vào" không đúng thực tế. Cây đó thân 20%, volume 1.68× → đây là **UT[B]** (test biên trên, đỉnh cao nhất range), không có nỗ lực phá vỡ nào.

### 6. Phase D (16) ngắn hơn Phase C (23) — L8
- A 26 · B **692** · C 23 · D 16 · E 121. B dài nhất: đúng. Nhưng C phải là phase ngắn nhất; ở đây D còn ngắn hơn — hệ quả của việc ranh giới C/D bị lệch (lỗi #4).

### 7. Ba chỉ số Phase B mới
- **SOT phía dưới:** `SOT, n=3, thrust 0.23, volume 0.13 (cạn kiệt)` — **đo đúng**: 3 nhịp, lực đẩy còn 23% và volume còn 13% ⇒ đúng biến thể "rút ngắn + volume yếu = cạn kiệt thật" của THEORY §7. Dùng được.
- **SOT phía trên:** `chớm, n=1, 0.00/0.00` — n=1 không đủ ≥3 lần đẩy để có nghĩa; tỉ lệ 0.00 nghĩa là không tính được nhưng vẫn in trạng thái. Nên ghi `n/a`.
- **Nỗ lực/kết quả:** `effort=1.24x, result=0.53, er=2.33` → "hấp thụ NGHI VẤN (volume nhiều, kết quả ít)". **Ở bài này câu đó đúng** (er > 1), nhưng đối chiếu bài #40 (er=0.46) và #43 (er=0.94) thấy cùng một câu → câu chữ **dán cứng**, không suy từ er. Phải gắn ngưỡng: er > ~1.5 mới nói hấp thụ; er < ~0.7 phải nói ngược lại ("nỗ lực nhỏ, kết quả lớn — thiếu đối lực").
- **Bias:** `+0`, giống cả lô 40–44.

## Đạt
- **Điều kiện mở range (L1):** MOVE giảm **46.2 giá** / 107 nến / hiệu suất 0.41, cụm climax 19:15–19:18 (VSA 2.94× rồi 1.53×) chặn đúng đáy move. Đây là ca mở range thuyết phục nhất trong lô.
- **Tên range (L4):** origin SC + phá **xuống** thật ⇒ **Tái phân phối**. Đúng, và đúng cả trên thực tế (giá đi tiếp xuống 4048).
- **Phase B dài nhất (L9):** 692/877 = 79%.
- **Phase D/E theo khuôn CBR (L10):** SOW 08:40 → LPSY[D] 08:48 (4087.0, VSA 1.09×, hồi yếu, **giữ được dưới biên**) → Phase E 121 nến chạy tiếp 40 giá. LPSY[D] ở đây gán **đúng vai** — trái ngược với LPSY[C] ở lỗi #1, cho thấy vấn đề nằm ở nhánh gán ngược chứ không ở định nghĩa.
- **Biên phụ (L3):** mỗi bên đúng 1, đều là cực trị xa nhất thật (4091.3 / 4144.7).
