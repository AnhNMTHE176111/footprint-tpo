# KẾT QUẢ ĐO CONCEPT CROWCONCEP × DFT (2026-07-31)

> Nguồn luật: [CROWCONCEP_DFT.md](../../../data-export/messages-with-pro-trader/CROWCONCEP_DFT.md) (X1…X9),
> chép từ 7 ảnh video "leak bộ não training" của pro trader.
> Script: [crow_v1.py](crow_v1.py) (engine) · [crow_run.py](crow_run.py) (driver) ·
> [crow_bubble.py](crow_bubble.py) · [crow_retest.py](crow_retest.py) · [crow_cpos.py](crow_cpos.py) ·
> [crow_nochase.py](crow_nochase.py).
> Dữ liệu: dxFeed GCQ26 M1 (cấu trúc, cửa sổ đo 2026-05…07 vì GCQ26 chỉ thanh khoản từ tháng 5)
> + feed merged dxFeed×footprint per-level (delta + bid/ask từng mức giá, 2026-01-29→07-28, 76% nến có delta).

## 0. Phán quyết 30 giây

**Concept này, đúng như đặc tả trong 7 ảnh, KHÔNG có edge trên dữ liệu vàng GCQ26 M1 của chúng ta.**
Lõi "chase momentum sau nến phát lực" **âm hơn ngẫu nhiên có ý nghĩa thống kê** (z = −2.39, percentile 0.0%).
Không có gì được đưa vào indicator gửi lệnh. Chi tiết + cách tôi tự bác bỏ 2 ứng viên cải tiến của mình ở §4–§6.

| Thành phần | Phán quyết | Bằng chứng |
|---|---|---|
| X1+X2+X9 lõi (impulse → hồi nông → RR2) | **ÂM RÕ** | n=574, WR 29.1% @2R (break-even 33%), **−73R**/3 tháng, mọi tháng âm, null z=−2.39 |
| X3 DMA > 0 mới buy | **LÀM TỆ HƠN** | −73R → −74R (áp luôn, n=281 EV −0.263). Bản "chỉ khi biên hẹp" gần như vô hiệu (đổi 5/574 lệnh) |
| X5 vị trí "bóng nổ" (bubble) trong nến | **KHÔNG CÓ THÔNG TIN** | Hiệu ứng biến mất hoàn toàn khi so với **mức giá ngẫu nhiên trong cùng nến** (§5) |
| X6 model Hấp thụ (không cần big volume) | KHÔNG ĐỦ | n=107, −11R @2R; BE cứu về +7R nhưng phí 2 tick → −20.5R |
| X7 veto tại VWAP/vùng quan trọng | KILL (là nhiễu) | partition: EV nhóm giữ − nhóm loại = **−0.000** |
| X8 biên rộng phải chờ break | KILL | partition: chênh EV +0.035 (cần ≥ +0.30) |
| Lọc thuận xu hướng (thêm bởi tôi) | KILL | chênh EV +0.120, chỉ giảm lỗ nhờ bớt lệnh |
| FADE = vào **ngược** hướng impulse | Dương nhưng **KHÔNG ĐỦ** | +22R, WR 36.2%, mọi tháng dương, nhưng z=+1.14 và **chết ở phí 3 tick** |

## 1. Cách dựng lõi (đặc tả chốt trước khi chạy)

Đặc tả đầy đủ nằm trong docstring [crow_v1.py](crow_v1.py). Tóm lại: nến impulse = `thân/range ≥ 0.60`
+ `range ≥ 1.5 × trung vị range 100 nến TRƯỚC` (chuẩn hoá biến động, portable) + `VSA ≥ 1.5`;
nhịp hồi đo bằng `retr = (đỉnh − low)/leg`, vào ở close nến thuận hướng đầu tiên có `0.15 ≤ retr ≤ 0.50`
("không được test quá sâu"), hồi quá 50% thì **huỷ** setup; SL neo cực trị nhịp hồi kẹp [2..5 giá]; TP = 2R.
Chống look-ahead: trung vị range là **cuốn, không gồm nến hiện tại**; volfloor dùng `VOLFLOOR_FROZEN`;
liqratio cuốn theo `cbr_v6.prepare` (bản đã sửa 3 lỗi parity).

