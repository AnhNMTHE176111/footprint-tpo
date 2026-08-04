# Chấm bài #30 — Tái phân phối (RE-DIST) · 2026-06-08 01:30 → 05:59 (269 nến M1)

**Điểm: 6/10** — Range vẽ được, hình đúng bản chất tái phân phối; phải sửa ST[A], hạ nhãn mSOS, và Phase E chốt quá non.

## Lỗi (nặng → nhẹ)

### 1. ST[A] không test lại vùng climax — nằm giữa range · luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 4343.4 (01:50), chốt Phase A tại đó.
- **Đúng phải là:** ST[A] phải là cú quay về **phía climax** rồi bị chặn lần nữa. 4343.4 nằm cách SC 4323.6 tới **19.8 giá = 66% chiều cao range**, tức nó chỉ hồi 10.0 giá (34%) từ AR 4353.4 xuống. Đây là một cái ngọ nguậy ngay dưới biên trên, không phải test đáy. Phase A **chưa xong** tại 01:50; cú test đáy thật (giá về sát 4325.7) chỉ xảy ra mãi trong Phase B.
- **Dấu hiệu quyết định trên chart:** trên ảnh nhãn ST[A] treo ngay sát cụm AR/mSOS ở nửa trên khung, cách hẳn đường `bien CHINH duoi 4323.6`. ST[A] chỉ cách AR đúng **5 nến** (01:45 → 01:50).
- **Nghi phạm trong thuật toán:** mục 4.2 — ST[A] là "swing pivot đầu tiên về phía climax, sàn 1.5× ATR", **không có sàn tối thiểu về khoảng cách tới mức climax**. Trần thì có (≤1.0× chiều cao) nhưng sàn thì không, nên một pivot hồi 34% cũng được nhận. Đây đúng lỗi Ca #19 nguồn 2.pdf ("Sai Phase A") và Ca #12 nguồn 7.pdf (nhầm thứ tự AR/ST).

### 2. mSOS gán cho một cú thọc 1.4 giá — quá nặng tay · luật vi phạm: L6 + mục 5.1 spec
- **Thuật toán gắn:** mSOS tại 4354.8 (02:00), VSA 2.61x — "đã phá hẳn ra ngoài rồi thu về".
- **Đúng phải là:** **UT[B]**. Cú này vượt biên chính trên 4353.4 chỉ **1.4 giá = 14 tick = 4.7% chiều cao range**, thân nến 0.61. Ngưỡng "mạnh" của spec là `max(15 tick, 15% chiều cao) HOẶC VSA ≥ 2.2x`; nó **không đạt** nhánh độ sâu (cần 4.5 giá) mà lọt qua chỉ nhờ nhánh VSA. Một cú thọc 14 tick không phải "phá hẳn ra ngoài".
- **Dấu hiệu quyết định trên chart:** nhãn mSOS nằm chồng gần như trùng lên đường biên chính trên; biên phụ trên 4354.8 chỉ cách biên chính 1.05x.
- **Nghi phạm trong thuật toán:** nhánh `HOẶC VSA ≥ 2.2x` trong điều kiện "cú rũ/thăm dò mạnh" (bảng tham số dòng "Cú rũ: sâu/mạnh tối thiểu"). Nên đổi thành **AND** với một sàn độ sâu tối thiểu, hoặc ít nhất bắt buộc đóng cửa ngoài biên.

### 3. Phase E chốt khi chỉ đạt 50% đích, rồi giá thu hẳn vào trong range · luật vi phạm: L10 + THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** Phase E 15 nến (05:45 → 05:59), range `completed`, tên **Tái phân phối**.
- **Đúng phải là:** đích Phase E là 4323.6 − 29.8 = **4293.8**; giá chỉ xuống tới ~4295–4297 rồi bật ngược. Ngay sau khi range đóng, giá leo lại **~4340**, tức **cao hơn biên chính dưới 4323.6 tới 16 giá** — cú SOW không giữ được bên ngoài biên. Theo L10 (D+E = CBR: phá → retest → **giữ** ngoài biên → đi tiếp) thì đây là SOW **thất bại**, phải hạ cấp thành mSOW và trả phase về B, không được đặt tên pattern.
- **Dấu hiệu quyết định trên chart:** nửa phải ảnh, sau vạch Phase E, nguyên một cụm nến xanh leo từ 4305 lên ~4340, nằm hẳn trên đường biên chính dưới.
- **Nghi phạm trong thuật toán:** "Đích Phase E tối thiểu (khi hết giờ) = 0.5× chiều cao" — ngưỡng này cho phép chốt E khi cú phá mới đi được nửa đường, và sau khi E chốt thì **không còn kiểm tra giá có quay vào range hay không**. Cần nối tiếp kiểm tra vô hiệu (lỗi F) sang cả Phase E.

