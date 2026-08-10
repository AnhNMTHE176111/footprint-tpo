# Chấm bài #06 — Chưa rõ (BCLX) (DIST?) · 2026-04-02 14:43 → 2026-04-02 20:59 (223 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây: cái được khoanh là **đoạn giữa của một cú giảm**, còn vùng cân bằng thật nằm thấp hơn và nằm sau. Đáng tiếc vì đây là bài duy nhất trong lô có dữ liệu dày, đọc được bằng mắt.

## Lỗi (nặng → nhẹ)

### 1. Range khoanh nhầm chỗ — vùng đấu giá thật nằm ở 4700–4740, thấp hơn — luật vi phạm: L1
- **Thuật toán gắn:** biên chính **4720.0 – 4762.2**, Phase A 45 nến rồi Phase B kéo 179 nến, đóng ở trạng thái "Chưa rõ".
- **Đúng phải là:** nhìn ảnh, sau khi BCLX chặn move tăng 95.5 giá, giá **rơi liên tục** qua 4720 xuống **4704.8**, rồi mới đi ngang **4700–4740 suốt hơn 4 giờ** (từ ~16:20 tới hết chart). Vùng đi ngang đó mới là vùng cân bằng. Cái được khoanh (4720–4762) chỉ là nửa trên của nhịp rơi — giá xuyên qua nó đi tiếp, đúng nghĩa "một đoạn xu hướng bị cắt ngang".
- **Dấu hiệu quyết định trên chart:** đường nét liền 4720.0 bị giá cắt qua cắt lại hàng chục lần ở nửa phải ảnh, không có vai trò hỗ trợ/kháng cự nào; trong khi biên phụ 4704.8 lại là mức giá được tôn trọng.
- **Nghi phạm trong thuật toán:** AR chốt tại pivot swing đầu tiên (4720.0, 15:25) thay vì tại đáy thật của cú phản ứng sau BCLX (4704.8, 16:20). Ràng buộc "AR ≥ 0.5× nhịp hồi lớn nhất trong lòng move" bắt được nhiễu, nhưng không bắt được ca AR chốt **quá sớm** khi cú giảm còn đang chạy.

### 2. Nến mở range VSA 0.24x — thấp hơn cả trung bình — luật vi phạm: mục 3 spec
- **Thuật toán gắn:** climax tại 14:43, **VSA 0.24x** (volume **2**), biên độ 3.7 giá.
- **Đúng phải là:** ngưỡng mở range là VSA ≥ 2.2x. Nến này ở mức **1/9 ngưỡng**. Đây là ca tệ nhất của lỗi "mức climax dời theo cực trị giá bất kể chất lượng nến": cụm quanh đó có 4 nến VSA 2.27x–6.61x (14:36 tới 14:44) nhưng mức lại rơi đúng vào cây 2 lot chỉ vì nó cao hơn 4.6 giá.
- **Dấu hiệu quyết định trên chart:** panel volume ở 14:36–14:44 có cụm cột vàng rõ; nến được chọn làm climax nằm giữa cụm đó nhưng cột volume của nó gần như không thấy.

### 3. Nhãn BCLX nằm ngoài khung range — luật vi phạm: L3
- **Thuật toán gắn:** BCLX tại **14:36** (giá 4756.0, VSA 6.61x), trong khi range bắt đầu **14:43**.
- **Đúng phải là:** nhãn phải nằm tại mức biên chính trên 4762.2, bên trong khung.
- **Dấu hiệu quyết định trên chart:** chấm BCLX vẽ **bên trái vạch tím Phase A**. Lệch chỉ 6.2 giá (nhẹ nhất trong lô 5 ca mắc lỗi này) nhưng vẫn cùng một lỗi: cửa sổ cụm quét ngược về trước nến mở range. Sửa #4 của v7 **chưa vá được**.
- Ghi nhận: nến 14:36 có thân **0.05** — gần như doji. Gọi nó là BCLX cũng khiên cưỡng.

