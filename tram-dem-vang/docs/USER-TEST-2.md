# USER TEST 2 — Trạm Đêm Vàng 1.0.2 (trader mới học order flow/TPO 1 tháng, lần dùng thứ hai)

Cách thử: Playwright + Chromium, mở bản đã deploy https://anhnmthe176111.github.io/tram-dem-vang/ (1.0.2), xóa localStorage trước khi bắt đầu, 1366×768 và 390×844. Giờ máy lúc thử 17:59–18:11 (trước 20:30, nên công cụ ở chế độ "mở ảo, cỡ ½"). Nhập giả lập giống lần 1: VWAP tuần 4181, VAL Âu 4182, VAH Âu 4192, HVN 3 tuần 4200, kịch bản B hấp thụ buy. Không đọc code, không đọc README. Ảnh nằm trong `user-test-shots-2/` (khoảng 97 ảnh, số thứ tự theo thời gian).

## (a) 10 điều lần 1: đã sửa chưa?

| # | Điều lần 1 | Kết quả lần 2 | Bằng chứng |
|---|---|---|---|
| 1 | Thuật ngữ không có chỗ dạy | **Sửa một phần.** Có nút "Từ điển" (22 mục) và mỗi "?" có thêm nút "Mở Từ điển". Nhưng "?" vẫn 1-2 dòng nén, không có ví dụ số hay hình; Từ điển mở ra đã cuộn xuống cuối (xem mục c); "Mở Từ điển" từ "?" không nhảy tới đúng mục. | [06-help-2](user-test-shots-2/06-help-2.png) [67-tu-dien-vua-mo](user-test-shots-2/67-tu-dien-vua-mo.png) [66](user-test-shots-2/66-tu-dien-tu-help.png) |
| 2 | ENTRY xanh mà cỡ lệnh 0 hợp đồng | **Đã sửa thỏa đáng.** SL 3 giá, cỡ ½: thanh đỏ "KHÔNG VÀO — Rủi ro cho phép chưa đủ 1 hợp đồng MGC với SL này — giảm SL hoặc bỏ kèo". SL 2 giá thì ra ENTRY BUY "1 hợp đồng". Hai phụ: (i) bấm "Tôi vẫn vào, chấp nhận phá luật" vẫn tạo lệnh **0 hợp đồng** (nhãn "phá luật") — [68](user-test-shots-2/68-0-hop-dong-van-vao.png); (ii) mặc định 2000$ khiến gần như không vào được (xem mục e). | [40](user-test-shots-2/40-B-sl3-0hopdong.png) [41](user-test-shots-2/41-B-entry.png) |
| 3 | Tải lại hiện ENTRY BUY cũ sau khi đóng lệnh | **Đã sửa.** Sau khi đóng lệnh + kết phiên + tải lại: tầng 3 hiện "Chọn một kịch bản đang bật để bắt đầu", thanh vàng "CHỜ thiếu: Chọn kịch bản", không còn ENTRY cũ. Tải lại giữa lúc có lệnh mở thì rơi đúng vào tầng 4. | [56](user-test-shots-2/56-tang3-sau-ket-phien.png) [46](user-test-shots-2/46-reload-khi-lenh-mo.png) |
| 4 | Bias bấm tay; kế hoạch ngược bias im lặng | **Sửa nửa đầu, chưa sửa nửa sau.** Có hai ô "Giá hiện tại" và "VWAP tuần": gõ 4184,5 và 4181 thì tự chọn "Trên" → BUY; gõ 4181,0 và 4181 thì ra "Sát (±2 giá)" → bias CHỜ kèm giải thích. Nhưng viết Kế hoạch 1 "sell ở VAH Âu" khi bias BUY rồi bấm Chốt: không cảnh báo gì. | [10-bias-tu-dong](user-test-shots-2/10-bias-tu-dong.png) [13](user-test-shots-2/13-ke-hoach-nguoc-bias.png) |
| 5 | Ô "Nến M1 cao nhất trong 5 nến" dễ nhập sai | **Đã sửa thỏa đáng.** Nhãn thành "Biên độ nến M1 cao nhất trong 5 nến (giá)". Gõ 4184,5 vào đó: thanh dưới báo "Biên độ hơn 20 giá — gõ biên độ nến, không gõ mức giá". | [22](user-test-shots-2/22-A-bien-do-sai.png) |
| 6 | Thanh trên quá nhiều chip | **Sửa một phần.** Điện thoại: đầu trang còn 1 hàng cao 43px (trước đây gần 1/4 màn hình) nhưng chip bị cắt ngang ("Cửa so…") và nút nổi "Thẻ phiên" đè lên chip. Máy tính: vẫn 7-8 chip; câu "Trước 20:30 vàng hay mở ảo (cú phá chưa đáng tin): cỡ ½" xuất hiện **3 lần** (thanh trên, tầng 2, thanh dưới), nền vàng đậm chiếm 2 hàng, thanh sticky che một phần nội dung khi cuộn. "HT 3.2" đã biến mất. | [01](user-test-shots-2/01-mo-trang.png) [m-f01](user-test-shots-2/m-f01-mo-trang.png) |
| 7 | Số câu hỏi / mã câu hỏi lệch | **Đã sửa.** Tiêu đề "Tám câu hỏi", câu đánh số Q1..Q8, thông báo "Còn thiếu: Q1 (hình hôm qua), Q7 (đóng hôm qua so với VA), Q8 (Âu dựng range), VWAP tuần, ít nhất 1 vùng" có tên kèm mã. | [08](user-test-shots-2/08-chot-thieu.png) |
| 8 | Tầng 4: SL mới sau be, "be" không viết đủ | **Đã sửa thỏa đáng.** Dòng SL ghi "4180,0 → 4182,0 · SL đã về hòa vốn (be)"; hộp vàng "Đã dời SL về hòa vốn (be): kéo SL trên sàn về 4182,0 ngay, công cụ không tự sửa lệnh trên sàn"; câu khó đọc được viết lại "Chỉ dời SL về giá vào (hòa vốn, gọi tắt be) khi giá đạt mốc dưới đây". Số hợp đồng ghi đúng 1. Còn lại: câu "Sau khi vào không đổi SL…" vẫn hiện sau khi đã dời; "Giá hiện tại" mất sau tải lại. | [49](user-test-shots-2/49-be.png) |
| 9 | Bạn cộng/Máy cộng; Markdown thiếu thẻ phiên | **Đã sửa.** Nhập 2,5 khác +3: chip đỏ "Lệch so với máy cộng — kiểm lại từng lệnh". Markdown mở đầu bằng "Thẻ phiên (18:01)": bias, chế độ, vùng, kế hoạch, hủy khi, và cuối có "Máy cộng +3 R · Bạn cộng +2,5 R". Còn "bb giữ · Δ giảm" ở bảng sổ và Markdown chưa giải thích. | [54](user-test-shots-2/54-ket-phien.png) `user-test-shots-2/export.md` |
| 10 | Nút bật/tắt, phản hồi, "?" | **Sửa phần lớn.** Bấm phím `2` hai lần không còn xóa kịch bản; kịch bản bị khóa (sau nến dài nhất) mờ, viền đứt nét, có hộp vàng "Kịch bản này đang tắt: …"; "Bỏ khóa" chạy; "Chế độ hiệu lực" có hộp vàng "Chưa công nhận: chọn hướng phá, cạnh vừa phá rồi tới bước 1 và bước 2" ngay đầu thẻ; tooltip ở tầng 0 đẩy nội dung xuống thay vì che. Còn: nút "?" 28px trên điện thoại (trước 22px, vẫn dưới 44px); tooltip "?" ở Q3 tầng 1 vẫn nằm đè đúng hàng nút trả lời của câu đó. | [60](user-test-shots-2/60-nen-dai-t3.png) [15](user-test-shots-2/15-vua-pha.png) [06-help-2](user-test-shots-2/06-help-2.png) |

