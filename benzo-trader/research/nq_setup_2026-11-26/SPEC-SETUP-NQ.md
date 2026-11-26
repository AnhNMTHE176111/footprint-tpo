# SPEC — Chuẩn setup CORVEN cho NQ M1 (làm lại từ đầu, chốt 2026-11-26)

> **Trạng thái:** spec chốt TRƯỚC khi nhìn kết quả tháng kiểm tra (2026-10-26 → 2026-11-25).
> **Nguồn luật duy nhất:** lời CORVEN và quan sát trên chart CORVEN, lấy từ
> [THU-THAP-1-van-ban.md](THU-THAP-1-van-ban.md) (viết tắt **TT1**) và [THU-THAP-2-meet-chart.md](THU-THAP-2-meet-chart.md) (viết tắt **TT2**),
> đã đối chiếu `corven-meet/2026-11-07/transcript.md` và `data-export/messages-with-pro-trader/CORVEN_TONG_HOP.md`.
> Không dùng luật, tham số hay số backtest nào của Benzo cũ.
> **Đây là luật chưa đo.** Chưa có con số nào nói setup này có lợi thế; mục 4 là cách đo.

## 0. Quy ước

- **Nhãn nguồn** trên mỗi luật:
  - **[CORVEN nguyên văn]** — có câu CORVEN nói/viết (mã dòng + mốc giờ Meet hoặc tên ảnh chat).
  - **[quan sát chart CORVEN]** — đọc từ chart/khung hình của CORVEN, không phải lời.
  - **[số do agent chọn để cơ khí hoá]** — CORVEN không cho số; agent chọn số sát nghĩa nhất, có ghi lý do.
- Dòng loại [người học diễn giải] / [Claude diễn giải] **không** làm luật. Dòng `[CV-video]` (chữ slide video, không còn ảnh gốc để đối chiếu) **không** làm luật riêng, chỉ ghi nhãn trên lệnh để xem sau (mục 6).
- Sản phẩm: **NQZ26**, khung **M1**, tick 0,25 điểm, **1 hàng = 8 tick = 2 điểm** như chart CORVEN (TT2-C22).
- "Nến i" = nến M1 vừa **đóng**. Mọi luật chỉ dùng nến ≤ i. Lệnh khớp ở giá mở nến i+1.
- `mbr` = trung vị (high − low) của 100 nến M1 gần nhất tính tới nến i (đúng cách tính của Range Box). Trước 2026-10-26, mbr NQ: trung vị 8,75 điểm (phiên Á 7,25 · Âu 9,0 · Mỹ 11,75).
- `TB|delta|20` = trung bình |delta| của 20 nến trước nến i (không gồm nến i).
- Giờ: file dữ liệu ghi **UTC**. Phiên tính theo giờ **New York** (tự đổi mùa hè/đông): Á 18:00–03:00, Âu 03:00–09:30, Mỹ 09:30–17:00.
- Dữ liệu dày chỉ có từ **2026-09-14**. Đoạn chọn số = 2026-09-14 → 2026-10-23. Trước 09-14 dữ liệu mỏng, không dùng.

## 1. Chuẩn setup (một chuẩn duy nhất)

**Một câu:** trên M1, xác định cấu trúc và range; chờ giá về **một trong ba loại mốc** (cạnh range đang hiệu lực · cạnh range vừa bị Break · vùng stacked imbalance gần cùng hướng cấu trúc); tại mốc phải có **nến tín hiệu đã đóng** với **bóng + delta cùng phe** và **thêm ít nhất một tín hiệu order flow nữa**; SL sau mốc quan trọng; TP 2R.

Ba loại mốc dùng **chung** tầng xác nhận và tầng lệnh; chỉ khác bối cảnh cho phép. Tên gọi trong báo cáo: **Fail Break** (đánh ngược vào lòng range tại cạnh), **Break** (retest sau khi phá range), **Test vùng stacked** (đi theo cấu trúc).

### Tầng A — Cấu trúc thị trường (M1)

| # | Luật | Số cho NQ | Nguồn | Nhãn |
|---|---|---|---|---|
| 1 | Tìm cấu trúc trên đúng khung đang đánh = M1 | M1 | TT2-A10 [0:17:20] "Dùng khung nào thì tìm cấu trúc của khung đấy" | [CORVEN nguyên văn] |
| 2 | Đỉnh/đáy cấu trúc = đỉnh/đáy nhỏ, gần nhất, một nến là đủ | Tại lúc nến i đóng, nến j = i−1 là **đỉnh** nếu High[j] > High[j−1] và High[j] ≥ High[i]; là **đáy** nếu Low[j] < Low[j−1] và Low[j] ≤ Low[i] | TT2-A11 [0:42:23] "Chỉ cần một cái nến thôi", [0:42:34] "Chỉ cần nhỏ thôi, gần nhất thôi"; TT1-A10 "đỉnh đáy cấu trúc" | Luật: [CORVEN nguyên văn]. Công thức 1 nến mỗi bên: [số do agent chọn để cơ khí hoá] — pivot nhỏ nhất có thể, đúng chữ "một nến", trùng công thức Range Box |
| 3 | Gãy cấu trúc tính bằng **nến đóng cửa**, râu không tính | Close[i] < đáy gần nhất → gãy cấu trúc tăng; Close[i] > đỉnh gần nhất → gãy cấu trúc giảm. Râu vượt mà đóng lại = chưa gãy | TT2-A14 [1:04:00] "phải nến đóng cửa chứ… Không dùng râu nến"; TT2-A15 [0:43:53] "Phá mà rút râu luôn thì khả năng là fail"; TT2-A19 [0:21:59] | [CORVEN nguyên văn] |
| 4 | Hướng cấu trúc: **tăng** khi (a) vừa có nến đóng trên đỉnh gần nhất, hoặc (b) hai đỉnh gần nhất và hai đáy gần nhất đều cao dần; **giảm** thì ngược lại. Giữ hướng cũ tới khi có điều kiện ngược | — | TT2-A16 [0:43:09] "gãy cấu trúc giảm… tạo 2 đỉnh đáy cao dần cũng là cấu trúc tăng" | [CORVEN nguyên văn] |

Phương án còn lại (không chọn): pivot cần 2–3 nến mỗi bên; hoặc "giữ được" = thêm 1 nến sau vẫn đóng ngoài (TT2-A15 đọc chặt). Không chọn vì CORVEN trả lời thẳng "chỉ cần một cái nến".

### Tầng B — Bối cảnh

