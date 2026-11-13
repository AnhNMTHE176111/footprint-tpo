# Bàn giao: thêm vùng HVN vào indicator "Benzo Volume Profile"

> Cách dùng ở máy khác: mở Claude Code trong repo chứa indicator (có thư mục `footprint-tpo` bên cạnh,
> hoặc chính repo này), rồi gõ:
> **"Đọc `tradingview-nasdaq/hvn-handoff/PROMPT.md` và làm theo."**
> Trả lời người dùng bằng **tiếng Việt**, ngắn gọn. Giữ nguyên các từ **buy / sell / limit / market**.

## Các file trong thư mục này
| File | Là gì |
|---|---|
| `PROMPT.md` | file này — yêu cầu nguyên văn + tri thức đã gom |
| `benzo-volume-profile.inputs.json` | nội dung tab **Inputs** đang dùng (nguyên văn người dùng dán) |
| `benzo-volume-profile.script.js` | nội dung tab **Script** đang dùng (nguyên văn người dùng dán) |
| `traderdale-vi-du-hvn.png` | ảnh mẫu Trader Dale người dùng gửi (mở bằng tool Read để xem) |

⚠️ Script **không phải Pine** — chạy trên một nền tảng chart JS riêng (có tab Inputs/Script, API
`bv.security`, `bv.securityLowerTf`, `bv.detectBarMs`, `bv.visible`, `bv.xOfIndex`, `bv.yOfPrice`,
hàm `calc(dataList, indicator)` + `draw(args)` vẽ bằng canvas, kiểu KLineCharts). Bản Pine gốc cũ hơn:
`footprint-tpo/tradingview-nasdaq/benzo-volume-profile.pine`. Chart dùng: `OANDA:NAS100USD`
(tick volume), vào lệnh `USTEC` Exness.

---

## 1. Yêu cầu nguyên văn của người dùng

> oke, bây giờ tôi muốn có thêm phần bật HVN theo vol profile đó. HVN là các volume cluster mạnh ấy, bạn
> có thể research thật kỹ cả internet cũng như folder footprint-tpo ở bên cạnh repo này để lấy đủ kiến thức.
> Vì kỹ thuật chơi của tôi tức là, nếu giá đang ở HVN, rồi nó break ra ngoài, rồi khi nó quay lại chạm vào
> HVN đấy thì nó sẽ phản ứng bật ngược lại. Nên vùng HVN rất quan trọng.
>
> Tôi muốn khi bật HVN, thì dải giá trị đó có thể thay đổi đường màu sắc, và kéo dài sang ngang hết luôn để
> dễ tìm.
>
> Vùng thì bạn phải kết hợp từ internet, youtube của dale trader (ảnh), script mà corven nói về TPO HVN,
> cách xác định, rồi đo đạc về việc nó rời đi quay lại và phản ứng nhé. Vùng có thể rộng hẹp, tùy theo
> mức đó của nó nhé.
>
> Ưu tiên dải của tuần hiện tại trước nếu đã hình thành được cluster, còn nếu tuần hiện tại chưa rõ ràng
> hoặc giá chưa có mức đấy thì sẽ có dải của tuần trước. Vùng HVN canh sell thì màu khác, vùng HVN canh
> buy thì màu khác nhé.
>
> Làm xong nhớ đo đạc với data đã có, đo đạc cả lần phản ứng nhé. Testing thật kỹ. Và tối ưu code để load
> nhanh.

### Tóm tắt yêu cầu thành tiêu chí nghiệm thu
1. **Công tắc bật/tắt HVN** (input mới), không phá các tính năng cũ (profile, POC, VA, VWAP, dải σ).
2. **Xác định HVN** = cụm khối lượng mạnh trên volume profile; **độ rộng vùng co giãn** theo hình dạng cụm
   (không cố định số điểm).
3. **Vùng kéo dài ngang tới mép phải chart** (như dải đỏ/xanh trong ảnh Trader Dale), có màu riêng.
4. **Hai màu:** HVN **nằm trên giá hiện tại** = vùng canh **sell**; HVN **nằm dưới giá** = vùng canh **buy**
   (đề xuất; khi giá đang nằm trong vùng thì vùng "chưa có giá trị" — xem luật CORVEN dưới).
5. **Ưu tiên tuần hiện tại:** dùng HVN của profile tuần đang chạy nếu đã hình thành cụm rõ; nếu chưa rõ /
   giá chưa đi qua mức đó thì lấy HVN của **tuần trước**. Chồng nhau thì gộp.
