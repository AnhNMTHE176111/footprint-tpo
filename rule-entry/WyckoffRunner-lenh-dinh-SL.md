# Danh sách lệnh DÍNH SL — WyckoffRunner nhánh CBR (M1), config đang ship

Nguồn: dxFeed `_GCQ26XCEC` 1 phút, cửa sổ 05-07/2026. Cấu hình: CleanBreak=true, PullMax=1.00, RR=4.0 (khớp mặc định WyckoffRunner.cs — xem BASELINE.md). Nhánh CBR là nhánh DUY NHẤT đang bắn tín hiệu mặc định (nhánh QUAY ĐẦU VWAP đang TẮT — `EnableReversal=false`, xem `wyckoffrunner-setup-va-kich-ban.md`).
Tổng 33 lệnh: 17 dính SL, 16 chạm TP, 0 nến chạm CẢ SL lẫn TP cùng lúc (không phân định được thứ tự trong nến — liệt kê riêng ở cuối).

Giờ ghi theo cột `Time left` gốc dxFeed (UTC) — khớp trực tiếp giờ mở nến trên chart nếu chart cùng feed; nếu chart hiển thị giờ khác (vd Quantower TzOffset=+7 = giờ VN), cộng/trừ theo lệch múi giờ sàn của bạn.

Cách đọc cột **Cạnh vùng co (phá)**: giá cạnh range nội bộ (8 nến trước) bị phá — CBR neo theo range nội bộ, KHÔNG phải zone volume-profile như EntrySignal; cột **Hợp lưu** vẫn là số vùng POC/VAH/VAL/Đỉnh/Đáy (phiên Á/Âu/Mỹ + D-1) chồng lấp quanh giá vào (ConfluenceTol=7 tick) — CHỈ hiển thị (Grade A/B), KHÔNG lọc/chặn lệnh nào.

