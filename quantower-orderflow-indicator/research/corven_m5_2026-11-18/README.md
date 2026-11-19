# Chart M5 của CORVEN ngày 18/11/2026: luật Ô Bid/Ask lớn, chấm nhỏ và Kiệt sức (theo từng tick)

> Ghi chú nghiên cứu. Đây là luật **mô phỏng hiển thị** của chart CORVEN để đọc bằng mắt, **không phải lợi thế đã kiểm định**.
> Bản chốt ngày 19/11/2026 thay hoàn toàn luật gom hàng ngày 18/11 (giữ lại dưới đây ở mục "Lịch sử" để biết vì sao đổi).

## Dữ liệu

- Ảnh chart của CORVEN: `corven-m5-2026-11-18.png` (GC, khung M5, 12:15 đến 14:25 UTC). Ảnh chart của người học cùng giai đoạn: `user-m5-2026-11-18.png`.
- Dữ liệu của mình: `data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h.csv` và file `_bars.csv` cùng tên (từng mức giá và từng nến M5).
- Chuẩn thật (ground truth) đọc từ ảnh: `gt_corven_m5.csv` (25 vòng tròn, 16 cụm chấm, 11 dấu kiệt sức; 26 nến, không tính nến 14:25 đang chạy dở). Đã sửa trục giá bằng cách khớp 26 đường lưới ngang (xem mục 0 trong `results_iter.md`): **không có độ lệch giá** giữa chart CORVEN và dữ liệu của mình.
- Nhật ký đầy đủ mọi luật đã thử và điểm số: `results_iter.md`.

## Luật chốt (tất cả theo từng tick, không gom hàng)

Ký hiệu cho mỗi ô giá có giao dịch của một nến: bên trội = bên lớn hơn giữa Bid và Ask; bên yếu = bên còn lại; số lệnh = số lệnh đã khớp tại ô đó. Màu: Ask trội thì xanh (buy), ngược lại đỏ (sell).

Hai mức nền, chỉ tính từ **20 nến đã đóng liền trước** (cần ít nhất 5 nến):
- volume trung bình mỗi ô có giao dịch = trung bình, trên 20 nến trước, của (volume trung bình mỗi ô có giao dịch của nến đó);
- bên trội lớn nhất trung bình = trung bình, trên 20 nến trước, của (bên trội lớn nhất trong các ô của nến đó).

| Dấu | Điều kiện |
|---|---|
| Vòng tròn lớn mờ | bên trội ≥ 0,5 × bên trội lớn nhất trung bình; **và** bên trội lớn hơn hẳn bên trội của mọi tick khác trong ±5 tick cùng nến (tick vắng tính 0, bằng nhau thì không nổ); **và** bên trội ≥ 4 × bên yếu (bên yếu bằng 0 thì tính là 1) |
| Chấm nhỏ đặc | số lệnh ≥ 2,4 × volume trung bình mỗi ô; **và** bên trội lớn hơn hẳn bên trội của mọi tick khác trong ±3 tick |
| Kiệt sức | râu phía đó ≥ 3 tick; **và** tổng volume bên soi (Ask ở đỉnh, Bid ở đáy) trên 6 tick từ cực trị đi vào trong ≤ 1,1 × volume trung bình mỗi ô của 20 nến trước (mức nền lịch sử, không phải trung bình của chính nến) |

- Một tick có thể vừa là vòng tròn vừa là chấm: vẽ cả hai, chấm nằm trên cùng.
- Sàn tuyệt đối 9 hợp đồng cho bên trội của vòng tròn và chấm. Đã đo: sàn này **không đổi kết quả** trên 26 nến mẫu (22 vòng và 37 chấm cả khi có lẫn không có sàn), nên giữ cho cả hai.
- Cỡ vòng tròn to dần theo (bên trội ÷ bên trội lớn nhất trung bình): 1,0 × bề ngang nến ở mức 0,5 lần, 2,5 × ở mức 2 lần trở lên, nén căn bậc hai. Đây là lựa chọn của người viết code, không fit từ chart. Hệ số tương quan giữa bán kính vòng của CORVEN và volume ô là 0,79 nên cỡ theo độ lớn là hợp lý, nhưng công thức cụ thể chưa được kiểm.
- Cỡ chấm: 45% bề ngang nến, kẹp trong 5 đến 10 px. Bóng của nến quét trong một stop hunt được tô tím, cả vòng lớn lẫn chấm.
- Chế độ ngưỡng cố định (`UseFixedThreshold`, giữ để tương thích): vòng tròn dùng bên trội ≥ ngưỡng cố định thay cho 0,5 × bên trội lớn nhất trung bình; chấm dùng bên trội ≥ ngưỡng cố định thay cho điều kiện số lệnh. Các điều kiện còn lại giữ nguyên. Chế độ này chưa được fit với chart nào.

## Điểm số trên 26 nến mẫu (12:15 đến 14:20 UTC)

| Dấu | Của mình | CORVEN | Trùng |
|---|---|---|---|
| Vòng tròn lớn mờ | 22 | 25 | 7 trùng (dung sai ±2 tick, cùng màu), 15 thừa, 18 sót; F1 0,30 |
| Chấm nhỏ đặc | 37 chấm (30 cụm) | 16 cụm (khoảng 33 chấm) | 10 cụm trùng, 19 thừa, 6 sót; F1 theo điểm ảnh 0,43 |
| Kiệt sức | 13 | 11 | 11 trùng, 2 thừa, 0 sót; F1 0,917 |

