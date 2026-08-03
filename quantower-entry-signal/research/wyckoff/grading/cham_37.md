# Chấm bài #37 — Tích lũy (ACC) · 2026-07-09 00:54 → 02:43 (109 nến M1)

**Điểm: 3/10** — Vẽ sai nhãn quan trọng nhất của bài: Spring thật ở 01:31 bị bỏ, một cú test không phá đáy ở 01:54 lại được gọi là Spring. Kéo theo đó, tên range "Tích lũy" gán cho một cấu trúc mà cú phá lên đã bị vô hiệu ngay trong Phase D.

## Lỗi (nặng → nhẹ)

### 1. Spring gán cho một đáy KHÔNG phá đáy thấp nhất range — luật vi phạm: lỗi kinh điển #6 nguồn 2.pdf (4/22 ca, lỗi phổ biến nhất của nguồn đó) / THEORY §3.3
- **Thuật toán gắn:** Spring tại 01:54, giá 4077.7, trạng thái "confirmed", VSA 6.41x.
- **Đúng phải là:** Spring phải là **điểm giá thấp nhất trong suốt Trading Range**. Đáy thấp nhất của range này là **4071.4 ở 01:31** — thấp hơn điểm được gọi Spring **6.3 giá**. Cú 01:54 chỉ thủng biên chính dưới 1.5 giá và không phá được đáy cũ → chỉ là **ST/LPS thường**, không phải Spring.
- **Dấu hiệu quyết định trên chart:** nến 01:31 (O 4074.0, L **4071.4**, C 4074.5, volume 276 = VSA 4.56x, thân 0.12 — râu dưới rất dài) rồi 01:32 đóng 4078.7, 01:33 đóng 4080.9 → **rút vào lại trong range sau đúng 2 nến**. Theo L5 (Spring = rút vào rất nhanh, ≈3-4 nến hoặc ít hơn) thì **01:31 mới là Spring**, và nó là Spring #3/Terminal Shakeout theo THEORY §3.5 (volume nổ, phá sâu). Máy để nó trắng nhãn.
- **Nghi phạm trong thuật toán:** cơ chế theo dõi cú phá biên **chỉ bật từ Phase B** (spec mục 5: "sau khi Phase A đã chốt, mỗi nến chỉ hỏi một câu"). Cú 01:31 nằm trong Phase A (00:54→01:41) nên chỉ âm thầm nới biên phụ xuống 4071.4 mà không sinh nhãn nào.

### 2. ST[A] gán muộn 10 nến, bỏ mất cú test vượt mức climax — luật vi phạm: L2, L3
- **Thuật toán gắn:** ST[A] tại 01:41, giá 4079.4, VSA 0.35x.
- **Đúng phải là:** ST[A] = đáy **4071.4 ở 01:31**. Đó chính là lần đổi hướng thứ ba theo L2 (giá quay về phía climax rồi bị chặn), và nó **vượt qua mức climax** — L3 nói tường minh trường hợp này tạo biên phụ, tức luật đã lường trước ca ST[A] nằm ngoài biên chính.
- **Dấu hiệu quyết định trên chart:** biên phụ dưới 4071.4 nằm sát đáy dài nhất của cả range; ST[A] mà máy chọn (4079.4) nằm **cao hơn 8 giá**, gần đúng mức climax, tức nó là lần chạm lại **thứ hai**.
- **Nghi phạm trong thuật toán:** điều kiện ST[A] "phải hồi ≥40% chiều cao climax↔AR rồi 5 nến liên tiếp không tạo cực trị mới". Sau 01:31 giá bật lên rất nhanh nên bộ đếm 5 nến bị reset/chưa kịp chốt, máy phải đợi tới nhịp lình xình 01:36-01:41.

### 3. Tên range "Tích lũy" trong khi cú phá lên đã bị vô hiệu — luật vi phạm: L4 + L10 / THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** ACC (Tích lũy), Phase D 02:18→02:43, range đóng ở D.
- **Đúng phải là:** cú SOS chỉ đi được tới **4091.9 ở 02:26** (3.7 giá trên biên chính trên 4088.2 = 41% chiều cao range), rồi **02:33 đóng cửa 4083.4** — lùi hẳn vào trong range **4.8 giá = 48 tick**, vượt ngưỡng "cú phá hỏng 30 tick" của chính spec (mục 7 Câu 1). Sau khi range đóng, giá xuống **4063.4 lúc 03:18** — thấp hơn cả biên phụ dưới 4071.4 tới 8 giá. Đây là **tích luỹ thất bại = thực chất phân phối** (THEORY §9: "tích luỹ thất bại sẽ luôn là một cấu trúc phân phối").
- **Dấu hiệu quyết định trên chart:** ngay bên phải nhãn SOS, giá rơi liền một mạch từ 4091 xuống 4061 trong ~40 phút — dài gấp hơn 3 lần chiều cao range, ngược hướng nhãn ACC.
- **Nghi phạm trong thuật toán:** kiểm tra "cú phá hỏng" (mục 7 Câu 1) chạy trong cửa sổ 25 nến sau SOS, nhưng khi nó bắn thì range **vẫn được đóng và vẫn giữ tên** theo hướng SOS. Cần: cú phá bị vô hiệu → không được dùng hướng đó để đặt tên range (quay về "chưa rõ", hoặc đổi tên theo hướng phá kế tiếp).

### 4. Phase B là phase NGẮN NHẤT, Phase C dài gấp đôi Phase B — luật vi phạm: L9, L8
- **Thuật toán gắn:** A 48 · B 12 · C 24 · D 26.
- **Đúng phải là:** B dài nhất (L9), C ngắn nhất (L8). Ở đây trật tự bị đảo hoàn toàn: B ngắn nhất, C và D đều dài gấp đôi B.
- **Dấu hiệu quyết định trên chart:** vạch "Phase B (12n)" và "Phase C (24n)" nằm sát nhau ở giữa chart, còn Phase A chiếm gần một nửa khung range.
- **Nghi phạm trong thuật toán:** hệ quả của lỗi 2 — ST[A] muộn 10 nến ăn hết Phase B; và mốc "Phase C chờ tối đa 120 nến" cho phép C dài tuỳ ý miễn dưới 120.

## Đạt
- **Điều kiện mở range (L1):** MOVE giảm 19.9 giá / 39 nến / hiệu suất 0.40; climax 00:54 là đáy cửa sổ, VSA 2.69x, thân 0.82. Đúng "climax chặn move".
- **Biên (L3):** biên chính 4079.2 + 4088.2 chốt sau Phase A và không bị kéo theo giá; biên phụ 4071.4/4090.7 đúng là hai cực trị xa nhất, mỗi bên 1.
- **Đọc effort/result tại 01:54:** volume 311 (VSA 6.41x) mà giá chỉ thủng 1.5 giá dưới biên rồi bật — nỗ lực lớn / kết quả nhỏ, đúng dấu hiệu hấp thụ. Máy phát hiện đúng **chỗ** này, chỉ gọi **sai tên** (Spring thay vì LPS/test).
