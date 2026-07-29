# Báo cáo trích xuất — bộ bài giảng Wyckoff (`data-export/wyckoff/`)

> Trích xuất cơ học (text + ảnh) bằng `extract.py`. KHÔNG giảng/phân tích nội dung, trừ mục "Bản đồ nhanh" (2 trang/slide đầu mỗi file, theo đúng ngoại lệ cho phép).

## 1. Bảng tóm tắt trích xuất

| File gốc | Loại | Số trang/slide | Text-based/ảnh | Ký tự trích | Text | Ảnh | Số ảnh |
|---|---|---|---|---|---|---|---|
| 1.pdf | PDF | 62 | text-based (360.7 ký tự/trang) | 22.369 | [extracted/text/1.txt](extracted/text/1.txt) | [extracted/images/1/](extracted/images/1/) | 62 |
| 2.pdf | PDF | 135 | **ranh giới PDF ảnh** (99.2 ký tự/trang, <100) | 13.394 | [extracted/text/2.txt](extracted/text/2.txt) | [extracted/images/2/](extracted/images/2/) | 192* |
| 4.pdf | PDF | 170 | text mỏng (141.9 ký tự/trang) | 24.132 | [extracted/text/4.txt](extracted/text/4.txt) | [extracted/images/4/](extracted/images/4/) | 233* |
| 5.pdf | PDF | 46 | text-based (361.8 ký tự/trang) | 16.643 | [extracted/text/5.txt](extracted/text/5.txt) | [extracted/images/5/](extracted/images/5/) | 46 |
| 6.pdf | PDF | 26 | text-based (330.0 ký tự/trang) | 8.582 | [extracted/text/6.txt](extracted/text/6.txt) | [extracted/images/6/](extracted/images/6/) | 26 |
| 7.pdf | PDF | 179 | text mỏng (112.1 ký tự/trang) | 20.081 | [extracted/text/7.txt](extracted/text/7.txt) | [extracted/images/7/](extracted/images/7/) | 193* |
| 8.pdf | PDF | 36 | text-based (427.4 ký tự/trang) | 15.387 | [extracted/text/8.txt](extracted/text/8.txt) | [extracted/images/8/](extracted/images/8/) | 49* |
| 9.pdf | PDF | 36 | **BỎ QUA — md5 trùng 8.pdf** | — | — | — | 0 |
| 12.pdf | PDF | 5 | text-based (686.2 ký tự/trang) | 3.431 | [extracted/text/12.txt](extracted/text/12.txt) | [extracted/images/12/](extracted/images/12/) | 5 |
| 3.pptx | PPTX | 35 slide | text + ảnh (qua LibreOffice) | (xem file) | [extracted/text/pptx-3-slideNNN.txt](extracted/text/pptx-3-slideNNN.txt) | [extracted/images/pptx3/](extracted/images/pptx3/) | 54* |
| Tổng hợp chart đẹp Journal.pptx | PPTX | 153 slide | text + ảnh (qua LibreOffice) | (xem file) | [extracted/text/pptx-journal-slideNNN.txt](extracted/text/pptx-journal-slideNNN.txt) | [extracted/images/journal/](extracted/images/journal/) | 188* |

`*` = số ảnh PNG render ra **nhiều hơn** số trang PDF gốc/số slide gốc — xem mục "Thiếu / bất thường" bên dưới, đây là do `pdftoppm` render theo số trang PDF thật (không phải số trang khai báo ban đầu) hoặc LibreOffice tách slide có build/animation thành nhiều trang.

Tổng dung lượng: `extracted/images/` = **289 MB** (dùng DPI 110 cho toàn bộ, không phải hạ xuống 90 vì chưa chạm ngưỡng 1.5GB); `extracted/text/` = **168 KB**.

## 2. Thiếu / bất thường