Cách đọc đúng các con số này:
- **Vị trí từng vòng tròn khớp kém.** Không có đặc trưng nào của một ô (bên trội, volume, số lệnh, chênh lệch, mất cân bằng chéo) đoán được tốt vòng tròn của CORVEN (diện tích dưới đường cong 0,55 đến 0,67 cho riêng từng đặc trưng; 1,0 là hoàn hảo, 0,5 là ngẫu nhiên). Giả thuyết chưa kiểm được: vòng của CORVEN dựa trên kích cỡ lệnh đơn, mà dữ liệu của mình không có (`max_one_trade` bằng 0).
- **Chấm nhỏ:** các chấm chồng lên nhau nên số chấm thật của CORVEN không đếm được; kết quả chấm ở mức cụm và điểm ảnh.
- **Kiệt sức khớp tốt**, và số trùng giữ nguyên 11/11 trên một vùng tham số rộng (6 tick với hệ số 1,2 đến 2,0; râu 2 đến 3 tick), chỉ số dấu thừa thay đổi dần theo hệ số. Tuy vậy tham số được chọn **trên chính 26 nến này**, nên điểm số lạc quan; chưa có phần dữ liệu giữ lại để kiểm.
- Màu (bên trội của cửa sổ ±2 tick) khớp 22 trên 25 vòng.

## Tác động lên toàn bộ lịch sử M1 (87.362 nến GCZ26, cấu hình mặc định, qua `perf/Golden`)

Đo bằng `dotnet perf/Golden/bin/Release/net10.0-windows/Golden.dll stophunt` (số dấu hiện còn đúng sau khi nạp từ đầu, gồm cả nến cuối).

| Đại lượng | Luật gom hàng cũ (18/11) | Luật theo từng tick (19/11) |
|---|---|---|
| Vòng tròn lớn mờ | 58.766 | 35.506 |
| Chấm nhỏ đặc | 49.505 | 32.140 |
| Dấu kiệt sức | 16.048 | 12.594 |
| Dấu stop hunt | 748 | 634 |
| Bóng tím | 1.924 (vòng 945, chấm 979) | 1.130 (vòng 506, chấm 624) |

Luật được chỉnh theo chart M5 nên trên M1 số dấu mỗi nến khác xa M5; không dùng các con số M1 này để so với CORVEN. Stop hunt chấp nhận bóng ở cả hai loại dấu tại nến quét.

## Đối chiếu C# với Python

`export_marks.py` chạy lại luật chốt bằng Python (`rules.py`, `feats.py`, `exh_feats.py`, tham số trong `final_eval.py`) rồi ghi `marks_python_26bars.csv` (cột: nến, tick, loại, màu). Test `tests/CorvenM5ParityTests.cs` tính lại đúng 26 nến bằng `CellBigLogic` và `ExhaustionLogic` thật, mức nền làm nóng từ mọi nến trước đó trong file, và đòi **tập (nến, tick, loại, màu) giống hệt**: 22 vòng, 37 chấm, 13 dấu kiệt sức, tổng 72, không lệch dấu nào. Bỏ qua nếu thiếu file dữ liệu.

```bash
cd quantower-orderflow-indicator/research/corven_m5_2026-11-18
python build_cache.py        # sinh F_m5.pkl, E_m5.pkl (một lần)
python final_eval.py         # in điểm số và so sánh từng nến
python export_marks.py       # ghi marks_python_26bars.csv (thêm --floor N để thử sàn khác)
cd ../.. && dotnet run -c Release --project tests    # chạy cả test đối chiếu
```

## Giới hạn cần nhớ

1. **Chỉ một biểu đồ, 26 nến.** Luật khớp với mẫu này chưa chứng minh khớp với chart CORVEN ở ngày khác hay khung khác; tham số được chọn trên chính mẫu nên điểm số lạc quan.
2. **Nguồn dữ liệu của CORVEN khác của mình.** Delta hai bên lệch ở một số nến (tương quan delta từng nến 0,97 trên 26 nến, nhưng lệch hẳn ở 12:50, 12:55 và 14:05 đến 14:20), nên khớp vị trí từng bóng có trần thấp.
3. Mức kiệt sức bị quét qua với tỷ lệ gần như nến bất kỳ (44% / 70% / 84% sau 1 / 5 / 20 nến, nến bất kỳ 46% / 72% / 85%): đây là dấu để đọc chart, không phải lợi thế.
4. Big Trade không chỉnh được vì lịch sử không có kích cỡ từng lệnh đơn.

## Lịch sử (luật gom hàng ngày 18/11, đã thay)

Luật cũ gom 2 tick thành một hàng, vòng tròn nổ khi bên trội của hàng ≥ 1,25 × volume trung bình mỗi hàng của 20 nến trước, ≥ 3 × bên yếu, sàn 9; chấm nổ khi ≥ 1,5 × mức đó. Trên 27 nến cho 17 vòng và 79 chấm ngoài vòng (CORVEN vẽ khoảng 33 chấm), kiệt sức dùng tổng 3 tick ≤ 0,5 × trung bình của chính nến (23 dấu, 9 trùng). Sau khi sửa trục giá và đọc lại chấm, người ta thử khoảng 40 họ luật theo từng tick (xem mục 4 trong `results_iter.md`); luật theo từng tick ở trên cho số chấm sát CORVEN hơn nhiều (37 so với 79) và kiệt sức chính xác hơn (13 dấu, trùng 11).
