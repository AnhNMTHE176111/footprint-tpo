# Chart M5 của CORVEN ngày 18/11/2026: chấm nhỏ, Big Trade (vòng mờ) và Kiệt sức

> Ghi chú nghiên cứu. Đây là luật **mô phỏng hiển thị** của chart CORVEN để đọc bằng mắt, **không phải lợi thế đã kiểm định**.
> Bản chốt ngày 19/11/2026 thay hoàn toàn luật gom hàng ngày 18/11 (giữ lại dưới đây ở mục "Lịch sử" để biết vì sao đổi).
> **Cập nhật chiều 19/11/2026 (người học chốt):** vòng mờ không còn suy từ volume của ô, mà là **Big Trade = một lệnh đơn chủ động rất lớn** (xem mục ngay dưới). Luật chấm nhỏ và Kiệt sức giữ nguyên.

## Dữ liệu

- Ảnh chart của CORVEN: `corven-m5-2026-11-18.png` (GC, khung M5, 12:15 đến 14:25 UTC). Ảnh chart của người học cùng giai đoạn: `user-m5-2026-11-18.png`.
- Dữ liệu của mình: `data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h.csv` và file `_bars.csv` cùng tên (từng mức giá và từng nến M5).
- Chuẩn thật (ground truth) đọc từ ảnh: `gt_corven_m5.csv` (25 vòng tròn, 16 cụm chấm, 11 dấu kiệt sức; 26 nến, không tính nến 14:25 đang chạy dở). Đã sửa trục giá bằng cách khớp 26 đường lưới ngang (xem mục 0 trong `results_iter.md`): **không có độ lệch giá** giữa chart CORVEN và dữ liệu của mình.
- Nhật ký đầy đủ mọi luật đã thử và điểm số: `results_iter.md`.

## Luật chốt (tất cả theo từng tick, không gom hàng)

Ký hiệu cho mỗi ô giá có giao dịch của một nến: bên trội = bên lớn hơn giữa Bid và Ask; bên yếu = bên còn lại; số lệnh = số lệnh đã khớp tại ô đó. Màu: Ask trội thì xanh (buy), ngược lại đỏ (sell).

Mức nền, chỉ tính từ **20 nến đã đóng liền trước** (cần ít nhất 5 nến): volume trung bình mỗi ô có giao dịch = trung bình, trên 20 nến trước, của (volume trung bình mỗi ô có giao dịch của nến đó).

| Dấu | Điều kiện |
|---|---|
| Chấm nhỏ đặc | số lệnh ≥ 2,4 × volume trung bình mỗi ô; **và** bên trội lớn hơn hẳn bên trội của mọi tick khác trong ±3 tick (tick vắng tính 0, bằng nhau thì không nổ); **và** bên trội ≥ 9 hợp đồng |
| Kiệt sức | râu phía đó ≥ 3 tick; **và** tổng volume bên soi (Ask ở đỉnh, Bid ở đáy) trên 6 tick từ cực trị đi vào trong ≤ 1,1 × volume trung bình mỗi ô của 20 nến trước (mức nền lịch sử, không phải trung bình của chính nến) |
| Vòng tròn mờ (Big Trade) | một lệnh đơn lớn nhất tại mức giá ≥ 10 hợp đồng (xem mục dưới); không còn là luật dựa trên volume của ô |

- Chấm luôn vẽ trên cùng, đè lên vòng mờ.
- Sàn tuyệt đối 9 hợp đồng cho bên trội của chấm (đã đo: sàn này không đổi kết quả trên 26 nến mẫu).
- Cỡ chấm: 45% bề ngang nến, kẹp trong 5 đến 10 px. Bóng của nến quét trong một stop hunt được tô tím, cả chấm lẫn vòng Big Trade.
- Chế độ ngưỡng cố định (giữ để tương thích): chấm dùng bên trội ≥ ngưỡng cố định thay cho điều kiện số lệnh; các điều kiện còn lại giữ nguyên. Chế độ này chưa được fit với chart nào.

## Big Trade: vòng mờ là một lệnh đơn lớn (chốt 19/11/2026, chiều)

Người học (nhà giao dịch) chốt: vòng mờ là **một lệnh chủ động duy nhất rất lớn đánh một lần**. Chấm đặc thường nổ ở khoảng 9 hợp đồng (13 Bid hay 18 Ask có thể là 3 đến 4 nhà đầu tư nhỏ cộng lại), nhưng nếu 60 Bid đến trong **một** lệnh thì nổ vòng mờ: nhìn thấy nghĩa là cá lớn vào chủ động. Giải thích này khớp với phát hiện buổi sáng: không đặc trưng nào của ô đoán được vòng của CORVEN, vì dữ liệu lịch sử của mình không có kích cỡ từng lệnh đơn.

