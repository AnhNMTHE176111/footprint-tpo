# 📕 SYLLABUS TPO v2 — Dạy lại từ gốc, theo đúng cách CORVEN dùng

> **Vì sao có bản này:** người học tự đánh giá "TPO chưa được học kỹ" (2026-08-11). Bản cũ
> (`00-tpo-loi-thuc-chien.md` + 3 buổi) dạy TPO theo **sách Keppler/Dalton** — trục là *IB + giá mở vs VA*.
> Nhưng **CORVEN dùng TPO theo một trục khác**: *hình dạng profile → check tail → HVN → chế độ balance
> → follow break*. Và có một nguồn cực đậm đặc **chưa hề được dạy**: `TPO.pdf` (17 trang note thực chiến
> vàng), chứa ~30 luật hành vi cụ thể.
>
> Bản này **hợp nhất 3 nguồn** thành một chuỗi quyết định thực chiến, và **nói rõ chỗ nào 3 nguồn mâu thuẫn**.

---

## 🗂️ Nguồn — 4 tài liệu, vai trò khác nhau

| Nguồn | File | Vai trò | Độ tin |
|---|---|---|---|
| **Note thực chiến vàng** | `TPO.pdf` (17tr) · ảnh `tpo/images/note/pNNN.png` | ⭐ **Đậm đặc nhất về HÀNH VI.** ~30 luật ngắn, viết bởi trader vàng thực chiến | ⚠️ Không rõ tác giả, **chưa backtest** — coi là giả thuyết chất lượng cao |
| **Keppler** *Profit With the Market Profile* | `TPO - Market ProFile.pdf` (170tr) · ảnh `tpo/images/keppler/` | Lý thuyết chuẩn: auction theory, bell curve, IB/RE, day types, tails | ✅ Sách gốc |
| **Tuyển tập TraderViet** | `Market Profile _Vn.pdf` (102tr) · ảnh `tpo/images/tv/` | ⭐ **Giải thích HÌNH DẠNG D/P/b/thin kỹ nhất** + 6 day types + cách lấy S/R từ hình dạng | ✅ Diễn giải tốt |
| **CORVEN** (pro trader) | `data-export/messages-with-pro-trader/` (`TRANSCRIPT.md` §13, `CORVEN_SPEC_V1.md`) | ⭐ **Trục thực chiến.** Quyết định *dùng cái gì, bỏ cái gì* | ✅ Nguyên văn chat |

---

## 🧭 Trục xuyên suốt — chuỗi 6 câu hỏi CORVEN thực sự chạy

Mọi buổi dưới đây là **một khâu** trong chuỗi này. Học xong phải trả lời được cả 6, theo thứ tự:

```
1. HÌNH DẠNG profile đang là gì?        → đấu giá XONG chưa?          (Buổi 2)
2. TAIL có ổn không?                    → cực trị THẬT hay SCAM?      (Buổi 3)
3. Còn SINGLE PRINT nào chưa fix?       → market sẽ quay lại đâu?     (Buổi 4)
4. HVN nằm ở đâu?                       → vùng CANH LỆNH             (Buổi 5)
5. Đang TRONG balance hay SAU balance?  → bật play nào?              (Buổi 6)
6. VA có move khỏi range?               → break hay reject?          (Buổi 7)
                                        ↓
                              ENTRY M1 bằng footprint/delta          (Buổi 8)
```

> Nguyên văn CORVEN, đúng thứ tự này: *"Tpo thành chữ D"* → *"**Check tail các thứ xem ổn hết chưa**"*
> → *"Day scap nhìn **tpo daily**"* / *"Gộp 3 week, 1 period vẫn là 30p"* → *"Trong balance thì **chop**…
> xác định range rồi 2 cạnh mà vả"* → *"**Giờ break ra là follow theo**"*.

---

## 📗 Buổi 1 — Vòng đời đấu giá: toàn bộ TPO gói trong một cơ chế

**Mục tiêu:** giải thích được *tại sao* profile có hình dạng đó, thay vì nhớ tên hình dạng.

