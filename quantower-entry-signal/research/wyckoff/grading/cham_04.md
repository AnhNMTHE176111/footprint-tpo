# Chấm bài #04 — Phân phối (DIST) · 2026-01-28 23:41 → 2026-01-29 17:05 (183 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây. Biên trên là một cây gai 1 phút sau khe giá 70 giá, biên chính cao 136 giá (2.39%) — đây là một đoạn xu hướng dữ dội bị cắt ngang, không phải vùng cân bằng.

## Lỗi (nặng → nhẹ)

### 1. Biên chính trên neo vào một cây gai 1 phút sau khe giá — luật vi phạm: L3 + Ca #5 nguồn 4.pdf ("ranh giới phải neo GIÁ ĐÓNG CỬA, không neo bóng nến")
- **Thuật toán gắn:** biên chính trên = **5696.0**, lấy từ nến 23:41 (O 5689.0 / H 5696.0 / L 5675.4 / C 5696.0, **volume 3**, VSA **1.13×**, biên độ 20.6 giá).
- **Đúng phải là:** nến ngay trước đó (23:40) nhảy từ **5610.0 lên 5680.1** trong một phút với 5 hợp đồng. Đỉnh 5696.0 là kết quả của một khe giá thanh khoản mỏng, không phải một mức được đấu giá. Suốt 116 nến Phase B sau đó giá **không lần nào** giao dịch trở lại vùng 5696 (trừ một print 1 hợp đồng ở 5700 = UT[B]). Biên trên đúng phải neo quanh **5680** (vùng đóng cửa cao nhất được giao dịch thật), và khi đó chiều cao range còn ~120 giá — vẫn quá rộng, xem lỗi 2.
- **Dấu hiệu quyết định trên chart:** biên chính trên (nét liền) và biên phụ (nét đứt 5700.0) gần như trùng nhau ở sát đỉnh khung, còn toàn bộ thân giá của Phase B nằm dưới đó 20–60 giá.
- **Nghi phạm trong thuật toán:** climax level lấy `high` của nến; chưa có bộ lọc khe giá. Tài liệu thuật toán mục 0b lỗi I chỉ loại "chính cây climax" khỏi phép đo MOVE, chưa xử lý **khe giá ngay trước climax**.

### 2. Cây mở range VSA 1.13× / 3 hợp đồng — không đạt ngưỡng climax của chính thuật toán
- Ngưỡng là VSA ≥ 2.2×; nến mở range chỉ 1.13×. Cây có nỗ lực thật là nến **-3 (23:23): 16 hợp đồng, VSA 6.53×** — và nó nằm ở **5595.8**, tức **100.2 giá dưới** biên chính trên. Cùng nguyên nhân với bài #03: mốc giá dời sang cực trị cụm mà không kiểm lại điều kiện climax.

### 3. Nhãn BCLX nằm ở phần ba dưới của range — luật vi phạm: THEORY §4.1, L3
- **Thuật toán gắn:** nhãn `BCLX` tại **5595.8**, trong khi biên chính trên là 5696.0 và biên chính dưới 5560.0. Nhãn "cao trào mua" đang nằm ở **26% chiều cao tính từ đáy range**, thấp hơn cả ST[A] (5660.0).
- **Dấu hiệu quyết định trên chart:** chấm BCLX vẽ sát chấm AR, cả hai ở đáy khung; đỉnh khung không có nhãn nào. Đọc chart ra kết luận ngược hoàn toàn.
- **Nghi phạm trong thuật toán:** như bài #01 và #03 — nhánh tách nhãn/mức climax v6. Đây là lỗi **lặp trên 5/6 bài của lô này**, cần vá ở một chỗ: nhãn climax phải bị kẹp trong cửa sổ cụm và phải là cực trị phía climax.

### 4. Range 136 giá / 2.39% trên 183 nến M1 không phải một vùng đấu giá — luật vi phạm: L1 + mục 1
- **Thuật toán gắn:** MOVE trước climax 418.3 giá / 182 nến, hiệu suất **0.35** (đúng bằng ngưỡng sàn), rồi range cao 136 giá.
- **Đúng phải là:** biên chính cao 136 giá = **32.5% chiều dài MOVE** mà nó được cho là đã chặn. Một "vùng cân bằng" chiếm 1/3 đợt xu hướng thì nó là đoạn xu hướng, không phải cân bằng. Chart xác nhận: từ 01-27 08:00 tới 01-29 giá đi một mạch 5170 → 5700, và cái gọi là "range" chỉ là đoạn dao động cuối trước khi sụp 250 giá. Đúng bài là **không mở range**, hoặc đợi vùng cân bằng thật hẹp hơn hình thành.
- **Nghi phạm trong thuật toán:** guard huỷ range "biên chính > 3.5% giá" quá lỏng cho vàng M1 (mục 12.5 tài liệu đã tự nhận là guard tự đặt). Nên thêm guard tương đối: chiều cao biên chính ≤ ~15–20% chiều dài MOVE.

