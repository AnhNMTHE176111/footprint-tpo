# Chấm bài #53 — Tái phân phối (RE-DIST) · 2026-07-14 16:07 → 19:55 (228 nến M1)

**Điểm: 4/10** — chuỗi nhãn Phase B→D đọc mạch lạc, nhưng biên phụ dưới sai hẳn 10 giá, range không có cao trào thật, và nó vốn là nửa sau của range #52 bị cắt ra.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới bỏ qua chính cực trị xa nhất — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới **4061.8** (tỷ lệ biên phụ/chính 1.18×).
- **Đúng phải là:** **4051.3** — đáy của cây mSOW lúc 18:41 (VSA 7.78x). L3 nói rõ biên phụ = *mức cực trị xa nhất mà một thế lực đã cố phá range gốc tạo ra*, và cú thăm dò đó đã thất bại (giá quay lại trong range tới 4064.1) nên nó chính là ứng viên biên phụ chuẩn.
- **Dấu hiệu quyết định trên chart:** nét đứt cam dưới nằm ở 4061.8, trong khi chấm mSOW rơi tận đáy khung ở ~4051 — cách nhau **10.5 giá**, hơn cả chiều cao biên chính (8.9 giá).
- **Nghi phạm trong thuật toán:** cơ chế "phía đang test chỉ nới một lần sau khi biết kết cục" (mục 5.1 v6) không chạy cho nhánh hạ cấp `pending_shock → mSOW`, nên cú sâu nhất không bao giờ được ghi vào `out_edge`.

### 2. SOW chỉ vượt biên chính, chưa vượt biên phụ đúng nghĩa — luật vi phạm: L3
- **Thuật toán gắn:** SOW 19:30 tại 4055.6 (VSA 5.87x). So với biên phụ đang báo (4061.8) thì "mạnh"; nhưng so với cực trị thật 4051.3 (lỗi #1) thì **chưa vượt** — cú phá này không đi xa bằng cú thăm dò thất bại trước đó.
- **Đúng phải là:** đây chỉ là một cú phá tầm thường lặp lại vùng đã bị thọc; muốn gọi SOW mạnh thì phải đóng cửa dưới 4051.3.
- **Dấu hiệu quyết định:** đáy sau SOW (~4053) vẫn cao hơn đáy mSOW 18:41 (4051.3) — nỗ lực lần hai lớn hơn nhưng kết quả kém hơn, đúng dấu hiệu cạn kiệt mà thuật toán không đọc.

### 3. Range không có cao trào thật, sinh từ cú phá của range #52 — luật vi phạm: L1
- Phiếu ghi "SINH TU CU PHA, khong co climax that", nhãn `SC?` (VSA 2.31x, biên độ 5.2 giá), **không có dòng MOVE** nào.
- Range #52 kết thúc bằng SOW tại đúng nến 16:07 — tức range này bắt đầu ngay trên nến phá của range cha. Về mặt cấu trúc đây là **Phase D/E của #52** bị cắt ra làm range riêng, khiến cả hai đều mất tên hoặc mang tên nửa vời.

### 4. Phase E = 1 nến — luật vi phạm: L10
- Phase E 19:55 → 19:55. Sau SOW giá chỉ đi từ 4063.4 xuống ~4053 (1.2× chiều cao range) rồi lình xình quanh 4055–4062 tới hết ảnh. Không có "đi tìm vùng giá mới". Lỗi J của v5 vẫn tái phát ở dạng nhẹ.

### 5. ST[A] là một cây doji — cảnh báo chất lượng, không có luật chống lưng
- ST[A] 16:23 tại 4064.9, thân/biên độ **0.04** (doji gần như không thân), VSA 1.68x. Về vị trí thì đúng (hồi 83% khoảng AR↔climax, sát vùng climax). Chỉ ghi nhận: một doji làm mốc chốt Phase A là mỏng manh.

## Đạt
- Vị trí ST[A] (L2): 4064.9 so với climax 4063.4 — cách đúng 1.5 giá trên range 8.9 giá = test đúng vùng climax. Ngưỡng 0.55 mới ăn đúng ở ca này.
- Tỉ lệ phase đúng: B 170n dài nhất, C 16n ngắn nhất (L8, L9).
- Chuỗi Phase C đọc mạch lạc: mSOW (thăm dò thất bại) → LPSY[C] 19:14 tại 4064.1 (test lại đúng biên chính dưới 4063.4, một điểm duy nhất — L7) → SOW → LPSY[D] 19:38.
- Tên range khớp L4: origin SC + phá xuống = Tái phân phối. Đúng bảng 4 pattern.
- LPSY[D] (19:38, 4058.8) giữ được dưới biên chính — nhịp retest hợp lệ theo L10.
