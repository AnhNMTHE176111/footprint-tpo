# quantower-entry-signal — Gợi ý điểm vào lệnh (footprint M1)

Indicator M1 real-time gợi ý Entry/SL/TP cho vàng theo cách người dùng đánh (bias + vùng + footprint,
2 kịch bản phá&hồi / chạm&đảo). **Thiết kế đầy đủ ở [PLAN.md](PLAN.md).** Chưa implement.

## Phát hiện then chốt (backtest 28 ngày dữ liệu thật)
- Tín hiệu cơ học **thô** (bắn ở mọi vùng) **không có edge** — tệ hơn ngẫu nhiên (MFE/MAE 0.86 vs 1.05).
- **HỢP LƯU ≥2 vùng chồng nhau = bộ lọc THẬT:** +0.30R@2R (74 lệnh), đơn điệu theo bậc confluence,
  **giữ ở cả 2 nửa tháng** (chống overfit). ~3 lệnh/ngày.
- Phá&hồi > chạm&đảo. SL 2–4đ > 6đ. VSA/climax/VWAP-đơn-lẻ **không** tự tạo edge → chỉ là thành phần hợp lưu.
- Lớp **footprint theo mức giá (hấp thụ/imbalance)** chỉ có **LIVE** → validate bằng log, không backtest được.

## Research (tái lập số)
```bash
python3 research/entry_month.py   # backtest chính 28 ngày (4 cấu hình + soi 2 ví dụ 7/24)
python3 research/research.py      # MFE/MAE vs baseline + subset + SL sweep
python3 research/research2.py     # chống overfit: đơn điệu confluence + chia đôi 28 ngày
python3 research/profile_data.py  # mổ cột dữ liệu (cột sống/chết)
```

## Trạng thái
PLAN + research xong. Chờ user review PLAN → hạ effort để code (thứ tự phase ở PLAN §8).
```