Sửa làm tệ hơn: không có điều nào trong 10 điều. Nhưng phát hiện bug mới (có thể có từ trước): click bị nuốt sau khi gõ số, và Từ điển mở ở cuối (mục b, c).

## (b) Nhật ký bước mới và chỗ kẹt mới

| # | Làm gì | Thấy gì | Kẹt / đoán ở đâu |
|---|---|---|---|
| 1 | Mở lần đầu (xóa dữ liệu) | Vào "0 Trước". Tab đổi tên: Trước, Vùng, Chế độ, Kèo, Lệnh, Sổ. Kèo/Lệnh có ổ khóa. Thêm nút "Từ điển". | Rõ hơn lần 1. Chip "Phá luật 0/2", "SL liên tiếp 0/3", "Lệnh mở 0/1" vẫn không giải thích. |
| 2 | Cố tình bấm tab "Kèo" đang khóa | Hiện bong bóng "Chưa chốt thẻ phiên — không có thẻ thì không có lệnh." | Tốt, một câu nói đúng lý do. [02](user-test-shots-2/02-bam-keo-khoa.png) |
| 3 | Tầng 0: Có, "?" cửa sổ cấm, Không (tin lớn), gõ kịch bản nền, Xong | Hộp "?" đẩy nội dung xuống chứ không che. | "Hạng 1 / hạng 2" vẫn không được nói khác nhau gì trong "?" (có trong Từ điển mục "hạng vùng"). "Giờ tự dịch +1h khi Mỹ hoặc London sang giờ mùa đông" đọc không hiểu. [69](user-test-shots-2/69-tang0-help.png) |
| 4 | Tầng 1: bấm "Chốt thẻ phiên" khi thiếu | Nút mờ, cạnh nó ghi "Còn thiếu: …". Bấm không phản hồi thêm. | Chấp nhận được; nhưng bấm vào nút mờ không có phản hồi gì ngoài dòng nhỏ bên cạnh. |
| 5 | Tầng 1: 8 câu Q1-Q8, ô Giá hiện tại + VWAP tuần | Gõ cả hai số thì tự chọn Trên/Dưới/Sát, bias đổi ngay. | **Bug:** chuyển từ ô này sang ô kia lúc gõ, đôi khi con trỏ rơi về nền trang, chữ gõ không vào ô. Phải bấm lại. |
| 6 | Thêm 4 vùng | Mỗi vùng vẫn 3 thao tác (chọn loại, gõ giá, Thêm). Chọn HVN 3 tuần tự vào "VÙNG CẤM" ở thẻ phiên. | Chưa giảm. |
| 7 | Viết Kế hoạch 1 "sell ở VAH" khi bias BUY, Chốt | Chốt được, nhảy sang tầng 2. Không cảnh báo. | Chưa sửa. |
| 8 | Tầng 2: Vừa phá | Có hộp vàng "Chưa công nhận: chọn hướng phá…". Bước 1 = Có thì "Chế độ hiệu lực: chờ công nhận · lên"; bước 2 = Có thì "vừa phá · lên". | Đã hiểu. Cụm "Lần 1 chui lại ⇒ không đuổi, chờ lần 2" vẫn quá cô đọng. |
| 9 | Kịch bản A phá hồi (Vừa phá lên, cạnh z3 VAH Âu) | "Giờ phá" tự điền bằng giờ hiện tại (18:02) nên A bị tắt: "Cú phá trong 18:00–19:20 hay là phá giả — nghi trước, tin sau". Sửa Giờ phá thành 19:45 thì A "✔ bật". Chọn A thì vùng tự điền "VAH Âu 4192,0 (tự điền)" và hướng "buy (tự điền)". | Hay: không phải chọn vùng/hướng. Nhưng một người mới sẽ không biết phải sửa "Giờ phá" mới bật được A; lý do nói đúng mà vẫn khó hiểu. SL 4195 (sai phía): "SL nằm sai phía so với giá vào". SL 4190 (2,0) < nến 2,5: "SL 2,0 nhỏ hơn nến 2,5 — đẩy SL ra hoặc bỏ kèo". SL 4189,5: 0 hợp đồng, KHÔNG VÀO. [21](user-test-shots-2/21-A-chon.png) [28](user-test-shots-2/28-A-sl-nguoc-phia.png) |
| 10 | Chọn kịch bản D (mờ) bằng tay | Không có gì xảy ra; thanh dưới vẫn nói lý do của A đang chọn trước đó ("phá hồi chưa bật"). | **Kẹt:** bấm D, nhận câu trả lời về A. Nên hiện bong bóng "D đang tắt vì …". |
| 11 | Quay về Cân bằng, kịch bản C fade cạnh | C tại z3 VAH Âu: hướng tự điền "sell", hiện chip đỏ "Ngược bias: không được phép", thanh đỏ "Ngược bias — kịch bản này không được ngược bias". C tại z4 (HVN 3 tuần): "Giữa range không có lệnh — chỉ làm tại cạnh". | Câu thứ hai không đúng chuyện (HVN là vùng cấm fade, không phải "giữa range"). Chọn "Ngược phe, còn giữ" khi chưa chọn vùng/hướng: chỉ báo "CHỜ thiếu: Chọn vùng · Chọn hướng", không còn lý do vô nghĩa. [64](user-test-shots-2/64-C-z3.png) |
| 12 | Kịch bản B: z1, buy, bong bóng, cách vùng, biên độ, DMA | Đáp án xấu vẫn chặn đúng lý do: bong bóng ngược phe, "Từ 3 giá (ở lưng)", nhịp hồi V ("phe hồi đang thắng"). | Phần hay nhất vẫn giữ nguyên. |
| 13 | **Bug lặp lại:** gõ biên độ rồi bấm "Đi ngang" (DMA) | Bấm lần 1: không có gì. Đợi 1,5 giây vẫn không. Bấm lần 2: ghi nhận, tab nhảy sang "Bấm". | Tôi đã thử bằng chuột thật (mouse down/up), không phải lỗi của cách tự động. Chuỗi: gõ số → bấm nút liền sau bị nuốt. Giống hệt xảy ra ở ô Giá hiện tại. |
| 14 | Tab Canh → Bấm | Tự nhảy sang Bấm ngay khi trả lời DMA xong (có lúc không nhảy, tùy thứ tự trả lời). | Lần 1 đã nêu "tab tự nhảy", chưa thay đổi. Có thêm dòng mô tả "Trước/Sau khi nến xác nhận đóng" giúp hiểu Canh/Bấm là gì. |
| 15 | Bấm: U, thân nến "Giảm dần", nến xác nhận Đạt, giá vào 4182, SL 4179 | KHÔNG VÀO (0 hợp đồng). Đổi SL 4180 → ENTRY BUY 4182,0 · SL 4180,0 (2,0 giá) · TP 4188,0 · 1:3 · cỡ ½ · 1 hợp đồng. | Lúc ra 0 hợp đồng, tôi phải mở "Cỡ lệnh MGC" mới biết "Vốn 2000 $ · rủi ro 2 % = 20 $". 2% của 2000 là 40, không phải 20 (20 là sau khi giảm ½): đọc dễ nhầm. Thanh dưới không nói SL tối đa chấp nhận được (2 giá), cũng không nói chỗ chỉnh vốn (nằm sâu ở Sổ → Cài đặt). |
| 16 | "Tôi vẫn vào" khi KHÔNG VÀO | Hộp thoại "Vào lệnh phá luật?" kèm lý do, "2 lệnh phá luật thì tắt máy", Hủy / Vẫn vào, chấp nhận phá luật. Lỗi chấm kép đã hết. | Tốt. Chấp nhận thì lệnh 0 hợp đồng vẫn tạo ra. [42](user-test-shots-2/42-toi-van-vao.png) |
| 17 | Tầng 4: Vào lệnh, limit, Xác nhận, Khớp rồi, giá 4184 (R +1), 4185,5, tick nến, Đã dời, Chạm TP, Xác nhận đóng | Mọi bước đúng chỗ. Đóng lệnh tự nhảy sang Sổ. Dòng "Máy cộng: +3 R". | Rất trơn. Vẫn mất ô "Giá hiện tại" sau tải lại. |
| 18 | Sổ: Bạn cộng 2,5, Kết phiên, Tải Markdown | Xem mục (a) điều 9. | "Chuỗi đêm 0 phá luật: 1" vẫn khó hiểu. |
| 19 | Phím tắt `?` | Bảng có 1-4, B/S, U/V, Enter, N, Esc. | Ổn. |
| 20 | Điện thoại 390px, chạy lại toàn bộ đường tới ENTRY | Không tràn ngang (scrollWidth 390). Đầu trang 43px. Thanh dưới khoảng 150-190px (khoảng 20% màn hình), nút "?" 28×28, nút trả lời cao 40px. "Thẻ phiên" thành nút nổi, mở được. | Chip đầu trang bị cắt và nút "Thẻ phiên" nằm đè. [m-f05-entry](user-test-shots-2/m-f05-entry.png) [m-g03-help](user-test-shots-2/m-g03-help.png) |

