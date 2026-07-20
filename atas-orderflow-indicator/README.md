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

## Cài đặt

### Cách 1 — thả file .cs (dễ nhất)
ATAS tự biên dịch các file `.cs` đặt trong thư mục nguồn indicator:
1. Chép `OrderFlowBubbles.cs` vào `Documents\ATAS\Indicators` (một số bản là `%APPDATA%\ATAS\Indicators` — kiểm tra máy bạn).
2. Mở/khởi động lại ATAS → thêm indicator **"OrderFlow Bubbles"** vào chart footprint.
3. Nếu ATAS báo lỗi compile → xem [Checklist rủi ro](#checklist-rủi-ro).

### Cách 2 — build DLL (Visual Studio 2022+ / Rider trên Windows)
1. Sửa `OrderFlowBubbles.csproj`: `<TargetFramework>` và `<AtasDir>` cho khớp bản ATAS.
2. `dotnet build -c Release` → copy DLL vào thư mục Indicators của ATAS.

## Checklist rủi ro (sửa nhanh nếu ATAS báo lỗi)
Xếp theo khả năng phải động tới:

1. **Màu (`ObjectColor = color`)** — `ObjectColor` là kiểu `CrossColor` của ATAS, code đang gán `System.Windows.Media.Color` nhờ *implicit conversion*. Nếu báo lỗi ép kiểu → sửa **một chỗ** trong hàm `AddBubble`: đổi `ObjectColor = color` thành `ObjectColor = color.Convert()` (hoặc cách chuyển CrossColor mà bản ATAS của bạn cung cấp).
2. **`_render[bar].Clear()` / `.Add(...)`** — nếu kiểu collection khác, đây là chỗ cần khớp với `ClusterSearch.cs` (mẫu gốc). Về bản chất pattern này đã kiểm chứng.
3. **`ObjectsTransparency`** — chưa rõ thang 0–100 hay 0–255. Nếu halo/độ trong nhìn sai → chỉnh `HaloTransparency`/`SolidTransparency` trong Settings (hoặc đảo thang).
4. **`_render.IsHidden`, `base(true)`** — nếu compiler than, bỏ dòng `IsHidden` / đổi ctor `base()`; không ảnh hưởng logic.
5. **Ngưỡng volume CHƯA chuẩn cho MGC** — mọi z-score/volume là *điểm khởi đầu*, PHẢI tinh chỉnh live (xem dưới).

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
