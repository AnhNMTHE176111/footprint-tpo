# Chấm bài #40 — Tích lũy (ACC) · 2026-07-06 00:01 → 01:57 (116 nến M1)

**Điểm: 3/10** — Phase A vẽ đúng, nhưng biên chính không bao được vùng đấu giá thật, tỉ lệ phase sai (B≈C), và tên "Tích luỹ" gán cho một cú phá mà giá sập ngược xuyên qua cả range ngay sau đó.

## Lỗi (nặng → nhẹ)

### 1. Biên chính không mô tả vùng đấu giá — L3 (hệ quả), L1 (range có thật hay không)
- **Thuật toán gắn:** biên chính 4182.4–4193.9 = **11.5 giá**; biên phụ 4182.4–4204.8 = **22.4 giá** (1.95×).
- **Đúng phải là:** vùng cân bằng thật trên chart là **4184–4205**. Từ 00:33 tới 01:31 (gần hết Phase B và toàn bộ Phase C) giá dao động **trên** biên chính trên 4193.9 — nét liền phía trên nằm giữa vùng giá, chẳng phân định gì. Nếu AR được chốt đúng ở đỉnh nhịp bật thật (~4198–4204) thì hai nét liền mới bao được vùng.
- **Dấu hiệu quyết định trên chart:** AR chốt tại 00:17 = **16 nến** sau climax, nhịp hồi chỉ 11.5 giá trong khi MOVE giảm 24.3 giá (hồi <50%); ngay sau ST[A] giá đi thẳng lên 4204.8, tức **vượt AR 10.9 giá ≈ 95% chiều cao range**.
- **Nghi phạm trong thuật toán:** AR = "swing pivot ngược đầu tiên được xác nhận (5 nến, sàn 1.5× ATR)". Sàn quá thấp nên chốt AR ở nhịp bật non đầu tiên. Mục 4.0 có guard "giá còn vượt **mức climax** quá 3× ATR thì bỏ range" nhưng **không có guard đối xứng cho mức AR** — vượt AR bao nhiêu cũng chỉ nới biên phụ.

### 2. Tên range "Tích luỹ" — cú phá không giữ được — L4, L10
- **Thuật toán gắn:** SOS 01:32 → Phase D → Phase E (1 nến) → `completed`, đặt tên **Tích lũy**.
- **Đúng phải là:** trên ảnh, sau LPS[D] giá lên đỉnh ~4214 lúc 01:45 rồi **đổ thẳng về 4181** (dưới cả biên chính dưới) trong vòng 50 nến kế. Đó không phải "giá rời range đi tìm vùng giá mới" (L10) mà là một cú **phá lên thất bại** — theo L4 thì hướng phá **thật** ở đây là xuống, range phải đọc là **Tái phân phối**, hoặc chí ít cú phá phải bị hạ cấp mSOS và range đóng ở trạng thái chưa rõ.
- **Dấu hiệu quyết định trên chart:** Phase E dài **đúng 1 nến** — chính máy đã ghi nhận "giá lùi hẳn vào trong biên" ngay tại nến đầu Phase E. Một Phase E 1 nến là bằng chứng nội tại rằng cú phá không giữ được, nhưng nó vẫn được dùng để đặt tên pattern.
- **Nghi phạm trong thuật toán:** đích Phase E tối thiểu **0.5× chiều cao** (5.75 giá) quá dễ đạt với range 11.5 giá; và điều kiện vô hiệu hoá cú phá (lỗi F) chỉ xét **trước** khi đạt 50% tiến độ — đạt xong rồi sập thì không ai chặn. Nên thêm: Phase E dài ≤ 2 nến ⇒ không được đặt tên pattern.

### 3. mSOS gán cho một cây râu không có nỗ lực — L3 / THEORY §6.4
- **Thuật toán gắn:** `mSOS` 01:16 tại 4204.8, **VSA 0.72×**, thân/biên độ **0.04**.
- **Đúng phải là:** **UT[B]** — test biên trên. mSOS (theo nghĩa v6: đã phá hẳn ra ngoài rồi thu hẳn vào) hàm ý một nỗ lực phá vỡ; một cây doji thân 4% với volume **dưới trung bình** không phải nỗ lực nào cả. Đây đúng là No Demand ở biên trên.
- **Nghi phạm trong thuật toán:** nhánh phân loại "cú thăm dò mạnh" dùng **hoặc** (sâu ≥15% chiều cao, **hoặc** VSA ≥ 2.2×). Với range 11.5 giá thì 15% = 1.7 giá — quá dễ, nên độ sâu một mình đã đủ nâng cấp lên mSOS dù volume 0.72×. Nên buộc **và** với một sàn thân nến (≥45% như SOS/SOW).

