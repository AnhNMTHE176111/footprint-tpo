# Chấm bài #37 — Tái phân phối (RE-DIST) · 2026-06-30 00:09 → 00:56 (47 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây: 47 nến, biên chính 10.4 giá, mà nhét đủ A→E. Đây là nhiễu, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range quá vụn — 47 nến đủ 5 phase — luật vi phạm: "khung quá thô / range quá vụn" (CHART_CASES), L9
- **Thuật toán gắn:** A=10 · B=6 · C=12 · D=14 · E=6 nến. Biên chính 4017.1–4027.5 = **10.4 giá (0.26% giá)**.
- **Đúng phải là:** không vẽ range. Một vùng cân bằng cần thời gian đàm phán; 6 nến Phase B không đủ để "xây nguyên nhân" cho bất cứ thứ gì. Giảng viên đã nhiều lần bắt học viên đổi khung để cấu trúc ra hình — ở đây ngược lại: M1 quá mịn nên một nhịp nghỉ 8 phút bị đọc thành cả một schematic.
- **Dấu hiệu quyết định trên chart:** nhìn toàn cảnh, đoạn 00:09–00:56 chỉ là một cái **gờ ngang giữa hai chân giảm** của cùng một đợt rơi 4041 → 3955. Move trước và Phase E sau nối liền nhau thành một xu hướng duy nhất.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range". Quyết định đó đang trả giá ở đây. Nếu không đặt sàn nến thì tối thiểu phải đặt **sàn theo cấu trúc**: Phase B phải là phase dài nhất (đang bị vi phạm) mới cho đóng range và đặt tên.

### 2. Thứ tự độ dài phase đảo ngược hoàn toàn — luật vi phạm: L9 + L8
- **Thuật toán gắn:** B = 6 nến (ngắn nhất), C = 12 nến, D = 14 nến (dài nhất).
- **Đúng phải là:** B dài nhất, C ngắn nhất. Ở đây C **gấp đôi** B, D gấp hơn hai lần B.
- **Dấu hiệu quyết định trên chart:** bảng phase trong phiếu số liệu, đọc thẳng.
- **Nghi phạm trong thuật toán:** không có kiểm tra hậu nghiệm nào về tỉ lệ phase trước khi chốt range. Hai luật tỉ lệ (L8, L9) đang là mô tả trong tài liệu chứ chưa là điều kiện trong code.

### 3. Nhãn SC nằm NGOÀI range, trước cả nến mở range — luật vi phạm: L3 (biên chính = mức climax), mục 9 (nhãn sai vị trí)
- **Thuật toán gắn:** SC dán tại **00:06** giá 4018.2 (VSA 4.47x), trong khi range bắt đầu **00:09** và mức climax = **4017.1** (nến 00:09).
- **Đúng phải là:** nhãn climax phải nằm trong cụm climax kể từ nến mở range. 00:06 là **3 nến trước** khi range tồn tại — trên ảnh thấy rõ chấm SC nằm bên trái vạch tím "Phase A".
- **Dấu hiệu quyết định trên chart:** 00:06 có low 4018.2, cao hơn mức biên chính dưới 4017.1 đúng 1.1 giá; nhãn treo lơ lửng phía trên đường biên nó lẽ ra phải đánh dấu.
- **Nghi phạm trong thuật toán:** sửa #4 của v7 ("kẹp nhãn cụm climax theo nến mở range cố định") **chưa kín cạnh dưới** — mới kẹp trần (start+8) mà chưa kẹp sàn (không được nhỏ hơn start).

### 4. LPSY[C] nằm giữa range, không phải test biên — luật vi phạm: L8
- **Thuật toán gắn:** LPSY[C] 00:25 @ 4022.6, VSA 0.51x. Trung điểm range = 4022.3.
- **Đúng phải là:** Phase C là tín hiệu **đầu tiên** cho thấy giá ở biên này bắt đầu phá biên kia — nó phải sinh ra ở một biên. Một pivot đúng giữa range không nói được điều gì về ai đang thắng.
- **Nghi phạm trong thuật toán:** điều kiện "pivot phải trong range + đúng nửa range" chỉ chặn nửa sai, không đòi pivot **tiệm cận biên**. Nên thêm ràng buộc: pivot cách biên tương ứng ≤ 25-30% chiều cao range.

### 5. Phase E cắt sớm ngay trước cú rơi thật — luật vi phạm: L10
- **Thuật toán gắn:** E = 6 nến, range đóng 00:56 tại ~4005.
- **Đúng phải là:** Phase E là lúc giá **rời range đi tìm vùng giá mới**. Cú rơi thật xảy ra ngay sau đó: 01:00–01:05 giá sụp thẳng xuống 3955 kèm cây volume lớn nhất toàn ảnh.
- **Dấu hiệu quyết định trên chart:** cột volume vàng khổng lồ ở ~01:03 nằm **ngoài** khung range đã đóng.
- **Nghi phạm trong thuật toán:** đích Phase E = 1.0× chiều cao biên chính. Biên chính chỉ 10.4 giá nên đích đạt được chỉ sau vài nến. Đích Phase E nên có sàn tuyệt đối theo ATR khi range quá hẹp.

## Đạt
- **ST[A] chuẩn nhất trong cả lô này:** 4018.3 so climax 4017.1 — test lại **đúng vùng climax**, hồi 0.88 khoảng AR↔climax (L2).
- **Nhãn SOW đặt đúng cây phá thật:** 00:37, VSA 6.90x, đóng cửa 4010.1 vượt hẳn biên phụ dưới 4016.1 (L3, mục 8).
- **Tên range đúng:** SC + phá xuống thật = Tái phân phối (L4).
- **Chú thích nỗ lực/kết quả đọc đúng dấu** (er=0.31 → "HIỆU QUẢ") — lỗi hard-code v6 đã hết.
- **LPSY[D] đúng vai:** đỉnh nhịp hồi sau SOW, vẫn nằm dưới biên đã phá (L10).
