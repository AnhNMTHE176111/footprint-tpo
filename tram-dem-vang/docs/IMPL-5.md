# IMPL-5 — Trạm Đêm Vàng, vòng 5 (lịch tin Forex Factory, thu gọn tầng 0–3, REVIEW-4, USER-TEST-4)

Ngày: 2026-10-20 · Nguồn: QĐ-22 (lịch tin tự động), QĐ-23 (tầng 1), QĐ-24 (tầng 2), QĐ-25 (tầng 3), yêu cầu Từ điển / chip, ràng buộc "thu gọn nhưng đủ checklist", REVIEW-4 (3 điều kiện + mục chữ), USER-TEST-4 · Phiên bản: **1.0.6**

## Kết quả chạy THẬT (Node 22, Playwright chromium, máy Windows 11)

`npm test`
```
1..248
# tests 248
# suites 0
# pass 248
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 1079.4397
```

`npm run e2e`
```
1..59
# tests 59
# suites 0
# pass 59
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 14379.4271
```

`npm run lint:vi`
```

lint:vi — 844 chuỗi, 433 khóa ui, 142 từ được phép
Kết quả: 0 lỗi
```

Ảnh chụp (1366×768, giờ cố định): [tang0-tin](shots/tang0-tin.png) · [tang0-moi](shots/tang0-moi.png) · [tang1-moi](shots/tang1-moi.png) · [tang2-moi](shots/tang2-moi.png) · [tang3-moi](shots/tang3-moi.png) · [tu-dien](shots/tu-dien.png). Script chụp: `scripts/shots.mjs`.

## 1. Lịch tin Forex Factory (QĐ-22)

| Phần | Làm gì | Ở đâu |
|---|---|---|
| Nguồn dữ liệu | GitHub Action `*/15 * * * *` + chạy tay; tải `thisweek` và `nextweek`, thử lại 3 lần cách 20 giây, 429 / lỗi ⇒ giữ `data/ff.json` cũ và thoát 0; 404 (nextweek chưa phát hành) không thử lại; chỉ ghi file khi tin đổi hoặc bản cũ quá 45 phút | `.github/workflows/ff-news.yml`, `.github/scripts/ff-fetch.mjs` (Node không gói ngoài); chép sang repo Pages bởi `deploy.sh`, `data/` không bị xóa |
| Trang | `js/news.js`: đổi feed → tin tối nay + khung giờ cấm; id ổn định theo (mã tiền, tên, giờ tuyệt đối); `js/main.js` tải `./data/ff.json?t=…` lúc mở và mỗi 5′ khi tab hiện, lưu `localStorage` (`tdv.ff.v1`) để mở file:// vẫn có; service worker KHÔNG cache `data/ff.json` | `js/news.js`, `js/main.js`, `sw.js` |
| Luật | USD High ⇒ hạng 1 ±15′; USD Medium ⇒ hạng 2 ±5′; EUR / GBP High ⇒ chỉ cảnh báo (`WARN_FX_NEWS`); FOMC Statement / Press Conference / Fed Chair / Federal Funds ⇒ hạng 1 + đóng sạch trước giờ tin 15′ (`flatBefore`); NFP, CPI, Core CPI, FOMC Statement / Press Conference, Federal Funds ⇒ `newsDay` tự bật; Tentative / All Day (00:00 hoặc không có giờ) bỏ qua và ghi chú | `js/news.js` (`classify`, `forNight`), `js/rules.js` (`effectiveWindows`, `effectiveNewsDay`), `js/time.js` (`flatDeadline`) |
| Hiển thị | khối "Tin tối nay" ở tầng 0 (giờ VN · tên · tác động · dự báo / kỳ trước / thực tế · công tắc), tiêu đề "cập nhật lúc hh:mm"; chip đếm ngược "Tin kế 19:30 · CPI m/m · còn 60′" ở thanh trạng thái; thanh đỏ "Lịch tin chưa cập nhật — tự kiểm Forex Factory" khi lịch cũ hơn 2 giờ hoặc không có (khi đó dùng mặc định cũ: 19:30 thứ Năm, 21:00) | `js/ui/tier012.js`, `js/ui/status.js` |
| Tắt / ghi lại | tắt một khung tự sinh ⇒ `t0.newsOverrides[id] = {on:false, offAt}` (id ổn định nên giữ qua tải lại); `newsDay` tắt tay ⇒ `t0.newsDaySet`, `t0.newsDay` | `js/ui/tier012.js`, `js/journal.js` |

