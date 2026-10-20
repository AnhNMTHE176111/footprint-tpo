# REVIEW-1 — Trạm Đêm Vàng, vòng 1 (kỹ thuật + nghiệp vụ)

Ngày 2026-10-20 · Người review: Claude Opus · Đối chiếu: `plans/CHECKLIST-DEM-VANG-plan.md` bản 4 (gọi tắt **plan**), `daily-trading/HE-THONG-DEM-VANG.html` (gọi tắt **HT**), mã nguồn `tram-dem-vang/` ở commit `f5a8573`.

**Số chạy lại thật trên máy này:** `npm test` 165/165 xanh · `npm run e2e` 11/11 xanh (8,7 s) · `npm run lint:vi` 0 lỗi. Đi tay tầng 0→5 từ dữ liệu trống bằng Playwright, ở 1366×768 và 360×740; ảnh nằm ở `docs/review-shots/` (`d1366-*.png`, `p360-*.png`). Console không lỗi ở cả hai cỡ màn hình; `file://` chạy tốt.

Các kiểm tra phụ (dò engine bằng `node`) nằm ở mục "Bằng chứng" của từng mục. Mức: **SAI LUẬT** (engine cho/chặn trái HT hoặc plan) · **CHẶN ĐƯỜNG ĐI** (người dùng kẹt) · **MÃ** · **UX** · **CHỮ** · **TEST**. Mục nặng xếp trước.

---

## A. Sai luật và chặn đường đi

### 1. [SAI LUẬT] Đổi về "Cân bằng" rồi chọn lại "Vừa phá" thì giữ nguyên bước 1, bước 2, hướng, cạnh và giờ phá cũ ⇒ cú phá mới "được công nhận" ngay, A bật ngay
- **Mô tả:** `setRegimeMode` chỉ đổi `mode`. Khi bấm lại "Vừa phá", `breakout` của cú phá trước (step1 = step2 = true) vẫn còn, nên `effectiveRegime` trả `broken` tức thì: A và D bật mà không qua công nhận 2 bước (HT 3.1, "thiếu bước 2 thì chưa phải phá"). Ngoài ra `breakoutFailed` không xóa `at`, `dir`, `edgeZoneId`. Lần phá sau sẽ dùng lại giờ phá cũ, nên `DIS_EARLY_BREAK` bắn sai: một cú phá cũ lúc 18:30 làm A bị tắt oan, còn một cú phá cũ sau 19:20 lại che mất một cú phá sớm mới.
- **Bằng chứng:** `js/journal.js:100-110` (`setRegimeMode`, `breakoutFailed`); `js/ui/tier012.js:210-215` (chỉ điền `at` khi đang trống). Chạy UI: bước 1 + bước 2 "Có" → bấm "Cân bằng" → bấm "Vừa phá" ⇒ "Chế độ hiệu lực: **vừa phá · xuống**" ngay (log Playwright `after balanced→broken eff: vừa phá · xuống`; ảnh `d1366-t2-broken-again.png`).
- **Sửa:** trong `setRegimeMode(night, mode, nowMs)`, khi `mode === 'broken'` và mode cũ khác `'broken'` thì gán `night.regime.breakout = { dir: null, edgeZoneId: null, at: hm(nowMs), nth: bo.nth || 1, step1: false, step2: false }`. Bỏ dòng tự điền `at` trong `tier012.js:214` vì đã chuyển vào đây. `breakoutFailed`: thêm `bo.dir = null; bo.edgeZoneId = null; bo.at = null;`. Thêm test đơn vị (vừa phá đủ 2 bước → cân bằng → vừa phá ⇒ `effective` = `balanced`, A `DIS_NOT_BROKEN`) và e2e đi đúng chuỗi bấm trên.

### 2. [CHẶN ĐƯỜNG ĐI] Trên điện thoại, mở ngăn "Thẻ phiên" xong thì không đóng lại được
- **Mô tả:** dưới 900 px, ngăn thẻ phiên (`z-index: 70`, rộng 88vw, phủ cả góc phải trên) đè lên đúng nút "Thẻ phiên" (`z-index: 50`). Không có nút đóng, không xử lý chạm ra ngoài. Người dùng chỉ còn cách tải lại trang.
- **Bằng chứng:** `css/app.css:234-236`; `js/main.js:255` (chỉ toggle). Playwright 360 px: phần tử ở tâm nút toggle là `ptitle` của thẻ; `page.click('#cardtoggle')` hết giờ; chạm ra ngoài vẫn `open = true`. Ảnh `p360-the-phien-mo.png`.
- **Sửa:** nâng `.cardtoggle` lên `z-index: 80`, đổi chữ thành "Đóng" khi thẻ đang mở. Thêm nút "✕" ở đầu `renderCard` khi màn ≤ 900 px. Thêm `#overlay` mờ phía sau ngăn để chạm ra ngoài là đóng. `Esc` cũng đóng. Thêm e2e mở rồi đóng ở 360 px.

