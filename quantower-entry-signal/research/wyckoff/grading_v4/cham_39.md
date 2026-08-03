# Chấm bài #39 — Tái phân phối (RE-DIST) · 2026-07-12 22:40 → 2026-07-13 03:42 (301 nến M1)

**Điểm: 3/10** — Bối cảnh đọc đúng (một chỗ nghỉ giữa đợt xả, xả tiếp), tên range đúng, nhưng ba trụ của cấu trúc đều sai: AR đặt ở nến thứ 89 sau climax, Phase C dài 121 nến thành phase dài thứ hai, và SOW gán vào một nến doji volume 0.30×.

## Lỗi (nặng → nhẹ)

### 1. SOW gán vào nến doji volume 0.30× — luật vi phạm: THEORY §4.1 (SOW = "chênh lệch + khối lượng tăng") / Effort vs Result §2.2
- **Thuật toán gắn:** SOW tại 03:17, giá 4066.9, **VSA 0.30x**, **thân 0.13**.
- **Đúng phải là:** SOW tại **03:11** (O 4066.8 → C 4063.0, đáy 4061.4, volume 406 = **VSA 4.24x**, thân 0.58), nối tiếp bởi 03:12 (VSA 2.52x). Đây là hai nến duy nhất trong vùng có khối lượng nổi bật và đóng cửa bứt sâu qua biên phụ dưới 4069.4.
- **Dấu hiệu quyết định trên chart:** cột khối lượng vàng cao ở 03:11-03:12; nến 03:17 mà máy chọn có volume 36 — bằng **1/11** nến phá, và thân chỉ 13% biên độ, tức một nến do dự nằm trong nhịp hồi đã bắt đầu. Chính spec của thuật toán yêu cầu thân ≥45% để công nhận SOS/SOW; nến này 13%.
- **Nghi phạm trong thuật toán:** giống bài #36 — nhãn đặt ở nến **xác nhận cuối chuỗi** (hoặc nến timeout "ở ngoài quá 40 nến") thay vì nến **phá**. Chuỗi "3 nến liên tiếp đóng cửa vượt biên phụ ≥30 tick, thân ≥45%" bị ngắt tại 03:12 (thân 0.03), nên nhãn trôi tiếp.

### 2. AR đặt ở nến thứ 89 sau climax — không còn là "phản ứng tự động" — luật vi phạm: L2 / THEORY §3.3 (AR = "áp lực bán giảm mạnh → sóng mua đẩy giá lên")
- **Thuật toán gắn:** AR tại 00:09 (89 nến sau climax 22:40), giá 4099.0 → biên chính trên 4099.7.
- **Đúng phải là:** AR là cú bật **ngay sau** climax. Cực trị của cửa sổ 40 nến chuẩn là **4088.8 lúc 22:52** (bật 3.4 giá). Đợt leo tới 4099.0 xảy ra **sau khi giá đã đi ngang khoảng 60 nến** trong vùng 4076-4088 — đó là một nhịp tăng nội bộ range, không phải Automatic Rally.
- **Dấu hiệu quyết định trên chart:** giữa nhãn SC và nhãn AR có gần một giờ nến lình xình quanh 4078-4085, rồi mới có đoạn leo dốc lên 4099. Một AR thật không có đoạn đi ngang chen giữa.
- **Nghi phạm trong thuật toán:** ngưỡng "**AR phải hồi ≥ 30% độ dài move**" — với move 43.6 giá, ngưỡng này đòi AR bật ≥ **13.1 giá**, gấp gần 4 lần cú bật thật (3.4 giá). Máy buộc phải chờ 89 nến. Chính tài liệu thuật toán ghi ngưỡng này là "Claude tự thêm, KHÔNG có trong review" (mục 12.4) — đây là ca cho thấy nó gây hại.

### 3. Phase C dài 121 nến, dài hơn cả Phase B cộng lại — luật vi phạm: L8 (C ngắn nhất), L9 (B dài nhất)
- **Thuật toán gắn:** A 98 · B 15 · **C 121** · B 42 · D 26.
- **Đúng phải là:** C ngắn nhất, B dài nhất. Ở đây C (121 nến) dài hơn tổng hai đoạn B (15+42 = 57 nến) hơn hai lần, và A (98 nến) cũng dài hơn B.
- **Dấu hiệu quyết định trên chart:** vạch "Phase C (121n)" trải gần một nửa chiều ngang khung range, đúng chỗ giá đang dao động qua lại giữa hai biên — tức đúng nơi phải là Phase B.
- **Nghi phạm trong thuật toán:** ngưỡng "Phase C chờ tối đa 120 nến" (mục 6). Cú rũ ở 00:34 không sinh SOW nên Phase C được giữ nguyên đúng 120 nến rồi mới lùi về B — biến một phase định nghĩa là "ngắn nhất" thành phase dài nhất.

