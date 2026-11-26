# THU THẬP 1 — Quy tắc giao dịch của CORVEN từ nguồn VĂN BẢN + ẢNH CHAT

> Lập 2026-11-26. Chỉ thu thập, lọc trùng, phân loại, ghi nguồn. Không đề xuất setup, không đo.
> CORVEN = "Trương Linh" trên Messenger (cùng một người).
> Phạm vi: `data-export/messages-with-pro-trader/` (8 file .md + 36 ảnh), `cửu âm chân kinh.md`,
> `plans/CUU-AM-CHAN-KINH-plan.md`, `cuu-am-chan-kinh/chi-tiet.html`, 2 file memory.
> KHÔNG đọc `corven-meet/` (ngoài phạm vi); các ý lấy từ buổi Meet 07/11 chỉ có ở đây qua bản tóm của
> plan / chi-tiet.html, nên xếp loại [Claude] kèm mốc giờ mà plan ghi — cần đối chiếu transcript Meet.

## Quy ước loại nguồn

- **[CV]** = CORVEN nguyên văn (chép đúng chữ, kể cả lỗi gõ). Đã đối chiếu trực tiếp trên ảnh nếu ghi tên ảnh.
- **[CV-video]** = chữ trên slide video CROWCONCEP của CORVEN, chép lại trong `CROWCONCEP_DFT.md` (ảnh gốc không có trong repo, không đối chiếu được).
- **[NH]** = người học diễn giải hoặc chốt (kể cả câu người học thuật lại lời CORVEN mà không có ảnh chat).
- **[NH→CV xác nhận]** = người học nói, CORVEN gật ("Uh", "Đúng r", "Hợp lý đấy chú").
- **[Claude]** = Claude diễn giải / chưng cất trước đây.

Viết tắt file: TR = `TRANSCRIPT.md`, RU = `RULES.md`, 3KB = `TRUONG_LINH_3_KICH_BAN.md`,
TH = `CORVEN_TONG_HOP.md`, BG = `BAI_GIANG_CORVEN.md`, SPEC = `CORVEN_SPEC_V1.md`,
CH = `CAU_HOI_CAN_THONG_NHAT.md`, DFT = `CROWCONCEP_DFT.md`, CA = `cửu âm chân kinh.md`,
PLAN = `plans/CUU-AM-CHAN-KINH-plan.md`, CT = `cuu-am-chan-kinh/chi-tiet.html`. "d." = số dòng.
"1 giá" = 1 USD vàng = 10 tick (TR d.13).

---

## A. Cấu trúc thị trường

| Mã | Nội dung | Loại | Nguồn |
|---|---|---|---|
| A1 | Đỉnh thấp hơn / đáy thấp hơn chưa đủ để vào; phải xem cả delta. "k phải thế đâu" · "đỉnh thấp hơn phải nhìn sang cả delta nữa". Delta ở đây = "bid-ask thôi chú" · "mấy cái khớp lệnh trong fp thôi" | [CV] | IMG_1797, IMG_1798 (Jan 21 23:46–23:48); TR d.93–94 |
| A2 | Trong balance: "Trong balance thì chop" · "Trong balance thì xác định range rồi 2 cạnh mà vả thôi" · "Thì cứ tăng mà delta âm là yếu" | [CV] | TR d.371–373 (§13.6, Messenger Aug 8; ảnh gốc không có trong repo) |
| A3 | Ra khỏi balance thì follow: caption ảnh TPO "Giờ break ra là follow theo" | [CV] | TR d.384 (§13.8, Aug 7 8:04 PM) |
| A4 | Vị trí trong sóng: "Đầu sóng là dự kiến cho move mới" · "Cuối sóng là suy yếu" · "Nhịp hồi là suy yếu" | [CV] | TR d.355–357 (§13.5) |
| A5 | "Đầu sóng" = ngay sau một balance. Người học: "điều kiện là move đấy phải nằm ở ngay sau đấu giá xong à" → "Uh" · "Sau một balance" | [NH→CV xác nhận] | TR d.368–369 |
| A6 | Không cần nhãn Wyckoff: "Mà mẹ k cần nhãn nhiếc đâu" · "Xác định range thôi là đc" · "Rồi nhìn phân tích vol trong range là đc" | [CV] | IMG_1819 (May 5 9:18 AM); TR d.245–247 |
| A7 | Tìm range ngay trên M1: "Tìm biên m1 xong et m1 luôn cũng đc chú" (trả lời câu "Tìm phase ở khung M5, rồi entry M1 à chú") | [CV] | IMG_1817 (Apr 13 4:31 PM); TR d.227 |
| A8 | Range 15 giá trên M1 bị chê to: "Biên của chú to thế=))" · "Mà thôi" · "Vậy cũng đúng" (chart Gold Spot M1 FXCM, hai cạnh ≈ 4786–4798, người học tự nói "Tầm 15 giá") | [CV] | IMG_1817, IMG_1818; TR d.233–234 |
| A9 | Footprint tự đoán được biên tích luỹ / phân phối, không cần học Wyckoff: "không cần học gì chú" · "cái này là hệ số lieu mà" · "nó đoán được cả biên tích biên phối" · "à tuần rồi t cũng ăn khá khá nhờ vụ đoán biên xong allin" · "toàn đúng" | [CV] | IMG_1799 (Jan 21 23:59 – Jan 22 00:00); TR d.96–100 |
| A10 | "đỉnh đáy cấu trúc ấy chú" (2:52 PM Feb 05; câu trước bị mờ, đọc được "chắc là swing low, swing high") — CORVEN nhắc khái niệm đỉnh/đáy cấu trúc, ngữ cảnh đầy đủ không thấy | [CV] (mảnh) | IMG_1801 đầu ảnh; KHÔNG có trong TR |
| A11 | Sideway biên rộng: "Khi giá sideway biên rộng, cần chờ một nhịp phát lực break rõ ràng thì mới follow" (slide vẽ range 2 đường đỏ, giá dập 2–3 lần rồi break cạnh trên đi thẳng) | [CV-video] | DFT d.92–94 |
| A12 | Lực phát đi / momentum: "Đầu tiên chúng ta cần xác định một lực phát đi có thể là tăng hoặc giảm, lực này đủ lớn và tạo ra nến thân to ít râu." · "Một lực phát đi đủ lớn kèm nến thân to, khi này chúng ta sẽ thực hiện follow theo dòng chảy." | [CV-video] | DFT d.37–38 |
| A13 | Follow: "khi follow phải để ý momentum" · "giá không được phép test quá sâu" · "Follow theo Orderflow (không cản tàu)" | [CV] | TH d.18–20; CA d.16–17 |
| A14 | "Không cản tàu" = người học chốt "follow theo footprint, ko cản tàu" → CORVEN "Uh" · "Đúng r" | [NH→CV xác nhận] | 3KB d.36–43 |
| A15 | Nhận biết đang có "tàu" (move): chuỗi nến cùng chiều + delta liên tiếp cùng dấu; không cần delta ngày càng to | [NH] | CH d.65 (B2); SPEC §4 KB-C |
| A16 | Phá range = nến ĐÓNG ngoài cạnh; râu chọc ra rồi đóng lại trong = stop hunt, chưa phá. Phá thật = 1–2 nến sau vẫn đóng ngoài cạnh | [Claude] (tóm Meet 07/11, mốc 0:12:56, 0:13:58, 0:14:42, 0:14:50, 1:04:00, 1:04:25) | PLAN d.47, d.118; CT #b1-range; CA d.20 |
| A17 | Trong range chỉ đánh 2 cạnh; đã phá và giữ 1–2 nến thì chỉ follow hướng phá; không follow giữa lòng range | [Claude] (ghép A2 + A3 + Meet 0:16:29, 0:39:16, 0:40:00) | PLAN d.48; CT #b1-the; CA d.21 |
| A18 | Gãy cấu trúc: chỉ cần 1 nến đóng qua đỉnh/đáy gần nhất; chọc qua rồi rút râu = chưa gãy (fail). Cấu trúc gãy ngược hướng đánh thì bỏ lệnh. Trích trong plan: "đừng nhìn mỗi cái đấy… quan trọng phải phá được cấu trúc" (0:36:21) | [Claude] (tóm Meet 0:42:23, 0:43:09, 0:43:53, 0:40:46) | PLAN d.29, d.49, d.121; CT #b1-cautruc; CA d.22 |
| A19 | Fail break (đóng ngoài rồi đóng lại trong) → tìm tín hiệu ngược; "chờ 1–2 cây xem giữ được trong range không" (0:08:46), "phải vào lòng range" (1:00:02) | [Claude] (tóm Meet) | PLAN d.37, d.120; CT #b2-test |
| A20 | Range rối trên M1 → lên M15 để thấy range; cạnh đặt chỗ giá chạm rồi quay đầu nhiều lần, không đặt ở râu nhọn nhất; 2 range chồng nhau thì gộp | [Claude] (tóm Meet) | CT #b1-range; CA d.20 |

