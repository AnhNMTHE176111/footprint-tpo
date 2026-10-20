# USER TEST 3 — Trạm Đêm Vàng 1.0.3 (trader mới học order flow/TPO 1 tháng, lần dùng thứ ba)

Cách thử: Playwright + Chromium, mở bản đã deploy https://anhnmthe176111.github.io/tram-dem-vang/ (Sổ → Cài đặt ghi "Phiên bản 1.0.3"), xóa localStorage rồi dùng như người mới (gặp hộp hỏi vốn). 1366×768 và 390×844. Mọi cú bấm dùng chuột thật (`mouse.move/down/up`), gõ bằng bàn phím thật. Giờ máy lúc thử 18:43–19:06 (trước 20:30, nên công cụ ở chế độ "mở ảo, cỡ ½"). Đêm thứ hai tôi giả lập bằng cách đặt đồng hồ trình duyệt sang 21/10 18:30 (cùng tuần). Nhập giả lập giống hai lần trước: VWAP tuần 4181, VAL Âu 4182, VAH Âu 4192, HVN 3 tuần 4200. Không đọc code. Ảnh trong `user-test-shots-3/` (khoảng 70 ảnh), hai bản Markdown xuất ra: `export-dem1.md`, `export-dem2.md`.

## (a) 10 điều của lần 2: đã sửa chưa?

