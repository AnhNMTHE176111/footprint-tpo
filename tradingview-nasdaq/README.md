# TradingView — Nasdaq

- Chart: `OANDA:NAS100USD` (TradingView, miễn phí, khối lượng là tick volume của OANDA).
- Vào lệnh: `USTEC` trên Exness.
- Phương pháp: volume profile + VWAP.

## File
- `benzo-volume-profile.pine` — indicator **Benzo Volume Profile** đang dùng trên TradingView
  (Pine v6): profile theo phiên (mặc định 1 ngày) có POC + Value Area 70%, tách khối lượng nến tăng/giảm,
  VWAP phiên kèm 3 dải lệch chuẩn, cảnh báo cắt POC / VAH / VAL / VWAP.
  Gộp volume profile + VWAP trong 1 indicator để vừa giới hạn 2 indicator/chart của gói miễn phí.
- `benzo-volume-profile.inputs.json` + `benzo-volume-profile.script.js` — bản **thefreechart.com**
  (Build Indicators → New Indicator: dán JSON vào tab Inputs, JS vào tab Script; Overlay bật).
  Profile Week/Day (Day màu xanh dương + vàng), POC + VA, VWAP + 3 dải σ, vùng **HVN** tự nhận diện:
  cụm chữ D (loại khối chữ nhật, cụm volume thấp, cụm lệch một phía), vùng = lõi dày ≥ 70% đỉnh,
  trên giá = sell, dưới giá = buy, giá trong vùng = xám. Week: tuần này + tuần trước, chồng nhau thì gộp
  (CORVEN). Day: hôm nay + N ngày, chồng nhau thì giữ 1 khung uy tín nhất (ghi số ngày).
  Bản trong `hvn-handoff/` là bản cũ lúc bàn giao.