6. **Đo đạc trên dữ liệu thật:** giá rời HVN → quay lại chạm → có **phản ứng bật ngược** không, bao nhiêu %,
   so với nền ngẫu nhiên (mức giá bất kỳ không phải HVN). Báo số liệu trung thực, kể cả khi không có lợi thế.
7. **Test kỹ** (unit test cho hàm tìm HVN / gộp vùng / phân loại buy-sell, chạy được bằng Node) và
   **tối ưu tốc độ load** (không tính lại profile tuần mỗi tick; cache theo phiên đã đóng; dùng TypedArray).

### Ảnh mẫu `traderdale-vi-du-hvn.png` (USDJPY M30, Trader Dale)
Profile của khoảng 5–8/9 có 2 cụm khối lượng: cụm trên ~106,23–106,32 (khung đỏ) và cụm dưới ~105,90–105,98
(khung xanh). Sau khi giá rời khỏi profile, hai cụm được kéo dài ngang sang phải thành **resistance** (đỏ,
giá quay lên chạm nhiều lần rồi bị đẩy xuống — mũi tên đen) và **support** (xanh, giá quay xuống chạm rồi bật
lên). Đây chính là hình người dùng muốn indicator vẽ.

---

## 2. Tri thức đã có trong `footprint-tpo` (đọc các file này)

### 2a. CORVEN (mentor của người dùng) — nguồn ưu tiên cao nhất
`footprint-tpo/corven-meet/2026-11-07/transcript.md` mục **25 (1:11:00 – 1:19:03)**, ảnh trong
`corven-meet/2026-11-07/frames/1-11-05.jpg`, `1-12-59.jpg`, `1-13-45.jpg`:
- [1:11:00] Giá **đang nằm trong** vùng HVN thì vùng **chưa có giá trị**.
- [1:11:16] Giá **cắt ra khỏi** vùng thì vùng **bắt đầu có giá trị** → quay lại test mới chơi được.
- [1:11:49] Tuần này, tuần trước: **chồng nhau thì gộp lại một** HVN.
- [1:12:59] **POC cũng là HVN.**
- [1:13:41] Nhiều vùng gần nhau quá thì **chọn vùng lớn nhất**.
- [1:16:56] Kiểu bị break qua rồi test lại vùng đấy.
- [1:18:49] Chồng nhau thì gộp, không chồng thì để riêng.

Các file khác:
- `data-export/messages-with-pro-trader/CORVEN_SPEC_V1.md` — §2 "Vùng — CHỈ HVN và VWAP"; Play 1 = chạm →
  đảo chiều tại HVN; Play 2 = phá HVN rồi hồi về mép vùng → vào thuận hướng phá; RR 1:3, xác nhận nến M1.
  Ghi chú: HVN tuần nên đo trên **cửa sổ 3 tuần**.
- `data-export/messages-with-pro-trader/CAU_HOI_CAN_THONG_NHAT.md` (mục A2, C2, C3) — CORVEN: "chỉ quan tâm
  HVN thôi", không dùng POC/VAH/VAL tuần; HVN vừa là chỗ đảo chiều vừa là chỗ phá rồi hồi.
- `data-export/messages-with-pro-trader/BAI_GIANG_CORVEN.md` dòng ~144, 207, 283 — đo cũ: `hvn_week` WR 57%,
  EV +0.429R; `hvn_day` EV −0.375R. ⚠️ Số đo này chạy trên dữ liệu **mỏng** (xem 2c) ⇒ chưa đáng tin.
- `data-export/messages-with-pro-trader/CORVEN_TONG_HOP.md` — "Vùng quan trọng của TPO là HVN; chạm HVN thì
  giá có thể đảo chiều hoặc phá vùng".

