# Kết quả backtest tháng kiểm tra — chuẩn setup CORVEN NQ M1

- Dữ liệu: NQZ26 M1, tháng kiểm tra 2026-10-26 → 2026-11-25 (23 ngày giao dịch). Máy trạng thái chạy từ 2026-09-14.
- Spec: [SPEC-SETUP-NQ.md](SPEC-SETUP-NQ.md), chốt trước khi chạy; chạy một lần, không chỉnh số sau khi xem.
- **Bản 2** (người học 2026-11-26, sau khi xem bản 1): bỏ Fail Break, chỉ còn Break và Test vùng stacked (follow trend). Quyết định này có sau khi đã nhìn tháng kiểm tra ⇒ số dưới đây **không còn là kiểm tra mù**; cần dữ liệu mới (sau 25/11) để kiểm.
- Chi phí 1.0 điểm/lệnh; cùng nến chạm SL và TP tính SL; đóng lệnh 16:59 NY.

## Tổng

| Nhóm | Lệnh | WR | R/lệnh sau phí | Tổng R | Chuỗi thua dài nhất | Sụt giảm lớn nhất (R) |
|---|---|---|---|---|---|---|
| Tất cả | 81 | 35 % | -0.019 | -1.5 | 7 | 10.4 |
| (trước phí) | 81 | 35 % | +0.011 | +0.9 | 7 | 10.0 |
| Loại: Break | 62 | 34 % | -0.029 | -1.8 | 9 | 10.5 |
| Loại: Test vùng stacked | 19 | 37 % | +0.015 | +0.3 | 6 | 6.2 |
| Phiên: Mỹ | 20 | 30 % | -0.173 | -3.5 | 6 | 7.3 |
| Phiên: Á | 46 | 35 % | -0.011 | -0.5 | 4 | 5.5 |
| Phiên: Âu | 15 | 40 % | +0.163 | +2.4 | 3 | 3.1 |
| Hướng: buy | 39 | 33 % | -0.030 | -1.2 | 5 | 6.2 |
| Hướng: sell | 42 | 36 % | -0.008 | -0.3 | 6 | 7.2 |
| Tín hiệu thứ hai: kiệt sức | 24 | 21 % | -0.443 | -10.6 | 5 | 10.6 |
| Tín hiệu thứ hai: stacked mới | 46 | 37 % | +0.081 | +3.7 | 8 | 9.4 |
| Tín hiệu thứ hai: stop hunt | 7 | 57 % | +0.674 | +4.7 | 2 | 2.1 |
| Tín hiệu thứ hai: vùng đang test | 19 | 37 % | +0.015 | +0.3 | 6 | 6.2 |
| Mốc lớn: kịch bản 1 | 2 | 50 % | +0.477 | +1.0 | 1 | 1.0 |
| Mốc lớn: kịch bản 2.1 | 3 | 33 % | -0.022 | -0.1 | 2 | 2.0 |
| Mốc lớn: kịch bản 2.2 | 76 | 34 % | -0.032 | -2.4 | 7 | 10.4 |
| Bias: chưa có bias | 32 | 38 % | +0.098 | +3.1 | 7 | 7.4 |
| Bias: có bias | 49 | 33 % | -0.095 | -4.7 | 11 | 12.3 |

- Lệnh/ngày: 3.52. Khoảng SL trung vị: 38.75 điểm. Thời gian giữ trung vị: 13 nến. Kết cục: TP 27 · SL 53 · đóng cuối phiên 1.

## Đối chứng vào ngẫu nhiên (200 lệnh / lệnh thật, 1.000 bộ)

| Nhóm | Lệnh | R/lệnh thật | Ngẫu nhiên trung vị | Ngẫu nhiên phần trăm 95 | Vị trí của lệnh thật |
|---|---|---|---|---|---|
| Tất cả | 81 | -0.019 | -0.008 | +0.274 | 46 % |
| Fail Break | 0 | – | – | – | – |
| Break | 62 | -0.029 | +0.036 | +0.315 | 37 % |
| Test vùng stacked | 19 | +0.015 | -0.039 | +0.499 | 58 % |

## Cột phụ (chốt trước, chỉ tham khảo, không dùng để chọn)

| Biến thể | Lệnh | WR | R/lệnh sau phí | Tổng R | Chuỗi thua | Sụt giảm (R) |
|---|---|---|---|---|---|---|
| TP 4R (cùng lệnh) | 81 | 21 % | -0.083 | -6.7 | 12 | 15.4 |
| Chi phí 1,5 điểm (cùng lệnh) | 81 | 35 % | -0.034 | -2.7 | 7 | 10.6 |
| Không lọc bias | 107 | 36 % | +0.047 | +5.0 | 9 | 14.6 |
| Bỏ tầng xác nhận order flow (luật 15–18) | 481 | 32 % | -0.077 | -37.3 | 10 | 47.6 |

## Ứng viên bị loại theo cổng (một ứng viên có thể trượt nhiều cổng)

| Loại | Cổng | Số lần |
|---|---|---|
| Break | delta nhỏ/ngược | 2966 |
| Break | không bóng cùng phe | 2934 |
| Break | thiếu tín hiệu thứ hai | 2639 |
| Break | nến không đẹp | 2078 |
| Break | ngược cấu trúc | 1144 |
| Break | ngược bias | 1050 |
| Break | đang có lệnh | 348 |
| Break | kiệt sức ngược phe | 341 |
| Break | SL xa quá | 175 |
| Break | sau 16:45 NY | 31 |
| Break | nến kế sau khoảng trống | 5 |
| Break | giá vào đã qua SL | 4 |
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
