# Chấm bài #19 — Tái phân phối (RE-DIST) · 2026-05-26 00:19 → 10:04 (575 nến M1)

**Điểm: 3/10** — Cấu trúc range thì đọc được, nhưng **tên range sai**: cú SOW hỏng ngay tại chỗ, giá bật lên 4570+ chứ không phân phối tiếp. Phải hạ SOW thành mSOW và để range ở trạng thái "chưa rõ".

## Lỗi (nặng → nhẹ)

### 1. Đặt tên RE-DIST trong khi cú phá xuống thất bại tức thì — luật vi phạm: L4 + L10, lỗi hệ thống F chưa hết
- **Thuật toán gắn:** SOW 09:39 tại 4549.5 → LPSY[D] 09:59 tại 4556.5 → Phase E 10:04 (**dài 1 nến**) → range đóng, đặt tên **Tái phân phối**.
- **Đúng phải là:** đọc chuỗi số cho thấy cú phá chết yểu. SOW ở 4549.5, rồi 20 nến sau giá đã ở **4556.5** — tức hồi lên 7 giá, cao hơn cả **biên phụ dưới 4553.4**, tức **vào lại trong range**. Nhìn chart, ngay sau vạch Phase E giá dựng đứng lên 4567–4572 và ở đó. Không có phân phối nào tiếp diễn. Theo L10 (Phase D/E = phá biên rồi **giữ được** ngoài biên) thì cú này không đủ tư cách. Đúng phải là **mSOW**, trả dải phase về B, **không đặt tên range** — để "Chưa rõ (SC)".
- **Dấu hiệu quyết định trên chart:** LPSY[D] 4556.5 > biên phụ dưới 4553.4 (đọc từ phiếu). Trên ảnh, chấm LPSY[D] tím nằm **trên** đường cam nét đứt; và 30 nến cuối chart là một nhịp tăng liền mạch lên gần 4572.
- **Nghi phạm trong thuật toán:** hai chỗ. (a) Mục 7 Câu 1 chỉ huỷ cú phá khi nến **đóng cửa lùi hẳn vào trong range quá 30 tick** — nhưng "trong range" ở đây được đo theo **biên chính** (4574.6), mà giá hồi lên 4556.5 vẫn còn cách biên chính 18 giá nên không bị bắt, dù nó đã vào lại trong **biên phụ**. Câu 1 phải đo theo đúng cái biên mà SOW đã phá, tức biên phụ. (b) Mục 7 cho chốt Phase E khi "hết 25 nến mà mới đi được ≥50% chiều cao range" — chiều cao biên chính chỉ 11.4 giá nên mốc 50% là 5.7 giá, cú phá đi được ~5 giá là đủ đậu. Ngưỡng quá dễ.

### 2. Phase E dài đúng 1 nến — luật vi phạm: L10, lỗi hệ thống J chưa hết
- **Thuật toán gắn:** Phase E = 10:04 → 10:04 = **1 nến**.
- **Đúng phải là:** Phase E theo L10 là "giá thuận lực đi tiếp để tìm vùng giá mới" — không thể là một nến. Vá lỗi J ở v5 hứa "Phase E kéo tới khi giá lùi vào trong biên / đi xa 2× chiều cao / hết 120 nến", nhưng ở đây nó lại về đúng 1 nến như bản v4. Lý do thật: giá **lùi vào trong biên ngay lập tức** nên điều kiện dừng bắn ở nến đầu tiên. Tức con số "1 nến" chính là bằng chứng số học cho lỗi #1 — máy đã tự đo được rằng cú phá hỏng, nhưng vẫn đặt tên range.
- **Dấu hiệu quyết định trên chart:** vạch Phase D và Phase E gần như trùng nhau ở mép phải khung range.
- **Nghi phạm trong thuật toán:** Phase E chốt ở 1 nến vì lùi-vào-biên là tín hiệu **hỏng**, nhưng code lại xử lý nó như tín hiệu **kết thúc bình thường**. Cần phân biệt hai lối ra của Phase E: "đi đủ xa" (thành công → đặt tên) vs "lùi vào biên" (thất bại → không đặt tên).

