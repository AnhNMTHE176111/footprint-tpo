# Chấm bài #49 — Chưa rõ (SC) / ACC? · 2026-07-09 00:54 → 04:10 (196 nến M1)

**Điểm: 2/10** — cấu trúc có thật nhưng vẽ sai gần hết: biên chính nằm giữa vùng giá, và nhãn SOW rơi vào nhịp hồi *sau* cú sụp thật 45 nến.

## Lỗi (nặng → nhẹ)

### 1. SOW đặt sai chỗ hoàn toàn — luật vi phạm: L10 + §6.5 THEORY (nhãn phá vỡ phải neo vào cây phá thật)
- **Thuật toán gắn:** SOW tại 03:45, giá 4070.8, **VSA 0.89x**, thân 0.38. Phase D bắt đầu 03:45.
- **Đúng phải là:** cú sụp thật xảy ra 02:55 → 03:10 (từ ~4088 xuống ~4062, xuyên thẳng qua cả biên chính dưới 4079.2 lẫn biên phụ dưới 4071.4, panel volume có chuỗi thanh vàng liên tiếp ở đúng đoạn này). SOW phải neo vào cây mạnh nhất trong đoạn đó, và Phase D phải bắt đầu ở đấy chứ không phải 35 nến sau.
- **Dấu hiệu quyết định trên chart:** nến mang nhãn SOW có VSA 0.89x — **dưới trung bình**; nó là nến trong nhịp hồi từ 4062 lên 4072, tức đang đi NGƯỢC hướng SOW. Giá đã đóng cửa dưới 4071.4 liên tục từ ~02:55.
- **Nghi phạm trong thuật toán:** nhánh quét hồi tố "cây VSA cao nhất, đúng hướng, đóng cửa vượt biên" (mục 5.1) — cửa sổ quét bắt đầu quá muộn, hoặc đoạn sụp bị nuốt vào state Phase C nên không được đưa vào cửa sổ quét.

### 2. Cú sụp thật bị xếp vào Phase C, Phase C phình 58 nến — luật vi phạm: L8 (Phase C ngắn nhất)
- **Thuật toán gắn:** Phase C = 02:47 → 03:44 = **58 nến**, dài hơn cả Phase D (26 nến), và chứa trọn cú sụp 26 giá.
- **Đúng phải là:** Phase C chỉ là LPSY[C] tại 02:47 + vài nến; từ nến phá xuống là Phase D.
- **Dấu hiệu quyết định:** trong đoạn "Phase C" giá đi 4080.8 → 4062 = hơn **2× chiều cao biên chính (9.0 giá)**. Một đoạn đi xa gấp đôi cả range không thể là "phase ngắn nhất".
- **Nghi phạm:** trần `len(C) ≤ min(len(B), len(D))` vẫn chưa được cài (đã ghi ở mục 13.1b là việc cần làm, chưa làm).

### 3. Cây volume mạnh nhất range bị gán nhãn *minor* — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** mSOW tại 01:54, giá 4077.7, **VSA 6.41x** (cây volume cao nhất toàn range, thanh vàng cao nhất panel dưới ngoài cụm climax).
- **Đúng phải là:** cú này chỉ thò 1.5 giá dưới biên chính rồi quay lại — nhãn *minor* về mặt kết cục là đúng, nhưng chuyện range có **một cây 6.41x đẩy giá được đúng 1.5 giá** chính là nỗ lực lớn/kết quả nhỏ = dấu hiệu hấp thụ, và thuật toán bỏ qua hoàn toàn: chỉ số "nhịp nỗ lực/kết quả cao nhất" lại chỉ ra nến 02:55 với er=0.94 và ghi "nhịp HIỆU QUẢ".
- **Nghi phạm:** chỉ số er tính theo *nhịp giữa hai pivot*, không quét theo *từng nến* nên bỏ sót cây đơn lẻ effort-cao/result-thấp.

### 4. Biên chính nằm giữa vùng giá — luật vi phạm: L3 + L1
- **Thuật toán gắn:** biên chính 4079.2 – 4088.2 = **9.0 giá**; biên phụ 4071.4 – 4091.9 = 20.5 giá (2.28×).
- **Đúng phải là:** vùng đấu giá thật trên ảnh là ~4071 – 4092. Hai nét liền cắt ngang giữa thân vùng, phần lớn nến Phase B nằm ngoài chúng.
- **Dấu hiệu quyết định:** ST[A] (4076.1) đã nằm **thấp hơn chính mức climax 3.1 giá** ngay trong Phase A — tức cây climax không chặn nổi move, và biên dưới đã sai từ nến thứ 13 của range.
- **Nghi phạm:** guard "climax không chặn được move" (4× biên độ TB) tắt sau Phase A; và trần ST[A] ≤ 1.0× chiều cao range quá rộng khi range chỉ cao 9.0 giá.

### 5. Nhãn SC lệch khỏi nến mở range — luật vi phạm: L3 (mốc climax)
- **Thuật toán gắn:** range mở tại 00:54 (đáy 4079.2, VSA 2.69x) nhưng nhãn SC đặt tại **01:00**, giá 4080.6, VSA 4.72x.
- **Đúng phải là:** nhãn và mốc biên phải cùng chỉ về một cây. Đây là lỗi cụm climax đã biết, chưa sửa — ghi nhận, không tính nặng.

### 6. Range không được đặt tên dù đã phá rõ — luật vi phạm: L4
- Range đóng ở trạng thái `superseded`, tiêu đề "Chưa rõ (SC)". Nhưng giá đã đóng cửa hẳn dưới cả hai biên và đi tiếp xuống 4062 — origin SC + phá xuống = **Tái phân phối**. Cơ chế SIDEWAYS đang cướp tên của một cấu trúc đã hoàn tất.

## Đạt
- Điều kiện mở range (L1): có MOVE giảm thật 17.4 giá / 39 nến, hiệu suất 0.37, cây climax 2.69x là đáy cửa sổ — hợp lệ (dù hiệu suất sát sàn 0.35).
- Phase A đủ 3 lần đổi hướng và kết thúc đúng tại ST[A] (L2).
- LPSY[C] tại 02:47 (4080.8) đặt đúng chỗ: nhịp test cuối ngay biên chính dưới trước khi sụp.
- Phase B là phase dài nhất (99 nến) — thoả L9.
