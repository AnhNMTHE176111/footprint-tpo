# GĐ1 — Chưng cất lý thuyết Wyckoff (phần 1–12) thành nguồn bền vững

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | medium |
| **Cần trước** | GĐ0 |
| **Chi phí** | cao về token đọc, thấp về suy luận → đúng vai Sonnet |
| **Output** | `data-export/wyckoff/THEORY.md` + `data-export/wyckoff/WYCKOFF_RULES.md` |

**Thiết kế chống tràn context:** làm theo lô, **ghi file sau mỗi lô**, không giữ hết trong đầu.
Nếu hết context giữa đường, phiên sau đọc `THEORY.md` là biết đã làm tới đâu và tiếp được.

---

=== PROMPT ===

Đọc `data-export/wyckoff/EXTRACT_REPORT.md` trước. Việc của bạn: **chưng cất toàn bộ lý thuyết Wyckoff (phần 1–12)** thành 2 file markdown làm nguồn bền vững, để mọi phiên sau đọc file này thay vì mở lại PDF/ảnh.

Đây là việc **trích xuất + hệ thống hoá**, KHÔNG phải việc thiết kế chiến lược. Đừng đề xuất setup trade ở lượt này.

## Cách làm — BẮT BUỘC theo lô, checkpoint sau mỗi lô

Xử lý **từng file một** theo thứ tự 1, 2, 3(pptx), 4, 5, 6, 7, 8, 12 (bỏ 9.pdf — trùng 8.pdf; thiếu 10, 11).

Với mỗi file:
1. Đọc text đã trích (`extracted/text/`). Nếu text rỗng/vô nghĩa → đọc ảnh trang trong `extracted/images/`,
   **mỗi lượt tool call tối đa 3–4 ảnh** (đọc nhiều hơn sẽ khiến ảnh cũ bị đẩy khỏi context và mất nội dung —
   đã xảy ra ngày 2026-07-29).
2. Ngay sau khi xong file đó → **ghi/append vào `THEORY.md`**, rồi mới sang file tiếp.
3. Đầu `THEORY.md` giữ một **bảng tiến độ** `file | trạng thái | mục nào trong THEORY.md` để phiên sau tiếp được.

## `THEORY.md` phải có

1. **Bảng tiến độ** (như trên) + **bảng tra `nguồn → nội dung`**: mỗi mục ghi rõ lấy từ file/trang nào
   (ví dụ `4.pdf p112`, `journal s037`) kèm **link Markdown tới ảnh** nếu có.
2. **Bộ khái niệm chuẩn hoá.** Hai nguồn có thể dịch máy / dùng từ khác nhau → chốt một tên chuẩn cho mỗi
   khái niệm và ghi các biến thể. Bắt buộc phủ (nếu tài liệu có):
   - Phase A/B/C/D/E — dấu hiệu nhận biết từng phase, **cái gì bắt buộc, cái gì chỉ điển hình**
   - Sự kiện: PS, SC, AR, ST, Spring, Test, LPS, SOS, BU/LPS lại · phía phân phối: PSY, BC, AR, ST, UT, UTAD, LPSY, SOW
   - Trading range: cách xác định biên, creek/ice, jump the creek
   - Vai trò volume & spread trong từng phase (đây là phần dùng để code)
   - Effort vs Result, absorption, no-supply/no-demand
3. **Với mỗi khái niệm, tách rõ 2 tầng** (rất quan trọng, đã từng sai vì lẫn 2 tầng này):
   - **ĐỊNH NGHĨA GỐC** — điều kiện bắt buộc, nguyên văn tài liệu
   - **HỆ QUẢ ĐIỂN HÌNH** — mô tả ca thường gặp, KHÔNG được dùng làm điều kiện lọc
4. **Nguyên văn khi quan trọng.** Chỗ nào là câu chốt của tài liệu → trích nguyên văn trong blockquote.
   Chỗ nào là bạn tự tổng hợp/suy ra → ghi rõ `[Claude tổng hợp]`.
5. **Mục "Mâu thuẫn / mơ hồ"**: chỗ nào tài liệu nói khác nhau giữa các phần, hoặc mô tả không đủ để code
   (ví dụ "volume giảm dần" — giảm so với gì, trong bao nhiêu nến?). Đây là input quan trọng cho GĐ4.

## `WYCKOFF_RULES.md` phải có

Bảng luật **có thể code**, theo đúng khuôn đã dùng cho pro trader (mở
[RULES.md](../data-export/messages-with-pro-trader/RULES.md) xem mẫu trước khi viết). Mỗi dòng:

