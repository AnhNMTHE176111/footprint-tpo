# Chấm bài #36 — Tái phân phối (RE-DIST) · 2026-07-06 12:43 → 2026-07-07 22:23 (1886 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây. Cây "climax" VSA 1.28× không chặn được gì, và cái range 17.4 giá bị giá đi lang thang 64.7 giá quanh nó suốt 1886 nến — đó không phải một vùng đấu giá, đó là một đoạn chart bị cắt bừa.

## Lỗi (nặng → nhẹ)

### 1. Climax không phải climax, và không chặn được move — luật vi phạm: L1
- **Thuật toán gắn:** SC tại 12:43, giá 4143.3, **VSA 1.28×**, biên độ nến 1.9 giá, thân/biên 0.16.
- **Đúng phải là:** không mở range. Ngưỡng climax của chính spec là **VSA ≥ 2.2×** (mục 11 tài liệu thuật toán) — 1.28× thậm chí còn thấp hơn nến −2 (3.27×) và nến −1 (1.93×) ngay trước nó. Nếu buộc phải chọn một cây cao trào trong cụm này thì đó là **12:41 (VSA 3.27×, biên độ 5.6 giá, thân 0.82)**, chứ tuyệt đối không phải cây 12:43.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến quanh climax — cây được chọn có volume 173 trong khi hai cây trước nó là 418 và 256. Cây climax mà volume **nhỏ hơn** hai cây liền trước thì không có gì để gọi là "cao trào".
- **Nghi phạm trong thuật toán:** cơ chế "cụm climax" ở mục 4.0 — nó dời mốc climax sang **cực trị mới** trong 8 nến đầu mà **không kiểm lại điều kiện VSA/biên độ tại cây mới**. Cây 12:41 đủ ngưỡng, nhưng đáy thấp hơn nằm ở 12:43, nên mốc bị dời sang một cây nến hoàn toàn tầm thường và VSA in ra trên tiêu đề chart cũng là VSA của cây tầm thường đó. Phải giữ nguyên "cây đủ tiêu chuẩn climax" làm sự kiện, chỉ dời **MỨC GIÁ** biên xuống cực trị của cụm.

