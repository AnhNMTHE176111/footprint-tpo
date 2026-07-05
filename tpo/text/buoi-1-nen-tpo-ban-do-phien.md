# Phụ lục TPO — Buổi 1/3: Đọc chart TPO & bản đồ trong phiên

> ⏱ ~75–90' · Buổi mở màn của phụ lục TPO/Market Profile (sau khi đã xong toàn bộ ebook Order Flow). Buổi 1 xây nền: đọc được chart TPO và vẽ "bản đồ trong phiên" (IB, range extension, tails, single print). Buổi 2 sẽ vào hình dạng ngày + Value Area động, buổi 3 là playbook thực chiến vàng.

## 🎯 Mục tiêu buổi

Sau buổi này bạn:
- Hiểu khung auction theory của Market Profile: ai tạo balance, ai tạo trend, giá công bằng vs giá có lợi — và thấy nó khớp với khung chủ động/thụ động đã học từ order flow.
- Đọc trôi chảy một chart TPO: chữ cái bracket 30', ký hiệu O/*, dạng gộp (composite) vs tách (split), phân biệt TPO-POC với Volume-POC khi bật cả hai trên ATAS.
- Xác định Initial Balance, đọc range extension để trả lời "phiên này ai kiểm soát", và chiếu mục tiêu giá từ độ rộng IB (lọc bằng ADR/ATR đã học).
- Nhận diện buying/selling tail, single print giữa profile (minus development), ledge — biết vùng nào sẽ thành S/R tương lai và có playbook chờ retest thay vì đuổi giá.
- Nối được poor high/low với Unfinished Business đã học.

## 🔑 Thuật ngữ mới

| EN | VN | Cơ chế 1 dòng |
|---|---|---|
| TPO (Time Price Opportunity) | Cơ hội Giá–Thời gian | 1 chữ cái = mức giá đó ĐƯỢC CHẠM ít nhất 1 lần trong bracket 30'; chạm 100 lần vẫn chỉ in 1 chữ |
| Bracket / Period | Khung 30 phút | Mỗi 30' đổi sang chữ cái kế tiếp: A, B, C, D… |
| Initial Balance (IB) | Cân bằng ban đầu | Range của 2 bracket đầu A+B (60 phút đầu phiên) |
| Range Extension (RE) | Mở rộng phạm vi | Giá vượt ra ngoài IB → dấu hiệu trader khung lớn nhập cuộc |
| OTF trader (Other Timeframe) | Trader khung thời gian khác | Chơi dài hơn 1 phiên, không bị ép đóng lệnh cuối ngày → là người tạo trend |
| Day timeframe trader | Trader trong phiên | Bị ép đóng lệnh trước khi phiên đóng cửa → sống bằng thanh khoản quanh giá hợp lý, tạo balance |
| Fair price / Advantageous price | Giá công bằng / giá có lợi | Fair = nơi 2 phe khớp nhiều nhất (vol lớn); advantageous = xa giá trị, vol mỏng, chỉ OTF thèm |
| Acceptance / Rejection | Chấp nhận / từ chối vùng giá | Giá ở LẠI đủ lâu để xếp TPO = chấp nhận; bật đi nhanh trong <30' = từ chối |
| Buying / Selling Tail | Đuôi mua / đuôi bán | Chuỗi ô in đơn ở đáy/đỉnh profile = OTF phản ứng (responsive) từ chối giá bất công |
| Single Print | Vùng in đơn | Đoạn giá cả phiên chỉ có đúng 1 cột chữ chạm qua |
| Minus Development | Phát triển thiếu | Single print nằm GIỮA profile — vết giá chạy quá nhanh, không kịp xây giá trị |
| Ledge | Gờ | ≥3 TPO cùng dừng phẳng ở 1 mức giá → nền hỗ trợ/kháng cự |
| Poor High / Poor Low | Đỉnh/đáy dở dang | Đỉnh/đáy phẳng ≥2 TPO, KHÔNG có tail = đấu giá chưa xong ở cực trị |
| Composite / Split Profile | Profile gộp / tách | Gộp: chồng các cột chữ thành 1 phân phối; tách: mỗi bracket đứng riêng như bar chart |
| TPO-POC vs Volume-POC (VPOC) | POC theo thời gian vs theo khối lượng | TPO-POC = hàng chữ dài nhất (nhiều bracket ghé nhất); VPOC = mức giá khớp volume lớn nhất |
| Pioneer Range | Phạm vi tiên phong | Vùng giá được in TPO LẦN ĐẦU trong phiên — nơi quan sát thị trường chấp nhận hay từ chối giá mới |

**Ghi chú lỗi dịch máy trong tài liệu nguồn** (khi bạn tự tra lại sách): bản dịch Keppler hay ghi "Hồ sơ thị trường" = Market Profile, "số dư ban đầu / khoảng cân bằng ban đầu" = Initial Balance, "phần mở rộng / phạm vi mở rộng" = Range Extension, "sự phát triển trừ/âm" = Minus Development, "gờ" = Ledge, "bản in đơn" = Single Print; các mốc kiểu "mở cửa lúc 12 giờ 32 phút" thực ra là MỨC GIÁ 1232.x chứ không phải giờ. Bài này dùng thuật ngữ tiếng Anh chuẩn, đối chiếu thêm ở `glossary.md`.

---

## 1️⃣ Auction theory tinh gọn — ai tạo balance, ai tạo trend (~10')

Bạn đã học đấu giá 2 chiều ở tầng vi mô (ô Bid×Ask: ai chủ động nhấc Ask, ai đạp Bid). Market Profile nhìn CÙNG cuộc đấu giá đó nhưng ở tầng vĩ mô hơn, và chia người chơi theo **thời gian** thay vì theo chủ động/thụ động:

