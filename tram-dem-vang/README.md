# Trạm Đêm Vàng

Trang web tĩnh dẫn người dùng đi đúng thứ tự của **Hệ thống Đêm Vàng** (`daily-trading/HE-THONG-DEM-VANG.html` v1.2):
kẻ vùng → bias → chế độ → kịch bản → SL → ghi sổ. Tầng dưới khóa khi tầng trên chưa xong; chữ **ENTRY** chỉ bật đúng lúc đủ điều kiện.

- Bản chạy: https://anhnmthe176111.github.io/tram-dem-vang/ (cài được như ứng dụng, chạy không mạng)
- Nguồn thiết kế duy nhất: `plans/CHECKLIST-DEM-VANG-plan.md` (bản 4, chốt) ở thư mục gốc repo
- Không framework, không bước build, không `type="module"`. Mở thẳng `index.html` bằng `file://` vẫn chạy (khi đó không có service worker).
- Dữ liệu nằm trong `localStorage["tdv.v1"]` của trình duyệt. Xuất / nhập JSON, xuất Markdown và CSV ở tầng 5.

## Cấu trúc

```
index.html · manifest.webmanifest · sw.js · icons/ · img/kb-*.png · css/app.css
js/rules.js     luật có thứ tự (RULES) + hằng số, ma trận bias, bảng loại vùng, mốc giờ có múi
js/time.js      giờ VN, giờ mùa đông Mỹ / London, nightKey, cửa sổ cấm, pha, dải giờ
js/content.js   TOÀN BỘ chữ hiển thị + htRef của từng mã luật (dữ liệu thuần)
js/engine.js    thuần: (nights, nightKey, now, settings) → phán quyết, reasons, missing, dots, enabled, half
js/journal.js   tạo / đóng lệnh, ngắt mạch, thẻ phiên, sổ 7 cột, Markdown, CSV, thống kê tuần
js/store.js     localStorage, migrate, nhập JSON gộp theo trades.id
js/ui/*.js      vẽ giao diện (status + thẻ phiên, tầng 0–2, tầng 3 + thanh phán quyết, tầng 4–5)
js/main.js      trạng thái, vẽ lại, hộp thoại, phím tắt, service worker
tests/          node:test (CommonJS) — luật, 5 fixture Phụ lục A, ngắt mạch, thời gian, sổ, store
e2e/            Playwright (chromium, file://) — 11 kịch bản
scripts/        lint-vi.mjs (kiểm chữ), vi-khong-dau.txt, gen-icons.mjs
docs/           IMPL-1.md (báo cáo vòng 1), shots/ (ảnh chụp)
```

Mỗi file JS là một UMD nhỏ: `require` được trong Node (test) và gắn vào `window.TDV.<tên>` trong trình duyệt.

## Lệnh

```bash
npm install          # chỉ cần playwright (devDependency) để chạy e2e
npm test             # 165 test đơn vị (node:test)
npm run e2e          # 11 kịch bản Playwright; cần chromium: npx playwright install chromium
npm run lint:vi      # kiểm chữ trong js/content.js (cấm "bán/mua/lệnh chờ/đập giá", từ lạ, nhãn > 9 từ, dấu chấm thập phân)
./deploy.sh          # tăng APP_VERSION, sao chép app sang bản clone repo Pages, commit + push
```

`deploy.sh` đọc biến `DEPLOY_DIR` (thư mục clone của `AnhNMTHE176111/tram-dem-vang`) và `BUMP=0` (không tăng phiên bản).
Chỉ chép app (không chép tests, e2e, node_modules, docs, scripts) và thêm `.nojekyll`.

## Thêm / sửa luật

1. Thêm mã vào `js/rules.js` đúng vị trí trong `RULES` (thứ tự ảnh hưởng tới `reasons` và `missing`).
2. Thêm chữ + `htRef` vào `codes` trong `js/content.js` (và `ctl` nếu muốn bấm vào ô liên quan).
3. Viết test trong `tests/` rồi chạy `npm test` và `npm run lint:vi`.
