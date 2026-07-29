# GĐ2 — Chưng cất toàn bộ tài liệu CHỮA BÀI (806 ảnh) → thư viện ca thực tế

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | medium |
| **Cần trước** | GĐ0 |
| **Chi phí** | **cao nhất trong cả lộ trình** — 806 ảnh |
| **Output** | `data-export/wyckoff/CHART_CASES.md` (append dần qua nhiều lượt) |

Chạy **song song được** với GĐ1/GĐ3/GĐ5 (phiên khác). Đây là nguồn quý nhất về *cách gán nhãn thực tế* — lý
thuyết nói "spring", tài liệu chữa bài cho thấy spring trông như thế nào và học viên hay gán sai chỗ nào.

⚠ **Phải chia thành 4 LƯỢT CHẠY riêng** (mỗi lượt một phiên mới), vì 806 ảnh không vừa một context:

| Lượt | Nguồn | Số ảnh | Thư mục ảnh |
|---:|---|---:|---|
| 2a | `7.pdf` | 193 | `extracted/images/7/` |
| 2b | `2.pdf` | 192 | `extracted/images/2/` |
| 2c | `4.pdf` | 233 | `extracted/images/4/` |
| 2d | `Tổng hợp chart đẹp Journal.pptx` | 188 | `extracted/images/journal/` |

Khi dán prompt, ghi rõ ở đầu: **"Lượt này làm 2a — nguồn `7.pdf`"** (hoặc 2b/2c/2d).
Nên bắt đầu bằng **2a (`7.pdf`)** vì text của nó chứa sẵn nhiều câu nhận xét của giảng viên → dễ ghép nhất.

---

=== PROMPT ===

**Lượt này làm: 2_ — nguồn `______`** ← điền trước khi gửi (xem bảng 4 lượt ở trên).

Trong `data-export/wyckoff/` có 4 nguồn **chữa bài gán nhãn Wyckoff của học viên** (giảng viên nhận xét trực tiếp trên chart): `7.pdf`, `2.pdf`, `4.pdf`, và `Tổng hợp chart đẹp Journal.pptx`. GĐ0 đã trích text + ảnh ra `data-export/wyckoff/extracted/` — đọc `EXTRACT_REPORT.md` trước để biết đường dẫn và các cảnh báo.

Việc của bạn ở lượt này: chưng cất **đúng một nguồn** đã nêu trên vào **`data-export/wyckoff/CHART_CASES.md`** (**append**, không ghi đè — các lượt khác đã/sẽ ghi phần của chúng), để phiên sau tra ca mà không mở lại 806 ảnh.

⚠ **Cảnh báo mapping từ GĐ0:** với 2 file PPTX, số thứ tự ảnh `sNNN` **không map 1-1** với số slide gốc
(LibreOffice tách slide có animation thành nhiều trang: 153 slide → 188 ảnh; 35 → 54). Dùng **ảnh để xem hình**,
dùng **text `=== SLIDE N ===` để biết đúng slide số mấy**. Với PDF thì số ảnh khớp `pdfinfo`, nhưng lệch so với
số trang từng khai báo — bám tên file ảnh, đừng bám số trang in trong tài liệu.

Lưu ý bản chất tài liệu: đây là tài liệu **giúp xác định phase và các mốc quan trọng, KHÔNG cho kịch bản trade**. Đừng cố suy ra setup vào lệnh từ nó; nhiệm vụ ở đây là bắt đúng *cách nhận dạng cấu trúc*.

## Cách làm — theo lô, checkpoint sau mỗi lô

- Chia nguồn của lượt này thành **lô 10 ảnh**. Mỗi lô: đọc ảnh (**tối đa 3–4 ảnh mỗi tool call** — đọc nhiều
  hơn làm ảnh cũ bị đẩy khỏi context và mất nội dung, đã xảy ra 2026-07-29) + text tương ứng → **append ngay vào
  `CHART_CASES.md`** → sang lô sau.
- Đầu file giữ **bảng tiến độ chung cho cả 4 lượt**: `nguồn | lô ảnh | trạng thái`. Lượt sau đọc bảng này là
  biết còn gì chưa làm. Nếu hết context giữa đường: dừng, cập nhật bảng tiến độ, báo lại đã tới ảnh nào —
  **đừng cố nhồi cho hết**.
- Ghép nhận xét với chart: text `pdftotext` xuất nhận xét theo thứ tự xuất hiện (xem `extracted/text/7.txt`:
  tên học viên + câu nhận xét xen kẽ). Dùng text để lấy **nguyên văn** câu giảng viên, dùng ảnh để biết câu đó
  nói về chart nào. Không ghép chắc chắn được → ghi `chưa ghép được nhận xét`, đừng đoán.
