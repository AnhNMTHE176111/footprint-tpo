# Chấm bài #24 — Phân phối (DIST) · 2026-06-12 15:21 → 19:59 (278 nến M1)

**Điểm: 2/10** — **Không được gọi là Phân phối.** Cú "SOW" chỉ chọc 2.1 giá ra khỏi biên rồi đóng cửa quay lại ngay vào trong range, và tới hết dữ liệu phiên (20:59) giá vẫn nằm trong range — range này **chưa được phân xử**, phải để "Chưa rõ (BCLX)". Ngoài ra Phase C dài nhất, Phase B 6 nến: vi phạm kép L8 + L9.

## Lỗi (nặng → nhẹ)

### 1. Đặt tên range dựa trên một cú phá KHÔNG hề thành — luật vi phạm: L4 + L5 + L10
- **Thuật toán gắn:** SOW 19:34 @4225.6 → Phase D 26 nến → range đóng, tên **Phân phối (DIST)**.
- **Đúng phải là:** đáy sâu nhất sau SOW là **4223.2 (19:35)**, tức chỉ **2.1 giá** dưới biên phụ dưới 4225.3 = **14% chiều cao biên chính (14.9 giá)**. Ngay nến 19:36 đóng **4227.2** (đã vào trong range), 19:41 đóng **4228.4** (quá ngưỡng "lùi hẳn 30 tick" của chính thuật toán), 19:59 đóng **4231.9**, và tới **20:59 giá 4239.9 — vẫn nằm giữa hai đường liền**. Theo L4, tên range chỉ được gán khi có **hướng phá thật**; ở đây không bên nào phá được, phải giữ trạng thái "Chưa rõ (BCLX)", tô xám.
- **Dấu hiệu quyết định trên chart:** sau nhãn SOW, thân nến đi **lên** và vượt cả đường liền 4227.4; nửa phải ảnh không có một nến nào trụ dưới biên.
- **Nghi phạm trong thuật toán:** tên range được gán ngay khi 3 nến "giữ ngoài biên" thoả, **trước** khi biết retest có giữ được không; và `_try_lps_and_phase_e()` đã trả `False` (thất bại) nhưng call site dòng ~604 bỏ giá trị trả về — đúng như docstring của chính hàm đó nói "False = lùi Phase B".

### 2. Vi phạm kép: Phase C là phase DÀI NHẤT, Phase B chỉ 6 nến — luật vi phạm: L8 + L9
- **Thuật toán gắn:** A 56 · B 5 · **C 121** · B 1 · **C 70** · D 26 → Phase C tổng **191 nến = 69% cả range**; Phase B tổng **6 nến**.
- **Đúng phải là:** Phase B phải là phase dài nhất (giai đoạn nỗ lực↔kết quả), Phase C là phase ngắn nhất (tín hiệu đầu tiên cho thấy sắp phá biên kia). Toàn bộ đoạn 16:22 → 19:33 là **Phase B** (giá lắc trong dải 4232–4256, 32% số nến vẫn đóng cửa trên biên chính trên) — không thể là Phase C.
- **Nghi phạm trong thuật toán:** đoạn Phase C đầu dài **đúng 121 nến = trần `SHOCK_MAX_WAIT` (120)** — tức nó chỉ kết thúc vì *hết giờ chờ*, không vì đọc được gì trên chart; hết giờ thì lùi Phase B **1 nến** rồi cú rũ kế tiếp lại mở một Phase C mới 70 nến. Cần: shock hết hạn thì **xoá Phase C khỏi timeline** và hạ nhãn thành UT/mSOS-mSOW trong Phase B (đúng như ghi chú LOI 12 đang chờ vá trong `wyckoff_schematic.py`).

### 3. ST[A] gán ở mức CAO HƠN climax 11.8 giá — luật vi phạm: L2 + lỗi kinh điển CHART_CASES #6 (nhầm hướng test: test ở biên trên là UT, không phải ST)
- **Thuật toán gắn:** ST[A] 16:16 @**4254.1** (VSA 2.46x, thân **0.15**) — cao hơn biên chính trên 4242.3 và hồi tới **179%** chiều cao climax↔AR.
- **Đúng phải là:** một cây thân 0.15 với râu trên dài, thọc lên vùng đỉnh thật 4256.8 = **UT / cú thăm dò đỉnh**, không phải ST[A] (ST[A] là nhịp quay lại phía climax rồi **bị chặn**, phải nằm *trong* range). Phase A do đó chưa được đóng ở đây.
- **Nghi phạm trong thuật toán:** `STA_MIN_RETRACE = 0.40` chỉ là **SÀN**, không có **TRẦN** — nên một cú vượt hẳn qua mức climax (179%) vẫn được nhận là ST[A].

