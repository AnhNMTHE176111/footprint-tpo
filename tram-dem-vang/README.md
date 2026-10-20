# Trạm Đêm Vàng

Trang web tĩnh dẫn người dùng đi đúng thứ tự của **Hệ thống Đêm Vàng** (`daily-trading/HE-THONG-DEM-VANG.html` v1.2):
kẻ vùng → bias → chế độ → kịch bản → SL → ghi sổ. Tầng dưới khóa khi tầng trên chưa xong; chữ **ENTRY** chỉ bật đúng lúc đủ điều kiện.

## Cách dùng (một trang)

**Mở ở đâu.** https://anhnmthe176111.github.io/tram-dem-vang/ — mở bằng Chrome hoặc Edge, trên máy tính hoặc điện thoại. Dùng nút cài ứng dụng ở thanh địa chỉ để cài như một ứng dụng; cài rồi thì mở được cả khi mất mạng. Dữ liệu nằm trong trình duyệt của máy bạn, không gửi đi đâu.

**Cài đặt vốn (làm một lần).** Lần đầu mở, hộp "Vốn và rủi ro mỗi lệnh" hiện ra: mặc định 2000 $ và 2 %. Bấm "Lưu" (hoặc "Để sau"). Đổi lại bất cứ lúc nào ở tầng **Sổ**, mục Cài đặt, hoặc bấm nút "Đổi vốn" khi thanh dưới báo "SL tối đa …". Công cụ chỉ nhận số lớn hơn 0; xóa trắng ô thì trả lại số cũ.

**Đêm đầu tiên.** Đi từ tầng 0 sang 5:
1. **Trước** (làm trước 18:00, hai thao tác): bấm Có ở "Tỉnh táo, không bực dọc?" rồi "Xong tầng 0". Khối **Tin tối nay** tự lấy từ lịch Forex Factory: mỗi tin một dòng (giờ VN, tên tin, mức tác động, dự báo / kỳ trước / thực tế) và công tắc bật / tắt khung giờ cấm của tin đó. Không cần nhập khung giờ hay "có tin lớn không": công cụ tự suy; "Thêm tay…" ở cuối khối chỉ dùng khi lịch thiếu.
2. **Vùng**: một dòng gợi ý các mức cần kẻ trên chart A, ba câu (hình hôm qua, đóng hôm qua so với VA, giá hiện tại và VWAP tuần: gõ hai số để bias tự chọn), rồi thêm vùng và "Chốt thẻ phiên". Thêm vùng nhanh nhất: gõ một dòng như `vwapw 4205, vah 4199, val 4185, hvn 4195` rồi Enter (mã ghi ngay dưới ô); hoặc chọn loại + gõ giá + Enter. Chốt xong tự sang tầng Chế độ. Chưa chốt thì tầng Kèo khóa.
3. **Chế độ**: ba nút Cân bằng · Vừa phá · Trend thin. "Vừa phá" cần hướng, cạnh và hai công tắc công nhận; giờ phá công cụ tự ghi lúc bấm "Vừa phá". Đổi hướng hoặc cạnh sau khi đã công nhận là một cú phá mới, phải công nhận lại; sửa chọn nhầm trước khi công nhận thì giữ nguyên giờ phá.
4. **Kèo**: một màn. Khối **Canh** ở trên (làm khi còn thời gian: kịch bản, vùng, hướng, bong bóng, cạnh hay lưng, biên độ nến, nhịp hồi U / V, và với B, D thêm cực trị cụm / đỉnh nhịp hồi); đủ thì tự gập thành một dòng tóm tắt, bấm dòng để mở lại. Khối **Bấm** ở dưới luôn hiện, đúng ba việc sau khi nến xác nhận đóng: nến đạt chuẩn (phím `Đ`), giá vào, SL (Enter ở ô SL khi đang ENTRY là "Vào lệnh"). TP tự gợi ý. Công cụ tự kiểm SL phải nằm qua mép vùng (A, C) hoặc qua cực trị (B, D) ít nhất 0,3 giá. Thanh dưới đổi màu: **CHỜ** (còn thiếu gì), **KHÔNG VÀO** (lý do), **ENTRY** (đủ điều kiện, có số hợp đồng).
5. **Lệnh**: nhập giá hiện tại để thấy R; dời SL về hòa vốn khi tới mốc; đóng lệnh.
6. **Sổ**: xem sổ đêm, gõ "Bạn cộng tay" để đối chiếu máy, "Kết phiên".

