# TEST-1 — Cửu Âm Chân Kinh (tester độc lập, 2026-11-08)

Phạm vi: `index.html`, `chi-tiet.html`, `style.css`, `img/`, `../cửu âm chân kinh.md`, đối chiếu plan
`../plans/CUU-AM-CHAN-KINH-plan.md` mục 2, 3, 4, 6. Không commit, không deploy.

Công cụ: Python (script trong `docs/test/`), Chrome headless điều khiển qua giao thức gỡ lỗi (CDP, tự viết
`docs/test/cdp.py`, giả lập đúng rộng 390 px nên không cần iframe), `html5lib`. Máy không có Node nên không dùng
puppeteer/Playwright.

## 1. Bảng kết quả

| # | Mục kiểm | Kết quả | Bằng chứng |
|---|---|---|---|
| a | Trích dẫn có mốc giờ trong `chi-tiet.html` khớp nguyên văn `transcript.md` | **PASS** | `check_quotes.py`: 87/87 câu khớp đúng mốc (bỏ thẻ HTML, chuẩn hoá khoảng trắng, bỏ `**`). Câu 0:26:48 khớp dòng chính + 3 dòng con của transcript. 4 câu Messenger + 1 câu "Tổng hợp 02/11" đều có trong `TRANSCRIPT.md` / `CORVEN_TONG_HOP.md`; ngày (07/08 20:04, 05/02, 08–09/02) khớp. |
| b | 2.2 `index.html` = plan mục 2 = `cửu âm chân kinh.md` | **PASS** | `check_22.py`: 21/21 dòng (5 tiêu đề nhóm + 14 điều kiện + 2 dòng ⛔) giống hệt cả 3 nguồn. |
| c | Lint thuật ngữ (mua/bán, volatility, aggressive/passive, lệnh chờ…) | **PASS** | "mua/bán" chỉ xuất hiện trong lời nguyên văn CORVEN (0:24:28, 0:26:48, 0:27:22, 0:54:43), được phép. Không có volatility/aggressive/passive. Số thập phân dùng dấu phẩy. |
| c2 | Từ tiếng Anh chưa giải thích | **ĐÃ SỬA 1 / còn lại ghi nhận** | Sửa "Tap ô vuông… Tap chữ…" → "Chạm…". Còn: "spec" (4 chỗ), "UT", "sang D" (bảng mâu thuẫn), mã luật "R7, R13, W3" — người đọc trang công khai không hiểu. |
| d | Mục 1, 2.1, Lưu ý, ghi chú cuối giữ đúng chữ người học | **PASS (kèm ghi nhận)** | So với `git show HEAD:"cửu âm chân kinh.md"` và `CORVEN_TONG_HOP.md`: giữ đúng từng chữ ở cả md lẫn `index.html`. Ghi nhận: 2 dòng gốc của CORVEN dưới 2.2 ("khi follow phải để ý momentum", "giá không được phép test quá sâu") bị thay hẳn trong md và trang chính (đúng plan), chỉ còn trích ở `chi-tiet.html#tong`. |
| e | Bảng mâu thuẫn đủ 4 dòng | **PASS** | R:R, SL, Fail break, Follow khi nào; chữ khớp plan mục 1. |
| f1 | Ảnh không lộ mặt / tên / tab / taskbar | **PASS** | Mở xem cả 18 ảnh. Chỉ còn chữ mặc định "ExampleChartbook" (Sierra) và thanh "meet.google.com đang chia sẻ màn hình của bạn" ở 0-19-30, 0-24-15 (không tên, không mặt; đã ghi trong CROPS.md). |
| f2 | Ảnh ≤ 250 KB, khớp `CROPS.md` | **PASS** | 45–72 KB/ảnh. Cắt lại từ `frames/` theo toạ độ CROPS.md: sai khác trung bình 0,9–2,5/255 (chỉ là nhiễu nén JPG) ⇒ toạ độ đúng. `width/height` trong HTML khớp kích thước thật (1128×559, 1128×540). |
| f3 | Chú thích ảnh đọc số đúng | **PASS** | Đối chiếu từng chú thích với ảnh: các số delta (−353/131, −178, −96/70, −45/−47, −104/−113/−22/−4/66, −9/−71, −81, −42/−14/−112, −87/−109, R/R 1,71, −13/−17/23/3/33/64) và mức giá đều đọc được trên ảnh. |
| g | Không cuộn ngang ở 390 | **PASS** | `scrollWidth = clientWidth = 390` cả 2 trang, sáng + tối; không phần tử nào tràn phải (trừ mục lục cuộn ngang có chủ đích). |
| h | Chữ ≥ 14 px | **ĐÃ SỬA một phần** | Trước: nhiều chữ 11,5–13,5 px. Đã nâng lên 14 px: mũi tên `›`, bộ đếm, mục lục, nút "← Trang chính", mốc giờ `.ts`. Còn dưới 14 px (nhãn trang trí, chữ in hoa): eyebrow 12,5; h4 "NGUYÊN VĂN CORVEN" 12; nhãn "DIỄN GIẢI" 11,5; tiêu đề cột bảng 12; tên file trong ghi chú 12,6–13. |
| i | Ô tick ≥ 44 px, chạm đổi trạng thái | **PASS** | 14/14 nhãn 44×44. Chạm vào góc ô 44 px (ngoài ô vuông 26 px) vẫn tick; chạm lại thì bỏ tick; dòng đổi màu (`li.done`). |
| j | Bộ đếm + nút Xoá tick | **PASS** | 1/14 → 2/14 → 3/14 → 2/14; Xoá tick → 0/14, hết `li.done`. Nút 92×44. |
| k | Link `index → chi-tiet#id` có đích | **PASS** | 16 link, 0 thiếu; 9 link mục lục trong trang, 0 thiếu; không trùng id. Mở thẳng `chi-tiet.html#id` (tải mới): mục nằm ngay dưới mục lục dính (điện thoại top 60 / mục lục 57; máy tính top 64–72 / 49). Bấm mục lục `#g3` hoạt động. |
| l | Nút "← Trang chính" | **PASS** | 138×44, bấm về `index.html`. Ở cuối trang không che dòng nguồn. |
| m | Ảnh không 404, không lỗi console | **PASS** | 22 thẻ ảnh đều tải; 0 phản hồi ≥ 400, 0 lỗi console, 0 lỗi JS. |
| n | HTML hợp lệ | **ĐÃ SỬA** | `html5lib`: 3 lỗi/trang do `&` trần trong link Google Fonts → đổi thành `&amp;`, giờ 0 lỗi. Kiểm thẻ đóng: không thẻ mở sai/thiếu đóng. |
| o | Bảng mâu thuẫn thành thẻ ở điện thoại | **PASS** | Ảnh `chi-tiet-mobile-light-39/40.jpg`. |
| p | Nút dính đáy không che nội dung cuối | **PASS** | Cuối `index.html`: nút ở 551–607, dòng nguồn ở 647–714 (không chồng). Trong lúc cuộn, nút che ~66 px đáy màn hình (chấp nhận được). |
| q | Dark mode ảnh không quá tối | **PASS** | Bộ lọc `brightness(.85) contrast(1.05)`; nền chart xám vẫn đọc rõ số (`chi-tiet-desktop-dark-4.jpg`). |
| r | 2.2 "≤ 18 dòng, mỗi dòng ≤ 2 dòng điện thoại" (plan mục 4) | **FAIL** | Ở 390 px mỗi điều kiện chiếm 2–6 dòng (đo: 5,4,4,6,5,4,4,4,4,3,4,3,4,2); khối 2.2 cao 2454 px ≈ 3 màn hình. Là vấn đề nội dung (chữ chốt ở plan dài) ⇒ không tự sửa. |

