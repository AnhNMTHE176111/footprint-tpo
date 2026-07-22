# TPO — Lõi thực chiến (đọc chart, không học vẹt)

> Bản cô đọng theo mindset thực chiến: **chỉ xoay quanh IB + giá mở vs VA + chất lượng đấu giá + đọc số trên chart.** Ba buổi chi tiết (`buoi-1/2/3`) giữ làm THAM CHIẾU để tra khi cần đào sâu, KHÔNG dạy tuần tự nữa. Những nhãn bội thực (4 tên kiểu mở cửa, Normal/Normal Variation Day, 5 phân đoạn ES, Big Smile/Frown) đã cắt — xem cuối file.

---

## 0️⃣ Chu kỳ TPO đặt sao cho đúng

**Nguyên tắc gốc (không phải bảng tra cứng):** chọn chu kỳ TPO sao cho phiên bạn vẽ profile chia ra **~13–48 bracket**, và profile **neo vào một NGÀY giao dịch** (đó là chỗ Market Profile lấy sức: cuối ngày day-trader bị ép tất toán, để lại POC/giá trị của ngày).

- **Khung Daily → bracket 30′.** ✅ Đây là convention CHUẨN (Steidlmayer/Dalton) và là khung ta dùng. Phiên Mỹ vàng ~ nhiều giờ → hàng chục bracket, đủ nén thành hình chuông.
- **Khung M30 → chu kỳ M1?** Chạy được về cơ học (30 bracket 1′) nhưng **KHÔNG phải Market Profile chuẩn** — nó là micro-profile. Ở thang 1 phút biến mất cái neo "ngày" và động lực OTF-vs-day-trader; và nó **trùng việc mà footprint/delta đã làm tốt hơn**. → Muốn soi 1 phút thì mở **footprint/delta trên ATAS** (bạn đã thành thạo), đừng gọi TPO-1′ là "MP chuẩn".
- **IB = 2 bracket ĐẦU** (định nghĩa gốc). Con số phút là HỆ QUẢ của thang: ở Daily/M30 = **A+B = 60′**; nếu ép xuống M30/M1 thì IB = 2′ (quá ít data để đọc "ai kiểm soát"). → Với vàng: **giữ bracket 30′, dùng IB của khung DAILY** (bạn ấy: *"dùng IB Daily"*) = 2 bracket đầu của cây Daily. Vàng/forex chạy ~24h, không có "mở cửa" trung tâm → **giờ phiên chỉ tương đối, đừng chỉnh ly ti mốc**; lấy IB theo cây Daily chart bạn vẽ, miễn nhất quán.

---

## 1️⃣ Mindset lõi — 3 câu hỏi mỗi phiên

Mở ATAS lên, trước khi nghĩ tới lệnh, trả lời đúng 3 câu:

### Câu 1 — Giá mở nằm ĐÂU so với VA phiên Mỹ hôm qua?
Mất cân bằng tăng dần (⇒ cơ hội có ngày trend tăng dần):
| Mở ở… | Nghĩa | Tham chiếu |
|---|---|---|
| **trong VA** hôm qua | cân bằng, chấp nhận giá cũ | xoay quanh POC/VAH/VAL, chờ bằng chứng khác |
| **ngoài VA, trong range** | mất cân bằng nhẹ | chấp nhận cú thoát → mép VA cũ thành tường; từ chối → về VA |
| **ngoài range** hôm qua | mất cân bằng rõ, OTF đã ra tay | xác suất tiếp diễn cao nhất, vẫn xem giá phát triển sau mở |

*Đọc số:* trong bracket A, đếm **số ô TPO trên vs dưới giá mở** — lệch hẳn bên nào = bên đó thắng phiên mở. (Đây là "Delta của người không có footprint"; đối chiếu luôn Delta 30′ trên ATAS.)

