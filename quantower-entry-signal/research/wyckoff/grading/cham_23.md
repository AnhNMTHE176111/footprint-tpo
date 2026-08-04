# Chấm bài #23 — Tái phân phối (RE-DIST) · 2026-05-27 05:33 → 07:50 (137 nến M1)

**Điểm: 8/10** — Đọc cấu trúc **đúng**, kể cả ca khó nhất: SC ở đáy nhưng phá **xuống** → gọi Tái phân phối, và Phase C không có shock nên phải gán ngược từ SOW. Chỉ cần siết Phase E, sửa Phase C/D và vá chỉ số nỗ lực/kết quả.

## Lỗi (nặng → nhẹ)

### 1. Phase E kéo 85 nến, gộp luôn một vùng đấu giá MỚI — luật vi phạm: L10 (Phase E = rời range đi tìm vùng giá mới, không phải "mọi thứ còn lại")
- **Thuật toán gắn:** Phase E = 06:26 → 07:50 = **85 nến**, tức 62% toàn bộ range.
- **Đúng phải là:** Phase E chỉ nên bao đoạn giá thực sự **thuận lực rời range** — ở đây là đoạn 06:26 → ~06:35, rơi từ 4521 xuống ~4506. Từ ~06:40 trở đi giá **đi ngang 4511–4522 suốt gần 70 nến** với nhiều lần lên/xuống (nhìn ảnh: 3 nhịp bò lên tới 4522 rồi bị dập). Đó là một **vùng cân bằng mới** (giai đoạn đi ngang, THEORY §2.3), đúng ra phải sinh range kế tiếp, không nhét vào Phase E của range cũ.
- **Dấu hiệu quyết định trên chart:** cuối "Phase E" giá đóng ở **4519.5**, tức **cao hơn** cả SOW (4520.2 ≈ ngang) và cao hơn LPSY[D] (4521.7 ≈ ngang) — nghĩa là suốt 85 nến "Phase E" giá không đi được đâu cả. Một Phase E mà kết thúc ở đúng chỗ nó bắt đầu thì không phải Phase E.
- **Nghi phạm trong thuật toán:** `range.end` được đặt bằng "hết dữ liệu / hết cửa sổ" thay vì đóng khi giá lại vào trạng thái đi ngang. Cần điều kiện đóng Phase E: đóng khi phát hiện climax/CHoCH mới, hoặc khi N nến liên tiếp không mở rộng cực trị theo hướng phá.

### 2. Phase C (10n) dài hơn Phase D (8n) — luật vi phạm: L8
- **Thuật toán gắn:** A 12n · B 23n · **C 10n** · **D 8n**.
- **Đúng phải là:** Phase C phải là phase ngắn nhất. Ở đây C mở từ 06:08 (LPSY[C]) và kéo tới 06:17, gồm cả nhịp trượt từ 4530.8 về 4525 — nhịp trượt đó đã là hành vi Phase D (cung áp đảo). Phase C đúng chỉ là 2-3 nến quanh LPSY[C].
- **Dấu hiệu quyết định trên chart:** trong khung "Phase C (10n)" có chuỗi nến đỏ liên tiếp đi xuống chạm biên chính dưới 4525.6 — đó là SOW đang hình thành, không phải "test nguồn cầu còn lại".
- **Nghi phạm trong thuật toán:** cùng bug với #21/#22 — Phase C được kéo từ nhãn C đầu tiên tới nến SOW/SOS. Nên đóng C sớm hơn, ngay sau nến LPSY[C].

### 3. Chỉ số nỗ lực/kết quả: chọn sai nhịp + diễn giải NGƯỢC — luật vi phạm: THEORY §2.2 (lỗi ĐO)
- **Thuật toán in:** "nhịp nỗ lực/kết quả **cao nhất** trong Phase B: effort (VSA TB) = **0.81x**, result = 2.16, er = **0.38** → vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** hai lỗi cùng lúc. (a) effort **0.81x = dưới trung bình 20 nến** thì không thể là "nhịp nỗ lực cao nhất" — tiêu chí chọn nhịp sai chiều (đang chọn nhịp er **nhỏ nhất**). (b) er = 0.38 nghĩa là kết quả gấp ~2,6 lần nỗ lực → "nỗ lực ÍT, kết quả NHIỀU", tức trượt giá trong vùng rỗng — **ngược hẳn** với "volume nhiều, kết quả ít".
- **Dấu hiệu quyết định:** đối chiếu 6 bài #19–#24, câu "vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)" in ra ở **cả** er=0.18, 0.38, 0.49, 0.52, 1.32, 1.54 → chuỗi bị **hardcode**.
- **Nghi phạm trong thuật toán:** (a) hàm chọn nhịp dùng `min(er)` thay vì `max(effort)` hoặc `max(er)`; (b) câu kết luận nằm ngoài nhánh `if er > 1`.

