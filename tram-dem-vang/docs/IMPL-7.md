# IMPL-7 — Trạm Đêm Vàng 2.1.0

Ngày 20–21/10/2026. Sửa theo ba biên bản (`VALIDATE-v2.md`, `TEST-UX-v2.md`, `TEST-UI-v2.md`) và mục 7 của `plans/TRAM-V2-SETUP-ENTRY.md`.
Kiểm: `npm test` 137 test, `npm run e2e` 30 test, `npm run lint:vi` 0 lỗi. Ảnh: `docs/shots/v2-*.png` (chụp lại).

## Thay đổi do yêu cầu người dùng ngày 21/10 (ghi đè một phần biên bản)

1. **Bỏ ô nhập Giá vào, SL, TP, biên độ nến M1** ở cả 4 khối và ô chung. Engine không còn tính R:R, TP gợi ý, SL sai phía.
2. **Bỏ toàn bộ nhóm "SL"** (không còn checkbox SL nào, kể cả tick tay). Luật SL của HT mục 6 chỉ còn ở Từ điển (mục "luật SL (3 điều kiện)") và nút "?" cạnh thanh ENTRY; không tính vào tiến độ khối, không chặn ENTRY.
3. **Bỏ máy tính cỡ lệnh MGC**, ô "Đủ vốn", hộp hỏi vốn lần đầu và cài đặt vốn. Cỡ ½ chỉ còn là nhãn nhắc.
4. **Thanh ENTRY**: "ENTRY BUY · khối B · vùng VWAP tuần · mục tiêu 3R" (+ "cỡ ½" nếu có, + "ngược bias · 2R · cỡ ½" ở B ngược bias).
5. **Sổ**: dòng lệnh không còn giá; R kết quả chọn bằng nút nhanh +3 · +2 · +1 · 0 · −1 hoặc gõ số (TP mặc định = R mục tiêu, SL = −1, hòa = 0, đóng tay phải nhập). Ngắt mạch vẫn theo R (R ≤ −0,2 cộng chuỗi). Markdown / CSV bỏ cột giá. Dữ liệu cũ giữ nguyên giá trong lệnh cũ (chỉ không hiện ô nhập); lệnh cũ có giá thoát vẫn tính R từ giá.
6. "Giá cách vùng ≤ 1 giá, không ở lưng (hoặc râu nến xác nhận chạm vùng)" là **checkbox tick tay** cuối nhóm Kiểm tra của cả 4 khối (HT 4.4).

Số ô mỗi khối (engine): A 12 · B 15 · C 12 · D 12.

## Số thao tác từ nến xác nhận đóng tới ghi lệnh (đo bằng e2e `v21-1`)

Đo: mỗi lần bấm hoặc bấm phím = 1 thao tác.
- Đã làm sẵn Bối cảnh + Kiểm tra trong lúc chờ nến: **2** (tick "Điểm vào" · Enter ghi lệnh).
- Làm nguội, chưa tick ô "giá cách vùng": **3** (thêm 1 tick). Trước bản này: 9 (đã làm sẵn) và 23 (làm nguội).

Trang Setup Entry trên máy tính 1366×768 khi 3 khối thu gọn, khối đang làm đầy ô: `scrollHeight` ≤ 3 màn (e2e `v21-2`; đo thực tế khoảng 2,2 màn).

## 1. VALIDATE-v2 (43 mục)