### 4. ST[A] chỉ là một cái ngọ nguậy 3 nến giữa range — luật vi phạm: L2
- **Thuật toán gắn:** AR 15:25 (4720.0) → **ST[A] 15:28 (4737.6)**, cách nhau đúng **3 nến**; Phase A kết thúc ngay tại đó.
- **Đúng phải là:** ST[A] là lần đổi hướng thứ 3 — giá phải **quay lại phía climax và bị chặn lần nữa**. 4737.6 nằm ở **42% chiều cao range**, còn cách mức climax 4762.2 tới 24.6 giá (58% chiều cao). Đó không phải test lại vùng climax.
- **Dấu hiệu quyết định:** hồi từ AR = 17.6/42.2 = **0.42×** — vừa đúng qua ngưỡng mới 0.4 rồi dừng. Ngưỡng 0.4 đang siết sai đầu: nó ràng buộc khoảng cách tới **AR**, cái cần ràng buộc là khoảng cách tới **climax**. Lỗi #2 của v7 chỉ giảm chứ chưa hết (bài #01 ở 39%, bài #05 ở 36%, bài này 42%).
- **Nghi phạm:** `STA_MIN_AR_FRAC` = 0.4. Đề xuất thêm điều kiện thứ hai: ST[A] phải nằm trong ~30% chiều cao range tính **từ mức climax**.

### 5. mSOW gán trên nến VSA 1.20x — luật vi phạm: mục 8, sửa #5 chưa ăn hết
- **Thuật toán gắn:** mSOW 4704.8 (16:20), VSA 1.20x, thân 0.73.
- **Đúng phải là:** nến VSA cao nhất trong đoạn thăm dò. Trên panel volume, cụm 16:20 có cột cao hơn hẳn cột được chọn. Đỡ tệ hơn bài #03/#05 (0.54–0.57x) nhưng vẫn chưa đúng.
- **Đọc thêm:** cú xuống 4704.8 này thực chất **không phải** mSOW mà là **AR thật** — nó là đáy của cú phản ứng sau BCLX (xem lỗi 1).

### 6. Range đóng "completed" khi mới có A→B — lỗi trạng thái
- **Thuật toán gắn:** chỉ 2 phase (A, B), không có C/D/E, không có SOS/SOW, nhưng trạng thái ghi **completed** và tên "Chưa rõ (BCLX)".
- **Đúng phải là:** trung thực khi không đặt tên 4 pattern (đúng L4), nhưng "completed" cho một range chưa có một cú phá nào là gây hiểu nhầm. Nên là "đóng — chưa rõ hướng" như mục 13.3 điểm 3 đã mô tả.

## Đạt
- **Không ép đặt tên (L4):** giữ "Chưa rõ (BCLX)" khi chưa có cú phá xác nhận — đúng tinh thần không gò dữ liệu cho khớp mô hình (Ca #20 nguồn 7.pdf).
- **Biên (L3):** đúng 1 biên phụ dưới (4704.8), tỷ lệ 1.36x, do đúng cực trị xa nhất tạo ra, không tự nới thêm.
- **Ngưỡng phá 30 tick có tác dụng:** mSOW vượt biên chính 15.2 giá = 152 tick — không còn ca phá vài tick.
- MOVE trước climax là thật: 95.5 giá / 78 nến / hiệu suất 0.36, nhìn trên ảnh là một cú leo dốc rõ ràng từ 4657 lên 4762.

## Cần hỏi người học
- Khi cú phản ứng sau climax **chưa dừng** mà đã có một pivot swing hợp lệ (như 4720.0 ở đây), nên chốt AR tại pivot đó hay nên chờ tới đáy thật của cả đợt phản ứng (4704.8)? Luật L2 chỉ nói "hồi ngược tới AR" mà không định nghĩa dừng ở đâu; đây là chỗ quyết định range này khoanh đúng hay sai.