### Câu 2 — IB BREAK: cú phá IB có "đấu giá thật" không? ⭐
Đây đúng trục bạn ấy gọi **"IB break"**: dựng IB (A+B, 60′), rồi canh **giá phá biên IB** (= range extension). Cả bài toán gói trong 1 câu — **cú phá có được đấu giá / chấp nhận không?**
- **Break UY TÍN (đấu giá thật):** phá biên IB và **giữ được** — có follow-through, TPO in tiếp phía ngoài, delta/volume cùng phe (soi footprint để xác nhận) → **OTF nhập cuộc → đi THEO hướng phá.**
- **Failed break (đấu giá thất bại):** phá biên nhưng **không giữ nổi ~30′** rồi chui lại vào IB → đám kẹt phía sai phải thoát = nhiên liệu chiều ngược → **fade, kỳ vọng quay test MÉP KIA của IB.**
- **Chất lượng IB làm nền:** IB xoay 2 chiều dày dặn (đấu giá cân bằng) → biên sạch, cú phá đáng tin hơn; IB chỉ là 1 cú đẩy mỏng 1 chiều → biên yếu, dễ **phá giả**.

**Neo IB (đã chốt):** IB = 2 bracket đầu của cây **Daily**, và **Session cây Daily/TPO phải neo vào phiên Mỹ — bracket A khởi ~19:20 VN (COMEX floor), KHÔNG dùng thanh Globex 05:00**. ("Giờ phiên tương đối" chỉ là ±10–20′ quanh mốc pit, không phải chọn Globex vs pit — nếu vẽ nhầm sang Globex thì "2 bracket đầu" lệch 14 tiếng, hỏng cả trục.) ⇒ **IB Daily = 19:20–20:20.**

**Luật đánh cú IB break** *(luật 1 — entry — ✅ ĐÃ CHỐT với bạn trader 2026-07-13, nguyên văn: **"Phá biên rồi chờ test"**; luật 2–5 vẫn là mặc định Claude tổng hợp — đối chiếu tiếp khi bạn ấy rảnh)*:
1. **Phá biên rồi CHỜ TEST — không đuổi cú phá. ✅ Quy trình 4 nhịp:** (1) giá phá biên IB → (2) chờ **1 nến M30 ĐÓNG hẳn ngoài biên** = công nhận break thật (chui lại trong ~30′ → nhảy Failed break) → (3) chờ **RETEST đúng biên vừa phá** (biên cũ đổi vai thành tường — cùng logic single print) → (4) tại retest cần thêm **X1–X4 cùng hướng + delta fresh** mới bấm cò. Phương án phụ: cú phá lần 1 bị từ chối → phục kích **break lần 2 tại chính biên IB đó** [GT-11].
2. **Xác nhận "đấu giá thật" — hai điều kiện ở HAI NHỊP khác nhau, không phải chọn một** (chốt từ feedback đa agent 2026-07-13): "giá trụ ngoài ~30′" là thước đo **CẤU TRÚC ở nhịp (2)** để CÔNG NHẬN break (chịu được data trễ 15′); delta/imbalance follow-through là **TRIGGER ở nhịp (4)** tại retest — KHÔNG dùng delta live làm cổng công nhận (ATAS free trễ 15′ xác nhận muộn, retest bay mất). *Câu còn hỏi mentor [GT-21]: acceptance công nhận đo bằng 1 nến M30 đóng ngoài, hay cần in trọn 1 bracket TPO + VA nhích ra?*
3. **Failed break → mặc định ĐỨNG NGOÀI;** chỉ fade khi có trigger footprint (X1–X4) tại cú chui lại. Target: **T1 = POC/giữa IB** (chỗ hay xoay), chỉ kéo về mép IB đối diện khi value/delta đi theo. Invalidation kèo fade: giá ĐÓNG M30 vượt lại cực trị cú phá hụt → out. Kiểm R:R trước khi vào, < ~1:2 thì bỏ [GT-22].
4. **Stop = cấu trúc:** bên kia biên IB vừa phá (break-follow) hoặc ngoài cực trị cú phá hụt (fade) — đúng "SL sau lưng tường", độ rộng đối chiếu 10–20% ADR; rộng hơn 20% → giảm size/bỏ, KHÔNG thay bằng SL cố định cắt ngang tường.
5. **Target break-follow:** không dùng chiếu IB±width nữa — dùng **scaling-out theo vùng volume**: VAH/POC/VAL phía trước + HVN kế tiếp, chốt TRƯỚC vùng nặng một chút.

