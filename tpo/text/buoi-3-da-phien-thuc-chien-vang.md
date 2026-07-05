# Phụ lục TPO — Buổi 3/3: Bản đồ đa phiên + thực chiến vàng + khởi động thực hành

> ⏱ ~75-90' · Buổi cuối của phụ lục TPO: buổi 1 đọc MỘT profile, buổi 2 đọc cấu trúc ngày — buổi này ghép NHIỀU phiên thành bản đồ, mổ 2 ca vàng thật (GCQ23) và chốt bộ khung để bắt đầu backtest trên ATAS.

## 🎯 Mục tiêu buổi

- Sau buổi này bạn chia được một ngày giao dịch thành các phân đoạn có "tính cách" riêng, biết settlement là mốc neo và đọc được phiên overnight so với nó (gap lấp hay không lấp nói lên điều gì).
- Đọc được QUAN HỆ giữa các phiên: VA nâng dần / hạ dần / chồng nhau / thu hẹp, và tìm POC clustering — mức đặt lệnh chờ chất lượng cao.
- Hiểu vì sao TPO-POC và VPOC trên ATAS không luôn trùng nhau.
- Đọc được 2 ca thực chiến vàng trong note: break range 2 lần + retest vùng supply bị hấp thụ, và buyer chủ động + delta âm không đè được giá.
- Có trong tay bộ khung thực hành: công thức sizing 2%, scaling out 3 mục tiêu, nguyên tắc đặt SL theo cấu trúc, nguyên tắc hợp lưu, mẫu nhật ký backtest và checklist trước phiên.

---

## 1️⃣ Phiên & overnight — bản đồ thời gian của một ngày (~15')

### 1.1 Năm phân đoạn của phiên Mỹ

Hoạt động thị trường đi theo thói quen hằng ngày của trader chuyên nghiệp — volume và độ sôi động dao động theo "lịch sinh hoạt" của họ. Keppler chia phiên Mỹ của ES thành 5 phân đoạn, mỗi phân đoạn một tính cách:

1. **Giờ đầu tiên** — sôi động, dò hướng ngày.
2. **Phiên sáng** — nếu giờ đầu đã chọn hướng thì sáng đẩy tiếp; chưa chọn thì bó hẹp trong range.
3. **Phiên trưa** — nghỉ, volume tụt; *nhưng* thời đại thuật toán, thi thoảng move lớn khởi động đúng lúc ít ai ngờ nhất — đừng bỏ màn hình hoàn toàn.
4. **Phiên chiều** — hay bất ngờ: có thể đảo ngược xóa sạch lãi buổi sáng, có thể tiếp diễn, có thể đi ngang chờ tin.
5. **Settlement** — 15' chốt ngày: day trader buộc phải tất toán, trader khung dài quyết giữ hay đóng → biến động và volume dồn về 10' cuối; giá settlement là "giá đóng cửa chính thức" của ngày.

Số phân đoạn thay đổi theo từng thị trường — trước khi phân đoạn cho vàng phải quan sát nhịp riêng của vàng, không bê nguyên lịch ES sang.