Phím tắt ở tầng Kèo: `1 2 3 4` chọn kịch bản, `B`/`S` hướng, `U`/`V` nhịp hồi, `Đ` nến xác nhận đạt, `Enter` vào lệnh, `N` kèo mới (giữ kịch bản, vùng, hướng của B và biên độ nến; xóa các câu quan sát; nút "Xóa hết" bỏ cả kèo), `?` xem bảng phím. Phím tắt tự tắt khi bạn đang gõ vào ô.

**Khi nào công cụ chặn.**
- **TẮT MÁY** (đen, đến hết đêm): đủ 2 lệnh phá luật, hoặc 3 SL liên tiếp (lệnh đóng lỗ từ 0,2R trở lên tính là SL, kể cả đóng tay; quyết định của công cụ, chưa đo). Sang đêm mới thì đếm lại từ 0.
- **"Tôi vẫn vào (phá luật)"** vẫn cho vào lệnh khi thanh dưới là KHÔNG VÀO, nhưng ghi cờ ⚠ vào sổ và tính một lần phá luật.
- **Chế độ chỉ xem**: trả lời "Không" ở câu tỉnh táo thì cả đêm ENTRY hiện xám; lệnh ghi là luyện mắt, không cộng chuỗi SL.
- **Khung giờ cấm** quanh tin lớn: mọi kịch bản KHÔNG VÀO; lệnh đang mở thì đóng sạch trước khung giờ hạng 1.
- **Bản mới**: khi có bản mới, góc trang hiện "Có bản mới. Tải lại". Xóa dữ liệu trình duyệt là mất sổ nếu chưa tải JSON ở tầng Sổ; hãy tải JSON cuối mỗi tuần.

**Lịch tin Forex Factory (tự động).** Một GitHub Action trong repo Pages chạy mỗi 15 phút, tải lịch tuần này và tuần sau, ghi `data/ff.json` (chỉ commit khi nội dung đổi, hoặc bản cũ quá 45 phút). Trang đọc file đó lúc mở và mỗi 5 phút, lưu bản gần nhất để mở bằng file:// vẫn có. Luật: tin USD mức cao ⇒ khung giờ hạng 1 (trước 15′ sau 15′); USD mức vừa ⇒ hạng 2 (±5′); EUR / GBP mức cao ⇒ chỉ cảnh báo; FOMC Statement, họp báo, Chủ tịch Fed ⇒ hạng 1 và đóng sạch lệnh trước giờ tin 15′; NFP, CPI, Core CPI, FOMC trong đêm ⇒ "Đêm có tin lớn — cỡ ½" tự bật (tắt tay được, giờ tắt được ghi lại). Tin chưa có giờ (Tentative, All Day) bị bỏ qua. Lịch cũ hơn 2 giờ hoặc không có ⇒ thanh đỏ "Lịch tin chưa cập nhật — tự kiểm Forex Factory" và công cụ dùng mặc định cũ (19:30 thứ Năm, 21:00). Độ trễ của số "thực tế" tối đa khoảng 15 phút.

**Đêm sau.** Mở lại: công cụ tự nhận đêm mới theo giờ. Ở tầng Vùng, nút **"Sao chép vùng từ đêm …"** (đầu khối vùng) chép VWAP tuần, HVN 3 tuần và hình 3 tuần của đêm trước cùng tuần, và điền luôn giá VWAP tuần vào ô bias; sửa lại giá nếu đã đổi. VAL / VAH Âu vẫn gõ lại mỗi đêm.

**Xuất sổ.** Tầng **Sổ**, mục "Xuất và nhập": Tải Markdown (sổ + thẻ phiên của đêm đang xem), Sao chép Markdown, Tải JSON (toàn bộ dữ liệu, dùng để sao lưu và chuyển máy), Tải CSV (mọi lệnh). Cuối tuần công cụ nhắc tải JSON; nhập JSON gộp vào dữ liệu hiện có, không ghi đè lệnh trùng mã.