### 4. Tỉ lệ phase sai: Phase C không phải phase ngắn nhất — L8, L9
- **Thuật toán gắn:** A 26 · B **33** · C **32** · D 25 · E 1.
- **Đúng phải là:** B phải dài **hẳn** (L9), C phải ngắn nhất (L8). Ở đây C = 32 ≈ B = 33 và **dài hơn** D. Với 116 nến chia 5 phase gần đều nhau thì đây không phải một vùng đấu giá có 5 giai đoạn — đó là **nhiễu** bị chia phase cơ học (đúng lỗi "khung quá thô / range quá vụn" trong CHART_CASES).
- **Nghi phạm trong thuật toán:** Phase C gán ngược mở tại **swing pivot cuối trong 60 nến** trước cú phá; khi Phase B chỉ dài 33 nến thì cửa sổ 60 nến ăn ngược gần hết B. Guard `min(60, 1/2 độ dài Phase B)` có trong spec nhưng kết quả 32 nến cho thấy nó không hiệu lực ở bài này.

### 5. Nhãn mSOS ghi Phase "B" nhưng nằm giữa dải Phase C — lỗi trình bày/timeline
- Bảng sự kiện ghi mSOS 01:16 thuộc **Phase B**, trong khi dải phase nói 01:00–01:31 là **Phase C**. Trên ảnh nhãn mSOS nằm hẳn trong khoảng Phase C. Mâu thuẫn nội bộ — người đọc chart không biết tin cái nào.

### 6. Ba chỉ số Phase B mới: đo chưa đúng bản chất
- **Nỗ lực/kết quả:** ghi `effort=2.72x, result=5.85, er=0.46` rồi kết luận "**vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)**". er = 0.46 nghĩa là **kết quả lớn hơn nỗ lực** — đây là dấu hiệu *thiếu cung* (nỗ lực nhỏ đi được xa), ngược hẳn với hấp thụ. Câu diễn giải là **hằng số dán cứng**, không phụ thuộc giá trị er (kiểm chứng: bài #42 er=2.33 và bài #43 er=0.94 đều nhận đúng một câu này).
- **SOT phía dưới:** ghi trạng thái `chớm` với **n=1** nhịp, tỉ lệ thrust 0.00 và volume 0.00. THEORY §7 nói rõ SOT cần **≥3 lần đẩy** mới có nghĩa; n=1 mà đã gọi "chớm" là đọc SOT từ một nhịp đơn lẻ. Khi tỉ lệ không tính được (0.00) thì nên ghi `n/a`, không ghi trạng thái.
- **Bias test biên:** `+0` — giống hệt cả 5 bài 40–44. Một chỉ số nhận đúng một giá trị trên toàn lô thì chưa phân biệt được gì.

## Đạt
- **Điều kiện mở range (L1):** MOVE giảm 24.3 giá / 33 nến / hiệu suất 0.45, climax VSA 3.72× biên độ 11.1 giá và **là đáy thật** của cửa sổ (4182.4 = biên dưới). Climax chặn move đúng nghĩa.
- **Phase A (L2):** đủ 3 lần đổi hướng, ST[A] 00:26 tại **4183.0** — cách biên climax 0.6 giá, đúng là test lại vùng climax; Phase A kết thúc đúng tại ST[A].
- **Biên phụ (L3):** đúng 1 cái mỗi bên, biên phụ trên 4204.8 = cực trị xa nhất thật.
- **Nhãn climax neo đúng cực trị:** nhãn SC và mức biên trùng nhau (4182.4) — sửa được lỗi A của v4.
- **LPS[C] đặt đúng vị trí** (4184.3, sát biên dưới, là nhịp test cuối trước cú lên) — tuy VSA 3.24× cho thấy đây là **hấp thụ** chứ không phải test cạn cung, nên đọc kèm ghi chú.
