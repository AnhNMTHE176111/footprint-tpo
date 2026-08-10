# Chấm bài #21 — "Chưa rõ (BCLX) (DIST?)" · 2026-05-24 23:42 → 2026-05-25 02:14 (137 nến M1)

**Điểm: 5.5/10** — Khung range chấp nhận được, nhưng nhãn BCLX đặt sai chỗ và range không dám đặt tên.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX đặt giữa move tăng, không phải đỉnh chặn move — luật vi phạm: L1
- **Thuật toán gắn:** BCLX tại **23:07, giá 4607.9**, VSA 3.84x. Nhưng nến mở range là 23:42 tại **4615.4**.
- **Đúng phải là:** climax phải là cây **chặn** move, tức nằm ở cực trị. 4607.9 thấp hơn đỉnh 4615.4 tới 7.5 giá — nó nằm giữa dốc lên.
- **Dấu hiệu quyết định trên chart:** trên ảnh, nhãn BCLX đỏ nằm lưng chừng đoạn dốc lên, còn đỉnh thật (nơi biên chính trên 4615.4 cắt qua) ở xa bên phải. Nến mở range thật (23:42) chỉ có VSA **1.16x**, volume 13.
- **Nghi phạm trong thuật toán:** lỗi **nhãn cụm climax chưa vá** (đã biết, bị revert). Nhãn lấy "cây volume cao nhất trong cụm" nên nhảy về 23:07; đề bài ghi rõ mục này chưa sửa. Đây là ca minh hoạ điển hình: chênh 35 nến và 7.5 giá.

### 2. Range không được đặt tên — luật vi phạm: L4
- **Thuật toán gắn:** tiêu đề "Chưa rõ (BCLX) (DIST?)", trạng thái `superseded`, ghi chú "khong dat ten 4 mau hinh".
- **Đúng phải là:** L4 nói rõ đủ **4 pattern**, hướng MOVE quyết định loại climax, hướng phá thật quyết định tên. MOVE tăng + phá **xuống** (SOW 01:46 tại 4594.9, dưới biên chính dưới 4601.5 tới 6.6 giá = 66 tick) → **DIST**, không có gì "chưa rõ".
- **Dấu hiệu quyết định trên chart:** SOW và LPSY[D] đều nằm dưới biên chính dưới; giá sau đó bò quanh 4592-4600, không lấy lại range.
- **Nghi phạm trong thuật toán:** trạng thái `superseded` đang **chặn** bước đặt tên. Việc bị range sau thay thế không xoá đi sự thật là range này đã phá xuống — nên tách "đặt tên" khỏi "trạng thái vòng đời".

### 3. mSOW ở Phase B phá biên sâu hơn cả SOW ở Phase D — luật vi phạm: L3 / L8
- **Thuật toán gắn:** mSOW 01:10 tại **4596.3** (Phase B) → tạo biên phụ dưới 4595.2; SOW 01:46 tại **4594.9** (Phase D).
- **Đúng phải là:** SOW của Phase D chỉ hơn mSOW của Phase B đúng **1.4 giá**, và chỉ vượt biên phụ 4595.2 đúng **0.3 giá = 3 tick**. Theo L3, "phá thật" phải bứt qua **biên phụ** — 3 tick không phải bứt. Cú ở Phase D này thực chất là lần chạm lại đúng vùng mSOW, tức vẫn là test biên, chưa phải MSOW.
- **Dấu hiệu quyết định trên chart:** hai điểm mSOW và SOW nằm gần như cùng độ cao, đều dính vào đường đứt 4595.2.
- **Nghi phạm trong thuật toán:** ngưỡng +30 tick mới áp cho biên **chính**; qua biên **phụ** vẫn không có ngưỡng → vẫn còn ca "phá biên vài tick" đúng như câu hỏi số 3 của đề.

### 4. Không có Phase E dù range đóng bằng một cú phá — luật vi phạm: L10
- **Thuật toán gắn:** Phase D = 01:46 → 02:14 (26 nến), hết range, không có E.
- **Đúng phải là:** hoặc có Phase E (giá rời range đi tìm vùng mới), hoặc phải kết luận cấu trúc **thất bại** (THEORY §9) vì giá không đi được về phía đối diện.
- **Dấu hiệu quyết định trên chart:** sau LPSY[D] 01:54, giá chỉ dao động 4592–4606 tới 02:56 — chưa hề rời vùng. Đây đúng nghĩa "cấu trúc thất bại", không phải Phase E.

## Đạt
- **L1 (phần MOVE) đạt:** MOVE tăng 36.1 giá / 99 nến, hiệu suất 0.47, mũi xám vẽ đúng chân move từ 4562.7.
- **L2 đạt:** AR 23:59 (4601.5) là cú bật ngược thật; ST[A] 00:11 tại 4610.6 hồi **(4610.6−4601.5)/13.9 = 65%** khoảng AR↔climax → qua ngưỡng 55% mới, và nó test đúng vùng đỉnh chứ không lửng giữa range. Vá v7.1 hiệu quả ở đây.
- **L8 đạt về độ dài:** A 30n, B 69n, C **13n** (ngắn nhất), D 26n — tỷ lệ đúng chuẩn, Phase C không phình.
- **L9 đạt:** Phase B 69 nến, dài nhất.
- **L7 đạt:** LPSY[C] và LPSY[D] mỗi cái đúng 1 điểm, không vẽ vùng, tách vai đúng trước/sau SOW.
- **L6 đạt:** không dùng nhãn ST[B] trong bài này.
