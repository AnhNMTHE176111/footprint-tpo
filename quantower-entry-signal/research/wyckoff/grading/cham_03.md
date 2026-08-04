# Chấm bài #03 — Tái tích luỹ (RE-ACC) · 2026-01-20 15:05 → 2026-01-21 03:05 (82 nến M1)

**Điểm: 3/10** — Tên range đúng và hướng đọc đúng, nhưng toàn bộ Phase A dựng sai: climax VSA 0,65×, ST[A] nằm **ngoài** range phía trên, và Phase C/D/E bị nén thành 1-2 nến. Sửa được nếu vá Phase A, nhưng ở dạng hiện tại chưa dùng được.

## Lỗi (nặng → nhẹ)

### 1. Climax VSA 0,65×, biên độ 0,0 giá — trong khi cây thật nằm ngay bên cạnh — luật vi phạm: L1 + mục 3(1) tài liệu thuật toán
- **Thuật toán gắn:** BCLX tại 4854,8, nến 15:05, VSA **0,65×**, biên độ 0,0.
- **Đúng phải là:** đọc bảng 12 nến — nến **+1 (15:06)** có volume 10, **VSA 5,00×**; nến **−1 (14:30)** có VSA 2,35× và là nến duy nhất trong cụm có thân thật (thân/biên 1,00). Cây climax thật là một trong hai cây đó, không phải cây 1 lot ở giữa.
- **Dấu hiệu quyết định trên chart:** thanh volume vàng cao vọt nằm ngay tại mốc BCLX trên panel dưới — nhưng đó là thanh của nến +1, còn chấm BCLX được đặt trên nến trước nó.
- **Nghi phạm trong thuật toán:** lặp đúng lỗi #1 của bài #02 — cơ chế "cụm climax" (v5 lỗi A) dời mốc sang **cực trị giá** mà bỏ qua **VSA của nến mới**. Ở đây nó chọn nến có High cao nhất (4854,8) thay vì nến có volume lớn nhất trong cụm. Đề xuất: trong cửa sổ cụm, chọn nến theo **tích (VSA × biên độ)**, không theo mỗi cực trị giá.

### 2. ST[A] nằm ngoài range, cao hơn climax 20,1 giá = 91% chiều cao biên chính — luật vi phạm: L2 (ST[A] phải là test lại vùng climax)
- **Thuật toán gắn:** ST[A] tại **4874,9** trong khi biên chính là 4832,8-4854,8 (cao 22,0 giá).
- **Đúng phải là:** ST[A] là lần thứ 3 đổi hướng, giá **quay về phía climax rồi bị chặn lại**. 4874,9 không phải bị chặn tại vùng climax — nó **vượt qua climax 20,1 giá**, tức gần đúng một lần chiều cao range. Đây chính là ca giảng viên đã bắt ở vòng trước ("ST[A] ở 179% và 275% chiều cao range vẫn được nhận"), và v5 đã đặt trần "vượt quá climax hơn 1 lần chiều cao range → bỏ ứng viên". Ở đây tỉ lệ là **0,91 lần** — lọt sát ngưỡng.
- **Dấu hiệu quyết định trên chart:** chấm ST[A] nằm hẳn phía trên đường nét đứt "biên phụ trên 4874,9", còn nét liền "biên CHÍNH trên 4854,8" nằm thấp hơn nó rõ rệt. Nói cách khác chính ST[A] tự tạo ra biên phụ cho mình.
- **Nghi phạm trong thuật toán:** trần 1,0× chiều cao range quá lỏng. Nếu ST[A] vượt qua climax thì về bản chất giá đã **đi tiếp**, không phải test. Đề nghị hạ trần xuống ~0,3× chiều cao range, hoặc yêu cầu ST[A] phải đóng cửa **trong** biên chính.

