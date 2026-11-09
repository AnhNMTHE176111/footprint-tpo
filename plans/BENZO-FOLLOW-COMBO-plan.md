# Benzo FOLLOW-COMBO — thiết kế đo các combo "Follow sau cú phá" (Fable, 2026-11-09)

> Mục 11 của `BENZO-CORVEN-plan.md` tách ra file riêng vì dài. **Đây là bản ĐĂNG KÝ TRƯỚC**: mọi định nghĩa, combo, tiêu chí
> chọn viết ở đây **trước khi chạy số**; hash commit của file này là mốc. Sửa gì sau khi đã nhìn số phải ghi "hậu kiểm" và chỉ
> được xác nhận bằng dữ liệu chưa nhìn. Opus làm theo mục 7, không hỏi lại; thiếu gì thì chọn cách đơn giản nhất và ghi vào báo cáo.
> **Không đụng** `setup_corven.py` (đang là chuẩn parity của port GĐ3) và các file C# — việc này chạy song song, chỉ thêm file Python mới.

## 0. Yêu cầu của người học và ví dụ gốc

Nguyên văn: *"range này tôi có 1 setup đó là break hẳn range, có trap sell, và nến sell cũng là nến nhịp hồi, và sau đó trong vòng 3 nến
có nến cf. Đây là tín hiệu nguyên thủy nhất của follow, là dựa vào move, tín hiệu hồi về có trap và nến cf. Sau đó corven có thêm các
combo nữa khi kết hợp với stack imbalance hoặc kiệt sức."* Hai combo minh hoạ: (1) hồi nhẹ không trap, CF có **bóng buy + delta xanh +
đóng cao** → buy; (2) hồi nhẹ không trap, CF có **kiệt sức sell + delta xanh + đóng cao** → buy. Yêu cầu: brainstorm combo có tên, **đo
trực tiếp từng combo**, review chọn combo tốt, **mổ lệnh SL** để cải tiến dần.

Ảnh gốc (GCZ26 M1, trục giờ = giờ máy người học ≈ 11:25–11:35, không có ngày; giá ≈ 4126–4138 ⇒ đầu 11/2026, **sau mốc 21/10 của file 90d
⇒ ca này KHÔNG có trong dữ liệu đã xuất**, chỉ dùng làm ca neo định nghĩa + ca unit test tổng hợp). Đọc trên ảnh:
- Range vàng nhạt, cạnh trên ≈ 4131; cú phá lên gồm nến +9/+6 rồi nến đóng ngoài.
- Nến hồi: 1 nến đỏ nhỏ, **chấm đỏ ở đỉnh** (ô Bid lớn ở phần trên nến = phe sell lao vào ở đỉnh) — người học gọi là **trap sell**, và chính nến này là nhịp hồi.
- CF: nến tăng ngay sau, **Δ +26, có chấm xanh** (bóng buy), đóng 4132,2 cao hơn nến hồi ⇒ vào buy ở giá đóng.
- SL 4129,1 (dưới cạnh ≈ 2 giá, rủi ro 3,1) · TP 4138,5 (6,3 = **2,03R**) · chạm TP (hai nến +9 rồi đỉnh −39/−55).
- Ghi chú trên ảnh: *"Nến cf chỉ cần tăng với delta xanh và đóng ở giá cao hơn"* ⇒ CF Follow **lỏng hơn 4a** (không đòi thân 0,4 / đóng sát 0,3).

Đối chiếu nguồn CORVEN (`corven-meet/2026-11-07/transcript.md`): 0:05:36 "trap … xong phá cấu trúc thì sẽ mạnh"; 0:05:41 "follow trend:
giá đi lên tạo stacked, xong test về"; 0:18:13 "đẩy mạnh, test về stacked mà không phản ứng ngược thì buy thôi"; **0:46:13 "delta buy với bóng
xanh phải vào thì mới có tín hiệu — trap xong, buy có vào đâu, nhỏ mà, không có bóng xanh"**; **0:48:07 "trap xong nhưng buy hơi yếu → vẫn không
vào"**; 0:08:23 "trap sell, nhưng đoạn sau buy yếu thì không vào được". ⇒ Hai câu in đậm chính là combo 1 của người học: **trap một mình
chưa đủ, CF phải có lực (delta + bóng)**. Đây là căn cứ để F1 "nguyên thủy" và F4 "trap + bóng CF" là hai combo khác nhau.

## 1. Khác gì so với Thế B đang port (mục 1 plan chính)

| | Thế B (`setup_corven.py`, đang port) | Follow (file mới) |
|---|---|---|
| Lúc nào được xét | sau `BreakConfirmed` (K = 3 nến không đóng lại) | **ngay từ nến đóng ngoài** (`CloseOutside`); huỷ nếu `FailBreak` |
| Mốc | cạnh vừa phá / stacked mới, giá phải **hồi về mốc** (≤ 1 mbr) | **nhịp hồi 1–2 nến ngay sau cực trị cú đẩy**, không đòi về cạnh |
| Xác nhận | ≥ 2 dấu hiệu bất kỳ trong 5 loại | **từng combo có tên**, đo riêng |
| CF | 4a (thân ≥ 0,4 · đóng–cực trị ≤ 0,3 · biên ≥ 0,5 mbr · Δ ≥ 0,5 medΔ) | **tăng · Δ·D > 0 · đóng cao hơn nhịp hồi** (4a chỉ là biến thể báo cáo) |
| Mục tiêu | E ∓ chiều cao range, đòi R sẵn ≥ 1,7 | **TP 2R, không cổng mục tiêu** (như ảnh); cổng 1,7R là biến thể báo cáo |

Trong ảnh, CF là nến **thứ 2 sau nến đóng ngoài** ⇒ chưa có `BreakConfirmed` ⇒ Thế B hiện tại **không bao giờ bắt được ca này**. Đây là lỗ
hổng cấu trúc thật, không phải chỉ là tinh chỉnh tham số — lý do chính tôi cho đo tiếp (xem mục 8).

## 2. ĐỊNH NGHĨA MÁY MÓC (ký hiệu như plan chính: tick 0,1 · mbr · tol = max(2 tick, 0,5 mbr) · medΔ · nền_ô; chỉ xét nến đã đóng)

Hướng D = +1 (phá lên, buy) / −1 (phá xuống, sell). Mọi so sánh giá viết cho D = +1; D = −1 lật dấu.

