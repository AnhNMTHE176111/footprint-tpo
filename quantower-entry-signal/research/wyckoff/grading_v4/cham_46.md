# Chấm bài #46 — Tái phân phối (RE-DIST) · 2026-07-22 22:00 → 2026-07-23 13:46 (945 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây. Toàn bộ biên dưới do **một cái râu của nến mở lại phiên** tạo ra, và cái gọi là "Phase B" thực chất là một nhịp xu hướng giảm hoàn chỉnh.

## Lỗi (nặng → nhẹ)

### 1. Climax là nến MỞ LẠI PHIÊN, biên dưới là một cái râu — luật vi phạm: L1 + L3, mục 1 & 3
- **Thuật toán gắn:** SC tại 4074.6, VSA 13.73x, biên độ nến 55.1 giá → lấy 4074.6 làm biên chính dưới.
- **Đúng phải là:** không mở range trên nến này. Nến trước nó là 20:59, nến climax là 22:00 — **lệch 61 phút**, tức đây đúng là cây đầu tiên sau giờ nghỉ phiên COMEX (21:00–22:00 UTC). Cây này mở 4126.0, thọc xuống 4074.6 rồi đóng lại 4119.9: **thân/biên độ = 0.11**. Đó là một cú hút thanh khoản lúc mở lại phiên, không phải một vùng giá được đấu giá.
- **Dấu hiệu quyết định trên chart:** biên độ riêng cây này (55.1 giá) chiếm **79% toàn bộ chiều cao biên chính** (69.4 giá). Và giá **không quay lại mức 4074.6 suốt 14 tiếng** (22:00 → 12:24 hôm sau) — một mức mà thị trường không chịu quay lại thì không phải biên của vùng cân bằng. Thêm nữa VSA 13.73x bị thổi phồng: 6 nến ngay trước climax có volume 12–20 lot (phiên chết trước giờ nghỉ), trong khi nến climax 1254 lot.
- **Nghi phạm trong thuật toán:** (a) điều kiện mở range (mục 3) không loại nến đầu phiên sau khoảng nghỉ dữ liệu; (b) VSA lấy trung bình 20 nến **bắc qua giờ nghỉ phiên** → mẫu số là volume phiên chết; (c) không có ràng buộc thân nến cho cây climax — thân 0.11 vẫn được nhận.

### 2. "Phase B (617 nến)" là một xu hướng giảm, không phải vùng đàm phán — luật vi phạm: L9, THEORY §2.3
- **Thuật toán gắn:** Phase B từ 02:06 đến 12:23, dài 617 nến, coi cả đoạn đó là giai đoạn xây nguyên nhân.
- **Đúng phải là:** đoạn 07:28 → 12:23 (~300 nến) là một **nhịp xu hướng giảm bậc thang**, đỉnh thấp dần và đáy thấp dần, đi từ vùng ~4130 xuống ~4078. Đó là "giai đoạn xu hướng" (THEORY §2.3 mục 1), không phải "giai đoạn đi ngang" (mục 3) — nơi duy nhất cấu trúc Phase A–E được phép diễn ra.
- **Dấu hiệu quyết định trên chart:** quãng giảm đó bằng **~52 giá = 75% chiều cao biên chính**, đi một chiều trong 300 nến. Nó "nằm trong range" chỉ vì biên dưới đã bị cái râu ở lỗi #1 kéo xuống quá thấp. Bỏ cái râu đó ra thì giá đã phá biên từ rất sớm.
- **Nghi phạm trong thuật toán:** trong Phase B mỗi nến chỉ được hỏi đúng một câu "có thò ra ngoài biên chính không?" (mục 5). Không có bất kỳ phép kiểm nào về **hình dạng bên trong** range (đỉnh/đáy thấp dần, hiệu suất hướng nội bộ) → một xu hướng nằm gọn trong hai biên rộng vẫn được coi là Phase B hợp lệ.

### 3. ST[A] là nhịp lùi giữa range, không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 4114.7 (02:05), đóng Phase A ở đó.
- **Đúng phải là:** ST[A] phải là cú quay về **phía climax rồi bị chặn lần nữa**. 4114.7 nằm cách climax 4074.6 tới 40 giá, tức **58% chiều cao range** — đó là giữa range. Giá chưa hề test lại vùng SC. Theo L2 "thiếu ST[A] thì Phase A chưa xong" → range này **chưa bao giờ hoàn thành Phase A**, đáng lẽ bị bỏ ứng viên.
- **Dấu hiệu quyết định trên chart:** lần đầu giá thật sự về vùng 4074.6 là 12:24 — và khi về thì nó **phá luôn**, không test.
- **Nghi phạm trong thuật toán:** ngưỡng "ST[A] phải hồi ≥ 40% chiều cao climax↔AR" (mục 4.2) quá lỏng: 40% × 69.4 = 27.8 giá, nên một nhịp lùi tới 4116 là đủ điểm. Ngưỡng này không ràng buộc ST[A] phải **gần mức climax**.