### 3. Phase D dài 1 nến, Phase E dài 2 nến — luật vi phạm: L10 (D+E = CBR: phá → retest giữ ngoài biên → đi tiếp)
- **Thuật toán gắn:** D = 03:03 → 03:03 (1 nến), E = 03:04 → 03:05 (2 nến). Range đóng.
- **Đúng phải là:** CBR cần **nhịp hồi retest** rồi mới đi tiếp. Ở đây không có LPS[D] nào được ghi, D chỉ chứa đúng cây SOS. Đây là lỗi J của v4 ("Phase E luôn dài 1 nến") **chưa hết**, chỉ đổi từ 1 nến thành 2.
- **Dấu hiệu quyết định trên chart:** ba vạch tím "Phase C / Phase D (1n) / Phase E (2n)" chồng sát nhau ở mép phải, nhãn đè lên nhau. Trong khi đó giá thật sau SOS còn chạy tiếp tới ~4990 (thấy rõ bên phải ảnh) — cả đoạn đó nằm **ngoài** range.
- **Nghi phạm trong thuật toán:** SOS được chốt ở 03:03 rồi range đóng ngay ở 03:05, tức cửa sổ chờ 25 nến của Phase D bị cắt sớm. Nghi ngờ điều kiện "đi thêm 1,0× chiều cao range" (22,0 giá) đạt ngay trong 2 nến vì giá nhảy — chiều cao range quá nhỏ nên đích Phase E vô nghĩa. Nên đặt đích Phase E theo **max(1,0× chiều cao range, k × ATR)**.

### 4. LPS[C] tại 4905,0 — cao hơn biên trên 50,2 giá, nằm hoàn toàn ngoài range — luật vi phạm: L7, L8
- **Thuật toán gắn:** LPS[C] tại 4905,0, Phase C dài 20 nến.
- **Đúng phải là:** LPS[C] là **test cuối cùng trước SOS**, phải nằm quanh vùng biên đang được test. Một điểm cao hơn biên trên 50,2 giá (= 2,3 lần chiều cao range) không phải "điểm hỗ trợ cuối cùng" của range này — giá lúc đó đã bỏ range đi từ lâu.
- **Dấu hiệu quyết định trên chart:** chấm LPS[C] nằm cao hơn cả đường nét đứt biên phụ, ở giữa đoạn giá đang leo dốc đều đặn.
- **Nghi phạm trong thuật toán:** đây là nhánh "Phase C gán ngược" (mục 6 case KHÓ) — nhìn lại 60 nến trước SOS và lấy **đáy sâu nhất**. Trong một đoạn giá leo dốc thẳng, "đáy sâu nhất trong 60 nến" chỉ là điểm thấp nhất của một cái dốc, không phải một nhịp test. Cần thêm điều kiện: LPS[C] gán ngược phải nằm **trong hoặc sát biên** (vd trong vòng 0,5× chiều cao range tính từ biên bị phá), nếu không thì range đó **không có Phase C** — hoàn toàn hợp lệ theo THEORY §3.2 ("không phải cấu trúc nào cũng có Spring/Shakeout").

### 5. Phase A (40 nến) dài gấp đôi Phase B (20 nến) — luật vi phạm: L9 (B phải dài nhất)
- **Thuật toán gắn:** A=40, B=20, C=20, D=1, E=2.
- **Đúng phải là:** B là phase dài nhất. Ở đây A dài nhất, chiếm 49% cả range. Lỗi này là hệ quả trực tiếp của lỗi #2 — ST[A] bị đẩy ra xa nên Phase A bị kéo dài.
- **Dấu hiệu quyết định trên chart:** dải "Phase A (40n)" trải rộng gấp đôi mọi dải khác.
- **Nghi phạm trong thuật toán:** sửa lỗi #2 thì lỗi này tự hết. Ngoài ra nên có kiểm tra hậu nghiệm: nếu A ≥ B thì Phase A đang bị dựng sai.

## Đạt
- **Tên range đúng theo L4:** origin BCLX (move tăng bị chặn) + phá thật lên trên = Tái tích luỹ. Đây chính là loại range mà bản v2/v3 xoá oan; v5 giữ và gọi đúng tên.
- MOVE trước climax đo đúng: 147,9 giá / 143 nến / hiệu suất 0,38 — một đợt tăng thật, không phải đi ngang. Điều kiện CẦN của L1 về phía move ĐẠT.
- SOS neo đúng cây: VSA 1,94×, thân/biên độ 1,00 — nhãn nằm trên cây phá thật, không phải nến xác nhận thứ 3. Vá lỗi B của v4 **có tác dụng**.
- Phase C (20 nến) ngắn hơn Phase B — không vi phạm L8, và không còn hiện tượng "Phase C dài 121 nến" của v4.
- LPS[C] chỉ đánh dấu **một điểm** — đúng L7.
- Không có nhãn ST[B] — đúng L6.
