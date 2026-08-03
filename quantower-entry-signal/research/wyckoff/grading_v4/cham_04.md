# Chấm bài #04 — Phân phối (DIST) · 2026-04-02 14:35 → 2026-04-05 22:50 (265 nến M1)

**Điểm: 4/10** — Khung range đọc được và **hướng phá đúng** (giá xuống 4663.5 sau SOW). Nhưng climax
gán không đúng đỉnh, **nhãn AR lệch mức biên chính 10.2 giá**, và Phase C thực chất là **kỳ nghỉ cuối
tuần**. Sửa nhãn + sửa cách đếm cửa sổ.

## Lỗi (nặng → nhẹ)

### 1. BCLX gán không phải đỉnh — luật vi phạm: L1
- **Thuật toán gắn:** BCLX = 4746.1 tại 14:35 (VSA 3.45x, 15 hợp đồng).
- **Đúng phải là:** đỉnh thật là **4762.2 lúc 14:43** — **8 nến sau** nhãn, cao hơn **16.1 giá**. Hơn
  nữa nến **+1 (14:36)** có **39 hợp đồng, VSA 6.61x** — nỗ lực gấp 2.6 lần cây được gọi climax.
  Cây BCLX thật là nến 14:36-14:43, không phải 14:35.
- **Dấu hiệu quyết định trên chart:** biên phụ trên = 4762.2; cụm nến cao nhất nằm **bên phải** nhãn
  BCLX, chạm nét đứt. Trên panel khối lượng, cột cao nhất vùng đó cũng nằm bên phải nhãn.
- **Nghi phạm trong thuật toán:** giống #02/#03 — nến đầu tiên thoả `range ≥ 1.4×ATR` + `VSA ≥ 2.2x`
  là chốt ngay, không chờ hết chùm climax. **Đây là lỗi hệ thống, xuất hiện ở 3/5 bài.**

### 2. Nhãn AR không trùng mức biên chính dưới — luật vi phạm: L3
- **Thuật toán gắn:** nhãn AR = **4715.0** @15:57; biên chính dưới vẽ tại **4704.8**.
- **Đúng phải là:** L3 nói thẳng "biên chính = mức climax **+ mức AR**". Hai số này phải bằng nhau.
  Đáy thật của nhịp phản ứng là **4704.8 @16:20** — biên vẽ đúng, **nhãn thì bị bỏ lại** ở cái đáy nông
  hơn 23 phút trước đó.
- **Dấu hiệu quyết định trên chart:** trên ảnh chấm AR xanh nằm **cao hơn hẳn** đường "bien CHINH duoi
  4704.8"; đọc dữ liệu thì cực trị của khoảng AR→ST[A] là 4704.8 @16:20. Lệch **10.2 giá = 25% chiều
  cao range**. Thêm nữa nến tại nhãn AR có VSA 0.43x và **thân 0.00** — một cây doji không khối lượng,
  không đủ tư cách là "cú bật ngược thật".
- **Nghi phạm trong thuật toán:** §4.1 có câu "AR được dời tới cực trị mới" nhưng rõ ràng chỉ **mức
  biên** được dời, còn **bản ghi sự kiện AR** không được cập nhật theo. Đây là bug đồng bộ, sửa được
  ngay: khi dời AR thì phải ghi lại cả `events['AR'].i` và `.price`.

### 3. Phase C = trọn kỳ nghỉ cuối tuần; LPSY[C] cũ 3 ngày — luật vi phạm: L8
- **Thuật toán gắn:** Phase C = 53 nến, 04-02 19:08 → 04-05 22:11; LPSY[C] = 4742.1 @04-02 19:08.
- **Đúng phải là:** Phase C là phase **ngắn nhất** và LPS/LPSY[C] là **nhịp test cuối ngay trước cú
  phá**. Ở đây "nhịp test cuối" nằm cách cú SOW **3 ngày**.
- **Dấu hiệu quyết định trên chart:** trong khoảng Phase C có một khe **4381 phút (73 giờ)** giữa
  04-02 20:59 và 04-05 22:00 — thị trường đóng cửa cuối tuần. Trên ảnh, trục thời gian nhảy từ
  04-02 19:59 sang 04-05 22:04 mà dải Phase C vẫn vẽ liền một mạch.
