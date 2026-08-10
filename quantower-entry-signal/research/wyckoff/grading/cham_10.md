# Chấm bài #10 — Phân phối (DIST) · 2026-04-23 12:06 → 17:32 (233 nến M1)

**Điểm: 5/10** — Bài tốt nhất nhì lô: khung range, tên gọi, tỉ lệ A/B/C và cây SOW đều đúng. Nhưng **UTAD gọi sai chỗ** — đúng lỗi kinh điển của 3/5 ca nguồn 4.pdf — và nhãn đó còn nằm lạc hẳn ra ngoài dải Phase C của chính nó.

## Lỗi (nặng → nhẹ)

### 1. UTAD gán tại 12:43 nhưng cấu trúc mãi 17:16 mới sụp — luật vi phạm: THEORY §4.1, Ca #1/#3/#4 nguồn 4.pdf
- **Thuật toán gắn:** `UTAD · 12:43 · 4795.6 · Phase C · confirmed`.
- **Đúng phải là:** **UT[B]**. UTAD chỉ là cú test **cuối cùng** phá đỉnh range ngay trước khi cấu trúc sụp, không có nhịp hồi đáng kể nào sau đó. Ở đây sau 12:43 còn **178 nến Phase B**, giá còn quay lên vượt biên chính trên lần nữa (mSOS 15:19 tại 4792.4) rồi mới sụp lúc 17:16. Có nhịp hồi giữ lại trong range ⇒ theo tiêu chí Ca #4 (4.pdf) đó là UT/ST[B], chưa phải UTAD.
- **Dấu hiệu quyết định:** khoảng cách UTAD → SOW = **273 phút**; và giữa hai mốc đó có hẳn một mSOS ở biên trên.
- **Nghi phạm trong thuật toán:** nhánh Phase C "case dễ" bắn UTAD ngay khi cú thăm dò vượt biên phụ + quay lại trong range, rồi đánh `confirmed` chỉ dựa vào tiêu chí "đi được ≥50% sang biên đối diện" (mục 6). Tiêu chí đó không loại được ca có **nhịp hồi trở lại biên cũ** sau đó. Cần thêm: shock bị **huỷ tư cách** nếu giá quay lại chạm/vượt biên phía shock trước khi SOS/SOW nổ ra.

### 2. Nhãn UTAD (Phase C) nằm hoàn toàn ngoài dải Phase C — luật vi phạm: nhất quán timeline, L8
- **Thuật toán gắn:** dải Phase C = 16:51 → 17:15 (16 nến); nhãn UTAD ghi Phase C nhưng đứng ở 12:43, tức nằm giữa dải Phase B (12:32–16:48).
- **Đúng phải là:** nếu Phase C thật sự bắt đầu tại LPSY[C] 16:51 thì UTAD ở 12:43 phải bị hạ cấp và ghi rõ Phase B — hai thứ này đang mâu thuẫn nhau ngay trên cùng một chart. Nhìn ảnh: nhãn UTAD ở góc trái, ô "Phase C (16n)" ở góc phải, cách nhau gần hết chiều ngang.
- **Nghi phạm trong thuật toán:** khi shock hết hạn/thất bại, spec nói phải "đổi nhãn thành UT/mSOS/mSOW và **xoá hẳn đoạn C**" (lỗi C v5). Ở đây đoạn C bị xoá và mở lại ở chỗ khác, nhưng **nhãn UTAD cũ không bị đổi tên**, `phase` vẫn treo là C. Đúng họ lỗi #6 của v6 (nhãn mồ côi) — chưa dứt điểm.

