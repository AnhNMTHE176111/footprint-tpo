# Chế độ ngưỡng "Không theo CORVEN": bóng = volume bất thường đo bằng thống kê (kế hoạch, 2026-11-24)

> Kế hoạch do Fable viết. Opus chạy đo và viết code theo đúng tài liệu này; chỗ nào tài liệu chưa nói thì hỏi lại, không tự đoán.
> Mọi thứ ở đây là **định nghĩa hiển thị** ("ô nào đáng nổ bóng"), **không phải lợi thế giao dịch đã kiểm định**.
> Hai điều cấm xuyên suốt: (1) không dùng giá chạy sau khi bóng nổ, ở bất cứ bước nào; (2) không lấy chart CORVEN làm đích. CORVEN chỉ được đem ra so ở vòng cuối, để tham khảo.

## 0. Tóm tắt

- Hai loại bóng: **chấm Bid/Ask** (volume một bên của một ô giá) và **Big Trade** (lệnh đơn lớn nhất của một ô giá).
- "Bất thường" = giá trị nằm ở phần đuôi lớn của một **tập tham chiếu chỉ gồm nến đã đóng trước đó**. Năm cách dựng tập tham chiếu được đem ra đo (mục 2 và 3).
- Chọn cách nào là do **số đo**, theo các ngưỡng đạt / không đạt viết sẵn ở mục 4, trước khi nhìn kết quả.
- Vòng 1 chỉ chạy Python trên dữ liệu có sẵn, chưa đụng C# (mục 5). Các vòng sau ở mục 6.

Số đã xem nhanh khi lập kế hoạch (để hiểu vì sao cần tham chiếu theo giờ; Opus đo lại đầy đủ ở bước 1):

| Phân vị 99 của volume một bên (ô có giao dịch), theo giờ UTC | Giờ thấp nhất | Giờ cao nhất | Cùng một giờ, giữa các ngày (thấp nhất / trung vị / cao nhất) |
|---|---|---|---|
| GC M1 | 13 (phiên Á) | 24 (14 giờ) | 14 giờ: 14 / 21 / 39 |
| GC M15 | 30 | 63 | 14 giờ: 36 / 54 / 136 |
| NQ M1 | 10 | 50 (19 giờ) | 14 giờ: 24 / 35 / 59 |
| NQ M15 | 26 | 155 (19 giờ) | 14 giờ: 66 / 110 / 175 |

Đọc: giữa các giờ chênh 2 đến 6 lần, nên ngưỡng cố định là sai. Nhưng cùng một giờ, giữa các ngày cũng chênh 2,5 đến 4 lần, nên "cùng giờ các ngày trước" một mình cũng chưa chắc đủ; vì vậy có phương án lai.

Một hướng đã kiểm và **bỏ ngay**: chuẩn hóa Big Trade theo cỡ lệnh trung bình (volume / số lệnh). Cỡ lệnh trung bình gần như hằng số (GC 1,12 / 1,13 / 1,12 và NQ 1,08 / 1,09 / 1,07 hợp đồng ở phiên Á / Âu / Mỹ), nên nó không mang thông tin phiên.

## 1. Quy ước chung cho mọi phương án

**Đơn vị xét.** Khung của chart (M1, M5, M15, M30, H1). Một *ô* = (nến, mức giá theo tick). Mỗi ô có hai *giá trị bên*: Bid (sell chủ động) và Ask (buy chủ động). Với Big Trade, giá trị của ô = lệnh đơn lớn nhất của ô đó.

**Mẫu.** Chỉ lấy giá trị **lớn hơn 0**. Bid và Ask gộp chung một tập tham chiếu (bước 1 kiểm lại rằng hai bên có phân phối gần như nhau; nếu lệch quá 10% ở phân vị 99 thì báo, không tự tách).

**Tập tham chiếu.** Chỉ gồm các **nến đã đóng trước nến đang xét**. Nến đang chạy dùng tập tham chiếu của các nến đã đóng. Mỗi nến đóng nộp dữ liệu đúng một lần.

**Hai cách nói "hiếm cỡ nào" (mức danh nghĩa):**
- *Theo ô*: tỉ lệ p. "Ô nổ khi nó thuộc nhóm p lớn nhất của tập tham chiếu." Số được vượt: `K = floor(p × số mẫu)`. Cần `số mẫu ≥ 5 / p`.
- *Theo nến*: mật độ λ. "Trung bình λ ô vượt ngưỡng mỗi nến." `K = floor(λ × số nến trong tập tham chiếu)`. Cần ít nhất 5 nến và `K ≥ 1`.

**Ngưỡng (dùng cho mọi phương án kiểu phân vị).** Sắp tập tham chiếu giảm dần. `ngưỡng = giá trị lớn thứ K + 1`. Ô nổ khi giá trị **lớn hơn hẳn** ngưỡng. Như vậy trong chính tập tham chiếu có nhiều nhất K giá trị vượt; giá trị bằng nhau không gây vượt quá mức danh nghĩa. Volume là số nguyên nên điều này tương đương "ngưỡng nguyên nhỏ nhất t sao cho số mẫu ≥ t không quá K".

**Chưa đủ tập tham chiếu.** Trả về "chưa có ngưỡng" (không nổ gì). Ở vòng 1 đo riêng tỉ lệ nến rơi vào tình trạng này; phương án dự phòng chỉ ghép ở vòng 2.

