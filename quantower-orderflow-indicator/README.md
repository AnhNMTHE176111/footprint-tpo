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
| **Big Trade (một lệnh đơn lớn)** | ⬤ **tròn MỜ** (độ đậm khoảng 35%, viền mảnh), vẽ dưới các chấm đặc | to dần theo cỡ lệnh: 1,0 × bề ngang nến ở ngưỡng, 2,5 × từ 6 lần ngưỡng trở lên (căn bậc hai), kẹp 8 đến 80 px | xanh nếu ô có Ask nhiều hơn Bid, đỏ nếu ngược lại · **chỉ feed sống mới có**, lịch sử gần như không có |
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
| 2 | **Big Trade (một lệnh đơn lớn)** | Tại một mức giá, lệnh đơn lớn nhất của nến ≥ **10 hợp đồng** thì nổ một vòng tròn mờ. Không còn điểm z, không so với trung vị, không giới hạn số vòng, không bỏ khi trùng Absorption, không suy từ volume của ô. Feed chỉ cấp số lệnh đơn lúc đang chạy sống (lịch sử gần như luôn bằng 0), bóng được niêm phong để nạp lại vẫn còn. | **BẬT** |
| 3 | **Big Delta line** | 1 mức có net delta lệch mạnh: `|Δ/Vol| ≥ 0.35` **và** `|Δ|` z cao. Giữ **top-N** mức/nến. | **BẬT** |
| 4/5 | **Nến delta lớn** | `|Δ/Vol| ≥ 0.30` **và** `|Δ|` z ≥ 2 **và** volume ≥ 0.8× median → tô thân **theo DẤU DELTA** (không theo close). | **BẬT** |
| 6 | **Exhaustion** | Cực trị swing mới + volume teo + **delta rút khỏi đỉnh intrabar** (dùng `Total.MaxDelta/MinDelta` THẬT). | tắt |
| 7 | **Stacked Imbalance** (2026-11-08, theo CORVEN) | Thuần: chéo Ask[i] ≥ 250% × Bid[i−1] (buy) / Bid[i] ≥ 250% × Ask[i+1] (sell), ≥3 mức liên tiếp, bên áp đảo ≥ 5 hợp đồng (sàn tuyệt đối, chỉnh được). Vẽ vùng từ nến tạo ra, kéo sang phải tới nến đầu tiên chạm lại (hoặc tới khi nến đóng xuyên qua). Logic ở `StackedImbalance.cs`. | bật |
| 8 | **Delta Divergence** | Giá HH nhưng CVD LH (ngược ở đáy) tại pivot + **volume pivot ≥ 1.5× median** + cooldown. | tắt |
| 9 | **Liquidity Sweep** | Wick vượt swing cũ + đóng lại trong range + delta ngược dấu. | tắt |
| 10 | **Unfinished** | Đỉnh/đáy còn cả 2 phía (> sàn nhiễu). | tắt |
| 11 | **Stop-hunt** | Quét cực trị + bóng Ô lớn ngay đó + fail break (logic ở StopHuntLogic.cs). | bật |

