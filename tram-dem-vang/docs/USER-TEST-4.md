# USER TEST 4 — Trạm Đêm Vàng 1.0.4 (trader mới học order flow/TPO 1 tháng, lần dùng thứ tư, cuối)

Cách thử: Playwright + Chromium, mở bản đã deploy https://anhnmthe176111.github.io/tram-dem-vang/ (Sổ → Cài đặt ghi "Phiên bản 1.0.4"), xóa localStorage, dùng như người mới (hộp hỏi vốn → "Lưu"). 1366×768 và 390×844. Mọi cú bấm dùng chuột thật (di chuột, nhấn, giữ 90 ms, thả); gõ bằng bàn phím thật, tôi bấm vào ô rồi gõ (không dùng `fill`). Giờ giả lập 18:45 VN (đêm 1, 20/10) và 18:45 hôm sau (đêm 2, 21/10); riêng kịch bản A thử thêm ở 20:45. Nhập giả lập như ba lần trước: giá hiện tại 4184, VWAP tuần 4181, VAL Âu 4182, VAH Âu 4192, HVN 3 tuần 4200. Không sửa code, không commit. Ảnh trong `user-test-shots-4/` (khoảng 45 ảnh), Markdown xuất ra: `export-dem1.md`.

Đã đọc trước: USER-TEST-3 (4,4/5), phần "Chưa sửa" ở IMPL-4, README mục "Cách dùng".

## (a) 5 vấn đề lớn của lần 3: đã sửa chưa?

| # | Vấn đề lần 3 | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Điện thoại: thanh trên 105 px + thanh dưới 189 px = 35 % màn hình | **Thỏa đáng.** Đo ở 390 px: thanh trên **43 px** (giờ, BIAS, nút "Trạng thái ▾"; các chip còn lại mở xuống khi bấm), thanh dưới ENTRY **118 px** = 161/844 = **19 %** (lần 3: 35 %). Bấm "Trạng thái" thì khung chip mở xuống đè lên nội dung, không đẩy trang. Nút "?" đo được 40×40. Chưa hết hẳn: nút "Thẻ phiên" nổi ở góc phải chồng lên mép thanh trên; thanh tầng 0-5 cao 75 px. | [m04](user-test-shots-4/m04-entry-dau.png) [m06](user-test-shots-4/m06-trang-thai-mo.png) [m03](user-test-shots-4/m03-tang3-dau.png) |
| 2 | "Sao chép vùng" không điền VWAP tuần của bias, nằm quá thấp, thông báo nhắc Q1′ khi không có | **Thỏa đáng một phần.** Chép xong ô "VWAP tuần" của bias **tự có 4181** (lần 3 vẫn trống); thông báo đúng: "Đã chép: VWAP tuần 4181,0 · HVN 3 tuần 4200,0" (không còn Q1′). Nút nay nằm sát đầu danh sách vùng 1d. Nhưng "đầu khối vùng" vẫn cách đầu trang khoảng **1250 px** (nằm sau Q1…Q6 và bias), nên người mới phải cuộn mới thấy; và đêm 2 vẫn 29 thao tác (mục c). | [32](user-test-shots-4/32-sau-sao-chep.png) |
| 3 | Chữ tắt trong Sổ và 3 chip đếm | **Thỏa đáng.** Sổ có dòng chú giải dưới bảng ("bb bong bóng · Δ delta · cạnh hay lưng…"), cũng có trong Markdown; chip đổi thành "Phá luật 0 trên 2", "SL liên tiếp 0 trên 3", "Lệnh mở 0 trên 1"; "Số đêm liên tiếp không phá luật". Tôi hiểu được cả Sổ mà không cần hỏi. Bảng vẫn dùng "bb giữ" và "Δ giảm" trong ô nhưng đã có chú giải ngay dưới. | [17b](user-test-shots-4/17b-ket-phien.png) `export-dem1.md` |
| 4 | Từ điển thiếu VA/VAH/VAL/POC, phá giả, cửa sổ cấm | **Thỏa đáng một phần.** Đã có "VA / VAH / VAL / POC", "phá giả", "khung giờ cấm" (tìm "vah" ra mục đúng). Nhảy từ "?" của DMA: tiêu đề "DMA" hiện đủ, không bị ô tìm che; trên điện thoại mở Từ điển không bật bàn phím. Còn thiếu: gõ "cua so" không ra gì (vì đổi tên thành "khung giờ cấm" mà tầng 0 lúc mở đầu còn ghi "Cửa sổ cấm"), không có "SL bị quét", "hình dạng B" vẫn ghi "chưa mô tả riêng", DMA vẫn không nói là đường nào. | [21](user-test-shots-4/21-tu-dien-vah.png) [22](user-test-shots-4/22-nhay-DMA.png) |
| 5 | "Giờ phá" tự điền giờ hiện tại làm A luôn tắt | **Thỏa đáng.** Lúc 20:45, chọn Vừa phá + Phá lên + cạnh VAH Âu + bước 1 Có + bước 2 Có thì A bật 3R, vùng "VAH Âu 4192,0 (tự điền)", hướng "buy (tự điền)", **không phải sửa giờ**. Lúc 18:45 A tắt đúng lý do "Cú phá trong 18:00–19:20 hay là phá giả — nghi trước, tin sau", và dưới ô giờ có chú thích "Mặc định là giờ bấm; sửa thành giờ nến M5 đóng ngoài cạnh". Bấm A đang tắt khi chưa chọn gì thì tấm bên dưới vẫn "Chọn một kịch bản đang bật" (không còn thanh đỏ của kịch bản khác). | [43](user-test-shots-4/43-a1845-bam-A.png) [42](user-test-shots-4/42-a2045-tang3.png) |