- Nếu ảnh nhỏ không đọc được số/nhãn → **crop phóng to** vùng cần đọc rồi đọc lại (dùng script Pillow trong
  scratchpad). Chỉ ghi con số đã **nhìn rõ**; không suy diễn số cho khớp lý thuyết.

## `CHART_CASES.md` phải có

1. **Bảng tiến độ** + **bảng tra**: `slide → chủ đề → link ảnh`. Mọi slide nhắc đến đều phải có link Markdown
   tới ảnh của nó.
2. **Mỗi ca một mục**, khuôn cố định:
   ```
   ### Ca #NN — <tên học viên nếu có> · <mã sản phẩm / khung thời gian nếu đọc được> (<nguồn> ảnh NNN)
   ảnh: [pNNN.png](extracted/images/7/p001.png)   ← đường dẫn thật của nguồn lượt này
   - **Cấu trúc:** tích luỹ / phân phối / re-accumulation / re-distribution / không rõ
   - **Học viên gán:** ...
   - **Giảng viên sửa:** ... (nguyên văn nếu có text)
   - **Dấu hiệu quyết định:** cái gì làm nó là phase X chứ không phải Y (volume, spread, vị trí đóng, số lần test)
   - **Đọc được số:** volume/spread/mốc giá thực đọc được trên chart, hoặc `không đọc rõ`
   - **Code được?** dấu hiệu này biểu diễn được bằng biến gì trên nến M1, hay cần mắt người
   ```
3. **Mục "Lỗi gán nhãn hay gặp"** (mục CHUNG cho cả 4 lượt — append thêm, đừng tạo mục mới) — tổng hợp: học viên hay sai ở đâu (ví dụ gọi UT khi chưa sang phase D,
   gọi spring cho mọi cú thủng biên, xác định biên range quá hẹp/rộng). Với mỗi lỗi, ghi **cách phân biệt
   bằng tiêu chí quan sát được**. Đây là mục có giá trị cao nhất cho GĐ4.
4. **Mục "Cách xác định biên range trong thực tế"** — journal chắc chắn có nhiều ca vẽ range. Rút ra:
   - Biên được neo vào cái gì (đỉnh/đáy swing, thân nến hay râu, đóng nến hay extreme)
   - Cần bao nhiêu lần chạm mới coi là biên
   - Range được coi là hỏng/hết hiệu lực khi nào
   Ba câu này là **input trực tiếp** cho kịch bản 3 (scalp biên↔biên) ở GĐ4 — trả lời càng cụ thể càng tốt,
   kèm số ca làm bằng chứng.
5. **Mục "Thống kê thô"** (theo từng nguồn, để cộng dồn được): bao nhiêu ca tích luỹ / phân phối / không rõ;
   bao nhiêu ca giảng viên **sửa** nhãn của học viên vs bao nhiêu ca **khen đúng**. Số thật, đếm được.
6. Phần nào là bạn tự suy → gắn nhãn `[Claude tổng hợp]`.

## Điều KHÔNG làm

- Không gán nhãn Wyckoff cho ca mà giảng viên không nói rõ, rồi trình bày như thể là ý giảng viên.
- Không quy đổi ca chart D1/H4 thành khuyến nghị cho M1 — chỉ ghi khung thời gian gốc, việc quy đổi để GĐ4 làm.
- Không đề xuất tham số backtest ở lượt này.

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi ảnh/file nhắc đến phải có **link Markdown** ngay tại chỗ nhắc.
2. **Đọc số thật trên chart trước khi diễn giải.** Không nhìn rõ → ghi `không đọc rõ`, không đoán.
3. Repo **PUBLIC**: không commit ảnh render — chỉ commit `.md`.
4. Không publish lên Claude Artifacts.
5. Xong → **commit + push `origin main`**.
6. Trung thực: lô nào chưa làm phải ghi trong bảng tiến độ.

## Xong khi nào

- [ ] Toàn bộ ảnh của **nguồn thuộc lượt này** đã qua (hoặc bảng tiến độ ghi rõ còn lô nào, vì sao)
- [ ] Bảng tiến độ 4 lượt đã cập nhật đúng
- [ ] Mỗi ca có đủ khuôn 6 gạch đầu dòng
- [ ] Có mục "Lỗi gán nhãn hay gặp" với tiêu chí phân biệt quan sát được
- [ ] Có mục "Cách xác định biên range" trả lời được 3 câu (neo vào gì / bao nhiêu lần chạm / hỏng khi nào), kèm số ca dẫn chứng
- [ ] Có thống kê thô bằng số đếm thật
- [ ] Đã commit + push

Cuối lượt báo: nguồn nào đã xong, số ca đã chưng cất, **3 lỗi gán nhãn phổ biến nhất tới giờ**, câu trả lời cho "biên range neo vào gì / bao nhiêu lần chạm / hỏng khi nào", và **lượt tiếp theo cần chạy là lượt nào**.