Số liệu thật lúc chạy: `data/ff.json` trên Pages có 86 tin của tuần 18–24/10 (feed `thisweek`); tối 20/10 không có tin USD mức cao / vừa (khung giờ cấm tối nay chỉ còn dòng mặc định 21:00 ±5′ và cảnh báo NYSE 20:30); tối thứ Năm 22/10 có "Unemployment Claims" (USD, vừa) 08:30 EDT = 19:30 VN ⇒ khung hạng 2 19:25–19:35. Lần chạy tay đầu: Action thành công, commit `data/ff.json`, Pages trả 200. Cron `*/15` của GitHub chạy trễ với workflow mới (chưa thấy lần cron nào sau khoảng 25 phút đầu); lịch cũ hơn 2 giờ thì app tự báo đỏ nên không nguy hiểm, nhưng cần theo dõi.

## 2. Số thao tác sau thu gọn (đếm click / chọn / gõ một ô)

| Tầng | Trước | Sau | Cách đạt |
|---|---|---|---|
| 0 | Có, Không, Xong + chỉnh khung giờ | **2** (Có, Xong) | tin tự lấy từ lịch; bỏ đoạn "Mặc định", câu "tin lớn", form thêm khung giờ (gập trong "Thêm tay…") |
| 1 (bốn vùng) | 18 | **6** (Q1, Q5, gõ giá, gõ VWAP, gõ nhanh một dòng cho bốn vùng, Chốt); mỗi vùng riêng lẻ: chọn loại + gõ giá + Enter = 2 | 3 câu thay cho 8; ô "gõ nhanh" `vwapw 4205, vah 4199, val 4185, hvn 4195` |
| 2 (Vừa phá) | 7 + gõ giờ phá | **5** (Vừa phá, hướng, cạnh, công tắc 1, công tắc 2); Cân bằng: 1 | bỏ ô Giờ phá, Lần mấy, dải giờ |
| 3 Canh / Bấm | | | xem bảng dưới |

| Kịch bản | Canh (làm lúc còn thời gian) | Bấm (sau nến xác nhận) |
|---|---|---|
| A | 5: C1, C4, C5, C6, B1 (vùng và hướng tự điền từ chế độ) | **3**: nến đạt (Đ), giá vào, SL (Enter ở SL = Vào lệnh) |
| B | 10: C1, C3, C2, C4, C5, C7 (DMA), C6, B1, B2, cực trị cụm | **3** |
| C | 5: C1, C3, C4, C5, C6 (hướng tự từ phía vùng; không có B1, B2) | **3** |
| D | 9: C1, C3, C4, C5, C6, C7 (move), C7 (hồi quá 70 %), B1, đỉnh nhịp hồi | **3** |

(Test: `e2e/vong5.spec.mjs` v5-6A…D đo đúng 3 thao tác Bấm; `e2e/app.spec.mjs` 1a, 1b đo Canh 5 / 10 và Bấm 3.)

## 3. Bảng "8 câu checklist (tám chấm HT mục 9) → ô cung cấp dữ liệu sau khi thu gọn"

Engine chấm tám chấm từ cùng dữ liệu như cũ (`js/engine.js`, mảng `dots`); chỉ đổi NƠI nhập.

