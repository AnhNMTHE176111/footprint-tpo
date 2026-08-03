# Chấm bài #03 — Tái phân phối (RE-DIST) · 2026-04-02 01:04 → 03:07 (115 nến M1)

**Điểm: 1/10** — **KHÔNG NÊN VẼ RANGE Ở ĐÂY.** Đây là một dòng thác giảm 4855 → 4712 trong 90 phút.
**99/100 nến** từ 01:20 tới hết range đóng cửa **dưới** biên chính dưới. Không có vùng đấu giá nào,
chỉ có một đoạn xu hướng bị cắt ngang rồi dán nhãn Phase A-D lên trên.

## Lỗi (nặng → nhẹ)

### 1. Không có vùng đấu giá — range vẽ trên một đoạn xu hướng — luật vi phạm: L1 / mục chấm 1
- **Thuật toán gắn:** range 4791.5 – 4829.7 (38.2 giá), Phase A 44 · B 27 · C 19 · D 26 nến.
- **Đúng phải là:** không mở range. Wyckoff yêu cầu "chuyển động trước đó **đã bị dừng lại** và có sự
  cân bằng tương đối giữa cung và cầu" (THEORY §3.1). Ở đây chuyển động không hề dừng.
- **Dấu hiệu quyết định trên chart:** đếm trên dữ liệu thật — từ 01:20 đến 03:07, **99 trong 100 nến
  đóng cửa dưới 4791.5**. Nghĩa là **72 trong 115 nến của "range"** nằm ngoài range. Trên ảnh, toàn bộ
  Phase B, C, D nằm hẳn dưới đường "bien CHINH duoi 4791.5"; hai đường cam kẹp đúng vào 40 giá đầu của
  một cú rơi 143 giá.
- **Nghi phạm trong thuật toán:** không có **điều kiện kiểm chứng "range còn sống"**. Sau khi Phase A
  chốt, thuật toán chỉ hỏi "giá có thò ra ngoài biên không" (mục 5) và mỗi lần thò thì nới biên phụ —
  nhưng **không bao giờ hỏi "giá đã ở ngoài biên bao lâu rồi"**. Cần guard: nếu > X% nến kể từ ST[A]
  đóng cửa ngoài biên chính → **huỷ range**, không phải gắn phase tiếp.

### 2. ST[A] nằm dưới biên chính dưới hơn cả một chiều cao range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] = 4748.8 (01:47), Phase A.
- **Đúng phải là:** ST[A] là lần giá **quay về vùng climax rồi bị chặn nhẹ lần nữa**. 4748.8 nằm
  **42.7 giá DƯỚI** climax 4791.5 — trong khi cả chiều cao range chỉ có **38.2 giá**. Tức ST[A] ở
  ngoài range hơn một tầm range. Đó không phải test, đó là cú phá vỡ.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] trên ảnh nằm thấp hơn đường cam dưới một khoảng lớn
  hơn khoảng cách giữa hai đường cam. Phase A đã hỏng ngay khi chốt → mọi phase sau đó vô nghĩa.
- **Nghi phạm trong thuật toán:** §4.2 chỉ đòi "hồi ≥ 40% chiều cao climax↔AR + 5 nến không cực trị
  mới" — **không có chặn trên**. Giá xuyên qua mức climax bao xa cũng vẫn được nhận là ST[A]. Phải
  thêm: nếu điểm ST[A] vượt mức climax quá (vd) 50% chiều cao range → đó là **SOW/Spring**, không phải
  ST[A]; range phải bị huỷ hoặc chuyển thẳng sang Phase C/D.

### 3. SOW không bứt qua biên phụ — cú phá thật đã xảy ra từ trong Phase A — luật vi phạm: L3
- **Thuật toán gắn:** SOW 4732.6 (02:34), VSA 1.45x → Phase D.
- **Đúng phải là:** L3 nói "SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua biên **PHỤ**". Biên phụ
  dưới là **4712.2**, làm lúc **01:32** — tức **62 phút TRƯỚC** cây SOW. SOW ở 4732.6 nằm **20.4 giá
  CAO HƠN** biên phụ: nó không bứt qua gì cả, chỉ là một nến giữa đường.
