# Chấm bài #49 — Chưa rõ (SC) (ACC?) · 2026-07-16 13:05 → 2026-07-17 20:59 (1853 nến M1)

**Điểm: 3/10** — Range là THẬT và Phase A vẽ đúng, nhưng bài bỏ sót nguyên một Shakeout + SOS ở cuối và để Phase B chạy 1819 nến. Cần sửa: 3963.0 là **Shakeout (Phase C)**, 4028.9 là **SOS (Phase D)** — đây là một cấu trúc **Tích luỹ hoàn chỉnh**, không phải "chưa rõ".

## Lỗi (nặng → nhẹ)

### 1. Cú rũ ở 3963.0 bị hạ thành mSOW — luật vi phạm: L5, L8, THEORY §5 (mục tiêu tối thiểu của cú rũ)
- **Thuật toán gắn:** mSOW tại 2026-07-17 13:01, giá 3963.0 (VSA 1.79x) — nhãn "phá thất bại", ở lại Phase B.
- **Đúng phải là:** **Shakeout** = Phase C. Cú này phá biên chính dưới 3977.1 xuống 3963.0, lùng bùng ngoài range khoảng 25 nến (13:01 → ~13:30) rồi rút hẳn vào trong — theo L5 quá 4 nến là Shakeout, không phải Spring, và **không phải** mSOW.
- **Dấu hiệu quyết định trên chart:** sau khi rút vào, giá đi một mạch từ 3963 lên 4028.9 = **185% chiều cao biên chính** (35.5 giá). THEORY §5 nói mục tiêu tối thiểu của cú rũ là "đến được đầu đối diện của cấu trúc" — ở đây nó tới đầu đối diện rồi vượt luôn. Đó là cú rũ **XÁC NHẬN**, không có cách nào gọi là thất bại. Panel volume: cụm cột vàng dày nhất cả range nằm đúng ở 13:01–13:30.
- **Nghi phạm trong thuật toán:** cú này thoả "vượt biên phụ" (biên phụ dưới lúc đó là 3973.4, cú xuống 3963.0 vượt được) và thoả "mạnh". Nghi nhánh phân loại rơi vào ô "mạnh nhưng không đủ tư cách rũ → mSOW" do guard **"mỗi range chỉ MỘT cú rũ"** đã bị mSOW 16/07 19:38 chiếm chỗ, hoặc do so sánh độ sâu dùng nhãn đã gán thay vì mức giá. Đây là lỗi hệ thống nghiêm trọng nhất trong lô.

### 2. Cú phá lên 4028.9 bị hạ thành mSOS, mất Phase D/E — luật vi phạm: L5, L10, L3
- **Thuật toán gắn:** mSOS tại 17/07 16:24, giá 4028.9 (VSA 2.41x, thân **0.90**), ở lại Phase B; range đóng "chưa rõ hướng".
- **Đúng phải là:** **SOS**. Giá đóng cửa vượt biên chính trên 4012.6 rồi **giữ ở ngoài hơn 5 giờ** (15:30 → 20:59), tạo biên phụ trên 4028.9. L5 nói rõ: "đóng cửa hẳn ngoài biên và các nến sau đủ mạnh giữ nó ở ngoài → đó là phá THẬT". Nhịp lùi về 4008–4012 lúc 18:55 rồi bật lại lên 4023 chính là **LPS[D]** (retest giữ được ngoài/tại biên).
- **Dấu hiệu quyết định trên chart:** từ 15:30 tới hết dữ liệu, gần như toàn bộ nến nằm **trên** đường cam 4012.6; nến thân 0.90 tại 16:24 là cây bứt dứt khoát.
- **Nghi phạm trong thuật toán:** điều kiện phá thật đòi "3 nến đóng cửa vượt **biên phụ** thêm ≥30 tick" — biên phụ trên 4028.9 do chính cú phá này tạo, nên tự khoá. Cùng vòng khoá logic với bài #48 lỗi 3.

### 3. Phase B dài 1819 nến, không có C/D/E — luật vi phạm: L9 (đúng nhưng bệnh lý) + L8
- **Thuật toán gắn:** A 35 nến → B 1819 nến, hết.
- **Đúng phải là:** với Shakeout ở 13:01 và SOS ở 16:24 ngày 17/07, Phase B phải kết thúc quanh 17/07 13:00 (≈1400 nến), rồi C ≈ 25–30 nến, D ≈ 25 nến, E phần còn lại. Một Phase B chiếm **98%** range là dấu hiệu máy không tìm được sự kiện nào, chứ không phải "Phase B dài nhất" theo nghĩa L9.
- **Nghi phạm trong thuật toán:** hệ quả trực tiếp của lỗi 1 và 2. Ngoài ra nhánh gán ngược Phase C không thể chạy vì không có SOS/SOW nào được xác nhận.