## B. Bối cảnh / vùng

| Mã | Nội dung | Loại | Nguồn |
|---|---|---|---|
| B1 | "Vùng quan trọng của TPO là HVN" · "Khi chạm vào vùng HVN thì giá có thể đảo chiều hoặc Phá vùng" | [CV] | TH d.8–9; CA d.3–4 |
| B2 | 3 kịch bản: "1. Chạm vùng lớn có thể hold dài: Vùng lớn là: + VWAP tuần + TPO tuần" · "2. Đánh scalp · 2.1 Theo VWAP ngày/TPO ngày · 2.2 Follow theo Orderflow (không cản tàu)" | [CV] | TH d.11–20 |
| B3 | Bản chat gốc của B2: "Có 2" · "Một là chạm vùng lớn có thể hold dài" · "2 là scap" · "À có 3 kiểu." · "Scap có 2 kiểu — 1 là đánh vwap" · "2 là đánh follow theo orderflow" · "Ngày phải vài chục lệnh đấy" | [CV] | 3KB d.23–29 (ảnh Messenger 2026-07-31 không có trong repo) |
| B4 | "Vwap tuần" · "Có chơi đc" · "Vwap ngày scap" · "Tpo ngày thì hơi nhỏ nên t nhìn hẳn tuần cho bao quát" | [CV] | 3KB d.33–34 |
| B5 | TPO cho day scalp: "Day scap nhìn tpo daily" | [CV] | TR d.378–380 |
| B6 | TPO vùng lớn: "Gộp 3 week" · "1 preiod vẫn là 30p" | [CV] | TR d.386 (Aug 7 8:46 PM) |
| B7 | TPO chữ D = đang / đã đấu giá xong: người học "Tpo thành chữ D à" → "Chữ D" · "Check tail các thứ xem ổn hết chưa" | [CV] | TR d.310–312 |
| B8 | "Khi đấu giá xong (nhọn, đều 2 cạnh) thì hạn chế trading mà chờ break mới canh vào lệnh" | [NH] (ghi chú cuối file người học; plan d.12 coi là ghi chú người học) | CA d.43 |
| B9 | "Học hiểu khi nào gộp TPO profile 1 hay 3 tuần." — việc còn mở, chưa có luật | [NH] | CA d.44 |
| B10 | VWAP tuần neo từ ĐẦU TUẦN, reset 1 lần/tuần, không rolling | [NH] | CH d.23 (A1); SPEC §2 |
| B11 | TPO tuần chỉ lấy HVN, không dùng POC/VAH/VAL của tuần | [NH] | CH d.28 (A2), d.100 (C3) |
| B12 | Không dùng VAH/VAL/POC từng phiên Á-Âu-Mỹ ("Tất nhiên là không rồi") | [NH] | CH d.106 (C4); SPEC §2 |
| B13 | Lệnh canh vùng tuần có tỉ lệ thắng cao nhất: "lệnh canh tuần sẽ winrate cao hơn 2 cách scap kia"; ~10 lệnh/tuần | [NH] (thuật lại) | CH d.48, d.120–121 |
| B14 | Bias theo phiên: "đưa ra bias thì cần nhiều chú ạ" · "t phải can đo đong đếm giữa buy và sell" · "xem bên nào đang kiểm soát thì theo bên đó" · "bias tang thì chỉ canh mua" · "mua thì mua đến đâu canh sell" · "mỗi phiên sẽ có một bias" · "xong vào low tìm entry thôi" | [CV] | IMG_1802, IMG_1803 (Feb 05 3:02–3:03 PM); TR d.154–160 |
| B15 | Giờ: "sáng entry time là 8h"; người học nói "chiều nó sideway nhiều", "Sáng tầm 7h chạy mạnh", "giờ mỗi phiên nó lại chạy khác nhau" → "đúng chú" | [CV] + [NH→CV xác nhận] | IMG_1803 (3:05 PM); TR d.162–165 |
| B16 | "t chơi RR theo entrytime" · "t biết time nào giá hay chạy mạnh" · "vào được time ngon thì gong có khi 1:5, 1:6" | [CV] | IMG_1795 (Jan 21 23:26–23:27); TR d.92 |
| B17 | Phải có bản đồ vùng trước khi săn lệnh: gửi chart TPO rồi nói "map của t" · "đi săn phải có map" · "không là lạc đường" | [CV] | IMG_1804 (Feb 05 3:05–3:06 PM); KHÔNG có trong TR |
| B18 | "mọi nhịp đa phần dự được hết mà" | [CV] | IMG_1804, IMG_1806 (3:07 PM); KHÔNG có trong TR |
| B19 | Vùng POC là nơi giá phản ứng thật trong ví dụ của CORVEN: chart kèm caption "qua giảm ở poc" | [CV] | IMG_1806, IMG_1807; TR d.177 |
| B20 | Hỏi mốc khung lớn khi review lệnh thua: "Với chú sell ở đâu" · "Mốc time lớn là mốc nào k chú" (người học đáp "M5") | [CV] | IMG_1815 (Feb 9 8:16 PM); TR d.216–217 |
| B21 | Mảnh chữ mờ ở đầu IMG_1808: "time lớn là snr H4, kèm việc đi lên …" (bong bóng bên trái, không rõ người nói — có thể là ảnh chụp chat Messenger với "Lê Đức Huy" chuyển tiếp ở cuối IMG_1806, trong đó có câu "Khung lớn chỗ đó k hợp lưu gì nhỉ") | chưa xác định | IMG_1806 cuối ảnh, IMG_1808 đầu ảnh |
| B22 | Mảnh chữ mờ ở đầu IMG_1819 (trước mốc April 21): "…phản ứng thôi" · "muốn view dài rộng hơn phải có tpo" — bong bóng bên trái (phía CORVEN), không đọc được trọn câu | [CV] (mảnh, đọc mờ) | IMG_1819 đầu ảnh; KHÔNG có trong TR |
| B23 | Mốc lớn chặn follow: "Lưu ý các mốc Vwap D, các vùng quan trọng: nếu giá phản ứng ở đó thì sẽ không follow nữa, mà chờ phát lực để follow theo hướng mốc lớn." | [CV-video] | DFT d.91 |
| B24 | Mốc gần cho nhánh follow: cạnh range / cạnh vừa phá (retest) / stacked imbalance mới tạo / đỉnh-đáy vừa gãy; mốc xa hoặc đã bị chạm nhiều lần → bỏ; không đuổi giá | [Claude] (tóm Meet 0:06:54, 0:17:58–0:18:39, 0:19:38, 0:20:12, 1:05:32) | PLAN d.52, d.122; CT #b2-moc; CA d.25 |
| B25 | Sách nền CORVEN đưa: "Oder Flow vietsub.pdf" — "quyển này là cơ bản nhất"; về 2 quyển (Order Flow Trading Setups + Delta bài 1): "Cơ bản thì cuốn bên trái" · "Chú chỉ cần học cơ bản thôi" · "Học nhiều loạn đấy mà nhiều cái k dung đc" | [CV] | IMG_1798, IMG_1799, IMG_1825; TR d.273–276 |
| B26 | Nền tảng: Sierra Chart, chart future vàng `GCQ26_FUT_CME` 1 Min: "này là SC đấy chú" · "chứ tdv làm gì có data" · "này là chart future của vàng" · "tdv mình xem là chart cfd" | [CV] | IMG_1825 (May 6 11:18–11:19 PM), IMG_1826; TR d.281–282 |

