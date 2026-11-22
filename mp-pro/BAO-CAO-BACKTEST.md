# Backtest sách "Thực chiến cùng Pro Market Profile" trên vàng GC — báo cáo (2026-11-22)

## Kết luận
Sau 5 vòng (dò → đối chiếu sách → chỉnh → dò lại), **không setup nào của sách có lợi thế** trên vàng GC khi viết thành luật cơ học.
Hai ứng viên tốt nhất trên tập dò đều **âm rõ** khi chạy nguyên trạng trên 2 năm dữ liệu chưa dùng.

## Dữ liệu và cách đo
- Dò: GCZ26 M1 footprint 90 ngày (11/08–09/11/2026). TRAIN 44 phiên, TEST 20 phiên.
- Kiểm độc lập: GC liên tục M1 footprint 2 năm (08/2024–08/2026, ~500 phiên, ~168 nghìn hợp đồng/phiên).
  Loại lệnh có dữ liệu vắt qua bước nhảy giá giả khi đổi hợp đồng.
- Phí + trượt: 0,2 giá/lệnh. Lệnh limit chỉ khớp khi giá giao dịch xuyên qua 1 tick. Cùng nến chạm SL và TP thì tính SL.
- SL/TP của sách (12/10 pip EURUSD trên M30) quy đổi thành 1,3 / 1,1 ATR của khung dùng.
- Bỏ vào lệnh ±10 phút quanh 08:30 và 10:00 giờ New York (sách: tránh tin 10 phút).

## Kết quả chính
| Setup (trang sách) | Khung | Dữ liệu | Số lệnh | Kỳ vọng/lệnh |
|---|---|---|---|---|
| POC vùng tích lũy, đánh lần quay về đầu tiên (25-28, 50, 52) | M5 | TRAIN 90d | 51 | −0,22R |
| như trên | M30 | 2 năm, dò | 39 | +0,03R |
| Phá LVN, profile 3 ngày (66-71) | M5 | TRAIN → TEST | 19 → 18 | +0,79R → +0,18R |
| như trên, giữ nguyên | M5 | 2 năm | 271 | **−0,18R** |
| Fake out mép VA đang hình thành (90-92) | M5 | TRAIN → TEST | 48 → 23 | +0,23R → +0,02R |
| như trên, giữ nguyên | M5 | 2 năm | 539 | **−0,20R** |
| Mẫu P/b, mẫu D (21-23, 30-34) | ngày | 2 năm, dò | 33 / 95 | −0,02R / +0,01R |
| Quy tắc 80% (83-86) | 30 phút | 2 năm, dò | 52 | +0,07R, kiểm +0,16R, khoảng tin cậy chứa 0 |
| Open Drive (77-78) | 30 phút | 2 năm, dò → kiểm | 51 → 34 | +0,17R → −0,26R |
| Phá LVN khung sách (M30) | M30 | 2 năm | 84–130 | −0,13 đến +0,03R |
| POC phiên bị phá rồi retest (53, 55-56) | M30 | 2 năm, dò | 56 | −0,27R |
| Cụm nhiều POC hợp lưu (56-57) | ngày | 2 năm dò → 90d | 16 → 18 | +0,20R → −0,02R |
| Spike (87-88) | 30 phút | 2 năm | 18 | −0,11R |
| Nến pin + giá đóng vượt POC (98-99), R:R 1:1 | M15/M30 | 2 năm | 250–1.530 | −0,02 đến −0,17R |

Chi tiết từng vòng: `backtest/r3_fake.txt`, `backtest/holdout2y.txt`, `backtest/r4_book_scale.csv`, `backtest/r5.csv`.

## Điều rút ra
1. **Vào lệnh ở M1 âm ở mọi setup.** Ở M1, nhiễu và phí nuốt hết phần chênh.
2. **Setup chính của sách (limit tại POC vùng tích lũy) thua đều ở khung scalp.** Giá về POC thường đi xuyên qua.
3. **Tỷ lệ thắng cao không có nghĩa là lời.** Phá LVN thắng 70–80% nhưng TP (HVN kế) quá gần so với SL nên kỳ vọng âm.
4. **Số dương trên 44 phiên TRAIN đều là chọn tham số.** Sang dữ liệu mới, chúng co về 0 hoặc âm.

## Giới hạn
- Phần định tính của sách không viết thành luật được: "xu hướng", hợp lưu Fibonacci/trendline, đọc tin. Đã thay bằng phiên bản cơ học đơn giản.
- Sách viết cho forex 24h trên M30. Định nghĩa phiên vàng (Globex 22:00 UTC hoặc pit 08:20 NY) là lựa chọn của Claude.
- Ô nào có dưới khoảng 30 lệnh thì chưa đủ để kết luận theo chiều nào.

## Code
`backtest/core.py` (dữ liệu, profile, mô phỏng lệnh), `setup_a.py`, `setups_other.py`, `r2.py`, `r4_book_scale.py`, `r5.py`, `holdout2y.py`.
Cấu hình chốt trước khi kiểm: `backtest/FROZEN.md`.
