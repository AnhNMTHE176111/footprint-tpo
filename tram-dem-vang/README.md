# Trạm Đêm Vàng

Trang web tĩnh dẫn người dùng đi đúng thứ tự của **Hệ thống Đêm Vàng** (`daily-trading/HE-THONG-DEM-VANG.html` v1.2):
kẻ vùng → bias → chế độ → kịch bản → SL → ghi sổ. Tầng dưới khóa khi tầng trên chưa xong; chữ **ENTRY** chỉ bật đúng lúc đủ điều kiện.

## Cách dùng (một trang)

**Mở ở đâu.** https://anhnmthe176111.github.io/tram-dem-vang/ — mở bằng Chrome hoặc Edge, trên máy tính hoặc điện thoại. Dùng nút cài ứng dụng ở thanh địa chỉ để cài như một ứng dụng; cài rồi thì mở được cả khi mất mạng. Dữ liệu nằm trong trình duyệt của máy bạn, không gửi đi đâu.

**Cài đặt vốn (làm một lần).** Lần đầu mở, hộp "Vốn và rủi ro mỗi lệnh" hiện ra: mặc định 2000 $ và 2 %. Bấm "Lưu" (hoặc "Để sau"). Đổi lại bất cứ lúc nào ở tầng **Sổ**, mục Cài đặt, hoặc bấm nút "Đổi vốn" khi thanh dưới báo "SL tối đa …". Công cụ chỉ nhận số lớn hơn 0; xóa trắng ô thì trả lại số cũ.

**Đêm đầu tiên.** Đi từ tầng 0 sang 5:
1. **Trước** (làm trước 18:00): tỉnh táo chưa, cửa sổ cấm tối nay, có tin lớn không.
2. **Vùng**: tick các mức đã kẻ trên chart, trả lời ba câu bắt buộc (Q1, Q5, Q6), gõ giá hiện tại và VWAP tuần để bias tự chọn, thêm 3–5 vùng, rồi "Chốt thẻ phiên". Chưa chốt thì tầng Kèo khóa.
3. **Chế độ**: chọn cân bằng, vừa phá hay Trend thin. "Vừa phá" cần hướng, cạnh và hai bước công nhận; đổi hướng hoặc cạnh về sau là một cú phá mới, phải công nhận lại.
4. **Kèo**: chọn kịch bản đang bật, trả lời lần lượt ở tab **Canh** (trước khi nến xác nhận đóng) rồi tab **Bấm** (sau khi nến đóng). Canh đủ thì tự sang Bấm đúng một lần; nút "Quay lại Canh" ở đầu tab. Thanh dưới đổi màu: **CHỜ** (còn thiếu gì), **KHÔNG VÀO** (lý do), **ENTRY** (đủ điều kiện, có số hợp đồng). Bấm "Vào lệnh" khi ENTRY.
5. **Lệnh**: nhập giá hiện tại để thấy R; dời SL về hòa vốn khi tới mốc; đóng lệnh.
6. **Sổ**: xem sổ đêm, gõ "Bạn cộng tay" để đối chiếu máy, "Kết phiên".

Phím tắt ở tầng Kèo: `1 2 3 4` chọn kịch bản, `B`/`S` hướng, `U`/`V` nhịp hồi, `Enter` vào lệnh, `N` kèo mới, `?` xem bảng phím. Phím tắt tự tắt khi bạn đang gõ vào ô.

**Đêm sau.** Mở lại: công cụ tự nhận đêm mới theo giờ. Ở tầng Vùng, nút **"Sao chép vùng từ đêm …"** (đầu khối vùng) chép VWAP tuần, HVN 3 tuần và hình 3 tuần của đêm trước cùng tuần, và điền luôn giá VWAP tuần vào ô bias; sửa lại giá nếu đã đổi. VAL / VAH Âu vẫn gõ lại mỗi đêm.

**Xuất sổ.** Tầng **Sổ**, mục "Xuất và nhập": Tải Markdown (sổ + thẻ phiên của đêm đang xem), Sao chép Markdown, Tải JSON (toàn bộ dữ liệu, dùng để sao lưu và chuyển máy), Tải CSV (mọi lệnh). Cuối tuần công cụ nhắc tải JSON; nhập JSON gộp vào dữ liệu hiện có, không ghi đè lệnh trùng mã.

**Đổi giờ mùa đông (01/11/2026).** Mỹ sang giờ mùa đông từ Chủ nhật 01/11/2026, London từ 25/10/2026: các mốc giờ Mỹ (COMEX, NYSE, tin, FOMC) muộn thêm 1 giờ. Công cụ tự dịch; không cần làm gì. Thanh trên có chip "Mỹ mùa đông +1h" (bấm "?" cạnh chip để đọc đủ câu), và đúng ngày đổi giờ có thêm dòng nhắc **đổi neo session TPO / SessionZones trên chart từ 19:20 sang 20:20** (IB = 20:20–21:20): việc đó làm trên chart, công cụ không làm thay. Tắt dịch giờ ở Sổ → Cài đặt → "Mốc giờ dịch theo giờ mùa đông" nếu muốn mọi mốc luôn theo giờ mùa hè.

---

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
e2e/            Playwright (chromium, file://, có ca bấm bằng chuột thật) — 43 kịch bản
scripts/        lint-vi.mjs (kiểm chữ), vi-khong-dau.txt, gen-icons.mjs
docs/           IMPL-1…4.md (báo cáo từng vòng), REVIEW-*.md, USER-TEST-*.md, shots/ (ảnh chụp)
```

Mỗi file JS là một UMD nhỏ: `require` được trong Node (test) và gắn vào `window.TDV.<tên>` trong trình duyệt.

## Lệnh

```bash
npm install          # chỉ cần playwright (devDependency) để chạy e2e
npm test             # 220 test đơn vị (node:test)
npm run e2e          # 43 kịch bản Playwright; cần chromium: npx playwright install chromium
npm run lint:vi      # kiểm chữ trong js/content.js (cấm "bán/mua/lệnh chờ/đập giá", từ lạ, nhãn > 9 từ, dấu chấm thập phân)
./deploy.sh          # tăng APP_VERSION, sao chép app sang bản clone repo Pages, commit + push
```

`deploy.sh` đọc biến `DEPLOY_DIR` (thư mục clone của `AnhNMTHE176111/tram-dem-vang`) và `BUMP=0` (không tăng phiên bản).
Chỉ chép app (không chép tests, e2e, node_modules, docs, scripts) và thêm `.nojekyll`.

## Thêm / sửa luật

1. Thêm mã vào `js/rules.js` đúng vị trí trong `RULES` (thứ tự ảnh hưởng tới `reasons` và `missing`).
2. Thêm chữ + `htRef` vào `codes` trong `js/content.js` (và `ctl` nếu muốn bấm vào ô liên quan).
3. Viết test trong `tests/` rồi chạy `npm test` và `npm run lint:vi`.
