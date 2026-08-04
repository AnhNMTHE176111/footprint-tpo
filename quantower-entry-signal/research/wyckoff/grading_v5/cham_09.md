# Chấm bài #09 — Phân phối (DIST) · 2026-04-23 12:06 → 14:38 (127 nến M1)

**Điểm: 2/10** — Phase C (71 nến) dài gấp 9 lần Phase B (8 nến): tỉ lệ phase lộn ngược hoàn toàn. Range này phải vẽ lại từ Phase A.

## Lỗi (nặng → nhẹ)

### 1. Phase C = 71 nến, Phase B = 8 nến — luật vi phạm: L8 (C ngắn nhất) VÀ L9 (B dài nhất), vi phạm cùng lúc cả hai
- **Thuật toán gắn:** A 23 · **B 8** · **C 71** · D 25 · E 1.
- **Đúng phải là:** Phase B là nơi xây nguyên nhân, phải dài nhất; Phase C là tín hiệu đầu tiên của cú phá, phải ngắn nhất. Ở đây đảo ngược với tỉ số 9:1. Đúng bệnh v4 (lỗi C: Phase C 121 nến = trần timeout) chỉ nhẹ hơn về con số — **chưa hết bệnh**, chỉ hạ từ 121 xuống 71.
- **Dấu hiệu quyết định trên chart:** vạch tím "Phase C (71n)" trải từ 12:43 tới 14:05, bao trọn nguyên đoạn giá đi từ 4796 xuống 4770 rồi ngược lên 4790 — tức bao cả **một chu kỳ dao động đầy đủ** trong range. Đoạn đó chính là Phase B thật.
- **Nghi phạm trong thuật toán:** UTAD được gán quá sớm (xem lỗi #2) nên Phase C mở từ 12:43; sau đó cơ chế "chờ tối đa 120 nến" chưa kịp bắn thì SOW đã tới ở nến 71. Trần timeout không cứu được vì trần đặt ở 120 mà bệnh phát ở 71. Cần luật tỉ lệ tương đối: nếu độ dài C **vượt** độ dài B thì cú rũ đó không phải Phase C → hạ cấp thành UT, trả dải về B.

### 2. UTAD gọi sai chỗ — nó là UT trong Phase B, và không vượt biên phụ — luật vi phạm: L3 (cú rũ phải vượt biên PHỤ) + lỗi kinh điển Ca #1/#4 nguồn 4.pdf
- **Thuật toán gắn:** UTAD tại 12:43, giá **4795.6**, VSA 1.82x, thân/biên độ **0.00** (doji), trạng thái "confirmed".
- **Đúng phải là:** (a) biên phụ trên là **4796.4** — UTAD ở 4795.6 **không vượt qua nó**, tức theo đúng luật L3 và mục 5.1 câu hỏi 1 của chính thuật toán, cú này **chỉ là test**, phải gán **UT**, ở lại Phase B. Máy tự vi phạm luật nó khai. (b) UTAD là cú test **cuối cùng** phá đỉnh range ngay trước khi cấu trúc sụp (Ca #1 nguồn 4.pdf). Sau 12:43 giá còn dao động trong range **71 nến** và còn lên tận 4796.4 rồi 4790 nữa — còn nhiều nhịp hồi đáng kể → theo tiêu chí Ca #4 nguồn 4.pdf, "nếu sau đỉnh vẫn còn dao động đi ngang/hồi lại trong range → đó là ST[B]/UT, chưa phải UTAD". (c) Thân nến = 0.00, VSA 1.82x dưới ngưỡng 2.2x — một cây doji khối lượng tầm thường không đủ tư cách làm cú rũ quyết định.
- **Dấu hiệu quyết định trên chart:** chấm UTAD nằm **thấp hơn** cả chấm LPSY[C] (4796.4) ở ngay bên phải nó, và **thấp hơn** đường đứt "bien phu tren 4796.4". Một UTAD mà không phải đỉnh cao nhất range thì không phải UTAD.
- **Nghi phạm trong thuật toán:** thứ tự kiểm tra ở mục 5.1 — điều kiện "vượt biên phụ" đang được so với **biên phụ tại thời điểm đó**, mà lúc 12:43 biên phụ trên có thể còn chưa hình thành (ST[A] ở 4794.1 < 4795.6), nên cú này tự nó nới biên phụ rồi tự nhận là đã vượt. Phải so với biên phụ **trước khi** cú này nới, và cấm gán UTAD cho nến thân < 45%.

### 3. LPSY[C] cao hơn UTAD — hai nhãn đổi vai — luật vi phạm: L7/L8 (LPSY[C] là test SAU cú rũ, phải thấp hơn cú rũ trong phân phối)
- **Thuật toán gắn:** UTAD 4795.6 (12:43) → LPSY[C] **4796.4** (12:58).
- **Đúng phải là:** trong phân phối, LPSY là "đợt phục hồi **yếu**" sau cú rũ — nó phải **không vượt** được đỉnh cú rũ. Ở đây LPSY[C] cao hơn UTAD 0.8 giá, tức phe mua vẫn đẩy được giá lên cao hơn. Vậy **4796.4 mới là UTAD** (đỉnh cao nhất, cú test cuối cùng), còn cây 12:43 là UT. Hai nhãn phải đổi chỗ.
- **Dấu hiệu quyết định trên chart:** chấm LPSY[C] nằm đúng trên đường đứt biên phụ trên 4796.4 — nó chính là cái tạo ra biên phụ đó. Cú tạo cực trị xa nhất mới là cú rũ, đúng L3.
- **Nghi phạm trong thuật toán:** mục 6 — "trong lúc chờ, giá quay về test đúng vùng điểm rũ → LPS[C]/LPSY[C]". Không có kiểm tra "nhịp test này có vượt qua điểm rũ hay không". Nếu vượt → cú rũ cũ bị hạ cấp, cú mới lên thay (đúng luật "mỗi range chỉ MỘT cú rũ, cú sâu hơn hạ cấp cú trước" ở lỗi G).

### 4. SOW neo vào cây VSA 0.59x — luật vi phạm: THEORY §4.1 (SOW = "chênh lệch/khối lượng tăng"), lỗi B của v4 chưa hết
- **Thuật toán gắn:** SOW tại 14:06, giá 4774.6, VSA **0.59x**, thân 1.00.
- **Đúng phải là:** cây phá thật phải có volume tăng. Nhìn panel volume: ngay quanh 13:42–14:04 có một cột vàng rất cao (VSA rõ ≥ 2.2x) và cả cụm cột đỏ dày — cây phá thật ở đó. Cây 0.59x là nến xác nhận theo sau, đúng y lỗi B mà v5 khai đã vá bằng "neo hồi tố vào cây VSA cao nhất".
- **Dấu hiệu quyết định trên chart:** nhãn SOW đặt ở một nến bé, trong khi cụm nến đỏ biên độ lớn nằm lệch sang trái nó khoảng 5-8 nến.
- **Nghi phạm trong thuật toán:** cùng nghi phạm với bài #07 lỗi #1 — cửa sổ quét "cây VSA cao nhất" quá hẹp, không phủ hết đoạn từ nến thò ra tới nến xác nhận.

### 5. Phase E = 1 nến — luật vi phạm: L10 (Phase E = giá rời range đi tìm vùng giá mới) + lỗi J của v4
- **Thuật toán gắn:** E từ 14:38 tới 14:38 = **1 nến**.
- **Đúng phải là:** lỗi J của v4 ghi rõ "Phase E luôn dài 1 nến" và khai đã vá. Ở bài này bệnh **quay lại nguyên trạng**. Nhìn ảnh, sau 14:38 giá còn chạy tiếp: bật lên 4795 rồi mới đổ xuống 4777 — nhưng range đã đóng.
- **Nghi phạm trong thuật toán:** mục 7 — "hết 25 nến mà mới đi được ≥ 50% → vẫn cho chốt Phase E". Chốt E tại đúng nến hết hạn cửa sổ 25 nến (D = 25 nến, khớp chính xác) → E ăn phần dư = 1 nến. Trần lại quyết định thay cấu trúc.

### 6. Range chỉ 127 nến M1 với đủ Phase A→E — luật vi phạm: mục "khung quá thô / range quá vụn"
- **Thuật toán gắn:** biên chính cao **11.7 giá (0.24%)**, 127 nến, đủ 5 phase.
- **Đúng phải là:** đây là mức mà giảng viên nhiều lần yêu cầu đổi khung (Ca #4, #6, #19 nguồn 7.pdf). Một vùng đấu giá thật trên vàng không xong cả 5 phase trong 2 tiếng với biên độ 11.7 giá. Nghi ngay: **nhiễu, không phải vùng đấu giá**. Người học đã chốt "không đặt sàn độ dài tối thiểu", nên đây không phải lỗi luật — nhưng là **cờ đỏ chất lượng** cần ghi nhận.

## Đạt
- Điều kiện mở range: climax VSA **3.68x**, MOVE 43.0 giá / 64 nến / hiệu suất 0.37 — trên chart đợt tăng từ ~4737 lên 4790 là move thật, cây climax chặn đúng đỉnh (L1 ĐẠT).
- **Tên range đúng:** BCLX chặn move tăng → phá xuống → **Phân phối**. Đúng bảng L4.
- LPSY[D] (4780.9, VSA 2.50x) đặt đúng vai: nhịp hồi **sau** SOW, quay lại loanh quanh biên chính dưới 4779.2 rồi thất bại. Phân biệt đúng LPSY[C] vs LPSY[D] về mặt trước/sau SOW — đúng bài học Ca #3 nguồn 4.pdf.
- Mỗi bên đúng 1 biên phụ (4796.4 / 4770.3), đều là cực trị xa nhất thật (L3).
- Biên chính 4779.2–4790.9 cố định suốt range (L3).
