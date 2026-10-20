# USER TEST 1 — Trạm Đêm Vàng (góc nhìn trader mới học order flow/TPO 1 tháng)

Cách thử: Playwright + Chromium, mở `index.html` (file://) ở 1366×768, thêm 390×844 cho điện thoại. Giờ máy lúc thử là 09:00–09:13 sáng (ban ngày, trước 20:30), nên công cụ luôn ở chế độ "mở ảo, cỡ ½". Không đọc code, không đọc README. Ảnh nằm trong `docs/user-test-shots/`. Nhập liệu giả lập: VWAP tuần 4181, VAL Âu 4182, VAH Âu 4192, HVN 3 tuần 4200.

Ghi chú về lúc thử: có một lần mất dữ liệu giữa các lần chạy, nguyên nhân là do cách tôi thử (đóng trình duyệt ngay, hai tiến trình dùng chung hồ sơ), KHÔNG phải lỗi công cụ. Sau khi sửa cách thử, tải lại trang giữ nguyên dữ liệu (xác nhận ở bước 14).

## (a) Nhật ký từng bước

| # | Làm gì | Thấy gì | Kẹt / đoán ở đâu | Ảnh |
|---|---|---|---|---|
| 1 | Mở lần đầu | Rơi đúng vào "0 Trước", tiêu đề "Trước khi mở chart — làm trước 18:00". Thanh trên cùng có 7 ô nhỏ (giờ, cửa sổ cấm, BIAS, phá luật 0/2...). Tầng 3 và 4 có ổ khóa. | Biết ngay phải làm gì tiếp: mất khoảng 10 giây. Nhưng 7 ô trên cùng đọc không hiểu hết: "mở ảo (HT 3.2): cỡ ½", "SL liên tiếp 0/3", "Lệnh mở 0/1". HT 3.2 là gì? Phải đoán là "Hệ thống mục 3.2". | [01](user-test-shots/01-mo-trang.png) |
| 2 | Tầng 0: bấm "Có" tỉnh táo, bấm "?" ở Cửa sổ cấm, "Không" cho tin lớn, gõ một dòng kịch bản nền | Tooltip "?" hiện đè lên đúng các dòng cửa sổ cấm mà nó đang giải thích. Nút "Xong tầng 0" nằm cuối trang, phải kéo xuống. | "hạng 1 / hạng 2" ở cửa sổ cấm: không biết hạng khác nhau gì. "NYSE mở 20:30: luôn bật" thì hiểu. | [02](user-test-shots/02-tang0-tinhtao.png) [03](user-test-shots/03-tang0-help.png) |
| 3 | Tầng 1: đọc 1a, trả lời câu hỏi, đọc "?" từng câu | 1a là 6 ô tick "đã kẻ xong". Câu hỏi là các nút bấm. Chọn xong, Bias tự ra SELL/BUY. | Tiêu đề nói "Sáu câu hỏi" nhưng đếm được 8 câu. Giá VWAP tuần 4181 chỉ nhập được ở "Thêm vùng", còn "giá hiện tại so với VWAP tuần" thì tự bấm Trên/Dưới, công cụ không hỏi giá hiện tại nên không tự đối chiếu. Tôi bấm "Dưới" bừa và ra SELL, đến tầng 3 mới biết hậu quả. Nút Chốt báo "Còn thiếu: Q1, Q5, Q6, VWAP tuần" nhưng câu hỏi không đánh số: phải đoán Q1 là hình dạng profile hôm qua. | [06](user-test-shots/06-tang1.png) [07](user-test-shots/07-tang1-cau-hoi.png) |
| 4 | Thêm 4 vùng bằng ô chọn + gõ giá + "Thêm vùng" | Mỗi vùng ra một dòng z1..z4 với nhãn hạng. HVN 3 tuần tự vào "VÙNG CẤM" ở thẻ phiên. | Hay: tôi không phải tự biết HVN là cấm fade. Nhưng mỗi vùng tốn 3 thao tác, 5 vùng thì 15 thao tác. Tiêu đề "Vùng (4/5)" và "chọn 3–5 vùng" nhưng chỉ có 1 vùng vẫn chốt được ở bước sau. | [09](user-test-shots/09-vung-4.png) |
| 5 | Gõ Kế hoạch 1, 2, Hủy khi, bấm Chốt thẻ phiên | Nút hết mờ, báo "Đã chốt thẻ phiên", tự nhảy sang tầng 2, thẻ phiên bên phải có đủ kế hoạch. | Tôi cố tình viết Kế hoạch 1 là "buy ở VWAP tuần" trong khi bias SELL: công cụ im lặng, không cảnh báo mâu thuẫn. Trader mới dễ tự lừa mình ở chỗ này. | [11](user-test-shots/11-chot-the.png) |
| 6 | Tầng 2: Cân bằng, rồi Vừa phá | Cân bằng là mặc định. Vừa phá hiện thêm: Hướng phá, Cạnh vừa phá, Giờ phá, Bước 1, Bước 2, nút "Chui lại trong (phá hụt)". | Bấm "Vừa phá" xong ô "Chế độ hiệu lực" vẫn ghi "cân bằng" tới khi chọn hướng + cạnh: tưởng nút hỏng. Dòng "Chọn hướng phá và cạnh vừa phá" nằm cuối thẻ, ngoài màn hình. Bước 1 = Có thì hiện "chờ công nhận · lên", Bước 2 = Có thì thành "vừa phá · lên". Tôi hiểu nhờ diễn biến trên màn hình, không phải nhờ chữ. | [12](user-test-shots/12-vua-pha.png) [14](user-test-shots/14-buoc2-co.png) |
| 7 | Tầng 3: chọn B (Hấp thụ), vùng z1, hướng buy lúc bias SELL | Thanh dưới màn hình đỏ: "KHÔNG VÀO — Ngược bias chỉ được ở High / Low hôm qua có tail thật hoặc single print đúng phía". | Phản ứng rõ, đỏ, một câu lý do. Nhưng lý do dùng "tail thật", "single print" mà tôi chưa chắc hiểu. Tôi quay lại đổi bias sang BUY (thẻ ghi "1 lần sửa") để đi tiếp: một cú bấm là "chữa" được bias, cảm giác như lách luật. | [21](user-test-shots/21-B-buy-bias-ok.png) |
| 8 | Chọn đáp án xấu: "Ngược phe, còn giữ", "Từ 3 giá (ở lưng)", nhịp hồi V | Mỗi lần thanh dưới đỏ với đúng lý do: "Bong bóng to gần nhất đứng phe ngược lại", "Giá đã đi từ 3 giá khỏi vùng — ở lưng, không vào", "Nhịp hồi hình V — phe hồi đang thắng". Đổi lại đáp án tốt thì về vàng "CHỜ thiếu: ...". | Phần hay nhất của công cụ. Thiếu sót: khi chưa chọn hướng lệnh mà đã báo "bong bóng đứng phe ngược" thì lý do vô nghĩa (ngược so với hướng nào?). | [21](user-test-shots/21-B-buy-bias-ok.png) [23](user-test-shots/23-B-xau-cach3.png) [27](user-test-shots/27-B-V-xau.png) |
| 9 | Điền hết Canh + Bấm tới ENTRY | Câu hỏi hiện dần (U/V, thân nến-delta, nến xác nhận, giá vào/SL/TP, SL đúng chỗ). Tôi gõ nhầm ô "Nến M1 cao nhất trong 5 nến" thành 4184,5, thanh đỏ "SL 3,0 nhỏ hơn nến 4184,5". | Ô đó có đơn vị "giá", placeholder 0,0: tôi hiểu là mức giá đỉnh nến, thật ra là độ dài nến (2,5 giá). Chỉ ngộ ra vì thông báo lỗi in lại số tôi gõ. Dòng "Nhập giá vào và SL ở bước Bấm" nói một đằng, trong khi các ô giá vào/SL đã có sẵn ngay cuối trang. Tab tự nhảy Canh sang Bấm làm tôi tưởng mất câu hỏi. | [26](user-test-shots/26-B-cuoi-hoi.png) [29](user-test-shots/29-B-entry.png) |
| 10 | Thấy ENTRY BUY | Thanh xanh lớn "ENTRY BUY 4182,0 · SL 4179,0 (3,0 giá) · TP 4191,0 · 1:3 · cỡ ½" + nút trắng "Vào lệnh". | Rất đã. Nhưng mở "Cỡ lệnh MGC" thì ghi **0 hợp đồng** (vốn 2000$, rủi ro 2% = 20$, mỗi hợp đồng rủi ro 30$). ENTRY xanh mà cỡ lệnh 0 là mâu thuẫn. | [30](user-test-shots/30-B-co-lenh.png) |
| 11 | Bấm "Tôi vẫn vào (phá luật)" khi đang KHÔNG VÀO | Hộp thoại "Vào lệnh phá luật?" kèm lý do và "2 lệnh phá luật thì tắt máy". Hai nút Hủy / Vẫn vào, chấp nhận phá luật. | Rõ, ma sát vừa đủ. Lỗi nhỏ: dấu chấm kép "thắng.." trong câu. Tôi bấm Hủy. | [32](user-test-shots/32-toi-van-vao.png) |
| 12 | Tầng 4: Vào lệnh, limit, Xác nhận, "Khớp rồi", nhập giá 4187, tick nến đóng ngoài vùng, "Đã dời về hòa", "Chạm TP", "Xác nhận đóng" | Mỗi bước nút hiện đúng lúc. Gõ giá thì hiện "R hiện tại +1,67". Nút "Đã dời về hòa" mờ tới khi có giá + tick. | "be" không bao giờ được viết đủ (đoán là hòa vốn nhờ chữ "dời về hòa"). Sau "Đã dời về hòa" dòng SL ghi "4179,0 · SL đã về hòa": SL mới là bao nhiêu? Không in 4182, cũng không nhắc tôi tự kéo SL trên sàn. Câu "Không sửa SL sau khi vào. Chưa be thì không sờ SL." đọc ba lần mới hiểu. Thẻ lệnh ghi "Số hợp đồng 0" suốt từ lúc khớp tới lúc đóng. | [35](user-test-shots/35-tang4-cho-khop.png) [36](user-test-shots/36-khop.png) [38](user-test-shots/38-be.png) [39](user-test-shots/39-dong-tp.png) |
| 13 | Tầng 5: xem sổ, nhập "Bạn cộng", Kết phiên, xuất Markdown | Đóng lệnh xong tự nhảy sang Sổ. Có 1 dòng, "Máy cộng +3 R", ô "Bạn cộng", 4 con số cuối tuần. Tải được `.md`. | Không hiểu sao phải tự cộng R khi máy đã cộng. Nhập 2,5 khác 3 của máy: không cảnh báo. Cột "4 kiểm tra" ghi "U · bb giữ · Δ giảm · cạnh" (bb đoán là bong bóng). File Markdown chỉ có bảng lệnh, KHÔNG có thẻ phiên, bias, vùng, kế hoạch. | [40](user-test-shots/40-sau-dong.png) [41](user-test-shots/41-ban-cong-lech.png) [43](user-test-shots/43-ket-phien.png) `user-test-shots/export.md` |
| 14 | Tải lại trang | Thẻ phiên, đáp án, lệnh, sổ còn nguyên. | Nhưng sau khi đã đóng lệnh và kết phiên, tải lại lại rơi vào tầng 3 và hiện lại thanh xanh "ENTRY BUY ... Vào lệnh" như chưa có gì: dễ vào lệnh lần hai. Không nhớ tầng đang đứng. Ô "Giá hiện tại" ở tầng 4 mất sau khi tải lại. | [44](user-test-shots/44-phim-tat.png) |
| 15 | Phím tắt | Bấm `?` mở bảng phím tắt tầng 3 (1-4 kịch bản, B/S hướng, U/V nhịp hồi, Enter, N, Esc). Chạy được. | B/S/1-4 là nút bật-tắt: bấm lần hai là bỏ chọn, nên lỡ bấm hai lần sẽ xóa đáp án mà không hay. | [45](user-test-shots/45-phim-tat-bang.png) |
| 16 | Khóa "nến dài nhất phiên" | Bấm ở tầng 2: mọi kịch bản tắt, hiện "Mở lại 09:17" và "Bỏ khóa". Sang tầng 3 thanh đỏ nêu lý do. | Hay. Nhưng nút B ở tầng 3 vẫn sáng như chọn được dù đang bị khóa. | [52](user-test-shots/52-nen-dai.png) [53](user-test-shots/53-nen-dai-t3.png) |
| 17 | Điện thoại 390px | Không tràn ngang. Thẻ phiên thành nút nổi "Thẻ phiên". | Phần đầu (7 chip xếp dọc) chiếm gần 1/4 màn hình, thanh dưới gần 1/5: chỉ còn khoảng nửa màn hình cho nội dung. Nút "?" chỉ 22px, khó bấm bằng ngón tay. | [47](user-test-shots/47-m-tang3.png) [49](user-test-shots/49-m-tang1.png) [50](user-test-shots/50-m-so.png) |

## (b) Từ / khái niệm không hiểu hoặc gây hiểu nhầm

| Từ / chỗ | Gặp ở đâu | Vấn đề |
|---|---|---|
| mở ảo (HT 3.2) | thanh trên | Không biết "mở ảo", "HT 3.2". Đoán là "cổng NYSE chưa mở, ít thanh khoản nên giảm cỡ ½". |
| hạng 1 / hạng 2 / cạnh / cấm fade / trung tính / chỉ mục tiêu | loại vùng ở tầng 1 | Nhãn cạnh tên vùng nhưng không có chỗ giải thích đủ các loại. "Cạnh" khác "hạng" thế nào? |
| Tail thật, Mồi, Poor high/low | câu Đỉnh/Đáy hôm qua | "?" của hai câu hiện cùng một đoạn; "Mồi" chỉ được nhắc nửa dòng. Mới học TPO 1 tháng thì tail/poor còn mơ hồ. |
| Nợ | câu "Nợ chưa lấp", thẻ phiên | Ở đây là single print/poor chưa bị lấp lại, dễ tưởng nợ tiền. |
| thin, Chữ nhật, P, b, B, D | hình dạng profile | Chỉ có một "?" gộp ("D là đấu giá xong, chờ phá. P cân bằng ở đỉnh..."), không có hình minh họa. |
| Bias | tầng 1c | Giữ tiếng Anh, chưa giải thích. |
| Q1, Q5, Q6 | thông báo "Còn thiếu" khi chốt | Câu hỏi trên màn hình không đánh số. |
| "Sáu câu hỏi" | tiêu đề 1b | Thực tế có 8 câu, tưởng mình bỏ sót. |
| Phá hồi, Trap | kịch bản A, D | Không được định nghĩa trong công cụ; mới học không biết trap là gì. |
| Hấp thụ | kịch bản B | Chỉ hiểu mơ hồ; dòng thu gọn "Hấp thụ · mục tiêu 3R · be +1,5R" nén quá. |
| 3R, 2R, be +1,5R, be | nút kịch bản, tầng 4 | R tôi biết; "be" không bao giờ được viết đủ. |
| chờ công nhận / chui lại / phá hụt / nhịp hồi giữ được cạnh | tầng 2 Vừa phá | Mỗi cụm một kiểu từ; "Lần 1 chui lại ⇒ không đuổi, chờ lần 2" quá cô đọng. |
| Canh / Bấm | hai tab tầng 3 | Tiếng lóng ("Canh" = theo dõi, "Bấm" = nhấn lệnh). Tab tự nhảy khi trả lời xong. |
| Bong bóng (bb) | tầng 3, sổ | Khái niệm lạ; "bb" viết tắt ở sổ. |
| DMA | tầng 3 | Không nói DMA là gì. |
| "Nến M1 cao nhất trong 5 nến", đơn vị "giá" | tầng 3 | Dễ hiểu thành mức giá đỉnh nến; thật ra là độ dài nến. |
| "Delta đảo dấu từ nửa nến lớn nhất của move" | Nến xác nhận đạt chuẩn | Câu quá dày; tôi tick "Đạt" mà không chắc. |
| Vùng đang chọn 0/2, Lần thứ 2 tại vùng | thanh trên, dưới ô vùng vào lệnh | Không biết nghĩa. |
| Bạn cộng / Máy cộng | tầng 5 | Không biết vì sao có hai số, số nào là số thật. |
| Cỡ lệnh MGC · 0 hợp đồng | tầng 3, tầng 4 | Vẫn cho vào lệnh với 0 hợp đồng. |

## (c) Số click / thao tác từ mở trang tới ENTRY

Đường tối thiểu, người dùng làm lần đầu, chế độ Cân bằng, kịch bản B, 4 vùng, không tick 1a:

| Tầng | Thao tác | Số |
|---|---|---|
| 0 | Có (tỉnh táo) 1, tin lớn Không 1, "Xong tầng 0" 1 | 3 |
| 1 | 8 câu hỏi 8, VWAP Trên/Dưới 1, 4 vùng × (chọn loại, gõ giá, Thêm) 12, gõ 3 ô kế hoạch 3, Chốt thẻ 1 | 25 |
| 2 | Bấm sang tầng 3 | 1 |
| 3 | Kịch bản 1, vùng 1, hướng 1, bong bóng 1, cách vùng 1, gõ độ dài nến 1, DMA 1, U/V 1, thân nến-delta 1, nến xác nhận 1, gõ giá vào 1, gõ SL 1, SL đúng chỗ 1 | 13 |
| | **Tổng tới khi thanh xanh ENTRY hiện** | **42** (khoảng 30 click + 12 lần gõ) |
| | Từ ENTRY tới lệnh ghi vào sổ: Vào lệnh, limit, Xác nhận | +3 |

Ghi chú: thử "Vừa phá" thì thêm 6 thao tác ở tầng 2. Tầng 0 và 1 làm trước 18:00 nên 28 thao tác là chấp nhận được; 13 thao tác ở tầng 3 giữa lúc chart đang chạy thì nặng, và mỗi kèo mới trong đêm phải làm lại gần hết.

## (d) 10 điều cần sửa, xếp theo mức làm tôi khó dùng

1. **Thuật ngữ không có chỗ dạy.** Bias, nợ, mồi, tail thật, poor, thin, hấp thụ, trap, phá hồi, bong bóng, DMA, be, cạnh/hạng. Mỗi "?" chỉ 1-2 dòng cô đọng, vài "?" trùng nội dung. Mỗi thuật ngữ cần "là gì + 1 ví dụ số/hình nhỏ", nhất là ở mức hướng dẫn "Mới".
2. **ENTRY xanh mà cỡ lệnh 0 hợp đồng.** Mâu thuẫn trực tiếp. Phải báo to khi cỡ lệnh làm tròn xuống 0 ("SL 3 giá = 30$/hợp đồng, vượt 20$ rủi ro: giảm SL hoặc bỏ") và không cho "Xác nhận vào lệnh" với 0 hợp đồng.
3. **Sau khi đóng lệnh / kết phiên, tải lại lại hiện ENTRY BUY cũ với nút "Vào lệnh".** Dễ vào lệnh lần hai. Nên xóa/khóa kèo sau khi lệnh đã đóng, và nhớ tầng đang đứng khi tải lại.
4. **Bias do người dùng bấm tay "Trên/Dưới", không nhập giá hiện tại.** Bấm nhầm là sai cả đêm (tôi đã bấm nhầm). Nên có ô giá hiện tại để công cụ tự so với VWAP tuần. Kế hoạch 1 ngược bias (buy trong khi SELL) cũng nên bị nhắc ngay lúc chốt thẻ.
5. **Ô "Nến M1 cao nhất trong 5 nến" dễ nhập sai** (tôi nhập mức giá). Đổi nhãn thành "Độ dài nến M1 lớn nhất trong 5 nến (giá)" và chặn giá trị phi lý.
6. **Thanh trên cùng quá nhiều chip, nhất là trên điện thoại**, và có chip không hiểu ("mở ảo (HT 3.2)", "Vùng đang chọn 0/2"). Ở 390px, đầu trang + thanh dưới chiếm khoảng 45% màn hình. Gom còn 2-3 chip quan trọng.
7. **Số câu hỏi và mã câu hỏi lệch nhau.** "Sáu câu hỏi" nhưng 8 câu; thông báo thiếu ghi Q1/Q5/Q6 mà câu không đánh số. Đánh số Q1..Q8 trên giao diện và sửa tiêu đề.
8. **Tầng 4 sau "dời về hòa" không nói SL mới là bao nhiêu và không nhắc kéo SL trên sàn.** Viết đủ "hòa vốn (be)". Câu "Chưa be thì không sờ SL" rất khó đọc.
9. **Sổ: "Bạn cộng" và "Máy cộng" gây rối; Markdown thiếu thẻ phiên/bias/vùng/kế hoạch.** Nếu hai số lệch nên hiện cảnh báo; Markdown nên kèm thẻ phiên để ôn đêm đó.
10. **Nút bật/tắt dễ xóa nhầm và thiếu phản hồi:** B/S/1-4 bấm hai lần là bỏ chọn; kịch bản bị khóa (sau nến dài) nhìn vẫn như chọn được; "Chế độ hiệu lực" không đổi tới khi chọn đủ ở tầng 2; dấu chấm kép "thắng.."; tooltip "?" che đúng nội dung nó giải thích; "?" 22px trên điện thoại.

## (e) 5 điều hay, nên giữ

1. **Thanh dưới màn hình nói "KHÔNG VÀO — lý do" hoặc "ENTRY BUY ..."**: một câu, màu đỏ/vàng/xanh, đổi ngay mỗi lần bấm. Đây là lý do tôi muốn dùng: nó thay cho cái đầu đang bốc đồng.
2. **Đáp án xấu bị chặn kèm lý do cụ thể** (bong bóng ngược phe, giá ở lưng từ 3 giá, nhịp hồi V, ngược bias, ba nến sau nến dài nhất), và "Tôi vẫn vào (phá luật)" có hộp thoại nhắc "2 lệnh phá luật thì tắt máy". Có ma sát đúng chỗ, không cấm tuyệt đối.
3. **Câu hỏi tầng 3 hiện dần và thanh "CHỜ thiếu: ..." chỉ ra ba thứ còn thiếu**, kèm dấu chấm tiến độ. Không bị ngợp dù tổng cộng nhiều câu.
4. **Thẻ phiên cố định bên phải** (bias, vùng, vùng cấm, kế hoạch, hủy khi) luôn trong tầm mắt, kèm nhãn "Đã chốt lúc ... / 1 lần sửa" để tự thấy mình đã sửa luật.
5. **Khóa tầng 3 khi chưa chốt thẻ, tự nhảy tầng kế, tự điền SL/R:R/TP gợi ý/mốc dời hòa (4186,5 = +1,5R) và tự báo R hiện tại khi gõ giá**; dữ liệu giữ khi tải lại; phím tắt chạy; xuất được Markdown/JSON/CSV.

## (f) Điểm "muốn dùng đêm mai": 3,5 / 5

Tôi muốn dùng lại vì thanh phán quyết và các lý do chặn làm tôi chậm lại đúng lúc, và thẻ phiên bắt tôi viết ra trước khi nhìn chart. Điều kéo điểm xuống là ngày đầu: khoảng 42 thao tác tới ENTRY, hàng chục chữ chưa quen mà phần giải thích quá ngắn, và ít nhất hai chỗ làm tôi tin nhầm (bias bấm tay bấm nhầm, ENTRY với 0 hợp đồng). Nếu sửa ba điều đầu của mục (d) và có mức "hướng dẫn Mới" giải thích từng thuật ngữ kèm ví dụ số, tôi cho 4,5/5.