- **Chu trình gốc:** đấu giá tại một vùng → hai phe đồng thuận → **đấu giá XONG** → giá rời đi tìm vùng
  giá trị mới → vùng mới cần đủ **thời gian + giá + khối lượng + độ mở rộng TPO** mới thành VA mới.
- **Vùng THIẾU mở rộng TPO = mất cân bằng (IMB)** — sinh ra đúng lúc giá break.
- **Balance → Trend → Balance:** *"Giá luôn muốn được phân phối đều theo thời gian và khối lượng, nhưng
  market không thể lúc nào cũng phân phối chuẩn — đó là lý do **sau khi có bell curve là có trend**."*
- Vì sao TPO đo **thời gian** (không phải volume) và điều đó cho ta cái gì volume profile không cho.
- Bracket 30′ · neo vào NGÀY · composite vs split.

**Chốt phải nhớ:** hình dạng profile = **ảnh chụp tiến độ đấu giá**, không phải mẫu hình để nhớ.

**Nguồn load:** `TPO.pdf` tr.1 ([note/p001-0.png](images/note/p001-0.png)) · Keppler ch.2 bell curve
([keppler/p011-0.png](images/keppler/p011-0.png), [p012-0.png](images/keppler/p012-0.png)) ·
TraderViet tr.10 Bell Curve · `buoi-1` §1–§2 *(đã học — ôn nhanh)*

**Trạng thái:** `[~]` phần cơ chế chart đã học ở buổi 1 cũ; **phần chu trình đấu giá + "bell curve xong là có trend" CHƯA học.**

---

## 📗 Buổi 2 — ⭐ HÌNH DẠNG PROFILE: đọc "đấu giá xong chưa" bằng mắt

> **Đây là lỗ hổng lớn nhất.** Bản cũ **cắt** phần này với lý do "P/b chỉ là hình dạng, không phải loại
> ngày" — đúng về mặt phân loại sách, nhưng **sai về mặt thực chiến**: câu đầu tiên CORVEN nói khi mở
> chart là *"Tpo thành chữ D"*. Hình dạng là **input số 1**, không phải nhãn trang trí.

**Mục tiêu:** nhìn một profile bất kỳ → nói ngay *đấu giá xong ở đâu, còn dở ở đâu, tiếp theo giá phải đi đâu*.

### 2.1 Sáu hình dạng — đọc bằng CƠ CHẾ
| Hình | Cơ chế sinh ra | Đấu giá xong? | Hệ quả |
|---|---|---|---|
| **D** (bell curve) | hai phe đồng thuận quanh một mức, phân phối đều | ✅ xong | Balance chuẩn → **chờ break**, và "sau bell curve là có trend" |
| **P** (lồi trên, thoải dưới) | giá bị đua lên rồi **cân bằng ở đỉnh** (short covering / mua đua giá) | xong ở PHẦN TRÊN, dở ở dưới | Đầu chữ P = vùng cân bằng; **đuôi P = hỗ trợ** (vùng phe mua đua giá) |
| **b** (lồi dưới, thoải trên) | bán tháo rồi cân bằng ở đáy (long liquidation) | xong ở PHẦN DƯỚI | Gương ngược của P; **POC phụ phía trên b = kháng cự tiếp** |
| **B** / **Double Distribution** | hai vòm giá trị, **giữa mỏng ngăn bởi single print** | xong ở HAI cực, **dở ở GIỮA** | Vệt giữa = LVN → S/R; khó lường, độ tin thấp hơn trend day thường |
| **Thin / trend** (cột dọc) | một chiều, không dừng đấu giá ở đâu cả | ❌ **chưa xong ở đâu hết** | Không đánh ngược; profile sẽ phải được "fix" sau |
| **Chữ nhật** (DD đã lấp giữa) | DD sau đó **vào chính vùng mỏng giữa đấu giá nốt** | ✅ xong TOÀN DẢI | Balance **rộng** → hết chỗ đấu giá bên trong → nghiêng về **break một trong hai đầu** |

