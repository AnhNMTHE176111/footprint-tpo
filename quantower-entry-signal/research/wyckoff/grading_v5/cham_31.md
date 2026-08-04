# Chấm bài #31 — Tích luỹ (ACC) · 2026-06-15 12:18 → 16:10 (232 nến M1)

**Điểm: 4/10** — cấu trúc Phase A đọc được, nhưng SOS neo sai cây và Phase E là một đoạn 119 nến giá đi ngược hoàn toàn ý nghĩa "rời range tìm vùng giá mới". Phải sửa nhãn, không phải vẽ lại range.

## Lỗi (nặng → nhẹ)

### 1. Phase E dài 119 nến nhưng giá QUAY VỀ lại range — không phải Phase E — luật vi phạm: L10
- **Thuật toán gắn:** Phase E từ 14:12 đến 16:10, 119 nến, range đóng ở trạng thái "completed", tên **Tích luỹ**.
- **Đúng phải là:** nhìn trên ảnh, sau đỉnh ~4392 (khoảng 14:05) giá lăn dốc suốt phần còn lại và **kết thúc ở 4359-4360**, tức là **quay hẳn về giữa/dưới biên chính** (biên trên 4370.8, biên dưới 4345.3). Phase E theo L10 là "giá thuận lực đi tiếp để tìm vùng giá mới". Ở đây giá đi được đúng ~1 nhịp rồi trả lại toàn bộ. Đây là **cú phá THẤT BẠI** — theo lỗi F đã vá ở v5, nó phải hạ cấp thành mSOS, trả dải phase về B, và range **không được đặt tên** "Tích luỹ".
- **Dấu hiệu quyết định trên chart:** giá cuối range 4359.8 < biên trên 4370.8. Giá đã đóng cửa lùi lại **vào trong** biên chính, thoả đúng điều kiện "lùi hẳn qua biên 30 tick" ở mục 7 Câu 1.
- **Nghi phạm trong thuật toán:** cửa sổ kiểm tra Câu 1/Câu 2 của mục 7 chỉ dài **25 nến** sau SOS. Giá giữ ngoài biên trong 25 nến đó rồi mới sụp ở nến thứ ~40 → máy đã chốt Phase E và đóng range trước khi cú phá hỏng. Cửa sổ 25 nến quá ngắn so với Phase E được vẽ 119 nến; ít nhất phải theo dõi hết chiều dài Phase E, không phải chỉ 25 nến đầu.

### 2. SOS neo vào nến VSA 0.51× — đúng lỗi B mà v5 tuyên bố đã vá — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** SOS tại 13:47, giá 4383.0, **VSA 0.51×**, thân 0.53.
- **Đúng phải là:** cây phá thật nằm sớm hơn. Đọc panel volume: cụm thanh vàng (VSA ≥ 2.2×) dày đặc quanh **13:30-13:37** — chính là đoạn giá bứt từ 4373 lên 4385. SOS phải hồi tố về cây VSA cao nhất trong đoạn đó, không phải cây 0.51× ở 13:47 khi giá đã đi xong.
- **Dấu hiệu quyết định trên chart:** VSA 0.51× nghĩa là khối lượng **chỉ bằng một nửa trung bình 20 nến**. Một cây SOS mà nỗ lực dưới trung bình thì theo định nghĩa gốc SOS ("spread + volume tăng đều", THEORY §3.3) nó không phải SOS.
- **Nghi phạm trong thuật toán:** logic hồi tố lỗi B ("nhãn đặt vào cây VSA cao nhất, đúng hướng, đóng cửa vượt biên") chỉ tìm trong **đoạn 3 nến xác nhận**, không tìm ngược tới cây khởi phát cú phá. Phải mở cửa sổ tìm ngược từ nến thò ra khỏi biên đầu tiên.

