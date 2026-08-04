# Chấm bài #44 — Tích lũy (ACC) · 2026-07-20 12:02 → 2026-07-21 00:59 (715 nến M1)

**Điểm: 4/10** — Vùng đấu giá là thật và tên range đúng, nhưng **biên chính vẽ sai hoàn toàn**: 5.4 giá cho một range mà giá dao động 22 giá. Mọi phép đo phía sau đều lệch theo.

## Lỗi (nặng → nhẹ)

### 1. Biên chính chỉ 5.4 giá — AR bắt vào một cái ngọ nguậy, không phải cú bật thật — luật vi phạm: L2 + L3
- **Thuật toán gắn:** AR tại 12:06, giá 4021.9, **VSA 0.69×**. Biên chính = 4016.5-4021.9 = **5.4 giá (0.13%)**.
- **Đúng phải là:** AR là "cú bật ngược thật" sau climax. Cây 12:06 có volume 86 lot (0.69× TB) và biên độ 1.9 giá — đó là nhiễu, không phải sóng phản ứng. Biên chính thật nên là ~4016.5 (SC) tới ~4024 hoặc cao hơn; nhìn ảnh, cú bật đáng gọi là AR là nhịp lên **4023.8-4024** ngay đoạn 12:00-12:16, hoặc cấu trúc thật của cả vùng này là **4001.6 - 4023.9** (chính là biên phụ đang vẽ).
- **Dấu hiệu quyết định trên chart:** biên phụ 22.3 giá = **4.1 lần** biên chính 5.4 giá. Nhìn ảnh: hai đường cam liền nằm sát nhau như một dải mỏng ở nửa trên, còn **phần lớn 715 nến giá dao động ở DƯỚI cả hai đường đó** (vùng 4005-4016). Một "biên chính" mà giá sống bên ngoài nó suốt phần lớn thời gian thì không phải biên.
- **Nghi phạm trong thuật toán:** vá lỗi D bỏ hết ngưỡng % và chỉ còn "swing pivot đầu tiên xác nhận 5 nến + nhịp ≥ 1.5× biên độ TB". Vấn đề: biên độ TB tại đó bị **kéo lên** bởi chính cụm climax (cây 12:00 rơi 7.1 giá, cây 12:02 rơi 9 giá), nhưng 1.5× của một TB nhỏ trước đó vẫn quá dễ thoả. Cần thêm điều kiện tương đối với **độ dài move** hoặc với **biên độ cây climax** (AR phải hồi ít nhất X% biên độ cụm climax), đúng như ghi chú "nghi ngờ #4" trong tài liệu thuật toán — chỗ đó đã bị gỡ và giờ hậu quả lộ ra.