### 2.2 Đọc hình dạng ĐANG PHÁT TRIỂN (không chờ hết phiên)
- Trình tự nở của profile trong ngày: một chiều → chững → nở ngang.
- **Trend day rõ có thể đột ngột chuyển thành double distribution** — Keppler cảnh báo thẳng: đừng khoá
  nhãn sớm.
- Chuỗi tiến hoá hay gặp: `D nhỏ → P → P/b (chữ B) → chữ nhật` = **đấu giá lan dần ra rồi lấp đầy**.
  *(Chuỗi này do người học tự quan sát 2026-08-11 và ĐÚNG về cơ chế; không có sách nào viết thành công thức.)*

### 2.3 Chốt sổ hình dạng bằng giá ĐÓNG CỬA
- **Giá đóng cửa nằm NGOÀI vùng balance ⇒ VA đó KHÔNG phải vùng giá trị đúng** — dùng giá đóng, *"không
  quan tâm giá mở cửa"*.
- ⚠️ **Mâu thuẫn cần phân xử:** trục cũ đã học lấy **giá MỞ vs VA** làm câu hỏi số 1 (Dalton). Note thực
  chiến lại nói bỏ giá mở, dùng giá đóng. → xử ở §Mâu thuẫn cuối file.

**Nguồn load:** TraderViet tr.21–23 (D/P/b/thin — [tv/p021-0.png](images/tv/p021-0.png),
[p021-1.png](images/tv/p021-1.png), [p023-0.png](images/tv/p023-0.png)) · TraderViet tr.58–65 (6 day types,
DD tr.64 — [tv/p064-0.png](images/tv/p064-0.png), Neutral tr.65 — [tv/p065-0.png](images/tv/p065-0.png)) ·
Keppler DD + P/b ([keppler/p075-0.png](images/keppler/p075-0.png), [p077-0.png](images/keppler/p077-0.png),
[p078-0.png](images/keppler/p078-0.png), [p079-0.png](images/keppler/p079-0.png)) · `TPO.pdf` tr.2 (4 loại
ngày, [note/p002-0.png](images/note/p002-0.png)) · CORVEN §13.1, §13.7

**Trạng thái:** `[ ]` **CHƯA HỌC** (D/P/b/thin học bên Volume Profile 2026-06-22 nhưng **chưa bao giờ áp
lên TPO**, chưa học chữ B/chữ nhật, chưa học tiến hoá hình dạng).

---

## 📗 Buổi 3 — ⭐ CHECK TAIL: cực trị THẬT hay SCAM

> Bước số 2 của CORVEN, nguyên văn: *"**Check tail các thứ xem ổn hết chưa**"*. Bản cũ có dạy tail nhưng
> **thiếu hẳn phần phân biệt tail xịn / tail scam** — mà đó mới là phần dùng được.

**Mục tiêu:** trước mọi lệnh bắt đỉnh/đáy, phán được cực trị đó có đáng tin không.

- **Định nghĩa:** tail = cực trị bị **từ chối nhanh** (1 TPO đơn ở cực trị). *"1 TPO không thể được hoàn
  thành nếu như không có tail."*
- **Poor high / poor low:** cực trị có **≥2 TPO** ⇒ theo thuyết đấu giá là **đấu giá CHƯA hoàn thành**
  ⇒ dễ bị phá, và là **mục tiêu** phải quay lại test.
- ⭐ **Tail xịn vs tail SCAM — luật lọc quan trọng nhất mục này:**
  - Chỉ buy/sell ở tail khi **tại đó volume THẤP (LVN)**.
  - **Tail mà volume DÀY = scam** — *"Mấy cái tail mà vol như này đều là scam hết, ko kỳ vọng nó là cực
    trị xịn được"*; note ghi thẳng **"Never short here: SCAM PUMP"** / **"Never long here"**.
  - Đỉnh có **1 TPO volume cực nhỏ** ⇒ **kỳ vọng đó là đỉnh thật**.
  - Đỉnh (top tail) có **rất nhiều volume tập trung** ⇒ **đừng kỳ vọng đó là đỉnh**.
