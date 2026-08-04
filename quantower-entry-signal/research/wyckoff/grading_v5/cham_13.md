# Chấm bài #13 — Tích luỹ (ACC) · 2026-05-07 16:19 → 2026-05-08 14:07 (631 nến M1)

**Điểm: 2/10** — Climax không chặn được move (giá thủng thêm 42 giá sau đó), SOS neo vào cây VSA 0.62x. Range này phải bị **huỷ**, hoặc mở lại tại đáy thật 4708.0.

## Lỗi (nặng → nhẹ)

### 1. Climax KHÔNG chặn được move — giá thủng thêm 42 giá dưới mức SC — luật vi phạm: L1 + mục 4.0 chính tài liệu thuật toán
- **Thuật toán gắn:** SC tại 4750.0, biên chính dưới = 4750.0, giữ nguyên suốt range.
- **Đúng phải là:** biên phụ dưới ghi **4708.0** — giá đã đi xuống thêm **42.0 giá** dưới mức climax, tức **2.3 lần chiều cao biên chính** (18.4 giá). Một cây climax mà giá sau đó thủng qua nó gấp 2.3 lần chiều cao vùng thì nó **không chặn được gì**. Đáy thật của cấu trúc là 4708.0 ngày 07-05 22:00, không phải 4750.0.
- **Dấu hiệu quyết định trên chart:** đường liền cam dưới (4750.0) cắt **ngang giữa** vùng giá — nhìn ảnh, có ít nhất 4 cụm nến nằm hẳn dưới nó (khoảng 17:11, 18:45, 20:30, 23:54), sâu nhất tới đường đứt 4708.0. Đây đúng là lỗi hệ thống A của v4: "biên chính nằm giữa vùng giá" — **CHƯA HẾT**.
- **Nghi phạm trong thuật toán:** guard mục 4.0 ("vượt mức climax quá 3× biên độ TB → bỏ range") chỉ chạy trong cửa sổ cụm 8 nến. Cú thủng ở đây xảy ra ~340 nến sau climax nên guard không bắn. Cần một guard chạy suốt Phase B: nếu giá vượt biên chính quá 1× chiều cao range thì range gốc hỏng.

### 2. SOS neo vào cây VSA 0.62x — luật vi phạm: mục 8 (Effort vs Result) + lỗi hệ thống B v4
- **Thuật toán gắn:** SOS tại 05-08 13:39, giá 4785.2, VSA **0.62x**, thân 1.00.
- **Đúng phải là:** SOS là "spread + volume tăng đều". Volume của cây này **dưới trung bình 20 nến**. Nhìn panel volume ở đoạn 13:44 có vài cột vàng (VSA ≥ 2.2x) — nhãn phải rơi vào một trong số đó.
- **Dấu hiệu quyết định trên chart:** nhãn SOS đặt ở đỉnh cây tăng vọt lên 4797, nhưng cột volume dưới nó không phải cột cao nhất trong cụm.
- **Nghi phạm trong thuật toán:** vá lỗi B (đặt hồi tố vào cây VSA cao nhất) rõ ràng **chưa ăn** ở bài này. So sánh: bài #11 SOS được 4.36x, bài #12 được 10.29x, bài #14 được 2.05x — nhưng bài này 0.62x và bài #15 1.07x. Nhánh hồi tố chỉ chạy ở một số đường đi, cần kiểm lại.

### 3. AR VSA 0.27x, ST[A] VSA 0.17x — cả Phase A không có cây nào có nỗ lực — luật vi phạm: mục 2.2 THEORY (Effort vs Result)
- **Thuật toán gắn:** SC 1.90x → AR **0.27x** → ST[A] **0.17x**.
- **Đúng phải là:** AR là "sóng mua đẩy giá lên" sau khi áp lực bán cạn — nó phải có dấu vết trên volume. Cả 3 mốc Phase A đều dưới trung bình, trong đó ST[A] chỉ 0.17x. Một CHoCH mà cả 3 lần đổi hướng đều không có nỗ lực thì đó là nhiễu giá, không phải cuộc đấu giá.
- **Nghi phạm trong thuật toán:** mục 4.1/4.2 chỉ xét **swing pivot theo giá** (5 nến không cực trị mới + biên độ ≥1.5× TB), hoàn toàn không nhìn volume. Nên thêm điều kiện tối thiểu về nỗ lực cho AR.

### 4. mSOW VSA 0.13x vẫn nới biên phụ xuống 4708.0 — luật vi phạm: L3
- **Thuật toán gắn:** mSOW 07-05 22:00, 4708.0, VSA **0.13x**, thân 0.00.
- **Đúng phải là:** VSA 0.13x, thân 0.00 (doji) — đây là râu nến trong phiên Á, không phải "một thế lực đã cố phá range". Nhưng cái râu này lại **đặt luôn biên phụ dưới**, và biên phụ dưới là thứ SOW sẽ phải vượt qua để được công nhận. Một cây rác định đoạt điều kiện xác nhận của cả range.
- **Nghi phạm trong thuật toán:** cùng lỗi với bài #11 mục 5 — điều kiện "mạnh" dùng **hoặc** (sâu ≥15% chiều cao **hoặc** VSA ≥2.2×). Ở đây sâu 42 giá thoả điều kiện độ sâu nên bỏ qua VSA 0.13x. Đổi thành **và**.

### 5. LPS[C] 4770.8 nằm **trên** biên chính trên 4768.4 — luật vi phạm: L8
- **Thuật toán gắn:** LPS[C] 05-08 13:29 tại 4770.8.
- **Đúng phải là:** LPS[C] là nhịp test cuối **trước** cú phá lên, nó phải là một cái **đáy** nhịp hồi. Ở đây nó nằm cao hơn biên trên — máy chọn "đáy sâu nhất trong 60 nến trước cú phá" nhưng cả 60 nến đó đã nằm trên biên rồi.
- **Nghi phạm trong thuật toán:** mục 6 case khó, giống lỗi bài #12 mục 4.

### 6. Phase E dài **1 nến** — luật vi phạm: L10
- **Thuật toán gắn:** E = 1 nến (14:07 → 14:07).
- **Đúng phải là:** đây chính là lỗi hệ thống J của v4 ("Phase E luôn dài 1 nến") — mô tả nói đã vá, nhưng bài này vẫn 1 nến. Nhìn ảnh, sau SOS giá lên 4797 rồi **rơi thẳng về 4759** — cú phá này hỏng, không có Phase E nào cả. Range nên đóng ở trạng thái cú phá thất bại (mSOS), không đặt tên "Tích luỹ".

## Đạt
- L1 phần move: move giảm 53.5 giá / 70 nến / hiệu suất 0.48 — là move thật.
- L9/L8 tỉ lệ phase: B (577n) dài nhất, C (10n) ngắn nhất. Đúng khuôn.
- L2 Phase A đủ 3 lần đổi hướng và kết thúc tại ST[A]. Đúng khuôn (dù chất lượng volume kém).
- ST[A] 4757.2 nằm trong khoảng climax↔AR, không vượt trần. Đúng L2.

## Cần hỏi người học
- (không có — mọi lỗi trên đều quy được về luật)