- **Day timeframe trader** (trader trong phiên): bị "điểm ép buộc" — hết phiên PHẢI đóng lệnh. Họ đánh size lớn ăn mỏng, nên cần thanh khoản, và thanh khoản lớn nhất nằm quanh **giá công bằng (fair price)** — mức giá mà nhiều người mua lẫn người bán chấp nhận nhất. Họ giao dịch qua lại quanh giá trị → chính họ xây nên vùng **balance**.
- **OTF trader** (khung thời gian khác: swing, tổ chức, quỹ): không bị ép đóng lệnh cuối ngày. Họ KHÔNG tìm giá công bằng — họ tìm **giá có lợi (advantageous price)**: mua ở mức thấp bất công, bán ở mức cao bất công, hoặc chủ động đẩy giá khi nhận thức giá trị của họ thay đổi. Khi họ vào đủ khối lượng, range trong phiên bị kéo giãn → chính họ tạo **trend / range extension**.

Hai khái niệm then chốt còn lại:

- **Acceptance (chấp nhận)**: giá đến vùng mới và Ở LẠI — TPO xếp dày dần, volume duy trì → thị trường đồng ý đây là giá trị mới.
- **Rejection (từ chối)**: giá đến vùng mới và bị đá đi ngay trong vòng chưa đầy 1 bracket → để lại tail hoặc single print. Sách gói gọn: *nếu thị trường từ chối mức cao/thấp bất công, giá sẽ quay về vùng giá trị*.

**Nối với order flow đã học:** cẩn thận một điểm — "phản ứng" (responsive) ở đây KHÔNG đồng nghĩa "thụ động". Responsive nghĩa là phản ứng với GIÁ BẤT CÔNG và kéo giá VỀ vùng giá trị; Keppler mô tả người mua responsive "nhanh chóng tìm đến và MUA những giá hời" — họ có thể chặn giá bằng tường limit thụ động (như Large Limit Orders bạn đã học) HOẶC vồ hàng bằng market order chủ động. Chữ "responsive" nói về VỊ TRÍ so với giá trị, không nói về chủ động/thụ động. Còn OTF "chủ động đẩy giá" (initiative) là phe market order quét thanh khoản tạo Imbalance/Stacked khi nhận thức giá trị của họ thay đổi. TPO không cho bạn thấy TỪNG lệnh như footprint — nó cho thấy **hậu quả tích lũy theo thời gian** của các hành vi đó.

### 📊 Đọc chart thật

1. [tpo/images/tv/p008-1.png](tpo/images/tv/p008-1.png) — sơ đồ "3 tầng người chơi" của TraderViet: dải đỏ trên cùng ghi **Long-term sellers** (mũi tên đỏ ép xuống), dải xám giữa ghi **"vùng mà đa số tin là giá trị"** — chú thích bên phải: Short-term Traders / Daytrading / Local / Middle man, dải xanh dưới cùng ghi **Long-term Buyer** (mũi tên xanh đẩy lên). Bên trái là hình phân phối màu cam — chính là cái profile hình chuông sinh ra từ cấu trúc 3 tầng này.
2. [tpo/images/keppler/p043-0.png](tpo/images/keppler/p043-0.png) — bản chuẩn của Keppler (Fair Price Area): hình chữ D nằm ngang; phía trên ghi *Advantageous Price Area for Long Term Sellers*, bụng chữ D ghi *Most of the Trading Activity… Between Short Term Sellers and Buyers*, phía dưới ghi *Advantageous Price Area for Long Term Buyers*. Bụng D = sân của day trader; hai mép = sân của OTF.

### 🥇 Áp cho vàng MGC

- Vàng chạy gần 23h/ngày trên Globex (mở 18:00 ET = **05:00 VN**, giờ mùa hè), nhưng OTF của vàng hoạt động đậm nhất quanh 2 mốc: COMEX floor 8:20 ET = **19:20 VN** và US equities open 9:30 ET = **20:30 VN**. Trước 19:20 VN (phiên Á/Âu sáng-chiều VN) chart TPO vàng thường là day trader xây balance; sau 19:20–20:30 VN là lúc OTF quyết định chấp nhận hay từ chối vùng giá trị đó **[GIẢ THUYẾT — suy luận của người soạn từ giờ COMEX/US, chưa backtest]**.
- Câu hỏi thường trực khi nhìn chart TPO vàng mỗi tối: "range hiện tại là do day trader xoay quanh giá trị, hay OTF đã nhúng tay (range bị kéo giãn một phía)?"

*— Nguồn: TraderViet tr.7–10; Keppler tr.33, 40–43.*

---

## 2️⃣ Cơ chế chart TPO — thời gian, không phải khối lượng (~20')

### TPO và bracket 30'

**TPO = Time Price Opportunity**: cứ mỗi khung 30 phút (bracket), mức giá nào được giao dịch chạm tới ÍT NHẤT 1 lần thì in đúng 1 chữ cái tại mức đó. Bracket đầu phiên = chữ **A**, bracket thứ hai = **B**, cứ thế nối tiếp. Trong CÙNG một bracket, giá quay lại mức cũ bao nhiêu lần cũng không in thêm — chỉ khi bracket SAU quay lại mức đó thì chữ cái mới in thêm ở cột bên phải.

