# REVIEW-3 — Trạm Đêm Vàng, vòng 3 (kỹ thuật + nghiệp vụ)

Ngày 2026-10-20 · Người review: Claude Opus · Đối chiếu: plan bản 4 + QĐ-1…QĐ-21 (`plans/CHECKLIST-DEM-VANG-plan.md`), trang HT (bản text), mã ở commit `78b9ee1` (bản chạy 1.0.3; Pages trả 200, `APP_VERSION = '1.0.3'` khớp `sw.js`).

**Số chạy lại thật trên máy này:** `npm test` 209/209 xanh · `npm run e2e` 27/27 xanh · `npm run lint:vi` 0 lỗi (4 khóa ui không dùng: `cardEdits`, `boNeed`, `sideNone`, `unitGiaShort`).
**Đi tay** tầng 0→5 từ dữ liệu trống bằng Playwright với **chuột thật** (`mouse.move/down/up`, giữ 90 ms) ở 1366×768 và 360×740, giờ 21:30 và 20:24 ngày 20/10/2026, và 21:00 ngày 03/11/2026 (mùa đông Mỹ). Console không lỗi. Ảnh ở `docs/review-shots-3/` (`d1366-*`, `d1366-2024-*`, `d1366-dong-*`, `p360-*`, `hold-T1-help-mat.png`, `*-toast-che.png`, `*-c6-sau-thanh.png`).
Kịch bản dò (không đưa vào repo), thư mục `C:\Users\anhla\AppData\Local\Temp\claude\c--Users-anhla-OneDrive-Documents-footprint-tpo\bcfa2f0c-e665-455f-9235-2f428bc8a04f\scratchpad\r3\`: `probe1.js` (engine: QĐ-21, C chờ công nhận, SL sau be, TẮT MÁY, gộp JSON, mùa đông), `probe2.js` (đường khó), `walk3.mjs` (đi tay), `hold.mjs`, `t1.mjs`, `t3b.mjs` (click sau khi gõ), `toast.mjs`, `fit.mjs`, `dbg360.mjs`, `fs.mjs`.

Chỉ ghi chỗ **chưa đạt**. Nặng trước.

---

## A. Sai luật

### 1. [SAI LUẬT] Lệnh lỗ nhỏ (−0,5R < R < −0,2R) xóa chuỗi SL về 0 ⇒ lách được TẮT MÁY; tài liệu nói "±0,2R là hòa" nhưng mã không có ngưỡng 0,2
- **Mô tả:** QĐ-10: "Chỉ SL cộng chuỗi; TP và hòa reset". Mã coi mọi lệnh có R > −0,5 là "không phải SL" và **cắt chuỗi** (`break`). Vậy sau 2 SL, lệnh thứ ba "Đóng tay · Hấp thụ ngược đe dọa TP" ở −0,45R (lý do hợp lệ, không tính phá luật) đưa chuỗi về 0 thay vì giữ 2/3. Tương tự: "Về hòa" hoặc "Chạm SL (đã ở hòa vốn)" mà gõ giá thoát xấu tới −0,4R. Lệnh lỗ 0,45R không phải TP, cũng không phải hòa. IMPL-3 (tự chọn 3) ghi "R trong [−0,2; +0,2] coi là hòa" nhưng trong mã không có ngưỡng 0,2 nào; chỉ có −0,5.
- **Bằng chứng:** `js/engine.js:14-19` (`isSLTrade` chỉ so −0,5), `:29-35` (không phải SL ⇒ `break`). Dò `probe1.js`: `SL, SL, MANUAL −0,45 ⇒ slStreak 0`; `SL, SL, BE −0,3 ⇒ 0`. Test `tests/review2-fixes.test.js:102-105` chỉ thử −0,2.
- **Sửa:** trong `countTrades`: R ≤ −0,5 (hoặc kind SL chưa be) ⇒ cộng; −0,5 < R < −0,2 ⇒ `continue` (không cộng, **không reset**); chỉ TP, R ≥ −0,2 (hòa) mới `break`. Ghi QĐ vào plan (đây là quyết định của công cụ, chưa đo) và thêm test cho −0,45 và −0,3.

### 2. [SAI LUẬT] Đổi hướng phá hoặc cạnh vừa phá **sau khi đã công nhận** vẫn giữ bước 1, bước 2 ⇒ cú phá hướng mới được công nhận ngay, không cần nến M5 nào
- **Mô tả:** ở tầng 2, nút "Phá lên / Phá xuống" và chọn "Cạnh vừa phá" vẫn bấm được sau khi bước 1, 2 đã "Có", và chỉ ghi `dir` / `edgeZoneId`. HT 3.1: công nhận cần nến M5 đóng ngoài **cạnh đó** rồi nhịp hồi giữ được; đổi hướng là một cú phá khác (REVIEW-1 mục 1 đã đặt nguyên tắc "vào Vừa phá là cú phá mới: xóa bước 1, bước 2").
- **Bằng chứng:** `js/ui/tier012.js:264` (`breakout.dir = v`), `:266` (`edgeZoneId = v`), không đụng `step1/step2`. Dò `probe2.js`: công nhận phá xuống tại z2, đổi sang "lên" ⇒ `step1/2 vẫn true true`, chế độ hiệu lực `broken · lên` (bias SELL nên A ra `DIS_BREAK_AGAINST_BIAS`; với bias BUY thì A buy bật ngay).
- **Sửa:** khi `dir` hoặc `edgeZoneId` đổi giá trị mà bước 1 đã có: đặt `step1 = step2 = false`, `at` = bây giờ, ghi `regime.log` (có thể hỏi xác nhận "Đổi hướng = cú phá mới, công nhận lại?"). Thêm unit test + e2e.

---

## B. Click bị nuốt (dạng mới) và chặn click

### 3. [UX] Sau khi gõ số, bấm "?" hoặc bấm mở một mục thu gọn thì nó mở ra rồi **tự đóng** sau ~0,1 giây (hồi quy của cách sửa "hoãn vẽ lại")
- **Mô tả:** ô số có `onCommit` gây vẽ lại cả tầng (C6, "Move vừa rồi" của D, giá vùng ở tầng 1, Giá hiện tại / VWAP tuần ở tầng 1, "Bạn cộng"). Gõ xong bấm thẳng: (a) nút "?" — `helpBtn` mở khung rồi `stopPropagation`, nên chỉ còn bộ hẹn 100 ms của `pointerup` gọi `flushHold` ⇒ vẽ lại ⇒ khung mất; (b) tiêu đề `<details>` (ảnh kịch bản "Phá hồi · mục tiêu 3R…", "Cỡ lệnh MGC", "Ghi đè bias (cần lý do)", "Sau đóng lệnh…") — mở ra rồi bị vẽ lại đóng. Người dùng thấy "bấm không ăn", đúng loại lỗi vòng này định sửa. Các nút có tự vẽ lại (nút 3 trạng thái, "Kèo mới", ô tick) thì không bị.
- **Bằng chứng:** `js/main.js:55` (hẹn 100 ms), `:58` (vẽ bù sau click), `js/ui/dom.js:56-57` (`stopPropagation` trong "?"). `t1.mjs` (chuột thật, 1366×900): chưa gõ ⇒ `"?" pop 1`, `details open 1`, DOM giữ nguyên; gõ C6 "2" ⇒ `pop 0`, `details 0`, `rebuilt: true`. `hold.mjs` T3, T3c (tầng 1 sau khi sửa giá vùng): `pop 0`, `details 0`. Ảnh `hold-T1-help-mat.png`. e2e `v3-1`, `v3-2` không thử loại nút này.
- **Sửa:** trong `render()` chụp và khôi phục trạng thái mở như đang làm với focus: `details[open]` (khóa = `data-ctl` + chữ `summary`) và `.pop:not([hidden])` (khóa = `data-ctl` gần nhất hoặc chỉ số nút "?"). Hoặc đơn giản hơn: `helpBtn` và `summary` gọi `app.flushNow()` (vẽ phần hoãn) **trước** khi tự mở. Thêm e2e: gõ C6 rồi bấm "?" của C4 và tiêu đề ảnh kịch bản, chờ 300 ms, phải còn mở.

### 4. [UX] Thông báo nổi (toast) chặn click 4 giây ngay giữa vùng nút của tầng 3; nếu sau đó gõ số vào chỗ không có ô, phím số đổi kịch bản
- **Mô tả:** `.toast-item` có `pointer-events: auto`, nằm giữa màn hình cách đáy 110 px, sống 3,6 s + 0,4 s. Ngay sau "Chốt thẻ phiên" (2 toast: cảnh báo kế hoạch + đã chốt), "Kèo mới", "Đã ghi lệnh…", các toast đè lên hàng C4 / C5 ở 1366×768. Lần đi tay đầu tiên: bấm "Không có / giữa move" của C4 trúng toast (mất), bấm ô C6 cũng không vào ô, gõ "2" ⇒ phím tắt **2 = chọn kịch bản B**: kèo A thành B, thiếu vùng, hướng, bong bóng (thanh "CHỜ thiếu: Chọn vùng · Chọn hướng · Bong bóng…").
- **Bằng chứng:** `css/app.css:234-235`. `toast.mjs`: 1366×768 sau "Chốt thẻ" + "Kèo mới" ⇒ `covered: ["c4:unclear"]`; ảnh `d1366-toast-che.png`, `p360-toast-che.png`. Toast cũng nằm trên hộp Từ điển (`p360-glossary.png`).
- **Sửa:** `.toast-item { pointer-events: none }` (giữ `auto` cho `.sticky` có nút "Tải lại"), hoặc dời toast lên góc trên phải, ngoài vùng nút. Thêm e2e: sau "Kèo mới" bấm ngay C4 phải ăn.

---

## C. Mã

### 5. [MÃ] "Tôi vẫn vào" khi kịch bản đang **tắt** (`DIS_*`) chỉ ghi mã DIS, bỏ mất mọi `NO_*` khác (V, lưng, SL…) — trái QĐ-20 "mọi luật NO_* luôn được xét để ruleCodes đủ"
- **Bằng chứng:** `js/engine.js:203` (`if (c.blocked) return;` bỏ qua cả NO lẫn WAIT sau khi DIS chặn). Dò: A ở cân bằng + V + "từ 3 giá" ⇒ `forceCodes = ['DIS_NOT_BROKEN']`; dòng ⚠ sổ chỉ "phạm mục 3.1", mất "4.1, 4.4". Cuối tuần đếm sai luật nào bị phạm nhiều nhất.
- **Sửa:** khi `blocked`, vẫn chạy các luật NO nhưng ghi vào danh sách phụ (`c.shadow`), trả trong `ruleReasons` (phán quyết không đổi). Test: ca trên ⇒ `['DIS_NOT_BROKEN', 'NO_BACK', 'NO_V_PULLBACK']` theo thứ tự luật.

### 6. [MÃ] Xóa trắng ô Vốn hoặc Rủi ro ở tầng 5 ⇒ `capital = null` được lưu ngay ⇒ ENTRY không còn số hợp đồng và `NO_SIZE_ZERO` không bao giờ xét
- **Bằng chứng:** `js/ui/tier45.js:215-217` (`oninput` ghi `v` kể cả `null`); `js/engine.js:106` trả `null`; `js/rules.js:285` cần `sizeOf() !== null`. Dò `probe2.js`: `capital null ⇒ ENTRY, size null`. Hộp vốn lần đầu có kiểm (`capBad`) nhưng ô ở Cài đặt thì không.
- **Sửa:** ô Cài đặt chỉ ghi khi `v > 0` (dùng `onCommit`, ô trống thì trả lại số cũ); engine: thiếu vốn hoặc % ⇒ mã CHỜ "Cài vốn và % rủi ro" trỏ tới nút "Đổi vốn".

### 7. [MÃ] Ghi đè bias **bằng đúng** bias tự động vẫn bật cờ "ghi đè" ⇒ `DIS_BREAK_AGAINST_BIAS` bị bỏ qua: bảng tầng 2 hiện A, D "bật" khi phá ngược bias, tới tầng 3 mới ra KHÔNG VÀO
- **Bằng chứng:** `js/rules.js:140` (`overridden` không so với `auto`), `:183-187`. Dò: tự động SELL, phá lên ⇒ A `DIS_BREAK_AGAINST_BIAS`; ghi đè SELL (lý do có) ⇒ A bật, tầng 3 `NO_COUNTER_BIAS_SCENARIO`.
- **Sửa:** `overridden = !!override && override !== auto`.

---

## D. Chữ

### 8. [CHỮ] Hộp "Cỡ lệnh MGC" nói "cỡ ½ … nên chỉ rủi ro 20 $" trong khi QĐ-21 vào 1 hợp đồng, rủi ro thật 24 $ (SL 2,4)
- **Bằng chứng:** `js/ui/tier3.js:66` dùng `cc.riskUsd` (½ số $) kể cả khi `sizeMinOne`; `js/content.js:330` (`sizeHalf`). Hộp này hiện khi CHỜ / KHÔNG VÀO (A1 6/10 20:24 lúc chưa chọn B5).
- **Sửa:** khi `sizeMinOne`: "Cỡ ½ ({why}) không chia được: vào 1 hợp đồng, rủi ro thật {real} $ (hơn ½ kế hoạch)", `real = slDist × 10`.

### 9. [CHỮ] Chữ `NO_C_NOT_EDGE` hẹp hơn luật: chỉ nói "cạnh VA Âu hoặc cạnh range", nhưng engine (và bảng 1d của plan) nhận cả IB high / low và High / Low hôm qua
- **Bằng chứng:** `js/content.js:84`; `js/rules.js:216-219` (`edge` hoặc `edgeOuter`). Dò: C ở IB low, Low hôm qua ⇒ ENTRY.
- **Sửa:** "Fade chỉ ở vùng cạnh (VAH / VAL Âu, IB, cạnh range, High / Low hôm qua), cách không quá 1 giá; vùng này không phải cạnh."

### 10. [CHỮ] Nút "Thêm FOMC 01:00" in cứng giờ; từ 01/11 cửa sổ FOMC thực là 02:00 VN (mã đã dịch đúng, đóng sạch trước 01:45)
- **Bằng chứng:** `js/content.js:283` (`addFomc`), `js/ui/tier012.js:59-60` (`at: '01:00', tz: 'ET'`). Mục 6 REVIEW-2 sót chỗ này.
- **Sửa:** `addFomc: 'Thêm FOMC {fomc}'`, điền `time.fmtMin(time.markMin({at:'01:00',tz:'ET'}, key, useDst))`.

### 11. [CHỮ] Từ điển: ví dụ số (mồi 4210 / 4208, trap 4200 → 4194 → 4197) là minh họa của công cụ nhưng không ghi, trong khi đầu Từ điển nói "lấy từ trang Hệ thống"
- **Bằng chứng:** `js/content.js:396`, `:400`; IMPL-3 tự chọn 8 tự nhận là minh họa. Ví dụ R (4193,0 / 4195,4) là ca thật 6/10 nên không sao.
- **Sửa:** thêm "(ví dụ minh họa, không phải ca thật)" sau hai ví dụ. 20 mục còn lại khớp HT (đã đối chiếu 2.1, 2.2, 3, 3.1, 3.2, 4.3, 5·A–D, 6, 7).

---

## E. UX

### 12. [UX] Chữ ENTRY 30 px trên máy tính (26 px điện thoại), plan §3c ghi "≥ 32 px" — IMPL-3 tự chọn 11 trái plan
- **Bằng chứng:** `css/app.css:197`, `:251`; đo `fs.mjs`: 1366 ⇒ 30px, 1920 ⇒ 30px, 360 ⇒ 26px.
- **Sửa:** giữ 32 px; lấy chỗ bằng cách gộp dòng chip "Cỡ ½ vì …" vào thanh phán quyết, hoặc rút `erest` (bỏ "(2,4 giá)" khi màn hẹp).

### 13. [UX] Mùa đông (mỗi đêm từ 01/11 tới 14/03): dòng "Mỹ đang giờ mùa đông…" làm thanh trên cao thêm 33 px ⇒ bước Bấm của B trước 21:30 không vừa 1366×768, B5 nằm dưới thanh phán quyết
- **Bằng chứng:** `fit.mjs`: hè 21:30 / 20:24, A và B ⇒ `scrollHeight 768`; đông 03/11 21:00, B ⇒ `797 / 768`, đáy B5 657 > đỉnh thanh phán quyết 652; thanh trên 47 ⇒ 80 px. `js/ui/status.js:50-51` in thông báo mỗi đêm. e2e `v3-9` chỉ đo ngày hè.
- **Sửa:** đêm thường chỉ thêm chip ngắn "+1h" trên thanh trạng thái (chữ đầy đủ trong "?"); dòng dài chỉ hiện đúng ngày đổi giờ. Thêm ca mùa đông vào `v3-9`.

### 14. [UX] Thanh phán quyết cố định che ô cuối của Canh mà trình duyệt vẫn coi là "đang thấy"; điện thoại chạm vào chỗ ô C6 lại trúng nút của thanh và nhảy sang Bấm
- **Bằng chứng:** `dbg360.mjs` sau khi cuộn ô C6 "vào tầm nhìn": 360×740 ⇒ điểm giữa C6 là nút "Nhịp hồi U hay V" của thanh (`focusCtl('b1')` ⇒ sang Bấm); 1366×768 ⇒ trúng thanh. Ảnh `p360-c6-sau-thanh.png`, `d1366-c6-sau-thanh.png`. Tab vào C6 cũng để ô nằm dưới thanh. `css/app.css:25` chỉ có `padding-bottom`, không có `scroll-padding`.
- **Sửa:** `html { scroll-padding-bottom: calc(var(--vbar-h, 120px) + 16px); }`; `focusCtl` và tô "ô cần làm" cuộn ô kế tiếp lên trên thanh.

### 15. [UX] Gõ số rồi Tab sang một nút (không phải ô nhập) ⇒ vẽ lại ⇒ mất focus về `body`, Tab kế tiếp chạy lại từ đầu trang
- **Bằng chứng:** `js/main.js:60` (vẽ ở `focusin`), `:62-77` (`snapFocus` chỉ giữ INPUT / TEXTAREA / SELECT). `hold.mjs` T6: sau Tab ⇒ `BODY.has-vbar`.
- **Sửa:** `snapFocus` nhận cả `button` (khóa = `data-ctl` + `data-v` hoặc `data-testid`).

---

## F. Test

### 16. [TEST] Chưa có test cho các lỗi trên
- Unit: chuỗi SL với R −0,45 / −0,3 (mục 1); đổi hướng hoặc cạnh sau công nhận (mục 2); "Tôi vẫn vào" khi DIS + NO khác (mục 5); vốn `null` (mục 6); ghi đè bằng tự động (mục 7).
- E2E: "?" và `<details>` ngay sau khi gõ (mục 3); bấm ngay sau toast (mục 4); vừa một màn ở ngày mùa đông (mục 13). E2E hiện dùng `page.click()` cho mọi nút: nên có một ca bằng `mouse.down` / `mouse.up` giữ ≥ 80 ms như người thật.

---

## Kiểm lại 16 mục REVIEW-2 ghi "đã sửa"

Đúng và không hồi quy (dò engine + đi tay chuột thật):
- **1 QĐ-21** — vốn 2 000 $ / 2 %: A1 6/10 20:24 ⇒ ENTRY, 1 hợp đồng, chữ "cỡ ½ không chia được — 1 hợp đồng (tối thiểu)" (ảnh `d1366-2024-t3-bam-entry.png`); C 21:30 SL 2,4 và SL 4,0 ⇒ 1 hợp đồng; SL 4,1 ⇒ `NO_SL_CAP … NO_SIZE_ZERO`; 1 000 $ ⇒ `NO_SIZE_ZERO` với "SL tối đa 2,0"; 5 000 $ ⇒ cỡ chuẩn 4, ½ = 2. Hộp vốn hiện ở lần mở đầu (cả 360 px), "Để sau" không hỏi lại. (Chữ sai ở mục 8.)
- **2 C khi chờ công nhận** — single print, poor low, naked POC, HVN 3 tuần, VWAP tuần ⇒ `NO_C_NOT_EDGE`; VAL Âu khác cạnh vừa phá, IB low, Low hôm qua ⇒ ENTRY; cạnh vừa phá ⇒ `NO_PENDING_ACCEPT`; bias KHÔNG tại Low hôm qua ⇒ `NO_BIAS_NONE_EDGE`.
- **3 SL sau be** — UI: dời be rồi "Chạm SL (đã ở hòa vốn)" ⇒ giá mặc định 4193,0, R 0, `beStop`, chuỗi 0/3 (cả 1366 và 360). (Lỗ hổng ngưỡng ở mục 1.)
- **4 TẮT MÁY + "Tôi vẫn vào"** — `['OFF_RULE_BREAKS', 'NO_V_PULLBACK']`; thiếu B1 ⇒ thêm mã CHỜ. (Trường hợp DIS ở mục 5.)
- **5 gộp JSON** — 21:00 SL · 23:50 SL · 00:20 TP ⇒ đúng thứ tự, chuỗi 0.
- **6 giờ theo mùa** — 03/11: `comex 20:20, nyse 21:30, real 21:20–22:30, FOMC 01:45`; 21:00 VN ⇒ cỡ ½ "trước 21:30", dải "Mở ảo"; 22:00 ⇒ `NO_NEWS_WINDOW`; phá lúc 20:10 ⇒ `DIS_EARLY_BREAK`; `nightKey` 04/11 05:30 ⇒ đêm 03/11, 06:00 ⇒ đêm 04/11; thứ Năm 05/11 "đóng sạch trước 20:15". (Sót nút FOMC, mục 10.)
- **7 Q1…Q6**, **8 Từ điển 2 mục**, **9 chữ `NO_SIZE_ZERO`**, **10 QĐ-19 trong "?"** (thanh trạng thái, banner tầng 2, chip thanh phán quyết), **11 không còn "Cú phá đáng tin" lúc 20:24**, **13 A/D "Chọn hướng ở tầng 2"** (bước 1 khóa tới khi có hướng + cạnh, bước 2 khóa thật), **14 nút Thẻ phiên không đè chip ở 360 px**, **15 Giá hiện tại còn sau tải lại**: đúng.
- **12 vừa một màn** — đúng ngày hè (768/768 ở 21:30 và 20:24, A và B); mùa đông B trước 21:30 vượt (mục 13).
- **16 test** — đúng phần đã nêu; còn lỗ ở mục 16.
- **Click bị nuốt (USER-TEST-2 #1)** — với nút 3 trạng thái, ô tick, "Thêm vùng", "Vào lệnh", "Đã dời", "Xác nhận đóng": ăn ở lần bấm đầu bằng chuột thật; gõ rồi Enter (không mở hộp vào lệnh, số được lưu, focus giữ); gõ rồi Esc rồi phím tắt; gõ rồi chuyển tab trình duyệt; nhấn chuột rồi kéo ra ngoài (state và ô hiển thị khớp): đều đúng. Lỗi còn lại ở mục 3, 15.

## 12 chỗ tự chọn ở IMPL-3

| # | Kết luận |
|---|---|
| 1 "Để sau" / Esc đặt `sizeAsked` | Không trái |
| 2 SL tối đa = rủi ro chuẩn ÷ 10 $ | **Hợp lý**: đúng số học (cỡ chuẩn 1 hợp đồng), ở mặc định trùng trần 4 giá, chỉ in trong `NO_SIZE_ZERO` kèm "bỏ kèo, hoặc tăng vốn", không khuyên thu SL (đúng HT 6) |
| 3 "±0,2R là hòa" | **Không hợp lý như đang chạy**: mã không có ngưỡng 0,2; khoảng (−0,5; −0,2) reset chuỗi ⇒ mục 1 |
| 4 gõ giá khác sau be thì R theo giá đó | Không trái |
| 5 `NO_C_NOT_EDGE` cùng mã ngược bias | Không trái |
| 6 `WAIT_SIDE` cho B, C; `WAIT_REGIME_DIR` cho A, D | Không trái |
| 7 sao chép từ đêm trước cùng tuần | Không trái (có câu nhắc sửa giá) |
| 8 ví dụ số trong Từ điển là minh họa | Chưa ghi rõ ⇒ mục 11 |
| 9 ẩn hộp tính khi ENTRY | Không trái (thanh ENTRY có SL, R:R, số hợp đồng) |
| 10 bước 2 chặn thật | Không trái |
| 11 ENTRY 34 → 30 px | **Trái plan §3c (≥ 32 px)** ⇒ mục 12 |
| 12 hoãn vẽ lại chỉ cho `change` | Đúng hướng nhưng gây mục 3 và 15 |

---

## Kết luận
1. Vòng 3 sửa đúng cả 16 mục REVIEW-2 (mục 12 chỉ đúng ngày hè); test, e2e, lint xanh thật; bản 1.0.3 đã lên Pages; đi tay 0→5 bằng chuột thật ở 1366 và 360 px không lỗi console.
2. Còn 2 lỗi luật ở đường hiếm: lệnh lỗ −0,2R…−0,5R xóa chuỗi SL (lách TẮT MÁY), và đổi hướng / cạnh sau khi đã công nhận giữ nguyên công nhận.
3. Cách sửa click bị nuốt đúng cho nút chọn nhưng tạo dạng mới với "?" và mục thu gọn; toast giữa màn hình chặn click 4 giây. Còn lại là mã ghi sổ thiếu, chữ và vừa màn mùa đông.

| Mức | Số mục | Mục |
|---|---|---|
| SAI LUẬT | 2 | 1, 2 |
| CHẶN ĐƯỜNG ĐI | 0 | — |
| MÃ | 3 | 5, 6, 7 |
| CHỮ | 4 | 8, 9, 10, 11 |
| UX | 6 | 3, 4, 12, 13, 14, 15 |
| TEST | 1 | 16 |
| **Tổng** | **16** | |

**Đã đủ để người dùng thật dùng đêm nay chưa?** **Có.** Không còn lỗi chặn đường đi; đường chính (kẻ vùng → bias → chế độ → A/B/C/D → ENTRY đúng số hợp đồng ở vốn mặc định → be → đóng → sổ) chạy đúng luật cả trước và sau 20:30, và đêm nay 20/10 còn là giờ mùa hè. Hai lỗi luật chỉ xảy ra khi người dùng tự làm khác thường; đêm nay tự giữ ba điều: (a) lỗ do đóng tay vẫn tự tính là một SL khi đếm 3 SL liên tiếp; (b) đã công nhận cú phá mà muốn đổi hướng hoặc cạnh thì bấm "Chui lại trong" rồi công nhận lại từ bước 1; (c) vừa chốt thẻ hoặc bấm "Kèo mới" thì chờ thông báo tắt (≈ 4 giây) rồi mới bấm hàng bong bóng / giá cách vùng. Mục 3, 4 nên sửa trong vòng tới; mục 10, 13 phải xong trước 01/11/2026.