| # | Luật | Số cho NQ | Nguồn | Nhãn |
|---|---|---|---|---|
| 5 | **Range** = cụm nến đi ngang trên M1; cạnh đặt ở chỗ giá phản ứng nhiều; hai vùng chồng nhau thì gộp | Dùng nguyên máy trạng thái `quantower-range/RangeLogic.cs` trên nến M1 NQ, tick 0,25, tham số mặc định: lõi ≥ 8 nến, cao 1,6–6 × mbr, dung sai cạnh `tol` = max(2 tick; 0,5 × mbr), chờ 3 nến sau nến đóng ngoài, cho quay lại trong 30 nến, tối đa 2 lần quay lại | TT2-A1 [0:12:56], A4 [0:14:50], A5 [0:14:42], A6 [0:13:58] "M1 dùng range nhỏ hơn"; TT1-A7 "Tìm biên m1 xong et m1 luôn"; hình dạng hộp TT2-A28, A29 (hộp NQ ≈ 43 điểm, 23 nến) | Luật: [CORVEN nguyên văn]. Tham số: [quan sát chart CORVEN] (khớp 20 hộp CORVEN vẽ tay) — theo mbr nên dùng thẳng cho NQ, không chỉnh lại |
| 6 | **Ba trạng thái bối cảnh**, đánh kiểu nào theo trạng thái đó: (i) **đang range** (range Active/Pending) → chỉ đánh ở cạnh range; (ii) **vừa Break** (có `BreakConfirmed`, còn trong 30 nến) → chỉ đánh theo hướng phá; (iii) **không có range** → đánh theo cấu trúc | 30 nến = hằng G của Range Box | TT2-A2 [0:16:29] "đi range… đánh theo range; còn khi nó trend thì mới đánh theo trend"; TT2-A23 [0:39:16]; TT1-A2 "xác định range rồi 2 cạnh mà vả"; TT1-A3 "Giờ break ra là follow theo" | [CORVEN nguyên văn] |
| 7a | **Vùng stacked imbalance** là một vùng (lo–hi), buy làm hỗ trợ, sell làm kháng cự | Lấy `zoneB` / `zoneS` của OrderFlowBubbles (so chéo 250%, 3 hàng liên tiếp, hàng 8 tick) | TT2-B10 [0:03:14], C1 [0:03:56] "đang để 250%", C7 [0:17:58]; TT2-C22 | [CORVEN nguyên văn] + [quan sát chart CORVEN] |
| 7b | **Chất lượng vùng theo vị trí trong nến sinh ra nó:** giữa thân nến thì dùng; nằm ở râu thì chỉ dùng nếu nến sau đi tiếp | Vùng **đạt** nếu phần vùng nằm trong thân nến sinh (giữa Open và Close) ≥ 50% chiều cao vùng. Nếu không: chỉ đạt khi nến kế đóng vượt qua vùng theo hướng vùng (buy: Close > hi; sell: Close < lo); không thì bỏ vùng | TT2-C2 [0:03:35] "ở giữa thân nến thì nó mới khỏe", C3 [0:03:40]–[0:03:45], C4 [0:19:38] | Luật: [CORVEN nguyên văn]. 50%: [số do agent chọn để cơ khí hoá] — "giữa thân" = quá nửa vùng nằm trong thân. Trước 10-26: 89% vùng đạt ngay |
| 7c | **Vùng chỉ có giá trị sau khi giá đã rời vùng** rồi quay lại test | Vùng buy "sẵn sàng" khi có một nến sau đó có Low > hi (sell: High < lo). Lần test = nến đầu tiên sau đó chạm lại vùng (buy: Low ≤ hi) | TT2-C7 [0:05:41] "giá đi lên mà tạo ra stacked imbalance, xong nó test về"; TT2-C9 [0:18:21] "nó lên, xong quay lại test stacked gần" | Luật: [CORVEN nguyên văn]. "Rời vùng" = cả nến nằm ngoài vùng: [số do agent chọn để cơ khí hoá] |
| 7d | **Vùng hết hiệu lực** khi: bị đâm thủng · ở xa · cấu trúc đã gãy · đã bị chạm | (1) có nến **đóng** qua mép xa (buy: Close < lo); (2) tuổi > **30 nến** tính từ nến sinh; (3) hướng cấu trúc (luật 4) khác hướng vùng tại bất kỳ lúc nào sau khi vùng sinh; (4) hết **lần test đầu tiên** (3 nến kể từ nến chạm) | TT2-C13 [0:06:29], C14 [0:06:54] "Dùng gần thôi, đừng dùng xa", C15 [0:20:00], C16 [0:20:12] "chạm một mớ… vứt luôn", C10 [0:18:39]; TT2-C20 (dải vẽ tới lần chạm đầu) | Luật: [CORVEN nguyên văn] + [quan sát chart CORVEN]. **30 nến** và **chỉ lần chạm đầu**: [số do agent chọn để cơ khí hoá] — ca CORVEN chỉ trên NQ (khung 0-09-42) retest trong ≤ 28 nến; trước 10-26, 84% lần test đầu rơi trong 30 nến; dải trên chart CORVEN dừng ở lần chạm đầu |
| 7e | **"Giá không được phép test quá sâu"** | Trong lần test không được có nến **đóng** qua mép xa của vùng / qua cạnh range vừa phá (đã nằm trong 7d-1 và luật 12) | TT1-A13 (CORVEN_TONG_HOP d.20); TT2-C13 | Luật: [CORVEN nguyên văn]. Ngưỡng "mép xa, tính nến đóng": [số do agent chọn để cơ khí hoá] — theo "dùng nến đóng cửa hết" (TT2-A14) |
| 8 | **Bias phiên:** mỗi phiên một bias; xem bên nào kiểm soát thì theo bên đó; bias tăng thì chỉ canh buy | Tại nến i: `cumΔ` = tổng delta từ đầu phiên; `Δgiá` = Close[i] − giá mở phiên. **Bias buy** nếu cumΔ > 0 và Δgiá > 0; **bias sell** nếu cả hai < 0; còn lại (hoặc 30 nến đầu phiên) = **chưa có bias**. Có bias thì các lệnh **Break** và **Test vùng stacked** chỉ được vào cùng hướng bias; chưa có bias thì không chặn. **Fail Break không bị lọc bias** (CORVEN đánh cả hai cạnh range) | TT1-B14 (IMG_1802–1803) "can đo đong đếm giữa buy và sell" · "xem bên nào đang kiểm soát thì theo bên đó" · "bias tang thì chỉ canh mua" · "mỗi phiên sẽ có một bias"; TT2-C79 [0:31:49] "nhìn cấu trúc của delta để xem buyer hay seller đang kiểm soát… có tương xứng không"; TT1-A2 (2 cạnh) | Luật: [CORVEN nguyên văn]. Công thức cumΔ + Δgiá, 30 nến khởi động, ranh giới 3 phiên: [số do agent chọn để cơ khí hoá] — đây là chỗ cơ khí hoá **yếu nhất** (CORVEN: "đưa ra bias thì cần nhiều") |
| 9 | **Mốc lớn (bản đồ):** HVN/POC của TPO và VWAP — chạm thì giá có thể đảo chiều hoặc phá | Tính nhân quả 4 mốc: **VWAP ngày** (neo 18:00 NY), **VWAP tuần** (neo 18:00 NY Chủ nhật), **POC TPO tuần trước**, **POC TPO hôm trước** (TPO 30 phút, hàng 2 điểm; POC = hàng có nhiều chữ nhất, hoà thì lấy hàng gần giữa profile). Mốc POC chỉ tính khi giá đã từng **rời** mốc trong tuần/ngày hiện tại. Lệnh có giá vào cách mốc ≤ **10 điểm** được gắn nhãn `tại mốc lớn` (tuần → kịch bản 1; ngày → kịch bản 2.1; không mốc → kịch bản 2.2). **Chỉ gắn nhãn, không lọc** | CORVEN_TONG_HOP (TT1-B1, B2): "Vùng quan trọng của TPO là HVN… có thể đảo chiều hoặc Phá vùng", 3 kịch bản; TT1-B6 "1 preiod vẫn là 30p"; TT2-B2 [1:11:00]–[1:11:24]; TT2-B4 [1:12:59] "POC cũng là HVN"; TT2-B13 (VWAP trên chart NQ) | Luật mốc: [CORVEN nguyên văn]. Chỉ lấy POC (không lấy bướu HVN khác), 10 điểm, neo VWAP: [số do agent chọn để cơ khí hoá] — CORVEN không nói cách tính bướu HVN và không nói chạm mốc thì đánh hướng nào, nên **không thể làm bộ lọc có hướng**; điểm vào tại mốc lớn vẫn cần xác nhận M1 (TT1-D1) = đúng tầng D |
| 10 | **Giờ:** CORVEN chọn R:R theo giờ vào nhưng không cho giờ nào cho NQ | Không lọc giờ. Báo cáo tách theo 3 phiên. Không vào lệnh mới sau 16:45 NY | TT1-B15, B16 | Không lọc: vì CORVEN không cho số. 16:45: [số do agent chọn để cơ khí hoá] (mô phỏng, mục 4) |

### Tầng C — Mốc vào (3 loại, cùng một chuẩn xác nhận)

Ký hiệu chung: `W` = cửa sổ phản ứng = 3 nến [i−2, i]. `E` = cạnh range. Viết cho **buy**; sell đối xứng.