Ký hiệu phụ: **O** = giá mở cửa, **\*** (một số nền tảng dùng **#**) = giá đóng của chu kỳ. Tại sao 30 phút? Lý giải của Keppler: con người tự nhiên ra quyết định theo nhịp nửa giờ/một giờ — nên M30 thành chuẩn mặc định của Market Profile.

### Composite vs Split

- **Split profile (tách)**: mỗi bracket một cột riêng, nhìn giống bar chart M30 — dễ thấy range từng bracket nở hay co.
- **Composite (gộp)**: các cột chữ dồn hết sang trái, chồng lên nhau thành MỘT phân phối — dễ thấy hình chuông, POC, Value Area. Đây là dạng mặc định để phân tích cấu trúc phiên.

### TPO-POC vs Volume-POC — điểm bạn phải nắm chắc nhất mục này

Đây là chỗ dễ lẫn nhất với Volume Profile đã học:

| | TPO Profile | Volume Profile (đã học) |
|---|---|---|
| Đếm cái gì | **THỜI GIAN**: giá ở mức này bao nhiêu bracket | **KHỐI LƯỢNG**: mức này khớp bao nhiêu hợp đồng |
| POC | Hàng chữ dài nhất (nhiều bracket ghé nhất) | Mức khớp volume lớn nhất (VPOC) |
| Ý nghĩa | Nơi thị trường DÀNH nhiều thời gian nhất = giá hợp lý theo thời gian | Nơi tiền THẬT đổ vào nhiều nhất |

Hai POC **thường gần nhau nhưng không trùng nhau** — giá có thể "ngồi lâu" ở một mức mà khớp ít (thời gian nhiều, vol mỏng), hoặc quét qua nhanh nhưng khớp cực dày (vol lớn, thời gian ít). Value Area cũng vậy: có TPO-Value Area (70% số TPO) và Volume-Value Area (70% volume) — cùng công thức 70% ≈ 1 độ lệch chuẩn của phân phối chuẩn mà bạn đã biết từ Volume Profile.

### 📊 Đọc chart thật

1. [tpo/images/keppler/p009-0.png](tpo/images/keppler/p009-0.png) — viên gạch đầu tiên: chữ **O** in tại 1316.00, bốn chữ **A** xếp dọc bên dưới xuống 1315.00, chữ A cuối kèm dấu **\***. Chú thích trên ảnh: *Open For Period "A"* và *Four TPO Prints Below The Open*. Vậy 30 phút đầu giá mở 1316.00 rồi trượt xuống 1315.00 — mỗi mức giá đi qua để lại đúng 1 TPO.
2. [tpo/images/keppler/p011-0.png](tpo/images/keppler/p011-0.png) — một bracket A trọn vẹn: chuỗi chữ A phủ kín từ **1302.75 lên 1307.75**, chữ **O** nằm tại **1304.50** → mở cửa 1304.50, trong 30' đầu giá quét xuống 7 mức giá dưới O và lên 13 mức trên O, đỉnh bracket 1307.75 kèm dấu \*.
3. [tpo/images/keppler/p013-0.png](tpo/images/keppler/p013-0.png) — **split profile** 5 bracket A→E: cột B leo lên đỉnh 1310.00 rồi các bracket C-D-E rơi dần, cột cuối in **DE\*** kết thúc tại 1303.00. Nhìn dạng tách này bạn thấy ngay "câu chuyện" từng 30 phút — nhưng khó thấy đâu là giá trị.
4. [tpo/images/keppler/p036-0.png](tpo/images/keppler/p036-0.png) — cùng dữ liệu dạng **composite**: các hàng chữ chồng nhau thành hình chuông; hàng dài nhất tại **1339.50** được đánh dấu mũi tên *Point of Control* kèm nhãn `1339.50 (60/69)`; Value Area đóng khung từ **1338.00** lên **1341.50**. Để ý các hàng 1338.75–1339.75 dài gần bằng nhau (đều ~9 chữ) — khi nhiều mức đồng dài nhất, POC được gán cho mức gần TÂM Value Area nhất.
5. [tpo/images/keppler/p038-0.png](tpo/images/keppler/p038-0.png) — **Price (TPO) Value Area vs Volume Value Area** trên cùng một phiên: đáy hai vùng trùng nhau tại **1338.00**, nhưng đỉnh TPO-VA là **1341.50** trong khi đỉnh Volume-VA chỉ **1341.00**; TPO-POC 1339.50 nằm TRÊN VPOC 1339.00. Bằng chứng trực quan: thời gian và khối lượng không phải một.

### 🥇 Áp cho vàng MGC

- Trên ATAS bạn đã có chart TPO: để đúng chuẩn buổi này, đặt bracket = **30 phút**, bật **cả TPO-POC lẫn Volume-POC** (ATAS cho hiện song song). Tick MGC = 0.1 = $1 → mỗi ô giá trên profile là 0.1.
- Quy tắc đọc kép: TPO-POC và VPOC **trùng nhau** → vùng giá trị rất "thật", S/R đáng tin (thời gian + tiền cùng xác nhận). Hai POC **lệch xa nhau** → tự hỏi: giá ngồi lâu ở đâu, tiền thật đổ ở đâu — một cách nghiêng phổ biến (heuristic của người soạn, tự kiểm khi backtest) là ưu tiên VPOC vì bạn đã biết volume là dấu chân tiền thật.
- Data delayed 15' của gói free không ảnh hưởng việc HỌC cấu trúc phiên (profile hình thành chậm theo bracket 30'); chỉ cần nhớ khi sang thực chiến entry theo footprint thì độ trễ mới thành vấn đề.
- Bài tập tại chart tối nay: mở TPO phiên gần nhất của MGC ở dạng composite, tự xác định bằng mắt: chữ cái bracket hiện tại, TPO-POC, VPOC, và trả lời "hai POC cách nhau bao nhiêu tick?" — thao tác 2 phút này lặp mỗi tối sẽ thành phản xạ.

*— Nguồn: Keppler tr.9–14, 26, 35–38; TraderViet tr.10–14, 43–44.*

---

## 3️⃣ Initial Balance + Range Extension — khung xương của phiên (~25')

### Initial Balance: 60 phút định hình cả ngày

**IB = range của 2 bracket đầu A+B (60 phút đầu phiên).** *(Chuẩn hóa: tài liệu TraderViet chỗ ghi 1 giờ, chỗ dùng ví dụ khác — ta cố định theo Keppler/Dalton: A+B, 60 phút.)* Vẽ 2 đường ngang tại IB High và IB Low ngay khi bracket B đóng — đó là khung tham chiếu cho phần còn lại của phiên.

