# IMPL-4 — Trạm Đêm Vàng, vòng 4 (sửa theo REVIEW-3 và USER-TEST-3)

Ngày: 2026-10-20 · Nguồn: REVIEW-3 (16 mục), USER-TEST-3, quyết định chủ plan trong đề bài · Phiên bản: **1.0.4**

## Kết quả chạy THẬT (Node 22, Playwright chromium, máy Windows 11)

`npm test`
```
# tests 220
# suites 0
# pass 220
# fail 0
# cancelled 0
# skipped 0
```
Theo file: `bias-enable` 43 · `verdict` 56 · `breaker-tier4` 16 · `time-card` 27 · `journal-store` 16 · `fixtures` 9 · `review1-fixes` 19 · `review2-fixes` 23 · **`review3-fixes` 11 (mới)**.

`npm run e2e`
```
# tests 43
# suites 0
# pass 43
# fail 0
# cancelled 0
# skipped 0
```
Theo file: `app.spec` 11 · `vong2.spec` 4 · `vong3.spec` 12 · **`vong4.spec` 16 (mới, dùng chuột thật: di chuột, nhấn, giữ 90 ms, thả)**.
Thử đảo ngược: tắt phần khôi phục khung "?" / mục thu gọn, trả `pointer-events: auto` cho thông báo nổi và bỏ chốt phím tắt thì `v4-1` … `v4-5` đỏ cả năm; bật lại thì xanh. Test bắt đúng lỗi.

`npm run lint:vi`: `825 chuỗi, 421 khóa ui, 125 từ được phép — Kết quả: 0 lỗi` (thêm 3 từ không dấu: minh, quanh, quay).

Ảnh chụp lại (`docs/shots/`): `tang1-vung.png`, `tang3-entry.png` (1366×768, 21:30), `dien-thoai-360.png`, và mới `dien-thoai-390.png` (20:24, ENTRY: thanh trên một hàng, thanh dưới 118 px), `dien-thoai-390-thanh-tren.png` (nút "Trạng thái" mở xuống).

## Bảng mục → trạng thái

### REVIEW-3

| Mục | Trạng thái | Ghi chú |
|---|---|---|
| 1 chuỗi SL | Đã sửa | Một định nghĩa: R ≤ −0,2 (hoặc kind SL chưa be) cộng; (−0,2; +0,2) hòa reset; R ≥ +0,2 reset. Bỏ ngưỡng −0,5. Test −0,45 / −0,3 / −0,2 / −0,19 / +0,19 / +0,2; ba lệnh −0,45R ⇒ TẮT MÁY |
| 2 đổi hướng / cạnh sau công nhận | Đã sửa | `J.setBreakoutField`: xóa bước 1, 2, giờ phá = bây giờ, ghi `regime.log`, có thông báo. Unit test + e2e `v4-6` |
| 3 "?" và mục thu gọn tự đóng | Đã sửa | `render()` chụp và khôi phục trạng thái mở (khung "?", `<details>`) ở status / main / verdict / card. e2e `v4-1`, `v4-2`, `v4-3` |
| 4 thông báo nổi chặn click | Đã sửa | `pointer-events: none` (trừ "Tải lại"), đặt ở góc. e2e `v4-4` |
| 5 "Tôi vẫn vào" mất mã NO_* | Đã sửa | Kịch bản bị DIS: luật NO vẫn xét, ghi vào `shadow`, trả trong `ruleReasons` (phán quyết không đổi). Test ⇒ `['DIS_NOT_BROKEN','NO_BACK','NO_V_PULLBACK']` |
| 6 xóa trắng ô Vốn | Đã sửa | Ô Cài đặt chỉ ghi khi > 0, trống thì trả số cũ + thông báo; engine thêm mã CHỜ `WAIT_CAPITAL` (bấm vào hoặc nút "Đổi vốn" mở hộp vốn). Unit `mục 6`, e2e `v4-8`, `v4-16` |
| 7 ghi đè bằng đúng bias tự động | Đã sửa | `overridden` chỉ khi khác bias tự động. Test |
| 8 chữ "rủi ro 20 $" | Đã sửa | Cỡ ½ không chia được ⇒ "1 hợp đồng = cỡ đầy, rủi ro 23 $" (số thật, `calc.realUsd`); hộp Cỡ lệnh nói "rủi ro thật … (hơn ½ kế hoạch)" |
| 9 chữ NO_C_NOT_EDGE | Đã sửa | Nêu VAH / VAL Âu, IB, cạnh range, High / Low hôm qua |
| 10 nút FOMC | Đã sửa | Giờ lấy từ `time.markMin` (01:00 hè, 02:00 đông). e2e `v4-9` |
| 11 ví dụ Từ điển | Đã sửa | Thêm "(ví dụ minh họa, không phải ca thật)" sau mồi và trap |
| 12 ENTRY ≥ 32 px | Đã sửa | 32 px mọi màn; vừa một màn 1366×768 nhờ thanh trên một hàng (chip 12 px) |
| 13 mùa đông | Đã sửa | Mỗi đêm chỉ chip "Mỹ mùa đông +1h" (+ "?" đủ câu); dòng dài chỉ ngày đổi giờ. e2e `v4-10`: giả lập 03/11 21:00, B vừa 768/768 |
| 14 thanh phán quyết che ô | Đã sửa | `scroll-padding-bottom` theo `--vbar-h`; ô "cần làm" bị thanh che thì cuộn lên trên thanh |
| 15 mất focus khi Tab sang nút | Đã sửa | `snapFocus` giữ cả nút (chỉ khi focus bằng bàn phím, `:focus-visible`) |
| 16 test | Đã bổ sung | Xem hai bảng test ở trên |