| # | Điều lần 2 | Kết quả lần 3 | Bằng chứng |
|---|---|---|---|
| 1 | Click đầu sau khi gõ số bị nuốt | **Thỏa đáng (gần như hết).** Gõ biên độ rồi bấm "Đi ngang"/"Còn dốc": đo bằng chuột thật 5 lần xen kẽ, 5/5 ăn ngay lần đầu. Gõ "Giờ phá" rồi bấm "Sang tầng 3", gõ giá khớp rồi "Khớp rồi", gõ giá hiện tại rồi tick nến, gõ SL rồi "Đúng chỗ": đều ăn. Duy nhất 1 lần không ăn (lần đầu tiên, ca B đêm 1: gõ 1,8 rồi bấm "Đi ngang", nút có viền focus mà không chọn); 14 lần sau đều ăn, nên tôi coi là còn nghi 1 lần, không lặp lại được. | [16b](user-test-shots-3/16b-B-sau-dma.png) [38](user-test-shots-3/38-repro-1.png) |
| 2 | Vốn 2000 $ + cỡ ½ chặn gần hết kèo | **Đã sửa thỏa đáng.** Lần đầu mở có hộp "Vốn và rủi ro mỗi lệnh" (Để sau / Lưu). SL 2 giá và SL 3 giá đều ra ENTRY BUY, dòng ghi "cỡ ½ không chia được — 1 hợp đồng (tối thiểu)". SL 4 giá ra ENTRY, SL 5 giá ra KHÔNG VÀO kèm câu "SL tối đa 4,0 giá. Bỏ kèo, hoặc tăng vốn" và nút "Đổi vốn" ngay trên thanh. Kèo B SL 3 giá quen thuộc của tôi giờ vào được. Chưa thử lại "Tôi vẫn vào" khi 0 hợp đồng (IMPL-3 nói giữ nguyên). | [01](user-test-shots-3/01-mo-trang-hop-von.png) [17c](user-test-shots-3/17c-B-ENTRY.png) [56](user-test-shots-3/56-sl-5-gia.png) |
| 3 | Từ điển mở ở cuối, không tìm, "Mở Từ điển" không nhảy | **Đã sửa thỏa đáng.** Mở ra là đầu trang, con trỏ nằm sẵn trong ô "Tìm từ…", xếp chữ cái, gõ "moi" không dấu ra "mồi" + "tail thật", gõ bừa ra "Không có mục nào khớp". Từ "?" của DMA bấm "Mở Từ điển" thì nhảy đúng mục DMA và tô nền. Lỗi nhỏ còn lại: ô tìm dính trên đầu hộp che mất dòng tiêu đề "DMA" của mục vừa nhảy tới (chỉ thấy phần thân). | [40](user-test-shots-3/40-tu-dien-mo.png) [41](user-test-shots-3/41-tim-moi.png) [43](user-test-shots-3/43-tu-dien-nhay.png) |
| 4 | Mục Từ điển còn yếu (mồi, trap, bong bóng, DMA, R, hình dạng) | **Thỏa đáng một phần.** Nay 24 mục. "mồi" có ví dụ số (đỉnh 4210 một TPO khối lượng thấp = tail thật, đỉnh 4208 khối lượng dày = mồi), "trap" có ví dụ 4200 → 4194 → 4197, "R" có ví dụ sell 4193 SL 4195,4, "hình dạng profile" có đủ D/P/b/B/thin/chữ nhật. Còn chưa: DMA nói thẳng "không ghi tên đầy đủ" (đúng nhưng tôi vẫn không biết là đường nào); hình dạng B ghi "chưa mô tả riêng"; vẫn không có VA/VAH/VAL/POC (gõ "vah" chỉ ra mục "cạnh"), phá giả, cửa sổ cấm, SL bị quét; không có hình. | [41](user-test-shots-3/41-tim-moi.png) (nội dung các mục lấy từ hộp, không chụp riêng) |
| 5 | Số thao tác vẫn 42 | **Sửa một phần, có giảm thật.** Đêm 1 đường tối thiểu 34 thao tác, đêm 2 (có sao chép vùng) 29. Xem mục (c). | mục (c) |
| 6 | Kế hoạch ngược bias chốt im lặng | **Đã sửa thỏa đáng.** Bias BUY, gõ "nếu giá lên VAH Âu 4192 bị từ chối thì sell": ngay dưới ô hiện hộp vàng đậm "Kế hoạch đang ngược bias BUY. Vẫn chốt được, nhưng vào lệnh ngược bias phải ghi lý do." sát nút Chốt. Sửa thành "…thì buy" thì hộp biến mất. | [11](user-test-shots-3/11-ke-hoach-canh-bao.png) |
| 7 | Thanh trên vẫn dày | **Một phần; điện thoại tệ hơn.** Máy tính: chip "trước 20:30 · cỡ ½" thay câu dài, thanh vẫn 7-8 chip, cỡ ½ vẫn xuất hiện 2-3 chỗ (chip trên, banner tầng 2, chip "Cỡ ½ vì…" dưới). Điện thoại 390px: nút "Thẻ phiên" không còn đè chip và chip không bị cắt, nhưng chip xuống dòng nên thanh trên cao **105px** (lần 2: 43px), cộng thanh dưới ENTRY 189px = 294/844 px, tức 35% màn hình bị khóa. | [m03](user-test-shots-3/m03-tang1-dau.png) [m07](user-test-shots-3/m07-entry-dau.png) |
| 8 | "?" quá nén, đè đáp án, 28px | **Một phần.** "?" của Q1 giờ có đủ chữ (D/P/b/thin/chữ nhật) và hộp mở ra đẩy hàng nút xuống chứ không đè. "?" của Q3 vẫn chỉ một câu ("Single print chưa lấp là mục tiêu ưa thích. Nợ cũ trả trước."). Nút "?" vẫn 28×28 trên điện thoại. Không hình. | [62](user-test-shots-3/62-q1-help.png) [60](user-test-shots-3/60-q3-help.png) |
| 9 | Bấm kịch bản mờ không phản hồi; "Giờ phá"; HVN báo "giữa range" | **Một phần.** Bấm D mờ nay hiện bong bóng "Chưa có move rõ để gọi trap." Bấm A mờ hiện bong bóng "Cú phá trong 18:00–19:20 hay là phá giả…". C trên HVN nay báo đúng chuyện "Fade chỉ ở đúng cạnh VA Âu hoặc cạnh range; vùng này không phải cạnh". Còn: bong bóng chỉ sống vài giây và tấm bên dưới vẫn hiện kịch bản đang chọn trước đó; "Giờ phá" vẫn tự điền giờ hiện tại nên A luôn tắt vì "phá giả", tôi phải tự gõ 19:45 mới bật được A (người mới không biết); ô "Hướng lệnh" của C trên HVN còn nói "Vùng này chưa có phía. Chọn phía ở tầng 1 — Về tầng 1", lạc đề (HVN không bao giờ có phía). | [14](user-test-shots-3/14-bam-D-mo.png) [27](user-test-shots-3/27-C-hvn.png) [32](user-test-shots-3/32-A-chon.png) [33](user-test-shots-3/33-A-bat.png) |
| 10 | Chữ viết tắt còn sót | **Chưa sửa (đúng như IMPL-3 nói).** Sổ vẫn "U · bb giữ · Δ giảm · cạnh", "Chuỗi đêm 0 phá luật 1", chip "Phá luật 0/2", "SL liên tiếp 0/3", "Lệnh mở 0/1", thêm chip mới "Đã vào 0/2 lần ở vùng này" cũng không giải thích. Có một cải thiện nhỏ: tiêu đề cột Markdown nay ghi "4 kiểm tra (V/U · bb · Δ · cạnh)" (có thứ tự nhưng chưa nói bb, Δ là gì). Câu "Sau khi vào không đổi SL…" vẫn hiện sau khi đã dời be. "Giá hiện tại" ở tầng 4 **đã giữ được sau tải lại** (gõ 4184, tải lại vẫn thấy 4184, R +1). | [25](user-test-shots-3/25-so-sau-hoa.png) [57](user-test-shots-3/57-reload-giu-gia.png) `export-dem1.md` |