**Từ "vượt ngưỡng" tới "chấm vẽ ra".** Tách hai lớp và báo cáo cả hai:
1. *Vượt ngưỡng thô*: mọi giá trị bên lớn hơn hẳn ngưỡng.
2. *Chấm sau gộp*: trong các giá trị vượt, chỉ giữ giá trị lớn hơn hẳn cùng bên của mọi tick khác trong ±w tick cùng nến, `w = max(4, floor(biên độ trung bình / 6 + 0,5))`, biên độ trung bình lấy trên N nến trước với `N = min(20, max(5, floor(120 / số phút một nến + 0,5)))` (đúng `UnifiedDots.Window` và `BaselineWindow.BarsFor` đang có). Đây là gộp các ô sát nhau thành một chấm, thuần hình học, không nhìn tương lai.

Chế độ mới **không** có luật che chấm xanh gần chấm đỏ (đó là bắt chước cách CORVEN vẽ) và **không** có sàn cố định ở vòng 1 (sàn chỉ thêm ở vòng 2 nếu số đo "chấm tí hon" ở mục 4 không đạt).

**Làm tròn.** `floor(x + 0,5)`, không dùng làm tròn về số chẵn.

**Giờ và phiên.** UTC. Phiên: Á 22:00–07:00, Âu 07:00–13:30, Mỹ 13:30–22:00 (`bt_common.ses_of`). *Ngày giao dịch* = ngày của (giờ nến + 2 giờ), tức bắt đầu 22:00 UTC. *Khung giờ trong ngày* (dùng cho phương án cùng giờ): chia ngày UTC thành các khoảng rộng `W = max(30, số phút một nến)` phút; chỉ số khoảng = `floor(phút trong ngày UTC / W)`.

**Tách dữ liệu để khỏi tự lừa.** Mọi ngưỡng đều chỉ nhìn quá khứ nên con số nào cũng là "ngoài mẫu" theo nghĩa từng nến. Nhưng việc *chọn tham số* thì không. Vì vậy chia theo ngày: **đoạn chọn** và **đoạn kiểm**. Tham số chọn trên đoạn chọn, đoạn kiểm chỉ để xác nhận.
- Chấm GC: chọn 11/08 → 04/10, kiểm 05/10 → 09/11.
- Chấm NQ: chọn 14/09 → 25/10, kiểm 26/10 → 24/11.
- Hai lần đổi giờ (châu Âu 25/10, Mỹ 01/11) rơi vào đoạn kiểm; đây là cố ý, để thử phương án cùng giờ.

## 2. Chấm Bid/Ask: năm phương án ứng viên + hai mốc đối chứng

Tên trong ngoặc là tên cấu hình dùng trong script.

### 2.1 Phân vị cuốn (`cuon`)

- **Ý:** ô bất thường so với những gì vừa giao dịch trong T phút gần nhất.
- **Tập tham chiếu:** mọi giá trị bên > 0 của `n = max(5, floor(T / số phút một nến + 0,5))` nến đã đóng gần nhất.
- **Tham số:** T ∈ {60, 120, 240, 480} phút; mức danh nghĩa p ∈ {2%, 1%, 0,5%, 0,2%} hoặc λ ∈ {0,25; 0,5; 1; 2}.
- **Dữ liệu lịch sử cần:** T phút. Dùng được gần như ngay sau khi mở chart.
- **Khung và phiên:** tự theo khung vì tập tham chiếu là ô của chính khung đó. Theo phiên: bám tốt ở M1/M5; ở M30/H1 cửa sổ 5 nến dài 2,5 đến 5 giờ nên sẽ trễ qua phiên, và mức p nhỏ không đủ mẫu. Điểm yếu đoán trước: nến đầu phiên Mỹ (tham chiếu còn là phiên Âu).
- **Chi phí C#:** một mảng đếm theo giá trị nguyên (0…4095, giá trị lớn hơn thì dồn vào ô cuối) + hàng đợi n nến để trừ ra khi nến cũ rời cửa sổ. Mỗi nến đóng: cộng/trừ vài chục đến vài trăm số. Lấy ngưỡng: quét mảng từ trên xuống, một lần mỗi nến. Rất rẻ.

### 2.2 Cùng khung giờ, K ngày trước (`cung_gio`)

- **Ý:** 21 giờ tối nay so với 21 giờ của các ngày trước, không so với phiên Á.
- **Tập tham chiếu:** mọi giá trị bên > 0 của các nến đã đóng nằm trong **cùng khung giờ trong ngày** (rộng W), ở K lần xuất hiện gần nhất của khung giờ đó **trước hôm nay**. Biến thể "lân cận": gộp thêm khung giờ liền trước và liền sau (±1), để chịu được đổi giờ mùa và lệch vài phút.
- **Tham số:** K ∈ {5, 10, 20}; lân cận ∈ {không, ±1}; cùng các mức p và λ. Cần ít nhất 3 lần xuất hiện, nếu không thì "chưa có ngưỡng".
- **Dữ liệu lịch sử cần:** K ngày giao dịch đã nạp trên chart. Ba ngày đầu chart không có ngưỡng.
- **Khung và phiên:** theo phiên tốt nhất về lý thuyết, kể cả nến đầu phiên và H1. Điểm yếu đoán trước: hôm nay sôi động hoặc vắng hơn hẳn các ngày trước (số ở mục 0: cùng giờ chênh 2,5–4 lần giữa các ngày) thì nổ quá nhiều hoặc không nổ; tuần sau đổi giờ bị lệch một tiếng; ngày lễ.
- **Chi phí C#:** mỗi khung giờ (tối đa 48) giữ K mảng đếm thưa + một mảng tổng. Ngưỡng tính một lần khi bước sang khung giờ mới. Rẻ hơn cả phương án cuốn. Bộ nhớ: 48 × K danh sách nhỏ.

### 2.3 Lai: bội số đo được theo giờ (`lai`)

