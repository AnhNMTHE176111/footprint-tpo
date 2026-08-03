# Chấm bài #02 — Phân phối (DIST) · 2026-03-31 01:19 → 11:12 (357 nến M1)

**Điểm: 2/10** — **Sai tên cấu trúc.** Climax gán không đúng đỉnh, và cú SOW dùng để đặt tên
"Phân phối" là một cú phá **THẤT BẠI** — giá quay vào range sau 5 nến rồi chạy lên +60 giá. Đây là
**Shakeout ở biên dưới của một TÁI TÍCH LUỸ**, không phải phân phối.

## Lỗi (nặng → nhẹ)

### 1. BCLX gán không phải đỉnh — climax không chặn move — luật vi phạm: L1
- **Thuật toán gắn:** BCLX = 4633.4 tại 01:19 (VSA 3.78x).
- **Đúng phải là:** đỉnh thật của đợt tăng là **4683.6 lúc 01:44** — sau nhãn BCLX **25 phút** và
  **cao hơn 50.2 giá**. Cây được gọi climax nằm **giữa** move, không chặn move.
- **Dấu hiệu quyết định trên chart:** biên phụ trên = 4683.6, và cực trị của toàn khoảng
  01:19 → 07:19 (AR) đúng là 4683.6 @01:44. Trên ảnh cụm nến cao nhất nằm **bên phải** nhãn BCLX.
  Hệ quả: biên chính 26.6 giá chỉ là **32%** của biên phụ 83.1 giá — đỉnh thật của cấu trúc bị bỏ
  ngoài biên chính.
- **Nghi phạm trong thuật toán:** điều kiện mở range chỉ kiểm climax là cực trị của **cửa sổ 240 nến
  phía sau**, không kiểm phía trước → nến đầu tiên của chùm climax thoả `range ≥ 1.4×ATR` và
  `VSA ≥ 2.2x` là bắn ngay, "first match wins". Cần **chờ chùm climax kết thúc** (vd N nến không tạo
  cực trị mới) rồi mới chốt nhãn tại **cực trị của cả chùm**.

### 2. SOW là cú phá THẤT BẠI → tên range sai — luật vi phạm: L5 + L4
- **Thuật toán gắn:** SOW 4600.6 @10:38 → Phase D → đóng range, tên **Phân phối**.
- **Đúng phải là:** đây là **Shakeout** (phá ra, lùng bùng ngoài rồi quay vào = một SOW **thất bại**),
  tức một sự kiện **Phase C ở biên dưới**. Range thật sau đó là **Tái tích luỹ** (BCLX + phá lên).
- **Dấu hiệu quyết định trên chart:** đáy sâu nhất 4593.5 @10:40 (2 nến sau SOW); nến 10:43 **đóng
  cửa 4608.2, trên biên chính dưới 4606.8** — tức chỉ **5 nến** ở ngoài. Rồi giá lên **4660.0 @12:09**
  và đỉnh khung ảnh 4691.9. Cú "phá xuống" ăn được đúng 6.2 giá dưới biên rồi bị hoàn toàn phủ định.
- **Nghi phạm trong thuật toán:** hai chỗ. (a) Kết cục B chỉ đòi **3 nến đóng cửa vượt biên ≥ 30 tick**
  — ba nến 4600.6 / 4598.7 / 4601.3 vượt biên **chính** 4606.8 vừa đủ, nên SOW được xác nhận trong
  khi giá chưa đi đâu cả. (b) Mục 7 "dù Phase E có đạt hay không, range vẫn ĐÓNG" — nên một cú phá bị
  đảo ngay lập tức vẫn được đóng sổ thành một cấu trúc hoàn tất. Cần điều kiện **giữ được ngoài biên
  trong K nến** hoặc **đi được ≥ x% chiều cao range** trước khi cho phép đặt tên range.

### 3. Phase A chiếm 62% range — luật vi phạm: L9
- **Thuật toán gắn:** A=222 · B=30+3=33 · C=22+55=77 · D=26 nến.
- **Đúng phải là:** Phase B dài nhất. Ở đây Phase A dài gấp **6.7 lần** Phase B.
- **Dấu hiệu quyết định trên chart:** trong 222 nến Phase A có **215 nến** là đoạn climax → AR
  (01:19 → 07:19) — tức Phase A đang ôm trọn cả nhịp giảm 4683.6 → 4606.8. Đoạn đó là **move**, không
  phải "giai đoạn xây vùng".