Luật: tại một mức giá, lệnh đơn lớn nhất (số do feed sống cấp) ≥ ngưỡng thì nổ một vòng. Ngưỡng mặc định **10 hợp đồng**. Không điểm z, không so trung vị, không giới hạn số vòng. Phía của lệnh đơn không có trong dữ liệu, nên màu theo phía trội của ô. Cỡ vòng: 1,0 × bề ngang nến ở ngưỡng, 2,5 × từ 6 lần ngưỡng trở lên, theo đường căn bậc hai, kẹp 8 đến 80 px. Chỉ feed sống cấp số lệnh đơn; lịch sử thường bằng 0 nên trên 87.362 nến M1 lịch sử không có vòng nào.

### Hiệu chỉnh ngưỡng từ nhật ký sống

Nguồn: nhật ký indicator tự ghi mỗi lệnh đơn quan sát được trên nến M1 đã đóng (thư mục bigtrade-log, mã GCZ26, khung 1 phút), từ 10/11/2026 đến 19/11/2026: **4.169 nến M1**, 73.219 dòng (nến, mức giá). Script tái lập: `bigtrade_threshold.py`. Với nến M5, lấy **lớn nhất theo mức giá** của lệnh đơn trên 5 nến M1 của các khoảng 5 phút đầy đủ (812 nến M5).

Phân bố lệnh đơn: trung vị 1, phân vị 99 là 9, phân vị 99,9 là 23, lớn nhất 186 hợp đồng.

| Ngưỡng (hợp đồng) | Vòng mỗi nến M1 | Vòng mỗi nến M5 | Số vòng M5 | Trung bình một vòng sau |
|---|---|---|---|---|
| 5 | 0,608 | 2,882 | 2.340 | 0,0 giờ |
| 9 | 0,181 | 0,881 | 715 | 0,1 giờ |
| **10** | **0,150** | **0,732** | 594 | 0,1 giờ |
| 15 | 0,051 | 0,257 | 209 | 0,3 giờ |
| **20** | 0,025 | **0,128** | 104 | 0,7 giờ |
| 40 | 0,007 | 0,034 | 28 | 2,4 giờ |
| **60** | 0,003 | **0,014** | 11 | 6,2 giờ |

Chart M5 của CORVEN ngày 18/11 có khoảng 0,96 vòng mờ mỗi nến (25 vòng trên 26 nến), nên ngưỡng 10 (0,73 vòng mỗi nến M5) là mức gần nhất trong các mốc tròn. Số liệu nhật ký đo trên một giai đoạn 9 ngày và con số của CORVEN đến từ một biểu đồ, nên đây là hiệu chỉnh thô; nhật ký vẫn đang ghi thêm, chạy lại script để cập nhật.

## Điểm số trên 26 nến mẫu (12:15 đến 14:20 UTC)

| Dấu | Của mình | CORVEN | Trùng |
|---|---|---|---|
| Vòng tròn mờ | không còn so sánh | 25 | luật cũ dựa trên volume ô chỉ trùng 7 vị trí (F1 0,30) nên đã bỏ; nay là Big Trade từ lệnh đơn, lịch sử không có số liệu để so |
| Chấm nhỏ đặc | 37 chấm (30 cụm) | 16 cụm (khoảng 33 chấm) | 10 cụm trùng, 19 thừa, 6 sót; F1 theo điểm ảnh 0,43 |
| Kiệt sức | 13 | 11 | 11 trùng, 2 thừa, 0 sót; F1 0,917 |

Cách đọc đúng các con số này:
- **Vòng tròn mờ không khớp được bằng dữ liệu lịch sử.** Không đặc trưng nào của một ô (bên trội, volume, số lệnh, chênh lệch, mất cân bằng chéo) đoán được tốt vòng của CORVEN (diện tích dưới đường cong 0,55 đến 0,67; 1,0 là hoàn hảo, 0,5 là ngẫu nhiên). Giải thích đã được người học chốt: vòng dựa trên kích cỡ lệnh đơn, mà dữ liệu lịch sử của mình không có. Vì vậy luật cũ dựa trên volume ô đã bỏ.
- **Chấm nhỏ:** các chấm chồng lên nhau nên số chấm thật của CORVEN không đếm được; kết quả chấm ở mức cụm và điểm ảnh.
- **Kiệt sức khớp tốt**, và số trùng giữ nguyên 11/11 trên một vùng tham số rộng (6 tick với hệ số 1,2 đến 2,0; râu 2 đến 3 tick), chỉ số dấu thừa thay đổi dần theo hệ số. Tuy vậy tham số được chọn **trên chính 26 nến này**, nên điểm số lạc quan; chưa có phần dữ liệu giữ lại để kiểm.

## Tác động lên toàn bộ lịch sử M1 (87.362 nến GCZ26, cấu hình mặc định, qua `perf/Golden`)

Đo bằng `dotnet perf/Golden/bin/Release/net10.0-windows/Golden.dll stophunt` (số dấu hiện còn đúng sau khi nạp từ đầu, gồm cả nến cuối).

