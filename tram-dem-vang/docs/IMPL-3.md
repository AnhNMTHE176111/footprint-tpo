# IMPL-3 — Trạm Đêm Vàng, vòng 3 (sửa theo REVIEW-2 và USER-TEST-2)

Ngày: 2026-10-20 · Nguồn quyết định: plan bản 4 + QĐ-20, QĐ-21 · Phiên bản triển khai: **1.0.3**

## Kết quả chạy THẬT (Node 22, Playwright chromium, máy Windows 11)

`npm test`
```
# tests 209
# suites 0
# pass 209
# fail 0
# cancelled 0
# skipped 0
```
Theo file: `bias-enable` 43 · `verdict` 56 · `breaker-tier4` 16 · `time-card` 27 · `journal-store` 16 · `fixtures` 9 · `review1-fixes` 19 · **`review2-fixes` 23 (mới)**.
Toàn bộ test chạy với vốn mặc định **2000 $ · 2 %** (`tests/helpers.js` đổi từ 20000). Ca 20000 $ còn lại chỉ để kiểm số học (A4a ⇒ 8 hợp đồng).

`npm run e2e`
```
# tests 27
# suites 0
# pass 27
# fail 0
# cancelled 0
# skipped 0
```
Theo file: `app.spec` 11 · `vong2.spec` 4 · **`vong3.spec` 12 (mới)**. Hai ca `v3-1`, `v3-2` đã thử tắt phần sửa (hoãn vẽ lại) thì **đỏ**, bật lại thì xanh: test thật sự bắt được lỗi click bị nuốt.

`npm run lint:vi`: `802 chuỗi, 406 khóa ui, 122 từ được phép — Kết quả: 0 lỗi` (4 khóa ui chưa dùng: `cardEdits`, `boNeed`, `sideNone`, `unitGiaShort`).

Ảnh chụp lại (giờ 20:24, vốn mặc định): `docs/shots/tang1-vung.png`, `tang3-entry.png`, `dien-thoai-360.png`.

## Phát hiện thêm khi sửa

**Cảnh báo "kế hoạch ngược bias" chưa bao giờ chạy** (USER-TEST-2 mục b7 "Chốt im lặng"): hai biểu thức chính quy trong `planConflict` bị ghi nhầm thành ký tự lùi (mã 8) thay cho `\b`, nên không bao giờ khớp "buy" / "sell". Lỗi có từ vòng 1, test không bắt vì hàm nằm trong UI. Đã chuyển hàm sang `journal.js` (`J.planConflict`), viết lại bằng `\b`, thêm unit test, và quét toàn bộ mã nguồn: không còn ký tự điều khiển nào khác.

## Bảng mục REVIEW-2 → trạng thái