### 3. LPS[C] đặt tại cây VSA 2.87× NGOÀI biên trên — sai vai — luật vi phạm: L7 + §5 THEORY
- **Thuật toán gắn:** LPS[C] tại 13:30, giá **4373.6**, VSA 2.87×.
- **Đúng phải là:** biên chính trên = 4370.8, biên phụ trên = 4371.5. Giá 4373.6 nằm **trên cả hai biên**. Một điểm nằm ngoài biên trên, với volume gần 3× trung bình, không phải "test hỗ trợ cuối cùng" (LPS) — đó chính là **cây SOS** (xem lỗi #2). Máy đã gọi đúng cây nhưng gán sai tên.
- **Dấu hiệu quyết định trên chart:** LPS theo định nghĩa là điểm **hỗ trợ** — phải là một cái đáy của nhịp hồi. Cây 13:30 nằm ở đỉnh cú bứt, cao hơn mọi biên.
- **Nghi phạm trong thuật toán:** nhánh "Phase C gán ngược" (mục 6, case khó) nhìn lại 60 nến trước cú phá và lấy **cực trị**; nó lấy đáy sâu nhất — nhưng vì SOS đã bị neo trễ ở 13:47, cửa sổ 60 nến quét ngược lại rơi trúng chính vùng bứt phá. Sửa lỗi B (neo SOS đúng cây) sẽ tự kéo LPS[C] về đúng chỗ.

### 4. Phase A 49 nến > Phase B 23 nến — luật vi phạm: L9
- **Thuật toán gắn:** A=49, B=23, C=17, D=25.
- **Đúng phải là:** Phase B phải là phase dài nhất. Ở đây B chỉ bằng chưa tới một nửa A.
- **Dấu hiệu quyết định trên chart:** ST[A] chốt ở 13:06 tại giá 4362.8, nhưng nhìn ảnh giá còn dao động trong biên tới 13:30. Cả đoạn 13:06→13:30 nên chủ yếu là Phase B; A dài 49 nến vì AR mãi tới 12:57 (39 nến sau climax) mới được xác nhận.
- **Nghi phạm trong thuật toán:** AR là "swing pivot đầu tiên xác nhận sau 5 nến" (mục 4.1) nhưng cú bật từ SC 4345.3 lên 4370.8 là một chân tăng **liên tục 39 nến** không có pivot trung gian — nên AR bị đẩy ra rất xa. Không phải lỗi logic thuần, mà là hệ quả của việc range này thực chất là **một chân tăng, không phải vùng cân bằng** (xem mục 10).

### 5. ST[A] không test lại vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 13:06, giá 4362.8.
- **Đúng phải là:** ST[A] là lần thứ 3 đổi hướng, giá **quay về phía climax rồi bị chặn**. Climax ở 4345.3, AR ở 4370.8 — chiều cao 25.5 giá. ST[A] ở 4362.8 chỉ lùi 8.0 giá từ AR = **31% chiều cao**, còn cách climax 17.5 giá. Đây là một cái ngọ nguậy ở **nửa trên** range, không phải test vùng SC.
- **Dấu hiệu quyết định trên chart:** trên ảnh, nhãn ST[A] nằm cao hơn hẳn đường "biên CHINH duoi 4345.3" — cách nhau gần 2/3 chiều cao chart của range.
- **Nghi phạm trong thuật toán:** mục 4.2 đã **bỏ hết ngưỡng %** theo chốt của người học ("đo bằng cấu trúc"), chỉ còn "swing pivot 5 nến + nhịp ≥1.5× biên độ TB". Với nhịp lùi 8 giá trên nền biên độ TB nhỏ, điều kiện này quá dễ thoả. Cần thêm ràng buộc **hướng**: ST[A] phải nằm ở nửa range phía climax (xem THEORY §5 — bảng vị trí ST chia 3 phần).

## Đạt
- Điều kiện mở range (L1): có MOVE giảm thật 20.2 giá / 36 nến / hiệu suất 0.51, cây climax 12:18 là đáy 4345.3 chặn đúng move đó — đọc chuỗi 6 nến trước climax thấy volume leo đều 83→282, đúng dạng bán tháo. Mở range ở đây hợp lệ.
- Biên chính = climax 4345.3 + AR 4370.8, cố định suốt range, không bị kéo theo giá. Đúng L3.
- Biên phụ chỉ 1 cái ở trên (4371.5), không spam. Đúng L3.
- Phase C 17 nến là phase ngắn nhất. Đúng L8.
- LPS[D] chỉ 1 điểm duy nhất. Đúng L7.

## Kết luận cấu trúc
Nếu là tôi: **vẫn vẽ range ở đây nhưng không đặt tên "Tích luỹ"**. Biên chính đúng, Phase A đúng ý tưởng. Nhưng cú bứt 13:30 không giữ được — giá trả về 4359 sau 2 tiếng — nên nó là **mSOS**, range kết thúc ở trạng thái chưa rõ. Gọi "Tích luỹ hoàn tất Phase E" cho một cấu trúc mà giá quay về đúng chỗ cũ là gán tên cho cú phá đã hỏng.
