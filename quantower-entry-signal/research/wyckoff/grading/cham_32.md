# Chấm bài #32 — Phân phối (DIST) · 2026-07-02 12:30 → 16:59 (269 nến M1)

**Điểm: 2/10** — Vùng đi ngang là thật, nhưng **mọi mốc đều neo sai**: range mở trên một cây tin (không có MOVE trước), AR chỉ 1 nến, hai nhãn UTAD đều sai chỗ, và cú SOW dùng để đặt tên "Phân phối" đã **thất bại ngay sau đó**. Phải vẽ lại từ đầu.

## Lỗi (nặng → nhẹ)

### 1. Không có MOVE trước climax — chính cây climax tạo ra "move" cho nó — luật vi phạm: L1
- **Thuật toán gắn:** BCLX 12:30 (VSA 13.73x, biên độ 61.8 giá), "MOVE trước climax dài 68.8 giá / 83 nến / hiệu suất 0.47".
- **Đúng phải là:** không mở range ở đây. Cây 12:30 (O4078.2 → H4138.5) **một mình đi 61.8 trong 68.8 giá** của cái gọi là MOVE. Trước nó, 83 nến (10:47→12:29) giá đi ngang trong khoảng **4074.9-4082.1 (≈7 giá)**. Đúng nguyên văn L1: "Giá đang đi ngang mà xuất hiện nến volume cao thì **không** được mở range."
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, đoạn bên trái mũi xám hoàn toàn phẳng; cả "move" là một cây nến dọc duy nhất (12:30 UTC = giờ ra số liệu Mỹ). Wyckoff cũng không có PSY nào trước BCLX này.
- **Nghi phạm trong thuật toán:** `_find_move()` tính độ dài move và hiệu suất hướng **bao gồm chính nến climax**, nên một cây gap/tin tự chứng minh điều kiện CẦN cho chính nó. Phải đo move tới nến `climax_i − 1` và loại ứng viên khi >70% độ dài move nằm trong 1-2 nến.

### 2. AR = đúng 1 nến sau climax → biên chính không phải biên đấu giá — luật vi phạm: L2 + L3
- **Thuật toán gắn:** AR (yếu) tại 12:31, giá 4117.3 → biên chính 4117.3-4138.5 (21.2 giá).
- **Đúng phải là:** AR phải là một **đợt phản ứng** thật, không phải cái low của nến kế tiếp. Biên đấu giá thật của phiên này là **4114.5-4157.1** — chính là cặp biên PHỤ mà bài đã vẽ nét đứt.
- **Dấu hiệu quyết định trên chart:** ngay sau "AR", giá quay lên **vượt hẳn mức climax 4138.5 tới 4157.1** và lượn quanh vùng 4121-4157 suốt 3 giờ. Đường nét liền trên 4138.5 nằm **giữa** đám nến chứ không đỡ/chặn gì — thấy rõ trên ảnh. Bài tự gắn nhãn "AR (yếu)" (AR cách climax ≤2 nến) nhưng vẫn dùng nó làm biên chính.
- **Nghi phạm trong thuật toán:** mục 4.1 — `AR_MIN_RETRACE_OF_MOVE = 0.30` thoả quá dễ (21.2 / 68.8 = 31%) vì mẫu số move đã bị cây tin bơm to. Nhãn "AR (yếu)" hiện chỉ để hiển thị, "không đổi logic" — ở đây nó **phải** đổi logic (loại ứng viên hoặc chờ AR thật).

### 3. UTAD #1 (13:50, 4157.1) gọi sai chỗ — luật vi phạm: CHART_CASES Ca #1/#3/#4 (4.pdf)
- **Thuật toán gắn:** UTAD tại đỉnh 4157.1, sau đó tự hạ thành "(thất bại)".
- **Đúng phải là:** đây là **đỉnh của range** (mức kháng cự cao nhất), không phải UTAD. UTAD chỉ là cú test cuối cùng **ngay trước khi cấu trúc sụp**; sau 13:50 giá còn lượn trong range **thêm 2 giờ 45 phút** (164 nến).
- **Dấu hiệu quyết định trên chart:** sau nhãn UTAD, giá còn tạo cụm đỉnh 4146-4152 ở 14:30-15:40 và một Phase B mới — đúng tiêu chí phân biệt của giảng viên: "nếu sau đỉnh vẫn còn dao động/hồi trong range → ST[B] hoặc UT thường". Ngoài ra nến đó VSA chỉ 1.21x, thân **0.12** (một cái râu).
- **Nghi phạm trong thuật toán:** mục 5.1 — "thăm dò THẬT" chỉ cần độ sâu ≥15 tick; vì biên chính trên bị đặt quá thấp (4138.5) nên cái râu này sâu 186 tick → tự động thành UTAD. Thiếu điều kiện về volume/thân cho cú rũ.