Vì sao 60' đầu quan trọng? Keppler dùng khái niệm **Pioneer Range** để giải thích: vùng giá được in TPO LẦN ĐẦU trong phiên là nơi quan sát thị trường chấp nhận hay từ chối giá mới — và giá mở cửa/IB chính là Pioneer Range đầu tiên của cả phiên, nên nó cho ta tín hiệu SỚM nhất về tâm lý ngày hôm đó. Đó cũng là lúc day trader dò tìm vùng giá hợp lý để mua bán hai chiều. Thực tế nhiều ngày, high hoặc low CỦA CẢ NGÀY được lập ngay trong IB. Quy tắc đọc quyền kiểm soát:

- **High/low lập trong IB và GIỮ được suốt phiên** → day trader kiểm soát ngày hôm đó (không ai đủ lực kéo giá đi).
- **OTF vào đủ khối lượng** → IB bị phá, range bị kéo giãn → quyền kiểm soát đổi chủ.

Độ rộng IB cho kịch bản:

- **IB hẹp** → xác suất cao sẽ bị mở rộng về một phía (chân đèn hẹp, đẩy nhẹ là đổ — ví von của TraderViet). Ngoại lệ: ngày chờ tin lớn, giá có thể nằm im trong IB hẹp cả buổi.
- **IB rộng** → 3 kịch bản: (1) tiếp tục chạy cùng hướng IB thành ngày xu hướng; (2) cả ngày nằm gọn trong IB — IB chính là range cả ngày; (3) chỉ lòi nhẹ ra ngoài hai mép để test rồi quay vào.

### Range Extension: đọc "ai kiểm soát"

**RE = mọi biến động giá vượt ra ngoài IB.** Bảng đọc nhanh:

| Diễn biến so với IB | Thông điệp |
|---|---|
| RE lên, giữ được | Người mua (OTF) kiểm soát |
| RE xuống, giữ được | Người bán (OTF) kiểm soát |
| RE cả 2 phía | Biến động cao, chưa ai thắng — thường là dạo đầu cho một cú định hướng |
| Không RE phía nào | Thị trường chưa sẵn sàng rời vùng giá — nghỉ ngơi hoặc chuyển tiếp |

**Failed auction (đấu giá thất bại):** giá phá ra ngoài IB nhưng không giữ được — theo note thực chiến, không giữ được động lượng **quá ~30 phút [GIẢ THUYẾT — tự kiểm khi backtest]** rồi chui lại vào IB → kỳ vọng giá quay sang test **mặt kia** của IB. Cơ chế đấu giá: phá biên mà không ai theo (không có acceptance) = từ chối, đám đông kẹt hàng phía sai phải thoát → nhiên liệu cho chiều ngược lại. Đây chính là logic "phá tường thất bại" bạn đã gặp ở Absorption, nhìn bằng cấu trúc TPO.

### Chiếu mục tiêu từ độ rộng IB

Công thức Keppler dùng trong ví dụ AAPL: khi RE xác nhận một hướng, mục tiêu tối thiểu = **biên IB phía đó ± đúng 1 lần độ rộng IB** (RE lên: IB High + độ rộng IB; RE xuống: IB Low − độ rộng IB). Trong ví dụ sách: IB của AAPL rộng ~$2, IB High 335.40 → mục tiêu 337.40; stop đặt theo CẤU TRÚC (đáy bracket B = 333.90), không đặt theo con số đô la tùy hứng. *(Chú thích nếu bạn tra lại sách: text ghi IB 332.80–335.40, tức ≈$2.60, nhưng khi chiếu mục tiêu lại dùng tròn "$2" — số minh họa của sách hơi vênh nội bộ; cái cần giữ là LOGIC: mục tiêu tối thiểu = biên IB + đúng độ rộng IB.)*

**Lọc bằng ADR/ATR đã học:** mục tiêu chiếu chỉ đáng tin khi ngày hôm đó CÒN "quỹ đạn". Sách cũng đối chiếu mục tiêu với ADR (AAPL chạy trung bình ~$6/ngày nên +$2 là khả thi). Quy trình cho bạn: lấy ATR(Daily) → trừ đi quãng đường giá đã chạy trong ngày → nếu mục tiêu chiếu vượt quá phần còn lại, hạ kỳ vọng hoặc bỏ kèo.

### 📊 Đọc chart thật

1. [tpo/images/keppler/p018-0.png](tpo/images/keppler/p018-0.png) — chart mẫu cả mục này: khung IB đóng hộp từ **1302.75** (nhãn dưới) lên **1310.00** (nhãn trên) — độ rộng IB = 7.25 điểm. Phía dưới hộp, các chữ D-E tràn xuống: cột E in tiếp 1302.50 → **1300.00**, kèm **O\*** tại ~1301.75 và mũi tên *Range Extension Below Initial Balance*. Phe bán phá đáy IB và giữ được → người bán kiểm soát cuối phiên.
2. [tpo/images/keppler/p019-0.png](tpo/images/keppler/p019-0.png) — sơ đồ 4 loại RE đặt cạnh nhau: *No Range Extensions / Range Extension Up / Range Extension Down / Range Extension Up & Down* — dùng làm flashcard cho bảng đọc nhanh ở trên.
3. [tpo/images/tv/p016-0.png](tpo/images/tv/p016-0.png) — ví dụ TraderViet trên hợp đồng trái phiếu (giá kiểu 114-04): bracket A đứng riêng trên đỉnh 114-06→114-09, từ 114-05 trở xuống profile dày dần (ABDEF, ABDEFG…) và hộp vàng **RANGE EXTENSION** khoanh vùng 113-31 xuống 113-25 — các bracket muộn C-I-J-K-L-M liên tục mở đáy mới: RE xuống, người bán kiểm soát.
4. [tpo/images/note/p009-0.png](tpo/images/note/p009-0.png) — slide "ĐẤU GIÁ THẤT BẠI" trong note thực chiến: TPO bên trái minh họa *Failed Auction in "D" Period*; nến bên phải chú thích *"D" period candle tried to break below IB but was quickly bought back* — nến D chọc thủng đáy IB rồi bị mua ngược ngay trong bracket.

