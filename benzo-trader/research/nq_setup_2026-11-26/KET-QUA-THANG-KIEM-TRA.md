# Kết quả backtest tháng kiểm tra — chuẩn setup CORVEN NQ M1

- Dữ liệu: NQZ26 M1, tháng kiểm tra 2026-10-26 → 2026-11-25 (23 ngày giao dịch). Máy trạng thái chạy từ 2026-09-14.
- Spec: [SPEC-SETUP-NQ.md](SPEC-SETUP-NQ.md), chốt trước khi chạy; chạy một lần, không chỉnh số sau khi xem.
- Chi phí 1.0 điểm/lệnh; cùng nến chạm SL và TP tính SL; đóng lệnh 16:59 NY.

## Tổng

| Nhóm | Lệnh | WR | R/lệnh sau phí | Tổng R | Chuỗi thua dài nhất | Sụt giảm lớn nhất (R) |
|---|---|---|---|---|---|---|
| Tất cả | 116 | 34 % | -0.049 | -5.7 | 9 | 14.3 |
| (trước phí) | 116 | 34 % | -0.010 | -1.1 | 9 | 11.1 |
| Loại: Break | 61 | 33 % | -0.062 | -3.8 | 9 | 10.5 |
| Loại: Fail Break | 36 | 33 % | -0.061 | -2.2 | 6 | 9.3 |
| Loại: Test vùng stacked | 19 | 37 % | +0.015 | +0.3 | 6 | 6.2 |
| Phiên: Mỹ | 26 | 31 % | -0.146 | -3.8 | 6 | 9.6 |
| Phiên: Á | 60 | 35 % | -0.006 | -0.3 | 6 | 8.7 |
| Phiên: Âu | 30 | 33 % | -0.052 | -1.5 | 4 | 5.5 |
| Hướng: buy | 57 | 32 % | -0.093 | -5.3 | 6 | 11.6 |
| Hướng: sell | 59 | 36 % | -0.006 | -0.4 | 10 | 10.5 |
| Tín hiệu thứ hai: kiệt sức | 30 | 23 % | -0.363 | -10.9 | 5 | 10.9 |
| Tín hiệu thứ hai: stacked mới | 58 | 33 % | -0.049 | -2.9 | 11 | 12.5 |
| Tín hiệu thứ hai: stop hunt | 37 | 38 % | +0.076 | +2.8 | 3 | 4.4 |
| Tín hiệu thứ hai: vùng đang test | 19 | 37 % | +0.015 | +0.3 | 6 | 6.2 |
| Mốc lớn: kịch bản 1 | 4 | 50 % | +0.459 | +1.8 | 2 | 2.0 |
| Mốc lớn: kịch bản 2.1 | 6 | 33 % | -0.036 | -0.2 | 3 | 3.1 |
| Mốc lớn: kịch bản 2.2 | 106 | 33 % | -0.069 | -7.3 | 8 | 14.0 |
| Bias: chưa có bias | 41 | 34 % | -0.008 | -0.3 | 4 | 7.8 |
| Bias: có bias | 75 | 33 % | -0.071 | -5.4 | 11 | 13.5 |

- Lệnh/ngày: 5.04. Khoảng SL trung vị: 31.94 điểm. Thời gian giữ trung vị: 10 nến. Kết cục: TP 38 · SL 77 · đóng cuối phiên 1.

## Đối chứng vào ngẫu nhiên (200 lệnh / lệnh thật, 1.000 bộ)

| Nhóm | Lệnh | R/lệnh thật | Ngẫu nhiên trung vị | Ngẫu nhiên phần trăm 95 | Vị trí của lệnh thật |
|---|---|---|---|---|---|
| Tất cả | 116 | -0.049 | -0.039 | +0.179 | 47 % |
| Fail Break | 36 | -0.061 | -0.061 | +0.300 | 50 % |
| Break | 61 | -0.062 | +0.026 | +0.331 | 32 % |
| Test vùng stacked | 19 | +0.015 | -0.039 | +0.499 | 58 % |

## Cột phụ (chốt trước, chỉ tham khảo, không dùng để chọn)

| Biến thể | Lệnh | WR | R/lệnh sau phí | Tổng R | Chuỗi thua | Sụt giảm (R) |
|---|---|---|---|---|---|---|
| TP 4R (cùng lệnh) | 116 | 20 % | -0.120 | -13.9 | 13 | 21.4 |
| Chi phí 1,5 điểm (cùng lệnh) | 116 | 34 % | -0.069 | -8.0 | 9 | 16.4 |
| Không lọc bias | 142 | 35 % | +0.006 | +0.8 | 11 | 15.3 |
| Bỏ tầng xác nhận order flow (luật 15–18) | 1084 | 34 % | -0.041 | -44.9 | 14 | 57.7 |

## Ứng viên bị loại theo cổng (một ứng viên có thể trượt nhiều cổng)

| Loại | Cổng | Số lần |
|---|---|---|
| Break | delta nhỏ/ngược | 2966 |
| Break | không bóng cùng phe | 2934 |
| Break | thiếu tín hiệu thứ hai | 2639 |
| Break | nến không đẹp | 2078 |
| Break | ngược cấu trúc | 1144 |
| Break | ngược bias | 1050 |
| Break | đang có lệnh | 351 |
| Break | kiệt sức ngược phe | 341 |
| Break | SL xa quá | 175 |
| Break | sau 16:45 NY | 31 |
| Break | nến kế sau khoảng trống | 5 |
| Break | giá vào đã qua SL | 4 |
| Fail Break | không bóng cùng phe | 9804 |
| Fail Break | delta nhỏ/ngược | 9409 |
| Fail Break | thiếu tín hiệu thứ hai | 7884 |
| Fail Break | không đủ 1,7R tới cạnh đối diện | 7182 |
| Fail Break | nến không đẹp | 6092 |
| Fail Break | kiệt sức ngược phe | 1270 |
| Fail Break | đang có lệnh | 1051 |
| Fail Break | SL xa quá | 359 |
| Fail Break | sau 16:45 NY | 136 |
| Fail Break | nến kế sau khoảng trống | 8 |
| Fail Break | giá vào đã qua SL | 6 |
| Test vùng stacked | delta nhỏ/ngược | 720 |
| Test vùng stacked | không bóng cùng phe | 650 |
| Test vùng stacked | nến không đẹp | 469 |
| Test vùng stacked | ngược bias | 233 |
| Test vùng stacked | kiệt sức ngược phe | 101 |
| Test vùng stacked | đang có lệnh | 81 |
| Test vùng stacked | SL xa quá | 42 |
| Test vùng stacked | sau 16:45 NY | 4 |
| Test vùng stacked | nến kế sau khoảng trống | 1 |
| Test vùng stacked | giá vào đã qua SL | 1 |