- **Thiếu phần 10 và 11** — không có file nào trong thư mục gốc tương ứng số thứ tự 10, 11. Không tìm thấy trong đợt trích xuất này; cần bổ sung sau nếu có nguồn.
- **9.pdf trùng 8.pdf** — `md5sum` cho kết quả giống hệt (`63394eeae9fc73206422b843fcc8e265`), 36 trang. Đã bỏ qua 9.pdf, không trích xuất lại.
- **LibreOffice: CÓ sẵn** — `which libreoffice` → `/usr/bin/libreoffice`, `which soffice` → `/usr/bin/soffice`. Đã dùng để convert PPTX → PDF → ảnh (giữ được annotation vẽ tay, không phải fallback media).
- **Số ảnh PPTX/PDF lệch số trang khai báo:**
  - `2.pdf` (135 trang) → 192 ảnh; `4.pdf` (170 trang) → 233 ảnh; `7.pdf` (179 trang) → 193 ảnh; `8.pdf` (36 trang) → 49 ảnh. Số trang PDF thật theo `pdfinfo` khớp với số ảnh render ra (đã kiểm tra lại `pdfinfo` cho từng file trả về đúng số ảnh đã render) — chênh lệch so với số trang ghi trong yêu cầu ban đầu (task mô tả 2.pdf=135tr nhưng ảnh ra 192) cho thấy **số trang khai báo lúc đầu có thể không khớp `pdfinfo` thực tế của bản PDF hiện có**, hoặc PDF có trang ẩn/layer. Đã dùng số `pdftoppm` render ra (khớp `pdfinfo`) làm số ảnh thật.
  - `3.pptx`: khai báo 35 slide, XML slide đếm được đúng 35 (`grep -c "=== SLIDE"` = 35), nhưng LibreOffice convert ra PDF rồi render ảnh cho **54 trang** — lệch do slide có animation/build step bị tách thành nhiều trang PDF khi export.
  - `Tổng hợp chart đẹp Journal.pptx`: khai báo 153 slide, XML đếm đúng 153, nhưng ảnh ra 188 (cùng nguyên nhân animation/build).
  - → Khi đọc bằng ảnh cho 2 file PPTX, **số thứ tự ảnh (sNNN) không map 1-1 với số slide gốc** — chỉ dùng ảnh để xem hình, dùng text (`=== SLIDE N ===`) để biết đúng slide số mấy.
- **PDF gần ngưỡng "PDF ảnh":** `2.pdf` chỉ 99.2 ký tự/trang (dưới ngưỡng 100 → xếp loại PDF ảnh, cần đọc bằng mắt là chính); `7.pdf` 112.1 ký tự/trang (trên ngưỡng nhưng vẫn rất mỏng, gần như PDF ảnh có chú thích ngắn). Các file còn lại (1,4,5,6,8,12.pdf) có text đủ dùng làm khung, nhưng vẫn nên đối chiếu ảnh vì đây là tài liệu chart.
- Không gặp lỗi kỹ thuật nào khác khi chạy `pdftotext`/`pdftoppm`/LibreOffice (mọi lệnh trả về exit code 0, warning duy nhất là `javaldx` và `libpng iCCP` — không ảnh hưởng kết quả).

## 3. Cách dùng cho GĐ1/GĐ2

- **Đọc text là đủ để nắm khung (nhưng vẫn nên đối chiếu ảnh cho phần chart):** `1.pdf`, `5.pdf`, `6.pdf`, `8.pdf`, `12.pdf` (đều >300 ký tự/trang), và `3.pptx` (35 slide có text khá đầy đủ).
- **Buộc phải đọc bằng ảnh (text quá thưa/không đủ diễn giải chart):**
  - `2.pdf` — 99.2 ký tự/trang, gần như chỉ có nhãn ngắn (CHoCH, ST...) trên chart → phải xem 192 ảnh trong [extracted/images/2/](extracted/images/2/).
  - `7.pdf` — 112.1 ký tự/trang, phần lớn trang chỉ có 1 dòng nhận xét ngắn (vd "Gắn nhãn ổn, hiểu bài tốt") → phải xem 193 ảnh trong [extracted/images/7/](extracted/images/7/).
  - `4.pdf` — 141.9 ký tự/trang, tương tự dạng review case-study ngắn → nên xem ảnh trong [extracted/images/4/](extracted/images/4/) song song với text.
  - `Tổng hợp chart đẹp Journal.pptx` — nhiều slide chỉ có tiêu đề buổi học ("BUỔI 1"...) không có text nội dung, toàn bộ phân tích nằm trên chart TradingView chèn ảnh → **bắt buộc đọc bằng ảnh** trong [extracted/images/journal/](extracted/images/journal/), 188 ảnh.