| Đại lượng | Luật gom hàng cũ (18/11) | Luật theo từng tick (19/11 sáng) | Big Trade từ lệnh đơn (19/11 chiều) |
|---|---|---|---|
| Vòng tròn mờ | 58.766 | 35.506 (theo volume ô) | **0** (lịch sử không có lệnh đơn) |
| Chấm nhỏ đặc | 49.505 | 32.140 | 32.140 |
| Dấu kiệt sức | 16.048 | 12.594 | 12.594 |
| Dấu stop hunt | 748 | 634 | 496 |
| Bóng tím | 1.924 (vòng 945, chấm 979) | 1.130 (vòng 506, chấm 624) | 660 (chỉ chấm) |

Số dấu stop hunt giảm từ 634 xuống 496 vì bóng ở nến quét nay chỉ còn là chấm (lịch sử không có vòng Big Trade). Trên chart sống, vòng Big Trade cũng được tính, nên số dấu sẽ nhiều hơn. Chạy thử với lệnh đơn giả lập (bằng bên trội của ô, chỉ để kiểm đường mã, không phải số liệu thật) đã cho thấy vòng Big Trade được nhận và tô tím đúng.

Luật được chỉnh theo chart M5 nên trên M1 số dấu mỗi nến khác xa M5; không dùng các con số M1 này để so với CORVEN. Stop hunt chấp nhận bóng ở cả hai loại dấu (chấm và vòng Big Trade) tại nến quét.

## Đối chiếu C# với Python

`export_marks.py` chạy lại luật chốt bằng Python (`rules.py`, `feats.py`, `exh_feats.py`, tham số trong `final_eval.py`) rồi ghi `marks_python_26bars.csv` (cột: nến, tick, loại, màu). Test `tests/CorvenM5ParityTests.cs` tính lại đúng 26 nến bằng `CellBigLogic` và `ExhaustionLogic` thật, mức nền làm nóng từ mọi nến trước đó trong file, và đòi **tập (nến, tick, loại, màu) giống hệt**: 37 chấm, 13 dấu kiệt sức, tổng 50, không lệch dấu nào (không còn so vòng mờ). Bỏ qua nếu thiếu file dữ liệu.

```bash
cd quantower-orderflow-indicator/research/corven_m5_2026-11-18
python build_cache.py        # sinh F_m5.pkl, E_m5.pkl (một lần)
python final_eval.py         # in điểm số và so sánh từng nến
python export_marks.py       # ghi marks_python_26bars.csv (thêm --floor N để thử sàn khác)
python bigtrade_threshold.py # bảng hiệu chỉnh ngưỡng Big Trade từ nhật ký sống
cd ../.. && dotnet run -c Release --project tests    # chạy cả test đối chiếu
```

## Giới hạn cần nhớ

1. **Chỉ một biểu đồ, 26 nến.** Luật khớp với mẫu này chưa chứng minh khớp với chart CORVEN ở ngày khác hay khung khác; tham số được chọn trên chính mẫu nên điểm số lạc quan.
2. **Nguồn dữ liệu của CORVEN khác của mình.** Delta hai bên lệch ở một số nến (tương quan delta từng nến 0,97 trên 26 nến, nhưng lệch hẳn ở 12:50, 12:55 và 14:05 đến 14:20), nên khớp vị trí từng bóng có trần thấp.
3. Mức kiệt sức bị quét qua với tỷ lệ gần như nến bất kỳ (44% / 70% / 84% sau 1 / 5 / 20 nến, nến bất kỳ 46% / 72% / 85%): đây là dấu để đọc chart, không phải lợi thế.
4. Ngưỡng Big Trade (10 hợp đồng) hiệu chỉnh từ nhật ký sống 9 ngày, chỉ khớp về **tần suất** (0,73 so với 0,96 vòng mỗi nến M5), chưa khớp được **vị trí** từng vòng với chart CORVEN vì lịch sử không có kích cỡ lệnh đơn.

## Lịch sử (luật gom hàng ngày 18/11, đã thay)

Luật cũ gom 2 tick thành một hàng, vòng tròn nổ khi bên trội của hàng ≥ 1,25 × volume trung bình mỗi hàng của 20 nến trước, ≥ 3 × bên yếu, sàn 9; chấm nổ khi ≥ 1,5 × mức đó. Trên 27 nến cho 17 vòng và 79 chấm ngoài vòng (CORVEN vẽ khoảng 33 chấm), kiệt sức dùng tổng 3 tick ≤ 0,5 × trung bình của chính nến (23 dấu, 9 trùng). Sau khi sửa trục giá và đọc lại chấm, người ta thử khoảng 40 họ luật theo từng tick (xem mục 4 trong `results_iter.md`); luật theo từng tick ở trên cho số chấm sát CORVEN hơn nhiều (37 so với 79) và kiệt sức chính xác hơn (13 dấu, trùng 11).
