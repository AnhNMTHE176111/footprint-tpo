# Kết quả backtest tháng kiểm tra — chuẩn setup CORVEN NQ M1

- Dữ liệu: NQZ26 M1, tháng kiểm tra 2026-10-26 → 2026-11-25 (23 ngày giao dịch). Máy trạng thái chạy từ 2026-09-14.
- Spec: [SPEC-SETUP-NQ.md](SPEC-SETUP-NQ.md), chốt trước khi chạy; chạy một lần, không chỉnh số sau khi xem.
- **Bản 3** (người học 2026-11-26): Break + Follow trend = theo move đang đi (không cần vùng stacked: move ≥ 2 × mbr trong 30 nến, hồi 1–10 nến, không sâu quá 50 % move); **bỏ bias phiên**. Có sau khi đã nhìn tháng kiểm tra ⇒ **không còn là kiểm tra mù**.
- Chi phí 1.0 điểm/lệnh; cùng nến chạm SL và TP tính SL; đóng lệnh 16:59 NY.

## Tổng

| Nhóm | Lệnh | WR | R/lệnh sau phí | Tổng R | Chuỗi thua dài nhất | Sụt giảm lớn nhất (R) |
|---|---|---|---|---|---|---|
| Tất cả | 179 | 37 % | +0.092 | +16.4 | 9 | 14.7 |
| (trước phí) | 179 | 37 % | +0.126 | +22.5 | 9 | 14.0 |
| Loại: Break | 82 | 35 % | +0.025 | +2.0 | 12 | 14.3 |
| Loại: Follow trend | 97 | 39 % | +0.148 | +14.4 | 6 | 8.4 |
| Phiên: Mỹ | 43 | 35 % | +0.057 | +2.5 | 5 | 6.6 |
| Phiên: Á | 101 | 36 % | +0.022 | +2.2 | 9 | 11.7 |
| Phiên: Âu | 35 | 46 % | +0.335 | +11.7 | 4 | 4.1 |
| Hướng: buy | 86 | 37 % | +0.088 | +7.6 | 8 | 10.9 |
| Hướng: sell | 93 | 38 % | +0.095 | +8.8 | 10 | 11.6 |
| Tín hiệu thứ hai: kiệt sức | 53 | 32 % | -0.070 | -3.7 | 9 | 15.5 |
| Tín hiệu thứ hai: stacked mới | 136 | 38 % | +0.102 | +13.9 | 8 | 14.0 |
| Tín hiệu thứ hai: stop hunt | 10 | 70 % | +1.061 | +10.6 | 2 | 2.1 |
| Mốc lớn: kịch bản 1 | 3 | 67 % | +0.975 | +2.9 | 1 | 1.0 |
| Mốc lớn: kịch bản 2.1 | 6 | 17 % | -0.524 | -3.1 | 5 | 5.1 |
| Mốc lớn: kịch bản 2.2 | 170 | 38 % | +0.098 | +16.7 | 9 | 13.4 |
| Bias: chưa có bias | 52 | 37 % | +0.063 | +3.3 | 8 | 8.5 |
| Bias: có bias | 127 | 38 % | +0.104 | +13.2 | 8 | 12.5 |

- Lệnh/ngày: 7.78. Khoảng SL trung vị: 32.50 điểm. Thời gian giữ trung vị: 11 nến. Kết cục: TP 67 · SL 110 · đóng cuối phiên 2.

## Đối chứng vào ngẫu nhiên (200 lệnh / lệnh thật, 1.000 bộ)

| Nhóm | Lệnh | R/lệnh thật | Ngẫu nhiên trung vị | Ngẫu nhiên phần trăm 95 | Vị trí của lệnh thật |
|---|---|---|---|---|---|
| Tất cả | 179 | +0.092 | -0.011 | +0.158 | 86 % |
| Break | 82 | +0.025 | -0.001 | +0.264 | 57 % |
| Follow trend | 97 | +0.148 | +0.008 | +0.246 | 84 % |

## Cột phụ (chốt trước, chỉ tham khảo, không dùng để chọn)

| Biến thể | Lệnh | WR | R/lệnh sau phí | Tổng R | Chuỗi thua | Sụt giảm (R) |
|---|---|---|---|---|---|---|
| TP 4R (cùng lệnh) | 179 | 25 % | +0.160 | +28.6 | 16 | 16.5 |
| Chi phí 1,5 điểm (cùng lệnh) | 179 | 37 % | +0.075 | +13.4 | 9 | 15.0 |
| Có lọc bias | 133 | 38 % | +0.094 | +12.5 | 6 | 7.5 |
| Bỏ tầng xác nhận order flow (luật 15–18) | 1124 | 34 % | -0.027 | -30.3 | 13 | 49.8 |

## Ứng viên bị loại theo cổng (một ứng viên có thể trượt nhiều cổng)

| Loại | Cổng | Số lần |
|---|---|---|
| Break | delta nhỏ/ngược | 2966 |
| Break | không bóng cùng phe | 2934 |
| Break | thiếu tín hiệu thứ hai | 2639 |
| Break | nến không đẹp | 2078 |
| Break | ngược cấu trúc | 1144 |
| Break | đang có lệnh | 473 |
| Break | kiệt sức ngược phe | 341 |
| Break | SL xa quá | 175 |
| Break | sau 16:45 NY | 31 |
| Break | nến kế sau khoảng trống | 5 |
| Break | giá vào đã qua SL | 4 |
| Follow trend | delta nhỏ/ngược | 4044 |
| Follow trend | không bóng cùng phe | 4005 |
| Follow trend | thiếu tín hiệu thứ hai | 3982 |
| Follow trend | nến không đẹp | 2600 |
| Follow trend | đang có lệnh | 726 |
| Follow trend | kiệt sức ngược phe | 417 |
| Follow trend | SL xa quá | 218 |
| Follow trend | sau 16:45 NY | 45 |
| Follow trend | nến kế sau khoảng trống | 2 |
| Follow trend | giá vào đã qua SL | 2 |