| Mục | Trạng thái | Ghi chú |
|---|---|---|
| 1 SAI LUẬT · cỡ lệnh QĐ-21 | đã sửa | `sizeFor`: cỡ chuẩn ≥ 1 mà ½ < 1 ⇒ 1 hợp đồng, `sizeMinOne`; `NO_SIZE_ZERO` chỉ khi cỡ chuẩn < 1; thanh ENTRY in "cỡ ½ không chia được — 1 hợp đồng (tối thiểu)"; hộp hỏi vốn lần đầu (`settings.sizeAsked`); chữ `NO_SIZE_ZERO` nói SL tối đa và có nút "Đổi vốn". Test: A1 20:24 ⇒ ENTRY 1; vốn 1000 $ ⇒ `NO_SIZE_ZERO`; e2e `v3-3`, `v3-4` |
| 2 SAI LUẬT · C khi chờ công nhận | đã sửa | mã mới `NO_C_NOT_EDGE` (htRef `5·C`, ô c3) xét ở mọi chế độ còn bật C; `NO_MID_RANGE` chỉ còn cho B. C chỉ ở `edge` / `edgeOuter`. Ô "Hướng" của C luôn chỉ đường: chưa chọn vùng ⇒ nhắc chọn vùng; vùng chưa có phía ⇒ nút "Về tầng 1"; ô phía của cạnh range / single print không còn bỏ chọn được |
| 3 SAI LUẬT · chạm SL sau be | đã sửa | `closeTrade`: SL sau be ⇒ giá mặc định = giá vào, `exit.beStop`, R = 0; `engine.isSLTrade`: cộng chuỗi khi (kind SL chưa be) hoặc R ≤ −0,5; "Về hòa" R trong [−0,2; +0,2] không cộng. Nhãn nút "Chạm SL (đã ở hòa vốn)". Test + e2e `v3-7` |
| 4 MÃ · "Tôi vẫn vào" khi TẮT MÁY | đã sửa | engine trả `ruleReasons`; `J.forceCodes` gộp `reasons ∪ ruleReasons`, rỗng thì mã CHỜ; hộp xác nhận cũng liệt kê đủ |
| 5 MÃ · nhập JSON qua nửa đêm | đã sửa | sắp theo `time.baseMinute` (ổn định theo thứ tự cũ) |
| 6 CHỮ · giờ in cứng | đã sửa | `{comex}` `{nyse}` `{real1}` `{real2}` `{fomcFlat}` điền từ `time.textVars` (`C.fill`, `ui.fillTimes`): 7 chỗ + "đóng sạch trước 00:45". Test ngày 02/11/2026 ra 21:30 / 20:20 |
| 7 CHỮ · Q1…Q8 | đã sửa | Q1, Q1′, Q2a, Q2b, Q3, Q4, Q5, Q6; tiêu đề "Sáu câu hỏi"; `need_q5`, `need_q6` |
| 8 CHỮ · Từ điển 2 mục | đã sửa | "mở ảo" tách "Hệ thống:" / "Công cụ: … (QĐ-19, quyết định của công cụ, chưa đo)"; "hạng vùng" chỉ hấp thụ đi cỡ ½ |
| 9 CHỮ · `NO_SIZE_ZERO` khuyên giảm SL | đã sửa | bỏ "giảm SL"; "bỏ kèo, hoặc tăng vốn" |
| 10 CHỮ · QĐ-19 trong "?" | đã sửa | "?" trên thanh trạng thái, banner tầng 2, chip cỡ ½ ở thanh phán quyết |
| 11 UX · hai điều ngược nhau 20:20–20:30 | đã sửa | còn cảnh báo thì không in nhãn "Cú phá đáng tin" |
| 12 UX · bước Bấm vừa một màn | đã sửa | chip rút thành "trước 20:30 · cỡ ½"; ẩn hộp tính khi ENTRY; đệm gọn; chữ ENTRY nhỏ lại. e2e `v3-9` đo `scrollHeight ≤ innerHeight` ở 21:30 và 20:24 (sau khi `--vbar-h` đã cập nhật) |
| 13 UX · A, D kẹt "Chọn hướng" | đã sửa | mã CHỜ `WAIT_REGIME_DIR` "Chọn hướng ở tầng 2" (bấm vào ⇒ tầng 2; ô c2 có nút "Về tầng 2"); bước 1 khóa tới khi chọn hướng phá và cạnh; bước 2 bị khóa thật (trước đây bấm vẫn lọt) |
| 14 UX · nút Thẻ phiên đè chip | đã sửa | ≤ 900 px chừa 112 px bên phải; ≤ 600 px chip tự xuống dòng thay vì cuộn. e2e `v3-11` |
| 15 UX · mất "Giá hiện tại" | đã sửa | lưu vào `open.curPrice`; e2e `v3-7` tải lại còn giá |
| 16 TEST | đã sửa | vốn 2000 $; test A4a đổi theo QĐ-21; bảng bật kịch bản pending / thin × bias KHÔNG / CHỜ; QĐ-4 `deepEqual`; e2e: trước 20:30 cài đặt mặc định, lệnh qua đêm bằng UI, dời be rồi chạm SL |

## Bảng mục USER-TEST-2 (10 điều cần sửa tiếp) → trạng thái

