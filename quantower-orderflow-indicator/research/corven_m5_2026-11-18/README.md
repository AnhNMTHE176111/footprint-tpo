# Chart M5 của CORVEN ngày 18/11/2026: chỉnh luật Ô Bid/Ask lớn và Kiệt sức

> Ghi chú nghiên cứu. Đây là luật **mô phỏng hiển thị** của chart CORVEN để đọc bằng mắt, **không phải lợi thế đã kiểm định**.

## Dữ liệu

- Ảnh chart của CORVEN: `corven-m5-2026-11-18.png` (GC, khung M5, 12:15 đến 14:25 UTC, 27 nến). Ảnh chart của người học cùng giai đoạn: `user-m5-2026-11-18.png`.
- Dữ liệu của mình: `data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h.csv` và file `_bars.csv` cùng tên (từng mức giá và từng nến M5).
- Vị trí 24 bóng và 11 dấu kiệt sức của CORVEN được đọc bằng mắt và bằng `segment_chart.py` (tách màu trên ảnh), rồi ghi tay vào hai script `fit_*.py`.

## Phương pháp

Thử nhiều luật đơn giản, chấm điểm bằng F1 so với chart CORVEN. Với bóng: ghép từng nến, tham lam theo khoảng cách, dung sai 0,5 giá. Với kiệt sức: so cặp (nến, phía đỉnh hay đáy).

### Ô Bid/Ask lớn (bóng)

| Luật | Số bóng | F1 theo vị trí |
|---|---|---|
| Cũ: bên áp đảo của hàng ≥ 1,3 × mức trung bình volume mỗi hàng của 20 nến trước, sàn 9 | 123 | 0,16 |
| **Mới: ≥ 1,25 × mức trung bình đó, và ≥ 3 × bên yếu, sàn 9** | **17** | **0,39** |
| CORVEN | 24 | |

- Luật mới trùng vị trí 8 bóng; 11 trên 15 nến có bóng của CORVEN cũng có bóng của mình; 11 nến CORVEN để trống mình cũng để trống.
- Mật độ trên 9 ngày M5: 2,87 giảm còn 0,73 bóng mỗi nến (CORVEN khoảng 0,9).
- CORVEN bỏ qua hàng cân bằng (ví dụ 100 Bid × 101 Ask) và chỉ đánh bóng hàng lệch hẳn một phía; đó là lý do thêm điều kiện "≥ 3 × bên yếu".
- Bóng vàng (hai bên cùng lớn) bị bỏ hẳn, vì CORVEN không có và người học không cần.
- Đánh đổi: so với các chấm M1 cũ của CORVEN (`research/row2_test.py`, buổi Meet 05–06/11), F1 giảm từ 0,835 xuống 0,572. Người học chấp nhận để có kiểu hiển thị giống chart M5.

### Kiệt sức

Luật mới: râu phía đó dài ≥ 3 tick, và tổng volume bên soi (Ask ở đỉnh, Bid ở đáy) trên 3 tick từ cực trị đi vào trong ≤ 0,5 × volume trung bình mỗi mức giá có giao dịch của nến.

| Luật | Số dấu | Trùng CORVEN (trên 11) | F1 |
|---|---|---|---|
| Cũ (cực trị nhỏ hoặc giảm dần, râu ≥ 1 tick) | 30 | 6 | 0,29 |
| **Mới** | **23** | **9** | **0,53** |

Mật độ dấu mỗi nến: M1 ngày 05/11 là 0,28; M5 ngày 17/11 là 0,48.

### Big Trade

Không chỉnh được: lịch sử không có kích cỡ từng lệnh đơn (cột `max_one_trade` bằng 0). Giữ nguyên.

### Hai loại dấu: vòng tròn lớn mờ (Big) và chấm nhỏ đặc (Dot)

Chart của CORVEN vẽ **hai loại dấu**: vòng tròn lớn mờ có cỡ theo độ lớn (người học gọi là "big trade") và chấm nhỏ đặc đỏ/xanh (chấm Bid/Ask của CORVEN). Luật Big ở trên khớp với vòng tròn mờ (ví dụ 14:00 ở 3786,15 ra 41 Bid × 79 Ask; nến 11/15), nên giờ được vẽ **mờ**. Chấm đặc thì trước đây thiếu hẳn (ví dụ chấm xanh 14:00 và 14:05).

Phương pháp: dùng cùng cách gom hàng 2 tick và cùng mức trung bình volume mỗi hàng của 20 nến trước, quét hệ số từ 0,5 đến 4,0, so với 16 chấm đặc đọc từ ảnh, chấm F1 theo vị trí và màu.

| Luật chấm | Số chấm | F1 |
|---|---|---|
| **Bên áp đảo ≥ 1,5 × mức trung bình, sàn 9, không đòi mất cân bằng** | 91 (trong đó 12 trùng với Big, còn lại 79) | **0,52** |

