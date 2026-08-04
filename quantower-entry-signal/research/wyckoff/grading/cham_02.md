# Chấm bài #02 — Tái tích lũy (RE-ACC) · 2026-01-08 23:07 → 2026-01-09 15:23 (67 nến M1)

**Điểm: 6/10** — cấu trúc đọc đúng, tên range đúng, chỉ phải sửa cây climax và độ dài Phase E. Bài khá nhất trong lô 01–06.

## Lỗi (nặng → nhẹ)

### 1. Cây BCLX có biên độ 0.4 giá — không phải cao trào mua — luật vi phạm: THEORY §4.1 (BCLX = "volume **và** spread tăng rõ rệt")
- **Thuật toán gắn:** BCLX tại 2026-01-08 23:07, giá 4587.0, VSA 4.88×, **biên độ nến 0.4 giá**, volume 20.
- **Đúng phải là:** 0.4 giá là 1/47 chiều cao range (19.0 giá). Một cây như thế không thể là cao trào — nó chỉ là cây in giá cao nhất của phiên Á. Ứng viên climax thật nằm ở nến **-6 (18:29)**: volume **37**, VSA **12.13×**, biên độ **2.7 giá**, thân 0.59 — cây này mới có nỗ lực. Nếu cây 18:29 không phải cực trị giá thì đúng bài là gọi nó **PSY** và coi đợt tăng này kết thúc kiểu **cạn kiệt** (climax of exhaustion, THEORY §6.2) chứ không dán nhãn BCLX vào một cây 0.4 giá.
- **Dấu hiệu quyết định trên chart:** panel khối lượng — thanh vàng cao nhất trong vùng Phase A nằm ở 01-08 17:54 chứ không ở chỗ chấm BCLX; nến climax trên chart là một vạch ngang mảnh.
- **Nghi phạm trong thuật toán:** điều kiện "biên độ ≥ 1.4× TB 20 nến" tính TB trên chuỗi nến phiên Á toàn doji (0.0–0.4 giá) → ngưỡng tuyệt đối trôi xuống gần 0. Cần thêm sàn tương đối theo **chiều cao range/ATR ngày**, ví dụ biên độ cây climax ≥ 10% chiều cao biên chính.

### 2. Phase E chỉ 2 nến trong khi "kết quả" thật là +90 giá — luật vi phạm: L10
- **Thuật toán gắn:** Phase D 9 nến (14:10→15:00), Phase E 2 nến (15:09→15:23), range đóng.
- **Đúng phải là:** Phase E là giai đoạn "giá rời range đi tìm vùng giá mới". Trên chart giá tiếp tục leo từ ~4602 lên **4690+** trong 3 ngày sau đó (thấy rõ nửa phải ảnh, không có nhịp nào đóng cửa lùi lại 4587). Cắt Phase E ở 2 nến là bỏ mất toàn bộ kết quả.
- **Dấu hiệu quyết định trên chart:** biên chính trên 4587.0; sau SOS không có một nến nào đóng cửa lại xuống dưới mức đó cho tới hết ảnh. Đích Phase E (1.0× chiều cao = 4606) thực tế đã bị vượt xa.
- **Nghi phạm trong thuật toán:** ba điều kiện kết thúc Phase E (lùi hẳn vào biên / đi 2× chiều cao / 120 nến) — với range chỉ cao 19 giá, mốc "2× chiều cao = 38 giá" đạt gần như ngay, nên E vẫn ngắn; và mốc "lùi hẳn 30 tick" quá nhạy so với range 19 giá. Cả hai mốc nên tính theo **chiều cao range** thay vì tick tuyệt đối, hoặc cho Phase E chạy tới khi có range mới.

### 3. Phase C (14 nến) dài hơn Phase D (9) và gần bằng Phase B (27) — luật vi phạm: L8 (Phase C là phase ngắn nhất)
- Không phải lỗi nhãn: LPS[C] đặt đúng chỗ (xem mục Đạt). Nhưng Phase B chỉ 27 nến thì cả cấu trúc quá vụn để chia 5 phase — 67 nến M1 với đủ A→E là đúng cảnh báo "range quá vụn". Nhắc để hiệu chỉnh: hoặc gộp phần đầu Phase C vào B, hoặc nhận rằng đây là một range con và không nên chia đủ 5 phase.

## Đạt
- **Điều kiện mở range (L1):** có MOVE tăng thật 53.7 giá / 21 nến, hiệu suất 0.53 (cao nhất trong lô), cây climax là **đỉnh của cả cửa sổ** → nó đang chặn move, không nằm giữa move.
- **Phase A (L2):** đủ 3 lần đổi hướng và đúng chuẩn — BCLX 4587 → AR 4568 (biên dưới) → **ST[A] 4584** tức chỉ 3 giá dưới mức climax. Đây là ST[A] tốt nhất trong 6 bài: test đúng vùng climax, VSA co lại còn 0.29× (đúng THEORY §3.3: spread/volume giảm khi quay lại tiệm cận climax). Phase A kết thúc đúng tại ST[A].
- **Biên (L3):** biên chính = climax + AR, cố định; không có biên phụ nào (tỷ lệ 1.00×) — hoàn toàn hợp lệ theo L3 ("có thể không có biên phụ nào"), và đúng: trong cả Phase B giá không thò ra ngoài biên lần nào.
- **Tên range (L4):** origin BCLX + phá **lên** thật = **Tái tích lũy**. Đúng, và chart xác nhận (giá đi tiếp lên 4690). Đây chính là nhóm range mà bản v3 từng xoá oan.
- **Phase C (L8 case khó):** không có UTAD/Spring nào, thuật toán gán ngược từ SOS lấy nhịp test cuối cùng làm LPS[C] tại 4572.2 — **đúng cách xử lý** người học đã chốt ("có Phase D rồi mới xác định được Phase C").
- **Khối lượng (mục 8):** SOS tại 4601.9 có **VSA 8.14×, thân 0.89** — nỗ lực lớn, kết quả lớn, đúng định nghĩa SOS (spread + volume tăng). Đây là điểm mạnh nhất của bài.
- **Chỉ số Phase B mới — đo ĐÚNG bản chất:**
  - `Nhịp nỗ lực/kết quả cao nhất = nến 1736..1739 (01-09 12:54), effort 2.36×, er 0.07 → hấp thụ nghi vấn`: chỉ số này chỉ đúng vào **cùng cây LPS[C]** (VSA 4.44×, thân 1.00). Nghĩa là nó bắt được **hấp thụ dọc** (THEORY §8: nguồn cung tạo đáy mới nhưng cầu hấp thụ, nỗ lực lớn kết quả nhỏ) ngay trước SOS. Đây là cách đọc đúng, và nó **giải thích được** tại sao một LPS lại có volume cao thay vì thấp.
  - `SOT-up = chớm (n=2), thrust cuối/đầu 0.38, volume 1.11× → HẤP THỤ (volume ≥ nhịp đầu)`: đọc đúng theo THEORY §7 — rút ngắn lực đẩy **kèm** volume không giảm = nỗ lực lớn phần thưởng ít, phe đối lập sắp xuất hiện. Range sau đó phá **lên**, khớp với diễn giải "cung bị hấp thụ ở biên trên".
- Không có nhãn dư, không spam nhãn, không nhãn nào sai vai (LPS[C] trước SOS, không lẫn với LPS[D]).

## Cần hỏi người học
- Không có. Bài này chỉ cần vá cây climax và nhánh kết thúc Phase E.
