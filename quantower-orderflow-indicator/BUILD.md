# Build & nạp OrderFlow Bubbles (QUANTOWER)

> Bản port của indicator ATAS cùng tên. Quantower là app **Windows-only** — nhưng ta vẫn
> **build DLL trên Linux** (giống ATAS) rồi copy sang máy Windows chạy Quantower.

## Cách nhanh (máy dev Linux này)
Bộ build đã dựng sẵn: DLL tham chiếu Quantower lưu ở `~/quantower-libs/`, .NET 10 SDK ở `~/.dotnet`.
```bash
~/quantower-libs/qw-rebuild.sh
```
→ tạo `quantower-orderflow-indicator/dist/OrderFlowBubbles.dll` (**net10.0-windows**, khớp Quantower 1.146.x).
Commit + push, rồi máy Windows tải về.

## Nạp DLL vào Quantower (máy Windows)
1. Tải DLL đã build (sau khi push lên GitHub):
   ```powershell
   [Net.ServicePointManager]::SecurityProtocol='Tls12'; iwr "https://raw.githubusercontent.com/AnhNMTHE176111/footprint-tpo/main/quantower-orderflow-indicator/dist/OrderFlowBubbles.dll" -OutFile "$env:USERPROFILE\Downloads\OrderFlowBubbles.dll"
   ```
2. Tạo thư mục **riêng** trong kho indicator của Quantower và bỏ DLL vào:
   ```
   <Quantower>\Settings\Scripts\Indicators\OrderFlowBubbles\OrderFlowBubbles.dll
   ```
   - `<Quantower>` = thư mục cài Quantower (bản portable). Nếu không thấy `Settings` ở đó, thử mặc định:
     `C:\Users\<User>\Documents\Quantower\Settings\Scripts\Indicators\OrderFlowBubbles\`
   - **Bắt buộc để trong 1 thư mục con** (tên tuỳ ý) — Quantower quét theo thư mục.
3. **Khởi động lại Quantower** (không hot-reload DLL ngoài).
4. Trên chart: chuột phải → **Indicators → Add Indicator** → nhóm **Custom** → **OrderFlow Bubbles** → Double-click.

## ⚠️ ĐIỀU KIỆN BẮT BUỘC — phải có dữ liệu Volume Analysis (footprint)
Indicator implement `IVolumeAnalysisIndicator` và đọc `bar.VolumeAnalysisData.PriceLevels`.
- Chỉ chạy khi data feed **có lịch sử trade thật** (futures CME: AMP/CQG, dxFeed, Rithmic…).
- Feed **không có volume/trade thật** (vài CFD) → `PriceLevels` rỗng → không có bubble.
- Lần đầu add: Quantower **nạp volume analysis** (có % tiến trình); bubble hiện sau khi nạp xong.

## Build trên Windows (nếu tự làm bằng Visual Studio / dotnet)
Xem `OrderFlowBubbles.csproj`. Chỉnh `<QuantowerDir>` = thư mục cài Quantower, rồi `dotnet build -c Release`.
Reference cần: `TradingPlatform.BusinessLayer.dll` + `System.Drawing.Common.dll` (trong `…\TradingPlatform\v<ver>\bin\`).

## Bộ reference DLL lấy từ đâu (tái lập)
DLL tham chiếu được trích **từ chính installer Quantower** (Windows-only, không có gói NuGet):
```bash
# innoextract cài không cần root: apt-get download innoextract libboost-* liblzma5 ; dpkg -x *.deb tools/
innoextract Quantower.exe -d out --include "bin"
# lấy 2 file: app/TradingPlatform/v<ver>/bin/TradingPlatform.BusinessLayer.dll
#             app/TradingPlatform/v<ver>/bin/System/System.Drawing.Common.dll
cp <2 file trên> ~/quantower-libs/
```
> Khi Quantower **update lên bản .NET khác** (hiện 1.146.16 = net10.0): trích lại 2 DLL này và
> chỉnh `<TargetFramework>` trong `qw-rebuild.sh` cho khớp, rồi build lại.

## Checklist rủi ro (nếu không hiện bubble)
1. Feed không có trade thật → `PriceLevels` rỗng. Kiểm bằng cách bật **Footprint/Cluster chart native** của Quantower: nếu native cũng trống thì do feed.
2. Chưa nạp xong Volume Analysis → chờ % chạy hết.
3. Ngưỡng quá cao (z-score, min volume) trên MGC → hạ xuống (xem README).
4. Sai thư mục con trong `Settings\Scripts\Indicators\` → không thấy trong nhóm Custom.
