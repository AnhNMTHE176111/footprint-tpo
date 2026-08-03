# Chấm bài #34 — Phân phối (DIST) · 2026-07-07 12:09 → 16:18 (249 nến M1)

**Điểm: 3/10** — Đọc đúng **hướng** (đây là phân phối), nhưng **neo sai cây climax**: giá còn tăng thêm 8.9 giá trong 93 nến sau "BCLX", nên toàn bộ biên và Phase A lệch. Range phải vẽ lại từ đỉnh 13:42.

## Lỗi (nặng → nhẹ)

### 1. BCLX không chặn được move — climax nằm GIỮA move — luật vi phạm: L1 (mục 1 rubric: "climax là cực trị hay nằm giữa move?")
- **Thuật toán gắn:** BCLX 12:09, giá 4183.5, VSA 2.78x → biên chính trên 4183.5.
- **Đúng phải là:** đỉnh thật của đợt tăng là **4192.4 tại 13:42** — cao hơn "BCLX" **8.9 giá** và muộn **93 nến**. Cấu trúc đúng phải là: **BCLX ≈ 13:41-13:42** (13:41 VSA 2.52x, 453 lot — nến mạnh nhất vùng đỉnh) → **AR = 4154.5 (14:42)** → **ST[A] = 4166.7 (15:08)** → biên chính **4154.5-4192.4**. Đọc như vậy thì cú phá xuống dưới 4154.5 lúc 15:5x mới là SOW đúng vai.
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, đường nét liền 4183.5 bị xuyên qua liên tục trong toàn bộ Phase A (giá lượn 4176-4192 từ 12:10 tới 13:45) — nó không chặn gì. Đỉnh thật nằm ở đường nét đứt 4192.4.
- **Nghi phạm trong thuật toán:** mục 3 chỉ đòi nến climax là cực trị của **cửa sổ 240 nến nhìn về sau lưng**, không có điều kiện "giá không được tạo cực trị mới trong N nến kế tiếp". Ngoài ra đỉnh thật (13:42, VSA 1.39x) là dạng **cao trào cạn kiệt** (THEORY §6.2: xu hướng kết thúc bằng cầu cạn dần, không cần nổ volume) — bộ lọc `VSA ≥ 2.2x` không bao giờ bắt được loại đỉnh này.

### 2. Phase A dài 130 nến (52% cả range), dài hơn Phase B (49 nến) — luật vi phạm: L9 + L2
- **Thuật toán gắn:** A 130 (12:09→14:18) · B 49 · C 45 · D 26. AR nằm ở nến thứ **109** sau climax.
- **Đúng phải là:** Phase A là "sự dừng lại của xu hướng", đo bằng vài chục nến quanh đỉnh; Phase B mới là phase dài nhất. Ở đây Phase A đã nuốt cả đoạn giá vẫn đang **tăng** (12:10→13:42) — tức nuốt luôn phần cuối của xu hướng cũ.
- **Dấu hiệu quyết định trên chart:** vạch tím "Phase A (130n)" trải từ trước đỉnh 4192.4 sang tận 14:18.
- **Nghi phạm trong thuật toán:** `AR_MAX_WAIT = 300` cho phép chờ AR gần như vô hạn; điều kiện `AR_MIN_RETRACE_OF_MOVE = 0.30` (0.3 × 52.9 = 15.9 giá) chỉ được thoả ở 13:58. Cần huỷ ứng viên khi giá tạo **cực trị mới cùng phía climax** trong lúc chờ AR (thay vì lặng lẽ nới `r.high`).

### 3. Nhãn AR (4167.3) không trùng biên chính dưới (4161.9) — luật vi phạm: L3
- **Thuật toán gắn:** AR tại 13:58 giá 4167.3; biên chính dưới vẽ ở **4161.9** (đáy nến 14:14).
- **Đúng phải là:** hai số phải trùng theo định nghĩa L3. Lệch **5.4 giá**.
- **Dấu hiệu quyết định trên chart:** chấm AR nằm cao hơn đường nét liền dưới một khoảng thấy rõ bằng mắt.
- **Nghi phạm trong thuật toán:** giống bài #33 — state `A_st` dời `r.ar_price` xuống 4161.9 (nến 14:14) nhưng **event AR không được cập nhật**.