### USER-TEST-3 (mục chủ plan yêu cầu)

| Việc | Trạng thái | Ghi chú |
|---|---|---|
| (1) điện thoại 390 px | Đã sửa | Thanh trên **43 px** (giờ, bias, nút "Trạng thái"; chip còn lại mở xuống). Thanh dưới ENTRY **118 px** ở 20:24 (có hàng ghi chú) và 86 px ở 21:30. Nút "?" 40 px. e2e `v4-12` |
| (2) sao chép vùng | Đã sửa | Nút nằm đầu khối vùng; chép VWAP tuần thì điền luôn giá vào ô bias; thông báo chỉ nêu mục có thật ("hình 3 tuần" chỉ khi chép). e2e `v4-13` |
| (3) giờ phá | Đã sửa | Giữ tự điền giờ hiện tại; thêm chú thích và cảnh báo khi giờ phá trước 18:00 (ngoài giờ giao dịch). Engine: `DIS_EARLY_BREAK` chỉ áp trong 18:00 đến giờ COMEX theo mùa (đã đúng từ trước, nay có test 14:05, 17:59, 18:50, 19:19, 19:30; mùa đông 19:30, 20:19, 20:20). e2e `v4-14` |
| (4) cỡ ½ không chia được | Đã sửa | Xem mục 8 |
| (5) chữ tắt | Đã sửa | Chú giải một dòng dưới bảng Sổ và Markdown; chip "Phá luật 0 trên 2", "SL liên tiếp 0 trên 3", "Lệnh mở 0 trên 1" kèm chú thích khi rê chuột; "Số đêm liên tiếp không phá luật"; Canh → Bấm chỉ nhảy một lần cho mỗi kèo, có nút "Quay lại Canh"; Từ điển thêm VA / VAH / VAL / POC, phá giả, cửa sổ cấm. e2e `v4-7`, `v4-15` |

## Chỗ tự chọn (chỗ mơ hồ chọn cách đơn giản nhất)

