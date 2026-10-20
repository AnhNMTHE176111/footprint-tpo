# REVIEW-2 — Trạm Đêm Vàng, vòng 2 (kỹ thuật + nghiệp vụ)

Ngày 2026-10-20 · Người review: Claude Opus · Đối chiếu: plan bản 4 + QĐ-20, QĐ-21 (`plans/CHECKLIST-DEM-VANG-plan.md`), trang HT (bản text), mã ở commit `717d823` (bản chạy 1.0.2, Pages trả 200, `APP_VERSION = '1.0.2'`).

**Số chạy lại thật trên máy này:** `npm test` 185/185 xanh · `npm run e2e` 15/15 xanh · `npm run lint:vi` 0 lỗi (3 khóa ui không dùng: `cardEdits`, `boNeed`, `unitGiaShort`). Đi tay tầng 0→5 từ dữ liệu trống bằng Playwright ở 1366×768 và 360×740, giờ 21:30 và 20:24 ngày 20/10/2026; console không lỗi. Ảnh ở `docs/review-shots-2/` (`d1366-*`, `p360-*`, `d1366-2024-*`). Dò engine bằng `scratchpad/r2/probe2.js`, `probe3.js` (đường dẫn đầy đủ ở cuối file).

Chỉ ghi chỗ **chưa đạt**. Nặng trước.

---

## A. Sai luật

### 1. [SAI LUẬT] Cỡ lệnh chưa theo QĐ-21: cỡ ½ làm tròn xuống ra 0 ⇒ `NO_SIZE_ZERO` chặn gần hết kèo hợp lệ ở cài đặt mặc định
- **Mô tả:** QĐ-21: `NO_SIZE_ZERO` chỉ khi **cỡ chuẩn** < 1 hợp đồng; cỡ chuẩn ≥ 1 mà ½ < 1 thì size = 1 kèm chữ "cỡ ½ không chia được — 1 hợp đồng (tối thiểu)"; lần mở đầu hỏi vốn và % rủi ro. Code hiện nhân ½ vào số $ rồi làm tròn xuống, nên với 2.000 $ / 2 % (mặc định) và SL ≥ 2,1 giá: **mọi kèo C**, **mọi kèo trước 20:30**, B ở hạng 2, ngày có tin đều ra 0 hợp đồng ⇒ KHÔNG VÀO. Chính ca ĐÚNG 6/10 20:24 (fixture A1) bị chặn. Chưa có hộp hỏi vốn lần đầu.
- **Bằng chứng:** `js/engine.js:91-99` (`riskUsd × 0,5` rồi `Math.floor`); `js/rules.js:277`. Dò: A 20:24 mặc định ⇒ `NO [NO_SIZE_ZERO] size 0 half [BEFORE_2030]`; C 21:30 mặc định ⇒ `NO [NO_SIZE_ZERO]`; D 20:24 ⇒ như A. UI: ảnh `d1366-2024-t3-bam-entry.png` (8 chấm sáng hết mà vẫn KHÔNG VÀO). Test `tests/fixtures.test.js:89-91` khóa luôn hành vi cũ. Test dùng vốn 20.000 $ (`tests/helpers.js:11`) nên không thấy lỗi này.
- **Sửa:** trong `sizeFor`: `full = floor(cap·rp/100 / (slDist·10))`; nếu có `halfs`: `n = floor(full$·0,5 / (slDist·10))`, và nếu `full ≥ 1 && n < 1` thì `n = 1`, `cl.sizeMinOne = true`; lưu `cl.sizeFull = full`. `NO_SIZE_ZERO` đổi `when` thành `cl.sizeFull === 0`. Thanh ENTRY khi `sizeMinOne`: thay "cỡ ½ · 0 hợp đồng" bằng "cỡ ½ không chia được — 1 hợp đồng (tối thiểu)" (thêm khóa ui, lint ≤ 9 từ thì để trong `rest`). Thêm cờ `settings.sizeAsked`: lần đầu `boot()` mở hộp hỏi vốn + % (mặc định 2.000 / 2), lưu xong đặt `true`. Test: đổi `fixtures.test.js:89` thành ENTRY size 1; thêm A1 với `capital 2000` đúng Phụ lục A ⇒ ENTRY size 1; vốn 1.000 $, SL 2,4 ⇒ `NO_SIZE_ZERO` (cỡ chuẩn 0); e2e một ca trước 20:30 với cài đặt mặc định.