## (c) Đánh giá Từ điển

Hình thức: nút "Từ điển" ở thanh trên mở hộp thoại 22 mục, mỗi mục 1-3 câu, không đánh theo thứ tự chữ cái, **không có ô tìm kiếm**, không ví dụ số, không hình. Bấm "Mở Từ điển" trong hộp "?" chỉ mở hộp chung, không nhảy tới đúng mục.

**Lỗi dùng được ngay:** mỗi lần mở, hộp thoại **đã cuộn xuống gần cuối** (cuộn 1469 trên tổng 2083 ở 1366×768; 1745 trên 2420 ở 390px). Việc đầu tiên tôi thấy là "naked POC … mở ảo", không có tiêu đề "Từ điển", không thấy các mục đầu (bias, nợ, mồi…). Người mới không biết còn phần phía trên. [67](user-test-shots-2/67-tu-dien-vua-mo.png)

Từng định nghĩa, đọc bằng mắt người mới 1 tháng:

| Mục | Giúp tôi hiểu không | Lý do |
|---|---|---|
| bias | Một phần | Có BUY/SELL/KHÔNG/CHỜ và "ngược bias phải ghi lý do", nhưng không nói khi nào ra KHÔNG hay CHỜ (CHỜ chỉ được nói ở mục VWAP tuần). |
| nợ | Có | Nói rõ "nợ giá, không phải nợ tiền". Sửa đúng điều lần 1. |
| mồi | Chưa | "Cực trị khối lượng dày, trông như đỉnh/đáy nhưng không phải bị từ chối thật": tôi vẫn không phân biệt được trên chart với đỉnh thật. Cần hình hai đỉnh cạnh nhau. |
| tail thật | Có | "1 TPO với khối lượng thấp" cụ thể; đặt cạnh "mồi" và "poor high" để so. |
| poor high / poor low | Có | "Từ 2 TPO, chưa bị từ chối dứt khoát": đối lập tốt với tail thật. |
| thin | Một phần | Nói "mỏng, đi một chiều" nhưng không nói nhận ra bằng gì trên profile. |
| trap (bẫy) | Chưa | "Sau một move rõ từ 5 giá, phe hồi thử rồi thất bại ở đỉnh nhịp hồi": quá dày, cần ví dụ với giá. |
| bong bóng | Chưa | "Tròn đặc là hấp thụ (vòng trắng…), tròn mờ từ 100 là lệnh lớn": phụ thuộc chỉ báo trên chart của người dùng mà từ điển không nói tên; "từ 100" là 100 cái gì. |
| DMA | Chưa | "Đường trên chart M1 dùng để đọc đà": vẫn không nói DMA viết tắt của gì, hay đường nào. Câu "đi ngang khi giá còn chạy là đà đang cạn" dùng được. |
| be (hòa vốn) | Có | Rõ, kèm mốc +1,5R / +1R. |
| hạng vùng | Một phần | Giải thích hạng 1 và hạng 2 nhưng không nói hạng nhỏ hơn thì bấm cỡ nhỏ hơn là bao nhiêu. |
| cạnh | Có | Kèm quy tắc "ở cạnh là cách vùng không quá 1 giá". |
| acceptance (công nhận cú phá) | Có | Hai bước rõ, trùng với Bước 1/Bước 2 ở tầng 2. |
| hấp thụ | Có | "Nỗ lực có, kết quả không" dễ nhớ. "Thân nến và độ lớn delta giảm dần qua 3 nến" còn hơi kỹ. |
| phá hồi | Có | |
| fade | Có | Gắn kịch bản C. |
| naked POC | Có | |
| HVN / LVN | Có | |
| single print | Có | |
| IB | Có | Có khung giờ. |
| VWAP tuần | Có | Có luật "sát" ±2 giá. |
| mở ảo | Có | Khung giờ cụ thể, giải thích vì sao giảm ½. |

