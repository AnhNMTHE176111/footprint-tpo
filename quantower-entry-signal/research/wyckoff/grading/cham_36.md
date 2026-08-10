# Chấm bài #36 — Tái phân phối (RE-DIST) · 2026-06-23 00:22 → 03:49 (207 nến M1)

**Điểm: 3/10** — sửa nhãn nặng: thiếu hẳn Phase C, Phase A dài hơn Phase B, và cú thủng biên đầu tiên bị bỏ trắng không tên.

## Lỗi (nặng → nhẹ)

### 1. Thiếu hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** dải phase chỉ có A(45) → B(30) → D(12) → E(121). Không có đoạn C nào.
- **Đúng phải là:** phải có Phase C. Đọc trên chart: sau ST[A] (01:06, 4202.2) giá thủng biên chính dưới xuống 4188 (~01:15-01:20), rồi hồi lên ~4198 quãng 01:23-01:26 — **đó chính là LPSY[C]**: cú hồi cuối cùng lên đúng vùng biên chính dưới cũ (4196) nhìn từ bên ngoài, ngay trước khi mSOW/SOW nổ ra 01:33-01:37. Phase C phải bắt đầu tại nhịp hồi đó.
- **Dấu hiệu quyết định trên chart:** khoảng cách từ nhịp hồi 4198 tới SOW (01:37) chỉ ~11-14 nến — đúng đặc trưng "Phase C là phase ngắn nhất". Biên chính dưới 4196; đỉnh nhịp hồi ~4198 nằm **sát trên** mức đó, tức là test-lại-từ-dưới cổ điển.
- **Nghi phạm trong thuật toán:** guard v6 mục 1.5 — Phase C gán ngược bắt pivot phải nằm **đúng nửa range** (LPSY[C] phải ở nửa TRÊN, tức > 4206). Đỉnh 4198 nằm ở nửa dưới nên bị loại. Nới cửa sổ 0.5x → 0.8x len(B) (sửa #3 của v7) **không cứu được ca này** vì bị chặn bởi điều kiện nửa-range, không phải bởi cửa sổ. Điều kiện "nửa range" cần đổi thành "nằm trong dải biên chính ± dung sai" theo hướng phá.

### 2. Phase A (45 nến) dài hơn Phase B (30 nến) — luật vi phạm: L9
- **Thuật toán gắn:** A = 00:22→01:06 (45 nến), B = 01:07→01:36 (30 nến).
- **Đúng phải là:** B phải là phase dài nhất. Ở đây "giai đoạn xây nguyên nhân" chỉ có 30 nến, còn Phase A ngốn 45 nến chỉ để chờ AR.
- **Dấu hiệu quyết định trên chart:** AR chốt tận 01:00, cách climax 38 nến; trong 38 nến đó giá đi một mạch từ 4196 lên 4216 gần như không nghỉ — đó là **một chân đẩy**, không phải một quá trình Phase A.
- **Nghi phạm trong thuật toán:** AR = swing pivot đầu tiên xác nhận sau 5 nến. Trên một nhịp bật liên tục 38 nến, pivot đầu tiên chỉ xuất hiện ở đỉnh cùng → Phase A tự động phình.

### 3. AR xoá 100% MOVE, range mở trên nền quá mỏng — luật vi phạm: L1 / L2
- **Thuật toán gắn:** MOVE dài 17.6 giá (chân ~4213.6 → climax 4196.0), hiệu suất 0.43. AR = 4216.0.
- **Đúng phải là:** AR là "phản ứng tự động" — một cú bật **một phần** của move bị chặn. Ở đây AR 4216 **cao hơn cả chân MOVE 4213.6**, tức nhịp bật đã xoá sạch move giảm và còn đi xa hơn. Không có cân bằng nào bị thiết lập; đây là nhịp hồi rồi tiếp diễn giảm.
- **Dấu hiệu quyết định trên chart:** nhãn "chân MOVE (17.6 gia)" nằm **thấp hơn** đường biên chính trên 4216.0 trên chính ảnh này.
- **Nghi phạm trong thuật toán:** không có guard nào chặn AR vượt qua chân MOVE. Nên thêm: AR > 1.0× độ dài move → move đã bị phủ định, huỷ ứng viên hoặc mở lại range từ đỉnh mới.

### 4. Cú thủng biên đầu tiên (xuống 4188) không được gán nhãn — luật vi phạm: L5 / L3
- **Thuật toán gắn:** không nhãn. Biên phụ dưới 4188.0 tự xuất hiện, không sự kiện nào sinh ra nó trên bảng.
- **Đúng phải là:** cú thủng biên chính 4196 xuống 4188 (8 giá = 40% chiều cao range) rồi rút lại vào trong range là một cú rũ — Spring nếu quay lại ≤4 nến, Shakeout nếu lùng bùng lâu hơn. Phải có tên.
- **Dấu hiệu quyết định trên chart:** đường nét đứt "bien phu duoi 4188.0" tồn tại nhưng không có chấm sự kiện nào ở mức đó — bằng chứng biên phụ được nới bởi một cú không ai gọi tên.
- **Nghi phạm trong thuật toán:** vẫn là "biên phụ tự nới rồi tự vượt" (mục sửa #6). Cú thăm dò phải **vượt biên phụ** mới được gọi Spring/Shakeout, nhưng biên phụ lúc đó do chính nó tạo ra → không bao giờ vượt nổi chính mình. Nâng ngưỡng 10→30 tick không giải quyết gốc: cần đóng băng biên phụ trong suốt cửa sổ theo dõi cú thăm dò.

### 5. mSOW dư — cùng một nhịp rơi bị tách hai nhãn — luật vi phạm: mục 9 (nhãn dư)
- **Thuật toán gắn:** mSOW 01:33 @ 4185.5 (VSA 2.04x) và SOW 01:37 @ 4178.7 (VSA 5.63x) — cách nhau 4 nến, cùng một cú sụp liên tục.
- **Đúng phải là:** một cú phá, một nhãn. mSOW theo định nghĩa v6 là cú đã phá được nhưng **thu hẳn vào trong range** rồi hướng sang biên đối diện — điều đó không hề xảy ra ở đây, giá rơi thẳng một mạch từ 4188 xuống 4144.
- **Nghi phạm trong thuật toán:** nhánh hạ cấp mSOS/mSOW bắn trước khi cửa sổ xác nhận SOS/SOW kịp chốt, rồi cả hai nhãn cùng được giữ lại.

## Đạt
- **Chú thích nỗ lực/kết quả đọc đúng dấu** (er=0.25 → ghi "HIỆU QUẢ, không phải hấp thụ") — lỗi hard-code "vùng hấp thụ NGHI VẤN" của v6 đã hết.
- **Biên chính đúng = climax 4196.0 + AR 4216.0**, cố định suốt range, không bị kéo theo giá (L3).
- **Biên phụ đúng 1 cái mỗi bên** (chỉ có dưới, 4188.0) — không spam (L3).
- **Tên range đúng:** SC (move giảm bị chặn) + phá xuống thật = Tái phân phối (L4).
- **Nhãn SOW đặt đúng cây phá thật** — VSA 5.63x, thân 0.82, cây cao nhất cả đoạn (mục 8).
- **Phase E có độ dài thật** 121 nến, giá rời range đi tìm vùng giá mới 4144 (L10).