### 2. [SAI LUẬT] Hồi quy của R8: khi `pending`, C vào được ở single print / poor low / Low hôm qua ngoài cạnh; ở VWAP, naked POC, LVN, HVN thì kẹt CHỜ "Chọn hướng" không có chỗ chọn
- **Mô tả:** R8 sửa `NO_MID_RANGE` thành chỉ xét `balanced` — đúng cho B, nhưng luật này cũng là chốt vùng duy nhất của **C**. HT 5·C: "giá ở đúng cạnh VA Âu / range (≤ 1 giá)", loại bỏ "giá ở giữa range"; bảng 1d của plan: C chỉ hợp lệ ở `edge`, `edgeOuter`. Nay khi `pending`: C buy ở single print phía dưới hoặc poor low ⇒ **ENTRY 8/8 chấm**; C ở vùng không có phía (VWAP tuần, naked POC, LVN, HVN 3 tuần) ⇒ CHỜ "Chọn hướng" mãi, trong khi C2 của C là tự điền, không bấm được.
- **Bằng chứng:** `js/rules.js:206-212` (`e !== 'balanced'` trả `false` cho cả C). Dò `probe3.js`: `C pending buy at sp ⇒ ENTRY`, `C pending buy at poorLow ⇒ ENTRY`; so với `balanced` cùng vùng ⇒ `NO [NO_MID_RANGE]`. `probe2.js`: `C pending at vwapW/nakedPoc/lvn/hvn3w ⇒ WAIT [WAIT_SIDE, …]`.
- **Sửa:** tách nhánh C khỏi điều kiện chế độ: `if (c.scen === 'C') return !hasFlag(z,'edge') && !hasFlag(z,'edgeOuter');` đặt **trước** dòng `if (!z || c.counter || e !== 'balanced') return false;` (C đã bị tắt ở `broken`/`thin` nên không cần xét chế độ). Giữ nhánh B như R8. Thêm test: C `pending` tại sp / poorLow / VWAP tuần ⇒ `NO_MID_RANGE`; C `pending` tại VAL Âu khác cạnh vừa phá ⇒ qua.

### 3. [SAI LUẬT] Sau khi đã dời SL về hòa vốn, bấm "Chạm SL" ghi **−1R** và cộng chuỗi SL ⇒ sổ sai R, có thể TẮT MÁY oan
- **Mô tả:** `markBE` chỉ bật cờ `beDone`, `trade.sl` vẫn là SL gốc. Ở tầng 4, chọn "Chạm SL" thì giá thoát mặc định là `t.sl` gốc ⇒ `r = −1`, `kind = SL` ⇒ chuỗi SL +1. Sau be, giá quay về giá vào là chuyện thường; người dùng bấm "Chạm SL" (đúng là SL vừa bị chạm) thì sổ ghi thua 1R, máy cộng sai, và ba lần như vậy là TẮT MÁY trái QĐ-10 ("hòa reset"). Cùng gốc: đóng "Về hòa vốn" với giá trượt 1 tick (r = −0,04) cũng bị đếm là SL vì luật mới `r < 0`.
- **Bằng chứng:** `js/ui/tier45.js:90` (`ck === 'SL' ? t.sl`); `js/journal.js:185-192, 202`; `js/engine.js:24`. Dò: lệnh sell 4193 / SL 4195,4, `beDone = true`, đóng `SL` giá mặc định ⇒ `price 4195,4, r −1, streak 1`; chuỗi `SL, SL, BE(−0,04)` ⇒ `slStreak 3`.
- **Sửa:** khi `op.beDone`: giá mặc định của "Chạm SL" = `t.entry`, nhãn "Chạm SL (đã ở hòa vốn)"; `closeTrade` ghi `t.exit.beStop = true` khi `kind === 'SL' && open.beDone`. `countTrades`: `isSL = (kind === 'SL' && !t.exit.beStop) || (kind !== 'BE' && !t.exit.beStop && r < 0)` — "Về hòa vốn" đã chỉ chọn được sau `beDone` (R4) nên tin được `kind`. Thêm test cho cả hai ca.