### 🥇 Áp cho vàng MGC

- **Mốc tính IB cho vàng là LỰA CHỌN QUY ƯỚC** (vàng chạy gần 24h, không có "mở cửa" duy nhất như cổ phiếu). Khuyến nghị test cả 2 mốc khi backtest: IB từ **19:20 VN** (COMEX floor: A = 19:20–19:50, B = 19:50–20:20) và IB từ **20:30 VN** (US equities open: A = 20:30–21:00, B = 21:00–21:30). Chọn mốc nào cho tín hiệu RE/failed auction sạch hơn trên dữ liệu vàng thì cố định mốc đó.
- Độ rộng IB đo bằng tick 0.1 = $1: ví dụ IB rộng 4.0 giá (40 tick) thì mục tiêu chiếu = biên IB ± 4.0, tương đương ±$40/hợp đồng MGC — luôn đối chiếu với ATR(Daily) của vàng trước khi tin mục tiêu.
- Note thực chiến có quy tắc: **IB có range ≤1% (biên độ rất hẹp) → xác suất cao phiên sau breakout [GIẢ THUYẾT — tự kiểm khi backtest]** — với vàng hãy quy đổi "hẹp" theo phân vị độ rộng IB lịch sử thay vì % cứng.
- Khung giờ canh failed auction đáng chú ý nhất với mốc 19:20: cú phá IB đầu tiên hay rơi vào bracket 20:20–21:30 VN (trùng US equities open 20:30) **[GIẢ THUYẾT — suy luận của người soạn từ giờ mở cửa Mỹ, chưa backtest]** — đây là lúc OTF chứng khoán Mỹ đổ tiền, quan sát acceptance/rejection kỹ nhất ở đó.

*— Nguồn: Keppler tr.15–19, 69, 74, 78–79, 142–143; TraderViet tr.15–16; Note tr.9 + slide đấu giá thất bại.*

---

## 4️⃣ Tails + Single Print — vết chân OTF trên profile (~25')

### Buying tail / Selling tail: từ chối ở cực trị

Khi giá rơi xuống vùng "thấp bất công", OTF mua phản ứng nhảy vào vồ hàng giá hời → giá bật lên nhanh đến mức các mức giá dưới cùng chỉ kịp in **1 cột chữ duy nhất** → chuỗi in đơn dưới đáy profile = **buying tail (đuôi mua)**. Ngược lại ở đỉnh: giá lên vùng "cao bất công", OTF bán xả mạnh → **selling tail (đuôi bán)**.

Quy tắc sức mạnh: **đuôi càng DÀI càng ý nghĩa** — mỗi ô giá của đuôi là một mức mà phe phản ứng không thèm cho giá ngồi lại quá 30'. **Đuôi chỉ 1 TPO thì không mang ý nghĩa như đuôi dài** — về mặt kỹ thuật ô cuối cùng của range gần như luôn là in đơn, nên đuôi 1 ô coi như nhiễu. Thị trường sẽ thường quay lại TEST các mức đuôi này để kiểm tra phe phản ứng còn ở đó không → đuôi dài = ứng viên S/R.

**Nối order flow:** tail trả lời CÙNG CÂU HỎI với Absorption/Large Limit Orders — "ai đang chặn giá ở cực trị?" — nhưng KHÔNG cùng cơ chế hiển thị, đừng đánh đồng. Absorption bạn đã học là giá ĐỨNG YÊN nuốt lệnh với volume lớn ở cả hai cột; tail thì ngược về hình thái: giá bị ĐÁ ĐI NHANH khỏi vùng bất công, volume tại các mức in đơn thường mỏng — về hình thái nó gần với rejection tốc độ cao/exhaustion tại biên hơn là absorption. Footprint cho bạn thấy cú chặn NGAY LÚC ĐÓ (từng ô Bid×Ask), còn tail hiện ra SAU KHI bracket đóng — đổi lại nó tự động lưu thành cấu trúc trên bản đồ phiên.

### Single print giữa profile = Minus Development

Single print không chỉ nằm ở 2 đầu. Khi nó nằm **GIỮA** profile, sách gọi là **minus development (phát triển thiếu)**: giá chạy XUYÊN qua vùng đó quá nhanh, không kịp xây dựng giá trị — thị trường đã phán vùng này là giá bất công nên "không lãng phí thời gian ở đó". Đây là vết chân OTF rõ nhất trên chart TPO: chỉ OTF mới đủ lực kéo giá xuyên vùng giá nhanh như vậy.

Hệ quả quan trọng: vùng minus development có **xác suất cao bị quay lại test** trong phiên đó hoặc các phiên sau — giá vượt lên để lại single print bên dưới → vùng đó thành **hỗ trợ**; giá lao xuống để lại single print bên trên → thành **kháng cự**. Bạn nhận ra ngay: đây chính là logic LVN của Volume Profile (giá không giao dịch = kẽ hở), nhưng đo bằng thời gian.

### 🎯 PLAYBOOK: đừng đuổi — chờ retest single print

Keppler mô tả đúng cái bẫy mà trader hay dính khi thị trường chạy nhanh: đuổi theo bằng lệnh market thì khớp ở đỉnh sóng, spread rộng; đặt limit thì không khớp; vào được thì dính cú giật ngược quét stop xong giá... đi tiếp hướng cũ. Cách của Profile trader:

1. **Không đuổi** cú chạy đang tạo single print.
2. **Chờ giá quay lại test vùng single print / minus development.**
3. Vùng giữ được vai trò S/R (giá chạm và bị đẩy đi) → **vào lệnh theo hướng cú chạy ban đầu** ở giá đẹp hơn hẳn.
4. **SL đặt theo cấu trúc**: bên kia vùng single print — nếu giá lấp hẳn vùng in đơn (từng mức bắt đầu in chữ thứ hai) thì tiền đề "giá bất công" sụp, thoát. Khớp nguyên tắc SL "sau lưng tường" bạn đã học ở quản lý lệnh.

