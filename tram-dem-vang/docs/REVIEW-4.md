# REVIEW-4 — Trạm Đêm Vàng, vòng 4 (nghiệm thu)

Ngày 2026-10-20 · Người review: Claude Opus · Đối chiếu: plan (QĐ-1…QĐ-21), trang HT (bản text), mã ở commit `a40885f` (bản 1.0.4; Pages trả 200, `APP_VERSION = '1.0.4'`).

**Số chạy lại thật trên máy này:** `npm test` 220/220 xanh · `npm run e2e` 43/43 xanh · `npm run lint:vi` 0 lỗi (7 khóa ui không dùng: `cardEdits`, `boNeed`, `sideNone`, `halfNote`, `unitGiaShort`, `halfNoteMin`, `copyShape`).
**Dò thêm** (không đưa vào repo), thư mục `C:\Users\anhla\AppData\Local\Temp\claude\c--Users-anhla-OneDrive-Documents-footprint-tpo\bcfa2f0c-e665-455f-9235-2f428bc8a04f\scratchpad\r4\`: `p1.js` (chuỗi SL), `p3.js` (mốc giờ 23/10 → 03/11), `p4.js` (giờ phá), `probe.mjs`, `probe2.mjs` (Playwright, file://, chuột thật giữ 90 ms; 360×740, 390×844, 1366×768; mùa đông 03/11 21:00). Console không lỗi ở mọi lượt.

Chỉ ghi chỗ **chưa đạt**. Nặng trước.

---

## A. Chưa đạt

### 1. [UX · hạn 02/11/2026] Dòng nhắc "đổi neo session TPO / SessionZones 19:20 → 20:20" chỉ hiện ở đêm **Chủ nhật** — đêm không có phiên, người dùng không mở công cụ
- **Mô tả:** `time.notices` chỉ đẩy `US_SWITCH` khi đêm hôm trước còn giờ hè. Mỹ đổi giờ Chủ nhật 01/11, nên dòng chỉ hiện ở `nightKey` 2026-11-01 (Chủ nhật VN, chợ đóng). Đêm giao dịch đầu tiên là thứ Hai 02/11: chỉ có chip "Mỹ mùa đông +1h", và trên điện thoại chip này nằm trong khung "Trạng thái" đóng sẵn. Tương tự `LDN_SWITCH` chỉ ở 25/10 (Chủ nhật) và `US_SWITCH_BACK` ở 14/03/2027 (Chủ nhật). Đổi neo là việc tay trên chart; bỏ lỡ ⇒ IB lệch 1 giờ.
- **Bằng chứng:** `js/time.js` hàm `notices` (so với `addDays(key, -1)`). `p3.js`: 01/11 (dow 0) ⇒ `[US_WINTER, US_SWITCH]`; 02/11 (dow 1) ⇒ chỉ `[US_WINTER]`; 25/10 (dow 0) ⇒ `LDN_SWITCH`. `probe2.mjs` 360 và 390 px, 03/11: thanh trên chỉ "21:00 VN · BIAS BUY · Trạng thái ▾".
- **Sửa:** so với **đêm giao dịch trước** (bỏ thứ Bảy, Chủ nhật): thứ Hai 02/11 so với thứ Sáu 30/10 ⇒ hiện `US_SWITCH`; hoặc hiện từ ngày đổi tới hết đêm giao dịch đầu tiên. Thêm unit test 02/11/2026 và 15/03/2027. README (mục "Đổi giờ mùa đông") sửa "đúng ngày đổi giờ" thành "đêm giao dịch đầu tiên sau khi đổi giờ".

### 2. [CHỮ · QĐ] Ngưỡng "R ≤ −0,2 là SL" là quyết định của công cụ nhưng chưa ghi vào plan và không có trong "?"
- **Mô tả:** HT chỉ ghi "SL liên tiếp: 3 ⇒ tắt máy". Định nghĩa một ngưỡng (đóng tay ở −0,2R cũng cộng chuỗi; −0,19R là hòa, reset) do chủ plan chốt ở vòng 4, nhưng QĐ-10 trong plan vẫn chỉ ghi "TP và hòa reset". Plan (dòng 25) yêu cầu quyết định không có trong HT phải hiện trong "?" kèm "quyết định của công cụ, chưa đo". Chip "SL liên tiếp N trên 3" chỉ nói "Số SL liên tiếp ở cuối sổ"; người dùng đóng tay ở −0,3R sẽ thấy chuỗi tăng mà không biết vì sao.
- **Bằng chứng:** `plans/CHECKLIST-DEM-VANG-plan.md:38` (không có ngưỡng); tìm "0,2" trong `js/content.js` không ra; `chipStreakTip` ở `js/content.js:273`. Mã thì đúng: `p1.js` ⇒ −0,45 / −0,2 / −0,2000001 cộng (chuỗi 3), −0,19 / −0,199 / +0,19 reset (0), đúng cho cả "Đóng tay", "Về hòa", "Chạm SL (đã ở hòa vốn)"; ba lệnh −0,45R ⇒ chuỗi 3 ⇒ TẮT MÁY.
- **Sửa:** thêm QĐ-22 vào plan ("Lệnh đóng có R ≤ −0,2 hoặc chạm SL chưa be là SL; R trong (−0,2; +0,2) là hòa; chưa đo"). Thêm vào `chipStreakTip` và "?" của `OFF_SL_STREAK`: "Lệnh đóng lỗ từ 0,2R trở lên tính là SL, kể cả đóng tay (quyết định của công cụ, chưa đo)."

### 3. [MÃ · đường hiếm] Sửa cạnh hoặc hướng **trước khi công nhận** vẫn ghi đè giờ phá đã gõ bằng giờ hiện tại ⇒ mất `DIS_EARLY_BREAK`
- **Mô tả:** `J.setBreakoutField` reset khi giá trị cũ khác null **hoặc** đã có bước 1, 2 (IMPL-4 tự chọn 1). Ca: phá xuống tại z2 lúc 19:00 (giờ phá giả, A phải tắt), người dùng chọn nhầm cạnh rồi sửa z2 → z3 trước khi công nhận ⇒ `at` thành 21:30 ⇒ công nhận xong thì A **bật**. Có thông báo và ô giờ phá hiện 21:30, nhưng đây là sửa chọn nhầm, không phải cú phá mới.
- **Bằng chứng:** `js/journal.js:174-175`. `p4.js`: `at 19:00` đã công nhận ⇒ A `DIS_EARLY_BREAK`; `setBreakoutField(edgeZoneId z3)` khi chưa công nhận ⇒ `at: "21:30"`; công nhận lại ⇒ A `null` (bật).
- **Sửa:** chỉ đặt `at = bây giờ` khi `bo.step1 || bo.step2` (đã công nhận, đúng là cú phá mới); chưa công nhận thì chỉ đổi trường, giữ `at`. Thêm unit test cho ca trên.

### 4. [CHỮ] Từ điển VA / VAH / VAL / POC là định nghĩa do công cụ thêm nhưng không ghi rõ, trong khi đầu Từ điển nói "Đầy đủ ở trang Hệ thống"
- **Bằng chứng:** `js/content.js:429`; IMPL-4 tự chọn 6 tự nhận "không có sẵn trên trang"; chú thích mã `js/content.js:403` hứa "chỗ là luật của công cụ thì ghi rõ".
- **Sửa:** thêm "(định nghĩa TPO chuẩn; trang Hệ thống không định nghĩa)" sau câu VAH / VAL / POC.

### 5. [CHỮ] Hai chữ cho cùng một khái niệm: "cỡ đầy" (`sizeMinOne`: "1 hợp đồng = cỡ đầy, rủi ro 23 $") và "cỡ đủ" (`sizeFull`, các chỗ khác)
- **Bằng chứng:** `js/content.js:386` và `:339`.
- **Sửa:** dùng một chữ "cỡ đủ" ở cả hai.

### 6. [MÃ · dọn] `WAIT_CAPITAL` khai báo hai lần liền nhau trong `RULES`; 7 khóa ui không dùng
- **Bằng chứng:** `js/rules.js`, hai khối giống hệt ngay trước `NO_SIZE_ZERO` (có cả trên bản Pages). Vô hại vì `push` bỏ trùng và `RULE_ORDER` lọc trùng, nhưng dễ nhầm khi thêm luật theo thứ tự (README "Thêm / sửa luật"). Lint báo 7 khóa ui không dùng.
- **Sửa:** xóa một khối; xóa các khóa không dùng.

### 7. [TÀI LIỆU] README đủ để tự dùng đường chính, nhưng thiếu bốn điều người dùng sẽ gặp
- **Thiếu:** (a) khi nào **TẮT MÁY** (2 lệnh phá luật, 3 SL liên tiếp theo định nghĩa ở mục 2; đêm mới về 0); (b) "Tôi vẫn vào (phá luật)" ghi cờ ⚠ và tính vào phá luật; (c) trả lời "Không" ở câu tỉnh táo ⇒ cả đêm **chỉ xem**, lệnh ghi là luyện mắt; (d) khi có bản mới, thông báo "Tải lại" hiện ở góc; xóa dữ liệu trình duyệt là mất sổ nếu chưa Tải JSON.
- **Sửa:** thêm một đoạn "Khi nào công cụ chặn" 4–5 dòng vào phần "Cách dùng".

---

## B. Kiểm lại 16 mục REVIEW-3 ghi "đã sửa"

Đúng, không hồi quy:
- **1 chuỗi SL** — mã đúng định nghĩa một ngưỡng (số ở mục 2); `R` làm tròn 2 chữ số trước khi so (giá thoát 4200,47 với SL 2,4 ra −0,2 ⇒ SL), nhất quán với số người dùng thấy. Thiếu ghi QĐ ⇒ mục 2.
- **2 đổi hướng / cạnh sau công nhận** — chuột thật ở tầng 2: công nhận phá xuống z2, bấm cạnh z3 ⇒ `step1/step2 = false`, thông báo "Đổi hướng hoặc cạnh là một cú phá mới…", chế độ hết "vừa phá". Đường trước khi công nhận ⇒ mục 3.
- **3 "?" và mục thu gọn** — chuột thật, sau khi gõ ở các ô chưa có trong e2e: Giá hiện tại (tầng 1) rồi bấm "?" ⇒ còn mở sau 400 ms; VWAP tuần rồi mở `<details>` ⇒ còn mở; "Move vừa rồi" của D rồi "?" C5 ⇒ còn mở, số được lưu.
- **4 thông báo nổi** — `pointer-events: none`; 1366: góc trên phải ngoài cột nút; 360: dưới thanh trên (y 66–111), không chặn bấm.
- **5** mã NO_* khi DIS (`shadow` → `ruleReasons`, `forceCodes` đủ), **6** vốn trống (ô Cài đặt trả số cũ, `WAIT_CAPITAL`), **7** `overridden` chỉ khi khác tự động, **8** "rủi ro thật" (chữ ở mục 5), **9** `NO_C_NOT_EDGE` đủ IB / High / Low hôm qua, **10** nút FOMC lấy `markMin` (01:00 / 02:00), **11** ghi "ví dụ minh họa" cho mồi và trap, **12** ENTRY 32 px, **13** mùa đông chỉ chip (03/11 21:00: 1366 thanh trên 40 px, thanh dưới 100 px; 360 / 390 thanh trên 42 px, không tràn ngang ở cả 6 tầng), **14** `scroll-padding-bottom`, **15** `snapFocus` giữ nút: đúng.
- **Phím tắt** — đang nhấn chuột ⇒ bỏ phím; đang ở ô ⇒ bỏ; hộp thoại mở ⇒ bỏ; `Enter` trên nút ⇒ nút tự xử lý (`js/main.js:326-330`; e2e `v4-5`).
- **16 test** — đủ các ca REVIEW-3 yêu cầu, có ca chuột thật.

Rà engine lần cuối: thứ tự `RULES` khớp bảng bật và QĐ-1…QĐ-21 (OFF → LOCK → cửa sổ → DIS theo bảng → HALF → NO/WAIT theo C1…B5 → R:R, TP, vốn, `NO_SIZE_ZERO` theo QĐ-20, QĐ-21); QĐ-17 (`paper` không cộng chuỗi, phá luật, lần tại vùng); mốc giờ 23/10 → 03/11 đúng (London đóng 22:30 → 23:30 từ 25/10; Mỹ từ 01/11: COMEX 20:20, tin 20:30, NYSE 21:30, cửa sổ 22:00, FOMC đóng sạch 01:45). Không thấy sai luật mới ngoài mục 3.

## C. 9 chỗ tự chọn ở IMPL-4

| # | Kết luận |
|---|---|
| 1 đổi hướng / cạnh chỉ xóa khi có giá trị cũ | **Một phần trái HT 3.2**: trước khi công nhận vẫn ghi đè giờ phá ⇒ mục 3 |
| 2 phím tắt khi vẽ lại hoãn, `Enter` trên nút | Không trái |
| 3 khôi phục "?" / `<details>` theo khung, chỉ số, tiêu đề | Không trái |
| 4 vị trí thông báo nổi | Không trái |
| 5 chip "Vùng này N trên 2" chỉ khi N ≥ 1 | Không trái (ô C3 vẫn có "lần thứ N") |
| 6 VA / VAH / VAL / POC tự thêm | Không trái nội dung, nhưng chưa ghi rõ nguồn ⇒ mục 4 |
| 7 chip điện thoại gom vào khung mở xuống | Không trái, nhưng làm mục 1 nặng hơn trên điện thoại |
| 8 SL sau be, giá thoát xấu R ≤ −0,2 là SL | Không trái (một định nghĩa); cần ghi QĐ ⇒ mục 2 |
| 9 chú giải dưới bảng Markdown | Không trái |

---

## Kết luận

| Mức | Số mục | Mục |
|---|---|---|
| SAI LUẬT | 0 | — |
| CHẶN ĐƯỜNG ĐI | 0 | — |
| MÃ | 2 | 3, 6 |
| UX | 1 | 1 |
| CHỮ / QĐ | 3 | 2, 4, 5 |
| TÀI LIỆU | 1 | 7 |
| **Tổng** | **7** | |

16 mục REVIEW-3 sửa đúng, không hồi quy; test 220/220, e2e 43/43, lint 0 lỗi chạy lại thật; file://, 360 / 390 / 1366 px và đêm mùa đông 03/11 21:00 không lỗi console, không tràn ngang.

**NGHIỆM THU: đạt có điều kiện.** Điều kiện:
1. Mục 1 (dòng đổi neo session hiện ở đêm giao dịch đầu tiên) phải xong **trước tối thứ Hai 02/11/2026**.
2. Mục 2 (ghi QĐ-22 vào plan và vào "?" của chuỗi SL).
3. Mục 3 (giữ giờ phá khi sửa cạnh / hướng trước khi công nhận) nên sửa cùng đợt; tới lúc đó người dùng tự giữ: sửa cạnh xong thì gõ lại giờ phá thật.

Mục 4–7 làm khi tiện, không chặn việc dùng.
