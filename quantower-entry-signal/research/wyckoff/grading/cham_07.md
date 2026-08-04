# Chấm bài #07 — Tái tích luỹ (RE-ACC) · 2026-04-13 16:47 → 2026-04-14 06:26 (265 nến M1)

**Điểm: 7/10** — cấu trúc đọc đúng, tên range đúng, chỉ cần sửa vị trí ba nhãn (Phase C, LPS[C], SOS) và sửa cách diễn giải chỉ số nỗ lực/kết quả.

## Lỗi (nặng → nhẹ)

### 1. Phase C dài 41 nến, gần bằng Phase B (44 nến) — luật vi phạm: L8 (Phase C là phase NGẮN NHẤT), L9
- **Thuật toán gắn:** A=36 · B=44 · **C=41** · D=24 · E=121.
- **Đúng phải là:** Phase C phải là đoạn ngắn nhất, chỉ bao nhịp test cuối cùng ngay trước SOS. Ở đây SOS bắn lúc 23:04; Phase C phải bắt đầu quanh 22:2x–22:46 (nhịp test cuối trước khi giá bứt biên phụ 4810.9), tức 10-20 nến, không phải mở từ 19:07.
- **Dấu hiệu quyết định trên chart:** từ LPS[C] 19:07 (4791.4) tới SOS, giá đi lên **liên tục** qua 4796 → 4806.7 → 4810.9 mà không có nhịp lùi nào. Đoạn đó là markup đang chạy, không phải một phase "test nguồn cung còn lại". Nhìn ảnh: cụm nến từ 19:07 tới 22:46 leo thang từng bậc, không lùng bùng.
- **Nghi phạm trong thuật toán:** nhánh Phase C gán ngược (mục 6 case khó) lấy cửa sổ min(60 nến, 1/2 Phase B) rồi chọn **đáy sâu nhất** trong cửa sổ. Với Phase B=44 nến, cửa sổ 22 nến vẫn quá rộng và tiêu chí "đáy sâu nhất" luôn kéo mốc về sớm nhất có thể. Phải chọn **swing pivot cuối cùng** trước cú phá, không phải cực trị sâu nhất.

### 2. Nhãn SOS đặt cách biên bị phá 14 giá — luật vi phạm: L3 (SOS phải đóng cửa bứt qua biên PHỤ), mục 5.1 lỗi B
- **Thuật toán gắn:** SOS tại 4824.7, VSA 1.94x.
- **Đúng phải là:** cây phá thật là cây đầu tiên đóng cửa vượt biên phụ 4810.9 với thân ≥45%. 4824.7 nằm **13.8 giá trên biên phụ** — đó là giữa nhịp markup, không phải điểm phá.
- **Dấu hiệu quyết định trên chart:** biên phụ trên vẽ ở 4810.9; chấm SOS trên ảnh nằm hẳn phía trên vùng nhãn LPS[D] (4814.6), tức cao hơn cả nhịp retest sau đó. Một cú phá mà nhãn nằm trên đỉnh của cả nhịp retest là dấu hiệu neo sai.
- **Nghi phạm trong thuật toán:** "hồi tố về cây VSA cao nhất trong đoạn" — cây VSA cao nhất trong markup thường là cây **giữa** nhịp, không phải cây phá biên. Phải thêm điều kiện: trong số các cây đóng cửa vượt biên, lấy cây **sớm nhất** đủ thân, không lấy cây VSA lớn nhất.

### 3. ST[A] không test vùng climax mà vượt qua nó 4.2 giá — luật vi phạm: L2 (ST[A] = test lại vùng climax)
- **Thuật toán gắn:** ST[A] tại 4810.9, trong khi mức climax BCLX = 4806.7.
- **Đúng phải là:** hợp lệ về câu chữ (dưới trần 1.0× chiều cao range, và L3 cho phép ST[A] vượt climax để tạo biên phụ), nhưng phải ghi nhận đây là **ST[A] ở biên trên / ngoài range** — theo THEORY §5 đó là dấu "phe mua rất mạnh", tức tín hiệu sớm cho hướng phá LÊN. Thuật toán không dùng thông tin này ở đâu cả.
- **Dấu hiệu quyết định trên chart:** ST[A] VSA 0.58x (volume co lại) nhưng lại tạo **đỉnh mới** trên climax — nỗ lực nhỏ mà kết quả vượt đỉnh = không có cung ở biên trên. Đó là bằng chứng RE-ACC sớm hơn SOS 6 giờ.
- **Nghi phạm trong thuật toán:** không có nhánh nào đọc vị trí ST[A] trong range (THEORY §5) để làm bias hướng.

