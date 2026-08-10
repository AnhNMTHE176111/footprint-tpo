# Chấm bài #18 — Tích luỹ (ACC) · 2026-05-20 01:36 → 16:46 (724 nến M1)

**Điểm: 4/10** — Xương sống đúng (climax sạch, tỉ lệ phase chuẩn, không lạm dụng nhãn Spring), nhưng hai nhãn m-SOS/m-SOW đều sai về định nghĩa, và ST[A] chốt Phase A quá sớm.

## Lỗi (nặng → nhẹ)

### 1. mSOW gán cho một điểm NẰM TRONG range — luật vi phạm: mục 5.1 (định nghĩa mSOS/mSOW ở v6)
- **Thuật toán gắn:** `mSOW 04:20 @4500.0, VSA 6.15x, thân 0.00`.
- **Đúng phải là:** định nghĩa v6 nói rõ mSOW là cú phá **CÓ THẬT** — đã bứt hẳn ra ngoài biên chính rồi mới thu vào. 4500.0 nằm **cao hơn biên chính dưới 4491.0 tới 9 giá**, tức chưa hề rời range. Điểm này chỉ là **ST[B]**.
- **Dấu hiệu quyết định trên chart:** chấm mSOW vẽ hẳn phía trên đường liền "biên CHINH duoi 4491.0"; thân/biên độ = 0.00 (doji).
- **Nghi phạm trong thuật toán:** nhánh gán nhãn cho thăm dò thất bại không kiểm lại `giá nhãn` có thực sự nằm ngoài biên chính hay không — nó gán theo **kết cục của đợt thăm dò**, rồi lấy nến VSA cao nhất trong đoạn (v7 #5) làm mốc, mà nến đó nằm trong range.

### 2. mSOS neo vào nến khối lượng ~0 (VSA 0.04×) và nến đó định nghĩa luôn biên phụ trên — luật vi phạm: L3 + mục 8 + vá v7 #5
- **Thuật toán gắn:** `mSOS 13:14 @4542.2, VSA 0.04x, thân 0.00` → `biên phụ trên = 4542.2`.
- **Đúng phải là:** VSA 0.04× là gần như **không có giao dịch**; không thể coi là "một thế lực đã cố phá range". Cây nỗ lực thật của đợt đó là cụm nến 12:47–13:00 (panel volume có thanh vàng rõ).
- **Nghi phạm trong thuật toán:** giống hệt #13 và #15 — nhãn mSOS sinh từ nới biên phụ vẫn neo theo **cực trị giá**, hoàn toàn không đi qua bước quét lại VSA cao nhất. Vá v7 #5 **chưa chạy** cho nhánh này (3/6 bài lô này dính).

### 3. SOS đặt ở mức THẤP HƠN biên phụ mà nó phải bứt qua — luật vi phạm: L3
- **Thuật toán gắn:** `SOS 14:21 @4540.5` trong khi `biên phụ trên = 4542.2`.
- **Đúng phải là:** L3 chốt "SOS muốn thực sự mạnh phải đóng cửa bứt qua biên PHỤ". Nhãn đang nằm **dưới** biên phụ 1.7 giá — hoặc mốc nhãn sai, hoặc điều kiện xác nhận đang dùng close của nến khác với nến mang nhãn. Trên ảnh giá sau đó đi thẳng lên 4590 nên cú phá là thật; chỉ là **nhãn đặt sai cây**.
- **Nghi phạm trong thuật toán:** nhãn hồi tố chọn "cây VSA cao nhất, đúng hướng, đóng cửa vượt **biên chính**" (đổi mốc ở v6) → cây được chọn vượt biên chính 4523.2 nhưng chưa vượt biên phụ. Nếu giữ tinh thần L3 thì mốc so sánh cho **nhãn** cũng nên là biên phụ.

### 4. ST[A] chốt Phase A sớm, bỏ qua cú test thật ở 4488 — luật vi phạm: L2
- **Thuật toán gắn:** `ST[A] 02:37 @4501.2`, Phase A kết thúc tại đó (43 nến).
- **Đúng phải là:** 4501.2 còn cách climax 4491.0 tới **10.2 giá = 32% chiều cao range** — chưa phải "quay về test vùng climax". Ngay sau đó, quanh `05-20 03:00–03:12`, giá xuống **4488.0** (chính là biên phụ dưới đang vẽ) — đó mới là lần chạm lại vùng cao trào, tức ST[A] thật, và Phase A phải kết thúc ở đó.
- **Dấu hiệu quyết định trên chart:** đáy nhọn chạm đường nét đứt 4488.0 nằm **sau** vạch tím kết thúc Phase A.
- **Nghi phạm trong thuật toán:** vá v7 #2 nâng ngưỡng hồi lên 0.4× khoảng AR↔climax — ST[A] này hồi 0.68× nên **lọt cửa**. Ngưỡng đang đo "hồi được bao nhiêu từ AR" chứ không đo "còn cách climax bao xa"; đúng như mục 13.1 đã ghi ("ST[A] vẫn thiếu ràng buộc khoảng cách đáy tới climax") — vá v7 chưa giải quyết.

### 5. (Nhẹ) LPS[D] neo vào nến VSA 0.58× và Phase E chạm trần 121 nến
- `LPS[D] 14:24 @4532.0, VSA 0.58x, thân 0.41` — nhịp retest chỉ 3 nến sau SOS, quá sớm để gọi là "giữ được ngoài biên".
- Phase E = 121 nến = đúng trần; nên ghi rõ "(chạm trần)".

## Đạt
- Điều kiện mở range (L1): MOVE giảm 34.6 giá / 39 nến / hiệu suất 0.41; cây climax VSA **6.97×**, biên độ 14.1 giá, 54 lot, đúng là đáy chặn move.
- **Nhãn SC neo đúng nến climax** (cùng nến 01:36) — vá v7 #4 chạy đúng ở bài này.
- AR @4523.2 VSA 5.57× — cú bật ngược thật, biên chính 4491.0–4523.2 (32.2 giá) khớp đúng vùng dao động suốt 528 nến Phase B trên ảnh.
- **Tỉ lệ phase đúng lý thuyết:** B 528 dài nhất (L9), C 8 ngắn nhất (L8) — đạt cả hai luật tỉ lệ.
- Phase C gán ngược ra `LPS[C] 14:13 @4503.0`: nằm **trong** range, đúng nửa dưới, ngay trước cú bứt — và đặc biệt **không** bị gọi nhầm là Spring dù nó là đáy sâu của nhịp cuối (4503.0 > biên chính dưới 4491.0). Tránh đúng lỗi lặp nhiều nhất của nguồn 2.pdf.
- Tên range: SC origin + phá lên = Tích luỹ, khớp L4.
- Chú thích nỗ lực/kết quả đúng dấu er (0.68 → "nhịp HIỆU QUẢ") — vá v7 #1 tốt.
