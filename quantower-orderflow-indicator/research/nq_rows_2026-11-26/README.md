# NQ như chart CORVEN — gom 8 tick (2 điểm) một hàng (2026-11-26)

Nguồn: ảnh chart Sierra NQ của CORVEN ngày 06/11 (14:39–16:27 giờ VN = UTC+7), dữ liệu
`data-export/data-footprint/fp_NQZ26_XCME_Time_20260826-20261124_90d.csv` (delta từng nến khớp số in trên chart CORVEN: 84, −34, −84, −14, 37 lúc 14:49–14:53).

## Stacked imbalance (si_rows.py)
10 vùng CORVEN đọc trên ảnh. Tỷ lệ 250%, chuỗi 3, khung 14:39–16:01:

| Hàng | Sàn | Số vùng | Trùng vùng CORVEN |
|---|---|---|---|
| 1 tick (cũ) | 5 | 7 | 0/10 |
| 4 tick | 1 | 61 | 9/10 |
| 8 tick, mốc lẻ (26999, 27001…) | 1 | 18 | **10/10** |

Vùng vẽ từ giá đầu hàng thấp nhất tới giá đầu hàng cao nhất (3 hàng = 4 điểm, như Sierra).

## Chấm (corven_nq_dots.py → 95 chấm CORVEN; nq_grid2.py, nq_g8.py)
Hàng 8 tick mốc lẻ, k 1,8 × trung vị mỗi hàng (TB 20 nến trước), lớn hơn hẳn hàng kề, không che, sàn 9: trùng 59, thừa 13, sót 36.
Bộ co dãn theo từng tick (mặc định cũ): trùng 46, thừa 52, sót 49. Đoạn nến ngắn 16:12–16:22: theo từng tick (nổ mọi mức giá) 19 chấm, hàng 8 tick 1 chấm.
C# = Python từng nến (parity.py, 105 nến, 0 lệch). NQ M1 78 ngày: 77.980 → 30.791 chấm.