Tóm lại: 14/22 giúp được, 5 chỉ giúp một phần, 4 chưa giúp (mồi, trap, bong bóng, DMA). Những mục chưa giúp đúng là những khái niệm "không nhìn thấy bằng mắt nếu chưa từng thấy" nên cần hình.

**Thiếu hẳn:** R (1R, 3R là gì), VA/VAH/VAL/POC, các hình dạng profile D / P / b / B / thin / Chữ nhật (tầng 1 Q1-Q2 dùng mà Từ điển không có; "?" của Q1 vẫn chỉ "D là đấu giá xong, chờ phá. P cân bằng ở đỉnh, b ngược lại"), phá giả, cạnh ngoài, cụm POC, cửa sổ cấm, nhịp hồi U/V, "SL bị quét".

## (d) Số thao tác từ mở trang tới ENTRY (kịch bản B, đo bằng kịch bản chạy thật, đường tối thiểu)

| Tầng | Thao tác | Số |
|---|---|---|
| 0 | Có, tin lớn Không, Xong tầng 0 | 3 |
| 1 | 8 câu Q1-Q8 (8), Trên/Dưới (1, hoặc gõ 2 số), 4 vùng × (chọn loại, gõ giá, Thêm) (12), gõ 3 ô kế hoạch (3), Chốt (1) | 25 |
| 2 | "Sang tầng 3" (chốt xong nhảy sang tầng 2, không phải tầng 3) | 1 |
| 3 | Kịch bản, vùng, hướng, bong bóng, cách vùng, gõ biên độ, DMA, U/V, thân nến-delta, nến xác nhận, gõ giá vào, gõ SL, SL đúng chỗ | 13 |
| | **Tổng tới khi thanh xanh ENTRY hiện** | **42** (32 click + 10 lần gõ) |
| | Cộng 1 click bị nuốt sau khi gõ (mục b, bước 13) | **43** |
| | Từ ENTRY tới lệnh ghi sổ: Vào lệnh, limit, Xác nhận | +3 (46) |

