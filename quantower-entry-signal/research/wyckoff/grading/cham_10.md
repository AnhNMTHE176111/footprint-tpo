# Chấm bài #10 — Tái phân phối (RE-DIST) · 2026-04-28 02:02 → 06:04 (101 nến M1)

**Điểm: 3/10** — Tên range đúng và hướng đọc đúng, nhưng climax là nến 3 hợp đồng và cú phá xuống bị bỏ mất hoàn toàn nhãn Shakeout/SOW đúng chỗ. Phải vẽ lại Phase A.

## Lỗi (nặng → nhẹ)

### 1. SC là nến VSA 0.92x / 3 hợp đồng, trong khi nến sát cạnh có VSA 5.07x — luật vi phạm: L1 (điều kiện ĐỦ), THEORY §3.3
- **Thuật toán gắn:** SC tại 02:02, giá 4715.0, **VSA = 0.92x**, volume **3 hợp đồng**, biên độ 2.8 giá.
- **Đúng phải là:** nến **−2 (02:00)** có VSA **5.07x**, volume 19, biên độ 2.6 giá, đáy 4715.8 — đó mới là cao trào bán. Nến −5 (01:57) cũng 2.64x. Cây được chọn (0.92x) thấp hơn ngưỡng mở range 2.2x của chính thuật toán **2.4 lần**.
- **Dấu hiệu quyết định trên chart:** trên panel khối lượng, cột vàng cao nằm **ngay bên trái** nhãn SC (đúng nến 02:00); tại vạch Phase A thì cột volume gần như không thấy.
- **Nghi phạm trong thuật toán:** giống hệt bài #06 — logic "cụm climax" (mục 4.0) dời mốc sang cực trị mới (4715.0 thấp hơn 4715.8 đúng **0.8 giá**) mà **không kiểm lại VSA trên cây đích**. Đổi 0.8 giá độ sâu để mất một cây 5.07x lấy một cây 0.92x là lỗ. Sửa: khi dời mốc cụm, chỉ dời nếu cây đích cũng đạt ngưỡng VSA, hoặc giữ nhãn ở cây có VSA cao nhất trong cụm và chỉ dời **mức biên**.

### 2. Cú phá xuống bị bỏ mất nhãn — LPSY[C] đặt ở nơi thật ra là Shakeout/SOW thất bại — luật vi phạm: L5 + L8
- **Thuật toán gắn:** LPSY[C] tại 05:24, giá **4707.5** — tức **thấp hơn biên chính dưới 4715.0 tới 7.5 giá**, hoàn toàn NGOÀI range. Phase C dài 5 nến.
- **Đúng phải là:** nhìn ảnh, giá đã phá biên dưới từ khoảng **04:43** (nến đỏ dài từ 4712 xuống 4697, panel volume có cột vàng cao nhất toàn ảnh ở đúng đó), rồi lùng bùng ngoài biên từ 04:43 tới 05:35 — **khoảng 50 nến ngoài biên**. Theo L5 đó là một cú phá đã đóng cửa hẳn ngoài biên và giữ được → **SOW thật**, phải bắn từ ~04:45, không phải chờ tới 05:36. Còn nhãn LPSY[C] ở 4707.5 là một nhịp hồi **giữa đường đi xuống**, ngoài biên — nó không test biên nào cả.
- **Dấu hiệu quyết định trên chart:** chấm LPSY[C] nằm lơ lửng **dưới** đường liền cam "bien CHINH duoi 4715.0" một khoảng rõ rệt, không chạm biên. Một điểm test phải chạm cái nó test.
- **Nghi phạm trong thuật toán:** không có biên phụ (biên phụ = biên chính, cả hai đều 4715.0–4728.5), nên điều kiện "SOS/SOW phải đóng cửa vượt **biên phụ**" trở thành trùng với biên chính — lẽ ra cú 04:43 đã thoả ngay. Việc SOW chỉ bắn ở 05:36 cho thấy điều kiện "3 nến liên tiếp đóng vượt biên ≥ 30 tick với thân ≥ 45%" bị trượt vì các nến hồi xen giữa reset bộ đếm. Nên dùng "≥ 3 trong 5 nến" thay vì "3 nến liên tiếp".