| Chấm | Điều kiện (engine) | Ô nguồn sau thu gọn | Ghi chú |
|---|---|---|---|
| 1 | thẻ đã chốt, có hướng, bias đủ, ngược bias thì có lý do | Tầng 1 (ba câu + Chốt) · tầng 3 C2 (+ lý do ngược bias) | không đổi nội dung |
| 2 | có vùng, C5 "ở cạnh", không dính nhóm mã vùng | Tầng 3 Canh: C3, C5 | không đổi |
| 3 | kịch bản đang bật | Tầng 2 (chế độ) + tầng 1 + tầng 3 C1 | không đổi |
| 4 | B1 = U (C: tự đạt) | **Canh** B1 (chuyển từ Bấm) | chỉ đổi chỗ hỏi |
| 5 | C4 hợp lệ | Canh C4 | không đổi |
| 6 | B: B2 = giảm dần; A, C, D: nến xác nhận đạt | **Canh** B2 (B) · Bấm nến xác nhận | B2 chuyển sang Canh |
| 7 | nến xác nhận đạt và không trong 3 nến sau nến dài nhất | Bấm nến xác nhận · tầng 2 nút nến dài nhất | không đổi |
| 8 | SL đúng chỗ + số liệu hợp lệ + R:R + C6 trong 0–20 + trần SL + chưa quá 2 lần vùng | Bấm giá vào, SL (TP gợi ý) · Canh C6 · **máy tự kiểm B5** từ vùng (A, C) hoặc ô cực trị ở Canh (B, D) | B5 hết là ô 3 trạng thái |

## 4. Bảng "mã luật → ô nguồn" (70 mã, đủ `RULE_ORDER`; không bỏ mã nào)

