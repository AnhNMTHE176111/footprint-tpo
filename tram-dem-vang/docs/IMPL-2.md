# IMPL-2 — Trạm Đêm Vàng, vòng 2 (sửa theo REVIEW-1 và USER-TEST-1)

Ngày: 2026-10-20 · Nguồn quyết định: plan bản 4 + QĐ-20 · Phiên bản triển khai: **1.0.2**

## Kết quả chạy THẬT (Node 22, Playwright chromium, máy Windows 11)

`npm test`
```
# tests 185
# suites 0
# pass 185
# fail 0
# cancelled 0
# skipped 0
```
Theo file: `bias-enable` 43 · `verdict` 56 · `breaker-tier4` 16 · `time-card` 27 · `journal-store` 16 · `fixtures` 8 · **`review1-fixes` 19 (mới, mỗi lỗi đã sửa một test)**.

`npm run e2e`: 15 pass, 0 fail (11 cũ + 4 mới trong `e2e/vong2.spec.mjs`). Ca `v2-1` đi từ dữ liệu TRỐNG bằng giao diện thật: tầng 0 → 1 (8 câu, hai ô số VWAP, 4 vùng, kế hoạch ngược bias) → chốt thẻ → tầng 2 (Vừa phá, công nhận 2 bước, về Cân bằng rồi Vừa phá lại phải công nhận lại) → tầng 3 ENTRY → ghi lệnh → tải lại → đóng lệnh → tải lại về "Kèo mới".

`npm run lint:vi`: `766 chuỗi, 384 khóa ui, 121 từ được phép — Kết quả: 0 lỗi`.

Ảnh chụp lại: `docs/shots/tang1-vung.png`, `tang3-entry.png`, `dien-thoai-360.png`.

Deploy: https://anhnmthe176111.github.io/tram-dem-vang/ trả 200; `sw.js` và `js/rules.js` đều `APP_VERSION = '1.0.2'`; `tests/helpers.js` trả 404 (không bị đưa lên).

## Bảng mục review → trạng thái

