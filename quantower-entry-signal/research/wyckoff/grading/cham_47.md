# Chấm bài #47 — Phân phối (DIST) · 2026-07-15 18:31 → 2026-07-16 03:24 (473 nến M1)

**Điểm: 7/10** — Bài tốt nhất trong lô. Range thật, biên đúng, tên đúng, CBR đọc sạch. Chỉ cần thêm Phase C và kéo ST[A] về đúng vai.

## Lỗi (nặng → nhẹ)

### 1. Thiếu hoàn toàn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** timeline A(42) → B(286) → D(25) → E(121), không có dải C.
- **Đúng phải là:** đây là case KHÓ (không có UTAD nào phá được biên trên) → theo L8 phải **chờ SOW xuất hiện rồi quay lại vẽ Phase C**. Nhịp test cuối cùng là đỉnh ~4068 lúc 00:31–00:45 ngay trước cú sụp → đó là **LPSY[C]**, Phase C ≈ 00:45 → 00:58 (13 nến, đúng tinh thần "phase ngắn nhất").
- **Dấu hiệu quyết định trên chart:** ngay trước nến SOW 00:59 có một nhịp hồi lên chạm đúng biên chính dưới 4064.4 rồi bị đạp xuống một mạch 14 giá — nhịp hồi cuối cùng thất bại, kinh điển LPSY.
- **Nghi phạm trong thuật toán:** nhánh "gán ngược Phase C" (spec mục 6, cửa sổ min(60 nến, ½ Phase B)) không kích hoạt. Lỗi này lặp ở cả bài #46 và #48 → nghi nhánh gán ngược bị điều kiện tiền đề chặn (ví dụ đòi phải chưa có mSOS/mSOW nào, mà range nào cũng có).

### 2. ST[A] không quay về phía climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 19:12, giá 4069.7.
- **Đúng phải là:** climax 4089.1, AR 4064.4, chiều cao 24.7 giá. ST[A] ở 4069.7 = chỉ hồi **21%** chiều cao, tức 5.3 giá trên một range 24.7 giá — nằm ở 1/3 dưới cùng. Theo L2, lần đổi hướng thứ 3 phải là cú **quay về phía climax rồi bị chặn**; hồi 21% chưa đủ để gọi là test lại vùng climax.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm sát ngay trên nhãn AR, cách nhau vài giá, cả hai đều ở nửa dưới; sau ST[A] giá lập tức rơi xuống 4055.2 (mSOW).
- **Nghi phạm trong thuật toán:** giống bài #45 — "swing pivot 5 nến + sàn 1.5× biên độ TB" không có sàn tối thiểu theo chiều cao range. Đề xuất: ST[A] phải vào được 1/3 phía climax (THEORY §5 chia range 3 phần), nếu không thì tiếp tục chờ pivot sau.

### 3. Chỉ số SOT đo thiếu ở phía quyết định — lỗi đo
- **Thuật toán in:** SOT-up = `chớm`, n=1; SOT-dn = `SOT`, n=3, thrust cuối/đầu 0.19, volume 0.49 ("cạn kiệt").
- **Đúng phải là:** đây là range PHÂN PHỐI, thứ cần đo là **rút ngắn lực đẩy phía TRÊN** (đỉnh mới không cao hơn đỉnh cũ trước khi cung áp đảo). Đọc trên chart: đỉnh 19:01 ≈ 4070, đỉnh 20:49 ≈ 4072, đỉnh 22:43 ≈ 4068, đỉnh 00:31 ≈ 4068 — từ 20:49 trở đi các đỉnh thấp dần, đủ 3 nhịp = **có SOT phía trên**. Máy báo n=1.
- **Dấu hiệu quyết định trên chart:** ba đỉnh cuối Phase B đều nằm dưới đường biên chính dưới 4064.4… không, nằm quanh 4068–4072 và thấp dần đều — thấy rõ bằng mắt trên ảnh.
- **Nghi phạm trong thuật toán:** cách chia "nhịp" (swing leg) phía trên bỏ qua các đỉnh cách nhau xa (2 giờ) hoặc dùng sàn biên độ quá lớn nên gộp cả Phase B thành 1 nhịp. Ngược lại SOT-dn=3 nhịp lại báo bên **bán** cạn kiệt trong một range kết cục là phá xuống — công thức chạy đúng nhưng nội dung dẫn tới kết luận trái ngược với kết cục; đây là dấu hiệu SOT đang đo trên leg không đúng vai (phải đo leg **theo hướng xu hướng trước range**, tức phía trên).

