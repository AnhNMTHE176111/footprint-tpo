# IMPL-6 — Trạm Đêm Vàng 2.0 "Setup Entry"

Ngày: 2026-10-20 · Nguồn: `plans/TRAM-V2-SETUP-ENTRY.md` (mục 1–6) · Phiên bản **2.0.0**

## Kết quả chạy THẬT (Node 22, Playwright chromium, Windows 11)

`npm test`
```
1..128
# tests 128
# suites 0
# pass 128
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 597.6436
```

`npm run e2e`
```
1..16
# tests 16
# suites 0
# pass 16
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 6456.941
```

`npm run lint:vi`
```
lint:vi — 748 chuỗi, 342 khóa ui, 147 từ được phép
Kết quả: 0 lỗi
```

Ảnh (1366×768, giờ cố định 21:30): [v2-tang1-dropdown](shots/v2-tang1-dropdown.png) (đang rê "Poor low") · [v2-setup-entry](shots/v2-setup-entry.png) · [v2-setup-entry-390](shots/v2-setup-entry-390.png) · [v2-so](shots/v2-so.png). Script: `node scripts/shots.mjs`.

## Đã làm theo từng mục thiết kế

| Mục | Việc | Ở đâu |
|---|---|---|
| 1 | Bốn tầng `0 Trước · 1 Vùng · 2 Setup Entry · 3 Sổ`; không khóa; thẻ phiên vẫn ở cột phải, bỏ dòng "Chế độ" | `js/main.js`, `js/content.js` (`tiers`), `js/ui/status.js` |
| 2 | Ô chọn loại vùng tự vẽ (combobox): rê chuột hoặc ↑ ↓ hiện định nghĩa + "dùng thế nào"; gõ lọc; Enter / Esc; điện thoại hiện ngay dưới dòng; 18 loại vùng; Từ điển sinh từ cùng bảng `zoneTypes` | `js/ui/zonepick.js`, `js/content.js` (`zoneTypes`, `glossary`), test `content.test.js`, e2e v2-9, v2-10 |
| 3 | Bỏ tầng Chế độ và tầng Lệnh. "Ghi lệnh" ghi thẳng dòng Sổ; kết quả nhập trên dòng lệnh mở ở đầu Sổ; nhắc be thành một dòng; ô chung thay "chỉ một lệnh mở" | `js/journal.js` (`createTrade`, `closeTrade`, `beInfo`), `js/ui/tier3.js` |
| 4 | Bốn khối dọc mở sẵn, thanh nhảy A·B·C·D dính đầu, thanh ENTRY dính đáy, tiến độ `n/tổng`, viền xanh khi đủ, khối tick cuối thắng, ô chung, ô ngược bias, phím 1–4 / Enter / N, "Vẫn vào (thiếu n ô)" | `js/ui/tier2.js`, `js/engine.js`, `css/app.css` |
| 5 | Sổ: dòng lệnh mở trên cùng + nút kết quả; cột "vùng" thay "chế độ"; cột "4 kiểm tra" in các ô kiểm tra đã tick; Markdown / CSV cập nhật | `js/ui/tier3.js`, `js/journal.js` |
| 6 | `store` version 2 + migrate v1 → v2; `evaluate(night, now, settings, news)` → `{common, blocks, entry, focus, breaker}`; test viết lại; xóa mã luật DIS_ / NO_, tầng Chế độ / Lệnh, test cũ | `js/store.js`, `js/engine.js`, `tests/`, `e2e/v2.spec.mjs` |

Số ô mỗi khối (tính cả hướng, vùng, giá, ô tự kiểm): A, B 18 · C, D 15 (cộng thêm 1 khi ngược bias, vì có ô lý do).

## Chỗ tự chọn (thiết kế để mở)