- **Nghi phạm trong thuật toán:** cửa sổ tìm AR được **chờ tới 300 nến** và giữa climax với ST[A]
  thuật toán **không được phép gắn nhãn nào** → mọi biến động nửa đầu range bị gộp vào Phase A. Đây
  cũng là gốc của lỗi #1: climax sai chỗ làm nhịp giảm thật rơi vào trong Phase A.

### 4. Năm nhãn dồn trong 43 phút, trong dải giá 4 giá — luật vi phạm: L7 + spec giãn cách 5 nến
- **Thuật toán gắn:** UT 4634.6 (08:06) → UTAD thất bại 4636.9 (08:08) → LPSY[C] 4637.2 (08:29) →
  UTAD 4638.4 (08:49) → LPSY[C] 4637.2 (09:04).
- **Đúng phải là:** **một** LPSY[C] duy nhất (L7 nói rõ: chỉ đánh 1 điểm). Và UT ↔ UTAD cách nhau
  **2 nến**, phá vỡ chính tham số "giãn cách tối thiểu giữa 2 sự kiện = 5 nến" của thuật toán.
- **Dấu hiệu quyết định trên chart:** trên ảnh 5 hộp nhãn chồng lên nhau quanh 4635-4638; nhãn UT bị
  UTAD (thất bại) che gần hết. Cả 5 nhãn nằm trong **4 giá** — đó là một lần test duy nhất, không
  phải 5 sự kiện.
- **Nghi phạm trong thuật toán:** LPSY[C] được phát lại mỗi lần vào Phase C mới (chuỗi C→B→C), không
  có bộ đếm "mỗi Phase C chỉ 1 LPSY[C]".

### 5. ST[A] có khối lượng ngang cây climax — luật vi phạm: THEORY §3.3 (ST) / mục 8
- **Thuật toán gắn:** ST[A] 4619.9, VSA **3.58x**.
- **Đúng phải là:** ST là cú test — spread và **volume phải CO LẠI** khi giá quay về vùng climax.
  3.58x so với climax 3.78x là gần bằng nhau: đó là một cây nỗ lực lớn, không phải test.
- **Dấu hiệu quyết định trên chart:** cột khối lượng cao nhất nửa đầu chart nằm đúng quanh 07:08-07:28,
  tức tại AR/ST[A]. Nỗ lực lớn mà giá chỉ nhích lên 13 giá = **nỗ lực lớn, kết quả nhỏ**, dấu hiệu
  thuật toán bỏ qua hoàn toàn.
- **Nghi phạm trong thuật toán:** ST[A] chỉ kiểm **hình học** (hồi ≥40% + 5 nến không cực trị mới),
  **không kiểm volume**. Nên thêm điều kiện `VSA(ST[A]) < VSA(climax)`.

### 6. Biên phụ dưới = đáy của chính cây SOW — luật vi phạm: L3
- Biên phụ dưới 4600.5 chính là `low` cây SOW 10:38. Trước cú phá đó không có biên phụ dưới nào, nên
  câu "SOW đóng cửa bứt qua biên phụ" không kiểm được. Cùng lỗi với bài #01 → **cần đóng băng biên phụ
  tại nến trước khi xét cú phá.**

## Đạt
- **L1 (một nửa)** — có MOVE tăng thật trước đó: 88.5 giá / 44 nến / hiệu suất 0.50.
- **L3 (một nửa)** — biên chính đúng bằng mức BCLX + mức AR và không bị kéo theo giá; biên phụ **trên**
  4683.6 đúng là cực trị xa nhất, mỗi bên chỉ 1 cái.
- **L4 (cơ chế)** — máy đã không xoá range khi phá "sai hướng", chỉ đổi tên. Cơ chế đúng, chỉ dữ liệu
  đầu vào (cú phá thất bại) làm tên sai.
- Chiều cao biên chính 26.6 giá (0.57%) — đúng tinh thần "vùng cân bằng hẹp".

## Cần hỏi người học
- Với một cú phá bị đảo trong 5 nến như thế này, muốn thuật toán **đổi tên range** (DIST → RE-ACC) hay
  **giữ range mở ở Phase B/C** rồi chờ cú phá sau? Lý thuyết cho cả hai đường; đây là quyết định thiết kế.