- **Giá dừng ở HVN tại một đỉnh kỹ thuật ⇒ đỉnh đó thường FAIL.**
- **TPO ở đỉnh/đáy tạo thành một đường CHÉO ⇒ khả năng rất cao sẽ bị test lại.**

**Chốt phải nhớ:** *tail = từ chối; tail + volume dày = không phải từ chối, mà là hấp thụ/mồi.*

**Nguồn load:** `TPO.pdf` tr.4–6 ([note/p004-0.png](images/note/p004-0.png),
[p004-1.png](images/note/p004-1.png), [p005-0.png](images/note/p005-0.png),
[p005-1.png](images/note/p005-1.png), [p006-0.png](images/note/p006-0.png)) · Keppler tails
([keppler/p049-1.png](images/keppler/p049-1.png), [p050-0.png](images/keppler/p050-0.png)) ·
`batch-B` ⑥ *(đã học phần cơ bản)* · CORVEN §13.1

**Trạng thái:** `[~]` tail/poor high-low cơ bản đã học (batch-B); **luật tail-scam theo volume CHƯA học.**

---

## 📗 Buổi 4 — ⭐ SINGLE PRINT & "FIXER": profile chưa xong thì market quay lại sửa

> Toàn bộ mục này **chưa được dạy** ngoài phần "chờ retest single print". Đây là **cơ chế dự đoán market
> sẽ quay lại đâu**, mạnh hơn hẳn một setup lẻ.

**Mục tiêu:** khoanh trên chart những vùng market **buộc phải quay lại**, và theo thứ tự nào.

- **Single print (SP) = IMB = vùng thiếu mở rộng TPO**, sinh ra khi *"phiên đấu giá bất thường"*, và
  *"Day trader sẽ phải đi fix trong tương lai"*.
- Trong SP tồn tại **liquidation (lệnh limit)**; SP hay nằm ở **vùng thanh khoản** (chỗ break kháng cự/hỗ trợ).
- **Trend mạnh, hoặc SP không có nhiều liquidation ⇒ ít khả năng được fix.**
- **Fix cần VOL + TIME.** Vol to mà time ít, hoặc fix không hết ⇒ *"thợ lởm, giá không move"*.
- ⭐ **Hai nguyên tắc của "fixer":**
  1. **Tuần tự** — cái xuất hiện **trước fix trước**, cái sau fix sau.
  2. **Tôn trọng trend hiện hữu** — trend TĂNG thì fix IB/SP ở **phía TRÊN** giá hiện tại; trend GIẢM thì
     fix ở **phía DƯỚI**. (Nếu là sửa IB thì lấy trend khung **Daily**.)
- ⭐ **"1 trend mạnh diễn ra khi profile được sửa XONG và sửa SẠCH."** ← điều kiện tiền đề của mọi kèo follow trend.
- **Đọc lực trong lúc fix:** trend tăng mà **chỗ lõm được sửa với NHIỀU vol nhưng giá KHÔNG tăng** ⇒ phe
  **sell** đang chiếm ưu thế. (Gương ngược cho trend giảm.) — đây là *absorption đọc bằng TPO*.
- **Playbook:** đừng đuổi cú chạy để lại SP; **chờ retest** vùng SP, SL bên kia vùng.

**Nguồn load:** `TPO.pdf` tr.1, 3, 7 ([note/p001-0.png](images/note/p001-0.png),
[p003-0.png](images/note/p003-0.png), [p007-0.png](images/note/p007-0.png),
[p007-1.png](images/note/p007-1.png)) · `buoi-1` §4.2 · `batch-B` ③ *(đã học phần retest)*

**Trạng thái:** `[~]` chỉ học "chờ retest SP"; **2 nguyên tắc fixer + luật vol/time + "sửa sạch mới có trend" CHƯA học.**

---

## 📗 Buổi 5 — ⭐ LVN vs HVN: bản đồ kỳ vọng, và vùng canh lệnh của CORVEN

