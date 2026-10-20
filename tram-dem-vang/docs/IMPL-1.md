# IMPL-1 — Trạm Đêm Vàng, vòng 1 (implement + test)

Ngày: 2026-10-20 · Nguồn thiết kế: `plans/CHECKLIST-DEM-VANG-plan.md` bản 4 (chốt) · Không đổi luật nào trong plan.

## Kết quả chạy THẬT

Máy Windows 11, Node 22.12.0, Playwright 1.64.1 (chromium headless shell 156). Lệnh chạy trong `tram-dem-vang/`.

### `npm test` — 165 pass, 0 fail
```
# tests 165
# suites 0
# pass 165
# fail 0
# cancelled 0
# skipped 0
```
Theo file: `bias-enable` 43 · `verdict` 56 · `breaker-tier4` 16 · `time-card` 27 · `journal-store` 16 · `fixtures` 7.
- **Năm ca Phụ lục A** (A1, A2, A3a/b, A4a/b, A5 = 7 test) xanh, đúng verdict / reasons / half / dots / số liệu (rr 3,33 · tpSuggested 4185,8 · missing[0] = `WAIT_B2_MIXED`…).
- Ma trận bias 14 ca + 2 ca "chốt lại bias" / thiếu dữ liệu; bật kịch bản: 15 hàng bảng × (bias, chế độ, hướng phá) + `DIS_NO_EDGE`, `DIS_NO_CARD`, `DIS_LONGEST_BAR`, acceptance (đủ / thiếu bước 2 / phá 18:30 / 19:19 / 19:20), giờ 20:29–20:31 hè và 21:29–21:31 đông (chỉ đổi `half`).
- Phán quyết: từng mã `NO_*` / `WAIT_*` một ca, ca "B sell ngược bias BUY tại High hôm qua cờ `tail` ⇒ ENTRY 2R ½", lệnh mở (cả qua đêm) ⇒ khóa tầng 3, `missing` đúng thứ tự.
- Ngắt mạch (2 phá luật, "Tôi vẫn vào" ×2 đi qua `journal.createTrade`, 3 SL, hòa / TP reset, đêm mới, đóng tay "khác", `paper`, hủy limit), tầng 4 (be +1,5R / +1R với SL lẻ 0,1).
- Thời gian: `nightKey` tại 00:30, 04:59, 05:00, 10:00 (hè) và 05:30 ngày 02/11/2026; mốc giờ tại 24/10, 25/10, 31/10, 01/11/2026, 13/03, 14/03, 27/03, 28/03/2027; cửa sổ ±15′ / ±5′; thẻ thông báo đổi giờ.
- Thẻ phiên (vết trước / sau 19:20, xác nhận khi đang canh kèo), sổ (cộng R, lệch máy / tay, 4 con số tuần, Markdown so chuỗi, dòng ⚠ từ `htRef`, cột V/U và Δ cho 4 kịch bản), store (migrate, JSON hỏng, nhập gộp theo `trades.id`).

### `npm run e2e` — 11 pass, 0 fail (≈ 40 giây)
```
ok 1 - 1a · đường đi tới ENTRY và ghi sổ — kịch bản A (4 thao tác Canh + 5 Bấm)
ok 2 - 1b · đường đi tới ENTRY và ghi sổ — kịch bản B (7 thao tác Canh + 6 Bấm)
ok 3 - 2 · tầng 3 khóa khi chưa chốt thẻ / bias CHỜ / có lệnh
ok 4 - 3 · nhịp hồi V ⇒ KHÔNG VÀO màu đỏ
ok 5 - 4 · tải lại giữ nguyên lựa chọn
ok 6 - 5 · mở bằng file:// không lỗi console ở mọi tầng, không thiếu chữ
ok 7 - 6 · 360 px không tràn ngang ở mọi tầng
ok 8 - 7 · phím tắt chạy ở tầng 3 và tắt khi đang gõ vào ô nhập
ok 9 - 8 · "Tôi vẫn vào (phá luật)" hai lần ⇒ TẮT MÁY
ok 10 - 9b · chế độ chỉ xem: ENTRY xám, ghi kèo luyện mắt, không cộng phá luật / chuỗi SL
ok 11 - 9 · chụp ảnh: tầng 1, tầng 3 ENTRY, điện thoại 360 px
# tests 11  # pass 11  # fail 0
```
Số thao tác đếm bằng chính các lần bấm trong test: A = 4 (Canh) + 5 (Bấm); B = 7 + 6. Mọi test mở `index.html` bằng `file://`, giờ cố định 21:30 VN ngày 13/10/2026 (`page.clock.setFixedTime`), và kiểm `console` không có lỗi / cảnh báo.