| # | Mốc | Điều kiện bối cảnh + chạm mốc | Nguồn | Nhãn |
|---|---|---|---|---|
| 11 | **Fail Break — cạnh range đang hiệu lực** (đánh ngược vào lòng range) | Range Active/Pending (trạng thái i). Trong `W` có nến chạm cạnh dưới: Low ≤ E_dưới + tol (gồm cả râu thò ra, cả nến đóng ngoài). Nến i **đóng trong lòng range**: E_dưới < Close[i] < E_trên. Không cần cùng hướng cấu trúc, không lọc bias | TT2-A22 [0:08:29] "Khi nó fail break thì tìm tín hiệu sell"; TT2-D4 [0:08:46] "Chơi được. Hoặc cẩn thận thì chờ 1–2 cây"; TT2-D5 [1:00:02] "phải vào lòng range nữa"; TT2-C32 [0:55:06]; TT2-C60 [0:09:42] (ca NQ); TT2-A26 [0:56:28] | Luật: [CORVEN nguyên văn]. `W` = 3 nến: [số do agent chọn để cơ khí hoá] — "1–2 cây sau" + chính nến quét; bằng hằng K = 3 của Range Box |
| 12 | **Break — retest cạnh range vừa bị phá** (đánh theo hướng phá) | Có `BreakConfirmed` lên trên cạnh E_trên, chưa quá 30 nến từ nến đóng ngoài đầu tiên. Trong `W` có nến về chạm cạnh vừa phá: Low ≤ E_trên + tol. Nến i đóng **ngoài** range: Close[i] > E_trên. Hướng cấu trúc = tăng. Không ngược bias | TT2-D10 [0:12:39] "confirm được buy, xong retest về, đáy bị kiệt sức, buy lên"; TT2-D9 [0:20:31] "retest lên range, retest luôn cái stacked imbalance này → sell"; TT2-D8 [0:11:23] (ca NQ); TT2-A15 [0:43:53] "phá thì phải giữ được"; TT2-D1 [0:08:16] "Chưa vội buy luôn"; TT2-A20 [0:11:20] | Luật: [CORVEN nguyên văn]. 30 nến: [quan sát chart CORVEN] (hằng G của Range Box) |
| 13 | **Test vùng stacked — đi theo cấu trúc** | Trạng thái (ii) hoặc (iii) (không dùng vùng khi đang range). Vùng `zoneB` đạt 7b, sẵn sàng 7c, còn hiệu lực 7d. Nến chạm đầu tiên nằm trong `W`. Nến i đóng **trên mép gần**: Close[i] ≥ hi. Hướng cấu trúc = tăng suốt từ lúc vùng sinh. Không ngược bias | TT2-C7 [0:17:58] "dùng làm mốc tham chiếu — để giá về đấy xem phản ứng trước rồi mới buy lên"; TT2-C9 [0:18:21]; TT2-C10 [0:18:39] "cấu trúc vẫn phải giữ được"; TT2-C11 [0:07:08]; CORVEN_TONG_HOP "Follow theo Orderflow (không cản tàu)" | [CORVEN nguyên văn] |

Ghi chú luật 12: nếu sau `BreakConfirmed` có nến đóng lại trong lòng range thì Range Box chuyển về range (quay lại, tối đa 2 lần) → áp luật 11.

### Tầng D — Xác nhận order flow tại mốc (dùng chung cho cả 3 mốc)

Tất cả phải đúng tại nến i (viết cho buy):

| # | Luật | Số cho NQ | Nguồn | Nhãn |
|---|---|---|---|---|
| 14 | **Nến tín hiệu đã đóng và đóng đẹp** | Close[i] > Open[i] và (Close − Low) / (High − Low) ≥ 0,5 | TT2-D13 [1:01:13] "Xem nó phản ứng thế nào, có đẹp không. K11 đẹp rồi → vào thôi"; TT1-C13 (IMG_1814–1815) "Đóng có đẹp k · Mấy cây giảm đóng râu dưới vẫn rút kìa" | Luật: [CORVEN nguyên văn]. Nửa trên biên độ: [số do agent chọn để cơ khí hoá] |
| 15 | **Bắt buộc: delta buy + bóng xanh cùng vào** | Delta[i] > 0 và \|Delta[i]\| ≥ 1,0 × `TB\|delta\|20`; **và** nến i có ít nhất một `dotB` (hoặc `bt` mà mức giá đó Ask > Bid) | TT2-C43 [0:46:13] "Delta buy với bóng xanh phải vào… nó nhỏ mà… không có bóng xanh"; TT2-C83 [0:35:55] "Delta dương nhưng nhỏ thì không đánh được"; TT2-D2 [0:08:23]; TT1-A1 "phải nhìn sang cả delta nữa"; TT2-C77 [0:31:42] | Luật: [CORVEN nguyên văn]. Ngưỡng 1,0 × trung bình 20 nến: [số do agent chọn để cơ khí hoá] — "không nhỏ" = không dưới mức thường; trước 10-26 có 37% nến đạt |
| 16 | **Bắt buộc: thêm ít nhất 1 tín hiệu cùng phe nữa** (không vào khi "tín hiệu mới có mỗi một cái") | Ít nhất một trong: (a) **kiệt sức đáy**: có `exhB` trong `W`, còn hiệu lực (chưa nến nào sau đó có Low thấp hơn Low nến mang dấu); (b) **stop hunt đáy**: có dấu trong `sh.csv` với side = day, sweep_time trong `W`, và Close[i] > level; **hoặc** trong `W` có nến thò dưới cạnh range ≥ 1 tick và nến đó có bóng (màu nào cũng tính) ở giá ≤ cạnh + 0,75 điểm; (c) **stacked buy mới**: có `zoneB` sinh trong `W` đạt 7b; (d) riêng luật 13: chính vùng đang được test là tín hiệu thứ hai | TT2-D5 [0:59:37]; TT2-D16 [1:05:57] "chơi những đoạn có nhiều tín hiệu cùng lúc"; TT2-C17 [0:07:01] "Phải kết hợp thêm cả bóng… chứ không dùng mỗi stacked imbalance"; (a) TT2-C25–C30, C35 [0:12:39]; (b) TT2-C55 [0:23:45], C61 [0:46:03], C62 [0:27:36], C68–C69; (c) TT2-C6 [0:07:38], D3 [0:08:29] | Luật: [CORVEN nguyên văn]. "Thêm ≥ 1" (tức tổng ≥ 2): số nhỏ nhất lớn hơn "mỗi một cái". 0,75 điểm (3 tick): [quan sát chart CORVEN] |
| 17 | **Kiệt sức ngược hướng thì chưa vào:** muốn sell mà đáy vừa kiệt sức sell thì chờ râu quét qua đáy đó | Sell bị chặn nếu trong 5 nến [i−4, i] có `exhB` chưa bị nến nào sau đó quét qua (Low thấp hơn). Buy bị chặn tương tự bởi `exhT` chưa bị quét. Vô hiệu chỉ cần **râu**, không cần đóng nến | TT2-C31 [0:53:05]–[0:53:35]; TT2-C30 [0:54:05]–[0:54:43] "Quét qua là được rồi, không cần [đóng nến]" | Luật: [CORVEN nguyên văn]. 5 nến: [số do agent chọn để cơ khí hoá] — "đáy vừa tạo" = vài nến gần nhất |
| 18 | **Ngoại lệ "xác nhận lần 2"** của luật 11: nến i chưa đóng vào lòng range vẫn vào được | Sau lần thò cạnh đầu tiên (trong 30 nến gần nhất), có nến trong `W` tạo đáy **thấp hơn** đáy lần thò trước (trap đáy lần nữa) **và** nến đó mang `exhB` còn hiệu lực; luật 14, 15 vẫn bắt buộc | TT2-D6 [1:00:09] "chưa vào lòng range nhưng nó confirm lại lần 2 rồi — nó trap đáy một lần nữa và bị kiệt sức đáy → vào được"; TT2-D7 (khung 0-59-50) | Luật: [CORVEN nguyên văn] + [quan sát chart CORVEN]. 30 nến: [số do agent chọn để cơ khí hoá] |

### Tầng E — Lệnh