Ảnh chụp: `docs/shots/` — 158 ảnh JPG (đã chuyển từ PNG để giảm còn ~12 MB), chụp tới cuối trang cho mỗi tổ hợp
`{index, chi-tiet} × {desktop 1280, mobile 390} × {light, dark}`, tên `<trang>-<thiết bị>-<sáng/tối>-<số thứ tự>.jpg`
(index 4–5 ảnh, chi-tiet 30–40 ảnh mỗi tổ hợp). Ảnh `index-*` chụp sau mọi lần sửa; ảnh `chi-tiet-*` chụp sau khi
sửa CSS/HTML (lần sửa chữ "Chạm" chỉ ở index).

## 2. Đọc như người dùng

- **"Đang nhìn chart, 30 giây đọc được 2.2 không?" — Không, trên điện thoại.** 14 ô, khối dài ~3 màn hình, nút
  "Chi tiết" dính đáy che thêm một dải. Trên máy tính đọc được trong khoảng 1 phút.
  Đề xuất: mỗi dòng giữ phần chữ đậm làm "từ khoá" một dòng (vd "Delta đồng thuận, to, thẳng"), đưa phần trong
  ngoặc và giải thích sang chi tiết; hoặc cho phép thu gọn từng nhóm ①–④.
- **Logic đếm lệch với luật:** nhóm ③ ghi "cần ≥ 2 dấu hiệu" nhưng bộ đếm là "x/14", gợi ý phải tick đủ 14.
  Thêm nữa "Nến xác nhận đã đóng" là điều kiện BẮT BUỘC theo luật chốt (bối cảnh + mốc + ≥ 2 dấu hiệu + nến đóng +
  2R) nhưng lại nằm chung danh sách "chọn ≥ 2" của ③. Đề xuất: tách "nến đóng" ra khỏi ③ (hoặc ghi rõ bắt buộc), và
  bộ đếm hiển thị theo nhóm, vd "③ 2/5 dấu hiệu".