### 4. UTAD (thất bại) 16:22 gọi sai chỗ — luật vi phạm: lỗi kinh điển Ca #1/#4 nguồn 4.pdf (UTAD chỉ là cú test cuối trước khi cấu trúc sụp)
- **Thuật toán gắn:** UTAD (thất bại) 16:22 @4244.3, **VSA 0.52x**, thân **0.03**.
- **Đúng phải là:** một nến doji với **nửa** khối lượng trung bình, chỉ hơn biên chính 2.0 giá và còn **thấp hơn đỉnh thật 12.5 giá** — không đủ tư cách UTAD dưới bất kỳ định nghĩa nào. Ở nhiều nhất nó là một cú chạm biên nhẹ (UT), và theo L8 nó không được mở Phase C.
- **Nghi phạm:** ngưỡng "thăm dò NHẸ" = < 15 tick **và** VSA < 3.3x; cú này 20 tick nên bị xếp "thăm dò THẬT" dù volume dưới trung bình. 15 tick = 1.5 giá là quá nhỏ với vàng.

### 5. UTAD (xác nhận) 18:24 neo sai cực trị và chưa phá đỉnh cao nhất — luật vi phạm: Ca #18 nguồn 2.pdf (SOS/UTAD chỉ hợp lệ khi phá đỉnh cao nhất từng có của range)
- **Thuật toán gắn:** UTAD (confirmed) 18:24 @4251.5, VSA 0.84x.
- **Đúng phải là:** cực trị của cú thăm dò đó là **4256.2 lúc 18:21** (VSA 2.89x, đóng 4255.4) — nhãn đặt **3 nến muộn và thấp hơn 4.7 giá**. Hơn nữa 4256.2 **< 4256.8** (đỉnh cao nhất từng có, tạo lúc 15:27) → đây là một **đỉnh thấp hơn (SOT)**, không phải UTAD.
- **Dấu hiệu quyết định trên chart:** đỉnh nến ngay trước nhãn UTAD chạm sát nhưng **không vượt** đường nét đứt 4256.8.

### 6. Bỏ qua hai cây "nỗ lực lớn – kết quả nhỏ" rõ nhất cả range — luật vi phạm: mục chấm 8 (Effort vs Result), THEORY §2.2
- 17:06: v=**545 (VSA 5.03x)**, H4247.1 nhưng đóng 4242.4, thân **0.17** → bị gắn nhãn **LPSY[C]**, trong khi một test hợp lệ phải có volume **co lại**, không phải 5x.
- 17:29: v=**882 (VSA 6.13x)** mà biên độ chỉ **3.2 giá**, thân 0.31 → **không có nhãn nào**. Đây là dấu hiệu cung hấp thụ toàn bộ cầu tại biên trên, đáng giá hơn mọi nhãn khác trong bài.

## Đạt
- **L1 (phần MOVE):** move tăng thật 44.8 giá / 34 nến / hiệu suất 0.39.
- **L3 (quy tắc biên phụ):** mỗi bên đúng 1 biên phụ (4225.3 / 4256.8), giữ cái xa nhất.
- **L7:** LPSY[C] chỉ đánh 1 điểm, không vẽ vùng, không lặp.
- **Phần đọc đúng đáng ghi nhận:** biên phụ trên 4256.8 và biên phụ dưới 4225.3 đã **khoanh đúng** vùng đấu giá thật — chỉ tiếc là nét liền (biên chính) lại nằm sai bên trong.

## Cần hỏi người học
- Khi một cú SOS/SOW đã "xác nhận" bằng 3 nến giữ ngoài biên **rồi hỏng** (giá đóng cửa lùi hẳn vào range, như ca này), anh muốn xử thế nào: (a) lùi hẳn về Phase B và **gỡ tên** range, hay (b) vẫn đóng range nhưng đặt tên **"phá thất bại"** riêng? Mục 7 tài liệu thuật toán cố ý đóng range ở Phase D để tránh vòng lặp vô tận, nhưng hệ quả là những ca như bài này bị dán nhãn Phân phối mà không có bằng chứng.