### `npm run lint:vi` — 0 lỗi
```
lint:vi — 685 chuỗi, 360 khóa ui, 120 từ được phép
Kết quả: 0 lỗi
```
Lint còn kiểm thêm (e): mọi khóa `T('…')` mà `js/ui` và `js/main.js` gọi đều có trong `content.ui` (e2e cũng kiểm trang không chứa `⟦…⟧`).

### Ảnh (docs/shots/)
`tang1-vung.png` (tầng 1) · `tang3-entry.png` (tầng 3, ENTRY xanh) · `dien-thoai-360.png` (điện thoại 360 px, ENTRY).

### Deploy
Repo công khai `AnhNMTHE176111/tram-dem-vang`, Pages nhánh `main` thư mục `/`. Kiểm sau deploy: trang chính, `manifest.webmanifest`, `sw.js`, icon, ảnh kịch bản trả 200; `tests/helpers.js` trả 404 (không bị đưa lên). Mở bằng chromium: service worker kích hoạt, tải lại khi **tắt mạng** vẫn vào được, console không lỗi. `deploy.sh` đã tăng `APP_VERSION` 1.0.0 → 1.0.1 (trong `js/rules.js` và `sw.js`).

Cỡ tải: 196 KB thô (HTML + CSS + JS, không tính ảnh kịch bản), **55 KB sau gzip** (Pages tự nén). Mục "< 100 KB" của plan chỉ đạt theo cỡ nén.

## Những lỗi do chạy thật mà ra (đã sửa, ghi lại cho trung thực)
- Hai test bật kịch bản của tôi kỳ vọng sai: bias KHÔNG tắt cả **B** (plan: `DIS_BIAS_NONE` ở A, B, D). Sửa test, không sửa luật.
- `store.importMerge` báo `tradesAdded` sai khi bản nhập mới hơn bản có sẵn (đếm theo bản gốc chứ không theo bản máy). Đã sửa.
- `computeR` trả `-0` khi thoát đúng giá vào. Đã chuẩn hóa về `0`.
- CSS: lớp `.locked` dùng cho hộp "tầng khóa" trùng với nút tầng bị khóa ⇒ nút nở cao 104 px. Đổi hộp thành `.lockpanel`.
- Nút tầng khóa dùng `aria-disabled` (vẫn bấm được để hiện lý do); test phải bấm bằng `force: true`.

