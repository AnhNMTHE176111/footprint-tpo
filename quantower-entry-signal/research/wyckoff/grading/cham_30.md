# Chấm bài #30 — Tái tích lũy (RE-ACC) · 2026-06-14 22:09 → 2026-06-15 04:14 (365 nến M1)

**Điểm: 7/10** — Bài tốt nhất của lô: cấu trúc, tỉ lệ phase và tên range đều đúng, cú phá chạy thật. Trừ điểm vì nhãn BCLX neo vào một nến doji VSA 1.22x và range thiếu hẳn nhãn ở Phase B.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX neo vào nến doji VSA 1.22x, thân/biên 0.04 — luật vi phạm: L1, §4.1 THEORY
- **Thuật toán gắn:** BCLX tại 4329.6 lúc 22:09, VSA **1.22x**, thân/biên **0.04**, biên độ 5.5 giá.
- **Đúng phải là:** cụm cao trào mua thật nằm **trước** đó: 22:03 (VSA **2.73x**, 412 lot, biên độ 14.9 giá, thân 0.63) và 22:04 (VSA **3.07x**, 542 lot). Còn cây thể hiện cung xuất hiện là **22:10 (VSA 2.84x, 755 lot — volume lớn nhất vùng, đóng cửa giảm)**. Nến 22:09 kẹp giữa hai cụm đó với volume 280 lot và thân 4% — nó chỉ là cây đánh dấu **đỉnh giá**, không mang tính chất cao trào nào.
- **Dấu hiệu quyết định trên chart:** ngưỡng climax của chính thuật toán là VSA ≥ 2.2x; nến mang nhãn BCLX đạt **1.22x**. Trên panel volume, thanh cao nhất cả chart nằm ở 22:10 (755 lot) — ngay **sau** nhãn, không phải tại nhãn.
- **Nghi phạm trong thuật toán:** lặp lại lỗi của bài #28/#29 — mục 4.0 "cụm climax" dời mốc theo **cực trị giá** trong 8 nến mà không kiểm nến đích còn đạt VSA ≥ 2.2x. Đây là lỗi xuất hiện ở **3/5 bài** của lô, nên là lỗi thuật toán chứ không phải lỗi lẻ.