**Sửa làm tệ hơn: một điều, và nó nằm ngay ca quan trọng.** Khi SL từ 3 giá trở lên (ca cỡ ½ không chia được và ca KHÔNG VÀO vì SL quá lớn), chip dưới thanh phán quyết hiện chữ thô **"⟦halfNoteMin⟧"** (SL 4 giá) và **"⟦halfNote⟧"** (SL 5 giá), tức khóa chữ chưa có nội dung. Phần "1 hợp đồng = cỡ đủ, rủi ro 40 $" ở dòng ENTRY thì đúng (vấn đề cỡ ½ của lần 3 đã được sửa ở đây), nhưng chip bên dưới hỏng. [60](user-test-shots-4/60-sl-4178.png)

Các kịch bản đã đi lại:

- **B (đêm 1):** ENTRY BUY 4182 · SL 4180 (2,0 giá) · TP 4188 · 1:3 · cỡ ½ · 1 hợp đồng. Ở 1366×768 vừa đúng một màn, thanh dưới 115 px. [08](user-test-shots-4/08-B-ENTRY.png)
- **limit → khớp → be → đóng:** "Vào lệnh" → chọn limit; **ô giá limit đã tự điền 4182** → "Xác nhận" → ô "Giá khớp thật" cũng tự điền 4182 → "Khớp rồi". Gõ giá hiện tại 4185,5 ("R hiện tại +1,75"), tick nến (ăn ngay), "Đã dời SL về hòa vốn" (dòng "4180,0 → 4182,0 · SL đã về hòa vốn (be)", nhắc kéo SL trên sàn, câu "Sau khi vào không đổi SL" đã biến mất). Nút đóng đổi thành "Chạm SL (đã ở hòa vốn)", giá thoát tự 4182, "R gợi ý: 0". Xác nhận đóng thì trang tự sang Sổ: R = 0, "Máy cộng: 0 R". Ra hòa, đúng. [13](user-test-shots-4/13-sau-be.png) [16](user-test-shots-4/16-so.png)
- **C:** trên HVN 3 tuần: KHÔNG VÀO, ô hướng nói "Vùng này không có phía nên không fade được; C chỉ làm ở cạnh" (đúng chuyện, hết câu lạc đề "chọn phía ở tầng 1"). Trên VAH Âu (bias BUY): tự điền sell, chip "Ngược bias: không được phép", thanh "KHÔNG VÀO — Ngược bias…", và **không còn mời gõ lý do**. Trên VAL Âu: tự điền buy, CHỜ thiếu bong bóng, giá cách, biên độ. [50](user-test-shots-4/50-C-hvn.png) [51](user-test-shots-4/51-C-vah.png)
- **Đêm 2:** sao chép vùng như dòng 2 bảng trên. Mã vùng vẫn nhảy z1, z2 (HVN), z3 (VAL), z4 (VAH) vì HVN nằm trước VAL; tôi phải để ý z3 mới là VAL. [33](user-test-shots-4/33-dem2-ENTRY.png)
- **Kích cỡ theo SL:** SL 4179 (3 giá), 4178 (4 giá): ENTRY "1 hợp đồng = cỡ đủ, rủi ro 40 $"; SL 4177 (5 giá): KHÔNG VÀO "SL tối đa 4,0 giá. Bỏ kèo, hoặc tăng vốn" kèm nút "Đổi vốn" mở đúng hộp vốn. [61](user-test-shots-4/61-doi-von.png)
- **Sổ / Bạn cộng / Kết phiên / Markdown:** có "Thẻ phiên (18:45)", bảng lệnh, dòng chú giải, "Máy cộng: 0 R · Bạn cộng: 0 R · Lệnh phá luật: 0 · SL bị quét rồi tới TP: 0". Lỗi ở nút "Kết phiên", xem mục (b) số 1.
- **Gõ số rồi bấm ngay "?" và nút kế, chuột thật:**
  - Nút kế sau khi gõ (gõ biên độ rồi "Đi ngang/Còn dốc" xen kẽ; gõ giá vào, gõ SL, gõ giá hiện tại rồi tick nến): **30/30 ăn ngay lần đầu**, cả 1366 và 390 px.
  - "?" sau khi gõ biên độ (DMA) hoặc gõ giá hiện tại (bias): khoảng **32/34 mở và giữ mở**; 2 lần khung không mở (1 lần ở 1366, 1 lần ở 390, không lặp lại được theo quy luật). Khi mở thì không bị vẽ lại làm mất và không đè đáp án. [18](user-test-shots-4/18-help-DMA-mo.png)