---

## B. Mã

### 4. [MÃ] "Tôi vẫn vào" lúc TẮT MÁY chỉ ghi `OFF_RULE_BREAKS`, mất mã luật thật của kèo
- **Bằng chứng:** `js/engine.js:210` (`reasons = c.offs`), `js/journal.js:152`. Dò: đêm đã 2 phá luật, kèo A có V ⇒ `ruleCodes ['OFF_RULE_BREAKS']`, dòng ⚠ "phạm mục 7" — thiếu "4.1". Cuối tuần không đếm được lệnh phá luật nào thật sự vi phạm 4.x.
- **Sửa:** engine trả thêm `ruleReasons: c.reasons.slice()`; `createTrade` khi `ruleBreak`: `codes = offs ∪ ruleReasons`, nếu rỗng thì `missing`.

### 5. [MÃ] Nhập JSON gộp lệnh rồi sắp theo chuỗi "HH:MM" ⇒ lệnh sau nửa đêm nhảy lên đầu, chuỗi SL tính sai
- **Bằng chứng:** `js/store.js:50`. Dò: 21:00 SL, 23:50 SL, 00:20 TP (thứ tự thật, chuỗi 0) ⇒ sau gộp `00:20 TP, 21:00 SL, 23:50 SL`, `slStreak 2`.
- **Sửa:** sắp theo `time.baseMinute(t.time)` (00:00–05:59 cộng 1440), hoặc thêm `createdAt` (ms) lúc `createTrade` và sắp theo đó.

---

## C. Chữ

### 6. [CHỮ] Mốc giờ in cứng trong chữ, sai từ 01/11/2026 (còn 12 ngày)
- **Bằng chứng:** `js/content.js:77` `DIS_EARLY_BREAK` "18:00–19:20"; `:137` `halfText.BEFORE_2030` "trước 20:30"; `:141` `WARN_BEFORE_2030`; `:234` `qd['QĐ-19']`; `:298` `t1CardHelp` "Sau 19:20"; `:300` `editAfterLock`; `:402` từ điển "mở ảo". Engine đã dịch mốc +1h (QĐ-7) nhưng chữ vẫn nói 20:30 / 19:20. R19 mới sửa `t0WinNote`.
- **Sửa:** đổi các chuỗi sang `{nyse}`, `{comex}`, `{early}` và điền bằng `time.fmtMin(time.markMin(R.MARKS.nyse|comex, key, useDst))` ở chỗ gọi (`ui.codeText` nhận thêm biến, `C.warnText` đi qua `T`-kiểu thay thế). Thêm test chữ ngày 02/11/2026 có "21:30".

### 7. [CHỮ] Câu hỏi tầng 1 đánh số Q1…Q8, lệch HT 2.1 (Q1–Q6) và trùng chữ "Tám câu" với checklist HT 9
- **Mô tả:** HT 2.1 "Sáu câu hỏi", Q4 = HVN/LVN, Q5 = đóng so VA, Q6 = Âu dựng range. App ghi "Q4 · Đỉnh hôm qua", "Q7 · Đóng hôm qua so với VA", "Q8 · Âu đã dựng range chưa", tiêu đề "Tám câu hỏi"; nút "?" lại mở `#sau-cau-hoi` của HT với số khác. "Tám câu" là tên checklist HT 9 (tám chấm của thanh phán quyết) ⇒ dễ lẫn.
- **Bằng chứng:** `js/content.js:287` (`t1Title2`), `:299` (`need_q5` "Q7", `need_q6` "Q8"), `:370` (`qPrefix`), `js/ui/tier012.js:95`.
- **Sửa:** đánh số theo plan 1b: Q1, Q1′, Q2a, Q2b, Q3, Q4, Q5, Q6 (thêm trường `num` trong `questions`); tiêu đề "1b · Sáu câu hỏi trên chart A"; `need_q5` = "Q5 (đóng hôm qua so với VA)", `need_q6` = "Q6 (Âu dựng range)". Sửa regex `^Q8 · ` trong `e2e/vong2.spec.mjs`.

