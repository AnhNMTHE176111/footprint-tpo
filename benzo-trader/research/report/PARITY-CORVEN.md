# Parity Python ↔ C# — setup CORVEN (corven-1)

> Opus, GĐ3 (plan mục 10.6). `research/parity_corven.py` chạy `setup_corven.run_gd1` (chuẩn) và `tools/ReplayCorven` (mã C# sản phẩm: BenzoEngine + DetectorCorven + RangeLogic/StackedImbalance/ExhaustionLogic nối nguồn) trên `fp_GCZ26_XCEC_Time_20260723-20261021_90d`. Phiên mỏng đầu file (nến < 3697) không vào lệnh ở cả hai bên.

**Ranh giới TEST:** phần TEST (nến > 51318, sau 2026-09-15) chỉ so **định danh** (giờ, thế, hướng, range, mốc, dấu hiệu, entry/SL/TP, R sẵn); cột kết cục/R/nến thoát bị bỏ trước khi so, không in, không ghi file; không liệt kê từng lệnh TEST.

## Kết quả

| Phép so | khớp / tổng |
|---|---|
| **TRAIN lệnh (kể cả kết cục, R, nến thoát)** — C# chạy phần TRAIN | **97/97** |
| TRAIN ứng viên (mọi CF qua ②: dấu hiệu, cổng, entry/SL/TP, R sẵn) | 10094/10094 |
| **TRAIN lệnh (kể cả kết cục)** — C# chạy TOÀN file một lần | **97/97** |
| TRAIN ứng viên — C# toàn file | 10094/10094 |
| **TEST lệnh — CHỈ định danh** | **66/66** |
| TEST ứng viên — chỉ định danh | 7302/7302 |

Hồi quy TRAIN: Python 97 lệnh (thế A 43, thế B 54) = C# 97 lệnh.

## Lệch có chủ đích

- **Tin USD** (`IsNewsBlocked`, ±15′ tin mức cao): chỉ C# có; ReplayCorven không có lịch tin nên không phát sinh trong phép so.
- **Nến cuối phiên**: Python gắn cổng `cuoi_phien` khi CF là nến cuối phiên (biết trước). C# gắn `cuoi_phien` khi `sm ≥ 1379` (nến mở 16:59 ET — cách nhân quả duy nhất) và giữ cơ chế **huỷ** ở BenzoEngine làm lưới dự phòng (ngày đóng sớm / thiếu nến) — kết quả lệnh giống hệt; cột `gates` bỏ `cuoi_phien` ở **cả hai phía** trước khi so.
- **Range chồng range / mục tiêu thế B**: Python đọc cạnh range cũ ở CUỐI file (nhìn trước nhẹ), C# đọc tại lúc xét. Không gây lệch nào trên file này (số khớp ở trên).

File đối chiếu TRAIN từng lệnh: `report/_parity_corven_train.csv`.