| STT | Giờ vào lệnh | Kịch bản | Hướng | Cạnh vùng co (phá) | Entry | SL | TP (4R) | Giờ dính SL | Hợp lưu | VSA | Climax | Lý do nến vào |
|---:|---|---|:---:|---:|---:|---:|---:|---|:---:|---:|:---:|---|
| 1 | 2026-05-26 09:44 | CBR phá→hồi→tiếp diễn | SHORT | 4548.3 | 4545.8 | 4548.8 | 4533.8 | 2026-05-26 09:45 | 0 | 2.48x | có | phá 4548.3 (span 51.0tick);hồi 96%;VSA2.48x(tim) |
| 2 | 2026-05-26 17:58 | CBR phá→hồi→tiếp diễn | SHORT | 4527.6 | 4523.6 | 4527.2 | 4509.2 | 2026-05-26 18:26 | 0 | 2.30x | có | phá 4527.6 (span 62.0tick);hồi 83%;VSA2.30x(tim) |
| 3 | 2026-05-29 09:50 | CBR phá→hồi→tiếp diễn | LONG | 4563.9 | 4569.6 | 4565.4 | 4586.4 | 2026-05-29 09:52 | 1 | 2.85x | có | phá 4563.9 (span 66.0tick);hồi 65%;VSA2.85x(tim) |
| 4 | 2026-06-02 13:59 | CBR phá→hồi→tiếp diễn | SHORT | 4535.9 | 4532.1 | 4535.4 | 4518.9 | 2026-06-02 14:00 | 0 | 2.06x | không | phá 4535.9 (span 74.0tick);hồi 79%;VSA2.06x |
| 5 | 2026-06-03 09:34 | CBR phá→hồi→tiếp diễn | SHORT | 4473.9 | 4470.3 | 4473.4 | 4457.9 | 2026-06-03 09:37 | 0 | 4.73x | có | phá 4473.9 (span 63.0tick);hồi 90%;VSA4.73x(tim) |
| 6 | 2026-06-04 16:15 | CBR phá→hồi→tiếp diễn | LONG | 4506.4 | 4508.4 | 4505.4 | 4520.4 | 2026-06-04 17:12 | 1 | 3.71x | có | phá 4506.4 (span 36.0tick);hồi 89%;VSA3.71x(tim) |
| 7 | 2026-06-15 13:34 | CBR phá→hồi→tiếp diễn | LONG | 4377.9 | 4384.5 | 4378.2 | 4409.7 | 2026-06-15 13:52 | 0 | 2.87x | có | phá 4377.9 (span 48.0tick);hồi 94%;VSA2.87x(tim) |
| 8 | 2026-06-16 08:13 | CBR phá→hồi→tiếp diễn | LONG | 4357.8 | 4359.4 | 4356.4 | 4371.4 | 2026-06-16 11:36 | 2 | 2.50x | có | phá 4357.8 (span 33.0tick);hồi 90%;VSA2.50x(tim) |
| 9 | 2026-06-16 12:56 | CBR phá→hồi→tiếp diễn | LONG | 4370.0 | 4374.1 | 4370.9 | 4386.9 | 2026-06-16 13:01 | 0 | 2.64x | có | phá 4370.0 (span 61.0tick);hồi 82%;VSA2.64x(tim) |
| 10 | 2026-06-17 17:37 | CBR phá→hồi→tiếp diễn | LONG | 4384.3 | 4393.3 | 4390.3 | 4405.3 | 2026-06-17 18:00 | 0 | 9.88x | có | phá 4384.3 (span 38.0tick);hồi 65%;VSA9.88x(tim) |
| 11 | 2026-06-18 11:06 | CBR phá→hồi→tiếp diễn | SHORT | 4273.2 | 4268.7 | 4272.8 | 4252.3 | 2026-06-18 12:12 | 0 | 2.86x | có | phá 4273.2 (span 70.0tick);hồi 88%;VSA2.86x(tim) |
| 12 | 2026-06-18 15:36 | CBR phá→hồi→tiếp diễn | SHORT | 4256.0 | 4248.2 | 4253.4 | 4227.4 | 2026-06-18 15:41 | 0 | 2.27x | có | phá 4256.0 (span 74.0tick);hồi 74%;VSA2.27x(tim) |
| 13 | 2026-06-29 10:02 | CBR phá→hồi→tiếp diễn | SHORT | 4051.3 | 4044.4 | 4048.1 | 4029.6 | 2026-06-29 10:10 | 0 | 2.86x | có | phá 4051.3 (span 71.0tick);hồi 74%;VSA2.86x(tim) |
| 14 | 2026-07-06 00:06 | CBR phá→hồi→tiếp diễn | SHORT | 4193.2 | 4184.6 | 4190.1 | 4162.6 | 2026-07-06 00:09 | 1 | 3.72x | có | phá 4193.2 (span 45.0tick);hồi 69%;VSA3.72x(tim) |
| 15 | 2026-07-06 09:34 | CBR phá→hồi→tiếp diễn | SHORT | 4153.4 | 4149.4 | 4152.5 | 4137.0 | 2026-07-06 09:36 | 0 | 5.13x | có | phá 4153.4 (span 71.0tick);hồi 78%;VSA5.13x(tim) |
| 16 | 2026-07-21 18:32 | CBR phá→hồi→tiếp diễn | LONG | 4083.2 | 4089.1 | 4085.6 | 4103.1 | 2026-07-21 18:47 | 1 | 4.31x | có | phá 4083.2 (span 73.0tick);hồi 72%;VSA4.31x(tim) |
| 17 | 2026-07-22 14:07 | CBR phá→hồi→tiếp diễn | LONG | 4155.1 | 4162.3 | 4158.4 | 4177.9 | 2026-07-22 14:15 | 0 | 2.76x | có | phá 4155.1 (span 61.0tick);hồi 74%;VSA2.76x(tim) |

## Tổng kết

- n=33, TP=16, SL=17, amb=0 → WR=48.5%, tổng=+47.0R (khớp BASELINE.md nếu amb=0).
