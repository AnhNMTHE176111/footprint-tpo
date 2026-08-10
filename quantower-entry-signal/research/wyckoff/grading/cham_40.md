# Chấm bài #40 — Tái phân phối (RE-DIST) · 2026-06-23 00:22 → 03:49 (207 nến M1)

**Điểm: 4/10** — Tên range đúng và cú SOW đọc đúng cây, nhưng ST[A] lại rơi giữa range, mSOW và SOW là **cùng một cú phá** bị tách làm hai, và Phase D mất hẳn nhịp retest.

## Lỗi (nặng → nhẹ)

### 1. ST[A] rơi lửng giữa range, không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 01:06, giá 4202.2.
- **Đúng phải là:** test lại vùng SC 4196.0. Điểm 4202.2 cách climax **6.2 giá trên tổng chiều cao 20.0 = 31%** — trên ảnh nhãn ST[A] treo giữa hai đường biên, không chạm cái nào.
- **Dấu hiệu quyết định trên chart:** sau AR (01:00 @ 4216.0) giá **rơi thẳng một mạch** xuống dưới 4188 lúc 01:33, không có nhịp dừng nào ở vùng 4196. Cái gọi ST[A] chỉ là một cái ngọ nguậy 6 nến trên đường rơi — đúng lỗi kinh điển giảng viên hay bắt.
- **Nghi phạm trong thuật toán:** giống bài #38 — `STA_MIN_AR_FRAC=0.55` đo được 0.69 nên lọt, trong khi đại lượng cần chặn là **khoảng cách còn lại tới climax**.

### 2. mSOW và SOW là cùng một cú rơi, cách nhau 4 nến — luật vi phạm: mục 5.1 (mSOW = cú phá **đã thất bại**, tức giá phải quay vào range)
- **Thuật toán gắn:** mSOW 01:33 @ 4185.5 (VSA 2.04x), rồi SOW 01:37 @ 4178.7 (VSA 5.63x).
- **Đúng phải là:** **một** nhãn SOW duy nhất, đặt hồi tố vào cây 5.63x. Giữa 01:33 và 01:37 giá **không hề quay lại trong range** — không có "cú phá thất bại" nào để gọi mSOW.
- **Dấu hiệu quyết định trên chart:** hai nhãn nằm sát nhau trên ảnh, cùng nằm dưới đường biên phụ 4188.0, chênh nhau 6.8 giá trong 4 nến — một đoạn rơi liên tục.
- **Nghi phạm trong thuật toán:** đúng ca "SOS cách mSOS vài tick" đã ghi ở 13.1b (bài #45 vòng v7) — nhánh hạ cấp `pending_shock` bắn nhãn minor rồi nhánh `_fire_break` bắn tiếp nhãn thật trên cùng một đoạn, không khử trùng lặp.

### 3. mSOW gán Phase B nhưng thời điểm nằm trong đoạn Phase C — mâu thuẫn nội tại
- mSOW @ 01:33, cột Phase ghi **B**, trong khi bảng phase ghi C = 01:27 → 01:36. Cùng lỗi nhãn mồ côi như bài #39.

### 4. Phase D thiếu hẳn LPSY[D] — luật vi phạm: L10
- **Thuật toán gắn:** Phase D = 12 nến (01:37 → 01:48), không có nhãn retest nào; đoạn hồi bị đẩy vào Phase E.
- **Đúng phải là:** nhịp hồi thật nằm ở 01:49 → 02:20 — trên ảnh giá bật từ ~4165 lên **4182**, tức lên **sát dưới** biên phụ 4188 rồi bị chặn. Đó chính là LPSY[D] sách vở: retest từ dưới lên và **giữ được ngoài biên**.
- **Nghi phạm trong thuật toán:** cửa sổ retest 25 nến sau SOW hết hạn trước khi nhịp hồi xảy ra; Phase E mở ngay khi giá chạy nhanh, nuốt mất nhịp hồi.

### 5. Diễn giải nỗ lực↔kết quả bỏ sót cây quan trọng nhất — mục 8 (Effort vs Result)
- **Thuật toán gắn:** "nhịp hiệu quả, er=0.25, không phải hấp thụ" cho một nhịp Phase B.
- **Đúng phải là:** cây đáng đọc nhất là chính **AR 01:00 — VSA 5.23x nhưng thân chỉ 0.06** (volume nổ, giá không đi đâu). Đó là nỗ lực lớn / kết quả nhỏ kinh điển, báo trước cú rơi 30 nến sau. Chỉ số chỉ quét Phase B nên bỏ qua hoàn toàn.
- **Nghi phạm trong thuật toán:** thêm nữa `effort` (VSA, thang 0.2–5) và `result` (biên độ/ATR, thang 1–3.3) khác đơn vị nên er gần như luôn <1 → luôn kết luận "HIỆU QUẢ" — lỗi đã bắt ở 13.1b, chưa sửa.

### 6. Climax chỉ 88 hợp đồng — ghi nhận, không tính lỗi
- Các nến quanh climax có volume 7 / 11 / 16 / 31 / 15 lot (phiên Á giờ chết). VSA 2.48x là ảo về tuyệt đối. Người học đã chốt không dùng sàn volume tuyệt đối nên không trừ điểm, nhưng đây là range xây trên thanh khoản gần bằng 0.

## Đạt
- L1: MOVE giảm 17.6 giá / 44 nến / hiệu suất 0.43; climax là đáy chặn move, không nằm giữa move.
- L4: **RE-DIST đúng** — origin SC, phá xuống thật; trên ảnh giá đi tiếp xuống 4144, thấp hơn biên phụ 44 giá.
- L8: Phase C = 10 nến, ngắn nhất; LPSY[C] @ 4198.3 nằm sát biên chính dưới 4196 — đúng vai test biên ngay trước cú phá.
- SOW đặt đúng cây VSA 5.63x thân 0.82 — hồi tố hoạt động đúng ở ca này.
- L3: biên chính cố định, 1 biên phụ dưới, tỷ lệ 1.40x.

## Kết luận cấu trúc
Vẽ range ở đây là hợp lý (một chỗ nghỉ 20 giá giữa đợt giảm 68 giá). Sửa: dời ST[A] hoặc thừa nhận Phase A chưa xong, gộp mSOW vào SOW, và kéo Phase D bao trọn nhịp hồi 01:49–02:20 để có LPSY[D].