## 2. Lõi — bảng số

```
LOI mac dinh (PMAX.50 RR2)   n=574 WR=29.1% tong=-73.0R EV=-0.127 MDD=85R | 05:-11 06:-18 07:-44 ✗
```
Sweep (mỗi dòng là toàn bộ 3 tháng): PMAX 0.30→0.90 cho EV −0.203…−0.011 (**không mức nào dương**);
IMP_K 1.2→3.0: −0.147…−0.094; IMP_BODY 0.5→0.8: −0.100…−0.132; IMP_VSA 1.0→2.5: −0.136…−0.168;
RR 1.0→4.0: −0.056…−0.077 (RR=2 mà video chốt lại là **điểm tệ nhất**: −0.127);
SL[10..30]t là biến thể ít âm nhất (−0.052). WAIT 6→30 không đổi gì (entry gần như luôn xảy ra trong
vài nến đầu) — nghĩa là **hồi nông là hồi rất nhanh**, và đó chính là kiểu vào lệnh chase.

**Null model** (giữ nguyên phía + risk, ngẫu nhiên hoá thời điểm vào trong cùng ngày, 400 lần):
lõi thật −73R, ngẫu nhiên trung bình +2.1R (sd 31.4) ⇒ **percentile 0.0%, z = −2.39**.
Đây là kết luận mạnh nhất của cả đợt đo: **không phải "kém may", mà là mất tiền có hệ thống.**

## 3. Vòng 2 — tôi tự nghi ngờ mình dựng sai, và đã kiểm

Ba khả năng "Claude triển khai lệch đặc tả", đo riêng từng cái:

| Sửa | Lý do nghi | Kết quả |
|---|---|---|
| **COMPRESS**: impulse phải phá biên **vùng nén** (ảnh 1/ảnh 7 đều vẽ "sideway rồi phát lực"), không được ở giữa xu hướng | Vòng 1 cho phép impulse ở giữa trend = chase | −22…−51R, mọi biến thể âm |
| **CONFIRM**: chờ nến sau **đóng vượt cực trị nến hồi** mới vào (giống nhánh arm→confirm của KB4 vốn có giá trị) | Vào ngay nến thuận hướng đầu tiên là quá sớm | **tệ hơn**: −47…−51R |
| **COMPRESS + CONFIRM** | | −14…−37R |
| + TREND + KEY12 lên trên | | +3R với n=33 — vô nghĩa |

Không sửa nào cứu được. Ngược lại, **FADE** (vào ngược hướng impulse, cùng risk) đổi dấu ngay:
lõi +8R, +COMPRESS +10R, **+CONFIRM +22R (WR 36.2%, mọi tháng dương, MDD 16R)**.
Tức cơ chế thật trên GCQ26 M1 là **mean-reversion sau cú phát lực**, không phải continuation.

## 4. Kiểm định FADE+CONFIRM — vẫn KHÔNG đủ để ship

| Test | Kết quả | Đánh giá |
|---|---|---|
| Null model 400 lần | +22R vs ngẫu nhiên −2.9R (sd 21.8) ⇒ percentile 84.8%, **z = +1.14** | Không đạt ý nghĩa |
| Phí 0/1/2/3 tick | +22 / +13.7 / +5.4 / **−2.9R** | Chết ở 3 tick |
| Cao nguyên tham số | có: CF_WAIT 3/6/10 = +13/+22/+21; PMAX 0.30→0.75 đều dương; RR 1→3 đều dương; IMP_K 1.2→2.5 đều dương | Điểm cộng thật |
| Đa phép thử | ~60 cấu hình trong đợt này | Kỳ vọng max của 60 lần rút ≈ percentile 98% ⇒ +22R **nằm trong mức nhiễu sinh được** |
| Holdout 2026-01…04 và 2025-11…12 | **n = 0** | Vô hiệu — volume 1–2/nến chặn ở gate. Vẫn là món nợ dữ liệu độc lập từ v5 |
| Quản lý lệnh BE (SL về entry sau 1R) | +22R → +27R | Nhỏ, cùng chiều |