**📊 Đọc chart thật** — [tpo/images/keppler/p084-0.png](tpo/images/keppler/p084-0.png): profile ngày của ES được tách thành các cột chữ cái A→N (kỹ thuật **Split Profile** — tách profile ngày thành từng cột 30'/từng phân đoạn để so sánh từng nhịp đấu giá), đóng khung theo 5 phân đoạn: First Hour 9:30–10:30 (A,B), Morning 10:30–12:00 (C,D,E), Lunch 12:00–14:00 (F,G,H,I), Afternoon 14:00–16:00 (J,K,L,M), Settlement 16:00–16:15 (N). Trên chart này cột N in dấu `N*` sát đỉnh ngày quanh 1363.50, trong khi POC ngày nằm 1359.50 (panel trái) — ngày đóng cửa mạnh, trên vùng giá trị.

### 1.2 Overnight session — đọc bằng mốc settlement

Thị trường là dòng vốn 24h: hết phiên Mỹ không có nghĩa hết thông tin. Cách đọc phiên đêm của Keppler: lấy **vùng settlement hôm trước làm mốc chuẩn**, rồi xem phiên đêm phát triển ở đâu so với mốc đó.

**📊 Đọc chart thật** — [tpo/images/keppler/p088-0.png](tpo/images/keppler/p088-0.png): ngày hôm trước settlement gần đỉnh ngày (vòng tròn "Bullish Settlement Almost at Day's High" quanh cụm 1345–1348.5; theo sách khung này mở 1346, đóng 1347.75). Phiên đêm (cột chữ thường bên phải) mở NGAY DƯỚI giá đóng settlement, lượn xuống tìm hỗ trợ ở đáy phiên chiều, tạo phân phối kép, rồi đến sáng leo về lại đúng đỉnh vùng settlement — tức cả đêm chỉ đưa giá về điểm xuất phát → thiếu niềm tin vào đà tăng hôm trước. Sáng hôm sau chu kỳ A chỉ nhích được ~2 tick trên đỉnh settlement rồi quay đầu — xác nhận sự đuối sức đó.

**Logic gap fill:** nếu phiên đêm đóng TRÊN vùng settlement → mở cửa có gap.
- Không lấp gap + tiếp tục đi lên = phe mua tự tin thật.
- Rơi xuống lấp gap = thị trường yếu hơn vẻ ngoài.

Chú ý: "đuối sức" chưa chắc là đảo chiều — chỉ là đà hiện tại hụt hơi; thị trường có thể tích lũy lấy sức đi tiếp, hoặc yếu dần rồi bán tháo. Đừng nhảy từ "yếu" sang "short" khi chưa có cấu trúc.

### 1.3 Hai mẫu volume qua đêm: Big Smile / Frown

- **Big Smile (cười):** đêm trôi ngang-nhích nhẹ với volume mỏng → mở phiên mới volume nổ đột biến → move TĂNG theo sau. Vòng cung võng xuống như miệng cười.
- **Frown (cau mày):** ngược lại — vòng cung úp, volume xuất hiện là mở màn cho move GIẢM.

⚠️ **Caveat quan trọng (chính Keppler nhấn):** lúc volume đổ vào, biến động tăng và giá **có thể giật NGƯỢC hướng với xu hướng thật sắp tới** trước; phải kiên nhẫn chờ biến động lắng xuống thì hướng đi mới lộ rõ. Tức là: cú nổ volume ở mở cửa là *tín hiệu chuẩn bị*, không phải lệnh nhảy vào ngay.

**📊 Đọc chart thật** — [tpo/images/keppler/p127-0.png](tpo/images/keppler/p127-0.png): chuỗi profile 30' của ES võng thành vòng cung suốt đêm; vòng tròn "Increased Volume" quanh 23:30–00:30 ở vùng ~1135–1140, sau đó giá bốc lên vùng ~1145 (ô giá hiện tại bên phải ~1144.5). Ảnh ngược lại — [tpo/images/keppler/p128-0.png](tpo/images/keppler/p128-0.png): vòng cung úp, KVT khoanh volume tăng lúc 06:30–07:30 — vòng tròn phủ dải **~1115–1135**, đỉnh cụm profile được khoanh chạm ~1133–1134 — rồi mũi tên xuống tận vùng 1100–1105.

### 🥇 Áp cho vàng MGC

- **Quy giờ VN (mùa hè):** phiên **Á 07:00–14:00**, **Âu 14:00–19:20**, **Mỹ** chạy tới ~02:00 VN — mốc mở có 2 cách tính: **19:20 VN** (COMEX floor 8:20 ET) hoặc **20:30 VN** (chứng khoán Mỹ mở 9:30 ET). Globex mở lại 18:00 ET = **05:00 VN**.
- Vàng là hàng 23h/ngày nên "overnight" của vàng thực chất là phiên Á+Âu — và theo note thực chiến: **phiên Á build range cho Âu, Âu build range cho CME** **[GT-2]**. Kèm theo: VA nằm gọn trong IB phiên Âu với biên độ thấp → phiên Mỹ dễ có trend **[GT-4]**.
- Khung settlement của vàng rơi vào quãng sau nửa đêm giờ VN (~00:30 mùa hè) — *đây là tổng hợp riêng của Claude, không có trong 3 nguồn; tự xác nhận mốc chính xác trên ATAS*.
- IB = A+B 60′, mốc bắt đầu 19:20/20:30 theo quy ước đã chốt ở buổi 1 (→ **GT-8**).

*— Keppler tr.84-89, 127-128; note tr.5, 13*

---

## 2️⃣ Value migration đa phiên — đọc QUAN HỆ giữa các phiên (~20')

Một profile đơn lẻ trả lời "hôm nay đấu giá thế nào". Nhiều profile đặt cạnh nhau trả lời câu quan trọng hơn: **giá trị đang di cư về đâu?** Đây là "kịch bản nền" trước khi vào bất kỳ lệnh nào.

### 2.1 Bốn quan hệ giữa VA phiên sau và phiên trước

| Quan hệ | Đấu giá đang nói gì |
|---|---|
| **VA nâng dần** (đáy VA phiên sau nằm từ nửa trên range phiên trước trở lên, và đóng cửa trên VAH phiên trước) | Người mua chấp nhận giá trị cao hơn → thuận xu hướng tăng |
| **VA hạ dần** | Người bán kéo nhận thức giá trị xuống → thuận xu hướng giảm |
| **VA chồng lên nhau** (đặc biệt khi đáy VA mới rơi đúng POC phiên trước) | Đà yếu đi, có chốt lời; thị trường quay về "kiểm định" giá trị cũ |
| **VA thu hẹp** | Biên độ đồng thuận co lại — dấu hiệu đà không còn khỏe như các phiên trước, và range hẹp thì dễ break ở phiên sau |

Chuỗi điển hình trong Keppler (EURUSD): VA nâng dần A→B→C, nhưng VA của C **thu hẹp** hẳn → cảnh báo; sang D đỉnh VA vẫn cao hơn nhưng thân VA **chồng xuống** phiên trước, đáy VA của D rơi đúng POC phiên trước → hôm sau giá giảm xác nhận — cơ hội bán xuất hiện đúng lúc "giá trị cao hơn bị từ chối".

**📊 Đọc chart thật** — [tpo/images/keppler/p093-0.png](tpo/images/keppler/p093-0.png): 5 profile ngày liên tiếp của ES (trục giá 1324.25–1371.25). Nhìn các thanh VA đậm: ngày 1 quanh ~1358–1364, ngày 2 tụt xuống ~1350–1355, ngày 3 ~1341–1347, ngày 4 ~1332–1341 — bốn ngày VA hạ dần bậc thang; ngày 5 VA bật lên chồng ngược vào vùng ngày 3–4. Chỉ cần liếc quan hệ các VA là thấy câu chuyện tuần: xu hướng giảm có trật tự, rồi phiên cuối người mua quay lại.

### 2.2 POC clustering — mức đặt lệnh chờ chất lượng cao

POC là giá được thị trường "đồng ý" nhiều nhất trong một phiên. Khi POC của **nhiều phiên tụ gần nhau**, đó là sự chấp nhận giá được xác nhận lặp lại → mức tham chiếu rất mạnh, giá rời xa rồi quay về thường phản ứng ở đó.

**📊 Đọc chart thật** — [tpo/images/keppler/p153-0.png](tpo/images/keppler/p153-0.png): 10 phiên EURUSD, các phiên đánh chữ A→J. Ellipse lớn "Area of Price Acceptance" khoanh dải quanh ~1.408–1.411: POC của A, G, H nằm sát nhau (sách ghi POC của H và I chỉ cách nhau vài pip). Cũng trên ảnh này đọc luôn **hình dạng**: A và J dài-hẹp = phiên trend; B, G, I ngắn, TPO túm quanh POC = phiên balance — đúng logic hình dạng D/P/b/thin bạn đã học ở Volume Profile, giờ nhìn bằng TPO.

Note thực chiến bổ sung 2 ý cùng hướng: **POC trùng hoặc gần S/R thì rất hay được test**; và kinh nghiệm TraderViet: **POC cũ một khi bị breakout thường thành cản mới rất tốt** **[GT-5]**.

### 2.3 Composite tuần/tháng và các "núm"

Gộp 5 profile ngày → **profile tuần**; gộp 20 ngày → **profile tháng**. Composite có đủ VAH/VAL/POC riêng, và làm lộ ra các **knob (núm)** — mức giá có số TPO vượt trội, thường thành S/R khi giá quay lại. Núm càng lên khung lớn càng rõ: núm của tuần thường chính là núm của tháng, chỉ đậm nét hơn.

**📊 Đọc chart thật:**
- [tpo/images/keppler/p095-0.png](tpo/images/keppler/p095-0.png) — composite tuần của ES, POC tuần **1342.25** (header, kèm phân bổ TPO 635/486 trên/dưới). Bốn mũi tên đánh số khoanh 4 núm: quanh ~1355.5, ~1353 (có cặp đường gióng 1352.75/1353.25), ~1347.5 và ~1337.5; dưới cùng thêm hai đường 1334.75 và 1333.00. Đây chính là bộ level kẻ sẵn cho tuần sau.
- [tpo/images/keppler/p097-0.png](tpo/images/keppler/p097-0.png) — composite tháng (trục 1325.50–1367.50): POC tháng **1343.00** (TPO 981/749), đường gióng trên 1356.50/1355.00, dưới 1335.25/1335.00. So với composite tuần ở trên: POC tuần 1342.25 và POC tháng 1343.00 gần như dính nhau — POC clustering liên khung thời gian.
- [tpo/images/keppler/p098-0.png](tpo/images/keppler/p098-0.png) — hai profile 20 ngày cạnh nhau: tháng trước POC **1328.25**, VAH 1335.75, VAL 1295.25 (panel trái); tháng hiện tại VAL rơi xuống đúng vùng POC tháng trước (đường gióng ~1329.00). Sách: nếu thủng ~1329 thì hỗ trợ kế tiếp là núm dưới của profile trước quanh **1310.50**; số TPO tại POC hai tháng gần bằng nhau (~39 vs ~44) nhưng CẤU TRÚC khác — tháng trước POC nép sát VAH, tháng này POC giữa range (POC nép sát VAH = người mua chấp nhận trả vùng giá cao, lực đẩy sẵn; POC giữa range = hai phe còn giằng co đúng giữa, chưa phe nào thắng để làm bàn đạp trend) → thị trường cần "phát triển cân bằng" thêm trước khi có chân tăng mới. Mức lớn của composite cũ **không hết hạn** khi sang tháng mới.

### 2.4 Cùng kỹ thuật, thu nhỏ vào trong phiên: value tracking 30'

Kỹ thuật so VA giữa các NGÀY dùng được y nguyên cho các cột 30' TRONG ngày (mỗi cột 30' chia 6 đoạn 5'): VA từng cột nâng/hạ/chồng/thu hẹp cho thấy giá trị di cư theo thời gian thực.

**📊 Đọc chart thật** — [tpo/images/keppler/p115-0.png](tpo/images/keppler/p115-0.png): các cột A→N của ES ngày 20/5. Đọc chuỗi: A đổ xuống, B–C tiếp tục hạ (C đóng sát đáy), D–E quay đầu nâng giá trị, F mở màn bằng cú test đáy VA của D — **giữ được** → F,G,H,I nâng tiếp; sang J đáy trước **vỡ** → K,L,M,N hạ giá trị dần về cuối ngày. Chi tiết đắt nhất: đáy VA của cột N tại **1328.75** (ô gióng bên phải) trùng đúng vùng đáy VA của cột C — mức cũ trong ngày quay lại hoạt động ngay trong chính ngày đó.

### 2.5 TPO-POC vs VPOC trên ATAS — lệch nhau là thông tin

Hai POC trả lời hai câu khác nhau:
- **TPO-POC**: giá nào được Ở LÂU nhất (thời gian).
- **VPOC**: giá nào TRAO TAY nhiều hợp đồng nhất (khối lượng — cái bạn vẫn dùng ở Volume Profile).

Trùng nhau = thời gian và tiền đồng thuận, mức rất chắc. **Lệch nhau = có chỗ giá ở lâu nhưng ít tiền, và có chỗ tiền dồn vào nhanh mà giá không ở lại** — phải hỏi tiếp "khối lượng đó là ai, mua hay bán?", và manh mối là vị trí đóng cửa.

**📊 Đọc chart thật** — [tpo/images/keppler/p104-0.png](tpo/images/keppler/p104-0.png): ngày 2/5 của ES. Panel trái ghi TPO-POC **1359.50**, nhưng đường VPOC gióng tại **1358.00** kèm cặp số **1.098.142 hợp đồng trên VPOC vs 311.091 dưới VPOC** — mất cân bằng nặng về phía trên. Giá đóng **1357.75** sát đáy range → khối lượng khổng lồ phía trên VPOC đó phải là khối lượng BÁN (mua mà đóng đáy thì vô lý theo cơ chế đấu giá). Diễn tiến sau đó sách ghi: hôm sau mở 1354.75 dưới VAL volume cũ, các chu kỳ A, B, E, F cố ngoi lên lại **1357.25** (VAL cũ) đều thất bại → VAL cũ thành kháng cự → rơi tiếp về 1345.75; và ngày 3/5 tỷ lệ trên/dưới VPOC còn 727.387 vs 622.740 — áp lực bán đã cân bằng lại.

### 🥇 Áp cho vàng MGC

- Trước phiên Mỹ (trước 19:20 VN) kẻ VA của **3 phiên gần nhất** (Á/Âu hôm nay + Mỹ hôm qua, hoặc 3 ngày gần nhất) và trả lời 1 câu: giá trị đang **nâng / hạ / chồng / thu hẹp**? Đó là kịch bản nền.
- Tìm **POC tụ chùm**: các POC cách nhau ≤ 5–10 tick MGC (0.5–1.0 điểm giá) → gộp thành 1 level đặt lệnh chờ, ưu tiên level trùng thêm núm của composite tuần.
- Trên ATAS: bật đồng thời TPO và fixed Volume Profile kéo 5 ngày làm composite tuần; khi TPO-POC lệch VPOC, dùng câu hỏi "close nằm đâu so với VPOC" như ví dụ trên để đoán khối lượng lệch về phe nào.

*— Keppler tr.92-98, 104-106, 113-116, 152-154; note tr.13; mp-vn tr.53*

---

## 3️⃣ Note thực chiến vàng — từ lý thuyết sang lệnh (~25') ⭐ PHẦN ĐINH

Đây là 17 trang note của một trader vàng thật, viết quanh các phiên GCQ23 (hợp đồng vàng tháng 8/2023). Ngôn ngữ đời thường, nhưng cơ chế bám sát những gì bạn đã học — nhiệm vụ của mình là dịch nó về đúng khung.

### 3.1 Hai nguyên tắc "fix profile" **[GT-7]**

Buổi trước đã học: đấu giá bất thường để lại single print / vùng thiếu mở rộng, và thị trường sẽ quay lại "fix" (sửa) chúng. Note cho 2 nguyên tắc chọn CÁI NÀO được fix:

1. **Market vận hành tuần tự** — cái xuất hiện TRƯỚC fix trước, cái xuất hiện SAU fix sau. Đừng kỳ vọng giá nhảy cóc sang vùng dang dở mới nhất khi vùng cũ hơn còn treo.
2. **Tôn trọng trend hiện hữu** — trend tăng thì các IB/SP phía TRÊN giá hiện tại được sửa; trend giảm thì fix phía dưới. Trend ở đây lấy theo **khung Daily** (khi đối tượng fix là IB).

Poor high/low (đỉnh/đáy có ≥2 TPO) — tức **Unfinished Business** bản TPO như đã nối ở buổi 1 — cũng nằm trong danh sách "việc chờ fix" này.

### 3.2 Quy tắc break 2 lần **[GT-1]**

Cơ chế của note (diễn đạt lại cho rõ): khi VA của các cột 30' mới trượt ra khỏi range đang có, chỉ có 2 kết cục — **break thật**, hoặc **bị từ chối** đẩy ngược vào trong. **Break lần 1 bị từ chối → lần break thứ 2 mới là clean break; chỉ việc chờ giá retest các vùng canh để vào lệnh.**

- Lưu ý chiều: lần 2 không bắt buộc cùng chiều lần 1 — ca thật bên dưới break lần 1 LÊN thất bại, lần 2 XUỐNG mới là clean break. Cái "clean" là ở chỗ *ý định rời range đã lộ và phe chặn đã kiệt*, không phải ở hướng.
- Kèm tip giờ: **18h–19h VN rất hay có fake break VA** **[GT-3]** — khớp với caveat "volume mở cửa giật ngược trước khi đi thật" ở khối 1.

**📊 Đọc chart thật** — [tpo/images/note/p013-0.png](tpo/images/note/p013-0.png): minh họa **GT-2** (Á/Âu build range): hộp đỏ trên khoanh chuỗi ~8 profile 30' xếp ngang cùng độ cao (range Á–Âu), mũi tên đỏ chéo xuống chỉ lúc VA move khỏi range, rồi hộp đỏ dưới khoanh chuỗi profile mới thấp hơn hẳn — VA đã "di cư" xong, range mới hình thành. Ảnh này cắt mất trục giá nên chỉ đọc cấu trúc, không đọc số.

### 3.3 Vùng hấp thụ supply/demand trên TPO + delta fresh vs tested

Cơ chế (note mô tả — chính là **Absorption** bạn đã học, giờ nhìn bằng cột delta từng mức giá trên TPO thay vì ô Bid×Ask):

- **Cột delta DƯƠNG lớn ở đỉnh** mà giá **đóng cửa phiên bên dưới** = một lượng buy market lớn đẩy vào mà giá không lên nổi → đã bị sell hấp thụ hết → vùng đó là **supply**.
- **Cột delta ÂM lớn ở đáy** mà giá **đóng cửa bên trên** = sell market bị nuốt → **demand**.

Không phải vùng nào cũng dùng được. Khi giá quay về, note check 3 thứ: (a) price action có dấu hiệu đảo chiều chưa; (b) order flow tại đó nói gì — kiệt sức, hấp thụ, thanh khoản (note gọi tắt là "BM", nhiều khả năng là Bookmap — *suy đoán của Claude*; với bạn vai trò này do footprint ATAS đảm nhận); (c) vùng đó **fresh hay tested** — vùng delta **fresh** (giá chưa quay lại chạm lần nào) mới còn nguyên giá trị, tested rồi thì hạ độ tin cậy **[GT-6]**. Note ưu tiên entry trong "mây VA" nếu trade scalp.

**📊 Đọc chart thật** — [tpo/images/note/p014-0.png](tpo/images/note/p014-0.png): chuỗi TPO có cột delta từng mức giá. Hộp ĐỎ = supply (cụm delta dương ở đỉnh, close phiên dưới đó), hộp XANH = demand ở đáy/giữa. Hai hàng số dưới chân mỗi phiên là tổng delta / tổng volume — đọc thử vài phiên: **-7281/156.507**, **-1800/53.526**, **-1055/106.399**. Chú ý phiên delta -7281 trên volume 156.507: bán ròng lớn nhưng nhìn vị trí các hộp xanh phía dưới — nhiều cụm sell đã bị hấp thụ, đó là các demand zone được khoanh.

### 3.4 🔬 Ca 1 — GCQ23 ngày 21/7: break range 2 lần + retest vùng supply

**📊 Đọc chart thật** — [tpo/images/note/p016-0.png](tpo/images/note/p016-0.png) (TPO M30, GCQ23-COMEX, các cột từ 15:30 đến 22:30 trên chart; trục giá 1958.5–1973.0; VAH phiên Tokyo kẻ sẵn **1971.3**, VAL Tokyo quanh ~1960):

1. **Range phiên Âu** (note viết "giá tạo range vào phiên Âu" — chart chỉ hiện từ 15:30 nên phần Á không thấy): hộp đỏ lớn bên trái khoanh thân range **~1964.5–1966.5**; đuôi các profile thò xuống **~1963** (các cột in delta -281, -104) — đó chính là đáy range mà mũi tên 3 phá qua sau này. Volume mỏng dần về cuối (V:1455, V:2263 mỗi cột).
2. **Mũi tên 1 — break lần 1 (LÊN)**: gần giờ mở CME, giá break khỏi range, đỉnh với lên vùng **~1970**. Nhưng nhìn hai hộp đỏ "Vùng giá bị hấp thụ" người viết khoanh: quanh **~1970** và dải **~1967.0–1967.6** — các cụm mua chủ động ở đỉnh bị đội sell nuốt sạch (delta dương lớn nhưng close cột nằm dưới).
3. **Mũi tên 2 — bị đẩy ngược về range**: sau 30' đầu phiên CME, cột dài đâm ngược xuyên range xuống ~1960.5; volume nổ V:5267 → V:7852 → V:9707.
4. **Mũi tên 3 — break lần 2 (XUỐNG)**: giá break qua đáy range ~1963 — theo quy tắc break 2 lần, đây là **clean break**.
5. **Entry**: giá hồi lên **retest đúng dải supply 1967.0–1967.6** (hộp đỏ kéo dài ngang qua các cột sau) rồi rơi về vùng 1959–1960 — cột rơi in delta **-282**. Note chốt: "có những entry bắt ngay tại râu nến là nhờ delta vol" — vì level đã kẻ sẵn TRƯỚC từ vùng hấp thụ, chỉ chờ giá chạm.

Bài học ghép: **TPO cho context** (range → break 1 fail → break 2 clean → chờ retest ở đâu), **delta/footprint cho trigger** (vùng hấp thụ + phản ứng tại retest). Đây chính xác là mô hình hợp lưu bạn sẽ backtest.

### 3.5 🔬 Ca 2 — GCQ23 ngày 26/7: buyer chủ động 12h30 + delta âm không đè được giá

**📊 Đọc chart thật** — [tpo/images/note/p017-0.png](tpo/images/note/p017-0.png) (GCQ23, các cột từ 7:30 đến 15:30; bên phải kẻ sẵn Tokyo VAH / POC / VAL và mấy đường `sp` = single print của phiên trước):

1. **Phiên Á lại build range**: hộp đỏ khoanh chuỗi cột 8:00→12:30 kẹp quanh Tokyo-POC, volume phần lớn lèo tèo V:445–V:1502 — riêng cột 8:00 đầu phiên nhô lên **V:2197** kèm delta **+205**, nhưng cú đẩy sớm đó không đi đến đâu: giá vẫn kẹt trong range suốt 4 tiếng sau. Còn lại delta lắt nhắt (-69, -48, -19, -2, -68...).
2. **Tín hiệu 12h30**: cột 12:30 được khoanh — delta **+128** (khoanh tròn, mũi tên chỉ lên). Con số này KHÔNG phải lớn nhất phiên (+205 lúc 8:00 to hơn), nhưng đây mới là tín hiệu: nó đến sau cả quãng dài delta lắt nhắt, giá **đóng cửa trên vùng mua**, và được cây break V:5857 confirm ngay sau đó — chữ "đột biến" của note là so với quãng im ắng trước nó, không phải so với cả phiên. Buyer chủ động xuất hiện.
3. **Cây break confirm 13:00**: volume nhảy vọt **V:1004 → V:5857**, cột dựng đứng xuyên qua các đường sp và VAH Tokyo (mũi tên ngang chỉ vào cột này).
4. **Sau break — chi tiết đắt nhất**: xuất hiện đội sell với **delta âm liên tục** — các vòng tròn đỏ khoanh **-105**, **-158** và một cột âm lớn hơn ở giữa — **nhưng giá không xuống**, vẫn ghim trên vùng VAH. Note kết luận: giá tiếp tục đi lên.

Nối cầu: đây chính là **Effort vs Result / absorption** bạn đã nắm — nỗ lực bán (delta âm) không tạo ra kết quả (giá không giảm) nghĩa là có limit buyer đủ lớn đang đỡ → tiếp diễn tăng. Note chỉ nói bằng ngôn ngữ khác.

Cảnh giác đi kèm trong note: hôm đó có tin lãi suất FED, thị trường chạy theo "mua tin đồn, bán sự thật" → mọi lệnh buy nên chốt/quản lý khi giá đến vùng nhạy cảm, đề phòng một cú quét toàn bộ đội buy — tức là **context tin tức có quyền phủ quyết setup kỹ thuật**.

### 🥇 Áp cho vàng MGC

- Hai ca trên là chart GC — MGC đi cùng giá, áp nguyên xi.
- Giờ trên hai chart này khớp logic "break gần giờ mở CME 19:20 VN" → chart của note nhiều khả năng để múi giờ VN (GMT+7); kiểm tra lại múi giờ ATAS của bạn trước khi so mốc **[lưu ý của Claude]**.
- Quy trình tái hiện: (1) đánh dấu range Á/Âu; (2) khoanh vùng hấp thụ supply/demand (cột delta lớn ngược hướng close) và ghi chú fresh/tested; (3) nếu break lần 1 fail → phục kích lần 2 + retest; (4) trigger bằng footprint tại vùng đã kẻ.

*— note toàn bộ, trọng tâm tr.9-17*

---

## 4️⃣ Kick-off thực hành (~20')

### 4.1 Sizing theo quy tắc 2%

Quy tắc bất di bất dịch của tác giả TraderViet: **mỗi lệnh chỉ được lỗ tối đa 2% tài khoản** — nhờ nó "không quan tâm chuyện ăn thua từng lệnh, chỉ tập trung phân tích cho tốt". Công thức cho MGC:

```
Số hợp đồng = (Vốn × 2%) / (SL tính bằng tick × $1)
```

- Vốn $2.000, SL 35 tick (3.5 điểm giá) → 40/35 = 1.1 → **1 hợp đồng**.
- Vốn $2.000, SL 80 tick → 40/80 = 0.5 → **không đủ cho 1 hợp đồng → bỏ kèo đó**, chờ setup có SL cấu trúc gần hơn. KHÔNG kéo SL lại gần cho "vừa tiền" — xem 4.3.
- Ăn hay thua đều giữ nguyên công thức, không tăng size gỡ.

### 4.2 Scaling out 3 mục tiêu + dời SL

**📊 Đọc chart thật** — [tpo/images/keppler/p135-0.png](tpo/images/keppler/p135-0.png): lệnh SHORT 3 hợp đồng ES tại **1339.00**. Ba mục tiêu lấy thẳng từ các mức volume/TPO của profile (panel trái: VAH 1337.50, POC 1333.50, VAL 1330.50):
- **Target 1 @ 1336.50** — vùng giá trị khối lượng cao,
- **Target 2 @ 1333.50** — POC,
- **Target 3 @ 1330.50** — vùng giá trị khối lượng thấp.

Mỗi target đạt → **đóng 1 hợp đồng + dời SL** về gần mức vừa đạt. Sau Target 1, lệnh này dù bị quét cũng không còn lỗ. Trên chart, giá chạy xuống đóng cửa 1328.50 (`N*` sát đáy) — cả 3 mục tiêu ăn trọn. Nối cầu: đây là phiên bản TPO của "TP theo volume" bạn đã học — mục tiêu luôn đặt TRƯỚC vùng volume dày, và ở đây các vùng đó tên là VAH/POC/VAL.

### 4.3 SL = điểm cấu trúc cho biết lệnh đã SAI

Nguyên tắc Keppler, đúng một câu hỏi: **"Mức giá nào trên cấu trúc profile cho ta biết giao dịch đã thất bại?"** — đặt SL ở đó, không bao giờ chọn SL theo một con số tiền tùy tiện.

- Đây chính là "SL sau lưng tường" bạn đã học ở ebook, phát biểu bằng ngôn ngữ profile: mức cấu trúc (đáy IB, biên VA, biên vùng hấp thụ) bị thủng = tiền đề của lệnh sụp đổ, ở lại vô nghĩa.
- Muốn rủi ro nhỏ hơn? **Giảm size hoặc chọn kèo khác có SL cấu trúc gần hơn — tuyệt đối không bóp stop**. Keppler: dùng size nhỏ tốt hơn nhiều so với một cái stop đặt sai chỗ; stop sai chỗ chỉ đẻ ra những khoản lỗ không cần thiết.
- Tỷ lệ tối thiểu **RR 1:2**, và phải đánh giá cùng xác suất thắng của chiến lược.
- Bị quét stop rồi giá chạy đúng hướng ≠ "cần stop xa hơn" — thường là vào sai thời điểm/giá vào xấu.

### 4.4 Hợp lưu phải đến từ nguồn ĐỘC LẬP

Keppler định nghĩa hợp lưu chiến lược: nhiều yếu tố từ **các nguồn thông tin khác nhau** cùng ủng hộ một lệnh. Bẫy kinh điển: *"giá đang tăng" + "giá vượt kháng cự"* trông như 2 yếu tố nhưng là **một** — cả hai đều rút ra từ cùng biến giá. Thêm volume tăng + xu hướng trung gian cùng chiều thì mới thành hợp lưu thật.

Áp vào bộ công cụ của bạn: **TPO cho context** (kịch bản ngày, VA migration, vùng hấp thụ, mức chờ) + **footprint cho trigger** (absorption, stacked imbalance, delta tại mức chờ) — đúng cặp nguồn độc lập của Ca 1: thời gian/cấu trúc vs dòng lệnh. Còn "TPO nói lên + đường MA cũng dốc lên" thì chưa chắc, vì cả hai cùng ăn từ giá.

### 4.5 Nhật ký backtest

Keppler: chiến lược **phải test trên sim/demo trước, không bao giờ test bằng tiền thật**; mỗi lần test phải có log — quy tắc chiến lược viết rõ, ảnh chart lúc vào và lúc thoát, báo cáo ngắn vì sao thắng/thua. 3/5 lần thắng **chưa phải** xác suất 60% — mẫu quá nhỏ, phải lặp đủ nhiều.

Mẫu cột nhật ký (mỗi phiên backtest 1 dòng):

| Ngày | Kịch bản ngày dự đoán (trước phiên) | Loại ngày thực tế | Setup đã vào | Kết quả (R) | Giả thuyết đã kiểm + kết quả kiểm |
|---|---|---|---|---|---|
| … | … | … | … | … | … |

Cột cuối là cột quan trọng nhất của giai đoạn này: mỗi phiên chọn 1 giả thuyết trong mục ⚠️ dưới đây và ghi nó ĐÚNG hay SAI hôm đó.

### 4.6 ✅ CHECKLIST TRƯỚC PHIÊN (in ra, dán cạnh màn hình)

1. **Kẻ 5 mức của phiên/ngày hôm qua**: High — VAH — POC — VAL — Low.
2. Kẻ thêm nếu có: POC clustering nhiều phiên, núm composite tuần, vùng supply/demand delta còn **fresh** (GT-6), single print chưa fix (GT-7).
3. **Đánh dấu IB** khi đủ 60' (A+B) — ghi mốc đang dùng: 19:20 hay 20:30 VN (GT-8).
4. **Xác định kiểu mở cửa** so với value hôm qua (trong/ngoài VA, gap có lấp không).
5. **Chọn kịch bản ngày** (balance hay trend, hướng nghiêng) — viết ra TRƯỚC, phiên xong đối chiếu vào nhật ký.
6. Nhắc bản thân: volume mở cửa có thể giật ngược; 18–19h VN hay fake break (GT-3); tin lớn có quyền phủ quyết.

*— mp-vn tr.53-54; Keppler tr.131-144*

---

## ⚠️ Tổng hợp giả thuyết cần kiểm khi backtest

GT-1 đến GT-7 là kinh nghiệm cá nhân tác giả note/TraderViet — chưa phải chuẩn Dalton/Keppler; riêng GT-8 là quy ước do giáo trình tự đặt để backtest. Mỗi phiên backtest hãy chấm ĐÚNG/SAI ít nhất một mục:

1. **GT-1 · Break 2 lần**: VA break khỏi range lần 1 bị từ chối → lần 2 là clean break; entry chờ ở retest. (Lưu ý: lần 2 có thể ngược chiều lần 1.)
2. **GT-2 · Á build range cho Âu, Âu build range cho CME** — chỉ cần canh lúc VA move khỏi range.
3. **GT-3 · 18h–19h VN hay có fake break VA** (ngay trước mở COMEX floor 19:20 VN).
4. **GT-4 · VA nằm gọn trong IB phiên Âu + biên độ thấp → phiên Mỹ có trend**.
5. **GT-5 · POC cũ bị breakout → "90%" thành cản mới tốt** (kháng cự thủng thành hỗ trợ; con số 90% là kinh nghiệm cá nhân tác giả).
6. **GT-6 · Vùng delta fresh đáng tin hơn hẳn vùng đã tested** — đo bằng tỷ lệ phản ứng tại chạm lần 1 vs lần 2+.
7. **GT-7 · Hai nguyên tắc fix profile**: SP/IB cũ hơn được fix trước SP mới; trend Daily quyết định phía được fix — chấm ĐÚNG/SAI mỗi lần thấy giá quay lại vùng dang dở.
8. **GT-8 · Mốc tính IB cho vàng**: 19:20 vs 20:30 VN — mốc nào cho cấu trúc IB/RE sạch hơn trên dữ liệu MGC của bạn.

---

## 🔑 Thẻ ôn thuật ngữ

Tra nhanh sau khi học — mỗi thuật ngữ 1 dòng cơ chế:

| EN | VN | Cơ chế 1 dòng |
|---|---|---|
| Settlement | Khung/giá thanh toán | 15' chốt ngày — cơ hội thanh khoản cuối của day trader → thành mốc neo cho phiên đêm và mở cửa hôm sau |
| Overnight Session | Phiên qua đêm | Đấu giá ngoài giờ Mỹ; đọc bằng vị trí của nó SO VỚI vùng settlement hôm trước |
| Gap Fill | Lấp khoảng trống | Mở cửa lệch khỏi settlement tạo gap; không lấp = phe theo hướng gap tự tin, quay về lấp = phe đó yếu |
| Big Smile / Frown | Nụ cười lớn / Cau mày | Vòng cung: đêm volume nhẹ → mở phiên volume nổ → move lên (Smile) hoặc xuống (Frown) |
| Composite Profile | Profile gộp | Gộp 5 profile ngày = profile tuần, gộp 20 ngày = profile tháng; các mức lớn hiện rõ dần |
| Knob | "Núm" | Mức giá có số TPO vượt trội nhô ra trên composite → thường thành S/R khi giá quay lại |
| Value Migration | Dịch chuyển vùng giá trị | Cách VA phiên sau đặt so với phiên trước — đó là câu trả lời của đấu giá: chấp nhận hay từ chối giá mới |
| POC Clustering | POC tụ chùm | POC của nhiều phiên nằm sát nhau = thị trường nhiều lần đồng ý cùng một giá → mức tham chiếu mạnh |
| TPO-POC vs VPOC | POC thời gian vs POC khối lượng | Nơi giá Ở LÂU nhất vs nơi TRAO TAY nhiều nhất — hai câu hỏi khác nhau |
| Delta fresh / tested | Vùng delta còn mới / đã test | Vùng cung–cầu delta chưa bị giá quay lại chạm = còn "đạn"; đã test rồi thì giá trị giảm |
| Scaling out | Chốt lời từng phần | Vào nhiều hợp đồng, mỗi mục tiêu đạt → đóng 1 phần + dời SL theo |
| Position sizing 2% | Khối lượng theo rủi ro 2% | Mỗi lệnh chỉ được thua tối đa 2% tài khoản → size tính NGƯỢC từ SL, không chọn tùy hứng |

## ✅ Kiểm tra cuối buổi

**Câu 1.** Phiên đêm đóng cửa TRÊN vùng settlement hôm trước → mở cửa có gap tăng. Kịch bản A: giá không lấp gap và đi tiếp lên. Kịch bản B: giá quay xuống lấp đầy gap. Mỗi kịch bản nói gì về phe mua, và vì sao settlement (chứ không phải giá đóng nến ngày) được chọn làm mốc?

**Câu 2.** Ba phiên liên tiếp: VA phiên 2 nâng lên nhưng THU HẸP còn một nửa; VA phiên 3 đỉnh cao hơn nhưng thân chồng xuống, đáy VA chạm đúng POC phiên 2. Theo cơ chế đấu giá, chuỗi này đang kể chuyện gì và bạn nghiêng kịch bản nào cho phiên 4?

**Câu 3.** *(đọc ảnh)* Mở [tpo/images/note/p016-0.png](tpo/images/note/p016-0.png): (a) mũi tên số mấy là clean break theo quy tắc break 2 lần, và nó ngược hay cùng chiều với break lần 1? (b) Entry short được phục kích ở dải giá nào, và dải đó được kẻ ra từ dấu hiệu gì có sẵn TRƯỚC khi giá quay lại?

**Câu 4.** Một ngày MGC có TPO-POC tại 2345.0 nhưng VPOC tại 2342.5; khối lượng trên VPOC gấp ~3 lần dưới VPOC; giá đóng cửa 2341.8 gần đáy ngày. Khối lượng dày phía trên VPOC nghiêng về mua hay bán, và mức nào đáng gờm hơn cho phiên sau?

**Câu 5.** Vốn $3.000, setup short tại kháng cự có SL cấu trúc cách entry 25 tick MGC. (a) Được vào mấy hợp đồng theo quy tắc 2%? (b) Nếu SL cấu trúc là 70 tick thì làm gì?

<details><summary>Đáp án</summary>

**1.** A = phe mua tự tin thật: giá mới cao hơn được CHẤP NHẬN, không ai cần quay về giá cũ để khớp lệnh → thuận đà tăng. B = thị trường yếu hơn vẻ ngoài: gap tăng không giữ nổi, giá phải quay về vùng giao dịch cũ tìm người mua. Settlement được chọn vì đó là cơ hội thanh khoản CUỐI CÙNG — mọi day trader buộc phải tất toán quanh nó và trader khung dài ra quyết định giữ/đóng tại đó, nên nó là "giá đồng thuận có cam kết" cuối ngày, còn phiên đêm được đo bằng phản ứng quanh chính mốc đó.

**2.** VA nâng nhưng thu hẹp = người mua vẫn thắng nhưng vùng đồng thuận co lại — đà đuối; VA phiên 3 chồng xuống, đáy chạm POC phiên 2 = thị trường quay về kiểm định giá trị cũ, có chốt lời — "giá trị cao hơn đang bị nghi ngờ". Nghiêng kịch bản phiên 4: từ chối giá cao → giảm/quay về vùng giá trị cũ (trong chuỗi EURUSD của Keppler, phiên sau giảm xác nhận và là cơ hội bán). Nếu phiên 4 bất ngờ đóng vững trên VAH phiên 3 thì phủ nhận kịch bản.

**3.** (a) Mũi tên **số 3** — break lần 2, và NGƯỢC chiều lần 1 (lần 1 phá lên ~1970 bị hấp thụ, lần 2 phá XUỐNG qua đáy range ~1963). Chữ "clean" nằm ở việc ý định rời range đã rõ và phe chặn đã kiệt, không quy định hướng. (b) Dải supply **~1967.0–1967.6** (hộp đỏ "Vùng giá bị hấp thụ") — kẻ từ các cột delta dương lớn ở đỉnh mà giá đóng cửa nằm dưới, tức cụm mua chủ động đã bị nuốt, có sẵn TRƯỚC cú retest; giá hồi chạm dải này rồi rơi về ~1959–1960 (cột rơi delta -282).

**4.** Nghiêng về BÁN: khối lượng dồn phía trên VPOC mà giá đóng gần đáy ngày → theo cơ chế đấu giá, lượng trao tay lớn ở giá cao không giữ được giá thì bên chủ động thắng cuộc là bên bán (y hệt ca ES: 1.098.142 trên VPOC, close 1357.75 sát đáy). Mức đáng gờm cho phiên sau là **vùng quanh VPOC 2342.5 và dải khối lượng phía trên nó** — hồi lên đó dễ gặp lại nguồn cung; TPO-POC 2345.0 chỉ nói giá Ở LÂU, còn tiền thật đã đổi chủ quanh 2342.5.

**5.** (a) Risk = 3.000 × 2% = $60; SL 25 tick × $1 = $25/hợp đồng → 60/25 = 2.4 → **2 hợp đồng** (luôn làm tròn XUỐNG). (b) 70 tick → 60/70 = 0.85 < 1 hợp đồng → **bỏ kèo hoặc chờ setup có SL cấu trúc gần hơn** — không được kéo SL từ 70 về 60 tick cho "vừa tiền", vì SL phải nằm ở điểm cấu trúc nói lệnh đã SAI; giải pháp đúng theo Keppler là giảm size hoặc đổi kèo, mà size đã là tối thiểu thì chỉ còn đổi kèo.

</details>

## 📋 Ảnh load khi dạy

Theo thứ tự giảng:

1. [tpo/images/keppler/p084-0.png](tpo/images/keppler/p084-0.png) — 5 phân đoạn phiên Mỹ trên split profile ES (A→N)
2. [tpo/images/keppler/p088-0.png](tpo/images/keppler/p088-0.png) — settlement gần đỉnh ngày + phiên overnight quay về điểm xuất phát
3. [tpo/images/keppler/p127-0.png](tpo/images/keppler/p127-0.png) — mẫu Big Smile (volume nổ ~1135–1140 → lên ~1145)
4. [tpo/images/keppler/p128-0.png](tpo/images/keppler/p128-0.png) — mẫu Frown (volume nổ ~1115–1135 → rơi về 1100–1105)
5. [tpo/images/keppler/p093-0.png](tpo/images/keppler/p093-0.png) — 5 profile ngày liên tiếp: VA hạ bậc thang rồi bật
6. [tpo/images/keppler/p153-0.png](tpo/images/keppler/p153-0.png) — POC clustering A/G/H + Area of Price Acceptance (EURUSD)
7. [tpo/images/keppler/p095-0.png](tpo/images/keppler/p095-0.png) — composite tuần, POC 1342.25 + 4 núm
8. [tpo/images/keppler/p097-0.png](tpo/images/keppler/p097-0.png) — composite tháng, POC 1343.00
9. [tpo/images/keppler/p098-0.png](tpo/images/keppler/p098-0.png) — hai profile 20 ngày: VAL tháng này rơi đúng POC tháng trước ~1329
10. [tpo/images/keppler/p115-0.png](tpo/images/keppler/p115-0.png) — value tracking 30': đáy VA cột N 1328.75 trùng vùng cột C
11. [tpo/images/keppler/p104-0.png](tpo/images/keppler/p104-0.png) — TPO-POC 1359.50 vs VPOC 1358.00, khối lượng 1.098.142/311.091
12. [tpo/images/note/p013-0.png](tpo/images/note/p013-0.png) — Á/Âu build range, VA move khỏi range (đọc cấu trúc)
13. [tpo/images/note/p014-0.png](tpo/images/note/p014-0.png) — vùng hấp thụ supply/demand bằng cột delta trên TPO
14. [tpo/images/note/p016-0.png](tpo/images/note/p016-0.png) — ⭐ Ca 1 GCQ23 21/7: break 2 lần + retest supply 1967.0–1967.6
15. [tpo/images/note/p017-0.png](tpo/images/note/p017-0.png) — ⭐ Ca 2 GCQ23 26/7: delta +128 lúc 12h30, V:1004→V:5857, delta âm không đè được giá
16. [tpo/images/keppler/p135-0.png](tpo/images/keppler/p135-0.png) — scaling out: short 1339, T1 1336.50 / T2 1333.50 / T3 1330.50