### 2b. Cách xác định HVN đã tổng hợp — `footprint-tpo/tpo/HVN-CACH-XAC-DINH.md`
(Tổng hợp riêng của Claude, **chưa kiểm định**.)
1. Profile: ngày cho scalp, gộp 3 tuần cho vùng lớn. 2. Làm mượt mỗi dòng với 2 dòng sát bên.
3. Đỉnh = dòng cao hơn 2 dòng sát bên. 4. Độ nổi = đỉnh − thung lũng **cao hơn** trong 2 thung lũng hai bên;
giữ đỉnh có độ nổi **≥ 30% POC**; 2 đỉnh không có thung lũng thật ở giữa = 1 HVN.
5. Mép vùng: đi từ đỉnh ra 2 phía, dừng khi khối lượng đã rơi **60% quãng** từ đỉnh xuống thung lũng.
6. Kiểm độ bền: đổi cỡ dòng mà HVN vẫn còn mới tin.
Nguồn: pycoders "How to Analyze Volume Profiles With Python" (ngưỡng độ nổi), TradingView "HVN Zones"
(6TPrx1GV — mép 60%), LuxAlgo "High/low-volume Nodes", traderprofesional.com "HVN and LVN".

Code C# đã có hàm tương đương: `footprint-tpo/quantower-tpo-suite/ProfileEngine.cs` → `FindHvn(rows, tick,
minRatio)`; dùng ở `quantower-entry-signal/RunnerSignal.cs:654-673` và `quantower-tpo-suite/DailyTpoBias.cs:195`.
Nên đọc để port logic sang JS cho đồng nhất.

### 2c. Dữ liệu để đo — đọc `footprint-tpo/data-export/README.md` trước
- Nguồn chuẩn (vàng GC, M1, có khối lượng thật): `data-export/data-footprint/fp_GC_XCEC_Time_*.csv` +
  `_bars.csv`, và mới nhất `fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv` + `_90d_bars.csv` (90 ngày).
- ⛔ `Data_Footprint_Export.csv` cũ mỏng hơn 154 lần — không dùng để kết luận.
- ⚠️ Mã liên tục nối thô không bù giá (bước nhảy giả +61,2 ngày 2026-07-29) — lọc bỏ cửa sổ vắt qua chỗ nối.
- Chưa có dữ liệu NAS100 trong repo. Nếu cần đo đúng Nasdaq thì xin người dùng xuất CSV M1 `OANDA:NAS100USD`
  (≥ 3 tháng); trong lúc chờ, đo trên vàng GC và **nói rõ là đo trên vàng**.

---

## 3. Quy tắc làm việc (từ `footprint-tpo/CLAUDE.md`)
- Trả lời **ngắn, tiếng Việt có dấu**; thuật ngữ mới phải giải thích; buy/sell/limit/market giữ tiếng Anh.
- Sửa code xong **phải test** rồi mới báo xong; báo cả lỗi nếu có.
- Luật chưa đo được bằng số thì **không nói như đã kiểm định**. "Không có lợi thế" là kết quả hợp lệ.
- Phần nào là tổng hợp riêng của Claude (không phải CORVEN nói) phải ghi rõ.
- Commit + push sau mọi lượt có sửa file, báo hash.

## 4. Đề xuất hướng làm (chỉ là gợi ý, tự quyết sau khi đọc)
1. Thêm input: `showHVN` (bool), `hvnRows` (số dòng profile tuần, vd 60–120), `hvnMinProm` (độ nổi tối thiểu
   % POC, mặc định 30), `hvnEdgePct` (mép 60%), `hvnWeeks` (1–3), `colHvnSell`, `colHvnBuy`, `colHvnInside`.
2. Profile tuần dựng từ nến 1m/5m qua `bv.securityLowerTf` (như `buildProfile`), **cache theo tuần đã đóng**
   (khóa = thời điểm mở tuần + tham số), chỉ tính lại tuần đang chạy.
3. Tìm HVN: làm mượt → tìm đỉnh → lọc độ nổi → mép 60% → gộp vùng chồng nhau tuần này/tuần trước → nhiều vùng
   sát nhau thì giữ vùng lớn nhất.
4. Chọn vùng hiển thị: tuần hiện tại nếu đã có HVN đạt chuẩn và giá đã rời vùng; nếu không thì tuần trước.
5. Màu: trên giá = sell, dưới giá = buy, giá đang ở trong = màu trung tính ("chưa có giá trị").
   Vẽ hình chữ nhật từ đầu tuần tạo ra vùng tới **mép phải chart**, kèm nhãn giá biên.
6. Đo: viết script Node/Python chạy cùng thuật toán trên CSV; với mỗi vùng: lần đầu giá rời ra ≥ X điểm, rồi
   quay lại chạm mép → đo bật ngược ≥ Y điểm trước khi xuyên qua vùng ≥ Z điểm; so với mức giá ngẫu nhiên
   cùng khoảng cách; báo n, tỉ lệ, khoảng tin cậy.
