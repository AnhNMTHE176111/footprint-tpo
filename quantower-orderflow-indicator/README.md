# OrderFlow Bubbles — bản QUANTOWER (tập trung VÀNG)

Indicator order-flow dạng **bubble/hình** cho **Quantower**, đọc footprint (Volume Analysis) theo
từng mức giá. Triết lý: gom mọi tín hiệu order-flow thành hình trên chart, **bật/tắt từng phần**,
**ngưỡng tương đối** để cùng một cấu hình chạy đúng trên mọi feed/sàn. Cách build & nạp: [BUILD.md](BUILD.md).

> ✅ **Build sạch** trên Linux → `dist/OrderFlowBubbles.dll` (net10.0, khớp Quantower 1.146.x).
> ⚠️ **Chưa chạy thử trên Quantower thật** (Quantower Windows-only, máy dev Linux) — cần add lên
> chart Windows để xác nhận trực quan + tinh chỉnh ngưỡng theo feed.

## ⚠️ Điều kiện bắt buộc
Đọc footprint qua `IVolumeAnalysisIndicator`. Chỉ hiện tín hiệu khi feed **có trade/volume thật**
(futures CME: AMP/CQG, dxFeed, Rithmic…). Feed CFD không volume thật → không có gì. Lần đầu add phải
chờ Quantower **nạp Volume Analysis** (có % tiến trình).

## 🔑 Vì sao "ngưỡng tương đối" — câu chuyện số delta lệch ~4 lần
Cùng 1 nến GC M1, số delta trên ATAS của bạn lớn ~3–4× số của bạn (Sierra). Đó là **tích của nhiều
hệ số**: single- vs double-count volume (~2×), contract GC 100oz vs MGC 10oz (10×), cách gộp lệnh/
phân loại bid-ask giữa feed, filter [CV]… → **mọi ngưỡng SỐ HỢP ĐỒNG tuyệt đối đều vô nghĩa khi đổi
feed**.

Cách chống (đã áp dụng): mọi trigger dùng **thống kê tương đối & robust** —
**modified z-score theo median + MAD** trên baseline động (không dùng mean+std vì volume đuôi nặng,
std bị spike thổi phồng), hoặc **tỷ lệ** `deltaPct = Δ/Volume`. Nhờ vậy **mọi hệ số thang đo triệt
tiêu** → cùng cấu hình chạy đúng cho GC, MGC, hay feed proxy. Knob **tuyệt đối duy nhất** còn lại là
**sàn chống nhiễu** (`MinLevelVolFloor`/`MinBarVolFloor`) cho nến đêm quá mỏng.

## Đọc hình thế nào — hệ mã hoá mới
| Tín hiệu | HÌNH | Kích thước | Màu |
|---|---|---|---|
| **Absorption (hấp thụ)** | ⬤ **tròn ĐẶC**, vẽ **trên cùng** | = bề rộng nến, **sàn 14 px** (trước đây zoom hẹp là gần như vô hình) | cyan (đỉnh) / đỏ (đáy) · **vòng trắng = mức GIỮ được**, mờ đi = **mức VỠ** |
| **Big Trade / HVN cell** | ⬤ **tròn MỜ (halo)** | to dần theo z | cyan/đỏ = phe aggressor · **bỏ nếu trùng mức với Absorption** |
| **Big Delta profile** | ━ **gạch ngang** (rộng = nến) | dày nhẹ theo độ mạnh | **xanh = buy dồn / đỏ = sell dồn** |
| **Nến delta lớn** | **tô thân nến** | cả thân | **xanh (Δ>0) / đỏ (Δ<0)** |
| **Số Delta** | chữ dưới nến | — | xanh/đỏ theo dấu |
| Exhaustion / Divergence / Sweep | ▲ tam giác | vừa | đỉnh→cyan, đáy→đỏ |
| Stacked Imbalance | ▭ vùng chữ nhật kéo sang phải | số mức | xanh lơ buy / hồng sell (nhạt = bị rút râu; vùng còn hiệu lực nhưng đã xa ≥ ImbFarBars nến thì KHÔNG vẽ; hover chỉ ghi "Stacked imbalance buy/sell N mức") |
| Unfinished / Stop-hunt | ▭ / ⬤ halo | nhỏ / lớn | 2 phía / phe hấp thụ |

