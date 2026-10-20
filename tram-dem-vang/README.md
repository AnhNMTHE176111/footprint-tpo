# Trạm Đêm Vàng

Trang web tĩnh chạy theo **Hệ thống Đêm Vàng** (`daily-trading/HE-THONG-DEM-VANG.html` v1.2). Bản 2.1: bốn tầng
**0 Trước · 1 Vùng · 2 Setup Entry · 3 Sổ**. Không tầng nào bị khóa; chữ **ENTRY** chỉ hiện khi một khối đủ ô.

## Cách dùng (một trang)

**Mở ở đâu.** https://anhnmthe176111.github.io/tram-dem-vang/ — Chrome hoặc Edge, máy tính hoặc điện thoại. Cài như ứng dụng ở thanh địa chỉ để chạy cả khi mất mạng. Dữ liệu nằm trong trình duyệt, không gửi đi đâu.


**Đêm đầu tiên.**
1. **Trước** (trước 18:00): bấm Có ở "Tỉnh táo, không bực dọc?" rồi "Xong tầng 0". Khối **Tin tối nay** tự lấy từ lịch Forex Factory và sinh khung giờ cấm.
2. **Vùng**: ba câu (hình hôm qua, đóng hôm qua so với VA, giá và VWAP tuần), thêm vùng, "Chốt thẻ phiên". Ô **Loại vùng** là danh sách tự vẽ: rê chuột (hoặc ↑ ↓) lên một loại để đọc định nghĩa và cách dùng; gõ chữ để lọc; Enter chọn; Esc đóng. Cùng định nghĩa đó nằm trong **Từ điển**. Thêm nhanh: gõ `vwapw 4205, vah 4199, val 4185, hvn 4195` rồi Enter.
3. **Setup Entry** (bản 2.1): bốn khối **A Phá hồi · B Hấp thụ · C Fade cạnh · D Trap** xếp dọc; khối đang làm mở, khối khác thu gọn một dòng (bấm tiêu đề để mở). Trên cùng là **ô chung**: bốn ô máy tự kiểm (thẻ đã chốt, ngoài khung giờ cấm, chưa tắt máy, không có lệnh mở) gộp một dòng "4/4 đạt", và nút "vừa có nến dài nhất phiên" (mặc định tắt). Mỗi khối: hướng (mặc định theo bias), vùng (bấm ở thẻ phiên cũng được), ba nhóm checkbox **Bối cảnh · Kiểm tra · Điểm vào** (Kiểm tra có ô "Giá cách vùng ≤ 1 giá, không ở lưng"), và các ô máy tự kiểm: bias cho phép kịch bản, giờ phá (khối A), lần ≤ 2 tại vùng. **Không còn ô nhập giá vào, SL, TP, biên độ nến và không còn nhóm SL**: luật SL ở Từ điển (mục "luật SL") và nút "?" cạnh thanh ENTRY. Ngược bias: chỉ khối B, kèm lý do và ô tail. Thanh **ENTRY** dính đáy: "ENTRY BUY · khối B · vùng VWAP tuần · mục tiêu 3R · cỡ ½ (nếu có)" và nút **Ghi lệnh** (Enter). Sau khi ghi, thanh đổi thành lệnh đang mở với nút kết quả TP · SL · Hòa · Đóng tay.
4. **Sổ**: dòng lệnh đang mở nằm trên cùng, nhập kết quả ngay tại đó (Chạm TP · Chạm SL · Hòa · Đóng tay + lý do; R chọn bằng nút nhanh +3 · +2 · +1 · 0 · −1 hoặc gõ số; "SL bị quét rồi tới TP?"); kèm nhắc dời SL về hòa vốn (be). Không còn cột giá. Dưới là bảng 7 cột, "Bạn cộng", Kết phiên, 4 con số tuần, xuất / nhập.

Phím tắt ở Setup Entry: `1 2 3 4` nhảy tới khối, `Enter` ghi lệnh khi ENTRY, `N` xóa tick khối đang làm, `?` bảng phím. Tự tắt khi đang gõ vào ô.

**Khi nào công cụ nhắc.** Không có gì bị khóa. Ô chung hoặc ô tự kiểm sai thì hiện đỏ kèm lý do và tính là "chưa đủ" cho mọi khối; bạn vẫn tick tiếp để luyện mắt.
- **Vẫn vào (thiếu n ô — tính phá luật)**: ghi lệnh khi thiếu ô; dòng Sổ có cờ phá luật và danh sách ô thiếu. Đủ 2 lệnh phá luật hoặc 3 SL liên tiếp thì ô "Chưa tắt máy" đỏ (lệnh đóng lỗ từ 0,2R trở lên tính là SL, kể cả đóng tay; quyết định của công cụ, chưa đo).
- **Chế độ chỉ xem**: trả lời "Không" ở câu tỉnh táo thì cả đêm ENTRY hiện xám; lệnh ghi là luyện mắt, không cộng phá luật hay chuỗi SL.
- **Cỡ ½** là nhãn nhắc (bias KHÔNG, fade cạnh, ngược bias, ngày có tin lớn, vùng hạng 2 ở B, trước 20:30); công cụ không còn tính số hợp đồng.

