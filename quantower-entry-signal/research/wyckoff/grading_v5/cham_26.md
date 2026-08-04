# Chấm bài #26 — Tái phân phối (RE-DIST) · 2026-06-08 01:30 → 05:59 (269 nến M1)

**Điểm: 6/10** — Khung range vẽ đúng, tên range đúng, nhưng Phase C gán ngược rơi vào giữa range nên toàn bộ ranh giới B/C/D bị đẩy sai chỗ.

## Lỗi (nặng → nhẹ)

### 1. LPSY[C] nằm đúng GIỮA range — Phase C gán ngược sai điểm neo — luật vi phạm: L8 + §5 THEORY (test phải ở biên)
- **Thuật toán gắn:** LPSY[C] tại 4339.0 lúc 05:22, mở Phase C 12 nến.
- **Đúng phải là:** LPSY[C] phải là nhịp bật lên cuối cùng chạm/tiệm cận **biên trên** (4353.4 chính, 4354.8 phụ) trước khi SOW rơi. 4339.0 nằm ở 52% chiều cao range (biên 4323.6–4353.4) — đó là điểm giữa, không phải một cú test biên nào cả.
- **Dấu hiệu quyết định trên chart:** (4339.0 − 4323.6) ÷ 29.8 = **0.52**. Một LPSY đúng nghĩa phải là "đợt phục hồi yếu ở biên" (§4.1 THEORY); nến này VSA 1.29x, thân/biên **0.12** — một cây doji lửng giữa vùng, không mang vai trò test cung ở kháng cự.
- **Nghi phạm trong thuật toán:** mục 6 "case KHÓ" — nhìn ngược 60 nến lấy **đỉnh cao nhất** làm LPSY[C]. Trong 60 nến trước cú phá giá chỉ loanh quanh 4330–4345 nên đỉnh cao nhất của cửa sổ vẫn nằm giữa range. Thiếu ràng buộc "điểm gán ngược phải nằm trong X tick của một biên", nếu không có thì không gán Phase C (chấp nhận range A→B→D).

### 2. mSOS ở 4354.8 lẽ ra là biên phụ trên duy nhất, nhưng nó vượt biên AR chứ không vượt biên climax — nhãn đúng, vai trò bị bỏ qua — luật vi phạm: L3
- **Thuật toán gắn:** mSOS tại 4354.8 (VSA 2.61x) lúc 02:00, chỉ dùng để nới biên phụ trên 4354.8.
- **Đúng phải là:** đây là điểm đọc được nhiều hơn thế — nỗ lực 2.61x mà chỉ đẩy giá qua biên AR đúng **1.4 giá** rồi thất bại. Đó là "nỗ lực lớn, kết quả nhỏ" ngay đầu Phase B, tức tín hiệu sớm rằng phe mua không có hàng — hợp với việc range kết thúc bằng SOW. Thuật toán vẽ đúng nhãn nhưng không dùng nó vào việc gì.
- **Dấu hiệu quyết định trên chart:** biên phụ 4354.8 chỉ hơn biên chính 4353.4 đúng 1.4 giá, trong khi VSA cây đó 2.61x — trên panel volume là thanh vàng.
- **Nghi phạm trong thuật toán:** không có nhánh nào đọc effort↔result (mục 5 chỉ hỏi "có thò ra ngoài biên không"). Đây là lỗi thiếu tính năng, không phải nhãn sai.

### 3. Phase B 211/269 nến nhưng không có một nhãn nào trong suốt 200 nến giữa — luật vi phạm: L9 (trình bày/thiếu nhãn)
- **Thuật toán gắn:** từ mSOS 02:00 tới LPSY[C] 05:22 là 202 nến trống trơn.
- **Đúng phải là:** Phase B là giai đoạn đọc cung/cầu; trên chart nhìn rõ ít nhất 3 nhịp chạm vùng 4345–4350 (khoảng 02:48, 03:54, 04:27) đều không vượt được biên chính — đó là chuỗi UA/test biên trên đáng ghi, và chính chúng cho thấy đỉnh thấp dần (SOT §7 THEORY).
- **Dấu hiệu quyết định trên chart:** ba đỉnh cục bộ giảm dần trong khi biên dưới 4323.6 không bị chạm lần nào — cung đè, cầu không đỡ.
- **Nghi phạm trong thuật toán:** mục 5.0 "UA/UT/DA mỗi bên chỉ giữ MỘT cái duy nhất" — quy tắc này xoá mất chuỗi test, mà chuỗi test mới là thứ đọc được SOT.

## Đạt
- Mục 1 (L1): MOVE giảm 43.3 giá / 62 nến / hiệu suất 0.35, cây SC VSA **3.55x** biên độ 14.9 giá đóng cửa gần đáy — climax thật, chặn đúng đáy move. Mở range hợp lệ.
- Mục 2 (L2): đủ 3 lần đổi hướng, ST[A] 4343.4 quay về đúng phía climax và bị chặn, Phase A kết thúc tại ST[A] (21 nến). Đúng.
- Mục 3 (L3): biên chính = 4323.6 (SC) + 4353.4 (AR), cố định suốt range, không kéo theo giá. Biên phụ trên 4354.8 duy nhất, không có biên phụ dưới — đúng luật "mỗi bên nhiều nhất 1".
- Mục 4 (L4): origin SC + phá xuống thật = **Tái phân phối**. Tên đúng.
- Mục 7 (L10): SOW 4311.2 VSA **7.36x** thân 0.93 đóng cửa dưới cả biên chính lẫn biên phụ; LPSY[D] 4317.6 hồi lên nhưng vẫn giữ dưới biên 4323.6; Phase E 15 nến giá đi tiếp. Đúng khuôn CBR.
- Mục 8: climax 3.55x / SOW 7.36x / LPSY[D] 0.79x — nỗ lực đúng chỗ cần lớn, test đúng chỗ cần co. Đọc volume tốt.
- Mục 9: không có nhãn spam, không có nhãn sai vai (LPSY[C] và LPSY[D] tách đúng trước/sau SOW — không mắc lỗi Ca #3 nguồn 4.pdf).

## Kết luận cấu trúc
Vẽ range ở đây là **đúng**. Nếu là tôi: giữ nguyên biên, giữ nguyên SC/AR/ST[A]/SOW/LPSY[D], **bỏ LPSY[C] ở 4339.0** và dời Phase C về nhịp chạm biên trên cuối cùng quanh 05:00–05:10; hoặc nếu không tìm được nhịp chạm biên nào thì chấp nhận range A→B→D→E không có Phase C, đúng tinh thần "không phải cấu trúc nào cũng có Phase C" (§3.5 THEORY).
