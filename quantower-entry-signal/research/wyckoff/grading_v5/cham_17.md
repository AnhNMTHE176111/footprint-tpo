# Chấm bài #17 — Chưa rõ (BCLX) (DIST?) · 2026-05-20 15:16 → 2026-05-22 20:59 (2485 nến M1)

**Điểm: 1/10** — Không nên vẽ range ở đây. Đây không phải một vùng đấu giá, đây là **2,5 ngày lịch sử giá** bị nhét vào một cái khung cao 25.6 giá. Range chết vì hết hạn 2500 nến chứ không vì cấu trúc nào kết thúc.

## Lỗi (nặng → nhẹ)

### 1. Range chạy 2485 nến rồi bị guard timeout giết, vẫn được vẽ như bài làm hoàn chỉnh — luật vi phạm: mục 8 THEORY (TR = vùng cân bằng), mục 8 tài liệu thuật toán
- **Thuật toán gắn:** range 2485 nến, tiêu đề ghi `[completed]`, Phase A 25 nến + Phase B 2461 nến, hết. Không có C, D, E.
- **Đúng phải là:** 2485 nến sát ngưỡng huỷ 2500 — nghĩa là range này bị **cắt vì hết giờ**, không phải vì hoàn tất. Một cấu trúc không bao giờ ra Phase C/D/E trong 2,5 ngày thì giả thuyết "có vùng đấu giá ở đây" đã sai từ đầu, phải **bỏ range**, không vẽ. Vẽ ra rồi gắn `[completed]` là báo cáo sai trạng thái.
- **Dấu hiệu quyết định trên chart:** dải phase chỉ có A và B; hai vạch tím dồn hết vào 25 phút đầu bên trái, còn lại 2,5 ngày trắng trơn không mốc nào.
- **Nghi phạm trong thuật toán:** guard 2500 nến (mục 8) khi bắn ra vẫn đẩy range sang danh sách "được vẽ" và gắn cờ completed, thay vì xếp vào "bị bỏ" kèm lý do. Cần: range chết vì timeout mà chưa từng có Phase C → **loại khỏi output**, hoặc ít nhất đổi nhãn thành "(bỏ: quá dài)".

### 2. Biên chính 25.6 giá nhưng giá thực tế lượn trong 83.6 giá — biên chính vô nghĩa — luật vi phạm: L3
- **Thuật toán gắn:** biên chính 4565.6–4591.2 (25.6 giá); biên phụ 4521.8–4605.4 (83.6 giá).
- **Đúng phải là:** biên phụ rộng **gấp 3.27 lần** biên chính. Theo L3 biên phụ là "mức cực trị xa nhất mà một thế lực đã cố phá range gốc tạo ra" — nó được phép nới ra một chút. Nới gấp 3,3 lần thì không còn là "cố phá range" nữa, mà là bằng chứng range gốc đã bị xoá sổ từ lâu. Nhìn chart: giá đi từ 4605 xuống 4521 rồi lại về 4592, cắt qua cặp biên chính hàng chục lần.
- **Dấu hiệu quyết định trên chart:** hai đường cam nét liền nằm vắt ngang giữa biểu đồ, giá cắt qua chúng liên tục cả hai chiều suốt 2,5 ngày — không cạnh nào có vai trò hỗ trợ/kháng cự.
- **Nghi phạm trong thuật toán:** không có guard nào cho **tỉ lệ biên phụ / biên chính**. Guard duy nhất là "biên chính > 3.5% giá" (mục 8) — mà biên chính ở đây chỉ 0.56% nên không bao giờ bắn. Đề xuất: biên phụ vượt ~2× biên chính → range mất hiệu lực.

### 3. Climax gán vào nến 4.45x trong khi nến ngay trước có VSA 7.69x và mới là cây chặn move — luật vi phạm: L1, lỗi hệ thống A (chưa hết)
- **Thuật toán gắn:** BCLX tại 15:16, VSA 4.45x, high 4591.2.
- **Đúng phải là:** đọc phiếu, nến **-1 (15:15)** có volume 133, **VSA 7.69x**, biên độ 22.2 giá (4562.3→4584.5), thân 0.84 — đó mới là cây cao trào mua thật, gấp 1,7 lần cây được chọn cả về VSA. Nến 15:16 chỉ là cây nối đuôi (volume 91) đẩy thêm 6.7 giá rồi tắt. Đúng ra cụm climax phải neo ở 15:15.
- **Dấu hiệu quyết định trên chart:** volume 133 vs 91; biên độ 22.2 giá vs 10.1 giá. Cây bị bỏ qua lớn hơn cây được chọn ở cả hai thước đo.
- **Nghi phạm trong thuật toán:** mục 4.0 dời mốc climax trong 8 nến đầu **chỉ khi có cực trị mới cùng phía** — 15:16 có high cao hơn 15:15 nên máy chốt ở 15:16 và không bao giờ nhìn lại. Nhưng luật chọn "cực trị" bỏ qua hoàn toàn khối lượng và biên độ. Với BCLX nên chọn cây có VSA×biên độ lớn nhất trong cụm, rồi mới lấy mức giá cực trị của cả cụm làm biên.