## Chỗ phải tự chọn (plan mơ hồ hoặc tự mâu thuẫn)
1. **`DIS_BIAS_NONE` ở B**: theo bảng plan, bias KHÔNG tắt A, B, D; chỉ C bật.
2. **`NO_COUNTER_BIAS_SCENARIO` cho A**: với A và D, hướng luôn bằng `regimeDir`, nên ngược bias thì `DIS_BREAK_AGAINST_BIAS` luôn chặn trước và `NO_COUNTER_BIAS_SCENARIO` không bao giờ tới. Chọn: `DIS_BREAK_AGAINST_BIAS` **chỉ xét khi bias tự động**; bias **ghi đè** ngược `regimeDir` thì kịch bản vẫn bật và `NO_COUNTER_BIAS_SCENARIO` chặn (khớp ca test của plan).
3. **`NO_RR` và `NO_TP_PAST_ZONE` chỉ xét khi chưa có mã `NO_*` nào phía trước.** Fixture A2 (TP 4181 vượt VAL Âu 4186) và A3 (TP 4182,7 vượt VAL Âu 4188) kỳ vọng không có mã này; đọc đúng QĐ-16 thì cả hai sẽ dính. Cách này khớp mọi fixture và hợp lý (SL sai thì R:R vô nghĩa).
4. **`NO_MID_RANGE`** chỉ bắn cho vùng hạng 1–2 không trùng cạnh (plan: "VWAP giữa range"); High / Low hôm qua rơi vào `NO_B_RANK` đúng như test plan. Với C: vùng không phải `edge` / `edgeOuter`. Khi ngược bias, `NO_MID_RANGE`, `NO_B_RANK` không bắn thêm (tránh trùng mã với `NO_COUNTER_BIAS_ZONE`).
5. **Cạnh (`edge`) chỉ nâng hạng cho B khi `balanced` hoặc `pending`**; `broken` thì không (test plan: B tại VAH Âu khi broken ⇒ `NO_B_RANK`).
6. `mode = broken` mà chưa có bước 1 ⇒ hiệu lực **cân bằng**; có bước 1 chưa có bước 2 ⇒ `pending`.
7. **Vùng kế tiếp** (QĐ-16) = vùng gần nhất theo hướng lệnh trong thẻ, loại vùng vào lệnh và vùng chứa giá vào; tính theo mép gần nhất. TP trống ⇒ dùng TP gợi ý.
8. **Chuỗi SL**: đóng tay có R âm tính như SL, R ≥ 0 thì reset. Chỉ `kind = SL` hoặc đóng tay lỗ cộng chuỗi.
9. **Cửa sổ 19:30 mặc định bật** mỗi đêm (plan: "thứ Năm và khi `t0.touched = false`"). Không tự bật lại vào thứ Năm sau khi người dùng đã tắt.
10. **FOMC** là một cửa sổ hạng 2 từ 01:00 đến 01:30 (thêm bằng nút), nhắc đóng sạch trước 00:45.
11. **Cỡ lệnh MGC**: 1 giá = 10 $ mỗi hợp đồng (tick 0,1 = 1 $). Làm tròn xuống nên với vốn 2.000 $ và rủi ro 2 % có thể ra 0 hợp đồng (hiện rõ "0 hợp đồng").
12. **Giờ mùa đông** tính tại 18:00 VN của đêm (độ chính xác ngày); quy đổi chính xác theo mốc UTC của Mỹ (CN 2 tháng 3 – CN 1 tháng 11) và London (CN cuối tháng 3 – CN cuối tháng 10).
13. **Tự chuyển Canh → Bấm** khi Canh đã điền đủ, để số thao tác đúng 4 / 7; ô số chỉ chốt khi rời ô (sự kiện `change`) để không giật khi đang gõ.
14. Mã `WAIT_*`, `LOCK_OPEN_TRADE`, tên khóa `order` (= `RULE_ORDER`) do tôi đặt, vì plan chỉ nêu `WAIT_B2_MIXED`.
15. Chế độ luyện mắt (`paper`) chỉ bật khi `t0.alert = false`; ENTRY xám, nút "Ghi kèo luyện mắt".
16. Cụm POC là **loại vùng người dùng chọn**; công cụ không tự dò "≥ 2 POC cách ≤ 1 giá".
17. Cờ vùng không lưu trong `localStorage`; engine tính lại từ `type` mỗi lần.
18. "SL bị quét rồi tới TP" và ghi chú nằm ở tầng 5 (và ở hộp "lệnh đóng gần nhất" của tầng 4), không bật hộp thoại riêng.
19. E2E dùng `node:test` + thư viện `playwright` (không dùng `@playwright/test`), chạy toàn bộ trên `file://`.
20. `vi-khong-dau.txt` ngoài từ Việt không dấu còn có vài ký hiệu / từ mượn đã nằm sẵn trong Hệ thống: `ht`, `vn`, `mgc`, `chart`, `london`, `sessionzones`. Lint (c) chỉ áp cho nhóm khóa nhãn (nhãn câu hỏi, nhãn điều khiển, nhãn nút chọn, tiêu đề tầng / mục, nhãn thẻ phiên và sổ), không áp cho câu trợ giúp.
21. Phím `?` mở bảng phím tắt; `Enter` chỉ vào lệnh khi phán quyết là ENTRY.
22. Thanh phán quyết chỉ hiện ở tầng 3 (đúng plan); dưới 900 px thẻ phiên thành ngăn trượt mở bằng nút ở góc trên phải.

## Chưa làm / hạn chế
- Chưa có `REVIEW-1.md`, `USER-TEST-1.md` (thuộc bước 2 của quy trình, không phải vòng implement).
- Giao diện chưa có test đơn vị riêng; phần UI chỉ được kiểm bằng 11 kịch bản e2e và 3 ảnh chụp. Các đường ít đi (nhập JSON qua hộp chọn tệp, tải tệp, sao chép Markdown, đổi giờ mùa đông trên UI, FOMC thêm bằng nút) chưa có e2e.
- Mức hướng dẫn "Quen" chỉ ẩn tiêu chí và ảnh kịch bản; câu trợ giúp "?" vẫn luôn có.
- Chưa có chế độ in / xuất PDF. Chưa đồng bộ đám mây (đúng "Không làm" của plan).
- Service worker chỉ được kiểm trên bản đã deploy (kích hoạt + chạy khi tắt mạng), chưa có test tự động.
