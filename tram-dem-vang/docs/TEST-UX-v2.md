# Kiểm thử trải nghiệm Trạm Đêm Vàng 2.0.0 (người trade M1 vàng, mới học 1–2 tháng)

Ngày 2026-10-20. Bản `file://` của repo (giống bản trên Pages), Playwright + chuột thật, 1366×768 và 390×844, xóa localStorage trước khi chạy, giờ giả lập 21:30 VN, lịch tin tắt (nên có thanh đỏ "không có lịch tin", không tính là lỗi). Ảnh: `docs/test-ux-v2/*.png`. Không sửa code, không commit.

Lưu ý phương pháp: số thao tác là **đếm thật** từ kịch bản; số giây là **ước lượng theo mô hình** (bấm 1 s, ô số 2,5 s, một lần cuộn 1 s), chưa phải người thật bấm. Thời gian đọc chart và quyết định không tính.

## (a) Nhật ký từng bước và chỗ kẹt

1. **Mở lần đầu** ([01](test-ux-v2/01-lan-dau.png)): hộp "Vốn và rủi ro" chặn màn hình, Lưu là xong. Tầng 0: "Có" rồi "Xong tầng 0" (2 bấm). Ổn.
2. **Tầng Vùng** ([02](test-ux-v2/02b-tang1.png)): nhãn "Ba câu hỏi" nhưng hiện Q1, Q5 và một câu không số, không biết Q2–Q4 đâu. Gõ giá hiện tại 4178 và VWAP tuần 4175 thì máy tự chọn "Trên" và bias BUY. **Bẫy:** tôi bấm thêm "Trên" cho chắc thì nó bỏ chọn, bias quay về "chưa đủ dữ liệu" (nút đã sáng mà bấm lại là tắt, không cảnh báo).
3. **Ô chọn loại vùng** ([03](test-ux-v2/03-picker-open.png), [04](test-ux-v2/04-hover-poorLow.png)): bấm mở, rê chuột lên "Poor low" thì khung bên phải hiện ngay "Đáy có từ 2 TPO: giá chưa bị từ chối dứt khoát ở đó. Dùng thế nào: Là nợ: giá hay quay lại chạm. Không phải chỗ bắt đảo chiều." Đúng điều người dùng muốn. Rê lên dòng khác đổi ngay, ↑↓ chạy tốt, gõ "poor l" + Enter chọn được. Naked POC có nhãn "chỉ mục tiêu" (gõ "npoc" không lọc ra, phải gõ "naked"). **Kẹt nhỏ:** ở 768 px cao, danh sách xổ xuống bị cắt đáy màn hình, 19 dòng chỉ thấy ~8, phải cuộn trang mới thấy phần còn lại.
4. **Thêm vùng:** gõ nhanh `vwapw 4175, vah 4184, val 4172, hvn 4190` + Enter ra 4 vùng một lần, nhanh. Thêm Poor low bằng ô chọn: mở, gõ, Enter, gõ giá, bấm Thêm vùng (6 thao tác cho 1 vùng, chậm hơn gõ nhanh nhiều). Thẻ phiên cột phải nhân đôi dòng "Poor low 4160" (một dòng trong VÙNG, một dòng trong NỢ).
5. **Chốt thẻ** (1 bấm) tự nhảy sang Setup Entry ([06](test-ux-v2/06-after-lock.png)). Cả tầng 0 + 1 mất 7 bấm + 5 ô gõ.
6. **Setup Entry:** ô chung chiếm ~300 px đầu trang, trong đó 4 dòng ✓ máy tự kiểm xanh hết (không làm gì được), chỉ 1 ô tick tay ("không trong 3 nến sau nến dài nhất") và nó **đỏ sẵn**. Khối A mới bắt đầu ở y = 580 trên màn 768. Mỗi khối cao ~1.100 px (A 1.099, B 1.099, C 979, D 979), cả trang 4.896 px (8,5 màn). Thanh dính trên + banner + thanh nhảy + thanh ENTRY dưới ăn ~25% chiều cao ([08](test-ux-v2/08-blockB-top.png), [09](test-ux-v2/09-blockB-mid.png)).
7. **Kèo B buy tại VWAP tuần, làm nguội** ([11](test-ux-v2/11-B-before-sl.png), [12](test-ux-v2/12-B-entry.png)): tick nến dài, Hướng buy, Vùng z1, 9 checkbox, gõ Giá vào 4176, SL 4173,7, biên độ nến 2, rồi ô SL. Thanh xanh hiện **ENTRY BUY · kịch bản B 4176,0 · SL 4173,7 (2,3 giá) · TP 4182,9 · 1:3 · cỡ đủ · 1 hợp đồng** kèm nút Ghi lệnh. Chữ to, rõ, đọc được trong 1 giây. Thiếu 1 ô thì thanh vàng nói đúng tên ô thiếu.
8. **Ghi lệnh** ([13](test-ux-v2/13-after-write.png)): trang **cuộn về đầu**, khối B bị xóa 15/18 tick (còn Hướng, Vùng, "Lần ≤ 2"), ô chung "Không có lệnh đang mở" đỏ, thanh dưới đổi thành CHỜ và liệt kê 3 ô thiếu "(+12 ô nữa)".
9. **Kèo A sell (ngược bias BUY)** ([14](test-ux-v2/14-A-counter.png)): chọn sell hiện ô lý do đỏ bắt buộc, gõ lý do, tick 10 ô, 3 số → A **19/19, viền xanh, nhưng thanh vàng**: "khối A đủ ô, nhưng ô chung chưa đạt: Không có lệnh đang mở" + nút "Vẫn vào (thiếu 1 ô — tính phá luật)" ([19](test-ux-v2/19-A-full-but-open.png)). Lệnh B đang mở nên bị chặn đúng luật, nhưng lối thoát là sang Sổ.
10. **Sổ** ([16](test-ux-v2/16-journal-open.png), [17](test-ux-v2/17-journal-tp.png)): dòng "Lệnh đang mở" nằm trên cùng, nhắc be "+1,5R tại 4179,5". Bấm Chạm TP: giá thoát 4182,9 và R +3 tự điền; Xác nhận là xong (3 bấm). Thử Chạm SL cũng vậy (R −1, "SL liên tiếp 1 trên 3"). Quay lại Setup Entry (1 bấm): A vẫn giữ nguyên tick, **ENTRY SELL · kịch bản A 4171,2 · SL 4173,6 · TP 4164,0 · 1:3 · 1 hợp đồng = cỡ đủ, rủi ro 24 $** → Ghi lệnh. Cờ "Lẽ ra cỡ ½ vì ngược bias; không chia được" hiện rõ.
11. **Kèo C fade VAH Âu (thiếu ô, lệnh A còn mở)** ([21](test-ux-v2/21-C-force.png), [22](test-ux-v2/22-force-dialog.png)): C 14/16, thanh vàng nêu 2 ô thiếu. "Vẫn vào (thiếu 3 ô — tính phá luật)" mở hộp thoại liệt kê đủ 3 ô (kể cả "Không có lệnh đang mở"), xác nhận → dòng Sổ có ⚠ và "Phá luật 1 trên 2". Có lệnh mở rồi mà vẫn mở thêm được lệnh thứ hai nếu chịu phá luật.
12. **Tải lại trang** ([23](test-ux-v2/23-after-reload.png)): có lệnh mở thì mở thẳng tầng Sổ (hợp lý); khi không có lệnh mở thì ở lại tầng 2 và tick vẫn còn (đã thử: hướng + 1 tick + ô chung "nến dài" giữ nguyên).
13. **Điện thoại 390 px** ([32](test-ux-v2/32-m-tier1.png) đến [36](test-ux-v2/36-m-B3.png)): không tràn ngang; khối cao 1.477–1.728 px, cả trang 7.723 px (9 màn). Ảnh minh họa chiếm 1/3 màn đầu mỗi khối. **Ô chọn vùng trên điện thoại: chạm vào dòng là chọn luôn**, không đọc được định nghĩa trước khi chọn (chỉ dòng đang chọn sẵn hiện định nghĩa), mất đúng tính năng người dùng đòi.
14. **Số nhập sai** (thử thêm): Giá vào 4181 trong khi vùng z1 là 4175 (cách 6 giá) → không cảnh báo gì, "Giá cách vùng ≤ 1 giá" vẫn là ô tick tay. Gõ "abc" vào ô giá thì chữ "abc" nằm lại trong ô. SL 4182 cao hơn giá vào 4181 của lệnh buy thì hiện chung "Nhập hướng, giá vào và SL để tính R:R" (sai nghĩa: không thiếu mà là SL sai phía).