### 4. Nhãn mSOW dư — luật vi phạm: L3 ("biên phụ cũ biến mất, chỉ giữ cái xa nhất")
- **Thuật toán gắn:** hai nhãn mSOW cùng tồn tại: 16/07 19:38 @ 3973.4 và 17/07 13:01 @ 3963.0.
- **Đúng phải là:** theo đúng quy tắc biên phụ mà spec đã tự viết ("nhãn UA/UT/DA mỗi bên chỉ giữ một cái duy nhất, cú mới nông hơn thì không ghi gì"), cú 3963.0 sâu hơn phải **xoá** nhãn 3973.4. Trên chart hiện còn cả hai.
- **Nghi phạm trong thuật toán:** quy tắc "chỉ giữ 1" được áp cho UA/UT/DA nhưng không áp cho mSOS/mSOW.

### 5. Chỉ số SOT báo none(n=0) trên Phase B 1819 nến — lỗi đo
- **Thuật toán in:** SOT-up `none` n=0, SOT-dn `none` n=0; và **không in** dòng "nhịp nỗ lực/kết quả cao nhất" (bài #45–#48 đều có).
- **Đúng phải là:** trên 30 giờ dữ liệu với hàng chục nhịp lên/xuống rõ ràng (đọc trên ảnh: đáy 3973 → 3974 → 3963, đỉnh 4012 → 4008 → 4028…) không thể không tìm được nhịp nào. Chỉ số đang không chạy trên range dài.
- **Nghi phạm trong thuật toán:** bộ dò nhịp có trần số nến hoặc trần số pivot, hoặc bị chia mảng theo cửa sổ nhỏ rồi trả về rỗng khi Phase B vượt kích thước. Dòng effort/result mất hẳn củng cố giả thuyết "hàm bail-out khi Phase B quá dài".

### 6. (nhẹ, cấu trúc) Range đóng vì khe cuối tuần chứ vì cấu trúc
Trục thời gian nhảy từ 17/07 20:59 sang 19/07 22:40 → range bị cắt bởi guard khe > 4 giờ (lỗi K, cơ chế đúng). Ghi nhận để không tính là lỗi, nhưng kết quả là range bị đóng ở trạng thái "chưa rõ" trong khi cấu trúc đã hoàn tất trước khi cắt.

## Đạt
- **Mục 1 (mở range):** MOVE giảm 67.7 giá / 61 nến / hiệu suất 0.45 — trên ảnh là cú rơi thẳng 4045 → 3977 rất rõ, cây SC 13:04 (VSA 2.34x, thân 0.69) chặn đúng đáy. Điều kiện CẦN của L1 thoả sạch. Đây là ca mở range đúng nhất trong lô.
- **Mục 2 (Phase A):** đủ 3 lần đổi hướng — SC 3977.1 → AR 4012.6 (bật 35.5 giá, cú bật thật) → ST[A] 3985.5 (cách mức climax 8.4 giá = 24% chiều cao, tức nằm trong 1/3 phía climax, đúng vai test). Phase A dài 35 nến và **kết thúc đúng tại ST[A]**. Đúng L2.
- **Mục 3 (biên chính):** 3977.1–4012.6 = climax + AR, cố định suốt 1853 nến, không bị kéo theo giá. Đúng L3.
- **Mục 3 (biên phụ):** 3963.0 dưới và 4028.9 trên — mỗi bên đúng 1 cái và đúng là cực trị xa nhất. Đúng L3.
- **Chỉ số bias = +0** (test cả hai biên) — khớp đúng hình: giá chạm cả hai biên nhiều lần suốt 30 giờ.
- **Trung thực:** đóng range ở trạng thái "chưa rõ (SC) (ACC?)" thay vì ép đặt tên — thái độ đúng, chỉ tiếc là nguyên nhân "chưa rõ" đến từ hai lỗi phân loại ở trên chứ không phải vì chart thật sự mơ hồ.

## Cần hỏi người học
- Điều kiện "SOS/SOW phải đóng cửa bứt qua **biên phụ**" (L3) đang tạo vòng khoá: chính cú phá sinh ra biên phụ rồi bị đòi vượt biên phụ đó. Có phải ý người học là "vượt biên phụ **đã tồn tại trước** cú phá đang xét"? Nếu đúng thì cả bài #48 và #49 đều đổi kết luận, và đây là bản vá đơn lẻ có tác động lớn nhất cho vòng v7.
