# Bài giảng — hệ CORVEN xâu chuỗi thành MỘT mạch (soạn 2026-08-10)

> **Mục đích file này:** 3 file kia là *nguyên liệu* — [TRANSCRIPT.md](TRANSCRIPT.md) (nguyên văn),
> [RULES.md](RULES.md) (luật rời để code), [CORVEN_SPEC_V1.md](CORVEN_SPEC_V1.md) (spec code).
> Đọc rời thì thấy một đống luật lẻ. File này xếp lại thành **7 tầng nhân–quả**: mỗi tầng chỉ hiểu được
> khi đã có tầng dưới nó. Đây là giáo án để dạy, không phải để code.
>
> **Quy ước:** ✅ = có nguyên văn CORVEN xác nhận · 🔬 = đã đo bằng backtest trong repo · ⚠️ = suy luận
> của Claude, chưa có nguyên văn · ❓ = chưa biết, cần hỏi.

---

## Sơ đồ toàn hệ — đọc trước khi vào từng tầng

```
TẦNG 1  ĐẤU GIÁ & 2 LOẠI LỆNH        "hiểu nguyên nhân với hệ quả của các order"
          │  chủ động (market) tạo MOVE  ·  thụ động (limit) CHẶN sóng
          ▼
TẦNG 2  ĐỌC MỘT NHỊP                 nhịp này tăng nhờ LỆNH GÌ?
          │  market bơm → delta dương   ·  limit kê dần → GIÁ TĂNG MÀ DELTA ÂM
          ▼
TẦNG 3  BỐI CẢNH (TPO)               đang BALANCE hay đang MOVE?
          │  balance → vả 2 cạnh       ·  hết balance → mới có sóng để follow
          ▼
TẦNG 4  VỊ TRÍ TRONG SÓNG            đầu sóng / giữa / cuối sóng / nhịp hồi
          │  ← chính tầng này ĐẢO NGƯỢC ý nghĩa của tầng 2
          ▼
TẦNG 5  KỊCH BẢN + PLAY              3 kịch bản (vùng tuần / vùng ngày / follow flow)
          │                          × 2 play (chạm-đảo / phá-hồi)
          ▼
TẦNG 6  THỰC THI                     bias phiên → entry time → xác nhận M1 → bóp SL → RR
          ▼
TẦNG 7  VÒNG LẶP                     hiểu hết → có signal → theo signal → trade nhiều → fix signal
```

---

## TẦNG 1 — Gốc của mọi thứ: hai loại lệnh ✅

> "**Chú phải hiểu nguyên nhân với hệ quả của các order.** Xong chú hiểu đc như nào là đẹp như nào k."
> "**Ví dụ limit order là chặn đc sóng. Move là nhờ market order. Market buy > sell thì move tăng lên.**"

Chỉ có **hai** vai:

| | Lệnh CHỦ ĐỘNG (market) | Lệnh THỤ ĐỘNG (limit) |
|---|---|---|
| Vai | **Tạo** chuyển động | **Chặn** chuyển động |
| Cơ chế | Nhấc/đập vào lệnh chờ của người khác | Đứng chờ người khác đập vào mình |
| Trên footprint | Buy market khớp ở **ASK** · Sell market khớp ở **BID** | Buy limit bị đập vào ⇒ hiện ở **BID** · Sell limit bị nhấc ⇒ hiện ở **ASK** |
| Delta | Là thứ **sinh ra** delta | Là thứ **hấp thụ** delta |

**Delta = ASK − BID = (khối lượng do market buy) − (khối lượng do market sell).**
Vậy delta không đo "ai nhiều hơn ai", nó đo **bên nào đang CHỦ ĐỘNG hơn**.

Đủ 8 loại lệnh (CORVEN gửi bảng — TRANSCRIPT §4), và CORVEN nói **"ăn tiền ở chỗ luận ra được lệnh gì"**:

| Loại lệnh | Khớp với | Hiện ở |
|---|---|---|
| Buy Market / Buy Stop | Sell Limit | **ASK** |
| Buy Limit / Buy Stop Limit | Sell Market | **BID** |
| Sell Market / Sell Stop | Buy Limit | **BID** |
| Sell Limit / Sell Stop Limit | Buy Market | **ASK** |

Điểm cần nhớ: **Buy Stop nằm cùng cột với Buy Market** (đều ở ASK) nhưng **hành vi khác nhau** —
> "**di chuyển nhờ quét stoploss chạy mạnh nhưng k đi được xa, vì hành vi khác với chủ đích buy**" ✅