| Mục | Trạng thái | Ghi chú |
|---|---|---|
| R1 phá lại sau Cân bằng | đã sửa | `setRegimeMode` tạo cú phá mới; `breakoutFailed` xóa hướng, cạnh, giờ |
| R2 ngăn thẻ phiên điện thoại | đã sửa | nút đổi thành "Đóng", ✕, chạm ngoài, Esc; e2e `v2-2` |
| R3 bias KHÔNG chỉ C ở VAH/VAL Âu | đã sửa | mã mới `NO_BIAS_NONE_EDGE` (htRef 2.2) |
| R4 chuỗi SL | đã sửa | cộng khi `kind = SL` hoặc `r < 0`; "Về hòa vốn" chỉ chọn được sau khi dời SL |
| R5 cửa sổ 19:30 | đã sửa | mặc định bật thứ Năm; engine tự bật khi chưa qua tầng 0 hoặc ngày có tin, trừ khi bạn đã tắt tay |
| R6 NO_RR / NO_TP luôn xét | đã sửa | fixture A2, A3a, A3b đúng QĐ-20 |
| R7 vùng kế tiếp | đã sửa | bỏ vùng cùng cụm (≤ 1 giá) và LVN |
| R8 NO_MID_RANGE khi pending | đã sửa | chỉ khi `balanced` |
| R9 múi giờ cửa sổ tự thêm | đã sửa | lưu `tz: 'VN'`, placeholder "giờ VN" |
| R10 0 hợp đồng | đã sửa | `NO_SIZE_ZERO` (htRef `ST §6`); thanh ENTRY in số hợp đồng |
| R11 bước Bấm vừa một màn | **một phần** | đã: ẩn tiêu chí sau khi chọn, giảm đệm, thanh phán quyết thấp hơn. Chưa: B4 + B5 chung hàng, chip SL/R:R lên thanh phán quyết, e2e đo `scrollHeight` |
| R12 điện thoại hai thanh dính | đã sửa | một dòng cuộn ngang, chip bằng 0 ẩn, chiều cao thanh đo bằng `ResizeObserver`; e2e đo ≤ 35 % |
| R13 mất dữ liệu im lặng | đã sửa | banner đỏ + nút tải JSON khi lưu lỗi; nghe sự kiện `storage` giữa hai tab |
| R14 mã vùng dùng lại | đã sửa | `card.zoneSeq` tăng đơn điệu; vùng đã có lệnh thì không xóa được |
| R15 màu buy / sell | đã sửa | token `--buy` xanh dương, `--sell` cam; lớp `dir-buy`, `dir-sell` |
| R16 nhãn C6 | đã sửa | "Biên độ nến M1 cao nhất trong 5 nến (giá)"; trên 20 giá ⇒ CHỜ `WAIT_C6_BIG` |
| R17 QĐ trong "?" | **một phần** | đã: QĐ-1, QĐ-3 (C3), QĐ-9 (C2) kèm "chưa đo". Chưa: QĐ-19 trên banner trước 20:30 |
| R18 htRef cho mã CHỜ | đã sửa | dòng ⚠ của sổ có chữ |
| R19 chữ nhỏ | đã sửa | 8 chỗ |
| R20 sổ theo đêm | đã sửa | ô chọn đêm ở tầng 5; "Bạn cộng", "Kết phiên", Markdown theo đêm đang chọn |
| R21 form thêm vùng | đã sửa | e2e kiểm ô giá về rỗng |
| R22 nút "?" | đã sửa | 28 px, vùng chạm lớn hơn trên điện thoại |
| R23 vàng cả ngày | đã sửa | cảnh báo trước 20:30 chỉ từ 18:00; e2e `v2-4` |
| R24 tab Bấm thiếu ô chọn kịch bản | đã sửa | chưa chọn kịch bản thì luôn hiện C1 |
| R25 vết sửa thẻ | đã sửa | `<details>` "n lần sửa thẻ" |
| R26 vẽ lại định kỳ | đã sửa | vẽ lại đầy đủ khi bảng bật, cửa sổ hoặc khóa đổi; chờ khi đang gõ |
| R27 service worker | đã sửa | `cache: 'reload'` |
| R28 kích thước | đã sửa | ảnh kịch bản bỏ khỏi precache, nạp lười; không ép < 100 KB (theo chủ plan) |
| R29 nhập JSON thiếu trường | đã sửa | chuẩn hóa từng lệnh; giá vùng dạng chuỗi đi qua `parseNum` |
| R30 "Kết phiên" | đã sửa | gõ "Bạn cộng" không đổi `closedAt` |
| R31 parseNum | đã sửa | "4.193,5" ⇒ 4193,5; ô không hiểu được viền đỏ |
| R32 test khóa nhầm | đã sửa | theo R6, R10 |
| R33 | không cần làm | review xác nhận đúng plan |
| R34 test thiếu | **một phần** | đã: test cho 1, 3, 4, 5, 7, 8, 9, 14, 16, 18, 23, 29, 30, 31; e2e từ dữ liệu trống; e2e 360 px mở / đóng + đo thanh dính. Chưa: ca bật kịch bản `pending` × bias KHÔNG / CHỜ và `thin` × CHỜ, QĐ-4 đổi sang `deepEqual` |

## Bảng mục USER-TEST → trạng thái