## (b) Số đo

| Việc | Số thao tác | Ước lượng thời gian | Cuộn |
|---|---|---|---|
| Tầng 0 + Vùng, 4 vùng gõ nhanh + chốt (một lần đầu đêm) | 7 bấm + 5 ô gõ | ~45 s | 0 |
| Thêm 1 vùng bằng ô chọn tự vẽ | 6 | ~12 s | 0–1 |
| **Kèo B làm nguội, từ trang trống tới ENTRY và Ghi lệnh** | 13 bấm + 3 ô số × 3 (bấm, gõ, Tab) + Ghi lệnh = **23** | ~28–35 s | ~4 lần cuộn (~2 màn) |
| Kèo A ngược bias, từ trống | **25** (thêm ô lý do) | ~35–40 s | ~4 |
| **Làm sẵn ngữ cảnh + kiểm tra trong lúc chờ** (12 bấm + 1 số, một lần) rồi **từ lúc nến xác nhận đóng tới Ghi lệnh** | **9** (tick điểm vào 1, giá vào 3, SL 3, tick SL 1, Ghi lệnh 1) | ~10–14 s | 1–2 |
| Mức tối thiểu lý tưởng (nếu số tự điền) | ~4 (điểm vào, giá vào, tick SL, Ghi) | ~6 s | 0–1 |
| Nhập kết quả ở Sổ (TP/SL) | 3 (sang Sổ, kết quả, xác nhận) + 1 quay lại Setup Entry | ~5 s | 0 |
| Từ lệnh mở sang kèo kế (đóng B rồi vào A) | 4 thao tác chen giữa + cuộn lại từ đầu trang | ~8 s | 1–2 |
| Cả 3 kèo (B, A, C) kể cả Sổ, chưa kể "Vẫn vào" | ~23 + 25 + ~22 + 8 ≈ **78** | ~2 phút | ~12 |

