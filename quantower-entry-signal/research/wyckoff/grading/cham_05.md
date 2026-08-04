# Chấm bài #05 — Tái phân phối (RE-DIST) · 2026-03-18 13:16 → 2026-03-19 03:31 (143 nến M1)

**Điểm: 3/10** — hướng và tên range đọc đúng, chuỗi mSOS → LPSY[C] → SOW đúng bài, nhưng phải sửa 4 nhãn: cây climax, vị trí nhãn SC, độ dài Phase C, và LPSY[D] đang nằm **trong** range nên theo đúng luật thì cú phá đã bị vô hiệu.

## Lỗi (nặng → nhẹ)

### 1. LPSY[D] nằm 21.9 giá TRONG range — cú phá không giữ được ngoài biên — luật vi phạm: L10, mục 7 Câu 1 của chính thuật toán
- **Thuật toán gắn:** biên chính dưới **4918.1**; `LPSY[D]` tại **4940.0** (2026-03-19 01:40); range vẫn được đặt tên **Tái phân phối**, Phase D 25 nến, Phase E 1 nến.
- **Đúng phải là:** L10 nói rõ Phase D+E = CBR = "phá biên, hồi về retest nhưng **giữ được** ở ngoài biên". Ở đây nhịp hồi đưa giá **21.9 giá vào trong** range (42% chiều cao), tức cú phá bị vô hiệu theo đúng Câu 1 mục 7 ("một nến đóng cửa lùi hẳn vào trong range quá 30 tick trước khi đi được ≥50% tiến độ tối thiểu"). Tiến độ tối thiểu = 0.5 × 51.9 = 26 giá tính từ 4918.1, tức phải xuống 4892; đáy thực tế của cú phá chỉ ~4895–4899 (chấm SOW ở 4898.9). Vậy giá **chưa** đi đủ 50% mà đã lùi hẳn vào trong → phải hạ SOW thành mSOW, trả dải phase về B, **không đặt tên range**.
- **Dấu hiệu quyết định trên chart:** chấm tím `LPSY[D]` vẽ **phía trên** đường nét liền "biên CHINH dưới 4918.1" một khoảng rõ; sau đó mới có nến rơi tiếp.
- **Nghi phạm trong thuật toán:** LPS[D]/LPSY[D] giờ đo bằng swing pivot (vá lỗi J) nhưng **không kẹp điều kiện "pivot phải nằm ngoài biên đã phá"**. Hai nhánh (vá lỗi J và vá lỗi F) chạy độc lập nên pivot trong range vẫn được nhận là retest hợp lệ và không kích hoạt vô hiệu hoá. Cần bắt LPS[D]/LPSY[D] phải nằm ngoài biên, hoặc chạy kiểm vô hiệu trước khi gán nhãn.

### 2. Cây mở range VSA 1.05× / 3 hợp đồng, biên độ 2.4 giá — không đạt ngưỡng climax
- **Thuật toán gắn:** "Climax mở range: SC tại 4918.1, **VSA = 1.05×**, biên độ 2.4 giá" (volume 3).
- **Đúng phải là:** ngưỡng của chính thuật toán là VSA ≥ 2.2×. Cây có nỗ lực thật là nến **+4 (13:30): 11 hợp đồng, VSA 3.61×, biên độ 1.9 giá** — nhưng nó là cây **sau** đáy 14 phút, và đáy của nó (4930.4) cao hơn đáy range 12.3 giá. Đọc đúng bài: đợt giảm này kết thúc kiểu **cạn kiệt** (THEORY §6.2 — nến biên độ bình thường, volume trung bình, người bán hết quan tâm), không có SC nổ volume. Vẫn mở được range nhưng phải ghi nhãn khác (dạng `SC?` như cơ chế mới đã có cho range sinh từ cú phá) chứ không dán SC trên cây 1.05×.
- **Dấu hiệu quyết định trên chart:** panel khối lượng ở vùng Phase A không có thanh vàng nào tại chỗ chấm SC; thanh vàng cao nhất của cả ảnh nằm ở 03-18 12:01, tức **trước** khi range mở.

### 3. Nhãn SC nằm 12.3 giá trên mức SC, không ở đáy — luật vi phạm: THEORY §3.3, L3
- **Thuật toán gắn:** nhãn `SC` tại **4930.4**, mức climax dùng làm biên chính dưới là **4918.1**.
- **Đúng phải là:** SC đánh dấu đáy của đợt giảm bị chặn. Trên chart chấm SC vẽ **phía trên** đường biên chính dưới, giữa lưng chừng — nhìn ra thì "cao trào bán" không nằm ở đáy. Cùng một lỗi hệ thống với #01/#03/#04/#06.