| Mã luật | Hiệu ứng | Ô cung cấp dữ liệu SAU thu gọn | Trước |
|---|---|---|---|
| OFF_RULE_BREAKS | OFF | Sổ lệnh (cờ phá luật) | không đổi |
| OFF_SL_STREAK | OFF | Sổ lệnh (R ≤ −0,2 hoặc chạm SL chưa be) | không đổi |
| LOCK_OPEN_TRADE | LOCK | Lệnh đang mở (tầng 4) | không đổi |
| NO_NEWS_WINDOW | NO | Tầng 0 · Tin tối nay (lịch tự động + dòng mặc định 21:00 + Thêm tay) | tầng 0 · nhập khung giờ tay |
| DIS_LONGEST_BAR | DISABLE | Tầng 2 · nút "Vừa có nến dài nhất phiên" | không đổi |
| DIS_NO_CARD | DISABLE | Tầng 1 · Chốt thẻ phiên | không đổi |
| DIS_BIAS_WAIT | DISABLE | Tầng 1 · ba câu (Q1, Q5, giá / VWAP tuần) | Q1, Q5, VWAP tuần |
| DIS_BIAS_NONE | DISABLE | Tầng 1 · ba câu | Q1, Q5, VWAP tuần |
| DIS_NO_EDGE | DISABLE | Tầng 1 · có vùng loại cạnh trong thẻ (thay Q6) | Q6 + vùng |
| DIS_NOT_BROKEN | DISABLE | Tầng 2 · ba nút chế độ + hai công tắc | không đổi |
| DIS_PENDING_ACCEPT | DISABLE | Tầng 2 · hai công tắc công nhận | không đổi |
| DIS_NO_MOVE | DISABLE | Tầng 2 · chế độ | không đổi |
| DIS_M5_OUTSIDE | DISABLE | Tầng 2 · chế độ | không đổi |
| DIS_USE_D | DISABLE | Tầng 2 · chế độ | không đổi |
| DIS_THIN_NO_FADE | DISABLE | Tầng 2 · chế độ | không đổi |
| DIS_BREAK_AGAINST_BIAS | DISABLE | Tầng 2 · hướng phá + bias tầng 1 | không đổi |
| DIS_EARLY_BREAK | DISABLE | Tầng 2 · giờ phá TỰ GHI lúc bấm "Vừa phá" (không hiện) | ô "Giờ phá" gõ tay |
| BIAS_NONE | HALF | Tầng 1 · bias | không đổi |
| SCENARIO_C | HALF | Tầng 3 · C1 | không đổi |
| COUNTER_BIAS | HALF | Tầng 3 · C2 + lý do ngược bias | không đổi |
| NEWS_DAY | HALF | Tầng 0 · lịch tự suy (NFP / CPI / FOMC); tắt tay được; "Thêm tay…" để bật tay | câu "Hôm nay có tin lớn" |
| B_RANK2 | HALF | Tầng 1 · loại vùng | không đổi |
| BEFORE_2030 | HALF | Đồng hồ | không đổi |
| WAIT_SCENARIO | WAIT | Tầng 3 · C1 | không đổi |
| NO_COUNTER_BIAS_SCENARIO | NO | Tầng 3 · C2 | không đổi |
| NO_COUNTER_BIAS_ZONE | NO | Tầng 3 · C2 | không đổi |
| NO_BIAS_NONE_EDGE | NO | Tầng 3 · C3 | không đổi |
| WAIT_COUNTER_REASON | WAIT | Tầng 3 · C2 (lý do) | không đổi |
| WAIT_ZONE | WAIT | Tầng 3 · C3 | không đổi |
| WAIT_REGIME_DIR | WAIT | Tầng 2 · hướng | không đổi |
| WAIT_SIDE | WAIT | Tầng 3 · C2 | không đổi |
| NO_ZONE_3RD | NO | Tầng 3 · C3 | không đổi |
| NO_BANNED_ZONE | NO | Tầng 3 · C3 + loại vùng tầng 1 | không đổi |
| NO_MID_RANGE | NO | Tầng 3 · C3 | không đổi |
| NO_C_NOT_EDGE | NO | Tầng 3 · C3 | không đổi |
| NO_PENDING_ACCEPT | NO | Tầng 3 · C3 + tầng 2 | không đổi |
| NO_B_RANK | NO | Tầng 3 · C3 | không đổi |
| NO_FIGHT_BREAK | NO | Tầng 3 · C3 | không đổi |
| NO_BUBBLE_AGAINST | NO | Tầng 3 · Canh · C4 | không đổi |
| NO_UNCLEAR | NO | Tầng 3 · ô đang "Không rõ" (C4, B1, B2 trong Canh; B3 trong Bấm) | không đổi (B1, B2 ở Bấm) |
| WAIT_C4 | WAIT | Canh · C4 | không đổi |
| WAIT_C4_SAME | WAIT | Canh · C4 | không đổi |
| WAIT_C5 | WAIT | Canh · C5 | không đổi |
| WAIT_C5_BACK | WAIT | Canh · C5 | không đổi |
| NO_BACK | NO | Canh · C5 | không đổi |
| WAIT_C6 | WAIT | Canh · C6 | không đổi |
| WAIT_C6_BIG | WAIT | Canh · C6 | không đổi |
| WAIT_C7_DMA | WAIT | Canh · C7 (B) | không đổi |
| NO_DMA_SLOPE | NO | Canh · C7 (B) | không đổi |
| WAIT_C7_MOVE | WAIT | Canh · C7 (D) | không đổi |
| NO_D_NO_MOVE | NO | Canh · C7 (D) | không đổi |
| WAIT_C7_DEEP | WAIT | Canh · C7 (D) | không đổi |
| NO_D_DEEP | NO | Canh · C7 (D) | không đổi |
| WAIT_B1 | WAIT | Canh · B1 (CHUYỂN từ Bấm) | Bấm |
| NO_V_PULLBACK | NO | Canh · B1 (CHUYỂN từ Bấm) | Bấm |
| WAIT_B2 | WAIT | Canh · B2 (CHUYỂN từ Bấm) | Bấm |
| WAIT_B2_MIXED | WAIT | Canh · B2 (CHUYỂN từ Bấm) | Bấm |
| NO_MOMENTUM | NO | Canh · B2 (CHUYỂN từ Bấm) | Bấm |
| WAIT_B3 | WAIT | Bấm · nến xác nhận (phím Đ) | không đổi |
| WAIT_B3_NOT | WAIT | Bấm · nến xác nhận | không đổi |
| WAIT_CALC | WAIT | Bấm · giá vào + SL (TP gợi ý) | không đổi |
| WAIT_B5 | WAIT | Canh · cực trị cụm / đỉnh nhịp hồi (B, D); A, C: chỉ khi vùng không có giá | nút B5 3 trạng thái |
| NO_SL_POS | NO | MÁY TỰ KIỂM: SL qua mép vùng (A, C) hoặc cực trị (B, D) + 0,3 | nút B5 3 trạng thái |
| NO_SL_SIDE | NO | Bấm · SL | không đổi |
| NO_SL_FLOOR | NO | Bấm · SL + C6 (Canh) | không đổi |
| NO_SL_CAP | NO | Bấm · SL | không đổi |
| NO_RR | NO | Bấm · giá vào / SL / TP | không đổi |
| NO_TP_PAST_ZONE | NO | Bấm · TP | không đổi |
| WAIT_CAPITAL | WAIT | Cài đặt vốn (nút Đổi vốn) | không đổi |
| NO_SIZE_ZERO | NO | Bấm · SL + Cài đặt vốn | không đổi |

