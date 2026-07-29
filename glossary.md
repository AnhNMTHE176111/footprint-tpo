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

## 🕐 TPO / Market Profile *(Phụ lục TPO — bổ sung 2026-07-05)*
| EN | VN | Giải thích ngắn |
|---|---|---|
| **Market Profile / TPO chart** | Hồ sơ thị trường / biểu đồ TPO | Profile gom theo **THỜI GIAN** (≠ Volume Profile gom theo khối lượng): mỗi mức giá đếm số **bracket 30'** giá ghé qua |
| **TPO (Time Price Opportunity)** | Cơ hội giá theo thời gian | 1 chữ cái = giá chạm mức đó trong 1 bracket 30'; nhiều lệnh cùng giá cùng bracket vẫn chỉ in 1 TPO |
| **Bracket / Period** | Chu kỳ chữ cái | Mỗi 30 phút = 1 chữ (A, B, C…); `O` = giá mở cửa |
| **Initial Balance (IB)** | Khoảng cân bằng ban đầu | Phạm vi giá của **60 phút đầu phiên (bracket A+B)** — chuẩn hóa của mình, vì tài liệu tự mâu thuẫn |
| **Range Extension (RE)** | Mở rộng phạm vi | Giá vượt ra ngoài IB → đọc "ai kiểm soát phiên" |
| **Single Print** | Bản in đơn | Đoạn profile chỉ 1 TPO → giá đi quá nhanh, vết chân dòng tiền lớn → S/R tương lai |
| **Buying / Selling Tail** | Đuôi mua / đuôi bán | Single print ở **đáy/đỉnh** profile = từ chối giá quyết liệt; **đuôi càng dài càng ý nghĩa, đuôi 1 TPO vô nghĩa** |
| **Minus Development** | Phát triển thiếu | Single print ở **giữa** profile (tên của Steidlmayer) |
| **Poor High / Poor Low** | Đỉnh/đáy "đểu" | Đỉnh/đáy ≥2 TPO = đấu giá chưa ngã ngũ, dễ bị phá — chính là **Unfinished Business** nhìn bằng TPO |
| **Day types** | Phân loại ngày | Trend Day · Normal · Normal Variation · Neutral · Non-trend · Double Distribution — quyết định fade hay follow |
| **Open Drive / Open Test Drive / Open Rejection Reverse / Open Auction** | 4 kiểu mở cửa (Dalton) | Độ conviction của dòng tiền lớn giảm dần từ trái sang phải; đỉnh/đáy 30' đầu Open Drive = mốc invalidation ngày |
| **80% Rule** | Quy tắc 80% | Giá mở ngoài VA rồi quay vào + giữ 2 bracket → xu hướng xuyên hết VA sang mép đối diện |
| **Value Migration** | Dịch chuyển vùng giá trị | VA các phiên nâng dần/hạ dần/chồng nhau → đọc xu hướng đa phiên |
| **Composite Profile** | Profile gộp | Gộp nhiều phiên thành 1 profile (tuần/tháng) → level lớn |
| **TPO-POC vs VPOC** | POC theo thời gian vs theo khối lượng | Hai POC **không luôn trùng** — lệch nhau cũng là thông tin |
| **Ledge** | Gờ | ≥3 TPO bằng nhau tạo mép phẳng → level phụ |
| **Spike** | Cú nhọn cuối phiên | Đợt giá cuối phiên chưa kịp xây value → phân xử bằng vị trí mở cửa hôm sau |
| **OTF (Other Timeframe) trader** | Dòng tiền khung lớn | Người chơi dài hạn — kẻ tạo trend, phá IB, để lại tail/single print |

> ⚠️ Lỗi dịch riêng của tài liệu TPO: sách Keppler bản dịch có chỗ biến **mức giá thành giờ** (vd "13 giờ 10 phút" thực ra là **giá 1310**), số liệu chép sai — luôn đối chiếu hình gốc. Sách TraderViet: định nghĩa IB tự mâu thuẫn (đã chuẩn hóa = 60'), quy tắc Spike viết sai chiều. Cụm dịch máy hay gặp trong bản Keppler: "Hồ sơ thị trường" = Market Profile, "số dư ban đầu / khoảng cân bằng ban đầu" = Initial Balance, "phần mở rộng / phạm vi mở rộng" = Range Extension, "sự phát triển trừ/âm" = Minus Development, "bản in đơn" = Single Print, "gờ" = Ledge.

> Thiếu từ nào trong lúc học, mình sẽ bổ sung vào đây.

---

## 🤖 Thuật ngữ dự án indicator (Wyckoff Runner) — **CỐ ĐỊNH, không dùng từ đồng nghĩa**

Chốt 2026-07-30: trước đó Claude dùng lẫn "kịch bản"/"nhánh"/"setup" cho cùng một thứ, gây rối. Từ nay:

| Dùng từ này | KHÔNG dùng | Nghĩa |
|---|---|---|
| **kịch bản** (KB1/KB2/KB3) | ~~nhánh~~, ~~setup~~, ~~scenario~~, ~~branch~~ | Một cách vào lệnh độc lập. Chỉ có **3** kịch bản, cố định. |
| **CBR** | ~~phá range~~ (thiếu nghĩa) | Viết tắt **C**onsolidation → **B**reak → **R**etest → **R**esume: co cụm → phá → hồi về giữ mép → vào nến tiếp diễn. = KB1. |
| **QUAY ĐẦU** | ~~reversal~~, ~~đảo chiều~~ | Vào lệnh ngược khi giá bị VWAP đẩy lại. = KB2. |
| **biên↔biên** | ~~range scalp~~, ~~edge-to-edge~~ | Mua mép dưới / bán mép trên trong range. = KB3. |
| **BẬT / TẮT** | ~~enable~~, ~~on/off~~ | Trạng thái kịch bản trong DLL. |

**Ba kịch bản và trạng thái (theo `AUDIT_V7.md`, đóng băng):**

| | Tên đầy đủ | Trạng thái | Trong DLL |
|---|---|---|---|
| **KB1** | CBR (co cụm→phá→hồi→tiếp diễn) | ✅ PASS có điều kiện | **BẬT** — kịch bản duy nhất được cấp vốn |
| **KB2** | QUAY ĐẦU tại VWAP | ❌ FAIL (p=0.072, chết sau Bonferroni) | có code, **TẮT** (`EnableReversal=false`) |
| **KB3** | biên↔biên trong range | ❌ KILL (chết ở 2 tick phí) | **không có dòng code nào** |

⚠ "Cả 2 kịch bản" chỉ đúng khi nói về **thống kê lịch sử** (KB1+KB2 đã có số). Nói về **DLL đang chạy** thì
chỉ có **1 kịch bản: KB1**.
