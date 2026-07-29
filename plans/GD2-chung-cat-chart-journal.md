# GĐ2 — Chưng cất journal 153 slide (review bài tập học viên)

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | medium |
| **Cần trước** | GĐ0 |
| **Chi phí** | cao về token đọc ảnh |
| **Output** | `data-export/wyckoff/CHART_CASES.md` |

Chạy **song song được** với GĐ1 (phiên khác). Đây là nguồn quý nhất về *cách gán nhãn thực tế* — lý thuyết
nói "spring", journal cho thấy spring trông như thế nào và học viên hay gán sai chỗ nào.

---

=== PROMPT ===

`data-export/wyckoff/Tổng hợp chart đẹp Journal.pptx` (153 slide) là nơi giảng viên review bài tập gán nhãn Wyckoff của học viên. GĐ0 đã trích text + ảnh ra `data-export/wyckoff/extracted/` — đọc `EXTRACT_REPORT.md` trước để biết đường dẫn và mapping slide↔ảnh.

Việc của bạn: chưng cất thành **`data-export/wyckoff/CHART_CASES.md`** — thư viện ca thực tế, để phiên sau tra ca mà không mở lại 153 slide.

Lưu ý bản chất tài liệu: journal này **giúp xác định phase và các mốc quan trọng, KHÔNG cho kịch bản trade**. Đừng cố suy ra setup vào lệnh từ nó; nhiệm vụ ở đây là bắt đúng *cách nhận dạng cấu trúc*.

## Cách làm — theo lô, checkpoint sau mỗi lô

- Chia 153 slide thành **lô 10 slide**. Mỗi lô: đọc ảnh (**tối đa 3–4 ảnh mỗi tool call** — đọc nhiều hơn làm
  ảnh cũ bị đẩy khỏi context và mất nội dung, đã xảy ra 2026-07-29) + text slide tương ứng → **append ngay vào
  `CHART_CASES.md`** → sang lô sau.
- Đầu file giữ **bảng tiến độ** `lô slide | trạng thái` để phiên sau tiếp được nếu hết context.
- Nếu ảnh nhỏ không đọc được số/nhãn → **crop phóng to** vùng cần đọc rồi đọc lại (dùng script Pillow trong
  scratchpad). Chỉ ghi con số đã **nhìn rõ**; không suy diễn số cho khớp lý thuyết.

## `CHART_CASES.md` phải có

1. **Bảng tiến độ** + **bảng tra**: `slide → chủ đề → link ảnh`. Mọi slide nhắc đến đều phải có link Markdown
   tới ảnh của nó.
2. **Mỗi ca một mục**, khuôn cố định:
   ```
   ### Ca #NN — <mã sản phẩm / khung thời gian nếu đọc được> (slide NNN)
   ảnh: [sNNN.png](extracted/images/journal/sNNN.png)
   - **Cấu trúc:** tích luỹ / phân phối / re-accumulation / re-distribution / không rõ
   - **Học viên gán:** ...
   - **Giảng viên sửa:** ... (nguyên văn nếu có text)
   - **Dấu hiệu quyết định:** cái gì làm nó là phase X chứ không phải Y (volume, spread, vị trí đóng, số lần test)
   - **Đọc được số:** volume/spread/mốc giá thực đọc được trên chart, hoặc `không đọc rõ`
   - **Code được?** dấu hiệu này biểu diễn được bằng biến gì trên nến M1, hay cần mắt người
   ```
3. **Mục "Lỗi gán nhãn hay gặp"** — tổng hợp: học viên hay sai ở đâu (ví dụ gọi UT khi chưa sang phase D,
   gọi spring cho mọi cú thủng biên, xác định biên range quá hẹp/rộng). Với mỗi lỗi, ghi **cách phân biệt
   bằng tiêu chí quan sát được**. Đây là mục có giá trị cao nhất cho GĐ4.
4. **Mục "Cách xác định biên range trong thực tế"** — journal chắc chắn có nhiều ca vẽ range. Rút ra:
   - Biên được neo vào cái gì (đỉnh/đáy swing, thân nến hay râu, đóng nến hay extreme)
   - Cần bao nhiêu lần chạm mới coi là biên
   - Range được coi là hỏng/hết hiệu lực khi nào
   Ba câu này là **input trực tiếp** cho kịch bản 3 (scalp biên↔biên) ở GĐ4 — trả lời càng cụ thể càng tốt,
   kèm số ca làm bằng chứng.
5. **Mục "Thống kê thô"**: bao nhiêu ca tích luỹ / phân phối / không rõ; bao nhiêu ca giảng viên sửa nhãn
   của học viên. Số thật, đếm được.
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

- [ ] Cả 153 slide đã qua (hoặc bảng tiến độ ghi rõ còn lô nào, vì sao)
- [ ] Mỗi ca có đủ khuôn 6 gạch đầu dòng
- [ ] Có mục "Lỗi gán nhãn hay gặp" với tiêu chí phân biệt quan sát được
- [ ] Có mục "Cách xác định biên range" trả lời được 3 câu (neo vào gì / bao nhiêu lần chạm / hỏng khi nào), kèm số ca dẫn chứng
- [ ] Có thống kê thô bằng số đếm thật
- [ ] Đã commit + push

Cuối lượt báo: số ca đã chưng cất, **3 lỗi gán nhãn phổ biến nhất**, và câu trả lời cho "biên range neo vào gì / bao nhiêu lần chạm / hỏng khi nào".