### 8. [CHỮ] Từ điển: 2/22 mục chưa đúng ý HT (20 mục còn lại khớp)
- "mở ảo" (`content.js:402`): "Vì vậy trước 20:30 chỉ giảm cỡ còn ½" là QĐ-19 của công cụ; HT 3.2 viết "Trước 20:30 chỉ fade cạnh, cỡ nhỏ". Từ điển tự nhận "lấy từ trang Hệ thống Đêm Vàng" nên đây là gán luật cho HT. Sửa: "…HT: trước 20:30 chỉ fade cạnh, cỡ nhỏ. Công cụ: không tắt kịch bản, chỉ giảm ½ (QĐ-19, chưa đo)."
- "hạng vùng" (`content.js:391`): "hạng 2 … dùng cỡ lệnh nhỏ hơn" — theo QĐ-14 chỉ áp cho hấp thụ (B); phá hồi, trap ở hạng 2 vẫn cỡ chuẩn. Sửa: "…hạng 2 thì hấp thụ đi cỡ ½."

### 9. [CHỮ] Chữ `NO_SIZE_ZERO` khuyên "giảm SL" — trái HT 6
- **Bằng chứng:** `js/content.js:101` "…giảm SL hoặc bỏ kèo." HT 6: SL theo cấu trúc + sàn nhiễu, "không thu nhỏ SL cho đẹp R"; thu SL lại sẽ phạm `NO_SL_FLOOR`.
- **Sửa:** "Vốn × rủi ro chưa đủ 1 hợp đồng MGC với SL này — bỏ kèo (hoặc tăng vốn ở tầng 5)." (đi cùng mục 1).

### 10. [CHỮ] QĐ-19 vẫn chưa có trong "?" của cảnh báo trước 20:30 (R17 một phần)
- **Bằng chứng:** `js/ui/tier012.js:291`, `js/ui/status.js:36`, `js/ui/tier3.js:256` chỉ in chữ, không có `helpBtn`. Plan §0 bắt buộc QĐ hiện trong "?" kèm "quyết định của công cụ, chưa đo".
- **Sửa:** banner tầng 2 và chip `halfNote` ở tầng 3 thêm `ui.helpBtn({ text: …, ref: 'thoi-gian' }, C.qd['QĐ-19'] + ' (' + C.unmeasured + ')')`.

---

## D. UX

### 11. [UX] 20:20–20:30 thanh trạng thái nói hai điều ngược nhau: "Cú phá đáng tin" cạnh "Trước 20:30 vàng hay mở ảo (cú phá chưa đáng tin)"
- **Bằng chứng:** ảnh `d1366-2024-t3-bam-entry.png` (20:24: "Giờ tin · Cú phá đáng tin" và chip vàng "cú phá chưa đáng tin"). `js/time.js:152` (dải "đáng tin" từ 20:20) vs `engine.js:224` (cảnh báo tới 20:30).
- **Sửa:** khi có `WARN_BEFORE_2030` thì không in nhãn dải "Cú phá đáng tin" (hoặc nhãn "Chuyển tiếp 20:20–20:30"). Không đổi luật.

### 12. [UX] Bước Bấm vẫn chưa vừa một màn 1366×768 (R11 một phần)
- **Bằng chứng:** đo bằng Playwright ở bước Bấm đã điền đủ: `scrollHeight` 796 / 768 lúc 21:30; 854 / 768 lúc 20:24 vì thanh trạng thái xuống 2 dòng (80 px) do chip "Trước 20:30 vàng hay mở ảo…" dài. B5 thấy được, nhưng hộp tính + "Cỡ lệnh MGC" nằm sau thanh phán quyết (ảnh `d1366-t3-bam-entry.png`, `d1366-2024-t3-bam-entry.png`). Lúc chưa điền: 873 / 946.
- **Sửa:** rút chip cảnh báo trên thanh trạng thái thành "trước 20:30 · cỡ ½" (chữ dài để trong "?"); ở bước Bấm khi ENTRY ẩn hộp tính vì thanh phán quyết đã có SL, R:R, số hợp đồng; thêm e2e đo `scrollHeight ≤ innerHeight` ở 21:30 và 20:24.