**Lịch tin Forex Factory (tự động).** Một GitHub Action trong repo Pages chạy mỗi 15 phút, ghi `data/ff.json`. Trang đọc file đó lúc mở và mỗi 5 phút. Tin USD mức cao ⇒ khung giờ hạng 1 (±15′), mức vừa ⇒ hạng 2 (±5′), EUR / GBP mức cao ⇒ chỉ cảnh báo, FOMC ⇒ hạng 1 và đóng sạch lệnh trước 15′, NFP / CPI / FOMC ⇒ ngày tin lớn (cỡ ½). Lịch cũ không phủ đêm nay thì dùng mặc định (19:30 thứ Năm, 21:00) và thanh đỏ báo.

**Dữ liệu v1.** Bản cũ tự được nâng lên v2 khi mở: giữ thẻ phiên, vùng, sổ; bỏ chế độ và kèo cũ; lệnh mở cũ thành dòng Sổ chưa có kết quả.

**Xuất sổ.** Tầng Sổ, mục "Xuất và nhập": Markdown, JSON (sao lưu), CSV; nhập JSON gộp theo mã lệnh. Cuối tuần có nhắc tải JSON.

**Giờ mùa đông (01/11/2026).** Các mốc giờ Mỹ muộn thêm 1 giờ, tự dịch; ngày đổi giờ có thẻ nhắc đổi neo session TPO trên chart từ 19:20 sang 20:20.

---

## Cấu trúc

```
index.html · manifest.webmanifest · sw.js · icons/ · img/kb-*.png · css/app.css
js/rules.js     hằng số, ma trận bias, bảng loại vùng, mốc giờ có múi, hình dạng 4 khối (BLOCK_SHAPE)
js/news.js      lịch Forex Factory (data/ff.json) → tin tối nay + khung giờ cấm tự sinh
js/time.js      giờ VN, giờ mùa đông Mỹ / London, nightKey, khung giờ cấm, pha
js/content.js   TOÀN BỘ chữ: 4 khối, ô chung, định nghĩa loại vùng (cùng nguồn với Từ điển), nhãn
js/engine.js    thuần: evaluate(night, now, settings, news) → common, blocks, entry, focus, breaker
js/journal.js   ghi lệnh từ khối, nhập kết quả, thẻ phiên, sổ 7 cột, Markdown, CSV, thống kê tuần
js/store.js     localStorage (version 2), migrate v1 → v2, nhập JSON gộp
js/ui/*.js      dom, status + thẻ phiên, zonepick (ô chọn loại vùng), tier01, tier2 (Setup Entry + thanh ENTRY), tier3 (Sổ)
js/main.js      trạng thái, vẽ lại, hộp thoại, ghi lệnh, phím tắt, service worker
tests/          node:test (CommonJS): engine, bias, sổ + store, chữ, thời gian, lịch tin
e2e/            Playwright (chromium, file://, chuột thật)
```

Mỗi file JS là một UMD nhỏ (không dùng ES module, để mở `file://` vẫn chạy): `require` được trong Node và gắn vào `window.TDV.<tên>` trong trình duyệt.

## Lệnh

```bash
npm install          # chỉ cần playwright (devDependency) để chạy e2e
npm test             # test đơn vị
npm run e2e          # Playwright; cần chromium: npx playwright install chromium
npm run lint:vi      # kiểm chữ trong js/content.js (cấm "bán/mua/lệnh chờ/đập giá", từ lạ, nhãn > 9 từ, thiếu khóa chữ)
node scripts/shots.mjs   # chụp 4 ảnh vào docs/shots/
./deploy.sh          # tăng APP_VERSION, sao chép app sang bản clone repo Pages, commit + push (BUMP=0: không tăng)
```

`deploy.sh` đọc `DEPLOY_DIR` (thư mục clone của `AnhNMTHE176111/tram-dem-vang`). Chỉ chép app cùng `.github/` và `.nojekyll`; thư mục `data/` (file `ff.json` do Action ghi) không bị xóa.

## Sửa nội dung một khối

1. Số ô mỗi nhóm nằm ở `BLOCK_SHAPE` (`js/rules.js`); chữ từng ô nằm ở `blocks` (`js/content.js`). Hai nơi phải khớp (có test).
2. Ô tự kiểm mới: thêm vào `evalBlock` (`js/engine.js`), nhãn vào `itemLabels`, lý do vào `autoBad`.
3. Loại vùng mới: thêm vào `ZONE_TYPES` / `ZONE_ORDER` và `zoneTypes` (nhãn, vai, định nghĩa, cách dùng); Từ điển và ô chọn tự có.
4. Chạy `npm test`, `npm run e2e`, `npm run lint:vi`.