**2a. Move (cú đẩy).** Sự kiện `CloseOutside` của `RangeEngine` tại nến `ref` ở cạnh E (range ACTIVE hoặc BROKEN còn tuổi ≤ 30 nến — nhánh
"leg 2" bên dưới). Move = chuỗi nến từ `ref` tới **nến cực trị x** (nến có high cao nhất tính tới lúc đó, chưa bị nến sau vượt). Điều kiện
"có momentum" (CORVEN "để ý momentum", chi-tiet 2.2):
- `high[x] − E ≥ 1,0 mbr` (đẩy hẳn ra ngoài, không chỉ chọc râu);
- `ΣΔ(ref…x) · D > 0` (phe D chủ động — đã có ở ⛔ "quét stop" plan chính).
- Nhãn đo thêm, **không phải cổng**: `move_strong` = ΣΔ(ref…x) ≥ 3 medΔ **hoặc** có nến trong move thân ≥ 0,7 biên độ và |Δ| ≥ 2 medΔ.
- `FailBreak` (đóng lại trong range trong K nến) ⇒ **huỷ** mọi ứng viên của cú phá này (giữ đúng "phá thì phải giữ được").
- **Leg 2:** sau khi đã có 1 nhịp hồi + CF (hoặc hết hạn), nếu giá lập **cực trị mới** x′ > high[x] trong tuổi 30 nến của BROKEN và chưa `ReEntry`
  ⇒ cú đẩy mới với x = x′, cùng E. Tối đa **2 leg / cú phá**; cột `leg` ∈ {1, 2}, báo tách.

**2b. Nhịp hồi.** Nến i > x là **nến hồi** nếu `high[i] ≤ high[x]` (không lập cực trị mới) **và** `close[i] < close[x]`. Nhịp hồi = các nến hồi
liên tiếp bắt đầu từ x+1; **≥ 1 nến** (ảnh: đúng 1 nến). Độ sâu `depth = high[x] − min(low[nhịp hồi])`; `move_h = high[x] − E`.
- "Không quá sâu": `min(low[nhịp hồi]) ≥ E − tol` (râu chạm cạnh được, như ví dụ 2 CORVEN); nến hồi đóng trong range = `FailBreak` ⇒ huỷ (đã có ở 2a).
- Nhãn đo: `shallow` = depth ≤ 0,5 · move_h ("giảm nhẹ về" của người học); `deep` = depth > 0,7 · move_h.
- Hết hạn: không có CF ở nến ≤ **x + 3** ⇒ ứng viên chết ("trong vòng 3 nến"). Tham số `cf_within` = 3 cố định ở vòng 1; biến thể {4} chỉ báo cáo.

**2c. CF Follow.** Nến c, x+2 ≤ c ≤ x+3, có ≥ 1 nến hồi trước nó, thoả:
- `close[c] > open[c]` (tăng) · `Δ[c] > 0` (delta xanh) · `close[c] > max(close[nhịp hồi])` (đóng cao hơn nhịp hồi — "đóng ở giá cao hơn");
- **không** đòi thân/đóng sát/biên độ/Δ ≥ 0,5 medΔ. Nhãn đo: `cf_4a` = c thoả 4a đầy đủ (để biết cổng cũ đã loại bao nhiêu ca Follow đẹp).
- Biến thể báo cáo `cf_strict`: thêm `close[c] > high[nhịp hồi]` (lấy lại toàn bộ nhịp hồi).

Ứng viên **F0** = (move hợp lệ, nhịp hồi hợp lệ, CF Follow). Mỗi F0 là **một dòng** trong `_follow_cands.csv` với toàn bộ cờ dấu hiệu bên
dưới = true/false + số đo. Chính F0 cũng là **đối chứng C1**.

**2d. Dấu hiệu (cờ trên từng F0; mỗi cờ có nến neo và con số):**

| Mã | Tên | Định nghĩa máy móc (D = +1) | Nguồn |
|---|---|---|---|
| **T** | Trap sell ở nhịp hồi | trong nhịp hồi có nến p với ô **Bid** ≥ 3 × nền_ô và ≥ 10 hợp đồng, ô nằm ở **nửa trên** nến p (giá ô ≥ trung điểm p) **và** `close[c] > giá ô` (phe sell lao vào ở đỉnh nhịp hồi, tới khi CF đóng thì đã lỗ = bị kẹt). Nến neo = p, số = side-volume ô / nền_ô | ảnh (chấm đỏ ở đỉnh nến hồi); 0:19:23 |
| **Bc** | Bóng buy ở CF | ô **Ask** của c ≥ 3 × nền_ô, ≥ 10 hợp đồng, nằm ở **nửa dưới** c (= ③b nhưng nến neo **bắt buộc là c**) | ảnh (chấm xanh ở CF); 0:46:13 |
| **K** | Kiệt sức sell ở đáy hồi | `ExhaustionLogic.Detect` đáy (Bid nhỏ) tại nến hồi **hoặc** tại c, mức đó chưa bị râu quét (`IsSwept`, 1 tick) tới khi c đóng | combo 2 người học; 0:54:43 |
| **S** | Stacked mới giữ được | vùng stacked buy (250 %, run 3, Body, không Weak) sinh trong move (ref…x), nhịp hồi có râu chạm [Lo − tol, Hi + tol] **và** không nến nào đóng dưới Lo | 0:05:41, 0:18:13 |
| **Dh** | Δ ngược giá ở nhịp hồi | `ΣΔ(nhịp hồi) > 0` trong khi giá hồi xuống (giá giảm, delta vẫn dương = phe sell không có, phe buy hấp thụ) | ③a dạng ngược giá, lật cho Follow |
| **Dc** | Δ to ở CF | `Δ[c] ≥ 2 × medΔ` | ③a dạng "to" |
| **Sh** | Hồi nông | `shallow` (2b) | "giảm nhẹ về" |
| **Mv** | Move mạnh | `move_strong` (2a) | "để ý momentum" |
| **Vk** (veto) | Kiệt sức buy ở đỉnh move | kiệt sức **đỉnh** (Ask nhỏ) tại x hoặc nến hồi, chưa bị quét tới c ⇒ **loại** F0 | ⛔ plan chính, 0:53:05 |

Lưu ý định nghĩa: **T ở đây khác ③e cũ** (③e = râu quét qua mốc rồi đóng lại). T của Follow là "phe ngược lao vào ở cực trị nhịp hồi rồi bị
kẹt" — bám đúng chữ người học và ảnh. Không gộp hai cái; ③e không dùng trong file này.