1. **Đổi hướng / cạnh** chỉ xóa công nhận khi đã có giá trị cũ khác (hoặc đã có bước 1, 2); lần chọn đầu giữ giờ phá người dùng đã gõ. Không hỏi xác nhận, chỉ báo bằng thông báo.
2. **Phím tắt khi vẽ lại hoãn:** đang nhấn giữ chuột thì bỏ qua phím; hết nhấn mà còn phần vẽ hoãn thì vẽ nốt rồi mới xét phím. Phím `Enter` khi một nút đang focus thì nút tự xử lý, không chạy phím tắt "Vào lệnh".
3. **Khôi phục "?" và mục thu gọn** theo (khung chứa, chỉ số, 8 ký tự đầu tiêu đề), chỉ khi vẫn ở cùng tầng và cùng đêm. Bấm ra ngoài đóng "?" ở pha bắt (trước các nút) để cú vẽ lại do chính cú bấm đó không dựng lại khung cũ.
4. **Thông báo nổi** ở góc trên phải (máy tính, ngoài cột nút), dưới thanh trên (điện thoại).
5. **Chip "Vùng này N trên 2 lần"** chỉ hiện khi N ≥ 1 (hàng "Lần thứ N tại vùng" ở ô C3 vẫn có); nếu không, thanh trên mùa đông tràn sang hai hàng.
6. **Từ điển VA / VAH / VAL / POC:** trang Hệ thống chỉ nói VA trong / ngoài và "cạnh VA Âu"; câu "VAH là mép trên, VAL là mép dưới, POC là mức giá giao dịch nhiều nhất" là định nghĩa chuẩn của TPO do tôi thêm, không có sẵn trên trang. Phá giả và cửa sổ cấm lấy từ mục 3.2 và t0WinNote.
7. **Chip trên điện thoại** gom vào khung mở xuống, đóng khi bấm ra ngoài; thanh dưới hàng ghi chú một dòng, chữ dài bị cắt bằng "…".
8. **Chuỗi SL sau be:** lệnh "Chạm SL (đã ở hòa vốn)" vẫn là hòa; nếu người dùng gõ giá thoát xấu làm R ≤ −0,2 thì tính là SL (cùng một định nghĩa R).
9. **Sổ Markdown** có thêm một dòng chú giải ngay dưới bảng (mẫu HT 8 giữ nguyên, cập nhật test so chuỗi).

## Chưa sửa (và lý do)

- USER-TEST-3 (d) 7: bấm kịch bản đang tắt vẫn không chuyển tấm bên dưới sang kịch bản vừa bấm (không nằm trong danh sách chủ plan chốt).
- USER-TEST-3 (d) 10, phần "?" của Q3 và các câu còn lại thêm ví dụ giá hoặc hình: thiếu nội dung gốc từ trang Hệ thống; nút "?" 40 px thì đã làm.
- USER-TEST-3 DMA ghi tên đường cụ thể, hình dạng B "chưa mô tả riêng", mục "SL bị quét" trong Từ điển: trang Hệ thống không có chữ để chép.
- USER-TEST-3 (b) 1 (iv): mã vùng nhảy z1, z3, z4 sau khi sao chép (HVN 3 tuần nằm ở dòng VÙNG CẤM) là hành vi đúng, chỉ gây khó hiểu; chưa đổi.
- Đã làm thêm vài câu lạc đề nhỏ của USER-TEST-3 (d) 9: C ở HVN nói "không có phía", C ngược bias bị cấm thì không mời gõ lý do, ẩn câu "Sau khi vào không đổi SL…" sau khi đã be; ô tìm của Từ điển không đè tiêu đề mục nhảy tới và không bật bàn phím trên điện thoại.

## Deploy

`./deploy.sh` đã tăng `APP_VERSION` lên **1.0.4** (`js/rules.js` và `sw.js`) và đẩy lên https://anhnmthe176111.github.io/tram-dem-vang/ : trang chủ trả 200, `sw.js` và `js/rules.js` trên Pages đều ghi `APP_VERSION = '1.0.4'`. Sau khi tăng phiên bản đã chạy lại `npm test`: 220/220.