Note thực chiến bổ sung góc nhìn thanh khoản: trong single print tồn tại **liquidation/lệnh limit chưa khớp**, và SP hay nằm ở vùng thanh khoản (chỗ break kháng cự/hỗ trợ) **[kinh nghiệm tác giả note]**; để "fix" (lấp) một SP cần **volume + thời gian** — vol to mà không lấp nổi thì lực đẩy đó "lởm", giá không đi **[GIẢ THUYẾT — tự kiểm khi backtest]**. Trong trend mạnh, SP ít khả năng được lấp sớm **[GIẢ THUYẾT]**.

### Ledge — nhắc nhanh

**Ledge (gờ)** = các cột TPO cùng dừng PHẲNG ở một mức giá, cần **≥3 TPO** mới tính. Càng nhiều TPO trên gờ càng mạnh; gờ được test lại mà vẫn giữ thì càng đáng tin. Cơ chế: ai đó đặt tường limit ngay mức đó khiến giá cứ chạm là bật — Large Limit Orders nhìn bằng TPO.

### NỐI CẦU: Poor high / Poor low = Unfinished Business nhìn bằng TPO

Note thực chiến: phiên nào **đỉnh/đáy có từ 2 TPO trở lên nằm ngang** (đỉnh/đáy PHẲNG, không có tail) là **poor high / poor low — "đỉnh đáy đểu", dễ bị phá**, vì theo thuyết đấu giá, cực trị mà phẳng nghĩa là đấu giá tại đó CHƯA hoàn tất — không có phe phản ứng nào đá giá đi một cách dứt khoát. Note chốt: *một profile không thể hoàn thành nếu không có tail ở cực trị*.

Bạn đã học đúng khái niệm này rồi: **Unfinished Business** — ở footprint bạn soi Ô Bid×Ask tại đỉnh/đáy (đỉnh còn Bid khớp = chưa xong); ở TPO bạn chỉ cần nhìn HÌNH: đỉnh nhọn có tail = xong việc, đỉnh phẳng ≥2 TPO = chưa xong, giá có "món nợ" phải quay lại xử. Hai công cụ, một cơ chế đấu giá.

### 📊 Đọc chart thật

1. [tpo/images/keppler/p021-0.png](tpo/images/keppler/p021-0.png) — **Selling Tail**: chuỗi chữ **B đơn độc** treo trên đỉnh profile từ **1310.00** (nhãn trên hộp) xuống ~1309.00, bên dưới các hàng mới dày lên (ABM, ABLM…) từ 1308.50. Bracket B chọc lên vùng cao bất công và bị bán phản ứng đá xuống ngay — đuôi ~5 ô giá, đủ dài để tin.
2. [tpo/images/keppler/p020-0.png](tpo/images/keppler/p020-0.png) — **Buying Tail** đối xứng: đáy profile là chuỗi chữ **I** đứng một mình (~7 ô giá đóng khung *Buying Tail*), lên trên mới dày thành IJ rồi FGHIJ (ảnh này thang giá in mờ nên chỉ đọc cấu trúc, không đọc số).
3. [tpo/images/keppler/p025-0.png](tpo/images/keppler/p025-0.png) — **Single Print Within Profile Structure**: profile phiên ES; trong bracket E giá lao từ 1195.00 xuống 1187.00, các nhịp hồi sau không lần nào vượt lại 1193.25 → dải in đơn kẹp GIỮA profile quanh **1193.25–1194.50** (ngoặc đánh dấu trên ảnh, thang giá bên phải đọc rõ 1193.00–1195.00). Đây là minus development mẫu mực: kháng cự cho phần còn lại của phiên.
4. [tpo/images/keppler/p159-0.png](tpo/images/keppler/p159-0.png) — **Minus Development trên EURUSD**: hai khối phân phối dày (trên quanh 1.4180–1.4197, dưới quanh 1.4124–1.4148) nối nhau bằng một cột chữ đơn kéo dài quãng **~1.4160–1.4172** (ngoặc *Minus Development*). Giá rơi xuyên 12 pip không xây nổi giá trị — vùng đó thành kháng cự chờ retest.
5. [tpo/images/keppler/p157-0.png](tpo/images/keppler/p157-0.png) — **Bottom Ledge**: đáy profile EURUSD phẳng lì tại **1.4067** (nhãn trên ảnh, vòng tròn đánh dấu các chữ G-h-m cùng dừng một mức). Gờ hình thành ở bracket G và H, bốn bracket sau ("m") quay về test — vẫn giữ → đáy Value Area phiên đó, hỗ trợ được xác nhận.
6. [tpo/images/note/p003-0.png](tpo/images/note/p003-0.png) — single print trên nền tảng thực chiến (chart dark của note): indicator tự khoanh 2 hộp xanh **SP: 44812.5–45462.5 (27)** và **SP: 44387.5–44462.5 (4)** — số trong ngoặc là số ô giá in đơn; góc trên còn thấy 2 đường **IBH 46077 / IBL 45690.5**. Đúng bộ khung buổi này: IB + single print được máy đánh dấu sẵn, việc của trader là chờ giá quay về hộp SP.

### 🥇 Áp cho vàng MGC