**2e. Lệnh.** Vào ở `close[c]`. Hai neo SL, **đo cả hai, neo chính = S2**:
- **S2 (chính, theo ảnh + 4.2 "sau mốc quan trọng gần nhất" = cạnh vừa phá):** SL = `min(E, min low[nhịp hồi ∪ c]) − đệm`, đệm = max(3 tick, 0,2 mbr).
- **S1 (báo cáo):** SL = `min(low[nhịp hồi ∪ c]) − đệm` (sát hơn; nếu < sàn thì đẩy ra).
- Sàn 1,0 mbr · trần 4,0 mbr (bỏ lệnh) — giữ nguyên plan chính.
- **TP = 2R cố định, KHÔNG cổng mục tiêu** (chính, theo ảnh). Biến thể báo cáo `gate17`: thêm đòi R sẵn ≥ 1,7 tới `E + 1,0 × chiều cao range`.
- Giới hạn: 1 lệnh mở (`kernel.simulate` one_at_a_time) · **1 lệnh / (range, cạnh, leg)** · chặn 19:20–20:30 VN bật · 15 nến đầu phiên · TIME khi hết phiên · phí 0,2 giá · chạm SL+TP cùng nến = SL. **Thêm:** mỗi F0 cũng mô phỏng **độc lập** (không one_at_a_time) để có `r_alone` — dùng cho kiểm hoán vị (mục 4) và mổ SL (mục 5).

## 3. DANH SÁCH COMBO (đăng ký trước — đúng 10, không thêm sau khi nhìn số)

| Combo | Tên | Điều kiện (trên F0, đã qua veto Vk) | Ý người học / CORVEN |
|---|---|---|---|
| **F0** | nền = C1 | không đòi gì | đối chứng |
| **F1** | nguyên thủy | **T** | "tín hiệu nguyên thủy nhất của follow" |
| **F2** | bóng CF | **Bc** | combo 1 (không trap, CF có bóng buy) |
| **F3** | kiệt sức hồi | **K** | combo 2 (không trap, kiệt sức sell) |
| **F4** | trap + bóng CF | **T ∧ Bc** | 0:46:13 "trap xong, buy phải vào, phải có bóng xanh" |
| **F5** | trap + kiệt sức | **T ∧ K** | ví dụ 3 CORVEN (trap + kiệt sức đáy) lật sang Follow |
| **F6** | stacked giữ | **S** | 0:05:41 / 0:18:13 |
| **F7** | Δ ngược hồi | **Dh** | ③a ngược giá |
| **F8** | hồi nông + lực CF | **Sh ∧ (Bc ∨ Dc)** | "giảm nhẹ về … phe mua lao vào" |
| **F9** | move mạnh + 1 dấu hiệu | **Mv ∧ (T ∨ Bc ∨ K ∨ S)** | "để ý momentum" |
| **F10** | ≥ 2 dấu hiệu khác loại | ≥ 2 trong {T, Bc, K, S, Dh} | = luật ③ cũ áp lên cấu trúc Follow — để biết lỗi trước đây nằm ở **cấu trúc** hay ở **cách đếm** |

Combo nào có **n < 30 trên TRAIN** ⇒ ghi "không đo được", **không** được kết luận tốt/xấu, giữ ở trạng thái "đọc chart, không code signal"
(bảng cuối `EVIDENCE-DRILLS.md`). Dự đoán thẳng trước khi chạy: trap chỉ có ở 2,9 % CF theo định nghĩa cũ ⇒ **F1/F4/F5 rất có thể n < 30**;
nếu vậy thì "tín hiệu nguyên thủy" của người học **chưa đo được** chứ không phải sai — nói rõ với người học, không nặn số.

## 4. GIAO THỨC ĐO — chống khớp quá tay khi có 10 combo

