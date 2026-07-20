# SPEC — Order Flow Bubble Indicator cho ATAS (v0.2)

> Bản thiết kế do người học + Claude cùng chốt. Đây là indicator **của riêng mình** (lấy cảm hứng từ indicator bubble của một người bạn chạy trên Sierra Chart), build cho **ATAS**, ưu tiên tín hiệu **limit / hấp thụ (passive)**.

## 1. Mục tiêu & phạm vi
- **Một** indicator duy nhất chứa **tất cả** loại tín hiệu order flow, vẽ dạng **bubble/hình** trên chart.
- **Mỗi tín hiệu bật/tắt được** trong Settings.
- **Default gọn nhất – đủ để trade nhất**: chỉ bật nhóm A (passive/absorption core), nhóm B/C tắt sẵn.
- Nền tảng: **ATAS**, custom indicator C# (DLL). Dữ liệu **tick bid/ask thật** (người dùng đã xác nhận có).
- Sản phẩm mẫu: **MGC (Micro Gold Futures, COMEX), khung M1**.

## 2. Hệ mã hoá 3 kênh (nguyên tắc cốt lõi — giữ chart dễ đọc)
Rút từ research: dùng màu để mã hoá *loại tín hiệu* là không chuẩn hoá và gây rối. Ta tách bạch:

| Kênh | Mã hoá | Quy ước |
|---|---|---|
| **MÀU** | Phe **aggressor** (kẻ vượt spread) | Cyan = mua chủ động · Đỏ/Cam = bán chủ động |
| **HÌNH** | **Loại** tín hiệu | dot = big trade · ring/halo = absorption · diamond = stacked imbalance · triangle = exhaustion · square = iceberg · (xem §3) |
| **KÍCH THƯỚC** | **Độ mạnh** | to = volume / cường độ lớn |

- Bubble **neo theo PRICE-LEVEL** (đúng mức giá trong footprint của nến), không phải 1 bubble/nến.
- Nhãn chữ ("Hấp thụ", "exhaustion"...) và hộp Entry/Stop/Target: **KHÔNG làm** (bên bạn ấy gõ tay) → ngoài scope.

## 3. Catalog tín hiệu

### Nhóm A — Passive / Limit (DEFAULT BẬT)
| Tín hiệu | Hình | Điều kiện phát hiện |
|---|---|---|
| Buy/Sell **Absorption** | ring/halo | volume cao bất thường (z-score) + 1 phe áp đảo (imbalance ≳60%) **nhưng giá dịch rất ít** tại mức đó |
| Buy/Sell **Exhaustion** | triangle | tại cực trị: volume + delta **teo dần**, prints cuối nhỏ hẳn, delta sụp ở tick cuối |
| **Iceberg** | square | cùng 1 mức giá **nạp lại** liên tục: khớp nhiều hơn size hiển thị, nuốt lệnh mà giá đứng |
| **Stop-hunt → hấp thụ** | ring + viền | quét thanh khoản qua cực trị rồi bị hấp thụ ngược |

### Nhóm B — Aggressive / Continuation (DEFAULT TẮT)
| Tín hiệu | Hình | Điều kiện |
|---|---|---|
| **Big trade** | dot | 1 lệnh (hoặc chuỗi cùng chiều) ≥ ngưỡng volume |
| **Stacked imbalance** | diamond | ≥3 mức giá liên tiếp tỷ lệ chéo ask/bid > ~3:1 |
| **Delta surge** | dot đậm | delta 1 nến vượt ngưỡng (momentum) |
| **Delta divergence** | mark | giá tạo đỉnh/đáy mới nhưng delta không xác nhận (pivot) |
| **Liquidity sweep** | mũi tên | chuỗi nhanh ăn nhiều mức 1 chiều |
| **Unfinished business** | vạch | đấu giá dở ở biên nến (còn bid/ask cả 2 phía ở cực trị) |

### Nhóm C — Bối cảnh (overlay, DEFAULT TẮT trừ Cumulative Delta)
- Cumulative Delta (subpanel) · VWAP + bands · HVN/LVN · Value Area shading.

## 4. Default "gọn để trade"
Bật sẵn: **Absorption (mua/bán) + Exhaustion (mua/bán) + Iceberg**. Tất cả còn lại tắt.
Lý do: đúng triết lý limit/absorption; chart không bị nhiễu; giống độ "sạch" của bản bạn ấy.

## 5. Nền tảng & môi trường
- ATAS custom indicator C# → biên dịch thành DLL, nạp vào thư mục Indicators của ATAS.
- Máy dev (Linux) **không có .NET/ATAS SDK** → chỉ viết source + hướng dẫn; **compile & test trong ATAS**.
- Ngưỡng mặc định theo MGC (tick size, tick value, volume điển hình) — xem phần code sau research.

## 6. Việc còn phải kiểm nghiệm trong ATAS (vì ta tự giải mã, không có legend gốc)
1. Ngưỡng z-score volume / imbalance % / big-trade volume → tinh chỉnh live cho MGC M1.
2. Xác nhận absorption đảo chiều thật (thu thập thêm screenshot có "giá sau đó").
3. Đối chiếu bubble mình sinh ra vs Big Trades / Cluster Search native của ATAS để canh ngưỡng.

---
*Trạng thái: chờ kết quả research API để viết code. Cập nhật dần khi tinh chỉnh.*
