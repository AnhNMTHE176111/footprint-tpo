# Chấm bài #17 — Phân phối (DIST) · 2026-05-14 04:36 → 14:01 (352 nến M1)

**Điểm: 5/10** — Bài tốt nhất của lô: khung range, tỉ lệ phase và chuỗi C→D→E đều đọc được. Hỏng ở hai chỗ: nhãn mSOS đặt ở một mức giá mâu thuẫn với chính tên nhãn, và cú upthrust rõ nhất của cả range không được gán nhãn nào.

## Lỗi (nặng → nhẹ)

### 1. Nhãn mSOS đặt DƯỚI biên chính dưới — mâu thuẫn nghĩa nhãn — luật vi phạm: mục 5.1 (định nghĩa mSOS)
- **Thuật toán gắn:** `mSOS 09:30 @4732.4, VSA 9.33x` — trong khi biên chính là 4735.0–4753.0.
- **Đúng phải là:** mSOS = một cú phá **lên** có thật rồi thu lại vào range. Một điểm nằm **thấp hơn biên chính dưới 2.6 giá** không thể mang nhãn "sign of strength"; đó là một cú thăm dò **xuống**, phải là ST[B] hoặc mSOW.
- **Dấu hiệu quyết định trên chart:** chấm cam mSOS vẽ dưới đường liền 4735.0, ngay đáy một nhịp giảm.
- **Nghi phạm trong thuật toán:** vá v7 #5 "quét lại lấy nến VSA cao nhất trong đoạn thăm dò" **không lọc theo hướng/theo phía biên** — nó lấy cây VSA 9.33× mạnh nhất của cả đoạn, mà cây đó nằm ở đáy nhịp hồi chứ không ở phía biên bị phá. Vá làm sai thêm so với v6 ở ca này.

### 2. Cú upthrust 4757.7 lúc ~07:36 không được gán nhãn — luật vi phạm: L3 + L6 (chỉ còn UT/UA/DA cho test nhẹ) + mục 9 (nhãn thiếu)
- **Thuật toán gắn:** không có sự kiện nào ở đỉnh; chỉ lặng lẽ nới `biên phụ trên = 4757.7`.
- **Đúng phải là:** đó là cú duy nhất trong cả range vượt hẳn biên chính trên 4753.0 rồi bị đánh sập ngay trong 2 nến — đúng vai **UT[B]** (và nếu nó là cú test đỉnh cuối trước khi cấu trúc sụp thì mới được xét UTAD; ở đây vẫn còn 5 tiếng dao động sau đó nên **UT[B]** mới đúng, theo Ca #1/#4 nguồn 4.pdf).
- **Dấu hiệu quyết định trên chart:** cây xanh cao vượt hẳn đường liền 4753.0 lúc 07:36, kèm thanh volume vàng cao nhất nửa đầu chart, nến kế tiếp là nến đỏ nuốt lại.
- **Nghi phạm trong thuật toán:** nhánh "chỉ nới biên phụ, không ghi nhãn" khi cú thăm dò không đạt ngưỡng "mạnh" (≥max(15 tick, 15% chiều cao) hoặc VSA≥2.2×). Với chiều cao range 18.0 giá thì 15% = 2.7 giá; cú này thò ra 4.7 giá nên **đáng lẽ** đủ — cần soi lại vì sao nhánh này im lặng.

### 3. Nhãn BCLX rơi ra ngoài khung range — luật vi phạm: vá v7 #4
- **Thuật toán gắn:** range mở 04:36, nhãn `BCLX` đặt tại **04:32** (@4752.0, VSA 2.33×).
- **Nghi phạm trong thuật toán:** lặp lại y hệt #13 và #15 — nhãn climax không bị kẹp `≥ range_start`. 3/6 bài trong lô mắc lỗi này → chưa vá xong.

### 4. Cây mở range chỉ 4 lot, VSA 0.91× — luật vi phạm: mục 3(1) THUẬT TOÁN
- **Thuật toán gắn:** climax @4753.0, VSA **0.91×**, biên độ 1.8 giá.
- **Đúng phải là:** cây thoả ngưỡng thật là 04:32 (VSA 2.33×, 10 lot). Cụm climax dời **mức** sang cây cực trị giá mà không kiểm lại ngưỡng — cùng nghi phạm với bài #14, chỉ nhẹ hơn vì ở đây MOVE trước rất sạch (38.0 giá / 23 nến / hiệu suất **0.86**).

### 5. (Nhẹ) LPSY[D] lùi vào trong biên phụ — luật vi phạm: L10
- `SOW 13:30 @4727.1` (dưới biên phụ dưới 4728.8, tốt) → `LPSY[D] 13:50 @4731.4` nằm **trên** cả biên phụ dưới. Nhịp retest phải giữ được ở ngoài biên; nên bổ sung điều kiện `lpsy_price ≤ biên phụ`.

## Đạt
- Điều kiện mở range (L1): MOVE tăng 38.0 giá / 23 nến / hiệu suất 0.86 — chân move rõ nhất cả lô, climax đúng là đỉnh của cửa sổ.
- Phase A đủ 3 lần đổi hướng và kết thúc đúng tại ST[A]; AR @4735.0 VSA 4.17× thân 1.00 — một cú bật ngược thật, không phải râu nhiễu.
- **Tỉ lệ phase đúng lý thuyết:** A 30 · B 277 (dài nhất, L9) · **C 14 (ngắn nhất, L8)** · D 25 · E 7. Đây là bài duy nhất trong lô đạt cả L8 lẫn L9.
- Phase C gán ngược cho ra `LPSY[C] 13:14 @4746.4` — nằm trong range, đúng **nửa trên**, ngay trước SOW; đúng cách xử lý "case khó" của L8, và tách bạch được LPSY[C] với LPSY[D] (tránh đúng lỗi Ca #3 nguồn 4.pdf).
- SOW @4727.1 VSA 6.12× đóng cửa vượt **cả biên chính lẫn biên phụ** dưới — đúng yêu cầu L3 "SOS/SOW mạnh phải bứt qua biên phụ".
- Tên range: BCLX origin + phá xuống = Phân phối, khớp L4.
- Chú thích nỗ lực/kết quả đúng dấu er (0.25 → "nhịp HIỆU QUẢ") — vá v7 #1 tốt.
