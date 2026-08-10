# Chấm bài #50 — Phân phối (DIST) · 2026-07-16 11:48 → 12:51 (63 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây. Lỗi chí tử: **BCLX và AR được gắn lên CÙNG MỘT CÂY NẾN**, và cây nến đó là nến **ĐỎ sập 15 giá**. Phase A vì thế không tồn tại; mọi thứ phía sau là hệ quả.

## Lỗi (nặng → nhẹ)

### 1. BCLX và AR trùng đúng một nến — Phase A không có lần đổi hướng nào — luật vi phạm: L2; guard "climax trùng AR" (mục 8) KHÔNG bắn
- **Thuật toán gắn:** BCLX 11:49 giá 4047.8 (VSA 5.10×, thân 0.65) và **AR (yếu) 11:49 giá 4032.8 (VSA 5.10×, thân 0.65)** — cùng thời điểm, cùng nến.
- **Đúng phải là:** Phase A cần **đúng 3 lần đổi hướng** (climax chặn move → hồi ngược tới AR → quay lại bị chặn = ST[A]). Ở đây climax và AR là đỉnh và đáy của **cùng một cây**, tức không có lần đổi hướng nào — chỉ có một cây nến biên độ 15 giá. Range này chưa đủ điều kiện tồn tại.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến, nến 11:49: O 4047.8 / H 4047.8 / L 4032.8 / C 4038.0. Biên chính 4032.8–4048.4 = 15.6 giá thì **15.0 giá đến từ đúng cây nến này**.
- **Nghi phạm trong thuật toán:** mục 8 có ghi điều kiện bỏ ứng viên "climax trùng AR", nhưng phép so sánh gần như chắc chắn so **chỉ số nến của mốc mở range (11:48)** với chỉ số nến AR (11:49) → khác nhau nên không bắn, trong khi **nhãn** climax đã bị dời sang đúng nến 11:49. Guard phải so với `climax_ev.bar` (nến mang nhãn) chứ không phải nến mở range.

### 2. Nhãn BCLX đặt lên một cây nến ĐỎ — luật vi phạm: mục 3 (3) "màu nến khớp hướng move"; vá #4 CHƯA đủ
- **Thuật toán gắn:** BCLX (cao trào **mua**) tại 11:49 — nến đỏ, đóng cửa 4038.0 thấp hơn mở cửa 4047.8, sập 15 giá.
- **Đúng phải là:** BCLX phải là nến **xanh** chặn move tăng, đánh dấu tại **đỉnh** nến. Nến mở range 11:48 (O 4043.8 / C 4048.2, xanh, thân 0.90) mới đúng vai — chỉ tiếc VSA của nó là 1.38×.
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm đỏ BCLX nằm ngay đầu một cây nến đỏ dài duy nhất trong cụm nến xanh của nhịp tăng.
- **Nghi phạm trong thuật toán:** vá #4 kẹp cửa sổ cụm theo nến mở range cố định, nhưng khi dời nhãn theo VSA cao nhất **không kiểm lại điều kiện màu nến / phía cực trị**. Cây đỏ 5.10× ở đây thực chất là cây **bắt đầu cú xả** — nó là mSOW/SOW sớm, không phải BCLX.

### 3. Cây phá thật (VSA 8.14×) bị hạ cấp thành mSOW; nhãn SOW trao cho cây yếu hơn muộn 27 nến — luật vi phạm: L5, mục 5.1; vá #5 CHƯA đủ
- **Thuật toán gắn:** mSOW 12:16 tại **4017.4, VSA 8.14×** (cây volume cao nhất cả chart) — ở lại Phase B; SOW 12:43 tại 4007.5, VSA **3.36×**.
- **Đúng phải là:** cú 12:16 phá thủng biên chính dưới 15 giá và giá **không hề quay lại giữ trong range** — nhìn ảnh, nhịp hồi sau đó chỉ bò lên chạm đúng biên chính dưới 4032.8 lúc ~12:31 rồi rơi tiếp. Theo L5 đó là **SOW thật**, nhịp hồi 12:31 là **LPSY[D]**, Phase D bắt đầu từ 12:16.
- **Dấu hiệu quyết định trên chart:** cột volume vàng cao nhất panel dưới nằm đúng tại 12:16; sau đó giá không bao giờ đóng cửa lại trên 4032.8.
- **Nghi phạm trong thuật toán:** vá #5 "quét lại lấy nến VSA cao nhất trong đoạn thăm dò" chỉ chỉnh **vị trí nhãn**, không chỉnh **quyết định hạ cấp**. Điều kiện hạ cấp (giá lùi qua biên chính) đang bắn nhầm ở nhịp hồi *chạm* biên; cần dùng **đóng cửa vượt hẳn 30 tick vào trong** như mục 5.1 đã nêu, và cây VSA 8.14× phải được ưu tiên giữ vai SOS/SOW.