1. **Dữ liệu:** chỉ `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (+ `_bars`). TRAIN = phiên dày ≤ 2026-09-15 (35 phiên), bỏ 4 phiên thưa đầu và
   phiên `thin` (cùng bộ lọc `setup_corven.load_train`). **TEST ≥ 2026-09-16 (26 phiên) KHOÁ**; script phải cắt TEST ngay khi nạp, không có cờ mở.
2. **Một cấu hình chính duy nhất để chọn combo:** S2 · TP 2R không cổng · `cf_within` 3 · CF lỏng. Các biến thể (S1, `gate17`, `cf_strict`,
   `cf_within` 4, `cf_4a`) **chỉ báo cáo**, không tham gia chọn ⇒ số phép thử có sức chọn = **10** (F1…F10), không phải 40.
3. **Đối chứng cho TỪNG combo** (cùng SL/TP/phí/neo): **C1** = F0 (mọi F0, không đòi dấu hiệu) — báo cả R TB toàn F0 và R TB của **phần F0 không
   thuộc combo** (để thấy combo tách được gì); **C2** = `controls_corven.c2` (20 nến ngẫu nhiên cùng phiên, ±30′, cùng hướng, cùng rủi ro mbr) cho
   các lệnh của combo đó.
4. **Hiệu chỉnh nhiều phép thử — kiểm hoán vị thống kê cực đại:** 2.000 lần: trong **từng phiên**, hoán vị ngẫu nhiên **bộ cờ dấu hiệu nguyên
   dòng** giữa các F0 của phiên đó (giữ tương quan giữa các cờ, giữ cấu trúc thời gian), tính lại `R TB(combo) − R TB(F0)` cho cả 10 combo bằng
   `r_alone`, lấy **max** ⇒ phân bố null của "combo tốt nhất do may". Ngưỡng = **phân vị 95**. Combo thật phải vượt ngưỡng này. Báo luôn
   p-value từng combo (có và không hiệu chỉnh).
5. **Tiêu chí lọt vòng trong (được mổ SL):** n ≥ 30 **và** R TB ≥ C1 **và** ≥ C2 (của chính combo).
6. **Tiêu chí ĐẠT (được mở TEST) — chốt trước, không hạ:** n ≥ 30 · R TB ≥ C1 + **0,15** · ≥ C2 + **0,15** · cận dưới KTC 95 % (bootstrap) > **−0,10**
   · R TB **> 0 ở cả hai nửa TRAIN** (18 phiên đầu / 17 phiên sau, chia theo phiên) · **vượt ngưỡng hoán vị** mục 4.4.
7. **Mở TEST:** chỉ khi ≥ 1 combo ĐẠT; mở **một lần cho tất cả combo ĐẠT (≤ 3)** cùng lúc, đúng cấu hình chính, không sửa gì sau. Tiêu chí trên
   TEST = T1 plan chính 3.6 (R TB > 0, n cộng dồn ≥ 60, không đổi dấu theo thế/leg). Không ĐẠT ⇒ **không mở**, đăng ký lại cho dữ liệu mới.
8. **Xung đột với giả thuyết C (mục 9 plan chính):** mục 9 đăng ký C trên **dữ liệu từ 22/10/2026 trở đi**, không phải trên TEST; câu "giữ TEST
   cho C" ở 10.6 chỉ là dự phòng. **Quyết:** C giữ nguyên như mục 9 (dữ liệu mới); TEST 26 phiên được dành cho Follow, mở một lần theo 4.7.
   Sau khi mở, TEST coi như đã dùng — mọi giả thuyết về sau (kể cả C nếu đổi ý) đều phải sang dữ liệu mới. Ghi vào plan chính mục 11.
9. **Dữ liệu mới** (người học xuất GCZ26/GCG27 M1 từ 22/10 → nay, rồi hằng tuần): là **vòng xác nhận cuối** cho combo đã qua TEST, và là nơi
   duy nhất xác nhận các sửa đổi sinh ra từ mổ SL (mục 5). Ca ảnh gốc (đầu 11/2026) nằm trong đợt này ⇒ khi có file, **kiểm trước tiên** máy có
   bắt đúng ca đó không; không bắt được = định nghĩa 2a–2c sai, sửa định nghĩa (không tính là tinh chỉnh) rồi mới đọc số.

## 5. QUY TRÌNH "MỔ LỆNH SL" (có giới hạn — đây là động cơ khớp quá tay nếu thả lỏng)

Áp cho **combo lọt vòng trong** (4.5). Mỗi vòng:
1. `plot_follow.py` xuất ảnh **mọi** lệnh SL của combo (gọi `plot_corven.plot_trade` với trước 40 / sau 30 nến; vẽ thêm hộp range, nến x, nến hồi,
   CF, ô trap/bóng) → `report/follow_shots/<combo>/SL_<idx>.png`, và 5 lệnh TP để đối chiếu.
2. **Phân loại máy móc, danh mục cố định, ưu tiên từ trên xuống, mỗi lệnh đúng 1 nhãn** (`mo_sl_follow.py`):

| Nhãn | Định nghĩa |
|---|---|
| `MOVE_GIA` | trong ≤ 5 nến sau c có nến đóng trong range (`ReEntry`/đóng < E) — cú phá là giả |
| `SL_QUET` | SL bị chạm bởi râu ≤ 2 tick quá SL, rồi giá chạm TP gốc trong 30 nến — SL quá sát |
| `HOI_SAU` | `deep` (depth > 0,7 move_h) |
| `CF_YEU` | c không thoả 4a (thân < 0,4 hoặc đóng–đỉnh > 0,3 biên độ) |
| `NGUOC_1H` | `close[c] − close[c−60]` ngược dấu D (đẩy ngược xu hướng 1 giờ) |
| `PHIEN_MONG` | phiên Á hoặc volume nến c < p25 volume các nến của phiên đó |
| `TIN` | trong ±15′ sự kiện lịch tin USD — **chỉ nếu** Python có lịch (`kernel`/`NewsCalendar` port); không có thì bỏ hạng mục, ghi rõ |
| `KHONG_RO` | còn lại |

3. Bảng: với mỗi nhãn, **% trong lệnh SL** và **% trong lệnh TP** của cùng combo. Một nhãn chỉ được coi là "nguyên nhân" nếu ≥ **40 %** lệnh SL
   **và** ≤ **20 %** lệnh TP mang nhãn đó (nếu TP cũng mang nhãn thì đó là đặc điểm chung của setup, không phải nguyên nhân thua).
4. Fable xem mắt ≤ 10 ảnh SL + 5 ảnh TP mỗi combo, đối chiếu nhãn máy; ghi nhận xét vào `report/MO-SL-FOLLOW.md`.
5. **Sửa:** mỗi vòng **tối đa 1 luật / combo**, phải là luật suy ra trực tiếp từ nhãn đạt 5.3 (vd `MOVE_GIA` ⇒ đòi CF ≥ x+2 và nến hồi không chạm E;
   `SL_QUET` ⇒ thử S2 với đệm 5 tick; `HOI_SAU` ⇒ đòi `Sh`). Combo đã sửa đổi tên thành `F<n>b`, gắn nhãn **hậu kiểm**, chạy lại 4.3–4.6; **không
   được mở TEST cho `F<n>b`** — chỉ dữ liệu mới (4.9) mới xác nhận được nó.
6. **Giới hạn: tối đa 2 vòng mổ SL trên TRAIN.** Hết 2 vòng mà không combo nào ĐẠT ⇒ dừng, báo người học; không nới tiêu chí.

## 6. ĐẦU RA

- `report/RESULTS-FOLLOW.md`: (i) tần suất: move/ngày, F0/ngày, % F0 bị Vk loại, % có từng cờ T/Bc/K/S/Dh/Dc/Sh/Mv; (ii) bảng 11 dòng F0…F10 cấu
  hình chính: n · lệnh/ngày · WR · R TB + KTC · ΣR · max DD · chuỗi thua · C1 (toàn F0 và F0∖combo) · C2 · R nửa 1 / nửa 2 · p hoán vị (thô / cực đại)
  · **ĐẠT?**; (iii) cùng bảng cho các biến thể báo cáo (S1, gate17, cf_strict, cf_within 4, cf_4a) — ghi rõ "không có sức chọn"; (iv) theo leg 1/2,
  theo phiên Á/Âu/Mỹ, theo giờ VN, theo tháng, theo `b_from_exhausted`; (v) 5 thắng + 5 thua mỗi combo lọt vòng trong kèm giờ UTC; (vi) phễu:
  CloseOutside → move hợp lệ → có nhịp hồi → có CF ≤ x+3 → qua Vk → qua trần SL → qua giờ → lệnh.
- `report/_follow_cands.csv` (1 dòng / F0: idx_ref, idx_x, idx_c, leg, D, E, range_id, move_h, depth, cờ T/Bc/K/S/Dh/Dc/Sh/Mv/Vk + số đo, entry/sl_S1/sl_S2/tp, `r_alone`,
  outcome_alone, phien) · `report/_follow_trades_<combo>.csv` (lệnh thật, one_at_a_time, header như `_corven_trades.csv` + `combo,leg,co`) ·
  `report/_follow_perm.csv` (2.000 giá trị max) · `report/follow_shots/` · `report/MO-SL-FOLLOW.md`.
- Bảng theo dõi "luật đã kiểm / chưa kiểm" cuối `tpo/EVIDENCE-DRILLS.md`: thêm 10 dòng F1…F10, trạng thái cập nhật sau mỗi giai đoạn.

## 7. FILE VÀ THỨ TỰ VIỆC CHO OPUS (mỗi giai đoạn dừng, Fable review)

**File mới trong `benzo-trader/research/` (không sửa file cũ):**
- `follow_combo.py` — nạp dữ liệu qua `setup_corven.load_train` (chỉ import, không sửa) hoặc `kernel.load_bars` + bộ lọc tương đương; `RangeEngine`
  từ `quantower-range/research/range_proto.py` (sys.path như `setup_corven`); dấu hiệu từ `of_signals.py` (`bubbles`, `exhaustion`, `is_swept`,
  `stacked_zones`, `CellBaseline`); mô phỏng `kernel.simulate`; C2 từ `controls_corven.c2` (nếu cần đổi dạng `R` thì viết hàm bọc trong file này,
  không sửa `controls_corven.py`). Chứa: máy trạng thái 2a–2c, cờ 2d, lệnh 2e, bảng combo mục 3, kiểm hoán vị 4.4, xuất mục 6.
- `test_follow_combo.py` — ca tổng hợp: (1) **ca ảnh gốc** dựng lại theo số đọc ở mục 0 (range tới 4131; nến đóng ngoài; nến hồi đỏ 1 nến có ô Bid
  lớn ở nửa trên; CF +26 có ô Ask lớn nửa dưới, đóng 4132,2) ⇒ F0 ✓, T ✓, Bc ✓, F1/F2/F4 bắn; SL S2 ≈ dưới E; TP 2R; (2) nến hồi đóng trong range ⇒
  FailBreak ⇒ không F0; (3) CF ở x+4 ⇒ hết hạn; (4) CF Δ < 0 hoặc đóng không cao hơn nhịp hồi ⇒ không CF; (5) kiệt sức đỉnh chưa quét ⇒ Vk loại; đã
  quét ⇒ không loại; (6) leg 2 chỉ khi lập cực trị mới, tối đa 2; (7) T đòi `close[c] >` giá ô; ô ở nửa dưới nến hồi ⇒ không T; (8) 1 lệnh/(range,
  cạnh, leg); (9) lật dấu D = −1 cho toàn bộ ca 1; (10) hoán vị: dữ liệu giả có cờ độc lập với R ⇒ p ≈ đều, không combo nào "ĐẠT".
- `plot_follow.py`, `mo_sl_follow.py` — mục 5.

**Giai đoạn:**
- **GĐ-F0 — định nghĩa + đếm (chưa mô phỏng R):** `follow_combo.py` chạy tới F0 + cờ trên TRAIN; báo tần suất mục 6(i) + phễu 6(vi); test (1)–(9)
  xanh. Kỳ vọng sơ bộ (không ép): 2–6 F0/ngày; cờ T hiếm (< 10 % F0). Nếu F0 > 10/ngày ⇒ 2a quá lỏng, **báo lại trước khi** đổi (sửa định nghĩa
  phải ghi hậu kiểm nếu đã nhìn R — ở GĐ-F0 chưa nhìn R nên được sửa). *Dừng.*
- **GĐ-F1 — đo 10 combo:** toàn bộ mục 4 trên TRAIN, `RESULTS-FOLLOW.md` đủ mục 6, test (10). **Không chạm TEST.** *Dừng — Fable đọc bảng + 5 thắng/5 thua.*
- **GĐ-F2 — mổ SL** cho combo lọt vòng trong, ≤ 2 vòng theo mục 5. *Dừng sau mỗi vòng.*
- **GĐ-F3 — mở TEST** một lần nếu có combo ĐẠT (4.7); kết luận; commit "mở TEST Follow". Không ĐẠT ⇒ viết `report/KET-LUAN-FOLLOW.md` cho người học
  (đã thử gì, số, vì sao dừng, combo nào chưa đo được vì n nhỏ) và đăng ký lại cho dữ liệu mới.
- **Port C#** (`corven-2`, thêm detector Follow cạnh Thế A/B hoặc thay) **chỉ khi** qua TEST với T1; đạt T0 (không kém C1/C2) mà chưa qua TEST
  ⇒ **không port**, khác với quyết định A của Thế A/B — vì người học đã có một tín hiệu "chưa có lợi thế" trên chart rồi, thêm cái thứ hai cùng
  nhãn chỉ làm nhiễu.

Mỗi lượt có sửa file: `git add` đúng file của mình → commit tiếng Việt → `git push origin main` → báo hash (CLAUDE.md quy tắc 4).

## 8. Ý KIẾN THẲNG CỦA FABLE

**Hợp lý ở đâu.** (i) Thế B hiện tại chờ `BreakConfirmed` (3 nến) rồi chờ giá hồi về cạnh — ca ảnh của người học vào ở nến thứ 2 sau nến đóng
ngoài, Thế B **không thể** bắt. Kết quả −0,29R vừa rồi đo trên 97 lệnh của một cấu trúc **khác** cấu trúc này, nên không suy ra Follow cũng âm.
(ii) "Combo có tên, đo riêng" là thiết kế thí nghiệm sạch hơn "≥ 2 dấu hiệu bất kỳ": F10 chính là luật cũ áp lên cấu trúc mới — nếu F10 âm mà
F2/F4 dương thì lỗi cũ nằm ở cách đếm; nếu tất cả âm thì lỗi nằm ở chỗ khác (dữ liệu, hoặc cái CORVEN nhìn chưa dịch được). (iii) Hai câu
0:46:13 / 0:48:07 của CORVEN ủng hộ đúng combo 1 của người học, nên đây không phải ý tự nghĩ ra.

**Rủi ro — nói trước để không bất ngờ.**
1. **Nền F0 nhiều khả năng âm.** MEASURE.md: ~2 fail break mỗi range, vào máy móc ở cú phá = −0,2R; C1 của Thế B là −0,24. Follow vào **sớm hơn** Thế B
   (chưa đợi K nến) nên ăn thêm phần phá giả. Combo phải nâng ≥ 0,3R so với nền mới dương — đòi hỏi lớn với dấu hiệu đo trên dữ liệu không có
   lệnh đơn / không có delta trong nến.
2. **10 combo trên 35 phiên:** không hiệu chỉnh thì gần như chắc có 1–2 combo "đẹp" do may (vòng 2 vừa rồi C2 đã dao động ±0,1R giữa các ô). Kiểm
   hoán vị cực đại (4.4) là lưới bắt cái này; combo nào chỉ qua p thô mà không qua p cực đại thì **không** được gọi là có lợi thế.
3. **n nhỏ ở đúng combo người học thích nhất:** trap hiếm ⇒ F1/F4/F5 có thể < 30 lệnh ⇒ "chưa đo được". Phải chấp nhận câu trả lời đó thay vì nới
   định nghĩa trap cho đủ số.
4. **Mổ SL là nơi dễ tự lừa nhất:** nhìn 20 ảnh thua luôn thấy "lý do". Vì vậy mới có 5.3 (nhãn phải vắng ở lệnh TP), giới hạn 1 luật/combo/vòng,
   2 vòng, và sửa đổi **không được mở TEST**, chỉ dữ liệu mới xác nhận.
5. **Ca neo không có trong dữ liệu** (sau 21/10). Người học cần xuất GCZ26 M1 22/10 → nay càng sớm càng tốt — vừa để kiểm máy có bắt đúng ca ảnh,
   vừa là tập xác nhận cuối.

**Dự đoán đăng ký trước (để sau này tự chấm):** F0 âm (−0,1…−0,3R); 1–2 combo trong {F2, F4, F8, F9} dương trên TRAIN nhưng **không** qua ngưỡng
hoán vị cực đại; F1/F5 n < 30. Xác suất có ≥ 1 combo ĐẠT và mở được TEST: khoảng **30 %**. Nếu đúng vậy thì kết luận trung thực là: Follow kiểu
này **đọc chart được, chưa code thành signal được** với dữ liệu hiện có — và việc tiếp theo là dữ liệu mới + sửa Footprint Export ghi delta trong
nến, không phải thêm combo.

## 9. QUYẾT ĐỊNH SAU F1 (Fable, 2026-11-09, đọc `report/RESULTS-FOLLOW.md` commit 9396f30 — kết quả: 0/10 combo ĐẠT, 0 lọt vòng trong)

> Kết luận GĐ-F1 của Opus **đúng theo chữ plan**. Nhưng câu hỏi 3 của Opus chỉ ra một lỗi **trong đối chứng do tôi thiết kế** (C2), và lỗi đó
> ảnh hưởng tới cả tiêu chí "lọt vòng trong" lẫn nhãn đang in trên Benzo corven-1. Vì vậy thứ tự việc tiếp theo là: **sửa C2 trước → chấm lại
> vòng trong → mổ SL**. Mọi điều dưới đây là **hậu kiểm** (viết sau khi đã nhìn R trên TRAIN) và chỉ được xác nhận bằng dữ liệu mới ≥ 22/10.

### 9.1 Trả lời 5 câu hỏi

1. **F0 = 22/ngày — KHÔNG siết 2a lúc này.** Ước lượng 2–6/ngày của tôi sai vì tôi không đếm rằng `RangeEngine` sinh ~25 range/ngày ⇒ 97 cú đóng
   ngoài/ngày; đây là đặc tính của bộ range, không phải Follow lỏng. Sau cổng chỉ còn 9,7 lệnh/ngày. Siết bây giờ = sửa định nghĩa sau khi nhìn R.
   Ghi nhận cho vòng dữ liệu mới một **biến thể báo cáo** `move_mbr 1,5` (không có sức chọn). Không đổi gì ở cấu hình chính.
2. **Ngưỡng hoán vị — CHỐT: max chỉ lấy trên combo có ≥ 30 F0 trong lần hoán vị đó** (= 0,31R lượt này). Lý do: combo n < 30 không được chấm theo mục 3,
   nên không được phép làm phồng phân bố null của các combo được chấm. Đây là sửa giao thức hậu kiểm nhưng **không đổi kết luận lượt này** (F7 Δ 0,20 < 0,31).
   Báo cả hai ngưỡng trong mọi bảng về sau, ngưỡng ≥ 30 là ngưỡng chấm.
3. **C2 có thiên lệch dương — ĐÚNG, và đó là lỗi thiết kế của tôi.** Cơ chế: với nến ngẫu nhiên j **trước** nến CF, hướng vào S được lấy từ cú phá
   xảy ra **sau** j ⇒ lệnh giả "biết trước" hướng của chính cú đẩy đã định nghĩa setup, nên ăn trọn cú đẩy đó. Setup Follow nằm cách cú phá chỉ 2–5
   nến, cửa sổ −30′ chứa gần như toàn bộ cú đẩy ⇒ C2 +0,28 trong khi F0 −0,05 là hệ quả trực tiếp. Thế A/B của CORVEN dùng cùng `controls_corven.c2`
   nên **cũng dính**, mức độ nhỏ hơn (CF cách cú phá xa hơn) nhưng chưa đo nên chưa biết.
   **Sửa (đăng ký trước, không nhìn số rồi chọn):** `C2'` = pool chỉ gồm nến j **sau** nến CF, cùng phiên, `0 < sm[j] − sm[i] ≤ 30′`, các điều kiện khác
   giữ nguyên (cùng hướng, cùng rủi ro theo mbr, TP 2R, 20 nến, bỏ lệnh nếu pool < 5 nến). Ý nghĩa mới của C2': *"vào đúng nến CF có hơn vào bừa một
   nến bất kỳ trong 30 phút sau đó không"* = đo giá trị của **thời điểm** vào, không còn nhìn trước. Cài bằng tham số `after_only=False` thêm vào
   `controls_corven.c2` (mặc định giữ nguyên hành vi cũ ⇒ không ảnh hưởng parity/kết quả đã in), **không** sửa `setup_corven.py`.
   **Đính chính nhãn — quyết ngay, có điều kiện, không đợi số:** nhãn "kém vào ngẫu nhiên (−0,08R)" trên Benzo corven-1 dựa trên C2 lệch ⇒ phải đo lại
   C2' cho **bộ gốc vòng 1** (ô đang in −0,29R, C1 −0,24, C2 −0,08) trên TRAIN. (a) Nếu −0,29 < C2' − 0,05: nhãn **giữ**, chỉ thay số trong ngoặc và thêm
   ghi chú đính chính vào `RESULTS-CORVEN.md`/`RESULTS-CORVEN-GD1.md`/README. (b) Nếu −0,29 ≥ C2' − 0,05: nhãn đổi thành **"−0,29R/lệnh, chưa có lợi thế
   (kém C1 −0,24R)"** ở cả 4 chỗ (`BenzoCorven.cs` `BacktestLine`/`SettingLabel`, `BenzoTrader.cs`, README, test `Program.cs`), build + test + deploy.
   Kết luận "chưa có lợi thế" của CORVEN **không đổi** trong cả hai nhánh: −0,29R có KTC dưới 0 và thua C1 (C1 không dính lỗi này). Dự đoán đăng ký
   trước của tôi: C2' của F0 Follow rơi về −0,10…+0,05; C2' của CORVEN bộ gốc rơi về −0,25…−0,10 ⇒ nhiều khả năng nhánh (b).