Sửa làm tệ hơn: một điều. Thanh trên điện thoại cao gấp 2,4 lần lần 2 (43 → 105px) khi chip xuống dòng.

Các kịch bản tôi đi lại và kết quả:

- **B (đêm 1):** vào ENTRY BUY 4182 · SL 4180 (2,0 giá) · TP 4188 · 1:3 · cỡ ½ · 1 hợp đồng. Bước Bấm ở 1366×768 vừa đúng một màn, không phải cuộn (ảnh 17c).
- **limit → khớp → be → "Chạm SL" sau be:** limit 4182, gõ giá khớp 4182, gõ giá hiện tại 4185,5 ("R hiện tại +1,75"), tick nến, "Đã dời SL về hòa vốn" (dòng "4180,0 → 4182,0 · SL đã về hòa vốn (be)" và nhắc kéo SL trên sàn). Nút đóng đổi tên thành "Chạm SL (đã ở hòa vốn)", giá thoát tự điền 4182, "R gợi ý: 0". Xác nhận: Sổ ghi R = 0, "Máy cộng: 0 R", chip "SL liên tiếp" vẫn 0/3. **Ra hòa, đúng.** [24](user-test-shots-3/24-cham-sl-sau-be.png) [25](user-test-shots-3/25-so-sau-hoa.png)
- **C:** tại HVN 3 tuần: KHÔNG VÀO, lý do đúng chuyện. Tại VAH Âu (bias BUY): hướng tự điền "sell", chip đỏ "Ngược bias: không được phép", thanh đỏ "Ngược bias — kịch bản này không được ngược bias". Tại VAL Âu: hướng tự điền "buy", chờ bong bóng/giá cách/biên độ. [28](user-test-shots-3/28-C-vah.png) [29](user-test-shots-3/29-C-val.png)
- **A (Vừa phá):** chọn "Phá lên" + cạnh VAH Âu + bước 1 Có + bước 2 Có thì "Chế độ hiệu lực: vừa phá · lên". Giờ phá mặc định = giờ hiện tại nên A tắt; sửa "Giờ phá" thành 19:45 thì A bật 3R, vùng "VAH Âu 4192,0 (tự điền)", hướng "buy (tự điền)". Khi chế độ vừa phá lên, C tự tắt kèm hộp vàng "Kịch bản này đang tắt: Đã có nến M5 đóng ngoài cạnh…". [31](user-test-shots-3/31-pha-len-cong-nhan.png) [33](user-test-shots-3/33-A-bat.png)
- **Xuất Markdown:** có "Thẻ phiên (18:46)", bảng lệnh, dòng cuối "Máy cộng: 0 R · Bạn cộng: 0 R · Lệnh phá luật: 0 · SL bị quét rồi tới TP: 0". Đêm 2 không có dòng "Kế hoạch" vì tôi không viết, đúng.
- **Sổ có "Chọn đêm":** hai nút ngày 2026-10-21 / 2026-10-20, xem được từng đêm riêng. Mới và tiện.