### 3. mSOS và mSOW đều neo vào nến volume THẤP — luật vi phạm: THEORY §2.2, bản vá #5
- **Thuật toán gắn:** `mSOS 15:19 · VSA 0.91x` · `mSOW 16:05 · VSA 0.56x`.
- **Đúng phải là:** mSOS/mSOW theo định nghĩa v6 là cú phá **có thật** ra ngoài biên chính rồi mới bị thu về. Một cú phá thật không thể nằm ở nến có volume bằng **một nửa trung bình**. Cây thật của mỗi đoạn thăm dò chắc chắn mạnh hơn — nhìn panel volume quanh 15:19 và 16:05 đều có thanh vàng (VSA≥2.2x) ở gần đó.
- **Nghi phạm trong thuật toán:** bản vá #5 ("quét lại lấy nến VSA cao nhất trong đoạn thăm dò") **chưa có hiệu lực trên nhánh này** — cả hai nhãn vẫn rơi vào nến chốt kết cục, không phải nến mạnh nhất. Kiểm lại xem hạ cấp mSOS/mSOW từ shock pending có đi qua cùng hàm hồi tố với SOS/SOW không.

### 4. Phase E dài 2 nến, range đóng ngay trước cú sụp thật — luật vi phạm: L10
- **Thuật toán gắn:** Phase E = 17:31 → 17:32 (2 nến), range `completed`.
- **Đúng phải là:** Phase E là "giá rời range đi tìm vùng giá mới". Nhìn ảnh, cú tìm vùng giá mới xảy ra **sau** khi range đóng: từ 17:32 giá rơi thêm gần 40 giá xuống 4717 với cụm volume lớn nhất cả chart. Phase E đang cắt đúng chỗ nó vừa bắt đầu.
- **Dấu hiệu quyết định:** chiều cao biên chính chỉ 11.7 giá; đích Phase E "đi thêm 1.0× chiều cao" = 11.7 giá, đạt được trong 2 nến nên máy chốt luôn.
- **Nghi phạm trong thuật toán:** đích Phase E buộc theo **chiều cao biên chính**, mà biên chính ở đây rất hẹp (0.24% giá) ⇒ đạt đích tức thì. Nên dùng max(chiều cao biên **phụ**, k×ATR) làm đích, hoặc giữ Phase E chạy tới khi giá lùi vào biên như spec đã ghi.

### 5. AR volume 0.19x, thân 0.00 mà không gắn cờ yếu
AR 12:16 tại 4779.2 — một nến gần như không giao dịch lại đang định nghĩa **biên chính dưới** của cả range. Cùng nghi phạm với bài #08: `ar_vsa` đã đo nhưng chưa dùng để gắn cờ.

## Đạt
- **Mục 1 (L1):** MOVE tăng 43.0 giá / 64 nến, hiệu suất 0.37; BCLX 12:06 VSA 3.68x đúng đỉnh move. Climax chặn move — chuẩn.
- **Mục 2 (L2) một phần:** đủ 3 lần đổi hướng, ST[A] 12:31 (4794.1) vượt nhẹ climax rồi bị chặn — đúng vai một cú test biên trên và đúng L3 khi nó tạo biên phụ.
- **Mục 3 (L3):** biên chính 4779.2–4790.9 cố định; biên phụ 4768.9 / 4795.6 đúng là cực trị xa nhất mỗi bên, tỷ lệ 2.28x còn trong ngưỡng. **SOW 4765.0 đóng cửa bứt qua biên phụ dưới 4768.9** — đúng yêu cầu "SOS/SOW mạnh phải qua biên phụ".
- **Mục 4 (L4):** BCLX chặn move tăng + phá thật xuống ⇒ **Phân phối**. Đúng.
- **Mục 5 (L9):** Phase B 178/233 nến — dài nhất, đúng tỉ lệ. Phase C 16 nến — ngắn nhất, đúng L8 về độ dài (chỉ sai nội dung, xem lỗi 2).
- **Mục 8:** SOW neo đúng cây VSA 3.40x; LPSY[C] tại nến VSA 2.92x — cả hai đều là cây có nỗ lực thật.
- **Chú thích nỗ lực/kết quả đúng dấu** (er=0.51 → "HIỆU QUẢ").
