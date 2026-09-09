# "Xanh đầu đỏ đít" (CORVEN) — đo trên dữ liệu THEO MỨC GIÁ

**Nguồn:** `data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv` (583 MB,
per-level bid/ask) + file `_bars.csv` cùng tên. **724.279 nến M1**, 2024-08-01 → 2026-08-19.

**Cách dịch hình sang số** (đọc được ngay khi nến đóng, không nhìn trước):
- band **30% TRÊN** của nến: `ask > bid` ⇒ *xanh đầu* (mua chủ động đẩy lên đỉnh nến)
- band **30% DƯỚI** của nến: `bid > ask` ⇒ *đỏ đít* (bán chủ động đẩy xuống đáy nến)

Hình này **không phụ thuộc chiều** — nó nói "hai đầu nến đều do lệnh CHỦ ĐỘNG tạo ra rồi bị hấp thụ"
⇒ dùng y nguyên cho cả hấp thụ bán (ở đáy) và hấp thụ mua (ở đỉnh).

**Thước đo:** rào chắn đối xứng ±2×(trung vị biên độ 50 nến) từ giá đóng nến sự kiện, 60 nến,
bên nào chạm trước. Nền chuẩn = **50%**. Tách đôi thời gian: ngưỡng lấy từ nửa đầu.

## 1. Vấn đề lớn nhất: hình này KHÔNG HIẾM — nó là mặc định của gần như mọi nến

| Hình | tần suất trên MỌI nến |
|---|---|
| **xanh đầu + đỏ đít** | **47,5%** |
| xanh cả hai đầu | 19,2% |
| đỏ cả hai đầu | 19,2% |
| đỏ đầu + xanh đít | 5,1% |
| bản "đúng cực trị" (ask>bid tại giá cao nhất, bid>ask tại giá thấp nhất) | **67,4%** |
| imbalance xếp tầng ≥2 ở cả hai đầu | 2,3% |

Bản "đúng cực trị" chiếm 67,4% vì nó gần như là **hằng đúng cơ học**: giá cao nhất của nến được tạo
bởi một lệnh mua khớp ask, giá thấp nhất bởi một lệnh bán khớp bid. Một dấu hiệu xuất hiện ở
một nửa số nến thì không thể mang thông tin phân biệt.

## 2. Kết quả — mọi kiểu sắp xếp màu (để không thể nói là "dịch sai hình")

Tập **mọi nến** (nhãn = giá chạm +2u trước −2u):

| Hình | nửa đầu | nửa sau |
|---|---|---|
| **xanh đầu + đỏ đít (CORVEN)** | 50,2% (n=5.104) | 50,3% (n=5.066) |
| đỏ đầu + xanh đít | 52,6% (n=546) | 47,8% (n=552) |
| xanh cả hai đầu | 50,7% | 49,8% |
| đỏ cả hai đầu | 50,5% | 49,6% |
| đúng cực trị | 50,4% (n=7.163) | 50,0% (n=7.265) |
| xếp tầng ≥2 hai đầu | 48,2% | 53,0% |

Tập **cụm khối lượng lớn + delta lệch hẳn** (nhãn = THUẬN chiều hấp thụ):

| Hình | nửa đầu | nửa sau |
|---|---|---|
| **xanh đầu + đỏ đít (CORVEN)** | 50,7% (n=2.876) | 51,8% (n=2.582) |
| đỏ đầu + xanh đít (hình NGƯỢC) | 51,2% | **52,6%** |
| xếp tầng ≥3 hai đầu | 40,0% (n=40) | 50,0% (n=100) |

⇒ **Hình ngược lại còn nhẹ nhàng hơn hình CORVEN.** Không có tách biệt nào.

## 3. Test mạnh nhất: chia ngũ phân vị theo ĐỘ MẠNH của hình

Điểm hình = (delta band trên / khối lượng band trên) − (delta band dưới / khối lượng band dưới).
Q1 = đỏ đầu xanh đít · Q5 = xanh đầu đỏ đít rõ nhất. Ngưỡng lấy từ nửa đầu.

| Tập | lệch Q5−Q1 nửa đầu | lệch Q5−Q1 nửa sau |
|---|---|---|
| tất cả cụm vol lớn (n=9.100 / 8.471) | **+0,1** | **+0,1** |
| chỉ combo B — hấp thụ đúng nghĩa (n=174 / 132) | −5,7 | +22,8 |
| chỉ tại VWAP ngày ±2 giá (n=2.060 / 904) | +10,0 | −3,7 |

Ô có n lớn cho **đúng 0**. Hai ô còn lại **đổi dấu** giữa hai nửa (mỗi ô chỉ ~35 ca) ⇒ nhiễu.

## 4. Cách đọc thứ hai — "nến DELTA có bóng dưới đỏ, thân xanh" — KHÔNG đo được từ export này