### 4. Biên chính chỉ 7.3 giá (0.16%) trên 137 nến — cảnh báo độ mỏng, luật vi phạm: L1 (biên)
- **Thuật toán gắn:** biên chính 4525.6–4532.9 = **7.3 giá**, move trước climax 19.4 giá nhưng hiệu suất chỉ **0.49**.
- **Đánh giá:** phần range **thật** (Phase A→D, 05:33→06:25) chỉ ~53 nến trong 10.7 giá — chấp nhận được cho M1 vàng. Nhưng hiệu suất hướng 0.49 nghĩa là move trước climax đi vòng vèo gần một nửa quãng đường; đây là ca **ranh giới** của L1. Ghi nhận, không tính là lỗi nặng vì climax rất rõ (VSA 4.84x, 268 lot, biên độ 5.5 giá, và cây liền trước 4.42x/191 lot).

### 5. LPSY[D] có VSA 3.13x — không khớp "phục hồi yếu trên biên hẹp" (nhẹ, ngữ nghĩa)
- **Thuật toán gắn:** LPSY[D] 06:21 tại 4521.7, VSA **3.13x**, thân/biên 0.82.
- **Đúng phải là:** THEORY §4.1 định nghĩa LPSY = "đợt phục hồi **yếu** trên biên hẹp → nguồn cầu cạn kiệt". Volume 3.13x với thân đầy là **không yếu**. Nhìn chart, nhãn này nằm đúng ở nhịp giật lên sau SOW — vai trò (retest giữ ngoài biên) thì đúng, nhưng thuật toán nên hạ cấp/ghi chú khi volume test **không co lại**, vì THEORY §6.5 cảnh báo rõ: "volume cao trong lúc test lại → nên thận trọng, dấu hiệu quan tâm hướng ngược lại".
- **Nghi phạm trong thuật toán:** không có gate volume cho nhãn LPSY/LPS (test đúng chuẩn phải có volume **co lại** — THEORY §3.3, §6.4).

### 6. SOT phía dưới = none(n=0) trong một range mà phe bán thắng (nhẹ, chỉ số)
- Với range kết thúc bằng phá xuống, đo SOT phía dưới = 0 nhịp nghĩa là chỉ số không nói được gì về bên thắng. Nguyên nhân là Phase B chỉ 23 nến — không đủ 3 nhịp (THEORY §7). Không phải lỗi logic, nhưng nên in `chưa đủ nhịp` để người đọc không hiểu là "không có SOT".

## Đạt
- **L1 — mở range:** move giảm 19.4 giá / 44 nến bị chặn bởi đúng cây cao trào tại **cực trị** 4525.6 (VSA 4.84x, vol 268 = cao nhất cụm 12 nến). Climax chặn move, không nằm giữa move.
- **L2 — Phase A hoàn hảo:** đúng 3 lần đổi hướng — SC 4525.6 → AR 4532.9 (bật 7.3 giá trong 4 nến, VSA 1.36x) → **ST[A] 4523.2 quay lại và chọc xuống DƯỚI mức climax**. Phase A kết thúc đúng tại ST[A], không kéo dài thêm. Đây là Phase A chuẩn nhất trong lô #19–#24.
- **L3 — biên:** biên chính = climax + AR, cố định. Biên phụ đúng logic L3: **dưới 4523.2 do chính ST[A] vượt mức climax tạo ra** (đúng câu "ST[A] vượt qua mức climax cũng tạo biên phụ"), trên 4533.9; mỗi bên đúng 1, đều là cực trị xa nhất.
- **L4 — tên range: đúng và là ca khó.** Origin = SC (move giảm bị chặn) nhưng phá **xuống** thật → **Tái phân phối (RE-DIST)**, đúng ô bảng 4 mẫu hình. Thuật toán không mắc lỗi "phá sai hướng thì huỷ range", cũng không mắc lỗi kinh điển "gán SC trong cấu trúc không phải tích luỹ" (Ca #9/#14 nguồn 7.pdf) — vì ở đây trước range **thật sự** là một move giảm, SC hợp lệ.
- **L8 — case khó gán ngược đúng:** không có UTAD/shock, chỉ có **LPSY[C] tại 4530.8** (sát biên chính trên 4532.9) rồi SOW theo sau — đúng cách làm "chờ SOW xuất hiện rồi quay lại vẽ Phase C". Không gọi bừa UTAD (tránh được lỗi kinh điển Ca #1/#4 nguồn 4.pdf).
- **L10 — CBR đọc đúng:** SOW 06:18 (4520.2, VSA **4.23x**) đóng cửa **dưới biên phụ dưới 4523.2** (không chỉ vượt biên chính) → đúng yêu cầu L3 "SOW thực sự mạnh phải bứt qua biên phụ". LPSY[D] 06:21 hồi về 4521.7 nhưng **vẫn ở ngoài** biên phụ → giữ được ngoài biên, đúng L10.
- **Phân tách LPSY[C] vs LPSY[D]** đúng vai trước/sau SOW — tránh được lỗi gộp nhầm ở Ca #3 nguồn 4.pdf.
- **L9:** Phase B dài nhất trong A–D (23n). **L6/L7:** không có ST[B] rác, mỗi nhãn 1 điểm.
- **SOT phía trên** đo đúng bản chất: thrust cuối/đầu 0.51 + volume 0.92 → "cạn kiệt" khớp THEORY §7, và đúng là ngay sau đó cung áp đảo.