**Mục tiêu:** biết vào vùng nào thì **kỳ vọng trend**, vùng nào **kỳ vọng sideway** → quyết định có đặt lệnh hay không.

### 5.1 Luật kỳ vọng (từ note thực chiến)
- Giá đi vào **LVN (vol ít) ⇒ kỳ vọng TREND** sau đó.
- Giá đi vào **HVN (vol nhiều) ⇒ kỳ vọng SIDEWAY**. (Trong VP: *"giá sẽ dừng ở HVN"*.)
- **LVN + volatility cao ⇒ trend.**
- **Đỉnh có LVN mà BỊ PHÁ ⇒ trend up. Đỉnh có LVN mà KHÔNG bị phá ⇒ trend down.**
- VA **volatility thấp** đáng tin cậy hơn VA volatility cao.

### 5.2 Vùng CANH LỆNH — cấu hình thật của CORVEN
- **Chỉ dùng HVN + VWAP.** Nguyên văn: *"Chỉ quan tâm HVN thôi"*. VAH/VAL/POC **từng phiên Á–Âu–Mỹ**:
  *"Tất nhiên là không rồi"*.
- **Hai tầng profile:**
  - **TPO daily** → day scalp (*"Day scap nhìn tpo daily"*).
  - **TPO gộp 3 TUẦN, period vẫn 30 phút** → vùng lớn (*"Gộp 3 week / 1 period vẫn là 30p"*).
- **VWAP:** VWAP ngày (scalp) + VWAP tuần **neo từ đầu tuần, reset 1 lần/tuần**.
- ⚠️ **Mâu thuẫn nặng với bản cũ:** bản cũ dạy VAH/VAL/POC + 80% rule làm xương sống. → xử ở §Mâu thuẫn.
- ⚠️ **Đã đo, chưa chứng minh được:** thử `FindHvn` trên n=4–6 ca → **ngang mức ngẫu nhiên**. Nghĩa là
  luật này đáng học để đọc chart, **nhưng chưa có số bảo chứng** — không được nói như đã kiểm định.

**Nguồn load:** `TPO.pdf` tr.4–5 · `CORVEN_SPEC_V1.md` §2 · `TRANSCRIPT.md` §13.7–13.8 ·
`value-migration-poc-clustering.md` §3 composite *(đã học)* · indicator `quantower-tpo-suite/M30SessionZones`

**Trạng thái:** `[~]` HVN/LVN khái niệm đã học bên ebook; **luật kỳ vọng trend/sideway + cấu hình gộp 3 tuần CHƯA học.**

---

## 📗 Buổi 6 — ⭐⭐ BALANCE vs SAU BALANCE: chế độ thị trường quyết định bật play nào

> **Lỗ hổng lớn thứ hai.** Không có buổi nào trong bản cũ dạy điều này, mà nó là **công tắc gốc**: cùng
> một tín hiệu delta mang ý nghĩa **trái ngược** tuỳ đang ở chế độ nào.

**Mục tiêu:** mở chart là phân loại được ngay *đang trong balance* hay *vừa ra khỏi balance*, rồi bật đúng play.

### 6.1 Công tắc
| Chế độ | Nhận biết | Play được bật | Phân kỳ delta nghĩa là gì |
|---|---|---|---|
| **TRONG balance** | profile đang nở ngang, range co, TPO cân hai phía | *"xác định range rồi **2 cạnh mà vả**"* — chỉ mean-revert | *"tăng mà delta âm **là yếu**"* — không dự báo gì |
| **SAU balance** (đấu giá xong, vừa break) | bell curve/chữ nhật đã xong + giá ra khỏi VA | **follow** — *"Giờ break ra là follow theo"* | leg đầu = **ĐẦU SÓNG**: tăng mà delta âm ⇒ **chờ squeeze** (tín hiệu THUẬN) |
| **Cuối sóng / nhịp hồi** | leg thứ n, đã đi xa balance | thoát/không vào mới | tăng mà delta âm ⇒ **suy yếu** |

