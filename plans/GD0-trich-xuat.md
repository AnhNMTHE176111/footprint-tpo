# GĐ0 — Trích xuất cơ học tài liệu Wyckoff

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | low |
| **Cần trước** | — |
| **Chi phí** | thấp (chủ yếu chạy script, không đọc nội dung) |
| **Output** | `data-export/wyckoff/extracted/` + `data-export/wyckoff/EXTRACT_REPORT.md` |

Đây là pha **build**, không phải pha đọc hiểu. Tuyệt đối không đọc nội dung bài giảng ở pha này.

---

=== PROMPT ===

Trong `data-export/wyckoff/` có bộ bài giảng Wyckoff mới bổ sung. Việc của bạn ở lượt này là **trích xuất cơ học** ra text + ảnh để các phiên sau đọc bản đã trích xuất, KHÔNG mở lại file gốc. **Không đọc nội dung bài giảng, không giảng, không phân tích** — chỉ trích xuất và báo cáo hiện trạng.

## Hiện trạng đã kiểm (dùng luôn, không cần kiểm lại)

| File | Loại | Số trang/slide | Ghi chú |
|---|---|---|---|
| 1.pdf | PDF | 62 | |
| 2.pdf | PDF | 135 | |
| 3.pptx | PPTX | 35 slide | |
| 4.pdf | PDF | 170 | |
| 5.pdf | PDF | 46 | |
| 6.pdf | PDF | 26 | |
| 7.pdf | PDF | 179 | |
| 8.pdf | PDF | 36 | |
| 9.pdf | PDF | 36 | **md5 trùng khít 8.pdf → BỎ QUA, chỉ ghi nhận là bản trùng** |
| 12.pdf | PDF | 5 | |
| Tổng hợp chart đẹp Journal.pptx | PPTX | 153 slide | journal review bài tập học viên |

- **Thiếu phần 10 và 11** — phải ghi rõ trong report để người học biết mà bổ sung.
- `poppler-utils` có sẵn (`pdfinfo`, `pdftotext`, `pdftoppm` chạy được).

## Việc phải làm

1. **Viết một script trích xuất** đặt ở `data-export/wyckoff/extract.py` (theo tinh thần `build_setup.py` ở gốc repo — mở ra xem pattern trước khi viết). Script phải **idempotent** (chạy lại không hỏng, bỏ qua file đã có).

2. **PDF** — với mỗi file (trừ 9.pdf):
   - `pdftotext -layout` → `extracted/text/<n>.txt`
   - Đo **số ký tự có nghĩa / số trang**. Nếu `< 100 ký tự/trang` → coi là **PDF ảnh (scan/slide ảnh)**, phải render.
   - Render trang ra PNG: `pdftoppm -r 110 -png` → `extracted/images/<n>/p%03d.png`.
     Với file text-based cũng nên render (slide Wyckoff bản chất là chart — text không đủ), **nhưng** nếu tổng
     dung lượng ảnh vượt ~1.5GB thì hạ xuống `-r 90` và ghi rõ trong report.

3. **PPTX** — với `3.pptx` và `Tổng hợp chart đẹp Journal.pptx`:
   - Trích text từng slide bằng cách unzip `ppt/slides/slideN.xml` và lấy nội dung các thẻ `<a:t>` (kèm cả
     `ppt/notesSlides/` nếu có) → `extracted/text/pptx-<tên>-slideNNN.txt` hoặc một file gộp có phân đoạn rõ
     `=== SLIDE N ===`.
   - Ảnh: kiểm `which libreoffice soffice`.
     - **Có** → convert sang PDF rồi `pdftoppm` để giữ nguyên annotation (mũi tên, nhãn vẽ trong PowerPoint)
       → `extracted/images/journal/sNNN.png`.
     - **Không có** → fallback: `unzip ppt/media/*` lấy ảnh chart nhúng → `extracted/images/journal-media/`,
       và **ghi rõ trong report rằng annotation vẽ ngoài ảnh sẽ bị mất**, chỉ còn trong text XML.
   - Quan trọng: phải giữ được **mapping slide ↔ ảnh** (slide 37 dùng ảnh nào), vì GĐ2 cần ghép nhận xét với chart.

4. **Viết `data-export/wyckoff/EXTRACT_REPORT.md`** gồm:
   - Bảng: file gốc | loại | số trang/slide | text-based hay ảnh | số ký tự trích được | đường dẫn text | đường dẫn ảnh | số ảnh
   - Mục **"Thiếu / bất thường"**: thiếu phần 10, 11; 9.pdf trùng 8.pdf; libreoffice có/không; mọi file lỗi.
   - Mục **"Cách dùng cho GĐ1/GĐ2"**: nói rõ file nào đọc bằng text, file nào buộc phải đọc bằng ảnh, và
     ước lượng khối lượng (bao nhiêu trang cần đọc bằng mắt) để phiên sau biết chia lô.
   - Mục **"Bản đồ nhanh"**: với mỗi PDF, đọc **mục lục / 2 trang đầu** (chỉ 2 trang, bằng text nếu có) để ghi
     một dòng "phần này nói về gì". Đây là ngoại lệ duy nhất được phép chạm nội dung.

5. **`.gitignore`**: file gốc PDF/PPTX **đã được người dùng commit** ở `15be47d` ("add wyckoff data") nên
   không cần (và không nên) tự ý gỡ khỏi tracking — gỡ cũng không làm `.git` nhỏ lại. Việc cần làm là chặn
   **sản phẩm sinh ra**:
   ```
   data-export/wyckoff/extracted/images/
   ```
   Text trích xuất (`extracted/text/`) thì **có commit** nếu tổng < 20MB (kiểm dung lượng trước, báo số).
   Nếu ảnh render vượt ~1GB, nói với người dùng để họ biết đang chiếm đĩa (không tự xoá).

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file nhắc đến phải có **link Markdown**.
2. **Không bịa số** — mọi con số là output thật của lệnh vừa chạy.
3. Repo **PUBLIC**: không hardcode token. Không commit ảnh render (file gốc đã được commit sẵn từ trước).
4. Không publish lên Claude Artifacts.
5. Xong → **commit + push `origin main`** (commit: `extract.py`, `EXTRACT_REPORT.md`, `extracted/text/`, `.gitignore`).
6. Báo cáo trung thực phần nào lỗi/bỏ qua.

## Xong khi nào (definition of done)

- [ ] `extract.py` chạy hết không lỗi, chạy lại lần 2 không làm gì thêm
- [ ] Mọi PDF (trừ 9) có text + ảnh trong `extracted/`
- [ ] Cả 2 PPTX có text theo slide + ảnh (hoặc ghi rõ vì sao không có ảnh)
- [ ] `EXTRACT_REPORT.md` đầy đủ 4 mục
- [ ] `.gitignore` đã chặn file nặng; `git status` sạch, không có file >5MB được stage
- [ ] Đã commit + push

Báo lại cuối lượt: bảng tóm tắt trích xuất, danh sách bất thường, và **khối lượng cần đọc bằng mắt ở GĐ1/GĐ2**.