### 4. UTAD #2 (16:00, 4143.2) không phá được đỉnh range — luật vi phạm: L3 + CHART_CASES lỗi #6 (2.pdf, lỗi lặp nhiều nhất)
- **Thuật toán gắn:** UTAD "confirmed" tại 4143.2, thân **0.04** (nến doji), VSA 1.16x → mở Phase C rồi dẫn ra SOW.
- **Đúng phải là:** một cú rũ ở biên trên bắt buộc phải **vượt đỉnh cao nhất từng có của TR**. 4143.2 thấp hơn đỉnh 4157.1 tới **13.9 giá**. Đây chỉ là một cú test biên (UT/ST[B]), không phải UTAD.
- **Dấu hiệu quyết định trên chart:** nhãn UTAD nằm **dưới** đường nét đứt 4157.1 — nhìn ảnh thấy ngay.
- **Nghi phạm trong thuật toán:** mục 10 nói "đo một cú Spring/UTAD với **nét liền** (biên chính)". Sai với L3: phải đo với **biên PHỤ** (`r.high`/`r.low`), đúng như điều kiện đã áp cho SOS/SOW.

### 5. Cú SOW thất bại mà range vẫn chốt "Phân phối [completed]" — luật vi phạm: L10 + L4
- **Thuật toán gắn:** SOW 16:34 (close 4115.8 — chỉ **1.5 giá = 15 tick** dưới biên chính 4117.3, VSA 1.71x), Phase D 26 nến, tên range **Phân phối**.
- **Đúng phải là:** L10 đòi "phá biên, hồi về retest nhưng **giữ được** ở ngoài biên". Chỉ **4 nến** sau SOW, 16:38 đóng **4120.6** (cao hơn biên 3.3 giá = 33 tick), rồi giá leo tiếp lên 4131-4134 và ở đó tới hết ảnh. Cú phá bị phủ định hoàn toàn → chưa có hướng phá thật → theo L4 **chưa được đặt tên** cho range (vẫn phải là "Chưa rõ (BCLX)", tô xám).
- **Dấu hiệu quyết định trên chart:** nửa phải ảnh, sau chấm SOW giá quay lên nằm hẳn trên đường nét liền 4117.3.
- **Nghi phạm trong thuật toán:** `_fire_break()` gọi `_try_lps_and_phase_e(...)` nhưng **bỏ qua giá trị trả về**; hàm này đã phát hiện `failed` (close > level + 3.0 giá) và trả `False`, song `_fire_break` vẫn `r.state = 'END'` → range đóng, `r.dir` đã set nên vẫn được đặt tên pattern. Đây là bug thực thi, không phải lựa chọn spec.

### 6. Phase C 121 nến, Phase B chỉ 44 nến — luật vi phạm: L8 + L9
- Chuỗi phase: A 45 · **C 121** · B 35+9 = 44 · C 34 · D 26. Phase C là phase **dài nhất**, Phase B ngắn hơn cả Phase A. Nguyên nhân: `SHOCK_MAX_WAIT = 120` — Phase C được vẽ suốt thời gian **chờ** rồi mới bị hạ "thất bại", nên cửa sổ chờ bị hiển thị thành độ dài phase. Khi shock thất bại phải **cắt Phase C về đúng vài nến quanh điểm rũ** và trả phần còn lại cho Phase B.

### 7. Biên phụ dưới ghi 4114.5 trong khi đáy thật trong range là 4113.0 (16:37) — L3, lỗi nhỏ
- Sau khi SOW bắn, `r.low` không còn được cập nhật nên biên phụ đóng băng tại đáy nến SOW. Sai câu chữ L3 ("cực trị xa nhất").

## Đạt
- Nhãn "AR (yếu)" được phát hiện và hiển thị đúng — cảnh báo đã bật, chỉ tiếc là không dùng.
- Không spam nhãn: mỗi bên đúng 1 biên phụ, không có LPSY vẽ thành vùng, UT/UA không lặp.
- Phase C thứ hai (34 nến) ngắn hơn Phase B — đúng tinh thần L8 (nếu bỏ qua Phase C 121 nến ở trên).

## Cần hỏi người học
- Với nến tin kiểu 12:30 (một cây 61.8 giá, VSA 13.7x) thì muốn: (a) **bỏ hẳn** ứng viên, hay (b) coi cây tin là "giai đoạn xu hướng dọc" rồi mở range từ **đợt phản ứng đầu tiên sau nó** (biên = 4114.5-4157.1)? Lý thuyết không phân xử được ca này vì Wyckoff gốc không làm việc trên M1 có gap tin.
