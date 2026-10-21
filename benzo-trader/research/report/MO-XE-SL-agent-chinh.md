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

## Phần 2 — Đọc chart từng lệnh SL (agent chính, 2026-10-21, ảnh ở scratchpad/benzo/charts, script `_plot_sl.py`, `_plot_run.py`)

| Lệnh | Thấy gì trên chart | Lỗi gọi tên |
|---|---|---|
| A sell 28/09 21:14 (E = VAL Âu 4173,6) | Xu hướng giảm rõ từ 4190; vào 4171,5 (cách E 2 giá = ở lưng), SL 4175,4 ngay trên E; nến hồi +22 lúc 21:19 lên 4175,7 quét SL rồi giá rơi tới 4148 | **SL đặt sát cạnh, vào ở lưng** — ý tưởng đúng, mất lệnh 5R |
| A buy 13/08 19:52 (E = VAH Âu 4450,4) | 19:52 ngay sau mở COMEX; range 4441–4452 lình xình; "phá" là 1 nến M5 đóng trên VAH sau nến +169 dài; nến −116 kéo về 4449 → SL | **vào trong khung mở ảo 19:20–20:30**, cú phá sinh từ 1 nến dài |
| A sell 21/10 13:19 (E = VWAP ngày 4135,2) | Vào 4134,1; giá rơi tới 4131 (đã +1,3R), nến +60 kéo lại 4136,5 → SL; sau đó rơi tới 4128 (TP) | **SL sát cạnh**; be hòa ở +1R cứu được lệnh này |
| A sell 09/10 19:29 (E = VAL Âu 4209,6) | E nằm giữa vùng chop 1 giờ 4205–4210,5; 19:29 có nến +265 volume 980 lên 4216 → SL; rồi giá rơi 15 giá | **cạnh E không phải cạnh của cân bằng thật** (nằm giữa chop) + khung mở ảo |
| C sell 22/09 20:30 (E = VAH Âu 4370) | Giá rơi tới 4365 (+1,3R, TP 2R ở 4362,7 chưa chạm), rồi bật 16 giá lên 4381 → SL | **TP 2R xa hơn biên độ range**; 47% lệnh SL của C đã đi ≥0,5R |
| C buy 23/09 19:22 (E = VAL Âu 4348,4) | Trước đó nến +81 lên 4355 rồi rơi thẳng (−71, −54); fade ngay sau cú rơi hình V | **fade ngược đà ngay sau nến dài**; luật "3 nến sau nến dài nhất phiên" không bắt vì nến dài nhất phiên ở chỗ khác |
| C buy 20/10 20:06 (E = VAL Âu 4135,2) | Vào 4137 (cách E 1,8 giá = ở lưng), SL 4134,2 trong vùng nhiễu; giá xuống 4132,7 quét SL rồi lên 4143 (TP) | **vào ở lưng + SL trong nhiễu** |
| C sell 01/10 19:20 (E = VAH Âu 4208,4) | Đúng 19:20 mở COMEX; nến +137 lên 4211 → SL | **khung mở ảo** |
| B buy 04/08 10:33 (VWAP ngày) | Move giảm chậm −13/−18/−13 (|Δ| nhỏ, không phải nỗ lực bán); vào, ngay sau −30/−38 | **"giảm dần" bắt nhầm cú trôi chậm làm hấp thụ** — không có nỗ lực để mà thất bại |
| B sell 25/09 14:26 (VWAP ngày) | Phase Âu, cụm 3 nến nhỏ tại VWAP, nến +52 ngay sau → SL | như trên, cụm nhỏ = thiếu thanh khoản, không phải hấp thụ |

### Đo lại 4 cách sửa rút từ chart (trên toàn bộ lệnh C và A, TP 2R)
| Sửa | C (n≈146) | A (n=21) |
|---|---|---|
| Gốc | −0,27R | −0,37R |
| Dời SL về hòa ở +1R | −0,25 | −0,32 |
| Chỉ vào khi |giá vào − E| ≤ 1 giá (không ở lưng) | −0,36 (n=91) | −0,45 (n=14) |
| SL ngoài cạnh E ≥ 1u | −0,25 | −0,45 |
| Loại ≤3 nến sau nến dài nhất 20 nến | −0,24 | −0,30 |

⇒ **Không cách sửa kỹ thuật nào (SL, be, vị trí vào, lọc nến dài) đổi được dấu.** Các lệnh SL "đúng ý tưởng nhưng sai SL" có thật
(28/09, 21/10, 20/10) nhưng bị bù bởi các lệnh sai hướng. Lỗi gốc nằm ở **chỗ chọn cạnh**: VA Âu / VA hôm qua trong 65 phiên này
không phải cạnh cân bằng thật (giá chop quanh nó hoặc xuyên thẳng), nên "fade" lẫn "phá hồi" quanh nó đều ≈ ngẫu nhiên trừ chi phí.
Luật duy nhất có số ủng hộ: **không vào 19:20–20:30 VN** (C: −0,26 → −0,06).