### 4. Chỉ số bias báo "test CẢ HAI biên" trong khi Phase B không chạm biên nào · lỗi ĐO LƯỜNG (chỉ số v6)
- **Thuật toán gắn:** `bias = +0`, diễn giải "test CẢ HAI biên — ca THƯỜNG".
- **Đúng phải là:** trong 211 nến Phase B, đỉnh cao nhất chỉ tới ~4345.7 (cách biên trên 4353.4 **7.7 giá = 26% chiều cao**), đáy sâu nhất ~4325.7 (cách biên dưới 2.1 giá, ngoài dung sai chạm 10 tick). Tức **cả hai biên đều không được test lại lần nào** sau mSOS ở nến thứ 9 của Phase B. Trạng thái đúng là "không test biên nào" — một trạng thái mà chỉ số hiện chưa có, nên nó bị dồn nhầm vào ô "0 = test cả hai".
- **Nghi phạm trong thuật toán:** biến bias chỉ có 3 giá trị {+1, −1, 0} và 0 mang **hai nghĩa khác nhau** ("test cả hai" và "không test bên nào"). Cần tách thành 4 trạng thái, hoặc xuất kèm 2 số đếm lần chạm mỗi biên.

### 5. Diễn giải nhịp nỗ lực/kết quả ngược dấu · lỗi ĐO LƯỜNG (chỉ số v6)
- **Thuật toán gắn:** nhịp 04:07, effort 1.17x, result 1.85, er = 0.63 → "vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** er = 0.63 nghĩa là **kết quả lớn hơn nỗ lực** (result 1.85 ATR trên effort chỉ 1.17x) — đây là dấu hiệu di chuyển dễ dàng, đúng THEORY §6.3 ("nguồn cung nổi thấp, không cần volume cao"), **trái ngược** với "volume nhiều, kết quả ít". Câu diễn giải bị gán cứng: đối chiếu bài #32 (er = 4.79) và #34 (er = 0.24) đều nhận **cùng một câu** — chứng tỏ chuỗi mô tả không phụ thuộc giá trị er.
- **Nghi phạm trong thuật toán:** phần format chỉ số Phase B nối chuỗi tĩnh `"vung hap thu NGHI VAN (volume nhieu, ket qua it)"` thay vì phân nhánh theo er, và không có sàn effort tối thiểu để được gọi là "nỗ lực lớn".

## Đạt
- **Mục 1 (mở range):** MOVE giảm 43.3 giá / 62 nến / hiệu suất 0.35 đọc rõ trên ảnh; nến 01:30 VSA 3.55x, biên độ 14.9 giá, thân 0.85, và **đúng là đáy** của cả cửa sổ — climax chặn được move, không nằm giữa move.
- **Mục 3 (biên):** biên chính = climax 4323.6 + AR 4353.4, cố định suốt range; biên phụ trên duy nhất 4354.8; không có biên phụ dưới cho tới khi phá thật. Tỉ lệ 1.05x, không phình.
- **Mục 4 (tên range):** origin SC + phá thật xuống = **Tái phân phối** — đúng bảng L4, không xoá range vì "phá sai hướng".
- **Mục 5 (B dài nhất):** B 211 nến so với A 21 / C 12 / D 11 / E 15 — L9 thoả rõ ràng.
- **Mục 6 (C ngắn nhất):** C 12 nến, ngắn hơn mọi phase trừ D — L8 thoả; case khó gán ngược từ SOW về LPSY[C] 05:22 (đỉnh cuối trước cú sụp) là một chọn lựa hợp lý.
- **Mục 8 (khối lượng):** SOW 05:34 có **VSA 7.36x, thân 0.93** — cây phá thuyết phục nhất cả lô, thấy rõ bằng cột vàng cao nhất trên panel volume; LPSY[D] 0.79x (volume co lại khi test) đúng chiều Wyckoff.