### 4. Cú rũ bị gán "(thất bại)" dù đã đi được 95% sang biên đối diện — luật vi phạm: mâu thuẫn nội bộ với spec mục 6 ("≥50% → XÁC NHẬN")
- **Thuật toán gắn:** Shakeout (thất bại), trạng thái `failed`, vẽ xám, tại 00:34 giá 4069.4.
- **Đúng phải là:** từ điểm rũ 4069.4 giá đã lên tới **4098.3 lúc 01:32** — đi được 28.9 trên tổng 30.3 giá tới biên đối diện 4099.7 = **95%**. Theo chính mục 6 của spec, mốc 50% đã bị vượt xa nên cú rũ phải được ghi **XÁC NHẬN** (chấm viền trắng đậm), không phải "(thất bại)" màu xám.
- **Dấu hiệu quyết định trên chart:** đỉnh cao nhất trong dải Phase C nằm sát ngay dưới đường biên chính trên 4099.7 — mắt thường thấy giá đã đi hết range.
- **Nghi phạm trong thuật toán:** hai điều kiện "đi ≥50% → xác nhận" và "quá 120 nến → thất bại" chồng lên nhau, và trạng thái cuối lấy theo **timeout** thay vì theo tiến độ đã đạt trước đó. Cần: một khi đã đạt 50%, trạng thái `confirmed` phải bị chốt cứng, timeout sau đó chỉ được đóng Phase C chứ không được đổi nhãn thành thất bại.
- **Ghi chú trung thực:** theo THEORY §9, một cú sốc quay đầu **trước khi** chạm hẳn biên đối diện vẫn là "cấu trúc thất bại", nên nhãn "(thất bại)" tình cờ hợp với sách. Nhưng nó không được suy ra bằng phép đo đó — nó ra từ timeout — và nó trái với ngưỡng 50% mà spec tự đặt. Đây là lỗi **nhất quán logic**, không phải lỗi Wyckoff thuần.

### 5. Phase A dài 98 nến, dài nhất trong range — luật vi phạm: L2, L9
- **Thuật toán gắn:** Phase A = 22:40 → 00:18, 98 nến.
- **Đúng phải là:** Phase A chỉ gồm 3 lần đổi hướng (climax → AR → ST[A]). 98 nến trên M1 chứa hàng chục lần đổi hướng.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của lỗi 2 — AR trôi 89 nến thì Phase A phình theo.

## Đạt
- **Điều kiện mở range (L1):** MOVE giảm rất rõ — 43.6 giá / 41 nến / hiệu suất 0.46, trên chart là một cú rơi thẳng đứng liên tục; climax 22:40 là đáy cửa sổ, VSA 4.10x, biên độ 4.6 giá. Đúng "climax chặn move".
- **Tên range (L4):** origin SC + phá xuống thật = Tái phân phối. Đúng, và đúng cả về bối cảnh: giá rơi 43 giá, nghỉ 300 nến, xả tiếp xuống 4061.
- **Biên (L3):** biên chính 4085.4 + 4099.7 cố định; biên phụ dưới 4069.4 = cực trị xa nhất, không có biên phụ trên (giá chưa vượt 4099.7 — đỉnh cao nhất chỉ 4098.3). Nhất quán.
- **Phân loại Shakeout thay vì Spring (L5):** đúng. Nến 00:34 đóng 4071.0, và giá phải mất hơn 4 nến mới đóng cửa lại trên biên chính dưới 4085.4 (00:42 vẫn còn ở 4081.7) → theo L5 là Shakeout, không phải Spring. Không sửa.
- **LPSY[D] (L7, L10):** một điểm duy nhất tại 03:29 giá 4070.3, là nhịp hồi sau SOW và chỉ vượt lại biên phụ 0.9 giá (9 tick, dưới ngưỡng 30 tick) → vẫn "giữ được ngoài biên". Đúng vai và đúng cách vẽ.