4. **S2 vượt trần 4 mbr ở leg 2 — là đặc tính, giữ S2 làm neo chính.** Nhưng "mốc quan trọng gần nhất" của CORVEN với leg 2 hợp lý hơn là **cực trị
   leg 1** chứ không phải cạnh E. Đăng ký **biến thể báo cáo S3**: leg 1 = S2; leg 2 = `min(high[x_leg1], min low[nhịp hồi ∪ c]) − đệm`. Chỉ báo cáo,
   không có sức chọn; chạy cùng lượt C2'.
5. **Hạng `TIN` — BỎ trên TRAIN.** `NewsCalendar` (ProfileEngine.cs) chỉ tải lịch tuần hiện tại, không có lịch sử 07–09/2026 ⇒ không port được gì
   có ích. Ghi rõ "TIN không đo được" trong `MO-SL-FOLLOW.md`; danh mục còn 7 nhãn. Lịch tin cho dữ liệu mới: indicator live đã lưu `news_cache.json`
   hằng tuần — gom lại sau, không chặn việc này.

### 9.2 Có mổ SL không — CÓ, ở chế độ "khám phá, hậu kiểm", trên F7 và F10 (F1 chỉ xem để học)

**Căn cứ:** F7 (Dh, n 96, +0,20, dương cả hai nửa, dương ở cả 5 biến thể báo cáo) và F10 (n 120, +0,12) đều **≥ C1** và n ≥ 30; thứ duy nhất chặn
chúng khỏi vòng trong là C2 — mà C2 đang lệch. Nếu C2' xác nhận F7/F10 ≥ C2' thì GĐ-F2 chạy **đúng theo plan** (mục 5), không cần ngoại lệ. Nếu
C2' vẫn cao hơn, vẫn mổ nhưng ghi nhãn "khám phá" và người học hiểu đây là **bài học đọc chart**, không phải bước tới signal.
**Không được nói "F7 có lợi thế"**: p cực đại 0,76, Δ 0,20 < ngưỡng 0,31. F7 là *triển vọng chưa chứng minh*.