## C. Tín hiệu order flow

| Mã | Nội dung | Loại | Nguồn |
|---|---|---|---|
| C1 | Phải phân tích nhịp tăng nhờ lệnh gì: "một nhịp tang chú phải phân tích xem nó tang nhờ lệnh gì" · "nó đẩy chủ yếu nhờ limit buy kê cao dần lên làm giá tăng" · "khác với buy market chủ động bơm vào" · "trường hợp này thường lạ kiểu kiệt sức trong footprint" | [CV] | IMG_1792, IMG_1793 (Jan 21 23:16); TR d.48–51 |
| C2 | "đoạn nó giảm là kiệt sức buyer" · "đoạn tang đó nó đẩy nhờ buy limit nên không bền" | [CV] | IMG_1792 (23:13); TR d.43–44 |
| C3 | Buy limit bền hay không tuỳ vị trí: "tùy chứ chú" · "buy limit ở đâu" · "buy limit ở chân con song tang( sau một nhịp giảm) thì là ngon" · "còn buy limit mà ở đỉnh là lỏ" | [CV] | IMG_1794 (23:22); TR d.60–64 |
| C4 | Footprint chỉ cho số hợp đồng, phải suy luận loại lệnh: "phải luận nữa" · "fp chỉ toàn hợp đồng thôi" · "chú phải đoán là buylimit hay buy market" · "đoán có cơ sở ấy" | [CV] | IMG_1794 (23:23); TR d.65–68 |
| C5 | Hành vi tổ chức: "cái này là hành vi của tổ chức" · "nên phải đọc còn biết đường chơi" · "big nó thường kê limit ở range để đỡ trượt giá" · "đa phần là thế" · "còn phần nhỏ thì dung iceberg" | [CV] | IMG_1793 (23:21); TR d.54–58 |
| C6 | 2 loại lệnh chính + 8 loại: "lệnh chờ là limit" · "2 loại lệnh chính là chủ động và bị động" · "còn đầy đủ là có 8 loại". Bảng ảnh: Buy Market↔Sell Limit→ASK; Buy Limit↔Sell Market→BID; Buy Stop↔Sell Limit→ASK; Buy Stop Limit↔Sell Market→BID; Sell Market↔Buy Limit→BID; Sell Limit↔Buy Market→ASK; Sell Stop↔Buy Limit→BID; Sell Stop Limit↔Buy Market→ASK | [CV] | IMG_1801 (Feb 05 2:57–2:58 PM); TR d.121–136 |
| C7 | Phải luận ra lệnh gì: "có chứ" · "ăn tiền ở chỗ luận ra được lệnh gì mà" · "để còn biết hành vi chứ" | [CV] | IMG_1801, IMG_1802; TR d.139–141 |
| C8 | Nhịp do quét SL: "di chuyển nhờ quét stoploss nhiều khi k bền" · "nhưng di chuyển nhờ stoploss lại chạy mạnh" · "nhưng k đi được xa" · "vì hành vi khác với chủ đích buy" · "nó có hành vi hết mà" · "đủ công cụ là đọc được" | [CV] | IMG_1802 (2:59–3:00 PM); TR d.142–147 |
| C9 | Limit chặn, market tạo move: "Chú phải hiểu nguyên nhân với hệ quả của các order" · "Ví dụ limit order là chặn đc sóng" · "Move là nhờ market order" · "Market buy > sell thì move tăng lên" · "Limit vẫn làm cho giá tăng đc nhưng nó làm một kĩ thuật khác" · "Dí limit sát theo giá" | [CV] | TR d.334–340 (§13.3) |
| C10 | Giá tăng mà delta âm = dí limit: "Nó dí sát limit đấy" · "Dí sát limit vào giá giữ trend" · "Giá lên nó nâng limit sát vô giá" · "Này chú nhìn order book là rõ luôn" · mục đích: "Tùy mục đích" | [CV] | TR d.344–351 (§13.4) |
| C11 | Ý nghĩa "tăng mà delta âm" theo vị trí: ở đầu sóng → "T bảo chưa phải squeeze vì tăng delta vẫn âm" · "Nó ở đầu sóng" · "Thì dự sau đó sẽ có một nhịp mạnh" · "Thì tối là một nhịp bay mạnh squeeze delta dương"; ở cuối sóng → "Còn hôm nay" · "Tăng delta đang âm" · "Ở cuối sóng" · "Là suy yếu" · "Chỉ cần tối delta k dương mạnh mà seller vào mạnh tạo ra nến giảm là rớt" · "Test lại balance hôm qua" | [CV] | TR d.358–364 (§13.5) |
| C12 | Đi lên không cần volume: "Đi lên k có ai bán thì nó vẫn lên mà chú" | [CV] | IMG_1814, IMG_1815 (Feb 9 8:12 PM); TR d.210 |
| C13 | Muốn sell thì nến giảm phải chất lượng: "Chú xem cây giảm vol có ngon k" · "Đóng có đẹp k" · "Mấy cây giảm đóng râu dưới vẫn rút kìa" | [CV] | IMG_1814, IMG_1815 (8:13–8:14 PM); TR d.212–214 |
| C14 | Footprint hơn volume: "PA với volume thì đi đâu cũng dùng rồi" · "thực ra fp nó trên volume vài bậc" · "volume là bề nổi" · "còn footprint là sâu ở trong" · "nó toàn số lieu chứ không phải tâm linh như mấy pp khác đâu" | [CV] | IMG_1798, IMG_1800; TR d.102–105 |
| C15 | Bộ công cụ trên chart Sierra: "đống chart fp t tích hợp hết vô đây rồi" · "ở kia t tích hợp có big trade bị động( sau khi khớp), big trade chủ động, big delta profile, big delta nến, big volume, với POC của nến" | [CV] | IMG_1824, IMG_1825 (May 6 11:13–11:17 PM); TR d.277–279 |
| C16 | Mô tả chart IMG_1826 (GCQ26_FUT_CME 1 Min, 2026-06-03 khoảng 19:49–22:46): nến có chấm màu trên thân (xanh lá / đỏ / xanh dương / tím) và số delta dưới mỗi nến (vd −75, 79, 96, −51, 38); bóng tròn mờ to: 2 bóng xanh dương chồng ≈ 20:23 quanh 4480–4483, 1 bóng đỏ to ≈ 20:42 quanh 4471 ngay trước nhịp rơi về 4464 rồi giá bật lại; bóng hồng nhạt ≈ 21:09; đường xanh đậm phía trên (≈ 4494 → 4488, dốc xuống) kèm dải tô tím nhạt (4480–4497) — dạng VWAP + dải; đường đen phía dưới (≈ 4468 rồi tụt); panel "Volume … CC Volume Spike Highlight (30, 200…)" có cột vàng ở nến đột biến; panel "Cumulative Delta Bars - Up/Down Tick Volume" dạng nến (Open −557, Close −565) | mô tả ảnh | IMG_1826 |
| C17 | Model "Phe chủ động": "bóng nổ không được ở quá sát high or low. Ví dụ trường hợp buy follow, thì bóng nổ buy không được ở sát high của cây nến." · "Nổ gần high là không được follow theo" · "Bóng phải được nổ ở khoảng giữa giữa or low của cây nến" | [CV-video] | DFT d.64–78 |
| C18 | Model "Hấp thụ": "Đối với model Hấp thụ không cần điều kiện cây hấp thụ big volume." | [CV-video] | DFT d.86 |
| C19 | Sideway biên hẹp cần DMA: "nếu giá có dấu hiệu sideway biên hẹp thì DMA phải > 0 nếu muốn buy và < 0 nếu muốn sell" | [CV-video] | DFT d.45 |
| C20 | Ví dụ chart trong video (2026-07-30): sau đoạn lình xình biên hẹp, nến xanh thân dài delta +374 rồi +271 = "lực phát đi"; sau đó các nến điều chỉnh delta −77, −76, −72 nhưng giá giữ được | mô tả ảnh (Claude chép) | DFT d.40–42 |
| C21 | Tín hiệu vào nhánh follow: trong 1 move có xu hướng không cần VSA/volume; thấy nến có big trade hoặc imbalance / dấu hiệu đẩy lực chủ động là vào. Ví dụ move tăng: bubble big trade ở 30% DƯỚI của nến + delta xanh + thân nến vừa đủ dài đẹp → buy | [NH] | CH d.60 (B1); SPEC §4 KB-C |
| C22 | Ưu tiên absorption hơn exhaustion: "thích xem thằng TO thất bại hơn thằng NHỎ kiệt sức"; footprint xem cả Bid×Ask và Delta ("xem hết"); bảng thống kê để ý Max Delta | [CV] theo memory (2026-06-28, không có ảnh chat đối chiếu) | memory `mentor-corven-orderflow-style.md` |
| C23 | Chỉ báo của CORVEN: Cumulative Delta Bars (delta cộng dồn dạng nến) + DA (đường đen, độ lệch bình quân, đo "lực"/biên độ, không phải delta). Người học đang dùng DMA + Ask/Bid Volume Difference Bars + VSA Volume | [NH] / [Claude] | memory `indicator-setup-corven-vs-hien-tai.md` |
| C24 | Delta là dấu hiệu khi: (a) to, thẳng, cùng chiều lệnh, nhiều nến cùng dấu; hoặc (b) giá và delta vừa đi ngược nhau (nhịp đó yếu, bị hấp thụ → ủng hộ đánh ngược nhịp đó). Nhỏ, lình xình → không tính. Delta âm lớn chưa phải sell ngay, phải xem giá có xuống theo không | [Claude] (tóm Meet 0:31:42, 0:35:42–0:35:55, 0:45:48, 0:46:13) | PLAN d.123; CT #b3-delta; CA d.29 |
| C25 | Bóng: xanh ở đáy nhịp hồi → buy; đỏ ở đỉnh nhịp hồi → sell. Bóng xanh không luôn là người muốn buy (lệnh thoát của phe sell cũng hiện bóng xanh) → "3 hành vi của lệnh chủ động"; bóng xanh ngay trên cạnh trên range thường là SL phe sell bị quét. Bóng tốt nằm ở phần nến phía mình đẩy (buy: nửa dưới) và nến đóng đẹp | [Claude] (tóm Meet 0:46:03–0:46:13, 0:26:48, 0:27:22, 0:24:28) | PLAN d.124; CT #b3-bong; CA d.30 |
| C26 | Kiệt sức: đỉnh xem Ask, đáy xem Bid, lấy số ở râu (đáy Bid ≈ 0 → ủng hộ buy; đỉnh Ask ≈ 0 → ủng hộ sell). Hết hiệu lực khi nến sau quét râu qua mức đó (không cần đóng nến) | [Claude] (tóm Meet 0:10:25, 0:33:14, 0:54:05–0:54:43) | PLAN d.125; CT #b3-kietsuc; CA d.31 |
| C27 | Stacked imbalance: ≥ 3 mức giá liên tiếp một phe áp đảo (CT ghi ngưỡng Ask ≥ 2,5 × Bid chéo — con số của CT, không thấy ghi là lời CORVEN). Tốt khi nằm giữa thân nến và giá đi tiếp; sát râu rồi giá rút ngược → bỏ. Stacked cũ dùng làm mốc thì không tính là dấu hiệu; chỉ stacked mới tạo trong nhịp test mới tính | [Claude] (tóm Meet 0:06:54, 0:17:58–0:18:39) | CT #b3-stacked; PLAN d.59; CA d.32 |
| C28 | Trap / stop hunt: râu quét chỗ nhiều SL (cạnh range, đỉnh/đáy quan trọng) + nổ bóng, rồi đẩy ngược; chờ giá quay về và nến đóng mới dùng. Trích trong plan: "kết hợp với trap" (0:07:38) | [Claude] (tóm Meet 0:23:45–0:24:34, 0:07:38, 0:09:42) | PLAN d.60, d.126; CT #b3-trap; CA d.33 |
| C29 | Không vào theo một dấu hiệu đơn lẻ. Trích trong plan: "kết hợp thêm cả bóng" (0:07:01), "kết hợp thêm range mà đánh" (0:07:47), "chơi những đoạn có nhiều tín hiệu cùng lúc" (1:05:57). Luật chốt "≥ 2 dấu hiệu cùng phe" là của Claude | [CV] theo trích dẫn trong plan (chưa đối chiếu transcript Meet) + [Claude] chốt con số 2 | PLAN d.27–30 |