So với lần 1: **vẫn 42**. Không giảm. Các bản sửa tập trung vào đúng/sai chứ không vào số thao tác. Hai thay đổi đáng kể về cảm giác, không về con số: bias có thể gõ hai số thay vì một click (nhiều thao tác hơn nhưng có kiểm tra); và Canh → Bấm có lúc không phải click thêm.

## (e) 10 điều cần sửa tiếp, xếp theo mức khó dùng

1. **Click đầu tiên sau khi gõ số bị nuốt.** Gõ "1,8" vào ô biên độ rồi bấm "Đi ngang": không có phản hồi, phải bấm lần hai (đo bằng chuột thật, chờ 1,5 giây vẫn không). Tương tự khi chuyển giữa ô "Giá hiện tại" và "VWAP tuần": con trỏ rơi về nền trang. Đây là lỗi làm tôi nghi ngờ công cụ hỏng ngay giữa lúc chart đang chạy. (Nghi do vẽ lại giao diện khi ô mất focus, làm nút bị thay trước khi nhả chuột.)
2. **Vốn mặc định 2000$ + cỡ ½ + luật "SL không nhỏ hơn nến" gần như chặn mọi kèo trước 20:30.** Rủi ro cho phép 20$ = tối đa 2 giá SL cho 1 hợp đồng MGC. Kèo B quen thuộc của tôi (SL 3 giá) luôn KHÔNG VÀO. Thông báo không nói "SL tối đa 2 giá" hay chỉ chỗ chỉnh vốn (Sổ → Cài đặt, rất sâu). Câu "Vốn 2000$ · rủi ro 2% = 20$" đọc như sai toán (2% của 2000 là 40; 20 là sau ½). Và "Tôi vẫn vào" vẫn tạo lệnh 0 hợp đồng.
3. **Từ điển mở ở cuối, không có tìm kiếm, "Mở Từ điển" không nhảy tới mục đó.** Thêm: cuộn về đầu khi mở, ô tìm, nhảy tới mục, mục lục theo chữ cái.
4. **Mục Từ điển còn chưa giúp: mồi, trap, bong bóng, DMA (và chưa có R, hình dạng profile D/P/b/B/thin, nhịp hồi U/V).** Cần mỗi mục 1 ví dụ số hoặc 1 hình nhỏ; bong bóng/DMA nói tên chỉ báo và đường nào trên chart.
5. **Số thao tác vẫn 42.** Gợi ý: Q1-Q8 mặc định "Không rõ" và chỉ bắt đổi những câu quan trọng; ô vùng cho gõ nhanh "VWAP 4181"; sau Chốt nhảy thẳng tầng 3 (bỏ bước "Sang tầng 3"); đúng/sai tự điền khi chỉ có một đáp án hợp lệ.
6. **Kế hoạch ngược bias chốt im lặng** (Kế hoạch 1 "sell ở VAH" khi bias BUY). Nửa còn lại của điều 4 lần 1.
7. **Thanh trên vẫn dày, nhất là khi gần mở ảo:** banner vàng nhắc "mở ảo… cỡ ½" lặp 3 chỗ, 7-8 chip; trên điện thoại chip bị cắt ngang và nút "Thẻ phiên" nằm đè lên chip; thanh dưới khoảng 20% màn hình.
8. **"?" của câu hỏi vẫn quá nén và có chỗ che đáp án.** Q1: "D là đấu giá xong, chờ phá. P cân bằng ở đỉnh, b ngược lại. thin là một chiều, không đánh ngược" không có hình; "?" của Q3 nằm đè lên hàng nút trả lời của chính nó (ảnh 06-help-2). "?" 28px trên điện thoại vẫn nhỏ.
9. **Bấm kịch bản đang mờ không có phản hồi đúng:** bấm D (tắt) → không đổi gì, thanh dưới vẫn nói lý do của A; "Giờ phá" tự điền bằng giờ hiện tại làm A tắt vì "phá giả" mà người mới không biết phải sửa ô đó; HVN 3 tuần báo "Giữa range không có lệnh" thay vì "vùng cấm fade".
10. **Chữ viết tắt còn sót:** "bb giữ · Δ giảm" ở Sổ và Markdown, "Chuỗi đêm 0 phá luật: 1", "Lệnh mở 0/1", "SL liên tiếp 0/3", "Giờ tự dịch +1h khi Mỹ hoặc London sang giờ mùa đông"; "Sau khi vào không đổi SL…" vẫn hiện sau khi đã dời; "Giá hiện tại" ở tầng 4 mất sau tải lại.