### 2. Range chính 17.4 giá nhưng giá đi 64.7 giá xung quanh — luật vi phạm: L1 + L3
- **Thuật toán gắn:** biên chính 4143.3–4160.7 = 17.4 giá; biên phụ 4127.7–4192.4 = **64.7 giá**, tức gấp **3.7 lần** biên chính.
- **Đúng phải là:** khi biên phụ gấp gần 4 lần biên chính thì hai cái "biên chính" đó đã không còn là biên của bất cứ vùng cân bằng nào — chúng chỉ là hai đường ngang nằm lọt giữa chart. Đây đúng là ca giảng viên bắt trong CHART_CASES (Ca #20 nguồn 7.pdf — "gượng ép"): cấu trúc phải gò mới khớp thì đừng gò.
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, hai đường cam nét liền nằm **giữa** thân biểu đồ, giá đi lên tận 4192 rồi xuống 4127 rồi lại lên 4192 mà không hề coi hai đường đó là gì. Trên phiếu số liệu: biên chính = 0.42% giá, biên phụ = 1.57% giá.
- **Nghi phạm trong thuật toán:** guard "range quá cao" (mục 8) đo bằng **biên chính** cố định (3.5% giá) nên không bao giờ bắn. Cần thêm guard theo **tỉ lệ biên phụ / biên chính** — vượt ~2× là dấu hiệu biên chính đã mất nghĩa, phải bỏ range.

### 3. Phase B 1697 nến = 90% cả range — luật vi phạm: L9 (đúng chữ, sai tinh thần)
- **Thuật toán gắn:** A=33 · B=**1697** · C=28 · D=8 · E=121.
- **Đúng phải là:** L9 nói Phase B dài nhất, không nói Phase B được phép nuốt 28 tiếng đồng hồ trong khi Phase A chỉ 33 nến. Tỉ lệ A:B = 1:51 nghĩa là máy đã chốt hai biên trong 33 phút rồi treo chúng suốt 28 tiếng chờ một cú phá. Trong 28 tiếng đó giá đã đi qua **hai chu kỳ lên-xuống hoàn chỉnh** (nhìn ảnh: đỉnh 4181 lúc 16:40, đáy 4130 lúc 05:10, đỉnh 4192 lúc 13:37) — mỗi cái đáng lẽ là một range riêng.
- **Dấu hiệu quyết định trên chart:** mSOW ở 4130.6 (09:29) và mSOS ở 4192.4 (13:42) cách nhau **62 giá** — hai sự kiện này mà cùng nằm trong một Phase B thì "Phase B" ấy là cả một xu hướng, không phải giai đoạn xây nguyên nhân.
- **Nghi phạm trong thuật toán:** mục 13.3 đã tự nhận — "vẫn chỉ theo dõi ĐÚNG MỘT range một lúc". Range này mở lúc 12:43 và khoá cứng mọi climax mới trong 1886 nến. Đây là chỗ đắt nhất phải sửa.

### 4. mSOS 4192.4 vượt biên phụ trên rồi mà vẫn ở lại Phase B — luật vi phạm: L3 (SOS mạnh = đóng cửa bứt biên phụ)
- **Thuật toán gắn:** mSOS tại 4192.4 — **chính là mức biên phụ trên** (4192.4), VSA 1.39×, thân 0.34.
- **Đúng phải là:** ở đây gọi mSOS là chấp nhận được (nó tạo ra biên phụ chứ không bứt qua biên phụ đã có), nhưng phải thấy điều nó nói: một cú đi **32 giá trên biên chính trên** mà vẫn bị coi là "thăm dò thất bại trong Phase B" thì định nghĩa range đang sai chứ không phải nhãn sai. Cùng lý do như lỗi #2.
- **Dấu hiệu quyết định trên chart:** 4192.4 − 4160.7 = 31.7 giá trên biên chính trên, tức **1.8 lần chiều cao cả range chính**.
- **Nghi phạm trong thuật toán:** thiếu luật "cú thăm dò đi xa hơn N lần chiều cao range chính thì range chính đã hỏng, huỷ range" — hiện chỉ có nhánh nới biên phụ, không có nhánh phủ định range.

### 5. SOW đúng nhưng đến quá muộn để cứu bài — luật vi phạm: không, ghi nhận
- SOW tại 19:15, giá 4108.7, **VSA 2.94×, thân 0.82** — đây là một cây phá thật, gắn đúng cây (lỗi B của v4 đã hết ở bài này). LPSY[D] tại 19:18 giá 4112.4 cũng đúng vai: hồi lên retest rồi giá đi tiếp xuống.
- Vấn đề chỉ là nó phá cái **biên phụ dưới 4127.7** vốn được tạo từ một cú lang thang 10 tiếng trước, không phải phá một vùng cân bằng.

### 6. LPSY[C] gán ngược rơi vào giữa range — luật vi phạm: L8
- **Thuật toán gắn:** LPSY[C] tại 18:47, giá **4154.0** — nằm **giữa** biên chính 4143.3–4160.7 (vị trí 62% chiều cao).
- **Đúng phải là:** Phase C là "tín hiệu đầu tiên cho thấy giá ở biên này bắt đầu phá biên kia". Một cái test ở giữa range không phải tín hiệu gì cả. Nếu bắt buộc gán ngược thì phải lấy **đỉnh cuối cùng chạm/gần biên trên** trước cú sụp, tức nhịp quanh 4160 lúc ~18:20 (nhìn ảnh, giá còn chạm đúng đường cam trên trước khi đổ).
- **Dấu hiệu quyết định trên chart:** LPSY[C] 4154.0 thấp hơn biên chính trên 6.7 giá; chấm xanh của nó trên ảnh nằm rõ ở lưng chừng, không chạm đường cam nào.
- **Nghi phạm trong thuật toán:** mục 6 case khó — "nhìn ngược 60 nến, lấy **đỉnh cao nhất**". Lấy cực trị thô trong cửa sổ 60 nến mà không ràng buộc "phải trong dung sai X tick của biên" thì rơi vào giữa range là chuyện đương nhiên khi giá đã trôi xa biên.

## Đạt
- Nhãn SOW neo đúng cây phá thật (VSA 2.94×, thân 0.82), không rơi vào nến xác nhận thứ 3 — lỗi hệ thống B của v4 đã hết ở bài này.
- Phase A kết thúc đúng tại ST[A] (13:15), Phase B bắt đầu ngay sau — đúng L2.
- Phase C (28n) ngắn hơn Phase B rất nhiều, không còn dính trần timeout 121 nến — lỗi C của v4 đã hết.
- Phase E dài 121 nến, không còn bị ép về 1 nến — lỗi J của v4 đã hết.
- Tên "Tái phân phối" khớp L4: origin SC + phá xuống thật = RE-DIST. Đúng bảng.
- Mỗi bên đúng 1 biên phụ, không spam — đúng L3.

## Cần hỏi người học
- Có nên đặt guard **tỉ lệ biên phụ / biên chính** (đề xuất: > 2.0 thì huỷ range) không? Đây là thứ bắt được bài này và nhiều bài cùng kiểu, nhưng là ngưỡng tự đặt, không có trong sách.