Ràng buộc (ngoài mục 5, không hạ):
- Nhãn máy tính trên **toàn bộ** lệnh SL **và** TP của combo (để có % TP cho tiêu chí 5.3), ảnh xuất cho mọi SL + 5 TP.
- **Fable đọc ảnh và gắn nhãn tay TRƯỚC khi xem nhãn máy** (Opus để nhãn máy ở file CSV riêng, không in lên ảnh) — tránh tôi gật theo máy.
- Mỗi combo tối đa **1 luật** suy từ nhãn đạt 5.3 → `F7b`/`F10b`, đo lại trên TRAIN **chỉ để báo**, xác nhận duy nhất trên dữ liệu mới ≥ 22/10.
- F1 (n 11): xuất ảnh cả 11 lệnh (thắng lẫn thua) **chỉ để tôi và người học soi định nghĩa trap** — không rút luật, không đổi định nghĩa T từ 11 ca.
- Tổng cộng vẫn **≤ 2 vòng** mổ trên TRAIN (mục 5.6). Vòng này là vòng 1.

### 9.3 Việc giao Opus (một lượt, thứ tự A → B → C; dừng, Fable review)

**A. Sửa C2 + chạy lại bảng (TRAIN).**
1. `controls_corven.c2(..., after_only: bool = False)`: khi `True`, pool = `{j : s0 ≤ j < s1, 0 < sm[j] − sm[i] ≤ minutes, good[j], mbr[j] > 0}`;
   pool < 5 ⇒ bỏ lệnh đó. Mặc định `False` giữ nguyên. Thêm 2 test trong `test_setup_corven_gd1.py` hoặc file test mới: (i) `after_only=True` không bao
   giờ chọn j ≤ i; (ii) `after_only=False` cho kết quả **bit-giống** cũ trên một ca nhỏ.