- **Dấu hiệu quyết định trên chart:** cực trị thấp nhất của cả khoảng 01:04 → 02:34 là 4712.2 @01:32
  (thấy rõ trên ảnh là cái râu dài chọc xuống sát nét đứt "bien phu duoi 4712.2"), xảy ra khi thuật
  toán còn đang ở **Phase A**. Thêm nữa VSA của SOW chỉ 1.45x — không có nỗ lực nào đi kèm.
- **Nghi phạm trong thuật toán:** điều kiện Kết cục B đo "vượt biên phụ ≥ 30 tick" nhưng vì Phase A/B
  chưa từng "theo dõi cú phá" ở đoạn 01:32, biên phụ và trạng thái máy lệch pha nhau.

### 4. AR là một cái râu 1 nến — luật vi phạm: THEORY §3.3 (AR) / L2
- **Thuật toán gắn:** AR = 4829.7 (01:11), VSA 4.28x, **thân/biên độ = 0.01**.
- **Đúng phải là:** AR là "sóng mua đẩy giá lên" — một cú bật ngược **thật**. Thân 0.01 nghĩa là nến
  mở và đóng gần trùng nhau: toàn bộ 4829.7 là **râu**. Cả biên trên của range vì thế được neo vào một
  cái râu.
- **Dấu hiệu quyết định trên chart:** chấm AR trên ảnh nằm ở đầu một cái râu mảnh, không có thân nến
  nào chạm tới đường "bien CHINH tren 4829.7".
- **Nghi phạm trong thuật toán:** cảnh báo "AR (yếu)" chỉ bắn khi AR **rơi vào 1-2 nến ngay sát
  climax** (§4.1); ở đây AR ở nến thứ 7 nên không bắn. Điều kiện nên đổi thành **kiểm thân nến** hoặc
  neo AR theo **giá đóng cửa** (Ca #5 nguồn 4.pdf: ranh giới phải neo giá đóng cửa, không neo bóng nến).

### 5. Nến được gọi climax không phải cực trị và không phải nến nỗ lực lớn nhất — luật vi phạm: L1
- **Thuật toán gắn:** SC = 4791.5 tại nến +0, VSA 4.40x.
- **Đúng phải là:** nến **-1** có VSA **7.09x** (28 hợp đồng, lớn hơn 22 của cây được gọi climax) và
  nến **+2** có đáy **4788.8**, thấp hơn 4791.5. Vậy cây climax vừa không phải nỗ lực lớn nhất, vừa
  không phải đáy.
- **Dấu hiệu quyết định trên chart:** cột khối lượng cao nhất của cả ảnh nằm khoảng 01:32 — giữa cú
  rơi, không phải ở nhãn SC.
- **Nghi phạm trong thuật toán:** cùng gốc với bài #02 — chốt climax tại nến đầu tiên thoả ngưỡng, không
  chờ hết chùm climax.

### 6. Không có Phase E, và sau SOW giá bật ngược 28 giá — *ghi nhận kết quả*
- Sau SOW, giá lên **4760.9 @03:24** (+28.3 giá so với SOW) trước khi đi tiếp. Range đóng ở Phase D
  đúng theo mục 7 của thuật toán, nhưng "kết quả" của cấu trúc thì rỗng.

## Đạt
- **L4 (tên gọi)** — move trước là giảm (SC) và hướng phá là xuống → Tái phân phối. Tên đúng theo bảng
  4 pattern, đây là phần logic duy nhất chạy đúng ở bài này.
- **L7** — LPSY[C] chỉ một điểm, không spam.
- **L8 (số nến)** — Phase C = 19 nến, đúng là phase ngắn nhất trong bài.

## Cần hỏi người học
- Không có. Bài này lý thuyết phân xử được dứt khoát: **không vẽ range.**