| # | Luật | Số cho NQ | Nguồn | Nhãn |
|---|---|---|---|---|
| 19 | **Vào** sau khi nến tín hiệu đóng, một lần đủ khối lượng | Lệnh **market** tại giá mở nến i+1 | TT2-D4, D12 [0:21:34] "chơi từ cây …", D13; TT1-D11 "vào một phát to" | "Vào theo nến tín hiệu": [CORVEN nguyên văn]. Market ở giá mở nến kế: [số do agent chọn để cơ khí hoá] — CORVEN không nói limit hay market (TT1-D17, TT2-D19) |
| 20 | **SL sau mốc quan trọng**, không đặt sát; buy sau cú quét thì SL dưới cái đáy vừa quét; SL xa quá thì bỏ; SL không ngắn quá | SL buy = min(Low thấp nhất từ nến chạm mốc tới nến i; mép xa của mốc: cạnh range hoặc `lo` của vùng) − **2 điểm** (1 hàng). Nếu khoảng SL < **5 điểm** thì nới ra đúng 5 điểm. Nếu khoảng SL > **3 × mbr** thì **bỏ lệnh** (không kéo SL lại gần) | TT2-E1 [0:50:18]–[0:50:25] "Đặt gần thì dễ bị quét"; TT2-E2 [0:51:25] "đặt dưới cái đáy mới quét"; TT2-E3 [0:51:16] "SL bị xa quá thì thôi"; TT2-E5 [0:59:07]; TT2-C57 [0:24:11] "trên đỉnh này một tí"; TT1-E1 "Đừng ngắn quá vì ngắn quá bị lỗ phí"; TT1-E2 "Khoảng dưới cây m1 thôi · Từ 2- 4 giá"; TT1-E3 "Sl 5 giá ổn đấy"; TT1-E11 | Vị trí SL: [CORVEN nguyên văn]. **2 điểm**, **5 điểm**, **3 × mbr**: [số do agent chọn để cơ khí hoá] — "một tí" = 1 hàng giá của chart CORVEN; 5 điểm = phí 1 điểm không quá 20% rủi ro; 3 × mbr = quy đổi "5 giá ổn" của vàng (≈ 3 lần biên độ nến M1 vàng 1,7 giá; tính theo % giá cũng ra ≈ 29 điểm NQ) |
| 21 | **R:R tối thiểu 2R; khoảng 1,7R tới cạnh range đối diện thì chấp nhận; TP vẫn đặt 2R** | TP = giá vào ± **2,0 × khoảng SL**. Riêng **Fail Break**: chỉ vào khi khoảng từ giá vào tới cạnh range đối diện ≥ **1,7 × khoảng SL** (tính bằng giá khớp thật). **Break** và **Test vùng stacked**: TP 2R, không kiểm khoảng trống | TT2-E6 [0:58:13] "Nếu không 2R thì không chơi nữa"; TT2-E7 [0:58:35]; TT2-E8 [0:58:49] "Tầm 1,7R là được. Nhưng TP vẫn cứ đặt 2R"; TT2-E9 (khung 0-58-35, "R/R: 1.71"); TT2-D18 [0:58:29] | [CORVEN nguyên văn]. Với Break / Test vùng CORVEN không nói đo khoảng trống tới đâu → không thêm luật |
| 22 | **Một lệnh mở, không nhồi** | Đang có lệnh thì bỏ mọi tín hiệu mới | TT1-D11 (IMG_1812–1813) "nay t méo nhồi nữa · vào một phát to mẹ luôn" | [CORVEN nguyên văn] |
| 23 | **Quản lý lệnh:** CORVEN không nói dời SL, hoà vốn, chốt từng phần | Giữ nguyên SL và TP tới khi chạm; cuối phiên CME thì đóng (mục 4) | TT1-E22, TT2-E11 (ghi "CORVEN không nói") | Không thêm luật |

Phương án R:R còn lại (không chọn làm chuẩn): 1:4 – 1:6 trong chat đầu năm (TT1-E8 "đánh RR 1:4 là ngon rồi chú", TT1-B16, E4). Chọn 2R vì Meet 07/11 là nguồn mới nhất, nói thẳng thành luật trên đúng loại chart M1 này và nói cả cách xử lý 1,7R; chat chỉ là ví dụ lệnh. Backtest in thêm cột phụ "TP 4R" để tham khảo, **không dùng để chọn**.

### Tầng F — Điều cấm (đều là hệ quả của các luật trên; không thêm số mới)

| # | Cấm | Thực thi bởi | Nguồn |
|---|---|---|---|
| F-1 | Không đánh theo trend khi thị trường đang range; không dùng vùng stacked giữa lòng range | luật 6, 13 | TT2-F17 [0:16:29] |
| F-2 | Không đánh riêng stacked imbalance | luật 15 + 16 | TT2-F1 [0:07:01], [0:07:47] |
| F-3 | Không dùng vùng stacked ở xa / cấu trúc đã gãy / đã chạm nhiều / bị đâm thủng | luật 7d | TT2-F2, F3, F4, C13 |
| F-4 | Không vào khi Break chưa có dấu hiệu | luật 12 + 15 + 16 | TT2-F5 [0:08:16] |
| F-5 | Không vào khi nhịp sau trap yếu (delta nhỏ, không bóng) | luật 15 | TT2-F6, F7, F10 |
| F-6 | Không vào khi còn ngoài range mà mới một tín hiệu | luật 11, 16, 18 | TT2-F11 [0:59:37] |
| F-7 | Không vào hướng mà kiệt sức đang chống | luật 17 | TT2-F16 |
| F-8 | Không đánh theo hướng cũ khi cấu trúc đã gãy (không cản tàu) | luật 12, 13 (cùng hướng cấu trúc) | TT2-F19 [0:11:20]; TT1-F1 |
| F-9 | Không tính phá bằng râu; không lấy kiệt sức ở thân nến | luật 3, 5; tín hiệu `exh` của OrderFlowBubbles lấy ở râu | TT2-F14, F15 |
| F-10 | Không chơi dưới 2R (nới 1,7R); không đặt SL sát; SL xa quá thì bỏ; SL không ngắn quá | luật 20, 21 | TT2-F12, F13; TT1-F4, F11 |
| F-11 | Không nhồi lệnh | luật 22 | TT1-F10 |
| F-12 | Không đánh ngược bias phiên (áp cho Break và Test vùng) | luật 8 | TT1-F12 |
| F-13 | Không dùng range khung lớn để vào lệnh M1 | luật 5 (chỉ range M1) | TT2-F21 [1:08:57] |
| F-14 | Không dùng mốc HVN/POC khi giá còn nằm trong vùng | luật 9 | TT2-F18 [1:11:00] |

## 2. Chỗ CORVEN nói hai cách — đã chọn cách nào

| Vấn đề | Chọn | Vì sao | Phương án còn lại |
|---|---|---|---|
| Có đánh trong range không (TT1-G1) | Có, đánh hai cạnh (Fail Break) **và** đánh Break | Meet 07/11 có hơn 10 câu về đánh cạnh range (TT2-A2, A3, A22, C32, C60, D3–D6, E7…) + chat 08/08 "2 cạnh mà vả"; phía kia chỉ một câu "Đánh break thôi chú" (05/05, đang nói về sơ đồ Wyckoff của người học) | Chỉ đánh Break: backtest đã tách theo loại mốc nên đọc được ngay |
| R:R (TT1-G2) | TP 2R, sàn 1,7R | xem dưới luật 21 | 1:4 trở lên (cột phụ) |
| SL ngắn hay SL sau mốc (TT1-G3) | SL sau mốc quan trọng, có sàn 5 điểm và trần 3 × mbr | Meet nói thẳng và giải thích lý do (quét râu); chính chat cũng nhận SL ngắn "dễ quét lắm" | SL "dưới cây M1" = râu nến tín hiệu − 1 tick |
| Vào ngay nến tín hiệu hay chờ 1–2 nến (TT2-G3) | Vào ngay sau nến tín hiệu đóng | "Chơi được" là câu trả lời đầu; chờ là "hoặc cẩn thận thì…" | Chờ thêm 1 nến còn đóng trong range |
| "xem phản ứng rồi mới buy" hay "không phản ứng thì buy" (TT2-G9) | Phải có nến phản ứng (luật 14–16) | [0:17:58], [1:01:13], [0:08:16] cùng nói chờ phản ứng; câu [0:18:13] máy nghe thiếu chữ | Vào limit tại vùng không chờ phản ứng |
| Kiệt sức vừa là tín hiệu vừa là cảnh báo (TT2-G5) | Cùng phe → tín hiệu (16a); ngược phe → chặn (17) | đúng hai vai CORVEN mô tả | — |
| POC/VAH/VAL hay chỉ HVN (TT1-G4) | HVN, trong đó POC là một HVN | "Vùng quan trọng của TPO là HVN" + "POC cũng là HVN" | VAH/VAL: không dùng |
| TPO 1 tuần hay gộp 3 tuần (TT1-G5) | 1 tuần (tuần trước) | "nhìn hẳn tuần cho bao quát" + CORVEN_TONG_HOP "TPO tuần"; "Gộp 3 week" chỉ một lần | Gộp 3 tuần |
| Ngoại lệ không bóng vẫn vào (TT2-C44, có dấu [?]) | Không dùng | câu máy nghe không chắc; trái với [0:46:13] | — |

## 3. Chỗ mơ hồ và số agent đã chọn (tóm tắt)

