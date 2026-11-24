# Chấm Bid/Ask cho NQ (2026-11-24)

Câu hỏi: bộ số chấm Bid/Ask (2,8 × trung vị, lớn nhất trong ±4 tick, che chấm xanh cách chấm đỏ ≤ 6 tick, sàn 9) được fit trên vàng GC. Đem sang NQ thì có cần đổi không, và đổi thế nào cho giống chart của CORVEN.

Kết luận: **cần đổi**. Mã NQ/MNQ giờ tự dùng **3,5 × trung vị, ±8 tick, che 12 tick, sàn 9** (ô cài đặt "Mã NQ/MNQ tự dùng bộ số Nasdaq", mặc định bật). Mã khác giữ nguyên. Đây là khớp **mật độ hiển thị**, không phải lợi thế đã kiểm định.

## 1. Dữ liệu

- NQ: `fp_NQZ26_XCME_Time_20260826-20261124_90d.csv`. NQZ26 chỉ thành hợp đồng chính từ 14/09 (trước đó khoảng 1.500 hợp đồng/ngày), nên đo từ 14/09: 71.047 nến M1.
- GC: `fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv`, 87.362 nến M1.
- Chart CORVEN: Meet 07/11, phút 2:45 đến 10:30 là **NQZ26 M1 trên Sierra** (ngày 06/11, giờ trên chart là UTC+7). Trích từ video 15 giây một khung, 31 khung, giữ 25 khung khớp nến tốt (sai lệch ≤ 2,5 px): **534 nến M1, 1.205 chấm** (480 đỏ, 442 xanh, 283 tím). Phần GC lấy từ đo cũ: 580 nến M1, 885 chấm.

## 2. Vì sao bộ GC không hợp với NQ

| M5 (trung vị) | GC | NQ |
|---|---|---|
| Biên độ nến (tick) | 39 | 104 |
| Số mức giá có giao dịch / nến | 38 | 101 |
| Volume trung vị mỗi mức | 7,5 | 8,0 |

Nến NQ rộng gấp khoảng 2,7 lần tính theo tick, còn volume mỗi mức gần bằng GC. Cửa sổ ±4 tick vì vậy chỉ phủ một phần nhỏ của nến NQ, nên NQ ra **1,61 chấm/nến M5, gần gấp đôi GC (0,84)**.

## 3. Mật độ chấm theo bộ số (`grid.py`)

| | M5 chấm/nến (đỏ / xanh) | M1 chấm/nến |
|---|---|---|
| GC, bộ GC | 0,84 (0,53 / 0,31) | 0,46 |
| NQ, bộ GC | 1,61 (1,04 / 0,57) | 0,79 |
| NQ, 2,8 / ±8 / che 12 | 1,30 | 0,68 |
| **NQ, 3,5 / ±8 / che 12** | **0,82 (0,51 / 0,31)** | **0,47** |

Theo phiên (M5, giờ UTC, `session.py`): GC 0,83 / 0,95 / 0,74 (Á / Âu / Mỹ), NQ bộ mới 0,63 / 0,96 / 0,97.

## 4. So với chart NQ của CORVEN (`corven_nq_extract.py`, `corven_nq_compare.py`)

Chấm khớp khi cùng nến, cùng màu (tím khớp cả xanh lẫn đỏ), cách ≤ 3 tick.

| | Chấm/nến M1 | Mình / CORVEN | Khớp vị trí (recall / precision) |
|---|---|---|---|
| GC, CORVEN | 1,53 | | |
| GC, bộ GC | 0,57 | 0,37 | 0,46 / 0,98 |
| NQ, CORVEN | 2,26 | | |
| NQ, bộ GC | 1,09 | 0,48 | 0,30 / 0,50 |
| **NQ, bộ Nasdaq** | **0,82** | **0,36** | 0,23 / 0,50 |

Cách đọc:
- CORVEN tự hiện nhiều chấm hơn trên NQ (2,26 so với 1,53 trên GC, gấp 1,48 lần). Bộ Nasdaq giữ đúng tỉ lệ đó: trên cùng các nến, mình ra 0,82 chấm trên NQ so với 0,57 trên GC (gấp 1,44 lần), tức mình/CORVEN là 0,36 trên NQ và 0,37 trên GC. Bộ GC thì lệch (0,48).
- **Vị trí khớp kém hơn hẳn GC** (precision 0,50 so với 0,98), với **cả hai bộ số**. Lý do đo được: chart NQ của CORVEN **gộp 8 tick (2,0 điểm) thành một hàng**. Giá của các chấm CORVEN dồn về lưới 8 tick (độ tập trung pha 0,61 với chu kỳ 8 tick, 0,30 với 4 tick là bội, gần 0 với 5, 10, 16 tick). Indicator đọc từng tick nên không thể khớp vị trí từng chấm với chart gộp hàng. Thử chạy luật trên hàng 8 tick (`rows_test.py`) cũng chỉ đạt F1 0,58 với luật rất lỏng, precision tối đa khoảng 0,77, nên chưa đổi indicator sang gộp hàng.
- Mức ngẫu nhiên để so: dịch chấm của mình ngẫu nhiên ±30 tick thì precision 0,25 (cách ≤ 4 tick). Precision 0,55 ở cùng khoảng cách nghĩa là chấm của mình vẫn hay nằm gần chấm CORVEN, chỉ không trùng từng tick.

