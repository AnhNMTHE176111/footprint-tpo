# Chấm bài #29 — Chưa rõ (BCLX) (DIST?) · 2026-06-12 08:20 → 20:59 (759 nến M1)

**Điểm: 1/10** — Không nên vẽ range ở đây. Biên chính rộng 9.2 giá trong khi giá lang thang 59.3 giá quanh nó: cái được vẽ không phải một vùng đấu giá, chỉ là 9 giá bất kỳ ở giữa một ngày giao dịch 13 tiếng.

## Lỗi (nặng → nhẹ)

### 1. Nến mang nhãn BCLX có VSA 0.96x — DƯỚI cả trung bình — luật vi phạm: L1, §3.3/§4.1 THEORY
- **Thuật toán gắn:** BCLX tại 4242.0 lúc 08:20, VSA **0.96x**, 154 lot.
- **Đúng phải là:** cao trào mua thật là **08:18 (VSA 2.89x, 474 lot, thân 0.85, đóng đúng đỉnh 4240.3)**, hỗ trợ bởi 08:19 (2.00x). Nến 08:20 volume 154 lot — **thấp hơn mức trung bình 20 nến**. Gọi một nến dưới trung bình là "cao trào" là mâu thuẫn tự thân với định nghĩa (§4.1: "volume + spread tăng rõ rệt").
- **Dấu hiệu quyết định trên chart:** 474 → 337 → **154** lot. Ngưỡng mở range của chính thuật toán là VSA ≥ 2.2x; nến mang nhãn đạt **0.96x**, tức **kém ngưỡng 2.3 lần**.
- **Nghi phạm trong thuật toán:** đúng lỗi ở bài #28 nhưng nặng hơn — mục 4.0 dời mốc climax theo **cực trị giá** trong 8 nến mà không kiểm lại tính chất nến đích. Ở đây đỉnh 4242.0 (râu nến 08:20) cao hơn đỉnh 4240.3 của cây climax thật đúng **1.7 giá**, và chỉ vì 1.7 giá râu nến mà nhãn BCLX bị dời sang một nến vô nghĩa. Đây cũng là lỗi "neo bóng nến thay vì giá đóng cửa" (Ca #5 nguồn 4.pdf): đóng cửa 08:18 là 4240.3, đóng cửa 08:20 là **4234.8** — thấp hơn 5.5 giá.

