# Chấm bài #10 — Phân phối (DIST) · 2026-04-23 12:06 → 17:32 (233 nến M1)

**Điểm: 5/10** — khung range và tỷ lệ phase đúng hình, tên DIST đúng, SOW bứt biên phụ đúng. Nhưng **UTAD gọi sai chỗ** (đúng lỗi kinh điển Ca #1/#4 nguồn 4.pdf) và biên chính hẹp hơn vùng đấu giá thật 2,3 lần, kéo Phase E xuống còn 2 nến.

## Lỗi (nặng → nhẹ)

### 1. UTAD gán vào cú vượt đỉnh ở ĐẦU Phase B, cách cấu trúc sụp 4,5 giờ — luật vi phạm: L8, CHART_CASES Ca #1 và Ca #4 nguồn 4.pdf
- **Thuật toán gắn:** UTAD tại **12:43 / 4795.6**, Phase="C", trạng thái **confirmed** — nhưng dải Phase C trên timeline lại là **16:51 → 17:15**. Nhãn UTAD nằm mồ côi ngoài chính phase nó thuộc về.
- **Đúng phải là:** cú 12:43 là **UT[B]** — test biên trên trong Phase B. UTAD chỉ được công nhận ở cú test **cuối cùng** phá đỉnh range **ngay trước khi** cấu trúc sụp. Sau 12:43 giá còn dao động **178 nến** trong range và còn lên lại 4792.4 lúc 15:19 — đúng tiêu chí phân biệt của Ca #4: "nếu sau đỉnh vẫn còn dao động đi ngang/hồi lại trong range → đó là ST[B]/UT[B], chưa phải UTAD".
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm UTAD (vàng) nằm ở cột thời gian 12:43, ngay cạnh vạch tím "Phase B (178n)" — cách dải "Phase C (16n)" gần hết chiều ngang chart. Range này thực chất **không có UTAD**: cú hồi cuối 16:51 lên 4789.8 **không phá được** đỉnh 4790.9, nên nhãn đúng cho nó là LPSY[C] (thuật toán đã gắn đúng), và nhãn UTAD phải bị **xoá**.
- **Nghi phạm trong thuật toán:** cú rũ được chốt ngay tại thời điểm phá + rút vào (mục 5.1) rồi mở Phase C tại đó; khi Phase C hết hạn 120 nến thì đoạn C bị xoá (vá lỗi C của v5) **nhưng nhãn cú rũ không bị hạ cấp** — spec nói phải đổi thành UT/UA/mSOS/mSOW. Ở đây trạng thái còn ghi "confirmed". Nhánh hạ cấp nhãn không chạy, hoặc chạy nhưng bị nhánh Phase C gán ngược (16:51) ghi đè mà không dọn nhãn cũ.

### 2. Biên chính 11.7 giá nằm GIỮA vùng dao động rộng 26.7 giá — luật vi phạm: L3 (biên chính = 2 biên quan trọng nhất)
- **Thuật toán gắn:** biên chính 4779.2-4790.9 (11.7 giá = 0.24% giá); biên phụ 4768.9-4795.6 (26.7 giá) → tỷ lệ **2.28x**.
- **Đúng phải là:** vùng đấu giá thật là ~4769-4796. AR 12:16 tại 4779.2 chỉ hồi 11.7 giá trong 10 nến với **VSA 0.19x, thân 0.00** — đó là một nến rác, không phải "phản ứng tự động" sau BCLX. Chọn nó làm biên dưới khiến giá xuyên qua biên chính liên tục cả hai phía suốt 178 nến, và mọi sự kiện sau đó (UT/mSOS/mSOW) đều được đo bằng một biên vô nghĩa.
- **Dấu hiệu quyết định trên chart:** hai đường cam nét liền nằm gọn **bên trong** đám nến Phase B — giá đi lên trên và xuống dưới chúng vài chục lần. Đối chiếu chính lỗi A mà v5 đã vá cho climax ("biên chính nằm giữa vùng giá"): lỗi đó nay tái xuất ở phía **AR**.
- **Nghi phạm trong thuật toán:** AR = swing pivot ngược đầu tiên xác nhận (5 nến + sàn 1.5× biên độ TB). Sàn 1.5× ATR quá thấp so với chiều cao vùng thật. Cần thêm: AR phải giữ được (không bị giá vượt qua trong Phase B quá X% chiều cao), nếu bị vượt hẳn thì **dời AR** như đã làm cho climax ở mục 4.2.

### 3. mSOS 15:19 không đủ tư cách — luật vi phạm: mục 5.1 (cú "mạnh" = sâu ≥ max(15 tick, 15% chiều cao) hoặc VSA ≥ 2.2x)
- **Thuật toán gắn:** mSOS tại 4792.4, **VSA 0.91x**.
- **Đúng phải là:** **UT[B]** (test nhẹ biên trên). Cú này vượt biên chính đúng **1.5 giá**, không vượt biên phụ trên 4795.6, và VSA 0.91x — trượt cả hai điều kiện "mạnh" (15% × 11.7 = 1.76 giá > 1.5 giá; 0.91 < 2.2). Theo chính spec nó phải là test nhẹ.
- **Dấu hiệu quyết định trên chart:** chấm mSOS nằm sát ngay trên đường "biên CHÍNH trên 4790.9" và thấp hơn hẳn đường nét đứt 4795.6; cột volume ở nhịp đó không phải cột vàng.
- **Nghi phạm trong thuật toán:** ngưỡng "mạnh" tính bằng max(15 tick, 15% chiều cao) — với range hẹp 11.7 giá thì 15% chỉ = 1.76 giá, cực dễ chạm; hoặc phép so đang dùng **high** thay vì **close** (Ca #5 nguồn 4.pdf: ranh giới phải neo giá đóng cửa). Nến 15:19 thân 1.00 nên nghi phép so dùng high/close của một nến quá nhỏ.

### 4. Phase E chỉ 2 nến — luật vi phạm: L10 (Phase E = giá rời range đi tìm vùng giá mới), mục 7 lỗi J
- **Thuật toán gắn:** D=15 nến, **E=2 nến**.
- **Đúng phải là:** sau SOW 17:16 (4765.0) giá lao xuống tới **4720** — thêm **45 giá**, gần 4 lần chiều cao biên chính. Phase E đáng lẽ dài vài chục nến.
- **Dấu hiệu quyết định trên chart:** vạch "Phase E (2n)" nằm ở đúng chỗ giá bắt đầu đổ; toàn bộ đoạn sụp mạnh nhất (cột volume vàng cao nhất chart, quanh 17:41) nằm **ngoài** dải phase.
- **Nghi phạm trong thuật toán:** đích đóng Phase E = đi xa **2.0× chiều cao range** = 23.4 giá. Vì biên chính bị chốt hẹp (lỗi #2), mốc này đạt trong 2 nến. Đích Phase E nên đo theo **biên phụ** hoặc theo ATR, không theo chiều cao biên chính đang bị co.

### 5. Thiếu LPSY[D] — luật vi phạm: L10 (retest giữ được ngoài biên)
- **Thuật toán gắn:** Phase D dài 15 nến nhưng không có nhãn hồi test nào.
- **Đúng phải là:** trên ảnh, sau cú SOW có nhịp hồi lên ~4772 (quanh 17:20-17:25) rồi tiếp tục sụp — đó là một LPSY[D] rõ ràng: giá bò lên **chạm lại** vùng biên phụ 4768.9 nhưng không lấy lại được nó, rồi cung áp đảo tiếp. Đúng vai retest của CBR, phải được đánh dấu 1 điểm (L7).
- **Nghi phạm trong thuật toán:** LPS/LPSY[D] = swing pivot 5 nến + sàn 1.5× biên độ TB. Ở nhịp sụp, biên độ TB phình lên rất nhanh (cây SOW VSA 3.40x) nên sàn 1.5× trở nên quá cao, nhịp hồi thật bị loại. Sàn nên tính bằng ATR **trước** cú phá, không phải ATR đang bị cây phá kéo lên.

### 6. Diễn giải chỉ số nỗ lực/kết quả — lỗi chỉ số (trình bày)
- **Thuật toán gắn:** effort 2.40x, result 4.69, er=0.51 → "hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** er=0.51 là kết quả **gấp đôi** nỗ lực, không phải "kết quả ít". Nhãn in cứng, không phân ngưỡng (lỗi lặp ở cả 6 bài lô này).

## Đạt
- **Mục 1 (L1):** MOVE thật 43.0 giá / 64 nến, hiệu suất 0.37; đường xám trên ảnh đi từ 4735 lên đúng đỉnh BCLX. Climax là đỉnh cao nhất cửa sổ.
- **Mục 2 (L2):** đủ 3 lần đổi hướng, và ST[A] 12:31 tại **4794.1** — test lại **đúng** vùng climax 4790.9 (vượt nhẹ 3.2 giá, tạo biên phụ trên), VSA 1.38x. Đây là ST[A] chuẩn nhất trong cả lô 07-12.
- **Mục 4 (L4):** BCLX + phá xuống = **Phân phối**. Đúng.
- **Mục 5 (L9):** Phase B = 178 nến, chiếm 76% range, dài nhất — tỷ lệ phase đúng hình. Phase C 16 nến, ngắn nhất trong A/B/C/D. Đúng L8/L9 về tỷ lệ.
- **Mục 6 phần LPSY[C]:** LPSY[C] 16:51 tại 4789.8, VSA **2.92x**, thân 0.00 — nhịp hồi cuối lên sát biên trên rồi bị chặn, nỗ lực lớn kết quả bằng 0. Đúng vai LPSY[C] (test **trước** SOW), và không bị gộp lẫn với LPSY[D] — tránh được lỗi Ca #3 nguồn 4.pdf.
- **Mục 7/8 phần SOW:** SOW 17:16 tại 4765.0, đóng cửa **dưới cả biên phụ 4768.9**, VSA **3.40x**. Đúng yêu cầu L3 ("SOS/SOW mạnh phải bứt qua biên phụ") và đúng Effort vs Result.
- **mSOW 16:05** (4768.9, sâu 10.3 giá = 88% chiều cao biên chính) được để lại Phase B thay vì nâng thành Spring: đúng, cạnh AR không quyết định cú rũ; và nó khớp THEORY §4.4 dấu hiệu #1 (minor SOW xuất hiện ở Phase B).
- **Chỉ số SOT:** SOT-dn "chớm" n=2 với tỷ lệ volume 0.54 = **cạn kiệt** ở phía dưới, SOT-up "chớm" với volume 1.35 = hấp thụ ở trên. Đọc đúng bản chất một range sắp phá xuống.