### 4. Diễn giải chỉ số nỗ lực/kết quả bị ĐẢO DẤU — lỗi chỉ số (không phải lỗi cấu trúc)
- **Thuật toán gắn:** effort 3.45x, result 3.93, er=0.88 → in nhãn "vùng hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** er = effort/result = 0.88 nghĩa là kết quả **tương xứng** nỗ lực. "Volume nhiều, kết quả ít" chỉ đúng khi er lớn hẳn (>1.5-2). Nhãn này đang in cứng cho mọi nhịp bất kể giá trị er (đối chiếu bài #09 er=0.10, #12 er=0.04 cũng mang đúng nhãn đó) → chỉ số **không đo đúng bản chất** ở tầng diễn giải, dù phép đo thô có thể đúng.
- **Nghi phạm trong thuật toán:** chuỗi mô tả gắn cứng vào nhịp "er cao nhất" thay vì phân ngưỡng er.

### 5. Phase E 121 nến dài gấp 2,7 lần Phase B — luật vi phạm: L9 (Phase B dài nhất)
- **Thuật toán gắn:** E=121 nến (đúng trần 120).
- **Đúng phải là:** Phase E dài hơn Phase B không tự động sai (E ở ngoài range), nhưng B=44 nến cho một vùng cân bằng trải gần 2 giờ là **mỏng**. Đây là hệ quả của lỗi #1: 41 nến đáng lẽ thuộc B bị cắt sang C. Sửa lỗi #1 thì B≈75, tỷ lệ phase mới đúng hình.
- **Dấu hiệu quyết định trên chart:** vạch tím "Phase B (44n)" và "Phase C (41n)" nằm sát nhau trong khi cụm nến hai đoạn có hành vi giống nhau (đều lình xình rồi leo).

## Đạt
- **Mục 1 (L1):** MOVE thật — 42.4 giá / 60 nến, hiệu suất 0.36; trên ảnh đường xám đi từ 4753 lên đúng chân nến BCLX. Climax là đỉnh cao nhất cửa sổ, đang chặn move.
- **Mục 2 (L2):** đủ 3 lần đổi hướng: BCLX 4806.7 → AR 4785.7 → ST[A]. AR là cú bật ngược thật (21 giá, 21 nến, VSA 1.71x), không phải râu nhiễu.
- **Mục 3 (L3):** biên chính = climax + AR, không bị kéo theo giá; biên phụ mỗi bên đúng 1 cái (4810.9 trên do ST[A], 4783.2 dưới do ST[B]), tỷ lệ 1.32x — hợp lý.
- **Mục 4 (L4):** BCLX + phá LÊN = **Tái tích luỹ**. Đúng, và đây chính là ca mà bản trước hay xoá oan.
- **Mục 6:** ST[B] 18:27 thọc xuống 4783.2 (2.5 giá dưới biên chính, dưới ngưỡng 15% chiều cao) — **không** bị nâng thành Spring. Đúng: cú này quá nhẹ để làm cú rũ, đối chiếu Ca #7 nguồn 7.pdf (chỉ cú thủng biên rồi bật mới là Spring).
- **Mục 7 (L10):** LPS[D] 4814.6 nằm **trên** biên phụ 4810.9 — retest giữ được ở ngoài biên, đúng CBR.
- **Mục 8:** chỉ số SOT phía DƯỚI đo **đúng bản chất**: n=3 nhịp rút ngắn, tỷ lệ volume 1.89 → hấp thụ ở đáy range. Range phá lên. Đây là chỉ số hữu ích nhất trong bài, khớp THEORY §7 (rút ngắn + volume lớn = phe đối lập sắp xuất hiện).

## Cần hỏi người học
- 265 nến M1 nhưng trải **13,5 giờ lịch** (phiên Á thưa nến). Khi so tỷ lệ độ dài phase, đếm bằng **số nến** hay bằng **thời gian lịch**? Câu này quyết định L8/L9 có bị vi phạm ở các range phiên Á hay không — áp cho cả bài #09, #11, #12.
