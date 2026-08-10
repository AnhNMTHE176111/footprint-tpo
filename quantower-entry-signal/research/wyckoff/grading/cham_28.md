# Chấm bài #28 — Tái phân phối (RE-DIST) · 2026-06-03 05:31 → 09:13 (222 nến M1)

**Điểm: 5/10** — Phase B phình 176 nến vì ôm trọn cả một đoạn giá đã sống hẳn ngoài biên; SOW thật bị bỏ lỡ, SOW được gán là cú thứ hai.

## Lỗi (nặng → nhẹ)

### 1. ~50 nến đóng cửa dưới biên chính vẫn bị tính là Phase B — luật vi phạm: L5, L9, L10
- **Thuật toán gắn:** Phase B kéo từ 05:46 đến **08:41** (176 nến), trong đó có nhãn `mSOW` 08:24 tại 4478.8. SOW chỉ được công nhận ở 08:51 (4472.0, VSA 9.63x).
- **Đúng phải là:** SOW thật xảy ra quanh **07:45**, khi giá đóng cửa hẳn dưới 4486.9 và các nến sau đủ mạnh giữ nó ở ngoài. Phase B phải kết thúc ở đó; đoạn 07:45→08:35 là Phase D (giá thuận lực đi xuống), cú hồi 08:42 chạm lại 4487 là **LPSY[D]**, rồi Phase E.
- **Dấu hiệu quyết định trên chart:** biên chính dưới 4486.9. Từ khoảng 07:45 đến 08:35 **không một nến nào** đóng cửa trở lại trên đường đó — giá lê từ 4486 xuống 4478.8 rồi mới hồi. L5 nói rõ: "đóng cửa hẳn ngoài biên và các nến sau đủ mạnh giữ nó ở ngoài → đó là phá THẬT". 50 nến ngoài biên không thể là một cú test trong Phase B. Điểm thấp nhất của đoạn này (4478.8) còn được chính thuật toán lấy làm **biên phụ dưới** — tức nó thừa nhận đó là một nỗ lực phá đáng kể, nhưng vẫn không nâng cấp thành SOW.
- **Nghi phạm trong thuật toán:** đây đúng là ca "hàng chục nến ngoài biên không công nhận" mà v7.1 định chữa. Bản vá mới chỉ đổi mốc so sánh (biên chính + 30 tick) chứ **chưa thêm luật timed-out theo số nến**: cần luật "nếu ≥N nến liên tiếp đóng cửa ngoài biên chính (N ≈ 10-15) thì chốt SOW/SOS tại nến đầu tiên của chuỗi", chạy song song với luật ngưỡng giá.

### 2. LPSY[D] hồi trở lại vào TRONG range — luật vi phạm: L10
- **Thuật toán gắn:** LPSY[D] 09:08 tại 4487.5.
- **Đúng phải là:** LPSY[D] phải **giữ được ở ngoài biên**. 4487.5 nằm **trên** biên chính dưới 4486.9 → cú hồi đã ăn trọn vào lại range, không còn là retest giữ vùng.
- **Dấu hiệu quyết định trên chart:** marker LPSY[D] nằm đúng trên đường liền cam 4486.9, cùng mức với LPSY[C] (4487.2) — hai nhãn khác vai mà cùng một giá, dấu hiệu tiêu chí phân biệt đang trống.
- **Nghi phạm:** điều kiện chọn LPSY[D] chỉ kiểm "là đỉnh cục bộ sau SOW", chưa kiểm "đóng cửa vẫn ngoài biên".

### 3. Phase E chỉ 1 nến — luật vi phạm: L10
- **Thuật toán gắn:** E = 09:13 → 09:13, đúng 1 nến, rồi range đóng `completed`.
- **Đúng phải là:** Phase E là giai đoạn giá rời range đi tìm vùng giá mới — 1 nến thì chưa có Phase E. Trên chart giá tiếp tục xuống 4466 sau 09:13, nghĩa là Phase E có thật nhưng range bị cắt cụt trước khi nó thành hình.
- **Nghi phạm:** điều kiện đóng range (hết cửa sổ tối đa / range mới sinh) chạy trước điều kiện phát triển Phase E. Nếu E < ~5 nến thì nên gộp vào D thay vì in ra một phase 1 nến.

### 4. Nhãn SC nằm trước nến mở range (lỗi đã biết, chưa sửa)
- SC ghi 05:30 giá 4488.6, VSA **11.08x**; nến mở range là 05:31 (low 4486.9, VSA chỉ 2.09x). Bài này lỗi đó gây hậu quả thấy rõ: tiêu đề chart ghi `VSA_nhan=11.08x` nhưng cây thực sự mở range chỉ 2.09x — người đọc bị dẫn sai về cường độ climax. Ghi nhận theo yêu cầu, không tính điểm.

### 5. MOVE trước climax hiệu suất thấp (trình bày/cảnh báo)
- 22.2 giá trong **76 nến**, hiệu suất hướng **0.37** — move lê thê nhiều nhịp hồi, không phải một cú đẩy dứt khoát bị chặn. Đây là ca biên của L1: chưa đến mức bác range, nhưng nên hiện cảnh báo như bài #30 đã làm.

## Đạt
- **Mục 2 (L2):** đủ 3 lần đổi hướng, và ST[A] 05:45 tại 4489.3 hồi **76%** khoảng AR↔climax — vượt ngưỡng 55% mới, không còn rơi lửng giữa range. Phase A gọn 15 nến, kết đúng tại ST[A].
- **Mục 3 (L3) — biên phụ dưới:** 4478.8 = cực trị xa nhất, mỗi bên 1 biên, không kéo theo giá. Đúng luật (dù nó lẽ ra phải kích hoạt SOW, xem lỗi #1).
- **Mục 4 (L4):** move giảm + SC + phá xuống = Tái phân phối. Tên đúng.
- **Mục 6 (L8):** Phase C 9 nến — ngắn nhất, đúng L8.
- **Mục 8:** SOW 08:51 VSA 9.63x, thân/biên 0.80 — nỗ lực và kết quả khớp nhau, đọc đúng. Chỉ số nỗ lực/kết quả Phase B (er=1.24, "hấp thụ nghi vấn") cũng đúng chiều với một cấu trúc sắp gãy xuống.
- **Mục 9:** không lẫn vai LPSY[C]/LPSY[D] về mặt tên gọi, không có nhãn spam.
