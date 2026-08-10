# Chấm bài #03 — Phân phối (DIST) · 2026-01-21 06:34 → 2026-01-22 05:50 (127 nến M1)

**Điểm: 5/10** — Câu chuyện cấu trúc đọc đúng (đỉnh → xả → phá xuống), nhưng cả hai đầu của Phase A đều neo sai cây.

## Lỗi (nặng → nhẹ)

### 1. Biên chính TRÊN neo vào một nến 2 lot, biên độ 0.0 giá — luật vi phạm: L3 (biên chính = mức climax) + L1
- **Thuật toán gắn:** climax mở range = nến 06:34, **VSA 0.85x, biên độ 0.0 giá, 2 hợp đồng**, giá 4989.4 → thành "biên CHINH tren 4989.4".
- **Đúng phải là:** biên trên phải là mức của cây cao trào thật. Trong cửa sổ, cây có ý nghĩa là **06:57 (111 lot, VSA 13.62x, biên độ 7.4 giá, thân 0.72)** — cây bán tháo đầu tiên; đỉnh đấu giá thật quanh 4985–4989 nhưng phải neo bằng cây có volume, không phải một tick đơn lẻ.
- **Dấu hiệu quyết định trên chart:** nến mở range không thoả chính điều kiện mở range của thuật toán (cần VSA ≥ 2.2x và biên độ ≥ 1.4× TB). Nó lọt vào vì cơ chế cụm **dời mức giá** sang cực trị mới bất kể cây đó có phải climax hay không.
- **Nghi phạm trong thuật toán:** cửa sổ cụm 8 nến dời `climax_price`/`r.start_i` theo cực trị giá thuần tuý, không kiểm lại tính chất climax của cây được dời tới.

### 2. Nhãn BCLX rơi trước nến mở range và thấp hơn biên của chính nó 30 giá — luật vi phạm: L3
- **Thuật toán gắn:** BCLX tại 04:19, giá **4958.9**, VSA 3.12x.
- **Đúng phải là:** nhãn climax phải nằm tại/sát 4989.4. 4958.9 là một mức giữa đoạn dốc lên, đọc trên chart thì cái chấm BCLX treo lửng bên ngoài khung range, phía dưới đỉnh.
- **Nghi phạm trong thuật toán:** lỗi cụm climax đã biết (13.1c, thử sửa rồi revert) — nhãn kẹp một phía nên vẫn trôi **về trước** nến mở range.

### 3. SOW không bứt qua biên PHỤ, chỉ qua biên chính — luật vi phạm: L3 ("SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua biên phụ")
- **Thuật toán gắn:** SOW tại 21:00, giá **4928.5** (VSA 5.00x); biên phụ dưới đã có sẵn tại **4916.4** do mSOW 17:31 tạo ra.
- **Đúng phải là:** cú phá muốn được gọi SOW thật phải đóng cửa vượt **dưới 4916.4**. 4928.5 còn nằm **trên** cực trị mà chính phe bán đã đạt trước đó trong Phase B → tại thời điểm đó vẫn là mSOW thứ hai.
- **Dấu hiệu quyết định trên chart:** chấm SOW nằm rõ **phía trên** đường nét đứt "bien phu duoi 4916.4".
- **Nghi phạm trong thuật toán:** bản vá 13.1c đổi mốc quyết định decisive từ `out_edge` sang `edge` (biên chính). Sửa đúng chiều "không bị vô hiệu oan", nhưng lại **mở cửa cho cú phá yếu hơn cú thăm dò cũ** được thăng cấp. Cần tách: `edge` để quyết định *có phá không*, `out_edge` để quyết định *có gọi là SOS/SOW mạnh không*.

### 4. LPSY[C] nằm ở 21% chiều cao range — luật vi phạm: THEORY §4.1 (LPSY = đợt **phục hồi** yếu)
- **Thuật toán gắn:** LPSY[C] tại 4951.6, chỉ cao hơn biên chính dưới (4941.5) 10 giá.
- **Đúng phải là:** một LPSY là nhịp bật lên rồi thất bại; ở đây nó chấp nhận được về vai trò (nhịp hồi cuối trước cú rơi) nhưng biên độ hồi quá mỏng để gọi tên. Đây là hệ quả của việc **bỏ hẳn** ràng buộc nửa-range ở 13.1c — bỏ đúng nút thắt nhưng bỏ hết thì pivot trôi xuống sát đáy.
- **Đề nghị:** thay ràng buộc "đúng nửa range" bằng "pivot phải cách biên sắp bị phá ≥ 40% chiều cao".

### 5. AR và ST[A] đều có VSA ~0.12x mà không bị gắn cờ "(yếu)"
- AR 4941.5 VSA **0.12x**, ST[A] 4985.9 VSA **0.13x** — cả hai biên chính của range dựng trên nến 1 hợp đồng. Biến `ar_vsa`/`sta_vsa` đã đo sẵn nhưng chưa dùng để cảnh báo (lỗi đã ghi ở 13.1b, chưa sửa).

## Đạt
- Điều kiện mở range: MOVE 188.8 giá / 175 nến / hiệu suất 0.38, climax chặn đúng đỉnh — đúng L1.
- ST[A] tại 4985.9 = hồi **93%** khoảng AR↔climax, test đúng vùng climax rồi Phase A đóng ngay tại đó — đúng L2. Ngưỡng 0.55 mới ăn đúng ở ca này.
- Tỉ lệ phase: A 18 · B **49** · C 21 · D 25 · E 15 — B dài nhất (L9), C không phình quá D (L8) — đạt.
- Tên **Phân phối**: origin BCLX + phá thật xuống = đúng L4.
- Phase D/E đúng CBR: LPSY[D] 4911.9 nằm **dưới** biên chính 4941.5, giữ được ngoài biên rồi giá đi tiếp xuống 4860 — đúng L10.
- mSOW ở Phase B được giữ đúng vai (không bị nâng thành Shakeout) và nới biên phụ một lần — đúng L3/L5.
- LPSY[C] và LPSY[D] tách vai rõ, mỗi cái một điểm — đúng L7, tránh được lỗi kinh điển Ca #3 nguồn 4.pdf.
