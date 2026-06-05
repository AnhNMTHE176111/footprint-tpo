# Glossary — Thuật ngữ Footprint / Order Flow (EN ↔ VN)

> Hai PDF dịch bằng máy nên **nhiều thuật ngữ sai**. Bảng này là chuẩn dùng chung. Cột "Dịch máy" là từ sai hay gặp trong PDF để bạn không bị rối khi đọc.

## ⚠️ Lỗi dịch máy hay gặp nhất
| Từ đúng (EN) | Tiếng Việt chuẩn | Dịch máy SAI trong PDF |
|---|---|---|
| Delta | Delta | **Đồng bằng** / đồng bằng |
| Volume | Khối lượng | **Âm lượng** (đôi chỗ) |
| High Volume Node (HVN) | Nút khối lượng cao | **Nút âm lượng cao** |
| Footprint | Biểu đồ Footprint | Dấu chân |
| Bar / Candle | Nến / thanh | **quán bar**, "bar" |
| Unfinished Business | Phiên đấu giá chưa hoàn tất | Công việc chưa hoàn thành |
| Absorption | Sự hấp thụ | (ổn) Sự hấp thụ |

## 📐 Khái niệm cốt lõi
| EN | VN | Giải thích ngắn |
|---|---|---|
| **Order Flow** | Dòng lệnh / luồng lệnh | Dòng chảy lệnh mua–bán thực tế đang khớp trên thị trường |
| **Footprint** | Biểu đồ Footprint | Nến hiển thị **khối lượng khớp tại từng mức giá** bên trong nó (xem được mua/bán ở mỗi giá) |
| **Bid** | Giá chào mua | Giá tốt nhất người mua sẵn sàng trả. **Lệnh bán chủ động** khớp tại đây |
| **Ask / Offer** | Giá chào bán | Giá tốt nhất người bán chấp nhận. **Lệnh mua chủ động** khớp tại đây |
| **Bid x Ask** (trong 1 ô) | (KL bán ở Bid) × (KL mua ở Ask) | Cách đọc một ô footprint: trái = bán chủ động, phải = mua chủ động |
| **Delta** | Delta | `Delta = KL mua chủ động (Ask) − KL bán chủ động (Bid)`. Dương = phe mua chủ động mạnh hơn |
| **Cumulative Delta (CVD)** | Delta tích lũy | Cộng dồn Delta qua nhiều nến → xem áp lực mua/bán tích lũy |
| **Delta Divergence** | Phân kỳ Delta | Giá và Delta đi ngược nhau (vd giá tạo đỉnh mới nhưng Delta yếu) → cảnh báo đảo chiều |

## 🧱 Lệnh & người tham gia
| EN | VN | Giải thích |
|---|---|---|
| **Market Order** | Lệnh thị trường | Khớp **ngay** ở giá tốt nhất → người **chủ động (aggressive)**, làm giá di chuyển |
| **Limit Order** | Lệnh giới hạn | Đặt **chờ** ở một giá → người **thụ động (passive)**, cung cấp thanh khoản |
| **Passive participant** | Người tham gia thụ động | Đặt limit, chờ được khớp |
| **Active / Aggressive participant** | Người tham gia chủ động | Đánh market, "ăn" vào limit của người khác |
| **Large Limit Order / Iceberg** | Lệnh giới hạn lớn / lệnh tảng băng | Lệnh chờ khối lượng lớn (có thể ẩn) → tường mua/bán |

## 📊 Volume Profile & cấu trúc khối lượng
| EN | VN | Giải thích |
|---|---|---|
| **Volume Profile** | Hồ sơ khối lượng | Biểu đồ phân bố **khối lượng theo từng mức giá** (ngang) |
| **POC (Point of Control)** | Điểm kiểm soát | Mức giá có khối lượng giao dịch **lớn nhất** |
| **Value Area (VA)** | Vùng giá trị | Vùng chứa ~**70%** khối lượng quanh POC |
| **HVN (High Volume Node)** | Nút khối lượng cao | Mức giá tích lũy **nhiều** khối lượng → hay làm S/R, vùng giá "công bằng" |
| **LVN (Low Volume Node)** | Nút khối lượng thấp | Mức giá **ít** khối lượng → giá thường đi nhanh qua |
| **D / P / b / thin profile** | Hình dạng hồ sơ chữ D, P, b, mỏng | Hình dạng phân bố KL → gợi ý cân bằng/xu hướng |

## 🎯 Tín hiệu Footprint / setup
| EN | VN | Giải thích |
|---|---|---|
| **Volume Cluster** | Cụm khối lượng | Vùng tập trung khối lượng lớn trên footprint |
| **Imbalance** | Mất cân bằng | Chênh lệch lớn giữa mua chủ động và bán chủ động (so chéo Bid/Ask giữa các mức giá) |
| **Stacked Imbalance** | Mất cân bằng xếp chồng | Nhiều imbalance **liên tiếp** cùng phía → lực mạnh |
| **Absorption** | Hấp thụ | Lệnh limit lớn "nuốt" hết lực đối nghịch mà **giá không đi** → sắp đảo chiều |
| **Exhaustion** | Cạn kiệt | Lực đẩy yếu dần ở cuối xu hướng |
| **Unfinished Business / Unfinished Auction** | Phiên đấu giá chưa hoàn tất | Đỉnh/đáy nến vẫn có khớp **cả 2 phía** (không có mức = 0) → giá hay quay lại "hoàn tất" |
| **Trade Filter** | Bộ lọc giao dịch | Tính năng của TD Orderflow lọc tín hiệu |
| **Divergence** | Phân kỳ | Hai chỉ số/giá đi ngược nhau |

## 💰 Quản lý lệnh & nền tảng
| EN | VN |
|---|---|
| Take Profit (TP) | Chốt lời |
| Trailing (TP/Stop) | Dời chốt lời/dừng lỗ theo giá |
| Stop Loss (SL) | Dừng lỗ / cắt lỗ |
| Support / Resistance | Hỗ trợ / Kháng cự |
| Tick | Tick (bước giá nhỏ nhất) |
| NinjaTrader 8 | Nền tảng giao dịch (dùng trong tài liệu) |
| CQG | Nguồn cấp dữ liệu (data feed) hợp đồng tương lai |
| Futures / Forex | Hợp đồng tương lai / Ngoại hối |

> Thiếu từ nào trong lúc học, mình sẽ bổ sung vào đây.