## 4b. Tự nới theo khung (`tf_scale.py`, `tf_csv.py`)

Cửa sổ ±8 cố định làm khung lớn dày chấm: M15 1,45, M30 2,40, H1 2,66 chấm/nến (vàng GC: 1,11 / 1,34 / 1,54). Nến NQ càng lớn càng rộng (biên độ TB: M1 47, M5 113, M15 203, M30 303, H1 439 tick), nên cửa sổ nới theo biên độ:
**w = max(8, làm tròn(biên độ TB 20 nến trước / 14))**, che giữ 12 tick, 3,5 × trung vị, sàn 9.

| Chấm/nến (đỏ / xanh) | M1 | M5 | M15 | M30 | H1 |
|---|---|---|---|---|---|
| GC, bộ GC | 0,46 | 0,84 | 1,11 (0,70/0,41) | 1,34 | 1,54 |
| NQ, ±8 cố định | 0,47 | 0,82 | 1,45 (1,02/0,43) | 2,40 | 2,66 |
| **NQ, tự nới /14, che 12** | **0,47** | **0,78** | **1,19 (0,76/0,42)** | **1,67** | **1,54** |
| NQ, tự nới /14, che 1,5 × w | 0,47 | 0,76 | 1,08 (0,76/0,31) | 1,41 | 1,23 |

Che 1,5 × w xóa quá nhiều chấm xanh (tỉ lệ đỏ 70–79% so với GC 63–65%), nên giữ che 12. C# = Python (`Golden.dll stophunt --tick 0.25 --symbol NQZ26 --levels <tf_csv>`): M1 33.492 (19.653 + 13.839), M5 11.105 (6.716 + 4.389), M15 5.628 (3.618 + 2.010), H1 1.823 (1.141 + 682). M1 chỉ 6,9% nến có cửa sổ > 8.

## 5. Big Trade (vòng mờ) trên NQ

Giữ ngưỡng **10 hợp đồng**. Nhật ký lệnh đơn sống của NQ mới có 18 nến M1 (24/11, 12:01 đến 12:19 UTC, trước giờ Mỹ): trung vị 1, phân vị 99 là 5, lớn nhất 13; ≥ 10 hợp đồng khoảng 0,11 lần mỗi nến M1 (GC 0,16). Quá ít để hiệu chỉnh. Một hợp đồng NQ (20 USD × 26.000 ≈ 520 nghìn USD) gần bằng một hợp đồng GC (100 oz × 4.100 ≈ 410 nghìn USD), nên cùng ngưỡng số hợp đồng là hợp lý. Chạy lại `../corven_m5_2026-11-18/bigtrade_threshold.py --log .../_NQZ26_XCME_Time_1Minute.csv` khi nhật ký đủ vài ngày.

## 6. Đối chiếu C# với Python

`perf/Golden` thêm `--tick` và `--symbol`. Trên toàn bộ file NQ (78.464 nến M1):

| | C# (`Golden.dll stophunt --tick 0.25 --symbol NQZ26`) | Python (`dots.py`) |
|---|---|---|
| Bộ Nasdaq | 33.958 (19.930 đỏ + 14.028 xanh) | 33.958 (19.930 + 14.028) |
| Bộ GC (không `--symbol`) | 56.297 (33.636 + 22.661) | 56.297 (33.636 + 22.661) |

Golden của vàng GC không đổi (`GOLDEN: KHOP HET`), vì dấu vân tay chỉ thêm phần Nasdaq khi mã là NQ/MNQ.

## Giới hạn

1. Chỉ một buổi CORVEN chiếu NQ (534 nến M1 của ngày 06/11), khung M1. Chưa có chart NQ M5 của CORVEN để so.
2. Chart CORVEN gộp hàng 8 tick, indicator xét từng tick, nên chỉ so được mật độ, không khớp được từng chấm.
3. MNQ dùng chung bộ Nasdaq nhưng chưa đo riêng (MNQ có nhiều hợp đồng nhỏ hơn, sàn 9 có thể cần khác).

## Chạy lại

```bash
python load.py                    # sinh F_/S_{GC,NQ}_m{1,5}.pkl (không commit)
python grid.py; python session.py
python corven_nq_extract.py --img <thư mục ảnh 15 giây/khung trích từ video Meet 07/11>
python corven_nq_compare.py; python rows_test.py
```