### 2. Phase B 159 nến không có một nhãn nào — luật vi phạm: L9
- **Thuật toán gắn:** từ ST[A] (22:35) tới LPS[C] (01:15) là 159 nến trắng, không nhãn.
- **Đúng phải là:** Phase B là giai đoạn đọc nỗ lực↔kết quả, và ở đây có tài liệu rất rõ để đọc: giá tạo đáy **cao dần** (đáy quanh 23:06 ở ~4302, đáy quanh 01:1x ở 4310.4) trong khi đỉnh cũng cao dần (~4326 lúc 00:34) — đó là **cấu trúc dốc lên**, dạng tái tích luỹ "thể hiện sức mạnh" (§3.6 loại 2 THEORY, giống Ca #13/#17 nguồn 7.pdf). Nhãn đáng có: ít nhất một DA/test biên dưới quanh 23:06 và một test biên trên quanh 00:34.
- **Dấu hiệu quyết định trên chart:** biên dưới 4300.0 **chỉ bị chạm một lần duy nhất** ở đầu range (AR) và không bao giờ bị chạm lại trong 159 nến Phase B — người mua không cho giá về đáy. Đúng chữ trong §3.4: "người mua hung hăng không cho phép giá rơi xuống biên dưới".
- **Nghi phạm trong thuật toán:** mục 5 Phase B chỉ hỏi một câu "giá có thò ra ngoài biên chính không?" — giá không thò ra thì **không ghi gì**. Nên toàn bộ thông tin đắt nhất của Phase B (đáy cao dần, không test lại biên dưới) không được biểu diễn.

### 3. SOS chỉ VSA 1.62x và biên phụ trùng biên chính — cú phá không có "nỗ lực" tương ứng — luật vi phạm: L3, §6.3 THEORY (cần phân biệt 2 loại breakout ít volume)
- **Thuật toán gắn:** SOS tại 4338.6 lúc 01:49, VSA **1.62x**, thân 0.90; biên phụ = biên chính (29.6 giá, không có biên phụ thật).
- **Đúng phải là:** ghi nhận đây là ca breakout **không có volume nổi bật** — theo §6.3 điều này **vẫn hợp lệ** ("nguồn cung nổi đã thấp, CO không cần nỗ lực đặc biệt"), và bằng chứng hậu nghiệm ủng hộ: giá chạy từ 4338 lên 4364 và **giữ ở đó suốt 121 nến Phase E**. Nhưng thuật toán không phân biệt được ca này với ca "breakout yếu vì không ai quan tâm" — nó gọi SOS y như nhau. Với biên phụ trùng biên chính (chưa từng có ai thò ra ngoài range cả range), điều kiện L3 "SOS mạnh phải bứt biên phụ" trở thành vô nghĩa ở đây.
- **Dấu hiệu quyết định trên chart:** biên phụ 29.6 = biên chính 29.6, tức **không có biên phụ nào** — suốt 365 nến không phe nào thò được ra ngoài range. Điều đó tự nó đã là thông tin (cân bằng chặt), và làm cho cú phá đầu tiên đáng tin hơn bình thường.
- **Nghi phạm trong thuật toán:** không có nhánh phân loại breakout theo volume (§6.3). Ghi nhận là **thiếu tính năng**, không phải nhãn sai.

### 4. Thiếu nhãn LPS[D] sau SOS — luật vi phạm: L10/L7
- **Thuật toán gắn:** SOS (01:49) → Phase D 25 nến → Phase E, **không có LPS[D]**.
- **Đúng phải là:** nhìn ảnh, sau khi SOS bứt lên 4338.6 có một nhịp lùi nhẹ quanh 4335–4340 trước khi giá đi tiếp lên 4364 — đó chính là nhịp retest giữ ngoài biên, đáng đánh dấu LPS[D] (một điểm, đúng L7).
- **Dấu hiệu quyết định trên chart:** nhịp lùi nằm ngay dưới nhãn SOS trên ảnh, khoảng 01:5x–02:0x, vẫn **trên** biên 4329.6.
- **Nghi phạm trong thuật toán:** mục 7 gom LPS[D] với sai số **20 tick (2.0 giá)** quanh biên vừa phá. Nhịp lùi ở đây chỉ về tới ~4335, cách biên 4329.6 khoảng **5.4 giá** — ngoài cửa sổ 2.0 giá nên bị bỏ. Sai số 20 tick quá chặt cho một range cao 29.6 giá; nên đo theo % chiều cao range thay vì tick cố định.

## Đạt
- Mục 1 (L1): MOVE tăng **76.7 giá / 94 nến / hiệu suất 0.73** — move mạnh và sạch nhất cả lô, climax đúng là đỉnh cao nhất của cửa sổ, chặn move thật. Range mở hợp lệ (chỉ sai nến neo).
- Mục 2 (L2): đủ 3 lần đổi hướng. AR 4300.0 là cú bật ngược thật (rơi 29.6 giá). ST[A] 4306.9 quay lên phía climax rồi bị chặn — đúng vai test, **không** rơi giữa range vô nghĩa. Phase A chốt tại ST[A], 27 nến.
- Mục 3 (L3): biên chính = 4329.6 (climax) + 4300.0 (AR), cố định suốt 365 nến. Không có biên phụ — và đúng là **không nên có**, vì không nến nào đóng ngoài biên. Đây là ca thuật toán xử lý biên đúng nhất trong lô.
- Mục 4 (L4): origin BCLX + phá **lên** thật = **Tái tích luỹ**. Tên đúng — và đây chính là pattern mà bản trước bị xoá oan (mục 2b), nay bắt được.
- Mục 5 (L9): Phase B **159/365 nến** = phase dài nhất. Đúng tỉ lệ.
- Mục 6 (L8): Phase C **34 nến**, ngắn hơn Phase B và Phase E — đúng "phase ngắn nhất" (bằng D+9). LPS[C] tại 4310.4 nằm **trong** range (35% chiều cao, phía dưới), là nhịp test cuối trước khi bung — vị trí hợp lý cho một LPS[C] của case khó, khác hẳn bài #26/#28.
- Mục 7 (L10): SOS đóng cửa trên biên, Phase D 25 nến, Phase E **121 nến** với giá đi tìm vùng giá mới ở 4340–4364 và không lùi lại vào range. CBR đầy đủ nhất của lô.
- Mục 9: không nhãn dư, không nhãn sai vai. LPS[C] đúng là [C] (trước SOS).

## Kết luận cấu trúc
**Vẽ đúng, chỉ sửa nhãn.** Nếu là tôi: dời nhãn BCLX về cụm 22:03–22:04 (giữ mức biên 4329.6), thêm một nhãn test biên dưới trong Phase B để thể hiện đáy cao dần, thêm LPS[D] ở nhịp lùi sau SOS, và ghi chú đây là **tái tích luỹ dạng "thể hiện sức mạnh"** (§3.6 loại 2) vì biên dưới không bị test lại lần nào sau AR. Bài này chứng minh lõi v5 đã chạy đúng khi dữ liệu đủ sạch.