- ⭐ Nguyên văn CORVEN: *"Đầu sóng là dự kiến cho move mới / Cuối sóng là suy yếu / Nhịp hồi là suy yếu"*;
  điều kiện của "đầu sóng" là **ngay sau một balance** (*"Uh — sau một balance"*).

### 6.2 Đọc trước ngày mai bằng chất lượng balance hôm nay
- **IB bao trọn VA + giá đóng & mở đều trong IB + biên độ thấp** = session "đẹp" chỉ có day trader &
  short-term trader ⇒ **session sau tỉ lệ cao có TREND (breakout)**.
- **VA nằm trong IB** ⇒ phiên đó do day trader/short-term trader điều khiển.
- **Range IB ≤ 1%** ⇒ khả năng cao session sau **breakout**.
- **VA (balance) nằm trong IB của phiên ÂU với biên độ thấp** ⇒ **phiên MỸ có trend**.
- **Biên độ giao dịch hẹp** ⇒ phiên sau khả năng break **rất cao**.

**Nguồn load:** `TPO.pdf` tr.2, 3 ([note/p002-0.png](images/note/p002-0.png),
[p003-0.png](images/note/p003-0.png)) · `TRANSCRIPT.md` §13.5–13.7 · `CORVEN_SPEC_V1.md` §bổ sung 2026-08-10 ·
`00-tpo-loi-thuc-chien.md` §1 Câu 2 *(IB break — đã học)*

**Trạng thái:** `[ ]` **CHƯA HỌC.** (Đây là mục có đòn bẩy cao nhất trong cả syllabus.)

---

## 📗 Buổi 7 — ⭐ VA MOVE KHỎI RANGE: break hay reject? + chuỗi phiên Á→Âu→CME

**Mục tiêu:** khi giá rời vùng giá trị, phán được đây là break thật hay cú từ chối, và vào ở đâu.

- ⭐ **Luật gốc:** *"VA mà move khỏi range thì chỉ có 2 mục đích: **BREAK hoặc REJECT**."*
- ⭐ **Break 2 lần:** lần 1 VA break ra rồi **quay lại range** ⇒ **lần 2 luôn là clean break**. Không đuổi
  lần 1; chờ lần 2 rồi **retest tại vùng canh** mới vào.
- **Accept breakout:** tạo VA ở trên → break → **tạo VA mới ở dưới** ⇒ VA trên đã **được chấp nhận**.
  (Chấp nhận = *đã dựng được VA mới*, không phải "giá đứng ngoài một lúc".)
- **TPO breakout TIÊU CHUẨN — 2 điều kiện:**
  1. VA nằm **trên/ngay vùng breakout**, biên độ **không rộng**, phân bố **đều**;
  2. giá **quay lại test mép ngoài VA** (edge of balance) và **tập trung nhiều volume** ở đó.
- **Nhận diện FAIL break:** VA **rộng** + nằm **lưng chừng** + hôm sau **không move** mà quay lại test.
- **Sau break, giá có xu hướng đi về POC của session TRƯỚC.**
- **POC trùng/gần kháng cự–hỗ trợ ⇒ POC đó rất hay được test.**
- ⭐ **Chuỗi phiên:** *"Á build range VA cho ÂU, Âu build range VA cho CME"* ⇒ **không cần vào nhiều lệnh,
  chỉ cần canh lúc VA move khỏi range**.
- **Tip cảnh báo:** khung **18h–19h (giờ VN) rất hay xảy ra fake break VA**.
- Nối với cái đã học: **IB break 4 nhịp** (phá → 1 nến M30 đóng ngoài → retest đúng biên → trigger).

**Nguồn load:** `TPO.pdf` tr.8–10, 12 ([note/p008-0.png](images/note/p008-0.png),
[p008-1.png](images/note/p008-1.png), [p009-0.png](images/note/p009-0.png),
[p010-0.png](images/note/p010-0.png), [p012-0.png](images/note/p012-0.png)) ·
`buoi-3` §3.2 (GT-1 break 2 lần — đã học) · `00-tpo-loi-thuc-chien.md` §1 Câu 2

