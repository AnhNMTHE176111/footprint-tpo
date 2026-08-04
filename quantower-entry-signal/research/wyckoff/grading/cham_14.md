# Chấm bài #14 — Tích luỹ (ACC) · 2026-05-12 13:16 → 2026-05-13 01:56 (422 nến M1)

**Điểm: 5/10** — Bài tốt nhất trong lô: climax thật (VSA 6.34x), Phase A đúng khuôn, tên range đúng, cú phá lên là thật. Nhưng biên chính dưới vẫn bị giá thủng 41.7 giá và cụm nhãn Phase C/D bị nén.

## Lỗi (nặng → nhẹ)

### 1. Giá thủng 41.7 giá dưới biên chính dưới rồi mới quay lại — climax không chặn được move — luật vi phạm: L1 + mục 4.0 tài liệu thuật toán
- **Thuật toán gắn:** biên chính dưới = 4722.5 (mức SC), giữ cố định; biên phụ dưới = **4680.8**.
- **Đúng phải là:** 4722.5 − 4680.8 = **41.7 giá**, gấp **1.9 lần** chiều cao biên chính (21.9 giá). Nhìn ảnh, cú sụp lúc 05-12 15:23 đâm thẳng xuống 4680.8 rồi bật lên — đó mới là **Spring/Shakeout** thật của cấu trúc này, và đáy thật của range là 4680.8. Máy đã ghi nó nhưng chỉ gọi là "mSOW" ở 4710.8 (16:54), tức **bỏ sót hẳn cú rũ ở 4680.8**.
- **Dấu hiệu quyết định trên chart:** cây đỏ dài nhất toàn chart nằm ở 05-12 15:23, chạm đúng đường đứt 4680.8, kèm cột volume cao nhất panel dưới. Sau đó giá bò lên liên tục 4681 → 4753 — đúng khuôn "Spring → SOS".
- **Nghi phạm trong thuật toán:** mSOW được ghi ở 16:54 (4710.8) chứ không phải ở 15:23 (4680.8) — tức máy **bỏ qua** đáy sâu nhất. Nghi ngờ: nến 15:23 không đóng cửa quay lại trong range trong cùng nhịp nên rơi vào nhánh "đang theo dõi cú phá", rồi cú phá đó bị timeout mà không ghi nhãn tại cực trị. Đây là biến thể lỗi G chưa vá hết.

### 2. Cú rũ thật ở 4680.8 bị bỏ, Phase C phải gán ngược → LPS[C] rơi ra ngoài biên trên — luật vi phạm: L8 + L5
- **Thuật toán gắn:** LPS[C] 19:40 tại **4750.2**, VSA 0.54x, thân 0.00 — nằm **cao hơn biên chính trên 4744.4** 5.8 giá.
- **Đúng phải là:** nếu đã nhận cú rũ ở 4680.8 làm Shakeout (giá lùng bùng ngoài lâu, không quay lại trong 4 nến → theo L5 là **Shakeout**, không phải Spring), thì Phase C là case DỄ, đánh dấu ngay tại 15:23. Không cần gán ngược, và không có chuyện LPS[C] nằm ngoài biên.
- **Dấu hiệu quyết định trên chart:** Phase C chỉ dài **5 nến** và nằm sát Phase D — cả cụm C/D/E chen chúc trong 3 vạch tím.
- **Nghi phạm trong thuật toán:** hệ quả dây chuyền của lỗi 1.

### 3. LPS[D] 4755.3 cao hơn SOS 4753.2 — "retest" mà lại đi xa hơn cú phá — luật vi phạm: L10
- **Thuật toán gắn:** SOS 19:50 tại 4753.2; LPS[D] 20:25 tại **4755.3**, VSA 0.46x.
- **Đúng phải là:** LPS[D] là nhịp **hồi về retest biên vừa phá** — nó phải nằm **thấp hơn** SOS, gần biên 4744.4. Một điểm cao hơn SOS 2.1 giá là một cây trong đà tăng, không phải retest.
- **Nghi phạm trong thuật toán:** mục 7 tìm "đáy sâu nhất của nhịp hồi" trong sai số 20 tick quanh biên vừa phá — nhưng nhãn thực tế rơi ở 4755.3, cách biên 4744.4 tới **10.9 giá = 109 tick**. Sai số 20 tick không được áp. Kiểm lại nhánh này.

### 4. MOVE trước climax chỉ 23.6 giá / 23 nến — sát cả hai sàn — luật vi phạm: L1 (mức độ, không phải nguyên tắc)
- **Thuật toán gắn:** move 23.6 giá, 23 nến, hiệu suất 0.57.
- **Đúng phải là:** sàn là ≥20 nến và ≥8× biên độ TB. 23 nến chỉ hơn sàn 3 nến. Nhìn ảnh, đoạn trước climax là một đợt giảm ngắn từ 4746 xuống 4722 — có thật nhưng khiêm tốn so với chiều cao range 21.9 giá (move chỉ dài hơn range 1.08 lần). "Một MOVE bị climax chặn" theo L1 hàm ý move phải **lớn hơn hẳn** vùng nghỉ sau nó.
- **Ghi chú:** đây là góp ý về ngưỡng, không phải lỗi vi phạm luật rõ ràng — climax VSA 6.34x đủ mạnh để bù.

## Đạt
- Climax thật: 05-12 13:16, VSA **6.34x**, volume 59, biên độ 5.2 giá, nằm ở đáy chặn move. Đây là climax duy nhất trong lô 5 bài đạt chuẩn §3.3 THEORY.
- L2 Phase A đủ 3 lần đổi hướng; ST[A] 4719.1 (VSA 4.71x — có nỗ lực thật) nằm dưới mức climax → tạo biên phụ đúng L3.
- L4 tên range: origin SC + phá lên = **Tích luỹ**. Đúng.
- L9/L8: B (249n) dài nhất, C (5n) ngắn nhất. Đúng tỉ lệ.
- L10 Phase E (99n) là phase dài thứ hai, giá đi từ 4753 lên 4774 rồi đi tiếp — đúng nghĩa "rời range tìm vùng giá mới". Đây là bài duy nhất trong lô có Phase E ra hồn.
- SOS VSA 2.05x, thân 0.86 — cây phá có nỗ lực, neo đúng.

## Cần hỏi người học
- Cú sụp xuống 4680.8 rồi bò lại vào range: theo L5 nó lùng bùng ngoài range khá lâu → **Shakeout**. Nhưng nó thủng biên chính tới 1.9× chiều cao range. Ngưỡng nào phân xử giữa "Shakeout hợp lệ" và "climax không chặn được move, huỷ range"? Hai luật này đang chỉ ngược nhau ở đúng ca này.
