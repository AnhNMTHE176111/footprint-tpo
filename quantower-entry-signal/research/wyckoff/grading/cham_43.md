# Chấm bài #43 — Tích lũy (ACC) · 2026-07-09 00:54 → 06:22 (328 nến M1)

**Điểm: 4/10** — Phần Phase C→E làm tốt nhất cả lô (LPS[C] volume co 0.11×, SOS VSA 8.08× vượt biên phụ, LPS[D] giữ ngoài biên). Nhưng Phase A chốt sau **14 nến** với AR chỉ cách climax 1 nến, làm biên chính chỉ **9.0 giá** trong một vùng đấu giá **26.4 giá** — hai nét liền nằm lọt giữa vùng, và cú Shakeout thật bị hạ thành mSOW.

## Lỗi (nặng → nhẹ)

### 1. Biên chính 9.0 giá là vô nghĩa với vùng giá 26.4 giá — L2, L3
- **Thuật toán gắn:** Phase A = **14 nến**; AR 01:01 tại 4088.2 (**1 nến** sau nhãn SC 01:00), biên chính 4079.2–4088.2 = **9.0 giá (0.22%)**; biên phụ 4065.9–4092.3 = **26.4 giá (2.93×)**.
- **Đúng phải là:** trên ảnh giá dao động **4065.9–4092.3** suốt 328 nến. Vùng cân bằng thật là **4076–4092**. AR đúng phải là đỉnh nhịp bật thật (~4091.7 lúc 02:14 hoặc 4092.3), không phải cái râu 01:01. Với AR = 4092 và climax = 4076–4079 thì biên chính mới bao được cấu trúc.
- **Dấu hiệu quyết định trên chart:** nến AR (01:01) có VSA 2.93× nhưng **thân 0.43** và nằm **1 nến** sau climax — chính spec gọi trường hợp này là "**AR (yếu)** — nhiều khả năng chỉ là râu nhiễu", nhưng cảnh báo đó *không đổi logic*. Hệ quả đo được: tỉ lệ biên phụ/biên chính **2.93×**, gần sát guard huỷ range 4.0×.
- **Nghi phạm trong thuật toán:** (a) AR = swing pivot xác nhận sau **5 nến** với sàn **1.5× ATR** — ATR quanh climax rất nhỏ (phiên Á, volume 3–45 lot) nên một râu 7.6 giá đủ vượt sàn; (b) nhãn "AR (yếu)" chỉ hiển thị mà không loại → nên biến nó thành điều kiện **loại thật**: AR cách climax < 3 nến ⇒ tiếp tục chờ pivot sau.