> **Sàn tối thiểu của chấm Bid/Ask (2026-11-24):** ô "Chấm Bid/Ask nhỏ · Dùng sàn tối thiểu" (mặc định bật) và ô số "Sàn tối thiểu (hợp đồng)" (mặc định 9, chỉ hiện khi ô trên bật). Tắt = chấm chỉ còn điều kiện k × trung vị. Trên 78.464 nến M1 NQ: sàn 9 → 33.958 chấm, tắt sàn → 35.130, sàn 20 → 18.180 (C# = Python).

> **Chấm Bid/Ask trên NQ/MNQ (2026-11-24):** mã NQ/MNQ tự dùng bộ số Nasdaq **3,5 × trung vị, lớn nhất trong ±8 tick, che chấm xanh cách chấm đỏ ≤ 12 tick** (sàn 9 giữ nguyên) thay cho bộ vàng 2,8 / ±4 / 6, vì nến NQ rộng gấp ~2,7 lần tính theo tick. Tắt bằng ô "Chấm Bid/Ask nhỏ · Mã NQ/MNQ tự dùng bộ số Nasdaq". Số liệu và so sánh với chart NQ của CORVEN: [research/nq_calib_2026-11-24/README.md](research/nq_calib_2026-11-24/README.md).

> **Hấp thụ (Absorption) đã gỡ hoàn toàn (2026-11-19):** indicator không còn tính, vẽ, niêm phong hay xác nhận hấp thụ đỉnh/đáy; các ô cài đặt và tham số của nó đã bị xoá, nên chart cũ lưu cài đặt hấp thụ cũng không bật lại được. Bản ghi niêm phong cũ có bóng hấp thụ bị bỏ khi nạp lại.

## Khác biệt so với bản ATAS
1. **Vẽ tay GDI+** (Quantower không có `PriceSelectionValue`) → tự tính + tự vẽ trong `OnPaintChart`.
2. **Exhaustion = đúng intrabar.** Quantower **CÓ** `Total.MaxDelta/MinDelta` (ghi chú port cũ sai) →
   không còn phải xấp xỉ bằng "delta swing".
3. **Big Trade dùng `MaxOneTradeVolume`** (lệnh đơn lớn nhất) — sát nghĩa "cú đánh lớn" hơn tổng
   volume/mức; không có fallback: feed không cấp số này (lịch sử) thì không có vòng mờ.
4. **Baseline robust median+MAD** (không mean+std) + ngưỡng z/percentile/ratio → **portable feed**.
5. Field map: `BuyVolume↔Ask`, `SellVolume↔Bid`, `Trades↔Ticks`, `Total.Delta/Volume` = cả nến.

## Nên bật gì trên M1 vs M30
| Tín hiệu | M1 | M30 | Ghi chú |
|---|:---:|:---:|---|
| Số Delta + Nến delta | ✅ | ➖ | M1 cần timing; M30 số chồng nhau |
| Big Trade | ✅ | ✅ | ngưỡng cố định 10 hợp đồng; chỉ feed sống có số lệnh đơn |
| Big Delta line | ✅ | ➖ | Nhiều mức ở HTF dễ rối |
| Exhaustion / Divergence / Sweep | ➖ | ➖ | Thử nghiệm, bật lẻ quan sát |

**Native Quantower nên thêm:** M1 → Cumulative Delta (line) + VWAP; M30 → Volume Profile phiên (VA + HVN/LVN).

## Bảng cấu hình then chốt (Settings)
> ⚠️ **Từ 2026-11-08 Settings chỉ còn 12 ô bật/tắt (từ 2026-11-18 thêm ô thứ 13; từ 2026-11-19 gỡ ô Hấp thụ nên còn 12 "Chấm Bid/Ask nhỏ · Bật"; sau đó thêm ô "Chấm Bid/Ask nhỏ · Nổ ở mọi mức giá" (mặc định tắt) — bật thì chấm nổ ở MỌI mức vượt ngưỡng, bỏ điều kiện lớn nhất trong ±4 tick; Settings còn 13 ô)** (Nến delta, Ô Bid/Ask lớn, Số Delta,
> Big Trade, Big Delta line, Kiệt sức, Stacked Imbalance, Divergence, Sweep, Unfinished, Stop-hunt) — người
> học không bao giờ chỉnh số nên mọi con số/màu bên dưới thành **hằng số mặc định trong code** (bỏ attribute
> `[InputParameter]`, giữ property). Giá trị chốt theo cấu hình đang chạy trên chart: Số Delta cỡ chữ **7**,
> cách đáy **8 px**, Big Delta line **tắt**; còn lại giữ mặc định. Muốn chỉnh số → sửa default trong code.
> Bảng dưới là tài liệu ý nghĩa các hằng số (một số con số trong bảng là lịch sử, xem code để biết giá trị hiện tại).

| Nhóm | Tham số | Ý nghĩa |
|---|---|---|
| Baseline | Số nến (100) · Warm-up (40) · **Sàn nhiễu** vol/mức (5), vol/nến (20) · **Số ô đậm nhất/nến (3)** | Cửa sổ median+MAD. **Top-3 ô** = so POC với POC lịch sử; để 0 sẽ nạp cả ô rìa 1-2 lot làm median tụt → tín hiệu nổ khắp nơi (lỗi bản cũ) |
| Big Trade: vòng tròn mờ = một lệnh đơn lớn (chốt 2026-11-19) | Người học chốt: vòng mờ là **một lệnh chủ động duy nhất rất lớn**, không phải volume cộng dồn của ô. Ví dụ chấm đặc thường nổ ở khoảng 9 hợp đồng (13 Bid hay 18 Ask có thể là 3 đến 4 nhà đầu tư nhỏ cộng lại), nhưng nếu 60 Bid đến trong **một** lệnh thì nổ vòng mờ: cá lớn vào chủ động. Luật: tại một mức giá, lệnh đơn lớn nhất ≥ **10 hợp đồng** (ngưỡng mặc định, chỉnh được) thì nổ; mọi mức giá đạt đều có vòng. Phía của lệnh đơn không có trong dữ liệu, nên màu lấy theo phía trội của ô (Ask nhiều hơn Bid thì xanh buy, ngược lại đỏ sell). Cỡ: 1,0 × bề ngang nến ở ngưỡng, 2,5 × từ 6 lần ngưỡng trở lên, theo đường căn bậc hai, kẹp 8 đến 80 px; độ đậm khoảng 35% và viền mảnh. Chấm đặc vẽ đè lên trên. Rê chuột: "Big trade: 1 lệnh n hợp đồng \| ô b Bid a Ask". Stop hunt chấp nhận bóng ở nến quét là chấm hoặc vòng Big Trade và tô tím cả hai. Chốt chặn lúc vẽ: bóng có giá ngoài [thấp nhất của nến − 2 tick, cao nhất + 2 tick] không được vẽ. Đã bỏ hoàn toàn bậc "vòng mờ dựa trên volume ô" của bản 19/11 sáng (bên trội ≥ 0,5 × trung bình, lớn nhất trong ±5 tick, ≥ 4 lần bên yếu). | **Hiệu chỉnh từ nhật ký sống** (4.169 nến M1, 10 đến 19/11/2026): lệnh đơn trung vị 1, phân vị 99 là 9, phân vị 99,9 là 23, lớn nhất 186. Ngưỡng 10 cho 0,15 vòng mỗi nến M1 và 0,73 vòng mỗi nến M5 (CORVEN vẽ khoảng 0,96 vòng mờ mỗi nến M5); ngưỡng 20 cho 0,13 mỗi nến M5; ngưỡng 60 cho 0,014 (khoảng một lần mỗi 6 giờ). Bảng đầy đủ: [research/corven_m5_2026-11-18/](research/corven_m5_2026-11-18/README.md). ⚠ Lịch sử không có số lệnh đơn nên không đếm được vòng mờ trên 87.362 nến M1 (0 vòng); chỉ chạy sống mới thấy. Dấu vân tay `bigtrade-v1`. |
| Ô Bid/Ask: chấm nhỏ đặc, xét riêng từng bên (2026-11-19, chiều muộn) | Luật xét **theo từng tick**, không gom hàng; bóng nằm đúng giá khớp của ô. Mức nền = **trung vị** volume của các ô có giao dịch trong một nến, lấy trung bình trên **20 nến đã đóng liền trước** (cần ít nhất 5 nến). **Bid và Ask được xét riêng ở từng tick.** Chấm **đỏ** (sell) nổ khi Bid tại tick ≥ **2,8 ×** mức nền, **và** Bid lớn hơn hẳn Bid của mọi tick khác trong ±**4** tick cùng nến (tick vắng tính 0, bằng nhau thì không nổ), **và** Bid ≥ sàn **9 hợp đồng**. Chấm **xanh** (buy) tương tự với Ask. Một tick có thể có cả hai. **Luật che** (CORVEN vẽ đỏ đè xanh): chấm xanh bị bỏ nếu cùng nến có chấm đỏ cách ≤ **6** tick. Thứ tự vẽ: xanh trước, đỏ sau (đỏ nằm trên; rê chuột ưu tiên chấm nằm trên). **Tím** nếu thuộc nến quét của stop hunt. Cỡ chấm 45% bề ngang nến, kẹp 5 đến 10 px. Ngưỡng cố định: chấm đỏ dùng Bid, chấm xanh dùng Ask, cùng ≥ max(ngưỡng cố định, sàn), vẫn cần lớn hơn hẳn trong ±4 tick và áp luật che. Không giới hạn số chấm mỗi nến. Chốt chặn lúc vẽ: bóng có giá ngoài [thấp nhất của nến − 2 tick, cao nhất + 2 tick] không được vẽ. Rê chuột: "Sell - 53 Bid (Ask 39) \| ngưỡng 31" hoặc "Buy - 40 Ask (Bid 12) \| ngưỡng 31" (ngưỡng = 2,8 × mức nền, ít nhất sàn). | Trên 26 nến M5 mẫu: **33 chấm sau khi che (10 xanh + 23 đỏ)**; ở các nến giảm 12:35 đến 12:55, CORVEN vẽ 1 xanh và 17 đỏ, luật cũ ra 9 xanh và 10 đỏ, luật mới ra 4 xanh và 10 đỏ. Trùng ở mức điểm ảnh F1 0,33 (luật cũ 0,43): luật mới là lựa chọn theo màu mắt thấy, chưa khớp hơn về điểm số. ⚠ Một biểu đồ, không phải lợi thế đã kiểm định. Số liệu trên 87.362 nến M1 (cấu hình mặc định), trước và sau: chấm 32.140 (16.373 đỏ + 15.767 xanh) → 40.590 (25.094 đỏ + 15.496 xanh), dấu stop hunt 496 → 568, bóng tím 660 → 715, kiệt sức 12.594 không đổi. Dấu vân tay `cellbig-v18` / `exh-v3` / `stophunt-v8`. |
| Kiệt sức (luật chỉnh 2026-11-19) | Đỉnh soi bên **Ask**, đáy soi bên **Bid**, chỉ lấy ở **râu nến**. Một nến có dấu khi: râu phía đó dài ≥ **3 tick** (`ExhMinWickTicks`) **và** tổng volume bên soi trên **6 tick** tính từ cực trị đi vào trong (`ExhSumLevels`) ≤ **1,1 ×** volume trung bình mỗi ô có giao dịch của **20 nến đã đóng liền trước** (`ExhSumHistRatio`; mức nền lịch sử, không phải trung bình của chính nến; chưa đủ 5 nến thì chưa đánh dấu). Mức giá trống tính 0. Dấu bị vô hiệu khi một nến sau chỉ cần râu quét qua mức đó (`ExhSweepTicks`); tam giác hết hiệu lực vẫn được tô đặc nền mờ. | Đo trên 26 nến M5 ngày 18/11: CORVEN 11 dấu; luật ra **13 dấu, trùng 11, thừa 2, sót 0** (F1 0,917). Điểm số này là kết quả **sau khi chọn tham số trên chính 26 nến đó**, nên lạc quan; nhưng số trùng giữ nguyên trên một vùng tham số rộng nên luật không phải một ngưỡng may mắn. ⚠ Một biểu đồ; chỉ là dấu để đọc chart, **không phải tín hiệu đã kiểm định lợi thế**. Big Trade không chỉnh được vì lịch sử không có kích cỡ từng lệnh đơn. Logic ở `ExhaustionLogic.cs`, kiểm bằng `tests/ExhaustionTests.cs` |
| Nến delta | deltaPct (0.30) · z (2.0) · cổng volume (0.8×) · độ đậm tô (85) | Tô thân xanh/đỏ khi delta lớn & 1 chiều |
| Big Trade | lệnh đơn lớn nhất tại mức giá ≥ 10 hợp đồng | Không còn điểm z, không so trung vị, không giới hạn số vòng |
| Big Delta line | deltaPct (0.35) · z (2.0) · top-N (2) | Số gạch ngang mạnh nhất mỗi nến |

## Thông số MGC/GC (Micro/Full Gold)
Tick 0.10. **Không cần** đổi ngưỡng khi chuyển GC↔MGC hay đổi feed — z/ratio tự chuẩn hoá. Chỉ chỉnh
**sàn nhiễu** (`MinLevelVolFloor`/`MinBarVolFloor`) cho khớp thang volume của feed (MGC nhỏ → để thấp;
GC lớn → có thể nâng). Ít tín hiệu → hạ z; nhiễu → tăng z.

## Tốc độ nạp (2026-11-11)
Nạp lại nguội 87.362 nến M1 (đổi tham số / bản DLL mới → tính lại + niêm phong) nhanh hơn ~10 lần nhờ ghi niêm phong theo lô, median+MAD cuốn, danh sách vùng đang hoạt động; đọc file niêm phong nhanh hơn và file tự nén khi nhiều dòng thừa. Dữ liệu không đổi (golden hash khớp). Số đo + cách chạy: `perf/README.md`, `research/PERF-RESEARCH-2026-11-11.md`.
