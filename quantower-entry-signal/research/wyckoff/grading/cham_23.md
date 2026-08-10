# Chấm bài #23 — Tái phân phối (RE-DIST) · 2026-05-26 00:19 → 03:23 (179 nến M1)

**Điểm: 3.5/10** — Phase A vẽ rất đẹp, nhưng phần sau hỏng: nhận cú phá muộn ~90 nến và mất hẳn Phase C.

## Lỗi (nặng → nhẹ)

### 1. Hàng chục nến nằm ngoài biên mà vẫn tính là Phase B — luật vi phạm: L3 / L10
- **Thuật toán gắn:** Phase B = 00:41 → **02:56** (134 nến). SOW mãi 02:57.
- **Đúng phải là:** giá đã đóng cửa dưới biên phụ dưới 4573.4 từ khoảng **01:27** và rơi thẳng xuống ~4560 lúc 01:35, rồi bò quanh 4562-4575 suốt hơn 80 nến. Cú phá thật là ở 01:27-01:35; Phase D phải bắt đầu ở đó, không phải 02:57.
- **Dấu hiệu quyết định trên chart:** trên ảnh, từ mốc 01:27 trở đi **không còn một nến nào** chạm lại biên chính trên 4586.0; đường đứt biên phụ dưới 4573.4 bị xuyên qua và nằm phía trên toàn bộ đám nến còn lại. Panel volume cho thấy cụm nến cao nhất khu vực rơi đúng vào 01:27-01:35.
- **Nghi phạm trong thuật toán:** đây đúng ca số 3 mà đề yêu cầu kiểm — **vẫn còn** "hàng trăm nến ngoài biên không được công nhận". Điều kiện `outside/timed-out` đang so với biên **CHÍNH dưới 4574.6** + 30 tick = 4571.6; giá 4560 đã thoả từ lâu nhưng nhãn SOW vẫn không bật. Nghi phạm là ràng buộc phụ (volume/VSA tối thiểu cho SOW) đang chặn: SOW cuối cùng được gán có VSA chỉ **0.96x**, tức bộ lọc không phải volume mà là thứ tự phase.

### 2. Thiếu hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** bảng phase chỉ có A (20n) → B (134n) → **D (25n)** → E (1n). Không có C.
- **Đúng phải là:** L8 cho phép case khó (chỉ có LPSY[C], gán ngược sau khi thấy SOW), nhưng không cho phép **bỏ trống** phase. Với mốc phá đúng ở 01:27, Phase C là nhịp hồi thất bại quanh 01:20 ở ~4577-4580 (ngay chỗ mSOW 00:59 và các đỉnh thấp dần sau đó).
- **Dấu hiệu quyết định trên chart:** trên ảnh, giữa vạch tím "Phase B" và vạch tím "Phase D" là một khoảng trống 134 nến, trong đó có một chuỗi đỉnh thấp dần rõ rệt (SOT-dn phiếu ghi `SOT, n=4`) — đúng vật liệu để dựng Phase C.
- **Nghi phạm trong thuật toán:** nhánh gán ngược Phase C từ SOS/SOW chỉ chạy khi tìm được ứng viên LPSY trong cửa sổ hẹp trước SOW; vì SOW bị đặt muộn tới 02:57, cửa sổ đó rơi vào vùng đi ngang chết nên không có ứng viên nào.

### 3. Nhãn SC đặt giữa move giảm, cách nến mở range 18 nến — luật vi phạm: L1
- **Thuật toán gắn:** SC tại **00:01, giá 4583.4**, VSA 4.53x. Nến mở range là 00:19 tại **4574.6**.
- **Đúng phải là:** climax phải là cây chặn move, tức cực trị. 4583.4 cao hơn đáy move 8.8 giá.
- **Dấu hiệu quyết định trên chart:** nhãn SC đỏ trên ảnh nằm lưng chừng dốc giảm; cây đáy thật là nến 00:18 (low 4575.4, volume 49, VSA 3.50x) và 00:19 (low 4574.6).
- **Nghi phạm trong thuật toán:** lỗi **nhãn cụm climax chưa vá** (đã biết). Ghi nhận, không tính là trọng tâm vòng này.

### 4. LPSY[D] không giữ được ngoài biên — luật vi phạm: L10
- **Thuật toán gắn:** LPSY[D] 03:01 tại 4569.4, rồi Phase E dài 1 nến.
- **Đúng phải là:** CBR đòi retest **giữ được** ở ngoài biên rồi giá thuận lực đi tiếp. Ở đây ngay sau range giá bật lên 4580, tức trở lại **trong** biên phụ dưới 4573.4.
- **Dấu hiệu quyết định trên chart:** đoạn 03:10-03:35 trên ảnh nằm hẳn trên đường đứt 4573.4, cao nhất ~4580.
- **Nghi phạm trong thuật toán:** không kiểm điều kiện "sau LPSY[D], giá không được đóng cửa trở lại trong biên" trước khi tuyên Phase E.

## Đạt
- **L1 (MOVE) đạt:** MOVE giảm 25.7 giá / 59 nến, hiệu suất 0.47 — mũi xám vẽ đúng từ đỉnh 4614 xuống đáy, move rõ ràng bị chặn.
- **L2 đạt và đạt đẹp:** AR 00:31 (4586.0) bật ngược thật; ST[A] 00:40 tại 4576.7 hồi **(4586.0−4576.7)/11.4 = 82%** khoảng AR↔climax — test đúng vào vùng climax, không lửng giữa range. Đây là ca cho thấy ngưỡng 55% mới hoạt động tốt.
- **L3 (biên chính) đạt:** 4574.6 / 4586.0 = climax + AR, cố định, không kéo theo giá.
- **L4 đạt:** SC + phá xuống thật = RE-DIST, tên đúng.
- **L6 đạt:** không có nhãn ST[B].
- Đọc SOT tốt: phiếu ghi SOT phía dưới `n=4, thrust cuối/đầu = 0.12, volume cuối/đầu = 0.61 (cạn kiệt)` — đúng dấu hiệu bên bán mất đà ở đáy, và đúng là sau range giá hồi lên thật.