| # | Chỗ CORVEN không cho số | Số chọn | Lý do ngắn |
|---|---|---|---|
| 1 | Đỉnh/đáy cấu trúc "nhỏ, gần nhất, một nến" | pivot 1 nến mỗi bên | sát chữ nhất |
| 2 | Kích thước range M1 | tham số Range Box theo mbr (lõi ≥ 8 nến, cao 1,6–6 × mbr, tol 0,5 × mbr) | khớp 20 hộp CORVEN vẽ |
| 3 | Vùng stacked "ở giữa thân nến" | ≥ 50% vùng nằm trong thân | — |
| 4 | Vùng stacked "gần / xa" | ≤ 30 nến M1 | ca NQ của CORVEN ≤ 28 nến; 84% lần test trong 30 nến |
| 5 | "Chạm một mớ thì vứt" | chỉ dùng lần test đầu (3 nến) | dải trên chart CORVEN dừng ở lần chạm đầu |
| 6 | "Test không quá sâu" | không có nến đóng qua mép xa của vùng / cạnh | "dùng nến đóng cửa hết" |
| 7 | Cửa sổ phản ứng tại mốc | 3 nến | "chờ 1–2 cây" + nến chạm |
| 8 | Delta "không nhỏ" | ≥ 1,0 × trung bình \|delta\| 20 nến trước | 37% nến đạt |
| 9 | "Nhiều tín hiệu cùng lúc" | bóng + delta **và** ≥ 1 tín hiệu khác | lớn hơn "mỗi một cái" |
| 10 | Nến "đóng đẹp" | cùng màu hướng lệnh, đóng ở nửa biên độ phía hướng lệnh | — |
| 11 | Kiệt sức ngược hướng "vừa tạo" | trong 5 nến gần nhất, chưa bị râu quét | — |
| 12 | SL "trên đỉnh một tí" | 2 điểm (1 hàng 8 tick) | đơn vị hàng của chart CORVEN |
| 13 | SL "ngắn quá lỗ phí" | sàn 5 điểm | phí 1 điểm ≤ 20% rủi ro |
| 14 | SL "xa quá thì thôi" | > 3 × mbr thì bỏ (≈ 26 điểm ở mbr trung vị) | quy đổi "5 giá ổn" của vàng |
| 15 | Loại lệnh vào | market, giá mở nến kế | CORVEN không nói |
| 16 | Bias phiên | dấu cumΔ phiên + dấu (Close − mở phiên), 30 nến khởi động; 3 phiên theo giờ New York | yếu nhất, xem luật 8 |
| 17 | Mốc lớn | VWAP ngày/tuần, POC TPO hôm trước/tuần trước; gần = ≤ 10 điểm; chỉ gắn nhãn | CORVEN không nói hướng đánh tại mốc |
| 18 | Stop hunt tại cạnh range | râu thò ≥ 1 tick + bóng trong 0,75 điểm quanh cạnh, hoặc dấu `sh.csv` | theo ca mẫu CORVEN |
| 19 | "Trap" | CORVEN không định nghĩa → coi là cú quét mốc rồi đóng ngược (stop hunt / thò cạnh range) | TT2-G15 |
| 20 | "Xác nhận lần 2" | đáy thấp hơn lần thò trước + kiệt sức đáy trên chính nến đó | đúng ví dụ duy nhất CORVEN nêu |

Chưa cơ khí hoá được (không có trong setup, không bịa thêm): "đầu sóng / cuối sóng" (TT1-A4, C11); đoán limit hay market đứng sau một nhịp (TT1-C1…C10, cần sổ lệnh); hấp thụ nhiều nến và phân kỳ delta ở đáy quan trọng (TT2-C78, C80–C82); "đang giảm mạnh thì không buy đảo chiều" (TT2-A25); cấu trúc lớn bọc cấu trúc nhỏ (TT2-A17); range khung 15 để đánh dài (TT2-A7, A8); "range chồng range thì khó" (TT2-A9 — chỉ có phần gộp range của Range Box).

## 4. Kế hoạch backtest

### 4.1 Dữ liệu và kỷ luật
- Nến: `data-export/data-footprint/fp_NQZ26_XCME_Time_20260204-20261125_293d16h_bars.csv` (UTC). Tín hiệu: `marks.csv`, `sh.csv` trích từ OrderFlowBubbles bằng C# thật.
- **Tháng kiểm tra: 2026-10-26 00:00 UTC → 2026-11-25** (hết dữ liệu). Máy trạng thái (cấu trúc, range, vùng, mbr) chạy liên tục từ 2026-09-14 để khởi động; chỉ **đếm lệnh** có nến tín hiệu trong tháng kiểm tra.
- Spec này chốt trước. Agent thiết kế chỉ chạy trên 2026-09-14 → 10-23 để lấy 4 con số mô tả (mbr theo phiên, tỷ lệ nến đạt ngưỡng delta, tỷ lệ vùng đạt 7b, thời gian tới lần test đầu). **Chưa chạy một lệnh mô phỏng nào ở bất kỳ đoạn nào.** Của tháng kiểm tra mới chỉ nhìn số nến và volume mỗi ngày để biết dữ liệu có đủ.
- Chạy tháng kiểm tra **một lần**. Không sửa số sau khi xem. Nếu muốn đổi luật thì ghi thành bản spec mới và cần dữ liệu mới để kiểm.
- Trước khi chạy tháng kiểm tra, chạy thử trên 09-14 → 10-23 chỉ để bắt lỗi code (đối chiếu tay 10 lệnh với chart), không để chỉnh số.

### 4.2 Kiểm tra nhìn trước (bắt buộc trước khi tin kết quả)
- `sh.csv`: dấu stop hunt chỉ được biết khi có nến đóng ngược lại (tới 2 nến sau `sweep_time`). Luật 16b đã buộc Close[i] > level tại nến tín hiệu; không dùng dấu sớm hơn. Hai dòng trùng `sweep_time` + `side` tính là một.
- `bt` (Big Trade): ngưỡng "nhóm 8 lệnh lớn nhất mỗi ngày của 5 ngày" phải là **5 ngày trước**, không gồm hôm nay. Nếu gồm hôm nay thì bỏ `bt`, chỉ dùng `dotB`/`dotS`. `marks.csv` chưa có màu cho `bt` → cần xuất thêm Bid/Ask của mức giá đó, hoặc bỏ `bt`.
- `exh`, `zone`, `dot`: chỉ dùng từ lúc nến mang dấu **đóng**. Luật 7b nhánh "nến kế đi tiếp" làm vùng chậm thêm 1 nến.
- Range Box: dùng trạng thái range **tại nến i** (chạy từng nến), không dùng hộp đã vẽ xong về sau.
- Chạy 2 lần: một mạch và từng nến một → danh sách lệnh phải giống hệt.

### 4.3 Mô phỏng
- Vào: market tại Open[i+1]. Trượt giá gộp vào chi phí.
- Từ nến i+1 trở đi (gồm chính nến vào): chạm SL trước TP theo từng nến; **một nến chạm cả SL và TP → tính SL**. Nến mở nhảy qua SL → khớp tại giá mở (xấu hơn SL).
- **Chi phí: 1,0 điểm mỗi lệnh khứ hồi** (phí sàn + môi giới ≈ 0,25 điểm; trượt 1 tick lúc vào market + 2 tick lúc dính SL ≈ 0,75 điểm). Chạy thêm độ nhạy 1,5 điểm. R sau phí = (lãi/lỗ điểm − chi phí) / khoảng SL.
- Cuối phiên: không vào mới sau **16:45 New York**; lệnh còn mở lúc **16:59 New York** đóng tại Close nến đó, tính R theo điểm thật. Không giữ qua giờ nghỉ, không giữ qua cuối tuần.
- Một lệnh mở tại một thời điểm.
- Bỏ lệnh nếu tại Open[i+1] giá đã vượt TP hoặc đã qua SL, hoặc (Fail Break) R:R tới cạnh đối diện < 1,7.

### 4.4 Đối chứng: vào ngẫu nhiên
- Với **mỗi** lệnh thật, bốc 200 lệnh ngẫu nhiên: cùng hướng, cùng khoảng SL và TP (điểm), cùng chi phí, cùng luật cuối phiên; thời điểm vào = giá mở một nến M1 ngẫu nhiên trong **cùng giờ New York (±30 phút)** của một ngày giao dịch bất kỳ trong tháng kiểm tra.
- So: R/lệnh thật với phân phối R/lệnh trung bình của 1.000 bộ ngẫu nhiên cùng cỡ → báo vị trí phần trăm và z. Làm riêng cho từng loại mốc.
- Đối chứng thứ hai (rẻ): cùng luật mốc + cấu trúc nhưng **bỏ tầng D** (luật 15–18) → cho biết tầng xác nhận order flow có thêm gì không.

### 4.5 Thước đo (in cả trước phí và sau phí)
- Số lệnh, lệnh/ngày giao dịch, tỷ lệ thắng, R/lệnh, tổng R, chuỗi thua dài nhất, sụt giảm lớn nhất tính bằng R, khoảng SL trung vị (điểm), thời gian giữ lệnh trung vị, số lệnh đóng cuối phiên.
- Tách theo: loại mốc (Fail Break / Break / Test vùng stacked) · phiên (Á / Âu / Mỹ) · hướng buy/sell · tín hiệu thứ hai (kiệt sức / stop hunt / stacked mới / vùng test) · nhãn mốc lớn (tuần / ngày / không) · có bias hay chưa có bias.
- Cột phụ chốt trước (chỉ để tham khảo, không dùng chọn): TP 4R; không lọc bias; chi phí 1,5 điểm.
- **Cách đọc đã chốt trước:** tháng kiểm tra chỉ ≈ 22 ngày. Dưới 30 lệnh ở một nhóm thì không kết luận gì về nhóm đó. Chỉ nói "có dấu hiệu lợi thế" khi R/lệnh sau phí > 0 **và** vượt phần trăm thứ 95 của đối chứng ngẫu nhiên; còn lại ghi "chưa thấy lợi thế". Một tháng không đủ để gọi là đã kiểm định.
- Ghi chú mật độ: trước 10-26, `exh` chỉ ≈ 27 dấu/ngày (0,02 dấu/nến), thấp hơn mật độ trên chart CORVEN (TT2-C40: 0,10–0,12) → tín hiệu kiệt sức sẽ hiếm; vùng stacked ≈ 99 vùng/ngày, 53% có lần test hợp lệ.