**Đổi giờ mùa đông (01/11/2026).** Mỹ sang giờ mùa đông từ Chủ nhật 01/11/2026, London từ 25/10/2026: các mốc giờ Mỹ (COMEX, NYSE, tin, FOMC) muộn thêm 1 giờ. Công cụ tự dịch; không cần làm gì. Thanh trên có chip "Mỹ mùa đông +1h" (bấm "?" cạnh chip để đọc đủ câu), và suốt 8 đêm kể từ ngày đổi giờ (Chủ nhật đổi giờ cộng cả tuần giao dịch đầu tiên, 02/11–08/11) có thẻ nhắc **đổi neo session TPO / SessionZones trên chart từ 19:20 sang 20:20** (IB = 20:20–21:20): việc đó làm trên chart, công cụ không làm thay. Tắt dịch giờ ở Sổ → Cài đặt → "Mốc giờ dịch theo giờ mùa đông" nếu muốn mọi mốc luôn theo giờ mùa hè.

---

## Cấu trúc

```
index.html · manifest.webmanifest · sw.js · icons/ · img/kb-*.png · css/app.css
js/rules.js     luật có thứ tự (RULES) + hằng số, ma trận bias, bảng loại vùng, mốc giờ có múi
js/news.js      lịch Forex Factory (data/ff.json) → tin tối nay + khung giờ cấm tự sinh
js/time.js      giờ VN, giờ mùa đông Mỹ / London, nightKey, khung giờ cấm, pha, dải giờ
js/content.js   TOÀN BỘ chữ hiển thị + htRef của từng mã luật (dữ liệu thuần)
js/engine.js    thuần: (nights, nightKey, now, settings) → phán quyết, reasons, missing, dots, enabled, half
js/journal.js   tạo / đóng lệnh, ngắt mạch, thẻ phiên, sổ 7 cột, Markdown, CSV, thống kê tuần
js/store.js     localStorage, migrate, nhập JSON gộp theo trades.id
js/ui/*.js      vẽ giao diện (status + thẻ phiên, tầng 0–2, tầng 3 + thanh phán quyết, tầng 4–5)
js/main.js      trạng thái, vẽ lại, hộp thoại, phím tắt, service worker
tests/          node:test (CommonJS) — luật, 5 fixture Phụ lục A, ngắt mạch, thời gian, sổ, store
e2e/            Playwright (chromium, file://, có ca bấm bằng chuột thật) — 59 kịch bản
.github/        workflow ff-news.yml (cron 15′) + scripts/ff-fetch.mjs (không phụ thuộc gói ngoài)
scripts/        lint-vi.mjs (kiểm chữ), vi-khong-dau.txt, gen-icons.mjs
docs/           IMPL-1…5.md (báo cáo từng vòng), REVIEW-*.md, USER-TEST-*.md, shots/ (ảnh chụp)
```

Mỗi file JS là một UMD nhỏ: `require` được trong Node (test) và gắn vào `window.TDV.<tên>` trong trình duyệt.

## Lệnh

```bash
npm install          # chỉ cần playwright (devDependency) để chạy e2e
npm test             # 248 test đơn vị (node:test)
npm run e2e          # 59 kịch bản Playwright; cần chromium: npx playwright install chromium
npm run lint:vi      # kiểm chữ trong js/content.js (cấm "bán/mua/lệnh chờ/đập giá", từ lạ, nhãn > 9 từ, dấu chấm thập phân)
./deploy.sh          # tăng APP_VERSION, sao chép app sang bản clone repo Pages, commit + push
```

`deploy.sh` đọc biến `DEPLOY_DIR` (thư mục clone của `AnhNMTHE176111/tram-dem-vang`) và `BUMP=0` (không tăng phiên bản).
Chỉ chép app (không chép tests, e2e, node_modules, docs, scripts) cùng `.github/` (workflow lịch tin) và thêm `.nojekyll`. Thư mục `data/` của repo Pages (file `ff.json` do Action ghi) không bị xóa hay ghi đè.

## Thêm / sửa luật

1. Thêm mã vào `js/rules.js` đúng vị trí trong `RULES` (thứ tự ảnh hưởng tới `reasons` và `missing`).
2. Thêm chữ + `htRef` vào `codes` trong `js/content.js` (và `ctl` nếu muốn bấm vào ô liên quan).
3. Viết test trong `tests/` rồi chạy `npm test` và `npm run lint:vi`.
