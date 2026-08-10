# Chấm bài #02 — Tái tích luỹ (RE-ACC) · 2026-01-08 23:07 → 2026-01-09 15:23 (67 nến M1)

**Điểm: 6/10** — cấu trúc và tên range đúng, chỉ cần sửa nhãn climax và cắt Phase E cho đúng; đây là bài khá nhất trong lô.

## Lỗi (nặng → nhẹ)

### 1. "BCLX" là nến biên độ 0.4 giá — không phải cao trào — luật vi phạm: THEORY §4.1 (BCLX = volume + spread tăng rõ rệt)
- **Thuật toán gắn:** BCLX tại 4587.0, O=4586.6 H=4587.0 L=4586.6 C=4587.0, **biên độ 0.4 giá**, volume 20 (VSA 4.88x).
- **Đúng phải là:** nếu vẫn muốn mở range ở đây thì phải gọi đúng tên là **climax cạn kiệt** (THEORY §6.2), không phải BCLX kinh điển. Một cây chặn move 53.7 giá mà chỉ nhấc được 0.4 giá là "cầu biến mất", không phải "cầu đạt đỉnh".
- **Dấu hiệu quyết định trên chart:** chấm BCLX trên ảnh nằm sát biên chính trên, nhưng thân nến gần như không nhìn thấy; cây volume cao thật nằm ở **-6 nến (18:29, volume 37, VSA 12.13x)** — cao gấp đôi cây được gọi climax.
- **Nghi phạm trong thuật toán:** điều kiện "biên độ ≥ 1.4× TB 20 nến" bị vô hiệu trong phiên chết vì TB 20 nến lúc đó ≈ 0.2 giá. Đây đúng mục 12.1 đã tự nghi ngờ. Cần thêm sàn biên độ **tương đối với chiều cao range** (ví dụ ≥ 10% chiều cao range) chứ không chỉ tương đối với ATR.

### 2. Phase E chỉ 2 nến trong khi giá còn chạy 90 giá — luật vi phạm: L10
- **Thuật toán gắn:** E = 15:09 → 15:23 = **2 nến**, range đóng tại 4602 vùng.
- **Đúng phải là:** Phase E là giai đoạn giá **rời range đi tìm vùng giá mới**. Trên ảnh, sau khi range đóng giá còn đi liền một mạch lên **4690** (ngày 01-11/01-12) mà không lùi vào biên. Cắt E sau 14 phút là cắt đúng chỗ Phase E vừa bắt đầu.
- **Dấu hiệu quyết định trên chart:** toàn bộ nửa phải ảnh là một chuỗi nến xanh leo dốc đều, nằm hoàn toàn trên biên chính 4587 — đó mới là Phase E.
- **Nghi phạm:** mốc "đi xa 2.0× chiều cao range" đóng E. Chiều cao chỉ 19 giá → 38 giá là đạt ngay, trong khi cause của range (67 nến) nhỏ nhưng effect thực tế lớn hơn nhiều. Mốc tuyệt đối theo chiều cao range quá chặt với range hẹp.

### 3. "Nhịp nỗ lực/kết quả cao nhất trong Phase B" lại nằm ngoài Phase B — lỗi phiếu số liệu
- **Thuật toán gắn:** nhịp 1736..1739 tại **12:54** ghi là "trong Phase B", nhưng bảng Phase ghi Phase B kết thúc 12:53 và **12:54 chính là nến mở Phase C** (LPS[C]).
- **Đúng phải là:** cửa sổ đo phải cắt đúng tại biên Phase B.
- **Nghi phạm:** chỉ số Phase B được tính sau khi Phase C đã được gán ngược, nhưng đoạn đo chưa trừ lại phần bị Phase C lấy đi.

### 4. Chỉ số er đã đổi nhãn theo dấu, nhưng thang đo làm nó không bao giờ ≥1 — lỗi đo lường (cảnh báo cho vòng sau)
- **Thuật toán gắn:** `effort=2.36x` (VSA), `result=35.00` (biên độ/ATR), `er=0.07` → in "nhịp HIỆU QUẢ".
- **Đúng phải là:** lỗi hard-code "vùng hấp thụ NGHI VẤN" của v6 **đã được vá** (nhãn giờ đổi theo dấu er) — ghi nhận. Nhưng `effort` chạy trong khoảng 0.2–5 còn `result` chạy tới 35, nên `er` gần như **luôn** < 1 → nhãn mới lại thành hard-code ngược ("luôn hiệu quả"). Xem cả 4 bài có dòng này trong lô (02/03/04/05): er = 0.07 / 0.09 / 0.08 / 0.32, không bài nào ≥ 1.
- **Nghi phạm:** hai vế không cùng thang. Cần chuẩn hoá result theo cùng cách VSA chuẩn hoá volume (biên độ nhịp ÷ **biên độ trung bình các nhịp trong range**, không phải ÷ ATR nến).

### 5. Range 67 nến trải 16 giờ đủ A→E — nghi là nhiễu, không phải vùng đấu giá — luật vi phạm: L1 (mức cảnh báo)
- **Dấu hiệu quyết định:** 67 nến / 16h16 = ~1 nến/15 phút; panel volume gần phẳng suốt Phase A và B, chỉ có 2 cột vàng ở Phase C/D.
- Không hạ điểm nặng vì cấu trúc vẫn ra hình và cú SOS sau đó là thật, nhưng cần ghi nhận.

## Đạt
- **Tên range đúng (L4):** origin BCLX + phá thật lên trên = **Tái tích luỹ**. Đúng bảng 4 pattern.
- **Tỉ lệ phase đúng (L8, L9):** B=27 dài nhất, C=14 ngắn hơn B, D=9. Đây là bài duy nhất trong lô 6 bài làm đúng cả hai luật tỉ lệ.
- **ST[A] đúng vai (L2):** 4584.0 = **84% chiều cao**, test sát mức BCLX 4587.0 với VSA 0.29x (volume co lại) — đúng định nghĩa ST của THEORY §3.3. ST[A] chặt hơn hẳn v6.
- **SOS thật (L10, mục 8):** 4601.9, VSA **8.14x**, thân 0.89, đóng cửa vượt hẳn biên chính 4587 — cây phá thật, nhãn đặt đúng cây chứ không rơi vào nến xác nhận thứ 3.
- **Biên (L3):** không có biên phụ (tỷ lệ 1.00x) — hợp lệ, L3 cho phép 0 biên phụ. Biên chính cố định đúng climax+AR.
- **Phase C gán ngược hợp lý (L8 case khó):** LPS[C] 4572.2 nằm trong range, đúng **nửa dưới**, ngay trước cú SOS — đúng cách "có Phase D rồi mới vẽ được Phase C".
