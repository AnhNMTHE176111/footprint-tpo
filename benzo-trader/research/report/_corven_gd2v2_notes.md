## Nhận định vòng 2 (Opus) — số TRAIN, không phải kết luận

- **Không ô nào đạt (a).** Mọi ô đều có n ≥ 35 (đạt (c)), nhưng không ô nào có R TB ≥ C2 của chính ô. Gần nhất:
  `delta_mult = 3` (−0,24 so với C1 −0,24, C2 −0,05), `sl_buf_ticks = 5` (−0,15 so với C1 −0,15, C2 −0,02), `near_mbr = 1,5`
  (−0,18 so với C1 −0,19, C2 +0,07), `win_b = 4` (−0,24 so với C1 −0,23, C2 −0,04). Các ô này ngang C1 nhưng thua C2 0,04–0,25R.
- **`need_signs = 3` (hậu kiểm):** n = 38, R TB +0,01 [−0,46; 0,48] — ô duy nhất không âm, hơn C1 (−0,24) nhưng **thua C2 (+0,22)**
  ⇒ không đạt (a). KTC rộng gần ±0,5R.
- **C2 dao động mạnh giữa các ô** (−0,17 tới +0,22) dù chỉ đổi một tham số: C2 mỗi ô = trung bình 20 lệnh ngẫu nhiên quanh từng lệnh
  thật của ô đó, nên tập lệnh thật đổi thì C2 đổi theo (giờ/hướng/rủi ro khác). Với n 38–133 lệnh, C2 cũng có sai số cỡ ±0,1R —
  so sánh R TB với C2 ở mức chênh < 0,1R là trong vùng nhiễu.
- **Đổi tham số làm tệ đi rõ:** `si_run = 4` (−0,47), `b_from_exhausted` tắt (−0,39), `win_b = 2` (−0,35).
- **Phiên:** phiên Á **âm ở cả 12 ô** (−0,10 tới −0,73), phiên Mỹ âm ở cả 12 ô (−0,07 tới −0,63), phiên Âu ≥ 0 ở 10/12 ô
  (−0,31 tới +0,40). Rủi ro trung vị phiên Á ≈ 1,7–2,2 giá so với Mỹ ≈ 2,5–3,3 giá: phí 0,2 giá ăn ≈ 0,10R ở Á so với ≈ 0,07R
  ở Mỹ — chênh do phí chỉ ≈ 0,03–0,04R, **không giải thích** được khoảng cách Á −0,60 so với Âu +0,10 ở bộ gốc. Đây vẫn là
  hậu kiểm trên n 15–51 mỗi phiên/ô; plan 8.2 không cho lọc phiên ở v1.

## Ghi chú cách quét
- Plan 8.4 ghi "14 ô mới + bộ gốc" và "một bảng 15 dòng", nhưng danh sách giá trị in đậm chỉ có **11** ô (`si_run` 4 · `bubble_mult` 4 ·
  `delta_mult` 3 · `near_mbr` 0,5 / 1,5 · `win_b` 2 / 4 · `sl_buf_ticks` 2 / 5 · `b_from_exhausted` tắt · `need_signs` 3). Đã làm
  đúng 11 ô của danh sách (bảng 12 dòng); không tự thêm ô. Nếu Fable muốn thêm ô nào thì chỉ định.
- `bubble_mult` đổi cả ngưỡng bóng ③b và ngưỡng bóng ngược màu của ⛔ "nhịp quét stop" (cùng tham số trong code); bóng của trap ③e
  giữ cố định 3 × nền (plan ③e). `si_run` đổi cả vùng stacked làm mốc ② và dấu hiệu ③d (cùng một `Detect`).
- Bộ gốc chạy qua đường quét cho đúng 97 lệnh của vòng 1, từng nến vào và từng R trùng `_corven_trades.csv` (test `test_sweep_corven.py`).