Kiểm trực tiếp cột trong `_bars.csv`: `max_delta == min_delta == delta` ở **724.260/724.279 nến
(99,997%)**. Tức export không lưu đường đi của delta trong nến ⇒ bóng nến delta là không thể phục hồi.
Muốn đo cách đọc này phải xuất thêm dữ liệu **tick/trade-by-trade**, hoặc để indicator ghi
max/min delta trong lúc chạy live.

## 5. Kết luận
1. Ở định nghĩa **theo mức giá**, "xanh đầu đỏ đít" **không phải tín hiệu** trên GC khung M1:
   50,2–51,8% ở mọi cách cắt, lệch ngũ phân vị **+0,1** trên mẫu 17.500 ca.
2. Lý do có thể giải thích được: hình này xuất hiện ở **47,5% mọi nến** (bản cực trị: 67,4%) —
   nó là hệ quả cơ học của việc giá chạm được hai đầu biên độ, không phải dấu vết của hấp thụ.
3. Điều này **không chứng minh CORVEN sai** — có thể ý anh ấy là cách đọc ở §4, mà export hiện tại
   không đo được. Nhưng ở cách đọc đo được thì kết quả là bằng không.
4. ⚠️ Theo luật trong CLAUDE.md: **không được code hình này thành signal**, và không được nói
   như thể đã kiểm định thuận lợi.

**Script:** `research/perlevel_extract.py` (quét 583 MB → `research/perlevel_feats.csv`),
`research/xanh-dau-do-dit.py`, `-2.py`, `-3.py`.

---

# SỬA LẠI: "xanh đầu đỏ đít" là **BUBBLE BIG TRADE**, không phải màu ô imbalance

Người học đính chính (2026-09-09): xanh/đỏ ở đây là **marker tròn lệnh đơn lớn** trên footprint —
bubble MUA (xanh) ở đỉnh nến + bubble BÁN (đỏ) ở đáy nến. Toàn bộ §1–§3 ở trên đo **màu ô mất cân
bằng bid/ask**, tức **đo sai đối tượng**. Lỗi cụ thể: đã đọc và trích chính `CORVEN_SPEC_V1.md`
("bubble big trade nằm ở 30% DƯỚI của nến") trong cùng lượt mà không nối được với câu hỏi.

## Kết quả kiểm khả thi: KHÔNG ĐO ĐƯỢC — cột `max_one_trade` rỗng

`max_one_trade` là cột duy nhất định vị được lệnh đơn lớn. Độ phủ thực tế:

| File | dòng | % mức giá có big trade | lớn nhất |
|---|---|---|---|
| `fp_GC_XCEC_..._748d9h.csv` (583 MB, 2 năm) | ~11,4 triệu | **0,00%** (chỉ 2026-08 có 0,08%) | 19 |
| `Data_Footprint_Export.csv` | 182.844 | **0,00%** | 0 |
| `27-7/sample.csv` | 761.199 | **0,00%** | 0 |
| `data-footprint/Data_Footprint_Export.csv` | 44.054 | **0,00%** | 0 |
| **`28-7/30-7-2026.csv`** (2 ngày) | 9.907 | **6,55%** | 34 |

File 2 ngày là file duy nhất có số liệu (1.381 nến M1). Đếm hình trên đó:

| Ngưỡng lệnh đơn | bubble MUA ở đỉnh nến | bubble BÁN ở đáy nến | **CẢ HAI (xanh đầu đỏ đít)** |
|---|---|---|---|
| ≥ 5 HĐ | 5 nến | 3 nến | **0 nến** |
| ≥ 10 HĐ | 3 nến | 0 nến | **0 nến** |
| ≥ 15 HĐ | 2 nến | 0 nến | **0 nến** |

⇒ **n = 0.** Không có gì để đo.

## Nguyên nhân — cùng gốc với lỗi "nến chỉ ra gạch ngang" của indicator Ask/Bid Difference

Quantower chỉ cấp chi tiết **từng lệnh** (`MaxOneTradeVolume`) cho nến được xử lý **khi chạy tiến /
live**. Nạp volume-analysis lịch sử chỉ cho **tổng bid/ask từng mức giá**. Vì vậy 2 năm dữ liệu dày
có đủ bid/ask per-level nhưng **không có cỡ lệnh đơn** — đúng hiện tượng người học đã gặp trên chart.

## Muốn kiểm được thì phải làm gì
Xuất dữ liệu mà `max_one_trade` **có số** — tức cho chart chạy tiến (replay/live) rồi mới export,
hoặc dùng nguồn tick. Cần cỡ **vài tháng** mới đủ n: 2 ngày chỉ cho 8 ca một phía và **0 ca hai phía**.

## Bằng chứng liên quan đã có trong repo (không thay thế được phép đo trên)
`quantower-orderflow-indicator/OrderFlowBubbles.cs` ghi rõ: đã đo lại trên **538.558 ô per-level
thật**, base rate ~50,6%, **không thành phần nào còn lợi thế** (noResult −7,2đpt · POC nổi bật −5,8đpt
· hai phe cùng lớn −1,2σ · phân kỳ delta −0,0σ). Hiệu ứng vững duy nhất **ngược dấu**: ô đậm tại cực
trị + biên độ hẹp báo mức **SẮP BỊ XUYÊN**. Big Trade trong file đó dùng cùng metric — nhưng đó là
đo **cỡ ô**, chưa phải đo **vị trí bubble hai đầu nến** như CORVEN nói.