> ⚙️ **Data ATAS free trễ 15′:** MẮT trễ, không phải LỆNH trễ. Nến M1 nhìn thấy là quá khứ 15′ → phản ứng theo X1–X4 rồi mới bấm = bắn vào bóng ma. Trên free data: **luyện đọc X1–X4 trên paper, vào thật bằng lệnh chờ/limit đặt trước** tại vùng/biên đã kẻ (vẫn khớp real-time).

### Câu 3 — Cú mở mang NIỀM TIN gì? (đọc cơ chế, bỏ 4 cái tên)
Thay cho taxonomy Latin, đọc 3 nhánh niềm tin:
- **DRIVE** — mở ngoài value, đi **một chiều** không quay lại giá mở = niềm tin OTF cao nhất, **đừng fade**. Đây là *tiền đề* phiên RE sẽ nới 1 chiều (IB = A+B **chưa đóng** nên CHƯA gọi "IB break" — xử theo luật DRIVE). **Bám theo = vào ở CÚ TEST/pullback nông đầu tiên** về cực trị bracket A / mức vừa phá, **KHÔNG đuổi giá đang bay**; không có nhịp test → BỎ kèo, chấp nhận MISS (đúng luật "chờ test"). ⭐ **Cực trị bracket A (30′ đầu) = mốc invalidation CẢ NGÀY** [GT-9]: giá xuyên ngược qua nó = kịch bản chết → thoát, cân nhắc đảo.
- **ROTATION** — xoay 2 chiều quanh giá mở/VA cũ, biến động thấp = ngày của day-trader, chờ ở mép, ít cơ hội lớn.
- **REJECTION-REVERSE** — mở ở **cực trị hôm qua** rồi bị đánh bật quay đầu = **phe ngược ra tay**, sóng/xu hướng hiện tại sắp tàn. Đây là read ĐẢO CHIỀU (mở đỉnh đóng đáy hoặc ngược lại).

> ⚠️ Bạn của bạn nói *"Open Drive quá lý thuyết"* — **ngược lại**: Open Drive là kiểu mở **rõ và dễ trade nhất**, chính là nhánh DRIVE ở trên. Cái đáng cắt là 4 *cái tên* (Open Test Drive / Auction Out-of-Range… nhòe vào nhau), không phải cơ chế drive.

---

## 2️⃣ Bộ setup thực chiến giữ lại (đã lọc)

> 📊 Setup 1 & 2 có diagram minh họa riêng (đã vẽ vì người học thích nhìn chart) → [`batch-A-80-rule-va-tai-nhap.md`](batch-A-80-rule-va-tai-nhap.md).
> 📊 Setup 3–6 cũng có diagram riêng → [`batch-B-single-print-beartrap-trendday-tails.md`](batch-B-single-print-beartrap-trendday-tails.md).

1. **80% rule** — mở **ngoài** VA → quay **vào** VA → giữ **2 bracket 30′ liên tiếp kể từ lúc tái nhập** → ~80% xuyên **hết VA sang mép đối diện**. Entry khi điều kiện chốt; **target = mép VA đối diện** (chốt trước 1 chút vì trùng HVN); stop ngoài mép vừa tái nhập / cực trị bracket A.
2. **Mở ngoài value + tái nhập THẤT BẠI** → mép VA cũ thành **tường** (mở dưới VAL, ngoi lên fail nhiều lần → VAL thành trần → Short tựa lưng VAL; gương ngược cho mở trên VAH).
3. **Single print / minus development** (vệt in đơn giữa profile = LVN đo bằng thời gian): **đừng đuổi** cú chạy, **chờ retest** vùng in đơn; SL bên kia vùng. Giá vượt lên để lại vệt dưới → hỗ trợ; lao xuống để lại vệt trên → kháng cự.
4. **Bear/bull trap** — phá cực trị hôm qua mà **bracket kế KHÔNG nới range thêm** = phá không người theo (mồi) → fade ngược. (Absorption nhìn bằng TPO.)
5. **Kỷ luật Trend Day** — **không bao giờ đánh ngược một trend day**; giá in **5+ TPO cùng một mức** = ngày đã tìm xong giá hợp lý, đà đuối → **ngừng trail, chốt bớt** (chưa cần đảo).
6. **Tails + poor high/low** (Unfinished Business ở cực trị) — đuôi dài / high-low "cụt" = mức phải quay lại test → S/R + mục tiêu cho phiên Á/Âu hôm sau.