**Trạng thái:** `[~]` break-2-lần đã học; **accept breakout, TPO breakout tiêu chuẩn, fail-break, POC session trước, chuỗi Á→Âu→CME CHƯA học.**

---

## 📗 Buổi 8 — NỐI TPO → ENTRY: vùng hấp thụ delta + 2 play + xác nhận M1

**Mục tiêu:** biến bias TPO thành một lệnh có SL/TP cụ thể — đây là chỗ TPO giao với footprint đã học.

### 8.1 Vùng hấp thụ đọc bằng cột delta TRÊN TPO
- **Cột delta XANH lớn ở ĐỈNH mà giá đóng session ở DƯỚI** ⇒ vùng **SUPPLY** (buy market bị hấp thụ hết).
- **Cột delta ĐỎ lớn ở ĐÁY mà giá đóng session ở TRÊN** ⇒ vùng **DEMAND**.
- **Không phải vùng nào cũng có giá trị** — khi giá tới, phải kiểm 4 thứ: (a) price action có dấu hiệu đảo
  không; (b) trên footprint có gì (kiệt sức / hấp thụ / liquidity / dòng tiền đẩy vào?); (c) **delta FRESH
  hay TESTED** — chỉ fresh mới dùng; (d) vùng đó có nằm trong **"mây VA"** không.
- **Scalp ⇒ ưu tiên entry trong mây VA. Bắt đỉnh–đáy ⇒ bỏ qua mây.**

### 8.2 Hai play tại MỘT vùng (CORVEN dùng CẢ HAI — không có luật nào cấm fade)
1. **CHẠM → ĐẢO CHIỀU tại HVN**: giá tới HVN, có nến xác nhận M1 ngược lại → vào ngược.
2. **PHÁ VÙNG → HỒI VỀ → ĐÁNH TIẾP** (break-retest): phá HVN, hồi về mép, có tín hiệu → vào thuận.

### 8.3 Bất biến khi vào lệnh
- Vào lệnh **luôn ở M1**, **bắt buộc chờ nến xác nhận** — không vào lúc vừa chạm.
- **SL 2–4 giá**, neo **dưới/trên cây M1 vào lệnh**. **RR 1:3.** Đóng trong ngày, không qua đêm.
- **"KO CẢN TÀU"** — không vào ngược move đang chạy.

### 8.4 Hai ca thật để chấm
- **GCQ23 21/7:** Á build range → break lần 1 sát giờ CME → bị đẩy về range → break lần 2 (clean) →
  retest vùng supply → entry.
- **GCQ23 26/7:** Á build range cho Âu → 12h30 buyer chủ động + delta đột biến + đóng trên vùng mua →
  cây break confirm → sau break delta âm liên tục **mà giá không xuống** ⇒ tiếp tục lên.

**Nguồn load:** `TPO.pdf` tr.13–17 ([note/p013-0.png](images/note/p013-0.png),
[p013-1.png](images/note/p013-1.png), [p014-0.png](images/note/p014-0.png),
[p015-0.png](images/note/p015-0.png), [p016-0.png](images/note/p016-0.png),
[p017-0.png](images/note/p017-0.png)) · `buoi-3` §3.3–3.5 · `CORVEN_SPEC_V1.md` §1, §3, §4

**Trạng thái:** `[~]` 2 ca GCQ23 + delta fresh/tested nằm trong buoi-3 nhưng **chưa dạy tới**; §8.1 luật
4-điểm-kiểm và §8.2 hai play **CHƯA học**.

---

## 📗 Buổi 9 — Thực hành: chấm chart thật + đo bằng số

**Mục tiêu:** chuyển từ "hiểu" sang "làm được, và biết luật nào thật".

1. **Bài tập gắn nhãn** trên chart TPO thật (`data-export/TPO-chart-daily.csv`, `tpo-data/tpo-m30.csv`):
   với mỗi phiên → hình dạng → tail ổn/scam → SP chưa fix → HVN → chế độ balance → play nào.