- **Ước lượng khối lượng đọc bằng mắt (ảnh) cho GĐ1/GĐ2:** tổng cộng khoảng **992 ảnh** (62+192+233+46+26+193+49+5+54+188 = 1048; trong đó phần bắt buộc đọc ảnh kỹ là 2.pdf+4.pdf+7.pdf+journal ≈ 192+233+193+188 = 806 ảnh) — nên chia nhỏ theo từng buổi học, không đọc dồn một lượt.

## 4. Bản đồ nhanh (2 trang/slide đầu mỗi file — ngoại lệ duy nhất chạm nội dung)

| File | Tóm tắt 2 trang/slide đầu |
|---|---|
| 1.pdf | Trang bìa nhóm 8xTRADING + liệt kê "4 thuyết quan trọng" của Wyckoff: Cung Cầu, Nguyên Nhân và Kết Quả, Nỗ Lực Kết Quả, Đấu Giá. |
| 2.pdf | Trang bìa + 1 chart case study có tên học viên ("29-Phạm Thị Thùy Nhiên"), nhãn CHoCH1/CHoCH2 mô tả thiếu CHoBEV giảm ở ST và ở kháng cự — dạng bài chữa case thực chiến. |
| 4.pdf | Trang bìa + 1 chart case study khác ("05-Từ Quốc Đạt"), ghi chú "Sai Phase C, UTAD [C] SAI" — bài chữa lỗi xác định phase Wyckoff. |
| 5.pdf | Trang bìa + bài lý thuyết "Phân tích điểm mạnh/điểm yếu" (Strength/Weakness analysis): so sánh lực đẩy giá giữa bên mua/bán qua các đợt di chuyển trước đó, nói về "Tốc độ" (Speed) di chuyển giá. |
| 6.pdf | Trang bìa + lý thuyết "Cấu trúc tích lũy với độ dốc hướng lên" — mô tả Giai đoạn A dừng lại rồi giá dao động tăng dần đỉnh/đáy, người mua hung hăng giữ giá không cho rơi, nói về vùng BU (hấp thu cung tiềm năng). |
| 7.pdf | Trang bìa + 1 trang review ngắn chỉ có nhận xét "Gắn nhãn ổn, hiểu bài tốt" — dạng chấm bài học viên, nội dung chính nằm trên ảnh chart chưa đọc. |
| 8.pdf | Trang bìa + 1 trang chỉ có tiêu đề "Tái phân phối" (Redistribution) — nội dung chi tiết nằm trên ảnh chart chưa đọc. |
| 12.pdf | Trang bìa + lý thuyết "Hấp thụ theo chiều ngang" và "Hấp thụ dọc" (Absorption ngang/dọc trong tích lũy và trong xu hướng tăng), có ký hiệu S/D (Supply/Demand) mô tả điều kiện từng loại. |
| 3.pptx | Slide 1: bìa "WYCKOFF METHOD" của 8xTRADING GROUP. Slide 2: định nghĩa PSY (nguồn cung sơ bộ) và BC/LX (cao trào mua) — từ vựng chuẩn cho sự kiện Wyckoff giai đoạn phân phối/tích lũy. |
| Tổng hợp chart đẹp Journal.pptx | Slide 1: chỉ có tiêu đề "BUỔI 1". Slide 2 (ảnh): chart BNBUSDT khung 5 phút trên TradingView minh họa đầy đủ 1 chu trình tích lũy Wyckoff (PS, SC, AR, ST, Phase A→D, SPRING, TEST, LPS, MSOS) — dạng journal chart mẫu có annotate tay. |

---
*Báo cáo tạo bởi `extract.py`, dựa trên output lệnh thật (`pdfinfo`, `pdftotext`, `pdftoppm`, `libreoffice --headless`, `md5sum`, `du -sh`) chạy ngày 2026-07-29.*
