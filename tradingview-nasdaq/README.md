# TradingView — Nasdaq

- Chart: `OANDA:NAS100USD` (TradingView, miễn phí, khối lượng là tick volume của OANDA).
- Vào lệnh: `USTEC` trên Exness.
- Phương pháp: volume profile + VWAP.

## File
- `benzo-volume-profile.pine` — indicator **Benzo Volume Profile** đang dùng trên TradingView
  (Pine v6): profile theo phiên (mặc định 1 ngày) có POC + Value Area 70%, tách khối lượng nến tăng/giảm,
  VWAP phiên kèm 3 dải lệch chuẩn, cảnh báo cắt POC / VAH / VAL / VWAP.
  Gộp volume profile + VWAP trong 1 indicator để vừa giới hạn 2 indicator/chart của gói miễn phí.