## (b) Chỗ kẹt mới

| # | Làm gì | Thấy gì | Kẹt / đoán ở đâu |
|---|---|---|---|
| 1 | Đêm 2, bấm "Sao chép vùng từ đêm 2026-10-20" | Chép được VWAP tuần 4181 và HVN 3 tuần 4200; thông báo "Đã chép 2 mục (VWAP tuần, HVN 3 tuần, Q1′)"; hộp vàng "Dưới 3 vùng". | (i) Nút nằm cuối mục vùng, cách đầu trang khoảng 1300px, người mới không thấy. (ii) Ô "VWAP tuần (tùy chọn)" ở bias **vẫn trống** dù vùng VWAP 4181 vừa chép, nên bias ra "chưa đủ dữ liệu", "Còn thiếu: VWAP tuần": tôi phải gõ lại hoặc bấm "Trên". (iii) Thông báo ghi "Q1′" dù đêm 1 tôi chưa hề trả lời Q1′, nên không rõ có chép hay không. (iv) Số vùng nhảy z1, z3, z4 vì HVN chép thành z2 nhưng nằm ở dòng "VÙNG CẤM". [53](user-test-shots-3/53-sau-sao-chep.png) |
| 2 | Đang ở tab "Canh" trả lời xong DMA | Tab tự nhảy sang "Bấm", lúc có lúc không tùy đã đủ các ô Canh hay chưa. Muốn đổi DMA phải tự quay về "Canh". | Không có dòng nào báo "đã đủ, chuyển sang Bấm". Lần 1 và 2 đã nêu, lần 3 vẫn chưa. |
| 3 | Bấm A khi đang chọn C | Bong bóng báo lý do A tắt rồi mất; tấm bên dưới vẫn nguyên kịch bản C và thanh đỏ của C. | Dễ đọc nhầm thanh đỏ là của A. [32](user-test-shots-3/32-A-chon.png) |
| 4 | Giờ phá | Ô tự điền 18:52 (giờ hiện tại), A bị tắt vì "phá giả". | Chưa sửa từ lần 2: tôi phải gõ giờ tương lai 19:45 để bật A, dễ hiểu thành "công cụ cho gian lận giờ". |
| 5 | C ngược bias | Ngoài chip đỏ "không được phép", vẫn hiện ô "Lý do ngược bias" cho gõ. | Một nơi vừa cấm vừa mời nhập lý do. [28](user-test-shots-3/28-C-vah.png) |
| 6 | SL sát 4 giá | ENTRY với "cỡ ½ không chia được — 1 hợp đồng (tối thiểu)". | SL 4 giá × 1 hợp đồng = 40 $ = 2 % vốn, tức đúng rủi ro cỡ **đầy**, không còn là ½. Công cụ nói rõ chữ "tối thiểu" nhưng không nói rủi ro thực tế gấp đôi mức ½. |
| 7 | Điện thoại 390px | Thanh trên 105px, thanh dưới ENTRY 189px. | Chỉ còn khoảng 550px cho nội dung; bước Bấm dài hơn một màn. [m07](user-test-shots-3/m07-entry-dau.png) |
| 8 | Điện thoại, mở Từ điển | Con trỏ nhảy vào ô tìm. | Trên điện thoại sẽ bật bàn phím, che gần nửa danh sách. |
| 9 | Từ điển, nhảy tới mục | Ô tìm đè dòng tiêu đề của mục đích. | Chỉ thấy phần thân. [43](user-test-shots-3/43-tu-dien-nhay.png) |
| 10 | Bong bóng thông báo ("Đã xóa kèo, bắt đầu lại", "Chưa có move…") | Nằm đè hàng nút "Không có / giữa move". | Thoáng qua nhưng che đáp án đang cần bấm. [28](user-test-shots-3/28-C-vah.png) |