---

## 3️⃣ Checklist trước phiên (2 phút mỗi tối)

1. Kẻ **VA / POC / VAH / VAL** phiên Mỹ hôm qua.
2. **Giá mở** rơi ở đâu so với VA/range? (Câu 1)
3. **IB (A+B, 60′):** acceptance 2 chiều hay 1 cú đẩy mỏng? Có RE chưa, về hướng nào? (Câu 2)
4. **Niềm tin mở:** Drive / Rotation / Rejection-Reverse? Nếu Drive → kẻ ngay **cực trị bracket A = mốc invalidation**. (Câu 3)
5. Setup nào khớp (mục 2)? Chờ **trigger footprint/delta** đúng vùng (hợp lưu nguồn độc lập).
6. **Sizing 2%**, SL = điểm cấu trúc (chỗ chứng minh lệnh SAI), không phải số đô tùy hứng.
7. **Giờ phiên chỉ tương đối** (vàng/forex 24h) — đừng cứng mốc giờ. Nhưng move thật của vàng thường đến trong **phiên Mỹ**, nên cú **IB break giờ Mỹ đáng tin hơn** IB break lúc Á/Âu mỏng.

*Phiên tin (NFP/CPI 19:30, FOMC ~01:00 VN):* **flat trước tin**, không trade lúc tin ra (ATAS free trễ 15′ → chart chưa hiện nến tin); ~sau 15′ đánh dấu POC/vùng tích lũy trước tin + LVN nến tin → **fade về vùng đó** khi có hợp lưu.

---

## ✂️ Đã CẮT (đừng học — gây bội thực, không đổi quyết định trade)
- **4 tên kiểu mở cửa Dalton** (Open Drive / Open Test Drive / Open Auction In-Out Range / Open Rejection-Reverse) — giữ CƠ CHẾ 3 nhánh niềm tin (mục 1, Câu 3), bỏ các NHÃN.
- **Normal Day / Normal Variation Day** và việc chẻ 6 loại ngày quá mịn — chỉ giữ 4 loại có hành động: Trend, Double Distribution (+bear trap + vệt single print), Non-Trend (nén trước tin → hôm sau dễ trend), và bẫy phân biệt **DD vs Neutral**.
- **5 phân đoạn phiên Mỹ của ES** — lịch riêng của cổ phiếu, không bê sang vàng.
- **Big Smile / Frown** (2 mẫu volume qua đêm) — nhãn hoa mỹ, độ tin thấp (chính Keppler cảnh báo volume mở cửa hay giật ngược trước).

## 📎 Muốn đào sâu thì tra (tham chiếu, không dạy tuần tự)
- Cơ chế chart TPO, TPO-POC vs VPOC, IB/RE/failed auction, tails, single print → [`buoi-1`](buoi-1-nen-tpo-ban-do-phien.md)
- Giá mở vs VA (3 kịch bản có chart ES thật), 80% rule, day types actionable → [`buoi-2`](buoi-2-day-types-mo-cua-80.md)
- Value migration, POC clustering, **note thực chiến vàng (2 ca GCQ23)**, kick-off thực hành → [`buoi-3`](buoi-3-da-phien-thuc-chien-vang.md)
