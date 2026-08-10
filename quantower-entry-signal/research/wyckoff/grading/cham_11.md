# Chấm bài #11 — Tích lũy (ACC) · 2026-04-26 23:41 → 2026-04-27 05:49 (146 nến M1)

**Điểm: 2/10** — **Không nên vẽ range ở đây.** Cái được gọi là "SC" là một nến 3 hợp đồng, biên độ 0,6 giá, trong phiên Á chết. Cả cấu trúc là một cú bật chữ V có nghỉ giữa chừng, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. "Climax" không phải climax — nến 0,6 giá / 3 lot — luật vi phạm: THEORY §3.3 (SC), L1
- **Thuật toán gắn:** climax mở range tại 23:41, giá 4724.5, **VSA 1.94x, biên độ nến 0.6 giá**; nhãn SC vẽ ở nến 23:40 (VSA 4.14x, **6 hợp đồng**, biên độ 0.8 giá).
- **Đúng phải là:** SC theo định nghĩa gốc là "**chênh lệch biên độ giá mở rộng + khối lượng tăng mạnh**, áp lực bán lên đỉnh điểm". Ở đây không có cái nào: 6 lot và 0,8 giá. VSA 4.14x chỉ là ảo giác của mẫu số — 6 nến trước đó đều **1 hợp đồng** (xem bảng 12 nến: volume 1,1,1,1,1). Đây đúng là ca giảng viên các vòng trước đã bắt: "climax chỉ 6–19 hợp đồng ở phiên Á giờ chết".
- **Dấu hiệu quyết định:** bảng 12 nến quanh climax — volume `1,1,1,1,1,6,3,1,4,1,2,1`. Toàn bộ cụm climax giao dịch **21 hợp đồng**.
- **Nghi phạm trong thuật toán:** người học đã chốt **không** dùng sàn khối lượng tuyệt đối (quyết định 6, mục 0b). Nhưng ca này cho thấy VSA tương đối vô nghĩa khi mẫu số ≈1. Đề xuất thay thế **không dùng số lot**: yêu cầu biên độ nến climax ≥ k×ATR *và* ≥ một tỷ lệ tối thiểu của **chiều cao range sẽ tạo ra** (0.6 / 34.6 = 1.7% — quá nhỏ để gọi là climax của range đó).

### 2. Sự kiện có ý nghĩa thật nằm ở nhịp TĂNG, không phải ở "SC" — luật vi phạm: L1 (climax phải chặn move)
- **Thuật toán gắn:** cả cụm volume lớn nhất chart (các thanh vàng cao vọt quanh 00:50–01:04) rơi vào **nhịp AR**, không phải nhịp climax.
- **Đúng phải là:** cây có nỗ lực thật là cây đẩy giá từ 4731 lên 4759 trong ~10 nến. Nếu muốn đọc cấu trúc ở đây thì phải neo vào cú bùng nổ đó, không neo vào cái đáy lặng lẽ trước nó.
- **Dấu hiệu quyết định:** panel volume — cụm 3 thanh vàng cao nhất toàn ảnh nằm đúng dưới nhịp nến xanh dựng đứng lúc 00:57, còn tại SC (23:40–23:41) panel gần như phẳng.

### 3. THIẾU Phase C — luật vi phạm: L8
- **Thuật toán gắn:** A → B → **D** → E, không có Phase C.
- **Đúng phải là:** phải gán ngược từ SOS (02:47). Cửa sổ hiện tại min(60, 0.8×44) = 35 nến — vẫn không tìm ra pivot hợp lệ "trong range + đúng nửa dưới". Lỗi lặp lại y hệt bài #09; bản vá #3 (0.5x→0.8x) không giải quyết.
- **Nghi phạm trong thuật toán:** ràng buộc kép "trong range **và** đúng nửa range" (vá v6 số 5) đang quá chặt — ở đây nhịp test cuối trước SOS nằm quanh 4753–4757, tức **nửa trên** range 4724.5–4759.1, nên bị loại. Nhưng với tích luỹ dốc lên (THEORY §3.4) LPS[C] nằm nửa trên là **bình thường**, thậm chí là dấu hiệu mạnh.

### 4. Phase B (44 nến) ngắn hơn Phase A (46 nến) — luật vi phạm: L9
Phase A chiếm 46/146 nến vì AR mất tới 83 phút mới thành hình. Với một range 146 nến thì B phải áp đảo, không phải chia đều.

### 5. ST[A] ở giữa range, VSA 0.29x — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 01:16, giá 4741.7.
- **Đúng phải là:** 4741.7 cách climax 4724.5 tới **17.2 giá = 50% chiều cao range** — chính giữa range, không test được vùng climax. Cùng lỗi với bài #08 và #09: ngưỡng hồi 0.4× (ở đây đạt 0.50) không thay được ràng buộc khoảng cách tới climax.

### 6. Không có LPS[D] trong Phase D 25 nến
Theo L10, Phase D là "phá biên → hồi retest **giữ được** ngoài biên". Ở đây chỉ có mỗi nhãn SOS. Nhìn ảnh thì giá sau SOS đi thẳng lên 4780 không hồi — đây là ca hợp lệ theo Ca #21 nguồn 7.pdf (Phase D không bắt buộc có BU), nên **không tính là lỗi cấu trúc**, chỉ ghi nhận Phase D trống nhãn suốt 25 nến.

## Đạt
- **Mục 3 (L3):** biên chính 4724.5–4759.1 = climax + AR, cố định; biên phụ 4760.1 đúng cực trị xa nhất, tỷ lệ 1.03x. Sạch, không có ca "biên phụ tự nới rồi tự vượt".
- **Mục 4 (L4):** climax từ move giảm + phá thật lên ⇒ **Tích luỹ**. Tên khớp bảng 4 pattern (với điều kiện chấp nhận cái climax kia là climax).
- **Mục 7 (L10) một phần:** SOS 02:47 (VSA 2.33x, thân 1.00) đóng cửa vượt cả biên chính lẫn biên phụ trên — cú phá thật, đúng yêu cầu L3. Phase E 32 nến, giá đi tiếp lên 4780.
- **Chú thích nỗ lực/kết quả đúng dấu** (er=0.09 → "HIỆU QUẢ").

## Cần hỏi người học
- Ở phiên Á thanh khoản ~1 hợp đồng/nến, VSA tương đối mất ý nghĩa nhưng anh đã chốt không dùng sàn lot tuyệt đối. Chấp nhận thay bằng ràng buộc **hình học** (biên độ nến climax ≥ x% chiều cao range mà nó tạo ra) chứ?