### 4. ST[A] không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 14:18 giá 4170.8 — cách BCLX 4183.5 tới **12.7 giá**, hồi đúng **41%** (ngưỡng 40%, vừa đủ lọt).
- **Đúng phải là:** ST[A] của một cấu trúc phân phối phải quay lên **tiệm cận vùng BCLX** với volume/spread co lại. Nến 14:18 chỉ 204 lot / VSA 0.91x và dừng ở nửa dưới range → theo THEORY §5, test ở 1/3 dưới nghĩa là "lực bán nhất định", không phải ST của đỉnh.
- **Nghi phạm trong thuật toán:** `STA_MIN_RETRACE = 0.40` — quá lỏng (lặp lỗi ở #33, #35).

### 5. SOW neo vào nến 41 lot vì "hết giờ chờ", bỏ mất cây phá thật — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** SOW 15:53, close 4152.1, **VSA 0.66x / 41 lot**, thân 0.63.
- **Đúng phải là:** cây phá thật là **15:54: 370 lot, VSA 4.70x**, thân 0.71, close 4149.0 — đúng định nghĩa SOW ("biên độ + khối lượng tăng, cam kết dưới hỗ trợ").
- **Dấu hiệu quyết định trên chart:** thanh vàng cao vọt ngay **bên phải** chấm SOW; chấm SOW đứng trên một thanh gần như không thấy.
- **Nghi phạm trong thuật toán:** SOW ở đây **không** bắn bằng 3 nến quyết đoán (không nến nào đóng dưới `out_edge − 3.0 giá = 4151.5`) mà bằng `BREAK_MAX_WAIT = 40` — "ở ngoài quá 40 nến không quay lại". Nhãn vì thế rơi vào nến thứ 41 một cách tuỳ tiện. Khi bắn bằng timeout, phải stamp lại tại **nến khối lượng lớn nhất của đoạn phá** hoặc tại `k['start_i']`.

### 6. Phase D chỉ đi được 0.35 × chiều cao range mà range vẫn "completed" mang tên Phân phối — luật vi phạm: L10 + L4
- **Thuật toán gắn:** Phase D 26 nến, không có Phase E, tên **Phân phối**.
- **Đúng phải là:** từ biên bị phá 4154.5, giá chỉ xuống tới **4146.9 (15:55) = 7.6 giá**, so với chiều cao range 21.6 giá → chưa tới cả mốc tối thiểu 50% (10.8 giá). Trong 25 nến sau đó giá bò ngược lên 4154.5. Cú phá này chưa "tìm được vùng giá mới" → chưa đủ để đặt tên pattern.
- **Nghi phạm trong thuật toán:** `_try_lps_and_phase_e()` đã trả `False` (chưa đủ tiến độ) nhưng `_fire_break()` **bỏ qua giá trị trả về** và vẫn `state = 'END'`. Cùng một bug với bài #32.

## Đạt
- **L1 (phần MOVE):** move tăng 52.9 giá / 160 nến / hiệu suất 0.36 là move thật, thấy rõ trên ảnh — điều kiện CẦN có thật, chỉ chọn sai cây chặn nó.
- **L4 (hướng):** phá xuống từ origin BCLX = Phân phối. Chiều đọc đúng.
- **L8:** Phase C (45 nến) ngắn hơn Phase B (49 nến) — bài duy nhất trong lô 31-35 không phình Phase C.
- **L3/L7:** DA (14:42, 4154.5) giữ đúng 1 cái ở cực trị và nới biên phụ đúng cách; LPSY[C] và LPSY[D] mỗi cái 1 điểm, tách đúng vai trước/sau SOW (không mắc lỗi gộp LPSY[C]/LPSY[D] của Ca #3 nguồn 4.pdf).
- Không có nhãn UTAD bịa ra — bài chấp nhận "case khó" và gán ngược LPSY[C], đúng tinh thần L8.

## Cần hỏi người học
- Không có.