| Mục | Kết quả |
|---|---|
| 1 blurb B | Đã sửa: "Vào ngược phe bị hấp thụ (theo phe đang hấp thụ)". Test V1 |
| 2 công nhận cú phá | Đã sửa: ba bước, ở trợ giúp và Từ điển. Test V2 |
| 3 TP B ngược bias | Đã sửa: R mục tiêu 2R (`TARGET_R_COUNTER_B`), chữ "ngược bias (2R)", ENTRY ghi "ngược bias · 2R · cỡ ½". Test V3 |
| 4 Từ điển khung giờ cấm | Đã sửa đúng chữ đề xuất. Test V4 |
| 5 D thiếu "giá cách vùng" | Đã sửa: ô tick Kiểm tra cuối ở cả 4 khối (D chk4). Test V5 |
| 6 D thiếu bong bóng | Đã sửa: D chk3. Test V6 |
| 7 B giữa range | Đã sửa: B ctx4. Test V7 |
| 8 trend thin | Đã sửa: B ctx5, C ctx3. Test V8 |
| 9 bias KHÔNG / CHỜ | Đã sửa: ô tự kiểm "Bias cho phép kịch bản này" (KHÔNG ⇒ chỉ C; CHỜ ⇒ cả 4 đỏ). Test V9 |
| 10 ngược bias | Đã sửa theo mục 7: chỉ B, kèm ô tail thật / single print đúng phía + lý do; A, C, D đỏ. Test V10 |
| 11 B thiếu U/V | Đã sửa: B chk4 (HT 9 câu 4 thắng chữ "ưu tiên"). Test V11 |
| 12, 34 "vùng đã kẻ" | Đã sửa: trợ giúp ghi "mở rộng của công cụ theo ca 6/10, chưa đo" |
| 13 bong bóng | Đã sửa chữ + trợ giúp "giữa move: bỏ qua" |
| 14 râu chạm vùng | Đã sửa: chữ ô và `HELP.edge` ("từ 3 giá trở lên là ở lưng") |
| 15 cụm POC | Đã sửa: ghi "QĐ-3, quyết định của công cụ, chưa đo" ở B ctx1, `hang`, vùng |
| 16 HVN ngày | Đã sửa theo cách (b): giữ chặn mọi HVN ngày, ghi QĐ-15; nhãn vùng đổi "chặn hấp thụ" |
| 17, 18 hạng 2 / VWAP tuần | Đã sửa chữ |
| 19, 36 xác nhận B | Đã sửa: trợ giúp riêng, chữ "độ lớn ≥ ½ \|delta\|" |
| 20 TP của C | Không còn áp dụng (bỏ ô TP). Luật "C: cạnh đối diện hoặc POC" nằm trong Từ điển luật SL |
| 21 high / low hôm qua, tail | Đã sửa chữ |
| 22, 23, 24 single print, poor, IB | Đã sửa chữ (IB: "fade ở IB là quyết định của công cụ, chưa đo") |
| 25, 26 đóng tay, ngày tin | Đã sửa: ghi QĐ-22, "quyết định của công cụ" |
| 27 ngưỡng 0,5 giá | Không còn áp dụng (bỏ tính TP) |
| 28, 29 | Đã sửa chữ |
| 30–33 (trích nguồn trong IMPL-6) | Không sửa IMPL-6 (tài liệu lịch sử của bản 2.0). Bản này thay bằng bảng "ô → nguồn" dưới đây, đã ghi đúng nguồn (cụm POC theo QĐ-3; HVN ngày theo QĐ-15; C chk3 chỉ bám HT 4.3; khung giờ theo QĐ-6, QĐ-22, 20:30 chỉ cảnh báo) |
| 35 A chk2 trợ giúp | Đã sửa: `HELP.step3` |
| 37, 38, 39 | Đã sửa chữ ("70%" thống nhất cả app) |
| 40, 41, 42, 43 | Đã sửa: Từ điển có `fade` mới, `move`, `range`, `test lại`; VA "khoảng 70%"; poor "đỉnh phẳng, không có tail" |

Test chữ cho 12–43: `tests/validate.test.js` ("V13–V43").

### Phủ 8 câu HT mục 9

| Câu | Ô phủ |
|---|---|
| 1 thẻ phiên + cùng chiều bias | chung · card; tự kiểm `bias`; ô lý do `counter`; ô `tail` (B) |
| 2 vùng ≤ 1 giá, hạng 1–2 hoặc cạnh khi cân bằng | chk cuối (giá cách vùng) cả 4 khối; B ctx1, B ctx4; C ctx1 |
| 3 chế độ, kịch bản được bật | tự kiểm `bias`; A ctx1–2, B ctx2, ctx5, C ctx2–3 |
| 4 U không V | A chk1, B chk4, D chk2 |
| 5 bong bóng | A chk3, B chk2, C chk3, D chk3 |
| 6 thân + \|delta\| | B chk1; A, B, C, D ent1 |
| 7 nến xác nhận, không 3 nến sau nến dài nhất | ent1 các khối; chung · longest |
| 8 SL 3 điều kiện, R:R, lần ≤ 2 | tự kiểm `zone2`; luật SL trong Từ điển và nút "?" cạnh ENTRY (theo yêu cầu 21/10, không còn ô) |

## 2. TEST-UX-v2 (10 điều + nhỏ)