## 5. Gợi ý implement

| Module | Việc | Nguồn dữ liệu / code |
|---|---|---|
| `Structure` | pivot 1 nến mỗi bên, hướng cấu trúc, đỉnh/đáy gần nhất (luật 1–4) | **tự tính** từ OHLC nến đã đóng (C# live + Python) |
| `Range` | hộp range, cạnh, tol, sự kiện `StopHunt` / `CloseOutside` / `FailBreak` / `BreakConfirmed` / `ReEntry` (luật 5, 6, 11, 12) | **dùng lại** `quantower-range/RangeLogic.cs` (link file nguồn, không chép); Python: `quantower-range/research/range_proto.py`, tick = 0,25 |
| `Zones` | vòng đời vùng stacked: chất lượng 7b, sẵn sàng 7c, hết hiệu lực 7d, lần test đầu | sinh vùng: **OrderFlowBubbles** (`zoneB`/`zoneS`); vòng đời: **tự tính** (không dùng luật 20 nến của indicator) |
| `Signals` | bóng (`dotB`/`dotS`/`bt`), kiệt sức (`exhT`/`exhB`) + hiệu lực theo râu, stop hunt | **OrderFlowBubbles**; phần "còn hiệu lực" (luật 16a, 17) và "stop hunt tại cạnh Range Box" (16b) **tự tính** |
| `Delta` | delta nến, `TB\|delta\|20`, cumΔ phiên | **tự tính** từ Bid/Ask volume của nến (cột `delta` trong file `_bars.csv`) |
| `Context` | phiên theo giờ New York, bias (luật 8), VWAP ngày/tuần, POC TPO hôm trước/tuần trước (luật 9) | **tự tính**; có thể mượn `quantower-tpo-suite/ProfileEngine.cs` cho TPO/VWAP |
| `Setup` | ghép tầng A–D thành nến tín hiệu + loại mốc + danh sách tín hiệu | **tự tính**; hàm thuần, vào = trạng thái tại nến i, ra = có/không + lý do |
| `Order` | SL, TP, kiểm R:R, một lệnh mở, đóng cuối phiên (luật 19–23) | **tự tính** |

- Viết **bản Python tham chiếu trước** (đọc `_bars.csv` + `marks.csv` + `sh.csv`), rồi port C#; hai bản phải ra cùng danh sách lệnh trên 09-14 → 10-23 trước khi đụng tháng kiểm tra.
- Indicator live: mọi quyết định ở sự kiện nến đóng; không vẽ lại dấu cũ. Dấu trên chart: mũi tên tại nến tín hiệu + chữ rê chuột ghi loại mốc, 2 tín hiệu, SL, TP (không dùng ký hiệu tự đặt).
- Chú ý múi giờ: file UTC, indicator C# chạy UTC+7 — so theo `bar_idx` hoặc đổi giờ, đừng so chuỗi giờ.
- Test tối thiểu: (1) pivot/cấu trúc trên 5 đoạn nến dựng tay; (2) vùng: sinh → rời → test → hết hiệu lực từng nhánh 7d; (3) cùng nến chạm SL và TP = SL; (4) chạy một mạch = chạy từng nến; (5) ca NQ của CORVEN ngày 06/11 khoảng 20:11 giờ chart (13:11 UTC, khung 0-09-42) — chỉ dùng để kiểm code đọc đúng hộp/bóng/vùng, **không** dùng để chỉnh số (ca này nằm trong tháng kiểm tra).

## 6. Bảng ánh xạ — mọi dòng trong THU-THAP-1 và THU-THAP-2

"L n" = luật số n ở mục 1. "Không dùng" luôn kèm lý do. Dòng không phải lời CORVEN / chart CORVEN vẫn liệt kê để thấy không sót, ghi "không phải nguồn luật".

### 6.1 THU-THAP-1 (văn bản + ảnh chat)

| Mã | Loại | Dùng ở / vì sao không |
|---|---|---|
| A1 | CORVEN | L15 (bắt buộc xem delta, không vào chỉ vì đỉnh thấp hơn) |
| A2 | CORVEN | L6, L11 (range → đánh hai cạnh); "tăng mà delta âm là yếu" → L15 (delta phải cùng hướng) |
| A3 | CORVEN | L6, L12 (Break thì đi theo) |
| A4 | CORVEN | Không dùng: "đầu sóng / cuối sóng / nhịp hồi" không có định nghĩa đo được (TT1-G18) |
| A5 | người học hỏi, CORVEN gật | Không phải nguồn luật; gần nghĩa L12 (sau một balance) |
| A6 | CORVEN | L5 (chỉ cần range, không nhãn Wyckoff) |
| A7 | CORVEN | L1, L5 (tìm cạnh trên M1, vào M1) |
| A8 | CORVEN | L5 (range M1 nhỏ; trần cao 6 × mbr của Range Box). Không có số chuẩn của CORVEN (TT1-G14) |
| A9 | CORVEN | Không dùng: lời kể, không có luật |
| A10 | CORVEN (mảnh) | L2 |
| A11, A12 | chữ slide video | Không làm luật (không đối chiếu được). Gần nghĩa L12, L15 |
| A13 | CORVEN | "để ý momentum" → L15; "không được phép test quá sâu" → L7e; "không cản tàu" → L12, L13 (cùng hướng cấu trúc) |
| A14 | người học nói, CORVEN gật | như A13 |
| A15–A20 | người học / Claude | Không phải nguồn luật (ý tương ứng đã lấy thẳng từ transcript qua TT2) |
| B1 | CORVEN | L9 |
| B2, B3 | CORVEN | L9 (nhãn kịch bản 1 / 2.1 / 2.2); "Follow theo Orderflow" = toàn bộ tầng C–D. "Ngày phải vài chục lệnh": không ép số lệnh, chỉ để so với lệnh/ngày đo được |
| B4, B5 | CORVEN | L9 (VWAP tuần, VWAP ngày, TPO tuần, TPO ngày) |
| B6 | CORVEN | L9 (TPO 30 phút); "Gộp 3 week" = phương án không chọn (mục 2) |
| B7 | CORVEN | Không dùng: "chữ D", "tail ổn" không có số (TT1-G18) |
| B8–B13 | người học | Không phải nguồn luật |
| B14 | CORVEN | L8; "xong vào low tìm entry" → L1 (vào ở M1) |
| B15 | CORVEN + người học | L10: "sáng 8h" là giờ Việt Nam cho vàng, không có giờ cho NQ → không lọc, tách báo cáo theo phiên |
| B16 | CORVEN | L10; R:R 1:5–1:6 = phương án (cột phụ TP 4R) |
| B17 | CORVEN | L9 (bản đồ mốc lớn tính sẵn trước khi tìm lệnh) |
| B18 | CORVEN | Không dùng: nhận định chung |
| B19 | CORVEN | L9 (POC là mốc) |
| B20 | CORVEN | L9 (ghi nhãn mốc lớn cho mỗi lệnh) |
| B21 | chưa rõ người nói | Không dùng |
| B22 | CORVEN (mảnh, mờ) | Không dùng làm luật; cùng ý L9 |
| B23 | chữ slide video | Không làm luật; nhãn "tại mốc lớn" của L9 cho phép xem sau |
| B24 | Claude | Không phải nguồn luật |
| B25 | CORVEN | Không dùng: sách tham khảo |
| B26 | CORVEN | Dùng dữ liệu future (NQZ26), không dùng CFD |
| C1, C2, C3 | CORVEN | Không dùng: phân biệt nhịp nhờ buy limit hay buy market cần sổ lệnh; dữ liệu footprint lịch sử không tách được. Phần "giá tăng mà delta không theo" nằm trong L15 |
| C4, C7 | CORVEN | Không dùng: yêu cầu suy luận tay, không cơ khí hoá |
| C5, C6 | CORVEN | Không dùng: kiến thức nền về loại lệnh |
| C8 | CORVEN | Một phần: L16b coi cú quét SL là dấu hiệu đánh ngược (như Meet). "Chạy mạnh nhưng không đi xa" không làm thành luật |
| C9, C10 | CORVEN | L15 (move thật phải có market cùng hướng = delta cùng dấu). "Dí limit" không đo được |
| C11 | CORVEN | Không dùng: phụ thuộc "đầu sóng / cuối sóng" |
| C12 | CORVEN | Không dùng làm luật riêng; đã tránh bằng L15 (không sell chỉ vì lên volume thấp) |
| C13 | CORVEN | L14 |
| C14 | CORVEN | Không dùng: nhận định |
| C15 | CORVEN | Danh sách công cụ = đúng bộ tín hiệu có sẵn (Big Trade, delta nến, big volume) dùng ở L15, L16 |
| C16 | chart CORVEN | Không thành luật: xác nhận chart có số delta dưới nến và đường dạng VWAP (L15, L9) |
| C17–C20 | chữ slide video / ảnh video | Không làm luật. Ghi nhãn phụ trên lệnh: vị trí bóng trong nến tín hiệu (nửa phía hướng đẩy hay sát cực trị) để xem sau |
| C21 | người học | Không phải nguồn luật |
| C22 | CORVEN theo ghi nhớ, không có ảnh | Không dùng: bộ tín hiệu có sẵn không có dấu hấp thụ riêng |
| C23–C28 | người học / Claude | Không phải nguồn luật |
| C29 | CORVEN (qua trích dẫn, đã đối chiếu transcript) | L16 |
| D1 | CORVEN | L14–L16 (thiếu xác nhận M1 thì không vào, kể cả ở mốc lớn) |
| D2 | CORVEN | L14–L16; "bóp sl lại ngắn" → L20 (có sàn) |
| D3 | chart lệnh người học | Không phải chart CORVEN |
| D4 | CORVEN | Không dùng: nhãn Wyckoff (CORVEN tự nói không cần nhãn, A6). Gần nghĩa L11: không đánh khi chưa có nến đóng lại trong range |
| D5 | CORVEN | L12 (Break là một loại mốc); mâu thuẫn với A2 → mục 2 |
| D6–D8 | người học | Không phải nguồn luật |
| D9, D10 | chữ slide video | Không làm luật (cần DMA, model không rõ) |
| D11 | CORVEN | L19, L22 |
| D12 | người học nói, CORVEN gật | Không dùng: setup này yêu cầu đủ mọi luật |
| D13 | CORVEN | Không dùng: lời khuyên quy trình |
| D14–D16 | Claude | Không phải nguồn luật |
| D17 | (thiếu) | L19: agent chọn market |
| E1 | CORVEN | L20 (sàn 5 điểm vì "ngắn quá bị lỗ phí") |
| E2, E3 | CORVEN | L20 (quy đổi 2–5 giá vàng sang NQ theo biên độ nến) |
| E4 | CORVEN | Không dùng làm luật: ví dụ lệnh 1:6; nêu rủi ro SL ngắn dễ quét → ủng hộ L20 |
| E5 | chart CORVEN | L20 (SL ngay trên đỉnh trước, ≈ 3,5 giá) |
| E6, E7 | CORVEN | Phương án R:R dài (cột phụ) |
| E8 | CORVEN | Phương án 1:4 (cột phụ TP 4R) |
| E9 | CORVEN | Không dùng: khối lượng vào lệnh; backtest đo bằng R |
| E10 | CORVEN | Không dùng: một lần thoát hoà vốn, không thành luật (L23) |
| E11 | CORVEN | L20 (SL xa thì bỏ) |
| E12, E13 | CORVEN | Không dùng làm luật: ví dụ lệnh 1:3 và 1:6,5 |
| E14 | CORVEN | Không dùng làm luật: tỷ lệ thắng 65–70% chỉ là số để so |
| E15–E17 | người học | Không phải nguồn luật |
| E18 | chữ slide video | Không làm luật; trùng L21 (R:R 1:2) |
| E19 | CORVEN (đã đối chiếu transcript) | L21 |
| E20 | CORVEN (đã đối chiếu transcript) + Claude | L20 |
| E21 | Claude / người học | L22, mục 4.3 |
| E22 | (thiếu) | L23 |
| F1 | CORVEN | F-8 |
| F2 | CORVEN | L7e |
| F3 | CORVEN | L14–L16 |
| F4 | CORVEN | L20 |
| F5 | CORVEN | Không dùng (nhãn Wyckoff), xem D4 |
| F6 | CORVEN | mục 2 (phương án chỉ đánh Break) |
| F7 | CORVEN | L14, L15 |
| F8, F9 | CORVEN | Không dùng: xem C1–C3, C8 |
| F10 | CORVEN | L22 |
| F11 | CORVEN | L20 |
| F12 | CORVEN | L8 |
| F13–F17 | chữ slide video | Không làm luật |
| F18, F19, F21 | người học / Claude | Không phải nguồn luật |
| F20 | CORVEN (đã đối chiếu transcript) | L21 |
| F22 | CORVEN | Không dùng: lời khuyên học |
| F23 | (thiếu) | Không có luật tin tức / đứng ngoài cả ngày |
| G1–G19 | ghi chú mâu thuẫn | đã xử lý ở mục 2, mục 3 |

### 6.2 THU-THAP-2 (Meet 07/11 + chart CORVEN)

| Mã | Loại | Dùng ở / vì sao không |
|---|---|---|
| A1 | CORVEN | L5 |
| A2, A3 | CORVEN | L6, L11 |
| A4, A5 | CORVEN | L5 (cạnh theo cụm đỉnh/đáy; gộp range của Range Box) |
| A6 | CORVEN | L5 (M1 dùng range nhỏ) |
| A7, A8 | CORVEN | F-13: range khung 15 chỉ để đánh dài → không dùng cho setup M1 này |
| A9 | CORVEN | Không cơ khí hoá riêng (chỉ có phần gộp range) |
| A10 | CORVEN | L1 |
| A11 | CORVEN xác nhận | L2 |
| A12, A13 | CORVEN | L3 (gãy = nến đóng qua); "thân nến là vùng giá trị" không thành luật riêng |
| A14 | CORVEN xác nhận | L3, L5 |
| A15 | CORVEN | L3, L12 (`BreakConfirmed` = giữ được 3 nến) |
| A16 | CORVEN | L4 |
| A17, A18 | CORVEN | Không dùng: "cấu trúc lớn", "chỗ quan trọng" không có số; setup chỉ dùng cấu trúc M1 gần nhất và cạnh range |
| A19, A20 | CORVEN | L3, L4, F-8 |
| A21 | CORVEN | L11, L12 (Break không dấu hiệu rồi quay vào = vẫn range; Range Box quay lại trạng thái range) |
| A22 | CORVEN | L11 |
| A23 | CORVEN | L6, L12; "về range dưới" không làm đích TP (CORVEN không cho cách chọn range dưới) |
| A24 | CORVEN xác nhận | L12 (yêu cầu vừa Break range vừa cùng hướng cấu trúc) |
| A25 | CORVEN | Không cơ khí hoá riêng ("giảm mạnh" không có số); L15 đòi delta không nhỏ |
| A26 | CORVEN | L11 (Fail Break không đòi cùng hướng cấu trúc) |
| A27 | CORVEN | Không dùng: mô tả một ca |
| A28, A29 | chart CORVEN | L5 (tham số Range Box; hộp NQ 43 điểm nằm trong 1,6–6 × mbr) |
| A30 | chart CORVEN | Không dùng: đường kẻ tay thêm, không có lời giảng |
| B1 | CORVEN | L5, L6 (bối cảnh trước, tín hiệu sau) |
| B2 | CORVEN | L9 (POC chỉ tính khi giá đã rời); cùng nguyên tắc ở L7c |
| B3, B5, B6 | CORVEN | Không dùng: L9 chỉ lấy một POC mỗi kỳ nên không có vùng chồng nhau; B6 có dấu [?] |
| B4 | CORVEN | L9 |
| B7, B8 | CORVEN (có dấu [?]) | Không dùng: máy nghe không chắc |
| B9 | CORVEN | L16 (kiệt sức chỉ tính khi ở mốc) |
| B10 | CORVEN | L7a |
| B11 | CORVEN | Không dùng: giải thích khái niệm |
| B12 | chart CORVEN | L1 (M1), L9 (profile tuần) |
| B13 | chart CORVEN | L9 (VWAP có trên chart NQ của CORVEN; CORVEN không nói gì về nó trong Meet) |
| B14 | chart CORVEN | Không dùng: không có lời giảng |
| C1 | CORVEN | L7a |
| C2, C3, C4 | CORVEN | L7b |
| C5, C6 | CORVEN | L16c (stacked mới sau cú quét = tín hiệu) |
| C7, C9, C11 | CORVEN | L13, L7c |
| C8 | CORVEN (chữ "ngược" do người soát chêm) | mục 2: chọn "phải có phản ứng" |
| C10 | CORVEN | L13, L7d-3 |
| C12 | CORVEN | L13 (ví dụ sell); L7d-1 |
| C13 | CORVEN | L7d-1 |
| C14 | CORVEN | L7d-2 |
| C15 | CORVEN | L7d-3 |
| C16 | CORVEN | L7d-4 |
| C17 | CORVEN | L15, L16, F-2 |
| C18 | CORVEN | L16c (stacked sell mới ngay trên đỉnh sau cú quét) |
| C19 | CORVEN | L7b + L16c (nến rút râu thì chờ có stacked mới) |
| C20 | chart CORVEN | L7d-4 (chỉ lần chạm đầu) |
| C21 | chart CORVEN | Không dùng: số của vàng |
| C22 | chart CORVEN | L7a (hàng 8 tick, 250%, 3 hàng) |
| C23 | chart CORVEN + Claude | L7a lấy phần sinh vùng; **không** lấy "hết hạn 20 nến" (số của dự án) |
| C24 | chart CORVEN | Không dùng: ca của vàng; ghi nhận tín hiệu có thể sót vùng |
| C25–C28 | CORVEN | L16a (đúng định nghĩa `exhT`/`exhB` của OrderFlowBubbles: đỉnh soi Ask, đáy soi Bid, ở râu) |
| C29 | CORVEN | L16a |
| C30 | CORVEN xác nhận | L16a, L17 (vô hiệu khi râu quét qua) |
| C31 | CORVEN | L17 |
| C32 | CORVEN | L11 + L16a |
| C33 | CORVEN | Màu dấu — không ảnh hưởng luật |
| C34 | CORVEN | L13 (đánh đảo chiều phải qua gãy cấu trúc: hướng cấu trúc mới + vùng mới) |
| C35 | CORVEN | L16a ở L11, L12, L13 |
| C36 | CORVEN | L17 + L7d-3 |
| C37–C40 | chart CORVEN | Tín hiệu `exh` có sẵn đã khớp theo các số này; setup không đặt lại ngưỡng. C40 dùng ở ghi chú mật độ mục 4.5 |
| C41 | số đo của dự án | Không dùng (không phải lời hay chart CORVEN) |
| C42 | CORVEN | L15, L16 (bóng chỉ tính khi ở mốc + đúng bối cảnh) |
| C43 | CORVEN | L15 |
| C44 | CORVEN (có dấu [?]) | Không dùng (mục 2) |
| C45 | CORVEN | L15 (nhịp đẩy ngược không có bóng + delta thì không vào) |
| C46 | CORVEN | L16c + L13 (chuỗi đảo chiều) |
| C47, C48 | chart CORVEN | Tín hiệu `dot` có sẵn; setup không phân biệt bóng tím (L16b cho "màu nào cũng tính") |
| C49 | chart CORVEN | Không dùng: chart M5 vàng |
| C50 | người học chốt | Không phải nguồn luật (`bt` chỉ được tính như một bóng ở L15) |
| C51 | chart CORVEN + Claude | L15: `bt` tính như bóng nếu qua kiểm tra nhìn trước (mục 4.2) |
| C52 | chart CORVEN | Tín hiệu `dotB`/`dotS` có sẵn (L15) |
| C53, C54 | chart CORVEN | Không dùng: luật chấm của vàng |
| C55, C56, C57 | CORVEN | L16b (cú quét phải ở mốc quan trọng = cạnh range; "một tí" → L20) |
| C58 | CORVEN | L16b (bóng ở nến quét, màu nào cũng tính, là SL bị quét chứ không phải mua thật) |
| C59, C60 | CORVEN | L11 + L16b |
| C61 | CORVEN | L16b + L15 (stop hunt xong vẫn phải chờ delta + bóng cùng phe); SL → L20 |
| C62 | CORVEN | L16b |
| C63, C64 | CORVEN | L16b (râu thò cạnh range) |
| C65–C67 | chart CORVEN | L16b (dạng ca mẫu); C67 là ca NQ dùng kiểm code (mục 5) |
| C68 | chart CORVEN | L16b (0,75 điểm) |
| C69 | chart CORVEN + Claude | L16b dùng dấu `sh.csv` làm một nhánh; nhánh còn lại dùng cạnh Range Box |
| C70 | số đo của dự án | Không dùng |
| C71–C76 | CORVEN | Không thành luật riêng: lý do vì sao bóng phải đọc trong bối cảnh → L15, L16b |
| C77 | CORVEN | L15 |
| C78, C80, C81, C82 | CORVEN | Không dùng: hấp thụ / phân kỳ nhiều nến không có trong bộ tín hiệu có sẵn, CORVEN không cho số |
| C79 | CORVEN | L8 |
| C83, C84, C86 | CORVEN | L15 (delta không nhỏ). "Thẳng lên" không cơ khí hoá riêng |
| C85 | CORVEN | L11 + L15 (đóng ngược vào range, delta cùng hướng lệnh) |
| C87 | chart CORVEN | L15 (CORVEN xem delta từng nến, to hay nhỏ) |
| C88 | chart CORVEN | Không dùng: phân kỳ vẽ tay |
| D1 | CORVEN | L12 + L15, F-4 |
| D2 | CORVEN | L15, F-5 |
| D3 | CORVEN | L11 + L16c |
| D4 | CORVEN xác nhận | L11, L19 (vào ngay sau nến tín hiệu); phương án chờ ở mục 2 |
| D5 | CORVEN xác nhận | L11, L16 |
| D6 | CORVEN | L18 |
| D7 | chart CORVEN | L18 |
| D8 | CORVEN | L12 + L16a/c |
| D9 | CORVEN | L12, L13 + L16a |
| D10 | CORVEN | L12 + L16a |
| D11 | CORVEN | L13 |
| D12 | CORVEN xác nhận | L13 + L16b (trap đúng vùng, cấu trúc còn giảm) |
| D13 | CORVEN | L14 |
| D14 | CORVEN | L15, L17 (không cơ khí hoá riêng phần "chờ xem hấp thụ") |
| D15 | CORVEN xác nhận | L20: vẫn giữ trần SL 3 × mbr; "phản ứng đẹp thì SL hơi xa cũng vào" không có số → không nới thêm |
| D16 | CORVEN (có dấu [?]) | L16 |
| D17 | CORVEN | L13 (đảo chiều = gãy cấu trúc + L15 + L16) |
| D18 | CORVEN | L21 (R:R tính bằng giá khớp thật) |
| D19 | (CORVEN không nói) | L19 |
| D20 | Claude | Không phải nguồn luật; L19 dựa vào D4, D12, D13 |
| E1 | CORVEN xác nhận | L20 |
| E2 | CORVEN xác nhận | L20 |
| E3 | CORVEN | L20 |
| E4 | người học hỏi, chữ "[được]" do người soát chêm | Không làm luật riêng; trùng L20 |
| E5 | CORVEN | L20 |
| E6, E7, E8 | CORVEN | L21 |
| E9 | CORVEN + chart CORVEN | L21 (đo tới cạnh range đối diện) |
| E10 | CORVEN | Không dùng làm TP (xem A23) |
| E11 | (CORVEN không nói) | L23 |
| F1–F21 | CORVEN | F1→F-2 · F2, F3, F4→F-3 · F5→F-4 · F6, F7, F10→F-5 · F8→không cơ khí hoá (xem A25) · F9→L15, L16b · F11→F-6 · F12, F13→F-10 · F14, F15→F-9 · F16→F-7 · F17→F-1 · F18→F-14 · F19→F-8 · F20→không cơ khí hoá (xem A9) · F21→F-13 |
| G1–G24 | ghi chú mâu thuẫn | G1: ba vai của râu → L3, L16a, L17 · G3→mục 2 · G4→L18 · G5→mục 2 · G7→L21 · G8→L20 · G9→mục 2 · G10→L7d-2 · G11→L7d-4 · G15→mục 3 dòng 19 · G16→L16b (màu nào cũng tính) · G19→L16b có nhánh cạnh Range Box · G21→áp luật dạy trên vàng cho NQ bằng đơn vị hàng/mbr · còn lại (G2, G6, G12–G14, G17, G18, G20, G22–G24): không ảnh hưởng luật |
