# Kiệt sức (exhaustion): so với chart CORVEN và luật đề xuất (2026-11-26)

Chỉ đo **độ khớp hiển thị** với chart Sierra của CORVEN (vị trí và số lượng tam giác). Không sửa C#, không commit.

## 1. Đáp án CORVEN đã trích

| Mẫu | Nguồn | Số nến | Số dấu CORVEN |
|---|---|---|---|
| NQ_A | ảnh NQ M1 06/11 14:39–16:01 giờ VN (soát bằng mắt + pixel) | 83 | 8 (5 đỉnh, 3 đáy) |
| NQ_B | 3 khung Meet NQ M1 06/11 (17:26–18:55, 19:32–20:37, 20:26–21:30 giờ VN) | 208 | 24 (12 đỉnh, 12 đáy) |
| GC | 18 khung Meet GC M1 05–06/11 | 737 | 52 (30 đỉnh, 22 đáy) |
| GC_M5 | chart GC M5 18/11 (mẫu cũ, `../corven_m5_2026-11-18`) | 26 | 11 |

- Tam giác dò bằng mặt nạ màu (`tri.py`), quy đổi pixel → nến/giá bằng `../calib.json` (GC) và `nq_calib.json` (NQ, `nq_calib.py`), rồi soát từng tam giác trên tờ ảnh phóng to (110 ứng viên, bỏ 3 nét vẽ tay màu vàng). Ảnh soát: `dbg/*.png` (vạch xanh lá = đỉnh/đáy nến theo dữ liệu của mình, ô tím/xanh = tam giác dò được kèm giờ UTC).
- Dấu trùng nhau giữa các khung hình chồng thời gian: 14/14 nhất quán.
- File: `gt_marks.csv` (95 dấu), `gt_sides.csv` (mọi phía nến nhìn thấy, y = có dấu), `raw_marks.csv`, `raw_visible.csv`.
- Vị trí tam giác CORVEN neo theo **hàng giá** của chart (NQ: tâm tam giác cách mép trong của hàng cực trị 2,4–2,9 điểm; GC: 0,3–0,45 giá), không neo đúng đỉnh/đáy nến. Tam giác nằm sau thân nến nên râu quá ngắn thì bị thân che gần hết.
- CORVEN vẽ dấu đã bị quét **giống hệt** dấu còn hiệu lực (đỉnh NQ 15:03 bị nến 15:05 quét, vẫn vàng đặc). Bản của mình vẽ dấu đã quét mờ 35%.

## 2. Luật hiện tại so với CORVEN

Bản Python của luật hiện tại (`cur_rule.py`) khớp C# từng dấu trên các nến của mẫu (`cs_parity_current.py`: NQ 143 = 143, GC 118 = 118, lệch 0).

| Mẫu | CORVEN | Hiện tại: mình / trùng / thừa / sót | Đề xuất: mình / trùng / thừa / sót |
|---|---|---|---|
| NQ_A (83 nến) | 8 | 35 / 5 / 30 / 3 | 9 / 7 / 2 / 1 |
| NQ_B (208 nến) | 24 | 108 / 18 / 90 / 6 | 31 / 21 / 10 / 3 |
| GC M1 (737 nến) | 52 | 118 / 30 / 88 / 22 | 66 / 44 / 22 / 8 |
| GC M5 (26 nến) | 11 | 12 / 11 / 1 / 0 | 11 / 10 / 1 / 1 |
| Cộng | 95 | 273 / 64 / 209 / 31 | 117 / 82 / 35 / 13 |

Chi tiết từng dấu: `out_compare_marks.csv`, tóm tắt: `out_compare_summary.csv`.

## 3. Vì sao lệch