Rê chuột vào bubble → **tooltip** tên tín hiệu + số liệu (z-score, deltaPct…).

## Giải nghĩa & thuật toán (ngưỡng portable, default vàng M1)
| # | Tín hiệu | Cơ chế + test | Default |
|---|---|---|---|
| 1 | **Absorption v3.2** | Chấm điểm có **TRỌNG SỐ ĐO TỪ DỮ LIỆU THẬT** (538.558 ô, xem [research/](research/)): EFFORT (volume ô z) 2đ + tại cực trị 1đ + **sau swing 20** 1đ → vẽ khi ≥ 4. Các thành phần no-result / POC nổi bật / hai phe / divergence / đa nến **đặt trọng số 0** vì đo được là **vô giá trị hoặc gây hại** (−7,2pp, −5,8pp…). Tổ hợp "range hẹp + POC nổi bật ngay mức" bị đổi nhãn thành **⚠ Mức DỄ VỠ** (vàng) — đo được là mức *sắp bị xuyên*. **Xác nhận** 1–3 nến sau đổi viền, không trì hoãn tín hiệu. | **TẮT** từ 2026-11-19 (chart CORVEN không có vòng đặc này, nó còn che bóng mờ cùng mức); vẫn bật lại được ở Settings |
| 2 | **Big Trade → HVN cell** | `MaxOneTradeVolume` (lệnh ĐƠN) z ≥ ngưỡng **VÀ** ≥ ×median. Feed dxFeed **không cấp** field này (0% trên 6 tháng) → tự fallback volume/ô và tooltip ghi **"HVN cell · vol/ô"** cho đúng bản chất. | **BẬT** |
| 3 | **Big Delta line** | 1 mức có net delta lệch mạnh: `|Δ/Vol| ≥ 0.35` **và** `|Δ|` z cao. Giữ **top-N** mức/nến. | **BẬT** |
| 4/5 | **Nến delta lớn** | `|Δ/Vol| ≥ 0.30` **và** `|Δ|` z ≥ 2 **và** volume ≥ 0.8× median → tô thân **theo DẤU DELTA** (không theo close). | **BẬT** |
| 6 | **Exhaustion** | Cực trị swing mới + volume teo + **delta rút khỏi đỉnh intrabar** (dùng `Total.MaxDelta/MinDelta` THẬT). | tắt |
| 7 | **Stacked Imbalance** (2026-11-08, theo CORVEN) | Thuần: chéo Ask[i] ≥ 250% × Bid[i−1] (buy) / Bid[i] ≥ 250% × Ask[i+1] (sell), ≥3 mức liên tiếp, bên áp đảo ≥ 5 hợp đồng (sàn tuyệt đối, chỉnh được). Vẽ vùng từ nến tạo ra, kéo sang phải tới nến đầu tiên chạm lại (hoặc tới khi nến đóng xuyên qua). Logic ở `StackedImbalance.cs`. | bật |
| 8 | **Delta Divergence** | Giá HH nhưng CVD LH (ngược ở đáy) tại pivot + **volume pivot ≥ 1.5× median** + cooldown. | tắt |
| 9 | **Liquidity Sweep** | Wick vượt swing cũ + đóng lại trong range + delta ngược dấu. | tắt |
| 10 | **Unfinished** | Đỉnh/đáy còn cả 2 phía (> sàn nhiễu). | tắt |
| 11 | **Stop-hunt + Absorption** | Quét cực trị + hấp thụ ngay đó. | tắt |

> **Absorption vs Exhaustion:** Absorption = volume CAO, giá bị chặn (tường limit). Exhaustion =
> đẩy tới cực trị mới nhưng lực (volume+delta) **teo dần**. Cả hai báo phe thắng sắp hụt hơi.

