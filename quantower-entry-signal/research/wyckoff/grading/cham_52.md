# Chấm bài #52 — Tích luỹ (ACC) · 2026-07-20 12:02 → 2026-07-21 01:16 (732 nến M1)

**Điểm: 4/10** — Đoạn C→D→E vẽ khá đẹp, nhưng **biên chính chỉ rộng 5.4 giá** trong một vùng đấu giá rộng 20.6 giá: hai đường nét liền nằm lọt thỏm giữa hành động giá, làm hỏng toàn bộ ý nghĩa của mọi nhãn "trong/ngoài biên" phía sau.

## Lỗi (nặng → nhẹ)

### 1. Biên chính vô nghĩa — AR không phải một cú bật ngược thật — luật vi phạm: L2 + L3
- **Thuật toán gắn:** biên chính 4016.5 (SC) – 4021.9 (AR) = **5.4 giá (0.13%)**; biên phụ 4003.3 – 4023.9 = 20.6 giá; tỷ lệ **3.81x**, lách guard 4.0x trong gang tấc.
- **Đúng phải là:** AR là "cú bật ngược thật" chặn move giảm. Ở đây "AR" là nến +4 (12:06), VSA **0.69x**, cả nhịp hồi chỉ 5.4 giá sau một move giảm 22.9 giá — chưa tới 1/4 move, và nhỏ hơn cả biên độ của chính cây climax (9.0 giá). Biên trên thật của vùng đấu giá này là ~4023–4024, biên dưới ~4003.
- **Dấu hiệu quyết định trên chart:** trong 673 nến Phase B, giá cắt qua **cả hai** đường nét liền hàng chục lần và đi ngang chủ yếu ở 4007–4016, tức **dưới** cả biên chính dưới. Một biên mà giá sống bên dưới nó phần lớn thời gian thì không phải biên.
- **Nghi phạm trong thuật toán:** AR nhận diện bằng swing pivot + sàn 1.5× biên độ TB (lỗi D của v5) — không có ràng buộc AR phải hồi tối thiểu một tỷ lệ của MOVE, và không có sàn "chiều cao biên chính ≥ biên độ cây climax". Guard 4.0x đặt quá lỏng: ca này 3.81x rõ ràng đã hỏng.

### 2. ST[A] xuyên hẳn qua mức climax, không phải test — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 4012.8 (VSA 3.83x).
- **Đúng phải là:** mức climax là 4016.5; ST[A] nằm **3.7 giá BÊN DƯỚI** climax, tức hồi 1.69 lần khoảng AR↔climax. Đó là một cú phá xuống, không phải "test lại vùng climax". Chính v5 từng bỏ range vì lý do này ("ST[A] vượt hẳn qua climax"); v7 lại giữ.
- **Dấu hiệu quyết định trên chart:** ST[A] thấp hơn climax 69% chiều cao biên chính. Nếu công nhận nó là ST[A] thì theo L3 nó **phải** nới biên phụ dưới về 4012.8 ngay từ Phase A — phiếu không ghi nhận việc đó.
- **Nghi phạm trong thuật toán:** fix #2 chỉ đặt **sàn** hồi tối thiểu 0.4; thiếu **trần**. Cần chặn trên: ST[A] không được vượt quá mức climax quá một tỷ lệ nhỏ, nếu vượt thì hoặc đổi mốc climax hoặc bỏ range.

### 3. mSOW neo giữa range — luật vi phạm: L3
- **Thuật toán gắn:** mSOW 07-20 15:09 tại **4016.7** (VSA 6.74x).
- **Đúng phải là:** 4016.7 nằm **trên** biên chính dưới 4016.5, tức trong range. mSOW phải là cú **thò ra ngoài** rồi thất bại. Cây VSA 6.74x đó là cây mạnh nhất Phase B thật, nhưng nó không phá gì cả.
- **Nghi phạm trong thuật toán:** cùng lỗi với bài #51 — fix #5 chọn nến VSA cao nhất mà không lọc "nến phải nằm ngoài biên". (mSOW thứ hai, 4003.3, thì đúng: đó là cực trị dưới thật.)

### 4. Vai UT[B] chồng lên nhịp phá — luật vi phạm: mục 5 THEORY (test theo phase)
- UT[B] 00:25 (4023.0) — SOS 00:36 (4023.9) cách nhau 11 nến, cùng một nhịp đẩy lên. Gọi cây 00:25 là "test biên trên trong Phase B" rồi 11 phút sau gọi cây kế là SOS là tách vai gượng. Thực chất 00:25 → 00:31 (LPS[C]) → 00:36 (SOS) là **một** chuỗi Phase C→D liền mạch.

## Đạt
- **Mục 1 (L1):** MOVE giảm 22.9 giá / 28 nến, hiệu suất 0.67, bị cây SC VSA 4.88x chặn ngay — mở range hợp lệ, climax đúng là cực trị của move.
- **Mục 4 (L4):** origin SC + phá thật lên → **Tích luỹ**. Tên đúng.
- **Mục 5-6 (L8, L9):** thứ tự độ dài phase đúng chuẩn: B 673 (dài nhất) · C 5 (ngắn nhất) · D 13 · E 28.
- **Mục 7 (L10):** SOS 4023.9 đóng cửa vượt **biên phụ** trên (đúng yêu cầu L3), LPS[D] 4025.8 giữ được ngoài biên, Phase E đi tiếp lên ~4040. Đây là đoạn làm tốt nhất của bài.
- **Mục 8:** chú thích er = 2.58 → ghi "vùng hấp thụ NGHI VẤN" — **đúng dấu** (er ≥ 1). Fix #1 chạy đúng ở bài này.
- **L7:** LPS[C] và LPS[D] mỗi cái đúng 1 điểm, không vẽ vùng.
