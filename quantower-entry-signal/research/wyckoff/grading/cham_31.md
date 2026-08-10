# Chấm bài #31 — Tái phân phối (RE-DIST) · 2026-06-05 13:00 → 14:24 (84 nến M1)

**Điểm: 3/10** — không nên vẽ range ở đây: đây là một nhịp nghỉ (bear flag) giữa đợt giảm, không phải vùng đấu giá; và nếu cố vẽ thì cấu trúc phase đã hỏng (Phase B chỉ 1 nến).

## Lỗi (nặng → nhẹ)

### 1. Phase B chỉ 1 nến, Phase A dài nhất — luật vi phạm: L9 (+ L2)
- **Thuật toán gắn:** A=32n, **B=1n**, C=4n, D=19n, E=29n. Toàn bộ "nguyên nhân" của range được xây trong đúng 1 nến (13:32).
- **Đúng phải là:** Phase B là phase DÀI NHẤT. Một range mà Phase A = 32 nến còn Phase B = 1 nến thì theo định nghĩa nó chưa xây được nguyên nhân nào — không có gì để phá.
- **Dấu hiệu quyết định trên chart:** ST[A] 13:31 → LPSY[C] 13:33 → SOW 13:37. Từ lúc Phase A kết thúc tới lúc phá biên chỉ 6 nến. Vùng "đấu giá" thật chỉ có 24 nến (13:32→13:55), 32 nến đầu là Phase A và 29 nến cuối đã ở ngoài range.
- **Nghi phạm trong thuật toán:** LPSY[C] được chọn là ứng viên **đầu tiên** sau ST[A]. Phase C = [LPSY[C] … trước SOW] nên khi ứng viên C bắt sớm, Phase B bị bóp về 0. Phải chọn ứng viên C **cuối cùng** trước SOS/SOW (đúng tinh thần L8: "có Phase D rồi mới xác định được Phase C").

### 2. Không đủ điều kiện mở range — luật vi phạm: L1
- **Thuật toán gắn:** MOVE giảm 42.2 giá / 40 nến (hiệu suất 0.68) bị chặn bởi SC 13:00 → mở range.
- **Đúng phải là:** climax phải **chặn** move, tức là cực trị. Nến 13:00 có low 4425.2 nhưng 31 nến sau giá xuống 4423.3 rồi thủng hẳn — nến này không chặn được gì, nó chỉ là nến giảm mạnh cuối leg. Cả khối 13:00→13:55 là một cờ giảm: hồi 50% rồi đi tiếp đúng hướng cũ.
- **Dấu hiệu quyết định trên chart:** AR bị chính thuật toán ghi là **"AR (yếu)"** — nến 13:16 VSA 0.59x, thân/biên độ 0.04. Đó không phải một cú bật ngược (Automatic Rally) mà là đỉnh của một đợt trôi ngang 16 nến. Không có CHoCH thật → L2 chưa thoả về chất, dù thoả về hình.
- **Nghi phạm trong thuật toán:** điều kiện AR chỉ kiểm "mức cao nhất sau climax", không kiểm chất lượng nhịp bật (tốc độ hồi / thân nến / volume). Nên thêm gate: AR bị đánh dấu "yếu" thì **huỷ range**, đừng vẽ tiếp A→E.

### 3. Nhãn SC nằm ngoài range và ở SAI BIÊN — luật vi phạm: L3 / lỗi nhãn cụm climax (đã biết, chưa sửa)
- **Thuật toán gắn:** SC | 12:52 | **4446.6** | VSA 4.58x — trong khi range mở lúc 13:00 và mức climax là **4425.2**.
- **Đúng phải là:** nhãn SC phải nằm tại đáy climax (4425.2, 13:00). Ở đây marker SC bị đẩy về nến volume cao nhất của cụm (12:52) và mang mức giá **4446.6 = đúng biên trên**. Trên ảnh, chữ SC nằm lơ lửng phía trên-trái range, ngang tầm AR — người đọc chart sẽ hiểu ngược hoàn toàn.
- **Dấu hiệu quyết định trên chart:** giá SC (4446.6) trùng khít giá AR (4446.6) trong bảng sự kiện — hai sự kiện đối lập cùng một mức.
- **Nghi phạm trong thuật toán:** nhánh "nhãn climax = cây volume cao nhất trong cụm, KHÔNG cần trùng cực trị giá". Tối thiểu phải kẹp nhãn vào **trong** [bar_start, bar_end] của range và lấy mức giá = cực trị của range, không lấy giá của nến mang nhãn.

### 4. Range chồng lấn với bài #32 — luật vi phạm: L3 (biên cố định) / cảnh báo "range quá vụn"
- **Thuật toán gắn:** #31 chạy 13:00→14:24; #32 mở lúc **14:06**, tức nằm gọn trong Phase E của #31.
- **Đúng phải là:** một range mới không được mở khi range cũ chưa đóng. Hai bộ biên chồng nhau trên cùng đoạn giá làm cả hai vô nghĩa.
- **Nghi phạm trong thuật toán:** bộ dò climax chạy độc lập, không khoá cửa sổ khi có range đang "completed nhưng chưa hết Phase E".

## Đạt
- Tên range đúng theo L4: MOVE giảm → SC → phá **xuống** = Tái phân phối. Khớp với thực tế giá đi từ 4425 xuống 4386.
- ST[A] 4423.3 hồi 108% khoảng AR↔climax — ngưỡng 0.55 mới đã ăn, ST[A] không còn lửng giữa range như vòng trước.
- Biên phụ dưới 4423.3 do ST[A] vượt mức climax tạo ra — đúng L3, mỗi bên 1 biên phụ, tỷ lệ 1.09x hợp lý.
- SOW 13:37 đóng cửa 4414.8, bứt qua biên phụ 4423.3 gần 9 giá, VSA 2.92x — đúng yêu cầu "SOW mạnh phải qua biên phụ" của L3.
- Không spam nhãn: 5 nhãn cho 84 nến, không có nhãn trùng vai.
