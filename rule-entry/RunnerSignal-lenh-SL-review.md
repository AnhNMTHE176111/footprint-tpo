# Danh sách lệnh DÍNH SL — RunnerSignal (M1), config đang ship

Nguồn: `data-export/27-7/RunnerSignal_signals.csv` — CSV do chính indicator **LIVE** xuất ra
(`ExportCsv=true`), KHÔNG phải backtest Python mô phỏng → khớp 100% với đúng tín hiệu đã vẽ trên
chart Quantower thật của bạn.
Tổng 9 lệnh đã đóng tính đến lúc export (2026-07-30 23:55): **7 dính SL** (liệt kê dưới đây), 2 chạm
TP. Mẫu còn nhỏ (mới bật export vài ngày) — sẽ nối thêm dòng khi bạn export CSV mới.

Giờ ghi theo `bar.TimeLeft` gốc (UTC) — khớp trực tiếp giờ mở nến trên chart nếu chart hiển thị UTC;
nếu chart hiển thị giờ khác, cộng/trừ theo lệch múi giờ của bạn (VN = UTC+7).

Cách đọc cột **Mép/vùng kích hoạt**: với nhánh CBR là mép range đã phá (giá bắt đầu leg); với nhánh
QUAY ĐẦU là giá VWAP phiên lúc chạm. Cột **Vùng chắn TP** là thông tin CHỈ ĐỂ HIỂN THỊ (không phải
điều kiện chặn lệnh) — khoảng cách R từ entry tới vùng mạnh gần nhất nằm trên đường đi tới TP.

| STT | Giờ vào lệnh (UTC) | Nhánh | Hướng | Mép/vùng kích hoạt | Entry | SL | TP (RR) | Giờ dính SL (UTC) | Vùng chắn TP | VSA | Climax | Lý do nến vào |
|---:|---|---|:---:|---|---:|---:|---:|---|:---:|---:|:---:|---|
| 1 | 2026-07-28 13:47 | CBR | SHORT | mép 4087.0 | 4081.9 | 4085.2 | 4072.0 (RR3) | 2026-07-28 13:49 | 1.7R | 2.34x | có | phá 4087.0;hồi 72%;leg 7.2giá;VSA2.3x(tim) |
| 2 | 2026-07-29 01:12 | CBR | SHORT | mép 4079.5 | 4073.1 | 4077.0 | 4061.4 (RR3) | 2026-07-29 01:28 | 0.2R | 5.58x | có | phá 4079.5;hồi 74%;leg 10.3giá;VSA5.6x(tim) |
| 3 | 2026-07-29 04:00 | QUAY_ĐẦU | SHORT | VWAP 4082.175 | 4081.1 | 4083.3 | 4077.8 (RR1.5) | 2026-07-29 04:25 | — | 1.87x | không | rút râu trên;VSA1.9x |
| 4 | 2026-07-29 10:51 | CBR | SHORT | mép 4088.7 | 4086.0 | 4089.0 | 4077.0 (RR3) | 2026-07-29 11:15 | 0.7R | 3.72x | có | phá 4088.7;hồi 70%;leg 3.3giá;VSA3.7x(tim) |
| 5 | 2026-07-29 11:28 | CBR | LONG | mép 4089.3 | 4092.7 | 4089.7 | 4101.7 (RR3) | 2026-07-29 11:35 | 0.3R | 2.75x | có | phá 4089.3;hồi **47%**⚠;leg 3.2giá;VSA2.8x(tim) |
| 6 | 2026-07-29 12:19 | CBR | SHORT | mép 4084.6 | 4077.4 | 4082.2 | 4063.0 (RR3) | 2026-07-29 12:56 | 0.1R | 5.40x | có | phá 4084.6;hồi 61%;leg 6.7giá;VSA5.4x(tim) |
| 7 | 2026-07-29 23:58 | QUAY_ĐẦU | LONG | VWAP 4141.44 | 4143.5 | 4141.24 | 4146.891 (RR1.5) | 2026-07-30 00:01 | 0.7R | 2.45x | có | rút râu dưới;VSA2.5x(tim);hấp thụ✓ |

**⚠ Điểm đáng ngờ, ưu tiên review trước:**
- **#5**: cột "hồi" ghi 47% — THẤP HƠN sàn cấu hình hiện tại `PullMin`=60%. Cần kiểm tra xem lúc lệnh này bắn, DLL trên máy có phải bản cũ (trước khi nâng sàn hồi 40%→60% ngày 2026-07-28) hay không, hoặc số ghi log tính sai cách so với code.
- **#1, #5, #7**: chạm SL chỉ sau 2, 7, 3 phút — SL rất sát, đáng xem trên chart có phải vào ngay đỉnh/đáy cú giật.
- 4/5 lệnh CBR thua đều có "Vùng chắn TP" rất gần (0.1R–1.7R) — gợi ý có thể cần thêm điều kiện chặn khi vùng mạnh cản đường quá gần, hiện tại đây mới chỉ là thông tin hiển thị.

## Sau khi review

Gửi lại theo từng STT (đúng/sai + lý do bạn thấy trên chart), tôi sẽ đối chiếu với code
`RunnerSignal.cs` (nhánh CBR ở hàm `Scan()`, nhánh QUAY ĐẦU ở `ScanReversal()`) để sửa đúng điều kiện
bạn chỉ ra, build lại DLL rồi gửi bạn test tiếp.