## 5. Các ô BỊ BỎ khỏi màn hình và lý do an toàn (điều kiện (a) không nuôi luật, hoặc (b) engine suy được)

| Ô bỏ | Lý do |
|---|---|
| 7 ô tick "đã kẻ trên chart" | (a) không luật nào đọc `card.drawn`; thay bằng một dòng gợi ý |
| Q1′ hình 3 tuần | (a) không luật nào đọc `q1w`; dữ liệu cũ và nút "Sao chép vùng" vẫn đọc / chép được |
| Q3 nợ chưa lấp | (b) nợ suy từ vùng single print / poor high-low / naked POC (thẻ phiên hiện từ đó); dữ liệu cũ vẫn được hiển thị |
| Q4 giá đang ở LVN / HVN | (a) không luật nào đọc `q4` |
| Q6 Âu đã dựng range | (b) suy từ việc thẻ có vùng cạnh (`DIS_NO_EDGE` đã đọc vùng); `lockCard` ghi `q6` suy ra để dữ liệu tương thích. Điều kiện chốt đổi từ "Q1, Q5, Q6, VWAP tuần, ≥ 1 vùng" thành "Q1, Q5, VWAP tuần, ≥ 1 vùng" (test `time-card` cập nhật) |
| Q2a / Q2b (tail thật) | **GIỮ dữ liệu** (`q2top` / `q2bot` nuôi cờ `tail` của QĐ-9): chuyển thành ô nhỏ "Tail thật?" ngay trên dòng vùng High / Low hôm qua |
| Ô Giờ phá | (b) `breakout.at` tự ghi lúc bấm "Vừa phá" (hoặc bước 1 nếu chưa có); `DIS_EARLY_BREAK` và QĐ-19 vẫn đọc giá trị đó |
| "Lần mấy" (`nth`) | (b) vẫn lưu và đếm khi bấm "Chui lại trong"; chỉ không hiện ô, hiện dòng "Đã phá hụt 1 lần — không đuổi, chờ lần 2" |
| Dải giờ phá giả / mở ảo / đáng tin ở tầng 2 | (a) chỉ là nhãn, đã có ở thanh trạng thái |
| Kế hoạch 1, Kế hoạch 2, Hủy khi | gộp một ô "Ghi chú kế hoạch (tùy chọn)" (`card.planNote`); cảnh báo kế hoạch ngược bias vẫn chạy trên ô đó; dữ liệu cũ (plan1, plan2, cancelWhen) vẫn hiện ở thẻ phiên |
| Nút 3 trạng thái B5 | (b) máy tự kiểm — xem mục 6 (có một giới hạn cần biết) |
| Câu "Hôm nay có tin lớn" | (b) tự suy từ lịch; ô ghi tay còn trong "Thêm tay…" |
| Khối "Mặc định: 21:00 ±5′…" | thành hai dòng mờ trong danh sách tin (21:00 ±5′ có công tắc; NYSE 20:30 luôn bật) |

## 6. Điều cần chủ plan biết (trung thực)