⇒ Cú chạy do quét stop trông y hệt cú chạy do người ta thật lòng muốn mua, trên delta cũng giống. Phân
biệt bằng **bối cảnh** (nó vừa phá cực trị swing nào không), chứ không bằng con số delta.

**Câu hỏi kiểm tra 1.1:** Một ô footprint hiện `Bid 40 × Ask 5`. Đã có những loại lệnh nào chắc chắn
tham gia vào con số 40 đó?
**1.2:** Tại sao "delta dương" *không* đồng nghĩa với "nhiều người mua hơn người bán"?

---

## TẦNG 2 — Đọc một nhịp: nó tăng nhờ lệnh gì? ✅ (luật lõi số 1 của CORVEN)

> "**một nhịp tang chú phải phân tích xem nó tang nhờ lệnh gì.** nó đẩy chủ yếu nhờ **limit buy kê cao
> dần lên** làm giá tăng — **khác với buy market chủ động bơm vào**."
> "**Limit vẫn làm cho giá tăng đc nhưng nó làm một kĩ thuật khác: dí limit sát theo giá.**"
> "**Dí sát limit vào giá giữ trend. Giá lên nó nâng limit sát vô giá. Này chú nhìn order book là rõ luôn.**"

Hai cách làm giá tăng — **cùng kết quả trên nến, ngược nhau trên delta**:

| | Cách A — market bơm | Cách B — "dí limit sát giá" |
|---|---|---|
| Việc bên mua làm | Đập buy market liên tục, ăn hết sell limit phía trên | Không mua chủ động; chỉ **liên tục nâng buy-limit lên sát giá** |
| Ai là người khớp chủ động | **Bên mua** | **Bên bán** (họ đập sell market vào limit đó) |
| Khối lượng dồn ở cột | **ASK** | **BID** |
| Delta | **dương mạnh** | **âm** — dù giá đang lên |
| Nến | tăng | **cũng tăng** |

Đây chính là lời giải cho hiện tượng người học quan sát cả tuần:
> "**nhiều move tăng nhưng đường delta lại cắm xuống, move đấy càng dài thì delta càng âm. Move giảm thì
> delta dương lên cao.**" → CORVEN: "**Nó dí sát limit đấy.**"

**Cơ chế của cách B:** bên mua không muốn trả giá ASK (trượt giá, lộ ý định). Họ kê một bức tường bid
ngay dưới giá; người bán nào muốn thoát thì đập vào tường đó. Tường không lùi, mà **nhích lên theo giá**
⇒ giá không thể xuống, và mỗi lần có người bán là **delta lại âm thêm**. CORVEN cũng nói cùng cơ chế này
từ tháng 1: "**big nó thường kê limit ở range để đỡ trượt giá, còn phần nhỏ thì dùng iceberg**". ✅

⚠️ **Đây là chỗ tôi (Claude) từng hiểu sai và đã ghi sai vào RULES.md:** tôi coi "giá tăng + delta âm"
là **luật vô điều kiện = nhịp giả, loại bỏ**. Sai. Nó là **một hiện tượng**, ý nghĩa do tầng 4 quyết định.
Cách đọc đúng nằm ở tầng 4.