Cuộn: trang 4.896 px / 768 px ≈ 8,5 màn; một khối ≈ 1,4 màn nhưng chỉ ~73% màn dùng được vì thanh dính. Điện thoại 9 màn. 9 trong 23 thao tác của kèo nguội là gõ số (Giá vào, SL, biên độ nến, mỗi ô 3 thao tác).

Không có `pageerror` hay cảnh báo console nào trong cả buổi.

## (c) 10 điều cần sửa (xếp theo mức làm chậm / mất cơ hội)

1. **Lệnh mở chặn kèo mới và buộc rời Setup Entry.** Đóng lệnh (TP/SL) ở Sổ rồi quay lại tốn 4 thao tác + đổi trang, đúng lúc giá đang chạy. Đưa nút **TP / SL / hòa** thành dòng nhỏ ngay trong ô chung hoặc thanh dưới, không cần sang Sổ.
2. **Sau "Ghi lệnh" trang cuộn về đầu và xóa gần hết tick.** Mất vị trí đang nhìn, thanh dưới đổi thành danh sách "thiếu 15 ô". Giữ nguyên vị trí cuộn và để thanh dưới nói "đã ghi, chờ kết quả" thay vì CHỜ.
3. **Ba ô số mỗi lệnh (Giá vào, SL, biên độ nến 5 nến) = 9 thao tác ngay sau nến đóng.** Gợi ý: "biên độ nến 5 nến" nhập một lần chung cho cả đêm (đổi khi cần), không hỏi lại ở từng khối; Enter ở ô số nhảy ô kế (bỏ Tab); Giá vào mặc định bằng "Giá hiện tại" nếu có.
4. **Ô máy biết được mà vẫn bắt tick tay:** "Giá cách vùng ≤ 1 giá" (A, B; có giá vào và giá vùng), "Giá ở đúng cạnh ≤ 1 giá" (C), "Cú phá không rơi vào 18:00–19:20" (A, có đồng hồ), "Bias cùng chiều phá" (A, có bias và hướng). Giá vào cách vùng 6 giá không cảnh báo gì. Chuyển thành ô tự kiểm.
5. **Ô chung "Không trong 3 nến sau nến dài nhất" luôn đỏ, phải tick tay mọi lệnh**, và **B còn một ô cùng ý** ("Không ngay sau nến dài nhất phiên"). Đổi thành nút "vừa có nến dài" mặc định tắt, bỏ ô trùng ở B.
6. **Hướng và Vùng chọn lại ở từng khối (2 bấm) dù bias và vùng đã chốt.** Cho chọn vùng ngay ở thẻ phiên cột phải (bấm vùng là điền vào khối đang làm), hướng mặc định theo bias.
7. **Quá dài để cuộn:** ô chung 300 px với 4 dòng ✓ xanh vô dụng; 4 dòng ô SL tự kiểm; mỗi khối ~1.100 px. Thu 4 dòng ✓ thành 1 dòng "4/4 máy kiểm đạt" (đỏ mới xổ ra); gộp 4 ô tự kiểm SL thành một dải chip; đặt checkbox hai cột ở màn rộng. Mục tiêu: một khối vừa trong 1 màn.
8. **Checkbox trùng ý:** B ctx1 "Giá tại vùng…" với B chk4 "Giá cách vùng ≤ 1 giá"; A chk2 "bong bóng hấp thụ phe ngược" với A chk3 "bong bóng to gần nhất không ngược phe còn giữ"; A ctx1 và ctx2 cùng một ý "công nhận cú phá" (hai bước); "Đủ vốn" và "Lần ≤ 2" lặp ở cả 4 khối. Gộp để giảm 3–4 ô mỗi khối.
9. **Ô chọn loại vùng trên điện thoại chạm là chọn** (không đọc được định nghĩa), và trên màn thấp danh sách bị cắt đáy. Cần nút "i" bên mỗi dòng hoặc chạm 1 lần để xem, chạm lần hai mới chọn; mở danh sách thì tự cuộn trang cho vừa.
10. **Nhập liệu không báo lỗi:** "abc" nằm lại trong ô, SL sai phía hiện thông điệp "nhập hướng, giá vào và SL" (sai nghĩa). Báo đỏ "SL phải thấp hơn giá vào (buy)" và xóa chữ rác.