## (f) Điểm "muốn dùng đêm mai": 4,0 / 5 (lần 1: 3,5)

Tôi cộng 0,5 điểm vì ba lỗi làm tôi tin nhầm lần trước đã hết: ENTRY với 0 hợp đồng thành KHÔNG VÀO, tải lại không bắn lại ENTRY cũ, bias tự tính từ hai số tôi gõ thay vì bấm bừa Trên/Dưới. Đáp án xấu vẫn bị chặn kèm lý do cụ thể (phần tôi thích nhất), đã thêm thông báo lỗi nhập (biên độ, SL sai phía), tầng 4 rõ hơn nhiều (SL mới sau be, nhắc kéo SL trên sàn), Markdown đủ thẻ phiên để ôn đêm đó.

Không lên 4,5 vì bốn việc: (1) click bị nuốt sau khi gõ số làm tôi nghi công cụ; (2) mặc định 2000$ khiến kèo thường ngày của tôi không vào được mà công cụ không chỉ đường chỉnh; (3) Từ điển mở ở cuối và bốn khái niệm khó nhất (mồi, trap, bong bóng, DMA) vẫn chưa giúp được; (4) vẫn 42 thao tác để tới ENTRY. Sửa (1) và (2) là tôi cho 4,3; thêm Từ điển cuộn đúng + có hình cho 4 mục khó là 4,6.