### 2. Biên chính 9.2 giá, biên phụ 59.3 giá — biên phụ gấp 6.4 lần biên chính — luật vi phạm: L3
- **Thuật toán gắn:** biên chính 4232.8–4242.0 (9.2 giá, 0.22%); biên phụ 4197.5–4256.8 (59.3 giá).
- **Đúng phải là:** biên phụ theo L3 là "mức cực trị xa nhất mà một thế lực đã cố phá range gốc tạo ra" — nó phải là phần **thò ra** khỏi range, không phải phần bao trùm range. Ở đây range gốc chiếm 9.2/59.3 = **15%** vùng giá thực tế. Nói cách khác: 85% hoạt động giá nằm ngoài cái range được vẽ. Đó không còn là biên phụ, đó là bằng chứng range gốc chọn sai chỗ.
- **Dấu hiệu quyết định trên chart:** hai đường liền cam (4232.8 / 4242.0) nằm sát nhau ở giữa ảnh, trong khi giá xuống tận 4197.5 lúc 14:47 rồi lên 4256.8 lúc 15:27 — cả hai đều thò ra xa gấp nhiều lần chiều cao range.
- **Nghi phạm trong thuật toán:** guard "range quá cao > 3.5% giá" (mục 8) chỉ đo biên chính nên vô hiệu — biên chính càng hẹp thì càng an toàn theo guard, đúng ngược với thực tế. Thiếu guard theo tỉ lệ biên phụ/biên chính (bài #28 cũng đã chạm lỗi này, ở đây nó bung hoàn toàn).

### 3. ST[A] ở 4244.9 với VSA 3.41x — nến mạnh nhất Phase A lại bị gọi là "test nhẹ" — luật vi phạm: L2, §3.3 THEORY (ST có spread/volume GIẢM)
- **Thuật toán gắn:** ST[A] tại 4244.9 lúc 08:39, VSA **3.41x**, thân/biên **0.08**.
- **Đúng phải là:** ST theo định nghĩa là cú test với volume/spread **thu hẹp** vì tay mạnh đã hành động ở climax. Một nến 3.41x — gấp 3.5 lần cây được gọi là BCLX (0.96x) — không thể là ST. Đây mới là cây cao trào thật của cấu trúc: nó vượt qua mức "climax" 4242.0, thân 0.08 (râu dài, bị đè) — đúng khuôn một **UT/BCLX thật**, và nó là điểm phải chọn làm biên trên.
- **Dấu hiệu quyết định trên chart:** VSA ST[A] 3.41x > VSA BCLX 0.96x. Vai trò bị đảo hoàn toàn: nến yếu làm climax, nến mạnh làm test.
- **Nghi phạm trong thuật toán:** mục 4.2 — ST[A] tìm bằng **swing pivot** thuần cấu trúc (5 nến không cực trị mới), người học đã chốt "không đo bằng %". Nhưng bỏ hết ngưỡng % thì cũng phải giữ ràng buộc chất: một ST không được có VSA **cao hơn** cây climax của chính nó. Đây là ràng buộc rẻ và an toàn, không vi phạm quyết định "đo bằng cấu trúc".

### 4. Có nhãn LPSY[C] gắn Phase "C" nhưng bảng phase KHÔNG có Phase C — timeline tự mâu thuẫn — luật vi phạm: L8, lỗi hệ thống C (v5 chưa vá hết)
- **Thuật toán gắn:** LPSY[C] tại 4245.8 lúc 09:14 với cột Phase = **C**; nhưng bảng phase chỉ có A (20 nến) và B (740 nến).
- **Đúng phải là:** hai thứ này không thể cùng tồn tại. Đây là dấu vết của Phase C bị xoá (đúng theo vá lỗi C) nhưng **nhãn sự kiện thuộc Phase C không bị xoá theo**.
- **Dấu hiệu quyết định trên chart:** LPSY[C] hiện trên ảnh lúc 09:14 mà không có vạch dọc tím nào mở Phase C.
- **Nghi phạm trong thuật toán:** vá lỗi C (mục 6) xoá **đoạn** Phase C khỏi timeline và đổi nhãn shock, nhưng không dọn các nhãn **LPS[C]/LPSY[C]** đã sinh ra trong đoạn đó.

### 5. Phase B 740/759 nến = 97.5% range, không có Phase C/D/E — nhưng range vẫn ghi "[completed]" — luật vi phạm: L2/L9 (trình bày + trạng thái)
- **Thuật toán gắn:** tiêu đề "[completed]", tên "Chưa rõ (BCLX) (DIST?)".
- **Đúng phải là:** một range đóng ở Phase B, chưa từng có cú phá được xác nhận, thì phải là **"bỏ / không kết luận"**, không phải "completed". Dấu "(DIST?)" cũng không có cơ sở: trong range này mSOW (4197.5) và mSOS (4256.8) đều xuất hiện và **mSOS đến sau** (15:27 sau 14:47) — nếu buộc phải đoán thì bằng chứng cuối nghiêng về phía TĂNG, ngược với "(DIST?)".
- **Dấu hiệu quyết định trên chart:** 740 nến Phase B; và cây tăng vọt cuối chart (khoảng 4290 → 4325 sau 20:59) cho thấy giá cuối cùng đi **lên**, không xuống.
- **Nghi phạm trong thuật toán:** nhãn "(DIST?)" hình như suy từ **loại climax** (BCLX ⇒ đoán phân phối) — đúng cái sai mà L4/mục 2b đã cấm ("thuật toán **không đoán**", phải hiển thị "Chưa rõ (BCLX)" là hết). Chuỗi "(DIST?)" nên bỏ.

## Đạt
- Mục 1 phần MOVE (L1): MOVE tăng 42.3 giá / 47 nến / hiệu suất **0.52** — move này là thật, hiệu suất cao nhất trong 5 bài của lô. Việc *có* một cao trào tại đây là đúng; chỉ có nến được chọn là sai.
- Mục 3 phần "mỗi bên tối đa 1 biên phụ": đúng — 1 trên (4256.8), 1 dưới (4197.5).
- Mục 4: thuật toán **không** đặt tên range khi chưa có cú phá xác nhận — giữ "Chưa rõ (BCLX)". Đúng L4/mục 2b (trừ cái đuôi "(DIST?)" nói ở lỗi 5).
- Mục 9 phần nhãn dư: không spam nhãn lặp; mSOS/mSOW mỗi bên đúng 1 cái.

## Kết luận cấu trúc
**Không vẽ range ở đây.** Ngày 12/06 này là một phiên dao động rộng 59 giá không có vùng cân bằng hẹp nào chiếm ưu thế; chọn 9.2 giá làm biên là chọn ngẫu nhiên. Nếu bắt buộc phải đọc, phải mở range bằng **đỉnh 08:39 (VSA 3.41x)** làm biên trên và lấy đáy 4197.5 hoặc một đáy cục bộ gần hơn làm biên dưới — tức một range rộng gấp mấy lần, và khi đó Phase A phải vẽ lại từ đầu. Bài này là ca dùng để chốt hai guard còn thiếu: (a) không dời nhãn climax sang nến không đạt VSA, (b) huỷ range khi biên phụ vượt quá ~1.5 lần biên chính.