## (c) Số thao tác từ mở trang tới ENTRY

Đo bằng kịch bản chạy thật, đường tối thiểu, kịch bản B. Mỗi lần click, mỗi lần chọn ô thả xuống, mỗi lần gõ một ô tính là 1.

| Đêm | Tầng 0 | Tầng 1 | Sang tầng 3 | Tầng 3 | Tổng |
|---|---|---|---|---|---|
| **Đêm 1** (mới hoàn toàn) | 3 (Có, Không, Xong) | 18 = Q1+Q5+Q6 (3) + gõ giá, gõ VWAP tuần để bias tự chọn (2) + 4 vùng × 3 (12) + Chốt (1) | 1 | 13 = B, vùng, buy, bong bóng, giá cách, gõ biên độ, DMA, U, thân nến, nến xác nhận, gõ giá vào, gõ SL, Đúng chỗ | **35** (34 nếu bấm "Trên" thay vì gõ 2 số) |
| **Đêm 2** (có "Sao chép vùng") | 3 | 12 = Sao chép (1) + 2 vùng VAL/VAH × 3 (6) + Q1+Q5+Q6 (3) + bias bấm "Trên" (1) + Chốt (1) | 1 | 13 | **29** |

Phụ: lần đầu thêm 1 click "Lưu" ở hộp hỏi vốn (+1 một lần duy nhất). Từ ENTRY tới lệnh ghi sổ thêm 3 (Vào lệnh, limit, Xác nhận) như lần 2.

So với lần 2 (42): giảm 7-8 nhờ chỉ còn 3 trong 7 câu hỏi bắt buộc (Q1, Q5, Q6; Q1′, Q2a, Q2b, Q3, Q4 không chặn Chốt) và nhờ gõ giá vùng một lần. Nếu trả lời đủ 7 câu như lần 2 thì đêm 1 là 39, tức giảm 3. Đêm 2 giảm thêm 5-6 nhờ sao chép vùng, nhưng sao chép chỉ giúp VWAP tuần + HVN 3 tuần (2 vùng, 6 thao tác), VAL/VAH Âu vẫn phải gõ lại mỗi đêm. Hai chỗ thừa vẫn còn: bước "Sang tầng 3" sau Chốt, và tab Canh → Bấm.

## (d) Việc cần sửa tiếp, xếp theo mức khó dùng