1. **B5 tự kiểm chỉ nửa với A và C.** HT 6 nói A: "sau râu nến xác nhận HOẶC mép xa của vùng, cái nào xa hơn, + 0,3"; C: "sau râu phá hụt + 0,3". Máy chỉ kiểm được vế "mép xa của vùng + 0,3" (đúng như đề bài QĐ-25); vế "râu nến" không có trong dữ liệu nên KHÔNG được kiểm (C6 sàn nhiễu `NO_SL_FLOOR` che một phần). Nếu muốn giữ đủ, cần một ô số "đầu râu nến xác nhận" ở Bấm (ngoài giới hạn 3 thao tác); chưa làm, chờ quyết định. B và D kiểm đủ vì hỏi cực trị ở Canh.
2. B5 trước là ô 3 trạng thái gồm "Chưa chắc ⇒ CHỜ". Ô đó bỏ; dữ liệu cũ có `slPos` (right / wrong / unsure) vẫn được tôn trọng (test `verdict.test.js` "B5 chưa chắc ⇒ CHỜ" giữ nguyên, xanh).
3. Fixture A1–A5 và mọi test luật xanh KHÔNG đổi kỳ vọng. Test đổi chỉ ở chỗ giao diện / điều kiện chốt: `time-card` (chốt không cần Q6; thẻ đổi giờ hiện 8 đêm), `review2-fixes` ("Ba câu hỏi"), e2e (đường đi tầng 1, 3; v4-7, v4-10, v4-14).
4. Ngưỡng "R ≤ −0,2 là SL" đã ghi vào trợ giúp chuỗi SL và `OFF_SL_STREAK` với chữ "quyết định của công cụ, chưa đo" (REVIEW-4 mục 2). Plan không bị sửa.
5. Sửa cạnh / hướng SAU khi đã công nhận vẫn là cú phá mới (xóa bước 1, 2 và giờ phá = lúc bấm, đúng REVIEW-3 mục 2); TRƯỚC khi công nhận thì giữ giờ phá (REVIEW-4 mục 3, test `news.test.js`, e2e v5-9).
6. Lỗi nặng USER-TEST-4 "⟦halfNoteMin⟧": do chính tôi xóa nhầm hai khóa `halfNote`, `halfNoteMin` khi dọn "khóa không dùng" (mã gọi chúng bằng `T(cond ? 'a' : 'b')` nên lint không thấy) rồi deploy bản đó. Đã khôi phục; lint nay nhận cả dạng `T(cond ? 'a' : 'b')`, test `vong5.test.js` chạy lint, e2e v5-12 quét chữ "⟦" ở sáu tầng và ca cỡ ½ SL 3 giá.
7. Hai "câu hỏi mở" của bản này: (a) có nên giữ vế "râu nến" của B5 cho A, C bằng một ô số (mục 6.1); (b) cron của GitHub chạy trễ, cần theo dõi vài giờ đầu.

## 7. REVIEW-4 và USER-TEST-4