## (b) Chỗ kẹt mới

| # | Làm gì | Thấy gì | Kẹt / đoán ở đâu |
|---|---|---|---|
| 1 | Sổ: gõ "Bạn cộng tay" = 0 rồi bấm ngay "Kết phiên" | Nút "Kết phiên" **xám** (disabled) cho tới khi ô gõ xong; cú bấm đầu **bị nuốt**, chỉ cú bấm thứ hai mới hiện "Đã kết phiên." (thử lại với đồng hồ thật, vẫn vậy) | Đúng loại lỗi "gõ số rồi bấm ngay bị nuốt" của lần 2-3, còn sót đúng ở nút cuối phiên. Người dùng không biết đã kết phiên chưa. [17c](user-test-shots-4/17c-ket-phien.png) |
| 2 | SL ≥ 3 giá khi cỡ ½ | Chip dưới thanh phán quyết là chữ thô "⟦halfNoteMin⟧" / "⟦halfNote⟧" | Thấy là lỗi chưa hoàn thiện, đúng ở kèo B SL 3-4 giá mà tôi hay vào. [60](user-test-shots-4/60-sl-4178.png) |
| 3 | Hộp limit: tôi quen gõ giá nên bấm vào ô rồi gõ 4182 | Ô đã tự điền 4182 nên thành "41824182", Sổ ghi "chờ khớp ở 41824182,0", không báo gì | Không có kiểm tra giá limit lệch xa giá vào (vô lý gấp 1000 lần). Người mới có thể ghi sai sổ mà không biết. [10](user-test-shots-4/10-lenh-limit.png) |
| 4 | Bấm kịch bản đang tắt khi đang chọn kịch bản khác (C rồi D tắt) | Tấm bên dưới vẫn là C | Chưa sửa (IMPL-4 đã nói). Dễ tưởng đã sang D. [53](user-test-shots-4/53-bam-D-mo.png) |
| 5 | Đầu tầng 3 lúc mở máy | Thỉnh thoảng có thêm dải vàng "Lịch tin chưa cập nhật — tự kiểm Forex Factory. Đang dùng khung giờ mặc định." trên cùng, đẩy cả trang xuống ~24 px | Không rõ là lỗi hay chỉ do thiếu mạng; không biết cần làm gì. |
| 6 | Đổi tên "Cửa sổ cấm" → "Khung giờ cấm" | Tầng 0 và chip lúc đầu còn "Cửa sổ cấm", các màn sau "Khung giờ cấm", Từ điển chỉ có "khung giờ cấm" | Hai tên cho một thứ; tìm "cua so" ra rỗng. |
| 7 | Điện thoại, nút "Thẻ phiên" | Nổi đè lên mép thanh trên và sát hàng tầng | Nhỏ, không chặn bấm. |

## (c) Số thao tác từ mở trang tới ENTRY

Cách đếm như lần 3: mỗi click, mỗi lần chọn ô thả xuống, mỗi lần gõ một ô là 1.

| Đêm | Tầng 0 | Tầng 1 | Sang tầng 3 | Tầng 3 | Tổng |
|---|---|---|---|---|---|
| **Đêm 1** | 3 (Có, Không, Xong) | 18 = Q1+Q5+Q6 (3) + gõ giá, gõ VWAP (2) + 4 vùng × 3 (12) + Chốt (1) | 1 | 13 | **35** (lần 3: 35) |
| **Đêm 2** | 3 | 12 = Sao chép (1) + Q1+Q5+Q6 (3) + gõ giá hiện tại (1, VWAP đã điền) + 2 vùng × 3 (6) + Chốt (1) | 1 | 13 | **29** (lần 3: 29) |