1. **Sai đơn vị.** CORVEN tính trên hàng giá của chart: NQ hàng 8 tick mốc điểm lẻ, GC M1 hàng 2 tick mốc lẻ (x,1–x,2 | x,3–x,4…). Quét cách gom hàng (`rowscan.py`): đúng lưới này F1 0,83; lệch mốc 1 tick hay đổi cỡ hàng tụt còn 0,36–0,72; theo từng tick 0,31 (NQ) và 0,47 (GC).
2. **Sai hình dạng điều kiện.** CORVEN đòi **đúng 3 hàng** sát cực trị, **từng hàng** đều nhỏ. 2 hàng: thừa gấp 4; 4 hàng: sót một nửa; lấy tổng thay vì từng hàng: kém hơn (`base_scan2.py`, `variants.py`). Luật hiện tại cộng 6 tick nên trên NQ chỉ soi 1,5 điểm.
3. **Thiếu điều kiện nến đủ volume.** Dấu CORVEN gần như không xuất hiện trên nến vắng: volume nến của mọi dấu ≥ 0,67 lần trung bình 20 nến trước (NQ ≥ 0,82), trong khi nửa số ứng viên "đuôi nhỏ" nằm dưới mức đó. Bỏ điều kiện này: thừa 151 thay vì 35.
4. Luật cũ fit trên 26 nến M5 nên trùng 11/11 ở đúng mẫu đó nhưng trên M1 ra nhiều gấp 2,3 lần (GC) đến 4,5 lần (NQ) số dấu CORVEN và vẫn sót 28–42%.

Cửa sổ nền 20 nến cho điểm cao nhất ở cả hai mã (5, 10, 30, 50, 100 đều thấp hơn, `base_scan.py`).

## 4. Các phương án đã đo (`variants.py` → `out_variants.csv`)

Cột = CORVEN/mình/trùng/thừa/sót; cột Tổng: trùng/thừa/sót, F1.

| # | Phương án | NQ_A | NQ_B | GC M1 | GC M5 | Tổng |
|---|---|---|---|---|---|---|
| 0 | Hiện tại | 8/35/5/30/3 | 24/108/18/90/6 | 52/118/30/88/22 | 11/12/11/1/0 | 64/209/31, 0,35 |
| 1 | Hiện tại đổi tick thành hàng | 8/4/1/3/7 | 24/6/3/3/21 | 52/24/3/21/49 | 11/7/5/2/6 | 12/29/83, 0,18 |
| 2 | Hàng cực trị bằng 0 | 8/5/1/4/7 | 24/6/0/6/24 | 52/51/5/46/47 | 11/0/0/0/11 | 6/56/89, 0,08 |
| 3 | Giảm dần về cực trị | 8/37/3/34/5 | 24/122/11/111/13 | 52/258/18/240/34 | 11/20/3/17/8 | 35/402/60, 0,13 |
| 4 | 3 hàng ≤ 0,35 × nền, không lọc volume | 8/14/7/7/1 | 24/52/21/31/3 | 52/154/48/106/4 | 11/17/10/7/1 | 86/151/9, 0,52 |
| 5 | 3 hàng nhỏ so với chính nến | 8/10/6/4/2 | 24/43/20/23/4 | 52/122/40/82/12 | 11/18/10/8/1 | 76/117/19, 0,53 |
| 6 | Như 5 + lọc volume | 8/10/6/4/2 | 24/33/20/13/4 | 52/79/38/41/14 | 11/14/10/4/1 | 74/62/21, 0,64 |
| **7** | **Đề xuất** | 8/9/7/2/1 | 24/31/21/10/3 | 52/66/44/22/8 | 11/11/10/1/1 | **82/35/13, 0,77** |
| 8 | Đề xuất theo từng tick | 8/34/5/29/3 | 24/91/13/78/11 | 52/125/34/91/18 | 11/16/10/6/1 | 62/204/33, 0,34 |
| 9 | Đề xuất 2 hàng | 8/19/7/12/1 | 24/66/23/43/1 | 52/134/45/89/7 | 11/19/10/9/1 | 85/153/10, 0,51 |
| 10 | Đề xuất 4 hàng | 8/7/5/2/3 | 24/16/10/6/14 | 52/37/25/12/27 | 11/8/7/1/4 | 47/21/48, 0,58 |
| 11 | Tổng 3 hàng ≤ 0,7 × nền | 8/10/6/4/2 | 24/37/23/14/1 | 52/85/42/43/10 | 11/12/10/2/1 | 81/63/14, 0,68 |
| 12 | Đề xuất + chỉ ở đỉnh/đáy cục bộ | 8/2/2/0/6 | 24/3/1/2/23 | 52/17/11/6/41 | 11/2/2/0/9 | 16/8/79, 0,27 |
| 13 | Đề xuất + bỏ dấu bị nến sau quét | 8/8/6/2/2 | 24/24/17/7/7 | 52/43/33/10/19 | 11/8/7/1/4 | 63/20/32, 0,71 |
| 14 | Đề xuất râu ≥ 1 hàng | 8/10/8/2/0 | 24/39/22/17/2 | 52/82/44/38/8 | 11/13/11/2/0 | 85/59/10, 0,71 |
| 15 | Đề xuất râu ≥ 3 hàng | 8/5/3/2/5 | 24/24/18/6/6 | 52/46/34/12/18 | 11/10/10/0/1 | 65/20/30, 0,72 |