---

# ĐO LẠI LẦN 3 — bubble = **HVN cell HOẶC stacked imbalance** (đúng 3 nguồn người học nói)

Người học đính chính tiếp: bubble nổi lên có thể do **HVN cell**, **stacked imbalance**, hoặc **lệnh
đơn**. Nguồn lệnh đơn không có dữ liệu (§trên), còn **hai nguồn kia đo được**. Lấy đúng ngưỡng trong
`quantower-orderflow-indicator/OrderFlowBubbles.cs`:

| Nguồn bubble | Luật trong indicator |
|---|---|
| **HVN cell** | khối lượng ô ≥ 5 · modified z-score ≥ **3,0** · **và** ≥ **4,0×** trung vị ô (nền 100 nến, median+MAD) |
| màu | `AggColor(buy, sell)` — **xanh** nếu ask ≥ bid, **đỏ** nếu ngược |
| **Stacked imbalance** | chéo **3:1** (`ImbalanceRatioPct = 300`), **≥ 3 mức liên tiếp**, lọc min-vol = max(5, trung vị ô) |

Hình CORVEN = **bubble XANH trong band 30% trên** và **bubble ĐỎ trong band 30% dưới**.
Script: `research/bubble_extract.py` → `research/bubble_feats.csv`, rồi
`research/bubble-xanh-dau-do-dit.py` và `research/bubble-vwap-kiem-chat.py`.

## Phát hiện phụ nhưng quan trọng: stacked imbalance gần như KHÔNG BAO GIỜ nổ
Với thiết lập mặc định (3:1, 3 mức liên tiếp) nguồn này chỉ nổ ở **0,0–0,1%** số nến trên GC M1.
⇒ Trên thực tế, **bubble mà bạn thấy gần như luôn là HVN cell**. Bubble bất kỳ: 25,4% số nến.
Hình "xanh đầu đỏ đít": **2,5%** số nến — lần này đủ hiếm để là một bộ lọc thật.

## Kết quả — so với ĐỐI CHỨNG SÁT NHẤT (cùng tại VWAP, có bubble nhưng KHÔNG đúng hình)

| Bán kính VWAP ngày | đúng hình | có bubble khác hình | không bubble | z (hình vs khác hình) |
|---|---|---|---|---|
| **±1 giá** | **57,8%** (n=109) | 50,8% (n=957) | 48,0% (n=492) | +1,39 |
| ±2 giá | 54,0% (n=252) | 51,9% (n=1.898) | 49,5% (n=864) | +0,62 |
| ±4 giá | 52,4% (n=477) | 50,1% (n=3.646) | 50,1% (n=1.522) | +0,93 |
| **mọi khoảng (không cần VWAP)** | **50,7%** (n=2.057) | 50,6% (n=11.945) | 50,5% (n=3.708) | +0,06 |

Đọc theo hàng: tỉ lệ **giảm đơn điệu** khi nới bán kính (57,8 → 54,0 → 52,4 → 50,7) — đúng dạng mà
một hiệu ứng thật phải có. **Không cần VWAP thì hình bằng đúng 0.**

## Nhưng phép tách đôi thời gian giết nó

Chênh lệch (đúng hình − có bubble khác hình), tính riêng từng nửa:

| Bán kính | nửa đầu | nửa sau |
|---|---|---|
| ±1 giá | **+11,8 điểm** (61,9% vs 50,1%) | **−0,1 điểm** (52,2% vs 52,3%) |
| ±2 giá | +2,4 | +0,9 |
| ±4 giá | +3,5 | +0,1 |
| mọi khoảng | −1,3 | +0,7 |

Toàn bộ "lợi thế" nằm ở **nửa đầu, bán kính ±1, n=63**. Ở nửa sau, hình **không thêm gì** ở mọi bán kính.

## Kết luận lần 3
1. Đây là bản đo **đúng đối tượng** (bubble, không phải màu ô) và **đúng ngưỡng của indicator**.
2. Hình có dạng đúng đắn về mặt cấu trúc: **chỉ có ý nghĩa khi ở sát VWAP**, và **đơn điệu theo
   khoảng cách tới VWAP**. Đây là dấu hiệu đáng theo, không phải rác.
3. Nhưng **chưa qua được phép tách đôi thời gian**: nửa sau bằng 0. n = 109 ở ô mạnh nhất là quá
   nhỏ để phân biệt "hiệu ứng thật yếu" với "may mắn nửa đầu".
4. ⚠️ **Chưa được code thành signal.** Cần tăng n: nới nhẹ ngưỡng HVN cell (4,0× → 3,0×) hoặc
   xuất thêm mã cùng dạng, rồi đo lại — đây là ô đầu tiên trong cả chuỗi nghiên cứu đáng làm việc đó.