1. **Điện thoại: thanh trên 105px + thanh dưới 189px chiếm 35% màn hình.** Chip xuống dòng thay vì cuộn đã sửa lỗi đè nhưng làm thanh cao gấp 2,4 lần. Gợi ý: thu thanh trên điện thoại về 1 hàng (BIAS + giờ + 1 chip "!" gộp các cảnh báo), thanh dưới cho thu gọn thành 1 dòng + nút mở rộng.
2. **"Sao chép vùng" nên chép luôn số vào ô "VWAP tuần" của bias, và đặt nút lên đầu mục 1d (hoặc đầu tầng 1).** Hiện nút ở cuối trang, bias vẫn trống, thông báo nhắc Q1′ khi không có. Nếu cho chép cả VAL/VAH Âu hôm trước làm gợi ý mờ thì đêm 2 giảm thêm 6 thao tác.
3. **Cho Q2a, Q2b, Q3, Q4, Q1′ mặc định "Không rõ", và đặt hộp "Giờ phá" mặc định trống.** "Giờ phá" tự điền giờ hiện tại làm A luôn tắt: người mới phải gõ giờ giả. Nếu để trống thì bấm A phải nhập giờ thật, và thông báo nói rõ "nhập giờ nến M5 đóng ngoài cạnh".
4. **Nói rõ rủi ro thực của "cỡ ½ không chia được — 1 hợp đồng".** Ghi thêm "rủi ro thực 40 $ = 2 %, bằng cỡ đầy" khi SL ≥ 3,0 giá, hoặc cảnh báo vàng. Hiện nó vừa tuân luật cỡ ½ vừa vi phạm tinh thần ½.
5. **Từ điển: thêm VA/VAH/VAL/POC, phá giả, cửa sổ cấm, SL bị quét; sửa ô tìm không đè tiêu đề mục nhảy tới; không bật bàn phím tự động trên điện thoại.** DMA nên ghi tên chỉ báo/đường cụ thể trên chart của bạn.
6. **Giải thích chữ tắt trong Sổ:** "bb giữ · Δ giảm" (bong bóng giữ · delta giảm), "Chuỗi đêm 0 phá luật", 3 chip đếm "Phá luật 0/2", "SL liên tiếp 0/3", "Lệnh mở 0/1", chip mới "Đã vào 0/2 lần ở vùng này". Chỉ cần hover/"?" một câu mỗi chip.
7. **Bấm kịch bản đang tắt: chuyển tấm bên dưới sang kịch bản vừa bấm, hoặc giữ bong bóng đến khi đóng.** Hiện bong bóng mất sau vài giây còn tấm bên dưới vẫn là kịch bản cũ.
8. **Báo "đã đủ Canh, chuyển sang Bấm" và/hoặc đừng tự nhảy tab.** Tab tự nhảy lúc có lúc không là chỗ khó đoán nhất ở tầng 3.
9. **Chữa các câu lạc đề:** C trên HVN nói "Vùng này chưa có phía. Chọn phía ở tầng 1 — Về tầng 1"; C ngược bias vừa "không được phép" vừa cho gõ lý do; câu "Sau khi vào không đổi SL…" vẫn hiện sau khi đã dời be.
10. **Bong bóng thông báo nên nằm ở góc, không đè hàng nút đáp án**; nút "?" nên 40px trở lên trên điện thoại; "?" của Q3 và các câu còn lại thêm ví dụ giá hoặc hình.

## (e) Điểm "muốn dùng đêm mai": 4,4 / 5 (lần 2: 4,0; lần 1: 3,5)

Tôi cộng 0,4 vì bốn việc làm tôi ngại nhất lần trước đã hết hoặc gần hết: (1) click bị nuốt sau khi gõ số (14/15 lần ăn ngay, đủ để tin công cụ không hỏng giữa lúc chart chạy); (2) kèo B SL 3 giá vào được kèm câu SL tối đa và nút "Đổi vốn", cộng hộp hỏi vốn ngay lần đầu; (3) Từ điển mở ở đầu, có ô tìm không dấu, nhảy đúng mục; (4) kế hoạch ngược bias không còn chốt im lặng. Thêm: Chạm SL sau be ra hòa (0 R, không tính chuỗi SL), "Giá hiện tại" không mất sau tải lại, đêm 2 có sao chép vùng và chọn đêm trong Sổ.

Không lên 4,6 vì: (1) điện thoại tệ hơn (header 105px + thanh dưới 189px); (2) sao chép vùng không điền ô VWAP tuần của bias và nằm quá thấp, đêm 2 vẫn 29 thao tác; (3) chữ tắt trong Sổ và 3 chip đếm chưa giải thích; (4) Từ điển vẫn thiếu VA/VAH/VAL/POC, phá giả, cửa sổ cấm; (5) A vẫn bị "Giờ phá" tự điền chặn. Sửa (1) và (2) tôi cho 4,6; thêm chữ tắt và Từ điển đủ mục là 4,8.