| # | Trạng thái | Ghi chú |
|---|---|---|
| 1 Click đầu sau khi gõ số bị nuốt | đã sửa | Nguyên nhân: mousedown làm ô mất focus ⇒ `change` ⇒ ghi state ⇒ vẽ lại cả tầng, nút bị thay trước khi nhả chuột. Sửa: `app.hold` ghi state ngay nhưng hoãn VẼ LẠI do `change` gây ra tới sau cú bấm (cú bấm tự vẽ lại và gộp phần hoãn), hoặc tới lúc ô kế nhận focus (Tab); ô đang gõ được khôi phục focus và vùng chọn sau mỗi lần vẽ. e2e `v3-1`, `v3-2` |
| 2 Vốn mặc định 2000 $ chặn kèo | đã sửa | QĐ-21 + hộp hỏi vốn + SL tối đa + nút "Đổi vốn"; câu "= 40 $" nay ghi rõ rủi ro chuẩn, rồi "cỡ ½ nên chỉ rủi ro 20 $". "Tôi vẫn vào" khi cỡ chuẩn 0 vẫn tạo lệnh 0 hợp đồng (ghi nhận phá luật, giữ nguyên) |
| 3 Từ điển | đã sửa | mở ở đầu (ô tìm nhận focus), xếp chữ cái, ô tìm không dấu, "?" mở đúng mục: cuộn + tô sáng. e2e `v3-5` |
| 4 Mục Từ điển còn yếu | đã sửa | mồi, trap, bong bóng, DMA viết lại theo trang hệ thống; thêm R và hình dạng profile (D, P, b, B, thin, chữ nhật) lấy từ Q1; "?" của Q1 có đủ nội dung |
| 5 Số thao tác | **một phần** | đã: "Sao chép vùng từ đêm {ngày}" (VWAP tuần, HVN 3 tuần, Q1′, cùng tuần); cảnh báo kế hoạch ngược bias hiện ngay khi gõ, sát nút chốt, in đậm. Chưa: Q mặc định "Không rõ", gõ nhanh "VWAP 4181", bỏ bước "Sang tầng 3" (ngoài danh sách chủ plan giao) |
| 6 Kế hoạch ngược bias im lặng | đã sửa | gốc là regex hỏng (xem "Phát hiện thêm") |
| 7 Thanh trên dày | một phần | đã: banner / chip cỡ ½ rút ngắn, điện thoại không bị đè. Chưa: bớt chip |
| 8 "?" quá nén, đè đáp án | chưa | chỉ làm "?" của Q1 đủ chữ. Chưa sửa vị trí pop của Q3 và nút 28 px |
| 9 Bấm kịch bản mờ không phản hồi | một phần | đã: HVN ở C nay báo `NO_C_NOT_EDGE` (đúng chuyện) thay vì "giữa range". Chưa: bong bóng khi bấm D mờ, "Giờ phá" tự điền |
| 10 Chữ viết tắt còn sót | chưa | "bb giữ · Δ", "Chuỗi đêm 0 phá luật", chip đếm: ngoài danh sách |

## Chỗ tự chọn (chỗ mơ hồ chọn đơn giản nhất)

1. Nút "Để sau" của hộp vốn, hoặc đóng hộp bằng Esc, cũng đặt `sizeAsked = true` (không hỏi lại mỗi lần mở).
2. "SL tối đa" = rủi ro cỡ chuẩn ÷ 10 $ (1 giá = 10 $ một hợp đồng MGC), làm tròn xuống 0,1: vốn 2000 $ · 2 % ⇒ 4,0 giá; 1000 $ ⇒ 2,0 giá.
3. "R trong [−0,2; +0,2] coi là hòa" hiểu theo đơn vị R (không phải giá). R trong (−0,5; −0,2) không cộng chuỗi nhưng cũng cắt chuỗi (không phải SL).
4. "Chạm SL" sau be: chỉ giá MẶC ĐỊNH đổi thành giá vào; nếu người dùng gõ giá khác thì R tính theo giá đó (≤ −0,5R vẫn cộng chuỗi).
5. `NO_C_NOT_EDGE` xét cả khi C ngược bias (hai mã cùng hiện).
6. `WAIT_SIDE` chỉ còn cho B và C; A, D dùng `WAIT_REGIME_DIR`.
7. "Sao chép từ đêm trước": chỉ VWAP tuần, HVN 3 tuần và Q1′; chỉ lấy đêm gần nhất CÙNG TUẦN (thứ Hai là đầu tuần) đã chốt thẻ; không đè vùng cùng loại đã có; tôn trọng trần 5 vùng. Ghi vết như mọi lần sửa thẻ sau 19:20.
8. Ví dụ số trong Từ điển (4210 / 4208, 4200 → 4194 → 4197, 4193 / 4195,4) là minh họa của công cụ, không phải ca thật. DMA: trang hệ thống không ghi tên đầy đủ nên Từ điển nói thẳng như vậy; hình dạng B: trang chưa mô tả riêng nên ghi như vậy.
9. Hộp tính cỡ lệnh bị ẩn khi ENTRY (thanh phán quyết đã đủ SL, R:R, số hợp đồng); khi KHÔNG VÀO vẫn có.
10. Bước 2 công nhận cú phá trước đây bấm vẫn lọt dù bị khóa (thiếu `onDisabled`); nay chặn thật.
11. Cỡ chữ dòng ENTRY giảm (34 → 30 px, 20 → 17 px) để bước Bấm vừa màn 1366×768; không đổi trên điện thoại.
12. Hoãn vẽ lại chỉ áp cho vẽ lại do `change` gây ra; cú bấm vào nút vẫn vẽ ngay (không trễ).