- **Nghi phạm trong thuật toán:** cửa sổ "gán ngược Phase C: nhìn lại **60 nến**" (mục 6) đếm bằng
  **số nến**. 60 nến M1 ở đây = 3 ngày lịch. Đây đúng là điểm nghi ngờ số 8 mà chính tài liệu thuật
  toán đã tự nêu — **nay đã có bằng chứng**. Phải đổi mọi cửa sổ (60 / 120 / 25 / 40 nến) sang **giới
  hạn thời gian thực**, và không cho range bắc qua khe > N phút.

### 4. Nhãn DA ghi Phase B nhưng thời điểm nằm trong Phase C — *bảng phase tự mâu thuẫn*
- **Thuật toán gắn:** DA = 4702.5 @04-05 22:00, cột Phase ghi **B**. Nhưng bảng phase ghi Phase C chạy
  tới **22:11**, Phase D bắt đầu **22:12**.
- **Đúng phải là:** một sự kiện phải nằm trong đúng dải phase của nó. Trên ảnh chấm DA nằm **bên trái**
  vạch tím Phase D, tức trong dải Phase C, nhưng nhãn lại nói Phase B.
- **Nghi phạm trong thuật toán:** DA/UA/UT được gán `phase` theo **trạng thái máy tại thời điểm đó**,
  trong khi dải phase xuất ra bảng lại được **gán ngược** (Phase C dời về 19:08 sau khi có SOW). Hai
  nguồn sự thật khác nhau → phải gán lại phase cho mọi event **sau khi** chốt dải phase cuối cùng.

### 5. ST[A] dừng 14.4 giá trước climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] = 4731.7 @16:40.
- **Đúng phải là:** ST[A] phải là cú quay về **vùng climax** và bị chặn ở đó. 4731.7 còn cách mức
  BCLX 4746.1 tới **14.4 giá = 35% chiều cao range** — đây là dạng "ngọ nguậy giữa range" mà giảng viên
  bắt lỗi. (Cùng lỗi, nhẹ hơn, so với bài #01.)
- **Nghi phạm trong thuật toán:** ngưỡng ST[A] tính theo **phần đã hồi (≥40%)** thay vì **phần còn
  lại tới mức climax** — sửa như đã ghi ở bài #01.

### 6. Phase A dài hơn Phase B — luật vi phạm: L9
- A=107 · B=80 · C=53 · D=26. Phase B phải là phase dài nhất. Cùng gốc nguyên nhân với #01/#02/#03:
  đoạn climax → AR (107 nến) bị gộp hết vào Phase A vì giữa climax và ST[A] thuật toán không được gắn
  nhãn nào.

## Đạt
- **L1 (một nửa)** — có MOVE tăng thật: 103.6 giá / 70 nến / hiệu suất 0.38; range đúng là mở ở nơi
  move bị chặn.
- **L3 (biên phụ)** — mỗi bên đúng **1** biên phụ (4762.2 trên, 4702.5 dưới), đều là cực trị xa nhất,
  không spam. Đây là bài làm biên phụ tốt nhất trong 5 bài.
- **L3 (SOS/SOW mạnh)** — SOW 4691.5 đóng cửa **bứt qua** biên phụ dưới 4702.5, đúng yêu cầu "SOW mạnh
  phải qua biên phụ" — bài **duy nhất trong 5 bài** kiểm được điều kiện này một cách không vòng tròn
  (biên phụ dưới do cú DA tạo trước đó, không phải do chính cây SOW).
- **L4** — BCLX + phá xuống = Phân phối, tên đúng; và kết quả đúng: giá xuống **4663.5 @04-06 00:28**
  (−28 giá dưới SOW).
- **L7** — LPSY[C] và DA mỗi cái một điểm.

## Cần hỏi người học
- Range bắc qua **cuối tuần / khe 73 giờ** thì nên **cắt range tại khe** (mở range mới sau khi thị
  trường mở lại) hay **cho phép nối liền**? Lý thuyết Wyckoff không bàn tới khe phiên; đây là quyết
  định của người học và nó ảnh hưởng tới cả bài #01.