| Mục | Kết quả |
|---|---|
| 1 lệnh mở chặn kèo mới | Đã sửa: thanh dưới có TP · SL · Hòa · Đóng tay (R điền sẵn, nút nhanh, Enter ghi) |
| 2 ghi lệnh cuộn về đầu, xóa gần hết tick | Đã sửa: giữ vị trí cuộn, giữ Bối cảnh + Kiểm tra, chỉ xóa Điểm vào; thanh dưới nói "Lệnh đang mở" |
| 3 ba ô số | Đã giải quyết bằng cách bỏ hẳn ô số (21/10) |
| 4 ô máy biết mà bắt tick | Một phần: bias và giờ phá (A) thành tự kiểm. "Giá cách vùng" quay lại tick tay do bỏ ô giá (21/10) |
| 5 "3 nến sau nến dài nhất" luôn đỏ, trùng ở B | Đã sửa: nút "vừa có nến dài" mặc định tắt; bỏ ô trùng B |
| 6 hướng và vùng chọn lại | Đã sửa: hướng mặc định theo bias (trừ C); bấm vùng ở thẻ phiên điền vào khối đang làm |
| 7 quá dài | Đã sửa: ô chung một dòng "4/4 đạt"; checkbox hai cột; khối thu gọn một dòng (mục 7) |
| 8 ô trùng ý | Một phần: bỏ ô trùng B; không gộp A ctx1 / ctx2 / chk2 vì là ba bước riêng của công nhận cú phá (HT 3.1) |
| 9 điện thoại chạm là chọn | Đã sửa: chạm lần đầu chỉ hiện định nghĩa, chạm lần hai mới chọn; danh sách tự cuộn cho vừa |
| 10 nhập sai | Đã sửa: chữ rác báo rõ và xóa (ô số còn ở Sổ); SL sai phía không còn vì bỏ ô SL |
| Nhỏ: bấm lại nút Trên tắt bias | Đã sửa: Q1, Q5, VWAP là chọn một, không tắt |
| Nhỏ: nhãn "Ba câu hỏi" | Đã sửa: "Câu hỏi chốt bias" |
| Nhỏ: Poor low hiện hai lần | Đã sửa: bỏ dòng NỢ lặp, thêm chip "nợ" ở dòng vùng |
| Nhỏ: ảnh ví dụ B ghi "+2R" | Không sửa: là ảnh PNG chụp từ chart, không dựng lại được trong vòng này |
| Nhỏ: thông báo che nút "Sổ" | Đã sửa: thông báo nằm trên thanh dưới |
| Nhỏ: gõ "npoc" không lọc ra | Không sửa: "npoc" là mã của ô gõ nhanh; ô lọc dùng tên (gõ "naked") |
| Nhỏ: "Đêm nay không còn khung giờ cấm" | Đã sửa chữ: "Không còn khung giờ cấm đã biết đêm nay" |

## 3. TEST-UI-v2 (14 mục)

| Mục | Kết quả |
|---|---|
| 1 nhãn bị bóp 380–730 px | Đã sửa (CSS đề xuất + bố cục mới); e2e đo ở 9 bề rộng 360–1920 |
| 2 ↑↓ bị chuột giành | Đã sửa: `mousemove`, bỏ qua khi cảm ứng; e2e: 12 lần ↓ đi đúng 12 dòng |
| 3 tương phản | Đã sửa; e2e đo ≥ 4,5:1 cho các phần tử biên bản nêu, sáng và tối |
| 4 ảnh ca thật | Đã sửa: bọc liên kết ảnh gốc, giới hạn chiều cao; điện thoại hộp toàn màn hình |
| 5 vùng bấm < 36 px | Đã sửa các selector nêu; e2e đo |
| 6 nhảy A·B·C·D | Đã sửa: đo chiều cao thanh nhảy (`--jbh`), focus vào tiêu đề khối |
| 7 Esc đóng "?" | Đã sửa, trả focus về nút "?" |
| 8 ô chọn vùng sát đáy | Đã sửa: `scrollIntoView` khi mở |
| 9 thanh rộng 1280 | Một phần: thanh ENTRY chạy hết bề rộng; thanh trạng thái giữ nguyên vì kéo tràn có thể sinh thanh cuộn ngang |
| 10 nút dính chữ | Đã sửa |
| 11 hai nút đóng thẻ | Đã sửa |
| 12 bảng Sổ điện thoại | Đã sửa |
| 13 chữ gợi ý bị cắt | Đã sửa (cỡ chữ nhỏ hơn ở ≤ 600 px) |
| 14 chú thích lệch | Đã sửa |

## Bảng ô → nguồn (thay bảng của IMPL-6)

Mã ô: `ctx` Bối cảnh · `chk` Kiểm tra · `ent` Điểm vào. Ô tự kiểm: `bias`, `breakHours` (A), `zone2`.

| Ô | Nguồn |
|---|---|
| A ctx1–ctx2, chk2 | HT 3.1 ba bước công nhận cú phá; "vùng đã kẻ" là mở rộng theo ca 6/10 (chưa đo) |
| A chk1, B chk4, D chk2 | HT 4.1 hình U |
| A chk3, B chk2, C chk3, D chk3 | HT 4.3 bong bóng (chỉ 4.3; "cùng phe càng tốt" ở C là cộng điểm, không phải ô bắt buộc) |
| mọi khối, chk cuối | HT 4.4 giá cách vùng ≤ 1 giá, râu chạm vùng, ở lưng |
| A `breakHours` | HT 3.2: 18:00–19:20 hay có phá giả |
| `bias` | HT 2.2; ngược bias chỉ B (tail thật hoặc single print đúng phía, 2R, cỡ ½) |
| B ctx1–ctx5 | HT 5·B, 3 (giữa range, trend thin); cụm POC theo QĐ-3; chặn mọi HVN ngày theo QĐ-15 |
| C ctx1–ctx3, chk1–chk2 | HT 5·C, 3 |
| D ctx, chk1 | HT 5·D |
| chung · news | khung quanh tin thật theo QĐ-6, QĐ-22 (20:30 chỉ cảnh báo) |
| chung · breaker, open, card | HT 7, 6, 2 |
| `zone2` | HT 7 và 9 câu 8: tối đa 2 lần mỗi vùng |