1. **Ô tự kiểm "Đủ vốn cho 1 hợp đồng"** (QĐ-21) là ô thứ 4 trong nhóm tự kiểm của mỗi khối: vốn × rủi ro không đủ 1 hợp đồng thì khối chưa đủ. Thiết kế chỉ ghi 3 ô SL; giữ QĐ-21 nên thêm ô này.
2. **Vùng kế tiếp / TP vượt vùng** (QĐ-20) gộp vào ô "R:R ≥ 1:2": đỏ khi R:R tới vùng kế tiếp dưới 1:2 hoặc TP vượt vùng đó quá 0,5 giá; lý do nói rõ từng trường hợp.
3. **Ô vị trí SL** chỉ còn là một ô tick của người (theo mục 4.2); bỏ phần máy tự kiểm vị trí theo mép vùng (QĐ-25) vì thiết kế yêu cầu ô tick.
4. **Ngược bias** không còn luật khóa vùng / kịch bản (QĐ-9): chỉ bắt gõ lý do và tính cỡ ½. Lệnh đóng tay lý do "khác" vẫn tính phá luật.
5. **Lệnh mở** là mọi dòng Sổ chưa có kết quả, ở mọi đêm, kể cả lệnh luyện mắt (nên nhập kết quả cho cả kèo luyện mắt). Mở app khi còn lệnh mở thì vào thẳng tầng Sổ.
6. Sau "Ghi lệnh" **ô chung "nến dài nhất" không tự bỏ tick** (thiết kế chỉ nói bỏ tick của khối); "N" gọi cùng hàm với sau Ghi lệnh (bỏ tick, giá vào / SL / TP / biên độ nến, lý do; giữ hướng, vùng).
7. Bias CHỜ / KHÔNG chỉ hiện nhắc ở đầu Setup Entry, không khóa khối nào.
8. Khóa `localStorage` giữ `tdv.v1` để dữ liệu cũ tự được nâng; trong dữ liệu `version = 2`. Dữ liệu v1 được lưu lại dạng v2 ngay lần mở đầu.

## Bảng: mỗi checkbox → câu nguồn trong trang Hệ thống

Mã ô: `ctx` = Bối cảnh, `chk` = Kiểm tra, `ent` = Điểm vào, `sl` = SL. Câu nguồn trích từ `hethong.txt` (mục 3.1, 4, 5, 6).

