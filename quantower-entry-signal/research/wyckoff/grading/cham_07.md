# Chấm bài #07 — Tái tích lũy (RE-ACC) · 2026-04-13 16:47 → 2026-04-14 06:26 (265 nến M1)

**Điểm: 3/10** — Khung range và tên gọi chấp nhận được, nhưng **dải phase vẽ sai hoàn toàn**: Phase C dài gấp đôi Phase B, Phase A cũng dài hơn Phase B. Phải vẽ lại toàn bộ ranh giới B/C/D.

## Lỗi (nặng → nhẹ)

### 1. Phase C (59 nến) DÀI HƠN Phase B (26 nến) — luật vi phạm: L8 + L9
- **Thuật toán gắn:** A=36 · B=26 · **C=59** · D=24 · E=121.
- **Đúng phải là:** B là phase dài nhất, C là phase ngắn nhất. Đoạn 18:17→23:03 mà máy gọi "Phase C" thực ra là **nguyên nhịp đi ngang rồi bò lên của Phase B** — nhìn ảnh, trong đoạn đó giá đi từ 4785 lên tận 4810 (hơn cả chiều cao biên chính 21.0 giá). Một đoạn giá chạy hết chiều cao range không thể là "phase ngắn nhất, tín hiệu đầu tiên".
- **Đúng ra:** Phase B kéo tới ~22:40; Phase C chỉ là nhịp test cuối ngay trước SOS (vài nến); Phase D bắt đầu tại cây phá.
- **Dấu hiệu quyết định:** LPS[C] gán tại 18:17 giá 4785.0 — cách SOS (23:04) tới 59 nến và 39.7 giá. Không có cách nào gọi đó là "điểm test cuối cùng trước cú phá" (Ca #8 nguồn 2.pdf: giảng viên thu hẹp Phase C quanh đúng điểm test cuối trước SOS).
- **Nghi phạm trong thuật toán:** nhánh gán ngược Phase C (mục 6 "case khó") — cửa sổ `min(60, 0.8×len(B))` với len(B)=26 cho ra 21 nến, nhưng LPS[C] lại nằm ở nến thứ 59 trước SOS ⇒ điểm này **không** đến từ nhánh gán ngược mà từ một nhánh khác (nhịp test vùng điểm rũ trong lúc chờ). Nhánh đó đang được phép đặt LPS[C] mà **không kiểm ràng buộc khoảng cách tới SOS**, rồi Phase C bị kéo từ đó tới hết.

### 2. Nhãn ST[B] (Phase B) nằm BÊN TRONG dải Phase C — luật vi phạm: L8, tính nhất quán timeline
- **Thuật toán gắn:** LPS[C] tại 18:17 (Phase C) rồi ST[B] tại 18:27 (ghi Phase B).
- **Đúng phải là:** một sự kiện xảy ra **sau** mốc mở Phase C không thể mang nhãn Phase B. Và về nội dung: ST[B] tại 4783.2 **sâu hơn** LPS[C] tại 4785.0 — cú test biên dưới thật sự là cú sau, nên nếu có Phase C thì phải bắt đầu tại 18:27 chứ không phải 18:17.
- **Dấu hiệu quyết định:** phiếu số liệu, cột Phase: `LPS[C] … 18:17 … C` / `ST[B] … 18:27 … B`; dải Phase C ghi bắt đầu 18:17.
- **Nghi phạm trong thuật toán:** trường `phase` của sự kiện được gán lúc tạo và không cập nhật lại khi dải phase dịch; thiếu một bước kiểm "mọi sự kiện phải nằm trong dải phase của nó".

### 3. Phase A (36 nến) dài hơn Phase B (26 nến) — luật vi phạm: L9
- **Thuật toán gắn:** ST[A] chốt tại 17:27, Phase B kết ở 18:16.
- **Đúng phải là:** với một TR 265 nến, Phase B phải chiếm phần lớn thời lượng. Ở đây A+C = 95 nến trong khi B chỉ 26.
- **Dấu hiệu quyết định:** cùng bảng độ dài phase ở trên; ST[A] tại 4810.9 đã vượt hẳn qua mức climax 4806.7 (4.2 giá) nên nó thực chất là một cú **thăm dò lên** đầu Phase B, không phải mốc kết Phase A.
- **Nghi phạm trong thuật toán:** ST[A] chỉ bị chặn bởi trần "≤1.0× chiều cao range" khi vượt climax — quá lỏng, cho phép ST[A] biến thành cú phá biên trên.

### 4. Nhãn SOS neo vào cây volume tầm thường — luật vi phạm: THEORY §2.2 (Effort vs Result), mục 5.1 spec
- **Thuật toán gắn:** SOS tại 23:04, giá 4824.7, **VSA 1.94x**.
- **Đúng phải là:** SOS là cú phá có nỗ lực nổi bật. VSA 1.94x còn dưới ngưỡng climax 2.2x của chính hệ. Nhìn panel volume ở đoạn 22:46–23:04, các thanh đều thấp — cú "phá" này đi lên bằng quán tính chứ không bằng nỗ lực.
- **Ghi thêm:** giá đã đóng cửa vượt biên phụ trên 4810.9 từ **trước** 23:04 khá lâu (nhìn ảnh, quanh 22:10 giá đã ở 4815+). Nhãn SOS đang bị đặt muộn so với chỗ cấu trúc thật sự vỡ.
- **Nghi phạm trong thuật toán:** hồi tố "cây VSA cao nhất trong đoạn" chỉ quét từ nến thò khỏi **biên chính**; ở đây đoạn quét nhiều nến volume thấp nên cây được chọn vẫn yếu. Thiếu một sàn tuyệt đối kiểu "VSA cây phá phải ≥ VSA climax" hoặc ít nhất cảnh báo khi VSA < 2.2x.

## Đạt
- **Mục 1 (L1):** có MOVE tăng thật 42.4 giá / 60 nến, hiệu suất 0.36; cây BCLX 16:47 là đỉnh của move và VSA 2.72x — climax **chặn** move, không nằm giữa move. Đúng điều kiện mở range.
- **Mục 3 (L3):** biên chính 4785.7–4806.7 = đúng AR + climax, cố định suốt range; biên phụ 4783.2 / 4810.9 đúng là cực trị xa nhất, mỗi bên đúng 1 cái, tỷ lệ 1.32x lành mạnh.
- **Mục 4 (L4):** BCLX chặn move tăng + phá thật lên trên ⇒ **Tái tích luỹ**. Tên đúng bảng 4 pattern.
- **Mục 8 một phần:** nhãn climax neo đúng cây VSA cao nhất của cụm (2.72x) và đúng đỉnh giá 4806.7 — lỗi "nhãn climax trôi" của vòng trước **đã hết ở bài này**.
- **Chú thích nỗ lực/kết quả đã sửa đúng dấu:** er=0.88 ghi "nhịp HIỆU QUẢ", không còn hard-code "vùng hấp thụ NGHI VẤN".
