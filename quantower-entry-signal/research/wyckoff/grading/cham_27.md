# Chấm bài #27 — Tái phân phối (RE-DIST) · 2026-06-05 13:00 → 14:24 (84 nến)

**Điểm: 2/10** — đây không phải một vùng đấu giá, đây là một nhịp nghỉ 30 nến giữa đợt giảm. Không nên vẽ range ở đây; nếu vẫn vẽ thì ít nhất phải bỏ Phase B/D/E vì chúng vô nghĩa.

## Lỗi (nặng → nhẹ)

### 1. Nhãn SC nằm ngoài range, đúng bằng giá của AR — luật vi phạm: L3 + guard "climax trùng AR"
- **Thuật toán gắn:** SC tại **12:52, giá 4446.6** — trong khi range bắt đầu 13:00 và mức climax là **4425.2**. 4446.6 chính là mức **AR / biên chính TRÊN**.
- **Đúng phải là:** nhãn SC phải nằm ở đáy 4425.2 (nến 13:00, VSA 2.57×). Nhìn ảnh: chấm đỏ "SC" lơ lửng giữa dốc giảm, cách khung range 8 nến về bên trái và cao hơn cả biên trên.
- **Dấu hiệu quyết định trên chart:** SC (4446.6) = AR (4446.6) đúng đến một phần mười giá. Guard "climax trùng AR" lẽ ra phải bắn và bỏ ứng viên.
- **Nghi phạm trong thuật toán:** vá #4 ("kẹp theo nến mở range cố định") **chưa đủ** — nhãn vẫn được phép nằm ở nến ứng viên gốc, trước cả `range.start`. Phải kẹp `climax_ev ∈ [range.start, range.start + 8]` và giá nhãn phải bằng cực trị đúng phía (low cho SC).

### 2. Phase B chỉ 5 nến, ngắn hơn cả Phase A và Phase E — luật vi phạm: L9
- **Thuật toán gắn:** A(32) → B(**5**) → D(19) → E(29).
- **Đúng phải là:** Phase B là phase **dài nhất** — nơi xây nguyên nhân. Một "Phase B" 5 nến nghĩa là không có quá trình đấu giá nào, tức chưa có nguyên nhân nào được xây, tức không có range.
- **Dấu hiệu quyết định trên chart:** toàn bộ đoạn đi ngang chỉ kéo dài từ 13:01 tới 13:31 (~30 nến) rồi giá rơi tiếp theo đúng hướng cũ. Đây là một lá cờ giảm, không phải TR.

### 3. ST[A] không test được vùng climax — nó xuyên qua luôn — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:31 tại **4423.3**, tức **thấp hơn** mức climax 4425.2.
- **Đúng phải là:** lần đổi hướng thứ ba phải **bị chặn lại** ở vùng climax mới gọi là ST[A] và mới chốt được Phase A. Ở đây giá đi thẳng qua đáy cũ và 6 nến sau đã là SOW tại 4414.8 — không có "chặn" nào cả, CHoCH không hoàn thành.
- **Nghi phạm trong thuật toán:** ST[A] chỉ bị chặn bởi **trần** "vượt climax ≤ 1.0× chiều cao range"; cần thêm điều kiện định tính: sau ST[A] giá phải quay lại **vào trong** range ít nhất một nhịp, nếu nó phá luôn thì đó là SOW của Phase A, tức range chưa từng hình thành.

### 4. Không có Phase C — luật vi phạm: L8
- Timeline nhảy thẳng B → D. Với B chỉ 5 nến, cửa sổ gán ngược `0.8 × 5 = 4 nến` co gần về 0 → không tìm nổi pivot. Đây đúng là lỗi đã ghi ở mục 13.1 và vá #3 (0.5→0.8) **không** khắc phục được vì gốc rễ là Phase B quá ngắn.

### 5. AR (yếu) là một cái râu, không phải cú bật ngược — luật vi phạm: L2 (AR = cú bật ngược thật)
- AR 13:16 có **VSA 0.59×, thân 0.04**. Máy tự gắn cảnh báo "(yếu)" nhưng vẫn dùng nó làm biên chính trên. Đã biết là râu nhiễu thì nên **bỏ ứng viên**, không nên chỉ ghi chú rồi vẽ tiếp.

## Đạt
- L1: MOVE 42.2 giá / 40 nến / hiệu suất 0.68 là move giảm thật, và nến 13:00 là đáy của nó — điều kiện mở range về mặt số liệu thoả.
- L4: origin SC + phá **xuống** = Tái phân phối — tên gọi khớp bảng 4 mẫu hình (đây là mặt hiếm hoi bài này làm đúng).
- Chú thích nỗ lực/kết quả er=0.31 ghi "HIỆU QUẢ" — đúng dấu.

## Cần hỏi người học
- Có nên đặt một **sàn mềm** cho Phase B (ví dụ B phải ≥ A) để chặn loại "range" 84 nến này không? Người học đã chốt "không đặt sàn độ dài tối thiểu cho range", nhưng L9 (B dài nhất) tự nó đã là một sàn **tương đối** — chưa rõ có được dùng làm điều kiện huỷ hay chỉ là mô tả.