## D. Điểm vào

| Mã | Nội dung | Loại | Nguồn |
|---|---|---|---|
| D1 | Thiếu xác nhận khung nhỏ thì không vào: "tối qua view được nhưng k entry được" · "k có tín hiệu ấy chú" · "mọi thứ đề chuẩn chỉ rồi" · "thiếu mỗi xác nhận trong m5, m1" | [CV] | IMG_1806 (Feb 05 3:07–3:08 PM); TR d.173–176 |
| D2 | Xác nhận bằng dữ liệu rồi mới vào: (người học: "phá đáy hồi thì entry luôn") → "cũng hay mà chú" · "t hơi cẩn thận" · "t check data xác nhận t mới vào" · "bóp sl lại ngắn" | [CV] | IMG_1808 (3:12 PM); TR d.185–189 |
| D3 | Mô tả chart IMG_1808 (lệnh sell của người học, Thu 05 Feb '26, M1 ≈ 08:15–09:40): giá phá đáy ≈ 09:15, hồi lên ≈ 09:28, vào sell ở nhịp hồi, giá rơi tiếp tới TP | mô tả ảnh | IMG_1808 |
| D4 | Wyckoff: "Đc chú nhưng đừng đánh UT sớm" · "Sang D chú mới đánh thì đc" (chart M5 XAUUSD FXCM của người học: SC ≈ 4500, AR ≈ 4527, ST, UT ≈ 4530, ST, LPS ≈ 4513, range ≈ 4500–4527) | [CV] | IMG_1819, IMG_1820 (May 5 9:16–9:18 AM); TR d.243–244 |
| D5 | (người học: "chú có chơi trong range ko hay toàn break mới chơi") → "Đánh break thôi chú" | [CV] | IMG_1821 (May 5 10:20 AM); TR d.249 |
| D6 | "Đánh break" = giá phá ra khỏi VÙNG giá, chờ hồi về + có tín hiệu rồi đánh (phá-rồi-hồi), không phải phá biên range M1 | [NH] | CH d.87 (C1); SPEC §3; RU dòng W5 |
| D7 | Hai cách đánh tại cùng một vùng HVN: chạm → đảo chiều, hoặc phá → hồi về → đánh tiếp | [NH] (khớp [CV] B1: "có thể đảo chiều hoặc Phá vùng") | CH d.95 (C2); SPEC §3; 3KB d.20 |
| D8 | Cả 3 kịch bản vào lệnh ở M1; chạm vùng tuần vẫn canh M1, chờ nến xác nhận rồi vào | [NH] | CH d.43 (A5); SPEC §1 |
| D9 | Test nông thì follow luôn; test sâu + sideway biên hẹp thì chỉ follow nếu DMA > 0 (buy) / < 0 (sell): "Vì follow trend nên giá không được phép test quá sâu; …" | [CV-video] (cây quyết định là Claude vẽ lại từ ảnh 4) | DFT d.45–54 |
| D10 | "Cách entry sử dụng Model entry: bỏ đi model zone trap và sử dụng các model còn lại để entry, kèm theo một vài điều kiện." (các model nhắc tên: zone trap, phe chủ động, hấp thụ; danh sách đầy đủ chưa biết) | [CV-video] | DFT d.57, d.126–127 |
| D11 | Vào một lần đủ khối lượng, không nhồi: "nay t méo nhồi nữa" · "nhồi hay quét vl" · "vào một phát to mẹ luôn" | [CV] | IMG_1812, IMG_1813 (Feb 05 3:18–3:19 PM); TR d.201 |
| D12 | Checklist: người học "pass tầm 70% checklist thì vào / dần dần tinh chỉnh tiếp" → "Hợp lý đấy chú" · "note ra rồi fix dần" · "t cũng làm thế mà" | [NH→CV xác nhận] | IMG_1796 (Jan 21 23:31–23:32); TR d.76–80 |
| D13 | Quy trình: "Chú phải hiểu hết" · "Xong có signal" · "Rồi theo signal thôi" · "Xong trade nhiều fix signal" · "Lúc trade k bị phân vân với lưỡng lự" · "Rồi fix tâm lý đúng theo rule là đc" · "T chỉ signal sơ sơ thôi" · "Nó còn nhiều rule đấy" | [CV] | TR d.320–329 (§13.2) |
| D14 | Nến xác nhận đã ĐÓNG: thân đủ, đóng sát cực trị, không rút râu dài ngược; sau fail break chờ 1–2 nến giữ trong range (ngoại lệ "xác nhận lần 2": chọc ra lần nữa + thêm dấu hiệu thì vào được dù chưa vào lòng range) | [Claude] (tóm Meet 0:08:46, 0:59:37–1:00:09; khớp [CV] C13 về nến đóng đẹp) | PLAN d.61, d.99; CT #b4-nen, #vi-du-3; CA d.36 |
| D15 | Test không quá sâu (cụ thể hoá): nhịp hồi chưa xuyên vùng stacked, chưa có nến đóng ngược qua cạnh vừa phá | [Claude] (cụ thể hoá câu [CV] A13) | PLAN d.53; CT #b2-test; CA d.26 |
| D16 | Vào ở nhịp hồi về mốc, không đuổi theo nến đang chạy | [Claude] (tóm Meet) | CT #b2-moc, #vi-du-2 |
| D17 | Không thấy nguồn nào trong phạm vi nói CORVEN vào bằng limit hay market | (thiếu) | — |

## E. SL / TP / R:R / quản lý lệnh

| Mã | Nội dung | Loại | Nguồn |
|---|---|---|---|
| E1 | Bóp SL: "Chua tập bóp sl lại" · "Bóp sl thì mới có cơ sở gồng dài" · "Chú tập bóp lại" · "Sl càng ngắn thì tỉ lệ lệnh tp 5-6R càng nhiều" · "Đừng ngắn quá vì ngắn quá bị lỗ phí" | [CV] | IMG_1822, IMG_1823 (May 5 10:23–10:28 AM); TR d.256–261 |
| E2 | Cỡ SL: (người học: "Tầm khoảng mấy giá vậy?") → "Khoảng dưới cây m1 thôi" · "Tập chứ đừng chơi" · "Tập nhìn thôi" · "Từ 2- 4 giá" (= 20–40 tick vàng) | [CV] | IMG_1823 (10:31–10:32 AM); TR d.263–265 |
| E3 | "Sl 5 giá ổn đấy" (nói về lệnh Wyckoff của người học ngày May 5) | [CV] | IMG_1821, IMG_1822 (10:22 AM); TR d.250 |
| E4 | "t sáng nay bóp được phát hơn 3 giá" · (người học: "RR 17 à chú") → "tầm 1 6 đó chú" · "rủi ro cao" · "bù rr cao thôi" · "dễ quét lắm chú" · "nhiều khi vào chưa được 5s đã sl" | [CV] | IMG_1809, IMG_1811 (Feb 05 3:14–3:15 PM); TR d.191 (thiếu câu "5s") |
| E5 | Mô tả chart IMG_1810 (lệnh sell của CORVEN, Thu 05 Feb '26, M1): đỉnh trước ≈ 5021,3 (đường đỏ ngang), 3 đỉnh thấp dần / ngang nối bằng đường xanh từ 06:45–07:45; vào sell ≈ 5017,3 lúc ≈ 07:48, SL ngay trên ≈ 5021 (≈ 3,5 giá), vùng TP tô tới ≈ 4994; giá rơi về ≈ 4954 lúc ≈ 08:15, volume tím/đỏ tăng từ 08:00 | mô tả ảnh | IMG_1810 |
| E6 | Lệnh mẫu: "Stop: 3.55 (0.071%) 355, Amount: 750" · "Open P&L: 72.51, Qty: 70, Risk/Reward Ratio: 60.14" · "Target: 213.48 (4.255%)" → "bóp được như vậy mà gong xem" · "mút chỉ" | [CV] + số trên ảnh | IMG_1811, IMG_1812 (3:18 PM); TR d.197–199 |
| E7 | SL dài: "chú chơi sl dài thì được cái ít quét nhưng khả năng có lệnh RR cao rất thấp" · "chứ lệnh mà chơi, chú tp được 2,3R" · "t có khi được vài chục R rồi" · "nhưng k gong được thôi" | [CV] | IMG_1811, IMG_1812 (3:17–3:18 PM); TR d.192–195 |
| E8 | "đánh RR 1:4 là ngon rồi chú" · "5%, một lệnh win 20% rồi" | [CV] | IMG_1813 (Feb 05 3:20 PM); KHÔNG có trong TR |
| E9 | Rủi ro mỗi lệnh: (người học: "3% vốn à") → "t giờ toàn bụp to thôi" · "5,6%" | [CV] | IMG_1811 (3:16 PM); TR d.167 (chỉ ghi "5,6%") |
| E10 | Lệnh mẫu Jan 21: "Stop: 5.16 (0.106%) 516, Amount: 750" · "Closed P&L: 17.07, Qty: 48, Risk/Reward Ratio: 3.31" · "Target: 17.07 (0.352%)"; sau đó "vừa xong buy ks" · "vào nhưng bị BE" · "tang nhờ limit" (thoát hoà vốn vì nhịp tăng nhờ limit) | [CV] + số trên ảnh | IMG_1796 (23:32–23:33); TR d.82–84 |
| E11 | Không vào khi SL xa: "Đoạn đó t thấy nhưng k chơi được, SL hơi xa nhìn sang eu cũng going vậy nên t đánh eu" | [CV] | IMG_1792 (Jan 21 23:14); TR d.45 |
| E12 | Lệnh buy của CHÍNH CORVEN (Feb 27): "Tuần này tạm được" · "Tối ăn đc lệnh buy này cũng oke"; người học hỏi "Vleu rr 1:10 à chú" → "Không" · "khoảng 1:3 thôi" · "SL nãy hơi xa". Chart: buy ≈ 4547–4560, chốt ≈ 4632–4640 | [CV] | IMG_1816 (Feb 27 11:25–11:28 PM) — TR d.33, d.294 ghi sai là lệnh của người học |
| E13 | Lệnh sell của CHÍNH CORVEN (May 4): gửi chart rồi "1:6.5 đây chú" · "Hôm qua". Chart: sell ≈ 4580, chốt một phần ≈ 4558, giá về ≈ 4516 | [CV] | IMG_1822, IMG_1823 (May 5 10:25–10:26 AM) — TR d.257, d.297 ghi sai là lời / chart của người học |
| E14 | Tỉ lệ thắng: (người học: "winrate 80% luôn à chú") → "khoảng 65-70 đấy chú"; (người học: "rr 13 nữa à chú") → "tùy lúc" | [CV] | IMG_1795 (Jan 21 23:25–23:26); TR d.90–91 |
| E15 | Người học tự nói: bình thường 1:2, vào form đẹp mới dám 1:3, "SL an toàn" vì "nó quét kinh vãi"; May 5: "Cố gắng chơi wyckoff này 1:3 1:4 cho đẹp, bỏ 1:2 thôi", "Hqua t backtest đc quả 1:5" | [NH] | IMG_1808, IMG_1809, IMG_1822; TR d.190 |
| E16 | Hệ của người học (chốt 2026-07-31): R:R cố định 1:3 cho mọi kịch bản, tỉ lệ thắng mục tiêu 40–50%, TP theo R, chỉ trong ngày; bỏ số 80% / 65–70% của CORVEN | [NH] | CH d.72, d.76, d.127–128; SPEC §1 |
| E17 | Nhánh vùng tuần: "những lệnh này chắc ăn dài nên sẽ ưu tiên 1:5, nhưng thôi ta cứ 1:4"; SL "giống hệt nhánh scalp chạm vùng"; chỉ trong ngày, không qua đêm | [NH] | CH d.33, d.38; SPEC §6 |
| E18 | Concept momentum follow: "RR 1:2", "chấp nhận nhiều SL", "tâm lý phải cực kỳ ổn định, không để cảm xúc chi phối"; là "1 trong 2 concept scalping dùng Momentum để follow theo trend" | [CV-video] | DFT d.29–30 |
| E19 | Meet 07/11: tối thiểu 2R, 1,7R chấp nhận, TP vẫn đặt 2R; không đủ thì không chơi kể cả 1R ("không 2R thì không chơi… 1,7R được, TP vẫn 2R" — mốc 0:58:13–0:58:49). Mục tiêu = cạnh đối diện / mốc kế | [CV] theo trích dẫn trong plan (chưa đối chiếu transcript Meet) | PLAN d.35, d.65, d.128; CT #b4-rr; CA d.38 |
| E20 | Meet 07/11: SL sau mốc quan trọng gần nhất (dưới đáy vừa quét / trên đỉnh yếu), không đặt sát; "đặt gần thì dễ bị quét… đặt dưới cái đáy mới quét" (0:50:25); "SL xa quá thì thôi" (0:51:16); xa tới mức không còn 1,7R thì bỏ lệnh, không kéo SL lại gần | [CV] theo trích dẫn trong plan + [Claude] chốt | PLAN d.36, d.64, d.127; CT #b4-sl; CA d.37 |
| E21 | Trong ngày, không nhồi | [Claude] / [NH] (khớp [CV] D11) | CA d.39; CT #b4-ngay |
| E22 | Không thấy nguồn nào trong phạm vi nói về dời SL (về hoà vốn, trailing) hay chốt từng phần; chỉ có: CORVEN từng "bị BE" (E10) và chart E13 có dấu chốt giữa đường | (thiếu) | — |

## F. Điều cấm / bộ lọc

| Mã | Nội dung | Loại | Nguồn |
|---|---|---|---|
| F1 | Không cản tàu (không đánh ngược một move đang có lực) | [CV] | TH d.18; 3KB d.41–43 |
| F2 | Không follow khi giá test quá sâu | [CV] | TH d.20; DFT d.45 |
| F3 | Không vào khi thiếu xác nhận M5/M1 dù vùng và bias đã chuẩn | [CV] | IMG_1806; TR d.175–176 |
| F4 | Không vào khi SL phải đặt xa | [CV] | IMG_1792; TR d.45 (và Meet 0:51:16 theo PLAN d.36) |
| F5 | Không đánh UT sớm; chờ sang phase D | [CV] | IMG_1819; TR d.243–244 |
| F6 | Không chơi trong range (trả lời về Wyckoff May 5): "Đánh break thôi chú" | [CV] | IMG_1821 — xem mâu thuẫn G1 |
| F7 | Không sell chỉ vì giá lên volume thấp; nến giảm râu dưới còn rút thì chưa sell | [CV] | IMG_1814, IMG_1815; TR d.210–214 |
| F8 | Không coi nhịp tăng nhờ buy limit là bền; buy limit ở đỉnh là "lỏ" | [CV] | IMG_1792, IMG_1794 |
| F9 | Nhịp chạy nhờ quét SL: mạnh nhưng không đi xa, không coi là chủ đích | [CV] | IMG_1802 |
| F10 | Không nhồi lệnh | [CV] | IMG_1813 |
| F11 | SL không ngắn quá (lỗ phí) | [CV] | IMG_1823 |
| F12 | Bias tăng thì chỉ canh mua (không đánh ngược bias phiên) | [CV] | IMG_1803 |
| F13 | Giá phản ứng ở VWAP ngày / vùng quan trọng thì không follow nữa, chờ phát lực theo hướng mốc lớn | [CV-video] | DFT d.91 |
| F14 | Sideway biên rộng: chưa có nhịp phát lực break rõ ràng thì không follow | [CV-video] | DFT d.92 |
| F15 | Bỏ model zone trap khi đánh concept momentum follow | [CV-video] | DFT d.57 |
| F16 | Bóng nổ buy sát high của nến (hoặc bóng sell sát low) thì không follow | [CV-video] | DFT d.64–78 |
| F17 | Sideway biên hẹp mà DMA ngược dấu lệnh thì không follow | [CV-video] | DFT d.45 |
| F18 | Đấu giá vừa xong (profile nhọn, đều 2 cạnh) → hạn chế trading, chờ break | [NH] | CA d.41, d.43 |
| F19 | Danh sách "không vào" của Cửu Âm: delta nhỏ, không bóng ("buy không vào") · kiệt sức đang chống hướng đánh (chờ râu quét qua mức đó) · còn ngoài range mà mới 1 dấu hiệu · nhịp đẩy do quét stop · range chồng range, đi lộn xộn | [Claude] (tóm Meet + F9) | CA d.41; PLAN d.68–70; CT #khong-vao |
| F20 | Dưới 2R (ngoại lệ 1,7R) thì không chơi | [CV] theo trích dẫn trong plan | PLAN d.35 |
| F21 | Không follow giữa lòng range; mốc xa / stacked đã bị chạm nhiều lần thì bỏ | [Claude] (tóm Meet) | PLAN d.48, d.52 |
| F22 | "Học nhiều loạn đấy mà nhiều cái k dung đc" — chỉ học cơ bản | [CV] | IMG_1825 |
| F23 | Điều kiện đứng ngoài cả ngày và bộ lọc tin tức: không nguồn nào trong phạm vi nói | (thiếu) | CH d.130–133 (chưa hỏi) |

## G. Mâu thuẫn / chỗ chưa rõ giữa các nguồn

| Mã | Vấn đề | Phía 1 | Phía 2 |
|---|---|---|---|
| G1 | Có đánh trong range không | [CV] May 5: "Đánh break thôi chú" (IMG_1821) trả lời câu "chú có chơi trong range ko hay toàn break mới chơi" | [CV] Aug 8: "Trong balance thì xác định range rồi 2 cạnh mà vả thôi" (TR d.372). Người học chốt "đánh break" = phá vùng rồi hồi (CH d.87) — đây là diễn giải sau, không phải chữ của CORVEN trong ảnh |
| G2 | R:R | [CV] chat: 1:5–1:6 theo giờ vào (IMG_1795), "đánh RR 1:4 là ngon rồi chú" (IMG_1813), lệnh thật 3,31 / ~1:3 / 1:6 / 1:6,5 / 60,14 | [CV-video] concept momentum follow: "RR 1:2" (DFT d.30); Meet 07/11: tối thiểu 2R, 1,7R chấp nhận (PLAN d.35); [NH] hệ riêng: cố định 1:3 (CH d.72), nhánh tuần 1:4 (CH d.33) |
| G3 | Chỗ đặt SL | [CV] chat: "Khoảng dưới cây m1 thôi", "Từ 2- 4 giá", bóp càng ngắn càng tốt (IMG_1823); "Sl 5 giá ổn đấy" (IMG_1821) | Meet 07/11 theo plan: "đặt gần thì dễ bị quét… đặt dưới cái đáy mới quét", SL sau mốc quan trọng, không đặt sát (PLAN d.36). Chính CORVEN cũng nói SL ngắn "dễ quét lắm", "chưa được 5s đã sl" (IMG_1811) |
| G4 | Dùng POC/VAH/VAL hay chỉ HVN | [NH]: chỉ HVN + VWAP, không POC/VAH/VAL (CH d.28, d.100); [CV]: "Vùng quan trọng của TPO là HVN" (TH d.8) | [CV] Feb 05: chart TPO ngày của CORVEN có nhãn VAH/POC/VAL từng ngày, gọi là "map của t", và nói "qua giảm ở poc" (IMG_1804–1807). Khác thời điểm (tháng 2 so với tháng 7–11) |
| G5 | Khung của vùng lớn | [CV] 07-31 và 11-02: "TPO tuần", "nhìn hẳn tuần cho bao quát" (3KB d.34; TH d.15) | [CV] 08-07: "Gộp 3 week" (TR d.386). Người học ghi còn phải "học hiểu khi nào gộp TPO profile 1 hay 3 tuần" (CA d.44) |
| G6 | "Hold dài" nghĩa là gì | [CV]: "chạm vùng lớn có thể hold dài" (TH d.12) — không nói bao lâu | [NH]: chỉ trong ngày, SL như scalp (CH d.33, d.38). Claude từng hiểu là swing nhiều ngày (3KB d.109–112, đã tự nhận sai) |
| G7 | Vị trí bóng trong nến | [CV-video]: bóng "ở khoảng giữa giữa or low", không sát high (DFT d.64–78) | [NH]: "bubble big trade ở 30% DƯỚI của nến" (CH d.60). CT: "nửa dưới nến". Ba mức khác nhau (giữa-hoặc-thấp / 30% dưới / nửa dưới) |
| G8 | Giá tăng mà delta âm | [CV] Jan 21: nhịp tăng nhờ buy limit "không bền", "kiệt sức" (IMG_1792) | [CV] Aug 8: ở đầu sóng sau balance thì là dấu hiệu sắp có nhịp mạnh (TR d.359–361). RU d.22 đã sửa R1 thành có điều kiện |
| G9 | Wyckoff có cần không | [CV] Jan 21: "không cần học gì chú" (IMG_1799) | [CV] Apr–May: vẫn hướng dẫn theo phase ("Sang D chú mới đánh"), rồi lại "k cần nhãn nhiếc đâu" (IMG_1819) |
| G10 | Fail break / UT | [CV] May 5: "đừng đánh UT sớm" | Meet 07/11 theo plan: fail break là chỗ tìm lệnh ngược, cần đóng lại trong range + xác nhận (PLAN d.37) |
| G11 | Tỉ lệ thắng | [CV]: "khoảng 65-70" (IMG_1795); con số 80% là do người học hỏi | CH d.72 / d.127 ghi "80% là số của CORVEN"; SPEC d.32 ghi "WR 80% của CORVEN" — lệch với ảnh |
| G12 | Lỗi ghi người nói trong TRANSCRIPT.md (đối chiếu ảnh) | TR d.33, d.294: IMG_1816 là "lệnh buy của Benzo, CORVEN chấm" | Ảnh: chart và câu "Tối ăn đc lệnh buy này cũng oke" nằm bên trái = của CORVEN; "khoảng 1:3 thôi / SL nãy hơi xa" là CORVEN tự nhận xét lệnh mình |
| G13 | như trên | TR d.257: "Benzo: 1:6.5 đây chú / Hôm qua"; d.258 "Benzo: Chưa tập bóp sl à chú" đứng trước; d.297 "Chart short 1:6.5" xếp vào chart do Benzo gửi | Ảnh IMG_1822–1823: chart và "1:6.5 đây chú" · "Hôm qua" bên trái = của CORVEN, gửi ngay sau "Bóp sl thì mới có cơ sở gồng dài" làm ví dụ |
| G14 | như trên | TR d.235: "CORVEN: Thế thường TR chú bao nhiêu" | Ảnh IMG_1817: bong bóng xanh bên phải "Thế thường TR chú bao nhiêu :))" = người học hỏi CORVEN; câu trả lời không có trong ảnh → KHÔNG biết range chuẩn của CORVEN rộng bao nhiêu (RU dòng W2 suy "TR chuẩn nhỏ hơn nhiều" là thiếu số) |
| G15 | như trên | TR d.21 (bảng ảnh): IMG_1791 = "Chart TPO/Volume-Profile ngày (VAH/POC/VAL), nến + volume — CORVEN gửi" | Ảnh IMG_1791: chart nến nền tối với hộp lệnh buy (vùng xanh TP phía trên, vùng đỏ SL phía dưới), không có TPO, không có volume; giá quét xuyên vùng SL ở cuối rồi bật lên. Không rõ ai gửi |
| G16 | Câu CORVEN có trong ảnh nhưng TRANSCRIPT.md bỏ sót | — | A10 (đỉnh đáy cấu trúc), B17 (map), B18 (dự được nhịp), E8 (RR 1:4 là ngon; 5% một lệnh win 20%), "nhiều khi vào chưa được 5s đã sl", "t giờ toàn bụp to thôi", "bid-ask thôi chú", "nó toàn số lieu…", B22 (muốn view dài rộng hơn phải có tpo) |
| G17 | Vị trí bóng: lời CORVEN vs số đo trong repo | [CV-video] / [NH]: vị trí bóng là điều kiện follow | DFT d.7–12 và BG d.225–226 ghi đã đo: vị trí bóng không mang thông tin, lõi "đuổi momentum sau nến phát lực" âm (−73R/3 tháng, z = −2,39) — ghi để biết, đây là số đo cũ của repo, không phải lời CORVEN |
| G18 | Ngưỡng chưa có số (CORVEN chưa nói) | "test quá sâu" = bao nhiêu %; "sát high" = bao nhiêu %; "nến thân to" = bao nhiêu; DMA chu kỳ nào; "đầu sóng" kéo dài mấy nến; "cuối sóng" nhận bằng gì; tail thế nào là "ổn"; 3 tuần rolling hay lịch; danh sách đầy đủ Model entry; "zone trap" là gì | DFT d.126–132; BG d.311–316 |
| G19 | Sản phẩm | Toàn bộ nguồn văn bản + ảnh trong phạm vi nói về VÀNG (GC future, XAUUSD), con số "giá" = USD vàng | Không câu nào của CORVEN trong phạm vi này nói riêng về NQ; chỉ CT có 2 ảnh ví dụ NQ M1 ngày 06/11 lấy từ buổi Meet (#b2-test, #b3-trap) |

---

## Danh sách đã đọc

### File văn bản (đọc trọn)
1. `data-export/messages-with-pro-trader/CORVEN_TONG_HOP.md` (21 dòng)
2. `data-export/messages-with-pro-trader/TRANSCRIPT.md` (402 dòng)
3. `data-export/messages-with-pro-trader/RULES.md` (54 dòng)
4. `data-export/messages-with-pro-trader/TRUONG_LINH_3_KICH_BAN.md` (158 dòng)
5. `data-export/messages-with-pro-trader/BAI_GIANG_CORVEN.md` (316 dòng)
6. `data-export/messages-with-pro-trader/CORVEN_SPEC_V1.md` (142 dòng)
7. `data-export/messages-with-pro-trader/CAU_HOI_CAN_THONG_NHAT.md` (151 dòng)
8. `data-export/messages-with-pro-trader/CROWCONCEP_DFT.md` (132 dòng)
9. `cửu âm chân kinh.md` (46 dòng)
10. `plans/CUU-AM-CHAN-KINH-plan.md` (167 dòng)
11. `cuu-am-chan-kinh/chi-tiet.html` (đọc phần chữ sau khi bỏ thẻ; KHÔNG mở 18 ảnh trong `cuu-am-chan-kinh/img/`)
12. memory `mentor-corven-orderflow-style.md`
13. memory `indicator-setup-corven-vs-hien-tai.md`

### 36 ảnh chat (đã mở từng ảnh)
| Ảnh | Nội dung | Có nội dung giao dịch? |
|---|---|---|
| IMG_1791 | Chart nến + hộp lệnh buy, không chữ | Có (chart), không rõ người gửi — G15 |
| IMG_1792 | Jan 21 23:13–23:16: kiệt sức buyer, buy limit / buy market, SL xa | Có |
| IMG_1793 | 23:16–23:22: hành vi tổ chức, kê limit ở range, iceberg | Có |
| IMG_1794 | 23:22–23:23: buy limit ở chân sóng / ở đỉnh, phải đoán có cơ sở | Có |
| IMG_1795 | 23:25–23:27: tỉ lệ thắng 65–70, RR theo giờ vào, 1:5 1:6 | Có |
| IMG_1796 | 23:31–23:33: checklist 70%, lệnh RR 3,31, "bị BE / tang nhờ limit" | Có |
| IMG_1797 | 23:43–23:46: chart lệnh của người học; "đỉnh thấp hơn phải nhìn sang cả delta nữa" | Có |
| IMG_1798 | 23:46–23:51: delta = bid-ask, fp là số liệu, sách | Có (ít) |
| IMG_1799 | 23:53 – Jan 22 00:01: sách cơ bản, không cần Wyckoff, đoán biên | Có (ít) |
| IMG_1800 | Jan 22 00:01–00:02 + Jan 29: fp trên volume vài bậc; chuyện kinh nghiệm 5 năm | Có (ít) |
| IMG_1801 | Feb 05 2:52–2:59 PM: "đỉnh đáy cấu trúc", 8 loại lệnh | Có |
| IMG_1802 | 2:58–3:03 PM: quét SL, bias | Có |
| IMG_1803 | 3:00–3:05 PM: bias mỗi phiên, vào low tìm entry, entry time 8h | Có |
| IMG_1804 | 3:05–3:07 PM: chart TPO "map của t", "đi săn phải có map" | Có |
| IMG_1805 | Chart TPO ngày XAU (VAH/POC/VAL từng ngày, đường ngang đỏ ≈ 5020 và ≈ 5115, xanh 4823,24, giá 4915,59, volume màu) | Có (chart) |
| IMG_1806 | 3:07–3:09 PM: thiếu xác nhận m5 m1, "qua giảm ở poc"; cuối ảnh là ảnh chụp chat Messenger khác | Có |
| IMG_1807 | Chart TPO phóng to: giá giảm từ POC (hộp đỏ), volume tím/đỏ đột biến | Có (chart) |
| IMG_1808 | 3:10–3:13 PM: lệnh sell của người học, "t check data xác nhận t mới vào" | Có |
| IMG_1809 | 3:12–3:15 PM: bóp hơn 3 giá, RR tầm 1:6 | Có |
| IMG_1810 | Chart lệnh sell của CORVEN 05 Feb (xem E5) | Có (chart) |
| IMG_1811 | 3:15–3:18 PM: 5,6% vốn, SL dài ít lệnh RR cao, chart RR 60,14 | Có |
| IMG_1812 | 3:16–3:19 PM: lặp IMG_1811 + "bóp được như vậy mà gong xem", không nhồi | Có |
| IMG_1813 | 3:18–3:20 PM: "vào một phát to", "đánh RR 1:4 là ngon rồi chú" | Có |
| IMG_1814 | Feb 9 8:06–8:14 PM: lệnh sell thua của người học, nhận xét nến giảm | Có |
| IMG_1815 | 8:07–8:17 PM: lặp + "Với chú sell ở đâu", "Mốc time lớn" | Có |
| IMG_1816 | Feb 27 11:25–11:28 PM: lệnh buy của CORVEN, "khoảng 1:3 thôi, SL nãy hơi xa" | Có |
| IMG_1817 | Apr 13: Wyckoff, "Tìm biên m1 xong et m1 luôn", "Biên của chú to thế" | Có |
| IMG_1818 | Chart Wyckoff phân phối M1 Gold Spot của người học (BCLX/ST/AR/UT/mSOW/UTAD/Test/LPSY/SOW) | Có (chart người học) |
| IMG_1819 | May 5 8:05–9:27 AM: "đừng đánh UT sớm", "Sang D", "k cần nhãn" | Có |
| IMG_1820 | Chart Wyckoff tích luỹ M5 XAUUSD của người học | Có (chart người học) |
| IMG_1821 | 9:27–10:23 AM: "Đánh break thôi chú", "Sl 5 giá ổn đấy" | Có |
| IMG_1822 | 10:22–10:26 AM: "Bóp sl thì mới có cơ sở gồng dài", chart sell của CORVEN | Có |
| IMG_1823 | 10:26–10:47 AM: "1:6.5 đây chú", 5–6R, dưới cây m1, 2–4 giá | Có |
| IMG_1824 | May 6 11:04–11:17 PM: 2 quyển sách, chart Sierra, danh sách công cụ | Có |
| IMG_1825 | 11:13–11:19 PM: lặp + Sierra Chart, chart future vs cfd | Có (công cụ) |
| IMG_1826 | Chart Sierra GCQ26_FUT_CME 1 Min 2026-06-03 (xem C16) | Có (chart) |

Ảnh hoàn toàn không có nội dung giao dịch: **không có**. Ảnh chỉ có chart, không có chữ chat: IMG_1791, 1805, 1807, 1810, 1818, 1820, 1826.

### Nguồn KHÔNG có trong repo nên không đối chiếu được
- 3 ảnh Messenger 2026-07-31 (3 kịch bản) — chỉ còn bản chép trong 3KB.
- 7 ảnh Messenger Aug 7–8 + ảnh TPO 3 tuần (§13) — chỉ còn bản chép trong TR.
- 7 ảnh video CROWCONCEP — chỉ còn bản chép trong DFT.
- Tin nhắn 2026-06-28 (absorption vs exhaustion) — chỉ còn trong memory.
- Câu trả lời của người học ở CH là người học thuật lại, không có ảnh chat của CORVEN đi kèm.