### 4. Phase C dài 34 nến, dài hơn cả Phase A (27) — luật vi phạm: L8 ("Phase C là phase NGẮN NHẤT")
- **Thuật toán gắn:** A 27 · B 57 · **C 34** · D 25 · E 1. Phase C bắt đầu ở LPSY[C] 17:42 và chạy tới 20:12, SOW ở 20:16.
- **Đúng phải là:** LPSY[C] neo quá sớm. Trên chart, từ 17:42 tới 20:12 giá còn đi xuống rồi hồi lên rồi mới sụp — nhịp hồi **cuối cùng** (quanh 19:51, chạm lại ~4950 rồi bị chặn) mới là LPSY[C] thật, và Phase C khi đó chỉ còn ~10 nến. Đây đúng bài học Ca #1 và Ca #8 nguồn 4.pdf/2.pdf: giảng viên thu hẹp Phase C về quanh **cú test cuối cùng ngay trước khi cấu trúc sụp**, không kéo từ cú test đầu tiên.
- **Nghi phạm trong thuật toán:** LPSY[C] được gán **ngay sau mSOS** (17:35 → 17:42) rồi giữ nguyên, không cập nhật khi có nhịp test muộn hơn. Nên lấy nhịp test **cuối cùng** trước SOS/SOW, giống cách nhánh "gán ngược" đã làm.

### 5. Phase E 1 nến, bỏ trọn kết quả — luật vi phạm: L10
- Phase E = **1 nến** (03-19 03:31), rồi range đóng. Nhưng chart cho thấy đợt giảm thật chỉ bắt đầu sau đó: từ ~4930 xuống **4820** (≈110 giá = 2.1× chiều cao range). Toàn bộ "kết quả" của nguyên nhân đã xây trong range nằm **ngoài** dải phase. Cùng lỗi với #02 và #04 → nhánh kết thúc Phase E là lỗi lặp của vòng này.

## Đạt
- **Tên range (L4):** origin **SC** (move giảm bị chặn) + phá **xuống** thật = **Tái phân phối**. Đúng, và đây chính là nhóm mà bản v3 từng xoá oan. Chart xác nhận (giá đi tiếp xuống 4820).
- **Chuỗi mSOS → LPSY[C] khớp bài chữa thật:** mSOS 4978.0 (cú phá biên trên **thất bại**, thu về trong range) rồi LPSY[C] ngay sau đó — đúng chính xác Ca #10 nguồn 2.pdf ("sau khi Failed SOS chuyển thành UT[B] thì LPS[C] tiềm năng"), chỉ đổi chiều. Và mSOS được **giữ ở Phase B**, không bị nâng thành cú rũ — đúng L5/L8.
- **Biên (L3):** biên chính = climax + AR, cố định; đúng một biên phụ trên 4978.0 = cực trị xa nhất, tỷ lệ 1.15×; phía dưới không có biên phụ nên SOW chỉ cần bứt biên chính — hợp lệ.
- **Phase A (L2):** đủ 3 lần đổi hướng; ST[A] tại 4937.0 = 36% chiều cao tính từ climax, thân 1.00 — chấp nhận được là test lại vùng SC (không hoàn hảo như bài #02 nhưng không rơi giữa range như #01/#06).
- **Phase B (L9):** 57 nến, dài nhất.
- **Khối lượng:** SOW có VSA 4.00×, thân 0.65 — nỗ lực khớp kết quả.
- **Chỉ số Phase B — đo đúng bản chất:** `SOT phía TRÊN = SOT (n=3), thrust cuối/đầu 0.21, volume nhịp cuối/đầu 0.60 → cạn kiệt`. Đọc trần trụi: ba nhịp đẩy lên liên tiếp ngắn dần còn 21% kèm volume rơi còn 60% = cầu rút lui ở biên trên (THEORY §7, biến thể "rút ngắn + volume yếu"). Range sau đó phá xuống — chỉ số này báo đúng hướng và đúng phía. Đây là chỉ số hữu ích nhất của bài.

## Cần hỏi người học
- Không có. Bốn lỗi trên đều quy được về luật đã chốt.
