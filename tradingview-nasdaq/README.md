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
  Profile tuần và profile ngày bật/tắt độc lập ("Show Week Profile", "Show Day Profile"; ngày màu xanh dương
  + vàng; "Profile Data Timeframe" chọn nến 1m / 5m / 15m / 30m để dựng profile + HVN/LVN; VWAP luôn tính từ nến 1m, mặc định neo theo ngày). HVN/LVN lấy theo tuần khi profile tuần bật, chỉ bật profile ngày thì theo ngày; "Hide Candles" ẩn nến bằng barColor trong suốt,
  chỉ còn profile + các vùng/đường đang bật), POC + VA, VWAP + 3 dải σ, vùng **HVN** tự nhận diện:
  cụm chữ D (loại khối chữ nhật, cụm volume thấp, cụm lệch một phía), vùng = lõi dày ≥ 70% đỉnh,
  trên giá = sell, dưới giá = buy, giá trong vùng = xám. Week: tuần này + tuần trước, chồng nhau thì gộp
  (CORVEN). Day: hôm nay + N ngày, chồng nhau thì giữ 1 khung uy tín nhất (ghi số ngày).
  Bản trong `hvn-handoff/` là bản cũ lúc bàn giao.
  Vùng **LVN** (bật/tắt riêng, viền nét đứt; dưới giá xanh nhạt, trên giá cam): khe mỏng giữa 2 cụm thật
  (mỗi cụm ≥ 8% volume, đỉnh ≥ 25% POC), đáy khe ≤ 50% đỉnh nhỏ hơn, vùng = phần mỏng nhất của khe.
  Week: tuần này + tuần trước; 2 LVN chồng nhau thì gộp thành 1 vùng phủ cả hai (ghi "· 2 tuần").
  Day: hôm nay + hôm qua, cùng luật. LVN tuần trước bị tuần này lấp giữa bằng cụm volume thì bỏ; chạm HVN
  thì HVN thắng (LVN bị cắt phần chồng).
  Đo GCZ26 T8–T10/2026 (giá rời ≥ 0,5u rồi quay lại chạm, trong 8 h: bật lại 1u hay xuyên qua 1u, so vùng
  ngẫu nhiên cùng độ rộng): LVN tuần bật lại 44% vs ngẫu nhiên 59%, xuyên qua 37% vs 31% (n = 43, chưa đủ
  ý nghĩa thống kê) — nghiêng về "giá trượt qua LVN" như CORVEN, **không** dùng LVN như vùng bật như HVN.
  LVN ngày ≈ ngẫu nhiên (n = 31).