### 3. [SAI LUẬT] Bias KHÔNG vẫn cho fade (C) ở High/Low hôm qua, IB, cạnh range — HT chỉ cho hai cạnh VA Âu
- **Mô tả:** HT 2.2 viết "KHÔNG bias: **Chỉ fade hai cạnh VA Âu**, mục tiêu 2R, cỡ lệnh một nửa"; plan 1c viết "chỉ C hai cạnh VA Âu". Engine không có luật nào giới hạn loại vùng của C khi bias KHÔNG. Chữ `DIS_BIAS_NONE` thì lại hứa "chỉ còn fade cạnh VA Âu".
- **Bằng chứng:** dò engine: bias KHÔNG, C buy tại `lowY` 4175 ⇒ `ENTRY`, `half [BIAS_NONE, SCENARIO_C]`. `js/rules.js:191-197` chỉ đòi `edge`/`edgeOuter`.
- **Sửa:** thêm luật `{ code: 'NO_BIAS_NONE_EDGE', scope: 'C', effect: 'NO', when: c => c.bias === 'KHÔNG' && !!c.zone && c.zone.type !== 'vahEu' && c.zone.type !== 'valEu' }`, đặt ngay sau `NO_COUNTER_BIAS_ZONE`. Trong `content.codes` thêm `{ text: 'Bias KHÔNG: chỉ fade hai cạnh VA Âu.', htRef: '2.2', ctl: 'c3' }` và thêm mã vào `zoneGroup` của chấm 2 (`engine.js:187`). Thêm test. Plan không đặt mã cho luật này; ghi vào docs/IMPL-2 để người viết plan bổ sung.

### 4. [SAI LUẬT] Đóng lệnh bằng "Về hòa" (hoặc "Chạm TP") ở giá lỗ thì không cộng vào chuỗi SL ⇒ né được ngắt mạch
- **Mô tả:** chuỗi SL chỉ đếm `exit.kind === 'SL'` hoặc đóng tay có R âm. Tầng 4 cho chọn "Về hòa" bất cứ lúc nào (kể cả chưa dời SL về hòa) và cho sửa giá thoát. Như vậy chỉ cần 2 SL rồi chọn "Về hòa" ở đúng giá SL là chuỗi về 0. Với người đang muốn gỡ, đây là cửa thoát của luật "3 SL liên tiếp ⇒ tắt máy" (HT 7).
- **Bằng chứng:** `js/engine.js:24`; `js/ui/tier45.js:84-87`. Dò engine: 2 SL, rồi lệnh thứ 3 đóng kind `BE` giá 4195,4 ⇒ `r = -1`, `slStreak = 0`, phán quyết `ENTRY`.
- **Sửa:** `engine.js:24` đổi thành `var isSL = t.exit.kind === 'SL' || (typeof t.r === 'number' && t.r < 0);`. Ở tầng 4, nút "Về hòa" chỉ bật khi `op.beDone`. Thêm test.