### 4. Phase C (37 nến) là phase DÀI NHẤT, Phase B (10 nến) là phase ngắn nhất — luật vi phạm: L8 và L9 cùng lúc
- **Thuật toán gắn:** A 8 · B **10** · C **37** · D 7 · E 2.
- **Đúng phải là:** B dài nhất, C ngắn nhất. Ở đây đảo ngược hoàn toàn — và Phase C 37 nến nuốt trọn cả cú sụp 12:16 lẫn nhịp hồi, tức nuốt cả Phase D.
- **Nghi phạm trong thuật toán:** nhánh Phase C gán ngược không có trần độ dài; cộng thêm lỗi #3 (SOW bị đẩy lùi tới 12:43) kéo dài đuôi Phase C thêm 27 nến.

### 5. LPSY[C] lại đặt lên một ĐỈNH sát biên trên — sai vai (lỗi lặp với bài #46)
- **Thuật toán gắn:** LPSY[C] 12:06 tại 4045.4 (VSA 2.94×) — cách biên chính trên 4048.4 đúng 3 giá.
- **Đúng phải là:** **UT[B]** (test biên trên rồi bị chặn). LPSY là nhịp hồi **yếu, biên hẹp, ở nửa dưới**, sau khi cung đã áp đảo — không phải một đỉnh chạm kháng cự.
- **Nghi phạm trong thuật toán:** giống bài #46 — nhánh gán ngược mặc định đặt tên LPSY[C] cho pivot nửa trên mà không phân loại hình thái.

### 6. Range 63 nến với đủ Phase A→E = một cú xả thẳng đứng bị cắt ngang, không phải vùng đấu giá — luật vi phạm: L1
- MOVE trước climax chỉ **16.8 giá / 23 nến** (vừa chạm sàn 20 nến). Toàn bộ "range" là 1 giờ đồng hồ, còn cú xả sau đó đi 40 giá. Theo chuẩn đã chốt, TR M1 ngắn mà đủ A→E phải nghi ngay là nhiễu.

### 7. Trình bày: biên phụ trên 4048.7 gần trùng biên chính trên 4048.4
- Hai đường (nét đứt và nét liền) chồng lên nhau trên ảnh, kèm nhãn đè lên chữ "bias" ở dòng phụ đề — không đọc được. Lỗi trình bày, không phải cấu trúc. Chênh 0.3 giá (3 tick) thì nên gộp, không vẽ biên phụ.

## Đạt
- **Tên range đúng (L4):** origin BCLX + phá xuống thật = **Phân phối** — và giá thực sự đi tiếp xuống 3986 sau đó.
- **Biên phụ dưới 4017.4 đúng là cực trị xa nhất** (đáy mSOW), mỗi bên 1 cái — L3 đạt ở phía dưới.
- **ST[A] 11:55 tại 4047.3** nằm sát mức climax 4048.4 (cách 1.1 giá) — về vị trí là một test đúng vai, dù Phase A tổng thể đã hỏng vì lỗi #1.
- Vá #1 chạy đúng: er = 0.27 → "nhịp HIỆU QUẢ, không phải hấp thụ", đúng dấu.
- SOT ghi `none` trung thực trên dữ liệu 10 nến Phase B, không bịa chuỗi.

## Nếu là tôi
Không vẽ range ở đây. Ngày 16/07 từ 11:48 là **một nhịp xả liên tục** 4048 → 3986; cây 11:49 (đỏ, 5.10×) là cú xả đầu tiên, cây 12:16 (8.14×) là SOW chính. Muốn vẽ Wyckoff cho đoạn này thì phải lùi ra khung lớn hơn để tìm vùng phân phối thật ở phía trên, chứ không cắt 63 nến giữa một cú rơi rồi dán đủ 5 phase lên đó.

## Cần hỏi người học
- Khi cây VSA cao nhất của cụm climax **ngược màu** với hướng move (như cây đỏ 5.10× ở đây), nên: (a) giữ nhãn ở nến đúng màu dù VSA thấp hơn, hay (b) coi cây ngược màu đó là tín hiệu đảo chiều tức thì và **bỏ luôn ứng viên range**? Tôi nghiêng về (b) nhưng lý thuyết không phân xử dứt khoát.
