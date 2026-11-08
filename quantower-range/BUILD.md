# Build & test Range Box

## Nguồn
- `RangeLogic.cs` — máy trạng thái range (logic thuần, port 1:1 từ `research/range_proto.py`).
- `RangeRenderer.cs` — vẽ GDI+ qua `IChartMap` (test render PNG không cần Quantower).
- `RangeBox.cs` — Indicator Quantower (chỉ OHLC, không Volume Analysis), 3 ô Settings.

## Toolchain (máy Windows này)
`.NET SDK 10` (`dotnet`) + `~/quantower-libs/{TradingPlatform.BusinessLayer, System.Drawing.Common, System.Private.Windows.Core}.dll`.
Chạy trong Git Bash, từ gốc repo.

## Thứ tự bắt buộc: test → build → kiểm DLL
```bash
dotnet run --project quantower-range/tests       # logic + đối chiếu Python↔C# (events_90d.csv) + PNG tests/ui-out/
bash quantower-range/build.sh                    # → quantower-range/dist/RangeBox.dll (lỗi hoặc cảnh báo => thoát 1)
dotnet run --project quantower-range/tests-dll   # phản chiếu DLL: 3 ô Settings, mặc định, OnClear
```
Đổi logic thì chạy lại Python trước rồi mới test C#:
```bash
cd quantower-range/research && python measure.py --events   # ghi lại events_90d.csv (bộ tham số chọn)
python measure.py && python measure.py --report             # quét lại tham số (~1 phút, 18 tiến trình)
```

## Nạp vào Optimus Flow / Quantower
`bash ~/quantower-libs/qw-deploy.sh quantower-range/dist/RangeBox.dll` (copy vào `C:\OptimusFLOW\Settings\Scripts\Indicators`,
không tự tạo thư mục mới), kiểm `cmp` khớp, khởi động lại app, chart → Add Indicator → nhóm Custom → **Range Box**.

## Đã kiểm API (tester, 2026-11-08 — `ilspycmd` trên `~/quantower-libs/TradingPlatform.BusinessLayer.dll` + `C:\OptimusFLOW\TradingPlatform1.146.4in\TradingPlatform.PresentationLayer.Plugins.dll`)
- **`Indicator.OnBackGround`** có thật (auto-property `bool`). Bên vẽ: `ChartIndicatorRenderer` gán `IsBackGround = indicatorModule.OnBackGround`;
  `ChartCustomDrawingRenderer` gọi `indicator.PaintChart` ở lượt `ChartToolRendererDrawingType.Background` khi `IsBackGround`, tức vị trí
  `IndicatorPosition.OnBackChart` = **vẽ dưới nến**. Dùng đúng, giữ nguyên.
- **`HistoricalData[i, SeekOriginHistory.Begin]`** = `items[i]`; `End` = `items[Count − 1 − i]`. `GetIndexByTime` tìm nhị phân `TicksLeft` tăng dần
  theo chỉ số `Begin`, và `Reload` lấy `this[0, Begin].TimeLeft` làm `FromTime` ⇒ **i = 0 là nến cũ nhất**. Dùng đúng.
- **`HistoricalData.Count`** = `items.Count` (tổng số nến đang có), KHÔNG tăng dần lúc nạp lịch sử: `Indicator.Update` chỉ tăng `Indicator.Count`
  (thuộc tính riêng của indicator) rồi gọi `OnUpdate`; `AddIndicator` gọi `Update(HistoricalBar)` đúng `Count` lần. ⇒ Lần `OnUpdate` đầu tiên
  `Process()` nạp một mạch `Count − 1` nến đã đóng, các lần sau không làm gì; `NewBar` làm `Count` tăng 1 ⇒ nến vừa đóng được nạp, **không bỏ sót**.
  Đã test bằng `HistoricalData` giả (indexer + `Count` là `virtual`) trong `tests-dll`: nạp lịch sử, NewBar, OnClear→OnUpdate, tải thêm lịch sử bên trái.
  Hạn chế đã biết: chart không có dữ liệu live (thị trường đóng) thì nến cuối coi là "đang chạy", chưa vào logic tới khi có nến mới.
- **`IChartWindowCoordinatesConverter.GetBarIndex(dt)`** (cài đặt: `CashItemPointsCoverter.GetBarIndex` → `ChartCashItemSeries.FindIntervalExactly`):
  chỉ số tính từ nến cũ nhất (khớp `Begin`), **ngoại suy** ra ngoài: thời gian trước nến 0 ⇒ số âm, sau nến cuối ⇒ `Count + phần lẻ`.
  Chính Quantower dùng `(int)GetBarIndex(GetTime(x))` rồi so với `historicalData.Count` (ChartCustomDrawingRenderer). Dùng đúng; li âm / ri > nến cuối
  đã được `BuildScene` xử lý (lọc theo khoảng).
- **`PaintChartEventArgs.MousePosition`** là `Point` (không nullable); Quantower truyền `Point.Empty` khi chưa có sự kiện rê chuột ⇒ `RangeBox.cs` nay
  coi `Point.Empty` hoặc chuột ngoài vùng chart là "không có chuột" (trước đây luôn truyền vào như có chuột ở (0,0)).
