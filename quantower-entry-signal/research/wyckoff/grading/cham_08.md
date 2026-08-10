# Chấm bài #08 — Chưa rõ (BCLX) (DIST?) · 2026-04-17 13:13 → 20:59 (266 nến M1)

**Điểm: 3/10** — Phase A đọc được, nhưng bài bỏ dở giữa chừng: giá phá biên dưới rồi đi mất mà thuật toán không nhận, không có Phase C/D/E, không đặt tên range, và biên phụ dưới sai hẳn.

## Lỗi (nặng → nhẹ)

### 1. Bỏ sót toàn bộ cú phá xuống — không có Phase C/D/E, range vẫn ghi "completed" — luật vi phạm: L4, L10
- **Thuật toán gắn:** chỉ có Phase A (49 nến) + Phase B (218 nến), tên range = "Chưa rõ (BCLX) (DIST?)".
- **Đúng phải là:** trên ảnh, từ khoảng 19:16 giá tuột hẳn dưới biên chính dưới 4909.2 và đi liền mạch xuống ~4886 và giữ ở đó tới hết range — đây là **SOW thật, có Phase D, có Phase E**. Range phải được đặt tên **Phân phối (DIST)**: move trước là tăng → BCLX, phá xuống thật → DIST (L4). "Chưa rõ" là không chấp nhận được khi giá đã đóng cửa dưới biên hàng chục nến.
- **Dấu hiệu quyết định trên chart:** biên chính dưới 4909.2; đáy trong range đọc trên ảnh ~4886 (thấp hơn biên 23 giá ≈ 230 tick), và cụm nến ở vùng đó kéo dài liên tục, không phải một cái quét.
- **Nghi phạm trong thuật toán:** điều kiện xác nhận SOW/breakout không kích hoạt trong range này; nhiều khả năng cửa sổ tìm Phase C bị hết trước (range đóng theo timeout) nên nhánh D/E không bao giờ chạy → cần cho phép gán C/D hồi tố khi phát hiện phá biên (đúng tinh thần L8: "có Phase D rồi mới xác định được Phase C").

### 2. Biên phụ dưới không phải cực trị xa nhất — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới **4908.8** (thấp hơn biên chính đúng **0.4 giá = 4 tick**), tỷ lệ phụ/chính 1.01x.
- **Đúng phải là:** cực trị xa nhất phía dưới trong range là ~4886 (đọc trên ảnh), tức biên phụ dưới phải nới xuống đó. Biên phụ 4908.8 vô nghĩa — nó chỉ ghi lại một cái ló 4 tick.
- **Dấu hiệu quyết định trên chart:** đường nét đứt dưới trên ảnh **trùng khít** đường nét liền 4909.2 (nhãn chữ chồng lên nhau) trong khi thân nến cuối range nằm thấp hơn hẳn.
- **Nghi phạm trong thuật toán:** biên phụ chỉ được cập nhật khi có sự kiện được gán nhãn (UA/UT/DA/ST[A]); vì cú rơi cuối không sinh nhãn nào (lỗi #1) nên biên phụ đứng yên. Biên phụ phải là hàm của **cực trị giá trong range**, không phải hàm của danh sách nhãn.

### 3. Nhãn BCLX đặt sai cây, sai cả giá lẫn vai — luật vi phạm: THEORY §4.1 (BCLX = cao trào MUA)
- **Thuật toán gắn:** `BCLX 13:18 · 4930.9 · VSA 5.30x`.
- **Đúng phải là:** climax mở range là cây **13:13, high 4953.8, VSA 3.31x** — đó mới là đỉnh chặn move. Cây 13:18 là nến nằm **5 nến sau**, thấp hơn 23 giá, và là nến trong đợt **rơi** sau climax (O 4923.7 → L 4922.4): gọi nó là "cao trào mua" là ngược nghĩa. Volume 124 của nó là volume của phe **bán** đang đổ ra.
- **Dấu hiệu quyết định trên chart:** trên ảnh, nhãn BCLX đỏ nằm rõ **dưới đỉnh**, cách đường biên chính trên 4953.8 một khoảng lớn.
- **Nghi phạm trong thuật toán:** nhánh "nhãn cụm climax = cây volume cao nhất trong cụm, không cần trùng cực trị" (đã biết, chưa sửa). Ở ca này nó kéo nhãn ra khỏi cả nến mở range.

### 4. Phase A dài 49 nến, Phase B 218 nến — không sai luật, nhưng B chưa kết thúc
- Chỉ ghi nhận: vì thiếu C/D/E nên Phase B "nuốt" 218 nến, trong đó đoạn cuối (từ ~19:16) thực chất đã là Phase D/E.

## Đạt
- **L1:** MOVE tăng 107.7 giá / 140 nến, climax chặn đúng tại đỉnh 4953.8 — điều kiện mở range rất rõ, đây là ca L1 đẹp.
- **L2 (một phần):** AR 4909.2 là cú bật ngược thật ngay sau climax (12 nến); ST[A] 4943.5 hồi **77%** khoảng AR↔climax, sát vùng climax → ST[A] ca này **không** lửng giữa range. Ngưỡng 55% chạy đúng ở bài này.
- **L3 (biên chính):** biên chính = climax 4953.8 + AR 4909.2, không bị kéo theo giá.
- **L6:** không còn nhãn ST[B].