⇒ Không port. Nếu muốn theo đuổi thì đúng quy trình đã dùng cho KB4: port dạng **chỉ ghi CSV, không gửi lệnh**,
chạy forward 2–4 tuần lấy OOS thật (~3 lệnh/ngày ⇒ n≈60–80).

## 5. ⭐ X5 — "bóng nổ sát high thì không follow": đo sạch và bị bác bỏ

Đây là phần người học nhấn mạnh nhất, nên tôi đo 3 lớp, mỗi lớp chặt hơn lớp trước.

**Lớp 1 — partition trên tập lệnh Crow** (n=574): bubble ở 1/3 trên (sát cực trị thuận hướng) EV **−0.285**
so với **−0.045** khi bubble ở giữa nến. Cả 4 tổ hợp (nến entry/nến impulse × ô aggressor/ô volume lớn nhất)
đều cùng chiều. *Nhìn qua thì đúng như video.* Nhưng đây là partition trên một lõi đang âm ⇒ chỉ nói được
"nhóm nào ít tệ hơn".

**Lớp 2 — hiệu ứng thuần trên 30.036 nến** ([crow_bubble.py](crow_bubble.py), triple-barrier ±1.5×trung vị range,
60 nến): P(đi tiếp thuận hướng) theo vị trí bubble = 49.6% / 49.8% / 49.4% / 48.3% / 49.1% (base 49.1%).
**Không bin nào đạt 2se.** Theo tháng: chênh +0.4pp (05), −0.3pp (06), +0.4pp (07) — không ổn định.
⇒ **Vị trí bubble không dự báo hướng đi tiếp.**

**Lớp 3 — "mức bubble có thành hỗ trợ/kháng cự không"** ([crow_retest.py](crow_retest.py)).
Chỉ xét những lần giá **đã quay lại chạm** mức bubble, rồi hỏi bật hay xuyên:

```
P(BẬT khi retest)  BASE = 35.4% (n=7113)
   bubble ở đáy nến   pos<0.2  → 44.0%  (+8.6pp, 3.9se)
   bubble sát cực trị pos≥0.8  → 27.5%  (−7.9pp, 8.0se)
```
Ổn định cả 4 tháng (+13…+21pp). Trông rất mạnh — **nhưng đối chứng giết nó**: lấy một **mức giá NGẪU NHIÊN
trong chính nến đó** và đo y hệt:
```
[ngẫu nhiên] pos<0.2 → 42.5%   pos≥0.8 → 28.6%     (bubble: 44.0% / 27.5%)
tổng thể: mức ngẫu nhiên 36.6%  vs  mức bubble 35.4%  (bubble KÉM 1.2pp)
```
Và khi kiểm soát khoảng cách close→mức, ở tầng gần nhất (DIST < 0.3×range) hiệu ứng **bằng 0**
(33.2% vs 32.3%).

⇒ **Toàn bộ hiệu ứng là hình học, không phải order flow.** Cái quyết định là *mức đó nằm ở đâu trong nến*
(mức nằm phía sau nến ⇒ khi giá quay về đó thì mục tiêu đã ở gần), **không phải việc có bubble ở đó hay không**.
Kết luận này trùng khít với kết luận cũ của repo về absorption (`OrderFlowBubbles.cs` §v3.2: đo trên
538.558 ô per-level, mọi thành phần điểm về 0).

