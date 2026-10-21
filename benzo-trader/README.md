# Benzo Trader — KHUNG indicator (chưa có logic 4 setup)

Trục thiết kế: `plans/BENZO-TRADER-plan.md` (mục 2, 2.2, 2.3, 6). Bản này chỉ dựng **đường ống**: nhận nến M1 đã đóng →
(chỗ cắm 4 detector, hiện RỖNG) → mô phỏng SL/TP → thống kê → bảng + mũi tên → Telegram kèm ảnh → CSV log.

## Build / deploy / test
```bash
cd benzo-trader
./build.sh            # concat ProfileEngine.cs + BenzoCore.cs + BenzoTrader.cs → dist/BenzoTrader.dll
dotnet run --project tests            # unit test (Debug, gồm test DemoDetector)
dotnet run -c Release --project tests # bản ship: không có DemoDetector
```
- `build.sh` copy thẳng vào `C:\OptimusFLOW\Settings\Scripts\Indicators\BenzoTrader\` (TẠO thư mục nếu chưa có).
- Cần `~/quantower-libs/{TradingPlatform.BusinessLayer,System.Drawing.Common,System.Private.Windows.Core}.dll`.
  `System.Private.Windows.Core.dll` lấy từ `C:\OptimusFLOW\TradingPlatform\v*\bin\System\` (cần để dùng `Bitmap`/`Graphics.FromImage`
  khi chụp ảnh); `qw-build.sh` tự thêm tham chiếu nếu file này có mặt.
- Add indicator vào **chart M1 có Volume Analysis**.

## Cấu trúc file
| File | Vai trò |
|---|---|
| `BenzoCore.cs` | Logic thuần, KHÔNG phụ thuộc SDK: `Signal`, `BarData`, `ISetupDetector`, `SetupContext`, `BenzoCore` (Simulate, thống kê, caption, mốc reset), `SignalCache`, `BenzoEngine`, `SignalCsv`, `TeleClient`, `DemoDetector` (chỉ DEBUG) |
| `BenzoTrader.cs` | Lớp dán Quantower: Settings, vòng đời, vẽ, chụp ảnh Win32, điều phối Telegram |
| `tests/` | Test chạy thật trên chính `BenzoCore.cs` |

## Settings (plan 2.3 — không có ngưỡng số nào)
Lệch giờ (7) · Telegram bật · bot token · chat id · **gửi thử** · bật setup A/B/C/D · **đặt lại thống kê** · Hiện bảng.
Hai "nút" là ô tick: **bật lên = bấm** (bắt cạnh lên; muốn bấm lần nữa thì tắt rồi bật lại).
Token/chat id điền tay, không có trong code.

## Vòng đời & chống tính lại
- Chỉ xử lý nến **đã đóng** (`Count−2`), mỗi nến dò **một lần**. `ClosedBars` chặn detector nhìn nến sau `closedIdx` (ném lỗi).
- **Niêm phong** `%LOCALAPPDATA%\BenzoTrader\cache_<symbol>_<khung>.jsonl`: dòng `sig` (tín hiệu) + dòng `rng` (khoảng thời gian đã dò).
  Nến trong khoảng đã dò **không dò lại** dù reload; kết quả TP/SL luôn tính lại từ nến. Đổi `BenzoCore.LogicVersion` (khi sửa logic detector)
  ⇒ cache cũ bị bỏ. Đổi công tắc A/B/C/D **không** dò lại lịch sử đã niêm phong (xoá file cache nếu muốn dò lại).
- 1 lệnh mở cùng lúc: khi còn lệnh mở thì không dò. Mô phỏng: chạm cả SL lẫn TP cùng nến ⇒ SL; chi phí 0,2 giá/lệnh.
- Mặc định thống kê đếm từ đầu lịch sử chart đã nạp; "Đặt lại thống kê" ghi mốc UTC vào `reset_<symbol>.txt`, chỉ đếm lệnh sau mốc.

## Telegram
- Tin mở = `sendPhoto` (ảnh + caption), tin đóng = `sendMessage`:
```
🟢 BUY · A Phá hồi · GCZ26 · 20:24 VN
Lý do: <Reason>
Vào 4193,1 · SL 4190,6 (2,5 giá) · TP 4200,6 (3R)

