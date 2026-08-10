# Chấm bài #39 — Tái tích lũy (RE-ACC) · 2026-06-21 23:10 → 06-22 02:55 (225 nến M1)

**Điểm: 3/10** — Tên range đúng và Phase E chạy thật, nhưng Phase A chưa hoàn tất CHoCH: cái được gọi ST[A] chính là cú phá lên, nên Phase B bị nén còn **4 nến** — ngắn hơn cả Phase C lẫn Phase D.

## Lỗi (nặng → nhẹ)

### 1. ST[A] vượt lên TRÊN mức climax — đó là cú phá, không phải test — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 00:17, giá **4187.7**, trong khi mức climax = 4181.5.
- **Đúng phải là:** ST[A] là "quay lại phía climax rồi **bị chặn** lần nữa". Điểm này không bị chặn — nó vượt climax **6.2 giá** và trở thành biên phụ trên. Phase A ở đây mới có **2 lần đổi hướng** (move tăng bị chặn → lùi tới AR → tăng lại và phá luôn) → chưa đủ CHoCH, chưa được chốt Phase A.
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm ST[A] nằm **đúng trên đường nét đứt "biên phụ trên 4187.7"**, cao hơn hẳn nét liền 4181.5. Nến đó VSA 0.99x, thân **0.02** — một cây râu, không phải cây test có ý nghĩa.
- **Nghi phạm trong thuật toán:** trần "ST[A] vượt climax ≤ 1.0× chiều cao range" quá lỏng (6.2/28.6 = 22% nên lọt). Vượt climax dù chỉ một chút đã là mâu thuẫn khái niệm — nên đổi sang trần theo dung sai chạm biên (10 tick), không phải 1.0× chiều cao.

### 2. Phase B chỉ 4 nến, ngắn hơn Phase C (8) và Phase D (25) — luật vi phạm: L9 + L8
- **Thuật toán gắn:** A=68 · B=**4** · C=8 · D=25 · E=121.
- **Đúng phải là:** B là phase dài nhất, C ngắn nhất. Ở đây thứ tự đảo ngược hoàn toàn.
- **Dấu hiệu quyết định trên chart:** Phase B = 00:18 → 00:21, đúng 4 phút. Không thể có "giai đoạn xây dựng nguyên nhân" trong 4 nến M1.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của lỗi 1. Chưa có kiểm tra hậu nghiệm tỉ lệ phase (đã ghi ở 13.1b là ứng viên v8, chưa làm).

### 3. SOS không bứt qua biên phụ, còn THẤP HƠN chính điểm ST[A] — luật vi phạm: L3
- **Thuật toán gắn:** SOS tại 00:30, giá **4186.7**; biên phụ trên = **4187.7**.
- **Đúng phải là:** "SOS muốn thực sự mạnh phải đóng cửa bứt qua biên PHỤ". Cây này thiếu **1.0 giá** so với mức mà chính ST[A] đã chạm 13 nến trước — nó chưa chứng minh được gì mới.
- **Dấu hiệu quyết định trên chart:** trên ảnh nhãn SOS nằm ngay dưới đường nét đứt biên phụ. Thêm nữa VSA của cây SOS chỉ **1.03x** — không có nỗ lực tăng kèm theo, trong khi cây volume lớn nhất cả chart (thanh vàng cao nhất) nổ mãi ~01:05, tức đã ở giữa Phase E.
- **Nghi phạm trong thuật toán:** v7.1 đổi mốc quyết định decisive từ `out_edge` sang `edge` (biên chính). Sửa đó đúng chiều cho các ca "hàng trăm nến ngoài biên không được công nhận", nhưng ở đây tạo ca **ngược lại**: công nhận SOS chưa qua biên phụ. Cần giữ hai tầng — biên chính để **không vô hiệu oan**, biên phụ để **xếp hạng "mạnh"**.

### 4. UT[B] gán Phase B nhưng thời điểm rơi vào đoạn Phase C — mâu thuẫn nội tại
- UT[B] @ 00:27, cột "Phase" ghi **B**, trong khi bảng phase ghi C = 00:22 → 00:29. Đây là nhãn mồ côi sinh trong Phase C rồi bị hạ cấp mà không được gán lại đoạn — lỗi số 6 của v6, còn dấu vết.

### 5. Nhãn BCLX nằm trước nến mở range 6 nến, thấp hơn biên chính trên 4.6 giá — L3 (ghi nhận, đã biết chưa sửa)
- BCLX @ 23:04 giá 4176.9 vs range mở 23:10 @ 4181.5. Trên ảnh nhãn BCLX nằm hẳn dưới nét liền biên trên.

## Đạt
- L1: MOVE tăng 24.6 giá / 70 nến / hiệu suất 0.39, chân move rõ trên ảnh (~4157 → 4181); climax là đỉnh của move, không nằm giữa move.
- L4: **RE-ACC đúng** — origin BCLX, phá lên thật, giá sau đó chạy tới 4238 (+57 giá = 2× chiều cao range).
- L10 phần E: Phase E 121 nến có độ dài thật, đúng "giá rời range đi tìm vùng giá mới".
- LPS[C] @ 00:22 VSA 0.13x — test volume cạn, đúng tinh thần No Supply (THEORY §6.4).

## Kết luận cấu trúc
Không nhận cách chia phase này. Nếu là tôi: Phase A **chưa xong** tại 00:17 — phải chờ một nhịp lùi về vùng 4181 rồi bị chặn mới có ST[A]. Cú 00:17 → 00:30 là **một cú phá liên tục**, phải gọi là SOS đặt tại cây mạnh nhất trong đoạn, và Phase C nếu có thì gán ngược về nhịp test 4179.1.
