# Absorption: các nền tảng/tác giả định nghĩa và phát hiện thế nào — và mình đang thiếu gì

Ngày 2026-07-28. Nối tiếp [RESEARCH-bubble-algo-2026-07-28.md](RESEARCH-bubble-algo-2026-07-28.md).
Nguồn: tài liệu chính thức ATAS, Bookmap KB, sách hướng dẫn Orderflows Absorption Tool (Mike Valtos,
NinjaTrader 8), TradingView (GB Footprint Pro), OrderFlow Labs, GoCharting, VSA/Wyckoff, và 2 nguồn
học thuật (Kyle's lambda; paper phát hiện iceberg trên CME của chính Devexperts/dxFeed).

---

## 1. Bảng so sánh: mỗi nguồn phát hiện absorption bằng gì

| Nguồn | Định nghĩa lõi | Cơ chế phát hiện | Ngưỡng công bố | Xác nhận |
|---|---|---|---|---|
| **Trader Dale** (ebook của mình, tr.87-88) | Volume lớn bất thường **trên CẢ Bid lẫn Ask** quanh S/R, giá ngừng đi | So ô footprint với **ô trung bình gần đây** | "cao hơn trung bình rất nhiều" (định tính) | Vào lệnh khi xác định được mức; "mất vài phút" mới hình thành → dùng **M5/M30** |
| **ATAS** (blog Absorption + Cluster Search) | "Volume cao **không tương xứng** sát high/low của nến, mà giá **không đi qua** mức đó" | Cluster Search lọc theo volume/bid/ask/delta/POC; ví dụ chính thức: **delta ±150 trên 3 mức giá liền nhau** | Delta tuyệt đối theo instrument, chỉnh tay | **Thành công** = giá bật khỏi mức; **thất bại** = xuyên qua, support→resistance |
| **Orderflows** (Valtos, NT8) | 7 **kịch bản** absorption khác nhau | Extreme (tại cực trị nến) · Expanded Extreme (gần cực trị) · **Momentum (tiếp diễn)** · Trapped · Level 1/2 Aggressive (hấp thụ **cả bid lẫn ask** khi giá đứng) · Stacked | Conditional Delta Volume (vd 25); Min bar volume (vd 500 cho ES) | 6 bộ lọc: **Swing filter + Swing period (9)**, min bar volume, **Delta Confirmation**, **Delta Divergence**, **Prominent POC** |
| **Bookmap** | Limit ẩn **nạp lại** liên tục tại một mức, aggressor không đẩy được giá | Thuật toán **"Resistance"**: limit mới xuất hiện **tức thì** sau execution tại mức đó | Cửa sổ thời gian "instant" + ngưỡng size (mặc định 1) — người dùng chỉnh | CVD tăng mà giá đứng = hấp thụ ẩn; mức giữ được qua nhiều lần bị đánh |
| **GB Footprint Pro** (TradingView) | Giá gần như không nhúc nhích dù volume nặng | **Delta % threshold** + **ATR range multiplier** | tham số, không công bố mặc định | không nêu |
| **OrderFlow Labs / GoCharting** | Volume lớn lặp lại tại **cùng một mức**, nến không tiến thêm | Đọc ô footprint; phân biệt rõ với imbalance (imbalance = 1 ô lệch 3:1; absorption = **không có kết quả giá**) | 3:1 (imbalance), absorption định tính | đặt trong bối cảnh volume profile / mức cấu trúc |
| **VSA / Wyckoff** ("stopping volume") | Effort to fall, **no result** | Volume rất cao + **spread HẸP** + close lùi khỏi cực trị | định tính | **Test bar**: nến sau volume **thấp**, quay lại vùng đó mà không có cung → xác nhận |
| **Học thuật** | Absorption = **price impact thấp bất thường** trên mỗi đơn vị order flow | **Kyle's lambda** = Δgiá / order-flow imbalance; lambda nhỏ = thị trường sâu, hấp thụ tốt | ước lượng hồi quy, tương đối | so lambda hiện tại với phân phối lịch sử |
| **dxFeed/Devexperts** (paper CME iceberg) | Iceberg = phần hiển thị nhỏ, nạp lại nhiều lần | **Native**: trade volume > resting volume của lệnh (dấu hiệu chắc chắn). **Synthetic**: tranche mới xuất hiện trong **dt ≈ 0,3 s** sau khi tranche cũ khớp hết | dt ~0,3 s; cần **MBO/full order depth** (order ID + Limit/Modify/Trade/Delete) | máy trạng thái theo chuỗi lệnh |

## 2. Hạt nhân chung của mọi định nghĩa

Gạt hết khác biệt câu chữ, **absorption = 5 thành phần**, và một tín hiệu đúng phải có ít nhất 4:

| # | Thành phần | Ý nghĩa | Ai nhấn mạnh |
|---|---|---|---|
| 1 | **EFFORT** | Volume/delta bất thường so với chuẩn động | tất cả |
| 2 | **NO RESULT** | Giá **không tiến**: spread hẹp / không phá mức / price impact thấp | VSA, ATAS, GB, Kyle |
| 3 | **VỊ TRÍ** | Tại mức cụ thể có ý nghĩa: cực trị nến, POC nổi bật, S/R, sau một cú swing | ATAS, Valtos (Swing filter + Prominent POC), Trader Dale |
| 4 | **THỜI GIAN / LẶP LẠI** | Hấp thụ là **quá trình**: nạp lại nhiều lần, kéo dài nhiều nến/nhiều giây | Bookmap, dxFeed, Trader Dale ("mất vài phút") |
| 5 | **XÁC NHẬN** | Sau đó mức **giữ hay vỡ**; VSA đòi test bar; ATAS phân biệt thành công/thất bại | VSA, ATAS, Bookmap |

Và một điểm mà hầu như mọi tài liệu phổ thông bỏ qua nhưng Valtos nói thẳng:
**absorption không chỉ là tín hiệu đảo chiều.** Momentum Absorption = hấp thụ **thuận xu hướng**
(iceberg đỡ giá trên đường đi) → tín hiệu **tiếp diễn**. Cùng một hình dạng số liệu, hai ý nghĩa
trái ngược, phân biệt bằng **ngữ cảnh vị trí**, không bằng bản thân ô footprint.

## 3. Đối chiếu với `OrderFlowBubbles.cs` — thiếu gì

| # | Thành phần | Code hiện tại | Trạng thái |
|---|---|---|---|
| 1 | EFFORT | volume/mức z ≥ 4 (median+MAD, 100 nến) | ✅ có (nhưng baseline gộp cả ô rìa → xem research trước) |
| 2 | NO RESULT | chỉ `High − Close ≥ 1 tick` | ⚠️ **rất yếu** — không đo range/ATR, không đo price impact |
| 3 | VỊ TRÍ | ≤2 tick từ cực trị nến | ⚠️ có một nửa: **không có swing filter**, không có POC nổi bật, không có S/R (VA/POC phiên trước) |
| 4 | THỜI GIAN | không có | ❌ **thiếu hoàn toàn** — chỉ xét 1 nến, không gộp đa nến, không dùng tick/refill |
| 5 | XÁC NHẬN | không có | ❌ **thiếu hoàn toàn** — không biết mức giữ hay vỡ |
| 6 | Phân loại kịch bản | 1 loại duy nhất | ❌ thiếu Momentum (tiếp diễn), Trapped, Stacked |
| 7 | Hướng delta | đòi **1 phe ≥60%** | ⚠️ lệch: Trader Dale/ATAS đòi lớn ở **cả hai phe**; Valtos dùng **Delta Divergence** |
| 8 | Sàn hoạt động | MinLevelVolFloor=5 | ✅ tương đương "Min bar volume" của Valtos |
| 9 | Big Trade | `MaxOneTradeVolume`, feed trả 0 → fallback volume/mức | ❌ thiếu **chế độ gộp lệnh** (ATAS "Cumulative Trades") — với feed 1 lot/trade thì bắt buộc phải gộp |
| 10 | Price impact | không có | ❌ thiếu (Kyle lambda là cách chuẩn hoá đẹp, portable đúng tinh thần indicator) |

Ba lỗ hổng lớn nhất theo thứ tự: **(4) thời gian → (5) xác nhận → (2) no-result**.
Đây chính là lý do tín hiệu hiện tại "nổ ở nến sôi động" thay vì "nổ ở vùng quan trọng".

## 4. Kiểm chứng các luật trên dữ liệu thật (GCQ26, 05–07/2026, 74.974 nến M1)

Script: [rules_from_web.py](rules_from_web.py). Tín hiệu tại cực trị cục bộ 10 nến; thắng = đi ngược
đà đủ target trước khi đi tiếp đủ target, trong 20 nến. `***` = vượt BASE quá 2 sai số chuẩn (n≥100).

| Luật (nguồn) | M1 (base 55,9%) | M5 (base 59,1%) | M15 (base 62,9%) |
|---|---|---|---|
| **Delta divergence** — vol≥2,5× & delta **thuận đà cũ** (Valtos) | **59,5%** n=2564 *** | **64,7%** n=306 | **73,3%** n=45 |
| Delta divergence — vol≥1,5× | 58,5% n=4639 *** | 62,7% n=620 | 70,3% n=128 |
| Delta **confirmation** — delta ngược đà (phe mới đập) | 55,2% n=1220 | 58,5% n=147 | 75,0% n=28 |
| VSA stopping volume (vol≥2× & range hẹp & close lùi) | 61,9% n=113 | 52,2% n=23 | 42,9% n=7 |
| … + test bar xác nhận | 67,9% n=28 | 40,0% n=5 | — |
| ATAS "2 nến sau không phá cực trị" (vào lệnh trễ 2 nến) | 54,9% n=3086 | 57,5% n=513 | 64,9% n=154 |
| Bookmap CVD-divergence | 56,6% n=6309 | 60,4% n=1284 | 65,5% n=435 |
| "Effort-result" đòi **close lùi >60% range** (research trước) | **50,5%** n=513 | — | — |

Bốn kết luận rút ra:

1. **Delta divergence là luật mạnh nhất và ổn định nhất** — tại đỉnh, volume cao + delta **dương**
   (người mua vẫn đang đập vào) là dấu hiệu hấp thụ đúng nghĩa, và edge **tăng dần theo khung**
   (+3,6 pp M1 → +5,6 pp M5 → +10,4 pp M15). Đây đúng là thứ Valtos gọi là *Use Delta Divergence*
   ("trên các nến volume nâng đỡ, delta thường âm").
2. **Đòi giá phải quay đầu ngay trong nến là sai lầm.** Cùng bộ điều kiện, thêm "close lùi >60%
   range" thì tụt xuống **50,5%** — dưới cả base. Lúc giá đã lùi hết về đáy nến thì phần lớn cú đảo
   đã xảy ra. Code hiện tại đang đi theo hướng này (`High−Close ≥ 1 tick`), tuy nhẹ hơn.
3. **Xác nhận kiểu "chờ 2 nến rồi mới vào" giết edge** (54,9% < base). Xác nhận nên dùng để **xếp
   hạng độ tin cậy / tô đậm bubble**, không nên dùng làm điều kiện vào lệnh trễ.
4. **VSA stopping volume + test bar** có tỉ lệ cao nhất (67,9%) nhưng **n=28** — chỉ là gợi ý, chưa
   đủ mẫu để kết luận. Nó hiếm vì đòi cả 3 điều kiện cùng lúc.

Bổ sung, ngược trực giác: "Momentum absorption" (tại đỉnh cục bộ M1, volume ≥2×, delta thuận đà,
đóng cửa mạnh) nếu đo theo chiều **tiếp diễn** chỉ đúng **39,5%** (n=1510). Trên vàng M1, mua đuổi
tại cực trị là kèo xấu — nếu port kịch bản Momentum của Valtos thì phải giới hạn ở khung lớn hơn
và trong trend rõ, đừng bật mặc định.

**Giới hạn:** mọi con số trên là **bar-level** (export không có per-level), nên đây là *proxy* của
các luật gốc vốn chạy trên từng ô giá. Chúng nói được luật nào đáng làm, không nói được ngưỡng cuối.

## 5. Việc còn thiếu quan trọng nhất: dữ liệu tick

Paper của Devexperts/dxFeed cho thấy iceberg **thật** chỉ xác định chắc chắn được từ **MBO/full
order depth** (order ID + chuỗi Limit/Modify/Trade/Delete): native iceberg lộ ra khi *trade volume >
resting volume*; synthetic iceberg lộ ra khi tranche mới xuất hiện trong **dt ≈ 0,3 giây**.
Feed hiện tại không có dữ liệu đó → **không thể** phát hiện iceberg đúng nghĩa.

Nhưng **trade-level (tick) thì có**, và đó là thứ đang bỏ phí. Từ chuỗi trade có thể dựng:
- **absorption run**: số trade liên tiếp tại **cùng một giá** trước khi giá đổi mức, tổng volume của
  run, và **thời gian** giá đứng ở đó → gần nhất với định nghĩa Bookmap ("bị đánh liên tục mà không
  qua được").
- **lệnh lớn thật** bằng cách **gộp trade** trong cửa sổ 50–200 ms tại cùng giá/cùng phe — đúng chế
  độ *Cumulative Trades* của ATAS. Đây là lời giải cho chuyện `MaxOneTradeVolume = 0`.

## 6. Đề xuất Absorption v3 (thay cho luật 4-AND hiện tại)

Chấm điểm thay vì AND cứng — mỗi thành phần góp điểm, vẽ bubble khi tổng vượt ngưỡng, độ đậm/kích
thước theo điểm:

```
// 1. EFFORT (bắt buộc)
effort   = z_robust(volume ô, baseline = top-3 ô mỗi nến, 100 nến)        // ≥ 3
// 2. NO RESULT — thay "close lùi 1 tick" bằng price impact
impact   = |Close − Open| / (volume nến)                                   // Kyle lambda thô
noResult = z_robust(impact) ≤ −1   HOẶC   range nến ≤ 0,9 × median range
// 3. VỊ TRÍ
atExtreme   = ô nằm ≤ 2 tick từ high/low nến
afterSwing  = nến là cực trị của N nến trước (Valtos: N = 9)               // swing filter
isBarPOC    = ô là POC của nến  VÀ  POC ≥ 1,5 × ô lớn thứ nhì              // prominent POC
// 4. HƯỚNG DELTA — theo Valtos, KHÔNG đòi 1 phe ≥60%
divergence  = tại đỉnh: delta ô/nến DƯƠNG   |  tại đáy: ÂM                 // luật mạnh nhất (mục 4)
twoSided    = min(buy, sell) ≥ 0,35 × volume ô                             // định nghĩa Trader Dale
// 5. THỜI GIAN (nếu có tick) hoặc gộp đa nến
runVol      = tổng volume của các trade liên tiếp tại cùng mức
multiBar    = cùng mức ±2 tick có effort cao ở ≥2 nến trong 5 nến gần nhất

score = 2·effort_ok + 2·noResult + 1·atExtreme + 1·afterSwing + 1·isBarPOC
      + 2·divergence + 1·twoSided + 2·multiBar
vẽ khi score ≥ 6;  đậm dần theo score
// XÁC NHẬN (cập nhật bubble, KHÔNG dùng để trì hoãn tín hiệu):
//   1–3 nến sau không phá mức → viền xanh "giữ";  phá → viền xám "thất bại"
```

Kèm 3 thay đổi đã đề xuất ở research trước (đóng cửa hậu `OR 3×median` của Big Trade, baseline theo
top-k ô, thứ tự vẽ) và đổi tên Big Trade → HVN cell khi feed không có lệnh đơn.

## Nguồn

- [ATAS – Absorption of demand and supply in the footprint chart](https://atas.net/blog/absorption-of-demand-and-supply-in-the-footprint-chart/)
- [ATAS – Cluster Search indicator](https://atas.net/atas-possibilities/indicators/cluster-search-indicator/) · [ATAS help – Cluster Search](https://help.atas.net/en/support/solutions/articles/72000602240-cluster-search) · [ATAS help – Big Trades](https://help.atas.net/en/support/solutions/articles/72000602332-big-trades)
- [Orderflows Absorption Tool – User Guide (Mike Valtos, PDF)](https://www.orderflows.com/dl/NT8/OrderflowsAbsorptionToolUserGuide.pdf)
- [Bookmap – Iceberg Orders Tracker (KB)](https://bookmap.com/knowledgebase/docs/KB-Bookmap-Wiki-Iceberg-Orders-Tracker) · [Bookmap – Detecting stop runs using CVD & iceberg absorption](https://bookmap.com/blog/detecting-stop-runs-using-cvd-and-iceberg-absorption-for-strategic-trading)
- [OrderFlow Labs – Footprint chart guide](https://orderflowlabs.com/blogs/theblog/footprint-chart-guide) · [GoCharting – Footprint patterns cheat sheet](https://gocharting.com/blog/footprint-charts/footprint-chart-patterns-cheatsheet)
- [GB Footprint Pro (TradingView)](https://www.tradingview.com/script/aEWUiKYL-GB-Footprint-Pro/)
- [Trading Setups Review – Stopping volume (VSA)](https://www.tradingsetupsreview.com/stopping-volume-volume-spread-analysis-vsa/)
- [Kyle's lambda – price impact](https://faustiandreams.github.io/2022-09-10/kyle-model) · [Empirical market impact conditional on order-flow imbalance (arXiv)](https://arxiv.org/pdf/2004.08290)
- [CME Iceberg Order Detection and Prediction — Zotikov & Antonov, Devexperts/dxFeed (arXiv 1909.09495)](https://arxiv.org/pdf/1909.09495)