### 5. [SAI LUẬT] Cửa sổ 19:30 bật mặc định MỌI đêm; plan chỉ bật vào thứ Năm và khi `t0.touched = false` ⇒ chặn ca ĐÚNG 5/10 19:25
- **Mô tả:** plan 0.2 viết "19:30 ±15′ bật vào **thứ Năm** và khi `t0.touched = false`". Phụ lục A dựng mọi ca với "19:30 off". Người implement chọn bật mọi đêm (IMPL "chỗ tự chọn" #9). Có hai hệ quả. Thứ nhất, ca hấp thụ ĐÚNG ngày 5/10 (thứ Hai) lúc 19:25 (fixture A5, HT "Ca thật") bị `NO_NEWS_WINDOW` nếu người dùng để mặc định. Thứ hai, mỗi đêm không phải thứ Năm, người dùng phải tắt bằng hộp xác nhận và để lại vết "đã tắt lúc …", trông như một lần nắn luật. `isThursday` có viết nhưng không dùng ở đâu.
- **Bằng chứng:** `js/rules.js:42-47`; `js/journal.js:37`; `content.ui.t0WinNote` ("đều bật"); `grep isThursday` chỉ có trong `time.js` và test.
- **Sửa:** `newNight(key)` nhận `key`, gán `w1930.on = time.isThursday(key)`. Trong engine, coi `w1930` là bật khi `!t0.touched` (an toàn khi người dùng bỏ qua tầng 0) hoặc khi `t0.newsDay` (NFP/CPI ra lúc 19:30). Bật một cửa sổ đang tắt thì không cần xác nhận; tắt cửa sổ đang bật vẫn phải xác nhận và để vết như plan. Sửa `t0WinNote`. Thêm test: thứ Năm ⇒ bật; thứ Hai đã chạm tầng 0 ⇒ tắt; thứ Hai chưa chạm ⇒ bật; `newsDay` ⇒ bật. Nếu chủ hệ thống muốn giữ "bật mọi đêm" (HT 7 "đánh tin 19:30: 0") thì phải sửa plan và fixture A5 trước, không tự chọn trong code.

### 6. [SAI LUẬT] `NO_RR` và `NO_TP_PAST_ZONE` bị giấu khi đã có mã NO khác (chỗ tự chọn #3) ⇒ sổ thiếu mã, lỗi lộ ra dần
- **Mô tả:** phán quyết vẫn là KHÔNG VÀO nên không mở cửa cho lệnh cấm. Nhưng có hai hậu quả. (a) Bấm "Tôi vẫn vào" thì `ruleCodes` thiếu mã R:R/TP, nên dòng ⚠ trong sổ thiếu "luật SL" (HT 4 luật cứng, HT 8). (b) Người dùng sửa xong lỗi đầu mới thấy lỗi R:R. Gốc của chuyện này là **plan tự mâu thuẫn**. Fixture A2 có VAL Âu 4186 cách giá vào 4188 đúng 2 giá với rủi ro 2,3 giá, tức 0,87R, nên theo QĐ-16 và HT 6 ("vùng kế tiếp… dưới 1:2 thì bỏ") phải dính `NO_RR`. Fixture A3 có TP 4182,7, vượt VAL Âu 4188 tới 5,3 giá. Người implement đã nắn luật cho khớp fixture, và test `'R:R và TP chỉ xét khi các luật phía trước đã qua'` khóa luôn cách nắn đó.
- **Bằng chứng:** `js/rules.js:255-260`; `tests/verdict.test.js:332-335`; `tests/fixtures.test.js:44,58,63`. Dò: A với V + TP 4189 ⇒ `ruleCodes ['NO_V_PULLBACK']`, ⚠ "phạm 4.1" (thiếu luật SL).
- **Sửa:** bỏ điều kiện `c.reasons.length` ở hai luật. Thanh phán quyết vẫn chỉ hiện 2 mã đầu, nên màn hình A2 không đổi. Sửa kỳ vọng: A2 `reasons` = `['NO_BUBBLE_AGAINST','NO_V_PULLBACK','NO_RR','NO_TP_PAST_ZONE']`; A3a = `['NO_SL_FLOOR','NO_TP_PAST_ZONE']`; A3b = `['NO_SL_POS','NO_SL_FLOOR','NO_TP_PAST_ZONE']`. Test ở `verdict.test.js:332` đổi thành `reasons[0] === 'NO_V_PULLBACK' && reasons.includes('NO_RR')`. Ghi vào IMPL-2 để sửa Phụ lục A của plan; ⚠ của A2 sẽ thành "phạm 4.3, 4.1 và luật SL".

### 7. [SAI LUẬT] "Vùng kế tiếp" tính cả vùng trùng cạnh nằm sát giá vào ⇒ `NO_RR` giả cho đúng kèo B mà QĐ-1 cho phép
- **Mô tả:** QĐ-1 cho B tại vùng hạng 1–2 trùng cạnh (cách ≤ 1 giá). Nếu giá vào nằm giữa hai mép của cặp trùng đó, `nextZoneFor` lấy chính vùng cạnh làm "vùng kế tiếp", nên TP gợi ý chỉ cách giá vào 0,5 giá và R:R rơi xuống 0,2. Thêm một chuyện nữa: LVN cũng bị coi là vùng chặn TP, trong khi QĐ-2 nói LVN là chỗ "giá đi nhanh qua".
- **Bằng chứng:** `js/engine.js:42-50`. Dò: B buy tại VWAP tuần 4181 trùng VAL Âu 4182, vào 4181,5, SL 4179 ⇒ `NO [NO_RR]`, `nextZone z2`, `tpSuggested 4182`.
- **Sửa:** trong `nextZoneFor`, bỏ qua vùng mà `R.zoneGap(z, entryZone) <= T.nearGap + EPS` (cùng cụm với vùng vào). Bỏ qua vùng `type === 'lvn'`; đây là đề xuất, cần chủ plan xác nhận nên ghi vào IMPL-2. Thêm test cho ca trên.

### 8. [SAI LUẬT] `NO_MID_RANGE` bắn cả khi `pending`; plan chỉ áp khi `balanced`
- **Mô tả:** plan 3a C3 viết "`balanced` và vùng không đạt QĐ-1 ⇒ `NO_MID_RANGE`"; bảng bật kịch bản viết `pending`: "B bật (trừ cạnh vừa phá)". Code chặn cả B tại VWAP tuần khi `pending`. Như vậy là chặt hơn plan và chặn một kèo hạng 1 hợp lệ.
- **Bằng chứng:** `js/rules.js:193` (`e !== 'balanced' && e !== 'pending'`). Dò: B buy tại VWAP tuần, `pending` ⇒ `NO [NO_MID_RANGE]`.
- **Sửa:** đổi điều kiện thành `e !== 'balanced'`. Ở `NO_B_RANK` (dòng 205) vẫn để cạnh nâng hạng khi `pending`, đúng như bảng. Nếu chủ hệ thống muốn coi pending là "vẫn trong range" thì phải sửa plan trước.

### 9. [MÃ] Cửa sổ cấm tự thêm được lưu múi `ET` ⇒ từ 01/11 tự cộng 1 giờ vào giờ người dùng gõ
- **Mô tả:** người dùng gõ giờ VN đang thấy trên đồng hồ, nhưng cửa sổ lưu `tz: 'ET'` nên mùa đông bị dịch +1h. Mỹ đổi giờ ngày 01/11/2026, chỉ còn 12 ngày.
- **Bằng chứng:** `js/ui/tier012.js:55`. Dò: cửa sổ tự thêm "21:00" ngày 10/11/2026 ⇒ tâm 22:00.
- **Sửa:** cửa sổ tự thêm lưu `tz: 'VN'` (`markMin` đã hỗ trợ múi VN). Đổi placeholder thành "giờ VN". FOMC giữ `ET`. Thêm test.

### 10. [UX] ENTRY không hiện số hợp đồng; cỡ ½ với cài đặt mặc định ra **0 hợp đồng** mà vẫn ENTRY xanh
- **Mô tả:** cài đặt mặc định là 2.000 $ và 2 %. Mọi lệnh ½ có SL ≥ 2,1 giá đều ra 0 hợp đồng (A1, A4, mọi lệnh trước 20:30). Thanh ENTRY chỉ ghi "cỡ ½"; con số 0 nằm trong mục thu gọn "Cỡ lệnh MGC". Test A4a còn khẳng định `size 0` như chuyện bình thường.
- **Bằng chứng:** `js/ui/tier3.js:222` (ENTRY chỉ in `sizeHalfShort/sizeFull`); `tests/fixtures.test.js:84`.
- **Sửa:** thêm `· {n} hợp đồng` vào dòng ENTRY. Khi `size === 0`, hiện chip đỏ "Cỡ ½ chưa đủ 1 hợp đồng MGC — không vào hoặc tăng vốn" và tắt nút "Vào lệnh" (vẫn để "Ghi kèo luyện mắt"). Ghi vào IMPL-2 để plan chốt.

### 11. [UX] Bước Bấm không vừa một màn 1366×768 (plan §4.1); ô B5 và hộp tính nằm dưới thanh phán quyết
- **Bằng chứng:** trang ở bước Bấm cao 971 px so với màn 768 px. Trước khi cuộn, B5 bị thanh phán quyết che (ảnh `d1366-t3-bam-empty.png`, `d1366-t3-entry.png`).
- **Sửa:** sau khi đã chọn thì ẩn danh sách tiêu chí của B1/B3 (chỉ hiện khi chưa chọn hoặc mức "Mới"); `.ctl` giảm padding còn 8 px; B4 + B5 xếp chung một hàng khi rộng ≥ 1100 px; đưa chip SL/R:R lên thanh phán quyết thay cho hộp tính riêng; `.vbar` min-height 64 px. Thêm e2e đo `scrollHeight ≤ innerHeight` ở bước Bấm.

### 12. [UX] Điện thoại 360 px: thanh trạng thái dính trên (165 px) cộng thanh phán quyết (172 px) chiếm 45 % màn hình
- **Bằng chứng:** đo bằng Playwright: `vbarH 172,5` / `innerH 740`; chip trạng thái xuống 4 dòng (ảnh `p360-t3-canh.png`: ô C6 bị che một nửa).
- **Sửa:** ở ≤ 600 px chỉ giữ một dòng dính trên (giờ · BIAS · cửa sổ kế), các chip còn lại không dính. Thanh phán quyết: chấm + chữ một dòng, nút bên phải, `padding-bottom` của `#app` bằng đúng chiều cao thanh (đo bằng `ResizeObserver`, thay cho số cố định 150/230 px).

### 13. [MÃ] Mất dữ liệu im lặng: lưu lỗi không báo, hai tab ghi đè nhau
- **Mô tả:** `persist()` bỏ qua giá trị trả về của `S.save`. Khi bộ nhớ đầy, Safari ẩn danh hoặc rơi về `memStorage`, sổ mất lúc tải lại mà người dùng không biết. Không có listener `storage`: mở PWA và một tab trình duyệt cùng lúc (plan §1 "màn phụ") thì tab nào lưu sau sẽ xóa lệnh của tab kia.
- **Bằng chứng:** `js/main.js:7-9,33`; `js/store.js:221-223`.
- **Sửa:** `persist()` nhận `false` ⇒ hiện banner đỏ cố định "Không lưu được vào máy — tải JSON ngay" kèm nút tải. Thêm `window.addEventListener('storage', e => { if (e.key === S.KEY) { state = S.load(storage); app.state = state; render(); app.toast('Dữ liệu vừa đổi ở cửa sổ khác — đã tải lại.'); } })`.

### 14. [MÃ] Mã vùng bị dùng lại sau khi xóa ⇒ "lần tại vùng" lẫn sang vùng khác, hoặc xóa rồi thêm lại để reset đếm
- **Bằng chứng:** `js/journal.js:67-71` (`max + 1`). Dò: có z1–z3, xóa z3, mã mới lại là `z3`. Lệnh cũ ở z3 cũ sẽ tính cho vùng mới; ngược lại, xóa vùng rồi thêm lại cùng giá với mã mới thì `NO_ZONE_3RD` mất tác dụng (HT 7 "vào lại cùng vùng: tối đa 2").
- **Sửa:** thêm `card.zoneSeq` (tăng đơn điệu, lưu trong thẻ, migrate = max hiện có). Nếu đã có lệnh ở vùng thì không cho xóa vùng đó (chỉ cho sửa ghi chú), hoặc khi đếm `zoneN` thì đếm theo `(zoneType, giá)` của dòng sổ.

---

## B. Chữ, hướng dẫn, màu

### 15. [UX] Hướng sell và BIAS SELL tô **đỏ**, cùng màu với "KHÔNG VÀO" và đáp án xấu
- **Mô tả:** plan §4.2 quy định màu cố định (đỏ = KHÔNG VÀO), §4.5 quy định "đáp án xấu tô đỏ". Chip BIAS SELL, chữ "SELL" to ở 1c, chip hướng ở C2, chip lệnh ở tầng 4 đều đỏ, nên đọc nhanh dễ hiểu thành "sai".
- **Bằng chứng:** `js/ui/status.js:37`, `tier012.js:118`, `tier3.js:142`, `tier45.js:37`, `status.js:63`.
- **Sửa:** thêm token `--buy` (xanh dương #4aa3ff) và `--sell` (cam #ff9f43) cho cả hai giao diện; lớp `.dir-buy` / `.dir-sell` thay cho `good` / `bad` ở 5 chỗ trên.

### 16. [CHỮ] Nhãn C6 "Nến M1 cao nhất trong 5 nến" dễ hiểu thành **giá cao nhất**
- **Mô tả:** plan C6 viết "**Biên độ** nến M1 cao nhất". Người dùng mới dễ gõ 4195 (giá đỉnh); khi đó `NO_SL_FLOOR` báo "SL 2,4 nhỏ hơn nến 4195,0".
- **Sửa:** `controls.c6.label` = "Biên độ nến M1 lớn nhất (5 nến)"; `c6Again` = "Biên độ nến M1 lớn nhất (sửa tại đây)"; `WAIT_C6.text` = "Biên độ nến M1 lớn nhất". Trong engine, `c6 > 20` thì ra CHỜ với mã mới `WAIT_C6_BIG` "Biên độ hơn 20 giá — gõ biên độ, không gõ giá".

### 17. [CHỮ] Không hiện "quyết định của công cụ, chưa đo" cho QĐ-n
- **Mô tả:** plan §0 bắt buộc QĐ hiện trong trợ giúp "?" kèm câu "quyết định của công cụ, chưa đo". `content.qd` và `content.unmeasured` có chữ nhưng không file UI nào dùng.
- **Sửa:** `helpBtn(help, extraNote)` đã có tham số. Truyền `C.qd['QĐ-1'] + ' (' + C.unmeasured + ')'` cho C3 khi kịch bản là B, `QĐ-9` cho hộp ngược bias ở C2, `QĐ-19` cho banner trước 20:30, `QĐ-3` cho chip "hạng 2" của cụm POC.

### 18. [CHỮ] "Tôi vẫn vào" ở trạng thái CHỜ ghi mã `WAIT_*` không có `htRef` ⇒ dòng ⚠ trong sổ trống
- **Bằng chứng:** dò: A với B3 "chưa", vào phá luật ⇒ `ruleCodes ['WAIT_B3_NOT']`, `warnLine` = `""`. Dòng sổ có cờ phá luật nhưng không ghi phạm gì; vào trước khi nến xác nhận đóng là lỗi hay gặp nhất.
- **Sửa:** thêm `htRef` cho các mã CHỜ trong `content.codes`: `WAIT_C4`/`WAIT_C4_SAME` 4.3 · `WAIT_C5`/`WAIT_C5_BACK` 4.4 · `WAIT_B1` 4.1 · `WAIT_B2`/`WAIT_B2_MIXED` 4.2 · `WAIT_B3`/`WAIT_B3_NOT` 5 · `WAIT_C7_*` 5 · `WAIT_C6`/`WAIT_CALC`/`WAIT_B5` 6 · `WAIT_COUNTER_REASON` 2.2 · `WAIT_SCENARIO`/`WAIT_ZONE`/`WAIT_SIDE` 5. Thêm test `warnLine`.

### 19. [CHỮ] Các lỗi chữ nhỏ
- `codes.DIS_NO_EDGE`: "(VAH, VAL Âu, IB, cạnh range)" → "(VAH Âu, VAL Âu, IB, cạnh range)".
- `controls.b3.criteria.B[1]`: "Delta đảo dấu từ nửa nến lớn nhất của move" (thiếu chữ "delta", đọc không ra nghĩa) → "Delta đảo dấu, từ ½ delta nến lớn nhất của move" (HT 5·B "≥ 50% delta nến lớn nhất").
- `ui.modeBalancedSub`: "chỉ fade cạnh" sai, vì B tại cạnh cũng bật → "fade cạnh, hấp thụ tại cạnh".
- `zoneTypes.pocCluster.label`: "Cụm POC (2 POC cách ≤ 1 giá)" → "Cụm POC (từ 2 POC, cách ≤ 1 giá)".
- `ui.t0WinNote`: in cứng "19:30 / 21:00", sang mùa đông sai giờ. Dùng `{a}`, `{b}` điền `fmtMin(markMin(...))`, hoặc bỏ giờ cụ thể.
- `notices.US_WINTER` / `LDN_SWITCH`: "lùi thêm 1 giờ" dễ hiểu ngược → "muộn thêm 1 giờ".
- `codes.WAIT_B2_MIXED`: "chưa đủ 3 nến giảm dần" → viết hoa chữ đầu như các mã khác. Đây là chữ plan ghi; chỉ đổi chữ hoa, không đổi mã.
- Placeholder ô "đến giá (tùy chọn)" bị cắt thành "đến giá (tùy c" ở 1366 px (ảnh `d1366-t1-filled.png`) → rút thành "đến giá".

---

## C. UX khác

### 20. [UX] Sổ chỉ xem được đêm hiện tại; qua 05:00 (mùa đông 06:00) là mất lối nhập "Bạn cộng" và "Kết phiên" của đêm trước
- **Mô tả:** plan §1 viết "ban ngày liếc điện thoại (thẻ phiên, sổ)". Hiện tầng 5 luôn dùng `app.key`. Hộp "Lệnh đóng gần nhất" ở tầng 4 chỉ cho sửa 1 lệnh.
- **Sửa:** thêm ô chọn đêm ở đầu tầng 5 (các `nightKey` có thẻ hoặc có lệnh, mới nhất trước). Bảng sổ, "Bạn cộng", "Kết phiên", Markdown đều theo đêm đang chọn. Truyền `{ key }` vào `app.update`.

### 21. [UX] Form thêm vùng: thêm xong, ô giá vẫn hiện số cũ nhưng trạng thái đã về rỗng ⇒ bấm "Thêm vùng" lần nữa thì báo "Nhập giá của vùng"
- **Bằng chứng:** `js/ui/tier012.js:156-166`: `zf.price = null` được gán **sau** `app.cardEdit`, mà `cardEdit` đã vẽ lại trang với giá cũ (ảnh `d1366-t1-filled.png`: ô thêm vẫn hiện 4199 sau khi đã có z4).
- **Sửa:** lấy `type/price/priceTo/side` ra biến cục bộ, gán `zf.price = zf.priceTo = null` **trước** khi gọi `app.cardEdit`.

### 22. [UX] Nút "?" chỉ 22×22 px (dưới mức 24 px của WCAG 2.5.8, khó bấm trên điện thoại)
- **Bằng chứng:** đo `.help` = 22×22 ở cả hai cỡ màn hình; `css/app.css:123`.
- **Sửa:** `.help { width: 28px; height: 28px }`; ở ≤ 900 px thêm `::after` để vùng chạm rộng 44 px.

### 23. [UX] Thanh trạng thái vàng cả ngày (từ 05:00 tới 20:30)
- **Mô tả:** `WARN_BEFORE_2030` bật khi `nowMin < nyseMin`, nên ban ngày cũng vàng. Cảnh báo thường trực làm mất nghĩa màu vàng.
- **Sửa:** `engine.js:217` thêm điều kiện `nowMin >= markMin(R.MARKS.prep)` (18:00).

### 24. [UX] Ở tab "Bấm" khi chưa chọn kịch bản thì không có ô chọn kịch bản; câu hướng dẫn bảo chọn mà không có chỗ chọn
- **Bằng chứng:** `js/ui/tier3.js:102-106`.
- **Sửa:** khi `!scen`, luôn hiện C1 bất kể tab, hoặc tự đặt `app.ui.sub = 'canh'`.

### 25. [UX] Vết sửa thẻ chỉ xem được qua `title` (rê chuột); điện thoại không xem được
- **Bằng chứng:** `js/ui/status.js:85`.
- **Sửa:** dùng `<details>` "n lần sửa" để mở ra danh sách `giờ · nội dung`.

### 26. [UX] Vẽ lại định kỳ 15 s không làm mới nội dung tầng
- **Mô tả:** khi hết khóa 3′ hay vào hoặc ra cửa sổ cấm, bảng "Kịch bản nào đang bật" ở tầng 2, các nút C1 bị tắt và banner "đã 10′" ở tầng 3 vẫn hiện như cũ cho tới cú bấm kế tiếp. Riêng thanh phán quyết thì có cập nhật.
- **Sửa:** trong vòng 15 s, nếu `JSON.stringify(res.enabled)`, `res.newsHit` hay `longestBarActive` khác lần trước thì gọi `render({ keep: false })`; nếu đang gõ trong ô nhập thì chờ sự kiện `blur` rồi mới vẽ.

---

## D. Mã

### 27. [MÃ] Service worker có thể nạp file cũ từ bộ nhớ đệm HTTP khi cài bản mới
- **Mô tả:** `cache.addAll(ASSETS)` đi qua bộ nhớ đệm HTTP; GitHub Pages trả `max-age=600`. Deploy xong trong vòng 10 phút thì bộ nhớ `tdv-<bản mới>` có thể chứa JS cũ, và chạy không mạng sẽ kẹt ở bản cũ cho tới lần đổi số phiên bản sau.
- **Sửa:** `sw.js`: `c.addAll(ASSETS.map((u) => new Request(u, { cache: 'reload' })))`.

### 28. [MÃ] Kích thước: 196 KB thô (plan "< 100 KB"), cộng 730 KB ảnh PNG kịch bản được tải sẵn vào bộ nhớ đệm
- **Sửa:** chuyển 4 ảnh `img/kb-*.png` sang WebP chất lượng 80 hoặc JPEG (≈ 40–60 KB mỗi ảnh). Bỏ chúng khỏi `ASSETS` (để `fetch` tự lưu khi xem). IMPL ghi đúng là "chỉ đạt theo cỡ nén", nên cần chủ plan chấp nhận.

### 29. [MÃ] Nhập JSON thiếu trường làm vỡ trang
- **Mô tả:** `normalizeNight` không chuẩn hóa từng dòng `trades`. Dòng không có `flags` (hoặc `ruleCodes`) sẽ làm `t.flags.indexOf` ném lỗi ở `recomputeTally`, `rowOf`, `weekStats`. Giá vùng dạng chuỗi ("4205") bị coi là không có giá mà không báo gì.
- **Sửa:** trong `normalizeNight`, `trades = (o.trades || []).map(t => Object.assign({ flags: [], ruleCodes: [], tests: {}, exit: null, r: null }, t))`; giá vùng đi qua `J.parseNum`.

### 30. [MÃ] "Kết phiên" gần như không có tác dụng
- **Mô tả:** `manualTally` đã gán `tally.closedAt` mỗi lần gõ vào ô "Bạn cộng". Phép gộp JSON lại dựa vào `closedAt` để chọn bản, nên gõ thử một số ở máy khác cũng làm bản đó "mới hơn".
- **Sửa:** `manualTally` không đụng tới `closedAt`; chỉ nút "Kết phiên" (và `recomputeTally` lúc đóng lệnh) mới gán.

### 31. [MÃ] `parseNum` trả `null` khi gõ có dấu chấm ngăn nghìn ("4.193,5"), ô bị coi như trống mà không báo
- **Sửa:** nếu chuỗi có cả "." lẫn "," thì bỏ "." rồi đổi "," thành "."; nếu `parseNum` trả `null` mà ô không trống thì tô viền đỏ ô đó.

---

## E. Test

### 32. [TEST] Test và fixture khóa luôn hai chỗ tự chọn sai (xem mục 6 và 10)
- `tests/verdict.test.js:332-335` khẳng định R:R/TP bị giấu. `tests/fixtures.test.js:44,58,63` dùng `deepEqual` danh sách đầy đủ nên buộc engine giấu mã. `fixtures.test.js:84` khẳng định `size 0` là bình thường.
- **Sửa:** theo mục 6 và 10. Với fixture, so `reasons.slice(0, 2)` theo plan rồi kiểm thêm mã đầy đủ.

### 33. [TEST] Hai test "bias KHÔNG tắt cả B" mà người implement nói đã sửa: **đúng plan**
- Bảng bật kịch bản của plan, hàng "Bias KHÔNG": A, B, D `DIS_BIAS_NONE`, chỉ C bật; HT 2.2 cũng viết "chỉ fade hai cạnh VA Âu". Không cần làm gì. Năm fixture A1–A5 khớp số của Phụ lục A (vùng, giờ, giá, `slDist`, `rr`, `tpSuggested`, `half`, `missing[0]`), trừ phần mâu thuẫn ở mục 6.

### 34. [TEST] Thiếu test (plan mục 6 và các lỗi ở trên)
- Plan mục 6 "thứ Năm bật 19:30": hiện chỉ test hàm `isThursday`, chưa test mặc định của `windows` (mục 5).
- "Bật kịch bản ≥ 28 ca": đếm được khoảng 27; thiếu `pending` × bias KHÔNG/CHỜ, `thin` × CHỜ, và các tổ hợp acceptance × giờ.
- `tests/verdict.test.js:257-261` (QĐ-4 ngược bias) dùng `includes(A) || includes(B)` nên quá lỏng. Chạy thật ra `['NO_COUNTER_BIAS_ZONE', 'NO_FIGHT_BREAK']`, nên đổi thành `deepEqual` với đúng danh sách này để khóa thứ tự luật.
- A2 chưa kiểm dòng ⚠ "phạm 4.3, 4.1" qua `journal.warnLine` như Phụ lục A yêu cầu.
- Chưa có test cho các mục 1, 3, 4, 7, 8, 9, 14, 18, 21.
- **E2E không đi tầng 0–2 bằng UI:** mọi kịch bản e2e đều gieo sẵn thẻ đã chốt và chế độ (`e2e/helpers.mjs:buildState`), nên lỗi 1 và 21 lọt. Thêm 1 e2e đi từ dữ liệu trống: tầng 0 → chốt thẻ → vừa phá 2 bước → ENTRY. Có thể dùng `scratchpad/walk.mjs` của review này làm mẫu (đường dẫn trong phần "Ghi chú" cuối file).
- E2E 360 px chỉ kiểm tràn ngang. Cần thêm: mở rồi đóng ngăn thẻ phiên (mục 2), và đo tổng chiều cao hai thanh dính ≤ 35 % màn hình.

---

## Ghi nhận phần làm tốt
- Thứ tự luật trong `RULES` khớp đúng thứ tự plan mục 5. `DIS_*` đúng nguyên tắc "không cần vùng/hướng". Bảng bật kịch bản đúng hàng nào ra mã nấy.
- Ma trận bias (14 ca, có QĐ-12), QĐ-9 (cờ `tail`/`sp` đúng phía, ép 2R, ½, bắt lý do), QĐ-4, QĐ-17 (không đếm luyện mắt), QĐ-8 (½ một lần) đều đúng.
- Giờ mùa đông, `nightKey`, cửa sổ ±15′/±5′, thẻ đổi giờ đều đúng ở 8 ngày mốc. `file://` không lỗi. Tải lại giữ đúng tầng và lựa chọn. Phím tắt tự tắt khi đang gõ. Không có "bán/mua/lệnh chờ/đập giá" ở bất kỳ file JS nào.

## Ghi chú
- Ảnh review: `docs/review-shots/d1366-t0…t5*.png`, `p360-t0…t5*.png`, `p360-the-phien-mo.png`.
- Kịch bản Playwright đi tay và đoạn dò engine (không đưa vào repo): `C:\Users\anhla\AppData\Local\Temp\claude\c--Users-anhla-OneDrive-Documents-footprint-tpo\bcfa2f0c-e665-455f-9235-2f428bc8a04f\scratchpad\walk.mjs`, `...\scratchpad\probe.js`, `...\scratchpad\drawer.mjs`.
- Các mục 3, 5, 6, 7, 8, 10, 28 có phần cần **chủ plan chốt**: ghi vào `docs/IMPL-2.md` mục "Chờ chủ plan", không tự quyết trong code ngoài cách sửa tối thiểu đã nêu.

---

## Kết luận
1. Engine bám plan tốt ở phần lớn luật, nhưng có 3 cửa mở cho lệnh hệ thống cấm: phá chưa công nhận vẫn bật A (mục 1), C ngoài cạnh VA Âu khi bias KHÔNG (mục 3), và né ngắt mạch SL bằng "Về hòa" (mục 4).
2. Có 1 lỗi chặn đường trên điện thoại (ngăn thẻ phiên không đóng được). Có 4 chỗ lệch plan chặn oan kèo đúng, trong đó cửa sổ 19:30 chặn chính ca ĐÚNG 5/10 19:25.
3. Test xanh nhưng có chỗ khóa luôn cách tự chọn sai của người implement (mục 6, 10), và e2e không đi tầng 0–2 bằng UI. Phải sửa các mục 1–9 rồi mới cho người dùng thử thật.

| Mức | Số mục | Mục |
|---|---|---|
| SAI LUẬT | 7 | 1, 3, 4, 5, 6, 7, 8 |
| CHẶN ĐƯỜNG ĐI | 1 | 2 |
| MÃ | 8 | 9, 13, 14, 27, 28, 29, 30, 31 |
| UX | 11 | 10, 11, 12, 15, 20, 21, 22, 23, 24, 25, 26 |
| CHỮ | 4 | 16, 17, 18, 19 |
| TEST | 3 | 32, 33 (ghi nhận đúng), 34 |
| **Tổng** | **34** | |