| Mục | Trạng thái | Ghi chú |
|---|---|---|
| 1 Từ điển | đã sửa | 22 mục (21 từ được yêu cầu + "mở ảo"), mở từ nút "Từ điển" ở thanh trạng thái và từ mỗi "?" khi mức hướng dẫn = Mới. Đã bỏ "(HT 3.2)" ở chip "mở ảo" |
| 2 ENTRY với 0 hợp đồng | đã sửa | như R10 |
| 3 Sau khi ghi lệnh | đã sửa | ghi lệnh hoặc hủy limit ⇒ `setup` về rỗng, tầng 3 về "Kèo mới"; tải lại không còn ENTRY cũ. Chưa nhớ tầng đang đứng khi tải lại, ô "Giá hiện tại" tầng 4 vẫn mất khi tải lại |
| 4 Bias do bấm tay | đã sửa | hai ô số tùy chọn tự chọn Trên / Dưới / Sát; kế hoạch ngược bias chỉ cảnh báo vàng |
| 5 Nhãn C6 | đã sửa | như R16 |
| 6 Nhiều chip | đã sửa | chip bằng 0 ẩn trên điện thoại, BIAS đứng ngay sau giờ; chip "mở ảo (HT 3.2)" và "Vùng đang chọn" đổi chữ |
| 7 Q1…Q8 | đã sửa | tiêu đề "Tám câu hỏi", câu có số; thông báo thiếu ghi "Q1 (hình hôm qua)", "Q7", "Q8" |
| 8 Tầng 4 sau be | đã sửa | dòng SL "{cũ} → {giá vào} · SL đã về hòa vốn (be)", banner nhắc kéo SL trên sàn, câu "không đổi SL" viết lại |
| 9 Sổ | đã sửa | Markdown có khối Thẻ phiên (bias, vùng, kế hoạch); nhãn "Bạn cộng tay (để đối chiếu máy)" và chip lệch dài hơn |
| 10 Nút bật / tắt | đã sửa | B/S/U/V chỉ chọn, không bỏ chọn khi bấm lần hai; kịch bản đang bị khóa mờ kèm banner lý do; banner "chưa công nhận" đưa lên đầu tầng 2; bỏ dấu chấm kép; "?" mở trong dòng, không che nội dung |
| Số thao tác 42 | không đổi | giữ nguyên đường đi |

## Chỗ phải tự chọn
1. **Fixture A1 và A4a** (½ cỡ với vốn 2.000 $) sẽ ra 0 hợp đồng ⇒ `NO_SIZE_ZERO` theo QĐ-20. Test dùng vốn 20.000 $ cho mọi fixture (`tests/helpers.js`), thêm test riêng chứng minh vốn 2.000 $ ra `NO_SIZE_ZERO`. Cài đặt mặc định của app giữ 2.000 $, 2 % (người dùng sẽ gặp `NO_SIZE_ZERO` cho tới khi tăng vốn trong tầng 5). Chủ plan nên quyết định mặc định.
2. **Cửa sổ 19:30**: tự bật khi `!touched` hoặc `newsDay`, trừ khi đã có `offAt` (tắt tay thì tôn trọng). Dòng ghi chú ở tầng 0 điền giờ theo mùa.
3. `NO_BIAS_NONE_EDGE`: plan chưa đặt mã; mã mới, htRef 2.2, nằm ngay sau `NO_COUNTER_BIAS_ZONE`.
4. `NO_RR`, `NO_TP_PAST_ZONE`, `NO_SIZE_ZERO` chỉ xét khi số liệu hợp lệ (có hướng, SL đúng phía), để không bắn ở ca SL sai phía.
5. `NO_BUBBLE_AGAINST` chỉ bắn khi đã có hướng lệnh (USER-TEST mục 8).
6. `WAIT_C6_BIG` (> 20 giá) là CHỜ, không phải KHÔNG VÀO; `NO_SL_FLOOR` bỏ qua khi C6 > 20.
7. "Về hòa vốn" khóa tới khi bấm "Đã dời SL về hòa vốn"; nếu cần đóng ở giá lỗ thì dùng "Chạm SL" hoặc "Đóng tay".
8. Vùng đã có lệnh thật (không tính luyện mắt) không xóa được, thay vì đếm theo (loại, giá).
9. Ô "Từ điển" trong "?" chỉ hiện khi mức hướng dẫn = Mới; mức Quen vẫn mở được từ thanh trạng thái.
10. Hiển thị cửa sổ 19:30 tự bật có chữ "(tự bật)"; bấm "Bật/Tắt" khi đang tự bật sẽ xin xác nhận và ghi `offAt` như thường.
11. Mục từ điển "mở ảo" thêm ngoài danh sách 21 từ vì chip trên thanh trạng thái dùng chữ đó.
12. Markdown chỉ in khối thẻ khi đêm có thẻ chốt, có câu trả lời hoặc có vùng.
13. `ST §6` hiển thị đúng như yêu cầu ("phạm ST §6"), không có tiền tố "mục".

## Chờ chủ plan
- Mặc định vốn / rủi ro (xem mục tự chọn 1).
- QĐ-19 trong "?" của banner trước 20:30.
- Phụ lục A của plan nên sửa kỳ vọng A2, A3a, A3b và ghi `NO_BIAS_NONE_EDGE`, `NO_SIZE_ZERO`.
