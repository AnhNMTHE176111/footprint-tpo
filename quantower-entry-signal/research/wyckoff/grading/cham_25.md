# Chấm bài #25 — Chưa rõ (SC) / mã nội bộ "ACC?" · 2026-06-04 14:53 → 06-05 02:56 (663 nến)

**Điểm: 4/10** — khung range mở đúng chỗ, nhưng ST[A] rơi giữa range làm Phase A phình lên 224 nến, mất hẳn Phase C, và nhãn SOW neo vào một cây doji. Sửa nhãn, không phải vẽ lại từ đầu.

## Lỗi (nặng → nhẹ)

### 1. ST[A] không phải test vùng climax — nó là một cái ngọ nguậy giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 18:36 tại 4500.0, chốt Phase A dài **224 nến**.
- **Đúng phải là:** ST[A] phải là nhịp quay về **phía climax** bị chặn lại, tức nằm ở 1/3 dưới của range (vùng 4483.8–4493.6). 4500.0 nằm ở **55% chiều cao** (biên chính 4483.8–4513.2, cao 29.4). Đây là một đáy giữa range, không phải test SC. Nhìn ảnh: chấm ST[A] nằm gần chính giữa hai đường liền cam.
- **Dấu hiệu quyết định trên chart:** hồi từ AR 4513.2 xuống 4500.0 = 13.2/29.4 = **45%** khoảng AR↔climax — vừa đủ vượt ngưỡng mới 0.4, tức ngưỡng v7 **không** chặn được ca này. Hệ quả dây chuyền: Phase A 224 nến so với Phase B 414 nến — Phase A gần bằng nửa Phase B, sai tỷ lệ mà L2/L9 hàm ý.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC` đo **từ AR xuống**, không đo **khoảng cách còn lại tới climax**. Cần thêm ràng buộc thứ hai: `|st_a − climax| ≤ ~0.35 × chiều cao range`. Đây đúng là lỗi đã ghi trong mục 13.1 ("ST[A] vẫn thiếu ràng buộc khoảng cách đáy tới climax") — nâng 0.2→0.4 **chưa** chạm tới nó.

### 2. Mất hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** timeline A(224) → B(414) → D(26). Không có Phase C.
- **Đúng phải là:** phá xuống thì trước đó phải có **LPSY[C]** — nhịp hồi cuối cùng lên phía biên trên trước cú sụp. Trên ảnh, nhịp hồi cuối ở khoảng 06-05 01:30 (đỉnh ~4482) là ứng viên LPSY[C] rõ ràng.
- **Dấu hiệu quyết định trên chart:** giá rời biên chính dưới 4483.8 từ khoảng 00:14, sau đó lùng bùng dưới biên suốt hơn 2 tiếng rồi mới có SOW — cả đoạn đó là Phase C + D chứ không phải Phase B.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược nới lên 0.8×B (=60 nến trần) **không cứu được**, vì ràng buộc v6 "pivot phải nằm **trong range** và đúng **nửa trên**" loại sạch mọi ứng viên — 60 nến trước SOW giá đã nằm hẳn **dưới** biên chính. Phải cho phép pivot nằm ngoài biên khi cú phá đã bắt đầu, hoặc đo nửa range theo **biên phụ**.

### 3. Nhãn SOW neo vào cây doji — luật vi phạm: THEORY §4.1 (SOW = spread + volume tăng), tham số "thân ≥ 45%"
- **Thuật toán gắn:** SOW 02:31 tại 4470.7, VSA 5.11× nhưng **thân/biên độ = 0.04**.
- **Đúng phải là:** cây phá thật phải có thân dứt khoát. Thân 4% = một cây rút chân/doji — nỗ lực lớn, kết quả không có, đây là dấu hiệu **hấp thụ**, ngược hẳn với ý nghĩa SOW.
- **Dấu hiệu quyết định trên chart:** cùng lỗi ở mSOW 01:00 (VSA 6.50×, thân 0.21).
- **Nghi phạm trong thuật toán:** khâu neo hồi tố chỉ chọn `argmax(VSA)` trong đoạn; điều kiện thân 45% đang áp cho nến **xác nhận** chứ không áp cho nến **được neo nhãn**. Bổ sung `body_ratio ≥ 0.45` vào bộ lọc argmax.

### 4. Nhãn SC nằm ngoài khung range — luật vi phạm: trình bày + L3 (mốc climax)
- **Thuật toán gắn:** SC tại 14:51, giá 4487.0 — **2 nến trước** mốc mở range (14:53) và **cao hơn** biên chính dưới 4483.8.
- **Đúng phải là:** nhãn climax phải nằm trong khung, tại đúng nến tạo mức 4483.8 (14:53, VSA 2.31×).
- **Nghi phạm trong thuật toán:** vá #4 vòng này ("kẹp theo nến mở range cố định") kẹp theo nến **ứng viên gốc**, trong khi mốc range đã dời sang cực trị mới → nhãn tụt lại phía sau. Phải kẹp theo `range.start_idx` **sau khi** cụm climax chốt xong.

### 5. (trình bày) Tiêu đề hiển thị mã "ACC?" cho một range đã có SOW
- Range đang ở trạng thái `superseded`, không đặt tên là đúng (L4 chưa đủ dữ kiện). Nhưng in mã nội bộ **"ACC?"** lên tiêu đề gây hiểu nhầm là tích luỹ trong khi trên chart có mSOW + SOW phá xuống. Đổi thành "Chưa rõ" trơn.

## Đạt
- L1: MOVE 50.6 giá / 68 nến / hiệu suất 0.46 là một đợt giảm thật, và cây climax là **đáy** của đợt đó — mở range đúng chỗ.
- L3: biên chính 4483.8–4513.2 cố định suốt range, biên phụ dưới 4477.5 đúng một cái, tỷ lệ 1.21× — không bị kéo theo giá.
- Chú thích nỗ lực/kết quả er=0.71 ghi đúng là "nhịp HIỆU QUẢ, không phải hấp thụ" — vá #1 vòng này **có tác dụng**.
- Phase B (414) là phase dài nhất — đúng L9.