- **Ý:** tách hai thứ. *Mặt bằng hiện tại* (hôm nay đang đông hay vắng) lấy từ các nến vừa đóng; *hình dạng đuôi* (ô lớn gấp mấy lần mặt bằng thì mới hiếm) lấy từ cùng khung giờ các ngày trước. Thực chất là thay bội số 2,0 / 2,4 / 2,8 (fit theo CORVEN) bằng một bội số **đo ra từ dữ liệu**, theo từng khung giờ.
- **Công thức:** với mỗi nến b, mặt bằng `L(b)` chỉ tính từ các nến đóng trước b. Mỗi giá trị bên v của nến b có tỉ số `u = v / L(b)`. Tập tham chiếu = các tỉ số u của cùng khung giờ trong K lần xuất hiện trước (như 2.2). Ngưỡng tỉ số = giá trị lớn thứ K + 1. Ô của nến đang xét nổ khi `v / L(nến đang xét)` lớn hơn hẳn ngưỡng tỉ số.
- **Tham số:** mặt bằng L ∈ {trung bình của trung vị volume mỗi ô trên N nến trước (`CellBigBaseline.TryGetMedian`, N theo `BaselineWindow`); trung bình của volume trung bình mỗi ô trên N nến trước}; K ∈ {5, 10, 20}; biến thể "một ngày cuốn" (tập tham chiếu = tỉ số của 1.380 phút gần nhất thay vì cùng khung giờ), để biết phần "cùng giờ" có thật sự cần không; cùng các mức p và λ.
- **Dữ liệu lịch sử cần:** như 2.2 cho bản cùng giờ; một ngày cho bản một ngày cuốn. Nến chưa có mặt bằng (dưới 5 nến) không nộp tỉ số.
- **Khung và phiên:** mặt bằng lo phần phiên và phần "hôm nay khác hôm qua"; đuôi lo phần hình dạng. Điểm yếu đoán trước: ở M1 mặt bằng theo trung vị chỉ 2–3 hợp đồng nên tỉ số thô.
- **Chi phí C#:** như 2.2 nhưng lưu tỉ số (số thực). Để C# khớp Python từng chấm, vòng 3 sẽ lượng tử hóa tỉ số thành số nguyên (ví dụ `floor(16 × u)`); vòng 1 để số thực.

### 2.4 Điểm lệch chuẩn hóa theo trung vị, trên logarit volume (`z_log`)

- **Ý:** cách chuẩn trong sách (NIST): một giá trị là ngoại lai khi cách trung vị quá z lần độ phân tán bền vững.
- **Công thức:** `x = ln(v)`. Trên tập tham chiếu của 2.1 (cửa sổ T): `m = trung vị(x)`, `d = trung vị(|x − m|)`. `z = (x − m) / (1,4826 × d)`. Nổ khi `z ≥ z0`. Nếu `d = 0` thì "chưa có ngưỡng".
- **Tham số:** T ∈ {120, 240}; z0 ∈ {2,5; 3,0; 3,5}. Mức danh nghĩa nếu logarit volume có phân phối chuẩn: 0,62% / 0,135% / 0,023%.
- **Điểm yếu đoán trước:** volume là số nguyên nhỏ (trung vị 2 ở GC M1), `d` hay bằng 0 hoặc nhảy bậc; đuôi thật không theo phân phối chuẩn nên tỉ lệ nổ thật có thể lệch xa mức danh nghĩa. Đưa vào để đo cho rõ, không kỳ vọng thắng.
- **Chi phí C#:** dùng chung mảng đếm của 2.1 (trung vị và độ phân tán đọc từ mảng đếm). Rẻ.

### 2.5 Kỷ lục theo nến (`ky_luc`)

- **Ý:** không hỏi "ô này hiếm cỡ nào trong các ô", mà hỏi "nến này có ô lớn hơn ô lớn nhất của hầu hết các nến trước không".
- **Công thức:** mỗi nến đã đóng nộp **một** số: giá trị bên lớn nhất của nến. Tập tham chiếu = số đó của n nến trước. `r = max(1, floor(q × (n + 1) + 0,5))`. `ngưỡng = giá trị lớn thứ r`. Ô nổ khi giá trị **lớn hơn hẳn** ngưỡng.
- **Mức danh nghĩa:** nếu các nến "đổi chỗ cho nhau được" thì xác suất một nến có ít nhất một ô nổ đúng bằng `r / (n + 1)`, **không cần giả định gì về phân phối**. Đây là lý do đưa phương án này vào: mức danh nghĩa kiểm được chính xác.
- **Tham số:** tập n nến lấy kiểu cuốn (T ∈ {120, 240, 480} phút, tối thiểu 8 nến) hoặc kiểu cùng khung giờ (K ∈ {10, 20} lần xuất hiện, n = số nến trong đó); q ∈ {0,5; 0,25; 0,1}.
- **Khung và phiên:** số nến có chấm tự bằng nhau ở mọi khung theo cách dựng. Điểm yếu đoán trước: một nến tin tức rất đông sẽ có rất nhiều ô vượt (không giới hạn số chấm trong một nến ngoài bước gộp).
- **Chi phí C#:** rẻ nhất (một số mỗi nến; cùng cấu trúc với `BigTradeAdaptive` đang có).

### 2.6 Hai mốc đối chứng (chỉ để so trên cùng thước đo, không phải ứng viên)