**Câu hỏi 2.1:** Giá đi từ 3350 → 3358, tổng ASK 1.200 / tổng BID 2.900. Ai đang là bên khớp chủ động,
và bên còn lại đang làm gì?
**2.2:** Vì sao chỉ nhìn footprint là **đoán**, còn nhìn order book là **thấy**? (CORVEN: "fp chỉ toàn
hợp đồng thôi, chú phải **đoán** là buylimit hay buy market — **đoán có cơ sở** ấy")

---

## TẦNG 3 — Bối cảnh: đang BALANCE hay đang MOVE? ✅

Trước khi diễn giải bất cứ delta nào, phải biết thị trường đang ở **chế độ** nào. CORVEN dùng TPO cho
việc này, và có **hai** tầng profile:

| Dùng để | Cấu hình | Nguyên văn |
|---|---|---|
| Scalp trong ngày | **TPO daily** | "**Day scap nhìn tpo daily** :))" |
| Vùng lớn, bao quát | **TPO gộp 3 TUẦN, 1 period = 30 phút** | "**Gộp 3 week / 1 preiod vẫn là 30p**"; "Tpo ngày thì hơi nhỏ nên t nhìn hẳn tuần cho bao quát" |
| Kiểm chất lượng đấu giá | **tail** (đuôi), **single print** | "**Check tail các thứ xem ổn hết chưa**" |
| Hình dạng | chữ **D** = đã đấu giá xong = **balance** | "Tpo thành chữ D à — **Chữ D**" |

**Hai chế độ, hai cách chơi hoàn toàn khác nhau:**

**(a) ĐANG TRONG BALANCE** ✅
> "**Trong balance thì chop. Trong balance thì xác định range rồi 2 cạnh mà vả thôi.
> Thì cứ tăng mà delta âm là yếu.**"

- Không đi tìm sóng. Không follow đà.
- Xác định range → đánh **hai cạnh** (đây đúng là kịch bản KB-B).
- Trong chế độ này, phân kỳ delta trở lại nghĩa đơn giản nhất: **tăng mà delta âm = yếu**.
- Ăn khớp với luật Wyckoff tháng 5: "**k cần nhãn nhiếc đâu, xác định range thôi là đc, rồi nhìn phân
  tích vol trong range**" ✅

**(b) ĐÃ RA KHỎI BALANCE** ✅
> "Giờ **break ra là follow theo**." (caption ảnh TPO 3 tuần)

- Lúc này mới có "sóng", mới có "đầu sóng / cuối sóng", mới áp được tầng 4.
- Đây là kịch bản KB-C: **follow order flow, "ko cản tàu"**.

🔬 **Số trong repo ủng hộ ý này:** nhánh fade (cản tàu) trong KB2 = FAIL, EV sụp về ≈0; nhánh thuận đà
KB1 = +47R. Và `hvn_week` là loại vùng **duy nhất** dương (WR 57%, EV +0.429) còn `hvn_day` tệ nhất
(WR 25%, EV −0.375) — khớp với "TPO ngày hơi nhỏ".

⚠️ **Hệ quả cho code (chưa làm):** hệ hiện tại chạy cả 3 engine song song mọi lúc. Theo tầng này, phải
có một **công tắc chế độ**: trong balance ⇒ chỉ bật engine vả-2-cạnh; ra khỏi balance ⇒ mới bật follow-đà.

**Câu hỏi 3.1:** TPO hôm nay ra hình chữ D đẹp, không đuôi. Được phép đi tìm setup follow-đà chưa? Vì sao?
**3.2:** Vì sao cùng một hiện tượng "tăng mà delta âm" mà trong balance thì kết luận thẳng là "yếu",
còn ngoài balance thì phải xét thêm?

---

## TẦNG 4 — ⭐ Vị trí trong sóng: tầng ĐẢO NGƯỢC ý nghĩa của tầng 2 ✅

Đây là mảnh ghép quan trọng nhất của batch chat mới, và là mảnh mà cả hệ code đang thiếu.

> "**Đầu sóng là dự kiến cho move mới. Cuối sóng là suy yếu. Nhịp hồi là suy yếu.**"

Cùng một tín hiệu "giá tăng mà delta âm", ba vị trí, ba kết luận **trái ngược**:

| Vị trí | Kết luận | Nguyên văn |
|---|---|---|
| **ĐẦU SÓNG** (ngay sau một balance) | **THUẬN** — dự báo sắp có nhịp mạnh, delta sẽ đảo sang dương (squeeze) | "**T bảo chưa phải squeeze vì tăng delta vẫn âm… nó ở đầu sóng, thì dự sau đó sẽ có một nhịp mạnh, thì tối là một nhịp bay mạnh squeeze delta dương**" |
| **CUỐI SÓNG** | **NGƯỢC** — suy yếu, sắp rớt | "**Còn hôm nay, tăng delta đang âm, ở cuối sóng, là suy yếu. Chỉ cần tối delta k dương mạnh mà seller vào mạnh tạo ra nến giảm là rớt**" |
| **NHỊP HỒI** | **NGƯỢC** — suy yếu | "**Nhịp hồi là suu yếu**" |

**"Đầu sóng" có định nghĩa vận hành rõ ràng** — người học hỏi thẳng và được xác nhận: ✅
> **Benzo:** "điều kiện là move đấy phải nằm ở **ngay sau đấu giá xong** à"
> **CORVEN:** "**Uh. Sau một balance.**"

**Cơ chế (⚠️ Claude diễn giải, CORVEN không nói ra):** ngay sau một balance, bên bán vẫn tin vào range
nên tiếp tục bán vào tường limit bid → delta âm. Nhưng giá **không xuống được**. Số hợp đồng short đó
chính là **nhiên liệu**: khi tường bid tiếp tục nhích lên và ai đó bắt đầu mua market, short buộc phải
cắt ⇒ **buy stop kích hoạt hàng loạt ⇒ squeeze, delta bật dương**. Ở cuối sóng thì ngược lại: người muốn
mua đã mua hết, tường limit chỉ còn là cái đỡ cuối cùng — hết là rớt.

⇒ **Công thức đọc, gộp tầng 2 + 3 + 4:**

```
tín hiệu     = phân kỳ delta (giá lên, delta âm — hoặc đối xứng)
chế độ       = BALANCE?  →  "yếu", hết. Đánh 2 cạnh range.
             = ĐÃ BREAK? →  xét vị trí:
                   ĐẦU SÓNG (ngay sau balance) → chờ SQUEEZE, đánh THUẬN
                   CUỐI SÓNG / NHỊP HỒI        → SUY YẾU, đánh NGƯỢC
```

⚠️ **Đây là lời giải cho một bí ẩn trong repo:** ghi chú cũ nói *"delta-gate làm tệ nhánh reversal"* —
tức là ép `delta cùng hướng giá` thì nhánh quay đầu tệ đi. Theo tầng này thì đúng như vậy: nhánh quay
đầu làm việc ở **cuối sóng/nhịp hồi**, nơi mà **phân kỳ delta là tín hiệu TỐT**, thế mà gate lại loại nó.
Một ngưỡng delta duy nhất cho cả hai nhánh là sai từ thiết kế. (❓ chưa test — đây là giả thuyết đáng đo nhất.)

**Câu hỏi 4.1:** Giá vừa phá lên khỏi range đi ngang cả sáng, nhịp phá có delta âm. Long, short, hay đứng ngoài?
**4.2:** Cùng cấu hình đó nhưng xảy ra ở nhịp hồi thứ ba của một xu hướng tăng đã chạy dài. Đổi kết luận thế nào?
**4.3:** Vì sao CORVEN nói "**chưa phải squeeze**" chứ không nói "không phải squeeze"?

---

## TẦNG 5 — Ba kịch bản × hai play ✅

**Ba kịch bản** (người học chốt lại, CORVEN xác nhận "Uh / Đúng r"):

| # | Kịch bản | Vùng neo | Kiểu | Tần suất |
|---|---|---|---|---|
| **KB-A** | Chạm vùng **lớn** → phản ứng | **HVN tuần** (⇒ nay là **TPO 3 tuần**), **VWAP tuần** (neo đầu tuần) | Vẫn vào **M1**, đóng **trong ngày**, WR cao nhất | ~10 lệnh/tuần |
| **KB-B** | Scalp phản ứng | **HVN ngày**, **VWAP ngày** | Mean-revert tại vùng | Cao |
| **KB-C** | **Follow order flow** | Không cần vùng — theo footprint | Thuận đà, **"KO CẢN TÀU"** | "vài chục lệnh/ngày" |

**Hai play tại CÙNG một vùng** — không phải hai kịch bản:
1. **CHẠM → ĐẢO CHIỀU** tại vùng, có nến xác nhận M1 ngược lại → vào ngược.
2. **PHÁ → HỒI VỀ → ĐÁNH TIẾP** (break-retest): "**đánh break**" của CORVEN nghĩa là **phá ra khỏi vùng,
   chờ hồi về mép vùng + có tín hiệu** rồi mới vào thuận hướng phá. ✅
   ⚠️ Tôi từng hiểu "đánh break" = đánh breakout của range M1 và viết vào RULES.md rằng hệ này "cấm fade" —
   **sai cả hai**. CORVEN dùng **cả hai** play.

Chỉ dùng **HVN + VWAP**. **Không** dùng POC / VAH / VAL, và **tuyệt đối không** dùng VAH/VAL/POC từng
phiên Á-Âu-Mỹ ("Tất nhiên là không rồi"). ✅

**Tín hiệu vào của KB-C** (không cần VSA, không cần volume climax) ✅: đang trong một move
(**chuỗi nến cùng chiều + delta liên tiếp cùng dấu**, không cần delta tăng dần), rồi thấy một nến **đẩy
chủ động** — ví dụ move tăng: **bubble big trade nằm ở 30% dưới của nến** + **delta nến xanh** + **thân
đủ dài, đóng đẹp** → LONG. Các dấu hiệu chủ động khác được dùng: **imbalance**, **big trade**.
🔬 ⚠️ Riêng phần "vị trí bubble" đã **đo và bác bỏ**: vị trí bubble không mang thông tin (z=−2.39, lõi âm
hơn ngẫu nhiên) — xem CROWCONCEP_DFT.md. Đây là điểm hệ CORVEN nói mà số của mình **không** xác nhận.

**Câu hỏi 5.1:** Giá đang ở HVN tuần. Có mấy cách đánh hợp lệ, và mỗi cách chờ tín hiệu gì?
**5.2:** Vì sao KB-A "hold dài" mà SL vẫn 2–4 giá y như scalp?

---

## TẦNG 6 — Thực thi: nơi phần lớn tiền được quyết định ✅

Thứ tự bắt buộc — **bias trước, entry sau**:

> "**đưa ra bias thì cần nhiều chú ạ. T phải can đo đong đếm giữa buy và sell, xem bên nào đang kiểm
> soát thì theo bên đó. Bias tang thì chỉ canh mua. Mua thì mua đến đâu canh sell. Mỗi phiên sẽ có một
> bias. Xong vào low tìm entry thôi.**"

| Bước | Luật | Nguyên văn |
|---|---|---|
| 1. Bias | **Một bias / một phiên**, khoá lại. Bias tăng ⇒ **chỉ** canh mua | "mỗi phiên sẽ có một bias" |
| 2. Giờ | **RR theo entry time**. Sáng ~7h chạy mạnh, **entry time là 8h**; chiều sideway nhiều | "t chơi RR theo entrytime" |
| 3. Xác nhận | Vùng đẹp nhưng **thiếu xác nhận M5/M1 ⇒ KHÔNG vào** | "mọi thứ đề chuẩn chỉ rồi, thiếu mỗi xác nhận trong m5, m1" |
| 4. SL | **Bóp 2–4 giá, neo dưới cây M1 vào lệnh.** Đừng ngắn quá kẻo lỗ phí | "**Bóp sl thì mới có cơ sở gồng dài**"; "**Sl càng ngắn thì tỉ lệ lệnh tp 5-6R càng nhiều**" |
| 5. RR | CORVEN: 1:5–1:6 khi vào giờ ngon. **Hệ của mình chốt RR 1:3 cố định, WR mục tiêu 40–50%** | Người học chốt 2026-07-31 |
| 6. Không nhồi | Vào **một phát**, không pyramiding | "**nhồi hay quét vl**" |
| 7. Không phải AND-gate | **Pass ~70% checklist là vào** (điểm số, không phải chuỗi điều kiện cứng) | "Hợp lý đấy chú" |

**Hai bài học chống-trực-giác, phải nhớ kỹ** ✅:
- **"Đi lên k có ai bán thì nó vẫn lên mà chú."** ⇒ **Volume thấp KHÔNG phải tín hiệu đảo.** Cạn cung ≠ có cầu.
- Muốn SHORT thì **chính các cây GIẢM phải ngon**: "**Chú xem cây giảm vol có ngon k / Đóng có đẹp k /
  Mấy cây giảm đóng râu dưới vẫn rút kìa**". Râu dưới bị rút = có người đỡ = chưa được short.

**Câu hỏi 6.1:** Bias phiên là tăng, giá chạy tới HVN tuần phía trên và có nến đảo chiều M1 rất đẹp.
Vào short không?
**6.2:** Vì sao SL ngắn lại **tăng** tỉ lệ lệnh 5–6R, chứ không phải giảm?

---

## TẦNG 7 — Vòng lặp xây hệ (CORVEN nói thẳng quy trình) ✅

> "**Chú phải hiểu hết → Xong có signal → Rồi theo signal thôi → Xong trade nhiều fix signal →
> Lúc trade k bị phân vân với lưỡng lự → Rồi fix tâm lý đúng theo rule là đc.**"
> "**Trade thật mới cảm xúc. Học có gì đâu.**"
> "T học nhiều phết đấy nên mới hiểu hết. **Tpo với fp gần như nắm đc hết rồi. Chú chỉ hiểu phần ngọn thôi.**"
> "**T chỉ signal sơ sơ thôi. Nó còn nhiều rule đấy.**"

Bốn điều rút ra:
1. **Thứ tự không đảo được:** hiểu cơ chế **trước**, signal **sau**. Signal không có cơ chế đỡ thì không
   biết đường sửa khi nó sai — đúng đoạn người học tự nhận: "chưa biết cải tiến gì tiếp vì đ hiểu sâu".
2. **Signal tồn tại để loại bỏ do dự**, không phải để thay thế hiểu biết.
3. **Vòng sửa là: trade thật → phát hiện signal sai ở đâu → sửa signal.** Backtest không thay được vòng này.
4. **CORVEN chưa nói hết** — "nó còn nhiều rule đấy". Bộ luật trong repo là **phần ngọn**, tự nhận là chưa đủ.

---

## Bảng theo dõi: cái gì đã chắc, cái gì chưa

| Nội dung | CORVEN nói | Repo đo được | Trạng thái |
|---|---|---|---|
| Vùng khung **tuần** tốt hơn khung ngày | ✅ | 🔬 `hvn_week` EV +0.429 vs `hvn_day` −0.375 | **khớp** |
| "Ko cản tàu" — thuận đà ăn hơn fade | ✅ | 🔬 KB1 +47R vs KB2 fade ≈0 | **khớp** |
| Scalp neo **VWAP ngày** | ✅ | 🔬 bản neo VWAP là bản duy nhất còn dương (+10.5R) | **khớp** |
| Vị trí **bubble big trade** trong nến là tín hiệu | ✅ | 🔬 **bác bỏ** (z=−2.39, không mang thông tin) | **vênh** |
| **R12** — vị trí sóng đảo nghĩa của phân kỳ delta | ✅ | ❓ chưa đo | **đáng đo nhất** |
| Công tắc **chế độ balance / move** | ✅ | ❓ chưa có trong code | **thiếu** |
| TPO **gộp 3 tuần, period 30p** | ✅ | ❓ đang dùng cửa sổ khác | **phải sửa lại rồi đo** |
| Kiểm **tail / single print** | ✅ | ❓ chưa có | **thiếu** |
| Tần suất "vài chục lệnh/ngày" | ✅ | 🔬 hệ hiện tại ~1 lệnh/ngày | **khoảng cách lớn nhất** |
| Nhánh **KB-A** (vùng tuần) | ✅ CORVEN xếp đầu, WR cao nhất | ❓ **chưa xây engine nào** | **vùng tối lớn nhất** |

---

## Đề nghị lộ trình dạy — 6 buổi

| Buổi | Nội dung | Tài liệu kèm |
|---|---|---|
| 1 | Tầng 1 — đấu giá, 8 loại lệnh, delta là gì thật sự | Bài 1–2 khóa Footprint + bảng 8 lệnh |
| 2 | Tầng 2 — limit kê vs market bơm, đọc trên footprint thật | ảnh footprint trong `course/images/` + data-export |
| 3 | Tầng 3 — TPO: balance/chữ D, tail, single print, 2 tầng profile | ảnh TPO của CORVEN + indicator DailyTpoBias |
| 4 | Tầng 4 — vị trí sóng × phân kỳ delta (buổi **quan trọng nhất**) | dựng chart ví dụ 3 ca từ data thật |
| 5 | Tầng 5 — 3 kịch bản × 2 play, tín hiệu vào từng nhánh | TRUONG_LINH_3_KICH_BAN + CORVEN_SPEC_V1 |
| 6 | Tầng 6–7 — bias/giờ/SL/RR + vòng lặp fix signal, rồi soi lại hệ code đang lệch đâu | RULES.md + bảng theo dõi ở trên |

---

## Câu nên hỏi CORVEN tiếp (ưu tiên theo mức chặn)

1. **"Đầu sóng" tính được bao xa?** Sau balance thì cửa sổ "đầu sóng" dài mấy nến / mấy giá thì hết hạn?
2. **Nhận biết "cuối sóng"** bằng gì — số nhịp, biên độ so với range, hay bằng chính delta?
3. **Balance kết thúc lúc nào** — phá biên bao nhiêu giá thì coi là đã ra khỏi balance?
4. **Tail thế nào là "ổn"** — dài mấy TPO, ở cạnh nào thì đáng tin?
5. TPO gộp 3 tuần: **rolling 3 tuần** hay 3 tuần lịch cố định?
6. Ba kịch bản đóng góp lợi nhuận thế nào — cái nào ra tiền chính?
