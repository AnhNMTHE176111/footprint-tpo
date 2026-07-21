# Build & nạp DLL (chỉ cần khi sửa code)

> Đã cài xong indicator rồi thì **không cần đọc file này**. Chỉ dùng khi muốn build lại sau khi sửa code.

## Cách nhanh (máy dev Linux này)
Bộ build đã dựng sẵn: DLL ATAS lưu ở `~/atas-libs/`, .NET 10 SDK ở `~/.dotnet`.
```bash
cd ~/atas-libs && ./rebuild.sh
```
→ tạo `atas-orderflow-indicator/dist/OrderFlowBubbles.dll`. Commit + push, rồi máy Windows tải về.

## Tải DLL đã build về Windows
```powershell
[Net.ServicePointManager]::SecurityProtocol='Tls12'; iwr "https://raw.githubusercontent.com/AnhNMTHE176111/footprint-tpo/main/atas-orderflow-indicator/dist/OrderFlowBubbles.dll" -OutFile "$env:USERPROFILE\Downloads\OrderFlowBubbles.dll"; explorer "$env:USERPROFILE\Downloads"
```
Rồi trong ATAS: **Indicators → Add custom indicator** chọn file DLL, **khởi động lại ATAS** (không hot-reload).

## Build trên máy Windows (nếu tự làm)
Cần Windows + .NET SDK + `dotnet` CLI. ATAS **không có gói NuGet** → `.csproj` tham chiếu trực tiếp DLL trong thư mục cài ATAS.
1. Xem DLL ATAS thuộc `net8.0` hay `net10.0` → đặt `<TargetFramework>` khớp. **ATAS của bạn = `net10.0-windows`** (bản 8.0.14.392).
2. Sửa `<AtasDir>` trong `OrderFlowBubbles.csproj` = thư mục cài ATAS (`C:\Program Files (x86)\ATAS Platform`).
3. `dotnet build -c Release` → DLL ra ở `bin\Release\OrderFlowBubbles.dll` (có target tự copy vào `Documents\ATAS\Indicators`).

**Reference cần** (đã cấu hình sẵn): `ATAS.Indicators`, `ATAS.DataFeedsCore`, `OFT.Rendering`, `OFT.Attributes`, `OFT.Localization`, `Utils.Common` — tất cả `<Private>false</Private>`, build **AnyCPU**, không ký assembly.

## Checklist rủi ro compile (nếu build lỗi)
1. **`ObjectColor = color`** — nếu lỗi ép kiểu, đổi thành `ObjectColor = color.Convert()` trong `AddBubble`.
2. **`Color` mập mờ (CS0104)** — đã xử lý bằng alias `using Color = System.Windows.Media.Color;` + fully-qualify `System.Drawing.*`. **KHÔNG thêm `using System.Drawing;` trần.**
3. **`DrawString`/`MeasureString` (CS1061)** — là extension, cần cả `using OFT.Rendering.Context;` và `using OFT.Rendering.Tools;`.
4. **`OnRender` không chạy** → thiếu `EnableCustomDrawing = true;` trong ctor.
5. **CS1705 "higher version"** → sai TargetFramework (net8 vs net10). ATAS của bạn = net10.

## Cách phụ — thả file .cs
Vài bản ATAS tự compile `.cs` trong `Documents\ATAS\Indicators`. Bản của bạn **nạp DLL** (đã xác nhận) → dùng DLL.