2. **Chấm chéo:** người học gắn nhãn trước, Claude chấm sau (giống quy trình `wyckoff-giao-vien`).
3. **Đo bằng số 3 luật đáng nghi nhất** (dùng data-export, không tin theo câu chữ):
   - "IB range ≤1% ⇒ session sau breakout" — đếm được ngay.
   - "Đỉnh có LVN bị phá ⇒ trend up" — đếm được.
   - "Tail có volume dày = scam" — cần per-level, có `fp_*.csv`.
4. **Chốt vào indicator:** luật nào qua được kiểm số thì đưa vào `M30SessionZones` / `DailyTpoBias`.

**Trạng thái:** `[ ]` chưa bắt đầu.

---

## ⚖️ MÂU THUẪN GIỮA 3 NGUỒN — phải phân xử, không được lờ

| # | Sách/bản cũ nói | Note thực chiến / CORVEN nói | Cách xử |
|---|---|---|---|
| 1 | **Giá MỞ vs VA hôm qua** là câu hỏi số 1 (Dalton) | **Giá ĐÓNG** ngoài balance ⇒ VA không đúng; *"không quan tâm giá mở cửa"* | Hai việc **khác nhau**: giá đóng để **chốt sổ VA hôm nay có hợp lệ**; giá mở để **đọc mất cân bằng sáng mai**. Giữ cả hai, đúng vai. |
| 2 | VAH/VAL/POC + **80% rule** là xương sống | **Chỉ HVN + VWAP**; VAH/VAL/POC từng phiên: *"tất nhiên là không"* | CORVEN thắng ở **chọn vùng canh lệnh**. 80% rule giữ lại như **một read độc lập**, không phải trục chính. Cần đo bằng số trước khi tin bên nào. |
| 3 | P/b *"chỉ là hình dạng, không phải loại ngày"* → bản cũ **cắt** | Hình dạng là **input số 1** (*"Tpo thành chữ D"*) | Sách đúng về **phân loại**, bản cũ sai về **thứ tự dùng**. Buổi 2 dạy lại hình dạng như bước 1. |
| 4 | Delta phân kỳ = suy yếu (một nghĩa) | **Ba nghĩa** tuỳ vị trí sóng (đầu sóng = chờ squeeze) | CORVEN đúng, có cơ chế giải thích (limit dí sát giá). Đây là lý do delta-gate trong code làm tệ nhánh reversal. |
| 5 | TPO chỉ nên là **profile NGÀY** | Có tầng thứ hai: **gộp 3 tuần, period 30′** | Bổ sung, không xung đột: ngày = scalp, 3 tuần = vùng lớn. |

---

## ✂️ Vẫn giữ nguyên phần ĐÃ CẮT (không học lại)
4 tên kiểu mở cửa Latin · Normal / Normal Variation Day như hai loại riêng · 5 phân đoạn phiên ES ·
Big Smile/Frown · chiếu mục tiêu IB±width.

## ✅ Phần ĐÃ HỌC — chỉ ôn 1 dòng, không dạy lại
Cơ chế chart TPO & bracket 30′ · TPO-POC vs VPOC · IB/RE · **IB break 4 nhịp** · 80% rule · tái nhập VA
thất bại · retest single print · bear trap · kỷ luật trend day · tails/poor high-low cơ bản ·
value migration (4 quan hệ VA) · POC clustering · sizing 2% · SL cấu trúc.

## ⚠️ Cảnh báo độ tin
`TPO.pdf` đóng góp phần lớn luật hành vi mới trong syllabus này, **nhưng không rõ tác giả và chưa có luật
nào được backtest**. Học để đọc chart tốt hơn được; **đừng code thành signal trước khi đo bằng data**
(Buổi 9 làm việc đó).

---

## 📅 Thứ tự dạy đề xuất
**2 → 3 → 6 → 4 → 5 → 7 → 8 → 9**, ôn Buổi 1 lồng vào Buổi 2.
Lý do: Buổi 2 (hình dạng) và Buổi 6 (chế độ balance) là hai lỗ hổng lớn nhất và là input của mọi thứ còn lại.