### 4. Nhãn AR không khớp biên chính do AR bị dời mà nhãn không dời — luật vi phạm: L3
- **Thuật toán gắn:** nhãn AR tại 4133.0 (22:30), nhưng **biên chính trên vẽ ở 4144.0**.
- **Đúng phải là:** hai số này phải là một (L3: biên chính = mức climax + mức AR). Lệch **11 giá = 16% chiều cao range**.
- **Dấu hiệu quyết định trên chart:** đường liền cam trên nằm đúng đỉnh cụm nến quanh 07-23 00:31, không nằm ở chấm AR màu xanh lúc 22:30.
- **Nghi phạm trong thuật toán:** mục 4.2 cho phép "giá phá xa hơn AR thì AR được dời tới cực trị mới" — code dời **biên** nhưng không dời **nhãn**. Hệ quả phụ đáng lo hơn: với Phase A dài 246 nến, luật dời này biến biên chính trên thành "đỉnh cao nhất 4 tiếng", không còn là cú bật AR.

### 5. Cú SOW thật bị chẻ thành 2 Spring(thất bại) + 2 LPS[C], rồi SOW gắn muộn trên nến 0.37x — luật vi phạm: L5, mục 8 & 9
- **Thuật toán gắn:** Spring(thất bại) 12:24 @4072.8 → LPS[C] 12:30 @4073.8 → Spring(thất bại) 12:37 @4066.5 → LPS[C] 12:45 @4068.4 → SOW 13:21 @4054.7.
- **Đúng phải là:** **một** sự kiện duy nhất — cú phá biên dưới bắt đầu 12:24. Theo L5, đóng cửa hẳn ngoài biên và các nến sau giữ nó ở ngoài thì đó là phá THẬT (SOW), không phải Spring. Cả 4 nhãn trước SOW đều nằm **dưới** biên chính dưới 4074.6 (4072.8 / 4073.8 / 4066.5 / 4068.4) — giá chưa từng lấy lại được vùng trong range, nên không có "Spring rút vào trong" nào cả.
- **Dấu hiệu quyết định trên chart:** nỗ lực thật nằm ở 12:20–12:45 — cụm thanh vàng cao nhất cả chart trên panel khối lượng, nến 12:24 VSA 2.36x. Nhãn SOW lại rơi vào nến 13:21 có **VSA 0.37x**, tức volume chỉ bằng 37% trung bình, sau khi giá đã rơi thêm 20 giá. Trái thẳng với THEORY §4.2 Phase D ("spread + volume tăng").
- **Nghi phạm trong thuật toán:** mục 5.1 kết cục B yêu cầu **3 nến liên tiếp** đóng cửa vượt biên phụ ≥30 tick, và code đóng dấu nhãn tại **nến xác nhận thứ 3** thay vì nến phá đầu tiên → nhãn luôn trễ và luôn rơi vào nến volume thấp. Lỗi này lặp ở cả bài #47 và #48 → là lỗi hệ thống, không phải ca lẻ.

## Đạt
- Tên range theo L4 đúng: origin SC + phá xuống thật = **Tái phân phối**, và bối cảnh (vàng giảm từ ~4150 về ~4040) khớp.
- L9 về mặt độ dài: Phase B (617) dài nhất; L8: Phase C (12 và 22 nến) ngắn nhất.
- L7 đúng: LPS[C] chỉ đánh 1 điểm, không vẽ vùng.
- Đọc effort↔result Phase B thực tế ủng hộ tên đã gán: volume gần như tắt từ 02:00 đến 07:28 rồi tăng mạnh với nhiều thanh vàng từ 10:56 — đúng "dấu hiệu khối lượng #2" của phân phối (THEORY §4.4).
- Không xoá range khi phá "sai hướng" so với origin SC — đúng L4, đây là chỗ bản trước làm sai.

## Cần hỏi người học
- Có nên **cấm mở range trên nến đầu tiên sau khoảng nghỉ phiên** (21:00–22:00 UTC) và cấm dùng biên độ của nến đó làm biên range không? Không luật nào trong L1–L10 phân xử ca này, nhưng nó là nguyên nhân gốc của cả bài #46.