| Ô | Chữ trên màn hình | Câu nguồn |
|---|---|---|
| A ctx1 | Có 1 nến M5 đóng ngoài cạnh (VA Âu, IB hoặc vùng đã kẻ) | 3.1: "Giá đóng 1 nến M5 ngoài cạnh VA Âu (hoặc ngoài IB…)"; A · Bối cảnh: "Cú phá đã được công nhận đủ 3 bước" |
| A ctx2 | Nhịp hồi về cạnh giữ được, không nến M5 nào đóng ngược vào trong | 3.1: "Nhịp hồi về cạnh giữ được: không có nến M5 nào đóng ngược trở lại trong vùng" |
| A ctx3 | Bias cùng chiều phá | A · Bối cảnh: "Bias cùng chiều phá" |
| A ctx4 | Cú phá không rơi vào 18:00–{comex} | A · Loại bỏ: "phá trong 18:00–19:20"; 3.2: "18:00–19:20: hay có phá giả VA" |
| A chk1 | Hồi hình U, ≥ 3 nến, không phải V | A · Kiểm tra: "Hồi hình U (4.1) về cạnh vừa phá, ≥3 nến" |
| A chk2 | Tại cạnh: delta cùng chiều phá hoặc bong bóng hấp thụ phe ngược | A · Kiểm tra: "Tại cạnh: delta cùng chiều phá, hoặc bong bóng hấp thụ phe ngược" |
| A chk3 | Bong bóng to gần nhất không ngược phe còn giữ | 4.3: "Không vào ngược phe bong bóng khi mức còn giữ (vòng trắng)" |
| A chk4 | Giá cách cạnh ≤ 1 giá | 4.4: "Entry hợp lệ khi giá cách vùng đã kẻ ≤ 1 giá" |
| A ent1 | Nến M1 đóng theo chiều phá, thân ≥ nửa biên độ, delta cùng dấu | A · Điểm vào: "Nến M1 đóng theo chiều phá, thân ≥ nửa biên độ, delta cùng dấu" |
| A sl1 | SL sau râu nến xác nhận hoặc mép xa vùng (cái xa hơn) + 0,3 giá | A · SL: "Sau râu nến xác nhận hoặc sau cạnh vùng (cái nào xa hơn) + 0,3 giá đệm" |
| B ctx1 | Giá tại VWAP tuần, VWAP ngày, HVN tuần, cụm POC, hoặc cạnh VA Âu khi đang cân bằng | B · Bối cảnh: "Giá tới VWAP tuần (tốt nhất); VWAP ngày / HVN tuần…; hoặc cạnh VA Âu khi đang cân bằng"; cụm POC theo bảng 2.3 của công cụ (hạng 2, chưa đo) |
| B ctx2 | Không phải HVN 3 tuần, LVN, HVN ngày | B · Bối cảnh: "Không gọi hấp thụ ở HVN ngày ngay sau cú phá cực trị, và ở HVN 3 tuần"; bảng 2.3: HVN 3 tuần "Không fade"; LVN là vùng cấm trên thẻ phiên |
| B ctx3 | Không đang phá VWAP / cạnh theo chiều move (nếu có là phá hồi — dùng A) | B · Loại bỏ: "đang đồng thời phá VWAP/cạnh VA theo chiều move (đó là phá hồi, phải theo)"; Xung đột: "Hấp thụ vs phá hồi cùng lúc ⇒ theo phá hồi" |
| B ctx4 | Không ngay sau nến dài nhất phiên | B · Loại bỏ: "ngay sau nến dài nhất phiên" |
| B chk1 | 3 nến cuối: thân và \|delta\| giảm dần, không cực trị mới | B · Kiểm tra: "3 nến cuối: thân và \|delta\| giảm dần (4.2), không cực trị mới" |
| B chk2 | Bong bóng ở cực trị cùng phe với lệnh | B · Kiểm tra: "Bong bóng ở cực trị cùng phe với lệnh định vào" |
| B chk3 | DMA đi ngang | B · Kiểm tra: "DMA đi ngang" |
| B chk4 | Giá cách vùng ≤ 1 giá | 4.4 (như A chk4) |
| B ent1 | Nến xác nhận ngược chiều move, delta đảo dấu ≥ ½ delta nến lớn nhất của move | B · Điểm vào: "Nến xác nhận ngược chiều move, delta đảo dấu ≥ 50% delta nến lớn nhất của move" |
| B sl1 | SL sau cực trị của cụm hấp thụ + 0,3 giá, không ở giữa cụm | B · SL: "Sau cực trị của cụm hấp thụ + 0,3 giá. Không đặt SL ở giữa cụm" |
| C ctx1 | Giá ở đúng cạnh VA Âu / range (≤ 1 giá), không ở giữa range | C · Bối cảnh: "Giá ở đúng cạnh VA Âu / range (≤1 giá)"; Loại bỏ: "Giá ở giữa range" |
| C ctx2 | Chưa có nến M5 nào đóng ngoài cạnh | C · Bối cảnh: "chưa có nến M5 đóng ngoài" |
| C chk1 | Phá hụt: râu xuyên cạnh rồi đóng lại trong | C · Kiểm tra: "Phá hụt: râu xuyên cạnh rồi đóng lại trong" |
| C chk2 | Delta ủng hộ chiều vào | C · Kiểm tra: "Delta ủng hộ chiều vào" |
| C chk3 | Bong bóng to gần nhất không ngược phe còn giữ | C · Kiểm tra: "Có bong bóng cùng phe ở cạnh càng tốt"; 4.3 |
| C ent1 | Nến M1 đóng lại trong range; thân không ngắn, râu ngược không dài | C · Điểm vào: "Nến M1 đóng lại trong range sau khi xuyên"; Loại bỏ: "nến xác nhận thân ngắn hoặc râu ngược dài" |
| C sl1 | SL sau râu phá hụt + 0,3 giá | C · SL: "Sau râu phá hụt + 0,3 giá" |
| D ctx1 | Có move rõ ≥ 5 giá cùng chiều bias | D · Bối cảnh: "Một move rõ (≥ 5 giá) cùng chiều bias" |
| D ctx2 | Không đang đi ngang | D · Bối cảnh: "Không gọi trap khi đang đi ngang" |
| D ctx3 | Nhịp hồi ngược tới một vùng, chưa quá 70 % move | D · Bối cảnh: "nhịp hồi ngược tới một vùng"; Loại bỏ: "Nhịp hồi đã đi quá 70% move trước" |
| D chk1 | Đỉnh hồi có bong bóng hấp thụ phe hồi, hoặc nến hồi delta thuận mà đóng dưới nửa thân | D · Kiểm tra: "bong bóng hấp thụ phe hồi, hoặc nến hồi có delta thuận mà đóng dưới nửa thân" |
| D chk2 | Hồi hình U, không phải V | 4.1 (V = phe hồi đang thắng) |
| D ent1 | Nến M1 đóng theo chiều move cũ, thân dài, delta cùng dấu | D · Điểm vào: "Nến M1 đóng theo chiều move cũ, thân dài, delta cùng dấu" |
| D sl1 | SL sau đỉnh nhịp hồi + 0,3 giá | D · SL: "Sau đỉnh nhịp hồi + 0,3 giá" |
| chung · card | Đã chốt thẻ phiên | Mục 2: "Không có thẻ phiên thì không có lệnh"; 7: "Lệnh khi chưa có thẻ phiên: 0" |
| chung · news | Không trong khung giờ cấm | 7: "Đánh tin 19:30 / 20:30 / 21:00: 0" (khung giờ tự sinh từ lịch, QĐ-22) |
| chung · breaker | Chưa tắt máy | 7: "Lệnh phá luật trong phiên: 2 ⇒ tắt máy"; "SL liên tiếp: 3 ⇒ tắt máy" |
| chung · open | Không có lệnh đang mở | 6: "tổng rủi ro mở cùng lúc là 1 lệnh. Không nhồi" |
| chung · longest | Không trong 3 nến M1 sau nến dài nhất phiên | Xung đột: "Sau nến dài nhất phiên: không kịch bản nào được bật trong 3 nến kế tiếp"; 7: "Lệnh trong 3 nến sau nến dài nhất phiên: 0" |
| tự kiểm · zone2 | Lần ≤ 2 tại vùng | 7: "Vào lại cùng vùng: tối đa 2"; 9 câu 8: "đây là lần ≤ 2 tại vùng này" |
| tự kiểm · slFloor | SL ≥ biên độ nến M1 cao nhất 5 nến | 6 · Luật SL: "Sàn nhiễu: khoảng SL ≥ biên độ nến M1 cao nhất trong 5 nến gần nhất" |
| tự kiểm · slCap | SL ≤ 4 giá | 6 · Luật SL: "Trần: khoảng SL ≤ 4 giá" |
| tự kiểm · rr | R:R ≥ 1:2 | 6 · TP: "3R, hoặc vùng kế tiếp nếu gần hơn (tính trước; dưới 1:2 thì bỏ)"; 9 câu 8: "R:R ≥ 1:2 tính trước" |
| ngược bias | Lý do ngược bias (ô gõ) | 2.2 Luật cứng: "Lệnh ngược bias phải ghi lý do vào thẻ phiên trước khi bấm. Không ghi = phá luật" |
| tự kiểm · size | Đủ vốn cho 1 hợp đồng | QĐ-21 của công cụ (quyết định của công cụ, chưa đo); không có trong Hệ thống |

Định nghĩa 18 loại vùng bám bảng 2.3, mục 2.1 (Q2, Q3, Q4) và định nghĩa Market Profile chuẩn; chỗ Hệ thống không có thì ghi định nghĩa chuẩn ngắn, không thêm luật (cụm POC và IB high / low là định nghĩa chuẩn).

## Mã đã xóa

Tầng Chế độ (`tier2` cũ), tầng Lệnh (`tier4` cũ), hộp "Vào lệnh" market / limit, `RULES` (mọi luật `DIS_*`, `NO_*`, `WAIT_*`), `effectiveRegime`, `derivedSlPos`, `setRegimeMode`, `setBreakoutField`, `breakoutFailed`, `changeScenario`, `newSetupKeep`, `fillLimit`, `cancelLimit`, `beStatus`, `markBE`, `forceCodes`, `priceProblem`, khối `controls` / `codes` của `content.js`, 125 khóa chữ không còn dùng, các luật CSS của tầng cũ, và các file test / e2e cũ (bias-enable, breaker-tier4, review1-3, verdict, fixtures, vong5, app, vong2–5).