### 2. Phase D = 1 nến, Phase E = 2 nến — luật vi phạm: L10 (lỗi J của vòng v4, CHƯA hết)
- **Thuật toán gắn:** D = 00:57 → 00:57 (**1 nến**), E = 00:58 → 00:59 (**2 nến**).
- **Đúng phải là:** Phase D phải bao trọn nhịp retest, Phase E là đoạn giá rời range đi tìm vùng giá mới. Nhìn ảnh: sau SOS giá còn chạy lên tới **4042** (đoạn 01:00-01:20 trên chart), tức Phase E thật dài vài chục nến. Range bị đóng ngay ở nến 00:59 nên cắt đúng lúc cú phá bắt đầu có kết quả.
- **Dấu hiệu quyết định trên chart:** không có nhãn LPS[D] nào — vì Phase D chỉ có 1 nến thì không thể có nhịp hồi để đánh dấu. Đây là bằng chứng D bị nén.
- **Nghi phạm trong thuật toán:** SOS xác nhận rồi range **đóng ngay** (mục 7 "dù Phase E có đạt hay không, range vẫn ĐÓNG tại đây") + đích Phase E = 1.0× chiều cao range. Vì chiều cao range chỉ **5.4 giá** (lỗi #1), đích E đạt ngay lập tức trong 2 nến → E = 2 nến. Hai lỗi cộng dồn.

### 3. SOS neo vào cây VSA 0.57× — luật vi phạm: mục 5.1 lỗi B (lặp lại y hệt bài #41, #42)
- **Thuật toán gắn:** SOS tại 00:57, giá 4029.2, **VSA 0.57×**, thân 0.60.
- **Đúng phải là:** cây phá thật phải là cây có nỗ lực. Nhìn panel volume đoạn 00:31-00:57 có cụm thanh vàng rõ; cây 0.57× là cây đã ở ngoài biên rồi. Lỗi B đã được vá cho trường hợp "3 nến xác nhận", nhưng ở đây nhãn vẫn rơi vào nến volume thấp.
- **Dấu hiệu quyết định trên chart:** 0.57× ghi trong phiếu — **thấp hơn nửa TB 20 nến**. Còn mSOS ở 15:09 lại có VSA **6.74×** và thân 0.87. Cây nỗ lực lớn nhất cả range bị gọi là "minor", cây yếu nhất được gọi là SOS.
- **Nghi phạm trong thuật toán:** cùng nghi phạm với bài #41 — cửa sổ hồi tố chọn cây VSA cao nhất có lẽ chỉ quét trong đoạn 3 nến xác nhận, quá hẹp. Nên quét từ nến đầu tiên đóng cửa vượt biên chính.

### 4. mSOS 4023.9 (VSA 6.74×) đáng là SOS thất bại nhưng làm hỏng chính điều kiện SOS về sau — luật vi phạm: L3 (SOS phải bứt qua biên phụ)
Cây 15:09 VSA **6.74×** thân 0.87 đẩy giá lên 4023.9 rồi thất bại → đúng là mSOS, gán đúng. **Nhưng** nó nới biên phụ trên lên 4023.9, và cú phá thật cuối cùng chỉ đạt 4029.2 — vừa đủ vượt 5.3 giá. Đây là cơ chế đúng theo L3, ghi nhận thuật toán làm đúng ý; chỉ lưu ý rằng khi biên chính bị vẽ hụt (lỗi #1) thì biên phụ gánh hết vai trò biên thật, và lúc đó "vượt biên phụ" mới là thứ có nghĩa.

### 5. LPS[C] có VSA 0.74× và thân 0.05 — đúng loại test, nhưng Phase C 26 nến dài gấp ~2 lần Phase A 14 nến — luật vi phạm: L8 vs L2
Về tuyệt đối C=26 nến vẫn ngắn hơn B=673, đạt L8. Nhưng Phase A chỉ 14 nến là quá ngắn cho một CHoCH thật — hệ quả của lỗi #1 (AR bắt ngay nến +4).

## Đạt
- **Mở range (L1):** climax **VSA 4.88×**, 516 lot, biên độ 9 giá, là đáy của cửa sổ, chặn một MOVE giảm 22.9 giá hiệu suất 0.67. Đây là climax thật nhất trong 4 bài lô này. Đạt.
- **Tên range (L4):** origin SC + phá lên thật = Tích luỹ. Đúng.
- **Phase B là phase dài nhất (L9):** 673/715. Đạt. Đọc effort↔result: phe bán đi được tới 4001.6 (mSOW 22:55, nhưng VSA chỉ **1.57×** và thân **0.12** — nỗ lực bé, râu dài, không có người bán thật); phe mua thì có cây 6.74×. Nỗ lực lớn nằm bên mua → tích luỹ. Kết luận cấu trúc đúng.
- **Mỗi bên đúng 1 biên phụ** (4001.6 và 4023.9), tuân L3.
- **Không spam nhãn:** 7 nhãn cho 715 nến, không có nhãn trùng vai.

## Cần hỏi người học
- Khi biên chính (climax↔AR) hẹp hơn nhiều so với biên phụ — ở đây 5.4 vs 22.3 giá — có nên **quay lại tìm AR khác** (huỷ ứng viên và mở lại) thay vì chấp nhận một range mà giá sống ngoài biên chính phần lớn thời gian? Hiện luật L3 nói biên chính cố định sau Phase A, nhưng không nói phải làm gì khi Phase A rõ ràng bắt sai.
