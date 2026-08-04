# Chấm bài #13 — Tích luỹ (ACC) · 2026-05-04 15:22 → 2026-05-05 15:41 (660 nến M1)

**Điểm: 4/10** — Phase A và biên chính đặt đúng, nhưng range bị kéo dài bao trọn cả một chân tăng 18 giờ và **thiếu hẳn Phase C**; phải cắt range sớm hơn nhiều.

## Lỗi (nặng → nhẹ)

### 1. Range bao trọn một MOVE TĂNG, không còn là vùng cân bằng — luật vi phạm: L1 / mục 1 phiếu chấm (THEORY §2.3 "giai đoạn đi ngang")
- **Thuật toán gắn:** Phase B dài 488 nến, từ 05-04 15:52 tới 05-05 12:09, coi toàn bộ là "đấu giá trong range".
- **Đúng phải là:** vùng cân bằng thật chỉ kéo từ 15:22 tới khoảng 05-05 01:24 (giá lắc trong 4556–4575). Từ đó trở đi giá tạo chuỗi đáy cao dần 4556 → 4565 → 4578 → 4590 và **đóng cửa hẳn trên biên chính trên 4588.3** từ khoảng 05-05 05:13, ở trên đó gần như liên tục 7 giờ. Range phải đóng ở đó (SOS), phần sau là Phase D/E — không phải Phase B.
- **Dấu hiệu quyết định trên chart:** biên chính trên 4588.3 bị cắt qua và giá nằm trên nó suốt nửa sau Phase B; nhãn mSOS đặt ở 4603.8, tức **15.5 giá trên biên chính** = 54% chiều cao range (28.5 giá) — không ai gọi đó là "test biên" được.
- **Nghi phạm trong thuật toán:** điều kiện phá thật ở mục 5.1 kết cục B đòi **3 nến liên tiếp đóng vượt BIÊN PHỤ + 30 tick, thân ≥ 45%**. Biên phụ trên 4603.8 do chính cú thăm dò nới ra, nên khi giá bò lên chậm bằng nến nhỏ thì không nến nào thoả, và range sống thêm 7 giờ. Nhánh phụ "ở ngoài quá 40 nến và ≥60% nến đóng ngoài biên" cũng đo theo biên phụ nên cùng bị hụt.

### 2. Thiếu hoàn toàn Phase C — luật vi phạm: L8, và mục 6 "case khó" của chính spec
- **Thuật toán gắn:** dải phase A(27) → B(488) → **D(25)** → E(121). Nhảy thẳng B sang D.
- **Đúng phải là:** spec đã có cơ chế gán ngược (nhìn lại 60 nến trước cú phá, lấy nhịp test cuối làm LPS[C]) mà không chạy. Nhìn chart, trong khoảng 05-05 11:00–12:00 có một nhịp lùi rõ về ~4586 sát biên chính trên rồi bật lên phá — đó là LPS[C] hợp lý.
- **Dấu hiệu quyết định trên chart:** giữa vạch tím Phase B và vạch Phase D không có đoạn C nào; trên chart có đúng một nhịp hồi trước cú SOS 4607.1 (VSA 4.36x).
- **Nghi phạm trong thuật toán:** nhánh gán ngược Phase C có lẽ bị chặn khi range đã ghi sẵn một mSOS/mSOW (shock bị hạ cấp) — cần kiểm điều kiện "range chưa từng có Phase C" xem nó có tính cả shock đã hạ cấp không. Đối chiếu Ca #20 nguồn 7.pdf: giảng viên phê "gượng ép" đúng vì học viên nhảy phase.

### 3. Nhãn mSOS neo vào nến rỗng — luật vi phạm: THEORY §2.2 Nỗ lực ↔ Kết quả
- **Thuật toán gắn:** mSOS tại 4603.8, **VSA 0.51x, thân/biên độ 0.00** (nến doji thanh khoản rỗng).
- **Đúng phải là:** một cú phá thất bại là một **nỗ lực** — phải neo vào cây có volume, không neo vào nến cực trị giá. Nếu cả đoạn không có cây nỗ lực nào thì đó không phải mSOS, chỉ là giá trôi.
- **Dấu hiệu quyết định trên chart:** panel volume tại 05-05 09:08 không có thanh vàng nào.
- **Nghi phạm trong thuật toán:** mốc mSOS/mSOW lấy đúng nến cực trị của cú thăm dò; cần áp cùng cơ chế **hồi tố về cây VSA cao nhất** đã dùng cho SOS/SOW (lỗi B của vòng v5).

### 4. Cú thọc 4545.6 bị gọi mSOW nhưng nó là cú rũ sâu nhất range — ghi nhận, chưa chắc là lỗi
- Cú 05-04 16:10 xuống 4545.6 = 14.2 giá dưới biên chính dưới, là cực trị thấp nhất toàn range, và sau đó giá đi tới biên đối diện rồi vượt xa. Theo tiêu chí "đi ≥50% sang biên đối diện" thì cú rũ này XÁC NHẬN → đáng là Shakeout, Phase C.
- Nhưng nó cách SOS tới ~1200 nến, quá trần 120 nến của Phase C, nên hạ cấp là **đúng luật**. Ghi ở đây để không nhầm là bỏ sót.

## Đạt
- Điều kiện mở range (L1): MOVE giảm 52.1 giá / 32 nến / hiệu suất 0.70 — move xu hướng thật, climax là đáy chặn move. Đạt.
- Phase A (L2): đủ 3 lần đổi hướng, SC 15:21 → AR 4588.3 → ST[A] 4556.0, dài 27 nến, kết thúc đúng tại ST[A]. Đạt.
- Biên chính (L3): 4559.8 (climax) + 4588.3 (AR), cố định suốt range, không kéo theo giá. Đạt.
- Biên phụ (L3): mỗi bên đúng 1 cái, 4545.6 dưới / 4603.8 trên = cực trị xa nhất. Đạt.
- Tách nhãn/mức climax (cơ chế v6): nhãn SC ở nến 15:21 VSA 2.70x, mức ở đáy 4559.8 — chỉ lệch 1.0 giá, đọc được. Đạt.
- Tên range (L4): SC + phá lên = Tích luỹ. Khớp.
- Chỉ số Phase B mới: SOT phía dưới n=4, thrust cuối/đầu 0.09, volume 0.86 → "cạn kiệt" — **đo đúng bản chất**: đáy trong range ngắn dần đúng như hình. Bias +0 (test cả hai biên) cũng khớp chart.

## Cần hỏi người học
- Khi giá bò lên chậm bằng nến nhỏ và ở hẳn trên biên chính nhiều giờ mà không có 3 nến thân lớn nào: có nên cho SOS bắn theo **giá đóng cửa trung bình** của một cửa sổ (ví dụ 20 nến đóng trên biên) thay vì đòi 3 nến liên tiếp thân ≥45%?