- **Luật đang chạy** (`UnifiedDots`): bộ Không sót và bộ Ít nhiễu, sàn 9, có luật che. Lấy từ `../adaptive_2026-11-24/dot_rule.py`.
- **Phần trăm volume của nến** (kiểu ATAS Cluster Search): ô nổ khi giá trị bên ≥ x% tổng volume của chính nến đó, x ∈ {5, 10, 15}. Chỉ tính trên nến đã đóng. Không là ứng viên vì trên nến đang chạy tổng volume còn tăng, chấm có thể hiện rồi mất.

## 3. Big Trade: bốn phương án ứng viên + hai mốc đối chứng

**Dữ liệu là điểm nghẽn.** Lịch sử của nền tảng không có lệnh đơn (cột `max_one_trade` gần như toàn 0). Nguồn duy nhất là nhật ký của indicator (`%APPDATA%/OrderFlowBubbles/bigtrade-log`), nạp bằng `bt_common.load_m1` / `to_tf`:
- GC: 31/08 → 23/09 liền mạch, 16 phiên, 22.948 nến M1 (`GC`).
- NQ: 25/10 → 02/11 liền mạch, 6 phiên, 8.340 nến M1 (`NQ`).
- GC sống 09/11 → 24/11, **đứt quãng** (5.517 nến M1; mỗi ngày chỉ 19 đến 937 nến) (`GClive`).

Hệ quả phải ghi vào mọi bảng: NQ chỉ có 6 phiên nên phương án "cùng giờ K ngày" chỉ thử được với K ≤ 5 và kết quả yếu; nhật ký sống đứt quãng nên trong thực tế phương án cùng giờ có thể không bao giờ đủ dữ liệu (bước 6 đo đúng điều này).

Giá trị của ô = lệnh đơn lớn nhất của ô (`mot`), chỉ ô có `mot > 0`. Quy ước ngưỡng, mức danh nghĩa, "chưa có ngưỡng" giống mục 1.

**Từ "vượt ngưỡng" tới "vòng vẽ ra".** Thô: mọi ô có `mot` lớn hơn hẳn ngưỡng. Sau gộp: duyệt `mot` giảm dần (bằng nhau thì tick thấp trước), bỏ ô cách ô đã giữ ≤ g tick, `g = max(2, floor(biên độ trung bình / 8 + 0,5))` (đúng `BigTradeAdaptive.Select` và `MergeTicks`). Chế độ mới **không** giới hạn số vòng mỗi nến và **không** có sàn ở vòng 1; đo phân phối số vòng mỗi nến rồi mới quyết.

### 3.1 Phân vị cuốn (`cuon`)
Như 2.1 trên `mot`. T ∈ {60, 120, 240, 480}; p ∈ {1%, 0,5%, 0,2%, 0,1%}; λ ∈ {0,25; 0,5; 1}. Nến không có số liệu lệnh đơn **không** được nộp (không nộp số 0) và không tính vào số nến của cửa sổ; cửa sổ đếm theo số nến có số liệu.
Chi phí C#: như 2.1, giá trị dồn ở 4095.

### 3.2 Cùng khung giờ, K ngày trước (`cung_gio`)
Như 2.2 trên `mot`. GC: K ∈ {5, 10}; NQ: K ∈ {3, 5}. Lân cận ∈ {không, ±1}. Cần nhật ký của các ngày trước nên phụ thuộc việc người dùng có để chart chạy hay không.

### 3.3 Kỷ lục theo nến (`ky_luc`)
Như 2.5: mỗi nến có số liệu nộp `mot` lớn nhất của nến; ngưỡng = giá trị lớn thứ r trong n nến trước; `r / (n + 1)` = xác suất danh nghĩa một nến có vòng. T ∈ {120, 240, 480} (tối thiểu 8 nến); q ∈ {0,5; 0,25; 0,1; 0,05}. Khác luật đang chạy ở chỗ: mỗi nến nộp một số (không phải K số lớn nhất), mức danh nghĩa là xác suất kiểm được, không phải mật độ 0,96 vòng/nến lấy từ chart CORVEN, không sàn, không giới hạn 3 vòng.

### 3.4 Lai với mặt bằng lấy từ footprint (`lai`)
- **Ý:** lệnh đơn không có trong lịch sử, nhưng volume mỗi ô thì có. Nếu "lệnh đơn / mặt bằng volume" có đuôi ổn định giữa phiên và giữa ngày, thì chỉ cần nhớ **một bội số** (đo từ nhật ký), còn mặt bằng lấy từ lịch sử nền tảng. Khi đó mở chart là có ngưỡng ngay, không phải chờ 5 nến sống, và không phụ thuộc nhật ký liền mạch.
- **Công thức:** `u = mot / L(b)`, L(b) từ footprint của các nến đóng trước b. Ngưỡng tỉ số = giá trị lớn thứ K + 1 của tập tỉ số tham chiếu. Vòng nổ khi `mot / L(nến đang xét)` lớn hơn hẳn ngưỡng tỉ số.
- **Tham số:** L ∈ {trung bình của trung vị volume mỗi ô trên N nến; trung bình của volume trung bình mỗi ô trên N nến; căn bậc hai của volume trung bình mỗi nến trên N nến; phân vị 90 của giá trị bên trên cửa sổ 120 phút}. Tập tỉ số tham chiếu: toàn bộ nhật ký trước đó (tích lũy) hoặc một ngày cuốn. Cùng các mức p, λ.
- **Việc phải đo trước khi tin (bước 5):** với mỗi L, phân vị 99 của u có ổn định giữa (ngày × phiên) không. Nếu không L nào ổn định hơn chính `mot` thô thì bỏ phương án này.
- **Chi phí C#:** mặt bằng đã có sẵn (`CellBigBaseline`); thêm một hàng đợi tỉ số. Rẻ. Cần ghép footprint với nhật ký theo (giờ nến, giá).