## Khác biệt so với bản ATAS
1. **Vẽ tay GDI+** (Quantower không có `PriceSelectionValue`) → tự tính + tự vẽ trong `OnPaintChart`.
2. **Exhaustion = đúng intrabar.** Quantower **CÓ** `Total.MaxDelta/MinDelta` (ghi chú port cũ sai) →
   không còn phải xấp xỉ bằng "delta swing".
3. **Big Trade dùng `MaxOneTradeVolume`** (lệnh đơn lớn nhất) — sát nghĩa "cú đánh lớn" hơn tổng
   volume/mức; tự fallback nếu feed không cấp.
4. **Baseline robust median+MAD** (không mean+std) + ngưỡng z/percentile/ratio → **portable feed**.
5. Field map: `BuyVolume↔Ask`, `SellVolume↔Bid`, `Trades↔Ticks`, `Total.Delta/Volume` = cả nến.

## Nên bật gì trên M1 vs M30
| Tín hiệu | M1 | M30 | Ghi chú |
|---|:---:|:---:|---|
| Số Delta + Nến delta | ✅ | ➖ | M1 cần timing; M30 số chồng nhau |
| Absorption | ✅ | ✅ | Ở M30 vùng đảo mạnh hơn |
| Big Trade | ✅ | ✅ | z tự chuẩn hoá nên chạy được cả hai |
| Big Delta line | ✅ | ➖ | Nhiều mức ở HTF dễ rối |
| Exhaustion / Divergence / Sweep | ➖ | ➖ | Thử nghiệm, bật lẻ quan sát |

**Native Quantower nên thêm:** M1 → Cumulative Delta (line) + VWAP; M30 → Volume Profile phiên (VA + HVN/LVN).

## Bảng cấu hình then chốt (Settings)
> ⚠️ **Từ 2026-11-08 Settings chỉ còn 12 ô bật/tắt (từ 2026-11-18 thêm ô thứ 13 "Chấm Bid/Ask nhỏ · Bật")** (Nến delta, Ô Bid/Ask lớn, Số Delta, Absorption,
> Big Trade, Big Delta line, Kiệt sức, Stacked Imbalance, Divergence, Sweep, Unfinished, Stop-hunt) — người
> học không bao giờ chỉnh số nên mọi con số/màu bên dưới thành **hằng số mặc định trong code** (bỏ attribute
> `[InputParameter]`, giữ property). Giá trị chốt theo cấu hình đang chạy trên chart: Số Delta cỡ chữ **7**,
> cách đáy **8 px**, Big Delta line **tắt**; còn lại giữ mặc định. Muốn chỉnh số → sửa default trong code.
> Bảng dưới là tài liệu ý nghĩa các hằng số (một số con số trong bảng là lịch sử, xem code để biết giá trị hiện tại).