| Mục | Kết quả |
|---|---|
| REVIEW-4 mục 1 (thẻ đổi neo session) | thẻ đổi giờ hiện suốt 8 đêm kể từ ngày đổi (Chủ nhật 01/11 + 02/11–08/11) ở dạng thẻ dưới thanh trên, không chỉ chip; LDN và hai thẻ quay lại cùng quy tắc; test `time-card`, e2e v4-10 |
| mục 2 (ngưỡng R ≤ −0,2) | chữ vào `chipStreakTip` và `OFF_SL_STREAK` |
| mục 3 (giờ phá) | xong, có test |
| mục 4 (VA / VAH / VAL / POC) | thêm "(Định nghĩa TPO chuẩn; trang Hệ thống không định nghĩa.)" |
| mục 5 ("cỡ đủ") | một chữ ở mọi nơi |
| mục 6 (WAIT_CAPITAL trùng, khóa không dùng) | đã xóa khối `WAIT_CAPITAL` trùng; khóa không dùng đã dọn (trừ khóa gọi gián tiếp) |
| mục 7 (README) | thêm "Khi nào công cụ chặn", "Lịch tin", sửa mục đổi giờ mùa đông |
| USER-TEST-4 b1 (Kết phiên nuốt cú bấm) | nút luôn bấm được, đọc thẳng giá trị trong ô lúc bấm; e2e v5-11 |
| b2 (⟦halfNote⟧) | mục 6.6 |
| b3 (giá limit / giá khớp gõ đè) | chặn khi quá 6 chữ số hoặc lệch quá 20 giá so với giá vào dự kiến, báo đỏ trong hộp; e2e v5-10 |
| b4 (bấm thẻ kịch bản tắt) | hiện ngay dưới hàng thẻ: "A · Phá hồi: Chưa có cú phá…"; e2e v5-8 |
| b5 (dải đỏ "lịch chưa cập nhật" lúc mở máy) | lúc đó lịch chưa tải xong / chưa có; nay đọc bản lưu `tdv.ff.v1` ngay khi mở nên chỉ đỏ khi thật sự cũ hơn 2 giờ hoặc chưa từng có |
| b6 (tên "cửa sổ cấm") | gõ "cua so" ra mục "khung giờ cấm (còn gọi cửa sổ cấm)" |
| (d)5 Sang tầng 3 | "Chốt thẻ phiên" tự sang tầng 2 (như cũ); nút "Sang tầng 2 / 3" còn lại chỉ là lối tắt khi quay lại; chưa gộp thêm |
| Từ điển | thêm "SL bị quét", mô tả hình B theo QĐ-11, khung giờ cấm theo QĐ-22; thẻ có đệm, thanh cuộn mảnh, ô tìm dính trên, nút X, 420 px (toàn màn trên điện thoại); hộp "?" và chip cùng kiểu gọn |

## 8. Chỗ tự chọn

1. Hạn "cũ" của lịch: 2 giờ tính từ `fetchedAt`; Action chỉ ghi lại khi tin đổi hoặc bản cũ quá 45 phút (nên `fetchedAt` tiến ít nhất mỗi giờ khi lịch đứng yên).
2. `data/ff.json` chỉ giữ các trường cần dùng (title, country, date, impact, forecast, previous, actual).
3. CPI và Core CPI cùng giờ cho hai dòng và hai khung giờ chồng nhau; không gộp.
4. Giờ "đóng sạch" của khung tự sinh (FOMC…) = giờ tin − 15′ (`flatBefore`); khung họp báo / Chủ tịch Fed kéo dài 30′ sau tin.
5. 19:30 mặc định bị ẩn khi lịch còn mới; lựa chọn tay trước đó ở dòng 19:30 không có tác dụng trong lúc lịch ok.
6. Gõ nhanh vùng: mã `vwapw vwapd vah val poc hvn hvn3 lvn high low npoc ibh ibl ph pl`, `spu spl reu rel` (u trên, l dưới), `hvn 4195-4197` cho vùng; mục lạ báo lại và không thêm gì.
7. Canh tự gập đúng một lần khi đủ (đủ nghĩa gồm B1, B2 và cực trị với B, D); sửa Canh sau đó không gập lại.
8. Phím `Đ` cũng nhận `d` / `D` (bàn phím Telex gửi `d`).
9. "Kèo mới" giữ C1–C3 và C6; "Xóa hết" bỏ cả kèo.
10. Bỏ chip "Lịch tin lúc hh:mm" khỏi thanh trạng thái (đẩy thanh trên lên hai dòng ở 1366 px); nhãn "cập nhật lúc" nằm ở tiêu đề khối Tin tối nay.

## 9. Chưa xong

- B5 nửa "râu nến" của A, C chưa kiểm (mục 6.1).
- Mã `WAIT_B5` trỏ tới ô `c8` chỉ có ở B, D; với A, C (khi vùng không có giá) bấm mã sẽ không tìm thấy ô.
- "Sao chép vùng chép luôn VAL / VAH Âu hôm trước làm gợi ý mờ" (USER-TEST-4 d5) chưa làm.
- Cron của GitHub chưa thấy chạy tự động trong lúc làm (chạy tay ba lần, đều thành công).
