# Chấm bài #19 — Tái phân phối (RE-DIST) · 2026-05-14 19:48 → 22:18 (49 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây. Đây là một đoạn nghỉ giữa xu hướng giảm M1, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Phase A dài đúng 1 nến — không có CHoCH nào cả — luật vi phạm: L2
- **Thuật toán gắn:** Phase A = 19:48 → 19:48 = **1 nến**. Trong đó AR (yếu) ở 19:34, SC? ở 19:38, ST[A] ở 19:48.
- **Đúng phải là:** Phase A = một CHoCH = đúng 3 lần đổi hướng, kết thúc tại ST[A]. Một nến không chứa nổi 3 lần đổi hướng.
- **Dấu hiệu quyết định trên chart:** thứ tự thời gian là **AR (19:34) → SC? (19:38) → climax mở range (19:48)**. AR đứng **trước** climax 14 phút. Cả 3 nhãn nằm trên cùng một đợt giảm liên tục 4704.8 → 4699.3 → 4693.1, đọc từ bảng sự kiện. Đó là ba mức giá thấp dần trong một move, không phải bật ngược → quay lại.
- **Nghi phạm trong thuật toán:** nhánh chọn nến mở range đang lấy **ST[A]** làm nến mở (climax mở range 4693.1 tại 19:48 trùng đúng nhãn ST[A]), đẩy AR/SC ra ngoài range. Kết hợp với lỗi nhãn cụm climax chưa vá (nhãn được phép nằm trước nến mở range) → toàn bộ Phase A rơi ra ngoài khung.

### 2. Không có MOVE hợp lệ trước climax — luật vi phạm: L1
- **Thuật toán gắn:** mở range, nhưng phiếu số liệu **không có dòng "MOVE truoc climax"** (so với bài #20, #21, #23, #24 đều có).
- **Đúng phải là:** không đủ điều kiện CẦN thì không mở range. Chính thuật toán cũng tự thú trong tiêu đề: *"SINH TU CHINH MOT CU PHA, khong co cao trao thuc su"*.
- **Dấu hiệu quyết định trên chart:** 12 nến quanh climax cho thấy giá bò từ 4697.9 xuống 4694.0 với volume 2-9 lot, VSA 0.49x–2.17x. Nến climax volume 18, VSA 3.50x nhưng biên độ chỉ **1.2 giá**. Đó là một nhịp trượt nhỏ trong downtrend, không phải cao trào chặn move.
- **Nghi phạm trong thuật toán:** guard L1 không chặn được khi dòng MOVE trống — cần biến điều kiện MOVE thành **bắt buộc cứng**, thiếu MOVE thì huỷ range.

### 3. Range 49 nến chứa đủ Phase A→E — luật vi phạm: "khung quá thô / range quá vụn" (CHART_CASES, Ca #4/#6/#19)
- **Thuật toán gắn:** A=1n, B=12n, C=11n, D=25n, E=1n trên tổng 49 nến; biên chính rộng 11.7 giá (0.25%).
- **Đúng phải là:** một TR M1 chỉ 49 nến mà đủ 5 phase phải nghi ngay là nhiễu. Nhìn ảnh: giá đi liền một mạch từ 4713 (18:49) xuống 4678 (23:23) — đoạn 19:48–22:18 chỉ là chỗ nghỉ giữa dốc.
- **Dấu hiệu quyết định trên chart:** panel volume gần như phẳng suốt range (thanh 1-4 lot), cây volume lớn nhất toàn ảnh nằm ở **23:42**, tức **ngoài** range hoàn toàn.
- **Nghi phạm trong thuật toán:** thiếu ngưỡng tối thiểu số nến / tối thiểu số lần chạm biên trước khi cho phép đóng đủ 5 phase.

### 4. Biên phụ dưới vô nghĩa (rộng hơn biên chính 4 tick) — luật vi phạm: L3
- **Thuật toán gắn:** biên chính dưới 4693.1, biên phụ dưới 4692.7. Tỷ lệ biên phụ/chính = **1.03x**.
- **Đúng phải là:** biên phụ chỉ có ý nghĩa khi ghi nhận một nỗ lực phá range **thật sự**. Chênh 0.4 giá = 4 tick là nhiễu tick, đúng ca "phá biên vài tick" mà vòng này muốn dẹp.
- **Dấu hiệu quyết định trên chart:** hai đường cam (liền 4693.1 và đứt 4692.7) sát nhau tới mức đè lên nhau trên ảnh.
- **Nghi phạm trong thuật toán:** điều kiện tạo biên phụ chưa áp ngưỡng tối thiểu (đề bài nói đã có +30 tick cho SOS/SOW nhưng chưa áp cho **việc sinh biên phụ**).

### 5. ST[A] trùng đúng nến climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 19:48 giá 4693.1 = đúng nến và đúng giá climax mở range.
- **Đúng phải là:** ST[A] là lần **quay lại** vùng climax sau khi đã bật lên AR. Nó không thể là chính cây climax.
- **Dấu hiệu quyết định trên chart:** cả hai cùng ghi 4693.1 / 19:48:00 trong phiếu.
- **Nghi phạm trong thuật toán:** ngưỡng STA_MIN_AR_FRAC=0.55 mới không cứu được ca này vì AR bị xác định **trước** climax → phép đo hồi bao nhiêu % khoảng AR↔climax bị vô nghĩa. Cần chặn cứng: `idx(AR) > idx(climax)`.

## Đạt
- Tên range RE-DIST khớp L4 (climax dạng SC + phá xuống thật) — nếu range này tồn tại thì tên đúng.
- Không spam nhãn: mỗi nhãn xuất hiện đúng 1 lần, LPSY[C]/LPSY[D] tách vai đúng trước/sau SOW (đúng bài học Ca #3 nguồn 4.pdf).
- SOW 20:14 VSA 2.65x, thân/biên 1.00 — chọn đúng cây phá có nỗ lực.