### 3. Climax VSA 1.54x, thấp hơn cả nến trước nó (3.50x) và nến sau nó (3.00x) — luật vi phạm: L1, lỗi hệ thống A
- **Thuật toán gắn:** SC tại 00:19, giá 4574.6, VSA **1.54x**, biên độ 4.4 giá.
- **Đúng phải là:** nến **-1 (00:18)** volume 49, **VSA 3.50x**, biên độ 7.0 giá (4582.4→4575.4), thân 0.94 — đó là cây bán tháo thật. Nến được chọn (00:19) chỉ có volume 23 và là một cây **tăng** (open 4575.0, close 4579.0, thân 0.91 xanh). Gọi một cây xanh là Selling Climax thì đã ngược mục 3(3) của chính tài liệu thuật toán ("nến **đỏ** chặn move giảm → SC").
- **Dấu hiệu quyết định trên chart:** phiếu ghi O=4575.0 < C=4579.0 tại nến climax → nến xanh. Volume 23 so với 49 của nến trước.
- **Nghi phạm trong thuật toán:** cụm climax (mục 4.0) dời mốc sang nến 00:19 vì nó tạo **low mới** (4574.6 < 4575.4) — chỉ thấp hơn 0.8 giá. Việc dời mốc kéo theo cả nhãn SC và làm mất luôn điều kiện "màu nến khớp hướng move" đã kiểm ở nến gốc. Cần: khi dời mốc trong cụm, **giữ nến gốc làm nến climax** (nhãn, VSA, màu) và chỉ dùng cực trị mới để đặt **mức biên**.

### 4. mSOW ở 08:34 với VSA 0.67x thân 0.52 — không "mạnh" theo bất kỳ nghĩa nào — luật vi phạm: mục 8, lỗi hệ thống H
- **Thuật toán gắn:** mSOW 08:34 tại 4553.4, VSA **0.67x**.
- **Đúng phải là:** mSOW = cú phá **mạnh** nhưng thất bại. VSA 0.67x là dưới trung bình. Cú thọc này sâu 21.2 giá dưới biên chính (4574.6 → 4553.4) nên đậu bằng nhánh "sâu", nhưng nó là một nhịp trôi chậm nhiều nến chứ không phải một cú đánh. Đúng hơn thì đây là **DA** (test nhẹ biên dưới), hoặc chính nó mới là cú Shakeout đáng xét vì đã ở ngoài biên rất lâu (từ ~04:30 đến 09:39 giá liên tục dưới 4574.6).
- **Dấu hiệu quyết định trên chart:** cả nửa phải chart (04:30–09:40) nằm **dưới** biên chính dưới 4574.6 — hơn 300 nến ngoài biên. Việc đó bị gói thành đúng một nhãn "mSOW".
- **Nghi phạm trong thuật toán:** giống lỗi #3 bài #16 — điều kiện "mạnh" dùng **HOẶC** giữa độ sâu và VSA, nên nhánh độ sâu tự bơi. Thêm nữa: 300+ nến ngoài biên chính mà không kích hoạt Kết cục B (phá thật) là vì Kết cục B đo theo **biên phụ**, mà biên phụ bị chính cú này nới ra — vòng lặp tự chặn.

### 5. Phase B ăn cả vùng giá đã rời range — luật vi phạm: L9, L10
- **Thuật toán gắn:** Phase B = 518 nến (00:41 → 09:26), chiếm 90% range.
- **Đúng phải là:** B là phase dài nhất thì đúng luật, nhưng phần lớn 518 nến đó giá đang ở **ngoài biên chính dưới**. Một phase B hợp lệ là giai đoạn đấu giá **trong** range. Sau khi sửa lỗi #4, đoạn từ ~04:30 phải là D/E của một cấu trúc khác (hoặc range mới), không phải B.
- **Dấu hiệu quyết định trên chart:** đường cam nét liền dưới (4574.6) nằm cao hơn toàn bộ phần chart từ 04:00 trở đi.

### 6. LPSY[C] VSA 0.47x thân 0.31 — nhãn không có nội dung khối lượng (mục 8). Nhỏ, ghi để đủ.

## Đạt
- **Mục 1 (một phần):** có MOVE giảm thật trước climax — 25.7 giá / 59 nến / hiệu suất 0.47, nhìn chart là đợt giảm rõ từ 4617 xuống 4575. Điều kiện CẦN của L1 thoả.
- **Mục 2 — Phase A đủ 3 lần đổi hướng:** SC 4574.6 → AR 4586.0 → ST[A] 4576.7, kết đúng tại ST[A], 20 nến. ST[A] test lại sát vùng climax (cách 2.1 giá) — đây là ST[A] **đẹp** nhất trong 5 bài lô này. Đúng L2.
- **Mục 3 — biên chính cố định:** = climax + AR, không bị kéo. Biên phụ đúng 1 cái phía dưới; phía trên không có biên phụ (đúng, giá chưa vượt AR) — thể hiện đúng L3 "có thể có 2, có 1, hoặc không có".
- **Mục 6 — Phase C ngắn nhất (12 nến):** đúng L8, gán ngược từ SOW hợp lý.
- **Mục 9:** không có ST[B], LPSY[C] và LPSY[D] mỗi cái một điểm, phân vai trước/sau SOW đúng — không mắc lỗi Ca #3 nguồn 4.pdf.