### 3. Thiếu hẳn biên phụ dù giá đã đi ra ngoài rất xa — luật vi phạm: L3
- **Thuật toán gắn:** "Bien PHU (net dut, cuc tri xa nhat): 4715.0 - 4728.5" = **y hệt biên chính**, tức không có biên phụ nào.
- **Đúng phải là:** biên phụ = cực trị xa nhất mà một thế lực đã cố phá range gốc tạo ra. Trong Phase B (03:00–05:22) nhìn ảnh giá có thọc xuống dưới 4715 ở khoảng 04:43 tới 4697 — đó là một cực trị ngoài range rõ ràng, phải tạo biên phụ dưới ~4697. Máy ghi "không có".
- **Dấu hiệu quyết định trên chart:** cả hai đường trên chart đều là nét liền, không có nét đứt nào, dù nửa dưới ảnh (4697 → 4667) toàn bộ nằm ngoài range.
- **Nghi phạm trong thuật toán:** biên phụ có lẽ chỉ được nới trong nhánh "theo dõi cú phá → kết cục A (rút về trong range)". Cú phá này rơi vào kết cục B (ở hẳn ngoài) nên nhánh nới biên phụ không chạy. Phải nới biên phụ **ngay khi giá thò ra**, độc lập với kết cục.

### 4. ST[A] không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 02:59, giá 4717.4, VSA 0.59x, thân **0.00** (doji).
- **Đúng phải là:** về mức giá thì 4717.4 cách climax 4715.0 chỉ 2.4 giá — **rất gần, chỗ này ĐẠT**. Vấn đề là chất lượng cây: VSA 0.59x thân 0.00. THEORY §3.3 nói ST có spread/volume **giảm** khi quay lại tiệm cận SC, nên volume thấp là đúng lý thuyết. Chấp nhận. Nhưng Phase A dài 25 nến trong đó AR chỉ ở nến thứ 14 và AR có VSA **0.25x thân 0.00** — AR mới là cây rác thật sự ở đây.
- **Dấu hiệu quyết định trên chart:** nhãn AR ở 4728.5 đặt trên một nến bé xíu; nhịp bật ngược thật từ 4715 lên 4728 gồm mấy nến xanh phía trước nó.
- **Nghi phạm trong thuật toán:** mục 4.1, AR là swing pivot thuần hình học, không xét khối lượng — cùng nghi phạm với bài #08 lỗi #2.

### 5. Phase E = 2 nến — luật vi phạm: L10 + lỗi J của v4
- **Thuật toán gắn:** E từ 06:03 tới 06:04 = 2 nến. D = 22 nến.
- **Đúng phải là:** nhìn ảnh, sau 06:04 giá vẫn còn hoạt động (bật lên 4685 rồi xuống 4670 rồi lại lên) — nhưng range đóng. Lỗi J tái phát, giống bài #09.
- **Nghi phạm trong thuật toán:** cùng nghi phạm bài #09 lỗi #5 — E ăn phần dư sau khi hết cửa sổ 25 nến của D.

### 6. Range 101 nến M1, biên chính 13.5 giá (0.29%), đủ A→E — cờ đỏ chất lượng
- Giống bài #09: một vùng đấu giá thật không xong cả 5 phase trong 1 tiếng với biên độ 13.5 giá. Thêm nữa đây là **phiên Á 02:00–06:00 UTC** — volume của cả range đếm bằng đơn vị hàng đơn vị (1-19 hợp đồng/nến). Người học đã chốt không dùng sàn khối lượng tuyệt đối, nên không tính là vi phạm luật, nhưng cấu trúc Wyckoff đọc trên 3 hợp đồng là đọc trên nhiễu.

## Đạt
- **Tên range đúng:** SC chặn move giảm, sau đó phá **xuống** → **Tái phân phối**. Đúng bảng L4 — đây chính là loại range mà bản v2/v3 xoá oan 61 lần.
- MOVE trước climax có thật: 33.1 giá / 58 nến / hiệu suất **0.43** (cao nhất lô này). Trên chart đợt giảm từ ~4750 xuống 4715 là một move xu hướng rõ, cây climax nằm đúng đáy chặn nó (L1 điều kiện CẦN ĐẠT).
- Phase A (25n) → B (48n) → C (5n): tỉ lệ **đúng** — B dài nhất, C ngắn nhất. Đây là bài duy nhất trong lô 06-10 thoả cả L8 và L9.
- LPSY[D] (4683.3) đặt đúng vai: nhịp hồi sau SOW, giữ được bên dưới biên → CBR hợp lệ (L10).
- Biên chính cố định suốt range (L3).
- Chỉ 1 điểm cho LPSY[C] và 1 điểm cho LPSY[D], không vẽ vùng, không spam (L7).
