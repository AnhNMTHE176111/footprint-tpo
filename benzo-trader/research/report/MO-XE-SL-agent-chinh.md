# Mổ xẻ lệnh SL — agent chính tự chạy (2026-10-21, chỉ file 90d GCZ26)

Script: `_dissect.py`, `_dissect2.py`, `_dissect3.py` (chạy lại được). u = trung vị biên độ nến M1 50 nến.

## C · Fade cạnh (ô chính xuyên 2 tick, TP 2R): n=121, SL=88, WR 27%
- Khoảng SL trung vị 2,9 giá = 1,55u (không phải SL quá chặt kiểu nhật ký).
- 78% lệnh SL chết trong ≤10 nến; 28% trong ≤3 nến. 47% đã đi ≥0,5R rồi mới SL; 49% sau khi SL giá vẫn tới TP cũ trong 60 nến.
- **Phân loại SL: 72 PHÁ THẬT / 16 QUÉT RÂU** (phá thật = trong 20 nến sau SL có nến đóng ngoài cạnh ≥1u). Á 27/6, Âu 14/3, Mỹ 31/7.
  ⇒ Cơ chế thua: "phá hụt" ở giai đoạn này phần lớn là **nhịp dò đầu của cú phá thật**, không phải từ chối.
- Nới SL +0,5u: n=67, −0,13R; +1,0u: −0,44R. Vào limit tại cạnh: −0,31R. ⇒ không cứu được bằng SL/giá vào.
- Giờ 19:20–20:30 VN: 26 lệnh, 85% SL (Hệ thống nói "mở ảo", đúng).
- Nghịch đảo (stop ngoài râu phá hụt, theo cú phá, SL = cạnh lùi vào 0,5u, TP 2R): n=88, WR 40%, +0,06R; TRAIN −0,05 / TEST +0,18 ⇒ yếu, không bền.

## A · Phá hồi (V3 hết hạn 30 nến, TP 3R): n=20, SL=18
- SL trung vị 2,25 giá = 1,73u. 72% SL trong ≤10 nến; 33% đã đi ≥1R rồi SL; 28% SL rồi tới TP.
- TP 2R: WR 25%, vẫn âm. 13/20 lệnh ở phase Á/đêm muộn (0–12h VN) dùng VA hôm qua — không phải cơ chế phiên Mỹ của Hệ thống.
- ⇒ Vào ở cuối nhịp hồi U, nhưng hồi tiếp xuyên lại cạnh (cú phá không được chấp nhận). Bộ lọc M5 đóng ngoài chưa đủ là "acceptance".

## Hướng sửa agent chính giao (vòng 3, cuối)
Một bài kiểm tra cơ chế chung cho cả A và C, lấy từ **footprint từng mức giá** (`kernel.load_levels`) tại cực trị của râu dò:
- Tại 3 mức giá sát cực trị râu (≤ 3 tick): tổng volume ≥ 1,5× trung vị volume/mức của 50 nến, và **delta ngược chiều dò** (dò lên mà
  bid ≥ 2× ask ⇒ limit sell chặn; dò xuống gương ngược) ⇒ gọi là **"tường limit"** = cạnh giữ ⇒ **fade (C)**.
- Không có tường, hoặc delta cùng chiều dò ⇒ cạnh không giữ ⇒ **theo cú phá** (C-nghịch đảo / A).
Đây là cơ chế CORVEN "limit chặn sóng, market tạo move" áp đúng vào cạnh, không phải tham số mới vô nghĩa. Tham số tự do: ngưỡng volume ×{1,5; 2,0} × tỉ lệ delta {2; 3}.