| Mã | Nguyên văn / nguồn | Cơ chế đấu giá | Feature code được (biến, cửa sổ, đơn vị) | Kiểm offline được? |
|----|--------------------|----------------|-------------------------------------------|--------------------|

- Mã dạng `WY01, WY02, ...` (đừng dùng lại `W1..W5` — đã dùng cho luật của pro trader).
- Cột "feature code được": phải cụ thể tới mức người khác code được mà không cần đọc lại PDF.
  Ví dụ tốt: `spring = nến đâm thủng biên dưới range ≥1 tick rồi đóng lại trong range, cpos ≥ 0.5`.
  Ví dụ tồi: `spring = phá giả biên dưới`.
- Cột "kiểm offline được": ghi `CÓ (dxFeed OHLCV)` / `CÓ (fp-m1 có delta nến)` / `CÓ (TPO csv)` /
  `KHÔNG — cần footprint từng mức giá` / `KHÔNG — cần đọc DOM live`. Nếu chưa chắc → ghi `?` (GĐ3 sẽ phân xử).
- Cuối file: mục **"3 luật đáng thử nhất"** kèm lý do — xếp theo (a) cơ chế mạnh, (b) dữ liệu có, (c) không
  trùng lặp cái v6 đã có.

## Bối cảnh cần biết (đừng đề xuất trùng / trái với cái đã chết)

Đọc nhanh 2 file này (chỉ mục cần):
- [WYCKOFF_V6_PLAN.md](../quantower-entry-signal/WYCKOFF_V6_PLAN.md) — **§9 "ĐÃ THỬ VÀ THẤT BẠI"** và
  **§10 "KHÔNG KIỂM ĐƯỢC OFFLINE"**. Đặc biệt: giả thuyết "bắt buộc có spring/upthrust (Phase C) trước khi
  phá" **đã bị dữ liệu bác** (n=26, WR 34.6%, tháng 6 âm); luật đúng lại là **ngược lại** — chỉ đánh cú phá
  KHÔNG có quét hụt ngược gần đó. Khi chưng cất, nếu tài liệu nói điều trái với kết quả này thì **vẫn ghi
  nguyên văn tài liệu**, và ghi thêm dòng `⚠ dữ liệu 5–7/2026 bác dạng lọc này, xem V6_PLAN §9`.
- [RULES.md](../data-export/messages-with-pro-trader/RULES.md) — luật của pro trader. Chỗ nào tài liệu Wyckoff
  **trùng** với luật pro trader → ghi mã chéo (`≈ R7`). Chỗ nào **xung đột** → ghi vào mục "Mâu thuẫn".

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file/ảnh nhắc đến phải có **link Markdown** ngay tại chỗ nhắc.
2. **Không bịa nội dung tài liệu.** Chỉ ghi cái đã đọc thấy. Phần tự tổng hợp phải gắn nhãn `[Claude tổng hợp]`.
3. Không dịch thô word-by-word; dùng thuật ngữ chuẩn tiếng Việt + kèm tên tiếng Anh trong ngoặc.
4. Repo **PUBLIC**: không commit ảnh render — chỉ commit `.md` (PDF/PPTX gốc đã được commit sẵn từ trước).
5. Không publish lên Claude Artifacts.
6. Xong → **commit + push `origin main`**.
7. Trung thực: file nào chưa xử lý xong phải ghi trong bảng tiến độ, không im lặng bỏ.

## Xong khi nào

- [ ] Bảng tiến độ trong `THEORY.md` đủ 9 file ở trạng thái `xong`
- [ ] Đủ Phase A–E + đủ bộ sự kiện tích luỹ và phân phối, mỗi cái tách ĐỊNH NGHĨA GỐC vs HỆ QUẢ ĐIỂN HÌNH
- [ ] `WYCKOFF_RULES.md` có ≥ 15 luật, mỗi luật đủ 5 cột, cột "feature code được" đủ cụ thể để code
- [ ] Có mục "Mâu thuẫn / mơ hồ" (không được để rỗng — tài liệu dịch/slide luôn có chỗ mơ hồ)
- [ ] Đã commit + push

Cuối lượt báo: đã chưng cất bao nhiêu trang, `THEORY.md`/`WYCKOFF_RULES.md` dài bao nhiêu, **3 luật đáng thử nhất**, và danh sách chỗ mơ hồ cần GĐ4 quyết.