**Nói cho đúng về video:** luật "bóng nổ buy không được sát high" **có mô tả đúng một hiện tượng thật**
(mức sát cực trị dễ bị xuyên hơn — 27.5% vs 44%), nhưng phần *"vì có bubble ở đó"* không thêm gì:
một mức bất kỳ ở cùng vị trí cho kết quả y hệt.

## 6. Hai ứng viên cải tiến của chính tôi — cũng bị bác bỏ

1. **Delta ngược hướng ở nến vào thì tốt hơn** (partition Crow: ddom thuận ≥+0.10 → EV −0.281;
   ddom ngược ≤−0.10 → **+0.131**). Đo thuần trên 30.089 nến: mọi bin ddom trong ±2.3pp của base 49.2%,
   **không bin nào đạt 2se** ⇒ là hệ quả của hình học entry, không phải tín hiệu.
2. **Luật "không chase" cho CBR v5 đang ship** ([crow_nochase.py](crow_nochase.py)): trên 55 lệnh v5,
   nhóm "close sát cực trị nến vào" (cpos ≥ 0.9) có EV **+0.000** (n=20) so với **+1.400** (n=35) — PASS
   quy tắc partition của repo. Nhưng đo cùng câu hỏi ở mức nến thuần, n=7.871 ([crow_cpos.py](crow_cpos.py)):
   P(đi tiếp) theo cpos = 49.2/49.5/50.0/47.6/**47.8%** (base 48.6%) — lệch **0.8se**, và tháng 7 **ngược dấu**.
   ⇒ Kết quả trên v5 là nhiễu của n=20. **Không sửa indicator.**

## 7. Quan điểm của tôi (không có trong video)

1. **Concept này không sai — nó thiếu đúng cái phần mang alpha.** Video đưa đủ *khung* (phát lực → hồi nông →
   follow) nhưng phần vào lệnh chỉ nói "dùng Model entry, bỏ model zone trap". **Danh sách model + định nghĩa
   zone trap là ẩn số**, và toàn bộ chênh lệch giữa "âm 73R" của tôi và kết quả thật của anh ấy rất có thể
   nằm ở đó. Đây là câu hỏi số 1 cần hỏi.
2. **Trên GCQ26 M1, cú phát lực có delta lớn nghiêng về mean-reversion, không phải continuation.** Ba đường
   độc lập cùng chỉ hướng đó: FADE đổi dấu, ddom ngược ăn hơn ddom thuận, và kết luận cũ "mức dễ vỡ" của
   bubble indicator. Nếu concept của anh ấy sống, khả năng cao là do (a) khung/sản phẩm khác (XAUUSD spot,
   tick chart), (b) quản lý lệnh chủ động (thoát tay, BE sớm) chứ không phải TP cứng 2R, hoặc (c) chọn lọc
   bối cảnh bằng mắt mà không mô tả được thành luật.
3. **RR 1:2 là điểm tệ nhất trong dải RR tôi đo cho lõi này** (EV −0.127, âm hơn cả RR 1 và RR 4). Với SL
   neo cực trị nhịp hồi trên vàng M1, 2R rơi đúng vào vùng "đủ xa để hay bị quét trước, chưa đủ xa để bù".
4. **"Bóng nổ" hãy đọc là *bubble*, và đừng dùng nó làm cổng vào lệnh.** Sau 3 lớp đo (30k nến, 7k retest,
   có đối chứng ngẫu nhiên) nó không mang thông tin. Vẫn hữu ích như **công cụ đánh dấu để đọc bằng mắt** —
   đúng như `OrderFlowBubbles.cs` đã tự ghi.
5. **Vì sao tôi không sửa indicator lần này:** cả 3 ứng viên (Crow lõi, FADE, no-chase) đều không vượt cổng
   audit của repo (z ≥ 2, sống sau phí, có OOS độc lập). Ship một cái z=1.14 sau 60 phép thử là đúng cái bẫy
   mà `RESULTS_KB4.md §3` đã cảnh báo.

## 8. Việc tiếp theo (theo thứ tự giá trị)

1. **Hỏi pro trader 7 câu trong CROWCONCEP_DFT.md §6** — nhất là **danh sách Model entry** và **định nghĩa
   zone trap**. Không có phần này thì mọi backtest concept đều đang đo một hệ khác hệ của anh ấy.
2. **Đối chiếu con số "win rate 80%"**: đo trên bao nhiêu lệnh, khung nào, TP/SL thế nào, có dời SL không?
   Nếu là live có sổ lệnh thì đó là dữ liệu quý hơn mọi backtest ở đây — và nó mâu thuẫn trực tiếp với
   bảng §2, nên phải tìm ra chỗ khác nhau (rất có thể là §7.1 hoặc §7.2b).
3. **Dữ liệu độc lập** (nợ từ v5): front-month liên tục / CCPA / symbol khác. Đây là thứ duy nhất phân xử
   được overfit bằng backtest.
4. Nếu vẫn muốn theo FADE: port **chỉ ghi CSV**, forward 2–4 tuần, chỉ bật gửi lệnh nếu EV ≥ +0.10R sau phí.

## 9. ⭐ Quản lý lệnh của pro trader — đã mô phỏng, và nó GIẢI THÍCH con số "WR 80%"

> Người học cung cấp 2026-07-31: *"ngày vài chục lệnh, M1, RR 1:3. Chờ setup đủ yếu tố rồi **nhồi 5–7 lệnh**:
> 2 lệnh TP 1:3 chốt nhanh chắc tiền, 2 lệnh để chạy 1:5, 1 lệnh treo đi xe đến điểm cao nhất của **HVN ngày
> hoặc tuần** — mất lệnh đó thì các lệnh khác đã đủ lãi. Lệnh nào **đi được 1R rồi thì BE lệnh lại**."*
> Script: [crow_mgmt.py](crow_mgmt.py). Mô phỏng đúng quy tắc trên, áp lên 3 nguồn tín hiệu khác nhau.
> Runner = TP tại D-1 High (LONG) / D-1 Low (SHORT) nếu xa hơn 5R, không thì 8R; hết phiên chưa đạt thì thoát ở close.

### 9.1 "WR 80%" là tỷ lệ lệnh KHÔNG LỖ, không phải tỷ lệ ăn TP

Với BE-tại-1R, mỗi lệnh có 3 kết cục: TP / **BE (hoà)** / SL. Đo trên CBR v5 (hệ đang chạy):

| Quy tắc BE | WR thô (chỉ TP) | **WR không-lỗ (TP+BE)** | Tổng R (5 lệnh/cụm) |
|---|---|---|---|
| BE tại 0.5R | 15.6% | **78.2%** | +27.5R |
| BE tại 1.0R (như anh ấy) | 19.3% | **63.6%** | +29.1R |
| BE tại 1.5R | 24.7% | 54.5% | +35.7R |
| BE tại 2.0R | 28.7% | 50.9% | +42.9R |
| **Không BE** | 36.0% | 36.7% | **+57.1R** |

⇒ Con số **80%** rơi đúng vào vùng "BE sớm + đếm lệnh hoà là thắng". **Không có mâu thuẫn nào** giữa
"WR 80%" của anh ấy và "WR 29%" trong bảng §2 — hai con số đo hai thứ khác nhau. Điều này cũng có nghĩa
**WR 80% không phải bằng chứng hệ có edge**: kết cục BE là hoà, và tôi đã kiểm bằng nhánh Crow âm
(§9.3) — nó cho WR-không-lỗ 47% mà vẫn lỗ.

### 9.2 BE sớm là thứ tốn tiền nhất trong cả quy tắc

Trên chính hệ v5 đang chạy: BE-tại-1R làm **mất gần một nửa R** (+57.1R → +29.1R). Cơ chế rõ: lệnh bị BE
là lệnh đã đi đúng hướng 1R rồi bị hồi về entry — phần lớn trong số đó **sau đó vẫn chạy tới TP**, nhưng
mình đã bị đóng. Đây là đánh đổi trực tiếp: **mua win rate bằng tiền thật**.

### 9.3 Nhồi lệnh + chia TP: ý "1 lệnh treo đi xe" là ý ĐÚNG và đo được

Phân rã từng chân (v5, BE 1R, n=55 setup):

| Chân | TP đạt | R trung bình/lệnh |
|---|---|---|
| 2× TP 3R | 23.6% | +0.345 |
| 2× TP 5R | 16.4% | +0.455 |
| **1× runner (HVN D-1 / 8R)** | 16.4% | **+1.045** |

Thử các cách chia 5 lệnh (không BE):

| Phân bổ | Tổng R | Mọi tháng dương |
|---|---|---|
| chỉ 5× TP 3R (= v5 đang ship) | +49.0R | ✓ |
| pro trader: 2×3R + 2×5R + 1×runner | +57.1R | ✓ |
| nâng runner: 1×3R + 1×5R + 3×runner | +75.4R | ✓ |
| **chỉ runner (5× HVN/8R)** | **+93.6R** | ✓ |

⇒ Hai kết luận đo được: (a) **cấu trúc nhồi + chia TP của anh ấy tốt hơn TP 3R cứng của v5** (+57 vs +49R);
(b) **chân đóng góp gần như toàn bộ lợi nhuận là chân runner đi tới HVN**, không phải 2 chân "chốt nhanh chắc tiền".
Khớp với `RULES.md R7` ("SL càng ngắn thì tỉ lệ lệnh TP 5–6R càng nhiều") và với kết luận cũ của v5 (RR 3 > RR 1.5 cho CBR).

⚠️ **Giới hạn:** n = 55 setup, và chân runner chỉ có 9 lần đạt TP ⇒ tổng R của nó do rất ít lệnh quyết định.
Chưa kiểm null model cho riêng phần phân bổ. Đừng đọc "+93.6R" như một con số chắc chắn — đọc nó như
"hướng phân bổ đang bị đặt sai, nghiêng quá nhiều về chốt sớm".

### 9.4 Quản lý lệnh KHÔNG tạo ra edge

Áp đúng bộ quy tắc đó lên nhánh Crow âm (−73R): thành −6.4R (WR-không-lỗ 47.3%) — **vẫn âm**, tháng 6 vẫn −42R.
Nhồi lệnh + BE + chia TP chỉ **tái phân phối** kết quả, không biến tín hiệu xấu thành tốt. Ngược lại, áp lên
FADE+CONFIRM (+22R) thành +24.8R — gần như không đổi.

### 9.5 Đề xuất cải tiến cho hệ đang chạy (chưa làm, cần bạn quyết)

1. **Bỏ hoặc dời BE về ≥1.5R** trong bất cứ nhánh nào có BE. Có bằng chứng trực tiếp: mỗi bậc BE sớm hơn
   đổi ~6–14R trên 3 tháng.
2. **Thêm scale-out cho RunnerSignal**: giữ 1 phần TP 3R (như hiện tại) + 1 phần đi tới **HVN ngày/tuần**.
   Việc này cần sửa cả `mt5-runner-bridge` (hiện gửi 1 lệnh/tín hiệu) nên tôi **chưa tự làm** — đây là thay
   đổi cách chốt lời của hệ đang trade tiền thật.

## Phụ lục — số phép thử đã dùng (để đếm đa phép thử)

Vòng 1 (lõi + sweep): 27 · Vòng 1 gates + partition: 13 · Vòng 2 (COMPRESS/CONFIRM/FADE): 20 ·
Vòng 3 (ABS/BE/phí): 22 · Thí nghiệm thuần (bubble/retest/cpos/nochase): 4 script, ~30 bảng chẩn đoán.
**Tổng ≈ 82 cấu hình + 4 thí nghiệm đối chứng.** Mọi cấu hình dương duy nhất đều nằm trong §4 và đã bị
kiểm định bác bỏ.