- Vàng quanh tin (CPI, FOMC, Non-farm ~19:30 VN mùa hè) rất hay in minus development: cú chạy 1–2 bracket xuyên $5–10. Playbook chuẩn: KHÔNG đuổi nến tin — đánh dấu vùng single print, đặt cảnh báo giá (alert) tại mép vùng, chờ retest ở các bracket sau hoặc phiên sau.
- SL theo cấu trúc trên MGC: bên kia vùng single print + đệm vài tick (mỗi tick 0.1 = $1); vùng SP rộng quá thì bỏ kèo — tinh thần khớp nguyên tắc lọc SL theo ADR/ATR bạn đã học, còn ngưỡng cụ thể ">1/3 ATR ngày" là **con số người soạn tự đặt [GIẢ THUYẾT — tự kiểm khi backtest]**, không có trong nguồn nào và cũng KHÔNG trùng quy tắc SL 10–20% ADR đã học.
- Poor high/low của phiên Mỹ hôm trước là mục tiêu ưa thích của phiên Á/Âu hôm sau **[GIẢ THUYẾT — suy luận của người soạn, chưa backtest]**: ghi lại các đỉnh/đáy phẳng ≥2 TPO vào watchlist mỗi sáng.

*— Nguồn: Keppler tr.19–25, 154–160; Note tr.3–4, 9.*

---

## 5️⃣ Tổng kết thao tác: trình tự đọc "bản đồ phiên" mỗi tối (~5')

Đây là phần tổng hợp riêng của buổi học (không có nguyên văn trong sách) — gom 4 khối trên thành checklist chạy trên chart TPO vàng MGC mỗi tối:

**Trước phiên Mỹ (trước 19:20 VN):**
1. Mở composite profile của 1–3 phiên gần nhất. Đánh dấu: TPO-POC + VPOC từng phiên, các vùng single print CHƯA bị lấp, ledge, và poor high/low còn "nợ".
2. Ghi ATR(Daily) hiện tại → biết hôm nay còn bao nhiêu "quỹ đạn".

**Trong 60' đầu (19:20–20:20 VN nếu chọn mốc COMEX floor):**
3. Chờ bracket A+B đóng → kẻ IB High / IB Low. Đánh giá IB hẹp hay rộng so với các phiên trước → chọn bộ kịch bản (hẹp: chờ RE một phía; rộng: 3 kịch bản).

**Sau khi IB chốt:**
4. Theo dõi RE: phá phía nào, có acceptance không (TPO xếp dày ngoài IB) hay failed auction (chui lại trong IB)?
5. RE xác nhận → chiếu mục tiêu = biên IB ± độ rộng IB, đối chiếu quỹ ATR còn lại.
6. Giá chạy nhanh tạo single print → KHÔNG đuổi; đánh dấu vùng, đặt alert chờ retest, SL dự kiến bên kia vùng in đơn.
7. Cuối phiên: nhìn 2 cực trị — có tail dứt khoát chưa, hay để lại poor high/low? Ghi vào watchlist cho phiên sau.

Toàn bộ buổi 1 chỉ mới trả lời "thị trường ĐANG ở đâu, ai kiểm soát, vùng nào còn nợ" — chưa phải hệ thống entry. Entry cụ thể (kết hợp footprint/delta tại vùng TPO chỉ ra) là việc của buổi 3.

## ⚠️ Tổng hợp giả thuyết cần kiểm khi backtest

Kiến thức chuẩn Dalton/Keppler ở trên dùng thẳng. Các con số/quy tắc sau là **kinh nghiệm cá nhân tác giả note/TraderViet HOẶC suy luận riêng của người soạn bài** (ghi rõ từng dòng) — backtest trên dữ liệu MGC trước khi tin:

1. Failed auction: phá IB mà không giữ được động lượng **quá ~30 phút** → kỳ vọng test mặt kia của IB (phần "30 phút" là số của note).
2. **IB range ≤1%** (rất hẹp) → phiên sau xác suất cao breakout (số của note).
3. Single print hay nằm ở vùng thanh khoản (break S/R) và chứa lệnh limit chưa khớp → giá quay lại "fix" (kinh nghiệm tác giả note).
4. Fix single print cần **volume + thời gian**; vol to mà không lấp nổi SP → lực đẩy yếu, giá không đi tiếp (kinh nghiệm tác giả note).
5. Trong trend mạnh, SP ít khả năng được lấp sớm (kinh nghiệm tác giả note).
6. Mốc tính IB cho vàng (19:20 vs 20:30 VN) — bản thân việc chọn mốc là quy ước, phải test cả hai.
7. Cú phá IB đầu tiên của vàng (mốc 19:20) hay rơi vào bracket **20:20–21:30 VN** — suy luận của người soạn từ giờ US equities open, chưa backtest.
8. Poor high/low của phiên Mỹ hôm trước là mục tiêu ưa thích của phiên Á/Âu hôm sau — suy luận của người soạn, chưa backtest.
9. Bỏ kèo khi vùng SP rộng **>1/3 ATR ngày** — con số người soạn tự đặt, không có trong nguồn nào; đối chiếu thêm với quy tắc SL 10–20% ADR đã học trước khi dùng.

## ✅ Kiểm tra cuối buổi

**Câu 1.** Mở [tpo/images/keppler/p018-0.png](tpo/images/keppler/p018-0.png): (a) IB nằm từ đâu đến đâu? (b) Range extension xảy ra phía nào, ai kiểm soát cuối phiên? (c) Áp công thức chiếu mục tiêu từ độ rộng IB, mục tiêu giá là bao nhiêu?

**Câu 2.** TPO-POC và Volume-POC khác nhau ở cơ chế nào? Trên [tpo/images/keppler/p038-0.png](tpo/images/keppler/p038-0.png), hai POC nằm ở giá nào, và nếu hai POC của phiên vàng lệch nhau xa thì bạn nghiêng về POC nào làm nam châm chính — vì sao?

**Câu 3.** Một profile có đuôi mua dài 1 TPO và một profile khác có đuôi mua dài 8 TPO. Giá trị thông tin khác nhau ra sao, và cơ chế đấu giá nào khiến đuôi dài đáng tin hơn?

**Câu 4.** Đỉnh phiên hôm qua là 3 TPO nằm ngang phẳng lì (không có tail). Gọi tên cấu trúc này, nối nó với khái niệm nào đã học từ footprint, và nêu kỳ vọng giao dịch cho phiên tới.