### 4. Phase D dài đúng 25 nến = đúng trần cửa sổ chờ — lỗi nhẹ, cấu trúc
- **Thuật toán gắn:** Phase D = 00:59 → 01:23 = 25 nến, bằng chính tham số "cửa sổ chờ retest 25 nến".
- **Đúng phải là:** ranh giới D/E nên do cấu trúc quyết định (nhịp retest LPSY[D] kết thúc ở đâu), không do hết giờ. LPSY[D] đã xong ở 01:10 → Phase E lẽ ra bắt đầu quanh 01:12–01:14.
- **Nghi phạm trong thuật toán:** mốc chốt E vẫn rơi vào nến cuối cửa sổ khi giá chưa đi đủ 1.0× chiều cao trong 25 nến — tàn dư của lỗi J.

## Đạt
- **Mục 1 (mở range):** MOVE tăng 49.8 giá / 107 nến, hiệu suất 0.35 — trên ảnh là một đợt tăng liên tục 4037 → 4089 rất rõ, và cây BCLX 18:30 (VSA 4.52x, thân 0.81) chặn đúng đỉnh move. Điều kiện CẦN của L1 thoả đầy đủ, không phải gap tin.
- **Mục 3 (biên):** biên chính 4064.4–4089.1 = climax + AR, cố định suốt range; biên phụ dưới 4055.2 đúng là cực trị xa nhất; không có biên phụ trên (giá chưa lần nào phá 4089.1) — đúng L3, "có thể không có biên phụ nào".
- **Mục 4 (tên):** move tăng → BCLX; phá thật xuống → **Phân phối**. Khớp bảng L4.
- **Mục 5:** Phase B 286 nến = phase dài nhất tuyệt đối, đúng L9.
- **Mục 7 (D/E = CBR):** SOW 00:59 đóng cửa 4050.4 — bứt qua **biên phụ** 4055.2 (không chỉ biên chính), VSA 4.46x, thân 0.81. LPSY[D] 01:10 hồi lên đúng 4055.1 = chạm lại biên phụ rồi bị chặn, **giữ được ngoài biên**. Phase E 121 nến, giá đi tiếp xuống 4026 = hơn 1 lần chiều cao range. Đây là CBR mẫu, đúng nguyên văn L10.
- **Mục 8 (volume):** climax 4.52x → mSOW 2.29x → SOW 4.46x → LPSY[D] 0.82x. Nỗ lực nổ ở climax và cú phá, co lại ở nhịp test. Đọc đúng effort↔result.
- **Chỉ số bias = −1** (nới được biên dưới, không nới được biên trên) — đo đúng bản chất và khớp kết cục phá xuống. Chỉ số này dùng được.
- **Nhịp nỗ lực/kết quả er = 5.25** (effort 1.01x, result 0.19) — lần này chú thích "volume nhiều, kết quả ít" đúng nghĩa.

## Cần hỏi người học
- SOT nên đo trên leg phía nào? Ở bài này SOT phía dưới báo "cạn kiệt" ngay trước khi giá sụp 40 giá — nếu đọc SOT theo phía có tín hiệu thì sẽ đọc ngược hẳn kết cục. Đề xuất chỉ đọc SOT phía **cùng hướng move trước range** (phía trên với range gốc BCLX), xin xác nhận.