### 13. [UX] Vừa phá / Trend thin chưa có hướng (hoặc chưa có cạnh) mà vẫn công nhận được ⇒ A, D kẹt CHỜ "Chọn hướng" / "Chọn vùng" trỏ vào ô tự điền
- **Bằng chứng:** `js/rules.js:145-155` (`broken` chỉ cần `step1 && step2`); dò: A khi `thin`, `thinDir = null` ⇒ `WAIT [WAIT_SIDE…]`; bấm vào mục thiếu thì nhảy tới C2 chỉ hiện "chưa có hướng (tự điền)". Bước 1 cũng tick được khi chưa chọn cạnh ⇒ `NO_PENDING_ACCEPT` không biết cạnh nào.
- **Sửa:** ở tầng 2 khóa "Bước 1" cho tới khi đã chọn hướng phá và cạnh vừa phá (giống bước 2 chờ bước 1); với A/D, mã CHỜ riêng `WAIT_REGIME_DIR` "Chọn hướng ở tầng 2" có nút về tầng 2.

### 14. [UX] Điện thoại 360 px: nút "Thẻ phiên" đè lên chip đếm ngược cửa sổ cấm
- **Bằng chứng:** ảnh `p360-t3-bam-entry.png`, `p360-t4.png`: chip chỉ còn "Hết cửa sổ c…". Đây là chip quan trọng nhất của thanh trên.
- **Sửa:** ở ≤ 900 px cho `.statusbar` `padding-right` bằng bề rộng `#cardtoggle` (khoảng 96 px), hoặc đưa nút "Thẻ phiên" xuống thanh tầng.

### 15. [UX] Tầng 4: ô "Giá hiện tại" mất khi tải lại (USER-TEST mục 3 phần còn lại)
- **Bằng chứng:** `js/ui/tier45.js:61` (`app.ui.curPrice` chỉ ở bộ nhớ).
- **Sửa:** lưu `open.curPrice` vào `night.open` (bằng `app.update(..., {keep:true})`), đọc lại khi vẽ.

---

## E. Test

### 16. [TEST] Test chưa bắt được 3 lỗi luật ở trên; còn các lỗ cũ của R34
- Toàn bộ unit test dùng vốn 20.000 $ (`tests/helpers.js:11`) trong khi Phụ lục A và app dùng 2.000 $ ⇒ không thấy mục 1. Thêm bộ fixture chạy đúng `settings` Phụ lục A.
- `tests/fixtures.test.js:89-91` khóa hành vi trái QĐ-21 (mục 1).
- Thiếu: C `pending` ở vùng ngoài cạnh (mục 2); "Chạm SL" sau be và "Về hòa" trượt giá (mục 3); TẮT MÁY + "Tôi vẫn vào" có mã luật thật (mục 4); gộp JSON qua nửa đêm (mục 5); chữ ngày mùa đông (mục 6).
- R34 còn mở: bảng bật kịch bản `pending` × bias KHÔNG / CHỜ, `thin` × CHỜ; `tests/verdict.test.js:155` (QĐ-4) vẫn `includes(A) || includes(B)` — đổi `deepEqual` đúng danh sách để khóa thứ tự luật.
- E2E: không có ca trước 20:30 với cài đặt mặc định (sẽ lộ mục 1), không có ca lệnh qua đêm bằng UI, không có ca dời be rồi "Chạm SL".

---

## Kiểm lại từng mục REVIEW-1 ghi "đã sửa"

Đúng và không hồi quy (dò engine hoặc đi UI): R1 (broken → thin → broken, chui lại → phá lần 2 `nth 2`, đều phải công nhận lại), R2 (e2e + tay), R3, R4 (đúng mục tiêu; có tác dụng phụ ở mục 3), R5 (thứ Năm / chưa qua tầng 0 / ngày tin / tắt tay có `offAt`), R6, R7, R9, R12 (360 px: hai thanh 43 + 151 px = 26 %), R13, R14, R15, R16, R18, R20, R21, R22, R23, R24, R25, R26, R27, R29, R30, R31. Sau ghi lệnh tải lại về đúng tầng 4; đóng lệnh tải lại về tầng 3 "Kèo mới" (0 kịch bản chọn, CHỜ). ENTRY in "· 1 hợp đồng". Từ điển 22 mục mở từ thanh trạng thái, cuộn trong hộp ở cả hai cỡ màn hình. Lệnh qua đêm: đêm mới khóa tầng 3 (`LOCKED`, `nightKey` của lệnh = đêm cũ).
- **R8:** đúng cho B nhưng hồi quy cho C ⇒ mục 2.
- **R10:** bị QĐ-21 thay ⇒ mục 1.
- **R11, R17, R34:** "một phần" — còn quan trọng: R11 (mục 12, mức nhẹ), R17 (mục 10, plan bắt buộc), R34 (mục 16).