### 2. Shakeout thật bị hạ cấp thành mSOW → mất Phase C thật — L5, L8
- **Thuật toán gắn:** `mSOW` 04:44 tại **4065.9**, VSA 3.67×, thân 0.74; Phase C mở muộn tại LPS[C] 05:23 (gán ngược).
- **Đúng phải là:** cú 04:44 là **Shakeout** (phá xuống, lùng bùng ngoài một lúc, rồi quay lại — đúng định nghĩa L5), và nó **được xác nhận** vì sau đó giá đi hết sang biên đối diện rồi phá lên bằng SOS VSA 8.08×. Đây là **cú rũ duy nhất và sâu nhất** của range (thấp hơn biên chính dưới **13.3 giá = 148% chiều cao range**). Phase C phải neo từ 04:44.
- **Dấu hiệu quyết định trên chart:** 4065.9 là đáy tuyệt đối của cả 328 nến; panel volume có thanh vàng rõ tại 04:44; ngay sau đó là chuỗi nến xanh liên tục lên 4092.
- **Nghi phạm trong thuật toán:** vì biên chính dưới bị đặt **quá cao** (lỗi #1), giá nằm dưới 4079.2 gần **liên tục ~100 nến** (03:20–05:00). Nhánh theo dõi cú phá thấy "ở ngoài biên quá lâu" nhưng không thoả điều kiện SOW (không có 3 nến đóng vượt **biên phụ** + thân 45%) nên rơi vào giỏ mSOW. Tức lỗi #1 **gây ra** lỗi #2: sửa AR là sửa được cả hai.

### 3. mSOS 05:51 dư — cùng một cú phá bị gắn hai nhãn trái nghĩa — L5
- **Thuật toán gắn:** `mSOS` 05:51 tại 4092.3 (VSA 2.07×, "phá ra rồi thu hẳn vào") và `SOS` 06:00 tại 4108.5 (VSA 8.08×) — cách nhau **9 nến**.
- **Đúng phải là:** một cú thọc lên rồi 9 nến sau bùng nổ cùng hướng thì đó là **một** cú phá đang hình thành, không phải một cú thất bại rồi một cú thành công. Nhãn hợp cho 05:51 là **UT[B]** (hoặc bỏ hẳn, chỉ nới biên phụ) — gọi mSOS làm người đọc tưởng phe mua đã thua một lần.
- **Ghi chú timeline:** bảng ghi mSOS thuộc **Phase B** nhưng 05:51 nằm trong dải **Phase C** (05:23–05:59). Mâu thuẫn nội bộ, giống bài #40.

### 4. Phase A quá ngắn / Phase C dài hơn Phase D — L8, L9
- A **14** · B 255 · C **37** · D 12 · E 11. Phase B dài nhất: đúng. Nhưng Phase A 14 nến cho một range 328 nến là bất thường (chính là hệ quả lỗi #1), và C = 37 > D = 12 nên C không phải phase ngắn nhất.

### 5. Nhãn SC lệch mức biên 1.4 giá — trình bày
- Nhãn SC vẽ tại 01:00 giá **4080.6** (VSA 4.72×) còn mức biên chính dưới là **4079.2** (nến 00:54). Cơ chế tách nhãn/mức là hợp lệ, nhưng trên ảnh chấm SC nằm **trên** nét liền dưới, cùng với ST[A] nằm **dưới** nó — cụm ba mốc SC/AR/ST[A] chồng nhau trong 14 nến rất khó đọc.

### 6. Ba chỉ số Phase B mới
- **SOT phía dưới:** `SOT, n=3, thrust 0.12, volume 0.86 (cạn kiệt)` — **đo đúng bản chất**: đúng 3 nhịp đẩy xuống, nhịp cuối chỉ còn 12% lực với volume gần như không giảm. Theo THEORY §7 đây là biến thể "rút ngắn + volume vẫn lớn ⇒ đối lực sắp xuất hiện", và thực tế SOS nổ ra sau đó. Chỉ số này **báo đúng** ở bài này.
- **SOT phía trên:** `chớm, n=1, 0.00/0.00` — n=1, chưa đủ ngưỡng ≥3 của §7; tỉ lệ 0.00 = không tính được nhưng vẫn in trạng thái.
- **Nỗ lực/kết quả:** `effort=1.87x, result=2.00, er=0.94` → "hấp thụ NGHI VẤN (volume nhiều, kết quả ít)". er ≈ 1 nghĩa **nỗ lực và kết quả cân nhau** — không có gì nghi vấn. Câu diễn giải là hằng số dán cứng (giống #40, #41, #44).
- **Bias:** `+0` như cả lô.

## Đạt
- **Điều kiện mở range (L1):** MOVE giảm 17.4 giá / 39 nến / hiệu suất 0.37, climax VSA 2.69× **là đáy thật** của cửa sổ. Đúng.
- **Tên range (L4):** origin SC + phá lên thật ⇒ **Tích luỹ**. Đúng, và giá đi tiếp lên 4120 sau range (đúng L10 — Phase E tìm vùng giá mới thật).
- **Phase B dài nhất (L9):** 255/328 = 78%.
- **LPS[C] 05:23 — mốc gán tốt nhất cả lô:** VSA **0.11×** (gần như không giao dịch), giá 4078.3 sát biên dưới ⇒ đúng chuẩn **No Supply** của THEORY §6.4 (test cạn cung, volume co lại). Đây là cách một test *nên* trông như thế nào.
- **SOS neo đúng cây phá thật (L3):** 06:00, VSA **8.08×**, thân **0.93**, giá 4108.5 **vượt hẳn biên phụ trên 4092.3** — không chỉ qua biên chính. Đúng yêu cầu "SOS mạnh phải bứt qua biên phụ".
- **Phase D/E đúng CBR (L10):** LPS[D] 06:07 hồi về 4097.8 nhưng **giữ trên biên**, rồi Phase E 11 nến đi tiếp — đúng khuôn phá → retest giữ ngoài → đi tiếp.
- **Biên phụ (L3):** mỗi bên đúng 1, đều là cực trị xa nhất thật.