### 4. AR (yếu) chỉ cách climax 14 nến và nến AR có VSA 0.62x — Phase A không đáng tin — luật vi phạm: L2
- **Thuật toán gắn:** AR (yếu) 15:30 tại 4565.6, VSA 0.62x, thân 0.41. ST[A] 15:40 tại 4576.4.
- **Đúng phải là:** máy tự gắn cờ "(yếu)" là đúng, nhưng rồi vẫn dùng cái AR yếu đó làm **biên chính dưới cố định vĩnh viễn cho 2485 nến**. Một mức do nến 0.62x tạo ra không đủ tư cách làm biên chính. Khi AR bị đánh dấu yếu thì nên bỏ ứng viên, không phải chỉ ghi chú rồi đi tiếp.
- **Dấu hiệu quyết định trên chart:** cả Phase A gói gọn 25 nến (15:16→15:40) — 25 phút để dựng một cấu trúc rồi giữ nó 2,5 ngày.
- **Nghi phạm trong thuật toán:** mục 4.1 ghi rõ nhãn "AR (yếu)" **"chỉ là cảnh báo hiển thị, không đổi logic"**. Đây chính là chỗ nên đổi logic.

### 5. Phase C được vẽ rồi biến mất, để lại nhãn LPSY[C] mồ côi trong Phase B — luật vi phạm: L8, lỗi hệ thống C (biến thể mới)
- **Thuật toán gắn:** bảng sự kiện ghi `LPSY[C] · 2026-05-21 13:05 · Phase C`, nhưng bảng phase **không có dòng Phase C nào** — chỉ có A và B. Sau đó mSOW 05-22 14:14 lại được ghi là Phase B.
- **Đúng phải là:** hai bảng phải nhất quán. Ở đây shock/LPSY[C] hết hạn nên đoạn C bị xoá khỏi timeline (đúng theo v5), **nhưng nhãn sự kiện thì không được cập nhật** — nó vẫn khai mình thuộc Phase C. Nhãn LPSY[C] phải bị xoá hoặc hạ cấp cùng lúc với đoạn phase.
- **Dấu hiệu quyết định trên chart:** nhãn LPSY[C] hiện giữa chart tại 4547.1 trong khi dải phase phía trên chỉ có "Phase B (2461n)".
- **Nghi phạm trong thuật toán:** vá lỗi C ở v5 xoá **đoạn phase** nhưng quên xoá **sự kiện** đã gán phase đó. Chỗ xoá đoạn C cần quét lại danh sách event có `phase == C` và hạ chúng về B (hoặc bỏ).

### 6. Ngoài ra: LPSY[C] neo vào nến VSA 0.36x thân 0.10 — mục 8, nhãn không có nội dung khối lượng nào.

## Đạt
- **Mục 1 (một nửa):** có MOVE thật trước climax — 81.5 giá / 63 nến / hiệu suất 0.44, move tăng rõ. Điều kiện CẦN của L1 thoả. Cái sai là chọn nhầm cây climax và giữ range quá lâu.
- **Mục 4 — không đặt tên bừa:** giá chưa phá thật nên range để "Chưa rõ (BCLX)", tô xám, không gán DIST. Đúng L4 và đúng tinh thần lỗi F đã vá.
- **Mục 9 — không spam:** mỗi bên một biên phụ, không có nhãn ST[B]. Đúng L3, L6.

## Cần hỏi người học
- Range chết vì guard timeout (2500 nến) mà chưa từng có Phase C: nên **bỏ hẳn không vẽ**, hay vẫn vẽ nhưng gắn nhãn "bỏ dở"? Em nghiêng về bỏ hẳn, vì vẽ ra thì nó chiếm chỗ range thật (thuật toán chỉ theo dõi một range một lúc — mục 13.3 — nên 2485 nến này đã **chặn** mọi climax mới suốt 2,5 ngày).
