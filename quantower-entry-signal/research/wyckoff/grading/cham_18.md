# Chấm bài #18 — Tích luỹ (ACC) · 2026-05-20 01:36 → 16:46 (724 nến M1)

**Điểm: 5/10** — Climax và Phase C/LPS[C] rất đẹp, nhưng **ST[A] chốt Phase A quá sớm** (mới đi 25% đường về climax) và **Phase B bao trọn một chân tăng 5 giờ nằm hẳn trên biên chính trên**.

## Lỗi (nặng → nhẹ)

### 1. ST[A] không test lại vùng climax — Phase A chốt sớm — luật vi phạm: L2 / mục 2 phiếu chấm
- **Thuật toán gắn:** ST[A] tại **4515.0** (01:58), trên range 4491.0–4523.2 (32.2 giá) → chỉ lùi được **8.2 giá từ AR = 25% chiều cao**.
- **Đúng phải là:** ST[A] là lần thứ 3 đổi hướng, **quay về phía climax rồi bị chặn lần nữa**. Điểm 4515.0 nằm ngay sát dưới AR, đó là một cái ngọ nguậy chứ không phải test. Cú test thật về vùng climax là nhịp 03:08 xuống **4488.0** (hiện bị gắn mSOW) — chính nó mới là ST[A] (hoặc Spring nếu tính vượt mức climax), và Phase A phải dài tới đó (~92 nến).
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm ST[A] nằm gần như trùng cao độ với chấm AR; mãi tới 03:12 mới có cụm nến chạm xuống hai đường biên dưới.
- **Nghi phạm trong thuật toán:** mục 4.2 — ST[A] là "swing pivot ngược đầu tiên được xác nhận (5 nến không cực trị mới) + sàn 1.5× biên độ TB". Người học đã chốt "đo bằng cấu trúc, không đo bằng %", nhưng "pivot ĐẦU TIÊN" + sàn nhiễu chỉ 1.5× ATR thì bắt luôn nhịp lắc đầu tiên. Cần điều kiện chất lượng khác vẫn thuần cấu trúc: ST[A] phải là pivot **chưa bị phá bởi một pivot cùng phía sâu hơn trong N nến sau đó** — ở đây 4488.0 sâu hơn 4515.0, nên 4515.0 phải bị hạ.

### 2. Phase B bao trọn một chân tăng 5 giờ nằm trên biên chính trên — luật vi phạm: L1 / mục 1 (lặp đúng lỗi bài #13)
- **Thuật toán gắn:** Phase B 550 nến (01:59 → 14:12).
- **Đúng phải là:** vùng cân bằng thật kéo tới khoảng 08:25 (giá lắc 4488–4523). Từ 08:25 tới 13:00 giá leo đều từ 4505 lên 4542, **đóng cửa hẳn trên biên chính trên 4523.2 từ khoảng 09:53 và ở trên đó liên tục ~200 nến**. Đó là Phase D của range, không phải Phase B.
- **Dấu hiệu quyết định trên chart:** cả nửa phải của Phase B nằm trên đường "biên CHÍNH trên 4523.2"; mSOS gán ở 4542.2 = **19 giá trên biên chính** = 59% chiều cao range.
- **Nghi phạm trong thuật toán:** giống bài #13/#14 — điều kiện phá thật đòi 3 nến liên tiếp đóng vượt **biên phụ** +30 tick thân ≥45%; giá bò lên bằng nến nhỏ nên không nến nào thoả, range sống thêm 5 giờ. Nhánh "40 nến ngoài biên và ≥60% đóng ngoài" cũng đo theo biên phụ nên hụt theo.

### 3. mSOS neo vào nến VSA 0.04x — luật vi phạm: THEORY §2.2 Nỗ lực ↔ Kết quả
- **Thuật toán gắn:** mSOS tại 4542.2, **VSA 0.04x, thân 0.00** — volume gần bằng 0.
- **Đúng phải là:** mSOS = một cú phá **thất bại**, tức một **nỗ lực** không thành. Nến VSA 0.04x không phải nỗ lực gì cả, chỉ là một cái râu trong khe thanh khoản. Nếu cả đoạn không có cây nỗ lực nào thì đừng gắn nhãn — chỉ nới biên phụ.
- **Nghi phạm:** mốc mSOS/mSOW lấy đúng nến cực trị giá; phải áp cơ chế hồi tố về cây VSA cao nhất như đã làm cho SOS/SOW (lỗi B vòng v5). **Lỗi này lặp ở 4/6 bài của lô (13, 15, 17, 18) → là lỗi hệ thống, không phải lỗi lẻ.**

### 4. SOS không bứt qua biên phụ — luật vi phạm: L3 ("SOS mạnh phải đóng cửa bứt qua biên PHỤ")
- **Thuật toán gắn:** SOS tại **4540.5**; biên phụ trên **4542.2**. Nhãn nằm **dưới** biên phụ 1.7 giá.
- **Đúng phải là:** cú phá này về sau đi tới 4590 nên nó là phá thật — vấn đề chỉ ở **vị trí nhãn**: nhãn hồi tố chọn cây VSA cao nhất (3.94x) mà cây đó chưa vượt biên phụ. Nên thêm ràng buộc: nến được chọn phải **đóng cửa vượt biên phụ**, nếu không thì lấy cây VSA cao nhất trong số các nến đã vượt.

### 5. LPS[D] lùi vào giữa hai biên — luật vi phạm: L10 (mức nhẹ)
- LPS[D] 4532.0 nằm dưới biên phụ trên 4542.2 (giữ được trên biên chính 4523.2). Cùng lỗi "đổi thước giữa hai bước" như bài #17: SOS xét theo biên phụ, retest lại xét theo biên chính.

## Đạt
- Climax (L1): SC 4491.0, **VSA 6.97x, biên độ 14.1 giá, 54 hợp đồng** — cao trào thật, mạnh. MOVE giảm 34.6 giá / 39 nến / hiệu suất 0.41. Đạt.
- AR 4523.2 với **VSA 5.57x, thân 0.58** — cú bật ngược thật, không phải râu. Đạt.
- Biên chính (L3): 4491.0 + 4523.2, cố định suốt 724 nến, không kéo theo giá. Đạt.
- Biên phụ (L3): đúng mỗi bên 1 cái, đúng cực trị xa nhất (4488.0 / 4542.2); tỷ lệ 1.68x — vùng làm việc hợp lý, không phình.
- **Phase C rất tốt (L8, case khó):** C dài **8 nến** — ngắn nhất trong cả dải phase, đúng luật. LPS[C] 4503.0 (VSA 3.18x) rơi đúng đáy nhịp đổ 41 giá từ 4542 về 4501 ngay trước cú bứt lên 4590. Đây chính là kiểu "test cuối trước SOS" mà giảng viên yêu cầu thu hẹp Phase C về (Ca #8 nguồn 2.pdf).
- Tên range (L4): SC + phá lên = Tích luỹ. Khớp, và cú phá đi thật (lên 4590 = 2 lần chiều cao range).
- Phase E có độ dài thật 121 nến.
- Chỉ số Phase B: SOT dưới n=2, thrust cuối/đầu 0.35, volume 0.49 → "cạn kiệt"; nhịp nỗ lực/kết quả cao nhất tại 12:09 (effort 2.48x, er 0.68) rơi đúng vùng giá bò chậm trước khi đổ về LPS[C] — **đo đúng bản chất**, đây là chỉ số hữu ích nhất trong 3 chỉ số mới ở bài này.