| Nhóm | Tham số | Ý nghĩa |
|---|---|---|
| Baseline | Số nến (100) · Warm-up (40) · **Sàn nhiễu** vol/mức (5), vol/nến (20) · **Số ô đậm nhất/nến (3)** | Cửa sổ median+MAD. **Top-3 ô** = so POC với POC lịch sử; để 0 sẽ nạp cả ô rìa 1-2 lot làm median tụt → tín hiệu nổ khắp nơi (lỗi bản cũ) |
| Ô Bid/Ask lớn: vòng tròn lớn mờ (luật theo từng tick, 2026-11-19) | Luật xét **theo từng tick**, không gom hàng; bóng nằm đúng giá khớp của ô. Với mỗi ô có giao dịch: bên trội = bên lớn hơn giữa Bid và Ask, bên yếu = bên còn lại. Hai mức nền chỉ tính từ **20 nến đã đóng liền trước** (cần ít nhất 5 nến): volume trung bình mỗi ô có giao dịch, và bên trội lớn nhất của nến, mỗi cái lấy trung bình 20 nến. Vòng tròn lớn mờ nổ khi **cả ba** điều kiện: (1) bên trội ≥ **0,5 ×** bên trội lớn nhất trung bình (`CellBigMaxSideRatio`); (2) bên trội **lớn hơn hẳn** bên trội của mọi tick khác trong ±**5** tick cùng nến (`CellBigLocalTicks`; tick vắng tính 0; bằng nhau thì không nổ); (3) bên trội ≥ **4 ×** bên yếu, bên yếu bằng 0 thì tính là 1 (`CellBigMinImbalance`). Thêm sàn tuyệt đối **9 hợp đồng** (`CellBigMinSide`). Cỡ to dần theo (bên trội ÷ bên trội lớn nhất trung bình): 1,0 × bề ngang nến ở 0,5 lần, 2,5 × ở 2 lần trở lên (nén căn bậc hai). Màu xanh khi Ask trội, đỏ khi Bid trội (hòa thì đỏ), cộng màu **tím** của stop hunt. Ngưỡng cố định (`UseFixedThreshold`): bên trội ≥ ngưỡng cố định thay cho điều kiện (1), vẫn cần (2), (3) và sàn. Không giới hạn số bóng mỗi nến; `CellBigMergeTicks` mặc định 0 (tắt). Đã bỏ cách gom 2 tick thành một hàng và các tham số hàng. | Luật **mô phỏng hiển thị của CORVEN**, **không phải lợi thế đã kiểm định**. Chỉnh trên 26 nến M5 (12:15 đến 14:20 UTC ngày 18/11/2026): luật ra **22 vòng**, CORVEN vẽ 25; trùng vị trí (±2 tick, cùng màu) chỉ 7, nên vị trí từng vòng khớp kém, chủ yếu khớp ở mức "nến nào có vòng". Bản Python gốc và nhật ký thử luật: [research/corven_m5_2026-11-18/](research/corven_m5_2026-11-18/README.md). Logic thuần ở `CellBigLogic.cs`; kiểm bằng `tests/CellBigTests.cs` (mọi điều kiện biên) và `tests/CorvenM5ParityTests.cs` (C# phải ra đúng cùng tập dấu với Python trên 26 nến) |
| Ô Bid/Ask: chấm nhỏ đặc (Dot, luật theo từng tick, 2026-11-19) | Chấm **đặc** nhỏ nổ khi: số lệnh khớp tại tick ≥ **2,4 ×** volume trung bình mỗi ô của 20 nến đã đóng trước (`CellDotTradesRatio`) **và** bên trội của tick lớn hơn hẳn bên trội của mọi tick khác trong ±**3** tick cùng nến (`CellDotLocalTicks`), cộng sàn 9 hợp đồng. Không đòi mất cân bằng. Một tick có thể vừa là vòng lớn vừa là chấm: vẽ cả hai, chấm nằm trên cùng. Cỡ chấm 45% bề ngang nến, kẹp 5 đến 10 px. Bật/tắt bằng `CellDotEnabled`. Ngưỡng cố định: chấm dùng bên trội ≥ ngưỡng cố định thay cho điều kiện số lệnh (vẫn cần lớn hơn hẳn trong ±3 tick và sàn). Stop hunt tô tím cả vòng lớn lẫn chấm (bóng ở nến quét là vòng lớn hay chấm đều được tính). Chốt chặn lúc vẽ: bóng có giá ngoài [thấp nhất của nến − 2 tick, cao nhất + 2 tick] không được vẽ. Rê chuột: vòng lớn "Buy/Sell lớn - n Bid m Ask \| Ngưỡng nổ k", chấm "Buy/Sell - n Bid m Ask \| t lệnh, ngưỡng k". | Trên 26 nến M5 mẫu: **37 chấm** (CORVEN có 16 cụm chấm; các chấm chồng lên nhau nên không đếm được số chấm thật). Trùng ở mức điểm ảnh: F1 0,43. ⚠ Một biểu đồ, không phải lợi thế đã kiểm định. Số liệu trên 87.362 nến M1 (cấu hình mặc định): vòng lớn 58.766 → 35.506, chấm 49.505 → 32.140, dấu kiệt sức 16.048 → 12.594, stop hunt 748 → 634 dấu (bóng tím 1.924 → 1.130). Dấu vân tay `cellbig-v16` / `exh-v3` / `stophunt-v6`. |
| Kiệt sức (luật chỉnh 2026-11-19) | Đỉnh soi bên **Ask**, đáy soi bên **Bid**, chỉ lấy ở **râu nến**. Một nến có dấu khi: râu phía đó dài ≥ **3 tick** (`ExhMinWickTicks`) **và** tổng volume bên soi trên **6 tick** tính từ cực trị đi vào trong (`ExhSumLevels`) ≤ **1,1 ×** volume trung bình mỗi ô có giao dịch của **20 nến đã đóng liền trước** (`ExhSumHistRatio`; mức nền lịch sử, không phải trung bình của chính nến; chưa đủ 5 nến thì chưa đánh dấu). Mức giá trống tính 0. Dấu bị vô hiệu khi một nến sau chỉ cần râu quét qua mức đó (`ExhSweepTicks`); tam giác hết hiệu lực vẫn được tô đặc nền mờ. | Đo trên 26 nến M5 ngày 18/11: CORVEN 11 dấu; luật ra **13 dấu, trùng 11, thừa 2, sót 0** (F1 0,917). Điểm số này là kết quả **sau khi chọn tham số trên chính 26 nến đó**, nên lạc quan; nhưng số trùng giữ nguyên trên một vùng tham số rộng nên luật không phải một ngưỡng may mắn. ⚠ Một biểu đồ; chỉ là dấu để đọc chart, **không phải tín hiệu đã kiểm định lợi thế**. Big Trade không chỉnh được vì lịch sử không có kích cỡ từng lệnh đơn. Logic ở `ExhaustionLogic.cs`, kiểm bằng `tests/ExhaustionTests.cs` |
| Nến delta | deltaPct (0.30) · z (2.0) · cổng volume (0.8×) · độ đậm tô (85) | Tô thân xanh/đỏ khi delta lớn & 1 chiều |
| Absorption | EFFORT z (2.5) · **điểm tối thiểu (6/12)** · cách cực trị (2 tick) · range ≤0.9×med · impact z ≤−1 · swing (9) · POC nổi bật (1.5×) · divergence (0.10) · hai phe (0.35) · đa nến (5) · xác nhận (3 nến) | Ít bubble → hạ **điểm tối thiểu** trước, rồi mới hạ EFFORT z. Ngưỡng hiện là **TẠM** — chạy `research/calibrate_perlevel.py` trên file footprint per-level để chốt |
| Big Trade | z (3.0) **VÀ** ≥4×median · bỏ nếu trùng mức Absorption | Đây là **AND**, không phải OR như bản cũ (cửa OR từng chiếm 51-71% số lần nổ) |
| Big Delta line | deltaPct (0.35) · z (2.0) · top-N (2) | Số gạch ngang mạnh nhất mỗi nến |

## Thông số MGC/GC (Micro/Full Gold)
Tick 0.10. **Không cần** đổi ngưỡng khi chuyển GC↔MGC hay đổi feed — z/ratio tự chuẩn hoá. Chỉ chỉnh
**sàn nhiễu** (`MinLevelVolFloor`/`MinBarVolFloor`) cho khớp thang volume của feed (MGC nhỏ → để thấp;
GC lớn → có thể nâng). Ít tín hiệu → hạ z; nhiễu → tăng z.

## Tốc độ nạp (2026-11-11)
Nạp lại nguội 87.362 nến M1 (đổi tham số / bản DLL mới → tính lại + niêm phong) nhanh hơn ~10 lần nhờ ghi niêm phong theo lô, median+MAD cuốn, danh sách vùng đang hoạt động; đọc file niêm phong nhanh hơn và file tự nén khi nhiều dòng thừa. Dữ liệu không đổi (golden hash khớp). Số đo + cách chạy: `perf/README.md`, `research/PERF-RESEARCH-2026-11-11.md`.