- Quy tắc cuối cùng: hàng là **Big** nếu thoả luật Big; không thì là **Dot** nếu bên áp đảo ≥ 1,5 × mức trung bình và ≥ sàn 9. Trên 26 nến (12:15–14:20, bỏ nến 14:25 đang chạy dở): Big 17, Dot 79.
- **Ca 14:05 không với tới**: chấm xanh của CORVEN ở 3786,9 nhưng bên áp đảo của hàng đó thấp hơn 1,5 × mức trung bình (35), nên không đạt ở mức 1,5. Không hạ ngưỡng vì sẽ thêm rất nhiều chấm giả.
- Mật độ Dot khá dày (91 chấm trên 26 nến, 3,5 mỗi nến); CORVEN chỉ có 16. Độ chính xác của Dot thấp (nhiều chấm của mình không có chấm CORVEN), nên đây là hiển thị tham khảo.
- Cách vẽ: Big là vòng tròn mờ (độ đậm 35%, viền mảnh), cỡ 1,0 đến 2,5 × bề ngang nến; Dot là chấm đặc 5–10 px, vẽ trên cùng. Stop hunt tô tím cả hai bậc.

## Giới hạn cần nhớ

1. **Chỉ một biểu đồ, 27 nến.** Luật khớp tốt với mẫu này chưa chứng minh khớp với chart CORVEN ở ngày khác hay khung khác.
2. **Nguồn dữ liệu của CORVEN khác của mình.** Delta hai bên lệch (ví dụ chart CORVEN −29 còn dữ liệu mình +10 ở cùng nến), nên khớp vị trí từng bóng có trần thấp; F1 0,39 là gần mức tối đa thực tế, không phải do luật kém.
3. Pha gom hàng (2 tick mỗi hàng, lệch pha 1) đo trên GC; mã khác chưa kiểm.
4. Mức kiệt sức bị quét qua với tỷ lệ gần như nến bất kỳ (44% / 70% / 84% sau 1 / 5 / 20 nến, nến bất kỳ 46% / 72% / 85%): đây là dấu để đọc chart, không phải lợi thế.

## Cách chạy lại

Mọi script chạy được từ bất kỳ thư mục nào (đường dẫn dữ liệu tính từ vị trí file). Cần Python với `pandas`, `numpy`, và `Pillow` (chỉ cho `segment_chart.py`).

```bash
python research/corven_m5_2026-11-18/fit_bubbles_m5.py      # in luật cũ và dòng "CHOSEN RULE": 17 bóng, 8 trùng
python research/corven_m5_2026-11-18/fit_exhaustion_m5.py   # in "current small-only" 30/6 và "CHOSEN RULE": 23 dấu, 9 trùng
python research/corven_m5_2026-11-18/fit_dots_m5.py         # in luật chấm tốt nhất và cuối file dòng "TIERS": Big 17, Dot 79
python research/corven_m5_2026-11-18/exh_density.py         # mật độ M5 ngày 17/11 (mặc định)
python research/corven_m5_2026-11-18/exh_density.py data-export/data-footprint/fp_GCZ26_XCEC_Time_20260811-20261109_90d 2026-11-05   # mật độ M1 ngày 05/11
python research/corven_m5_2026-11-18/segment_chart.py research/corven_m5_2026-11-18/corven-m5-2026-11-18.png   # tách bóng và dấu từ ảnh
```

Đối chiếu C# với Python: `dotnet run -c Release --project quantower-orderflow-indicator/tests` chạy `tests/CorvenM5ParityTests.cs`, tính lại đúng 27 nến bằng `CellBigLogic` và `ExhaustionLogic` thật và đòi ra đúng 17 bóng Big (8 trùng), 79 chấm Dot (trên 26 nến, như Python), 23 dấu (9 trùng). Bỏ qua nếu thiếu file dữ liệu.

## Tác động lên toàn bộ lịch sử M1 (87.362 nến GCZ26, cấu hình mặc định, qua `perf/Golden`)

| Đại lượng | Trước | Sau |
|---|---|---|
| Bóng Ô Bid/Ask lớn | 120.576 | 58.766 |
| Dấu kiệt sức | 20.299 | 16.048 |
| Dấu stop hunt (bóng tím) | 764 (2.098 bóng tím) | 606 (998 bóng tím) |

Mức giảm ở M1 (khoảng một nửa số bóng) nhỏ hơn mức giảm ở M5 (2,87 xuống 0,73 mỗi nến) vì luật được chỉnh theo chart M5. Dấu kiệt sức trên M1 toàn lịch sử giảm nhẹ (0,23 xuống 0,18 mỗi nến), trong khi riêng ngày 05/11 lại tăng (0,20 xuống 0,28, vì script đo mật độ chỉ so nhánh "nhỏ" của luật cũ, không so nhánh "giảm dần").

### Số lượng sau khi thêm bậc Dot (87.362 nến M1, cấu hình mặc định)

| Đại lượng | Trước | Sau |
|---|---|---|
| Bóng Big (vòng mờ) | 58.766 | 58.766 (không đổi) |
| Chấm Dot | 0 | 49.505 |
| Dấu stop hunt | 606 | 748 |
| Bóng tím | 998 | 1.924 (Big 945, Dot 979) |

Stop hunt tăng vì bộ dò giờ chấp nhận bóng ở cả hai bậc tại nến quét; số bóng Big tím giảm nhẹ (998 xuống 945) vì tập tín hiệu và thời gian nghỉ giữa hai dấu thay đổi.