Chống fit quá mức:
- Cấu trúc luật và tham số được tìm trên NQ M1 + GC M1. **GC M5 18/11 không dùng để tìm cấu trúc**, chỉ chấm sau: 11 / 10 trùng / 1 thừa / 1 sót (ngưỡng cuối 0,35 / 0,80 chọn theo điểm trung bình cả 4 mẫu).
- Kiểm chéo bỏ từng mẫu (`tune.py`, chọn tham số trên 3 mẫu, chấm mẫu còn lại): NQ_A F1 0,82 · NQ_B 0,76 · GC_M5 0,91 · GC M1 0,54 (khi bỏ GC M1 thì 3 mẫu còn lại chọn râu ≥ 1 hàng, A = 0,30).
- Fit riêng GC rồi chấm NQ, và ngược lại (`grid2.py`): F1 trên mẫu fit 0,78–0,82, trên mẫu kia 0,60.
- Vùng tham số phẳng: A 0,34–0,37 với C 0,80 cho F1 trung bình 0,81–0,83; A 0,38 hoặc C 0,75/0,85 tụt còn 0,75–0,79.

## 5. Spec đề xuất

Bản tham chiếu: **`ref_rule.py`** (chỉ dùng thư viện chuẩn, tính tuần tự từng nến).

**Hàng giá.** `row(tick) = floor((tick − off) / G)` (chia làm tròn xuống, đúng cả số âm).

| Mã | G (tick/hàng) | off |
|---|---|---|
| NQ, MNQ | 8 | 4 (= `NqRows` hiện có) |
| GC, MGC | 2 | 1 |
| mã khác | 1 | 0 (chưa có chart CORVEN để đối chiếu) |

**Mỗi nến** (o, h, l, c theo tick; các ô có volume > 0):
1. Gộp Ask, Bid, Volume theo hàng. `rowH = row(high)`, `rowL = row(low)`. Nến có high ≤ low: không dấu.
2. Nền, chỉ từ các nến **đã đóng trước** có giao dịch, tối đa N nến gần nhất, cần ≥ 5 nến (chưa đủ: không dấu):
   - `rowBase` = trung bình của (tổng volume nến ÷ số hàng có volume > 0). Với NQ đây chính là giá trị trung bình trong `_nqRowBase` (`BarStats(NqRows.Group(levels))` → mean).
   - `volBase` = trung bình tổng volume nến (tổng volume các ô, không lấy `bar.Volume`).
   - N = `DesiredBaseBars()` như hiện nay (M1, M5: 20).
3. Đỉnh (kiệt sức buy): `S_j` = Ask của hàng `rowH − j`, j = 0, 1, 2. Đáy (kiệt sức sell): `S_j` = Bid của hàng `rowL + j`. Hàng trống hoặc vượt ra ngoài nến tính 0.
4. Có dấu khi đủ cả ba:
   - (a) `max(S_0, S_1, S_2) ≤ 0,35 × rowBase`
   - (b) `tổng volume nến ≥ 0,80 × volBase`
   - (c) râu ≥ 2 hàng: đỉnh `rowH − row(max(open, close)) ≥ 2`; đáy `row(min(open, close)) − rowL ≥ 2`
5. Sau khi nến đóng: nộp (volume TB mỗi hàng, tổng volume) vào hàng đợi nền (mọi nến có giao dịch, kể cả high = low).

Tham số: `ExhRows = 3`, `ExhRowSmallRatio = 0,35`, `ExhMinBarVolRatio = 0,80`, `ExhMinWickRows = 2`. Các ô cũ (`ExhMinWickTicks`, `ExhSumLevels`, `ExhSumHistRatio`, `ExhTailMedianRatio`, `ExhTailBaseline`) không còn dùng. Đổi khoá chữ ký cache (vd `exh-v4`). Mức giá của dấu và luật quét râu giữ nguyên (đỉnh/đáy nến).

Hiển thị (tuỳ người dùng quyết): CORVEN không làm mờ dấu đã bị quét.