✅ A Phá hồi +2,8R · 20:24→20:51        (R đã trừ chi phí 0,2)
🛑 A Phá hồi −1,1R · 20:24→20:31
```
- Chống trùng: lần quét đầu sau reload chỉ nạp id; chỉ bắn khi tín hiệu ở **nến vừa đóng** và tuổi ≤ 90 giây; khoá file nguyên tử
  `%LOCALAPPDATA%\BenzoTrader\sent\` để nhiều chart cùng symbol chỉ gửi 1 lần mỗi id.
- Ảnh (`WinShot`): `GetWindowRect(Process.MainWindowHandle)` (không có thì cửa sổ foreground) → `Graphics.CopyFromScreen` → PNG.
  Lỗi ⇒ chụp toàn màn hình chính (`GetSystemMetrics`) ⇒ vẫn lỗi ⇒ gửi text không ảnh. Chụp + gửi chạy `Task.Run`, gửi ảnh tối đa 10 giây.
  **Giới hạn:** chụp từ màn hình thật nên cửa sổ Optimus Flow phải đang **hiện, không thu nhỏ, không bị cửa sổ khác che**.
- Log `%LOCALAPPDATA%\BenzoTrader\tele_log.txt` (token được che bằng `***`). Lỗi code ghi `error_log.txt`.

## CSV log
`%LOCALAPPDATA%\BenzoTrader\signals_<symbol>.csv` — header:
`time_utc,setup,side,entry,sl,tp,zone,reason,outcome,exit_time,r`. Ghi khi mở, cập nhật dòng đó khi đóng (khoá = time_utc+setup+side;
dòng cũ không còn trong bộ nhớ vẫn được giữ). `side` = BUY/SELL, `outcome` = OPEN/TP/SL, `exit_time`/`r` rỗng khi còn mở.

## Lịch tin
`NewsCalendar` (Forex Factory, trong `ProfileEngine.cs`) tải nền, cache 1 giờ. Đã thêm `NewsCalendar.IsBlocked(utc, tz, minutes)`;
indicator expose `IsNewsBlocked(DateTime utc)` (±15′ tin USD mức cao) và đưa vào `SetupContext.IsNewsBlocked`.
Giới hạn: feed chỉ phủ **tuần hiện tại** ⇒ với nến lịch sử cũ hơn luôn trả `false`.

## Cắm detector (cho agent port setup)
1. Viết class `: ISetupDetector` trong `BenzoCore.cs` (hoặc file mới, nhớ `using` bên trong namespace, thêm vào `build.sh` + `tests.csproj`).
2. `Signal TryDetect(SetupContext ctx, int closedIdx)`: nhìn `ctx.Bars[0..closedIdx]`; trả `new Signal{ Side, Entry, Sl, Tp, Reason, Zone }`
   hoặc `null`. `Setup` do engine gán từ `detector.Setup`; `Time/Id/Outcome` do engine gán.
3. Thêm vào `BenzoTrader.CreateDetectors()` **theo thứ tự ưu tiên A > B > D > C**.
4. Sửa logic ⇒ tăng `BenzoCore.LogicVersion`.
`SetupContext`: `Symbol, Tick, TzOffset, BarMinutes, Bars (ClosedBars), Signals (lệnh đã mở trước đó), GetLevels(idx) → LevelVol{Price,Bid,Ask}`
(Bid = sell chủ động, Ask = buy chủ động), `IsNewsBlocked(utc)`, `ToVn(utc)`.
`BarData`: `Idx, Time (giờ MỞ, UTC), O,H,L,C, Vol, BuyVol, SellVol, Delta`.
