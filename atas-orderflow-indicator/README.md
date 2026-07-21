# OrderFlow Bubbles — indicator order flow dạng bubble cho ATAS

Indicator **của riêng mình** (cảm hứng từ bản bubble trên Sierra Chart của một người bạn), gom **tất cả tín hiệu order flow** thành bubble/hình trên chart, **bật/tắt từng phần**, default gọn để trade. Xem [SPEC.md](SPEC.md) cho thiết kế đầy đủ.

> ⚠️ **Chưa compile được ở máy dev (Linux, không có ATAS SDK).** Mã viết bám sát API đã kiểm chứng, nhưng **phải build & test trong ATAS trên máy Windows của bạn.** Đọc [Checklist rủi ro](#checklist-rủi-ro) trước.

## Hệ mã hoá (đọc bubble thế nào)
| Kênh | Nghĩa |
|---|---|
| **Màu** | Phe chủ động: **cyan = mua** (Ask>Bid) · **cam/đỏ = bán** (Bid>Ask) |
| **Hình** | Loại tín hiệu: ⬤ Ellipse · ▲ Triangle · ▭ Rectangle · ◆ Diamond |
| **Kích thước** | Độ mạnh (z-score / tỷ lệ volume) — to = mạnh |

ATAS chỉ có **5 hình** (`Ellipse, Triangle, Rectangle, Diamond, OnlyCluster`) cho ~10 tín hiệu → vài loại **trùng hình**, phân biệt thêm bằng **màu + Tooltip** (rê chuột vào bubble để đọc tên tín hiệu).

| Tín hiệu | Hình | Default |
|---|---|---|
| Absorption (mua/bán) | ⬤ halo | **BẬT** |
| Exhaustion (mua/bán) | ▲ | **BẬT** |
| Stacked imbalance | ◆ | tắt |
| Big trade | ⬤ đặc | tắt |
| Delta surge | ⬤ | tắt |
| Delta divergence | ▲ | tắt (thử nghiệm) |
| Liquidity sweep | ▲ | tắt |
| Unfinished business | ▭ | tắt |
| Iceberg (xấp xỉ) | ▭ | tắt |
| Stop-hunt + absorption | ⬤ halo | tắt |

## Số Delta dưới nến (mới)
Ngoài bubble, indicator in **số delta tổng của mỗi nến ngay dưới đáy nến** (dưới râu nếu có râu) — thay cho việc phải đọc cả lưới số footprint.
- **Xanh = delta dương** (mua ròng) · **Đỏ = delta âm** (bán ròng) · xám = 0.
- Bật/tắt + chỉnh cỡ chữ, font, khoảng cách, nền mờ trong nhóm Settings **"Delta Numbers"** (default **BẬT**).
- Tự ẩn khi nến quá hẹp (`Chỉ vẽ khi bề rộng nến ≥ px`) để khỏi rối lúc zoom xa.
- Kỹ thuật: vẽ bằng `OnRender` (đường pixel), khác đường bubble — cần `EnableCustomDrawing=true` (đã set sẵn trong ctor).

### Màu nến nên để gì?
Khuyến nghị **nền nến trung tính** (rỗng/viền hoặc trắng-xám), **KHÔNG xanh–đỏ**: bubble đã dùng màu để mã hoá phe (cyan mua / cam bán), nếu thân nến cũng xanh–đỏ thì **nến đỏ đè bubble bán** → khó đọc. Trung tính → mọi màu trên chart đều là order-flow, mắt phóng thẳng vào tín hiệu (đúng lý do bản gốc dùng trắng/đen). Thân nến là **cài đặt của chart ATAS** (Chart → color scheme), không phải indicator này. Muốn giữ xanh–đỏ thì đổi màu bubble bán sang vàng/magenta để hết va chạm.

## Cài đặt

### Cách chính — build ra file DLL (ATAS của bạn nạp DLL)
Cần **Windows** + **.NET SDK** + Visual Studio 2022+/Rider (hoặc chỉ cần `dotnet` CLI). ATAS **không có gói NuGet** → `.csproj` tham chiếu trực tiếp DLL trong thư mục cài ATAS.

1. **Xác định TargetFramework**: mở thư mục cài ATAS, xem DLL thuộc `net8.0` hay `net10.0`.
   - ATAS thường (2024/2025) → `net8.0-windows`.
   - ATAS X (bản mới) → `net10.0-windows`, và `AtasDir = C:\Program Files\ATAS X`.
2. **Sửa `OrderFlowBubbles.csproj`**: đặt `<AtasDir>` = đúng thư mục cài ATAS (nơi có `ATAS.Indicators.dll`) và `<TargetFramework>` cho khớp bước 1.
3. **Build**: mở thư mục project, chạy `dotnet build -c Release` (hoặc bấm Build trong IDE).
   - DLL ra ở `bin\Release\<framework>\OrderFlowBubbles.dll`.
   - `.csproj` có target **tự copy** DLL vào `Documents\ATAS\Indicators` sau build (tắt được nếu không muốn).
4. **Nạp vào ATAS**: nếu chưa auto-copy → chép `OrderFlowBubbles.dll` vào `Documents\ATAS\Indicators`, **hoặc** trong ATAS mở cửa sổ Indicators → **"Add custom indicator"** chọn file DLL.
5. **Khởi động lại ATAS** (ATAS nạp DLL lúc mở, **không hot-reload**) → thêm **"OrderFlow Bubbles"** vào chart footprint.
6. Build lỗi/nạp lỗi → xem [Checklist rủi ro](#checklist-rủi-ro).

> **Reference cần trong .csproj** (đã cấu hình sẵn, lấy từ .csproj gốc của ATAS): `ATAS.Indicators`, `ATAS.DataFeedsCore`, `OFT.Rendering` (chứa `RenderContext`/`DrawString` — phần vẽ số delta), `OFT.Attributes`, `OFT.Localization`, `Utils.Common`. Tất cả để `<Private>false</Private>` (không kèm bản sao DLL của ATAS → tránh xung đột). Build **AnyCPU** (ATAS 64-bit), **không** ký assembly.

### Cách phụ — thả file .cs (nếu bản ATAS của bạn có tự biên dịch)
Một số bản ATAS tự compile file `.cs` trong `Documents\ATAS\Indicators`. Nếu bản bạn hỗ trợ: chép thẳng `OrderFlowBubbles.cs` vào đó rồi khởi động lại ATAS. Nếu không thấy indicator hiện ra → bản của bạn chỉ nạp DLL, dùng cách chính ở trên.

## Checklist rủi ro (sửa nhanh nếu ATAS báo lỗi)
Xếp theo khả năng phải động tới:

1. **Màu (`ObjectColor = color`)** — `ObjectColor` là kiểu `CrossColor` của ATAS, code đang gán `System.Windows.Media.Color` nhờ *implicit conversion*. Nếu báo lỗi ép kiểu → sửa **một chỗ** trong hàm `AddBubble`: đổi `ObjectColor = color` thành `ObjectColor = color.Convert()` (hoặc cách chuyển CrossColor mà bản ATAS của bạn cung cấp).
2. **`_render[bar].Clear()` / `.Add(...)`** — nếu kiểu collection khác, đây là chỗ cần khớp với `ClusterSearch.cs` (mẫu gốc). Về bản chất pattern này đã kiểm chứng.
3. **`ObjectsTransparency`** — chưa rõ thang 0–100 hay 0–255. Nếu halo/độ trong nhìn sai → chỉnh `HaloTransparency`/`SolidTransparency` trong Settings (hoặc đảo thang).
4. **`_render.IsHidden`, `base(true)`** — nếu compiler than, bỏ dòng `IsHidden` / đổi ctor `base()`; không ảnh hưởng logic.
5. **Ngưỡng volume CHƯA chuẩn cho MGC** — mọi z-score/volume là *điểm khởi đầu*, PHẢI tinh chỉnh live (xem dưới).

**Riêng phần vẽ số Delta (`OnRender`) — đã verify với docs + repo ATAS chính thức, nhưng lưu ý:**

6. **`Color` mập mờ (CS0104)** — file có `using System.Windows.Media;` mà `DrawString`/`FillRectangle` đòi `System.Drawing.Color`. Đã xử lý bằng `using Color = System.Windows.Media.Color;` (khoá `Color` trần = Media) + **fully-qualify `System.Drawing.*`** ở phần render. **TUYỆT ĐỐI không thêm `using System.Drawing;` trần** (sẽ vỡ toàn file).
7. **`DrawString`/`MeasureString` "không tồn tại" (CS1061)** — là extension trong `OFT.Rendering.Tools`. Cần **cả** `using OFT.Rendering.Context;` (kiểu `RenderContext`) **và** `using OFT.Rendering.Tools;` (đã thêm).
8. **`MeasureString` trả `Size` hay `SizeF`?** — chưa chắc 100%, nên dùng `var size = ...` rồi `(int)size.Width/.Height`; **đừng** khai báo cứng kiểu.
9. **`GetXByBar(bar,false)` / `GetYByPrice(price,false)`** — luôn truyền tham số bool thứ 2 (`false` = tâm bar / giữa price-level). Gọi qua `ChartInfo.PriceChartContainer`.
10. **`OnRender` không chạy** → thiếu `EnableCustomDrawing = true;` trong ctor (đã set).

Toàn bộ tín hiệu **tick-based thật** (iceberg/stop-hunt "chuẩn") đang được **thay bằng xấp xỉ level+bar** để tránh API tick chưa xác minh (`OnNewTrades`/`CumulativeTrade`/`MarketDataArg`). Khi đã xác nhận tên field trong SDK, có thể nâng cấp v2.

## Thông số MGC (Micro Gold, COMEX) — để đặt ngưỡng
- Tick size **0.10**, tick value **$1**, hợp đồng **10 oz**, point value **$10**. (Code đọc `InstrumentInfo.TickSize` lúc chạy, không hard-code.)
- Phiên Globex (giờ CT): CN 17:00 → T6 16:00, nghỉ bảo trì 16:00–17:00. Thanh khoản đỉnh trong RTH 08:20–13:30 (giờ ET).

## Tinh chỉnh & kiểm nghiệm (vì ta tự giải mã, chưa có legend gốc)
1. Bật **chỉ Absorption + Exhaustion** trước. Chỉnh `AbsorptionZ`, `AbsorptionImbalancePct`, `MaxDisplaceTicks`, `BaselineBars` tới khi bubble khớp các điểm giá đảo thật trên MGC M1.
2. So bubble với **Big Trades / Cluster Search native** của ATAS để canh ngưỡng volume.
3. Thu thập thêm screenshot có "giá SAU tín hiệu" → xác nhận đúng/sai từng loại.
4. Ngưỡng MGC nhỏ → nếu ít/không có bubble, **giảm** `ImbalanceMinVolume`, `BigTradeMinVolume`, các `z`.

## Chưa làm (dùng native ATAS thay thế)
VWAP + bands, Value Area, HVN/LVN, Cumulative Delta panel — **ATAS đã có sẵn native**, cứ thêm vào chart. Indicator này tập trung vào **bubble tín hiệu** (phần giá trị riêng).
