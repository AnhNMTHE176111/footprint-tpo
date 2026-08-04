# Chấm bài #17 — Phân phối (DIST) · 2026-05-14 04:36 → 14:01 (352 nến M1)

**Điểm: 7/10** — Bài tốt nhất trong lô. Vùng đấu giá thật, tỷ lệ phase đúng luật (B dài nhất, C ngắn nhất), SOW neo đúng cây nổ. Chỉ cần sửa vài nhãn và thận trọng với kết luận "Phân phối".

## Lỗi (nặng → nhẹ)

### 1. Kết luận "Phân phối hoàn tất" đóng đúng lúc giá quay lại vào range — luật vi phạm: L10 (Phase E = giá đi tìm vùng giá mới) + cảnh báo Ca #22 nguồn 2.pdf
- **Thuật toán gắn:** Phase E 7 nến, range đóng `completed`, tên **Phân phối**.
- **Đúng phải là:** phần cuối ảnh cho thấy ngay sau 14:01 giá bật từ ~4723 lên ~4755, tức **trở lại hẳn TRONG range, vượt cả biên chính trên 4753.0**. Cú SOW này rơi được 20 giá rồi bị mua lại toàn bộ. Với diễn biến đó, đây là một SOW **thất bại**, chưa đủ để chốt tên "Phân phối".
- **Dấu hiệu quyết định trên chart:** cụm nến 14:08 trên ảnh có đỉnh cao hơn cả đường "biên CHÍNH trên 4753.0"; Phase E chỉ 7 nến, ngắn hơn cả Phase C (14 nến) — Phase E ngắn hơn Phase C là dấu hiệu tự tố cáo cú phá không đi đâu.
- **Nghi phạm trong thuật toán:** mục 7 cho chốt Phase E khi "hết 25 nến mà đã đi ≥50% chiều cao". SOW xuống 4707 = 28 giá dưới biên = 1.5 lần chiều cao 18.0 → thoả, nhưng máy chốt E xong **đóng range ngay** và không kiểm tiếp. Nên: đã chốt E thì vẫn theo dõi tới khi giá lùi hẳn vào biên (như spec nói) — ở đây điều đó xảy ra chỉ 7 nến sau, đủ để hạ SOW → mSOW.

### 2. LPSY[D] hồi lên trên biên phụ dưới — retest không "giữ được ngoài biên" — luật vi phạm: L10
- **Thuật toán gắn:** LPSY[D] tại **4731.4**; biên phụ dưới **4728.8**.
- **Đúng phải là:** L10 đòi nhịp retest **giữ được ở ngoài biên**. Điểm 4731.4 nằm **trong** biên phụ (dù vẫn dưới biên chính 4735.0). Nếu chấp nhận thì phải nói rõ đang đo với biên chính; còn nếu SOW được công nhận vì bứt biên phụ (L3) thì retest cũng phải đo bằng biên phụ — không thể đổi thước giữa hai bước.
- **Nghi phạm:** LPS/LPSY[D] tìm bằng swing pivot thuần cấu trúc (mục 7 câu 2), **không kiểm nó có còn ngoài biên hay không**.

### 3. Nhãn SOW rơi vào nến thân 0.38 (< ngưỡng 45% của chính spec) — lỗi nhất quán nội bộ
- **Thuật toán gắn:** SOW tại 4727.1, **VSA 6.12x, thân/biên độ 0.38**.
- **Đúng phải là:** spec đặt "thân ≥ 45% mới công nhận SOS/SOW", nhưng nhãn hồi tố chọn theo **VSA cao nhất** nên bỏ qua tiêu chí thân. Cây VSA 6.12x đúng là cây phá thật nên chọn vậy chấp nhận được — chỉ cần thống nhất: tiêu chí thân dùng để **xác nhận cú phá**, không dùng để **chọn nến gắn nhãn**. Hiện tài liệu không nói rõ chỗ này.

### 4. mSOS neo vào nến rỗng (lặp lỗi hệ thống của lô) — luật vi phạm: THEORY §2.2
- mSOS tại 4757.7, **VSA 0.65x, thân 0.00**. Cùng lỗi với bài #13/#15/#18: mSOS/mSOW neo cực trị giá thay vì cây có nỗ lực.

### 5. ST[A] chỉ đi được nửa đường về vùng BCLX — ghi nhận, không trừ điểm
- ST[A] 4743.3 trên range 4735.0–4753.0 = 46% chiều cao, không thực sự **test lại vùng climax**. Theo THEORY §5, ST ở 1/3 nửa dưới nghĩa "lực bán nhất định" — hợp lệ về lý thuyết cho một cấu trúc phân phối, nên chấp nhận. Ghi ở đây để đối chiếu với bài #18 (nơi ST[A] còn nông hơn nhiều và **là** lỗi).

## Đạt
- Điều kiện mở range (L1): MOVE tăng 38.0 giá / 23 nến / **hiệu suất 0.86** — chân tăng thẳng nhất trong lô, climax là đỉnh chặn move. Đạt.
- Phase A (L2): đủ 3 lần đổi hướng; **AR 4735.0 với VSA 4.17x, thân 1.00** — một cú bật ngược THẬT, không phải râu nhiễu. Kết thúc đúng tại ST[A]. Đạt.
- Biên (L3): biên chính 4735.0 + 4753.0 cố định; biên phụ đúng mỗi bên 1 cái (4728.8 / 4757.7) và đúng là cực trị xa nhất. Đạt.
- **Range này là một vùng đấu giá thật:** trên ảnh, từ 05:42 tới 13:13 giá lắc đi lắc lại trong 4728–4753, chạm cả hai biên nhiều lần — đúng nghĩa cân bằng (THEORY §2.3), khác hẳn bài #13/#18 nơi Phase B chứa cả một chân xu hướng.
- Tỷ lệ phase đúng luật: B 277 nến (dài nhất, L9) · **C 14 nến (ngắn nhất, L8)** · A 30 · D 25. Đây là bài duy nhất trong lô có tỷ lệ phase khớp cả L8 và L9.
- Phase C gán ngược (case khó): LPSY[C] 4746.4 ngay trước cú sụp, đúng nhịp hồi cuối — kiểu điểm giảng viên gọi "LPSY[C] tiềm năng" (Ca #3 nguồn 4.pdf). Và quan trọng: máy **không** gọi cú vượt biên trên 4757.7 ở Phase B là UTAD — tránh được đúng lỗi kinh điển #1 của 4.pdf.
- SOW neo đúng cây phá: VSA 6.12x, đóng cửa dưới biên phụ dưới. Lỗi B của v5 đã vá.
- Tên range (L4): BCLX + phá xuống = Phân phối. Khớp.
- Chỉ số Phase B: bias +0 (test cả hai biên) — đúng như hình; SOT hai phía "chớm" với volume 0.91 / 0.32 — đo đúng, chưa kết luận quá.