### 5. SOW neo 150 giá dưới biên bị phá — luật vi phạm: Ca #5 nguồn 4.pdf (neo giá đóng cửa của nến mốc), L10
- **Thuật toán gắn:** biên chính dưới 5560.0, nhãn `SOW` tại **5410.0** (VSA 3.67×, thân 1.00).
- **Đúng phải là:** SOW là **cây phá biên**, tức cây đóng cửa xuyên 5560. Cây 5410 nằm cách biên **150 giá = 1.1× chiều cao range** — lúc đó cấu trúc đã sụp xong từ lâu; đó là cây giữa đợt rơi, không phải cây phá. Ranh giới C/D cũng bị đẩy theo.
- **Dấu hiệu quyết định trên chart:** chấm SOW nằm dưới khung range gần 1.5 ô lưới giá; giữa biên 5560 và chấm SOW có cả một đoạn nến rơi không nhãn.
- **Nghi phạm trong thuật toán:** vá lỗi B chọn "cây VSA cao nhất trong đoạn, đúng hướng, đóng cửa vượt biên" — nhưng "đoạn" tính tới hết cửa sổ xác nhận, nên cây to nhất của cả đợt sụp thắng cây phá thật. Phải giới hạn cửa sổ hồi tố về **3 nến đầu của cú phá**.

### 6. Phase E chỉ 2 nến — luật vi phạm: L10 (giống bài #02, #05)
- Phase D 22 nến, Phase E **2 nến** rồi đóng range, dù đợt giảm còn tiếp và giá vẫn ở 150–280 giá dưới biên. Nhánh kết thúc Phase E vẫn chưa đo đúng "giá đi tìm vùng giá mới".

### 7. Nhãn biên chồng nhau ở đỉnh (trình bày)
- `bien CHINH tren 5696.0` và `bien phu tren 5700.0` in đè lên nhau thành một dòng không đọc được; nhãn `Phase D`/`Phase E` cũng chồng lên đó.

## Đạt
- **ST[A] hợp lệ:** 5660.0, cách mức climax 36 giá = 26% chiều cao từ đỉnh, đúng chiều "quay lại phía climax rồi bị chặn". Phase A đủ 3 lần đổi hướng và kết thúc tại ST[A] (L2 ✓).
- **UT[B] đặt đúng vai:** cú thọc 5700.0 (trên biên chính, VSA 0.19×, 1 print) được gọi **UT[B]** và **giữ ở lại Phase B**, không bị nâng thành UTAD. Đây đúng là bài học Ca #1/#4 nguồn 4.pdf ("UTAD không dùng cho bất kỳ cú vượt đỉnh nào trong Phase B") — nhãn mới của v6 xử lý đúng chỗ này.
- **LPSY[C] đúng vai:** 5663.2 tại 14:29, là nhịp hồi yếu cuối cùng lên vùng trên range, 10 nến trước khi cấu trúc sụp — đúng định nghĩa LPSY (THEORY §4.1) và đúng ranh giới C/D mà giảng viên vẽ lại ở Ca #3 nguồn 4.pdf. Chỉ có **một** LPSY[C] và **một** LPSY[D], không spam.
- **Tên range (L4):** BCLX + phá xuống = Phân phối. Đúng.
- **Biên phụ (L3):** đúng một cái mỗi bên tối đa; ở đây một biên phụ trên 5700.0, tỷ lệ 1.03×.
- **Chỉ số Phase B — đo đúng số học:** `SOT phía DƯỚI = SOT (n=4), thrust cuối/đầu 0.56, volume 0.77× → cạn kiệt` và `SOT phía TRÊN = chớm (n=2), 0.75/0.67`. Cả hai đo đúng hiện tượng có thật trên chart (các nhịp thọc xuống ngắn dần).

## Cần hỏi người học
- Chỉ số SOT hiện chỉ ghi số, chưa ghi **bối cảnh**. Ở bài này SOT phía dưới (n=4, cạn kiệt) đọc trần trụi thì gợi ý "người bán cạn → sắp tăng", nhưng nó xuất hiện **sau UT[B] ở biên trên**, và THEORY §7 nói rõ: "SOT xuất hiện sau một Upthrust tiềm năng → giá đến từ Upthrust, rất có thể tiếp tục giảm". Anh có muốn thêm một cột "bối cảnh: SOT sau UT / sau Spring" để chỉ số không bị đọc ngược không?