2. `follow_combo.py`: cột **C2'** cạnh C2 cũ cho F0…F10 ở cấu hình chính; cột "lọt vòng trong (C2')" và "ĐẠT (C2')"; ngưỡng hoán vị báo cả hai,
   chấm bằng ngưỡng ≥ 30. Thêm biến thể báo cáo **S3** (9.1-4) và **move_mbr 1,5** (9.1-1). Không đổi cấu hình chính, không mở TEST.
3. `results_corven.py` (hoặc script nhỏ mới): C2' cho **bộ gốc vòng 1** CORVEN trên TRAIN (ô đang in −0,29R). Báo C2 cũ / C2' / R thật / C1 trong một bảng.
4. Áp 9.1-3 (a) hoặc (b) theo đúng số đo được — **ghi rõ nhánh nào và vì sao** vào `RESULTS-CORVEN.md` mục mới "Đính chính C2 2026-11-09". Nhánh (b)
   thì sửa 4 chỗ chuỗi, `./build.sh`, chạy test C#, deploy; dán kết quả build/test vào báo cáo.

**B. Mổ SL vòng 1 — F7, F10 (+ F1 để xem).**
1. `plot_follow.py`: với mỗi lệnh → `report/follow_shots/<combo>/SL_<idx_c>.png` / `TP_<idx_c>.png` (F7, F10: mọi SL + 5 TP rải đều theo thời gian;
   F1: cả 11 lệnh). Vẽ bằng `plot_corven.plot_trade` (trước 40 / sau 30 nến), thêm: hộp range + cạnh E, nến ref (đóng ngoài), nến x, nến hồi, nến CF,
   mức SL/TP, ô trap/bóng nếu cờ bật. Tiêu đề ảnh: combo · idx · UTC + giờ VN · side · leg · cờ · R. **Không in nhãn máy lên ảnh.**
2. `mo_sl_follow.py`: 7 nhãn (bỏ `TIN`), ưu tiên từ trên xuống, 1 nhãn/lệnh, tính cho **mọi** lệnh SL và TP của F7, F10, F0 ⇒ `report/_mo_sl_follow.csv`
   (combo, idx_c, outcome, r, nhãn, các số đo nền của nhãn) và bảng % SL / % TP theo nhãn trong `report/MO-SL-FOLLOW.md` mục "Nhãn máy"; nhãn nào đạt
   5.3 (≥ 40 % SL và ≤ 20 % TP) in đậm. F0 đưa vào để biết nhãn đó là đặc điểm chung của Follow hay riêng của combo.
3. `MO-SL-FOLLOW.md` để trống mục "Nhãn tay của Fable" và "Luật đề xuất" — Fable điền vòng sau.

**C. Cập nhật** `RESULTS-FOLLOW.md` (bảng chính thêm cột C2'), `tpo/EVIDENCE-DRILLS.md` bảng cuối (F1…F10 trạng thái: "đo TRAIN, chưa có lợi thế /
chưa đo được (n<30)"), commit tiếng Việt, push, báo hash. Chỉ `git add` file của mình (có tester khác đang làm trong `tools/TesterGd4/`, `tests/ui-out/`).

**Nhắc người học (không chặn Opus):** xuất **GCZ26 M1 từ 22/10 → nay** (Footprint Export, cùng định dạng `fp_*_90d`) — đó là nơi duy nhất mọi luật
rút từ mổ SL được xác nhận, và là nơi kiểm máy có bắt đúng ca ảnh gốc (mục 4.9).

## 10. QUYẾT ĐỊNH SAU 9.3 — mổ SL vòng 1 (Fable, 2026-11-09, đọc commit 798de45; chi tiết số ở `report/MO-SL-FOLLOW.md` mục 1, 3–6)

### 10.1 Kết luận vòng mổ 1
- Nhãn tay (toàn bộ 149 ảnh, gắn trước khi đọc nhãn từng lệnh của máy) khớp máy 77 % (F7) / 68 % (F10); **MOVE_GIA tay = máy 100 %** ⇒ con số 47 % là thật. Lệch chủ yếu ở CF_YEU (vế "đóng cách cực trị" mắt không thấy).
- Giả thuyết của agent chính "SL sát cạnh bị quét rồi giá đi đúng hướng": **bác**. Sau SL, giá tới mức TP không nhiều hơn nến ngẫu nhiên (F7 24 % vs nền 21 %; F10 11 % vs 17 %). Không nới đệm SL.
- Giả thuyết "vào xa cạnh / move từ phía đối diện": **không ủng hộ** ở dạng tổng quát (vào − E ≥ 2 mbr lại dương hơn); chỉ đuôi move ≥ 2× range âm, n nhỏ ⇒ ghi thành H3.
- Điều MOVE_GIA tập trung vào, biết được tại CF: **nhịp hồi chạm cạnh E** (Hc). F7: MOVE_GIA 39 % trong nhóm chạm vs 21 % không chạm; R TB −0,17 (33) vs +0,40 (62).
- Một phát hiện hậu kiểm ngược trực giác: **CF thân nhỏ thắng hơn** (F7 +0,64 (30) vs 0,00 (65); F10 +0,39 vs 0,00; F0 +0,10 vs −0,10). Đăng ký đo (H1), **không** làm luật.
- 25–32 % lệnh SL đã đi ≥ 1R rồi quay — chuyện quản lý lệnh, ghi nhận, chưa đụng.

### 10.2 Quyết định (đăng ký trước)
1. **F7b = Dh ∧ ¬Hc**, Hc (D = +1) = `min(low[x+1 … c−1]) ≤ E + tol`, tol = max(2 tick, 0,5 mbr) tại c. Nhãn **hậu kiểm**; TRAIN chỉ để báo; không mở TEST.
   **ĐẠT trên dữ liệu ≥ 22/10 khi và chỉ khi:** bộ tiêu chí bảng chính (n ≥ 30; ≥ C1 + 0,15; ≥ C2' + 0,15; KTC dưới > −0,10; dương cả hai nửa; vượt ngưỡng hoán vị ≥ 30) **và** `R TB(F7 ∧ ¬Hc) − R TB(F7 ∧ Hc) ≥ +0,20` trên dữ liệu mới. Dự đoán Fable: F7b rơi về 0,00…+0,30; xác suất ĐẠT < 1/3.
2. **F10: không rút luật** (không nhãn đạt 5.3). `F10 ∧ ¬Hc`, `F0 ∧ ¬Hc` chỉ là biến thể báo cáo.
3. **H1 / H2 / H3** (thân CF < 0,4 · rủi ro S2 ≥ 7 giá · move_h ≥ 2× range): cột báo cáo, đo trên dữ liệu mới, không cộng vào F7b, không có sức chọn.
4. **Không mổ F3. Không chạy lại lưới GĐ2 CORVEN bằng C2'. Không mở vòng mổ 2 trên TRAIN.** Vòng tiếp theo chỉ có trên dữ liệu mới.

### 10.3 Việc giao Opus (một lượt; dừng, Fable review; chỉ `git add` file của mình; không sửa mục 1, 3–6 `MO-SL-FOLLOW.md`)
1. **Cờ Hc + F7b trong `follow_combo.py`.** Thêm cột `Hc` (0/1) và `hc_ext_mbr = (E − min low[x+1…c−1])·D / mbr` vào `_follow_cands.csv`. Combo hậu kiểm **F7b = Dh ∧ ¬Hc**; biến thể báo cáo `F10 ∧ ¬Hc`, `F0 ∧ ¬Hc`. Chạy **đúng pipeline** (one_at_a_time, 1 lệnh/(range, cạnh, leg), C1 toàn F0, C1 F0∖combo, C2', nửa 1/2, p thô, p cực đại ≥ 30 — family hoán vị thêm F7b thành 11, ghi rõ F7b hậu kiểm). Kết quả vào `RESULTS-FOLLOW.md` mục mới **"10. Hậu kiểm vòng mổ 1 — F7b"** đúng cột bảng chính; đối chiếu với số lọc hậu kiểm của Fable (F7 ∧ ¬Hc n 62, +0,40) và ghi chênh. Không đổi cấu hình chính, không mở TEST. Test mới: (i) Hc đúng trên ca tổng hợp 3 nến (chạm trong tol / ngoài tol / đúng cạnh); (ii) mọi idx_c của F7b ⊆ F7; (iii) bảng chính F0…F10 **bit-giống** cũ.
2. **Ba cột giả thuyết** vào `_follow_cands.csv`: `cf_body = |close−open|/(high−low)` tại c, `risk_gia = risk_S2/10`, `move_x_rng = move_h/(top−bottom)`. Bảng "R TB hai phía" cho H1 (cf_body < 0,4), H2 (risk_gia ≥ 7), H3 (move_x_rng ≥ 2) trên F0, F7, F7b, F10 — TRAIN để đối chiếu mục 4.2 `MO-SL-FOLLOW.md`, sau này chạy y hệt trên dữ liệu mới.
3. **`follow_newdata.py` (file mới, cấu hình đóng băng).** Đầu vào duy nhất: đường dẫn file `fp_*.csv` + `_bars.csv` mới (≥ 22/10). Đầu ra: bảng chính F0…F10 + F7b (C1, C2', nửa, hoán vị ≥ 30); bảng H1–H3; kiểm F7b theo 10.2-1 và in **ĐẠT / KHÔNG** kèm từng điều kiện; đối chiếu ca ảnh gốc (4.9). Parity: chạy script trên 2 tuần cuối TRAIN phải ra số giống `follow_combo.py` trên cùng đoạn — viết thành test. Không tham số dòng lệnh nào khác ngoài đường dẫn.
4. **`tpo/EVIDENCE-DRILLS.md`** bảng cuối: thêm F7b "luật hậu kiểm từ mổ SL vòng 1 — chưa kiểm, chỉ dữ liệu ≥ 22/10"; H1–H3 "giả thuyết hậu kiểm, chỉ đo".
5. Commit tiếng Việt, push, báo hash. Nếu số pipeline của F7b lệch số lọc của Fable > 0,10R hoặc n lệch > 10, ghi riêng mục "7. Đối chiếu số Opus" trong `MO-SL-FOLLOW.md` và nêu vì sao.