### 3.5 Hai mốc đối chứng
- Ngưỡng cố định 10 hợp đồng.
- Luật thích nghi đang chạy (mật độ 1,0 · sàn 5 · gộp · tối đa 3), từ `../adaptive_2026-11-24/bt_rule.py`.

## 4. Tiêu chí đánh giá (viết trước khi đo)

Không tiêu chí nào dùng giá sau đó, không tiêu chí nào dùng chart CORVEN.

### 4.1 Nổ đúng mức danh nghĩa (độ khớp)

Với mỗi cấu hình: `tỉ số khớp = tỉ lệ nổ thực / mức danh nghĩa`, tính trên vượt ngưỡng thô.
- Kiểu p: tỉ lệ nổ thực = số giá trị vượt / số giá trị bên > 0 (của các nến đã có ngưỡng).
- Kiểu λ: số giá trị vượt / số nến đã có ngưỡng.
- Kỷ lục: số nến có ít nhất một giá trị vượt / số nến đã có ngưỡng, so với `r / (n + 1)`.
- `z_log`: so với mức danh nghĩa của phân phối chuẩn.

Vì giá trị nguyên bằng nhau làm ngưỡng nhảy bậc, báo thêm *mức danh nghĩa đạt được* = trung bình (theo nến) của tỉ lệ mẫu tham chiếu thật sự lớn hơn ngưỡng; tỉ số khớp chính thức tính so với mức danh nghĩa đạt được.

| Mã tiêu chí | Đo gì | Đạt khi |
|---|---|---|
| Khớp chung | Tỉ số khớp, toàn đoạn kiểm | 0,8 – 1,25 |
| Khớp theo phiên | Tỉ số khớp riêng Á, Âu, Mỹ | cả ba trong 0,67 – 1,5; phiên cao nhất / thấp nhất ≤ 1,8 |
| Khớp theo giờ | Tỉ số khớp từng giờ UTC (24 giờ) | ít nhất 20 / 24 giờ trong 0,5 – 2; ghi giờ tệ nhất |
| Khớp theo ngày | Tỉ số khớp từng ngày giao dịch | phân vị 10 và 90 của các ngày nằm trong 0,5 – 2; ghi ngày tệ nhất |

### 4.2 Độ đều (sau gộp, thứ người dùng nhìn thấy)

- Chấm/nến và chấm/giờ: toàn bộ, theo phiên, theo từng giờ UTC.
- Tỉ lệ nến không có chấm nào; phân vị 50 / 95 / lớn nhất của số chấm trong một nến; tỉ lệ nến có hơn 5 chấm.
- Nến đầu phiên: số chấm trung bình ở nến mở lúc 22:00, 07:00, 13:30 và 14:30 UTC so với trung bình của phiên đó.
- Tỉ lệ đỏ / xanh (kỳ vọng gần 50 / 50 vì không còn luật che; lệch quá 60 / 40 thì báo).
- Tương quan giữa (số chấm trong ngày) và (volume ngày / volume trung bình 10 ngày trước): **chỉ báo cáo, không có đạt / không đạt**. Con số này trả lời câu "ngày sôi động có nhiều bóng hơn không" — phương án cuốn sẽ gần 0, phương án cùng giờ sẽ dương. Đây là lựa chọn phải đem hỏi người học ở vòng 2.

| Mã tiêu chí | Đạt khi |
|---|---|
| Không trống phiên Á, không dồn phiên Mỹ | chấm/nến phiên cao nhất / thấp nhất ≤ 2,0 (kiểu λ và kỷ lục); kiểu p chỉ báo cáo |
| Nến đầu phiên | ≤ 3 lần trung bình phiên |
| Đều giữa các khung | chấm/nến lớn nhất / nhỏ nhất trên M1…H1 ≤ 2,5 (kiểu λ và kỷ lục); kiểu p chỉ báo cáo |

Kiểu p **biết trước** là số chấm mỗi nến tăng theo khung (nến H1 có nhiều ô hơn nến M1 hàng chục lần). Đó là tính chất của định nghĩa "1 trong 100 ô", không phải lỗi; bảng phải cho thấy tăng bao nhiêu để quyết kiểu nào làm mặc định.

### 4.3 "Không bỏ sót" và "không nhiễu": định nghĩa đo được

Cần một danh sách "ô mà ai nhìn lại cũng bảo là lớn bất thường". Dựng bằng **hai thước nhìn lại**, cấu trúc khác nhau để không thiên vị phương án nào. Hai thước này **dùng dữ liệu volume của cả trước và sau ô đó**; chúng chỉ để chấm điểm trong nghiên cứu, **không bao giờ** nằm trong indicator, và không dùng giá.

- **Thước cùng giờ:** tập so sánh = giá trị bên > 0 của cùng khung giờ trong ngày, trên 11 ngày giao dịch quanh ngày đó (5 trước, chính nó, 5 sau; ở hai đầu dữ liệu lấy những ngày có, tối thiểu 6).
- **Thước quanh nó:** tập so sánh = giá trị bên > 0 của mọi nến cách nến đó không quá `H = max(60, 4 × số phút một nến)` phút về cả hai phía, kể cả chính nó.

Với mỗi cấu hình, gọi p̂ là tỉ lệ nổ thực (theo ô) của nó trên đoạn đang xét. Trên mỗi thước:
- *cực trị chặt* = ô thuộc nhóm p̂ / 2 lớn nhất của tập so sánh;
- *cực trị lỏng* = ô thuộc nhóm 2 × p̂ lớn nhất.

So ở cùng mức p̂ để không thưởng cho phương án nổ nhiều.