**Câu 5.** Bạn chọn mốc IB 19:20 VN cho vàng MGC. Bracket A và B là những khung giờ nào? Nếu 20:35 VN giá phá đáy IB rồi 21:00 đã chui lại vào trong IB, theo buổi học hôm nay kịch bản kỳ vọng là gì (kèm nhãn độ tin cậy của quy tắc)?

<details><summary>Đáp án</summary>

**Câu 1.** (a) IB = 1302.75 → 1310.00 (hộp trên chart, độ rộng 7.25 điểm). (b) RE xuống dưới đáy IB — cột D-E in tiếp từ 1302.50 xuống 1300.00 và giữ dưới đó → người bán (OTF) kiểm soát. (c) Mục tiêu = IB Low − độ rộng IB = 1302.75 − 7.25 = **1295.50** (sau đó lọc bằng ADR còn lại của ngày).

**Câu 2.** TPO-POC đếm THỜI GIAN (hàng chữ dài nhất — mức giá được nhiều bracket ghé nhất); VPOC đếm KHỐI LƯỢNG (mức khớp vol lớn nhất). Trên ảnh: TPO-POC = 1339.50, VPOC = 1339.00 (đỉnh TPO-VA 1341.50 cũng cao hơn đỉnh Volume-VA 1341.00). Lệch xa → một cách nghiêng phổ biến (heuristic của người soạn, tự kiểm khi backtest) là ưu tiên VPOC làm nam châm chính vì volume là dấu chân tiền thật (giá "ngồi lâu" mà không có tiền thì giá trị đó rỗng); điều chắc chắn hơn: vùng nơi cả hai trùng nhau mới là S/R mạnh nhất.

**Câu 3.** Đuôi 1 TPO gần như vô nghĩa — ô cuối của range hầu như luôn là in đơn về mặt kỹ thuật, nên không nói lên phe phản ứng nào cả. Đuôi 8 TPO nghĩa là 8 mức giá liên tiếp bị từ chối nhanh đến mức không mức nào giữ được giá quá 1 bracket → phe mua phản ứng (OTF) vào mạnh và dứt khoát ở vùng thấp bất công → niềm tin của người mua tại vùng đó lớn, mức đuôi thành ứng viên hỗ trợ khi giá quay lại test.

**Câu 4.** Poor high (đỉnh dở dang): cực trị phẳng ≥2 TPO, không có selling tail = không có phe bán phản ứng đá giá đi dứt khoát = đấu giá tại đỉnh CHƯA hoàn tất. Đây chính là Unfinished Business nhìn bằng cấu trúc TPO thay vì ô Bid×Ask (ở footprint: đỉnh còn Bid khớp = chưa xong). Kỳ vọng: giá có "món nợ" ở đỉnh đó — xác suất cao sẽ quay lại phá/quét qua poor high trước khi đảo chiều thật; đưa mức đó vào watchlist làm mục tiêu/vùng canh phản ứng.

**Câu 5.** A = 19:20–19:50 VN, B = 19:50–20:20 VN → IB chốt lúc 20:20 VN. Cú phá đáy IB lúc 20:35 nhưng ~25–30 phút sau đã quay vào trong IB = failed auction (phá không có acceptance) → kỳ vọng giá đi test MẶT KIA (đỉnh IB). Lưu ý nhãn: cơ chế "phá thất bại → quay về vùng giá trị" là chuẩn auction theory, còn ngưỡng "không giữ quá ~30 phút" và kỳ vọng "test mặt kia" theo cách note diễn đạt là **[GIẢ THUYẾT — tự kiểm khi backtest]**; và bản thân mốc 19:20 là quy ước cần test song song với 20:30.

</details>

## 📋 Ảnh load khi dạy

Theo thứ tự giảng:

1. [tpo/images/tv/p008-1.png](tpo/images/tv/p008-1.png) — 3 tầng người chơi (TraderViet)
2. [tpo/images/keppler/p043-0.png](tpo/images/keppler/p043-0.png) — Fair Price Area (Keppler Fig 3.1)
3. [tpo/images/keppler/p009-0.png](tpo/images/keppler/p009-0.png) — TPO đầu tiên, O và \*
4. [tpo/images/keppler/p011-0.png](tpo/images/keppler/p011-0.png) — bracket A trọn vẹn 1302.75–1307.75
5. [tpo/images/keppler/p013-0.png](tpo/images/keppler/p013-0.png) — split profile A→E
6. [tpo/images/keppler/p036-0.png](tpo/images/keppler/p036-0.png) — composite + TPO-POC 1339.50
7. [tpo/images/keppler/p038-0.png](tpo/images/keppler/p038-0.png) — TPO-VA vs Volume-VA
8. [tpo/images/keppler/p018-0.png](tpo/images/keppler/p018-0.png) — IB 1302.75–1310.00 + RE xuống
9. [tpo/images/keppler/p019-0.png](tpo/images/keppler/p019-0.png) — 4 loại range extension
10. [tpo/images/tv/p016-0.png](tpo/images/tv/p016-0.png) — RE xuống ví dụ TraderViet
11. [tpo/images/note/p009-0.png](tpo/images/note/p009-0.png) — slide đấu giá thất bại
12. [tpo/images/keppler/p021-0.png](tpo/images/keppler/p021-0.png) — selling tail 1310.00
13. [tpo/images/keppler/p020-0.png](tpo/images/keppler/p020-0.png) — buying tail (đọc cấu trúc)
14. [tpo/images/keppler/p025-0.png](tpo/images/keppler/p025-0.png) — single print giữa profile 1193.25–1194.50
15. [tpo/images/keppler/p159-0.png](tpo/images/keppler/p159-0.png) — minus development EURUSD
16. [tpo/images/keppler/p157-0.png](tpo/images/keppler/p157-0.png) — bottom ledge 1.4067
17. [tpo/images/note/p003-0.png](tpo/images/note/p003-0.png) — SP boxes + IBH/IBL trên chart thực chiến