## 13 chỗ tự chọn ở IMPL-2

| # | Kết luận |
|---|---|
| 1 Vốn test 20.000 $, mặc định 2.000 $ | **Trái QĐ-21** ⇒ phải đổi code (mục 1) và test (mục 16) |
| 2 19:30 tự bật cả ngày có tin | Rộng hơn plan một chút (plan: thứ Năm + chưa qua tầng 0), hợp HT 7 "đánh tin 19:30: 0"; nên ghi vào plan |
| 3 `NO_BIAS_NONE_EDGE` | QĐ-21 đã công nhận |
| 4 R:R / TP / cỡ chỉ xét khi số liệu hợp lệ | Hợp QĐ-20 (SL sai phía đã có `NO_SL_SIDE`) |
| 5 `NO_BUBBLE_AGAINST` cần hướng | Không trái |
| 6 `WAIT_C6_BIG`, bỏ `NO_SL_FLOOR` khi C6 > 20 | Không trái |
| 7 "Về hòa" khóa tới khi dời be | Không trái, nhưng gây mục 3 |
| 8 Vùng có lệnh thật không xóa được | Không trái |
| 9–13 | Không trái |

---

## Kết luận
1. Vòng 2 sửa đúng phần lớn REVIEW-1 (chỉ R8 hồi quy; R10 bị QĐ-21 thay; R11, R17, R34 còn một phần), test/e2e/lint xanh thật; không còn lỗi chặn đường đi.
2. Còn 3 lỗi luật: cỡ ½ ra 0 hợp đồng chặn mọi C và mọi kèo trước 20:30 ở cài đặt mặc định (trái QĐ-21, chặn cả ca ĐÚNG 6/10); C lọt ở vùng ngoài cạnh khi chờ công nhận (hồi quy R8); "Chạm SL" sau be ghi −1R và cộng chuỗi SL.
3. Test vẫn chạy với vốn 20.000 $ nên không thấy mục 1; cần bộ fixture đúng Phụ lục A và các test ở mục 16.

| Mức | Số mục | Mục |
|---|---|---|
| SAI LUẬT | 3 | 1, 2, 3 |
| CHẶN ĐƯỜNG ĐI | 0 | — |
| MÃ | 2 | 4, 5 |
| CHỮ | 5 | 6, 7, 8, 9, 10 |
| UX | 5 | 11, 12, 13, 14, 15 |
| TEST | 1 | 16 |
| **Tổng** | **16** | |

**Đã đủ để người dùng thật dùng đêm nay chưa?** **Chưa, nhưng gần.** Mục 1–3 là sửa nhỏ (vài dòng mỗi mục + test), nên sửa trước phiên tối. Nếu buộc dùng bản 1.0.2 ngay đêm nay: (a) ở tầng 5 tăng vốn sao cho cỡ ½ ≥ 1 hợp đồng, và tự nhớ số hợp đồng thật vì số hiển thị sẽ sai; (b) sau khi dời be, đóng bằng "Về hòa vốn", không dùng "Chạm SL"; (c) không vào C khi chế độ hiệu lực là "chờ công nhận" mà vùng không phải cạnh. Mục 6 phải xong trước 01/11/2026.

## Ghi chú
- Ảnh: `docs/review-shots-2/d1366-{t0,t1,t2,t3-canh,t3-bam-empty,t3-bam-entry,enter-dialog,t4,t4-reload,t5,glossary}.png`, `p360-*.png` (cùng bộ), `d1366-2024-*.png` (20:24, cài đặt mặc định).
- Kịch bản dò (không đưa vào repo): `C:\Users\anhla\AppData\Local\Temp\claude\c--Users-anhla-OneDrive-Documents-footprint-tpo\bcfa2f0c-e665-455f-9235-2f428bc8a04f\scratchpad\r2\probe2.js`, `...\r2\probe3.js`, `...\r2\walk2.mjs`.