Một ô được coi là **đã được nổ** khi nó vượt ngưỡng thô, hoặc cùng nến, cùng bên có chấm sau gộp cách nó ≤ w tick (bị gộp vào chấm lớn hơn bên cạnh thì không tính là sót). Báo cả hai con số.

| Mã tiêu chí | Đo gì | Đạt khi |
|---|---|---|
| Không sót ô lớn nhất ngày | 20 giá trị bên lớn nhất của mỗi ngày giao dịch (ở khung đó): tỉ lệ được nổ | ≥ 99% |
| Không sót ô lớn nhất phiên | 5 giá trị bên lớn nhất của mỗi (ngày × phiên): tỉ lệ được nổ | ≥ 97% |
| Không sót cực trị rõ ràng | ô là cực trị chặt trên **cả hai** thước: tỉ lệ được nổ | ≥ 97% |
| Không nhiễu | chấm sau gộp **không** là cực trị lỏng trên **cả hai** thước: tỉ lệ trong tổng số chấm | ≤ 5% |
| Không chấm tí hon | chấm có giá trị ≤ 3 hợp đồng: tỉ lệ trong tổng số chấm (báo thêm mức ≤ 5) | ≤ 2% |

Ngoài ra báo cáo (không đạt / không đạt): trong số chấm, bao nhiêu phần chỉ là cực trị trên thước cùng giờ, bao nhiêu phần chỉ trên thước quanh nó. Đây là vùng "tùy định nghĩa"; Fable đọc số này để quyết ở vòng 2.

Nói thẳng giới hạn: "không bỏ sót" ở đây nghĩa là **không sót ô cực trị thống kê theo hai thước trên**. Nó không nói gì về việc ô đó có ý nghĩa giao dịch.

### 4.4 Ca biên (mỗi ca một dòng trong bảng ca biên)

1. **Đầu chart:** số nến đầu tiên chưa có ngưỡng; tỉ lệ nến chưa có ngưỡng trên toàn dữ liệu.
2. **Phụ thuộc lượng lịch sử đã nạp:** tính lại chấm của 5 ngày giao dịch cuối khi chỉ nạp 3, 7, 15 ngày cuối so với nạp toàn bộ; báo tỉ lệ chấm trùng (số chấm chung / số chấm hợp). Đạt khi ≥ 0,95 với 15 ngày.
3. **Sau nghỉ cuối tuần:** 20 nến đầu sau 22:00 UTC chủ nhật: chấm/nến và tỉ số khớp so với 20 nến đầu của các ngày khác.
4. **Sau giờ nghỉ hằng ngày** (21:00–22:00 UTC) và khung giờ thưa quanh đó: tỉ lệ nến chưa có ngưỡng, chấm/nến.
5. **Tuần sau đổi giờ:** 26/10 → 30/10 (châu Âu đã đổi, Mỹ chưa) và 02/11 → 06/11: tỉ số khớp theo giờ, so với hai tuần trước đó. Đây là bài thử chính của biến thể lân cận ±1.
6. **Đổi hợp đồng / volume tăng dần:** chạy NQ trên **toàn bộ** file từ 26/08 (trước 14/09 NQZ26 chưa là hợp đồng chính, volume thấp hơn rất nhiều): tỉ số khớp theo ngày trong khoảng 07/09 → 25/09, và số ngày cần để tỉ số khớp theo ngày quay về 0,5 – 2.
7. **Nến mỏng:** nến có ≤ 3 ô có giao dịch: tỉ lệ nến như vậy có chấm; giá trị của các chấm đó.
8. **Ngày lễ / ngày rất vắng:** ngày có volume < 50% trung bình 10 ngày trước: tỉ số khớp, chấm/nến; và ngày liền sau.

### 4.5 Cách chốt sau vòng 1

Một cấu hình vào vòng 2 khi đạt mọi tiêu chí có ngưỡng ở 4.1 và 4.3 trên **đoạn kiểm**, cho **cả GC lẫn NQ**, ở **ít nhất M1, M5, M15**. Nếu không cấu hình nào đạt hết: giữ ba cấu hình trượt ít tiêu chí nhất, ghi rõ trượt cái gì. Không nới ngưỡng đạt sau khi đã xem số; muốn nới phải ghi lý do thành một mục riêng.

## 5. Vòng 1: việc đo cụ thể (Opus chạy)

Thư mục: `quantower-orderflow-indicator/research/stat_anomaly_2026-11-24/`. Python, `PYTHONIOENCODING=utf-8`. Chỉ Python, **chưa sửa C#**. Không commit, không push. File `.pkl` và `__pycache__/` đã được `.gitignore` của thư mục chặn.

Mỗi script in bảng ra màn hình và ghi `out_r1_*.csv`. Mọi bảng có cột `ma` (GC / NQ), `khung` (1, 5, 15, 30, 60), `doan` (chon / kiem / tat_ca).

### Bước 0. `sa_common.py` (dùng chung)

- Nạp bảng ô `F_{GC,NQ}_m{1,5,15,30,60}.pkl` và bảng nến `S_…` từ `../nq_calib_2026-11-24/` (cột F: t, tk, bid, ask, vol; S: med, mean, hi, lo, nl, tot, rng). Không dùng cột `B_med` có sẵn; tự tính lại mặt bằng theo N của `BaselineWindow`.
- Hàm: phiên (`bt_common.ses_of`), ngày giao dịch, khung giờ trong ngày (W), đoạn chọn / kiểm theo mục 1, làm tròn nửa lên, cửa sổ gộp w, khoảng gộp g.
- Hàm ngưỡng "lớn thứ K + 1, lớn hơn hẳn" trên mảng đếm số nguyên; một bản cho số thực (tỉ số).
- Riêng ca biên 6: dựng thêm bảng NQ M1 và M5 từ toàn bộ file `fp_NQZ26_XCME_Time_20260826-20261124_90d.csv` (không cắt 14/09), theo đúng cách của `../nq_calib_2026-11-24/load.py`.