Nhỏ hơn, không xếp hạng: bấm lại nút đã sáng (Trên) thì tắt bias, không báo; "Ba câu hỏi" mà nhãn Q1, Q5; thẻ phiên nhân đôi dòng Poor low; ảnh ví dụ kèo B ghi "TP · +2R" trong khi tiêu đề khối là "3R"; thông báo "Đã chốt/Đã ghi lệnh" (4 giây) che nút tầng "Sổ"; gõ "npoc" không lọc ra Naked POC; thanh trạng thái "Đêm nay không còn khung giờ cấm" lúc 17:30 dễ hiểu nhầm là không có tin.

## (d) 5 điều nên giữ

1. **Ô chọn vùng rê chuột ra định nghĩa + "Dùng thế nào" ngay bên cạnh** (kèm ↑↓, gõ lọc). Đúng yêu cầu số 1, mượt trên máy tính.
2. **Thanh ENTRY dính đáy:** xanh, chữ cực to, đủ giá vào/SL/TP/R:R/cỡ lệnh trong một dòng, kèm Enter ghi lệnh; thiếu thì vàng và gọi tên ô thiếu. Đọc nhanh khi giá chạy.
3. **Bốn kèo mở sẵn, đếm tiến độ trên thanh nhảy (B 18/18 viền xanh), phím 1–4, tick lưu qua tải lại.** Không khóa gì, không phải đoán kèo nào "được phép".
4. **"Vẫn vào (thiếu n ô — tính phá luật)":** hộp thoại nói đúng ô thiếu, dòng Sổ ghi cờ ⚠ và danh sách thiếu, bộ đếm "Phá luật 1 trên 2" tăng ngay. Tự kỷ luật mà không cản tay.
5. **Sổ nhận kết quả nhanh:** dòng lệnh mở trên cùng, Chạm TP/SL tự điền giá thoát và R, nhắc be "+1,5R tại 4179,5". Cùng với gõ nhanh `vwapw 4175, vah 4184, …` cho 4 vùng trong một lần Enter.

## (e) Điểm "dùng được ngay đêm nay để trade M1": **3,5 / 5**

Luồng đúng ý (không rule khóa, 4 kịch bản dọc, ENTRY rõ, Sổ tiện) và dùng **được** nếu tôi làm sẵn ngữ cảnh/kiểm tra trong lúc chờ nến: lúc nến xác nhận đóng chỉ còn ~9 thao tác, ~10–14 s. Nhưng làm nguội mất ~25 thao tác, 4–6 lần cuộn; sau mỗi lệnh phải sang Sổ mới được kèo kế; ba ô gõ số và một ô "nến dài" tick tay lặp lại mỗi lệnh. Với M1 tôi vẫn mất cơ hội ở kèo thứ hai liền sau lệnh đầu. Sửa các mục 1–5 ở (c) có thể đưa lên khoảng 4,5.
