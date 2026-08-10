# Chấm bài #05 — Tái phân phối (RE-DIST) · 2026-03-18 13:16 → 2026-03-19 03:31 (143 nến M1)

**Điểm: 2/10** — hướng đọc (tái phân phối) đúng, nhưng cú SOW đáng lẽ phải bị **vô hiệu** theo chính spec, nhãn SC nằm sai phía range, Phase C dài gần bằng Phase B.

## Lỗi (nặng → nhẹ)

### 1. LPSY[D] nằm HẲN TRONG range — cú phá không giữ được ngoài biên nhưng vẫn được đặt tên — luật vi phạm: L10 + mục 7 câu 1 của chính spec
- **Thuật toán gắn:** SOW 4898.9 (20:16) → **LPSY[D] 4940.0** (01:40), rồi đặt tên range là "Tái phân phối".
- **Đúng phải là:** biên chính dưới = **4918.1**. Nhịp hồi lên 4940.0 đã lùi **21.9 giá = 219 tick** vào **trong** range — vượt xa ngưỡng "đóng cửa lùi hẳn qua biên chính = 30 tick". Theo mục 7 câu 1 của chính tài liệu, cú phá này phải bị **VÔ HIỆU**: hạ SOW xuống mSOW, trả dải phase về B, **không được đặt tên range**.
- **Dấu hiệu quyết định trên chart:** chấm tím LPSY[D] vẽ **bên trong khung range**, nằm cao hơn đường nét liền "bien CHINH duoi 4918.1" một khoảng rõ rệt bằng mắt thường.
- **Nghi phạm trong thuật toán:** kiểm tra vô hiệu chỉ chạy trong cửa sổ 25 nến sau SOW, và/hoặc chỉ xét nến **đóng cửa** lùi qua biên chứ không xét chính pivot LPS[D] mà nó vừa gán. Hai nhánh này đang mâu thuẫn: một nhánh gọi 4940 là "retest hợp lệ", nhánh kia lẽ ra phải gọi nó là "lùi hẳn vào trong". Sửa: điều kiện vô hiệu phải chạy trên **chính điểm LPS[D]/LPSY[D]** trước khi gán nhãn.

### 2. Nhãn SC nằm ngoài range và ở SAI PHÍA — luật vi phạm: L3 + THEORY §3.3
- **Thuật toán gắn:** SC tại **12:43**, giá **4953.9** (VSA 2.26x). Mức climax thật = **4918.1** (biên chính dưới).
- **Đúng phải là:** nhãn SC phải nằm tại đáy 4918.1. 4953.9 nằm ở **69% chiều cao range**, tức nhãn "cao trào **bán**" đang ngồi gần biên **trên** — sai phía hoàn toàn, lệch 35.8 giá.
- **Dấu hiệu quyết định trên chart:** chấm SC vẽ bên trái khung, ở tầm giá ngang với vùng mSOS/LPSY[C], trong khi biên dưới nằm thấp hơn nhiều.
- **Nghi phạm:** lặp lại lỗi #4 của lô này — nhãn climax được phép nhảy ngược về cây VSA cao nhất trước nến mở range. Đáng chú ý: cây VSA cao thật **3.61x nằm ở +4 (13:30)**, tức ngay trong cửa sổ cụm 8 nến xuôi — nếu chỉ quét xuôi thì nhãn đã đúng vùng. Bằng chứng trực tiếp cửa sổ đang quét **ngược**.

### 3. Nến mở range VSA 1.05x, biên độ 2.4 giá — không đủ tư cách climax — luật vi phạm: mục 3 spec
- **Thuật toán gắn:** climax 13:16, VSA **1.05x** (volume 3), biên độ 2.4 giá trên range cao 51.9 giá.
- **Đúng phải là:** ngưỡng của chính thuật toán là VSA ≥2.2x + biên độ ≥1.4× ATR20. Nến này không đạt vế volume.

### 4. Phase C = 34 nến, gần bằng Phase B = 57 nến, dài hơn Phase D — luật vi phạm: L8
- **Thuật toán gắn:** A=27 · B=57 · **C=34** · D=25 · **E=1**.
- **Đúng phải là:** C phải là phase ngắn nhất. Ở đây C dài hơn cả A lẫn D, chiếm 24% cả range.
- **Nghi phạm:** cửa sổ gán ngược Phase C nới lên 0.8× Phase B (sửa #3 v7) → 0.8×57 ≈ 46 nến, cho phép LPSY[C] lùi rất xa. Cùng nguyên nhân với bài #03. Cần trần tuyệt đối cho độ dài Phase C.

### 5. Phase E dài đúng 1 nến — luật vi phạm: L10, lỗi J của v5 tái xuất
- **Thuật toán gắn:** E = 03-19 03:31 → 03:31 = **1 nến**.
- **Đúng phải là:** trên ảnh, sau khi range đóng giá còn rơi liền một mạch từ 4918 xuống **4809** — nguyên đoạn đó mới là Phase E.
- **Nghi phạm:** vá lỗi J ở v5 đã cho Phase E độ dài thật ở phần lớn ca, nhưng ca này rơi lại về đúng 1 nến — nhiều khả năng do Phase D chiếm hết cửa sổ 25 nến rồi Phase E chỉ còn nến cuối.

### 6. mSOS gán trên nến VSA 0.54x — luật vi phạm: mục 8, sửa #5 v7 chưa ăn
- **Thuật toán gắn:** mSOS 4978.0, **VSA 0.54x**, thân 0.00.
- **Đúng phải là:** quét lại lấy nến VSA cao nhất trong đoạn thăm dò. Chưa vá — giống mSOW bài #03 (0.57x).

### 7. LPSY[C] 4971.0 nằm ngoài biên chính trên 4970.0, và chồng nhãn với mSOS — lỗi vai + lỗi trình bày
- Cùng lỗi với bài #03: pivot Phase C phải nằm **trong** range; điểm vượt biên trên rồi rơi là **UT**, không phải LPSY. Trên ảnh hai nhãn `LPSY[C]` và `mSOS` đè lên nhau, khó đọc (lỗi trình bày).

## Đạt
- **Tên range (L4):** origin SC + phá xuống = Tái phân phối — đúng bảng 4 pattern **về hướng**; giá sau đó rơi tiếp xuống 4809 xác nhận đọc đúng chiều. (Nhưng theo lỗi 1, range này lẽ ra chưa được đặt tên.)
- **ST[A] hồi đủ sâu:** 4937.0, hồi 33/51.9 = 0.64× khoảng AR↔climax — qua ngưỡng 0.4 mới. Tuy vậy vị trí 36% chiều cao vẫn hơi lửng so với mức climax 4918.1.
- **SOW là cây thật:** VSA 4.00x, thân 0.65, đóng dưới biên chính — nhãn đặt đúng cây phá.
- **Biên (L3):** đúng 1 biên phụ trên (4978.0), tỷ lệ 1.15x, do đúng cực trị xa nhất tạo ra; mSOS vượt biên chính 80 tick (> ngưỡng 30 tick mới).
- Chú thích er đã đổi theo dấu (er=0.32 → "hiệu quả"), không còn hard-code "hấp thụ NGHI VẤN".
- **SOT phía trên n=3 (SOT thật), tỷ lệ thrust 0.21, volume 0.60 = cạn kiệt** — đọc đúng: lực đẩy lên rút ngắn dần trước khi cấu trúc phá xuống.