### Bước 1. `sa_profile.py` → `out_r1_profile.csv`, `out_r1_profile.txt`

Mô tả dữ liệu, chưa có luật nào. Mỗi (mã, khung, giờ UTC): số nến; số ô mỗi nến; số giá trị bên > 0; phân vị 50 / 90 / 99 / 99,5 / 99,9 của giá trị bên (gộp Bid + Ask); phân vị 99 riêng Bid và riêng Ask; phân vị 99 tính riêng từng ngày rồi lấy phân vị 10 / 50 / 90 qua các ngày. Thêm một bảng tóm tắt theo phiên.
Mục đích: xác nhận gộp Bid + Ask được; biết số mẫu mỗi nến để biết mức p nào giải được ở khung nào.

### Bước 2. `sa_dot_rules.py` + `sa_dot_selftest.py`

- Cài năm phương án mục 2 và hai mốc đối chứng. Mỗi phương án có **bản chuẩn từng nến** (vòng lặp thẳng, cấu trúc dữ liệu đúng như C# sẽ làm: mảng đếm, hàng đợi) và có thể có bản nhanh.
- `sa_dot_selftest.py`: (a) ví dụ nhỏ tự dựng cho từng phương án, kết quả tính tay ghi trong script; (b) bản nhanh = bản chuẩn từng chấm trên GC M5 và NQ M15, 10 ngày giao dịch, mỗi phương án một cấu hình; (c) kiểm không nhìn tương lai: cắt dữ liệu tại một nến bất kỳ rồi chạy lại, mọi ngưỡng trước điểm cắt phải y hệt. In "ĐẠT" / "TRƯỢT" từng mục vào `out_r1_dot_selftest.txt`.

### Bước 3. `sa_dot_eval.py` → ba bảng

Lưới: 2 mã × 5 khung × các cấu hình liệt kê ở mục 2 (đủ mọi tổ hợp tham số đã nêu) × 3 đoạn.

- `out_r1_dot_calib.csv`: mỗi dòng = (cấu hình, phạm vi), phạm vi ∈ {tất cả, phiên Á / Âu / Mỹ, giờ 0…23}. Cột: số nến, số nến chưa có ngưỡng, số giá trị bên > 0, số vượt thô, mức danh nghĩa, mức danh nghĩa đạt được, tỉ lệ nổ thực, tỉ số khớp, ngưỡng trung vị. Thêm các cột tóm tắt theo ngày ở dòng "tất cả": phân vị 10 / 50 / 90 của tỉ số khớp từng ngày, ngày tệ nhất.
- `out_r1_dot_density.csv`: sau gộp, mọi con số của mục 4.2 (kể cả nến đầu phiên, đỏ / xanh, tương quan với volume ngày).
- `out_r1_dot_summary.csv`: mỗi cấu hình một dòng trên đoạn kiểm, mỗi tiêu chí có ngưỡng ở 4.1 và 4.2 một cột ĐẠT / TRƯỢT kèm con số.

### Bước 4. `sa_dot_oracle.py` → `out_r1_dot_oracle.csv`

Để khỏi tốn thời gian, chỉ chạy trên các cấu hình đạt "Khớp chung" ở bước 3, cộng hai mốc đối chứng; nếu hơn 40 cấu hình thì lấy 40 cấu hình có tỉ số khớp theo phiên tốt nhất. Mỗi dòng: p̂; số ô và tỉ lệ được nổ (thô / tính cả gộp) của bốn nhóm: 20 lớn nhất ngày, 5 lớn nhất phiên, cực trị chặt cả hai thước, cực trị chặt từng thước; tỉ lệ chấm nhiễu (ngoài cả hai thước lỏng); tỉ lệ chấm chỉ thuộc thước cùng giờ / chỉ thuộc thước quanh nó; tỉ lệ chấm ≤ 3 và ≤ 5 hợp đồng. Kèm cột ĐẠT / TRƯỢT theo 4.3.

### Bước 5. `sa_dot_edge.py` → `out_r1_dot_edge.csv`

Tám ca biên của 4.4, chạy trên tối đa 10 cấu hình tốt nhất sau bước 4 (mỗi phương án ít nhất một cấu hình, để có so sánh) cộng hai mốc đối chứng.

### Bước 6. Big Trade: `sa_bt_rules.py`, `sa_bt_selftest.py`, `sa_bt_eval.py`, `sa_bt_oracle.py`

- Nạp nhật ký bằng `../adaptive_2026-11-24/bt_common.py` (`load_m1('GC')`, `('NQ')`, `('GClive')`, `to_tf`, `bars_of`). Khung 1, 5, 15, 30, 60.
- Đoạn chọn / kiểm: GC 10 phiên đầu / 6 phiên cuối; NQ không chia (ghi rõ "6 phiên, không có đoạn kiểm"); `GClive` chỉ dùng cho phương án cuốn và kỷ lục, coi như đoạn kiểm thứ hai.
- `out_r1_bt_profile.csv`: như bước 1 trên `mot` (theo giờ, theo phiên; phân vị 50 / 90 / 99 / 99,5 / 99,9; biến động giữa các ngày).
- `out_r1_bt_level.csv` (cho phương án 3.4): ghép nhật ký với footprint theo (giờ nến, tick). Với mỗi mặt bằng L trong 3.4 và với `mot` thô: phân vị 99 của giá trị tính riêng từng (ngày × phiên), rồi hệ số biến thiên (độ lệch chuẩn / trung bình) của các phân vị đó, và tỉ số phiên Mỹ / phiên Á. Phương án 3.4 chỉ đo tiếp nếu có L cho hệ số biến thiên nhỏ hơn `mot` thô ít nhất 30%.
- `out_r1_bt_calib.csv`, `out_r1_bt_density.csv`, `out_r1_bt_summary.csv`, `out_r1_bt_oracle.csv`: cùng cột và cùng tiêu chí như bước 3 và 4, thay "chấm" bằng "vòng", gộp theo g. Thêm phân phối số vòng mỗi nến (phân vị 50 / 95 / lớn nhất) để sau này quyết có cần giới hạn số vòng không.
- `out_r1_bt_avail.csv`: trên `GClive`, với mỗi phương án, tỉ lệ nến có ngưỡng (đủ tập tham chiếu). Đây là thước "dùng được ngoài đời" của phương án cùng giờ.
- Selftest như bước 2 (ví dụ nhỏ; bản nhanh = bản chuẩn; không nhìn tương lai; nến không có số liệu không được nộp).

### Bước 7. `R1-KET-QUA.md`

Opus viết: mỗi bước một bảng rút gọn (chỉ đoạn kiểm, M1 / M5 / M15, cả hai mã), danh sách cấu hình đạt hết, danh sách ba cấu hình trượt ít nhất của mỗi phương án và trượt cái gì, mọi điều bất thường gặp khi chạy (dữ liệu thiếu, giả định trong kế hoạch sai, selftest trượt). **Không** đề xuất tham số mặc định, **không** kết luận phương án nào thắng: đó là việc của Fable ở vòng 2.

### Điều kiện xong vòng 1

- Mọi selftest in ĐẠT.
- Đủ các file `out_r1_*` nêu trên và `R1-KET-QUA.md`.
- Số nến trong bảng khớp số đã biết: GC M1 87.362 nến, NQ M1 71.047 nến; nhật ký GC 22.948 và NQ 8.340 nến M1.
- Mốc đối chứng "luật đang chạy" ra lại đúng số chuẩn cũ khi bật lại luật che và sàn như bản gốc (GC M1 bộ Ít nhiễu 39.918 chấm; bộ Không sót sàn 5 là 80.386 chấm) — để chắc lớp gộp và cách đọc dữ liệu không lệch.

## 6. Các vòng sau (phác, sẽ viết chi tiết khi có số vòng 1)

| Vòng | Ai | Việc |
|---|---|---|
| 2 | Fable đọc `R1-KET-QUA.md` | Chọn phương án cho chấm và cho Big Trade; quyết kiểu mức danh nghĩa (theo ô hay theo nến), phương án dự phòng khi chưa đủ lịch sử, có cần sàn / giới hạn số bóng mỗi nến không; nếu cần thì giao Opus đo thêm một lưới hẹp. Viết các mức cho người dùng chọn bằng lời (ví dụ "hiếm vừa / hiếm / rất hiếm") |
| 3 | Fable viết spec, Opus code | Spec C# từng dòng: lớp thuần mới cạnh `CellBigLogic`, lượng tử hóa để C# = Python, ô cài đặt "Chế độ ngưỡng: Theo CORVEN / Không theo CORVEN (thống kê)", dấu vân tay chỉ thêm khi chế độ mới bật, nến đầu chart. Mặc định giữ chế độ cũ cho tới khi người học duyệt |
| 4 | Opus test, Fable review | Unit test; `Golden stophunt` C# = Python từng dấu trên GC và NQ, M1 / M5 / M15 / H1; `inccheck` nạp nguội = nạp tăng dần; `golden` chế độ cũ không đổi; `tests-dll`. Fable đọc lại code và số |
| 5 | Fable | So tham khảo với chart CORVEN (chỉ báo cáo chênh, không chỉnh theo); viết phần README cho người học; nêu những gì chưa đo (MGC / MNQ, Big Trade NQ chỉ 6 phiên) |

Vòng 2 → 4 lặp lại nếu review ở vòng 4 tìm ra lỗi hoặc số không khớp.

## 7. Rủi ro đã thấy trước

1. **Big Trade thiếu dữ liệu**: NQ 6 phiên, nhật ký sống đứt quãng. Kết luận về Big Trade sẽ yếu hơn chấm; phải ghi rõ ở mọi bảng.
2. **Thước nhìn lại có cùng họ với hai phương án** (cùng giờ, cuốn). Vì vậy tiêu chí sót chỉ tính ô là cực trị trên **cả hai** thước, và có thêm hai tiêu chí không phụ thuộc thước (20 ô lớn nhất ngày, 5 ô lớn nhất phiên).
3. **Mức p nhỏ ở khung lớn không đủ mẫu** (H1 cuốn 5 nến). Kỳ vọng kết quả: khung lớn cần tham chiếu cùng giờ hoặc kiểu kỷ lục.
4. **Giá trị nguyên nhỏ ở M1** (trung vị 2, phân vị 99 chỉ 13 ở GC phiên Á): mức danh nghĩa đạt được nhảy bậc. Đã xử lý bằng cột "mức danh nghĩa đạt được".
5. **MGC / MNQ không có dữ liệu** trong kho: không đo được, chế độ mới chỉ được nói là đã đo trên GC và NQ.
6. **Mật độ đều không phải mục tiêu tự thân.** Một phương án ép số chấm mỗi nến gần hằng số sẽ làm ngày sôi động và ngày vắng trông giống nhau. Số tương quan ở 4.2 đo đúng điều này để người học chọn.