- **Mâu thuẫn trong chính 2.2:** ② ghi "đánh fail break thì giá phải đã đóng lại trong lòng range" như luật tuyệt
  đối, nhưng Ví dụ 3 (1:00:09) cho thấy CORVEN vẫn vào khi chưa vào lòng range nếu có xác nhận lần 2. Trang chi tiết
  có ghi ngoại lệ, trang chính thì không.
- **"Quên thì vào chi tiết có tìm được mục không?" — Có.** Mỗi dòng ở trang chính bấm thẳng tới đúng mục, mục được
  viền nổi (`:target`). Trong trang chi tiết, mục lục chỉ có 8 nhóm (không có từng điều kiện 1.1…4.3), và trên điện
  thoại phải cuộn ngang mới thấy hết, không có dấu hiệu còn mục bên phải ngoài chữ bị cắt "4 L…".
- Nút "← Trang chính" trên điện thoại luôn đè lên một dòng chữ ở góc trái dưới khi đọc.

## 3. Lỗi còn lại (xếp theo mức nặng)

1. **Trung bình — 2.2 quá dài trên điện thoại** (FAIL mục r): không đạt tiêu chí "≤ 2 dòng điện thoại/dòng",
   không đọc nổi trong 30 giây. Cần Fable/người học rút gọn chữ.
2. **Trung bình — bộ đếm "x/14" và nhóm ③ sai logic với luật "≥ 2 dấu hiệu"**; "nến đóng" bắt buộc nhưng nằm trong
   nhóm tuỳ chọn.
3. **Nhẹ — ngoại lệ "vào lòng range" (Ví dụ 3) không có ở trang chính**, dòng ② đọc như luật tuyệt đối.
4. **Nhẹ — 2 dòng gốc của CORVEN dưới 2.2 bị xoá khỏi file md của người học** (đúng plan, nhưng mất chữ gốc của
   người học/CORVEN ở file nguồn; chỉ còn trong `chi-tiet.html#tong`). Nên hỏi người học có muốn giữ lại không.
5. **Nhẹ — thuật ngữ chưa giải thích trên trang công khai:** "spec", "UT", "sang D", mã luật "R7/R13/W3",
   "R:R" ở bảng mâu thuẫn.
6. **Nhẹ — chữ < 14 px còn ở nhãn trang trí** (h4 12 px, "DIỄN GIẢI" 11,5 px, eyebrow 12,5 px, tiêu đề cột 12 px).
7. **Rất nhẹ — mục lục điện thoại** cuộn ngang không có gợi ý; nút "← Trang chính" đè chữ khi đọc; dấu `›` có lúc
   rơi xuống dòng riêng; trang index nhảy từ h1 xuống h3 ("Lưu ý") trước h2.
8. **Lưu ý repo:** `docs/shots/` nặng ~12 MB; cân nhắc không commit hoặc chỉ giữ vài ảnh tiêu biểu.

## 4. Đã sửa trong lượt test

- `index.html`, `chi-tiet.html`: `&` → `&amp;` trong link Google Fonts (HTML hợp lệ 0 lỗi).
- `style.css`: `.go`, `.count`, `nav.toc a`, `#back`, `.ts` lên 14 px.
- `index.html`: "Tap" → "Chạm" (dòng hướng dẫn 2.2).

Chạy lại: `python docs/test/check_quotes.py`, `python docs/test/check_22.py`, `python docs/test/ui.py`,
`python docs/test/interact.py` (cần `pip install websocket-client html5lib`; đặt `PYTHONIOENCODING=utf-8`).