Phụ: lần đầu thêm 1 click "Lưu" ở hộp vốn. Từ ENTRY tới lệnh ghi sổ chỉ **3** (Vào lệnh, limit, Xác nhận) vì ô giá limit và giá khớp tự điền; thêm 1 "Khớp rồi". Hai chỗ thừa vẫn còn: "Sang tầng 3" sau Chốt (Chốt đã tự đẩy sang tầng 2) và bấm lại Canh/Bấm. Vòng 4 không giảm số thao tác; lợi ích của nó là thanh điện thoại gọn, chữ rõ, VWAP tự điền.

## (d) Điều còn muốn sửa (tối đa 5)

1. **Chữ thô "⟦halfNoteMin⟧ / ⟦halfNote⟧"** ở chip dưới thanh phán quyết khi SL ≥ 3 giá cỡ ½. Sửa trước đêm mai: lỗi nằm trong ca kèo B SL 3-4 giá.
2. **Nút "Kết phiên" bị nuốt cú bấm đầu và xám khi vừa gõ "Bạn cộng"**: cho nút luôn bấm được, hoặc ghi giá trị ngay khi gõ.
3. **Kiểm tra giá limit / giá khớp lệch xa giá vào** (cảnh báo khi lệch quá vài giá), hoặc chọn sẵn toàn bộ chữ trong ô khi bấm vào để gõ đè được.
4. **Bấm kịch bản tắt: đưa tấm bên dưới sang kịch bản vừa bấm** (hoặc làm tấm cũ mờ), và thống nhất tên "Khung giờ cấm" khắp nơi + gõ "cửa sổ" cũng ra trong Từ điển; thêm "SL bị quét", "hình dạng B".
5. **Giảm thao tác:** gộp "Sang tầng 3" vào Chốt (hoặc nút Chốt chuyển thẳng sang Kèo), và cho "Sao chép vùng" chép luôn VAL/VAH Âu hôm trước làm gợi ý mờ, đêm 2 sẽ còn khoảng 20 thao tác.

## (e) Điểm "muốn dùng đêm mai": 4,5 / 5 (lần 3: 4,4; lần 2: 4,0; lần 1: 3,5)

Cộng 0,1 so với lần 3: (1) điện thoại gọn hẳn (43 + 118 px, 19 % màn hình thay vì 35 %), đủ để tôi xem công cụ ngay trên điện thoại khi chart chạy; (2) A bật được lúc 20:45 mà không phải sửa giờ, giải thích rõ khi tắt; (3) sao chép vùng điền sẵn VWAP tuần, thông báo đúng; (4) Sổ hết chữ tắt khó hiểu; (5) Từ điển có VAH/VAL/POC/phá giả; (6) kèo cỡ ½ không chia được nay ghi thẳng "cỡ đủ, rủi ro 40 $"; (7) "gõ rồi bấm nút kế" ăn 30/30.

Không lên 4,7+ vì: chữ thô "⟦halfNoteMin⟧" ngay trong ca tôi hay vào làm tôi mất tin vào độ hoàn chỉnh; "Kết phiên" vẫn dính lỗi click bị nuốt; số thao tác không giảm (35 / 29); giá limit sai bậy được ghi vào sổ không cảnh báo. Sửa mục 1-2 trong (d) tôi cho 4,7; thêm 3-5 là 4,8.

## (f) README có đủ để tự bắt đầu không?

**Đủ để bắt đầu đêm đầu**, thiếu vài chỗ nhỏ. Có: link mở, cách cài, hộp vốn, đi từ tầng 0 đến 5 đúng thứ tự tôi đã đi thật (kể cả ba câu bắt buộc Q1/Q5/Q6, gõ giá để bias tự chọn, Canh rồi Bấm, "Quay lại Canh", ba trạng thái CHỜ/KHÔNG VÀO/ENTRY, phím tắt), đêm sau có Sao chép vùng, cách xuất sổ, đổi giờ mùa đông. Thiếu: (1) không nói "Chốt thẻ phiên" tự nhảy sang tầng Chế độ rồi còn phải bấm "Sang tầng 3"; (2) không nói ô giá limit và giá khớp đã tự điền (người đọc sẽ gõ đè và ra "41824182"); (3) không giải thích "chart A", "DMA", "bong bóng" là gì trên chart nào (README chỉ trỏ tới Hệ thống Đêm Vàng, không có link bấm được); (4) "Cách dùng" chưa ghi thời điểm hợp lý để thử (trước 20:30 cỡ ½; A chỉ bật sau 19:20); (5) mục "Cấu trúc/Lệnh" ở dưới là cho lập trình viên, người dùng chỉ cần đọc phần "Cách dùng" nên nên tách rõ.