**Đối chiếu C# = Python từng nến:**
```
python ref_rule.py --levels <fp_*.csv> --tick 0.25 --symbol NQZ26 --minutes 1 --out marks_py.csv
dotnet perf/Golden/bin/Release/net10.0-windows/Golden.dll stophunt --levels <fp_*.csv> --tick 0.25 --symbol NQZ26 --minutes 1 --marks marks_cs.csv
```
So các dòng `exhT` / `exhB` (cột t, kind, price). Số chuẩn của bản Python:

| File | Nến | Dấu | File dấu |
|---|---|---|---|
| NQ 90 ngày (`fp_NQZ26_…_90d.csv`) | 78.464 | 3.310 | `ref_marks_NQ_90d.csv` |
| GC 90 ngày (`fp_GCZ26_…_90d.csv`) | 87.362 | 5.517 | `ref_marks_GC_90d.csv` |
| NQ 05–06/11 (cắt từ file 90 ngày) | 2.700 | 375 | `ref_marks_NQ_1105-1106.csv` |
| GC 04–06/11 (cắt từ file 90 ngày) | 4.059 | 383 | `ref_marks_GC_1104-1106.csv` |

## 6. Mật độ dấu trên toàn bộ dữ liệu (`density.py` → `out_density.csv`)

| Mã, khung | Số nến | Hiện tại (dấu/nến) | Đề xuất (dấu/nến) |
|---|---|---|---|
| NQ M1 (từ 14/09) | 71.047 | 22.480 (0,316) | 3.231 (0,045) |
| NQ M5 | 14.210 | 7.896 (0,556) | 2.376 (0,167) |
| NQ M15 | 4.737 | 3.223 (0,680) | 1.793 (0,379) |
| GC M1 | 87.362 | 12.566 (0,144) | 5.517 (0,063) |
| GC M5 | 17.623 | 6.247 (0,354) | 4.084 (0,232) |
| GC M15 | 5.875 | 3.293 (0,561) | 2.773 (0,472) |

Trên các mẫu CORVEN: NQ M1 0,10–0,12 dấu/nến, GC M1 0,07, GC M5 0,42 (26 nến phiên Mỹ).

## 7. Chưa chắc chắn

- Luật thật của CORVEN chưa biết; đây là luật gần nhất tìm được: trùng 82/95 dấu, thừa 35. Mẫu số "volume TB mỗi hàng của 20 nến trước" và ngưỡng 0,35 / 0,80 là ước lượng (dùng TB volume ô lớn nhất hoặc trung vị cho kết quả gần tương đương).
- Điều kiện râu không đo chính xác được: tam giác CORVEN bị thân nến che khi râu ngắn (GC dưới khoảng 4 tick, NQ dưới khoảng 8–10 tick), nên một phần dấu "thừa" có râu ngắn có thể là dấu CORVEN bị che. Chỉ tính phía có râu đủ dài thì GC M1 thừa 13 thay vì 22.
- Mốc hàng GC: M1 05–06/11 chọn rõ off = 1 (off = 0: F1 0,64). GC M5 18/11 thì off = 0 trùng 11/11, off = 1 trùng 10/11; 26 nến không đủ để kết luận mốc hàng trên M5 có khác.
- Khung từ M15 trở lên và các mã ngoài NQ/GC chưa có chart CORVEN nào để so.
- Khung 20:26–21:30 của NQ_B bỏ phần sau 21:30 vì volume profile che (ở đó nhìn thấy thêm 5 dấu CORVEN nhưng không đếm được phía không có dấu).
- Dữ liệu của mình và Sierra có thể lệch vài hợp đồng mỗi hàng; với hàng chỉ 1–5 hợp đồng, lệch 1 hợp đồng đủ đổi kết quả ở dấu sát ngưỡng (9 dấu GC nằm trong khoảng 0,33–0,35).

## 8. File

- Trích đáp án: `tri.py`, `nq_calib.py`, `extract.py`, `build_gt.py`.
- Dữ liệu và luật: `data.py`, `cur_rule.py` (luật hiện tại), `ref_rule.py` (luật đề xuất), `eval_all.py`, `compare_marks.py`, `cs_parity_current.py`.
- Dò luật: `feats.py` → `grid1.py`, `split.py`, `rowscan.py`, `make_x.py` → `grid2.py`, `grid3.py`; `base_scan.py` → `base_scan2.py`; `tune.py`, `variants.py`, `density.py`.
- Các file `.pkl` trung gian đã xoá (script tự dựng lại; `data.py` tạo `_cache_*.pkl` khoảng 250 MB, đừng commit).
